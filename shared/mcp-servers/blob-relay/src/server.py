"""Blob Relay MCP server (agent-identity passthrough).

This server demonstrates the Foundry **unattended (application-only) agent
identity** flow. Foundry Agent Service authenticates the calling agent's Entra
*instance identity*, exchanges it for an access token scoped to the Azure
Storage audience (``https://storage.azure.com``), and sends that token to this
server in the ``Authorization`` header. This server is a thin **passthrough**:
it forwards the caller-supplied bearer token straight to the Azure Blob REST
API. It never acquires a token of its own, so the agent identity - not this
server - is the security principal at Storage. Access is therefore governed
entirely by the RBAC roles assigned to the agent's instance identity.

Security guardrails (the relay is otherwise a classic confused-deputy):
  * A bearer token must be present on the request; requests without one are
    rejected before any Storage call is attempted.
  * The target storage account and container are pinned by environment
    variables - the caller cannot redirect the relay at an arbitrary resource.
  * Blob names are validated to block path traversal and injection.

Usage:
    python shared/mcp-servers/blob-relay/src/server.py

The server listens on http://0.0.0.0:<BLOB_RELAY_MCP_SERVER_PORT>/mcp (default 8080).
"""

from __future__ import annotations

import base64
import binascii
import json
import os
import re
from contextvars import ContextVar
from datetime import datetime, timezone

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send

# The bearer token supplied by Agent Service on the current request. Populated by
# the ASGI middleware below and read by the tools within the same request scope.
_incoming_bearer: ContextVar[str | None] = ContextVar('_incoming_bearer', default=None)

_PORT = int(os.environ.get('BLOB_RELAY_MCP_SERVER_PORT', '8080'))
# Pinned downstream target - the caller cannot change these (confused-deputy guard).
_STORAGE_ACCOUNT = os.environ.get('BLOB_RELAY_STORAGE_ACCOUNT', '')
_CONTAINER = os.environ.get('BLOB_RELAY_CONTAINER', 'agent-identity-demo')
# Azure Blob REST API version.
_BLOB_API_VERSION = '2021-08-06'
# Blob names: letters, digits, dot, dash, underscore, and forward slash only. No
# leading slash and no parent-directory segments (path-traversal guard).
_BLOB_NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._\-/]{0,1023}$')

mcp = FastMCP('Blob Relay', host='0.0.0.0', port=_PORT)


def _log(message: str) -> None:
    """Print a timestamped diagnostic line (never logs token material)."""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
    print(f'[{timestamp}] {message}', flush=True)


def _require_bearer() -> str | None:
    """Return the incoming bearer token, or None when absent."""
    token = _incoming_bearer.get()
    if not token:
        _log('rejected: no bearer token on request')
    return token


def _valid_blob_name(blob_name: str) -> bool:
    """Return True when the blob name is safe (no traversal, no injection)."""
    return bool(_BLOB_NAME_RE.match(blob_name)) and '..' not in blob_name


def _blob_url(blob_name: str) -> str:
    """Build the pinned Blob REST URL for the given blob name."""
    return (
        f'https://{_STORAGE_ACCOUNT}.blob.core.windows.net/'
        f'{_CONTAINER}/{blob_name}'
    )


def _decode_claims(token: str) -> dict:
    """Decode a JWT payload without verifying the signature (diagnostic only)."""
    try:
        payload_segment = token.split('.')[1]
        padded = payload_segment + '=' * (-len(payload_segment) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded))
    except (IndexError, ValueError, binascii.Error):
        return {'error': 'token is not a decodable JWT'}
    # Return only non-sensitive identity claims - never the raw token.
    return {key: claims.get(key) for key in ('aud', 'iss', 'appid', 'azp', 'oid', 'roles')}


@mcp.tool()
def whoami() -> dict:
    """Report the identity and audience of the token Agent Service supplied.

    Decodes the incoming bearer token and returns its ``aud`` (audience),
    ``oid``/``appid`` (the calling agent identity), and issuer. Use this to
    confirm the agent-identity token exchange reached this server with the
    expected Storage audience. Returns an error dict when no token is present.
    """
    token = _require_bearer()
    if not token:
        return {'error': 'No bearer token was supplied on the request.'}
    claims = _decode_claims(token)
    _log(f'whoami: aud={claims.get("aud")!r} oid={claims.get("oid")!r} appid={claims.get("appid")!r}')
    return {'storage_account': _STORAGE_ACCOUNT, 'container': _CONTAINER, 'token_claims': claims}


