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
- `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`
- `docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`
- `registries/local_precision_runtime_contract.v0.json`
- `docs/LOOP_24_AUTHORIZATION_DECISION.md`
- `registries/loop24_authorization_decision.v0.json`
- `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`
- `docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md`
- `docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md`
- `registries/causal_preprocessing_contract.v0.json`
- `docs/LOOP_25_ANTI_ALIAS_AUDIT.md`
- `docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`
- `registries/causal_preprocessing_contract.v1.json`
- `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`
- `registries/loop25_authorization_request.v1.json`
- `registries/loop25_authorization_decision.v1.json`
- `docs/LOOP_25_CAUSAL_PREPROCESSING_RESULT.md`
- `registries/loop25_causal_preprocessing_result.v1.json`
- `docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop26_research_boundary.v0.json`
- `docs/LOOP_26_SHARED_VALIDATION_RESULT.md`
- `registries/loop26_shared_validation_result.v0.json`
- `docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop27_research_boundary.v0.json`
- `docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop28_research_boundary.v0.json`
- `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop29_research_boundary.v0.json`
- `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop30_research_boundary.v0.json`
- `docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop31_research_boundary.v0.json`
- `docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop32_research_boundary.v0.json`
- `docs/POST_20_ROADMAP.md`
- `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`
- `docs/LOOPS_25_44_ROADMAP.md`
- `registries/next_20_loops.v0.json`
- `docs/OPEN_SOURCE_READINESS.md`

Preserve every existing change and the unrelated tracker inspection NDJSON.
Do not reset, revert, delete, or overwrite work already present.

## Current proof boundary

- Loops 1-12, 14-22, and 23.5 are complete. Loops 13, 23, and 24 are deliberately
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
- RW3's replay/live-source-equivalence protocol is frozen at commit `c3d1f01`.
  Five schedules, 18 future fixture families, 30 exact refusal IDs, and four
  sequential adapter stages are registered; no source chunk or adapter exists.
- Commit `163ff2f` prepares a hash-bound Stage A packet covering 90 proposed
  cases and all 30 refusals. Its machine request says `authorized_now: false`;
  the packet is not authorization.
- Loop 24 completed one registered target-free selection after its
  preregistration, authorization, implementation, and CI boundaries. Float16
  preserved behavior but was slower; QNNPACK qint8 reduced payload but changed
  behavior and was slower. No candidate qualified, seed 2402 stayed unopened,
  and 65.154951 seconds exceeded the 60-second cap. Loop 24 is parked, float32
  is retained, and seed 2401 is consumed. No rerun or post-result tuning is
  authorized. Real/consumed data, targets, labels, text, training, energy, RW3,
  devices, hardware, and Loops 26-44 remain unauthorized.
- Loop 25 causal preprocessing preserves immutable v0 history, green amendment
  `b6b92d8`, separate green authorization `1e7296a`, and green implementation
  `439f151`. One registered target-free run passed its static gate before either
  partition opened, then passed 24/24 items, 168 schedule checks, 240 resume
  checks, and 72 future-mutation controls with zero protected reads. Static plus
  complete-gate runtime was 5.542175 seconds, maximum RSS was 136,806,400 bytes,
  and generated output was 788,967 bytes. It is complete with no rerun open.
