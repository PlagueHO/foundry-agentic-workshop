"""Helpers for importing hyphenated workshop scripts in unit tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, script_name: str) -> ModuleType:
    """Load one script without executing its CLI entry point."""
    path = ROOT / 'scripts' / script_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Could not load module for {path}.')
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
