# Fixed numbers, their sources, and what a reviewer will not accept

Prepared 8 October 2026. Replaces `PARAMETER_SOURCES.md` of 7 October (archived). Read from the engine source
(`transit_kashmir_v3.py`, `extract_pois_kashmir.py`, plan version 3.4.5-geo), the analysis code, the module
outputs in `data/derived/`, the independent audit of 2–3 October and the source research of 5–6 October.

## How to use this document

Part 1 is the short answer. Part 2 ranks the fixed numbers by how much of the plan they decide. Part 3 is the
full register: every fixed number, where it came from, what it changes, and what would make it credible.
Part 4 lists what will not survive a serious review, with the reviewer's likely sentence and our best
response. Part 5 describes the ways the paper can fail. Part 6 is the work list.

Each number carries one of six grades.

| Grade | Meaning |
|---|---|
| **Standard** | A published manual, specification or study gives this value or a range containing it. |
| **Regulator** | Set in review with the transport regulator. A policy choice. |
| **Operator** | Taken from the e-bus operator's data or design. |
| **Fitted** | Tuned so the model reproduces the e-bus totals. |
| **Judgement** | Chosen by the authors. No source. |
| **Unsupported** | The code names a source that no project file holds. |

Sources marked **(checked)** were opened and read during the source research of 5–6 October. Sources marked
**(to check)** are quoted from memory of the standard literature. Nobody on the project has opened them for
this purpose, and each must be read before it is cited in the paper.

## Part 1 — the short answer

1. **Most of the fixed numbers are the authors' judgement.** A handful sit inside a published range, the
   headway rules were set with the regulator, a few come from the e-bus operator, one is fitted, two cite a
   source the project does not hold, and one is wrong. Part 3 grades each.
2. **The destination weights (hospital 1.0, school 0.4, tourist site 0.6) have no source, and they do not
   matter.** Changing them, re-tiering whole categories, or weighting every destination equally moves at most
   4 of 186 routes to another class.
3. **The larger problem with destinations is which tier each one was put in.** Every mapped place of worship
   was scored like a major hospital: 547 of the 1,030 top-tier destinations. This was not in the earlier
   parameter table. It also does not change the classes (at most 4 routes).
