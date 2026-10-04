# Full-text recoding of 23 studies: changes against `table1_coded_draft.csv`

Fields compared: geography, region_class, planning_stage, method_family, demand_input, data_intensity, equity, validation, implementable_plan, code_released. `basis` and `note` were rewritten for every row and are not counted as changes.

Every evidence locator refers to the extracted text in `pdfs/C##_*.txt` (C59: page images of the scanned PDF, pp. 336-343).

**Total fields changed: 80 across 22 studies** (1 studies with no change).

| cid | fields changed |
|---|---|
| C02 | 5 |
| C03 | 2 |
| C04 | 1 |
| C06 | 6 |
| C07 | 7 |
| C11 | 2 |
| C14 | 2 |
| C16 | 3 |
| C18 | 5 |
| C19 | 5 |
| C21 | 3 |
| C28 | 0 |
| C29 | 4 |
| C33 | 3 |
| C34 | 3 |
| C35 | 3 |
| C37 | 5 |
| C40 | 2 |
| C42 | 1 |
| C43 | 3 |
| C47 | 4 |
| C48 | 3 |
| C59 | 8 |

## Judgement calls the lead author should check

- **demand_input left `unclear` (C02, C03, C04, C28, C48).** Each paper takes a full OD matrix as input but does not say whether it comes from a survey or a model (wording quoted in the notes). `data_intensity` is 4 in every case regardless.
- **implementable_plan = Yes for C03, C06, C48** rests on the method producing specific routes and frequencies/fleet for a real city. None of the three prints a route-by-route list; they report aggregate tables (and a map for C48). If Yes requires a published route table, these become Partial. C02 and C04 print full route/headway tables.
- **C07 Rivera** is treated as a literature benchmark instance (reproduced from Mauttone & Urquhart 2009), hence region benchmark/synthetic and plan No. If treated as a real-city application it would be Global South (non-India).
- **C34 data_intensity 3** assumes the zone work-trip counts in the job proxy come from the 2009 mobility survey; the paper names the survey zones but not the source of the counts.
- **C35 data_intensity 2 → 3** because the gravity impedance is estimated from an on-board survey, although the paper presents the method as using public data.
- **C33 data_intensity stays 3**: the survey OD matrix enters only as zonal production/attraction totals, not as flows.
- **C47 planning_stage** kept as frequency/headway; fleet is derived from the optimised frequencies on existing routes.
- **C21 implementable_plan** kept as Partial; the site is real but the street layout and land use are stylised and the output is a service ratio, so No is also arguable.
- **C59**: the `.txt` extraction covers only pp. 333-336 (the scanned pages have no text layer). Pages 336, 337, 339, 340 and 343 were read as page images; pp. 338, 341, 342 were not read.

## C02 — Wai Yuen Szeto et al. (2014)

Draft basis: abstract → fulltext. Fields changed: 5.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | unclear | Tin Shui Wai, Hong Kong (plus small synthetic network and Winnipeg test network) | §4 intro and §4.2: small created network, Tin Shui Wai (23 zones), Winnipeg network from Emme |
| region_class | unclear | Global North | §4.2: real case is Tin Shui Wai, Hong Kong (Hong Kong classed Global North as for C04) |
| validation | unclear | multiple (benchmark-instance comparison; comparison with existing network/GTFS; sensitivity/uncertainty analysis) | §4.1 brute-force optimum on small network; §4.2 'Robustness' Table 4 (1,000 perturbed matrices) and Tables 5-6 vs existing design; §4.3 GA comparison on Winnipeg (Table 7) |
| implementable_plan | unclear | Yes | §4.2 Table 6: 10 routes with stop sequence, number of buses, headway for Tin Shui Wai |
| code_released | unclear | no | §4: coded in C++ with CPLEX 12.4; no availability statement anywhere in text |

Still `unclear`: demand_input — §4.2: TSW matrix 'estimated from the available data' (App. II), source unstated; Table 6 lists 10 routes with buses and headways; 1,000 perturbed matrices.

## C03 — Ernesto Cipriani et al. (2010)

Draft basis: abstract → fulltext. Fields changed: 2.

| Field | Old | New | Evidence |
|---|---|---|---|
| validation | unclear | multiple (comparison with existing network/GTFS; sensitivity/uncertainty analysis) | §5 Tables 3-4: existing 214-line network vs 85- and 130-line designs; §5: weights calibrated by sensitivity analysis, number of lines varied 40-160 (Tables 1-2) |
| code_released | unclear | no | §4: PGA implemented in C# with EMME; no availability statement |

Still `unclear`: demand_input — §3, §5: transit demand matrix (c. 230,000 peak-hour trips) is an input, source unstated; 85-line design with frequencies vs existing network (Tables 3-4); route list not printed.

