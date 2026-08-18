from pathlib import Path

from .script_test_helpers import load_script

seed_document_index = load_script('seed_document_index_script', 'seed-document-index.py')


def test_load_documents_returns_json_records(tmp_path: Path) -> None:
    path = tmp_path / 'documents.json'
    path.write_text('{"id": "doc-1"}\n', encoding='utf-8')
    assert seed_document_index._load_documents(path) == [{'id': 'doc-1'}]
