# Handoff Report: Specification Mining Survey across Phases 0 to 7

**Project:** Kashmir Bus Route Rationalisation Paper Companion (`E:\kash-paper`)  
**Target Manuscript:** *Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity* (Targeting *Transport Policy*)  
**Author/Role:** Spec Miner (Survey 1) / Teamwork Specialist  
**Working Directory:** `E:\kash-paper\.agents\teamwork_preview_spec_miner_survey_1`  
**Date/Timestamp:** 2026-09-03T11:14:00Z  

---

## 1. Observation

This specification mining investigation probed four primary authoritative documents and supporting verified analysis codebases:
1. `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` (Lines 1–94)
2. `E:\kash-paper\IMPLEMENTATION_AND_QA_PLAN.md` (Lines 1–674)
3. `E:\kash-paper\STATUS.md` (Lines 1–328)
4. `E:\kash-paper\paper\FINDINGS.md` (Lines 1–224)
5. Executable source files: `analysis/common.py` (Lines 1–299), `analysis/a03_index_weights.py` (Lines 1–150), `analysis/v04_gps_validation.py` (Lines 1–529), `analysis/a02_network_catchments.py` (Lines 1–100), `analysis/a02b_faithfulness.py` (Lines 1–100), `analysis/q01_data_quality.py` (Lines 1–100).

### 1.1 Verbatim Direct Observations from Authoritative Sources

- **Operational Baseline & Geography (`ORIGINAL_REQUEST.md:10-12`, `IMPLEMENTATION_AND_QA_PLAN.md:27-34`, `STATUS.md:18-20`):**
  > "Frozen operational baseline: Kashmir Valley v3.4.5 is the active baseline (644 rows: 614 permits + 30 SSCL routes; 186 active services; stated fleet 1,011; WorldPop denominator 6,584,762). Do not invent or imply an engine v4."
  > "Correct study area: Kashmir Division (10 districts) only, not Srinagar Metropolitan City. Any legacy SMC framing, 342-permit count, 207-route result, 39% route reduction claim, 95.7% coverage claim, or 1,009-bus headline is obsolete and prohibited from new material."

- **Data Integrity & Prohibitions (`ORIGINAL_REQUEST.md:13-18`, `IMPLEMENTATION_AND_QA_PLAN.md:35-57`):**
  > "GPS is not ridership: App GPS validates the supply-side chain (geometry, speed, runtime, cycle time, fleet). It cannot validate demand, boarding, latent demand, or ridership. Never claim ridership validation; use observational GPS validation or decision robustness."
  > "No invented data: Field enumeration and AHP/Delphi panel were not collected; report V3 plainly as not performed."
  > "Circularity disclosed: Disclose CHALO calibration circularity in V2 up front. Mark the 5 GPS-corrected corridors as in-sample for cycle re-anchoring."
  > "Population is not demand: Catchment populations overlap; report only the deduplicated union for network totals."
  > "Do not modify external repos: E:\kash and E:\bus-sathi-trace are read-only. Large caches (data/cache/) must never be committed to git."

- **Engine Fleet Sizing Formula (`ORIGINAL_REQUEST.md:35-36`, `IMPLEMENTATION_AND_QA_PLAN.md:232-236`, `STATUS.md:184-187`):**
  ```python
  operating = max(1, math.ceil(cycle / max(1, headway)))
  fleet     = max(max(1, math.ceil(operating * 1.15)),          # ceil on the PRODUCT
                  1 if route_type == "Regional_District" else 2)  # MIN_FLEET_REGIONAL/URBAN
  ```
  SSCL routes are explicitly excluded from this formula because their fleet counts are overwritten with empirical CHALO deployment figures (`IMPLEMENTATION_AND_QA_PLAN.md:237`, `STATUS.md:189-190`).

- **Cycle Time Model & Caps (`analysis/v04_gps_validation.py:39-43`, `STATUS.md:122-130`):**
  ```python
  n_stops     = max(1, floor(L * 1000 / STOP_SPACING_M))         # STOP_SPACING_M = 500.0 m
  dwell_model = n_stops * STOP_PENALTY_MIN                       # STOP_PENALTY_MIN = 0.5 min
  one_way     = OSRM_min * congestion + dwell_model + junction_penalty
  cycle_raw   = one_way * 2 * TERMINAL_LAYOVER_FACTOR            # TERMINAL_LAYOVER_FACTOR = 1.10
  cycle       = min(cycle_raw, L * 2 * cap_per_km)              # Urban 4.0, Peri_Urban 2.5, Regional 1.5 min/km
  ```
  Binding cap observation: 169 of 186 routes (90.9%) have `Cycle_Time_Min` bound at the cap (Regional 71/71 = 100%, Peri_Urban 46/47 = 97.9%, Urban 52/68 = 76.5%).

- **Catchment Formulation (`analysis/a02_network_catchments.py:23-45`, `paper/FINDINGS.md:152-187`):**
  $$A_{\text{net}} = \bigcup_{v \in V, d(v) \le R} B(v, \min(R - d(v), \tau))$$
  Where $R = 400\text{ m}$, $\tau = 100\text{ m}$ (tested across $\tau \in \{50, 100, 150\}\text{ m}$), stop spacing $250\text{ m}$.
  Observation: Euclidean catchment overstates population served by median 37.4% per route and 31.9% network-wide (2,339,394 Euclidean $\to$ 1,592,847 Network). Coverage falls from 35.5% to 24.2%.

- **Composite Demand Index (`analysis/a03_index_weights.py:16-24`, `analysis/common.py:75-98`):**
  $$\text{Pop\_Score}_i = \text{minmax}\left(\text{clip}\left(\frac{P_i}{L_i}, P_{95}\right)\right)$$
  $$\text{POI\_Score}_i = \text{minmax}\left(\frac{\sum_j w(\text{tier}_j) \cdot [d_{ij} \le 250\text{ m}]}{L_i}\right)$$
  $$\text{CDI}_i = w_{\text{pop}} \cdot \text{Pop\_Score}_i + w_{\text{poi}} \cdot \text{POI\_Score}_i$$
  Where $P_{95}$ is the 95th percentile cap, $w(\text{high})=1.0, w(\text{medium})=0.4, w(\text{seasonal})=0.6$, trunk eligibility gate is at 30th percentile, and class bands $k=3$ (Jenks).

- **Frozen Parameter Specifications (`analysis/common.py:75-128`):**
  - Fixed Random Seed: `RANDOM_SEED = 20260823`
  - Study Area Population Denominator: `6,584,762` (Census 2011 comparison: `6,888,475`)
  - Coordinate Reference Systems: `WGS84 = "EPSG:4326"`, `UTM = "EPSG:32643"` (Zone 43N)
  - 10 Districts: Anantnag, Bandipore, Baramulla, Budgam, Ganderbal, Kulgam, Kupwara, Pulwama, Shopian, Srinagar.
  - Headway Policy: SSCL Trunk = 15 min, High Priority (HP) = 20 min, Medium Priority (MP) = 35 min, Low Priority (LP) = 35 min, Maximum Urban/Peri Ceiling = 35 min, Regional Buckets = (35, 40, 45, 50) min.
  - Vehicle Capacities: HPV = 60, MPV = 35, LPV = 20.
  - Fleet Constraints: Min Fleet Urban = 2, Min Fleet Regional = 1, Spare Ratio = 1.15.

---

## 2. Logic Chain

1. **Premise 1 (Frozen Baseline):** The paper companion is an audited evaluation of the frozen engine version `v3.4.5-geo`. It does not construct an engine `v4`. Therefore, all 644 rows (614 permits + 30 synthetic SSCL routes), 186 active routes, 1,011 fleet count, and 6,584,762 population denominator are invariant ground-truth inputs.
2. **Premise 2 (Unit of Analysis):** As proved in Finding F1 and diagnostic D1, the 614 permit rows represent 157 distinct corridors. The transition 644 $\to$ 186 is 71.0 percentage points change-of-unit and 0.2 percentage points (1 corridor) physical consolidation. Therefore, claiming a "39% route reduction" or "342 permits $\to$ 207 routes" is factually invalid and forbidden.
3. **Premise 3 (Demarcation of GPS Scope):** Driver GPS data originates from an operator app deployed in the Srinagar metropolitan area covering 14 corridor matches (5 matched, 9 partial) across 11 planned routes. GPS tracks buses and speeds; it does not collect passenger boardings or demand. Therefore, GPS provides observational supply-side validation of runtime, cycle time, and fleet formulas only. Any assertion of "validated against ridership" is false.
4. **Premise 4 (Circularity & In-Sample Handling):** The 5 GPS-matched corridors were utilized by v3.4.5 to re-anchor cycle times. Thus, evaluating v3.4.5 against those same 5 corridors is an in-sample test and must be labelled as such. Furthermore, CHALO e-bus boarding counts were used to calibrate engine plausibility, making V2 a consistency check rather than an independent benchmark.
5. **Premise 5 (Methodological Corrections):** Euclidean buffers systematically cross natural water barriers (Dal Lake, Jhelum River), causing a 37.4% median overstatement of population served. Moreover, engine v3.4.5 embedded an undocumented 1.3 tourist multiplier directly into population headcounts on 8 routes (285,914 persons). The companion repo must isolate resident population from demand multipliers and recompute catchments over the pedestrian graph.
6. **Premise 6 (Independent Auditing):** Built-in Checkers A through F establish explicit stop conditions (e.g., zero fleet self-test mismatches, zero stale metrics, 5,000 Monte Carlo draws, fixed random seed 20260823). These form the gating criteria for transitioning across phases P0 through P7.

