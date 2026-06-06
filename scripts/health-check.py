"""Basic workshop environment health check."""

import os
import subprocess
import sys

REQUIRED_ENV_VARS = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'FOUNDRY_RESOURCE_NAME',
    'FOUNDRY_PROJECT_NAME',
]


def main() -> int:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        print('Missing required environment variables:')
        for name in missing:
            print(f'- {name}')
        return 1

    try:
        subscription_id = subprocess.check_output(
            ['az', 'account', 'show', '--query', 'id', '-o', 'tsv'],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print('Azure CLI check failed. Run `az login` and ensure `az` is installed.')
        return 1

    configured_subscription = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    if configured_subscription and subscription_id != configured_subscription:
        print('AZURE_SUBSCRIPTION_ID does not match the active Azure CLI subscription.')
        print(f'- Active: {subscription_id}')
        print(f'- Expected: {configured_subscription}')
        print('Run `az account set --subscription <AZURE_SUBSCRIPTION_ID>` and try again.')
        return 1

    print('Environment variables and Azure CLI context look good.')
    print('Next: run the lab setup in labs/introduction-foundry-agent-service/00-setup.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
