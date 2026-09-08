# 5. Results

> **Section owners:** Prashant, Misti. **Target length:** ~2,400 words. **Status:** diagnosis subsections
> (§5.1–§5.4) are complete and fully sourced; design/evaluation/stress-test subsections (§5.5–§5.13) are
> scaffolded and marked **⏳ pending module execution** with the exact module and statistic each awaits —
> no result is stated before its module has run. Every value cites `[CL-xx]`/`[F-x]`. Each completed
> subsection closes with a single *italicised policy sentence*.
>
> **Ordering** (per plan): diagnosis (§5.1–§5.3) → design (§5.4–§5.7) → evaluation (§5.8–§5.12) →
> stress-test (§5.13).

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
differentiation `[CL-09]`. Any inherited "39 % route reduction" or "342 permits → 207 routes" claim is
wrong in kind, not merely magnitude.

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
Peri-Urban, and 71 Regional-District services, under policy headways of 15/20/35 min (Urban / Peri-Urban
/ e-bus backbone) and demand-responsive rural headways capped at a 50-minute maximum wait (§4.7). The
required fleet is **1,011 vehicles (187 HPV / 754 MPV / 70 LPV)**, a **+68.5 % expansion over the
~600-vehicle operating baseline** and **43 buses per 100,000 residents served**, inside the MoHUA
40–60 benchmark `[CL-36]`. The sizing arithmetic is auditable: an independent self-test reproduces the
published per-route fleet on all 156 non-backbone routes with **zero mismatches** `[CL-36]`; the 30
e-bus backbone routes are held to their empirical deployment (283 vehicles) and excluded from the
self-test. Physical-alignment GPS corroborates 183 of 186 route geometries (median 94 % of length on
bus-carrying road) `[CL-35]`, while recurring *service* is observed on 66 of 186 `[CL-19]` — a floor on
activity, not a dormancy rate (§6.3).

*Policy: the fleet gap is an expansion problem, not a redistribution one — roughly 400 additional
vehicles concentrated on the busiest retained corridors, not vehicles moved off pruned routes.*

## 5.5 Network length and structural consolidation ⏳ pending `a10_network_diagnostics.py`

Route-km, unique network-km, and the route-km : network-km overlap ratio before and after
rationalisation. **Awaits** `a10`; reports the change in unique network-km against the (near-zero) change
in corridor count established in §5.1. *Policy sentence to be added on module completion.*

## 5.6 Frequent-network coverage ⏳ pending `a11_coverage_accessibility.py`

Share of residents within the walkshed of a route meeting a 15/20/35-minute frequency threshold — the
"frequent transit network," a stronger public metric than any-service coverage. **Awaits** `a11`
(deduplicated network catchments from `a02` intersected with the §4.7 headways).

## 5.7 Buses per capita and the interval fleet ⏳ pending `a09_monte_carlo_sobol.py`

Regression of buses/1000 served on population and density with a prediction interval, and the **fleet
90 % confidence interval** obtained by carrying the GPS-measured 0.51 run-time ratio `[CL-17]` as a
Monte Carlo prior (§4.10). **Awaits** `a09`. This is the subsection §5.3's policy sentence points to.

## 5.8 Tier assignment and class count ⏳ pending `a04_class_count.py`

Jenks GVF across $k = 2$–7 (Eq. 10), the objective elbow (expected $k = 3$), and Cohen's $\kappa$
against equal-interval, quantile, and $k$-means partitions to show the hierarchy is not an artefact of
the classifier. **Awaits** `a04`.

## 5.9 Equity and the losers ⏳ pending `a12_equity_gini.py`

Population-weighted accessibility Gini before/after, and an explicit, named account of which
populations lose access under consolidation (the §5.1 suppressed via-routings made spatial). **Awaits**
`a12`. Reporting the losers is a stated requirement, not an option.

## 5.10 Spatial structure of the uncovered surface ⏳ pending `a11`/`a12`

Moran's $I$ on the residual (uncovered) population surface to test whether gaps are clustered — a
policy-actionable pattern — or dispersed. **Awaits** `a11`/`a12`.

## 5.11 Transfers ⏳ pending `a13_transfers.py`

Distribution of 0 / 1 / 2+ transfer trips on the rationalised trunk–feeder structure and the
break-even transfer penalty at which consolidation stops being worthwhile for the passenger.
**Awaits** `a13`.

## 5.12 Cost, emissions, and cost per unit accessibility ⏳ pending `a14_cost_emissions.py`

Operating-cost and emissions envelope of the 1,011-vehicle fleet `[CL-36]` and cost per unit of
accessibility gained, to compress the efficiency case into one comparable ratio. **Awaits** `a14`.

## 5.13 Scenario stress-test ⏳ pending `a15_scenarios.py`

Five scenarios — do-nothing, efficiency-first, equity-first, balanced (the recommended plan), and
peak-tourist — evaluated on coverage, fleet, and equity so the recommendation is shown to be a
defensible point on an explicit trade-off frontier rather than an assertion. **Awaits** `a15`.

*Policy (network-level, to finalise once §5.5–§5.13 land): the recommended plan is the balanced
scenario; the diagnosis in §5.1–§5.3 shows the honest baseline it improves on and the interval within
which its fleet should be procured.*
