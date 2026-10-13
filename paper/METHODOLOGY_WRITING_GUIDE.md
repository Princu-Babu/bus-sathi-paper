# Writing Section 4 (Methodology) by hand: a guide for Prashant

Prepared 14 October 2026. For the lead author, who is writing Section 4 himself, without AI, and has not
written a research paper before.

## How to use this document

This guide tells you what each part of Section 4 must contain, in what order, with which numbers and
equations, and what to leave out. It gives no finished sentences, on purpose: the sentences are yours.
Where it lists content, it is in note form.

Read Parts 1 to 3 once. Then write one subsection at a time using its card in Part 4. Part 5 covers the
passenger survey. Part 6 is the checklist to run before you send the section to anyone.

The existing `paper/sections/04_methodology.md` was drafted with AI. Do not write with it open. Write your
own draft first, then use the old one only to check that you have not dropped a fact or an equation.

Every number in this guide comes from the module outputs as they stood on 8 October. Before you finalise,
check each number you used against `paper/CLAIM_LEDGER.md`.

## Part 1 — what a methodology section is for

A methodology section answers three questions for a reader who was not there.

1. **What exactly did you do?** In enough detail that a competent stranger with the same data could repeat
   it and get the same answer.
2. **Why did you do it that way?** Each choice needs a reason: a published source, a constraint, or a plain
   statement that it is an assumption.
3. **What can this method not tell us?** Stated by you, before the reviewer states it for you.

It does not report what you found. "Coverage is 24.2 %" is a result and belongs in Section 5. "Coverage is
the share of residents inside the union of catchments" is method and belongs here. The test: if the sentence
would change when the data changed, it is a result.

Three exceptions are normal and you will use them:

- Counts that describe the inputs (614 permits, 2,431 destinations) belong in the methodology.
- A number that explains why a method step exists may appear once (for example, that the cap binds on 169
  routes, because that is why you size the fleet a second way).
- Parameter values are method.

**Who you are writing for.** A transport researcher who knows what a headway and a catchment are, has never
heard of Kashmir's permit system, and has not seen your code. Prof. Kathuria's brief says the section "must
be reproducible from the text alone". Write for that person.

## Part 2 — before you write a sentence

### Have these open

| Document | Use |
|---|---|
| `paper/PARAMETERS_AND_DEFENSIBILITY.md` | Every parameter value, its source and its grade. This becomes Table 3 |
| `paper/CLAIM_LEDGER.md` | The authoritative value of every number |
| Prof. Kathuria's brief, Section 4 | The ten subsection titles and the 2,300-word target |
| Figure 4 (framework flowchart) | You will describe the method in the order the figure shows it |
| The symbol list in Part 3 of this guide | So one symbol means one thing throughout |

### Work in four passes

1. **Skeleton.** For each subsection write three to six bullet points in your own words: what was done, with
   what, and why. No sentences yet. Half a page for the whole section.
2. **Equations.** Write out all the equations and define every symbol. If you cannot define a symbol in a
   few words, you do not yet understand that step well enough to write about it. Go and read the code.
3. **Prose.** Turn each bullet into one or two sentences. Do not polish.
4. **Cut.** You will be over the word target. Remove anything that is a result, anything said twice, and any
   detail that belongs in a table or the supplement.

Write the easy subsections first (4.3, 4.6, 4.8 are mechanical). Leave 4.1 for last: an overview is easy to
write once the rest exists.

### Word budget

The brief allows 2,300 words. A workable split:

| Subsection | Words |
|---|---|
| 4.1 Framework overview | 200 |
| 4.2 Data conditioning and network construction | 320 |
| 4.3 Route catchment delineation | 250 |
| 4.4 Weighted opportunity accessibility | 180 |
| 4.5 Composite demand index | 300 |
| 4.6 Permit consolidation | 220 |
| 4.7 Hierarchy and service standards | 220 |
| 4.8 Cycle time and fleet sizing | 320 |
| 4.9 Quality assurance gates | 100 |
| 4.10 Sensitivity and uncertainty | 190 |

Equations, the algorithm box, tables and figure captions do not usually count as words. They are how you
stay inside the budget: a table of twenty parameters costs nothing, the same content as prose costs 400 words.

