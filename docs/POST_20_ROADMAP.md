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
- Loop 24: Parked after one registered target-free selection. All 12 balanced
  rounds complete; float16 preserves behavior but is slower, qint8 is smaller
  but incorrect and slower, no candidate qualifies, and seed 2402 stays
  physically unopened. Internal runtime is 65.154951 seconds against a frozen
  60-second cap. Float32 is retained and seed 2401 is consumed. Real data,
  targets, training, energy, RW3, and hardware remain unauthorized. See
  `docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md` and
  `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`.
- Loop 29: Planning research complete; experiment `Not Started`. Scalp EEG is
  the immediate local-first research lane, OPM-MEG is the same-modality
  partner/lab lane, and cryogenic MEG remains the reference. The 15-field
  matrix, six qualification levels, 5-10 GB capacity envelope, and exact
  1,106,030,247-byte future S20 plus S25 allocation are documented with 24
  false authorization flags. No download, real-data read, model, stream,
  device, partner, or hardware operation occurred. See
  `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md`.
- Loop 30: Planning research complete; target-free local replay experiment
  `Not Started`. The future inspector separates four source modes, a 30-field
  trace, nine clock domains, six latency levels, 18 requirements, and 30
  refusals while fixing loopback privacy, browser-network, and accessibility
  gates. All 30 authorization flags are false; no seed, trace, UI, server,
  browser run, model, stream, live source, or hardware operation exists. See
  `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md`.
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

## Closed And Current Post-Roadmap Gates

| # | Gate | Core question | Deliverable | Acceptance boundary |
|---:|---|---|---|---|
| 21 | Causal chunk/replay | Can a frame producer consume incremental signals without future context or chunk-boundary drift? | Versioned stream state, five schedule audit, latency/resource report. | Closed: 5/5 schedules pass; 0 right context; 300-byte state; exact schedule bits; no decoder or real data. |
| 22 | Tiny learned causal encoder | Can a small train-only causal model learn the synthetic motif task while preserving the Loop 21 stream contract? | Optional-Torch encoder, offline/stream replay, parameter/state/RSS/runtime report, prior comparator. | Closed: 1,130 parameters; validation and one frozen test pass; 5/5 replay schedules; 300-byte state; one-thread CPU; no real cache or text claim. |
| 23 | Streaming CTC prefix decoder | Can causal encoder frames produce stable incremental characters rather than only final strings? | Greedy/prefix state, partial-hypothesis trace, revision and emission-delay metrics. | Parked: mechanics and validation pass, but frozen exact test accuracy is 5/8 below 6/8; test consumed; no tuning or rerun. |
| 23.5 | Blank/boundary calibration | Can one train-frame-fitted, target-length-independent blank intercept suppress tail false positives on fresh splits without harming any item? | Fresh 64/16/16 fixture, one convex scalar fit, unchanged comparator, calibration metrics, and one new test. | Closed: validation and frozen test are 16/16 exact at CER 0; zero regressions; 5/5 replay; seed 2353 consumed; supervised synthetic calibration only. |
| 24 | Local precision and runtime | Can a decoder that first passes its correctness gate fit a realistic local CPU envelope without changing outputs beyond a registered tolerance? | float32/float16/dynamic-int8 candidates, state/parameter/RSS/RTF report. | Parked: float16 is exact but slower; qint8 is smaller but incorrect and slower; no qualification open; runtime 65.154951 sec exceeds 60 sec; retain float32 and do not rerun seed 2401. |
| 25 | Causal preprocessing audit | Can every upstream transform run with zero future context, full folding-band anti-alias protection, exact timing, and chunk/resume identity? | Frozen stateful notch/bandpass/dedicated-antialias SOS, decimation, normalization, and target-free v1 packet. | Complete after green authorization `1e7296a` and implementation `439f151`; 24/24 items, 168 schedules, 240 resumes, and 72 mutation controls passed with zero protected reads; no rerun is authorized. |
| 26 | Real validation-only encoder gate | Can one fixed tiny causal encoder beat honest controls on the six reserved source-validation sentences? | Planning-only identifiability note and machine boundary before any experiment contract. | Planning research complete at `03605c5`; 2,908/2,884-parameter recommendations, six controls, 64 exact paired assignments, and 14 false authorization fields; experiment remains `Not Started` with zero protected access. |
| 27 | Fresh holdout preregistration | Which independent recording can answer the next transfer claim without consumed evidence? | Planning-only official metadata selector, exact candidate identities, target-isolation design, and blockers. | Planning research complete at `b3d61b6`; S25 session 2 block 2 selected as two files/1,009,939,983 bytes; 18 false authorization fields; no preregistration, request, download, hash, header, signal, target, or model access. |
| 28 | Session and person transfer | What claim can one unseen-person final-only recording answer without fitting anything to that person? | Planning-only T0-T3 taxonomy and strict zero-shot final decision rule. | Planning research complete; S25 reserved for T2 with zero fit rows, a 48-row floor, 0.05 macro-CER margin, 65,535 paired assignments plus observed, four comparators, and 21 false authorization fields; experiment remains `Not Started`. |
| 29 | Portable sensing translation | Which requirements survive movement from cryogenic MEG to OPM-MEG or scalp EEG? | Planning-only modality matrix, qualification ladder, two-lane decision, and bounded data path. | Planning research complete; experiment `Not Started`; 15 requirements, 4 profiles, 6 qualification levels, 24 false authorization fields, and no data/device execution. |
| 30 | Local private streaming prototype | Can a user inspect incremental replay without confusing it with live neural decoding? | Planning-only target-free trace, clock, latency, privacy, accessibility, and browser-QA boundary. | Planning research complete; experiment `Not Started`; 4 source modes, 30 event fields, 9 clocks, 6 latency levels, 18 gates, 30 refusals, 30 false authorization fields, and no trace/UI/server execution. |

