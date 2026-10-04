# Quantitative Claim Ledger: Kashmir Transit Rationalisation Study

**Repository Root**: `E:\kash-paper`  
**Manuscript Title**: *Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*  
**Target Journal**: *Transport Policy*  
**Version**: 1.0.0 (Authoritative Single Source of Truth for Quantitative Results)  
**Authoritative Operational Baseline**: Engine `v3.4.5-geo` (644 funnel rows, 186 active routes, 1,011 fleet, 6,584,762 denominator)  
**Study Scope**: Kashmir Division, Jammu & Kashmir, India (10 Districts)  
**Random Seed**: `20260823`  

---

## 1. Governance & Ledger Protocol

### Purpose
This ledger registers every quantitative claim, empirical finding, statistic, denominator, universe, mathematical derivation, caveat, and manuscript location in the paper companion repository. 

### Non-Negotiable Rules for Authors & Reviewers
1. **Zero Untraced Numbers**: Every numerical statistic in the manuscript prose (Abstract, §1, §3, §4, §5, §6, §8), tables, and figure annotations must explicitly cite a Ledger Claim ID (`[CL-XX]`).
2. **Prohibited Obsolete Claims**: All legacy metrics (342 permits, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet, Srinagar Metropolitan City framing, and any claim of "validation against ridership") are strictly barred from the paper.
3. **Traceability**: Every statistic in this ledger must be directly reproducible via `python analysis/run_all.py --quick` or `--full`.

---

## 2. Summary Master Table of Quantitative Claims (`CL-01` to `CL-66`)

CL-37 onward were added 2026-09-30 as modules a04–a16, a06/a07/a14/a15, v01/v02 and the fleet_model reproduction landed. CL-56–CL-58 were filled from a08/a09 on 2026-09-30. CL-62–CL-66 (literature review, §2) were added 2026-10-04 from `paper/literature_review/`; they are produced by the review pipeline, not by an `analysis/` module.

