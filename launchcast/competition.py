"""Peak-share model: multinomial logit over the therapies actually available in the country."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

AVAILABILITY_FACTOR = {"available": 1.0, "limited": 0.35, "capacity_limited": 1.0, "none": 0.0}
STATUS_QUO_BONUS = 1.5  # inertia of the current standard of care (trial-and-stop behaviour, monitoring burden)


@dataclass
class Option:
    id: str
    name: str
    availability: str
    price_usd: float
    utility: float
    share: float
    efficacy: float
    convenience: float
    safety: float
    capped: bool = False


@dataclass
class SegmentShares:
    segment: str
    options: list[Option] = field(default_factory=list)
    asset_share: float = 0.0
    weights: dict = field(default_factory=dict)


def segment_shares(competitors: list[dict], country_code: str, weights: dict, asset_id: str,
                   asset_net_price_usd: float) -> SegmentShares:
    w_eff = float(weights.get("efficacy", 2.0))
    w_conv = float(weights.get("convenience", 1.0))
    w_safe = float(weights.get("safety", 1.0))
    w_price = float(weights.get("price", 1.0))
    soc = next((c for c in competitors if c["id"] == "soc"), None)
    soc_price = float(soc["annual_price_usd"]) if soc and soc.get("annual_price_usd") else 1.0

    opts: list[Option] = []
    for c in competitors:
        avail = c.get("availability", {}).get(country_code, "none")
        factor = AVAILABILITY_FACTOR.get(avail, 0.0)
        if factor == 0.0:
            opts.append(Option(c["id"], c["name"], avail, float(c.get("annual_price_usd") or 0), float("-inf"), 0.0,
                               c.get("efficacy", 0), c.get("convenience", 0), c.get("safety", 0)))
            continue
        price = asset_net_price_usd if c["id"] == asset_id else float(c.get("annual_price_usd") or soc_price)
        price_index = math.log10(max(price, 1.0) / max(soc_price, 1.0))
        util = (w_eff * float(c.get("efficacy", 0)) + w_conv * float(c.get("convenience", 0))
                + w_safe * float(c.get("safety", 0)) - w_price * price_index)
        if c["id"] == "soc":
            util += STATUS_QUO_BONUS
        util_eff = util + math.log(factor)
        opts.append(Option(c["id"], c["name"], avail, price, util_eff, 0.0,
                           c.get("efficacy", 0), c.get("convenience", 0), c.get("safety", 0)))

    live = [o for o in opts if o.utility != float("-inf")]
    denom = sum(math.exp(o.utility) for o in live)
    for o in live:
        o.share = math.exp(o.utility) / denom if denom else 0.0

    # Capacity caps (e.g. gene therapy centres): cap the share and give the remainder to the others pro rata.
    caps = {c["id"]: float(c["capacity_share_cap"]) for c in competitors if c.get("capacity_share_cap") is not None}
    capped_total = 0.0
    for o in live:
        if o.id in caps and o.share > caps[o.id]:
            o.share, o.capped = caps[o.id], True
            capped_total += caps[o.id]
    if any(o.capped for o in live):
        rest = [o for o in live if not o.capped]
        rest_sum = sum(o.share for o in rest)
        for o in rest:
            o.share = o.share / rest_sum * (1.0 - capped_total) if rest_sum else 0.0

    seg = SegmentShares(segment="", options=opts, weights={"efficacy": w_eff, "convenience": w_conv, "safety": w_safe, "price": w_price})
    seg.asset_share = next((o.share for o in opts if o.id == asset_id), 0.0)
    return seg