## Part 3 — how to write it

### The pattern for one method step

Almost every paragraph in a methodology section has the same five parts. Not every paragraph needs all five,
but the order does not change.

1. **Purpose.** What this step is for, in one clause.
2. **Procedure.** What was done, in the order it was done.
3. **Values.** The parameter values, with units.
4. **Reason.** Why this procedure and these values: a citation, a constraint, or "assumption".
5. **Limit or pointer.** What the step cannot do, or where its effect is tested (a later subsection).

If a paragraph you have written has no part 4, it is the paragraph a reviewer will mark.

### Tense and voice

- **Past tense** for what you did to the data: sampled, snapped, merged, computed.
- **Present tense** for definitions and for what an equation states: "the catchment is", "Eq. 3 shares".
- **"We"** is accepted in this journal and is clearer than the passive. Use it for choices ("we adopt",
  "we report"). Do not use it in every sentence.
- One tense per sentence.

### Equations

- Introduce each equation with a sentence that says what it computes, then give the equation, then define
  every symbol that has not appeared before. Give units.
- Number every equation, on the right, in order. Refer to them as "Eq. 3".
- A symbol keeps one meaning in the whole paper. Never reuse a letter.
- Do not write an equation for something a sentence says just as well. Keep the ones a reader would need in
  order to compute the quantity.
- After an equation, say what follows from it only if that is not obvious.

### Symbols to use throughout

Keep these exactly, so Sections 5 and 6 match.

| Symbol | Meaning | Unit |
|---|---|---|
| Ω | Study region: union of the ten districts | — |
| ρ_c , x_c | Residents in raster cell c; its centre | persons; coordinates |
| G = (V, E) | Walking network: nodes and edges | — |
| r, l(r) | A route; its length (script l in the paper) | —; km |
| d(v) | Walking distance from node v to the nearest stop | m |
| W | Walking budget | m (400) |
| τ | Off-network tolerance | m (100) |
| A_net(r), Π(r) | Catchment of a route; residents in it | area; persons |
| n_c , π_c(r) | Number of routes covering cell c; residents of c allocated to route r | —; persons |
| α_t | Weight of a destination of tier t | — (1.00, 0.40, 0.60) |
| O(r), O*(r), μ | Opportunity score; after tourist multiplier; the multiplier | —; —; 1.30 |
| β, CDI(r) | Weight on population; composite index | 0.50; 0 to 1 |
| κ, m | Scale and mode share in the ridership estimate | 0.33; share |
| S(r), φ, θ | Line buffer; overlap ratio; merge threshold | 80 m; —; 0.65 |
| k, GVF(k) | Number of classes; fit statistic | —; 0 to 1 |
| χ, J, δ, Δ | Congestion factor; river delay; dwell per stop; stop spacing | —; min; min; m |
| λ, ω | Layover factor; cap on cycle time per km | 1.10; min/km |
| h(r), σ | Headway; spare factor | min; 1.15 |
| N_op , N, N_emp | Buses in service; with spares; operator's deployed fleet | buses |

### Citations

You need a citation in three situations and only these:

1. You use someone else's method (Jenks breaks, Sobol' indices, entropy weights).
2. You use someone else's data (WorldPop, OpenStreetMap).
3. You take a value from a published standard (walking distance, layover).

One good citation per item is enough. Never cite a source you have not opened. The parameter register marks
which sources have been checked and which have not. If a value has no source, write that it is an assumption.
That is acceptable; a wrong citation is not.

### Tables, figure and algorithm

- **Figure 4** (the flowchart) is cited in the first paragraph of 4.1. The text follows its order.
- **Table 3** is the parameter table: symbol, meaning, value, tested range, source. Build it from the
  parameter register. The text then gives a value once and points to the table for the rest.
- **Algorithm 1** (consolidation) is a numbered list of five steps in a box. Steps start with a verb.
  Inputs and outputs are named at the top and bottom.
- Cite every table and figure in the text before it appears.

### Words and habits to avoid

