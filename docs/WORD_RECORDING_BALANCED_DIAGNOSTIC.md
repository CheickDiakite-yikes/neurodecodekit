# D2: does balancing the readout remove the apparent failure?

Declared after observing D1, before D2 fitting: September 6, 2026 UTC.
This is a separately named adaptive development analysis, `WORD-RECORDING-D2`.
It neither replaces nor repairs D1, and it is not confirmatory evidence.

D1's uniform baseline scored 20%, but its EEG-free empirical prior scored
8.92%. Holding a block out of a nearly class-balanced recording depletes the
held words from training; identical matched class quotas carry that problem
into the donor arm. This motivates one explicit intervention.

Change **only `class_weight='balanced'` in every learned logistic readout**:
joint TimesFM, covariance, temporal samples, their shuffle/feature-noise heads,
and metadata. Class weights are n/(5*n_class), computed on training labels,
and sum to n. Keep both uniform and empirical priors unchanged. All D1 input
hashes, windows, features, 240 splits, selected training rows, one-trial guards,
PCA8/scaling, C=0.1, seeds, shuffled labels, Gaussian features, twelve people,
1,198 out-of-fold trials, summaries and eighteen comparisons remain fixed.

The additive adapter injects a balanced head into the unchanged D1 engine;
child processes launch the adapter as well. Its new root shares only D1's
three development feature files. No D1 probabilities or targets are opened;
the development calibration sidecar is intentionally reused. Sessions 2, 5
and 6 remain closed. No feature extraction, downloads or additional models.

Save and hash every new probability before one separate score. Report all
arms and both D1 and D2 outcomes. The decisive question is whether real EEG
beats uniform probabilities **and** its balanced shuffled/noise controls.
Improvement shared with noise indicates removal of a prior artifact, not
newly demonstrated word information. A within-donor gap alone cannot identify
the source of recording dependence. All intervals remain descriptive and
unadjusted across the exploratory comparisons.

Use the same one-worker/thread, 4 GiB RSS, 256 MiB incremental-disk,
15-minute-per-stage caps and existing storage reserves. This follow-up costs
only new tiny classifier fits and local probability storage. Source cues,
missing EOG/EMG, small training sets and reused development data still limit
interpretation. No clinical, free-thought or isolated-inner-speech claim.
