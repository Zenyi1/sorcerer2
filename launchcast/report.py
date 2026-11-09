"""Plain-text rendering. ASCII only, ~100 columns, no colour, no UI."""
from __future__ import annotations

from .data import STATUS_LEGEND, source_of, status_of, v
from .competition import STATUS_QUO_BONUS
from .forecast import Forecast

WIDTH = 104


def money(x: float, decimals: int = 1) -> str:
    if x is None:
        return "-"
    neg = x < 0
    x = abs(x)
    if x >= 1e9:
        s = f"${x/1e9:,.{decimals}f}bn"
    elif x >= 1e6:
        s = f"${x/1e6:,.{decimals}f}m"
    elif x >= 1e3:
        s = f"${x/1e3:,.0f}k"
    else:
        s = f"${x:,.0f}"
    return f"-{s}" if neg else s


def pct(x: float, decimals: int = 0) -> str:
    return "-" if x is None else f"{x*100:.{decimals}f}%"


def num(x: float, decimals: int = 0) -> str:
    return "-" if x is None else f"{x:,.{decimals}f}"


def hr(title: str = "", char: str = "=") -> str:
    if not title:
        return char * WIDTH
    pad = WIDTH - len(title) - 4
    return f"{char*2} {title} {char*max(pad,2)}"


def table(headers: list[str], rows: list[list[str]], aligns: str | None = None, indent: int = 2) -> str:
    cols = len(headers)
    aligns = aligns or ("l" * cols)
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(str(cell)))
    def fmt(r):
        cells = []
        for i, cell in enumerate(r):
            s = str(cell)
            cells.append(s.ljust(widths[i]) if aligns[i] == "l" else s.rjust(widths[i]))
        return " " * indent + "  ".join(cells)
    sep = " " * indent + "  ".join("-" * w for w in widths)
    return "\n".join([fmt(headers), sep] + [fmt(r) for r in rows])


def wrap(text: str, width: int = WIDTH - 4, indent: int = 2) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(" " * indent + l for l in lines)


def tag(status: str) -> str:
    return {"verified": "[V]", "reported": "[R]", "company_stated": "[C]", "assumption": "[A]", "override": "[O]",
            "model": "[M]", "unknown": "[?]"}.get(status, f"[{status[:1].upper()}]")


def legend() -> str:
    lines = ["  Evidence grades: [V] verified primary source  [R] reported/secondary  [C] originator's own figure  "
             "[A] our assumption  [O] command-line override  [M] model output"]
    return "\n".join(lines)


def _pb(years) -> str:
    if years is None:
        return "none in horizon"
    return "immediate" if years == 0 else f"{years} yr"


# ---------------------------------------------------------------------------------------------------- sections

def render_header(fc: Forecast, config: dict) -> str:
    a, c = fc.asset, fc.country
    lines = [hr(), f"  LAUNCHCAST  |  {a['name']}  |  {c['name']} ({c['code']})  |  indication: {fc.indication}",
             wrap(f"Originator: {a['originator']}. Deal: {a['deal']['type']} with {a['deal']['partner']} ({a['deal']['signed']}).", indent=2),
             wrap(f"Perspective: launch partner P&L. Horizon: {config['analysis_start_year']}-{config['analysis_start_year']+config['horizon_years']-1}. "
                  f"Status here: {fc.timeline.approval_label}.", indent=2), hr(), legend()]
    return "\n".join(lines)


