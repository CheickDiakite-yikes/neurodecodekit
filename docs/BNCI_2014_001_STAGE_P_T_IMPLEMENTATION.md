# BNCI-C3C5-1 Stage P/T Live Implementation

Date: 2026-08-25

Status: **Implementation pending commit, push, and both required CI jobs. No
Stage P model or Stage T score is enabled by this document.**

## Purpose

Stage Q is complete, consumed, and remotely green. It created nine isolated
fold capabilities from the real BNCI 2014-001 MAT bundle while keeping each
held-out participant's E-session targets and all scoring keys outside the
predictive capability.

This milestone adds the narrow live bridge needed to use those capabilities:

1. Stage P loads one fold capability in an isolated child process;
2. it runs the already-qualified frozen models and controls;
3. it writes one private canonical prediction file per fold;
4. it publishes only an aggregate hash-only prediction freeze; and
5. Stage T can open the sealed targets and apply the frozen scorer only after
   that exact freeze is committed, pushed, and remotely green.

It does not change a model, feature, window, channel, split, seed, threshold,
control, gate, or route from the preregistration.

## Completeness Firewall

The live boundary requires the exact grid before either prediction freezing or
scoring:

```text
9 participants
2 source sessions for each of 8 source participants per fold
6 task runs per participant/session
48 trials per run
288 held-out E rows per fold
16 frozen prediction conditions per held-out row
```

Every `(participant, session, run, trial)` coordinate and every opaque row ID
must be unique. Trial ordinals outside `0..47`, duplicate coordinates mapped to
different opaque IDs, incomplete run grids, missing conditions, source-target
surplus, held-out target leakage, and any held-out-T delivery refuse the stage.

This closes a live-boundary gap in the generic generated scorer without
modifying the proof-bound G1 numerical or scoring core.

## Stage P Isolation

The coordinator receives only the Stage Q output directory and a fold ID. It
does not load numerical arrays. For each fold, one fresh spawned child receives
only the Stage Q capability directory and held-out participant ID. The child:

- verifies the 17 listed signal shards and one source-target capability by
  size and SHA-256;
- loads exactly 4,608 source rows and 288 target-free held-out-E rows;
- receives no repository root, scoring-key path, held-out-E target, or held-out-T
  signal or target;
- runs the frozen 52 fits and 55 prediction sets; and
- returns predictions, model hashes, operation counts, and aggregate resource
  state.

The coordinator writes and releases each fold sequentially. It never retains
nine fold matrices or fitted models together. One monotonic 3,600-second
deadline covers all staging, nine folds, freezing, and publication.

## Public Prediction Freeze

The Stage P public artifact contains:

- the exact Stage Q and remotely green control-plane proof;
- hashes of the aggregate private prediction stream and each condition stream;
- the fixed configuration, code, and split hashes;
- a keyed HMAC commitment to the private Stage Q capability manifest;
- an aggregate commitment to the nine encrypted target envelopes and scoring
  key vault;
- operation counts, resources, warnings, and acceptance gates; and
- aggregate E1/E2 selection counts only.

It contains no private path, derivative hash inventory, model coefficients,
individual prediction, probability, target, or participant outcome. The HMAC
key remains private until Stage T.

## Stage T Transport Binding

Stage Q intentionally did not publish a plaintext target-payload hash. Stage P
therefore binds the ordered encrypted-envelope inventory and key-vault digest.
After the prediction-freeze commit is remotely green, Stage T:

1. verifies the committed public freeze and private prediction hashes;
2. recomputes the keyed Stage Q source-capability commitment;
3. verifies the exact encrypted target transport commitment;
4. writes its consumed marker before opening the scoring-key vault;
5. authenticates and decrypts the same nine target envelopes once;
6. verifies the exact 9 x 6 x 48 target and prediction identity grid; and
7. applies the frozen C3/C5-partial scorer once.

No target-derived fit, exclusion, calibration, threshold, solver, seed, family,
feature, control, route, retry, or rerun is available.

## Resource Envelope

The unchanged registered caps are:

- one CPU thread, one worker, and one numerical job;
- 3,600 seconds for modeling/freezing/scoring;
- 1 GiB peak process-tree RSS;
- 512 MiB private generated output;
- 4 MiB public output;
- 540 parameter-update fits and 900 prediction sets;
- zero analysis network bytes; and
- cleanup only of invocation-created temporary files.

The exact Stage P schedule is 468 fits, 495 prediction sets, and 41,472 private
prediction rows. Stage T has one target delivery, one score, zero updates, and
zero reruns.

## Local Qualification

Before this implementation milestone was committed:

- the complete dependency-free suite passed 6,125 tests with 230 optional
  skips in 254.22 seconds;
- the focused BNCI base suite passed 51 tests with nine optional skips;
- the focused pinned optional-neuro suite passed 38 tests;
- an exact-shape generated fold exercised 4,608 source rows, 288 held-out rows,
  all 52 fits, and all 55 prediction sets; and
- Ruff 0.15.20, `git diff --check`, CLI help, and both Stage P/T plans passed.

These are generated engineering qualifications. They use no private Stage Q
capability, real target, real model execution, prediction freeze, or score.

## Proof Sequence

1. Commit and push this implementation; both CI jobs must pass.
2. Add a minimal Stage P activation bound to that exact green implementation.
3. Commit and push the activation; both CI jobs must pass.
4. Execute Stage P once and emit the aggregate prediction freeze.
5. Commit and push the exact freeze; both CI jobs must pass.
6. Add and remotely green the Stage T activation.
7. Deliver the targets and score once.
8. Commit, push, and remotely green the aggregate result and closeout.

## Claim Boundary

Engineering capability added: a bounded live adapter can turn the existing
target-firewalled real Stage Q derivatives into fold-isolated frozen
predictions and one proof-gated aggregate score.

Scientific claim not established: implementation alone establishes no
unseen-person prediction, EEG advantage beyond EOG, decoding accuracy,
language, thought, movement-intention, motor-cortex, live, hardware, home-use,
or clinical result.
