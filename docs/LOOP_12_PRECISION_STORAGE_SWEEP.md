# Loop 12 - Precision and Storage Sweep

Date: 2026-07-10

Status: **Done for real-cache representation, storage, reconstruction, and
resource characterization. Float32 remains the default. Qint16 and qint8 are
candidates for a later held-out decoder test, not accuracy winners.**

## Question

Can fixed, already validated sentence caches use less local disk space while
preserving an explicit, measurable bound on signal representation distortion?

This loop does not answer whether lower precision preserves CER, WER, semantic
accuracy, cross-session generalization, or real-time behavior. It uses one S21
block and trains no decoder.

Proof posture:

```text
single_block_multi_cache_representation_fidelity_study
```

## Why This Loop Exists

Local accessibility has several separate resource layers:

1. raw MEG download and storage
2. preprocessed cache storage and load time
3. decoded tensor RAM
4. model parameter and activation RAM
5. training and inference compute

Loop 12 addresses only layers 2 and part of 3. A packed cache is decoded to a
float32 semantic tensor before the current tiny CTC interface consumes it. It
therefore reduces disk bytes and may reduce file load time, but it does not by
itself provide integer-only inference, smaller model weights, lower activation
memory, causal decoding, or an at-home sensor.

## Research Anchor

The Brain2Qwerty v2 paper reports BF16 mixed-precision training with gradient
accumulation on eight A100 80 GB GPUs. The full staged pipeline ran for 275
epochs in 19.5 hours. This is useful compute context, but it does not establish
that official MEG inputs were stored as BF16 caches or that BF16 is the best
local signal representation.

Primary sources:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Pinned official v2 model configuration:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py
- BFLOAT16 training study:
  https://arxiv.org/abs/1905.12322
- Integer quantization research context:
  https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html
- NumPy compressed NPZ contract:
  https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html
- NumPy safe loading guidance:
  https://numpy.org/doc/stable/reference/generated/numpy.load.html

NumPy documents compressed NPZ as a ZIP archive using DEFLATE, with one NPY
member per array. Every Loop 12 loader uses `allow_pickle=False`.

Important comparison boundary:

```text
official v2 BF16: model training arithmetic on large GPU hardware
local Loop 12: input-cache serialization decoded to float32 on CPU
```

## Fixed Inputs

No raw data was downloaded or reprocessed. The sweep reads three Loop 11
sentence caches:

| Input | Shape | Source bytes | Purpose |
|---|---:|---:|---|
| `base_102mag_100hz` | 66 x 102 x 617 | 10,602,568 | full magnetometer base |
| `subset_spatial-fps_16ch` | 66 x 16 x 617 | 1,684,256 | geometry candidate |
| `subset_variance_16ch` | 66 x 16 x 617 | 1,636,209 | signal-proxy candidate |

All three contain the same 66 trial/text/timing rows at 100 Hz. Their signal
values were robust-scaled and clamped to `[-5, 5]` during the existing Loop 11
preprocessing path.

## Representation Contract

Loop 12 adds schema:

```text
b2q-signal-representation-cache@0
```

Each representation NPZ contains:

```text
signal_payload
input_lengths
target_token_ids
target_lengths
target_texts
reference_texts
mat_response_texts
trial_indices
sentence_start_sec
sentence_end_sec
channel_names
metadata
```

The packed file records its physical payload dtype and encoding parameters,
the complete semantic `b2q-sentence-cache@0` metadata, source path/bytes/hash,
array descriptors, and proof warnings. Loading performs these steps:

1. load with `allow_pickle=False`
2. validate the representation schema and payload dtype
3. decode signals to float32
4. validate the complete semantic sentence-cache contract
5. expose the same fields used by the tiny CTC baseline

`load_sentence_cache_auto()` accepts either the original sentence cache or a
packed representation. The original float32 sentence-cache format remains the
default and is not silently rewritten.

## Compared Encodings

| Encoding | Physical payload | Rule | Intended role |
|---|---|---|---|
| `float32` | float32 | direct reference copy | lossless control |
| `float16` | float16 | IEEE float16 cast | common 16-bit float baseline |
| `bfloat16` | packed uint16 | round-to-nearest-even upper float32 bits | BF16 context baseline |
| `qint16` | int16 | symmetric fixed range, scale `5/32767`, zero point 0 | high-fidelity packed candidate |
| `qint8` | int8 | symmetric fixed range, scale `5/127`, zero point 0 | aggressive storage candidate |

