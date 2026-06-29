# Loop 5 - Metrics + Error Report v1

Date: 2026-06-29

Status: Pending handoff. Code and tests are present, but the loop is not
formally closed because the local Excel tracker/final closeout step was
interrupted by an admin/tooling block on this machine.

## Question

Can every run produce an honest report without needing a notebook?

## Current Result

Partial but useful. The project now has a `neurodecode report` command that turns target and
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

Not formally met yet.

- Report runs from CLI on text target/prediction files.
- Report runs from CLI on a synthetic cache with `--identity-smoke`.
- JSON and Markdown artifacts are written.
- Metric/report edge cases are tested.
- The command does not require real Brain2Qwerty / SpanishBCBL data.
- Remaining closeout work: rerun full verification on the next machine, update
  `NEURODECODEKIT_20_LOOP_TRACKER.xlsx`, then change this loop from pending to
  done if the checks still pass.

## Verified Commands

These commands passed locally before the admin/tooling interruption:

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

## Current Limits

- `--identity-smoke` is only a plumbing check. It is not a baseline and should
  not be reported as model performance.
- The report command does not train or run a decoder yet.
- Predictions are currently supplied as text rows. Future loops can add model
  runners that emit those rows automatically.
- No subject/session/generalization split enforcement exists yet; reports only
  record the split label provided by the user.

## Decision

Do not proceed to Loop 6 yet.

The next agent should complete Loop 5 closeout first:

1. Rerun the focused and full test commands above.
2. Run `neurodecode report --help`.
3. Run a synthetic report smoke and inspect the JSON/Markdown outputs.
4. Update the Excel tracker and Markdown tracker.
5. If all checks pass, mark Loop 5 done and then proceed to Loop 6.
