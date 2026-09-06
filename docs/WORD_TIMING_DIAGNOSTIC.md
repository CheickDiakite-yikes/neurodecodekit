# D3: early versus later activity in prompted-word trials

`WORD-TIMING-D3`, declared September 6, 2026 before early extraction or fitting.
The user explicitly selected this experiment. This is exploratory development
analysis using the same 1,198 complete trials from twelve people and sessions
0, 1, 3, 4. Sessions 2, 5 and 6 stay closed. No downloads or new model weights.

Hypothesis: **cue-proximal [0,2) seconds provides more predictable word-condition
information than later prompted-task [2,4) seconds**, using the same fixed
readout. Primary contrast is joint TimesFM within recordings, measured by
equal-person class-macro log loss. Covariance and temporal features, and donor
recording fits, remain fully reported secondary diagnostics.

The [ArEEG paper](https://www.nature.com/articles/s41597-025-05387-w) describes
reading a displayed word, closing the eyes, and repeating it internally while
the word stays visible for five seconds. It does not provide separate measured
eye-closure or imagery-onset times. The named collection script was unavailable
on the inspected [official repository](https://github.com/Eslam21/ArEEG-an-Open-Access-Arabic-Inner-Speech-EEG-Dataset).
Thus this is an early/late comparison relative to annotations, not verified
cue-only versus imagery-only activity. Sensory, ocular, muscle and task signals
can affect both windows. Actual display/EEG synchronization remains unverified.

## Fixed matched analysis

- Verify the pinned original manifest and only the 144 files for the 48 selected
  development recordings. No directory-wide raw permission. BrainVision marker
  positions are one-based; subtract one once. Use actual word markers, not a
  nominal 15-second schedule containing variable Wait periods.
- Keep exactly D2's ordered identities and labels. Require the same full four
  seconds to exist even though early extraction needs two; retain the same two
  exclusions. Any additional missing/nonfinite early event stops this comparison.
- Extract samples [start,start+500), independently filter that window with the
  same fourth-order Butterworth 1–30 Hz zero-phase filter, then resample from
  250 to 64 Hz. Never filter the combined early/late interval before slicing.
- Use frozen joint TimesFM, log covariance and flattened temporal features with
  D2's exact class-balanced logistic heads: training-only scaler, whitened PCA8,
  C=0.1. Preserve all 240 block/guard splits, selected training rows, seeds,
  shuffled training labels and same-dimension Gaussian feature controls. Each
  head receives 16–19 examples, as in D2. Retain uniform, empirical prior
  (independent language-only baseline) and metadata arms unchanged.
- Reuse **D2 public participant aggregates** as the late comparator. Do not
  access late probabilities, refit late models or rescore the late data.
  Only early predictions are new. This avoids unnecessary computation while
  preserving paired participant-level comparisons on identical trials.
- Freeze all early probabilities and commit their hashes before one score.
  Check the exact D2 split digest. The canonical calibration digest binds
  identities/labels; the new early-array digest replaces the late signal digest.
- Report all 24 early condition/arm summaries and D2 late summaries. Compute
  early-versus-late gains for all three representations in within/donor settings,
  plus each early within arm versus uniform, prior, metadata, shuffled labels
  and Gaussian features. Use the same class-then-recording-then-person averaging
  and 4,000 paired person-bootstrap draws. Add an early-versus-late shuffled-label
  difference-of-differences to distinguish an actual-label timing gain from a
  gain also present under shuffled labels. All intervals are descriptive and
  unadjusted; this is not a new confirmatory test or an equivalence test.

An early advantage alone is insufficient: the early actual-label arm must also
improve over its no-signal controls to support word-condition predictability.
Failure at both windows limits these fixed representations and tiny calibration
sets; it does not establish absence of word information or validate alignment.
No window search, model replacement or retuning after these outcomes.

One offline worker/thread, 4 GiB RSS, 256 MiB new storage, 15 minutes per stage;
preserve the existing 20 GiB ceiling, 3 GiB reserve and 20 GiB free-space floor.
Measure timing, bytes and RSS. Commit code and public aggregates only. Raw
signals, features, labels, probabilities and weights remain ignored/local.
