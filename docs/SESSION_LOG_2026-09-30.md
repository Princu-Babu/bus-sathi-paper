# Session log — 2026-09-30

A record of one long working session (Prashant + Claude) that took the paper from "diagnostic half done"
to "every analysis run, every section drafted". Kept so teammates can see *why* things changed, not just
*what* changed. Commits: `15d78d7` … `a4ba64a` and later.

## Starting point (morning)

13 of 22 modules had run; 79 files of work were uncommitted; §5 was half-written; 0 figures; citations
not attached; no front matter. The critical path was `a08 → a09` (sensitivity → Monte Carlo/Sobol').

## What was built

| Area | Work | Key result |
|---|---|---|
| Supply model | `analysis/fleet_model.py` — vectorised reimplementation of the engine's cycle-time and fleet rules | reproduces the published plan on **all 186 routes** (1,011 buses; cap binds on 169) |
| a08a | walk catchments recomputed at W = 300–800 m and stop spacing 150–400 m (3 h, resumable) | exact reproduction of a02 at 400 m; coverage 20.3 % → 34.5 % across the radius range |
| a08 | one-at-a-time sensitivity, 11 parameters | cap on: run-time parameters move the fleet ≤17 buses; cap off: up to 956 |
| a09 | Monte Carlo (5,000) + Sobol' (15,360) with a GPS pace prior | fleet 989–1,058 as specified, **1,130–1,266 at observed pace**; tiers 97.8 % stable |
| a06 | depot deadhead (no depot register → bounded) | 0 % / 1.7 % / 5.5 % depending on assumption |
| a07 | load factor vs observed CHALO boardings | day-one ~8 boardings/trip vs 19–37 today |
| a14 | cost & CO₂ envelope (constants pending D8) | engine's e-bus emission factor ~29× too low |
| a15 | 5 scenarios + frontier + funding sequence | 30 % of fleet reaches 92 % of coverage |
| v01 | building-footprint cross-check (OSM, then Microsoft ML footprints) | see ledger CL-53 |
| v02 | CHALO benchmark (circular) | **fails** ±15 % at every service-day assumption |
| Figures | `analysis/fig_generate_all.py` | Figures 1, 3–9, 9b, S1, S2 |
| Manuscript | §4 corrected + trimmed; §5 written; §6 V1/V2/V5/V6; §7.5, §7.7; Abstract; §8 | ledger CL-37 … CL-61 |
| Citations | `[@key]` in §4–§6, renderer + reference list; 2 refs added (Crossref-verified) | 0 unresolved keys |
| Front matter | 6 drafts with placeholders for human decisions | `paper/front_matter/` |

## Things found in the engine that the paper had described wrongly (now corrected in §4; D20)

1. Capture scale κ is **0.33** (not 0.18).
2. The Eq. 8 demand proxy **does** set headways on the 67 non-backbone rural routes.
3. The merge rule is 80 m line-buffer overlap ≥ θ **and** start points within 2.5 km, merging only into a
   cluster's leading trunk (so surviving feeders can still overlap: 207 pairs pass the test).
4. Layover is multiplicative (×1.10); the backbone fleet is max(formula, CHALO deployment).
5. The "43 buses per lakh, inside MoHUA 40–60" figure uses the overstated Euclidean denominator; on the
   network walkshed it is **63.5** (above the band).

## Housekeeping decisions taken

- D19: a03's Jenks convention aligned with a04 (only unquoted band statistics moved).
- D9: V1 run first on the local OSM extract, then (with Prashant's go-ahead) on Microsoft's ML footprints.
- Synthetic smoke-test outputs were deleted before any commit; only real runs are committed.

## Known pitfalls for the next person

- Shell heredocs corrupt LaTeX backslashes (`\rho` → carriage return). Write scripts with a file tool.
- `a08a` takes ~3 h; it checkpoints every route — just re-run it after an interruption.
- `run_all.py --quick` runs a08/a09 only if the a08a grid is complete; otherwise a08 exits with a clear message.

## What is left

Human decisions (D1–D5, D13, D20–D25), co-author cuts and citations. See `MASTER_CONTEXT.md` §7 and
`paper/PENDING_DECISIONS.md` Part G.
