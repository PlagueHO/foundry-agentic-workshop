"""Seed the retail-product Azure AI Search vector index from shared/data/retail-products.jsonl.

This script creates a vector-capable HNSW index with semantic search support and
uploads pre-embedded product records (contentVector is already in the JSONL file;
no runtime embedding is performed).

Environment variables:
  AZURE_SEARCH_SERVICE_NAME         Azure AI Search service name (azd output).
  AZURE_SEARCH_PRODUCT_INDEX_NAME   Target index name (default 'retail-products').
  AZURE_SEARCH_ADMIN_KEY            Optional admin key; DefaultAzureCredential is used
                                    when not provided.
"""
# pylint: disable=duplicate-code

from __future__ import annotations

import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

_VECTOR_DIMENSIONS = 1536
_HNSW_CONFIG_NAME = 'retail-product-hnsw'
_VECTOR_PROFILE_NAME = 'retail-product-vector-profile'
_SEMANTIC_CONFIG_NAME = 'retail-product-semantic-config'


def _load_documents(path: Path) -> list[dict]:
    docs: list[dict] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if stripped:
            docs.append(json.loads(stripped))
    return docs


def _build_credential():
    admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY', '').strip()
    if admin_key:
        return AzureKeyCredential(admin_key)
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def _ensure_product_index(index_client: SearchIndexClient, index_name: str) -> None:
    existing = {idx.name for idx in index_client.list_indexes()}
    if index_name in existing:
        print(f'Index {index_name!r} already exists; skipping creation.')
        return

    fields = [
        SimpleField(name='id', type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name='title', type=SearchFieldDataType.String),
        SearchableField(name='content', type=SearchFieldDataType.String),
        SearchableField(
            name='category',
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchField(
            name='tags',
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            searchable=True,
            filterable=True,
        ),
        SimpleField(name='price', type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name='currency', type=SearchFieldDataType.String, filterable=True),
        SimpleField(
            name='stock_quantity',
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SimpleField(name='rating', type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name='created_at', type=SearchFieldDataType.String),
        SearchField(
            name='contentVector',
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=_VECTOR_DIMENSIONS,
            vector_search_profile_name=_VECTOR_PROFILE_NAME,
        ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=_HNSW_CONFIG_NAME)],
        profiles=[
            VectorSearchProfile(
                name=_VECTOR_PROFILE_NAME,
                algorithm_configuration_name=_HNSW_CONFIG_NAME,
            )
        ],
    )
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name=_SEMANTIC_CONFIG_NAME,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name='title'),
                    content_fields=[SemanticField(field_name='content')],
                ),
            )
        ]
    )
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
    index_client.create_index(index)
    print(f'Created index {index_name!r}.')


def main() -> int:
    """Seed the retail-product search index with documents from the shared data file."""
    service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()
    if not service_name:
        print('AZURE_SEARCH_SERVICE_NAME is not set. Skipping retail product index seed.')
        return 0

    index_name = os.getenv('AZURE_SEARCH_PRODUCT_INDEX_NAME', 'retail-products').strip()
    data_path = Path(__file__).resolve().parents[1] / 'shared' / 'data' / 'retail-products.jsonl'
    if not data_path.exists():
        repo_root = Path(__file__).resolve().parents[1]
        rel = data_path.relative_to(repo_root)
        print(
            f'Data file not found: {data_path}\n'
            'Run the data generator to create it:\n'
            f'  cd tools/python\n'
            f'  python -m data_generator --scenario retail-product --count 100 '
            f'--industry supermarket --out-file ../../{rel}'
        )
        return 1

    endpoint = f'https://{service_name}.search.windows.net'
    credential = _build_credential()
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    _ensure_product_index(index_client=index_client, index_name=index_name)

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    docs = _load_documents(data_path)
    if not docs:
        print('No documents found in retail-products.jsonl.')
        return 0

    results = search_client.upload_documents(documents=docs)
    failed = [r.key for r in results if not r.succeeded]
    if failed:
        print(f'Upload completed with failures. Failed document IDs: {", ".join(failed)}')
        return 1

    print(f'Uploaded {len(docs)} retail-product documents to index {index_name!r}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