## Next Planned Tranche: Loops 25-44

The next 20 loops are now defined in detail across five phases: causal evidence,
translation/generalization, reliability/confounds, reproducibility/local
deployment, and live translation/release. The machine source of truth is
`registries/next_20_loops.v0.json`; the human work orders and kill branches are
in `docs/LOOPS_25_44_ROADMAP.md`; the primary-source rationale is in
`docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`.

Loop 25 is now `Complete` with
`proof_posture: target_free_synthetic_causal_preprocessing_mechanics_passed`
and no rerun authorization. Loop 26
planning research is complete, but its experiment remains `Not Started` and
`planned_not_authorized`. Loop 27 has completed metadata research and selected
S25, but its preregistration remains blocked. Loop 28 planning research defines
the strict zero-shot rule while its experiment remains `Not Started`. Loop 29
planning research defines separate scalp EEG and OPM-MEG lanes while its
experiment remains `Not Started`. Loop 30 planning research defines the target-
free local replay boundary while its experiment remains `Not Started`. Loop 31
planning research defines a 10-condition encoder and contingent 5-condition
LLM/Neuro Token attribution firewall while its experiment remains `Not
Started`; its maximum future local claim is sensor-signal dependence and
brain-specific attribution remains blocked on Loop 35. Loop 32 planning
research recommends one causal 32-parameter hidden affine adapter, four
calibration modes, nested `0, 2, 4, 8, 16, 32` sentence budgets, and physically
separate 32/16/48 calibration/selection/final floors while its experiment
remains `Not Started`. All 22 authorization fields are false, no candidate or
mode is selected, and protected work is unauthorized. Loop 33 planning
research recommends nested `8, 16, 24, 32, 44, 55` unique-sentence prefixes,
at most three seeds and 18 candidate fits, size-matched priors, and one shared
validation event after every prediction is hash-frozen. Its experiment remains
`Not Started`; no physical-repetition lane or acquisition recommendation
exists, and all protected work is unauthorized. Loop 34 planning research
separates seven confidence semantics, eight score/control roles, and fresh
synthetic `128/64/256` calibration/selection/final recommendations. Its
experiment remains `Not Started`; confidence is unavailable, the six real
validation rows are ineligible for Loop 34 fitting and independent
qualification, and all fixture/fit/target/scoring work is unauthorized. Loop
35 planning research freezes ten confound classes, nine future synchronized
stream classes, 13 conditions, three stages, 24 gates, 32 refusals, and 31 false
authorization fields. Its experiment remains `Not Started`; existing evidence
lacks complete synchronized peripheral controls, and the maximum future local
claim is incremental brain-sensor information beyond recorded controls rather
than absolute brain origin. Loop 36 planning research freezes six
representation layers, five modality profiles, 24 channel fields, 12 operation
classes, 16 fixtures, 22 gates, 30 refusals, and 29 false authorization fields.
Its experiment remains `Not Started`; declared metadata compatibility is the
maximum future real-header claim. Loop 37 planning research freezes six export
layers, five artifact profiles, 15 stable BIDS mappings, 16 NeuroDecodeKit
extension fields, 20 fixtures, four stages, 24 gates, 32 refusals, and 29 false
authorization fields. Its experiment remains `Not Started` and unauthorized;
custom payloads remain explicitly non-standard. Loop 38 planning research
freezes five sensitivity levels, eight artifact classes, ten lifecycle
surfaces, 12 sensitive-field classes, 12 threats, five deletion-receipt levels,
24 fixtures, four stages, 26 gates, 36 refusals, and 32 false authorization
fields. Its experiment remains `Not Started`; unknown copies remain unresolved
and all scanner/deletion/identity/release work is unauthorized. Loop 39
planning research freezes seven qualification levels, 18 environment identity
fields, eight output classes, six comparison classes, six future matrix cells,
20 fixture families, four stages, 28 gates, 38 refusals, and 36 false
authorization fields. Its experiment remains `Not Started`; no matrix cell or
cross-machine reproduction has run. Loop 40 planning research freezes seven
qualification levels, six package layers, four unselected backend profiles, 20
identity fields, 24 fixtures, four stages, 30 gates, 40 refusals, and 40 false
authorization fields around the retained float32 reference. Its experiment
remains `Not Started`; no target, backend, install, export, package, inference,
simulator, device, or hardware operation exists. Loop 41 planning research
freezes the stream-to-NeuroToken clock, anomaly, state, schedule, and provenance
firewall while its experiment remains `Not Started` and unauthorized. Loop 42
planning research selects OpenBCI Cyton base 8-channel USB-radio at Q0 for one
future mechanics path while its experiment remains `Not Started` and
unauthorized; Loop 43 planning research defines the independent artifact-
reproduction firewall while its challenge remains `Not Started` and
unauthorized. Loop 44 artifact-only claim review is complete, with engineering
release held and scientific performance parked. All 20
`execution_authorized` flags are false. Loop 25's exact decision packet is
ready for review, while Loops 26-33 have no
preregistration or authorization packet. Roadmap approval, general
continuation, or documentation work cannot reopen Loop 24, authorize RW3 Stage
A, or authorize any Loop 25-44 operation.

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
explicitly approves the exact acquisition packet. Loop 24 is independently
preregistered at `186bb6f`, with every immutable contract flag false, and has a
separate narrow target-free authorization that takes effect only after its own
tested commit is pushed. It cannot authorize RW3, data access, or training; RW3
authorization cannot authorize Loop 24. Neither track may use consumed evidence
from the other.

