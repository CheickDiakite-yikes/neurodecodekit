# Early versus later word-trial activity: measured result

**The earlier window did not rescue TimesFM word decoding.** On the same 1,198
development trials from twelve people, its balanced accuracy was 18.25% early
and 18.71% late; uniform guessing is 20%. This completes the fixed
`WORD-TIMING-D3` exploratory experiment declared in
[the protocol](WORD_TIMING_DIAGNOSTIC.md). No further model selection followed
these scores.

## Scientific evidence

Within-recording results, averaged equally across people:

| Representation | Early accuracy | Late accuracy | Early log loss | Late log loss |
| --- | ---: | ---: | ---: | ---: |
| TimesFM-3 joint features (primary) | 18.25% | 18.71% | 1.65844 | 1.66158 |
| Log covariance | 20.12% | 21.79% | 1.95158 | 1.93515 |
| Raw temporal features | 21.00% | 15.75% | 1.67649 | 1.73282 |
| Uniform probabilities | 20.00% | 20.00% | 1.60944 | 1.60944 |

Accuracy is higher-is-better; log loss is lower-is-better and measures the
quality of the predicted probabilities. Log loss was the primary metric.

TimesFM's early-versus-late log-loss gain was **0.00314 nats**, with a
descriptive paired-person 95% bootstrap interval **[-0.01310, 0.01794]**.
Its accuracy change was -0.46 percentage points, interval [-3.17, 2.17].
Subtracting the corresponding shuffled-label timing gain left 0.00284 nats,
interval [-0.02044, 0.02377]. The donor-recording TimesFM arm also showed no
demonstrated early advantage: 18.67% early versus 19.60% late.

The secondary temporal representation improved by **5.25 percentage points**,
interval [2.50, 8.33], and 0.05633 nats, interval [0.01336, 0.12265]. However,
its shuffled-label arm also improved. After subtracting that improvement,
the timing gain was 0.05335 nats, interval [-0.00043, 0.11127], and 2.10
percentage points, interval [-1.15, 5.35]. Early temporal probabilities still
lost to both uniform probabilities and Gaussian feature controls. Its 21%
accuracy does not establish useful five-word decoding.

All 24 early arms, 24 late summaries, twelve participant aggregates, six timing
comparisons and six shuffled-adjusted comparisons are retained in the
[public aggregate](../registries/word_timing_result.v0.json). Uniform, prior,
metadata and all three Gaussian feature controls reproduced the corresponding
late participant metrics exactly: maximum absolute difference **0.0**.
Shuffled-label controls were refit on their corresponding early features.

## What this changes

The measured temporal improvement shows that this fixed pipeline's output
depends on which interval it receives. It does not establish a TimesFM timing
benefit, useful word information, or cue contamination. Failure here also does
not establish that the EEG contains no word information: each head had only
16–19 calibration examples and the representations/readout were fixed.

The intervals are exploratory, unadjusted and based on reused development
data. They are not confirmatory tests or evidence of equivalence. The early
window is [0,2) seconds and the late window [2,4) seconds after the recorded
word marker. The [dataset paper](https://www.nature.com/articles/s41597-025-05387-w)
does not establish separate measured cue and imagery onsets. These windows
cannot isolate reading, eye closure, internal speech, or peripheral artifacts.

## Enabling engineering and execution

Only early extraction, feature inference, fitting and scoring were new. Late
values came from already public D2 participant aggregates: **zero late refits
or rescores**. Identical trials, splits, training counts and label identities
were preserved. Early-window filtering never accessed later samples. Sessions
2, 5 and 6 remained closed; there were no downloads.

The code and early prediction hashes were committed and pushed at `724c4a6`
before the sole score. Three focused tests passed, including one-based marker
indexing, exact allowed inputs, and filtering isolation. Read-only independent
reviews checked implementation, timing interpretation and aggregate arithmetic.

| Stage | Runtime (seconds) | Peak RSS (bytes) |
| --- | ---: | ---: |
| Early extraction | 1.438 | 173,211,648 |
| Feature inference | 71.039 | 2,350,448,640 |
| Frozen-head predictions | 31.444 | 463,028,224 |
| Sole early score and aggregate comparison | 0.226 | 48,906,240 |

One CPU thread; approximately 104 seconds of measured worker time; 74,958,933
new bytes at scoring. The 144 existing selected files totaled 189,555,798 bytes.
Raw signals, labels, features, weights and trial probabilities remain local.

Render the aggregate-only figure and full comparison table locally with:

```sh
MPLCONFIGDIR=/tmp/neurodecodekit-mpl .venv/bin/python scripts/render_word_timing_diagnostic.py
```

This reads only the public aggregate and never runs a model or scorer. Outputs
are under `.codex_work/word-timing-d3/report/`.

The next result-bearing question is whether the current tiny calibration set
is limiting performance: a separately fixed calibration-size learning curve
with the same no-signal controls could test that. It was not run here.
