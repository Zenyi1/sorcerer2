# mitapivat (PYRUKYND / AQVESME) in Saudi Arabia (SA), indication thalassemia

Originator: Agios Pharmaceuticals (NASDAQ: AGIO). Deal: GCC distribution agreement (MOU-stage equivalent: originator supplies product, partner files, imports and commercializes) with NewBridge Pharmaceuticals, Dubai (2024).

Perspective: launch partner P&L. Horizon: 2026-2035. Status here: approved 2025-08-04 (SFDA Breakthrough Medicines Program (first approval worldwide in thalassemia)).

Evidence grades: [V] verified primary source, [R] reported/secondary, [C] originator's own figure, [A] our assumption, [O] command-line override, [M] model output.

## SUMMARY

Saudi Arabia: LAUNCH. 3,587 label-eligible adults, 75% chance of a paying route, first reimbursed sale 2026.7, peak $125.3m if reimbursed ($99.0m probability-weighted), risk-adjusted NPV $111.9m, payback immediate.

Colombia: DO NOT LAUNCH. 74 eligible, 37% chance of a paying route, first reimbursed sale 2030.9, peak $1.8m if reimbursed, risk-adjusted NPV -$1.5m, payback none in horizon.

Main disagreements with the originator: Patient count. Price. Timing.

## INPUTS

### 1. Epidemiology and prevalence: label-eligible patients

| Step | Factor | Patients | Grade |
| --- | --- | --- | ---: |
| Adults in the epidemiology base | 19,600,000 x 66.5% adults | 13,034,000 | [V] |
| Prevalent disease (adults) | x 0.7 per 1,000 adults | 9,124 | [V] |
| Other label-covered forms (alpha-thal / HbH) | x 1.12 | 10,219 | [A] |
| Diagnosed | x 90% | 9,197 | [A] |
| Followed in a specialist centre | x 65% | 5,978 | [A] |
| Label-eligible (adult, anemic, not cured) | x 60% | 3,587 | [A] |

Range on prevalence alone: 2,050 - 4,612 eligible adults; segment mix: TDT 45%, NTDT 55%.

