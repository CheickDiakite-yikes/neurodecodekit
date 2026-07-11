# Prompt to continue NeuroDecodeKit in Codex

Continue NeuroDecodeKit from the current branch. Before editing, inspect the
branch, git status, current tests, optional dependency versions, open pull
requests, and these files:

- `AGENTS.md`
- `README.md`
- `START_HERE.md`
- `CONTRIBUTING.md`
- `docs/CODEX_HANDOFF.md`
- `docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`
- `docs/BYO_NEURODATA_WORKBENCH_SPEC.md`
- `docs/POST_20_ROADMAP.md`
- `docs/OPEN_SOURCE_READINESS.md`

Preserve every existing change and the unrelated tracker inspection NDJSON.
Do not reset, revert, delete, or overwrite work already present.

## Current proof boundary

- Loops 1-12, 14-22, and 23.5 are complete. Loops 13 and 23 are deliberately
  parked after measured gates.
- Real S21 session-1 alignment is validated for all 66 trials. S21 session-2 is
  a consumed evaluation set and must not be used for tuning.
- The cross-session MEG model and the bounded S7 EEG classifier both performed
  worse than their no-signal priors.
- NeuroTokenCache v0, the causal mock stream, the tiny synthetic encoder, the
  parked synthetic CTC decoder, and the synthetic blank-intercept calibration
  are engineering results, not evidence of useful neural decoding.
- RW1 closes metadata-only local intake. RW2 closes bounded, redacted signal
  reading and descriptive reporting on generated fixtures only: 38 readable
  sources pass and two malformed or unsafe layouts refuse exactly.
- No real recording quality, neural advantage, unseen-person generalization,
  useful EEG decoder, real-time decoding, portable-hardware, arbitrary-thought,
  or clinical result has been demonstrated.
- The repository currently reports public while default `main` is stale.
  Review the current branch and draft PR; do not merge or alter visibility
  without explicit user approval.

## Primary task: preregister RW3 only

Create the smallest reviewable preregistration for **RW3 offline replay and
live-source equivalence**. This step freezes the future interface and test
rules; it does not implement a source adapter or read a live stream.

The preregistration must freeze:

1. A strict, versioned source-chunk schema carrying source/modality/device,
   channel order/types/units/geometry availability, source sampling rate,
   sample indices, source timestamps, corrected monotonic timestamps, packet
   sequence, true length, padding mask, and payload dtype/shape.
2. Exact replay, synthetic-source, future BrainFlow playback, and future LSL
   boundaries. BrainFlow and LSL remain optional and uninstalled in this step.
3. Clock domains, timestamp correction, jitter, drift, reordering, duplicate
   packets, gaps, dropped-packet representation, reconnects, and end-of-stream
   behavior. Unknown behavior must remain unavailable rather than inferred.
4. Chunk-schedule invariance, state serialization, causal status, required
   context, flush behavior, and exact tolerances for payload, sample index,
   timestamps, packet accounting, and replay summaries.
5. Strict source/config/registry/payload hashes, collision refusal, split and
   recording binding, privacy redaction, local-only operation, and explicit
   warnings and claim boundaries.
6. Resource caps for source bytes, emitted bytes, item/channel/sample counts,
   runtime, peak RSS, one CPU thread, artifact totals, and zero unauthorized
   network, target, model, training, consumed-cache, or real-data access.
7. Deterministic synthetic fixture families for clean playback, uneven chunk
   schedules, timestamp jitter/drift, packet loss, duplication, reordering,
   reconnect, malformed metadata, cap violation, and tampering.
8. Exact proceed, park, and kill rules. Passing fixtures can prove interface
   and accounting equivalence only; it cannot authorize hardware or support a
   decoding claim.

## Hard boundaries

1. Do not download data, open S20, or reopen consumed S7/S21 raw arrays,
   caches, target logs, or seeds 2203, 2303, and 2353.
2. Do not install or import BrainFlow, LSL, MNE-BIDS, or hardware SDKs. Do not
   connect to hardware, enumerate devices, open sockets, or execute a live
   source.
3. Do not implement RW3 adapters, source chunks, fixtures, or CLI commands in
   this preregistration milestone. Freeze the contract first.
4. Do not train or run a model, create target text or labels, calculate
   CER/WER, or claim decoding performance.
5. Keep heavy dependencies optional. Use one CPU thread and do not create
   generated data artifacts beyond tiny documentation-validation debris.
6. Keep RW3 independent from Loop 24 precision/runtime preregistration and the
   blocked RW4 S20 acquisition packet.

## Required deliverables

1. One detailed RW3 preregistration document with assumptions, schemas,
   fixture matrix, metrics, caps, tolerances, refusal IDs, access counters,
   acceptance gates, and exact claim boundary.
2. A small machine-readable versioned contract or registry only if the repo's
   existing preregistration pattern requires it. It must contain no waveform,
   participant, target, secret, or device-credential data.
3. Tracker, decision log, build notes, handoff, start-here, roadmap, workbook,
   and this continuation prompt updated consistently.
4. Documentation and contract validation, local-link checks, Ruff,
   `git diff --check`, Gitleaks, and the complete unit suites. Compare results
   with the current 258-unittest / 255-pytest baseline.
5. A coherent commit pushed to the current `codex/` branch and an updated
   draft PR. Preserve unrelated files and generated debris outside git.

Do not call RW3 implemented or validated. A successful milestone proves only
that a future replay/live-source equivalence experiment has been frozen before
code or hardware access.