- Loops 25-44 are now a detailed planning-only queue: exactly 20 contiguous
  rows across five phases, with source bindings, controls, metrics, acceptance
  gates, stop rules, dependencies, resource caps, and 20 false execution flags.
  Loop 25 is `Complete`; Loop 26/31/33 share a green preregistration at
  `881145d`, authorization at `1c0e52c`, and one consumed negative result; all
  three are parked and no rerun is authorized. Loop 27 planning research has
  selected S25 metadata while preregistration remains blocked; Loop 28 planning
  research defines a strict zero-shot rule while its experiment remains `Not
  Started`; Loops 29-39 have completed planning research while their
  experiments remain `Not Started`; confidence is unavailable, Loop 35's
  maximum future local claim is incremental brain-sensor information beyond
  recorded controls, Loop 36's maximum future real-header claim is
  declared metadata compatibility, Loop 37 caps future Stage B at a validator-
  assessed BIDS envelope with explicitly non-standard payloads, Loop 38 keeps
  unknown copies unresolved and separates path receipts from media
  sanitization, Loop 39 separates deterministic replay, semantic/numerical
  compatibility, reproduction, independent reproduction, and replication,
  Loop 40 separates the frozen graph from host state/timestamps, fallback,
  complete package cost, named-target qualification, and physical-device
  claims while its experiment remains `Not Started`; Loop 41 planning research
  defines the stream-to-NeuroToken clock, anomaly, state, schedule, and
  provenance firewall while its experiment remains `Not Started` and
  unauthorized; Loop 42 planning research selects OpenBCI Cyton base
  8-channel USB-radio for future mechanics only while its experiment remains
  `Not Started` and unauthorized; Loop 43 planning research defines the
  independent artifact-reproduction firewall while its challenge remains `Not
  Started` and unauthorized; Loop 44 artifact-only review is complete; all 20
  execution flags remain false.
- Loop 26's green shared contract froze a 2,908-parameter causal candidate,
  2,884-parameter linear comparator, 21 fits, 24 target-blind inferences, six
  priors, 31 prediction sets, ten encoder conditions, six nested data sizes,
  and all 64 paired sign assignments over six validation sentences. After the
  exact authorization and remote-green prediction freeze, the six targets
  opened once. Candidate macro CER was `0.938177` versus prior `0.751235`;
  primary, attribution, and scaling gates failed. Source test and session 2
  stayed closed. The result is consumed and no rerun or tuning is authorized.
- Loop 27 planning research at `b3d61b6` selects S25 session 2 block 2 as the
  smallest eligible strict MEG metadata pair: two files totaling
  1,009,939,983 bytes. S23 is officially excluded and S20 remains a separate
  EEG cohort. All 18 permissions are false; no preregistration, acquisition
  request, download, local MAT payload hash, header, signal, target, model,
  training, final open, or backup substitution exists.
- Loop 28 planning research defines four noninterchangeable T0-T3 transfer
  levels and reserves S25 for strict T2 zero-shot evaluation with zero fit or
  calibration rows. Its future recommendation requires at least 48 final rows,
  0.05 macro sentence-CER improvement, 65,535 deterministic paired assignments
  plus observed, and strict corruption-control wins. All 21 authorization
  fields are false; no preregistration, prediction, calibration, or final open
  exists.
- Loop 29 planning research is complete while the portable-sensing experiment
  remains `Not Started`. Scalp EEG is the immediate local-first research lane,
  OPM-MEG is the same-modality partner/lab lane, and cryogenic MEG remains the
  reference. The registry freezes 15 requirements, four modality profiles, six
  qualification levels, 12 future packet gates, a preferred 5,000,000,000-byte
  and absolute 10,000,000,000-byte capacity envelope, and 24 false
  authorization fields. Exact future S20 plus S25 bundles total 1,106,030,247
  bytes, but storage capacity is not download permission. No real-data read,
  model, SDK, stream, device, partner, or hardware operation occurred.
- Loop 30 planning research is complete while the target-free local replay
  experiment remains `Not Started`. The future inspector freezes four source
  modes, a 30-field trace contract, nine clock domains, six latency levels, 18
  requirements, 30 refusals, fixed loopback/browser/privacy/accessibility
  settings, and 30 false authorization fields. No seed, trace, fixture, UI,
  server, browser run, consumed artifact, model, stream, live source, or
  hardware operation exists. Stability is not confidence or correctness, and
  replay scheduling is not capture-to-user latency.
- Loop 31 planning research remains immutable, while its shared encoder matrix
  has now been consumed and parked. Exact-zero and timing-only components
  passed, but the complete six-row intersection-union gate failed. The
  contingent LLM/Neuro Token matrix stayed closed; sensor-signal dependence
  and brain-specific attribution were not established.
- Loop 32 planning research is complete while the fresh-person calibration
  experiment remains `Not Started`. The future boundary recommends one causal
  32-parameter hidden affine adapter, four distinct calibration modes, nested
  `0, 2, 4, 8, 16, 32` sentence budgets, physically separate 32/16/48
  calibration/selection/final floors, six conditions, 20 gates, 26 refusals,
  and 22 false authorization fields. No candidate or mode is selected; S25
  remains final-only. No participant/cache/signal/label/target, checkpoint,
  model, adapter-fit, training, final evaluation, download, stream, device, or
  hardware operation exists or is authorized.
