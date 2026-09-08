# Implementation and QA Plan — Kashmir Route Rationalisation Paper

**Purpose.** This document is the shared execution contract for any model or
person working in `E:\kash-paper`. It converts the paper brief into ordered,
testable work. A task is not complete because code exists or a chart renders; it
is complete only when its stated evidence, reproducibility check, and review
gate all pass.

**Target manuscript.** *Planning What You Cannot Count: An Open-Data Framework
for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*,
targeting *Transport Policy*, 9,000–10,000 words, 8 figures plus Figure 8b, and
8 numbered manuscript tables.

**Author ownership.** This plan covers Prashant’s work only: Abstract (shared),
§4 Methodology (sole owner), §5 Results (shared with Misti), §6 Validation
(shared with Avny and Krishnan), and §8 Conclusions (shared). It may flag
issues in other sections but must not silently rewrite co-author prose.

---

## 1. Non-negotiable research contract

Every implementer must read this section before editing code, numbers, figures,
or prose. A result that violates any item below is rejected even if it is
numerically convenient.

1. **Frozen operational baseline.** `Kashmir Valley v3.4.5` is the current
   engine baseline: 644 engine rows (614 permits + 30 SSCL routes), 186 active
   services, stated fleet 1,011, and a 6,584,762 WorldPop denominator. Do not
   create or imply an engine `v4` while completing this paper.
2. **Correct study area.** The paper is the **Kashmir Division (10 districts)**,
   not Srinagar Metropolitan City. Any inherited SMC framing, 342-permit count,
   207-route result, 39% route-reduction claim, 95.7% coverage claim, or
   1,009-bus headline is stale and must not appear in new material.
3. **GPS is not ridership.** Existing app GPS validates only the supply-side
   chain: geometry, observed movement, runtime, cycle time, and fleet
   implications. It cannot validate the Composite Demand Index (CDI), actual
   boarding, latent demand, or ridership. Never write “validated against
   ridership.” Use “observational GPS validation” or “decision robustness.”
4. **No invented data.** No field enumeration, boarding count, AHP/Delphi panel,
   or expert ranking has been collected. V3 must be reported as **not
   performed**. The original V4 field-validation specification must be rewritten
   as an observational-GPS channel with its narrower scope.
5. **Circularity must be disclosed.** CHALO aggregate ridership is used in the
   engine’s plausibility calibration and can only be a V2 consistency check, not
   independent validation. The five GPS-matched corridors were used by v3.4.5
   to re-anchor cycles and are in-sample for that correction.
6. **Population is not demand.** Residential WorldPop is reported separately
   from tourist demand adjustments. Per-route catchment populations overlap and
   must never be summed into a network total. Use the deduplicated union only.
7. **Do not silently repair the engine.** The paper companion analyses the
   frozen engine output. Any future operational patch belongs in a separately
   documented engine release, with a new version and tests; it must not overwrite
   the v3.4.5 inputs used here.
8. **No shared-file races.** One worker owns a file at a time. Never run two
   processes writing the same derived CSV, GeoPackage, table, figure, or log.

---

## 2. Workspace and source-of-truth map

### 2.1 Directories

```text
E:\kash-paper\
  analysis\       executable, paper-specific analysis modules
  data\raw\       staged inputs; never edit in-place
  data\cache\     regenerable heavy caches; never commit large third-party files
  data\derived\   module outputs (CSV / JSON, named by module)
  paper\
    FINDINGS.md   authoritative claims and values
    figures\      final publication figures only
    tables\       final publication tables only
  logs\           module logs, including command, timestamp and environment
  STATUS.md       live state; update only when a task genuinely passes QA
```

External read-only sources:

- `E:\kash` — engine v3.4.5 and its published plan.
- `E:\bus-sathi-trace` — GPS evidence definitions and source data.
- `E:\dash\bus-sathi-dashboard` — dashboard presentation layer only; not a
  primary analysis source.

### 2.2 Source precedence

When two sources disagree, use this order and record the conflict in the module
JSON output:

1. Raw staged data and the frozen v3.4.5 plan files.
2. Engine source code that generated a field.
3. GPS-source code defining a GPS measure.
4. Regenerated paper-analysis output.
5. `paper/FINDINGS.md` after its module’s QA gate passes.
6. `STATUS.md`, prose drafts, decks, dashboard, and prior documentation.

