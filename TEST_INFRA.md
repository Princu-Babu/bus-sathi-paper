# Test Infrastructure Specification: Kashmir Bus Route Rationalisation Paper Companion (E:\kash-paper)

## 1. Test Philosophy

### 1.1 Opaque-Box and Requirement-Driven
The testing track for `E:\kash-paper` operates strictly on **opaque-box principles**. Tests verify observable system behavior, published artifacts, schema compliance, interface contracts, mathematical properties, and domain invariants. They are entirely decoupled from internal module implementations, private helper functions, and ephemeral scripting details. If an internal algorithm or script is refactored, tests must pass without modification as long as the interface contract and domain requirements hold.

### 1.2 Non-Negotiable Research Contract Adherence
Every test suite directly enforces the non-negotiable research contract established in `ORIGINAL_REQUEST.md` and `PROJECT.md`:
1. **Frozen Operational Baseline (v3.4.5):** 644 engine rows (614 permits + 30 SSCL electric routes), exactly 186 active services, stated fleet of 1,011 buses, and WorldPop 2026 UN-adjusted denominator of 6,584,762 (or 6,584,763). Tests fail immediately if an engine v4 is implied or baseline counts deviate.
2. **Kashmir Division Scope (10 Districts):** The study area encompasses the 10 districts of Kashmir Division only (Anantnag, Bandipore, Baramulla, Budgam, Ganderbal, Kulgam, Kupwara, Pulwama, Shopian, Srinagar). Any legacy framing of Srinagar Metropolitan City (SMC) or obsolete metrics (342 permits, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet) triggers automated test failure.
3. **GPS Supply-Side Scope Boundary:** Observational app GPS validates the supply-side operational chain (geometry, speed, runtime, cycle time, fleet requirements). App GPS carries zero ridership, boarding, or latent demand signal. Tests strictly forbid any claim of "validated against ridership".
4. **No Fabricated Data:** Field enumeration surveys and AHP/Delphi expert panels were not collected. Validation channel V3 must be reported as "not performed". Any synthetic or simulated AHP/survey data disguised as empirical triggers test failure.
5. **Circularity Disclosure:** CHALO aggregate ridership calibrates the engine's plausibility term and serves as benchmark V2 (consistency check, not independent validation). The 5 GPS-matched corridors were utilized by v3.4.5 for cycle re-anchoring and must be tagged `in_sample`.
6. **Network Catchment Deduplication:** Residential WorldPop catchment populations across routes overlap significantly. Network totals must reflect only the deduplicated union; summing per-route catchments is strictly prohibited.
7. **Read-Only External Sources:** External repositories (`E:\kash` and `E:\bus-sathi-trace`) and heavy regenerable caches (`data/cache/`) are protected; tests verify they remain unmutated and excluded from git tracking.

### 1.3 Test Independence and Determinism
- **Isolation:** Every test sets up its own state, executes deterministically, and produces zero side effects on raw data or other tests.
- **Fixed Random Seed:** All stochastic methods (Monte Carlo, bootstrap CIs, Sobol sampling) must use `RANDOM_SEED = 20260823`.
- **Reproducibility:** Outputs must match byte-identically or within declared floating-point tolerances (`rel_tol=1e-4` unless otherwise specified).
- **Anti-Pattern Prohibition:** Facade tests that assert tautologies (`assert True`) or tests designed to mirror broken code rather than the authoritative specification are strictly forbidden.

---

## 2. Feature Inventory Mapping to Tiers 1–4

Each of the 43 project features defined in `PROJECT.md` is mapped to four testing tiers ensuring multi-layered verification:

