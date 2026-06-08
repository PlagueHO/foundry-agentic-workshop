"""Resolve attendee UPNs to Microsoft Entra object IDs and compute project names.

This is the azd preprovision hook for the Microsoft Foundry workshop. It:
  1. Reads AZURE_ATTENDEE_LIST and resolves each attendee UPN to its Entra object ID
     via the Azure CLI ('az ad user show').
  2. Computes each attendee's Foundry project name, mirroring infra/main.bicep exactly.
  3. Writes the enriched list to AZURE_ATTENDEE_LIST_RESOLVED via 'azd env set'.
  4. Writes a resolution audit CSV to .azure/ for early validation.

Bicep reads AZURE_ATTENDEE_LIST_RESOLVED at provision time and creates all RBAC role
assignments directly, using the object IDs and precomputed project names. Attendees
whose UPNs cannot be resolved are included in the resolved list with objectId='' and
resolved=false; Bicep skips role assignments for those entries.

Environment variables (set via `azd env set`):
  AZURE_ATTENDEE_LIST               Input attendee list (single-line JSON array).
  AZURE_ATTENDEE_DEFAULT_ROLE       Default role key (default 'foundry-user').
  AZURE_ATTENDEE_PROJECT_PREFIX     Project name prefix for standard attendees
                                    (default 'attendee').
  AZURE_FACILITATOR_PROJECT_PREFIX  Project name prefix for facilitators
                                    (default 'facilitator').
  AZURE_PROCTOR_PROJECT_PREFIX      Project name prefix for proctors (default 'proctor').
  AZURE_ORGANIZER_PROJECT_PREFIX    Project name prefix for organizers (default 'organizer').
  AZURE_ENSURE_FACILITATOR_PROJECT  Provision a facilitator-01 project even when no
                                    facilitator entry appears in AZURE_ATTENDEE_LIST
                                    (default 'true').
  AZURE_USE_UPN_PROJECT_NAMES       When true (default), project names are derived from
                                    the attendee UPN local part (before @, with '.' and '_'
                                    replaced by '-') instead of sequential prefix-NN names.
  AZURE_ENV_NAME                    azd environment name (used in the audit CSV filename).
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Valid Foundry role keys and their scope level.
# 'project' = role assigned on the attendee's individual Foundry project.
# 'account' = role assigned on the Foundry account resource.
# Mirrors ROLE_DEFINITIONS in scripts/generate-attendee-onboarding.py and
# the var foundryRoleCatalog in infra/main.bicep.
ROLE_SCOPE_LEVELS: dict[str, str] = {
    'foundry-user': 'project',
    'foundry-project-manager': 'account',
    'foundry-account-owner': 'account',
    'foundry-owner': 'account',
    'facilitator': 'account',
    'proctor': 'account',
    'organizer': 'account',
}

DEFAULT_ROLE_KEY = 'foundry-user'

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'


# ---------- helpers ----------

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


def _upn_to_project_name(upn: str) -> str:
    """Derive a Foundry project name from a UPN.

    Takes the local part (before @), replaces '.' and '_' with '-', lowercases,
    and truncates to 32 characters. Mirrors the Bicep expression:
      take(toLower(replace(replace(split(upn, '@')[0], '.', '-'), '_', '-')), 32)
    """
    local = upn.split('@')[0]
    return local.replace('.', '-').replace('_', '-').lower()[:32]


def _compute_attendee_project_name(
    attendee: dict[str, object],
    sequential_index: int,
    prefix: str,
    use_upn_project_names: bool,
) -> str:
    """Compute the Foundry project name for one attendee.

    Priority: explicit projectName > UPN-derived (if use_upn_project_names) > prefix-NN.
    Mirrors the name derivation logic in infra/main.bicep exactly.
    """
    explicit = str(attendee.get('projectName', '') or '').strip()
    if explicit:
        return explicit
    upn = str(attendee['upn']).strip()
    if use_upn_project_names:
        return _upn_to_project_name(upn)
    return f'{prefix}-{sequential_index:02d}'


def _compute_resolved_entries(
    attendees: list[dict[str, object]],
    default_role: str,
    attendee_prefix: str,
    facilitator_prefix: str,
    proctor_prefix: str,
    organizer_prefix: str,
    ensure_facilitator_project: bool,
    use_upn_project_names: bool,
) -> list[dict[str, object]]:
    """Compute project names for all attendees, mirroring infra/main.bicep.

    Sequential counters are only incremented when use_upn_project_names is False
    (matching the Bicep indexed comprehension behaviour). Duplicate UPN-derived names
    are deduplicated by tracking seen names per role group, matching Bicep's union().
    A 'default' standard project is guaranteed to exist (attendee-prefix-01) when the
    standard group would otherwise be empty.
    """
    # First pass: build the ordered list of unique project names per role group so we
    # can identify the default project for individualProject=False attendees.
    standard_names: list[str] = []
    facilitator_names: list[str] = []
    proctor_names: list[str] = []
    organizer_names: list[str] = []

    std_count = fac_count = pro_count = org_count = 0

    for attendee in attendees:
        role = str(attendee.get('role', '') or '').strip() or default_role
        individual = attendee.get('individualProject', True) is not False
        if not individual:
            continue

        if role == 'facilitator':
            if not use_upn_project_names:
                fac_count += 1
            name = _compute_attendee_project_name(attendee, fac_count, facilitator_prefix, use_upn_project_names)
            if name not in facilitator_names:
                facilitator_names.append(name)
        elif role == 'proctor':
            if not use_upn_project_names:
                pro_count += 1
            name = _compute_attendee_project_name(attendee, pro_count, proctor_prefix, use_upn_project_names)
            if name not in proctor_names:
                proctor_names.append(name)
        elif role == 'organizer':
            if not use_upn_project_names:
                org_count += 1
            name = _compute_attendee_project_name(attendee, org_count, organizer_prefix, use_upn_project_names)
            if name not in organizer_names:
                organizer_names.append(name)
        else:
            if not use_upn_project_names:
                std_count += 1
            name = _compute_attendee_project_name(attendee, std_count, attendee_prefix, use_upn_project_names)
            if name not in standard_names:
                standard_names.append(name)

    if not standard_names:
        standard_names.append(f'{attendee_prefix}-01')
    if not facilitator_names and ensure_facilitator_project:
        facilitator_names.append(f'{facilitator_prefix}-01')

    default_project_name = standard_names[0]

    # Second pass: assign a project name to each attendee entry.
    std_idx = fac_idx = pro_idx = org_idx = 0
    results: list[dict[str, object]] = []

    for attendee in attendees:
        upn = str(attendee['upn']).strip()
        role = str(attendee.get('role', '') or '').strip() or default_role
        individual = attendee.get('individualProject', True) is not False

        if not individual:
            project_name = default_project_name
        elif role == 'facilitator':
            if not use_upn_project_names:
                fac_idx += 1
            project_name = _compute_attendee_project_name(attendee, fac_idx, facilitator_prefix, use_upn_project_names)
        elif role == 'proctor':
            if not use_upn_project_names:
                pro_idx += 1
            project_name = _compute_attendee_project_name(attendee, pro_idx, proctor_prefix, use_upn_project_names)
        elif role == 'organizer':
            if not use_upn_project_names:
                org_idx += 1
            project_name = _compute_attendee_project_name(attendee, org_idx, organizer_prefix, use_upn_project_names)
        else:
            if not use_upn_project_names:
                std_idx += 1
            project_name = _compute_attendee_project_name(attendee, std_idx, attendee_prefix, use_upn_project_names)

        results.append({
            'upn': upn,
            'objectId': '',          # filled in by _resolve_object_ids()
            'projectName': project_name,
            'role': role,
            'individualProject': individual,
            'resolved': False,       # updated after resolution
        })

    return results


def _resolve_object_id(upn: str) -> str:
    result = _run_az(['ad', 'user', 'show', '--id', upn, '--query', 'id', '-o', 'tsv'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _resolve_subscription_id() -> str:
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    if subscription_id:
        return subscription_id
    result = _run_az(['account', 'show', '--query', 'id', '-o', 'tsv'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _emit_resolved_list(resolved: list[dict[str, object]]) -> None:
    """Write the resolved attendee list to the azd environment via 'azd env set'."""
    value = json.dumps(resolved, separators=(',', ':'))
    subprocess.run(
        [_AZD_CMD, 'env', 'set', 'AZURE_ATTENDEE_LIST_RESOLVED', value],
        check=True,
    )


def _write_resolution_audit(
    resolved: list[dict[str, object]],
    env_name: str,
) -> Path:
    """Write a per-attendee resolution audit CSV to .azure/."""
    audit_dir = Path('.azure')
    audit_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    audit_path = audit_dir / f'attendee-resolution-{env_name}-{timestamp}.csv'
    fieldnames = ['upn', 'object_id', 'project_name', 'role', 'individual_project', 'resolved', 'message']
    with audit_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in resolved:
            writer.writerow({
                'upn': entry['upn'],
                'object_id': entry['objectId'],
                'project_name': entry['projectName'],
                'role': entry['role'],
                'individual_project': entry['individualProject'],
                'resolved': entry['resolved'],
                'message': '' if entry['resolved'] else 'UPN not resolved to an Entra object ID.',
            })
    return audit_path


# ---------- main ----------

def main() -> int:
    try:
        attendees = _parse_attendee_list(os.getenv('AZURE_ATTENDEE_LIST', ''))
    except (json.JSONDecodeError, ValueError) as error:
        print(f'Invalid AZURE_ATTENDEE_LIST: {error}')
        return 1

    if not attendees:
        print('AZURE_ATTENDEE_LIST is not set or empty. Skipping UPN resolution.')
        print('Bicep will use attendeeCount for sequential project names; no role assignments will be created.')
        return 0

    default_role = os.getenv('AZURE_ATTENDEE_DEFAULT_ROLE', DEFAULT_ROLE_KEY).strip() or DEFAULT_ROLE_KEY
    if default_role not in ROLE_SCOPE_LEVELS:
        valid = ', '.join(sorted(ROLE_SCOPE_LEVELS))
        print(f"Unknown AZURE_ATTENDEE_DEFAULT_ROLE '{default_role}'. Valid values: {valid}.")
        return 1

    attendee_prefix = os.getenv('AZURE_ATTENDEE_PROJECT_PREFIX', 'attendee').strip() or 'attendee'
    facilitator_prefix = os.getenv('AZURE_FACILITATOR_PROJECT_PREFIX', 'facilitator').strip() or 'facilitator'
    proctor_prefix = os.getenv('AZURE_PROCTOR_PROJECT_PREFIX', 'proctor').strip() or 'proctor'
    organizer_prefix = os.getenv('AZURE_ORGANIZER_PROJECT_PREFIX', 'organizer').strip() or 'organizer'
    ensure_facilitator_project = (
        os.getenv('AZURE_ENSURE_FACILITATOR_PROJECT', 'true').strip().lower() not in ('false', '0', '')
    )
    use_upn_project_names = (
        os.getenv('AZURE_USE_UPN_PROJECT_NAMES', 'true').strip().lower() not in ('false', '0', '')
    )
    env_name = os.getenv('AZURE_ENV_NAME', 'workshop').strip() or 'workshop'

    print(f'Resolving {len(attendees)} attendee(s)...')

    resolved = _compute_resolved_entries(
        attendees,
        default_role=default_role,
        attendee_prefix=attendee_prefix,
        facilitator_prefix=facilitator_prefix,
        proctor_prefix=proctor_prefix,
        organizer_prefix=organizer_prefix,
        ensure_facilitator_project=ensure_facilitator_project,
        use_upn_project_names=use_upn_project_names,
    )

    unresolved_count = 0
    for entry in resolved:
        upn = str(entry['upn'])
        object_id = _resolve_object_id(upn)
        if object_id:
            entry['objectId'] = object_id
            entry['resolved'] = True
            print(f'  {upn} -> {object_id} (project: {entry["projectName"]}, role: {entry["role"]})')
        else:
            unresolved_count += 1
            print(f'  {upn} -> UNRESOLVED (project: {entry["projectName"]} will be created; role assignment skipped)')

    print('')
    print(f'Resolution complete: {len(resolved) - unresolved_count} resolved, {unresolved_count} unresolved.')

    _emit_resolved_list(resolved)
    print('AZURE_ATTENDEE_LIST_RESOLVED written to azd environment.')

    audit_path = _write_resolution_audit(resolved, env_name)
    print(f'Resolution audit written to {audit_path}.')

    if unresolved_count:
        print(
            f'\nWarning: {unresolved_count} UPN(s) could not be resolved. '
            'Foundry projects will be created for those attendees but no RBAC role assignments will be made. '
            'Verify the UPNs are correct and the caller has Microsoft Entra directory read access.'
        )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
