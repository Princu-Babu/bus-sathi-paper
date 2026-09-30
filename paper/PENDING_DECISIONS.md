# Pending Decisions and Open Questions

**Kashmir bus route rationalisation → *Transport Policy* manuscript**
Prepared for Prashant Bhadana and the co-author team · assembled 2026-09-13

---

## How to use this document

Every item below is a question **only a human on this project can answer**. They are not questions I can
resolve by reading the code, re-running a module, or searching the literature — I have already tried each of
those, and where a question *could* be settled that way I have settled it and recorded the answer in Part E
rather than asking you.

Each decision has the same six parts:

- **The question**, stated in one sentence.
- **Why it matters** — what breaks if it goes unanswered.
- **The evidence** — what is actually in the repository right now, with file paths, so you can check me.
- **The options**, with the honest consequence of each.
- **My recommendation**, and why.
- **If you do nothing** — the default that will apply, so silence is never accidentally a decision.

Answer them in any order. The five in **Part A** are the ones that can stop the paper being published; the
rest change its quality, not its viability.

> **One rule this document obeys.** Nothing here is padded and nothing is assumed. Where I do not know
> something, the entry says so. Where a number is not yet computed, the entry says the module has not run
> rather than offering an estimate. If any statement below turns out to be wrong when you check it against
> the repository, treat the whole document as stale and tell me — I would rather rebuild it than have you
> answer a question that rests on a false premise.

---

## Decision register — the whole list at a glance

| # | Decision | Severity | Who decides | Blocks |
|---|---|---|---|---|
| D1 | §1.6 roadmap describes a six-section paper; the manuscript has eight | **Blocker** | Misti + Avny (§1 owners) | Submission |
| D2 | The §6 field-observation table (10 sessions, 1–12 Aug) — use it or not | **Blocker** | Whoever ran the sessions | §6, Abstract |
| D3 | Scope: "Srinagar Municipal Area / SMR" vs Kashmir Division | **Blocker** | Prashant + all | §1, §3, §7, Abstract |
| D4 | GPS ethics, consent and anonymisation | **Blocker** | Prashant | Submission (Elsevier gate) |
| D5 | §2.1 systematic-review protocol — run it or drop it | **Blocker** | Sharvesh + Ankit | §2, Table 1, Figure 2 |
| D6 | Rank the data-maturity ladder by Sobol' variance reduction | High | Prashant (needs a09) | §7.5, Table 8 |
| D7 | Report fleet as a point (1,011) or an interval | High | Prashant | Abstract, §5, §8 |
| D8 | Cost and emission constants for a14 | Medium | Prashant | §5.12, §7 |
| D9 | Building footprints for validation channel V1 | Medium | Prashant | §6.1 |
| D10 | τ = 100 m and θ = 0.65 — keep as defaults or re-anchor | Medium | Prashant | §4.3, §4.6 |
| D11 | Before/after Gini is NOT_COMPUTABLE — how to say so | Medium | Prashant + Misti | §5.9 |
| D12 | The transfer analysis found losers — how prominently to report | High | Prashant + Ankit | §5.10, §7.8 |
| D18 | Objective tiers agree with the deployed plan's bands only 68.3% | High | Prashant + Misti | §5.3, §4.6 |
| D19 | a03 and a04 use opposite Jenks boundary conventions | Low | Prashant | §5.3 figures |
| D13 | Author list, affiliations, corresponding author, CRediT | Blocker (late) | Prashant | Submission |
| D14 | Which 8 figures, and who draws them | Medium | Prashant + Misti | All |
| D15 | Word budget: the draft is ~11,900 words against a 9,000–10,000 target | High | All | Submission |
| D16 | What exactly goes in the public repository | Medium | Prashant | Data-availability statement |
| D17 | Journal target — confirm *Transport Policy* | Low | All | Formatting |
| D20 | Confirm four corrections to the method as published (Part G) | High | Prashant | §4 |
| D21 | Per-lakh benchmark: 63.5 on network-served, above MoHUA band | Medium | Prashant | §4.8, §5.4, RTO deck |
| D22 | V2 fails the ±15% band — report as fail | High | Prashant + Avny | §6 |
| D23 | GPS collection window conflict (Feb–Jun vs Jun–Jul) | Blocker (with D4) | Prashant | Ethics, data availability |
| D24 | Day-one load ~8 boardings/trip — "supply-led bet" framing | Medium | Prashant + Ankit | §5.11, §7 |
| D25 | a14 cost/emission constants (was D8) | Medium | Prashant | §5.12 |

*Status 2026-09-30: D9, D14 (except Fig 2, 9, 9b), D19 resolved — see Part G.*

---

# Part A — Blocking decisions

These five can each, on their own, stop the paper from being published. Four of them are cheap to answer.

---

## D1 · The §1.6 roadmap describes a six-section paper

### The question
§1.6 of the co-author draft tells the reader the paper has six sections. The paper has eight. Which numbering
is correct, and who rewrites the paragraph?

### Why it matters
§1.6 is the paragraph a reviewer uses to navigate. If it says "Section 6 concludes" and the reader then finds
§6 is *Validation* and §8 is *Conclusions*, every cross-reference in the paper is suspect from page 3 onward.
Worse: under the six-section scheme there is **no slot at all for §6 Validation** — the section the co-author
attachment itself describes as the one that "decides the paper's fate."

### The evidence
- `paper/sections/01_introduction.md` §1.6, transcribed verbatim from the attachment, reads: *"Section 2
  reviews the literature… and details the physical and institutional setting… Section 6 concludes."*
- The same attachment's own operative structure — the table that assigns owners and word budgets — lists
  **eight** sections: §1 Introduction (Misti, Avny, 1,200 w) · §2 Literature (Sharvesh, Ankit, 1,400 w) · §3
  Study Area (Krishna, 1,100 w) · §4 Methodology (Prashant, 2,300 w) · §5 Results (Prashant, Misti, 2,400 w) ·
  §6 Validation (Avny, Krishnan, Prashant, 900 w) · §7 Discussion (Ankit, Avny, Misti, 1,200 w) · §8
  Conclusions (Ankit, Prashant, Sharvesh, 400 w).
- The repository has been built on the eight-section scheme since before the attachment arrived. All nine
  section files exist under that numbering.
- Your instruction was *"do as told in the pdf thats the format."* I read that as: adopt the PDF's operative
  structure — which is the eight-section table, not the stray sentence inside §1.6. **The repository and the
  PDF's own structure already agree.** The conflict is between the PDF and one paragraph of itself.

### The options
| Option | What happens | Cost |
|---|---|---|
| **A. Keep eight sections, rewrite §1.6** | The roadmap paragraph is replaced with one that names all eight sections. Everything else is untouched. | One paragraph. Replacement text is already drafted in the FLAG 1.6-a callout — it is *proposed, not applied*. |
| B. Collapse to six sections | Validation is folded into Results or Methodology; Discussion and Conclusions merge. | Loses the standalone Validation section. Given that validation is the paper's most exposed flank, burying it reads as evasion. |
| C. Leave it | A reviewer finds the contradiction. | Avoidable credibility damage on page 3. |

### My recommendation
**A.** It is one paragraph, the replacement is already written, and it preserves the section the paper most
needs to display prominently.

### If you do nothing
The prose stays as written and un-renumbered — I have not touched it — and the contradiction ships. This is
the single cheapest blocker on the list to clear.

---

## D2 · The §6 field-observation table

