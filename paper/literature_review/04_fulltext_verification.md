# 04 — Full-text verification of the five closest papers

**Date:** 2026-10-01 · **Input:** `03_novelty_check.md` (§A rows 1–5, §B) · **Sources:** the five extracted `.txt` files in `lit_review/pdfs/` plus the PDFs next to them.

**Verdict in one line:** None of the five papers invalidates SAFE claims 1–5 in `03_novelty_check.md` §B(a). Three findings from the full texts narrow the gap more than the abstracts suggested, so the first two novelty sentences in §B(c) must be reworded (final wording in §7) and the §A table needs six corrections (§6).

The three findings that matter:

1. **Sánchez-Atondo et al. (2026) design their network without any demand data.** Their Module 2 groups routes whose alignments overlap or run parallel within 200 m and keeps the trunk (or best-connected route) of each group. Their Module 3 sets headways from a minimum service frequency and the frequencies of the existing overlapping routes. The origin–destination survey enters only in the evaluation phase, which the authors call optional. This is a close precedent for our consolidation step and for demand-free headway setting.
2. **Mittal & Ukkusuri (2025) assign headways by usage quantile** (2 min for the top decile to 60 min for the bottom decile). This is an ordinal-tier headway rule, although the usage measure comes from proprietary mobile-phone trip flows.
3. **Mittal & Ukkusuri (2025) use WorldPop population density and OSM POI density per road segment** (500 m buffer), which are the same two ingredients as our CDI. They are two of several classifier features, not a standalone index.

---

## 0. What was read, and limits

| Paper | Text read | Figures and tables inspected from the PDF page images | Not inspected |
|---|---|---|---|
| Sánchez-Atondo 2026 | All 16 pages, including references | Figs. 4, 5, 6 (the three module flowcharts and their rule tables), Fig. 7, Table 4 | Figs. 1–3, 8–11 (captions only) |
| Ruiz 2017 | All 14 pages (pp. 220–233), including references | Table 2, Fig. 10 | Figs. 1–9, 11 (captions only) |
| Barzegari 2026 | All 20 pages, including references | none | Figs. 1–20 (captions only) |
| Dumedah 2023 | pp. 1–11 body text, data-availability statement | none | Figs. 1–6 (captions only); reference list (pp. 11–12) not read |
| Mittal & Ukkusuri 2025 | pp. 1–19 body text, data-availability statement | none | Figs. 1–8 (captions only); reference list (pp. 19–21) not read |

**Garbled extraction.** These passages could not be read reliably and nothing below depends on them:
- Mittal & Ukkusuri: the classification function (p. 7), the pseudo-label selection rule (p. 9), the operational alignment score formula (p. 10), parts of the edge-use probability and route score definitions (p. 11) and the accessibility formula (p. 13). The surrounding prose defines each of them and was readable.
- Ruiz: equations (1)–(9) are broken across lines but legible. In Table 3 (p. 231) the digits of adjacent columns are fused, so I did not transcribe individual optimised headways. The column totals (745 min) and the service-level and Gini summary rows are legible.
- Barzegari: equations are split across lines but legible.

**Quotations.** Three of the five papers are all-rights-reserved (Ruiz, Dumedah, Mittal & Ukkusuri). I have therefore paraphrased throughout and given page and section locators instead of the ≤25-word quotes requested, with one short verbatim quote (§5). Every paraphrase can be checked at the locator given. Page numbers are PDF page numbers for the three article-number papers and journal page numbers for Ruiz (pp. 220–233).

---

## 1. Sánchez-Atondo, García, Gutiérrez, Mungaray-Moctezuma, Montoya-Alcaraz, Calderón-Ramírez (2026), *TRIP* 36, 101859 (CC BY)

**Study area.** Mexicali, Baja California, Mexico; one city, estimated 885,354 inhabitants in 2024 (§3, p. 3).

**Starting object.** Bus services run by private companies under state-granted route concessions that fix alignment, vehicle type and expected frequency (§3.1, p. 4). The concessioned network is 41 routes, 12 companies, 936 km. Only 16 routes (457 km) were operating, and those 16 are the baseline network of the study (§3.1, p. 4; Table 1, p. 5). Phase 2 inputs are the as-operated alignments of existing routes (§4.2, p. 7). The method is therefore applied to the routes in operation, not to the concession register as such.

**Data used, by stage.**

