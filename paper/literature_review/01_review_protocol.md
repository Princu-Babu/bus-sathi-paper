# §2.1 Review protocol — design document

Status: DRAFT v1 (2026-09-30). Everything marked ⟨confirm⟩ needs author sign-off before it goes in the paper.

## 1. Purpose
Code 45–60 studies into a synthesis matrix (Table 1) so that §2.8 can **show** (cross-tab) — not merely claim — that implementable bus-network plans cluster at high demand-data intensity, while open-data studies stop at assessment/diagnosis.

Review type: **structured (semi-systematic) literature review** with a reproducible search + snowballing. Not a full PRISMA systematic review — we say "structured review following PRISMA-style reporting of the search and screening" (defensible and honest).

## 2. Research questions
- RQ1 What data does each family of bus network design / rationalisation methods require, and at which planning stage does demand data enter?
- RQ2 Which studies produce an implementable network plan (routes + frequencies/fleet for a real city), and at what data intensity?
- RQ3 What demand-independent / accessibility-based / open-data approaches exist, and how far down the planning chain do they go?
- RQ4 How are equity and validation handled, especially in Indian / Global South, permit-based or informal systems?

## 3. Sources
- **Primary (executed, reproducible):** OpenAlex (open index of Scopus/WoS/Crossref-scale literature; query + date logged; API).
- **Supplementary ⟨confirm⟩:** Scopus via institutional access — same strings run by an author, export CSV; merged + de-duplicated by DOI.
- **Snowballing:** backward (reference lists) and forward (cited-by) from 6 anchor reviews: Guihaire & Hao (2008); Kepaptsoglou & Karlaftis (2009); Farahani et al. (2013); Ibarra-Rojas et al. (2015); Durán-Micco & Vansteenwegen (2022); Ceder (2007/2016 book). ⟨verify each exists/details during search⟩
- **Grey literature (limited, for §2.7 only):** Indian government/multilateral reports (MoHUA SLBs, World Bank, ITDP/WRI India bus route rationalisation reports) — cited but **not coded** in Table 1.

## 4. Search strings (three concept blocks)
- **Block A — planning object:** ("transit network design" OR "bus network design" OR "route network design" OR "bus route rationali?ation" OR "route rationali?ation" OR "network redesign" OR "frequency setting" OR "fleet size" OR "route planning") AND (bus OR "public transport" OR transit)
- **Block B — data condition / approach:** ("origin-destination" OR "demand estimation" OR "smart card" OR "automated fare collection" OR "passenger count" OR "data scarcity" OR "data-scarce" OR "limited data" OR "open data" OR OpenStreetMap OR "gridded population" OR WorldPop OR accessibility OR "coverage" OR equity)
- **Block C — context (for §2.7 sub-search):** (India OR Indian OR "Global South" OR "developing countr*" OR "informal transport" OR paratransit OR minibus OR "permit")

Queries run: A∧B (core), A∧C (context), plus targeted queries per subsection (2.2–2.7) logged in `search_log.csv`.

## 5. Window & eligibility
- **Window:** 2000–2026 for the database search ⟨confirm⟩; pre-2000 seminal works (e.g. Mandl 1980; Ceder & Wilson 1986; Baaj & Mahmassani 1991) admitted via snowballing only and flagged "seminal".
- **Include:** peer-reviewed journal articles or full conference papers; English; bus or general road-based public transport; proposes or applies a method for route design/rationalisation, frequency/headway setting, fleet sizing, or accessibility/coverage-based network evaluation; the data inputs are identifiable.
- **Exclude:** rail/metro-only; crew/vehicle scheduling or timetabling only; pure demand-responsive/AV simulation without fixed-route design; purely behavioural or mode-choice studies; editorials; no identifiable method or data.

## 6. Screening
1. De-duplicate by DOI / normalised title.
2. Title–abstract screen against §5 (Sonnet agent, first pass; every exclusion reason logged).
3. Full-text/abstract check of the shortlist by Claude (Opus) + author spot-check ⟨confirm⟩.
4. Stratified selection to 45–60 so that each subsection 2.2–2.7 has coverage (not just the most-cited).
PRISMA-style counts (identified → de-duplicated → screened → eligible → coded) recorded in `prisma_counts.md`.

## 7. Coding scheme (Table 1 columns)
| Field | Values |
|---|---|
| Geography | country; region class (Global North / Global South / India / benchmark-network e.g. Mandl) |
| Planning stage | route design · frequency/headway · fleet sizing · network evaluation/accessibility · integrated (≥2) |
| Method family | mathematical optimisation (exact) · (meta)heuristic · rule/guideline-based · GIS/accessibility analysis · simulation · data-mining (AFC/GPS) |
| Demand input | none · proxy (pop/POI/land use) · modelled OD (4-step) · survey OD · smart-card/AFC · APC/boarding counts · synthetic/benchmark OD |
| **Data intensity 1–5** | see §8 |
| Equity treatment | none · coverage only · distributional metric (Gini/Lorenz/Palma etc.) · explicit equity objective/constraint |
| Validation performed | none · benchmark instance comparison · back-cast vs observed counts · field/expert · sensitivity/uncertainty |
| Produces implementable plan | **Yes** (specific routes + frequency/fleet for a real city) · **Partial** (routes or diagnosis for a real city, not full service plan) · **No** (method on benchmark/synthetic network, or assessment only) |
| Code/data released | yes / no |

## 8. Data-intensity scale (aligned with the paper's data-maturity ladder, §7.5)
| Level | Definition | Typical inputs |
|---|---|---|
| **1** | Open data only | OSM network, gridded population (WorldPop/GHSL), open POIs, routing-engine times |
| **2** | + official static data | census tracts, land use / master plan, published GTFS schedule, road inventory |
| **3** | + partial observations | sample counts, on-board or intercept surveys, operator GPS/AVL |
| **4** | + full demand matrix | household-survey OD, calibrated 4-step / activity model OD |
| **5** | + passive ridership at stop/trip level | AFC/smart-card, APC, ticket-machine transactions (often with OD inference) |
A study is coded at the **highest** level of data it *requires* to produce its main output. Synthetic/benchmark OD (e.g. Mandl) is coded 4 (the method requires an OD matrix) with "No" on implementable plan.

## 9. Analysis for §2.8
- Cross-tab: data intensity (1–5) × implementable plan (Yes/Partial/No) → Figure 2 inset heatmap.
- Secondary tabs: planning stage × demand input (shows where demand enters — mirrors §1.3); geography × equity treatment.
- Expected (hypothesis, to be tested, not assumed): Yes-plans cluster at 4–5; level 1–2 studies cluster at Partial/No.
- Closing wedge (conceptual): coverage and fleet sizing (fleet = cycle time / headway) do not need demand once headway is set by an ordinal, policy-anchored rule.

## 10. Reproducibility
Scripts, raw query results, screening decisions and the coded matrix are kept in `paper/lit_review/` and can go in Supplementary Material.
