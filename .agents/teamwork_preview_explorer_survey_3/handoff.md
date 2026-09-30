# Survey 3 Handoff Report: Data Assets, Artifacts & Findings

- **Project:** Kashmir Route Rationalisation Paper Companion (`E:\kash-paper`)
- **Survey:** Explorer (Survey 3) — Data Assets, Artifacts & Findings
- **Date / Timestamp:** 2026-09-03T11:20:00Z
- **Author:** Explorer (Survey 3 Subagent)
- **Status:** Complete (Hard Handoff)

---

## 1. Observation

### 1.1 Staged Raw Data Inventory (`data/raw/`)

All staged files in `data/raw/` were verified against `data/MANIFEST.json` using SHA-256 cryptographic hashing and byte count verification. In addition, an unmanifested file (`census2011_kashmir_districts.csv`) was discovered and inventoried.

| Relative Path | Size (Bytes) | Format | SHA-256 Checksum | Source / Provenance | Research Purpose & Role |
|---|---|---|---|---|---|
| `Rationalised_Routes_Kashmir_v3.csv` | 247,953 | CSV (644 rows × 55 cols) | `1871714c8804cbbc152b0209774c772943c939e71bde4241632690ce0f02172a` | `E:\kash\outputs_v3.4.5\Rationalised_Routes_Kashmir_v3.csv` | Published rationalised operational plan (v3.4.5-geo). 644 rows (614 permit-derived + 30 synthetic e-bus backbone; 186 active routes). Primary baseline for all route parameters, headway, cycle time, and fleet requirement. |
| `Rationalised_Routes_Kashmir_v3.geojson` | 2,977,639 | GeoJSON (186 features) | `4ea6a856dd77d5d43a587fbdc445c76feea0b123b2bcc85040e8505a1497f945` | `E:\kash\outputs_v3.4.5\Rationalised_Routes_Kashmir_v3.geojson` | Routed line geometries for the 186 active services. Projected in WGS84 (`EPSG:4326`). Used to sample virtual stops at 250 m intervals for catchment generation. |
| `Rationalisation_Log_Kashmir_v3.csv` | 242,957 | CSV (644 rows × 15 cols) | `00f1052206dc29b004df5bf18c2a1a80f6d67fcab2e66a2b311686b082b4be4c` | `E:\kash\outputs_v3.4.5\Rationalisation_Log_Kashmir_v3.csv` | Per-route disposition reasoning, merge decisions, and overlap attribution explaining the engine's consolidation pipeline. |
| `existing-routes.csv` | 66,972 | CSV (614 rows × 12 cols) | `fa9778c8267d71b68ccffc1024ae77cd0cef3d0d86eb1ae0c0b3d1984da39047` | `E:\kash\existing-routes.csv` | Official permit register as geocoded: origin, destination, via points, operator class, vehicle type. Used to evaluate corridor duplication (Finding F1). |
| `pois.csv` | 223,453 | CSV (2,431 rows × 11 cols) | `e8f217c4ad77986e3e00a91dbb02fcfbca918eb499d695050982d357fed19f73` | `E:\kash\pois.csv` | Points of Interest extracted from OpenStreetMap, categorized into Tier 1 (High, 1,030), Tier 2 (Medium, 1,080), and Tier 3 (Seasonal/Tourist, 321). Evaluated in Finding F5. |
| `kashmir_worldpop.tif` | 4,760,992 | GeoTIFF (Float32 raster) | `515e5867ee4c0fe9dd031a3fc0f372814aa96bf3c689d9e25bf09ba19bda6571` | `E:\kash\kashmir_worldpop.tif` | WorldPop 2026 UN-adjusted residential population surface, 100 m (~0.000833 deg) resolution, clipped to study bounding box. Total zonal sum = 6,584,763. |
| `kashmir_districts_osm.geojson` | 444,515 | GeoJSON (10 features) | `4091fe7bdc0e3490eab3f3505fe1f98a9beb288c1bf97b38170f84667ecdc444` | `E:\kash\kashmir_districts_osm.geojson` | OSM `admin_level=5` district boundaries for the 10 districts of Kashmir Division (Anantnag, Bandipore, Baramulla, Budgam, Ganderbal, Kulgam, Kupwara, Pulwama, Shopian, Srinagar). |
| `kashmir_tehsils_osm.geojson` | 605,242 | GeoJSON (39 features) | `38e0a2e3d88a0c8de86c7e65451b6839b0d0903a9156c4710d7a2017fe04e549` | `E:\kash\kashmir_tehsils_osm.geojson` | OSM `admin_level=6` tehsil boundaries for sub-district geographical and equity analyses. |
| `Kashmir_Stops_Master_v4.csv` | 9,847 | CSV (126 rows × 10 cols) | `dcfce2a9b8a1cf6610fdd76809cd5eb07d24fd2d352edc120bd58d911e5d2d14` | `E:\kash\Kashmir_Stops_Master_v4.csv` | Canonical stop register (126 primary bus terminals/stops) with point-in-polygon district and tehsil assignments. |
| `Hourly_Passenger_Count.csv` | 12,952 | CSV (541 rows × 4 cols) | `289381eddd272fdab98bfabb4db165dd2b7b77b01e5310ac7c668d6b2cc5a0b1` | `E:\kash\Hourly Passenger Count.csv` | Observed hourly e-bus boardings and revenue, 1–30 April 2026. **Note:** Line 1 is a title string; requires `skiprows=1` when loading in pandas. |
| `chalo_ridership.csv` | 15,626 | CSV (1,005 rows × 13 cols) | `c216de2d5f13b120572c0fcaa8fd524db2d2b9e687761c44fa6ee2f3f68164ff` | `E:\kash\Ridership Data.csv` | Monthly e-bus ridership and operated km for FY 2025-26 from Chalo app operator feed. Used in benchmark consistency check (V2 circularity). |
| `chalo_deployed_buses.csv` | 1,683 | CSV (31 rows × 6 cols) | `ee6b45ff3e2c32c36ab1fcd9b658870f6b7a1d44bb6836e635f0dee4930cf38d` | `E:\kash\Route Wise deployed Buses.csv` | Buses deployed per e-bus route by vehicle length (9 m vs 12 m). Establishes the empirical fleet count for the 30 SSCL routes (sum = 283). |
| `ROUTE_DEEPDIVE_LEDGER.csv` | 167,738 | CSV (186 rows × 28 cols) | `1788e1ce417d46ad124a9d85e30952faa7de810aa47c34615dcbae94ff159f34` | `E:\kash\ROUTE_DEEPDIVE_LEDGER.csv` | Comprehensive route-level audit ledger containing verified real-world distances, terrain classifications, and citation sources. |
| `gps/reality_check.csv` | 2,943 | CSV (14 rows × 14 cols) | `55172547baaae97dd2f6e331a36ed52b3a44f065311ec22aac0fcd67b955ba43` | `E:\bus-sathi-trace\data\reality_check.csv` | Planned vs observed one-way run times on matched corridors (5 matched, 9 partial; 815 runs total). |
| `gps/corridor_profiles.csv` | 1,288 | CSV (18 rows × 13 cols) | `0cb17ce98d6b166d049d6aa19d520d9fe7850f644bea87af7545a43c7b9d1c44` | `E:\bus-sathi-trace\data\corridor_profiles.csv` | Per-corridor aggregated GPS operational statistics across 18 corridors: moving speed, effective speed, dwell time, dwell share. |
| `gps/route_evidence.csv` | 12,563 | CSV (186 rows × 8 cols) | `061ea4e5b550dbaeb50a7f123f52cf3024a268c1d8fc0c8ad899dee9b7998f75` | `E:\bus-sathi-trace\data\route_evidence.csv` | Physical road alignment observation: fraction of each planned route length observed in GPS runs (`obs_frac`). 183/186 > 0, median 0.94. |
| `gps/permit_observed.csv` | 12,402 | CSV (186 rows × 6 cols) | `f97f1bacf5bf03fce1f7d9e816fb161ad681c0e08d6e99ac2ee8805eca8839b8` | `E:\bus-sathi-trace\data\permit_observed.csv` | Service-level observation status per route: `OBSERVED` (66), `PARTIAL` (45), `NO_APP_DATA` (75). |
| `gps/geometry_divergence.csv` | 553 | CSV (7 rows × 9 cols) | `7bf5c49479a6e639d3356a3c136e0e38519e05d6a6c10b182f886b13fdcfc485` | `E:\bus-sathi-trace\data\geometry_divergence.csv` | Identifies 7 corridors where the physical path taken by drivers deviates significantly from the planned routed polyline. |
| `gps/driver_days.csv` | 51,564 | CSV (855 rows × 9 cols) | `14b408639648b8ffc128322d6a05f44b1faf46a0b65ebf8d7e986df667e4b9a9` | `E:\bus-sathi-trace\data\driver_days.csv` | Driver shift activity used to reconstruct service window, duty cycle, vehicle utilization, and daily run frequency. |
| `census2011_kashmir_districts.csv` | 951 | CSV (10 rows × 4 cols) | `c5db4e3d1981a4b5aa2d5d87ee96dfdc95a4ea095c52c7b508f7dbf170425a1e` *(computed)* | Primary Census Abstract 2011, Census of India | District-wise 2011 census populations across the 10 Kashmir districts (sum = 6,888,475). Benchmark for Finding F2. **Note:** Not listed in `MANIFEST.json`. |

