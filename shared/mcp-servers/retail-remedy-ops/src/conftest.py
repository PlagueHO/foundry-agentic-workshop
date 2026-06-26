"""
Pytest configuration for retail-remedy-ops MCP server tests.

Ensures this server's src/ directory is first on sys.path and clears any
stale 'server' module cached from another MCP server's test run.
"""

import sys
from pathlib import Path

_src_dir = str(Path(__file__).parent)
sys.modules.pop('server', None)
if _src_dir in sys.path:
    sys.path.remove(_src_dir)
sys.path.insert(0, _src_dir)