### 2.3 Current validated evidence

These results are already reproducible and may be cited once source references
are added to the manuscript:

- **F1:** 614 permit rows are 157 distinct corridors; 156/157 remain in the
  active design. The apparent 71.1% reduction is almost entirely a change of
  unit, not consolidation.
- **F2:** WorldPop 2026 sum 6,584,763 versus Census 2011 6,888,475 for the same
  districts; report both directions of resulting bias.
- **F3:** pre-correction plan runtime materially understates observed GPS
  runtime; do not treat the first `v04` fleet counterfactual as valid.
- **F4:** 66/186 observed recurring-service status is a lower bound; it is not
  a dormancy rate.
- **F5/F6:** POIs are Srinagar-concentrated; district road density tracks
  population density strongly enough to support use of the OSM walk graph.
- **F7/F9:** route geometry/population inconsistencies and the tourist
  multiplier category error are fully diagnosed.
- **F8:** network walk catchments reduce coverage from 35.5% to 24.2%; median
  route-level Euclidean overstatement is 37.4% and deduplicated network-wide
  overstatement is 31.9%.

F10–F12 are promising but **not manuscript-ready** until the rewritten GPS
module passes its acceptance checks.

---

## 3. Multi-worker protocol

### 3.1 Before starting a task

1. Read `STATUS.md`, this file, `paper/FINDINGS.md`, and the relevant module.
2. Append a short claim to `logs/WORK_REGISTER.md` with: worker name, task ID,
   files to be edited, expected outputs, start time, and expected duration.
3. Confirm no other active entry owns any of the same output paths.
4. Create a task-specific branch if git is configured. If workers truly share a
   working directory, do not edit common files (`common.py`, `FINDINGS.md`,
   `STATUS.md`) without explicit ownership.
5. Record all assumptions in the module’s JSON result, not only in chat.

### 3.2 Completion protocol

1. Run the module from `E:\kash-paper` using
   `E:\kash-paper\.venv\Scripts\python.exe`.
2. Save stdout/stderr to `logs/<task-id>.log`.
3. Run every task-specific checker in §6.
4. Write a compact output manifest in JSON: input paths/hashes or timestamps,
   fixed random seed, output paths, sample size, exclusions, warnings, and the
   key numerical results.
5. Update `FINDINGS.md` only if a reviewer can trace the exact sentence back to
   the module’s derived output. Update `STATUS.md` only after all checks pass.
6. Mark the `WORK_REGISTER.md` entry complete and list any limitations that
   remain.

### 3.3 Prohibited shortcuts

- Do not change numbers in Markdown, CSV, or figure labels by hand.
- Do not change a random seed after seeing an inconvenient result.
- Do not call a partial GPS match a complete route match.
- Do not compare `reality_check.plan_oneway_min` (pre-v3.4.5 snapshot) to
  post-correction `Cycle_Time_Min` as if they came from the same model state.
- Do not combine modelled and observed passenger figures, or convert GPS runs
  into boarding counts.
- Do not overwrite raw data, the v3.4.5 engine export, or caches without first
  making a documented regeneration plan.

---

## 4. Implementation sequence

The order is deliberate. Do not draft Results or Validation around results that
have not passed their QA gate.

### Phase 0 — Repository baseline and claim freeze

**Owner:** reproducibility lead.  
**Inputs:** current `bus-sathi-paper` repository, `STATUS.md`, `FINDINGS.md`,
engine v3.4.5 output.  
**Deliverables:** project skeleton, baseline manifest, claim ledger.

1. Confirm the new paper repository’s remote, default branch, and licence.
2. Add or repair: `README.md`, `requirements.txt`, `.gitignore`, `LICENSE`,
   `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`, and
   `logs/WORK_REGISTER.md`.
3. Add `analysis/run_all.py` that supports `--stage`, `--module`, `--quick`, and
   `--full`; it must never silently redownload data or invoke the engine.
4. Add `data/MANIFEST.md`: source, licence/provenance, whether redistributable,
   original location, expected filename, and checksum procedure for every raw
   input. Do not commit the WorldPop TIFF, OSM graph cache, or catchment GPKG.
5. Create `paper/CLAIM_LEDGER.md`. Each claim needs ID, exact wording, source
   module/file, statistic, denominator, population/route universe, caveat, and
   manuscript location.

