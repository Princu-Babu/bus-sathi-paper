# Pending Decisions — v2

**Kashmir bus route rationalisation** → *Transport Policy*

Rewritten 2026-10-01 against the live repository and the journal's own *Guide for Authors*. It replaces v1
(kept in `paper/archive/` with its full original discussion). Everything here is still open unless it is in
Part F.

---

## Why a v2

v1 grew by appending updates, so its early pages described finished work as unfinished. While rewriting it,
the journal guide was checked for the first time, and it changed three things:

1. **The length limit is 8,000 words, not 10,000.** *"Articles should normally be no longer than 8000
   words."* The 10,000 in our planning came from the co-author brief and was never verified.
2. **Review is double-anonymised.** The manuscript file must not identify the authors — including our GitHub
   links, which carry a personal username.
3. **Use of generative AI must be declared** in a section before the references, and the authors must have
   reviewed and edited all AI-assisted text so it reflects their own work.

---

## Part A — The list, ranked

| # | Decision | Who | Effort | Blocks |
|---|---|---|---|---|
| **1** | **D4** GPS consent, anonymisation, ethics status | Prashant | a conversation | submission |
| **2** | **D13** authors, order, affiliations, corresponding author, CRediT | Prashant + all | an email | submission |
| **3** | **D26** cut to 8,000 words — what moves to supplementary material | all | 2–3 days | submission |
| **4** | **D28** declare AI use; every author reviews the AI-assisted sections | all | 1–2 days reading | submission |
| **5** | **D27** anonymise the manuscript for double-blind review | Prashant | 2 hours | submission |
| **6** | **D2** the August field-observation table: real, with sheets? | whoever ran it | a message | §6, Abstract |
| **7** | **D5** run the §2.1 literature protocol, or drop it | Sharvesh, Ankit | 2 days or 2 hours | §2, Figure 2 |
| **8** | **D3** "Srinagar Municipal Area" wording in co-author text | Policy-Failure author | 1 sentence | §1, §3, §7 |
| **9** | **D1** §1.6 says six sections; there are eight | Misti, Avny | 1 paragraph (drafted) | §1 |
| 10 | **D20** accept four corrections to how §4 described the engine | Prashant | read §4 | §4 |
| 11 | **D22** report V2 (operator benchmark) as a fail | Prashant | yes/no | §6 |
| 12 | **D7** report the fleet as 1,011 plus the 1,130–1,266 observed-pace range | Prashant | yes/no | Abstract, §5, §8 |
| 13 | **D21** per-lakh benchmark: 63.5 on network-served residents (above MoHUA 40–60) | Prashant | yes/no | §4, §5, RTO deck |
| 14 | **D25** confirm cost & emission constants, or keep §5.12 marked provisional | Prashant | an hour | §5.12 |
| 15 | **D29** the public repositories: personal data, operator data, DOI | Prashant | an hour | data statement |
| 16 | **D30** co-author editorial flags (citations, unsourced numbers, missing paragraph) | co-authors | 1–2 days | §1, §2, §3, §7 |
| 17 | D18, D24, D12, D11, D10 — confirm the current handling | Prashant | read §5 | — |

**If you only do four things this week: 1, 2, 3 and 4.** Nothing else blocks submission as hard.

---

# Part B — Blockers

## D4 · GPS consent, anonymisation and ethics  *(1)*

**Question.** On what basis were the driver GPS traces collected; were drivers told they might be used for
research or planning; what is released; and was any ethics body consulted?

**Why it matters.** It can stop the paper at the editor's desk. ~157 drivers' daily movement is human-
subject data by any reading, and validation channel V4 — the paper's strongest observational evidence —
rests on it. The §3.6 ethics paragraph is deliberately blank.

**What is already true.** Only aggregates are used or released (corridor speeds, dwell, counts). The one
per-driver table is published only de-identified in the citable repository. The collection window is
**February–June 2026** (D23, resolved).

**What only you can write down:** (i) the collection basis (app terms? were drivers told?); (ii) the
anonymisation — already "aggregates only"; (iii) ethics status: approved (committee + reference), exempt, or
**not consulted**. *"Not consulted" is an acceptable answer to write down. Silence is not.*

