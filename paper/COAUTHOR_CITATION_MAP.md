# Citation keys for co-author sections (§1, §2, §3, §7, §8)

Generated 2026-09-30 by scanning each section for author surnames that match a `references.bib` entry.
Prose in these sections was **not edited**. To attach a citation, append the key in pandoc form
`[@key]` after the mention (the working-draft builder renders it as author–year and adds it to the
reference list). A mention with no matching entry is listed under *unmatched* — add a verified entry or drop the mention.

| Section | Line | Mentioned | Suggested key |
|---|---|---|---|
| 01 | 17 | Forum 2026) | *unmatched* |
| 01 | 21 | Forum, 2026 | *unmatched* |
| 01 | 21 | MoHUA, 2014 | *unmatched* |
| 01 | 21 | Pucher et al., 2007 | *unmatched* |
| 01 | 23 | Forum, 2026) | *unmatched* |
| 01 | 49 | Badami & Haider, 2007) | `badami2007analysis` |
| 01 | 53 | Badami & Haider, 2007) | `badami2007analysis` |
| 01 | 74 | Ceder, 2007 | `ceder2007public` |
| 01 | 75 | Ibarra-Rojas et al., 2015) | `ibarrarojas2015planning` |
| 01 | 273 | Act, 1988 | *unmatched* |
| 02 | 56 | Guihaire and Hao (2008) | `guihaire2008transit` |
| 02 | 57 | Ibarra-Rojas et al. (2015) | `ibarrarojas2015planning` |
| 02 | 58 | Ceder (2007 | `ceder2007public` |
| 02 | 60 | Vuchic (2005) | `vuchic2005urban` |
| 02 | 62 | TRB, 2013) | *unmatched* |
| 02 | 100 | Untermann (1984) | `untermann1984accommodating` |
| 02 | 101 | El-Geneidy et al. (2014) | `elgeneidy2014new` |
| 02 | 103 | Palomares (2008) | *unmatched* |
| 02 | 121 | Tatem, 2017) | `tatem2017worldpop` |
| 02 | 124 | Millard-Ball (2017) | *unmatched* |
| 02 | 136 | Jenks (1967) | `jenks1967data` |
| 02 | 138 | Cohen's (1960) | *unmatched* |
| 02 | 140 | Shannon (1948) | `shannon1948mathematical` |
| 02 | 140 | Jolliffe, 2002) | `jolliffe2002principal` |
| 02 | 141 | Delbosc and Currie (2011) | `delbosc2011using` |
| 02 | 142 | Moran's (1950) | *unmatched* |
| 02 | 147 | Badami and Haider (2007) | `badami2007analysis` |
| 03 | 85 | WorldPop 2026 | *unmatched* |
| 03 | 113 | WorldPop 2026 | *unmatched* |
| 03 | 121 | Millard-Ball (2017) | *unmatched* |
| 07 | 147 | WorldPop 2026 | *unmatched* |

## Resolutions for the *unmatched* rows (checked by hand)

| Mention | Resolution |
|---|---|
| Pucher et al., 2007 (§1 l.21) | **Year is wrong.** The paper is Pucher, Korattyswaropam, Mittal & Ittyerah (**2005**), *Transport Policy* 12(3):185–198 → `pucher2005urban`. Fix the year in the prose. |
| TRB, 2013 (§2 l.62) | `trb2013transit` (TCQSM 3rd ed.) |
| García-Palomares (2008) (§2 l.103) | `gutierrez2008distance` (Gutiérrez & García-Palomares 2008) |
| Millard-Ball (2017) (§2 l.124, §3 l.121) | `barringtonleigh2017world` (Barrington-Leigh & Millard-Ball 2017) |
| Cohen's (1960) (§2 l.138) | `cohen1960coefficient` |
| Moran's (1950) (§2 l.142) | `moran1950notes` |
| MoHUA, 2014 (§1 l.21) | **No entry.** `moud2009service` is the 2009 Service Level Benchmark. Identify which 2014 MoHUA/MoUD document is meant, verify it, then add it; otherwise cite the 2009 benchmark. |
| Forum 2026 (§1 l.17, 21, 23) | **No entry.** Grey source; needs a full reference (publisher, title, URL, access date) before it can be cited. |
| Motor Vehicles Act, 1988 (§1 l.273) | Statute — cite in text as the Act; add a `@misc` entry only if the journal style requires it. |
| WorldPop 2026 (§3, §7) | Dataset → `tatem2017worldpop` (and `stevens2015disaggregating` for method), as §4 now does. |
