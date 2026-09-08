**Validation V4: run-time error decomposed into moving speed and dwell against observed driver GPS**

| comparison                                      | unit   |   n |   observed_median |   modelled_median |   mape_pct |   bias_pct |   ratio_median |   spearman_rho |   spearman_p |   pearson_r | mape_pass   | rank_pass   |
|:------------------------------------------------|:-------|----:|------------------:|------------------:|-----------:|-----------:|---------------:|---------------:|-------------:|------------:|:------------|:------------|
| Moving speed: OSRM/2.2 (City_Core) vs observed  | km/h   |  14 |            20.55  |            17.945 |       28.4 |        1.4 |          0.895 |         -0.069 |       0.816  |      -0.123 | False       | False       |
| Moving speed: OSRM/1.4 (Peri_Urban) vs observed | km/h   |  14 |            20.55  |            28.199 |       59.4 |       59.4 |          1.406 |         -0.069 |       0.816  |      -0.123 | False       | False       |
| Moving speed: OSRM/1.0 (Rural) vs observed      | km/h   |  14 |            20.55  |            39.479 |      123.2 |      123.2 |          1.969 |         -0.069 |       0.816  |      -0.123 | False       | False       |
| Dwell: engine 1.0 min/km vs observed            | min/km |  18 |             1.757 |             0.982 |       61.6 |      -22.3 |          0.558 |         -0.37  |       0.1302 |      -0.698 | False       | False       |
