# 5. Results

> **Section owners:** Prashant, Misti. **Target length:** ~2,400 words. **Status (2026-09-30):** all
> subsections drafted from executed modules, including the a09 interval fleet in §5.7;
> §5.12 is provisional pending decision D8 (cost/emission constants). Every value cites `[CL-xx]`/`[F-x]`.
> Each subsection closes with a single *italicised policy sentence* where one is warranted.

## 5.1 The inherited network is a permit register, not a route register

The starting network is **614 permit records** `[CL-01]` that resolve, by undirected endpoint hashing
at 11 m, to **157 distinct origin–destination corridors** `[CL-02, F1]` — 155 at 100 m, so the count
is structural, not a rounding artefact. Duplication is severe and skewed: a mean of 3.91 permits per
corridor against a median of one `[CL-04]`, with **42 separate permits on the single Hazratbal–Lal Ded
axis** `[CL-03]`. This governs how consolidation may be reported. Of the apparent 71.1 % row reduction
(644 engine rows → 186 active), **71.0 percentage points are a change of the unit of analysis**
(collapsing duplicate permits on an identical corridor) and only **0.16 pp is genuine spatial
consolidation** — a single corridor, Parimpora–Pantha Chowk `[CL-07]`. Measured on physical corridors,
the plan **retains 156 of 157 (99.4 %)** and adds 30 e-bus routes `[CL-08]`: it does not shrink route
coverage. The cost of corridor-level collapse is counted rather than assumed away — **32 alternative
via-routings across 20 corridors are suppressed**, and 38/34 corridors lose vehicle-class/service-type
differentiation `[CL-09]`.

*Policy: the reform to defend is frequency and fleet discipline on retained corridors, not a cut in the
number of places served — and it should be communicated that way to operators and the public.*

## 5.2 Straight-line catchments overstate who is served by a third

Recomputing each catchment on the walkable pedestrian graph instead of as a circular buffer lowers
measured population served by a **median of 37.4 % per route** (IQR 30.5–41.7 %, max 56.8 %; 184 of 186
routes overstated by >25 %) `[CL-26, F8]`. On the deduplicated network union — the only figure that may
be reported as a network total — Euclidean buffering overstates served population by **31.9 %**
(2,339,394 → 1,592,847 residents) `[CL-27]`, revising headline division coverage from **35.5 % to
24.2 %** `[CL-28]`. The result is robust to the one free parameter: off-network tolerance
$\tau = 50/100/150$ m gives 52.8 % / 37.4 % / 29.2 % `[CL-29]`, and because the network catchment is a
formal upper bound on the true walkshed, 37.4 % is a *lower* bound on the true bias. The comparison is
clean because the Euclidean baseline is the plan's *own* number: on the 142 self-consistent routes the
reimplementation reproduces published population served to a **median error of 0.245 % (r = 0.995)**
`[CL-24, CL-25, F7]`, so the F8 gap is attributable to the pedestrian network alone. Two integrity
issues surface in passing: 44 routes carry externally substituted road distances patched in without
redrawing geometry `[CL-24, F7]`, and a tourist multiplier had silently injected **285,914 synthetic
persons** into the coverage numerator on 8 routes `[CL-30, F9]`.

*Policy: coverage claims used to justify subsidy or route awards must be quoted on the network walkshed
against residents — the Euclidean figure overstates the public benefit by roughly a third.*

## 5.3 Modelled time understates reality, and a sanity cap silently governs it

Against 43,809 driver-GPS runs, modelled run time is far too fast: **MAPE(OSRM free-flow vs observed
in-motion) = 65.1 %**, **MAPE(plan one-way vs observed) = 47.6 %**, median plan/observed ratio **0.51**
`[CL-15, CL-16, CL-17, F3]`. The mechanism is a per-kilometre cycle-time cap intended as a guardrail
that instead **binds on 169 of 186 routes (90.9 %)** — 100 % of Regional, 97.9 % of Peri-Urban, 76.5 %
of Urban `[CL-31, F10]` — while sitting *below* real pace: observed median 4.62 min/km against the
4.0 min/km Urban cap, exceeded on 83–100 % of observed corridors by class `[CL-32]`. Decomposing the
run-time model shows *where* it holds and fails: the City-Core congestion divisor (÷2.20) reproduces
observed moving speed to **+1.4 %** `[CL-33, F11]`, but the assumed constant 1.0 min/km dwell is
unsupported — observed dwell is **1.76 min/km**, and an OLS fit ($R^2 = 0.03$, non-significant distance
slope) shows dwell is fixed terminal layover, not distance-proportional `[CL-34, F11]`.