**Also:** rotate the Firestore service-account key that was on disk in the trace repository.

**Recommendation.** Aggregates only + a plain statement of (i)–(iii). **If nothing is done:** cannot submit.

## D13 · Authors, order, affiliations, CRediT  *(2)*

A draft CRediT table is in `paper/front_matter/credit_statement.md`; surnames, order, affiliations and the
corresponding author are blank and cannot be inferred. Per the guide, author details go **only on a separate
title page** (D27). **If nothing is done:** cannot submit.

## D26 · Cutting to 8,000 words  *(3 — new)*

**Question.** The draft has ~13,600 body words against an 8,000 norm. What moves out?

**Why it matters.** A 70 %-over manuscript is a likely desk return. The journal's "normally" gives a little
room, not 5,600 words of it. (The 8,000 appears to apply to the main text; the guide does not say whether
references and tables count — assume they do not, but keep well under.)

**Proposed allocation** (details in `paper/WORD_BUDGET_PLAN.md`):

| | Now | Target | How |
|---|---:|---:|---|
| §1 Introduction | 2,343 | 900 | Policy-Failure block → §3.3, condensed; merge §1.1–§1.2 |
| §2 Literature | 1,413 | 900 | narrative focus; move protocol detail to supplement (or drop, D5) |
| §3 Study area | 1,242 | 700 | diagnostics → §4.2 or supplement |
| §4 Methodology | 2,422 | 1,700 | equations stay; QA gates, faithfulness detail → supplement |
| §5 Results | 2,412 | 1,800 | §5.10 transfers, §5.11 operations, §5.12 cost → supplement (one sentence each stays) |
| §6 Validation | 1,041 | 650 | V4 detail → supplement |
| §7 Discussion | 2,045 | 1,000 | merge co-author block into §7.2; trim §7.8 |
| §8 Conclusions | 475 | 350 | — |
| **Total** (Abstract excluded; it is 228 of a 250 limit) | **13,393** | **8,000** | |

Nothing is lost: a *Supplementary Material* file carries the moved subsections, and every number stays in the
repository and the ledger.

**Options.** A — this allocation (recommended). B — target a journal with a longer limit (D17 below; check
its guide first). C — submit long and ask the editor (risky).

**If nothing is done:** the manuscript goes in at ~13,600 words.

## D28 · Declaring generative-AI use  *(4 — new)*

**Question.** The journal requires a section *"Declaration of generative AI and AI-assisted technologies in
the manuscript preparation process"* before the references, and holds authors accountable for reviewing and
editing every AI-assisted passage and checking every AI-supplied reference.

**The facts to declare.** Claude (Anthropic) was used to write and run the analysis code, draft §4–§6, §8,
the Abstract and parts of §7, compile the ledger and bibliography (each reference was checked against
Crossref), and draw the figures. AI must not be listed as an author (git commit trailers are not authorship).

**What the authors must actually do.** Read §4–§6 and §8 critically and rewrite them in their own voice
where needed — this is also the best way to cut words (D26). Draft statement:

> *During the preparation of this work the authors used Claude (Anthropic) to write and execute analysis
> code, draft and edit sections of the manuscript, and verify references. After using this tool, the
> authors reviewed and edited the content as needed and take full responsibility for the content of the
> published article.*

**If nothing is done:** a policy breach discovered after submission is far worse than a declaration made
before it.

## D27 · Double-anonymised review  *(5 — new)*

Two files are required: a **title page** (authors, affiliations, acknowledgements, competing interests,
corresponding author) and an **anonymised manuscript** (no names, affiliations or acknowledgements). Three
things in our draft identify the authors:

1. Links to `github.com/Princu-Babu/...` and `GrostesqueChip/...` — replace with an anonymised mirror for
   review (e.g. anonymous.4open.science) and restore the real links on acceptance.
2. The competing-interest option that says the authors built the engine and app — this goes on the title
   page, not in the manuscript.
3. Self-references such as "our dashboard" or "we developed Bus Sathi" — rephrase in the third person.

**If nothing is done:** likely returned for anonymisation.

## D2 · The August field-observation table  *(6)*

