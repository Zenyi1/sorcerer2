"""Optional live refresh of the few inputs that have free public APIs. No keys needed.

World Bank (population) and frankfurter.app (ECB FX) are tried with a short timeout. Anything that
fails is left at the bundled value and reported. Prevalence, reimbursement and price inputs have no
free API; they stay in the JSON with their sources.
"""
from __future__ import annotations

import json
import urllib.request
from typing import Callable

ISO3 = {"SA": "SAU", "CO": "COL"}


def _get(url: str, timeout: float = 8.0):
    req = urllib.request.Request(url, headers={"User-Agent": "launchcast/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def refresh_country(country: dict, log: Callable[[str], None]) -> dict:
    code = country["code"]
    iso3 = ISO3.get(code)
    if iso3:
        try:
            data = _get(f"https://api.worldbank.org/v2/country/{iso3}/indicator/SP.POP.TOTL?format=json&per_page=5&mrnev=1")
            rec = data[1][0]
            total = float(rec["value"])
            old = country["population"]["total"]["value"]
            ratio = total / old if old else 1.0
            country["population"]["total"].update({"value": total, "year": int(rec["date"]), "status": "verified",
                                                   "source": "World Bank SP.POP.TOTL (live)"})
            if country["population"]["nationals"]["value"] == old:
                country["population"]["nationals"]["value"] = total
            else:
                country["population"]["nationals"]["value"] *= ratio
            log(f"{code}: population refreshed from World Bank: {total:,.0f} ({rec['date']})")
        except Exception as exc:  # network, schema or sandbox errors are all non-fatal
            log(f"{code}: World Bank population not refreshed ({exc.__class__.__name__}); bundled value kept")
    cur = country.get("currency")
    if cur and cur != "USD":
        try:
            fx = _get(f"https://api.frankfurter.app/latest?from=USD&to={cur}")
            rate = float(fx["rates"][cur])
            country["fx_per_usd"].update({"value": rate, "status": "verified", "source": f"frankfurter.app / ECB {fx['date']} (live)"})
            log(f"{code}: FX refreshed: {rate:,.2f} {cur}/USD ({fx['date']})")
        except Exception as exc:
            log(f"{code}: FX not refreshed ({exc.__class__.__name__}); bundled value kept")
    return country