@mcp.tool()
def read_blob(blob_name: str) -> dict:
    """Read a blob from the pinned container using the agent identity's token.

    Forwards the caller-supplied Storage-scoped bearer token to the Azure Blob
    REST API. Succeeds only when the agent identity has a role such as Storage
    Blob Data Reader/Contributor on the storage account. Returns the blob text
    on success, or an error dict describing the failure (for example a 403 when
    the agent identity lacks the required role).
    """
    token = _require_bearer()
    if not token:
        return {'error': 'No bearer token was supplied on the request.'}
    if not _valid_blob_name(blob_name):
        return {'error': f'Invalid blob name: {blob_name!r}'}
    _log(f'read_blob: {_CONTAINER}/{blob_name}')
    try:
        response = httpx.get(
            _blob_url(blob_name),
            headers={'Authorization': f'Bearer {token}', 'x-ms-version': _BLOB_API_VERSION},
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        return {'error': f'Request to Storage failed: {exc}'}
    if response.status_code == 200:
        return {'blob_name': blob_name, 'content': response.text}
    return {
        'error': f'Storage returned {response.status_code}',
        'status_code': response.status_code,
        'detail': response.text[:500],
    }


@mcp.tool()
def write_blob(blob_name: str, content: str) -> dict:
    """Write a blob to the pinned container using the agent identity's token.

    Forwards the caller-supplied Storage-scoped bearer token to the Azure Blob
    REST API to create or overwrite a block blob. Succeeds only when the agent
    identity has Storage Blob Data Contributor (or higher) on the storage
    account. Returns a status dict, or an error dict (for example a 403 when the
    agent identity lacks the required role).
    """
    token = _require_bearer()
    if not token:
        return {'error': 'No bearer token was supplied on the request.'}
    if not _valid_blob_name(blob_name):
        return {'error': f'Invalid blob name: {blob_name!r}'}
    _log(f'write_blob: {_CONTAINER}/{blob_name} ({len(content)} chars)')
    try:
        response = httpx.put(
            _blob_url(blob_name),
            headers={
                'Authorization': f'Bearer {token}',
                'x-ms-version': _BLOB_API_VERSION,
                'x-ms-blob-type': 'BlockBlob',
                'Content-Type': 'text/plain; charset=utf-8',
            },
            content=content.encode('utf-8'),
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        return {'error': f'Request to Storage failed: {exc}'}
    if response.status_code in (200, 201):
        return {'blob_name': blob_name, 'status': 'written', 'status_code': response.status_code}
    return {
        'error': f'Storage returned {response.status_code}',
        'status_code': response.status_code,
        'detail': response.text[:500],
    }


class _BearerCaptureMiddleware:
    """ASGI middleware that captures the request's Authorization bearer token.

    The token is stored in a context variable so the tool handlers can forward
    it to Storage within the same request scope. The token is never logged.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            token: str | None = None
            for name, value in scope.get('headers', []):
                if name == b'authorization':
                    raw = value.decode('latin-1')
                    if raw.lower().startswith('bearer '):
                        token = raw[7:].strip()
                    break
            reset_token = _incoming_bearer.set(token)
            try:
                await self._app(scope, receive, send)
            finally:
                _incoming_bearer.reset(reset_token)
            return
        await self._app(scope, receive, send)


def main() -> None:
    """Start the Blob Relay MCP server with bearer-capture middleware."""
    if not _STORAGE_ACCOUNT:
        raise SystemExit('BLOB_RELAY_STORAGE_ACCOUNT is not set.')
    print(f'Starting Blob Relay MCP server on http://0.0.0.0:{_PORT}/mcp')
    print(f'  Pinned target: {_STORAGE_ACCOUNT}/{_CONTAINER}')
    app = _BearerCaptureMiddleware(mcp.streamable_http_app())
    uvicorn.run(app, host='0.0.0.0', port=_PORT)


if __name__ == '__main__':
    main()