## Persistent Constraints

- Do not reopen the five observed S21 source-test rows or tune on the consumed
  63-row session-2 evaluation.
- Do not reopen Loop 22 seed 2203 or Loop 23 seed 2303 for selection, tuning,
  thresholding, calibration, endpoint design, or fresh evaluation.
- Do not reopen Loop 23.5 seed 2353 for precision selection, tolerance setting,
  tuning, endpoint design, or fresh evaluation.
- Do not rerun or tune Loop 24 selection seed 2401 after its parked result.
- Keep Loop 24 seed 2402 physically unopened; candidate outputs, targets,
  labels, text, and consumed evidence may not repurpose it.
- Do not rerun or tune Loop 25 or repurpose its consumed seeds 2501 and 2502.
  Loop 26 and every later experiment require their own tested, pushed, green
  authorization sequence.
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
- Keep Loop 32 planning-only. Its 32-parameter adapter, four modes, six budgets,
  physical split floors, and human-burden ledger are recommendations, not
  permission to select a participant, repurpose S25, read signal or labels,
  fit an adapter, train, or open a final target.
- Keep Loop 33 planning-only. Its `8, 16, 24, 32, 44, 55` prefixes, three-seed
  ceiling, 18 candidate fits, trend rules, and shared target-open order are
  recommendations, not permission to read protected data, train, score,
  duplicate rows as physical repetitions, acquire data, or extrapolate a
  universal scaling law. The experiment is `Not Started` and unauthorized.