| Claim ID | Finding / Metric | Short Description | Numerical Value | Denominator / Universe | Primary Source Module | Manuscript Location |
|---|---|---|---|---|---|---|
| `CL-01` | F1 | Raw permit register rows | 614 rows | 614 permit records | `q01_data_quality.py` (D1) | §3.5, §5.1, Table 2a |
| `CL-02` | F1 | Distinct physical corridors | 157 corridors (11m) | 614 permits | `q01_data_quality.py` (D1) | §3.5, §5.1, Table 2a |
| `CL-03` | F1 | Maximum permits on one corridor | 42 permits | Hazratbal–LD corridor | `q01_data_quality.py` (D1) | §3.5, §5.1, Table 2a |
| `CL-04` | F1 | Mean permits per corridor | 3.91 (median: 1.0) | 157 distinct corridors | `q01_data_quality.py` (D1) | §3.5, §5.1 |
| `CL-05` | F1 | Total operational engine input rows | 644 rows | 614 permits + 30 SSCL | `q01_data_quality.py` (D1) | §3.1, §4.1, Table 4 |
| `CL-06` | F1 | Active rationalised routes | 186 routes | 644 engine rows | `Rationalised_Routes_Kashmir_v3.csv` | Abstract, §3.1, §5.1 |
| `CL-07` | F1 | Row reduction decomposition | 71.0 pp unit vs 0.16 pp consolidation | 71.1% raw reduction (458 merged) | `q01_data_quality.py` (D1) | §5.1, Figure 5 |
| `CL-08` | F1 | Physical corridor retention rate | 99.4% (156/157 retained) | 157 distinct corridors | `q01_data_quality.py` (D1) | §3.5, §5.1 |
| `CL-09` | F1 | Suppressed corridor diversity count | 32 via routings suppressed | 20 mixed corridors | `q01_data_quality.py` (D1) | §3.5, §5.1, Table 2a |
| `CL-10` | F1 | Positional permit-to-plan join match | 80.5% token agreement | 614 permit rows | `q01_data_quality.py` (D1) | §3.5 |
| `CL-11` | F2 | WorldPop 2026 study area population | 6,584,763 (active denom: 6,584,762) | 10-district division union | `q01_data_quality.py` (D4) | §3.1, §3.5, Table 2d |
| `CL-12` | F2 | Census 2011 aggregate population | 6,888,475 residents | 10-district division union | `census2011_kashmir_districts.csv` | §3.5, Table 2d |
| `CL-13` | F2 | WorldPop-to-Census population ratio | 0.956 (−0.30%/yr implied CAGR) | 6,584,763 / 6,888,475 | `q01_data_quality.py` (D4) | §3.5, Table 2d |
| `CL-14` | F2 | Districts outside plausible growth band | 8 of 10 districts | 10 districts ([0.5%, 3.0%] CAGR) | `q01_data_quality.py` (D4) | §3.5, Table 2d |
| `CL-15` | F3 | OSRM vs observed in-motion MAPE | 65.1% (RMSE 28.00 min) | 14 matched corridors | `v04_gps_validation.py` | §3.5, §6.3, Table 6a |
| `CL-16` | F3 | Plan vs observed one-way time MAPE | 47.6% (matched corridors) | 5 matched corridors | `v04_gps_validation.py` | §3.5, §6.3, Table 6a |
| `CL-17` | F3 | Plan to observed travel time ratio | 0.513 median (0.51) | 5 matched corridors | `v04_gps_validation.py` | §3.5, §6.3, Table 6a |
| `CL-18` | F4 | Clean driver-GPS trace volume | 43,809 runs (~157 drivers) | Driver app collection Feb–Jun 2026 | `bus-sathi-trace` pipeline | §3.5, §6.3 |
| `CL-19` | F4 | Observed recurring active routes in GPS | 66 of 186 routes (35.5%) | 186 active routes | `q01_data_quality.py` (D2) | §3.5, §6.3, Table 2b |
| `CL-20` | F5 | Total OpenStreetMap POI inventory | 2,431 POIs across 63 categories | 10 districts (0 unplaced) | `q01_data_quality.py` (D5) | §3.5, Table 2e |
| `CL-21` | F5 | POI concentration in Srinagar | 65.3% in Srinagar (1,588 POIs) | 2,431 total POIs | `q01_data_quality.py` (D5) | §3.5, Table 2e |
| `CL-22` | F6 | Walkable road network length | 18,533.2 km (23,323 km bbox) | 10 districts | `q01_data_quality.py` (D3) | §3.5, Table 2c |
| `CL-23` | F6 | Population vs road density correlation | rho = 0.915 (p = 0.0002) | 10 districts | `q01_data_quality.py` (D3) | §3.5, Table 2c |
| `CL-24` | F7 | Plan geometry-distance consistency | 142 consistent / 44 substituted | 186 active routes | `a02b_faithfulness.py` | §4.2, §5.2, Table 3b |
| `CL-25` | F7 | Faithfulness reproduction accuracy | Median error 0.245%, r = 0.995 | 142 consistent routes | `a02b_faithfulness.py` | §4.2, Table 3b |
| `CL-26` | F8 | Catchment population overstatement | 37.4% median (IQR 30.5%–41.7%) | 186 active routes | `a02_network_catchments.py` | Abstract, §4.3, §5.2, Table 3a |
| `CL-27` | F8 | Deduplicated network union overstatement | 31.9% overstatement | 2,339,394 -> 1,592,847 residents | `a02_network_catchments.py` | §4.3, §5.2 |
| `CL-28` | F8 | Headline population coverage revision | 35.5% -> 24.2% of division | 6,584,762 study population | `a02_network_catchments.py` | Abstract, §5.2 |
| `CL-29` | F8 | Parameter sweep robustness on tau | 52.8% (50m) / 37.4% (100m) / 29.2% (150m) | 186 active routes | `a02_network_catchments.py` | §4.3, §5.2 |
| `CL-30` | F9 | Embedded tourist multiplier headcount | 285,914 synthetic persons | 8 tourist-flagged routes | `a02b_faithfulness.py` | §4.2, §5.2 |
| `CL-31` | F10 | Operational sanity cap binding rate | 90.9% of active routes (169/186) | 186 active routes | `v04_gps_validation.py` | §5.3, §6.3, Table 6c |
| `CL-32` | F10 | Caps below real-world pace | Observed median 4.62 min/km | 18 observed corridors | `v04_gps_validation.py` | §5.3, §6.3, Table 6c |
| `CL-33` | F11 | Congestion multiplier moving speed bias | +1.4% bias on City Core (2.20) | 14 matched corridors | `v04_gps_validation.py` | §6.3, Table 6b |
| `CL-34` | F11 | Passenger dwell time model failure | Observed 1.76 min/km vs engine 1.0; R²=0.03 | 18 observed corridors | `v04_gps_validation.py` | §6.3, Table 6b |
| `CL-35` | F12 | Road alignment vs service coverage | 94.0% alignment (obs_frac) vs 35.5% service | 186 active routes | `v04_gps_validation.py` | §3.5, §6.3 |
| `CL-36` | F1/Fleet | Stated rationalised fleet size & self-test | 1,011 buses (+68.5% over 600; 0 mismatches) | 186 routes / 156 non-SSCL self-test | `common.py`, `v04_gps_validation.py` | Abstract, §3.1, §5.4 |
| `CL-37` | F13 | Objective class count | k = 3 by both elbow rules; GVF 0.902; tiers 37/41/108 | 186 active routes, network CDI | `a04_class_count.py` | §4.7, §5.8, Table 5, Fig 7 |
| `CL-38` | F13 | Classifier agreement at k = 3 | Jenks–quantile κ 0.427; Jenks–equal-interval κ 0.748; Jenks ≡ k-means | 186 routes | `a04_class_count.py` | §5.8, Table 5b |
| `CL-39` | F13 | Objective tiers vs published bands | 68.3% agreement, κ 0.503; 20 of 55 published HP routes fall in objective Tier 3 | 186 routes | `a04_class_count.py` | §5.8, §7 |
| `CL-40` | F14 | Route-km vs unique network-km | 5,567.7 vs 1,524.5 km (ratio 3.65); max 53 routes on one link (Lal Chowk); 46.6% of network-km served by one route; baseline unique km NOT_COMPUTABLE, bounded [1,524.5, 13,756.4] | 186 active geometries | `a10_network_diagnostics.py` | §5.5, Table 5c |
| `CL-41` | F15 | Time-of-day profile & banding | Peak 09:00, peak-hour factor 10.67%, peak/base 1.37; peak-anchored banding −9.4% bus-hours at the same fleet; mean-anchored needs +496 (prop.) / +215 (sqrt) buses | CHALO hourly boardings, Apr 2026 (1,221,848) | `a05_headway_timeofday.py` | §5.11, Table 5h |
| `CL-42` | F16 | Frequent-network coverage | ≤15 min 10.4%; ≤20 min 12.2%; ≤35 min 19.2%; any 24.2% | 6,584,762 residents | `a11_coverage_accessibility.py` | §5.6, Table 5d |
| `CL-43` | F16 | Clustering of the uncovered surface | Moran's I 0.664 (2 km, p = 0.001); 0.729 (5 km) | 4,200 / 711 lattice cells | `a11_coverage_accessibility.py` | §5.6, Table 5e |
| `CL-44` | F17 | Accessibility Gini (after) | 0.903 all residents; 0.599 served only; 75.8% with zero service; before-Gini NOT_COMPUTABLE | 6,584,762 residents | `a12_equity_gini.py` | §5.9, Table 5f |
| `CL-45` | F17 | The losers | 32 suppressed via-routings on 20 corridors; 114,879 residents within 400 m of a dropped via-place, of whom 13,087 lose bus access | deduplicated union | `a12_equity_gini.py` | §5.9, Table 5g |
| `CL-46` | F18 | Transfers | 12.5% of stop pairs one-seat, 72.3% one transfer, 13.8% two+, 1.4% unconnected; 66/68 suppressed O–D pairs keep a one-seat ride; 5/68 (7.4%) wait longer; median break-even penalty 31.4 min | 10,153 stop pairs; 68 O–D pairs | `a13_transfers.py` | §5.10, Table 5i |
| `CL-47` | F18 | Observed vehicle duty | median duty factor 0.242; 217 in-service min per vehicle-day | 855 driver-days, 157 drivers | `a13_transfers.py` | §5.10, §5.11 |
| `CL-48` | F19 | Peer-city fleet benchmark | 0.154 buses/1,000 (total pop) = 61st pct, inside M3 PI; 0.635 on served pop = 97th pct, inside M3 PI, above M1 | 36 peer cities (ASRTU 2024) | `a16_peer_regression.py` | §5.7, Table 5j |
| `CL-49` | F20 | Depot deadhead (bounded) | 0% (terminal parking) to 1.7% (district depot, plan day) / 5.5% (observed day); plan assumes 320 vs 99 service km/bus/day | 186 routes; no depot register | `a06_deadhead.py` | §5.11, Table 5k |
| `CL-50` | F21 | Load on the e-bus backbone | today 18.6–37.3 boardings/one-way trip; plan day-one 8.3; ridership ×2.24–4.49 to hold today's; proxy peak boarding/capacity median 0.227, 152/186 < 0.40 | CHALO 12-month mean; plan | `a07_load_factor.py` | §5.11, Table 5l |
| `CL-51` | F22 | Cost & CO2 envelope (PROVISIONAL, D8) | ₹642–1,054 cr/yr (plan km) or ₹206–338 cr (observed km); 65–103 kt or 21–33 kt CO2/yr; engine e-bus factor 30 g/km vs ~874 g/km (×29) | 120M / 38M veh-km/yr | `a14_cost_emissions.py` | §5.12, Table 5m |
| `CL-52` | F23 | Policy scenarios | S1 1,169 (+15.6%); S2 1,271 (+25.7%, bound); S3 1,106 (+9.4%); S4 84 routes, 533 buses (−47.3%), coverage 24.2→20.3%; S5 1,172 (+15.9%), ≤15-min coverage 10.4→14.5% | S0 = 1,011 | `a15_scenarios.py` | §5.13, Table 8 |
| `CL-53` | V1 | Building-footprint cross-check | **Microsoft ML footprints (1,852,714 in the union; 99.8% of population in cells with a building): route ρ 0.975 (area), 0.940 (count); 1-km grid ρ 0.907 all / 0.950 populated — all pass.** OSM (12,343 buildings): route 0.657 / 0.544, grid 0.316 — OSM mapping covers 4–31% of populated cells | 186 routes; 13,645 cells | `v01_spatial_crossval.py` | §6.2, Table 6d/6e |
| `CL-54` | V2 | CHALO benchmark (circular) | plan 283 vs CHALO 98 scaled to 15 min = 179–220 → ratio 1.29–1.58: FAIL ±15% at every service-day assumption; route rank ρ 0.22 (p 0.24) | 30 SSCL routes, 12-month mean | `v02_benchmark.py` | §6.2, Table 6f |
| `CL-55` | F10 | Supply-model reproduction & cap counterfactual | cycle 186/186, fleet 186/186 (1,011), 169 at cap; cap removed alone → 1,648 buses | 186 routes | `fleet_model.py` | §4.8, §5.4 |
| `CL-56` | V6 | Fleet interval (Monte Carlo, 5,000 draws) | Regime A (as specified): 1,013 [989–1,058]; Regime B (observed urban/peri-urban pace): 1,182 [1,130–1,266] — Urban 372, Peri-Urban 428, Regional 384 (as modelled); B at median pace = 1,169 | 11 declared parameters + 2 pace priors (16 Srinagar-belt corridors) | `a09_monte_carlo_sobol.py` | Abstract, §5.7, §6.2, §8, Table 7b, Fig 9 |
| `CL-57` | V6 | Tier stability and coverage interval | tier agreement 97.8% [94.6–100%], P(>80%) = 1.00; 179/186 routes (96.2%) keep their tier in >80% of draws, 7 do not; coverage 26.7% [22.1–32.2%] (driven by the walk-radius definition) | 5,000 draws | `a09_monte_carlo_sobol.py`, `a08_sensitivity_oat.py` | §5.7, §6.2, Table 7b |
| `CL-58` | V5 | Sobol' variance decomposition (total order) | Fleet A: spare ratio 0.94; Fleet B: spare ratio 0.55, peri-urban pace 0.32, urban pace 0.13; tiers: population weight 0.93, walk radius 0.17; coverage: walk radius 0.97; OAT with cap on: run-time parameters move fleet ≤17 buses, with cap off up to 956 | Saltelli N = 1,024, 15,360 evaluations | `a09_monte_carlo_sobol.py`, `a08_sensitivity_oat.py` | §5.7, §6.2, §7.5, Table 7a/7c, Fig 9b |
| `CL-59` | Method | Corrections to the method as published | engine capture scale κ = 0.33 (not 0.18); Eq. 8 demand proxy sets headway on the 67 non-backbone Regional routes (5 at 35, 62 at 50 min); engine merge test = 80 m line-buffer overlap ≥ θ AND starts ≤ 2.5 km | engine source | `transit_kashmir_v3.py:547, 5551, 2640` | §4.5, §4.6, §4.7 |
| `CL-60` | Fleet | Buses per 100,000 by denominator | 15.4 (division 6,584,762); 43.6 (engine Euclidean served 2,317,958); 63.5 (network served 1,592,847) — last above MoHUA 40–60 | 1,011 buses | `a11`, plan CSV | §4.8, §5.4 |
| `CL-61` | F23 | Funding-constrained sequencing | 30% of fleet (303 buses, 63 routes) reaches 22.4% of residents = 92% of the full plan's 24.2%; 50% of reach costs 54 buses, 90% costs 264 | greedy marginal coverage per bus | `a15_scenarios.py` | §7.7, Table 8b |
| `CL-62` | Lit | Literature search yield | 5,488 unique records (OpenAlex 3,584; Scopus 3,965; 2,061 overlap); 2,518 screened on title/abstract; 873 eligible (469 maybe, 1,176 excluded) | 13 OpenAlex + 19 Scopus queries, 2000–2026, run 2026-09-30/10-01 | `paper/literature_review/prisma_counts.md`, `search_log.csv`, `scopus_log.csv`, `screening_decisions.csv` | §2.1 |
| `CL-63` | Lit | Coded corpus | 60 studies (57 from search + 3 seminal by citation chaining); 46 coded from full text, 14 from abstracts; 56 placed on both axes (C56, C57, C58, C60 excluded as unclear) | purposive, theme-stratified sample of the 873 | `paper/literature_review/table1_final.csv`, `table1_summary.json` | §2.1, §2.8, Table 1 |
| `CL-64` | Lit | Data intensity × planning output | full plans: 6, all at intensity 4; intensity 2–3: 0 full / 8 partial of 30; intensity 5: 0 of 5; intensity 1: no coded study | 56 studies on both axes | `paper/literature_review/crosstab_intensity_plan.csv`, `finalise_table1.py` | §2.8, Figure 2 |
| `CL-65` | Lit | Corpus descriptors | 10 of 60 demonstrated only on benchmark/synthetic OD; 42 of 60 report no equity treatment | 60 coded studies | `paper/literature_review/table1_summary.json` | §2.2, §2.6 |
| `CL-66` | Lit | Novelty check | 750 records scored against six pipeline elements (359 Scopus novelty-query hits, 377 OpenAlex, 14 screener-flagged) + 12 web searches; five closest papers read in full; no study performs the whole chain, every single element has prior work | — | `paper/literature_review/03_novelty_check.md`, `04_fulltext_verification.md` | §1.5, §2.4, §2.7, §2.8 |

