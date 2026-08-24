# EEGMMIDB-UG1 Unseen-Participant Generalization Authorization Packet

Date: 2026-08-24

Status: **All-false Tier C request; no network, payload, model, target, or score operation is authorized**

Machine request:

- `registries/eegmmidb_unseen_participant_generalization_authorization_request.v0.json`

## Why This Is The Next Scientific Test

The existing EEGMMIDB result is real but participant-specific: separate models
reached held-out-run balanced accuracy `0.680975` for executed movement and
`0.728014` for imagery across S004-S015. It beat no-signal, but early-cue and
frontal controls remained strong. It therefore established repeatable task
information, not unseen-person generalization, movement intention, motor-cortex
origin, or an eye-independent neural effect.

`EEGMMIDB-UG1` asks a narrower and more difficult question: can one model fitted
only on S001-S015 predict left versus right protocol condition in S016-S030,
with no held-out-person calibration, while beating frozen no-signal, timing,
derangement, temporal, and spatial controls?

The source gate runs before fresh acquisition. If source-participant LOSO is
weak, the experiment stops without downloading or opening S016-S030.

## Requested Staged Sequence

Only a fresh packet-bound maintainer decision, committed, pushed, and remotely
green, may activate this sequence. Each later barrier is mandatory.

### G: generated and mocked implementation

Implement exact cohort/path validation, sequential bounded acquisition, EDF
reading, target isolation, causal preprocessing, the single frozen model,
participant-level controls/statistics, checkpoint and prediction freezing,
isolated scoring, resource monitoring, and CLI surfaces. Qualify with generated
EDF fixtures and mocked transport only. Commit, push, and require both CI jobs
green before metadata access.

### M: metadata-only identity freeze

Request metadata for only these 36 named paths:

- S001-S003 runs 04 and 08; and
- S016-S030 runs 11 and 12.

Use only official PhysioNet `1.0.0` surfaces. Make at most 36 sequential
requests, transfer at most 2 MiB, and open no EDF body. Freeze exact paths,
sizes, and official SHA-256 values or equally immutable registered validators.
The combined payload must be at most 256 MiB. Commit, push, and require both CI
jobs green before payload access.

### S: source acquisition, LOSO gate, and checkpoint freeze

Acquire only the six missing S001-S003 run-04/run-08 files. Reuse only these
existing source-fit payloads under the fresh decision:

- six S001-S003 run-03/run-07 EDFs in
  `data/physionet_motor/eegmmidb-1.0.0`; and
- 48 S004-S015 run-03/run-04/run-07/run-08 EDFs in
  `data/physionet_motor/wo9r-eegmmidb-1.0.0`.

Those 54 existing source-fit EDFs total exactly 138,333,504 bytes. Previously
scored run-11/run-12 files and targets are forbidden. Fit the fixed execution
and imagery models and run the 15-fold leave-one-source-participant-out gate.
If execution fails, consume at R1 and request zero fresh payloads. If it passes,
freeze the two full-source checkpoints and all preprocessing, control, split,
configuration, code, and payload hashes. Commit, push, and require both CI jobs
green before fresh acquisition.

### F: fresh acquisition and target-blind prediction freeze

Acquire only S016-S030 runs 11 and 12 into a new isolated bundle. A separate
target-isolation process may read T0/T1/T2 annotations, discard T0, emit
target-free timing rows, and seal exactly 450 T1/T2 identities. Predictive code
receives signals, cue times, participant IDs, and task family, but no T1/T2
identity, target-derived exclusion, calibration statistic, normalization fit,
threshold selection, or test-time adaptation.

Generate all frozen primary and control predictions once. Publicly freeze only
hashes and aggregate completeness counts. Publish no individual prediction,
probability, target, or participant outcome. Commit, push, and require both CI
jobs green before target delivery.

### T: one frozen score

Deliver the same 450 sealed targets once and apply the frozen participant-level
router. Score execution first. Imagery may upgrade a passing execution result
but cannot rescue a failed execution result. No target-dependent update,
exclusion, threshold, seed, model, or rerun is allowed.

## Frozen Scientific Contract

The primary model is exactly:

```text
64 EEG channels -> instantaneous common-average reference
causal fourth-order Butterworth 0.5-4 Hz SOS over each continuous run
decision window [+1,+3) seconds from cue
four 500 ms means + one slope per channel = 320 features
source-only standardization
pooled shrinkage LDA, lsqr, shrinkage 0.1, equal priors
```

Execution uses source runs 03/07 and fresh run 11. Imagery uses source runs
04/08 and fresh run 12. There is one candidate and no hyperparameter search.

The source execution gate requires macro balanced accuracy at least `0.57`, a
margin at least `0.07` over the stronger no-signal/timing control, at least
10/15 participants above chance, and exact one-sided participant sign-flip
`p <= 0.05`.

The fresh execution gate requires pooled and macro balanced accuracy at least
`0.60`, margin at least `0.10` over the stronger no-signal/timing control,
11/15 participants above chance, exact one-sided participant sign-flip
`p <= 0.01`, margin at least `0.02` over every frozen derangement, and paired
participant sign-flip `p <= 0.05` against those controls.

Frozen conditions are whole-head primary, equal-prior no-signal, timing-only,
zero-signal, channel permutation, nonwrapping event displacement, source-label
derangement, pre-cue, early-cue, central, frontal, and occipital views.

## Frozen Routes

| Route | Maximum meaning |
|---|---|
| `EEGMMIDBUG1-R0` | Integrity, identity, payload, firewall, freeze, or resource refusal. |
| `EEGMMIDBUG1-R1` | Source LOSO execution gate failed; no fresh payload was requested. |
| `EEGMMIDBUG1-R2` | Fresh execution failed one or more primary/control gates. |
| `EEGMMIDBUG1-R3` | Strict zero-calibration protocol-condition prediction passed for 15 unseen execution participants. |
| `EEGMMIDBUG1-R4` | The same strict result also passed for imagery. |

Every reached route is terminal. R2-R4 consume the one final target event.

## Resource And Safety Limits

- one CPU thread, one worker, one numerical job;
- at most 36 metadata requests and 2 MiB metadata transfer;
- at most 36 EDF payload requests and 256 MiB new payload transfer;
- at most 512 MiB incremental disk and 128 MiB private derivatives;
- at most 2 MiB public artifacts and 1 GiB peak RSS;
- at most 300 parameter-update fits and 640 prediction sets;
- at least 2 GiB free disk before payload stages;
- zero retries, reruns, substitutions, or post-target updates; and
- cleanup only of temporary files created by the active invocation.

No `.event` sidecar, other participant/run/dataset, old final target, S20,
S21, IACKD, SpanishBCBL, raw FIF/MAT, larger/deep/pretrained model, language
model, provider, stream, device, hardware, release, or individual protected
output is requested.

## Current Authorization State

Every authority flag and operation counter is false or zero. This packet and a
non-scope-changing proof closeout must each be committed, pushed, and remotely
green. Only then may `EEGMMIDB-UG1` be identified as the sole active Tier C
packet. A fresh unambiguous maintainer message after that identification may
authorize this unchanged packet by reference. No earlier `continue`,
`approve`, or `lets go` is retroactive authority.

Engineering capability requested: a one-shot, zero-calibration,
participant-independent EEG evaluation pipeline with an early source stop gate
and frozen no-signal, timing, derangement, temporal, and spatial controls.

Scientific claim not established: this all-false request opens no real data,
fits no model, freezes no prediction, and scores no target, so it establishes
no unseen-person result, neural advantage, movement intention, motor-cortex
origin, eye-independent signal, thought or language decoding, or live result.
