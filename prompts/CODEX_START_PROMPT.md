# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: implement PR 1 from `docs/CODEX_HANDOFF.md`: real event/window extraction for one selected SpanishBCBL block.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Add an `extract-windows` CLI command that takes one `.fif` file and one `.mat` log file and writes a small `.npz` cache.
3. Use optional imports for MNE/SciPy/NumPy only inside the extraction path.
4. Report output shape, sampling rate, number of events kept/dropped, and output file size.
5. Add unit tests for event/window edge cases using synthetic arrays; avoid requiring real data in CI.
6. Do not download the full SpanishBCBL dataset.
7. Keep `download-selection` dry-run by default; only `--execute` should fetch files.

Acceptance:

- Tests pass.
- CLI help works.
- Synthetic window extraction works.
- Real extraction code has graceful dependency errors when MNE/SciPy are missing.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
