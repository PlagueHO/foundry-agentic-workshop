"""
flight-ops MCP server - provides flight status, rebooking options, and
compensation claim tools for the Trip Disruption Concierge demo.

Start with:
    python shared/mcp-servers/flight-ops/src/server.py

The server listens on http://0.0.0.0:<FLIGHT_OPS_MCP_SERVER_PORT>/mcp (default port 3001).
Override with FLIGHT_OPS_MCP_SERVER_PORT environment variable.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

_PORT = int(os.environ.get('FLIGHT_OPS_MCP_SERVER_PORT', '3001'))

mcp = FastMCP(
    name='flight-ops',
    instructions=(
        'Provides live flight status, rebooking options, and compensation '
        'claim filing for airline passenger disruptions.'
    ),
    host='0.0.0.0',
    port=_PORT,
)

# ---------------------------------------------------------------------------
# Static fixture data
# ---------------------------------------------------------------------------

_FLIGHT_STATUS: dict[str, dict] = {
    'AU123': {
        'flight_number': 'AU123',
        'origin': 'AKL',
        'destination': 'SYD',
        'scheduled_departure': '2025-06-24T08:00:00+12:00',
        'status': 'CANCELLED',
        'cancellation_reason': 'Aircraft unserviceable - maintenance fault',
        'notice_hours': 3,
    },
    'AU124': {
        'flight_number': 'AU124',
        'origin': 'AKL',
        'destination': 'SYD',
        'scheduled_departure': '2025-06-24T14:30:00+12:00',
        'status': 'ON_TIME',
        'cancellation_reason': None,
        'notice_hours': None,
    },
    'AU125': {
        'flight_number': 'AU125',
        'origin': 'AKL',
        'destination': 'SYD',
        'scheduled_departure': '2025-06-24T19:00:00+12:00',
        'status': 'DELAYED',
        'delay_minutes': 90,
        'cancellation_reason': None,
        'notice_hours': None,
    },
}

_REBOOKING_OPTIONS: list[dict] = [
    {
        'flight_number': 'AU124',
        'origin': 'AKL',
        'destination': 'SYD',
        'departure': '2025-06-24T14:30:00+12:00',
        'arrival': '2025-06-24T16:00:00+11:00',
        'seats_available': 4,
        'cabin_class': 'Economy',
    },
    {
        'flight_number': 'AU126',
        'origin': 'AKL',
        'destination': 'SYD',
        'departure': '2025-06-25T08:00:00+12:00',
        'arrival': '2025-06-25T09:30:00+11:00',
        'seats_available': 12,
        'cabin_class': 'Economy',
    },
    {
        'flight_number': 'AU127',
        'origin': 'AKL',
        'destination': 'SYD',
        'departure': '2025-06-24T14:30:00+12:00',
        'arrival': '2025-06-24T16:00:00+11:00',
        'seats_available': 2,
        'cabin_class': 'Business',
    },
]

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_flight_status(flight_number: str) -> str:
    """
    Returns the current status of a flight.

    Args:
        flight_number: IATA flight number, e.g. AU123.
    """
    flight = _FLIGHT_STATUS.get(flight_number.upper())
    if flight is None:
        return json.dumps({
            'error': f'Flight {flight_number} not found.',
            'available_flights': list(_FLIGHT_STATUS.keys()),
        })
    return json.dumps(flight)


@mcp.tool()
def get_rebooking_options(
    booking_ref: str,
    origin: str,
    destination: str,
) -> str:
    """
    Returns available rebooking options for a disrupted passenger.

    Args:
        booking_ref: Passenger booking reference, e.g. BK98765.
        origin:      IATA origin airport code, e.g. AKL.
        destination: IATA destination airport code, e.g. SYD.
    """
    options = [
        opt
        for opt in _REBOOKING_OPTIONS
        if opt['origin'].upper() == origin.upper()
        and opt['destination'].upper() == destination.upper()
    ]

    return json.dumps({
        'booking_ref': booking_ref,
        'route': f'{origin.upper()}→{destination.upper()}',
        'options_count': len(options),
        'options': options,
    })


@mcp.tool()
def file_compensation_claim(
    booking_ref: str,
    flight_number: str,
    reason: str,
) -> str:
    """
    Files a passenger compensation claim for a disrupted flight.

    Args:
        booking_ref:    Passenger booking reference, e.g. BK98765.
        flight_number:  Disrupted flight number, e.g. AU123.
        reason:         Reason for the claim (cancellation, delay, etc.).
    """
    claim_id = f'CLM-{uuid.uuid4().hex[:8].upper()}'
    filed_at = datetime.now(timezone.utc).isoformat()

    return json.dumps({
        'claim_id': claim_id,
        'booking_ref': booking_ref,
        'flight_number': flight_number.upper(),
        'reason': reason,
        'filed_at': filed_at,
        'status': 'SUBMITTED',
        'expected_resolution_days': 10,
        'message': (
            f'Compensation claim {claim_id} submitted successfully. '
            f'You will receive a decision within 10 business days.'
        ),
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'Starting flight-ops MCP server on http://0.0.0.0:{_PORT}/mcp')
    mcp.run(transport='streamable-http')
