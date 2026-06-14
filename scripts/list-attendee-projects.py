"""List attendee project names expected from infra parameterization."""

from __future__ import annotations

import argparse


def main() -> None:
    """List expected attendee project names based on count and prefix."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=20)
    parser.add_argument('--prefix', default='attendee')
    args = parser.parse_args()

    for i in range(1, args.count + 1):
        print(f"{args.prefix}-{i:02d}")


if __name__ == '__main__':
    main()
