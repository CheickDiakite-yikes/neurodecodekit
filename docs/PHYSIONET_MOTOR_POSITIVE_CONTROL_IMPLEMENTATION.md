# PhysioNet Motor Positive-Control Implementation

Date: 2026-08-09

Status: **Implemented locally; generated-fixture qualified; exact implementation
commit and remote-green CI still required before any real EDF access**

Frozen contract:
`registries/physionet_motor_positive_control_contract.v0.json`

Authorization decision:
`registries/physionet_motor_positive_control_authorization_decision.v0.json`

Implementation registry:
`registries/physionet_motor_positive_control_implementation.v0.json`

## Ordered Parent Evidence

Registration commit `3c00557ecfb09c80e30843589ae295a09feec97c` passed
Base Python job `93330354031` and Optional Neuro Readers job `93330354047` in
CI `31346882592`. The separate request commit `c62b10a` passed both required
jobs in CI `31347209691`. The maintainer then supplied the exact registered
authorization sentence.

Authorization-only commit `da9399c4290fc2be81834ed1036a6bede5f52154`
passed Base Python job `93334251403` and Optional Neuro Readers job
`93334251379` in CI `31348287824` before implementation began. Its decision
registry SHA-256 is
`33c066ecc54953d7ec5fb17da894856a7622e66c1aadd4a5b709c79429e0a246`.

No acquired PhysioNet path, private acquisition receipt, EDF header,
annotation, signal sample, target, or local payload was statted, opened,
hashed, parsed, or interpreted during this implementation milestone. All
reader, derivative, model, control, freeze, and scorer qualification used
generated arrays only.

## Capability Added

NeuroDecodeKit now has a bounded Work Order 9 implementation with two CLI
surfaces:

```bash
neurodecode physionet-motor-positive-control
neurodecode score-physionet-motor-positive-control
```

The first command defaults to a no-stat, no-open, no-hash, no-parse plan. Its
`--fixture` mode runs the full interface over generated arrays. Its `--execute`
mode refuses unless the current exact implementation commit and both remotely
green CI job IDs are supplied and the tracked implementation registry matches
the current source hashes.

The scoring command defaults to a no-target plan. Its `--execute` mode refuses
unless the aggregate prediction-freeze ledger is tracked at the exact current
commit and that commit's Base Python and Optional Neuro Readers jobs are both
remotely green.

## Narrow Optional Environment

The dependency-free base install remains unchanged at `dependencies = []`.
One `classical` optional extra adds only the registered families:

- NumPy `>=1.26`
- SciPy `>=1.11`
- MNE `>=1.12,<1.13`
- scikit-learn `>=1.4,<2`
- pyRiemann `==0.12`

