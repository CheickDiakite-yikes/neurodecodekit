# BNCI-C3C5-1 Stage P Live Activation

Date: 2026-08-25

Status: **Prepared with delayed effect. Stage P remains closed until this exact
activation commit is pushed and both required CI jobs pass.**

## Green Preconditions

The activation binds the remotely green Stage Q result and the exact Stage P/T
implementation milestone:

- Stage Q result commit `9832ae5e60c42bf975ccfdd22740267ef802d191`,
  CI `32827957362`;
- Stage P/T implementation commit
  `7ba4f7c30f260bc7603e8928ad8d9ff010e54872`, CI `32906104408`;
- Base Python job `97990455561`; and
- Optional Neuro Readers job `97990455765`.

The activation also freezes the byte count and SHA-256 of all six runtime,
test, documentation, and machine-record artifacts used by Stage P.

## Enabled Operation

After this activation itself is remotely green, it enables exactly one real
Stage P execution over the already-consumed Stage Q private capability:

- nine sequential participant folds;
- 468 parameter-update fits, below the registered 540-fit maximum;
- 495 target-blind prediction sets, below the 900-set maximum;
- 41,472 private prediction rows;
- zero held-out-E targets;
- zero held-out-T signal or targets;
- zero scores and zero Stage T delivery; and
- zero retry, rerun, post-target update, or analysis network bytes.

The consumed marker is written before any private capability or model open.
Each fold runs in a fresh spawned child under one CPU thread and the shared
3,600-second, 1 GiB RSS, and 512 MiB private-output envelope.

## Next Barrier

If the one Stage P invocation succeeds, its only public output is an aggregate,
hash-only prediction freeze. That exact freeze must be committed, pushed, and
remotely green before a separate Stage T activation can deliver targets or
score. A failed consumed invocation cannot be repaired or repeated.

## Claim Boundary

Engineering capability enabled after the remote barrier: one bounded,
target-firewalled real model execution can freeze predictions from the existing
Stage Q derivatives.

Scientific claim not established: this activation has not run a real model,
produced a prediction freeze, delivered a target, generated a score, or shown
unseen-participant prediction or EEG information beyond recorded EOG.