---

## 3. Detailed Claim Profiles & Verification Records

### [CL-01] Raw Permit Register Count
- **Finding**: F1
- **Exact Manuscript Text**: "The official stage carriage register in Kashmir Division contains 614 permit records (`existing-routes.csv`)."
- **Numerical Value**: 614
- **Formula / Derivation**: `len(pd.read_csv("data/raw/existing-routes.csv")) == 614`
- **Denominator / Universe**: Complete digitized RTO Kashmir permit database.
- **Source Module & File**: `analysis/q01_data_quality.py:73`, `data/raw/existing-routes.csv`.
- **Caveats**: Each row represents an administrative vehicle permit, not a distinct transit route.
- **Manuscript Placement**: §3.5, §5.1, Table 2a.

### [CL-02] Distinct Physical Corridors
- **Finding**: F1
- **Exact Manuscript Text**: "Spatial clustering of permit endpoints reveals that the 614 permits operate over exactly 157 distinct origin–destination corridors at 11 m resolution (155 corridors at 100 m resolution)."
- **Numerical Value**: 157 (at 11 m), 155 (at 100 m)
- **Formula / Derivation**: Undirected coordinate hashing of origin/destination coordinates: `len(corridors_11m) == 157`.
- **Denominator / Universe**: 614 permit rows.
- **Source Module & File**: `analysis/q01_data_quality.py:98-115`, `data/derived/q01_data_quality.json:19-20`.
- **Caveats**: Corridors are undirected (A–B is treated as identical to B–A).
- **Manuscript Placement**: §3.5, §5.1, Table 2a.

### [CL-03] Maximum Permits on a Single Corridor
- **Finding**: F1
- **Exact Manuscript Text**: "Permit concentration is highly skewed: the single most heavily duplicated corridor, Hazratbal to Lal Ded Hospital (LD), carries 42 separate permits across different operators."
- **Numerical Value**: 42 permits
- **Formula / Derivation**: `permits_per_corridor.max() == 42` (Hazratbal to LD, Route `FDR-147`).
- **Denominator / Universe**: 157 distinct corridors.
- **Source Module & File**: `analysis/q01_data_quality.py:120`, `data/derived/q01_data_quality.json:6`.
- **Caveats**: Reflects historical individual minibus permit issuance along the major hospital/university axis.
- **Manuscript Placement**: §3.5, §5.1, Table 2a.

