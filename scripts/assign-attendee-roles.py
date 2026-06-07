"""Assign Microsoft Foundry roles to workshop attendees.

Bicep cannot resolve a user principal name (UPN) to a Microsoft Entra object ID,
so per-attendee role assignments are applied here as an azd postprovision step.
The structured attendee list in AZURE_ATTENDEE_LIST is the single source of truth
for both project creation (Bicep) and role assignment (this script).

For each attendee, this script:
  1. Resolves the attendee UPN to an Entra object ID via the Azure CLI.
  2. Resolves the attendee role key to a Foundry built-in role and scope.
  3. Grants that role at the resolved scope (the attendee project, or the
     Foundry account for account-scoped roles).
  4. Records the outcome in a CSV audit file and a console summary.

Environment variables (set via `azd env set`):
  AZURE_ATTENDEE_LIST           Single-line JSON array of attendee objects:
                                  { "upn": required,
                                    "role"?: role key (see ROLE_DEFINITIONS),
                                    "individualProject"?: bool (default true),
                                    "projectName"?: explicit project name }.
  AZURE_ATTENDEE_DEFAULT_ROLE   Default role key for attendees without "role"
                                  (default 'foundry-user').
  AZURE_ATTENDEE_PROJECT_PREFIX Project name prefix for standard attendees
                                  (default 'attendee').
  AZURE_FACILITATOR_PROJECT_PREFIX  Project name prefix for facilitators
                                    (default 'facilitator').
  AZURE_PROCTOR_PROJECT_PREFIX  Project name prefix for proctors (default 'proctor').
  AZURE_ORGANIZER_PROJECT_PREFIX  Project name prefix for organizers (default 'organizer').
  AZURE_ENSURE_FACILITATOR_PROJECT  Provision a facilitator-01 project even when no
                                    facilitator is in attendeeList (default 'true').
  FOUNDRY_RESOURCE_NAME         Foundry account name (azd output).
  AZURE_RESOURCE_GROUP          Resource group name (azd output).
  AZURE_SUBSCRIPTION_ID         Subscription id (optional; resolved if unset).
  AZURE_ENV_NAME                azd environment name (used in the audit filename).
  AZURE_SEARCH_SERVICE_NAME     Azure AI Search service name (azd output). When set,
                                  a paired Search role is also assigned (see
                                  SEARCH_ROLE_DEFINITIONS).
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Foundry built-in roles keyed by attendee role.
# Each value is (display_name, role_definition_id, scope_level) where scope_level
# is 'project' (assigned on the attendee project) or 'account' (assigned on the
# Foundry account, granting capabilities that span projects such as model
# deployment and cross-project publishing).
ROLE_DEFINITIONS: dict[str, tuple[str, str, str]] = {
    'foundry-user': ('Foundry User', '53ca6127-db72-4b80-b1b0-d745d6d5456d', 'project'),
    'foundry-project-manager': ('Foundry Project Manager', 'eadc314b-1a2d-4efa-be10-5d325db5065e', 'account'),
    'foundry-account-owner': ('Foundry Account Owner', 'e47c6f54-e4a2-4754-9501-8e0985b135e1', 'account'),
    'foundry-owner': ('Foundry Owner', 'c883944f-8b7b-4483-af10-35834be79c4a', 'account'),
    # Workshop staff roles — all equivalent to foundry-owner at account scope.
    # Projects are named under role-specific prefixes (facilitator-NN, proctor-NN, organizer-NN).
    'facilitator': ('Foundry Owner', 'c883944f-8b7b-4483-af10-35834be79c4a', 'account'),
    'proctor': ('Foundry Owner', 'c883944f-8b7b-4483-af10-35834be79c4a', 'account'),
    'organizer': ('Foundry Owner', 'c883944f-8b7b-4483-af10-35834be79c4a', 'account'),
}

# Azure AI Search built-in roles assigned alongside each Foundry role.
# Keyed by Foundry role key; each value is (role_key, display_name, role_definition_id).
# See https://learn.microsoft.com/en-us/azure/search/search-security-rbac
SEARCH_ROLE_DEFINITIONS: dict[str, tuple[str, str, str]] = {
    'foundry-user': ('search-index-data-reader', 'Search Index Data Reader', '1407120a-92aa-4202-b7e9-c0e197c71c8f'),
    'foundry-project-manager': ('search-index-data-contributor', 'Search Index Data Contributor', '8ebe5a00-799e-43f5-93ac-243d3dce84a7'),
    'foundry-account-owner': ('search-service-contributor', 'Search Service Contributor', '7ca78c08-252a-4471-8644-bb5ff32d4ba0'),
    'foundry-owner': ('search-contributor', 'Contributor', 'b24988ac-6180-42a0-ab88-20f7382dd24c'),
    'facilitator': ('search-contributor', 'Contributor', 'b24988ac-6180-42a0-ab88-20f7382dd24c'),
    'proctor': ('search-contributor', 'Contributor', 'b24988ac-6180-42a0-ab88-20f7382dd24c'),
    'organizer': ('search-contributor', 'Contributor', 'b24988ac-6180-42a0-ab88-20f7382dd24c'),
}

DEFAULT_ROLE_KEY = 'foundry-user'

# Resolve the Azure CLI executable; on Windows it is az.cmd which subprocess
# cannot find by bare name without shell=True.
_AZ_CMD: str = shutil.which('az') or 'az'


def _run_az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_AZ_CMD, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_attendee_list(raw: str) -> list[dict[str, object]]:
    stripped = raw.strip()
    if not stripped:
        return []
    parsed = json.loads(stripped)
    if not isinstance(parsed, list):
        raise ValueError('AZURE_ATTENDEE_LIST must be a JSON array of attendee objects.')
    attendees: list[dict[str, object]] = []
    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError('Each AZURE_ATTENDEE_LIST entry must be a JSON object.')
        if not str(item.get('upn', '')).strip():
            raise ValueError("Each AZURE_ATTENDEE_LIST entry requires a non-empty 'upn'.")
        attendees.append(item)
    return attendees


def _project_name_for(attendee: dict[str, object], index: int, project_prefix: str) -> str:
    explicit = str(attendee.get('projectName', '')).strip()
    if explicit:
        return explicit
    return f'{project_prefix}-{index:02d}'


def _resolve_project_names(
    attendees: list[dict[str, object]],
    attendee_prefix: str,
    facilitator_prefix: str,
    proctor_prefix: str,
    organizer_prefix: str,
    ensure_facilitator_project: bool,
) -> list[str]:
    """Derive the ordered project list matching what Bicep creates.

    Mirrors the derivation in infra/main.bicep so role scopes line up exactly.
    Standard attendees are numbered within their own group; facilitator, proctor,
    and organizer entries are numbered within their respective groups.
    """
    standard: list[str] = []
    facilitator: list[str] = []
    proctor: list[str] = []
    organizer: list[str] = []

    for attendee in attendees:
        role = str(attendee.get('role', '') or '').strip()
        if attendee.get('individualProject', True) is False:
            continue
        explicit = str(attendee.get('projectName', '') or '').strip()
        if role == 'facilitator':
            name = explicit or f'{facilitator_prefix}-{len(facilitator) + 1:02d}'
            if name not in facilitator:
                facilitator.append(name)
        elif role == 'proctor':
            name = explicit or f'{proctor_prefix}-{len(proctor) + 1:02d}'
            if name not in proctor:
                proctor.append(name)
        elif role == 'organizer':
            name = explicit or f'{organizer_prefix}-{len(organizer) + 1:02d}'
            if name not in organizer:
                organizer.append(name)
        else:
            name = explicit or f'{attendee_prefix}-{len(standard) + 1:02d}'
            if name not in standard:
                standard.append(name)

    if not standard:
        standard.append(f'{attendee_prefix}-01')
    if not facilitator and ensure_facilitator_project:
        facilitator.append(f'{facilitator_prefix}-01')

    return standard + facilitator + proctor + organizer


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


def _account_scope(subscription_id: str, resource_group: str, foundry_name: str) -> str:
    return (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.CognitiveServices/accounts/{foundry_name}'
    )


def _search_scope(subscription_id: str, resource_group: str, search_service_name: str) -> str:
    return (
        f'/subscriptions/{subscription_id}/resourceGroups/{resource_group}'
        f'/providers/Microsoft.Search/searchServices/{search_service_name}'
    )


def _assign_role(object_id: str, role_definition_id: str, scope: str) -> tuple[bool, str]:
    result = _run_az([
        'role', 'assignment', 'create',
        '--assignee-object-id', object_id,
        '--assignee-principal-type', 'User',
        '--role', role_definition_id,
        '--scope', scope,
    ])
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ''


def _write_audit_csv(rows: list[dict[str, str]]) -> Path:
    audit_dir = Path('.azure')
    audit_dir.mkdir(exist_ok=True)
    env_name = os.getenv('AZURE_ENV_NAME', 'workshop').strip() or 'workshop'
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    audit_path = audit_dir / f'attendee-provisioning-{env_name}-{timestamp}.csv'
    fieldnames = [
        'upn', 'object_id', 'role_key', 'role_display_name',
        'role_definition_id', 'project_name', 'scope', 'status', 'message',
    ]
    with audit_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return audit_path


def _print_summary(rows: list[dict[str, str]]) -> None:
    succeeded = sum(1 for row in rows if row['status'] == 'succeeded')
    failed = sum(1 for row in rows if row['status'] == 'failed')
    per_role: dict[str, int] = {}
    for row in rows:
        per_role[row['role_key']] = per_role.get(row['role_key'], 0) + 1

    print('')
    print('Attendee role assignment summary')
    print(f'  Succeeded: {succeeded}')
    print(f'  Failed:    {failed}')
    print('  Per role:')
    for role_key in sorted(per_role):
        print(f'    {role_key}: {per_role[role_key]}')


def main() -> int:
    try:
        attendees = _parse_attendee_list(os.getenv('AZURE_ATTENDEE_LIST', ''))
    except (json.JSONDecodeError, ValueError) as error:
        print(f'Invalid AZURE_ATTENDEE_LIST: {error}')
        return 1

    if not attendees:
        print('AZURE_ATTENDEE_LIST is not set. Skipping attendee role assignment.')
        return 0

    default_role = os.getenv('AZURE_ATTENDEE_DEFAULT_ROLE', DEFAULT_ROLE_KEY).strip() or DEFAULT_ROLE_KEY
    if default_role not in ROLE_DEFINITIONS:
        valid = ', '.join(sorted(ROLE_DEFINITIONS))
        print(f"Unknown AZURE_ATTENDEE_DEFAULT_ROLE '{default_role}'. Valid values: {valid}.")
        return 1

    project_prefix = os.getenv('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee').strip() or 'attendee'
    facilitator_prefix = os.getenv('AZURE_FACILITATOR_PROJECT_PREFIX', 'facilitator').strip() or 'facilitator'
    proctor_prefix = os.getenv('AZURE_PROCTOR_PROJECT_PREFIX', 'proctor').strip() or 'proctor'
    organizer_prefix = os.getenv('AZURE_ORGANIZER_PROJECT_PREFIX', 'organizer').strip() or 'organizer'
    ensure_facilitator_project = (
        os.getenv('AZURE_ENSURE_FACILITATOR_PROJECT', 'true').strip().lower() not in ('false', '0', '')
    )
    foundry_name = os.getenv('FOUNDRY_RESOURCE_NAME', '').strip()
    resource_group = os.getenv('AZURE_RESOURCE_GROUP', '').strip()
    if not foundry_name or not resource_group:
        print('FOUNDRY_RESOURCE_NAME and AZURE_RESOURCE_GROUP must be set. Skipping attendee role assignment.')
        return 1

    search_service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()
    if not search_service_name:
        print('AZURE_SEARCH_SERVICE_NAME is not set. Azure AI Search role assignments will be skipped.')

    subscription_id = _resolve_subscription_id()
    if not subscription_id:
        print('Unable to resolve the subscription id. Skipping attendee role assignment.')
        return 1

    project_names = _resolve_project_names(
        attendees,
        attendee_prefix=project_prefix,
        facilitator_prefix=facilitator_prefix,
        proctor_prefix=proctor_prefix,
        organizer_prefix=organizer_prefix,
        ensure_facilitator_project=ensure_facilitator_project,
    )
    default_project_name = project_names[0]
    account_scope = _account_scope(subscription_id, resource_group, foundry_name)
    search_svc_scope = _search_scope(subscription_id, resource_group, search_service_name) if search_service_name else ''

    rows: list[dict[str, str]] = []
    standard_attendee_count = 0  # index within the standard-attendee group only
    facilitator_count = 0
    proctor_count = 0
    organizer_count = 0
    for attendee in attendees:
        upn = str(attendee['upn']).strip()
        role_key = str(attendee.get('role', '') or default_role).strip()

        display_name, role_definition_id, scope_level = ('', '', '')
        if role_key not in ROLE_DEFINITIONS:
            valid = ', '.join(sorted(ROLE_DEFINITIONS))
            message = f"Unknown role '{role_key}'. Valid values: {valid}."
            print(f'{upn}: {message}')
            rows.append({
                'upn': upn, 'object_id': '', 'role_key': role_key,
                'role_display_name': '', 'role_definition_id': '',
                'project_name': '', 'scope': '', 'status': 'failed', 'message': message,
            })
            continue

        display_name, role_definition_id, scope_level = ROLE_DEFINITIONS[role_key]

        individual = attendee.get('individualProject', True) is not False
        if scope_level == 'account':
            scope = account_scope
            if individual:
                if role_key == 'facilitator':
                    facilitator_count += 1
                    target_project_name = _project_name_for(attendee, facilitator_count, facilitator_prefix)
                elif role_key == 'proctor':
                    proctor_count += 1
                    target_project_name = _project_name_for(attendee, proctor_count, proctor_prefix)
                elif role_key == 'organizer':
                    organizer_count += 1
                    target_project_name = _project_name_for(attendee, organizer_count, organizer_prefix)
                else:
                    standard_attendee_count += 1
                    target_project_name = _project_name_for(attendee, standard_attendee_count, project_prefix)
            else:
                target_project_name = default_project_name
        else:
            standard_attendee_count += 1
            target_project_name = (
                _project_name_for(attendee, standard_attendee_count, project_prefix)
                if individual
                else default_project_name
            )
            scope = f'{account_scope}/projects/{target_project_name}'

        scope_label = target_project_name if scope_level == 'project' else 'account'
        print(f'Assigning {display_name} ({scope_level} scope) to {upn} on {scope_label}.')

        object_id = _resolve_object_id(upn)
        if not object_id:
            message = 'Could not resolve object id. Check the UPN and directory read access.'
            print(f'  {message}')
            rows.append({
                'upn': upn, 'object_id': '', 'role_key': role_key,
                'role_display_name': display_name, 'role_definition_id': role_definition_id,
                'project_name': target_project_name, 'scope': scope_level,
                'status': 'failed', 'message': message,
            })
            continue

        assigned, error_message = _assign_role(
            object_id=object_id, role_definition_id=role_definition_id, scope=scope
        )
        if not assigned:
            print(f'  Failed to assign role: {error_message}')
        rows.append({
            'upn': upn, 'object_id': object_id, 'role_key': role_key,
            'role_display_name': display_name, 'role_definition_id': role_definition_id,
            'project_name': target_project_name, 'scope': scope_level,
            'status': 'succeeded' if assigned else 'failed', 'message': error_message,
        })

        if search_svc_scope and role_key in SEARCH_ROLE_DEFINITIONS:
            search_role_key, search_display_name, search_role_def_id = SEARCH_ROLE_DEFINITIONS[role_key]
            print(f'Assigning {search_display_name} (search scope) to {upn}.')
            search_assigned, search_error = _assign_role(
                object_id=object_id, role_definition_id=search_role_def_id, scope=search_svc_scope,
            )
            if not search_assigned:
                print(f'  Failed to assign search role: {search_error}')
            rows.append({
                'upn': upn, 'object_id': object_id, 'role_key': search_role_key,
                'role_display_name': search_display_name, 'role_definition_id': search_role_def_id,
                'project_name': '', 'scope': 'search',
                'status': 'succeeded' if search_assigned else 'failed', 'message': search_error,
            })

    audit_path = _write_audit_csv(rows)
    _print_summary(rows)
    print(f'\nAudit written to {audit_path}.')

    failures = sum(1 for row in rows if row['status'] == 'failed')
    if failures:
        print(f'Completed with {failures} failed attendee role assignment(s).')
        return 1

    print('Attendee role assignments completed successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
