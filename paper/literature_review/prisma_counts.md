# PRISMA-style counts — search run 2026-09-30 (OpenAlex) and 2026-09-30/10-01 (Scopus)

Limits in both: 2000–2026, English, journal articles / conference papers / reviews, title+abstract(+keywords in Scopus).

## Identification
| Source | Queries | Sum of hits | Unique records | Log |
|---|---:|---:|---:|---|
| OpenAlex (title+abstract) | 13 | 3,908 | 3,584 | `search_log.csv`, `raw_results.csv` |
| Scopus (TITLE-ABS-KEY) | 13 core + 6 novelty | 4,062 + 361 = 4,423 | 3,965 (combined query) | `scopus_log.csv`, `scopus_export_2026-10-01_abstracts.csv` |
| Overlap (DOI or normalised title) | | | 2,061 | `scopus_merge.py` |
| **Unique across both** | | | **5,488** (3,584 + 1,904 Scopus-only) | |

## Screening
| Stage | OpenAlex | Scopus-only | Total |
|---|---:|---:|---:|
| Records | 3,584 | 1,904 | 5,488 |
| Removed by keyword pre-filter (identical rules) | 1,939 | 1,031 | 2,970 |
| — no bus/public-transport term | 935 | 432 | 1,367 |
| — no planning/network term | 417 | 288 | 705 |
| — off-topic keyword | 587 | 311 | 898 |
| Title/abstract screened | 1,645 | 873 | 2,518 |
| — excluded | 725 | 451 | 1,176 |
| — included | 599 | 274 | 873 |
| — maybe | 321 | 148 | 469 |
| Selected for coding (Table 1) | | | _pending_ (target 45–60) |
| + snowballed seminal / pre-2000 | | | _pending_ |

Files: `screened_all.csv` (OpenAlex), `scopus_screened.csv` (Scopus-only), `prefilter_log.csv`, `scopus_prefilter_log.csv`.

## Novelty check (separate, exhaustive)
Six dedicated Scopus queries (N1–N6): 359 unique records (`scopus_novelty_hits.csv`), plus 14 screener-flagged records (`novelty_extra_from_screening.csv`), plus relevant OpenAlex includes/maybes — all reviewed individually → `03_novelty_check.md`.

## Honest-reporting notes (must appear in §2.1 wording)
- First-pass title/abstract screening was done by LLM agents (Claude Sonnet) against written criteria; integrity-checked (SID ranges, uniqueness, reason–title spot checks); final selection and coding by the authors.
- Keyword pre-filter rules are published in `prefilter.py` / `scopus_merge.py`; the off-topic list may drop a small number of relevant papers.
- Web of Science: _pending — institutional access being checked_.
