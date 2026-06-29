# Loop 3 - Safe Tiny-Shard Selector

Date: 2026-06-29

Status: Done for local safety planning and dry-run download gating.

## Question

Can a user request the smallest meaningful shard without accidentally
downloading the universe?

## Result

Yes. The selector now treats a tiny shard as an explicit download plan with
file-count limits, byte limits, exact path reporting, and separate execution
acknowledgement.

Implemented behavior:

- `select-tiny` accepts `--max-files` and `--max-total-gb`.
- Default safety limits are 8 files and 5 GB.
- When sizes are known, the selector prefers the smallest complete raw+log
  candidate before falling back to deterministic path order.
- Selection JSON persists safety limits, known bytes, missing-size counts, and
  safety warnings.
- `download-selection` prints a concrete plan before either dry-run or execute.
- `download-selection` remains dry-run by default.
- Real downloads still require `--execute`.
- `--execute` fails safely when selected files lack size metadata unless the
  user also passes `--allow-unknown-size` after reviewing the exact file list.
- The older `--dry-run` spelling is accepted as an explicit no-download mode.

## Acceptance Gate

Met.

- Dry-run prints exact files and size estimate.
- Real download requires `--execute`.
- Unknown-size real downloads require an additional acknowledgement.
- File-count and known-byte caps fail before any Hugging Face call.
- Tests cover synthetic selector edge cases and CLI dry-run/execute behavior.

## Verified Commands

```bash
python -m unittest tests.test_selection tests.test_cli_selection
```

Result:

```text
Ran 9 tests
OK
```

```bash
python -m unittest discover -s tests
```

Result:

```text
Ran 31 tests
OK
```

## Current Limits

- File sizes depend on the manifest input. Plain Hugging Face path listings may
  not include sizes, so unknown-size warnings are expected until a richer file
  list is available.
- Size-aware choice is intentionally simple: prefer exact raw+log matches, then
  known smaller totals, then deterministic path order.
- The selector still does not fetch remote metadata by itself. That is a
  deliberate safety decision.

## Decision

Proceed to Loop 4: B2Q-mini Cache v0.

The next loop should stabilize the cache metadata contract so both synthetic
and real extracted `.npz` files can be loaded, inspected, and compared with the
same small API.
