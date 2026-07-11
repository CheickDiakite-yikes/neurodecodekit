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
- Loop 23: Parked after one preregistered frozen test. Decoder semantics,
  controls, 5/5 replay schedules, repeated-pair recovery, and resource gates
  pass, but exact test accuracy is 5/8 against a 6/8 threshold. All three test
  errors are correct targets plus one false tail symbol. Seed 2303 is consumed.
  See `docs/LOOP_23_STREAMING_CTC_DECODER.md`.
- Loop 23.5: Done. One preregistered train-frame blank-logit intercept corrects
  10 validation and 9 frozen-test tail errors with no regressions. Validation
  and the once-opened seed-2353 test both reach 16/16 exact and CER 0; 5/5
  calibrated and unmodified replay schedules, controls, bootstrap, access, and
  resource gates pass. Seed 2353 is consumed. See
  `docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`.
- Real-World Practice Track RW0: Done as a primary-source research and planning
  gate. Versioned dataset/device registries, a local BYO Neurodata contract,
  and an exact 96,090,264-byte S20 EEG approval packet are frozen. No raw data,
  consumed cache, model, or target was opened, and no download is authorized.
  See `docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md`.
- Real-World Practice Track RW1: Done as a dependency-free level-0 metadata
  interface gate. Eleven focused tests cover six format families, safe paths,
  companions, caps, collision behavior, target isolation, deterministic core
  artifacts, measured audit sidecars, and inspect-time hash validation. The
  532-byte synthetic roundtrip writes 11,545 bytes with zero binary, raw,
  cache, target, model, training, or network access. See
  `docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`.
- Real-World Practice Track RW2: Done at exact synthetic compatibility level 2.
  Forty generated fixtures cover six format families: 38 read successfully and
  two refuse exactly. One measured FIF report selects nine channels and three
  windows, returns 11,520 values, writes 76,592 bytes in 3.839168 seconds, and
  records 150,749,184-byte peak RSS with zero real/cache/target/model/training/
  network access. See `docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`.
- Real-World Practice Track RW3: Registration is frozen at `c3d1f01`, and the
  Stage A decision packet is prepared at `163ff2f`. The packet binds a future
  5-schedule by 18-fixture matrix (90 cases), all 30 exact refusal IDs, one-
  thread caps, and an authorization-only commit sequence. Its machine request
  says `authorized_now: false`; no runtime, fixture, adapter, socket, board,
  device, recording, target, model, or training access is authorized. See
  `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`.

## Loops 21-30

| # | Gate | Core question | Deliverable | Acceptance boundary |
|---:|---|---|---|---|
| 21 | Causal chunk/replay | Can a frame producer consume incremental signals without future context or chunk-boundary drift? | Versioned stream state, five schedule audit, latency/resource report. | Closed: 5/5 schedules pass; 0 right context; 300-byte state; exact schedule bits; no decoder or real data. |
| 22 | Tiny learned causal encoder | Can a small train-only causal model learn the synthetic motif task while preserving the Loop 21 stream contract? | Optional-Torch encoder, offline/stream replay, parameter/state/RSS/runtime report, prior comparator. | Closed: 1,130 parameters; validation and one frozen test pass; 5/5 replay schedules; 300-byte state; one-thread CPU; no real cache or text claim. |
| 23 | Streaming CTC prefix decoder | Can causal encoder frames produce stable incremental characters rather than only final strings? | Greedy/prefix state, partial-hypothesis trace, revision and emission-delay metrics. | Parked: mechanics and validation pass, but frozen exact test accuracy is 5/8 below 6/8; test consumed; no tuning or rerun. |
| 23.5 | Blank/boundary calibration | Can one train-frame-fitted, target-length-independent blank intercept suppress tail false positives on fresh splits without harming any item? | Fresh 64/16/16 fixture, one convex scalar fit, unchanged comparator, calibration metrics, and one new test. | Closed: validation and frozen test are 16/16 exact at CER 0; zero regressions; 5/5 replay; seed 2353 consumed; supervised synthetic calibration only. |
| 24 | Local precision and runtime | Can a decoder that first passes its correctness gate fit a realistic local CPU envelope without changing outputs beyond a registered tolerance? | float32/float16/dynamic-int8 candidates, state/parameter/RSS/RTF/energy proxy report. | Unblocked for preregistration only; preserve the frozen reference, keep seed 2353 out of candidate selection, and distinguish label storage from true integer execution. |
| 25 | Causal preprocessing audit | Can existing real MEG train rows be replayed incrementally without future-aware filters, normalization, or padding leakage? | Train-only causal preprocessing contract and offline/stream audit; no score. | Open source-train rows only; keep five source-test and all consumed session-2 rows frozen. |
| 26 | Real validation-only encoder gate | Does the fixed small causal model learn anything above a no-signal prior on source validation without touching test? | Preregistered architecture, train-only fit, six-row validation report with uncertainty. | Proceed only on a registered margin and failure analysis; validation is consumed for model selection. |
| 27 | Fresh holdout preregistration | What new independent recording or participant slice can answer the next claim without recycling observed data? | Metadata-only candidate table, license/bytes/protocol, preregistered one-time analysis. | No download before exact cap and approval; no test until architecture and decision rule are frozen. |
| 28 | Session/person transfer | Does the frozen causal system transfer, and what calibration is actually required? | One-time fresh holdout report, calibration curve, no-signal comparator, uncertainty. | Separate same-person session and unseen-person claims; negative results close or redirect the branch. |
| 29 | Portable sensing translation | Which requirements survive movement from cryogenic MEG toward OPM-MEG or EEG? | Sensor geometry/bandwidth/noise/shielding/compute requirement matrix and partner-data gate. | No synthetic channel subset is called OPM-equivalent; hardware claims require measured device data. |
| 30 | Local private streaming prototype | Can a user inspect incremental output, revisions, latency, and provenance entirely on-device? | Loopback-only replay/live-fixture UI with stage-level latency and resource telemetry. | Real text remains protected; no cloud dependency; user-visible latency includes capture, preprocessing, encoder, decoder, and rendering stages. |

