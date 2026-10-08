# Fixed parameters of the planning engine: where each number comes from

Prepared 7 October 2026 from the engine source (`transit_kashmir_v3.py`, plan version 3.4.5) and the
paper's sensitivity analyses. It covers every fixed number that shapes the plan: 56 entries in seven groups. Of these, 39 are the
authors' judgement, 8 rest on a published manual or specification, 6 were set with the regulator, 1 is
fitted, 1 cites a source the project does not hold, and 1 is wrong (and unused by the paper).

## How to read this

Each parameter is given one of five grades for its present basis.

| Grade | Meaning |
|---|---|
| **Standard** | A published planning manual or study gives this value or a range containing it. |
| **Regulator** | Set in review with the transport regulator. A policy choice, reported as such. |
| **Fitted** | Tuned so the model reproduces the e-bus operator's published totals. |
| **Judgement** | Chosen by the authors. No source. |
| **Unsupported** | The code comment names a source, but that source is not in any project file. |

References marked † are quoted from memory of the standard literature and have not been opened in this
round. Each must be checked against the document before it is cited in the paper.

## The short answer

1. **The scoring weights (hospital, market, school and so on) have no published source.** They are the
   authors' judgement. No Indian or international manual gives per-category weights of this kind.
2. **They also barely matter.** Moving the second-tier weight across 0.2–0.6, the third-tier weight across
   0.3–0.9 and the tourist multiplier across 1.0–1.8 changes the class of at most 1 route in 186. This
   measured insensitivity is the strongest defence available, and it is already computed.
3. **The numbers that do matter are different ones.** The fleet total is driven by the spare ratio (94 % of
   its variance), the headway rules, and the cap on minutes per kilometre, which binds on 169 of 186 routes.
   Coverage is driven by the walking distance (20.3 % at 300 m to 34.5 % at 800 m).
