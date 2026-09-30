# 1. Introduction

> **Provenance and editorial status.** Sections 1.1–1.6 below are **co-author prose, transcribed verbatim**
> from the author attachment *"Copy of Paper Route Rationale_AK.pdf"* (owners: Misti and Avny; drafted text
> recovered via `paper/_reflow_ak.py`). **Nothing in that prose has been rewritten, condensed, or deleted.**
> The only mechanical interventions are (a) restoring section headings that the flat PDF extraction lost,
> (b) rejoining two sentences that a page break had split mid-number, and (c) adding clearly delimited
> `> **[EDITORIAL FLAG …]**` blocks. Every flag raises a question for the co-authors; none resolves one.
> Target length for this section is 1,200 words (attachment). Current verbatim body: ~1,280 words.

---

## 1.1 Urban bus transport under stress in Indian cities

India is facing a structural and widening shortage for urban public buses. In estimation from 2026 to 2047,
the country's urban population is to grow from 490 million to about 763 million; this adds more than 270
million residents who will have dependencies for public transport (CSE & CITIES Forum 2026). In contrast to
this demographic situation and demand, the municipal bus fleets continue to shrink relatively. The current
national bus availability ranges roughly from 0.13 to 0.14 buses per 1000 people, this makes national
provision nearly 70% below the benchmark of 0.44 set by Ministry of Housing and Urban Affairs (MoHUA) as per
CSE & CITIES Forum, 2026; MoHUA, 2014; Pucher et al., 2007. This shortage issue hits secondary cities most.
Over 400 Class-I cities with population count ranging from 100,000 to 1 Million have no organised municipal
bus network at all (CSE-CITIES Forum, 2026) while at the same time base digital transit data is almost non
existing; less than 15 indian transit agencies publish open General Transit Feed Specification (GTFS) feeds.
On ground, this gap is covered with private minibuses and other vehicles. Operating through this ad-hoc,
permit by permit allocation without route integration or systematic timetable leaves the urban cities with
fragmented and unreliable service to public.

> **[EDITORIAL FLAG 1.1-a — citation verification]** Five quantitative claims in this paragraph each need a
> page-level citation before submission: the 490→763 million urban projection; the 0.13–0.14 buses/1,000
> figure; the MoHUA 0.44 benchmark; the ">400 Class-I cities with no organised bus network" count; and the
> "<15 agencies publish GTFS" count. `paper/references.bib` carries the CSE & CITIES Forum (2026), MoHUA
> (2014) and Pucher et al. (2007) entries; the specific page/table for each number is still needed. This is
> the highest-yield paragraph in the paper for a reviewer to fact-check, because every number in it is
> externally verifiable.

> **[EDITORIAL FLAG 1.1-b — in-text citation format]** "as per CSE & CITIES Forum, 2026; MoHUA, 2014; Pucher
> et al., 2007" should be parenthetical *(CSE & CITIES Forum, 2026; MoHUA, 2014; Pucher et al., 2007)* in
> Elsevier/APA style. Also note "CSE & CITIES Forum 2026" and "CSE-CITIES Forum, 2026" appear as two
> different strings for the same source — one form must be chosen.

---

## 1.2 Route rationalisation as a low-cost, high-leverage intervention

Urban transport policies often emphasize for capital-intensive, mass transit infrastructure to address the
growing demand. Though the urban rail metro systems provide substantial capacity along high density corridors
in primary metropolitan areas, they require significant capital for enabling route to over US$ 40 Million per
km, compared to US$ 2.5 Million per km when its Bus Rapid Transit (BRT) (Badami & Haider, 2007). In secondary
and Tier-II urban regions, taking mutli-year timeline projects and heavy infrastructure costs creates need for
careful fiscal planning along with catering needs for immediate transit needs. Instead, comprehensive bus
route rationalisation along with network redesign can make an exceptional cost effective and efficient
solution that costs under US$0.05 Million per km (Badami & Haider, 2007). Rather than relying on heavy civil
construction, this restructuring optimizes for existing ground infrastructure and operational vehicle assets.
By merging overlapping services on busy central spines and deploying the spare assets to cover underserved
peripheral corridors, route rationalisation delivers rapid improvements for better public access. This is even
positively practical and cost efficient for municipal and transport departments that seek solution for
delivery of time effective results on ground for people.

