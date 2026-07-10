"""Show available Azure AI / Foundry model quota across one or more regions.

Fetches quota usage from 'az cognitiveservices usage list' and displays a clean
summary table showing TPM limits, current usage, and remaining capacity for every
model quota entry in each requested region, grouped by provider (OpenAI, etc.).

Usage:
    python scripts/show-model-quota.py
    python scripts/show-model-quota.py --location eastus westus3 swedencentral
    python scripts/show-model-quota.py --location eastus --all
    python scripts/show-model-quota.py --filter gpt-4o
    python scripts/show-model-quota.py --available-only
    python scripts/show-model-quota.py --provider openai
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_LOCATIONS: list[str] = [
    'eastus',
    'eastus2',
    'westus',
    'westus3',
    'northcentralus',
    'southcentralus',
    'swedencentral',
    'westeurope',
    'uksouth',
    'australiaeast',
    'japaneast',
]

_AZ_CMD: str = shutil.which('az') or 'az'


# ---------------------------------------------------------------------------
# Colour support
# ---------------------------------------------------------------------------


@dataclass
class _Colors:
    reset: str = ''
    bold: str = ''
    dim: str = ''
    cyan: str = ''
    green: str = ''
    yellow: str = ''
    red: str = ''
    white: str = ''


def _make_colors(enabled: bool) -> _Colors:
    if not enabled:
        return _Colors()
    return _Colors(
        reset='\033[0m',
        bold='\033[1m',
        dim='\033[2m',
        cyan='\033[36m',
        green='\033[32m',
        yellow='\033[33m',
        red='\033[31m',
        white='\033[97m',
    )


def _colors_enabled() -> bool:
    """Return True when the terminal supports ANSI colour codes."""
    if os.environ.get('NO_COLOR'):
        return False
    return sys.stdout.isatty()


# Populated in main() once we know whether colour is available.
_C: _Colors = _Colors()

# Column widths for the output table.
_COL_MODEL = 40
_COL_SKU = 24
_COL_LIMIT = 10
_COL_USED = 10
_COL_AVAIL = 10
_COL_BAR = 20


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class QuotaEntry:
    location: str
    provider: str
    model: str
    sku: str
    limit: int
    used: int

    @property
    def available(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def used_pct(self) -> float:
        return (self.used / self.limit * 100) if self.limit > 0 else 0.0

    @property
    def avail_pct(self) -> float:
        return (self.available / self.limit * 100) if self.limit > 0 else 0.0


# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------


def _run_az(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_AZ_CMD, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _check_az_login() -> bool:
    """Return True if the user is logged in to az cli."""
    result = _run_az(['account', 'show', '-o', 'json'])
    return result.returncode == 0


def _fetch_usages(location: str) -> list[dict]:
    result = _run_az([
        'cognitiveservices', 'usage', 'list',
        '--location', location,
        '-o', 'json',
    ])
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout) or []
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_quota_name(raw_name: str) -> tuple[str, str, str] | None:
    """Parse a quota name into (provider, sku, model).

    Handles:
      '<Provider>.<SKU>.<Model>' -> (provider, sku, model)
      '<Provider>.<Name>'        -> (provider, '', name)
    Single-segment names (e.g. bare counters) are skipped.
    """
    parts = raw_name.split('.', 2)
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], '', parts[1]
    return None


def _parse_usages(location: str, raw: list[dict]) -> list[QuotaEntry]:
    entries: list[QuotaEntry] = []
    for item in raw:
        raw_name: str = (item.get('name') or {}).get('value', '')
        parsed = _parse_quota_name(raw_name)
        if parsed is None:
            continue
        provider, sku, model = parsed
        limit = int(item.get('limit') or 0)
        used = int(item.get('currentValue') or 0)
        entries.append(QuotaEntry(
            location=location,
            provider=provider,
            model=model,
            sku=sku,
            limit=limit,
            used=used,
        ))
    return sorted(entries, key=lambda e: (0 if e.provider == 'OpenAI' else 1, e.provider.lower(), e.model.lower(), e.sku.lower()))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _bar(used_pct: float, width: int = _COL_BAR) -> str:
    """Render a coloured usage bar like '[████░░░░░░░░░░░░░░░░]'."""
    filled = round(used_pct / 100 * width)
    filled = max(0, min(width, filled))
    if used_pct >= 80:
        colour = _C.red
    elif used_pct >= 50:
        colour = _C.yellow
    else:
        colour = _C.green
    bar_fill = colour + '█' * filled + _C.reset
    bar_empty = _C.dim + '░' * (width - filled) + _C.reset
    return '[' + bar_fill + bar_empty + ']'


def _fmt_tpm(value: int) -> str:
    """Format TPM value with K suffix for readability."""
    if value >= 1_000:
        return f'{value // 1_000}K'
    return str(value)


def _print_provider_section(provider: str, entries: list[QuotaEntry]) -> None:
    """Print one provider's rows within a location table."""
    inner_sep = _COL_MODEL + _COL_SKU + _COL_LIMIT + _COL_USED + _COL_AVAIL + _COL_BAR + 14
    provider_label = f' {provider} '
    dash_tail = '─' * max(0, inner_sep - len(provider_label) - 4)
    print(f'  │  {_C.bold}{_C.white}── {provider}{_C.reset}{_C.dim} {dash_tail}{_C.reset}')

    header = (
        f"  │    {_C.bold}{'Model':<{_COL_MODEL}}  {'SKU':<{_COL_SKU}}  "
        f"{'Limit':>{_COL_LIMIT}}  {'Used':>{_COL_USED}}  {'Available':>{_COL_AVAIL}}  "
        f"{'Usage':^{_COL_BAR}}{_C.reset}"
    )
    divider = (
        f"  │    {_C.dim}{'─' * _COL_MODEL}  {'─' * _COL_SKU}  "
        f"{'─' * _COL_LIMIT}  {'─' * _COL_USED}  {'─' * _COL_AVAIL}  "
        f"{'─' * _COL_BAR}{_C.reset}"
    )
    print(header)
    print(divider)

    for e in entries:
        exhausted = e.available == 0 and e.limit > 0
        if exhausted:
            avail_marker = f' {_C.red}!{_C.reset}'
            avail_str = f'{_C.red}{_fmt_tpm(e.available):>{_COL_AVAIL}}{_C.reset}'
        elif e.used > 0:
            avail_marker = '  '
            avail_str = f'{_C.yellow}{_fmt_tpm(e.available):>{_COL_AVAIL}}{_C.reset}'
        else:
            avail_marker = '  '
            avail_str = f'{_C.green}{_fmt_tpm(e.available):>{_COL_AVAIL}}{_C.reset}'
        row = (
            f"  │  {avail_marker} {e.model:<{_COL_MODEL}}  {_C.dim}{e.sku:<{_COL_SKU}}{_C.reset}  "
            f"{_fmt_tpm(e.limit):>{_COL_LIMIT}}  {_fmt_tpm(e.used):>{_COL_USED}}  "
            f"{avail_str}  "
            f"{_bar(e.used_pct)}"
        )
        print(row)


