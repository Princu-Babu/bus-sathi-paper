# MASTER CONTEXT — Kashmir Bus Route-Rationalisation Paper

**Purpose.** This is the single drop-in briefing for any person or agent picking up this project. Read
this and you have the whole story — tech stack, data, the analysis, the manuscript, what is done, what
is missing, and the non-negotiable rules — without having to read three GitHub repos. Written
2026-09-08. If numbers here disagree with `paper/CLAIM_LEDGER.md`, **the ledger wins** and this file is
stale.

---

## 1. What this project is (in three sentences)

Most Indian cities that need bus-network reform have no origin–destination or ridership data, so the
cheapest useful intervention — rationalising an inherited minibus-permit network — is exactly the one
for which the required demand data are missing. This paper presents a **fully open-data, demand-free
framework** for bus route rationalisation and fleet sizing, applied to the **10 districts of Kashmir
Division, India (6,584,762 residents)**, using only a gridded population surface, OpenStreetMap layers,
a road-routing engine, and the digitised stage-carriage permit register. The headline methodological
finding: **straight-line catchments overstate who is served by a median of 37.4% per route**, cutting
defensible division coverage from 35.5% to 24.2%.

**Target journal:** *Transport Policy* (Elsevier). **Length target:** 9,000–10,000 words, 8 figures +
F8b, 8 tables. **Framing slogan:** *"planning what you cannot count."*

---

## 2. The three repositories

| Repo | Role | Local path | Remote | State |
|---|---|---|---|---|
| **Paper companion** | The manuscript + analysis pipeline + claim ledger. **This repo.** | `E:\kash-paper` | → `github.com/Princu-Babu/bus-sathi-paper` (to be pushed) | active |
| **Engine** | Source of the published operational plan (v3.4.5-geo). **READ-ONLY — never modified by the paper project.** | `E:\kash` | `github.com/Princu-Babu/kashmir-transit-rationalisation` | frozen |
| **App-GPS / trace intelligence** | Source of the observational GPS layer (driver-app traces → corridors). **READ-ONLY.** | `E:\bus-sathi-trace` | `github.com/Princu-Babu/bus-sathi-trace-intelligence` (public) | frozen |

The engine repo also drives a **dashboard** (`github.com/GrostesqueChip/bus-sathi-dashboard`, Next.js,
`E:\dash\bus-sathi-dashboard`) which carries the current authoritative numbers publicly.

> **We are the makers of the whole system.** The dashboard + `E:\kash-paper` numbers are the LATEST and
> authoritative. Co-authors were originally shared an OLD report; a corrections briefing for them lives
> at `paper/Corrections_for_Coauthors.pdf` (generator: `paper/make_corrections_pdf.py`).

---

## 3. Tech stack