### The question
The co-author attachment contains a table of **ten field-observation sessions conducted 1–12 August** on named
corridors, with buses observed, frequency, waiting time, route group and overlap. Is this real data collected
by a member of this team, and may it be used?

### Why it matters
This is the **only demand-side observation in the entire project.** Everything else is supply-side. If it is
real, it materially strengthens §6 — it is the one channel that puts a human being at a bus stop counting
buses, which is exactly what a reviewer will ask for. If it is illustrative or reconstructed, using it is
research misconduct.

I have deliberately **not** imported a single number from it into §5, §6 or the Abstract, and I will not until
this is answered.

### The evidence
- The table is in the attachment and is reproduced in `paper/_ak_reflowed.txt`, which is the reflowed
  extraction of the source PDF. The corridors named are: TRC–Hazratbal; Soura–Lal Ded and Soura–Jehangir
  Chowk; Saidakadal–Bypass; Lalbazar–Lal Ded; Malbagh–Lal Ded; Parimpora–Pantha Chowk; Batamaloo–Pantha
  Chowk; Lal Chowk–Rangreth; Qamarwari–Pantha Chowk; Narbal–Lal Chowk.
- The attachment's own prose around it is appropriately careful, describing it as something that *"should…
  be interpreted as a validation exercise rather than a comprehensive operational survey."* That is the
  language of someone who did the work and knows its limits — which is a point in favour of it being real.
- **There is no data file for it anywhere in this repository or in the engine repository.** No CSV, no
  spreadsheet, no field sheet, no photographs. I searched both.
- There is no claim ID for it in `paper/CLAIM_LEDGER.md`.

### What is needed before a single number can be used
1. **Who collected it, on what dates, at which locations.** Names and a date range.
2. **The method.** Was it a fixed-point count over a stated observation window? How long at each site? One
   observer or several? Time of day?
3. **The raw data file.** Even a photographed field sheet transcribed into a CSV is enough. It must be staged
   in `data/raw/` and hashed into `data/MANIFEST.md` like every other input.
4. **A new claim ID** in the ledger for every number that enters the manuscript.
5. **The ethics position**, which is easier here than for the GPS: counting buses in a public street observes
   vehicles, not identifiable people, and normally needs no consent — but it should still be stated.

### The options
| Option | Consequence |
|---|---|
| **A. It is real → supply items 1–4 above** | §6 gains a genuine demand-side observation channel. This is the single largest available upgrade to the paper's validation, and it is worth chasing hard. |
| B. It is real but the raw sheets are gone | It can still be reported, but only as a described observation with its provenance limits stated in the text. Weaker, still honest, still publishable. |
| C. It is illustrative / reconstructed | It is removed from the manuscript entirely. §6 stays supply-side-only, as it is now. |

### My recommendation
Chase **A**. Ask whoever ran the sessions for the field sheets this week — memory of an August count fades,
and the sheets get thrown out. Even ten sessions of real counts is worth more to a reviewer than any
additional modelling.

### If you do nothing
The table stays in the source extract, attributed, and **no number from it enters the manuscript**. §6 remains
supply-side only. That is the safe default and it is what is in the draft today.

---

## D3 · Scope — "Srinagar Municipal Area" versus Kashmir Division

### The question
Several passages of co-author prose describe the study as covering Srinagar and the Srinagar Municipal
Corporation area. The plan covers ten districts. Which is the paper's scope, and how is the difference
explained?

### Why it matters
The denominator changes by a factor of four. Coverage of 24.2% against 6,584,762 division residents is a
different claim from 24.2% against ~1.66 million in the Srinagar urban agglomeration. A reviewer who spots
both framings in one manuscript will not try to work out which is meant; they will conclude the authors did
not know either.

### The evidence
Three separate places carry the Srinagar framing, all of them co-author prose I have left untouched:

1. **The "Policy Failure" block** (currently at the end of §1) says *"bus service data for Srinagar (the area
   falling within the limits of the Srinagar Municipal Corporation (SMC)) was studied."*
2. **The §3.1 heading** in the attachment reads *"The SMR as a critical case."* This is the **one place** in
   the four co-author sections where I changed a co-author's words rather than flagging them — the heading now
   reads "Kashmir Division as a critical case", because leaving "SMR" in a heading would push a barred scope
   into the table of contents. It is disclosed at the point of change in FLAG 3-A. **Tell me to revert it and
   I will.**
3. **The §7 "Policy Contribution" block** says "Srinagar" and "Srinagar Municipal Area" throughout. That block
   is reproduced verbatim and unchanged.

Meanwhile §1.4 of the same attachment is already correctly on the division framing — ten districts, 15,948
km², 6.58 million, 640+ permits, 38–42 permits on the Lal Ded corridor. So the attachment is internally
inconsistent, not simply wrong.

### The reconciliation I think is true
The **institutional analysis is genuinely Srinagar-specific** — the RTA/STA competence question, the permit
law, the named overlapping corridors are all about the city. The **network plan is division-wide**. Both
statements are true; they just need one sentence to hold them together, something like:

> *The institutional analysis that follows is specific to Srinagar, where permit overlap is most acute and
> where the RTA/STA boundary problem is sharpest; the network plan developed in §4–§5 covers all ten
> districts of Kashmir Division.*

**I have not inserted that sentence.** Putting words into a co-author's paragraph is not an editorial call.

### The options
| Option | Consequence |
|---|---|
| **A. Division-wide plan + Srinagar-specific institutional analysis, joined by one sentence** | Everything already written stays. One sentence added, by its author. |
| B. Narrow the whole paper to Srinagar | Discards the ten-district analysis, the 6.58 M denominator and most of §5. Would require rebuilding the pipeline. Not recommended. |
| C. Rewrite the co-author blocks to be division-wide | Changes their text. Only they can authorise it. |

### My recommendation
**A**, with the joining sentence written by the author of the Policy Failure block.

### If you do nothing
The manuscript ships with both framings visible and flagged. The flags are in the working draft, so at least
nobody is misled internally — but the flags cannot go to the journal.

---

## D4 · GPS ethics, consent and anonymisation

### The question
Under what basis were the driver GPS traces collected, were the drivers told, is the released data
anonymised, and did any ethics body review this?

### Why it matters
This is the one item on the list that can stop the paper at the *editorial desk*, before review. Elsevier
requires an ethics statement for human-subjects-adjacent data. Roughly **157 identifiable workers' daily
movement traces** is human-subjects-adjacent by any reading. A reviewer who reaches §6, sees the GPS corpus,
and finds no consent paragraph will stop reading.

It also matters because **validation channel V4 rests entirely on this corpus.** If the data cannot be used,
§6 loses its only observational channel and the paper's validation becomes internal-consistency checking.

### The evidence
- `paper/sections/03_study_area.md` §3.6 currently contains reproducibility and licensing text, and then
  **a deliberately blank space where the ethics paragraph belongs.** I did not write a plausible-sounding
  statement there. Fabricating an ethics position is worse than having none.
- The corpus: 43,809 clean runs, approximately 157 drivers, February–June 2026, from the Bus Sathi driver
  application (CL-18).
- The staged files use **hashed driver identifiers**. That is good practice and it is *not sufficient on its
  own*: a trace that starts from the same depot every morning and follows the same route is re-identifiable
  to anyone who knows the roster, regardless of what the ID field says.
- Separately and urgently: the Firestore admin key in the companion trace repository is gitignored but was
  present on disk. **It should be rotated** whether or not this paper is ever published.

