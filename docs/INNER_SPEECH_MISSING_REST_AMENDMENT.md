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
