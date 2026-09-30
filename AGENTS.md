# AGENTS.md — instructions for AI coding agents (identical to CLAUDE.md)

1. **Read `MASTER_CONTEXT.md` first.** It is the current briefing (results, layout, open decisions, rules).
2. **Numbers come from `data/derived/` via `paper/CLAIM_LEDGER.md`.** Never type a number into prose that
   no module produced; add a ledger row (next free CL ID) when you add one.
3. **Co-author prose is not yours to edit** (§1, §2, §3 and the verbatim blocks in §7). Raise conflicts as
   `> **[FLAG …]**` callouts and log them in `paper/PENDING_DECISIONS.md`.
4. **Run before you claim.** `analysis/run_all.py --quick` and `pytest tests -q` must pass before a commit
   that changes analysis code. Figures come only from `analysis/fig_generate_all.py`.
5. **Python:** `.venv/Scripts/python.exe` (3.14). Heavy caches are in Git LFS (`git lfs pull`).
6. **Editing section files from scripts:** write the script with a file-writing tool, not a shell heredoc —
   heredocs have corrupted LaTeX backslashes here before (`\rho` became a carriage return). Keep LF endings.
7. **Rules that cannot be relaxed** are in `MASTER_CONTEXT.md` §8 (no fabrication, no "validated against
   ridership", CHALO circularity first, no summed walksheds, raw GPS never committed, barred legacy figures).
8. **Commits** end with a `Co-Authored-By:` line naming the assistant model.
