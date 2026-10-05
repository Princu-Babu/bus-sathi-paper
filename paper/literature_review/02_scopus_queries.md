# Scopus search plan (mirrors OpenAlex run of 2026-09-30 + dedicated novelty queries)

Common limits appended to every query:
`AND PUBYEAR > 1999 AND PUBYEAR < 2027 AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(re))`

## Part 1 — Core blocks (same concepts as OpenAlex, Scopus syntax)
| Tag | TITLE-ABS-KEY( … ) |
|---|---|
| S_A_design | ("transit network design" OR "bus network design" OR "route network design") AND (bus OR "public transport" OR transit) |
| S_A_rational | ("route rationali?ation" OR "network redesign" OR "route restructuring" OR "network restructuring") AND (bus OR "public transport" OR transit) |
| S_A_freqfleet | ("frequency setting" OR headway OR "fleet siz*") AND ("bus route*" OR "transit route*" OR "bus network") |
| S_AB_demand | ("transit network design" OR "bus route design" OR "frequency setting") AND ("origin-destination" OR "smart card" OR "automated fare collection" OR "passenger count*") |
| S_B_od | ("origin-destination" OR "OD matri*") AND ("smart card" OR "fare collection" OR "passenger count*" OR GPS) AND (bus OR "public transport" OR transit) |
| S_B_scarce | ("data scarcity" OR "data-scarce" OR "limited data" OR "data-poor" OR "lack of data") AND (bus OR "public transport" OR transit) AND (planning OR network OR route*) |
| S_B_open | (OpenStreetMap OR "open data" OR "gridded population" OR WorldPop OR GTFS) AND (bus OR "public transport" OR transit) AND (network OR route* OR accessibility OR coverage) |
| S_B_access | (accessibility OR coverage) AND ("bus network design" OR "transit network design" OR "bus route*" OR "route planning") |
| S_B_proxy | ("demand proxy" OR "demand index" OR "land use" OR "points of interest" OR "population density") AND ("bus route*" OR "transit route*" OR "bus network") AND (design OR planning OR rationali*) |
| S_B_equity | (equity OR Gini OR Lorenz OR "social exclusion" OR "transit desert*") AND ("bus network" OR "transit network" OR "public transport network") AND (design OR planning OR accessibility) |
| S_C_india | (India OR Indian) AND ("bus route*" OR "bus network" OR "bus service*" OR "public transport") AND (rationali* OR design OR planning OR optimi*) |
| S_C_south | ("Global South" OR "developing countr*" OR "developing cit*" OR paratransit OR "informal transport" OR minibus OR matatu OR trotro OR jeepney) AND (bus OR "public transport" OR transit) AND (route* OR network) AND (planning OR design OR rationali* OR mapping OR reform) |
| S_C_permit | ("route permit*" OR "stage carriage" OR "bus regulation" OR "bus reform" OR "bus franchising" OR "gross cost contract*") AND (bus OR "public transport" OR transit) |

## Part 2 — NOVELTY queries (goal: find ANY paper already doing our logic)
Our logic = demand-free, open-data (gridded pop + OSM/POI + routing engine) pipeline that consolidates an existing permit/route set via overlap, assigns tiers/headways by an ordinal index, and sizes fleet from cycle time.
| Tag | TITLE-ABS-KEY( … ) |
|---|---|
| N1_rationalisation_all | ("route rationali*" OR "network rationali*" OR "route consolidation" OR "route restructur*" OR "network restructur*" OR "route overlap*" OR "route duplication") AND (bus OR "public transport" OR transit OR minibus) |
| N2_demand_free | (bus OR transit OR "public transport") AND (route* OR network) AND ("without demand data" OR "no demand data" OR "absence of demand" OR "lack of demand data" OR "data-scarce" OR "data scarce" OR "data-poor" OR "demand-free" OR "demand independent" OR "supply-side" OR "supply side") |
| N3_open_fleet | (bus OR transit) AND ("fleet siz*" OR "fleet requirement*" OR "number of buses") AND (OpenStreetMap OR OSM OR "open data" OR WorldPop OR "gridded population" OR "points of interest" OR GTFS OR OSRM) |
| N4_permit_reform | (bus OR "stage carriage" OR minibus OR paratransit) AND (permit* OR licen* OR franchis*) AND (route* OR network) AND (rationali* OR reform OR restructur* OR redesign OR consolidat*) |
| N5_proxy_headway | ("composite index" OR "demand proxy" OR "demand index" OR "potential demand" OR "demand potential") AND (bus OR transit) AND (route* OR headway* OR frequenc* OR "service level*") |
| N6_kashmir_india_bus | (Kashmir OR Srinagar OR "Jammu") AND (bus OR "public transport" OR transit) |

## Procedure
1. An author logs in to Scopus through institutional access; no credentials are handled by any tool.
2. Claude enters each query in Advanced Search, records hit count + date in `scopus_log.csv`.
3. Export per query: CSV with "Citation information" + "Abstract & keywords" (Scopus limit 20,000 per CSV export; all our queries are far below).
4. Merge with OpenAlex by DOI → new records only go through the same screening.
5. Novelty queries (Part 2) are screened by Claude (Opus) in full, not just by title — every hit that resembles our pipeline gets a full-text check and a written "how it differs" note.