### The three things that must be written down
**(i) Collection basis.** Why was the location data collected in the first place — operational tracking for
the app? Was there a terms-of-service the drivers accepted? Were they told, at any point, that operational
traces might be used for research or planning?

**(ii) Anonymisation mechanism.** What is actually released? My recommendation: release only *aggregated
corridor-level* statistics — median moving speed, run counts per corridor, dwell distributions — and **no
individual traces at all**. That removes the re-identification risk entirely at almost no cost to the paper,
because §6 only ever uses aggregates.

**(iii) Ethics review status.** One of: approved by a named committee with a reference number; formally
exempted; or **not consulted**.

> **"Not consulted" is an acceptable answer to write down. Silence is not.** Many operational-data studies
> proceed without formal review and say so plainly. What sinks a paper is the appearance of concealment.

### The options
| Option | Consequence |
|---|---|
| **A. Aggregates only + a plain-language statement of (i)–(iii)** | The likeliest safe route. No individual traces released; the paper says exactly what happened. |
| B. Seek retrospective ethics review | Slower, stronger. Worth doing if the institution offers it quickly. |
| C. Drop the GPS channel | §6 loses V4 and with it the strongest evidence in the paper. Only if (i) has no acceptable answer. |
| D. Leave §3.6 blank | Desk rejection risk. |

### My recommendation
**A**, and start today, because it depends on facts only you know and it gates the submission.

### If you do nothing
The paragraph stays blank and the paper cannot be submitted. This is the hardest blocker on the list, not
because it is difficult but because nobody else can answer it.

---

## D5 · The §2.1 systematic-review protocol

### The question
§2 currently states a systematic review protocol and promises a synthesis matrix of 45–60 coded studies
(Table 1). **The search has not been run.** Do we run it, or do we drop the protocol and reframe §2 as a
narrative review?

### Why it matters
A PRISMA-style protocol with invented database names, a fabricated corpus size, or a made-up date window is
research misconduct, and it is the single easiest thing in a paper for an editor to catch — the counts have to
reconcile, and if they do not, it is a desk reject. There is no version of this where the protocol stays and
the numbers are estimated.

### The evidence
`paper/sections/02_literature.md` §2.1 is written as a **template with bracketed placeholders** — `[Scopus]`,
`[Web of Science]`, `[N]`, `[2000–2026]`. The search string and the inclusion/exclusion criteria are fully
drafted and are good; only the execution is missing. Table 1 does not exist and **no module in `analysis/` can
produce it** — it is hand-coding work, not computation.

### The options
| Option | Effort | Consequence |
|---|---|---|
| **A. Actually run the search** | ~1–2 days | Record database, search date, exact string, hit counts at each screening stage, and inclusion/exclusion decisions. Code the surviving studies into Table 1 on the attachment's own scheme: geography · planning stage · method family · demand input · data intensity (1–5) · equity treatment · validation performed · produces an implementable plan · code released. The attachment is right that this raises perceived rigour more than any other three sentences in the paper. |
| B. Delete §2.1 and Table 1; reframe §2 as narrative | ~2 hours | Costs some rigour, costs nothing in integrity. *Transport Policy* publishes narrative reviews routinely. It does not publish fake PRISMA counts. |

### My recommendation
**A if anyone has two days; B otherwise.** Both are honest. B is far better than a half-executed A.

There is a knock-on: §2.8 promises a cross-tabulation of *data intensity* against *produces an implementable
plan*, and Figure 2 renders it. Both depend entirely on Table 1. Under Option B, §2.8 keeps its argument —
which is the paper's intellectual hinge and stands on its own — but drops the quantified gap claim, and
Figure 2 becomes a conceptual diagram rather than a data graphic.

One more thing, and it is important: if the coding is done and the cells do **not** cluster as expected, §2.8
must report what they actually show. A gap smaller than claimed is still a publishable finding. A gap asserted
without the table behind it is not.

### If you do nothing
The placeholders stay visible in the draft — which is safe internally and impossible externally.

---

# Part B — Analytical decisions

These change the paper's numbers or its claims. None of them can stop publication, but several determine how
strong the paper is.

---

## D6 · Ranking the data-maturity ladder by variance reduction

### The question
§7.5 defines a four-level data-maturity ladder (open data → census + road width → GPS → fare cards). The
attachment asks that the rungs be **ranked by the variance reduction each dataset would deliver**, taken from
the Sobol' indices. Do we run the Sobol' decomposition, or ship the ladder unranked?

### Why it matters
The attachment calls this *"one of the paper's most distinctive elements"*, and it is right. It converts a
data request — the thing every consultancy report ends with — into a research contribution: *here is what each
dataset is worth, in units of the uncertainty it removes.* I have not seen it done in this literature.

### The evidence
`analysis/a09_monte_carlo_sobol.py` **does not exist yet.** It is the single highest-value unwritten module in
the repository, because it produces three things at once: the Sobol' indices for §7.5, the fleet confidence
interval for D7, and validation channels V5 and V6.

The ladder in the current §7.5 draft is ordered by *methodological dependency*, which is defensible, and it
says so explicitly. It is **not** ordered by variance contribution, which would be an assertion.

### The options
| Option | Consequence |
|---|---|
| **A. Write and run a09** | §7.5 gains its best paragraph and §5 gains an interval fleet. I intend to do this regardless unless told otherwise. |
| B. Ship the ladder ordered by dependency | Honest, weaker, already drafted. |

### My recommendation
**A.** This is on my list and does not need your input — I am flagging it so you know what changes when it
lands.

### If you do nothing
I write a09 and the ladder gets ranked. The ranking will be whatever the indices say, including if they say
something inconvenient.

---

## D7 · Fleet as a point estimate or an interval

### The question
The plan's fleet is 1,011 vehicles. Do we report that number, or an interval around it?

### Why it matters
This is the number the RTO will quote and the number a reviewer will interrogate. Its precision is currently
overstated: 1,011 is the output of a deterministic chain whose inputs are uncertain, and one of those inputs
is known to be biased.

### The evidence
- **F10 / CL-31:** the per-kilometre sanity cap binds on **169 of 186 routes (90.9%)**. The cap, not the
  routing engine, is what sets cycle time on nine routes out of ten.
- **F10 / CL-32:** the cap sits **below observed real-world pace** — the observed median is 4.62 min/km across
  18 corridors. So the binding constraint is set tighter than reality, which biases cycle time downward and
  fleet downward.
- **F3 / CL-17:** planned one-way time is a median **0.51×** observed. Planned times are roughly half of what
  buses actually take.
- Engine version v3.4.5 already re-anchored **five** GPS-measured corridors and fleet rose 1,004 → 1,011. Five
  of 186. If the same correction applied network-wide, the fleet would be substantially higher.
- §8 already says fleet "is reported as an interval, not a point" — **but the interval does not exist yet**,
  because a09 has not run. That sentence is currently writing a cheque the pipeline has not cashed.

### The options
| Option | Consequence |
|---|---|
| **A. Report 1,011 as the point plan and an interval from a09 alongside it** | Honest and defensible. The plan number stays quotable for the RTO; the paper carries the uncertainty. |
| B. Point estimate only | A reviewer who reads F10 and F3 will ask why, and they will be right to. |
| C. Interval only | Loses the operational deliverable. The RTO needs a number to procure against. |

### My recommendation
**A.** And note your own instruction here — *"just do the best possible option which is correct and true"* —
which I read as authorising the headline to move when the modules land. **The Abstract will be updated when
a09 runs.** If 1,011 must stay fixed for an external commitment, tell me now.

### If you do nothing
I run a09, report both, and update the Abstract accordingly.

