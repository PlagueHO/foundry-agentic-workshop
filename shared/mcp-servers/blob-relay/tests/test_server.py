"""Unit tests for the Blob Relay MCP server."""

# The tests intentionally exercise private helpers and import the module from
# the component's configured src path.
# pyright: reportMissingImports=false, reportPrivateUsage=false
# pylint: disable=import-error, protected-access

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest

import server


def _jwt(payload: dict[str, Any]) -> str:
    encoded_payload = base64.urlsafe_b64encode(
        json.dumps(payload).encode('utf-8')
    ).rstrip(b'=').decode('ascii')
    return f'header.{encoded_payload}.signature'


@pytest.fixture(autouse=True)
def bearer_token() -> None:
    server._incoming_bearer.set('test-token')


@pytest.fixture(autouse=True)
def configure_storage_target() -> None:
    with patch.object(server, '_STORAGE_ACCOUNT', 'storage-account'), patch.object(
        server, '_CONTAINER', 'container'
    ):
        yield


@pytest.mark.parametrize(
    ('blob_name', 'expected'),
    [
        ('blob.txt', True),
        ('folder/blob.txt', True),
        ('a' * 1024, True),
        ('', False),
        ('/blob.txt', False),
        ('../blob.txt', False),
        ('folder/../blob.txt', False),
        ('a' * 1025, False),
        ('blob name.txt', False),
    ],
)
def test_valid_blob_name(blob_name: str, expected: bool) -> None:
    assert server._valid_blob_name(blob_name) is expected


def test_blob_url_uses_pinned_storage_target() -> None:
    assert (
        server._blob_url('folder/blob.txt')
        == 'https://storage-account.blob.core.windows.net/container/folder/blob.txt'
    )


def test_decode_claims_returns_only_identity_claims() -> None:
    token = _jwt(
        {
            'aud': 'https://storage.azure.com',
            'iss': 'issuer',
            'appid': 'application-id',
            'azp': 'authorized-party',
            'oid': 'object-id',
            'roles': ['Storage Blob Data Reader'],
            'secret': 'must-not-be-returned',
        }
    )

    assert server._decode_claims(token) == {
        'aud': 'https://storage.azure.com',
        'iss': 'issuer',
        'appid': 'application-id',
        'azp': 'authorized-party',
        'oid': 'object-id',
        'roles': ['Storage Blob Data Reader'],
    }


@pytest.mark.parametrize('token', ['not-a-jwt', 'one.two.%%%', 'one.@@@@.three'])
def test_decode_claims_rejects_malformed_tokens(token: str) -> None:
    assert server._decode_claims(token) == {'error': 'token is not a decodable JWT'}


def test_whoami_without_bearer_token() -> None:
    server._incoming_bearer.set(None)

    assert server.whoami() == {
        'error': 'No bearer token was supplied on the request.'
    }


def test_whoami_reports_pinned_target_and_claims() -> None:
    token = _jwt({'aud': 'storage', 'oid': 'agent-id'})
    server._incoming_bearer.set(token)

    result = server.whoami()

    assert result == {
        'storage_account': 'storage-account',
        'container': 'container',
        'token_claims': {
            'aud': 'storage',
            'iss': None,
            'appid': None,
            'azp': None,
            'oid': 'agent-id',
            'roles': None,
        },
    }


@pytest.mark.parametrize('operation', ['read_blob', 'write_blob'])
def test_blob_operations_require_bearer_token(
    operation: str,
) -> None:
    server._incoming_bearer.set(None)
    http_method_name = 'get' if operation == 'read_blob' else 'put'

    with patch.object(
        server.httpx, http_method_name, side_effect=AssertionError('HTTP call made')
    ):
        result = (
            server.read_blob('blob.txt')
            if operation == 'read_blob'
            else server.write_blob('blob.txt', 'content')
        )

    assert result == {'error': 'No bearer token was supplied on the request.'}


def test_read_blob_rejects_invalid_name_without_http_call() -> None:
    with patch.object(server.httpx, 'get', side_effect=AssertionError('HTTP call made')):
        result = server.read_blob('../secrets.txt')

    assert result == {"error": "Invalid blob name: '../secrets.txt'"}