def _print_location_table(location: str, entries: list[QuotaEntry]) -> None:
    sep = '─' * (_COL_MODEL + _COL_SKU + _COL_LIMIT + _COL_USED + _COL_AVAIL + _COL_BAR + 14)
    print()
    print(f'  ┌─ {_C.bold}{_C.cyan}{location.upper()}{_C.reset} {"─" * max(0, len(sep) - len(location) - 4)}')

    if not entries:
        print(f'  │  {_C.dim}(no quota entries found){_C.reset}')
        print(f'  └{"─" * (len(sep) - 1)}')
        return

    # Group by provider, preserving the already-sorted order.
    providers: dict[str, list[QuotaEntry]] = {}
    for e in entries:
        providers.setdefault(e.provider, []).append(e)

    first = True
    for provider, group in providers.items():
        if not first:
            print('  │')
        first = False
        _print_provider_section(provider, group)

    print(f'  └{"─" * (len(sep) - 1)}')


def _print_summary(all_entries: list[QuotaEntry]) -> None:
    if not all_entries:
        return
    total_limit = sum(e.limit for e in all_entries)
    total_used = sum(e.used for e in all_entries)
    total_avail = sum(e.available for e in all_entries)
    locations_with_avail = len({e.location for e in all_entries if e.available > 0})

    print()
    print(f'  ┌─ {_C.bold}SUMMARY{_C.reset} ──────────────────────────────────────')
    print(f'  │  Regions queried    : {_C.white}{len({e.location for e in all_entries})}{_C.reset}')
    print(f'  │  Regions with quota : {_C.white}{locations_with_avail}{_C.reset}')
    print(f'  │  Total limit (TPM)  : {_C.white}{_fmt_tpm(total_limit)}{_C.reset}')
    print(f'  │  Total used (TPM)   : {_C.yellow}{_fmt_tpm(total_used)}{_C.reset}')
    print(f'  │  Total available    : {_C.green}{_fmt_tpm(total_avail)}{_C.reset}')
    print('  └────────────────────────────────────────────────')
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Show Azure OpenAI / Foundry model quota across regions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  python scripts/show-model-quota.py\n'
            '  python scripts/show-model-quota.py --location eastus swedencentral\n'
            '  python scripts/show-model-quota.py --filter gpt-4o --available-only\n'
            '  python scripts/show-model-quota.py --provider openai\n'
            '  python scripts/show-model-quota.py --all\n'
        ),
    )
    parser.add_argument(
        '--location', '-l',
        nargs='+',
        metavar='REGION',
        default=None,
        help=f'One or more Azure regions to check. Defaults to {len(_DEFAULT_LOCATIONS)} common regions.',
    )
    parser.add_argument(
        '--filter', '-f',
        metavar='TEXT',
        default=None,
        help='Case-insensitive substring filter applied to model names.',
    )
    parser.add_argument(
        '--available-only', '-a',
        action='store_true',
        default=False,
        help='Only show entries where available TPM > 0.',
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=False,
        help='Include entries with zero quota limit (hidden by default).',
    )
    parser.add_argument(
        '--provider', '-p',
        metavar='TEXT',
        default=None,
        help='Case-insensitive substring filter applied to provider names (e.g. openai).',
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    locations: list[str] = args.location or _DEFAULT_LOCATIONS
    name_filter: str | None = args.filter.lower() if args.filter else None
    provider_filter: str | None = args.provider.lower() if args.provider else None
    available_only: bool = args.available_only
    show_all: bool = args.all

    # Ensure UTF-8 output on Windows where the default console encoding may be CP1252.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    global _C  # noqa: PLW0603
    _C = _make_colors(_colors_enabled())

    # Verify az login.
    if not _check_az_login():
        print('Error: not logged in to Azure CLI. Run: az login', file=sys.stderr)
        return 1

    print()
    print(f'  {_C.bold}{_C.cyan}Azure AI / Foundry Model Quota{_C.reset}')
    print(f'  {_C.cyan}══════════════════════════════{_C.reset}')
    print(f'  Querying {_C.white}{len(locations)}{_C.reset} region(s)...', flush=True)

    all_entries: list[QuotaEntry] = []

    for location in locations:
        print(f'  Fetching {location}...', end='\r', flush=True)
        raw = _fetch_usages(location)
        entries = _parse_usages(location, raw)

        # Apply filters.
        if not show_all:
            entries = [e for e in entries if e.limit > 0]
        if name_filter:
            entries = [e for e in entries if name_filter in e.model.lower()]
        if provider_filter:
            entries = [e for e in entries if provider_filter in e.provider.lower()]
        if available_only:
            entries = [e for e in entries if e.available > 0]

        all_entries.extend(entries)
        _print_location_table(location, entries)

    _print_summary(all_entries)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