> **[EDITORIAL FLAG 1.2-a — page-break repair, disclosed]** The PDF extraction split "US$ 40 Million per km,
> compared to US$ / 2.5 Million per km" across a page boundary. The two fragments have been rejoined as
> "US$ 2.5 Million per km". No wording was altered. If the intended figure was different, correct here.

> **[EDITORIAL FLAG 1.2-b — cost figures need a year and a base]** The three capital-cost figures (US$40M/km
> metro, US$2.5M/km BRT, US$0.05M/km rationalisation) are attributed to Badami & Haider (2007). A 2007 dollar
> figure quoted in a 2026 paper needs either the base year stated explicitly or inflation adjustment. A
> reviewer will ask. Recommend: "(in 2007 US$; Badami & Haider, 2007)".

---

## 1.3 The demand-data precondition and why it binds

The academic literature in Transit Network Desgin and Frequency Setting (TNDFS) provides extensive
mathematical frameworks to optimize bus routes and their operating schedules (Ceder, 2007; Guihaire & Hao,
2008; Ibarra-Rojas et al., 2015). However, these methodologies have the fundamental precondition: the
availability of comprehensive, empirical passenger demand data, such like household origin-destination (OD)
surveys, automated fare collection (AFC) transactions or automatic passenger counts (APC). In real practise,
this demand creates bottleneck across four core stages of public transit planning:

1. **Objective function formation:** Classical network optimization models minimize generalized passenger
   travel disutility like in-vehicle time, waiting time and transfer penalties while balancing against
   operator cost.

2. **Frequency and Headway setting:** Standard operational methods calculate route frequency (*f<sub>k</sub>*)
   as a function of peak passenger volume on the heaviest loaded link (*Q<sub>k,max</sub>*):

   <!-- FORMULA PLACEHOLDER — see EDITORIAL FLAG 1.3-a -->

   Where *C<sub>veh</sub>* is rated vehicle capacity and *LF<sub>target</sub>* is the target load factor. If
   peak passenger volume is unobserved, frequency cannot be derived.

3. **Route Pruning:** Standard algorithms identify and eliminate redundant routes based on
   passenger-kilometre revenue or observed boarding numbers. Without electronic ticketing data, authorities
   have no reliable way to separate essential trunk routes from redundant parallel ones.

4. **Model Validation:** Conventional planning pipeline validate their results by back-casting simulated
   passenger flows against historical counts.

For mid-sized and secondary cities, this creates an operational deadlock. Local authorities cannot run
standard network optimization without passenger demand data and also lack the infrastructure or survey budget
to collect the needful data. This seeks rethinking of planning model. As shown in **Figure 1**, instead of
waiting for unavailable demand data, cities can adopt a supply-side approach which builds an implementable
network using open spatial data and clear, policy-driven service standards.

> **[EDITORIAL FLAG 1.3-a — missing equation]** The PDF carries a `<formula>` placeholder here; the equation
> itself did not survive extraction. The standard form implied by the surrounding text is
> *f<sub>k</sub>* = *Q<sub>k,max</sub>* / (*C<sub>veh</sub>* · *LF<sub>target</sub>*). **This has NOT been
> inserted into the body** — the co-authors must supply and confirm their intended equation, since it is
> their prose and their citation. It is worth numbering it as Eq. (0) or moving it to §2, because §4 already
> owns Equations 1–14 and a stray unnumbered formula in §1 will confuse the cross-reference scheme.

> **[EDITORIAL FLAG 1.3-b — this is the load-bearing subsection]** The attachment's own guidance is that
> "§1.3 is the section that earns the paper … If the reader does not feel the constraint bite here, nothing
> later lands." The four-stage breakdown does this well. One strengthening suggestion (co-authors' call): each
> of the four stages could name the *specific* data object it requires — stage 1 an OD matrix, stage 2 link
> loads, stage 3 boarding counts, stage 4 a historical count series — so the reader can tick off exactly what
> Kashmir lacks.

---

## 1.4 Data scarcity in Tier-II, permit-based networks

