# Loop 10 - Sampling-Rate Resource Sweep

Date: 2026-07-10

Status: **Done for resource and CTC-length characterization. No sampling rate
has been selected, and no real decoding accuracy is claimed.**

## Question

How much local storage and sequence length can be removed by changing the
continuous sentence-cache sampling rate, and what constraints does that place
on a future CTC encoder?

This loop deliberately does not answer which rate preserves decoding accuracy.
The current real dataset slice is one S21 block, so training and evaluating on
it would not establish session or subject generalization.

## Research Anchor

The official Brain2Qwerty v2 configuration uses:

```text
sampling rate: 100 Hz
bandpass:      0.5-45 Hz
notch:         50 Hz
scaler:        RobustScaler
clamp:         +/-5
```

Pinned source at the audited upstream commit:

https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/xp_config.py#L45-L59

The official v2 temporal reducer uses a no-padding 1D convolution with kernel
size 16 and stride 4. The upstream length utility computes:

```text
(input_steps - 16) // 4 + 1
```

Pinned sources:

- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py#L33-L50
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/utils.py#L72-L78

MNE documents that `Raw.resample()` applies a low-pass filter before sample
selection to avoid aliasing. Therefore, the lower-rate variants are not merely
smaller representations:

```text
100 Hz -> Nyquist 50 Hz -> effective upper bandwidth 45 Hz
 50 Hz -> Nyquist 25 Hz -> effective upper bandwidth 25 Hz
 25 Hz -> Nyquist 12.5 Hz -> effective upper bandwidth 12.5 Hz
```

Source:

https://mne.tools/stable/help/faq.html#resampling-and-decimating-data

MNE also warns that resampling continuous raw data can quantize or jitter event
timing. NeuroDecodeKit derives STI101 events at the original raw rate before
resampling, then stores the resulting sentence boundaries on each target-rate
grid. This report measures the remaining boundary-grid difference explicitly.

## Implementation

Loop 10 adds:

```text
src/neurodecodekit/experiments/sampling_rate_sweep.py
tests/test_sampling_rate_sweep.py
neurodecode sampling-rate-sweep
```

The runner:

1. sorts and validates unique rates
2. refuses to overwrite planned artifacts unless `--overwrite` is explicit
3. launches one fresh extraction worker per rate
4. runs workers sequentially, never concurrently
5. forces common BLAS/OpenMP thread environment variables to `1`
6. validates every resulting sentence cache
7. checks exact trial, typed text, reference text, MAT response, and channel
   identity across rates
8. excludes zero padding from signal summaries
9. computes exact CTC minimum-length margins, including repeated-character
   requirements
10. writes JSON, Markdown, per-rate metadata, extraction summaries, and worker
    logs

Separate worker processes are intentional. They release MNE state between
rates and make each reported peak RSS a fresh-process high-water mark.

## Real Command

No new data was downloaded. The sweep reuses the validated S21 session-1 block:

```bash
neurodecode sampling-rate-sweep \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out-dir cache/loop10_s21_sampling_rate_sweep \
  --rates 100 50 25 \
  --pre-context 0.4 \
  --post-context 0.45 \
  --picks meg \
  --max-channels 16 \
  --stim-channel STI101 \
  --l-freq 0.5 \
  --h-freq 45 \
  --notch-freq 50 \
  --clamp 5
```

Runtime environment:

```text
macOS 26.6 arm64
Python 3.13.5
MNE 1.12.1
NumPy 2.5.0
SciPy 1.18.0
one thread per worker
```

## Measured Result

All three caches contain the same 66 trial IDs, typed targets, prompt texts,
MAT-recorded responses, and 16 MEG channel names.

| Rate | Effective bandwidth | Cache bytes | vs 100 Hz | Extraction | Peak RSS | Shape | Valid steps |
|---:|---:|---:|---:|---:|---:|---|---:|
| 100 Hz | 45 Hz | 1,663,209 | 100.0% | 4.121 s | 560,627,712 B | 66 x 16 x 617 | 28,397 |
| 50 Hz | 25 Hz | 846,334 | 50.9% | 3.586 s | 602,537,984 B | 66 x 16 x 309 | 14,234 |
| 25 Hz | 12.5 Hz | 431,451 | 25.9% | 3.539 s | 614,154,240 B | 66 x 16 x 155 | 7,148 |

Whole-sweep resources:

```text
wall time:          11.778 sec inside the final report
summed extraction:  11.246 sec
total cache bytes:  2,940,994 (2.80 MiB)
peak worker RSS:    614,154,240 bytes (about 586 MiB)
additional raw data: 0 bytes
```

Three successful validation passes produced 11.78-13.20 seconds total internal
wall time and about 586-604 MiB peak worker RSS. Cache sizes, shapes, identity,
bandwidth limits, timing grids, and CTC margins were unchanged. Runtime and RSS
should be treated as machine-local measurements with normal cold/warm-cache
variation.

