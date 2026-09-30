# MASTER CONTEXT — Kashmir Bus Route-Rationalisation Paper

**Read this first.** It is the single drop-in briefing for any teammate or AI assistant picking up the
project: what it is, where everything lives, what is done, what is open, and the rules that must not be
broken. **Rewritten 2026-09-30** after every analysis module had run. If a number here disagrees with
`paper/CLAIM_LEDGER.md`, the ledger wins.

---

## 1. The project in four sentences

Most Indian cities that need bus-network reform have no origin–destination or ridership data, so the
cheapest useful reform — rationalising an inherited private-permit network — is the one their data least
support. This paper presents an **open-data, demand-free framework** for route rationalisation and fleet
sizing, applied to the **ten districts of Kashmir Division (6,584,762 residents)**, using a gridded
population surface, OpenStreetMap, a routing engine and the digitised permit register. It then tests its
own plan against 43,809 driver-GPS runs, the one operator that publishes data, building footprints, and a
full uncertainty analysis. **Target journal: *Transport Policy*.** Slogan: *planning what you cannot count.*

## 2. Headline results (all traceable to the ledger)

| Result | Value | Claim |
|---|---|---|
| Permits → corridors | 614 permits are 157 corridors; the plan keeps 156 (99.4 %) | CL-01, CL-02, CL-08 |
| Straight-line catchment bias | median 37.4 % overstatement per route; coverage 35.5 % → **24.2 %** | CL-26, CL-28 |
| Frequent network | only 10.4 % of residents near a ≤15-min service | CL-42 |
| Speed cap | binds on 169/186 routes, below real GPS pace | CL-31, CL-32 |
| **Fleet** | published 1,011; **989–1,058** as specified; **1,130–1,266 at observed pace** | CL-56 |
| Hierarchy | 97.8 % tier agreement under uncertainty; 179/186 routes stable | CL-57 |
| Funding | 30 % of the fleet reaches 92 % of the plan's coverage | CL-61 |
| Equity | Gini 0.903; 13,087 residents lose bus access through consolidation | CL-44, CL-45 |
| Load | ~8 boardings/trip on day one vs 19–37 today on the e-bus backbone | CL-50 |
| Validation | V1 partial pass · **V2 fails (circular)** · V3 not run · V4 · V5 · V6 executed | Table 7 |

## 3. Repositories

| Repo | Role | Local path |
|---|---|---|
| **bus-sathi-paper** (this) | manuscript, analysis pipeline, claim ledger, decisions | `E:\kash-paper` |
| kashmir-transit-rationalisation | the engine that produced the plan (v3.4.5-geo). **Read-only for the paper.** | `E:\kash` |
| bus-sathi-trace-intelligence | driver-GPS ground-truth layer. **Read-only.** Raw GPS is PII and never committed | `E:\bus-sathi-trace` |
| bus-sathi-dashboard | public Next.js dashboard for the plan | `E:\dash\bus-sathi-dashboard` |
| krishaniitjammu/Bus-Sathi | the driver app the GPS came from | — |
| **Princu-Babu/Bus-sathi** | the polished, citable consolidation of all of the above (code + data + results) — the repository the paper cites | — |

## 4. How to run

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Python 3.14
git lfs pull                                                             # heavy caches (walk graph, catchments, raster)
.venv/Scripts/python.exe analysis/run_all.py --list                      # 23 modules, all written
.venv/Scripts/python.exe analysis/run_all.py --quick                     # everything except the heavy graph builds (~4 min)
.venv/Scripts/python.exe -m pytest tests -q                              # 65 passed, 2 skipped
.venv/Scripts/python.exe paper/make_manuscript_pdf.py                    # working-draft PDF with citations + figures
.venv/Scripts/python.exe analysis/fig_generate_all.py                    # all figures
```

Heavy modules (only if the cache is missing): `a01_build_walk_graph` (needs `india-latest.osm.pbf`, ~9 min),
`a02_network_catchments` (~70 min), `a08a_catchment_grid` (~3 h, resumable from `data/cache/a08a_checkpoint.csv`).
V1's Microsoft building tiles are fetched per quadkey into `data/external/ms_buildings/` (index + tile list
committed; tiles themselves re-downloadable).

## 5. Where things are

| Path | What |
|---|---|
| `analysis/` | 23 modules + `common.py` (paths, parameters, seed) + `fleet_model.py` (verified supply model) + `run_all.py` |
| `data/raw/` | frozen inputs, hashed in `data/MANIFEST.md` |
| `data/derived/` | every module's JSON/CSV output — the only source prose may quote |
| `paper/sections/` | manuscript, one file per section (00 Abstract … 08 Conclusions) |
| `paper/CLAIM_LEDGER.md` | every number → module (CL-01…CL-61) |
| `paper/PENDING_DECISIONS.md/.pdf` | the decision queue; Part G is current |
| `paper/WORD_BUDGET_PLAN.md` | proposed cuts to reach 10,000 words |
| `paper/COAUTHOR_CITATION_MAP.md` | citation keys for the co-author sections |
| `paper/front_matter/` | highlights, CRediT, competing interests, data availability, acknowledgements, cover letter |
| `paper/figures/`, `paper/tables/` | generated; never edit by hand |
| `paper/gaps/` | the (older) brutally-honest gap analysis; superseded in part by Part G |
| `.agents/` | working notes of earlier AI work sessions (context, not deliverables) |
| `logs/` | module run logs; `logs/LATEST_RUN.json` is the last `run_all` |

## 6. Manuscript state

All nine parts are drafted (~13,600 body words against a 10,000 ceiling). §4–§6, §8 and the Abstract are
Prashant's and are written on final results. §1, §2, §3 and §7's co-author blocks are **co-author prose,
transcribed verbatim and not to be edited unilaterally**; conflicts are raised as callouts. The working
draft PDF is `paper/Kashmir_Manuscript_Working_Draft.pdf`.

## 7. What is open (all human)

- **Blockers:** D1 (§1.6 roadmap), D2 (is the August field table real?), D3 (Srinagar vs Division scope in
  co-author text), D4 (GPS consent/ethics), D5 (literature protocol), D13 (authors, CRediT), D23 (GPS date
  window conflict: Feb–Jun vs Jun–Jul).
- **Analytical sign-offs:** D20 (four corrections to the method as published), D21 (per-lakh benchmark),
  D22 (V2 reported as fail), D24 (load framing), D25/D8 (cost constants).
- **Co-author work:** word cuts (`WORD_BUDGET_PLAN.md`), citations (`COAUTHOR_CITATION_MAP.md`), Pucher year
  2005 not 2007.

## 8. Non-negotiable rules

1. **No fabrication.** V3 (expert panel) and the field/boarding survey were not conducted; say so.
2. **Never "validated against ridership."** GPS is supply-side. The claim is decision-robustness.
3. **Disclose the CHALO circularity before the V2 result.**
4. **Never sum per-route walksheds** — only the deduplicated union is a network total.
5. **Every number in prose cites a CL/F ID**, and a number whose module has not run does not exist.
6. **The engine repo is read-only** for this project.
7. **Barred legacy figures:** 342 permits, 207 routes, 39 % reduction, 95.7 % coverage, 1,009 buses,
   Srinagar-metropolitan scope.
8. **Uncomfortable results stay in:** the fleet above 1,011 at observed pace, the V2 fail, the 20 promoted
   high-priority routes, the 13,087 residents who lose access.
9. **Raw driver GPS is PII** and never enters any repository.
10. **Verify against the repo, not memory.**
