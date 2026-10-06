**Validation V1: WorldPop population vs building footprints, by source, in the order the layers were adopted (Spearman rho; threshold > 0.6 declared in the claim ledger on 2026-09-08 for the OSM layer, not registered; the Microsoft layer was added afterwards; circularity disclosed in text)**

| Source    | Scale                                  | Measure        |   rho |        p | Pass   | Declared_order                                   |
|:----------|:---------------------------------------|:---------------|------:|---------:|:-------|:-------------------------------------------------|
| osm       | Route catchment (n = 186)              | footprint area | 0.657 | 2.4e-24  | True   | 1st: declared 2026-09-08 (fails at grid scale)   |
| osm       | Route catchment (n = 186)              | building count | 0.544 | 9.6e-16  | False  | 1st: declared 2026-09-08 (fails at grid scale)   |
| osm       | 1 km grid, all cells (n = 13,645)      | footprint area | 0.316 | 0        | False  | 1st: declared 2026-09-08 (fails at grid scale)   |
| osm       | 1 km grid, populated cells (n = 9,255) | footprint area | 0.312 | 4e-208   | False  | 1st: declared 2026-09-08 (fails at grid scale)   |
| microsoft | Route catchment (n = 186)              | footprint area | 0.975 | 1.9e-122 | True   | 2nd: added 2026-10-01, after the OSM grid result |
| microsoft | Route catchment (n = 186)              | building count | 0.94  | 9.7e-88  | True   | 2nd: added 2026-10-01, after the OSM grid result |
| microsoft | 1 km grid, all cells (n = 13,645)      | footprint area | 0.907 | 0        | True   | 2nd: added 2026-10-01, after the OSM grid result |
| microsoft | 1 km grid, populated cells (n = 9,255) | footprint area | 0.95  | 0        | True   | 2nd: added 2026-10-01, after the OSM grid result |
