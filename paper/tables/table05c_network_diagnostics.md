**Network diagnostics for the rationalised plan: route-km against unique network-km, link duplication, and the baseline quantities that the published release does and does not support**

| quantity                                            |     value | unit   | status              | basis                                                                |
|:----------------------------------------------------|----------:|:-------|:--------------------|:---------------------------------------------------------------------|
| Active routes carrying service                      |   186     | routes | COMPUTED            | GeoJSON features                                                     |
| Baseline permit-routes                              |   644     | routes | COMPUTED            | plan CSV, all rows                                                   |
| Route-km, active network                            |  5567.7   | km     | COMPUTED            | geometry length, UTM 43N                                             |
| Route-km, baseline                                  | 13756.4   | km     | COMPUTED            | Route_KM column, all rows                                            |
| Unique network-km, active                           |  1524.5   | km     | COMPUTED            | distinct OSRM links (union cross-check 1524.5 km)                    |
| Unique network-km, baseline                         |           | km     | NOT_COMPUTABLE      | no geometry for the 458 merged rows; bounded to [1524.5, 13756.4] km |
| Route-km : network-km, active                       |     3.652 | ratio  | COMPUTED            | headline duplication statistic                                       |
| Mean routes per network link                        |     3.309 | routes | COMPUTED            | 35650 distinct links                                                 |
| Mean routes per network-km (km-weighted)            |     3.645 | routes | COMPUTED            | weighted by link length                                              |
| Median routes per network-km (km-weighted)          |     2     | routes | COMPUTED            | weighted by link length                                              |
| 90th percentile routes per network-km (km-weighted) |     9     | routes | COMPUTED            | weighted by link length                                              |
| Maximum routes on one link                          |    53     | routes | COMPUTED            | Lalchowk, Srinagar                                                   |
| Network-km served by exactly one route              |   710.132 | km     | COMPUTED            | 46.6% of the network                                                 |
| Network-km carrying >= 10 routes                    |   128.466 | km     | COMPUTED            | 8.4% of the network                                                  |
| Permit chords, distinct geometries                  |   200     | chords | PROXY_STRAIGHT_LINE | of 614 permits; chords are not road alignments                       |