| Feature # | Feature Name | Tier 1: Unit & Smoke | Tier 2: Component Integration | Tier 3: System & Pairwise | Tier 4: E2E Scenarios |
|---|---|---|---|---|---|
| **F01** | Repo Hygiene Files | Verify file existence, non-empty, formatting | Cross-reference citations, licenses, and data availability | Git ignore & work register race condition checks | Scenario 1: Clean workspace init & hygiene gate |
| **F02** | Reproducibility Runner | CLI argument parsing (`--stage`, `--quick`, `--full`) | Runner invokes modules without invoking external engine | Stage dependency sequence and dry-run execution | Scenario 1: Quick reproduction run (`run_all.py --quick`) |
| **F03** | Raw Data Manifest | Checksum validator, file existence check | Manifest hash matching on staged `data/raw/*` | Missing file / corrupted checksum error handling | Scenario 2: Data integrity & manifest audit |
| **F04** | Quantitative Claim Ledger | Schema validation, unique Claim IDs (`CL-XX`) | Cross-check claim IDs with `paper/FINDINGS.md` | Audit numerical values against derived CSV/JSON | Scenario 2: Zero legacy metric enforcement |
| **F05** | Repaired GPS Script (v04) | OLS/WLS dwell regression math, pace calculations | In-sample (5) vs out-of-sample (9) grouping integrity | Corridor speed decomposition under extreme pace inputs | Scenario 3: Supply-side GPS validation pipeline |
| **F06** | Derived GPS Datasets | CSV schema check, null checks, unique corridor IDs | Join validation with active plan (`Rationalised_Routes`) | Floating point precision & tolerance verification | Scenario 3: Supply-side GPS validation pipeline |
| **F07** | Publication Tables 6a-6d | Table column checks, Markdown/CSV synchronization | Cell-by-cell numerical consistency with derived data | Header formatting and caveat footnotes validation | Scenario 3: Supply-side GPS validation pipeline |
| **F08** | Formal Findings F10-F12 | Text parser for F10-F12 assertions in FINDINGS.md | Consistency with Table 6 values and GPS JSON results | Boundary condition verification for speed sanity caps | Scenario 3: Supply-side GPS validation pipeline |
| **F09** | Index Weights Analysis | Shannon entropy math, min-max normalizer unit test | Input handoff from `a02_catchments.csv` | Pairwise weight permutations (Equal, Entropy, PCA) | Scenario 4: Accessibility & index weight scenario |
| **F10** | Objective Class Count | Jenks GVF unit tests, Cohen's kappa math | JSON output schema (`a04_class_count.json`) | Class count sweeps (k=2..7), elbow point identification | Scenario 4: Route hierarchy & tier stability |
| **F11** | Hierarchy Tables & Fig 6 | Table 3 & Table 5 column structure & sorting | Cross-module linking between a03/a04 and tables | Agreement across ranking methods (Jenks vs Quantiles) | Scenario 4: Route hierarchy & tier stability |
| **F12** | Network Diagnostics | Route-km to network-km ratio, permit counting math | Decomposition of 614 permits into 157 corridors | Overlap metric boundary analysis (0.0 to 1.0) | Scenario 2: Network structure & permit audit |
| **F13** | Headway & Time-of-Day | Parser tests for `Hourly_Passenger_Count.csv` (skiprows=1) | Headway assignment per time-of-day band | Headway boundary clipping (max 50 min rural, 35 min urban) | Scenario 5: Operational scheduling scenario |
| **F14** | Coverage & Accessibility | Catchment buffer math, spatial CRS validation | Handoff from walk graph to catchment polygon union | Spatial Moran's I on uncovered populations | Scenario 4: Spatial accessibility & walk walkshed |
| **F15** | Equity & Gini Analysis | Population-weighted Gini calculation unit tests | Merging route accessibility with district census | Lorenz curve integration boundary tests (Gini in [0, 1]) | Scenario 4: Equity & accessibility scenario |
| **F16** | Transfer Analysis | Dijkstra/BFS transfer path counting logic | Integration with active network topology | Transfer penalty sensitivity (break-even transfer cost) | Scenario 5: Network connectivity & transfer audit |
| **F17** | Deadhead Analysis | Depot distance calculation unit tests | Integration with terminal locations and fleet counts | Deadhead percentage constraint sweep (5% to 12%) | Scenario 5: Operational cost & deadhead audit |
| **F18** | Load Factor Evaluation | Capacity calculation: `VEHICLE_CAPACITY * trips` | Peak demand proxy vs offered capacity checks | Overcrowding threshold flags and demand-gap boundaries | Scenario 5: Fleet plausibility & load factor audit |
| **F19** | Cost & Emissions | Cost per km formula, emission factor unit tests | Linking fleet, daily km, and vehicle class counts | Fuel price and electrification sensitivity bounds | Scenario 5: Environmental & financial sustainability |
| **F20** | Operational Scenarios | Scenario parameter parser (5 predefined scenarios) | Route fleet modifications across the 5 policy packages | Trade-off matrix consistency across efficiency vs equity | Scenario 5: Five-scenario policy comparison |
| **F21** | Peer Regression | Ordinary Least Squares regression unit test | External city benchmark dataset integration | Prediction interval calculation & outlier leverage check | Scenario 5: Peer benchmark validation |
| **F22** | OAT Parameter Sweeps | Parameter boundary parsing (10 predeclared parameters) | Sweep runner interaction with core evaluation functions | Parameter grid evaluation, monotonicity verification | Scenario 5: Robust decision & uncertainty pipeline |
| **F23** | Monte Carlo Simulation | Random sampling distribution generators (unif, tri) | Ingestion of v04 empirical speed/pace priors | 5,000 accepted sample validation, convergence check | Scenario 5: Robust decision & uncertainty pipeline |
| **F24** | Sobol Global Sensitivity | Saltelli sampling matrix generator unit test | SALib integration with model evaluation pipeline | First-order ($S_i$) and total-order ($S_{Ti}$) index sum checks | Scenario 5: Robust decision & uncertainty pipeline |
| **F25** | Spatial Cross-Val V1 | Spearman/Pearson correlation unit tests | OSM building footprint density vs demand index CDI | Density threshold boundary checks ($\rho > 0.60$) | Scenario 4: Convergent validation channel V1 |
| **F26** | Benchmark Check V2 | Benchmark ratio comparison unit test ($1.0 \pm 0.15$) | CHALO ridership dataset integration with demand index | Circularity disclosure assertion in output metadata | Scenario 4: Convergent validation channel V2 |
| **F27** | V3 Non-Performance Doc | Assertion that V3 is marked `performed: false` | JSON schema check in `table07_validation_matrix` | Verification that no synthetic survey data exists | Scenario 2: Integrity & non-performance audit |
| **F28** | Validation Table 7 | Matrix table schema and 6-channel completeness | Integration of V1-V6 channel results into single table | Pass/fail threshold verdict consistency checks | Scenario 4 & 5: Multi-channel validation gate |
| **F29** | Publication Figures 1-8b | Image / vector format check (PNG, SVG/PDF) | Figure script execution reading only `data/derived/*` | Aspect ratio, resolution (>=300 DPI), and label checks | Scenario 1: Publication graphics generation |
| **F30** | Publication Tables 1-8 | CSV & Markdown table structure and headers | Exact rounding match against derived data sources | Alignment check between manuscript citations & tables | Scenario 1: Publication tables generation |
| **F31** | Manuscript §4 Method | Equation and algorithm parameter symbol parser | Consistency between declared constants and common.py | Word count and section completeness check | Scenario 2: Manuscript §4 reproducible methods |
| **F32** | Manuscript §5 Results | Text regex scanner for quantitative claims | Claim ledger cross-referencing for all statistics | Check for mandatory italicized policy takeaway sentences | Scenario 2: Manuscript §5 claim traceability |
| **F33** | Manuscript §6 Validation | Text audit for circularity disclosures and GPS scope | Cross-reference with Table 7 validation results | Check for explicit statement of V3 non-performance | Scenario 2: Manuscript §6 validation integrity |
| **F34** | Manuscript §8 & Abstract | Word count bounds (Abstract <= 250, §8 <= 400) | Check for 6 structured paragraphs in §8 | Zero legacy metrics scanner across Abstract & §8 | Scenario 2: Abstract & Conclusions release gate |
| **F35** | Claim Ledger Mapping | Tag format validator (`[CL-XX]`) in markdown files | Completeness: 100% of prose numbers map to ledger | Unmapped statistic detector across all draft files | Scenario 2: Claim ledger audit |
| **F36** | Checker A Audit | Test suite: 10 districts, 6,584,762 pop, 186 active | Automated regex scanner across entire repository | Verification of cache exclusions in `.gitignore` | Scenario 2: Checker A scope & data audit |
| **F37** | Checker B Audit | Deterministic hash comparison on rerun CSV outputs | Random seed enforcement across all stochastic modules | Verification of CSV-only derived tables (no parquet) | Scenario 1: Checker B numerical reproducibility |
| **F38** | Checker C Audit | Fleet self-test unit assertion on individual routes | Complete fleet self-test across all 156 non-SSCL routes | In-sample tagging check and length MAPE restriction | Scenario 3: Checker C GPS validation audit |
| **F39** | Checker D Audit | Weight sum assertion (`sum(weights) == 1.0`) | Monte Carlo sample count check ($N = 5,000$) | Sobol confidence interval verification | Scenario 5: Checker D methodological rigour |
| **F40** | Checker E Audit | Prohibited phrase scanner ("validated against ridership") | Claim ledger trace validation for every headline claim | Zero-centred diverging scale verification on maps | Scenario 2: Checker E manuscript claims audit |
| **F41** | Checker F Audit | Quick reproduction clean run check | Dependency installation and Python version check | Full release readiness verification | Scenario 1: Checker F release gate |
| **F42** | Adversarial Hardening | Boundary value injection (NaNs, extreme lengths) | Malformed CSV / JSON recovery testing | Resource exhaustion and concurrent execution protection | Scenario 5: Adversarial robustness audit |
| **F43** | E2E Test Suite | Test runner execution and exit code verification | Harness execution across all checker modules | Coverage threshold verification across all 4 tiers | Scenario 1-5: Complete E2E testing gate |

