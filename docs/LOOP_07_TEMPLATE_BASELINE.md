# Loop 7 - Template / Nearest-Centroid Baseline

Date: 2026-07-01
Closed: 2026-07-01

Status: Done. A tiny nearest-centroid baseline over cache windows is
implemented, tested, wired into the standard report artifact, and documented.

## Question

Is there separable signal in the windows before deep learning?

## Current Result

Complete for v1. The project now has a `neurodecode template-baseline` command
that trains class templates from cache windows and predicts held-out cache
windows by nearest centroid.

Implemented behavior:

- `neurodecode template-baseline` accepts:
  - `--cache` for one-cache stratified train/eval holdout
  - or `--train-cache` plus `--eval-cache` for explicit train/eval cache paths
- The single-cache path uses deterministic stratified holdout by label.
- The baseline averages training windows by label.
- Prediction uses nearest squared-Euclidean distance to class templates.
- Outputs:
  - one-prediction-per-line text file
  - JSON report
  - Markdown report
  - baseline metadata inside the report
- Report warnings explicitly say the command uses neural windows but no deep
  learning.

## Acceptance Gate

Met.

- Baseline exists and is runnable from the CLI.
- It trains/evaluates in seconds on a synthetic B2Q-mini cache.
- It writes predictions and standard JSON/Markdown reports.
- Report includes baseline metadata, train/eval counts, split mode, feature
  shape, and warnings.
- Unit and CLI tests cover holdout behavior, separate-cache warnings, shape
  errors, and report output.
- The command does not require real Brain2Qwerty / SpanishBCBL data.

## Verified Commands

These commands passed locally during closeout on 2026-07-01:

```bash
python -m unittest tests.test_template_baseline tests.test_cli_template_baseline tests.test_report
```

Result:

```text
Ran 13 tests
OK
```

```bash
python -m unittest discover -s tests
```

Result:

```text
Ran 62 tests
OK
```

```bash
neurodecode template-baseline --help
```

Result: command help printed successfully.

```bash
neurodecode make-synthetic-shard --out cache/loop7_synthetic_tiny.npz --samples 64 --channels 4 --times 12 --classes 4
neurodecode template-baseline \
  --cache cache/loop7_synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/loop7_template_predictions.txt \
  --out-json cache/loop7_template_report.json \
  --out-md cache/loop7_template_report.md \
  --run-name loop7_template_nearest_centroid \
  --split synthetic-holdout
```

Result:

```text
split_mode=single-cache-stratified-holdout
train_rows=32
eval_rows=32
n_classes=4
feature_shape=(4, 12)
exact_match_rate=1.0
corpus_cer=0.0
corpus_wer=0.0
warnings=template_baseline_uses_neural_windows,
         template_baseline_no_deep_learning,
         template_single_cache_holdout_split,
         cache:synthetic_cache_not_real_neural_data
```

## Interpretation

The perfect synthetic score is expected. The synthetic cache has explicit class
bump patterns, so a transparent nearest-centroid model should recover the label
signal. This result validates the cache/model/report plumbing; it is not a real
Brain2Qwerty performance claim.

Loop 7 is meaningful because it creates the first neural-window comparator:

1. Loop 5: identity smoke verifies report plumbing.
2. Loop 6: prior-only baseline verifies what can be guessed without windows.
3. Loop 7: template baseline verifies whether cache windows contain separable
   label signal before deep learning.

## Current Limits

- The current feature is the full flattened window; there is no channel
  selection, normalization sweep, or feature engineering yet.
- The single-cache split is stratified by label, not by session, sentence, or
  subject.
- Real experiments should prefer explicit train/eval caches or split metadata.
- No probability/confidence calibration is implemented.
- No deep learning is used.

## Decision

Loop 7 is closed. Proceed to Loop 8: Tiny Conv / EEGNet-style Baseline.

The next loop should add an optional lightweight neural baseline with CPU-safe
synthetic smoke tests, while keeping the base package free of heavy ML
dependencies.
