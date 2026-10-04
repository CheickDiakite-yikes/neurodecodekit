# Calibration compatibility correction and one complete successor

September 21, 2026. This is an implementation correction before any held-out
scoring, not a scientific result or a change to the registered experiment.

The maintainer explicitly approved the calibration-only audit, then answered
the scoped question about one corrected complete two-hour invocation:
**"Yes—fix, validate, then run and score once".** This authorizes one new root,
not resumption of either failed invocation or an automatic retry after failure.

## What the audit establishes

The six pinned calibration event sidecars contain 100 trials each, valid
five-word mappings, and the following class counts in the fixed order green,
magenta, orange, violet, yellow:

| Participant / condition | Counts | Ten folds, every training fold has all five classes |
|---|---|---|
| 1 / minimally overt | 22, 22, 20, 20, 16 | Yes |
| 1 / covert | 24, 23, 24, 17, 12 | Yes |
| 2 / minimally overt | 30, 26, 18, 15, 11 | Yes |
| 2 / covert | 29, 26, 18, 14, 13 | Yes |
| 3 / minimally overt | 31, 25, 18, 13, 13 | Yes |
| 3 / covert | 37, 28, 13, 8, 14 | Yes |

Our blanket requirement of at least ten examples per class was not in the
author procedure. The pinned [trainer's `fit_decoder_CV`](https://github.com/arayabrain/uhd-gmail-public/blob/0dca00584c528b288392684dcec0d496b6aa4951/uhd_eeg/trainers/trainer.py#L30-L56)
calls `StratifiedKFold(n_splits=args.n_splits)`; the
[configuration](https://github.com/arayabrain/uhd-gmail-public/blob/0dca00584c528b288392684dcec0d496b6aa4951/configs/trainer/config_color_multirun.yaml#L4-L39)
sets ten folds. Random values supplied as the splitter's placeholder `X` do not
shuffle its returned dataset indices. The splitter defaults to `shuffle=False`.
Installed scikit-learn warns, but permits ten folds when only some classes have
fewer than ten trials. The author dependency file does not pin its version.

Remove only our unsupported minimum-count rejection. Preserve the exact ten
nonshuffled folds; do not rebalance, oversample, drop trials or reduce folds.
Our additional conservative check rejects a training fold missing a class;
all 60 training folds pass. Two validation folds for participant 3 covert lack
violet. Their ordinary sample-weighted loss and accuracy remain the registered
selection criteria; do not change weighting or replace them with class-macro
validation accuracy. This sparse validation support is a limitation, not an
evaluation result. Evaluation five-class completeness rules are unchanged.

The [aggregate audit](../registries/speech_reproduction_calibration_audit.v0.json)
retains per-fold class counts and proves exact validation-index agreement for
the five previously trained pairs. Source byte sizes and Git blob identities
were checked before parsing. No online event rows, private targets, EEG,
predictions, or weights were read by this audit; no training or scoring occurred.
The same production splitter is used by audit, training and checkpoint reuse.

Local validation passed 76 focused tests plus 43 subtests, including a
generated six-pair prediction-to-freeze-to-one-score transaction, sparse-class
fold checks and fail-closed lineage/consumption checks. Repository Ruff passed
(two pre-existing inaccessible pytest temporary directories were skipped).
These checks validate implementation, not decoding performance. Remote CI
must pass on the exact implementation commit before invocation.

## One new invocation, unchanged scientific settings

Use `data/speech_repro_1_corrected_20260921` exclusively. The original
`data/speech_repro_1_20260921` and failed
`data/speech_repro_1_recovery_20260921` remain immutable evidence. Bind both
failure identities and hash their saved artifacts without opening target values.
Count storage across all three roots. Reuse exactly the original 50 EEGNet
checkpoints; reconstruct fixed compact models and unscored predictions; train
the final ten folds for 100 epochs each. Preserve all 600 calibration and 341
evaluation trials, both conditions, all participants and all nine arms.

Before any modeling, reverify all sources, all 13 timing/padding checks and all
six calibration fold receipts. Compare the calibration audit to its committed
aggregate. A fresh 7,200-second wall cap includes prediction, hash-freeze commit
and push, and final scoring. The 900-second stage, single numerical thread,
4-GiB RSS, combined 1.5-GiB payload and 20-GiB free-space limits remain.

Commit and push the implementation and audit before execution. On complete
prediction, commit and push **only**
`registries/speech_reproduction_prediction_freeze.v0.json`, verify its remote
commit, then invoke exactly once:

```text
.venv\Scripts\python.exe -u scripts/recover_speech_reproduction.py score --freeze-commit PUSHED_SHA
```

The corrected driver refuses either a failure marker or consumed scoring.
It also rejects altered lineage, incomplete pairs, changed provenance and
code changes between prediction and scoring. Failure stops this invocation;
no partial scoring and no automatic rerun. Scientific code stays fixed during
execution. Only aggregates and documentation may be pushed after scoring.

## Scientific decision remains unchanged

The imminent result must separately answer whether the reference predicts
five words on later recordings of known people and whether filtered EEG adds
information beyond measured nuisances and registered controls. Report both
conditions and every null, using the
[fixed interpretation map](SPEECH_REPRODUCTION_RESEARCH_DECISION.md).
Neither a positive reference nor a conditional increment establishes cortical
origin, cue-independent thought, unseen-person transfer, arbitrary text,
clinical utility or prospective live operation. No post-test tuning here.

The two implementation failures have not answered that question. The next
priority is the complete frozen result, not a new architecture or dataset.