- Keep Loop 34 planning-only. Its seven semantics, eight score/control roles,
  `128/64/256` partition recommendation, coverage grid, bounded-loss rules,
  generalized-risk metrics, and revision-delay contract are not permission to
  generate a fixture, fit confidence, open targets, score, expose confidence,
  or access real data. The experiment is `Not Started`, confidence is
  unavailable, and all 26 authorization fields are false.
- Keep Loop 35 planning-only. Its confound taxonomy, stream registry,
  13-condition matrix, 32/16/48 split recommendation, estimands, gates, and
  refusal IDs are not permission to generate a fixture, acquire synchronized
  EOG/EMG/gaze/motion/audio, open protected data, fit or score a model, or
  claim brain origin. Missing controls remain unavailable, not clean.
- Keep Loop 36 planning-only. Its identity layers, modality profiles, channel
  record, operation taxonomy, unit/transform checks, fixture families, gates,
  and refusals are not permission to generate a fixture, inspect a real header,
  read signals, transform coordinates, scale signals, rereference, compensate,
  interpolate, fit a mapping, run a model, or claim device equivalence. Unknown
  metadata remains unavailable rather than guessed.
- Keep Loop 37 planning-only. Its BIDS field map, artifact profiles, fixture
  families, path/identity rules, no-raw-copy audit, validator ceiling, gates,
  and refusals are not permission to generate a fixture or derivative tree,
  install/run a validator, inspect protected payloads, copy data, map real
  subject identifiers, release/upload an artifact, or call a non-standard NPZ
  or report payload BIDS-compliant.
- Keep Loop 38 planning-only. Its sensitivity, artifact, lifecycle, redaction,
  threat, and deletion-receipt taxonomies are not permission to create a
  fixture or scanner, inspect protected roots, delete files, rewrite history,
  clean remotes or backups, run an identity attack, decide consent/license,
  release/upload data, or call path absence secure media sanitization. Unknown
  copies stay unresolved.
- Keep Loop 39 planning-only. Its qualification levels, environment identity
  schema, output classes, tolerance policy, future matrix, fixture families,
  gates, and refusals are not permission to create fixtures, install or lock
  dependencies, mutate CI, build packages, open protected payloads, run models
  or training, recruit an independent reproducer, package an edge runtime, or
  claim cross-machine reproduction. Deterministic replay, exact semantics,
  numerical compatibility, reproduction, independent reproduction, and
  replication remain distinct claims.
- Keep Loop 40 planning-only. Its backend profiles, package layers, identity
  fields, host-state boundary, fixture families, gates, and refusals are not
  permission to select a target, install a runtime, export or convert a model,
  generate a package, run inference/profiling/delegation, launch a simulator or
  app, or operate a device. ExecuTorch/XNNPACK is a research lead only;
  desktop packaging is not portable hardware and packaging is not science.
- Keep Loop 41 planning-only. Its six integration layers, seven clock views,
  eight anomaly classes, five schedules, five resume cuts, bounded state, 18
  hash bindings, 28 fixtures, 32 gates, and 42 refusals are not permission to
  create a source chunk, fixture, adapter, preprocessing output, NeuroToken
  payload, stream, latency claim, device operation, or scientific result. The
  experiment remains `Not Started` and unauthorized.
- Keep Loop 42 planning-only. Its Q0 Cyton candidate, identity and packet
  fields, clock-origin rules, anomaly accounting, privacy/locality surfaces,
  battery-only safety rules, stages, gates, and refusals are not permission to
  purchase a board, install/import BrainFlow, read a serial port, discover or
  connect hardware, query/update firmware, contact a participant, place
  electrodes, record data, open a network path, or claim signal quality,
  capture latency, decoding, portability, safety, or home usability.
- Keep Loop 43 planning-only. Its independent identity record, packet and
  submission fields, commit-reveal order, comparison/discrepancy classes,
  security/privacy rules, stages, gates, and refusals are not permission to
  create a packet, oracle, fixture, challenge workflow, outreach, contributor
  submission, adjudication, archive, DOI, badge, release, or runtime. The
  challenge remains `Not Started` and unauthorized. Independent artifact
  reproduction is not scientific replication, neural decoding evidence, or
  person, platform, device, and home-use generalization.
