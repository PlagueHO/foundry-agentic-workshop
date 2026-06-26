"""Generate per-attendee onboarding files and a provisioning summary.

This is the azd postprovision hook for the Microsoft Foundry workshop. It:
  1. Reads AZURE_ATTENDEE_LIST_RESOLVED (written by the preprovision hook).
  2. Reads azd provisioning outputs (Foundry resource name, resource group, etc.).
  3. Writes a per-attendee onboarding markdown file to .azure/<env>/<upn_local>.md.
  4. Writes a provisioning summary CSV to .azure/<env>/attendee-provisioning-<env>-<ts>.csv.
  5. Writes the attendee onboarding index to .azure/<env>/index.json.
  6. Uploads the onboarding index and markdown backups to Azure Blob Storage.

Role assignments for the deployer principal are handled by Bicep during provisioning.
This script uploads the onboarding index to Azure Blob Storage after generating it.

The recommended default attendee role for lab deployments is `foundry-project-manager`,
which covers all lab modules including Module 07 (Foundry IQ) and Module 12 (Publishing
Agents). All attendee roles receive the Azure AI Search permissions needed for Module 07
(Foundry IQ); `foundry-user` is project-scoped and additionally cannot complete Module 12
(Publishing Agents), which requires account-scoped permissions. The effective role for each
attendee is encoded in AZURE_ATTENDEE_LIST_RESOLVED.

Environment variables (azd outputs populated after provisioning):
  AZURE_ATTENDEE_LIST_RESOLVED  Enriched attendee list from the preprovision hook.
                                When not set, this script exits without error.
  FOUNDRY_RESOURCE_NAME         Foundry account name (azd output).
  FOUNDRY_CUSTOM_DOMAIN_NAME    Foundry custom subdomain name (azd output). Used to
                                construct project and OpenAI endpoint URLs.
  AZURE_RESOURCE_GROUP          Resource group name (azd output).
  AZURE_SEARCH_SERVICE_NAME     Azure AI Search service name (azd output).
  AZURE_CONTAINER_REGISTRY_NAME      Azure Container Registry name for hosted agents
                                (azd output).
  AZURE_CONTAINER_REGISTRY_ENDPOINT  Azure Container Registry login server (azd output).
  RETAIL_REMEDY_OPS_MCP_SERVER_URL  Shared MCP server URL (azd output). Empty when the
                                Container Apps deployment is disabled.
  FLIGHT_OPS_MCP_SERVER_URL     Flight operations MCP server URL (azd output). Empty
                                when the Container Apps deployment is disabled.
  AZURE_SUBSCRIPTION_ID         Subscription ID (required; set automatically by azd
                                after provision).
  AZURE_ENV_NAME                azd environment name (used in the audit CSV filename).
"""
# pylint: disable=duplicate-code
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient, ContentSettings
    _BLOB_UPLOAD_AVAILABLE = True
except ImportError:  # azure-storage-blob not installed; upload is skipped gracefully
    _BLOB_UPLOAD_AVAILABLE = False

# Metadata for the provisioning summary CSV.
# Mirrors ROLE_DEFINITIONS in scripts/prepare-attendee-roles.py and
# var foundryRoleCatalog in infra/main.bicep.
ROLE_DISPLAY_NAMES: dict[str, str] = {
    'foundry-user': 'Foundry User',
    'foundry-project-manager': 'Foundry Project Manager',
    'foundry-account-owner': 'Foundry Account Owner',
    'foundry-owner': 'Foundry Owner',
    'facilitator': 'Foundry Owner',
    'proctor': 'Foundry Owner',
    'organizer': 'Foundry Owner',
}

ROLE_DEFINITION_IDS: dict[str, str] = {
    'foundry-user': '53ca6127-db72-4b80-b1b0-d745d6d5456d',
    'foundry-project-manager': 'eadc314b-1a2d-4efa-be10-5d325db5065e',
    'foundry-account-owner': 'e47c6f54-e4a2-4754-9501-8e0985b135e1',
    'foundry-owner': 'c883944f-8b7b-4483-af10-35834be79c4a',
    'facilitator': 'c883944f-8b7b-4483-af10-35834be79c4a',
    'proctor': 'c883944f-8b7b-4483-af10-35834be79c4a',
    'organizer': 'c883944f-8b7b-4483-af10-35834be79c4a',
}