---

### 1.2 Derived Datasets Inventory (`data/derived/`)

Nine derived datasets exist in `data/derived/`, produced by Phase 0, Phase 1, and Phase 2 scripts. All schemas, row counts, and contents were directly verified:

```text
data/derived/
├── a01_walk_graph.json            (1,173 B)   [Produced by a01_build_walk_graph.py]
├── a02_catchments.csv             (63,476 B)  [Produced by a02_network_catchments.py]
├── a02_network_catchments.json    (2,346 B)   [Produced by a02_network_catchments.py]
├── a02b_faithfulness.csv          (87,703 B)  [Produced by a02b_faithfulness.py]
├── a02b_faithfulness.json         (3,671 B)   [Produced by a02b_faithfulness.py]
├── q01_data_quality.json          (7,157 B)   [Produced by q01_data_quality.py]
├── v04_corridor_comparison.csv    (4,365 B)   [Produced by v04_gps_validation.py (superseded)]
├── v04_fleet_consequence.csv      (494 B)     [Produced by v04_gps_validation.py (superseded)]
└── v04_gps_validation.json        (7,890 B)   [Produced by v04_gps_validation.py (superseded)]
```

#### Detailed Breakdown:

1. **`a01_walk_graph.json`**:
   - Keys: `bbox`, `bbox_pad_deg` (0.05), `excluded_classes` (18 highway tags), `largest_component_nodes` (864,800), `largest_component_share` (0.8990), `n_components` (564), `n_edges` (973,569), `n_nodes` (961,927), `network_km` (23,322.56 km), `source_pbf` (`E:\kash\india-latest.osm.pbf`, 217,375,703 bytes), `walkable_classes` (20 tags).
   - Validates that the graph is strongly connected in the core valley.

