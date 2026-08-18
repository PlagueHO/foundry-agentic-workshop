from unittest.mock import patch

from .script_test_helpers import load_script

deploy_attendee_portal = load_script('deploy_attendee_portal_script', 'deploy-attendee-portal.py')


def test_truthy_and_command_redaction() -> None:
    assert deploy_attendee_portal._is_truthy('yes') is True
    assert deploy_attendee_portal._is_truthy('0') is False
    redacted = deploy_attendee_portal._redact_command(['az', '--password', 'secret', '--name', 'demo'])
    assert redacted == ['az', '--password', '***', '--name', 'demo']


def test_docker_build_args() -> None:
    with patch.dict(deploy_attendee_portal.os.environ, {}, clear=True):
        assert deploy_attendee_portal._docker_build_args() == []
    with patch.dict(
        deploy_attendee_portal.os.environ,
        {'UV_DEFAULT_INDEX': 'https://packages.example/simple/', 'https_proxy': 'http://proxy.example:8080'},
        clear=True,
    ):
        assert deploy_attendee_portal._docker_build_args() == [
            '--build-arg', 'UV_DEFAULT_INDEX', '--build-arg', 'HTTPS_PROXY',
        ]