## Parallel Real-World Practice Track

This track uses `RW` identifiers so it does not renumber Loop 24 or overwrite
the causal-decoder sequence. It may share file, cache, report, and source
contracts, but each predictive task remains in its own evidence cohort.

| ID | Gate | Core question | Deliverable | Acceptance boundary |
|---|---|---|---|---|
| RW0 | Dataset/device research | Which public cohorts, devices, formats, and transports are credible, and which claims do they support? | Primary-source research, versioned registries, BYO spec, exact fresh-data approval packet. | Closed: 8 datasets, 13 devices, and one no-download S20 proposal; zero signal/consumed/model/target access. |
| RW1 | Local metadata intake | Can a user safely identify a local recording or BIDS root without importing MNE or reading binary signal samples? | Level-0 scanner, companion/path/cap validation, JSON/Markdown report, CLI. | Closed: 11 focused tests; 532-byte fixture; 11,545 output bytes; deterministic core; zero signal/target/network access. |
| RW2 | Signal-quality contract | Can optional MNE adapters read bounded samples and report units, reference, channels, geometry, events, PSD, and quality warnings reproducibly? | Lazy readers and frozen quality metrics for BrainVision, EDF/BDF, EEGLAB, FIF, and BIDS. | Closed: 38/38 readable fixtures pass; 2/2 refusals match; privacy/no-mutation/caps/replay pass; synthetic only and no real-quality claim. |
| RW3 | Offline replay/live-source equivalence | Can a recording replay through the exact chunk contract intended for a live board? | Versioned source chunks, BrainFlow playback/synthetic adapters, LSL timestamp audit. | Preregistered at `c3d1f01`; Stage A packet prepared at `163ff2f` for 90 future cases and 30 refusals; no runtime result and `authorized_now` remains false. |
| RW4 | First fresh public EEG benchmark | Does one independently approved task-matched EEG block show event-label signal above prior and shuffle controls? | One-time S20 packet or a formally revised alternate, extraction, strict split, aggregate report. | Blocked on explicit approval; exactly four files/96,090,264 bytes; no CER/WER or test reuse. |
| RW5 | Board-neutral acquisition | Can one BrainFlow or LSL EEG board pass replay equivalence and privacy checks? | Device descriptor, consent/locality audit, recorded/live comparison. | One board only; raw API and timing measured; no portable decoding claim from connectivity alone. |
| RW6 | Prompted-typing EEG protocol | Can a task-matched local EEG recording be collected with synchronized prompts and keystrokes? | Consent-aware protocol, triggers, calibration, acquisition QC, preregistration. | No collection before ethics/consent/retention and exact task/split approval. |
| RW7 | Multimodal accessibility ablations | What comes from EEG versus eye, EOG, EMG, PPG, IMU, microphone, or hand tracking? | Brain-only, peripheral-only, and combined reports under one synchronized protocol. | No peripheral contribution attributed to EEG; Meta Neural Band remains sEMG. |
| RW8 | Local BYO Neurodata workbench | Can users inspect, replay, qualify, and report recordings without cloud upload? | Operational local UI with five entry actions and compatibility levels 0-6. | Unknown files remain inspectable but non-decodable; every result carries proof posture. |
| RW9 | Phone/wearable deployment | Which validated local capabilities fit a phone or wearable envelope? | Measured packaging, privacy, battery, latency, and offline inference gate. | Requires a qualified device/task/model first; no deployment theater or clinical claim. |

`RW1` and `RW2` are closed at their exact synthetic proof boundaries. `RW3`'s
chunk, clock, packet-loss, replay, privacy, resource, and tolerance contract is
frozen at `c3d1f01`, before implementation. The next practice-track decision is
whether to authorize Stage A pure-Python synthetic replay only, using the
packet prepared at `163ff2f`, or hold it. Packet preparation is not
authorization. BrainFlow, LSL, PyXDF, sockets, live sources, hardware, and
Stages B-D remain independently gated. `RW4` remains blocked until the user
explicitly approves the exact acquisition packet. Loop 24 can proceed
independently after its own preregistration; neither track may use consumed
evidence from the other.

## Persistent Constraints

- Do not reopen the five observed S21 source-test rows or tune on the consumed
  63-row session-2 evaluation.
- Do not reopen Loop 22 seed 2203 or Loop 23 seed 2303 for selection, tuning,
  thresholding, calibration, endpoint design, or fresh evaluation.
- Do not reopen Loop 23.5 seed 2353 for precision selection, tolerance setting,
  tuning, endpoint design, or fresh evaluation.
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
- Do not compare prompted typing, imagined speech, reading, P300, SSVEP, or
  motor imagery as one task or one leaderboard.
- Do not call eye tracking, wrist EMG, PPG, IMU, microphone, or hand tracking
  brain activity. Require brain-only, peripheral-only, and combined ablations.
- Keep the S20 packet dry-run-only until explicit approval names its revision,
  four files, 128-MiB acquisition cap, and one-time split.
