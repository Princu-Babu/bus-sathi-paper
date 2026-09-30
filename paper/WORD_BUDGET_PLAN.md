# Word-budget plan (D26)

**Limit.** *Transport Policy* Guide for Authors (checked 2026-10-01): *"Articles should normally be no
longer than 8000 words."* Abstract ≤ 250 words (ours: 228). The guide does not say whether references and
tables count; we plan the **main text at ≤ 8,000**, which is safe either way for references and leaves tables
out of the count as is conventional. (The 9,000–10,000 used before came from the co-author brief and was
never checked.)

**Now:** 13,393 body words (Abstract excluded), measured by `make_manuscript_pdf.word_count` — prose only,
no headings, tables or callouts. **Cut needed: ~5,400 words (40 %).**

## Principle: move, don't lose

A *Supplementary Material* file (Elsevier accepts it) carries whole subsections that move out. Every number
stays in the ledger and the repository. The main text keeps one sentence per moved subsection with a pointer
("Supplementary §S3"). This is also where the authors' own editing of AI-assisted text happens (D28).

## Allocation

| Section | Owner | Now | Target | Cut | Main levers |
|---|---|---:|---:|---:|---|
| §1 Introduction | Misti, Avny | 2,343 | 900 | −1,443 | Policy-Failure block (897) → §3.3, condensed to ~250; merge §1.1+§1.2; drop §1.4's repeat of §1.3; figure/table call lists out (197) |
| §2 Literature | Sharvesh, Ankit | 1,413 | 900 | −513 | if D5 = B, §2.1 protocol goes (~250); tighten §2.2–§2.7 |
| §3 Study area | Krishna | 1,242 | 700 | −542 | §3.5 diagnostics → one paragraph (detail is in §4.2 / supplement); call list out |
| §4 Methodology | Prashant | 2,422 | 1,700 | −722 | keep all equations; QA-gate list, faithfulness detail, notation paragraph → supplement |
| §5 Results | Prashant, Misti | 2,412 | 1,800 | −612 | §5.10 transfers, §5.11 operations (time of day, deadhead, load), §5.12 cost → Supplementary S5; one summary sentence each stays |
| §6 Validation | Prashant, Avny, Krishnan | 1,041 | 650 | −391 | V4 detail → supplement; Table 7 carries the six results |
| §7 Discussion | Ankit, Avny, Misti | 2,045 | 1,000 | −1,045 | Policy-Contribution block folded into §7.2; §7.8 limitations → 5 lines; §7.3/§7.4 merged |
| §8 Conclusions | Ankit, Prashant, Sharvesh | 475 | 350 | −125 | — |
| **Total** | | **13,393** | **8,000** | **−5,393** | |

## Suggested order of work

1. **Structural moves first** (no rewriting): Policy-Failure block → §3.3; §5.10–§5.12 and V4 detail →
   supplement; call lists out. That alone removes ~2,500 words.
2. **Decide D5.** Option B removes §2.1 outright.
3. **Then line-editing**, each owner on their own section — this is also the D28 author review of
   AI-assisted text for §4–§6 and §8.
4. Re-measure with `python paper/make_manuscript_pdf.py` (the contents page shows every section against
   its target).

## What must not be cut

- The CHALO circularity disclosure (§6.1) and the V2 fail.
- The statements that V3 and a boarding survey were **not** conducted.
- The 13,087 residents who lose access (§5.9) and the 20 promoted high-priority routes (§5.8).
- The fleet range at observed pace (§5.7).
