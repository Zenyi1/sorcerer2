"""Deterministic 10-year launch forecast for one asset in one country."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .competition import SegmentShares, segment_shares
from .data import v
from .funnel import Funnel, patient_funnel
from .pricing import ERPResult, erp_price


@dataclass
class YearRow:
    year: int
    eligible: float
    access_success: float
    access_expected: float
    uptake: float
    treated_success: float
    treated_expected: float
    list_price: float
    net_price: float
    budget_cap_factor: float
    net_sales_success: float
    net_sales_expected: float
    opex: float
    upfront: float
    cash_success: float
    cash_expected: float
    cum_cash_expected: float
    pv_cash_expected: float


@dataclass
class Timeline:
    start_year: int
    already_approved: bool
    filing_t: Optional[float]
    approval_t: float
    pricing_t: float
    coverage_t: dict
    p_registration: float
    approval_label: str


@dataclass
class Forecast:
    country: dict
    asset: dict
    indication: str
    funnel: Funnel
    erp: ERPResult
    shares: dict
    peak_share: float
    timeline: Timeline
    rows: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    payer_table: list = field(default_factory=list)


def _ramp(t: float, start: float, length: float = 1.0) -> float:
    if t <= start:
        return 0.0
    return min(1.0, (t - start) / length)


def _uptake(tau: float, years_to_peak: float) -> float:
    """Logistic uptake: 5% of peak at launch, 95% at years_to_peak."""
    if tau < 0:
        return 0.0
    k = 2.0 * math.log(19.0) / years_to_peak
    return 1.0 / (1.0 + math.exp(-k * (tau - years_to_peak / 2.0)))


def _year_from_date(text: str) -> float:
    parts = text.split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 6
    return year + (month - 0.5) / 12.0


def run_forecast(country: dict, asset: dict, config: dict, indication: Optional[str] = None,
                 include_assumed_prices: bool = True) -> Forecast:
    code = country["code"]
    start = int(config.get("analysis_start_year", 2026))
    horizon = int(config.get("horizon_years", 10))
    main_ind = asset["indication"]["id"]
    indication = indication or main_ind
    notes: list[str] = []

    # --- indication / regulatory status -------------------------------------------------
    pipeline = None
    if indication != main_ind:
        pipeline = asset["pipeline_indications"][indication]
        competitors = pipeline["competitors"]
    else:
        competitors = asset["competitors"]
    if indication not in country["epidemiology"]:
        raise KeyError(f"{country['name']} has no epidemiology block for '{indication}'")

    reg = country["regulatory"]
    review_years = float(v(reg["typical_review_months"])) / 12.0
    status = asset["regulatory_status"].get(code, {"status": "not_filed"})
    if pipeline is None and status.get("status") == "approved":
        approval_t = _year_from_date(status["date"]) - start
        filing_t = None
        p_reg = 1.0
        already = True
        approval_label = f"approved {status['date']} ({status.get('pathway', country['regulatory']['agency'])})"
    elif pipeline is None and status.get("status") == "filed":
        # Dossier already with the regulator: no filing cost, decision at the expected date.
        filing_t = None
        approval_t = (_year_from_date(status["expected_decision"]) - start) if status.get("expected_decision") else review_years
        approval_t = max(approval_t, 0.1)
        p_reg = float(status.get("p_approval", v(reg["p_approval_given_fda_ema"])))
        already = False
        approval_label = (f"filed {status.get('date', '')}; decision expected ~{start + approval_t:.1f} "
                          f"({country['regulatory']['agency']}), P(approval)={p_reg:.0%}")
    else:
        filing_t = float(reg.get("filing_lag_years", 0))
        if pipeline is not None:
            # File once the reference agency has approved the new indication.
            filing_t = max(filing_t, float(pipeline["approval_year"]) - start)
        approval_t = filing_t + review_years
        p_reg = float(v(reg["p_approval_given_fda_ema"]))
        if pipeline is not None:
            p_reg *= float(pipeline["p_approval"])
        already = False
        approval_label = (f"not filed; file {start + filing_t:.1f}, decision ~{start + approval_t:.1f} "
                          f"({country['regulatory']['agency']} ~{float(v(reg['typical_review_months'])):.0f} months), "
                          f"P(approval)={p_reg:.0%}")
    pricing_t = approval_t + float(v(country["pricing"]["months_to_price_after_approval"])) / 12.0

    payers = country["payers"]
    coverage_t = {p["id"]: pricing_t + float(p["months_to_coverage"]) / 12.0 for p in payers if p["p_coverage"] > 0}
    timeline = Timeline(start, already, filing_t, approval_t, pricing_t, coverage_t, p_reg, approval_label)

    # --- inputs ---------------------------------------------------------------------------
    funnel = patient_funnel(country, indication, asset)
    erp = erp_price(country["pricing"], asset["reference_prices"], origin_country="US",
                    include_assumed=include_assumed_prices, indication=main_ind)
    list_price = erp.list_price_usd
    covered = [p for p in payers if p["p_coverage"] > 0]
    cov_weight = sum(p["share_of_patients"] for p in covered)
    net_factor_full = sum(p["share_of_patients"] * p["net_price_factor"] for p in covered) / cov_weight if cov_weight else 1.0
    asset_net_for_share = list_price * net_factor_full

    weights = country["competition_weights"]
    shares: dict[str, SegmentShares] = {}
    for seg_name, comps in competitors.items():
        seg = segment_shares(comps, code, weights, asset["id"], asset_net_for_share)
        seg.segment = seg_name
        shares[seg_name] = seg
    # Blend segment shares by the country's eligible mix. A single-segment asset needs no mix.
    seg_ids = list(competitors.keys())
    if len(seg_ids) == 1:
        mix = {seg_ids[0]: 1.0}
    else:
        missing = [sg for sg in seg_ids if sg not in funnel.segment_mix]
        if missing:
            raise KeyError(f"{country['name']} epidemiology.{indication}.segment_mix lacks segment(s) {missing} used by {asset['id']}")
        tot = sum(funnel.segment_mix[sg] for sg in seg_ids)
        mix = {sg: funnel.segment_mix[sg] / tot for sg in seg_ids}
    funnel.segment_mix = mix
    peak_share = sum(mix[sg] * shares[sg].asset_share for sg in seg_ids)

    # --- economics --------------------------------------------------------------------------
    com = country["commercial"]
    persistence = float(v(com["persistence_annual"]))
    transfer = float(v(com["transfer_price_share_of_net"]))
    logistics = float(com.get("logistics_share_of_net", 0.0))
    coc = float(com.get("cost_of_capital", 0.10))
    launch_opex = float(v(com["launch_opex_usd_per_year"]))
    prelaunch_opex = float(com.get("prelaunch_opex_usd_per_year", 0.0))
    ramp_years = float(com.get("opex_ramp_years", 1))
    ea_share = float(v(country["early_access_share"]))
    ceiling = float(v(country["budget_ceiling_share_of_pharma_market"])) * float(v(country["macro"]["pharma_market_usd"]))
    growth = float(v(country["population"]["annual_growth"]))
    drift = float(v(country["fx_annual_drift_vs_usd"]))
    reprice_after = float(country["pricing"].get("reprice_after_years", 99))
    reprice_cut = float(v(country["pricing"].get("reprice_cut", 0.0)))
    years_to_peak = float(v(asset.get("uptake", {}).get("years_to_peak", 5)))

    rows: list[YearRow] = []
    cum = 0.0
    cap_years: list[int] = []
    for i in range(horizon):
        year = start + i
        t = i + 0.5
        eligible = funnel.eligible * (1 + growth) ** i
        tau = t - approval_t
        f = _uptake(tau, years_to_peak)

        # access by payer
        acc_s = acc_e = 0.0
        net_s = net_e = 0.0
        bd_s = dso_s = 0.0
        pub_s = 0.0
        for p in covered:
            r = _ramp(t, coverage_t[p["id"]])
            w_s = p["share_of_patients"] * r
            w_e = w_s * p["p_coverage"]
            acc_s += w_s
            acc_e += w_e
            net_s += w_s * p["net_price_factor"]
            net_e += w_e * p["net_price_factor"]
            bd_s += w_s * p.get("bad_debt", 0.0)
            dso_s += w_s * p.get("dso_days", 0.0)
            if p.get("public"):
                pub_s += w_s * p["net_price_factor"]
        # Early access: case-by-case treatment from hospital budgets before any listing, paid at list.
        # Modelled as a share of eligible patients that ramps in over the first year after approval and
        # is displaced as paying routes open (1 - access).
        ea_frac = ea_share * _ramp(t, approval_t, 1.0) * (1.0 - acc_s) if tau >= 0 else 0.0
        bd = bd_s / acc_s if acc_s else 0.0
        dso = dso_s / acc_s if acc_s else 0.0

        erosion = (1 - reprice_cut) if (approval_t + reprice_after) <= t else 1.0
        fx = (1 + drift) ** max(0.0, t - pricing_t)
        lp = list_price * erosion * fx

        # patients on therapy: reimbursed routes follow the competitive share and the uptake curve;
        # early access is a direct (small) share of eligible patients
        reimb_frac_s = acc_s * peak_share * f
        reimb_frac_e = acc_e * peak_share * f
        treated_s = eligible * (reimb_frac_s + ea_frac) * persistence
        treated_e = eligible * (reimb_frac_e + ea_frac) * persistence * p_reg
        acc_s_total = acc_s + ea_frac
        acc_e_total = acc_e + ea_frac

        # budget-impact ceiling on public spend (success case, price-volume agreement)
        public_spend = eligible * pub_s * peak_share * f * persistence * lp
        cap_factor = min(1.0, ceiling / public_spend) if public_spend > 0 and ceiling > 0 else 1.0
        if cap_factor < 1.0:
            cap_years.append(year)
        # blended net price: reimbursed patients at their route's net factor (capped), early access at list
        def blend(reimb_frac: float, net_w: float, acc: float) -> float:
            total = reimb_frac + ea_frac
            if total <= 0:
                return lp * net_factor_full
            reimb_price = lp * (net_w / acc if acc else net_factor_full) * cap_factor
            return (reimb_frac * reimb_price + ea_frac * lp) / total
        net_price_s = blend(reimb_frac_s, net_s, acc_s)
        net_price_e = blend(reimb_frac_e, net_e, acc_e)

        sales_s = treated_s * net_price_s
        sales_e = treated_e * net_price_e

        # costs
        upfront_s = upfront_e = 0.0
        for item in com.get("upfront_costs_usd", []):
            when = item.get("timing", "approval")
            if when == "filing" and filing_t is not None and int(math.floor(filing_t)) == i:
                upfront_s += item["amount"]; upfront_e += item["amount"]
            if when == "approval":
                yr = int(math.floor(approval_t)) if approval_t >= 0 else 0
                if yr == i:
                    upfront_s += item["amount"]; upfront_e += item["amount"] * p_reg
        opex_s = opex_e = 0.0
        if (filing_t if filing_t is not None else 0.0) <= t < approval_t:
            opex_s += prelaunch_opex; opex_e += prelaunch_opex
        if t >= approval_t:
            ramp = min(1.0, 0.6 + 0.4 * max(0.0, (t - approval_t) / max(ramp_years, 1e-9))) if ramp_years > 0 else 1.0
            opex_s += launch_opex * ramp; opex_e += launch_opex * ramp * p_reg

        def cash(sales: float, opex: float, upfront: float) -> float:
            margin = sales * (1 - transfer - logistics - bd)
            wc = sales * (dso / 365.0) * coc
            return margin - wc - opex - upfront

        cash_s = cash(sales_s, opex_s, upfront_s)
        cash_e = cash(sales_e, opex_e, upfront_e)
        cum += cash_e
        disc = 1.0 / (1 + coc) ** t
        rows.append(YearRow(year, eligible, acc_s_total, acc_e_total, f, treated_s, treated_e, lp, net_price_s,
                            cap_factor, sales_s, sales_e, opex_e, upfront_e, cash_s, cash_e, cum, cash_e * disc))

    # --- metrics -----------------------------------------------------------------------------
    p_reimb = sum(p["share_of_patients"] * p["p_coverage"] for p in payers) / max(sum(p["share_of_patients"] for p in payers), 1e-9)
    max_sales = max(r.net_sales_success for r in rows)
    peak_row = next(r for r in rows if r.net_sales_success >= 0.99 * max_sales)  # first year at plateau
    first_sale = next((r.year for r in rows if r.net_sales_success > 1000), None)
    payback = None
    if first_sale is not None:
        neg_seen = any(r.cum_cash_expected < 0 for r in rows)
        for r in rows:
            if r.year >= first_sale and r.cum_cash_expected >= 0 and neg_seen:
                payback = r.year - first_sale + 1
                break
            if r.year >= first_sale and r.cum_cash_expected >= 0 and not neg_seen:
                payback = 0
                break
    first_cov = min(coverage_t.values()) if coverage_t else None
    metrics = {
        "eligible": funnel.eligible,
        "eligible_low": funnel.eligible_low,
        "eligible_high": funnel.eligible_high,
        "peak_share": peak_share,
        "list_price_usd": list_price,
        "net_price_at_peak_usd": peak_row.net_price,
        "peak_year": peak_row.year,
        "peak_treated_success": peak_row.treated_success,
        "peak_treated_expected": max(r.treated_expected for r in rows),
        "peak_net_sales_success": peak_row.net_sales_success,
        "peak_net_sales_expected": max(r.net_sales_expected for r in rows),
        "cum_net_sales_expected": sum(r.net_sales_expected for r in rows),
        "cum_net_sales_success": sum(r.net_sales_success for r in rows),
        "rnpv_expected": sum(r.pv_cash_expected for r in rows),
        "npv_success": sum(r.cash_success / (1 + coc) ** (idx + 0.5) for idx, r in enumerate(rows)),
        "p_registration": p_reg,
        "p_reimbursement": p_reimb,
        "p_launch_success": p_reg * p_reimb,
        "first_sale_year": first_sale,
        "first_reimbursed_year": (start + first_cov) if first_cov is not None else None,
        "payback_years": payback,
        "budget_cap_years": cap_years,
        "budget_ceiling_usd": ceiling,
        "horizon": horizon,
        "start_year": start,
        "access_at_peak_success": peak_row.access_success,
        "persistence": persistence,
        "bad_debt_blended": sum(p["share_of_patients"] * p.get("bad_debt", 0) for p in covered) / cov_weight if cov_weight else 0.0,
        "indication": indication,
    }
    if cap_years:
        notes.append(f"Budget-impact ceiling (${ceiling/1e6:,.0f}m/yr public spend) binds in {cap_years[0]}-{cap_years[-1]}; "
                     f"modelled as a price-volume agreement that lowers the effective net price.")
    if erp.capped_by_origin:
        notes.append("ERP result capped at the country-of-origin price.")
    assumed = [r["country"] for r in erp.used if r.get("status") == "assumption"]
    if assumed:
        notes.append(f"ERP basket includes assumed EU prices ({', '.join(assumed)}); replace when Avanzanite lists in Europe.")

    payer_table = []
    for p in payers:
        payer_table.append({
            "id": p["id"], "name": p["name"], "share": p["share_of_patients"], "p": p["p_coverage"],
            "months": p["months_to_coverage"], "net": p["net_price_factor"], "dso": p.get("dso_days", 0),
            "bad_debt": p.get("bad_debt", 0.0),
            "coverage_year": (start + coverage_t[p["id"]]) if p["id"] in coverage_t else None,
            "note": p.get("note", ""),
        })
    return Forecast(country, asset, indication, funnel, erp, shares, peak_share, timeline, rows, metrics, notes, payer_table)
