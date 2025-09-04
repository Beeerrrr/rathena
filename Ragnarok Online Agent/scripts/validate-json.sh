#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
mapfile -t files < <(find "$root" -type f -name '*.json' \( -path '*/ANALYSIS_CACHE/*' -o -path '/*CACHE/*' -o -path '*/CACHE/*' \) 2>/dev/null || true)
if [[ ${#files[@]} -eq 0 ]]; then echo 'No JSON files found under cache directories.'; exit 0; fi
have_jq=false; command -v jq >/dev/null 2>&1 && have_jq=true
failed=0; for f in "${files[@]}"; do if $have_jq; then jq -e '.' "$f" >/dev/null 2>&1 && echo "OK   $f" || { echo "FAIL $f"; failed=$((failed+1)); }; else python -m json.tool "$f" >/dev/null 2>&1 && echo "OK   $f" || { echo "FAIL $f"; failed=$((failed+1)); }; fi; done
exit $failed

