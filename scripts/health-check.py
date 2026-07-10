"""Workshop environment health check - core checks entry point.

Runs the core set of environment checks required for all workshop labs.
For lab-specific checks (additional env vars, MCP servers, .NET SDK, etc.)
run the health-check script in the lab's shared/ folder instead:

    uv run python labs/introduction-foundry-agent-service/shared/health-check.py
    uv run python labs/agent-framework-dotnet/shared/health-check.py
"""

from __future__ import annotations

import os
import sys

# Add the repository root to sys.path so that shared.health_check is importable
# regardless of the working directory from which this script is invoked.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import shared.health_check as core  # noqa: E402

if __name__ == '__main__':
    raise SystemExit(core.main())