| Avoid | Why | Instead |
|---|---|---|
| "validated", "validation against demand" | Nothing in this paper is validated against demand | "checked against", "compared with" |
| "demand-free", "no demand data" | The e-bus data enters at five points | "no observed demand for the routes being planned" |
| "optimal", "optimised" | Nothing is optimised | "selected", "assigned" |
| "robust" without an object | Robust to what? | Name the variation it survives |
| "novel", "rigorous", "comprehensive", "state of the art" | Praise is the reviewer's to give | Delete |
| "it is clear that", "obviously", "of course" | If it were, you would not write it | Delete |
| "significant" for "large" | It means a statistical test was run | "large", "substantial" |
| "pre-registered", "fixed in advance" | The thresholds were written with the results | "stated in the analysis code" |
| "ensures", "guarantees" | Rarely true | "limits", "is intended to" |
| Engine version numbers (v3.4.5) | Internal labels | "the plan", "the published plan" |
| Code names (CDI_POP_WEIGHT, a09) | The reader has no code | The symbol or the plain name |

Write short sentences. One idea each. If a sentence has two "which" clauses, split it.

### The honesty rule for this paper

The audit found that the paper's weakness is unsourced choices, and that hiding them is what turns a weakness
into a rejection. So in this section, every fixed number is labelled one of four ways, in plain words:

- from a published source (cite it);
- set by the transport regulator as a service standard;
- taken from the e-bus operator;
- an assumption of the authors, tested in Section 4.10.

If you do this consistently, the reviewer's main objection is answered before it is raised.

## Part 4 — subsection cards

Each card gives: the job of the subsection, the paragraphs in order, the facts and numbers, the citations,
the traps, and the reviewer's question with the substance of your answer.

### 4.1 Framework overview (about 200 words; write it last)

**Job.** Tell the reader what goes in, what comes out, and the stages between. No detail.

**Paragraphs.**

1. *What the framework does.* Input: an inherited permit register. Output: a tiered network with a headway
   and a fleet for each route. What it does without: an origin–destination matrix, boarding counts, fare
   data for the routes being planned.
2. *Inputs, open and not open.* Open: population grid, OpenStreetMap, a routing engine. Not open: the permit
   register (from the transport regulator) and ridership totals for the one operator with electronic
   ticketing. Say that 4.5 lists every place the second one enters.
3. *The four phases,* with Figure 4: diagnosis of inputs; accessibility; consolidation and hierarchy; sizing
   and uncertainty. One clause each. Point to Table 3 for parameters.
4. *Notation.* Define Ω, ρ_c, x_c, G, r, l(r). State the total population of Ω.

**Facts.** Ten districts of Kashmir Division. Population 6,584,762. Population grid: WorldPop, release
R2025A, constrained, 100 m. OpenStreetMap extract dated 6 January 2026.

**Citations.** WorldPop (dataset and method paper); OpenStreetMap; the routing engine.

**Traps.** Do not write "entirely from open data". Do not write "demand-free". Do not describe results.
The number is 6,584,762 everywhere, never 6,584,763.

**Reviewer asks:** "Is this really free of demand data?" Your answer is already in paragraph 2: no observed
demand for the routes planned; one operator's totals used where they exist; listed in 4.5.

### 4.2 Data conditioning and network construction (about 320 words)

**Job.** Describe each input as it was actually used, with its known defects, and say how the plan under
study was produced.

**Paragraphs.**

1. *The permit register.* What a permit is (it authorises a vehicle; it is not a route). How permits were
   reduced to corridors: both end points, direction ignored, matched at 11 m. Counts.
2. *Population.* Used as published. How it compares with the 2011 Census in total and by district. What that
   means for district-level results.
3. *Walking network and destinations.* Size of the walking graph. Number of destinations, three tiers, and
   their concentration in one district. Say plainly that this layer reflects how well a place is mapped.
4. *Provenance of the plan.* Four facts, one sentence each (see below). This paragraph is the most important
   in the subsection. Do not soften it and do not bury it.

**Facts.**

- 614 permit records; 157 distinct corridors; the median corridor has one permit; one corridor, Hazratbal to
  Lal Ded, has 42.