## C04 — Wai Yuen Szeto et al. (2010)

Draft basis: abstract → fulltext. Fields changed: 1.

| Field | Old | New | Evidence |
|---|---|---|---|
| code_released | unclear | no | §4: coded in Visual C++ 2003; no availability statement |

Still `unclear`: demand_input — §2: demand matrix 'estimated from the available data' (Appendix I), source unstated; Table 4 lists 10 routes with buses and headways; §4.6 perturbed matrices.

## C06 — Fang Zhao et al. (2007)

Draft basis: abstract → fulltext. Fields changed: 6.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | benchmark network (literature instances) + large-scale realistic network (unnamed in abstract) | Miami-Dade County, Florida, USA; benchmark network (Mandl) | §7: first experiment Mandl's Swiss network; second experiment Miami-Dade Transit service area |
| region_class | unclear | Global North | §7: real application is Miami-Dade, USA |
| demand_input | synthetic or benchmark OD | modelled OD (4-step/calibrated model) | §7: 'OD matrix was generated from the 1999 validated Miami-Dade travel demand model' (161,944 daily transit trips) |
| validation | benchmark-instance comparison | multiple (benchmark-instance comparison; comparison with existing network/GTFS) | §7 Table 1 (Mandl, vs Mandl / Baaj & Mahmassani / Shih & Mahmassani) and Table 2 (vs existing MDT network) |
| implementable_plan | unclear | Yes | §7 Table 2: route network and headways optimised for MDT with 600 vehicles; NB route-level list not printed, only aggregate statistics |
| code_released | unclear | no | No availability statement in text |

## C07 — Mahmoud Owais et al. (2018)

Draft basis: abstract → fulltext. Fields changed: 7.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | unclear (two real-size networks, unnamed in abstract) | benchmark networks (Rivera, Uruguay instance from Mauttone & Urquhart 2009; Mandl) | §5.1 Rivera city network (Fig. 8 'reproduced from Mauttone & Urquhart, 2009'); §5.2 Mandl's Swiss network |
| region_class | unclear | benchmark/synthetic | §5.1-5.2: both are published literature instances with given OD matrices |
| demand_input | unclear | synthetic or benchmark OD | §3.1: fixed transit demand set d_ij is input; §5.1: 378 O/D pairs of published Rivera instance; §5.2: Mandl 15,570 trips |
| data_intensity | unclear | 4 | §6: 'With only the Origin-Destination matrix and the network structure, it designs its routes' -> OD matrix required (level 4) |
| validation | unclear | benchmark-instance comparison | §5.2 Table 3: comparison with seven published Mandl solutions |
| implementable_plan | unclear | No | §5.1 Table 2: 21 non-dominated networks reported by aggregate indicators only, on a literature instance; no plan selected |
| code_released | unclear | no | §5: written in C#; no availability statement |

## C11 — James J. Barry et al. (2009)

Draft basis: abstract → fulltext. Fields changed: 2.

| Field | Old | New | Evidence |
|---|---|---|---|
| validation | unclear | back-cast vs observed counts/ridership | Section 'Validation' (pp. 9-10): comparison with subway register entry/exit counts, bus ride-check boardings/alightings, and ten predetermined MetroCard tours |
| code_released | unclear | no | Section 'Query software': custom TransCAD application for NYCT; no release statement |

## C14 — Chao Chen et al. (2014)

Draft basis: abstract+web → fulltext. Fields changed: 2.

| Field | Old | New | Evidence |
|---|---|---|---|
| validation | unclear | multiple (comparison with existing network/GTFS; sensitivity/uncertainty analysis) | §V.D 'Comparison with Real Routes' (Fig. 15, Table III); §V parameter studies of merge/split thresholds T1/T2 and of k (e.g. Fig. 13) |
| code_released | unclear | no | No availability statement in text |

## C16 — Wenzhe Sun et al. (2021)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | unclear (three lines of one bus system; city not in abstract) | Shizuoka City, Japan (three bus routes) | §1 and §5: 'three main bus routes in Shizuoka City, Japan'; data from Shizutetsu Group (Acknowledgements) |
| region_class | unclear | Global North | §5: Japan |
| code_released | unclear | no | No availability statement in text |

## C18 — Calvin P. Tribby et al. (2012)

Draft basis: abstract → fulltext. Fields changed: 5.