---

## D8 · Cost and emission constants

### The question
Module a14 needs a fuel price, a per-kilometre operating cost, and emission factors. You said you have no
local figures. Confirm published defaults are acceptable.

### Why it matters
It is the difference between a plan and a costed plan. A costed plan is what an authority can act on.

### The evidence
No local cost data exists in either repository. I checked.

### What I will use, with citation
- Per-kilometre operating cost, diesel and electric, from MoHUA / published Indian bus-operations sources.
- Emission factors from a published Indian or IPCC-default source.
- Every constant declared in `analysis/common.py` under `PARAMETERS`, with a cited source, and **swept in the
  sensitivity analysis** so that the conclusion does not depend on any single value.

### The honest caveat that will appear in the text
Costs computed from national defaults are indicative, not a budget. Kashmir's terrain, winter operations and
fuel logistics all push real costs above national averages, and the direction of that bias will be stated.

### If you do nothing
I proceed with cited published defaults, all swept. This is the answer you already gave — it is here so it is
on the record with the caveat attached.

---

## D9 · Building footprints for validation channel V1

### The question
Validation channel V1 cross-checks the WorldPop population surface against an independent settlement
indicator. Do we download the OSM building layer for the ten districts?

### Why it matters
V1 is the only check on the paper's *denominator*. Every coverage percentage divides by 6,584,762, and that
number comes from a **model**, not a count — one that already sits 4.4% below the 2011 Census for the same
districts (F2). An independent settlement layer tests whether WorldPop puts people where buildings are.

### The evidence
`data/raw/` has no building layer. I confirmed its absence rather than assuming it.

### The plan
Download OSM buildings for the ten districts, compute building density and footprint area per analysis unit,
correlate against WorldPop density, and report both the correlation and the spatial pattern of disagreement.
Open data, no licence obstacle, ODbL attribution as for all other OSM inputs.

### The caveat
OSM building completeness is uneven and is likely to be *worse* in exactly the peripheral districts where the
coverage gap is largest. A weak correlation there is ambiguous — it could be WorldPop error or OSM
incompleteness — and the text will say so rather than reading it one way.

### If you do nothing
I proceed. You already said "sure do whatever u can and want to do"; this entry records what that means
concretely.

---

## D10 · The τ and θ parameters

### The question
Network catchments use τ = 100 m (the perpendicular reach off the walk network) and consolidation uses
θ = 0.65 (the corridor-overlap threshold for merging). Are these the right defaults?

### Why it matters
τ drives the headline. The 37.4% median overstatement of Euclidean over network catchments is measured at
τ = 100 m. The parameter sweep (CL-29) shows the result is **highly sensitive** to it:

| τ | Median overstatement |
|---|---|
| 50 m | 52.8% |
| **100 m** | **37.4%** |
| 150 m | 29.2% |

A reviewer will ask why 100. The answer must be better than "it looked reasonable."

### The evidence and the argument for 100 m
- It is the reach from a pedestrian way to a doorway in a mapped street network — the gap OSM does not
  represent because footpaths and building entrances are not fully mapped.
- The whole sweep is reported, so the reader can see the sensitivity rather than having to trust the choice.
- Critically, the **direction of the finding does not change anywhere in the sweep**: Euclidean buffers
  overstate at every τ tested. Only the magnitude moves.
- θ = 0.65 is likewise swept across 0.5–0.9.

### The options
| Option | Consequence |
|---|---|
| **A. Keep 100 m, report the sweep, argue the direction is invariant** | Current draft. Defensible. |
| B. Re-anchor τ empirically | If the building-footprint layer from D9 lands, median distance from a building centroid to the nearest walk-network node is a *measured* τ for this region. Much stronger. |

### My recommendation
**A now, B if D9 delivers.** An empirically anchored τ would turn the paper's most exposed parameter into one
of its better-defended ones.

---

## D11 · The before/after Gini cannot be computed

### The question
Module a12 was designed to report an accessibility Gini before and after rationalisation. It **cannot** —
and it says so rather than inventing a counterfactual. How should the paper present this?

### Why it matters
"Did rationalisation make access more or less equal?" is the first equity question any reviewer asks. We
cannot answer it as a before/after pair, and pretending otherwise would be fabrication.

### The evidence
From `data/derived/a12_equity_gini.json`, verbatim:

> *The 458 merged permit records carry no routed line geometry on disk (the plan GeoJSON holds the 186 active
> features only), so a pre-consolidation accessibility surface cannot be built from real data. A before/after
> Gini pair is therefore not reported; only the after-state Gini and the concrete losers analysis are.*

What **is** computed, and is strong:
- Frequency-weighted accessibility **Gini = 0.903** across all residents.
- **75.8% of the division's population has zero scheduled service** within a 400 m network walk.
- Population-weighted mean of 3.58 scheduled departures per hour; **median 0.0** — the median resident has no
  service at all.
- **Conditional Gini = 0.599** among the 1,592,847 residents who *do* have service. This second number
  exists because a referee would otherwise point out — correctly — that a Gini of 0.90 is mostly just
  restating the 24% coverage share in a different unit. The conditional figure says something the headline
  cannot: **even among the served, service intensity is highly unequal.** Both are reported, with the
  distinction stated.
- A named **losers** analysis: 32 suppressed alternative via-routings across 20 corridors; the deduplicated
  union of their walksheds holds 114,879 residents, of whom **13,087 fall outside the plan's network catchment
  entirely** — those are people who lose bus access, not merely a preferred routing.

### The options
| Option | Consequence |
|---|---|
| **A. Report the after-state Gini + the named losers; state plainly why no before/after pair exists** | Honest, and the losers analysis is arguably *more* useful to a policymaker than a Gini delta, because it names 20 corridors and 13,087 people rather than moving a summary statistic. |
| B. Reconstruct a synthetic baseline from permit straight-line chords | Would produce a number. It would be a number about straight lines, not about bus routes. Not recommended. |
| C. Obtain baseline geometries from the engine | If the 458 merged rows can be re-routed through OSRM, a genuine before/after becomes possible. This is a real option, and it needs OSRM in Docker — the engine repo has it. Worth scoping. |

### My recommendation
**A now, C if someone can spare a run of the engine.** And note the framing: 13,087 identified residents
losing access is a stronger sentence than any Gini delta.

---

## D12 · The transfer analysis found losers, and they are real

### The question
Module a13 finds that consolidation makes a specific set of origin–destination pairs **worse off**. How
prominently does the paper report this?

### Why it matters
This is the paper's most self-critical finding. Reporting it prominently is the single most credibility-
enhancing move available — it demonstrates the analysis was not built to flatter the plan. Burying it is the
kind of thing a reviewer finds and then distrusts everything else.

### The evidence
From `data/derived/a13_transfers.json`:
- **88.75%** of suppressed permits' origin–destination pairs still have a one-seat ride in the plan (363 of
  409). That is the good news and it is genuinely good.
- **11.25% (46 pairs) now require a transfer.**
- For **all 46**, the break-even transfer penalty is **negative** (median −14.22 minutes). In plain terms:
  *the two waits in the plan already exceed the single wait in the permit baseline, so those passengers are
  worse off even if the transfer itself costs them nothing.*
- The module's own caveats, which the paper must carry: these are shares of **stop pairs, not trips** — no OD
  matrix exists, so no passenger weighting is possible, and the figure must never be quoted as a share of
  travellers. The wait model uses h/2, which the module notes inflates waits on **both** sides and makes the
  break-even magnitude an upper bound. The baseline assumes evenly-spaced permits, which independent operators
  do not achieve — so the true baseline wait was worse than modelled, and the reported break-even is a floor.

