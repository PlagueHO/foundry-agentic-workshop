"""Delete the Entra app registration created for the Attendee Onboarding Portal EasyAuth.

This script runs as the `azd` predown hook to clean up the Entra app registration
created by deploy-attendee-portal.py before the infrastructure is torn down. It is
idempotent: if the app has already been deleted or was never created, it exits cleanly.

All required values are read from the azd environment; no arguments are needed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TICK = '\u2705'
CROSS = '\u274c'


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


def main() -> int:
    """Delete the EasyAuth Entra app registration and clear the stored app ID."""
    env = _load_azd_env()
    app_id = env.get('AZURE_ATTENDEE_PORTAL_APP_ID', '').strip()

    if not app_id:
        print(
            f'{TICK} AZURE_ATTENDEE_PORTAL_APP_ID is not set; '
            'no Entra app to delete.'
        )
        return 0

    print(f'Deleting Entra app registration {app_id}...')
    result = subprocess.run(
        [_AZ_CMD, 'ad', 'app', 'delete', '--id', app_id],
        check=False,
    )
    if result.returncode != 0:
        print(
            f'{CROSS} Failed to delete Entra app {app_id} '
            '(it may have already been deleted).',
            file=sys.stderr,
        )
        # Return 0 so azd down is not blocked by a missing app.
        return 0

    # Clear the stored app ID so re-provision starts fresh.
    subprocess.run(
        [_AZD_CMD, 'env', 'set', 'AZURE_ATTENDEE_PORTAL_APP_ID', ''],
        check=False,
    )

    print(f'{TICK} Entra app {app_id} deleted.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