| Field | Old | New | Evidence |
|---|---|---|---|
| demand_input | none | proxy (population/POI/land use/need index) | Methods: address points weighted by residential units from land-use layer; transit users' index from 2000 Census block-group variables |
| data_intensity | unclear | 2 | Methods (pp. 347 ff.): city's published bus schedules, street network, address points, land-use layer, 2000 Census -> official static data (level 2) |
| equity | none | distributional metric (Gini/Lorenz/group comparison) | Methods and Results (Fig. 7): travel-time savings compared with transit-need index by block group, 'distributive equity framework' |
| validation | unclear | none | Discussion (limitations paragraph): model uses average scheduled times, 'as opposed to actual travel times'; no comparison with observations |
| code_released | unclear | no | No availability statement in text |

## C19 — Eric M. Delmelle et al. (2012)

Draft basis: abstract → fulltext. Fields changed: 5.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | unclear (one inbound urban bus route; city not in abstract) | Charlotte, North Carolina, USA (CATS route 9) | §4-5: route 9, Charlotte Area Transit System, Mecklenburg County, North Carolina |
| region_class | unclear | Global North | §5: USA |
| data_intensity | unclear | 2 | §5: 2008 parcel data (land use, square footage) for Mecklenburg County, CATS stop/route data, 2008 aerial photos -> official static data (level 2) |
| validation | unclear | multiple (field/expert; sensitivity/uncertainty analysis) | §4 'System evaluation': two meetings with three CATS transit planners; §5: number of stops p and impedance β (2 -> 5) varied, MCLP comparison (Figs. 7-8) |
| code_released | unclear | no | §3-4: GIS interface described; no availability statement |

## C21 — Hema Rayaprolu et al. (2022)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| data_intensity | unclear | 2 | 'Street network and land use assignment': future population and employment projections per precinct (Levinson et al. 2020), authors' own street layout and GTFS, OpenTripPlanner -> official static projections (level 2) |
| validation | unclear | none | Conclusion: 'Future studies could test the sensitivity and robustness'; no comparison with observations or existing network |
| code_released | unclear | no | Python GTFS generator mentioned; no availability statement |

## C28 — Jose Morales et al. (2017)

Draft basis: fulltext → fulltext. Fields changed: 0.

No coded field changed; draft values confirmed against the full text.

Still `unclear`: demand_input — pp. 213-214: GC 2005 OD matrices (173 TAZ) 'were available', provenance unstated; used to fit decay parameters and as job proxy; expert workshop.

## C29 — Emily Eros et al. (2014)

Draft basis: abstract → fulltext. Fields changed: 4.

| Field | Old | New | Evidence |
|---|---|---|---|
| method_family | unclear | data-mining (AFC/GPS/phone) | 'Project Overview and Outputs': GPS field tracking with TransitWand app plus conversion of agency files; coded as C30 (same type of project) |
| data_intensity | unclear | 3 | 'Project Overview and Outputs': agency schedule/KML files plus field GPS collection for nearly 1,100 ramales -> partial observations (level 3), as C30/C31 |
| validation | unclear | field/expert | 'Project Overview and Outputs': second series of agency meetings; Google Transit engineers 'review and clear the data feed' |
| code_released | unclear | no | GTFS feed released as open data; no code availability statement |

## C33 — Hasan Shahab et al. (2026)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| method_family | GIS/accessibility analysis | mixed | §3 and §3.3.3-3.3.4: weighted linear combination demand surface (GIS) plus MCLP / p-median location-allocation optimisation |
| validation | unclear | multiple (field/expert; sensitivity/uncertainty analysis) | §3.3.2: candidate stops field-checked; §3.3.1: sensitivity tests of WLC weights (Appendix Table S5) |
| code_released | unclear | no | Supplementary data only; no code availability statement |

## C34 — Diego Hernández (2017)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| data_intensity | unclear | 3 | §3: zones of the 2009 Montevideo mobility survey; job proxy uses 'number of work trips in each zone'; school enrolment; 'Como ir' trip planner -> survey-based partial observations (level 3). NB the paper does not name the source of the work-trip counts |
| validation | unclear | none | §3-4: no validation or sensitivity test reported |
| code_released | unclear | no | No availability statement in text |

## C35 — Alex A. Karner (2018)

Draft basis: abstract+web → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| data_intensity | 2 | 3 | Methods p. 8: 'impedance term was derived using ridership information from the 2010-2011 Valley Metro on-board survey' (geocoded boardings/alightings) -> on-board survey (level 3) |
| validation | unclear | none | Results: comparison with ridership-share route classification (Fig. 5) is a method contrast, not a validation; no sensitivity analysis |
| code_released | unclear | no | No availability statement in text |

## C37 — Ferguson E.M. et al. (2012)

Draft basis: abstract → fulltext. Fields changed: 5.

