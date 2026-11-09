"""Regression and unit tests. Run with: python3 -m unittest discover -s tests -v"""
from __future__ import annotations

import copy
import io
import json
import math
import unittest
from contextlib import redirect_stdout

from launchcast import cli
from launchcast.compare import decompose
from launchcast.competition import segment_shares
from launchcast.data import apply_overrides, load_asset, load_config, load_country
from launchcast.decision import evaluate
from launchcast.forecast import _uptake, run_forecast
from launchcast.funnel import patient_funnel
from launchcast.pricing import erp_price, percentile, statistic
from launchcast.sensitivity import tornado
from launchcast.validate import validate_asset, validate_country


class PricingTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        self.assertAlmostEqual(percentile([10, 20, 30, 40], 0.5), 25.0)
        self.assertAlmostEqual(percentile([10, 20, 30, 40], 0.25), 17.5)
        self.assertEqual(percentile([7], 0.9), 7)

    def test_statistics(self):
        vals = [1.0, 2.0, 3.0, 10.0]
        self.assertEqual(statistic(vals, "min"), 1.0)
        self.assertEqual(statistic(vals, "median"), 2.5)
        self.assertEqual(statistic(vals, "p25"), 1.75)
        with self.assertRaises(ValueError):
            statistic(vals, "bogus")

    def test_erp_uses_basket_and_origin_cap(self):
        refs = [
            {"country": "US", "indication": "x", "annual_usd": 100, "status": "company_stated"},
            {"country": "DE", "indication": "x", "annual_usd": 120, "status": "assumption"},
            {"country": "FR", "indication": "x", "annual_usd": 50, "status": "assumption"},
            {"country": "BR", "indication": "x", "annual_usd": 10, "status": "verified"},  # not in basket
            {"country": "JP", "indication": "y", "annual_usd": 5, "status": "verified"},   # other indication
        ]
        pricing = {"basket": ["US", "DE", "FR", "JP"], "statistic": "median", "origin_country_cap": True}
        res = erp_price(pricing, refs, "US", True, "x")
        self.assertEqual(len(res.used), 3)
        self.assertAlmostEqual(res.list_price_usd, 100.0)  # median of 50, 100, 120
        pricing["statistic"] = "max"  # 120 > origin 100 -> capped
        res = erp_price(pricing, refs, "US", True, "x")
        self.assertTrue(res.capped_by_origin)
        self.assertAlmostEqual(res.list_price_usd, 100.0)
        # excluding assumed prices leaves only the origin price
        res = erp_price({**pricing, "statistic": "min"}, refs, "US", False, "x")
        self.assertAlmostEqual(res.list_price_usd, 100.0)


class FunnelTests(unittest.TestCase):
    def test_saudi_funnel_arithmetic(self):
        c = load_country("SA")
        f = patient_funnel(c, "thalassemia")
        base = 19_600_000 * 0.665
        expected = base * 0.7 / 1000 * 1.12 * 0.90 * 0.65 * 0.60
        self.assertAlmostEqual(f.eligible, expected, places=3)
        self.assertLess(f.eligible_low, f.eligible)
        self.assertGreater(f.eligible_high, f.eligible)
        self.assertEqual(len(f.steps), 6)