*Policy: because the binding constraint on nine-tenths of the network is a modelling ceiling set below
real driving pace, the fleet it produces is a floor, and procurement should plan against the upper end
of the interval in §5.7, not the point estimate.*

## 5.4 The rationalised hierarchy and fleet

The plan designates **186 active routes — 32 trunk and 154 feeder** `[CL-06]` — spanning 68 Urban, 47
Peri-Urban, and 71 Regional-District services, under policy headways of 15 min on the e-bus backbone, 20 min on other
high-priority routes and 35 min on medium- and low-priority routes, with demand-responsive rural
headways capped at a 50-minute maximum wait (§4.7). The required fleet is **1,011 vehicles (187 HPV /
754 MPV / 70 LPV)**, a **+68.5 % expansion over the ~600-vehicle operating baseline** `[CL-36]`. The
engine reported this as 43 buses per 100,000 residents served, inside the MoHUA 40–60 benchmark; on the
network-walkshed population of §5.2 it is **63.5 per 100,000, above the band** `[CL-60]`. The sizing
arithmetic is auditable: an independent reimplementation reproduces the published cycle time and fleet
on **all 186 routes** — including the 30 backbone routes, whose fleet is the larger of the formula and
CHALO's deployment (283 vehicles) `[CL-36, CL-55]`. Physical-alignment GPS corroborates 183 of 186 route geometries (median 94 % of length on
bus-carrying road) `[CL-35]`, while recurring *service* is observed on 66 of 186 `[CL-19]` — a floor on
activity, not a dormancy rate (§6.3).

*Policy: the fleet gap is an expansion problem, not a redistribution one — roughly 400 additional
vehicles concentrated on the busiest retained corridors, not vehicles moved off pruned routes.*

## 5.5 Network length: one kilometre of road, 3.65 kilometres of route

The 186 active routes total **5,567.7 route-km on only 1,524.5 km of distinct road** — a route-km :
network-km ratio of **3.65** `[CL-40]`. Duplication is concentrated rather than uniform: 46.6 % of the
network is served by a single route, while a 0.09 km link at Lal Chowk carries **53 routes** (28 % of
the network) `[CL-40]`. The same measure cannot be computed for the inherited permit network, because
the 458 consolidated rows carry no drawn geometry; it is bounded between 1,524.5 and 13,756.4 km and
reported as not computable rather than estimated `[CL-40]`. Consolidation therefore changed how many
vehicles run on each corridor, not how much of the road network is served — consistent with the 99.4 %
corridor retention of §5.1.

*Policy: the overlap that survives rationalisation is in the Srinagar core, and it is the place to test
through-routing or stop consolidation next — not the rural periphery, where most road is single-route.*

## 5.6 Frequent-network coverage and where the gaps are

Any-service coverage (24.2 %) flatters the network. Restricting to routes that run at least every 15
minutes [@walker2011human] — the e-bus backbone — covers **10.4 % of residents**; at 20 minutes 12.2 %, at 35 minutes 19.2 %
`[CL-42]`. The three-quarters of residents outside every walkshed are not scattered: Moran's $I$ on the
uncovered-population surface [@moran1950notes] is **0.664** on a 2 km lattice and 0.729 at 5 km (both $p = 0.001$)
`[CL-43]`, so the gaps form contiguous blocks — whole valley-floor settlement belts between the radial
corridors (Figure 8) — rather than isolated households.

*Policy: clustered gaps are addressable by a small number of new feeder corridors; they should be
identified from the uncovered surface, not from the permit register, which by construction only
describes where operators already run.*

## 5.7 Fleet as an interval, and against peer cities