| Stage | Data | Locator |
|---|---|---|
| Trunk definition (Module 1) | Road hierarchy from official urban plans; trip-attractor polygons from an official economic directory (DENUE); population and urban area thresholds (one trunk per 200,000 inhabitants; one per 40 km²) | §4.1, p. 7; Fig. 4, p. 8 |
| Consolidation (Module 2) | Route geometries only | §4.1, p. 7; Fig. 5, p. 9 |
| Headways (Module 3) | Frequencies of existing routes (sample peak-period frequencies) and a minimum service frequency | §4.1–4.2, p. 7; Fig. 6, p. 10 |
| Stops (Module 3) | Observed informal boarding and alighting points, transfer zones, stop-spacing criteria | §4.1–4.2, p. 7; Fig. 6, p. 10 |
| Fleet | Not computed | — |
| Evaluation (Phases 3–4) | Origin–destination survey (3,128 public-transport users), 100 zones, cross-classification production, DENUE-based attraction, gravity distribution calibrated in PTV Visum, headway-based assignment, 26,845 peak-period trips | §4.3, p. 7; Table 5, p. 12 |

**No demand data enters the design.** Table 2 (p. 6) lists the origin–destination survey as an input to Phase 3 only and marks Phases 3–4 as optional case validation. No AFC, APC, smart-card or mobile-phone data is used anywhere. The limitations paragraph nevertheless says the method requires route alignments, stop locations and "demand proxies" (§6, p. 15).

**Consolidation method.** Routes are grouped by alignment similarity, defined as overlap or parallel running within 200 m. In each group the trunk line is kept and the others discarded; if the group has no trunk, the route with the best connectivity (trunk links and major attractors) is kept (Fig. 5, p. 9). Then: sinuosity below 1.7 for feeders, maximum length 25 km with splitting into sections under 15 km, and a 500 m buffer coverage check that triggers new feeders (§4.1, p. 7; Fig. 5).
- **Inconsistency inside the paper:** the similarity threshold is 30 % in the text (§4.1, p. 7) and in Table 3 (p. 7), but more than 50 % in the Fig. 5 flowchart (p. 9). Table 4 (p. 11) reports overlap within 100 m, not 200 m. Cite the threshold with care.

**Demand proxy.** None in the sense of an index. Attractor polygons from the official activity directory and the road hierarchy steer trunk alignment; population and area set the minimum number of trunks.

**Headway setting.** For each proposed route, existing routes with at least 15 % layout coincidence are identified. A trunk takes the highest frequency among coinciding routes if that exceeds the minimum, otherwise the minimum (suggested 5 vehicles per hour, i.e. 12 min). A feeder takes the highest coinciding frequency if above the minimum, otherwise the weighted average of coinciding routes (Fig. 6, p. 10; §4.1, p. 7). Headways are called indicative and subject to operational refinement (§5.1, p. 10). **The per-route headway values are not published:** Table 4 gives only length, sinuosity and overlap.

**Fleet sizing.** None. Operational-cost estimation is listed as outside the method (§6, p. 15).

**Validation.** Like-for-like assignment of one calibrated demand matrix on the current and proposed networks. Reported changes: travel time −20 %, walking −6 %, waiting −34 %, transfers +513 % (§5.2, p. 11). Assignment parameters were varied for plausibility (§4.3, p. 7). The design thresholds were not tested; the authors list sensitivity to the overlap, sinuosity, length and buffer cut-offs as future work (§6, p. 15). No field or GPS validation.

**Implementable plan.** Partial. 23 routes (4 trunks, 19 feeders), 402 km, with a map and candidate stops (§5.1, p. 9; Fig. 7 and Table 4, p. 11). No published headway table, no fleet.

**Equity.** The Urban Marginalization Index (IMU) stratifies the evaluation only: 26 of 100 zones are lower quality-of-life, and their travel-time reduction is 22 % against 18 % for other users (§5.2, p. 14; Table 6). The authors state that the index is not an input to the method (§4.4, p. 9; Table 2 note, p. 6).

**Code and data.** No code. Data on request (p. 15).

**Element-by-element comparison with our pipeline.**

