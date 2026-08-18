from unittest.mock import patch

from .script_test_helpers import load_script

deploy_flight_ops = load_script('deploy_flight_ops_script', 'deploy-flight-ops-mcp-server.py')


def test_truthy_and_docker_build_args() -> None:
    assert deploy_flight_ops._is_truthy('1') is True
    assert deploy_flight_ops._is_truthy('false') is False
    with patch.dict(deploy_flight_ops.os.environ, {}, clear=True):
        assert deploy_flight_ops._docker_build_args() == []
    with patch.dict(
        deploy_flight_ops.os.environ,
        {'HTTPS_PROXY': 'http://proxy.example:8080'},
        clear=True,
    ):
        assert deploy_flight_ops._docker_build_args() == ['--build-arg', 'HTTPS_PROXY']