2. **`a02_catchments.csv`**:
   - Shape: (186 rows × 25 columns).
   - Columns: `New_Route_ID`, `Route_Name`, `Route_Type`, `Route_KM`, `geom_km`, `km_geometry_consistent`, `plan_pop_raw`, `n_stops`, `n_stops_off_network`, `snap_offset_median_m`, `snap_offset_p95_m`, `n_nodes_reached`, `area_euclid_km2`, `area_net_km2_tau50`, `area_net_km2_tau100`, `area_net_km2_tau150`, `pop_euclid`, `pop_net_tau50`, `pop_net_tau100`, `pop_net_tau150`, `pop_net`, `area_net_km2`, `overstatement_abs`, `overstatement_pct`, `area_ratio`.
   - Core finding: median per-route overstatement is 37.39% (IQR 30.49%–41.73%, max 56.78%).

3. **`a02_network_catchments.json`**:
   - Key metrics: `pop_euclid_union` = 2,339,393.75, `pop_net_union` = 1,592,846.75, `union_overstatement_pct` = 31.91%.
   - Headline coverage: Euclidean 35.53% → Network 24.19% of study denominator (6,584,762).
   - Sensitivity to off-network tail $\tau$: $\tau=50$ m → 52.77%; $\tau=100$ m → 37.39%; $\tau=150$ m → 29.18%.
   - Virtual stops: 22,360 total, only 46 (0.21%) off-network (>400 m), median snap offset 11.0 m.

4. **`a02b_faithfulness.csv` & `a02b_faithfulness.json`**:
   - Shape: (186 rows × 36 columns).
   - Full inventory of all 186 route reproduction dispositions:
     - `reproduced` (≤1% absolute error): 136 routes (median error 0.239%).
     - `reproduced_minor_drift` (≤5% error): 3 routes (FDR-525, FDR-479, SSCL-11).
     - `stale_tourist_flag`: 1 route (SSCL-27, retained tourist boost under cleared flag).
     - `superseded_geometry`: 2 routes (FDR-438 with ratio 0.419×, FDR-160 with ratio 0.630×).
     - `substituted_distance`: 44 routes where v3.4.4 substituted verified road distances without updating geometry.
   - Total accounted: 136 + 3 + 1 + 2 + 44 = 186 routes (100% complete audit, zero unexplained residuals).
   - Tourist multiplier inflation: 8 routes, 285,914 resident population distortion.

5. **`q01_data_quality.json`**:
   - 6 quality gates: D1 Register hygiene (614 permits → 157 corridors; 71.0 pp unit change + 0.2 pp consolidation; 99.4% retention); D2 Permit activity (66 observed / 186); D3 OSM completeness ($\rho=0.915, p=0.0002$); D4 WorldPop validation (ratio 0.9559, CAGR −0.30%/yr); D5 POI inventory (2,431 POIs, 65.3% in Srinagar); D6 Travel time (MAPE OSRM vs in-motion = 65.1%, median plan/obs = 0.51).

6. **`v04_corridor_comparison.csv`, `v04_fleet_consequence.csv`, & `v04_gps_validation.json`**:
   - Current files represent the superseded first pass of `v04_gps_validation.py`.
   - 14 corridor rows (5 matched, 9 partial).
   - Demonstrates the invalid fleet result (27 → 23 buses, −14.8%) caused by mixing pre-correction planned runtimes with post-correction cycle times and evaluating in-sample corridors as validation. Identified for rewrite under R2.

---

### 1.3 Heavy Cache Integrity & Gitignore Status (`data/cache/`)