- Population total is 95.6 % of the 2011 Census total; district ratios range from 0.71 to 1.20.
- Walking graph: 18,533 km of edges inside the ten districts.
- Destinations: 2,431 points (1,030 high, 1,080 medium, 321 seasonal); two thirds in Srinagar district.
- Provenance: (a) a gazetteer of 103 place names; 37 villages no geocoder could find were placed at their
  district's centre; 19 of 186 routes (93 buses) end at such a point. (b) Road distances on 49 routes were
  replaced with values from an AI-assisted desk check, not verified by a person, with no source links kept;
  fleet on those routes went from 247 to 207. (c) Cycle times on five routes were re-timed from driver GPS;
  total went from 1,004 to 1,011. (d) Headway rules were fixed over about fifteen revisions reviewed with
  the transport regulator; the total ranged from 855 to 1,144 buses.

**Citations.** WorldPop; OpenStreetMap; Census of India 2011.

**Traps.** WorldPop R2025A is an alpha release; say so. Do not call the regulator "RTO"; write "the
transport regulator". Whether you may say the headway rules were set "in review with the regulator" is still
an open question for Avny ma'am; until she answers, write "policy constraints supplied to the study". Dataset
dates and graph statistics go in Table 2 or the supplement, not the text.

**Reviewer asks:** "How were corridors extracted from permits that record an area of operation?" Paragraph 1
must answer: what fields the register holds, how end points were geocoded, how many could not be placed.

### 4.3 Route catchment delineation (about 250 words)

**Job.** Define who counts as "served" by a route, and how overlapping routes are handled.

**Paragraphs.**

1. *Why not a straight-line buffer.* One sentence on the known bias, with citations. Kashmir's lakes and the
   Jhelum make it worse; the brief asks you to say this.
2. *The procedure.* Stops sampled along the route; each snapped to the nearest network node; a shortest-path
   search gives each node its walking distance to the nearest stop; the catchment is built from nodes within
   the budget, with a small tolerance for the last stretch off the network. Then Eq. 1.
3. *Population in the catchment.* Eq. 2.
4. *Overlap.* Per-route figures cannot be added. A cell covered by several routes is shared equally between
   them, Eq. 3, so allocated populations sum to the population of the union.
5. *What the comparison depends on.* The gap between straight-line and network figures depends on W, τ, the
   stop spacing and the cell-counting rule; Section 5.2 reports it across settings.

**Equations.** Eq. 1: catchment as a union of discs around reachable nodes, radius min(W − d(v), τ). Eq. 2:
sum of ρ_c over cells whose centre is inside. Eq. 3: π_c(r) = ρ_c / n_c for covered cells.

**Facts.** Stop spacing 250 m. Median snap distance 11 m. W = 400 m. τ = 100 m (one raster cell).

**Citations.** Two or three on straight-line versus network catchments (Gutiérrez and García-Palomares;
Biba et al.; El-Geneidy et al.). For 400 m: the UN indicator on access to public transport uses 500 m, and
Daniels and Mulley (2013) show walking distance depends on supply. The usual manual citation has not been
opened by anyone on the project; do not use it until someone has.

**Traps.** Do not claim Eq. 1 gives a "lower bound" on the bias; at other settings the difference is
smaller. Do not give the coverage percentages here. 400 m is a convention; call it that.

**Reviewer asks:** "Why 400 m, and why τ = 100 m?" Answer: 400 m is the convention, tested from 300 to
800 m; τ is one raster cell, tested from 50 to 150 m; both in 4.10.

### 4.4 Weighted opportunity accessibility (about 180 words)

**Job.** Define the destination score and be straightforward that its weights are judgement.

**Paragraphs.**

1. *The score.* Weighted count of destinations near the route, by tier. Eq. 4. Give the three weights.
2. *How destinations were put into tiers.* By OpenStreetMap tag, with name rules for known landmarks. Say
   that the assignment is coarse: for example every place of worship and every hospital tag is in the top
   tier.
3. *The tourist multiplier.* Why it exists (visitors are not in a residential population grid), which routes
   get it, Eq. 5. Where it entered and where it did not.
4. *Status of the weights.* They are assumptions. No expert weights were obtained. Their effect is tested in
   5.4 and 4.10.

