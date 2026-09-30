# STATUS — Kashmir Route-Rationalisation Paper

Single source of truth for project state. Updated at the end of each working session. Anything not listed here as **DONE** is not done, regardless of what exists on disk.

- **Repo:** `E:\kash-paper` (paper companion; ready for git init)
- **Engine repo:** `E:\kash` — read-only source of the published plan; left as working history and **not modified by this project**
- **App-GPS repo:** `E:\bus-sathi-trace` — read-only source of the observational layer
- **Python:** 3.14.2 venv at `E:\kash-paper\.venv`
- **Last updated:** 2026-09-03 (Session Pause & State Freeze)

> **Superseded 2026-09-30.** The sections below describe the 2026-09-03 state and are kept for history.
> Current state: `PAPER_COMPLETION_PLAN.md` §1 (refreshed 2026-09-30), the claim ledger
> (`paper/CLAIM_LEDGER.md`, CL-01…CL-61) and the decision queue (`paper/PENDING_DECISIONS.md`, Part G).
> All 22 registered analysis modules are written; §1–§8 and front matter are drafted; decisions
> D1–D5, D13 and D20–D25 wait on the team.

---

## 0. Locked Decisions — Do Not Relitigate

| Decision | Choice | Consequence |
|---|---|---|
| Study area | **Kashmir Division only** (10 districts) | 614 permits + 30 e-bus → 644 rows → 186 active; fleet 1,011; denominator 6,584,762. The co-authors' §3 "Srinagar Metropolitan City" framing is wrong and must be rewritten. |
| Validation | **V4 via existing app GPS only** | V3 expert AHP/Delphi panel and the field-enumeration survey **will not be collected**. Both must be reported plainly as not performed. Neither may be fabricated. |
| Publication | **New clean paper-companion repo** | The engine repo stays untouched. |

### Standing Constraints

1. **Never write "validated against ridership."** GPS carries no demand signal. V4 validates the *supply* chain (geometry → cycle time → fleet) only. The defensible phrasing is "decision-robust" or "observational GPS validation".
2. **Disclose the CHALO circularity up front** in §6, not at the end: e-bus ridership both calibrates the plausibility term and is offered as benchmark V2, so V2 is a consistency check, not an independent validation.
3. **No fabricated data.** V3 and the field survey are absent; say so.
4. **Do not sum per-route walkshed populations** — they overlap. Only the deduplicated union is a network total.
5. Target: *Transport Policy*, 9,000–10,000 words, 8 figures + F8b, 8 tables.

---

## 1. Ownership — Prashant's Sections

| Section | Words | Co-owners | State |
|---|---|---|---|
| Abstract | — | Ankit, Sharvesh | **DRAFT COMPLETE** — `paper/sections/00_abstract.md`; ~230 w on locked numbers; provisional pending §5 evaluation figures |
| **§4 Methodology** | **2,300** | **sole owner** | **DRAFT COMPLETE** — `paper/sections/04_methodology.md`; Equations 1–14 + Algorithm 1, reproducible from text; every number cites CL/F |
| §5 Results | 2,400 | Misti | **PARTIAL** — `paper/sections/05_results.md`; diagnosis §5.1–§5.4 complete + sourced; design/eval/stress §5.5–§5.13 scaffolded, marked ⏳ pending modules a04/a10–a15/a08/a09 |
| §6 Validation | 900 | Avny, Krishnan | **DRAFT COMPLETE** — `paper/sections/06_validation.md`; V4 established, V1/V2/V5/V6 method-fixed & pending, V3 + field survey reported NOT performed |
| §8 Conclusions | 400 | Ankit, Sharvesh | **DRAFT COMPLETE** — `paper/sections/08_conclusions.md`; six paragraphs + four future directions + "the sentence to design against" |