---

## 3. Test Architecture

### 3.1 Runner and Environment
- **Python Environment:** Python 3.14.2 at `E:\kash-paper\.venv\Scripts\python.exe`
- **Test Framework:** `pytest >= 9.0`
- **Execution Command:**
  ```powershell
  # Run entire test suite
  E:\kash-paper\.venv\Scripts\pytest.exe tests/ -v

  # Run specific tiers
  E:\kash-paper\.venv\Scripts\pytest.exe tests/unit/ -v
  E:\kash-paper\.venv\Scripts\pytest.exe tests/integration/ -v
  E:\kash-paper\.venv\Scripts\pytest.exe tests/system/ -v
  E:\kash-paper\.venv\Scripts\pytest.exe tests/e2e/ -v

  # Run Checkers A-F audit suite
  E:\kash-paper\.venv\Scripts\pytest.exe tests/checkers/ -v
  ```

### 3.2 Pass/Fail Semantics
1. **Exit Codes:**
   - `0`: All tests passed. Release criteria satisfied.
   - `1`: One or more tests failed. Execution blocked; issues must be escalated or repaired.
   - `2`: Interrupted execution or syntax error in test files.
2. **Tolerance Semantics:**
   - Integer counts (routes, permits, districts, fleet counts): **Exact integer match** (`assert actual == expected`).
   - Floating-point calculations: `math.isclose(actual, expected, rel_tol=1e-4)` or `pytest.approx(expected, rel=1e-4)`.
   - String integrity: Exact case-sensitive matching for route IDs, district names, and actions; case-insensitive regex for prohibited legacy claims.