**Facts.** α = 1.00, 0.40, 0.60. μ = 1.30 on 8 active routes; applied to those routes' resident count, so it
raised their index; it did not enter network coverage. Destinations are counted within 250 m of a route, not
400 m: in the plan by straight line, in the re-analysis along the network. State this distance correctly;
the old draft said "the same catchment", which is wrong.

**For your information, not necessarily for the text.** Re-tiering whole categories, or weighting every
destination equally, changes the class of at most 4 of 186 routes. That is a result (Section 5.4), but one
clause here pointing to it is reasonable.

**Traps.** The brief asks for weights derived three ways including an expert panel (AHP). The panel was not
run. Write what was done: equal and entropy weights for the two components, a sweep of the tier weights. Do
not mention the women's-destination boost as a method feature unless you also defend it; it touches 12
points. Do not repeat the code's reason for 0.4 ("education drives 30 % of women's ridership"); no data
supports it.

**Reviewer asks:** "Where do 1.0, 0.4 and 0.6 come from?" Answer: assumption; shown not to matter.

### 4.5 Composite demand index (about 300 words)

**Job.** Define the index, say what it is and is not, and list every place observed ridership enters.

**Paragraphs.**

1. *Construction.* Both components divided by route length; population density capped at its 95th
   percentile; each scaled from 0 to 1 across routes (Eq. 6); combined with weight β (Eq. 7).
2. *Is the composite doing any work?* Report the correlation between the two components and say what it
   implies. State which alternative weights are reported.
3. *What the index is.* A proxy for where demand is likely, not a measure of demand.
4. *Where observed ridership enters.* A numbered list of five items (below). Keep it as a list.
5. *The ridership estimate.* Eq. 8, what each term is, what it is used for, and that it is not a forecast.
   Close with the limited claim.

**Equations.** Eq. 6 minimum–maximum scaling. Eq. 7 CDI = β z_Π + (1 − β) z_O, with z the scaled values. Eq. 8 the ridership
estimate. Write Eq. 8 completely: it contains a trip rate (1.6 trips per person per day) and mode shares
(9 % urban, 7.2 % peri-urban, 5.4 % regional) as well as κ. The old draft left the trip rate out.

**Facts.** β = 0.50. Pearson correlation between components 0.88 to 0.89. κ = 0.33, fitted to 11.63 million
annual e-bus boardings. The five entry points: (1) the 30 e-bus routes are taken as given and never merged;
(2) their headway is the operator's 15-minute target and they are placed in the top class whatever their
index; (3) their fleet is the larger of the computed and the deployed fleet; (4) the scale, mode share and
trip rate of Eq. 8 are set from the operator's totals; (5) on 67 rural routes the headway is lengthened where
Eq. 8 implies low load.

**Citations.** OECD handbook on composite indicators; Shannon and the entropy-weight paper.

**Traps.** Never call Eq. 8 a forecast or a demand model. Do not write that principal-component weights were
a third independent weighting: with two components they equal equal weights. Say that trip rate, mode share
and κ multiply together, so only their product is fixed by the data. The name "Composite Demand Index" is in
the brief; keep the name but say in paragraph 3 that it is a proxy.

**Reviewer asks:** "What shows the index order matches demand order?" Honest answer: nothing in this paper;
the only route-level comparison available is reported in Section 6 and does not support it.

### 4.6 Permit consolidation (about 220 words)

**Job.** State the rule by which permits become routes, exactly enough to be coded.

**Paragraphs.**

1. *Overlap measure.* Buffers around route lines; overlap as a share of the smaller buffer. Eq. 9.
2. *The merge rule.* Three conditions, all required: overlap at least θ; start points within 2.5 km; and a
   route is merged only into the lead route of its group, never into another member. Say that the second and
   third conditions are why few distinct corridors merge.
3. *Algorithm 1,* in a box, five steps.
4. *Outcome and limits.* Routes in, routes out. The merge rule is not varied in the uncertainty analysis;
   one scenario (S4) shows how different the route set could be.

**Facts.** Buffer 80 m. θ = 0.65. 644 candidate rows (614 permits plus 30 e-bus routes) become 186 active
routes (32 trunks, 154 feeders); 458 rows are absorbed. 156 of 157 corridors are kept. Lead route: highest
index, at least 5 km long, above the 30th percentile of the index. E-bus routes are never merged. S4 lowers θ
to 0.50 and merges connected groups; describe it that way, not as "overlap alone".

