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
