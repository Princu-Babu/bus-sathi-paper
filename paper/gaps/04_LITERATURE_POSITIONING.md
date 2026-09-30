# Gap 4 — Literature Positioning & the Missing Reference List

**Severity: CRITICAL for submission (no `.bib` exists) + HIGH for framing.**

Two problems: (1) the repo has **no bibliography at all**, so every method the prose name-drops is
uncited; (2) the paper has not yet been *positioned* against the closest published work, which a
*Transport Policy* reviewer will expect in §1–§2. This document gives the minimum canonical set to cite
and the framing that distinguishes this study from what already exists.

> **Verification note.** The positioning claims below were checked against the literature via web
> search on 2026-09-08 (Google Scholar). Where a specific comparison number is cited it is from a named
> paper; where the field is characterised ("thinly published"), that is a considered judgement from the
> search, not a hard count. Do not present the novelty claim as if it were exhaustively proven — present
> it as "to our knowledge."

---

## A. Minimum canonical reference set (build `paper/references.bib` from this)

**Transit planning & service standards**
- Vuchic, V. R. (2005). *Urban Transit: Operations, Planning, and Economics.* Wiley. — headway/fleet fundamentals.
- Ceder, A. (2016). *Public Transit Planning and Operation: Modeling, Practice and Behavior*, 2nd ed. CRC Press. — the frequency→fleet chain.
- TCRP Report 165 (2013). *Transit Capacity and Quality of Service Manual (TCQSM)*, 3rd ed. TRB. — service frequency / QoS standards, cited for headway logic.

**Accessibility & catchments (the core methodological contribution)**
- El-Geneidy, A. et al. (2014). "New evidence on walking distances to transit stops." *Transportation*. — network vs Euclidean walksheds; direct antecedent.
- Untermann, R. (1984). *Accommodating the Pedestrian.* — the 400 m ped-shed convention.
- Gutiérrez, J. & García-Palomares, J. C. (2008). "Distance-measure impacts on the calculation of transport service areas using GIS." *Environment and Planning B*. — Euclidean-vs-network service-area bias; **cite as the closest prior formalisation**.
- Biba, S., Curtin, K. M., & Manca, G. (2010). "A new method for determining the population with walking access to transit." *IJGIS*. — network-based transit catchment population; direct comparator.

**Population & opportunity surfaces**
- Tatem, A. J. (2017). "WorldPop, open data for spatial demography." *Scientific Data* 4:170004. — the population raster.
- (OSM POI use is conventional; cite OpenStreetMap contributors + a VGI-bias paper, e.g. Barrington-Leigh & Millard-Ball 2017, "The world's user-generated road map is more than 80% complete," *PLoS ONE*.)

**Classification & weighting**
- Jenks, G. F. (1967). "The data model concept in statistical mapping." *International Yearbook of Cartography*. — natural breaks.
- Shannon, C. E. (1948) + Zou, Yun & Sun (2006, *J. Environ. Sci.*) — entropy weighting of a composite index.
- (PCA weighting: any standard multivariate reference, e.g. Jolliffe 2002.)

**Routing & uncertainty**
- Luxen, D. & Vetter, C. (2011). "Real-time routing with OpenStreetMap data." *ACM SIGSPATIAL*. — OSRM.
- Sobol', I. M. (2001). "Global sensitivity indices for nonlinear mathematical models." *Math. Comput. Simul.* — variance decomposition (needed once `a09` runs).
- Saltelli, A. et al. (2008). *Global Sensitivity Analysis: The Primer.* — MC/Sobol practice.

**Equity (once `a12` runs)**
- Delbosc, A. & Currie, G. (2011). "Using Lorenz curves to assess public transport equity." *J. Transport Geography*. — accessibility Gini.

---

## B. Closest published work & how we differ

**Euclidean-vs-network catchment bias is NOT new** — Gutiérrez & García-Palomares (2008), Biba et al.
(2010), and El-Geneidy et al. (2014) all establish that straight-line buffers overstate transit
catchment population. All three are verified and shipped in `paper/references.bib`.

> **CORRECTED 2026-09-13 — an unverifiable citation was removed from this paragraph.** An earlier
> version of this document claimed that "Li et al. 2022 report Euclidean/network area ratios around
> 1.3", and used that to argue our 37.4% median overstatement "sits squarely inside the documented
> range". **The reference-verification pass could not identify any such paper** (Crossref, OpenLibrary,
> Wayback; WebSearch was abandoned after it returned model-generated bibliographic text). It is
> therefore **not in the `.bib`, and the 1.3 ratio must not enter the manuscript.**
>
> The argument does not need it. Gutiérrez & García-Palomares, Biba et al. and El-Geneidy et al. already
> establish the buffer-overstatement point qualitatively, which is all §2 has to concede. If a
> *quantitative* range comparison is wanted, someone must find and verify a real source for it — until
> then, 37.4% is reported as **our measurement**, not as a value positioned inside a published band.

**We must cite the three verified works above and claim only that we
*apply* the correction at network scale to a rationalisation-and-fleet decision — not that we invented
the network-catchment critique.** Claiming novelty on the catchment method itself would be rejected.

**Where we are genuinely novel (to our knowledge):** the *combination* — an entirely **open-data,
demand-free** pipeline that (a) deconstructs a permit register into corridors, (b) prioritises via an
open population+POI composite index, (c) sizes fleet from routing-engine cycle times, and (d) validates
the *supply chain* against real driver GPS — assembled specifically for a **demand-data-scarce**
governance context. Web search did not surface a paper doing all four together for bus rationalisation.
That is the defensible contribution: **method integration + the honest supply-side-only validation
stance**, not any single technique.

**The framing that sells it:** "planning what you cannot count." The paper's value to *Transport
Policy* is the **policy method** for cities that will never have AFC/ridership data — plus the candid
demonstration (via GPS) that the plan's own engine mis-times itself, which is a transferable cautionary
finding about uncalibrated routing-engine fleet sizing.

---

## C. Actions

1. Create `paper/references.bib` with at least the set in §A.
2. Attach `\cite` keys at every method mention in §4 and every framing claim in §1–§2 (§1/§2 not yet written — Gap 2).
3. In §1/§2, explicitly cite Gutiérrez & García-Palomares (2008) and Biba et al. (2010) and state that the catchment critique is established, positioning our contribution as *application at rationalisation scale + open-data integration + supply-side validation honesty*.
4. Add the equity/Sobol references only once `a12`/`a09` have actually run (do not cite methods the paper does not yet execute).