One isolated Git-ignored environment was installed with one installer worker.
The qualified versions are NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`,
scikit-learn `1.9.0`, and pyRiemann `0.12`. Installation took 7.24 seconds,
used 55,279,616-byte peak RSS, downloaded approximately 55.8 MiB, and retained
205,276 KiB on disk. This is below the 900-second, 256 MiB transfer, and
512 MiB incremental-disk caps. Heavy packages are imported only inside the
functions that require them.

## Exact Reader And Split

The future real executor is restricted to the acquired EEGMMIDB v1.0.0 files
for S001-S003 runs 03, 07, and 11, totaling exactly 23,248,224 bytes. It:

1. Verifies the private acquisition-manifest SHA-256 and exact nine-member
   inventory without following symlinks.
2. Makes one new sequential size and SHA-256 pass per EDF.
3. Makes one semantic MNE parse per EDF and retains all 64 standardized EEGBCI
   channels, standard-1005 geometry, 160 Hz samples, and only T0/T1/T2
   annotations.
4. Refuses any unexpected channel type, annotation, event count, nonfinite
   sample, geometry drift, duplicate identity, or out-of-bounds window.
5. Uses runs 03 and 07 only for fitting and family selection.
6. Creates a target-free run-11 prediction derivative and a separate sealed
   45-target scorer input.

There is no row-random split. Subject and run identity are carried through all
derivatives, and fit and prediction event IDs must be unique and disjoint.

## Target Firewall

The extraction stage must parse the T1/T2 annotations once because it creates
both the run-03/07 fit labels and the sealed run-11 scorer input. That stage
writes the run-11 target file but does not print or return its values. The
subsequent model stage opens only the fit derivative and the target-free
run-11 prediction derivative. It does not open the sealed target file.

This is a function and artifact boundary, not an operating-system security
sandbox. The precise guarantee is that run-11 targets are not supplied to any
fit, selection, threshold, channel, parameter, prediction, or control
operation, and the sealed target file is not opened by the model stage before
the remotely green prediction freeze. The isolated scorer is the only future
stage allowed to reopen that file, exactly once.

## Causal Features And Fixed Families

All signal paths apply instantaneous common-average reference across all 64
retained channels, then a fourth-order Butterworth SOS filter with
`scipy.signal.sosfilt` on the continuous run in time order. The primary window
is cue-relative `+1` through `+3` seconds. The prediction time is `+3` seconds,
so right context is zero. This is cue-causal, not pre-movement: actual movement
onset is unavailable and end-to-end acquisition latency is unmeasured.

Runs 03/07 alone select between:

- four-component 8-30 Hz CSP plus fixed-shrinkage LDA; and
- regularized Riemannian MDM with fixed 0.1 trace regularization.

An exact tie selects CSP-LDA. A fixed 0.5-4 Hz shrinkage-LDA comparator is not
a selection candidate. Numerical floors for zero-signal CSP features and
zero-trace covariance are fixed implementation constants, not outcome-driven
fallbacks.

The complete inventory is 33 classical parameter-update fits, 45
target-blind model-inference runs, three train-only no-signal prior fits, and
12 final prediction sets. These are below the authorized maxima of 40 fits and
64 target-blind inference runs.

## Prediction And Control Inventory

The 12 mandatory final sets are:

1. selected full-head primary
2. low-frequency shrinkage-LDA comparator
3. train-only no-signal prior
4. all-zero final signal
5. pre-cue model
6. event-index-and-timing-only model
7. fixed train-label derangement
8. fixed one-trial final-signal displacement
9. fixed validation-channel derangement
10. fixed left/right hemisphere swap
11. frontal/occipital proxy-channel model
12. central sensorimotor-channel model

The public freeze contains no individual event ID, participant ID, prediction,
probability, target, or participant outcome. It binds:

- one SHA-256 for every 45-row prediction set;
- the private prediction payload and fit/prediction/sealed derivative hashes;
- the acquisition-manifest identity and source inventory size;
- the exact split-protocol and configuration hashes;
- the implementation-registry hash and its tracked-file-hash inventory;
- the selected family and dependency versions; and
- all fit, inference, target-firewall, runtime, RSS, output, network, retry,
  and rerun counters.

The scorer recomputes every condition hash before opening targets. Any mismatch
parks at `WO9-V0`.

## Frozen Aggregate Scorer

After the freeze commit is remotely green, the scorer may deliver the same 45
run-11 targets once. It publishes aggregate condition metrics only. The
ordered router is unchanged:

- `WO9-V0`: integrity, access-order, resource, split, or freeze failure.
- `WO9-V1`: primary predictive gate fails.
- `WO9-V2`: prediction passes but physiology or confound conjunction fails.
- `WO9-V3`: prediction, motor-compatible physiology, and all controls pass.

The motor-physiology direction is frozen as a negative contralateral-minus-
ipsilateral mu/beta active-minus-baseline effect. The hemisphere-swap
condition must fail the primary predictive gate for `WO9-V3`. These signs and
router details were fixed before any real EDF was accessed.

## Generated-Fixture Qualification

The deterministic seed-5509 fixture creates nine generated 64-channel runs,
135 events, the exact 90/45 run split, synthetic motor structure, nuisance
structure, geometry, timing, and annotations. It exercises both registered
families, all derivatives, the target firewall, all 12 prediction conditions,
per-condition hashes, aggregate scoring, malformed-run refusals, output caps,
and private-prediction tampering.

The final measured CLI roundtrip reported:

```text
synthetic runs / events:                    9 / 135
selected family:                           fixed_8_to_30_hz_csp_lda
classical parameter-update fits:           33
target-blind model-inference runs:          45
prediction sets:                           12
runtime:                                   8.961233 seconds
peak RSS:                                  327,647,232 bytes
generated bytes including summary:         20,825,424
real data / real target / network reads:   0 / 0 / 0
all implementation gates:                  passed
```

The synthetic router happened to return `WO9-V2`. That value has no scientific
or predictive meaning because the fixture was constructed to qualify the
interface. The generated output directory was inspected and then removed;
only the isolated optional environment remains.

## Complete Verification

The final one-thread broad local suite ran 1,504 tests in 41.199 seconds:
1,499 passed and five were expected skips. External wall time was 42.24
seconds and maximum RSS was 639,238,144 bytes. The separate isolated
registered-classical environment ran 1,489 tests in 15.244 seconds: 1,455
passed and 34 were expected skips. External wall time was 17.55 seconds and
maximum RSS was 500,006,912 bytes.

The focused Work Order 9 matrix ran 19 checks. The broad environment passed 17
with two expected optional-stack skips; the isolated environment passed all
19. The authorization milestone's earlier clean-base run had 1,414 tests and
163 expected skips. Those totals are not a direct dependency-for-dependency
delta because the local environments expose different optional packages, but
no previously passing test failed in either final complete matrix.

One initial sandboxed complete run correctly exposed two stale tracker tests
that required the literal status word `Gated`; the tracker now says both
`Gated` and `Implementation Qualified Locally; Execution Pending Remote Green`.
That run's only other error was an existing forkserver timing test being denied
permission to create its local multiprocessing socket. Both final suites
passed outside that sandbox with the same one-thread numerical limits.

## Failure And Resource Behavior

Before a future real read, the executor refuses an ungreen or non-current
implementation, dirty implementation hashes, wrong dependency versions,
non-one-thread environment, low free disk, output collision, wrong path,
symlink, unexpected bundle member, or private-manifest mismatch. Once the
registered execution marker is created, any later failure consumes and parks
the one execution. There is no retry, rerun, substitute, post-target update,
or automatic cleanup outside invocation-created temporary paths.

The real cap remains one CPU thread, one worker, one numerical job, 1,800
seconds, 805,306,368-byte peak RSS, 67,108,864 private generated bytes, at
least 2 GiB free disk, zero network bytes, and zero new payload bytes.

## Implementation Access Ledger

```text
registered PhysioNet path stats / opens:       0 / 0
private acquisition-manifest reads:            0
real EDF hash / semantic parse passes:          0 / 0
real header / annotation / signal reads:        0 / 0 / 0
real target rows delivered / scored:            0 / 0
real derivatives / fits / inferences:           0 / 0 / 0
prediction freezes / scoring events:            0 / 0
network requests / bytes:                       0 / 0
additional payload bytes:                       0
provider / RW3 / stream / device / hardware:   0 / 0 / 0 / 0 / 0
retained generated experiment bytes:            0
real execution retries / reruns:                0 / 0
```

## Next Gate

This exact implementation, registry, tests, CLI, optional dependency surface,
and documentation must be committed and pushed. Both required CI jobs must be
green at that exact commit. Only then may the one no-network nine-EDF execution
begin. A successful target-blind run still cannot score: its aggregate
prediction-freeze ledger must first be committed, pushed, and remotely green.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can now execute a strict,
resource-bounded, target-firewalled, held-out-run public EEG motor-task
positive-control protocol with fixed classical models, physiology and confound
controls, per-condition prediction hashes, and an isolated aggregate scorer.

Scientific claim not established: generated-fixture qualification establishes
no real EEG readability, motor-task accuracy, neural effect, physiology,
brain-specific origin, unseen-person generalization, typing, language or
thought decoding, end-to-end latency, real-time operation, portable hardware,
home use, assistive benefit, or clinical utility.
