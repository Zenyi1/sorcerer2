# launchcast

Terminal-only launch forecaster for in-licensed / MOU-stage pharma assets. Pick a country, get the
full reasoning: the inputs (epidemiology and prevalence, reimbursement routes, competing therapies,
pricing references), a worked 10-year forecast with a LAUNCH / CONDITIONAL / DO NOT LAUNCH verdict
and the rules that produced it, a side-by-side against a comparator country with the revenue gap
decomposed factor by factor, and a bridge showing where the model disagrees with the originator's
own numbers and why.

No UI. No required API keys. Python 3.9+, standard library only. Everything runs offline from the
JSON in `data/`, and every number carries an evidence grade and a source.

The worked example is a real asset with a real GCC partnering deal: **mitapivat (PYRUKYND /
AQVESME, Agios Pharmaceuticals)** for thalassemia, distributed in the Gulf by NewBridge
Pharmaceuticals under a 2024 agreement, approved by the SFDA on 4 August 2025 (the first approval
anywhere in thalassemia), by the FDA on 23 December 2025 and by the European Commission in May 2026.
Agios has said enough in public (70,000 GCC patients, $425k US price, 4,000 addressable US patients,
$1bn global peak across indications, quarterly ex-US revenue) to disagree with.

## Quick start

```bash
git clone <this repo> && cd sorcerer2
python3 -m launchcast                      # interactive: pick the asset, the country, then the comparator
python3 -m launchcast --country SA --vs CO # Saudi Arabia vs Colombia, full report
```

Or install the console script:

```bash
pip install -e .
launchcast --country SA --vs CO
```

## Output file

Add `--out FILE` to any command. A `.md` extension gives light Markdown (headings, pipe tables where
there is a table, plain paragraphs otherwise, summary first); any other extension gives the plain
text you would see in the terminal. The terminal then shows only the verdicts.

```bash
launchcast --country SA --vs CO --out reports/mitapivat_SA_vs_CO.md
launchcast screen --asset endari --out reports/endari_screen.md
```

## Commands

| Command | What it prints |
|---|---|
| `launchcast --country SA --vs CO run` | Everything below in order (default command) |
| `... inputs` | 1 epidemiology funnel, 2 reimbursement routes, 3 competing therapies and share model, 4 pricing references and ERP result, 5 launch economics |
| `... forecast` | Year-by-year table (success case and probability-weighted), key metrics, verdict with rule table |
| `... compare` | Side-by-side metrics and the multiplicative decomposition of the peak-sales gap |
| `... disagree` | Bridge from the originator's stated numbers to the model's, with the disagreements spelled out |
| `... sensitivity` | One-at-a-time tornado on risk-adjusted NPV; marks drivers that flip the verdict |
| `launchcast screen --asset <id>` | One asset against every country file, ranked by risk-adjusted NPV, with verdict and failing rules per country |
| `... list` | Countries and assets available |
| `... validate` | Schema-check every data file; exit 1 with plain-language problems if any |

Useful flags:

```bash
--asset endari                   # second bundled asset (Emmaus' Endari, sickle cell)
--indication SCD                 # what-if for a pipeline indication (sickle cell, PDUFA Feb 2027)
--set payers.*.bad_debt=0        # override any input by dotted path; '*' fans out over lists
--set vs:payers.0.p_coverage=0.9 # prefix 'vs:' targets the comparator, 'asset:' the asset file
--exclude-assumed-prices         # drop assumption-grade prices from the ERP basket
--json                           # machine-readable output of everything
--no-sensitivity                 # faster
--live                           # refresh population (World Bank) and FX (ECB) - no keys
--narrate                        # plain-English narration from Claude - needs ANTHROPIC_API_KEY
```

Examples of the full output are in `examples/`.

## What API keys do you need?

**None for the model.** It is deterministic and runs from bundled, sourced data.

Optional:

| Purpose | Key / credential | Notes |
|---|---|---|
| `--narrate` (plain-English explanation of the result) | `ANTHROPIC_API_KEY` (or an `ant auth login` profile) and `pip install anthropic` | Uses `claude-opus-5-5` with server-side refusal fallback; explains the numbers it is given, never adds any |
| `--live` population and FX refresh | none | World Bank `SP.POP.TOTL`; frankfurter.app (ECB rates) |
| SFDA public price list (to replace the ERP estimate with the registered SAR price) | none | xlsx download from sfda.gov.sa, no API; paste into `reference_prices` |
| Colombia SISMED / INVIMA open data | optional Socrata app token for datos.gov.co | Only raises the rate limit |
| SEC EDGAR (originator filings for the biotech view) | none, but a descriptive `User-Agent` is required | Figures are already transcribed into `biotech_view` with the filing cited |
| openFDA labels | optional `OPENFDA_API_KEY` | Only raises the rate limit |
| Licensed epidemiology / sales / HTA feeds (IQVIA MIDAS, Evaluate, GlobalData, Citeline, Cortellis) | licensed credentials | Not integrated; the JSON schema is where those numbers would be dropped in, with `status: "verified"` |

