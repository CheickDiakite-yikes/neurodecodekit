# D4: does more calibration improve prompted-word decoding?

`WORD-CALIBRATION-D4`, exploratory reused-development experiment, September 6,
2026. The user explicitly selected increasing calibration examples. Declare
this protocol and bind implementation/input hashes before fitting; freeze all
probabilities before the sole scoring pass. No tuning follows these outcomes.

Hypothesis: increasing same-person calibration from 15 to 60 labeled examples
improves word prediction on another recording **beyond the improvement seen in
no-signal controls**. Primary representation is the pre-existing late (2–4 s)
joint TimesFM feature array. Early (0–2 s), covariance and temporal features
remain secondary; report them all without choosing a winning window or model.

## Matched learning curve

- Reuse the exact 1,198 development trials from twelve people in sessions
  0, 1, 3, 4. Sessions 2, 5 and 6 remain closed. No raw signals, mixed feature
  caches, old predictions, downloads or model weights are needed.
- Leave each complete recording out in turn: 48 folds. Use the other three
  recordings from the same person as donors at **every** calibration size.
  Their class pools each contain at least four examples, verified before fits.
- A single fixed seeded permutation per person/held-recording/donor/class
  defines nested prefixes of **1, 2 and 4 examples per class per donor**.
  Training sizes are exactly **15, 30 and 60**, with balanced classes and donor
  composition. Test trials and training selections match across representations
  and early/late windows. Every development trial is tested once per size/arm.
- No held-recording example enters its training pool. This is offline
  leave-recording-out evaluation within known people, not unseen-person or
  prospective chronological evaluation. These new splits differ from D2/D3;
  do not interpret a difference from their scores as a sample-size effect.
- Fit standardization, whitened PCA8 and multinomial logistic regression on
  training rows only. Preserve the fixed feature extractor and PCA dimension.
  Use `C_N = 1.5/N`: C=0.1, 0.05 and 0.025. The installed scikit-learn lbfgs
  objective uses `1/(C * sum_weights)` as the penalty coefficient on mean loss;
  equal class counts make all balanced class weights one. This adjustment keeps
  that coefficient constant, so increasing N does not also weaken regularization.
  PCA is refitted on each training subset, as part of calibration.
- Each representation has a shuffled-training-label control and independent
  standard-Gaussian feature control of identical input dimension. Shuffle labels
  separately within each donor recording, preserving balanced donor/class counts.
  Use the same fold/size permutations across modes/windows. Generate each mode's
  Gaussian array once and reuse across sizes/windows. Uniform probabilities,
  training-only prior and trial-position metadata remain independent baselines.
  The prior must equal uniform because training classes are balanced.
- Fit input-independent controls once per split/size and reuse their predictions
  across windows. They must match exactly. Gaussian features do not pass through
  TimesFM; they test the readout, not synthetic-EEG feature extraction.

## Scoring and interpretation

Keep all 72 window/size/arm summaries. Average class-macro log loss and balanced
accuracy over each held recording, then four recordings per person, then twelve
people. Primary evidence is late joint TimesFM's 15-to-60 log-loss gain and its
60-example performance versus uniform, prior, metadata, shuffled labels and
Gaussian features. Also subtract each control's own 15-to-60 gain from the
real-label gain. Report these contrasts for all six window/representation pairs.

Use one shared `numpy.random.default_rng(20260906)` array of 4,000 resamples of
twelve people, numeric person ordering, with NumPy default linear 2.5/97.5%
quantiles. Intervals are descriptive and unadjusted. This is a single frozen
subset ordering, not uncertainty over many random training subsets.

A falling loss is insufficient: more data can reduce overconfidence on noise.
Evidence favoring usable prompted-word information requires advantage over
the controls at 60 as well as a gain not reproduced by those controls. A
negative or uncertain result limits this pipeline and calibration range, not
the existence of information in EEG. Neither window isolates imagined speech;
missing peripheral measurements and reused data preclude neural attribution or
an independent confirmation. No open-text or clinical claim follows.

One offline worker/thread, 4 GiB RSS, 256 MiB new disk, 15 minutes per stage;
retain the existing 20 GiB ceiling, 3 GiB untouched reserve and 20 GiB free
floor. Reuse only the six hash-bound development feature arrays; publish code
and aggregate results, keeping all labels, features and probabilities local.