### [CL-04] Mean Permits per Corridor
- **Finding**: F1
- **Exact Manuscript Text**: "The 614 permits average 3.91 permits per corridor, with a median of 1.0 permit."
- **Numerical Value**: Mean: 3.9108; Median: 1.0
- **Formula / Derivation**: `614 / 157 = 3.9108`
- **Denominator / Universe**: 157 distinct corridors.
- **Source Module & File**: `analysis/q01_data_quality.py:122`, `data/derived/q01_data_quality.json:7-8`.
- **Caveats**: 75 corridors have duplicate permits; 82 corridors have exactly 1 permit.
- **Manuscript Placement**: §3.5, §5.1.

### [CL-05] Total Operational Engine Input Rows
- **Finding**: F1
- **Exact Manuscript Text**: "The operational optimization engine ingests 644 route rows, comprising 614 permit-derived rows (`R0001`–`R0614`) and 30 synthetic electric bus backbone routes (`SSCL-01`–`SSCL-30`)."
- **Numerical Value**: 644
- **Formula / Derivation**: `614 + 30 = 644`
- **Denominator / Universe**: Total input route candidates in engine v3.4.5.
- **Source Module & File**: `analysis/common.py:35`, `data/raw/Rationalised_Routes_Kashmir_v3.csv`.
- **Caveats**: SSCL routes are fixed modern e-bus services operated under smart city tenders.
- **Manuscript Placement**: §3.1, §4.1, Table 4.

### [CL-06] Active Rationalised Routes
- **Finding**: F1
- **Exact Manuscript Text**: "The rationalisation plan designates 186 active routes (32 trunk and 154 feeder services), with the remaining 458 rows consolidated."
- **Numerical Value**: 186 active routes (32 Trunk, 154 Feeder)
- **Formula / Derivation**: `plan['Action_Taken'].isin(['UPGRADED_TO_TRUNK', 'RETAINED_AS_FEEDER']).sum() == 186`
- **Denominator / Universe**: 644 engine candidate rows.
- **Source Module & File**: `analysis/common.py:124`, `data/derived/q01_data_quality.json:13`.
- **Caveats**: Active routes comprise 68 Urban, 47 Peri_Urban, and 71 Regional_District routes.
- **Manuscript Placement**: Abstract, §3.1, §5.1.

### [CL-07] Row Reduction Decomposition
- **Finding**: F1
- **Exact Manuscript Text**: "The 71.1% apparent route reduction (644 rows → 186 active routes) is almost entirely an accounting artifact: 71.0 percentage points reflect changing the unit of analysis by collapsing duplicate permits on identical corridors, while genuine spatial consolidation of distinct corridors accounts for only 0.16 percentage points (1 corridor)."
- **Numerical Value**: 71.12% total reduction; 70.96 pp unit change; 0.16 pp spatial consolidation.
- **Formula / Derivation**: Unit change: `457 / 644 = 0.7096`; Spatial consolidation: `1 / 644 = 0.00155`; Total: `458 / 644 = 0.7112`.
- **Denominator / Universe**: 644 engine input rows.
- **Source Module & File**: `analysis/q01_data_quality.py:140-165`, `data/derived/q01_data_quality.json:27-29`.
- **Caveats**: The only corridor consolidated on spatial overlap is `FDR-289` (Parimpora–Pantha Chowk).
- **Manuscript Placement**: §5.1, Figure 5.

### [CL-08] Physical Corridor Retention Rate
- **Finding**: F1
- **Exact Manuscript Text**: "Measured on distinct physical corridors, the rationalisation plan retains 156 of 157 permit corridors (99.4%) and adds 30 new e-bus routes, resulting in zero route count reduction."
- **Numerical Value**: 99.36% (156 / 157 retained)
- **Formula / Derivation**: `156 / 157 = 0.99363`
- **Denominator / Universe**: 157 distinct permit corridors.
- **Source Module & File**: `analysis/q01_data_quality.py:170`, `data/derived/q01_data_quality.json:3`.
- **Caveats**: Rebuts all claims of bus network shrinkage; rationalisation reformed frequencies and fleet, not physical route coverage.
- **Manuscript Placement**: §3.5, §5.1.

### [CL-09] Suppressed Corridor Diversity Count
- **Finding**: F1
- **Exact Manuscript Text**: "Collapsing permit records into unified corridors imposes concrete operational trade-offs: 32 alternative via-routings across 20 corridors are suppressed, 38 corridors lose vehicle class differentiation, and 34 lose service tier differentiation."
- **Numerical Value**: 32 alternative via-routings; 20 corridors; 38 mixed vehicle classes; 34 mixed service types.
- **Formula / Derivation**: Direct enumeration of distinct `Via_Points_Raw`, `Vehicle_Category`, and `Service_Type` per corridor.
- **Denominator / Universe**: 157 distinct corridors.
- **Source Module & File**: `analysis/q01_data_quality.py:180-210`, `data/derived/q01_data_quality.json:14-18`.
- **Caveats**: Quantifies the unstated cost of corridor-level consolidation for passengers on non-representative alignments.
- **Manuscript Placement**: §3.5, §5.1, Table 2a.

### [CL-10] Positional Permit-to-Plan Join Match Rate
- **Finding**: F1
- **Exact Manuscript Text**: "The positional linkage between the permit register and engine plan achieves an 80.5% name-token match rate across non-synthetic routes."
- **Numerical Value**: 80.46% (0.80456)
- **Formula / Derivation**: Origin and destination name-token overlap check on 614 permit-derived rows.
- **Denominator / Universe**: 614 permit rows with origin/destination strings.
- **Source Module & File**: `analysis/q01_data_quality.py:93`, `data/derived/q01_data_quality.json:5`.
- **Caveats**: Residual mismatches stem from vernacular Kashmiri spelling variants (e.g., Rainawari / Rainawara).
- **Manuscript Placement**: §3.5.

### [CL-11] WorldPop 2026 Study Area Population
- **Finding**: F2
- **Exact Manuscript Text**: "The WorldPop 2026 UN-adjusted population surface yields a zonal sum of 6,584,763 residents across the 10-district Kashmir Division union, exactly matching the active engine denominator of 6,584,762."
- **Numerical Value**: 6,584,763 (raster zonal sum: 6,584,762.62; engine active denominator: 6,584,762)
- **Formula / Derivation**: `rasterstats.zonal_stats(districts_union, 'kashmir_worldpop.tif', stats='sum')`
- **Denominator / Universe**: 10 districts of Kashmir Division.
- **Source Module & File**: `analysis/common.py:119`, `data/derived/q01_data_quality.json:77-90`.
- **Caveats**: Single source of truth denominator for all network-level population coverage shares.
- **Manuscript Placement**: §3.1, §3.5, Table 2d.

### [CL-12] Official Census 2011 Population Total
- **Finding**: F2
- **Exact Manuscript Text**: "Official Census of India 2011 Primary Census Abstract records 6,888,475 residents across the same 10 districts."
- **Numerical Value**: 6,888,475
- **Formula / Derivation**: Sum of `population_2011` in `census2011_kashmir_districts.csv`.
- **Denominator / Universe**: 10 districts of Kashmir Division.
- **Source Module & File**: `data/raw/census2011_kashmir_districts.csv`, `data/derived/q01_data_quality.json:70`.
- **Caveats**: Official decennial census benchmark; last census enumeration conducted in Jammu & Kashmir.
- **Manuscript Placement**: §3.5, Table 2d.