**Acceptance gate P0:** a fresh clone plus locally provided third-party raw data
can run `python analysis/run_all.py --quick`; the README explains what cannot be
redistributed; `git status` contains no credentials or derived binary cache.

### Phase 1 — Repair observational GPS validation (`v04`)

**Owner:** runtime-validation analyst.  
**Files owned:** `analysis/v04_gps_validation.py`, `data/derived/v04_*`,
`paper/tables/table06*`, `logs/v04_*`.  
**Do not edit:** engine code or GPS raw files.

**Goal:** produce a defensible validation of the supply-side time and fleet
chain, not a demand validation and not a new engine version.

1. Create explicit analysis groups:
   - `matched_in_sample`: the five corridors whose GPS evidence informed
     v3.4.5’s measured-cycle corrections.
   - `partial_out_of_sample`: the nine partial corridor-route associations.
   - `all_corridors_descriptive`: all 18 profile rows, only for descriptive
     moving-speed/dwell evidence.
2. Preserve both model states in the corridor output:
   - `plan_oneway_min_pre_v345` from `reality_check.csv`.
   - `cycle_min_post_v345` and `fleet_post_v345` from the active plan.
   Never calculate an error mixing those columns.
3. Limit absolute route-length agreement to the five matched rows. For partial
   rows, report the mismatch as a matching limitation, never as route error.
4. Test moving speed only against City_Core multiplier 2.2. Results labelled
   Peri_Urban or Rural must be explicitly marked classification counterfactuals,
   since observations are Srinagar-area.
5. Estimate dwell two ways: ordinary least squares and WLS weighted by `n_runs`.
   Report coefficient, intercept, confidence intervals, R², N corridors, total
   runs, and the influence of the low-run C17 outlier. Do not infer a universal
   dwell model from 18 corridors.
6. Census cap binding across all 186 routes by route type. A route is at-cap if
   its absolute difference from `2 * Route_KM * cap_per_km` is within a declared
   floating tolerance (e.g. 0.01 min). Report counts and percentages.
7. Report both GPS coverage measures with their actual definitions:
   - `obs_frac`: fraction of sampled route grid cells hit by clean matched GPS
     runs; supports alignment-on-bus-used-road corroboration.
   - `observed_cover/status`: share of sampled route alignment near a recurring
     corridor; supports recurrent-service corroboration.
8. Implement a fleet-formula self-test before any fleet illustration:
   ```python
   operating = max(1, ceil(cycle_min / max(1, headway_min)))
   fleet = max(max(1, ceil(operating * 1.15)),
               1 if route_type == "Regional_District" else 2)
   ```
   Exclude SSCL because their fleet is overwritten with empirical CHALO counts.
   The test must reproduce every non-SSCL published fleet count exactly or stop.
9. If illustrating a sensitivity consequence, apply observed urban pace only to
   at-cap Urban/Peri_Urban routes, mark it as a bounded scenario, and retain
   Regional routes at cap because rural pace was not observed. Never present it
   as a revised fleet recommendation.

**Expected outputs:**

- `data/derived/v04_corridor_comparison.csv`
- `data/derived/v04_gps_validation.json`
- `data/derived/v04_fleet_illustration.csv` (optional, clearly labelled)
- `paper/tables/table06a_v04_runtime.{csv,md}`
- `paper/tables/table06b_v04_components.{csv,md}`
- `paper/tables/table06c_v04_cap_binding.{csv,md}`
- `paper/tables/table06d_v04_coverage_definitions.{csv,md}`

**Acceptance gate P1:**

- Fleet self-test has 0 mismatches for every eligible route.
- All five matched rows are labelled in-sample; no result claims independent
  validation from them.
- No out-of-sample result compares complete-route lengths on partial matches.
- Table notes state GPS cannot validate demand/ridership.
- Results reproduce F10–F12 or document any changed numbers with explanations.

### Phase 2 — Finish the index and hierarchy evidence

**Owner:** index analyst.  
**Files owned:** `a03_index_weights.py`, `a04_class_count.py`, their outputs,
Table 3 parameter material, Table 5 and Figure 6 inputs.

1. Run `a03_index_weights.py` without changing the predeclared ranges in
   `common.PARAMETERS`.
2. Report resident population and POI components separately before reporting
   CDI. Calculate Spearman/Pearson association between components; if high,
   state that the composite adds limited independent information.