| Element | Sánchez-Atondo et al. | Ours | Assessment |
|---|---|---|---|
| Starting object | 16 operating routes out of 41 concessioned; city scale | 614 permits + 30 e-bus routes from the statutory register; division scale | Similar legal object (concession vs permit). They work from the operating subset, we from the full register. |
| Route geometry | As-operated alignments | OSRM routing of permit endpoints | Different. |
| Demand proxy | None; attractor polygons and road hierarchy | CDI (WorldPop + OSM POIs, walk-network catchments) | Different. |
| Consolidation | Similarity groups (overlap or within 200 m; 30 % or >50 %), keep trunk | Buffer share θ = 0.65, transitive clustering, 186 routes | **Close precedent.** Ours is a variant with a different threshold and explicit clustering. |
| Headways | Minimum frequency + inherited existing frequencies | Jenks tiers → policy bands 15/20/35, rural ≤50 | Both demand-free. Theirs inherits supply; ours is assigned by index tier. |
| Fleet | None | ⌈⌈cycle/headway⌉ × 1.15⌉ from routing-engine cycle times | Ours only. |
| Demand data | Origin–destination survey in evaluation | None at any stage | Ours is stricter. |
| Validation | Demand-model scenario comparison | Driver GPS, Monte Carlo/Sobol', tier stability | Different stance. |
| Open data | Official sources, field observation | Open data only (plus the register) | Different. |

---

## 2. Ruiz, Seguí-Pons, Mateu-Lladó (2017), *Journal of Transport Geography* 58, 220–233

**Study area.** Palma (Mallorca, Spain); 421,708 inhabitants, 88 districts (§2, p. 221).

**Starting object.** The 31 existing lines and 957 stops of the municipal operator EMT (§2, p. 221). Routes are left unchanged; the authors argue that changing routes or stops meets social resistance (§1, p. 221). Table 3 lists 28 lines.

**Data used.** Stop map, district map, line headways (§3.1.1, p. 222); district population and municipal socio-demographic variables (§3.1.2, p. 222); registered economic activities by district for a supplementary Gini (§4.3, p. 227).

**Does ridership enter the objective? No.** This resolves the ⚠ in §A row 2 and §B(d) item 2.
- The service level is computed only from stops, headways and district areas (§3.1.1, p. 222).
- The four optimisation objectives are the global Bus Service Level, the horizontal Gini, the vertical Gini, and service level jointly with horizontal Gini (§3.3, p. 225).
- The authors state that no stop-level load data was available, and use line-level occupancy and ridership only to comment on results (§4.5, p. 229; Fig. 10, p. 230, which plots normalised saturation, passengers and frequencies per line).
- They note that ridership and frequency are closely related and that this should be built into the model in future (§4.6, p. 232).

**Demand proxy.** A Public Transport Need Index per district: a weighted sum of four normalised variables with AHP weights from six experts (dependency rate 48.6, immigrant rate 27.7, female rate 16.3, economic activity 7.2, the last on an inverse scale) (§3.1.2, pp. 222–223). Catchments are 400 m Euclidean buffers around stops, overlaid on districts (§3.1.1, p. 222).

**Headway setting.** Optimisation by genetic algorithm with Monte Carlo evaluation (RISK Optimizer, 50,000 simulations per model). Constraints: at most ±5 min per line, and the sum of all headways fixed at the current 745 min (§3.3, p. 225). A 7 min floor applies in the simulation step (§3.2, p. 224).

**Fleet sizing.** None. Fleet neutrality is approximated by the constant-sum constraint on headways. No cycle times are used. The abstract's phrase about adapting the fleet's spatial distribution is not backed by a fleet calculation.

**Consolidation.** None.

**Sensitivity analysis.** Latin hypercube sampling, 100,000 simulations, each headway drawn from a triangular distribution of ±5 min, followed by regression of service level and Gini coefficients on line headways (§3.2, p. 224; Table 1, p. 229). Its purpose is to rank the influence of each line, not to test the stability of a plan.

**Validation.** None against observed outcomes. Results are modelled changes: joint optimisation gives +27 % service level, +3 % horizontal and +1 % vertical equity (§4.6, pp. 229–231). The authors say the results need further assessment of cost and acceptability before use (§4.6, p. 232).

**Implementable plan.** Partial: four alternative headway sets for existing lines (Table 3, p. 231). No routes, no fleet.

**Equity.** Central. Horizontal equity (service against population), vertical equity (service against need), Lorenz curves and Gini coefficients (§3.1.3–3.1.4, p. 223).

**Code and data.** None released. Tools are ArcGIS 10.2, Excel 2013 and @Risk 6.2 (§3, p. 222).

**Element-by-element comparison.**