### [CL-13] WorldPop-to-Census Ratio & Implied Growth
- **Finding**: F2
- **Exact Manuscript Text**: "The WorldPop 2026 surface sits below Census 2011 for the same administrative boundary (ratio: 0.956), implying an annual growth rate of −0.30%/year over 15 years against historical decadal growth of +23.6% (+2.1%/year)."
- **Numerical Value**: Ratio: 0.95591; Implied CAGR: −0.00300 (−0.30%/yr).
- **Formula / Derivation**: Ratio: `6,584,763 / 6,888,475 = 0.95591`; CAGR: `(6584763 / 6888475)**(1/15) - 1 = -0.0030016`.
- **Denominator / Universe**: 10-district division population.
- **Source Module & File**: `analysis/q01_data_quality.py:270-285`, `data/derived/q01_data_quality.json:79-89`.
- **Caveats**: Proves the population raster is structurally conservative. Downstream coverage percentages are biased upward; absolute headcounts served are biased downward.
- **Manuscript Placement**: §3.5, Table 2d.

### [CL-14] Districts Outside Plausible Population Growth Band
- **Finding**: F2
- **Exact Manuscript Text**: "8 of the 10 valley districts fall outside a plausible annual population growth band of [0.5%, 3.0%], indicating unmodelled regional out-migration or downscaling artifacts in global gridded products."
- **Numerical Value**: 8 of 10 districts
- **Formula / Derivation**: Evaluation against `CAGR_BAND = (0.005, 0.030)`.
- **Denominator / Universe**: 10 districts.
- **Source Module & File**: `analysis/q01_data_quality.py:290`, `data/derived/q01_data_quality.json:80`.
- **Caveats**: Only Ganderbal (+1.23%/yr) and Pulwama (+0.53%/yr) fall within the plausible growth interval.
- **Manuscript Placement**: §3.5, Table 2d.

### [CL-15] OSRM Free-Flow vs Observed In-Motion Runtime Error
- **Finding**: F3
- **Exact Manuscript Text**: "Uncalibrated routing-engine free-flow driving duration underestimates observed bus in-motion travel time with a Mean Absolute Percentage Error (MAPE) of 65.1% (RMSE 28.00 min)."
- **Numerical Value**: MAPE: 65.12% (0.65117); RMSE: 28.00 min.
- **Formula / Derivation**: `mean(abs(OSRM_duration - obs_in_motion) / obs_in_motion) = 0.6512`.
- **Denominator / Universe**: 14 matched corridor runs.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/q01_data_quality.json:167-177`.
- **Caveats**: Compares driving duration without dwell against GPS in-motion time excluding dwell.
- **Manuscript Placement**: §3.5, §6.3, Table 6a.

### [CL-16] Plan vs Observed One-Way Travel Time MAPE
- **Finding**: F3
- **Exact Manuscript Text**: "Modelled one-way travel time in the transit plan diverges from observed door-to-door GPS runtime with a MAPE of 47.6% on matched corridors."
- **Numerical Value**: 47.64% (0.4764)
- **Formula / Derivation**: `mean(abs(plan_time - obs_total_time) / obs_total_time) = 0.4764` across 5 matched corridors.
- **Denominator / Universe**: 5 matched in-sample corridors (`FDR-050`, `FDR-262`, `FDR-270`, `FDR-370`, `FDR-575`).
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:241`.
- **Caveats**: Evaluated on in-sample corridors whose cycle times were post-corrected in v3.4.5.
- **Manuscript Placement**: §3.5, §6.3, Table 6a.