Nothing in this repository phones home. The three primary documents that could not be read from the
build sandbox (SFDA pricing guideline via the PPRI 2024 report, Colombia's Circular 18 de 2024, and
the Saudi TDT cost-of-illness study) are cited in the data files with what the secondary sources say
about them; those entries are graded `reported`, not `verified`.

## How the model decides

Per asset and country, five input blocks feed one deterministic engine (`launchcast/forecast.py`):

1. **Epidemiology.** Adults in the base population x disease prevalence per 1,000 adults x other
   label-covered forms x diagnosed x followed in a specialist centre x label-eligible (adult, anemic,
   not cured). Saudi Arabia anchors on the national premarital screening programme (0.7 beta-thal
   disease per 1,000 adults screened, 2011-2015, n=1.23m). Colombia has no national figure; the
   central case is ~200 adults with beta-thal major/intermedia and is flagged as the weakest input.
2. **Reimbursement.** Registration (status, review months, probability), pricing lag, then payer
   routes each with share of patients, probability of coverage, months to coverage, net-to-list
   factor, days sales outstanding and bad debt. Saudi Arabia: NUPCO central procurement, other
   government hospitals, CHI-insured private sector. Colombia: contributory and subsidized EPS funded
   through ADRES, with the 2025 presupuestos-maximos shortfall and EPS debt crisis expressed as
   coverage probability, DSO and bad debt. Early access before listing is a small direct share of
   eligible patients, calibrated in Saudi Arabia to Agios' reported 2026 rest-of-world revenue.
3. **Competing therapies.** Multinomial logit over the therapies actually available in the country
   (standard of care, luspatercept, exa-cel, the asset) on efficacy, convenience, safety and a log
   price index, with payer-specific weights (Colombia weighs price twice as heavily), a status-quo
   bonus for standard of care and capacity caps for gene therapy. Segment shares (TDT / NTDT) are
   blended by the eligible mix.
4. **Pricing references.** The asset's reference price table is run through each country's external
   reference pricing rule: SFDA median of the available basket capped at the country-of-origin price;
   Colombia 25th percentile under the CNPMDM circulars. Net price then takes payer discounts, a
   repricing cut, FX drift for COP-denominated prices, and a budget-impact ceiling modelled as a
   price-volume agreement when public spend would exceed a share of national drug spend.
5. **Economics.** Launch-partner P&L: transfer price to the originator, logistics, launch and
   pre-launch opex, upfront dossiers, working-capital cost from DSO, bad debt, cost of capital.

Patients on therapy in year t = eligible x paying-route access(t) x peak share x logistic uptake(t)
x persistence, plus early access. The success case assumes registration and every modelled payer
route pays; the expected case weights by registration probability and each route's coverage
probability. Risk-adjusted NPV is the discounted expected cash flow over the horizon.

**Verdict rules** (`data/config.json`): hard rules are expected rNPV >= 0, success-case peak net
sales >= $3m and P(registered and reimbursed) >= 50%; soft rules are payback <= 5 years from first
sale and >= 20 patients at peak. All pass -> LAUNCH; only soft rules fail -> CONDITIONAL; any hard
rule fails -> DO NOT LAUNCH.

## The worked output, in one paragraph

Saudi Arabia: LAUNCH. About 3,600 label-eligible adults (range 2,050-4,600), 75% probability of a
paying route, first institutional listings in late 2026 and NUPCO from 2027, ERP list price ~$234k
falling to a ~$160k blended net once the budget ceiling binds around 2030, ~780 patients and ~$125m
net sales at peak if reimbursed ($99m probability-weighted), risk-adjusted NPV ~$112m for the launch
partner. Colombia: DO NOT LAUNCH. About 74 eligible adults, INVIMA decision not before 2029, 37%
probability of a paying route, 12% expected bad debt, ~10 patients and ~$1.8m at peak, rNPV about
-$1.5m, and no single sensitivity driver flips it. The gap decomposes as 49x patients x 1.6x share
x 0.9x price, i.e. it is epidemiology and access, not price, and Colombia only becomes interesting
with a sickle-cell label (`--indication SCD`).

Where the model disagrees with Agios: the 70,000 GCC headline counts all ages and forms, while the
adult, anemic, in-care, label-eligible Saudi pool is ~3,600 (9% of the population-allocated
figure); the $425k US price is not a Saudi reference (ERP gives $234k list, ~$160k net); national
procurement in 2027 and peak uptake only around 2030 mean 2026-27 revenue is early-access business;
and at the modelled volumes the public bill would exceed 1% of national drug spend, which a payer
answers with a price-volume agreement. Where it agrees: Saudi Arabia deserved an approval-first
strategy, persistence (~75-78%), and the segment logic from the ENERGIZE trials.

## What an asset file needs

Think of it as three tiers. The engine runs on tier 1; tiers 2 and 3 make the bridge and the
sensitivity sections say something.

