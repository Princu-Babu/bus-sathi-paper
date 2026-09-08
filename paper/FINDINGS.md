# Findings that change the paper

Running record of results that alter what the paper can claim. Each entry names
the module that produced it so the number can be regenerated. Numbers here are
authoritative over anything inherited from the engine's own documentation.

---

## F1 — The register is a permit register, not a route register (`q01`, D1)

`existing-routes.csv` carries **one row per permitted vehicle-service**, not one
row per route. 614 rows describe **157 distinct origin–destination corridors** at
11 m endpoint resolution (155 at 100 m — so this is not a rounding artefact).
Mean 3.9 permits per corridor; the largest corridor, Hazratbal–LD, carries **42**.
The recurrence is by operator, vehicle class (MPV/LPV), service type
(Ordinary/Express/Goods) and spelling of the same via point
(RAINAWARI / RAINAWARA; TENGPORA / MOMINABAD TENGPORA).

**Consequence.** The engine's funnel is 644 rows (614 permits + 30 synthetic
e-bus backbone) → 186 active, a 71.1% "reduction". Decomposed:

| Component | pp of the 71.1% |
|---|---|
| Change of unit — collapsing duplicate rows on an identical corridor | **71.0** |
| Consolidation of a *distinct* corridor on spatial overlap | **0.2** (1 corridor) |

Measured on corridors the design **retains 156 of 157 (99.4%)** and adds 30 e-bus
routes. **The plan does not reduce route count.** What it changes is frequency,
vehicle allocation and fleet size.

