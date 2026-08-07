# Prompt to continue NeuroDecodeKit in Codex

Continue NeuroDecodeKit from the current branch. Before editing, inspect the
branch, git status, current tests, optional dependency versions, open pull
requests, and these files:

- `AGENTS.md`
- `README.md`
- `START_HERE.md`
- `CONTRIBUTING.md`
- `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md`
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
- `docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop48_failure_localization_contract.v0.json`
- `docs/LOOP_48_AUTHORIZATION_PACKET.md`
- `registries/loop48_authorization_request.v0.json`
- `docs/LOOP_48_AUTHORIZATION_DECISION.md`
- `docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md`
- `registries/loop48_failure_localization_result.v0.json`
- `docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md`
- `registries/loop48_hypothesis_portfolio.v0.json`
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
- `docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md`
- `registries/foundation_model_decoder_strategy.v0.json`
- `docs/FOUNDATION_MODEL_BRIDGE_V0.md`
- `registries/foundation_model_bridge_v0.json`
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
- The additive decoder direction uses a compact causal sensor adapter followed
  by frozen `gpt-5.6-sol`. Only the FM-0 synthetic no-call bridge is eligible;
  full `FM-A02` must eventually beat CTC-only and fixed item-deranged evidence
  under the same model. FM-0 is implemented: 7,327 synthetic input bytes
  compile into 12 plans and 34,349 bytes with no provider transport. No API
  credential, provider call, protected row, target, score, or fine-tuning is
  authorized by that implementation.
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
Loop 48 artifact-only failure localization is complete at its one-shot Stage A
boundary. Read `docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md` and
`registries/loop48_failure_localization_result.v0.json`: four exact committed
aggregate JSON artifacts totaling 155,545 bytes selected descriptive `F5`
output-instability in `0.016568875` seconds at 23,429,120-byte peak RSS. It is
not a proven root cause. Authorization commit `5bae880` and implementation
commit `ca21539` were remotely green before execution. The result is consumed;
do not rerun, tune thresholds or seeds, read ignored/protected payloads, reopen
targets, or increase the model.
The train-only portfolio in
`docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md` and
`registries/loop48_hypothesis_portfolio.v0.json` preserves the green
five-hypothesis starting point. The additive research in
`docs/LOOP_48_HYPOTHESIS_DISCRIMINATION_RESEARCH.md` and
`registries/loop48_hypothesis_discrimination.v0.json` narrows `H1` to the exact
fixed recipe, adds `H6` for data quantity/diversity, and routes the orthogonal
`T1` shortcut threat to Loop 35. Its separately authorized Stage B is now
complete and consumed. Read `docs/LOOP_48_STAGE_B_RESULT.md`,
`registries/loop48_stage_b_prediction_freeze.v0.json`, and
`registries/loop48_train_only_discrimination_result.v0.json`. The primary
candidate reached macro CER `0.953566` versus prior `0.822045`. All six full-
size causal and linear probes were finite and stable but none cleared its prior,
supporting `H4` stable nonseparability. Fixed-shift `H3` has evidence against
it; `H1/H2/H5/H6` remain unresolved. Freeze commit `00215b1` passed both CI
workflows before one 11-target score. Applied route `L50-R05` parks S24
acquisition for this model family. Do not rerun Stage B, tune from the check
rows, acquire S24, substitute a participant, open S25, or implement a
protected post-outcome repair from a broad continuation request. Read
`docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md` and
`registries/loop48_stage_c_representation_repair_research.v0.json` for the
frozen `R1` temporal-context hypothesis, then read
`docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md` and
`registries/loop48_stage_c_synthetic_result.v0.json`. The one synthetic gate is
consumed: the 7,692-parameter, 470 ms causal candidate reached CER `0.433333`
and `1/8` exact versus ablation CER `1.000000`. Its `0.566667` relative CER
improvement and mechanics checks passed, but both absolute gates failed. Stage
C is parked with no rerun or post-final tuning. Do not stat, hash, or read the
S21 cache; do not use real targets, S24, or S25; and do not treat the synthetic
contrast as a neural or decoding result. The implementation lives in
`docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md` and
`registries/loop48_stage_c_synthetic_implementation.v0.json`. No protected
Stage C contract or further real-data/model operation is open.

Loop 27 is also review-only planning evidence. Do not turn the selected S25
paths, official hashes, local MAT presence, 1 GiB cap, or roadmap status into a
download or content-open instruction. Preregistration waits for compatible
Loop 25 mechanics, a frozen Loop 26 model/control package, target isolation,
and a Loop 28 final-only decision rule.

Loop 53 fresh S20 acquisition is now consumed and passed:

