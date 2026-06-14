"""Mocked Retail Remedy Operations MCP server.

Exposes six tools that the acl-remedy-advisor agent calls during its reasoning
loop. All data is loaded from a local JSON file — no real POS, CRM, or
database connections are required.

Usage:
    python shared/mcp-servers/retail-remedy-ops/src/server.py

The server listens on http://0.0.0.0:<MCP_SERVER_PORT>/mcp (default port 8080).
Expose this port via a public dev tunnel or Codespaces port forwarding before
connecting the agent (see the Module 06 README).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_DATA_FILE = Path(__file__).parent / 'data' / 'retail-operations.json'

with _DATA_FILE.open() as _f:
    _DATA = json.load(_f)

_PURCHASES: dict = {p['receipt_id']: p for p in _DATA['purchases']}
_PRODUCTS: dict = {p['product_id']: p for p in _DATA['products']}
_POLICIES: list = _DATA['policies']
_INVENTORY: dict = _DATA['inventory']

_PORT = int(os.environ.get('MCP_SERVER_PORT', '8080'))

mcp = FastMCP('Retail Remedy Operations', host='0.0.0.0', port=_PORT)


def _log_tool_call(tool_name: str, **arguments: object) -> None:
    """Print a timestamped line for each tool call to the server console."""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
    args = ', '.join(f'{key}={value!r}' for key, value in arguments.items())
    print(f'[{timestamp}] tool call: {tool_name}({args})', flush=True)


@mcp.tool()
def lookup_purchase(receipt_id: str) -> dict:
    """Return the purchase record for the given receipt ID.

    Returns the full purchase record including customer ID, product ID,
    purchase date, price paid, channel, and store location.
    Returns an error dict if the receipt ID is not found.
    """
    _log_tool_call('lookup_purchase', receipt_id=receipt_id)
    record = _PURCHASES.get(receipt_id)
    if record is None:
        return {'error': f'Receipt {receipt_id} not found'}
    return record


@mcp.tool()
def get_product_profile(product_id: str) -> dict:
    """Return the product profile for the given product ID.

    Includes category, brand, expected lifespan in months, manufacturer
    warranty period in months, repairability rating, and current RRP.
    Returns an error dict if the product ID is not found.
    """
    _log_tool_call('get_product_profile', product_id=product_id)
    profile = _PRODUCTS.get(product_id)
    if profile is None:
        return {'error': f'Product {product_id} not found'}
    return profile


@mcp.tool()
def search_store_policy(topic: str) -> list[dict]:
    """Search store policies for excerpts relevant to the given topic.

    Matches against policy titles and keywords. Returns a list of matching
    policy objects each containing a title and an excerpt. Returns a note
    dict if no policies match.
    """
    _log_tool_call('search_store_policy', topic=topic)
    topic_lower = topic.lower()
    results = [
        p for p in _POLICIES
        if any(topic_lower in kw.lower() for kw in p.get('keywords', []))
        or topic_lower in p.get('title', '').lower()
    ]
    return results or [{'note': f'No specific policy found for topic: {topic}'}]


@mcp.tool()
def find_replacement_options(product_id: str) -> dict:
    """Return available in-stock replacement products comparable to the given product ID.

    Includes current stock status and a list of replacement options with
    current prices and price deltas relative to the original purchase price.
    Returns an error dict if no inventory data exists for the product ID.
    """
    _log_tool_call('find_replacement_options', product_id=product_id)
    entry = _INVENTORY.get(product_id)
    if entry is None:
        return {'error': f'No inventory data for product {product_id}'}
    return entry


@mcp.tool()
def draft_remedy_summary(
    receipt_id: str,
    product_name: str,
    issue: str,
    likely_failure_type: str,
    recommended_remedy: str,
    notes: str = '',
) -> dict:
    """Produce a structured staff-facing remedy summary.

    Compiles the key facts into a formatted summary for the staff member to
    present or record. Does not persist any data. The likely_failure_type
    should be 'major' or 'minor' based on the ACL assessment.
    """
    _log_tool_call(
        'draft_remedy_summary',
        receipt_id=receipt_id,
        product_name=product_name,
        issue=issue,
        likely_failure_type=likely_failure_type,
        recommended_remedy=recommended_remedy,
        notes=notes,
    )
    return {
        'receipt_id': receipt_id,
        'product_name': product_name,
        'issue': issue,
        'likely_failure_type': likely_failure_type,
        'recommended_remedy': recommended_remedy,
        'notes': notes,
        'status': 'draft',
        'disclaimer': 'General guidance only — not legal advice.',
    }


@mcp.tool()
def create_remedy_case(
    receipt_id: str,
    remedy_type: str,
    notes: str = '',
) -> dict:
    """Simulate creating a remedy case in the retail operations system.

    Returns a deterministic case ID for demonstration purposes.
    No data is actually persisted — this is a mocked write operation
    that shows how the agent would log an approved remedy outcome.
    """
    _log_tool_call(
        'create_remedy_case',
        receipt_id=receipt_id,
        remedy_type=remedy_type,
        notes=notes,
    )
    receipt_num = ''.join(filter(str.isdigit, receipt_id)) or '0'
    case_id = f'CASE-2026-{int(receipt_num) % 10000:05d}'
    return {
        'case_id': case_id,
        'receipt_id': receipt_id,
        'remedy_type': remedy_type,
        'notes': notes,
        'status': 'created',
        'message': f'Case {case_id} created successfully (simulated).',
    }


def main() -> None:
    """Start the Retail Remedy Operations MCP server."""
    print(f'Starting Retail Remedy Operations MCP server on http://0.0.0.0:{_PORT}/mcp')
    mcp.run(transport='streamable-http')


if __name__ == '__main__':
    main()
