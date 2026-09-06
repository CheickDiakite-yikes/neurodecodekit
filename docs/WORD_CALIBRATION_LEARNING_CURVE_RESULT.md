# More calibration did not establish useful word decoding

`WORD-CALIBRATION-D4` completed September 6, 2026. Increasing calibration from
15 to 60 examples improved probability loss, but the primary TimesFM-based
decoder still failed to demonstrate an advantage over uniform guessing or
noise. Shuffled training labels produced a similar learning-curve improvement.

## Scientific evidence

Primary late-window TimesFM joint features, predicting another recording from
the same person:

| Calibration examples | Balanced word accuracy | Log loss (lower is better) |
| ---: | ---: | ---: |
| 15 | 21.10% | 1.62515 |
| 30 | 18.92% | 1.62063 |
| 60 | 19.58% | 1.61068 |
| Uniform probabilities | 20.00% | 1.60944 |

The 15-to-60 log-loss improvement was **0.01448 nats**, descriptive paired-person
95% interval **[0.00536, 0.02328]**, positive in 10/12 people. Accuracy changed
by -1.52 percentage points, interval [-4.67, 1.56].

At 60 examples, the TimesFM log-loss advantage over uniform was **-0.00124**,
interval **[-0.00815, 0.00533]**. The advantage over Gaussian feature controls
was -0.00091, interval [-0.00793, 0.00568]; over shuffled labels it was 0.00341,
interval [-0.00655, 0.01211]. It beat the trial-position metadata model in log
loss, but that weaker comparison does not establish word decoding.

The shuffled-label model's own 15-to-60 gain was 0.01228 nats. Subtracting this
from the actual-label gain leaves **0.00220**, interval **[-0.00911, 0.01293]**.
The experiment therefore did not establish a label-specific learning-curve gain.
It also does not establish equivalence or absence of word information.

All six feature/window combinations at 60 examples:

| Window | Representation | Balanced accuracy | Log loss |
| --- | --- | ---: | ---: |
| Early 0–2 s | TimesFM joint | 20.44% | 1.61870 |
| Early 0–2 s | Log covariance | 19.44% | 1.64805 |
| Early 0–2 s | Raw temporal | 20.46% | 1.63040 |
| Late 2–4 s | TimesFM joint (primary) | 19.58% | 1.61068 |
| Late 2–4 s | Log covariance | 20.02% | 1.64259 |
| Late 2–4 s | Raw temporal | 20.10% | 1.63615 |

Every mean log loss remained worse than uniform. All 72 arm means, twelve
participant aggregates and 132 descriptive intervals are retained in the
[public result](../registries/word_calibration_result.v0.json). Prior probabilities
equaled uniform exactly; uniform, prior, metadata and noise predictions matched
across windows exactly. No models or outcomes were selected after scoring.

## What was tested, and what remains unresolved

The same 1,198 development trials from twelve people and 48 recordings were
evaluated at every training size. Each recording was held out in turn. The
other three same-person recordings supplied nested, equally balanced samples:
one, two or four examples per word per donor, totaling 15, 30 or 60. PCA8 and
normalization were fitted only on those training rows. The logistic penalty on
mean loss stayed constant via C=1.5/N. The complete method was
[declared before fitting](WORD_CALIBRATION_LEARNING_CURVE.md).

These splits differ from D2/D3: this result measures a size effect within D4,
not a direct performance change from their scores. It uses one fixed subset
ordering and reused development data. The intervals resample people, are
unadjusted, and are not an independent confirmation. Neither time window
isolates imagined speech, and peripheral/cue explanations remain uncontrolled.

The strongest supported conclusion is that **15-to-60-example scaling did not
demonstrate useful prompted-word decoding across recordings with these fixed
representations and readout**. Loss improvements alone are insufficient, because they
also occur when the training labels are shuffled. This result does not identify
whether remaining limitations arise from representation, compression into PCA8,
recording differences, data quality, or weak task-related information.

## Enabling engineering and verification

The experiment reused six hash-verified development feature arrays totaling
108,644,992 bytes. There were no downloads, no new feature extraction, and no
access to raw signals, old predictions, mixed caches or sessions 2, 5 and 6.
Four focused tests passed. Independent code/statistical reviews found no
protocol or numerical defects before fitting. All predictions were frozen and
pushed at **f87ab9c** before the sole score.

After scoring, an independent aggregate-only audit reproduced all 72 summaries,
132 contrast means/counts and 132 interval endpoints; maximum mean roundoff
was 4.4e-16 and interval endpoints matched exactly. No targets or probabilities
were reopened by the reviewer.

The 2,304 fits took **19.31 seconds**, peak RSS **565,936,128 bytes**. Scoring
and aggregate comparisons took **0.49 seconds**, peak RSS **53,444,608 bytes**.
Both stages used one offline CPU thread. Exact incremental bytes and hashes
are in the public result and prediction-freeze records. Labels, features and
trial probabilities remain local.

Render the complete local comparison without running models or scoring again:

```sh
MPLCONFIGDIR=/tmp/neurodecodekit-mpl .venv/bin/python scripts/render_word_calibration_learning_curve.py
```

The next discriminating change would test whether the fixed unsupervised PCA8
compression discards useful task features, with the same held-recording splits
and matched controls. That experiment was not run here.
