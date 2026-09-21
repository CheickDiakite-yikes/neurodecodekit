# SPEECH-REPRO-1 recovery stopped at calibration eligibility

September 21, 2026. **No held-out score or scientific result was produced.**
The approved recovery stopped after 171.66 seconds (2 minutes 52 seconds),
well below its two-hour cap. This invocation is terminal and must not be retried.

## Confirmed outcome

All 13 source identity, timing and all-channel padding checks passed. The
source-backed timing correction therefore resolved the previously observed
alignment blocker. Five pair reports confirm reuse of all 50 existing EEGNet
fits, unchanged fold selections and extraction metadata. Their 291 online
predictions were regenerated in memory but never evaluated.

Both final participant-3 covert recordings were extracted. Before fitting any
new EEGNet fold, `calibration_folds` raised:

```text
ValueError: Ten-fold calibration needs at least ten original trials per class
```

The integer-label and five-class checks precede this guard and passed. Therefore
at least one of the five classes has fewer than ten calibration examples; no
class is absent. Exact counts and word identities were not inspected in this
status review. This is **our executor's eligibility requirement**, not proof
that ten-fold cross-validation is mathematically impossible or that the source
is corrupt. Whether this extra support rule matches the author procedure needs
a calibration-only compatibility audit.

No new EEGNet checkpoints, complete prediction archive, prediction freeze,
scoring marker or aggregate scientific result exists. The new compact models
and partial probabilities were RAM-only and were lost on exit. Existing source,
50 checkpoints, both failure records and sealed targets remain local. Nothing
was deleted or uploaded. Online labels were not released to a scorer.

## Belief update and next priority

We verified timing recovery and checkpoint reuse, but neither reference word
prediction nor EEG's increment beyond nuisance signals has been evaluated.
This is not a biological null or progress on the scientific endpoint.

The missing preflight was calibration eligibility across all six pairs; it
should have been checked before either execution. More compute will not resolve
the present guard. The next proposed action is one calibration-only audit of
aggregate class support, label mapping and the pinned author's fold construction,
with online targets sealed. Establish whether the guard is unnecessarily strict
or the selected source conflicts with the fixed procedure before proposing any
amendment. No new audit execution, rule change or successor run is authorized
by this failure record. Do not drop a participant/condition, shorten training,
score a partial subset or automatically rerun. The heartbeat is paused.

Evidence: recovery implementation `059b75bd7c6a1b00098e65f583abfb53a5088138`
(65 focused tests and both remote CI jobs passed); five local recovery pair
reports; process exit 1; local
`data/speech_repro_1_recovery_20260921/execution_failed.json`, SHA-256
`acb4394ead52bbe084e547b192e9a92012841bd0bdeddd8dc08daa7645cc8dc5`.
The [original failure](SPEECH_REPRODUCTION_EXECUTION_FAILURE.md) and
[approved recovery scope](SPEECH_REPRODUCTION_RECOVERY.md) remain historical
records, not successful scientific outcomes.
