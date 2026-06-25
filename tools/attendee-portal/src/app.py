"""Attendee Onboarding Portal.

Serves per-attendee workshop environment configuration from a JSON index stored in
Azure Blob Storage. Authentication is handled by Azure Container Apps built-in EasyAuth
(Entra ID single-tenant). EasyAuth sets ``X-MS-CLIENT-PRINCIPAL-NAME`` from the token's
``name`` claim (display name). The portal extracts the actual UPN from
``X-MS-CLIENT-PRINCIPAL`` claims (``preferred_username`` / ``emailaddress``) so the
correct attendee record can be found in the index.

All user-derived values embedded in the HTML response are escaped with ``html.escape()``
to prevent cross-site scripting. The ``/healthz`` endpoint responds without authentication
and is used as the Container Apps liveness probe.

The UPN-to-key derivation in ``_upn_key()`` must stay in sync with the equivalent
function in ``scripts/generate-attendee-onboarding.py``.
"""
from __future__ import annotations

import base64
import html
import json
import logging
import os
import time

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', '')
_CONTAINER_NAME = os.environ.get('ATTENDEE_ONBOARDING_CONTAINER', 'attendee-onboarding')
_BLOB_NAME = 'index.json'

# When AZURE_CLIENT_ID is set, DefaultAzureCredential selects that specific
# user-assigned managed identity. Container Apps injects this env var automatically
# when a single user-assigned MI is attached (set via the Bicep module).
_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '') or None

# Cache the index in memory for this many seconds before re-downloading from blob storage.
# Short enough that re-running generate-attendee-onboarding.py is reflected quickly;
# long enough to avoid hammering storage when many attendees load the portal concurrently.
_INDEX_CACHE_TTL: int = int(os.environ.get('INDEX_CACHE_TTL', '60'))
_index_cache: dict[str, dict] = {}
_index_cache_ts: float = 0.0

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
_log = logging.getLogger(__name__)

app = FastAPI(title='Attendee Onboarding Portal', docs_url=None, redoc_url=None)

_SKIP_LINK_CSS = (
    '.sr-only:not(:focus):not(:active){'
    'clip:rect(0 0 0 0);clip-path:inset(50%);'
    'height:1px;overflow:hidden;position:absolute;white-space:nowrap;width:1px;}'
)