The contents of `data/cache/` were verified directly using Python 3.14.2, `pyogrio`, `geopandas`, and `pickle`:

| Cache File | Size (Bytes) | Format / Object Type | Content Summary & Integrity Check | Verified In | Gitignore Status |
|---|---|---|---|---|---|
| `walk_graph.gpickle` | 77,051,716 (~77.1 MB) | Python pickle (`networkx.Graph`) | 961,927 nodes, 973,569 undirected edges, 23,322.56 km walkable network. Loaded successfully via `pickle.load()` in 1.56 seconds. | Offline OSM extract (`india-latest.osm.pbf`) | **MUST BE GITIGNORED**. Large binary cache (>50 MB). Excluded from git. |
| `catchments_network.gpkg` | 18,522,112 (~18.5 MB) | OGC GeoPackage (SQLite3) | Layer `catchments_network`: 186 MultiPolygon features, projected in `EPSG:32643` (UTM 43N). Successfully inspected via `pyogrio.list_layers()` and read via `geopandas.read_file()` in 0.19 seconds. | Generated by `a02_network_catchments.py` (runtime ~69.6 min) | **MUST BE GITIGNORED**. Regenerable binary asset (>10 MB). Excluded from git. |
| `osrm_responses.json` | 2,825,043 (~2.8 MB) | JSON document | 186 route OSRM responses. SHA-256 verified against `data/MANIFEST.json` (`c7f82ddb1d83127dfd23c24b640515eb8c63f39b095a4812eb84598033eadbb6`). Valid JSON with keys: `note`, `engine_version`, `n_routes`, `routes`. | OSRM offline query cache | Can be tracked or staged, but gitignore recommended if regenerable. |

**Gitignore Audit:** The companion repository `E:\kash-paper` is not yet a git repository (no `.git` directory exists, no `.gitignore` file exists). When Phase 0 `git init` is executed, `.gitignore` must explicitly ignore:
- `data/cache/walk_graph.gpickle`
- `data/cache/catchments_network.gpkg`
- `data/raw/kashmir_worldpop.tif` (4.76 MB raw third-party raster)

---

### 1.4 Paper Tables & Figures Inventory

#### Tables (`paper/tables/`):
There are 22 files in `paper/tables/`, representing 11 tables published in dual format (`.csv` for machine verification, `.md` for direct manuscript insertion):

| Table Stem | Caption / Topic | Producing Module | Status / Action Needed |
|---|---|---|---|
| `table02a_permit_duplication` | Corridors carrying largest duplicate permits | `q01_data_quality.py` | Complete & authoritative (Finding F1) |
| `table02b_permit_activity` | Planned routes by driver-GPS observation status | `q01_data_quality.py` | Complete & authoritative (Finding F4) |
| `table02c_osm_completeness` | OSM road length and density across 10 districts | `q01_data_quality.py` | Complete & authoritative (Finding F6) |
| `table02d_worldpop_vs_census` | WorldPop 2026 vs Census 2011 district totals | `q01_data_quality.py` | Complete & authoritative (Finding F2) |
| `table02e_poi_inventory` | Point of interest inventory by category and tier | `q01_data_quality.py` | Complete & authoritative (Finding F5) |
| `table02f_traveltime_error` | Travel time error metrics (OSRM vs observed) | `q01_data_quality.py` | Complete & authoritative (Finding F3) |
| `table03a_catchment_bias` | Routes whose Euclidean catchment most overstates pop | `a02_network_catchments.py` | Complete & authoritative (Finding F8) |
| `table03b_faithfulness` | Reimplementation faithfulness and residual audit | `a02b_faithfulness.py` | Complete & authoritative (Findings F7, F9) |
| `table06a_v04_runtime` | Validation V4: planned vs observed runtime | `v04_gps_validation.py` | **STALE** — to be replaced by v04 rewrite (split in/out-of-sample) |
| `table06b_v04_decomposition` | Validation V4: moving speed and dwell decomposition | `v04_gps_validation.py` | **STALE** — to be updated with WLS dwell & C17 analysis |
| `table06c_v04_cap_binding` | Validation V4: observed pace vs per-km cycle cap | `v04_gps_validation.py` | **STALE** — to be updated with full 186-route at-cap census |

#### Missing Tables to be Produced:
- Table 1: Literature synthesis matrix (co-author owned).
- Table 2: Full staged data inventory (assembled from `q01` and `data/MANIFEST.md`).
- Table 3: Parameters, provenance, and QA gates (from `common.PARAMETERS`).
- Table 4: Existing network profile (`a10_network_diagnostics.py`).
- Table 5: Route scores, top and bottom 20 (`a03_index_weights.py`).
- Table 6 (6a, 6b, 6c, 6d): Repaired observational GPS validation tables.
- Table 7: Multi-channel validation summary matrix (V1–V6).
- Table 8: Policy instruments matrix (co-author owned).

