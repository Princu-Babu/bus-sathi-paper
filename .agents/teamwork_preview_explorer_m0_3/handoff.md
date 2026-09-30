# Handoff Report — Explorer M0-3: Manifest & Claim Ledger Architecture

**Agent**: Explorer (Milestone M0, Subtask 3 — Manifest & Claim Ledger Architecture)  
**Working Directory**: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_3`  
**Handoff Type**: Hard (Task Complete)  
**Target Files Designed**:
- `data/MANIFEST.md` (Implementation candidate: `.agents/teamwork_preview_explorer_m0_3/proposed_MANIFEST.md`)
- `paper/CLAIM_LEDGER.md` (Implementation candidate: `.agents/teamwork_preview_explorer_m0_3/proposed_CLAIM_LEDGER.md`)

---

## 1. Observation

### 1.1 Primary Input Files and Hashes
1. `data/MANIFEST.json` contains metadata for 19 raw files plus OSRM cache.
2. Running filesystem verification on `data/raw/` confirmed 20 files (19 from `MANIFEST.json` + `census2011_kashmir_districts.csv`):
   - `census2011_kashmir_districts.csv`: 951 B, SHA-256 `d7c94f326e7cd9abd42e82b2c1d51814d76d708162b57aceda9ddf82b65bd559`.
   - `chalo_deployed_buses.csv`: 1,683 B, SHA-256 `ee6b45ff3e2c32c36ab1fcd9b658870f6b7a1d44bb6836e635f0dee4930cf38d`.
   - `chalo_ridership.csv`: 15,626 B, SHA-256 `c216de2d5f13b120572c0fcaa8fd524db2d2b9e687761c44fa6ee2f3f68164ff`.
   - `existing-routes.csv`: 66,972 B, SHA-256 `fa9778c8267d71b68ccffc1024ae77cd0cef3d0d86eb1ae0c0b3d1984da39047`.
   - `Hourly_Passenger_Count.csv`: 12,952 B, SHA-256 `289381eddd272fdab98bfabb4db165dd2b7b77b01e5310ac7c668d6b2cc5a0b1`.
   - `kashmir_districts_osm.geojson`: 444,515 B, SHA-256 `4091fe7bdc0e3490eab3f3505fe1f98a9beb288c1bf97b38170f84667ecdc444`.
   - `Kashmir_Stops_Master_v4.csv`: 9,847 B, SHA-256 `dcfce2a9b8a1cf6610fdd76809cd5eb07d24fd2d352edc120bd58d911e5d2d14`.
   - `kashmir_tehsils_osm.geojson`: 605,242 B, SHA-256 `38e0a2e3d88a0c8de86c7e65451b6839b0d0903a9156c4710d7a2017fe04e549`.
   - `kashmir_worldpop.tif`: 4,760,992 B, SHA-256 `515e5867ee4c0fe9dd031a3fc0f372814aa96bf3c689d9e25bf09ba19bda6571`.
   - `pois.csv`: 223,453 B, SHA-256 `e8f217c4ad77986e3e00a91dbb02fcfbca918eb499d695050982d357fed19f73`.
   - `Rationalisation_Log_Kashmir_v3.csv`: 242,957 B, SHA-256 `00f1052206dc29b004df5bf18c2a1a80f6d67fcab2e66a2b311686b082b4be4c`.
   - `Rationalised_Routes_Kashmir_v3.csv`: 247,953 B, SHA-256 `1871714c8804cbbc152b0209774c772943c939e71bde4241632690ce0f02172a`.
   - `Rationalised_Routes_Kashmir_v3.geojson`: 2,977,639 B, SHA-256 `4ea6a856dd77d5d43a587fbdc445c76feea0b123b2bcc85040e8505a1497f945`.
   - `ROUTE_DEEPDIVE_LEDGER.csv`: 167,738 B, SHA-256 `1788e1ce417d46ad124a9d85e30952faa7de810aa47c34615dcbae94ff159f34`.
   - `gps/corridor_profiles.csv`: 1,288 B, SHA-256 `0cb17ce98d6b166d049d6aa19d520d9fe7850f644bea87af7545a43c7b9d1c44`.
   - `gps/driver_days.csv`: 51,564 B, SHA-256 `14b408639648b8ffc128322d6a05f44b1faf46a0b65ebf8d7e986df667e4b9a9`.
   - `gps/geometry_divergence.csv`: 553 B, SHA-256 `7bf5c49479a6e639d3356a3c136e0e38519e05d6a6c10b182f886b13fdcfc485`.
   - `gps/permit_observed.csv`: 12,402 B, SHA-256 `f97f1bacf5bf03fce1f7d9e816fb161ad681c0e08d6e99ac2ee8805eca8839b8`.
   - `gps/reality_check.csv`: 2,943 B, SHA-256 `55172547baaae97dd2f6e331a36ed52b3a44f065311ec22aac0fcd67b955ba43`.
   - `gps/route_evidence.csv`: 12,563 B, SHA-256 `061ea4e5b550dbaeb50a7f123f52cf3024a268c1d8fc0c8ad899dee9b7998f75`.
3. Inspection of `data/cache/` revealed three heavy precomputed artifacts:
   - `catchments_network.gpkg`: 18,522,112 B, SHA-256 `6ecaa5529abc7e41af37e5973bd670c186ea9f6234d8c2741d934a741410a9eb`.
   - `osrm_responses.json`: 2,825,043 B, SHA-256 `c7f82ddb1d83127dfd23c24b640515eb8c63f39b095a4812eb84598033eadbb6`.
   - `walk_graph.gpickle`: 77,051,716 B, SHA-256 `315a345e0c77f299f59f5fb2614df6ce0bc5f75dc1138ed54d62b125d53e2f7b`.
4. Inspection of `paper/FINDINGS.md`, `STATUS.md` §2.3, and derived files (`q01_data_quality.json`, `a02_network_catchments.json`, `a02b_faithfulness.json`, `v04_gps_validation.json`) confirmed the mathematical parameters of findings F1–F12:
   - F1: 614 permit rows → 157 corridors (11m). 644 engine rows → 186 active routes (458 merged: 457 unit change + 1 spatial consolidation). Retention: 156/157 (99.4%). Suppressed diversity: 32 via routings across 20 corridors.
   - F2: WorldPop 2026 total = 6,584,763 (active denom: 6,584,762). Census 2011 = 6,888,475. Ratio = 0.956. Implied CAGR = −0.30%/yr. 8/10 districts outside [0.5%, 3.0%] CAGR band.
   - F3: OSRM vs observed in-motion MAPE = 65.1% (RMSE 28.00 min). Plan vs observed one-way MAPE = 47.6%. Median ratio = 0.513 (5 matched corridors).
   - F4: 43,809 GPS runs. 66 of 186 routes observed in GPS (35.5% activity floor).
   - F5: 2,431 POIs (1,030 Tier 1, 1,080 Tier 2, 321 Tier 3). 65.3% in Srinagar (density range 0.32 to 120.44 per 100k).
   - F6: 18,533 km walkable road network in 10 districts. Spearman rho(pop density, road density) = 0.915 (p = 0.0002).
   - F7: 142 consistent routes (error <= 1%), 44 substituted distance routes. Faithfulness on 142 routes: median error 0.245%, r = 0.995.
   - F8: Euclidean catchment overstatement: median 37.4% per route (IQR 30.5%–41.7%, 184/186 > 25%). Deduplicated union overstatement: 31.9% (2,339,394 → 1,592,847). Coverage revision: 35.5% → 24.2%. Tau sensitivity: 52.8% (50m), 37.4% (100m), 29.2% (150m). Off-network stops: 46/22,360 (0.21%, median offset 11.0m).
   - F9: Embedded tourist multiplier 1.30× injects 285,914 synthetic headcount across 8 tourist routes.
   - F10: Operational per-km cycle cap binds on 169 of 186 active routes (90.9%): Regional 71/71 (100%), Peri_Urban 46/47 (97.9%), Urban 52/68 (76.5%). Observed median pace is 4.62 min/km (83.3% Urban, 88.9% Peri_Urban, 100% Regional exceed cap).
   - F11: Congestion multiplier City Core 2.20 reproduces observed moving speed at +1.4% bias (17.95 vs 20.55 km/h). Dwell model fails: observed 1.76 min/km vs 1.0; OLS dwell intercept 17.67 min (p < 0.05, R² = 0.03).
   - F12: Physical road alignment coverage (`obs_frac`) median 94.0% (183/186 > 0) vs service status corroboration 35.5% (66/186).
   - Baseline fleet: 1,011 buses (187 HPV, 754 MPV, 70 LPV; +68.5% over 600 baseline; 43 buses/lakh; 0 mismatches on formula self-test across 156 non-SSCL routes).

---

## 2. Logic Chain

1. **Premise 1 (Data Integrity)**: Transparent reproducibility requires complete cryptographic and provenance accounting for all staged data assets. Cataloging all 20 raw files (including the Census 2011 file omitted from `MANIFEST.json`) with their exact SHA-256 hashes, byte sizes, licensing, and upstream locations guarantees that any downstream modification or corruption is immediately detected.
2. **Premise 2 (Cache Hygiene)**: Committing large precomputed binary graphs and spatial vectors violates git repository best practices, inflates repository size (>98 MB), and risks non-deterministic diffs. Documenting the exact regeneration procedures for `data/cache/` while enforcing `.gitignore` exclusions protects repository hygiene while maintaining full reproducibility.
3. **Premise 3 (Traceable Claims)**: In academic publication, reviewer scrutiny targets unsubstantiated numerical discrepancies. Establishing a unique Claim ID ledger (`CL-01` through `CL-36`) that maps every quantitative finding (F1–F12) to exact formulas, denominators, data tables, and manuscript locations creates an unbreakable chain of evidence.
4. **Premise 4 (Elimination of Legacy Errors)**: Prohibiting obsolete metrics (342 permits, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet, SMC framing, and "validated against ridership") via an explicit negative register ensures that no superseded numbers contaminate the publication drafts.

---

## 3. Caveats

1. **Read-Only Explorer Boundary**: In accordance with the Explorer persona and dispatch instructions ("*DO NOT edit or create production code/data files*"), the production targets `data/MANIFEST.md` and `paper/CLAIM_LEDGER.md` were authored as proposed specification files (`proposed_MANIFEST.md` and `proposed_CLAIM_LEDGER.md`) within the agent's assigned directory. The implementer can copy them directly to their target production paths.
2. **Proprietary Operator Data Terms**: While the 13 engine files, OSM vector files, and census benchmarks are open or academic research assets, SSCL/Chalo ticketing records (`Hourly_Passenger_Count.csv`, `chalo_ridership.csv`, `chalo_deployed_buses.csv`) and Bus Sathi GPS traces are shared under confidential research agreements. This distinction is explicitly documented in the manifest.
3. **V3 Survey Absence**: No field enumeration or Delphi/AHP panel survey was conducted; this is cataloged in the ledger and must be documented as "not performed" rather than omitted.

---

## 4. Conclusion

1. The data manifest specification is complete, covering all 20 raw staged files, 3 heavy precomputed cache files, and multi-platform integrity verification commands.
2. The claim ledger architecture is complete, encompassing 36 distinct Claim IDs (`CL-01` to `CL-36`) covering findings F1 through F12, parameter ranges, prohibited legacy terms, and multi-channel validation (V1–V6).
3. The proposed files are written and verified at:
   - `E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_MANIFEST.md`
   - `E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_CLAIM_LEDGER.md`

---

## 5. Verification Method

### 5.1 Verification Commands
To verify the integrity and completeness of the proposed files:

1. **Verify Raw Data Hashes against Manifest**:
   ```powershell
   Get-ChildItem -Path E:\kash-paper\data\raw -Recurse -File | ForEach-Object {
       [PSCustomObject]@{
           Path = $_.FullName.Replace('E:\kash-paper\data\raw\','');
           Bytes = $_.Length;
           SHA256 = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower()
       }
   } | Format-Table -AutoSize
   ```
2. **Verify Proposed Artifacts Exist in Agent Directory**:
   ```powershell
   Test-Path E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_MANIFEST.md
   Test-Path E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_CLAIM_LEDGER.md
   ```
3. **Verify Claim Count**:
   ```powershell
   (Select-String -Path E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_CLAIM_LEDGER.md -Pattern "### \[CL-").Count
   # Expected output: 36
   ```

### 5.2 Deployment Instructions for Implementer
The implementer can deploy these verified artifacts to production with:
```powershell
Copy-Item E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_MANIFEST.md E:\kash-paper\data\MANIFEST.md
Copy-Item E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_CLAIM_LEDGER.md E:\kash-paper\paper\CLAIM_LEDGER.md
```