_PAGE_CSS = (
    '*,*::before,*::after{box-sizing:border-box;}'
    ':focus-visible{outline:3px solid #0078d4;outline-offset:2px;}'
    'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;'
    'background:#f4f6f9;color:#1a1a2e;margin:0;padding:0;line-height:1.6;}'
    '.page-wrap{max-width:900px;margin:0 auto;padding:1.25rem 1rem;}'
    'nav.nav-bar{display:flex;justify-content:space-between;align-items:center;'
    'background:#003087;color:#fff;padding:.7rem 1.5rem;'
    'border-radius:8px;margin-bottom:1rem;}'
    '.nav-brand{font-size:.92rem;font-weight:600;color:#fff;}'
    '.signout-btn{background:transparent;color:#fff;'
    'border:1px solid rgba(255,255,255,.55);border-radius:4px;'
    'padding:.3rem .85rem;cursor:pointer;font-size:.82rem;'
    'text-decoration:none;white-space:nowrap;}'
    '.signout-btn:hover,.signout-btn:focus{background:rgba(255,255,255,.18);}'
    'img.banner{width:100%;max-height:150px;object-fit:cover;'
    'border-radius:8px;margin-bottom:1rem;display:block;}'
    'header{margin-bottom:1.5rem;}'
    'h1{font-size:1.6rem;margin:0 0 .3rem;color:#003087;}'
    '.subtitle{color:#555;font-size:.95rem;}'
    '.role-badge{display:inline-block;background:#e3f2fd;color:#003087;'
    'border-radius:12px;padding:.15rem .65rem;font-size:.78rem;'
    'margin-left:.5rem;vertical-align:middle;font-weight:600;}'
    'section{background:#fff;border-radius:8px;padding:1.5rem;margin-bottom:1.25rem;'
    'box-shadow:0 1px 4px rgba(0,0,0,.08);}'
    'h2{font-size:1.05rem;margin:0 0 .75rem;color:#003087;}'
    'p{margin:.5rem 0;}'
    '.note{color:#555;font-size:.88rem;margin-bottom:.75rem;}'
    'code{background:#f0f0f0;border-radius:3px;padding:.1rem .3rem;font-size:.9em;}'
    '.code-wrap{position:relative;}'
    '.btn-row{display:flex;gap:.5rem;margin-top:.65rem;flex-wrap:wrap;align-items:center;}'
    'pre{background:#1e1e2e;color:#cdd6f4;border-radius:6px;padding:1rem;'
    'overflow-x:auto;font-size:.87rem;margin:0;white-space:pre-wrap;word-break:break-all;}'
    '.copy-btn{position:absolute;top:.5rem;right:.5rem;background:#0078d4;color:#fff;'
    'border:none;border-radius:4px;padding:.3rem .75rem;cursor:pointer;font-size:.82rem;}'
    '.copy-btn:hover{background:#005a9e;}'
    'a.download-btn{display:inline-block;background:#107c10;color:#fff;'
    'border-radius:4px;padding:.35rem 1rem;font-size:.85rem;'
    'text-decoration:none;line-height:1.4;}'
    'a.download-btn:hover{background:#0d6b0d;}'
    '.alert{background:#fff8e1;border-left:4px solid #f9a825;border-radius:4px;'
    'padding:1rem 1.25rem;color:#5f4400;}'
    '.alert-error{background:#fdecea;border-left:4px solid #d32f2f;border-radius:4px;'
    'padding:1rem 1.25rem;color:#611212;}'
    '.unresolved-warn{background:#fff3e0;border-left:4px solid #f57c00;'
    'border-radius:4px;padding:.75rem 1rem;color:#663c00;'
    'font-size:.9rem;margin-bottom:1rem;}'
    '.resources-section{background:#fff;border-radius:8px;'
    'padding:1.1rem 1.5rem;margin-bottom:1.25rem;'
    'box-shadow:0 1px 4px rgba(0,0,0,.08);}'
    '.resources-list{display:flex;gap:.5rem 1.5rem;flex-wrap:wrap;'
    'padding:0;margin:.3rem 0 0;list-style:none;}'
    '.resources-list a{color:#0078d4;font-size:.9rem;}'
    '.resources-list a:hover{text-decoration:underline;}'
    'footer{text-align:center;color:#777;font-size:.8rem;'
    'margin-top:1.5rem;padding-bottom:1rem;}'
    'footer a{color:#0078d4;}'
)

_COPY_JS = (
    'function copyText(btnId,codeId){'
    'navigator.clipboard.writeText(document.getElementById(codeId).innerText).then(function(){'
    'var b=document.getElementById(btnId);var orig=b.textContent;'
    'b.textContent="Copied!";'
    'setTimeout(function(){b.textContent=orig;},2000);});}'
)


_BANNER_URL = (
    'https://raw.githubusercontent.com/PlagueHO/foundry-agentic-workshop'
    '/main/docs/public/banners/microsoft-foundry-agentic-workshop.png'
)