ROLE_SCOPE_LEVELS: dict[str, str] = {
    'foundry-user': 'project',
    'foundry-project-manager': 'account',
    'foundry-account-owner': 'account',
    'foundry-owner': 'account',
    'facilitator': 'account',
    'proctor': 'account',
    'organizer': 'account',
}

RESOURCE_GROUP_READER_ROLE_ID = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'

# Azure AI Search role definition GUIDs paired with each Foundry role. Mirrors the
# searchRoleCatalog variable in infra/main.bicep, which is the authoritative source.
#
# Foundry IQ knowledge base/source creation (Module 07) requires Search Service Contributor
# plus Search Index Data Contributor on the shared search service. Every lab attendee role
# receives both; higher roles keep the broad Contributor role and add Search Index Data
# Contributor for data-plane access.
SEARCH_SERVICE_CONTRIBUTOR_ROLE_ID = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
SEARCH_INDEX_DATA_CONTRIBUTOR_ROLE_ID = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
CONTRIBUTOR_ROLE_ID = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

_ATTENDEE_SEARCH_ROLES = [
    ('Search Service Contributor', SEARCH_SERVICE_CONTRIBUTOR_ROLE_ID),
    ('Search Index Data Contributor', SEARCH_INDEX_DATA_CONTRIBUTOR_ROLE_ID),
]
_HIGH_SEARCH_ROLES = [
    ('Contributor', CONTRIBUTOR_ROLE_ID),
    ('Search Index Data Contributor', SEARCH_INDEX_DATA_CONTRIBUTOR_ROLE_ID),
]

# Each Foundry role maps to a list of (display_name, role_definition_id) search roles.
SEARCH_ROLES: dict[str, list[tuple[str, str]]] = {
    'foundry-user': _ATTENDEE_SEARCH_ROLES,
    'foundry-project-manager': _ATTENDEE_SEARCH_ROLES,
    'foundry-account-owner': _ATTENDEE_SEARCH_ROLES,
    'foundry-owner': _HIGH_SEARCH_ROLES,
    'facilitator': _HIGH_SEARCH_ROLES,
    'proctor': _HIGH_SEARCH_ROLES,
    'organizer': _HIGH_SEARCH_ROLES,
}

_AZD_CMD = 'azd'


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() not in ('', 'false', '0', 'no', 'off')


