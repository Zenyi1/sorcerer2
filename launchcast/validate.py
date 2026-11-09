"""Schema checks for country and asset files, so a new file fails with a sentence, not a KeyError."""
from __future__ import annotations

from .data import v

STATUSES = {"verified", "reported", "company_stated", "assumption", "unknown", "override"}
AVAILABILITY = {"available", "limited", "capacity_limited", "none"}
REG_STATUS = {"approved", "filed", "not_filed", "withdrawn", "rejected"}


def _need(d: dict, keys: list[str], where: str, errors: list[str]) -> None:
    for k in keys:
        if k not in d:
            errors.append(f"{where}: missing '{k}'")


def _graded(node, where: str, errors: list[str], numeric: bool = True) -> None:
    if isinstance(node, dict):
        if "value" not in node:
            errors.append(f"{where}: graded node needs 'value'")
        elif numeric and not isinstance(node["value"], (int, float)):
            errors.append(f"{where}: 'value' must be a number")
        if node.get("status") not in STATUSES:
            errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
    elif numeric and not isinstance(node, (int, float)):
        errors.append(f"{where}: must be a number or a graded node")


def validate_country(c: dict) -> list[str]:
    e: list[str] = []
    where = f"country {c.get('code', '?')}"
    _need(c, ["code", "name", "currency", "fx_per_usd", "fx_annual_drift_vs_usd", "population", "macro", "health_system",
              "regulatory", "pricing", "payers", "early_access_share", "budget_ceiling_share_of_pharma_market",
              "epidemiology", "competition_weights", "commercial"], where, e)
    if e:
        return e
    for k in ("fx_per_usd", "fx_annual_drift_vs_usd", "early_access_share", "budget_ceiling_share_of_pharma_market"):
        _graded(c[k], f"{where}.{k}", e)
    _need(c["population"], ["total", "nationals", "adult_share_nationals", "annual_growth"], f"{where}.population", e)
    _need(c["macro"], ["pharma_market_usd"], f"{where}.macro", e)
    _need(c["regulatory"], ["agency", "typical_review_months", "p_approval_given_fda_ema"], f"{where}.regulatory", e)
    _need(c["pricing"], ["basket", "statistic", "months_to_price_after_approval"], f"{where}.pricing", e)
    if c["pricing"].get("statistic") not in ("min", "max", "mean", "median") and not str(c["pricing"].get("statistic", "")).startswith("p"):
        e.append(f"{where}.pricing.statistic: use min | max | mean | median | pNN")
    shares = 0.0
    for i, p in enumerate(c["payers"]):
        _need(p, ["id", "name", "share_of_patients", "p_coverage", "months_to_coverage", "net_price_factor"], f"{where}.payers[{i}]", e)
        shares += float(p.get("share_of_patients", 0))
        if not 0 <= float(p.get("p_coverage", 0)) <= 1:
            e.append(f"{where}.payers[{i}].p_coverage must be in [0, 1]")
    if abs(shares - 1.0) > 0.01:
        e.append(f"{where}.payers: share_of_patients sums to {shares:.2f}, must be 1.0")
    for ind, blk in c["epidemiology"].items():
        w = f"{where}.epidemiology.{ind}"
        _need(blk, ["disease_prevalence_per_1000_adults", "alpha_thal_hbh_multiplier", "diagnosed_share",
                    "in_specialist_care_share", "label_eligible_share", "segment_mix", "soc_annual_cost_usd"], w, e)
        for k in ("disease_prevalence_per_1000_adults", "diagnosed_share", "in_specialist_care_share", "label_eligible_share"):
            if k in blk:
                _graded(blk[k], f"{w}.{k}", e)
        mix = blk.get("segment_mix", {})
        vals = [float(x) for k, x in mix.items() if k not in ("status", "source", "note")] if isinstance(mix, dict) else []
        if vals and abs(sum(vals) - 1.0) > 0.01:
            e.append(f"{w}.segment_mix sums to {sum(vals):.2f}, must be 1.0")
    _need(c["competition_weights"], ["efficacy", "convenience", "safety", "price"], f"{where}.competition_weights", e)
    _need(c["commercial"], ["launch_opex_usd_per_year", "transfer_price_share_of_net", "persistence_annual"], f"{where}.commercial", e)
    return e


def validate_asset(a: dict, countries: dict[str, dict] | None = None) -> list[str]:
    e: list[str] = []
    where = f"asset {a.get('id', '?')}"
    _need(a, ["id", "name", "originator", "deal", "indication", "regulatory_status", "reference_prices", "competitors"], where, e)
    if e:
        return e
    _need(a["deal"], ["type", "partner", "signed", "territory"], f"{where}.deal", e)
    _need(a["indication"], ["id", "label", "segments"], f"{where}.indication", e)
    ind = a["indication"].get("id")
    for code, st in a["regulatory_status"].items():
        if st.get("status") not in REG_STATUS:
            e.append(f"{where}.regulatory_status.{code}: status must be one of {sorted(REG_STATUS)}")
        if st.get("status") == "approved" and code in (countries or {}) and not st.get("date"):
            e.append(f"{where}.regulatory_status.{code}: approved entries for modelled countries need a 'date' (YYYY-MM[-DD])")
    usable = [r for r in a["reference_prices"] if r.get("indication") == ind and r.get("annual_usd")]
    if not usable:
        e.append(f"{where}.reference_prices: need at least one priced entry for indication '{ind}'")
    for i, r in enumerate(a["reference_prices"]):
        _need(r, ["country", "indication", "annual_usd", "status"], f"{where}.reference_prices[{i}]", e)
    segs = set(a["indication"]["segments"].keys())
    if set(a["competitors"].keys()) != segs:
        e.append(f"{where}: competitors segments {sorted(a['competitors'])} must equal indication.segments {sorted(segs)}")
    for seg, comps in a["competitors"].items():
        ids = [c.get("id") for c in comps]
        if "soc" not in ids:
            e.append(f"{where}.competitors.{seg}: needs an entry with id 'soc' (standard of care)")
        if a["id"] not in ids:
            e.append(f"{where}.competitors.{seg}: needs an entry with id '{a['id']}' (the asset itself, annual_price_usd null)")
        for c in comps:
            for k in ("efficacy", "convenience", "safety"):
                if not 0 <= float(c.get(k, -1)) <= 1:
                    e.append(f"{where}.competitors.{seg}.{c.get('id')}: '{k}' must be in [0, 1]")
            for code, av in (c.get("availability") or {}).items():
                if av not in AVAILABILITY:
                    e.append(f"{where}.competitors.{seg}.{c.get('id')}.availability.{code}: use {sorted(AVAILABILITY)}")
    if countries:
        for code, c in countries.items():
            if ind not in c.get("epidemiology", {}):
                e.append(f"{where}: country {code} has no epidemiology block for '{ind}'")
            elif len(segs) > 1:
                mix = c["epidemiology"][ind].get("segment_mix", {})
                missing = [s for s in segs if s not in mix]
                if missing:
                    e.append(f"{where}: country {code} epidemiology.{ind}.segment_mix lacks {missing}")
            for seg, comps in a["competitors"].items():
                for comp in comps:
                    if code not in (comp.get("availability") or {}):
                        e.append(f"{where}.competitors.{seg}.{comp.get('id')}: no availability entry for {code}")
    return e
