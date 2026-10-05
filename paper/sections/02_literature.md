# 2. Literature review and research gap

> **Section owners:** Sharvesh, Ankit. **Target:** ~900 words (D26). **Status (2026-10-04):** rewritten on an
> executed review. Decision **D5 = Option A**: the search was run (OpenAlex and Scopus, 30 September –
> 1 October 2026), 60 studies were coded (46 from full text), and the §2.8 cross-tabulation is computed, not
> asserted. Protocol, query log, screening counts, coding rubric, novelty check and the full Table 1 are in
> `paper/literature_review/` (Supplementary Material S1). Every citation resolves in `references.bib` and was
> checked against Crossref. Flags 2-A to 2-D are closed; open points are listed at the end.

---

## 2.1 Review protocol

We searched Scopus (title, abstract, keywords) and OpenAlex (title, abstract) for English-language articles,
conference papers and reviews from 2000 to 2026. Thirteen query blocks combined planning terms (network
design, rationalisation, frequency setting, fleet size), data terms (origin–destination, smart card, data
scarcity, open data, accessibility, equity) and context terms (India, Global South, paratransit, permits);
six further Scopus queries targeted work resembling our own pipeline. The searches returned 5,488 unique
records. A keyword pre-filter left 2,518 for title-and-abstract screening against written criteria (a first
pass assisted by a large language model, then checked by the authors), and 873 were eligible. We coded a
purposive, theme-stratified sample of 57 of these, plus three seminal earlier papers found by citation
chaining, on data intensity, demand input, equity treatment, validation and planning output (Table 1;
Supplementary Material S1). Forty-six were coded from full text.

## 2.2 Network design and route rationalisation

The transit network design and frequency-setting problem has been reviewed repeatedly
[@guihaire2008transit; @kepaptsoglou2009transit; @ibarrarojas2015planning; @duranmicco2022survey], and its
operational fundamentals are textbook material [@vuchic2005urban; @ceder2016public]. The object
optimised is a route set with frequencies and the objective is defined over passenger flows, so an
origin–destination (OD) matrix is an input. Ten of our 60 coded studies are demonstrated only on benchmark
or synthetic networks with a given OD matrix, most often the Mandl network
[@mandl1980evaluation; @arbex2015efficient; @yoo2023reinforcement]. Real-city route-and-frequency plans exist, for Rome
[@cipriani2012transit], Tin Shui Wai [@szeto2011simultaneous; @szeto2014transit], Miami-Dade
[@zhao2008optimization] and Bangalore [@verma2017development], but each starts from a demand matrix.

Restructuring an inherited network is studied less often. Overlapping Istanbul routes have been altered
inside an assignment model with a 452-zone OD matrix [@ergun2011alteration], and 14 overlapping Bangkok
routes merged using on-board counts [@hoonsiri2020energy]. Duplication can be measured from schedule data
alone, but that work stops at diagnosis [@barzegari2026comprehensive].

## 2.3 Demand estimation and its data requirements

Where demand is not surveyed it is inferred, and the inference consumes passive data: smart-card and
vehicle-location records [@barry2009use; @wang2011bus; @alsger2015use], fare cards with GPS
[@farzin2008constructing], mobile-phone traces [@pinelli2016data; @mittal2025overcoming] or taxi GPS
[@chen2014bplanner]. Even an attempt to predict passenger flows from network properties alone was trained on
fare-collection data [@luo2020can]. These sources presuppose electronic ticketing or operator
instrumentation, which permit-based minibus systems do not have.

## 2.4 Demand-independent and accessibility-based approaches

A second tradition plans against potential rather than realised travel: need indices built from census
variables [@yao2007where], accessibility surfaces [@tribby2012high; @karner2018assessing], and transit-desert
detection that uses no demand data [@carmody2025identifying]. One recent study states the premise plainly,
assuming demand proportional to population [@liu2026quantifying].

Two results from this tradition bear directly on our method, and we claim neither. First, straight-line
buffers overstate catchment population relative to network distance
[@gutierrez2008distance; @biba2010new; @elgeneidy2014new], a bias also shown for Indian cities
[@yenisetty2020measuring]; §4 applies this correction and reports its size for our network. Second, headways
can be set without ridership: frequencies on existing lines in Palma were adjusted from a socio-demographic
need index [@ruiz2017improving]. These studies evaluate networks or set a single service attribute. None
carries the logic through to a fleet.

## 2.5 Open data and planning under scarcity

