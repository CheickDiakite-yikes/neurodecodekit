# BNCI-C3C5-1 Cross-Participant EEG-Gain Authorization Packet

Date: 2026-08-24

Status: **All-false Tier C request; no generated implementation, network,
payload, MAT parse, signal, target, model, prediction, score, release, or claim
operation is authorized**

Machine request:

- `registries/bnci_2014_001_cross_participant_eeg_gain_authorization_request.v0.json`

## Why This Is The Next Scientific Test

NeuroDecodeKit's strongest real positive result is still participant-specific:
the compact EEGMMIDB model recovered held-out-run protocol-condition information
across 12 people, but its early-cue and frontal controls were strong. It did not
test a completely unseen person or show that EEG added information beyond a
recorded ocular comparator.

`BNCI-C3C5-1` directly targets those two limitations on an independent public
dataset. It uses nine fully isolated held-out-participant folds and asks whether
scalp EEG predicts four classes with zero calibration. In the same frozen run,
it asks whether adding EEG improves held-out-person log loss over both recorded
EOG alone and an equally sized fusion carrying deranged EEG.

This is not a retry, repair, resume, fallback, or substitution for consumed
EEGMMIDB-UG1 Stage S-A2 or any consumed MARC2 lane.

## Requested One-Shot Sequence

Only a fresh packet-bound maintainer decision after this request and its
proof-only closeout are remotely green may activate this sequence. Every later
barrier remains mandatory.

### G1: generated and mocked full-pipeline qualification

Implement and qualify with generated MAT fixtures and mocked transport only:

- exact source manifest, path, hash, size, symlink, overwrite, and disk guards;
- bounded sequential transport with invocation-local partial-file resume;
- strict MAT structure and channel validation;
- separate source-target and held-out-target capabilities;
- nine isolated outer folds and eight source-person inner folds;
- causal filters, E1/E2 selection, P, P+E, P+D(E), and every fixed control;
- deterministic fitting, inference, prediction hashing, and replay;
- aggregate-only scoring and exact participant sign-flip tests;
- runtime, RSS, bytes, fit, prediction, target-delivery, and warning receipts;
  and
- fail-closed cleanup, mutation, output-cap, and resource behavior.

The implementation and sole generated qualification must be committed, pushed,
and both CI jobs green before any payload request.

### A: one opaque acquisition

Make one acquisition invocation for only the 18 original MAT files frozen by
the request. Final accepted bytes must total exactly `779,873,919`, and every
file must match its published SHA-256.

The acquisition process may inspect URL, path, response status, range support,
content length, final file size, and SHA-256 only. It may make at most three
attempts per file and 54 payload requests total. Resume is allowed only from an
invocation-created `.part` file using a validated byte range. A completed file
cannot be requested again. A hash or identity mismatch refuses the stage.

Acquisition may not parse a MAT header, MATLAB key, run, channel, sample, trial,
event, artifact flag, label, or target. The exact private manifest and aggregate
receipt must be frozen and remotely green before semantic access.

### Q: one target-blind semantic and signal qualification

Sequentially open each verified MAT once. A target-isolation process validates
the expected top-level structure, six nonempty task runs, 48 trials per task
run, sampling, channel width, trial indices, and complete signal windows. It
emits:

- target-free run/trial timing and signal capabilities;
- fold-scoped source-label capabilities;
- nine sealed held-out-E target sets; and
- one aggregate structural receipt with no row, target, or participant outcome.

The predictive process never receives the target vector for its own held-out
participant. Non-task calibration structs may be recognized structurally but
their signal is not eligible for a feature, model, control, prediction, or
score. Qualification freezes exact counts, hashes, channel order, sampling,
geometry availability, warnings, and capability lineage. It may not select a
model from held-out outcomes or exclude a row using target or artifact flags.

Q must be committed, pushed, and both CI jobs green before modeling.

### P: nine fold-isolated fits and one prediction freeze

For outer fold `Ai`, only A01-A09 excluding `Ai` may provide source labels and
fit state. `AiT` is unused. `AiE` provides target-free signal and timing only.
The fold selects E1 or E2 by source-person inner cross-validation, fits P and
the two frozen fusions from source cross-fits, generates all controls, and
predicts `AiE` once.

All nine fold processes run sequentially under one numerical thread. Public
output contains only condition completeness, aggregate hashes, operation
counts, resources, warnings, and claim boundaries. It contains no individual
prediction, probability, target, row, or participant outcome.

The aggregate hash-only prediction freeze must be committed, pushed, and both
CI jobs green before target delivery.

