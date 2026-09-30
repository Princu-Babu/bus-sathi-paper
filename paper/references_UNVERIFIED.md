# references_UNVERIFIED.md

Companion to `paper/references.bib`. Records (A) entries that shipped but rest on
**indirect** verification, (B) works named in the source material or brief that were
**excluded** because they could not be confirmed, (C) thematic searches that returned
nothing citable, (D) commonly-miscited works whose real details differ, and (E) edition
and year judgement calls a copy-editor may want to revisit.

**Verification method.** Every shipped entry was checked against an authoritative
bibliographic register — the Crossref REST API (`api.crossref.org/works`, by DOI where
known, otherwise by bibliographic query), OpenLibrary for books/ISBNs, the National
Academies record for TRB reports, or the issuing body's own website via the Internet
Archive for grey literature. **Generic web search was deliberately not used as a
verification source**: in this environment it returned plausible-looking but
model-generated bibliographic text, which is exactly the failure mode that produces
hallucinated citations.

**Result: 59 entries shipped, 53 of them carrying a DOI.** The six without a DOI are
print books and grey literature that genuinely have none (Vuchic 2005, Untermann 1984,
Walker 2011, Jenks 1967, MoUD 2009, OpenStreetMap).

---

## A. Shipped, but verified indirectly — read before submission

Two entries are in `references.bib` because their details were corroborated from
independent authoritative records rather than from the document itself. Both are
standard, widely-cited works; neither is invented. Flagged so nobody is surprised
under review.

### A1. `jenks1967data` — Jenks, G. F. (1967), *International Yearbook of Cartography* 7, 186–190

