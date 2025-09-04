from __future__ import annotations
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


STATE_VERSION = 1


class SharedContext:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.state_dir = self._resolve_state_dir()
        self.state_file = self.state_dir / "context.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        # Ensure root structure exists
        data = self._load()
        if "meta" not in data:
            data["meta"] = {}
        data["meta"].setdefault("state_version", STATE_VERSION)
        data["meta"].setdefault("workspace_id", self._compute_workspace_id())
        self._save(data)

    def _resolve_state_dir(self) -> Path:
        override = os.getenv("DEVAI_STATE_DIR")
        if override:
            return Path(override)
        return self.base_dir / "WORKSPACE_STATE"

    def _compute_workspace_id(self) -> str:
        try:
            root = str(self.base_dir.resolve())
        except Exception:
            root = str(self.base_dir)
        h = hashlib.sha256(root.encode("utf-8")).hexdigest()
        return h[:16]

    def _load(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save(self, data: Dict[str, Any]):
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.state_file)

    def get(self, keypath: str, default: Any = None) -> Any:
        data = self._load()
        cur = data
        for part in keypath.split('.'):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def set(self, keypath: str, value: Any):
        data = self._load()
        parts = keypath.split('.')
        cur = data
        for part in parts[:-1]:
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]
        cur[parts[-1]] = value
        self._save(data)

    def append(self, keypath: str, value: Any):
        data = self._load()
        parts = keypath.split('.')
        cur = data
        for part in parts[:-1]:
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]
        leaf = parts[-1]
        if leaf not in cur or not isinstance(cur[leaf], list):
            cur[leaf] = []
        cur[leaf].append(value)
        self._save(data)

    def log_event(self, component: str, event: str, data: Optional[Dict[str, Any]] = None):
        entry = {
            "component": component,
            "event": event,
            "data": data or {},
            "ts": datetime.utcnow().isoformat() + "Z",
        }
        self.append("timeline", entry)