def _load_azd_env() -> dict[str, str]:
    """Load all azd environment values as a fallback for variables not in os.environ.

    When the script is run directly (outside of `azd up`), azd outputs such as
    FOUNDRY_RESOURCE_NAME and AZURE_ATTENDEE_LIST_RESOLVED are stored in the azd
    env store but not exported to the current shell. This function retrieves them
    so the script can be re-run manually without needing `azd up`.
    """
    result = subprocess.run(
        [_AZD_CMD, 'env', 'get-values', '--output', 'json'],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def _build_attendee_env_dict(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    project_name: str,
    subscription_id: str,
    resource_group: str,
    foundry_name: str,
    foundry_custom_domain_name: str,
    search_service_name: str,
    container_registry_name: str,
    container_registry_endpoint: str,
    mcp_server_url: str,
    flight_ops_mcp_server_url: str,
) -> dict[str, str]:
    """Build the .env key/value dict for an attendee.

    Optional keys (search service, container registry, MCP server URLs) are omitted
    when not configured so consumers can distinguish "not set" from an empty string.
    Single source of truth for env content - used by both the onboarding index and
    the per-attendee markdown files.
    """
    project_endpoint = (
        f'https://{foundry_custom_domain_name}.services.ai.azure.com'
        f'/api/projects/{project_name}'
    )
    openai_endpoint = f'https://{foundry_custom_domain_name}.openai.azure.com/openai/v1'
    env: dict[str, str] = {
        'AZURE_SUBSCRIPTION_ID': subscription_id,
        'AZURE_RESOURCE_GROUP': resource_group,
        'FOUNDRY_RESOURCE_NAME': foundry_name,
        'FOUNDRY_PROJECT_NAME': project_name,
        'FOUNDRY_PROJECT_ENDPOINT': project_endpoint,
        'AGENT_NAME': 'acl-remedy-advisor',
        'HOSTED_AGENT_NAME_CONTAINER': 'acl-remedy-advisor-hosted-container',
        'HOSTED_AGENT_NAME_CODE': 'acl-remedy-advisor-hosted-code',
        'KNOWLEDGE_BASE_NAME': f'acl-remedy-knowledge-{project_name}',
        'TOOLBOX_NAME': 'acl-remedy-toolbox',
        'AZURE_OPENAI_ENDPOINT': openai_endpoint,
    }
    if search_service_name:
        env['AZURE_SEARCH_SERVICE_NAME'] = search_service_name
    if container_registry_name:
        env['AZURE_CONTAINER_REGISTRY_NAME'] = container_registry_name
    if container_registry_endpoint:
        env['AZURE_CONTAINER_REGISTRY_ENDPOINT'] = container_registry_endpoint
    env['RETAIL_REMEDY_OPS_MCP_SERVER_PORT'] = '8080'
    if mcp_server_url:
        env['RETAIL_REMEDY_OPS_MCP_SERVER_URL'] = mcp_server_url
    env['RETAIL_REMEDY_OPS_MCP_SERVER_LABEL'] = 'retail_remedy_ops'
    if flight_ops_mcp_server_url:
        env['FLIGHT_OPS_MCP_SERVER_URL'] = flight_ops_mcp_server_url
    env['FLIGHT_OPS_MCP_SERVER_LABEL'] = 'flight_ops'
    env['AZURE_SEARCH_PASSENGER_RIGHTS_INDEX_NAME'] = 'passenger-rights'
    return env


def _env_dict_to_str(env_dict: dict[str, str]) -> str:
    """Render an env dict as a KEY=VALUE string for .env files and markdown code blocks."""
    return '\n'.join(f'{k}={v}' for k, v in env_dict.items())


def _build_attendee_markdown_content(
    upn_local: str,
    upn: str,
    env_dict: dict[str, str],
    attendee_portal_url: str,
) -> str:
    """Build the onboarding markdown content for an attendee.

    Produces the same information as the Attendee Onboarding Portal page in a
    portable markdown format. Used for local audit files and as backup blobs
    uploaded to the onboarding container.
    """
    subscription_id = env_dict.get('AZURE_SUBSCRIPTION_ID', '')
    env_block_str = _env_dict_to_str(env_dict)
    portal_section = (
        '## Self-Serve Portal\n'
        '\n'
        'Visit the attendee portal to view your configuration interactively:\n'
        '\n'
        f'[Open Attendee Portal]({attendee_portal_url})\n'
        '\n'
        'Sign in with your lab Microsoft account to see your `.env` values.\n'
        '\n'
    ) if attendee_portal_url else ''
    return (
        '---\n'
        f'title: Workshop Onboarding - {upn_local}\n'
        f'description: Environment configuration for {upn}.\n'
        '---\n'
        '\n'
        f'# Workshop Onboarding: {upn_local}\n'
        '\n'
        'Use these values to configure your `.env` file and connect to the shared lab\n'
        'environment. Follow the [Attendee Quickstart](../docs/quickstart-attendee.md) or\n'
        'the full [Attendee Guide](../docs/guide-attendee.md) for step-by-step setup\n'
        'instructions.\n'
        '\n'
        f'{portal_section}'
        '## Your Environment Variables\n'
        '\n'
        'Copy `shared/.env.example` to `.env` in the repository root, then set these values:\n'
        '\n'
        '```env\n'
        f'{env_block_str}\n'
        '```\n'
        '\n'
        '## Sign In\n'
        '\n'
        '```bash\n'
        'az login\n'
        f'az account set --subscription {subscription_id}\n'
        '```\n'
        '\n'
        '## Validate Setup\n'
        '\n'
        '```bash\n'
        'uv run python scripts/health-check.py\n'
        '```\n'
        '\n'
        '## Next Steps\n'
        '\n'
        'Follow the [Attendee Quickstart](../docs/quickstart-attendee.md) to complete\n'
        'setup and begin the labs.\n'
    )


# ---------- helpers ----------

def _parse_resolved_list(raw: str) -> list[dict[str, object]]:
    stripped = raw.strip()
    if not stripped:
        return []
    parsed = json.loads(stripped)
    if not isinstance(parsed, list):
        raise ValueError('AZURE_ATTENDEE_LIST_RESOLVED must be a JSON array.')
    return [item for item in parsed if isinstance(item, dict)]


def _upn_key(upn: str) -> str:
    """Derive the index lookup key for a UPN.

    Must match _upn_key() in tools/attendee-portal/src/app.py so the portal
    can look up each attendee's record using the UPN from the EasyAuth header.
    """
    return upn.split('@')[0].lower().replace('.', '-').replace('_', '-')


def _build_onboarding_index(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    resolved: list[dict[str, object]],
    subscription_id: str,
    resource_group: str,
    foundry_name: str,
    foundry_custom_domain_name: str,
    search_service_name: str,
    container_registry_name: str,
    container_registry_endpoint: str,
    mcp_server_url: str,
    flight_ops_mcp_server_url: str,
    attendee_portal_url: str,
) -> dict[str, object]:
    """Build the attendee onboarding index dict.

    Keys are derived from attendee UPNs using _upn_key() so they match the keys used
    by the portal to look up records from the EasyAuth UPN header. Includes a ``_meta``
    key with generation metadata. Every attendee entry is included regardless of
    resolution status so the portal can serve config for facilitators, proctors, and
    organisers alongside regular attendees.
    """
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    index: dict[str, object] = {}
    for entry in resolved:
        upn = str(entry.get('upn', ''))
        project_name = str(entry.get('projectName', ''))
        role = str(entry.get('role', 'foundry-user'))
        is_resolved = bool(entry.get('resolved', False))
        key = _upn_key(upn)
        upn_local = upn.split('@', maxsplit=1)[0]

        env_dict = _build_attendee_env_dict(
            project_name=project_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            foundry_name=foundry_name,
            foundry_custom_domain_name=foundry_custom_domain_name,
            search_service_name=search_service_name,
            container_registry_name=container_registry_name,
            container_registry_endpoint=container_registry_endpoint,
            mcp_server_url=mcp_server_url,
            flight_ops_mcp_server_url=flight_ops_mcp_server_url,
        )
        markdown_content = _build_attendee_markdown_content(
            upn_local=upn_local,
            upn=upn,
            env_dict=env_dict,
            attendee_portal_url=attendee_portal_url,
        )
        index[key] = {
            'upn': upn,
            'projectName': project_name,
            'role': role,
            'roleDisplayName': ROLE_DISPLAY_NAMES.get(role, role),
            'resolved': is_resolved,
            'env': env_dict,
            'markdownContent': markdown_content,
        }

    total_count = len(index)
    resolved_count = sum(
        1 for v in index.values()
        if isinstance(v, dict) and v.get('resolved')
    )
    index['_meta'] = {
        'generatedAt': generated_at,
        'totalCount': total_count,
        'resolvedCount': resolved_count,
        'attendeePortalUrl': attendee_portal_url,
    }
    return index


def _upload_onboarding_index(
    index: dict[str, object],
    storage_account_name: str,
    onboarding_container: str,
) -> None:
    """Upload a pre-built onboarding index dict to Azure Blob Storage.

    The Attendee Onboarding Portal reads this blob to serve per-attendee environment
    configuration. Skips gracefully when the storage account name is not set or the
    azure-storage-blob library is not installed.
    """
    if not _BLOB_UPLOAD_AVAILABLE:
        print('azure-storage-blob is not installed; skipping onboarding index upload.')
        return
    if not storage_account_name:
        print('AZURE_STORAGE_ACCOUNT_NAME is not set; skipping onboarding index upload.')
        return

    meta = index.get('_meta')
    total_count = meta.get('totalCount', 0) if isinstance(meta, dict) else 0
    resolved_count = meta.get('resolvedCount', 0) if isinstance(meta, dict) else 0

    account_url = f'https://{storage_account_name}.blob.core.windows.net'
    try:
        client = BlobServiceClient(
            account_url=account_url,
            credential=DefaultAzureCredential(),
        )
        blob = client.get_blob_client(container=onboarding_container, blob='index.json')
        blob.upload_blob(
            json.dumps(index, ensure_ascii=False, indent=2),
            overwrite=True,
        )
        print(
            f'Onboarding index uploaded: {total_count} entr{"y" if total_count == 1 else "ies"} '
            f'({resolved_count} resolved) '
            f'-> {account_url}/{onboarding_container}/index.json'
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Warning: could not upload onboarding index: {exc}', file=sys.stderr)
        print(
            f'  Ensure the deployer principal has Storage Blob Data Contributor on '
            f'  storage account "{storage_account_name}". '
            f'  RBAC propagation can take a few minutes after provision.',
            file=sys.stderr,
        )
        print(
            '  Attendees will see "no configuration found" in the portal '
            'until the index is available.',
            file=sys.stderr,
        )


def _upload_onboarding_markdowns(
    audit_dir: Path,
    storage_account_name: str,
    onboarding_container: str,
) -> None:
    """Upload per-attendee markdown files from audit_dir as backup blobs.

    Files are uploaded to the root of the onboarding container, mirroring the
    filenames in .azure/<env>/, so the storage layout matches the local layout.
    Skips gracefully when the storage account is not set or the
    azure-storage-blob library is not installed.
    """
    if not _BLOB_UPLOAD_AVAILABLE:
        return
    if not storage_account_name:
        return

    md_files = list(audit_dir.glob('*.md'))
    if not md_files:
        return

    account_url = f'https://{storage_account_name}.blob.core.windows.net'
    try:
        client = BlobServiceClient(
            account_url=account_url,
            credential=DefaultAzureCredential(),
        )
        uploaded = 0
        for md_path in md_files:
            blob_name = md_path.name
            blob = client.get_blob_client(container=onboarding_container, blob=blob_name)
            blob.upload_blob(
                md_path.read_bytes(),
                overwrite=True,
                content_settings=ContentSettings(
                    content_type='text/markdown; charset=utf-8',
                ),
            )
            uploaded += 1
        print(
            f'Onboarding markdown backups uploaded: {uploaded} file(s) '
            f'-> {account_url}/{onboarding_container}/'
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Warning: could not upload onboarding markdown backups: {exc}', file=sys.stderr)
        print(
            f'  Ensure the deployer principal has Storage Blob Data Contributor on '
            f'  storage account "{storage_account_name}".',
            file=sys.stderr,
        )


def _write_provisioning_summary(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    resolved: list[dict[str, object]],
    audit_dir: Path,
    env_name: str,
    subscription_id: str,
    resource_group: str,
    search_service_name: str,
) -> Path:
    """Write the attendee provisioning summary CSV to audit_dir.

    Columns match the format expected by CI validation workflows.
    Role assignments are performed by Bicep; this CSV records their expected state.
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    audit_path = audit_dir / f'attendee-provisioning-{env_name}-{timestamp}.csv'

    search_scope = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.Search/searchServices/{search_service_name}'
        if search_service_name else ''
    )

    fieldnames = [
        'upn', 'object_id', 'role_key', 'role_display_name',
        'role_definition_id', 'project_name', 'scope', 'status', 'message',
    ]

    rows: list[dict[str, str]] = []
    for entry in resolved:
        upn = str(entry.get('upn', ''))
        object_id = str(entry.get('objectId', ''))
        role = str(entry.get('role', 'foundry-user'))
        project_name = str(entry.get('projectName', ''))
        was_resolved = bool(entry.get('resolved', False))

        scope_level = ROLE_SCOPE_LEVELS.get(role, 'project')
        status = 'succeeded' if was_resolved else 'failed'
        message = (
            '' if was_resolved
            else 'UPN not resolved to an Entra object ID; role assignment skipped by Bicep.'
        )

        # Main Foundry role row.
        rows.append({
            'upn': upn,
            'object_id': object_id,
            'role_key': role,
            'role_display_name': ROLE_DISPLAY_NAMES.get(role, role),
            'role_definition_id': ROLE_DEFINITION_IDS.get(role, ''),
            'project_name': project_name,
            'scope': scope_level,
            'status': status,
            'message': message,
        })

        # Resource group Reader row.
        rows.append({
            'upn': upn,
            'object_id': object_id,
            'role_key': 'rg-reader',
            'role_display_name': 'Reader',
            'role_definition_id': RESOURCE_GROUP_READER_ROLE_ID,
            'project_name': '',
            'scope': 'resource-group',
            'status': status,
            'message': message,
        })

        # Azure AI Search role rows (one per paired search role; included when search configured).
        if search_scope:
            for search_role_name, search_role_id in SEARCH_ROLES.get(role, []):
                rows.append({
                    'upn': upn,
                    'object_id': object_id,
                    'role_key': role,
                    'role_display_name': search_role_name,
                    'role_definition_id': search_role_id,
                    'project_name': '',
                    'scope': 'search',
                    'status': status,
                    'message': message,
                })

    with audit_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return audit_path


def _write_attendee_markdowns(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    resolved: list[dict[str, object]],
    audit_dir: Path,
    subscription_id: str,
    resource_group: str,
    foundry_name: str,
    foundry_custom_domain_name: str,
    search_service_name: str,
    container_registry_name: str,
    container_registry_endpoint: str,
    mcp_server_url: str,
    flight_ops_mcp_server_url: str,
    attendee_portal_url: str = '',
) -> list[Path]:
    """Write a per-attendee onboarding markdown file to audit_dir for resolved attendees."""
    written: list[Path] = []
    for entry in resolved:
        if not entry.get('resolved'):
            continue
        upn = str(entry.get('upn', ''))
        project_name = str(entry.get('projectName', ''))
        upn_local = upn.split('@', maxsplit=1)[0]
        out_path = audit_dir / f'{upn_local}.md'
        env_dict = _build_attendee_env_dict(
            project_name=project_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            foundry_name=foundry_name,
            foundry_custom_domain_name=foundry_custom_domain_name,
            search_service_name=search_service_name,
            container_registry_name=container_registry_name,
            container_registry_endpoint=container_registry_endpoint,
            mcp_server_url=mcp_server_url,
            flight_ops_mcp_server_url=flight_ops_mcp_server_url,
        )
        content = _build_attendee_markdown_content(
            upn_local=upn_local,
            upn=upn,
            env_dict=env_dict,
            attendee_portal_url=attendee_portal_url,
        )
        out_path.write_text(content, encoding='utf-8')
        written.append(out_path)
    return written


def _print_summary(resolved: list[dict[str, object]]) -> None:
    total = len(resolved)
    resolved_count = sum(1 for e in resolved if e.get('resolved'))
    unresolved_count = total - resolved_count
    per_role: dict[str, int] = {}
    for entry in resolved:
        role = str(entry.get('role', 'unknown'))
        per_role[role] = per_role.get(role, 0) + 1

    print('')
    print('Attendee provisioning summary')
    print(f'  Resolved (roles assigned by Bicep): {resolved_count}')
    print(f'  Unresolved (no role assignment):    {unresolved_count}')
    print('  Per role:')
    for role_key in sorted(per_role):
        print(f'    {role_key}: {per_role[role_key]}')


# ---------- main ----------

def main() -> int:  # pylint: disable=too-many-locals
    """Generate per-attendee onboarding files and a provisioning summary CSV."""
    # Merge azd env store values as fallbacks for variables not in the current shell.
    # This lets the script be re-run manually after `azd provision` without `azd up`.
    azd_env = _load_azd_env()

    def _env(key: str, default: str = '') -> str:
        return os.environ.get(key) or azd_env.get(key) or default

    raw_resolved = _env('AZURE_ATTENDEE_LIST_RESOLVED').strip()
    if not raw_resolved:
        print('AZURE_ATTENDEE_LIST_RESOLVED is not set. Skipping onboarding file generation.')
        print('Run the preprovision hook (scripts/prepare-attendee-roles.py) first, or use azd up.')
        return 0

    try:
        resolved = _parse_resolved_list(raw_resolved)
    except (json.JSONDecodeError, ValueError) as error:
        print(f'Invalid AZURE_ATTENDEE_LIST_RESOLVED: {error}')
        return 1

    if not resolved:
        print('AZURE_ATTENDEE_LIST_RESOLVED is empty. Nothing to generate.')
        return 0

    individual_mode = _is_truthy(_env('AZURE_INDIVIDUAL_MODE'))

    env_name = _env('AZURE_ENV_NAME', 'workshop').strip() or 'workshop'
    foundry_name = _env('FOUNDRY_RESOURCE_NAME').strip()
    foundry_custom_domain_name = _env('FOUNDRY_CUSTOM_DOMAIN_NAME').strip()
    resource_group = _env('AZURE_RESOURCE_GROUP').strip()
    search_service_name = _env('AZURE_SEARCH_SERVICE_NAME').strip()
    container_registry_name = _env('AZURE_CONTAINER_REGISTRY_NAME').strip()
    container_registry_endpoint = _env('AZURE_CONTAINER_REGISTRY_ENDPOINT').strip()
    mcp_server_url = _env('RETAIL_REMEDY_OPS_MCP_SERVER_URL').strip()
    flight_ops_mcp_server_url = _env('FLIGHT_OPS_MCP_SERVER_URL').strip()
    attendee_portal_url = _env('ATTENDEE_PORTAL_URL').strip()
    storage_account_name = _env('AZURE_STORAGE_ACCOUNT_NAME').strip()
    onboarding_container = _env('ATTENDEE_ONBOARDING_CONTAINER', 'attendee-onboarding').strip()
    subscription_id = (os.environ.get('AZURE_SUBSCRIPTION_ID') or azd_env.get('AZURE_SUBSCRIPTION_ID') or '').strip()

    missing = [
        name for name, val in [
            ('FOUNDRY_RESOURCE_NAME', foundry_name),
            ('FOUNDRY_CUSTOM_DOMAIN_NAME', foundry_custom_domain_name),
            ('AZURE_RESOURCE_GROUP', resource_group),
            ('AZURE_SUBSCRIPTION_ID', subscription_id),
        ] if not val
    ]
    if missing:
        print(f'Required environment variable(s) not set: {", ".join(missing)}.')
        print(
            'These are populated by azd after provisioning. '
            'Ensure azd provision completed successfully.'
        )
        return 1

    audit_dir = Path('.azure') / env_name
    audit_dir.mkdir(parents=True, exist_ok=True)

    index = _build_onboarding_index(
        resolved=resolved,
        subscription_id=subscription_id,
        resource_group=resource_group,
        foundry_name=foundry_name,
        foundry_custom_domain_name=foundry_custom_domain_name,
        search_service_name=search_service_name,
        container_registry_name=container_registry_name,
        container_registry_endpoint=container_registry_endpoint,
        mcp_server_url=mcp_server_url,
        flight_ops_mcp_server_url=flight_ops_mcp_server_url,
        attendee_portal_url=attendee_portal_url,
    )

    index_path = audit_dir / 'index.json'
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Onboarding index written to {index_path}')

    markdown_paths = _write_attendee_markdowns(
        resolved=resolved,
        audit_dir=audit_dir,
        subscription_id=subscription_id,
        resource_group=resource_group,
        foundry_name=foundry_name,
        foundry_custom_domain_name=foundry_custom_domain_name,
        search_service_name=search_service_name,
        container_registry_name=container_registry_name,
        container_registry_endpoint=container_registry_endpoint,
        mcp_server_url=mcp_server_url,
        flight_ops_mcp_server_url=flight_ops_mcp_server_url,
        attendee_portal_url=attendee_portal_url,
    )

    _upload_onboarding_markdowns(
        audit_dir=audit_dir,
        storage_account_name=storage_account_name,
        onboarding_container=onboarding_container,
    )
    _upload_onboarding_index(
        index=index,
        storage_account_name=storage_account_name,
        onboarding_container=onboarding_container,
    )

    audit_path = _write_provisioning_summary(
        resolved=resolved,
        audit_dir=audit_dir,
        env_name=env_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        search_service_name=search_service_name,
    )

    _print_summary(resolved)
    if attendee_portal_url:
        print(f'\nAttendee Portal URL: {attendee_portal_url}')
        print('  Share this URL with attendees so they can view their .env configuration.')
    print(f'\nProvisioning summary written to {audit_path}.')
    print(f'Onboarding index written to {index_path}.')
    print(f'Attendee onboarding files written: {len(markdown_paths)}')
    for md_path in markdown_paths:
        print(f'  {md_path}')

    unresolved_count = sum(1 for e in resolved if not e.get('resolved'))
    if unresolved_count:
        print(
            f'\nWarning: {unresolved_count} attendee(s) were not resolved during preprovision. '
            'No RBAC role assignments were created for those attendees by Bicep.'
        )

    if individual_mode:
        if len(resolved) != 1:
            print(
                f'\nWarning: AZURE_INDIVIDUAL_MODE is enabled but {len(resolved)} attendees were resolved; '
                'skipping .env generation.'
            )
        else:
            resolved_entry = resolved[0]
            env_dict = _build_attendee_env_dict(
                project_name=str(resolved_entry.get('projectName', '')),
                subscription_id=subscription_id,
                resource_group=resource_group,
                foundry_name=foundry_name,
                foundry_custom_domain_name=foundry_custom_domain_name,
                search_service_name=search_service_name,
                container_registry_name=container_registry_name,
                container_registry_endpoint=container_registry_endpoint,
                mcp_server_url=mcp_server_url,
                flight_ops_mcp_server_url=flight_ops_mcp_server_url,
            )
            env_path = Path(__file__).resolve().parent.parent / '.env'
            env_path.write_text(_env_dict_to_str(env_dict) + '\n', encoding='utf-8')
            print(f'\nIndividual mode: environment written to {env_path}')
            print('  Review .env and run: uv run python scripts/health-check.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