A co-author draft contains ten on-street sessions (1–12 August) on named Srinagar corridors. If real, it is
the paper's **only demand-side observation** — the single biggest possible upgrade to §6. No data file, method
note or claim ID exists, so **no number from it is used**. Needed: who, when, where, method (fixed-point
count? how long?), the raw sheets (a photo is enough), then ledger IDs. **Recommendation:** ask this week.
**If nothing is done:** it stays out; §6 remains supply-side only.

## D5 · The §2.1 systematic-review protocol  *(7)*

§2.1 describes a search that has **not been run** (placeholders `[Scopus]`, `[N]`). Option A: run it (~2 days)
and code Table 1. Option B: delete §2.1 and Table 1 and keep §2 narrative (~2 hours; also helps D26). Fake
PRISMA counts are misconduct; a narrative review is not. **Recommendation:** B unless someone has two days.
**If nothing is done:** placeholders cannot go to the journal.

## D3 · "Srinagar Municipal Area" wording  *(8)*

Three co-author passages (Policy-Failure block, the §3.1 heading — already changed and disclosed in FLAG 3-A —
and the §7 Policy-Contribution block) describe a Srinagar-only study; the plan covers ten districts.
**Recommendation:** one joining sentence by that block's author: *"The institutional analysis is specific to
Srinagar, where permit overlap is most acute; the network plan covers all ten districts of Kashmir
Division."*

## D1 · §1.6 roadmap  *(9)*

§1.6 says "Section 6 concludes"; the paper has eight sections. Replacement text is drafted in FLAG 1.6-a.
One paragraph.

---

# Part C — Sign-offs (a yes or no each)

