# IACKD Cue-to-Action Reversal Implementation

Date: 2026-08-10

Status: **Generated-fixture qualified; exact implementation must be committed,
pushed, and remotely green before the registered acquisition or analysis.**

Registry:
`registries/iackd_cue_action_dissociation_implementation.v0.json`

## Parent Gate

This implementation is downstream of the packet-bound authorization decision
at commit `1f48b3011e19ba8da35a18c3d3395813f159adc2`. CI run
`31403012709` passed Base Python job `93502398308` and Optional Neuro Readers
job `93502398753` before implementation began.

The implementation does not broaden
`registries/iackd_cue_action_dissociation_contract.v0.json`. The frozen
OpenNeuro version, 1,340-object inventory, participant-hand split, causal
features, model family, controls, target firewall, resources, one-shot order,
router, and claim ceiling remain authoritative.

## Capability Implemented

Three dry-run-first commands now expose the complete registered interface:

```bash
neurodecode iackd-acquire
neurodecode iackd-cue-action
neurodecode score-iackd-cue-action
```

The acquisition command uses only the Python standard library. It rejects
redirects and retries, strictly parses the two registered S3 listing pages,
reconstructs the 1,340-object canonical identity, requires exact metadata and
response identities, and streams one SHA-256 while writing each allowlisted
object. It performs no neural-reader import or content parse, promotes only a
complete isolated bundle, and writes bounded private receipts.

The analysis command implements one-run-at-a-time BrainVision reading with the
exact existing optional dependency versions. It requires 32 ordered EEG
channels plus M1, M2, HEOG, and VEOG, 1,024 Hz sampling, finite signals, and
available EEG geometry. It reconciles the registered marker sequence with ball
and Leap streams, including declared timestamp and spatial units, while
retaining no raw signal or trajectory window.

Continuous causal preprocessing applies instantaneous common average and a
fourth-order 0.5-4 Hz Butterworth SOS filter before windowing. The registered
stop is at least 30 ms before measured movement onset. Four 250 ms means and
one slope per EEG channel form the 160-dimensional primary feature. Compact
EOG, timing, pre-window, early/late, central, and physiology summaries are
kept separate.

The target builder is an isolated artifact boundary. Congruent fit rows expose
their action label to fit code. Held-out incongruent rows expose no action
direction, visual direction, signed trajectory, ball position, label,
probability, or prediction. Both opposite final target views are written
together into one sealed scorer input and remain unopened by the model stage.

Thirty participant-hand units each execute ten fixed fits, for exactly 300
parameter-update runs. Fourteen prespecified conditions produce exactly 420
target-blind participant-condition prediction sets. There is one classifier
family, no real-data family selection, no hyperparameter or threshold search,
and no post-target update.

The public freeze has a strict aggregate-only schema. It binds the contract,
decision, implementation, source manifest and object hashes, split, feature
configuration, reader metadata, quality summary, target firewall, dependency
versions, private derivative hashes, physiology content, operation counts, and
all 420 prediction hashes. It contains no individual prediction, probability,
target, signed trajectory, or participant outcome.

The isolated scorer verifies those bindings, recomputes the physiology content
hash, opens both sealed target views together once, computes only aggregate and
participant-level inference summaries, applies the frozen `IACKD-R1`, `R0`,
`R2`, `R3`, `R4` order, and permits no update after target delivery.

## One-Shot Ordering

Four fail-closed order rules are executable and tested:

1. Acquisition writes its consumed marker before metadata access or any object
   request. A later failure cannot create a retry.
2. Real analysis writes its consumed marker before bundle inspection, object
   hashing, semantic parsing, or target-firewall work.
3. The model stage receives only fit and target-free final derivatives. It
   does not open or re-hash the sealed target payload.
4. Scoring writes its consumed marker before the first private prediction,
   derivative, physiology, or sealed-target hash/open, and is unavailable until
   the aggregate freeze commit is pushed and both CI jobs are green.

## Generated-Fixture Qualification

One measured generated-only qualification exercised the complete analysis,
firewall, prediction, freeze, and scoring interface in the exact existing
optional environment:

| Measure | Observed |
|---|---:|
| Generated run records | 128 |
| Generated trials | 2,048 |
| Fit rows | 1,568 |
| Target-free final rows | 480 |
| Participant-hand units | 30 |
| Parameter-update fits | 300 |
| Target-blind inference calls | 420 |
| Prediction sets | 420 |
| Runtime | 8.674020 seconds |
| Peak RSS | 263,618,560 bytes |
| Generated bytes before cleanup | 5,683,285 bytes |
| Network bytes | 0 |
| Real-data reads | 0 |
| Real-target reads | 0 |

All generated artifact hashes and predictions replayed exactly. The synthetic
router emitted `IACKD-R2`; this is an interface fixture outcome with no
scientific or model-performance meaning. The generated output was removed
after measurement.

The exact qualified versions are NumPy 2.5.2, SciPy 1.18.0, MNE 1.12.1, and
scikit-learn 1.9.0. No dependency was installed, resolved, downloaded, or
added to the base package.

## Adversarial Coverage

Focused tests cover:

- canonical inventory replay, malformed listing pages, metadata drift,
  redirects, missing or wrong ETags, truncated payloads, symlinked parents,
  thread mismatches, exclusive roots, cleanup scope, and one-shot consumption;
- channel order, sampling, geometry, finite values, marker order, stream joins,
  declared units, motion timing, target-derived failures, and minimum counts;
- deterministic NPZ and prediction replay, strict dimensions, target-like
  fields in target-free artifacts, output caps, and malformed caches;
- exact 300-fit and 420-prediction-set counts, all fourteen controls, private
  prediction hashes, strict aggregate freeze fields, complete provenance, and
  physiology-content binding; and
- all five registered router outcomes without changing thresholds or models.

Final implementation verification is recorded in the machine registry. The
focused exact-stack suite passes 77 tests: 69 interface/contract tests plus
eight implementation-registry invariants. CLI help and default dry runs make no
local IACKD stat, network request, dependency operation, or target access.

## Real-Access Counters

This implementation milestone performed zero real OpenNeuro metadata
reverifications, payload requests, payload bytes, local IACKD stats or opens,
object hash passes, BrainVision parses, EEG/EOG header reads, marker/event
reads, signal reads, ball/Leap reads, target reads, real derivative creations,
real fits, real inference calls, real prediction freezes, target deliveries,
scores, retries, reruns, provider calls, stream/device/hardware operations, or
claim upgrades.

## Next Gate

Commit and push this exact implementation and require both Base Python and
Optional Neuro Readers jobs to pass at the same commit. Only then may the one
registered 7,249,113,684-byte acquisition and target-blind analysis run. The
dual final target views remain closed until the aggregate prediction freeze is
committed, pushed, and remotely green.

Engineering capability added: NeuroDecodeKit now has a fixture-qualified,
resource-bounded, target-firewalled IACKD cue-to-action reversal pipeline that
can freeze the same held-out predictions for action-versus-cue scoring.

Scientific claim not established: no real IACKD payload or target was opened,
so this implementation establishes no EEG effect, action decoding,
brain-specific origin, generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.
