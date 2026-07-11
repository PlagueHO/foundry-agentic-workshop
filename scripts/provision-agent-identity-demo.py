"""Provision the agent-framework-dotnet Module 11 unattended agent identity demo.

Runs as an azd postprovision step, after the Blob Relay MCP server Container App
exists. For each Foundry project in the environment it:

  1. Creates a project connection (``AgenticIdentityToken`` / ``RemoteTool``) that
     points at the Blob Relay MCP endpoint with the Azure Storage audience.
  2. Creates a new-model prompt agent whose MCP tool is bound to that connection.
  3. Reads the agent's Entra *instance identity* and grants it
     ``Storage Blob Data Contributor`` on the demo storage account. This grant can
     only happen after the agent is created (the identity does not exist before),
     so it is an organizer/provisioning step - attendees cannot self-assign it.

It also seeds a sample blob the agent can read. All values are read from the azd
environment. The script is idempotent: connections and agent versions are
content-addressable, and an existing role assignment is treated as success.

Prerequisites: azd and the Azure CLI (signed in with permission to create role
assignments, for example Owner or Role Based Access Control Administrator).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TICK = '\u2705'
CROSS = '\u274c'

# Stable resource names for the Module 11 demo.
CONNECTION_NAME = 'blob-relay'
AGENT_NAME = 'trip-concierge-storage'
SERVER_LABEL = 'blob_store'
BLOB_CONTAINER = 'agent-identity-demo'
SAMPLE_BLOB_NAME = 'welcome.txt'
STORAGE_AUDIENCE = 'https://storage.azure.com'
CONNECTIONS_API_VERSION = '2025-10-01-preview'

AGENT_INSTRUCTIONS = (
    'You are the Trip Disruption Concierge with access to a passenger case store '
    'in Azure Blob Storage. Use the blob_store MCP tools (read_blob, write_blob) '
    'to read and record passenger case notes when asked. Report tool results '
    'clearly. You never handle tokens or secrets yourself - the platform '
    'authenticates you with your own agent identity.'
)

SAMPLE_BLOB_CONTENT = (
    'Passenger case AU123: flight AKL->SYD cancelled with 3 hours notice. '
    'Passenger is entitled to rebooking or a refund under the carrier policy.'
)


def _fail(message: str) -> int:
    print(f'{CROSS} {message}', file=sys.stderr)
    return 1


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() not in ('', 'false', '0', 'no', 'off')


def _load_azd_env() -> dict[str, str]:
    result = subprocess.run(
        [_AZD_CMD, 'env', 'get-values', '--output', 'json'],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def _az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([_AZ_CMD, *args], capture_output=True, text=True, check=False)


def _project_endpoint(foundry_endpoint: str, project_name: str) -> str:
    """Build a project data-plane endpoint from the account endpoint."""
    base = foundry_endpoint.rstrip('/')
    return f'{base}/api/projects/{project_name}'


def _discover_model(client: AIProjectClient) -> str:
    """Return a chat-capable model deployment name from the project."""
    for deployment in client.deployments.list():
        data = deployment.as_dict() if hasattr(deployment, 'as_dict') else {}
        name = data.get('name', '')
        model_name = (data.get('model_name') or '').lower()
        if name and 'embedding' not in name.lower() and 'embedding' not in model_name:
            return name
    return 'chat'


def _put_connection(
    subscription_id: str, resource_group: str, account_name: str,
    project_name: str, relay_url: str,
) -> bool:
    """Create or update the AgenticIdentityToken RemoteTool connection."""
    url = (
        f'https://management.azure.com/subscriptions/{subscription_id}'
        f'/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices'
        f'/accounts/{account_name}/projects/{project_name}/connections/{CONNECTION_NAME}'
        f'?api-version={CONNECTIONS_API_VERSION}'
    )
    body = json.dumps({
        'properties': {
            'authType': 'AgenticIdentityToken',
            'category': 'RemoteTool',
            'target': relay_url,
            'audience': STORAGE_AUDIENCE,
        }
    })
    result = _az(['rest', '--method', 'PUT', '--url', url, '--body', body, '-o', 'none'])
    if result.returncode != 0:
        print(f'{CROSS} connection PUT failed: {result.stderr.strip()}', file=sys.stderr)
        return False
    return True


def _grant_storage_role(principal_id: str, storage_account_id: str) -> bool:
    """Grant Storage Blob Data Contributor to the agent identity (idempotent)."""
    result = _az([
        'role', 'assignment', 'create',
        '--assignee-object-id', principal_id,
        '--assignee-principal-type', 'ServicePrincipal',
        '--role', 'Storage Blob Data Contributor',
        '--scope', storage_account_id,
        '-o', 'none',
    ])
    if result.returncode == 0:
        return True
    if 'RoleAssignmentExists' in result.stderr or 'already exists' in result.stderr.lower():
        return True
    print(f'{CROSS} role assignment failed: {result.stderr.strip()}', file=sys.stderr)
    return False


def _provision_project(
    env: dict[str, str], project_name: str, relay_url: str, storage_account_id: str,
) -> bool:
    """Provision the connection, agent, and role grant for a single project."""
    subscription_id = env.get('AZURE_SUBSCRIPTION_ID', '')
    resource_group = env.get('AZURE_RESOURCE_GROUP', '')
    account_name = env.get('FOUNDRY_RESOURCE_NAME', '')
    foundry_endpoint = env.get('FOUNDRY_ENDPOINT', '')

    print(f'\n=== Project: {project_name} ===')
    if not _put_connection(subscription_id, resource_group, account_name, project_name, relay_url):
        return False
    print(f'{TICK} connection {CONNECTION_NAME!r} -> {relay_url}')

    endpoint = _project_endpoint(foundry_endpoint, project_name)
    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    model = _discover_model(client)

    tool = MCPTool(
        server_label=SERVER_LABEL,
        server_url=relay_url,
        project_connection_id=CONNECTION_NAME,
        require_approval='never',
    )
    definition = PromptAgentDefinition(model=model, instructions=AGENT_INSTRUCTIONS, tools=[tool])
    version = client.agents.create_version(agent_name=AGENT_NAME, definition=definition)
    version_data = version.as_dict() if hasattr(version, 'as_dict') else {}
    principal_id = (version_data.get('instance_identity') or {}).get('principal_id')
    print(f'{TICK} agent {AGENT_NAME!r} v{version_data.get("version")} (model {model})')

    if not principal_id:
        _fail(f'agent {AGENT_NAME!r} has no instance_identity - is this a new-model project?')
        return False
    if not _grant_storage_role(principal_id, storage_account_id):
        return False
    print(f'{TICK} granted Storage Blob Data Contributor to agent identity {principal_id}')
    return True


def _seed_sample_blob(storage_account: str) -> None:
    """Upload the sample case blob the agent reads (best effort)."""
    result = _az([
        'storage', 'blob', 'upload',
        '--account-name', storage_account,
        '--auth-mode', 'login',
        '-c', BLOB_CONTAINER,
        '-n', SAMPLE_BLOB_NAME,
        '--data', SAMPLE_BLOB_CONTENT,
        '--overwrite',
        '-o', 'none',
    ])
    if result.returncode == 0:
        print(f'{TICK} seeded {BLOB_CONTAINER}/{SAMPLE_BLOB_NAME}')
    else:
        print(
            f'{CROSS} could not seed sample blob (the storage account may block public '
            f'access): {result.stderr.strip()}',
            file=sys.stderr,
        )


def main() -> int:
    env = _load_azd_env()
    if not env:
        return _fail("Could not read the azd environment. Run 'azd provision' first.")

    deploy_enabled = env.get(
        'AZURE_CONTAINER_APPS_DEPLOY_ENABLED',
        env.get('AZURE_CONTAINER_APPS_DEPLOY', 'true'),
    )
    if not _is_truthy(deploy_enabled):
        print(f'{TICK} Container Apps deployment is disabled. Skipping agent identity demo.')
        return 0

    relay_url = env.get('BLOB_RELAY_MCP_SERVER_URL', '')
    storage_account = env.get('AZURE_STORAGE_ACCOUNT_NAME', '')
    resource_group = env.get('AZURE_RESOURCE_GROUP', '')
    if not (relay_url and storage_account and resource_group):
        return _fail('The azd environment is missing the relay URL, storage account, or resource group.')

    show = _az([
        'storage', 'account', 'show', '-n', storage_account, '-g', resource_group,
        '--query', 'id', '-o', 'tsv',
    ])
    storage_account_id = show.stdout.strip()
    if show.returncode != 0 or not storage_account_id:
        return _fail(f'Could not resolve the storage account id: {show.stderr.strip()}')

    # Provision every Foundry project in the environment (attendee projects, or the default).
    projects: list[str] = []
    try:
        projects = [p for p in json.loads(env.get('AZURE_ATTENDEE_PROJECT_NAMES', '[]')) if p]
    except json.JSONDecodeError:
        projects = []
    if not projects:
        default_project = env.get('FOUNDRY_PROJECT_NAME', '')
        projects = [default_project] if default_project else []
    if not projects:
        return _fail('No Foundry projects found in the azd environment.')

    _seed_sample_blob(storage_account)

    failures = 0
    for project_name in projects:
        if not _provision_project(env, project_name, relay_url, storage_account_id):
            failures += 1

    if failures:
        return _fail(f'Agent identity demo provisioning failed for {failures} project(s).')
    print(f'\n{TICK} Agent identity demo provisioned for {len(projects)} project(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
