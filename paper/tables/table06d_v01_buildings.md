**Validation V1: WorldPop population vs building footprints, by source (Spearman rho, target > 0.6; partial circularity disclosed in text)**

| Source   | Scale                                  | Measure        |   rho |       p | Pass   |
|:---------|:---------------------------------------|:---------------|------:|--------:|:-------|
| osm      | Route catchment (n = 186)              | footprint area | 0.657 | 2.4e-24 | True   |
| osm      | Route catchment (n = 186)              | building count | 0.544 | 9.6e-16 | False  |
| osm      | 1 km grid, all cells (n = 13,645)      | footprint area | 0.316 | 0       | False  |
| osm      | 1 km grid, populated cells (n = 9,255) | footprint area | 0.312 | 4e-208  | False  |