---

## 3. Detailed Specification Inventories

### 3.1 Inventory of Non-Negotiable Constraints & Frozen Parameters

| # | Constraint Name | Authority / Source | Specification / Rule | Hard Stop / Invalidation Condition |
|---|---|---|---|---|
| C1 | Frozen Engine Baseline | `ORIGINAL_REQUEST.md:11`, `IMPLEMENTATION_AND_QA_PLAN.md:27-30` | Version `v3.4.5-geo`: exactly 644 rows (614 permits + 30 SSCL), 186 active services, 1,011 fleet, 6,584,762 WorldPop denominator. | Any code implying or creating an engine v4 or editing `E:\kash`. |
| C2 | Correct Study Area Geography | `ORIGINAL_REQUEST.md:12`, `IMPLEMENTATION_AND_QA_PLAN.md:31-34` | Kashmir Division (10 districts only). | Any framing of Srinagar Metropolitan City as study area. |
| C3 | Forbidden Numbers & Claims | `ORIGINAL_REQUEST.md:12, 70`, `IMPLEMENTATION_AND_QA_PLAN.md:32-34, 528-530` | Absolutely no occurrences of: `342` permits, `207` routes, `39%` route reduction, `95.7%` coverage, `1,009` fleet headline. | Presence of any uncontextualized stale metric in code, tables, figures, or prose. |
| C4 | GPS Demarcation | `ORIGINAL_REQUEST.md:13`, `IMPLEMENTATION_AND_QA_PLAN.md:35-39`, `STATUS.md:26-28` | App GPS validates supply-side only (geometry, speeds, runtime, cycle, fleet). Never demand. | Any claim that the plan is "validated against ridership". |
| C5 | No Invented Data / V3 Status | `ORIGINAL_REQUEST.md:14`, `IMPLEMENTATION_AND_QA_PLAN.md:40-43`, `STATUS.md:21` | No field enumeration or AHP panel was conducted. V3 must be reported as "not performed". | Fabricating AHP weights, Delphi panel, or boarding counts. |
| C6 | Circularity Disclosures | `ORIGINAL_REQUEST.md:15`, `IMPLEMENTATION_AND_QA_PLAN.md:44-47` | CHALO calibration circularity disclosed up front in V2. 5 matched GPS corridors labelled `in_sample`. | Claiming independent validation from CHALO or the 5 re-anchored routes. |
| C7 | Deduplicated Population Catchments | `ORIGINAL_REQUEST.md:16`, `IMPLEMENTATION_AND_QA_PLAN.md:48-50` | Overlapping route catchments must never be summed for network totals. Only the spatial union. | Summing route catchment populations to produce a network coverage figure. |
| C8 | Read-Only Repositories & Git Hygiene | `ORIGINAL_REQUEST.md:17`, `IMPLEMENTATION_AND_QA_PLAN.md:67-68, 185` | `E:\kash` and `E:\bus-sathi-trace` are read-only. Git ignores large caches (`walk_graph.gpickle`, `catchments_network.gpkg`, `kashmir_worldpop.tif`). | Writing to external repos or committing binary caches/keys to git. |
| C9 | Work Register & Race Prevention | `ORIGINAL_REQUEST.md:18`, `IMPLEMENTATION_AND_QA_PLAN.md:55-57, 128-136` | Active task ownership logged in `logs/WORK_REGISTER.md`. One worker owns a file at a time. | Concurrent processes writing to the same derived file. |
| C10 | Deterministic Random Seed | `ORIGINAL_REQUEST.md:80`, `IMPLEMENTATION_AND_QA_PLAN.md:550`, `analysis/common.py:127` | `RANDOM_SEED = 20260823` applied across all stochastic processes (Monte Carlo, Sobol, bootstrapping). | Any run producing non-reproducible or unseeded stochastic results. |
| C11 | Separation of Tourist Multiplier | `paper/FINDINGS.md:188-212`, `analysis/a02b_faithfulness.py:24-32` | `TOURIST_POPULATION_MULTIPLIER = 1.3` on 8 routes must be separated from resident population counts. | Treating tourist-boosted headcount as resident population in coverage numerators. |

### 3.2 Complete Mathematical Definitions, Algorithms, and Self-Tests

#### Math 1: Network Walk Catchment Formulation
Let $R = 400.0\text{ m}$ (walk budget), $S = \{s_k\}$ be the virtual stops spaced at interval $\Delta s = 250.0\text{ m}$ along route alignment $L_i$. Let $G = (V, E)$ be the walkable OpenStreetMap network graph in UTM Zone 43N (EPSG:32643).
1. Snap each stop $s \in S$ to nearest graph node $n(s) \in V$ with snap offset $o(s) = \|s - n(s)\|_2$. If $o(s) > R$, mark stop as off-network (Finding F8: 46 of 22,360 stops = 0.21% off-network, median offset 11.0 m).
2. Execute multi-source Dijkstra from $\{n(s)\}$ initialized with distance labels $d(n(s)) = o(s)$. For every visited node $v \in V$ with shortest walking distance $d(v) \le R$:
   $$\text{Remaining walk budget: } r(v) = \min(R - d(v), \tau)$$
   Where $\tau = 100.0\text{ m}$ (grid resolution of WorldPop 2026 UN-adjusted raster).
3. The route network catchment polygon is:
   $$A_{\text{net}} = \bigcup_{v \in V, d(v) \le R} B(v, r(v))$$
   Where $B(v, r)$ is a 2D Euclidean disc of radius $r$ centered at node coordinates $v$.
4. Zonal statistics: Overlap $A_{\text{net}}$ with WorldPop raster using `rasterstats.zonal_stats` with nodata handling. Network total is computed exclusively on $\bigcup_{i=1}^{186} A_{\text{net}, i}$.

#### Math 2: Composite Demand Index (CDI) & Alternative Weightings
For route $i$ with length $L_i$ (km), resident catchment population $P_i$, and opportunity set $\{j\}$ within pedestrian walk budget $250.0\text{ m}$:
1. Population Density Score:
   $$\text{Pop\_Density}_i = \frac{P_i}{\max(10^{-6}, L_i)}$$
   $$\text{Pop\_Capped}_i = \min\left(\text{Pop\_Density}_i, \text{Percentile}_{95}(\{\text{Pop\_Density}\})\right)$$
   $$\text{Pop\_Score}_i = \frac{\text{Pop\_Capped}_i - \min(\text{Pop\_Capped})}{\max(\text{Pop\_Capped}) - \min(\text{Pop\_Capped})}$$
2. Opportunity Gravity Score:
   $$\text{POI\_Weighted}_i = \sum_{j: d(j, S_i) \le 250\text{ m}} w(\text{tier}_j)$$
   Where $w(\text{high}) = 1.0, w(\text{medium}) = 0.4, w(\text{seasonal}) = 0.6$.
   $$\text{POI\_Score}_i = \frac{\frac{\text{POI\_Weighted}_i}{\max(10^{-6}, L_i)} - \min}{\max - \min}$$
3. Composite Demand Index:
   $$\text{CDI}_i = w_{\text{pop}} \cdot \text{Pop\_Score}_i + w_{\text{poi}} \cdot \text{POI\_Score}_i$$
   - Equal Weighting: $w_{\text{pop}} = 0.50, w_{\text{poi}} = 0.50$.
   - Shannon Entropy Weighting:
     $$p_{ik} = \frac{x_{ik}}{\sum_{i=1}^n x_{ik}}, \quad e_k = -\frac{1}{\ln n} \sum_{i=1}^n p_{ik} \ln(p_{ik}), \quad d_k = 1 - e_k, \quad w_k = \frac{d_k}{\sum_{m} d_m}$$
   - PCA First Component Weighting: SVD on standardized matrix $Z = U \Sigma V^T$, weights $w_k = \frac{|V_{1k}|}{\sum_m |V_{1m}|}$.
   - AHP weights derived: explicitly set to `false`.

