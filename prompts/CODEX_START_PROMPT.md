# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: implement the preregistered post-roadmap Loop 23
synthetic streaming CTC/prefix-decoder gate, preserving the completed Loop 22
encoder evidence without reopening its consumed test or any observed real
holdout.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_22_TINY_CAUSAL_ENCODER.md`; treat seed-2203 test metrics and checkpoint selection as frozen.
3. Read `docs/LOOP_23_PREREGISTRATION.md` and do not change its registered beam, fixture, metric, access, or cap values.
4. Implement blank/repeat collapse and prefix probabilities with hand-built tests and exhaustive tiny-path enumeration.
5. Build fixture/decoder/gate code and rehearse only with alternate seeds; do not create seed-2303 yet.
6. Prove frame-indexed partial traces and final outputs across all five transport schedules.
7. Record first-correct, stable-correct, finalization, revisions, edit overhead, state, runtime, RSS, and controls.
8. Commit and push passing mechanics before generating the registered fixture and opening its fresh test once.
9. Keep language models, real-cache conversion, and all observed MEG/EEG holdouts out of this gate.
10. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- The preregistered protocol remains unchanged and seed-2303 stays absent
  until alternate-seed mechanics are committed.
- CTC blank/repeat semantics and incremental state are explicit and tested on
  nonregistered fixtures only.
- First/stable/final emission and revision metrics are mathematically defined.
- No language model, real data, observed holdout, or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
