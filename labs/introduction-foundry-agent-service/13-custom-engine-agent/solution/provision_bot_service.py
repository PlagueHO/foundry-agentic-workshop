"""Provision the attendee-owned identity and Azure Bot Service for Module 13."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'infra' / 'bot-service.bicep'


def run_az(arguments: list[str]) -> str:
    """Run Azure CLI and return its JSON or text output."""
    az = shutil.which('az')
    if az is None:
        raise RuntimeError('Azure CLI was not found. Install it and run az login.')
    result = subprocess.run([az, *arguments], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'Azure CLI command failed.')
    return result.stdout.strip()


def run() -> None:
    """Create the app registration and deploy the standalone Bot Service template."""
    load_dotenv()

    display_name = os.environ.get('BOT_APP_DISPLAY_NAME', 'ACL Remedy Advisor Custom Engine Agent')
    resource_group = os.environ.get('BOT_RESOURCE_GROUP', 'rg-acl-remedy-advisor-cea')
    location = os.environ.get('BOT_LOCATION', 'australiaeast')
    bot_service_name = os.environ.get('BOT_SERVICE_NAME', 'acl-remedy-advisor-cea')
    messaging_endpoint = os.environ.get('BOT_MESSAGING_ENDPOINT', '').strip()
    if not messaging_endpoint.startswith('https://') or not messaging_endpoint.endswith('/api/messages'):
        raise ValueError('BOT_MESSAGING_ENDPOINT must be an HTTPS URL ending in /api/messages.')

    account = json.loads(run_az(['account', 'show', '-o', 'json']))
    tenant_id = os.environ.get('BOT_TENANT_ID', account['tenantId'])
    app = json.loads(
        run_az(
            [
                'ad', 'app', 'create', '--display-name', display_name,
                '--sign-in-audience', 'AzureADMyOrg',
                '--query', '{appId:appId,objectId:id}', '-o', 'json',
            ]
        )
    )
    app_client_id = app['appId']
    secret = json.loads(
        run_az(
            [
                'ad', 'app', 'credential', 'reset', '--id', app_client_id,
                '--append', '--display-name', 'Module 13 local development',
                '--years', '1', '-o', 'json',
            ]
        )
    )

    run_az(['group', 'create', '--name', resource_group, '--location', location, '-o', 'none'])
    run_az(
        [
            'deployment', 'group', 'create', '--resource-group', resource_group,
            '--template-file', str(TEMPLATE), '--parameters',
            f'botServiceName={bot_service_name}', f'appClientId={app_client_id}',
            f'tenantId={tenant_id}', f'messagingEndpoint={messaging_endpoint}',
            f'location={location}', '-o', 'none',
        ]
    )

    print('Bot Service provisioned. Add these values to your local .env file:')
    print(f'BOT_APP_CLIENT_ID={app_client_id}')
    print(f'BOT_APP_CLIENT_SECRET={secret["password"]}')
    print(f'BOT_TENANT_ID={tenant_id}')
    print(f'BOT_SERVICE_NAME={bot_service_name}')
    print(f'BOT_RESOURCE_GROUP={resource_group}')


if __name__ == '__main__':
    run()
