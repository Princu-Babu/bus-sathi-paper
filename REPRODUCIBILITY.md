# Reproducibility Guide

**Paper Title:** *Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*  
**Target Journal:** *Transport Policy*  
**Repository:** `E:\kash-paper`  
**Fixed Deterministic Seed:** `20260823`  
**Reference Environment:** Python 3.14.2 on Windows 11 / x86_64

This guide provides complete, step-by-step instructions to replicate every analysis, table, figure, and quantitative claim in the manuscript from a clean environment.

---

## 1. System Requirements & Prerequisites

### Hardware Requirements
- **CPU:** Quad-core 64-bit x86_64 or ARM64 processor (8+ cores recommended for parallel network walk catchments).
- **RAM:** Minimum 8 GB; 16 GB recommended when building the full OpenStreetMap pedestrian network graph from scratch.
- **Disk Space:** 5 GB free space (to store input datasets, network graph caches, and derived outputs).

### Software Requirements
- **Operating System:** Windows 10/11, Linux (Ubuntu 22.04+ LTS), or macOS (Sonoma+).
- **Python:** Version 3.14.0 or higher (tested against Python 3.14.2).
- **Git:** Standard git client for repository cloning.
- **C/C++ Build Chain:** Required only if building wheels from source (standard pre-compiled binary wheels for `pyosmium`, `rasterio`, `shapely`, and `pyogrio` install directly via `pip`).

---

## 2. Environment Setup

### 2.1 Clone Repository and Create Virtual Environment

```bash
# Navigate to working directory
cd /d E:\kash-paper  # On Windows
# or cd ~/kash-paper # On Linux/macOS

# Create isolated Python virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows Command Prompt:
.venv\Scripts\activate.bat

# Linux / macOS Bash:
source .venv/bin/activate
```

### 2.2 Install Exact Pinned Dependencies

```bash
# Upgrade pip to latest release
python -m pip install --upgrade pip

# Install pinned dependencies
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import geopandas, rasterio, shapely, sklearn, SALib, networkx; print('All core scientific packages imported successfully.')"
```

---

## 3. Data Architecture: Raw Inputs vs. Precomputed Caches

The repository maintains strict boundary conditions between raw inputs, heavy caches, and derived outputs:

1. **`data/raw/` (Read-Only Raw Inputs):**  
   Contains 19 staged files (canonical plan CSV/GeoJSON, permit register, OSM boundaries, POIs, WorldPop raster, stop master, CHALO logs, and driver GPS profiles). Integrity can be verified against `data/MANIFEST.json`.
2. **`data/cache/` (Heavy Precomputed Caches):**  
   Because certain spatial graph operations require substantial computational time, the repository ships with precomputed caches:
   - `walk_graph.gpickle` (77 MB): Routable pedestrian network (961,927 nodes, 973,569 edges; ~9 min compute).
   - `catchments_network.gpkg` (35 MB): Network walking catchments across 186 routes and 22,360 virtual stops (**~69 min compute**).
   - `osrm_responses.json`: Frozen driving distances and uncorrected OSRM runtimes across 186 routes.
   *Git Exclusion:* `data/cache/` is strictly excluded from version control via `.gitignore`.
3. **`data/derived/` (Module Outputs):**  
   All intermediate analysis datasets are emitted strictly as canonical **CSV and JSON** files. No binary parquet/pyarrow formats are used.

---

## 4. Replication Workflows

All analysis and figure generation is driven by the master CLI runner: `analysis/run_all.py`.

### 4.1 Quick Replication Pipeline (`--quick`) — Recommended (< 3 minutes)

The quick pipeline uses the precomputed network walking catchments (`data/cache/catchments_network.gpkg`) and precomputed walk graph to execute all downstream analyses, sensitivity sweeps, and figure generation:

```bash
python analysis/run_all.py --quick
```

**What `--quick` executes:**
1. Data Quality & Register Deconstruction (`q01_data_quality.py` → F1–F6, Tables 2a–2f).
2. Euclidean Catchment Replication & Residual Audit (`a02b_faithfulness.py` → F7, F9, Table 3b).
3. Repaired Observational GPS Validation (`v04_gps_validation.py` → F10–F12, Tables 6a–6d).
4. Demand Index Weighting Sensitivity (`a03_index_weights.py` → Equal, Entropy, PCA weights, Table 3).
5. Objective Class Count Determination (`a04_class_count.py` → Jenks GVF elbow, Kappa, Table 5, Figure 6).
6. Network Diagnostics & Headway Profiles (`a10_network_diagnostics.py`, `a05_headway_timeofday.py` → Table 4).
7. Network Accessibility & Spatial Equity (`a11_coverage_accessibility.py`, `a12_equity_gini.py`, `a13_transfers.py`).
8. Operational Plausibility & Scenarios (`a06_deadhead.py`, `a07_load_factor.py`, `a14_cost_emissions.py`, `a15_scenarios.py`).
9. Parameter Sweeps & Monte Carlo Uncertainty (`a08_sensitivity_oat.py`, `a09_monte_carlo_sobol.py` with 5,000 draws).
10. Multi-Channel Validation Matrix (`v01_spatial_crossval.py`, `v02_benchmark.py` → Table 7).
11. Publication Figures & Tables (`fig01` to `fig08b` → `paper/figures/`, `paper/tables/`).

