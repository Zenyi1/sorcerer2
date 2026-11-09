"""Launch verdict rules. Hard rules decide go / no-go; soft rules make a go conditional."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleResult:
    rule: str
    value: str
    threshold: str
    passed: bool
    hard: bool


def evaluate(metrics: dict, rules: dict) -> tuple[str, list[RuleResult]]:
    out: list[RuleResult] = []
    rnpv = metrics["rnpv_expected"]
    out.append(RuleResult("Risk-adjusted NPV (expected)", f"${rnpv/1e6:,.1f}m", f">= ${rules['min_rnpv_usd']/1e6:,.0f}m",
                          rnpv >= rules["min_rnpv_usd"], True))
    peak = metrics["peak_net_sales_success"]
    out.append(RuleResult("Peak net sales if reimbursed", f"${peak/1e6:,.1f}m", f">= ${rules['min_peak_net_sales_usd']/1e6:,.0f}m",
                          peak >= rules["min_peak_net_sales_usd"], True))
    p = metrics["p_launch_success"]
    out.append(RuleResult("P(registered and reimbursed)", f"{p:.0%}", f">= {rules['min_p_reimbursement']:.0%}",
                          p >= rules["min_p_reimbursement"], True))
    pb = metrics["payback_years"]
    out.append(RuleResult("Payback from first sale", "none in horizon" if pb is None else ("immediate" if pb == 0 else f"{pb} yr"),
                          f"<= {rules['max_payback_years_from_first_sale']} yr",
                          pb is not None and pb <= rules["max_payback_years_from_first_sale"], False))
    pts = metrics["peak_treated_success"]
    out.append(RuleResult("Patients on therapy at peak", f"{pts:,.0f}", f">= {rules['min_peak_patients']}",
                          pts >= rules["min_peak_patients"], False))
    hard_fail = any(not r.passed and r.hard for r in out)
    soft_fail = any(not r.passed and not r.hard for r in out)
    verdict = "DO NOT LAUNCH" if hard_fail else ("CONDITIONAL" if soft_fail else "LAUNCH")
    return verdict, out
