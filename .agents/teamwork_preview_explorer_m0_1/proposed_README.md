# Kashmir Bus Route Rationalisation: Paper Companion Repository

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python: 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](requirements.txt)
[![Reproducibility: Seed 20260823](https://img.shields.io/badge/Reproducibility-Seed%2020260823-green.svg)](REPRODUCIBILITY.md)
[![Study Area: Kashmir Division (10 Districts)](https://img.shields.io/badge/Study%20Area-Kashmir%20Division%20(10%20Districts)-orange.svg)](DATA_AVAILABILITY.md)

This repository is the official open-data analysis and reproducibility companion for the research paper:

> **Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity**  
> *Targeting:* Transport Policy  
> *Authors:* Prashant et al. (2026)

---

## 1. Project Purpose & Research Scope

In public transit systems across the Global South, formal demand surveys (household travel surveys, smart-card automated fare collection, and comprehensive origin–destination matrices) are rarely available. Route networks frequently evolve through decades of fragmented commercial permit issuance, resulting in severe corridor duplication, irregular headways, and operational opacity.

This companion repository implements an end-to-end, reproducible open-data framework for evaluating bus route rationalisation, network pedestrian accessibility, operational plausibility, and fleet requirements under severe demand-data scarcity.

### Research Framing & Boundary Conditions

1. **Geographic Scope — Kashmir Division (10 Districts Only):**  
   The study area comprises the entire Kashmir Division of Jammu & Kashmir, India, encompassing exactly 10 districts: **Anantnag, Bandipore, Baramulla, Budgam, Ganderbal, Kulgam, Kupwara, Pulwama, Shopian, and Srinagar** (39 administrative tehsils).  
   *Note on Obsolete Metrics:* Legacy drafts erroneously framed the study area around Srinagar Metropolitan City (SMC), quoting 342 permits, 207 routes, a "39% route reduction", a "95.7% coverage", or a 1,009-bus fleet headline. These metrics are obsolete, empirically refuted, and strictly prohibited across this repository.

2. **Frozen Operational Baseline (v3.4.5):**  
   All analyses evaluate the frozen operational baseline **Kashmir Valley v3.4.5** (`outputs_v3.4.5`):
   - **644 Engine Rows:** 614 permitted vehicle-service rows + 30 Srinagar Smart City Limited (SSCL) electric bus backbone routes.
   - **186 Active Services:** Rationalised network carrying service (156 feeder/retained corridors + 30 e-bus trunk routes).
   - **1,011 Stated Fleet:** Published required vehicle allocation across the 186 active routes.
   - **6,584,762 Population Denominator:** High-resolution WorldPop 2026 UN-adjusted residential count within the dissolved 10-district boundary.

3. **Non-Negotiable Research Contract:**
   - **GPS is not ridership:** Driver smartphone GPS traces (`E:\bus-sathi-trace`) validate the supply-side physical and operational chain (geometry alignment, operating speeds, runtimes, cycle times, and fleet sizing). Passive GPS traces contain no passenger boarding, latent demand, or ridership signal. Never claim ridership validation.
   - **No invented data:** No field boarding enumeration or expert AHP/Delphi panel was collected. Channel V3 is transparently documented as *not performed*.
   - **Disclosed circularity:** Srinagar Smart City Limited (SSCL) / CHALO e-bus ridership was utilized during engine plausibility tuning and is therefore reported strictly as a consistency check (V2), not independent validation. Five GPS-corrected corridors are explicitly treated as *in-sample* for cycle re-anchoring.
   - **Catchment population is not demand:** Route catchment walksheds overlap extensively; network coverage is computed strictly via the deduplicated spatial union, never by summing per-route figures.

---

## 2. Key Methodological & Empirical Findings (F1–F12)

The companion repository reproduces and documents 12 foundational findings that govern the manuscript's findings:

- **F1 — Permit Register vs. Route Register (`q01`):**  
  The 614 permit rows describe only **157 distinct origin–destination corridors** at 11 m endpoint resolution (mean 3.9 permits/corridor; Hazratbal–LD carries 42). The apparent 71.1% route reduction decomposes into **71.0 percentage points change-of-unit** (collapsing duplicate permits) and only **0.2 pp genuine consolidation** (1 corridor). The rationalised design retains **156 of 157 corridors (99.4%)**. However, collapsing suppresses 32 alternative via-routings and merges disparate vehicle classes.
- **F2 — WorldPop 2026 Baseline Discrepancy (`q01`):**  
  The 10-district WorldPop 2026 zonal sum is **6,584,763** (matching engine denominator 6,584,762), whereas the Census 2011 count for the identical districts was **6,888,475** (ratio 0.956, implied −0.30%/year growth vs. historical +2.1%/year). The population surface is conservative; coverage shares are biased slightly upward, and absolute headcount counts downward.
- **F3 — Supply-Side Runtime Understatement (`q01`, `v04`):**  
  Compared to driver GPS traces, uncorrected plan runtimes substantially understate reality: Mean Absolute Percentage Error (MAPE) of OSRM driving vs. observed in-motion runtime is **65.1%**; plan one-way vs. observed is **47.6%** (median plan/observed ratio = **0.51**). Cycle times and fleet requirements must be evaluated with empirical pace priors.
- **F4 — Observational Activity Floor (`q01`):**  
  **66 of 186 routes (35%)** appear in the driver GPS telemetry. The remaining 120 routes represent app adoption limits among informal operators, not proven service dormancy.
- **F5 — Spatial Concentration of Mapped Opportunities (`q01`):**  
  Of 2,431 OpenStreetMap points of interest (POIs), **65% are concentrated within Srinagar district** (0.3 to 120.4 POIs per 100k residents across districts), reflecting volunteered geographic information (VGI) mapping effort.
- **F6 — Road Network Concordance (`q01`):**  
  Mapped OpenStreetMap road density tracks population density across districts at **$\rho = 0.92$**, confirming the pedestrian graph is not peripherally attenuated and validating its use for network walk catchments.
- **F7 — Published Plan Internal Inconsistency (`a02`, `a02b`):**  
  On **44 of 186 routes**, the engine substituted external road distances into `Route_KM` without redrawing geometries or recomputing catchments. On the remaining 142 self-consistent routes, Euclidean catchments reproduce published figures to a median absolute error of **0.245% ($r = 0.995$)**.
- **F8 — The Euclidean Catchment Distortion (`a02`):**  
  Replacing straight-line circular buffers (400 m) with walking distance on an OpenStreetMap pedestrian network graph reduces population served by a **median of 37.4% per route** (IQR 30.5%–41.7%; 184/186 routes overstated by >25%). On the deduplicated network union, coverage drops from **35.5% (2,339,394) to 24.2% (1,592,847)**—an overstatement of **31.9%**.
- **F9 — Embedded Demand Multipliers (`a02b`):**  
  The engine embedded a $1.3\times$ tourist multiplier directly into the population count of 8 routes (285,914 headcount artifact). The companion pipeline strictly decouples resident census counts from visitor demand proxies.
- **F10 — Dominance of the Sanity Cap (`v04`):**  
  **169 of 186 routes (90.9%)** have their cycle times determined strictly by the engine's hard sanity cap per kilometer (100% of Regional, 97.9% of Peri-Urban), rather than the routing model. The cap truncates cycle times below observed operating speeds, mechanistically driving the fleet understatement.
- **F11 — Speed Decomposition & Dwell Model Failure (`v04`):**  
  The OSRM urban congestion multiplier ($2.2\times$) accurately matches observed moving speeds (bias +1.4%), but the engine's fixed stop dwell assumption (1.0 min/km) fails against empirical dwell (observed 1.76 min/km; OLS $R^2 = 0.03$).
- **F12 — Alignment Geometry vs. Service Corroboration (`v04`):**  
  GPS coverage comprises two distinct metrics: `obs_frac` measures physical road-segment coverage (median 0.94 across 183 routes), whereas `observed_cover` measures recurring service presence (66 routes).

---

## 3. Quick Start & Replication

### Prerequisites
- Python 3.14+ (tested on Python 3.14.2 64-bit on Windows and Linux).
- Git.
- C++ build tools for pyosmium (pre-built wheels available for standard platforms).

### Step 1: Clone and Set Up Virtual Environment
```bash
git clone https://github.com/prashant/kash-paper.git
cd kash-paper

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

# Install exact pinned dependencies
pip install -r requirements.txt
```

### Step 2: Quick Reproduction Pipeline (< 3 minutes)
The quick pipeline executes all data quality audits, index weighting alternatives, class count determinations, network diagnostics, sensitivity sweeps, validation matrices, and generates all publication tables and figures using precomputed network catchments:

```bash
python analysis/run_all.py --quick
```

### Step 3: Full End-to-End Pipeline
To recompute the entire pedestrian walk graph and network catchments from scratch (Note: network catchment generation takes ~69 minutes across 22,360 virtual stops):

```bash
python analysis/run_all.py --full
```

### Targeted Execution
Individual stages or modules can be run independently:
```bash
# Run specific milestone stage (0 to 5)
python analysis/run_all.py --stage 2

# Run single analysis module
python analysis/run_all.py --module a03_index_weights
```

For complete step-by-step instructions, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

---

## 4. Repository Layout

```text
E:\kash-paper\
├── README.md               # Project overview, research contract, findings, quick start
├── requirements.txt        # Pinned Python dependencies (Python 3.14.2)
├── .gitignore              # Robust exclusions (caches, binaries, venv, secrets)
├── LICENSE                 # GNU General Public License v3.0 (GPL-3.0)
├── CITATION.cff            # Citation metadata for manuscript and code
├── DATA_AVAILABILITY.md    # Formal data provenance and access statements
├── REPRODUCIBILITY.md      # Comprehensive step-by-step reproduction instructions
│
├── analysis/               # Paper analysis modules
│   ├── common.py           # Shared paths, parameters, CRS, metrics, loaders
│   ├── run_all.py          # Master CLI reproduction runner
│   ├── q01_data_quality.py # Baseline audits and data sanity checks (F1-F6)
│   ├── a01_build_walk_graph.py # OSM pedestrian network extraction
│   ├── a02_network_catchments.py # Graph walking catchments vs Euclidean (F8)
│   ├── a02b_faithfulness.py # Euclidean catchment replication and residuals (F7, F9)
│   ├── a03_index_weights.py # Equal, entropy, and PCA demand weights
│   ├── a04_class_count.py  # Jenks GVF elbow and Cohen's kappa tier stability
│   ├── v04_gps_validation.py # Repaired observational GPS validation (F10-F12)
│   └── fig*.py             # Scripts generating publication Figures 1–8b
│
├── data/
│   ├── raw/                # 19 staged input datasets (read-only)
│   ├── cache/              # Heavy precomputed caches (excluded from git)
│   │   ├── walk_graph.gpickle      # NetworkX pedestrian graph (77 MB)
│   │   ├── catchments_network.gpkg # Route catchment polygons (69 min compute)
│   │   └── osrm_responses.json     # Frozen OSRM route queries
│   ├── derived/            # Canonical CSV and JSON output tables
│   └── MANIFEST.md         # Cryptographic checksums (SHA-256) and source metadata
│
├── paper/
│   ├── CLAIM_LEDGER.md     # Single source of truth for all quantitative claims
│   ├── FINDINGS.md         # Authoritative numerical results and findings
│   ├── tables/             # Publication Tables 1–8 in CSV and Markdown
│   ├── figures/            # Vector and high-resolution publication figures
│   └── draft/              # Manuscript text drafts (§4, §5, §6, §8, Abstract)
│
└── logs/
    └── WORK_REGISTER.md    # Multi-worker lock file preventing concurrency races
```

---

## 5. License & Citation

- **Code & Repository:** Licensed under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE).
- **Data & Metadata:** Staged datasets are governed by their respective upstream licenses as detailed in [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md).
- **Citation:** Please cite the paper companion as specified in [CITATION.cff](CITATION.cff).