class CompetitionTests(unittest.TestCase):
    def test_shares_sum_to_one_and_cap_applies(self):
        a = load_asset("mitapivat")
        seg = segment_shares(a["competitors"]["TDT"], "SA", {"efficacy": 2.5, "convenience": 1, "safety": 1, "price": 0.8}, "mitapivat", 190_000)
        live = [o for o in seg.options if o.availability != "none"]
        self.assertAlmostEqual(sum(o.share for o in live), 1.0, places=6)
        exa = next(o for o in seg.options if o.id == "exacel")
        self.assertTrue(exa.capped)
        self.assertAlmostEqual(exa.share, 0.03)

    def test_unavailable_option_gets_zero(self):
        a = load_asset("mitapivat")
        seg = segment_shares(a["competitors"]["TDT"], "CO", {"efficacy": 2.5, "convenience": 1, "safety": 1, "price": 1.6}, "mitapivat", 200_000)
        exa = next(o for o in seg.options if o.id == "exacel")
        self.assertEqual(exa.share, 0.0)

    def test_higher_price_weight_lowers_asset_share(self):
        a = load_asset("mitapivat")
        lo = segment_shares(a["competitors"]["NTDT"], "SA", {"efficacy": 2.5, "convenience": 1, "safety": 1, "price": 0.8}, "mitapivat", 200_000).asset_share
        hi = segment_shares(a["competitors"]["NTDT"], "SA", {"efficacy": 2.5, "convenience": 1, "safety": 1, "price": 1.6}, "mitapivat", 200_000).asset_share
        self.assertLess(hi, lo)


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.asset = load_asset("mitapivat")
        self.sa = run_forecast(load_country("SA"), self.asset, self.config)
        self.co = run_forecast(load_country("CO"), self.asset, self.config)

    def test_uptake_curve_endpoints(self):
        self.assertAlmostEqual(_uptake(0.0, 5), 0.05, places=6)
        self.assertAlmostEqual(_uptake(5.0, 5), 0.95, places=6)
        self.assertEqual(_uptake(-1.0, 5), 0.0)

    def test_saudi_launch_colombia_no(self):
        v_sa, _ = evaluate(self.sa.metrics, self.config["decision_rules"])
        v_co, rules_co = evaluate(self.co.metrics, self.config["decision_rules"])
        self.assertEqual(v_sa, "LAUNCH")
        self.assertEqual(v_co, "DO NOT LAUNCH")
        self.assertTrue(any(not r.passed and r.hard for r in rules_co))
        self.assertGreater(self.sa.metrics["rnpv_expected"], 0)
        self.assertLess(self.co.metrics["rnpv_expected"], 0)

    def test_expected_never_exceeds_success(self):
        for fc in (self.sa, self.co):
            for r in fc.rows:
                self.assertLessEqual(r.net_sales_expected, r.net_sales_success + 1e-6)
                self.assertLessEqual(r.treated_expected, r.treated_success + 1e-6)

    def test_saudi_already_approved_colombia_not(self):
        self.assertTrue(self.sa.timeline.already_approved)
        self.assertEqual(self.sa.metrics["p_registration"], 1.0)
        self.assertFalse(self.co.timeline.already_approved)
        self.assertLess(self.co.metrics["p_registration"], 1.0)
        self.assertGreater(self.co.metrics["first_reimbursed_year"], 2030)

    def test_budget_cap_binds_in_saudi_only(self):
        self.assertTrue(self.sa.metrics["budget_cap_years"])
        self.assertFalse(self.co.metrics["budget_cap_years"])

    def test_decomposition_multiplies_through(self):
        rows = decompose(self.sa, self.co)
        product = 1.0
        for r in rows:
            if r["in_product"]:
                product *= r["ratio"]
        sales = next(r for r in rows if r["factor"].startswith("="))
        self.assertAlmostEqual(product / sales["ratio"], 1.0, places=2)

    def test_segment_mix_is_generic(self):
        self.assertEqual(set(self.sa.funnel.segment_mix), {"TDT", "NTDT"})
        self.assertAlmostEqual(sum(self.sa.funnel.segment_mix.values()), 1.0)
        expected = sum(self.sa.funnel.segment_mix[s] * self.sa.shares[s].asset_share for s in self.sa.shares)
        self.assertAlmostEqual(self.sa.peak_share, expected)

    def test_second_asset_runs_without_code_changes(self):
        endari = load_asset("endari")
        sa = run_forecast(load_country("SA"), endari, self.config)
        co = run_forecast(load_country("CO"), endari, self.config)
        self.assertEqual(sa.indication, "SCD")
        self.assertEqual(sa.funnel.segment_mix, {"SCD": 1.0})           # single-segment asset needs no mix
        self.assertFalse(sa.timeline.already_approved)                  # 'filed' status path
        self.assertIsNone(sa.timeline.filing_t)
        self.assertAlmostEqual(sa.metrics["p_registration"], 0.75)
        self.assertEqual(sa.funnel.steps[-1].factor, "x 50%")            # asset-level eligibility override
        for fc in (sa, co):
            evaluate(fc.metrics, self.config["decision_rules"])
        self.assertGreater(sa.metrics["rnpv_expected"], co.metrics["rnpv_expected"])

    def test_pipeline_indication_runs(self):
        fc = run_forecast(load_country("SA"), self.asset, self.config, indication="SCD")
        self.assertEqual(fc.indication, "SCD")
        self.assertLess(fc.metrics["p_registration"], 1.0)
        self.assertGreater(fc.metrics["eligible"], self.sa.metrics["eligible"])

    def test_overrides_change_output(self):
        c = apply_overrides(load_country("CO"), ["epidemiology.thalassemia.disease_prevalence_per_1000_adults.value=0.05", "payers.*.bad_debt=0"])
        fc = run_forecast(c, self.asset, self.config)
        self.assertGreater(fc.metrics["eligible"], self.co.metrics["eligible"] * 5)
        self.assertEqual(fc.metrics["bad_debt_blended"], 0.0)
        self.assertEqual(c["epidemiology"]["thalassemia"]["disease_prevalence_per_1000_adults"]["status"], "override")

    def test_sensitivity_runs_and_is_sorted(self):
        tor = tornado(load_country("CO"), self.asset, self.config, "thalassemia")
        self.assertGreater(len(tor["results"]), 5)
        swings = [r["swing"] for r in tor["results"]]
        self.assertEqual(swings, sorted(swings, reverse=True))


