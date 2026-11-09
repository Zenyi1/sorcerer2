# L-glutamine oral powder (ENDARI) in Saudi Arabia (SA), indication SCD

Originator: Emmaus Life Sciences (NASDAQ: EMMA). Deal: Exclusive MENA commercialization partnership: partner bears all commercialization costs and pays milestones plus a high double-digit royalty on net sales with taiba Healthcare (Kuwait) (2019).

Perspective: launch partner P&L. Horizon: 2026-2035. Status here: filed 2021-05; decision expected ~2027.5 (SFDA), P(approval)=75%.

Evidence grades: [V] verified primary source, [R] reported/secondary, [C] originator's own figure, [A] our assumption, [O] command-line override, [M] model output.

## SUMMARY

Saudi Arabia: LAUNCH. 12,258 label-eligible adults, 56% chance of a paying route, first reimbursed sale 2028.5, peak $37.7m if reimbursed ($22.4m probability-weighted), risk-adjusted NPV $13.8m, payback 3 yr.

Colombia: DO NOT LAUNCH. 740 eligible, 37% chance of a paying route, first reimbursed sale 2030.9, peak $940k if reimbursed, risk-adjusted NPV -$1.5m, payback none in horizon.

Main disagreements with the originator: Price. Timing. Revealed uptake.

## INPUTS

### 1. Epidemiology and prevalence: label-eligible patients

| Step | Factor | Patients | Grade |
| --- | --- | --- | ---: |
| Adults in the epidemiology base | 19,600,000 x 66.5% adults | 13,034,000 | [V] |
| Prevalent disease (adults) | x 3.8 per 1,000 adults | 49,529 | [V] |
| Other label-covered forms (alpha-thal / HbH) | x 1.00 | 49,529 | [V] |
| Diagnosed | x 90% | 44,576 | [A] |
| Followed in a specialist centre | x 55% | 24,517 | [A] |
| Label-eligible (adult, >= 2 crises in the prior year) | x 50% | 12,258 | [A] |

Range on prevalence alone: 8,387 - 14,517 eligible adults; segment mix: single segment.

- Adults in the epidemiology base: GASTAT 2024: Saudis 55.6% of population
- Prevalent disease (adults): Premarital screening 2011-2015: SCD 49.6/1000 (45.8 trait, 3.8 disease)
- Other label-covered forms (alpha-thal / HbH): n/a
- Diagnosed: Screening programme
- Followed in a specialist centre: Large SCD population; milder Arab-Indian haplotype in Eastern Province
- Label-eligible (adult, >= 2 crises in the prior year): Phase 3 enrolled patients with >= 2 crises in the prior year; roughly half of adult SCD patients in care meet that in Saudi cohorts (the Arab-Indian haplotype in the Eastern Province is milder), fewer in Colombia's Pacific-coast population with poorer access. One value used for both.

Base note: Hemoglobinopathy burden is concentrated in Saudi nationals (Eastern Province, Jazan, Madinah). Expatriate carriers exist but are rarely reimbursed by the state; excluded.

### 2. Reimbursement and market access

Regulator: SFDA. Abridged/verification review for FDA- or EMA-approved products; Breakthrough Medicines Program for priority assets. Typical review 9 months [R]; P(approval | FDA/EMA approved) 95% [A].

System: Government-dominated. MoH hospitals (procured centrally through NUPCO), other government providers (KFSH&RC, National Guard, Ministry of Defense, university hospitals) with their own budgets, and a private sector funded by mandatory CHI health insurance for expatriates and private-sector employees. Hereditary blood disease centres sit in the Eastern Province (Qatif, Al-Ahsa, Dammam), Jazan, Madinah, Jeddah and Riyadh.

