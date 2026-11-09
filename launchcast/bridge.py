"""Bridge between the originator's own stated numbers and this model's output."""
from __future__ import annotations

from .data import source_of, status_of, v
from .forecast import Forecast


def build_bridge(fc: Forecast) -> dict:
    asset, country, m = fc.asset, fc.country, fc.metrics
    bv = asset.get("biotech_view", {})
    code = country["code"]
    max_sales = max(r.net_sales_success for r in fc.rows)
    peak = next(r for r in fc.rows if r.net_sales_success >= 0.99 * max_sales)
    out: dict = {"label": bv.get("label", "Originator view"), "patient_steps": [], "price_steps": [],
                 "comparators": [], "agreements": [], "disagreements": [], "calibration": []}

    in_territory = code in asset.get("deal", {}).get("territory", [])
    us_price = float(v(bv.get("us_price_usd", 425000)))
    addressable = float(v(bv.get("us_launch_addressable_share", 0.65)))
    penetration = float(v(bv.get("implied_us_penetration_at_peak", 0.2)))

    steps = out["patient_steps"]
    if in_territory and "gcc_thalassemia_patients" in bv and fc.indication == asset["indication"]["id"]:
        gcc = float(v(bv["gcc_thalassemia_patients"]))
        share = float(v(bv["gcc_population_share_SA"]))
        implied = gcc * share
        steps.append({"label": "Originator: thalassemia patients in the GCC", "value": gcc, "status": status_of(bv["gcc_thalassemia_patients"]),
                      "note": source_of(bv["gcc_thalassemia_patients"])})
        steps.append({"label": f"Allocated to {country['name']} (population share {share:.0%})", "value": implied, "status": status_of(bv["gcc_population_share_SA"]),
                      "note": "All ages, all thalassemia forms, carriers possibly included in regional registries"})
        steps.append({"label": "Model: prevalent adults with disease (national screening rate)", "value": fc.funnel.prevalent, "status": "verified",
                      "note": f"{fc.funnel.prevalent/implied:.0%} of the allocated originator figure. The label is adults only; the screening-based rate (0.7/1000 adults) already excludes children and carriers."})
        naive_patients = implied
    else:
        steps.append({"label": "Model: prevalent adults with disease", "value": fc.funnel.prevalent, "status": "model", "note": "No originator figure for this country"})
        naive_patients = fc.funnel.prevalent
    steps.append({"label": "Diagnosed", "value": fc.funnel.diagnosed, "status": "model", "note": ""})
    steps.append({"label": "Followed in a specialist centre", "value": fc.funnel.in_care, "status": "model", "note": ""})
    steps.append({"label": "Label-eligible (adult, anemic, not cured)", "value": fc.funnel.eligible, "status": "model", "note": ""})
    steps.append({"label": f"With a paying route at peak ({peak.year}, if reimbursed)", "value": fc.funnel.eligible * peak.access_success, "status": "model",
                  "note": f"{peak.access_success:.0%} of eligible; uncovered and not-yet-listed payers excluded"})
    steps.append({"label": "Choosing this therapy (peak competitive share)", "value": fc.funnel.eligible * peak.access_success * fc.peak_share, "status": "model",
                  "note": f"{fc.peak_share:.0%} vs standard of care, luspatercept, gene therapy where available"})
    steps.append({"label": "Still on therapy (persistence)", "value": peak.treated_success, "status": "model",
                  "note": f"x {m['persistence']:.0%}; originator reports {v(bv.get('persistency_6m', {}), 0.75):.0%} 6-month persistency in the US"})

    ps = out["price_steps"]
    ps.append({"label": "Originator: US price per patient-year", "value": us_price, "status": status_of(bv.get("us_price_usd", {}), "company_stated")})
    ps.append({"label": f"Model: {country['name']} list price after external reference pricing", "value": m["list_price_usd"], "status": "model",
               "note": fc.erp.note})
    ps.append({"label": "Model: blended net price at peak (tenders, formulary discounts, budget cap, FX)", "value": peak.net_price, "status": "model",
               "note": ("budget-impact ceiling binding" if peak.budget_cap_factor < 1 else "budget-impact ceiling not binding")})

    comps = out["comparators"]
    naive_tam = naive_patients * us_price
    comps.append({"label": "Naive TAM: originator patient figure x US price", "value": naive_tam,
                  "note": "What a prevalence-times-US-price slide implies"})
    comps.append({"label": f"Originator US launch logic applied here: {addressable:.0%} addressable x {penetration:.0%} penetration x US price",
                  "value": naive_patients * addressable * penetration * us_price,
                  "note": "Agios' own US assumptions (65% addressable, ~20% implied net penetration) transplanted to this country"})
    comps.append({"label": f"Same US logic on the model's eligible pool ({fc.funnel.eligible:,.0f} x {addressable:.0%} x {penetration:.0%} x US price)",
                  "value": fc.funnel.eligible * addressable * penetration * us_price,
                  "note": "Isolates the price and access effects from the patient-count effect"})
    comps.append({"label": f"This model: peak net sales if reimbursed ({peak.year})", "value": peak.net_sales_success, "note": ""})
    comps.append({"label": "This model: peak net sales, probability-weighted", "value": m["peak_net_sales_expected"], "note": ""})

    # Where we disagree, and why
    dis = out["disagreements"]
    if in_territory and "gcc_thalassemia_patients" in bv:
        dis.append(f"Patient count. The 70,000 GCC figure is a headline prevalence across all ages and forms. The adult, anemic, in-care, "
                   f"label-eligible pool in {country['name']} is {fc.funnel.eligible:,.0f} ({fc.funnel.eligible/naive_patients:.0%} of the allocated figure). "
                   f"Saudi national screening data (0.7 beta-thalassemia disease per 1,000 adults screened, 2011-2015) is the anchor, not a regional registry.")
    dis.append(f"Price. US ${us_price:,.0f} is not a reference for {country['name']}: the ERP rule ({fc.erp.note}) gives ${m['list_price_usd']:,.0f} list, "
               f"and procurement discounts, early-access pricing and the budget ceiling bring the blended net to ${peak.net_price:,.0f} at peak "
               f"({peak.net_price/us_price:.0%} of US).")
    if code == "SA":
        dis.append(f"Timing. Agios guided 'national procurement agreements over the next couple of years' (Q3 2025). The model has the first institutional "
                   f"listings in {m['first_reimbursed_year']:.1f} and NUPCO coverage from {fc.timeline.start_year + fc.timeline.coverage_t.get('moh_nupco', 0):.1f}, "
                   f"with peak uptake only in {peak.year}. Revenue before that is early-access, hospital-budget business.")
    if m["budget_cap_years"]:
        dis.append(f"Budget impact. At the modelled patient numbers the public bill would exceed {v(country['budget_ceiling_share_of_pharma_market']):.1%} of national drug spend from "
                   f"{m['budget_cap_years'][0]}; the model assumes the payer forces a price-volume agreement rather than paying list for everyone. An originator deck rarely models this.")
    if code == "CO" or not in_territory:
        dis.append("Geography. The originator has not filed here and lists no partner; the model agrees with that revealed preference and shows why: "
                   f"a {fc.funnel.eligible:,.0f}-patient eligible pool, {m['p_launch_success']:.0%} probability of a paying route, "
                   f"{fc.country['regulatory']['agency']} review of ~{v(fc.country['regulatory']['typical_review_months']):.0f} months and {m['bad_debt_blended']:.0%} expected bad debt.")

    agr = out["agreements"]
    agr.append(f"Persistence: originator reports {v(bv.get('persistency_6m', {}), 0.75):.0%} at 6 months (US); the model uses {m['persistence']:.0%} annual on-therapy.")
    if code == "SA":
        agr.append("Saudi Arabia was worth an approval-first strategy: the model's verdict and Agios' sequencing (SFDA before FDA, NewBridge partnership) agree.")
        agr.append("NTDT is the larger patient segment and TDT the better-paying one; the model's segment shares reflect the same trial results Agios cites (ENERGIZE 42.3% vs 1.6%; ENERGIZE-T 30.4% vs 12.6%).")

    # Calibration against reported ex-US revenue
    exus = bv.get("ex_us_quarterly_revenue_usd", {})
    if code == "SA" and isinstance(v(exus), dict):
        q = v(exus)
        total_2026 = sum(q.values())
        model_2026 = next((r.net_sales_success for r in fc.rows if r.year == 2026), 0.0)
        model_2026_pat = next((r.treated_success for r in fc.rows if r.year == 2026), 0.0)
        out["calibration"].append(f"Agios ex-US net revenue reported so far in 2026 (EU + GCC combined): ${total_2026/1e6:,.1f}m across "
                                  f"{', '.join(q.keys())}. The model's 2026 Saudi in-market net sales (early access only) are ${model_2026/1e6:,.1f}m "
                                  f"(~{model_2026_pat:,.0f} patients on therapy). Saudi alone must stay below the ex-US total, which it does.")
    return out
