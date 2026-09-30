# Paper Completion Plan

**What this is.** The implementation plan for getting the Kashmir bus route-rationalisation manuscript
from where it actually is today to a *Transport Policy* submission. It is a work plan, not a status
report: every item is a thing somebody has to do, with what it blocks, what blocks it, and how you know
it is finished.

**Companion documents.** `MASTER_CONTEXT.md` is the briefing (what the project *is*).
`paper/PENDING_DECISIONS.md` is the decision queue (what only a human can answer). `paper/gaps/` is the
unflattering assessment (what is wrong). This file is the sequencing layer that sits on top of all
three — it does not repeat their content, it orders it.

---

> **Correction, and why this file exists.**
>
> In an earlier session I told the project lead that this document had been written and pushed to git.
> **It had not been.** No file was created and no commit was made. The claim was false when I made it.
>
> This is the real file, written 2026-09-13 against a live read of the repository. I am recording the
> error here rather than quietly fixing it because the whole methodology of this project rests on the
> claim that every number is traceable to something that actually ran — and a plan that says work is
> done when it is not is the same failure mode as a paper that reports a module that never executed.
>
> Everything below was checked against `run_all.py --list`, `ls paper/tables/`, `ls data/derived/`,
> `git log`, and `pytest tests/` on the date above. If you re-run those and the counts differ, this
> file is stale — regenerate it rather than trusting it.

---

## 1. Where the paper actually stands (refreshed 2026-09-30)

Measured, not estimated:

