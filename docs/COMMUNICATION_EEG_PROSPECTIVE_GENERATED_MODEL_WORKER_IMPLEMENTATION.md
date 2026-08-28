# COMM-P0-G Capability-Poor Model Worker

Date: 2026-08-28

Status: **additive generated-only implementation pending exact commit, push,
and remote CI; official qualification remains inactive**

Machine record:
`registries/communication_eeg_prospective_generated_model_worker_implementation.v0.json`

## Capability Boundary

The generated qualification now has a descriptor-only fold worker. Its model
process receives exactly four preopened descriptors and one fictional held-out
identity:

- target-free feature rows with opaque item identifiers;
- labels for source participants only;
- the frozen generated qualification contract; and
- a write-only prediction stream.

It receives no held-out label, `TrialPlan`, target commitment, target key,
target vault, local path, activation state, prediction-freeze authority, scorer
capability, or post-target update surface. Unexpected fields refuse before a
fit. Source labels must cover every source feature row exactly once and must
contain no row from the held-out participant.

## Fixed Fold Schedule

One participant-held-out fold performs the frozen compact schedule:

- two endpoint-specific source-only residualizer fits;
- one source-only class-prior fit;
- 15 compact classifier fits;
- 15 source-only scalar temperature fits;
- 17 inference passes;
- 34 endpoint-separated prediction sets; and
- 2,176 prediction rows for one complete fictional held-out participant.

Predictions are emitted one canonical JSON record at a time. The worker never
holds the complete official 91,392-row output and never reads a target. It also
checks that every inherited descriptor is a single-link regular file with its
exact read-only or write-only access mode. The future coordinator remains
responsible for no-follow descriptor construction, parent traversal, complete
inventory and order validation, the 256-row maximum validation buffer,
cryptographic freeze attestation, process-group resource monitoring, and
durable invocation consumption.

## Verification

The focused optional-stack tests exercised one complete three-participant
fictional fold in 2.779 seconds. They verified all fixed per-fold counters,
zero held-out labels, zero trial-plan objects, zero target-vault capabilities,
zero target deliveries, zero scores, and zero post-target updates. The complete
dependency-light suite passed 6,695 tests with 270 optional skips in 253.816
seconds while this implementation and its contract amendment were present.

Those measurements are local development evidence only. Exact commit identity,
remote Base Python, remote Optional Neuro Readers, and GitHub `main` remain
pending for this milestone.

## Boundary

Engineering capability added: a model fold can now be fit and inferred through
a capability-poor descriptor interface without receiving held-out targets or
scoring authority.

Scientific claim not established: generated fixtures provide no evidence of
communication decoding, EEG information beyond peripheral signals,
unseen-person generalization, independent replication, live operation, or
benefit to a person.

No official qualification, real/private data access, human/device operation,
network request, release, or scientific claim is authorized by this work.
`DREYER-C5R-1-HL` remains the sole active Tier C gate.
