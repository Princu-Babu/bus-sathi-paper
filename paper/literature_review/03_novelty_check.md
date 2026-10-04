# 03 — Novelty check: does any published paper already do what this paper does?

**Date:** 2026-10-01 · **Scope:** Kashmir Division permit-register rationalisation pipeline (Transport Policy manuscript)
**Verdict in one line:** No record we reviewed runs the whole chain: a legacy permit register, then an open-data ordinal proxy, then overlap consolidation, then policy-anchored headway tiers, then fleet sized from routing-engine cycle times, then supply-side-only validation. Every *individual* element has prior work, however, and three novelty phrasings would be wrong if used (§B). The novelty claim has to be about the **integration, the institutional object (an Indian stage-carriage permit register) and the demand-free decision logic**. It cannot be about any single technique.

---

## 0. What was reviewed and how

| Pool | Records | Selection |
|---|---|---|
| `scopus_novelty_hits.csv` (6 targeted novelty queries N1–N6) | 359 | all |
| `screened_all.csv` (OpenAlex) | 377 | `queries` contains A_rationalisation / B_data_scarce / B_demand_proxy / B_open_data / C_permit_regulation / C_india / C_global_south **and** decision ∈ {INCLUDE, MAYBE} |
| `novelty_extra_from_screening.csv` (Scopus screeners' flags; added mid-task) | 14 | all (IDs X00–X13) |
| Targeted web searches (WebSearch, 12 queries) | — | close matches outside the databases; each listed hit was checked against a publisher, DOI or OpenAlex record |
| **Total records scored** | **750** | (includes ~20 cross-pool duplicates, e.g. S042 = O1355, S006 = O0349, S309 = O1163, S071 = O0866, O0507 = X12) |

**Scoring.** Each record gets 0–3 on the six pipeline elements:
- **e1** legacy permit/concession/existing-route register as the starting object
- **e2** open-data demand proxy / catchment method (population raster, OSM POIs, network vs Euclidean catchments)
- **e3** overlap-based consolidation / rationalisation
- **e4** headway set by policy/ordinal tiers, not link loads
- **e5** fleet = f(cycle time, headway) from routing-engine times
- **e6** supply-side-only validation, uncertainty analysis, "decision-robust not demand-validated" stance

Shortlist rule (as specified): total ≥ 6 **or** a 3 on e1, e4 or e5. Five records meet the rule. Two of them are the same paper, so there are **4 distinct papers**. I added **10 more papers by judgement** because each is the closest prior work on at least one element, and §2 of the manuscript has to deal with them. The shortlist therefore holds 14 papers plus one grey-literature report.

**Honesty about the appendix scores.** Everyone reading the appendix should know how its numbers were produced:
- 84 records have hand-assigned scores ("manual"): the shortlist plus every record I judged at all related.
- The other 658 transit-related records carry a **keyword-derived floor**: 0/1 per element, from regex hits in the title and abstract ("kw").
- 8 records are off-topic outside transit (e.g. power grids, biology) and are scored 0.

I read every abstract, including all the "kw" ones (many are false-topic hits from generic words like "supply side", "bus" as in electrical bus, or "route overlap" in route-choice logit models). No "kw" record scored above 4, and none came near any element at level 2 or higher on reading. The kw numbers are an audit screen, not a judgement of relatedness.

**Full-text access.** Elsevier/ScienceDirect, MDPI and Springer blocked automated access (HTTP 403 / Cloudflare / login redirect), including for the open-access articles. The "Read" column says exactly what was read. **Nothing below is inferred beyond what was read.** Items marked **⚠ needs full-text check** must be read by someone with a browser or institutional access before the §2 text is finalised.

---

## A. Shortlisted papers (closest prior work)

Scores are e1–e6 / total. "Abstract+" means the abstract plus publisher or indexing snippets returned by web search (quoted facts only).

| # | Citation | Read | e1 | e2 | e3 | e4 | e5 | e6 | Tot | What they do | How this paper differs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Sánchez-Atondo, A., García, L., Gutiérrez-Moreno, J.M., Mungaray-Moctezuma, A., Montoya-Alcaraz, M., Calderón-Ramírez, J. (2026).** Reorganization of public transport systems in Global South cities and its relation with quality of life: A case study of Mexicali, Mexico. *Transportation Research Interdisciplinary Perspectives*. doi:10.1016/j.trip.2026.101859 (S042 = O1355) | Abstract+ (full text blocked) **⚠** | 3 | 1 | 3 | 1 | 1 | 0 | **9** | Four-phase workflow for restructuring a **non-integrated, individual-concession** network in a data-scarce Global South city. Its core is three modules: (i) define trunk routes; (ii) optimise sinuosity, **overlay (overlap)** and route length; (iii) define **frequency and stop points**. It "relies on information obtainable from official sources or generated with minimal effort". The result is **evaluated through modelling** of travel/walk/wait times, disaggregated by quality of life. Web snippets: 41 routes, 936 km, 12 companies, ~75–80% of route-km overlapping. | **Closest paper found. It undermines any "first to restructure a legacy fragmented network under data scarcity" claim.** Differences, as far as the abstract shows: (a) the object is a Mexican concession network, not an Indian stage-carriage permit register, and at city rather than regional scale; (b) evaluation uses a transport model, so it does not take a supply-only / "not demand-validated" stance; (c) there is no stated open raster/POI proxy, no ordinal tiering, no routing-engine fleet derivation and no GPS or Sobol validation. **Unknown until read:** how frequencies are set. If they use service standards, the gap on e4 narrows. |
| 2 | **Ruiz-Pérez, M., Seguí-Pons, J.M., Mateu-Lladó, J. (2017).** Improving Bus Service Levels and social equity through bus frequency modelling. *Journal of Transport Geography* 58, 220–233. doi:10.1016/j.jtrangeo.2016.12.005 (X11) | Abstract+ **⚠** | 2 | 2 | 0 | 2 | 1 | 0 | **7** | Adjusts **headways on existing bus lines** (Palma) using a spreadsheet that joins route geography with **district socio-demographic need** (neighbourhoods, census sections, 400 m mesh). "Small changes in the headways … can significantly enhance service level and social equity"; the fleet is redistributed. | Closest prior work on **e4**: headways set from a need/proxy measure rather than observed loads. Differences: they **optimise/adjust** frequencies against an equity objective, whereas this paper assigns **policy bands by Jenks tier** of an ordinal index. They do not consolidate routes, do not derive fleet from routing-engine cycle times, and do not start from a permit register. Whether ridership enters their objective is **not confirmed from the abstract ⚠**. |
| 3 | **Barzegari, V., Taubkin, G.G., Barsukov, P., Nourinejad, M. (2026).** A comprehensive analysis of duplication in public transportation. *Transportation Research Part A* 104747. doi:10.1016/j.tra.2025.104747 (S024) | Abstract (OpenAlex full abstract) | 2 | 0 | 2 | 1 | 1 | 0 | **6** | Formal definition of route duplication (segment and passenger-connection perspectives, weighted by frequency and vehicle size) on a **multi-operator network (Almaty)**. Recommends shortening under-used segments and reallocating resources. | Pairwise-overlap consolidation is **not new** (see also #6–#9). This paper uses a buffer-share overlap threshold with transitive clustering and trunk selection. That is a simpler and different operationalisation, which should be presented as a pragmatic choice rather than a methodological contribution. Barzegari et al. do not do demand proxying, tiering or fleet sizing. |
| 4 | **Dumedah, G., Abass, K., Gyasi, R.M., Forkuor, J.B., Novignon, J. (2023).** Inefficient allocation of paratransit service terminals and routes in Ghana: The role of driver unions and paratransit operators. *Journal of Transport Geography* 111, 103643. doi:10.1016/j.jtrangeo.2023.103643 (O0352) | Abstract+ (snippet) | 2 | 2 | 2 | 0 | 0 | 0 | **6** | Uses **GTFS-like data of existing paratransit routes** with nearest-neighbour and service-area analysis of **population served** (Oforikrom, Ghana). Finds routes fragmented and that "existing routes can be reduced … by 53%". Links the pattern to union/operator governance. | Close on e1–e3 **as a diagnostic**. It does not produce a rationalised network with tiers, headways or fleet, and does not work from a statutory permit register. Cite as prior evidence that legacy informal and licensed networks can be diagnosed and compressed with low-data GIS methods. |
| 5 | **Mittal, S., Ukkusuri, S.V. (2025).** Overcoming Data Scarcity in Transit Planning: A Novel Framework Combining Machine Learning and Metaheuristics. *Data Science for Transportation*. doi:10.1007/s42421-025-00116-6 (S210) | Abstract+ (Springer snippet) | 0 | 2 | 1 | 0 | 0 | 0 | 3 | Greater Maputo: extracts transit-viable road segments, high-demand stops and routes using **OpenStreetMap roads and POIs, WorldPop population**, Meta Relative Wealth Index **and mobile-phone location data**, via semi-supervised learning, clustering and multi-objective metaheuristics. | **Kills any claim that WorldPop + OSM POIs as a demand signal for bus planning in a data-scarce city is new.** Differences: they design routes from scratch and rely on proprietary phone data as the core demand signal. This paper starts from a legal permit register and uses only open, ordinal data. |
| 6 | **Hassan, M., Mahin, H.D., Ahmed, F., Hassan, M.M., Rahaman, A., et al. (2025).** Assessing Public Transit Network Efficiency and Accessibility in Johor Bahru and Penang, Malaysia: A Data-Driven Approach. *Results in Engineering* 106126. doi:10.1016/j.rineng.2025.106126 (S006 = O0349) | Abstract | 1 | 2 | 1 | 0 | 0 | 0 | 4 | GTFS combined with **OSM POIs, walking-friction surfaces and population-density rasters**, plus centrality, KDE and **Jaccard route similarity**, to assess network efficiency and equity. | Same open-data ingredients (population raster + OSM POIs) but used for **evaluation**, not rationalisation or fleet decisions. |
| 7 | **Liu, J., Rosenberg, E. (2026).** Quantifying the Accessibility to Public Transit in Rural Areas Using ArcGIS and GTFS. *Papers in Applied Geography*. doi:10.1080/23754931.2026.2646852 (S309 = O1163) | Abstract | 1 | 2 | 0 | 0 | 0 | 1 | 4 | "Lacking actual demand data, we assume demand is proportional to population" and build a **supply-side composite index**. | Prior use of the explicit "no demand data, so a population proxy and a supply-side index" stance, for **evaluation** only. Blunts the claim that the stance itself is new. |
| 8 | **Ergun, M., Kesten, A.S. (2011).** Alteration of bus routes in large-scale networks. *Scientific Research and Essays*. doi:10.5897/SRE11.814 (S016) | Abstract | 2 | 0 | 2 | 1 | 0 | 0 | 5 | Istanbul: modifies/shortens existing overlapping routes "without changing the vehicle headway". | Prior overlap-driven alteration of an existing network. It keeps headways fixed and does not use a proxy, tiers or fleet derivation. |
| 9 | **Hoonsiri, C., Kiattikomol, V., Chiarakorn, S. (2020).** Energy Saving and CO2 Reduction Potential from Partial Bus Routes Reduction Model in Bangkok Urban Fringe. *Energies* 13(22), 5963. doi:10.3390/en13225963 (O0872) | Abstract (full abstract via OpenAlex) | 2 | 0 | 2 | 1 | 0 | 0 | 5 | Reduces overlapping partial routes in Bangkok and evaluates waiting-time and fuel/CO2 effects using passenger loads. | Overlap reduction on an existing network, but it is demand-based. |
| 10 | **Mustaqeem, M.N., Jalaluddin, F., Hassan, R. (2018).** Bus Network Coverage Analysis of Dhaka City Along with its Service Quality. (conference paper; no DOI in record) (O0844) | Abstract | 2 | 1 | 2 | 0 | 0 | 0 | 5 | 160 privately operated routes (137 companies) "never the result of any assessment of demand", with heavy overlap; GIS coverage analysis. | Same **problem diagnosis** in a South-Asian licensed-private-bus setting (closest institutional analogue in the pool). It is diagnosis only, with no redesign pipeline. |
| 11 | **Saleeshya, P.G., Anirudh, S. (2015).** A bi-level approach to frequency optimisation of public transport systems. *Int. J. Business Innovation and Research*. doi:10.1504/ijbir.2015.071598 (O0982) | Abstract | 2 | 0 | 0 | 1 | 2 | 0 | 5 | Indian state transport corporation: minimum fleet per existing route at level 1, then load-feasible frequency allocation. | Fleet and frequency on existing Indian routes, but **load-based**. It is the conventional demand-driven counterpart to this paper's demand-free rule. |
| 12 | **Blum, J.J., Mathew, T.V. (2012).** Implications of the computational complexity of transit route network redesign for metaheuristic optimisation systems. *IET Intelligent Transport Systems*. doi:10.1049/iet-its.2011.0021 (O0459) | Abstract (full via OpenAlex) | 2 | 0 | 1 | 1 | 0 | 0 | 4 | Mumbai redesign constrained so that **existing routes remain** (possibly at lower frequency); OD-based utility. | Indian precedent for redesigning around an existing route set. Demand-based. |
| 13 | **Canca, D., Saldanha-da-Gama, F. (2026).** Maximal demand coverage transit network redesign with resource reutilization. *Journal of Transport Geography* 104748. doi:10.1016/j.jtrangeo.2026.104748 (O1336) | Abstract (OpenAlex) | 2 | 0 | 1 | 1 | 1 | 0 | 5 | Redesign of existing bus lines that reuses stops and vehicles, with frequency and fleet size as extensions. Demand-coverage optimisation. | Demand-based optimisation. Relevant only as a redesign-with-fleet precedent. |
| 14 | **Ratriaga, A.R.N. (2026).** GIS-Based Accessibility Analysis for Optimizing Feeder Public Transportation Routes in Surabaya. *IOP Conf. Ser.: Earth Environ. Sci.* 1595, 012010. doi:10.1088/1755-1315/1595/1/012010 (X00, extra file) | Abstract (OpenAlex) | 2 | 2 | 0 | 0 | 0 | 0 | 4 | Coverage of **existing** feeder routes with network analysis and 400 m buffers against population; about 14% of residents served. | Coverage audit of existing routes, the same family as this paper's 35.5% → 24.2% coverage result. No rationalisation, tiers or fleet. |
| G1 | **GIZ SMART-SUT / CRDF CEPT University — KSRTC Thiruvananthapuram city bus route rationalisation** (grey literature; practitioner blog, LinkedIn "Modernising City Bus Services in India … Blog #1", Cheriyan) | Web page read (non-peer-reviewed) | 2 | 0 | 3 | 1 | 0 | 0 | 6 | Indian state transport undertaking (STU) routes: overlap analysis against demand corridors plus OD desire lines and load profiles. **650 → 166 routes**, 8 corridors, 29 trunk routes at 15-minute frequency. | Indian practice already does **overlap-based route rationalisation with trunk routes and 15-minute trunk headways**, but with OD and load data. This paper's difference is doing it **without** OD/ETM data, and on private stage-carriage permits rather than STU schedules. Cite (if at all) as practice context. Do not claim Indian route rationalisation is unprecedented. |

**Other records scored 3–4 on reading, and why they are not closer.** None changes the verdict.
- Iarkov et al. 2026 (Tobolsk duplication, S031), Kasatkina et al. 2022 (Izhevsk duplication, S046), Sembiring et al. 2023 (Medan paratransit overlap GIS, S060), Khemapech & Kidbunjong 2020 (Bangkok overlap cost, O0921) and Zhang & Huang 2011 (Wuhan GA, S020): overlap/duplication diagnosis only.
- Simard et al. 2010 (Waterloo GIS desire-line tools, O0856) and Huang et al. 2010 (GIS+GA from land use/population, O0351): the population/land-use proxy is used to *generate* demand, followed by conventional TNDP.
- Macuchova & Brandt 2025 (rural Sweden, supply-side, grid population; S071/O0866), Devulapalli & Agrawal 2017 (crowd-sourced mapping of Hyderabad routes, O0579) and Choudhary et al. 2026 (Bhopal SDG 11.2.1 with operator stop register + 100 m population + **Euclidean** catchments, O1351): open-data coverage evaluation only.
- Agustin & Fillone 2025 (Iloilo, Philippine LPTRP route-planning guidelines; X02): the LPTRP standards are a *policy-standards* analogue, but the study uses a household survey and EMME assignment.
- Ergül et al. 2026 (supply–demand gap index with POIs, but ridership included; S237) and Mateo-Babiano et al. 2020 (jeepney franchise reform; S256): partial overlaps only.

**Catchment method (element 2).** This was already conceded in `04_LITERATURE_POSITIONING.md` and is confirmed here. Beyond Gutiérrez & García-Palomares (2008), Biba et al. (2010) and El-Geneidy et al. (2014), the pool contains more Euclidean-vs-network work:
- Yenisetty & Bahadure 2020, *IJGI* 9(7):446, doi:10.3390/ijgi9070446: **India**, Euclidean vs OSM network distance.
- Petre et al. 2026, *Transp. Res. Procedia*, doi:10.1016/j.trpro.2026.02.041: route-based vs buffer catchments.
- Nieland et al. 2025 (PtAC), *TRIP*, doi:10.1016/j.trip.2025.101516: SDG 11.2.1 from open population + OSM.

**Kashmir-specific literature.** No route-planning or rationalisation paper was found:
- Peer et al. 2026, *Transp. Res. Procedia*, doi:10.1016/j.trpro.2026.04.063: Srinagar scenario/emissions study using demand modelling.
- Pasha et al. 2020, doi:10.1016/j.trpro.2020.08.245: car-restrictive policies.
- The rest are mode-choice or congestion-pricing surveys (S329, S337, S349, S355, S356).

Grey sources confirm that Srinagar Smart City's e-bus routes were set by an "integrated public transport system plan". No methodology for that plan was found in published literature.

---

## B. Verdict

### (a) Novelty claims that are SAFE to make, each hedged "to our knowledge"

1. **Object.** No study found takes a **statutory Indian stage-carriage permit register** (614 permits + 30 e-bus routes) as the unit of analysis and turns it into a rationalised, tiered, fleet-sized network. Closest: Mexicali concessions (#1), Ghana paratransit (#4), Dhaka licensed routes (#10), KSRTC practice (G1).
2. **Integration.** No study found chains **permit register → OSRM routing → open ordinal proxy (WorldPop + OSM POIs) → overlap consolidation → Jenks tiers → policy-anchored headway bands → fleet = ⌈⌈C/h⌉×1.15⌉ from routing-engine cycle times → supply-side GPS check + Monte Carlo/Sobol' + tier-stability**.
3. **Validation stance.** No study found explicitly frames a rationalisation as **"decision-robust, not demand-validated"**, validating only the supply chain (speeds and cycle times against driver-app GPS) and testing decision stability under uncertainty. Liu & Rosenberg (#7) take a supply-side-only stance, but for evaluation, not for a plan.
4. **Setting.** This is the first published route-rationalisation / fleet-sizing study for **Kashmir Division / Srinagar** we found. Existing Kashmir transport papers are mode choice, pricing or scenario studies.
5. **Finding.** The measured catchment correction is an **empirical result for this network** (37.4% median overstatement; coverage 35.5% → 24.2%) and can be reported as such, **but only as an application of an established critique** (point b-4).

### (b) Claims that are UNSAFE and must be dropped or reworded

| Unsafe phrasing | Prior work that contradicts it |
|---|---|
| "First to rationalise / restructure an existing (legacy, concession, informal) bus network under data scarcity in the Global South" | **Sánchez-Atondo et al. 2026** (#1); Dumedah et al. 2023 (#4) |
| "Novel use of open data (WorldPop/gridded population + OSM POIs) as a demand proxy for bus planning" | **Mittal & Ukkusuri 2025** (#5); Hassan et al. 2025 (#6); Basso et al. 2015/2020 (OSM facilities as demand proxy; LNCS doi:10.1007/978-3-319-26401-1_41 and JUCS doi:10.3217/jucs-025-08-0946); Huang et al. 2010 (O0351); Liu & Rosenberg 2026 (#7) |
| "Novel overlap/duplication-based route consolidation method" | **Barzegari et al. 2026** (#3); Ergun & Kesten 2011 (#8); Hoonsiri et al. 2020 (#9); Iarkov et al. 2026; Kasatkina et al. 2022; Sembiring et al. 2023; KSRTC practice (G1) |
| "First to set bus frequencies without ridership data" / "headways from a proxy index is new" | **Ruiz-Pérez et al. 2017** (#2): headways on existing lines from socio-demographic need. Policy headways are also standard practice (TCQSM service standards). |
| "Network-vs-Euclidean catchment overstatement is a new finding" | Gutiérrez & García-Palomares 2008; Biba et al. 2010; El-Geneidy et al. 2014; Yenisetty & Bahadure 2020 (India) |
| "The demand-free hinge is a new theory/model" | The formula N = ⌈C/h⌉ is textbook (Vuchic 2005; Ceder 2016). Present the hinge as an **explicit articulation of a decision logic**, not a new model. |

### (c) Defensible novelty sentences for §1/§2

> "Methods for restructuring fragmented, concession- or permit-based bus networks in data-scarce cities now exist (Sánchez-Atondo et al., 2026; Dumedah et al., 2023), as do open-data demand proxies (Mittal and Ukkusuri, 2025) and overlap-based duplication measures (Barzegari et al., 2026). To our knowledge, however, no study has taken a statutory stage-carriage permit register as its starting object and carried it through to a tiered, fleet-sized network using only open data, with no origin–destination, ticketing or passenger-count data at any stage."

> "Our contribution is an integration and a decision logic rather than a new technique. Once headways are anchored to policy bands assigned by an ordinal open-data index, fleet size and coverage follow from supply-side quantities alone (routing-engine cycle times and walk-network catchments). The plan can therefore be tested for decision robustness (GPS-checked cycle times, Monte Carlo/Sobol' variance, tier stability) even though it cannot be demand-validated. We are, to our knowledge, the first to state and test this stance explicitly for a route rationalisation."

> "The catchment correction we apply is established (Gutiérrez and García-Palomares, 2008; Biba et al., 2010; El-Geneidy et al., 2014). What we add is its measured consequence at rationalisation scale: a 37.4% median overstatement per route and a fall in network coverage from 35.5% to 24.2%."

### (d) Papers that MUST be cited in §2 as closest prior work

1. Sánchez-Atondo et al. (2026), *TRIP*, doi:10.1016/j.trip.2026.101859. **⚠ Read the full text first**, especially the frequency and stop module and what "evaluated through modelling" used as demand.
2. Ruiz-Pérez, Seguí-Pons & Mateu-Lladó (2017), *J. Transport Geography* 58:220–233, doi:10.1016/j.jtrangeo.2016.12.005. **⚠ Confirm whether ridership enters their objective.**
3. Mittal & Ukkusuri (2025), *Data Science for Transportation*, doi:10.1007/s42421-025-00116-6
4. Barzegari et al. (2026), *Transportation Research Part A*, doi:10.1016/j.tra.2025.104747
5. Dumedah et al. (2023), *J. Transport Geography* 111:103643, doi:10.1016/j.jtrangeo.2023.103643
6. Liu & Rosenberg (2026), *Papers in Applied Geography*, doi:10.1080/23754931.2026.2646852 (demand ∝ population, supply-side stance)
7. Already in `.bib`: Gutiérrez & García-Palomares (2008), Biba et al. (2010) and El-Geneidy et al. (2014). Add Yenisetty & Bahadure (2020) as the Indian Euclidean-vs-network instance.
8. Recommended context: Hassan et al. (2025, doi:10.1016/j.rineng.2025.106126); Saleeshya & Anirudh (2015) and/or Blum & Mathew (2012) as Indian demand-based counterparts; Peer et al. (2026) for Srinagar context.

### Other points for the co-author

- **Public-exposure risk.** A web search ("bus route rationalisation OpenStreetMap WorldPop …") returned the project's **public GitHub repository** (`github.com/Princu-Babu/bus-sathi-paper`), and the search engine's summary reproduced the paper's headline numbers (186 routes, 37.4%, WorldPop, 10 districts). The work is indexed publicly before submission. Check the journal's preprint/anonymity policy; *Transport Policy* reviewing may be double-blind.
- **Unread items.** Nothing here is inferred from unread text. Items marked ⚠ were not read in full because the publishers blocked automated access, and the verdict on them rests on abstracts and publisher/index snippets.
- **Search limits.** The database pools are Scopus (6 novelty queries) and OpenAlex, plus 12 web searches. Google Scholar, Web of Science, TRID and Indian grey literature (UMTA/CMP reports, ITDP/WRI India, GIZ) were **not** systematically searched. Indian practitioner route rationalisation reports (Delhi, Kolkata, Thiruvananthapuram) do exist, so do not claim "first in India" for route rationalisation in general; claim it only for the permit-register + open-data + demand-free combination.

---

## Appendix — every record reviewed, with scores

Columns: ID (S = Scopus novelty hits row; O = OpenAlex screened_all row index; X = extra screening file row), source/query, year, title, DOI, e1–e6, total, basis (manual = scored by hand after reading; kw = keyword floor, abstract read, judged not close; off-topic = outside transit). Sorted by total, descending. Cross-pool duplicates are kept so that each input row can be traced. Web-search-only items (G1, and background items such as the *Nature Communications* 2024 study of self-organising informal transport networks, doi:10.1038/s41467-024-49193-1, read as a search snippet only, not close) are not in this table.

| ID | Source | Year | Title | DOI | e1 | e2 | e3 | e4 | e5 | e6 | Total | Basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O1355 | oa:A_rationalisation;C_global_south | 2026 | Reorganization of public transport systems in Global South cities and its relation with quality of life: A cas | 10.1016/j.trip.2026.101859 | 3 | 1 | 3 | 1 | 1 | 0 | 9 | manual |
| S042 | scopus:N1_rationalisation_all | 2026 | Reorganization of public transport systems in Global South cities and its relation with quality of life: A cas | 10.1016/j.trip.2026.101859 | 3 | 1 | 3 | 1 | 1 | 0 | 9 | manual |
| X11 | extra:P0562 | 2017 | Improving Bus Service Levels and social equity through bus frequency modelling | 10.1016/j.jtrangeo.2016.12.005 | 2 | 2 | 0 | 2 | 1 | 0 | 7 | manual |
| O0352 | oa:B_open_data | 2023 | Inefficient allocation of paratransit service terminals and routes in Ghana: The role of driver unions and par | 10.1016/j.jtrangeo.2023.103643 | 2 | 2 | 2 | 0 | 0 | 0 | 6 | manual |
| S024 | scopus:N1_rationalisation_all | 2026 | A comprehensive analysis of duplication in public transportation | 10.1016/j.tra.2025.104747 | 2 | 0 | 2 | 1 | 1 | 0 | 6 | manual |
| O0844 | oa:A_rationalisation;B_accessibility | 2018 | Bus Network Coverage Analysis of Dhaka City Along with its Service Quality |  | 2 | 1 | 2 | 0 | 0 | 0 | 5 | manual |
| O0872 | oa:C_permit_regulation | 2020 | Energy Saving and CO2 Reduction Potential from Partial Bus Routes Reduction Model in Bangkok Urban Fringe | 10.3390/en13225963 | 2 | 0 | 2 | 1 | 0 | 0 | 5 | manual |
| O0982 | oa:A_core_design;C_india | 2015 | A bi-level approach to frequency optimisation of public transport systems | 10.1504/ijbir.2015.071598 | 2 | 0 | 0 | 1 | 2 | 0 | 5 | manual |
| O1336 | oa:A_rationalisation | 2026 | Maximal demand coverage transit network redesign with resource reutilization | 10.1016/j.jtrangeo.2026.104748 | 2 | 0 | 1 | 1 | 1 | 0 | 5 | manual |
| S016 | scopus:N1_rationalisation_all | 2011 | Alteration of bus routes in large-scale networks | 10.5897/SRE11.814 | 2 | 0 | 2 | 1 | 0 | 0 | 5 | manual |
| O0349 | oa:B_open_data;B_equity | 2025 | Assessing Public Transit Network Efficiency and Accessibility in Johor Bahru and Penang, Malaysia: A Data-Driv | 10.1016/j.rineng.2025.106126 | 1 | 2 | 1 | 0 | 0 | 0 | 4 | manual |
| O0459 | oa:A_core_design;A_rationalisation;C_ind | 2012 | Implications of the computational complexity of transit route network redesign for metaheuristic optimisation  | 10.1049/iet-its.2011.0021 | 2 | 0 | 1 | 1 | 0 | 0 | 4 | manual |
| O0856 | oa:A_core_design;A_freq_fleet;AB_demand_ | 2010 | Development and Deployment of GIS Tools to Facilitate Transit Network Design and Operational Evaluation |  | 0 | 2 | 0 | 1 | 1 | 0 | 4 | manual |
| O0866 | oa:B_open_data | 2025 | Public transport supply in rural Sweden: Examining distribution through the lens of equity | 10.1016/j.jrurstud.2025.103887 | 1 | 2 | 0 | 0 | 0 | 1 | 4 | manual |
| O0921 | oa:C_global_south | 2020 | Analysis of Excessive Cost of Overlapped Bus Route System in Bangkok | 10.13140/rg.2.2.33793.68962 | 2 | 0 | 2 | 0 | 0 | 0 | 4 | manual |
| O1163 | oa:B_open_data | 2026 | Quantifying the Accessibility to Public Transit in Rural Areas Using ArcGIS and GTFS | 10.1080/23754931.2026.2646852 | 1 | 2 | 0 | 0 | 0 | 1 | 4 | manual |
| O1313 | oa:B_data_scarce | 2026 | Plan Now, Ride Later: Simulation-Based Fleet Optimisation and Inclusive Service Design for Cities | 10.48494/realcorp2026.2090 | 0 | 1 | 0 | 1 | 1 | 1 | 4 | kw |
| O1437 | oa:A_core_design;A_rationalisation;B_acc | 2026 | A decision-support framework for evaluating bus network design: Machine learning classification and two-stage  | 10.1016/j.cie.2026.112322 | 0 | 1 | 1 | 1 | 0 | 1 | 4 | kw |
| S006 | scopus:N1_rationalisation_all | 2025 | Assessing Public Transit Network Efficiency and Accessibility in Johor Bahru and Penang, Malaysia: A Data-Driv | 10.1016/j.rineng.2025.106126 | 1 | 2 | 1 | 0 | 0 | 0 | 4 | manual |
| S020 | scopus:N1_rationalisation_all | 2011 | Evaluation and optimization of bus route network in Wuhan China | 10.1049/cp.2011.1392 | 1 | 1 | 2 | 0 | 0 | 0 | 4 | manual |
| S031 | scopus:N1_rationalisation_all | 2026 | On the uniqueness and duplication of bus routes in the urban transport infrastructure | 10.1117/12.3109587 | 2 | 0 | 2 | 0 | 0 | 0 | 4 | manual |
| S046 | scopus:N1_rationalisation_all | 2022 | Optimization of the Public Transport System Using Data Analysis Methods | 10.1109/SUMMA57301.2022.9974076 | 2 | 0 | 2 | 0 | 0 | 0 | 4 | manual |
| S060 | scopus:N1_rationalisation_all | 2023 | Mapping the overlapping paratransit route in Medan City using GIS | 10.1088/1742-6596/2421/1/012031 | 2 | 0 | 2 | 0 | 0 | 0 | 4 | manual |
| S071 | scopus:N2_demand_free | 2025 | Public transport supply in rural Sweden: Examining distribution through the lens of equity | 10.1016/j.jrurstud.2025.103887 | 1 | 2 | 0 | 0 | 0 | 1 | 4 | manual |
| S309 | scopus:N5_proxy_headway | 2026 | Quantifying the Accessibility to Public Transit in Rural Areas Using ArcGIS and GTFS | 10.1080/23754931.2026.2646852 | 1 | 2 | 0 | 0 | 0 | 1 | 4 | manual |
| X00 | extra:P0049 | 2026 | GIS-Based Accessibility Analysis for Optimizing Feeder Public Transportation Routes in Surabaya | 10.1088/1755-1315/1595/1/012010 | 2 | 2 | 0 | 0 | 0 | 0 | 4 | manual |
| X02 | extra:P0096 | 2025 | Assessment of Inter-municipal Public Transport Services in Southern Iloilo, Philippines | 10.1016/j.trpro.2024.12.101 | 2 | 0 | 1 | 1 | 0 | 0 | 4 | manual |
| O0127 | oa:B_data_scarce;B_open_data | 2021 | Comparing paratransit in seven major African cities: An accessibility and network analysis | 10.1016/j.jtrangeo.2021.103131 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | manual |
| O0162 | oa:A_core_design;A_rationalisation;A_fre | 2019 | Joint Design of Multimodal Transit Networks and Shared Autonomous Mobility Fleets | 10.1016/j.trpro.2019.05.007 | 0 | 0 | 1 | 1 | 1 | 0 | 3 | kw |
| O0205 | oa:A_rationalisation;B_accessibility;C_i | 2019 | Improvement in direct bus services through route planning | 10.1016/j.tranpol.2019.07.001 | 2 | 0 | 1 | 0 | 0 | 0 | 3 | manual |
| O0351 | oa:B_accessibility;B_demand_proxy | 2010 | A GIS-based framework for bus network optimization using genetic algorithm | 10.1080/19475683.2010.513152 | 0 | 2 | 1 | 0 | 0 | 0 | 3 | manual |
| O0365 | oa:A_freq_fleet;C_global_south | 2022 | A data-driven system for cooperative-bus route planning based on generative adversarial network and metric lea | 10.1007/s10479-022-04842-w | 0 | 0 | 0 | 1 | 1 | 1 | 3 | kw |
| O0484 | oa:C_india;C_global_south | 2024 | A tactical planning framework to integrate paratransit with formal public transport systems | 10.1016/j.trd.2024.104438 | 1 | 0 | 0 | 1 | 1 | 0 | 3 | manual |
| O0497 | oa:C_global_south | 2020 | Public Bus Accessibility and its Implications in Energy and Environment: A Case Study of Kathmandu Valley | 10.3126/jie.v15i3.32190 | 1 | 1 | 0 | 0 | 1 | 0 | 3 | kw |
| O0579 | oa:C_india;C_global_south | 2017 | Mapping bus transit services in Hyderabad – an illustrative example of the use of open geospatial data | 10.1016/j.trpro.2017.05.369 | 2 | 1 | 0 | 0 | 0 | 0 | 3 | manual |
| O0589 | oa:B_open_data | 2024 | GTFS Segments: A Fast and Efficient Library to Generate Bus Stop Spacings | 10.21105/joss.06306 | 0 | 1 | 0 | 1 | 0 | 1 | 3 | kw |
| O0630 | oa:A_core_design;A_freq_fleet;B_accessib | 2017 | Using accessibility measures in transit network design | 10.3846/16484142.2017.1295401 | 0 | 1 | 0 | 1 | 1 | 0 | 3 | kw |
| O0675 | oa:C_india | 2020 | Demand-Based Model for Line Planning in Public Transport | 10.1016/j.trpro.2020.08.252 | 1 | 1 | 0 | 1 | 0 | 0 | 3 | kw |
| O1021 | oa:C_india | 2025 | Design and implementation of a network-aware automated bus scheduling system for optimizing operational effici | 10.1016/j.cstp.2025.101448 | 1 | 0 | 1 | 1 | 0 | 0 | 3 | kw |
| O1053 | oa:A_rationalisation;B_equity | 2023 | Leveraging Location-Based Services Data to Optimize Generation of High-Demand and Equitable Bus Network Option | 10.1177/03611981231180202 | 1 | 1 | 1 | 0 | 0 | 0 | 3 | manual |
| O1153 | oa:B_open_data;B_accessibility | 2025 | Multicriteria Assessment of Transit Accessibility: Accounting for Criterion and Spatial Interdependence | 10.1080/24694452.2025.2589316 | 0 | 1 | 0 | 1 | 0 | 1 | 3 | kw |
| O1333 | oa:A_rationalisation | 2013 | Evaluation of the Denver RTD Route Restructuring Project | 10.21949/1526687 | 1 | 1 | 1 | 0 | 0 | 0 | 3 | kw |
| O1351 | oa:C_india | 2026 | Who Can Reach a Service? Zone-Level Measurement of Convenient Access to Public Transport in Bhopal, India | 10.9734/ajgr/2026/v9i4465 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | manual |
| O1498 | oa:B_open_data | 2012 | Using open source transit timetable databases in transport model development |  | 1 | 0 | 0 | 1 | 0 | 1 | 3 | kw |
| S021 | scopus:N1_rationalisation_all | 2026 | Enhancing Public Transport Reliability in Indian Cities Through GPS-Based Trip Validation in Intelligent Trans | 10.1007/s40031-026-01331-7 | 0 | 1 | 1 | 0 | 0 | 1 | 3 | kw |
| S045 | scopus:N1_rationalisation_all | 2020 | A new method to measure the rationalities of transit route layouts | 10.1016/j.cstp.2020.11.002 | 2 | 0 | 1 | 0 | 0 | 0 | 3 | manual |
| S053 | scopus:N1_rationalisation_all | 2025 | Synchronization in bus systems with partially overlapping routes | 10.1103/39cy-mztc | 0 | 1 | 1 | 0 | 0 | 1 | 3 | kw |
| S075 | scopus:N2_demand_free | 2026 | Schedule-Aware Transit Service Intensity and Urban Equity in the Greater Toronto Area | 10.3390/urbansci10060309 | 0 | 1 | 1 | 0 | 0 | 1 | 3 | kw |
| S161 | scopus:N2_demand_free | 2026 | AdaptiMOD: A Hybrid Deep Learning and Multi-Agent Reinforcement Learning Framework for Sustainable Multimodal  | 10.1109/B-HTC67770.2026.11502222 | 1 | 1 | 0 | 0 | 0 | 1 | 3 | kw |
| S210 | scopus:N2_demand_free | 2025 | Overcoming Data Scarcity in Transit Planning: A Novel Framework Combining Machine Learning and Metaheuristics | 10.1007/s42421-025-00116-6 | 0 | 2 | 1 | 0 | 0 | 0 | 3 | manual |
| S237 | scopus:N3_open_fleet;N5_proxy_headway | 2026 | A GIS-based methodology to assess bus public transit supply-demand gaps | 10.1016/j.cstp.2026.101750 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | manual |
| S240 | scopus:N3_open_fleet | 2023 | Innovative Discrete Event Simulation With GPS Assistance for Bus Route 45 Scheduling in Seattle, WA | 10.1109/R10-HTC57504.2023.10461879 | 0 | 1 | 0 | 0 | 1 | 1 | 3 | kw |
| S256 | scopus:N4_permit_reform | 2020 | Formalising the jeepney industry in the Philippines – A confirmatory thematic analysis of key transitionary is | 10.1016/j.retrec.2020.100839 | 2 | 0 | 1 | 0 | 0 | 0 | 3 | manual |
| S279 | scopus:N5_proxy_headway | 2019 | Controlling for endogeneity between bus headway and bus ridership: A case study of the Orlando region | 10.1016/j.tranpol.2019.07.004 | 0 | 1 | 0 | 1 | 0 | 1 | 3 | kw |
| S310 | scopus:N5_proxy_headway | 2018 | A demand and capacity analysis on bus semirapid transit network (Case: Jabodetabek public transport network) | 10.1051/matecconf/201818110001 | 1 | 0 | 0 | 1 | 0 | 1 | 3 | kw |
| X08 | extra:P0341 | 2021 | Research on Layered Planning of Tourism Bus Network Based on TOD Concepte: A Case of the Tourism Bus of Guilin | 10.1145/3512576.3512658 | 0 | 2 | 0 | 1 | 0 | 0 | 3 | manual |
| X13 | extra:P0743 | 2016 | Analysing and designing automated and dynamic bus route allocation | 10.1109/ICCTICT.2016.7514587 | 1 | 1 | 1 | 0 | 0 | 0 | 3 | manual |
| O0058 | oa:C_india | 2016 | Informal public transport modes in India: A case study of five city regions | 10.1016/j.iatssr.2016.01.001 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0076 | oa:C_global_south | 2019 | Mapping minibuses in Maputo and Nairobi: engaging paratransit in transportation planning in African cities | 10.1080/01441647.2019.1598513 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0105 | oa:B_open_data | 2019 | On the accuracy of schedule-based GTFS for measuring accessibility | 10.5198/jtlu.2019.1502 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0106 | oa:B_open_data | 2019 | Modelling geographic accessibility to Primary Health Care Facilities: combining open data and geospatial analy | 10.1080/10095020.2019.1645508 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0116 | oa:A_rationalisation;B_equity | 2011 | Bi-Level Optimization Model for Public Transportation Network Redesign Problem | 10.3141/2263-17 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| O0122 | oa:B_open_data | 2018 | A multi-modal relative spatial access assessment approach to measure spatial accessibility to primary care pro | 10.1186/s12942-018-0153-9 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0128 | oa:C_india | 2014 | Differences between the Perceptions of Captive and Choice Riders toward Bus Service Attributes and the Need fo | 10.1061/(asce)up.1943-5444.0000205 | 0 | 0 | 0 | 1 | 1 | 0 | 2 | kw |
| O0180 | oa:B_open_data;B_equity | 2023 | MaaS for the masses: Potential transit accessibility gains and required policies under Mobility-as-a-Service | 10.1016/j.multra.2023.100086 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0182 | oa:C_india | 2016 | Public Transport Accessibility Levels for Ahmedabad, India | 10.5038/2375-0901.19.3.2 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0183 | oa:B_accessibility;C_permit_regulation | 2017 | Accessibility, Affordability, and Addressing Informal Services in Bus Reform: Lessons from Bogotá, Colombia | 10.3141/2634-06 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| O0228 | oa:B_open_data | 2020 | Measuring the Sustainable Development Goal (SDG) Transport Target and Accessibility of Nairobi’s Matatus | 10.1177/0361198120914620 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0233 | oa:C_india | 2018 | Examining Travel Time Reliability-Based Performance Indicators for Bus Routes Using GPS-Based Bus Trajectory D | 10.1061/jtepbs.0000109 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0274 | oa:C_india;C_global_south | 2020 | Efficiency Based Evaluation of Public Transport and Paratransit Systems with a View to Integrating Transportat | 10.1177/0361198120980322 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0318 | oa:C_global_south | 2015 | Adapting the Swedish Service Route Model to Suburban Transit in the United States | 10.3141/2536-07 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0340 | oa:B_open_data | 2020 | Measuring Accessibility to Various ASFs from Public Transit using Spatial Distance Measures in Indian Cities | 10.3390/ijgi9070446 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O0364 | oa:C_india | 2018 | Multimodal data modeling for efficiency assessment of social priority based urban bus route transportation sys | 10.1007/s11042-018-6147-6 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | manual |
| O0461 | oa:B_open_data | 2017 | Transit Trip Itinerary Inference with GTFS and Smartphone Data | 10.3141/2652-07 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| O0501 | oa:B_open_data;B_accessibility | 2022 | Whose express access? Assessing the equity implications of bus express routes in Montreal, Canada | 10.5198/jtlu.2022.1879 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0502 | oa:B_open_data | 2025 | From Raw GPS to GTFS: A Real-World Open Dataset for Bus Travel Time Prediction | 10.3390/data10080119 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| O0503 | oa:B_open_data | 2017 | Challenges of Open Data Quality | 10.1145/3110291 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0507 | oa:B_open_data | 2020 | Planning of Urban Public Transportation Networks in a Smart City | 10.3217/jucs-025-08-0946 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O0519 | oa:B_open_data | 2023 | TRansit ACessibility Tool (TRACT): Developing a novel scoring system for public transportation system accessib | 10.1016/j.jth.2023.101742 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0545 | oa:A_freq_fleet;B_demand_proxy | 2016 | Implementation of Bus Rapid Transit (BRT) on an optimal segment of a long regular bus route | 10.1080/12265934.2015.1133317 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0565 | oa:B_open_data;B_accessibility | 2019 | Practical Framework for Benchmarking and Impact Evaluation of Public Transportation Infrastructure: Case of Be | 10.1177/0361198119835528 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0612 | oa:C_global_south | 2012 | Planning of Fixed-Route Fixed-Schedule Feeder Service to Bus Stops in Rural India | 10.1061/(asce)te.1943-5436.0000419 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0655 | oa:B_accessibility;C_global_south | 2024 | Measuring access distance and geographic catchment areas for the bus rapid transit interchange from a longitud | 10.1016/j.cstp.2024.101189 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0660 | oa:B_od_estimation;B_open_data | 2025 | Data analytics to advance the inference of origin–destination in public transport systems: tracing network vul | 10.1186/s12544-025-00720-1 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0681 | oa:C_permit_regulation | 2005 | Competition or Complementarity: Regulatory Options for Urban Road Transit in Brazilian Cities |  | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| O0693 | oa:B_data_scarce;C_global_south | 2024 | Studying transfers in informal transport networks using volunteered GPS data | 10.1016/j.tbs.2024.100936 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| O0754 | oa:B_open_data | 2020 | Evaluation of public transport policy formulation and implementation: Case study of 24 mid-sized Nordic cities | 10.1016/j.trpro.2020.02.068 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | kw |
| O0796 | oa:C_permit_regulation | 2024 | Risk mitigation in urban bus concession contracts: Overcoming uncertainties with a real options model | 10.1016/j.tranpol.2024.05.027 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | kw |
| O0813 | oa:C_global_south | 2012 | Challenges and Opportunities for the Integration of Commuter Minibus Operators into the Dar es Salaam City BRT |  | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0847 | oa:B_open_data | 2023 | Framework for the Analysis and Enhancement of the Accessibility of Large-Scale Urban Transit Networks: A Data- | 10.1177/03611981231172939 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O0852 | oa:B_open_data | 2025 | Designing transit routes based on vehicle routing behavior determined through location-based services data | 10.1140/epjds/s13688-025-00559-5 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0879 | oa:C_permit_regulation | 2013 | Marknadsöppning – och sen?: samhällsekonomisk analys av förutsättningarna för en stärkt kollektivtrafik |  | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O0936 | oa:B_open_data;B_equity | 2015 | Development of Highly Resolved Spatial and Temporal Metrics of Public Transit Accessibility and Their Applicat |  | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O0954 | oa:C_india | 2020 | Travel Probability Fields – An approach to understand travel behavior: Case study of slum dwellers in Kolkata, | 10.1016/j.trpro.2020.08.197 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O0975 | oa:B_open_data | 2025 | Modal Accessibility Gap in Curitiba (Brazil). Dynamic Analysis Considering Time and Spatial Variations | 10.1007/s12061-025-09639-5 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1005 | oa:B_open_data | 2022 | GIS based methodology to analyse the public transport supply: Hungarian case studies | 10.5937/gp26-36423 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1010 | oa:B_open_data | 2026 | An Open-Source System for Public Transport Route Data Curation Using OpenTripPlanner in Australia | 10.3390/computers15010058 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1017 | oa:A_rationalisation | 2023 | Optimization and Simulation of Public Transportation Systems to Reduce Inequality in Urban Mobility Access | 10.52783/anvi.v24.5723 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O1019 | oa:C_india | 2022 | Analysis and Visulization of Public Transport for Integrated monitoring dashboard : Case Study of Thane, Mahar | 10.46300/9101.2022.16.25 | 0 | 1 | 0 | 0 | 1 | 0 | 2 | kw |
| O1022 | oa:A_rationalisation | 2018 | Generic bus route simulation model and its application to a new bus network development for Caieiras City, Bra | 10.5555/3320516.3320537 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| O1037 | oa:B_open_data | 2021 | Measuring regional accessibility with public transport – case of Koroška region, Slovenia | 10.31075/pis.67.04.07 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1052 | oa:C_india | 2020 | Assessing impact of occupancy, revenue and expenditure patterns on public bus transit system | 10.5958/2321-2136.2020.00005.3 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1099 | oa:C_india | 2025 | Detecting Transit Deserts Through a Blend of Machine Learning (ML) Approaches, Including Decision Trees (DTs), | 10.3390/futuretransp5020070 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1112 | oa:B_demand_proxy | 2022 | EQUITY OF TRANSIT NEED IN BAGHDAD CITY | 10.20858/tp.2022.17.1.03 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O1117 | oa:B_demand_proxy;B_equity | 2001 | Transport and Urban Planning in Curitiba | 10.1080/02513625.2001.10556783 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1140 | oa:B_open_data | 2023 | Role discovery in node-attributed public transportation networks: the model description | 10.17586/2226-1494-2023-23-2-340-351 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O1148 | oa:C_permit_regulation | 2018 | Review of Sustainability of Use Effectiveness City Bus Stopin Surakarta Region | 10.24247/ijcseierdec20182 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1156 | oa:B_open_data | 2021 | Measuring regional accessibility with public transport – case of Koroška region, Slovenia | 10.31075/67.04.07 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1161 | oa:B_open_data | 2026 | Equity-Oriented Public Transport Accessibility Analysis Using GTFS, Spatial Proximity, and Demographic Sensiti | 10.3390/su18094506 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O1166 | oa:B_demand_proxy | 2013 | SEQ Bus Network Review: the network planning approach |  | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| O1228 | oa:B_demand_proxy | 2019 | RANKING NODES IN COMPLEX NETWORKS: A CASE STUDY OF THE GAUBUS | 10.5194/isprs-archives-xlii-2-w13-1333-2019 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O1294 | oa:B_accessibility;B_demand_proxy | 2026 | Urban Bus Route Planning Method Integrating Heuristic and Non-Dominated Sorting Algorithms—A Case Study of Kun | 10.3390/app16073153 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O1315 | oa:B_data_scarce | 2026 | Spatial optimization of bus stop locations using gis and an integrated accessibility index in addis ababa Ethi | 10.1007/s44327-026-00287-z | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O1319 | oa:B_data_scarce | 2026 | EVALUATING THE QUALITY OF PUBLIC TRANSPORT SERVICE IN AL-RASHEED MUNICIPALITY, BAGHDAD | 10.30572/2018/kje/170322 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | kw |
| O1322 | oa:A_rationalisation | 2013 | Maintaining Key Services While Retaining Core Values: NYC Transit’s Environmental Justice Strategies | 10.5038/2375-0901.16.1.7 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O1323 | oa:A_rationalisation | 2012 | Maintaining Key Transit Services While Retaining National Core Values: New York City Transit’s Title VI and En |  | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O1346 | oa:C_india | 2019 | Rationalizing Urban Transportation using Smart Card Data | 10.35940/ijitee.k1086.09811s19 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| O1379 | oa:B_open_data | 2026 | Measuring Inter-Stop Distances to Improve Scheduling, Costing, and Enhance Sustainable Urban Mobility | 10.3390/su18020556 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | kw |
| O1496 | oa:B_open_data | 2019 | Measurement of effective transit supply index between OD pairs |  | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O1499 | oa:B_open_data | 2025 | Gtfswizard: a set of tools for exploring and manipulating general transit feed specification in R language | 10.55905/revconv.18n.1-197 | 0 | 0 | 0 | 1 | 1 | 0 | 2 | kw |
| O1500 | oa:B_open_data | 2025 | Introducing PtAC – an open source tool to assess SDG 11.2 using open data | 10.1016/j.trip.2025.101516 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O1528 | oa:B_open_data | 2011 | “Go_Sync- A Framework To Synchronize Mapping Contributions From Online Communities And Transit Agency Bus Stop |  | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1539 | oa:B_open_data | 2026 | Assessment of transit stop accessibility and usage potential using detailed synthetic populations | 10.1016/j.trpro.2026.02.041 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O1552 | oa:C_global_south | 2026 | Dar es Salaam’s Bus-Rapid-Transit system in view of systemic criticality | 10.1016/j.trip.2025.101824 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1554 | oa:C_global_south | 2025 | An Optimized Graph Based Implementation for Efficient Journey Planning with Public Transport in Kathmandu Vall | 10.3126/injet.v2i2.78657 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| O1571 | oa:C_global_south | 2026 | Review of sustainable public transport alternatives in low- and middle income cities | 10.1007/s42452-026-09635-5 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| O1572 | oa:C_global_south | 2023 | Study of Paratransit Transport Tragel Model as a Feeder in Tamalanrea District, Makassar City | 10.32996/jmcie.2023.4.3.2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| O1576 | oa:C_global_south | 2024 | EVALUATING THE TIME AND COST EFFICIENCY OF PUBLIC TRANSPORT SYSTEM IN DELHI | 10.29121/shodhkosh.v5.iicomabe.2024.2256 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| S000 | scopus:N1_rationalisation_all | 2022 | Multi-class hazmat distribution network design with inventory and superimposed risks | 10.1016/j.tre.2022.102693 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S001 | scopus:N1_rationalisation_all | 2018 | Inside the endometrial cell signaling subway: Mind the gap(s) | 10.3390/ijms19092477 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S003 | scopus:N1_rationalisation_all | 2026 | From Metrics to Decisions: Interpreting Route Deviation and Service Quality Indices in Public Transport Planni | 10.1109/SCSP69985.2026.11548643 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S004 | scopus:N1_rationalisation_all | 2014 | A maximum entropy fixed-point route choice model for route correlation | 10.3390/e16073635 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S007 | scopus:N1_rationalisation_all | 2026 | GIS-based public transport network optimization in UNESCO World Heritage cities in the example of Bukhara, Uzb | 10.3389/frsc.2026.1782977 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S010 | scopus:N1_rationalisation_all | 2022 | Power System Flexibility Improvement and Loss Reduction Using Optimal Restructuring of Transmission Network | 10.1109/ICEEICT53079.2022.9768463 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S011 | scopus:N1_rationalisation_all | 2026 | Gravitational Search Algorithm Based Optimal Position of DG and Capacitor with Restructuring | 10.1007/978-3-032-00884-8_18 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S022 | scopus:N1_rationalisation_all | 2026 | A new recourse algorithm for school bus routing with overlapped routes and process flexibility | 10.1080/15472450.2025.2487808 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S029 | scopus:N1_rationalisation_all | 2020 | Bus Scheduling of Overlapping Routes with Multi-Vehicle Types Based on Passenger OD Data | 10.1109/ACCESS.2019.2961930 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S030 | scopus:N1_rationalisation_all | 2020 | Mixed Scheduling Strategy for High Frequency Bus Routes with Common Stops | 10.1109/ACCESS.2020.2974740 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | kw |
| S032 | scopus:N1_rationalisation_all | 2013 | Maintaining key services while retaining core values: NYC transit's environmental justice strategies | 10.5038/2375-0901.16.1.7 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S033 | scopus:N1_rationalisation_all | 2025 | Presenting a stochastic framework for resilient self-healing active distribution networks with integrated dist | 10.17531/ein/202095 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S037 | scopus:N1_rationalisation_all | 2022 | Modeling the capacity of multimodal and intermodal urban transportation networks that incorporate emerging tra | 10.1016/j.tre.2022.102937 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S039 | scopus:N1_rationalisation_all | 2025 | Enhancing Distribution System Flexibility through Network Restructuring and Optimal Planning of Distributed En | 10.17531/ein/196065 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S040 | scopus:N1_rationalisation_all | 2020 | Weighted complex networks in urban public transportation: Modeling and testing | 10.1016/j.physa.2019.123498 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S044 | scopus:N1_rationalisation_all | 2023 | Reliability evaluation of distribution network for educational purpose: An analytical approach to results anal | 10.1016/j.prime.2023.100343 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | kw |
| S047 | scopus:N1_rationalisation_all | 2010 | City wide bus network restructuring using an inclusive planning approach |  | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| S052 | scopus:N1_rationalisation_all | 2020 | Topological properties of bus transit networks considering demand and service utilization weight measures | 10.1016/j.physa.2020.124683 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S054 | scopus:N1_rationalisation_all | 2016 | Assessing the potential of bus rapid transit-led network restructuring for enhancing affordable access to empl | 10.1016/j.retrec.2016.05.006 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| S055 | scopus:N1_rationalisation_all | 2026 | Customized bus network for efficient service: design of modular vehicle transfer scheme | 10.1080/21680566.2026.2683399 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S057 | scopus:N1_rationalisation_all | 2024 | Maximum capture problem based on paired combinatorial weibit model to determine park-and-ride facility locatio | 10.1016/j.trb.2023.102855 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S058 | scopus:N1_rationalisation_all | 2024 | Identification and Mitigation of Weak Points in an Electrical Network for Optimal Solar PV Power Integration | 10.1109/MNE3SD63831.2024.10812154 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S059 | scopus:N1_rationalisation_all | 2021 | Battery electric bus network: Efficient design and cost comparison of different powertrains | 10.3390/su13094745 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S062 | scopus:N1_rationalisation_all | 2010 | Inclusive planning process for citywide bus network restructuring: Experience and impacts | 10.3141/2145-03 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| S063 | scopus:N2_demand_free | 2026 | A Small Signal Stability Evaluation Model of Power Systems Based on Lightweight CNN-BiLSTM Hybrid Network | 10.1109/EPSIC70071.2026.11590027 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S070 | scopus:N2_demand_free | 2022 | Flexible Integrated Transport Systems’ Potential to Unleash Net Benefits in Rural Areas | 10.1007/978-981-16-7160-9_164 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | kw |
| S076 | scopus:N2_demand_free | 2017 | Urban development control based on transportation carrying capacity | 10.1088/1755-1315/70/1/012019 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| S080 | scopus:N2_demand_free | 2026 | Analysing power system cascading failures and service disruptions in a data-scarce environment: A case study o | 10.1016/j.ress.2026.112575 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S091 | scopus:N2_demand_free | 2021 | Agent-Based Optimizing Match between Passenger Demand and Service Supply for Urban Rail Transit Network with N | 10.1109/ACCESS.2021.3060816 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S092 | scopus:N2_demand_free | 2020 | Can multi-modal integration provide enhanced public transport service provision to address the needs of vulner | 10.1016/j.retrec.2020.100954 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S113 | scopus:N2_demand_free | 2025 | Development, practical challenges, and application of a state-wide transport model system in Australia | 10.1080/03081060.2024.2367757 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S123 | scopus:N2_demand_free | 2014 | Reliability assessment of incentive- and priced-based demand response programs in restructured power systems | 10.1016/j.ijepes.2013.10.007 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | kw |
| S125 | scopus:N2_demand_free | 2026 | Aligning transit provision with urban morphology: A diagnostic assessment of Porto and Cagliari | 10.1016/j.cities.2026.107306 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| S133 | scopus:N2_demand_free | 2022 | A framework for selecting bus priority system locations in medium-sized cities: Case study in Araraquara, Braz | 10.1016/j.cstp.2022.09.006 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| S139 | scopus:N2_demand_free | 2017 | Assessing the spatial equity of Seoul’s public transportation using the Gini coefficient based on its accessib | 10.1080/12265934.2016.1235487 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S142 | scopus:N2_demand_free | 2026 | Urban mobility and CO₂ reduction in Maiduguri, Nigeria: Integrating random utility mode choice modelling with  | 10.1016/j.aftran.2026.100123 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | kw |
| S143 | scopus:N2_demand_free | 2023 | Bi-objective robust planning model for optimal allocation of soft open points in active distribution network:  | 10.1016/j.epsr.2023.109780 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S144 | scopus:N2_demand_free | 2023 | A Comprehensive Analysis of Load Shedding with DSM in a Power Grid with IEEE 14 Bus System Adoption of Chittag | 10.1109/ECCE57851.2023.10101510 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S146 | scopus:N2_demand_free | 2026 | Mapping service disruptions and transit user adaptive behaviour: A systematic literature review | 10.1016/j.urbmob.2026.100213 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| S150 | scopus:N2_demand_free | 2025 | Transit Operational Assessment with Modified Level of Service-Based Measures | 10.1007/978-981-96-8114-3_11 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| S154 | scopus:N2_demand_free | 2025 | Assessing pedestrian crash risks and safety perceptions using video analytics at High-Risk Intersections in In | 10.1016/j.trpro.2025.12.103 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S158 | scopus:N2_demand_free | 2021 | Integrated Model for Timetabling and Circulation Planning on an Urban Rail Transit Line: a Coupled Network-Bas | 10.1007/s11067-021-09525-w | 0 | 0 | 0 | 1 | 1 | 0 | 2 | kw |
| S164 | scopus:N2_demand_free | 2023 | Probabilistic optimal power allocation of dispatchable DGs and energy storage units in a reconfigurable grid-c | 10.1016/j.est.2023.108207 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S165 | scopus:N2_demand_free | 2020 | Predicting peak load of bus routes with supply optimization and scaled Shepard interpolation: A newsvendor mod | 10.1016/j.tre.2020.102041 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S176 | scopus:N2_demand_free | 2025 | Studying transfers in informal transport networks using volunteered GPS data | 10.1016/j.tbs.2024.100936 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| S177 | scopus:N2_demand_free | 2026 | MAP: Mapping accessibility for ethically informed urban planning | 10.1177/23998083251387382 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S182 | scopus:N2_demand_free | 2026 | Commuter bus accessibility evaluation in metropolitan area considering social equity; [考虑社会公平性的都市圈通勤公交可达性评价] | 10.19961/j.cnki.1672-4747.2025.04.023 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S184 | scopus:N2_demand_free | 2026 | An in-depth investigation of time and space-based accessibility inequities in the public transport system of A | 10.1016/j.cstp.2026.101816 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S188 | scopus:N2_demand_free | 2025 | Identifying public transit deserts: A travel demand-independent persistent homology-based method | 10.1093/tse/tdaf015 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | manual |
| S191 | scopus:N2_demand_free | 2026 | Towards Sustainable Electric Bus Fleet Electrification: A Rolling Stock Digital Twin for Pre-Investment Chargi | 10.3390/su18157774 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S206 | scopus:N2_demand_free | 2025 | Agent-based modeling of network-wide metro operations for control strategy evaluation | 10.1016/j.cie.2025.111448 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S213 | scopus:N2_demand_free | 2026 | Platform competition and adoption heterogeneity: How dockless bike sharing shapes urban air quality | 10.1177/10591478261472202 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S216 | scopus:N2_demand_free | 2022 | Sustainable development assessment of incentive-driven shared on-demand mobility systems in rural settings | 10.1186/s12544-022-00565-y | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S241 | scopus:N3_open_fleet | 2025 | Accelerating Computation for Estimating Land Surface Temperature: An Efficient Global–Local Regression (EGLR)  | 10.3390/ijgi14110427 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | kw |
| S242 | scopus:N3_open_fleet | 2021 | The effect of high-density built environments on elderly individuals’ physical health: A cross-sectional study | 10.3390/ijerph181910250 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| S243 | scopus:N3_open_fleet | 2023 | A method for the selection of bus route time control points incorporating APTS and POI data | 10.1117/12.2668562 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S247 | scopus:N4_permit_reform | 2001 | Evaluating optimizations for multiprocessors E-commerce server running TPC-W workload | 10.1109/HICSS.2001.927077 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S249 | scopus:N4_permit_reform | 2008 | Operating system controlled processor-memory bus encryption | 10.1109/DATE.2008.4484834 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S251 | scopus:N4_permit_reform | 2015 | Large-scale power system controlled islanding based on Backward Elimination Method and Primary Maximum Expansi | 10.1016/j.ijepes.2014.12.008 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S252 | scopus:N4_permit_reform | 2026 | Citywide traffic sensor network in Nova Gorica, Slovenia: 2025-2026 telraam S2 dataset | 10.1016/j.dib.2026.113190 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S253 | scopus:N4_permit_reform | 2006 | Single-metal-ion-based molecular building blocks (MBBs) approach to the design and synthesis of metal-organic  | 10.1016/j.molstruc.2006.02.064 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S254 | scopus:N4_permit_reform | 2000 | Upgrading a TEXTOR Data Acquisition system for remote participation using Java and Corba | 10.1016/S0920-3796(00)00138-1 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | kw |
| S257 | scopus:N5_proxy_headway | 2026 | Usage intensity and passenger satisfaction in mixed formal-informal public transport systems: Evidence from Da | 10.1016/j.aftran.2026.100103 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| S260 | scopus:N5_proxy_headway | 2011 | Analysis of passenger-ferry routes using connectivity measures | 10.5038/2375-0901.14.1.2 | 1 | 0 | 0 | 1 | 0 | 0 | 2 | kw |
| S277 | scopus:N5_proxy_headway | 2025 | Causal effect between financial viability and service quality in Indian public transport: Evidence from a Dumi | 10.1016/j.rtbm.2025.101471 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | kw |
| S280 | scopus:N5_proxy_headway | 2026 | Multidimensional Benchmarking of Metro Systems in India: A PCA-SFA Framework for Operational and Financial Eff | 10.1016/j.cstp.2026.101939 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S283 | scopus:N5_proxy_headway | 2007 | Where are public transit needed - Examining potential demand for public transit for commuting trips | 10.1016/j.compenvurbsys.2007.08.005 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| S284 | scopus:N5_proxy_headway | 2024 | Distributed Stochastic Scheduling of Massive Backup Batteries in Cellular Networks for Operational Reserve and | 10.35833/MPCE.2023.000414 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S286 | scopus:N5_proxy_headway | 2025 | Performance assessment of public transport routes: A framework using revealed data | 10.1016/j.rtbm.2024.101283 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S289 | scopus:N5_proxy_headway | 2023 | Mass Transit Route Network Planning in Makassar City | 10.14445/22315381/IJETT-V71I12P208 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | kw |
| S301 | scopus:N5_proxy_headway | 2025 | Forced Oscillation Source Location and Source type Classification | 10.1109/ISGTMiddleEast65737.2025.11314276 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S302 | scopus:N5_proxy_headway | 2019 | Foot-based audit of streets adjacent to new light rail stations in Houston, Texas: Measurement of health-relat | 10.1186/s12889-019-6560-4 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| S313 | scopus:N5_proxy_headway | 2022 | Optimized two-directional phased development of a rail transit line | 10.1016/j.trb.2021.12.007 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S316 | scopus:N5_proxy_headway | 2024 | A Strategic Grid Forming Inverter Placement Framework Considering Centre of Inertia and Voltage Stiffness | 10.1109/PESGM51994.2024.10689139 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S317 | scopus:N5_proxy_headway | 2026 | An improved GWO-based closed-loop bi-level optimization strategy for integrated multi-energy microgrid-distrib | 10.1088/2631-8695/ae7bb4 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S318 | scopus:N5_proxy_headway | 2022 | A Planning Model for Flexible-Route Bus Operations with Financial Constraints | 10.1007/s12205-022-1157-3 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S319 | scopus:N5_proxy_headway | 2026 | Unified Stability Metrics for Grid-Support Technologies in a PV-Dominated IEEE 9-Bus Test System | 10.3390/en19081906 | 0 | 0 | 0 | 1 | 0 | 1 | 2 | kw |
| S320 | scopus:N5_proxy_headway | 2024 | Equity of access to rail services by complementary motorized and active modes | 10.1016/j.jtrangeo.2024.104007 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | kw |
| X01 | extra:P0059 | 2026 | BusOptima - Bus Scheduling & Route Management System | 10.1109/EVST69093.2026.11660518 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | manual |
| X05 | extra:P0197 | 2024 | Generative Methods for Planning Public Transportation Systems | 10.1007/978-3-031-64605-8_25 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | manual |
| X07 | extra:P0205 | 2024 | Equity in Public Transportation Systems in Tourist Cities: A Comparative Study of Palma and Málaga (Spain) | 10.3233/ATDE241189 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| X09 | extra:P0382 | 2020 | Using Open Big Data to Build and Analyze Urban Bus Network Models within and across Administrations | 10.1155/2020/5402620 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | manual |
| X10 | extra:P0517 | 2019 | Maximal market potential of feeder bus route design using particle swarm optimization |  | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| X12 | extra:P0681 | 2015 | Efficient planning of urban public transportation networks | 10.1007/978-3-319-26401-1_41 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | manual |
| O0003 | oa:B_open_data | 2013 | Modelling travel time in urban networks: comparable measures for private car and public transport | 10.1016/j.jtrangeo.2013.06.011 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0006 | oa:B_open_data | 2013 | Modelling the potential effect of shared bicycles on public transport travel times in Greater Helsinki: An ope | 10.1016/j.apgeog.2013.05.010 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0024 | oa:C_india | 2005 | Review of Urban Transportation in India | 10.5038/2375-0901.8.1.5 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0039 | oa:B_open_data | 2018 | Measuring the impacts of new public transit services on space-time accessibility: An analysis of transit syste | 10.1016/j.apgeog.2018.02.012 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0063 | oa:B_open_data;C_global_south | 2023 | Mobility-as-a-Service and the role of multimodality in the sustainability of urban mobility in developing and  | 10.1016/j.tranpol.2023.10.013 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0107 | oa:B_open_data | 2020 | Cumulative (and self-reinforcing) spatial inequalities: Interactions between accessibility and segregation in  | 10.1177/2399808320958426 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0119 | oa:B_open_data | 2020 | Visualizing public transit system operation with GTFS data: A case study of Calgary, Canada | 10.1016/j.heliyon.2020.e03729 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0124 | oa:C_india | 2009 | Public Transport in Pakistan: A Critical Overview | 10.5038/2375-0901.12.2.4 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0146 | oa:B_demand_proxy | 2016 | Analysis of Public Bus Transportation of a Brazilian City Based on the Theory of Complex Networks Using the P- | 10.1155/2016/3898762 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0152 | oa:C_india | 2021 | Development of public transport systems in small cities: A roadmap for achieving sustainable development goal  | 10.1016/j.iatssr.2021.02.002 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0156 | oa:C_global_south | 2016 | A bus route evaluation model based on GIS and super-efficient data envelopment analysis | 10.1080/03081060.2016.1160582 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0170 | oa:C_global_south | 2021 | The Bus Rapid Transit (BRT) in Dar es Salaam: A Pilot Study on Critical Infrastructure, Sustainable Urban Deve | 10.3390/su13031058 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0184 | oa:B_open_data | 2016 | Innovative GTFS Data Application for Transit Network Analysis Using a Graph-Oriented Method | 10.5038/2375-0901.19.4.2 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0202 | oa:B_data_scarce | 2017 | Mapping Urban Accessibility in Data Scarce Contexts Using Space Syntax and Location-Based Methods | 10.1007/s12061-017-9239-1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0207 | oa:B_open_data | 2022 | A GIS-based analysis of reachability aspects in rural public transportation | 10.1016/j.cstp.2022.07.012 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0222 | oa:B_open_data | 2021 | Data to the people: a review of public and proprietary data for transport models | 10.1080/01441647.2021.1977414 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0223 | oa:C_india | 2019 | Performance Optimization of Public Transport Using Integrated AHP–GP Methodology | 10.1007/s40864-019-0103-2 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0255 | oa:B_demand_proxy | 2007 | Stop Spacing Analysis Using Geographic Information System Tools with Parcel and Street Network Data | 10.3141/2034-09 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| O0265 | oa:C_global_south | 2014 | Formulating a New Express Minibus Service Design Problem as a Clustering Problem | 10.1287/trsc.2013.0497 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0271 | oa:B_open_data;C_global_south | 2018 | Mapping Rural Road Networks from Global Positioning System (GPS) Trajectories of Motorcycle Taxis in Sigomre A | 10.3390/ijgi7080309 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0308 | oa:A_rationalisation | 2024 | Resilience enhancement of multi-modal public transportation system via electric bus network redesign | 10.1016/j.tre.2024.103810 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0312 | oa:B_open_data | 2016 | The use of general transit feed specification (GTFS) application to identify deviations in the operation of pu | 10.7163/eu21.2016.31.4 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0316 | oa:B_demand_proxy | 2016 | Prediction of bus passenger trip flow based on artificial neural network | 10.1177/1687814016675999 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0334 | oa:B_open_data | 2012 | Stop Aggregation Model | 10.3141/2276-05 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0354 | oa:C_india | 2016 | Prioritizing Accessible Transit Systems for Sustainable Urban Development: Understanding and Evaluating the Pa | 10.1061/(asce)up.1943-5444.0000338 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0377 | oa:B_open_data | 2020 | Modeling and Evaluating Public Transit Equity and Accessibility by Integrating General Transit Feed Specificat | 10.1061/jtepbs.0000426 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0383 | oa:B_open_data | 2023 | An accessibility-based methodology to prioritize public-transit investments: Application to older adults in th | 10.1016/j.apgeog.2023.103022 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0405 | oa:C_global_south | 2011 | Economic conditions for minibus usage in a multimodal feeder network | 10.1080/03081060.2011.613594 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0436 | oa:B_data_scarce | 2022 | Building a spatial decision support system for tourism and infrastructure planning: technical solution and dat | 10.48088/ejg.d.bra.13.1.094.108 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0465 | oa:C_global_south | 2024 | Creating an Informal Transport Route | 10.1080/01944363.2024.2307920 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0483 | oa:B_open_data | 2024 | Bus stop spacing statistics: Theory and evidence | 10.1016/j.jpubtr.2024.100083 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0491 | oa:B_demand_proxy | 2012 | Grouping of Bus Stops for Aggregation of Route-Level Passenger Origin–Destination Flow Matrices | 10.3141/2277-05 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0492 | oa:B_demand_proxy | 2012 | BRT IN METRO DHAKA: TOWARDS ACHIEVING A SUSTAINABLE URBAN PUBLIC TRANSPORT SYSTEM |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0508 | oa:B_open_data | 2018 | GTFS bus stop mapping to the OSM network | 10.1016/j.future.2018.02.020 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0512 | oa:B_open_data | 2016 | Bus Network Microsimulation with General Transit Feed Specification and Tap-in-Only Smart Card Data | 10.3141/2544-09 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0513 | oa:B_equity;C_global_south | 2011 | Inequity in the Provision of Public Bus Service for Socially Disadvantaged Groups | 10.5539/jsd.v4n5p229 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0520 | oa:A_rationalisation;B_equity | 2022 | Bus network redesigns and public transit equity analysis: Evaluating system-wide changes in Richmond, Virginia | 10.1016/j.tbs.2022.12.002 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0525 | oa:B_open_data | 2012 | Development of a Regional Forecasting Model Based on Google Transit Feed |  | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0529 | oa:C_permit_regulation | 2020 | Hybrid markets in public transport – contract design, performance and conflicts | 10.1016/j.retrec.2020.100897 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0552 | oa:A_freq_fleet;C_global_south | 2018 | Optimization of Headways and Departure Times in Urban Bus Networks: A Case Study of Çorlu, Turkey | 10.1155/2018/7094504 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0563 | oa:C_global_south | 2014 | Challenges of Implementing à la Mode Transport Projects | 10.3141/2451-15 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0566 | oa:C_permit_regulation | 2010 | Effects of regulation changes in seoul bus system: private bus operation under non‐competitive fixed price con | 10.1002/atr.116 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0595 | oa:C_india | 2024 | How do you travel? A holistic evaluation of public transport journeys of women: A case study of Delhi, India | 10.1016/j.jpubtr.2024.100106 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0599 | oa:B_open_data | 2022 | A geospatial workflow for the assessment of public transit system performance using near real‐time data | 10.1111/tgis.12942 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0625 | oa:C_india | 2016 | MULTILEVEL FRAMEWORK FOR OPTIMIZING BUS STOP SPACING | 10.15623/ijret.2016.0505055 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0627 | oa:B_open_data | 2022 | Private car transport or public transport? The study of daily accessibility in Szczecin | 10.31577/geogrcas.2022.74.4.17 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0636 | oa:B_open_data | 2014 | Towards a Standard for Paratransit Data: Lessons from Developing GTFS Data for Nairobi's Matatu System |  | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0644 | oa:B_open_data | 2022 | Mapping the transit network of greater Cartagena with mobile phones: Coverage, accessibility, and informality | 10.1016/j.jtrangeo.2022.103484 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0657 | oa:B_open_data | 2025 | Using Realtime GTFS to generate easy-to-use transit accessibility measures under travel time uncertainty | 10.1016/j.tbs.2025.101054 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0661 | oa:A_core_design;B_data_scarce | 2024 | A sequential transit network design algorithm with optimal learning under correlated beliefs | 10.1016/j.tre.2024.103707 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0676 | oa:A_freq_fleet;C_india | 2012 | Simulation model to determine frequency of a single bus route with single and multiple headways | 10.1504/ijbpscm.2012.044973 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0680 | oa:C_permit_regulation | 2010 | Regulatory Framework and Operational System of Urban Bus Transportation in Yangon, Myanmar |  | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| O0700 | oa:C_global_south | 2021 | A Holistic Decision-Making Process to Improve the Productivity of Public Transportation in Cuenca-Ecuador | 10.33333/rp.vol48n2.03 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0701 | oa:B_open_data | 2015 | Using GTFS Data to Measure and Map Transit Accessibility |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0704 | oa:C_permit_regulation | 2014 | Bus Patronage Change after Sustainable Bus Reform: A Nested Logit Approach with the Case of Seoul | 10.1080/15568318.2013.814078 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0714 | oa:B_open_data | 2022 | The Importance Of Open Data Accessibility For Multimodal Travel Improvement* | 10.7906/indecs.20.2.6 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0715 | oa:A_core_design;C_global_south | 2018 | Optimization of service frequencies in bus networks with Harmony Search Algorithm: An application on Mandl’s t | 10.5505/pajes.2018.43410 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O0727 | oa:C_global_south | 2025 | Evolution of bus rapid transit concepts in Sub-Saharan Africa: towards lighter design and incremental deployme | 10.1016/j.retrec.2025.101604 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0730 | oa:C_global_south | 2024 | Determinants of paratransit feeder service provision using AI-synthesized revealed preference data: a paratran | 10.1080/03081060.2024.2408427 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0750 | oa:B_open_data | 2025 | Spatio‐Temporal Accessibility Modeling With Mobile Phone and GTFS Data: Insights for Urban Transport Planning  | 10.1111/tgis.70163 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0751 | oa:A_rationalisation;B_equity | 2025 | Is Title VI enough? A review of bus network redesign equity analyses | 10.1016/j.trd.2025.104905 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0757 | oa:A_rationalisation | 2021 | Investigating the Preferences of Local Residents toward a Proposed Bus Network Redesign in Chattanooga, Tennes | 10.1177/03611981211013043 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0761 | oa:B_open_data | 2020 | Multicriterial analysis of the accessibility of public transport stops in Cracow | 10.4467/2543859xpkg.20.025.13127 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0772 | oa:C_global_south | 2020 | The use of mobile phone data in transport planning | 10.1504/ijtpm.2020.104867 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0792 | oa:B_open_data | 2023 | Transport and Mobility Segregation in Urban Spaces | 10.23889/ijpds.v8i3.2268 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0798 | oa:B_open_data | 2024 | Assessing Service Imbalances as Contributing Factors to Mobility Issues in the Metropolitan District of Quito, | 10.3390/urbansci8040261 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0809 | oa:C_global_south | 2012 | The Impact of Service Type and Route Length on the Operating Cost per Passenger and Revenue of Paratransit Ope |  | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0812 | oa:C_global_south | 2021 | Shorter commutes, but for whom? Comparing the distributional effects of Bus Rapid Transit on commute times in  | 10.5198/jtlu.2021.1907 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0828 | oa:B_demand_proxy | 2023 | Vulnerability Analysis of Bus Network Based on Land-Use Type of Bus Stops: The Case of Xi’an, China | 10.3390/su151612566 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0832 | oa:B_demand_proxy | 2021 | Discussion on Optimization of Public Transportation Network Setting considering Three-State Reliability | 10.1155/2021/6940263 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0848 | oa:B_open_data | 2022 | ANALYSIS OF THE STATE OF PUBLIC TRANSPORT IN ALMATY | 10.30892/gtg.454spl01-972 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0849 | oa:B_open_data | 2024 | City Transport Analyzer: A Powerful Qgis Plugin For Public Transport Accessibility And Intermodality Analysis | 10.5194/isprs-archives-xlviii-4-w12-2024-113-2024 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0854 | oa:C_global_south | 2025 | Spatial, mobility, or socio-economic inequity? A district level job accessibility evaluation in Jakarta, Indon | 10.1080/12265934.2025.2553714 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0867 | oa:B_open_data | 2025 | Assessing equitable access in X-minute cities through open spatial data | 10.1177/23998083251398660 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0878 | oa:C_permit_regulation | 2025 | Bus regulation and the net-zero transition dynamics in Great Britain | 10.1080/15568318.2025.2524475 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0883 | oa:C_global_south | 2025 | How to ensure sufficient access to public transport in rural areas? A comparative analysis of institutional de | 10.1016/j.tbs.2025.101096 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0893 | oa:B_demand_proxy | 2023 | MULTI-OBJECTIVE OPTIMIZATION FOR BRT ROUTES USING GENETIC ALGORITHM: NEW CAIRO CASE STUDY | 10.35741/issn.0258-2724.58.1.60 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0900 | oa:C_global_south | 2020 | The use of mobile phone data in transport planning | 10.1504/ijtpm.2020.10026599 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0907 | oa:B_accessibility;B_equity;C_global_sou | 2024 | Joint optimization of fixed route bus networks and complementary paratransit service areas | 10.1080/19427867.2024.2320499 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O0931 | oa:B_open_data | 2026 | Robustness Assessment of Public Transport Networks in Various Graph Representations: Systematic Review, Decisi | 10.1002/net.70021 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O0953 | oa:B_open_data | 2022 | A LARGE SCALE METHOD FOR EXTRACTING GEOGRAPHICAL FEATURES ON BUS ROUTES FROM OPENSTREETMAP AND ASSESSMENT OF T | 10.5194/isprs-archives-xlviii-4-w5-2022-37-2022 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0966 | oa:A_rationalisation | 2022 | Acceleration of Integrated Public Transport Management: Study on Bus Rapid Transit Management in DKI Jakarta | 10.36348/sjbms.2022.v07i07.001 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O0973 | oa:B_open_data | 2022 | Assessment of the Bus Transit Network: A Perspective from the Daily Activity-Travel Organization of Travelers | 10.3390/su14042406 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0976 | oa:B_open_data | 2025 | Transport Mode Choice for Disaggregated Mobility Demand Generation | 10.1109/access.2025.3570126 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O0978 | oa:B_demand_proxy | 2024 | BRPVis: Visual Analytics for Bus Route Planning Based on Perception of Passenger Travel Demand | 10.1109/mcg.2024.3454645 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1003 | oa:B_open_data | 2023 | Trip Timing Algorithm for GTFS Data with Redis Model to Improve the Performance | 10.61186/jist.36842.11.43.260 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1006 | oa:B_open_data | 2026 | The uneven geographies of care: Transport disadvantage and healthcare accessibility in Melbourne | 10.1016/j.jth.2026.102334 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1009 | oa:B_open_data | 2019 | Analysis of Jeju Public Transit System Reorganization Effect Based on Accessibility of Public Transit Networks | 10.17208/jkpa.2019.11.54.6.68 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1041 | oa:C_india | 2020 | COMPARATIVE STUDY AND ANALYSIS OF PUNE BRTS AND HUBBALLI DHARWAD BRTS IN INDIA (2018-2019) | 10.33564/ijeast.2020.v04i11.037 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1043 | oa:B_open_data | 2019 | Network-based Visualisation of Accessibility for a Public Transport System | 10.5194/ica-adv-1-7-2019 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1046 | oa:B_data_scarce | 2018 | Measuring Spontaneous Accessibility for Iterative Transit Planning | 10.1177/0361198118780834 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1054 | oa:B_open_data | 2026 | Mapping Service Accessibility Through Urban Analytics: A Linked Open Data Approach in the Lazio Region (Italy) | 10.3390/smartcities9020020 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1069 | oa:C_global_south | 2018 | Bus stop network catchment analysis of integrated feeder service for public bus transit system - a case study  | 10.1504/writr.2018.10010625 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| O1072 | oa:A_core_design;B_data_scarce | 2025 | An AI Framework for Generating and Simulating Public Transportation | 10.7759/s44389-025-07783-0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O1121 | oa:B_open_data | 2026 | Topographic friction and spatial equity: a fuzzy RS–GIS accessibility assessment of metropolitan Tehran | 10.1080/23754931.2026.2657351 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1133 | oa:B_open_data | 2022 | Accessibility to various destinations by public and private transport in Szczecin | 10.4467/2543859xpkg.22.010.16268 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1135 | oa:B_open_data | 2014 | Bus stop usage evaluation and BRT station selection strategy by machine learning methods | 10.54014/g3jy-8wvh | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1144 | oa:C_permit_regulation | 2021 | Service Innovation for Route Permits and Public Transport Operations Permits through Si Pintar Solo at the Sur | 10.15575/jpan.v13i2.12267 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| O1145 | oa:C_permit_regulation | 2022 | Analysis of Rapid Transit (Brt) Bus Network Development in Ternate City | 10.5281/zenodo.5883462 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| O1146 | oa:C_permit_regulation | 2025 | INDICATORS OF THE ADOPTION OF A CONTRACTING SYSTEM FOR REGULAR PUBLIC TRANSPORT SERVICES IN RUSSIA | 10.17323/1999-5431-2025-0-2-137-160 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1147 | oa:C_permit_regulation | 2007 | Competitive Tendering in Local Bus Services. Effects on Rural Service Levels and on Administrative Costs |  | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| O1155 | oa:B_open_data | 2023 | Planning for accessibility by transit for older adults |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1165 | oa:B_demand_proxy | 2001 | WHY BOTHER WITH BUS ROUTES |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1167 | oa:B_demand_proxy | 2010 | Planning Method of Public Transit Route and Station in New Urban Area |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1190 | oa:B_demand_proxy | 2017 | Improvement Assessment of Bus Serviceability by Proposing Route Revision |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1193 | oa:B_demand_proxy | 2016 | Towards an Agent-based Approach to Integrated Transit-Land Use PLannig for Small and Rural Communities (SRC) - |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1194 | oa:B_demand_proxy | 2026 | Bus network reform in Barcelona during the 2010s: did it improve transit accessibility and network performance | 10.1108/jtas-05-2025-0035 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1198 | oa:B_demand_proxy | 2015 | Transforming Adelaide into a city of networked TODs using buses: case study of the Adelaide OBahn |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1200 | oa:B_demand_proxy | 2004 | INTDAS: An Integrated National Transit Database Analysis System |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1205 | oa:B_demand_proxy | 2009 | OD Matrix Estimation of Pubic Transportation Flow |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1226 | oa:B_demand_proxy | 2011 | Development of a Transit Decision Support System |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1230 | oa:B_equity;C_global_south | 2026 | Inclusion and equity from accessibility lens: A study of public transit planning practice in mid-sized urban c | 10.1016/j.urbmob.2026.100245 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1316 | oa:B_data_scarce | 2026 | Assessing bus stop accessibility for persons with reduced mobility in Durban, South Africa | 10.1680/jmuen.26.00031 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| O1330 | oa:B_open_data | 2014 | Development of a tool for determining speed and road directions using GPS vehicle devices and free resources |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1334 | oa:A_rationalisation | 2024 | ANALYSIS OF BUS DELAY TIME AND THE IMPACT OF BUS ROUTE NETWORK REDESIGN IN MITO CITY USING PASSENGER OD DATA | 10.2208/jscejj.22-00201 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1335 | oa:A_rationalisation | 2015 | Study on Bus Route Restructuring in rural core cities : from the case of Oita City |  | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1337 | oa:A_rationalisation | 2020 | A STUDY ON SOCIAL IMPACT ASSESSMENT OF LOCAL PUBLIC TRANSPORT POLICIES WITH FOCUS ON BUS NETWORK REDESIGN IN R | 10.2208/jscejipm.75.6_i_555 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1338 | oa:A_rationalisation | 2021 | Transit in transition: insights into large-scale public transport network redesigns |  | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| O1344 | oa:C_india | 2002 | TRANSIT ROUTE PLANNING USING OPTIMIZATION TECHNIQUE FOR A CORRIDOR IN HYDERABAD CITY |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1345 | oa:C_india | 2011 | Transport Management in Emerging Cities - The Integration of ITS in Public Transport |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1350 | oa:C_india | 2009 | Sustainable Urban Transport Planning Initiatives in India |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1354 | oa:C_india | 2000 | POLICY FORMULATION FOR AN INTEGRATED MULTI-MODAL PUBLIC TRANSPORT PLAN CASE STUDY: CALCUTTA, INDIA |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1368 | oa:A_core_design;B_open_data | 2015 | Automation of Process to Load Database from OSM for the Design of Public Routes. |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1374 | oa:C_india | 2024 | AICTSL: Sustainable Capacity Planning by Cash Flow Management | 10.1177/23197145241232185 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| O1375 | oa:C_india | 2017 | A Micro-Analysis of Accessibility and Travel Behavior of a Small Sized Indian City: A Case Study of Agartala | 10.21817/ijet/2017/v9i2/170902083 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1377 | oa:B_open_data | 2025 | MODELING OF SOCIO-ECONOMIC STRUCTURES OF TERRITORIAL COMMUNITIES | 10.32782/2520-2200/2025-2-6 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1378 | oa:B_open_data | 2025 | Environmental Protection Agency (EPA), Smart Location Mapping Tools and Data |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1380 | oa:B_open_data;B_equity | 2026 | Assessment of spatial equity of school and workplace locations from the perspective of source and destination: | 10.7163/gpol.0315 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1381 | oa:B_open_data | 2025 | Bridging the gap: Transport accessibility challenges and inclusive mobility outcomes for vulnerable groups in  | 10.48346/imist.prsm/ajlp-gs.v9i1.61367 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1388 | oa:C_india | 2019 | Optimization Of Rural Roads Network Of Vikarabad Bus Depot Transportation Operation | 10.26634/jce.9.1.14633 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1396 | oa:C_india | 2026 | Enhanced Multi-Criteria Accessibility Modelling for Rural Transport Systems: Evidence from a Pilgrimage Villag | 10.56975/tijer.v13i4.161696 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1469 | oa:B_open_data | 2026 | Linking Public Transport Provision to Functional Regions: Evaluating Transport–Commuting Alignment in Estonia | 10.5194/agile-giss-7-24-2026 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1488 | oa:B_open_data | 2026 | An Open Geospatial Framework for Proximity-Based Community Planning: Integrating Mobility-Based Community Dete | 10.5194/isprs-archives-l-4-w1-2026-35-2026 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1493 | oa:B_open_data | 2012 | Estimating Individual Travel Times for Public Transit Passengers |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1494 | oa:B_open_data | 2026 | Beyond Proximity: Multimodal Job Accessibility Within 15–30 Min and Urban Inequality | 10.3390/world7070126 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1525 | oa:B_open_data | 2026 | Assessing public transport equity: The case of Alexandria, Egypt | 10.1016/j.aej.2026.03.006 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1527 | oa:B_open_data;B_equity | 2026 | Does Public Transit Serve People Experiencing Homelessness? A National Assessment of Homeless Shelter Accessib | 10.1177/07349149261465369 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1540 | oa:C_global_south | 2022 | Conceptual Framework of Environmentally Sustainable Transportation in Local Public Transport Route Planning | 10.14398/urpr.9.122 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1541 | oa:C_global_south | 2004 | A citizen consensus framework for planning neighbourhood bus routes |  | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1542 | oa:C_global_south | 2025 | Formalizing Public Transit in Mid-Sized Developing Cities | 10.14500/aro.12185 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1548 | oa:B_open_data | 2021 | Assessing the spatial impacts of unreliable public transport systems: A quasi real-time data-driven approach |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1558 | oa:C_global_south | 2026 | A data-light GIS framework for initiating bus stop formalization in mid-sized developing cities | 10.1016/j.cstp.2026.101959 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| O1560 | oa:C_global_south;C_permit_regulation | 2026 | The Dichotomous Coverage Model: When Formal Networks and Informal Paratransit Collide in A Megacity | 10.5281/zenodo.21881206 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1561 | oa:C_global_south;C_permit_regulation | 2026 | The Dichotomous Coverage Model: When Formal Networks and Informal Paratransit Collide in A Megacity | 10.5281/zenodo.21881205 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1563 | oa:C_global_south | 2018 | Bus stop network catchment analysis of integrated feeder service for public bus transit system - a case study  | 10.1504/writr.2018.089534 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| O1564 | oa:C_global_south | 2026 | Paratransit networks inefficiencies and future directions: Case of Nairobi metropolitan area | 10.1016/j.retrec.2026.101792 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| O1566 | oa:C_global_south | 2014 | Modifying traffic routes and bus stations down town "Hamedan" using geographically informational systems(GIS) |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1590 | oa:C_global_south | 2021 | STUDY OF THE MOVEMENT INTENSITY OF URBAN PASSENGER TRANSPORT THROUGH BUS STOP POINTS | 10.12731/2227-930x-2021-11-3-45-56 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1591 | oa:C_global_south | 2024 | ECONOMIC IMPACT OF COMMUTERS AND DRIVERS’ PERCEPTION OF MINIBUS (KOROPE) AS A MEANS OF PUBLIC TRANSPORTATION I | 10.37500/ijessr.2024.7304 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| O1592 | oa:C_global_south | 2019 | Governance and Transportation in Nairobi, Kenya: Understanding How Policy, Planning, and Levels of Governance  | 10.7916/d8-dr9j-hk87 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1600 | oa:C_global_south | 2026 | MILP for Multimodal Urban Transport: Formal and Informal Sectors | 10.14569/ijacsa.2026.01705100 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1618 | oa:C_permit_regulation | 2020 | Design of Operational Management Information Systems for Route Licenses at the Ternate City Transportation Age | 10.47324/ilkominfo.v3i1.95 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| O1628 | oa:C_global_south | 2026 | Navigating the urban fringe: Socially embedded adaptation of informal transportation amid Bogotá’s urban gondo | 10.1177/00420980251398997 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| O1644 | oa:C_permit_regulation | 2021 | Penegakan Hukum Terhadap Pelanggaran Izin Trayekd di Kabupaten Manggarai Tengah | 10.22225/jkh.2.3.3634.515-519 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| S002 | scopus:N1_rationalisation_all | 2018 | A route efficiency analysis using Shannon entropy-based modified DEA method and route characteristics investig | 10.1080/03155986.2017.1393727 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S005 | scopus:N1_rationalisation_all | 2009 | VIA downtown transferring O-D survey |  | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S008 | scopus:N1_rationalisation_all | 2023 | An Adaptive Battery Charging Method for the Electrification of Diesel or CNG Buses as In-Motion-Charging Troll | 10.1109/TTE.2023.3243022 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S009 | scopus:N1_rationalisation_all | 2023 | Strategy-based transit stochastic user equilibrium model with capacity and number-of-transfers constraints | 10.1016/j.ejor.2022.05.040 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S012 | scopus:N1_rationalisation_all | 2020 | Street protests and air pollution in Hong Kong | 10.1007/s10661-020-8243-0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S013 | scopus:N1_rationalisation_all | 2006 | A multi-tier data model for bus transit and its applications in Chinese cities | 10.1117/12.712688 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S014 | scopus:N1_rationalisation_all | 2022 | Multimodal Urban Transportation Network Capacity Model Considering Intermodal Transportation | 10.1177/03611981221086931 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S015 | scopus:N1_rationalisation_all | 2022 | Modeling Network Capacity for Urban Multimodal Transportation Applications | 10.1155/2022/6034369 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S017 | scopus:N1_rationalisation_all | 2023 | Perception of overlap in multi-modal urban transit route choice | 10.1080/23249935.2021.2005180 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S018 | scopus:N1_rationalisation_all | 2013 | Assessing public transport systems connectivity based on Google Transit data | 10.1016/j.jtrangeo.2013.09.015 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S019 | scopus:N1_rationalisation_all | 2020 | A multi-modal network equilibrium model with captive mode choice and path size logit route choice | 10.1016/j.tra.2020.03.035 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S023 | scopus:N1_rationalisation_all | 2014 | Reviewing Efficiency and Effectiveness of Interurban Public Transport Services: A Practical Experience | 10.1016/j.trpro.2014.07.024 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S025 | scopus:N1_rationalisation_all | 2025 | Shuttle buses along the subway lines: function of public transport in mitigating road congestion in Kunming, C | 10.1080/12265934.2025.2595988 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S026 | scopus:N1_rationalisation_all | 2011 | Standardizing network transit in NATO coalition networks | 10.1109/MILCOM.2011.6127617 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S027 | scopus:N1_rationalisation_all | 2021 | Optimal network restructure via improved whale optimization approach | 10.1002/dac.4617 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S028 | scopus:N1_rationalisation_all | 2022 | Impact of introducing a metro line on urban bus services | 10.1016/j.cstp.2022.03.007 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S034 | scopus:N1_rationalisation_all | 2025 | A robust approach to resiliency enhancement of distribution system using ensembled deep reinforcement learning | 10.1007/s12667-025-00729-4 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S035 | scopus:N1_rationalisation_all | 2014 | Hybrid firms and transit delivery: The case of Berlin | 10.1111/apce.12026 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S036 | scopus:N1_rationalisation_all | 2013 | An application-level routing method with transit cost reduction based on a distributed heuristic algorithm | 10.1587/transcom.E96.B.1481 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S038 | scopus:N1_rationalisation_all | 2012 | Centralized and distributed heuristic algorithms for application-level traffic routing | 10.1109/ICOIN.2012.6164376 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S041 | scopus:N1_rationalisation_all | 2017 | Transit assignment model for Tokyo metropolitan area considering route overlapping and in-vehicle congestions |  | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S043 | scopus:N1_rationalisation_all | 2026 | The responsibility of Western European coastal states for the conservation of two emblematic migratory seabird | 10.1016/j.biocon.2025.111678 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S048 | scopus:N1_rationalisation_all | 2018 | RNR: Reliability oriented Network Restructuring | 10.1109/RTUCON.2018.8659868 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S049 | scopus:N1_rationalisation_all | 2016 | Modeling Mode and Route Similarities in Network Equilibrium Problem with Go-Green Modes | 10.1007/s11067-013-9201-y | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S050 | scopus:N1_rationalisation_all | 2019 | Using Smart Farecard Data to Support Transit Network Restructuring: Findings from Los Angeles | 10.1177/0361198119845661 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S051 | scopus:N1_rationalisation_all | 2025 | Optimizing Campus Bus Operations: A Case Study in Sustainable Transport Automation | 10.1109/ROMA66616.2025.11155732 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S056 | scopus:N1_rationalisation_all | 2024 | Security constrained optimal power flow solution for practical transmission grid using hybrid use of generatin | 10.1007/s42452-024-06301-6 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S061 | scopus:N1_rationalisation_all | 2020 | Park-and-Ride Choice Behavior in a Multimodal Network with Overlapping Routes | 10.1177/0361198120908866 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S064 | scopus:N2_demand_free | 2014 | Cash or prepay: Understanding passenger choice for different products |  | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S066 | scopus:N2_demand_free | 2026 | Joint optimization of fleet size and operating speed for service planning in oversaturated urban rail transit  | 10.1016/j.tre.2026.105076 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| S072 | scopus:N2_demand_free | 2025 | Research on an Active Distribution Network Planning Strategy Considering Diversified Flexible Resource Allocat | 10.3390/pr13072254 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S073 | scopus:N2_demand_free | 2025 | Stackelberg-Nash bargaining-based low-carbon scheduling for multiple integrated multi-energy systems | 10.1016/j.energy.2025.139024 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S074 | scopus:N2_demand_free | 2022 | Impact of Unplanned Long-Term Service Disruptions on Urban Public Transit Systems | 10.1109/OJITS.2022.3199108 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S077 | scopus:N2_demand_free | 2026 | Quantifying local mobility and unraveling nonlinear mechanisms in the 15-minute city: Evidence from residentia | 10.1016/j.cities.2026.107115 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S078 | scopus:N2_demand_free | 2014 | Development of a data-driven platform for transit performance measures using smart card and GPS data | 10.1061/(ASCE)TE.1943-5436.0000714 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S079 | scopus:N2_demand_free;N3_open_fleet | 2022 | Exploring Built Environment Influence on Taxi Vacant Time in Megacities: A Case Study of Chongqing, China | 10.1155/2022/3096901 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S081 | scopus:N2_demand_free | 2026 | Adaptive Liquid Time-Constant Equivalent Dynamic Model with Transfer Learning for Active Distribution Networks | 10.1109/TSG.2026.3720584 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S082 | scopus:N2_demand_free | 2010 | Electric cars or high-efficiency transport networks?; [Auto elettrica o reti di trasporto ad alta efficienza?] |  | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S084 | scopus:N2_demand_free | 2017 | Impact of Transport Zone Number in Simulation Models on Cost-Benefit Analysis Results in Transport Investments | 10.1088/1757-899X/245/4/042052 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S085 | scopus:N2_demand_free | 2022 | A Novel Shared Energy Storage Planning Method Considering the Correlation of Renewable Uncertainties on the Su | 10.1109/TSTE.2022.3179837 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S087 | scopus:N2_demand_free | 2022 | The spatial planning of public electric vehicle charging infrastructure in a high-density city using a context | 10.1016/j.tra.2022.02.012 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S090 | scopus:N2_demand_free | 2026 | An integrated framework for dynamic risk coupling and evaluation in railway cold chain transport | 10.1016/j.ress.2026.112737 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S096 | scopus:N2_demand_free | 2025 | Multi-Agent Deep Reinforcement Learning for Simulating Centralized Double-Sided Auction Electricity Market | 10.1109/TPWRS.2024.3404472 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S098 | scopus:N2_demand_free | 2021 | Multi-dimensional analysis of load characteristics of electrical vehicles based on power supply side data and  | 10.3390/wevj12030125 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S102 | scopus:N2_demand_free | 2011 | Design and implementation of efficient transit networks: Procedure, case study and validity test | 10.1016/j.sbspro.2011.04.510 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S105 | scopus:N2_demand_free | 2026 | Swarm learning for P2P trading among aggregators within virtual power plants: Optimized operation strategy wit | 10.1016/j.ijepes.2026.112155 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S106 | scopus:N2_demand_free | 2026 | Domain-Adversarial Transfer Learning for Urban Crime Forecasting: A Case Study of the Surrey - Langley SkyTrai | 10.1109/CCWC67433.2026.11393839 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S107 | scopus:N2_demand_free | 2008 | Impact of transmission constraints on supply-Side bidding strategy using BLP approach | 10.1109/PES.2008.4596136 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S108 | scopus:N2_demand_free | 2018 | Decarbonized Unit Commitment Applying Water Cycle Algorithm Integrating Plug-In Electric Vehicles | 10.1109/MEPCON.2018.8635152 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S111 | scopus:N2_demand_free | 2017 | Achieving Low Carbon Emission Using Smart Grid Technologies | 10.1109/VTCSpring.2017.8108624 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S112 | scopus:N2_demand_free | 2008 | Improving zonal congestion relief management using economical and technical factors of the demand side | 10.1109/PECON.2008.4762626 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S115 | scopus:N2_demand_free | 2026 | Resilience Enhancement Strategy for Power Systems: A Novel Active Response Model | 10.3390/pr14101585 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S117 | scopus:N2_demand_free | 2019 | Optimization of household energy consumption towards day-ahead retail electricity price in home energy managem | 10.1016/j.scs.2019.101468 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S118 | scopus:N2_demand_free | 2008 | Integrated railways-based policies: The Regional Metro System (RMS) project of Naples and Campania | 10.1016/j.tranpol.2007.11.001 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S126 | scopus:N2_demand_free | 2021 | Estimating the route-level passenger demand profile from bus dwell times | 10.1016/j.trc.2021.103273 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S127 | scopus:N2_demand_free | 2011 | Design and implementation of efficient transit networks: Procedure, case study and validity test | 10.1016/j.tra.2011.04.006 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S130 | scopus:N2_demand_free | 2021 | Co-Optimization of Supply and Demand Resources for Load Restoration of Distribution System under Extreme Weath | 10.1109/ACCESS.2021.3102497 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S131 | scopus:N2_demand_free | 2018 | A smart grid framework for optimally integrating supply-side, demand-side and transmission line management sys | 10.3390/en11051038 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S132 | scopus:N2_demand_free | 2015 | Optimal use of energy storage systems with renewable energy sources | 10.1016/j.ijepes.2015.01.025 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S135 | scopus:N2_demand_free | 2022 | Urban Grid and Accessibility of Proposed Metro Stations in an Organic City: Using Space Syntax as an Analytica |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S136 | scopus:N2_demand_free | 2020 | The impact of information on system operations | 10.1088/1742-6596/1646/1/012145 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S145 | scopus:N2_demand_free | 2025 | Optimizing bidding strategy in electricity market based on graph convolutional neural network and deep reinfor | 10.1016/j.apenergy.2024.124978 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S148 | scopus:N2_demand_free | 2026 | Power System Risk Dispatch Driven by Multi-Modal Fusion and Transfer Learning | 10.1109/ICSGGE69348.2026.11508999 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S151 | scopus:N2_demand_free | 2005 | Supply-side invasion ecology: Characterizing propagule pressure in coastal ecosystems | 10.1098/rspb.2005.3090 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S153 | scopus:N2_demand_free | 2022 | How do pandemics affect intercity air travel? Implications for traffic and environment | 10.1016/j.tra.2022.11.008 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S160 | scopus:N2_demand_free | 2021 | Integrated agent-based microsimulation framework for examining impacts of mobility-oriented policies | 10.1007/s00779-020-01363-w | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S162 | scopus:N2_demand_free | 2026 | ASSESSING LIGHT RAIL TRANSIT PERFORMANCE FROM AN OPERATOR’S PERSPECTIVE: EVIDENCE FROM ADDIS ABABA | 10.19272/202606701004 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S166 | scopus:N2_demand_free | 2026 | Integration of PINN with Conventional Well Logging for Few-Shot TOC Prediction in Ultradeep Source Rocks | 10.1021/acsomega.5c10927 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S167 | scopus:N2_demand_free | 2026 | Research on Distribution Transformer Layout Planning Model of Distribution Networks Considering the Impact of  | 10.13052/spee1048-5236.4527 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S168 | scopus:N2_demand_free | 2012 | Measuring transit system accessibility using a modified two-step floating catchment technique | 10.1080/13658816.2011.574140 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| S175 | scopus:N2_demand_free | 2025 | Multi-Level Evaluation for Flexible Load Regulation Potential in Distribution Network Based on Ensemble Cluste | 10.3390/app152412885 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S181 | scopus:N2_demand_free | 2020 | Overvoltage simulation and analysis of switching-off shunt reactor with 12kV vacuum circuit breaker | 10.1109/ACPEE48638.2020.9136172 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S183 | scopus:N2_demand_free | 2022 | Rolling unit commitment based on dual-discriminator conditional generative adversarial networks | 10.1016/j.epsr.2021.107770 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S186 | scopus:N2_demand_free | 2021 | A comparative design of a campus microgrid considering a multi-scenario and multi-objective approach | 10.3390/en14112853 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S187 | scopus:N2_demand_free | 2019 | Mapping Urban Accessibility in Data Scarce Contexts Using Space Syntax and Location-Based Methods | 10.1007/s12061-017-9239-1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S198 | scopus:N2_demand_free | 2021 | An Individual-Based Simulation Approach to Demand Responsive Transport | 10.1007/978-3-030-71454-3_5 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S199 | scopus:N2_demand_free | 2020 | Reliable drug war data: The Consolidated Counterdrug Database and cocaine interdiction in the “Transit Zone” | 10.1016/j.drugpo.2020.102719 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | kw |
| S203 | scopus:N2_demand_free | 2018 | Determination of Optimal Configuration Point for DSTATCOM in Distribution System | 10.1109/EI2.2018.8582056 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S204 | scopus:N2_demand_free | 2016 | Approximating the performance of a "last mile" transportation system | 10.1287/trsc.2014.0553 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| S205 | scopus:N2_demand_free | 2012 | Public transport pre-pay tickets: Understanding passenger choice for different products | 10.1016/j.tranpol.2011.07.003 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S211 | scopus:N2_demand_free | 2019 | Analysing public transport data through the use of big data tecnhologies for urban mobility | 10.1109/YEF-ECE.2019.8740816 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S212 | scopus:N2_demand_free | 2026 | The partial adaptation of mobility practices to public transport shock effects: evidence from the Greater Gene | 10.1016/j.trip.2026.102219 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S214 | scopus:N2_demand_free | 2022 | A Black Start Simulation Method with Energy Storage Assistance Systems in Wind Power Consumption | 10.1109/CEEPE55110.2022.9783307 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S215 | scopus:N2_demand_free | 2024 | Passenger social rerouting strategies in capacitated public transport systems | 10.1016/j.tre.2024.103598 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S218 | scopus:N2_demand_free | 2006 | Assessing the market power due to the network constraints in competitive electricity markets | 10.1016/j.epsr.2005.12.004 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S222 | scopus:N2_demand_free | 2025 | Optimization of sizing and energy management in hybrid energy storage systems for transient suppression in shi | 10.1016/j.ijepes.2025.110864 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S224 | scopus:N2_demand_free | 2018 | Integrating shared autonomous vehicle in public transportation system: A supply-side simulation of the first-m | 10.1016/j.tra.2018.04.004 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| S228 | scopus:N2_demand_free | 2021 | The potential of real-time crowding information in reducing bus bunching under different network saturation le | 10.1109/MT-ITS49943.2021.9529310 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S232 | scopus:N3_open_fleet | 2025 | Synthetic population and urban mobility modeling using open and publicly available data - a Washington, DC COV | 10.1007/s43762-025-00214-9 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S234 | scopus:N3_open_fleet | 2023 | Quantifying the environmental characteristics influencing the attractiveness of commercial agglomerations with | 10.1177/23998083231158370 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S235 | scopus:N3_open_fleet | 2020 | Research on the Influence of Built Environment on Ridership: Insights from Nanjing | 10.1061/9780784483053.252 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S236 | scopus:N3_open_fleet | 2020 | Traffic flow city index based on public transportation vehicles data | 10.1145/3407982.3408007 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| S238 | scopus:N3_open_fleet | 2012 | Spatially aware model for optimal site selection | 10.3141/2276-18 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S239 | scopus:N3_open_fleet | 2026 | Nonlinear responses of station-area functional vitality to the built environment in urban rail transit network | 10.3389/fphy.2026.1897232 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S244 | scopus:N3_open_fleet | 2019 | Identification and interpretation of spatial–temporal mismatch between taxi demand and supply using global pos | 10.1080/15472450.2018.1518137 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S245 | scopus:N3_open_fleet | 2023 | Popularity influence mechanism of creative industry parks: A semantic analysis based on social media data | 10.1016/j.scs.2022.104384 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S246 | scopus:N3_open_fleet | 2022 | Spatially Varying Relation between Built Environment and Station-Level Subway Passenger-Distance | 10.1155/2022/7542560 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S248 | scopus:N4_permit_reform | 2022 | Improving paratransit service: Lessons from transport management companies in Nairobi, Kenya and their transfe | 10.1016/j.cstp.2021.11.013 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | manual |
| S250 | scopus:N4_permit_reform | 2011 | Effects of regulation changes in seoul bus system: Private bus operation under non-competitive fixed price con | 10.1002/atr.116 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S258 | scopus:N5_proxy_headway | 2024 | Optimization Study of Metro Service Based on LSTM Model and Floyd Algorithm | 10.1109/CIPAE64326.2024.00104 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S263 | scopus:N5_proxy_headway | 2008 | Analysis of transit quality of service and employment accessibility for the greater Chicago, Illinois, region | 10.3141/2042-03 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S265 | scopus:N5_proxy_headway | 2015 | Robustness assessment of urban rail transit based on complex network theory: A case study of the Beijing Subwa | 10.1016/j.ssci.2015.06.006 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S270 | scopus:N5_proxy_headway | 2024 | Simultaneous Assessment of Multiple Aspects of Stability of Power Systems With Renewable Generation | 10.1109/TPWRS.2023.3241862 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S271 | scopus:N5_proxy_headway | 2016 | Determining optimal strategies for single-line bus operation by means of smartphone demand data | 10.3141/2539-15 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | kw |
| S273 | scopus:N5_proxy_headway | 2012 | Using floating catchment analysis (FCA) techniques to examine intra-urban variations in accessibility to publi | 10.1016/j.jtrangeo.2012.06.014 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| S274 | scopus:N5_proxy_headway | 2011 | Differences in travel behavior and demand potential of tram-and bus-based neighborhoods: Evidence from a clust | 10.3141/2217-01 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S275 | scopus:N5_proxy_headway | 2021 | Optimal Design for Demand Responsive Connector Service Considering Elastic Demand | 10.1109/TITS.2021.3054678 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S276 | scopus:N5_proxy_headway | 2023 | Mitigating bus bunching with real-time crowding information | 10.1007/s11116-022-10270-3 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S278 | scopus:N5_proxy_headway | 2021 | Coupling degree between the demand and supply of bus services at stops: A density-based approach | 10.3390/ijgi10030173 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S281 | scopus:N5_proxy_headway | 2024 | Spatiotemporal impacts of metro network structure on land use change | 10.1016/j.jum.2024.04.002 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S288 | scopus:N5_proxy_headway | 2020 | The planning of campus bus in Islamic University of Indonesia with geographic system information | 10.1088/1757-899X/771/1/012052 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S290 | scopus:N5_proxy_headway | 2019 | Bus service indicator: The different sight of performance index development | 10.1088/1742-6596/1349/1/012049 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S291 | scopus:N5_proxy_headway | 2014 | Spatial analysis of access to and accessibility surrounding train stations: A case study of accessibility for  | 10.1016/j.jtrangeo.2014.06.022 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S292 | scopus:N5_proxy_headway | 2021 | A Data Driven Approach to Match Demand and Supply for Public Transport Planning | 10.1109/TITS.2020.2991834 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S293 | scopus:N5_proxy_headway | 2020 | Assessment of alternative mobility opportunities for connecting jelgava and riga | 10.22616/ERDev2020.19.TF471 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S296 | scopus:N5_proxy_headway | 2024 | Analysis of potential demand of LRT Jakarta Velodrome - Manggarai route based on public preferences | 10.1063/5.0236733 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S297 | scopus:N5_proxy_headway | 2023 | A Study on the Choice of Self-Driving Rides for Elderly People | 10.1061/9780784484876.045 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S300 | scopus:N5_proxy_headway | 2014 | Rail transit route optimization model for rail infrastructure planning and design: Case study of Saint Andrews | 10.1061/(ASCE)TE.1943-5436.0000445 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S304 | scopus:N5_proxy_headway | 2026 | Customized bus routing optimization considering carbon emission reduction benefits; [考虑碳减排收益的定制公交线路规划与运营优化] | 10.19961/j.cnki.1672-4747.2025.08.016 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S306 | scopus:N5_proxy_headway | 2024 | Optimal fare and headway for a demand adaptive paired-line hybrid transit system in a rectangular area with el | 10.1080/21680566.2024.2389882 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S311 | scopus:N5_proxy_headway | 2024 | Exploring the effect of neighbouring built and demographic environment on station-level bike-sharing trips und | 10.1016/j.jth.2024.101818 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S315 | scopus:N5_proxy_headway | 2017 | Improving public transport management through optimizing use of resources: A case study |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S321 | scopus:N5_proxy_headway | 2023 | The Impacts of Demand Side Management on Combined Frequency and Angular Stability of the Power System | 10.1109/TPWRS.2022.3203887 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S322 | scopus:N5_proxy_headway | 2005 | Optimal urban rail transit corridor identification within integrated framework using geographical information  | 10.1061/(ASCE)0733-9488(2005)131:2(98) | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S324 | scopus:N5_proxy_headway | 2017 | Modeling transportation demand in short sea shipping oa | 10.1057/mel.2016.9 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S330 | scopus:N6_kashmir_india_bus | 2025 | Evolutionary computation based wind energy integrated multi-objective optimal reactive power dispatch and econ | 10.1016/j.compeleceng.2025.110587 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S331 | scopus:N6_kashmir_india_bus | 2000 | The impacts of tourism on the environment of Mussoorie, Garhwal Himalaya, India | 10.1023/A:1006760015997 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S334 | scopus:N6_kashmir_india_bus | 2017 | Preparation of Papers - Potential Alternate Energy Resources for Sustainability: A Must Need for a top Pilgrim | 10.1016/j.egypro.2017.05.047 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S335 | scopus:N6_kashmir_india_bus | 2024 | Demand Response Based Techno-Socio-Economic Improvements with Time-Varying Incentives at DN using Cuckoo Searc | 10.1109/ICISSGT58904.2024.00030 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S338 | scopus:N6_kashmir_india_bus | 2025 | Sustainability and Capacity Estimation of Photovoltaic Based Distribution Network Integrated with Demand Respo | 10.1007/s40998-024-00762-6 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S340 | scopus:N6_kashmir_india_bus | 2011 | Traffic problems in Jammu City |  | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S341 | scopus:N6_kashmir_india_bus | 2026 | Sustainable and Green Transportation Strategies for Enhanced Urban Liveability: Quantifying Emission Reduction | 10.1016/j.trpro.2026.04.063 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| S342 | scopus:N6_kashmir_india_bus | 2024 | Optimising power distribution systems: solar-powered capacitors and cost reduction through meta-heuristic meth | 10.1504/IJIEI.2024.138864 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S343 | scopus:N6_kashmir_india_bus | 2022 | Application of Public Transport Accessibility Level (PTAL) Study for Accessing Service Gap in Upcoming Metro S | 10.3233/ATDE220773 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | kw |
| S344 | scopus:N6_kashmir_india_bus | 2010 | The national honey bee disease and pest survey: 2009-2010 pilot study |  | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S347 | scopus:N6_kashmir_india_bus | 2026 | Evaluating the socio-economic profile of the tribal communities: insights from Gujjar and Bakarwal areas in Sh | 10.1007/s43545-026-01569-4 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S348 | scopus:N6_kashmir_india_bus | 2017 | Status and distribution pattern of sour cherry (Prunus cerasus I.) in moist temperate region of Jammu & Kashmi |  | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S353 | scopus:N6_kashmir_india_bus | 2023 | Foot-and-Mouth Disease Virus Serotype O Exhibits Phenomenal Genetic Lineage Diversity in India during 2018–202 | 10.3390/v15071529 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| S355 | scopus:N6_kashmir_india_bus | 2024 | Empowering Mobility: Investigating the Mode Choice of Women Commuters in Developing Countries Using Multinomia | 10.1007/978-981-97-8116-4_8 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | kw |
| S356 | scopus:N6_kashmir_india_bus | 2020 | Modelling and Analysis of Mode Choice Behaviour for Work Trips in Srinagar | 10.1007/978-3-030-42363-6_9 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | kw |
| S358 | scopus:N6_kashmir_india_bus | 2025 | Impact of Metro Infrastructure on Emergence and Growth of Commercial Hubs: The Case of Jammu, India | 10.14445/23488352/IJCE-V12I3P110 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | kw |
| X03 | extra:P0122 | 2025 | A Social Impact Calculation and Visualization Method for the Discontinuation of Public Transportation | 10.1109/IES67184.2025.11161056 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| X04 | extra:P0155 | 2025 | Geospatial Analysis of Public Transportation Accessibility for University Students: A Case Study from Mexico | 10.13053/CyS-29-4-5444 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| X06 | extra:P0203 | 2024 | A Study on the Design of Transportation Network Based on OD Flow in Utsunomiya City | 10.1109/GCCE62371.2024.10760476 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | manual |
| O0037 | oa:B_open_data | 2018 | Assessing public transit service equity using route-level accessibility measures and public data | 10.1016/j.jtrangeo.2018.01.005 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0077 | oa:C_india | 2021 | Public transit accessibility approach to understand the equity for public healthcare services: A case study of | 10.1016/j.jtrangeo.2021.103123 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0085 | oa:B_open_data | 2016 | Comparable Measures of Accessibility to Public Transport Using the General Transit Feed Specification | 10.3390/su8030224 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0086 | oa:C_global_south | 2020 | Strategic Planning Based on Sustainability for Urban Transportation: An Application to Decision-Making | 10.3390/su12093589 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0087 | oa:B_open_data | 2018 | A cost-minimization model for bus fleet allocation featuring the tactical generation of short-turning and inte | 10.1016/j.trc.2018.11.007 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0090 | oa:C_global_south | 2015 | AllAboard: Visual Exploration of Cellphone Mobility Data to Optimise Public Transport | 10.1109/tvcg.2015.2440259 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0098 | oa:B_open_data | 2016 | Health research needs more comprehensive accessibility measures: integrating time and transport modes from ope | 10.1186/s12942-016-0052-x | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0131 | oa:C_india | 2019 | Mapping public transport accessibility levels (PTAL) in India and its applications: A case study of Surat | 10.1016/j.cstp.2019.03.004 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0136 | oa:B_open_data | 2019 | Integrating network science and public transport accessibility analysis for comparative assessment | 10.1016/j.jtrangeo.2019.102505 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0137 | oa:C_global_south | 2023 | How much is accessibility worth? Utility-based accessibility to evaluate transport policies | 10.1016/j.jtrangeo.2023.103683 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0139 | oa:C_permit_regulation | 2016 | The benefits of a high-resolution analysis of transit accessibility | 10.1080/13658816.2016.1191637 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0145 | oa:B_open_data | 2022 | The impacts of accessibility measure choice on public transit project evaluation: A comparative study of cumul | 10.1016/j.jtrangeo.2022.103508 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0155 | oa:B_data_scarce | 2019 | A Shared Bus Profiling Scheme for Smart Cities Based on Heterogeneous Mobile Crowdsourced Data | 10.1109/tii.2019.2947063 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0158 | oa:C_india | 2005 | Feeder Bus Routes Generation within Integrated Mass Transit Planning Framework | 10.1061/(asce)0733-947x(2005)131:11(822) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0176 | oa:B_open_data | 2023 | Evaluating the impact of public transport travel time inaccuracy and variability on socio-spatial inequalities | 10.1016/j.jtrangeo.2023.103590 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0179 | oa:B_data_scarce | 2019 | Can passenger flow distribution be estimated solely based on network properties in public transport systems? | 10.1007/s11116-019-09990-w | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0188 | oa:C_global_south | 2023 | Disparities in public transit accessibility and usage by people with mobility disabilities: An evaluation usin | 10.1016/j.jtrangeo.2023.103589 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0192 | oa:C_global_south | 2007 | How Public Transportation's past is Haunting its Future in Bogotá, Colombia | 10.3141/2038-02 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0194 | oa:C_global_south | 2008 | Use of a Hybrid Algorithm for Modeling Coordinated Feeder Bus Route Network at Suburban Railway Station | 10.1061/(asce)0733-947x(2009)135:1(1) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0212 | oa:B_od_estimation;B_data_scarce | 2021 | Estimating the route-level passenger demand profile from bus dwell times | 10.1016/j.trc.2021.103273 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0250 | oa:B_open_data | 2021 | Time-varying accessibility to senior centers by public transit in Philadelphia | 10.1016/j.tra.2021.06.020 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0253 | oa:C_permit_regulation | 2019 | Analysis on Public’s Response Toward Bus Reform Policy in Indonesia Considering Latent Variables | 10.2174/1874447801913010017 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0261 | oa:C_india | 2011 | Achieving sustainable transportation system for Indian cities - problems and issues |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0275 | oa:C_permit_regulation | 2006 | Norwegian experiences with tendered buss services |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0278 | oa:B_open_data | 2023 | Measuring the impacts of disruptions on public transit accessibility and reliability | 10.1016/j.jtrangeo.2023.103769 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0281 | oa:B_open_data | 2018 | Constructing Spatiotemporal Load Profiles of Transit Vehicles with Multiple Data Sources | 10.1177/0361198118781166 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0285 | oa:C_permit_regulation | 2021 | The case for negotiated contracts under the transition to a green bus fleet | 10.1016/j.tra.2021.10.006 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0288 | oa:C_permit_regulation | 2001 | THE EVOLUTION OF ORGANISATIONAL FORMS IN EUROPEAN PUBLIC TRANSPORT |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0297 | oa:C_india | 2020 | Measuring road space consumption by transport modes: Toward a standard spatial efficiency assessment method an | 10.5198/jtlu.2020.1526 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0301 | oa:C_india | 2019 | Bus Passenger Demand Modelling Using Time-Series Techniques- Big Data Analytics | 10.2174/1874447801913010041 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0310 | oa:B_open_data;C_global_south | 2014 | Applying the General Transit Feed Specification to the Global South | 10.3141/2442-06 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0319 | oa:C_global_south | 2008 | Limitation of Competition in and for the Public Transportation Market in Developing Countries | 10.3141/2048-02 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0331 | oa:B_open_data;B_equity | 2017 | Accessibility Scenario Analysis of a Hypothetical Future Transit Network: Social Equity Implications of a Gene | 10.3141/2671-01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0369 | oa:B_equity;C_india | 2021 | Visualising public transport accessibility to inform urban planning policy in Hubli-Dharwad, India | 10.1007/s10708-021-10548-6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0376 | oa:B_open_data | 2020 | Potential and cumulative accessibility of workplaces by public transport in Szczecin | 10.2478/bog-2020-0037 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0380 | oa:C_global_south | 2021 | Assessing accessibility to ASFs from bus stops using distance measures: Case of two Indian cities | 10.1016/j.landusepol.2021.105567 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0384 | oa:B_od_estimation;B_open_data | 2024 | Origin–destination matrix estimation for public transport: A multi-modal weighted graph approach | 10.1016/j.trc.2024.104694 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0392 | oa:C_india | 2021 | Public transport accessibility mapping and its policy applications: A case study of Lucknow, India | 10.1016/j.cstp.2021.08.001 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0398 | oa:B_open_data | 2021 | GIS tools and programming languages for creating models of public and private transport potential accessibilit | 10.1007/s10109-020-00337-z | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0404 | oa:B_open_data | 2019 | A Semi-Automatic Data–Scraping Method for the Public Transport Domain | 10.1109/access.2019.2932197 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0413 | oa:C_global_south | 2005 | Institutional and Regulatory Options for Bus Rapid Transit in Developing Countries: Lessons from International | 10.3141/1939-21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0419 | oa:C_india | 2019 | Travel Time Reliability Analysis on Selected Bus Route of Mysore Using GPS Data | 10.1007/s40890-019-0083-7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0433 | oa:C_permit_regulation | 2013 | Evaluating the impact of bus network planning changes in Sydney, Australia | 10.1016/j.tranpol.2013.07.003 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0473 | oa:B_open_data | 2017 | Space-Time Variation of Accessibility to Jobs with used by Public Transport - case study in Szczecin | 10.7163/eu21.2017.33.4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0476 | oa:B_open_data | 2023 | Quantification and comparison of hierarchy in Public Transport Networks | 10.1016/j.physa.2023.129479 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0485 | oa:B_open_data | 2019 | Smart data at play: improving accessibility in the urban transport system | 10.1080/0144929x.2019.1652852 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0488 | oa:B_open_data;B_accessibility | 2016 | Comparing Accessibility in Urban Slums Using Smart Card and Bus GPS Data |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0490 | oa:C_global_south | 2005 | Institutional and Regulatory Options for Bus Rapid Transit in Developing Countries | 10.1177/0361198105193900121 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0494 | oa:C_global_south | 2015 | Potentials of Online Media and Location-Based Big Data for Urban Transit Networks in Developing Countries | 10.3141/2537-06 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0496 | oa:C_global_south | 2023 | Transforming urban mobility with internet of things: public bus fleet tracking using proximity-based bluetooth | 10.3389/friot.2023.1255995 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0521 | oa:C_india | 2024 | Origin-destination demand prediction of public transit using graph convolutional neural network | 10.1016/j.cstp.2024.101230 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0532 | oa:B_accessibility;B_demand_proxy;C_glob | 2023 | Suitable Bus Stop Locations for a Proposed Bus Rapid Transit Corridor in a Developing Country City: An Analyti | 10.1007/s40890-023-00179-6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0541 | oa:C_global_south | 2025 | Impact of transferring light busses to BRT route on traffic congestion, mobility, and safety at Sweileh inters | 10.5937/jaes0-55112 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0550 | oa:B_open_data | 2024 | Evaluation Framework for Multi-Modal Public Transport Systems Based on Connectivity and Transfers at Stop Leve | 10.1177/03611981241231963 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0561 | oa:B_od_estimation;B_open_data | 2025 | Assessing public transport accessibility using GPS data | 10.1186/s12544-025-00733-w | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0570 | oa:C_india | 2009 | Indian Bus Rapid Transit Systems Funded by the Jawaharlal Nehru National Urban Renewal Mission | 10.3141/2114-02 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0572 | oa:C_india | 2025 | Assessment of Infrastructure and Service Supply on Sustainable Urban Transport Systems in Delhi-NCR: Implicati | 10.3390/futuretransp5040134 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0621 | oa:C_permit_regulation | 2019 | Integrated Transport Planning: The 'Rehabilitation' of a contested concept in UK bus reforms | 10.1016/j.jclepro.2019.05.282 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0633 | oa:B_open_data | 2016 | Lossless Compression of Public Transit Schedules | 10.1109/tits.2016.2542131 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0635 | oa:C_india | 2021 | Does capacity utilisation influence financial performance? A study of Indian public bus transport companies | 10.1108/bij-01-2021-0039 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0638 | oa:B_data_scarce | 2023 | Transferable supervised learning model for public transport service load estimation | 10.1007/s11116-023-10411-2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0639 | oa:C_global_south | 2002 | International Perspective on the Changing Structure of the Urban Bus Market | 10.3141/1799-12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0641 | oa:B_open_data | 2025 | Identifying pharmacy gaps: a spatiotemporal study of multimodal accessibility throughout the day | 10.1186/s12942-025-00396-9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0642 | oa:B_open_data | 2022 | Open Data as a Condition for Smart Application Development: Assessing Access to Hospitals in Croatian Cities | 10.3390/su141912014 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0666 | oa:C_global_south | 2022 | Formalization of East Jerusalem public transport: Mobility, politics and planning | 10.1016/j.jtrangeo.2022.103463 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0687 | oa:C_global_south | 2002 | Cross-town bus routes as a solution for decentralized travel: a cost-benefit analysis for Monterrey, Mexico | 10.1016/s0965-8564(00)00040-9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0688 | oa:C_global_south | 2004 | THE ECONOMICS OF TRANSMILENIO, A MASS TRANSIT SYSTEM FOR BOGOTÁ |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0707 | oa:B_open_data | 2024 | Spillover effects in transit networks: A parameterized weight matrix spatial lagged approach | 10.1016/j.urbmob.2024.100081 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0709 | oa:B_open_data | 2025 | Examining the spatial disparities of urban public transport fares in Kumasi, Ghana – Are fares consistent by r | 10.1016/j.aftran.2025.100032 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0710 | oa:B_open_data | 2021 | Optimizing Transit Equity and Accessibility of the City of Charlotte, North Carolina, by Integrating Transit G | 10.1061/jtepbs.0000503 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0716 | oa:B_open_data | 2013 | GO_Sync — A Framework to Synchronize Crowd-Sourced Mapping Contributors from Online Communities and Transit Ag | 10.1007/s13177-013-0056-x | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0728 | oa:C_global_south | 2019 | Network Centrality Analysis of Public Transport Systems: Developing a Strategic Planning Tool to Assess Passen | 10.35940/ijitee.j1086.08810s19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0739 | oa:C_global_south | 2020 | Market initiative and central planning: A study of the Moscow bus network | 10.1016/j.retrec.2020.100919 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0743 | oa:B_open_data | 2023 | Simplified geodata models for integrated urban and public transport planning | 10.5194/agile-giss-4-32-2023 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0748 | oa:B_open_data | 2022 | Digital traces: Mapping Bogotá’s unmapped transit network using smartphones and networked databases | 10.1177/23998083221117831 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0749 | oa:C_india;C_global_south | 2017 | A Conceptual Approach for Optimising Bus Stop Spacing | 10.1007/s40030-017-0199-x | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0753 | oa:C_india | 2014 | Bus Karo 2.0 Case Studies from India |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0759 | oa:B_open_data | 2014 | Proof Of Concept: GTFS Data As A Basis For Optimization Of Oregon’s Regional And Statewide Transit Networks |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0784 | oa:B_open_data | 2020 | Adding Semantics to Enrich Public Transport and Accessibility Data from the Web |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0794 | oa:B_open_data | 2023 | “How Far Is the Closest Bus Stop?” An Evaluation of Self-Reported versus GIS-Computed Distance to the Bus amon | 10.3390/geomatics3040031 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0822 | oa:C_global_south | 2021 | Peran Kebijakan dalam Peningkatan Performa Layanan BRT Transjakarta | 10.35718/specta.v5i3.373 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0851 | oa:B_open_data | 2021 | Geospatially Partitioning Public Transit Networks for Open Data Publishing | 10.13052/jwe1540-9589.2045 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0869 | oa:B_open_data | 2015 | Quality Assessment of Open Realtime Data for Public Transportation in the Netherlands | 10.1553/giscience2015s579 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0919 | oa:C_global_south | 2025 | Understanding the Conditions for Passengers to Consider Accepting Transfers between MyCiTi and Minibus Taxi | 10.1016/j.trpro.2025.05.048 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0923 | oa:C_global_south | 2025 | A framework for assessing the financial sustainability of minibus taxi route typologies by means of onboard tr | 10.1016/j.aftran.2024.100022 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0928 | oa:B_open_data | 2018 | The HARMONY project – Study for the harmonization of data in the public transport network and road network | 10.5281/zenodo.1485705 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0934 | oa:B_open_data | 2019 | Leveraging Twitter and Machine Learning for Real-Time Transit Network Evaluation |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0942 | oa:C_india | 2004 | URBAN PUBLIC TRANSPORT IN INDIA: TRENDS, CHALLENGES AND INNOVATIONS |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O0952 | oa:B_open_data | 2023 | Modeling the accessibility of public transport to people with disabilities in the GTFS standard | 10.53502/rail-176332 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1011 | oa:B_open_data | 2025 | Dynamic public transit accessibility analysis using actual transit operation data | 10.1080/12265934.2025.2503727 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1028 | oa:C_india | 2025 | The Illusion of Inclusion: Examining the Failure of Accessibility Implementation of Public Transport Systems i | 10.62225/2583049x.2025.5.4.4821 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1040 | oa:C_india | 2025 | Performance evaluation and design of multi-modal transport system for integrated transit hubs | 10.1680/jmuen.25.00015 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1051 | oa:B_open_data | 2025 | Understanding the interplay between public transport travel time variability and jobs competition on accessibi | 10.1016/j.jtrangeo.2025.104526 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1071 | oa:C_india | 2005 | Traveller information system in GIS : a case study of Hyderabad city |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1075 | oa:C_india | 2026 | Who decides, who pays: Evaluating equity in financial decision making in Bengaluru’s public bus system | 10.1080/29941849.2026.2643104 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1143 | oa:C_permit_regulation | 2006 | Three issues dominate 'third way' bus regulation |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1154 | oa:B_open_data | 2018 | Developing a new job accessibility measurement based on crowdsourced traffic data and GTFS |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1157 | oa:B_open_data | 2025 | Coverage of digital public transport information in Poland | 10.24136/tren.2025.002 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1158 | oa:B_open_data | 2026 | GTFS-Based Changes and Spatial Inequality in Interregional Public Transport Mobility-Based Accessibility : A C | 10.7470/jkst.2026.44.3.482 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1159 | oa:B_open_data | 2018 | Decentralized open data publishing for the public transport route planning ecosystem |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1160 | oa:B_open_data | 2026 | A GTFS-Based Dataset for the US Intercity Bus Network | 10.32866/001c.159284 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1164 | oa:B_open_data | 2017 | Using the GTFS format to improve public transport data accessibility in Gauteng |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1308 | oa:B_accessibility;B_demand_proxy;B_equi | 2026 | Identifying detour patterns of rail feeder bus routes: A city-scale analysis | 10.1016/j.jtrangeo.2026.104816 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1317 | oa:B_data_scarce | 2011 | Expanding a Multi-agent Transport Model with Limited Data: A South African Case Study |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1349 | oa:C_india | 2025 | Continuity Analysis of Passenger-Centric Metrics and Economic Outcomes in TNSTC (Town Bus) Services | 10.14419/77ajfs03 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1353 | oa:C_india | 2025 | Micro-public transport accessibility mapping to enhance local area planning (LAP) in Ahmedabad | 10.1016/j.cstp.2025.101455 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1360 | oa:C_india | 2018 | PLANNING FOR A FORMULATED GROWTH OF URBAN TRANSPORTATION IN JALANDHAR CITY |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1387 | oa:C_india | 2016 | Beyond Engineering: Political Economy in BRT Planning |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1405 | oa:C_india | 2009 | The Success Story of Transport Authority in Delhi |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1414 | oa:C_india | 2026 | A Study on the Economic and Operational Performance of Maharashtra State Road Transport Corporation (MSRTC) | 10.5281/zenodo.20580028 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1415 | oa:C_india | 2026 | A Study on the Economic and Operational Performance of Maharashtra State Road Transport Corporation (MSRTC) | 10.5281/zenodo.20580029 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1470 | oa:B_open_data | 2026 | Open source Digital Twin development pipeline for Public Transport: A case study in Stockholm | 10.1016/j.jpubtr.2026.100149 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1492 | oa:B_open_data | 2016 | 2016 (May) Mass Transit Spatial Layers for New York City Geodatabase |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1519 | oa:B_open_data | 2014 | A Recipe for an Online, Geospatial Transit Performance Archive |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1522 | oa:B_open_data | 2023 | Role discovery in node-attributed public transportation networks: the study of Saint Petersburg city open data | 10.17586/2226-1494-2023-23-3-553-563 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1526 | oa:B_open_data | 2019 | Webinar: Social Transportation Analytic Toolbox (STAT) for Transit Networks |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1562 | oa:C_global_south | 2021 | Understanding The Reform Of Public Transit In India |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1589 | oa:C_global_south | 2026 | Improving urban mobility through a chartered bus policy for large employers: a public policy and optimization- | 10.1080/03081060.2026.2675480 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1595 | oa:C_global_south | 2000 | TRANSIT-ASSIGNMENT MODELS. IN: HANDBOOK OF TRANSPORT MODELLING |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1597 | oa:C_permit_regulation | 2009 | MYTHS AND LEGENDS BY LI FUQING B.L. Riftin – 75 years | 10.1016/j.aeae.2009.08.018 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| O1643 | oa:C_permit_regulation | 2016 | Comparison of Functions Performed of Transport Authorities: Similarities and Differences |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S065 | scopus:N2_demand_free | 2026 | From ownership to access: Policies to support the growth of peer-to-peer car sharing in Italy | 10.1016/j.tranpol.2025.103989 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S067 | scopus:N2_demand_free | 2020 | A techno-economic assessment of energy efficiency in energy management of a micro grid considering green-virtu | 10.1016/j.scs.2020.102169 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S068 | scopus:N2_demand_free | 2025 | Sustainable Urban Transportation via Hydrogen-Enabled Integrated Energy System | 10.1109/AIoT66900.2025.00060 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S069 | scopus:N2_demand_free | 2012 | Research on in-vehicle bus network based on internet of things | 10.1109/ICCIS.2012.245 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S083 | scopus:N2_demand_free | 2025 | Resilience Evaluation Method for Rail Transit Networks Considering Dynamic Passenger Flows | 10.4271/2025-99-0438 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S086 | scopus:N2_demand_free | 2025 | Multi-agent reinforcement learning with causal communication for ride-sourcing pricing in mixed autonomy mobil | 10.1016/j.trc.2025.105164 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S088 | scopus:N2_demand_free | 2019 | Examining walk access to brt stations: A case study of ahmedabad brts |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S089 | scopus:N2_demand_free | 2016 | Assessment of the potential for modal shift to non-motorised transport in a developing context: Case of Lima,  | 10.1016/j.retrec.2016.05.010 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S093 | scopus:N2_demand_free | 2000 | A study of transmission planning under a deregulated environment in power system | 10.1109/DRPT.2000.855742 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S094 | scopus:N2_demand_free | 2006 | Modeling the strategic bidding of the producers in competitive electricity markets with the Watkins's Q(lambda |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S095 | scopus:N2_demand_free | 2026 | Eco-industrial park planning based on industrial ecology and ecological network analysis | 10.22034/gjesm.2026.04.13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S097 | scopus:N2_demand_free | 2025 | Integrating shared electric micromobility and public transport – A practitioner's perspective | 10.1016/j.jcmr.2025.100069 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S099 | scopus:N2_demand_free | 2026 | How Metro Expansion Influences Enterprise Labor Misallocation | 10.1111/ecpo.70042 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S100 | scopus:N2_demand_free | 2014 | Social welfare maximization of multimodal transportation: Theory, metamodel, and application to Tianjin Ecocit | 10.3141/2451-05 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S101 | scopus:N2_demand_free | 2010 | Long-term effects of feed-in tariffs and carbon taxes on distribution systems | 10.1109/TPWRS.2009.2038783 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S103 | scopus:N2_demand_free | 2020 | Evaluating Automated Demand Responsive Transit Using Microsimulation | 10.1109/ACCESS.2020.2991154 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S104 | scopus:N2_demand_free | 2004 | Short-term prediction of vehicle occupancy in advanced public transportation information systems (aptis) | 10.1007/978-1-4757-6467-3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S109 | scopus:N2_demand_free | 2017 | Demand variations and evacuation route flexibility in short-notice bus-based evacuation planning | 10.1016/j.iatssr.2017.01.002 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S110 | scopus:N2_demand_free | 2020 | Optimal allocation of distributed generations considering demand response and multi-agent benefits | 10.1109/EI250167.2020.9347355 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S114 | scopus:N2_demand_free | 2020 | Exploring the Dynamic Voltage Signature of Renewable Rich Weak Power System | 10.1109/ACCESS.2020.3041410 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S116 | scopus:N2_demand_free | 2019 | Comprehensive Evaluation of Grid Adaptability Considering Rolling Access of Cascade Power Stations | 10.1109/iSPEC48194.2019.8975238 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S119 | scopus:N2_demand_free | 2017 | Integrating public transport into mobiTopp | 10.1016/j.procs.2017.05.401 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S120 | scopus:N2_demand_free | 2014 | Braess-like paradox in transit network: Activity approach |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S121 | scopus:N2_demand_free | 2010 | Transmission network planning under a price-based demand response program | 10.1109/TDC.2010.5484267 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S122 | scopus:N2_demand_free | 2026 | Fusing Cellular Network Data and Tollbooth Counts for Urban Traffic Flow Estimation | 10.1109/SM69703.2026.11614143 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S124 | scopus:N2_demand_free | 2018 | Improved understanding of the relative quality of bus public transit using a balanced approach to performance  | 10.1016/j.tra.2017.11.019 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S128 | scopus:N2_demand_free | 2026 | Unveiling the challenges and opportunities of autonomous bus integration in rural and suburban areas: An exper | 10.1016/j.trip.2026.102072 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S129 | scopus:N2_demand_free | 2024 | Design an intermediary mobility-as-a-service (MaaS) platform using many-to-many stable matching framework | 10.1016/j.trb.2024.102991 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S134 | scopus:N2_demand_free | 2026 | Behaviorally informed optimization of mobility-as-a-service bundle and fleet design for car users | 10.1016/j.tre.2026.105095 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S137 | scopus:N2_demand_free | 2025 | Risk-constrained optimization of joint spatio-temporal flexibility of mobile energy storage and data centers u | 10.1016/j.egyr.2025.11.098 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S138 | scopus:N2_demand_free | 2022 | Open Data as a Condition for Smart Application Development: Assessing Access to Hospitals in Croatian Cities | 10.3390/su141912014 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S140 | scopus:N2_demand_free | 2022 | Interdicting International Drug Trafficking: a Network Approach for Coordinated and Targeted Interventions | 10.1007/s10610-020-09473-0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S141 | scopus:N2_demand_free | 2009 | Innovation in affordable housing in Australia: Bringing policy and practice for not-for-profit housing organis |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S147 | scopus:N2_demand_free | 2024 | On Source-Network-Load Multi-Body Economic Operation Planning Strategy Considering Transmission Blockage | 10.1109/ICPEA63589.2024.10784560 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S149 | scopus:N2_demand_free | 2021 | Market power assessment in electricity markets based on social network analysis | 10.1016/j.compeleceng.2021.107302 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S152 | scopus:N2_demand_free | 2024 | Operational Strategy of a DC Inverter Heat Pump System Considering PV Power Fluctuation and Demand-Side Load C | 10.3390/buildings14041139 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S155 | scopus:N2_demand_free | 2022 | A New Algorithm for Harmonic Impacts with Renewable DG and Non-linear Loads in Smart Distribution Networks | 10.1007/s40866-022-00134-1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S156 | scopus:N2_demand_free | 2002 | Anti-narcotics responses in Jordan |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S157 | scopus:N2_demand_free | 2021 | Virtual storage plants in parking lots of electric vehicles providing local/global power system support | 10.1016/j.est.2021.103249 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S159 | scopus:N2_demand_free | 2021 | Before-and-after evaluation of a bus network improvement using performance indicators from historical smart ca | 10.1007/s12469-019-00214-z | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S163 | scopus:N2_demand_free | 2025 | Vision-Based Few-Shot Railway Intrusion Detection via Dual-Detector and Contrastive Learning | 10.1109/JSEN.2025.3592669 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S169 | scopus:N2_demand_free | 2017 | Crowding cost estimation with large scale smart card and vehicle location data | 10.1016/j.trb.2016.10.015 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S170 | scopus:N2_demand_free | 2006 | Investigating smooth power flow control for dispersed generator working parallel to the grid system on the loa | 10.1109/PSCE.2006.296312 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S171 | scopus:N2_demand_free | 2023 | Design of dynamic voltage restorer in the power quality improvement for voltage problems | 10.1007/s13204-022-02364-2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S172 | scopus:N2_demand_free | 2022 | Optimization of Transport Services Based on the K Shortest Path Algorithm | 10.1109/ICAMechS57222.2022.10003423 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S173 | scopus:N2_demand_free | 2023 | Design and Application of An Integrated Energy Management System for Park Enterprises | 10.1109/PowerCon58120.2023.10331517 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S174 | scopus:N2_demand_free | 2004 | Schedule-based dynamic assignment models for public transport networks | 10.1007/978-1-4757-6467-3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S178 | scopus:N2_demand_free | 2020 | Scheduling energy storage to provide balancing during line contingency at high wind penetration | 10.1007/978-981-15-0214-9_93 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S179 | scopus:N2_demand_free | 2023 | Managerial decisions to recover from Covid-19 disruption: A multi-objective optimization approach applied to p | 10.1016/j.treng.2023.100163 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S180 | scopus:N2_demand_free | 2020 | Assessing the impacts of automated mobility-on-demand through agent-based simulation: A study of Singapore | 10.1016/j.tra.2020.06.004 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S185 | scopus:N2_demand_free | 2026 | Predicting Public Transit Demand Using Urban Imagery with a Dual-Latent Deep Learning Framework | 10.3390/su18010067 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S189 | scopus:N2_demand_free | 2012 | Missed connections: Quantifying and optimizing multi-modal interconnectivity in cities | 10.1145/2442942.2442948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S190 | scopus:N2_demand_free | 2014 | A FlexiFare Bus (F2B) system to reduce bus bunching problem | 10.1109/PIC.2014.6972415 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S192 | scopus:N2_demand_free | 2020 | Integrating public transport into mobiTopp | 10.1016/j.future.2017.12.051 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S193 | scopus:N2_demand_free | 2007 | Promoting transit oriented development in the Atlantis Corridor, Cape Town: Towards an implementable model |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S194 | scopus:N2_demand_free | 2018 | Optimal Charging Schemes for Electric Vehicles in Smart Grid: A Contract Theoretic Approach | 10.1109/TITS.2018.2841965 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S195 | scopus:N2_demand_free | 2026 | Local stakeholders' perspectives on food-related wellness tourism in Central Vietnam: Challenges and opportuni | 10.1080/02508281.2025.2506177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S196 | scopus:N2_demand_free | 2021 | Low-carbon economic dispatch of integrated electricity and natural gas energy system considering carbon captur | 10.1177/01423312211060572 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S197 | scopus:N2_demand_free | 2024 | Multi-objective Adaptive Fuzzy Campus Placement based Optimization Algorithm for optimal integration of DERs a | 10.1016/j.est.2023.109682 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S200 | scopus:N2_demand_free | 2025 | Supply of the hydrogen refuelling stations in the Hungarian part of the Trans-European Transport Network – com | 10.1016/j.ijhydene.2025.152084 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S201 | scopus:N2_demand_free | 2024 | Solution to Objectives of Supply Side Energy Management by Integrating Enhanced Demand Response Strategy | 10.22098/joape.2023.11565.1861 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S202 | scopus:N2_demand_free | 2019 | Rational choice in everyday mobility decisions of Austrian employees | 10.1080/23800127.2019.1573779 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S207 | scopus:N2_demand_free | 2026 | Coordinated scheduling and pricing for public transport-oriented MaaS systems: A passenger-centric approach | 10.1016/j.trc.2026.105687 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S208 | scopus:N2_demand_free | 2024 | Partial Electrification Strategies for Diesel Commuter Rail’s Climate Challenge | 10.1177/03611981231179468 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S209 | scopus:N2_demand_free | 2026 | Smart Mobility and Last-Mile Rail Integration | 10.3390/encyclopedia6010026 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S217 | scopus:N2_demand_free | 2021 | Providing Flexibility in Distribution Systems by Electric Vehicles and Distributed Energy Resources in the Con | 10.1109/EEEIC/ICPSEurope51590.2021.9584698 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S219 | scopus:N2_demand_free | 2026 | Zero-shot cross-city ride-hailing demand prediction leveraging transferable urban spatiotemporal dynamics | 10.1016/j.tra.2026.105233 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S220 | scopus:N2_demand_free | 2025 | Integrated practice of photovoltaic, energy storage, DC micro-grid and flexible energy control technologies in | 10.1088/1742-6596/3001/1/012025 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S221 | scopus:N2_demand_free | 2006 | Network constraint impacts on the competitive electricity markets under supply-side strategic bidding | 10.1109/TPWRS.2005.857833 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S223 | scopus:N2_demand_free | 2019 | Discovery of public transportation patterns through the use of big data technologies for urban mobility | 10.1115/IMECE2019-11415 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S225 | scopus:N2_demand_free | 2024 | Faster Convergence of Integrated Activity-Based Models in Dynamic Multimodal Transit Assignment Using Macrosco | 10.1177/03611981231220563 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S226 | scopus:N2_demand_free | 2024 | Meta-learning based passenger flow prediction for newly-operated stations | 10.1007/s10707-023-00510-8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S227 | scopus:N2_demand_free | 2021 | Research on Source-Load Coordination Improving the Flexibility of Power System with High Proportional Wind Pow | 10.1109/ACPEE51499.2021.9436995 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S229 | scopus:N2_demand_free | 2016 | Route choice of containership on a global scale and model development: Focusing on the Suez Canal |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S230 | scopus:N2_demand_free | 2005 | Transportation policies for the elderly and disabled in Japan | 10.1080/12265934.2005.9693575 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S231 | scopus:N2_demand_free | 2026 | Mechanisms of Air Transport Network Accessibility from the Supply-Side Perspective: Empirical Evidence from Xi | 10.1007/978-981-95-3019-9_42 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S233 | scopus:N3_open_fleet | 2024 | Moderation Effects of Streetscape Perceptions on the Associations Between Accessibility, Land Use Mix, and Bik | 10.2196/58761 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S255 | scopus:N4_permit_reform | 2025 | Quantitative urban economics ☆ | 10.1016/bs.hesreg.2025.06.007 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S259 | scopus:N5_proxy_headway | 2024 | Sustainability Challenges: How Public Transport Supports Eco-Tourism Industries | 10.1088/1755-1315/1395/1/012026 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S261 | scopus:N5_proxy_headway | 2026 | Degradation-constrained multi-agent reinforcement learning with centralized training and decentralized executi | 10.1038/s41598-026-55471-3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S262 | scopus:N5_proxy_headway | 2023 | Microtransit adoption in the wake of the COVID-19 pandemic: Evidence from a choice experiment with transit and | 10.1016/j.trc.2023.104395 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S264 | scopus:N5_proxy_headway | 2021 | Car users’ attitudes towards an enhanced bus system to mitigate urban congestion in a developing country | 10.1016/j.tranpol.2021.06.013 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S266 | scopus:N5_proxy_headway | 2001 | Development of feeder routes for Suburban railway stations using heuristic approach | 10.1061/(ASCE)0733-947X(2001)127:4(334) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S267 | scopus:N5_proxy_headway | 2013 | Analyzing demands and activities of public transit users from the accesses to the public transit guidance serv |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S268 | scopus:N5_proxy_headway | 2024 | A multi-task deep learning framework for forecasting sparse demand of demand responsive transit | 10.1016/j.eswa.2024.123833 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S269 | scopus:N5_proxy_headway | 2021 | Smart school routing problem for the new normality |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S272 | scopus:N5_proxy_headway | 2022 | Research on Customized Bus Demand Identification and Route Layout | 10.1061/9780784484265.128 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S282 | scopus:N5_proxy_headway | 2011 | Evaluation of bus service reliability based on avl information | 10.1061/41186(421)287 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S285 | scopus:N5_proxy_headway | 2023 | A simulation-optimization approach to solve the first and last mile of mass rapid transit via feeder services | 10.1016/j.trpro.2023.02.234 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S287 | scopus:N5_proxy_headway | 2021 | Estimating bicycle demand in an aggressive environment | 10.1080/15568318.2020.1734886 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S294 | scopus:N5_proxy_headway | 2020 | Model for future thin-haul air mobility demand in Germany | 10.1109/ICE/ITMC49519.2020.9198496 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S295 | scopus:N5_proxy_headway | 2013 | A log analyzer of public transit guidance service to improve a route bus service | 10.1007/978-3-642-39137-8_32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S298 | scopus:N5_proxy_headway | 2026 | Optimization of Feeder Buses Route to Connect High-Speed Railway Stations with Urban Areas † | 10.3390/engproc2025121006 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S299 | scopus:N5_proxy_headway | 2017 | Estimating light-rail transit peak-hour boarding based on accessibility at station and route levels in Wuhan,  | 10.1080/03081060.2017.1314497 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S303 | scopus:N5_proxy_headway | 2017 | Route Design Model of Feeder Bus Service for Urban Rail Transit Stations | 10.1155/2017/1090457 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S305 | scopus:N5_proxy_headway | 2023 | Designing and planning sustainable customized bus service for departing attendees of planned special events: A | 10.1016/j.scs.2023.104630 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S307 | scopus:N5_proxy_headway | 2020 | Travelers' Potential Demand toward Flex-Route Transit: Nanjing, China, Case Study | 10.1061/(ASCE)UP.1943-5444.0000538 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S308 | scopus:N5_proxy_headway | 2005 | Feeder bus routes generation within integrated mass transit planning framework | 10.1061/(ASCE)0733-947X(2005)131:11(822) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S312 | scopus:N5_proxy_headway | 2026 | Equity-aware optimization for urban transit decarbonization: Modeling and case study | 10.1016/j.scs.2026.107297 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S314 | scopus:N5_proxy_headway | 2025 | Where is the potential market for Taiwanese carriers to launch new direct flight services in the US? | 10.1016/j.trpro.2024.12.136 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S323 | scopus:N5_proxy_headway | 2020 | Bridging the gap between weak-demand areas and public transport using an ant-colony simulation-based optimizat | 10.1016/j.trpro.2020.03.012 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S325 | scopus:N6_kashmir_india_bus | 2022 | The impact of construction of hill roads on the environment, assessed using the multi-criteria approach | 10.1080/00207233.2021.1905298 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S326 | scopus:N6_kashmir_india_bus | 2020 | A retrospective study of fatal road traffic accident cases in a hilly region of Uttarakhand | 10.5958/0974-083X.2020.00100.4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S327 | scopus:N6_kashmir_india_bus | 2020 | Impact of Car Restrictive Policies: A Case Study of Srinagar City in JandK State India | 10.1016/j.trpro.2020.08.245 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | manual |
| S328 | scopus:N6_kashmir_india_bus | 2025 | Isolation and characterization of Lactic acid Bacteria from spontaneously fermented kohlrabi pickle of Jammu a | 10.1016/j.afres.2025.100973 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S329 | scopus:N6_kashmir_india_bus | 2026 | Evaluating Public Acceptance of Congestion Pricing in Developing Nations: An Indian Case Study | 10.1007/978-981-96-8444-1_5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S332 | scopus:N6_kashmir_india_bus | 2024 | Performance Evaluation of Electrical Distribution System Implementing Revamped Distribution Sector Scheme (RDS | 10.1109/SILCON63976.2024.10910719 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S333 | scopus:N6_kashmir_india_bus | 2003 | Crisis and conflict in South Asia after September 11, 2001 | 10.1177/097152310301000203 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S336 | scopus:N6_kashmir_india_bus | 2020 | Quantitative assessment of exposure of heavy metals in groundwater and soil on human health in Reasi district, | 10.1007/s10653-019-00294-7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S337 | scopus:N6_kashmir_india_bus | 2025 | Commuting in cold weather geographies: how weather-related public transport perceptions, trip attributes, and  | 10.1007/s41062-025-02154-z | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S339 | scopus:N6_kashmir_india_bus | 2023 | Jeopardizing Children’s Future: Insincere Reconciliation in Jammu and Kashmir | 10.1080/10402659.2023.2165877 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S345 | scopus:N6_kashmir_india_bus | 2007 | Indian power projection in the greater middle east: Tools and objectives | 10.1163/156914907X207810 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | off-topic |
| S346 | scopus:N6_kashmir_india_bus | 2016 | Cross-border firing and injury patterns | 10.4103/0974-2700.173864 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S349 | scopus:N6_kashmir_india_bus | 2025 | Acceptability of congestion pricing system in developing countries: A case study in India | 10.1016/j.cstp.2025.101458 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S350 | scopus:N6_kashmir_india_bus | 2021 | The transition to greener ways at Parsa’s | 10.1108/EEMCS-09-2020-0326 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S351 | scopus:N6_kashmir_india_bus | 2014 | Clinical pattern of chronic low backache. A prospective study of 210 cases at a multidisciplinary hospital |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S352 | scopus:N6_kashmir_india_bus | 2006 | The India-Pakistan peace process | 10.1080/14751790601104357 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S354 | scopus:N6_kashmir_india_bus | 2006 | The contribution of track II towards India-Pakistan relations | 10.1177/097152310601300203 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |
| S357 | scopus:N6_kashmir_india_bus | 2020 | National security exception in the general agreement on tariffs and trade (GATT) and India–Pakistan trade | 10.2139/ssrn.3394759 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | kw |

---
## Verification addendum (main session, 2026-10-01)
All six closest-paper DOIs resolved on Crossref (title, year, venue confirmed):
- 10.1016/j.trip.2026.101859 — Sánchez-Atondo, García, Gutiérrez (2026), TRIP — "Reorganization of public transport systems in Global South cities and its relation with quality…"
- 10.1016/j.jtrangeo.2016.12.005 — **Ruiz, Seguí-Pons, Mateu-Lladó (2017)**, JTG — "Improving Bus Service Levels and social equity through bus frequency modelling". ⚠ Cite first author as **Ruiz**, not "Ruiz-Pérez" (as written above).
- 10.1016/j.tra.2025.104747 — Barzegari, Taubkin, Barsukov (2026), TR-A — "A comprehensive analysis of duplication in public transportation"
- 10.1016/j.jtrangeo.2023.103643 — Dumedah, Abass, Gyasi (2023), JTG — paratransit terminals and routes in Ghana
- 10.1007/s42421-025-00116-6 — Mittal & Ukkusuri (2025), Data Science for Transportation — "Overcoming Data Scarcity in Transit Planning…"
- 10.1080/23754931.2026.2646852 — Liu & Rosenberg (2026), Papers in Applied Geography — rural transit accessibility with ArcGIS and GTFS
Full texts still required (publisher-blocked for automated access) before §2 is finalised.
