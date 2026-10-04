# SPEECH-REPRO-1: approved, bounded recovery

**Outcome: stopped before evaluation.** Timing/padding checks and reuse of all
50 existing fits succeeded, but the final calibration set failed the executor's
minimum-per-class guard before new reference training. Read the
[recovery failure and next decision](SPEECH_REPRODUCTION_RECOVERY_FAILURE.md).
This invocation is terminal; the authorization below is historical, not a retry.

September 21, 2026. The maintainer answered **"approved"** to:
"May I apply the narrow fix and complete the unchanged experiment, with a
two-hour recovery cap?" This authorizes implementation and one complete recovery
through prediction freeze, one held-out score and aggregate reporting. It does
not authorize automatic retries, partial scoring or scientific retuning.

## What changes, and what stays fixed

The [timing audit](SPEECH_REPRODUCTION_TIMING_AUDIT.md) identified an incorrect
reader assumption. Exact zero-based 2,880-sample trial grids with matching
recording length select the source's concatenated-buffer route even if trigger
edges remain. Continuous event/trigger alignment stays strict. All-channel EDF
padding validation, original buffers, action crops and filters remain intact.

Recovery uses `data/speech_repro_1_recovery_20260921`. The failed root
`data/speech_repro_1_20260921` is read-only: its failure marker, reports, weights,
source files and sealed targets are neither deleted nor overwritten. Its failure
SHA-256 remains
`cc260c268518fe2764132a57f83bf4b519ba07003c04192f036be45648fc33b6`.

Before modeling, verify the 13 selected source identities and pinned sidecars,
and validate timing/padding for every recording. No replacement raw download is
needed. Re-extract the same features for the five completed pairs; require their
extraction metadata and regenerated sealed-target hashes to match the original.
Never parse original private targets during recovery prediction.

Reuse all 50 saved EEGNet fits, verifying every checkpoint and retaining the
original four selected folds per pair. Calibration labels may verify the original
stratified split, but no calibration waveform is rescored to change selection.
Only the final pair's ten EEGNet folds are newly trained. Refit the fixed compact
comparators and regenerate probabilities; their original RAM-only state was lost.
No prior probability hash exists, so historical bit-identical reconstruction is
not claimed. Generated checkpoint replay tests check the inference implementation.

All three people, both speech conditions, 600 calibration trials, 341 online
trials, ten folds, 100 epochs, seeds, settings, nuisance comparisons and endpoint
definitions remain those in the [research decision](SPEECH_REPRODUCTION_RESEARCH_DECISION.md)
and [execution clarifications](SPEECH_REPRODUCTION_EXECUTION.md). No additional
dataset, model search or outcome-based decision is admitted.

## Budget and execution

The additional **7,200-second wall-clock budget begins at recovery invocation**
and includes verification, preprocessing, model work, committing/pushing the
prediction freeze and final scoring. Development and generated tests precede
that invocation. Keep one numerical thread, 900 seconds per stage/fit, four GiB
RSS, the combined old-plus-recovery 1.5-GiB research-payload limit, and the 20-GiB
free-filesystem floor. Source files are reused, not copied. A watchdog enforces
runtime/RSS limits; a failure preserves evidence and prohibits further execution.

After committing the implementation, invoke once with `PYTHONPATH=src`:

```text
.venv\Scripts\python.exe -u scripts/recover_speech_reproduction.py predict
```

The existing registry path receives a complete six-pair prediction hash freeze.
It binds the recovery root/start time, failed-run lineage, original artifact
hashes, models and source identities. Commit and push only that freeze; verify
the remote commit before invoking the recovery scorer once:

```text
.venv\Scripts\python.exe -u scripts/recover_speech_reproduction.py score --freeze-commit PUSHED_SHA
```

The scorer rejects failed, consumed, expired, incomplete or changed recovery
state before opening targets. It uses the unchanged registered scoring function
and consumes scoring before reading any label value. Raw data, labels,
predictions and weights remain local; only hashes, code and aggregates are pushed.

The next milestone remains the complete scientific result, preserving nulls and
both conditions. Reference reproduction and conditional EEG contribution are
separate claims; neither establishes cortical origin, cue independence, clinical
utility or unseen-person generalization. The hourly quiet monitor may resume
once this one recovery process is running and must pause on terminal outcome.
