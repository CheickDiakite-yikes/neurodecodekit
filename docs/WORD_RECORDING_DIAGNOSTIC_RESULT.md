# Words were not reliably decoded within recordings either

We tested the proposed recording-transfer explanation on **1,198 real ArEEG
trials from 48 recordings and twelve people**. TimesFM did not demonstrate
useful word prediction within recordings, and its within-versus-donor gap was
unresolved. This does not establish absence of word information: the test uses
only 16–19 training trials per fit and fixed, potentially unsuitable features.

The first diagnostic exposed a sampling limitation. A separate class-balanced
follow-up improved probability predictions but did not produce a word-decoding
advantage over the strongest no-signal baseline.

| Representation | D1 within accuracy | D1 donor accuracy | D2 within accuracy | D2 donor accuracy |
|---|---:|---:|---:|---:|
| Joint TimesFM-3 | 12.83% | 12.00% | 18.71% | 19.60% |
| Log covariance | 14.58% | 16.58% | 21.79% | 21.27% |
| Raw temporal samples | 10.67% | 12.58% | 15.75% | 19.60% |
| Uniform probabilities | 20.00% | 20.00% | 20.00% | 20.00% |

These are balanced accuracies, averaged equally over classes, recordings and
participants. Do not compare them with the earlier session-5 or session-6
evaluations as model gains: the training size, readout and evaluation changed.

## What the controls changed

D1 used five contiguous held blocks per recording with one-trial guards.
Both within and donor models predicted identical trials and received identical
per-class training counts. In nearly balanced recordings, holding words out
depletes those words from training. D1's **EEG-free word-frequency prior scored
8.92%**, while unrelated feature controls also fell below 20%. Below-chance
accuracy therefore cannot be interpreted as evidence of anti-neural information.
This mechanism does not explain every model failure.

After D1, we declared D2 as a separate adaptive development intervention:
balance each class's contribution to logistic training loss. All three actual
feature arms, their shuffled-label and Gaussian-feature controls, and metadata
received the same intervention. The empirical and uniform priors stayed fixed.
The exact selected rows, guards, feature arrays, seeds, PCA8, regularization
and endpoints were preserved. Class weighting does not guarantee removal of
every sampling bias.

The change improved TimesFM's within-recording log loss by approximately
**0.141 nats**, while its unrelated Gaussian-feature control improved by
**0.140 nats**. This nearly identical improvement is evidence that the gain
was largely nonspecific; it cannot be credited to newly recovered word content.

D2's primary probability metric remained unfavorable:

| D2 arm | Within log loss | Donor log loss |
|---|---:|---:|
| Joint TimesFM | 1.66158 | 1.65903 |
| TimesFM features, shuffled labels | 1.67181 | 1.67152 |
| Independent Gaussian features, TimesFM input dimension | 1.64279 | 1.64273 |
| Log covariance | 1.93515 | 3.01478 |
| Raw temporal samples | 1.73282 | 1.80107 |
| Uniform probabilities | **1.60944** | **1.60944** |

Lower log loss is better. Joint TimesFM's within-versus-donor log-loss gain was
**−0.00255**, descriptive paired-bootstrap 95% interval **[−0.01879, 0.01317]**.
Its accuracy gain was **−0.90 percentage points [−4.46, 2.33]**. Against uniform,
its within log-loss gain was **−0.05214 [−0.06568, −0.03839]**; none of the twelve
participants improved. Its log-loss advantage over shuffled labels was
**0.01023 [−0.00447, 0.02417]**, and it lost to independent Gaussian features.

The covariance pipeline was less overconfident within recordings: log-loss
gain **1.07964 [0.45355, 1.84110]**, positive for eleven people. However, both
conditions had worse log loss than uniform guessing, and its within-versus-donor
accuracy gain was only **0.52 points [−1.92, 2.71]**. This supports recording
sensitivity of that particular pipeline's probability predictions, not reliable
within-recording word decoding or a known physiological cause.

All intervals are unadjusted, descriptive participant bootstraps. Neither
experiment is confirmation; D2 was explicitly chosen after observing D1. No
significance or equivalence claim is made from these intervals. All 24
condition/arm summaries and eighteen comparisons per diagnostic are retained
in the public aggregates, including every failed control and method.

## Execution and reproducibility

Development sessions were **0, 1, 3, 4** from the same pinned CC0 ArEEG release.
Sessions **2, 5 and 6 stayed closed**. We rebuilt only the 1,198 development
feature rows from the previous development array; no mixed test cache was read.
All learned preprocessing refitted on each fold's training rows. Donor sampling
uses class counts from the target recording's non-test blocks, so this is not
a zero-calibration transfer experiment. Session numbers do not establish dates.

D1 feature extraction took **72.52 seconds**, peaking at **2.17 GiB RSS**.
Its **4,800 small classifier fits** took **31.98 seconds** at **448.70 MiB**.
D2 reused those development feature files and took approximately **34 seconds**
for another 4,800 fits. Each separate score took under one second of internal
computation. One CPU thread and one worker were used; no network, new payload,
checkpoint download or LLM generation occurred. New experiment data occupied
about **55 MiB**, with the three shared feature files counted once.

D1 probabilities were hashed locally before scoring reused development labels.
D2's exact prediction hash and code were additionally committed and pushed at
`4e7ddd1` before its separate score. These procedures do not make previously
known development labels an untouched test set. Five focused generated tests
passed, covering split isolation, count matching, closed-session rejection,
class-macro scoring, training-only transformations and the balanced adapter.
Independent critics reviewed the implementation and aggregate arithmetic.

Local reproduction uses the two additive experiment modules, with `features`,
`predict`, and `score` as separate stages; existing output stages refuse overwrite.
The D2 adapter shares the unchanged D1 engine and injects only its weighted head.
The figure/report renderer reads public aggregates only and can be rerun safely:

```sh
.venv/bin/python scripts/render_word_recording_diagnostic.py
```

- [D1 protocol](WORD_RECORDING_DIAGNOSTIC.md) and [D1 aggregate](../registries/word_recording_diagnostic_result.v0.json)
- [D2 protocol](WORD_RECORDING_BALANCED_DIAGNOSTIC.md) and [D2 aggregate](../registries/word_recording_balanced_result.v0.json)
- [D1 freeze](../registries/word_recording_diagnostic_freeze.v0.json) and [D2 freeze](../registries/word_recording_balanced_freeze.v0.json)

The results constrain these methods at this tiny calibration budget. They do
not establish isolated inner speech, arbitrary thoughts, sentence generation,
new-person generalization or clinical utility. Visible prompts and absent
eye/muscle channels remain unresolved attribution limits. A useful next test
must establish a trustworthy within-recording signal with verified event timing
and sufficient class-balanced calibration before claiming a transfer solution.
