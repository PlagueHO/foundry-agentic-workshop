"""
Tests for the flight-ops MCP server tools.

Run with:
    pytest shared/mcp-servers/flight-ops/src/test_flight_ops.py -v
"""

import json
import re
from datetime import datetime

import pytest

from server import file_compensation_claim, get_flight_status, get_rebooking_options


class TestGetFlightStatus:
    def test_returns_cancelled_flight(self) -> None:
        result = json.loads(get_flight_status('AU123'))
        assert result['status'] == 'CANCELLED'
        assert result['flight_number'] == 'AU123'

    def test_returns_on_time_flight(self) -> None:
        result = json.loads(get_flight_status('AU124'))
        assert result['status'] == 'ON_TIME'

    def test_returns_delayed_flight_with_delay_minutes(self) -> None:
        result = json.loads(get_flight_status('AU125'))
        assert result == {
            'flight_number': 'AU125',
            'origin': 'AKL',
            'destination': 'SYD',
            'scheduled_departure': '2025-06-24T19:00:00+12:00',
            'status': 'DELAYED',
            'delay_minutes': 90,
            'cancellation_reason': None,
            'notice_hours': None,
        }

    def test_case_insensitive_lookup(self) -> None:
        result = json.loads(get_flight_status('au123'))
        assert result['status'] == 'CANCELLED'

    def test_unknown_flight_returns_error(self) -> None:
        result = json.loads(get_flight_status('ZZ999'))
        assert result == {
            'error': 'Flight ZZ999 not found.',
            'available_flights': ['AU123', 'AU124', 'AU125'],
        }

    @pytest.mark.parametrize('flight_number', ['', ' AU123', 'AU123 '])
    def test_invalid_flight_identifier_returns_error(self, flight_number: str) -> None:
        result = json.loads(get_flight_status(flight_number))
        assert result['error'] == f'Flight {flight_number} not found.'
        assert result['available_flights'] == ['AU123', 'AU124', 'AU125']


class TestGetRebookingOptions:
    def test_returns_options_for_valid_route(self) -> None:
        result = json.loads(get_rebooking_options('BK98765', 'AKL', 'SYD'))
        assert result['booking_ref'] == 'BK98765'
        assert result['route'] == 'AKL→SYD'
        assert result['options_count'] == 3
        assert len(result['options']) == result['options_count']

    def test_options_have_expected_fields_and_match_requested_route(self) -> None:
        result = json.loads(get_rebooking_options('BK98765', 'AKL', 'SYD'))

        for option in result['options']:
            assert set(option) == {
                'flight_number',
                'origin',
                'destination',
                'departure',
                'arrival',
                'seats_available',
                'cabin_class',
            }
            assert option['origin'] == 'AKL'
            assert option['destination'] == 'SYD'
            assert option['seats_available'] > 0

    def test_case_insensitive_route(self) -> None:
        result = json.loads(get_rebooking_options('BK98765', 'akl', 'syd'))
        assert result['options_count'] > 0

    def test_no_options_for_unknown_route(self) -> None:
        result = json.loads(get_rebooking_options('BK00000', 'AKL', 'LHR'))
        assert result == {
            'booking_ref': 'BK00000',
            'route': 'AKL→LHR',
            'options_count': 0,
            'options': [],
        }

    @pytest.mark.parametrize(
        ('origin', 'destination'),
        [('', 'SYD'), ('AKL', ''), (' ', 'SYD'), ('AKL', ' SYD')],
    )
    def test_invalid_route_returns_no_options(
        self, origin: str, destination: str
    ) -> None:
        result = json.loads(get_rebooking_options('BK00000', origin, destination))
        assert result['options_count'] == 0
        assert result['options'] == []
        assert result['route'] == f'{origin.upper()}→{destination.upper()}'

    def test_booking_reference_is_preserved(self) -> None:
        result = json.loads(get_rebooking_options('  BK-123  ', 'akl', 'syd'))
        assert result['booking_ref'] == '  BK-123  '


class TestFileCompensationClaim:
    def test_returns_claim_id(self) -> None:
        result = json.loads(
            file_compensation_claim('BK98765', 'AU123', 'Flight cancelled')
        )
        assert result['status'] == 'SUBMITTED'
        assert re.fullmatch(r'CLM-[0-9A-F]{8}', result['claim_id'])

    def test_claim_preserves_inputs_and_uppercases_flight_number(self) -> None:
        result = json.loads(
            file_compensation_claim('  BK-123  ', 'au125', 'Delayed by weather')
        )
        assert result['booking_ref'] == '  BK-123  '
        assert result['flight_number'] == 'AU125'
        assert result['reason'] == 'Delayed by weather'

    def test_claim_timestamp_is_utc_iso8601(self) -> None:
        result = json.loads(
            file_compensation_claim('BK98765', 'AU123', 'Flight cancelled')
        )
        filed_at = datetime.fromisoformat(result['filed_at'])
        assert filed_at.tzinfo is not None
        assert filed_at.utcoffset().total_seconds() == 0

    def test_claim_message_contains_claim_id(self) -> None:
        result = json.loads(
            file_compensation_claim('BK98765', 'AU123', 'Flight cancelled')
        )
        assert result['claim_id'] in result['message']

    @pytest.mark.parametrize('value', ['', ' ', 'unknown reason'])
    def test_claim_accepts_reason_values_without_changing_them(self, value: str) -> None:
        result = json.loads(file_compensation_claim('BK98765', 'AU123', value))
        assert result['reason'] == value

    def test_claim_id_is_unique(self) -> None:
        result1 = json.loads(
            file_compensation_claim('BK00001', 'AU123', 'reason A')
        )
        result2 = json.loads(
            file_compensation_claim('BK00002', 'AU123', 'reason B')
        )
        assert result1['claim_id'] != result2['claim_id']

    def test_includes_resolution_days(self) -> None:
        result = json.loads(
            file_compensation_claim('BK98765', 'AU123', 'Cancellation')
        )
        assert result['expected_resolution_days'] == 10
