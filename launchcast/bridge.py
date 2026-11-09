"""Bridge between the originator's own stated numbers and this model's output.

Everything asset- or country-specific comes from the data files:
  asset.biotech_view: home_country, home_price_usd, home_launch_addressable_share,
                      implied_home_penetration_at_peak, persistency_6m, regional_patient_claims,
                      access_statements, reported_revenue, agreements
  asset.uptake.home_market_observed_share (optional): revealed uptake at home
  country.epidemiology.<ind>.disease_prevalence_per_1000_adults.anchor: one-line data anchor
"""
from __future__ import annotations

from .data import source_of, status_of, v
from .forecast import Forecast


def _peak(fc: Forecast):
    mx = max(r.net_sales_success for r in fc.rows)
    return next(r for r in fc.rows if r.net_sales_success >= 0.99 * mx)


def build_bridge(fc: Forecast) -> dict:
    asset, country, m = fc.asset, fc.country, fc.metrics
    bv = asset.get("biotech_view", {}) or {}
    code = country["code"]
    peak = _peak(fc)
    label = bv.get("label", f"{asset['originator'].split(' (')[0]}'s own numbers")
    out: dict = {"label": label, "patient_steps": [], "price_steps": [], "comparators": [],
                 "agreements": [], "disagreements": [], "calibration": []}

    home = bv.get("home_country", "US")
    home_price = v(bv.get("home_price_usd"))
    if home_price is None:  # fall back to the home reference price in the table
        home_price = next((r["annual_usd"] for r in asset["reference_prices"]
                           if r["country"] == home and r.get("indication") == asset["indication"]["id"] and r.get("annual_usd")), None)
    addressable = v(bv.get("home_launch_addressable_share"))
    penetration = v(bv.get("implied_home_penetration_at_peak"))
    epi = country["epidemiology"][fc.indication]
    anchor = epi["disease_prevalence_per_1000_adults"].get("anchor", "the country epidemiology inputs")
    in_territory = code in (asset.get("deal", {}) or {}).get("territory", [])

    # ---- patients ---------------------------------------------------------------------------------
    steps = out["patient_steps"]
    claim = None
    if fc.indication == asset["indication"]["id"]:
        claim = next((c for c in bv.get("regional_patient_claims", []) if code in c.get("country_shares", {})), None)
    if claim:
        share = float(claim["country_shares"][code])
        implied = float(claim["patients"]) * share
        steps.append({"label": f"Originator: {fc.indication} patients in {claim['region']}", "value": float(claim["patients"]),
                      "status": claim.get("status", "company_stated"), "note": claim.get("source", "")})
        steps.append({"label": f"Allocated to {country['name']} (share {share:.0%})", "value": implied, "status": "reported",
                      "note": (claim.get("shares_source", "") + " " + claim.get("basis_note", "")).strip()})
        steps.append({"label": "Model: prevalent adults with disease", "value": fc.funnel.prevalent, "status": status_of(epi["disease_prevalence_per_1000_adults"]),
                      "note": f"{fc.funnel.prevalent/implied:.0%} of the allocated originator figure. Anchor: {anchor}."})
        naive_patients = implied
    else:
        steps.append({"label": "Model: prevalent adults with disease", "value": fc.funnel.prevalent, "status": status_of(epi["disease_prevalence_per_1000_adults"]),
                      "note": f"No originator patient figure covers this country. Anchor: {anchor}."})
        naive_patients = fc.funnel.prevalent
    steps.append({"label": "Diagnosed", "value": fc.funnel.diagnosed, "status": "model", "note": ""})
    steps.append({"label": "Followed in a specialist centre", "value": fc.funnel.in_care, "status": "model", "note": ""})
    steps.append({"label": fc.funnel.steps[-1].label, "value": fc.funnel.eligible, "status": "model", "note": ""})
    steps.append({"label": f"With a paying route at peak ({peak.year}, if reimbursed)", "value": fc.funnel.eligible * peak.access_success, "status": "model",
                  "note": f"{peak.access_success:.0%} of eligible; uncovered and not-yet-listed payers excluded"})
    rivals = sorted({o.name.split(" (")[0] for seg in fc.shares.values() for o in seg.options
                     if o.id not in ("soc", asset["id"]) and o.availability != "none"})
    steps.append({"label": "Choosing this therapy (peak competitive share)", "value": fc.funnel.eligible * peak.access_success * fc.peak_share, "status": "model",
                  "note": f"{fc.peak_share:.0%} vs standard of care" + (f" and {', '.join(rivals)}" if rivals else "")})
    pers_note = f"x {m['persistence']:.0%}"
    if bv.get("persistency_6m"):
        pers_note += f"; originator reports {v(bv['persistency_6m']):.0%} 6-month persistency at home"
    steps.append({"label": "Still on therapy (persistence)", "value": peak.treated_success, "status": "model", "note": pers_note})

    # ---- price --------------------------------------------------------------------------------------
    ps = out["price_steps"]
    if home_price:
        ps.append({"label": f"Originator: {home} price per patient-year", "value": float(home_price),
                   "status": status_of(bv.get("home_price_usd"), "reported")})
    ps.append({"label": f"Model: {country['name']} list price after external reference pricing", "value": m["list_price_usd"], "status": "model", "note": fc.erp.note})
    ps.append({"label": "Model: blended net price at peak (tenders, formulary discounts, budget cap, FX)", "value": peak.net_price, "status": "model",
               "note": "budget-impact ceiling binding" if peak.budget_cap_factor < 1 else "budget-impact ceiling not binding"})

    # ---- revenue comparators -------------------------------------------------------------------------
    comps = out["comparators"]
    if home_price:
        comps.append({"label": f"Naive TAM: {'originator' if claim else 'prevalent'} patient figure x {home} price",
                      "value": naive_patients * home_price, "note": "What a prevalence-times-home-price slide implies"})
        if addressable and penetration:
            comps.append({"label": f"Originator {home} launch logic applied here: {addressable:.0%} addressable x {penetration:.0%} penetration x {home} price",
                          "value": naive_patients * addressable * penetration * home_price,
                          "note": "The originator's own home-market assumptions transplanted to this country"})
            comps.append({"label": f"Same logic on the model's eligible pool ({fc.funnel.eligible:,.0f} x {addressable:.0%} x {penetration:.0%} x {home} price)",
                          "value": fc.funnel.eligible * addressable * penetration * home_price,
                          "note": "Isolates the price and access effects from the patient-count effect"})
    comps.append({"label": f"This model: peak net sales if reimbursed ({peak.year})", "value": peak.net_sales_success, "note": ""})
    comps.append({"label": "This model: peak net sales, probability-weighted", "value": m["peak_net_sales_expected"], "note": ""})

    # ---- disagreements -------------------------------------------------------------------------------
    dis = out["disagreements"]
    if claim:
        dis.append(f"Patient count. The {claim['patients']:,.0f} {claim['region']} figure is a headline prevalence ({claim.get('basis_note', 'all ages and forms').lower()}). "
                   f"The label-eligible pool in {country['name']} is {fc.funnel.eligible:,.0f} ({fc.funnel.eligible/naive_patients:.0%} of the allocated figure). "
                   f"The anchor is {anchor}, not a regional registry.")
    if home_price:
        dis.append(f"Price. {home} ${home_price:,.0f} is not a reference for {country['name']}: the ERP rule ({fc.erp.note}) gives ${m['list_price_usd']:,.0f} list, "
                   f"and procurement discounts, early-access pricing and the budget ceiling bring the blended net to ${peak.net_price:,.0f} at peak "
                   f"({peak.net_price/home_price:.0%} of {home}).")
    stmt = (bv.get("access_statements") or {}).get(code)
    if stmt:
        public = [p for p in country["payers"] if p.get("public") and p["p_coverage"] > 0]
        biggest = max(public, key=lambda p: p["share_of_patients"]) if public else None
        big_year = fc.timeline.start_year + fc.timeline.coverage_t[biggest["id"]] if biggest else None
        dis.append(f"Timing. Originator: '{v(stmt)}' ({source_of(stmt) or 'company statement'}). The model has the first paying route in "
                   f"{m['first_reimbursed_year']:.1f}" + (f", {biggest['name'].split(' (')[0]} coverage from {big_year:.1f}" if biggest else "") +
                   f", and peak uptake only in {peak.year}. Revenue before that is early-access, hospital-budget business.")
    if m["budget_cap_years"]:
        dis.append(f"Budget impact. At the modelled patient numbers the public bill would exceed {v(country['budget_ceiling_share_of_pharma_market']):.1%} of national drug spend from "
                   f"{m['budget_cap_years'][0]}; the model assumes the payer forces a price-volume agreement rather than paying list for everyone. Originator decks rarely model this.")
    observed = (asset.get("uptake") or {}).get("home_market_observed_share")
    if observed and v(observed) is not None and fc.peak_share > v(observed) * 1.5:
        dis.append(f"Revealed uptake. At home the asset reached about {v(observed):.1%} of prevalent patients ({source_of(observed)}); the model's {fc.peak_share:.0%} peak share "
                   f"of label-eligible patients here ({fc.peak_share * fc.funnel.eligible / fc.funnel.prevalent:.1%} of prevalent) is far above that and rests on the "
                   f"competitive set and payer weights printed in the inputs. Treat it as the upper half of the range.")
    status = asset["regulatory_status"].get(code, {}).get("status", "not_filed")
    if status not in ("approved", "filed") and not in_territory:
        dis.append(f"Geography. The originator has not filed here and lists no partner; the model agrees with that revealed preference and shows why: "
                   f"a {fc.funnel.eligible:,.0f}-patient eligible pool, {m['p_launch_success']:.0%} probability of a paying route, "
                   f"{country['regulatory']['agency']} review of ~{v(country['regulatory']['typical_review_months']):.0f} months and {m['bad_debt_blended']:.0%} expected bad debt.")

    # ---- agreements ------------------------------------------------------------------------------------
    agr = out["agreements"]
    if bv.get("persistency_6m"):
        agr.append(f"Persistence: originator reports {v(bv['persistency_6m']):.0%} at 6 months at home; the model uses {m['persistence']:.0%} annual on-therapy.")
    for line in (bv.get("agreements") or {}).get(code, []) + (bv.get("agreements") or {}).get("*", []):
        agr.append(line)
    if not agr:
        agr.append("No originator statements about this country were found to agree or disagree with beyond price.")

    # ---- calibration -----------------------------------------------------------------------------------
    rev = bv.get("reported_revenue")
    if rev and code in rev.get("covers", []):
        periods = rev.get("periods", {})
        total = sum(periods.values())
        first_year = min(r.year for r in fc.rows if r.net_sales_success > 0) if any(r.net_sales_success > 0 for r in fc.rows) else None
        if first_year is not None:
            row = next(r for r in fc.rows if r.year == first_year)
            out["calibration"].append(f"Originator-reported {rev['label']}: ${total/1e6:,.1f}m across {', '.join(periods.keys())} ({rev.get('source', '')}). "
                                      f"The model's {first_year} {country['name']} in-market net sales are ${row.net_sales_success/1e6:,.1f}m "
                                      f"(~{row.treated_success:,.0f} patients on therapy). This country alone must stay below the reported total; "
                                      f"it {'does' if row.net_sales_success < total else 'does NOT, so the early-access share is too high'}.")
    return out