- **Python 3.14.2**, venv at `E:\kash-paper\.venv` — invoke as `./.venv/Scripts/python.exe`.
- Scientific: pandas, numpy, geopandas, rasterio, rasterstats, shapely, scikit-learn, jenkspy,
  statsmodels, networkx, SALib (Sobol), esda + libpysal (Moran's I), matplotlib 3.11.1, reportlab 5.0.1.
- **External services the *engine* needed** (not required to re-run the *paper* analysis, which consumes
  staged engine outputs): OSRM in Docker on localhost:5000; WorldPop raster.
- **Reproducibility spine:** `analysis/run_all.py` (staged pipeline), fixed `RANDOM_SEED = 20260823`,
  `tests/` (52 passed / 2 skipped), `CLAIM_LEDGER.md` (every number → a module).
- Engine's own Python is a *separate* conda env at `D:\plotting\ana` — that is the ENGINE repo's
  toolchain, documented in `E:\kash\CLAUDE.md`; the paper repo does not use it.

---

## 4. The data (what the analysis actually consumes)

Staged in `E:\kash-paper\data\raw/` (heavy rasters/graphs gitignored; see `.gitignore` + `data/MANIFEST.md`):

| File | What | Key claim |
|---|---|---|
| `existing-routes.csv` | 614 digitised RTO stage-carriage permits | CL-01 |
| `Rationalised_Routes_Kashmir_v3.csv` | Engine v3.4.5 output — 644 rows, 186 active, fleet 1,011 | CL-05, CL-06, CL-36 |
| `pois.csv` | 2,431 OSM POIs, 63 categories, 3 tiers | CL-20, CL-21 |
| `kashmir_worldpop.tif` | WorldPop 2026 population raster (gitignored) | CL-11 |
| `census2011_kashmir_districts.csv` | Census 2011 benchmark, 10 districts | CL-12 |
| `kashmir_districts_osm.geojson` / `..._tehsils_osm.geojson` | OSM admin boundaries (10 districts / 39 tehsils) | denominators |
| `Hourly_Passenger_Count.csv` | Time-of-day counts (parse with `skiprows=1`) — feeds `a05` | §5.6 |
| `gps/*.csv` | Driver-GPS derived: corridor profiles, permit_observed, route_evidence, reality_check (43,809 runs, ~157 drivers, Feb–Jun 2026) | CL-18, F3/F10–F12 |
| `chalo_ridership.csv` / `chalo_deployed_buses.csv` | CHALO e-bus published aggregates — calibration anchor (κ=0.18) AND benchmark V2 (→ circular, disclose) | §6.1, V2 |

**Data integrity rules:** (a) the GPS layer carries **zero ridership signal** — it is supply-side only;
(b) per-route walkshed populations **overlap and must never be summed** — only the deduplicated union is
a network total; (c) the GPS folder uses hashed driver IDs (e.g. `036e3d55480d`) — check anonymisation
before any public push, and the source Firestore admin key in the trace repo is gitignored (rotate it).

---

## 5. The method, in one pass (what §4 formalises)

1. **Deconstruct the permit register.** 614 permits → 157 undirected O–D corridors (mean 3.91
   permits/corridor, max 42 on Hazratbal–LD). The "71% route reduction" is 71.0pp change-of-unit +
   0.16pp real consolidation; **156/157 corridors retained (99.4%)**. (F1)
2. **Build catchments on a walkable pedestrian graph**, not Euclidean buffers. Multi-source Dijkstra on
   the OSM foot network; `A_net = ∪ B(v, min(400−d(v), τ))`, τ=100 m. Network catchment is an *upper
   bound* on the true walkshed → the measured overstatement is a *lower bound* on true bias. (F7, F8)
3. **Score routes by a Composite Demand Index (CDI):** `β·pop + (1−β)·opportunity`, β=0.50, min-max
   normalised, length-normalised, population capped at P95. Weights by equal / entropy / PCA (**AHP not
   collected** — forward work). (Table 4a)
4. **Consolidate** on spatial overlap coefficient θ=0.65; **tier** by Jenks natural breaks + GVF
   (k=2–7, elbow expected at 3), cross-checked with Cohen's κ vs quantile/k-means.
5. **Size fleet** from cycle time: `operating = ceil(cycle/headway)`, `fleet = ceil(operating·1.15)`
   with class floors. A per-km sanity cap was *intended as a guardrail* but **binds on 90.9% of routes**
   and sits *below* real GPS pace — so it, not demand, silently governs fleet. (F10)
6. **Validate the supply chain** (not demand) via 6 convergent channels — see §7 below.

Headways: Urban 15 / Peri-Urban 20 / e-bus backbone 15 / rural demand-responsive capped at 50-min max
wait. Fleet: **1,011 buses (187 HPV / 754 MPV / 70 LPV)**, +68.5% over ~600 baseline, 43 buses/lakh
served (inside MoHUA 40–60 benchmark).

---

## 6. The authoritative numbers (memorise these; legacy values are BARRED)

| Metric | Authoritative | BARRED legacy value |
|---|---|---|
| Study area | Kashmir Division, 10 districts | ~~Srinagar Metropolitan City~~ |
| Permits | **614** | ~~342~~ |
| Corridors | **157** | — |
| Active routes | **186** (32 trunk / 154 feeder) | ~~207~~ |
| "Reduction" | **99.4% corridor retention** | ~~39% route reduction~~ |
| Coverage | **24.2%** of division (network walkshed) | ~~95.7%~~ |
| Fleet | **1,011** buses | ~~1,009~~ |
| Denominator | **6,584,762** residents | ~~1.66M Srinagar UA~~ |
| Catchment overstatement | **37.4%** median per route | — |
| GPS runs | **43,809** (supply-side) | — |
| Validation claim | "supply-side GPS validation / decision-robust" | ~~"validated against ridership"~~ |
| Engine baseline | **v3.4.5-geo** (frozen) | ~~v4 / mixed~~ |

Full ledger CL-01 … CL-36 in `paper/CLAIM_LEDGER.md`. Barred metrics enumerated there in §4.

---

## 7. The six-channel validation protocol (V1–V6) — and its honesty constraints

| Ch | Target | Status | Note |
|---|---|---|---|
| V1 | Spatial cross-val vs OSM building footprints (ρ>0.60) | **Planned** (`v01`) | needs building layer staged |
| V2 | CHALO benchmark consistency (±15%) | **Planned** (`v02`) | **circular** — consistency check, NOT independent validation; disclose up front |
| V3 | Expert AHP/Delphi weight elicitation (W>0.70) | **Forward work (§6.4)** | **not collected; must NOT be fabricated**; weights meanwhile equal/entropy/PCA |
| V4 | Supply-side GPS (43,809 runs) | **ESTABLISHED** (`v04`) | the one executed observational channel; moving speed passes (+1.4%), dwell fails |
| V5 | Sobol global sensitivity | **Planned** (`a09`) | |
| V6 | Decision robustness — fleet 90% CI, tier stability >80% | **Planned** (`a09`) | interval fleet depends on this |

**Standing honesty rules (never violate):** never write "validated against ridership"; disclose the
CHALO circularity before the V2 result; never fabricate V3 or field-survey data; §6.4 frames the
demand-side loop (expert elicitation + on-street boarding survey) as **near-term work**, not as done.
The honest ceiling on the whole paper is **decision-robustness of the supply plan, not demand
validation.**

---

## 8. Manuscript state (what exists in `paper/sections/`)

| § | Section | Owner | State |
|---|---|---|---|
| Abstract | — | Prashant+Ankit+Sharvesh | **Draft** (318 w) — headline figures provisional |
| §1 | Introduction | co-authors | **ABSENT** (draft only in AK PDF) |
| §2 | Literature review | co-authors | **ABSENT** |
| §3 | Study area & data | co-authors (Misti/Krishna) | **ABSENT** — must use Kashmir-Division framing |
| §4 | **Methodology** | **Prashant (sole)** | **COMPLETE** (2,634 w) — Eqs 1–14, Algorithm 1, 10 QA gates |
| §5 | Results | Prashant+Misti | **HALF** — §5.1–5.4 done; §5.5–5.13 stubs (blocked by missing modules) |
| §6 | Validation | Prashant+Avny+Krishnan | **Draft** (1,170 w) — V4 done; §6.4 future-work framing |
| §7 | Discussion | co-authors | **ABSENT** |
| §8 | Conclusions | Prashant+Ankit+Sharvesh | **COMPLETE** (450 w) |

**Prashant's owned prose (§4, §6, §8, half of §5) is the most complete part.** The co-authored sections
(§1, §2, §3, §7) are not in this repo. **Section numbering is unreconciled** (AK PDF uses a 6-section
scheme; repo uses 8) — must be fixed before cross-refs finalise.

Tables: 12 of ~15 exist (`paper/tables/`: 2a–2f, 3a–3b, 4a–4b, 6a–6c). Missing: Table 5 (tiers, needs
`a04`), Table 7 (validation synthesis), Table 8 (scenarios, needs `a15`). **Figures: 0 of ~9 generated.**
**References: NO `.bib` file exists** — a desk-reject risk.

---

## 9. Analysis pipeline state (the biggest gap)

`python analysis/run_all.py --list` → **6 of 22 modules written**.

- **Written & executed (6):** `q01_data_quality`, `a01_build_walk_graph`, `a02_network_catchments`,
  `a02b_faithfulness`, `v04_gps_validation`, `a03_index_weights`.
- **PLANNED stubs (16):** `a04_class_count`, `a10_network_diagnostics`, `a05_headway_timeofday`,
  `a11_coverage_accessibility`, `a12_equity_gini`, `a13_transfers`, `a06_deadhead`, `a07_load_factor`,
  `a14_cost_emissions`, `a15_scenarios`, `a16_peer_regression`, `a08_sensitivity_oat`,
  `a09_monte_carlo_sobol`, `v01_spatial_crossval`, `v02_benchmark`, `fig_generate_all`.

`a09` is the single most important missing module: the **interval fleet** and the entire V5/V6
robustness story depend on it. Until a module runs, its numbers **do not exist and must not be written
as if they do.** Full detail + recommended execution order: `paper/gaps/01_MISSING_ANALYSIS_MODULES.md`.

---

## 10. The brutally-honest gap analysis (read before believing the paper is close)

Lives in `paper/gaps/`:
- `00_GAP_ANALYSIS_MASTER.md` — index + "not submittable today" headline judgement + DONE table.
- `01_MISSING_ANALYSIS_MODULES.md` — 16 of 22 modules unwritten; execution order.
- `02_MISSING_MANUSCRIPT_SECTIONS.md` — 4 sections absent, §5 half, 0 figures, no references.
- `03_METHODOLOGICAL_RISKS.md` — the 8 things a hostile-but-fair reviewer will attack (R1 demand-index
  gap; R2 n=5 corridors; R3 tourist multiplier; R4 τ; R5 CHALO circularity; R6 self-test tautology;
  R7 WorldPop<Census; R8 Srinagar-centric GPS).
- `04_LITERATURE_POSITIONING.md` — canonical citations to add + how we differ from Gutiérrez &
  García-Palomares (2008), Biba et al. (2010), El-Geneidy et al. (2014).
- `05_SUBMISSION_READINESS_CHECKLIST.md` — references, highlights, CRediT, competing interests, data
  availability, **GPS ethics/consent** (can sink the paper), figure standards, cover letter.

**One-line honest summary:** the *diagnostic spine* (permit deconstruction + network-catchment
correction + supply-side GPS validation) is real, reproducible, and genuinely novel in combination — but
more than half the analysis pipeline is unwritten, four of eight sections don't exist, there are no
figures and no reference list, and the headline runtime finding rests on five matched corridors. It is
weeks of honest work, not days.

---

## 11. Non-negotiable rules (the guardrails, collected)

1. **No fabrication.** V3 expert panel and field/boarding survey are NOT collected — never invent them.
2. **Never "validated against ridership."** Say "decision-robust" / "supply-side validation."
3. **Disclose CHALO circularity up front** in §6.
4. **Never sum per-route walksheds** — only the deduplicated union is a network total.
5. **Every manuscript number cites a CL/F ID.** No untraced numbers.
6. **Engine repo (`E:\kash`) is read-only** — the paper project must not modify it.
7. **Legacy metrics are barred** (342/207/39%/95.7%/1,009/Srinagar-metro) — see §6 table above.
8. **Don't advertise "fully reproducible pipeline"** while 16 of 22 modules are stubs — scope the claim
   to what actually executes.
9. **A number that has no executed module does not exist** — do not write it into the paper.
10. **Verify against the repo, not memory** — if this file and the ledger/`run_all --list` disagree,
    the live repo wins.

---

## 12. Immediate next actions (priority order)

1. Start the **GPS ethics/consent** conversation with the team — it gates whether §6 can use its
   strongest evidence (`gaps/05`).
2. Create **`paper/references.bib`** (`gaps/04`) — desk-reject risk without it.
3. Run the cheap unlocking modules — `a04` (tiers/Table 5/Fig 6), `a10`, `a16`, `a05` — then `a11`, then
   the uncertainty spine `a08`→`a09` (`gaps/01`).
4. Write the four missing sections (§1, §2, §3, §7) — co-author owned — and **reconcile section
   numbering**.
5. Generate figures + Tables 5/7/8 (`fig_generate_all`), last.
6. Front/back matter: highlights, CRediT, competing interests, cover letter.

*This file is a snapshot for 2026-09-08. Regenerate the counts (`run_all.py --list`, `pytest`) if you
suspect it is stale.*
