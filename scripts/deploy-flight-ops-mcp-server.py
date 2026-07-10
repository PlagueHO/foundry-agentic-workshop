"""Build and deploy the Flight Operations MCP server image to its Azure Container App.

The shared Azure Container Registry uses ABAC repository permissions, which azd's
image-push path cannot authenticate against. This script instead uses the
identity-based path that works against the ABAC registry:

  1. az acr login                     (token exchange using the signed-in identity)
  2. docker build                     (build the MCP server image locally)
  3. docker push                      (push using the ABAC repository role)
  4. az containerapp update --image   (roll the Container App to the new image)

Run it after `azd provision` has created the Container App (which happens by
default unless AZURE_CONTAINER_APPS_DEPLOY is false). This script also runs
automatically as the `azd` postprovision hook; it skips itself when
AZURE_CONTAINER_APPS_DEPLOY is false. All required values are read from the azd
environment, so no arguments are needed.

Prerequisites: azd, the Azure CLI (signed in), and a running Docker engine.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'
_DOCKER_CMD: str = shutil.which('docker') or 'docker'

# Repository root is the parent of the scripts/ directory.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_MCP_SERVER_DIR = _REPO_ROOT / 'shared' / 'mcp-servers' / 'flight-ops'
_DOCKERFILE = _MCP_SERVER_DIR / 'Dockerfile'

# Ensure Unicode output works on Windows terminals that default to cp1252.
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TICK = '\u2705'
CROSS = '\u274c'


def _fail(message: str) -> int:
    """Print a failure message and return a non-zero exit code."""
    print(f'{CROSS} {message}', file=sys.stderr)
    return 1


def _is_truthy(value: object) -> bool:
    """Return True unless the value represents an explicit false-like setting."""
    return str(value).strip().lower() not in ('', 'false', '0', 'no', 'off')


def _wait_for_docker(*, retries: int = 10, delay: float = 3.0) -> bool:
    """Wait for the Docker daemon to be ready. Returns True when ready, False on timeout."""
    print('Waiting for Docker daemon to be ready...')
    sys.stdout.flush()
    for attempt in range(1, retries + 1):
        result = subprocess.run(
            [_DOCKER_CMD, 'info'],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            print(f'{TICK} Docker daemon is ready.')
            sys.stdout.flush()
            return True
        print(f'  Docker not ready yet (attempt {attempt}/{retries}), retrying in {delay:.0f}s...')
        sys.stdout.flush()
        time.sleep(delay)
    return False


def _run(command: list[str], *, cwd: Path | None = None) -> int:
    """Run a command, streaming its output. Return its exit code."""
    print(f'$ {" ".join(command)}')
    sys.stdout.flush()
    return subprocess.run(command, cwd=cwd, check=False).returncode


def _load_azd_env() -> dict[str, str]:
    """Return the azd environment values as a dict, or empty on failure."""
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


def main() -> int:  # pylint: disable=too-many-return-statements
    """Build and push the Flight Ops MCP server image, then roll the Container App to the new revision."""
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
            '(AZURE_CONTAINER_APPS_DEPLOY=false). Skipping Flight Ops MCP server image deploy.'
        )
        return 0

    registry_name = env.get('AZURE_CONTAINER_REGISTRY_NAME', '')
    login_server = env.get('AZURE_CONTAINER_REGISTRY_ENDPOINT', '')
    resource_group = env.get('AZURE_RESOURCE_GROUP', '')
    container_app_name = env.get('AZURE_FLIGHT_OPS_MCP_SERVER_CONTAINER_APP_NAME', '')
    flight_ops_mcp_server_url = env.get('FLIGHT_OPS_MCP_SERVER_URL', '')

    if not container_app_name:
        return _fail(
            'The Flight Ops MCP server Container App is not provisioned. '
            'Enable Container Apps and provision first:\n'
            '  azd env set AZURE_CONTAINER_APPS_DEPLOY true\n'
            '  azd provision'
        )
    if not (registry_name and login_server and resource_group):
        return _fail('The azd environment is missing required registry or resource group values.')

    # Unique, time-based tag so `containerapp update` always rolls to a new revision.
    tag = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    image = f'{login_server}/flight-ops-mcp-server:{tag}'

    print(f'Deploying Flight Ops MCP server image {image} to Container App {container_app_name}...')
    sys.stdout.flush()

    if not _wait_for_docker():
        return _fail('Docker daemon did not become ready in time. Ensure Docker Desktop is running.')

    steps: list[tuple[str, list[str]]] = [
        ('Step 1/4: Authenticating with Container Registry...', [_AZ_CMD, 'acr', 'login', '--name', registry_name]),
        ('Step 2/4: Building Docker image (this may take a few minutes)...', [_DOCKER_CMD, 'build', '--tag', image, '--file', str(_DOCKERFILE), str(_MCP_SERVER_DIR)]),
        ('Step 3/4: Pushing image to registry...', [_DOCKER_CMD, 'push', image]),
        ('Step 4/4: Rolling Container App to new revision...', [
            _AZ_CMD, 'containerapp', 'update',
            '--name', container_app_name,
            '--resource-group', resource_group,
            '--image', image,
        ]),
    ]

    for label, step in steps:
        print(label)
        if _run(step) != 0:
            return _fail(f'Command failed: {" ".join(step)}')

    print(f'{TICK} Flight Ops MCP server deployed.')
    if flight_ops_mcp_server_url:
        print(f'   MCP endpoint: {flight_ops_mcp_server_url}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
