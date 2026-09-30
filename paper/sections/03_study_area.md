# 3. Study area and data

> **Provenance and editorial status.** The attachment assigns §3 to **Krishna** with a 1,100-word budget and
> supplies a subsection skeleton (§3.1–§3.6), three hints, a Figure 3 specification and a Table 2
> specification, **but no drafted prose**. What follows is **a draft written for co-author review**. Nothing
> written by another author has been displaced: the attachment's substantial institutional block ("Policy
> Failure") is preserved verbatim in `01_introduction.md`, and §3.3 below points to it rather than restating
> or replacing it.
>
> Every quantity in this draft is traceable to an executed module — `q01_data_quality`, `a01_build_walk_graph`,
> `a02_network_catchments`, `a02b_faithfulness`, `v04_gps_validation` — and carries its finding ID (F1–F12) or
> claim ID (CL-xx). **No number here is estimated.** Body length below: ~1,180 words excluding flags.

---

## 3.1 Kashmir Division as a critical case

Case selection here is deliberate rather than convenient. A critical case for a demand-free planning method is
one that maximises both terms of the problem: **data scarcity** and **planning need**. Kashmir Division
maximises both. On scarcity, the conventional bus network has no fare-card system, no automatic passenger
counting, no published GTFS feed, no household origin–destination survey, and operates under permits that
record an area of operation rather than a route; field data collection is further constrained by seasonal
closure and periodic security disruption. On need, the network is a 644-row permit register with heavy
duplication on hospital and civic arterials, transit deserts on the periphery, hard physical barriers (the
Jhelum crossings, and the Dal, Nigeen and Anchar lake systems), extreme seasonality, and a partially deployed
electric-bus system operating under a different authority from the incumbent minibuses. A method that produces
an implementable plan here is not thereby proven universal, but it has been tested against a harder
combination of constraints than most secondary cities present.

The study area is the **ten districts of Kashmir Division** — Srinagar, Budgam, Ganderbal, Baramulla,
Bandipora, Kupwara, Pulwama, Shopian, Anantnag and Kulgam — covering 15,948 km² with a modelled population of
**6,584,762** (CL-11). Administrative geography is taken from OpenStreetMap boundary relations at
`admin_level` 5 (10 districts) and 6 (39 tehsils), and all population denominators in this paper are computed
by point-in-polygon against the ten-district union, not against a bounding box.

> **[FLAG 3-A — ⚠ scope: the attachment's §3.1 heading reads "The SMR as a critical case". Escalated as
> Decision 3.]** "SMR" (Srinagar Metropolitan Region) is the **barred legacy framing**. The plan presented in
> §4–§6 is division-wide and its denominator is 6,584,762, not the ~1.66 million Srinagar urban agglomeration.
> This draft is written on the locked Kashmir-Division framing (`STATUS.md §0`, `CLAIM_LEDGER.md §4`). The
> heading has been changed accordingly — this is the one place in the four co-author sections where a
> co-author's *heading* has been altered rather than flagged, because leaving "SMR" in a section heading would
> propagate a barred scope into the table of contents. The co-authors should confirm.

## 3.2 Urban structure, population and opportunity distribution

The division is a single urban–rural basin with one dominant centre. Population is modelled from WorldPop
2026 at 100 m resolution (CL-11); opportunity is represented by **2,431 OpenStreetMap points of interest
across 63 categories**, grouped into three tiers by the weighting scheme set out in §4.4 (CL-20, CL-21).

The concentration of opportunity is itself a finding, and it constrains what the composite index can do.
**65.3% of all points of interest in the division (1,588 of 2,431) fall inside Srinagar district (F5).** Any
index with an opportunity term will therefore score Srinagar corridors highly almost by construction, which is
precisely why §4.5 reports the correlation between the population and opportunity components and §5.4 tests
whether the composite adds information over population alone. It is also why the paper reports results under
three independent weighting schemes rather than one.

*Opportunity concentration is a property of the data as much as of the city, and a planning index that ignores
it will recommend reinforcing the centre it was supposed to diagnose.*