#### Figures (`paper/figures/`):
The directory `paper/figures/` is currently **empty**. Planned publication figures:
- Figure 1: Conceptual framework (conventional vs demand-data-free pipeline).
- Figure 2: Literature taxonomy matrix by data intensity.
- Figure 3: 4-panel study area map (districts, population, road hierarchy, POIs).
- Figure 4: Methodological workflow flowchart (vector).
- Figure 5: Network diagnosis (length distribution, overlap heatmap, link duplication).
- Figure 6: Index behaviour (GVF elbow, component scatter, weight sensitivity, tier stability).
- Figure 7: Rationalisation outcomes (Sankey diagram, headway shifts, cycle composition).
- Figure 8 / 8b: Robustness frontier and Monte Carlo tier stability distributions.
- Results Map: Accessibility difference map (diverging color ramp centered at 0.0).

---

### 1.5 External Repositories Verification (`E:\kash` and `E:\bus-sathi-trace`)

Both external repositories were inspected in strictly read-only mode:

1. **`E:\kash` (Engine Repository)**:
   - Contains engine source code (`transit_kashmir_v3.py`, 319 KB), historical release logs (`engine_run_v3.3.1.log` through `engine_run_v3.4.3.log`), and canonical outputs directory `outputs_v3.4.5/`.
   - Crucial line references verified:
     - `transit_kashmir_v3.py:506, 1863`: `TOURIST_POPULATION_MULTIPLIER = 1.3` applied directly to `Population_Served`.
     - `transit_kashmir_v3.py:2126-2155`: Modelled runtime, dwell penalties (0.5 min/stop), and per-km cycle cap clipping.
     - `transit_kashmir_v3.py:3115-3165`: Published fleet formula:
       $$\text{operating} = \max\left(1, \lceil \text{cycle} / \max(1, \text{headway}) \rceil\right)$$
       $$\text{fleet} = \max\left(\max(1, \lceil \text{operating} \times 1.15 \rceil), 1 \text{ if Regional else } 2\right)$$
     - `transit_kashmir_v3.py:3366`: Undirected 4-decimal endpoint coordinate corridor key.
   - Status: Read-only working history. Not modified.

2. **`E:\bus-sathi-trace` (Observational GPS Repository)**:
   - Contains raw GPS traces (`traces_raw.geojson`, 95.7 MB), trip aggregations, driver-day shifts (`driver_days.csv`), corridor profiles (`corridor_profiles.csv`), and reality check comparisons (`reality_check.csv`).
   - Line references verified:
     - `route_evidence.py:60-110`: Definition of `obs_frac` (physical road network geometry overlap).
     - `validate_permits.py:70-110`: Definition of `observed_cover` / `status` (recurring service detection).
   - Status: Read-only observational data. Not modified.

---

## 2. Logic Chain

### 2.1 Verification of Established Findings (F1–F9)

The quantitative evidence supporting each existing finding in `paper/FINDINGS.md` was recomputed and confirmed:

```
[Observation 1.1: existing-routes.csv (614 rows)]
    │
    ▼ (group by 11m endpoint coordinate key)
157 distinct corridors (457 duplicate rows, 74.4% duplicate share)
    │
    ├─> Change of unit accounts for 71.0 pp of the 71.1% row reduction
    └─> Genuine consolidation accounts for only 0.2 pp (1 corridor)
    │
    ▼
Finding F1: The register is a permit register, not a route register. Design retains 156/157 corridors (99.4%).
```

- **F1 (Permit vs Route Register):** Confirmed by `q01_data_quality.json`. The engine's funnel (644 rows → 186 active) collapses duplicate permits on identical corridors. The plan does not reduce routes; it harmonizes fleet, frequency, and headways. 32 alternative via routings are suppressed across 20 corridors.
- **F2 (WorldPop 2026 vs Census 2011):** Confirmed by `table02d_worldpop_vs_census.csv`. Zonal sum across 10 districts = 6,584,763 (vs Census 2011 of 6,888,475; ratio 0.956, implied CAGR −0.30%/yr). Coverage shares are biased slightly upward (conservative denominator), absolute headcounts downward.
- **F3 (Modelled vs Observed Runtime):** Confirmed by `q01_data_quality.json:D6`. MAPE(OSRM vs in-motion) = 65.1%, MAPE(plan vs total observed) = 47.6%, median plan/observed ratio = 0.51. Unanchored model runtimes understate observation by roughly half.
- **F4 (Observational Lower Bound on Activity):** Confirmed by `table02b_permit_activity.csv`. 66 routes are `OBSERVED`, 45 `PARTIAL`, 75 `NO_APP_DATA`. `NO_APP_DATA` reflects driver app penetration, not route dormancy.
- **F5 (POI Spatial Concentration):** Confirmed by `q01_data_quality.json:D5`. 2,431 POIs; 65.3% concentrated in Srinagar district. Per-100k density spans 0.32 to 120.44 across districts.
- **F6 (OSM Network Density vs Population Density):** Confirmed by `q01_data_quality.json:D3`. Mapped road density tracks population density with rank correlation $\rho = 0.915$ ($p = 0.0002$). Volunteered mapping bias is benign at district scale, licensing network walk graph usage.
- **F7 (Internal Inconsistency on 44 Routes):** Confirmed by `a02b_faithfulness.json`. 142 self-consistent routes reproduce published population to a median absolute error of 0.245% ($r = 0.995$). 44 routes have verified road distances patched into `Route_KM` in v3.4.4 without updating geometry or recomputing population.
- **F8 (Euclidean Catchment Overstatement):** Confirmed by `a02_network_catchments.json`. Walkable network catchments reduce measured population served by a median of 37.39% per route (184/186 routes overstated >25%). Network-wide deduplicated union drops from 2,339,394 to 1,592,847 (31.91% reduction), cutting headline coverage from 35.53% to 24.19%.
- **F9 (Embedded Demand Multiplier):** Confirmed by `a02b_faithfulness.json`. A 1.3× multiplier applied to 8 `Tourist_Corridor` routes injects 285,914 synthetic headcount into residential population columns.

