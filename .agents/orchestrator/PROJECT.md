# Project: Kashmir Bus Route Rationalisation Paper Companion (E:\kash-paper)

## Architecture
- **Environment**: Python 3.14.2 at `E:\kash-paper\.venv` (CSV-only derived tables, no parquet).
- **Directory Boundaries**:
  - `analysis/`: Paper-specific analysis modules and runners.
  - `data/raw/`: Read-only staged input data (19 manifested files + census 2011).
  - `data/cache/`: Heavy precomputed caches (`walk_graph.gpickle`, `catchments_network.gpkg`, `osrm_responses.json`). Excluded from git.
  - `data/derived/`: Canonical CSV and JSON analysis outputs.
  - `paper/`: `CLAIM_LEDGER.md`, `FINDINGS.md`, `tables/`, `figures/`, and manuscript prose drafts (`draft/`).
  - `logs/`: `WORK_REGISTER.md` and module execution logs.
  - `.agents/`: Agent coordination metadata ONLY.
- **External Repositories (Strictly Read-Only)**: `E:\kash` (engine v3.4.5), `E:\bus-sathi-trace` (driver GPS).
- **Core Parameters**: `analysis/common.py` defines 11 predeclared parameters, fixed seed `20260823`, denominator `6,584,762`, UTM `EPSG:32643`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Repo Hygiene Files | README.md, requirements.txt, .gitignore, LICENSE, CITATION.cff, DATA_AVAILABILITY.md, REPRODUCIBILITY.md, logs/WORK_REGISTER.md | M0 | Survey 1, 2 |
| 2 | Reproducibility Runner | analysis/run_all.py supporting --stage, --module, --quick, --full without recomputing heavy caches | M0 | Survey 1, 2 |
| 3 | Raw Data Manifest | data/MANIFEST.md with sources, licenses, file sizes, SHA-256 hashes, and cache exclusion rules | M0 | Survey 1, 3 |
| 4 | Quantitative Claim Ledger | paper/CLAIM_LEDGER.md cataloging every statistic, denominator, universe, caveat, and paper location | M0 | Survey 1 |
| 5 | Repaired GPS Script (v04) | analysis/v04_gps_validation.py: explicit groupings (5 matched in-sample, 9 partial out-of-sample, 18 descriptive), split pre/post model runtime, length restricted to matched, dwell OLS/WLS, fleet formula self-test | M1 | Survey 1, 2, 3 |
| 6 | Derived GPS Datasets | data/derived/v04_corridor_comparison.csv and v04_gps_validation.json | M1 | Survey 1, 2, 3 |
| 7 | Publication Tables 6a-6d | paper/tables/table06a_*.{csv,md} through table06d_*.{csv,md} | M1 | Survey 1, 2, 3 |
| 8 | Formal Findings F10-F12 | Write findings F10 (sanity cap binds 90.9%), F11 (speed decomposition & dwell failure), F12 (physical vs service coverage) into paper/FINDINGS.md | M1 | Survey 1, 2, 3 |
| 9 | Index Weights Analysis | analysis/a03_index_weights.py: equal, entropy, PCA weights; resident pop vs POI separation; ahp_weights_derived=false | M2 | Survey 1, 2 |
| 10 | Objective Class Count | analysis/a04_class_count.py: Jenks GVF 2-7 classes, elbow identification, Cohen's kappa across Jenks/quantiles/kmeans | M2 | Survey 1, 2 |
| 11 | Hierarchy Tables & Figure 6 | Table 3 (parameters), Table 5 (top/bottom 20 routes), and Figure 6 source data | M2 | Survey 1, 2 |
| 12 | Network Diagnostics | analysis/a10_network_diagnostics.py: permit vs corridor decomposition, route-km : network-km, overlap heatmap, link duplication | M3 | Survey 1, 2 |
| 13 | Headway & Time-of-Day | analysis/a05_headway_timeofday.py: parse Hourly_Passenger_Count.csv with skiprows=1, peak/off-peak/evening headways | M3 | Survey 1, 2 |
| 14 | Coverage & Accessibility | analysis/a11_coverage_accessibility.py: deduplicated network catchments, Moran's I on uncovered surface, 15/20/35 min frequent coverage | M3 | Survey 1, 2 |
| 15 | Equity & Gini Analysis | analysis/a12_equity_gini.py: population-weighted accessibility Gini, identify and map losers | M3 | Survey 1, 2 |
| 16 | Transfer Analysis | analysis/a13_transfers.py: 0/1/2+ transfer shares, break-even transfer penalty | M3 | Survey 1, 2 |
| 17 | Deadhead Analysis | analysis/a06_deadhead.py: depot deadhead modeling (5-12% bus-hours) | M3 | Survey 1, 2 |
| 18 | Load Factor Evaluation | analysis/a07_load_factor.py: offered capacity vs proxy peak demand, logical gap evaluation | M3 | Survey 1, 2 |
| 19 | Cost & Emissions | analysis/a14_cost_emissions.py: cost per accessibility gained, emissions scenarios | M3 | Survey 1, 2 |
| 20 | Operational Scenarios | analysis/a15_scenarios.py: 5 scenarios (do-nothing, efficiency, equity, balanced, tourist) | M3 | Survey 1, 2 |
| 21 | Peer Regression | analysis/a16_peer_regression.py: buses/1,000 regressed on population & density with prediction intervals | M3 | Survey 1, 2 |
| 22 | OAT Parameter Sweeps | analysis/a08_sensitivity_oat.py: one-at-a-time sweeps across all 10 predeclared parameters | M4 | Survey 1, 2 |
| 23 | Monte Carlo Simulation | analysis/a09_monte_carlo_sobol.py: 5,000 draws using v04 measured pace prior, fleet 90% CI, tier stability > 80% | M4 | Survey 1, 2 |
| 24 | Sobol Global Sensitivity | First- and total-order Sobol indices with bootstrap confidence intervals | M4 | Survey 1, 2 |
| 25 | Spatial Cross-Validation V1 | analysis/v01_spatial_crossval.py: OSM building-footprint density vs demand index (target rho > 0.6) | M4 | Survey 1, 2 |
| 26 | Benchmark Check V2 | analysis/v02_benchmark.py: CHALO consistency check (+/- 15%) with explicit circularity disclosure | M4 | Survey 1, 2 |
| 27 | V3 Non-Performance Doc | Formal documentation of V3 expert AHP/Delphi panel as not performed | M4 | Survey 1, 2 |
| 28 | Validation Table 7 | paper/tables/table07_validation_matrix.{csv,md}: 6 channels, test, statistic, threshold, result, verdict | M4 | Survey 1, 2 |
| 29 | Publication Figures 1-8b | analysis/fig01_*.py through fig08b_*.py rendering vector/PNG publication figures to paper/figures/ | M5 | Survey 1, 2 |
| 30 | Publication Tables 1-8 | Clean, verified Markdown and CSV tables in paper/tables/ matching source data and rounding rules | M5 | Survey 1, 2 |
| 31 | Manuscript §4 Methodology | paper/draft/section4_methodology.md (2,300 words, sole owner: Equations 1-14, Algorithm 1, walk catchments, consolidation, Jenks tiers, cycle/fleet formulas) | M6 | Survey 1 |
| 32 | Manuscript §5 Results | paper/draft/section5_results.md (2,400 words: diagnosis, design, evaluation, stress tests, each closing with italicized policy sentence) | M6 | Survey 1 |
| 33 | Manuscript §6 Validation | paper/draft/section6_validation.md (900 words: convergent-validity framework, V1-V6 reporting, V3 not performed, CHALO circularity) | M6 | Survey 1 |
| 34 | Manuscript §8 & Abstract | paper/draft/section8_conclusions.md (400 words, 6 structured paragraphs) and abstract.md (250 words, zero legacy metrics) | M6 | Survey 1 |
| 35 | Manuscript Claim Ledger Mapping | Verify that every single quantitative statistic in draft prose cites a specific CLAIM_LEDGER.md ID | M6 | Survey 1 |
| 36 | Checker A Audit | Scope and data integrity audit: 10 districts, 6,584,762 denominator, zero legacy numbers (342, 207, 39%, 95.7%, 1009, SMC), cache exclusions | M7 | Survey 1 |
| 37 | Checker B Audit | Numerical reproducibility: random seed 20260823, deterministic outputs, byte/floating match | M7 | Survey 1 |
| 38 | Checker C Audit | GPS validation audit: fleet formula self-test 0 mismatches, in-sample labelling, no length MAPE on partials | M7 | Survey 1 |
| 39 | Checker D Audit | Methodological and statistical rigour: weights sum to 1.0, V3 not performed, MC 5,000 draws with pace prior, Sobol CIs | M7 | Survey 1 |
| 40 | Checker E Audit | Manuscript claims audit: claim ledger traceability, zero "validated against ridership", zero false consolidation | M7 | Survey 1 |
| 41 | Checker F Audit | Clean reproduction: python analysis/run_all.py --quick runs cleanly from .venv, unit tests pass 0 errors | M7 | Survey 1 |
| 42 | Tier 5 Adversarial Hardening | White-box stress testing, edge case audits, adversarial test suite | M7 | Survey 1 |
| 43 | E2E Opaque-Box Test Suite | TEST_INFRA.md and independent multi-tier opaque-box test runner publishing TEST_READY.md | E2E_TRACK | Survey 1 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M0 | Baseline Setup & Manifests | Hygiene files, run_all.py, data/MANIFEST.md, paper/CLAIM_LEDGER.md | none | IN_PROGRESS |
| M1 | Repaired GPS Validation (v04) | Rewrite v04_gps_validation.py, fleet self-test, Tables 6a-6d, update FINDINGS.md F10-F12 | M0 | PLANNED |
| M2 | Index Weights & Hierarchy | a03_index_weights.py, a04_class_count.py, Tables 3 & 5, Fig 6 source | M0 | PLANNED |
| M3 | Network Diagnostics & Scenarios | a10, a05, a11, a12, a13, a06, a07, a14, a15, a16 | M1, M2 | PLANNED |
| M4 | Uncertainty & Multi-Channel Validation | a08 (OAT), a09 (Monte Carlo + Sobol with v04 pace prior), v01, v02, V3 doc, Table 7 | M1, M2 | PLANNED |
| M5 | Publication Figures & Tables | Scripts fig01-fig08b, final PNG/vector figures, final Tables 1-8 | M1, M2, M3, M4 | PLANNED |
| M6 | Manuscript Drafting | Prashant sections: Abstract, §4, §5, §6, §8, mapped to CLAIM_LEDGER.md | M1, M2, M3, M4, M5 | PLANNED |
| M7 | Release Audit & Hardening | Checkers A-F, E2E test verification, Tier 5 adversarial hardening | M0-M6, TEST_READY | PLANNED |
| E2E | E2E Testing Track | TEST_INFRA.md, Tiers 1-4 opaque-box tests, TEST_READY.md | none (parallel) | IN_PROGRESS |