**Traps.** The brief says "207 routes"; that number is from an old version. The plan has 186. Do not write
"reduction of 71 %" without the unit: almost all of it is the change from permits to corridors. All three
values (80 m, 0.65, 2.5 km) are assumptions; say so.

**Reviewer asks:** "Why 0.65, and why is it not in your uncertainty analysis?" Answer: assumption; pair
counts are reported across 0.50 to 0.90; the route set is held fixed in 4.10 and that is stated as a limit.

### 4.7 Hierarchy and service standards (about 220 words)

**Job.** Separate two things the old drafts blurred: how routes are ranked (a method), and what frequency
each class gets (a policy).

**Paragraphs.**

1. *Classes.* Routes ranked by the index and divided by Jenks natural breaks. How the number of classes was
   chosen. Eq. 10.
2. *Headways are policy values.* Give them. Say who set them, in the wording agreed with Avny ma'am.
3. *Overrides.* The published class of a route also reflects three overrides: e-bus routes, district
   headquarters, socially designated routes. Point to 5.6 for how far published classes agree with
   index-only classes.
4. *One headway per route for the whole day.*

**Equations.** Eq. 10, goodness of variance fit, for k = 2 to 7.

**Facts.** Fit is 0.786 for two classes and 0.902 for three. Headways: 15 minutes on e-bus routes; 20 on
other high-class routes; 35 on remaining urban and peri-urban routes; 35 to 50 on rural routes, with 50 the
longest permitted wait. In practice 62 of the 67 rural routes sit at 50 and 5 at 35.

**Citations.** Jenks (1967) and Fisher (1958). For the fit statistic, cite a paper that defines it; do not
attribute it to Jenks 1967.

**Traps.** The "smallest k reaching 0.80" rule has no source; call 0.80 an assumption, or simply say three
classes were chosen and the fit statistic supports the choice. Do not write "evaluated across peak, off-peak
and evening bands": the plan has no time-of-day headways. Do not call the rural rule "demand-responsive"
without adding that nearly all routes sit at the maximum. Do not claim the headways follow from the index.

**Reviewer asks:** "So the frequencies are just the regulator's preferences?" Answer: yes, they are service
standards, and Section 5.7 reports the fleet that estimated demand alone would justify beside the plan's.

### 4.8 Cycle time and fleet sizing (about 320 words)

**Job.** Give the arithmetic from route length to number of buses, and say which term actually decides it.

**Paragraphs.**

1. *Running time.* Free-flow time scaled for congestion, plus river delay, plus dwell. Eq. 11. Values.
2. *Cycle time and the cap.* Eq. 12. Then the central disclosure: the cap was meant as a ceiling on
   implausible values but is the binding term on most routes, where Eq. 11 has no effect; and the urban cap
   is faster than observed pace. Therefore the fleet is also sized from observed pace (4.10).
3. *Fleet per route.* Eq. 13: buses in service, spares, minimum.
4. *E-bus floor and total.* Eq. 14.
5. *Vehicle classes.* The register's three size classes; the rule that assigns them. Totals.
6. *Check of the arithmetic.* Independent re-implementation and what it reproduces.
7. *Demand cross-check.* Because headways are policy values, capacity is not tied to demand; so the fleet is
   also computed with each headway set to reach a target load on Eq. 8 (results in 5.7).

**Equations.** Eq. 11 t_run = χ (t_free + J) + δ l/Δ. Eq. 12 t_cyc = min(2 λ t_run , 2 l ω). Eq. 13
N_op = t_cyc / h rounded up, and N = max(σ N_op rounded up, N_min). Eq. 14 the total with the operator's fleet as a floor.

**Facts.** χ = 2.2 in the zone treated as city core, 1.4 elsewhere. The "core" is defined by a line of
latitude and covers 170 of 186 routes; say so. J = 8 minutes. δ = 0.5 minutes, Δ = 500 m. λ = 1.10. ω = 4.0,
2.5, 1.5 minutes per km for urban, peri-urban, regional. The cap binds on 169 of 186 routes. Observed median
urban pace 4.62 minutes per km. σ = 1.15. Minimum 2 buses (urban, peri-urban), 1 (regional). Total
728 + 283 = 1,011. Classes: 187 heavy, 754 medium, 70 light. Re-implementation: all 186 routes with the
plan's headways, the five GPS-timed cycles and the e-bus floors; 180 routes and a total of 1,000 without the
last two.