3. Compare equal, entropy, and PCA first-component weights. Do **not** fabricate
   AHP weights; set `ahp_weights_derived=false` and state no panel convened.
4. Implement `a04_class_count.py` to evaluate 2–7 classes using Jenks GVF.
   Identify the elbow with a transparent rule, then compare route tiers from
   Jenks, quantiles, and k-means using Cohen’s kappa/confusion matrices.
5. Emit route-level scores, components, weights, assigned tier under every
   scheme, and agreement flags.

**Acceptance gate P2:** every 186-route output has an ID; all normalised values
are finite and within [0,1] to numerical tolerance; all reported weights sum to
1; the selected class count is justified by actual GVF values, not asserted.

### Phase 3 — Operational, equity, and network results

These analyses are required **only if their corresponding §5 subsection remains
in the manuscript**. If an input cannot support a result, remove or convert the
subsection to a stated limitation rather than creating a proxy without notice.

#### P3a: Network diagnostic and headway profile

Implement `a10_network_diagnostics.py` and `a05_headway_timeofday.py`.

- Calculate unique network length, route-km/unique-network-km ratio, link
  duplication, corridor overlap, and active-route typology.
- Parse `Hourly_Passenger_Count.csv` using `skiprows=1`; verify headers before
  calculating peak/off-peak/evening bands.
- Separate observed/current service evidence from planned headway standards.

**Gate:** report units, route universe, and whether a value describes permits,
active services, physical network links, or individual vehicles.

#### P3b: Access, spatial equity, and transfers

Implement `a11_coverage_accessibility.py`, `a12_equity_gini.py`, and
`a13_transfers.py`.

- Use the deduplicated network catchment for all network coverage totals.
- Compute Moran’s I on an explicitly described uncovered-population grid and
  spatial weights matrix.
- Calculate population-weighted accessibility Gini before/after only if both
  scenarios are defined on the same units and opportunity set.
- Produce a loss-and-gain map with a diverging colour scale centred exactly at
  zero. Name the number and locations of losers.
- Report 0/1/2+ transfer shares and a break-even transfer penalty; define the OD
  universe, transfer rule, wait-time assumption, and disconnected OD treatment.

**Gate:** any before/after result must preserve the same study boundary, grid,
population raster, POI set, and travel-time rule.

#### P3c: Fleet plausibility and operational scenarios

Implement `a06_deadhead.py`, `a07_load_factor.py`, `a14_cost_emissions.py`,
`a15_scenarios.py`, and optionally `a16_peer_regression.py` only if data source
quality is adequate.

- Deadhead must use explicit depots and routing assumptions; otherwise report
  a 5–12% literature-based sensitivity range, not a fabricated route value.
- Load factor must distinguish offered capacity from proxy demand and call the
  result an implied load factor, not observed occupancy.
- Cost/emissions must provide sources, price year, vehicle technology,
  electricity/fuel factors, operating-km assumptions, and scenario range.
- Scenarios must be pre-defined: do-nothing, efficiency-first, equity-first,
  balanced, and peak-tourist. All use the same baseline and report trade-offs.
- Peer regression requires a documented peer-city dataset and prediction
  interval. If this cannot be assembled from credible sources, omit the claim.

**Gate:** no output labelled “observed” may be a proxy, modelled, or scenario
quantity. Each scenario table includes its changed parameters and unchanged
parameters.

### Phase 4 — Uncertainty and independent validation channels

**Owner:** robustness analyst.  
**Files:** `a08_sensitivity_oat.py`, `a09_monte_carlo_sobol.py`,
`v01_spatial_crossval.py`, `v02_benchmark.py`.

1. OAT: sweep all ten predeclared parameters independently across the ranges in
   `common.PARAMETERS`; report output changes for coverage, class/tier, cycle
   time, fleet, and route disposition.
2. Monte Carlo: 5,000 deterministic-seed draws. Store sampled parameters,
   input distributions, rejected draws, and quantiles. Use the GPS-derived
   **measured pace prior from repaired P1**, not the raw OSRM time chain.
3. Sobol: state sampling design, base sample size, second-order setting, and
   confidence intervals. Do not quote an index without uncertainty.
4. V1 spatial cross-validation: use an independently sourced surface not used
   in CDI construction (e.g. OSM building footprint density). Confirm that the
   data were not reused as POIs or population.
