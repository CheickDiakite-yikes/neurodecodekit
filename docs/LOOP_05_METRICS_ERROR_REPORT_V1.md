# Loop 5 - Metrics + Error Report v1

Date: 2026-06-29
Closed: 2026-07-01

Status: Done. Code, tests, CLI help, synthetic smoke output, Markdown trackers,
workbook trackers, and closeout documentation are complete.

See also: `docs/BUILD_NOTES.md` for the build journal, environment constraints,
and next-agent handoff notes.

## Question

Can every run produce an honest report without needing a notebook?

## Current Result

Complete for v1. The project now has a `neurodecode report` command that turns target and
prediction rows into a compact report card with metrics, examples, warnings,
runtime, and optional cache/storage metadata.

Implemented behavior:

- `neurodecode report` accepts one-target-per-line and one-prediction-per-line
  text files.
- Reports include:
  - CER
  - WER
  - exact-match count/rate
  - keyboard-distance diagnostics
  - corpus-level edit counts
  - example rows
  - worst examples
  - runtime
  - warnings
  - optional B2Q-mini cache summary
- Reports can be written to JSON and Markdown from the same report dictionary.
- `--cache` attaches cache shape, schema, storage size, and cache warnings.
- `--identity-smoke` supports synthetic plumbing checks by copying targets into
  predictions and adding an explicit not-a-model-result warning.

## Acceptance Gate

Met.

- Report runs from CLI on text target/prediction files.
- Report runs from CLI on a synthetic cache with `--identity-smoke`.
- JSON and Markdown artifacts are written.
- Metric/report edge cases are tested.
- The command does not require real Brain2Qwerty / SpanishBCBL data.
- The identity smoke output carries explicit warnings that it is not a model
  result.

## Verified Commands

These commands passed locally during closeout on 2026-07-01:

```bash
python -m unittest tests.test_report tests.test_cli_report
```

Result:

```text
Ran 8 tests
OK
```

```bash
python -m unittest discover -s tests
```

Result:

```text
Ran 45 tests
OK
```

```bash
neurodecode report --help
```

Result: command help printed successfully.

```bash
neurodecode make-synthetic-shard --out cache/loop5_synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report \
  --cache cache/loop5_synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/loop5_synthetic_report.json \
  --out-md cache/loop5_synthetic_report.md \
  --run-name loop5_synthetic_identity_smoke \
  --split synthetic-smoke
```

Result:

```text
shape=(32, 4, 12)
cache bytes=7206
n_examples=32
exact_match_rate=1.0
corpus_cer=0.0
corpus_wer=0.0
warnings=targets_loaded_from_cache_labels,
         identity_smoke_predictions_equal_targets_not_model_result,
         cache:synthetic_cache_not_real_neural_data
```

## Current Limits

- `--identity-smoke` is only a plumbing check. It is not a baseline and should
  not be reported as model performance.
- The report command does not train or run a decoder yet.
- Predictions are currently supplied as text rows. Future loops can add model
  runners that emit those rows automatically.
- No subject/session/generalization split enforcement exists yet; reports only
  record the split label provided by the user.

## Decision

Loop 5 is closed. Proceed to Loop 6: LM-only / Prior-only Baseline.

The next loop should add a deliberately no-brain baseline and make its report
artifact directly comparable to this report format. That keeps the project
honest before any neural model scores are introduced.

## Managed-environment note

On 2026-07-01, the local GitHub push/export path was blocked by the
admin/reviewer layer, and the prior workbook update path had already been
interrupted by workstation tooling controls. A later workbook update succeeded
through the bundled spreadsheet runtime. The closeout remains a local commit
unless the user explicitly re-approves external export/push.

The next agent should avoid retrying blocked export paths unless the user
explicitly re-approves the action and the environment is known to allow it.
