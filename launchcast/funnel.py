"""Patient funnel: population -> prevalent disease -> diagnosed -> in care -> label-eligible."""
from __future__ import annotations

from dataclasses import dataclass, field

from .data import source_of, status_of, v


@dataclass
class FunnelStep:
    label: str
    factor: str          # human-readable factor applied
    value: float         # patients after this step
    status: str
    source: str = ""


@dataclass
class Funnel:
    steps: list[FunnelStep] = field(default_factory=list)
    eligible: float = 0.0
    eligible_low: float = 0.0
    eligible_high: float = 0.0
    segment_mix: dict = field(default_factory=dict)
    base_population: float = 0.0
    prevalent: float = 0.0
    diagnosed: float = 0.0
    in_care: float = 0.0


def patient_funnel(country: dict, indication: str, asset: dict | None = None) -> Funnel:
    """Build the funnel. The asset may override the label-eligible share (eligibility is a label
    property, not a country property) via indication.label_eligible_share_override."""
    pop = country["population"]
    epi = country["epidemiology"][indication]
    elig_node = epi["label_eligible_share"]
    if asset and asset.get("indication", {}).get("id") == indication and asset["indication"].get("label_eligible_share_override"):
        elig_node = asset["indication"]["label_eligible_share_override"]
    nationals = float(v(pop["nationals"]))
    adult_share = float(v(pop["adult_share_nationals"]))
    base = nationals * adult_share

    prev = epi["disease_prevalence_per_1000_adults"]
    prev_c = float(v(prev))
    overridden = isinstance(prev, dict) and prev.get("status") == "override"
    if isinstance(prev, dict) and not overridden:
        prev_lo = float(prev.get("low", prev_c * 0.6))
        prev_hi = float(prev.get("high", prev_c * 1.3))
    else:  # scalar or command-line override: the bundled range no longer applies
        prev_lo, prev_hi = prev_c * 0.6, prev_c * 1.3
    alpha = float(v(epi["alpha_thal_hbh_multiplier"]))
    dx = float(v(epi["diagnosed_share"]))
    care = float(v(epi["in_specialist_care_share"]))
    elig = float(v(elig_node))

    f = Funnel()
    f.base_population = base
    f.steps.append(FunnelStep("Adults in the epidemiology base", f"{nationals:,.0f} x {adult_share:.1%} adults", base,
                              status_of(pop["nationals"], "reported"), source_of(pop["nationals"])))
    prevalent = base * prev_c / 1000.0
    f.steps.append(FunnelStep("Prevalent disease (adults)", f"x {prev_c:g} per 1,000 adults", prevalent,
                              status_of(prev), source_of(prev)))
    prevalent_all = prevalent * alpha
    f.prevalent = prevalent_all
    f.steps.append(FunnelStep("Other label-covered forms (alpha-thal / HbH)", f"x {alpha:.2f}", prevalent_all,
                              status_of(epi["alpha_thal_hbh_multiplier"]), source_of(epi["alpha_thal_hbh_multiplier"])))
    diagnosed = prevalent_all * dx
    f.diagnosed = diagnosed
    f.steps.append(FunnelStep("Diagnosed", f"x {dx:.0%}", diagnosed, status_of(epi["diagnosed_share"]), source_of(epi["diagnosed_share"])))
    in_care = diagnosed * care
    f.in_care = in_care
    f.steps.append(FunnelStep("Followed in a specialist centre", f"x {care:.0%}", in_care,
                              status_of(epi["in_specialist_care_share"]), source_of(epi["in_specialist_care_share"])))
    eligible = in_care * elig
    criteria = elig_node.get("criteria", "") if isinstance(elig_node, dict) else ""
    f.steps.append(FunnelStep("Label-eligible" + (f" ({criteria})" if criteria else ""), f"x {elig:.0%}", eligible,
                              status_of(elig_node), source_of(elig_node)))
    f.eligible = eligible
    f.eligible_low = eligible * (prev_lo / prev_c) if prev_c else 0.0
    f.eligible_high = eligible * (prev_hi / prev_c) if prev_c else 0.0
    mix = epi.get("segment_mix", {})
    meta = {"status", "source", "note", "_comment"}
    mix = {k: float(v(x)) for k, x in mix.items() if k not in meta} if isinstance(mix, dict) else {}
    total = sum(mix.values())
    f.segment_mix = {k: x / total for k, x in mix.items()} if total else {}
    return f