def test_read_blob_returns_content_and_forwards_request() -> None:
    response = Mock(status_code=200, text='hello')
    with patch.object(server.httpx, 'get', return_value=response) as get:
        result = server.read_blob('folder/blob.txt')

    assert result == {'blob_name': 'folder/blob.txt', 'content': 'hello'}
    get.assert_called_once_with(
        'https://storage-account.blob.core.windows.net/container/folder/blob.txt',
        headers={
            'Authorization': 'Bearer test-token',
            'x-ms-version': '2021-08-06',
        },
        timeout=30.0,
    )


def test_read_blob_returns_truncated_storage_error() -> None:
    response = Mock(status_code=404, text='x' * 600)
    with patch.object(server.httpx, 'get', return_value=response):
        result = server.read_blob('missing.txt')

    assert result == {
        'error': 'Storage returned 404',
        'status_code': 404,
        'detail': 'x' * 500,
    }


def test_read_blob_returns_http_error() -> None:
    with patch.object(
        server.httpx, 'get', side_effect=httpx.ConnectTimeout('timed out')
    ):
        result = server.read_blob('blob.txt')

    assert result == {'error': 'Request to Storage failed: timed out'}


@pytest.mark.parametrize('status_code', [200, 201])
def test_write_blob_accepts_success_statuses(
    status_code: int,
) -> None:
    response = Mock(status_code=status_code, text='')
    with patch.object(server.httpx, 'put', return_value=response) as put:
        result = server.write_blob('blob.txt', 'héllo')

    assert result == {
        'blob_name': 'blob.txt',
        'status': 'written',
        'status_code': status_code,
    }
    put.assert_called_once_with(
        'https://storage-account.blob.core.windows.net/container/blob.txt',
        headers={
            'Authorization': 'Bearer test-token',
            'x-ms-version': '2021-08-06',
            'x-ms-blob-type': 'BlockBlob',
            'Content-Type': 'text/plain; charset=utf-8',
        },
        content='héllo'.encode('utf-8'),
        timeout=30.0,
    )


def test_write_blob_returns_storage_error() -> None:
    response = Mock(status_code=403, text='forbidden')
    with patch.object(server.httpx, 'put', return_value=response):
        result = server.write_blob('blob.txt', 'content')

    assert result == {
        'error': 'Storage returned 403',
        'status_code': 403,
        'detail': 'forbidden',
    }


def test_write_blob_returns_http_error() -> None:
    with patch.object(
        server.httpx, 'put', side_effect=httpx.ReadTimeout('timed out')
    ):
        result = server.write_blob('blob.txt', 'content')

    assert result == {'error': 'Request to Storage failed: timed out'}


def test_bearer_capture_middleware_captures_and_restores_context() -> None:
    observed: list[str | None] = []

    async def app(_scope: dict[str, Any], _receive: Any, _send: Any) -> None:
        observed.append(server._incoming_bearer.get())

    middleware = server._BearerCaptureMiddleware(app)
    asyncio.run(
        middleware(
            {'type': 'http', 'headers': [(b'authorization', b'BeArEr captured')]},
            Mock(),
            Mock(),
        )
    )

    assert observed == ['captured']
    assert server._incoming_bearer.get() == 'test-token'


@pytest.mark.parametrize(
    'headers',
    [
        [],
        [(b'authorization', b'Basic credentials')],
        [(b'authorization', b'Bearer')],
    ],
)
def test_bearer_capture_middleware_handles_missing_or_invalid_header(
    headers: list[tuple[bytes, bytes]],
) -> None:
    observed: list[str | None] = []

    async def app(_scope: dict[str, Any], _receive: Any, _send: Any) -> None:
        observed.append(server._incoming_bearer.get())

    middleware = server._BearerCaptureMiddleware(app)
    asyncio.run(middleware({'type': 'http', 'headers': headers}, Mock(), Mock()))

    assert observed == [None]
    assert server._incoming_bearer.get() == 'test-token'


def test_bearer_capture_middleware_passes_non_http_scope_unchanged() -> None:
    observed: list[dict[str, Any]] = []

    async def app(scope: dict[str, Any], _receive: Any, _send: Any) -> None:
        observed.append(scope)

    scope = {'type': 'lifespan'}
    middleware = server._BearerCaptureMiddleware(app)
    asyncio.run(middleware(scope, Mock(), Mock()))

    assert observed == [scope]
    assert server._incoming_bearer.get() == 'test-token'


def test_main_requires_storage_account() -> None:
    with patch.object(server, '_STORAGE_ACCOUNT', ''), pytest.raises(
        SystemExit, match='BLOB_RELAY_STORAGE_ACCOUNT is not set.'
    ):
        server.main()