**Citations.** Vuchic (2005) and Ceder (2007) for the cycle-time and fleet formulae, after someone has
checked the pages. For the spare ratio, the ministry's review of road transport undertakings gives the share
of buses on the road (87.6 % in 2019–20), which is a checked Indian source.

**Traps.** Never write that the cap "ensures neither class is a majority on a trunk": medium buses are the
majority on 29 of 32 trunks. Heavy, medium and light are vehicle sizes; never "priority" classes. The
congestion values have no source; the code's reference to traffic-police studies must not be repeated. Do not
say the congestion model was "calibrated".

**Reviewer asks:** "On 91 % of routes your fleet is length times a constant over headway. Where does the
constant come from?" Answer: an assumption, disclosed as binding, shown to be faster than observed pace, and
replaced by observed pace in the second regime.

### 4.9 Quality assurance gates (about 100 words)

**Job.** List the automatic checks that stop the pipeline. A short paragraph or a list.

**Content.** Every route inside the study area; one population total used throughout; the fleet model
reproduces the published fleet; permits, corridors and routes reconcile; route codes unique; vehicle classes
sum to the fleet on every route. Then two quantities that are reported but not enforced: agreement of the
recomputed straight-line catchment with the plan's own figure, and the number of route ends placed at a
district centre.

**Traps.** Name only gates that have a test which can fail. Before you write this subsection, open the
`tests/` folder and tick each gate against a test. If a gate has no test, either leave it out or ask for the
test to be written. Do not write "no route end is at a district centre": 19 routes have one.

### 4.10 Sensitivity and uncertainty (about 190 words)

**Job.** Say how the assumptions are tested, and exactly what the resulting ranges mean.

**Paragraphs.**

1. *Three tools.* One-at-a-time sweeps over each parameter's range. A Monte Carlo analysis sampling the
   parameters jointly. Sobol' indices attributing output variance to inputs. A grid for the catchment
   parameters.
2. *Two regimes for the fleet.* A: the plan as specified. B: cycle time from observed pace where pace was
   observed. Say which routes are in which group.
3. *What the ranges are and are not.* Median and 5th to 95th percentile of the draws; conditional on the
   distributions chosen; not confidence intervals. The merge rule is not sampled, so uncertainty in the
   route set lies outside. The analysis supports a statement about robustness to parameters and speed; it is
   not a check against demand.

**Facts.** 5,000 draws; twelve parameters. Walking budget 300 to 800 m; stop spacing 150 to 400 m. Regime B
uses pace observed on 16 corridors around Srinagar: 5 routes measured directly, 84 take the pooled pace,
30 e-bus and 67 regional routes unchanged because no pace was observed for them. Regime B is computed two
ways: from overall observed pace, and from moving pace with the model's own dwell.

**Citations.** Sobol' (2001); Saltelli et al. (2008, 2010).

**Traps.** The brief asks for "the probability that each route retains its assigned tier": you can describe
that output, but it is the stability of the index-only classes, not of the published classes. Do not write
"confidence interval". Do not report the ranges themselves; they are results. The ranges and distributions of
the inputs were chosen by the authors; say so and put them in Table 3.

**Reviewer asks:** "Your largest sensitivity is the spare ratio. Is that uncertainty or a policy choice?"
Answer: a policy choice; it dominates because the cap fixes everything else, which is why regime B exists.

## Part 5 — the passenger survey

The questionnaire you shared is a before-and-after passenger survey for Srinagar city buses: six background
questions, six trip facts (walk, wait, changes, total time, fare, days per week), ten ratings on a five-point
scale, and one overall-change question, in English, Hindi and Urdu, with consent and anonymity statements.

**What it does for the paper.** It is the first check in this project that does not depend on the plan's own
inputs. The parameter register lists "nothing independent validates the plan" as the third-largest risk. A
passenger survey is the right kind of answer.

