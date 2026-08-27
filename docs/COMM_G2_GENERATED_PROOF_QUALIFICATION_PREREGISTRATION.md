# COMM-G2 Generated Proof Qualification Preregistration

**Date:** 2026-08-27  
**Lane:** `COMM-G2`  
**Stage:** prospective generated-only registration  
**Scientific value:** none

## Purpose

COMM-G1 is consumed at `COMM-G1-R0`. Its numerical model output cannot be
accepted because the official proof omitted registered fields from its replay
digest, did not use two isolated clean workdirs, and did not explicitly execute
two named adversarial families.

COMM-G2 is a new generated-only lane. It tests whether the same frozen
scientific analysis can be executed behind a complete, deterministic, isolated
proof boundary. It does not repair, rerun, overwrite, or upgrade COMM-G1.

## Frozen scientific core

The following COMM-G1 behavior is immutable for COMM-G2:

- six fictional participants, three sessions, four classes, and 144 rows;
- participant-held-out folds with zero held-out-person calibration;
- the exact causal four-band feature transform;
- the exact source-only ridge residualizer;
- the exact source-only no-fixed-point class rotation from Amendment 1;
- the exact compact L2 multinomial logistic family and ten conditions;
- 60 parameter updates, 60 prediction sets, and 1,440 prediction rows per
  replay;
- the exact R0-R3 thresholds and participant-consistency rule; and
- no hyperparameter, seed, feature, condition, threshold, or model selection.

The frozen module is
`src/neurodecodekit/experiments/comm_g1_generated.py`, 46,496 bytes, SHA-256
`99178d463558c27dcfe8c4346d6f47c207cb8dc60b6d45cd6ad3dab4b08fb3f4`.
COMM-G2 may call its scientific primitives but may not modify that module.

## Canonical replay proof

Two independent child processes must run in two newly created exclusive clean
workdirs. Each replay performs the full 60-update schedule. The coordinator
must compare, byte for byte:

- canonical fixture digest;
- split and capability manifests;
- fit and inference schedule ledger;
- aggregate prediction-freeze digest;
- aggregate score payload excluding runtime and RSS fields;
- router outcome; and
- complete adversarial refusal ledger.

The fixture digest must bind every row field, including cue, timing, source
sample and time bounds, sampling rate, true length, padding mask, channel names,
channel roles, available geometry, signal dtype/shape/bytes, item, participant,
session, trial, repeat, split identity, and synthetic target. Arrays must use
explicit dtype, byte order, shape, and contiguous bytes. JSON metadata must use
sorted keys and fixed separators. Missing, extra, reordered, or type-changed
fields must change the digest or refuse.

## Process and target isolation

Each replay uses separate preparation, prediction, and scoring capabilities:

1. Preparation creates target-free fold packages and a separate sealed
   synthetic target vault.
2. Prediction workers receive only five source participants' signals and
   synthetic targets plus the held-out participant's signals. They cannot open,
   derive, enumerate, or traverse the held-out target vault.
3. The coordinator freezes the complete aggregate predictions before scoring.
4. A scorer-only child receives the frozen predictions and matching synthetic
   held-out targets exactly once.
5. No model, transform, threshold, calibration, or parameter update may occur
   after target delivery.

For every fold, the proof must bind disjoint source and held-out identity
hashes, source-only fit-row hashes, zero held-out fit/calibration rows, and an
exact one-row-per-participant/item/condition prediction inventory. Probabilities
must be finite, four-class, clipped as frozen, sum to one within `1e-12`, and
contain no duplicate or missing row.

## Filesystem and resource proof

Every workdir and output parent must be a no-follow directory capability.
Temporary and final files use exclusive creation. Publication is non-replacing,
fsyncs file and directory state, and cleans only invocation-owned temporaries.
Path replacement, ancestor symlink, leaf symlink, nonregular file, clobber,
cross-workdir traversal, stale temporary, and publication-race cases must
refuse.

The qualification must explicitly execute every named adversarial family,
including `symlink_escape` and `resource_cap_breach`. Resource checks must be
prospective where possible and measured separately for each replay and for the
coordinator. A breached cap must refuse before final publication.

## Exact schedule and caps

One official COMM-G2 qualification contains exactly two full isolated replays:

| Operation | Exact maximum |
|---|---:|
| Generated rows per replay | 144 |
| Parameter updates per replay / total | 60 / 120 |
| Prediction sets per replay / total | 60 / 120 |
| Prediction rows per replay / total | 1,440 / 2,880 |
| Synthetic target deliveries | 2, one per scorer |
| Synthetic scores | 2, one per scorer |
| Post-target updates | 0 |
| Official invocations | 1 |
| Reruns | 0 |

The operation uses one active numerical job at a time, one worker per child,
and one CPU thread. Caps are 180 seconds wall time, 512 MiB peak process-tree
RSS, 80 MiB total generated input, 64 MiB private generated output, 1 MiB
public output, 96 MiB temporary disk, zero network bytes, and zero real or
private dataset bytes. The existing 20 GiB total and 10 GiB selected-raw
allowances are unchanged and unused by this lane.

## Qualification router

- `COMM-G2-R1`: both isolated replays are byte-equivalent on every registered
  deterministic surface, every proof and firewall gate passes, every named
  adversarial family refuses, and the frozen positive fixture passes the frozen
  numerical thresholds in both replays.
- `COMM-G2-R2`: proof is complete and deterministic, but the frozen numerical
  effect or participant-consistency gate fails.
- `COMM-G2-R3`: proof is complete but a shortcut/no-increment condition wins.
- `COMM-G2-R0`: any structural, isolation, target-firewall, replay, filesystem,
  resource, completeness, or refusal-family gate fails.

No COMM-G2 route has scientific value.

## Ordered gates

1. Commit, push, and remotely green this registration.
2. Implement a new COMM-G2 wrapper and CLI without changing the frozen
   scientific module.
3. Commit, push, and remotely green the exact implementation.
4. Execute the one generated qualification once.
5. Close it against this router with no rerun.

## Boundaries

This registration authorizes no current execution. It does not authorize a
dataset request, real/private path read, EEG/MEG header or signal read, target
or label delivery, real training or inference, provider call, stream, device,
hardware, release, or scientific claim. `DREYER-C5R-1-HL` remains the sole
active Tier C packet with every authority flag false.