- Loop 33 planning research remains immutable, while its bounded local scaling
  curve has now been consumed and parked. The `8, 16, 24, 32, 44, 55` curve
  improved descriptively across all three seed slopes, but the 55-row model
  remained worse than its matched prior. No scaling-law, repetition, or
  acquisition claim exists, and no rerun is authorized.
- Loop 34 planning research is complete while the confidence, abstention, and
  revision experiment remains `Not Started`. The future boundary separates
  seven confidence semantics, eight score/control roles, recommended fresh
  target-free synthetic `128/64/256` calibration/selection/final partitions,
  bounded loss, generalized risk, and revision delay. All 26 authorization
  flags are false; the six real validation rows are unavailable for Loop 34
  fitting and independent qualification, confidence is unavailable, and every
  fixture/fit/target/scoring/product-confidence operation is unauthorized.
- Loop 35 planning research is complete while the peripheral-confound
  experiment remains `Not Started`. The boundary freezes 10 confound classes,
  9 future synchronized stream classes, 13 conditions, 3 independently
  authorized stages, 24 gates, 32 refusals, and 31 false authorization fields.
  Current S21/S7 evidence cannot supply a fresh complete peripheral-control
  comparison. Missing controls fail closed, and the maximum future local claim
  is incremental brain-sensor information beyond recorded controls, not
  absolute brain origin. No fixture, acquisition, protected-data read, model,
  training, scoring, no-keypress study, device, or hardware work is authorized.
- Loop 36 planning research is complete while the geometry/reference
  experiment remains `Not Started`. The boundary freezes 6 representation
  layers, 5 modality profiles, a 24-field channel record, 12 operation classes,
  16 fixture families, 22 gates, 30 refusals, and 29 false authorization fields.
  A future real-header result can establish at most declared metadata
  compatibility. No fixture, header/signal read, alias/transform fit or apply,
  unit conversion, rereference, compensation, interpolation, source
  localization, model, training, download, stream, device, hardware, or
  equivalence claim is authorized.
- Loop 37 planning research is complete while the BIDS derivative/provenance
  experiment remains `Not Started` and unauthorized. The boundary freezes 6
  export layers, 5 artifact profiles, 15 stable-field mappings, 16 explicit
  NeuroDecodeKit extension fields, 20 fixture families, 4 stages, 24 gates, 32
  refusals, and 29 false authorization fields. NeuroToken NPZ caches and report
  artifacts remain non-standard. No fixture, exporter, derivative tree,
  validator install/run, protected payload, raw copy, release/upload, model,
  training, stream, device, or hardware operation is authorized.
- Loop 38 planning research is complete while the privacy/lifecycle experiment
  remains `Not Started` and unauthorized. The boundary freezes 5 sensitivity
  levels, 8 artifact classes, 10 lifecycle surfaces, 12 sensitive-field
  classes, 12 threats, 5 deletion-receipt levels, 24 fixtures, 4 stages, 26
  gates, 36 refusals, and 32 false authorization fields. Pseudonyms, hashes,
  embeddings, and de-identified neural data remain potentially linkable;
  unknown backups, clones, PR refs, CI artifacts, and remotes remain
  unresolved. No fixture, scanner, deletion, protected-root scan, identity
  attack, history rewrite, consent determination, release/upload, model,
  training, stream, device, or hardware operation is authorized.
- Loop 39 planning research is complete while the cross-machine reproducibility
  experiment remains `Not Started` and unauthorized. The boundary freezes 7
  qualification levels, 18 environment identity fields, 8 output classes, 6
  comparison classes, 6 future Ubuntu/macOS matrix cells, 20 fixture families,
  4 stages, 28 gates, 38 refusals, and 36 false authorization fields. The
  current repository has 2 Ubuntu-latest Python 3.12 CI profiles, 0 explicit
  cross-OS cells, 0 tracked lockfiles, no package reproducibility job, and 2
  direct `tomllib` test imports that block claiming Python 3.10 qualification.
  No fixture, environment manifest, matrix job, dependency lock, package
  build, protected payload, model, training run, independent reproducer, edge
  runtime, device, or hardware operation is authorized.