5. V2 benchmark: label CHALO as a consistency check because of calibration
   circularity. Any external fleet/service benchmark needs source, year, and
   comparability adjustment.
6. V3: add a row marked “not performed; no expert panel convened.”
7. Compile Table 7 only after every channel has a result, exclusion reason, or
   non-performance declaration.

**Acceptance gate P4:** fixed random seed is written to every result JSON; no
uncertainty interval is quoted without its number of draws; Table 7 does not
silently turn an unavailable validation channel into a pass.

### Phase 5 — Figures and tables

**Owner:** publication-graphics analyst.  
**Rule:** generate figures from derived data, never screenshots or hand-edited
numbers. All plots need a script named `figXX_<name>.py`.

Required production set:

1. **Figure 1:** conceptual comparison of conventional demand-driven and
   open-data supply-side planning. No numeric claims.
2. **Figure 2:** literature taxonomy; depends on co-authors’ verified synthesis.
3. **Figure 3:** Kashmir Division boundary/admin units, population density, road
   hierarchy, opportunity density. Scale, north arrow, projection, data sources.
4. **Figure 4:** reproducible methodological workflow; show QA gates and where
   uncertainty enters.
5. **Figure 5:** network diagnosis: length distribution, overlap/duplication,
   physical-vs-permit unit distinction.
6. **Figure 6:** CDI distribution, components, weights, tier and threshold
   sensitivity.
7. **Figure 7:** revised outcome: do not use a false 342→207 Sankey. Use a
   truthful permit→distinct-corridor→active-service transition, planned headways,
   and cycle-cap composition.
8. **Figure 8 and 8b:** scenario trade-offs, fleet uncertainty, and tier
   stability.
9. **Accessibility difference map:** mandatory if any before/after accessibility
   claim remains. Centre colour scale at zero and show negative outcomes.

Required manuscript tables:

- T1 literature matrix (co-author source).
- T2 complete input-data inventory.
- T3 parameters and 10 QA gates.
- T4 existing-network profile.
- T5 top/bottom 20 route scores and sensitivity flags.
- T6 service standards and fleet, explicitly marked planned/illustrative where
  appropriate.
- T7 six-channel validation matrix.
- T8 policy instruments (co-author source).

**Figure/table QA gate P5:**

- Every number matches its CSV to specified rounding.
- Figure titles/captions state N, geography, time/reference version, and units.
- Every map has scale bar, north arrow, CRS/projection, source note, and a
  colour-blind-readable palette.
- Text stays readable at final single-column or double-column size.
- A second worker checks labels against `CLAIM_LEDGER.md` line by line.

### Phase 6 — Manuscript drafting

Draft in this order: §4 → §5 → §6 → §8 → Abstract. Put source-module IDs in
Markdown comments during drafting and remove them only in the final manuscript.

#### §4 Methodology — Prashant, 2,300 words

Must contain 4.1–4.10 from the brief and exactly define:

- study boundary and route/service universe;
- data conditioning and permit/corridor distinction;
- network-based catchment with `R=400 m`, non-zero snap-offset budget, and
  `tau=100 m` tail; state it is an upper bound on true walkshed;
- double-counting allocation;
- POI weighting alternatives (equal/entropy/PCA) and no AHP;
- resident population separate from tourism demand;
- CDI normalisation and thresholding;
- consolidation algorithm in Algorithm 1;
- Jenks/tier/headway logic;
- cycle and fleet equations including cap treatment;
- QA gates, OAT, Monte Carlo, Sobol design;
- all 14 equations, symbols, units, sources and assumptions.

Equation (8), the ridership plausibility estimate, must be labelled an
order-of-magnitude benchmark only; never forecast. The methodology must explain
the corrected research design, not merely narrate old engine functions.

#### §5 Results — Prashant + Misti, 2,400 words

Use the fixed order: diagnosis (5.1–5.3), design (5.4–5.7), evaluation
(5.8–5.12), stress test (5.13). Each result paragraph gives its N, denominator,
comparison universe, uncertainty, and policy meaning. Include adverse findings:
weak true consolidation, changed coverage, documented geometry inconsistency,
and locations harmed by any change. Do not claim a “materially better network”
unless the revised analyses demonstrate it against a defined counterfactual.

#### §6 Validation — Prashant + Avny + Krishnan, 900 words

