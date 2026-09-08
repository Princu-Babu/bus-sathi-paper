# Gap 1 — Missing Analysis Modules

**Severity: CRITICAL. This is the largest gap in the project.**

`python analysis/run_all.py --list` on 2026-09-08 reports **6 modules written, 16 PLANNED (not on
disk)**. Every "⏳ pending" subsection in §5 and every "planned" validation channel in §6 traces to a
module in this list. Until these run, the corresponding numbers **do not exist** and must not be
written into the paper as if they do.

## Written and executed (6)

`q01_data_quality`, `a01_build_walk_graph`, `a02_network_catchments`, `a02b_faithfulness`,
`v04_gps_validation`, `a03_index_weights`.

## Not written — PLANNED stubs (16)

| Module | Stage | Blocks (manuscript) | What it must produce | Est. effort |
|---|---|---|---|---|
| `a04_class_count` | 2 | §5.8, Fig 6, Table 5 | Jenks GVF k=2–7, elbow, Cohen's κ vs quantile/k-means | S (data ready in `a03_index.csv`) |
| `a10_network_diagnostics` | 3 | §5.5, Table 4 | route-km, unique network-km, overlap ratio | S |
| `a05_headway_timeofday` | 3 | §5.6 inputs, Table 6 | time-of-day headways from `Hourly_Passenger_Count.csv` (skiprows=1) | S |
| `a11_coverage_accessibility` | 3 | §5.6, §5.10 | frequent-network coverage; Moran's I on uncovered surface | M (needs `esda`/`libpysal`) |
| `a12_equity_gini` | 3 | §5.9 | population-weighted accessibility Gini; named losers | M |
| `a13_transfers` | 3 | §5.11 | 0/1/2+ transfer shares; break-even transfer penalty | M |
| `a06_deadhead` | 3 | (supports §5.12) | depot deadhead 5–12% bus-hours | S |
| `a07_load_factor` | 3 | (supports §5.12) | offered capacity vs proxy peak demand | S |
| `a14_cost_emissions` | 3 | §5.12 | cost per accessibility gain; emissions envelope | M |
| `a15_scenarios` | 3 | §5.13 | 5 scenarios on coverage/fleet/equity frontier | M |
| `a16_peer_regression` | 3 | §5.7 | buses/1k vs pop & density; prediction interval | S |
| `a08_sensitivity_oat` | 4 | §4.10, §5 robustness | 10–11 param OAT sweep | M |
| `a09_monte_carlo_sobol` | 4 | §5.7 interval fleet, V5, V6 | 5,000-draw MC w/ GPS prior; Sobol indices + CIs | L (headline uncertainty result) |
| `v01_spatial_crossval` | 4 | §6 V1 | OSM building-footprint ρ vs index | M (needs building layer — see note) |
| `v02_benchmark` | 4 | §6 V2 | CHALO-scaled fleet/headway ratio ±15%, circularity | S |
| `fig_generate_all` | 5 | ALL figures + Tables 5/7/8 | Figures 1–8b, table compilation | L |

Effort: S ≈ <½ day, M ≈ ½–1 day, L ≈ 1–2 days each, assuming the analyst knows the codebase.

## Hard dependencies / data you may not have

- **`v01_spatial_crossval`** needs an **OSM building-footprint layer** for Kashmir. Confirm it is
  downloaded and staged in `data/raw/` before promising V1. If not present, V1 stays "planned."
- **`a11`/`a12`** need `esda` + `libpysal` (Moran's I, spatial weights). Confirm installed in `.venv`.
- **`a09`** is the single most important missing module: the **interval fleet** and the entire V5/V6
  robustness story depend on it. The Abstract currently promises an interval fleet — that promise is
  **unbacked** until `a09` runs.

## Consequence for the Abstract and headline claims

The Abstract cites the 37.4% overstatement and 24.2% coverage (real, from `a02`) — those are safe. But
any Abstract/Conclusion language implying a *completed* uncertainty analysis, tier-stability rate, or
scenario frontier is **writing a cheque the pipeline has not cashed.** Keep those provisional until the
modules run.

## Recommended execution order (fastest path to a defensible §5)

1. `a04_class_count` → unlocks §5.8 + tier figure (data already on disk).
2. `a10_network_diagnostics`, `a16_peer_regression`, `a05_headway_timeofday` → cheap, unlock §5.5–§5.7 text.
3. `a11_coverage_accessibility` → §5.6 frequent-network coverage (a genuinely strong public metric).
4. `a08` then `a09` → the uncertainty spine; **do not** write §5.7/V5/V6 before these.
5. `a12`, `a13`, `a14`, `a15` → equity, transfers, cost, scenarios.
6. `v01`, `v02` → close the remaining validation channels.
7. `fig_generate_all` → figures + remaining tables, last.

*Basis: `analysis/run_all.py` MODULE_REGISTRY and `--list` output, 2026-09-08.*
