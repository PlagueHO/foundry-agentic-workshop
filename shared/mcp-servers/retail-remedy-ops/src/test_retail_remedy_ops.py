"""Tests for Retail Remedy Operations MCP server tool functions."""

from server import (
    create_remedy_case,
    draft_remedy_summary,
    find_replacement_options,
    get_product_profile,
    lookup_purchase,
    search_store_policy,
)


def test_lookup_purchase_found():
    result = lookup_purchase('R-1007')
    assert result['receipt_id'] == 'R-1007'
    assert result['product_id'] == 'PROD-LAPTOP-14'
    assert result['customer_id'] == 'C-1042'


def test_lookup_purchase_not_found():
    result = lookup_purchase('R-9999')
    assert 'error' in result


def test_get_product_profile_found():
    result = get_product_profile('PROD-LAPTOP-14')
    assert result['product_id'] == 'PROD-LAPTOP-14'
    assert result['expected_lifespan_months'] == 36
    assert result['warranty_months'] == 12


def test_get_product_profile_not_found():
    result = get_product_profile('PROD-UNKNOWN')
    assert 'error' in result


def test_search_store_policy_matches_battery():
    results = search_store_policy('battery')
    assert isinstance(results, list)
    assert len(results) >= 1
    assert 'note' not in results[0]


def test_search_store_policy_no_match_returns_note():
    results = search_store_policy('xyzzy_no_match_keyword')
    assert isinstance(results, list)
    assert len(results) == 1
    assert 'note' in results[0]


def test_find_replacement_options_found():
    result = find_replacement_options('PROD-LAPTOP-14')
    assert 'replacements' in result
    assert len(result['replacements']) >= 1


def test_find_replacement_options_not_found():
    result = find_replacement_options('PROD-UNKNOWN')
    assert 'error' in result


def test_draft_remedy_summary_shape():
    result = draft_remedy_summary(
        receipt_id='R-1007',
        product_name='ProBook 14 Laptop',
        issue='Battery retains only 20% charge after normal use',
        likely_failure_type='major',
        recommended_remedy='Full refund or replacement at customer choice under ACL',
    )
    assert result['receipt_id'] == 'R-1007'
    assert result['status'] == 'draft'
    assert 'disclaimer' in result
    assert result['likely_failure_type'] == 'major'


def test_create_remedy_case_is_deterministic():
    result1 = create_remedy_case('R-1007', 'refund')
    result2 = create_remedy_case('R-1007', 'refund')
    assert result1['case_id'] == result2['case_id']
    assert result1['status'] == 'created'
    assert result1['case_id'].startswith('CASE-')
