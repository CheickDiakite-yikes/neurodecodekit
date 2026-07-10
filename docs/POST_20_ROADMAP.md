# NeuroDecodeKit Post-20 Roadmap

The first 20-loop roadmap established safe data access, cache and report
contracts, honest baselines, two-session MEG evidence, one bounded EEG bridge,
and the continuous NeuroToken interface. Loop 13 remains deliberately parked
because current NPZ access never crossed its measured backend threshold.

This second roadmap moves toward genuinely local, incremental brain-to-text
without treating one interface proof as a product claim. Every loop must close
with a small artifact, explicit resource measurements, comparison against a
no-signal baseline where prediction is involved, and a kill/park/proceed
decision.

## Status

- Loop 21: Done. Five synthetic chunk schedules reproduce one causal frame
  stream with bitwise schedule invariance, zero right context, 300-byte mutable
  state, and explicit latency separation. See
  `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`.
- Loop 22: Done. One 1,130-parameter synthetic causal encoder was selected on
  validation, opened its frozen test once, beat both signal-free controls, and
  preserved all five replay schedules with 300-byte state. See
  `docs/LOOP_22_TINY_CAUSAL_ENCODER.md`.
- Loop 23: Preregistered. The language-model-free decoder, fresh 48/8/8 fixture,
  blank/repeat rules, partial-stability metrics, one-time access, and caps are
  frozen before implementation or target generation. See
  `docs/LOOP_23_PREREGISTRATION.md`.

## Loops 21-30

| # | Gate | Core question | Deliverable | Acceptance boundary |
|---:|---|---|---|---|
| 21 | Causal chunk/replay | Can a frame producer consume incremental signals without future context or chunk-boundary drift? | Versioned stream state, five schedule audit, latency/resource report. | Closed: 5/5 schedules pass; 0 right context; 300-byte state; exact schedule bits; no decoder or real data. |
| 22 | Tiny learned causal encoder | Can a small train-only causal model learn the synthetic motif task while preserving the Loop 21 stream contract? | Optional-Torch encoder, offline/stream replay, parameter/state/RSS/runtime report, prior comparator. | Closed: 1,130 parameters; validation and one frozen test pass; 5/5 replay schedules; 300-byte state; one-thread CPU; no real cache or text claim. |
| 23 | Streaming CTC prefix decoder | Can causal encoder frames produce stable incremental characters rather than only final strings? | Greedy/prefix state, partial-hypothesis trace, revision and emission-delay metrics. | Preregistered: fresh physical test, width-8 no-LM beam, blank/repeat oracle tests, first/stable/final timing, two signal-free controls, and one test open. Implementation pending. |
| 24 | Local precision and runtime | Can the fixed causal encoder/decoder fit a realistic local CPU envelope without changing outputs beyond a registered tolerance? | float32/float16/dynamic-int8 candidates, state/parameter/RSS/RTF/energy proxy report. | Select on synthetic validation; preserve float32 reference and label integer storage versus true integer execution honestly. |
| 25 | Causal preprocessing audit | Can existing real MEG train rows be replayed incrementally without future-aware filters, normalization, or padding leakage? | Train-only causal preprocessing contract and offline/stream audit; no score. | Open source-train rows only; keep five source-test and all consumed session-2 rows frozen. |
| 26 | Real validation-only encoder gate | Does the fixed small causal model learn anything above a no-signal prior on source validation without touching test? | Preregistered architecture, train-only fit, six-row validation report with uncertainty. | Proceed only on a registered margin and failure analysis; validation is consumed for model selection. |
| 27 | Fresh holdout preregistration | What new independent recording or participant slice can answer the next claim without recycling observed data? | Metadata-only candidate table, license/bytes/protocol, preregistered one-time analysis. | No download before exact cap and approval; no test until architecture and decision rule are frozen. |
| 28 | Session/person transfer | Does the frozen causal system transfer, and what calibration is actually required? | One-time fresh holdout report, calibration curve, no-signal comparator, uncertainty. | Separate same-person session and unseen-person claims; negative results close or redirect the branch. |
| 29 | Portable sensing translation | Which requirements survive movement from cryogenic MEG toward OPM-MEG or EEG? | Sensor geometry/bandwidth/noise/shielding/compute requirement matrix and partner-data gate. | No synthetic channel subset is called OPM-equivalent; hardware claims require measured device data. |
| 30 | Local private streaming prototype | Can a user inspect incremental output, revisions, latency, and provenance entirely on-device? | Loopback-only replay/live-fixture UI with stage-level latency and resource telemetry. | Real text remains protected; no cloud dependency; user-visible latency includes capture, preprocessing, encoder, decoder, and rendering stages. |

## Persistent Constraints

- Do not reopen the five observed S21 source-test rows or tune on the consumed
  63-row session-2 evaluation.
- Do not download another real recording without a pinned metadata plan,
  explicit file/byte cap, dry run, and approval.
- “Causal,” “streaming,” “online,” “real-time,” and “low latency” are distinct
  claims and require distinct evidence.
- Keep CTC/neural results beside a no-signal prior so language regularization
  is not credited to neural signal.
- Keep MEG, EEG, OPM-MEG, and sEMG evidence in separate cohorts.
- Treat all neural data and derived features as sensitive and local by default.
- Make no clinical, arbitrary-thought, or at-home hardware claim from healthy
  participants typing prompted or memorized sentences.