class ValidationTests(unittest.TestCase):
    def test_bundled_files_validate(self):
        countries = {c: load_country(c) for c in ("SA", "CO")}
        for c in countries.values():
            self.assertEqual(validate_country(c), [])
        for a in ("mitapivat", "endari"):
            self.assertEqual(validate_asset(load_asset(a), countries), [])

    def test_validator_catches_common_mistakes(self):
        a = load_asset("mitapivat")
        a["competitors"]["TDT"] = [c for c in a["competitors"]["TDT"] if c["id"] != "soc"]
        problems = validate_asset(a)
        self.assertTrue(any("'soc'" in p for p in problems))
        c = load_country("SA")
        c["payers"][0]["share_of_patients"] += 0.2
        self.assertTrue(any("sums to" in p for p in validate_country(c)))
        c = load_country("CO")
        del c["epidemiology"]["SCD"]
        self.assertTrue(any("no epidemiology block for 'SCD'" in p for p in validate_asset(load_asset("endari"), {"CO": c})))


class CliTests(unittest.TestCase):
    def test_json_output_parses(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli.main(["--country", "SA", "--vs", "CO", "--json", "--no-sensitivity"])
        self.assertEqual(rc, 0)
        d = json.loads(buf.getvalue())
        self.assertEqual(d["primary"]["verdict"], "LAUNCH")
        self.assertEqual(d["comparator"]["verdict"], "DO NOT LAUNCH")
        self.assertIn("disagreements", d["bridge"])

    def test_validate_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli.main(["validate"])
        self.assertEqual(rc, 0)
        self.assertIn("OK", buf.getvalue())

    def test_second_asset_report(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli.main(["--asset", "endari", "--country", "SA", "--vs", "CO", "run", "--no-sensitivity"])
        self.assertEqual(rc, 0)
        text = buf.getvalue()
        self.assertIn("ENDARI", text)
        self.assertIn("EMMAUS' OWN STATED NUMBERS", text)
        self.assertIn("Revealed uptake", text)

    def test_text_report_sections(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["--country", "SA", "--vs", "CO", "run", "--no-sensitivity"])
        text = buf.getvalue()
        for needle in ("EPIDEMIOLOGY", "REIMBURSEMENT", "COMPETING THERAPIES", "PRICING REFERENCES",
                       "10-YEAR FORECAST", "VERDICT: LAUNCH", "COMPARE: Saudi Arabia vs Colombia",
                       "WHERE THE MODEL DISAGREES", "BOTTOM LINE"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