### The options
| Option | Consequence |
|---|---|
| **A. Report it in §5 and again in §7.8 limitations** | Costs nothing analytically and buys a great deal of credibility. It is also just true. |
| B. Report the 88.75% only | A reviewer who reads the released JSON — and they can, it is in the public repository — finds the other number. |

### My recommendation
**A**, and put the sentence in the Discussion in the authors' own voice: consolidation has identifiable
losers, we have named them, and here is the corridor list.

---

## D18 · The objective classification disagrees with the deployed plan's own priority bands

### The question
Module a04's Jenks classification of the composite index agrees with the plan's published HP/MP/LP priority
bands only **68.3% of the time (κ = 0.503)**. How does the paper handle that?

### Why it matters
A reader's natural assumption is that the paper's method reproduces the plan the engine actually produced. It
does not — not exactly. Twenty routes the deployed plan treats as high-priority fall into objective Tier 3.
Left unaddressed, a reviewer finds this in the released data and asks why the paper's own classifier
disagrees with the plan the paper is about.

### The evidence
From `data/derived/a04_class_count.json` and `paper/tables/table05*`:
- k = 3 is selected independently by **both** pre-declared rules — first GVF above 0.80, and the largest
  second difference in the GVF curve. The second rule picks k = 3 by an order of magnitude over the runner-up.
  No tie-break was needed and no post-hoc choice was made.
- Jenks and k-means partition the 186 routes **identically** (κ = 1.000). Two independent
  variance-minimising criteria agreeing exactly is strong evidence the three-tier structure is in the data.
- Quantile classification disagrees badly (κ = 0.427) precisely *because* it forces 62/62/62 and cuts through
  the middle of the natural low band. That is the expected behaviour of an uninformative classifier, and it
  is reassuring rather than worrying.
- Against the plan's published bands: 68.3%, κ = 0.503. Moderate agreement.

### Why I think the disagreement is honest and worth reporting
The deployed plan's bands were **not** set by Jenks on the composite index. They reflect operational
judgement, the SSCL backbone's fixed design headway, and the rural-lifeline policy floor — real constraints
that a pure index classification does not see. Moderate agreement is roughly what one should expect between a
policy-constrained banding and an unconstrained statistical one, and reporting it is more informative than
either hiding it or forcing them to match.

### The options
| Option | Consequence |
|---|---|
| **A. Report the 68.3% / κ = 0.503 explicitly and explain the divergence** | Honest, and it actually strengthens §4 — it shows the method is an independent classifier rather than a post-hoc rationalisation of a plan that already existed. |
| B. Report only the internal comparisons (Jenks vs k-means vs quantile) | The internal numbers look excellent and the external one is absent. A reader who checks the released data will notice what is missing. |
| C. Re-band the plan to match the classifier | Changes the operational plan to fit the paper. Exactly backwards. |

### My recommendation
**A.** The sentence to build it around: the classification is a method applied to an index, not a
reconstruction of decisions already taken, and where it diverges from the deployed banding the divergence is
attributable to operational constraints the index does not encode.

---

## D19 · A boundary-convention inconsistency between two modules

### The question
Module `a03_index_weights` and module `a04_class_count` interpret Jenks break values with opposite
conventions. Do we fix a03 to match a04?

### Why it matters
It is small, it is real, and it is exactly the kind of thing that is embarrassing to have pointed out by a
reviewer who has the code — which they will, because the repository is public.

### The evidence
`jenkspy.jenks_breaks` returns interior breaks that are observed data values marking each class's **upper**
bound. `common.goodness_of_variance_fit` reads a break list as half-open `[lo, hi)` — i.e. as **lower**
bounds. Feeding one directly to the other evaluates a partition shifted by one route at every boundary.

This bug was present in a04's first implementation, was caught by its own self-check — k-means appeared to
beat "optimal" Jenks on Jenks's own objective, which is impossible — and was fixed. An exact Fisher (1958)
dynamic program was added as a permanent regression check and confirms `jenkspy` attains the true global
optimum at every k tested, for all three weighting schemes, to within 1.1 × 10⁻¹⁵.

**a04 is correct.** `a03_index_weights.jenks_bands` still uses the other convention, so its `band_*` labels
differ from a04's `tier_class` at class boundaries. a03's own stability diagnostics compare band to band, so
both sides are shifted alike and **its kappas remain valid** — the inconsistency does not invalidate any
published a03 number. But the two modules disagree about which tier a boundary route belongs to.

### The options
| Option | Consequence |
|---|---|
| **A. Fix a03 to the a04 convention and re-run** | The two modules agree. a03's stability kappas will move slightly. Any figure or table already drawn from a03 bands must be regenerated — none has been. |
| B. Leave a03 and document the difference | Defensible, since a03's conclusions are unaffected, but it leaves two definitions of "tier" in one repository. |

### My recommendation
**A**, and it should be done before any figure is drawn from a03's bands. I did not do it unilaterally
because a03 is an already-executed module whose outputs other modules consume, and silently changing a
published intermediate is the kind of thing that ought to be a recorded decision rather than a quiet commit.

### If you do nothing
I will fix a03 to match a04 and re-run, since a04 is demonstrably the correct convention and the fix makes
the repository self-consistent. Say so if you would rather I did not.

---

# Part C — Authorship and journal mechanics

---

## D13 · Author list, affiliations, corresponding author, CRediT

### The question
Who are the authors, in what order, with what affiliations, who corresponds, and what did each contribute?

### Status
**Deferred at your request.** Not started. No placeholder names have been invented and none will be.

### What is needed eventually
- Full author list **in final order** — order disputes after submission are painful and common.
- Each author's institutional affiliation and email.
- One corresponding author with a stable email.
- ORCID iDs where available (*Transport Policy* asks).
- **CRediT taxonomy roles** per author. Elsevier requires this. The fourteen roles are: conceptualisation ·
  methodology · software · validation · formal analysis · investigation · resources · data curation · writing
  – original draft · writing – review & editing · visualisation · supervision · project administration ·
  funding acquisition.
- A competing-interests statement (usually "none declared").
- A funding statement (or an explicit "no funding received").

### One observation, offered once and then dropped
The section-ownership table implies specific contributions, and the repository records who wrote what. If it
would help, I can draft a CRediT matrix from that record for you to correct — it is easier to edit a wrong
draft than to fill a blank table. Say the word.

### If you do nothing
The manuscript has no author block. It cannot be submitted, but nothing else is blocked, and this is
legitimately a late-stage task.

---

## D14 · Figures — which eight, and who draws them

### The question
The design calls for eight figures plus F8b. **Zero exist.** Which are essential, and who produces them?

### The specification as it stands
| # | Figure | Depends on | State |
|---|---|---|---|
| 1 | Conceptual framework — the demand-free chain | Nothing | Drawable today |
| 2 | Taxonomy of planning methods by data intensity, gap region shaded | Table 1 coding (D5) | Blocked |
| 3 | Study area, four panels: boundary · population density · road hierarchy · opportunity density | Staged data | Buildable today |
| 4 | Method flowchart / Algorithm 1 | Nothing | Drawable today |
| 5 | Permit → corridor → route funnel | q01, executed | Buildable today |
| 6 | Euclidean vs network catchment, side by side on one route + the distribution of overstatement | a02, executed | Buildable today |
| 7 | Service tiers mapped, with the Jenks breaks | a03 + a04, executed | Buildable today |
| 8 | Coverage and the uncovered-population surface | a11, executed | Buildable today |
| 8b | Sobol' indices / tornado | a09 | Blocked |

