"""Command-line entry point. Terminal only."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from . import __version__
from .bridge import build_bridge
from .compare import decompose
from .data import apply_overrides, list_assets, list_countries, load_asset, load_config, load_country
from .decision import evaluate
from .forecast import Forecast, run_forecast
from . import report
from .report import (hr, money, render_bridge, render_compare, render_forecast, render_header, render_inputs,
                     render_screen, render_summary, render_tornado, wrap)
from .sensitivity import tornado


COMMANDS = ["run", "inputs", "forecast", "compare", "disagree", "sensitivity", "screen", "list", "validate"]


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="launchcast",
                                description="Terminal launch forecaster: should this asset be launched in this country?")
    p.add_argument("--version", action="version", version=f"launchcast {__version__}")
    p.add_argument("--asset", default=None, help="asset id from data/assets (default from config)")
    p.add_argument("--country", "-c", default=None, help="country code to evaluate, e.g. SA")
    p.add_argument("--vs", default=None, help="comparator country code, e.g. CO (default from config)")
    p.add_argument("--indication", default=None, help="indication id; a pipeline indication (e.g. SCD) runs the what-if")
    p.add_argument("--set", action="append", default=[], metavar="PATH=VALUE",
                   help="override any input, e.g. --set epidemiology.thalassemia.diagnosed_share.value=0.8 "
                        "(prefix with 'vs:' to target the comparator, 'asset:' to target the asset)")
    p.add_argument("--exclude-assumed-prices", action="store_true", help="drop assumption-grade prices from the ERP basket")
    p.add_argument("--live", action="store_true", help="refresh population and FX from World Bank / ECB (no keys)")
    p.add_argument("--narrate", action="store_true", help="append a plain-English narration from Claude (needs ANTHROPIC_API_KEY)")
    p.add_argument("--json", action="store_true", help="machine-readable output instead of the report")
    p.add_argument("--no-sensitivity", action="store_true", help="skip the tornado (faster)")
    p.add_argument("--out", "-o", default=None, metavar="FILE",
                   help="write the report to FILE instead of the terminal; .md gives light Markdown, anything else plain text")
    p.add_argument("--format", choices=["text", "md"], default=None, help="force output format (default: by --out extension, else text)")
    p.add_argument("command", nargs="?", default="run", choices=COMMANDS,
                   help="run = full report (default); inputs | forecast | compare | disagree | sensitivity | screen (one asset, every country) | list | validate")
    return p


def _choose(prompt: str, options: list[str]) -> str:
    print(prompt)
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        if raw.upper() in options:
            return raw.upper()
        print("  pick a number from the list")


def _load(args, config) -> tuple[dict, dict, dict]:
    asset = load_asset(args.asset or config["default_asset"])
    country = load_country(args.country)
    comparator = load_country(args.vs) if args.vs else None
    own = [s for s in args.set if not s.startswith(("vs:", "asset:"))]
    vs_over = [s[3:] for s in args.set if s.startswith("vs:")]
    asset_over = [s[6:] for s in args.set if s.startswith("asset:")]
    country = apply_overrides(country, own)
    if comparator is not None:
        comparator = apply_overrides(comparator, vs_over)
    asset = apply_overrides(asset, asset_over)
    if args.live:
        from .live import refresh_country
        log = (lambda m: print(f"  [live] {m}", file=sys.stderr))
        country = refresh_country(country, log)
        if comparator is not None:
            comparator = refresh_country(comparator, log)
    return asset, country, comparator


def _summary(fc: Forecast, verdict: str, rules) -> dict:
    return {
        "country": fc.country["code"], "country_name": fc.country["name"], "asset": fc.asset["id"], "indication": fc.indication,
        "verdict": verdict,
        "rules": [asdict(r) for r in rules],
        "metrics": fc.metrics,
        "timeline": {"approval": fc.timeline.approval_label, "start_year": fc.timeline.start_year,
                     "coverage_years": {k: fc.timeline.start_year + t for k, t in fc.timeline.coverage_t.items()}},
        "funnel": [asdict(s) for s in fc.funnel.steps],
        "erp": {"list_price_usd": fc.erp.list_price_usd, "statistic": fc.erp.statistic, "note": fc.erp.note,
                "used": [{"country": u["country"], "annual_usd": u["annual_usd"], "status": u.get("status")} for u in fc.erp.used]},
        "shares": {seg: {"asset_share": s.asset_share, "options": [asdict(o) for o in s.options]} for seg, s in fc.shares.items()},
        "years": [asdict(r) for r in fc.rows],
        "notes": fc.notes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    config = load_config()
    command = args.command

    if command == "list":
        print("Countries:", ", ".join(f"{c} ({load_country(c)['name']})" for c in list_countries()))
        print("Assets:   ", ", ".join(f"{a} ({load_asset(a)['name']})" for a in list_assets()))
        return 0
    if command == "validate":
        from .validate import validate_asset, validate_country
        countries = {c: load_country(c) for c in list_countries()}
        problems = []
        for c in countries.values():
            problems += validate_country(c)
        for a_id in list_assets():
            problems += validate_asset(load_asset(a_id), countries)
        for pr in problems:
            print("  -", pr)
        print(f"{len(countries)} countries, {len(list_assets())} assets: " + ("OK" if not problems else f"{len(problems)} problem(s)"))
        return 0 if not problems else 1

    fmt = args.format or ("md" if args.out and args.out.lower().endswith((".md", ".markdown")) else "text")
    report.set_format(fmt)

    def emit(text: str) -> int:
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text.rstrip() + "\n")
            print(f"wrote {args.out} ({fmt}, {text.count(chr(10)) + 1} lines)")
        else:
            print(text)
        return 0

    if command == "screen":
        asset = apply_overrides(load_asset(args.asset or config["default_asset"]), [s[6:] for s in args.set if s.startswith("asset:")])
        codes = list_countries() if args.country is None else [args.country.upper()]
        results = []
        for code in codes:
            country = apply_overrides(load_country(code), [s for s in args.set if not s.startswith(("vs:", "asset:"))])
            if args.indication and args.indication not in country["epidemiology"]:
                continue
            try:
                fc = run_forecast(country, asset, config, args.indication, not args.exclude_assumed_prices)
            except KeyError as exc:
                print(f"  skipped {code}: {exc}", file=sys.stderr)
                continue
            verdict, rules = evaluate(fc.metrics, config["decision_rules"])
            results.append({"country": code, "country_name": country["name"], "verdict": verdict, "rules": rules,
                            "metrics": fc.metrics, "status": fc.timeline.approval_label})
        results.sort(key=lambda r: r["metrics"]["rnpv_expected"], reverse=True)
        if args.json:
            print(json.dumps([{**{k: r[k] for k in ("country", "country_name", "verdict", "status", "metrics")},
                                "rules": [asdict(x) for x in r["rules"]]} for r in results], indent=2, default=str))
            return 0
        return emit(render_screen(asset, results))

    interactive = args.country is None and sys.stdin.isatty() and not args.json
    if args.country is None:
        if interactive:
            if args.asset is None and len(list_assets()) > 1:
                names = [f"{a} - {load_asset(a)['name']}" for a in list_assets()]
                args.asset = _choose("Choose the asset:", names).split(" - ")[0]
            countries = list_countries()
            names = [f"{c} - {load_country(c)['name']}" for c in countries]
            pick = _choose("Choose the country to evaluate:", names)
            args.country = pick.split(" - ")[0]
            if args.vs is None:
                rest = [n for n in names if not n.startswith(args.country)]
                if len(rest) == 1:
                    args.vs = rest[0].split(" - ")[0]
                elif rest:
                    args.vs = _choose("Compare against:", rest).split(" - ")[0]
        else:
            args.country = config["default_country"]
    if args.vs is None and command in ("run", "compare"):
        args.vs = config["default_comparator"] if config["default_comparator"] != args.country.upper() else config["default_country"]
    if args.vs and args.vs.upper() == args.country.upper():
        args.vs = None

    asset, country, comparator = _load(args, config)
    from .validate import validate_asset, validate_country
    problems = validate_country(country) + (validate_country(comparator) if comparator else []) + \
        validate_asset(asset, {c["code"]: c for c in [country] + ([comparator] if comparator else [])})
    if problems:
        print("Input files have problems; fix them or run `launchcast validate`:", file=sys.stderr)
        for pr in problems:
            print("  -", pr, file=sys.stderr)
        return 2
    include_assumed = not args.exclude_assumed_prices
    fc = run_forecast(country, asset, config, args.indication, include_assumed)
    verdict, rules = evaluate(fc.metrics, config["decision_rules"])
    fc_b = vb = rules_b = None
    if comparator is not None:
        fc_b = run_forecast(comparator, asset, config, args.indication, include_assumed)
        vb, rules_b = evaluate(fc_b.metrics, config["decision_rules"])

    if args.json:
        payload = {"primary": _summary(fc, verdict, rules)}
        if fc_b is not None:
            payload["comparator"] = _summary(fc_b, vb, rules_b)
            payload["decomposition"] = decompose(fc, fc_b)
        payload["bridge"] = build_bridge(fc)
        if not args.no_sensitivity:
            payload["sensitivity"] = tornado(country, asset, config, fc.indication, include_assumed)
        print(json.dumps(payload, indent=2, default=str))
        return 0

    sections = []
    sections.append(render_header(fc, config))
    if command == "run":
        sections.append(render_summary(fc, verdict, rules, fc_b, vb, build_bridge(fc)))
    if command in ("run", "inputs"):
        sections.append(render_inputs(fc))
    if command in ("run", "forecast"):
        sections.append(render_forecast(fc, verdict, rules))
    if command in ("run", "compare") and fc_b is not None:
        sections.append(render_compare(fc, fc_b, verdict, vb, decompose(fc, fc_b)))
        if command == "compare":
            sections.append(render_forecast(fc_b, vb, rules_b))
    if command in ("run", "disagree"):
        sections.append(render_bridge(fc, build_bridge(fc)))
        if command == "run" and fc_b is not None:
            sections.append(render_bridge(fc_b, build_bridge(fc_b)))
    if command in ("run", "sensitivity") and not args.no_sensitivity:
        sections.append(render_tornado(fc, tornado(country, asset, config, fc.indication, include_assumed)))
        if fc_b is not None:
            sections.append(render_tornado(fc_b, tornado(comparator, asset, config, fc_b.indication, include_assumed), top=6))
    if command == "run":
        tail = [hr("BOTTOM LINE", "-"), ""]
        tail.append(wrap(f"{country['name']}: {verdict}. {comparator['name'] if comparator else ''}{': ' + vb if vb else ''}.", indent=2))
        tail.append(wrap(f"Override any input with --set path=value (see data/{'countries'}/{country['code']}.json for paths); "
                         f"run a pipeline what-if with --indication SCD; print JSON with --json; refresh population/FX with --live.", indent=2))
        sections.append("\n".join(tail))
    if args.narrate:
        from .narrate import narrate
        summary = {"primary": {"country": fc.country["name"], "verdict": verdict, "metrics": fc.metrics,
                               "rules": [asdict(r) for r in rules]}}
        if fc_b is not None:
            summary["comparator"] = {"country": fc_b.country["name"], "verdict": vb, "metrics": fc_b.metrics}
            summary["decomposition"] = decompose(fc, fc_b)
        summary["bridge"] = {k: build_bridge(fc)[k] for k in ("disagreements", "agreements", "comparators")}
        sections.append(hr("NARRATION (Claude)", "-") + "\n\n" + wrap(narrate(summary), indent=2))
    rc = emit("\n\n".join(sections))
    if args.out and command == "run":
        print(f"  {country['name']}: {verdict}" + (f"; {comparator['name']}: {vb}" if comparator else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
