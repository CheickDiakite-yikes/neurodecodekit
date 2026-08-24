# EEGMMIDB-UG1 Unseen-Participant Generalization Authorization Decision

Date: 2026-08-24

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both CI jobs are green**

Machine decision:

- `registries/eegmmidb_unseen_participant_generalization_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `EEGMMIDB-UG1` as the sole active Tier C packet and
reported the exact request/proof commits, both green CI runs, staged scope,
resource envelope, scientific ceiling, and fresh-decision requirement, the
maintainer's next message was exactly:

```text
continue
```

Those eight UTF-8 bytes have SHA-256:

```text
e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad
```

Under the approved short-form packet rule, this message authorizes only the
unchanged remotely green UG1 packet by reference. It does not fabricate a long
authorization sentence, infer a positive outcome, or expand any participant,
run, file, target, model, control, resource, retry, route, release, or claim.

## Exact Green Packet

```text
request commit:       c642d90b646ff32c6d83e648f7d7779810605e11
request CI:           32690289547
request Base job:     97322606634
request Optional job: 97322606501
proof commit:         9117b1db343be38248944c24e3d93cafc4058d98
proof CI:             32690987778
proof Base job:       97324487895
proof Optional job:   97324488042
```

The decision binds twelve immutable artifacts totaling 67,923 bytes with
canonical artifact-set SHA-256:

```text
f602c3dd10419050361c9d3b0b98c8216bd0268cc183a202b59d4b98b026e2e8
```

## Delayed Effect

Recording this decision performs zero network, retained-data, payload, EDF,
signal, annotation, target, label, model, prediction, score, release, or claim
operation. It becomes effective only after this exact decision commit is
pushed and both required CI jobs pass.

Before that proof, generated implementation is closed. Real metadata and every
later real-data stage remain closed even after this decision until their
registered preceding barriers pass.

## Fail-Closed Pre-Execution Review

Two independent target-free reviews completed before this decision was
committed. They found that the authorized maximum scope is clear, but several
implementation-critical details are not yet reproducibly frozen:

- the success router does not yet make every named temporal and spatial control
  conjunctive;
- participant identity is available for grouping but is not explicitly barred
  from predictor transformations;
- the prediction-freeze serialization, row order, and scorer verification are
  underspecified;
- exact imagery completeness and several deterministic control transforms are
  not fully enumerated; and
- causal filter state, channel views, early-window bins, checkpoint format, and
  resource-enforcement semantics need exact definitions.

The short-form authorization remains valid for the unchanged maximum packet,
but the ambiguity policy is fail closed. Even after this decision becomes
remotely green, Stage G remains blocked until a hash-changing, additive,
non-scope-expanding amendment freezes those details, is committed and pushed,
and passes both CI jobs. That amendment may only narrow or clarify the packet;
it may not add a participant, run, file, operation, model, request, byte, retry,
route, release, or claim.

## Authorized Sequence After Green Decision And Amendment

### G: generated and mocked implementation

Only after the decision and narrowing amendment are both remotely green,
implement additive, optional-dependency-safe UG1 modules and CLI surfaces for:

- exact participant/run/path and split validation;
- sequential bounded acquisition with mocked transport;
- generated EDF/header/channel/geometry/annotation fixtures;
- target isolation and leakage refusal;
- causal preprocessing and deterministic feature extraction;
- the one fixed shrinkage-LDA family;
- 15-fold participant LOSO and its stop route;
- all twelve frozen primary/control conditions;
- checkpoint and prediction freeze hashing;
- participant-level exact statistics and one-delivery scoring; and
- output, overwrite, symlink, mutation, resource, and no-rerun guards.

Qualification may use generated fixtures and mocked transport only. It may not
stat, list, resolve, hash, open, or parse any retained/real/ignored data root.
It must be committed, pushed, and remotely green before Stage M.

### M: metadata-only identity freeze

Only after Stage G is green, make at most 36 sequential metadata requests for
exactly S001-S003 runs 04/08 and S016-S030 runs 11/12 on official PhysioNet
v1.0.0 surfaces. Transfer at most 2 MiB and open zero EDF body bytes. Freeze
path, exact size, and official SHA-256 or an equally immutable registered
validator. The combined payload must not exceed 256 MiB. Commit and remotely
green the inventory before Stage S.

### S: source-only execution

Only after Stage M is green, acquire the six missing S001-S003 run-04/run-08
EDFs and open only the 54 named existing source-fit EDFs plus those six new
source files. Previously scored run-11/run-12 files are forbidden.

Run exactly the frozen source extraction, controls, and 15-fold source LOSO.
If execution fails its complete source gate, consume at R1 and request zero
fresh-participant payloads. If it passes, fit the two full-source models and
freeze checkpoint, scaler, channel order, preprocessing, source split,
configuration, code, control, and payload hashes. Commit and remotely green
that checkpoint before Stage F.

### F: fresh target-blind prediction freeze

Only after Stage S is green, acquire the thirty S016-S030 run-11/run-12 EDFs
into one new isolated bundle. A target-isolation process may parse annotations,
discard T0, publish target-free event timing rows, and seal exactly 450 T1/T2
targets: 225 execution and 225 imagery rows across exactly fifteen participants
per task. Participant identity may be used only by the orchestration and scorer
for completeness, grouping, and participant-level inference; it may not enter a
predictor, feature, normalization, model, threshold, or condition transform.
Predictive code may not receive target identity or any held-out-person fit,
calibration, exclusion, threshold, normalization, selection, or update.

Produce all frozen primary and control predictions once. Commit only aggregate
hashes and completeness publicly, with no individual prediction, probability,
target, or participant outcome. Commit and remotely green the prediction
freeze before Stage T.

### T: one target delivery and score

Deliver the same sealed targets once. Score execution first using participant-
macro balanced accuracy and the frozen exact sign-flip tests. Imagery may
upgrade a passing execution result but cannot rescue failure. No target-derived
change, rerun, additional model, threshold, seed, exclusion, or amendment is
authorized.

## Fixed Resource Envelope

```text
CPU threads / workers / jobs: 1 / 1 / 1
metadata requests / bytes:    <= 36 / <= 2 MiB
payload requests / bytes:     <= 36 / <= 256 MiB
incremental disk:             <= 512 MiB
private derivatives:          <= 128 MiB
public artifacts:             <= 2 MiB
peak RSS:                     <= 1 GiB
parameter-update fits:        <= 300
prediction sets:              <= 640
free disk before payload:     >= 2 GiB
target deliveries / scores:   1 / 1
retry / rerun / update:       0 / 0 / 0
```

Cleanup is restricted to temporary files created by the active invocation.
No existing file, unrelated project, consumed result, or user artifact may be
deleted, renamed, overwritten, or repaired.

## Explicitly Not Authorized

No `.event` sidecar; source run 11/12; participant outside S001-S030; other
run, file, dataset, or substitution; S20, S21, IACKD, SpanishBCBL, raw FIF or
MAT; row-random split; held-out-person calibration; target-derived selection;
larger, deep, pretrained, foundation, or language model; provider; RW3; stream;
device; hardware; publication or release; individual protected output; retry;
rerun; result-dependent amendment; post-target amendment; or scientific claim
above R4 is authorized.

Even R4 may establish only zero-calibration left/right EEGMMIDB protocol-
condition prediction across fifteen unseen participants. It cannot establish
movement intention, motor-cortex origin, EEG information beyond eyes/visual or
peripheral signals, thought/language decoding, live decoding, portable
hardware, or clinical use.

## Next Gate

Commit, push, and green this exact decision. Then freeze, commit, push, and
green the pre-execution narrowing amendment. Only then implement and run the
sole generated/mock Stage G qualification. Do not begin Stage M until the
exact Stage G implementation/result is also committed, pushed, and remotely
green.

Engineering capability authorized after the green decision and amendment: one
fully staged, target-firewalled unseen-participant EEG experiment may advance
through exact green barriers and stop before fresh acquisition if source
transfer is weak.

Scientific claim not established: this decision is authorization, not a model
result, and establishes no neural advantage or unseen-person generalization.
