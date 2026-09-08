# Gap 5 — Submission-Readiness Checklist (Journal Mechanics)

**Severity: MEDIUM now, BLOCKING at submission.** These are the *Transport Policy* / Elsevier
house-keeping items that do not depend on analysis but will cause a desk return if absent. Grouped by
whether they block submission or merely polish it.

---

## A. Hard blockers (Elsevier will bounce the submission without these)

| Item | State | Action |
|---|---|---|
| **Reference list / bibliography** | ABSENT | Build `paper/references.bib` — see [04_LITERATURE_POSITIONING.md](04_LITERATURE_POSITIONING.md). Desk-reject risk. |
| **Highlights** (3–5 bullets, ≤85 chars each) | Draft in AK attachment, not staged | Stage as `paper/front_matter/highlights.md`. |
| **Author contributions (CRediT)** | ABSENT | One line per author per CRediT role (Conceptualization, Methodology, Software, Validation, Writing…). Prashant = Methodology/Software/Validation lead. |
| **Declaration of competing interests** | ABSENT | Standard statement; note any relationship to the SSCL/RTO if one exists. |
| **Data availability statement** | Partial (`DATA_AVAILABILITY.md`) | Must state what is public (WorldPop, OSM, engine code) and what is restricted (**driver GPS — consent/privacy**, see §B ethics). |
| **Abstract ≤ journal word limit** | Draft 318 w | Check *Transport Policy* abstract cap (typically ~200–250 w) and trim. |
| **Corresponding author + affiliations** | Unknown in repo | Confirm with the team; not derivable here. |

## B. Ethics / consent — the one that can sink a data-heavy paper

The headline empirical layer is **43,809 driver-GPS runs from ~157 real drivers** (`CL-18`). A journal
will ask:
- **Consent & privacy.** Were drivers informed their GPS traces would be used for research? Is the data
  anonymised (no driver IDs, no home locations)? The trace repo's Firestore admin key is (correctly)
  gitignored, but the *manuscript* needs an explicit sentence on consent basis and anonymisation.
- **IRB / ethics approval.** State whether ethics review was obtained or why it was not required
  (e.g. operational data, fully anonymised, aggregate-only). **Do not leave this blank.**
- This is a genuine risk because the GPS is the study's strongest evidence — if its provenance looks
  unconsented, the reviewer may ask you to drop it, which guts §6. Get the consent story straight with
  the team **before** submission. Do not fabricate a consent basis; state the actual one.

## C. Figure & formatting standards

| Item | State | Action |
|---|---|---|
| Figures at journal DPI (≥300, vector where possible) | 0 generated | Gap 2; `fig_generate_all.py` must output print-res. |
| Figure captions self-contained | N/A yet | Write when figures exist. |
| Tables editable (not images) | 12 exist as data | Ensure final tables are typeset, not screenshots. |
| Word count 9,000–10,000 | ~5,700 written (§4+§5.1-4+§6+§8) + 4 missing sections | On track *once* missing sections written; watch the ceiling. |
| Section numbering reconciled (6- vs 8-scheme) | UNRECONCILED | Gap 2 note — fix before cross-refs are finalised. |
| SI / supplementary (module outputs, CLAIM_LEDGER) | Strong candidate | Offer CLAIM_LEDGER + `data/derived/` as supplementary — a reproducibility selling point. |

## D. Cover letter

- ABSENT. Draft one that leads with the **policy contribution** ("planning what you cannot count" — a
  demand-free rationalisation method for data-scarce cities) and the **honesty of the supply-side
  validation**, names suggested reviewers, and states the work is original / not under review elsewhere.

## E. Reproducibility (this is a strength — lean into it)

Already strong and worth foregrounding in the cover letter and a "Code & data availability" section:
- `analysis/run_all.py` pipeline + fixed random seed (`20260823`).
- `tests/` — 52 passed / 2 skipped.
- `CLAIM_LEDGER.md` — every number traced to a module.

**But** the reproducibility claim is only honest for the **6 modules that exist**. Do not advertise
"fully reproducible pipeline" while 16 of 22 modules are stubs — either run them (Gap 1) or scope the
reproducibility statement to what actually executes. Overstating this in front of expert reviewers who
*will* try to run it is the worst possible own-goal.

---

## Bottom line

None of §A–§E requires new analysis except the figures. They are perhaps a week of careful
house-keeping — but several (references, ethics/consent, CRediT, cover letter) are **absolute
prerequisites** and are currently at zero. Start the ethics/consent conversation with the team now,
because it gates whether §6's GPS evidence can be used at all.
