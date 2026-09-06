# TimesFM-3: three fixed uses for EEG word prediction

The maintainer requested actual local TimesFM-3 comparisons on September 5,
2026. This new exploratory experiment uses previously acquired ArEEG calibration
sessions 0, 1, 3, 4 and a fresh session 6, from the same pinned ds005262 release
`4ba1bb516d6cc98917143b0dfca23947935c7b15` (CC0). It never opens session 2 or the
consumed session 5. Session 6 is 36 files / 45,969,075 bytes for all twelve
participants, each checked against its release SHA256. No substitute session
is allowed. Missing/incomplete events are reported by the source broker.

Hypothesis: frozen TimesFM representations or forecast residuals improve
personally calibrated five-word prediction in a new recording beyond matched
simple representations and no-signal controls. This does not test free thought,
unseen people, or brain-specific attribution; the recordings lack EOG/EMG and
use visible prompts. No new recording-day assumption is made.

## Fixed comparison before new signal access or fitting

- Same eight electrodes and offline 2–4 s window as the earlier baseline;
  each window independently bandpassed 1–30 Hz, then resampled from 250 to
  64 Hz (128 samples). All numerical features receive only these samples.
- Official TimesFM code revision `0df95ae62085a6ac0d0afd1ad40dee2e6c1356ab`,
  checkpoint `43046b85ec22d584a13f8098c2ed39c889e129c2`, weights SHA256
  `a7592b0a8432baee54483254e5647856911ce69e09d09a9bb65904b2d98f17da`.
  Weights stay frozen, on one CPU thread, float32. No language model rewrites
  predictions. Convert volts to microvolts before TimesFM normalization.
- **Joint hidden features:** final context patch's hidden vector from each
  electrode, concatenated in the fixed sensor order; all electrodes in one
  multivariate forward pass. No prompt, word identity, or future covariate.
- **Independent hidden features:** identical operation with each electrode as
  a separate batch item, preventing cross-electrode attention. Same weights.
- **Forecast residuals:** jointly forecast samples 64–127 using only samples
  0–63, then flatten observed minus median forecast. Disable linear detrending,
  stitching and iterative RevIN refinement for this fixed application.
  This remains an offline within-window residual, not a causal neural claim:
  filtering and resampling can mix time points inside the completed window.
- **Simple comparisons:** the 36 log-covariance features and flattened temporal
  samples, each computed from the same resampled window.
- For every representation, use training-only standardization, 32-component
  PCA with whitening, and identical L2 multinomial logistic regression C=0.1.
  Fit one classifier per participant. No readout or representation selection.
- Independently fit a shuffled-label version of every representation, with one
  deterministic permutation within each training recording. Also compute
  variance-matched Gaussian windows for every representation, using scale from
  training samples only, and independently fit the identical classifier.
- Include a training-only word prior (the independent language-only baseline)
  and trial-position metadata baseline. Report every arm, including failures.
- Broker separates fresh targets. Numerical worker can read only its whitelisted
  signal/identity/training-label inputs, official code/weights and dependencies;
  it cannot read raw files, new evaluation labels, or old experiment outputs.
  Save all probabilities and freeze SHA256 before one separate scoring event.
- Primary outcome: equal-person class-macro log loss, with balanced accuracy,
  participant-paired gains and descriptive 95% bootstrap intervals. Compare each
  TimesFM mode with covariance, raw temporal, prior, metadata, its shuffled and noise arm.
  Report paired one-sided sign-flip tests with Holm correction across all these
  18 comparisons; do not select a winner and hide unsuccessful comparisons.
  Sign-flip p-values are conditional on symmetric/exchangeable participant
  differences, not assumption-free evidence. Metadata was included in this
  comparison family during review before feature extraction, fitting or scoring.

This is new recording-level exploratory evidence within one already known
cohort. A positive result needs independent replication and artifact controls.
It cannot repair or replace the earlier failed frozen evaluation.

## Bounded execution

One worker and one numerical CPU thread. New invocation cap 2 GiB on disk,
including the 1,322,898,824-byte checkpoint, 64 MiB fresh raw allowance, temporary
files and derivatives. Preserve the existing global 20 GiB ceiling, 3 GiB
untouched reserve, and 20 GiB free-disk floor. The former experiment's 1 GiB
RSS limit cannot load this requested foundation model: this invocation uses a
4 GiB RSS ceiling, with a two-window label-free timing probe and at most
60 minutes numerical execution. Record actual runtime, peak RSS and bytes.
Transport or implementation fixes are permitted before prediction/scoring;
no tuning or rerunning the new evaluation after scoring. No other cohort or
checkpoint substitution. No weights, raw data, labels or row predictions are
published. Official model weights are noncommercial/nonproduction and cannot
be redistributed; local research only.

Sources: [TimesFM-3](https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/),
[official code](https://github.com/google-research/timesfm),
[checkpoint and license](https://huggingface.co/google/timesfm-3.0-pytorch),
[ArEEG](https://www.nature.com/articles/s41597-025-05387-w).
