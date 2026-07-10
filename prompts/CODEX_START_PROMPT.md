# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: implement post-roadmap Loop 22's tiny learned causal
encoder gate described in `docs/CODEX_HANDOFF.md`, preserving the completed
Loop 21 stream contract without reopening observed real holdouts.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md` and preserve its state, timing, chunk, and claim contracts.
3. Add one optional-Torch causal encoder with a deliberately small parameter and mutable-state budget.
4. Fit on synthetic train rows only, choose stopping/configuration on validation, and run the frozen synthetic test once.
5. Compare against a no-signal prior and report parameters, state, runtime, peak RSS, RTF, and artifacts under explicit caps.
6. Prove learned offline-versus-streaming equivalence across registered chunk schedules before any decoder work.
7. Keep CTC/prefix decoding, language models, adapters, real-cache conversion, and all observed MEG/EEG holdouts out of this gate.
8. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- The learned synthetic validation gate and one frozen test pass are explicit.
- Learned offline/stream replay passes across multiple chunk schedules.
- The audit distinguishes producer causality from decoder causality and does
  not claim measured end-to-end latency.
- No real-data, observed-holdout, decoder, language-model, or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
