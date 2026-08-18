from unittest.mock import patch

from .script_test_helpers import load_script

ensure_resource_group = load_script('ensure_resource_group_script', 'ensure-resource-group.py')


def test_env_strips_missing_and_present_values() -> None:
    with patch.dict(ensure_resource_group.os.environ, {'DEMO_VALUE': '  value  '}, clear=True):
        assert ensure_resource_group._env('DEMO_VALUE') == 'value'
    with patch.dict(ensure_resource_group.os.environ, {}, clear=True):
        assert ensure_resource_group._env('DEMO_VALUE') == ''
