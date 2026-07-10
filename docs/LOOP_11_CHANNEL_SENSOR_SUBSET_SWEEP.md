# Loop 11 - Channel / Sensor Subset Sweep

Date: 2026-07-10

Status: **Done for real-data resource, geometry, and proxy characterization.
No channel count, sensor layout, or decoding-accuracy winner is selected.**

## Question

Can a geometry-aware channel selection replace the arbitrary first-channel
smoke subset, reduce local storage and model input width, and leave explicit
candidates for a later decoder test?

This loop does not answer how many channels are sufficient for decoding. The
available real slice is one S21 block, and one-block variance or random/text
splits cannot establish block, session, subject, or hardware generalization.

## Research Anchor

Brain2Qwerty v2 used a 306-channel Megin system with 102 magnetometers and 204
planar gradiometers. Its sensor-count ablation randomly retained 230, 153, or
76 of the 306 channels, retrained the complete multi-subject pipeline, and ran
four independent sensor-selection seeds at each fraction.

| Official retained fraction | Channels | WER | Difference from 306-channel WER 0.433 |
|---:|---:|---:|---:|
| 75% | 230 | 0.467 | +0.034 |
| 50% | 153 | 0.490 | +0.057 |
| 25% | 76 | 0.547 | +0.114 |

The paper presents this as evidence that lower-count arrays deserve further
study. It does not prove that arbitrary subsets are equivalent to OPM hardware
or that a particular low-count geometry is optimal.

The same v2 paper says that the encoder uses sensor coordinates in a learned
spatial channel merger, mapping variable raw arrays to 270 virtual channels.
That makes geometry part of the model contract, not optional metadata.

Primary sources:

- https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py#L33-L50

Important comparison boundary:

```text
official v2: 306 mixed MEG channels, nine subjects, full retraining, WER
local Loop 11: 102 magnetometers, one S21 block, no model, proxy metrics only
```

Brain2Qwerty v2 is also a whole-sentence, non-causal system recorded while
participants physically type. Neither the official result nor this loop is
arbitrary thought reading or current low-latency streaming.

## Why Build a 102-Magnetometer Base

The prior 16-channel cache used the first channels in FIF file order. Those 16
mixed channels covered only six nearby Neuromag sensor sites and were useful
for resource smoke testing, not sensor-layout research.

The validated raw header contains:

```text
raw bytes:       1,812,164,730
sampling rate:   2,048 Hz
duration:        705.322 sec
MEG channels:    306
magnetometers:   102
gradiometers:    204
bad channels:    0
```

Loop 11 extracts all 102 magnetometers. On this Megin array, that gives one
magnetometer at each of 102 physical sensor sites, avoiding a spatial selector
that spends several slots on co-located magnetometer/gradiometer triplets. It
is still a modality reduction from the official 306-channel input and is not
an OPM simulation.

Sentence extraction now records one geometry row per selected channel:

```text
name
type
position_m       raw.info["chs"][index]["loc"][:3]
coord_frame
coil_type
unit
```

All 102 positions are finite, unique, in coordinate frame `1`, and span a
267.321 mm array diameter.

## Implementation

Loop 11 adds:

```text
src/neurodecodekit/experiments/channel_subset_sweep.py
tests/test_channel_subset_sweep.py
neurodecode channel-subset-sweep
geometry-aware extract-sentence-cache metadata
```

The cache-only runner:

1. requires finite geometry for every base channel
2. validates unique channel counts below the base count
3. builds one nested ordering per strategy
4. preserves original base-cache channel order in every written cache
5. refuses projected output above `--max-output-mb` before writing
6. refuses silent overwrite without `--overwrite`
7. validates each written sentence cache
8. checks all trial, text, target, and timing arrays against the base
9. checks each written signal tensor against the exact base-cache slice
10. reports resource, variance, geometry, and set-overlap evidence

The four strategies are:

- `spatial-fps`: deterministic farthest-point sampling in device coordinates;
  starts farthest from the array centroid, then maximizes distance to the
  nearest selected sensor.
- `variance`: ranks post-RobustScaler marginal channel variance on this block.
  This is data-dependent and must be fit only on training data in a future
  evaluation.
