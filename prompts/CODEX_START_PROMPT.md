# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: preregister post-roadmap Loop 24 as a bounded local
precision/runtime comparison against the frozen Loop 23.5 synthetic reference.
Do not implement or benchmark a precision candidate before the protocol is
committed and pushed.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_23_STREAMING_CTC_DECODER.md`; treat seed 2303 as consumed.
3. Read `docs/LOOP_23_5_PREREGISTRATION.md` and `docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`; treat seed 2353 as consumed.
4. Define what numeric paths are actually executable on this CPU; distinguish float storage, float arithmetic, dynamic quantization, and true integer execution.
5. Freeze reference outputs, candidates, tolerances, comparison splits, failure rules, measurements, thread settings, and artifact caps.
6. Keep precision selection on a fresh synthetic calibration/validation split; do not use seeds 2203, 2303, or 2353.
7. Preserve calibrated/unmodified decoders, signal-free controls, exact sequence metrics, and five-schedule replay where applicable.
8. Require correctness preservation before any speed or size comparison can proceed.
9. Commit and push the preregistration before writing candidate code or creating fresh evaluation targets.
10. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- The preregistration is complete enough that no tolerance, candidate, split,
  or winner rule can be chosen after seeing evaluation output.
- Seeds 2203, 2303, and 2353 remain unopened and unreferenced by executable
  selection.
- Calibration, correctness, stability, and endpointing remain separate metrics.
- No language model, larger model, candidate benchmark, real data, observed
  holdout, or network access occurs during preregistration.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
