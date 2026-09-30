# Task Assignment — Explorer (Milestone M0, Subtask 1)

## Role
Explorer (Milestone M0 — Repository Hygiene & Configuration)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_explorer_m0_1

## Objective
Investigate and design complete specifications and contents for the paper companion repository hygiene files:
1. `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST).
2. `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Design detailed specifications for:
   - `README.md`: project purpose, research framing (Kashmir Division 10 districts, Transport Policy target), key findings summary (F1-F12), instructions for replication using python virtual environment.
   - `requirements.txt`: complete pinned dependency list (incorporating geopandas, rasterio, shapely, scikit-learn, jenkspy, statsmodels, networkx, salib, esda, libpysal, matplotlib, pyosmium, numpy, pandas, scipy, rasterstats, etc.).
   - `.gitignore`: robust exclusion rules ensuring `data/cache/` (specifically `walk_graph.gpickle`, `catchments_network.gpkg`, `kashmir_worldpop.tif`), temporary python files, IDE artifacts, and `.env` are never committed.
   - `LICENSE`: GPL-3.0 license text matching the engine repository.
   - `CITATION.cff`: formal citation file for the paper and companion repository.
   - `DATA_AVAILABILITY.md`: formal data availability statement covering OSM, WorldPop, permit register, and CHALO provenance.
   - `REPRODUCIBILITY.md`: step-by-step reproducibility guide from `.venv` activation to running quick/full pipelines.
   - `logs/WORK_REGISTER.md`: initial work register format with active lock mechanism.

## Scope & Boundaries
- Read-only exploration and design. DO NOT edit or create production code/data files.
- Write handoff report to: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_1\handoff.md`.
- Send completion message via `send_message` when done.

## 2026-09-03T11:18:27Z
You are Explorer (Milestone M0, Subtask 1 — Repository Hygiene & Configuration) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_explorer_m0_1
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_explorer_m0_1\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Investigate and design complete specifications and contents for the paper companion repository hygiene files:
- README.md (project purpose, research framing: Kashmir Division 10 districts, Transport Policy target, key findings F1-F12, replication instructions).
- requirements.txt (complete pinned dependency list).
- .gitignore (ensuring data/cache/ heavy files, .env, temporary files are excluded).
- LICENSE (GPL-3.0 matching engine repo).
- CITATION.cff (citation metadata).
- DATA_AVAILABILITY.md (provenance of OSM, WorldPop, permit register, CHALO).
- REPRODUCIBILITY.md (step-by-step reproduction instructions).
- logs/WORK_REGISTER.md (work register schema and initial entries).

Maintain progress.md with 'Last visited' timestamps.
Write handoff report to: E:\kash-paper\.agents\teamwork_preview_explorer_m0_1\handoff.md.
Send a completion message via send_message when done.