- `random`: deterministic NumPy permutation with seed 17; a control, not an
  optimized design.
- `first`: original FIF order after magnetometer picking; a file-order control,
  not an anatomical selection.

Counts `76/51/25` mirror 75/50/25 percent of the 102-magnetometer base. Counts
`16/8` test the much smaller local-device regime. Every strategy is nested, so
its smaller set is always contained in its larger set.

## Proxy Metrics

No CER, WER, or classifier score is computed. The reported metrics are:

- compressed NPZ bytes and fraction of the 102-channel base
- marginal variance share over valid, non-padding samples
- mean and maximum distance from every base sensor to its nearest selected
  sensor
- selected-array diameter and minimum pairwise distance
- selected-channel hashes and cross-strategy Jaccard overlap
- exact trial/text/timing and signal-slice identity

The variance metric is computed after per-channel median/IQR scaling and
clamping. It measures residual post-scaling dynamics, not raw magnetic energy,
unique information, causality, or decodability. The spatial metric uses device
coordinates, not cortical source localization or a motor-language ROI.

## Real Commands

No new raw data was downloaded.

```bash
OMP_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 \
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --sfreq 100 \
  --pre-context 0.4 \
  --post-context 0.45 \
  --picks mag \
  --max-channels 102 \
  --stim-channel STI101 \
  --l-freq 0.5 \
  --h-freq 45 \
  --notch-freq 50 \
  --clamp 5 \
  --summary-json cache/loop11_s21_channel_subset/base_102mag_100hz.extraction.json

neurodecode channel-subset-sweep \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --out-dir cache/loop11_s21_channel_subset/subsets \
  --counts 76 51 25 16 8 \
  --strategies spatial-fps variance random first \
  --seed 17 \
  --max-output-mb 128
```

Runtime environment:

```text
macOS 26.6 arm64
Python 3.13.5
MNE 1.12.1
NumPy 2.5.0
SciPy 1.18.0
one thread for the raw extraction command
```

## Resource Result

Base extraction:

```text
shape:              66 x 102 x 617
valid timepoints:   28,397
cache bytes:        10,602,568 (10.1 MiB)
runtime:            12.003939 sec
peak RSS:           1,679,278,080 B (about 1.56 GiB)
swaps:              0
additional data:    0 bytes
```

Subset sweep:

```text
subset caches:                  20
cache + metadata sidecar bytes: 73,683,875 (70.3 MiB)
runtime:                        3.491672 sec
peak RSS:                       270,499,840 B (about 258 MiB)
projected uncompressed bytes:   119,485,664
explicit cap:                   134,217,728 B (128 MiB)
```

## Measured Proxy Result

| Count | Strategy | Cache | Variance share | Mean coverage | Max coverage | Diameter |
|---:|---|---:|---:|---:|---:|---:|
| 76 | spatial-fps | 7.5 MiB | 74.2% | 8.5 mm | 33.8 mm | 267.3 mm |
| 76 | variance | 7.5 MiB | 80.0% | 9.0 mm | 45.6 mm | 267.3 mm |
| 76 | random | 7.5 MiB | 75.7% | 8.7 mm | 35.4 mm | 267.3 mm |
| 76 | first | 7.5 MiB | 75.5% | 13.5 mm | 99.0 mm | 265.5 mm |
| 51 | spatial-fps | 5.1 MiB | 48.5% | 17.0 mm | 35.2 mm | 267.3 mm |
| 51 | variance | 5.0 MiB | 56.6% | 21.3 mm | 74.2 mm | 267.3 mm |
| 51 | random | 5.1 MiB | 50.7% | 17.5 mm | 47.2 mm | 266.5 mm |
| 51 | first | 5.0 MiB | 50.7% | 39.1 mm | 157.8 mm | 235.7 mm |
| 25 | spatial-fps | 2.5 MiB | 23.3% | 27.6 mm | 49.9 mm | 267.3 mm |
| 25 | variance | 2.5 MiB | 30.7% | 40.2 mm | 98.8 mm | 251.1 mm |
| 25 | random | 2.5 MiB | 25.2% | 32.2 mm | 83.3 mm | 260.0 mm |
| 25 | first | 2.5 MiB | 24.9% | 83.5 mm | 215.2 mm | 204.1 mm |
| 16 | spatial-fps | 1.6 MiB | 14.8% | 34.9 mm | 69.8 mm | 267.3 mm |
| 16 | variance | 1.6 MiB | 21.3% | 56.6 mm | 140.3 mm | 233.4 mm |
| 16 | random | 1.6 MiB | 15.2% | 42.0 mm | 96.4 mm | 260.0 mm |
| 16 | first | 1.6 MiB | 14.7% | 102.2 mm | 219.3 mm | 170.8 mm |
| 8 | spatial-fps | 831.5 KiB | 7.1% | 54.4 mm | 107.8 mm | 267.3 mm |
| 8 | variance | 780.7 KiB | 12.5% | 65.8 mm | 140.3 mm | 231.6 mm |
| 8 | random | 830.4 KiB | 7.4% | 59.8 mm | 151.5 mm | 239.0 mm |
| 8 | first | 822.0 KiB | 7.7% | 127.2 mm | 219.8 mm | 109.7 mm |