Open with the convergent-validity logic and its limits. Present V1–V6 in Table
7. State V3 and field/boarding work are not performed. Put CHALO and GPS
circularity disclosures before the first favourable statistic. Explain that V4
observational GPS validates runtime/fleet components, not CDI/ridership.

#### §8 Conclusions — shared, 400 words

Six short paragraphs only: problem/approach; five quantified findings;
methodological contribution; policy contribution; fundable future research;
transferability. No new numbers or citations. Do not repeat stale headlines.

#### Abstract — shared, 250 words

Write last. Replace the obsolete Srinagar/342/207/39% narrative. The abstract
must not oversell route reduction and must not say validated against ridership.

**Draft QA gate P6:** every quantitative statement has a Claim Ledger ID;
every limitation in §6 appears consistently in Abstract/Results/Conclusion;
all co-author sections use Kashmir Division and v3.4.5 consistently.

### Phase 7 — Reproducibility, final review, and release

1. Create a clean virtual environment from pinned requirements.
2. Run the full analysis with raw data supplied according to the data manifest.
3. Run unit tests for catchment reproduction and fleet formula reproduction.
4. Regenerate all tables and figures from scratch; compare checksums or
   tolerances to committed publication outputs.
5. Run a claim audit, a numerical audit, and an editorial audit (see §6).
6. Use `git status`, secret scanning, and large-file checks before public push.
7. Tag a release only after final manuscript values, code, figures, tables, and
   README agree.

---

## 5. Task dependency order