The integer range is fixed from the existing preprocessing clamp. It is not
fit to these evaluation values, so the sweep does not introduce a data-derived
calibration threshold. By default, any source value outside `[-5, 5]` causes a
pre-write refusal. `--allow-clipping` must be explicit and reports the count.

## Reported Metrics

All numeric errors exclude zero padding and include:

- MAE, RMSE, relative RMSE against source RMS
- maximum and p99 absolute error
- SNR and global Pearson correlation
- first-difference RMSE as a temporal-change proxy
- worst per-channel RMSE
- exact-value fraction
- aggregate Hann-windowed bandpower error at 0.5-4, 4-8, 8-13, 13-30,
  and 30-45 Hz
- source values outside the fixed range
- source and payload values on quantizer rails
- exact zero padding after decode
- exact hashes for every non-signal array
- payload, compressed cache, sidecar, encode, write, decode, and load time

Bandpower is a signal-fidelity proxy. It is not evidence that task-relevant
neural information, decoder accuracy, or causal timing was preserved.

## Real Command

The host was already running unrelated browser workloads, so the sweep ran as
one low-priority sequential process with common numeric thread pools capped at
one:

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 \
nice -n 10 \
neurodecode precision-storage-sweep \
  --cache \
    cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
    cache/loop11_s21_channel_subset/subsets/subset_spatial-fps_16ch.npz \
    cache/loop11_s21_channel_subset/subsets/subset_variance_16ch.npz \
  --out-dir cache/loop12_s21_precision_storage \
  --variants float32 float16 bfloat16 qint16 qint8 \
  --clip-abs 5 \
  --repetitions 3 \
  --max-output-mb 96