## Interface Contracts
### a02_catchments.csv -> a03_index_weights.py & a04_class_count.py
- Input: `data/derived/a02_catchments.csv` (186 rows: route_id, route_type, length_km, pop_served_net, poi_high, poi_med, poi_seas).
- Output: `data/derived/a03_index_weights.csv` and `a03_weights_comparison.json`.
- Output: `data/derived/a04_class_count.json`.

### v04_gps_validation.py -> a09_monte_carlo_sobol.py
- Output: `data/derived/v04_gps_validation.json` providing empirical speed / pace prior distribution parameters:
  - `urban_moving_pace_mean_minkm`, `urban_moving_pace_sd_minkm`, `urban_dwell_intercept_min`, `urban_dwell_slope_minkm`.
- Consumer: `a09_monte_carlo_sobol.py` uses this prior instead of OSRM default multipliers.

### Analysis Modules -> Figures & Tables
- All figure scripts (`figXX_*.py`) read EXCLUSIVELY from `data/derived/*.csv` or `data/derived/*.json`. No direct raw data reads or engine invocation.
- All manuscript tables (`tableXX_*.csv`, `tableXX_*.md`) match derived data with explicit rounding declarations.

### CLAIM_LEDGER.md -> Manuscript Prose
- Format: `[CL-XX]` tags embedded in drafting notes or mapping table.
- Guarantee: Every quantitative statement in §4, §5, §6, §8, and Abstract is traced to a specific ledger entry.

## Code Layout
- `analysis/common.py`: Shared constants, paths, statistical functions (`gini`, `entropy_weights`, `goodness_of_variance_fit`), and table/result writers.
- `analysis/run_all.py`: Orchestrator CLI runner supporting `--stage`, `--module`, `--quick`, `--full`.
- `analysis/*.py`: Independent analysis and figure-generating scripts.
- `tests/`: Unit and integration test suite.
- `logs/WORK_REGISTER.md`: Task ownership log preventing concurrent write conflicts.
- `paper/CLAIM_LEDGER.md`: Single source of truth for all quantitative claims.
