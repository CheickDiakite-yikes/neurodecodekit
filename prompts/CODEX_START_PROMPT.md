# Prompt to continue NeuroDecodeKit in Codex

You are continuing the NeuroDecodeKit starter repo. Read `AGENTS.md`, `docs/CODEX_HANDOFF.md`, and `README.md` first.

Goal for this session: begin the post-20-loop causal chunk/replay gate described
in `docs/CODEX_HANDOFF.md`, building on `NeuroTokenCache v0` without reopening
observed real holdouts.

Concretely:

1. Run `python -m unittest discover -s tests` and inspect current state.
2. Read `docs/LOOP_20_NEUROTOKEN_CACHE_V0.md` and preserve its schema and claim boundaries.
3. Define fixed synthetic stream chunks, bounded state, right context, and flush behavior.
4. Test offline-versus-streaming equivalence where the contract promises it, including irregular and final partial chunks.
5. Report producer latency, state bytes, runtime, peak RSS, and output bytes under explicit caps.
6. Keep learned encoders, causal decoders, adapters, real-cache conversion, and all observed MEG/EEG holdouts out of this gate.
7. Do not download data; preserve dry-run and explicit-execution acquisition defaults.

Acceptance:

- Tests pass.
- CLI help works.
- Synthetic chunk/replay tests pass across multiple chunk schedules.
- The audit distinguishes producer causality from decoder causality and does
  not claim measured end-to-end latency.
- No model, training, real-data, holdout, or network access occurs.

The product principle is: `manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo`.
