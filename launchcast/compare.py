"""Side-by-side of two forecasts and a multiplicative decomposition of the revenue gap."""
from __future__ import annotations

from .forecast import Forecast


def decompose(a: Forecast, b: Forecast) -> list[dict]:
    """Peak-year (success case) revenue = eligible x access x share x uptake x persistence x net price.

    Returns one row per factor with both values and the A/B ratio; the product of the factor ratios equals
    the ratio of peak net sales. Memo lines (collections, timing) are shown but not part of the product.
    """
    def peak(fc):
        mx = max(r.net_sales_success for r in fc.rows)
        return next(r for r in fc.rows if r.net_sales_success >= 0.99 * mx)
    ra, rb = peak(a), peak(b)
    pa, pb = a.metrics, b.metrics
    factors = [
        ("Label-eligible adults (peak year)", ra.eligible, rb.eligible, "patients"),
        ("Share with a paying route at peak", ra.access_success, rb.access_success, "pct"),
        ("Peak competitive share", a.peak_share, b.peak_share, "pct"),
        ("Uptake reached by peak year", ra.uptake, rb.uptake, "pct"),
        ("Persistence on therapy", pa["persistence"], pb["persistence"], "pct"),
        ("Net price per patient-year", ra.net_price, rb.net_price, "usd"),
    ]
    rows = []
    for label, va, vb, unit in factors:
        ratio = (va / vb) if vb else float("inf")
        rows.append({"factor": label, "a": va, "b": vb, "ratio": ratio, "unit": unit, "in_product": True})
    rows.append({"factor": "= Peak net sales (success case)", "a": ra.net_sales_success, "b": rb.net_sales_success,
                 "ratio": (ra.net_sales_success / rb.net_sales_success) if rb.net_sales_success else float("inf"), "unit": "usd", "in_product": False})
    rows.append({"factor": "memo: collected share (1 - bad debt)", "a": 1 - pa["bad_debt_blended"], "b": 1 - pb["bad_debt_blended"],
                 "ratio": (1 - pa["bad_debt_blended"]) / (1 - pb["bad_debt_blended"]), "unit": "pct", "in_product": False})
    rows.append({"factor": "memo: years from decision to first reimbursed sale", "a": (pa["first_reimbursed_year"] or 0) - pa["start_year"],
                 "b": (pb["first_reimbursed_year"] or 0) - pb["start_year"], "ratio": float("nan"), "unit": "years", "in_product": False})
    return rows