## 3.3 Existing supply and institutional structure

The operative fact about supply in this setting is that no single agency holds the network. Permits for
services confined to one Regional Transport Authority's jurisdiction are issued by that RTA; services crossing
RTA boundaries fall to the State Transport Authority; the electric-bus system is operated by a municipal
Smart City special-purpose vehicle; and the state road transport corporation runs longer-distance services
designated decades ago. Permits are granted in perpetuity and specify an *area of operation* rather than a
route, and are not preceded by any assessment of duplication, service gaps, fleet requirement or frequency.

> **[FLAG 3-B — placement of the "Policy Failure" block.]** The detailed statutory account of this
> arrangement — RTA/STA competence under the Motor Vehicles Act 1988, the Eastern/Western area classification,
> the perpetual validity of permits, the named overlapping and under-served corridors — is **co-author prose
> that already exists**, currently sitting at the end of §1 in `01_introduction.md` where its author placed
> it. It is ~900 words and belongs here structurally (see FLAG PF-a). **It has not been moved.** If the
> co-authors agree to move it, §3.3 becomes that block plus the two paragraphs above as a lead-in, and §1
> drops back within its 1,200-word budget. If they prefer it in §1, §3.3 should be cut to a cross-reference.

The register itself is the paper's primary supply dataset: **614 digitised stage-carriage permits** (CL-01)
plus **30 electric-bus routes**, giving 644 rows. Its most important property is diagnosed in §3.5.

## 3.4 Data inventory

**Table 2** carries the full inventory — source, resolution, processing, validation and limitations — for
each dataset. The principal entries are: the RTO stage-carriage permit register (614 permits); the
OpenStreetMap road and pedestrian network, from which a walkable graph of **961,927 nodes, 973,569 edges and
23,323 km** was constructed; OSRM road travel times; the WorldPop 2026 gridded population surface; the 2011
Census district totals used as an external check; 2,431 OSM points of interest; the electric-bus route set
and its published ridership aggregates; OSM administrative boundaries at district and tehsil level; and a
driver-application GPS corpus of **43,809 recorded runs from approximately 157 drivers between February and
June 2026**.

Complete provenance, licence terms and SHA-256 hashes for all staged inputs are recorded in
`data/MANIFEST.md` in the companion repository.

> **[FLAG 3-C — Table 2 is partially blocked.]** Rows for the permit register, OSM network, OSRM times,
> WorldPop, Census, POIs, e-bus routes/ridership and boundaries can all be filled from `data/MANIFEST.md`
> today. The attachment additionally specifies rows for **Master Plan land use, terrain, water bodies,
> tourist arrivals, the fleet register and cost norms** — none of which are staged in the repository. Either
> those datasets are obtained and staged, or those rows are struck from Table 2. They must not appear as
> inventory rows for data the study does not hold.

## 3.5 Data quality diagnostics

This subsection is what separates a paper from a consultancy report, and the diagnostics reported here are
deliberately unflattering.

**The permit register is not a route register (F1).** The 614 permits resolve to **157 distinct undirected
origin–destination corridors**, a mean of 3.91 permits per corridor and a maximum of 42 on the
Hazratbal–Lal Ded corridor. This matters for how the headline result must be stated: the reduction from 644
rows to 186 active routes decomposes into **71.0 percentage points of change-of-unit and 0.2 percentage points
of genuine consolidation**, with **156 of 157 corridors retained (99.4%)**. Reporting a "71% route reduction"
without that decomposition would be reporting the cleaning of a register as a planning achievement.

**Modelled population runs below census (F2).** WorldPop 2026 gives 6,584,763 against a 2011 Census total of
6,888,475 across the same ten districts — a ratio of 0.956, implying a −0.30% annual rate that is
implausible for this region. The deficit is carried openly: it means coverage percentages in §5 are computed
against a denominator that is, if anything, conservative.

