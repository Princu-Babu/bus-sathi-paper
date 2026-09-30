# Data availability

> **[DECISION NEEDED — D4, D16]** Three facts are not established in the repository and are shown in
> brackets: the basis for using the CHALO aggregates, the consent basis for the driver GPS, and the GPS
> collection window. Note a conflict to resolve first: `DATA_AVAILABILITY.md` (repo root) says the GPS was
> collected in **June–July 2026**, while the ledger (CL-18) and the a13 driver-day file say
> **February–June 2026**.

The code, derived tables and figures that reproduce every number in this paper are openly available at
https://github.com/Princu-Babu/bus-sathi-paper (GPL-3.0), with a claim ledger mapping each reported value
to the module that computes it. The rationalisation engine is available at
https://github.com/Princu-Babu/kashmir-transit-rationalisation.

Open inputs: WorldPop 2026 constrained population for India (CC BY 4.0; retrieval described in
`data/MANIFEST.md`); OpenStreetMap roads, points of interest, buildings and administrative boundaries
(ODbL 1.0); the digitised stage-carriage permit register (614 records, included); Census of India 2011
district totals (included); ASRTU *SRTU Fleet Handbook 2024* (public).

Restricted inputs: monthly and hourly e-bus ridership and deployment for the 30 SSCL routes were provided
by [Srinagar Smart City Limited / Chalo — basis: ___]; only the aggregates used in the analysis are
included. Driver GPS traces from the Bus Sathi application ([dates]) were collected [consent basis: ___];
raw traces are not shared, and the repository contains only corridor- and route-level summaries with
hashed device identifiers.