def render_inputs(fc: Forecast) -> str:
    c, a = fc.country, fc.asset
    out = [hr("INPUTS", "-"), ""]
    # 1 epidemiology
    out.append("  1. EPIDEMIOLOGY AND PREVALENCE -> label-eligible patients")
    rows = [[s.label, s.factor, num(s.value), tag(s.status)] for s in fc.funnel.steps]
    out.append(table(["Step", "Factor", "Patients", "Grade"], rows, "lllr"))
    f = fc.funnel
    mix_txt = ", ".join(f"{k} {pct(x)}" for k, x in f.segment_mix.items()) if len(f.segment_mix) > 1 else "single segment"
    out.append(f"  Range on prevalence alone: {num(f.eligible_low)} - {num(f.eligible_high)} eligible adults; "
               f"segment mix: {mix_txt}.")
    for s in fc.funnel.steps:
        if s.source:
            out.append(wrap(f"- {s.label}: {s.source}", indent=6))
    out.append(wrap(f"Base note: {c['population'].get('base_note','')}", indent=4))
    out.append("")
    # 2 reimbursement
    out.append("  2. REIMBURSEMENT AND MARKET ACCESS")
    reg = c["regulatory"]
    out.append(wrap(f"Regulator: {reg['agency']}. {reg['pathway']}. Typical review {v(reg['typical_review_months']):.0f} months "
                    f"{tag(status_of(reg['typical_review_months']))}; P(approval | FDA/EMA approved) {pct(v(reg['p_approval_given_fda_ema']))} "
                    f"{tag(status_of(reg['p_approval_given_fda_ema']))}.", indent=4))
    out.append(wrap(f"System: {c['health_system']['summary']}", indent=4))
    rows = []
    for p in fc.payer_table:
        rows.append([p["name"][:58], pct(p["share"]), pct(p["p"]), f"{p['months']}" if p["p"] > 0 else "-",
                     f"{p['coverage_year']:.1f}" if p["coverage_year"] else "-", pct(p["net"]) if p["p"] > 0 else "-",
                     f"{p['dso']}" if p["p"] > 0 else "-", pct(p["bad_debt"]) if p["p"] > 0 else "-"])
    out.append(table(["Payer route", "Patients", "P(cover)", "Months", "From", "Net/list", "DSO d", "Bad debt"], rows, "lrrrrrrr"))
    for p in fc.payer_table:
        if p["note"]:
            out.append(wrap(f"- {p['id']}: {p['note']}", indent=6))
    out.append(f"  Early access before listing: {pct(v(c['early_access_share']))} of eligible {tag(status_of(c['early_access_share']))}. "
               f"Blended P(a patient has a paying route) = {pct(fc.metrics['p_reimbursement'])}.")
    out.append("")
    # 3 competition
    out.append("  3. COMPETING THERAPIES -> peak share model (multinomial logit on efficacy, convenience, safety, price)")
    w = fc.country["competition_weights"]
    out.append(f"  Payer utility weights here: efficacy {w['efficacy']}, convenience {w['convenience']}, safety {w['safety']}, "
               f"price {w['price']} {tag(status_of(w))}; standard of care gets a status-quo bonus of {STATUS_QUO_BONUS:g}.")
    for seg_name, seg in fc.shares.items():
        rows = []
        for o in seg.options:
            rows.append([f"{seg_name}" if o is seg.options[0] else "", o.name[:52], o.availability,
                         f"{o.efficacy:.2f}", f"{o.convenience:.2f}", f"{o.safety:.2f}",
                         money(o.price_usd, 0) if o.price_usd else "-",
                         pct(o.share, 1) if o.availability != "none" else "n/a", "cap" if o.capped else ""])
        out.append(table(["Seg", "Therapy", "Here", "Eff", "Conv", "Safe", "Price/yr", "Share", ""], rows, "lllrrrrrl"))
    blend = " + ".join(f"{sg} {pct(fc.shares[sg].asset_share, 1)} x {pct(f.segment_mix.get(sg, 1.0))}" for sg in fc.shares)
    out.append(f"  Blended peak share of label-eligible patients = {pct(fc.peak_share, 1)} ({blend}).")
    for seg_name, comps in (a["competitors"] if fc.indication == a["indication"]["id"] else a["pipeline_indications"][fc.indication]["competitors"]).items():
        for comp in comps:
            if comp.get("source"):
                out.append(wrap(f"- {comp['name']}: {comp['source']}", indent=6))
    out.append("")
    # 4 pricing
    out.append("  4. PRICING REFERENCES -> external reference price")
    pr = c["pricing"]
    out.append(wrap(f"Rule: {pr['authority']}; statistic '{pr['statistic']}' over basket {', '.join(pr['basket'])}; "
                    f"origin-country cap: {pr.get('origin_country_cap')}. {pr.get('notes','')}", indent=4))
    rows = []
    for r in a["reference_prices"]:
        used = any(u is r for u in fc.erp.used)
        why = next((e["reason"] for e in fc.erp.excluded if e.get("country") == r["country"] and e.get("indication") == r.get("indication") and e.get("brand") == r.get("brand")), "")
        rows.append([r["country"], r.get("indication", ""), r.get("brand", "") or "", money(r["annual_usd"], 0) if r.get("annual_usd") else "unknown",
                     tag(r.get("status", "assumption")), "used" if used else why])
    out.append(table(["Ctry", "Indication", "Brand", "USD/yr", "Grade", "In basket?"], rows, "llllll"))
    fx = v(c["fx_per_usd"])
    out.append(f"  ERP result: {money(fc.erp.list_price_usd, 0)} per patient-year list ({fc.erp.note}) = "
               f"{c['currency']} {fc.erp.list_price_usd*fx:,.0f} at {fx:g} {c['currency']}/USD {tag(status_of(c['fx_per_usd']))}. "
               f"Standard of care costs {money(v(c['epidemiology'][fc.indication]['soc_annual_cost_usd']),0)}/yr {tag(status_of(c['epidemiology'][fc.indication]['soc_annual_cost_usd']))}.")
    for r in a["reference_prices"]:
        out.append(wrap(f"- {r['country']} {r.get('brand') or r.get('indication')}: {r.get('source','')}", indent=6))
    out.append("")
    # 5 economics
    com = c["commercial"]
    out.append("  5. LAUNCH ECONOMICS (partner view)")
    out.append(wrap(f"Transfer price to originator {pct(v(com['transfer_price_share_of_net']))} of net sales {tag(status_of(com['transfer_price_share_of_net']))}; "
                    f"logistics {pct(com.get('logistics_share_of_net',0))}; launch opex {money(v(com['launch_opex_usd_per_year']),2)}/yr "
                    f"{tag(status_of(com['launch_opex_usd_per_year']))}; pre-launch opex {money(com.get('prelaunch_opex_usd_per_year',0),2)}/yr; "
                    f"upfront: " + "; ".join(f"{i['label']} {money(i['amount'],2)} at {i['timing']}" for i in com.get('upfront_costs_usd', [])) +
                    f". Cost of capital {pct(com.get('cost_of_capital',0.1))}. Persistence {pct(v(com['persistence_annual']))} {tag(status_of(com['persistence_annual']))}. "
                    f"Budget-impact ceiling {pct(v(c['budget_ceiling_share_of_pharma_market']),1)} of a {money(v(c['macro']['pharma_market_usd']),1)} drug market "
                    f"= {money(fc.metrics['budget_ceiling_usd'],0)}/yr public spend {tag(status_of(c['budget_ceiling_share_of_pharma_market']))}.", indent=4))
    return "\n".join(out)