- `docs/LOOP_53_ACQUISITION_RESULT.md`;
- `registries/loop53_acquisition_result.v0.json`;
- `docs/LOOP_53_ACQUISITION_IMPLEMENTATION.md`;
- `registries/loop53_acquisition_implementation.v0.json`;
- `tests/test_loop53_acquisition_result.py`.

Authorization `2a47bbc` and implementation `8ec5b1b` were separately remotely
green before the one invocation. All four files and 96,090,264 bytes matched;
runtime was 3.629499 seconds, peak RSS 63,225,856 bytes, peak incremental disk
102,035,529 bytes, and every forbidden counter zero. The gate has no rerun.
Do not reopen, parse, interpret, split, model, or score S20 from this result.
Stop before any Loop 54 content stage.

Loop 54 planning research is complete and reviewable at:

- `docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md`;
- `registries/loop54_eeg_trial_geometry_research.v0.json`;
- `tests/test_loop54_eeg_trial_geometry_research.py`.

Planning commit `aec440a` defines L54-A VHDR-only metadata without MNE or
sibling resolution, L54-B target-blind VHDR+EEG quality with all channels
retained, L54-C isolated target-bearing VMRK+MAT reconciliation, and L54-D
aggregate closeout. It requires at least 48 unique performed trials, treats the
trial rather than each key window as the future inference unit, and creates no
split or model. The committed Loop 19 extractor remains historical evidence but
is ineligible for this future claim path because it co-loads annotations, MAT,
and signal, excludes EOG-named channels, and writes plaintext labels. Loop 53
has completed cleanly; each real L54-A/B/C stage still needs a separate exact
Tier C sequence. The newer L54-A contract freezes this order: green contract,
green exact decision, synthetic-only implementation, green implementation, then
one real execution. Do not implement or open any real Loop 54 stage from the
older planning packet alone.

L54-A is now prospectively frozen at registration commit `c114623` in:

- `docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md`;
- `registries/loop54_stage_a_vhdr_contract.v0.json`; and
- `tests/test_loop54_stage_a_vhdr_contract.py`.

It binds exactly one 11,705-byte VHDR, a standard-library parser, no sibling
resolution, 18 gates, 22 refusals, one content open, one registered execution,
one thread/worker, 30 seconds, 256 MiB RSS, and 1 MiB output. Registration CI
`31127199848` was cancelled before any test step during the Actions outage; a
replacement run over exact commit `c114623` must become green before the exact
authorization request is frozen. Do not stat the local path, implement the real
parser, or open S20 from the preregistration alone.

Loop 55 planning research is also complete and reviewable at:

- `docs/LOOP_55_PRIMARY_SOURCE_RESEARCH.md`;
- `registries/loop55_eeg_neural_effect_research.v0.json`;
- `tests/test_loop55_eeg_neural_effect_research.py`;
- `docs/LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md`;
- `registries/loop55_ai_research_policy.v0.json`;
- `fixtures/loop55_ai_synthetic_proposal.v0.json`;
- `tests/test_ai_research_policy.py`.

Planning commit `f3158c7` separates causal pre-keypress performed-hand evidence
from harder causal 29-class performed-key evidence. Performed action is the
primary target; intended sentence text is secondary. The published
`[-200,+300] ms` keypress-centered window is a noncausal diagnostic only. A
future gate needs at least 48 Loop 54-qualified trials, one grouped trial-level
split, one compact causal family at `<=10,000` parameters, at most 12 fits,
twelve matched no-signal/timing/corruption/peripheral conditions, exact paired
final-trial tests, and a committed, pushed, remotely green prediction freeze
before final targets open once. No Loop 55 split, target, implementation,
model, training, inference, or score is authorized. Do not call any future
hand-only pass key decoding, or any centered-window pass causal or real time.
Documentation-sync commit `8efcb17` passed push CI `29473032843` and PR #33 CI
`29473045583`; Base Python and Optional Neuro Readers passed in both.

The additive AI policy is implemented at policy commit `8855fae` and code
commit `bd52cce`. Its only eligible phase validates synthetic JSON proposals
against one fixed causal family, exact hyperparameter and resource menus,
canonical SHA-256 identities, and zero protected-access counters. It performs
no AI-service call and no model operation. A future real agent may receive only
aggregate train-inner summaries under an exact post-Loop-54 preregistration;
never provide raw S20, individual labels/predictions, intended text,
selection/final outcomes, private paths, or claim authority. Do not treat the
synthetic guard as Loop 55 execution permission or scientific evidence.
Historical-hash repair `f50be96` passed push CI `29621564301`; it keeps the
consumed Loop 53 CLI hash historical while verifying that command remains
present. Final local qualification passes 1,087 tests with 3 expected skips.

The additive current-strategy review is in:

- `docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`;
- `registries/open_eeg_rd_strategy.v0.json`; and
- `tests/test_open_eeg_rd_strategy.py`.

