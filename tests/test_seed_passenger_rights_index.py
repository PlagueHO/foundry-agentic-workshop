from pathlib import Path

from .script_test_helpers import load_script

seed_passenger_rights = load_script('seed_passenger_rights_script', 'seed-passenger-rights-index.py')


def test_load_documents_returns_json_records(tmp_path: Path) -> None:
    path = tmp_path / 'rights.json'
    path.write_text('{"id": "right-1"}\n', encoding='utf-8')
    assert seed_passenger_rights._load_documents(path) == [{'id': 'right-1'}]
