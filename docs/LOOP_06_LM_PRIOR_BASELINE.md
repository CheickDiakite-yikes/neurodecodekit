# Loop 6 - LM-only / Prior-only Baseline

Date: 2026-07-01
Closed: 2026-07-01

Status: Done. A no-brain prior baseline is implemented, tested, wired into the
standard report artifact, and documented.

## Question

How much performance can come from label/text priors before using neural data?

## Current Result

Complete for v1. The project now has a `neurodecode prior-baseline` command that
predicts target rows without reading neural windows as signal.

Implemented behavior:

- `neurodecode prior-baseline` accepts eval targets from `--targets`, or from
  `--cache` labels when `--targets` is absent.
- Optional train priors can come from `--train-targets` or `--train-cache`.
- If no train source is provided, the command fits on eval targets and emits a
  smoke-only warning.
- Strategies: `most-frequent`, `frequency-sample`, and `uniform-random`.
- Outputs: predictions text, JSON report, Markdown report, and baseline
  metadata inside the report.
- Report warnings explicitly say no neural signal was used.

## Acceptance Gate

Met.

- Baseline exists and is runnable from the CLI.
- It can run from text targets.
- It can run from a synthetic B2Q-mini cache.
- It writes predictions and standard JSON/Markdown reports.
- Report includes baseline metadata and no-neural-signal warnings.
- Unit and CLI tests cover deterministic behavior and edge cases.
- The command does not require real Brain2Qwerty / SpanishBCBL data.

## Verified Commands

These commands passed locally during closeout on 2026-07-01:

```bash
python -m unittest tests.test_prior_baseline tests.test_cli_prior_baseline tests.test_report
```

Result:

```text
Ran 15 tests
OK
```

```bash
python -m unittest discover -s tests
```

Result:

```text
Ran 55 tests
OK
```

```bash
neurodecode prior-baseline --help
```

Result: command help printed successfully.

```bash
neurodecode make-synthetic-shard --out cache/loop6_synthetic_tiny.npz --samples 32 --channels 4 --times 12 --classes 8
neurodecode prior-baseline \
  --cache cache/loop6_synthetic_tiny.npz \
  --out-predictions cache/loop6_prior_predictions.txt \
  --out-json cache/loop6_prior_report.json \
  --out-md cache/loop6_prior_report.md \
  --run-name loop6_prior_most_frequent \
  --split synthetic-smoke
```

Result:

```text
strategy=most-frequent
top_target=G
top_count=6
n_examples=32
exact_match_rate=0.1875
corpus_cer=0.8125
corpus_wer=0.8125
warnings=prior_baseline_no_neural_signal,
         prior_fit_on_eval_targets_for_smoke_only,
         cache:synthetic_cache_not_real_neural_data
```

## Current Limits

- This is a prior-only baseline, not an LM with external text corpora.
- `frequency-sample` and `uniform-random` are deterministic by seed but still
  intentionally weak.
- If no train source is provided, fitting on eval targets is only acceptable for
  smoke testing. Real experiments should use separate train labels.
- No subject/session/sentence split enforcement exists yet.
- The command does not yet run a neural model; it only produces a comparator.

## Decision

Loop 6 is closed. Proceed to Loop 7: Template / Nearest-Centroid Baseline.

The next loop should train a tiny transparent classifier on cache windows and
write the same report format so we can compare:

1. identity smoke
2. no-brain prior-only baseline
3. simple neural-window template baseline

This keeps the project honest before any deep model is introduced.