| Field | Old | New | Evidence |
|---|---|---|---|
| method_family | unclear | (meta)heuristic | §3 'solution method': genetic algorithm |
| data_intensity | unclear | 2 | §4.1 Table 1: 2000 US Census, 2005 local MPO employment data, transit agency trip planner, Google Maps, FTA cost report -> official static data (level 2) |
| validation | sensitivity/uncertainty analysis | multiple (comparison with existing network/GTFS; sensitivity/uncertainty analysis) | §4.3: sensitivity analysis of a, b, budgets and uncertainty (Fig. 2); Table 2 compares existing service with model results |
| implementable_plan | unclear | Partial | §4.2-4.3: frequencies for 26 existing and three new routes among 15 origin and 10 destination tracts of an unnamed real city; frequencies only |
| code_released | unclear | no | No availability statement in text |

## C40 — Haijing Liu et al. (2022)

Draft basis: abstract → fulltext. Fields changed: 2.

| Field | Old | New | Evidence |
|---|---|---|---|
| data_intensity | unclear | 2 | §5 'Data and method': GTFS from GRTC, OSM, ACS 2014-2018, LEHD LODES 2017, SafeGraph POI -> official static data (level 2) |
| code_released | unclear | no | No availability statement in text |

## C42 — Giacomo Falchetta et al. (2021)

Draft basis: abstract+web → fulltext. Fields changed: 1.

| Field | Old | New | Evidence |
|---|---|---|---|
| validation | unclear | field/expert | §3.5: data could not be validated in the field; 'we have engaged with expert elicitation' from local researchers and practitioners |

## C43 — Bhargav Adhvaryu et al. (2019)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| data_intensity | unclear | 3 | §4.3: operator route/stop data plus primary surveys (Aug-Sep 2016) for City Bus delay, average peak frequency and willingness to walk -> partial observations (level 3) |
| validation | unclear | none | §4.3-4.6: only grid-size comparison (Fig. 2) and Ahmedabad comparison; no validation against observations |
| code_released | unclear | no | No availability statement in text |

## C47 — Ravi Kiran Sastry Gadepalli et al. (2024)

Draft basis: abstract → fulltext. Fields changed: 4.

| Field | Old | New | Evidence |
|---|---|---|---|
| method_family | unclear | exact optimisation | §4.3: 'IBM ILOG CPLEX 12.7.1 ... integer programming'; globally optimal solution |
| demand_input | unclear | modelled OD (4-step/calibrated model) | §4.1-4.2: four-step travel demand model in TransCAD calibrated from 3,058-household travel-diary survey, cordon OD surveys and counts; peak-hour OD matrix assigned |
| implementable_plan | unclear | Partial | §4.3-4.4: route-specific frequencies and fleet for existing 83 bus and 18 paratransit routes; routes not redesigned; values summarised in categories (Table 5) |
| code_released | unclear | no | 'Data availability': data confidential; no code statement |

## C48 — Verma A. et al. (2017)

Draft basis: abstract → fulltext. Fields changed: 3.

| Field | Old | New | Evidence |
|---|---|---|---|
| method_family | unclear | (meta)heuristic | §3.2-3.4: genetic algorithm for hub location-allocation, inter-hub and feeder routes (DEA only screens potential hubs) |
| data_intensity | unclear | 4 | §4: 'Demand matrix for each of these TAZs is obtained from secondary sources' (172 zones) -> full OD matrix required (level 4) |
| code_released | unclear | no | No availability statement in text |

Still `unclear`: demand_input — §4: 172-TAZ demand matrix 'obtained from secondary sources', type unstated; GA yields 344 routes with frequencies and 4,436 buses vs BMTC's 908 routes (Table 7).

## C59 — Ceder et al. (1986)

Draft basis: abstract+web → fulltext. Fields changed: 8.

| Field | Old | New | Evidence |
|---|---|---|---|
| geography | unclear | synthetic (5-node example network) | p. 339 'Example and discussion', Fig. 3: 'simple five-node network' |
| region_class | unclear | benchmark/synthetic | p. 339: illustrative example only, no real city |
| method_family | unclear | (meta)heuristic | p. 339: eight-step route construction algorithm (constructive enumeration of feasible routes under travel-time constraint) |
| demand_input | unclear | synthetic or benchmark OD | p. 336 notation: demand matrix D(i,j) is input; p. 340 Table 2 demand matrix of the example |
| data_intensity | unclear | 4 | p. 336 and Table 2: OD demand matrix required (level 4); p. 334 notes need for 'a reasonably accurate public transport matrix' |
| validation | unclear | none | pp. 339-343: worked example and appendix only; no comparison or test |
| implementable_plan | unclear | No | p. 339: five-node illustrative network |
| code_released | unclear | no | 1986 paper; no code statement |
