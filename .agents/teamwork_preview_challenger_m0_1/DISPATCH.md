# Task Assignment — Challenger 1 (Milestone M0)

## Role
Challenger 1 (Milestone M0 — Adversarial Verification & Stress Testing)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_challenger_m0_1

## Objective
Empirically stress-test and challenge Milestone M0 deliverables:
- Empirically verify `analysis/run_all.py` against edge cases, invalid flags, missing arguments, interrupt handling, and execution modes.
- Verify that `analysis/run_all.py` NEVER calls external engine or overwrites heavy caches (`walk_graph.gpickle`, `catchments_network.gpkg`).
- Write and run adversarial checks for regex leaks of forbidden legacy metrics (`342`, `207`, `39%`, `95.7%`, `1,009`, SMC framing) across all repository text and markdown files.

## Required Actions
1. Read `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` first.
2. Read `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Write and execute stress tests in Python or shell using `E:\kash-paper\.venv\Scripts\python.exe`.
4. Issue a clear verdict: `APPROVE` or `REQUEST_CHANGES` in `handoff.md`.
5. Send completion message via `send_message`.

## 2026-09-03T11:32:21Z

You are Challenger 1 for Milestone M0 (Baseline Setup, Manifests, and Claim Ledger) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_challenger_m0_1
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_challenger_m0_1\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Empirically stress-test and challenge Milestone M0 deliverables:
- Empirically verify analysis/run_all.py against edge cases, invalid flags, missing arguments, interrupt handling, and execution modes.
- Verify that analysis/run_all.py NEVER calls external engine or overwrites heavy caches (walk_graph.gpickle, catchments_network.gpkg).
- Write and run adversarial checks for regex leaks of forbidden legacy metrics (342, 207, 39%, 95.7%, 1009, SMC framing) across all repository text and markdown files.

Maintain progress.md with 'Last visited' timestamps.
Deliver handoff.md with a clear verdict: APPROVE or REQUEST_CHANGES.
Send completion message via send_message when done.
