"""Health check for the introduction-foundry-agent-service lab series.

Runs the shared core checks then adds lab-specific validation:
- Additional environment variables used across the IFS lab modules.
- MCP server reachability checks (retail-remedy-ops and flight-ops).

Run from the repository root:

    uv run python labs/introduction-foundry-agent-service/shared/health-check.py
"""

from __future__ import annotations

import os
import sys

# Add the repository root to sys.path so that shared.health_check is importable
# regardless of the working directory from which this script is invoked.
_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import shared.health_check as core  # noqa: E402

# Environment variables used by specific IFS lab modules.  Checked as optional
# warnings - missing values do not block core lab progress but must be set
# before the relevant module.
_ADDITIONAL_ENV_VARS = [
    'AGENT_NAME',
    'HOSTED_AGENT_NAME_CONTAINER',
    'HOSTED_AGENT_NAME_CODE',
    'KNOWLEDGE_BASE_NAME',
    'TOOLBOX_NAME',
    'AZURE_CONTAINER_REGISTRY_NAME',
    'AZURE_CONTAINER_REGISTRY_ENDPOINT',
    'RETAIL_REMEDY_OPS_MCP_SERVER_PORT',
    'RETAIL_REMEDY_OPS_MCP_SERVER_URL',
    'RETAIL_REMEDY_OPS_MCP_SERVER_LABEL',
    'FLIGHT_OPS_MCP_SERVER_URL',
    'FLIGHT_OPS_MCP_SERVER_LABEL',
    'AZURE_SEARCH_PASSENGER_RIGHTS_INDEX_NAME',
]


def _check_additional_env_vars() -> None:
    core._section('Additional environment variables (lab-specific)')
    for var in _ADDITIONAL_ENV_VARS:
        val = os.getenv(var, '')
        core.check_optional(
            var, bool(val), 'set' if val else 'not set \u2014 copy from your onboarding file'
        )


def main() -> int:
    """Run core and introduction-foundry-agent-service lab health checks."""
    print('Workshop Environment Health Check')
    print('\u2550' * 34)

    core.run_core_checks()

    _check_additional_env_vars()

    retail_remedy_ops_mcp_url = os.getenv('RETAIL_REMEDY_OPS_MCP_SERVER_URL', '').strip()
    core._check_mcp_server(retail_remedy_ops_mcp_url, 'MCP Server (retail-remedy-ops)')

    flight_ops_mcp_url = os.getenv('FLIGHT_OPS_MCP_SERVER_URL', '').strip()
    core._check_mcp_server(flight_ops_mcp_url, 'MCP Server (flight-ops)')

    return core._print_summary()


if __name__ == '__main__':
    raise SystemExit(main())