def _render_page(head_suffix: str, h1_suffix: str, subtitle: str, body: str, upn: str = '') -> str:
    """Render a complete HTML page with workshop branding."""
    signout_html = (
        f'<a href="/.auth/logout" class="signout-btn"'
        f' aria-label="Sign out {html.escape(upn)}">Sign out</a>'
        if upn else ''
    )
    nav = (
        '<nav class="nav-bar" aria-label="Portal navigation">'
        '<span class="nav-brand">'
        'Microsoft Foundry Agentic Workshop \u2014 Onboarding Portal'
        '</span>'
        f'{signout_html}'
        '</nav>'
    )
    banner = (
        f'<img src="{_BANNER_URL}"'
        ' alt="Microsoft Foundry Agentic Workshop banner"'
        ' class="banner" />'
    )
    resources = (
        '<section class="resources-section" id="workshop-resources">'
        '<h2>Workshop Resources</h2>'
        '<ul class="resources-list">'
        '<li><a href="https://github.com/PlagueHO/foundry-agentic-workshop"'
        ' target="_blank" rel="noopener noreferrer">GitHub Repository</a></li>'
        '<li><a href="https://github.com/PlagueHO/foundry-agentic-workshop'
        '/blob/main/docs/quickstart-attendee.md"'
        ' target="_blank" rel="noopener noreferrer">Attendee Quickstart</a></li>'
        '<li><a href="https://github.com/PlagueHO/foundry-agentic-workshop'
        '/tree/main/labs/introduction-foundry-agent-service"'
        ' target="_blank" rel="noopener noreferrer">Lab Modules</a></li>'
        '<li><a href="https://learn.microsoft.com/azure/ai-foundry/"'
        ' target="_blank" rel="noopener noreferrer">Microsoft Foundry Docs</a></li>'
        '<li><a href="https://ai.azure.com"'
        ' target="_blank" rel="noopener noreferrer">Foundry Portal (ai.azure.com)</a></li>'
        '</ul>'
        '</section>'
    )
    return (
        '<!DOCTYPE html>'
        '<html lang="en">'
        '<head>'
        '<meta charset="UTF-8" />'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
        f'<title>Microsoft Foundry Agentic Workshop \u2014 Onboarding'
        f'{html.escape(head_suffix)}</title>'
        f'<style>{_SKIP_LINK_CSS}{_PAGE_CSS}</style>'
        '</head>'
        '<body>'
        '<a href="#main-content" class="sr-only">Skip to main content</a>'
        f'{nav}'
        '<div class="page-wrap">'
        '<main id="main-content">'
        f'{banner}'
        '<header>'
        f'<h1>Workshop Onboarding{html.escape(h1_suffix)}</h1>'
        f'<p class="subtitle">{subtitle}</p>'
        '</header>'
        f'{body}'
        f'{resources}'
        '</main>'
        '</div>'
        '<footer>'
        '<p>Microsoft Foundry Agentic Workshop \u2014 Attendee Onboarding Portal \u2014 '
        '<a href="https://github.com/PlagueHO/foundry-agentic-workshop"'
        ' target="_blank" rel="noopener noreferrer">GitHub</a></p>'
        '</footer>'
        f'<script>{_COPY_JS}</script>'
        '</body>'
        '</html>'
    )


def _extract_upn(request: Request) -> str:
    """Extract the authenticated user's UPN from EasyAuth headers.

    Container Apps EasyAuth sets ``X-MS-CLIENT-PRINCIPAL-NAME`` from the
    token's ``name`` claim, which is the display name (e.g. "Azure Lab Attendee 1"),
    NOT the UPN.  The ``X-MS-CLIENT-PRINCIPAL`` header contains the full claims
    blob (base64-encoded JSON), where ``preferred_username`` and the WS-Federation
    ``emailaddress`` claim reliably hold the UPN/email used to key the index.
    """
    principal_b64 = request.headers.get('X-MS-CLIENT-PRINCIPAL', '')
    if principal_b64:
        try:
            principal = json.loads(base64.b64decode(principal_b64 + '=='))
            claims: dict[str, str] = {
                c.get('typ', ''): c.get('val', '')
                for c in principal.get('claims', [])
                if c.get('val')
            }
            upn = (
                claims.get('preferred_username')
                or claims.get(
                    'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'
                )
                or claims.get('email')
                or ''
            )
            if upn:
                return upn.strip()
        except Exception:  # pylint: disable=broad-except
            pass
    # Fallback: may be display name rather than UPN in some EasyAuth configurations.
    return request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME', '').strip()


def _copy_btn(btn_id: str, code_id: str, label: str) -> str:
    """Render an accessible copy-to-clipboard button."""
    safe_label = html.escape(f'Copy {label} to clipboard')
    return (
        f'<button class="copy-btn" id="{btn_id}" type="button" '
        f'onclick="copyText(\'{btn_id}\',\'{code_id}\')" '
        f'aria-label="{safe_label}">Copy</button>'
    )


def _code_section(
    section_id: str,
    heading: str,
    code_id: str,
    btn_id: str,
    content: str,
    note: str = '',
) -> str:
    """Render an accessible code section with a copy button."""
    note_html = f'<p class="note">{html.escape(note)}</p>' if note else ''
    return (
        f'<section id="{section_id}">'
        f'<h2>{html.escape(heading)}</h2>'
        f'{note_html}'
        f'<div class="code-wrap">'
        f'{_copy_btn(btn_id, code_id, heading.lower())}'
        f'<pre id="{code_id}" tabindex="0">{html.escape(content)}</pre>'
        f'</div>'
        f'</section>'
    )


def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential(managed_identity_client_id=_CLIENT_ID)