| Element | Ruiz et al. | Ours | Assessment |
|---|---|---|---|
| Starting object | Existing municipal lines | Permit register | Different. |
| Demand proxy | AHP need index from census-type variables, by district | CDI from WorldPop + OSM POIs, by route | Same idea (composite ordinal index in place of ridership); different inputs and unit. |
| Catchment | 400 m Euclidean stop buffers | Walk-network catchments | Different. |
| Headways | Optimised within ±5 min of current values | Tier → policy band | Both demand-free. Theirs adjusts existing headways; ours assigns bands. |
| Fleet | Constant sum of headways | Derived from cycle times | Ours only. |
| Uncertainty | Latin hypercube on headways | Monte Carlo/Sobol' on plan outputs | Similar tool, different question. |
| Consolidation | None | Yes | Ours only. |

---

## 3. Barzegari, Taubkin, Barsukov, Nourinejad (2026), *Transportation Research Part A* 204, 104747 (CC BY)

**Study area.** Almaty, Kazakhstan; over two million residents, about 680 km²; one metro line, 8 trolleybus lines, 111 bus routes, 240 route variants (LADs); about 19,000 trips on a weekday and about 1,900 vehicles (§4.3, p. 15).

**Starting object.** The existing scheduled network. The unit of analysis is the Line-Alternative-Direction, i.e. a route variant with its own trajectory and schedule (§2.2, pp. 4–5). The Almaty section does not describe the operators or the licensing regime. The "multi-operator" label in §A row 3 rests on the abstract and introduction, not on the case study.

**Data used.** Trajectories, stops, service frequencies or headways, vehicle sizes, and in-vehicle times between stops. The authors note the tools are compatible with GTFS (§5, p. 18).

**Demand data: none.** Passenger-connection duplication is computed from supply only: connection time is half the headway plus in-vehicle time (§3.2, p. 9, eq. 8). The figure of 10 passengers per hour on p. 12 is a hypothetical in a worked example. The authors name ridership data as a future extension (§6, p. 19).

**Method.**
- Segment duplication: each variant on a segment is weighted by its trips per hour, or trips × vehicle length, relative to the strongest variant; the segment's duplication is the sum of weights (§3.1, p. 7, eqs. 3–5). Aggregation to routes or networks is by length, trips or size (eqs. 6a–c, pp. 7–8).
- Passenger-connection duplication: for each pair of stop sites, variants are weighted by presence, distance ratio or travel-time ratio (§3.2, p. 9, eqs. 7–10). Stops are grouped into sites, with thresholds of about 50–70 m or 200 m and more depending on purpose (§3.2, p. 8).
- **They argue that geometric overlap overstates duplication.** In their worked example a variant that is 100 % duplicated by trajectory is only about 4–7 % duplicated by passenger connections (§4.2, p. 14). Our buffer-share measure is a geometric measure of the kind they criticise.

**Consolidation.** Not performed. The paper is a diagnostic. It suggests truncating one variant (5A-1) to its exclusive section and identifies another (trolleybus 7-0-1) as replaceable (§4.3, pp. 15–17; §5, p. 17). No consolidated network is produced.

**Frequency and fleet.** Not set or sized. Frequencies are inputs.

**Validation.** None. Numerical examples and an illustrative case.

**Implementable plan.** No.

**Equity.** None.

**Code and data.** A purpose-built toolkit is described but not released (§4.3, p. 15). Data on request (p. 19).

**Element-by-element comparison.**

| Element | Barzegari et al. | Ours | Assessment |
|---|---|---|---|
| Overlap measure | Frequency- and size-weighted, per segment and per stop-pair | Geometric buffer share, θ = 0.65 | Theirs is more refined and needs schedules. Ours is simpler and needs only geometry. |
| Action | Diagnosis and recommendations | Transitive clustering to 186 routes | Ours produces a network. |
| Demand data | None | None | Same. |
| Other elements | None | Proxy, tiers, fleet, validation | Ours only. |

---

## 4. Dumedah, Abass, Gyasi, Forkuor, Novignon (2023), *Journal of Transport Geography* 111, 103643

**Study area.** Oforikrom Municipality, Greater Kumasi, Ghana; about 50 km², 212,826 inhabitants (§2.1, p. 2).

**Starting object.** Informal paratransit (trotro minibuses and taxis) whose routes and terminals are decided by driver unions and operators, with little local-government control (§2.1.1, pp. 3–4). There is no licence or permit register; the authors recommend that authorities establish and license routes (§4.1, p. 11). 43 routes were mapped, 15 of them wholly inside the municipality (§3.1, p. 4; Table 1, p. 5).

