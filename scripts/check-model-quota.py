"""Validate model quota and availability before azd provision.

This is the first azd preprovision hook for the Microsoft Foundry workshop. It:
  1. Resolves the effective model-deployment profile (auto / individual-mode default / explicit).
  2. When profile is 'auto' or AZURE_INDIVIDUAL_MODE=true with no profile set, picks the
     largest profile that fits the target region's available quota and writes the concrete
     value via 'azd env set AZURE_MODEL_DEPLOYMENT_PROFILE'.
  3. Validates model availability in the target region via 'az cognitiveservices model list'.
  4. Validates quota sufficiency via 'az cognitiveservices usage list'.
  5. On shortfall: prints a required-vs-available table, recommends a fitting profile,
     suggests an alternate region from a curated candidate list, and exits non-zero.
  6. Skips the check entirely when AZURE_MODEL_QUOTA_CHECK=false.
  7. Validates that AZURE_LOCATION and AZURE_ENV_NAME are set.

Environment variables consumed:
  AZURE_LOCATION                  Required. Azure region for the deployment.
  AZURE_ENV_NAME                  Required. azd environment name.
  AZURE_MODEL_DEPLOYMENT_PROFILE  Profile to use: minimal | default | workshop | broad | auto.
                                  When unset, defaults to 'default' for individual mode
                                  (AZURE_INDIVIDUAL_MODE=true) or 'workshop' for organizer
                                  deployments. 'auto' triggers automatic quota-based selection.
  AZURE_MODEL_DEPLOYMENTS         Inline JSON array of deployment objects. Overrides profile.
  AZURE_MODEL_QUOTA_CHECK         Set to 'false' to skip the check entirely.
  AZURE_INDIVIDUAL_MODE           When 'true', defaults profile to 'default' (cap 50) instead
                                  of 'workshop' (cap 200).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPT_DIR.parent
_INFRA_DIR = _REPO_ROOT / 'infra'

_PROFILE_FILES: dict[str, Path] = {
    'minimal':  _INFRA_DIR / 'model-deployments.minimal.json',
    'default':  _INFRA_DIR / 'model-deployments.default.json',
    'workshop': _INFRA_DIR / 'model-deployments.workshop.json',
    'broad':    _INFRA_DIR / 'model-deployments.broad.json',
}

# Ordered from smallest to largest — used for auto-selection (largest-that-fits).
_PROFILES_ASCENDING = ['minimal', 'default', 'workshop', 'broad']

# Curated candidate regions to suggest when the chosen region lacks quota.
_CANDIDATE_REGIONS = [
    'eastus',
    'eastus2',
    'westus',
    'westus3',
    'northcentralus',
    'southcentralus',
    'swedencentral',
    'westeurope',
    'northeurope',
    'uksouth',
    'australiaeast',
    'japaneast',
    'southeastasia',
    'canadacentral',
]

_AZ_CMD: str = shutil.which('az') or 'az'
_AZD_CMD: str = shutil.which('azd') or 'azd'

# ---------------------------------------------------------------------------
# Helpers — subprocess
# ---------------------------------------------------------------------------


def _run_az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_AZ_CMD, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _azd_env_set(key: str, value: str) -> None:
    result = subprocess.run(
        [_AZD_CMD, 'env', 'set', key, value],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f'  Warning: could not write {key} via azd env set: {result.stderr.strip()}',
              file=sys.stderr)


# ---------------------------------------------------------------------------
# Helpers — environment
# ---------------------------------------------------------------------------


def _is_truthy(value: str | None) -> bool:
    return str(value or '').strip().lower() not in ('', '0', 'false', 'no', 'off')


def _load_env() -> dict[str, str]:
    """Return a snapshot of the relevant environment variables."""
    keys = [
        'AZURE_LOCATION',
        'AZURE_ENV_NAME',
        'AZURE_MODEL_DEPLOYMENT_PROFILE',
        'AZURE_MODEL_DEPLOYMENTS',
        'AZURE_MODEL_QUOTA_CHECK',
        'AZURE_INDIVIDUAL_MODE',
    ]
    return {k: os.environ.get(k, '') for k in keys}


def _validate_required_env(env: dict[str, str]) -> list[str]:
    """Return a list of error messages for missing required env vars."""
    errors: list[str] = []
    if not env['AZURE_LOCATION'].strip():
        errors.append(
            "AZURE_LOCATION is not set. Run: azd env set AZURE_LOCATION <region>  "
            "(e.g. eastus2)"
        )
    if not env['AZURE_ENV_NAME'].strip():
        errors.append(
            "AZURE_ENV_NAME is not set. Run: azd env new <name>  to create an environment."
        )
    return errors


# ---------------------------------------------------------------------------
# Helpers — profile / deployment resolution
# ---------------------------------------------------------------------------


def _load_profile_deployments(profile: str) -> list[dict]:
    path = _PROFILE_FILES[profile]
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _resolve_deployments(env: dict[str, str]) -> tuple[list[dict], str | None]:
    """Return (deployments, source_label).

    source_label is None when an inline override is used (no profile written back).
    """
    override_raw = env['AZURE_MODEL_DEPLOYMENTS'].strip()
    if override_raw:
        try:
            deployments = json.loads(override_raw)
        except json.JSONDecodeError as exc:
            print(f'Error: AZURE_MODEL_DEPLOYMENTS is not valid JSON: {exc}', file=sys.stderr)
            sys.exit(1)
        if not isinstance(deployments, list):
            print('Error: AZURE_MODEL_DEPLOYMENTS must be a JSON array.', file=sys.stderr)
            sys.exit(1)
        return deployments, None  # override — no profile to write back

    profile_raw = env['AZURE_MODEL_DEPLOYMENT_PROFILE'].strip().lower() or ''
    individual_mode = _is_truthy(env['AZURE_INDIVIDUAL_MODE'])

    if not profile_raw:
        # Apply mode-appropriate default when no profile is explicitly set.
        # Individual mode: right-sized capacity (50) for a single learner.
        # Organizer/workshop mode: higher capacity (200) for concurrent attendees.
        profile_raw = 'default' if individual_mode else 'workshop'

    return [], profile_raw  # second element is the profile string (may be 'auto')


# ---------------------------------------------------------------------------
# Helpers — quota / availability
# ---------------------------------------------------------------------------


def _list_models(location: str) -> list[dict]:
    result = _run_az([
        'cognitiveservices', 'model', 'list',
        '--location', location,
        '-o', 'json',
    ])
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def _list_usages(location: str) -> list[dict]:
    result = _run_az([
        'cognitiveservices', 'usage', 'list',
        '--location', location,
        '-o', 'json',
    ])
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def _build_availability_set(models: list[dict]) -> set[tuple[str, str]]:
    """Return a set of (sku_name, model_name) pairs available in the region."""
    available: set[tuple[str, str]] = set()
    for m in models:
        model_name = (m.get('model') or {}).get('name', '')
        for sku in (m.get('model') or {}).get('skus') or []:
            sku_name = sku.get('name', '')
            if model_name and sku_name:
                available.add((sku_name, model_name))
    return available


def _build_quota_map(usages: list[dict]) -> dict[str, dict]:
    """Return a map keyed by quota name: {limit, currentValue, available}."""
    result: dict[str, dict] = {}
    for u in usages:
        name = (u.get('name') or {}).get('value', '')
        if not name:
            continue
        limit = int(u.get('limit') or 0)
        current = int(u.get('currentValue') or 0)
        result[name] = {
            'limit': limit,
            'currentValue': current,
            'available': max(0, limit - current),
        }
    return result


def _quota_name(sku_name: str, model_name: str) -> str:
    """Compute the quota-usage key: OpenAI.<sku_name>.<model_name>."""
    return f'OpenAI.{sku_name}.{model_name}'


# ---------------------------------------------------------------------------
# Core check logic
# ---------------------------------------------------------------------------


def _check_profile(
    deployments: list[dict],
    availability: set[tuple[str, str]],
    quota_map: dict[str, dict],
) -> list[dict]:
    """Check one profile's deployments against availability and quota.

    Returns a list of shortfall dicts (one per failing deployment). Empty = passes.
    """
    shortfalls: list[dict] = []

    # Pre-compute aggregate required capacity per quota key.
    # A profile may include multiple deployments for the same model (e.g. 'chat' and
    # 'gpt54mini' both backed by gpt-5.4-mini). Quota must cover the combined total,
    # so check the sum rather than each deployment in isolation.
    aggregate_required: dict[str, int] = {}
    for dep in deployments:
        model_name = (dep.get('model') or {}).get('name', '')
        sku_name = (dep.get('sku') or {}).get('name', '')
        capacity = int((dep.get('sku') or {}).get('capacity') or 0)
        if model_name and sku_name:
            qname = _quota_name(sku_name, model_name)
            aggregate_required[qname] = aggregate_required.get(qname, 0) + capacity

    for dep in deployments:
        model_name = (dep.get('model') or {}).get('name', '')
        sku_name = (dep.get('sku') or {}).get('name', '')
        required_capacity = int((dep.get('sku') or {}).get('capacity') or 0)
        dep_name = dep.get('name', '?')

        # 1. Availability check
        if (sku_name, model_name) not in availability:
            shortfalls.append({
                'deployment': dep_name,
                'model': model_name,
                'sku': sku_name,
                'required': required_capacity,
                'available': 0,
                'reason': 'not available in region',
            })
            continue

        # 2. Quota check — use aggregate capacity for all same-model deployments in the profile.
        qname = _quota_name(sku_name, model_name)
        if qname not in quota_map:
            # No quota entry = treat as unlimited (some SKUs are metered differently).
            continue
        avail = quota_map[qname]['available']
        total_required = aggregate_required.get(qname, required_capacity)
        if avail < total_required:
            shortfalls.append({
                'deployment': dep_name,
                'model': model_name,
                'sku': sku_name,
                'required': total_required,
                'available': avail,
                'reason': 'insufficient quota',
            })

    return shortfalls


def _select_auto_profile(
    availability: set[tuple[str, str]],
    quota_map: dict[str, dict],
) -> str | None:
    """Pick the largest profile that passes the quota check. Returns None if none pass."""
    for profile in reversed(_PROFILES_ASCENDING):
        deployments = _load_profile_deployments(profile)
        shortfalls = _check_profile(deployments, availability, quota_map)
        if not shortfalls:
            return profile
    return None


def _print_shortfall_table(
    profile: str,
    shortfalls: list[dict],
    fitting_profile: str | None,
    location: str,
) -> None:
    print()
    print('╔══════════════════════════════════════════════════════════════════╗')
    print('║  ✗  Model quota / availability check FAILED                     ║')
    print('╚══════════════════════════════════════════════════════════════════╝')
    print(f'\n  Profile   : {profile}')
    print(f'  Region    : {location}')
    print()
    col_w = [24, 32, 12, 10, 10, 28]
    header = (
        f"{'Deployment':<{col_w[0]}}  {'Model':<{col_w[1]}}  "
        f"{'SKU':<{col_w[2]}}  {'Required':>{col_w[3]}}  "
        f"{'Available':>{col_w[4]}}  {'Reason':<{col_w[5]}}"
    )
    separator = '  '.join('-' * w for w in col_w)
    print(f'  {header}')
    print(f'  {separator}')
    for sf in shortfalls:
        row = (
            f"{sf['deployment']:<{col_w[0]}}  {sf['model']:<{col_w[1]}}  "
            f"{sf['sku']:<{col_w[2]}}  {sf['required']:>{col_w[3]}}  "
            f"{sf['available']:>{col_w[4]}}  {sf['reason']:<{col_w[5]}}"
        )
        print(f'  {row}')
    print()

    print('── Remediation ───────────────────────────────────────────────────')
    if fitting_profile:
        print(f'\n  The "{fitting_profile}" profile fits your available quota.')
        print('  Run:')
        print(f'\n    azd env set AZURE_MODEL_DEPLOYMENT_PROFILE {fitting_profile}')
    else:
        print('\n  No built-in profile fits the available quota in this region.')
        print('  Options:')
        print('    1. Try a different region (see suggestions below).')
        print('    2. Request a quota increase at:')
        print('       https://aka.ms/oai/quotaincrease')
        print('    3. Provide a custom deployment set:')
        print('       azd env set AZURE_MODEL_DEPLOYMENTS \'[{"name":"chat",...}]\'')

    print()
    print('  To try a different region:')
    print(f'    azd env set AZURE_LOCATION <region>')
    print()
    print('  To skip this check (not recommended):')
    print('    azd env set AZURE_MODEL_QUOTA_CHECK false')
    print()


def _suggest_region(
    deployments: list[dict],
    location: str,
) -> str | None:
    """Scan candidate regions and return the first one where all deployments fit."""
    print('  Checking candidate regions for quota availability...')
    for region in _CANDIDATE_REGIONS:
        if region.lower() == location.lower():
            continue
        availability = _build_availability_set(_list_models(region))
        quota_map = _build_quota_map(_list_usages(region))
        shortfalls = _check_profile(deployments, availability, quota_map)
        if not shortfalls:
            return region
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    env = _load_env()

    # 0. Skip check entirely if AZURE_MODEL_QUOTA_CHECK=false.
    if not _is_truthy(env.get('AZURE_MODEL_QUOTA_CHECK', 'true')):
        print('check-model-quota: AZURE_MODEL_QUOTA_CHECK=false — skipping quota preflight.')
        return 0

    print('check-model-quota: Validating model quota and availability...')

    # 1. Required env vars.
    errors = _validate_required_env(env)
    if errors:
        print('\nError: required environment variables are missing:\n', file=sys.stderr)
        for err in errors:
            print(f'  • {err}', file=sys.stderr)
        print(file=sys.stderr)
        return 1

    location = env['AZURE_LOCATION'].strip()

    # 2. Resolve deployments and profile.
    deployments, profile = _resolve_deployments(env)
    using_override = deployments != []

    if using_override:
        print(f'  Using AZURE_MODEL_DEPLOYMENTS inline override ({len(deployments)} deployment(s)).')
    else:
        # Profile may be 'auto' — need to fetch quota first, then decide.
        is_auto = profile == 'auto'
        if not is_auto:
            print(f'  Profile: {profile}  (region: {location})')

        # 3. Fetch availability and quota (needed for auto-selection or profile validation).
        print(f'  Fetching model availability for {location}...')
        availability = _build_availability_set(_list_models(location))
        print(f'  Fetching quota usage for {location}...')
        quota_map = _build_quota_map(_list_usages(location))

        if is_auto:
            chosen = _select_auto_profile(availability, quota_map)
            if chosen is None:
                # No profile fits; fall back to minimal and let the check report the shortfall.
                chosen = 'minimal'
                print(f'  auto: no profile fits quota in {location}; falling back to minimal.')
            else:
                print(f'  auto: selected profile "{chosen}" (largest that fits quota).')
            profile = chosen
            _azd_env_set('AZURE_MODEL_DEPLOYMENT_PROFILE', profile)

        deployments = _load_profile_deployments(profile)

        # Persist the resolved profile to the azd environment when it was mode-defaulted
        # (AZURE_MODEL_DEPLOYMENT_PROFILE was not explicitly set by the caller). This ensures
        # Bicep reads the same profile that was quota-checked here, preventing a mismatch where
        # the script checks 'default' (from AZURE_INDIVIDUAL_MODE=true) while Bicep deploys
        # 'workshop' (its hard-coded parameter default).
        if not is_auto and not env['AZURE_MODEL_DEPLOYMENT_PROFILE'].strip():
            _azd_env_set('AZURE_MODEL_DEPLOYMENT_PROFILE', profile)

        # 4. Run check.
        shortfalls = _check_profile(deployments, availability, quota_map)

        if not shortfalls:
            print(f'  ✓ Profile "{profile}" passes quota and availability checks in {location}.')
            return 0

        # 5. Find largest fitting profile for recommendation.
        fitting_profile = None
        for candidate in reversed(_PROFILES_ASCENDING):
            if candidate == profile:
                continue
            candidate_deps = _load_profile_deployments(candidate)
            if not _check_profile(candidate_deps, availability, quota_map):
                fitting_profile = candidate
                break

        _print_shortfall_table(profile, shortfalls, fitting_profile, location)

        # 6. Suggest an alternate region.
        alt_region = _suggest_region(deployments, location)
        if alt_region:
            print(f'  Suggested alternate region with sufficient quota: {alt_region}')
            print(f'    azd env set AZURE_LOCATION {alt_region}')
            print()
        else:
            print('  No candidate region with sufficient quota found for this profile.')
            print()

        return 1

    # Override path: still validate availability and quota.
    print(f'  Fetching model availability for {location}...')
    availability = _build_availability_set(_list_models(location))
    print(f'  Fetching quota usage for {location}...')
    quota_map = _build_quota_map(_list_usages(location))

    shortfalls = _check_profile(deployments, availability, quota_map)
    if shortfalls:
        _print_shortfall_table('custom (AZURE_MODEL_DEPLOYMENTS)', shortfalls, None, location)
        return 1

    print(f'  ✓ Custom deployment set passes quota and availability checks in {location}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