### [CL-17] Modelled to Observed Travel Time Ratio
- **Finding**: F3
- **Exact Manuscript Text**: "Modelled transit run times achieve a median ratio of only 0.51 relative to real-world GPS run times on matched corridors (0.62 across all 14 matches)."
- **Numerical Value**: Median ratio: 0.513 (5 matched corridors); 0.620 (14 corridor matches).
- **Formula / Derivation**: `median(plan_time / obs_total_time) = 0.513`.
- **Denominator / Universe**: 5 matched corridors / 14 corridor associations.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:247`.
- **Caveats**: Provides empirical justification for treating required fleet as an uncertainty interval rather than a single point estimate.
- **Manuscript Placement**: §3.5, §6.3, Table 6a.

### [CL-18] Driver-GPS Clean Trace Dataset Volume
- **Finding**: F4
- **Exact Manuscript Text**: "The empirical GPS observation layer comprises 43,809 clean service runs collected from approximately 157 driver devices between February and June 2026."
- **Numerical Value**: 43,809 runs (~157 drivers)
- **Formula / Derivation**: Filtered and sessionized trajectories in `E:\bus-sathi-trace`.
- **Denominator / Universe**: Full driver-app trace database.
- **Source Module & File**: `data/raw/gps/reality_check.csv`, `data/derived/q01_data_quality.json:52`.
- **Caveats**: Unofficial operator app adoption; spatial coverage is concentrated in Srinagar and surrounding suburban corridors.
- **Manuscript Placement**: §3.5, §6.3.

### [CL-19] Observed Active Routes in Driver GPS
- **Finding**: F4
- **Exact Manuscript Text**: "66 of the 186 active routes (35.5%) are corroborated by recurring service runs in driver GPS, providing an empirical lower bound on active service."
- **Numerical Value**: 66 of 186 routes (35.48%)
- **Formula / Derivation**: `(active['status'] == 'OBSERVED').sum() == 66`
- **Denominator / Universe**: 186 active routes (Urban: 45/68, Peri_Urban: 20/47, Regional: 1/71).
- **Source Module & File**: `analysis/q01_data_quality.py:220-250`, `data/derived/q01_data_quality.json:54-58`.
- **Caveats**: 75 routes have `NO_APP_DATA` and 45 have `PARTIAL` coverage. Unobserved routes reflect partial driver app uptake, not administrative dormancy.
- **Manuscript Placement**: §3.5, §6.3, Table 2b.

### [CL-20] OpenStreetMap Point of Interest Inventory
- **Finding**: F5
- **Exact Manuscript Text**: "The spatial opportunity layer incorporates 2,431 Points of Interest across 63 distinct categories, stratified into High (1,030), Medium (1,080), and Seasonal (321) importance tiers."
- **Numerical Value**: Total: 2,431; Tier 1: 1,030; Tier 2: 1,080; Tier 3: 321.
- **Formula / Derivation**: Exact counts in `data/raw/pois.csv`.
- **Denominator / Universe**: All placed POIs within Kashmir Division (0 unplaced).
- **Source Module & File**: `analysis/q01_data_quality.py:320-350`, `data/derived/q01_data_quality.json:96-105`.
- **Caveats**: No independent ground field survey was conducted (reported as not performed); inventory reflects OpenStreetMap mapping effort.
- **Manuscript Placement**: §3.5, Table 2e.

### [CL-21] POI Concentration in Srinagar District
- **Finding**: F5
- **Exact Manuscript Text**: "Opportunity data is heavily concentrated in the central urban area: 65.3% of all POIs (1,588 of 2,431) lie in Srinagar district, where POI density reaches 120.4 per 100,000 residents compared to 0.32 in Kupwara."
- **Numerical Value**: Srinagar share: 65.32% (1,588 / 2,431); Density range: 0.32 to 120.44 per 100k.
- **Formula / Derivation**: `1588 / 2431 = 0.65323`; `1588 / 13.1845 = 120.44`.
- **Denominator / Universe**: 2,431 POIs; district resident population.
- **Source Module & File**: `analysis/q01_data_quality.py:360`, `data/derived/q01_data_quality.json:112-114`.
- **Caveats**: Highlights potential volunteered geographic information (VGI) bias, requiring sensitivity testing of POI weights.
- **Manuscript Placement**: §3.5, Table 2e.

### [CL-22] Walkable Pedestrian Network Length
- **Finding**: F6
- **Exact Manuscript Text**: "The walkable road network extracted from OpenStreetMap spans 18,533.2 km within the 10 districts (23,323 km within the padded study bounding box)."
- **Numerical Value**: 18,533.2 km (in districts); 23,323.0 km (in bounding box).
- **Formula / Derivation**: Metric sum of walkable graph edges inside district administrative polygons.
- **Denominator / Universe**: 10 districts of Kashmir Division.
- **Source Module & File**: `analysis/a01_build_walk_graph.py`, `data/derived/q01_data_quality.json:66`.
- **Caveats**: Graph excludes motorways, trunks with foot=no, and steep mountain trails.
- **Manuscript Placement**: §3.5, Table 2c.

### [CL-23] Population vs Road Density Correlation
- **Finding**: F6
- **Exact Manuscript Text**: "District population density correlates strongly with mapped road network density (Spearman rho = 0.915, p = 0.0002), confirming that OpenStreetMap road completeness tracks settlement density without severe spatial bias."
- **Numerical Value**: rho = 0.91515; p-value = 0.000204.
- **Formula / Derivation**: `scipy.stats.spearmanr(pop_density, road_density)`.
- **Denominator / Universe**: 10 districts.
- **Source Module & File**: `analysis/q01_data_quality.py:310`, `data/derived/q01_data_quality.json:64`.
- **Caveats**: Serves as the primary validation check licensing the OSM pedestrian graph without ad-hoc completeness corrections.
- **Manuscript Placement**: §3.5, Table 2c.

### [CL-24] Plan Geometry vs Distance Internal Consistency
- **Finding**: F7
- **Exact Manuscript Text**: "142 of the 186 active routes (76.3%) exhibit self-consistent alignments where declared `Route_KM` agrees with OSRM geometry length within 1%, while 44 routes represent externally verified road distance substitutions."
- **Numerical Value**: 142 consistent routes (76.34%); 44 substituted distance routes (23.66%).
- **Formula / Derivation**: `abs(declared_km - geom_km) / declared_km <= 0.01`
- **Denominator / Universe**: 186 active routes.
- **Source Module & File**: `analysis/a02b_faithfulness.py`, `data/derived/a02b_faithfulness.json:2-7`.
- **Caveats**: On the 44 substituted routes, distance was patched in engine v3.4.4 without re-running geometry routing or recomputing catchment population.
- **Manuscript Placement**: §4.2, §5.2, Table 3b.

### [CL-25] Catchment Faithfulness Reproduction
- **Finding**: F7
- **Exact Manuscript Text**: "On the 142 self-consistent routes, the independent reimplementation reproduces the published plan's Euclidean population served with a median absolute error of 0.245% and Pearson r = 0.995, with 136 routes matching within 1%."
- **Numerical Value**: Median error: 0.245%; Pearson r = 0.99498; 136 of 142 <= 1.0% error; 139 of 142 <= 5.0% error.
- **Formula / Derivation**: `median(abs(recomputed - published) / published) = 0.00245` after applying tourist multiplier.
- **Denominator / Universe**: 142 self-consistent active routes.
- **Source Module & File**: `analysis/a02b_faithfulness.py`, `data/derived/a02b_faithfulness.json:81-89`.
- **Caveats**: Residuals are 100% accounted for (3 minor drift, 1 stale tourist flag, 2 superseded geometries).
- **Manuscript Placement**: §4.2, Table 3b.

### [CL-26] Euclidean Catchment Population Overstatement
- **Finding**: F8 (Central Methodological Finding)
- **Exact Manuscript Text**: "Across all 186 active routes, replacing straight-line circular Euclidean buffers with walkable network catchments on the OSM pedestrian graph reduces measured population served by a median of 37.4% per route (mean 37.1%, IQR 30.5%–41.7%, max 56.8%), with 184 routes overstated by more than 25%."
- **Numerical Value**: Median overstatement: 37.39%; IQR: [30.49%, 41.73%]; Max: 56.78%; 184/186 > 25%; 11/186 > 50%.
- **Formula / Derivation**: `overstatement = (pop_euclid - pop_net) / pop_euclid` per route.
- **Denominator / Universe**: 186 active routes.
- **Source Module & File**: `analysis/a02_network_catchments.py`, `data/derived/a02_network_catchments.json:8-17`.
- **Caveats**: Because network catchments allow an off-network buffer tolerance tau = 100m, this measured 37.4% overstatement is an empirical lower bound on true Euclidean bias.
- **Manuscript Placement**: Abstract, §4.3, §5.2, Table 3a.

### [CL-27] Network-Wide Deduplicated Catchment Overstatement
- **Finding**: F8
- **Exact Manuscript Text**: "On the deduplicated network-wide union, Euclidean buffering overstates total served population by 31.9%, collapsing from 2,339,394 to 1,592,847 residents."
- **Numerical Value**: 31.91% overstatement (Euclidean union: 2,339,394; Network union: 1,592,847).
- **Formula / Derivation**: `(2339393.75 - 1592846.75) / 2339393.75 = 0.31912`.
- **Denominator / Universe**: Deduplicated population raster cells within 400 m of transit network.
- **Source Module & File**: `analysis/a02_network_catchments.py`, `data/derived/a02_network_catchments.json:18-19, 53`.
- **Caveats**: Only deduplicated network unions may be reported; summing individual route catchments double-counts overlapping populations.
- **Manuscript Placement**: §4.3, §5.2.

### [CL-28] Headline Population Coverage Revision
- **Finding**: F8
- **Exact Manuscript Text**: "Correcting for real pedestrian path friction lowers headline regional population coverage from 35.5% to 24.2% of the study area population, while network catchment area shrinks to half of Euclidean buffer area (median ratio 0.502)."
- **Numerical Value**: Euclidean coverage: 35.53%; Network coverage: 24.19%; Median area ratio: 0.5025.
- **Formula / Derivation**: `2339394 / 6584762 = 0.35527`; `1592847 / 6584762 = 0.24190`.
- **Denominator / Universe**: 6,584,762 (WorldPop 2026 10-district division population).
- **Source Module & File**: `analysis/a02_network_catchments.py`, `data/derived/a02_network_catchments.json:2-4`.
- **Caveats**: Direct refutation of legacy 95.7% urban coverage claims.
- **Manuscript Placement**: Abstract, §5.2.

### [CL-29] Robustness of Catchment Bias to Off-Network Parameter Tau
- **Finding**: F8
- **Exact Manuscript Text**: "The catchment bias finding is structurally robust across parameter variations: sweeping off-network tolerance tau from 50 m to 150 m yields median population overstatements of 52.8%, 37.4%, and 29.2%."
- **Numerical Value**: tau=50m: 52.77%; tau=100m: 37.39%; tau=150m: 29.18%; 46 of 22,360 stops off-network (0.21%, median offset 11.0m).
- **Formula / Derivation**: Swept in `analysis/a02_network_catchments.py:350-410`.
- **Denominator / Universe**: 186 active routes; 22,360 virtual stops.
- **Source Module & File**: `analysis/a02_network_catchments.py`, `data/derived/a02_network_catchments.json:34-47`.
- **Caveats**: Demonstrates that Euclidean overstatement is invariant to parameter tuning.
- **Manuscript Placement**: §4.3, §5.2.

### [CL-30] Embedded Tourist Demand Multiplier Distortion
- **Finding**: F9
- **Exact Manuscript Text**: "An undocumented tourist demand multiplier (1.30×) applied to population served on 8 active routes artificially injects 285,914 synthetic persons into published headcount figures."
- **Numerical Value**: 285,914 synthetic headcount excess (published sum: 1,238,960; resident sum: 953,046).
- **Formula / Derivation**: `1238960 - 953046 = 285914` across 8 routes where `Route_Type == 'Tourist_Corridor'`.
- **Denominator / Universe**: 8 tourist-flagged routes.
- **Source Module & File**: `analysis/a02b_faithfulness.py`, `data/derived/a02b_faithfulness.json:100-108`.
- **Caveats**: A demand multiplier was incorrectly placed into a physical headcount metric and used as a coverage numerator.
- **Manuscript Placement**: §4.2, §5.2.

### [CL-31] Operational Cycle-Time Sanity Cap Binding Rate
- **Finding**: F10
- **Exact Manuscript Text**: "The operational per-km cycle-time cap binds exactly on 169 of the 186 active routes (90.9%), including 100% of Regional (71/71), 97.9% of Peri-Urban (46/47), and 76.5% of Urban routes (52/68)."
- **Numerical Value**: 90.86% (169 / 186 routes). Regional: 71/71 (100.0%); Peri_Urban: 46/47 (97.87%); Urban: 52/68 (76.47%).
- **Formula / Derivation**: `np.isclose(active['Cycle_Time_Min'], active['Route_KM'] * 2.0 * cap, rtol=0.005).sum() == 169`.
- **Denominator / Universe**: 186 active routes.
- **Source Module & File**: `analysis/v04_gps_validation.py:270-285`, `data/derived/v04_gps_validation.json:32-34`.
- **Caveats**: Proves that an intended sanity ceiling became the primary driver of cycle times and fleet sizing across 91% of the network.
- **Manuscript Placement**: §5.3, §6.3, Table 6c.

### [CL-32] Disparity Between Sanity Caps and Real Pace
- **Finding**: F10
- **Exact Manuscript Text**: "Asserted per-km caps sit substantially below real-world driving conditions: observed median bus pace from driver GPS is 4.62 min/km (p90 = 6.28 min/km), exceeding the Urban cap (4.0 min/km) on 83.3% of observed corridors, the Peri-Urban cap (2.5 min/km) on 88.9%, and the Regional cap (1.5 min/km) on 100%."
- **Numerical Value**: Observed median pace: 4.62 min/km; p90: 6.28 min/km. Corridors exceeding cap: Urban 15/18 (83.3%); Peri-Urban 16/18 (88.9%); Regional 18/18 (100.0%).
- **Formula / Derivation**: `obs_pace = 60.0 / effective_kmh`; compare against cap thresholds (4.0, 2.5, 1.5 min/km).
- **Denominator / Universe**: 18 corridor profiles from driver GPS.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:2-31`.
- **Caveats**: Mechanistically explains why uncalibrated modelled cycle times understate reality (Finding F3).
- **Manuscript Placement**: §5.3, §6.3, Table 6c.

