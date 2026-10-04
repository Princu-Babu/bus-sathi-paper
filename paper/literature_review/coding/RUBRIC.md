# Table 1 coding rubric (apply identically to every study)

Code what the study's MAIN METHOD REQUIRES / DOES, from the abstract and — wherever the abstract is not decisive — from open-access full text (try doi.org, Unpaywall `https://api.unpaywall.org/v2/<doi>?email=research@example.org`, OpenAlex, arXiv, publisher page). Record `basis` = abstract | abstract+web | fulltext. Never guess: if a field cannot be determined, write `unclear` and say why in `note`.

Fields
- `geography`: country/city of application, or "benchmark network (Mandl/…)" or "synthetic".
- `region_class`: Global North | Global South (non-India) | India | benchmark/synthetic | multi.
- `planning_stage` (one, the primary): route design (new network) | route redesign/rationalisation (existing network) | frequency/headway | fleet sizing | integrated (≥2 of route/frequency/fleet) | demand/OD estimation | network evaluation/accessibility | network mapping/data creation | diagnosis (overlap/efficiency).
- `method_family`: exact optimisation | (meta)heuristic | rule/guideline-based | GIS/accessibility analysis | simulation | data-mining (AFC/GPS/phone) | network-science indicators | mixed.
- `demand_input` (what demand information the method consumes): none | proxy (population/POI/land use/need index) | synthetic or benchmark OD | modelled OD (4-step/calibrated model) | survey OD/counts | mobile-phone/taxi-GPS traces | AFC/smart card | APC/boarding counts.
- `data_intensity` 1–5 = HIGHEST level the method requires to produce its main output:
  1 open data only (OSM, gridded population, open POIs, routing engine);
  2 + official static data (census tracts, land use, published GTFS schedule, operator route/stop register, road inventory);
  3 + partial observations (sample counts, on-board/intercept surveys, operator GPS/AVL, crowd-sourced traces);
  4 + full demand matrix (household-survey OD, calibrated model OD, benchmark/synthetic OD that the method needs as input, mobile-phone OD);
  5 + passive ridership at stop/trip level (AFC/smart card, APC).
  Rule: a method tested only on a benchmark network with a given OD matrix is level 4 (it needs an OD matrix).
- `equity`: none | coverage only | distributional metric (Gini/Lorenz/group comparison) | explicit equity objective/constraint.
- `validation`: none | benchmark-instance comparison | back-cast vs observed counts/ridership | comparison with existing network/GTFS | field/expert | sensitivity/uncertainty analysis | multiple (list).
- `implementable_plan`:
  Yes = specific routes AND frequencies (or fleet) for a REAL city;
  Partial = real-city output covering only part of a service plan (routes only, frequencies only, stop changes, or a diagnosis/ranking of real routes);
  No = method demonstrated on benchmark/synthetic network, OR assessment/measurement/mapping/OD-estimation with no service-plan output.
- `code_released`: yes (give URL) | no | unclear.
- `note`: ≤25 words, the fact that justified the hardest call.

Output CSV columns (exact order):
cid,geography,region_class,planning_stage,method_family,demand_input,data_intensity,equity,validation,implementable_plan,code_released,basis,note