def _is_permission_error(exc: Exception) -> bool:
    """Return True if the exception indicates an authentication or authorisation failure."""
    if isinstance(exc, ClientAuthenticationError):
        return True
    if isinstance(exc, HttpResponseError) and getattr(exc, 'status_code', None) in (401, 403):
        return True
    return False


def _load_index() -> tuple[dict[str, dict], Exception | None]:
    """Return ``(index, error)`` using an in-process TTL cache.

    The index is re-downloaded from blob storage at most once per
    ``_INDEX_CACHE_TTL`` seconds so that concurrent requests do not each
    issue a separate blob read, while still picking up updates written by
    ``scripts/generate-attendee-onboarding.py`` within a reasonable window.

    On success ``error`` is ``None``.  On failure ``error`` is the caught
    exception; the stale cache (possibly ``{}``) is returned alongside it so
    callers can still serve data when available.
    """
    global _index_cache, _index_cache_ts  # noqa: PLW0603
    now = time.monotonic()
    if _index_cache and (now - _index_cache_ts) < _INDEX_CACHE_TTL:
        return _index_cache, None
    if not _STORAGE_ACCOUNT_NAME:
        _log.warning('AZURE_STORAGE_ACCOUNT_NAME not set; portal will return no data.')
        return {}, None
    try:
        client = BlobServiceClient(
            account_url=f'https://{_STORAGE_ACCOUNT_NAME}.blob.core.windows.net',
            credential=_credential(),
        )
        blob = client.get_blob_client(container=_CONTAINER_NAME, blob=_BLOB_NAME)
        _index_cache = json.loads(blob.download_blob().readall())
        _index_cache_ts = now
        return _index_cache, None
    except Exception as exc:  # pylint: disable=broad-except
        _log.error('Failed to load onboarding index: %s', exc)
        return _index_cache, exc  # stale cache (possibly {}) alongside the error


def _upn_key(upn: str) -> str:
    """Derive the index lookup key from a UPN.

    Must match ``_upn_key()`` in ``scripts/generate-attendee-onboarding.py``
    so the portal can find the record uploaded by the onboarding script.
    """
    return upn.split('@')[0].lower().replace('.', '-').replace('_', '-')


@app.get('/healthz', include_in_schema=False)
async def healthz() -> Response:
    """Liveness probe - no authentication required."""
    return Response(content='ok', media_type='text/plain')