Sampling the eleven declared parameters jointly (5,000 draws) leaves the plan's own fleet almost where
it was: **1,013 buses (90 % interval 989–1,058)** `[CL-56]`. That narrowness is not robustness. With the
per-km cap in place, congestion, dwell and stop spacing each move the fleet by at most 17 buses, while
removing the cap lets the same parameters move it by up to 956 `[CL-58]`; the cap has absorbed the
uncertainty, and the spare ratio alone explains 94 % of what variance remains. When urban and
peri-urban run times are instead set from the observed pace of 16 Srinagar-belt GPS corridors (regime
B, §4.10), the fleet becomes **1,182 (1,130–1,266)** — 372 urban, 428 peri-urban and 384 regional
buses, the regional figure unchanged because rural pace is unobserved `[CL-56]`. The published 1,011
lies below the whole observation-anchored interval. Variance under regime B splits between the spare
ratio (total-order index 0.55) and the two observed paces (0.32 peri-urban, 0.13 urban) `[CL-58]`, so
more GPS on peri-urban corridors is the single most valuable data investment for the fleet (§7.5).
The hierarchy, by contrast, is stable: tier agreement with the baseline partition is **97.8 %
(94.6–100 %)**, 179 of 186 routes keep their tier in more than 80 % of draws, and the population weight
of the index accounts for 93 % of the variance in agreement `[CL-57, CL-58]`.

*Policy: procure against the observation-anchored range (about 1,130–1,270 buses), treating 1,011 as
the floor the model's own guardrail produces; the service hierarchy can be adopted as it stands.*

Against 36 Indian peer cities (ASRTU 2024 city fleets) [@asrtu2024fleet], the plan's **0.154 buses per 1,000 residents of
the division** sits at the 61st percentile and inside the preferred log-model prediction interval;
per resident actually within the network walkshed it is **0.635 per 1,000** — the 97th percentile, still
inside the log-model interval but above the levels-model interval `[CL-48]`. The peers are public-sector
fleets while 1,011 is an all-operator plan, so this places the plan within national practice; it does not
validate it.

## 5.8 The three-tier hierarchy is recoverable from the data — but not the published one

Jenks partitions of the network-catchment index [@jenks1967data; @fisher1958grouping] select **$k = 3$ under both pre-registered elbow rules**
(GVF 0.902; tiers of 37, 41 and 108 routes) `[CL-37]`, Figure 7. The partition is a property of the
index, not of Jenks: 1-D $k$-means reproduces it exactly, equal intervals agree at $\kappa = 0.748$, and
only equal-count quantiles — which ignore gaps by construction — disagree ($\kappa = 0.427$) `[CL-38]`.
The uncomfortable result is that the plan's *published* bands agree with this objective partition on
only **68.3 % of routes ($\kappa = 0.503$)**, and **20 of the 55 routes the plan designates high-priority
fall in the objective bottom tier** `[CL-39]`. The discrepancy has two identifiable sources: the engine
ran Jenks on Euclidean catchments across all 644 permit rows, including those later consolidated, and its
post-Jenks overrides (backbone lock, social
and district-headquarters floors) promote routes irrespective of index value.

*Policy: the hierarchy should be re-derived on network catchments before headways are fixed; the 20
promoted routes need an explicit, stated justification (social obligation, backbone status) or a demotion.*

## 5.9 Equity: who is served, and who loses

Accessibility — departures per hour reachable within a 400 m network walk, per resident — is extremely
unequal: population-weighted **Gini 0.903** [@delbosc2011using], driven by the **75.8 % of residents with no reachable
service**; among served residents it is 0.599 `[CL-44]`. A before/after comparison is not reported
because the consolidated permits have no geometry from which to rebuild the inherited network; the
module returns this as not computable rather than manufacturing a counterfactual `[CL-44]`. The losers of
consolidation are named instead (Table 5g): **32 alternative via-routings on 20 corridors are
suppressed; 114,879 residents live within 400 m of a dropped intermediate place, and 13,087 of them lose
bus access outright** because no surviving route passes within walking distance `[CL-45]`. The largest
single losses are Zoonimar on the Jehangir Chowk–Soura corridor (3,515 residents) and Rainawari on
Hazratbal–Lal Ded (3,046).

*Policy: the 13,087 residents who lose access are few and locatable; restoring a via-stop or a short
feeder for them is cheap relative to defending their loss.*

## 5.10 Transfers and waiting