Six of nine are unblocked right now. All must be ≥300 DPI, legible in greyscale, with no text smaller than
about 7 pt at final size.

### My recommendation
I generate the six unblocked ones as drafts; Misti and Prashant review for cartographic quality. Figure 1 and
Figure 4 are conceptual and might be better hand-drawn — a well-made conceptual diagram is worth a great deal
in a policy journal and is one of the few places where a human draws better than a script.

---

## D15 · The draft is ~11,900 words against a 9,000–10,000 target

### The question
Where do roughly 2,000 words come out?

### The evidence, measured from the files at build time (prose only — headings, tables, code and editorial
callouts excluded)

| Section | Words | Target | Over/under |
|---|---|---|---|
| Abstract | 249 | 230 | +19 |
| §1 Introduction | 2,343 | 1,200 | **+1,143** |
| §2 Literature | 1,413 | 1,400 | +13 |
| §3 Study area | 1,242 | 1,100 | +142 |
| §4 Methodology | 2,467 | 2,300 | +167 |
| §5 Results | 1,151 | 2,400 | **−1,249** |
| §6 Validation | 956 | 900 | +56 |
| §7 Discussion | 1,678 | 1,200 | +478 |
| §8 Conclusions | 421 | 400 | +21 |
| **Total** | **11,920** | **9,000–10,000** | **+1,920** |

Two of those rows matter and the rest are noise.

**§1 is 1,143 words over, and essentially all of it is the "Policy Failure" block** (~900 words). That block is
good — it is the most concrete institutional writing in the paper, it names real corridors and real permit
counts, and it should absolutely stay in the manuscript. But it is *study-area* material, not *introduction*
material. Moving it to §3.3 fixes §1's budget and §3's thinness in one operation, and changes not a word of
its text. **That is a decision for its author, and I have not made it** (FLAG PF-a, FLAG 3-B).

**§5 is 1,249 words under**, and that gap will close on its own as the remaining modules land — a10, a11, a12
and a13 have all completed since this draft was assembled and none of their results are written up yet.
Realistically §5 grows past its 2,400 target, not toward it.

**Net effect if the block moves and §5 fills out:** roughly 12,000–12,500 words, which is over. The remaining
cut has to come from §7 and from tightening throughout. Alternatively — and this is common — *Transport
Policy* will accept a longer paper if the content justifies it; the 9,000–10,000 figure is guidance, not a
hard limit.

### My recommendation
Move the Policy Failure block to §3.3 (its author decides), write up §5 fully, then do one tightening pass
across the whole manuscript rather than pre-emptively trimming sections that are still being written.

---

## D16 · What exactly goes in the public repository

### The question
The data-availability statement has to be specific. What is actually released?

### The current position
| Asset | State | Note |
|---|---|---|
| All analysis code | Released, GPL-3.0 | `analysis/`, `tests/` |
| Derived results (JSON, CSV, tables) | Released | `data/derived/`, `paper/tables/` |
| Population raster | **Excluded** (size) | Retrieval instructions + SHA-256 in `data/MANIFEST.md` |
| Cached walk graph | **Excluded** (size) | Rebuildable from OSM; hash recorded |
| Permit register | To be confirmed | Is the digitised register releasable? It came from the RTO. |
| **GPS traces** | **Must not be released as individual traces** | See D4. Aggregates only. |
| OSM / WorldPop inputs | Released by reference | ODbL and CC BY 4.0 respectively |

### The one question only you can answer
**Is the digitised permit register releasable?** It originates with the RTO. If it is not, the paper must say
so and offer the derived corridor-level aggregates instead — which is fine, and common, but it has to be
stated rather than left ambiguous.

### The claim that must stay scoped
The repository currently says *"all analysis code … is released"*, which is true. It deliberately does **not**
say *"fully reproducible pipeline"*, which would not be while several modules remain unwritten. When they
land, the wording strengthens — and not before (FLAG 3-E).

---

## D17 · Confirm the journal

### The question
Is *Transport Policy* still the target?

### Why it is worth thirty seconds
Everything — length, section structure, the policy-forward framing of §7, the citation style — is built for
it. If the target changes to, say, *Case Studies on Transport Policy*, *Journal of Transport Geography* or
*Transportation Research Part A*, the framing shifts and some of the structure with it. Cheap to confirm now,
expensive to discover late.

### My assumption
*Transport Policy* (Elsevier), 9,000–10,000 words, eight figures, eight tables. Everything is built on it.

---

# Part D — Every editorial flag, in one table

These are the callouts embedded in the manuscript draft. The five blockers above are the escalated ones; the
rest are here so nothing is lost. Each resolves to a tinted box in
`paper/Kashmir_Manuscript_Working_Draft.pdf`.