| Dimension | Done | Remaining | Basis |
|---|---|---|---|
| Analysis modules | **23 of 23 written and executed** (incl. a08a grid precompute) | — | `run_all.py --list` |
| Manuscript sections | **9 of 9 drafted**; §4–§6, §8, Abstract rewritten on final results | co-author review of §1–§3, §7 | `paper/sections/` |
| Body words | **~13,600** | ~3,600 over; plan in `paper/WORD_BUDGET_PLAN.md` | measured at PDF build |
| Tables | **43 generated**, incl. Table 7a–c (sensitivity, MC, Sobol'), Table 8 + 8b (scenarios, funding) | typeset from CSV at submission | `paper/tables/` |
| Figures | **10 drawn** (1, 3–9, 9b, S1, S2) | Figure 2 waits on D5 | `paper/figures/` |
| References | **62 entries**, 29 cited in §4–§6/§8, **0 unresolved** | co-author sections: `paper/COAUTHOR_CITATION_MAP.md` | `paper/citations.py` |
| Front/back matter | **6 of 6 drafted** | placeholders for D4, D13, D16 | `paper/front_matter/` |
| Claim ledger | **CL-01…CL-61** | — | `paper/CLAIM_LEDGER.md` |
| Tests | **65 passed, 2 skipped, 0 failed** (incl. `run_all.py --quick` end to end) | — | `pytest tests/` |
| Validation (Table 7) | V1 partial pass · V2 **fail** (circular) · V3 not run · V4 · V5 · V6 executed | V3 is forward work | ledger §6 |

**The honest one-line summary.** Every analysis the design promised has now run. What remains is human:
the blocking decisions (D1–D5, D13, D23), co-author review and cutting of §1/§3/§7, and the choice of
how to present two uncomfortable results — the fleet at observed pace (1,130–1,266, above the published
1,011) and the failed operator benchmark.

## 2. The critical path

Only one chain genuinely gates submission. Everything else can run beside it.

```
a08 (OAT sensitivity)
   └─► a09 (Monte Carlo + Sobol')
          ├─► fleet INTERVAL ────────► Abstract, §5, §8 headline numbers
          ├─► V5 (Sobol' ranking) ───► §6 Table 7, §7.5 data-maturity ladder
          ├─► V6 (decision robustness) ► §6 Table 7
          └─► Fig 8 + Fig 8b
```

`a09` is the single most load-bearing unwritten module in the project. Until it runs:
- the fleet figure must stay a **point estimate (1,011)** and cannot be reported as an interval;
- §7.5's data-maturity ladder is **asserted from intuition**, which FLAG 7-B and FLAG 7-D forbid;
- Table 7 cannot be assembled, because four of its six rows have no result;
- two of nine figures cannot be drawn.

Everything else in this plan is parallelisable. Plan the schedule around `a08 → a09` and fill the gaps
with the rest.

---

## 3. Work packages

Ordered by dependency, not importance. **B** = blocks submission. **Q** = quality only.

### WP1 — Finish the analysis pipeline (9 modules remaining) · **B**

| Module | Produces | Blocks | Notes |
|---|---|---|---|
| `a06_deadhead` | depot deadhead 5–12% of bus-hours | §5 operating-cost realism | independent |
| `a07_load_factor` | offered capacity vs proxy peak demand | §5.7, R1 rebuttal | independent |
| `a14_cost_emissions` | ₹/accessibility-gain, emissions range | §5.9, §7 policy costing | uses cited MoHUA/published defaults — decision D8 |
| `a15_scenarios` | five policy scenarios + trade-off frontier | **Table 8**, §7.7 sequencing, FLAG 7-D | independent |
| `a16_peer_regression` | buses/1k vs population & density | §5 benchmark context | **DONE** — 36 cities, ASRTU 2024 handbook (see §5) |
| `a08_sensitivity_oat` | 10-parameter OAT sweeps | `a09` | **critical path** |
| `a09_monte_carlo_sobol` | 5,000 draws, Sobol' indices | fleet interval, V5, V6, Fig 8/8b | **critical path** |
| `v01_spatial_crossval` | ρ vs OSM building footprints | V1 row of Table 7 | needs building layer (WP2) |
| `v02_benchmark` | CHALO ±15% consistency | V2 row of Table 7 | **must disclose circularity before the result** |
| `figures_tables` | Figures 1–8b, Tables 7–8 | all figure references | run last |

**Standing contract for every module:** a quantity that cannot be computed from available data is
returned as `NOT_COMPUTABLE` with its reason and, where meaningful, its bounds. It is never estimated,
interpolated, or replaced by a plausible number. Three modules have already exercised this
(`a10` unique-network-km, `a12` before-Gini, one `a12` loser row) and that is the behaviour to preserve.

### WP2 — Stage the OSM building-footprint layer · **B for V1 only**

Download buildings for the 10 districts (open data, no permission needed — decision taken per the
lead's "do whatever you can"). Stage under `data/raw/`, gitignore the heavy file, record it in
`data/MANIFEST.md`. Unblocks `v01`. If it proves impractical, V1 stays "planned" in §6 and Table 7
carries a NOT_RUN row — which is acceptable, but only if stated.

### WP3 — Write the landed results into §5 and the ledger · **B**

Six modules have produced results that **no section currently reports**: `a04`, `a05`, `a10`, `a11`,
`a12`, `a13`. §5 is 1,151 body words against a 2,400 target, so this is the one place where the
manuscript gets *longer* on purpose. Each new number needs a CL ID in `CLAIM_LEDGER.md` at the moment
it is written into prose — not afterwards.

Two results are uncomfortable and must be reported anyway:
- the objective tier partition agrees with the deployed plan's own HP/MP/LP bands only **68.3%**
  (κ = 0.503), with twenty HP routes landing in objective Tier 3 (decision D18);
- `a10` cannot compute unique network km at all and reports bounds instead.

### WP4 — Cut the manuscript to budget · **B**

11,920 body words against a 9,000–10,000 ceiling, *before* §5 grows by ~1,200. The realistic target is
a **~4,000-word reduction**. The single largest candidate is the ~900-word "Policy Failure" block
currently sitting in §1, which belongs in §3.3 (FLAG PF-a) — but moving it does not shrink the total.
Genuine cuts have to come from somewhere, and because most of the over-length prose is **co-author
prose that must not be altered unilaterally**, this work package is *blocked on co-author review*, not
on effort. Flag it to them early; it is the slowest human dependency in the plan.

### WP5 — Attach citations · **B**

59 verified entries exist; **zero `\cite` keys are attached in the prose.** Every method the paper
name-drops (Jenks, Fisher, Sobol', Saltelli, WorldPop, OSRM, TCQSM, entropy weighting, Moran's I, Gini)
needs its key inline. Two corrections from the verification pass must be honoured:
- **Pucher et al. is 2005, not 2007** (*Transport Policy* 12(3):185–198 — conveniently the target journal);
- the "Li et al. 2022 / ratio ≈ 1.3" comparison **does not exist** and has been struck from
  `gaps/04`; it must not reappear.

Cite **Fisher (1958)** for the algorithm actually implemented and **Jenks (1967)** for the cartographic
convention. Drop `\cite` calls for Sobol'/Saltelli/Delbosc if `a09`/`a12` have not produced results by
submission — keep the entries, drop the calls.

### WP6 — Figures · **B**

Nine at ≥300 DPI, vector where possible, self-contained captions. Six are unblocked today (Fig 1
conceptual framework, Fig 3 study area, Fig 4 method flowchart, Fig 5 permit funnel, Fig 6 Euclidean vs
network, Fig 7 tiers, Fig 8 coverage); Fig 8 fleet-uncertainty and Fig 8b Sobol'/tornado wait on `a09`.

### WP7 — Front and back matter · **B**

Highlights (3–5 bullets ≤85 chars), CRediT author contributions, competing-interests declaration, data
availability statement, acknowledgements, cover letter. All are mechanical **except** two, which are
human decisions and are already queued as D13 and D4:
- **authorship / affiliations / corresponding author** — deferred by the lead, still outstanding;
- **the GPS ethics and consent statement** — the one item that can cost the paper its strongest
  evidence. "Not consulted" is an acceptable answer to write down. Silence is not.

### WP8 — Integrity and reviewer pass · **B**

Run the manuscript through the academic-research-skills integrity gate and a hostile-reviewer pass
against `gaps/03_METHODOLOGICAL_RISKS.md` (R1 demand-index gap, R2 n=5 corridors, R3 tourist
multiplier, R4 τ, R5 CHALO circularity, R6 self-test tautology, R7 WorldPop<Census, R8 Srinagar-centric
GPS). Every claim in the final PDF must resolve to a CL or F ID.

---

## 4. Sequence

Four waves. Within a wave, items are independent.

| Wave | Contents | Gate to leave the wave |
|---|---|---|
| **1 — Unblock** | `a08`→`a09`; `a06`, `a07`, `a14`, `a15`, `a16`; stage building layer (WP2) | every module either produced a result or returned an explicit `NOT_COMPUTABLE` |
| **2 — Write up** | WP3 (§5 + ledger); `v01`, `v02`; Table 7; Table 8 | no number in any section lacks a CL/F ID |
| **3 — Assemble** | WP5 citations; WP6 figures; WP4 cut to budget | ≤10,000 body words; 9 figures at ≥300 DPI; every `\cite` resolves |
| **4 — Submit** | WP7 front matter; WP8 integrity + reviewer pass; final PDF | §5 checklist below is all green |

Waves 1 and 2 can overlap. Waves 3 and 4 cannot start until the numbers stop moving.

---

## 5. Known constraints that will not resolve themselves

**a16 peer regression — RESOLVED, and better than expected.** The city-vs-statewide scope problem that
made this module look intractable has been solved at source. `a16_peer_regression.py` is written and
executed against the **ASRTU *SRTU Fleet Handbook 2024*, "City" operations column, as on 31 Oct 2023** —
a purpose-built city-scope fleet field, not the statewide totals that a website scrape returns.
Thirty-six peer cities enter the fit (37 rows, 3 flagged as multi-city operators), all fleet figures
from that one dated source, all population/area from Census 2011 Table A-04(I) with a recorded SHA-256.

Result (M1, population-only, the honest basis because Kashmir's 413.8/km² density sits *below every
fitted city* so the density term would be extrapolation): R² = 0.096, n = 36. Kashmir's 1,011 buses are
**0.154 per 1,000 on the 6.58M total population — 61st percentile, inside the M1 prediction interval**;
0.436 per 1,000 on the engine's 2.318M served population (86th percentile, still inside). The
three-multi-city-excluded model (M2b) lifts R² to 0.217 with a significant population coefficient
(p = 0.008). The module ships one caveat that must survive into the manuscript: **peers are public-STU
fleets, whereas Kashmir's 1,011 is a planned all-operator fleet** (it absorbs private minibus permits
plus the SSCL/CHALO e-buses), so the regression benchmarks public provision, not a like-for-like
target. Reported honestly, this is a *supporting* result — the plan is not an outlier against national
practice — not a validation of the fleet number.

**No further data hunt is needed for a16.** Two independent metro/small-city verification passes
confirmed that scraping operator sites yields an uncomparable, multi-date, mixed-scope dataset; the
ASRTU handbook is the right single source and is already in use.

**Headline numbers may move.** The lead has already accepted this ("just do the best possible option
which is correct and true"). Specifically: the fleet figure may become an interval once `a09` runs, and
the Abstract, §5 and §8 must then be updated together. Numbers that are **locked** and must not drift:
614 permits, 157 corridors, 186 active routes, 6,584,762 denominator, 24.2% coverage, 37.4% median
overstatement, 43,809 GPS runs, v3.4.5-geo engine baseline.

**Legacy framings remain barred** throughout: 342 permits, 207 routes, "39% route reduction", 95.7%
coverage, 1,009 fleet, and any Srinagar-Metropolitan scoping of the study area.

---

## 6. Definition of done (the submission gate)

Submission is permitted when **all** of these are true, and not before:

1. Every module in `run_all.py --list` shows `YES`, or its absence is stated in the manuscript.
2. No sentence in any section contains a number without a CL or F ID.
3. Body word count ≤ 10,000.
4. Nine figures exist at ≥300 DPI with self-contained captions.
5. Every `\cite` key resolves to an entry in `references.bib`, and no entry is cited for a result that
   did not run.
6. Table 7 has a row for each of V1–V6, each either a result or an explicit NOT_RUN.
7. The GPS consent basis, anonymisation mechanism and ethics-review status are written down (D4).
8. Authorship, affiliations, corresponding author and CRediT roles are filled in (D13).
9. `pytest tests/` passes.
10. The CHALO circularity is disclosed **before** the V2 result, not after it.
11. No barred legacy metric appears anywhere in the manuscript.
12. V3 (expert elicitation) and the field boarding survey are described as future work and **nowhere
    reported as collected**.

Items 7 and 8 are the only two that no amount of work here can satisfy — they need the team.

---

*Written 2026-09-13 against commit `1b9345f` plus uncommitted work. Verification basis:
`analysis/run_all.py --list`, `pytest tests/` (53 passed / 2 skipped), and direct inspection of
`paper/sections/`, `paper/tables/`, `data/derived/`, `paper/references.bib`.*
