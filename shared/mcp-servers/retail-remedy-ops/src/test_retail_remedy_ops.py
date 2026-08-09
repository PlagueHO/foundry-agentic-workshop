"""Tests for Retail Remedy Operations MCP server tool functions."""

from __future__ import annotations

import pytest

from server import (
    create_remedy_case,
    draft_remedy_summary,
    find_replacement_options,
    get_product_profile,
    lookup_purchase,
    search_store_policy,
)


@pytest.mark.parametrize(
    ('receipt_id', 'product_id'),
    [
        ('R-1007', 'PROD-LAPTOP-14'),
        ('R-1023', 'PROD-PHONE-07'),
        ('R-1031', 'PROD-HEADPHONES-03'),
    ],
)
def test_lookup_purchase_returns_known_records(
    receipt_id: str, product_id: str
) -> None:
    result = lookup_purchase(receipt_id)

    assert result['receipt_id'] == receipt_id
    assert result['product_id'] == product_id
    assert result['customer_id'].startswith('C-')
    assert result['currency'] == 'AUD'


def test_lookup_purchase_found() -> None:
    result = lookup_purchase('R-1007')
    assert result['receipt_id'] == 'R-1007'
    assert result['product_id'] == 'PROD-LAPTOP-14'
    assert result['customer_id'] == 'C-1042'


@pytest.mark.parametrize('receipt_id', ['', 'r-1007', ' R-1007 ', 'R-9999'])
def test_lookup_purchase_not_found(receipt_id: str) -> None:
    result = lookup_purchase(receipt_id)
    assert result == {'error': f'Receipt {receipt_id} not found'}


@pytest.mark.parametrize(
    ('product_id', 'category'),
    [
        ('PROD-LAPTOP-14', 'laptop'),
        ('PROD-PHONE-07', 'mobile_phone'),
        ('PROD-HEADPHONES-03', 'headphones'),
    ],
)
def test_get_product_profile_returns_known_profiles(
    product_id: str, category: str
) -> None:
    result = get_product_profile(product_id)

    assert result['product_id'] == product_id
    assert result['category'] == category
    assert result['expected_lifespan_months'] > 0
    assert result['warranty_months'] > 0
    assert result['current_rrp_aud'] > 0


def test_get_product_profile_found() -> None:
    result = get_product_profile('PROD-LAPTOP-14')
    assert result['product_id'] == 'PROD-LAPTOP-14'
    assert result['expected_lifespan_months'] == 36
    assert result['warranty_months'] == 12


@pytest.mark.parametrize('product_id', ['', 'prod-laptop-14', 'PROD-UNKNOWN'])
def test_get_product_profile_not_found(product_id: str) -> None:
    result = get_product_profile(product_id)
    assert result == {'error': f'Product {product_id} not found'}


def test_search_store_policy_matches_battery() -> None:
    results = search_store_policy('battery')
    assert isinstance(results, list)
    assert len(results) >= 1
    assert 'note' not in results[0]


def test_search_store_policy_no_match_returns_note() -> None:
    results = search_store_policy('xyzzy_no_match_keyword')
    assert isinstance(results, list)
    assert len(results) == 1
    assert 'note' in results[0]


def test_search_store_policy_is_case_insensitive_and_matches_titles() -> None:
    results = search_store_policy('PRO-RATA REFUND CALCULATION')

    assert len(results) == 1
    assert results[0]['policy_id'] == 'POL-005'
    assert results[0]['title'] == 'Pro-Rata Refund Calculation'


def test_search_store_policy_can_return_multiple_keyword_matches() -> None:
    results = search_store_policy('consumer guarantee')

    assert [result['policy_id'] for result in results] == [
        'POL-001',
        'POL-002',
    ]


def test_search_store_policy_preserves_original_topic_in_no_match_note() -> None:
    results = search_store_policy('  no such policy  ')

    assert results == [{'note': 'No specific policy found for topic:   no such policy  '}]


def test_search_store_policy_empty_topic_matches_all_policies() -> None:
    results = search_store_policy('')

    assert len(results) == 6
    assert all('policy_id' in result for result in results)


@pytest.mark.parametrize(
    ('product_id', 'replacement_count'),
    [
        ('PROD-LAPTOP-14', 3),
        ('PROD-PHONE-07', 2),
        ('PROD-HEADPHONES-03', 1),
    ],
)
def test_find_replacement_options_returns_inventory(
    product_id: str, replacement_count: int
) -> None:
    result = find_replacement_options(product_id)

    assert result['product_id'] == product_id
    assert result['current_stock_status'] == 'in_stock'
    assert len(result['replacements']) == replacement_count
    for replacement in result['replacements']:
        assert replacement['product_id'].startswith('PROD-')
        assert replacement['current_price_aud'] > 0
        assert 'price_delta_aud' in replacement


def test_find_replacement_options_found() -> None:
    result = find_replacement_options('PROD-LAPTOP-14')
    assert 'replacements' in result
    assert len(result['replacements']) >= 1


@pytest.mark.parametrize('product_id', ['', 'prod-laptop-14', 'PROD-UNKNOWN'])
def test_find_replacement_options_not_found(product_id: str) -> None:
    result = find_replacement_options(product_id)
    assert result == {'error': f'No inventory data for product {product_id}'}


def test_draft_remedy_summary_shape() -> None:
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


def test_draft_remedy_summary_preserves_optional_notes() -> None:
    result = draft_remedy_summary(
        receipt_id='R-1023',
        product_name='Nova X7 Smartphone',
        issue='Device will not charge',
        likely_failure_type='minor',
        recommended_remedy='Repair within a reasonable time',
        notes='Customer provided photos.',
    )

    assert result == {
        'receipt_id': 'R-1023',
        'product_name': 'Nova X7 Smartphone',
        'issue': 'Device will not charge',
        'likely_failure_type': 'minor',
        'recommended_remedy': 'Repair within a reasonable time',
        'notes': 'Customer provided photos.',
        'status': 'draft',
        'disclaimer': 'General guidance only - not legal advice.',
    }


def test_draft_remedy_summary_defaults_notes_to_empty_string() -> None:
    result = draft_remedy_summary('R-1031', 'Headphones', 'No sound', 'minor', 'Repair')

    assert result['notes'] == ''
    assert result['status'] == 'draft'


def test_create_remedy_case_is_deterministic() -> None:
    result1 = create_remedy_case('R-1007', 'refund')
    result2 = create_remedy_case('R-1007', 'refund')
    assert result1['case_id'] == result2['case_id']
    assert result1['status'] == 'created'
    assert result1['case_id'].startswith('CASE-')


@pytest.mark.parametrize(
    ('receipt_id', 'expected_case_id'),
    [
        ('R-1007', 'CASE-2026-01007'),
        ('R-1A2B', 'CASE-2026-00012'),
        ('receipt-without-digits', 'CASE-2026-00000'),
        ('R-99999', 'CASE-2026-09999'),
    ],
)
def test_create_remedy_case_normalizes_receipt_digits(
    receipt_id: str, expected_case_id: str
) -> None:
    result = create_remedy_case(receipt_id, 'refund')

    assert result['case_id'] == expected_case_id
    assert result['receipt_id'] == receipt_id
    assert result['remedy_type'] == 'refund'
    assert result['notes'] == ''


def test_create_remedy_case_preserves_notes_and_includes_case_id_in_message() -> None:
    result = create_remedy_case('R-1007', 'replacement', 'Approved by supervisor')

    assert result['notes'] == 'Approved by supervisor'
    assert result['message'] == (
        f"Case {result['case_id']} created successfully (simulated)."
    )