| Flag | Section | What it says | Owner |
|---|---|---|---|
| 1.1-a | §1.1 | Five quantitative claims need page-level citations: the 490→763 M urban projection; 0.13–0.14 buses/1,000; the MoHUA 0.44 benchmark; ">400 Class-I cities with no organised bus network"; "<15 agencies publish GTFS". Highest-yield paragraph in the paper for a reviewer to fact-check, because every number is externally verifiable. | Misti, Avny |
| 1.1-b | §1.1 | "as per CSE & CITIES Forum, 2026; MoHUA, 2014; Pucher et al., 2007" should be parenthetical in Elsevier style. Also "CSE & CITIES Forum" and "CSE-CITIES Forum" appear as two strings for one source. | Misti, Avny |
| 1.2-a | §1.2 | **Disclosed repair.** A page break had split "US$ 40 Million per km, compared to US$ / 2.5 Million per km" mid-number. I rejoined it. No other wording changed. | Disclosure only |
| 1.2-b | §1.2 | The US$ 40 M/km metro and US$ 2.5 M/km BRT figures need a year and a currency base. | Misti, Avny |
| 1.3-a | §1.3 | A `<formula>` placeholder for the frequency rule did not survive PDF extraction. The implied form is *f = Q_max / (C · LF_target)*. **I did not insert it** — the co-authors must supply their own. | Misti, Avny |
| 1.3-b | §1.3 | This is the load-bearing subsection: the whole paper's wedge depends on establishing that demand enters the chain at exactly one point. Worth the most care of any paragraph in §1. | Misti, Avny |
| 1.4-a | §1.4 | **Good news flag.** This paragraph is already correctly on the locked ten-district framing. Nothing to fix; noted so nobody "corrects" it. | — |
| 1.4-b | §1.4 | "64.5% female ridership" and "2.5 million tourists" carry no source and no claim ID. | Misti, Avny |
| 1.4-c | §1.4 | Attachment guidance for this subsection not yet fully followed. | Misti, Avny |
| 1.5-a | §1.5 | Contribution (4) is exactly right and should be protected in editing. | — |
| 1.5-b | §1.5 | Objective O5's wording promises more than §6 can deliver. §6 can claim decision-robustness, not demand validation. Align the wording or the paper contradicts itself. | Misti, Avny + Prashant |
| 1.5-c | §1.5 | Contribution (3) says "novel … seasonal considerate demand-proxy". The seasonal element is **not** modelled — the tourist multiplier is a static 1.3× on eight routes. Either the claim narrows or the modelling has to appear. | Misti, Avny |
| 1.6-a | §1.6 | **Decision 1.** Six-section roadmap in an eight-section paper. | Misti, Avny |
| PF-a | Policy Failure block | The block belongs in §3.3, not §1 — it alone puts §1 ~900 words over budget. **Not moved.** | Its author |
| PF-b | Policy Failure block | **Decision 3.** "the area falling within the limits of the SMC" conflicts with the division-wide plan. | Its author |
| PF-c | Policy Failure block | The named overlapping corridors are checkable and worth keeping — they are the most concrete evidence in §1. | — |
| 2-A | §2.1 | **Decision 5.** Protocol not run. | Sharvesh, Ankit |
| 2-B | §2.4 | The Euclidean-vs-network critique is **not novel**. Gutiérrez & García-Palomares (2008) and Biba et al. (2010) must be cited by name, in the body, before §4 makes its measurement. Presenting the 37.4% as a discovery is the fastest route to a hostile review. | Sharvesh, Ankit |
| 2-C | §2.8 | The data-intensity cross-tabulation is stated as an *expectation*, deliberately, because the coding has not been done. If the coding contradicts it, report what it shows. | Sharvesh, Ankit |
| 2-D | §2 | Every citation must reconcile against `paper/references.bib` with a verified DOI before circulation. Two to check specifically: the Digital Matatus reference and MoHUA (2014)'s exact title and year. | Sharvesh, Ankit |
| 3-A | §3.1 | **The one heading I changed.** "The SMR as a critical case" → "Kashmir Division as a critical case". Reverting is one word. | Krishna |
| 3-B | §3.3 | Placement of the Policy Failure block. Pairs with PF-a. | Krishna + its author |
| 3-C | §3.4 | Table 2 rows for Master Plan land use, terrain, water bodies, tourist arrivals, fleet register and cost norms reference data **the study does not hold**. Obtain them or strike the rows. They must not appear as inventory for data we do not have. | Krishna |
| 3-D | §3.6 | **Decision 4.** GPS ethics. | Prashant |
| 3-E | §3.6 | Reproducibility claim scoped to "all analysis code is released" and deliberately not "fully reproducible pipeline". | Prashant |
| 7-A | §7.2 | The political-feasibility paragraph is missing. 458 merged permit rows are 458 contested livelihoods; the international redesign-resistance literature (Houston, Auckland, Barcelona, Santiago) must be cited. **Required, not optional.** | Ankit, Avny |
| 7-B | §7.5 | **Decision 6.** Ladder cannot be ranked until a09 runs. | Prashant |
| 7-C | §7.6 | "Applies to 400+ cities" is a claim about *preconditions being met*, not demonstrated external validity. The sentence must not read the other way. | Ankit, Avny |
| 7-D | §7.7 | The 30%-of-funding sequencing analysis has not been run. The attachment calls it "small analysis, large payoff" and it is right — it speaks directly to the commissioning authority's actual decision. | Prashant |
| 7-E | §7 | The co-author "Policy Contribution" block overlaps §7.1–§7.2 and uses Srinagar scope. Neither reconciled; both proposed. My view: keep the block's voice, it is pitched exactly right for this journal. | Ankit, Avny, Misti |

---

# Part E — Decisions I took on your behalf

You asked me to work without waiting for input. These are the calls I made. Each is reversible; each is here
so you can reverse it.

| # | Decision taken | Reasoning | How to reverse |
|---|---|---|---|
| E1 | Adopted the eight-section structure | Your instruction was "do as told in the pdf". The PDF's *operative* structure — the ownership and word-budget table — is eight sections. Only one stray sentence in §1.6 says six. | Tell me; I renumber everything. |
| E2 | Transcribed all co-author prose verbatim and raised every conflict as a callout instead of editing | Your instruction: "dont change or remove things they have already written." | n/a — this is the instruction. |
| E3 | Changed one heading: "The SMR as a critical case" → "Kashmir Division as a critical case" | A barred scope in a section heading propagates into the table of contents. Disclosed at the point of change (FLAG 3-A). | One word. |
| E4 | Left the §3.6 ethics paragraph blank | Writing a plausible-sounding ethics statement I cannot verify would be worse than leaving a gap. | Answer D4. |
| E5 | Wrote §2.1 as a template with visible placeholders | Inventing database names and corpus sizes is misconduct. Visible placeholders cannot be mistaken for results. | Answer D5. |
| E6 | Did not import any number from the §6 field-observation table | No data file, no method note, no claim ID. | Answer D2. |
| E7 | Did not insert the frequency-rule equation into §1.3 | The placeholder was lost in extraction; I do not know which form the author intended. | Author supplies it. |
| E8 | Reported a12's before/after Gini as NOT_COMPUTABLE rather than reconstructing a baseline | The merged permits have no geometry. A synthetic baseline would be a number about straight lines. | Answer D11 option C. |
| E9 | Reported a10's baseline unique-network-km as NOT_COMPUTABLE with explicit bounds (1,524 km ≤ x ≤ 13,756 km) | Same reason: the 458 merged rows have attributes but no geometry in the published release. | Re-run the engine with OSRM up. |
| E10 | Kept the tourist multiplier as a static 1.3× and did **not** model seasonality | The plan gives year-round recommended sizes; seasonal modelling was deliberately out of scope. But §1.5 currently claims a "seasonal considerate" proxy — that claim and this decision contradict each other (FLAG 1.5-c). | Either narrow the claim or commission the modelling. |
| E11 | Did not sum per-route walkshed populations anywhere | They overlap. Only the deduplicated union is a network total. This is enforced in code and in tests. | n/a — this is arithmetic, not preference. |
| E12 | Left author block, affiliations and CRediT entirely absent | Deferred at your request; inventing placeholders risks one surviving into a submission. | Answer D13. |

---

# Part F — What is running, and what will move

So that no number surprises you.

### Modules complete as of this document
`q01_data_quality` · `a00_stage_inputs` · `a01_build_walk_graph` · `a02_network_catchments` ·
`a02b_faithfulness` · `a03_index_weights` · `a04_class_count` · `a05_headway_timeofday` ·
`a10_network_diagnostics` · `a11_coverage_accessibility` · `a12_equity_gini` · `a13_transfers` ·
`v04_gps_validation`

### Results that landed after the current §5 draft was written, and are therefore not yet written up
- **a04:** Jenks at k = 3 gives a goodness-of-variance-fit of **0.9023**, and k = 3 is selected independently by
  both pre-declared rules (first GVF > 0.80, and the largest second difference — the latter by an order of
  magnitude). Jenks and k-means agree **exactly** (κ = 1.000, 100% of routes) while quantile classification
  does not (κ = 0.427, 61.8%). The three-tier hierarchy is a property of the data, not of the classifier —
  with the important caveat that quantile is the odd one out because it forces equal class sizes (62/62/62)
  and splits the natural low band down its middle. Objective tiers are **37 / 41 / 108**.
- **a04, and this one is uncomfortable:** the objective classification agrees with the **published** plan's
  own HP/MP/LP priority bands only **68.3% of the time (κ = 0.503)**. Twenty routes the plan calls
  high-priority fall into objective Tier 3. This is a finding, not a defect — the paper's classification is
  *not* a reproduction of the deployed plan's banding — but §5 has to say so plainly rather than letting a
  reader assume the two agree.
- **a10:** 5,568 route-km lie on **1,524 unique network-km** — a **3.65× duplication ratio**, measured two
  independent ways that agree to four decimal places. One 88-metre link near Lal Chowk carries **53 of the
  186 routes**. 46.6% of network kilometres are served by exactly one route; 8.4% carry ten or more.
