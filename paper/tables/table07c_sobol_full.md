**Sobol' indices with 95% bootstrap confidence half-widths (N = 1024, 100 resamples); flag marks estimates outside [0, 1]**

| Output                      | Parameter                            |      S1 |   S1_ci95 |     ST |   ST_ci95 | S1_distinguishable_from_zero   | ST_distinguishable_from_zero   | flag     |
|:----------------------------|:-------------------------------------|--------:|----------:|-------:|----------:|:-------------------------------|:-------------------------------|:---------|
| Fleet A (as specified)      | Walk catchment radius (m)            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Catchment sampling interval (m)      |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Assumed stop spacing for dwell (m)   |  0.0075 |    0.0124 | 0.0226 |    0.0039 | False                          | True                           |          |
| Fleet A (as specified)      | Composite weight on population       |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Tier-2 opportunity weight            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Tier-3 (seasonal) opportunity weight |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Tourist-corridor catchment boost     |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | City-core congestion multiplier      |  0.0019 |    0.0089 | 0.0109 |    0.0019 | False                          | True                           |          |
| Fleet A (as specified)      | Dwell penalty per stop (min)         |  0.0241 |    0.0182 | 0.0384 |    0.0058 | True                           | True                           |          |
| Fleet A (as specified)      | Fleet spare ratio                    |  0.9436 |    0.0825 | 0.9457 |    0.0624 | True                           | True                           |          |
| Fleet A (as specified)      | Observed urban pace (min/km)         |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet A (as specified)      | Observed peri-urban pace (min/km)    |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Walk catchment radius (m)            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Catchment sampling interval (m)      |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Assumed stop spacing for dwell (m)   | -0.0016 |    0.0023 | 0.0007 |    0.0001 | False                          | True                           | negative |
| Fleet B (obs.-anchored)     | Composite weight on population       |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Tier-2 opportunity weight            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Tier-3 (seasonal) opportunity weight |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Tourist-corridor catchment boost     |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | City-core congestion multiplier      |  0      |    0.0001 | 0      |    0      | False                          | False                          |          |
| Fleet B (obs.-anchored)     | Dwell penalty per stop (min)         | -0.0006 |    0.0026 | 0.0011 |    0.0002 | False                          | True                           | negative |
| Fleet B (obs.-anchored)     | Fleet spare ratio                    |  0.5695 |    0.0912 | 0.581  |    0.087  | True                           | True                           |          |
| Fleet B (obs.-anchored)     | Observed urban pace (min/km)         |  0.1494 |    0.0601 | 0.151  |    0.0397 | True                           | True                           |          |
| Fleet B (obs.-anchored)     | Observed peri-urban pace (min/km)    |  0.2443 |    0.1451 | 0.3    |    0.1073 | True                           | True                           |          |
| Fleet B-mov (engine method) | Walk catchment radius (m)            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | Catchment sampling interval (m)      |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | Assumed stop spacing for dwell (m)   |  0.3116 |    0.0478 | 0.3453 |    0.0375 | True                           | True                           |          |
| Fleet B-mov (engine method) | Composite weight on population       |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | Tier-2 opportunity weight            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | Tier-3 (seasonal) opportunity weight |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | Tourist-corridor catchment boost     |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Fleet B-mov (engine method) | City-core congestion multiplier      | -0      |    0      | 0      |    0      | False                          | False                          | negative |
| Fleet B-mov (engine method) | Dwell penalty per stop (min)         |  0.4232 |    0.0488 | 0.4602 |    0.0492 | True                           | True                           |          |
| Fleet B-mov (engine method) | Fleet spare ratio                    |  0.1927 |    0.0385 | 0.2005 |    0.022  | True                           | True                           |          |
| Fleet B-mov (engine method) | Observed urban pace (min/km)         |  0.0157 |    0.0097 | 0.0163 |    0.0016 | True                           | True                           |          |
| Fleet B-mov (engine method) | Observed peri-urban pace (min/km)    |  0.0201 |    0.0131 | 0.0204 |    0.0025 | True                           | True                           |          |
| Coverage                    | Walk catchment radius (m)            |  0.9744 |    0.0656 | 0.9749 |    0.0561 | True                           | True                           |          |
| Coverage                    | Catchment sampling interval (m)      |  0.0256 |    0.0135 | 0.026  |    0.0022 | True                           | True                           |          |
| Coverage                    | Assumed stop spacing for dwell (m)   |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Composite weight on population       |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Tier-2 opportunity weight            |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Tier-3 (seasonal) opportunity weight |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Tourist-corridor catchment boost     |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | City-core congestion multiplier      |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Dwell penalty per stop (min)         |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Fleet spare ratio                    |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Observed urban pace (min/km)         |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Coverage                    | Observed peri-urban pace (min/km)    |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Walk catchment radius (m)            |  0.0378 |    0.0356 | 0.1398 |    0.0294 | True                           | True                           |          |
| Tier agreement              | Catchment sampling interval (m)      |  0.0056 |    0.0319 | 0.129  |    0.0273 | False                          | True                           |          |
| Tier agreement              | Assumed stop spacing for dwell (m)   |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Composite weight on population       |  0.8286 |    0.0899 | 0.9286 |    0.0803 | True                           | True                           |          |
| Tier agreement              | Tier-2 opportunity weight            |  0.0094 |    0.0176 | 0.03   |    0.0089 | False                          | True                           |          |
| Tier agreement              | Tier-3 (seasonal) opportunity weight |  0.0038 |    0.0137 | 0.0283 |    0.0089 | False                          | True                           |          |
| Tier agreement              | Tourist-corridor catchment boost     | -0.0083 |    0.0073 | 0.0078 |    0.003  | True                           | True                           | negative |
| Tier agreement              | City-core congestion multiplier      |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Dwell penalty per stop (min)         |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Fleet spare ratio                    |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Observed urban pace (min/km)         |  0      |    0      | 0      |    0      | False                          | False                          |          |
| Tier agreement              | Observed peri-urban pace (min/km)    |  0      |    0      | 0      |    0      | False                          | False                          |          |