In secondary Indian cities, route-level permits stand as base for evolving the public transit network through
history, issued by Regional Transport Offices (RTOs) and State Transport Authorities (STAs) in response to
localized mobility demands. Over time, this point to point allocation has naturally concentrated them highly
along primary commercial and healthcare arterials, while peripherals and developing peri-urban links suffer
in frequency and service. In addition, the public transit delivery involves multiple stakeholders including
RTOs managing private stage carriages, municipal Special Purpose Vehicles (eg: Smart City Ltd) introducing
modern electric buses, and State Road Transport Corporations (SRTCs) — each operating under distinct mandates
without an integrated digital scheduling platform or system.

The Kashmir Valley illustrates this operational reality at a regional scale. It comprises of 10-district
urban-rural basin of 15,948 sq.km with 6.58 million residents. The valley in itself has unique physical
constraints for mobility network, including nine critical Jhelum River Bridge crossing in Srinagar, major
lakes barriers (Dal, Nigeen and Anchar), and sub-zero winter freezes during Chillai Kalan. The existing
network comprises of 640+ legacy permit routes, with heavy overlap along primary civic arterials — such as 38
to 42 active permits serving the Soura and Lal Ded hospital corridors. The network must also consider and
support the significant gender-specific transit dependency (64.5% female ridership recorded via CHALO
electronic ticketing) and an annual influx of 2.5 million tourists, all of this with lack of a unified open
GTFS feed.

> **[EDITORIAL FLAG 1.4-a — this paragraph is ALREADY on the locked framing. Good.]** §1.4 uses the correct
> Kashmir-Division scope (10 districts, 15,948 km², 6.58 million, 640+ permits, 38–42 permits on the Lal Ded
> corridor). This matches `STATUS.md §0`, `CLAIM_LEDGER.md` (CL-01, CL-05) and F1. **No change needed.**
> Note for the co-authors: this is the framing the whole paper now uses, and it *contradicts* the Abstract
> plan, the Highlights and the "Policy Failure" block in the same attachment, which still say "342 permits →
> 207 routes / ~1,009 buses / Srinagar Municipal Corporation". See `PENDING_DECISIONS.pdf` Decision 3.

> **[EDITORIAL FLAG 1.4-b — two numbers need a source line]** (i) "64.5% female ridership recorded via CHALO
> electronic ticketing" — this is not currently in the claim ledger and no module produces it. It needs a
> CHALO source document and a new CL ID, or it must be dropped. (ii) "2.5 million tourists" annually needs a
> JKTDC / J&K Economic Survey citation with a year. Both are strong, quotable numbers — worth the ten minutes
> to source them properly.

> **[EDITORIAL FLAG 1.4-c — attachment guidance not yet followed]** The attachment instructs: *"Introduce
> Srinagar in three sentences at the end of 1.4 … Do not open the paper with Kashmir. Transport Policy wants
> the problem class first, the city second."* §1.1–§1.3 correctly keep the problem class first, and the
> valley enters only in §1.4 — so the guidance **is** satisfied, but the valley paragraph runs to seven
> sentences rather than three. Co-authors may wish to compress, or may reasonably decide the extra detail
> earns its place given it now covers a 10-district region rather than one city.

---

## 1.5 Research gap, objectives and contributions

Despite the advancements in transit network design, present optimization frameworks offer no validated
methodology to restructure fragmented, permit based bus systems in complete absence of empirical demand data,
which is the case across most secondary and Tier-II Indian cities. To address this gap, this study develops a
supply-side, open-data planning framework that translates road topology, gridded population distributions, and
community anchors into a rationalised transit network.

**Main objectives:**

- **O1 (Spatial Baseline):** Construct an open spatial transit foundation integrating OpenStreetMap road
  networks, WorldPop demographics, and geo-located Points of Interest (POI) across a regional basin.
- **O2 (Topological Consolidation):** Develop an undirected graph consolidation algorithm to prune
  overlapping legacy permits into a coherent multi-tier corridor hierarchy.
- **O3 (Supply-Side Scheduling):** Derive policy-anchored headway bands from a Composite Demand Index (CDI)
  independent of unobserved passenger link flows.
- **O4 (Fleet Dimensioning):** Calculate realistic round-trip cycle times, fleet allocations, and vehicle size
  classes (light, medium, and heavy passenger vehicles: LPV, MPV, HPV) accounting for physical bridge
  bottlenecks and dwell penalties.
- **O5 (Validation & Portability):** Benchmark the operational outputs against empirical operational data and
  demonstrate policy transferability.