```text
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

Do not run P4 before P1. Do not finalise Figures 6–8 or §5–§6 before their
upstream analyses pass.

---

## 6. Built-in checker plan

The checker must be independent of the author of a module wherever possible.
For each phase, assign a different model/person as checker. Checkers may fix
clear mechanical defects only after recording them; they must escalate a
scientific or scope decision rather than choosing a convenient answer.

### 6.1 Checker checklist A — data and scope integrity

Run before P1–P4 and again before release.

- [ ] All modules use 186 active records unless a documented subset is intended.
- [ ] Kashmir Division has exactly 10 districts and denominator 6,584,762/3.
- [ ] No manuscript or figure contains `342`, `207`, `39% reduction`, `95.7%`,
      `Srinagar Metropolitan City` as the study area, or `1,009` as the v3.4.5
      fleet headline, unless quoted explicitly as an obsolete prior claim.
- [ ] Route, permit, corridor, observed corridor, and active service are not
      conflated in a column name, caption, or sentence.
- [ ] Raw inputs are unchanged from their staged manifest.
- [ ] Large caches and third-party raw datasets are ignored by git.

Suggested commands:

```powershell
rg -n -i '342|207 routes|39%|95\.7%|Srinagar Metropolitan City|1,009' paper README.md
E:\kash-paper\.venv\Scripts\python.exe analysis\q01_data_quality.py
git status --short
git check-ignore -v data\cache\walk_graph.gpickle data\cache\catchments_network.gpkg
```

### 6.2 Checker checklist B — numerical reproducibility

Run after every analysis module.

- [ ] Module starts from declared raw/derived inputs and has no hard-coded result.
- [ ] `RANDOM_SEED=20260823` is used wherever randomness exists.
- [ ] Output CSVs have one row per declared unit and unique IDs where expected.
- [ ] JSON includes N, exclusions, parameter values/ranges, seed, version, and
      source-output paths.
- [ ] Derived manuscript tables regenerate byte-identically or differ only by
      declared nondeterministic metadata.
- [ ] Values in `FINDINGS.md`, figure labels, and table Markdown agree with the
      source CSV after rounding.

Suggested generic checks:

```powershell
E:\kash-paper\.venv\Scripts\python.exe -m compileall analysis
E:\kash-paper\.venv\Scripts\python.exe analysis\<module>.py
E:\kash-paper\.venv\Scripts\python.exe analysis\<module>.py
Get-FileHash data\derived\<output>.csv
```

If reruns differ, the checker must identify whether the cause is random seed,
input-order instability, overwritten cache, external API usage, or timestamp
metadata. Do not accept “approximately similar” without a declared tolerance.

### 6.3 Checker checklist C — GPS validation integrity

Run only after P1 and before any V4 wording is used in prose.

- [ ] The five GPS-corrected corridors are visibly marked `in_sample`.
- [ ] Partial matches are not used for whole-route length MAPE.
- [ ] Pre-v3.4.5 and post-v3.4.5 time values are never placed in the same error
      calculation.
- [ ] The fleet self-test has 0 mismatches on every non-SSCL eligible route.
- [ ] SSCL routes are excluded with an explanation.
- [ ] WLS and unweighted dwell analyses state N corridors and total runs.
- [ ] All coverage labels use the exact source definitions.
- [ ] Every validation table/caption says what GPS cannot validate.
- [ ] No claim of independent validation relies on CHALO calibration or the
      five measured-cycle correction routes.

Required stop condition: **any fleet self-test mismatch, ambiguous match class,
or mixed model-state comparison invalidates all fleet counterfactual outputs.**

### 6.4 Checker checklist D — methods and statistical validity

Run after P2–P4.

- [ ] CDI components are kept separate and all normalisation denominators are
      documented.
- [ ] Weight alternatives sum to one; no AHP result is fabricated.
- [ ] Class-count selection cites the actual GVF curve and kappa results.
- [ ] Sensitivity covers the ten predeclared parameters, not a selective subset.
- [ ] Monte Carlo contains exactly 5,000 accepted draws or reports why not.
- [ ] Sobol indices have sample design and uncertainty intervals.
- [ ] Every benchmark has an external source, year, comparability adjustment,
      and circularity disclosure where relevant.
- [ ] Before/after measures use identical population, boundary, and network
      measurement rules.

Required stop condition: **do not report a confidence interval, stability rate,
or validation “pass” unless the calculation, denominator, and threshold are
stored in a reproducible result file.**

### 6.5 Checker checklist E — figure, table, and prose audit

Run after P5–P6.

- [ ] Each figure is generated by version-controlled script; no manual chart
      editing or untraceable PowerPoint graphic remains.
- [ ] Figure/table captions state data version, N, unit, and key caveat.
- [ ] Maps use a true zero-centred diverging scale for differences and retain
      losses, not just gains.
- [ ] Paper has exactly the planned figure/table numbering, with no stale
      references.
- [ ] Every claim maps to `CLAIM_LEDGER.md`.
- [ ] Every limitation is stated consistently in §4, §5, §6, §7 (co-author
      handoff), §8, and Abstract where relevant.
- [ ] “Ridership,” “demand,” “population served,” “validation,” and “route
      reduction” are used with their precise definitions.
- [ ] Citations are complete, current, and support the sentence they follow.
- [ ] Results do not promise policy benefit that is not measured.

### 6.6 Checker checklist F — final release gate

All must be true before submission or public release:

- [ ] Fresh environment installs the pinned dependencies.
- [ ] Quick reproduction runs to completion; full reproduction instructions are
      tested with expected long runtimes documented.
- [ ] Unit tests cover Euclidean faithfulness and fleet formula reproduction.
- [ ] Manuscript, `FINDINGS.md`, all figures, all tables, and README contain the
      same final headline values.
- [ ] Data availability and licence status are correct for every source.
- [ ] No secrets, GPS raw personal data, Firestore keys, caches, or restricted
      inputs are publicly committed.
- [ ] Two independent checks sign off: numerical/reproducibility and
      manuscript/claim integrity.

---

## 7. Definition of done

The paper is ready for co-author integration only when:

1. P0–P7 have passed and their logs/outputs exist.
2. `FINDINGS.md` includes only QA-passed claims, including final F10–F12.
3. Every Prashant-owned section is drafted and has passed checker E.
4. The actual evidence is compatible with the final claims: an audited,
   open-data, uncertainty-aware planning framework—not a falsely precise,
   ridership-validated route-reduction success story.
5. The public repository can reproduce the publication outputs without editing
   raw data, engine code, or chart labels manually.

## 8. First five tasks to assign now

1. **P0/repository lead:** establish reproducibility files, work register, data
   manifest, claim ledger, and git hygiene.
2. **P1/GPS lead:** rewrite `v04_gps_validation.py` and regenerate Table 6.
3. **P1/checker:** independently run checker C and approve/reject V4 outputs.
4. **P2/index lead:** run `a03`, implement `a04`, and produce Figure 6/Table 5
   source data.
5. **P3b/access lead:** define valid before/after counterfactuals before writing
   accessibility, equity, or transfer code.

No worker should draft the Abstract, §5, §6, Figure 7, Figure 8, or Table 7
until their dependencies are marked complete in `logs/WORK_REGISTER.md`.
