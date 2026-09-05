# Local imagined-word decoder: executed, usefulness not demonstrated

The system was built and run on real ArEEG recordings. Its frozen EEG model
failed the intended held-recording prediction task. It is an inspectable
experimental decoder, not a working thought-to-text communication system.

| Method | Balanced accuracy | Class-macro log loss ↓ |
|---|---:|---:|
| Actual EEG, 2–4 seconds | **16.73%** | **3.3611** |
| Training-only word prior | 20.00% | 1.6095 |
| Trial-position metadata | 17.45% | 1.7236 |
| Independently trained shuffled EEG | 21.09% | 2.8859 |
| Independently trained variance-matched Gaussian noise | 22.55% | 2.9611 |
| Early cue EEG, 0–2 seconds | 16.36% | 3.0518 |

These are equal-participant means from **274 trials across 11 people**. Each
person's model used five other recording sessions for calibration. Session
numbering does not establish chronological order or different recording days.

The primary EEG-versus-prior log-loss gain was **−1.7516 nats**, with a
descriptive paired participant-bootstrap 95% interval **[−3.8826, −0.5202]**.
Every participant had worse log loss than the prior. Shuffled/noise comparison
intervals cross zero: their larger accuracy numbers are not evidence that noise
is scientifically superior. There was no model tuning or test rescoring after
these outcomes. Independent arithmetic review reproduced the aggregate means,
paired gains and participant counts from the stored participant summaries.

The failed comparison constrains this representation and calibration protocol.
It neither proves that imagined speech cannot be decoded nor identifies the
biological source of any recorded information. The source uses prompted words
and has no dedicated eye or muscle channels. It cannot establish self-chosen
thoughts, unseen-person transfer, free sentences or live communication.

## What actually runs locally

- Eight EEG electrodes → fixed two-second interval → 36 log-covariance features
  → personally calibrated five-word probabilities → literal text output.
- Separate source broker and OS-restricted predictor. Test targets and a raw
  test marker were both demonstrably denied to the predictor.
- Eleven saved numerical models, a reusable target-free inference command,
  frozen prediction replay, and a self-contained HTML report showing every
  success and error, participant comparisons and the word confusion matrix.
- The finite-vocabulary language-only baseline is the training-only word prior.
  No external LLM, teacher-forced reference tokens or language rewriting is used.

From the repository directory, inspect a frozen prediction without scoring:

```sh
.venv/bin/python src/neurodecodekit/experiments/areeg_local_words.py replay \
  --root .codex_work/areeg-local-words-r0 --participant 0 --trial 0
```

For target-free saved-model inference, `infer` accepts `--model MODEL.npz`,
`--window WINDOWS.npy`, and `--index N`. Inputs must already be filtered
two-second, eight-channel EEG windows in volts, in the registered channel order.
The interface was exercised on one calibration window without scoring; reported
model probabilities are not established as calibrated confidence.

Local report: `.codex_work/areeg-local-words-r0/scored/report.html`.
Local weights: `.codex_work/areeg-local-words-r0/predicted/participant-*.npz`.
Raw recordings, targets, prediction rows and weights remain ignored locally.
The public machine summary is `registries/areeg_local_words_result.v0.json`.

## Execution and source quality

The selected public release files matched **216 SHA256 identities** and
**284,801,664 bytes**. Acquisition took **103.84 seconds**. Successful extraction
took **3.58 seconds**; the predictor process including imports took **19.09
seconds**, of which **1.44 seconds** was numerical fitting and prediction for
55 models (four signal/control models plus metadata per participant). Scoring
took **1.36 seconds**. These timings exclude source research and preparation
corrections. Predictor peak RSS was **344.25 MiB**; invocation storage immediately
after scoring was **327.11 MiB**, within its 512 MiB allowance and existing reserve.

Source-only corrections were made before fitting: numeric header formatting,
actual event counts, and duration-only exclusion of two short calibration events.
The selected sub-2/ses-5 recording has no word annotations; it was excluded
without substituting another session. Sub-4/ses-5 has 24 word events. There were
1,498 complete calibration events in the selected slice, of which 1,373 belonged
to evaluated participants. These pre-fit availability revisions make this an
exploratory result, not confirmation.

Predictions were committed and pushed at
`7cefaeb9fabeded6f21965ec0e2cd73f51c86902` before the single score. Their SHA256 is
`3fa938356513638ecfe7a91a5ea038eaa20454db06c0ac7a22caa0485f03eb3b`.
The completed evaluation is closed. HTML rendering and replay do not retrain or
rescore it. The next informative experiment would use fresh data to distinguish
within-recording word separability from failure to transfer between recordings,
with matched training size and null controls; it has not been launched here.

## Research used

[ArEEG, Scientific Data 2025](https://www.nature.com/articles/s41597-025-05387-w)
provides the actual prompted inner-speech data.
[Jo et al., Scientific Reports 2025](https://www.nature.com/articles/s41598-025-29587-x)
motivates noise controls and reference-free inference.
[Brain2Qwerty v2, 2026](https://arxiv.org/html/2608.18114v1) and
[COFETT, ACL 2026](https://aclanthology.org/2026.acl-long.61/)
informed the distinction between neural evidence, prompted content and language
readout. Their reported performance is not a result of this system.
