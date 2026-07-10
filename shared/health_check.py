"""Core workshop environment health-check module.

Provides the shared check infrastructure and all checks that are required
for every lab series.  Import this module from a lab-specific health-check
entry point to extend it with lab-specific checks.

Run directly to execute core checks only:

    python shared/health_check.py

For lab-specific checks run the health-check script in the lab's shared/
folder instead:

    uv run python labs/introduction-foundry-agent-service/shared/health-check.py
    uv run python labs/agent-framework-dotnet/shared/health-check.py
"""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import threading
import tomllib

import requests
from dotenv import load_dotenv

load_dotenv()

# Ensure Unicode output works on Windows terminals that default to cp1252.
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TICK = '\u2705'
CROSS = '\u274c'
WARN = '\u26a0\ufe0f'

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

# Populated by check_optional() for per-lab optional check results.
_opt_failures: list[str] = []


# ── Helpers ────────────────────────────────────────────────────────────────────

def _az(cmd: str, timeout: int | None = None) -> tuple[int, str, str]:
    """Run an az CLI command and return (returncode, stdout, stderr).

    When *timeout* is given, a daemon thread imposes a wall-clock limit so that
    commands like ``docker --version`` or ``docker info`` cannot hang the script
    indefinitely on Windows (where ``subprocess.run`` with ``shell=True`` can
    block in post-kill cleanup when the spawned process ignores SIGTERM/kill).
    """
    if timeout is None:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    outcome: dict[str, object] = {
        'rc': 1, 'out': '', 'err': f'command timed out after {timeout}s'
    }
    done = threading.Event()

    def _run() -> None:
        try:
            r = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=False)
            outcome['rc'] = r.returncode
            outcome['out'] = r.stdout.strip()
            outcome['err'] = r.stderr.strip()
        except Exception as exc:  # noqa: BLE001
            outcome['err'] = str(exc)
        finally:
            done.set()

    threading.Thread(target=_run, daemon=True).start()
    done.wait(timeout)
    return int(outcome['rc']), str(outcome['out']), str(outcome['err'])


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
        return 'DNS resolution failed \u2014 check network connectivity'
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
    """Print a check result and accumulate failures; return whether the check passed."""
    symbol = TICK if passed else CROSS
    line = f'  {symbol}  {name}'
    if detail:
        line += f'  ({detail})'
    if not passed:
        _failures.append(name)
    print(line)
    return passed


def check_optional(name: str, passed: bool, detail: str = '') -> bool:
    """Print a check result for an optional lab requirement.

    Failures are accumulated in *_opt_failures* and shown in the summary as
    warnings, but do not cause the health check to exit with a non-zero code.
    """
    symbol = TICK if passed else WARN
    line = f'  {symbol}  {name}'
    if detail:
        line += f'  ({detail})'
    if not passed:
        _opt_failures.append(name)
    print(line)
    return passed


def _section(title: str) -> None:
    print(f'\n{title}')
    print('\u2500' * len(title))


def _banner(title: str) -> None:
    """Print a prominent banner to separate major check groups."""
    width = max(len(title) + 4, 52)
    bar = '\u2550' * width
    print(f'\n{bar}')
    print(f'  {title}')
    print(bar)


def _print_summary() -> int:
    print()
    exit_code = 0

    if _failures:
        print(f'{CROSS}  {len(_failures)} core check(s) failed:')
        for name in _failures:
            print(f'     \u2022 {name}')
        print()
        print('Resolve the failures above before starting the labs.')
        print('See the Attendee Guide for troubleshooting steps.')
        exit_code = 1
    else:
        print(f'{TICK}  All core checks passed.')

    if _opt_failures:
        print()
        print(f'{WARN}  {len(_opt_failures)} optional lab check(s) did not pass:')
        for name in _opt_failures:
            print(f'     \u2022 {name}')
        print()
        print('These are only required for the specific lab(s) listed above.')
        print('They do not block core lab progress.')
    elif not _failures:
        print(f'{TICK}  All optional lab checks passed. You are ready for all labs.')

    return exit_code


# ── Check groups ───────────────────────────────────────────────────────────────

