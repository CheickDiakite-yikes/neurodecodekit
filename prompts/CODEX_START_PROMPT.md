# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: implement the already-preregistered post-roadmap Loop
23.5 synthetic blank-intercept calibration gate after Loop 23's frozen
exact-sequence failure. Use alternate seeds only until mechanics are committed
and pushed.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_23_PREREGISTRATION.md` and `docs/LOOP_23_STREAMING_CTC_DECODER.md`; treat seed 2303 as consumed.
3. Read `docs/LOOP_23_5_PREREGISTRATION.md` and preserve every fit, split, metric, access, threshold, and cap value exactly.
4. Implement the 80-iteration float64 bisection fit and validate it against analytic examples plus an independent dense-grid oracle.
5. Add a train frame-only access mode that never indexes targets and a separate target-only prior access that never indexes signals.
6. Apply the single fitted intercept only to the blank logit; leave all symbol logits and CTC state unchanged.
7. Compare calibrated/unmodified greedy and prefix decoders, both zero-signal variants, and the train-only sequence prior.
8. Rehearse all five schedules with alternate seeds 9351/9352/9353; do not create seed 2353.
9. Commit and push passing alternate mechanics before creating the registered fixture and opening its test once conditionally.
10. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- Tests, strict access tracking, hashes, CLI help, and caps pass on alternate
  fixtures.
- Registered seed 2353 remains absent until mechanics are committed and pushed.
- Seeds 2203 and 2303 remain unopened and unreferenced by executable selection.
- Calibration, correctness, stability, and endpointing remain separate metrics.
- No language model, larger model, precision sweep, real data, observed holdout,
  or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
