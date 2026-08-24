# BNCI-C3C5-1 Generated Pipeline Implementation

Date: 2026-08-24

Status: **implementation complete and component-qualified; sole G1 launcher
attempt refused before its first generated case; full G1 remains unproven**

Machine records:

- `registries/bnci_2014_001_cross_participant_eeg_gain_implementation.v0.json`
- `registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_failure.v0.json`

## Added Capability

The additive implementation supplies four narrow surfaces:

1. an exact 18-member opaque acquisition plan and mocked resumable transport
   with size, SHA-256, path, hardlink, symlink, request, network, disk, and
   cleanup refusals;
2. a strict generated MAT reader plus causal feature extraction for frozen E1,
   E2, P, temporal, spatial, channel-rotation, and displacement conditions;
3. nine sequential spawned fold workers, each receiving only source-person
   targets and target-free held-out-E features; and
4. canonical prediction freezing and a separate one-delivery aggregate scorer
   for the preregistered C3 and C5-partial routes.

The base import remains dependency-free. NumPy, SciPy, and scikit-learn are
loaded lazily and pinned only in the optional numerical environment. The CLI
exposes `plan` and generated-only `qualify`; it deliberately exposes no real
acquisition or execution command before a remotely green G1 proof.

## Fixed Mechanics

- E1 is 88-dimensional causal four-band log variance.
- E2 is 1,012-dimensional trace-normalized regularized log covariance with an
  explicit source-only log-Euclidean reference.
- P is the fixed 102-dimensional causal recorded-EOG comparator.
- Each outer fold performs 52 parameter-update fits and 55 prediction sets.
- The full frozen schedule is 468 fits and 495 prediction sets, under the
  registered maxima of 540 and 900.
- A spawned worker receives 384 compact generated source-label capabilities
  and zero generated held-out target values or identities.
- The scorer verifies configuration, code, split, source, target-payload, and
  prediction hashes before opening its target loader once.

## Component Qualification

Eight dependency-free tests and four optional numerical tests pass locally.
The numerical checks cover a 6-run, 288-trial generated MAT fixture, causal
future-impulse invariance, all frozen feature dimensions, source-only E2
reference fitting, one exact 52-fit fold, and one spawned target-firewalled
fold. Ruff, compileall, and `git diff --check` also pass.

These component checks are not the registered full G1 pass.

## G1 Launcher Incident

The sole authorized CLI attempt created its invocation-owned temporary root,
read the two tracked bound registries, checked free disk, and then refused in
0.027232958 seconds. The coordinator passed that existing root directly to a
helper whose contract requires a new child directory, producing
`FileExistsError` before the first generated MAT write.

The `finally` guard removed only that invocation-created empty temporary root.
No aggregate output was created. The failure is recorded as
`BNCIC3C5-R1`, with zero generated case executions, fits, predictions, target
deliveries, scores, real-data reads, or network bytes.

The wiring is repaired by passing a new `mat` child path. It has been
component-tested but not rerun. The original one-shot authority is consumed;
a new narrow recovery decision is required for one replacement G1 pass.

## Boundary

Stage A remains closed. No BNCI payload was downloaded, opened, parsed, or
scored. No result in this implementation changes a scientific claim.

Engineering capability added: NeuroDecodeKit now has a bounded, lazy,
target-firewalled BNCI generated pipeline implementation with exact model,
control, freeze, scorer, and resource surfaces.

Scientific claim not established: the registered full G1 pass refused before
its first case, so this work establishes no unseen-person EEG decoding, EEG
gain beyond recorded EOG, neural advantage, or decoding performance.