### T: one target delivery and score

Deliver the same nine sealed held-out-E target sets once to the isolated scorer.
Apply the frozen C3 and C5-partial gates and route once. Emit only aggregate
participant-macro metrics, exact p-values, counts, routes, resources, warnings,
and claim boundaries.

There is no post-target fit, exclusion, calibration, threshold, seed, family,
window, channel, fusion, or route change. R2-R5 consume the scientific score.

## Frozen Scientific Contract

The exact models, windows, controls, views, participant firewall, gates, and
router are in the preregistration and machine contract. In compact form:

```text
held-out unit: 1 entire participant, zero calibration
final session: E only; held-out T is unused
EEG endpoint: 22-channel causal 8-30 Hz E1/E2 source-selected model
eye comparator: 3-channel causal 0.5-8 Hz EOG model P
conditional test: P+E versus P and size-matched P+D(E)
decision time: one completed-trial prediction at 6.0 seconds
selection: inner source-person folds only
score: all nine folds frozen, then one aggregate target delivery
```

C3 requires EEG-only participant-macro balanced accuracy at least `0.35`, an
`0.08` margin over no-signal/timing, a `0.02` margin over the strongest frozen
derangement/temporal/spatial control, positive primary margins in at least
eight of nine people, and exact one-sided participant sign-flip `p <= 0.05`.

C5-partial requires P+E to improve participant-macro log loss by at least
`0.03` nats/trial over both P and P+D(E), positive deltas in at least eight of
nine people for each comparison, and exact one-sided paired participant
sign-flip `p <= 0.05` for each.

## Frozen Routes

| Route | Maximum meaning |
|---|---|
| `BNCIC3C5-R0` | Integrity, semantic, capability, payload, resource, freeze, or score refusal. |
| `BNCIC3C5-R1` | Generated or target-blind qualification failed; no scientific score. |
| `BNCIC3C5-R2` | Neither C3 nor C5-partial passed. |
| `BNCIC3C5-R3` | C3 passed; C5-partial failed. |
| `BNCIC3C5-R4` | C5-partial passed; C3 failed. |
| `BNCIC3C5-R5` | C3 and C5-partial both passed. |

## Resource And Storage Envelope

- one CPU thread, one worker, and one numerical job;
- one acquisition invocation, at most three attempts per file, 54 requests,
  and 2.5 GiB network transfer;
- exact accepted payload `779,873,919` bytes;
- at most 2 GiB incremental disk and at least 5 GiB free before acquisition;
- at most 512 MiB private derivatives and 4 MiB public output;
- at most 1 GiB peak RSS, 1,800 seconds acquisition, and 3,600 seconds analysis;
- at most 540 parameter-update fits and 900 prediction sets;
- zero network during qualification, modeling, freezing, and scoring; and
- cleanup only of temporary files created by the active invocation.

Transport attempts are not scientific reruns. The acquired complete bundle,
semantic qualification, model execution, prediction freeze, target delivery,
and score are each one-shot. There is no dataset substitution or second
scientific execution.

## Explicitly Not Requested

No BDF or HTML derivative, other BNCI dataset, EEGMMIDB, S20, S21, S24, S25,
SpanishBCBL, raw FIF, `.event` sidecar, language dataset, archive, provider,
foundation or language model, pretrained checkpoint, deep network, additional
candidate, hyperparameter search, row-random split, test-time adaptation,
target-derived exclusion, individual protected publication, stream, device,
hardware, release, or clinical action is requested.

No operation on a consumed marker, private MARC2 source, existing ignored
experiment output, or another project is requested.

## Current Authorization State

Every current authority flag is false and every protected operation counter is
zero. Public source-code inspection used to freeze loader semantics opened no
neural payload and granted no authority.

This request and a non-scope-changing proof closeout must each be committed,
pushed, and both remote CI jobs green. Only then may `BNCI-C3C5-1` be named as
the sole active Tier C packet. A fresh unambiguous maintainer message after that
identification may authorize the unchanged packet by reference. The current or
any earlier `continue`, `approve`, or similar message is not retroactive
authority.

Engineering capability requested: an independent, one-shot, completely
held-out-participant EEG evaluation with a recorded-EOG conditional comparator,
strict fold-scoped target capabilities, causal models, and frozen controls.

Scientific claim not established: this all-false request opens no real payload,
fits no real model, freezes no real prediction, and scores no target, so it
establishes no unseen-person result, EEG gain beyond eyes, motor intention,
motor-cortex origin, thought or language decoding, live result, or device result.
