# Start Here

1. Read `README.md` for the mission, results, proof boundaries, and quickstart.
2. Read `CONTRIBUTING.md` for the EEG data/hardware contribution paths.
3. Read `AGENTS.md` for coding-agent rules.
4. Read `docs/CODEX_HANDOFF.md` for the next three work orders.
5. Read `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md` for the measured parked
   result, then use its preregistration and authorization documents for audit.
6. Read `docs/LOOP_25_ANTI_ALIAS_AUDIT.md`,
   `docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`, and
   `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md` before making the next numbered
   decision. The original v0 registration remains historical provenance.
7. Review `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` only when deciding whether
   to authorize the independent RW3 Stage A.
8. Read `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md` and
   `docs/LOOPS_25_44_ROADMAP.md` for the planning-only Loops 25-44 queue.
9. Paste `prompts/CODEX_START_PROMPT.md` into Codex to continue.
10. Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tracker scope: the spreadsheet's `20` KPI is the size of the original roadmap,
not the current loop number. Its dashboard now separately reports the current
post-roadmap position as **Loop 25 amended v1; authorization pending**, and
its ninth sheet contains the separate **Loops 25-44 queue**. Loop 25 is in
review with `execution_authorized: false`; Loops 26-44 remain `Not Started` and
unauthorized. The queue does not reopen Loop 24 or authorize RW3.

