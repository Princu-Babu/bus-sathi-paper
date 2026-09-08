# Data Availability Statement

**Paper Title:** *Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*  
**Target Journal:** *Transport Policy*  
**Study Area:** Kashmir Division (10 districts), Jammu & Kashmir, India  
**Operational Baseline:** Kashmir Valley v3.4.5 (`outputs_v3.4.5`)

All analytical code, data manipulation scripts, figure-generation scripts, and tabular outputs in this paper companion repository are open source and fully reproducible. Input datasets used in this study derive from publicly accessible open-data portals, official government records, and academic research data-sharing arrangements.

This document details the provenance, licensing, redistribution status, and accession procedures for all primary data sources.

---

## 1. Summary of Primary Data Sources

| Dataset Name | Primary File(s) | Source & Custodian | License / Terms | Redistributable in Repo? | Role in Analysis |
|---|---|---|---|---|---|
| **OpenStreetMap (OSM)** | `kashmir_districts_osm.geojson`, `kashmir_tehsils_osm.geojson`, `pois.csv`, `walk_graph.gpickle` (cache) | OpenStreetMap contributors / Geofabrik regional extract | Open Database License (ODbL 1.0) | Yes (processed extracts) | District/tehsil boundaries, pedestrian walk graph (23,323 km), POI opportunity layer (2,431 points), road density checks (F5, F6) |
| **WorldPop Population Surface** | `kashmir_worldpop.tif` | WorldPop Project, University of Southampton (2026 UN-adjusted 100 m constrained raster) | Creative Commons Attribution 4.0 (CC-BY 4.0) | Accession URL provided (not committed to git due to size) | High-resolution residential population surface across route catchments; 10-district denominator = 6,584,762 (F2, F8) |
| **Permit Register** | `existing-routes.csv` | Regional Transport Authority / Transport Department, Government of Jammu & Kashmir | Public Sector Information / Regulatory Register | Yes (sanitised geocoded extract) | Baseline operational universe: 614 vehicle permits, 157 distinct OD corridors, vehicle class and service definitions (F1) |
| **SSCL / CHALO E-Bus Telemetry** | `chalo_ridership.csv`, `chalo_deployed_buses.csv`, `Hourly_Passenger_Count.csv` | Srinagar Smart City Limited (SSCL) & Chalo Mobility Pvt. Ltd. | Academic research data-sharing agreement | Aggregated research tables included | Operational benchmark for electric bus network (30 routes); hourly boardings; V2 consistency check (with circularity disclosure) |
| **Bus Sathi Driver GPS Telemetry** | `gps/reality_check.csv`, `gps/corridor_profiles.csv`, `gps/route_evidence.csv`, `gps/permit_observed.csv`, etc. | Bus Sathi driver dispatch app telemetry (`E:\bus-sathi-trace`) | Non-commercial research data agreement | Yes (derived corridor summaries) | Supply-side empirical validation: moving speeds, dwell times, cycle times, and fleet sizing (F3, F10, F11, F12) |
| **Census of India (2011)** | `data/raw/census2011_kashmir_districts.csv` | Office of the Registrar General & Census Commissioner, India | Open Government Data (data.gov.in) | Yes (summary extract) | Benchmark comparison against WorldPop 2026 (6,888,475 residents across 10 districts; F2) |

---

## 2. Detailed Source Provenance & Accession