3. **Hard Stop Invariants (Instant Failure):**
   - Any occurrence of uncontextualized legacy figures: `342`, `207 routes`, `39% route reduction`, `95.7% coverage`, `1,009 fleet`, or `Srinagar Metropolitan City` framing.
   - Any claim of ridership validation (e.g. "validated against ridership").
   - Any fleet formula self-test mismatch on eligible non-SSCL routes.
   - Any Parquet or binary table files committed in `data/derived/` (CSV-only derived tables enforced).

### 3.3 Directory Layout
```text
tests/
├── conftest.py                   # Central test fixtures, paths, data loaders, helper assertions
├── checkers/                     # Checkers A-F Auditor Release Suite
│   ├── test_checker_a_scope.py   # Scope & Data Integrity (10 districts, 6,584,762 pop, no legacy metrics)
│   ├── test_checker_b_numerical.py# Numerical Reproducibility (seed, CSV-only, deterministic tables)
│   ├── test_checker_c_gps.py     # GPS Validation & Fleet Self-Test (0 mismatches across non-SSCL)
│   ├── test_checker_d_methods.py # Methodological Rigour (weights sum to 1, V3 unperformed, 5k MC)
│   ├── test_checker_e_manuscript.py# Manuscript Claims & Ledger Audit (traceability, zero false claims)
│   └── test_checker_f_release.py # Clean Reproduction & Release Gate (venv clean run, no leaked keys)
├── unit/                         # Tier 1: Smoke & Baseline Unit Tests (>= 5 cases per feature)
│   ├── test_common_math.py       # Gini, entropy weighting, minmax, GVF calculation units
│   ├── test_fleet_formula.py     # Sizing formula boundary cases, headway rounding, floors
│   └── test_schemas.py           # Raw and derived CSV/JSON schema contracts
├── integration/                  # Tier 2: Component Integration & Interface Contracts
│   ├── test_catchment_pipeline.py# a02 catchments -> a03 weights / a04 class count contracts
│   ├── test_gps_pipeline.py      # v04 GPS validation -> a09 Monte Carlo speed prior contract
│   └── test_table_consistency.py # Derived data -> publication tables synchronization
├── system/                       # Tier 3: Pairwise Combinations & Boundary Stress Tests
│   ├── test_pairwise_params.py   # Pairwise parameter coverage across 10 predeclared parameters
│   └── test_boundary_stress.py   # Zero population, extreme road lengths, singular matrices
└── e2e/                          # Tier 4: Real-World Application Scenarios (>= 5 realistic workflows)
    ├── test_scenario_quickrun.py # Scenario 1: Quick reproduction run and pipeline sanity
    ├── test_scenario_baseline.py # Scenario 2: Data & scope invariant audit
    ├── test_scenario_gps_supply.py# Scenario 3: Supply-side GPS & fleet sizing validation
    ├── test_scenario_walkshed.py # Scenario 4: Spatial accessibility & walk catchment overstatement
    └── test_scenario_uncertainty.py# Scenario 5: Multi-channel validation & Monte Carlo uncertainty
```