- **a11:** any-service coverage recomputes to **24.19%**, reconciling with the established 24.2% headline to
  within 0.01 percentage points. Frequent-network coverage is far lower: **10.4%** at a 15-minute headway,
  12.2% at 20 minutes, 19.2% at 35 minutes. Most of the reached population has infrequent access.
- **a11 (Moran's I):** the uncovered-population surface returns **I = 0.664, p = 0.001** — the unserved are
  strongly spatially clustered, not scattered. That makes the gap addressable by a finite set of corridors,
  which is a policy-actionable finding rather than a diagnosis of general shortfall.
- **a12:** frequency-weighted accessibility **Gini 0.903**; **75.8%** of residents have no service; the
  median resident has **zero** departures per hour.
- **a13:** 88.75% of suppressed permits' OD pairs keep a one-seat ride; 46 pairs do not, and all 46 are worse
  off even with a zero-cost transfer.

### Still to run
`a06_deadhead` · `a07_load_factor` · `a08_sensitivity_oat` · **`a09_monte_carlo_sobol`** ·
`a14_cost_emissions` · `a15_scenarios` · `v01_spatial_crossval` · `v02_benchmark` · `fig_generate_all`

`a09` is the important one: it produces the fleet interval (D7), the Sobol' ranking for the data-maturity
ladder (D6), and validation channels V5 and V6 — three deliverables from one module.

### Headline numbers that may move
Per your instruction — *"just do the best possible option which is correct and true"* — the following are
**not** frozen and will be updated if the modules say otherwise: the fleet figure (1,011 → likely an
interval); the frequent-network coverage figures, now computed and lower than the any-service headline; and
anything in the Abstract that depends on either.

### Numbers that are locked and are not moving
614 permits · 157 corridors · 644 engine rows · 186 active routes · 6,584,762 study population · the 37.4%
median catchment overstatement · 24.2% division coverage · the 99.4% corridor-retention decomposition.

### Barred framings
342 permits · 207 routes · 39% reduction · 95.7% coverage · ~1,009 fleet · any Srinagar-metropolitan
denominator · any claim of "validated against ridership". If you see these in a draft, that draft predates the
current baseline.

---

## The shortest possible version

If you only have ten minutes, answer these four:

1. **D4 — GPS ethics.** Nobody but you can answer it and it gates submission.
2. **D2 — the field-observation table.** Is it real, and can we get the sheets?
3. **D3 — scope.** One sentence from the author of the Policy Failure block resolves it.
4. **D5 — the literature protocol.** Run it, or drop it. Either is fine; the current state is not.

D1 is a one-paragraph fix whose replacement text is already drafted. Everything else can wait for the modules.

---

# Part G — Update, 2026-09-30

Everything in this part was checked against the repository on the date above. It supersedes the status
lines of D7, D9, D14, D15 and D19 earlier in this document; the original entries are kept for the record.

## Resolved without you (reversible)

| # | What happened | How to reverse |
|---|---|---|
| D9 | **No download needed.** Buildings were extracted from the local OSM India file already used for the walk graph (`E:/kash/india-latest.osm.pbf`). V1 ran: route-scale ρ = 0.657 on footprint area (pass), 0.544 on count (fail); 1 km grid 0.316 (fail) because only 4–31% of populated cells contain any mapped building. That file looks partially filtered (847,866 buildings for all of India). A full OSM or Microsoft/Google footprint layer would strengthen V1, but it is a large external download and needs your go-ahead. | Say "download footprints" and name the source. |
| D19 | a03 now uses a04's Jenks convention and was re-run. Only a03's band-agreement statistics moved, by ≤0.02 κ, and none of them is quoted in the prose. | Revert `a03_index_weights.py:120`. |
| D14 | Figures 1, 3, 4, 5, 6, 7, 8 and S1 (trade-off frontier) are drawn by `analysis/fig_generate_all.py` at 300 dpi + vector PDF. Figures 9/9b are drawn once a09 runs. Figure 2 (review flow) waits on D5. | Replace any figure; the script is the single source. |
| D15 | Prashant's §4 was cut from 2,758 to 2,422 words. Co-author cuts are *proposed*, not applied, in `paper/WORD_BUDGET_PLAN.md`. | — |

## New decisions raised by today's modules

### D20 · The published method misdescribed the engine in four places — confirm the corrections
Checked line by line against `transit_kashmir_v3.py`: (a) the capture scale is κ = 0.33, not 0.18;
(b) Eq. 8 does set headways on the 67 non-backbone rural routes (5 at 35 min, 62 at 50 min), so
"demand never sizes the fleet" was false; (c) the merge test also requires start points within 2.5 km,
uses 80 m line buffers, and merges only into a cluster's leading trunk; (d) the backbone fleet is
max(formula, CHALO deployment), which binds on 2 of 30 routes. §4 now says all four (CL-59).
**Recommendation:** keep the corrections — a reviewer with the public code would find them.

### D21 · The MoHUA benchmark sentence
The engine's "43 buses per lakh served, inside the MoHUA 40–60 band" divides by the Euclidean served
population this paper shows is overstated. On the network walkshed it is **63.5 per lakh, above the band**
(15.4 on the whole division). §4.8 and §5.4 now report all three (CL-60). **Recommendation:** keep;
say which denominator the RTO deck uses before it is quoted externally.

### D22 · V2 fails — how to present it
The plan's backbone fleet (283) is 1.29–1.58× CHALO's 98 buses scaled to 15 minutes, under every
service-day assumption; route-level rank agreement is weak (ρ = 0.22). §6.2 reports this as a fail.
**Recommendation:** report as a fail. The pre-registered ±15% band cannot be widened after the fact.

### D23 · GPS collection window conflict (feeds D4)
`DATA_AVAILABILITY.md` says June–July 2026; the ledger (CL-18) and the driver-day file say
February–June 2026. The ethics statement must use the true window.

### D24 · Load and ridership framing
On day one the planned backbone carries ~8 boardings per trip against 19–37 today; ridership must grow
2.2–4.5× to hold today's loads (CL-50). §5.11 frames the plan as a supply-led bet and recommends staged
procurement. **Recommendation:** keep — it is the honest reading and a defensible policy recommendation.

### D25 · Cost and emissions stay provisional
a14 carries every constant as a range with `verified = false` (Table 5m-constants). Nothing from it is in
the Abstract. The engine's own e-bus emission factor (30 g CO₂/km) is about 29× too low and is not used.
This is D8; it now has concrete constants to confirm.

## D7 and D6 — now answerable with numbers (a08/a09 ran 2026-09-30)

**D7 · Fleet as a point or an interval.** The Monte Carlo gives 989–1,058 buses (median 1,013) as the
engine specifies, and **1,130–1,266 (median 1,182)** when urban and peri-urban run times follow observed
GPS pace; the published 1,011 lies below the whole observation-anchored interval (CL-56). The Abstract,
§5.7, §6.2 V6, §8, the highlights and the cover letter now say this. **Recommendation stands (option A):**
keep 1,011 as the plan's own figure and report the observation-anchored range as what to procure against.
If the RTO needs one number, 1,182 is the median at observed pace.

**D6 · Data-maturity ladder by variance reduction.** Written into §7.5 from the Sobol' indices (CL-58):
vehicle-availability records first (spare ratio 55 % of fleet variance), then peri-urban GPS (32 %), then
demand-side weights for the tiers (93 % of tier variance). Coverage is a walk-radius definition (97 %),
which no dataset resolves.
