"""Assign Microsoft Foundry project roles to workshop attendees.

Bicep cannot resolve a user principal name (UPN) to a Microsoft Entra object ID,
so per-attendee role assignments are applied here as an azd postprovision step.

For each attendee, this script:
  1. Resolves the attendee UPN to an Entra object ID via the Azure CLI.
  2. Grants the configured Foundry role on the attendee's Foundry project.

Environment variables (set via `azd env set`):
  AZURE_ATTENDEE_USER_PRINCIPAL_NAMES  JSON array or comma-separated list of UPNs.
  AZURE_ATTENDEE_ACCESS_PROFILE        'project-user' (default) or 'project-publisher'.
  AZURE_ATTENDEE_PROJECT_PREFIX        Project name prefix (default 'attendee').
  AZURE_ATTENDEE_COUNT                 Number of attendee projects (default len(UPNs)).
  FOUNDRY_RESOURCE_NAME                Foundry account name (azd output).
  AZURE_RESOURCE_GROUP                 Resource group name (azd output).
  AZURE_SUBSCRIPTION_ID                Subscription id (optional; resolved if unset).
"""

from __future__ import annotations

import json
import os
import subprocess

# Foundry built-in role definition IDs, keyed by attendee access profile.
ACCESS_PROFILE_ROLES: dict[str, str] = {
    'project-user': '53ca6127-db72-4b80-b1b0-d745d6d5456d',  # Foundry User
    'project-publisher': 'eadc314b-1a2d-4efa-be10-5d325db5065e',  # Foundry Project Manager
}


def _run_az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['az', *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_user_principal_names(raw: str) -> list[str]:
    stripped = raw.strip()
    if not stripped:
        return []
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in stripped.split(',') if item.strip()]


def _resolve_subscription_id() -> str:
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    if subscription_id:
        return subscription_id
    result = _run_az(['account', 'show', '--query', 'id', '-o', 'tsv'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _resolve_object_id(user_principal_name: str) -> str:
    result = _run_az(['ad', 'user', 'show', '--id', user_principal_name, '--query', 'id', '-o', 'tsv'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _assign_role(object_id: str, role_definition_id: str, scope: str) -> bool:
    result = _run_az([
        'role', 'assignment', 'create',
        '--assignee-object-id', object_id,
        '--assignee-principal-type', 'User',
        '--role', role_definition_id,
        '--scope', scope,
    ])
    if result.returncode != 0:
        print(f'  Failed to assign role: {result.stderr.strip()}')
        return False
    return True


def main() -> int:
    user_principal_names = _parse_user_principal_names(
        os.getenv('AZURE_ATTENDEE_USER_PRINCIPAL_NAMES', '')
    )
    if not user_principal_names:
        print('AZURE_ATTENDEE_USER_PRINCIPAL_NAMES is not set. Skipping attendee role assignment.')
        return 0

    access_profile = os.getenv('AZURE_ATTENDEE_ACCESS_PROFILE', 'project-user').strip() or 'project-user'
    role_definition_id = ACCESS_PROFILE_ROLES.get(access_profile)
    if role_definition_id is None:
        valid = ', '.join(sorted(ACCESS_PROFILE_ROLES))
        print(f"Unknown AZURE_ATTENDEE_ACCESS_PROFILE '{access_profile}'. Valid values: {valid}.")
        return 1

    project_prefix = os.getenv('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee').strip() or 'attendee'
    foundry_name = os.getenv('FOUNDRY_RESOURCE_NAME', '').strip()
    resource_group = os.getenv('AZURE_RESOURCE_GROUP', '').strip()
    if not foundry_name or not resource_group:
        print('FOUNDRY_RESOURCE_NAME and AZURE_RESOURCE_GROUP must be set. Skipping attendee role assignment.')
        return 1

    subscription_id = _resolve_subscription_id()
    if not subscription_id:
        print('Unable to resolve the subscription id. Skipping attendee role assignment.')
        return 1

    attendee_count = int(os.getenv('AZURE_ATTENDEE_COUNT', str(len(user_principal_names))))

    failures = 0
    for index in range(1, attendee_count + 1):
        project_name = f'{project_prefix}-{index:02d}'
        if index > len(user_principal_names):
            print(f'No attendee UPN provided for project {project_name}. Skipping.')
            continue

        user_principal_name = user_principal_names[index - 1]
        print(f'Assigning {access_profile} on {project_name} to {user_principal_name}.')

        object_id = _resolve_object_id(user_principal_name)
        if not object_id:
            print(f'  Could not resolve object id for {user_principal_name}. Check the UPN and directory read access.')
            failures += 1
            continue

        scope = (
            f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
            f'/providers/Microsoft.CognitiveServices/accounts/{foundry_name}/projects/{project_name}'
        )
        if not _assign_role(object_id=object_id, role_definition_id=role_definition_id, scope=scope):
            failures += 1

    if failures:
        print(f'Completed with {failures} failed attendee role assignment(s).')
        return 1

    print('Attendee role assignments completed successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
