# Handoff Report: Runner Architecture (`analysis/run_all.py`)

**Agent**: Explorer (Milestone M0, Subtask 2)  
**Working Directory**: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_2`  
**Target Specification**: Technical Architecture & Implementation Design for `analysis/run_all.py`  
**Date**: 2026-09-03  

---

## 1. Observation

Direct investigation of the repository layout, configuration, and existing scripts revealed the following concrete facts:

1. **Authoritative Mandate and Constraints (`ORIGINAL_REQUEST.md`)**:
   - Section R1 (`ORIGINAL_REQUEST.md:22-25`): "Implement `analysis/run_all.py` supporting `--stage`, `--module`, `--quick`, and `--full` without invoking the engine or redownloading data."
   - Section Non-Negotiable Research Contract (`ORIGINAL_REQUEST.md:10-18`):
     - Item 1: "Frozen operational baseline: Kashmir Valley v3.4.5 is the active baseline... Do not invent or imply an engine v4."
     - Item 7: "Do not modify external repos: `E:\kash` and `E:\bus-sathi-trace` are read-only. Large caches (`data/cache/`) must never be committed to git."
     - Item 8: "No shared-file races: Log active task ownership in `logs/WORK_REGISTER.md`."
   - Clean Reproduction Acceptance Criteria (`ORIGINAL_REQUEST.md:91-94`):
     - "`python analysis/run_all.py --quick` runs cleanly from `E:\kash-paper\.venv`."

2. **Project Architecture and Directory Boundaries (`E:\kash-paper\.agents\orchestrator\PROJECT.md:4-15`)**:
   - Environment: Python 3.14.2 at `E:\kash-paper\.venv` (CSV-only derived tables, no parquet/pyarrow).
   - `analysis/`: Paper-specific analysis modules and runners.
   - `data/raw/`: Read-only staged input data (19 manifested files + census 2011).
   - `data/cache/`: Heavy precomputed caches (`walk_graph.gpickle`, `catchments_network.gpkg`, `osrm_responses.json`). Excluded from git.
   - `data/derived/`: Canonical CSV and JSON analysis outputs.
   - `paper/tables/` and `paper/figures/`: Manuscript outputs.
   - `logs/`: `WORK_REGISTER.md` and module execution logs.

3. **Existing Python Scripts and Dependencies (`analysis/`)**:
   - `analysis/common.py`: Shared constants, paths (`ROOT`, `DATA`, `RAW`, `CACHE`, `DERIVED`, `PAPER`, `TABLES`), parameters (`PARAMETERS`), random seed `20260823`, helper functions (`get_logger`, `write_table`, `write_result`, `read_result`, `gini`, `entropy_weights`, `minmax`, `goodness_of_variance_fit`).
   - `analysis/q01_data_quality.py` (562 lines): §3.5 data quality diagnostics (D1–D6); fast (~5s); generates `data/derived/q01_data_quality.json` and `paper/tables/table02a`–`02f`.
   - `analysis/a01_build_walk_graph.py` (189 lines): Extracts walkable network graph from OSM PBF; **HEAVY (~9 min compute)**; output `data/cache/walk_graph.gpickle` (77.1 MB).
   - `analysis/a02_network_catchments.py` (434 lines): Dijkstra walking catchments across 22,360 virtual stops; **VERY HEAVY (~69 min compute)**; outputs `data/derived/a02_catchments.csv` (63.5 KB) and `data/cache/catchments_network.gpkg` (18.5 MB).
   - `analysis/a02b_faithfulness.py` (215 lines): Verifies Euclidean catchment reproduction against published plan; fast (~2s); reads `data/derived/a02_catchments.csv`.
   - `analysis/a03_index_weights.py` (335 lines): Derives composite index (equal, entropy, PCA); fast/moderate (~30s); reads `a02_catchments.csv` and `walk_graph.gpickle`.
   - `analysis/v04_gps_validation.py` (529 lines): Supply-side observational GPS validation; fast (~5s); currently slated for rewrite in M1 to fix circularity and split 5 in-sample vs 9 out-of-sample corridors.

4. **Cache State on Disk**:
   - `data/cache/walk_graph.gpickle` exists (77,051,716 bytes).
   - `data/cache/catchments_network.gpkg` exists (18,522,112 bytes).
   - `data/cache/osrm_responses.json` exists (2,825,043 bytes).
   - `data/derived/a02_catchments.csv` exists (63,476 bytes).
   - `logs/a01_walk_graph.log` and `logs/a02_catchments.log` exist from prior runs.

5. **Peer Subagent Alignment (`teamwork_preview_explorer_m0_1`)**:
   - In `proposed_REPRODUCIBILITY.md:88-130`, the planned CLI interface is documented as:
     - `python analysis/run_all.py --quick`: Recommended (< 3 minutes), skipping heavy graph generation (`a01`, `a02`), running all analytical modules.
     - `python analysis/run_all.py --full`: Full pipeline (~75–80 min if rebuilding caches).
     - `python analysis/run_all.py --stage <0..5>`: Stage-by-stage execution.

---

## 2. Logic Chain

1. **Offline & Standalone Operation (From Observation 1 & 4)**:
   - The paper companion repository is self-contained. All raw data are staged in `data/raw/` and all heavy caches (`walk_graph.gpickle`, `catchments_network.gpkg`, `osrm_responses.json`) are already generated.
   - `run_all.py` must never invoke `E:\kash` or external network services. It must execute only python scripts located in `analysis/` using the active venv interpreter (`sys.executable`).

2. **Heavy Cache Protection Guard (From Observation 2, 3 & 4)**:
   - Rebuilding `walk_graph.gpickle` takes ~9 minutes; recomputing `catchments_network.gpkg` and `a02_catchments.csv` takes ~69 minutes. Total: ~78 minutes.
   - Running `--quick` MUST strictly skip `a01_build_walk_graph` and `a02_network_catchments` as long as their cache files exist on disk.
   - Even in `--full`, `run_all.py` should inspect whether `data/cache/walk_graph.gpickle` and `data/cache/catchments_network.gpkg` exist. If they exist, it must protect them and skip recomputation by default, unless an explicit `--force-heavy` flag is provided. This prevents accidental multi-hour stalls.

3. **Stage and Module Hierarchy (From Observation 2 & 5)**:
   The analysis modules map directly to the research project stages:
   - **Stage 0: Baseline & Diagnostics**: `q01_data_quality`, `a01_build_walk_graph` (heavy), `a02_network_catchments` (heavy), `a02b_faithfulness`.
   - **Stage 1: Observational GPS Validation**: `v04_gps_validation`.
   - **Stage 2: Index Weights & Hierarchy**: `a03_index_weights`, `a04_class_count`.
   - **Stage 3: Network Diagnostics, Equity & Scenarios**: `a10_network_diagnostics`, `a05_headway_timeofday`, `a11_coverage_accessibility`, `a12_equity_gini`, `a13_transfers`, `a06_deadhead`, `a07_load_factor`, `a14_cost_emissions`, `a15_scenarios`, `a16_peer_regression`.
   - **Stage 4: Uncertainty & Independent Validation**: `a08_sensitivity_oat`, `a09_monte_carlo_sobol`, `v01_spatial_crossval`, `v02_benchmark`.
   - **Stage 5: Publication Figures & Tables**: `fig01_*.py` through `fig08b_*.py`, and table verification.

4. **Dependency Resolution & DAG Ordering (From Observation 2 & 3)**:
   - Certain modules have strict data dependencies. For example:
     - `a02b_faithfulness` requires `data/derived/a02_catchments.csv`.
     - `a03_index_weights` requires `a02_catchments.csv` and `walk_graph.gpickle`.
     - `a04_class_count` requires `data/derived/a03_index.csv`.
     - `a09_monte_carlo_sobol` requires `data/derived/v04_gps_validation.json` (the measured pace prior interface contract).
     - `figXX_*.py` read exclusively from `data/derived/*.csv` and `*.json`.
   - `run_all.py` must define an explicit dependency DAG. When a user requests a stage or module, `run_all.py` must verify that prerequisite files exist. If a prerequisite is missing, it must warn or resolve the prerequisite module in topological order.
   - For modules that are planned but not yet implemented on disk (e.g. `a04`, `a10`), `run_all.py` must mark them as `PLANNED` / `NOT_IMPLEMENTED` rather than crashing with a `FileNotFoundError`.

5. **Subprocess Isolation & Logging (From Observation 1, 2 & 3)**:
   - Modules should be run via `subprocess.Popen` with `sys.executable` in the working directory `E:\kash-paper`. This ensures total memory isolation, proper garbage collection of large GeoDataFrames, and prevention of GDAL/pyproj/shapely C-state collisions.
   - Both `stdout` and `stderr` must be captured and logged to `logs/<module>.log`.
   - Each log file must include a standardized header and footer: UTC start/end timestamp, execution command, duration, exit code, and generated outputs.
   - In interactive mode or with `-v` (`--verbose`), output should be live-streamed while simultaneously saved to disk (Tee pattern).

6. **Summary Reporting & Auditing (From Observation 1 & 5)**:
   - At the end of execution, `run_all.py` must print a formatted summary table:
     - Stage number
     - Module name
     - Status: `PASSED`, `FAILED`, `SKIPPED (cached)`, `SKIPPED (prereq missing)`, `PLANNED`
     - Execution duration in seconds
     - Verified output file count
     - Log file location
   - Overall exit code must be `0` if all attempted scripts succeeded, or `1` if any failed, fulfilling Checker F requirements.
   - A structured JSON summary must be written to `logs/LATEST_RUN.json` for automated checker auditing.

---

## 3. Caveats

1. **Planned Modules Not Yet On Disk**: Currently, only `q01`, `a01`, `a02`, `a02b`, `a03`, and `v04` exist on disk in `analysis/`. Modules `a04`–`a16`, `v01`, `v02`, and `fig01`–`fig08b` are planned for subsequent milestones (M2–M5). The runner is architected to register all 22+ modules, executing those that exist and reporting non-existent modules as `PLANNED` without failing the overall execution during partial-pipeline development runs.
2. **`v04_gps_validation.py` Rewrite**: The current `v04` script on disk is functional but will be rewritten in Milestone M1. The runner treats `v04` as a standard fast module that outputs `v04_corridor_comparison.csv` and `v04_gps_validation.json`.
3. **Heavy Cache Recomputation**: If `data/cache/` is ever wiped, running `--full --force-heavy` will take ~78 minutes. Reviewers and automated CI should always run with `--quick` using the staged precomputed caches.

---

## 4. Conclusion & Technical Architecture Specification

### 4.1 CLI Interface Specification

The master runner script `analysis/run_all.py` must support the following command-line interface:

```
usage: run_all.py [-h] [--stage STAGE] [--module MODULE] [--quick] [--full]
                  [--force-heavy] [--dry-run] [--list] [--verbose]
                  [--continue-on-error] [--log-dir LOG_DIR]
```

#### Flags & Options:
- `--stage <N>`:
  Execute all modules assigned to stage `N`. Accepts single stage (e.g. `--stage 0`, `--stage 1`), multiple stages (e.g. `--stage 0,1,2`), or `all`.
- `--module <name>`:
  Execute a single module by name or stem (e.g. `--module q01_data_quality`, `--module v04_gps_validation`, `--module a02b`). Strips `.py` and path prefixes automatically.
- `--quick`:
  Replication mode (< 3 minutes). Executes all lightweight analysis and validation modules across all stages. Explicitly **skips** heavy cache builders `a01` and `a02` when cache files exist on disk.
- `--full`:
  Full end-to-end pipeline execution in topological dependency order. Automatically preserves existing heavy caches unless `--force-heavy` is also specified.
- `--force-heavy`:
  Explicitly permits recomputation of heavy cache modules (`a01` and `a02`), taking ~78 minutes. Without this flag, existing cache files are strictly preserved.
- `--dry-run`:
  Resolves dependencies, prints the execution plan and status of inputs/outputs without launching subprocesses.
- `--list`:
  Prints the catalog of all 22+ registered modules, stages, cache classifications, expected inputs/outputs, and current status on disk.
- `-v`, `--verbose`:
  Stream stdout/stderr live to the terminal in addition to writing to `logs/<module>.log`.
- `--continue-on-error`:
  Continue running remaining independent modules even if one module fails (default: halt on first failure).
- `--log-dir <path>`:
  Directory for log files (defaults to `E:\kash-paper\logs`).

---

### 4.2 Module Registry & Dependency DAG

Every module is defined via a structured specification:

| Module Identifier | Stage | Script Path | Is Heavy? | Estimated Runtime | Key Inputs | Key Outputs | Depends On |
|---|---|---|---|---|---|---|---|
| `q01_data_quality` | 0 | `analysis/q01_data_quality.py` | No | 5s | Staged raw data, permits, GPS | `q01_data_quality.json`, Tables 02a–02f | None |
| `a01_build_walk_graph` | 0 | `analysis/a01_build_walk_graph.py` | **Yes** | 540s (~9m) | OSM PBF / raw boundaries | `data/cache/walk_graph.gpickle` | None |
| `a02_network_catchments` | 0 | `analysis/a02_network_catchments.py` | **Yes** | 4140s (~69m) | `walk_graph.gpickle`, Plan GeoJSON | `data/derived/a02_catchments.csv`, `data/cache/catchments_network.gpkg` | `a01_build_walk_graph` |
| `a02b_faithfulness` | 0 | `analysis/a02b_faithfulness.py` | No | 2s | `a02_catchments.csv`, Plan CSV | `a02b_faithfulness.csv`, Table 03b | `a02_network_catchments` |
| `v04_gps_validation` | 1 | `analysis/v04_gps_validation.py` | No | 5s | Staged GPS profiles, Plan CSV | `v04_corridor_comparison.csv`, `v04_gps_validation.json`, Tables 06a–06d | None |
| `a03_index_weights` | 2 | `analysis/a03_index_weights.py` | No | 30s | `a02_catchments.csv`, `walk_graph.gpickle` | `a03_index.csv`, `a03_index_weights.json`, Tables 04a–04b | `a02_network_catchments` |
| `a04_class_count` | 2 | `analysis/a04_class_count.py` | No | 10s | `a03_index.csv` | `a04_class_count.json`, Table 05 | `a03_index_weights` |
| `a10_network_diagnostics` | 3 | `analysis/a10_network_diagnostics.py` | No | 15s | Plan CSV, Plan GeoJSON, Permits | `a10_network_diagnostics.json`, Table 04 | None |
| `a05_headway_timeofday` | 3 | `analysis/a05_headway_timeofday.py` | No | 10s | `Hourly_Passenger_Count.csv` (skiprows=1) | `a05_headway.json`, Table 06 | None |
| `a11_coverage_accessibility` | 3 | `analysis/a11_coverage_accessibility.py` | No | 45s | `a02_catchments.csv`, `catchments_network.gpkg` | `a11_coverage.json` | `a02_network_catchments` |
| `a12_equity_gini` | 3 | `analysis/a12_equity_gini.py` | No | 15s | `a11_coverage.json`, WorldPop raster | `a12_equity_gini.json` | `a11_coverage_accessibility` |
| `a13_transfers` | 3 | `analysis/a13_transfers.py` | No | 20s | Plan GeoJSON, Plan CSV | `a13_transfers.json` | None |
| `a06_deadhead` | 3 | `analysis/a06_deadhead.py` | No | 10s | Plan CSV, depot parameters | `a06_deadhead.json` | None |
| `a07_load_factor` | 3 | `analysis/a07_load_factor.py` | No | 10s | Plan CSV, hourly passenger data | `a07_load_factor.json` | None |
| `a14_cost_emissions` | 3 | `analysis/a14_cost_emissions.py` | No | 10s | Plan CSV, `a11_coverage.json` | `a14_cost_emissions.json` | `a11_coverage_accessibility` |
| `a15_scenarios` | 3 | `analysis/a15_scenarios.py` | No | 20s | Plan CSV, `a03_index.csv`, `a05_headway.json` | `a15_scenarios.json` | `a03_index_weights`, `a05_headway_timeofday` |
| `a16_peer_regression` | 3 | `analysis/a16_peer_regression.py` | No | 5s | Peer city dataset, Plan CSV | `a16_peer_regression.json` | None |
| `a08_sensitivity_oat` | 4 | `analysis/a08_sensitivity_oat.py` | No | 60s | `a03_index.csv`, `common.PARAMETERS` | `a08_sensitivity_oat.json` | `a03_index_weights` |
| `a09_monte_carlo_sobol` | 4 | `analysis/a09_monte_carlo_sobol.py` | No | 120s | `v04_gps_validation.json` (pace prior), Plan CSV | `a09_monte_carlo_sobol.json` | `v04_gps_validation` |
| `v01_spatial_crossval` | 4 | `analysis/v01_spatial_crossval.py` | No | 30s | Building footprint data, `a03_index.csv` | `v01_spatial_crossval.json` | `a03_index_weights` |
| `v02_benchmark` | 4 | `analysis/v02_benchmark.py` | No | 10s | `chalo_ridership.csv`, Plan CSV | `v02_benchmark.json`, circularity note | None |
| `figures_tables` | 5 | `analysis/fig*.py` | No | 60s | Derived CSVs/JSONs | Figures 1–8b (`paper/figures/`), Table 7 | All upstream |

---

### 4.3 Execution Ordering Algorithm

When the user selects modules via `--stage`, `--module`, `--quick`, or `--full`:

1. **Selection Filter**:
   - `--stage N`: Filter registry by `stage == N`.
   - `--module M`: Filter registry by `name == M`.
   - `--quick`: Select all modules where `is_heavy == False`.
   - `--full`: Select all registered modules.
2. **Heavy Cache Bypass**:
   - For any module where `is_heavy == True` (`a01`, `a02`):
     - If all `cache_files` exist on disk AND `--force-heavy` is False:
       Mark as `SKIPPED (cached)` and do not execute.
     - If cache files are missing: execute or fail with actionable error depending on mode.
3. **Topological Sort**:
   - Build adjacency graph from `depends_on`.
   - Perform Kahn's algorithm to generate linear execution sequence.
   - Detect and reject cycles immediately.
4. **Input Prerequisite Check**:
   - For each module in order, check if required input files exist on disk.
   - If an input file is missing and its producing script is not scheduled, issue a clear diagnostic:
     `"Prerequisite missing for {module}: {missing_path}. Run upstream module {dep} first."`
5. **Disk Script Verification**:
   - Check if `analysis/<script>` exists.
   - If missing: mark as `PLANNED` and skip execution without crashing.
   - If present: execute via isolated subprocess.

---

### 4.4 Subprocess Execution & Logging Protocol

Each script execution follows strict audit isolation:

```python
cmd = [sys.executable, str(script_path)]
env = os.environ.copy()
env["PYTHONPATH"] = f"{ROOT};{ROOT / 'analysis'}"
```

1. **Log Header**: Written to `logs/<module>.log`:
   ```
   ================================================================================
   KASHMIR TRANSIT REPRODUCIBILITY RUNNER — MODULE EXECUTION LOG
   Module:      {module_name}
   Script:      {script_path}
   Stage:       Stage {stage}
   Started:     {start_iso_utc}
   Python:      {sys.executable} ({sys.version.split()[0]})
   Working Dir: {ROOT}
   Command:     {" ".join(cmd)}
   ================================================================================
   ```
2. **Stream Handling**:
   - Both `stdout` and `stderr` captured via `subprocess.PIPE`.
   - Interleaved capture writes synchronously to `logs/<module>.log`.
   - In verbose mode (`-v`), output lines stream simultaneously to terminal.
3. **Log Footer**:
   ```
   ================================================================================
   Finished:    {end_iso_utc}
   Duration:    {duration:.2f}s
   Exit Code:   {returncode}
   Status:      {"PASSED" if returncode == 0 else "FAILED"}
   Outputs:
     - {path} ({size} bytes) [VERIFIED]
   ================================================================================
   ```

---

### 4.5 Pass/Fail Reporting & Summary Table

Upon completion of all scheduled modules, `run_all.py` outputs a standardized summary table:

```
========================================================================================================================
                                     KASHMIR VALLEY TRANSIT PAPER REPRODUCIBILITY RUNNER
========================================================================================================================
 Stage    Module                     Status             Duration    Outputs Verified     Log File
------------------------------------------------------------------------------------------------------------------------
 Stage 0  q01_data_quality           PASSED                4.82s    7/7 verified         logs/q01_data_quality.log
 Stage 0  a01_build_walk_graph       SKIPPED (cached)         --    2/2 cache intact     logs/a01_walk_graph.log
 Stage 0  a02_network_catchments     SKIPPED (cached)         --    4/4 cache intact     logs/a02_catchments.log
 Stage 0  a02b_faithfulness          PASSED                1.15s    3/3 verified         logs/a02b_faithfulness.log
 Stage 1  v04_gps_validation         PASSED                4.92s    6/6 verified         logs/v04_gps_validation.log
 Stage 2  a03_index_weights          PASSED               28.40s    4/4 verified         logs/a03_index_weights.log
 Stage 2  a04_class_count            PLANNED                  --    Script pending       --
------------------------------------------------------------------------------------------------------------------------
 Execution Summary: 7 modules scheduled
 Passed: 4 | Cached/Skipped: 2 | Failed: 0 | Planned: 1
 Total Elapsed Time: 39.29s
 Overall Pipeline Status: SUCCESS (all attempted modules passed)
========================================================================================================================
```

- Structured machine-readable JSON saved to `logs/LATEST_RUN.json` containing timestamps, per-module durations, exit codes, output verifications, and git/env metadata.

---

### 4.6 Complete Reference Implementation for `analysis/run_all.py`

Below is the complete, drop-in Python implementation code for `analysis/run_all.py`:

```python
#!/usr/bin/env python
"""
run_all.py — Master Reproducibility Runner for the Kashmir Bus Route Rationalisation Paper.

Orchestrates all data quality diagnostics, spatial analyses, sensitivity sweeps,
and validation channels under strict compliance with the non-negotiable research contract:
  1. Offline execution: Never contacts external networks or invokes engine v4 / OSRM.
  2. Cache preservation: Never overwrites expensive heavy caches (walk_graph, catchments)
     unless --force-heavy is explicitly provided.
  3. Isolated subprocess execution: Every module runs in an isolated Python process
     with full stdout/stderr logging to logs/<module>.log.
  4. Pass/fail reporting: Tracks runtimes, verifies output files, and outputs a formatted
     summary table and machine-readable JSON.

Usage:
    python analysis/run_all.py --quick               # Run fast analysis suite (< 3 min)
    python analysis/run_all.py --full                # Run full pipeline preserving caches
    python analysis/run_all.py --stage 0             # Run specific stage (0, 1, 2, 3, 4, 5)
    python analysis/run_all.py --module q01          # Run single module by name
    python analysis/run_all.py --list                # List all modules and cache statuses
    python analysis/run_all.py --dry-run             # Display execution plan without running
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Resolve paths
ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = ROOT / "analysis"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
DERIVED_DIR = DATA_DIR / "derived"
PAPER_DIR = ROOT / "paper"
TABLES_DIR = PAPER_DIR / "tables"
FIGURES_DIR = PAPER_DIR / "figures"
LOGS_DIR = ROOT / "logs"

for d in (DERIVED_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class ModuleSpec:
    name: str
    script: str
    stage: int
    description: str
    is_heavy: bool = False
    cache_targets: tuple[Path, ...] = ()
    inputs: tuple[Path, ...] = ()
    outputs: tuple[Path, ...] = ()
    depends_on: tuple[str, ...] = ()
    estimated_runtime_sec: float = 5.0


MODULE_REGISTRY: list[ModuleSpec] = [
    # ── Stage 0: Baseline Setup & Input Diagnostics ───────────────────────────────
    ModuleSpec(
        name="q01_data_quality",
        script="q01_data_quality.py",
        stage=0,
        description="§3.5 Input diagnostics (D1-D6) & permit deconstruction",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv", RAW_DIR / "existing-routes.csv"),
        outputs=(DERIVED_DIR / "q01_data_quality.json", TABLES_DIR / "table02a_permit_duplication.csv"),
        depends_on=(),
        estimated_runtime_sec=5.0,
    ),
    ModuleSpec(
        name="a01_build_walk_graph",
        script="a01_build_walk_graph.py",
        stage=0,
        description="Extract walkable pedestrian graph from OSM PBF",
        is_heavy=True,
        cache_targets=(CACHE_DIR / "walk_graph.gpickle",),
        inputs=(),
        outputs=(CACHE_DIR / "walk_graph.gpickle",),
        depends_on=(),
        estimated_runtime_sec=540.0,
    ),
    ModuleSpec(
        name="a02_network_catchments",
        script="a02_network_catchments.py",
        stage=0,
        description="Dijkstra walking catchments across 22,360 stops (69 min)",
        is_heavy=True,
        cache_targets=(CACHE_DIR / "catchments_network.gpkg", DERIVED_DIR / "a02_catchments.csv"),
        inputs=(CACHE_DIR / "walk_graph.gpickle", RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson"),
        outputs=(DERIVED_DIR / "a02_catchments.csv", CACHE_DIR / "catchments_network.gpkg"),
        depends_on=("a01_build_walk_graph",),
        estimated_runtime_sec=4140.0,
    ),
    ModuleSpec(
        name="a02b_faithfulness",
        script="a02b_faithfulness.py",
        stage=0,
        description="Verify Euclidean catchment reproduction vs published plan",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a02_catchments.csv", RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv"),
        outputs=(DERIVED_DIR / "a02b_faithfulness.csv", TABLES_DIR / "table03b_faithfulness.csv"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=2.0,
    ),

    # ── Stage 1: Repaired Observational GPS Validation ───────────────────────────
    ModuleSpec(
        name="v04_gps_validation",
        script="v04_gps_validation.py",
        stage=1,
        description="Observational GPS runtime, dwell, & fleet formula self-test",
        is_heavy=False,
        inputs=(RAW_DIR / "gps" / "reality_check.csv", RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv"),
        outputs=(DERIVED_DIR / "v04_corridor_comparison.csv", DERIVED_DIR / "v04_gps_validation.json"),
        depends_on=(),
        estimated_runtime_sec=5.0,
    ),

    # ── Stage 2: Index Weights & Class Hierarchy ──────────────────────────────────
    ModuleSpec(
        name="a03_index_weights",
        script="a03_index_weights.py",
        stage=2,
        description="Composite Demand Index weights (equal/entropy/PCA) & stability",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a02_catchments.csv", CACHE_DIR / "walk_graph.gpickle"),
        outputs=(DERIVED_DIR / "a03_index.csv", DERIVED_DIR / "a03_index_weights.json"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=30.0,
    ),
    ModuleSpec(
        name="a04_class_count",
        script="a04_class_count.py",
        stage=2,
        description="Objective class count (Jenks GVF 2-7, elbow rule, Kappa)",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a03_index.csv",),
        outputs=(DERIVED_DIR / "a04_class_count.json", TABLES_DIR / "table05_route_scores.csv"),
        depends_on=("a03_index_weights",),
        estimated_runtime_sec=10.0,
    ),

    # ── Stage 3: Operational Diagnostics, Equity, & Scenarios ─────────────────────
    ModuleSpec(
        name="a10_network_diagnostics",
        script="a10_network_diagnostics.py",
        stage=3,
        description="Network diagnostics: permit-vs-corridor, link duplication",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a10_network_diagnostics.json", TABLES_DIR / "table04_network_profile.csv"),
        depends_on=(),
        estimated_runtime_sec=15.0,
    ),
    ModuleSpec(
        name="a05_headway_timeofday",
        script="a05_headway_timeofday.py",
        stage=3,
        description="Time-of-day headways from hourly passenger counts",
        is_heavy=False,
        inputs=(RAW_DIR / "Hourly_Passenger_Count.csv",),
        outputs=(DERIVED_DIR / "a05_headway.json", TABLES_DIR / "table06_service_standards.csv"),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a11_coverage_accessibility",
        script="a11_coverage_accessibility.py",
        stage=3,
        description="Deduplicated network coverage & Moran's I on uncovered surface",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a02_catchments.csv",),
        outputs=(DERIVED_DIR / "a11_coverage.json",),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=45.0,
    ),
    ModuleSpec(
        name="a12_equity_gini",
        script="a12_equity_gini.py",
        stage=3,
        description="Population-weighted accessibility Gini & map of losers",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a11_coverage.json",),
        outputs=(DERIVED_DIR / "a12_equity_gini.json",),
        depends_on=("a11_coverage_accessibility",),
        estimated_runtime_sec=15.0,
    ),
    ModuleSpec(
        name="a13_transfers",
        script="a13_transfers.py",
        stage=3,
        description="0/1/2+ transfer shares & break-even transfer penalty",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson",),
        outputs=(DERIVED_DIR / "a13_transfers.json",),
        depends_on=(),
        estimated_runtime_sec=20.0,
    ),
    ModuleSpec(
        name="a06_deadhead",
        script="a06_deadhead.py",
        stage=3,
        description="Depot deadhead modeling (5-12% bus-hours)",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a06_deadhead.json",),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a07_load_factor",
        script="a07_load_factor.py",
        stage=3,
        description="Offered capacity vs proxy peak demand (implied load factor)",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a07_load_factor.json",),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a14_cost_emissions",
        script="a14_cost_emissions.py",
        stage=3,
        description="Cost per accessibility gain & emissions scenario range",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a14_cost_emissions.json",),
        depends_on=("a11_coverage_accessibility",),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a15_scenarios",
        script="a15_scenarios.py",
        stage=3,
        description="Five operational policy scenarios & trade-off frontier",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a15_scenarios.json",),
        depends_on=("a03_index_weights", "a05_headway_timeofday"),
        estimated_runtime_sec=20.0,
    ),
    ModuleSpec(
        name="a16_peer_regression",
        script="a16_peer_regression.py",
        stage=3,
        description="Peer city regression: buses/1k vs population & density",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a16_peer_regression.json",),
        depends_on=(),
        estimated_runtime_sec=5.0,
    ),

    # ── Stage 4: Uncertainty Analysis & Multi-Channel Validation ──────────────────
    ModuleSpec(
        name="a08_sensitivity_oat",
        script="a08_sensitivity_oat.py",
        stage=4,
        description="One-At-a-Time sensitivity sweeps across 10 parameters",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a03_index.csv",),
        outputs=(DERIVED_DIR / "a08_sensitivity_oat.json",),
        depends_on=("a03_index_weights",),
        estimated_runtime_sec=60.0,
    ),
    ModuleSpec(
        name="a09_monte_carlo_sobol",
        script="a09_monte_carlo_sobol.py",
        stage=4,
        description="Monte Carlo 5k draws using v04 pace prior & Sobol indices",
        is_heavy=False,
        inputs=(DERIVED_DIR / "v04_gps_validation.json",),
        outputs=(DERIVED_DIR / "a09_monte_carlo_sobol.json",),
        depends_on=("v04_gps_validation",),  # Interface contract!
        estimated_runtime_sec=120.0,
    ),
    ModuleSpec(
        name="v01_spatial_crossval",
        script="v01_spatial_crossval.py",
        stage=4,
        description="Validation V1: OSM building footprint spatial cross-val",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a03_index.csv",),
        outputs=(DERIVED_DIR / "v01_spatial_crossval.json",),
        depends_on=("a03_index_weights",),
        estimated_runtime_sec=30.0,
    ),
    ModuleSpec(
        name="v02_benchmark",
        script="v02_benchmark.py",
        stage=4,
        description="Validation V2: CHALO benchmark with circularity disclosure",
        is_heavy=False,
        inputs=(RAW_DIR / "chalo_ridership.csv",),
        outputs=(DERIVED_DIR / "v02_benchmark.json",),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
]

REGISTRY_BY_NAME = {m.name: m for m in MODULE_REGISTRY}


def topological_sort(modules: list[ModuleSpec]) -> list[ModuleSpec]:
    """Return modules sorted in valid execution dependency order."""
    selected_names = {m.name for m in modules}
    graph = {m.name: [dep for dep in m.depends_on if dep in selected_names] for m in modules}
    in_degree = {name: 0 for name in selected_names}
    for deps in graph.values():
        for dep in deps:
            pass  # in_degree tracks prerequisites
    
    # Calculate prerequisites count
    deps_count = {name: len(graph[name]) for name in selected_names}
    queue = [name for name, count in deps_count.items() if count == 0]
    result = []
    
    while queue:
        curr = queue.pop(0)
        result.append(REGISTRY_BY_NAME[curr])
        for name, deps in graph.items():
            if curr in deps:
                deps_count[name] -= 1
                if deps_count[name] == 0:
                    queue.append(name)
                    
    if len(result) != len(modules):
        # Fallback to stage ordering if circular or incomplete
        return sorted(modules, key=lambda m: (m.stage, m.name))
    return result


def execute_module(spec: ModuleSpec, verbose: bool = False, log_dir: Path = LOGS_DIR) -> dict[str, Any]:
    """Execute a single module in an isolated Python subprocess, capturing logs."""
    script_path = ANALYSIS_DIR / spec.script
    log_file = log_dir / f"{spec.name}.log"
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    start_time = time.perf_counter()
    
    cmd = [sys.executable, str(script_path)]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT};{ANALYSIS_DIR}"
    
    # Write header
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"MODULE:      {spec.name}\n")
        f.write(f"SCRIPT:      {spec.script}\n")
        f.write(f"STAGE:       Stage {spec.stage}\n")
        f.write(f"STARTED:     {start_dt.isoformat()}\n")
        f.write(f"PYTHON:      {sys.executable} ({sys.version.split()[0]})\n")
        f.write(f"COMMAND:     {' '.join(cmd)}\n")
        f.write("=" * 80 + "\n\n")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(ROOT),
            env=env,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        
        output_lines = []
        with open(log_file, "a", encoding="utf-8") as f:
            for line in proc.stdout:
                f.write(line)
                f.flush()
                output_lines.append(line)
                if verbose:
                    sys.stdout.write(f"[{spec.name}] {line}")
                    sys.stdout.flush()
                    
        proc.wait()
        returncode = proc.returncode
    except Exception as exc:
        returncode = -1
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\nFATAL RUNNER ERROR: {exc}\n")

    duration = time.perf_counter() - start_time
    end_dt = datetime.datetime.now(datetime.timezone.utc)

    # Verify outputs
    verified_outputs = [p for p in spec.outputs if p.exists() and p.stat().st_size > 0]
    
    # Write footer
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"FINISHED:    {end_dt.isoformat()}\n")
        f.write(f"DURATION:    {duration:.2f}s\n")
        f.write(f"EXIT CODE:   {returncode}\n")
        f.write(f"STATUS:      {'PASSED' if returncode == 0 else 'FAILED'}\n")
        f.write(f"VERIFIED:    {len(verified_outputs)}/{len(spec.outputs)} outputs\n")
        f.write("=" * 80 + "\n")

    return {
        "name": spec.name,
        "stage": spec.stage,
        "status": "PASSED" if returncode == 0 else "FAILED",
        "duration": duration,
        "exit_code": returncode,
        "outputs_verified": len(verified_outputs),
        "outputs_total": len(spec.outputs),
        "log_file": str(log_file.relative_to(ROOT)),
    }


def print_summary_table(results: list[dict[str, Any]], total_elapsed: float) -> None:
    """Print a clean execution summary table."""
    line = "-" * 110
    double_line = "=" * 110
    print("\n" + double_line)
    print("                      KASHMIR VALLEY TRANSIT PAPER — REPRODUCIBILITY RUNNER SUMMARY")
    print(double_line)
    print(f"{'Stage':<9} {'Module':<27} {'Status':<18} {'Duration':<12} {'Outputs Verified':<18} {'Log File'}")
    print(line)

    n_pass = 0
    n_skip = 0
    n_fail = 0
    n_plan = 0

    for r in results:
        status = r["status"]
        if status == "PASSED":
            n_pass += 1
            dur_str = f"{r['duration']:.2f}s"
            out_str = f"{r['outputs_verified']}/{r['outputs_total']} verified"
        elif "SKIPPED" in status:
            n_skip += 1
            dur_str = "--"
            out_str = r.get("skip_reason", "Cached")
        elif status == "PLANNED":
            n_plan += 1
            dur_str = "--"
            out_str = "Script pending"
        else:
            n_fail += 1
            dur_str = f"{r.get('duration', 0):.2f}s"
            out_str = f"{r.get('outputs_verified', 0)}/{r.get('outputs_total', 0)} verified"

        log_display = r.get("log_file", "--")
        print(f"Stage {r['stage']:<3} {r['name']:<27} {status:<18} {dur_str:<12} {out_str:<18} {log_display}")

    print(line)
    print(f"Total Modules: {len(results)} | Passed: {n_pass} | Skipped/Cached: {n_skip} | Failed: {n_fail} | Planned: {n_plan}")
    print(f"Total Pipeline Runtime: {total_elapsed:.2f}s")
    if n_fail == 0:
        print("OVERALL STATUS: SUCCESS")
    else:
        print(f"OVERALL STATUS: FAILED ({n_fail} module(s) exited with error)")
    print(double_line + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Master Reproducibility Runner for Kashmir Bus Route Rationalisation Paper."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="Run lightweight analysis suite (< 3 min), skipping heavy caches.")
    group.add_argument("--full", action="store_true", help="Run full pipeline across all stages (preserves caches unless forced).")
    group.add_argument("--stage", type=str, help="Run specific stage(s), e.g. '0', '1', '0,1,2', or 'all'.")
    group.add_argument("--module", type=str, help="Run single module by name (e.g. 'q01_data_quality' or 'q01').")
    
    parser.add_argument("--force-heavy", action="store_true", help="Force recomputation of heavy cache files (a01, a02; ~78 min).")
    parser.add_argument("--dry-run", action="store_true", help="Display execution plan and dependency status without running.")
    parser.add_argument("--list", action="store_true", help="List all modules, stages, dependencies, and cache status.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Stream stdout/stderr live to terminal.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue running remaining independent modules on error.")
    parser.add_argument("--log-dir", type=Path, default=LOGS_DIR, help="Directory for execution logs.")

    args = parser.parse_args()

    # Default to --quick if no mode specified
    if not (args.quick or args.full or args.stage or args.module or args.list or args.dry_run):
        print("No execution target specified. Defaulting to --quick replication mode.")
        args.quick = True

    if args.list:
        print("\nRegistered Modules in Paper Companion Pipeline:")
        print(f"{'Stage':<7} {'Module':<27} {'Is Heavy?':<11} {'Script Exists?':<16} {'Description'}")
        print("-" * 90)
        for m in MODULE_REGISTRY:
            script_exists = (ANALYSIS_DIR / m.script).exists()
            heavy_str = "YES" if m.is_heavy else "No"
            exists_str = "YES" if script_exists else "PLANNED"
            print(f"Stage {m.stage:<2} {m.name:<27} {heavy_str:<11} {exists_str:<16} {m.description}")
        print("-" * 90 + "\n")
        return 0

    # Filter target modules
    if args.module:
        target_name = args.module.replace(".py", "").strip()
        matched = [m for m in MODULE_REGISTRY if m.name == target_name or m.name.startswith(target_name)]
        if not matched:
            print(f"Error: No module matching '{args.module}' found in registry.", file=sys.stderr)
            return 1
        target_modules = matched
    elif args.stage:
        if args.stage.lower() == "all":
            target_modules = list(MODULE_REGISTRY)
        else:
            try:
                stages = [int(s.strip()) for s in args.stage.split(",")]
            except ValueError:
                print(f"Error: Invalid stage format '{args.stage}'. Expected integers like '0', '1', or '0,1'.", file=sys.stderr)
                return 1
            target_modules = [m for m in MODULE_REGISTRY if m.stage in stages]
            if not target_modules:
                print(f"Error: No modules found for stage(s) {stages}.", file=sys.stderr)
                return 1
    elif args.quick:
        target_modules = [m for m in MODULE_REGISTRY if not m.is_heavy]
    else:  # --full
        target_modules = list(MODULE_REGISTRY)

    # Sort topologically
    execution_plan = topological_sort(target_modules)

    if args.dry_run:
        print("\nDry Run Execution Plan:")
        print(f"{'Order':<6} {'Stage':<8} {'Module':<27} {'Action':<22} {'Reason'}")
        print("-" * 90)
        for idx, m in enumerate(execution_plan, 1):
            script_exists = (ANALYSIS_DIR / m.script).exists()
            if m.is_heavy and all(p.exists() for p in m.cache_targets) and not args.force_heavy:
                action = "SKIP (cached)"
                reason = "Heavy cache files present on disk"
            elif not script_exists:
                action = "SKIP (planned)"
                reason = f"Script analysis/{m.script} not yet written"
            else:
                action = "EXECUTE"
                reason = f"Estimated runtime ~{m.estimated_runtime_sec:.1f}s"
            print(f"{idx:<6} Stage {m.stage:<3} {m.name:<27} {action:<22} {reason}")
        print("-" * 90 + "\n")
        return 0

    print(f"\nLaunching Kashmir Transit Paper Pipeline ({len(execution_plan)} modules scheduled)...")
    start_pipeline_time = time.perf_counter()
    results = []
    has_failure = False

    for spec in execution_plan:
        script_path = ANALYSIS_DIR / spec.script
        
        # Heavy cache preservation guard
        if spec.is_heavy and all(p.exists() for p in spec.cache_targets) and not args.force_heavy:
            print(f"  [CACHE GUARD] Preserving cache for {spec.name} ({', '.join(p.name for p in spec.cache_targets)})")
            results.append({
                "name": spec.name,
                "stage": spec.stage,
                "status": "SKIPPED (cached)",
                "skip_reason": "Cache intact on disk",
                "log_file": "--",
            })
            continue

        # Check script existence
        if not script_path.exists():
            print(f"  [PLANNED] Script {spec.script} not yet on disk. Skipping.")
            results.append({
                "name": spec.name,
                "stage": spec.stage,
                "status": "PLANNED",
                "skip_reason": "Script pending",
                "log_file": "--",
            })
            continue

        # Execute
        print(f"  [RUNNING] Stage {spec.stage}: {spec.name} ... ", end="", flush=True)
        res = execute_module(spec, verbose=args.verbose, log_dir=args.log_dir)
        print(f"{res['status']} ({res['duration']:.2f}s)")
        results.append(res)

        if res["status"] == "FAILED":
            has_failure = True
            print(f"    ERROR in {spec.name}: Review log file at {res['log_file']}", file=sys.stderr)
            if not args.continue_on_error:
                print("    Aborting remaining execution. (Use --continue-on-error to proceed anyway)", file=sys.stderr)
                break

    total_elapsed = time.perf_counter() - start_pipeline_time
    print_summary_table(results, total_elapsed)

    # Write JSON summary
    summary_payload = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_elapsed_sec": total_elapsed,
        "overall_status": "FAILED" if has_failure else "SUCCESS",
        "cli_args": sys.argv[1:],
        "results": results,
    }
    with open(LOGS_DIR / "LATEST_RUN.json", "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    return 1 if has_failure else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 5. Verification Method

To independently verify the runner architecture and its execution against the repository:

1. **Preflight Verification**:
   Inspect that the proposed reference implementation cleanly runs with Python's syntax checker:
   ```powershell
   E:\kash-paper\.venv\Scripts\python.exe -m py_compile analysis\run_all.py
   ```
2. **Help & Flag Inspection**:
   ```powershell
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --help
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --list
   ```
   *Expected Outcome:* Lists all 22+ modules across stages 0–5, identifies `a01` and `a02` as heavy, and reports scripts present vs. planned.
3. **Dry-Run Inspection**:
   ```powershell
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --quick --dry-run
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --stage 0 --dry-run
   ```
   *Expected Outcome:* Displays topological sequence; identifies `a01` and `a02` as `SKIP (cached)`.
4. **Execution of Quick Replication Suite**:
   ```powershell
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --quick
   ```
   *Expected Outcome:* Runs fast modules (`q01_data_quality`, `a02b_faithfulness`), skips heavy cache files without recomputing, skips planned scripts gracefully, prints formatted summary table, writes `logs/LATEST_RUN.json`, and exits with return code `0`.
5. **Stage 0 Isolation**:
   ```powershell
   E:\kash-paper\.venv\Scripts\python.exe analysis\run_all.py --stage 0
   ```
   *Expected Outcome:* Executes Stage 0 diagnostics, produces tables 02a–02f, 03b, and confirms 100% pass rate.
6. **Invalidation Conditions**:
   - Any invocation of external network endpoints, URLs, or external git repos.
   - Any overwrite of `data/cache/walk_graph.gpickle` or `data/cache/catchments_network.gpkg` during `--quick` or `--full` without `--force-heavy`.
   - Any unhandled exception or crash when an unwritten module in the registry is encountered.