It retains the compact specialist-first path and prospectively adds a
23,248,224-byte public left/right motor-execution positive control, one
public-data-selected classical baseline, a causal motor-physiology assay, and
local-first contributor receipts. No PhysioNet payload, S20 path, target,
model, checkpoint, training, inference, score, or upload was accessed.
Foundation models and generative EEG imputation remain separate later lanes.
The strategy is not a preregistration or Tier C decision; do not download the
public prospect or change frozen Loop 54/55 artifacts from it alone.

The additive `CML-v0` architecture research is in:

- `docs/LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md`;
- `registries/loop55_causal_motor_lattice_research.v0.json`; and
- `tests/test_loop55_causal_motor_lattice_research.py`.

It selects a source-independent compact hypothesis with potential, causal mu,
and causal beta branches; rank-8 spatial mixers; a 24-dimensional bottleneck;
and a physical 29-key lattice whose hand output is an exact probability
marginal. The 64-channel/18-primitive reference has 4,535 parameters. The
qualification ladder now separates PhysioNet laterality from a future EEG+EMG
pre-movement timing control. This is architecture research only: synthetic
implementation, public payload access, Loop 54 content, S20 model work, and
claim promotion remain unauthorized. Do not infer execution permission from
the selected hypothesis.

Loop 56 cross-modality accessibility planning research is complete and
reviewable at:

- `docs/LOOP_56_PRIMARY_SOURCE_RESEARCH.md`;
- `registries/loop56_cross_modality_accessibility_research.v0.json`;
- `tests/test_loop56_cross_modality_accessibility_research.py`.

It freezes five verdict classes, 12 non-skippable capability levels, 18
comparison dimensions, 16 claim fields, 28 gates, 34 refusals, and a 12-part
at-home conjunction. Current local tiny MEG and historical EEG prediction
evidence is negative but unmatched. The fresh S20 byte bundle is now local
after one opaque acquisition-only pass, but its header, signal, trial, target,
and neural evidence remain unavailable because content interpretation is still
closed.
Keep continuous input, causal incremental output, measured end-to-end latency,
device mechanics, repeated home feasibility, and clinical utility separate.
The final verdict is `Not Started`, Loop 55 result dependent, and requires an
exact aggregate allowlist plus a separate exact Tier C claim decision. Do not
open payloads, targets, predictions, checkpoints, models, or scores for Loop 56.
Planning commit `6583ca3` passed push CI `29586877054` and PR #34 CI
`29586915269`; Base Python and Optional Neuro Readers passed in both.

Independently, RW3 Stage A remains a separate pending decision surface:

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
sequence while leaving `authorized_now` false. Registration and packet
preparation alone do not authorize RW3. The parked Loop 24 result and any Loop
53 decision cannot authorize RW3 Stage A.

## Hard boundaries

1. Do not download more data, reopen or interpret S20, or reopen consumed S7/S21 raw arrays,
   caches, target logs, or seeds 2203, 2303, 2353, and 2401. Keep seed 2402
   unopened and do not repurpose it. Loop 25 seeds 2501 and 2502 are consumed
   for the completed mechanics gate; do not reopen, rerun, or repurpose them.
   Loop 53 passed once and is consumed with no rerun.
   Loop 54 planning is complete and L54-A is preregistered, but every real VHDR,
   EEG, VMRK, and MAT content stage remains separately unauthorized. Loop 55
   planning is complete but remains Loop 54 dependent and experimentally `Not
   Started`; it authorizes no split, target, model, training, inference, or
   score. Loop 56 planning is complete but its aggregate-only final verdict
   remains Loop 55 result dependent, `Not Started`, and separately unauthorized;
   it authorizes no payload, score recomputation, device, home, release, or
   scientific-claim action.
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
7. Keep RW3 independent from Loop 24 precision/runtime and the consumed Loop 53
   S20 result. The historical broad RW4/S20 packet is superseded for
   future S20 work and grants no permission.
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
   still-unauthorized request prepared at `163ff2f`. Keep Loop 53's exact
   96,090,264-byte four-file pass, measured caps, zero forbidden counters,
   consumed no-rerun state, and uninterpreted-payload boundary consistent. Keep
   Loop 54's four-stage VHDR/EEG/VMRK+MAT firewall, 48-trial floor, 22 gates,
   30 refusals, and zero real-stage access consistent. Keep Loop 55's ordered
   causal hand/key endpoints, performed-action target, noncausal centered
   diagnostic, twelve-condition control matrix, trial-level exact inference,
   at-most-12-fit and 10,000-parameter ceilings, one-shot target order, and
   false execution flags consistent. Keep its additive AI policy at synthetic-
   only validation, at most four future proposal rounds inside the same 12-fit
   total, and zero real/protected/model counters. Keep
   Loop 25's immutable
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
