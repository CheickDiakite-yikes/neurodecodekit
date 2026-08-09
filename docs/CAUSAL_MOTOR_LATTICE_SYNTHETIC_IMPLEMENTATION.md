# Causal Motor Lattice v0 Synthetic Implementation

Date: 2026-08-09

Status: **exact implementation qualified locally; registered execution not
started; remote-green implementation gate pending**

Machine record:
`registries/causal_motor_lattice_synthetic_implementation.v0.json`

Frozen contract:
`registries/causal_motor_lattice_synthetic_contract.v0.json`

## What Was Implemented

Work order 13 now has an exact, import-light implementation of the synthetic
Causal Motor Lattice v0 gate:

- `src/neurodecodekit/models/causal_motor_lattice.py` constructs the registered
  64-channel, three-view, 4,535-parameter Torch model only inside a lazy factory;
- `src/neurodecodekit/experiments/causal_motor_lattice_synthetic.py` binds the
  existing synthetic motor fixture to pair-anchored crops, deterministic
  projection and normalization, one frozen training recipe, check-before-final
  scoring, same-checkpoint controls, causal mutations, checkpoint replay, and
  bounded output;
- `neurodecode cml-v0-synthetic` is dry-run by default and refuses execution
  without an exact implementation commit and positive remote CI run ID; and
- `neurodecode inspect-cml-v0-synthetic` validates report and checkpoint hashes,
  members, sizes, warnings, unavailable fields, and caps without opening NumPy
  arrays.

No scientific dependency is imported when either new module is imported. The
base package remains dependency-free. NumPy, SciPy, and Torch remain lazy
optional research dependencies; this milestone installed nothing.

## Exact Model Mechanics

The implementation fails closed unless all of these match the frozen contract:

- 64 generic synthetic inputs produced by the rank-8, target-free 8-to-64
  projection with SHA-256
  `b377e42f75c6493fe44082c1dbcee278debf2cc5dfbaec3db954dede94ee4a50`;
- 33-tap one-sided mu and beta filters with their registered coefficient hashes;
- three rank-8 spatial mixers whose rows are zero-sum and unit-L2 before use;
- three fixed temporal cells and 72 fused features;
- a 24-feature bottleneck, 18 primitive logits, and 29 bounded-residual key
  logits;
- the fixed 29-by-18 incidence matrix with SHA-256
  `0d2451f4fe9354f9031ed59b007e8bc4c0aeae78a65494520abd970698c20309`;
- exact left/right hand probabilities recomputed from key probability mass; and
- exactly 4,535 trainable scalars.

The model receives only normalized signal and a mask. Pair, factor, partition,
length, time, synthetic class, event position, and peripheral proxy remain
outside the model input. The timing-only and pure-noise pair crops are checked
for byte equality before a model can be built.

## Registered Execution Shell

The execution function is present but was not invoked. It is bound to:

- one seed-5513, 600-step full-batch AdamW parameter-update run;
- 24 gradient-eligible source-train synthetic rows;
- 32 source-check rows scored once after checkpoint freeze;
- 16 synthetic final rows scored only if every check gate passes;
- nine same-checkpoint conditions per delivered partition;
- one checkpoint reload, never a second fit;
- one CPU thread, one worker, 600 seconds, 512 MiB RSS, 4 MiB output, and a
  20 GiB free-disk preflight; and
- one checkpoint NPZ plus one aggregate JSON report with no per-item target,
  label, prediction, identity, text, or path.

An existing output directory, dirty tracked worktree, mismatched contract or
source hash, nonfinite value, parameter drift, premature final access, cap
breach, or missing exact implementation proof fails closed. There is no
overwrite, retry, checkpoint selection, early stop, post-check update, or
rerun path.

## Qualification Performed

The implementation qualification used disposable synthetic arrays and
zero-update shape/control forwards only. It did not call the registered
execution function and performed no optimizer step or scoring event.

Observed static inventory:

```text
projection shape:       (64, 8), rank 8
lattice shape:          (29, 18)
mu / beta taps:         33 / 33
adapted input shape:    (96, 64, 96)
trainable parameters:   4,535
synthetic source bytes: 1,145,152
focused tests:          24 passed
complete tests:         1,380 passed; 3 expected skips; 493 subtests
complete-suite runtime: 39.26 seconds
pre-contract delta:     +24 passing tests
```

The tests cover lazy imports, contract substitution, dry-run behavior,
pair-anchor leakage, projection/FIR/lattice hashes, exact parameter accounting,
zero-update output shapes, bounded residuals, hand-key consistency,
common-mode rejection, future-tail masking, malformed model inputs, and proof
refusals. Repository-wide Ruff, compileall, all 95 registry JSON files, both
CLI help paths, dry-run JSON, and diff hygiene also pass.

## Access And Claim Boundary

Registered execution counters remain zero: no training run, optimizer step,
check score, final delivery, final score, checkpoint load, or retained output
has occurred. Every real/public/protected read, S20 or PhysioNet operation,
network or provider call, pretrained weight, external embedding, stream,
device, hardware, release, and scientific-claim counter is zero.

The next allowed action is to commit and push this exact implementation, wait
for its exact remote CI to pass, and only then invoke the one registered
synthetic execution. A failing CI parks the dependent stage.

**Engineering capability added:** NeuroDecodeKit now has a fail-closed exact
CML-v0 implementation and bounded execution shell that can be qualified before
real evidence is spent.

**Scientific claim not established:** no registered training or scoring run and
no real EEG payload was used, so this implementation establishes no EEG
information, neural advantage, decoding result, generalization, real-time or
portable behavior, home use, assistive value, or clinical utility.
