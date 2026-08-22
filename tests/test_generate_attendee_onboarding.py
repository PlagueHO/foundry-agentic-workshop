from .script_test_helpers import load_script

generate_onboarding = load_script('generate_onboarding_script', 'generate-attendee-onboarding.py')


def test_upn_key_normalizes_attendee_filename() -> None:
    assert generate_onboarding._upn_key('Jane.Doe_Smith@contoso.com') == 'jane-doe-smith'


def test_parse_resolved_list_rejects_non_array() -> None:
    try:
        generate_onboarding._parse_resolved_list('{"upn":"jane@example.com"}')
    except ValueError as error:
        assert 'JSON array' in str(error)
    else:
        raise AssertionError('Expected invalid resolved list to raise ValueError')


def test_attendee_environment_distinguishes_portal_and_sdk_mcp_identifiers() -> None:
    env = generate_onboarding._build_attendee_env_dict(
        project_name='workshop',
        subscription_id='subscription',
        resource_group='resource-group',
        foundry_name='foundry',
        foundry_custom_domain_name='foundry-domain',
        search_service_name='search',
        container_registry_name='registry',
        container_registry_endpoint='registry.azurecr.io',
        mcp_server_url='https://example.test/mcp',
        flight_ops_mcp_server_url='https://flight.example.test/mcp',
    )

    assert env['TOOLBOX_MCP_CONNECTION_NAME'] == 'retail-remedy-ops'
    assert env['TOOLBOX_MCP_SERVER_LABEL'] == 'retail-remedy-ops'
