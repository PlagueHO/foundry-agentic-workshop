"""
Tests for the flight-ops MCP server tools.

Run with:
    pytest shared/mcp-servers/flight-ops/src/test_flight_ops.py -v
"""

import json

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

    def test_case_insensitive_lookup(self) -> None:
        result = json.loads(get_flight_status('au123'))
        assert result['status'] == 'CANCELLED'

    def test_unknown_flight_returns_error(self) -> None:
        result = json.loads(get_flight_status('ZZ999'))
        assert 'error' in result
        assert 'available_flights' in result


class TestGetRebookingOptions:
    def test_returns_options_for_valid_route(self) -> None:
        result = json.loads(get_rebooking_options('BK98765', 'AKL', 'SYD'))
        assert result['options_count'] > 0
        assert result['route'] == 'AKL→SYD'

    def test_case_insensitive_route(self) -> None:
        result = json.loads(get_rebooking_options('BK98765', 'akl', 'syd'))
        assert result['options_count'] > 0

    def test_no_options_for_unknown_route(self) -> None:
        result = json.loads(get_rebooking_options('BK00000', 'AKL', 'LHR'))
        assert result['options_count'] == 0


class TestFileCompensationClaim:
    def test_returns_claim_id(self) -> None:
        result = json.loads(
            file_compensation_claim('BK98765', 'AU123', 'Flight cancelled')
        )
        assert result['status'] == 'SUBMITTED'
        assert result['claim_id'].startswith('CLM-')

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