4. **Two code comments cite evidence the project does not hold** (congestion multipliers and the education
   share of women's trips). Neither claim should appear in the paper.

## Recommendations, in order of value

| # | Action | Effort | What it buys |
|---|---|---|---|
| 1 | Publish the full parameter table as a supplement, with the grade of each number, and say plainly in §4 that the weights are judgement. | Done in this document | Reviewers penalise hidden judgement, not declared judgement. |
| 2 | Lead with the sensitivity result: the weights change at most 1 route's class. | Already computed | Makes the source of the weights a minor question. |
| 3 | Run a short structured expert survey (pairwise comparison, the AHP method) with 5–8 people: the regulator's officers, Prof. Kathuria, the e-bus operator. Report the consistency ratio and the resulting weights beside the judgement weights. | One form, about 20 minutes each | Turns "authors' judgement" into "elicited from local experts", which is the accepted practice for such indices. |
| 4 | Report the data-derived weights (entropy method) already computed for the population-versus-destination split, and show the plan's classes under them. | Already computed | An objective alternative with no judgement. |
| 5 | Replace the congestion multipliers and the minutes-per-kilometre cap with speeds measured from the drivers' GPS, by zone. | Needs an engine re-run; say so as future work if not done | Removes the weakest travel-time inputs. The paper already reports that observed speeds would need 1,130–1,266 buses. |
| 6 | Check the e-bus fit on data it was not fitted to (fit on some routes or months, test on the rest). | Small analysis | The demand scale is currently fitted and tested on the same totals. |
| 7 | Delete the two unsupported claims from code comments and never repeat them in text. | Minutes | Removes a claim that cannot be backed. |

## Group 1 — Destination scoring (the "hospital versus market" numbers)

The engine sorts destinations into three tiers and adds their weights within 250 m of a route.

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Tier 1 weight: major hospitals, bus and rail terminals, main markets and malls, large shrines, industrial estates, secretariat and courts, university campuses, migrant townships | 1.0 | Judgement | Reference level | Expert survey (action 3) |
| Tier 2 weight: schools and colleges, local markets, clinics, government offices, stadiums, parks, security establishments | 0.4 | Judgement. The comment's reason ("education drives about 30 % of women's ridership") is **Unsupported**: the operator data has no trip purpose. | 0.2–0.6: no route changes class | Expert survey; drop the stated reason |
| Tier 3 weight: tourist sites, gardens, lake gates (summer) | 0.6 | Judgement | 0.3–0.9: 1 route changes class | Expert survey; or scale by published visitor counts per site |
| Tier 3 weight in winter | 0.0 tourist-only; 0.4 residential anchors | Judgement | Not used: the published plan is the summer run | State that no winter plan is published |
| Unlisted category | 0.4 (treated as Tier 2) | Judgement | Small | Report how many destinations fall here |
| Boost for women-oriented destinations (women's colleges, maternity hospitals) | ×1.25 | Judgement, motivated by the 64.5 % women's share of e-bus boardings under free travel | Not separately tested | Add to the sensitivity sweep, or remove |
| Search distance for destinations | 250 m | Judgement | Varied together with stop spacing: up to 3 routes change class | Tie to the walking-distance source below |
| Which category sits in which tier | Lists in the code | Judgement | Same as the weights | Publish the lists in the supplement; include in the expert survey |

## Group 2 — Population and catchment

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Walking distance to a route | 400 m | Standard: 400 m (about 5 minutes) is the usual bus catchment in TRB's *Transit Capacity and Quality of Service Manual*, 3rd ed. (2013)†; El-Geneidy et al. (2014)† measured a longer median for bus | Coverage 20.3 % (300 m) to 34.5 % (800 m); up to 3 routes change class | Cite both; keep the range in the text |
| Spacing of sample points along a route for catchment | 250 m | Judgement (a computing choice) | Coverage 23.3–24.9 % over 150–400 m | Report as a numerical setting |
| Cap on population score | 95th percentile | Judgement (limits outliers before scaling) | Not tested | State it; standard practice in index building |
| Tourist-corridor population multiplier | ×1.3 | Judgement | 1.0–1.8: no route changes class | Report the null effect; or drop the multiplier |
| Population grid | WorldPop 2025, constrained, 100 m | Standard (dataset) | Sets the 6.58 million denominator | Already cited with DOI |

## Group 3 — Priority index and route class

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Weight of population versus destinations in the index | 50 : 50 | Judgement | 20:80 to 80:20: at least 90.3 % of routes keep their class (at most 18 change) | Report beside the entropy-method weights (action 4) and the expert weights (action 3) |
| Road-role multiplier | Trunk 1.25, feeder 0.75, other 1.00 | Judgement | Not separately tested | Add to the sweep, or justify from the road classes used |
| Bonus for routes connecting to the e-bus backbone | ×1.5 | Judgement | Not separately tested | Add to the sweep |
| Index gate for promotion to trunk | 30th percentile | Judgement | Reported in the class-count analysis | State as a design choice |
| Minimum length for a trunk | 5 km | Judgement | Small | State |
| Urban / peri-urban / regional split by length | under 15 km / 15–40 km / over 40 km | Judgement | Decides which headway rule a route gets | Consider replacing with the district and tehsil boundaries already in the project |

## Group 4 — Merging overlapping permits

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Width within which two routes count as sharing a road | 80 m | Judgement | Tested with the threshold below | State; a corridor width, wider than GPS and map error |
| Share of length that must overlap to merge | 65 % | Judgement | Swept 0.50–0.90 in the sensitivity table | Report the number of merges across the sweep |
| End-point closeness for the same corridor | 2,500 m | Judgement | Not tested | Add to the sweep |
| Width for stop merging in route codes | 150 m | Judgement | Naming only | None needed |

## Group 5 — Travel time and cycle time

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Congestion multiplier, city core | ×2.2 | **Unsupported**: the comment cites "Srinagar Traffic Police bottleneck studies", which are not in the project | Fleet 1,003–1,014 over 1.6–2.8, because the cap below overrides it on most routes | Replace with GPS-measured speeds (action 5); delete the cited source |
| Congestion multiplier, peri-urban | ×1.4 | Judgement | As above | Same |
| City-core boundary | north of latitude 34.07 | Judgement (a single line on the map) | Sets which routes get ×2.2 | Replace with a mapped zone |
| Stop spacing for time penalty | one per 500 m | Standard range: manuals give roughly 400–600 m for urban bus stops (TRB 2013†) | Fleet 1,001–1,016 over 300–800 m | Cite |
| Time lost per stop | 0.5 minute | Standard range: TRB (2013)† suggests 15–60 seconds by stop type | Fleet 999–1,016 over 0.3–1.5 minutes | Cite |
| Terminal layover | 10 % of running time | Standard range: 10–15 % in Vuchic (2005)† and Ceder (2007)† | Not separately tested | Cite |
| Penalty per sharp turn (over 75°) | 0.5 minute | Judgement | Small | State |
| Jhelum bridge delay | 8 minutes per crossing | Judgement | Not separately tested | Measure from GPS runs that cross the river |
| Cap on cycle time per km | Urban 4.0, peri-urban 2.5, regional 1.5 minutes per km one way | Judgement (implies at least 15, 24 and 40 km/h) | **Large.** The cap binds on 169 of 186 routes; without it the fleet would be 1,400–2,400 | Already disclosed. Replace with measured speeds, or keep and report the observed-speed fleet beside it |
| Fallback speeds if the routing engine is unavailable | 10 / 18 / 28 km/h | Judgement | Not used in the published run | State that they were not used |
| Straight-line to road-distance factor (fallback) | 1.25; 1.60 across the river | 1.25 is within the published range for road networks (Ballou et al. 2002†); 1.60 is Judgement | Not used in the published run | Same |

## Group 6 — Headway, fleet and vehicles

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Headway, e-bus backbone | 15 minutes | Regulator / operator's design target | Sets 283 of 1,011 buses | Obtain the operator's document stating the target |
| Headway, other trunks | 20 minutes | Regulator | Direct | Cite the review; confirm wording with the Administrative Secretary |
| Headway, feeders and lifelines | 35 minutes | Regulator | Direct | Same |
| Maximum headway, city | 35 minutes | Regulator | Direct | Same |
| Rural headway steps | 35, 40, 45, 50 minutes | Regulator (50-minute maximum wait) | Rural fleet | Same |
| Target load on rural routes | 55 % | Judgement | Rural fleet | Add to the sweep; the demand-sized analysis already tests 70 % |
| Spare buses | 15 % | Standard range: 10–20 % in transit practice (Vuchic 2005†); the comment's "operator's target" is not documented | **Largest single driver:** fleet 985–1,059 over 5–25 % | Cite the range; ask the operator for its actual spare ratio |
| Minimum buses per route | 2 urban, 1 regional | Judgement | Small routes | State |
| Maximum buses per route | 45 | Judgement | Rarely binds | State |
| Large-bus share on a trunk | at most 50 % | Regulator | Vehicle mix only, not the total | Cite the review |
| Vehicle capacity | 60 / 35 / 20 passengers | Close to India's Urban Bus Specifications II (2013)† for 12 m and 9 m buses; minibus figure is Judgement | Load factors only | Cite the specification |
| Service day | 16 hours in the plan; 11 h (13 h e-bus) in timetables | Judgement; timetable day from observed operating hours | Cost and trips | Settled: paper uses 11 h / 13 h, reports 16 h as nominal |

## Group 7 — Demand, economics and emissions

These feed the load, cost and emission columns. They do not affect routes, classes, headways or the fleet.

| Parameter | Value | Grade | Effect on the plan | To make it credible |
|---|---|---|---|---|
| Trips per person per day | 1.6 | Judgement; Indian city studies report roughly 0.8–1.5 (Ministry of Urban Development 2008†), so this is high | Absorbed by the fitted scale below | Use a cited value; the fitted scale will adjust |
| Bus share of trips | 9 % urban; 7.2 % peri-urban; 5.4 % regional | Judgement (the 0.8 and 0.6 steps have no source) | Absorbed by the fitted scale for urban routes; not checked for the others | Cite a city-size mode-share table, or state as assumption |
| Demand scale | 0.33 | Fitted to the e-bus annual boardings (11.63 million) | Sets all load factors | Out-of-sample check (action 6) |
| Fare | ₹10 per trip | Judgement | Engine's revenue column only | The paper does not use it; say so |
| Operating cost | ₹65 per km | Judgement | Engine's cost column only | The paper uses its own cost ranges with sources |
| Subsidy-risk threshold | 0.6 fare recovery | Judgement | A flag only | State |
| Long-journey flag | 45 minutes | Judgement | A flag only | State |
| Diesel emission factor | 950 g CO2 per km | Judgement | Engine's column only | The paper recomputes emissions by vehicle class |
| E-bus emission factor | 30 g CO2 per km | **Wrong** by a factor of about 26 against grid-based figures | Engine's column only | Already disclosed; the paper does not use it |
| Winter walking-distance shrink; winter service ratio | 0.65; 0.85 | Judgement; the second is described as "operator observed" without a file | Not used in the published plan | State that winter is not modelled |

## What the paper should say

A wording that is accurate and defensible:

> The engine has 56 fixed parameters (Supplementary Table S-P). Eight rest on planning manuals or published
> specifications, six were set in review with the transport regulator, one is fitted to operator totals, and
> the rest are the authors' judgement. Destination weights are judgement; varying them across their plausible ranges
> changes the class of at most one route in 186. The fleet total is governed by the spare ratio, the
> headway rules and the cap on cycle time per kilometre, each of which is varied in Section 5.

The counts are those of the tables above and should be re-checked if the supplement table changes.

## References to verify before citing (†)

- Ballou, Rahardja and Sakai (2002), circuity factors for road distance, *Transportation Research Part A*.
- Ceder (2007), *Public Transit Planning and Operation*.
- El-Geneidy et al. (2014), walking distance to transit, *Transportation*.
- Ministry of Urban Development (2008), study on traffic and transportation policies and strategies in urban areas in India.
- Ministry of Urban Development (2013), *Urban Bus Specifications II*.
- Saaty (1980), *The Analytic Hierarchy Process* (for the expert survey).
- Transportation Research Board (2013), *Transit Capacity and Quality of Service Manual*, 3rd edition.
- Vuchic (2005), *Urban Transit: Operations, Planning and Economics*.
