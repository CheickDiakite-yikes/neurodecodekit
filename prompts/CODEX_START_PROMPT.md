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
- RW3's replay/live-source-equivalence protocol is frozen at commit `c3d1f01`.
  Five schedules, 18 future fixture families, 30 exact refusal IDs, and four
  sequential adapter stages are registered; no source chunk or adapter exists.
- Commit `163ff2f` prepares a hash-bound Stage A packet covering 90 proposed
  cases and all 30 refusals. Its machine request says `authorized_now: false`;
  the packet is not authorization.
- Loop 24 is preregistered at commit `186bb6f`. Three exact CPU candidates,
  fresh target-free seeds 2401/2402, 12 balanced timing rounds, 30 refusal IDs,
  correctness/resource/claim gates, and nine dependency-free invariants are
  frozen. Every execution flag is false; no fixture, candidate, checkpoint
  read, inference, benchmark, profiler, energy, or qualification run exists.
- No real recording quality, neural advantage, unseen-person generalization,
  useful EEG decoder, real-time decoding, portable-hardware, arbitrary-thought,
  or clinical result has been demonstrated.
- The repository reports public. PR #1 merged the open-source community surface
  through `e5d89ed`; green draft PR #2 carries the latest evidence closeout and
  canonical license-text repair. Do not merge or alter visibility without
  explicit user approval.

## Primary task: review two independent decisions; do not implement either

For Loop 24, inspect and validate:

- `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`;
- `docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`;
- `registries/local_precision_runtime_contract.v0.json`;
- `tests/test_local_precision_runtime_contract.py`.

Confirm the exact float32 eager, explicit CPU float16, and dynamic-qint8 QNNPACK
candidates; frozen reference hashes; fresh target-free seeds 2401/2402; 12
balanced timing rounds; numerical, decoder, storage, RSS, timing, access, and
claim gates; 30 refusal IDs; and false execution flags. The only permissible
next Loop 24 decision is explicit authorization using the exact sentence in the
preregistration, an amendment, or a hold. General continuation is not
authorization.

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
Authorizing either Loop 24 or RW3 Stage A cannot authorize the other.

## Hard boundaries

1. Do not download data, open S20, or reopen consumed S7/S21 raw arrays,
   caches, target logs, or seeds 2203, 2303, and 2353.
2. Do not install or import BrainFlow, LSL, MNE-BIDS, or hardware SDKs. Do not
   connect to hardware, enumerate devices, open sockets, or execute a live
   source.
3. Do not implement RW3 adapters, source chunks, fixtures, or CLI commands
   unless the user explicitly authorizes Stage A after reviewing the packet.
   Authorization must first be recorded in its own tested and pushed commit.
4. Do not implement a Loop 24 candidate or CLI, generate its fixture, load or
   convert its checkpoint, run inference, benchmark, profile, or measure energy
   unless the user explicitly authorizes Loop 24 using the frozen scope.
5. Do not train or run a predictive model, create target text or labels,
   calculate CER/WER, or claim decoding performance.
6. Keep heavy dependencies optional. Use one CPU thread and do not create
   generated data artifacts beyond tiny documentation-validation debris.
7. Keep RW3 independent from Loop 24 precision/runtime and the
   blocked RW4 S20 acquisition packet.

## Required deliverables for this review milestone

1. Keep README, tracker, decision log, build notes, handoff, start-here,
   roadmap, workbook, and continuation prompt consistent with Loop 24 commit
   `186bb6f`, RW3 commit `c3d1f01`, and the still-unauthorized request prepared
   at `163ff2f`.
2. Run documentation/contract validation, local-link checks, Ruff,
   `git diff --check`, Gitleaks, and the complete unit suites. Compare with the
   pre-Loop-24 268-unittest / 265-pytest baseline and the registered 277/
   274-test post-contract counts.
3. Commit and push the coherent documentation milestone and refresh draft PR
   #2. Preserve unrelated files and generated debris outside Git.

Do not call Loop 24 or RW3 implemented or runtime-validated. The current
milestone proves only that two future synthetic experiments and their separate
decision boundaries were frozen before candidate, transport, data, or hardware
access.
