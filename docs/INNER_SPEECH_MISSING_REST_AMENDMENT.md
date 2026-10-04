# Approved missing-timing amendment and single run

September 29, 2026. The maintainer approved the amendment described in the
[structural audit](INNER_SPEECH_EVENT_AUDIT.md), validation, then one complete
20-minute experiment conditional on all ten participants qualifying.

The [amended plan](../registries/inner_speech_missing_rest_plan.v0.json)
inherits the entire original frozen comparison except the stated rest/timing
changes. The original plan, failures and structural audit remain immutable.
This is not represented as an unchanged retry or a successful decoding result.

An otherwise intact within-run trial may lack only its rest marker immediately
before the next trial start. Its rest timestamp remains null. Both affected
timing features—the trial's relaxation duration and the next trial's preceding
gap—retain observed values when available and otherwise use a fixed zero with
an explicit availability flag. The first trial has no preceding rest. Every
learned arm uses the same 87-column P block (77 peripheral, eight timing, two
flags), standardized on training rows only and normalized by sqrt(87). This
changes the nuisance model; unseen training missingness cannot be learned.

All other event, class, trial, split and window checks remain mandatory. An
unmeasurable rest interval is reported unavailable, never as passed. All ten
people qualify before any physiological window or model fit. Missing targets,
other missing core events or any other failure stop the whole attempt.

Reuse the existing reader, model and one-shot lifecycle through the fixed
`scripts/test_inner_speech_missing_rest.py` wrapper. It has a distinct local
attempt and distinct public freeze/result; the strict original route remains
the default. No new configurable source, path, hyperparameter or resource cap.
The 1,200-second clock includes qualification, prediction, hash-freeze commit
and push, remote freeze verification and the single score. RSS stays at 1 GiB,
output at 32 MiB, free disk at least 20 GiB, and one numerical worker.

After generated validation and remote CI pass, invoke `predict` once with the
actual approval recorded. If and only if all 30 pairs complete with no failure,
commit/push only the new hash freeze and invoke this wrapper's `score` once
with the remotely verified freeze commit. Do not wait for freeze CI before
scoring if it would consume the execution deadline; check that CI separately.
Never bypass failure/scoring markers or restart an expired clock. Only hashes,
sanitized metadata and aggregate results may leave local private storage.

The unchanged primary question is whether EEG adds inner-word information over
the amended peripheral/timing model and every primary control, with mean NLL
gain at least 0.02 nats and the same 9/10 people positive against all five controls.
All eight arms and all three conditions must remain visible. Neither outcome
establishes cortical origin, cue-independent thoughts, arbitrary text, new-day
or unseen-person transfer, prospective live performance or clinical utility.

Generated validation: 54 focused tests passed in 3.399 seconds; Ruff passed.
Coverage includes strict/default behavior, the narrow missing-rest exception,
both timing flags, unchanged physiological windows, last-participant failure
before any features/fits, both routes' one-shot score guards and sanitized
failure projection without a second parse. A metadata-only path check admitted
the canonical local destination and confirmed no successor attempt/freeze/result
exists, without opening participant files. Remote CI is checked before launch.

## Consumed execution result: trial-start mismatch in participant 02

The single approved invocation used `28983dafabb07cf3820de2b7bf199ecc669c7c69`
after both CI jobs passed (workflow `36589987257`). It stopped after **12.266
seconds**, at **45,846,528 bytes (43.72 MiB)** peak RSS. The earlier implementation
commit's base-only CI error was corrected before any real-data access; it did
not consume an experiment attempt.

All ten recordings passed full-file SHA verification. Participant 01 completed
all 200 trials and all three condition/split preflights under the amendment.
Participant 02 completed **72 trials**, then the parser encountered a
**direction cue where the next trial-start marker was required**. This is a
different structural mismatch from the admitted missing-rest case. The
[sanitized failure record](../registries/inner_speech_missing_rest_failure.v0.json)
separates observed failure metadata from consequences established by the
frozen control flow.

The all-ten qualification boundary worked: **zero physiological windows,
features, fits, predictions or scores** followed. No complete qualification,
freeze, score-consumed marker or scientific result exists. Status and
target-bearing codes were decoded for the first two people inside the runner;
raw event rows and target identities were not inspected or exported. The
attempt is consumed and its local failure evidence remains unchanged. There
was no retry, inferred timestamp, dropped trial or post-failure source read.

This does not estimate a neural effect or reject the primary hypothesis. It
establishes that the cohort's event compatibility is more complex than the
single rest-marker omission. The exact cause of the trial-start mismatch,
later trial alignment and later participants' compatibility remain unknown.

## Next priority: establish cohort-wide alignment before another model run

A separately approved **one-pass event-structure-only census of all ten
recordings** should enumerate structural exceptions across the whole cohort,
not stop at the first person or first mismatch. Proposed limits: 120 seconds,
256 MiB RSS, 1 MiB sanitized output, one worker, no new downloads. Decode only
Status, collapse direction/answer identities, preserve raw inputs, and export
only structural counts and categories. No physiological analysis, repaired
event list, label inference, model fitting or scoring.

Use that complete structural picture to decide whether one coherent policy
can retain unambiguous observed cue/action alignment for all trials. If not,
this frozen study is infeasible as specified; further piecemeal exceptions
would change the study without resolving its identification problem. This
proposal grants no new data access or execution authority.