Correspondingly, this paper sets five major contributions: (1) mathematical rigorous, supply-side methodology
of network design for data scarce regions; (2) a graph-based algorithm to merge overlapping route permits into
unified corridors; (3) a novel demographic based and seasonal considerate demand-proxy formulations; (4) a
regional-scale deployment across 10 districts in the Kashmir Valley, restructuring 644 legacy permits into 186
coordinated corridors; and (5) an open, reproducible spatial workflow designed for adoption across
data-constrained secondary urban regions.

> **[EDITORIAL FLAG 1.5-a — contribution (4) is exactly right and should be protected]** "644 legacy permits
> into 186 coordinated corridors" matches the locked numbers (CL-05, CL-06). Keep this sentence verbatim; it
> is the single place in §1 where the headline result is stated, and it is stated correctly.

> **[EDITORIAL FLAG 1.5-b — O5 wording vs. what §6 can actually claim]** O5 says "Benchmark the operational
> outputs against empirical operational data". §6 as drafted can support this **only** in the supply-side
> sense (geometry → cycle time → fleet, validated against 43,809 driver-GPS runs; F3, F10–F12). It cannot
> support a demand-side reading. Recommend tightening O5 to "…against empirical *operational* (supply-side)
> data", so that no reader takes O5 as a promise of ridership validation. This is a one-word-class change and
> is left to the co-authors.