**OSM completeness licenses the walk graph (F6).** The correlation between district population density and
OSM road density is **ρ = 0.915**, indicating that mapping effort tracks settlement rather than leaving
peripheral districts systematically blank. This is the empirical warrant for using an open street network as
the catchment substrate, and it is reported because Barrington-Leigh and Millard-Ball (2017) give good reason
to expect the opposite in some regions.

**Geometry is faithful for most routes, and diagnosably unfaithful for the rest (F7).** Of 186 active routes,
142 show close agreement between stated and routed distance (median error 0.245%, *r* = 0.995); **44 carry
substituted road distances**, each individually identified rather than averaged away.

**Modelled runtime understates observed runtime (F3).** Against the driver-GPS corpus, mean absolute
percentage error between routing-engine time and observed in-motion time is **65.1%**, and between planned and
observed one-way time **47.6%**, with a median planned-to-observed ratio of **0.51**. This is the most
consequential diagnostic in the paper and it is pursued in §6.

**Observed activity is a lower bound, not a dormancy measure (F4, F12).** GPS shows recurring service on 66 of
186 routes, while 183 of 186 route geometries lie on roads that buses demonstrably use. The gap between those
two figures is app adoption, not service absence, and the smaller number must never be reported as a dormancy
rate.

*A register that has never been audited will always yield a spectacular reduction; the diagnostic obligation
is to say how much of it is arithmetic.*

## 3.6 Ethics, reproducibility and data availability

All analysis code, staged inputs and derived outputs are released in a public companion repository under
GPL-3.0, with a fixed random seed (20260823), a pinned environment, and a claim ledger mapping every number in
this paper to the module that produced it. Heavy binary inputs (the population raster and the cached walk
graph) are excluded from version control and are documented with retrieval instructions and SHA-256 hashes in
`data/MANIFEST.md`. Population, street-network, point-of-interest and administrative-boundary inputs are open
data under their respective licences (WorldPop: CC BY 4.0; OpenStreetMap: ODbL).

> **[FLAG 3-D — ⚠ GPS ETHICS AND CONSENT IS UNANSWERED AND CAN SINK THE PAPER. Escalated as Decision 4.]**
> The driver-GPS corpus (43,809 runs, ~157 drivers) is the paper's strongest observational evidence and the
> whole of validation channel V4 rests on it. Before submission this subsection **must** state, in the
> author's own words and not in mine: (i) under what basis the location data were collected and whether
> drivers were informed that operational traces might be used for research; (ii) whether the released data are
> anonymised, and by what mechanism — the staged files use hashed driver identifiers, but hashing alone is not
> anonymisation if a trace can be re-identified from its home depot and daily pattern; (iii) whether an
> institutional ethics committee reviewed the study, granted an exemption, or was not consulted. **"Not
> consulted" is an acceptable answer to write down; silence is not.** Elsevier requires an ethics statement
> for human-subjects-adjacent data, and a reviewer who notices ~157 identifiable workers' movement traces with
> no consent paragraph will stop reading. **This paragraph has been left deliberately blank rather than
> filled with a plausible-sounding statement.**

> **[FLAG 3-E — reproducibility claim must be scoped honestly.]** At the time of writing, **6 of 22 analysis
> modules are implemented and executed**; the remainder are declared stubs. The sentence above therefore says
> "all analysis code … is released", which is true, and deliberately does **not** say "fully reproducible
> pipeline", which would not be. When the remaining modules land, this wording can be strengthened — and not
> before.

---

## Figure and table calls for §3

- **Figure 3 — Four-panel study area:** (a) boundary and administrative units; (b) population density;
  (c) road hierarchy; (d) opportunity density. **Status: not generated.**
- **Table 2 — Data inventory.** Source · resolution · processing · validation · limitations, per dataset.
  **Status: buildable today from `data/MANIFEST.md` for the staged datasets; see FLAG 3-C for the rows that
  reference data the study does not hold.**
- Diagnostic detail behind §3.5 is already tabulated: `table02a_permit_duplication`,
  `table02b_permit_activity`, `table02c_osm_completeness`, `table02d_worldpop_vs_census`,
  `table02e_poi_inventory`, `table02f_traveltime_error`.