**Data used.**
- Terminals and stops surveyed in the field with handheld GPS; routes identified by consulting station managers, operators, passengers and residents (§2.2, p. 4). This is the "GTFS-like" data of the abstract. No GTFS exists for Kumasi (§2.1, p. 3).
- Road network from OSM, processed with OSMnx (§2.2, p. 4).
- Population at about 100 m resolution for 2020 from the Humanitarian Data Exchange (§2.2, p. 4). The text does not name the product.
- Relative Wealth Index at 2.4 km resolution (§2.2, p. 4).

**Demand data: none.** Population density is described as a proxy for paratransit demand (§2.2, p. 4). Frequencies, fares, costs and fleet characteristics are listed as data to add in future (§4.1, p. 10).

**Method.** Nearest-neighbour analysis of terminals; service-area estimation of travel distance to routes on the road network, explicitly preferred to Euclidean distance (§2.3, p. 4); comparison of population served, land area covered and wealth index by distance band (§3.3, p. 9).

**Consolidation.** By judgement, not by algorithm. Seven fragmented routes south of the N6 highway could be reduced to two, and a "sample" zoning of the municipality into seven service zones reduces the 15 internal routes to 7, i.e. 53 % (§3.2, p. 7; Fig. 4). No overlap threshold or metric is defined. The 53 % figure applies to the 15 internal routes, not to all 43.

**Frequency and fleet.** None.

**Validation.** None. The authors acknowledge that the findings rest only on the configuration of terminals and routes (§4.1, p. 10).

**Implementable plan.** No. The zoning is illustrative.

**Equity.** Access is compared with the wealth index. The relation is weak (R² 0.208 with land area, 0.253 with population served) and the authors note the coarse resolution of the index (§3.3, p. 9). Access findings: 27 % of population within 200 m of a route, about 50 % within 400 m, 86 % within 1,000 m.

**Code and data.** No code. Data on request (p. 11).

**Element-by-element comparison.**

| Element | Dumedah et al. | Ours | Assessment |
|---|---|---|---|
| Starting object | Field-mapped informal routes, no register | Statutory permit register | Different. |
| Scale | 43 routes, 50 km² | 644 register entries, a division | Different. |
| Population proxy | 100 m gridded population | WorldPop + OSM POIs as CDI | Similar ingredient; theirs is descriptive. |
| Catchment | Road-network service areas | Walk-network catchments | **Same choice.** They do not measure the Euclidean overstatement. |
| Consolidation | Illustrative, by judgement | Thresholded, clustered | Ours is reproducible. |
| Headway, fleet, validation | None | Yes | Ours only. |

---

## 5. Mittal & Ukkusuri (2025), *Data Science for Transportation* 7:4

**Study area.** Greater Maputo, Mozambique; 2.86 million inhabitants; formal buses and informal minibuses (p. 6).

**Starting object.** None. Routes are designed from scratch on the road network. The research question is how to plan when public-transport information is unavailable (p. 2). An operational GTFS feed collected in the field by WhereIsMyTransport is used for comparison (Table 1, p. 5). Two exceptions to "from scratch": OSM bus-stop locations label segments as transit-viable and are added to the stop set (pp. 7, 10), and the distribution of stops per route is taken from GTFS where available (p. 11).

**Data used, by stage.**

| Stage | Data | Locator |
|---|---|---|
| Road-segment viability | WorldPop population density, OSM POI density, Relative Wealth Index, road density, road type, and four groups of mobile-phone ping and transit-waypoint densities, all within a 500 m buffer of each segment | Table 2, p. 8 |
| Stops | Mobile-phone pings within 100 m of viable segments, clustered by DBSCAN (200 m); top 10 % of clusters by footfall, plus OSM stops | p. 10 |
| Routes | Travel demand between stop pairs from mobile-phone traces, stop footfall, minimum spanning tree; hill climbing over 100,000 iterations; weights 0.4 use, 0.2 coverage, 0.2 directness, 0.2 feasibility | p. 11 |
| Headways | Usage quantiles from trip flows | p. 13 |
| Fleet | Not considered | p. 18 |
| Validation | Operational GTFS | pp. 13–17 |

