**Jenks natural-breaks goodness of variance fit for k = 2..7 on the network-catchment index (n = 186 routes), with the marginal and second-difference returns that locate the elbow. The 0.80 floor is an assumption (no source cited); k = 2 scores 0.7855, just below it, and the second difference is undefined at k = 2 and k = 7, so neither rule independently establishes three tiers. Exact-optimum column: globally optimal contiguous partition from an exact dynamic program**

|   k |    gvf |   gvf_exact_optimum | gvf_above_floor_0_80   |   delta_gvf |   second_difference_gvf | n_per_class                     |   smallest_class_n | selected   |
|----:|-------:|--------------------:|:-----------------------|------------:|------------------------:|:--------------------------------|-------------------:|:-----------|
|   2 | 0.7855 |              0.7855 | no                     |             |                         | 128 / 58                        |                 58 |            |
|   3 | 0.9023 |              0.9023 | yes                    |      0.1168 |                  0.086  | 108 / 41 / 37                   |                 37 | yes        |
|   4 | 0.9331 |              0.9331 | yes                    |      0.0308 |                  0.0057 | 55 / 59 / 37 / 35               |                 35 |            |
|   5 | 0.9582 |              0.9582 | yes                    |      0.0251 |                  0.0131 | 52 / 56 / 31 / 26 / 21          |                 21 |            |
|   6 | 0.9702 |              0.9702 | yes                    |      0.012  |                  0.0047 | 52 / 56 / 25 / 22 / 25 / 6      |                  6 |            |
|   7 | 0.9775 |              0.9775 | yes                    |      0.0073 |                         | 52 / 56 / 22 / 18 / 17 / 16 / 5 |                  5 |            |
