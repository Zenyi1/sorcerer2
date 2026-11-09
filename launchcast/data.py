"""Loading of the JSON knowledge base plus dotted-path overrides."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Iterable

PKG_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("LAUNCHCAST_DATA", PKG_DIR.parent / "data"))

STATUS_LEGEND = {
    "verified": "primary source read for this model (regulator, statistics office, filing)",
    "reported": "secondary source (press release, industry body, trade press)",
    "company_stated": "the originator's own figure (earnings call, investor deck)",
    "assumption": "our modelling assumption; rationale given; moves in sensitivity",
    "unknown": "not found; excluded from calculations",
}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_config() -> dict:
    return load_json(DATA_DIR / "config.json")


def list_countries() -> list[str]:
    return sorted(p.stem for p in (DATA_DIR / "countries").glob("*.json") if not p.stem.startswith("_"))


def list_assets() -> list[str]:
    return sorted(p.stem for p in (DATA_DIR / "assets").glob("*.json") if not p.stem.startswith("_"))


def load_country(code: str) -> dict:
    path = DATA_DIR / "countries" / f"{code.upper()}.json"
    if not path.exists():
        raise FileNotFoundError(f"No country file for '{code}'. Available: {', '.join(list_countries())}")
    return load_json(path)


def load_asset(asset_id: str) -> dict:
    path = DATA_DIR / "assets" / f"{asset_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No asset file for '{asset_id}'. Available: {', '.join(list_assets())}")
    return load_json(path)


def v(node: Any, default: Any = None) -> Any:
    """Unwrap {'value': x, 'status': ..., 'source': ...} nodes; pass scalars through."""
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    if node is None:
        return default
    return node


def status_of(node: Any, default: str = "assumption") -> str:
    if isinstance(node, dict):
        return node.get("status", default)
    return default


def source_of(node: Any) -> str:
    if isinstance(node, dict):
        return node.get("source", "")
    return ""


def _split(path: str) -> list[str]:
    return [p for p in path.split(".") if p]


def get_path(d: Any, path: str) -> Any:
    cur = d
    for key in _split(path):
        if isinstance(cur, list):
            cur = cur[int(key)]
        else:
            cur = cur[key]
    return cur


def iter_paths(d: Any, path: str) -> Iterable[tuple[Any, str]]:
    """Yield (container, final_key) pairs for a dotted path; '*' fans out over lists."""
    keys = _split(path)

    def walk(cur: Any, idx: int):
        if idx == len(keys) - 1:
            yield cur, keys[idx]
            return
        key = keys[idx]
        if key == "*":
            if not isinstance(cur, list):
                raise KeyError(f"'*' used on non-list at {'.'.join(keys[:idx])}")
            for item in cur:
                yield from walk(item, idx + 1)
        else:
            nxt = cur[int(key)] if isinstance(cur, list) else cur[key]
            yield from walk(nxt, idx + 1)

    yield from walk(d, 0)


def set_path(d: Any, path: str, value: Any) -> None:
    for container, key in iter_paths(d, path):
        if isinstance(container, list):
            container[int(key)] = value
        elif isinstance(container.get(key), dict) and "value" in container[key] and not isinstance(value, dict):
            container[key]["value"] = value
            container[key]["status"] = "override"
        else:
            container[key] = value
            if key == "value" and isinstance(container, dict) and "status" in container:
                container["status"] = "override"


def parse_literal(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def apply_overrides(d: dict, overrides: Iterable[str]) -> dict:
    """Apply 'a.b.c=value' overrides to a deep copy. Values are parsed as JSON when possible."""
    out = copy.deepcopy(d)
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"Override '{item}' must look like path=value")
        path, raw = item.split("=", 1)
        set_path(out, path.strip(), parse_literal(raw.strip()))
    return out