### [CL-33] Congestion Multiplier Decomposition
- **Finding**: F11
- **Exact Manuscript Text**: "Decomposing run-time components reveals that the City Core congestion multiplier (OSRM duration ÷ 2.20) reproduces observed bus moving speed with only +1.4% median bias (modelled 17.95 km/h vs observed 20.55 km/h), whereas Peri-Urban (+59.4%) and Rural (+123.2%) multipliers fail in the urban core."
- **Numerical Value**: City Core bias: +1.4% (modelled median: 17.95 km/h; observed median: 20.55 km/h; MAPE 28.4%).
- **Formula / Derivation**: `(modelled_speed - observed_speed) / observed_speed` for `CONGESTION['City_Core'] = 2.20`.
- **Denominator / Universe**: 14 matched corridors.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:134-178`.
- **Caveats**: All observed GPS corridors sit in the greater Srinagar urban region; Peri-Urban and Rural multipliers evaluated here are classification counterfactuals.
- **Manuscript Placement**: §6.3, Table 6b.

### [CL-34] Passenger Dwell Time Model Failure
- **Finding**: F11
- **Exact Manuscript Text**: "The engine's assumption of a constant 1.0 min/km dwell penalty fails against empirical observation: observed dwell averages 1.76 min/km (median dwell share 38.0%), and an ordinary least squares regression (`dwell_min = 17.67 + 0.247·km`, R² = 0.03) yields a significant constant intercept (p < 0.05) and non-significant distance slope, disproving distance-proportional dwell."
- **Numerical Value**: Observed dwell median: 1.757 min/km; Dwell share median: 38.0% (range: 15%–74%); OLS intercept: 17.67 min (95% CI: [7.41, 27.94]); slope: 0.247 min/km (95% CI: [-0.494, 0.989]); R²: 0.03.
- **Formula / Derivation**: OLS regression of total corridor dwell minutes against route length.
- **Denominator / Universe**: 18 observed corridor profiles.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:35-76`.
- **Caveats**: Passenger dwell is dominated by fixed terminal layover and dispatch holds rather than per-stop boardings.
- **Manuscript Placement**: §6.3, Table 6b.

### [CL-35] Road Alignment vs Operational Service Corroboration
- **Finding**: F12
- **Exact Manuscript Text**: "GPS traces corroborate that 98.4% of planned route alignments (183 of 186 routes, median `obs_frac` = 94.0%) operate over roads carrying active bus traffic, but only 35.5% of routes (66 of 186) are corroborated as recurring operational services."
- **Numerical Value**: Alignment coverage: 183 of 186 routes > 0 (median obs_frac = 0.94; 171 >= 50%; 137 >= 80%; 33 = 100%); Service status: 66 observed, 45 partial, 75 no app data.
- **Formula / Derivation**: `obs_frac` in `gps/route_evidence.csv` vs `status` in `gps/permit_observed.csv`.
- **Denominator / Universe**: 186 active routes.
- **Source Module & File**: `analysis/v04_gps_validation.py`, `data/derived/v04_gps_validation.json:180-190`.
- **Caveats**: Authors must never conflate physical road alignment coverage (94%) with service-level route validation (35.5%).
- **Manuscript Placement**: §3.5, §6.3.

### [CL-36] Stated Fleet Sizing & Formula Self-Test
- **Finding**: Baseline Fleet
- **Exact Manuscript Text**: "The published rationalisation plan mandates a total fleet of 1,011 buses (187 High Priority Vehicles, 754 Medium Priority Vehicles, 70 Low Priority Vehicles), representing a 68.5% expansion over the existing operating fleet of approximately 600 private minibuses and providing 43 buses per 100,000 residents served."
- **Numerical Value**: Total fleet: 1,011 buses (187 HPV, 754 MPV, 70 LPV); Expansion: +68.5% (+411 buses over 600 baseline); Service benchmark: 43 buses/lakh served; Fleet formula self-test mismatches: exactly 0 on all 156 non-SSCL active routes.
- **Formula / Derivation**:
  `operating = max(1, ceil(cycle_min / max(1, headway_min)))`  
  `fleet = max(max(1, ceil(operating * 1.15)), 1 if route_type == 'Regional_District' else 2)`