| # | Decision | What the draft does now | Recommendation |
|---|---|---|---|
| **D20** | Four places §4 misdescribed the engine: κ is 0.33 not 0.18; Eq. 8 *does* set 67 rural headways; the merge rule adds a 2.5 km start condition and merges only into a cluster's leading trunk; layover is ×1.10 and the backbone fleet is max(formula, CHALO) | §4 corrected, each with CL-59 | **Accept** — a reviewer with the public code would find them |
| **D22** | V2: plan backbone fleet is 1.29–1.58× CHALO scaled to 15 min | reported as **fail**, circularity disclosed first | **Accept** — the band was pre-registered |
| **D7** | Fleet: 1,011 as specified; 989–1,058 under parameter uncertainty; **1,130–1,266 at observed pace** | Abstract, §5.7, §6, §8 say so | **Accept**; if the RTO needs one number, 1,182 (median at observed pace) |
| **D21** | Buses per lakh: 15.4 (division), 43.6 (engine's Euclidean served), **63.5** (network-served, above MoHUA 40–60) | all three reported | **Accept**; check which one the RTO deck quotes |
| **D25** | Cost/CO₂ constants (km/L, INR/km, grid factor, e-bus kWh/km) are unverified ranges | §5.12 labelled provisional; not in Abstract | Confirm with sources, **or** move §5.12 to supplement (helps D26) |
| **D18** | 20 of the 55 routes the plan calls high-priority fall in the objective bottom tier | reported in §5.8 with a policy sentence | Keep; the RTO should justify or demote those 20 |
| **D24** | Day-one ~8 boardings/trip on the backbone vs 19–37 today | §5.11 frames the plan as a supply-led bet; recommends staged procurement | Keep |
| **D12** | 13,087 residents lose bus access; 32 via-routings suppressed | named in §5.9 and Table 5g | Keep as prominent as it is |
| **D11** | Before/after equity Gini not computable (merged permits have no geometry) | stated, not faked | Keep |
| **D10** | τ = 100 m, θ = 0.65 | both swept; direction of the τ result invariant; 207 surviving pairs pass the engine's own merge test at θ = 0.65 | Keep. **Upgrade available:** τ can now be anchored empirically from the Microsoft footprints (distance from building to nearest walkway) — ~1 hour of work if wanted |
| **D17** | Journal | *Transport Policy* (8,000 words, double-blind, AI declaration) | Confirm. If you consider another journal, check its guide first — do not assume its limits |

---

# Part D — Public repositories (D29)

| Item | State | Needed |
|---|---|---|
| Citable repository `Princu-Babu/Bus-sathi` | live, tagged v1.0.0, CI green | **Get a DOI:** link the repo in Zenodo, then create a GitHub Release from tag `v1.0.0`. Cite the DOI in the data statement. |
| Data statement (`front_matter/data_availability.md`) | points at the working repos | Point it at `Bus-sathi` (anonymised mirror for review, D27) |
| `driver_days.csv` (per-driver, hashed IDs) | **public in `bus-sathi-paper` and its history**; only de-identified in `Bus-sathi` | Decide: remove from `bus-sathi-paper` history (needs a force-push; teammates re-clone), or accept |
| CHALO / SSCL aggregates | published in all repos | Confirm SSCL/Chalo are content; if not, withdraw and keep only derived outputs |
| Permit register | published | Confirm the RTO is content with release |
| Your email in two engine geocoding scripts (Nominatim contact) | public | Accept, or swap for a project address |
| `CITATION.cff` authors | Prashant + "Bus Sathi research team" | Replace after D13 |

---

# Part E — Co-author editorial flags (D30)

Open flags in the manuscript, grouped by owner. Each is a tinted callout in the working-draft PDF.

**Misti, Avny (§1)**
- 1.1-a — five external figures need page-level citations (490→763 M urban projection; 0.13–0.14 buses/1,000;
  MoHUA 0.44 benchmark; ">400 Class-I cities"; "<15 agencies publish GTFS").
- 1.1-b — citation style, and "CSE & CITIES Forum" appears two ways. **Pucher et al. is 2005, not 2007.**
- 1.2-b — the US$ 40 M/km metro and US$ 2.5 M/km BRT figures need a year and currency base.
- 1.3-a — the frequency-rule equation was lost in extraction; the authors must supply it.
- 1.4-b — "64.5 % female ridership" and "2.5 million tourists" have no source.
- 1.5-b — objective O5 promises validation §6 cannot give; align to "decision-robustness".
- 1.5-c — contribution (3) claims a "seasonal" demand proxy; seasonality is not modelled. Narrow the claim.
- PF-a/3-B — move the Policy-Failure block to §3.3 (also D26).

**Sharvesh, Ankit (§2)**
- 2-B — the Euclidean-vs-network critique is **not novel**: cite Gutiérrez & García-Palomares (2008) and Biba
  et al. (2010) by name before §4 measures it.
- 2-C — the data-intensity cross-tabulation depends on D5.
- 2-D — reconcile every citation with `references.bib` (map in `COAUTHOR_CITATION_MAP.md`).

**Krishna (§3)**
- 3-C — Table 2 lists data the study does not hold (land use, terrain, tourist arrivals, fleet register,
  cost norms): obtain or strike.
- 3-A — heading change disclosed; revert if you object.

**Ankit, Avny, Misti (§7)**
- 7-A — the **political-feasibility paragraph is missing**: 458 merged permit rows are contested livelihoods;
  cite the international network-redesign literature. Required.
- 7-C — "applies to 400+ cities" must read as preconditions met, not validity shown.
- 7-E — the Policy-Contribution block overlaps §7.1–§7.2 and uses Srinagar scope (D3).

**Prashant (§3.6)**
- 3-E — the reproducibility wording can now be strengthened: every module runs end to end and CI reproduces
  the results in the citable repository.

---

# Part F — Resolved (for the record)

| # | Resolution | Date |
|---|---|---|
| D6 | Data-maturity ladder ranked by Sobol' indices (§7.5) | 2026-09-30 |
| D9 | Microsoft footprints downloaded; V1 passes (ρ 0.975 route, 0.950 grid), partly circular | 2026-10-01 |
| D14 | Figures 1, 3–9, 9b, S1, S2 drawn by `fig_generate_all.py`; Figure 2 waits on D5 | 2026-09-30 |
| D15 | Superseded by D26 (the limit is 8,000) | 2026-10-01 |
| D19 | a03 aligned with a04's Jenks convention | 2026-09-30 |
| D23 | GPS window is February–June 2026; `DATA_AVAILABILITY.md` corrected | 2026-10-01 |
| 7-B | = D6 | 2026-09-30 |
| 7-D | Funding sequence: 30 % of the fleet reaches 92 % of coverage (§7.7) | 2026-09-30 |

Full v1 discussion of every item: `paper/archive/PENDING_DECISIONS_v1_2026-09-30.md`.