On the rationalised network, 12.5 % of stop-to-stop pairs are one-seat rides, 72.3 % need one
interchange and 13.8 % two or more (1.4 % unconnected on drawn geometry) `[CL-46]`; these are shares of
stop pairs, not of trips, because no origin–destination matrix exists. For the 68 origin–destination
pairs whose permits were consolidated, **66 keep a one-seat ride** and two fall to one interchange.
Because the inherited permits ran only part of the day — the observed median vehicle is in service for
217 minutes, a duty factor of 0.242 `[CL-47]` — the plan's scheduled headways cut the median expected
wait [@welding1957instability; @osuna1972control] from 86.7 to 17.5 minutes, yet **5 of 68 pairs (7.4 %) wait longer**, and the median transfer
penalty at which consolidation stops paying is 31.4 minutes `[CL-46]`.

## 5.11 Operations: time of day, deadhead, and load

*Time of day.* The e-bus backbone's hourly boardings (1,221,848 in April 2026) peak at 09:00 with a
peak-hour factor of 10.67 % and a peak-to-base ratio of 1.37 `[CL-41]`. Reading the published headways as
peak design and relaxing them off-peak saves **9.4 % of bus-hours at the same 1,011 vehicles**; reading
them as all-day means would instead require 215–496 more buses at the peak `[CL-41]`.

*Deadhead.* No depot register exists, so deadhead is bounded rather than measured: zero if buses lay
over at a terminus, **1.7 %** of bus-kilometres if every bus returns to its district-headquarters stand
on the plan's 16-hour day, and 5.5 % on the operating day buses are actually observed to run `[CL-49]`.
The gap exposes a larger assumption: the plan implies **320 service-km per bus per day**, against 99 at
the observed duty `[CL-49]`.

*Load.* On the backbone, where boardings are observed, a CHALO bus-trip today carries 18.6–37.3
boardings (the operator's trip count is ambiguous between one-way and round trips). Running the same
routes at 15 minutes, with ridership held at today's level, gives **8.3 boardings per trip on day one**;
ridership must grow **2.2–4.5-fold** to restore today's loads `[CL-50]`. Across the network the
quarantined demand proxy (Eq. 8) implies a median peak boarding-to-capacity ratio of 0.23, with 152 of
186 routes below 0.40 `[CL-50]`.

*Policy: the plan is a supply-led bet on induced ridership; procurement should be staged against
observed boardings on the backbone, where they can be measured monthly, rather than committed in full.*

## 5.12 Cost and emissions (provisional)

With every external constant carried as a range pending verification, the plan costs **₹642–1,054
crore a year** to operate at its own vehicle-kilometres, or ₹206–338 crore at the observed operating day,
and emits 65–103 kt (or 21–33 kt) of CO₂ `[CL-51]`. Per resident within the walkshed, that is
₹4,033–6,615 a year on the plan's own kilometres. In passing, the engine's own emissions column assumes
30 g CO₂/km for the electric backbone; at published energy intensities and the Indian grid factor the
figure is of the order of 870 g/km, an understatement of about 29-fold `[CL-51]`, so the engine column is
not used.

## 5.13 Scenario stress-test

Table 8 changes one lever at a time from the published plan (S0: 1,011 buses, 24.2 % coverage)
`[CL-52]`. Replacing modelled urban and peri-urban run time with observed pace (S1) raises the fleet to
**1,169 (+15.6 %)**; bounding rural pace with the only two long observed corridors as well (S2) gives
1,271 (+25.7 %). Returning rural lifelines to a flat 35-minute headway (S3) costs 95 buses (+9.4 %) — the
price of the 50-minute rural maximum. Applying the engine's own merge test at the low end of its
threshold range (S4) would cut the network to 84 routes and 533 buses but lose 3.9 points of coverage
(24.2 → 20.3 %). Running every urban route at 15 minutes (S5) costs 161 buses (+15.9 %) and raises
15-minute coverage from 10.4 % to 14.5 %. The frontier (Figure S1) prices city frequency directly: each
step from 35 to 10 minutes costs progressively more, and more again at observed pace.

*Policy (network level): the published plan is a defensible point on this frontier only if read as a
lower bound — the realistic run-time scenarios all require more buses, and the one scenario that saves
buses does so by withdrawing coverage.*