### 4.2 Full End-to-End Replication (`--full`) (~75–80 minutes)

To rebuild all precomputed caches from scratch using the raw OpenStreetMap India extract and raw WorldPop raster:

```bash
python analysis/run_all.py --full
```
*Note:* Rebuilding `catchments_network.gpkg` via `analysis/a02_network_catchments.py` performs Dijkstra walking isochrones across 22,360 virtual stops and requires approximately 69 minutes on an 8-core machine.

### 4.3 Stage-by-Stage Execution (`--stage`)

You can execute individual milestone stages:
```bash
python analysis/run_all.py --stage 0   # Baseline setup, manifests, and claim ledger verification
python analysis/run_all.py --stage 1   # Repaired observational GPS validation (v04)
python analysis/run_all.py --stage 2   # Index weights and class hierarchy
python analysis/run_all.py --stage 3   # Network diagnostics, equity, and scenarios
python analysis/run_all.py --stage 4   # Uncertainty, Monte Carlo, Sobol, and multi-channel validation
python analysis/run_all.py --stage 5   # Publication tables and vector figures
```

### 4.4 Module-by-Module Execution (`--module`)

Individual analysis scripts can be executed directly:
```bash
python analysis/run_all.py --module q01_data_quality
python analysis/run_all.py --module v04_gps_validation
python analysis/run_all.py --module a03_index_weights
python analysis/run_all.py --module a04_class_count
```

---

## 5. Output Verification & Independent Audit Gates

To ensure complete fidelity with the manuscript, six independent audit checkers (Checkers A–F) verify output integrity:

| Checker | Audit Domain | Verification Command / Target | Success Criteria |
|---|---|---|---|
| **Checker A** | Scope & Denominators | `python -m pytest tests/test_checker_a_scope.py` | Exactly 10 districts; denominator = 6,584,762; zero legacy strings (`342`, `207`, `39%`, `95.7%`, `1,009`, `SMC`). |
| **Checker B** | Numerical Reproducibility | `python -m pytest tests/test_checker_b_numerical.py` | Fixed seed `20260823` applied; derived CSV tables match canonical reference outputs within declared floating tolerance ($10^{-5}$). |
| **Checker C** | GPS & Fleet Validation | `python -m pytest tests/test_checker_c_gps.py` | Mandatory fleet-formula self-test produces **0 mismatches** across all non-SSCL routes; 5 matched corridors labelled `in_sample`. |
| **Checker D** | Statistical Rigour | `python -m pytest tests/test_checker_d_statistics.py` | Index weights sum to 1.0; Monte Carlo uses 5,000 accepted draws with measured GPS pace prior; V3 documented as not performed. |
| **Checker E** | Manuscript Claim Ledger | `python -m pytest tests/test_checker_e_claims.py` | Every quantitative statistic in `paper/draft/*.md` maps to an active entry in `paper/CLAIM_LEDGER.md`. |
| **Checker F** | Clean Pipeline Execution | `python analysis/run_all.py --quick` | Process exits with return code 0; zero unhandled warnings or exceptions. |

---

## 6. Troubleshooting & Common Issues

- **Memory Exhaustion during Catchment Calculation:**  
  If running `--full` on memory-constrained systems (< 8 GB RAM), reduce the batch chunk size in `analysis/a02_network_catchments.py` or rely on the precomputed `catchments_network.gpkg` cache via `--quick`.
- **Pyosmium Geometry Parsing:**  
  Ensure `osmium==4.3.1` is installed. On Windows, pre-built wheels in `requirements.txt` are self-contained and do not require local Boost/Expat libraries.
- **Floating Point Discrepancies Across Architectures:**  
  Minor floating point differences ($< 10^{-6}$) in Jenks natural breaks or Gini coefficients across CPU architectures (x86_64 vs. ARM64) do not alter integer tier assignments or rounded table figures.
