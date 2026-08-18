from unittest.mock import patch

from .script_test_helpers import load_script

deploy_retail_remedy = load_script('deploy_retail_remedy_script', 'deploy-retail-remedy-ops-mcp-server.py')


def test_truthy_and_docker_build_args() -> None:
    assert deploy_retail_remedy._is_truthy('on') is True
    assert deploy_retail_remedy._is_truthy('') is False
    with patch.dict(deploy_retail_remedy.os.environ, {}, clear=True):
        assert deploy_retail_remedy._docker_build_args() == []
    with patch.dict(
        deploy_retail_remedy.os.environ,
        {'UV_DEFAULT_INDEX': 'https://packages.example/simple/', 'HTTPS_PROXY': 'http://proxy.example:8080'},
        clear=True,
    ):
        assert deploy_retail_remedy._docker_build_args() == [
            '--build-arg', 'UV_DEFAULT_INDEX', '--build-arg', 'HTTPS_PROXY',
        ]