def _check_prerequisites() -> bool:
    _section('Prerequisites')

    py = sys.version_info
    py_ok = check(
        'Python >= 3.13',
        py >= (3, 13),
        f'{py.major}.{py.minor}.{py.micro}',
    )

    _check_venv()
    _check_python_dependencies()

    rc, out, _ = _az('az --version')
    az_ver = out.splitlines()[0] if rc == 0 else ''
    az_ok = check('Azure CLI installed', rc == 0, az_ver)

    _check_azd()
    _check_docker()

    return py_ok and az_ok


def _check_venv() -> None:
    """Check that a Python virtual environment is active.

    When running via 'uv run python ...', uv activates the project virtual
    environment automatically.  If invoked without uv, activate the .venv
    manually or re-run the script via uv.
    """
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        check('Python virtual environment active', True, sys.prefix)
    else:
        if sys.platform == 'win32':
            activate_cmd = r'.venv\Scripts\Activate.ps1  (PowerShell)  or  .venv\Scripts\activate.bat  (cmd)'
        else:
            activate_cmd = 'source .venv/bin/activate'
        check(
            'Python virtual environment active',
            False,
            f'not active \u2014 re-run via: uv run python scripts/health-check.py\n'
            f'or activate manually with: {activate_cmd}',
        )


def _check_python_dependencies() -> None:
    """Check that the workshop Python packages declared in pyproject.toml are installed.

    Verifies that each package listed under [project] dependencies in pyproject.toml
    can be imported in the active Python environment.  Run 'uv sync' to install
    missing packages.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pyproject_path = os.path.join(repo_root, 'pyproject.toml')
    if not os.path.exists(pyproject_path):
        check('Workshop Python dependencies installed', False, f'{pyproject_path} not found')
        return

    with open(pyproject_path, 'rb') as fh:
        pyproject = tomllib.load(fh)

    raw_deps: list[str] = pyproject.get('project', {}).get('dependencies', [])

    # Map requirement names to importable module names where they differ.
    _import_map: dict[str, str] = {
        'azure-ai-projects': 'azure.ai.projects',
        'azure-identity': 'azure.identity',
        'azure-mgmt-authorization': 'azure.mgmt.authorization',
        'azure-search-documents': 'azure.search.documents',
        'azure-storage-blob': 'azure.storage.blob',
        'python-dotenv': 'dotenv',
        'agent-framework': 'agent_framework',
        'agent-framework-foundry-hosting': 'agent_framework_foundry_hosting',
        'mcp': 'mcp',
        'requests': 'requests',
    }

    # Strip version specifiers (e.g. '>=2.2.0') to get bare package names.
    pkg_names = [re.split(r'[>=<!;\[]', dep)[0].strip() for dep in raw_deps if dep.strip()]

    missing: list[str] = []
    for pkg in pkg_names:
        module_name = _import_map.get(pkg, pkg.replace('-', '_'))
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pkg)

    if missing:
        check(
            'Workshop Python dependencies installed',
            False,
            f'missing: {", ".join(missing)} \u2014 run: uv sync',
        )
    else:
        check(
            'Workshop Python dependencies installed',
            True,
            f'{len(pkg_names)} package(s) from pyproject.toml',
        )


def _check_azd() -> None:
    """Check that the Azure Developer CLI (azd) is installed.

    azd is required by the Attendee Guide for provisioning and environment
    management. It is a separate install from the Azure CLI.
    """
    rc, out, _ = _az('azd version')
    azd_ver = out.splitlines()[0] if rc == 0 else ''
    check(
        'Azure Developer CLI (azd) installed',
        rc == 0,
        azd_ver if azd_ver else 'not found \u2014 install from https://aka.ms/azd',
    )


def _check_docker() -> None:
    """Check for Docker as an optional prerequisite.

    Docker is required for:
    - introduction-foundry-agent-service Module 09 Part 1 (container deployment)
    - agent-framework-dotnet Module 12 (Aspire Dashboard observability)
    A missing or stopped Docker daemon is reported as a warning, not a failure,
    and never causes the health check to exit non-zero.
    """
    only_note = (
        'needed for introduction-foundry-agent-service Module 09 Part 1 '
        'and agent-framework-dotnet Module 12 (Aspire Dashboard); '
        'all other modules run without it'
    )

    rc, out, _ = _az('docker --version', timeout=10)
    if rc != 0:
        print(f'  {WARN}  Docker (optional)  (not installed \u2014 {only_note})')
        return

    docker_ver = out.splitlines()[0]
    rc_info, _, err_info = _az('docker info', timeout=10)
    if rc_info == 0:
        check_optional('Docker (optional)', True, docker_ver)
    else:
        timed_out = 'timed out' in err_info
        reason = 'timed out waiting for daemon' if timed_out else 'daemon not running'
        print(
            f'  {WARN}  Docker (optional)  ({docker_ver}; {reason}'
            ' \u2014 start Docker for introduction-foundry-agent-service Module 09 Part 1'
            ' or agent-framework-dotnet Module 12)'
        )


def _check_env_vars() -> bool:
    _section('Environment variables')
    all_ok = True
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, '')
        ok = check(
            var, bool(val), 'set' if val else 'not set \u2014 copy from your onboarding file'
        )
        if not ok:
            all_ok = False
    return all_ok


def _check_auth(sub: str) -> bool:
    _section('Azure authentication')

    ok, account, err = _az_json('az account show -o json')
    signed_in = check(
        'Signed in to Azure CLI',
        ok,
        '' if ok else (err if err else 'run az login'),
    )
    if not signed_in:
        return False

    user_info = account.get('user', {})
    user_name = user_info.get('name', '') or user_info.get('assignedIdentityInfo', '')
    user_type = user_info.get('type', '')
    active_sub = account.get('id', '')
    sub_name = account.get('name', '')
    tenant_id = account.get('tenantId', '')

    user_detail = user_name
    if user_type and user_type != 'user':
        user_detail = f'{user_name} ({user_type})'
    check(
        'Signed-in user',
        bool(user_name),
        user_detail if user_detail else 'unknown',
    )
    check(
        'Active subscription',
        True,
        f'{sub_name}  [{active_sub}]  tenant={tenant_id}',
    )

    match = active_sub == sub
    check(
        'Active subscription matches AZURE_SUBSCRIPTION_ID',
        match,
        '' if match else f'active={active_sub} -> run: az account set --subscription {sub}',
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
    state = (
        data.get('properties', {}).get('provisioningState', '') if isinstance(data, dict) else ''
    )
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


def _first_resource_name(sub: str, rg: str, resource_type: str) -> str:
    """Return the name of the first resource of the given type in the resource group."""
    rc, out, _ = _az(
        f'az resource list --resource-group {rg} --resource-type {resource_type} '
        f'--subscription {sub} --query "[0].name" -o tsv'
    )
    return out.strip() if rc == 0 else ''


def _check_scope_role(
    label: str, user_id: str, scope: str, sub: str, include_inherited: bool,
) -> None:
    """Verify the signed-in user has at least one role assignment on the given scope."""
    inherited_flag = ' --include-inherited' if include_inherited else ''
    ok, data, err = _az_json(
        f'az role assignment list --assignee {user_id} --scope "{scope}"{inherited_flag} '
        f'--subscription {sub} -o json'
    )
    if ok and isinstance(data, list):
        names = ', '.join(sorted({r.get('roleDefinitionName', '') for r in data}))
        check(
            label,
            len(data) > 0,
            names if names else 'no role assignments found \u2014 ask your organizer',
        )
    else:
        check(label, False, err)


def _check_roles(sub: str, rg: str, foundry: str) -> None:
    _section('Role assignments')

    rc, user_id, err = _az('az ad signed-in-user show --query id -o tsv')
    if not check('Resolved signed-in user identity', rc == 0, err.splitlines()[0] if err else ''):
        return
    user_id = user_id.strip()

    rg_scope = f'/subscriptions/{sub}/resourceGroups/{rg}'

    # Foundry account - include inherited assignments so attendees whose Foundry role is
    # granted on their individual project (foundry-user) or via the resource group still
    # register a result here.
    foundry_scope = f'{rg_scope}/providers/Microsoft.CognitiveServices/accounts/{foundry}'
    _check_scope_role(
        'Role assigned on Foundry account', user_id, foundry_scope, sub, include_inherited=True,
    )

    # Dependent resources - main.bicep grants each resolved attendee a direct role on these.
    dependent_resources = [
        ('AI Search service', 'Microsoft.Search/searchServices'),
        ('Container Registry', 'Microsoft.ContainerRegistry/registries'),
        ('Application Insights', 'Microsoft.Insights/components'),
    ]
    for label, resource_type in dependent_resources:
        name = _first_resource_name(sub, rg, resource_type)
        if not name:
            check(f'Role assigned on {label}', False, 'resource not found in resource group')
            continue
        scope = f'{rg_scope}/providers/{resource_type}/{name}'
        _check_scope_role(f'Role assigned on {label}', user_id, scope, sub, include_inherited=False)


def _check_endpoints(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    endpoint: str,
    openai_endpoint: str,
    search_name: str,
    rg: str,
    sub: str,
) -> None:
    _section('Service endpoints')

    # The new Foundry v1 endpoints require the ai.azure.com audience, not cognitiveservices.
    foundry_token = _get_token('https://ai.azure.com')

    # Foundry project endpoint - probe GET {endpoint}/connections
    if foundry_token and endpoint:
        probe_url = endpoint.rstrip('/') + '/connections?api-version=2025-05-15-preview'
        try:
            resp = requests.get(
                probe_url, headers={'Authorization': f'Bearer {foundry_token}'}, timeout=10
            )
            if resp.ok:
                connections = resp.json().get('value', [])
                count = len(connections)
                check(
                    'Foundry project endpoint reachable',
                    True,
                    f'URL {probe_url} | {count} connection(s) visible',
                )
            else:
                check(
                    'Foundry project endpoint reachable',
                    False,
                    f'URL {probe_url} | HTTP {resp.status_code}',
                )
        except requests.RequestException as exc:
            check('Foundry project endpoint reachable', False, f'URL {probe_url} | {_net_err(exc)}')
    else:
        probe_url = (
            (endpoint.rstrip('/') + '/connections?api-version=2025-05-15-preview')
            if endpoint else '<missing>'
        )
        check(
            'Foundry project endpoint reachable', False,
            f'URL {probe_url} | missing token or endpoint',
        )

    # Azure OpenAI endpoint - probe GET {endpoint}/models
    if foundry_token and openai_endpoint:
        probe_url = openai_endpoint.rstrip('/') + '/models'
        try:
            resp = requests.get(
                probe_url, headers={'Authorization': f'Bearer {foundry_token}'}, timeout=10
            )
            if resp.ok:
                models = resp.json().get('data', [])
                count = len(models)
                names = ', '.join(m.get('id', '') for m in models[:6])
                check(
                    'Azure OpenAI endpoint reachable',
                    True,
                    f'URL {probe_url} | {count} model(s): {names}'
                    if count else f'URL {probe_url} | 0 models',
                )
            else:
                check(
                    'Azure OpenAI endpoint reachable',
                    False,
                    f'URL {probe_url} | HTTP {resp.status_code}',
                )
        except requests.RequestException as exc:
            check('Azure OpenAI endpoint reachable', False, f'URL {probe_url} | {_net_err(exc)}')
    else:
        probe_url = (
            (openai_endpoint.rstrip('/') + '/models') if openai_endpoint else '<missing>'
        )
        check(
            'Azure OpenAI endpoint reachable', False,
            f'URL {probe_url} | missing token or endpoint',
        )

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
                        f'{count} index(es): {names}'
                        if count else 'no indexes \u2014 ask your organizer to seed',
                    )
                    if count > 0:
                        present = {i.get('name', '') for i in indexes}
                        for index_name in [
                            os.getenv('AZURE_SEARCH_PRODUCT_INDEX_NAME', 'retail-products').strip() or 'retail-products',
                            os.getenv('AZURE_SEARCH_DOCUMENT_INDEX_NAME', 'retail-policies').strip() or 'retail-policies',
                            os.getenv('AZURE_SEARCH_PASSENGER_RIGHTS_INDEX_NAME', 'passenger-rights').strip() or 'passenger-rights',
                        ]:
                            check(
                                f'AI Search index: {index_name}',
                                index_name in present,
                                'present' if index_name in present
                                else f'missing \u2014 run the seed script for {index_name}',
                            )
                else:
                    check('AI Search indexes seeded', False, f'HTTP {resp.status_code}')
            except requests.RequestException as exc:
                check('AI Search indexes seeded', False, _net_err(exc))
        else:
            check('AI Search indexes seeded', False, 'could not obtain Search access token')


def _check_mcp_server(mcp_url: str, label: str = 'MCP Server') -> None:
    """Validate that the MCP server at *mcp_url* is reachable and exposes tools.

    Sends a JSON-RPC ``initialize`` request followed by a ``tools/list`` request.
    Both JSON and SSE (text/event-stream) response bodies are handled.
    """
    _section(label)

    if not mcp_url:
        check(
            'MCP server reachable',
            False,
            'MCP server URL not set',
        )
        return

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
    }

    def _parse_jsonrpc(resp: requests.Response) -> dict:
        """Extract the first JSON-RPC payload from a JSON or SSE response."""
        content_type = resp.headers.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            for line in resp.text.splitlines():
                if line.startswith('data:'):
                    try:
                        return json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        pass
            return {}
        try:
            return resp.json()
        except (ValueError, AttributeError):
            return {}

    # ── initialize ────────────────────────────────────────────────────────────
    init_payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'health-check', 'version': '1.0.0'},
        },
    }
    session_id: str = ''
    try:
        resp = requests.post(mcp_url, json=init_payload, headers=headers, timeout=10)
        if not resp.ok:
            check('MCP server reachable', False, f'{mcp_url} | HTTP {resp.status_code}')
            return

        session_id = resp.headers.get('Mcp-Session-Id', '')

        data = _parse_jsonrpc(resp)
        server_info = data.get('result', {}).get('serverInfo', {})
        server_name = server_info.get('name', '')
        detail = f'{mcp_url} | server: {server_name}' if server_name else mcp_url
        check('MCP server reachable', True, detail)

    except requests.RequestException as exc:
        check('MCP server reachable', False, f'{mcp_url} | {_net_err(exc)}')
        return

    # Build session-aware headers for all requests after initialize.
    session_headers = {**headers}
    if session_id:
        session_headers['Mcp-Session-Id'] = session_id

    # ── notifications/initialized ─────────────────────────────────────────────
    notify_payload = {'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}}
    try:
        requests.post(mcp_url, json=notify_payload, headers=session_headers, timeout=10)
    except requests.RequestException:
        pass  # Notification failure is non-fatal; proceed to tools/list.

    # ── tools/list ────────────────────────────────────────────────────────────
    tools_payload = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}
    try:
        tresp = requests.post(mcp_url, json=tools_payload, headers=session_headers, timeout=10)
        if not tresp.ok:
            check('MCP server tools available', False, f'HTTP {tresp.status_code}')
            return

        tdata = _parse_jsonrpc(tresp)
        tools = tdata.get('result', {}).get('tools', [])
        count = len(tools)
        names = ', '.join(t.get('name', '') for t in tools[:6])
        check(
            'MCP server tools available',
            count > 0,
            f'{count} tool(s): {names}' if count else 'no tools registered',
        )
    except requests.RequestException as exc:
        check('MCP server tools available', False, _net_err(exc))


# ── Core orchestration ─────────────────────────────────────────────────────────

def run_core_checks() -> None:
    """Run all core environment checks.

    Executes prerequisites, environment variables, Azure authentication,
    Azure resources, role assignments, and service endpoint checks.  Skips
    Azure connectivity checks when prerequisites or environment variables are
    not satisfied, but always returns so callers can run additional lab-specific
    checks before printing the final summary.
    """
    _banner('Core Requirements')
    az_ok = _check_prerequisites()
    env_ok = _check_env_vars()

    if not env_ok or not az_ok:
        return

    sub = os.getenv('AZURE_SUBSCRIPTION_ID', '').strip()
    rg = os.getenv('AZURE_RESOURCE_GROUP', '').strip()
    foundry = os.getenv('FOUNDRY_RESOURCE_NAME', '').strip()
    project = os.getenv('FOUNDRY_PROJECT_NAME', '').strip()
    endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT', '').strip()
    openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').strip()
    search_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()

    if not _check_auth(sub):
        return

    _check_resources(sub, rg, foundry, project)
    _check_roles(sub, rg, foundry)
    _check_endpoints(endpoint, openai_endpoint, search_name, rg, sub)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> int:
    """Run core workshop environment health checks and print a summary.

    For lab-specific checks run the health-check script in the lab's
    shared/ folder instead:

        uv run python labs/introduction-foundry-agent-service/shared/health-check.py
        uv run python labs/agent-framework-dotnet/shared/health-check.py
    """
    print('Workshop Environment Health Check')
    print('\u2550' * 34)

    run_core_checks()

    return _print_summary()


if __name__ == '__main__':
    raise SystemExit(main())
