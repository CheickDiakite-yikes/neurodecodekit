# Does word information disappear between recordings?

`WORD-RECORDING-D1`, declared September 6, 2026 UTC before fitting this
diagnostic. The user explicitly requested this comparison. This is discovery:
it reuses ArEEG development sessions 0, 1, 3, 4 for twelve people (1,198 complete
trials). Sessions 2, 5 and 6 remain closed. No acquisition or weight download.

Question: with the same number of labeled examples, can a model distinguish
five prompted word conditions within a recording but fail across recordings?
The joint TimesFM representation is selected from the previous exploratory
comparison; this is not an untouched confirmation or an independent cohort.

- Evaluate five contiguous blocks, `trial_id // 5`, in each recording. Every
  complete trial is evaluated once per arm. Exclude the held block and its
  immediately adjacent trial on either side from within-recording training.
- Cross-recording training uses one fixed cyclic donor from the same person:
  target 0 uses 1, 1 uses 3, 3 uses 4, 4 uses 0. This is recording transfer,
  not a claim about recording days or forward-in-time deployment.
- For every fold and class, sample `min(within count, donor count, 4)` examples
  from each source with fixed seed 20260906. Both conditions predict the exact
  same held trials with identical training size and class counts. No source
  selection, tuning or replacement after outcomes.
  Donor sampling uses class counts from the target recording's non-test blocks;
  this matched diagnostic is not a zero-calibration transfer evaluation.
- Rebuild joint TimesFM features from the development-only `train.npy`, using
  the existing frozen checkpoint and per-window preprocessing. Do not read the
  mixed development/test feature files. Compare log covariance and flattened
  temporal samples from the same eight-channel, offline 2–4 s windows.
- Each fold refits standardization, eight-dimensional whitened PCA and
  multinomial logistic regression C=0.1 on its training rows only. Eight
  dimensions accommodate the smaller matched training sets; this does not
  repeat the earlier 32-dimensional evaluation.
- Every representation has independently fitted shuffled-training-label and
  independent standard-Gaussian-feature controls of the same input dimension.
  Gaussian features use no EEG-derived scale and do not pass through TimesFM;
  they test the readout on unrelated features, not synthetic EEG extraction.
  Use identical label permutations across representations in each split.
  Also report uniform probabilities, a smoothed training-only word prior
  (language-only baseline), and trial-position metadata with the same readout.
- Save all probabilities and their digest before a separate score operation.
  Primary summaries: class-macro log loss and balanced accuracy, first within
  recording, then equally across four recordings and twelve people. Report
  every arm, within-minus-cross gains, and each within arm versus uniform,
  prior, metadata, its shuffle and Gaussian controls. Paired 95% bootstrap
  intervals resample people (4,000 draws); these are descriptive, unadjusted
  exploratory intervals, not significance declarations. No trial-wise p-values.

A within-recording advantage supports a transfer-bottleneck hypothesis only
if it also beats the no-signal controls. Failure in both conditions does not
prove absence of word information: small training sets, representations,
preprocessing, task compliance and artifacts remain unresolved. Visible cues
and missing EOG/EMG prevent attribution to isolated inner speech.

One offline worker/thread, 15-minute stage limit, 4 GiB RSS and 256 MiB new
storage, preserving the global 20 GiB ceiling, 3 GiB reserve and 20 GiB free
floor. Only public code, this protocol and aggregate results may be committed;
raw signals, labels, features, row predictions and weights remain local.
