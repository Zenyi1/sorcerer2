"""One-at-a-time sensitivity (tornado) on risk-adjusted NPV."""
from __future__ import annotations

import copy

from .data import iter_paths
from .forecast import run_forecast


def _apply(container, key, spec: dict, side: str) -> None:
    node = container[key]
    is_wrapped = isinstance(node, dict) and "value" in node
    cur = node["value"] if is_wrapped else node
    if f"{side}_set" in spec:
        new = spec[f"{side}_set"]
    elif f"{side}_mult" in spec:
        new = cur * spec[f"{side}_mult"]
    elif f"{side}_add" in spec:
        new = cur + spec[f"{side}_add"]
    else:
        return
    if isinstance(new, (int, float)):
        if any(tok in key for tok in ("p_coverage", "share", "persistence", "bad_debt")):
            new = max(0.0, min(1.0, new))
        if key in ("months_to_coverage", "dso_days"):
            new = max(0.0, new)
    if is_wrapped:
        node["value"] = new
    else:
        container[key] = new


def tornado(country: dict, asset: dict, config: dict, indication: str, include_assumed: bool = True) -> dict:
    base = run_forecast(country, asset, config, indication, include_assumed).metrics["rnpv_expected"]
    results = []
    for spec in config["sensitivity"]["parameters"]:
        path = spec["path"].replace("<ind>", indication)
        vals = {}
        for side in ("low", "high"):
            c = copy.deepcopy(country)
            try:
                targets = list(iter_paths(c, path))
            except (KeyError, IndexError, TypeError):
                targets = []
            if not targets:
                vals[side] = None
                continue
            for container, key in targets:
                _apply(container, key, spec, side)
            vals[side] = run_forecast(c, asset, config, indication, include_assumed).metrics["rnpv_expected"]
        if vals["low"] is None or vals["high"] is None:
            continue
        lo, hi = vals["low"], vals["high"]
        results.append({"label": spec["label"], "low": lo, "high": hi, "swing": abs(hi - lo),
                        "flips": (lo < 0) != (hi < 0) or ((lo < 0) != (base < 0)) or ((hi < 0) != (base < 0))})
    results.sort(key=lambda r: r["swing"], reverse=True)
    return {"base": base, "results": results}