**Demand data enters every design stage.** The mobile-phone data comes from a vendor under a non-disclosure agreement: July and November 2019, 6,578 users (0.23 %), 4.5 pings per user per day (Table 1, p. 5; data availability, p. 19). No AFC, APC or survey.

**Demand proxy.** WorldPop and OSM POI density are two of nine attribute groups in a semi-supervised classifier (logistic regression to seed negative labels, then self-training with a random forest, 100 runs) that labels each of 2,379 road segments as viable or not (pp. 7–9). The buffers are Euclidean. The open-data variables are not combined into an index and are not used alone.

**Headway setting.** The one verbatim quote in this document: headways are "assumed as inversely proportional to route usage quantiles from trip flows" (Mittal & Ukkusuri 2025, p. 13), from 2 min for the top 10 % to 60 min for the bottom 10 %. The paper presents this as an assumption needed to build the GTFS feed, together with a 20 km/h bus speed, not as a contribution.

**Fleet sizing.** None. Fleet scheduling, fleet size and budget are named as omissions (p. 18).

**Consolidation.** Not of routes. The stop step identifies redundancy: 26 % of extracted stops (147) cover 50 % of operational stops (980) (p. 15).

**Validation.** Against the operational GTFS: 71 % segment agreement and an alignment score of 0.780 (p. 13); stop alignment 85.48 % and stop-density correlation 0.79 (p. 15); route alignment 87.19 % overall, 89.71 % informal, 74.79 % formal (p. 15); directness slope 1.034 against 1.155 (p. 15); accessibility 17 % higher, r = 0.882 (p. 17). A sensitivity analysis varies the four objective weights (p. 16).

**Implementable plan.** Partial. A GTFS feed for the evening peak with stops, routes, shapes and assumed headways (p. 13). No fleet, no costs. The number of routes is not stated in the text.

**Equity.** Population within 500 m of routes for all, the poorest 10 % and the richest 10 %. The extracted routes cover the poorest less well (below 60 % against about 60 %) and the richest better (nearly 80 % against about 70 %); the authors flag this as an equity concern (p. 15). Accessibility bias is tested against poverty and data representativeness (p. 17).

**Code and data.** Processed data and code from the corresponding author on reasonable request; phone data cannot be shared (p. 19). Not released.

**Element-by-element comparison.**

| Element | Mittal & Ukkusuri | Ours | Assessment |
|---|---|---|---|
| Starting object | Road network, no legacy routes | Permit register | Opposite. |
| Open inputs | WorldPop density + OSM POI density per segment, 500 m Euclidean buffer | WorldPop pop/km + OSM POIs/km per route, walk-network catchment | **Same two ingredients.** |
| Use of open inputs | Classifier features alongside phone data | Standalone ordinal index | Different. |
| Demand data | Proprietary phone traces at every stage | None | Different. |
| Headways | Usage quantiles → 2–60 min | Jenks tiers → 15/20/35 (≤50 rural) policy bands | **Same structure (ordinal tier → headway).** Their tiers come from phone trip flows and the values are assumed; ours come from an open index and are policy-anchored. |
| Fleet | None | Derived | Ours only. |
| Validation | Against existing GTFS; weight sensitivity | Supply-side GPS; Monte Carlo/Sobol'; tier stability | Different. |

---

## 6. Corrections needed in `03_novelty_check.md` §A

| Row | Statement in §A | What the full text says |
|---|---|---|
| 1 | "Unknown until read: how frequencies are set" | Resolved. Minimum frequency (5 vehicles/hour) plus frequencies inherited from existing overlapping routes. No demand data. e4 should be 2, not 1; total 10. |
| 1 | "~75–80 % of route-km overlapping" | About 80 % of route-km overlap on radial corridors (p. 4; Table 1); the average overlap factor of the current network is 75 % (p. 9). Both figures are in the paper. |
| 1 | "(b) evaluation uses a transport model" | Correct, and the model uses an origin–destination survey. Add: the design modules use no demand data, and the evaluation is declared optional. |
| 2 | "district socio-demographic need (neighbourhoods, census sections, 400 m mesh)" | The paper uses 88 districts and 400 m stop buffers. I found no census sections and no 400 m mesh in the full text. |
| 2 | "the fleet is redistributed" | No fleet is computed. The sum of headways is held at 745 min. |
| 2 | First author "Ruiz-Pérez" | The paper prints "Maurici Ruiz". Cite as Ruiz, Seguí-Pons and Mateu-Lladó (2017), as the addendum already says. |
| 3 | "multi-operator network (Almaty)" | The case study does not describe operators. Volume is 204 (2026). The paper measures duplication; it does not consolidate. |
| 4 | "existing routes can be reduced … by 53 %" | Applies to the 15 routes inside the municipality (15 → 7), by an illustrative zoning. The "GTFS-like" data is a field GPS survey. |
| 5 | e4 = 0 | Headways are assigned by usage quantile; e4 should be 1. Total 4. |
| 5 | "via semi-supervised learning, clustering and multi-objective metaheuristics" | Correct. Add: phone data enters viability, stops, routes and headways. |

