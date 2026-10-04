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

## Observed result: the all-trial design is blocked, not the neural hypothesis

The approved invocation completed once in **14.172 seconds**, at **43.07 MiB
RSS**, using `9afb73141d2e0c3af487b8ebce57fc4e08c188f2` after both remote CI jobs
passed (workflow `36594412546`). The
[complete sanitized census](../registries/inner_speech_event_census_result.v0.json)
contains all ten participants and all 10,515 retained events. Every full-file
source hash passed. Both prior failures, the first audit and scientific code
remained unchanged. No failure marker was created; no retry occurred.

All 50 runs had unambiguous observed start/end boundaries. There were no
unrecognized retained words or nonincreasing sample pairs. Every observed
adjacent interval checked was within its registered range. These statements
apply to the **existing decoder's output**, not an independent raw-trigger
reconstruction or scientific trial qualification.

Counts below combine pronounced, inner-speech and visualization runs; 200 is
the nominal per-person trial count, not a count of confirmed labels.

| Person | Starts | Cues | Actions | Relax | Rest | Contiguous cue/action/relax |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 | 200 | 200 | 200 | 200 | 199 | 200 |
| 02 | 199 | 200 | 200 | 200 | 200 | 200 |
| 03 | 199 | 200 | 200 | 200 | 200 | 200 |
| 04 | 200 | 200 | 200 | 200 | 200 | 200 |
| 05 | 198 | 199 | 200 | 200 | 199 | 199 |
| 06 | 199 | 200 | 199 | 200 | 200 | 199 |
| 07 | 200 | 200 | 199 | 200 | 200 | 199 |
| 08 | 200 | 199 | 200 | 200 | 199 | 199 |
| 09 | 200 | 200 | 199 | 199 | 200 | 198 |
| 10 | 200 | 199 | 200 | 200 | 200 | 199 |
| **Total** | **1,995** | **1,997** | **1,997** | **1,999** | **1,997** | **1,993** |

Three start-to-action transitions lack an intervening direction cue (people
05, 08, 10). Three cue-to-relax transitions lack an action marker (06, 07, 09),
and one action-to-rest transition lacks relax (09). Thus the deficit is not
confined to optional rest or concentration timing. Five missing start markers
also cause start-anchored blocks to combine multiple cue/action sequences.
Person 04 has one more attention question than answer; person 10 lacks the
baseline-end marker and has two pulses excluded by the frozen duration rule.
The census cannot identify those excluded pulses' codes. No event was repaired.

**Belief update:** a rest-only amendment cannot make the all-2,000-trial,
observed-label/action protocol executable. This is an event-identification
constraint, not a negative EEG result. Conversely, 1,993 contiguous core
sequences (99.65% of the nominal total) keep an observed-anchor study plausible.
They are candidate sequences, not 1,993 certified, independent or usable trials.
There were zero physiological windows, parser calls, features, fits or scores.
This says nothing about thought-to-text accuracy or cortical attribution.

## Evidence-led next priority: reconcile extraction, then change the study once

Do not launch another scientific attempt or add another permissive parser case.
First settle one concrete ambiguity: real trigger omissions versus extraction
semantics. Our reader masks to 16 bits before edge detection. The reviewed
[MNE 0.22 BDF reader](https://github.com/mne-tools/mne-python/blob/v0.22.0/mne/io/edf/edf.py)
retains 17 bits, while the author's
[event-processing code](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/events_analysis.py)
removes the overflow-only code after event extraction. These operations are
not generally equivalent; this census does **not** establish that the difference
caused any observed deficit. The author's correction routine also estimates
missing timestamps and chooses a missing direction from count imbalance; that
routine is not admissible as observed-label evidence for our frozen study.

Propose **one newly frozen successor**, with a single up-front whole-cohort
Status-only decoder-agreement gate, followed conditionally by the substantive
EEG-versus-peripheral test. The gate gets at most 120 seconds/256 MiB/1 MiB,
no repaired events or inferred labels. Compare source-compatible pre-repair
extraction with the frozen decoder, privately including exact cue/action/relax
identities, order and timestamps, exporting only aggregate agreement and
disagreement categories. Fix both definitions before access; never choose
whichever creates more usable trials. Any disagreement stops before physiology.

If core anchors agree and original trial slots are uniquely identifiable,
uniformly exclude only incomplete cue/action/relax slots, at most **seven**
across the cohort. Retain all ten people, all three conditions and all eight
arms; represent absent non-target start/rest timing as unavailable. Seven is
a proposed ceiling, not proof that seven distinct exclusions or 1,993 eligible
trials have been established. Small exclusion fractions do not bound selection
bias. Freeze slot identification, original-order folds/embargo, nuisance
availability features and eligibility before physiological access. Never infer
missing words or silently renumber time to make folds easier. Refuse if any
slot assignment, participant/condition coverage or fixed split is invalid.

The proposed successor keeps the prior **20-minute overall cap**, including
the gate, freeze commit/push and one final score; 1 GiB overall RSS, 32 MiB
generated output, one worker, no downloads. Keep the same models, calibration,
primary mean inner-speech NLL gain of 0.02 nats and same 9/10 people beating
every primary control. Freeze once, score once, retain every null and condition,
and stop without retry on any failure. No hyperparameter search or post-score
rescue. This conditional scientific attempt requires **fresh approval**;
today's census grants no successor access, exclusions, training or scoring.