---

## 4. Real-World Application Scenarios (Tier 4)

### Scenario 1: Quick Reproduction Run & Pipeline Sanity
- **Objective:** Verify that the paper's companion reproduction pipeline (`analysis/run_all.py --quick`) executes cleanly from a fresh virtual environment without errors, without calling external engines, and without recomputing heavy geometric caches (`walk_graph.gpickle`).
- **Execution:** Invokes `python analysis/run_all.py --quick` and verifies exit code 0, standard log emission in `logs/`, and non-empty output artifacts.
- **Verification Assertions:**
  - Zero execution errors or unhandled exceptions.
  - Runtime completes within declared quick budget (< 3 minutes).
  - Derived artifacts generated or validated: `q01_data_quality.json`, `a02b_faithfulness.csv`, `v04_gps_validation.json`.

### Scenario 2: Baseline Scope and Data Invariant Verification
- **Objective:** Verify absolute compliance of all input and intermediate datasets with the Kashmir Division research scope.
- **Execution:** Loads `data/raw/Rationalised_Routes_Kashmir_v3.csv`, `data/raw/existing-routes.csv`, and census data.
- **Verification Assertions:**
  - Total plan records = 644 (614 permits + 30 SSCL routes).
  - Active routes = 186; Merged routes = 458.
  - Stated baseline fleet = 1,011 buses.
  - Kashmir Division contains exactly 10 districts with population denominator 6,584,762 (or 6,584,763).
  - Corridors retained: 156 of 157 distinct corridors (99.4% retention; true consolidation is 0.2 pp, change-of-unit is 71.0 pp).
  - Zero occurrences of obsolete strings across codebase, manifests, and drafts.