> **[EDITORIAL FLAG 1.5-c — "novel … seasonal considerate demand-proxy" (contribution 3)]** The seasonality
> element is the 1.3× tourist multiplier applied to 8 routes, which F9 diagnoses as sizing 285,914 synthetic
> headcount. Calling it "novel" invites a reviewer to audit it. Safer framing: describe it as an explicit,
> parameterised and *sensitivity-tested* seasonal adjustment (it is in the Sobol' set, `a09`), rather than as
> a novelty. Co-authors' call.

---

## 1.6 Organisation of the paper

The remainder of this paper content is as follows. Section 2 reviews the literature on transit network design
under data constraints and details the physical and institutional setting of the Kashmir Valley. Section 3
formulates the supply-side methodology, detailing spatial baseline integration, topological permit
consolidation, demand proxying, and fleet dimensioning. Section 4 presents the empirical results and
sensitivity analyses. Section 5 discusses policy trade-offs, governance challenges, and framework
transferability, before Section 6 that concludes with directions for future work.

> **[EDITORIAL FLAG 1.6-a — ⚠ THE ONE REAL STRUCTURAL CONFLICT IN THE PAPER. Escalated as Decision 1.]**
> This paragraph describes a **six-section** paper (Lit+Setting / Methodology / Results / Discussion /
> Conclusions). The attachment it sits inside describes an **eight-section** paper, and assigns owners and
> word budgets to all eight: §1 Introduction (Misti+Avny, 1,200 w) · §2 Literature review and research gap
> (Sharvesh+Ankit, 1,400 w) · §3 Study area and data (Krishna, 1,100 w) · §4 Methodology (Prashant, 2,300 w) ·
> §5 Results and analysis (Prashant+Misti, 2,400 w) · §6 Validation (Avny+Krishnan+Prashant, 900 w) ·
> §7 Discussion and policy implications (Ankit+Avny+Misti, 1,200 w) · §8 Conclusions (Ankit+Prashant+Sharvesh,
> 400 w). The repository follows that eight-section scheme.
>
> **The prose above has been preserved exactly as written and has NOT been renumbered.** But it cannot go to
> the journal as-is, because under it there is no slot for §6 Validation — the section the attachment itself
> calls the one that "decides the paper's fate". The eight-section scheme is therefore what the rest of the
> manuscript is built on.
>
> **Replacement text is proposed — not applied — for the co-authors to accept or reject:**
>
> *"The remainder of the paper is organised as follows. Section 2 reviews the literature on transit network
> design and route rationalisation, and quantifies the research gap. Section 3 describes the study area, the
> data inventory and the data-quality diagnostics. Section 4 formulates the supply-side methodology, detailing
> spatial baseline integration, topological permit consolidation, demand proxying and fleet dimensioning.
> Section 5 presents the empirical results. Section 6 sets out the multi-channel validation protocol and what
> it can and cannot establish. Section 7 discusses policy trade-offs, governance challenges and framework
> transferability. Section 8 concludes with directions for future work."*

---

## Co-author block — "Policy Failure"

> **[PROVENANCE]** The following is **co-author prose, transcribed verbatim** from the attachment, where it
> appears immediately after §1.6 under the heading *"Policy Failure"*. It is reproduced here unchanged. See
> the flags beneath it for two placement/scope questions that only the co-authors can settle.

Public transport services operating in Jammu and Kashmir do not fall entirely under a single permitting
authority. Bus services operating within cities/districts are permitted by the Regional Transport Authority
(RTA), buses originating from other districts and operating within the Srinagar Municipal Area may fall under
the permitting jurisdiction of the State Transport Authority (STA), Srinagar and Jammu municipal areas operate
electric buses run by the respective Smart City Limited Companies, and finally, the JK Road Transport
Corporation (JKRTC) operates intra-state and inter state services. The transport network in J&K therefore
includes bus services that are governed by different permitting arrangements and agencies. For the purpose of
this study, bus service data for Srinagar (the area falling within the limits of the Srinagar Municipal
Corporation (SMC)) was studied. The RTA, issues permits broadly divided into Eastern and Western areas for
this purpose. For city bus services permitted by the RTA, an applicant generally applies for a vehicle and
indicates the area of operation, rather than proposing a specific route based on an assessment of passenger
demand or the requirements of the wider network. The RTA considers such applications in accordance with the
applicable legal and regulatory requirements. The Smart City electric-bus system is a separate planned
intervention. There is also no systematic route-rationalisation exercise before permits are allotted. The RTC
caters largely to destinations outside the municipal area and its routes were designated decades ago, without
having been modified to align with changing demographic and demand patterns. At present, there is an absence
of a comprehensive city-wide route plan for public transport and an absence of a single agency that regulates
and manages public transport operations.

In Jammu and Kashmir, the procedure for grant of a stage carriage permit is primarily governed by the Motor
Vehicles Act, 1988 and the rules made thereunder. Where the proposed Stage carriage service is to be operated
within the jurisdiction of a particular Regional Transport Authority (RTA), the application is made before the
concerned RTA. Accordingly, in the case of services operating within Srinagar District and falling within the
jurisdiction of the RTA Srinagar, the RTA is the competent authority to consider and grant the permit.
However, where the proposed service extends beyond the jurisdiction of a single RTA, the matter falls within
the competence of the State Transport Authority (STA), particularly where the service originates in one
district and terminates in another. The applicant is required to furnish details such as the proposed route in
the classified areas (Eastern/Western), vehicle particulars, seating capacity, number of trips, timetable and
other prescribed particulars. The competent authority examines the application and considers the proposed
service in the context of existing transport arrangements, route feasibility and the requirements of the
travelling public. The permit may be granted as applied for, granted with modifications, or refused in
accordance with the applicable provisions. Once granted, the permit specifies the area (Eastern/Western) and
is subject to conditions relating to the passenger capacity and other operational requirements.

Thus, the permit system in J&K operates through a two-level institutional structure, with the RTA dealing
primarily with services confined to its jurisdiction and the STA dealing with services that extend across the
jurisdiction of more than one RTA. These permits are permanent in nature, implying they do not have an end
validity. Over time, the existing route structure has consequently developed through a combination of existing
practices and the demands and representations of the Eastern and Western bus associations. While this allows
individual applications to be considered within the existing regulatory framework, it does not provide an
opportunity to assess how individual permits respond to travel demand and affect the transport network as a
whole. In particular, permit allocation is not systematically preceded by an assessment of route duplication,
passenger demand, service gaps, connectivity, fleet requirements or the frequency of services required on
different corridors.

This is reflected in the present pattern of public transport services. Some corridors have overlapping
services, while other areas have comparatively limited connectivity. Examples of overlapping service patterns
include Lal Chowk–Lalbazar and Bagh-i-Shuer–Lal Chowk; Chanapora–Soura and Lal Chowk–Soura; and Malbagh–LD and
Soura–LD. In contrast, Lal Chowk–Rangreth and Lal Chowk–PanthaChowk have been identified through official and
field-level observations as areas with comparatively inadequate connectivity. These observations suggest that
the issue is not simply the number of buses available, but also where those buses operate and how the routes
are distributed across the city.

The underlying policy issue is that presently permitting is done as a response to individual permit
applications rather than for planning the public transport network as a whole, not accounting for where
services are required, where routes overlap, which areas are underserved, or what level of fleet and service
frequency is appropriate for individual corridors. Moreover, the permit is valid in perpetuity, hence, it is
challenging for the regulator to control, alter and plan public transport routes in the face of dynamic
scenarios.

The study examines whether a city-wide bus network can be planned and fleet requirements estimated even where
detailed passenger-demand data are not available. It explores the use of readily available spatial and network
information as a starting point for route rationalisation and fleet planning. The intention is not to treat
such information as a substitute for actual passenger-demand data, but to provide a practical basis for
improving upon the present application driven approach and for developing better data systems over time.

> **[EDITORIAL FLAG PF-a — placement]** This block is the strongest institutional writing in the manuscript
> and is genuinely distinctive material — very few transit papers explain the *statutory* mechanism that
> produced the network being rationalised. But structurally it is **§3.3 "Existing supply and institutional
> structure"** material, not introduction material: it is ~900 words, which alone would push §1 to ~2,200
> words against a 1,200-word budget. **Recommendation (not applied): move this block to §3.3, and leave a
> two-sentence pointer in §1.4.** It has been left in place here so that the co-authors see it exactly where
> they wrote it.

> **[EDITORIAL FLAG PF-b — ⚠ scope: "bus service data for Srinagar (… Srinagar Municipal Corporation) was
> studied". Escalated as Decision 3.]** The quantitative plan in this paper covers **all ten districts of
> Kashmir Division** (614 permits + 30 e-bus routes → 644 rows → 186 active routes; denominator 6,584,762 —
> CL-01, CL-05, CL-06). The sentence above states the study is confined to the SMC area. Both cannot stand.
> The likely reconciliation — which the co-authors should confirm rather than have imposed — is that the
> **institutional and permit-law analysis** is Srinagar-specific (the RTA Srinagar Eastern/Western permit
> system genuinely is), while the **network plan** is division-wide. If so, one clarifying sentence fixes it,
> e.g. *"The institutional analysis in this subsection is drawn from the Srinagar Municipal Corporation area,
> where the RTA's Eastern/Western permit structure is documented; the network plan presented in Sections 4–6
> covers all ten districts of Kashmir Division."* **No such sentence has been inserted.**

> **[EDITORIAL FLAG PF-c — the named corridors are checkable and worth keeping]** Lal Chowk–Lalbazar,
> Bagh-i-Shuer–Lal Chowk, Chanapora–Soura, Lal Chowk–Soura, Malbagh–LD, Soura–LD (overlapping); Lal
> Chowk–Rangreth, Lal Chowk–Pantha Chowk (under-served). These are exactly the kind of concrete, falsifiable
> claim reviewers reward. Module `a10_network_diagnostics` computes per-corridor link duplication from the
> permit register independently; if its most-duplicated corridors match this list, that is a genuine
> convergence worth a sentence in §5. If they do **not** match, that disagreement must be reported, not
> smoothed over.

---

## Figure and table calls for §1

- **Figure 1 — Conceptual framework (two panels).** *(Top)* the conventional demand-driven transit planning
  pipeline, with data dependencies (OD matrices, AFC feeds, APC counts) drawn as locks that prevent
  optimisation in data-scarce settings. *(Bottom)* the proposed supply-side open-data pipeline, showing
  OpenStreetMap street topology, WorldPop gridded demographics and open Points of Interest feeding directly
  into topological consolidation, policy-anchored headway bands and cycle-time fleet dimensioning. **Status:
  not yet generated** (`analysis/fig_generate_all.py` is a stub). Caption above is the co-authors' own,
  transcribed verbatim.

- **Statistics the attachment requires for §1, each needing a verified citation.** (1) buses per 1,000
  population, India against comparators; (2) number of Indian cities publishing GTFS; (3) share of Class-I
  cities with an organised bus service; (4) capital cost per km, metro vs BRT vs network redesign; (5) study
  area population, vehicle registrations, tourist arrivals. Items 1–4 appear in §1.1–§1.2 above and are
  covered by FLAG 1.1-a and FLAG 1.2-b. **Item 5 is not yet written**: population is established
  (6,584,762 — CL-11), but *vehicle registrations* and *tourist arrivals* have no source in the repository
  and no module produces them. Either a co-author supplies citable figures (J&K Economic Survey; JKTDC
  arrivals series) or item 5 is reduced to population alone.
