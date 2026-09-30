**Validation V1: WorldPop population vs OpenStreetMap building footprints (Spearman rho; partial circularity disclosed in text)**

| Scale                                  | Measure        |   rho |       p | Target   | Pass   |
|:---------------------------------------|:---------------|------:|--------:|:---------|:-------|
| Route catchment (n = 186)              | footprint area | 0.657 | 2.4e-24 | > 0.6    | True   |
| Route catchment (n = 186)              | building count | 0.544 | 9.6e-16 | > 0.6    | False  |
| 1 km grid, all cells (n = 13,645)      | footprint area | 0.316 | 0       | > 0.6    | False  |
| 1 km grid, populated cells (n = 9,255) | footprint area | 0.312 | 4e-208  | > 0.6    | False  |