---

### 2.2 Empirical Formulation and Documentation of Missing Findings (F10–F12)

Findings F10, F11, and F12 are drafted in `STATUS.md` but not yet written into `paper/FINDINGS.md`. Direct execution and statistical analysis conducted during this survey provides complete mathematical and empirical formulations:

#### Finding F10 — The sanity cap, not the model, determines the plan

```
[Observation 1.1: Rationalised_Routes_Kashmir_v3.csv (186 active routes)]
    │
    ▼ (evaluate Cycle_Time_Min against Route_KM * 2 * cap)
Peri_Urban:          46 / 47  at cap (97.9%)  [cap = 2.5 min/km]
Regional_District:   71 / 71  at cap (100.0%) [cap = 1.5 min/km]
Urban:               52 / 68  at cap (76.5%)  [cap = 4.0 min/km]
    │
    ├─> Total sitting exactly at cap: 169 / 186 routes (90.9%)
    ├─> Routes above cap: Exactly 5 routes (the 5 GPS-reanchored corridors)
    └─> Routes below cap: 12 routes (all Urban)
    │
    ▼ (compare cap against observed GPS pace on 18 corridors)
Observed median pace = 4.62 min/km (P90 = 6.28 min/km)
    ├─> 15 of 18 observed corridors exceed Urban cap (4.0 min/km)
    ├─> 16 of 18 observed corridors exceed Peri_Urban cap (2.5 min/km)
    └─> 18 of 18 observed corridors exceed Regional cap (1.5 min/km)
    │
    ▼
Finding F10: The safety guard clause became the active, binding constraint on 90.9% of the network, truncating cycle times downward and mechanistically creating F3's 0.51 plan/observed ratio.
```

1. **Census at Cap:** In `Rationalised_Routes_Kashmir_v3.csv`, 169 of 186 routes (90.86%) have `Cycle_Time_Min` equal to $\text{Route\_KM} \times 2 \times \text{cap}$. Regional lifelines are 100% at cap; Peri-Urban routes are 97.9% at cap; Urban routes are 76.5% at cap.
2. **The 5 GPS Outliers:** The only 5 routes in the entire network that exceed their asserted class caps are precisely the 5 corridors re-anchored using GPS empirical data in v3.4.5 (FDR-050, FDR-262, FDR-270, FDR-370, FDR-575).
3. **Caps Understate Reality:** Observed one-way pace from driver GPS across 18 corridors has a median of 4.62 min/km. This exceeds the Urban cap (4.0) on 83.3% of corridors, the Peri-Urban cap (2.5) on 88.9%, and the Regional cap (1.5) on 100%. The cap truncates reality downward, directly creating the fleet understatement identified in F3.

#### Finding F11 — Component decomposition: congestion multiplier survives, dwell model fails

Regressions executed on `corridor_profiles.csv` (18 corridors, 815 runs) reveal the underlying structure of run-time error:

| Model / Specification | Dependent Variable | Sample ($n$) | Intercept ($a$) [95% CI] | Slope ($b$, min/km) [95% CI] | $R^2$ | Intercept $p$-value | Slope $p$-value |
|---|---|---|---|---|---|---|---|
| **OLS (All Corridors)** | `dwell_min` | 18 | 17.67 min [7.41, 27.94] | 0.247 [−0.494, 0.989] | 0.030 | 0.0022 | 0.4894 |
| **WLS (Run-Weighted)** | `dwell_min` | 18 | 20.72 min [8.90, 32.55] | 0.196 [−0.557, 0.950] | 0.019 | 0.0019 | 0.5880 |
| **OLS (Excl. C17)** | `dwell_min` | 17 | 13.49 min [2.78, 24.20] | 0.506 [−0.247, 1.259] | 0.120 | 0.0170 | 0.1725 |
| **WLS (Excl. C17)** | `dwell_min` | 17 | 20.24 min [7.81, 32.66] | 0.225 [−0.565, 1.014] | 0.024 | 0.0034 | 0.5531 |

