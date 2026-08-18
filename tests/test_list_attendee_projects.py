from unittest.mock import patch

from .script_test_helpers import load_script

list_attendee_projects = load_script('list_attendee_projects_script', 'list-attendee-projects.py')


def test_main_prints_requested_project_count() -> None:
    with patch.object(list_attendee_projects.argparse, 'ArgumentParser') as parser:
        parser.return_value.parse_args.return_value.count = 2
        parser.return_value.parse_args.return_value.prefix = 'attendee'
        with patch.object(list_attendee_projects, 'print') as output:
            list_attendee_projects.main()
    assert output.call_count == 2
