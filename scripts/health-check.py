"""Workshop environment health check.

Runs a comprehensive set of checks against the attendee's local environment,
Azure authentication, provisioned resources, role assignments, and service
endpoints. Each check prints a green tick (✅) on pass or a red cross (❌)
on failure. Exits 0 only when all checks pass.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TICK = '\u2705'
CROSS = '\u274c'

REQUIRED_ENV_VARS = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'FOUNDRY_RESOURCE_NAME',
    'FOUNDRY_PROJECT_NAME',
    'FOUNDRY_PROJECT_ENDPOINT',
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_SEARCH_SERVICE_NAME',
]

# Populated by check() as failures accumulate.
_failures: list[str] = []


# ── Helpers ────────────────────────────────────────────────────────────────────

def _az(cmd: str) -> tuple[int, str, str]:
    """Run an az CLI command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _az_json(cmd: str) -> tuple[bool, dict | list, str]:
    """Run an az CLI command that returns JSON. Returns (ok, parsed, error)."""
    rc, out, err = _az(cmd)
    if rc != 0:
        return False, {}, err.splitlines()[0] if err else 'command failed'
    try:
        return True, json.loads(out), ''
    except json.JSONDecodeError:
        return False, {}, f'unexpected output: {out[:80]}'


def _net_err(exc: Exception) -> str:
    """Extract a short, readable message from a requests exception."""
    msg = str(exc)
    if 'NameResolutionError' in msg or 'getaddrinfo failed' in msg:
        return 'DNS resolution failed — check network connectivity'
    if 'Connection refused' in msg:
        return 'connection refused'
    if 'timed out' in msg.lower():
        return 'connection timed out'
    # Fall back to first line only
    return msg.splitlines()[0][:100]


def _get_token(resource: str) -> str:
    """Retrieve an Azure access token for the given resource URI."""
    rc, out, _ = _az(f'az account get-access-token --resource {resource} -o json')
    if rc != 0:
        return ''
    try:
        return json.loads(out).get('accessToken', '')
    except json.JSONDecodeError:
        return ''


def check(name: str, passed: bool, detail: str = '') -> bool:
    symbol = TICK if passed else CROSS
    line = f'  {symbol}  {name}'
    if detail:
        line += f'  ({detail})'
    if not passed:
        _failures.append(name)
    print(line)
    return passed


def _section(title: str) -> None:
    print(f'\n{title}')
    print('\u2500' * len(title))


def _print_summary() -> int:
    print()
    if _failures:
        print(f'{CROSS}  {len(_failures)} check(s) failed:')
        for name in _failures:
            print(f'     \u2022 {name}')
        print()
        print('Resolve the failures above before starting the labs.')
        print('See the Attendee Guide for troubleshooting steps.')
        return 1
    print(f'{TICK}  All checks passed. You are ready to start the labs.')
    return 0


# ── Check groups ───────────────────────────────────────────────────────────────

def _check_prerequisites() -> bool:
    _section('Prerequisites')

    py = sys.version_info
    py_ok = check(
        'Python >= 3.13',
        py >= (3, 13),
        f'{py.major}.{py.minor}.{py.micro}',
    )

    rc, out, _ = _az('az --version')
    az_ver = out.splitlines()[0] if rc == 0 else ''
    az_ok = check('Azure CLI installed', rc == 0, az_ver)

    return py_ok and az_ok


def _check_env_vars() -> bool:
    _section('Environment variables')
    all_ok = True
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, '')
        ok = check(var, bool(val), 'set' if val else 'not set \u2014 copy from your onboarding file')
        if not ok:
            all_ok = False
    return all_ok


def _check_auth(sub: str) -> bool:
    _section('Azure authentication')

    rc, active_sub, err = _az('az account show --query id -o tsv')
    signed_in = check(
        'Signed in to Azure CLI',
        rc == 0,
        '' if rc == 0 else (err.splitlines()[0] if err else 'run az login'),
    )
    if not signed_in:
        return False

    match = active_sub == sub
    check(
        'Active subscription matches AZURE_SUBSCRIPTION_ID',
        match,
        '' if match else f'active={active_sub}  \u2192  run: az account set --subscription {sub}',
    )
    return match


def _check_resources(sub: str, rg: str, foundry: str, project: str) -> None:
    _section('Azure resources')

    # Resource group
    ok, data, err = _az_json(f'az group show --name {rg} --subscription {sub} -o json')
    state = data.get('properties', {}).get('provisioningState', '') if ok else ''
    check('Resource group accessible', ok, state or err)

    # Foundry account (Cognitive Services)
    ok, data, err = _az_json(
        f'az cognitiveservices account show --name {foundry} --resource-group {rg} '
        f'--subscription {sub} -o json'
    )
    state = data.get('properties', {}).get('provisioningState', '') if ok else ''
    check('Foundry account accessible', ok, state or err)

    # Foundry project (child resource via management REST)
    proj_url = (
        f'https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}'
        f'/providers/Microsoft.CognitiveServices/accounts/{foundry}'
        f'/projects/{project}?api-version=2025-04-01-preview'
    )
    ok, data, err = _az_json(f'az rest --method GET --url "{proj_url}" -o json')
    state = data.get('properties', {}).get('provisioningState', '') if isinstance(data, dict) else ''
    check('Foundry project accessible', ok, state or err)

    # Model deployments
    ok, data, err = _az_json(
        f'az cognitiveservices account deployment list --name {foundry} '
        f'--resource-group {rg} --subscription {sub} -o json'
    )
    if ok and isinstance(data, list):
        count = len(data)
        names = ', '.join(d.get('name', '') for d in data[:6])
        check(
            'Model deployments exist',
            count > 0,
            f'{count} deployment(s): {names}' if count else 'none found \u2014 ask your organizer',
        )
    else:
        check('Model deployments exist', False, err)


