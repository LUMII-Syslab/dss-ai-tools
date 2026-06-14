#!/usr/bin/env bash
# Keep the bundled copies of dss.py in sync with the canonical one at the repo
# root. The skill and the MCP server each need dss.py alongside them (a skill
# folder must be self-contained; the MCP server imports `dss` from its own
# dir), so the file is committed in three places. Run this script after editing
# the canonical dss.py; `--check` mode is suitable for a CI guard.
#
#   scripts/sync.sh          copy root dss.py -> skill/ and mcp-server/
#   scripts/sync.sh --check  exit non-zero if any copy is stale (use in CI)
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
src="$root/dss.py"
copies=("$root/skill/dss.py" "$root/mcp-server/dss.py")

if [[ "${1:-}" == "--check" ]]; then
    status=0
    for c in "${copies[@]}"; do
        if ! diff -q "$src" "$c" >/dev/null 2>&1; then
            echo "stale: $c differs from dss.py (run scripts/sync.sh)" >&2
            status=1
        fi
    done
    exit "$status"
fi

for c in "${copies[@]}"; do
    cp "$src" "$c"
    echo "synced -> $c"
done
