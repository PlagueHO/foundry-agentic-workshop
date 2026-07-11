# pylint: disable=invalid-name
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

"""Configure and optionally provision a Microsoft Foundry workshop environment.

Run from the repository root with::

    uv run python scripts/configure-workshop.py

The wizard writes configuration with ``azd env set`` and only starts provisioning
after an explicit confirmation. It never handles passwords, tokens, or secrets.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from typing import Any

# pylint: disable=invalid-name,too-few-public-methods


ROLE_KEYS = (
    'foundry-user',
    'foundry-project-manager',
    'foundry-account-owner',
    'foundry-owner',
    'facilitator',
    'proctor',
    'organizer',
)
MODEL_PROFILES = ('default', 'minimal', 'workshop', 'broad')
UPN_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PROJECT_NAME_PATTERN = re.compile(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$')
RESOURCE_DEPLOYMENT_ROLES = {'Owner', 'Contributor'}
ROLE_ASSIGNMENT_ROLES = {
    'Owner',
    'User Access Administrator',
    'Role Based Access Control Administrator',
}


class Palette:
    """Small ANSI palette that gracefully disables colour when stdout is redirected."""

    def __init__(self) -> None:
        enabled = sys.stdout.isatty() and os.getenv('NO_COLOR') is None
        self.bold = '\033[1m' if enabled else ''
        self.cyan = '\033[36m' if enabled else ''
        self.green = '\033[32m' if enabled else ''
        self.yellow = '\033[33m' if enabled else ''
        self.red = '\033[31m' if enabled else ''
        self.reset = '\033[0m' if enabled else ''


COLORS = Palette()
CALLOUT_WIDTH = 64


def _display_width(text: str) -> int:
    """Return the terminal display width of a string."""
    return sum(
        0 if unicodedata.combining(character) else 2 if unicodedata.east_asian_width(character) in {'W', 'F'} else 1
        for character in text
    )


def _callout_border(left: str, right: str, fill: str = '─') -> str:
    return f'{left}{fill * CALLOUT_WIDTH}{right}'


def _callout_line(text: str = '', left: str = '│', right: str = '│') -> str:
    padding = CALLOUT_WIDTH - _display_width(text) - 2
    if padding < 0:
        raise ValueError('Callout text exceeds the configured width.')
    return f'{left} {text}{" " * padding} {right}'


def _print_callout(
    sections: tuple[tuple[str, ...], ...],
    *,
    color: str,
    corners: tuple[str, str, str, str] = ('╭', '╮', '╰', '╯'),
    divider: str | None = None,
    section_colors: tuple[str, ...] | None = None,
) -> None:
    """Print a consistently sized callout with optional section dividers."""
    top_left, top_right, bottom_left, bottom_right = corners
    _print(_callout_border(top_left, top_right), color=color)
    for section_index, section in enumerate(sections):
        section_color = (
            section_colors[section_index]
            if section_colors is not None
            else color
        )
        for line in section:
            _print(_callout_line(line), color=section_color)
        if divider is not None and section_index < len(sections) - 1:
            _print(_callout_border('╠', '╣', divider), color=color)
    _print(_callout_border(bottom_left, bottom_right), color=color)


def _command_path(command: str) -> str:
    """Resolve a Windows ``.cmd`` executable as well as POSIX executables."""
    return shutil.which(command) or command


def _run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=capture,
        text=True,
        check=False,
    )


def _print(message: str = '', *, color: str = '') -> None:
    print(f'{color}{message}{COLORS.reset if color else ""}')


def _header() -> None:
    _print_callout(
        (
            ('✨ Microsoft Foundry Workshop Setup Wizard ✨',),
            (
                'I will configure your azd environment, check',
                'Azure access, and optionally start provisioning',
                'when you say go. 🚀',
            ),
        ),
        color=COLORS.cyan,
        section_colors=(COLORS.cyan, COLORS.bold),
    )


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f' [{default}]' if default is not None else ''
    while True:
        answer = input(f'{COLORS.cyan}{prompt}{suffix}: {COLORS.reset}').strip()
        if answer:
            return answer
        if default is not None:
            return default
        _print('Please enter a value so we can continue.', color=COLORS.yellow)


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    default_text = 'Y/n' if default else 'y/N'
    while True:
        answer = input(f'{COLORS.cyan}{prompt} [{default_text}]: {COLORS.reset}').strip().lower()
        if not answer:
            return default
        if answer in {'y', 'yes'}:
            return True
        if answer in {'n', 'no'}:
            return False
        _print('Please answer yes or no.', color=COLORS.yellow)


def _ask_choice(prompt: str, choices: tuple[str, ...], default: str) -> str:
    choices_text = ', '.join(choices)
    while True:
        answer = _ask(f'{prompt} ({choices_text})', default).lower()
        if answer in choices:
            return answer
        _print(f'Choose one of: {choices_text}.', color=COLORS.yellow)


def _require_tool(command: str) -> str:
    path = _command_path(command)
    if shutil.which(command) is None:
        _print(
            f'❌ Could not find {command}. Install it and run this wizard again.',
            color=COLORS.red,
        )
        raise RuntimeError(f'{command} is required')
    return path


def _json_output(command: list[str]) -> Any:
    result = _run(command)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or 'command failed'
        raise RuntimeError(f'{" ".join(command)}: {detail}')
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'Unexpected JSON output from {" ".join(command)}.') from exc


def _check_azure_access(az: str) -> dict[str, str]:
    _print(
        '🔐 Checking your Azure sign-in and deployment permissions.',
        color=COLORS.bold,
    )
    try:
        account = _json_output([
            az,
            'account',
            'show',
            '--query',
            '{subscriptionId:id,subscriptionName:name,tenantId:tenantId,'
            'user:user.name,state:state}',
            '--output',
            'json',
        ])
    except RuntimeError as exc:
        _print(
            '❌ Azure CLI is not authenticated. Run `az login`, then try again.',
            color=COLORS.red,
        )
        raise RuntimeError(str(exc)) from exc

    if account.get('state') != 'Enabled':
        raise RuntimeError(
            f"The selected subscription is not enabled (state: {account.get('state')})."
        )

    principal = _json_output([
        az,
        'ad',
        'signed-in-user',
        'show',
        '--query',
        '{objectId:id,displayName:displayName,userPrincipalName:userPrincipalName}',
        '--output',
        'json',
    ])
    principal_id = principal.get('objectId')
    if not principal_id:
        raise RuntimeError('Azure CLI did not return the signed-in user object ID.')

    scope = f"/subscriptions/{account['subscriptionId']}"
    assignments = _json_output([
        az,
        'role',
        'assignment',
        'list',
        '--assignee-object-id',
        principal_id,
        '--scope',
        scope,
        '--include-inherited',
        '--output',
        'json',
    ])
    role_names = {
        item.get('roleDefinitionName')
        for item in assignments
        if item.get('roleDefinitionName')
    }
    has_deployment = bool(role_names & RESOURCE_DEPLOYMENT_ROLES)
    has_role_assignment = bool(role_names & ROLE_ASSIGNMENT_ROLES)

    _print(
        f"  ✅ Signed in as {principal.get('userPrincipalName') or principal.get('displayName')}"
    )
    _print(
        f"  ✅ Subscription: {account.get('subscriptionName')} "
        f"({account['subscriptionId']})"
    )
    _print(f"  {'✅' if has_deployment else '❌'} Resource deployment permission")
    _print(f"  {'✅' if has_role_assignment else '❌'} Role-assignment permission")

    if not has_deployment or not has_role_assignment:
        missing = []
        if not has_deployment:
            missing.append('Owner or Contributor')
        if not has_role_assignment:
            missing.append(
                'Owner, User Access Administrator, or '
                'Role Based Access Control Administrator'
            )
        raise RuntimeError(
            'Missing required Azure permissions: '
            + '; '.join(missing)
            + '. Ask a subscription administrator to grant the required role(s).'
        )

    return {
        'subscription_id': account['subscriptionId'],
        'tenant_id': account['tenantId'],
        'principal_id': principal_id,
    }


def _select_environment(azd: str) -> str:
    current = _run([azd, 'env', 'get-value', 'AZURE_ENV_NAME'])
    current_name = current.stdout.strip() if current.returncode == 0 else ''
    prompt = 'azd environment name'
    environment = _ask(prompt, current_name or 'my-foundry-lab')
    if environment != current_name:
        selected = _run([azd, 'env', 'select', environment])
        if selected.returncode != 0:
            created = _run([azd, 'env', 'new', environment])
            if created.returncode != 0:
                detail = created.stderr.strip() or created.stdout.strip()
                raise RuntimeError(f'Could not select or create azd environment: {detail}')
    return environment


def _collect_attendees() -> tuple[list[dict[str, Any]], int | None]:
    if not _ask_yes_no('Do you have attendee UPNs to enter now?', True):
        while True:
            raw_count = _ask('Number of anonymous attendee projects', '1')
            if raw_count.isdigit() and int(raw_count) > 0:
                return [], int(raw_count)
            _print('Enter a positive whole number.', color=COLORS.yellow)

    attendees: list[dict[str, Any]] = []
    _print(
        'Enter attendee UPNs. Press Ctrl+C to cancel; finish with a blank line. 👥'
    )
    while True:
        upn = input(f'{COLORS.cyan}Attendee UPN: {COLORS.reset}').strip()
        if not upn:
            if attendees:
                return attendees, None
            _print(
                'Add at least one attendee, or choose anonymous headcount mode.',
                color=COLORS.yellow,
            )
            continue
        if not UPN_PATTERN.fullmatch(upn):
            _print(
                'That does not look like a valid UPN '
                '(for example, name@contoso.com).',
                color=COLORS.yellow,
            )
            continue
        role = _ask_choice('Role', ROLE_KEYS, 'foundry-project-manager')
        entry: dict[str, Any] = {'upn': upn, 'role': role}
        if _ask_yes_no('Give this attendee a dedicated project?', True):
            project_name = _ask('Explicit project name (blank uses the UPN-derived name)', '')
            if project_name:
                invalid_project_name = (
                    len(project_name) < 2
                    or len(project_name) > 64
                    or not PROJECT_NAME_PATTERN.fullmatch(project_name)
                )
                if invalid_project_name:
                    _print(
                        'Project names must be 2-64 characters: lowercase letters, '
                        'numbers, and hyphens.',
                        color=COLORS.yellow,
                    )
                    continue
                entry['projectName'] = project_name
        else:
            entry['individualProject'] = False
        attendees.append(entry)
        _print(f'  Added {upn} ✅', color=COLORS.green)


def _collect_common_settings(individual_mode: bool) -> tuple[str, bool, dict[str, str]]:
    default_profile = 'default' if individual_mode else 'workshop'
    profile = _ask_choice('Model deployment profile', MODEL_PROFILES, default_profile)
    container_apps = _ask_yes_no('Deploy the shared Container Apps services?', True)
    extra: dict[str, str] = {}
    if _ask_yes_no('Configure advanced options?', False):
        quota_check = _ask_yes_no('Run the model quota check before provisioning?', True)
        extra['AZURE_MODEL_QUOTA_CHECK'] = str(quota_check).lower()
        if _ask_yes_no('Enable Azure AI Search capability host?', False):
            extra['AZURE_AI_SEARCH_CAPABILITY_HOST'] = 'true'
        if _ask_yes_no('Enable Cosmos DB capability host?', False):
            extra['AZURE_COSMOS_DB_CAPABILITY_HOST'] = 'true'
        if _ask_yes_no('Enable Azure Storage capability host?', False):
            extra['AZURE_STORAGE_ACCOUNT_CAPABILITY_HOST'] = 'true'
    return profile, container_apps, extra


def _set_environment(azd: str, settings: dict[str, str]) -> None:
    _print('\n💾 Saving your azd environment settings...', color=COLORS.bold)
    for name, value in settings.items():
        result = _run([azd, 'env', 'set', name, value])
        if result.returncode != 0:
            detail = (
                result.stderr.strip()
                or result.stdout.strip()
                or 'azd env set failed'
            )
            raise RuntimeError(f'Could not set {name}: {detail}')
        display = '[JSON roster]' if name == 'AZURE_ATTENDEE_LIST' else value
        _print(f'  ✅ {name} = {display}', color=COLORS.green)


DOCKER_INSTALL_URL = 'https://docs.docker.com/get-started/get-docker/'


def _check_docker() -> bool:
    """Return True if the Docker daemon is reachable, False otherwise."""
    docker = shutil.which('docker')
    if not docker:
        return False
    result = _run([docker, 'info'])
    return result.returncode == 0


def _warn_docker_not_running() -> bool:
    """Print a prominent Docker warning and ask whether to continue.

    Returns True if the user chooses to continue despite Docker not running.
    """
    _print()
    _print_callout(
        (
            ('🐳  DOCKER IS NOT RUNNING — DEPLOYMENT WILL FAIL  🐳',),
            (
                'The post-provision hooks build and push the MCP Server',
                'container images to Azure Container Registry. Without',
                'a running Docker daemon those steps will fail and the',
                'Container Apps services will not be deployed.',
            ),
            (
                'Install / start Docker Desktop, then re-run this wizard.',
                f'👉  {DOCKER_INSTALL_URL}',
            ),
        ),
        color=COLORS.red,
        corners=('╔', '╗', '╚', '╝'),
        divider='═',
    )
    _print()
    return _ask_yes_no(
        '⚠️  Continue anyway and provision without working Docker?',
        False,
    )


LABS_URL = 'https://danielscottraynsford.com/foundry-agentic-workshop/#available-labs'


def _get_env_value(azd: str, key: str) -> str:
    """Return the value of an azd environment variable, or '' if absent."""
    result = _run([azd, 'env', 'get-value', key])
    return result.stdout.strip() if result.returncode == 0 else ''


def _show_post_provision_summary(
    azd: str,
    *,
    individual_mode: bool,
    environment: str,
) -> None:
    """Print a post-provisioning summary of key outputs and next steps."""
    subscription_id = _get_env_value(azd, 'AZURE_SUBSCRIPTION_ID')
    resource_group = _get_env_value(azd, 'AZURE_RESOURCE_GROUP')
    portal_url = '' if individual_mode else _get_env_value(azd, 'ATTENDEE_PORTAL_URL')

    _print()
    _print_callout((('📋 Deployment summary',),), color=COLORS.cyan)
    _print(f'\n  Environment   : {environment}')
    if subscription_id:
        _print(f'  Subscription  : {subscription_id}')
    if resource_group:
        _print(f'  Resource group: {resource_group}')
    if subscription_id and resource_group:
        rg_url = (
            f'https://portal.azure.com/#resource/subscriptions/{subscription_id}'
            f'/resourceGroups/{resource_group}/overview'
        )
        _print(f'  Azure portal  : {rg_url}')
    _print('  Foundry portal: https://ai.azure.com')
    if not individual_mode and portal_url:
        _print(f'  Attendee portal: {portal_url}', color=COLORS.cyan)

    _print('\n▶  What to do next', color=COLORS.bold)
    step = 1
    if not individual_mode and portal_url:
        _print(f'  {step}. Share the attendee portal URL with your attendees:')
        _print(f'       {portal_url}', color=COLORS.cyan)
        step += 1
    _print(f'  {step}. Run the health check to validate the environment:')
    _print( '       uv run python scripts/health-check.py')
    step += 1
    _print(f'  {step}. Open the workshop and begin the labs:')
    _print(f'       {LABS_URL}', color=COLORS.cyan)
    _print()


def _provision(azd: str) -> int:
    _print(
        '\n🚀 Starting `azd provision`. Azure output will appear below.\n',
        color=COLORS.bold,
    )
    result = _run([azd, 'provision'], capture=False)
    if result.returncode != 0:
        _print(
            '\n❌ Provisioning failed. Review the command output above and '
            'correct the reported issue.',
            color=COLORS.red,
        )
    else:
        _print('\n🎉 Provisioning completed successfully!', color=COLORS.green)
    return result.returncode


def main() -> int:
    """Run the interactive workshop setup wizard."""
    try:
        _header()
        az = _require_tool('az')
        azd = _require_tool('azd')
        account = _check_azure_access(az)
        environment = _select_environment(azd)
        location = _ask('Azure region', 'australiaeast')
        resource_group = _ask('Resource group name', f'rg-{environment}')
        individual_mode = _ask_choice(
            'How are you running the workshop?',
            ('individual', 'organizer'),
            'individual',
        ) == 'individual'

        attendees: list[dict[str, Any]] = []
        attendee_count: int | None = None
        extra: dict[str, str] = {}
        if individual_mode:
            profile, container_apps, extra = _collect_common_settings(True)
        else:
            attendees, attendee_count = _collect_attendees()
            profile, container_apps, extra = _collect_common_settings(False)
            extra['AZURE_ATTENDEE_DEFAULT_ROLE'] = 'foundry-project-manager'
            extra['AZURE_USE_UPN_PROJECT_NAMES'] = 'true'

        settings = {
            'AZURE_LOCATION': location,
            'AZURE_RESOURCE_GROUP': resource_group,
            'AZURE_PRINCIPAL_ID': account['principal_id'],
            'AZURE_INDIVIDUAL_MODE': str(individual_mode).lower(),
            'AZURE_MODEL_DEPLOYMENT_PROFILE': profile,
            'AZURE_CONTAINER_APPS_DEPLOY': str(container_apps).lower(),
            **extra,
        }
        if attendees:
            settings['AZURE_ATTENDEE_LIST'] = json.dumps(attendees, separators=(',', ':'))
        elif attendee_count is not None:
            settings['AZURE_ATTENDEE_COUNT'] = str(attendee_count)

        _print('\n📋 Configuration summary', color=COLORS.bold)
        _print(f'  Mode: {"individual" if individual_mode else "organizer"}')
        _print(f'  Environment: {environment}')
        _print(f'  Subscription: {account["subscription_id"]}')
        _print(f'  Region: {location}')
        _print(f'  Resource group: {resource_group}')
        _print(f'  Model profile: {profile}')
        _print(f'  Container Apps: {"enabled" if container_apps else "disabled"}')
        if not individual_mode:
            _print(f'  Attendees/projects: {len(attendees) if attendees else attendee_count}')

        _set_environment(azd, settings)
        _print('\n✅ Configuration saved.', color=COLORS.green)
        if container_apps and not _check_docker():
            if not _warn_docker_not_running():
                _print(
                    'Start Docker Desktop, then run `azd provision` when ready. 👋',
                    color=COLORS.yellow,
                )
                return 0
        if not _ask_yes_no(
            '\nWould you like to start provisioning now? '
            'This creates Azure resources.',
            True,
        ):
            _print('Run `azd provision` later from this repository when you are ready. 👋')
            return 0
        rc = _provision(azd)
        if rc == 0:
            _show_post_provision_summary(
                azd,
                individual_mode=individual_mode,
                environment=environment,
            )
        return rc
    except (KeyboardInterrupt, EOFError):
        _print('\n\nSetup cancelled. No provisioning was started.', color=COLORS.yellow)
        return 130
    except RuntimeError as exc:
        _print(f'\n❌ {exc}', color=COLORS.red)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
