#!/usr/bin/env bash
#
# test-lab-module.sh — Validate a workshop lab module README.
#
# Confirms every screenshot the README references exists on disk and runs
# markdownlint over the README. Exits non-zero if any screenshot is missing or
# markdownlint reports errors, so it can gate a lab update.
#
# Usage:
#   ./test-lab-module.sh --readme labs/introduction-foundry-agent-service/06-mcp-tools/README.md [--skip-lint]
#
# Requires: bash, grep, sed. The markdownlint step requires pnpm + markdownlint-cli2
# (skipped automatically if pnpm is not found).

set -euo pipefail

README_PATH=""
SKIP_LINT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --readme)
      README_PATH="${2:-}"
      shift 2
      ;;
    --skip-lint)
      SKIP_LINT=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$README_PATH" ]]; then
  echo "Error: --readme <path> is required." >&2
  exit 2
fi

if [[ ! -f "$README_PATH" ]]; then
  echo "README not found: $README_PATH" >&2
  exit 2
fi

readme_dir="$(cd "$(dirname "$README_PATH")" && pwd)"
readme_name="$(basename "$README_PATH")"

checked=0
missing=()

# Extract Markdown image references: ![alt](path)
while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue

  # Ignore remote images and in-page anchors
  case "$ref" in
    http://*|https://*|//*|\#*) continue ;;
  esac

  # Strip any title/fragment after the path
  path_part="${ref%%[[:space:]]*}"
  path_part="${path_part%%#*}"

  checked=$((checked + 1))

  if [[ ! -f "$readme_dir/$path_part" ]]; then
    missing+=("$path_part")
  fi
done < <(grep -oE '!\[[^]]*\]\([^)]+\)' "$README_PATH" | sed -E 's/!\[[^]]*\]\(([^)]+)\)/\1/')

echo "Checked $checked local image reference(s) in $readme_name."

if [[ ${#missing[@]} -gt 0 ]]; then
  echo ""
  echo "MISSING screenshot file(s):"
  for entry in "${missing[@]}"; do
    echo "  - $entry"
  done
else
  echo "All referenced screenshots exist on disk."
fi

lint_failed=0
if [[ "$SKIP_LINT" -eq 0 ]]; then
  if ! command -v pnpm >/dev/null 2>&1; then
    echo "Warning: pnpm not found; skipping markdownlint. Re-run with the lint toolchain installed." >&2
  else
    echo ""
    echo "Running markdownlint-cli2..."
    if ! pnpm exec markdownlint-cli2 "$README_PATH"; then
      lint_failed=1
    fi
  fi
fi

if [[ ${#missing[@]} -gt 0 || "$lint_failed" -eq 1 ]]; then
  exit 1
fi

echo ""
echo "Lab module validation passed."
exit 0