@app.get('/', response_class=HTMLResponse)
async def portal(request: Request) -> HTMLResponse:
    """Serve the attendee personal onboarding configuration page."""
    upn = _extract_upn(request)

    if not upn:
        # EasyAuth redirects unauthenticated requests before reaching here.
        # This branch handles misconfigured environments or direct internal access.
        body = (
            '<div class="alert" role="alert">'
            '<strong>Not authenticated.</strong> '
            'Please sign in with your lab Microsoft account.'
            '</div>'
        )
        return HTMLResponse(
            content=_render_page('', '', 'Authentication required.', body),
            status_code=401,
        )

    key = _upn_key(upn)
    _log.info('Portal request: upn=%s key=%s', upn, key)
    index, load_error = _load_index()
    record = index.get(key)

    if record is None:
        upn_safe = html.escape(upn)
        if load_error is not None and _is_permission_error(load_error):
            body = (
                '<div class="alert-error" role="alert">'
                '<strong>Configuration unavailable \u2014 permissions error.</strong> '
                'The portal cannot read the onboarding configuration from storage '
                'due to an access or permissions issue. '
                'Contact your organiser for assistance.'
                '</div>'
            )
        elif load_error is not None:
            body = (
                '<div class="alert-error" role="alert">'
                '<strong>Configuration temporarily unavailable.</strong> '
                'The portal encountered an error reading the onboarding configuration. '
                'Please try again in a few moments or contact your organiser.'
                '</div>'
            )
        else:
            body = (
                '<div class="alert" role="alert">'
                f'<strong>No configuration found</strong> for '
                f'<strong>{upn_safe}</strong>. '
                'Contact your facilitator or organiser for assistance.'
                '</div>'
            )
        return HTMLResponse(
            content=_render_page('', '', f'Signed in as {upn_safe}.', body, upn=upn),
        )

    env_block_raw = record.get('env', record.get('envBlock', {}))
    # env is a dict[str, str] in index.json; fall back to string for old blobs.
    if isinstance(env_block_raw, dict):
        env_block_str = '\n'.join(f'{k}={v}' for k, v in env_block_raw.items())
        subscription_id = env_block_raw.get('AZURE_SUBSCRIPTION_ID', '')
    else:
        env_block_str = str(env_block_raw)
        subscription_id = ''
        for line in env_block_str.splitlines():
            if line.startswith('AZURE_SUBSCRIPTION_ID='):
                subscription_id = line.split('=', 1)[1].strip()
                break
    role_raw: str = record.get('role', '')
    role_display = html.escape(record.get('roleDisplayName', role_raw))
    role_badge_html = (
        f'<span class="role-badge" aria-label="Assigned Foundry role: {role_display}">'
        f'{role_display}</span>'
    ) if role_display else ''
    unresolved_html = (
        '<div class="unresolved-warn" role="alert">'
        '<strong>Note:</strong> Your account could not be resolved during provisioning. '
        'Azure RBAC role assignments may be incomplete. '
        'Contact your organiser for assistance.'
        '</div>'
    ) if not record.get('resolved', True) else ''

    signin_block = (
        f'az login\naz account set --subscription {subscription_id}'
        if subscription_id
        else 'az login'
    )
    display_key = html.escape(_upn_key(upn))
    subtitle = f'Signed in as {html.escape(upn)}.{role_badge_html}'

    env_section = (
        '<section id="env-section">'
        '<h2>Your environment variables</h2>'
        f'{unresolved_html}'
        '<p class="note">Copy <code>shared/.env.example</code> to <code>.env</code> '
        'in the repository root, then paste these values.</p>'
        '<div class="code-wrap">'
        f'{_copy_btn("btn-env", "code-env", "environment variables")}'
        f'<pre id="code-env" tabindex="0">{html.escape(env_block_str)}</pre>'
        '</div>'
        '<div class="btn-row">'
        '<a href="/download-env" class="download-btn" '
        'aria-label="Download .env configuration file">&#8615; Download .env</a>'
        '</div>'
        '</section>'
    )

    body = (
        env_section
        + _code_section(
            section_id='signin-section',
            heading='Sign in to Azure',
            code_id='code-signin',
            btn_id='btn-signin',
            content=signin_block,
        )
        + _code_section(
            section_id='validate-section',
            heading='Validate setup',
            code_id='code-validate',
            btn_id='btn-validate',
            content='python scripts/health-check.py',
        )
        + (
            '<section id="next-steps">'
            '<h2>Next steps</h2>'
            '<p>Follow the '
            '<a href="https://github.com/PlagueHO/foundry-agentic-workshop'
            '/blob/main/docs/quickstart-attendee.md"'
            ' target="_blank" rel="noopener noreferrer">Attendee Quickstart</a> '
            'to complete setup and begin the labs.</p>'
            '</section>'
        )
    )
    return HTMLResponse(
        content=_render_page(
            f' \u2014 {display_key}',
            f': {display_key}',
            subtitle,
            body,
            upn=upn,
        ),
    )


@app.get('/download-env', include_in_schema=False)
async def download_env(request: Request) -> Response:
    """Download the attendee .env file as an attachment."""
    upn = _extract_upn(request)
    if not upn:
        return Response(status_code=401, content='Not authenticated.')
    index, load_error = _load_index()
    record = index.get(_upn_key(upn))
    if record is None:
        if load_error is not None and _is_permission_error(load_error):
            return Response(
                status_code=503,
                content='Configuration unavailable due to a permissions error.',
                media_type='text/plain',
            )
        if load_error is not None:
            return Response(
                status_code=503,
                content='Configuration temporarily unavailable.',
                media_type='text/plain',
            )
        return Response(
            status_code=404,
            content='# No configuration found for this account.',
            media_type='text/plain',
        )
    env_block_raw = record.get('env', record.get('envBlock', {}))
    if isinstance(env_block_raw, dict):
        env_block_str = '\n'.join(f'{k}={v}' for k, v in env_block_raw.items())
    else:
        env_block_str = str(env_block_raw)
    return Response(
        content=env_block_str,
        media_type='text/plain; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=".env"'},
    )


if __name__ == '__main__':
    import uvicorn  # noqa: PLC0415
    _port = int(os.environ.get('PORT', '8000'))
    uvicorn.run(app, host='0.0.0.0', port=_port, log_level='info')
