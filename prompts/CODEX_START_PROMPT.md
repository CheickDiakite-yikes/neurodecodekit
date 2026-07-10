# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: preregister the narrow post-roadmap Loop 23.5 synthetic
blank/boundary calibration gate after Loop 23's frozen exact-sequence failure.
Do not implement it or generate another fixture until the protocol is reviewed,
committed, and pushed.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_23_PREREGISTRATION.md` and `docs/LOOP_23_STREAMING_CTC_DECODER.md`; treat seed 2303 as consumed.
3. Explain why stable, low-CER output still failed exactness: every error is a correct target plus one false tail symbol, and prefix equals greedy.
4. Review primary literature for CTC blank calibration, confidence calibration, endpoint-independent emission suppression, and streaming latency/stability.
5. Preregister one target-independent blank-score calibration family and one validation-only selection rule; do not choose from seed-2303 behavior.
6. Require fresh physical train/validation/test splits and freeze their seeds, caps, hashes, and one-time access order before generation.
7. Keep the unmodified Loop 23 greedy/prefix decoder as the main comparator, plus train-only prior and zero-signal controls.
8. Forbid target-length trimming, endpoint knowledge, language models, lexicons, larger encoders, CTC retraining, and real data in this gate.
9. Commit and push the preregistration before writing implementation code or creating target arrays.
10. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- The new preregistration exists before any fresh target, calibration code, or
  test partition.
- Seeds 2203 and 2303 remain unopened and unreferenced by executable selection.
- Calibration, correctness, stability, and endpointing are separate metrics.
- No language model, larger model, precision sweep, real data, observed holdout,
  or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
