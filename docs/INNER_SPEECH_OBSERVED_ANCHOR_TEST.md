# Observed-anchor successor: one gate, then one scientific test

The October 2 **approved** response authorizes the successor proposed in
[the all-ten census closeout](INNER_SPEECH_EVENT_CENSUS.md). The fixed
[plan](../registries/inner_speech_observed_plan.v0.json) changes event eligibility
and missing-timing controls, not the scientific endpoint or model family.

The question remains: does EEG add imagined-word information beyond peripheral
physiology/timing and every primary null in the same nine of ten people, with
mean gain at least 0.02 nats? All eight arms and all three conditions remain.
No language model, architecture search or secondary rescue is introduced.

## Fixed admission and comparison

1. Independently decode only Status under pinned pre-repair author/MNE semantics
   and compare exact codes, chronology and timestamps to the frozen decoder.
   Require full-stream agreement, not merely equal counts. This also protects
   nuisance start/rest timing. Any disagreement stops before physiology.
2. Identify exactly 200 original slots per person from observed phase order.
   Each has four or five distinct phases, at most one missing. Repeated phases,
   ambiguous boundaries, wrong counts or invalid observed intervals refuse.
   Missing cue/action/relax excludes that unique slot; missing start/rest does
   not. Permit at most seven exclusions cohort-wide, no inferred words/times.
3. Preserve original nominal folds and both levels of original-neighbour
   embargo before intersecting with eligible rows. All thirty condition/split
   preflights must pass before any physiological window or fit.
4. Run the unchanged fixed spectral/ridge/calibration comparisons. P has 88
   features: 77 peripheral, eight timing/order values, and three availability
   flags. All learned arms share the amended P; its sqrt-dimension scaling
   changes explicitly. This is not an identical retry of either consumed run.
5. Freeze all thirty prediction pairs, push and verify only that hash freeze,
   then score once. Report every participant, condition, null and exclusion.

The Status/slot/split gate is limited to 120 seconds from overall launch,
256 MiB RSS and 1 MiB output. The entire attempt, including freeze commit/push
and scoring, is limited to 20 minutes, 1 GiB RSS and 32 MiB generated output.
One numerical worker; no downloads. Any failure consumes the attempt.

## Commands and boundaries

The new wrapper reuses the original identity, budget, failure and one-shot
scoring lifecycle. Default invocation is dry-run. After generated validation,
independent review and both remote CI checks:

```powershell
$env:PYTHONPATH='src'
.venv\Scripts\python.exe -u scripts/test_inner_speech_observed.py predict --approval-text approved
# Only after complete freeze is committed, pushed and remotely verified:
.venv\Scripts\python.exe -u scripts/test_inner_speech_observed.py score --freeze-commit THE_PUSHED_SHA
```

Never inspect raw events, physiological arrays, per-trial targets/predictions
or weights. Inspect only sanitized status, qualification/failure, hash freeze
and final aggregate. Preserve prior failed attempts and structural diagnostics.
No automatic retry, broader exclusion, time extension or partial scoring.

A positive result supports only a within-person, same-day conditional
prediction increment on structurally eligible closed-set trials. Exclusions
need not be missing-at-random. Neither success nor failure proves cortical
origin, cue-independent thoughts, arbitrary text, unseen-person transfer,
prospective usability or clinical benefit.

## Pre-data implementation checks

77 focused/generated regression tests passed in 6.486 seconds; Ruff passed.
The independent decoder follows inspected pinned MNE 0.22 source semantics;
80 generated-signal comparisons additionally passed against installed MNE
1.12.1, not a runtime execution under 0.22. Its reference path imports neither
MNE nor NumPy and decodes only Status bytes. The original reader is unchanged.
Independent review found no remaining blocker in the gate/lifecycle wrapper.
Generated checks cover phase ambiguity, original-slot preservation, both
embargo levels, all-thirty preflights, cohort-wide exclusions, missing-value
flags, default-route compatibility and consume-before-load one-shot scoring.
These checks establish implementation behavior, not participant eligibility.