Storage tracks the rate closely. Runtime and memory do not: repeated raw-file
opening, MNE/SciPy imports, filtering, and fixed process overhead dominate this
small 16-channel experiment.

## Timing Quantization

| Rate | Sample period | Max start shift vs 100 Hz | Max end shift vs 100 Hz |
|---:|---:|---:|---:|
| 100 Hz | 10 ms | 0 ms | 0 ms |
| 50 Hz | 20 ms | 10 ms | 10 ms |
| 25 Hz | 40 ms | 30 ms | 30 ms |

The total valid-duration difference between the coarsest and finest grids is
1.95 seconds summed over all 66 sentences, or 29.55 ms per sentence on average.
This is expected from flooring starts and ceiling ends to each target grid; it
is now measured rather than hidden.

## CTC Feasibility

The current tiny CTC emits one logit per input timepoint. Its minimum required
length accounts for adjacent repeated target characters, which need an
intervening blank.

| Rate | Stride-1 feasible | Stride-1 margin | Official k16/s4 feasible | Official margin | Conservative stride ceiling |
|---:|---:|---:|---:|---:|---:|
| 100 Hz | 66/66 | 302 | 66/66 | 49 | 10 |
| 50 Hz | 66/66 | 136 | 66/66 | 7 | 5 |
| 25 Hz | 66/66 | 53 | 0/66 | -15 | 2 |

The `25 Hz` cache is valid for the existing stride-one model, but **all 66
sentences become CTC-length infeasible under the exact official v2 kernel-16,
stride-4 reducer**. At 50 Hz the official temporal contract remains feasible,
but its worst row has only seven output steps of margin. A direct v2-style model
therefore cannot simply switch to 25 Hz; it would need less temporal
downsampling, a different tokenizer/target contract, or longer signal segments.

## Signal Summaries

Padding is excluded from these values:

| Rate | Valid RMS | Clamp saturation | Maximum absolute value |
|---:|---:|---:|---:|
| 100 Hz | 1.2406 | 2.442% | 5.0 |
| 50 Hz | 1.1749 | 1.835% | 5.0 |
| 25 Hz | 1.2111 | 2.139% | 5.0 |

The similar robust-scaled RMS values prove numerical stability, not retained
neural information. Per-rate robust scaling can make summary amplitudes look
similar after high-frequency content has been removed.

## Decision

```text
resource_characterized_no_rate_selected
```

Proceed with the compression/accessibility roadmap, but do not declare 25 or
50 Hz sufficient for decoding. The evidence supports these narrower claims:

- 50 Hz approximately halves sentence-cache storage and model timepoints.
- 25 Hz approximately quarters storage and model timepoints.
- neither rate materially reduces fresh extraction memory or wall time here.
- both rates reduce signal bandwidth and timing precision.
- all current targets remain CTC-length feasible at stride one.
- 50 Hz remains structurally feasible under the official v2 temporal reducer,
  with a narrow seven-step worst-case margin.
- 25 Hz is structurally incompatible with that exact reducer for 66/66 rows.

## Acceptance Gate

- [x] At least three sampling rates are compared.
- [x] The same real trials, texts, and channels are verified across rates.
- [x] Cache bytes, runtime, peak RSS, bandwidth, timing, and signal summaries
      are recorded.
- [x] Exact CTC length feasibility is recorded.
- [x] The official v2 kernel-16, stride-4 output-length contract is audited.
- [x] Execution is sequential and one-thread bounded.
- [x] No new raw data is downloaded.
- [x] No real decoder score or rate winner is claimed.
- [x] JSON and Markdown artifacts are written without a notebook.

## Artifacts

Local ignored artifacts:

```text
cache/loop10_s21_sampling_rate_sweep/sweep.json
cache/loop10_s21_sampling_rate_sweep/sweep.md
cache/loop10_s21_sampling_rate_sweep/sentence_100hz.npz
cache/loop10_s21_sampling_rate_sweep/sentence_50hz.npz
cache/loop10_s21_sampling_rate_sweep/sentence_25hz.npz
cache/loop10_s21_sampling_rate_sweep/*.metadata.json
cache/loop10_s21_sampling_rate_sweep/*.extraction.json
cache/loop10_s21_sampling_rate_sweep/*.worker.log
```

## Next Gate (completed by Loop 11)

Loop 11 characterized explicit geometry, variance, random, and file-order
channel subsets from the same validated source without selecting a channel
count. See `docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`. Actual sampling-rate
or channel accuracy decisions still require a second correctly paired
block/session and an explicit non-leaking split protocol; a one-block random or
text-hash score must not be presented as generalization.