### 2.1 OpenStreetMap (OSM)
- **Custodian:** OpenStreetMap contributors (https://www.openstreetmap.org/).
- **Extraction Snapshot:** May–June 2026 via Geofabrik India sub-region extract and Overpass API queries.
- **Components:**
  1. *Administrative Boundaries:* `kashmir_districts_osm.geojson` (10 districts at OSM `admin_level=5`) and `kashmir_tehsils_osm.geojson` (39 tehsils at `admin_level=6`).
  2. *Points of Interest (POIs):* `pois.csv` (2,431 geocoded amenities, education, healthcare, transit, and commercial destinations tiered by attraction class).
  3. *Pedestrian Network Graph:* Extracted using `pyosmium` and NetworkX via `analysis/a01_build_walk_graph.py`, generating a routable walking network of 961,927 nodes and 973,569 edges (23,323 km of pedestrian-accessible links).
- **Licensing:** Open Data Commons Open Database License (ODbL 1.0). You are free to copy, distribute, transmit and adapt the data, so long as you credit OpenStreetMap and its contributors.

### 2.2 WorldPop Global High-Resolution Population Denominators
- **Custodian:** WorldPop Research Project, School of Geography and Environmental Science, University of Southampton (https://www.worldpop.org/).
- **Dataset:** India 100 m resolution, constrained individual countries 2026 UN-adjusted population count raster (`ind_ppp_2026_UNadj_constrained.tif`).
- **Processing:** Clipped to the bounding box of Kashmir Division (bounding box: $73.8^\circ \text{E}$ to $75.6^\circ \text{E}$, $33.3^\circ \text{N}$ to $34.9^\circ \text{N}$, EPSG:4326).
- **Zonal Population Statistics:** Zonal sum across the dissolved 10-district polygon equals **6,584,763**, establishing the canonical study-area denominator of **6,584,762** used in the baseline engine.
- **Licensing:** Creative Commons Attribution 4.0 International (CC-BY 4.0).
- **Accession & Git Storage:** Due to binary size (4.8 MB) and git repository hygiene standards, raw TIFF rasters are excluded from git tracking (`.gitignore`) and staged in `data/raw/kashmir_worldpop.tif`. Download instructions and automated retrieval hashes are provided in `data/MANIFEST.md`.

### 2.3 J&K Bus Permit Register (`existing-routes.csv`)
- **Custodian:** Transport Department, Government of Jammu & Kashmir, Regional Transport Authority (RTA) Srinagar / Kashmir.
- **Provenance:** Regulatory permit records cataloging privately operated stage carriage bus permits across Kashmir Division. Geocoded to canonical stop pairs and intermediate via-points in engine pipeline `v3.4.1`–`v3.4.5`.
- **Nature of Data:** Represents 614 active vehicle service permits. As documented in Finding F1, these represent 157 distinct physical origin–destination corridors (mean 3.9 permits per corridor).
- **Licensing:** Public regulatory information released under the Right to Information Act and Open Government Data initiatives.

### 2.4 Srinagar Smart City Limited (SSCL) & CHALO Operations
- **Custodian:** Srinagar Smart City Limited (SSCL), Government of Jammu & Kashmir, and Chalo Mobility Pvt. Ltd. (automated fare collection and telemetry vendor).
- **Datasets:**
  1. `chalo_ridership.csv`: Monthly aggregate electric bus ridership and operated bus-kilometers by route across FY 2025–26.
  2. `chalo_deployed_buses.csv`: Route-level fleet deployment by vehicle length (9 m and 12 m air-conditioned electric buses).
  3. `Hourly_Passenger_Count.csv`: Observed hourly passenger boardings across the e-bus network during April 2026 (parsed with `skiprows=1`).
- **Circularity Disclosure:** CHALO ridership data was used during engine design to calibrate operational plausibility parameters. In this paper companion, CHALO metrics are utilized strictly as an empirical consistency benchmark (Channel V2), with explicit circularity disclosure in Section 6.
- **Terms:** Used under academic research collaboration.

### 2.5 Bus Sathi Driver GPS Telemetry (`gps/`)
- **Custodian:** Bus Sathi mobile dispatch platform (`E:\bus-sathi-trace`).
- **Dataset:** Passive smartphone GPS telemetry collected from operating bus drivers along 18 key transit corridors in Kashmir Valley during June–July 2026.
- **Datasets Staged in `data/raw/gps/`:**
  - `reality_check.csv`: Planned vs. measured one-way operating runtimes across matched corridors.
  - `corridor_profiles.csv`: Empirical moving speeds, effective speeds, and dwell time proportions.
  - `route_evidence.csv`: Spatial coverage of planned routes by observed vehicle trajectories (`obs_frac`).
  - `permit_observed.csv`: Recurrent service corroboration status per permit route.
  - `geometry_divergence.csv`: Corridors exhibiting route alignment divergence.
  - `driver_days.csv`: Driver active service window and shift duration telemetry.
- **Scope & Methodological Limits:** GPS telemetry validates only the physical and operational supply chain (route geometry, congestion multipliers, dwell times, and cycle times). **GPS data contains no passenger boarding counts or latent demand signal and cannot validate ridership.** Five corridors were used by engine v3.4.5 for cycle correction and are explicitly marked *in-sample*; 9 partial corridors are evaluated *out-of-sample*.

### 2.6 Census of India (2011)
- **Custodian:** Office of the Registrar General & Census Commissioner, Ministry of Home Affairs, Government of India.
- **Dataset:** 2011 Primary Census Abstract (PCA) for Jammu & Kashmir districts.
- **Purpose:** Independent validation of administrative population totals (6,888,475 across the 10 districts; F2).
- **Licensing:** Open Government Data (OGD) Platform India (data.gov.in).

---

## 3. Cryptographic Integrity & MANIFEST

Every raw staged input file, its exact byte size, and its cryptographic SHA-256 hash are cataloged in:
- `data/MANIFEST.json` (machine-readable)
- `data/MANIFEST.md` (human-readable)

Researchers can verify the integrity of their staged raw data at any time by running:
```bash
python -c "import hashlib, json; manifest=json.load(open('data/MANIFEST.json')); [print(f['file'], 'OK' if hashlib.sha256(open('data/raw/'+f['file'],'rb').read()).hexdigest()==f['sha256'] else 'FAIL') for f in manifest['files']]"
```
