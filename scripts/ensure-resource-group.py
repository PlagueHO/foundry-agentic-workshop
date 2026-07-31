# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

"""Ensure the azd target resource group exists before an RG-scoped deployment."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


_AZ_COMMAND = shutil.which('az') or 'az'


def _run_az(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_AZ_COMMAND, *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def _env(name: str) -> str:
    return os.environ.get(name, '').strip()


def main() -> int:
    """Reuse the configured RG or create it when the caller has permission."""
    resource_group = _env('AZURE_RESOURCE_GROUP')
    location = _env('AZURE_LOCATION')

    if not resource_group:
        print(
            'AZURE_RESOURCE_GROUP is not set. Select or create an azd environment '
            'with a resource group before provisioning.',
            file=sys.stderr,
        )
        return 1
    if not location:
        print(
            'AZURE_LOCATION is not set. Set the Azure region before provisioning.',
            file=sys.stderr,
        )
        return 1

    exists = _run_az(['group', 'exists', '--name', resource_group, '--output', 'tsv'])
    if exists.returncode != 0:
        detail = exists.stderr.strip() or exists.stdout.strip() or 'az group exists failed'
        print(f'Could not check resource group {resource_group}: {detail}', file=sys.stderr)
        return 1

    if exists.stdout.strip().lower() == 'true':
        print(f'Reusing existing resource group: {resource_group}')
        return 0

    print(f'Creating resource group {resource_group} in {location}.')
    created = _run_az(
        [
            'group',
            'create',
            '--name',
            resource_group,
            '--location',
            location,
            '--output',
            'none',
        ]
    )
    if created.returncode == 0:
        print(f'Resource group ready: {resource_group}')
        return 0

    detail = created.stderr.strip() or created.stdout.strip() or 'az group create failed'
    print(
        f'Could not create resource group {resource_group}. Existing RG-only users must '
        'use a pre-created resource group, while subscription-scope users need permission '
        'to create resource groups at subscription scope.',
        file=sys.stderr,
    )
    print(f'Azure CLI detail: {detail}', file=sys.stderr)
    print(
        'Ask an administrator to run: '
        f"az group create --name {resource_group} --location {location}",
        file=sys.stderr,
    )
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