**Prose drafted 2026-09-04** (Prashant's sections, in `paper/sections/`): `00_abstract.md`, `04_methodology.md`,
`05_results.md`, `06_validation.md`, `08_conclusions.md`. Not owned by Prashant and still unwritten: §1 Intro,
§2 Lit, §3 Study area, §7 Discussion — the attachment ("Copy of Paper Route Rationale_AK.pdf") already contains
co-author draft prose for §1, a Policy-Failure institutional block, §6 field validation, and §7 Policy Contribution.

### Open reconciliations forced by the AK attachment (for the co-authors — NOT resolved unilaterally)

1. **Stale-Srinagar vs Kashmir-Division scope, inside the co-authors' own draft.** The attachment's §1.4/§1.5
   already use the correct 10-district / 6.58M / "644 permits → 186 corridors" framing (matches the locked
   decision), but its Abstract plan, Highlights, and the "Policy Failure" block still carry the barred
   "342 permits → 207 routes / ~1,009 fleet / Srinagar Municipal Corporation" framing. Prashant's sections are
   written in the locked Kashmir-Division framing; the Abstract/Highlights/§3-header/Policy-Failure block (owned by
   Misti/Krishna/Ankit) must be brought into line. Barred legacy metrics are enumerated in `CLAIM_LEDGER.md §4`.

2. **§6 field-observation table vs the locked "field survey NOT performed / not fabricated" decision.** The
   attachment's §6 contains a drafted field-observation study (10 morning corridor sessions, 1–12 August, named
   Srinagar corridors with bus counts / frequency / waiting time / overlap) plus bus-association cross-checking.
   This contradicts the locked decision and `CLAIM_LEDGER.md` (CL-20 caveat + Table 7: V3 and field enumeration
   = NOT PERFORMED). **§6 as drafted follows the ledger** (reports no field enumeration/boarding survey was
   conducted) and does **not** import those counts, to avoid publishing unverified/fabricated field data. If a
   co-author genuinely conducted that exercise, it must be re-added **only** with documented method + a data file
   + a new ledger claim ID — an editorial decision for the §6 owners (Avny/Krishnan), not made here.

---

## 2. DONE

### 2.1 Infrastructure & Phase 0 Baseline
- [x] venv, Python 3.14.2, all scientific dependencies verified.
- [x] `analysis/common.py` — shared paths, parameter block, loader, metrics, `RANDOM_SEED = 20260823`.
- [x] `a00_stage_inputs.py` — all raw inputs staged in `data/raw/`.
- [x] Repository hygiene complete: `README.md`, `requirements.txt`, `.gitignore`, `LICENSE` (GPL-3.0), `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`.
- [x] `logs/WORK_REGISTER.md` — multi-worker concurrency protocol and active task ledger.
- [x] `data/MANIFEST.md` — comprehensive inventory of 20 raw datasets + 3 caches with source, licence, and SHA-256 hashes.
- [x] `paper/CLAIM_LEDGER.md` — master claim ledger registering `CL-01` through `CL-36` with denominators, universes, and manuscript mapping.
- [x] Master pipeline runner `analysis/run_all.py` supporting `--stage`, `--module`, `--quick`, and `--full`.
- [x] Comprehensive independent test suite (`tests/`) with **53 passed, 0 failed, 2 skipped** (Checkers A–F, unit tests, pipeline tests).

### 2.2 Analysis Modules Executed & Verified

| Module | Status | Runtime | Outputs | Findings / Scope |
|---|---|---|---|---|
| `q01_data_quality.py` | **PASSED** | 8.6s | `q01_data_quality.json`, tables 02a–02f | **F1–F6** (Permits, Denominator, OSM completeness, Road density) |
| `a01_build_walk_graph.py` | **PASSED** | ~9 min | `data/cache/walk_graph.gpickle` (77 MB) | 961,927 nodes / 973,569 edges / 23,323 km |
| `a02_network_catchments.py` | **PASSED** | 69 min | `a02_catchments.csv`, `catchments_network.gpkg`, table 03a | **F7, F8** (Walkshed coverage 35.5% → 24.2%) |
| `a02b_faithfulness.py` | **PASSED** | 1.9s | `a02b_faithfulness.{csv,json}`, table 03b | **F9** (Geometry faithfulness, 44 substituted distances) |
| `v04_gps_validation.py` | **PASSED** | 2.7s | `v04_corridor_comparison.csv`, `v04_fleet_consequence.csv`, `v04_gps_validation.json`, tables 06a–06c | **F3, F10–F12** (Observational GPS validation, Cap binding 90.9%, WLS dwell model, fleet self-test 0 mismatches) |
| `a03_index_weights.py` | **PASSED** | 14.7s | `a03_index.csv`, `a03_index_weights.json`, tables 04a–04b | Equal / entropy / PCA weights; AHP marked not performed (`ahp_weights_derived=false`) |