The parallel Real-World Practice Track starts at
`docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md`. RW0 is a completed research gate;
RW1 is closed as a synthetic-fixture metadata-only interface gate. RW2 is now
closed at exact synthetic compatibility level 2: 38 generated recordings are
readable and two malformed/unsafe layouts refuse exactly across BrainVision,
EDF/EDF+, BDF, EEGLAB external-FDT, FIF, and BIDS. RW3's offline
replay/live-source protocol is now frozen at commit `c3d1f01`; it is a
registration result, not a runtime result. Commit `163ff2f` adds a hash-bound
Stage A decision packet whose machine request keeps `authorized_now` set to
`false`. Loop 24 ran once under its frozen contract after separate authorization
and implementation commits were pushed and remotely green. Float16 preserved
behavior but was slower; QNNPACK qint8 reduced payload but failed behavior and
runtime gates; no candidate qualified, seed 2402 stayed unopened, and the gate
parked at 65.154951 seconds versus its 60-second cap. Seed 2401 is consumed and
must not be used for tuning. Real data, targets, training, energy measurement,
RW3 Stage A, BrainFlow/LSL/PyXDF, sockets, streams, hardware, consumed caches,
S20, and automatic cleaning remain unauthorized. Loop 24 and RW3 remain
independent.
Loop 25's original registration at `a36d97b` was superseded before
authorization by green anti-alias amendment `b6b92d8`. V1 preserves seeds
2501/2502, seven chunk schedules, ten resume cuts, and three future-mutation
cuts while adding a dedicated causal anti-alias SOS, a 65,537-point 0-500 Hz
response grid, 23 alias probes, 45 refusal IDs, and 23 access counters. Its
one-thread, 8 MiB output, and 45-second caps are unchanged. The replacement
machine request remains `authorized_now: false`; both seeds are unopened. No
coefficients, fixture, transform, partition open, cache read, target, model,
training run, CLI, or experiment payload exists. The next numbered decision is
to use the exact sentence in `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, amend
again, or hold.
The proposed fresh S20 EEG block is **not authorized** for download or signal
access. Its exact four-file, 96,090,264-byte dry run is in
`docs/FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md`.

Current verified state: two complete S21 SpanishBCBL MEG recordings plus one
94,842,381-byte S7 SpanishBCBL EEG BrainVision bundle and their matching MAT
logs have been selectively downloaded under exact caps; the full dataset and
12.79-GB EEG subtree have not been downloaded. Loops 9-12, 14-22, and 23.5 are
complete; Loops 13, 23, and 24 are parked after measured gates. Loop 24 retains
float32, consumed selection seed 2401, and left qualification seed 2402
physically unopened. Loop 25 is amended and preregistered but not authorized;
seeds 2501 and 2502 remain unopened. Loops 26-44 remain planning-only.
Session 1 provides a strict 55/6/5 split with
train-only robust scaling. Session 2 is a complete two-part FIFF recording with
63 performed trials; MAT slots 54, 58, and 60 are explicitly empty and are
preserved as gaps. Its 102-magnetometer cache is scaled only with frozen
session-1 train statistics. The fixed same-subject cross-session tiny CTC fails
to generalize: corpus CER 0.9179 versus 0.7755 for the no-signal prior, with a
paired interval wholly favoring the prior. There is no reliable neural
advantage, unseen-person result, retained-accuracy result, integer-only
inference, real-time decoder, or at-home hardware claim. Session 2 is now a
consumed evaluation set. Loop 15 Stage B separately proves unlabeled robust
channel-affine recovery on a fixed synthetic diagonal shift: identity/adapted
holdout CER is 0.3448/0.0000, with zero real cache reads and only 21,354 bytes
of artifacts. Loop 16 then tests six calibration sizes, three shift seeds, and
three independently calibrated shift families. One 1.26-second synthetic row
meets the registered median stationary-diagonal rule, but one seed only ties;
the adapter harms all channel-mixing and time-varying holdout seeds. This is
not a human calibration-time or real-MEG claim. Loop 17 adds a local
artifact-backed evidence console with 19 synthetic examples, aggregate-only
real metrics, explicit unavailable confidence, noncausal/task scope, and
responsive browser QA. It performs no real model run or raw-data read. Loop 18
adds 11 versioned cards across six exact cohorts and four method families from
saved reports only. Four within-cohort rankings are authorized; no global rank
exists, all missing recommended metadata stays visible, and the 103,789-byte
build opens no cache or holdout. Loop 19 then passes a metadata-only access and
dependency gate, lazily aligns all 2,534 MAT triggers to one real S7 EEG file,
and writes a 12,428,800-byte `2197 x 61 x 25` cache. Its first transparent
within-session classifier is a negative result: 0.91% exact key-label accuracy
versus 12.27% for the train-only no-signal prior. This is bridge validation,
not useful EEG decoding or a portable-hardware claim. Loop 20 adds a
76,646-byte synthetic `NeuroTokenCache v0` shaped `48 x 16 x 32`, with timing,
masks, modality, geometry availability, strict split/source hashes, and
explicit causality/resource boundaries. The deterministic target-free payload
replays exactly, and an access-tracked audit now confirms that no source target
array is opened. It is not learned, not a decoding result, and not an
end-to-end streaming claim. Loop 21 then passes a five-schedule synthetic
causal replay gate: zero right context, exact frame/timestamp identity, bitwise
stream-schedule identity, 300-byte mutable state, and no target/model/decoder/
real-data access. Transport delay still ranges from 0 to 610 ms depending on
chunking, and end-to-end text latency remains unmeasured. Loop 22 then trains
one preregistered 1,130-parameter model on synthetic motif frames, selects
epoch 34 on validation, opens its eight-item test once, and passes both the
signal-free comparison and all five streaming schedules with 300-byte state.
That perfect synthetic motif result is a mechanism check, not text or brain
decoding; its test is consumed. Loop 23 then implements the preregistered
language-model-free greedy and width-8 prefix CTC decoders. Registered
validation passes at CER 0.0182 and 7/8 exact, so seed 2303 opens once. Frozen
test CER is 0.0545 and all repeated pairs are correct, but exact sequence
accuracy is only 5/8 versus the required 6/8. Every error is a complete target
plus one false tail symbol; prefix and greedy agree. Loop 23 is parked and its
test is consumed. Loop 23.5 then fits one preregistered blank-logit intercept on
fresh train-frame labels. Validation reaches 16/16 exact, opening seed 2353
once; the frozen test also reaches 16/16 and CER 0 versus 7/16 and CER 0.0818
without calibration. Nine items are corrected, none worsens, and all resource,
access, control, bootstrap, and replay gates pass. This is supervised synthetic
calibration only, seed 2353 is now consumed, and Loop 24 requires a separate
fresh protocol. That protocol was frozen at `186bb6f`, authorized separately,
implemented before data access, and executed once. Float16 was exact but slower;
qint8 was smaller but incorrect and slower; the total runtime cap failed; seed
2402 stayed unopened; and Loop 24 parked with float32 retained. See
`docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`,
`docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`,
`docs/LOOP_24_AUTHORIZATION_DECISION.md`,
`docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`,
`docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md`,
`docs/LOOP_25_ANTI_ALIAS_AUDIT.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`,
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, and
`docs/POST_20_ROADMAP.md`.

RW1 adds dependency-free `inspect-recording` and `inspect-intake-report`
commands for BrainVision, EDF/EDF+, BDF, EEGLAB, FIF, and BIDS level-0
metadata. The 532-byte synthetic roundtrip produced 11,545 bytes of validated
JSON/Markdown/audit output in 0.001659 seconds with 21,643,264-byte peak RSS
and zero binary/raw/cache/target/model/training/network reads. This is file and
report interface proof only. See `docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`.

RW2's frozen protocol covers explicit optional MNE adapters for synthetic
BrainVision, EDF/EDF+, BDF, EEGLAB external-FDT, FIF, and BIDS fixtures;
three-window/32-MiB signal materialization, one-thread, 30-second, 1-GiB RSS,
4-MiB per-run output, and 16-MiB fixture-set caps; strict privacy redaction;
descriptive time-domain and Welch PSD summaries; and no source mutation or
automatic bad-channel action. The 40-fixture implementation passes with 38
readable fixtures and two exact refusals. One measured FIF roundtrip selects
nine channels and three windows, returns 11,520 values, materializes 92,160
bytes, and writes 76,592 report bytes in 3.839168 seconds with 150,749,184-byte
peak RSS. Real/cache/target/model/training/network access is zero, source
before/after hashes match, producer causality is false, and end-to-end latency
is unmeasured. See `docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`.

RW3 freezes a future `neurodecodekit.source_chunk` envelope, separate raw,
corrected, and arrival clocks, explicit packet anomalies and reconnect state,
five chunk schedules, 18 target-free future fixture families, 30 exact refusal
IDs, and four sequential stages. Seven contract tests plus three authorization-
binding tests protect that registration and the proposed 90-case Stage A scope.
No fixture, payload, source chunk, CLI, optional dependency, board, socket,
stream, or XDF file was created or opened. See
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`,
`registries/replay_equivalence_contract.v0.json`,
`docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`, and
`registries/rw3_stage_a_authorization_request.v0.json`.

Loop 24 executed the float32 eager reference, explicit CPU float16, and dynamic-
qint8 QNNPACK candidates around the 1,130-parameter synthetic producer. All 12
balanced rounds and the timing protocol passed. Float16 passed correctness but
was `1.170x` the producer latency and `1.088x` the full-pipeline latency. Qint8
used `47.1%` of the float32 numeric payload but changed greedy/prefix behavior
and was `2.785x`/`1.812x` the producer/full latency. The 65.154951-second
orchestration exceeded the 60-second cap, so Loop 24 is parked with float32
retained and qualification unopened. See
`docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`.

The current registries keep prompted typing, imagined speech, natural reading,
P300, SSVEP, and motor imagery as separate evidence cohorts. They also keep
EEG separate from eye tracking, wrist EMG, heart/PPG, IMU, microphone, and hand
tracking. No live or portable device is qualified.
