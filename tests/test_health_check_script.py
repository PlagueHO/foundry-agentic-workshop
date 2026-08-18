from unittest.mock import patch

from .script_test_helpers import load_script

health_check_script = load_script('health_check_script', 'health-check.py')


def test_wrapper_delegates_to_shared_health_check() -> None:
    with patch.object(health_check_script.core, 'main', return_value=0) as main:
        with patch.object(health_check_script.sys, 'argv', ['health-check.py']):
            assert health_check_script.core.main() == 0
        main.assert_called_once()