### 2.3 Authoritative Findings Established
- **F1**: Permit register, not route register. 614 rows = 157 distinct corridors. Decomposition: 71.0 pp change-of-unit + 0.2 pp consolidation. 156/157 corridors retained (99.4%).
- **F2**: WorldPop 2026 (6,584,763) vs Census 2011 (6,888,475) ratio 0.956 (−0.30%/yr implied CAGR).
- **F3**: Modelled runtime understates observed: MAPE(OSRM vs in-motion) 65.1%, MAPE(plan vs observed one-way) 47.6%, median plan/observed 0.51.
- **F4**: Observed recurring activity is a lower bound (66/186 routes in GPS), not dormancy.
- **F5**: POIs are 65.3% concentrated in Srinagar (1,588 / 2,431 POIs).
- **F6**: ρ(population density, road density) = 0.915 across districts; licenses OSM walk graph.
- **F7**: 142 consistent routes (median error 0.245%, r = 0.995); 44 substituted road distances diagnosed.
- **F8**: Network catchments overstate population served by 37.4% median; deduplicated network overstatement 31.9%; headline coverage revised from 35.5% to 24.2%.
- **F9**: Embedded tourist multiplier of 1.3 on 8 routes sizes at 285,914 synthetic headcount.
- **F10**: Sanity cap binds 90.9% of routes (169/186); caps sit below observed pace (Urban 4.0 vs 4.62 min/km).
- **F11**: Moving-speed congestion multiplier (÷2.2) reproduces observed speed at +1.4% bias; fixed dwell rate (1.0 min/km) unsupported (observed 1.76 min/km, OLS R² = 0.03).
- **F12**: Dual GPS coverage metrics: `obs_frac` (geometry on bus-used road, 183/186 > 0) vs `observed_status` (recurring service, 66/186).

---

## 3. IN PROGRESS / READY FOR IMMEDIATE EXECUTION

The repository execution state is cleanly frozen and all background agents have been terminated.

### Immediate Next Tasks to Resume:

1. **`analysis/a04_class_count.py` (Phase 2 / M2 completion):**
   - Evaluate Jenks GVF across 2–7 classes to identify the elbow objectively (expected at 3 tiers).
   - Compute pairwise Cohen's kappa and confusion matrices comparing Jenks, quantiles, and k-means.
   - Output: `data/derived/a04_class_count.json`, route tier assignments, inputs for Table 5 and Figure 6.

2. **Phase 3 Modules (Operational, Equity, Scenarios):**
   - `a10_network_diagnostics.py` (route-km to network-km ratio, corridor overlap).
   - `a05_headway_timeofday.py` (parse `Hourly_Passenger_Count.csv` with `skiprows=1`).
   - `a11_coverage_accessibility.py` (Moran's I on uncovered population, frequent network).
   - `a12_equity_gini.py` (population-weighted Gini, explicit identification of losers).
   - `a13_transfers.py` (0/1/2+ transfer shares, transfer penalty).
   - `a06_deadhead.py`, `a07_load_factor.py`, `a14_cost_emissions.py`, `a15_scenarios.py`.

3. **Phase 4 (Uncertainty & Multi-Channel Validation):**
   - `a08_sensitivity_oat.py` (10-parameter OAT sweep).
   - `a09_monte_carlo_sobol.py` (5,000 draws using v04 GPS pace prior; Sobol indices with CIs).
   - `v01_spatial_crossval.py` (OSM building footprints) & `v02_benchmark.py` (CHALO consistency).
   - Table 7 synthesis.

4. **Phase 5 & 6 (Figures, Tables & Manuscript Drafting):**
   - Figures 1–8b scripts (`analysis/figXX_*.py`).
   - Tables 1–8 generation.
   - Drafting §4, §5, §6, §8, Abstract following Claim Ledger mapping.

---

## 4. How to Resume Execution

To resume work in a future session:

1. Activate project virtual environment:
   ```powershell
   E:\kash-paper\.venv\Scripts\Activate.ps1
   ```
2. Verify baseline integrity and test harness:
   ```powershell
   pytest tests/
   python analysis/run_all.py --quick
   ```
3. Check `logs/WORK_REGISTER.md` to claim the next task (`a04_class_count.py`).
4. Implement `analysis/a04_class_count.py` following Phase 2 acceptance gate.
