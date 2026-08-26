# DREYER-C5R-1 Generated Implementation Closeout

Date: 2026-08-26

Status: **Generated implementation complete locally and ready for commit,
push, and remote CI. The one registered Stage G qualification has not run.**

## What Was Implemented

The implementation turns the frozen replication protocol into a small,
generated-fixture-only executable surface:

- a standard-library EDF fixed-header parser that returns only signal labels,
  record/sample counts, durations, and rates while withholding patient,
  recording, and date text;
- the exact causal one-second Hann-window spectral feature transform;
- fixed source-only ridge residualization against EOG, EMG, posterior EEG, and
  timing;
- adjacent-pair within-run residual derangement;
- one standardized L2 logistic family and participant-grouped source-only
  temperature calibration;
- an isolated held-out-person capability containing source targets and
  held-out features, but no held-out target;
- 17-condition target-blind predictions and an aggregate hash-only freeze;
- one-delivery target-vault behavior and an aggregate-only scorer with frozen
  R1/R2/R3 routing; and
- a sidecar CLI exposing only `plan`, `qualify`, and `inspect`.

There is deliberately no real download, header preflight, semantic parse,
training, prediction, delivery, or score command.

## Exact Real Schedule

The schedule planner independently derives the preregistered totals:

- 60 outer held-out-person folds;
- 4,740 parameter-update fits;
- 3,660 model-inference calls, including source calibration calls;
- 1,020 held-out prediction sets;
- 81,600 held-out prediction rows; and
- zero held-out target deliveries before a remotely green prediction freeze.

The planner cannot open a data path and does not depend on NumPy. Numerical
work remains behind the existing optional `classical` extra; the base package
still has zero required dependencies.

## Development Qualification

Unregistered temporary generated runs were used while implementing the
fixture. The final fixture has six synthetic participants, two runs and ten
trials per run. It deterministically exercises 330 fits, 258 inference calls,
102 held-out prediction sets, 2,040 prediction rows, one synthetic target
delivery after freeze, one synthetic score, and zero post-target updates.

The fixture's known independent central effect reaches the synthetic R1 route.
Separate tests force uniform predictions to R3 and a subthreshold candidate to
R2. These routes only validate software behavior; generated success has no
scientific value.

The measured temporary pass completed in about 2 seconds at 176,865,280 bytes
peak process-tree RSS, with 197,632 generated input bytes, 296,120 private
temporary prediction bytes, and a 2,831-byte public result. These are
development measurements, not the registered Stage G result.

## Adversarial Coverage

The focused suite checks:

- truncated, non-ASCII, duplicate-label, and malformed-layout EDF headers;
- deterministic spectral band localization;
- absence of target/label arguments from the feature producer;
- exact feature dimensions and participant/run/trial grids;
- source/held-out target capability separation;
- premature and repeated target-delivery refusal;
- prediction tamper detection against the freeze;
- public-freeze forbidden-field checks;
- exact fit/inference/prediction schedules;
- R1, R2, and R3 routing;
- no-clobber output and readback verification; and
- base-install behavior when optional numerical dependencies are absent.

Local focused verification passed 24 tests with the optional environment and
13 tests with eight numerical tests correctly skipped in the dependency-free
base environment. Pinned Ruff and Python compilation passed.

## Proof Binding

The implementation is bound to contract SHA-256
`ea6357a7b079aa3de885ef0a7c0e391c7810e2b94cbbb1702f934f65cc6b8fed`.
The 12 pre-result artifacts total 166,417 bytes under canonical artifact-set
SHA-256 `6b79c4e8173989c74d94c51e27d14caba3296c34fa1f77111410a61c4a1a2733`.

The preceding research/preregistration commit
`8d72f8b43c3c4e2f135a7a0e8654e0cac64f6414` passed Base Python job
`98053700149`, Optional Neuro Readers job `98053700308`, and CI run
`32927671087` before this implementation closeout.

## Next Gate

Commit and push this exact implementation, wait for both required CI jobs, and
then run the one registered generated Stage G qualification. Do not inspect a
real EDF header, request a payload, or perform a real model operation before a
later exact Tier C decision and its own remotely green activation.

## Claim Boundary

Engineering capability established: a complete generated target-firewall,
compact-model, prediction-freeze, and aggregate-scoring path now exists for the
prospective replication design.

Scientific claim not established: no real EEG payload, header, annotation,
signal, target, model result, unseen-person effect, EEG-beyond-peripherals
effect, movement intention, language, live, hardware, or clinical result was
tested.