Open inputs are now adequate for such work, with caveats. Gridded population is modelled, not observed
[@tatem2017worldpop], and OpenStreetMap road completeness, although above 80 % globally, is uneven
[@barringtonleigh2017world]. Schedule feeds support comparable accessibility measurement
[@bok2016comparable; @wessel2019accuracy], and field mapping has produced network data for informal systems
in Nairobi, Maputo and Bogotá [@williams2015digital; @klopp2019mapping; @vergeltovar2023digital], enabling
cross-city comparison [@falchetta2021comparing]. This literature largely stops at representation and
assessment. The exception designs a network for Maputo with WorldPop and OpenStreetMap inputs but relies on
proprietary phone data for demand [@mittal2025overcoming].

## 2.6 Network indicators and equity

Distributional assessment of transit supply is established [@delbosc2011using], and equity has entered
design as an objective or constraint
[@ferguson2012incorporating; @camporeale2017quantifying; @kim2019transit]. Of the 60 coded studies, 42 report
no equity treatment.

## 2.7 Indian and Global South evidence

Indian work is strong on diagnosis [@pucher2005urban; @badami2007analysis] and on accessibility mapping
[@adhvaryu2019mapping]; an early feeder-route design drew on commuter counts at railway stations
[@shrivastava2001development]. In Kumasi, paratransit route inefficiency was shown from field GPS and gridded
population, without a plan being proposed [@dumedah2023inefficient].

The closest study to ours restructures Mexicali's concession network by grouping overlapping routes and
setting headways from a service floor and inherited frequencies, with a travel survey used only for
evaluation [@sanchezatondo2026reorganization]. It does not size a fleet and does not start from a permit
register.

## 2.8 Synthesis: the gap, quantified

Figure 2 cross-tabulates data intensity (1 = open data only; 5 = stop-level passive ridership) against
planning output for the 56 studies that could be coded on both axes. Six produce a full plan, with routes
and frequencies or fleet for a real city, and all six sit at intensity 4: each needs a demand matrix. None
of the 30 studies at intensity 2–3 produces a full plan, although eight deliver part of one. The five
studies at intensity 5 estimate demand and plan nothing, and no coded study operates at intensity 1. The
literature can plan with a demand matrix or describe without one. It rarely plans without one.

The wedge is that most of the planning chain never needed demand. Cycle time depends on distance, speed and
dwell; fleet is cycle time over headway [@vuchic2005urban; @ceder2016public]; coverage depends on geometry
and population. Demand enters at one point, the frequency rule. Replace that rule with policy headway bands
assigned by an ordinal open-data index, and everything downstream is computable without ridership. This is
a decision logic, not a new model. To our knowledge, no study has taken a statutory stage-carriage permit
register through to a tiered, fleet-sized network on this basis, with no origin–destination, ticketing,
passenger-count or mobile-phone data at any stage, and tested whether the resulting decisions are robust to
the index's uncertainty.

---

## Figure and table calls for §2

- **Figure 2 — Data intensity against planning output** (`paper/figures/fig02_gap_heatmap`), n = 56, gap
  region outlined. Generated by `paper/literature_review/finalise_table1.py`.
- **Table 1 — Synthesis matrix of the 60 coded studies** (`paper/tables/table01_synthesis_matrix`). Too long
  for the main text under D26; proposed for Supplementary Material S1, with Figure 2 carrying the finding.

> **[OPEN 2-E — where our own study sits on the scale.]** By the coding rubric the permit register is
> "official static data", so this study is intensity **2**, not 1, and v3.4.5 used app GPS (intensity-3
> data) to correct cycle times on five routes. §2.8 therefore says "ordinal open-data index" and outlines
> the gap as full plans at intensity 1–2. Prashant to confirm this wording against §4.
>
> **[OPEN 2-F — four studies not on both axes.]** C56 (Saleeshya and Anirudh, 2015), C57 (Blum and Mathew,
> 2012), C58 (Mandl, 1980) and C60 (Baaj and Mahmassani, 1991) could not be obtained in full text; they stay
> in Table 1 coded from abstracts with `unclear` fields and are excluded from Figure 2 (hence n = 56).
>
> **[OPEN 2-G — three "full plan" codes rest on method output.]** Cipriani et al. (2012), Zhao and Zeng
> (2008) and Verma et al. (2017) produce routes and frequencies for a real city but print no route-by-route
> table. If "full plan" required a published table they would be Partial, leaving three full plans, all
> still at intensity 4. The finding does not change.
>
> **[OPEN 2-H — novelty wording.]** The novelty check (750 records scored; five closest papers read in full)
> found prior work for every single step of the pipeline. Claims to avoid anywhere in the manuscript: first
> to restructure a legacy network under data scarcity; novel open-data demand proxy; novel overlap
> consolidation; first to set headways without ridership; first route rationalisation in India. See
> `paper/literature_review/03_novelty_check.md` and `04_fulltext_verification.md`.
