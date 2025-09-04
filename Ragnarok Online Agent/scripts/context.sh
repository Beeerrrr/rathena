#!/usr/bin/env bash
set -euo pipefail

CMD=${1:-}
shift || true

CLI="$(pwd)/scripts/context-cli.py"
if [[ ! -f "$CLI" ]]; then
  echo "context-cli.py not found: $CLI" >&2
  exit 1
fi

case "$CMD" in
  get) python "$CLI" get "$@" ;;
  set) python "$CLI" set "$@" ;;
  append) python "$CLI" append "$@" ;;
  log) python "$CLI" log "$@" ;;
  dump) python "$CLI" dump ;;
  *) echo "Usage: scripts/context.sh {get|set|append|log|dump} ..." >&2; exit 2 ;;
esac

