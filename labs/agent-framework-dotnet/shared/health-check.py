"""Health check for the agent-framework-dotnet lab series.

Runs the shared core checks then adds lab-specific validation:
- .NET 10 SDK installation.
- NuGet package restore for the lab solution.

Run from the repository root:

    python labs/agent-framework-dotnet/shared/health-check.py
"""

from __future__ import annotations

import os
import subprocess
import sys

# Add the repository root to sys.path so that shared.health_check is importable
# regardless of the working directory from which this script is invoked.
_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import shared.health_check as core  # noqa: E402


def _check_dotnet() -> bool:
    """Check that the .NET 10 SDK is installed.

    .NET 10 is required by all modules in the agent-framework-dotnet lab.
    Returns True only when a 10.x SDK is found.
    """
    rc, out, _ = core._az('dotnet --version')
    if rc != 0:
        core.check_optional(
            '.NET 10 SDK installed',
            False,
            'not found \u2014 install from https://dot.net/download',
        )
        return False
    version = out.strip().splitlines()[0]
    is_v10 = version.startswith('10.')
    core.check_optional(
        '.NET 10 SDK installed',
        is_v10,
        version if is_v10
        else f'{version} (need 10.x \u2014 install from https://dot.net/download)',
    )
    return is_v10


def _check_dotnet_restore() -> None:
    """Verify that NuGet packages for the agent-framework-dotnet lab can be restored.

    Probes the Module 02 starter project as a representative of the whole lab.
    A successful restore confirms the SDK can reach NuGet and resolve the
    Microsoft Agent Framework packages referenced by Directory.Packages.props.
    """
    probe_proj = os.path.join(
        _REPO_ROOT,
        'labs', 'agent-framework-dotnet', '02-first-agent', 'src',
        'TripConcierge.FirstAgent.csproj',
    )
    if not os.path.exists(probe_proj):
        core.check_optional(
            '.NET packages restorable',
            False,
            f'project not found: {probe_proj}',
        )
        return
    result = subprocess.run(
        ['dotnet', 'restore', probe_proj, '--nologo'],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        core.check_optional('.NET packages restorable', True, 'TripConcierge.FirstAgent restored')
    else:
        err_lines = (result.stderr or result.stdout).strip().splitlines()
        err_line = err_lines[0] if err_lines else 'restore failed'
        core.check_optional('.NET packages restorable', False, err_line)


def _check_lab_agent_framework_dotnet() -> None:
    """Run health checks specific to the agent-framework-dotnet lab."""
    core._banner('agent-framework-dotnet Lab Requirements')
    core._section('.NET prerequisites')
    dotnet_ok = _check_dotnet()
    if dotnet_ok:
        _check_dotnet_restore()
    else:
        core.check_optional(
            '.NET packages restorable',
            False,
            'skipped \u2014 requires .NET 10 SDK',
        )
    print(
        f'\n  {core.WARN}  Docker (optional for Module 12 \u2014 Aspire Dashboard)'
        '  (see Core Prerequisites above)'
    )


def main() -> int:
    """Run core and agent-framework-dotnet lab health checks."""
    print('Workshop Environment Health Check')
    print('\u2550' * 34)

    core.run_core_checks()

    _check_lab_agent_framework_dotnet()

    return core._print_summary()


if __name__ == '__main__':
    raise SystemExit(main())
