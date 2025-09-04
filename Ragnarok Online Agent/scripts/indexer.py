#!/usr/bin/env python3
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

SKIP_DIRS = {
    '.git', 'node_modules', 'dist', 'build', '.venv', 'venv', '__pycache__',
    'DEBUG_CACHE', 'QA_CACHE', 'DATA_CACHE', 'API_CACHE', 'ANALYSIS_CACHE', 'WORKSPACE_STATE'
}

MAX_HASH_BYTES = 1024 * 1024


def file_hash(path: Path) -> str:
    h = hashlib.sha1()
    try:
        with path.open('rb') as f:
            h.update(f.read(MAX_HASH_BYTES))
        return h.hexdigest()
    except Exception:
        return ''


def index_workspace(root: Path) -> dict:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                rel = p.relative_to(root).as_posix()
            except ValueError:
                rel = str(p)
            try:
                size = p.stat().st_size
            except Exception:
                size = 0
            files.append({
                'path': rel,
                'size': size,
                'ext': p.suffix,
                'hash': file_hash(p),
            })
    return {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'root': str(root),
        'count': len(files),
        'files': files,
    }


def main():
    root = Path.cwd()
    state_dir = root / 'WORKSPACE_STATE'
    state_dir.mkdir(parents=True, exist_ok=True)
    out = state_dir / 'code_index.json'
    data = index_workspace(root)
    out.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f'Indexed {data["count"]} files -> {out}')


if __name__ == '__main__':
    main()

