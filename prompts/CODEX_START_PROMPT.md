# Prompt to continue NeuroDecodeKit in Codex

Continue NeuroDecodeKit from the current branch. Before editing, inspect the
branch, git status, current tests, optional dependency versions, and these
files:

- `AGENTS.md`
- `START_HERE.md`
- `docs/CODEX_HANDOFF.md`
- `docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`
- `docs/RW2_PRIMARY_SOURCE_RESEARCH.md`
- `docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`
- `registries/signal_quality_contract.v0.json`
- `docs/BYO_NEURODATA_WORKBENCH_SPEC.md`
- `docs/POST_20_ROADMAP.md`

Primary task: implement the preregistered Real-World Practice Track RW2 as the
smallest optional-neuro, synthetic-fixture-only bounded signal-read and
descriptive quality-report gate. The frozen registration is commit `eacb231`.
Do not expand or reinterpret its contract.

Hard boundaries:

1. Preserve all existing work and the unrelated tracker inspection NDJSON.
2. Do not download data or open S20. Do not open consumed S7/S21 raw arrays,
   caches, target logs, or seeds 2203, 2303, and 2353.
3. Use only deterministic generated fixtures. Do not create labels, target
   text, predictions, CER/WER, a decoder, a model, or a training run.
4. Keep MNE, NumPy, and SciPy optional and lazily imported. The base package
   must remain dependency-free and missing extras must produce actionable
   errors. Do not add MNE-BIDS or another heavy base dependency.
5. Use one CPU worker/thread. Keep the complete generated fixture/report set
   below 16 MiB and each run below its 4-MiB artifact cap.

Implementation contract:

1. Extend the RW1 source binding instead of bypassing it. Bind every report to
   the exact RW1 source manifest, registries, configuration, and hashes.
2. Add explicit adapters for BrainVision, EDF/EDF+, BDF, EEGLAB continuous
   external-FDT, FIF, and BIDS using the exact named readers and arguments in
   `registries/signal_quality_contract.v0.json`.
3. Do not call `mne_bids.read_raw_bids`. Resolve BIDS with RW1, then dispatch
   to the direct MNE reader. Refuse ambiguous sidecars or unauthorized event
   content exactly as registered.
4. Refuse embedded/epoched/ALLEEG/old-DAT EEGLAB before signal materialization.
   Refuse EDF/BDF level 2 unless one source sampling rate is proven.
5. Keep `preload=False`; select at most three deterministic windows at 5%, 50%,
   and 95%; enforce 512 channels, 4,194,304 channel-sample values, 32 MiB of
   materialized float64 signal, and at least 128 samples per selected window.
6. Report exact dimensions, channel order/type/unit, sampling rate, duration,
   sample indices/times, declared reference/filter/projector/compensation/bads
   state, geometry availability/hash, and aggregate-only annotation status.
7. Implement the frozen descriptive robust amplitude, finite/flat/duplicate,
   and median-Welch PSD formulas exactly. Use the registered frequency bounds,
   bands, Hann window, two-second segment, half overlap, DC removal, median
   aggregation, and `n_jobs=1`.
8. Do not invent generic clipping, excessive-amplitude, or line-noise pass/fail
   thresholds. Mark profile-dependent judgments unavailable. A warning must
   never delete, interpolate, filter, rereference, resample, normalize, or mark
   a channel bad.
9. Hash the registered bounded selected payload and in-memory metadata states
   before and after, then prove no mutation of signal values, annotations,
   bads, projectors, reference, compensation, sampling rate, or geometry. Do
   not hash or scan the full signal file to make this check.
10. Never persist waveforms. Redact absolute paths, participant/demographic
    data, measurement dates, serials, annotation/event descriptions and exact
    timestamps, free text, exact geometry coordinates, and signal values.
11. Add strict deterministic save/load/validate/summary APIs plus create and
    inspect CLI commands. Refuse malformed reports, tampering, collisions,
    unsafe paths, cap violations, and unexpected reader behavior.
12. Measure input and bytes actually read, output bytes, runtime, peak RSS,
    window/channel/sample counts, compatibility level, warnings/unavailable
    fields, and raw/cache/target/model/training/network counters. State that the
    producer is noncausal audit code and end-to-end latency is unmeasured.

Required tests and artifacts:

- Deterministic fixtures for all six format families plus every registered
  malformed/refusal family.
- Exact fixture-value, channel/timing/unit/geometry/event-state, PSD-peak,
  no-mutation, redaction, replay, tamper, collision, missing-extra, cap, and
  strict source-binding tests.
- One tiny ignored synthetic roundtrip and inspectable measured audit sidecar.
- A closeout document that distinguishes proven reader/report mechanics from
  unavailable real signal, task, benchmark, decoding, latency, and hardware
  claims.

Acceptance gates:

1. Run focused RW2 tests and the complete unittest and pytest suites with
   one-thread environment variables.
2. Run Ruff, compileall, `git diff --check`, root and RW2 CLI help, contract
   invariant checks, and one bounded synthetic roundtrip.
3. Measure and report runtime, peak RSS, every byte/counter/cap, and compare the
   complete suites with the pre-change baseline of 249 unittest tests with 3
   skips and 246 pytest tests with 3 skips plus 25 subtests.
4. Keep generated fixtures, reports, caches, and inspection debris out of git.
5. Commit and push coherent tested milestones. Do not call RW2 complete unless
   every frozen acceptance gate passes; park a failing adapter or the entire
   gate using the registered rule instead of expanding the architecture.

A passing RW2 implementation would prove only bounded, redacted,
source-preserving reader and descriptive-report mechanics on generated files.
It would not prove real recording quality, artifact detection validity,
preprocessing benefit, neural advantage, decoding, unseen-person transfer,
end-to-end real-time behavior, at-home hardware, arbitrary-thought reading, or
clinical utility.