def _check_roles(sub: str, rg: str, foundry: str) -> None:
    _section('Role assignments')

    rc, user_id, err = _az('az ad signed-in-user show --query id -o tsv')
    if not check('Resolved signed-in user identity', rc == 0, err.splitlines()[0] if err else ''):
        return

    scope = (
        f'/subscriptions/{sub}/resourceGroups/{rg}'
        f'/providers/Microsoft.CognitiveServices/accounts/{foundry}'
    )
    ok, data, err = _az_json(
        f'az role assignment list --assignee {user_id.strip()} --scope "{scope}" '
        f'--subscription {sub} --include-inherited -o json'
    )
    if ok and isinstance(data, list):
        names = ', '.join(sorted({r.get('roleDefinitionName', '') for r in data}))
        check(
            'Role assigned on Foundry account',
            len(data) > 0,
            names if names else 'no role assignments found \u2014 ask your organizer',
        )
    else:
        check('Role assigned on Foundry account', False, err)


def _check_endpoints(
    endpoint: str,
    openai_endpoint: str,
    search_name: str,
    rg: str,
    sub: str,
) -> None:
    _section('Service endpoints')

    cs_token = _get_token('https://cognitiveservices.azure.com')

    # Foundry project endpoint
    if cs_token and endpoint:
        try:
            resp = requests.get(
                endpoint, headers={'Authorization': f'Bearer {cs_token}'}, timeout=10
            )
            # Any response below 500 confirms the service is up and token is accepted.
            check('Foundry project endpoint reachable', resp.status_code < 500, f'HTTP {resp.status_code}')
        except requests.RequestException as exc:
            check('Foundry project endpoint reachable', False, _net_err(exc))
    else:
        check('Foundry project endpoint reachable', False, 'missing token or endpoint')

    # Azure OpenAI endpoint — list deployments as a lightweight probe
    if cs_token and openai_endpoint:
        base = openai_endpoint.split('/openai/v1')[0] if '/openai/v1' in openai_endpoint else openai_endpoint
        url = f'{base.rstrip("/")}/openai/deployments?api-version=2024-10-21'
        try:
            resp = requests.get(
                url, headers={'Authorization': f'Bearer {cs_token}'}, timeout=10
            )
            if resp.status_code == 200:
                count = len(resp.json().get('data', []))
                check('Azure OpenAI endpoint reachable', True, f'{count} deployment(s) visible')
            else:
                check('Azure OpenAI endpoint reachable', resp.status_code < 500, f'HTTP {resp.status_code}')
        except requests.RequestException as exc:
            check('Azure OpenAI endpoint reachable', False, _net_err(exc))
    else:
        check('Azure OpenAI endpoint reachable', False, 'missing token or endpoint')

    # AI Search service
    if search_name:
        ok, data, err = _az_json(
            f'az search service show --name {search_name} --resource-group {rg} '
            f'--subscription {sub} -o json'
        )
        state = data.get('provisioningState', '') if isinstance(data, dict) else ''
        check('AI Search service accessible', ok, state or err)

        # AI Search indexes
        search_token = _get_token('https://search.azure.com')
        if search_token:
            url = f'https://{search_name}.search.windows.net/indexes?api-version=2024-07-01'
            try:
                resp = requests.get(
                    url, headers={'Authorization': f'Bearer {search_token}'}, timeout=10
                )
                if resp.status_code == 200:
                    indexes = resp.json().get('value', [])
                    count = len(indexes)
                    names = ', '.join(i.get('name', '') for i in indexes[:6])
                    check(
                        'AI Search indexes seeded',
                        count > 0,
                        f'{count} index(es): {names}' if count else 'no indexes \u2014 ask your organizer to seed',
                    )
                else:
                    check('AI Search indexes seeded', False, f'HTTP {resp.status_code}')
            except requests.RequestException as exc:
                check('AI Search indexes seeded', False, _net_err(exc))
        else:
            check('AI Search indexes seeded', False, 'could not obtain Search access token')


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> int:
    print('Workshop Environment Health Check')
    print('\u2550' * 34)

    az_ok = _check_prerequisites()
    env_ok = _check_env_vars()

    if not env_ok or not az_ok:
        return _print_summary()

    sub = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    rg = os.getenv('AZURE_RESOURCE_GROUP', '').strip()
    foundry = os.getenv('FOUNDRY_RESOURCE_NAME', '').strip()
    project = os.getenv('FOUNDRY_PROJECT_NAME', '').strip()
    endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT', '').strip()
    openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').strip()
    search_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()

    if not _check_auth(sub):
        return _print_summary()

    _check_resources(sub, rg, foundry, project)
    _check_roles(sub, rg, foundry)
    _check_endpoints(endpoint, openai_endpoint, search_name, rg, sub)

    return _print_summary()


if __name__ == '__main__':
    raise SystemExit(main())

