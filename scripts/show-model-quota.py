"""Show available Azure OpenAI / Foundry model quota across one or more regions.

Fetches quota usage from 'az cognitiveservices usage list' and displays a clean
summary table showing TPM limits, current usage, and remaining capacity for every
OpenAI model quota entry in each requested region.

Usage:
    python scripts/show-model-quota.py
    python scripts/show-model-quota.py --location eastus westus3 swedencentral
    python scripts/show-model-quota.py --location eastus --all
    python scripts/show-model-quota.py --filter gpt-4o
    python scripts/show-model-quota.py --available-only
"""

from __future__ import annotations

import argparse
import json
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

_OPENAI_PREFIX = 'OpenAI.'

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


def _parse_quota_name(raw_name: str) -> tuple[str, str] | None:
    """Parse 'OpenAI.<sku>.<model>' into (sku, model). Returns None if not OpenAI."""
    if not raw_name.startswith(_OPENAI_PREFIX):
        return None
    remainder = raw_name[len(_OPENAI_PREFIX):]
    # The SKU is the first segment; the model name is everything after.
    parts = remainder.split('.', 1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def _parse_usages(location: str, raw: list[dict]) -> list[QuotaEntry]:
    entries: list[QuotaEntry] = []
    for item in raw:
        raw_name: str = (item.get('name') or {}).get('value', '')
        parsed = _parse_quota_name(raw_name)
        if parsed is None:
            continue
        sku, model = parsed
        limit = int(item.get('limit') or 0)
        used = int(item.get('currentValue') or 0)
        entries.append(QuotaEntry(
            location=location,
            model=model,
            sku=sku,
            limit=limit,
            used=used,
        ))
    return sorted(entries, key=lambda e: (e.model.lower(), e.sku.lower()))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _bar(used_pct: float, width: int = _COL_BAR) -> str:
    """Render a usage bar like '[████░░░░░░░░░░░░░░░░]'."""
    filled = round(used_pct / 100 * width)
    filled = max(0, min(width, filled))
    return '[' + '█' * filled + '░' * (width - filled) + ']'


def _fmt_tpm(value: int) -> str:
    """Format TPM value with K suffix for readability."""
    if value >= 1_000:
        return f'{value // 1_000}K'
    return str(value)


def _print_location_table(location: str, entries: list[QuotaEntry]) -> None:
    sep = '─' * (_COL_MODEL + _COL_SKU + _COL_LIMIT + _COL_USED + _COL_AVAIL + _COL_BAR + 14)
    print()
    print(f'  ┌─ {location.upper()} {"─" * max(0, len(sep) - len(location) - 4)}')

    if not entries:
        print('  │  (no OpenAI quota entries found)')
        print(f'  └{"─" * (len(sep) - 1)}')
        return

    header = (
        f"  │  {'Model':<{_COL_MODEL}}  {'SKU':<{_COL_SKU}}  "
        f"{'Limit':>{_COL_LIMIT}}  {'Used':>{_COL_USED}}  {'Available':>{_COL_AVAIL}}  "
        f"{'Usage':^{_COL_BAR}}"
    )
    divider = (
        f"  │  {'─' * _COL_MODEL}  {'─' * _COL_SKU}  "
        f"{'─' * _COL_LIMIT}  {'─' * _COL_USED}  {'─' * _COL_AVAIL}  "
        f"{'─' * _COL_BAR}"
    )
    print(header)
    print(divider)

    for e in entries:
        avail_marker = ' !' if e.available == 0 and e.limit > 0 else '  '
        row = (
            f"  │{avail_marker} {e.model:<{_COL_MODEL}}  {e.sku:<{_COL_SKU}}  "
            f"{_fmt_tpm(e.limit):>{_COL_LIMIT}}  {_fmt_tpm(e.used):>{_COL_USED}}  "
            f"{_fmt_tpm(e.available):>{_COL_AVAIL}}  "
            f"{_bar(e.used_pct)}"
        )
        print(row)

    print(f'  └{"─" * (len(sep) - 1)}')


def _print_summary(all_entries: list[QuotaEntry]) -> None:
    if not all_entries:
        return
    total_limit = sum(e.limit for e in all_entries)
    total_used = sum(e.used for e in all_entries)
    total_avail = sum(e.available for e in all_entries)
    locations_with_avail = len({e.location for e in all_entries if e.available > 0})

    print()
    print('  ┌─ SUMMARY ──────────────────────────────────────')
    print(f'  │  Regions queried    : {len({e.location for e in all_entries})}')
    print(f'  │  Regions with quota : {locations_with_avail}')
    print(f'  │  Total limit (TPM)  : {_fmt_tpm(total_limit)}')
    print(f'  │  Total used (TPM)   : {_fmt_tpm(total_used)}')
    print(f'  │  Total available    : {_fmt_tpm(total_avail)}')
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
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    locations: list[str] = args.location or _DEFAULT_LOCATIONS
    name_filter: str | None = args.filter.lower() if args.filter else None
    available_only: bool = args.available_only
    show_all: bool = args.all

    # Verify az login.
    if not _check_az_login():
        print('Error: not logged in to Azure CLI. Run: az login', file=sys.stderr)
        return 1

    print()
    print('  Azure OpenAI / Foundry Model Quota')
    print('  ════════════════════════════════════')
    print(f'  Querying {len(locations)} region(s)...', flush=True)

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
        if available_only:
            entries = [e for e in entries if e.available > 0]

        all_entries.extend(entries)
        _print_location_table(location, entries)

    _print_summary(all_entries)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
