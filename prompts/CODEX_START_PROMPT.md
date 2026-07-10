# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: preregister post-roadmap Loop 23's synthetic streaming
CTC/prefix-decoder gate, preserving the completed Loop 22 encoder evidence
without reopening its consumed test or any observed real holdout.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_22_TINY_CAUSAL_ENCODER.md`; treat seed-2203 test metrics and checkpoint selection as frozen.
3. Research streaming CTC greedy/prefix decoding, blank/repeat state, hypothesis revisions, and emission-latency definitions from primary sources.
4. Write and commit the full Loop 23 fixture, split, decoder, comparator, access, metric, and resource protocol before generating its test targets.
5. Use a new physically separate synthetic test; never use Loop 22 test rows to select decoder behavior.
6. Require partial-hypothesis traces and separate first, stable, and final emission times plus revision counts.
7. Keep the first decoder language-model-free and compare it with a no-signal prior.
8. Keep real-cache conversion and all observed MEG/EEG holdouts out of this gate.
9. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- Preregistration is committed before any new test target is created or opened.
- CTC blank/repeat semantics and incremental state are explicit and tested on
  nonregistered fixtures only.
- First/stable/final emission and revision metrics are mathematically defined.
- No language model, real data, observed holdout, or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
