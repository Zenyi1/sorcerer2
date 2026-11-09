"""External reference pricing (ERP) engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .data import v


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolated percentile, q in [0, 1]."""
    if not values:
        raise ValueError("percentile of empty list")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = q * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def statistic(values: list[float], name: str) -> float:
    name = name.lower()
    if name == "min":
        return min(values)
    if name == "max":
        return max(values)
    if name == "mean":
        return sum(values) / len(values)
    if name == "median":
        return percentile(values, 0.5)
    if name.startswith("p") and name[1:].isdigit():
        return percentile(values, int(name[1:]) / 100.0)
    raise ValueError(f"Unknown ERP statistic '{name}'")


@dataclass
class ERPResult:
    list_price_usd: float
    statistic: str
    used: list[dict] = field(default_factory=list)
    excluded: list[dict] = field(default_factory=list)
    capped_by_origin: bool = False
    origin_price: Optional[float] = None
    note: str = ""


def erp_price(pricing: dict, reference_prices: list[dict], origin_country: str = "US",
              include_assumed: bool = True, indication: str = "thalassemia") -> ERPResult:
    """Apply a country's ERP rule to the asset's reference price table.

    Only prices for the same indication, in the country's basket, with a known
    value are used. 'assumption'-grade prices are included unless disabled.
    """
    basket = [c.upper() for c in pricing.get("basket", [])]
    stat = pricing.get("statistic", "median")
    used, excluded = [], []
    for ref in reference_prices:
        reason = None
        if ref.get("indication") != indication:
            reason = "different indication"
        elif ref.get("use_in_basket") is False:
            reason = "excluded by table"
        elif ref.get("annual_usd") is None:
            reason = "no price known"
        elif ref["country"].upper() not in basket:
            reason = "not in basket"
        elif ref.get("status") == "assumption" and not include_assumed:
            reason = "assumed price excluded (--exclude-assumed-prices)"
        if reason:
            excluded.append({**ref, "reason": reason})
        else:
            used.append(ref)
    if not used:
        # Fall back to the origin price so the model still runs; flag it loudly.
        origin = next((r for r in reference_prices if r["country"].upper() == origin_country.upper()
                       and r.get("indication") == indication and r.get("annual_usd")), None)
        if origin is None:
            raise ValueError("No usable reference prices")
        return ERPResult(float(origin["annual_usd"]), stat, [origin], excluded, False, float(origin["annual_usd"]),
                         "No basket prices usable; country-of-origin price used as placeholder")
    values = [float(r["annual_usd"]) for r in used]
    price = statistic(values, stat)
    origin_price = next((float(r["annual_usd"]) for r in used if r["country"].upper() == origin_country.upper()), None)
    capped = False
    if pricing.get("origin_country_cap") and origin_price is not None and price > origin_price:
        price, capped = origin_price, True
    note = f"{stat} of {len(used)} basket prices"
    if capped:
        note += f"; capped at country-of-origin ({origin_country}) price"
    return ERPResult(price, stat, used, excluded, capped, origin_price, note)


def local_price(usd: float, fx_per_usd: float) -> float:
    return usd * fx_per_usd