---

## 7. Revised verdict

### 7.1 SAFE claims in §B(a)

| # | Claim | Status after full-text reading |
|---|---|---|
| 1 | Object: a statutory Indian stage-carriage permit register | **Stands.** The Mexicali concession is the closest legal analogue, but that study works from the 16 operating routes and stays at city scale. Dumedah has no register. Mittal & Ukkusuri have no legacy object. |
| 2 | Integration: the full chain | **Stands.** No paper sizes a fleet. No paper builds an open ordinal index. Only Sánchez-Atondo combines consolidation and headways, and it stops there. |
| 3 | Validation stance: "decision-robust, not demand-validated" | **Stands, with a caveat.** No paper states this stance. Sánchez-Atondo validate with a demand model; Mittal & Ukkusuri against existing GTFS; Ruiz, Barzegari and Dumedah do not validate. Monte Carlo sensitivity as a tool is not new: Ruiz use Latin hypercube sampling on headways, and Mittal & Ukkusuri run a weight-sensitivity analysis they describe as a robustness test. Claim the stance and its application to a rationalisation plan, not the technique. |
| 4 | Setting: Kashmir Division | **Stands.** None of the five concerns India. |
| 5 | Catchment finding as an application of an established critique | **Stands.** Dumedah already use road-network service areas with a 100 m population grid on an informal network, without measuring the Euclidean overstatement. Ruiz (400 m), Sánchez-Atondo (500 m) and Mittal & Ukkusuri (500 m) use Euclidean buffers. |

### 7.2 Additions to the UNSAFE table in §B(b)

| Unsafe phrasing | Contradicted by |
|---|---|
| "No prior method restructures a concession network without demand data" | Sánchez-Atondo et al. 2026: Modules 1–3 use no demand data (Table 2, p. 6). |
| "Threshold-based overlap grouping with trunk retention is our method" | Sánchez-Atondo et al. 2026, Fig. 5 (p. 9). Present ours as a variant. |
| "Assigning headways by ordinal tier is new" | Mittal & Ukkusuri 2025 (usage quantiles, p. 13); Sánchez-Atondo et al. 2026 (minimum frequency plus inherited frequencies, Fig. 6). Ruiz 2017 remains the need-index precedent. |
| "Combining WorldPop population and OSM POI density for bus planning is new" | Mittal & Ukkusuri 2025, Table 2 (p. 8). Already listed in §B(b); now confirmed at the level of the exact variables. |
| "Geometric overlap is an adequate duplication measure" (if stated without qualification) | Barzegari et al. 2026 argue it overstates duplication (p. 14). Acknowledge this and justify the geometric measure by the absence of reliable frequencies in the permit register. |

### 7.3 Final wording for §B(c)

**Sentence 1 — reword.** The existing version understates Sánchez-Atondo et al. and should add mobile-phone data to the list of excluded sources.

> "Rule-based methods for restructuring fragmented, concession-based bus networks now exist. Sánchez-Atondo et al. (2026) group routes whose alignments overlap, retain a trunk in each group and set headways from a minimum service frequency and the frequencies of existing routes, without demand data in the design step; they work from the routes in operation, do not size a fleet, and evaluate the result with an origin–destination survey and an assignment model. Low-data GIS diagnosis of informal networks (Dumedah et al., 2023), population-raster and OpenStreetMap inputs to route design (Mittal and Ukkusuri, 2025, who combine them with mobile-phone traces) and duplication measures (Barzegari et al., 2026) are also established. To our knowledge, however, no study has taken a statutory stage-carriage permit register as its starting object and carried it through to a tiered, fleet-sized network using only open data, with no origin–destination, ticketing, passenger-count or mobile-phone data at any stage, including evaluation."

**Sentence 2 — reword.** The existing version implies that demand-free headways are our step. They are not.

