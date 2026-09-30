# Gap 2 — Missing Manuscript Sections, Figures, Tables, References

**Severity: CRITICAL for submission.**

The paper is planned as 8 sections, 8 figures + F8b, 8 tables, 9,000–10,000 words. Here is what
actually exists in `paper/` on 2026-09-13.

> **Updated 2026-09-13.** All four co-author sections (§1, §2, §3, §7) have since been drafted and
> staged, and the whole manuscript is assembled into `paper/Kashmir_Manuscript_Working_Draft.pdf`
> (35 pp, 11,920 body words). The "ABSENT" rows below are resolved. The section-numbering note has
> been corrected — see the box beneath the table.

## Sections

| # | Section | Owner(s) | State in repo | Note |
|---|---|---|---|---|
| Abstract | — | Prashant + Ankit + Sharvesh | **Draft** (249 body w) | Headline figures provisional pending a09 |
| §1 | Introduction | Misti, Avny | **Drafted** (2,343 body w) | Co-author prose transcribed verbatim + 9 editorial flags. Over budget: the ~900-word "Policy Failure" block belongs in §3.3 (FLAG PF-a) |
| §2 | Literature review | Sharvesh, Ankit | **Drafted** (1,413 body w) | §2.1 systematic-review protocol is a template with visible placeholders — **the search has not been run** (FLAG 2-A) |
| §3 | Study area & data | Krishna | **Drafted** (1,242 body w) | Kashmir-Division framing. **Ethics paragraph deliberately blank** (FLAG 3-D) |
| §4 | Methodology | **Prashant (sole)** | **Complete** (2,467 body w) | Eqs 1–14, Algorithm 1 |
| §5 | Results | Prashant + Misti | **PARTIAL** (1,151 body w) | a04/a05/a10–a13 results landed after this draft and are not yet written up |
| §6 | Validation | Prashant + Avny + Krishnan | **Draft** (956 body w) | V4 done; V1/V2/V5/V6 pending modules; field/expert framed as §6.4 future work |
| §7 | Discussion | Ankit, Avny, Misti | **Drafted** (1,678 body w) | §7.1–7.8 + the co-author "Policy Contribution" block verbatim; 5 flags |
| §8 | Conclusions | Prashant + Ankit + Sharvesh | **Complete** (421 body w) | — |

Word counts are measured at build time by `paper/make_manuscript_pdf.py` and count body prose only —
headings, tables, code blocks and editorial callouts are excluded.

> **Note on section numbering — CORRECTED 2026-09-13.** An earlier version of this document described
> a "6-section scheme (AK PDF) vs 8-section scheme (repo)" conflict. **That framing was wrong.** The
> attachment's *operative* structure — the table that assigns section owners and word budgets — is
> **eight sections**, and it matches the repository exactly. The only six-section artefact is a single
> sentence inside §1.6 ("…Section 6 concludes"), which contradicts the attachment's own structure and,
> under its scheme, leaves no slot for §6 Validation at all.
>
> There is therefore nothing to reconcile between the PDF and the repo. What needs fixing is one
> paragraph of §1.6. Replacement wording is drafted in FLAG 1.6-a and is *proposed, not applied* —
> it is co-author prose. Escalated as **Decision 1** in `paper/PENDING_DECISIONS.md`.


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
