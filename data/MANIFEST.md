# Data Manifest: Kashmir Transit Rationalisation Companion Repository

**Repository Root**: `E:\kash-paper`  
**Operational Engine Baseline**: Kashmir Valley Transit Rationalisation Engine `v3.4.5-geo`  
**Study Area**: Kashmir Division, Jammu & Kashmir, India (10 Districts: Anantnag, Bandipore, Baramulla, Budgam, Ganderbal, Kulgam, Kupwara, Pulwama, Shopian, Srinagar)  
**Study Area Denominator**: 6,584,762 (WorldPop 2026 UN-adjusted constrained individual countries 100m raster)  
**Coordinate Reference Systems**: WGS84 (`EPSG:4326`) for spatial storage; UTM Zone 43N (`EPSG:32643`) for planar metric buffering and network walk graphs  
**Manifest Version**: 1.0.0 (Generated: 2026-08-23T15:17:23+00:00, Updated: 2026-09-03)

---

## 1. Overview & Data Architecture

This manifest establishes the authoritative data registry and cryptographic provenance for all staged raw inputs and precomputed intermediate caches in the paper companion repository `E:\kash-paper` (*Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*, targeting *Transport Policy*).

### Directory Boundaries
- `data/raw/`: Read-only frozen primary source datasets (20 files: 13 engine inputs/outputs, 6 driver-GPS trace outputs, 1 official census benchmark). No file in this directory may be modified or deleted during pipeline execution.
- `data/cache/`: Heavy precomputed spatial graphs, network walk catchments, and routing-engine caches. **Strictly excluded from version control** (`.gitignore`). Fully regenerable from `data/raw/`.
- `data/derived/`: Canonical, deterministic analysis outputs (CSV and JSON format only; no parquet).

---

## 2. Master Inventory of Raw Datasets (`data/raw/`)

The repository freezes exactly 20 raw input files (19 staged via `data/MANIFEST.json` plus `census2011_kashmir_districts.csv`).