- **What is solid:** author, year, title, volume and page range.
- **How:** the *International Yearbook of Cartography* is not digitised and has no DOI,
  so there is no publisher record to read. The volume/page details were instead
  corroborated from **two independent publisher-deposited reference lists** retrieved
  through Crossref (the citing works' own deposited metadata), which agree on
  `vol. 7, pp. 186–190`. Two unrelated publishers depositing the same pagination is
  strong evidence, but it is not the title page.
- **Risk:** very low. This is one of the most-cited references in thematic cartography.
- **Note:** the entry carries a `note` field stating the corroboration route.
- **See also D3** — Jenks is the conventional attribution, but Fisher (1958) is the
  actual algorithm; both are shipped.

### A2. `moud2009service` — Ministry of Urban Development, *Service Level Benchmarking in Urban Transport for Indian Cities*

- **What is solid:** the exact document title and the issuing ministry. Confirmed from
  an Internet Archive capture of the Ministry's own `Urban-Transport` page, which links
  the document (as `VolumeIV_UserManual02.pdf`) under that title.
- **What is NOT confirmed:** **the year.** The PDF's own bytes were never archived, so
  no title page was ever seen. `2009` reflects the documented release of the
  benchmarking programme, not a date read off the document.
- **Also unconfirmed:** whether a specific edition/volume number should be cited, and
  the exact form of the co-preparing body (the Institute of Urban Transport is credited
  on the programme, recorded in the entry's `note`).
- **Action before submission:** if the paper quotes a *specific benchmark value* from
  this document, obtain the PDF and confirm the year and page. If it is cited only as
  general policy context, the current entry is adequate.
- **Caveat on the issuer's name:** the ministry was reorganised into the **Ministry of
  Housing and Urban Affairs (MoHUA)** in 2017. The document was issued by the
  then-**Ministry of Urban Development (MoUD)**, which is what the entry says. Do not
  "modernise" this to MoHUA — that would misattribute a pre-2017 document.

---

## B. Named in the source material, but EXCLUDED — could not be verified

### B1. "Li et al. (2022)" — cited in `paper/gaps/04_LITERATURE_POSITIONING.md`

**This is the one item that needs the author's attention.**

`04_LITERATURE_POSITIONING.md` line 56 states that "Li et al. 2022 report Euclidean/network
area ratios around 1.3" and uses that figure to argue our 37.4% median overstatement sits
inside the documented range. **No such paper could be identified.** Crossref bibliographic
queries on the Euclidean-vs-network catchment comparison theme for 2022 returned nothing
matching an author "Li" with that finding.

Consequences:

1. It is **not** in `references.bib`.
2. **The 1.3 ratio must not appear in the paper** unless the author can produce the actual
   source. It is currently an uncited number attributed to an unidentified work — precisely
   the kind of claim that gets flagged.
3. **The positioning argument does not need it.** The three shipped antecedents —
   `gutierrez2008distance`, `biba2010new`, `elgeneidy2014new` — already establish that
   straight-line buffers overstate catchment population, which is the whole point of the
   passage. Rewrite the sentence to lean on those three and drop the specific ratio, or
   state our own measured ratio without claiming an external comparator.

---

## C. Thematic searches that returned nothing citable

These themes were in the brief's "also search" list. Searching produced no result
on-topic enough to cite honestly. **These are gaps in this search, not proof the
literature is empty** — if the author knows a specific paper in any of these areas,
it should be added (and verified) rather than assumed absent.

| Theme sought | Outcome | What shipped instead |
|---|---|---|
| An empirical **Indian bus route rationalisation** case study | No match. Hits were Japan, Taipei and Bogor network-restructuring studies — wrong context. | `badami2007analysis`, `pucher2005urban`, `verma2014public` cover the Indian bus-sector context, though none is a rationalisation case study. |
| **India-specific GTFS / open transit data** paper | No verified match. | `wessel2017constructing` (GTFS construction from a real-time feed) covers the generic method. |
| **Bus network redesign political feasibility** | No match. Hits were street-redesign valuation and US ridership studies. | `walker2008purpose` covers the ridership-vs-coverage goal conflict, which is the substantive part of that argument. |
| **Demand-free / supply-side-only transit planning** as a named approach | No match. This is consistent with the paper's own novelty claim, but absence of evidence is not evidence of absence — keep the "to our knowledge" hedge that `04_LITERATURE_POSITIONING.md` already prescribes. | — |

The lack of a direct predecessor for the last row **supports but does not prove** the
novelty claim. Keep it hedged.

---

## D. Corrections — commonly-miscited works whose real details differ

Recorded because the wrong versions circulate widely and may be sitting in the author's
notes or in a co-author's draft.

### D1. Pucher et al. is **2005, not 2007**

The brief requested "Pucher 2007". The real paper is:

> Pucher, J., Korattyswaropam, N., Mittal, N., Ittyerah, N. (2005). Urban transport crisis
> in India. *Transport Policy* **12**(3), 185–198. DOI `10.1016/j.tranpol.2005.02.008`

Shipped as `pucher2005urban`. Note the cite key deliberately reads `2005`. There *is* a
related 2007 Pucher item in circulation, but the *Transport Policy* article — the one this
paper wants, and conveniently in the target journal — is 2005.

### D2. Badami & Haider's real title is narrower than usually quoted

Often paraphrased as being about urban transport generally. The actual title is:

> "**An analysis of public bus transit performance in Indian cities**" — *Transportation
> Research Part A* **41**(10), 961–981. DOI `10.1016/j.tra.2007.06.002`

Shipped verbatim as `badami2007analysis`. The year 2007 is correct for this one.

### D3. "Jenks natural breaks" is really Fisher's (1958) algorithm

The optimal-partition algorithm universally called "Jenks natural breaks" was published by
Walter D. Fisher in 1958, nine years before Jenks (1967), as:

> Fisher, W. D. (1958). On grouping for maximum homogeneity. *JASA* **53**(284), 789–798.
> DOI `10.1080/01621459.1958.10501479`

**Both are shipped** (`fisher1958grouping`, `jenks1967data`). Recommended usage: cite Jenks
for the cartographic classification convention and Fisher for the algorithm actually
implemented. Citing Fisher alongside Jenks is a small, cheap signal of methodological care
— and it also insures the classification claim against the fact that Jenks 1967 is the one
reference here without a machine-readable record (see A1).

### D4. Saltelli *Primer* — Crossref dates the DOI to 2007, the book is 2008

`10.1002/9780470725184` is deposited with year **2007** (online release); the print
monograph is **2008** (ISBN 9780470059975), which is how it is universally cited. Shipped as
`saltelli2008global` with year 2008 — correct, but do not be alarmed if a DOI resolver
shows 2007.

### D5. Ceder 1st edition — DOI belongs to the CRC re-release

The 2007 1st edition was originally issued under the Elsevier Butterworth-Heinemann imprint,
but the DOI (`10.1201/b12853`, ISBN 9780429214004) is a **CRC Press** deposit. The shipped
entry follows the verified CRC record and carries a `note` recording the original imprint.
If the author holds the physical Butterworth-Heinemann copy, switching `publisher` is
defensible — the DOI stays the same either way.

---

## E. Edition and year judgement calls

Not errors; decisions that a copy-editor or co-author might reasonably make differently.

| Entry | Call made | Alternative |
|---|---|---|
| `walker2011human` | **2011**, Island Press — the first edition (OpenLibrary `first_publish_year` 2011, hardcover ISBN 9781597269711). | Many authors cite the 2012 paperback (ISBN 9781597269728); a *revised* edition appeared in 2024 from Princeton UP (DOI `10.2307/jj.41003582`). All three are the same book. Cite 2011 unless quoting page numbers from a specific printing. |
| `elgeneidy2014new` | **2014** — the print issue, *Transportation* 41(1), 193–210. | Online-first was 2013 (hence the `-013-` in the DOI). 2014 is standard and matches the brief. |
| `ceder2016public` | 2nd edition, 2016 — subtitle *Modeling, Practice and Behavior*. | The 1st edition (2007) has a **different subtitle** (*Theory, Modelling and Practice*). Both shipped; do not mix the subtitles. |
| `trb2013transit` | Authored by the consultant team (Kittelson & Associates et al.), per the Crossref/National Academies record. | Frequently cited corporately as "TRB (2013)" or "TCRP Report 165". The cite key is `trb2013` for that reason; the series field carries the TCRP number. |
| `osm2024planet` | `@misc`, accessed 2024. | Update the access year to match the actual data-extraction date used in the study before submission. This is a data source, not a bibliographic claim. |
| `sobol2001global` | Author rendered `{Sobol'}` with the brace-protected prime. | Some styles render "Sobol" or "Sobol′". The braces prevent BibTeX from mangling the apostrophe; leave them. |

---

## F. Nothing else was dropped

Every other item on the brief's required list and its "also search" list either shipped
verified, or is accounted for in sections B and C above. **No entry in `references.bib`
is unverified, and no entry was included on the strength of recall alone.**

---

## F. Added 2026-09-30 (with modules a05/a13/a16 and the §5 write-up)

- `welding1957instability`, `osuna1972control` — verified by Crossref DOI (10.1057/jors.1957.21;
  10.1287/trsc.6.1.52). Cited for the waiting-time formula used by a05/a13.
- `asrtu2024fleet` — grey literature; the document is the data source of a16 (URL recorded in
  `data/derived/a16_peer_regression.json`). No DOI exists.
- **Excluded:** Mohring (1972), *American Economic Review* 62(4) — named in a05's citations but not
  resolvable through Crossref in this environment; not cited in the prose. Add it only after checking
  the JSTOR record by hand.
- **Needed if a14 constants are confirmed (decision D8):** IPCC (2006) Guidelines Vol. 2 Ch. 3; CEA CO₂
  Baseline Database (current version); the GCC tender source for per-km cost. None is cited yet,
  deliberately — a14 is provisional.