- Loop 40 planning research is complete while the edge-runtime packaging
  experiment remains `Not Started` and unauthorized. The boundary freezes 7
  qualification levels, 6 package layers, 4 unselected backend profiles, 20
  identity fields, 24 fixtures, 4 stages, 30 gates, 40 refusals, and 40 false
  authorization fields. ExecuTorch/XNNPACK is a research lead only; Loop 39
  has not qualified the reference, and no fixture, install, export, package,
  inference, profiler, simulator, app, device, or hardware operation exists.
- Loop 41 planning research is complete while the RW3 stream-to-NeuroToken
  integration experiment remains `Not Started` and unauthorized. The boundary
  freezes 6 integration layers, 7 clock views, 8 anomaly classes, 5 schedules,
  5 resume cuts, 18 hash bindings, 28 fixtures, 4 stages, 32 gates, 42 refusals,
  and 42 false authorization fields. No source chunk, fixture, preprocessing,
  adapter, state, token runtime, end-to-end latency result, stream, device, or
  hardware operation exists.
- No real recording quality, neural advantage, unseen-person generalization,
  useful EEG decoder, real-time decoding, portable-hardware, arbitrary-thought,
  or clinical result has been demonstrated.
- The repository is public. PR #1 merged the open-source community surface;
  current evidence work is carried by green PR #3 and the stacked Loop 25
  branch. Do not merge or alter visibility without explicit user approval.

## Primary task: preserve Loop 24 and make only the Loop 25 decision

For Loop 24, inspect and preserve:

- `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`;
- `docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`;
- `docs/LOOP_24_AUTHORIZATION_DECISION.md`;
- `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`;
- `registries/local_precision_runtime_contract.v0.json`;
- `tests/test_local_precision_runtime_contract.py`.

Confirm the exact float32/float16/qint8 result, 12 completed timing rounds,
failed replacement/storage-only rules, unopened qualification, runtime-cap
failure, zero forbidden counters, ignored artifacts, and parked claim boundary.
Do not rerun seed 2401, open seed 2402, change worker startup, or retune a
threshold under the same claim.

Loop 25 causal preprocessing is complete. Review the result document and
machine record, then verify that the immutable request, separate authorization,
implementation, static-first access order, measured counters, and no-rerun
boundary remain intact. Do not regenerate the fixture, reopen either partition,
or rerun the gate.

Loop 26/31/33 was preregistered, authorized once, and is now a consumed
negative result. Review
`docs/LOOP_26_SHARED_VALIDATION_RESULT.md`,
`registries/loop26_shared_validation_result.v0.json`,
`docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md`,
`docs/LOOP_26_AUTHORIZATION_DECISION.md`,
`docs/LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md`, and the Loop 26 v0
registries. Do not rerun any implementation stage, reopen validation targets,
tune after targets, increase the model, or touch source test or session 2.
Loop 48 artifact-only failure localization is preregistered in
`docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop48_failure_localization_contract.v0.json`. The leading `F5`
output-instability phenotype is descriptive and not a proven root cause. The
contract remains unimplemented and every authorization field is false. Commit,
push, test, and remotely qualify the exact contract before preparing a separate
Stage A authorization packet. That qualification is now green at `83309bf`,
and the still-false request is in `docs/LOOP_48_AUTHORIZATION_PACKET.md` and
`registries/loop48_authorization_request.v0.json`. Any implementation,
train-array/protected read, target, checkpoint, private prediction, model run,
or tuning remains closed until the exact sentence receives its own green
decision record.
The future train-only portfolio in
`docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md` and
`registries/loop48_hypothesis_portfolio.v0.json` is design research only. It
compares five potentially coexisting hypotheses from shared evidence while
physical compute stays sequential and one-threaded. Do not create its split,
fixture, static prototype, model inventory, data read, or execution from a
Stage A decision.