```

The runner projected 63,297,389 uncompressed bytes before creating the output
directory, below the 100,663,296-byte cap. It refuses existing planned outputs
unless `--overwrite` is explicit.

## Real Results

Aggregate compressed cache results across all three inputs:

| Encoding | Cache bytes | Reduction vs float32 representation | Mean relative RMSE | Worst relative RMSE | Mean median load/decode |
|---|---:|---:|---:|---:|---:|
| `float32` | 13,925,424 | 0.00% | 0 | 0 | 0.026441 s |
| `float16` | 6,609,642 | 52.54% | 0.000173339 | 0.000179199 | 0.018091 s |
| `bfloat16` | 5,400,633 | 61.22% | 0.00138475 | 0.00143170 | 0.015717 s |
| `qint16` | 6,984,779 | 49.84% | 0.000034456 | 0.000036926 | 0.016381 s |
| `qint8` | 2,679,951 | 80.75% | 0.00889354 | 0.00953116 | 0.011714 s |

Per-input reconstruction:

| Input | Encoding | Compressed bytes | RMSE | Max error | SNR | Maximum bandpower error |
|---|---|---:|---:|---:|---:|---:|
| base 102 | `float16` | 5,097,428 | 0.000215804 | 0.00195313 | 75.05 dB | 0.000585% |
| base 102 | `bfloat16` | 4,186,617 | 0.00172563 | 0.0156245 | 56.99 dB | 0.026365% |
| base 102 | `qint16` | 5,361,654 | 0.000043704 | 0.000076532 | 88.92 dB | 0.000097% |
| base 102 | `qint8` | 2,046,008 | 0.0112794 | 0.0196851 | 40.68 dB | 1.087198% |
| FPS 16 | `float16` | 845,707 | 0.000212234 | 0.00195313 | 74.93 dB | 0.001848% |
| FPS 16 | `bfloat16` | 706,746 | 0.00169563 | 0.0156226 | 56.88 dB | 0.025383% |
| FPS 16 | `qint16` | 878,732 | 0.000043733 | 0.000076532 | 88.65 dB | 0.000265% |
| FPS 16 | `qint8` | 366,028 | 0.0112882 | 0.0196848 | 40.42 dB | 0.975311% |
| variance 16 | `float16` | 666,507 | 0.000232289 | 0.00195313 | 75.71 dB | 0.001673% |
| variance 16 | `bfloat16` | 507,270 | 0.00185358 | 0.0156226 | 57.67 dB | 0.019716% |
| variance 16 | `qint16` | 744,393 | 0.000043389 | 0.000076532 | 90.28 dB | 0.000387% |
| variance 16 | `qint8` | 267,915 | 0.0112002 | 0.0196850 | 42.04 dB | 0.405450% |

Every encoding lies on the per-input byte/RMSE Pareto frontier: each smaller
representation introduces more reconstruction error, while qint16 trades a
small compressed-size penalty against float16 for substantially lower error.

### Clipping and saturation

All integer inputs passed the strict range check:

```text
source values outside [-5, 5]: 0
decoded padding nonzero values: 0
```

The existing robust preprocessing clamp places some source values exactly at
`-5` or `5`. Across the three inputs, 67,113 values are already on those
boundaries. Qint16 has 67,116 payload values on its integer rails; qint8 has
67,461 because 8-bit rounding maps another 348 near-boundary values to a rail.
These are reported saturation counts, but they are not newly clipped source
values. No source value exceeded the declared range.

### Exact identity

All 15 artifacts preserve exact hashes for:

```text
input_lengths
target_token_ids
target_lengths
target_texts
reference_texts
mat_response_texts
trial_indices
sentence_start_sec
sentence_end_sec
channel_names
```

All semantic metadata is exact, all decoded shapes match, and all padded tails
remain exactly zero.

### Resources

```text
runtime:                              3.788511 sec
peak process RSS:                     385,318,912 bytes (367.5 MiB)
representation caches + sidecars:     36,083,085 bytes (34.4 MiB)
all artifacts including reports:      36,212,760 bytes (34.5 MiB)
hard output cap:                       100,663,296 bytes (96 MiB)
```

The peak RSS belongs to the whole analysis process, which holds the three
source caches and computes reconstruction/spectral metrics. It is not the RAM
required by a single qint8 cache load or by a future model.

## Decision

Keep `float32` as the default representation.

Carry two candidates into a future fixed-split decoder evaluation:

- `qint16`: fidelity candidate; about 50% smaller than the float32
  representation with at most 0.003693% relative RMSE across these inputs.
- `qint8`: aggressive storage candidate; about 81% smaller with at most
  0.9531% relative RMSE and at most 1.0872% aggregate bandpower error.

Do not call either candidate accuracy-preserving. A decoder must be trained and
evaluated on a leakage-resistant held-out block/session, with the float32
cache, no-brain baseline, and fixed model/split used for every representation.

Float16 and BF16 remain useful interoperability/context baselines. Qint16 has
about five times lower mean RMSE than float16 but slightly larger compressed
files. BF16 compresses better than float16 here but has substantially larger
reconstruction error. Official BF16 training does not override those local
input-cache measurements.

## Implementation Artifacts

Versioned:

```text
src/neurodecodekit/cache/signal_representation.py
src/neurodecodekit/experiments/precision_storage_sweep.py
tests/test_signal_representation.py
tests/test_precision_storage_sweep.py
docs/LOOP_12_PRECISION_STORAGE_SWEEP.md
```

Local ignored evidence:

```text
cache/loop12_s21_precision_storage/sweep.json
cache/loop12_s21_precision_storage/sweep.md
cache/loop12_s21_precision_storage/*.npz
cache/loop12_s21_precision_storage/*.metadata.json
```

## Verification

Focused contract verification before the real run:

```text
python -m unittest tests.test_signal_representation \
  tests.test_precision_storage_sweep tests.test_sentence_npz
Ran 13 tests in 0.246s - OK

ruff check focused Loop 12 files
All checks passed

git diff --check
clean
```

Final closeout verification after documentation and tracker edits:

```text
python -m unittest discover -s tests
Ran 130 tests in 3.183s - OK (skipped=3)

pytest -q
127 passed, 3 skipped, 13 subtests passed in 2.83s

ruff check .
All checks passed

all 15 real representation NPZ files revalidated through
neurodecode inspect-representation-cache

Excel tracker: 7/7 sheets visually rendered; key tables reconciled;
formula-error scan matched 0 cells
```

## What This Does Not Prove

- no decoder was trained or evaluated
- no CER, WER, semantic, or calibration result exists
- no session, subject, or hardware generalization was tested
- no packed representation reduces current model weights or activation RAM
- no integer-only inference kernel was implemented
- no causal or low-latency decoder was implemented
- no at-home MEG/EEG hardware claim exists
- the real cache records physical typing, not arbitrary thought production

## Next Gate

Loop 13 was run as a measured lazy-loading backend gate, not an automatic
rewrite. Compressed NPZ loads and decodes complete array members, but all nine
tested real standard/packed caches remained below the declared absolute time,
memory, and size budgets with exact decoded hashes. The optional Zarr build was
therefore parked and NPZ remains the bounded-block default. See
`docs/LOOP_13_LAZY_BACKEND_GATE.md`.

Representation candidates still require the later Loop 14 held-out split
protocol before any retained-accuracy claim.