def render_forecast(fc: Forecast, verdict: str, rules: list) -> str:
    m = fc.metrics
    out = [hr("OUTPUT: 10-YEAR FORECAST", "-"), ""]
    rows = []
    for r in fc.rows:
        rows.append([str(r.year), num(r.eligible), pct(r.access_success), pct(r.uptake), num(r.treated_success), num(r.treated_expected),
                     money(r.net_price, 0), money(r.net_sales_success), money(r.net_sales_expected), money(r.cash_expected), money(r.cum_cash_expected)])
    out.append(table(["Year", "Eligible", "Access", "Uptake", "Pts(succ)", "Pts(exp)", "Net $/pt", "Sales(succ)", "Sales(exp)", "Cash(exp)", "Cum cash"],
                     rows, "lrrrrrrrrrr"))
    out.append("  'succ' = if registered and every modelled payer route pays; 'exp' = probability-weighted (registration x coverage).")
    if fc.notes:
        for n in fc.notes:
            out.append(wrap(f"Note: {n}", indent=4))
    out.append("")
    out.append("  KEY METRICS")
    kv = [
        ["Label-eligible adults (range)", f"{num(m['eligible'])} ({num(m['eligible_low'])} - {num(m['eligible_high'])})"],
        ["Peak competitive share", pct(m["peak_share"], 1)],
        ["List price (ERP) / net at peak", f"{money(m['list_price_usd'],0)} / {money(m['net_price_at_peak_usd'],0)} per patient-year"],
        ["First sale / first reimbursed sale", f"{m['first_sale_year']} / {m['first_reimbursed_year']:.1f}" if m["first_reimbursed_year"] else f"{m['first_sale_year']} / -"],
        ["Patients on therapy at peak (succ / exp)", f"{num(m['peak_treated_success'])} / {num(m['peak_treated_expected'])} in {m['peak_year']}"],
        ["Peak net sales (succ / exp)", f"{money(m['peak_net_sales_success'])} / {money(m['peak_net_sales_expected'])}"],
        ["Cumulative net sales, horizon (exp)", money(m["cum_net_sales_expected"])],
        ["P(registration) x P(paying route)", f"{pct(m['p_registration'])} x {pct(m['p_reimbursement'])} = {pct(m['p_launch_success'])}"],
        ["Risk-adjusted NPV (exp) / NPV (succ)", f"{money(m['rnpv_expected'])} / {money(m['npv_success'])}"],
        ["Payback from first sale", "none within horizon" if m["payback_years"] is None else ("immediate (no cumulative loss)" if m["payback_years"] == 0 else f"{m['payback_years']} years")],
    ]
    out.append(table(["Metric", "Value"], [[k, s] for k, s in kv], "ll"))
    out.append("")
    out.append(f"  VERDICT: {verdict}")
    rows = [[r.rule, r.value, r.threshold, "pass" if r.passed else "FAIL", "hard" if r.hard else "soft"] for r in rules]
    out.append(table(["Rule", "Value", "Threshold", "Result", "Type"], rows, "lllll"))
    return "\n".join(out)