This must be stated in §3 and again at the top of §5. Any "39% route reduction"
or "342 permits → 207 routes" claim inherited from the earlier draft is wrong in
kind, not just in magnitude, and has to go. It is also a direct answer to the
reviewer watch-out in the paper plan ("'342 permits' is not '342 operating
routes'"): the honest version is stronger than the anticipated objection.

**What collapsing costs, counted rather than asserted away:** 20 corridors carry
more than one distinct via routing, so **32 alternative via routings are
suppressed** — passengers on the non-representative path lose their direct link.
38 corridors mix vehicle classes and 34 mix service types, so a single headway
and a single vehicle mix replace a differentiated offer. Report this as a
limitation of corridor-level planning, with the count.

Reproduced from published files only: the positional permit→plan join
(`R{i+1:04d}`) is verified at an 80.5% origin-and-destination name-token match
rate against the engine's own normalised route names, and the corridor key is the
engine's own 4-decimal undirected endpoint key
(`transit_kashmir_v3.py:3366`).

---

## F2 — WorldPop 2026 is below Census 2011 for the same districts (`q01`, D4)

Zonal sum over the 10-district union = **6,584,763** (matches the engine
denominator 6,584,762, so the coverage share is internally consistent). Census
2011 for the same districts = **6,888,475**. Ratio **0.956**, implied
**−0.30%/yr** over 15 years, against J&K decadal growth of 23.6% (~2.1%/yr) to
2011. The raster fully covers the district union, so this is not truncation.

**Consequence.** The population surface is conservative. Coverage *shares* are
therefore biased **upward** (a smaller denominator), while absolute
population-served counts are biased **downward**. State both directions
explicitly; do not rescale the raster — rescaling would break comparability with
the published plan and substitute a growth assumption for a measurement.

---

## F3 — Modelled run time substantially understates observed run time (`q01`, D6)

Against driver-GPS runs on matched corridors: **MAPE(OSRM driving vs observed
in-motion) = 65.1%**; **MAPE(plan one-way vs observed one-way) = 47.6%**; median
plan/observed = **0.51**. The comparison is against observed *in-motion* time for
OSRM (which excludes dwell) and against observed *total* for the plan (which
includes stop penalties), so neither is a unit mismatch.

**Consequence.** Cycle time — and therefore fleet — is understated wherever it is
not anchored to measurement. v3.4.5 re-anchored 5 corridors and fleet rose
1,004→1,011, but only 5 of 186 routes are measured. This is the strongest
argument in the paper for reporting fleet as an interval, not a point, and it
must be carried into the Monte Carlo as a speed-multiplier prior rather than
buried as a caveat.

---

## F4 — Activity is a lower bound, not a status (`q01`, D2)

**66 of 186 (35%)** active routes appear in the operator's driver-GPS record.
The remaining 120 are `NO_APP_DATA`, which reflects app adoption among drivers,
not proven dormancy. Report as an observational floor on activity; do not report
the complement as a dormancy rate.

---

## F5 — Opportunity data is heavily concentrated in Srinagar (`q01`, D5)

2,431 POIs, none unplaced, **65% in Srinagar**; per-100k density ranges
**0.3–120.4** across districts. Whether this is real opportunity concentration or
OSM mapping effort cannot be separated with these data, and no field enumeration
was carried out.

**Consequence.** The POI term in the composite index is the channel most exposed
to volunteered-data bias. It must be carried in the weight sensitivity (equal /
entropy / PCA) and in the Monte Carlo, and the index must be shown to be
decision-robust to down-weighting it.

---

## F7 — The published plan is internally inconsistent on 47 of 186 routes (`a02`, `a02b`)

Recomputing the Euclidean catchment with the engine's exact method — same
geometries, 250 m virtual stops, 400 m discs, `rasterstats.zonal_stats` in WGS84
with the raster's own nodata — reproduces the plan's `Population_Served_Raw`
**essentially exactly on most routes and fails on an identifiable minority**. The
split is not random:

| Group | n | `Route_KM` | geometry length vs `Route_KM` |
|---|---|---|---|
| Self-consistent | **142** | unrounded (e.g. 10.099, 14.207) | within 1% |
| Substituted distance | **44** | exact half-km (6.5, 17.0, 151.0) | 0.76–1.14× |

The half-km values are the externally verified road distances substituted by the
v3.4.4 correction pass, which rewrote `Route_KM` (and hence cycle time and fleet)
**without redrawing the geometry or recomputing population**. On those routes
`Route_KM` comes from one source and the geometry and `Population_Served_Raw`
from another. Worst cases: Srinagar–Chowkibal (125.5 km declared, 94.9 km drawn),
Srinagar–Uri (101.0 vs 77.6), Srinagar–Tangdar (151.0 vs 120.7).

**Faithfulness, and the full inventory of residuals** (`a02b`). On the 142
self-consistent routes the reimplementation reproduces the published column to a
**median absolute error of 0.245%** with **r = 0.995**, once the engine's
undocumented tourist multiplier (F9) is applied. Every route that does not
reproduce is named rather than left as noise:

| Disposition | n | Meaning |
|---|---|---|
| Reproduced (≤1%) | **136** | reimplementation matches the plan |
| Reproduced, minor drift (≤5%) | 3 | FDR-525, FDR-479, SSCL-11 |
| Stale tourist flag | 1 | SSCL-27 boosted under a flag since cleared |
| Superseded geometry | **2** | FDR-438 (0.419×), FDR-160 (0.630×) |
| Substituted distance — no valid target | 44 | see above |

**Consequence.** Two things follow. First, the Euclidean baseline used for the
network comparison in F8 is demonstrably *the plan's own number*, not an
approximation of it, so the difference F8 measures is attributable to the
pedestrian network alone. Second, this is the concrete cost of a pipeline that
patches outputs instead of re-running, and the paper should say so plainly in the
limitations: the reproduction package recomputes every downstream quantity from
geometry, so the inconsistency cannot recur.

---

## F8 — Euclidean catchments overstate population served by a third (`a02`)

Across all 186 active routes, replacing straight-line distance with walking
distance on an OSM pedestrian graph reduces measured population served by a
**median of 37.4% per route** (IQR 30.5–41.7%, max 56.8%). **184 of 186 routes
are overstated by more than 25%**; 11 by more than 50%. On the deduplicated
network union the overstatement is **31.9%** (2,339,394 → 1,592,847 residents),
which moves headline coverage from **35.5% to 24.2%** of the study population.
The network catchment is about **half** the Euclidean area (median area ratio
0.502).

Method: identical geometries, virtual stops and walk budget, the only change
being that distance is measured on the graph (961,927 nodes / 973,569 edges /
23,323 km, built offline from the India extract) instead of as the crow flies.
The network catchment is `∪ B(v, min(400 − d(v), τ))` over nodes within the 400 m
budget of a snapped stop, with τ = 100 m — one WorldPop cell, since the
population surface cannot resolve a finer tail. Because the final leg may run
straight, the network catchment is an **upper bound** on the true walkshed, so
the measured overstatement is a **lower bound** on the true bias.

**Robust to the one free parameter.** τ = 50 / 100 / 150 m gives a median
overstatement of **52.8% / 37.4% / 29.2%**. The finding is large and
same-signed across the whole defensible range, so it does not rest on the choice
of τ.

**Not an artefact of a sparse graph.** Of 22,360 virtual stops, only **46
(0.21%)** lie farther than the entire 400 m budget from the network; median snap
offset is **11.0 m**.

**Consequence.** This is the paper's central methodological result and the
justification for the PDF's "non-negotiable" requirement. Euclidean buffers are
the near-universal default in the rationalisation literature this paper sits in;
the correction is a third of the reported benefit.

---

## F9 — A demand multiplier is embedded in a population measurement (`a02b`)

`transit_kashmir_v3.py:1863` multiplies `Population_Served` by
`TOURIST_POPULATION_MULTIPLIER = 1.3` on the 8 active routes flagged
`Tourist_Corridor`, to stand in for visitors a residential raster cannot see.
The intent is defensible. The placement is not: the result is written to a column
named as a population count and then used as the **numerator of a coverage
share**, so on those routes the reported "population served" is not a population
and the coverage share is not a share of residents. The embedded adjustment is
**285,914** (published 1,238,960 vs resident 953,046 across the 8 routes; these
walksheds overlap and the sum is quoted only to size the effect, never as a
network total).

It is also undocumented in the published outputs — it was recoverable only
because the reproduction residuals clustered at exactly 1/1.3, and one route
(SSCL-27) still carries the boost under a flag that has since been cleared.

**Consequence.** The reproduction package keeps resident population and any
demand adjustment in **separate columns**, and the paper reports coverage against
residents only. Stated as a general methodological point: a visitor-demand term
belongs in the demand model, not in the catchment measurement, because once
mixed in it silently propagates into every coverage statistic downstream.

---

## F6 — Mapped road density tracks population density closely (`q01`, D3)

**18,533 km** of walkable network inside the 10 districts (23,323 km in the
padded bounding box). ρ(population density, mapped road density) = **0.92**
across districts.

**Consequence.** This is the usual peripheral-bias check for volunteered
geographic data, and it comes out benign at district scale: OSM is not
conspicuously thin where people are. It supports using the OSM pedestrian graph
for network catchments (F8) without a completeness correction, and should be
reported as such rather than left implicit.

---

## F10 — An intended sanity cap is the actual binding constraint on fleet (`v04`)

The per-kilometre cycle-time ceiling (`t_cyc ≈ 2·Route_KM·ω_class`, with ω =
4.0 / 2.5 / 1.5 min/km for Urban / Peri-Urban / Regional) was meant as a
guardrail against runaway cycle times. It instead **binds on 169 of 186 routes
(90.9%)** — 100% of Regional (71/71), 97.9% of Peri-Urban (46/47), 76.5% of
Urban (52/68) `[CL-31]`. And it sits **below** real driving pace: observed median
bus pace from driver GPS is **4.62 min/km** (p90 6.28), exceeding the Urban cap
(4.0) on 83.3% of observed corridors, the Peri-Urban cap (2.5) on 88.9%, and the
Regional cap (1.5) on 100% `[CL-32]`.

**Consequence.** An intended ceiling became the primary driver of cycle time — and
therefore fleet — across nine-tenths of the network, and because it lies below
measured pace it truncates cycle time **downward**. The published fleet is thus a
**floor**, which is the mechanical reason (alongside F3) to report fleet as an
interval and to procure against its upper end, not the point estimate. Carried in
§5.3, §5.7, §6.3, Table 6c.

---

## F11 — The congestion model holds in the core; the dwell model does not (`v04`)

Decomposing modelled run time against 43,809 driver-GPS runs separates two
assumptions. The **City-Core congestion divisor (2.20)** reproduces observed bus
moving speed to **+1.4% median bias** (modelled 17.95 vs observed 20.55 km/h,
MAPE 28.4%) `[CL-33]`; the Peri-Urban (+59.4%) and Rural (+123.2%) multipliers
fail here, but every observed corridor sits in the greater-Srinagar urban region,
so those are classification counterfactuals, not field-tested values. The
**constant 1.0 min/km dwell** assumption fails: observed dwell is **1.76 min/km**
(median dwell share 38%, range 15–74%), and an OLS fit `dwell = 17.67 + 0.247·km`
has R² = 0.03 with a significant intercept (95% CI [7.41, 27.94]) and a
non-significant distance slope `[CL-34]` — dwell is dominated by fixed terminal
layover and dispatch holds, not by distance.

**Consequence.** The urban moving-speed model is empirically sound and can be
trusted; the distance-proportional dwell model is not and should be replaced by a
fixed-layover-plus-boardings form. Both feed the Monte Carlo speed/run-time prior
(§4.10). Carried in §6.3, Table 6b.

---

## F12 — Road-alignment coverage is not service validation (`v04`)

Two GPS coverage metrics measure different things and must never be conflated.
**`obs_frac`** — the fraction of a planned alignment lying on roads that carry
observed bus traffic — is > 0 on **183 of 186 routes** (median 0.94; 171 ≥ 50%,
137 ≥ 80%, 33 = 100%): the planned *geometry* overwhelmingly follows roads buses
actually use. **`observed_status`** — recurring service on the route itself — holds
for only **66 of 186 routes** (35.5%; 45 partial, 75 no-app-data) `[CL-35, CL-19]`.

**Consequence.** "94% of alignments run on bus-carrying road" is a statement about
geometry; "35.5% of routes are corroborated as recurring services" is a statement
about operations, and it is a lower bound set by driver-app uptake (F4), not a
dormancy rate. The paper reports both and conflates neither. Carried in §3.5, §5.4,
§6.3.
