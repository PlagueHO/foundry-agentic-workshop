"""Build and deploy the Attendee Onboarding Portal image and configure EasyAuth.

The shared Azure Container Registry uses ABAC repository permissions. This script
follows the same identity-based flow used by deploy-retail-remedy-ops-mcp-server.py:

  1. az acr login                     (token exchange using the signed-in identity)
  2. docker build                     (build the portal image locally)
  3. docker push                      (push using the ABAC repository role)
  4. az containerapp update --image   (roll the Container App to the new image)
  5. Find or create an Entra app registration for EasyAuth
  6. Issue a client secret and store it as a Container App secret
  7. az rest PUT authConfigs/current  (enable Container Apps EasyAuth)

Run it after `azd provision` has created the Container App. It also runs
automatically as the `azd` postprovision hook; it skips itself when
AZURE_CONTAINER_APPS_DEPLOY is false. All required values are read from the
azd environment, so no arguments are needed.

Prerequisites: azd, the Azure CLI (signed in), and a running Docker engine.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'
_DOCKER_CMD: str = shutil.which('docker') or 'docker'

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PORTAL_DIR = _REPO_ROOT / 'tools' / 'attendee-portal'
_DOCKERFILE = _PORTAL_DIR / 'Dockerfile'

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TICK = '\u2705'
CROSS = '\u274c'


def _fail(message: str) -> int:
    print(f'{CROSS} {message}', file=sys.stderr)
    return 1


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() not in ('', 'false', '0', 'no', 'off')


def _run(command: list[str], *, cwd: Path | None = None) -> int:
    print(f'$ {" ".join(command)}')
    return subprocess.run(command, cwd=cwd, check=False).returncode


_CAE_HINT = (
    'Your Azure CLI token has expired or requires re-authentication (CAE challenge).\n'
    '  Run: az login\n'
    '  Then re-run: uv run python scripts/deploy-attendee-portal.py'
)


def _run_json(command: list[str]) -> object:
    """Run a command and parse its stdout as JSON. Returns None on failure."""
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        if 'InteractionRequired' in result.stderr or 'TokenCreatedWithOutdatedPolicies' in result.stderr:
            print(f'ERROR: {result.stderr.strip()}', file=sys.stderr)
            print(f'\n{_CAE_HINT}', file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _load_azd_env() -> dict[str, str]:
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


def _azd_env_set(key: str, value: str) -> None:
    subprocess.run([_AZD_CMD, 'env', 'set', key, value], check=False)


def _find_or_create_app(display_name: str, redirect_uri: str) -> str | None:
    """Return the client ID of the Entra app, creating it if necessary."""
    apps = _run_json([
        _AZ_CMD, 'ad', 'app', 'list',
        '--display-name', display_name,
        '--output', 'json',
    ])
    if apps and isinstance(apps, list) and apps:
        app_id: str = apps[0]['appId']
        print(f'{TICK} Found existing Entra app: {display_name} ({app_id})')
        # Ensure the redirect URI is registered.
        _run([
            _AZ_CMD, 'ad', 'app', 'update',
            '--id', app_id,
            '--web-redirect-uris', redirect_uri,
        ])
        return app_id

    result = subprocess.run(
        [
            _AZ_CMD, 'ad', 'app', 'create',
            '--display-name', display_name,
            '--web-redirect-uris', redirect_uri,
            '--sign-in-audience', 'AzureADMyOrg',
            '--output', 'json',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        if 'InteractionRequired' in result.stderr or 'TokenCreatedWithOutdatedPolicies' in result.stderr:
            print(f'\n{_CAE_HINT}', file=sys.stderr)
        else:
            print(result.stderr, file=sys.stderr)
        return None
    try:
        data = json.loads(result.stdout)
        app_id = data['appId']
        print(f'{TICK} Created Entra app: {display_name} ({app_id})')
        return app_id
    except (json.JSONDecodeError, KeyError):
        return None


def _reset_credential(app_id: str) -> str | None:
    """Reset (or create) the client secret for an Entra app. Returns the secret value."""
    result = subprocess.run(
        [
            _AZ_CMD, 'ad', 'app', 'credential', 'reset',
            '--id', app_id,
            '--display-name', 'easyauth',
            '--output', 'json',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)['password']
    except (json.JSONDecodeError, KeyError):
        return None


def _ensure_storage_blob_reader(
    resource_group: str,
    container_app_name: str,
    storage_account_name: str,
    subscription_id: str,
) -> int:
    """Ensure the portal managed identity has Storage Blob Data Reader on the storage account.

    The Bicep template grants this role, but only when ``azureContainerAppsDeploy=true``
    at provision time. Running the deploy script independently (without re-running
    ``azd provision``) can leave the assignment absent. This step is idempotent.
    """
    ca_data = _run_json([
        _AZ_CMD, 'containerapp', 'show',
        '--name', container_app_name,
        '--resource-group', resource_group,
        '--output', 'json',
    ])
    if not ca_data or not isinstance(ca_data, dict):
        print(f'{CROSS} Could not retrieve Container App details for role check.', file=sys.stderr)
        return 1

    user_identities: dict = (
        ca_data.get('identity') or {}
    ).get('userAssignedIdentities') or {}
    if not user_identities:
        print(
            f'{CROSS} No user-assigned identities found on Container App '
            f'{container_app_name!r}.',
            file=sys.stderr,
        )
        return 1

    identity_resource_id = next(iter(user_identities))
    principal_id: str = user_identities[identity_resource_id].get('principalId', '')
    if not principal_id:
        print(
            f'{CROSS} Could not read principalId from identity {identity_resource_id!r}.',
            file=sys.stderr,
        )
        return 1

    scope = (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.Storage/storageAccounts/{storage_account_name}'
    )
    # Well-known GUID for the built-in "Storage Blob Data Reader" role.
    _STORAGE_BLOB_DATA_READER = '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'

    existing = _run_json([
        _AZ_CMD, 'role', 'assignment', 'list',
        '--assignee', principal_id,
        '--role', _STORAGE_BLOB_DATA_READER,
        '--scope', scope,
        '--output', 'json',
    ])
    if existing and isinstance(existing, list) and existing:
        print(f'{TICK} Storage Blob Data Reader already assigned to portal managed identity.')
        return 0

    print('Assigning Storage Blob Data Reader to portal managed identity...')
    return _run([
        _AZ_CMD, 'role', 'assignment', 'create',
        '--assignee', principal_id,
        '--role', _STORAGE_BLOB_DATA_READER,
        '--scope', scope,
    ])


def _configure_easyauth(
    resource_group: str,
    container_app_name: str,
    tenant_id: str,
    app_id: str,
) -> int:
    """Configure Container Apps EasyAuth using the dedicated az containerapp auth commands.

    Uses the official CLI path documented at
    https://learn.microsoft.com/azure/container-apps/authentication
    which requires two commands: one to register the AAD identity provider and
    one to enable the auth middleware with the desired unauthenticated-client action.
    """
    # Step 1: register the Microsoft identity provider with the client secret reference.
    if _run([
        _AZ_CMD, 'containerapp', 'auth', 'microsoft', 'update',
        '--name', container_app_name,
        '--resource-group', resource_group,
        '--client-id', app_id,
        '--client-secret-name', 'easyauth-client-secret',
        '--tenant-id', tenant_id,
        '--yes',
    ]) != 0:
        return 1
    # Step 2: enable the auth middleware and redirect unauthenticated requests to AAD.
    return _run([
        _AZ_CMD, 'containerapp', 'auth', 'update',
        '--name', container_app_name,
        '--resource-group', resource_group,
        '--enabled', 'true',
        '--action', 'RedirectToLoginPage',
        '--yes',
    ])


def main() -> int:  # pylint: disable=too-many-return-statements
    """Build, push, and configure the Attendee Onboarding Portal."""
    if not _DOCKERFILE.is_file():
        return _fail(f'Dockerfile not found at {_DOCKERFILE}')

    env = _load_azd_env()
    if not env:
        return _fail("Could not read the azd environment. Run 'azd provision' first.")

    deploy_enabled = env.get(
        'AZURE_CONTAINER_APPS_DEPLOY_ENABLED',
        env.get('AZURE_CONTAINER_APPS_DEPLOY', 'true'),
    )
    if not _is_truthy(deploy_enabled):
        print(
            f'{TICK} Azure Container Apps deployment is disabled '
            '(AZURE_CONTAINER_APPS_DEPLOY=false). Skipping attendee portal deploy.'
        )
        return 0

    registry_name = env.get('AZURE_CONTAINER_REGISTRY_NAME', '')
    login_server = env.get('AZURE_CONTAINER_REGISTRY_ENDPOINT', '')
    resource_group = env.get('AZURE_RESOURCE_GROUP', '')
    subscription_id = env.get('AZURE_SUBSCRIPTION_ID', '')
    container_app_name = env.get('AZURE_ATTENDEE_PORTAL_CONTAINER_APP_NAME', '')
    portal_url = env.get('ATTENDEE_PORTAL_URL', '')
    tenant_id = env.get('AZURE_TENANT_ID', '')
    storage_account_name = env.get('AZURE_STORAGE_ACCOUNT_NAME', '')

    if not container_app_name:
        return _fail(
            'AZURE_ATTENDEE_PORTAL_CONTAINER_APP_NAME is not set. '
            'Ensure the portal is provisioned:\n'
            '  azd provision'
        )
    if not (registry_name and login_server and resource_group):
        return _fail('Missing required registry or resource group values in the azd environment.')
    if not tenant_id:
        return _fail('Missing AZURE_TENANT_ID in the azd environment.')
    if not subscription_id:
        return _fail('Missing AZURE_SUBSCRIPTION_ID in the azd environment.')
    if not storage_account_name:
        return _fail('Missing AZURE_STORAGE_ACCOUNT_NAME in the azd environment.')

    tag = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    image = f'{login_server}/attendee-portal:{tag}'

    print(f'Deploying attendee portal image {image} to Container App {container_app_name}...')

    build_steps: list[list[str]] = [
        [_AZ_CMD, 'acr', 'login', '--name', registry_name],
        [
            _DOCKER_CMD, 'build',
            '--tag', image,
            '--file', str(_DOCKERFILE),
            str(_PORTAL_DIR),
        ],
        [_DOCKER_CMD, 'push', image],
        [
            _AZ_CMD, 'containerapp', 'update',
            '--name', container_app_name,
            '--resource-group', resource_group,
            '--image', image,
        ],
    ]

    for step in build_steps:
        if _run(step) != 0:
            return _fail(f'Command failed: {" ".join(step)}')

    print(f'{TICK} Portal image deployed. Ensuring Storage Blob Data Reader role...')

    if _ensure_storage_blob_reader(
        resource_group, container_app_name, storage_account_name, subscription_id,
    ) != 0:
        return _fail('Failed to ensure Storage Blob Data Reader role for portal managed identity.')

    print(f'{TICK} Storage role confirmed. Configuring EasyAuth...')

    # Entra app registration for EasyAuth.
    app_display_name = f'{container_app_name}-easyauth'
    redirect_uri = f'{portal_url}/.auth/login/aad/callback' if portal_url else ''

    if not redirect_uri:
        print(
            f'{TICK} Portal image deployed, but ATTENDEE_PORTAL_URL is not set.\n'
            '   EasyAuth configuration skipped. Re-run after azd provision outputs the URL.',
            file=sys.stderr,
        )
        return 0

    app_id = _find_or_create_app(app_display_name, redirect_uri)
    if not app_id:
        return _fail(f'Failed to find or create Entra app: {app_display_name}')

    _azd_env_set('AZURE_ATTENDEE_PORTAL_APP_ID', app_id)

    # Enable ID token issuance - required for Container Apps EasyAuth.
    # See https://learn.microsoft.com/azure/container-apps/authentication
    if _run([
        _AZ_CMD, 'ad', 'app', 'update',
        '--id', app_id,
        '--enable-id-token-issuance', 'true',
    ]) != 0:
        return _fail('Failed to enable ID token issuance on the Entra app.')

    # Create the service principal if it does not already exist.
    sp_result = subprocess.run(
        [_AZ_CMD, 'ad', 'sp', 'create', '--id', app_id],
        capture_output=True,
        text=True,
        check=False,
    )
    if sp_result.returncode == 0:
        print(f'{TICK} Service principal created for Entra app {app_id}.')
    else:
        # SP already exists - not an error.
        print(f'{TICK} Service principal already exists for Entra app {app_id}.')

    client_secret = _reset_credential(app_id)
    if not client_secret:
        return _fail('Failed to obtain a client secret for the Entra app.')

    if _run([
        _AZ_CMD, 'containerapp', 'secret', 'set',
        '--name', container_app_name,
        '--resource-group', resource_group,
        '--secrets', f'easyauth-client-secret={client_secret}',
    ]) != 0:
        return _fail('Failed to set the EasyAuth client secret on the Container App.')

    if _configure_easyauth(
        resource_group, container_app_name, tenant_id, app_id
    ) != 0:
        return _fail('Failed to configure EasyAuth on the Container App.')

    print(f'{TICK} EasyAuth configured.')
    if portal_url:
        print(f'   Portal URL: {portal_url}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