4. **The destination layer adds almost nothing to the index.** With destinations removed altogether, 173 of
   186 routes keep their class. The "composite" index is close to a population-density ranking. A reviewer
   can use this against us ("why have it?") and we can use it for us ("the judgement weights cannot have
   driven the result").
5. **Three sets of numbers decide the fleet, and none is derived.** The headway rules (15, 20, 35 and 50
   minutes), the cap on minutes per kilometre (which fixes the cycle time on 169 of 186 routes), and the
   15 % spare allowance. About half the fleet (503 of 1,011 buses) comes from the headway rules, not from
   estimated demand.
6. **The "demand-responsive" rural rule is in practice a 50-minute rule.** Of 67 rural routes outside the
   e-bus network, 62 sit at the 50-minute maximum and 5 at 35. None landed on 40 or 45.
7. **No independent check passes.** The building-footprint check is circular, the e-bus benchmark fails and
   is circular, the expert panel was not run, and the GPS check fails on travel time.
8. **The paper is still worth submitting if it argues what the evidence supports.** Four findings hold:
   614 permits are 157 corridors; straight-line catchments overstate reach; the speed cap, not the congestion
   model, sets the fleet; and the sensitivity ranking says which data to collect first. The paper fails if it
   claims a validated demand-based plan.

## Part 2 — which numbers decide the plan

| Rank | Number | What it decides | Measured effect | Basis |
|---|---|---|---|---|
| 1 | Headway rules: 15 / 20 / 35 / 50 min | Fleet on every route | Buses by headway: 283 at 15 min, 120 at 20, 303 at 35, 305 at 50. Sizing by estimated demand instead gives 551 buses | Regulator and operator |
| 2 | Cap on cycle time: 4.0 / 2.5 / 1.5 min per km | Cycle time on 169 of 186 routes | With the cap removed the same model gives 1,648 buses; at observed pace 1,130–1,266 | Judgement |
| 3 | Which permits merge (65 % overlap, start points within 2.5 km, and only into a cluster's lead route) | The route set itself | Among the 186 surviving routes, 207 pairs still pass the merge test with each other. Merging connected groups at a 50 % threshold leaves 84 routes and 533 buses | Judgement |
| 4 | Spare allowance: 15 % | Fleet total | 985–1,059 over 5–25 %; 94 % of the variance of the fleet as specified | Inside a published range |
| 5 | Walking distance: 400 m | Coverage | 20.3 % at 300 m to 34.5 % at 800 m; 97 % of the variance of coverage | Convention |
| 6 | Population-to-destination split: 50 : 50 | Route class | 20:80 to 80:20 moves at most 18 routes; 93 % of the variance of class stability | Judgement |
| 7 | Overrides on class (e-bus lock, social floor, district-headquarters floor) | Published class of about 44 routes | Published classes match the index-only classes on 68.3 % of routes (79.5 % without the e-bus routes) | Judgement and operator |
| 8 | Destination weights and tiers | Route class | At most 4 routes | Judgement |
| 9 | Congestion multipliers, dwell, bridge delay | Cycle time on the 17 routes the cap does not bind | Fleet 999–1,016 across their ranges | Judgement; one unsupported |

Everything below rank 4 changes little. A reviewer who reads Part 3 will still ask about each one, because
the paper presents them as a method.

## Part 3 — the register

### A. Destination scoring

The engine adds the weights of all destinations within 250 m of a route, divides by route length and scales
the result from 0 to 1 across routes.

| Number | Value | Grade | Where it came from | Effect | To make it credible |
|---|---|---|---|---|---|
| Tier 1 weight | 1.0 | Judgement | Reference level. 1,030 destinations | — | Expert survey (below) |
| Tier 2 weight | 0.4 | Judgement. The code's reason, "education drives about 30 % of women's ridership", is **Unsupported**: the e-bus data has no trip purpose | Raised from 0.2 in the Jammu version of the engine. 1,080 destinations | 0.2–0.6: no route changes class | Drop the stated reason. Expert survey |
| Tier 3 (seasonal) weight | 0.6 | Judgement | 321 destinations. No visitor counts were used | 0.3–0.9: 1 route changes class | Scale by published visitor numbers per site, or set equal to Tier 2 |
| Winter weights | 0.0 tourist-only; 0.4 others | Judgement | Winter switch is off in the published plan | Not used | Say that no winter plan exists |
| Weight if tier missing | 0.4 | Judgement | All 2,431 destinations carry a tier, so this never applies | None | State |
| Boost for women-oriented destinations | × 1.25 | Judgement, motivated by the 64.5 % women's share of e-bus boardings | Applies to 12 destinations (6 girls' schools, 4 maternity hospitals, 1 girls' college, 1 anganwadi) | Not tested; too few to matter | Remove it. It adds an undefended number for no effect |
| Search distance | 250 m | Judgement | Shorter than the 400 m used for residents; no reason recorded | Varied with stop spacing: up to 3 routes | Use the same distance as residents, or justify the difference |

**How destinations were put into tiers.** This is a second, larger set of judgements. The extraction script
first matches about 70 name patterns (SKIMS, Lal Ded, Hazratbal, Lal Chowk and so on), then falls back on the
OpenStreetMap tag.

| Rule in the script | Result in the data | Problem |
|---|---|---|
| Any place of worship → Tier 1, labelled "jamia_masjid" | 547 points, 53 % of Tier 1. 401 are not named Jamia or Jama. The label is applied to all religions; one sampled row is a temple | A neighbourhood mosque counts the same as SKIMS and 2.5 times a school |
| Shop tagged mall or department store → Tier 1 | 138 points, including small shops and office complexes | Kashmir does not have 138 malls |
| Any hospital tag → Tier 1 | 155 points, including primary health centres and one under construction | A primary health centre equals a tertiary hospital |
| Hotel, guest house or hostel → Tier 3 (0.6) | 240 points, including student hostels | A hotel outweighs a school (0.4) |
| Park → Tier 2 | 244 points | As many parks as schools (245) |
| Pharmacy → Tier 2 "small medical" | 80 points | A pharmacy equals a college |
| University tag → Tier 2 unless the name matches four listed universities | 47 colleges | Depends on spelling in OpenStreetMap |

Two thirds of all destinations are in Srinagar district, so the layer mostly measures how thoroughly
volunteers have mapped a place. Four routes have no destination within 250 m at all.

**Test run for this document** (`analysis/checks/poi_retier_check.py`; index-only classes, the engine's own
250 m rule; the baseline reproduces the analysis pipeline on 186 of 186 routes):

| Change | Routes changing class | Agreement |
|---|---|---|
| Places of worship not named Jamia/Jama: 1.0 → 0.4 | 1 | 99.5 % |
| Same, dropped | 2 | 98.9 % |
| All places of worship dropped | 4 | 97.8 % |
| Worship, shops and hotels all at 0.4 | 2 | 98.9 % |
| Worship and hotels dropped, shops at 0.4 | 4 | 97.8 % |
| Every destination weighted 1 | 3 | 98.4 % |
| No destination layer (population only) | 13 | 93.0 % |

These counts are for the index alone. The published classes also carry the overrides in group C.

**Can a source be found for such weights?** No manual gives per-category trip-attraction weights of this
kind. Three defensible routes exist:

1. *Elicit them.* A pairwise-comparison survey (the analytic hierarchy process, Saaty 1980 **(to check)**)
   with 5–8 people: regulator's officers, the e-bus operator, Prof. Kathuria. Report the consistency ratio and
   the plan's classes under the elicited weights. About 20 minutes per person.
2. *Derive them from data.* Trip-generation rates by land use exist for Indian cities in comprehensive
   mobility plans; the Srinagar plan by RITES would be the natural source if the regulator can supply it.
   The e-bus boardings by stop, if the operator can supply them, would allow a regression of boardings on
   nearby destinations. Neither is in the project today.
3. *Stop defending them.* Report the table above and say the layer is a minor adjustment to a density
   ranking. This costs nothing and is the honest position.

### B. Population and catchment

| Number | Value | Grade | Where it came from | Effect | To make it credible |
|---|---|---|---|---|---|
| Walking distance to a route | 400 m | Convention. The UN indicator for access to public transport uses 500 m **(checked)**. Daniels and Mulley (2013) find walking distance depends on supply **(checked)**. The usual citation, the *Transit Capacity and Quality of Service Manual*, could not be opened **(to check)**. India's 2009 benchmarks appear to set no walking distance **(to check)** | — | Coverage 20.3 % (300 m) to 34.5 % (800 m) | Cite the UN indicator and Daniels and Mulley. Report 400 m and 500 m side by side |
| Sampling interval along a route | 250 m | Judgement (a computing choice) | — | Coverage 23.3–24.9 % over 150–400 m | Report as a numerical setting |
| Off-network tolerance in the walking catchment | 100 m (one raster cell) | Judgement, paper's analysis only | Swept 50–150 m | Part of the 28.7–52.8 % range in straight-line overstatement | State; the range is already reported |
| Cap on population density before scaling | 95th percentile | Judgement | — | Not tested | Add to the sweep (90th–100th) |
| Tourist-corridor multiplier | × 1.3 | Judgement | Applied to the per-route resident count of 8 active routes | 1.0–1.8: no route changes class | Remove. Null effect, undefended number |
| Ceiling on a route's resident count | 2,000,000 | Judgement | A guard against errors | None | State |
| Population surface | WorldPop R2025A v1, constrained, 100 m | Standard (dataset). It is an **alpha release** and "may change" **(checked)** | — | Denominator 6,584,762. District totals are 0.71–1.20 of the 2011 Census | Say "alpha" and give the access date. Report district coverage with that error |

### C. Index and route class

| Number | Value | Grade | Where it came from | Effect | To make it credible |
|---|---|---|---|---|---|
| Population : destination split | 50 : 50 | Judgement | Equal weighting is the usual default discussed in the OECD handbook on composite indicators **(to check)** | 20:80 to 80:20: at most 18 routes change class | Report with the entropy weights (computed) and elicited weights |
| Scaling | Minimum–maximum | Standard method | — | Sensitive to outliers; partly handled by the 95th-percentile cap | State |
| Number of classes | 3, fixed in the engine | Judgement | The paper's rule "smallest number reaching a fit of 0.80" has no citation. Two classes score 0.786, three 0.902 | A threshold of 0.78 would give two classes | Say three classes were a design choice that the fit statistic supports; do not present the 0.80 rule as a derivation |
| Road-role multiplier | Trunk 1.25, feeder 0.75, other 1.00 | Judgement | Used only as a tie-break within 5 % of a class boundary | Not tested | Add to the sweep, or remove |
| Bonus for routes connecting to the e-bus network | × 1.5 | Judgement | Applied when choosing the lead route of a cluster | Not tested | Add to the sweep |
| Gate for promotion to trunk | 30th percentile of the index | Judgement, lowered from the 50th | Computed over all 644 rows, including duplicates | Not tested | Add to the sweep |
| Minimum trunk length | 5 km | Judgement | — | Small | State |
| E-bus routes locked to the top class | 30 routes | Operator | 20 of them fall in the lowest index class | Largest single cause of the 68.3 % agreement | Report both 68.3 % and 79.5 % |
| Social floor: lowest class raised to middle | 11 hand-listed places (4 migrant townships, 3 Srinagar hospitals, 4 district hospitals), 250 m | Judgement. The district hospitals of Baramulla, Bandipora, Kupwara, Kulgam and Shopian are not listed | 37 routes flagged | Not tested | List the places in the supplement; add the five missing district hospitals or explain |
| Route type by length | under 15 km urban; 15–40 km peri-urban; over 40 km regional | Judgement. The permit's vehicle category can override it | Decides the cap, the minimum fleet and the headway rule | Not tested | Replace with district and tehsil boundaries already in the project, or add to the sweep |

### D. Merging permits

| Number | Value | Grade | Effect | To make it credible |
|---|---|---|---|---|
| Buffer around route lines for overlap | 80 m | Judgement | Tested with the threshold | State |
| Share of length that must overlap | 65 % | Judgement | 0.50–0.90 swept for pair counts only: 354 to 90 qualifying pairs among surviving routes, 207 at 65 % | Report the route count and fleet at each value |
| Start points within | 2,500 m | Judgement | Removes about two thirds of overlapping pairs (614 pass on overlap alone at 65 %, 207 with this condition). Never varied | Add to the sweep |
| Merge only into the cluster's lead route | A rule, not a number | Judgement | **Large.** It is why 207 qualifying pairs remain unmerged. Merging connected groups at 50 % gives 84 routes and 533 buses, an upper bound with fleets not re-sized | Explain the rule in §4.6 and report the scenario beside it. This is the least-examined large choice in the plan |
| Corridor identity (endpoints hashed) | 11 m | Judgement | Gives 157 corridors | Report the count at 50 m and 100 m |
| Name-matching threshold for e-bus routes | 0.80, or one shared distinctive word | Judgement | Earlier value 0.45 wrongly matched 11 routes as e-bus routes; corrected before the published plan | None needed |

### E. Travel time and cycle time

| Number | Value | Grade | Where it came from | Effect | To make it credible |
|---|---|---|---|---|---|
| Congestion multiplier, city core | × 2.2 | **Unsupported.** The code cites "Srinagar Traffic Police bottleneck studies"; no such file exists | Raised from 1.4 after an internal audit | Fleet 1,003–1,014 over 1.6–2.8 | Never repeat the cited source. Replace with GPS speeds |
| Congestion multiplier, elsewhere | × 1.4 | Judgement | — | As above | Same |
| "City core" | Every point north of latitude 34.07 | Judgement, and wrong as geography | 170 of 186 routes are treated as city core, including routes in Kupwara and Baramulla | Hidden by the cap | Disclose. A reviewer who finds this unaided will distrust the rest |
| Stop spacing for time | 500 m | Inside the usual 400–600 m range **(to check)** | — | Fleet 1,001–1,016 over 300–800 m | Cite after checking |
| Time lost per stop | 0.5 min | Low. Observed in driver GPS: about 0.87 min per assumed stop | The code's own description says 1.5 | Fleet 999–1,016 over 0.3–1.5 | Use the observed value |
| Terminal layover | 10 % of running time | Inside the 10–15 % textbook range **(to check)** | Reduced from 15 % | Not tested | Cite after checking; add to the sweep |
| Penalty per sharp turn | 0.5 min above 75° | Judgement | — | Small | State |
| Jhelum crossing delay | 8 min, multiplied by the congestion factor | Judgement. The crossing test is a single line of longitude | — | Not tested | Measure from GPS runs that cross the river |
| **Cap on cycle time per km** | Urban 4.0, peri-urban 2.5, regional 1.5 min/km one way | Judgement. The code calls it a "sanity cap" | Implies at least 15, 24 and 40 km/h | **Binds on 169 of 186 routes.** Observed urban pace is 4.62 min/km at the median and 6.28 at the 90th percentile | See Part 4, item 2 |
| Fallback speeds and distance factors | 10 / 18 / 28 km/h; 1.25; 1.60 across the river | Judgement | Used only if the routing engine is down | Not used in the published run | State that they were not used |

### F. Headway and fleet

| Number | Value | Grade | Where it came from | Effect | To make it credible |
|---|---|---|---|---|---|
| Headway, e-bus routes | 15 min | Operator's stated design target. No document held | — | 283 buses | Obtain the operator's document |
| Headway, other high-class routes | 20 min | Regulator. The code also cites Bengaluru (10–15 min) and Mysuru (20–30 min) with no source | Was 15 | 120 buses | A written note from the regulator |
| Headway, other city routes | 35 min | Regulator ("one hour is too long") | Was 30 and 60 | 303 buses | Same |
| City maximum | 35 min | Regulator | — | — | Same |
| Rural steps | 35, 40, 45, 50 min | Regulator and lead author ("waits must not exceed about 50 minutes") | Earlier steps ran to 120 min | 62 of 67 routes sit at 50; none at 40 or 45 | Describe it as a 50-minute maximum wait. Do not call it demand-responsive |
| Target load on rural routes | 55 % | Judgement | — | Has no effect at the 50-minute maximum | Say so |
| Headway by permit category | "city bus" at least 20; "mps" at least 35; "regular" 35 | Judgement | Legacy from earlier versions | Not disclosed in the paper | Disclose or show it changes nothing |
| Spare allowance | 15 % | Inside the usual 10–20 % range **(to check)**. The code's "operator's target" has no document | India's road-transport undertakings had 87.6 % of buses on the road in 2019–20 and 72.3 % in 2021–22 **(checked)**, which implies 14 % and 38 % | Fleet 985–1,059 over 5–25 % | Cite the ministry's utilisation figures; they are Indian and already verified |
| Minimum buses per route | 2 urban and peri-urban; 1 regional | Judgement | — | Small | State |
| Maximum buses per route | 45 | Judgement | — | Rarely binds | State |
| E-bus fleet floor | Operator's deployed buses | Operator | Binds on 2 routes | With the five GPS-timed routes, the difference between 1,000 and 1,011 | Disclosed |
| Service day | 16 h in the plan; 11 h (13 h e-bus) in timetables | Judgement; timetable day from observed hours | — | Cost and trips | Settled |

### G. Vehicle mix

| Number | Value | Grade | Effect | To make it credible |
|---|---|---|---|---|
| Routes under 12 km | No full-size buses | Regulator and judgement | With the operator's own mix on e-bus routes, 25 of 32 trunks have none | State the rule as it is |
| Routes of 12 km or more | Full-size buses at most 50 % | Regulator ("neither class a majority"); was 85 %, then 60 % | Medium buses are the majority on 29 of 32 trunks | Already corrected in §4 |
| E-bus routes | Split scaled from the operator's 9 m and 12 m counts | Operator | Not disclosed | One sentence |
| Capacity | 60 / 35 / 20 passengers | Near India's Urban Bus Specifications **(to check)**; the 20 is judgement. The code calls 60 a "crush load" | Load factors only | Cite after checking |

### H. The ridership estimate (Eq. 8)

It affects load factors, the rural headway rule and the demand-sized fleet. It does not affect routes or
classes.

| Number | Value | Grade | Where it came from | To make it credible |
|---|---|---|---|---|
| Trips per person per day | 1.6 | Judgement; Indian city studies report lower values for cities of this size **(to check)** | Chosen with the mode share so the product matched the e-bus totals | Use a cited value; the fitted scale absorbs the change |
| Bus share of trips | 9 % urban; 7.2 % peri-urban; 5.4 % regional | Judgement. The 0.8 and 0.6 steps have no source | — | Cite a mode-share table, or state as assumption |
| Scale | 0.33 | Fitted | 11,632,326 e-bus boardings in May 2025–April 2026 ÷ 365 = 31,869 a day. Was 0.18 before the routes were re-geocoded | Fit on half the routes or months and test on the rest |
| Peak-hour share | 10.67 % of daily boardings | Operator data, April 2026 | One month, one operator, city routes only | State the scope |

The three numbers above multiply together, so only their product is identified. The estimate is fitted and
tested on the same 30 routes. At route level it does not rank the e-bus routes correctly (rank correlation
0.22, p = 0.24).

### I. Engine columns the paper does not use

Fare ₹10; operating cost ₹65 per km; subsidy threshold 0.6; long-journey flag 45 min; diesel 950 g CO₂ per
km; e-bus 30 g CO₂ per km (wrong by a factor of about 26 against grid-based figures); winter walking factor
0.65; winter service ratio 0.85. All judgement. One sentence in the supplement should say the paper
recomputes cost and emissions and ignores these columns.

### J. Settings in the paper's own analysis

| Setting | Value | Basis | Issue |
|---|---|---|---|
| Ranges and distributions in the uncertainty analysis | 12 inputs, uniform or triangular around the plan's value | Judgement | The output ranges are only as good as these choices. The dwell range was widened upward after seeing the GPS |
| Draws; seed | 5,000; 20260823 | — | Fine |
| Pass marks for the GPS check | error under 20 %, rank correlation over 0.5 | Judgement, written in the same commit as the first results | Cannot be called pre-registered |
| Pass mark for the e-bus benchmark | ± 15 % | Judgement; the engine's own check used ± 25 % | Same |
| Pass mark for the building check | rank correlation over 0.60 | Judgement; the building layer was changed after the first one failed | Disclosed |
| Plausible growth band for population check | 0.5–3.0 % a year | Judgement | 8 of 10 districts fall outside it |
| "Frequent" service | 15 min | Convention | Fine |
| Funded share in the staged-funding result | 30 % | Judgement | Report the whole curve |
| Target loads in the demand-sized fleet | 50 %, 70 %, 85 % | Judgement around textbook values | Fine as a range |
| Diesel economy, full-size bus | 3.5–5.0 km per litre | Named source not held. The ministry's review gives 1.95–5.66 for city undertakings **(checked)** | Replace with the checked range |
| Diesel economy, minibus; all costs per km | 7–10 km per litre; ₹25–90 per km | Judgement | Cost results stay "provisional" |
| E-bus energy, 12 m | 0.98–1.3 kWh per km | ITDP India 2022 **(checked)** | Fine. No 9 m figure exists |
| Grid emission factor | 0.675–0.705 kg CO₂ per kWh | Central Electricity Authority, version 22 **(checked)** | Fine |
| Kilometres per bus per day, national | 218.2 | Ministry review, 2021–22 **(checked)** | Fine |

### K. Fixed inputs that are data, not choices

| Input | Value | Caveat |
|---|---|---|
| Permit register | 614 records, from the regulator; 679 valid bus permits on 14 March 2026 | Not open data. The reduction of the regulator's 1,467 rows to these 614 is not described in the paper |
| E-bus aggregates | 30 routes, 98 buses, 11.63 million boardings, May 2025–April 2026 | Permission to publish not yet in writing |
| Driver GPS | 2,526 runs, about 157 devices, February–June 2026 | Consent screen added after collection. Around Srinagar only; two rural corridors |
| Road and footpath map | OpenStreetMap, northern-India extract of 6 January 2026 | Completeness uneven outside Srinagar |
| Destinations | 2,431 from OpenStreetMap | Two thirds in one district |
| Today's fleet | 777 = 679 + 98 | A valid permit is not proof a bus runs |

### L. Hand-made inputs that behave like parameters

These are not numbers in a configuration block, so earlier tables missed them. Each changes the plan.

| Input | What was done | Effect |
|---|---|---|
| Road distance on 49 routes | Replaced by values a language model researched from the web. No person checked them. The record keeps no source links | Fleet on those routes 247 → 207 |
| Village locations | 37 villages no geocoder could find were placed at their district's centre | 19 routes, 93 buses |
| Cycle time on 5 routes | Re-timed from driver GPS | Fleet 1,004 → 1,011. The same five routes are then used in the GPS check |
| The 30 e-bus routes | Typed in by hand, without intermediate points | Geometry and length of the routes carrying 283 buses |
| Route lines on 18 routes | Redrawn after the distance changes; 3 could not be reconciled | Catchments on those routes |
| Tourist zones | 19 hand-entered coordinates with 2 km and 0.6 km buffers | Which 8 routes get the × 1.3 |
| Version history | About 15 versions under regulator review; fleet between 855 and 1,144 | The plan is a negotiated outcome as much as a computed one |

## Part 4 — what will not survive review

Ordered by damage. "Cheap" means days of analysis with data already held.

### 1. The headways are not a result, and they produce half the fleet

*Reviewer:* "The frequencies are the regulator's preferences. By the authors' own estimate the median route
would run about one-ninth full at peak. What is the method contributing?"

*Why they are right.* 508 of 1,011 buses are explained by estimated demand at a 70 % load target; 503 by the
service standards. Median estimated peak load is 0.113, and 168 of 186 routes are below 0.40. On the e-bus
routes boardings would have to grow 2.2 to 4.5 times.

*What we can do.* Nothing analytical makes these numbers derived. Present them as service standards chosen
by the regulator, which is ordinary coverage-oriented planning (Walker's ridership-versus-coverage
distinction). Put the demand-sized fleet of 551 beside 1,011 in the abstract. Obtain one written line from
the regulator confirming the standards. Cite a level-of-service scale for headway **(to check)** so that
15 to 50 minutes can be placed on a published scale.

### 2. The speed cap is the model

*Reviewer:* "Equation 11 is decoration. On 91 % of routes the fleet is route length times a constant divided
by headway, and the constant has no source and is faster than the buses you measured."

*Why they are right.* The cap binds on 169 routes. It implies 15 km/h in the city; the observed median is
13 km/h and the slowest tenth is under 10 km/h. Rural pace was observed on two corridors only.

*What we can do (cheap).* Derive the urban and peri-urban caps from the GPS itself (for example the 75th
percentile of observed pace by class) and report the fleet under them. State the rural cap as untested.
Lead with the observed-pace fleet (1,130–1,266) wherever 1,011 appears.

### 3. Nothing independent validates the plan

*Reviewer:* "Four validation channels: one circular, one failed and circular, one not run, one failed."

*Why they are right.* WorldPop R2025A uses Microsoft building footprints as an input **(checked)**, so
agreement with them is expected. The e-bus benchmark tests the plan against the data it was tuned to and
fails the ± 15 % band. Travel time fails in sample (25.6 % error on 5 corridors) and out of sample (31.1 %
on 8). Route length passes on 5 corridors.

*What we can do.* Stop using the word "validation" for the footprint and e-bus checks; call them consistency
checks. The one channel that could be independent is the August field observation, and that needs the raw
sheets. A week of boarding counts at 10–15 stops would be worth more than any further modelling.

### 4. The index has no shown link to demand, and its second component is nearly inert

*Reviewer:* "A composite of two components correlated at 0.88, with arbitrary weights, never tested against
ridership. Why should its order mean anything?"

*Why they are right.* The only route-level test available gives a rank correlation of 0.22. Removing the
destination layer changes 13 routes. The tier assignment of destinations is crude (group A).

*What we can do (cheap).* Report the re-tiering table. Describe the index as a density ranking with a
destination adjustment. Remove the women's boost and the tourist multiplier, which add undefended numbers
for no effect. Run the expert survey if the regulator's officers are willing.

### 5. The plan cannot be regenerated, and parts of it were set by hand

*Reviewer:* "The released code produces 1,044 buses, not 1,011. Forty-nine distances came from a language
model with no sources."

*What we can do.* The provenance paragraph in §4.2 already discloses this. Add the fleet with the original
routed distances on those 49 routes as a sensitivity row (about 1,050 by simple addition of the 40 buses
removed; it has not been computed properly). Ship the correction logs. Say plainly
which results are reproducible (the analysis from frozen inputs) and which are not (the plan itself).

### 6. "Robust" is claimed for the wrong object

*Reviewer:* "97 % stability is the stability of your re-implementation's classes. The published classes
agree with it on 68 %."

*What we can do.* Already corrected in the numbers sheet. The abstract, §6 and §8 must lead with 68.3 % and
79.5 %, and explain that the gap is the e-bus lock.

### 7. The uncertainty ranges are not uncertainty about the fleet

*Reviewer:* "The spare allowance explains 94 % of the variance because the cap freezes everything else. The
route set, the cap, the headway rules and the number of classes are not sampled."

*What we can do (cheap).* Add the cap values, the merge conditions and the headway of the middle class as
scenario rows. Call 989–1,058 "the range under the plan's own rules".

### 8. The coverage headline depends on settings with no ground truth

Coverage is 24.2 % at 400 m, 20.3 % at 300 m and 34.5 % at 800 m. The straight-line overstatement ranges
from 28.7 % to 52.8 % across settings. The population surface is an alpha release with district errors up to
29 %. *Response:* report the ranges in the abstract, not a single figure.

### 9. Smaller points a careful reviewer will raise

- The "city core" is a line of latitude covering 170 of 186 routes.
- The 2.5 km merge condition and the lead-route rule are never varied, although the route set depends on them.
- The 30th-percentile trunk gate is computed over rows that include duplicates.
- Five district hospitals are missing from the social-floor list.
- The benchmark "44 buses per lakh" is a think-tank's blend, not a ministry figure **(checked)**.
- The peer-city regression explains 10 % of the variance and cannot discriminate any fleet.
- The 13,087 residents "losing access" is a proxy with a range of 3,822–13,087.
- All cost figures rest on unverified unit rates.

### 10. Matters outside the analysis that can end the paper first

Ethics and consent for the GPS; written permission for the e-bus data; the declaration of AI use, which must
now also cover the AI-researched distances; Srinagar-only scope and old counts in §1, §3 and §7; length.

## Part 5 — how the paper can fail

| Outcome | What triggers it | Likelihood as the draft stands | What removes the trigger |
|---|---|---|---|
| Rejected by the editor without review | Over length; blank ethics paragraph; section 1 contradicting the abstract on scope and counts; prose that reads as machine-drafted; "a local case study" | Real | Finish Part E of the decisions list; state the general contribution in the first paragraph |
| Rejected after review | A reviewer concludes the method is unsourced rules agreed with a regulator, with no successful validation, described as a demand-free planning method | Real if the framing stays | Reframe as an audit of an open-data plan: what such a plan can and cannot establish |
| Major revision | Reviewers accept the framing and ask for derived caps, an out-of-sample demand check, elicited weights and field counts | The best realistic first outcome | Do the cheap items in Part 6 before submission so the revision is small |
| Accepted, then challenged | Someone re-runs the public repository and gets 1,044, or finds mosques weighted as hospitals | Avoidable | Disclose both in the paper and the repository before anyone else does |

**The claims that hold up**, in the order a reviewer would rank them:

1. 614 permits describe 157 corridors, and a 71 % "route reduction" is almost entirely a change of unit.
2. Straight-line catchments overstate reach by 29–53 % depending on settings; coverage falls from 35.5 % to
   24.2 % at 400 m.
3. A per-kilometre cap, added as a safeguard, became the rule that sets the fleet. Measured against driver
   GPS it is too fast, and the fleet at observed pace is 12–25 % higher.
4. The plan's fleet is half demand and half service standard, and the paper can say which half is which.
5. Sensitivity analysis ranks what to measure first: bus speeds, then walking distance, then demand.

**The claims that do not hold up:** a demand-based or demand-validated plan; a validated plan of any kind; a
robust published hierarchy; an index that reflects demand; transferability shown by one case.

## Part 6 — work list

**Can be done now with data already held**

| # | Task | What it buys |
|---|---|---|
| 1 | Publish this register as the supplement's parameter table, with grades | Declared judgement is criticised far less than hidden judgement |
| 2 | Add the re-tiering table to §5 and describe the index as a density ranking with a destination adjustment | Closes the weights question |
| 3 | Derive urban and peri-urban caps from GPS and report the fleet under them | Replaces the weakest large number with a measured one |
| 4 | Fit the ridership scale on half the e-bus routes and test on the rest; repeat by month | Turns "fitted" into "fitted and tested", or shows honestly that it fails |
| 5 | Add to the sweep: the merge conditions, trunk gate, road multiplier, connection bonus, layover, bridge delay, population cap, route-type thresholds | Every untested number becomes a tested one |
| 6 | Fleet with the original routed distances on the 49 desk-checked routes | Bounds the effect of the least defensible input |
| 7 | Remove from the described method: women's boost, tourist multiplier, the "30 % of women's ridership" and "Traffic Police" statements | Fewer undefended numbers |
| 8 | Replace the diesel economy range with the ministry's checked figures | One fewer unverified cost constant |

**Needs a person**

| # | Task | Who |
|---|---|---|
| 9 | A written line confirming the headway standards were set in review | Regulator, through Avny ma'am |
| 10 | The operator's design headway, actual spare ratio, and whether a trip is counted one way | E-bus operator |
| 11 | Raw sheets of the August field observations | Avny ma'am |
| 12 | Pairwise-comparison survey for destination weights, 5–8 respondents | Lead author to circulate |
| 13 | A week of boarding counts at 10–15 stops, or stop-level e-bus boardings | Regulator or operator |
| 14 | Open and check every source marked "to check" | Any co-author with library access |

## Sources

**Checked on 5–6 October 2026** (details and links in the research notes): UN indicator 11.2.1 metadata;
Daniels and Mulley (2013), *Journal of Transport and Land Use* 6(2); Ministry of Urban Development (2009),
*Service Level Benchmarks for Urban Transport*, bands confirmed through ITDP India (2022); ITDP India (2022),
*Guidance for Electric Bus Rollout in Indian Cities*; Central Electricity Authority (2026), CO₂ baseline
database, version 22; Ministry of Road Transport and Highways, *Review of the Performance of State Road
Transport Undertakings 2019–20 to 2021–22*; WorldPop Global2 release statement R2025A; Microsoft Global ML
Building Footprints licence; Centre for Science and Environment and CITIES Forum (2026), *Reinventing the
Urban Bus*.

**To check before citing:** Transportation Research Board (2013), *Transit Capacity and Quality of Service
Manual*, 3rd edition (walking distance, stop spacing, dwell, headway level of service); Vuchic (2005), *Urban
Transit: Operations, Planning and Economics* (layover, spare ratio); Ceder (2007), *Public Transit Planning
and Operation* (layover); Ministry of Urban Development (2013), *Urban Bus Specifications II* (capacities);
Ministry of Urban Development (2008), study on traffic and transportation policies in urban India (trip
rates, mode shares); Saaty (1980), *The Analytic Hierarchy Process*; Walker (2012), *Human Transit*
(ridership and coverage goals); OECD (2008), *Handbook on Constructing Composite Indicators* (already in the
reference list).
