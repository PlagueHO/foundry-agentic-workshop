from pathlib import Path

from .script_test_helpers import load_script

seed_product_index = load_script('seed_product_index_script', 'seed-product-index.py')


def test_load_documents_returns_json_records(tmp_path: Path) -> None:
    path = tmp_path / 'products.json'
    path.write_text('{"id": "product-1"}\n', encoding='utf-8')
    assert seed_product_index._load_documents(path) == [{'id': 'product-1'}]
