# Task Assignment — Explorer (Survey 2)

## Role
Explorer (Survey 2) — Codebase & Script Infrastructure

## Working Directory
E:\kash-paper\.agents\teamwork_preview_explorer_survey_2

## Objective
Thoroughly explore and document the codebase, execution environment, and script architecture in `E:\kash-paper`:
- Read `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` (MANDATORY).
- Inspect all files in `analysis/` (`common.py`, `a00_stage_inputs.py`, `q01_data_quality.py`, `a01_build_walk_graph.py`, `a02_network_catchments.py`, `a02b_faithfulness.py`, `a03_index_weights.py`, `v04_gps_validation.py`, etc.).
- Inspect the Python environment at `E:\kash-paper\.venv`.
- Inspect existing logs, tests, and utility functions in `common.py`.
- Identify what scripts are already written, what needs to be rewritten (especially `v04_gps_validation.py`), and what scripts are yet to be written.

## Scope & Boundaries
- Read-only investigation.
- DO NOT edit or create any source code or data files.
- Compile your analysis in `E:\kash-paper\.agents\teamwork_preview_explorer_survey_2\handoff.md`.

## Deliverables in handoff.md
1. Code architecture summary: `common.py` parameters, paths, helpers.
2. Status and inventory of every script in `analysis/` (written/tested, written/untested, superseded, missing).
3. Exact code structure and bug/flaw analysis of `v04_gps_validation.py` per STATUS.md requirements.
4. Environment and runner details (`.venv`, run commands, dependency inventory).

## 2026-09-03T11:11:13Z
You are Explorer (Survey 2) — Codebase & Script Infrastructure for the Kashmir paper companion project E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_explorer_survey_2
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_explorer_survey_2\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Explore and document the codebase, execution environment, and script architecture in E:\kash-paper:
- Read E:\kash-paper\.agents\ORIGINAL_REQUEST.md first.
- Inspect all files in analysis/ (common.py, a00_stage_inputs.py, q01_data_quality.py, a01_build_walk_graph.py, a02_network_catchments.py, a02b_faithfulness.py, a03_index_weights.py, v04_gps_validation.py, etc.).
- Inspect the Python environment at E:\kash-paper\.venv.
- Identify existing functions in common.py, status of all analysis scripts (written/unwritten/superseded), and the exact technical defects of current v04_gps_validation.py as noted in STATUS.md and IMPLEMENTATION_AND_QA_PLAN.md.

Hard constraints:
- Read-only investigation. NEVER write or edit code or data files.
- Maintain your progress.md in your working directory with 'Last visited' timestamps.
- Write your comprehensive report to: E:\kash-paper\.agents\teamwork_preview_explorer_survey_2\handoff.md.
- Follow the Handoff Protocol: Observation, Logic Chain, Caveats, Conclusion, Verification Method.
- Send a completion message via send_message to orchestrator when done.