- **Denominator / Universe**: 186 active routes (156 non-SSCL routes in self-test; 30 SSCL routes fixed to empirical Chalo counts of 283 buses).
- **Source Module & File**: `analysis/common.py:96, 115`, `data/raw/Rationalised_Routes_Kashmir_v3.csv`.
- **Caveats**: SSCL e-bus routes are excluded from formula self-test because their fleets are overwritten with empirical deployment data. Meets the MoHUA Service Level Benchmark (40–60 buses/lakh served).
- **Manuscript Placement**: Abstract, §3.1, §5.4.

---

## 4. Prohibited Legacy Metrics (Audit & Release Enforcement)

The following historical, superseded, or erroneous metrics appeared in preliminary consultancy drafts or early code prototypes. Their inclusion anywhere in the final manuscript or release artifacts constitutes a critical QA failure.

| Prohibited Legacy Term / Metric | Historical Origin | Why It Is Erroneous / Prohibited | Correct Replacement Metric |
|---|---|---|---|
| **"342 permits"** | Early intermediate audit filter | Counted only a subset of geocoded permits, omitting regional routes | Exactly **614 permit records** (`[CL-01]`) |
| **"207 routes"** | Engine v3.3.6 output | Included unmerged duplicate trunks and pre-reconciliation routes | Exactly **186 active routes** (`[CL-06]`) |
| **"39% route reduction"** | Early draft calculation | Conflated administrative permits with physical corridors | **99.4% corridor retention** (`[CL-08]`); 71.0 pp change-of-unit (`[CL-07]`) |
| **"95.7% coverage"** | Pre-v3.3.8 metric | Used legacy Srinagar Urban Agglomeration denominator (~1.66M) | **24.2% network coverage** of 6.58M division population (`[CL-28]`) |
| **"1,009 buses"** | Engine v3.3.7 headline | Pre-dated v3.4.5 measured GPS cycle-time re-anchoring | Exactly **1,011 buses** (`[CL-36]`) |
| **"Srinagar Metropolitan City"** | Early municipal scope | Geographic scope error; study encompasses entire 10-district division | **Kashmir Division (10 districts)** |
| **"Validated against ridership"** | Erroneous draft phrasing | Driver GPS measures vehicle speed and geometry, carrying zero ridership signal | **"Supply-side observational GPS validation"** |
| **"Engine v4"** | Speculative future version | The operational research baseline is frozen at `v3.4.5-geo` | **Transit engine v3.4.5-geo** |

---

## 5. Parameter Sweeps and Uncertainty Framework

The 11 predeclared engine parameters swept in one-at-a-time (OAT) sensitivity analyses (`analysis/a08_sensitivity_oat.py`) and sampled across 5,000 Monte Carlo draws (`analysis/a09_monte_carlo_sobol.py`) are registered below:

| Parameter Key | Baseline Value | Swept Range | Marginal Prior Distribution | Operational Description |
|---|---|---|---|---|
| `WALK_CATCHMENT_M` | 400.0 m | [300.0, 800.0] | Triangular (mode: 400.0) | Maximum pedestrian walking catchment radius |
| `VIRTUAL_STOP_SPACING_M` | 250.0 m | [150.0, 400.0] | Uniform | Alignment sampling interval for catchment generation |
| `STOP_SPACING_M` | 500.0 m | [300.0, 800.0] | Uniform | Assumed stop spacing used in dwell penalty modeling |
| `CDI_POP_WEIGHT` | 0.50 | [0.20, 0.80] | Uniform | Weight assigned to resident population in composite demand |
| `POI_TIER2_WEIGHT` | 0.40 | [0.20, 0.60] | Triangular (mode: 0.40) | Weight assigned to Medium Priority commercial POIs |
| `POI_TIER3_WEIGHT` | 0.60 | [0.30, 0.90] | Triangular (mode: 0.60) | Weight assigned to Seasonal / Tourist POIs |
| `TOURIST_POPULATION_MULTIPLIER` | 1.30 | [1.00, 1.80] | Triangular (mode: 1.30) | Headcount boost factor on designated tourist corridors |
| `OVERLAP_THRESHOLD` | 0.65 | [0.50, 0.90] | Uniform | Pairwise spatial overlap threshold $\theta$ for consolidation |
| `CONGESTION_CITY_CORE` | 2.20 | [1.60, 2.80] | Triangular (mode: 2.20) | Free-flow OSRM speed division factor in urban core |
| `STOP_PENALTY_MIN` | 0.50 min | [0.30, 1.50] | Triangular (mode: 0.50) | Dwell penalty per assumed stop |
| `FLEET_SPARE_RATIO` | 1.15 | [1.05, 1.25] | Triangular (mode: 1.15) | Maintenance and reserve fleet buffer multiplier |

---

## 6. Multi-Channel Validation Architecture (Table 7)

| Channel | Validation Target | Benchmark / Evidence Source | Test Statistic / Metric | Success Threshold | Empirical Result | Status |
|---|---|---|---|---|---|---|
| **V1** | Spatial cross-validation (partly circular) | Microsoft ML building footprints (1.85 M); OSM (12,343) | Spearman $\rho$, route and 1-km grid | $\rho > 0.60$ | Microsoft: 0.975 route, 0.950 grid — pass; OSM: 0.657 route, 0.312 grid (mapping gap) `[CL-53]` | Executed (`v01`); **pass** on the complete footprint layer |
| **V2** | Benchmark consistency (circular) | CHALO 98 buses, 12-month trips | Plan SSCL fleet / CHALO scaled to 15 min | Ratio within $\pm 15\%$ | 1.29–1.58 at a 13–16 h service day; route rank $\rho$ 0.22 `[CL-54]` | Executed (`v02`); **fail** |
| **V3** | Delphi / AHP expert survey | Independent expert panel | Panel consensus Kendall $W$ | $W > 0.70$ | Pending elicitation | Forward work (§6.4); weights meanwhile equal/entropy/PCA |
| **V4** | Supply-side GPS validation | Driver-GPS trace logs (43,809 runs) | MAPE on runtime & pace; rank corr | MAPE $< 20\%$, $\rho > 0.50$ | Moving speed passes (+1.4%); Dwell fails (61.6% MAPE) | Established (`v04`) |
| **V5** | Sobol' global sensitivity | 15,360 Saltelli evaluations | First- and total-order indices | Bootstrap 95% CI | Fleet B driven by spare ratio (0.55) and observed pace (0.45 combined); tiers by population weight (0.93) `[CL-58]` | Executed (`a09`) |
| **V6** | Decision robustness | 5,000 Monte Carlo draws with GPS pace prior | Fleet 90% interval; tier stability | Stability $> 80\%$ | Fleet 989–1,058 (as specified) / 1,130–1,266 (observed pace); tier agreement 97.8%, 96.2% of routes stable `[CL-56, CL-57]` | Executed (`a09`); tiers pass, fleet interval excludes 1,011 at observed pace |
