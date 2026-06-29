# Codex prompt: use the post-PR1 20-loop tracker

I uploaded the NeuroDecodeKit starter repo. Please inspect the repo and the roadmap files before making changes.

Read first:
- START_HERE.md
- AGENTS.md
- docs/CODEX_HANDOFF.md
- docs/NEXT_20_LOOPS_TRACKER.md
- docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx if spreadsheet viewing is available

Operating principle:
Work one loop at a time. Each loop should produce a small, testable artifact: a command, cache, report, demo, or decision note. Avoid overengineering. The project is trying to make complex neural-language decoding research accessible through simple repeated loops.

After PR1:
Start with the first non-complete loop in `docs/NEXT_20_LOOPS_TRACKER.md`. For the first post-PR1 run, that is usually Loop 1: PR1 Closeout + Smoke Loop.

For the selected loop:
1. State the loop ID and acceptance gate.
2. Inspect the relevant existing code.
3. Make the smallest code/doc/test changes needed.
4. Do not download real datasets unless explicitly instructed and guarded by dry-run/max-size protections.
5. Run `python -m unittest discover -s tests`.
6. Summarize:
   - what changed
   - tests run
   - commands to try
   - whether the acceptance gate is met
   - what loop should come next

Guardrails:
- Keep `download-selection` dry-run by default.
- Keep heavy dependencies optional.
- Every result needs baseline context.
- Every model result should name the split type.
- No clinical claims.
- No arbitrary mind-reading claims.