def render_compare(a: Forecast, b: Forecast, va: str, vb: str, decomposition: list[dict]) -> str:
    out = [hr(f"COMPARE: {a.country['name']} vs {b.country['name']}", "-"), ""]
    ma, mb = a.metrics, b.metrics
    rows = [
        ["Verdict", va, vb],
        ["Status", a.timeline.approval_label[:48], b.timeline.approval_label[:48]],
        ["Label-eligible adults", num(ma["eligible"]), num(mb["eligible"])],
        ["P(registered) x P(paying route)", pct(ma["p_launch_success"]), pct(mb["p_launch_success"])],
        ["First reimbursed sale", f"{ma['first_reimbursed_year']:.1f}" if ma["first_reimbursed_year"] else "-", f"{mb['first_reimbursed_year']:.1f}" if mb["first_reimbursed_year"] else "-"],
        ["List price (ERP)", money(ma["list_price_usd"], 0), money(mb["list_price_usd"], 0)],
        ["Net price at peak", money(ma["net_price_at_peak_usd"], 0), money(mb["net_price_at_peak_usd"], 0)],
        ["Peak share", pct(ma["peak_share"], 1), pct(mb["peak_share"], 1)],
        ["Patients at peak (succ)", num(ma["peak_treated_success"]), num(mb["peak_treated_success"])],
        ["Peak net sales (succ / exp)", f"{money(ma['peak_net_sales_success'])} / {money(ma['peak_net_sales_expected'])}", f"{money(mb['peak_net_sales_success'])} / {money(mb['peak_net_sales_expected'])}"],
        ["Risk-adjusted NPV", money(ma["rnpv_expected"]), money(mb["rnpv_expected"])],
        ["Payback", _pb(ma["payback_years"]), _pb(mb["payback_years"])],
        ["Expected bad debt", pct(ma["bad_debt_blended"]), pct(mb["bad_debt_blended"])],
    ]
    out.append(table(["", a.country["name"], b.country["name"]], rows, "lll"))
    out.append("")
    out.append(f"  WHY: multiplicative decomposition of peak-year net sales ({a.country['code']} / {b.country['code']})")
    rows = []
    for d in decomposition:
        fmt = {"patients": lambda x: num(x), "pct": lambda x: pct(x, 1), "usd": lambda x: money(x, 0), "years": lambda x: f"{x:.1f}"}[d["unit"]]
        if d["ratio"] != d["ratio"]:  # nan
            ratio = ""
        else:
            ratio = "inf" if d["ratio"] == float("inf") else f"{d['ratio']:.2f}x"
        rows.append([d["factor"], fmt(d["a"]), fmt(d["b"]), ratio])
    out.append(table(["Factor", a.country["code"], b.country["code"], "Ratio"], rows, "lrrr"))
    out.append(wrap("The factor ratios above the '=' line multiply to the peak-sales ratio, so the gap can be attributed line by line. "
                    "Memo lines are not in the product: collections hit cash rather than sales, and timing hits the NPV through the "
                    "years lost to registration and listing.", indent=4))
    return "\n".join(out)


