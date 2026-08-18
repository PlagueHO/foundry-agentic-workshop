from unittest.mock import MagicMock, patch

from .script_test_helpers import load_script

delete_attendee_portal = load_script('delete_attendee_portal_script', 'delete-attendee-portal.py')


def test_load_azd_env_returns_empty_dict_on_command_failure() -> None:
    result = MagicMock(returncode=1, stdout='not json')
    with patch.object(delete_attendee_portal.subprocess, 'run', return_value=result):
        assert delete_attendee_portal._load_azd_env() == {}