Loop 27 is also review-only planning evidence. Do not turn the selected S25
paths, official hashes, local MAT presence, 1 GiB cap, or roadmap status into a
download or content-open instruction. Preregistration waits for compatible
Loop 25 mechanics, a frozen Loop 26 model/control package, target isolation,
and a Loop 28 final-only decision rule.

Independently, inspect and validate the RW3 Stage A decision surface:

- `docs/RW3_PRIMARY_SOURCE_RESEARCH.md`;
- `docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`;
- `registries/replay_equivalence_contract.v0.json`;
- `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`;
- `registries/rw3_stage_a_authorization_request.v0.json`;
- `tests/test_replay_equivalence_contract.py`.

Confirm that the documents and machine contract agree on source identity,
clock views, packet anomalies, state, five schedules, 18 fixture families, 30
refusal IDs, four staged adapters, resource caps, access counters, and claim
boundaries. Confirm that the request binds the exact contract hash, 90-case
matrix, 30 refusals, caps, forbidden work, and authorization-only commit
sequence while leaving `authorized_now` false. The only permissible next
decision is whether the user separately authorizes Stage A pure-Python
synthetic replay or holds it. Registration and packet preparation alone do not.
The parked Loop 24 result cannot authorize RW3 Stage A.

## Hard boundaries

1. Do not download data, open S20, or reopen consumed S7/S21 raw arrays,
   caches, target logs, or seeds 2203, 2303, 2353, and 2401. Keep seed 2402
   unopened and do not repurpose it. Loop 25 seeds 2501 and 2502 are consumed
   for the completed mechanics gate; do not reopen, rerun, or repurpose them.
2. Do not install or import BrainFlow, LSL, MNE-BIDS, or hardware SDKs. Do not
   connect to hardware, enumerate devices, open sockets, or execute a live
   source.
3. Do not implement RW3 adapters, source chunks, fixtures, or CLI commands
   unless the user explicitly authorizes Stage A after reviewing the packet.
   Authorization must first be recorded in its own tested and pushed commit.
4. Do not rerun, retune, amend, or reopen Loop 24 under its consumed selection
   claim. Its generated artifacts stay ignored and outside Git.
5. Do not train or run a predictive model, create target text or labels,
   calculate CER/WER, or claim decoding performance.
6. Keep heavy dependencies optional. Use one CPU thread and do not create
   generated data artifacts beyond tiny documentation-validation debris.
7. Keep RW3 independent from Loop 24 precision/runtime and the
   blocked RW4 S20 acquisition packet.
8. Do not rerun Loop 25 or Loop 26/31/33, or implement/execute another Loop
   26-44 item from roadmap
   approval, packet preparation, or a broad request to continue. Loop 25 v1 is
   complete and frozen; later loops still require their own packets. A failed
   gate parks its dependent claim branch.
9. Keep Loop 26 source test and session 2 closed. The six validation targets
   are consumed; no rerun, new metric selection, model/checkpoint operation,
   training, validation prediction, or post-target analysis is authorized.
10. Keep S25 sealed. Do not hash or open its local MAT payload, download its
    FIF, inspect a header, read signal/targets, substitute S24/S22/S18, or
    prepare a transfer run from Loop 27 planning research.
11. Treat the Loop 28 final-only rule as planning research, not permission.
    Target-wide signal statistics, subject embeddings, adapters, labels,
    calibration, model/control predictions, and final targets remain sealed.
    A future calibrated result cannot be relabeled as zero-shot.
12. Treat the Loop 29 modality map and 5-10 GB envelope as planning research,
    not a device or acquisition authorization. Do not infer OPM-MEG or EEG
    behavior from cryogenic channel ablation; do not select, purchase, connect,
    import an SDK for, stream from, or qualify hardware from this prompt.
13. Treat the Loop 30 target-free replay contract as planning research, not UI
    or server authorization. Do not generate its trace, reopen consumed Loop
    23/24 artifacts, launch a browser/server, expose a file path, make a network
    request, display confidence, or imply live neural decoding from this prompt.
14. Treat Loop 31 as a consumed failed attribution conjunction. Do not reopen
    source validation, targets, caches, checkpoints, models, or an LLM; do not
    rerun an ablation, access S20/S25, or turn the zero/timing component wins
    into sensor-signal or brain-specific wording.
