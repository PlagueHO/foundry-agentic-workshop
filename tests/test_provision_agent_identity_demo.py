"""Tests for the agent identity demo provisioning script."""

from .script_test_helpers import load_script

provisioner = load_script(
    'provision_agent_identity_demo_script',
    'provision-agent-identity-demo.py',
)


def test_connection_name_is_unique_to_each_foundry_project() -> None:
    """Prevent a connection owned by one project from being reused by another."""
    first_connection = provisioner._connection_name('lab-attendee-1')
    second_connection = provisioner._connection_name('lab-attendee-2')

    assert first_connection == 'blob-relay-lab-attendee-1'
    assert second_connection == 'blob-relay-lab-attendee-2'
    assert first_connection != second_connection


def test_project_endpoint_and_truthy_helpers() -> None:
    assert provisioner._project_endpoint('https://example.test/', 'demo') == (
        'https://example.test/api/projects/demo'
    )
    assert provisioner._is_truthy('true') is True
    assert provisioner._is_truthy('false') is False