**Where it goes.** The design belongs to whoever runs it, and its results belong in Section 6. If Prof.
Kathuria wants the design in the methodology, it is a short new subsection (4.11) written by him or with him.
Do not write it from this guide alone. Whoever writes it needs to state six things:

1. **Population and sampling.** Who could be sampled (adult bus passengers on which routes, which stops,
   which hours and days) and how respondents were chosen.
2. **Sample size.** How 348 was derived: the formula, the confidence level, the margin of error and the
   population figure used. I cannot tell from the number alone. It is in the range a 95 % confidence, ± 5 %
   calculation gives for a population of a few thousand; ask which calculation it was.
3. **Design.** The form allows three modes: before only, after only, and both in a single visit. These are
   different designs with different strengths. A single visit asking people to recall "before" is the weakest
   (memory and present mood colour the answer). The paper must say which mode produced which share of the 348.
4. **What "after" means.** The form says "after the new routes began". Section 6 must say plainly which
   routes had changed, when, and how that relates to the plan studied in this paper. This connects to the open
   question for Avny ma'am on what was actually implemented.
5. **Analysis.** Paired comparison for the same respondents, or two independent samples; which test; how
   "cannot recall" and NA are handled.
6. **Ethics.** Consent is on the form. The paper still needs the ethics committee's approval or exemption.

**What it cannot show.** Stated satisfaction and self-reported times, in Srinagar, on changed routes. It does
not check the fleet number, the index, or anything outside the city. Section 6 should say so.

**For Section 4 as you write it.** Nothing changes except one pointer: where 4.10 says the analysis is not a
check against demand, you may add that a passenger survey is reported in Section 6.

## Part 6 — before you send it to anyone

### Content

- [ ] Every subsection of the brief (4.1 to 4.10) is present, with its title unchanged.
- [ ] Every fixed number is labelled: published source, regulator, operator, or assumption.
- [ ] Every equation is numbered, introduced, and has all symbols defined with units.
- [ ] Each symbol means one thing; the list matches Part 3 of this guide.
- [ ] The provenance paragraph in 4.2 has all four facts.
- [ ] The five entry points of e-bus data are listed in 4.5.
- [ ] The cap is disclosed as binding in 4.8.
- [ ] 4.10 says what the ranges are not.
- [ ] No result appears that belongs in Section 5.
- [ ] None of the avoided words in Part 3 appears.
- [ ] No old numbers: 342 permits, 207 routes, 1,009 buses, 43,809 GPS runs, 6,584,763.

### Numbers

- [ ] Every number checked against `paper/CLAIM_LEDGER.md` on the day you finish.
- [ ] 728 + 283 = 1,011 and 187 + 754 + 70 = 1,011.
- [ ] 614 permits + 30 e-bus routes = 644 rows; 186 active + 458 absorbed = 644.

### Form

- [ ] About 2,300 words of prose, not counting equations, the algorithm, tables and captions.
- [ ] Figure 4, Table 3 and Algorithm 1 are each cited in the text before they appear.
- [ ] Every citation is to a source someone on the team has opened.
- [ ] British spelling throughout (the co-authors' sections mix both; the paper needs one).
- [ ] Read it aloud once. Any sentence you run out of breath on is too long.

### Then

Give it to one co-author who has not seen the code and ask a single question: "Could you redo this from the
text?" Every place they say no is a place to add a sentence.

### Common mistakes in a first paper

1. Reporting results in the methodology.
2. Describing the code instead of the method ("the script loops over routes").
3. Telling the history of the project ("we first tried", "an earlier version"). Only the final method is
   described. The one exception here is the provenance paragraph, which exists because the history changed
   the plan.
4. Defending choices with adjectives instead of sources.
5. Introducing a symbol and never using it again, or using one that was never defined.
6. Hiding a weakness in a subordinate clause. State it in its own sentence.
7. Writing to the word limit by adding. Good sections are made by cutting.

### A note on the AI declaration

If you write Section 4 by hand, the declaration of AI use changes for this section: the text is yours, while
the analysis code, the numbers and this guide's outline were produced with AI assistance. Tell whoever
maintains the declaration so it says exactly that.
