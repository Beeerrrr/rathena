#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pattern> [path=. ] [--regex]" >&2
  exit 2
fi

pattern="$1"; shift || true
path="${1:-.}"; [[ $# -ge 1 ]] && shift || true
regex=false
if [[ "${1:-}" == "--regex" ]]; then regex=true; fi

if command -v rg >/dev/null 2>&1; then
  if $regex; then
    rg -n --hidden --no-heading "$pattern" "$path"
  else
    rg --fixed-strings -n --hidden --no-heading "$pattern" "$path"
  fi
  exit $?
fi

if $regex; then
  grep -RIn --line-number --binary-files=without-match --exclude-dir .git -- "$pattern" "$path"
else
  grep -RIn --line-number --fixed-strings --binary-files=without-match --exclude-dir .git -- "$pattern" "$path"
fi

