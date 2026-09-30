# Gap Analysis — Master Index (Brutally Honest)

**Purpose.** This is the deliberately unflattering assessment of the paper's current state, written
against the standard of a well-regarded transport journal (*Transport Policy* tier) and industry
expert review. It exists so that nobody submits this manuscript believing it is closer to done than it
is. **Nothing here is padded and nothing is assumed** — every "done" claim was checked against the
repository on 2026-09-08 (`run_all.py --list`, `pytest tests/`, and a file-by-file read of
`paper/sections/`).

> **Headline judgement.** The *diagnostic spine* of the paper is real, reproducible, and strong. The
> *evaluation, uncertainty, and demand-side validation* that a journal will demand are **largely not yet
> executed** — 16 of 22 analysis modules are unwritten stubs, four of eight manuscript sections do not
> exist in this repo, and 0 of ~8 figures are generated. The paper is **not submittable today.** It is a
> well-built skeleton with four load-bearing limbs missing.

---

## What is genuinely DONE and defensible

These are safe to show an expert reviewer today.

| Area | State | Evidence |
|---|---|---|
| Permit→corridor deconstruction (F1) | Executed, tested | `q01_data_quality.py`, Table 2a, CL-01–CL-10 |
| WorldPop vs Census reconciliation (F2) | Executed | `q01`, Table 2d, CL-11–CL-14 |
| OSM completeness / road-density check (F6) | Executed | `q01`, Table 2c, CL-22–CL-23 |
| Network walk-catchment vs Euclidean (F7, F8, F9) | Executed, heavy run done | `a01`, `a02`, `a02b`; Tables 3a/3b; CL-24–CL-30 |
| Supply-side GPS validation (F3, F10, F11, F12) | Executed | `v04_gps_validation.py`; Tables 6a/6b/6c; CL-15–CL-19, CL-31–CL-35 |
| Composite index weights (equal/entropy/PCA) | Executed | `a03_index_weights.py`; Table 4a; CL (weights) |
| §4 Methodology prose | Complete draft, every number cited | `paper/sections/04_methodology.md` (2,634 w) |
| §5.1–§5.4 (diagnosis) prose | Complete, cited | `paper/sections/05_results.md` |
| §6 Validation prose (V4 + framing) | Complete draft | `paper/sections/06_validation.md` |
| §8 Conclusions prose | Complete draft | `paper/sections/08_conclusions.md` |
| Abstract | Draft (figures provisional) | `paper/sections/00_abstract.md` |
| Claim ledger + reproducibility harness | Complete | `CLAIM_LEDGER.md`, `tests/` 52 pass / 2 skip |

## What is MISSING or unfinished (the honest list)

Each has its own document in this folder:

1. **[01_MISSING_ANALYSIS_MODULES.md](01_MISSING_ANALYSIS_MODULES.md)** — 16 of 22 pipeline modules are
   unwritten stubs. This blocks §5.5–§5.13, all of V1/V2/V5/V6, and every figure. **Biggest single gap.**
2. **[02_MISSING_MANUSCRIPT_SECTIONS.md](02_MISSING_MANUSCRIPT_SECTIONS.md)** — §1 Introduction, §2
   Literature, §3 Study Area, §7 Discussion do not exist in this repo; §5 is half-written; no figures;
   Tables 5/7/8 not generated; **no References/bibliography file exists at all.**
3. **[03_METHODOLOGICAL_RISKS.md](03_METHODOLOGICAL_RISKS.md)** — the substantive things a hostile but
   fair reviewer will attack: the demand-index-to-demand gap, the GPS sample size (n=5 matched
   corridors for the headline runtime ratio), tourism multiplier provenance, τ choice, CHALO
   circularity, absence of any demand-side ground truth.
4. **[04_LITERATURE_POSITIONING.md](04_LITERATURE_POSITIONING.md)** — what the paper must cite and
   distinguish itself from; the canonical references it currently lacks; comparison to the closest
   published work.
5. **[05_SUBMISSION_READINESS_CHECKLIST.md](05_SUBMISSION_READINESS_CHECKLIST.md)** — journal-mechanics
   gaps: cover letter, author contributions, data-availability specifics, ethics/consent for the GPS
   data, figure standards, word budget.

## The one-paragraph honest summary for the team

> We have an unusually strong *diagnostic* paper: the permit-register deconstruction, the
> network-catchment correction, and the supply-side GPS validation are real, reproducible, and
> genuinely novel in combination. But as of today the manuscript cannot be submitted: more than half the
> analysis pipeline is unwritten, four of eight sections don't exist, there are no figures and no
> reference list, and the headline runtime finding rests on only five matched corridors. None of this is
> fatal — it is all *buildable* — but it is weeks of honest work, not days, and no number in the paper
> should be presented to a reviewer as final until its module has actually run.

---

*Verification basis for this document: `python analysis/run_all.py --list` (module existence),
`python -m pytest tests/` (53 passed, 2 skipped, 0 failed), and direct read of every file in
`paper/sections/` on 2026-09-08. If you re-run these and the counts differ, this document is stale —
regenerate it.*