> "Our contribution is an integration and a decision logic rather than a new technique. Headways have been set from need indices (Ruiz et al., 2017), from inherited frequencies with a service floor (Sánchez-Atondo et al., 2026) and from usage quantiles (Mittal and Ukkusuri, 2025); none of these studies derives a fleet. We assign policy headway bands by ordinal tier of an open-data index, so that fleet size and coverage follow from supply-side quantities alone (routing-engine cycle times and walk-network catchments). The plan can therefore be tested for decision robustness (GPS-checked cycle times, Monte Carlo/Sobol' variance, tier stability) even though it cannot be demand-validated. We are not aware of a rationalisation study that states this stance explicitly and tests it."

**Sentence 3 — keep.** Optional addition after the first sentence: "Network-based catchments have also been applied to an informal network (Dumedah et al., 2023)."

**Section 3 or limitations — add one sentence on the overlap measure:**

> "Barzegari et al. (2026) show that geometric overlap overstates duplication relative to frequency-weighted and passenger-connection measures. We use a geometric buffer share because the permit register carries no reliable service frequencies, and we treat the resulting clusters as candidates for consolidation."

This last sentence assumes the register has no reliable frequencies. I did not check that against the manuscript; the authors must confirm it.

### 7.4 §B(d)

Remove both ⚠ flags. Items 1 and 2 are now read in full.

---

## 8. Table-1-ready coding

Data intensity scale as specified: 1 open data only; 2 + official static data, census or schedules; 3 + partial observations (sample counts, surveys, operator GPS/AVL); 4 + full origin–destination matrix from survey or calibrated model; 5 + passive ridership (AFC, APC, smart card). Coded at the highest level the study uses.

| Paper | Geography | Planning stage | Method family | Demand input | Data intensity | Equity treatment | Validation | Implementable plan | Code released |
|---|---|---|---|---|---|---|---|---|---|
| Sánchez-Atondo et al. 2026 | Mexicali, Mexico (city) | Network restructuring: consolidation, trunk–feeder layout, headways, stops | Rule-based GIS heuristics; four-step model for evaluation | None in design (road hierarchy, official activity directory, existing frequencies); survey-based OD matrix in evaluation | **4** (design modules alone: 3) | Deprivation index, evaluation stratification only | Demand-model scenario comparison; assignment-parameter plausibility tests | Partial (23 routes, stops; headways indicative and unpublished; no fleet) | No (data on request) |
| Ruiz et al. 2017 | Palma, Spain (city) | Frequency setting on existing lines | Simulation (Latin hypercube) + genetic-algorithm optimisation in a spreadsheet | None in objective; AHP need index from socio-demographic variables; line ridership shown descriptively | **2** | Core objective: horizontal and vertical equity, Lorenz/Gini | None against observations; modelled service and Gini changes | Partial (headway sets; no routes, no fleet) | No |
| Barzegari et al. 2026 | Almaty, Kazakhstan (city) | Network diagnosis (duplication) | Analytical indicators on schedule data | None | **2** | None | None; numerical examples and illustrative case | No | No (data on request) |
| Dumedah et al. 2023 | Oforikrom, Kumasi, Ghana (municipality) | Network diagnosis (coverage, fragmentation) | GIS: nearest neighbour, network service areas | None; gridded population as proxy | **3** (field GPS survey of terminals, stops, routes) | Wealth index compared with access; weak relation | None | No (illustrative zoning, 15 → 7 routes) | No (data on request) |
| Mittal & Ukkusuri 2025 | Greater Maputo, Mozambique (metropolitan) | Network design from scratch: corridors, stops, routes, assumed headways | Semi-supervised learning, DBSCAN, hill-climbing metaheuristic | Proprietary mobile-phone traces (trip flows, footfall) at every stage; WorldPop and OSM POIs as features | **4** (see note) | Coverage of poorest and richest deciles; bias tests | Against field-collected operational GTFS; weight sensitivity | Partial (GTFS feed with assumed headways; no fleet) | No (on request) |

**Note on Mittal & Ukkusuri.** The scale has no level for mobile-phone data. I coded 4 because the traces yield stop-pair demand, which is equivalent to an origin–destination matrix, and they are not transit ridership. If the authors treat any proprietary passive data as level 5, change this to 5 and say so in the Table 1 note.

**Note on Sánchez-Atondo et al.** If Table 1 codes only what the transferable method requires, use 3 and footnote that the published evaluation used an origin–destination survey.
