# SPEECH-REPRO-1 stopped before evaluation

September 21, 2026. **No scientific score was produced.** The run stopped after
6,115 seconds (101.9 minutes), below its approved six-hour maximum.

## What happened

All 13 pinned source recordings were acquired and hash-verified. Five of six
person/condition pairs completed: 50 reference fits, each with 100 epochs,
using 500 calibration trials. The associated 291 online-trial predictions
were generated but were not evaluated.

Extraction then refused participant 3's covert calibration recording:
`sub-3/ses-20230524/eeg/sub-3_ses-20230524_task-covert_acq-calibration_run-01_eeg.edf`.
The exact error was `ValueError: Source event/trigger timing cannot be reconciled`.
The check requires event samples to equal the selected rising trigger edges.
It did not permit silently shifting, dropping, or relabeling trials.

This establishes a mismatch under our extraction rule, **not** that the source
is corrupt. Its cause has not been diagnosed. No source event rows or private
target values were opened during the failure review.

## What remains—and what does not

The existing source files, five pair reports, saved model checkpoints, sealed
target files and failure record remain local. Nothing was deleted or uploaded.
The executor retained probability arrays in memory until all six pairs were
complete; those arrays were lost on process exit. There is no complete
`predictions.npz`, committed prediction freeze, scoring invocation, or result.
Saved checkpoints may support a later recovery, but recovery was not attempted.

Held-out accuracy and the incremental EEG endpoint remain unknown. This is
neither a successful reproduction nor a biological null. Completing training
does not change the scientific conclusion.

## Next priority

Seek authorization for a narrowly scoped, label-blind timing audit of the
failed recording against the pinned converter. It should establish whether
the released timing can be justified without changing trial identity or
consulting word outcomes. Do not retrain, reconstruct predictions, score a
partial subset, or bypass the failure marker under this stopped invocation.

Any proposed successor should validate timing across the entire selection
before fitting, and assess whether the saved checkpoints can avoid repeating
the 50 completed fits. No such successor is activated here. Automatic check-ins
are to be paused after this failure is reported.

Evidence: implementation commit `479c1c3964823e43bafc995b11a48242980a532b`;
local `data/speech_repro_1_20260921/execution_failed.json`, SHA-256
`cc260c268518fe2764132a57f83bf4b519ba07003c04192f036be45648fc33b6`;
five local pair reports; and the completed process traceback. The implementation
passed both remote CI jobs. See the [fixed experiment](SPEECH_REPRODUCTION_RESEARCH_DECISION.md)
and [execution clarifications](SPEECH_REPRODUCTION_EXECUTION.md).
