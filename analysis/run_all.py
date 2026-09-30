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
        outputs=(
            DERIVED_DIR / "a04_class_count.json",
            DERIVED_DIR / "a04_route_tiers.csv",
            TABLES_DIR / "table05_class_count.csv",
            TABLES_DIR / "table05b_classifier_agreement.csv",
        ),
        depends_on=("a03_index_weights",),
        estimated_runtime_sec=10.0,
    ),

    # ── Stage 3: Operational Diagnostics, Equity, & Scenarios ─────────────────────
    ModuleSpec(
        name="a10_network_diagnostics",
        script="a10_network_diagnostics.py",
        stage=3,
        description="Network diagnostics: route-km vs unique network-km, link duplication",
        is_heavy=False,
        inputs=(
            RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson",
            RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",
            RAW_DIR / "existing-routes.csv",
            RAW_DIR / "Kashmir_Stops_Master_v4.csv",
        ),
        outputs=(
            DERIVED_DIR / "a10_network_diagnostics.json",
            TABLES_DIR / "table05c_network_diagnostics.csv",
        ),
        depends_on=(),
        estimated_runtime_sec=15.0,
    ),
    ModuleSpec(
        name="a05_headway_timeofday",
        script="a05_headway_timeofday.py",
        stage=3,
        description="Time-of-day headways from hourly passenger counts",
        is_heavy=False,
        inputs=(RAW_DIR / "Hourly_Passenger_Count.csv",
                RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",
                RAW_DIR / "chalo_ridership.csv"),
        outputs=(DERIVED_DIR / "a05_headway_timeofday.json",
                 TABLES_DIR / "table05h_timeofday.csv",
                 TABLES_DIR / "table05h_timeofday_headways.csv",
                 TABLES_DIR / "table05h_timeofday_headways_meananchored.csv",
                 TABLES_DIR / "table05h_timeofday_fleet.csv"),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a11_coverage_accessibility",
        script="a11_coverage_accessibility.py",
        stage=3,
        description="Frequent-network coverage & Moran's I on uncovered surface",
        is_heavy=False,
        inputs=(CACHE_DIR / "catchments_network.gpkg", RAW_DIR / "kashmir_worldpop.tif",
                RAW_DIR / "kashmir_districts_osm.geojson"),
        outputs=(DERIVED_DIR / "a11_coverage_accessibility.json",
                 TABLES_DIR / "table05d_frequent_network.csv",
                 TABLES_DIR / "table05e_morans_i.csv"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=45.0,
    ),
    ModuleSpec(
        name="a12_equity_gini",
        script="a12_equity_gini.py",
        stage=3,
        description="Population-weighted accessibility Gini & map of losers",
        is_heavy=False,
        inputs=(CACHE_DIR / "catchments_network.gpkg",
                RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",
                RAW_DIR / "existing-routes.csv", RAW_DIR / "kashmir_worldpop.tif"),
        outputs=(DERIVED_DIR / "a12_equity_gini.json",
                 TABLES_DIR / "table05f_equity_gini.csv",
                 TABLES_DIR / "table05g_losers.csv"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=15.0,
    ),
    ModuleSpec(
        name="a13_transfers",
        script="a13_transfers.py",
        stage=3,
        description="0/1/2+ transfer shares & break-even transfer penalty",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson",
                RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",
                RAW_DIR / "existing-routes.csv",
                RAW_DIR / "Kashmir_Stops_Master_v4.csv",
                RAW_DIR / "gps" / "driver_days.csv"),
        outputs=(DERIVED_DIR / "a13_transfers.json",
                 DERIVED_DIR / "a13_transfer_od.csv",
                 TABLES_DIR / "table05i_transfers.csv",
                 TABLES_DIR / "table05i_transfers_sensitivity.csv",
                 TABLES_DIR / "table05i_transfers_breakeven.csv",
                 TABLES_DIR / "table05i_transfers_geomaudit.csv"),
        depends_on=(),
        estimated_runtime_sec=20.0,
    ),
    ModuleSpec(
        name="a06_deadhead",
        script="a06_deadhead.py",
        stage=3,
        description="Depot deadhead, bounded by two depot assumptions (no depot register)",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv", RAW_DIR / "Kashmir_Stops_Master_v4.csv"),
        outputs=(DERIVED_DIR / "a06_deadhead.json", TABLES_DIR / "table05k_deadhead.csv"),
        depends_on=("a13_transfers",),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a07_load_factor",
        script="a07_load_factor.py",
        stage=3,
        description="Offered capacity vs proxy peak demand (implied load factor)",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv", RAW_DIR / "chalo_ridership.csv"),
        outputs=(DERIVED_DIR / "a07_load_factor.json", TABLES_DIR / "table05l_load_factor.csv"),
        depends_on=("a05_headway_timeofday",),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a14_cost_emissions",
        script="a14_cost_emissions.py",
        stage=3,
        description="Cost per accessibility gain & emissions scenario range",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a14_cost_emissions.json", TABLES_DIR / "table05m_cost_emissions.csv"),
        depends_on=("a11_coverage_accessibility", "a06_deadhead"),
        estimated_runtime_sec=10.0,
    ),
    ModuleSpec(
        name="a15_scenarios",
        script="a15_scenarios.py",
        stage=3,
        description="Five operational policy scenarios & trade-off frontier",
        is_heavy=False,
        inputs=(RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",),
        outputs=(DERIVED_DIR / "a15_scenarios.json", TABLES_DIR / "table08_scenarios.csv"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=20.0,
    ),
    ModuleSpec(
        name="a16_peer_regression",
        script="a16_peer_regression.py",
        stage=3,
        description="Peer city regression: buses/1k vs population & density",
        is_heavy=False,
        inputs=(RAW_DIR / "peer_cities.csv",
                RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv"),
        outputs=(DERIVED_DIR / "a16_peer_regression.json",
                 TABLES_DIR / "table05j_peer_regression.csv"),
        depends_on=(),
        estimated_runtime_sec=5.0,
    ),

    # ── Stage 4: Uncertainty Analysis & Multi-Channel Validation ──────────────────
    ModuleSpec(
        name="a08a_catchment_grid",
        script="a08a_catchment_grid.py",
        stage=4,
        description="Catchment populations on a walk-budget / stop-spacing grid (~2.5 h)",
        is_heavy=True,
        cache_targets=(DERIVED_DIR / "a08a_catchment_grid.csv",),
        inputs=(CACHE_DIR / "walk_graph.gpickle", RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson"),
        outputs=(DERIVED_DIR / "a08a_catchment_grid.csv", DERIVED_DIR / "a08a_catchment_grid.json"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=9000.0,
    ),
    ModuleSpec(
        name="a08_sensitivity_oat",
        script="a08_sensitivity_oat.py",
        stage=4,
        description="One-At-a-Time sensitivity sweeps across 11 parameters",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a08a_catchment_grid.csv",),
        outputs=(DERIVED_DIR / "a08_sensitivity_oat.json", TABLES_DIR / "table07a_oat_sensitivity.csv"),
        depends_on=("a08a_catchment_grid", "a04_class_count"),
        estimated_runtime_sec=60.0,
    ),
    ModuleSpec(
        name="a09_monte_carlo_sobol",
        script="a09_monte_carlo_sobol.py",
        stage=4,
        description="Monte Carlo 5k draws using v04 pace prior & Sobol indices",
        is_heavy=False,
        inputs=(DERIVED_DIR / "a08a_catchment_grid.csv", RAW_DIR / "gps" / "corridor_profiles.csv"),
        outputs=(DERIVED_DIR / "a09_monte_carlo_sobol.json", TABLES_DIR / "table07b_mc_intervals.csv",
                 TABLES_DIR / "table07c_sobol.csv"),
        depends_on=("a08a_catchment_grid", "v04_gps_validation"),
        estimated_runtime_sec=600.0,
    ),
    ModuleSpec(
        name="v01_spatial_crossval",
        script="v01_spatial_crossval.py",
        stage=4,
        description="Validation V1: OSM building footprint spatial cross-val",
        is_heavy=False,
        inputs=(CACHE_DIR / "catchments_network.gpkg", DERIVED_DIR / "a02_catchments.csv"),
        outputs=(DERIVED_DIR / "v01_spatial_crossval.json", TABLES_DIR / "table06d_v01_buildings.csv"),
        depends_on=("a02_network_catchments",),
        estimated_runtime_sec=30.0,
    ),
    ModuleSpec(
        name="v02_benchmark",
        script="v02_benchmark.py",
        stage=4,
        description="Validation V2: CHALO benchmark with circularity disclosure",
        is_heavy=False,
        inputs=(RAW_DIR / "chalo_ridership.csv", RAW_DIR / "chalo_deployed_buses.csv"),
        outputs=(DERIVED_DIR / "v02_benchmark.json", TABLES_DIR / "table06f_v02_benchmark.csv"),
        depends_on=(),
        estimated_runtime_sec=10.0,
    ),
    # ── Stage 5: Publication Figures & Tables ─────────────────────────────────────
    ModuleSpec(
        name="figures_tables",
        script="fig_generate_all.py",
        stage=5,
        description="Publication Figures 1-8b and manuscript tables compilation",
        is_heavy=False,
        inputs=(),
        outputs=(),
        depends_on=(),
        estimated_runtime_sec=60.0,
    ),
]

REGISTRY_BY_NAME = {m.name: m for m in MODULE_REGISTRY}


def topological_sort(modules: list[ModuleSpec]) -> list[ModuleSpec]:
    """Return modules sorted in valid execution dependency order, prioritizing stage order."""
    selected_names = {m.name for m in modules}
    graph = {m.name: [dep for dep in m.depends_on if dep in selected_names] for m in modules}
    deps_count = {m.name: len(graph[m.name]) for m in modules}
    queue = sorted([name for name, count in deps_count.items() if count == 0], key=lambda n: (REGISTRY_BY_NAME[n].stage, n))
    result = []
    
    while queue:
        curr = queue.pop(0)
        result.append(REGISTRY_BY_NAME[curr])
        for name, deps in graph.items():
            if curr in deps:
                deps_count[name] -= 1
                if deps_count[name] == 0:
                    queue.append(name)
                    queue.sort(key=lambda n: (REGISTRY_BY_NAME[n].stage, n))
                    
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