#### Math 3: Classification & Tier Agreement Statistics
1. Jenks Natural Breaks Optimization: Partition route scores into $k$ classes ($k \in \{2, 3, 4, 5, 6, 7\}$) minimizing squared deviations from class means:
   $$\text{SDAM} = \sum_{i=1}^n (x_i - \bar{x})^2, \quad \text{SDCM} = \sum_{c=1}^k \sum_{i \in C_c} (x_i - \bar{x}_c)^2$$
   $$\text{GVF} = 1 - \frac{\text{SDCM}}{\text{SDAM}}$$
   Elbow criterion identifies optimal class count $k=3$.
2. Agreement Metrics across Jenks, Quantiles, and K-Means:
   $$\text{Observed Agreement } p_o = \frac{1}{n} \sum_{i=1}^n [C_{1, i} == C_{2, i}]$$
   $$\text{Expected Chance Agreement } p_e = \sum_{c=1}^k \left(\frac{n_{1, c}}{n} \cdot \frac{n_{2, c}}{n}\right)$$
   $$\text{Cohen's Kappa } \kappa = \frac{p_o - p_e}{1 - p_e}$$

#### Math 4: Supply-Side Time, Cycle, and Fleet Sizing Engine Model
For route with length $L$ (km), route type $T \in \{\text{Urban}, \text{Peri\_Urban}, \text{Regional\_District}\}$, and OSRM free-flow travel time $t_{\text{osrm}}$:
1. Implied Stop Count:
   $$n_{\text{stops}} = \max\left(1, \lfloor \frac{L \cdot 1000}{500.0} \rfloor\right)$$
2. Dwell Time:
   $$t_{\text{dwell}} = n_{\text{stops}} \cdot 0.5\text{ min} \quad (\approx 1.0\text{ min/km})$$
3. Congestion Multiplier:
   $$c(T) = \begin{cases} 2.2 & T = \text{Urban (City Core)} \\ 1.4 & T = \text{Peri\_Urban} \\ 1.0 & T = \text{Regional\_District (Rural)} \end{cases}$$
4. One-Way Plan Runtime:
   $$t_{\text{oneway}} = t_{\text{osrm}} \cdot c(T) + t_{\text{dwell}} + t_{\text{junction}}$$
5. Cycle Time with Layover and Sanity Cap:
   $$t_{\text{cycle, unconstrained}} = t_{\text{oneway}} \cdot 2 \cdot 1.10$$
   $$\text{Cap Rate } \text{cap}(T) = \begin{cases} 4.0\text{ min/km} & T = \text{Urban} \\ 2.5\text{ min/km} & T = \text{Peri\_Urban} \\ 1.5\text{ min/km} & T = \text{Regional\_District} \end{cases}$$
   $$\text{Cycle\_Time\_Min} = \min(t_{\text{cycle, unconstrained}}, L \cdot 2 \cdot \text{cap}(T))$$
6. Operating Buses and Fleet Requirement Rule:
   $$\text{Operating Buses } = \max\left(1, \lceil \frac{\text{Cycle\_Time\_Min}}{\max(1, \text{Headway\_Min})} \rceil\right)$$
   $$\text{Fleet\_Required} = \max\left(\max\left(1, \lceil \text{Operating Buses} \cdot 1.15 \rceil\right), \begin{cases} 1 & T = \text{Regional\_District} \\ 2 & T \in \{\text{Urban}, \text{Peri\_Urban}\} \end{cases}\right)$$
   *(Note: $\lceil \text{Operating} \cdot 1.15 \rceil$ takes the ceiling of the product).*

#### Math 5: Mandatory Fleet Formula Self-Test
The self-test evaluates the above fleet rule on all 186 active routes against published `Fleet_Required`:
- Exclude 30 SSCL routes (their fleet is empirically overwritten by CHALO deployment records).
- For all 156 non-SSCL active routes:
  $$\Delta = |\text{Fleet\_Calculated}_i - \text{Fleet\_Published}_i|$$
- **Strict Acceptance Condition:** $\sum_{i=1}^{156} \Delta_i \equiv 0$ (exactly zero mismatches). Any mismatch halts execution.

#### Math 6: Observational GPS Dwell Regressions
1. OLS Form:
   $$\text{dwell\_min}_i = \alpha + \beta \cdot \text{km}_i + \varepsilon_i$$
   Observed empirical values: $\hat{\alpha} = 17.67\text{ min}$ ($p < 0.05$), $\hat{\beta} = 0.247\text{ min/km}$, $R^2 = 0.03$. Engine implied ($0.0\text{ intercept}, 1.0\text{ slope}$) rejected.
2. WLS Form:
   Weighted by run counts $w_i = n\_runs_i$ (varying from 5 to 211 runs).
   Examine sensitivity to outlier corridor C17 (6 runs, 9.6 min/km).

#### Math 7: Monte Carlo & Sobol Global Sensitivity Formulation
1. Deterministic Sampling: $N = 5,000$ accepted parameter draws seeded with `20260823`.
2. Empirical Pace Prior: For Urban and Peri-Urban routes, sample observed one-way pace (min/km) from triangular distribution $\text{Triangular}(\text{low}=3.45, \text{mode}=4.62, \text{high}=9.60)$ derived from GPS profiles, rather than raw OSRM. Rural pace retained at modelled cap due to lack of rural observations.
3. Sobol Decomposition:
   $$Y = f(X_1, \dots, X_p) = f_0 + \sum_i f_i(X_i) + \sum_{i < j} f_{ij}(X_i, X_j) + \dots$$
   - First-order index: $S_i = \frac{\text{Var}(E[Y|X_i])}{\text{Var}(Y)}$
   - Total-order index: $S_{Ti} = 1 - \frac{\text{Var}(E[Y|X_{\sim i}])}{\text{Var}(Y)}$
   - Report 95% bootstrap confidence intervals for all indices.

#### Math 8: Accessibility Gini & Spatial Equity
Population-weighted Gini coefficient of accessibility distribution:
$$G = 1 - 2 \int_0^1 L(p) dp$$
Where $x_i$ is accessibility score of unit $i$, weighted by resident population $w_i$.
Spatial autocorrelation of uncovered population: Moran's $I$:
$$I = \frac{n}{\sum_{i} \sum_{j} w_{ij}} \frac{\sum_{i} \sum_{j} w_{ij} (z_i - \bar{z})(z_j - \bar{z})}{\sum_{i} (z_i - \bar{z})^2}$$
Where $w_{ij}$ is row-standardized spatial contiguity weights matrix over the uncovered population grid.

---

## 4. Phase-by-Phase Deliverables & Audit Gates (Phases 0 to 7)

```
P0 repository + claim freeze
  ├─ P1 repaired observational GPS validation ──> §6, P4 pace prior, Fig 7
  │    └─ P4 OAT + Monte Carlo + Sobol ──> Fig 8/8b, Table 7, fleet interval
  ├─ P2 index weights + classes ──> Fig 6, Table 5, §4.4–4.7, §5.4
  ├─ P3a network/headway ──> Fig 5, Table 4, §5.1–5.3/5.6
  ├─ P3b access/equity/transfers ──> access map, §5.9–5.11
  └─ P3c operational scenarios ──> Fig 8, §5.12–5.13
                         ↓
                   P5 figures/tables
                         ↓
                   P6 prose drafting
                         ↓
                   P7 full reproduction + release
```

### Phase 0: Baseline Setup, Manifests, and Claim Ledger
- **Lead / Files Owned:** Reproducibility Lead; `README.md`, `requirements.txt`, `.gitignore`, `LICENSE`, `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`, `logs/WORK_REGISTER.md`, `analysis/run_all.py`, `data/MANIFEST.md`, `paper/CLAIM_LEDGER.md`.
- **Deliverables:**
  1. Repository hygiene and GPL-3.0 licensing.
  2. `analysis/run_all.py` supporting `--stage`, `--module`, `--quick`, `--full` without invoking engine or downloading data.
  3. `data/MANIFEST.md` cataloging raw data sources, licenses, expected filenames, and checksums.
  4. `paper/CLAIM_LEDGER.md` with unique ID, exact claim, source file, statistic, denominator, universe, caveat, manuscript section.
- **Audit Gate P0:** Fresh clone + raw inputs runs `python analysis/run_all.py --quick`; README details non-redistributable data; `git status` clean of keys or binary caches.

### Phase 1: Repaired Observational GPS Validation (`v04`)
- **Lead / Files Owned:** Runtime-Validation Analyst; `analysis/v04_gps_validation.py`, `data/derived/v04_*`, `paper/tables/table06*`, `logs/v04_*`.
- **Deliverables:**
  1. Separation of analysis groups: `matched_in_sample` (5 corridors), `partial_out_of_sample` (9 corridors), `all_corridors_descriptive` (18 profiles).
  2. Model state separation: `plan_oneway_min_pre_v345` vs `cycle_min_post_v345`; no mixed calculations.
  3. Route-length MAPE limited strictly to 5 matched corridors.
  4. OLS and WLS dwell regressions with C17 outlier analysis.
  5. 186-route census of cycle cap binding by class (Urban 4.0, Peri_Urban 2.5, Regional 1.5 min/km).
  6. GPS coverage metrics defined: `obs_frac` (alignment on bus-used road) vs `observed_cover` (recurring corridor).
  7. Mandatory fleet formula self-test with 0 mismatches on all non-SSCL routes.
  8. Bounded sensitivity illustration on at-cap Urban/Peri_Urban routes.
  9. Derived datasets: `v04_corridor_comparison.csv`, `v04_gps_validation.json`, `v04_fleet_illustration.csv` (optional), Tables 6a, 6b, 6c, 6d.
- **Audit Gate P1 (Checker C):** Fleet self-test produces exactly 0 mismatches; 5 matched corridors marked in-sample; no out-of-sample whole-route length comparison on partial matches; Table notes state GPS cannot validate demand/ridership; F10–F12 reproduced or documented.

### Phase 2: Index Weights and Hierarchy Evidence
- **Lead / Files Owned:** Index Analyst; `analysis/a03_index_weights.py`, `analysis/a04_class_count.py`, `data/derived/a03_*`, `data/derived/a04_*`, Table 4a, 4b, Table 5, Figure 6 inputs.
- **Deliverables:**
  1. `a03_index_weights.py` executing equal, entropy, and PCA first-component weighting on network catchments.
  2. Resident population and POIs reported separately before CDI; correlation between components quantified.
  3. Explicit recording of `ahp_weights_derived = false` and declaration that no panel convened.
  4. `a04_class_count.py` computing Jenks GVF for $k=2\dots 7$, identifying elbow at $k=3$.
  5. Cohen's kappa and confusion matrices comparing Jenks, quantiles, and k-means tiers.
  6. Route-level score table for all 186 active routes with tier assignments and agreement flags.
- **Audit Gate P2:** All 186 routes present with unique IDs; normalized values in $[0, 1]$; weights sum to 1.0; 3-tier class count justified by empirical GVF curve.

### Phase 3: Operational, Equity, and Network Results
- **Sub-phases & Deliverables:**
  - **P3a (Network & Headways):** `analysis/a10_network_diagnostics.py` and `analysis/a05_headway_timeofday.py` (parsing `Hourly_Passenger_Count.csv` with `skiprows=1`). Unique network length, duplication ratio, overlap heatmap, peak/off-peak/evening headway profiles. Distinct counts for permits, distinct corridors, and active services. Feeds Table 4, Figure 5.
  - **P3b (Accessibility, Equity & Transfers):** `analysis/a11_coverage_accessibility.py`, `analysis/a12_equity_gini.py`, `analysis/a13_transfers.py`. Deduplicated network union only. Moran's I on uncovered population. Population-weighted accessibility Gini before and after rationalization on identical spatial units. Zero-centred diverging loss-and-gain map naming count and location of losers. Transfer shares (0/1/2+) and break-even penalty. Feeds Accessibility Difference Map.
  - **P3c (Fleet Plausibility & Scenarios):** `analysis/a06_deadhead.py` (depot routing or 5–12% literature range), `analysis/a07_load_factor.py` (offered capacity vs proxy demand labelled "implied load factor", never "observed occupancy"), `analysis/a14_cost_emissions.py`, `analysis/a15_scenarios.py` (5 predefined scenarios: do-nothing, efficiency-first, equity-first, balanced, peak-tourist). Optional `a16_peer_regression.py` only if peer-city data is robust.
- **Audit Gate P3:** No output labelled "observed" if modelled or proxy; before/after measures preserve boundary, raster, and opportunity definitions; explicit accounting of losers.

### Phase 4: Uncertainty Analysis and Multi-Channel Validation
- **Lead / Files Owned:** Robustness Analyst; `analysis/a08_sensitivity_oat.py`, `analysis/a09_monte_carlo_sobol.py`, `analysis/v01_spatial_crossval.py`, `analysis/v02_benchmark.py`, Table 7.
- **Deliverables:**
  1. OAT sensitivity sweeps across all 10 predeclared parameters in `common.PARAMETERS`.
  2. Monte Carlo simulation: exactly 5,000 deterministic draws (`seed = 20260823`) consuming GPS measured pace prior from P1 for Urban/Peri_Urban routes. 90% CI for fleet and tier stability ($> 80\%$).
  3. Sobol global sensitivity analysis: first-order and total-order indices with bootstrap confidence intervals.
  4. Multi-channel validation framework (Table 7):
     - V1: Spatial cross-validation against OSM building footprint density (target $\rho > 0.6$).
     - V2: Benchmark consistency check ($\pm 15\%$) with CHALO circularity disclosure.
     - V3: Expert panel / field survey marked "not performed; no panel convened".
     - V4: Observational GPS validation (supply chain only; MAPE $< 20\%$, rank $\rho > 0.5$).
     - V5: Operational plausibility (implied load factors, cycle caps, fleet formulas).
     - V6: Decision robustness (tier stability across parameter distributions).
- **Audit Gate P4 (Checker D):** Fixed seed in every result JSON; exactly 5,000 draws; Sobol indices include CIs; Table 7 does not turn missing validation channels into a pass.

### Phase 5: Reproducible Publication Figures and Tables
- **Lead / Files Owned:** Publication-Graphics Analyst; `analysis/figXX_*.py`, `paper/figures/*`, `paper/tables/*`.
- **Deliverables:**
  - Figures 1–8b programmatically generated from `data/derived/` without manual edits:
    - Fig 1: Conceptual comparison (demand-driven vs supply-side open-data).
    - Fig 2: Literature taxonomy of planning methods.
    - Fig 3: Study area map (4 panels: admin units, population density, road hierarchy, opportunities; UTM 43N).
    - Fig 4: Methodological workflow with QA audit gates.
    - Fig 5: Network diagnostics (length distribution, link duplication, overlap heatmap).
    - Fig 6: Index behaviour (CDI distribution, component scatter, weight sensitivity, tier sensitivity).
    - Fig 7: Rationalisation outcome (permit $\to$ corridor $\to$ active service; headways; cap binding).
    - Fig 8 & 8b: Scenario trade-off frontier, fleet uncertainty interval, tier stability.
    - Accessibility Difference Map: Diverging palette centered at zero showing gains and losses.
  - Tables 1–8 (Markdown and CSV):
    - T1 Literature synthesis matrix (co-author).
    - T2 Full input data inventory.
    - T3 Parameters and 10 QA audit gates.
    - T4 Existing network profile.
    - T5 Route scores (top/bottom 20) and sensitivity flags.
    - T6 Service standards and fleet (with planned/illustrative labels).
    - T7 Six-channel validation matrix.
    - T8 Policy instruments (co-author).
- **Audit Gate P5 (Checker E):** Numbers match source CSVs exactly to declared rounding; captions state N, units, version, caveats; maps have scale, north arrow, projection, accessible palettes; line-by-line check against `CLAIM_LEDGER.md`.

### Phase 6: Manuscript Drafting (Prashant-Owned Sections)
- **Drafting Sequence:** §4 $\to$ §5 $\to$ §6 $\to$ §8 $\to$ Abstract.
- **Deliverables:**
  - §4 Methodology (2,300 words, sole owner: Equations 1–14, Algorithm 1, network walk catchments, consolidation, Jenks tiers, cycle/fleet formulas, reproducible from text alone).
  - §5 Results (2,400 words, shared with Misti: diagnosis 5.1–5.3 $\to$ design 5.4–5.7 $\to$ evaluation 5.8–5.12 $\to$ stress test 5.13; adverse findings included: 0.2 pp true consolidation, 35.5% $\to$ 24.2% coverage drop, 44 substituted distances, loser locations).
  - §6 Validation (900 words, shared with Avny and Krishnan: convergent validity, V1–V6 findings, CHALO/GPS circularity disclosed up front, GPS supply-side limits).
  - §8 Conclusions (400 words, shared: 6 structured paragraphs, zero new citations or numbers).
  - Abstract (250 words, shared: written last, total removal of stale 342/207/39%/95.7%/1,009/SMC narrative).
- **Audit Gate P6:** Every quantitative statement cites a Claim Ledger ID; limitations match across all sections; Kashmir Division and v3.4.5 used consistently.

### Phase 7: Independent Reproducibility & Release Audit
- **Deliverables & Actions:**
  1. Virtual environment installation from pinned dependencies (`requirements.txt`).
  2. Automated test suite execution:
     - `test_catchment_reproduction`: Euclidean population served matches published on self-consistent routes ($r = 0.995$, median error 0.245%).
     - `test_fleet_formula_reproduction`: Fleet formula reproduces 156 non-SSCL routes with 0 mismatches.
  3. Execution of `python analysis/run_all.py --quick` and `--full`.
  4. Checkers A through F formal audits.
  5. Repository secret scanning and `.gitignore` audit (ensuring no caches or keys committed).
  6. Final release tagging.
- **Audit Gate P7 (Checker F):** Both unit tests pass; quick run clean; tables and figures reproduce byte-identically or within declared floating tolerance; two independent sign-offs recorded.

---

## 5. Built-in Checker Audit Protocols (Checkers A–F)

| Checker | Focus Area | When Executed | Scope & Verification Commands | Invalidation / Stop Conditions |
|---|---|---|---|---|
| **Checker A** | Data & Scope Integrity | Before P1–P4, and before release | Check 186 active routes; 10 districts; 6,584,762 denominator.<br>`rg -n -i '342\|207 routes\|39%\|95\.7%\|Srinagar Metropolitan City\|1,009' paper README.md`<br>`git status --short`<br>`git check-ignore -v data\cache\walk_graph.gpickle data\cache\catchments_network.gpkg` | Any uncontextualized occurrence of obsolete metrics; raw input file modified; large cache tracked in git. |
| **Checker B** | Numerical Reproducibility | After every analysis module | Module starts from declared inputs, no hard-coded results.<br>`RANDOM_SEED = 20260823`.<br>Derived CSVs have unique IDs.<br>`Get-FileHash data\derived\<output>.csv` | Any non-deterministic output variation across identical runs without declared tolerance. |
| **Checker C** | GPS Validation Integrity | After P1, before prose drafting | 5 matched corridors marked `in_sample`.<br>Partial matches excluded from whole-route length MAPE.<br>Pre- and post-v3.4.5 times never combined.<br>Fleet self-test produces exactly 0 mismatches on non-SSCL routes. | Any fleet self-test mismatch, ambiguous match class, or mixed model-state comparison. |
| **Checker D** | Methods & Statistical Validity | After P2–P4 | Normalization denominators documented.<br>Weights sum to 1.0; no fabricated AHP.<br>Jenks elbow justified by GVF curve.<br>Monte Carlo has exactly 5,000 accepted draws.<br>Sobol indices have bootstrap CIs. | Reporting confidence interval, stability rate, or validation pass without reproducible result file. |
| **Checker E** | Figure, Table, and Prose Audit | After P5–P6 | All figures scripted, no manual graphics.<br>Difference maps use zero-centred diverging palette with losses.<br>Every claim mapped to `CLAIM_LEDGER.md`.<br>No claim of "validated against ridership". | Any figure number mismatch, unmapped claim, or oversold benefit claim. |
| **Checker F** | Final Release Gate | Before submission or public push | Pinned dependencies installed in fresh venv.<br>`python analysis/run_all.py --quick` completes cleanly.<br>Catchment and fleet unit tests pass with 0 errors.<br>All publication outputs match repository values. | Secret keys, raw GPS personal records, or binary caches present in git index. |

---

## 6. Authoritative Findings Inventory (F1 to F12)

| ID | Finding Name | Primary Metric / Observation | Source Module | Direct Methodological Consequence |
|---|---|---|---|---|
| **F1** | Permit vs Route Register | 614 permit rows = 157 distinct corridors. Engine 71.1% "reduction" decomposes to 71.0 pp change-of-unit + 0.2 pp consolidation (1 corridor). Plan retains 156 of 157 corridors (99.4%). | `q01_data_quality.py` (D1) | Kills the "39% route reduction" claim. What collapsing costs: 32 alternative via routings suppressed, 38 corridors mixing vehicle class, 34 mixing service types. |
| **F2** | WorldPop vs Census Denominator | WorldPop 2026 sum = 6,584,763 vs Census 2011 = 6,888,475 (ratio 0.956, implied −0.30%/yr). Matches engine denominator 6,584,762. | `q01_data_quality.py` (D4) | Population surface is conservative: coverage shares biased upward, absolute population served biased downward. State both directions; do not rescale. |
| **F3** | Modelled vs Observed Runtime | MAPE(OSRM vs observed in-motion) = 65.1%; MAPE(plan vs observed one-way) = 47.6%; median plan/observed ratio = 0.51. | `q01_data_quality.py` (D6) | Cycle times and fleet requirements understated where unmeasured. Must carry into Monte Carlo as an empirical speed prior, not a caveat. |
| **F4** | Driver GPS Observational Floor | 66 of 186 active routes (35%) appear in driver-GPS record (`OBSERVED`). Complement (120 routes) is driver app adoption, not dormancy. | `q01_data_quality.py` (D2) | Report 66/186 as an observational floor; do not cite complement as a dormancy rate. |
| **F5** | Opportunity Geographic Bias | 2,431 POIs; 65% in Srinagar; per-100k density ranges 0.3–120.4 across districts. | `q01_data_quality.py` (D5) | POIs are exposed to volunteered-data bias. Must survive weight sensitivity (equal/entropy/PCA) and Monte Carlo down-weighting. |
| **F6** | Road Network Completeness | 18,533 km walkable road inside 10 districts. $\rho(\text{population density}, \text{mapped road density}) = 0.92$. | `q01_data_quality.py` (D3) | Peripheral bias check is benign at district scale. Licenses using OSM walk graph without completeness correction. |
| **F7** | Plan Internal Geometry Inconsistency | Published plan internally inconsistent on 44 of 186 routes where v3.4.4 substituted verified road distances into `Route_KM` without redrawing geometry or recomputing population. | `a02_network_catchments.py`, `a02b_faithfulness.py` | Full residual inventory: 142 self-consistent, 44 substituted distances, 3 minor drift, 2 superseded geometry, 1 stale tourist flag. |
| **F8** | Catchment Population Overstatement | Euclidean catchments overstate population served by median 37.4% per route (IQR 30.5–41.7%) and 31.9% network-wide (2,339,394 $\to$ 1,592,847). Coverage drops 35.5% $\to$ 24.2%. | `a02_network_catchments.py` | Central methodological result of the paper. Robust across $\tau \in \{50, 100, 150\}\text{ m}$ (52.8%, 37.4%, 29.2%). Only 0.21% stops off-network. |
| **F9** | Embedded Tourist Demand Multiplier | `TOURIST_POPULATION_MULTIPLIER = 1.3` multiplied into `Population_Served` on 8 routes (285,914 persons) and written to headcount column. | `a02b_faithfulness.py` | Category error mixing demand into headcount. Reproduction separates resident population and demand boost; coverage reported on residents only. |
| **F10** | Binding Per-KM Cycle Time Caps | 169 of 186 active routes (90.9%) have `Cycle_Time_Min` sitting exactly at the asserted per-km cap (Regional 100%, Peri_Urban 97.9%, Urban 76.5%). Caps truncate downward below reality. | `v04_gps_validation.py` (rewrite) | The sanity cap, not the model, determines the plan's fleet. Explains F3's 0.51 ratio. Only 5 routes above cap are the 5 with GPS measurements. |
| **F11** | Runtime Component Decomposition | Congestion multiplier survives (OSRM $\div 2.2$ reproduces observed moving speed at $+1.4\%$ bias). Dwell model fails (observed 1.76 min/km vs engine 1.00; OLS $R^2 = 0.03$, significant intercept). | `v04_gps_validation.py` (rewrite) | Purely proportional dwell model unsupported. Speed over-prediction and dwell under-prediction partially offset. |
| **F12** | Distinct GPS Coverage Definitions | `obs_frac` (median 0.94; 183/186 > 0) = alignment lies on roads with bus traffic. `observed_cover/status` (66 OBSERVED / 45 PARTIAL / 75 NO_APP_DATA) = recurring service on alignment. | `v04_gps_validation.py` (rewrite) | Labels must be kept distinct: `obs_frac` corroborates geometry alignment; `status` corroborates recurring service. |

---

## 7. Required Tables: Features Discovered and Edge Cases

### Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Baseline | Repository Skeleton & Hygiene | Setup clean companion repo with license, citation, and reproducible execution runner | Pinned requirements, license templates | `README.md`, `LICENSE`, `CITATION.cff`, `requirements.txt` | Missing package fails venv install | `ORIGINAL_REQUEST.md:23`, `IMPLEMENTATION_AND_QA_PLAN.md:178` |
| 2 | Baseline | Master Reproducibility Runner | Command-line driver executing analysis stages without redownloading data | CLI flags (`--stage`, `--module`, `--quick`, `--full`) | Orchestrated pipeline execution | Invalid flag prints usage; engine invocation blocked | `ORIGINAL_REQUEST.md:24`, `IMPLEMENTATION_AND_QA_PLAN.md:181` |
| 3 | Baseline | Raw Data Manifest & Checksums | Audit manifest detailing origin, license, redistributability, and checksums for raw files | Staged files in `data/raw/` | `data/MANIFEST.md` | Missing file or hash mismatch halts QA | `ORIGINAL_REQUEST.md:25`, `IMPLEMENTATION_AND_QA_PLAN.md:184` |
| 4 | Baseline | Scientific Claim Ledger | Registry mapping every numeric claim to code, denominator, universe, and paper section | Module derived JSON/CSVs | `paper/CLAIM_LEDGER.md` | Unmapped claim rejected by Checker E | `ORIGINAL_REQUEST.md:26`, `IMPLEMENTATION_AND_QA_PLAN.md:186` |
| 5 | Baseline | Work Register Lock | Concurrency tracking preventing multi-worker write collisions on shared outputs | Task claims, worker ID | `logs/WORK_REGISTER.md` | Conflict detection if output path claimed | `IMPLEMENTATION_AND_QA_PLAN.md:128-136` |
| 6 | GPS Validation | Match Classification Split | Explicit stratification into in-sample, out-of-sample, and descriptive sets | `reality_check.csv`, `corridor_profiles.csv` | Categorized corridor tables | Unmatched route logs warning; no partial route length comparison | `ORIGINAL_REQUEST.md:29`, `STATUS.md:160` |
| 7 | GPS Validation | Model State Separation | Isolated comparison of pre-v3.4.5 snapshot runtime vs post-v3.4.5 cycle time | `reality_check.csv`, active plan CSV | Unmixed error metrics | Assert error if pre- and post-values mixed | `ORIGINAL_REQUEST.md:30`, `STATUS.md:162` |
| 8 | GPS Validation | Dwell OLS & WLS Regressions | Empirical regression of dwell time on distance with run-weighting and outlier tracking | `corridor_profiles.csv` (`km`, `dwell_min`, `n_runs`) | Coefficients, CIs, $R^2$, C17 influence | Singular matrix or $<3$ points returns NaN | `ORIGINAL_REQUEST.md:32`, `STATUS.md:169` |
| 9 | GPS Validation | 186-Route Cap Binding Census | Evaluation of planned cycle times against per-km sanity caps across all route types | `active.csv` (`Cycle_Time_Min`, `Route_KM`, `Route_Type`) | `table06c_v04_cap_binding.{csv,md}` | Unmapped class falls back to 4.0 min/km | `STATUS.md:171`, `analysis/v04_gps_validation.py:244` |
| 10 | GPS Validation | Dual GPS Coverage Reporting | Precise delineation of road alignment traffic (`obs_frac`) vs service recurrence (`status`) | `route_evidence.csv`, `permit_observed.csv` | `table06d_v04_coverage_definitions.{csv,md}` | Division by zero avoided; floor semantics | `ORIGINAL_REQUEST.md:38`, `STATUS.md:173` |
| 11 | GPS Validation | Fleet Formula Self-Test | Reproduction of published fleet counts from cycle and headway across all non-SSCL routes | `active.csv` (`Cycle_Time_Min`, `Headway_Min`, `Fleet_Required`) | Mismatch count $\equiv 0$ | Hard stop if mismatch count $>0$ | `ORIGINAL_REQUEST.md:34-37`, `STATUS.md:178-187` |
| 12 | GPS Validation | Bounded Fleet Sensitivity | Applying observed urban pace to at-cap Urban/Peri_Urban routes holding Regional at cap | `v04_corridor_comparison.csv`, active plan | `v04_fleet_illustration.csv` | Halts if fleet self-test has not passed | `ORIGINAL_REQUEST.md:37`, `IMPLEMENTATION_AND_QA_PLAN.md:239` |
| 13 | Demand Index | Pedestrian Network Recomputation | Building walksheds and POI counts using Dijkstra on OSM graph instead of Euclidean buffers | `walk_graph.gpickle`, `pois.csv`, `kashmir_worldpop.tif` | `a03_index.csv` | Stop offset $>400\text{ m}$ logged as off-network | `ORIGINAL_REQUEST.md:41`, `analysis/a03_index_weights.py:26` |
| 14 | Demand Index | Alternative Weight Derivations | Computing equal, Shannon entropy, and PCA first-component weights; setting AHP to false | Route criterion matrix (Pop Score, POI Score) | `table04a_index_weights.{csv,md}` | Uniform criterion defaults to equal weight | `ORIGINAL_REQUEST.md:42`, `analysis/a03_index_weights.py:33` |
| 15 | Demand Index | Class Count GVF Elbow Analysis | Determining optimal route classes ($k=2\dots 7$) using Jenks Goodness of Variance Fit | Route CDI scores | `a04_class_count.json`, GVF elbow curve | Array variance zero returns NaN | `ORIGINAL_REQUEST.md:43`, `IMPLEMENTATION_AND_QA_PLAN.md:276` |
| 16 | Demand Index | Tier Agreement Evaluation | Quantifying cross-scheme tier assignment agreement via Cohen's kappa and confusion matrix | Jenks, quantile, k-means tier labels | `table04b_decision_stability.{csv,md}` | Single-class trivial agreement handled | `ORIGINAL_REQUEST.md:43`, `analysis/common.py:276` |
| 17 | Network Analysis | Physical Network Topology | Computing unique network length, route-km to network-km ratio, and link duplication | Active route geometries (`.geojson`), OSM graph | `table04_network_profile.{csv,md}` | Geometry self-intersections repaired | `ORIGINAL_REQUEST.md:47`, `IMPLEMENTATION_AND_QA_PLAN.md:294` |
| 18 | Network Analysis | Temporal Headway Profiling | Parsing hourly passenger counts with `skiprows=1` and generating time-of-day headway bands | `Hourly_Passenger_Count.csv`, active plan | Headway profile tables | Header verification halts on missing cols | `ORIGINAL_REQUEST.md:47`, `STATUS.md:213` |
| 19 | Network Analysis | Deduplicated Network Coverage | Measuring network-wide population served strictly as union of all route catchments | Route catchment polygons, WorldPop raster | Coverage headcount and percentage | Overlap double-counting strictly prevented | `ORIGINAL_REQUEST.md:48`, `IMPLEMENTATION_AND_QA_PLAN.md:310` |
| 20 | Equity & Access | Uncovered Population Moran's I | Spatial autocorrelation analysis of unserved population across the 10-district grid | Uncovered population raster, spatial weights | Moran's $I$, $z$-score, $p$-value | Zero variance in unserved area handled | `ORIGINAL_REQUEST.md:48`, `IMPLEMENTATION_AND_QA_PLAN.md:311` |
| 21 | Equity & Access | Population-Weighted Gini | Measuring spatial equity before/after rationalization via Lorenz integration | Zonal accessibility scores, population weights | Before/after Gini coefficients | Zero or negative population filtered | `ORIGINAL_REQUEST.md:48`, `analysis/common.py:217` |
| 22 | Equity & Access | Zero-Centred Loss/Gain Mapping | Delineating geographic winners and losers with diverging palette centered at zero | Zonal accessibility difference grid | Difference GeoPackage & map | Monochromatic gain-only scales prohibited | `ORIGINAL_REQUEST.md:48`, `IMPLEMENTATION_AND_QA_PLAN.md:315` |
| 23 | Equity & Access | Transfer & Penalty Model | Evaluating 0/1/2+ transfer shares and break-even transfer penalty across OD pairs | Stop topology, route alignments, headway schedules | Transfer share distribution, penalty | Disconnected OD pairs explicitly reported | `ORIGINAL_REQUEST.md:48`, `IMPLEMENTATION_AND_QA_PLAN.md:317` |
| 24 | Plausibility | Deadhead Estimation | Quantifying depot pull-out/pull-in mileage using explicit depots or 5–12% range | Depot locations, route terminals, runtimes | Deadhead bus-km and bus-hours | Unanchored route deadhead flagged | `ORIGINAL_REQUEST.md:49`, `IMPLEMENTATION_AND_QA_PLAN.md:329` |
| 25 | Plausibility | Implied Load Factor Analysis | Comparing offered seat-capacity against proxy demand; labelling as implied load factor | Vehicle capacity (HPV 60, MPV 35, LPV 20), headways | Implied load factor distribution | "Observed occupancy" label strictly prohibited | `ORIGINAL_REQUEST.md:49`, `IMPLEMENTATION_AND_QA_PLAN.md:331` |
| 26 | Plausibility | Cost & Emissions Modeling | Estimating operational costs and fleet emissions across operational scenarios | Vehicle-km, fuel/electric consumption factors | Cost per accessibility gain, emissions range | Assumed vs empirical factors distinguished | `ORIGINAL_REQUEST.md:49`, `IMPLEMENTATION_AND_QA_PLAN.md:333` |
| 27 | Scenarios | Multi-Scenario Policy Frontier | Evaluating 5 pre-defined scenarios: do-nothing, efficiency, equity, balanced, tourist | Scenario parameter configurations | Scenario trade-off matrix | Inconsistent baseline across scenarios barred | `ORIGINAL_REQUEST.md:49`, `IMPLEMENTATION_AND_QA_PLAN.md:335` |
| 28 | Scenarios | Peer-City Fleet Regression | Benchmarking buses per 1,000 against peer cities with prediction intervals (optional) | Peer-city population, density, fleet data | Regression plot with 95% PI | Bar chart without prediction interval barred | `STATUS.md:224`, `IMPLEMENTATION_AND_QA_PLAN.md:337` |
| 29 | Uncertainty | One-At-a-Time (OAT) Sweeps | Sweeping all 10 (11) parameters across predeclared ranges in `common.PARAMETERS` | Parameter intervals, active plan | Parameter sensitivity curves | Out-of-bounds parameter sweep halted | `ORIGINAL_REQUEST.md:52`, `IMPLEMENTATION_AND_QA_PLAN.md:350` |
| 30 | Uncertainty | Monte Carlo Simulation | 5,000 deterministic-seed draws using GPS pace prior for Urban/Peri_Urban routes | Prior distributions, `RANDOM_SEED = 20260823` | Fleet 90% CI, tier stability $>80\%$ | Draw count $\ne 5,000$ fails Checker D | `ORIGINAL_REQUEST.md:53`, `IMPLEMENTATION_AND_QA_PLAN.md:353` |
| 31 | Uncertainty | Sobol Global Sensitivity | Decomposing output variance into first-order and total-order Sobol indices with CIs | Monte Carlo sampled outputs, SALib | $S_i, S_{Ti}$ indices with 95% bootstrap CIs | Missing confidence intervals fails QA | `ORIGINAL_REQUEST.md:54`, `IMPLEMENTATION_AND_QA_PLAN.md:356` |
| 32 | Validation | V1 Spatial Cross-Validation | Testing route CDI scores against independent OSM building footprint density | OSM building footprints, route alignments | Spearman correlation (target $\rho > 0.6$) | Re-use of POIs or WorldPop prohibited | `ORIGINAL_REQUEST.md:55`, `STATUS.md:225` |
| 33 | Validation | V2 External Benchmark Check | Benchmarking ridership/fleet against CHALO data with explicit circularity disclosure | CHALO monthly boardings, bus deployments | Percentage deviation ($\pm 15\%$) | Circularity must appear in caption/table notes | `ORIGINAL_REQUEST.md:55`, `STATUS.md:226` |
| 34 | Validation | V3 Panel Non-Performance Doc | Formally recording expert Delphi panel and boarding survey as not performed | Protocol template | Formal non-performance declaration | Fabricating survey or panel strictly prohibited | `ORIGINAL_REQUEST.md:55`, `IMPLEMENTATION_AND_QA_PLAN.md:364` |
| 35 | Validation | Master Table 7 Validation Matrix | Consolidating V1–V6 channels with test statistics, thresholds, and verdicts | Outputs from V1 to V6 | `paper/tables/table07_validation.{csv,md}` | Failed channel cannot be marked as pass | `ORIGINAL_REQUEST.md:55`, `IMPLEMENTATION_AND_QA_PLAN.md:408` |
| 36 | Publication | Programmatic Figures 1–8b | Automated vector rendering of publication figures reading only derived files | `data/derived/*.csv`, `*.json` | Publication EPS/PDF/PNG figures | Screenshots or hand edits fail Checker E | `ORIGINAL_REQUEST.md:58`, `IMPLEMENTATION_AND_QA_PLAN.md:374` |
| 37 | Publication | Manuscript Tables 1–8 | Generating Markdown and CSV tables matching source data to declared precision | Derived analysis outputs | `paper/tables/table01` to `table08` | Numeric mismatch with source fails audit | `ORIGINAL_REQUEST.md:59`, `IMPLEMENTATION_AND_QA_PLAN.md:399` |
| 38 | Drafting | §4 Methodology (Equations 1–14) | Comprehensive mathematical methodology draft reproducible from text alone | Formal equations, Algorithm 1, parameters | 2,300-word draft in `paper/` | Equation omission or imprecise symbol fails QA | `ORIGINAL_REQUEST.md:62`, `IMPLEMENTATION_AND_QA_PLAN.md:425` |
| 39 | Drafting | §5 Results (Fixed Structure) | Result narrative structured as diagnosis $\to$ design $\to$ evaluation $\to$ stress test | Findings F1–F12, Tables 4–6 | 2,400-word draft with adverse findings | Interleaving sections or missing losers barred | `ORIGINAL_REQUEST.md:63`, `IMPLEMENTATION_AND_QA_PLAN.md:447` |
| 40 | Drafting | §6 Validation & Circularity | Validation chapter presenting convergent validity, V1–V6, and circularity disclosures | Table 7, GPS limits, CHALO notes | 900-word draft with circularity up front | Favourable claim before circularity barred | `ORIGINAL_REQUEST.md:64`, `IMPLEMENTATION_AND_QA_PLAN.md:456` |
| 41 | Drafting | §8 Conclusions (6 Paragraphs) | Structured conclusion covering problem, 5 findings, methods, policy, research, transfer | Manuscript findings | 400-word structured draft (6 paragraphs) | New numbers or citations prohibited | `ORIGINAL_REQUEST.md:65`, `IMPLEMENTATION_AND_QA_PLAN.md:463` |
| 42 | Drafting | Abstract (Final Synthesis) | Truthful abstract eliminating all legacy route-reduction and ridership validation claims | Final verified findings | 250-word abstract written last | Any occurrence of stale metrics barred | `ORIGINAL_REQUEST.md:65`, `IMPLEMENTATION_AND_QA_PLAN.md:469` |
| 43 | Release | Catchment Faithfulness Unit Test | Verifying Euclidean population reproduction on 142 self-consistent routes ($r=0.995$) | `Rationalised_Routes_Kashmir_v3.csv` | Test pass / fail assertion | Absolute error $>1\%$ on clean routes fails | `ORIGINAL_REQUEST.md:93`, `IMPLEMENTATION_AND_QA_PLAN.md:482` |
| 44 | Release | Fleet Formula Unit Test | Verifying engine fleet formula reproduction on 156 non-SSCL active routes | `Rationalised_Routes_Kashmir_v3.csv` | Test pass / fail assertion | Any mismatch fails build | `ORIGINAL_REQUEST.md:93`, `IMPLEMENTATION_AND_QA_PLAN.md:482` |

### Edge Cases
| # | Feature | Input / Condition | Observed Behavior / Required Handling |
|---|---------|-------------------|---------------------------------------|
| 1 | Catchment Dijkstra | Virtual stop $>400.0\text{ m}$ from pedestrian network (`a02_network_catchments.py:84`) | Marked off-network and logged. Observed: 46 of 22,360 stops (0.21%) off-network with median snap offset 11.0 m. Excluded from graph walking source set. |
| 2 | Faithfulness Accounting | Substituted road distance without redrawn geometry (`a02b_faithfulness.py:78`) | 44 of 186 routes have exact half-km `Route_KM` (e.g. 6.5, 17.0, 151.0 km) differing by 0.76–1.14× from drawn geometry. Labeled `substituted_distance`; not treated as random noise. |
| 3 | Faithfulness Accounting | Undocumented tourist multiplier embedded in headcount (`a02b_faithfulness.py:65`) | 8 routes boosted by exactly 1.3× in `Population_Served`. Reproduction recovers exact match only by factoring out 1.3×; separates resident headcount from tourist demand. |
| 4 | Faithfulness Accounting | Stale tourist boost flag on cleared route (`a02b_faithfulness.py:82`) | Route SSCL-27 carries `Tourist_Corridor = False` but published population reproduces at $1/1.3$ of target. Classified as `stale_tourist_flag`. |
| 5 | Faithfulness Accounting | Superseded geometry on redrawn alignments (`a02b_faithfulness.py:86`) | Routes FDR-438 (0.419×) and FDR-160 (0.630×) retain population computed on longer historical alignment. Classified as `superseded_geometry`. |
| 6 | Fleet Self-Test | Synthetic SSCL e-bus routes (`v04_gps_validation.py`, `STATUS.md:189`) | 30 SSCL routes have `Fleet_Required` overwritten by empirical CHALO bus counts. Must be explicitly excluded from fleet formula self-test to avoid false mismatch flags. |
| 7 | Fleet Self-Test | Regional District minimum fleet constraint (`transit_kashmir_v3.py:3165`) | Minimum fleet is 1 for Regional_District but 2 for Urban/Peri_Urban routes. Formula must evaluate `1 if route_type == "Regional_District" else 2`. |
| 8 | GPS Match Stratification | Partial corridor-route association (`v04_gps_validation.py:28-34`) | 9 partial corridors have route length mismatches up to 3× (`obs_km` vs `eng_km`). Primary comparison restricted to length-invariant rates (min/km, km/h); whole-route length MAPE prohibited. |
| 9 | GPS Congestion Validation | Suburban/rural corridors tested on city multiplier (`v04_gps_validation.py:166`) | All 18 observed corridors are located in Srinagar or immediate belt. Peri_Urban (1.4) and Rural (1.0) congestion checks must be labelled classification counterfactuals, not rural field tests. |
| 10 | GPS Dwell Model | Outlier corridor with minimal run sample (`STATUS.md:170`) | Corridor C17 has only 6 runs and extreme dwell of 9.6 min/km. WLS regression weighted by $n\_runs$ prevents C17 from distorting overall dwell parameter estimates. |
| 11 | Cycle Time Cap Binding | Urban routes with high modelled delays (`STATUS.md:125`) | 52 of 68 Urban routes (76.5%) truncate at 4.0 min/km cap. The 5 routes exceeding cap are precisely the 5 routes with empirical GPS re-anchoring; all others truncate at cap. |
| 12 | Headway Data Ingestion | Raw passenger count CSV header structure (`STATUS.md:213`) | `Hourly_Passenger_Count.csv` contains descriptive metadata on line 1. Must be parsed with `pd.read_csv(..., skiprows=1)` to avoid corrupting column headers. |
| 13 | Network Catchment Union | Overlapping catchments across routes (`IMPLEMENTATION_AND_QA_PLAN.md:48`) | Catchments of multiple routes serving same corridor overlap heavily. Summing route populations gives 2,339,394 (Euclidean) vs 1,592,847 (Network union). Union must dissolve overlapping geometries before zonal stats. |
| 14 | Opportunity Weighting | POIs with missing or invalid importance tier (`a03_index_weights.py:143`) | Unrecognized importance strings fall back to engine default of 0.4 (`medium`) with a logger warning rather than dropping the POI. |
| 15 | Entropy Weighting | Criterion with zero or uniform variance (`analysis/common.py:253`) | If all routes have identical scores on a criterion, $d_k = 0$. Algorithm catches $\sum d_k \le 0$ and assigns equal default weights ($1/m$). |
| 16 | Spatial Autocorrelation | Unserved population grid with invariant cells (`IMPLEMENTATION_AND_QA_PLAN.md:311`) | Grid cells outside district boundary or in uninhabited mountain zones must be masked to prevent zero-variance errors in Moran's $I$ computation. |
| 17 | Monte Carlo Pace Sampling | Rural routes with absent GPS observations (`v04_gps_validation.py:388`) | GPS pace prior applies exclusively to Urban and Peri_Urban routes. Rural routes must be held at their modelled values with explicit uncertainty notes because rural pace was unobserved. |
| 18 | Deadhead Modeling | Lack of specific depot roster in staged data (`IMPLEMENTATION_AND_QA_PLAN.md:329`) | In the absence of documented physical depot allocations, module must report a literature-based sensitivity range of 5–12% rather than fabricating route-level deadhead links. |

---

## 8. Caveats

1. **Read-Only Scope:** In compliance with the dispatch assignment, this report was compiled strictly through static analysis and observation of existing files and logs. No code, analysis modules, tables, or figures were executed or modified during this survey.
2. **Author Ownership Boundaries:** This specification covers the technical core owned by Prashant (§4 Methodology, §5 Results, §6 Validation, §8 Conclusions, Abstract, and associated analysis modules). Sections owned by co-authors (§1 Introduction, §2 Literature Review, §3 Study Area background, §7 Policy Instruments, and Table 1) are flagged for scope alignment (e.g. Kashmir Division vs SMC framing) but their detailed internal prose was not rewritten.
3. **Pending Module Implementations:** While Phase 0 and Phase 1 specifications are completely defined, several Phase 3 and Phase 4 modules (`a04`, `a05`, `a06`, `a07`, `a08`, `a09`, `a10`, `a11`, `a12`, `a13`, `a14`, `a15`, `v01`, `v02`) are currently unwritten or in draft status. Their mathematical definitions and acceptance criteria have been fully inventoried here from `IMPLEMENTATION_AND_QA_PLAN.md` and `STATUS.md`, but their execution traces will be validated by subsequent implementation subagents.
4. **Hardware and Environment Assumptions:** Full reproduction of `a02_network_catchments.py` requires approximately 69 minutes and `a01_build_walk_graph.py` requires 9 minutes. However, their outputs are already cached in `data/derived/` and `data/cache/`, so downstream tasks can proceed without re-running heavy spatial graph algorithms.

---

## 9. Conclusion

The specification mining across Phases 0 to 7 has established an exhaustive, unified operational inventory for the Kashmir paper companion project:
- **Contractual & Methodological Integrity:** All 8 non-negotiable contract rules are codified with zero tolerance for obsolete numbers (`342`, `207`, `39%`, `95.7%`, `1,009`, SMC).
- **Mathematical Formulations:** All 8 major mathematical models (Network Catchments, CDI Index, Entropy/PCA Weights, Jenks GVF, Cohen's Kappa, Supply-Side Runtime/Cycle/Cap Model, Fleet Sizing Self-Test, and Sobol Sensitivity) are documented with exact equations, parameter values, and distributions.
- **Audit Gate Gating:** Checkers A through F define concrete, automated stop conditions for every stage of development.
- **Execution Readiness:** This report provides the definitive blueprint for implementation, QA verification, and manuscript drafting.

---

## 10. Verification Method

To independently verify the observations, references, and findings documented in this handoff report, execute the following commands in PowerShell from `E:\kash-paper`:

1. **Verify Invariant Constants & Denominators:**
   ```powershell
   # Confirm frozen parameters in analysis/common.py
   Select-String -Path "analysis\common.py" -Pattern 'STUDY_AREA_POPULATION|RANDOM_SEED|PARAMETERS|HEADWAY_'
   ```
2. **Verify Prohibition of Obsolete Metrics (Checker A):**
   ```powershell
   # Scan repository for forbidden stale claims
   rg -n -i '342|207 routes|39%|95\.7%|Srinagar Metropolitan City|1,009' paper README.md
   ```
3. **Verify Fleet Formula Self-Test Code:**
   ```powershell
   # Check fleet formula implementation in analysis/v04_gps_validation.py
   Select-String -Path "analysis\v04_gps_validation.py" -Pattern 'fleet_obs|ceil\(obs_cycle'
   ```
4. **Verify Documented Findings F1 to F12:**
   ```powershell
   # Inspect authoritative findings in paper/FINDINGS.md
   Get-Content -Path "paper\FINDINGS.md" | Select-String -Pattern '^## F'
   ```
5. **Verify Catchment Faithfulness Residual Inventory:**
   ```powershell
   # Inspect faithfulness classification logic in analysis/a02b_faithfulness.py
   Select-String -Path "analysis\a02b_faithfulness.py" -Pattern 'classify\(|substituted_distance|reproduced'
   ```
