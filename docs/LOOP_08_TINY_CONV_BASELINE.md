# Loop 8 - Tiny Conv / EEGNet-style Baseline

Date: 2026-07-01
Closed: 2026-07-01

Status: Done for the optional-ML implementation path. The command, model
scaffold, report metadata, dependency guardrails, and tests are implemented.
The current local venv does not have Torch installed, so the actual training
smoke tests are present but skipped locally until `pip install -e ".[ml]"` is
available.

## Question

Can a small neural model beat transparent baselines on the tiny loop?

## Current Result

Loop 8 adds:

- `neurodecode tiny-conv-baseline`
- `src/neurodecodekit/models/tiny_conv_baseline.py`
- one-cache deterministic stratified holdout
- explicit `--train-cache` / `--eval-cache`
- CPU-safe defaults: `--device cpu`, `--num-threads 1`
- training controls for epochs, batch size, learning rate, hidden channels
- JSON/Markdown report output through the standard report artifact
- baseline metadata for:
  - model name
  - split mode
  - train/eval rows
  - train/eval label counts
  - feature shape
  - train/eval accuracy
  - loss history
  - optional dependency extra
  - warnings

The tiny model is a temporal-then-spatial ConvNet with adaptive pooling. It is
inspired by EEG/MEG ConvNet baselines but intentionally much smaller than a real
Brain2Qwerty model.

## Acceptance Gate

Met with an environment caveat.

- CLI command exists and help works.
- Base install stays lightweight.
- Missing Torch produces a helpful install message:
  `pip install -e '.[ml]'`.
- Tests cover helper behavior, CLI validation, graceful dependency errors, and
  Markdown report metadata.
- Torch-enabled synthetic training tests are included and will run when the
  `ml` extra is installed.
- No real Brain2Qwerty / SpanishBCBL data is required in CI.

The actual local Torch training smoke was not executed because Torch is not
installed in the current Bain-managed venv. No heavy ML dependency download was
attempted from this environment.

## Verified Commands

These commands passed locally during closeout on 2026-07-01:

```bash
python -m unittest tests.test_tiny_conv_baseline tests.test_cli_tiny_conv_baseline tests.test_report
```

Result:

```text
Ran 15 tests
OK (skipped=2)
```

The two skipped tests are the Torch training smoke tests.

```bash
neurodecode --help
neurodecode tiny-conv-baseline --help
```

Result: command help printed successfully.

```bash
neurodecode make-synthetic-shard --out cache/loop8_synthetic_tiny.npz --samples 64 --channels 4 --times 12 --classes 4
neurodecode tiny-conv-baseline --cache cache/loop8_synthetic_tiny.npz --epochs 2
```

Result on the current base venv:

```text
error: Tiny Conv baseline requires optional ML dependencies: `pip install -e '.[ml]'`.
```

## ML-enabled Smoke Command

Run this in an environment where optional ML dependencies are allowed:

```bash
pip install -e ".[ml]"

neurodecode make-synthetic-shard \
  --out cache/loop8_synthetic_tiny.npz \
  --samples 96 \
  --channels 4 \
  --times 12 \
  --classes 2

neurodecode tiny-conv-baseline \
  --cache cache/loop8_synthetic_tiny.npz \
  --train-fraction 0.75 \
  --epochs 30 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --out-predictions cache/loop8_tiny_conv_predictions.txt \
  --out-json cache/loop8_tiny_conv_report.json \
  --out-md cache/loop8_tiny_conv_report.md \
  --run-name loop8_tiny_conv_smoke \
  --split synthetic-holdout
```

## Interpretation

Loop 8 should not be read as a performance claim. It creates the first
deep-learning slot in the repeated loop:

1. Loop 6: no-brain prior baseline.
2. Loop 7: transparent nearest-centroid window baseline.
3. Loop 8: optional tiny ConvNet over the same cache/report contract.

A tiny synthetic score only verifies that the PyTorch path can train, predict,
and write a report. It does not imply real SpanishBCBL decoding performance.

## Current Limits

- Torch is optional and not installed in the current local venv.
- The model is a classifier over event labels, not a sequence decoder.
- No session/subject leakage controls are added yet.
- No calibration, confidence, checkpointing, or early stopping is implemented.
- No GPU path has been tested locally; CPU remains the default.

## Decision

Loop 8 is closed. Proceed to Loop 9: CTC Character Decoder Scaffold.

The next loop should prove a minimal sequence-decoding interface on synthetic
data first. It should not depend on real timing assumptions until event labels,
durations, and target text alignment are explicit.