Spatial FPS has the lowest mean coverage distance at every count. Variance has
the highest marginal variance share at every count. File-order selection
becomes strongly spatially clustered below 76 channels.

The low-count candidate sets are genuinely different:

| Count | FPS/variance overlap | Jaccard |
|---:|---:|---:|
| 76 | 57 | 0.600 |
| 51 | 24 | 0.308 |
| 25 | 5 | 0.111 |
| 16 | 2 | 0.067 |
| 8 | 0 | 0.000 |

At 16 channels, spatial FPS improves mean coverage by 67.8% versus file order
(`102.2 -> 34.9 mm`) while keeping nearly the same variance share. Variance
ranking raises variance share by 44.3% versus spatial FPS (`14.8% -> 21.3%`)
but doubles the mean coverage distance (`34.9 -> 56.6 mm`). These are different
hypotheses, not interchangeable implementations.

## Decision

```text
carry_two_candidates_to_future_accuracy_test
```

Carry `spatial-fps` and `variance` forward. Keep `random` and `first` as
controls. Do not choose a channel count yet.

A valid future accuracy comparison must:

1. obtain a second correctly paired block/session or broader subject data
2. define the split before fitting any data-dependent selector
3. fit variance ranking only on training data
4. keep the same selected channel identity across train/eval as required by
   the model contract
5. compare against the no-brain baseline
6. report CER/WER separately from resource and geometry metrics
7. avoid claiming equivalence to OPM or at-home hardware

## Acceptance Gate

- [x] A full 102-magnetometer base is picked before signal preload.
- [x] Every channel has finite, unique geometry metadata.
- [x] Four explicit strategies and five counts are compared.
- [x] Twenty written caches validate under the sentence-cache contract.
- [x] Trial, text, target, timing, and signal-slice identity all pass.
- [x] Projected and actual output stay below the explicit 128 MiB cap.
- [x] Runtime, peak RSS, bytes, geometry, variance, and overlap are recorded.
- [x] No new raw data is downloaded.
- [x] No model is trained and no accuracy/channel-count winner is claimed.
- [x] JSON, Markdown, metadata sidecars, docs, and workbook tracker are updated.

## Artifacts

Local ignored artifacts:

```text
cache/loop11_s21_channel_subset/base_102mag_100hz.npz
cache/loop11_s21_channel_subset/base_102mag_100hz.extraction.json
cache/loop11_s21_channel_subset/subsets/sweep.json
cache/loop11_s21_channel_subset/subsets/sweep.md
cache/loop11_s21_channel_subset/subsets/subset_*.npz
cache/loop11_s21_channel_subset/subsets/subset_*.metadata.json
```

Versioned artifacts:

```text
src/neurodecodekit/experiments/channel_subset_sweep.py
tests/test_channel_subset_sweep.py
docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md
docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx
```

## Next Gate

Loop 12 should compare numeric representation and serialization cost on the
fixed 102-channel base plus the 16-channel FPS and variance candidates. It must
report reconstruction error, clipping/saturation, encode/load time, bytes, and
exact non-signal identity. Representation distortion is not retained decoder
accuracy; model selection still waits for the held-out real-data gate.
