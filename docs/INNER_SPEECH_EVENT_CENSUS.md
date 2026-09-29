# INNER-SPEECH-EVENT-CENSUS-1: whole-cohort structural census

The maintainer's **approved** response authorizes exactly the proposed all-ten
event-structure census after the consumed `INNER-SPEECH-TEST-1-MR1` failure.
It does not authorize another decoding attempt or any event repair.

## Fixed scope

- All ten already acquired ds003626 v2.1.2 `ses-01` recordings; no downloads.
- One invocation, 120 seconds, 256 MiB RSS, 1 MiB generated sanitized output,
  one numerical worker; maintain the existing 20 GiB free-disk floor.
- Full-file opaque SHA256 identity checks, technical BDF headers and Status
  decoding only. Never read physiological windows, train, predict or score.
- Reuse the frozen reader and family projection. No alternate decoder,
  filtering change, reconstructed event list, inferred label or timestamp.
- Preserve both failed scientific attempts, the first audit and scientific
  code. A distinct exclusive local output directory records this census.
- No automatic retry, including after a source, resource or process failure.
  Publish no partial census as a complete cohort result.

## Measurements fixed before data access

For each entire recording, retain collapsed event-family counts, all adjacent
family-transition counts, and the count of nonincreasing sample pairs.
Direction, answer and condition identities collapse before aggregation;
unknown numeric codes are represented only as `unrecognized_status_word`.
No raw rows, sample positions, timestamps or target values leave the process.

Inventory runs only where observed start/end boundaries are unambiguous:
exactly one run start followed by one end, without nesting. Report all other
boundary markers and events outside these blocks; never infer a boundary.
Retain per-run family counts, not condition identities.

For every observed trial start, examine the block up to the next trial start
or run boundary. Aggregate zero/one/multiple cue, action, relax and rest
counts, whether its immediate prefix is start/cue/action/relax, and the
ending boundary family. These are **anchor blocks, not qualified trials**.
Separately count every cue's preceding family and whether its immediate
successors are action/relax, so missing trial starts cannot hide cue anchors.
All transitions also retain each relax marker's immediate successor family.

For immediately adjacent start/cue, cue/action, action/relax and relax/rest
pairs only, report counts inside/outside the existing parser's interval
ranges: `(0,5]`, `[0.375,3]`, `[2,4]`, `(0,3]` seconds respectively. No duration
or imputed interval is exported. Absent/interrupted pairs are not validated.

These checks cover the full event stream even after an anomaly; they do not
claim to enumerate every possible defect. Matching totals cannot prove word
identity, condition layout, trial alignment, cortical origin or decoding
performance. The scientific parser is not called and no qualification is
promoted from this census.

## Execution and decision

`scripts/census_inner_speech_events.py` defaults to a no-data dry run.
After generated checks, independent review, push and both remote CI jobs:

```powershell
$env:PYTHONPATH='src'
.venv\Scripts\python.exe -u scripts/census_inner_speech_events.py --execute-approved-census
```

Read only the sanitized terminal result/failure. Commit the complete
sanitized aggregate and its interpretation, never source events or targets.
Use the census to decide whether a coherent prospective amendment could
retain all observed cue/action anchors without inventing labels. If not,
the current frozen study is infeasible as specified. Any implementation
amendment and new scientific attempt require a separate decision; this
approval cannot be carried forward to another run.

Pre-data validation: 10 generated/mocked census tests passed in 0.017 seconds;
36 existing reader/audit/amendment tests passed in 1.267 seconds. Ruff passed.
An independent static review found no remaining blocker after nested run
components were made explicitly ambiguous. These are implementation checks,
not evidence that any acquired recording qualifies for scientific analysis.