### Scenario 3: Observational GPS Validation & Fleet Self-Test
- **Objective:** Validate the supply-side operational chain using driver GPS records while preventing methodological leakage.
- **Execution:** Executes the fleet formula self-test and checks GPS corridor classifications.
- **Verification Assertions:**
  - Fleet formula self-test achieves **exactly 0 mismatches** across all 156 non-SSCL active routes:
    $$\text{operating} = \max\left(1, \left\lceil \frac{\text{cycle\_min}}{\max(1, \text{headway\_min})} \right\rceil\right)$$
    $$\text{fleet} = \max\left(\max(1, \lceil \text{operating} \times 1.15 \rceil), 1 \text{ if Regional\_District else } 2\right)$$
  - 30 SSCL routes (`SSCL-01` to `SSCL-30`) are explicitly excluded from formula self-test with contractual documentation.
  - Exactly 5 corridors labeled `matched` / `in_sample` (used in v3.4.5 cycle re-anchoring).
  - Exactly 9 corridors labeled `partial` / out-of-sample.
  - Length error MAPE evaluated strictly on the 5 matched corridors; partial matches strictly excluded.
  - Dwell time estimation reports both unweighted OLS and run-weighted WLS regressions with explicit sample counts ($N$ corridors and total runs).

### Scenario 4: Spatial Accessibility & Catchment Overstatement (Finding F8)
- **Objective:** Verify the central methodological result regarding Euclidean vs. realistic network walk catchments.
- **Execution:** Reads `data/derived/a02_catchments.csv` and `data/derived/a02_network_catchments.json`.
- **Verification Assertions:**
  - Median per-route Euclidean population overstatement is $\approx 37.4\%$ (IQR 30.5%–41.7%).
  - At least 180 of 186 routes exhibit $> 25\%$ Euclidean overstatement.
  - Network-wide deduplicated population coverage drops from $\approx 35.5\%$ (Euclidean 2,339,394) to $\approx 24.2\%$ (network walk 1,592,847), an overstatement of $\approx 31.9\%$.
  - Stop snapping diagnostics: $> 99\%$ of stops snap within 50m of the walk network; median snap distance $\approx 11.0\text{ m}$.

### Scenario 5: Uncertainty Analysis and Multi-Channel Decision Robustness
- **Objective:** Verify the complete uncertainty quantification pipeline and multi-channel validation matrix.
- **Execution:** Reads parameter definitions, Monte Carlo outputs, and Table 7 validation matrix.
- **Verification Assertions:**
  - All 10 predeclared parameters swept in One-At-a-Time (OAT) sensitivity with documented intervals.
  - Monte Carlo simulation executes with exactly 5,000 accepted draws utilizing the empirical GPS pace prior.
  - Sobol sensitivity analysis calculates both first-order ($S_i$) and total-order ($S_{Ti}$) indices with bootstrap confidence intervals.
  - Validation Channel V1: OSM building footprint density correlates with demand index ($\rho > 0.60$).
  - Validation Channel V2: CHALO ridership benchmark consistency check within $\pm 15\%$ with circularity disclosure.
  - Validation Channel V3: Expert AHP/Delphi panel documented explicitly as unperformed.

---

## 5. Coverage Thresholds

To guarantee rigorous quality assurance, the testing suite enforces the following quantitative coverage thresholds:

1. **Tier 1 (Unit & Smoke):**
   - $\ge 5$ distinct unit test cases / assertion vectors per feature.
   - 100% coverage of mathematical functions in `analysis/common.py` (`gini`, `entropy_weights`, `minmax`, `goodness_of_variance_fit`).
   - 100% schema validation of all 19 raw staged files and all derived CSV tables.

2. **Tier 2 (Integration & Interface Contracts):**
   - $\ge 5$ integration assertions per module interface boundary.
   - Explicit validation of inter-module data handoffs (e.g. `a02` catchments $\to$ `a03`/`a04`; `v04` $\to$ `a09`).
   - Publication table cell-to-source synchronization tests.

3. **Tier 3 (System & Pairwise Testing):**
   - Complete pairwise (all-pairs) coverage across the 10 predeclared parameters ($10 \times 10$ combinatorial interactions).
   - Boundary stress tests covering edge values (zero population, extreme road lengths, maximum headway, zero dwell).

4. **Tier 4 (E2E Application Scenarios):**
   - $\ge 5$ comprehensive end-to-end operational scenarios exercising realistic workflows.
   - Complete execution of the quick reproduction pipeline.

5. **Checkers A–F Release Audit Suite:**
   - 100% pass rate across Checkers A through F checklists. Zero warnings, zero skips on critical invariants, zero uncontextualized legacy metrics.