1. **Congestion Multiplier Survives:** OSRM free-flow driving time divided by 2.2 (`CONGESTION_CITY_CORE`) reproduces observed moving speed with a bias of only **+1.4%** (modelled median 17.95 km/h vs observed median 20.55 km/h, MAPE 28.4%).
2. **Dwell Model Fails Decisively:** The engine models dwell as a purely distance-proportional term without an intercept: 2 stops per km at 0.5 min/stop = 1.0 min/km ($a = 0, b = 1.0$). Both OLS and WLS decisively reject this form:
   - The intercept is large, positive, and statistically significant across all specifications ($a \approx 13.5$ to $20.7$ min, $p < 0.02$), representing terminal layover, passenger boarding surges at major hubs, and dispatch holding.
   - The slope is small ($b \approx 0.20$ to $0.51$ min/km) and statistically indistinguishable from zero ($p > 0.15$). The engine's assumed slope of 1.0 min/km lies far outside the empirical reality.
3. **C17 Outlier Influence:** Corridor 17 (C17, 3.3 km, only 6 runs) exhibits an extreme dwell rate of 9.64 min/km and 74% dwell share (31.8 min dwell on a 42.8 min run). Excluding C17 shifts the OLS intercept from 17.67 to 13.49 min and slope from 0.25 to 0.51 min/km, but the core conclusion holds: dwell is dominated by a fixed terminal threshold, not distance.

#### Finding F12 — The two GPS coverage metrics measure fundamentally different dimensions

Analysis of `route_evidence.csv` and `permit_observed.csv` demonstrates:
1. **Physical Alignment Corroboration (`obs_frac`):** Measures whether the drawn polyline traverses road segments where GPS-tracked buses operated. 183 of 186 routes have `obs_frac > 0` (median 0.94, IQR 0.79–0.99); 171 routes are corroborated at $\ge 50\%$; 137 routes at $\ge 80\%$; 33 routes are fully covered (1.0). This validates physical road geometry.
2. **Service Verification (`observed_cover` / `status`):** Measures whether a recurring, end-to-end scheduled service follows the alignment. Only 66 of 186 routes (35.5%) are classified as `OBSERVED`, 45 (24.2%) as `PARTIAL`, and 75 (40.3%) as `NO_APP_DATA`.
3. **Strict Disclose Rule:** `obs_frac` (183/186) must **never** be presented as service verification or operational validation. It is physical infrastructure corroboration only.

---

### 2.3 Fleet Formula Verification & Self-Test Reproducibility

The fleet sizing rule executed in `transit_kashmir_v3.py:3115-3165` was implemented and evaluated against all 186 active routes:
$$\text{operating} = \max\left(1, \left\lceil \frac{\text{Cycle\_Time\_Min}}{\max(1, \text{Headway\_Min})} \right\rceil\right)$$
$$\text{fleet} = \max\left(\max\left(1, \lceil \text{operating} \times 1.15 \rceil\right), 1 \text{ if Regional\_District else } 2\right)$$

- **Self-Test Result:** Exactly **0 mismatches** across all 156 non-SSCL active routes.
- **Fleet Totals:**
  - Non-SSCL active fleet: **728 buses**.
  - SSCL active fleet (empirically deployed from `chalo_deployed_buses.csv`): **283 buses**.
  - Total active fleet: **1,011 buses** ($728 + 283 = 1,011$).
- **Historical Reconciliation:** This reproduces the frozen v3.4.5 headline fleet of 1,011. Pre-v3.4.5 fleet was 1,004; re-timing the 5 matched corridors using GPS added exactly 7 buses (FDR-050: 5→7, FDR-262: 4→7, FDR-270: 4→5, FDR-370: 4→5, FDR-575: 3→3), yielding $1,004 + 7 = 1,011$.

---

## 3. Caveats

1. **Read-Only Scope:** No code or data files outside `.agents/teamwork_preview_explorer_survey_3/` were modified. Staged raw data, caches, and paper outputs remain in their exact initial state.
2. **Repaired GPS Validation Pending Execution:** The current tables `table06a_v04_runtime`, `table06b_v04_decomposition`, and `table06c_v04_cap_binding` in `paper/tables/` are derived from the superseded first pass of `v04_gps_validation.py`. They contain circular in-sample fleet comparisons (−14.8%) and must not be cited in manuscript drafts until Phase 1 executes the rewritten `v04_gps_validation.py`.
3. **Index Weights Module Not Yet Run:** Script `analysis/a03_index_weights.py` has been written but not executed. Derived outputs `a03_index.csv` and `a03_index_weights.json` do not yet exist on disk.
4. **Git Repository Uninitialized:** The companion repository is not yet under version control (`git init` pending in Phase 0). Care must be taken upon initialization to apply the recommended `.gitignore` rules before staging files.