| Tier | Field | What it is | Where it comes from |
|---|---|---|---|
| 1 must have | `indication.id`, `indication.segments` | Disease id (must match an `epidemiology.<id>` block in each country file) and the patient segments the label splits into (one is fine) | Label |
| 1 | `regulatory_status.<CC>` | `approved` + date, `filed` + expected decision + probability, or `not_filed`, per country | Regulator, company releases |
| 1 | `reference_prices[]` | Annual price per patient in any country where it is sold (US WAC and dosing arithmetic at minimum); assumed EU prices allowed if graded `assumption` | Pricing disclosures, Lauer-Taxe, CADTH, company |
| 1 | `competitors.<segment>[]` | Standard of care (`id: soc`), the asset itself (`id: <asset id>`, price null), each rival with efficacy / convenience / safety scores in [0,1], annual price, and availability in each country | Trials, labels, local registration status |
| 2 should have | `indication.label_eligible_share_override` | Share of in-care adults who meet the label (when eligibility is a label property, not a country one) | Trial entry criteria |
| 2 | `deal` | Partner, territory, economics in words; territory drives the "geography" disagreement | Term sheet / MOU |
| 2 | `uptake.years_to_peak`, `uptake.home_market_observed_share` | Ramp speed; revealed uptake at home if launched (flags optimistic shares) | Analogues; home revenue / prevalence |
| 3 nice to have | `biotech_view` | The originator's own numbers: home price, addressable share, patient claims by region with country split, access statements per country, reported regional revenue, points of agreement | Earnings calls, decks, 10-Q |
| 3 | `clinical`, `pipeline_indications` | Trial facts for the record; next indications with approval probability and year for what-ifs | Publications, PDUFA dates |

The country file carries everything about the place (population, prevalence per disease, payers,
regulator, pricing rule, costs), so a new asset in a disease the country files already cover is
one file. A new disease means adding an `epidemiology.<id>` block to each country file, which is
the only input that is genuinely hard to source; the template shows the fields and the grades.

## Adding an asset or a country

The engine has no asset in it. `data/assets/mitapivat.json` and `data/assets/endari.json` are the two
bundled examples; `data/assets/_template.json` and `data/countries/_template.json` are annotated
starting points. Steps:

1. Copy the template to `data/assets/<id>.json`. Fill the deal, label and segments, regulatory status
   per country (`approved` with a date, `filed` with an expected decision and probability, or
   `not_filed`), the reference price table, the competitor set per segment with availability in each
   country, and whatever the originator has said in public (`biotech_view`).
2. Make sure each country file has an `epidemiology.<indication id>` block. If the asset has more than
   one segment, the block's `segment_mix` must use the same segment ids. If eligibility is a property of
   the label rather than the country, set `indication.label_eligible_share_override` on the asset.
3. Run `launchcast validate`; it lists every missing or inconsistent field in plain words.
4. Run `launchcast --asset <id> --country SA --vs CO`.

The second bundled asset shows the range: Endari is a low-priced, modest-efficacy oral therapy with a
royalty-style MENA deal, filed with the SFDA since 2021 and still pending, and with seven years of
revealed uptake at home (about 1% of US patients). The bridge section uses that revealed uptake to
flag the model's own share assumption as optimistic.

## Data and evidence grades

Everything lives in `data/`:

- `countries/SA.json`, `countries/CO.json`: population, macro, health system, regulator, pricing
  rule and basket, payer routes, epidemiology per indication, competition weights, commercial costs.
- `assets/mitapivat.json`, `assets/endari.json`: deal, label and segments, regulatory status by
  country, trial results, reference prices, competitors per segment with per-country availability, the
  originator's own stated numbers (`biotech_view`), revealed home-market uptake, pipeline indications.
- `assets/_template.json`, `countries/_template.json`: annotated templates (ignored by the CLI).
- `config.json`: horizon, decision rules, sensitivity ranges.

Every input node is `{"value": ..., "status": ..., "source": ...}` with status one of `verified`
(primary source read), `reported` (secondary source), `company_stated` (originator's figure),
`assumption` (ours, with rationale), `unknown` (excluded). The report prints the grade next to
every number as `[V] [R] [C] [A] [?]`, and `[O]` for a command-line override.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Limitations

- Prevalence for Colombia is an order-of-magnitude estimate; the tornado shows it does not change
  the verdict, but it would change the size of any opportunistic named-patient business.
- EU reference prices for the thalassemia indication are assumptions until Avanzanite lists; the
  Saudi result is insensitive to them because the budget ceiling binds, the Colombian list price is
  not.
- The SFDA statistic (median vs lowest) and the current basket are from secondary sources; set
  `pricing.statistic` to `min` to see the lower bound.
- The share model is a utility heuristic, not a fitted model; its weights are printed and
  overridable.
- Single horizon, no Monte Carlo; use `--set` and `sensitivity` for ranges.
