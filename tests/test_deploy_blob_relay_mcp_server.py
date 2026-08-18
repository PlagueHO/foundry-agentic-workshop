from unittest.mock import patch

from .script_test_helpers import load_script

deploy_blob_relay = load_script('deploy_blob_relay_script', 'deploy-blob-relay-mcp-server.py')


def test_truthy_and_docker_build_args() -> None:
    assert deploy_blob_relay._is_truthy('true') is True
    assert deploy_blob_relay._is_truthy('off') is False
    with patch.dict(deploy_blob_relay.os.environ, {'AZURE_CONTAINER_REGISTRY_NAME': 'registry'}, clear=True):
        assert deploy_blob_relay._docker_build_args() == []
    with patch.dict(
        deploy_blob_relay.os.environ,
        {'https_proxy': 'http://proxy.example:8080', 'no_proxy': 'localhost'},
        clear=True,
    ):
        assert deploy_blob_relay._docker_build_args() == [
            '--build-arg', 'HTTPS_PROXY', '--build-arg', 'NO_PROXY',
        ]