def render_bridge(fc: Forecast, bridge: dict) -> str:
    out = [hr(f"WHERE THE MODEL DISAGREES WITH {bridge['label'].upper()}", "-"), ""]
    out.append("  Patients")
    rows = [[s["label"], num(s["value"]), tag(s["status"]) if s["status"] != "model" else "[M]"] for s in bridge["patient_steps"]]
    out.append(table(["Step", "Patients", "Grade"], rows, "lrr"))
    for s in bridge["patient_steps"]:
        if s.get("note"):
            out.append(wrap(f"- {s['label']}: {s['note']}", indent=6))
    out.append("")
    out.append("  Price per patient-year")
    rows = [[s["label"], money(s["value"], 0), tag(s["status"]) if s["status"] != "model" else "[M]"] for s in bridge["price_steps"]]
    out.append(table(["Step", "USD", "Grade"], rows, "lrr"))
    for s in bridge["price_steps"]:
        if s.get("note"):
            out.append(wrap(f"- {s['label']}: {s['note']}", indent=6))
    out.append("")
    out.append("  Revenue comparators")
    rows = [[c["label"], money(c["value"])] for c in bridge["comparators"]]
    out.append(table(["View", "Per year"], rows, "lr"))
    out.append("")
    out.append("  Disagreements, and why")
    for i, d in enumerate(bridge["disagreements"], 1):
        out.append(wrap(f"{i}. {d}", indent=4))
    out.append("")
    out.append("  Agreements")
    for d in bridge["agreements"]:
        out.append(wrap(f"- {d}", indent=4))
    if bridge["calibration"]:
        out.append("")
        out.append("  Calibration")
        for d in bridge["calibration"]:
            out.append(wrap(f"- {d}", indent=4))
    return "\n".join(out)


def render_tornado(fc: Forecast, tor: dict, top: int = 14) -> str:
    out = [hr(f"SENSITIVITY: {fc.country['name']} risk-adjusted NPV (base {money(tor['base'])})", "-"), ""]
    res = tor["results"][:top]
    if not res:
        return "\n".join(out + ["  (no sensitivity parameters resolved)"])
    maxswing = max(r["swing"] for r in res) or 1.0
    rows = []
    for r in res:
        bar_len = int(round(30 * r["swing"] / maxswing))
        rows.append([r["label"], money(r["low"]), money(r["high"]), "#" * bar_len, "FLIPS" if r["flips"] else ""])
    out.append(table(["Driver", "Low case", "High case", "Swing", "Verdict"], rows, "lrrll"))
    out.append(wrap("'Low case' is the unfavourable end of each driver's range, 'High case' the favourable end; 'FLIPS' marks drivers that "
                    "change the sign of the NPV on their own.", indent=4))
    return "\n".join(out)
