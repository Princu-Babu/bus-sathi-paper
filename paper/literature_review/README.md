# Literature review evidence (§2, Supplementary Material S1)

Everything §2 states about the literature is produced here. Ledger rows: `CL-62` to `CL-66`.

## Protocol as executed

| Item | Value |
|---|---|
| Sources | OpenAlex (title + abstract search) and Scopus (TITLE-ABS-KEY). Web of Science was not available. |
| Search dates | OpenAlex 30 September 2026; Scopus 30 September – 1 October 2026 |
| Window and limits | 2000–2026; English; articles, conference papers, reviews |
| Queries | 13 concept blocks in both databases + 6 novelty queries in Scopus (`search_log.csv`, `scopus_log.csv`, `02_scopus_queries.md`) |
| Records | OpenAlex 3,584 unique; Scopus 3,965 unique; overlap 2,061; **5,488 unique** |
| Keyword pre-filter | identical rules in `prefilter.py` and `scopus_merge.py`; 2,970 removed |
| Title/abstract screening | 2,518 screened: 873 include, 469 maybe, 1,176 exclude (`screening_decisions.csv`) |
| Coded corpus | 60 studies: 57 from the search (purposive, theme-stratified) + 3 seminal by citation chaining (`corpus_selected.csv`) |
| Coding | rubric in `coding/RUBRIC.md`; 46 from full text, 14 from abstracts (`table1_final.csv`); audit trail of every changed code in `coding/coded_fulltext_23_changes.md` |
| Cross-tabulation | `crosstab_intensity_plan.csv`, n = 56 on both axes; drawn as Figure 2 by `finalise_table1.py` |
| Novelty check | `03_novelty_check.md` (750 records scored) and `04_fulltext_verification.md` (five closest papers read in full) |

Counts at each stage: `prisma_counts.md`.

## What is deliberately not here

- **Raw Scopus exports and abstracts.** Licensed content. The files here keep identifiers, DOIs, titles,
  years and our decisions, which is enough to re-run and audit the review. Anyone with Scopus access can
  regenerate the export from the logged query strings.
- **Publisher PDFs and extracted full texts.** Copyrighted.

## How AI assistance was used (for the D28 declaration)

First-pass title/abstract screening, the novelty scoring and the coding of Table 1 were carried out with a
large language model (Claude, Anthropic) working to the written criteria in `01_review_protocol.md` and
`coding/RUBRIC.md`. Integrity checks were run on every batch (identifier ranges, uniqueness, reason-to-title
spot checks), every cited reference was resolved against Crossref, and the closest prior work was read in
full text. The authors are responsible for the final selection, the codes and the text of §2.

## Known limits

- Four studies (C56, C57, C58, C60) could not be obtained in full text and are not on both axes of Figure 2.
- The sample of 60 is purposive, not random: it contains the most-cited method and application studies per
  theme, recent work, and every closest-prior-work paper. The cross-tabulation describes this sample.
- `01_review_protocol.md` is the design document written before the search; where it differs from the table
  above (it anticipated a Web of Science run), the table above is what was done.
- Grey literature (Indian practitioner route-rationalisation reports) was not searched systematically.

## Reproduce

```
python search_openalex.py     # OpenAlex queries -> raw_results.csv (rate-limited; cached per query)
python prefilter.py           # keyword pre-filter
python scopus_merge.py        # needs your own Scopus export of the logged queries
python finalise_table1.py     # Table 1, cross-tab, Figure 2
```
