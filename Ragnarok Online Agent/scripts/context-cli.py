#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path


def get_state_dir(base: Path) -> Path:
    override = os.getenv("DEVAI_STATE_DIR")
    if override:
        return Path(override)
    return base / "WORKSPACE_STATE"


def state_path(base: Path) -> Path:
    d = get_state_dir(base)
    d.mkdir(parents=True, exist_ok=True)
    return d / "context.json"


def load_state(p: Path) -> dict:
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(p: Path, data: dict):
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def get_nested(d: dict, keypath: str):
    cur = d
    for part in keypath.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def set_nested(d: dict, keypath: str, value):
    parts = keypath.split('.')
    cur = d
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def ensure_list(d: dict, keypath: str):
    parts = keypath.split('.')
    cur = d
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    leaf = parts[-1]
    if leaf not in cur or not isinstance(cur[leaf], list):
        cur[leaf] = []
    return cur[leaf]


def parse_kv_pairs(pairs: list[str]) -> dict:
    out = {}
    for p in pairs:
        if '=' in p:
            k, v = p.split('=', 1)
            out[k] = v
    return out


def main():
    parser = argparse.ArgumentParser(description="Shared workspace context CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_get = sub.add_parser("get", help="Get a value by dotted path")
    p_get.add_argument("key")

    p_set = sub.add_parser("set", help="Set a value by dotted path")
    p_set.add_argument("key")
    p_set.add_argument("value")

    p_append = sub.add_parser("append", help="Append to a list at dotted path")
    p_append.add_argument("key")
    p_append.add_argument("value")

    p_log = sub.add_parser("log", help="Append an event to timeline")
    p_log.add_argument("component")
    p_log.add_argument("event")
    p_log.add_argument("data", nargs="*", help="key=value pairs")

    p_dump = sub.add_parser("dump", help="Print entire context as JSON")

    args = parser.parse_args()

    base = Path.cwd()
    p = state_path(base)
    state = load_state(p)

    if args.cmd == "get":
        val = get_nested(state, args.key)
        if isinstance(val, (dict, list)):
            print(json.dumps(val, indent=2, ensure_ascii=False))
        else:
            print(val if val is not None else "")
        return

    if args.cmd == "set":
        value = args.value
        try:
            value = json.loads(value)
        except Exception:
            pass
        set_nested(state, args.key, value)
        save_state(p, state)
        print("OK")
        return

    if args.cmd == "append":
        lst = ensure_list(state, args.key)
        try:
            val = json.loads(args.value)
        except Exception:
            val = args.value
        lst.append(val)
        save_state(p, state)
        print("OK")
        return

    if args.cmd == "log":
        timeline = ensure_list(state, "timeline")
        data = parse_kv_pairs(args.data)
        timeline.append({
            "component": args.component,
            "event": args.event,
            "data": data,
            "ts": datetime.utcnow().isoformat() + "Z",
        })
        save_state(p, state)
        print("OK")
        return

    if args.cmd == "dump":
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return


if __name__ == "__main__":
    main()

