# Task Assignment — Explorer (Milestone M0, Subtask 2)

## Role
Explorer (Milestone M0 — Runner Architecture `analysis/run_all.py`)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_explorer_m0_2

## Objective
Investigate and design the complete technical architecture and implementation specification for `analysis/run_all.py`:
1. `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST).
2. `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Design complete specification for `analysis/run_all.py`:
   - CLI flags: `--stage` (e.g., 0, 1, 2, 3, 4, 5), `--module` (run single script by name), `--quick` (skip heavy cache generation `a01`, `a02` and run lightweight/analysis scripts), `--full` (full pipeline run).
   - Execution ordering and dependency resolution across modules.
   - Logging of stdout/stderr and execution timestamps to `logs/<module>.log`.
   - Explicit guard: MUST NOT call the engine or redownload/overwrite raw data or heavy caches if already present.
   - Pass/fail reporting with runtime tracking and summary table.

## Scope & Boundaries
- Read-only exploration and design. DO NOT edit or create production code/data files.
- Write handoff report to: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_2\handoff.md`.
- Send completion message via `send_message` when done.

## 2026-09-03T11:18:27Z
You are Explorer (Milestone M0, Subtask 2 — Runner Architecture analysis/run_all.py) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_explorer_m0_2
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_explorer_m0_2\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Investigate and design the complete technical architecture and implementation specification for analysis/run_all.py:
- CLI flags: --stage, --module, --quick, --full without calling the engine or downloading data.
- Execution ordering and dependency resolution across all modules.
- Logging of stdout/stderr and timestamps to logs/<module>.log.
- Pass/fail reporting with runtime tracking and summary table.

Maintain progress.md with 'Last visited' timestamps.
Write handoff report to: E:\kash-paper\.agents\teamwork_preview_explorer_m0_2\handoff.md.
Send a completion message via send_message when done.
