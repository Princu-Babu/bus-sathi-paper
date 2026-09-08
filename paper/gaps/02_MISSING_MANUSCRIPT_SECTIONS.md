# Gap 2 — Missing Manuscript Sections, Figures, Tables, References

**Severity: CRITICAL for submission.**

The paper is planned as 8 sections, 8 figures + F8b, 8 tables, 9,000–10,000 words. Here is what
actually exists in `paper/` on 2026-09-08.

## Sections

| # | Section | Owner(s) | State in repo | Note |
|---|---|---|---|---|
| Abstract | — | Prashant + Ankit + Sharvesh | **Draft** (318 w) | Figures provisional pending §5 modules |
| §1 | Introduction | co-authors | **ABSENT** in repo | Draft prose exists only inside the AK attachment PDF, not staged here |
| §2 | Literature review | co-authors | **ABSENT** | — |
| §3 | Study area & data | co-authors (Misti/Krishna) | **ABSENT** | Must be written in Kashmir-Division framing; AK draft still carries stale-Srinagar framing in places |
| §4 | Methodology | **Prashant (sole)** | **Complete** (2,634 w) | Strong |
| §5 | Results | Prashant + Misti | **HALF** — §5.1–5.4 done, §5.5–5.13 are stubs | Blocked by missing modules (Gap 1) |
| §6 | Validation | Prashant + Avny + Krishnan | **Draft** (1,170 w) | V4 done; V1/V2/V5/V6 pending modules; field/expert now framed as §6.4 future work |
| §7 | Discussion | co-authors | **ABSENT** | AK attachment has a "Policy Contribution" block to draw from |
| §8 | Conclusions | Prashant + Ankit + Sharvesh | **Complete** (450 w) | — |

> **Note on section numbering.** The AK attachment uses a 6-section scheme (Intro / Lit+Setting /
> Methodology / Results / Discussion / Conclusions). The repo/CLAIM_LEDGER uses an 8-section scheme.
> **These must be reconciled before submission** or cross-references will break. Pick one numbering and
> propagate it through every `[CL]` "Manuscript Location" and every in-text §-reference.

## Figures — 0 of ~9 generated

No `paper/figures/` directory is populated; `fig_generate_all.py` is a PLANNED stub. Planned set
(from the paper plan): Fig 1 study area, Fig 2 data pipeline, Fig 3 catchment method schematic,
Fig 4 framework flowchart, Fig 5 permit-reduction decomposition, Fig 6 tier classification, Fig 7
coverage map (Euclidean vs network), Fig 8 fleet/uncertainty, Fig 8b Sobol/tornado. **All absent.**
Figures 6/7/8/8b depend on missing modules a04/a11/a09.

## Tables — 12 of ~15 exist; 3 blocked

Present in `paper/tables/`: 2a–2f, 3a–3b, 4a–4b, 6a–6c (12 tables, all backed by executed modules).
**Missing:** Table 5 (route scores/tiers — needs `a04`), Table 7 (validation synthesis — needs
V1/V2/V5/V6 to have results), Table 8 (scenarios — needs `a15`). Table 7 currently exists only as a
*method* scaffold in CLAIM_LEDGER §6, not as a results table.

## References — ABSENT (this will get a desk-reject flag)

There is **no bibliography file anywhere in the repo** (only `CITATION.cff`, which cites the software,
not the literature). A *Transport Policy* submission needs a full reference list. The paper's prose
already name-drops methods (Jenks, Sobol, WorldPop, OSRM, TCQSM, entropy weighting) with **no citations
attached.** See [04_LITERATURE_POSITIONING.md](04_LITERATURE_POSITIONING.md) for the minimum canonical
set. **Action: create `paper/references.bib` and attach `\cite` keys throughout.**

## Front/back matter not yet present

- Highlights (3–5 bullets, journal requires) — draft exists in AK attachment, not staged.
- Author contributions (CRediT taxonomy) — absent.
- Declaration of competing interests — absent.
- Data availability statement — `DATA_AVAILABILITY.md` exists but must be tuned to the GPS-consent point.
- Acknowledgements — absent.

## Bottom line

Even if every analysis module ran tomorrow, **four sections would still need to be written from
scratch, ~9 figures generated, a reference list built, and the numbering reconciled.** The Prashant-owned
prose (§4, §6, §8, half of §5) is the most complete part of the manuscript.