| Payer route | Patients | P(cover) | Months | From | Net/list | DSO d | Bad debt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MoH hospitals via NUPCO central procurement | 50% | 80% | 18 | 2029.2 | 80% | 120 | 0% |
| Other government providers (KFSH&RC, NGHA, MODA, universit | 33% | 85% | 10 | 2028.5 | 85% | 90 | 0% |
| Private sector, CHI-insured (Unified Drug Formulary) | 12% | 60% | 18 | 2029.2 | 95% | 75 | 2% |
| No payer (cash / uninsured) | 5% | 0% | - | - | - | - | - |

- moh_nupco: National procurement agreement is the gate Agios itself named ('over the next couple of years', Q3 2025). Tender discount vs SFDA list assumed 20%.
- other_gov: Institution-level formulary decisions; faster than NUPCO; these centres ran the ENERGIZE trials
- private_chi: Mostly expatriates and private-sector Saudis; insurers restrict high-cost orphan drugs

Early access before listing: 1.2% of eligible [R]. Blended P(a patient has a paying route) = 75%.

### 3. Competing therapies: peak share model (multinomial logit on efficacy, convenience, safety, price)

Payer utility weights here: efficacy 2.5, convenience 1.0, safety 1.0, price 0.8 [A]; standard of care gets a status-quo bonus of 1.5.

| Seg | Therapy | Here | Eff | Conv | Safe | Price/yr | Share |  |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| SCD | Hydroxyurea + supportive care (folate, analgesia, tr | available | 0.00 | 0.80 | 0.80 | $3k | 84.9% |  |
|  | L-glutamine (ENDARI, 6 packets of powder a day) | available | 0.20 | 0.55 | 0.90 | $35k | 11.4% |  |
|  | crizanlizumab (Adakveo, monthly IV) | limited | 0.25 | 0.50 | 0.80 | $100k | 2.7% |  |
|  | exagamglogene autotemcel (Casgevy, one-time gene edi | capacity_limited | 0.95 | 0.40 | 0.60 | $2m | 1.0% | cap |

Blended peak share of label-eligible patients = 11.4% (SCD 11.4% x 100%).

- Hydroxyurea + supportive care (folate, analgesia, transfusion as needed): Generic hydroxyurea is standard of care in both countries
- crizanlizumab (Adakveo, monthly IV): FDA 2019 on SUSTAIN (45% fewer crises); confirmatory STAND trial failed 2023 and the EU authorisation was revoked, so use is limited where still registered
- exagamglogene autotemcel (Casgevy, one-time gene editing): SFDA approval Jan 2024 for SCD >= 12y; one authorised centre so far

### 4. Pricing references: external reference price

Rule: SFDA Drug Pricing (2023 Drug Pricing Guidelines); statistic 'median' over basket US, DE, FR, GB, IT, ES, NL, SE, AT, PT, PL, HU, CA, AU, JP, KR; origin-country cap: True. Basket size has moved 30 -> 20 (2021) -> 16 (2022) per ISPOR 2023 poster; one 2024 source cites 34. The statistic (median vs lowest) is not fixed in public text: 'SFDA did not state that they will strictly select the lowest price'. Median of available basket prices, capped at the country-of-origin price, is used as the base case; 'min' is run in sensitivity.

| Ctry | Indication | Brand | USD/yr | Grade | In basket? |
| --- | --- | --- | --- | --- | --- |
| US | SCD | ENDARI | $42k | [R] | used |

ERP result: $42k per patient-year list (median of 1 basket price) = SAR 157,500 at 3.75 SAR/USD [V]. Standard of care costs $15k/yr [A].

- US ENDARI: Emmaus operational update: WAC $1,154 per 60-packet box from Q1 2020 (up from $1,110). An adult >= 65 kg takes 6 packets/day = 36.5 boxes/yr = ~$42k; ICER's 2020 draft modelled ~$24k/yr at label-average dosing. US generic L-glutamine (ANI) launched July 2024, so the US list price is a ceiling, not a floor.

### 5. Launch economics (partner view)

Transfer price to originator 65% of net sales [A]; logistics 6%; launch opex $900k/yr [A]; pre-launch opex $0/yr; upfront: Pricing / market-access dossiers, NUPCO and institutional listings $150k at approval; Pharmacovigilance, import licence, cold-chain / 3PL set-up $100k at approval. Cost of capital 10%. Persistence 78% [R]. Budget-impact ceiling 1.0% of a $10.7bn drug market = $107m/yr public spend [A].

## OUTPUT: 10-YEAR FORECAST, Saudi Arabia

| Year | Eligible | Access | Uptake | Pts(succ) | Pts(exp) | Net $/pt | Sales(succ) | Sales(exp) | Cash(exp) | Cum cash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026 | 12,258 | 0% | 0% | 0 | 0 | $35k | $0 | $0 | $0 | $0 |
| 2027 | 12,442 | 0% | 5% | 5 | 4 | $42k | $204k | $153k | -$559k | -$559k |
| 2028 | 12,629 | 1% | 15% | 118 | 89 | $42k | $5.0m | $3.7m | $405k | -$155k |
| 2029 | 12,818 | 50% | 37% | 270 | 174 | $33k | $8.9m | $5.8m | $840k | $686k |
| 2030 | 13,011 | 95% | 65% | 727 | 433 | $32k | $23.0m | $13.7m | $2.9m | $3.5m |
| 2031 | 13,206 | 95% | 86% | 968 | 576 | $32k | $30.6m | $18.2m | $4.0m | $7.6m |
| 2032 | 13,404 | 95% | 95% | 1,087 | 647 | $32k | $34.4m | $20.4m | $4.6m | $12.2m |
| 2033 | 13,605 | 95% | 98% | 1,141 | 679 | $32k | $36.1m | $21.4m | $4.9m | $17.1m |
| 2034 | 13,809 | 95% | 100% | 1,170 | 696 | $32k | $37.0m | $22.0m | $5.0m | $22.1m |
| 2035 | 14,016 | 95% | 100% | 1,192 | 709 | $32k | $37.7m | $22.4m | $5.1m | $27.2m |

'succ' = if registered and every modelled payer route pays; 'exp' = probability-weighted (registration x coverage).

### Key metrics

| Metric | Value |
| --- | --- |
| Label-eligible adults (range) | 12,258 (8,387 - 14,517) |
| Peak competitive share | 11.4% |
| List price (ERP) / net at peak | $42k / $32k per patient-year |
| First sale / first reimbursed sale | 2027 / 2028.5 |
| Patients on therapy at peak (succ / exp) | 1,192 / 709 in 2035 |
| Peak net sales (succ / exp) | $37.7m / $22.4m |
| Cumulative net sales, horizon (exp) | $127.6m |
| P(registration) x P(paying route) | 75% x 75% = 56% |
| Risk-adjusted NPV (exp) / NPV (succ) | $13.8m / $24.2m |
| Payback from first sale | 3 years |

### Verdict: LAUNCH

| Rule | Value | Threshold | Result | Type |
| --- | --- | --- | --- | --- |
| Risk-adjusted NPV (expected) | $13.8m | >= $0m | pass | hard |
| Peak net sales if reimbursed | $37.7m | >= $3m | pass | hard |
| P(registered and reimbursed) | 56% | >= 50% | pass | hard |
| Payback from first sale | 3 yr | <= 5 yr | pass | soft |
| Patients on therapy at peak | 1,192 | >= 20 | pass | soft |

## COMPARE: Saudi Arabia vs Colombia

|  | Saudi Arabia | Colombia |
| --- | --- | --- |
| Verdict | LAUNCH | DO NOT LAUNCH |
| Status | filed 2021-05; decision expected ~2027.5 (SFDA), | not filed; file 2027.0, decision ~2029.4 (INVIMA |
| Label-eligible adults | 12,258 | 740 |
| P(registered) x P(paying route) | 56% | 37% |
| First reimbursed sale | 2028.5 | 2030.9 |
| List price (ERP) | $42k | $42k |
| Net price at peak | $32k | $34k |
| Peak share | 11.4% | 5.0% |
| Patients at peak (succ) | 1,192 | 27 |
| Peak net sales (succ / exp) | $37.7m / $22.4m | $940k / $358k |
| Risk-adjusted NPV | $13.8m | -$1.5m |
| Payback | 3 yr | none in horizon |
| Expected bad debt | 0% | 12% |

### Why: multiplicative decomposition of peak-year net sales (SA / CO)

| Factor | SA | CO | Ratio |
| --- | ---: | ---: | ---: |
| Label-eligible adults (peak year) | 14,016 | 776 | 18.06x |
| Share with a paying route at peak | 95.1% | 98.0% | 0.97x |
| Peak competitive share | 11.4% | 5.0% | 2.27x |
| Uptake reached by peak year | 99.9% | 95.4% | 1.05x |
| Persistence on therapy | 78.0% | 75.0% | 1.04x |
| Net price per patient-year | $32k | $34k | 0.92x |
| = Peak net sales (success case) | $38m | $940k | 40.14x |
| memo: collected share (1 - bad debt) | 99.7% | 88.0% | 1.13x |
| memo: years from decision to first reimbursed sale | 2.5 | 4.9 |  |

The factor ratios above the '=' line multiply to the peak-sales ratio, so the gap can be attributed line by line. Memo lines are not in the product: collections hit cash rather than sales, and timing hits the NPV through the years lost to registration and listing.

## WHERE THE MODEL DISAGREES WITH EMMAUS' OWN STATED NUMBERS: Saudi Arabia

### Patients

| Step | Patients | Grade |
| --- | ---: | ---: |
| Model: prevalent adults with disease | 49,529 | [V] |
| Diagnosed | 44,576 | [M] |
| Followed in a specialist centre | 24,517 | [M] |
| Label-eligible (adult, >= 2 crises in the prior year) | 12,258 | [M] |
| With a paying route at peak (2035, if reimbursed) | 11,653 | [M] |
| Choosing this therapy (peak competitive share) | 1,332 | [M] |
| Still on therapy (persistence) | 1,192 | [M] |

- Model: prevalent adults with disease: No originator patient figure covers this country. Anchor: Saudi national premarital screening data (3.8 sickle cell disease per 1,000 adults screened, 2011-2015).
- With a paying route at peak (2035, if reimbursed): 95% of eligible; uncovered and not-yet-listed payers excluded
- Choosing this therapy (peak competitive share): 11% vs standard of care and crizanlizumab, exagamglogene autotemcel
- Still on therapy (persistence): x 78%

### Price per patient-year

| Step | USD | Grade |
| --- | ---: | ---: |
| Originator: US price per patient-year | $42k | [R] |
| Model: Saudi Arabia list price after external reference pricing | $42k | [M] |
| Model: blended net price at peak (tenders, formulary discounts, budget cap, FX) | $32k | [M] |

- Model: Saudi Arabia list price after external reference pricing: median of 1 basket price
- Model: blended net price at peak (tenders, formulary discounts, budget cap, FX): budget-impact ceiling not binding

### Revenue comparators

| View | Per year |
| --- | ---: |
| Naive TAM: prevalent patient figure x US price | $2.1bn |
| This model: peak net sales if reimbursed (2035) | $37.7m |
| This model: peak net sales, probability-weighted | $22.4m |

### Disagreements, and why

1. Price. US $42,000 is not a reference for Saudi Arabia: the ERP rule (median of 1 basket price) gives $42,000 list, and procurement discounts, early-access pricing and the budget ceiling bring the blended net to $31,647 at peak (75% of US).

2. Timing. Originator: 'Endari received market exclusivity in the Kingdom of Saudi Arabia through NUPCO; the marketing authorization application is awaiting final action by the SFDA; Emmaus continues to supply GCC patients through its early access program' (Emmaus press release, 2025). The model has the first paying route in 2028.5, MoH hospitals via NUPCO central procurement coverage from 2029.2, and peak uptake only in 2035. Revenue before that is early-access, hospital-budget business.

3. Revealed uptake. At home the asset reached about 1.0% of prevalent patients (Emmaus net revenue has run at roughly $25-30m a year against ~100,000 US SCD patients, i.e. on the order of 1% of prevalent patients on therapy seven years after approval); the model's 11% peak share of label-eligible patients here (2.8% of prevalent) is far above that and rests on the competitive set and payer weights printed in the inputs. Treat it as the upper half of the range.

### Agreements

- Emmaus and taiba put their Gulf effort into Saudi Arabia (priority review, NUPCO exclusivity, early access); the model also finds it the only one of the two countries worth a dedicated effort.

## WHERE THE MODEL DISAGREES WITH EMMAUS' OWN STATED NUMBERS: Colombia

### Patients

| Step | Patients | Grade |
| --- | ---: | ---: |
| Model: prevalent adults with disease | 4,110 | [A] |
| Diagnosed | 2,466 | [M] |
| Followed in a specialist centre | 1,480 | [M] |
| Label-eligible (adult, >= 2 crises in the prior year) | 740 | [M] |
| With a paying route at peak (2034, if reimbursed) | 725 | [M] |
| Choosing this therapy (peak competitive share) | 36 | [M] |
| Still on therapy (persistence) | 27 | [M] |

- Model: prevalent adults with disease: No originator patient figure covers this country. Anchor: no national count exists for Colombia; the estimate rests on the Afro-Colombian population share and patient-group figures.
- With a paying route at peak (2034, if reimbursed): 98% of eligible; uncovered and not-yet-listed payers excluded
- Choosing this therapy (peak competitive share): 5% vs standard of care and crizanlizumab
- Still on therapy (persistence): x 75%

### Price per patient-year

| Step | USD | Grade |
| --- | ---: | ---: |
| Originator: US price per patient-year | $42k | [R] |
| Model: Colombia list price after external reference pricing | $42k | [M] |
| Model: blended net price at peak (tenders, formulary discounts, budget cap, FX) | $34k | [M] |

- Model: Colombia list price after external reference pricing: p25 of 1 basket price
- Model: blended net price at peak (tenders, formulary discounts, budget cap, FX): budget-impact ceiling not binding

### Revenue comparators

| View | Per year |
| --- | ---: |
| Naive TAM: prevalent patient figure x US price | $172.6m |
| This model: peak net sales if reimbursed (2034) | $940k |
| This model: peak net sales, probability-weighted | $358k |

### Disagreements, and why

1. Price. US $42,000 is not a reference for Colombia: the ERP rule (p25 of 1 basket price) gives $42,000 list, and procurement discounts, early-access pricing and the budget ceiling bring the blended net to $34,276 at peak (82% of US).

2. Revealed uptake. At home the asset reached about 1.0% of prevalent patients (Emmaus net revenue has run at roughly $25-30m a year against ~100,000 US SCD patients, i.e. on the order of 1% of prevalent patients on therapy seven years after approval); the model's 5% peak share of label-eligible patients here (0.9% of prevalent) is far above that and rests on the competitive set and payer weights printed in the inputs. Treat it as the upper half of the range.

3. Geography. The originator has not filed here and lists no partner; the model agrees with that revealed preference and shows why: a 740-patient eligible pool, 37% probability of a paying route, INVIMA review of ~29 months and 12% expected bad debt.

### Agreements

- No originator statements about this country were found to agree or disagree with beyond price.

## BOTTOM LINE

Saudi Arabia: LAUNCH. Colombia: DO NOT LAUNCH.
Override any input with --set path=value (see data/countries/SA.json for paths); run a pipeline what-if with --indication SCD; print JSON with --json; refresh population/FX with --live.