15. Treat the Loop 32 calibration boundary as planning research, not permission
    to select or open a participant, repurpose S25, read calibration or final
    signal/labels, run the 32-parameter adapter, train, or evaluate. Calibrated
    performance is not zero-shot, and one person is not population evidence.
16. Treat Loop 33 as a consumed failed scaling gate. Do not reopen source train
    or validation data, retrain the 18 models, rescore targets, duplicate rows
    as physical repetitions, fit a post-hoc scaling law, or acquire more data
    from this result.
17. Treat the Loop 34 confidence boundary as planning research, not permission
    to generate its fresh fixture, compute candidate scores, fit a probability
    map or threshold, open final targets, score, or expose confidence. Do not
    reuse the six source-validation rows, call stability correctness, report
    raw scores as probabilities, transfer a synthetic pass to real data, or
    hide abstention delay. The experiment is `Not Started`, confidence is
    unavailable, and all work remains unauthorized.
18. Treat the Loop 42 Q0 candidate selection as planning research, not a
    purchase, SDK, serial, device, participant, or recording authorization.
    Do not substitute Daisy or Wi-Fi, infer sensor-capture latency from
    BrainFlow timestamps, call generic ExG EEG without verified configuration,
    or promote connectivity into signal quality, decoding, home usability, or
    safety.

## Required deliverables for the next authorized milestone

1. Keep README, tracker, decision log, build notes, handoff, start-here,
   roadmap, workbook, and continuation prompt consistent with Loop 24's parked
   closeout, RW3 commit `c3d1f01`, and the
   still-unauthorized request prepared at `163ff2f`. Keep Loop 25's immutable
   `a36d97b` v0 registration, green `b6b92d8` v1 amendment, false replacement
   authorization request, the planning-only Loop 26 registry with 14 false
   authorization fields and zero protected access, the Loop 27 registry with
   18 false permissions and zero payload access, the Loop 28 registry with 21
   false permissions and zero protected access, and all 20 Loops 25-44
   execution flags consistent. Keep the Loop 32 registry at four modes, six
   budgets, one 32-parameter recommendation, 32/16/48 physical floors, 20
   gates, 26 refusals, 22 false permissions, and zero candidate or execution.
   Keep the Loop 33 registry at six nested `8, 16, 24, 32, 44, 55` prefixes,
   at most three seeds and 18 candidate fits, one prospective shared validation
   event, four conditions, 20 gates, 30 refusals, 23 false permissions, no
   physical-repetition lane, no acquisition recommendation, and zero execution.
   Keep the Loop 34 registry at seven confidence semantics, eight score/control
   roles, recommended `128/64/256` fresh synthetic partitions, 20 gates, 30
   refusals, 26 false permissions, no eligible existing real confidence
   partition, explicit unavailable confidence, and zero fixture/fit/target/
   scoring/product-confidence execution.
2. Run documentation/contract validation, local-link checks, Ruff,
   `git diff --check`, Gitleaks, and the complete unit suites. Compare with the
   313-unittest Loop 24 baseline, the 323-unittest Loop 25 v0 preregistration
   baseline, the 342-unittest Loop 25 v1 amendment baseline, the 366-unittest
   Loop 26 public closeout, and the 380-unittest Loop 27 public closeout.
3. Commit and push any future authorization-only milestone and confirm its own
   CI before implementation. Preserve unrelated files and generated debris
   outside Git.

Do not call Loop 24 a speedup, retained-accuracy, integer-only, neural,
decoding, energy, real-time, transport, or hardware result. Its engineering
gate exists and ran; its primary decision is parked.

## Loop 43 Continuation Boundary

Loop 43 planning research is complete, but its independent artifact-
reproduction challenge is `Not Started` and unauthorized. Do not create a
packet, oracle, challenge issue, workflow, fixture, outreach message,
contributor submission, adjudication, archive, DOI, badge, release, or runtime.
The future target-free NeuroToken causal-replay lane remains ineligible until
compatible Loop 37, 38, and 39 execution closeouts exist. A maintainer rerun is
repeatability, author-artifact reproduction is not scientific replication, and
one independent environment is not generalization. Continue with Loop 44
planning research only unless a narrower exact authorization is separately
prepared, committed, pushed, and green.