| # | Filename (relative to `data/raw/`) | Size (Bytes) | SHA-256 Checksum | Upstream Source / Provenance | License / Access Terms | Redistributable |
|---|---|---|---|---|---|---|
| 1 | `Rationalised_Routes_Kashmir_v3.csv` | 247,953 | `1871714c8804cbbc152b0209774c772943c939e71bde4241632690ce0f02172a` | `E:\kash\outputs_v3.4.5\Rationalised_Routes_Kashmir_v3.csv` | Academic / Govt Research Use | Yes |
| 2 | `Rationalised_Routes_Kashmir_v3.geojson` | 2,977,639 | `4ea6a856dd77d5d43a587fbdc445c76feea0b123b2bcc85040e8505a1497f945` | `E:\kash\outputs_v3.4.5\Rationalised_Routes_Kashmir_v3.geojson` | Academic / Govt Research Use | Yes |
| 3 | `Rationalisation_Log_Kashmir_v3.csv` | 242,957 | `00f1052206dc29b004df5bf18c2a1a80f6d67fcab2e66a2b311686b082b4be4c` | `E:\kash\outputs_v3.4.5\Rationalisation_Log_Kashmir_v3.csv` | Academic / Govt Research Use | Yes |
| 4 | `existing-routes.csv` | 66,972 | `fa9778c8267d71b68ccffc1024ae77cd0cef3d0d86eb1ae0c0b3d1984da39047` | `E:\kash\existing-routes.csv` (RTO Kashmir permit records) | Official Transit Records (RTO J&K) | Yes (Aggregated/Geocoded) |
| 5 | `pois.csv` | 223,453 | `e8f217c4ad77986e3e00a91dbb02fcfbca918eb499d695050982d357fed19f73` | `E:\kash\pois.csv` (OpenStreetMap extract) | ODbL (Open Database License) | Yes |
| 6 | `kashmir_worldpop.tif` | 4,760,992 | `515e5867ee4c0fe9dd031a3fc0f372814aa96bf3c689d9e25bf09ba19bda6571` | `E:\kash\kashmir_worldpop.tif` (WorldPop 2026 UN-adjusted) | CC BY 4.0 International | Yes |
| 7 | `kashmir_districts_osm.geojson` | 444,515 | `4091fe7bdc0e3490eab3f3505fe1f98a9beb288c1bf97b38170f84667ecdc444` | `E:\kash\kashmir_districts_osm.geojson` (OSM admin_level 5) | ODbL | Yes |
| 8 | `kashmir_tehsils_osm.geojson` | 605,242 | `38e0a2e3d88a0c8de86c7e65451b6839b0d0903a9156c4710d7a2017fe04e549` | `E:\kash\kashmir_tehsils_osm.geojson` (OSM admin_level 6) | ODbL | Yes |
| 9 | `Kashmir_Stops_Master_v4.csv` | 9,847 | `dcfce2a9b8a1cf6610fdd76809cd5eb07d24fd2d352edc120bd58d911e5d2d14` | `E:\kash\Kashmir_Stops_Master_v4.csv` | Academic / Govt Research Use | Yes |
| 10 | `Hourly_Passenger_Count.csv` | 12,952 | `289381eddd272fdab98bfabb4db165dd2b7b77b01e5310ac7c668d6b2cc5a0b1` | `E:\kash\Hourly Passenger Count.csv` (SSCL/Chalo AFCS) | Proprietary Operator Data (SSCL/Chalo) | Research Use Only |
| 11 | `chalo_ridership.csv` | 15,626 | `c216de2d5f13b120572c0fcaa8fd524db2d2b9e687761c44fa6ee2f3f68164ff` | `E:\kash\Ridership Data.csv` (SSCL/Chalo monthly ETM) | Proprietary Operator Data (SSCL/Chalo) | Research Use Only |
| 12 | `chalo_deployed_buses.csv` | 1,683 | `ee6b45ff3e2c32c36ab1fcd9b658870f6b7a1d44bb6836e635f0dee4930cf38d` | `E:\kash\Route Wise deployed Buses.csv` (SSCL/Chalo) | Proprietary Operator Data (SSCL/Chalo) | Research Use Only |
| 13 | `ROUTE_DEEPDIVE_LEDGER.csv` | 167,738 | `1788e1ce417d46ad124a9d85e30952faa7de810aa47c34615dcbae94ff159f34` | `E:\kash\ROUTE_DEEPDIVE_LEDGER.csv` | Research Verification Audit | Yes |
| 14 | `gps/reality_check.csv` | 2,943 | `55172547baaae97dd2f6e331a36ed52b3a44f065311ec22aac0fcd67b955ba43` | `E:\bus-sathi-trace\data\reality_check.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 15 | `gps/corridor_profiles.csv` | 1,288 | `0cb17ce98d6b166d049d6aa19d520d9fe7850f644bea87af7545a43c7b9d1c44` | `E:\bus-sathi-trace\data\corridor_profiles.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 16 | `gps/route_evidence.csv` | 12,563 | `061ea4e5b550dbaeb50a7f123f52cf3024a268c1d8fc0c8ad899dee9b7998f75` | `E:\bus-sathi-trace\data\route_evidence.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 17 | `gps/permit_observed.csv` | 12,402 | `f97f1bacf5bf03fce1f7d9e816fb161ad681c0e08d6e99ac2ee8805eca8839b8` | `E:\bus-sathi-trace\data\permit_observed.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 18 | `gps/geometry_divergence.csv` | 553 | `7bf5c49479a6e639d3356a3c136e0e38519e05d6a6c10b182f886b13fdcfc485` | `E:\bus-sathi-trace\data\geometry_divergence.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 19 | `gps/driver_days.csv` | 51,564 | `14b408639648b8ffc128322d6a05f44b1faf46a0b65ebf8d7e986df667e4b9a9` | `E:\bus-sathi-trace\data\driver_days.csv` | Research Trace Output (Bus Sathi) | Research Use Only |
| 20 | `census2011_kashmir_districts.csv` | 951 | `d7c94f326e7cd9abd42e82b2c1d51814d76d708162b57aceda9ddf82b65bd559` | Office of the Registrar General & Census Commissioner, India (PCA J&K) | Open Government Data (OGD) India | Yes |
| 21 | `peer_cities.csv` | 28,483 | `7a8494f74d6d7dbea78d5ccde32dfb379987200a932b635657769af90a761b61` | ASRTU *SRTU Fleet Handbook 2024* ('City' column) + Census 2011 Table A-04(I); consumed by `a16` | Public | Yes |

**External inputs read in place (not copied into `data/raw/`):**

| File | Size (Bytes) | SHA-256 | Used by | Note |
|---|---|---|---|---|
| `E:/kash/india-latest.osm.pbf` | 217,375,703 | `681021c55963ed736fd95dcb89c55ca34f0dbcb5431085eeb621dbc3bf9a908a` | `a01` (walk graph), `v01` (buildings) | OSM India extract (ODbL). It contains 847,866 building ways nationally — far fewer than the full national OSM building layer — so it appears to be a partially filtered extract; V1's completeness table must be read with that in mind. |
| `data/cache/osm_buildings_kashmir.csv` (derived, gitignored) | 705,483 | `e906e2f0f8ede2f20393cd957a389cfe707011cef4c7c7ba286c2666ac1194a4` | `v01` | 13,603 closed building ways in the study bounding box (12,343 inside the 10-district union), extracted by `v01_spatial_crossval.py`. |

---

## 3. Detailed Dataset Specifications

### Domain A: Route Rationalisation Plan & Optimization Records (Engine v3.4.5-geo)
1. **`Rationalised_Routes_Kashmir_v3.csv`**
   - *Format*: CSV, UTF-8, 644 rows × 55 columns.
   - *Description*: The primary output table of the route-rationalisation engine. Contains 614 permit-derived rows plus 30 synthetic SSCL e-bus trunk routes (`SSCL-01` to `SSCL-30`). 186 rows represent active routes (`Action_Taken` in `{"UPGRADED_TO_TRUNK", "RETAINED_AS_FEEDER"}`) and 458 rows represent merged routes (`Action_Taken == "MERGED_INTO_TRUNK"`).
   - *Key Columns*: `Route_ID`, `New_Route_ID`, `Route_Name`, `Route_Type` (Urban, Peri_Urban, Regional_District), `Action_Taken`, `Route_KM`, `Headway_Min`, `Cycle_Time_Min`, `Fleet_Required`, `Population_Served_Raw`, `CDI`, `OSRM_Duration_S`.
   - *License*: Government of Jammu & Kashmir / Academic Research Use.

2. **`Rationalised_Routes_Kashmir_v3.geojson`**
   - *Format*: GeoJSON (FeatureCollection), EPSG:4326.
   - *Description*: LineString geometries for all 186 active routes routed via OSRM over OpenStreetMap road network. 15 geometries redrawn in v3.4.5-geo based on driver-GPS and gazetteer terminal anchoring.
   - *Key Properties*: `New_Route_ID`, `Route_Name`, `Route_Type`, `Route_KM`.

3. **`Rationalisation_Log_Kashmir_v3.csv`**
   - *Format*: CSV, 644 rows × 22 columns.
   - *Description*: Per-permit disposition audit trail recording candidate evaluation, pairwise spatial overlap scores against trunk corridors, merge decisions, and rationale.

4. **`existing-routes.csv`**
   - *Format*: CSV, 614 rows × 15 columns.
   - *Description*: Digitized Regional Transport Authority (RTO) Kashmir route permit register. Each row represents an individual permit granted to an operator. Coordinates derived from district-aware gazetteer geocoding.
   - *Key Columns*: `Permit_No`, `Origin`, `Destination`, `Via_Points_Raw`, `Origin_Lat`, `Origin_Lon`, `Dest_Lat`, `Dest_Lon`, `Vehicle_Category`, `Service_Type`.

5. **`Kashmir_Stops_Master_v4.csv`**
   - *Format*: CSV, 126 canonical transit stops.
   - *Description*: Curated transit stop master directory where stop coordinates were established from engine terminal clusters and audited against OSM administrative polygons (point-in-polygon).
   - *Key Columns*: `Stop_ID`, `Stop_Name`, `District`, `Tehsil`, `Latitude`, `Longitude`, `Stop_Type`.

### Domain B: Spatial Infrastructure & Administrative Boundaries (OpenStreetMap & WorldPop)
6. **`pois.csv`**
   - *Format*: CSV, 2,431 rows × 12 columns.
   - *Description*: Points of Interest extracted from OpenStreetMap for Kashmir Division, classified into 3 attraction tiers: Tier 1 (High: education, hospitals, public admin; 1,030 POIs), Tier 2 (Medium: commercial, markets, services; 1,080 POIs), and Tier 3 (Seasonal/Tourism: shrines, tourist hotels, parks; 321 POIs).
   - *License*: Open Database License (ODbL), OpenStreetMap contributors.

7. **`kashmir_worldpop.tif`**
   - *Format*: Cloud-Optimized GeoTIFF (Float32), 100m spatial resolution (~0.0086 km²/pixel), EPSG:4326.
   - *Description*: WorldPop 2026 UN-adjusted population distribution grid for Jammu & Kashmir, clipped to bounding box `[73.70, 33.30, 75.65, 34.85]`. Study area total sum is 6,584,763 (active engine denominator: 6,584,762).
   - *License*: Creative Commons Attribution 4.0 International (CC BY 4.0).

8. **`kashmir_districts_osm.geojson`**
   - *Format*: GeoJSON (FeatureCollection), 10 polygon features.
   - *Description*: Authoritative OpenStreetMap `admin_level=5` district boundaries for the 10 districts of Kashmir Division.

9. **`kashmir_tehsils_osm.geojson`**
   - *Format*: GeoJSON (FeatureCollection), 39 polygon features.
   - *Description*: Authoritative OpenStreetMap `admin_level=6` sub-district (tehsil) boundaries across Kashmir Division.

### Domain C: Observed Electronic Ticketing & Operational Fleet Data (SSCL / Chalo Mobility)
10. **`Hourly_Passenger_Count.csv`**
    - *Format*: CSV, 721 rows (header + 30 days × 24 hours).
    - *Description*: Hourly boarding totals from automated fare collection systems (AFCS) on Srinagar Smart City Limited (SSCL) e-buses between 1 April 2026 and 30 April 2026.
    - *Note*: **Pipeline requires `skiprows=1`** during loading to bypass metadata preamble.
    - *License*: Proprietary operator data provided under research agreement; non-redistributable outside academic/audit scope.

11. **`chalo_ridership.csv`**
    - *Format*: CSV, monthly records FY 2025–26.
    - *Description*: Monthly aggregated ridership, scheduled km, operated km, and revenue for SSCL e-bus operations. 12-month total ridership = 11,632,326; operated/scheduled ratio = 84.5%; female passenger share = 64.5%.

12. **`chalo_deployed_buses.csv`**
    - *Format*: CSV, 30 rows.
    - *Description*: Empirical bus deployment per SSCL trunk route partitioned by vehicle length (9-metre MPV vs 12-metre HPV). Used to overwrite synthetic fleet formulas on SSCL routes with real deployed fleet (total 283 buses).

### Domain D: Route Verification & Physical Ground-Truth Audit
13. **`ROUTE_DEEPDIVE_LEDGER.csv`**
    - *Format*: CSV, 186 rows × 28 columns.
    - *Description*: Web-audited ground-truth road distances, terrain notes, verified intermediate waypoints, and gazetteer references for every active route. Documents 49 distance corrections and 44 deferred distances applied in v3.4.4.

### Domain E: Driver-GPS Trace Intelligence (`data/raw/gps/`, Bus Sathi)
14. **`gps/reality_check.csv`**
    - *Format*: CSV, 14 corridor match rows × 12 columns.
    - *Description*: Direct comparison between modelled transit engine run times and empirical GPS run times. Differentiates `matched` (5 in-sample corridors) from `partial` (9 out-of-sample corridors).

15. **`gps/corridor_profiles.csv`**
    - *Format*: CSV, 18 corridor rows.
    - *Description*: Per-corridor empirical speed and dwell profiles extracted from 43,809 clean GPS runs. Provides moving speed (median 20.55 km/h), effective speed (median 13.00 km/h), and dwell share (median 38.0%).

16. **`gps/route_evidence.csv`**
    - *Format*: CSV, 186 active route rows.
    - *Description*: Road network physical coverage fraction (`obs_frac`) showing the percentage of each route's drawn alignment intersected by observed bus GPS trajectories (median 94.0%).

17. **`gps/permit_observed.csv`**
    - *Format*: CSV, 614 permit rows.
    - *Description*: Observation status and corridor linkage for each permit in `existing-routes.csv`.

18. **`gps/geometry_divergence.csv`**
    - *Format*: CSV, divergence audit records.
    - *Description*: Flags locations where observed driver paths diverge from OSRM shortest-path calculations.

19. **`gps/driver_days.csv`**
    - *Format*: CSV, 1,213 driver session records.
    - *Description*: Daily operational time stamps establishing the observed operating service window (08:00 to 19:00).

### Domain F: Official Demographic Benchmark
20. **`census2011_kashmir_districts.csv`**
    - *Format*: CSV, 10 district rows × 4 columns.
    - *Description*: Official Primary Census Abstract (PCA) 2011 population totals for all 10 districts of Kashmir Division (total: 6,888,475). Source: Office of the Registrar General and Census Commissioner, India.

---

## 4. Heavy Precomputed Caches & Gitignore Declarations (`data/cache/`)

To prevent repository bloat and comply with the non-negotiable research contract ("*Large caches (`data/cache/`) must never be committed to git*"), the following three intermediate binary/data artifacts are strictly gitignored:

| Cache Path | Size (Bytes) | SHA-256 Checksum | Regenerating Script | Reproduction Command |
|---|---|---|---|---|
| `data/cache/walk_graph.gpickle` | 77,051,716 | `315a345e0c77f299f59f5fb2614df6ce0bc5f75dc1138ed54d62b125d53e2f7b` | `analysis/a01_build_walk_graph.py` | `python analysis/a01_build_walk_graph.py` |
| `data/cache/catchments_network.gpkg` | 18,522,112 | `6ecaa5529abc7e41af37e5973bd670c186ea9f6234d8c2741d934a741410a9eb` | `analysis/a02_network_catchments.py` | `python analysis/a02_network_catchments.py` |
| `data/cache/osrm_responses.json` | 2,825,043 | `c7f82ddb1d83127dfd23c24b640515eb8c63f39b095a4812eb84598033eadbb6` | `analysis/a00_stage_inputs.py` | `python analysis/a00_stage_inputs.py --build-cache` |

### Gitignore Specification
The companion repository `.gitignore` must contain the following declarations:

```gitignore
# Exclude heavy precomputed caches
data/cache/*
!data/cache/.gitkeep

# Exclude binary spatial rasters if exceeding git limits (managed via data/raw/kashmir_worldpop.tif)
*.gpickle
*.gpkg
*.geoparquet
*.parquet

# Python environments and execution logs
.venv/
__pycache__/
*.py[cod]
logs/*.log
```

---

## 5. Checksum Verification Procedure

To verify that the local `data/raw/` directory matches the published manifest byte-for-byte, execute either of the following commands:

### PowerShell (Windows)
```powershell
Get-ChildItem -Path E:\kash-paper\data\raw -Recurse -File | ForEach-Object {
    [PSCustomObject]@{
        Path = $_.FullName.Replace('E:\kash-paper\data\raw\','');
        Bytes = $_.Length;
        SHA256 = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower()
    }
} | Format-Table -AutoSize
```

### Python 3
```python
import hashlib
from pathlib import Path

raw_dir = Path("data/raw")
for p in sorted(raw_dir.rglob("*")):
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{str(p.relative_to(raw_dir)):<40} {p.stat().st_size:>9} B  {h}")
```

### Bash / Linux / macOS
```bash
find data/raw -type f -exec sha256sum {} + | sort
```