- Adults in the epidemiology base: GASTAT 2024: Saudis 55.6% of population
- Prevalent disease (adults): National premarital screening 2011-2015, n=1,230,582: beta-thalassemia 13.6/1000 (12.9 trait, 0.7 disease); JEGH 2019 https://doaj.org/article/efa04d78045743e4831a5bf995ebcd2d ; regional 134/1000 hemoglobinopathy in Eastern Province (Memish 2011, https://pubmed.ncbi.nlm.nih.gov/21623050/)
- Other label-covered forms (alpha-thal / HbH): HbH disease is common in the Eastern Province (Thrombosis J 2023, https://link.springer.com/article/10.1186/s12959-023-00560-w); label covers alpha-thalassemia; adds ~12% to the pool
- Diagnosed: Mandatory premarital screening since 2004 plus dedicated hereditary blood disease centres
- Followed in a specialist centre: Single-centre cohorts (Al-Ahsa 158 TDT, Jeddah 152 TDT, Madinah 111 TDT) imply most TDT are followed; many NTDT are not
- Label-eligible (adult, anemic, not cured): Adults with TDT, or NTDT with Hb <=10 g/dL (ENERGIZE entry criteria); excludes post-HSCT / gene therapy

Base note: Hemoglobinopathy burden is concentrated in Saudi nationals (Eastern Province, Jazan, Madinah). Expatriate carriers exist but are rarely reimbursed by the state; excluded.

### 2. Reimbursement and market access

Regulator: SFDA. Abridged/verification review for FDA- or EMA-approved products; Breakthrough Medicines Program for priority assets. Typical review 9 months [R]; P(approval | FDA/EMA approved) 95% [A].

System: Government-dominated. MoH hospitals (procured centrally through NUPCO), other government providers (KFSH&RC, National Guard, Ministry of Defense, university hospitals) with their own budgets, and a private sector funded by mandatory CHI health insurance for expatriates and private-sector employees. Hereditary blood disease centres sit in the Eastern Province (Qatif, Al-Ahsa, Dammam), Jazan, Madinah, Jeddah and Riyadh.

| Payer route | Patients | P(cover) | Months | From | Net/list | DSO d | Bad debt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MoH hospitals via NUPCO central procurement | 50% | 80% | 18 | 2027.4 | 80% | 120 | 0% |
| Other government providers (KFSH&RC, NGHA, MODA, universit | 33% | 85% | 10 | 2026.7 | 85% | 90 | 0% |
| Private sector, CHI-insured (Unified Drug Formulary) | 12% | 60% | 18 | 2027.4 | 95% | 75 | 2% |
| No payer (cash / uninsured) | 5% | 0% | - | - | - | - | - |

- moh_nupco: National procurement agreement is the gate Agios itself named ('over the next couple of years', Q3 2025). Tender discount vs SFDA list assumed 20%.
- other_gov: Institution-level formulary decisions; faster than NUPCO; these centres ran the ENERGIZE trials
- private_chi: Mostly expatriates and private-sector Saudis; insurers restrict high-cost orphan drugs

Early access before listing: 1.2% of eligible [R]. Blended P(a patient has a paying route) = 75%.

### 3. Competing therapies: peak share model (multinomial logit on efficacy, convenience, safety, price)

Payer utility weights here: efficacy 2.5, convenience 1.0, safety 1.0, price 0.8 [A]; standard of care gets a status-quo bonus of 1.5.

| Seg | Therapy | Here | Eff | Conv | Safe | Price/yr | Share |  |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| TDT | Standard of care only (transfusion + iron chelation) | available | 0.00 | 0.30 | 0.80 | $40k | 51.8% |  |
|  | mitapivat (oral BID) | available | 0.45 | 1.00 | 0.65 | $196k | 35.6% |  |
|  | luspatercept (Reblozyl, SC every 3 weeks) | limited | 0.45 | 0.50 | 0.80 | $150k | 9.6% |  |
|  | exagamglogene autotemcel (Casgevy, one-time gene edi | capacity_limited | 0.95 | 0.40 | 0.60 | $2m | 3.0% | cap |
| NTDT | Watchful waiting / occasional transfusion / off-labe | available | 0.00 | 0.70 | 0.90 | $8k | 69.5% |  |
|  | mitapivat (oral BID) | available | 0.60 | 1.00 | 0.65 | $196k | 24.0% |  |
|  | luspatercept (Reblozyl, EU label for NTDT beta-thal  | limited | 0.60 | 0.50 | 0.80 | $150k | 6.5% |  |

Blended peak share of label-eligible patients = 29.2% (TDT 35.6% x 45% + NTDT 24.0% x 55%).

- luspatercept (Reblozyl, SC every 3 weeks): FDA approval for TDT beta-thal 2019 (BELIEVE: 21.4% vs 4.5% >=33% transfusion reduction); US WAC $3,441/25 mg vial at launch; CADTH annual CAD 114-152k. Saudi: named-patient and a BMS Middle East real-world study (NCT07215975, Jizan site); no SFDA price found. Colombia: INVIMA registration not confirmed.
- exagamglogene autotemcel (Casgevy, one-time gene editing): SFDA approval Jan 2024 for SCD and TDT >=12y via Breakthrough Medicines Program; first authorized centre MNGHA Riyadh, https://investors.vrtx.com/news-releases/news-release-details/vertex-announces-approval-first-crisprcas9-gene-edited-therapy
- luspatercept (Reblozyl, EU label for NTDT beta-thal only): EU extension to NTDT beta-thalassemia 2023 (BEYOND: 77% vs 0% Hb >=1 g/dL); not FDA approved for NTDT; alpha-thalassemia not covered

### 4. Pricing references: external reference price

Rule: SFDA Drug Pricing (2023 Drug Pricing Guidelines); statistic 'median' over basket US, DE, FR, GB, IT, ES, NL, SE, AT, PT, PL, HU, CA, AU, JP, KR; origin-country cap: True. Basket size has moved 30 -> 20 (2021) -> 16 (2022) per ISPOR 2023 poster; one 2024 source cites 34. The statistic (median vs lowest) is not fixed in public text: 'SFDA did not state that they will strictly select the lowest price'. Median of available basket prices, capped at the country-of-origin price, is used as the base case; 'min' is run in sensitivity.

| Ctry | Indication | Brand | USD/yr | Grade | In basket? |
| --- | --- | --- | --- | --- | --- |
| US | thalassemia | AQVESME | $425k | [C] | used |
| US | PK deficiency | PYRUKYND | $336k | [V] | different indication |
| DE | thalassemia |  | $255k | [A] | used |
| FR | thalassemia |  | $234k | [A] | used |
| GB | thalassemia |  | $212k | [A] | used |
| IT | thalassemia |  | $225k | [A] | used |
| AE | thalassemia |  | unknown | [?] | no price known |

ERP result: $234k per patient-year list (median of 5 basket prices) = SAR 877,500 at 3.75 SAR/USD [V]. Standard of care costs $40k/yr [A].

- US AQVESME: Agios management on the FDA-approval earnings call: 'addressable launch population' 4,000 patients, price $425,000/yr. Not a published WAC.
- US PYRUKYND: Agios Connecticut pricing disclosure 2025: WAC $25,760 per 56-tablet carton (28 days at BID) -> 13.04 cartons/yr, https://agios.com/wp-content/uploads/2025/01/Agios_CT_Pricing_Sheet_2025.pdf
- DE thalassemia: Avanzanite EU launch pricing not yet public. Assumed 60% of US company-stated price, the typical EU/US ratio for orphan small molecules. Replace with Lauer-Taxe price when listed.
- FR thalassemia: Assumed 55% of US; replace with JO price after CEPS negotiation
- GB thalassemia: Assumed 50% of US; NICE/NHS England confidential discounts not captured
- IT thalassemia: Assumed 53% of US; Italy is the largest EU thalassemia market
- AE thalassemia: Approved Mar 2026; MoHAP price not found. Relevant for the GCC-lowest clause.

### 5. Launch economics (partner view)

Transfer price to originator 65% of net sales [A]; logistics 6%; launch opex $900k/yr [A]; pre-launch opex $0/yr; upfront: Pricing / market-access dossiers, NUPCO and institutional listings $150k at approval; Pharmacovigilance, import licence, cold-chain / 3PL set-up $100k at approval. Cost of capital 10%. Persistence 78% [R]. Budget-impact ceiling 1.0% of a $10.7bn drug market = $107m/yr public spend [A].

## OUTPUT: 10-YEAR FORECAST, Saudi Arabia

| Year | Eligible | Access | Uptake | Pts(succ) | Pts(exp) | Net $/pt | Sales(succ) | Sales(exp) | Cash(exp) | Cum cash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026 | 3,587 | 1% | 13% | 29 | 29 | $234k | $6.9m | $6.9m | $888k | $888k |
| 2027 | 3,641 | 35% | 32% | 114 | 98 | $205k | $23.3m | $20.2m | $4.4m | $5.3m |
| 2028 | 3,695 | 95% | 61% | 489 | 388 | $176k | $86.1m | $68.0m | $16.7m | $22.0m |
| 2029 | 3,751 | 95% | 83% | 680 | 539 | $176k | $119.8m | $94.6m | $23.6m | $45.6m |
| 2030 | 3,807 | 95% | 94% | 779 | 617 | $161k | $125.3m | $98.9m | $24.7m | $70.3m |
| 2031 | 3,864 | 95% | 98% | 823 | 652 | $152k | $125.3m | $98.9m | $24.7m | $95.1m |
| 2032 | 3,922 | 95% | 99% | 846 | 671 | $148k | $125.3m | $98.9m | $24.7m | $119.8m |
| 2033 | 3,981 | 95% | 100% | 862 | 683 | $145k | $125.3m | $99.0m | $24.7m | $144.5m |
| 2034 | 4,040 | 95% | 100% | 876 | 695 | $143k | $125.3m | $99.0m | $24.7m | $169.3m |
| 2035 | 4,101 | 95% | 100% | 890 | 705 | $141k | $125.3m | $99.0m | $24.7m | $194.0m |

'succ' = if registered and every modelled payer route pays; 'exp' = probability-weighted (registration x coverage).

- Note: Budget-impact ceiling ($107m/yr public spend) binds in 2030-2035; modelled as a price-volume agreement that lowers the effective net price.
- Note: ERP basket includes assumed EU prices (DE, FR, GB, IT); replace when Avanzanite lists in Europe.

### Key metrics

| Metric | Value |
| --- | --- |
| Label-eligible adults (range) | 3,587 (2,050 - 4,612) |
| Peak competitive share | 29.2% |
| List price (ERP) / net at peak | $234k / $161k per patient-year |
| First sale / first reimbursed sale | 2026 / 2026.7 |
| Patients on therapy at peak (succ / exp) | 779 / 705 in 2030 |
| Peak net sales (succ / exp) | $125.3m / $99.0m |
| Cumulative net sales, horizon (exp) | $783.4m |
| P(registration) x P(paying route) | 100% x 75% = 75% |
| Risk-adjusted NPV (exp) / NPV (succ) | $111.9m / $142.3m |
| Payback from first sale | immediate (no cumulative loss) |

### Verdict: LAUNCH

| Rule | Value | Threshold | Result | Type |
| --- | --- | --- | --- | --- |
| Risk-adjusted NPV (expected) | $111.9m | >= $0m | pass | hard |
| Peak net sales if reimbursed | $125.3m | >= $3m | pass | hard |
| P(registered and reimbursed) | 75% | >= 50% | pass | hard |
| Payback from first sale | immediate | <= 5 yr | pass | soft |
| Patients on therapy at peak | 779 | >= 20 | pass | soft |

## COMPARE: Saudi Arabia vs Colombia

|  | Saudi Arabia | Colombia |
| --- | --- | --- |
| Verdict | LAUNCH | DO NOT LAUNCH |
| Status | approved 2025-08-04 (SFDA Breakthrough Medicines | not filed; file 2027.0, decision ~2029.4 (INVIMA |
| Label-eligible adults | 3,587 | 74 |
| P(registered) x P(paying route) | 75% | 37% |
| First reimbursed sale | 2026.7 | 2030.9 |
| List price (ERP) | $234k | $225k |
| Net price at peak | $161k | $184k |
| Peak share | 29.2% | 18.4% |
| Patients at peak (succ) | 779 | 10 |
| Peak net sales (succ / exp) | $125.3m / $99.0m | $1.8m / $697k |
| Risk-adjusted NPV | $111.9m | -$1.5m |
| Payback | immediate | none in horizon |
| Expected bad debt | 0% | 12% |

### Why: multiplicative decomposition of peak-year net sales (SA / CO)

| Factor | SA | CO | Ratio |
| --- | ---: | ---: | ---: |
| Label-eligible adults (peak year) | 3,807 | 77 | 49.28x |
| Share with a paying route at peak | 95.1% | 98.0% | 0.97x |
| Peak competitive share | 29.2% | 18.4% | 1.59x |
| Uptake reached by peak year | 94.3% | 95.4% | 0.99x |
| Persistence on therapy | 78.0% | 75.0% | 1.04x |
| Net price per patient-year | $161k | $184k | 0.88x |
| = Peak net sales (success case) | $125m | $2m | 68.55x |
| memo: collected share (1 - bad debt) | 99.7% | 88.0% | 1.13x |
| memo: years from decision to first reimbursed sale | 0.7 | 4.9 |  |

The factor ratios above the '=' line multiply to the peak-sales ratio, so the gap can be attributed line by line. Memo lines are not in the product: collections hit cash rather than sales, and timing hits the NPV through the years lost to registration and listing.

## WHERE THE MODEL DISAGREES WITH AGIOS' OWN STATED NUMBERS: Saudi Arabia

### Patients

| Step | Patients | Grade |
| --- | ---: | ---: |
| Originator: thalassemia patients in GCC | 70,000 | [C] |
| Allocated to Saudi Arabia (share 58%) | 40,600 | [R] |
| Model: prevalent adults with disease | 10,219 | [V] |
| Diagnosed | 9,197 | [M] |
| Followed in a specialist centre | 5,978 | [M] |
| Label-eligible (adult, anemic, not cured) | 3,587 | [M] |
| With a paying route at peak (2030, if reimbursed) | 3,410 | [M] |
| Choosing this therapy (peak competitive share) | 996 | [M] |
| Still on therapy (persistence) | 779 | [M] |

- Originator: thalassemia patients in GCC: Agios Q3 2024 earnings call: 'the GCC region is home to approximately 70,000 patients with thalassemia'
- Allocated to Saudi Arabia (share 58%): GCC population ~60.5m (2024); Saudi Arabia 35.3m = 58%. Used to allocate the GCC figure to Saudi Arabia; the Eastern Province burden argues for an even higher share All ages, all thalassemia forms; carriers possibly included in regional registries
- Model: prevalent adults with disease: 25% of the allocated originator figure. Anchor: Saudi national premarital screening data (0.7 beta-thalassemia disease per 1,000 adults screened, 2011-2015).
- With a paying route at peak (2030, if reimbursed): 95% of eligible; uncovered and not-yet-listed payers excluded
- Choosing this therapy (peak competitive share): 29% vs standard of care and exagamglogene autotemcel, luspatercept
- Still on therapy (persistence): x 78%; originator reports 75% 6-month persistency at home

### Price per patient-year

| Step | USD | Grade |
| --- | ---: | ---: |
| Originator: US price per patient-year | $425k | [C] |
| Model: Saudi Arabia list price after external reference pricing | $234k | [M] |
| Model: blended net price at peak (tenders, formulary discounts, budget cap, FX) | $161k | [M] |

- Model: Saudi Arabia list price after external reference pricing: median of 5 basket prices
- Model: blended net price at peak (tenders, formulary discounts, budget cap, FX): budget-impact ceiling binding

### Revenue comparators

| View | Per year |
| --- | ---: |
| Naive TAM: originator patient figure x US price | $17.3bn |
| Originator US launch logic applied here: 65% addressable x 20% penetration x US price | $2.2bn |
| Same logic on the model's eligible pool (3,587 x 65% x 20% x US price) | $198.2m |
| This model: peak net sales if reimbursed (2030) | $125.3m |
| This model: peak net sales, probability-weighted | $99.0m |

### Disagreements, and why

1. Patient count. The 70,000 GCC figure is a headline prevalence (all ages, all thalassemia forms; carriers possibly included in regional registries). The label-eligible pool in Saudi Arabia is 3,587 (9% of the allocated figure). The anchor is Saudi national premarital screening data (0.7 beta-thalassemia disease per 1,000 adults screened, 2011-2015), not a regional registry.

2. Price. US $425,000 is not a reference for Saudi Arabia: the ERP rule (median of 5 basket prices) gives $234,000 list, and procurement discounts, early-access pricing and the budget ceiling bring the blended net to $160,888 at peak (38% of US).

3. Timing. Originator: 'Early patient access case-by-case; national procurement agreements expected over the next couple of years' (Agios Q3 2025 results, https://investor.agios.com/news-releases/news-release-details/agios-reports-third-quarter-2025-financial-results-and-provides). The model has the first paying route in 2026.7, MoH hospitals via NUPCO central procurement coverage from 2027.4, and peak uptake only in 2030. Revenue before that is early-access, hospital-budget business.

4. Budget impact. At the modelled patient numbers the public bill would exceed 1.0% of national drug spend from 2030; the model assumes the payer forces a price-volume agreement rather than paying list for everyone. Originator decks rarely model this.

### Agreements

- Persistence: originator reports 75% at 6 months at home; the model uses 78% annual on-therapy.
- Saudi Arabia was worth an approval-first strategy: the model's verdict and Agios' sequencing (SFDA before FDA, NewBridge partnership) agree.
- NTDT is the larger patient segment and TDT the better-paying one; the model's segment shares rest on the same trial results Agios cites (ENERGIZE 42.3% vs 1.6%; ENERGIZE-T 30.4% vs 12.6%).

### Calibration

- Originator-reported ex-US net revenue (EU + GCC combined): $12.3m across 2026Q1, 2026Q2, 2026Q3 (Agios 10-Q Q1 2026 (rest of world $1,895k), 8-K Q2 2026 (ex-US $3.8m: 'anticipated demand in EU and continued early demand in the GCC'), Q3 2026 call ($6.6m ex-US). EU + GCC combined; Saudi share not disclosed.). The model's 2026 Saudi Arabia in-market net sales are $6.9m (~29 patients on therapy). This country alone must stay below the reported total; it does.

## WHERE THE MODEL DISAGREES WITH AGIOS' OWN STATED NUMBERS: Colombia

### Patients

| Step | Patients | Grade |
| --- | ---: | ---: |
| Model: prevalent adults with disease | 216 | [A] |
| Diagnosed | 151 | [M] |
| Followed in a specialist centre | 113 | [M] |
| Label-eligible (adult, anemic, not cured) | 74 | [M] |
| With a paying route at peak (2034, if reimbursed) | 72 | [M] |
| Choosing this therapy (peak competitive share) | 13 | [M] |
| Still on therapy (persistence) | 10 | [M] |

- Model: prevalent adults with disease: No originator patient figure covers this country. Anchor: no national prevalence figure exists for Colombia; the estimate is bounded by regional studies and the national orphan-disease registry.
- With a paying route at peak (2034, if reimbursed): 98% of eligible; uncovered and not-yet-listed payers excluded
- Choosing this therapy (peak competitive share): 18% vs standard of care and luspatercept
- Still on therapy (persistence): x 75%; originator reports 75% 6-month persistency at home

### Price per patient-year

| Step | USD | Grade |
| --- | ---: | ---: |
| Originator: US price per patient-year | $425k | [C] |
| Model: Colombia list price after external reference pricing | $225k | [M] |
| Model: blended net price at peak (tenders, formulary discounts, budget cap, FX) | $184k | [M] |

- Model: Colombia list price after external reference pricing: p25 of 5 basket prices
- Model: blended net price at peak (tenders, formulary discounts, budget cap, FX): budget-impact ceiling not binding

### Revenue comparators

| View | Per year |
| --- | ---: |
| Naive TAM: prevalent patient figure x US price | $91.7m |
| Originator US launch logic applied here: 65% addressable x 20% penetration x US price | $11.9m |
| Same logic on the model's eligible pool (74 x 65% x 20% x US price) | $4.1m |
| This model: peak net sales if reimbursed (2034) | $1.8m |
| This model: peak net sales, probability-weighted | $697k |

### Disagreements, and why

1. Price. US $425,000 is not a reference for Colombia: the ERP rule (p25 of 5 basket prices) gives $225,000 list, and procurement discounts, early-access pricing and the budget ceiling bring the blended net to $183,607 at peak (43% of US).

2. Geography. The originator has not filed here and lists no partner; the model agrees with that revealed preference and shows why: a 74-patient eligible pool, 37% probability of a paying route, INVIMA review of ~29 months and 12% expected bad debt.

### Agreements

- Persistence: originator reports 75% at 6 months at home; the model uses 75% annual on-therapy.

## SENSITIVITY: Saudi Arabia risk-adjusted NPV (base $111.9m)

| Driver | Low case | High case | Swing | Verdict |
| --- | ---: | ---: | --- | --- |
| Transfer price to originator | $67.6m | $156.2m | ############################## |  |
| Budget-impact ceiling | $60.0m | $126.4m | ###################### |  |
| Reimbursement probability | $66.2m | $129.1m | ##################### |  |
| Bad debt | $67.1m | $113.0m | ################ |  |
| Disease prevalence | $73.4m | $118.9m | ############### |  |
| Payer price sensitivity | $80.8m | $117.5m | ############ |  |
| Days sales outstanding | $93.5m | $117.4m | ######## |  |
| Label-eligible share | $93.3m | $116.9m | ######## |  |
| Share in specialist care | $93.3m | $116.9m | ######## |  |
| Persistence | $99.9m | $114.8m | ##### |  |
| Months to reimbursement | $101.7m | $114.7m | #### |  |
| Net price (discounts) | $104.9m | $113.7m | ### |  |
| ERP statistic (min vs p75) | $109.1m | $114.2m | ## |  |
| Launch opex | $109.6m | $113.1m | # |  |

'Low case' is the unfavourable end of each driver's range, 'High case' the favourable end; 'FLIPS' marks drivers that change the sign of the NPV on their own.

## SENSITIVITY: Colombia risk-adjusted NPV (base -$1.5m)

| Driver | Low case | High case | Swing | Verdict |
| --- | ---: | ---: | --- | --- |
| Launch opex | -$1.9m | -$1.3m | ############################## |  |
| Transfer price to originator | -$1.6m | -$1.4m | ########## |  |
| Bad debt | -$1.6m | -$1.5m | ####### |  |
| Payer price sensitivity | -$1.5m | -$1.5m | ### |  |
| Days sales outstanding | -$1.5m | -$1.5m | ### |  |
| Disease prevalence | -$1.5m | -$1.5m | ## |  |

'Low case' is the unfavourable end of each driver's range, 'High case' the favourable end; 'FLIPS' marks drivers that change the sign of the NPV on their own.

## BOTTOM LINE

Saudi Arabia: LAUNCH. Colombia: DO NOT LAUNCH.
Override any input with --set path=value (see data/countries/SA.json for paths); run a pipeline what-if with --indication SCD; print JSON with --json; refresh population/FX with --live.
