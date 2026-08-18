from .script_test_helpers import load_script

prepare_attendee_roles = load_script('prepare_attendee_roles_script', 'prepare-attendee-roles.py')


def test_parse_attendee_list_rejects_invalid_entries() -> None:
    try:
        prepare_attendee_roles._parse_attendee_list('[{"upn":""}]')
    except ValueError as error:
        assert 'non-empty' in str(error)
    else:
        raise AssertionError('Expected an empty UPN to raise ValueError')


def test_compute_resolved_entries_shares_non_individual_project() -> None:
    attendees = [
        {'upn': 'one@example.com'},
        {'upn': 'two@example.com', 'individualProject': False},
    ]
    entries = prepare_attendee_roles._compute_resolved_entries(
        attendees, 'foundry-user', 'attendee', 'facilitator', 'proctor', 'organizer',
        False, True,
    )
    assert entries[0]['projectName'] == 'one'
    assert entries[1]['projectName'] == 'one'
