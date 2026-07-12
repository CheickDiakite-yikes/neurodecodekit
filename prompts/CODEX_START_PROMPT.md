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
- `docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop26_research_boundary.v0.json`
- `docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md`
- `registries/loop27_research_boundary.v0.json`
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
  devices, hardware, and Loops 25-44 remain unauthorized.
- Loop 25 causal preprocessing was preregistered at `a36d97b`, then superseded
  before authorization by anti-alias amendment v1 at green commit `b6b92d8`.
  The current contract freezes a dedicated causal anti-alias SOS, 65,537
  response points, 23 alias probes, seeds 2501/2502, 7 schedules, 10 resume
  cuts, 3 future-mutation cuts, 45 refusals, 23 access counters, and the same
  8-MiB/45-second caps. Its replacement request says `authorized_now: false`;
  both seeds are unopened and no Loop 25 coefficient, runtime, or payload exists.
- Loops 25-44 are now a detailed planning-only queue: exactly 20 contiguous
  rows across five phases, with source bindings, controls, metrics, acceptance
  gates, stop rules, dependencies, resource caps, and 20 false execution flags.
  Loop 25 is `Amended Preregistration`; Loop 26 planning research is complete
  while its experiment remains `Not Started`; Loop 27 planning research has
  selected S25 metadata while preregistration remains blocked; Loops 28-44 are
  `Not Started`; all 20 execution flags remain false.
- Loop 26's planning boundary recommends a 2,908-parameter causal candidate, a
  2,884-parameter linear comparator, six controls, and exact enumeration of all
  64 paired sign assignments over six reserved source-validation sentences.
  All 14 authorization fields are false. No Loop 26 cache content, target,
  model, checkpoint, training, validation prediction, source-test row, or
  session-2 evidence was opened; no preregistration or authorization exists.
- Loop 27 planning research at `b3d61b6` selects S25 session 2 block 2 as the
  smallest eligible strict MEG metadata pair: two files totaling
  1,009,939,983 bytes. S23 is officially excluded and S20 remains a separate
  EEG cohort. All 18 permissions are false; no preregistration, acquisition
  request, download, local MAT payload hash, header, signal, target, model,
  training, final open, or backup substitution exists.
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

Loop 25 causal preprocessing has completed its superseding preregistration at
`b6b92d8`. Review the anti-alias audit, immutable v1 contract, and
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`. The only permissible numbered
decision is to authorize the exact v1 target-free implementation, amend it
again before authorization, or hold. Packet preparation, roadmap approval, and
this continuation prompt do not authorize implementation. Exact authorization
must first become its own tested, pushed, remotely green v1 authorization-only
commit, after which the static filter gate must pass before seed 2501 opens.

Loop 26 is review-only planning evidence until Loop 25 closes compatibly. Do
not turn `docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md`, its roadmap status, or this
prompt into an experiment contract. A future Loop 26 preregistration must
separately freeze architecture, controls, statistics, seeds, access order, and
resources before any exact authorization can permit real-cache, target,
training, model, or one-time validation access.

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
   unopened and do not repurpose it. Keep Loop 25 seeds 2501 and 2502 unopened
   until a separate v1 authorization-only commit is pushed and green. Even
   after authorization, the static filter-design gate must pass before either
   seed can be opened.
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
8. Do not implement or execute a Loop 25-44 item from roadmap approval, packet
   preparation, or a broad request to continue. Loop 25 v1 is frozen but still
   awaits its exact decision; v0 is immutable history, and later loops still
   require their own packets. A failed gate parks its dependent claim branch.
9. Keep Loop 26 source test and session 2 closed. Planning research does not
   authorize preregistration, implementation, real-cache or target reads,
   model/checkpoint operations, training, validation predictions, or metrics.
10. Keep S25 sealed. Do not hash or open its local MAT payload, download its
    FIF, inspect a header, read signal/targets, substitute S24/S22/S18, or
    prepare a transfer run from Loop 27 planning research.

## Required deliverables for the next authorized milestone

1. Keep README, tracker, decision log, build notes, handoff, start-here,
   roadmap, workbook, and continuation prompt consistent with Loop 24's parked
   closeout, RW3 commit `c3d1f01`, and the
   still-unauthorized request prepared at `163ff2f`. Keep Loop 25's immutable
   `a36d97b` v0 registration, green `b6b92d8` v1 amendment, false replacement
   authorization request, the planning-only Loop 26 registry with 14 false
   authorization fields and zero protected access, the Loop 27 registry with
   18 false permissions and zero payload access, and all 20 Loops 25-44
   execution flags consistent.
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
