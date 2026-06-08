"""Generate per-attendee onboarding files and a provisioning summary.

This is the azd postprovision hook for the Microsoft Foundry workshop. It:
  1. Reads AZURE_ATTENDEE_LIST_RESOLVED (written by the preprovision hook).
  2. Reads azd provisioning outputs (Foundry resource name, resource group, etc.).
  3. Writes a per-attendee onboarding markdown file to .azure/<upn_local>.md.
  4. Writes a provisioning summary CSV to .azure/attendee-provisioning-<env>-<ts>.csv.

Role assignments are handled by Bicep during provisioning. This script generates
output files only and makes no Azure API calls.

Environment variables (azd outputs populated after provisioning):
  AZURE_ATTENDEE_LIST_RESOLVED  Enriched attendee list from the preprovision hook.
                                When not set, this script exits without error.
  FOUNDRY_RESOURCE_NAME         Foundry account name (azd output).
  AZURE_RESOURCE_GROUP          Resource group name (azd output).
  AZURE_SEARCH_SERVICE_NAME     Azure AI Search service name (azd output).
  AZURE_SUBSCRIPTION_ID         Subscription ID (optional; resolved via az account show).
  AZURE_ENV_NAME                azd environment name (used in the audit CSV filename).
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

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

SEARCH_ROLE_DEFINITION_IDS: dict[str, str] = {
    'foundry-user': '1407120a-92aa-4202-b7e9-c0e197c71c8f',
    'foundry-project-manager': '8ebe5a00-799e-43f5-93ac-243d3dce84a7',
    'foundry-account-owner': '7ca78c08-252a-4471-8644-bb5ff32d4ba0',
    'foundry-owner': 'b24988ac-6180-42a0-ab88-20f7382dd24c',
    'facilitator': 'b24988ac-6180-42a0-ab88-20f7382dd24c',
    'proctor': 'b24988ac-6180-42a0-ab88-20f7382dd24c',
    'organizer': 'b24988ac-6180-42a0-ab88-20f7382dd24c',
}

SEARCH_ROLE_DISPLAY_NAMES: dict[str, str] = {
    'foundry-user': 'Search Index Data Reader',
    'foundry-project-manager': 'Search Index Data Contributor',
    'foundry-account-owner': 'Search Service Contributor',
    'foundry-owner': 'Contributor',
    'facilitator': 'Contributor',
    'proctor': 'Contributor',
    'organizer': 'Contributor',
}

_AZ_CMD: str = shutil.which('az') or 'az'


# ---------- helpers ----------

def _run_az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_AZ_CMD, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_resolved_list(raw: str) -> list[dict[str, object]]:
    stripped = raw.strip()
    if not stripped:
        return []
    parsed = json.loads(stripped)
    if not isinstance(parsed, list):
        raise ValueError('AZURE_ATTENDEE_LIST_RESOLVED must be a JSON array.')
    return [item for item in parsed if isinstance(item, dict)]


def _resolve_subscription_id() -> str:
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    if subscription_id:
        return subscription_id
    result = _run_az(['account', 'show', '--query', 'id', '-o', 'tsv'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _write_provisioning_summary(
    resolved: list[dict[str, object]],
    audit_dir: Path,
    env_name: str,
    subscription_id: str,
    resource_group: str,
    foundry_name: str,
    search_service_name: str,
) -> Path:
    """Write the attendee provisioning summary CSV to audit_dir.

    Columns match the format expected by CI validation workflows.
    Role assignments are performed by Bicep; this CSV records their expected state.
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    audit_path = audit_dir / f'attendee-provisioning-{env_name}-{timestamp}.csv'

    account_scope_base = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.CognitiveServices/accounts/{foundry_name}'
    )
    search_scope = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.Search/searchServices/{search_service_name}'
        if search_service_name else ''
    )
    rg_scope = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'

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
        foundry_scope = (
            f'{account_scope_base}/projects/{project_name}'
            if scope_level == 'project'
            else account_scope_base
        )
        status = 'succeeded' if was_resolved else 'failed'
        message = '' if was_resolved else 'UPN not resolved to an Entra object ID; role assignment skipped by Bicep.'

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

        # Azure AI Search role row (always included when search service is configured).
        if search_scope:
            rows.append({
                'upn': upn,
                'object_id': object_id,
                'role_key': role,
                'role_display_name': SEARCH_ROLE_DISPLAY_NAMES.get(role, role),
                'role_definition_id': SEARCH_ROLE_DEFINITION_IDS.get(role, ''),
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


def _write_attendee_markdowns(
    resolved: list[dict[str, object]],
    audit_dir: Path,
    subscription_id: str,
    resource_group: str,
    foundry_name: str,
    search_service_name: str,
) -> list[Path]:
    """Write a per-attendee onboarding markdown file to audit_dir for resolved attendees."""
    written: list[Path] = []
    for entry in resolved:
        if not entry.get('resolved'):
            continue
        upn = str(entry.get('upn', ''))
        project_name = str(entry.get('projectName', ''))
        upn_local = upn.split('@')[0]
        out_path = audit_dir / f'{upn_local}.md'
        search_line = (
            f'AZURE_SEARCH_SERVICE_NAME={search_service_name}'
            if search_service_name
            else '# AZURE_SEARCH_SERVICE_NAME=  # not configured'
        )
        project_endpoint = (
            f'https://{foundry_name}.services.ai.azure.com/api/projects/{project_name}'
        )
        openai_endpoint = f'https://{foundry_name}.openai.azure.com/openai/v1'
        content = (
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
            '## Your Environment Variables\n'
            '\n'
            'Copy `shared/.env.example` to `.env` in the repository root, then set these values:\n'
            '\n'
            '```env\n'
            f'AZURE_SUBSCRIPTION_ID={subscription_id}\n'
            f'AZURE_RESOURCE_GROUP={resource_group}\n'
            f'FOUNDRY_RESOURCE_NAME={foundry_name}\n'
            f'FOUNDRY_PROJECT_NAME={project_name}\n'
            f'FOUNDRY_PROJECT_ENDPOINT={project_endpoint}\n'
            f'AZURE_OPENAI_ENDPOINT={openai_endpoint}\n'
            f'{search_line}\n'
            '```\n'
            '\n'
            '## Sign In\n'
            '\n'
            '```bash\n'
            f'az login\n'
            f'az account set --subscription {subscription_id}\n'
            '```\n'
            '\n'
            '## Validate Setup\n'
            '\n'
            '```bash\n'
            'python scripts/health-check.py\n'
            '```\n'
            '\n'
            '## Next Steps\n'
            '\n'
            'Follow the [Attendee Quickstart](../docs/quickstart-attendee.md) to complete\n'
            'setup and begin the labs.\n'
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

def main() -> int:
    raw_resolved = os.getenv('AZURE_ATTENDEE_LIST_RESOLVED', '').strip()
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

    env_name = os.getenv('AZURE_ENV_NAME', 'workshop').strip() or 'workshop'
    foundry_name = os.getenv('FOUNDRY_RESOURCE_NAME', '').strip()
    resource_group = os.getenv('AZURE_RESOURCE_GROUP', '').strip()
    search_service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()

    if not foundry_name or not resource_group:
        print('FOUNDRY_RESOURCE_NAME and AZURE_RESOURCE_GROUP must be set. Skipping onboarding generation.')
        return 1

    subscription_id = _resolve_subscription_id()
    if not subscription_id:
        print('Unable to resolve the subscription ID. Skipping onboarding generation.')
        return 1

    audit_dir = Path('.azure') / env_name
    audit_dir.mkdir(parents=True, exist_ok=True)

    markdown_paths = _write_attendee_markdowns(
        resolved=resolved,
        audit_dir=audit_dir,
        subscription_id=subscription_id,
        resource_group=resource_group,
        foundry_name=foundry_name,
        search_service_name=search_service_name,
    )

    audit_path = _write_provisioning_summary(
        resolved=resolved,
        audit_dir=audit_dir,
        env_name=env_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        foundry_name=foundry_name,
        search_service_name=search_service_name,
    )

    _print_summary(resolved)
    print(f'\nProvisioning summary written to {audit_path}.')
    print(f'Attendee onboarding files written: {len(markdown_paths)}')
    for md_path in markdown_paths:
        print(f'  {md_path}')

    unresolved_count = sum(1 for e in resolved if not e.get('resolved'))
    if unresolved_count:
        print(
            f'\nWarning: {unresolved_count} attendee(s) were not resolved during preprovision. '
            'No RBAC role assignments were created for those attendees by Bicep.'
        )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