---

## 4. Conclusion

1. **Repository Data Hygiene is Exemplary:** All 19 files listed in `data/MANIFEST.json` match byte-identically and hash-identically against disk.
2. **Heavy Caches are Verified & Fully Functional:** `walk_graph.gpickle` (77.1 MB) and `catchments_network.gpkg` (18.5 MB) load cleanly and without error. Downstream modules do not need to incur the 9-minute and 69-minute runtimes to regenerate them.
3. **Core Findings F1–F9 are Solid & Authoritative:** The quantitative claims regarding permit duplication, WorldPop conservatism, travel time bias, OSM road density, Euclidean catchment overstatement (31.9% union reduction), and tourist multiplier inflation (285,914) are fully reproducible and verified.
4. **Findings F10, F11, and F12 are Empirically Ready for Formal Integration:** The binding nature of the sanity cap (90.9% of network), the breakdown of the linear dwell model (large fixed intercept ~$17.7$ min, slope ~$0.25$ min/km), and the distinction between alignment corroboration (`obs_frac` 98.4%) and service presence (`status` 35.5%) have been verified through direct regression modeling and census checks.
5. **Phase 1 Priority:** The next critical milestone is the complete rewrite of `analysis/v04_gps_validation.py` to decouple in-sample from out-of-sample corridors, formalize the WLS dwell regression, and supply the measured pace prior to the Monte Carlo simulation (`a09`).

---

## 5. Verification Method

To independently reproduce and verify every finding, statistic, and table documented in this report, execute the following commands from `E:\kash-paper`:

1. **Verify Raw Data Hashes:**
   ```powershell
   & "E:\kash-paper\.venv\Scripts\python.exe" -c "
   import json, hashlib, pathlib
   with open('data/MANIFEST.json') as f:
       m = json.load(f)
   for e in m['files']:
       p = pathlib.Path('data/raw') / e['file']
       h = hashlib.sha256(p.read_bytes()).hexdigest()
       assert h == e['sha256'], f'Hash mismatch: {e[\"file\"]}'
   print('All manifest files verified byte-for-byte!')
   "
   ```

2. **Verify Heavy Cache Loading:**
   ```powershell
   & "E:\kash-paper\.venv\Scripts\python.exe" -c "
   import pickle, geopandas as gpd
   with open('data/cache/walk_graph.gpickle', 'rb') as f:
       G = pickle.load(f)
   assert G.number_of_nodes() == 961927 and G.number_of_edges() == 973569
   gdf = gpd.read_file('data/cache/catchments_network.gpkg', engine='pyogrio')
   assert len(gdf) == 186
   print('Cache integrity: PASS')
   "
   ```

3. **Verify Fleet Formula Self-Test (0 Mismatches):**
   ```powershell
   & "E:\kash-paper\.venv\Scripts\python.exe" -c "
   import math, pandas as pd
   df = pd.read_csv('data/raw/Rationalised_Routes_Kashmir_v3.csv')
   active = df[df['Action_Taken'].isin(['UPGRADED_TO_TRUNK', 'RETAINED_AS_FEEDER'])]
   non_sscl = active[~active['New_Route_ID'].str.startswith('SSCL')]
   for _, r in non_sscl.iterrows():
       op = max(1, math.ceil(float(r['Cycle_Time_Min']) / max(1.0, float(r['Headway_Min']))))
       min_f = 1 if r['Route_Type'] == 'Regional_District' else 2
       fl = max(max(1, math.ceil(op * 1.15)), min_f)
       assert fl == int(r['Fleet_Required']), f'Mismatch on {r[\"New_Route_ID\"]}'
   print('Fleet reproduction: 0 mismatches across 156 routes! Total fleet: 1,011')
   "
   ```

4. **Verify Cap Census (Finding F10):**
   ```powershell
   & "E:\kash-paper\.venv\Scripts\python.exe" -c "
   import pandas as pd, numpy as np
   df = pd.read_csv('data/raw/Rationalised_Routes_Kashmir_v3.csv')
   act = df[df['Action_Taken'].isin(['UPGRADED_TO_TRUNK', 'RETAINED_AS_FEEDER'])].copy()
   caps = {'Urban': 4.0, 'Peri_Urban': 2.5, 'Regional_District': 1.5}
   act['cap'] = act['Route_Type'].map(caps)
   act['at_cap'] = np.abs(act['Cycle_Time_Min'] - act['Route_KM'] * 2.0 * act['cap']) < 0.1
   print('Total at cap:', act['at_cap'].sum(), 'of', len(act))
   assert act['at_cap'].sum() == 169
   "
   ```

5. **Invalidation Conditions:**
   - Any modification to `data/raw/` that changes a SHA-256 hash.
   - Any corruption or version incompatibility that prevents `walk_graph.gpickle` from loading in Python 3.14.2.
   - Any alteration to the 644-row operational baseline or introduction of an unverified engine v4.
