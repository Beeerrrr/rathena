#!/usr/bin/env bash
set -euo pipefail
force=false; root=""; while [[ $# -gt 0 ]]; do case "$1" in -f|--force) force=true; shift;; -r|--root) root="$2"; shift 2;; *) echo "Unknown arg: $1" >&2; exit 2;; esac; done
tool_root="${root:-$(cd "$(dirname "$0")/.." && pwd)}"; echo "Cache init at: $tool_root"
mapfile -t templates < <(find "$tool_root" -type f -name '*_template.*' \( -path '*/ANALYSIS_CACHE/*' -o -path '/*CACHE/*' -o -path '*/CACHE/*' \) 2>/dev/null || true)
count=0; for tpl in "${templates[@]}"; do dest="${tpl/_template/}"; if [[ -f "$dest" && $force == false ]]; then continue; fi; cp -f "$tpl" "$dest"; echo "Copied: $tpl -> $dest"; count=$((count+1)); done
echo "Cache init complete. Files created/updated: $count"

