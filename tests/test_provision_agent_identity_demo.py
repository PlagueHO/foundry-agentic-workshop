"""Tests for the agent identity demo provisioning script."""

# pylint: disable=protected-access

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_provisioner() -> ModuleType:
    path = Path(__file__).parents[1] / 'scripts' / 'provision-agent-identity-demo.py'
    spec = importlib.util.spec_from_file_location('provision_agent_identity_demo', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Could not load {path}.')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provisioner = _load_provisioner()


def test_connection_name_is_unique_to_each_foundry_project() -> None:
    """Prevent a connection owned by one project from being reused by another."""
    first_connection = provisioner._connection_name('lab-attendee-1')
    second_connection = provisioner._connection_name('lab-attendee-2')

    assert first_connection == 'blob-relay-lab-attendee-1'
    assert second_connection == 'blob-relay-lab-attendee-2'
    assert first_connection != second_connection
