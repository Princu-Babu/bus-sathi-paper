# Data availability

> **[DECISIONS — D27, D29, D4]** (1) For **double-anonymised review** the links below must be replaced by an
> anonymised mirror (e.g. anonymous.4open.science) and restored on acceptance. (2) Add the Zenodo DOI of the
> `Bus-sathi` v1.0.0 release once minted. (3) Fill the GPS consent basis from D4. The GPS window is settled:
> February–June 2026 (D23).

The code, data and results that reproduce every number in this article are openly available at
https://github.com/Princu-Babu/Bus-sathi (release v1.0.0; DOI: [to be minted via Zenodo]), under GPL-3.0 for
code and CC BY 4.0 for project data, with a claim ledger mapping each reported value to the module that
computes it. The repository includes the published route plan, the rationalisation engine, the driver-GPS
aggregation pipeline, and a test suite that reproduces the published plan exactly.

Open inputs: WorldPop 2026 constrained population for India (CC BY 4.0); OpenStreetMap roads, points of
interest, buildings and administrative boundaries (ODbL 1.0); Microsoft Global ML Building Footprints (ODbL
1.0); the digitised stage-carriage permit register (614 records); Census of India 2011 district and city
totals; ASRTU *SRTU Fleet Handbook 2024*.

Third-party aggregates: monthly and hourly e-bus ridership and per-route deployment for the 30 SSCL routes,
provided by [Srinagar Smart City Limited / Chalo — basis: ___], are included as aggregates only.

Personal data: driver GPS from the Bus Sathi application (February–June 2026; ~157 drivers) was collected
[consent basis: ___]. Raw traces are not shared. Only corridor- and route-level aggregates, and a
de-identified duty table (no identifiers or dates), are released.
