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
- Loops 25-44 are now a detailed planning-only queue: exactly 20 contiguous
  rows across five phases, with source bindings, controls, metrics, acceptance
  gates, stop rules, dependencies, resource caps, and 20 false execution flags.
  Loop 25 is the next numbered candidate, but the queue authorizes no operation.
- No real recording quality, neural advantage, unseen-person generalization,
  useful EEG decoder, real-time decoding, portable-hardware, arbitrary-thought,
  or clinical result has been demonstrated.
- The repository reports public. PR #1 merged the open-source community surface
  through `e5d89ed`; green draft PR #2 carries the latest evidence closeout and
  canonical license-text repair. Do not merge or alter visibility without
  explicit user approval.

## Primary task: preserve Loop 24 and prepare only the next authorized decision

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

Loop 25 causal preprocessing is the next numbered planning candidate. Before
any Loop 25 implementation or execution, require a dedicated preregistration
that binds target-free fixtures, transform state, chunk schedules, timestamps,
future-context tests, tolerances, resources, access counters, refusals, and an
exact authorization sentence. Roadmap approval and this continuation prompt do
not authorize that work.

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
   unopened.
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
8. Do not implement or execute a Loop 25-44 item from roadmap approval or a
   broad request to continue. Freeze and authorize the loop-specific packet
   first; a failed gate parks its dependent claim branch.

## Required deliverables for the next authorized milestone

1. Keep README, tracker, decision log, build notes, handoff, start-here,
   roadmap, workbook, and continuation prompt consistent with Loop 24's parked
   closeout, RW3 commit `c3d1f01`, and the
   still-unauthorized request prepared at `163ff2f`. Keep the Loops 25-44
   planning-only contract and all 20 false execution flags consistent too.
2. Run documentation/contract validation, local-link checks, Ruff,
   `git diff --check`, Gitleaks, and the complete unit suites. Compare with the
   293-unittest / 290-pytest authorization-only baseline and the 313-unittest /
   310-pytest Loop 24 implementation baseline.
3. Commit and push any future authorization-only milestone and confirm draft PR
   #2 CI before implementation. Preserve unrelated files and generated debris
   outside Git.

Do not call Loop 24 a speedup, retained-accuracy, integer-only, neural,
decoding, energy, real-time, transport, or hardware result. Its engineering
gate exists and ran; its primary decision is parked.
