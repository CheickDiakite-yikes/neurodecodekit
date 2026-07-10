# Prompt to continue NeuroDecodeKit in Codex

Continue NeuroDecodeKit from the current branch. Read `AGENTS.md`,
`START_HERE.md`, `docs/CODEX_HANDOFF.md`,
`docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md`, and
`docs/BYO_NEURODATA_WORKBENCH_SPEC.md` before editing.

Primary task: complete Real-World Practice Track RW1 as the smallest strict
metadata-only local intake slice.

Requirements:

1. Preserve all existing work and the unrelated tracker inspection NDJSON.
2. Do not open consumed S7/S21 raw arrays or caches, and do not use seeds 2203,
   2303, or 2353.
3. Do not download anything. The S20 packet remains unapproved.
4. Add a dependency-free level-0 scanner for BrainVision, EDF/EDF+, BDF,
   EEGLAB, FIF, and BIDS synthetic fixtures.
5. Validate resolved paths, symlink escape, duplicate roles, required
   companions, archive/pickle refusal, file/depth/input/text/output caps, and
   collision behavior.
6. Read only bounded text headers/sidecars. Do not read binary signal samples,
   labels, or target text, and do not import MNE in the metadata path.
7. Emit deterministic versioned JSON and Markdown with compatibility level,
   known/unavailable metadata, warnings/refusals, source and registry hashes,
   runtime, RSS, declared/read/output bytes, and raw/cache/model/training/network
   counters.
8. Add useful create/inspect CLI help and tests for every refusal boundary.
9. Keep one CPU thread and generated artifacts below 4 MiB for the roundtrip.
10. Run focused tests, the complete unit and pytest suites, Ruff, compileall,
    CLI help, `git diff --check`, and one synthetic roundtrip.
11. Compare against the recorded pre-change baseline of 238 unittest tests
    with 3 skips.
12. Commit and push only after all gates pass. Never commit generated reports,
    raw data, caches, secrets, or inspection debris.

RW1 adds no waveform, PSD, signal-quality, MNE read, live-device, GUI,
predictive, CER/WER, or decoding capability. Unknown or incompatible input must
produce an inspection/refusal report, never fake text.
