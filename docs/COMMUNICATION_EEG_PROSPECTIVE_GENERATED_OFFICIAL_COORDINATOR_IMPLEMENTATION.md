# COMM-P0-G Official Coordinator Implementation

Date: 2026-08-28

Status: **generated-only successor pending exact commit, push, and remote CI;
official qualification remains inactive and unconsumed**

Machine record:
`registries/communication_eeg_prospective_generated_official_coordinator_implementation.v0.json`

## Why This Successor Exists

Post-proof audit found that the accepted V1 hardening evidence did not close the
official coordinator. The future official entry still stopped after creating
its consumed marker, both replays ran in one parent, activation accepted an
arbitrary artifact table, target values entered coordinator memory before the
durable score freeze, and not every schedule or resource counter was an
acceptance gate. The full-scale rehearsal also delivered one combined target
map and reported one delivery and one score. The frozen contract requires one
isolated target delivery and score for discovery and one for independent
replication, for two deliveries and two scores in each replay.

The V1 implementation and its measured rehearsal remain immutable historical
engineering evidence. This successor does not reinterpret that rehearsal as
the official qualification and does not alter its recorded counters.

## Added Engineering Capability

The activation-locked official coordinator now has a complete two-replay path:

1. validate the exact activation before any marker or generated work;
2. refuse while the compile-time activation lock is false;
3. durably create the no-replace consumed marker before fixture generation,
   model execution, target delivery, or scoring;
4. run two complete 21-person-per-cohort replays in distinct sanitized child
   processes and work directories against one absolute 180-second deadline;
5. require exact canonical replay equivalence, 91,392 prediction rows, 1,428
   prediction sets, seven numerical shortcut routes, 70 refusal observations,
   two cohort deliveries, two cohort scores, and zero post-target updates in
   each replay;
6. enforce every fit, inference, prediction, shortcut, delivery, score,
   generated-input, private-output, temporary-disk, aggregate-disk, process-
   monitor, and memory counter; and
7. stage, fsync, read back, and atomically publish one target-free aggregate
   result without replacing an existing path.

Activation is restricted to an exact ordered allowlist of 11 public
implementation files plus the exact Amendment 2 hash. Missing, extra,
reordered, substituted, absolute, parent-escaping, or duplicate paths refuse.
The runtime performs no Git, network, or CI request; those identities must be
bound prospectively by the separately green activation record.

The scorer now requires exact `discovery` and `independent_replication` target
envelopes in official mode, validates each envelope against its own manifest,
and reports two deliveries and two scores. The target supplier is not invoked
until the target-free score attestation has been written, fsynced, read back,
and HMAC-verified. Legacy generated development paths retain their one-envelope
behavior.

The replay loop also removes avoidable coordinator overhead without changing
scientific behavior. A cohort's target-free feature stream and frozen contract
are serialized once and reused read-only across folds. Every held-out fold still
receives a unique source-label file, starts a fresh model child, and writes a
unique prediction output. Item ownership is precomputed rather than repeatedly
searched. Splits, features, model family, calibration, conditions, targets,
thresholds, and scoring are unchanged.

The `comm_p0_runner_cli qualify` route now dispatches this coordinator and
requires both `--output` and `--consumed-marker`; it no longer points at the
obsolete fail-closed scaffold.

## Reduced Child-Process Measurement

One nonofficial reduced measurement ran two distinct child-process replays with
three fictional participants per cohort:

| Measure | Result |
|---|---:|
| Runtime | 44.6720 s |
| Prediction rows / sets per replay | 13,056 / 204 |
| Main target deliveries / scores | 4 / 4 total |
| Shortcut target deliveries / scores | 14 / 14 per replay |
| Refusal observations | 140 |
| Maximum raw prediction rows buffered | 1 |
| Peak process-tree RSS | 236,437,504 bytes |
| Generated input written, maximum replay | 957,295 bytes |
| Private output written, maximum replay | 8,787,202 bytes |
| Temporary disk peak, maximum replay | 5,549,075 bytes |
| Monitor samples | 512 |
| Network / real-data / device operations | 0 / 0 / 0 |
| Retained generated payload | 0 bytes |

The two canonical replay surfaces matched exactly. This qualifies reduced
engineering behavior only; participant count is not the official schedule.

## Failure Semantics

Focused tests prove that the marker is absent when activation is closed and is
present before either future replay starts. Replay mismatch, same replay PID,
second-child failure, any model or shortcut ledger drift, zero monitoring,
input/output/disk cap drift, and output collision all leave the invocation
consumed and publish no replacement result. Injected staged-write failure
leaves no partial public path, and a pre-existing output remains byte-identical.

The compile-time `OFFICIAL_IMPLEMENTATION_ACTIVATED` value remains `False`.
No consumed marker or official result was created outside disposable tests.

## Remaining Barriers

1. This exact successor must pass Base Python and Optional Neuro Readers in
   remote CI and reach GitHub `main`.
2. The optimized two-replay route needs bounded evidence that it can complete
   inside the frozen 180-second total cap. The prior single-replay rehearsal
   took 101.5826 seconds, so that evidence cannot be assumed.
3. A separate exact-green activation must bind the proven implementation.
4. Only then may the single official generated qualification run once.

No additional full-scale rehearsal and no official qualification ran in this
milestone. No real/private data, network, person, device, provider, release, or
scientific-claim operation occurred.

Engineering capability added: NeuroDecodeKit now has a fail-closed,
activation-locked two-replay coordinator with contract-exact cohort target
delivery, one-shot consumption, bounded publication, and unchanged held-out
model isolation.

Scientific claim not established: this generated-only implementation does not
show communication decoding, EEG information beyond peripheral controls,
unseen-person generalization, independent replication, causal live-device
performance, hardware benefit, or clinical value.
