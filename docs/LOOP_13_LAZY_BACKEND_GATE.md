# Loop 13 - Measured Lazy-Backend Gate

Date: 2026-07-10

Status: **Parked by evidence. Keep per-block NPZ as the default. Do not install
or implement Zarr yet. Proceed to Loop 14.**

Proof posture:

```text
current_real_cache_npz_access_gate_no_zarr_install
```

This loop closes a roadmap question, not a decoder-performance question. It
asks whether the current compressed NPZ cache path is already slow, memory
heavy, or awkward enough to justify another runtime backend.

It does **not**:

- train or evaluate a neural decoder
- compare decoder accuracy across cache formats
- install or benchmark Zarr
- establish a universal NPZ-versus-Zarr result
- claim low-latency streaming or at-home hardware readiness

## Decision

Park the optional Zarr implementation and retain one bounded NPZ file per
recording block.

All nine tested real standard/packed caches remained below the declared local
budgets:

```text
largest compressed cache:       10,602,568 bytes (10.1 MiB)
slowest full-load median:       60.386 ms
slowest partial-load median:    53.634 ms
highest worker peak RSS:       147,456,000 bytes (140.6 MiB)
exact decoded-signal hashes:     all pass
total benchmark runtime:         5.358 sec
new cache/backend bytes:         0
report bytes:                   40,101
```

The current evidence says NPZ partial access is inefficient but not yet a
material local bottleneck. Another backend would add a dependency, schema,
test matrix, migration path, and disk footprint without solving the next
scientific risk. The next risk is evaluation leakage, so Loop 14 takes priority.

## Question and acceptance gate

Question:

> Does complete or partial access to current sentence caches exceed a declared
> local time, memory, or file-size budget while preserving exact semantic
> signals?

The gate was declared before the real run:

| Measure | Revisit threshold |
|---|---:|
| Median full semantic load | 250 ms |
| Median partial row read | 100 ms |
| Worker peak RSS | 512 MiB |
| One compressed cache | 128 MiB |
| Decoded signal identity | Exact SHA-256 match required |

These are local product budgets for the current tiny-cache workflow. They are
not general claims about either file format.

If any threshold or identity check failed, the next action would be a bounded
Zarr comparison, not immediate adoption.

## Primary-source research

NumPy documents `savez_compressed` as writing a compressed ZIP archive whose
members are `.npy` files. `NpzFile` lazily exposes archive members, but this
does not make a slice within one compressed array member independently
addressable:

- https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html
- https://numpy.org/doc/stable/reference/generated/numpy.lib.npyio.NpzFile.html

Zarr arrays are divided into chunks. A regular chunk grid maps array regions to
independently addressable chunk keys, which can make repeated subarray access
materially cheaper when the chunk layout matches the workload:

- https://zarr.readthedocs.io/en/stable/quick-start/
- https://zarr.readthedocs.io/en/stable/user-guide/arrays/
- https://zarr-specs.readthedocs.io/en/latest/v3/chunk-grids/regular-grid/

That capability is real. The engineering question is whether the current
workflow needs it now. Capability alone is not sufficient evidence to add a
backend.

## Implementation

Loop 13 adds:

- `neurodecodekit.experiments.lazy_backend_gate.run_lazy_backend_gate`
- `neurodecode lazy-backend-gate`
- fresh subprocesses for each cache/access pattern
- one-thread caps for common numerical runtimes
- complete semantic loads plus 1-row and 8-row partial reads
- standard `b2q-sentence-cache` and packed
  `b2q-signal-representation-cache` support
- exact decoded-array SHA-256 comparisons
- explicit time, RSS, and compressed-size thresholds
- JSON and Markdown reports
- a park/build decision with durable revisit triggers

No Zarr dependency, cache, adapter, or migration code was added.

## Real inputs

The gate reused nine existing S21 artifacts. It did not read the raw 621 MiB
FIF file and did not generate another signal cache.

| Input | Encoding | Compressed bytes | Shape |
|---|---|---:|---|
| `base_102mag_100hz` | float32 | 10,602,568 | 66 x 102 x 617 |
| `subset_spatial-fps_16ch` | float32 | 1,684,256 | 66 x 16 x 617 |
| `subset_variance_16ch` | float32 | 1,636,209 | 66 x 16 x 617 |
| `base_102mag_100hz__qint16` | qint16 | 5,361,654 | 66 x 102 x 617 |
| `base_102mag_100hz__qint8` | qint8 | 2,046,008 | 66 x 102 x 617 |
| `subset_spatial-fps_16ch__qint16` | qint16 | 878,732 | 66 x 16 x 617 |
| `subset_spatial-fps_16ch__qint8` | qint8 | 366,028 | 66 x 16 x 617 |
| `subset_variance_16ch__qint16` | qint16 | 744,393 | 66 x 16 x 617 |
| `subset_variance_16ch__qint8` | qint8 | 267,915 | 66 x 16 x 617 |

## Method

Each operation ran in a fresh child process. The parent set these environment
variables to `1` for every worker:

```text
OMP_NUM_THREADS
OPENBLAS_NUM_THREADS
MKL_NUM_THREADS
VECLIB_MAXIMUM_THREADS
NUMEXPR_NUM_THREADS
```

For every cache, the gate performed:

1. Five complete semantic loads through the public standard/packed auto-loader.
2. Five accesses to the first row.
3. Five accesses to the first eight rows.
4. Exact decoded-signal hash comparison against the public semantic loader.
5. Compressed byte, median time, and peak-RSS checks.

The partial path deliberately mirrors how the current NPZ representation must
be used: access the complete compressed signal/payload member, then slice and,
for packed formats, decode the selected payload.

Real command:

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 \
nice -n 10 neurodecode lazy-backend-gate \
  --cache \
    cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
    cache/loop11_s21_channel_subset/subsets/subset_spatial-fps_16ch.npz \
    cache/loop11_s21_channel_subset/subsets/subset_variance_16ch.npz \
    cache/loop12_s21_precision_storage/base_102mag_100hz__qint16.npz \
    cache/loop12_s21_precision_storage/base_102mag_100hz__qint8.npz \
    cache/loop12_s21_precision_storage/subset_spatial-fps_16ch__qint16.npz \
    cache/loop12_s21_precision_storage/subset_spatial-fps_16ch__qint8.npz \
    cache/loop12_s21_precision_storage/subset_variance_16ch__qint16.npz \
    cache/loop12_s21_precision_storage/subset_variance_16ch__qint8.npz \
  --out-dir cache/loop13_lazy_backend_gate \
  --row-counts 1 8 \
  --repetitions 5 \
  --max-full-load-ms 250 \
  --max-partial-load-ms 100 \
  --max-peak-rss-mb 512 \
  --revisit-cache-mb 128
```

## Results

| Cache | Full median | 1-row median | 8-row median | Highest worker RSS |
|---|---:|---:|---:|---:|
| base float32 | 60.386 ms | 49.449 ms | 53.634 ms | 97.0 MiB |
| FPS-16 float32 | 12.227 ms | 7.451 ms | 7.833 ms | 59.9 MiB |
| variance-16 float32 | 12.230 ms | 7.503 ms | 7.299 ms | 71.1 MiB |
| base qint16 | 29.970 ms | 21.889 ms | 23.174 ms | 140.6 MiB |
| base qint8 | 18.500 ms | 11.956 ms | 12.761 ms | 106.2 MiB |
| FPS-16 qint16 | 6.388 ms | 3.869 ms | 3.742 ms | 63.7 MiB |
| FPS-16 qint8 | 4.894 ms | 2.425 ms | 2.351 ms | 59.7 MiB |
| variance-16 qint16 | 6.499 ms | 5.334 ms | 4.975 ms | 78.6 MiB |
| variance-16 qint8 | 4.784 ms | 1.953 ms | 1.931 ms | 69.5 MiB |

All decoded-signal hashes matched exactly.

## What the partial-read numbers mean

A one-row request returns 1/66 of the sentence rows but causes the complete
compressed signal/payload member to be materialized before slicing. The
logical member-access amplification is therefore 66x. An eight-row request has
8.25x amplification.

The one-row median consumed 40.8% to 82.1% of the corresponding full-load
median. This confirms the predicted inefficiency. It does **not** cross the
absolute local budget: the slowest partial operation was 53.634 ms and the
largest worker peak was 140.6 MiB.

This distinction is the reason for the park decision:

```text
relative inefficiency: demonstrated
current material bottleneck: not demonstrated
```

## Revisit triggers

Rerun this gate and perform a bounded Zarr comparison when any of these becomes
true:

1. One compressed cache exceeds 128 MiB.
2. A complete semantic load exceeds 250 ms median.
3. A partial access exceeds 100 ms median.
4. A worker exceeds 512 MiB peak RSS.
5. A real training/inference workflow repeatedly reads subarrays instead of
   consuming one full bounded block.
6. Multi-block aggregation makes per-block NPZ files operationally awkward.

Adoption would still require:

- exact semantic parity with the sentence-cache interface
- bounded output preflight and overwrite protection
- chunk-shape rationale tied to measured access patterns
- no regression in the simple NPZ path
- measured bytes, load time, write time, and peak RSS

## Resource and storage posture

The run was intentionally small:

```text
input caches:            reused
raw FIF reads:           0
new signal caches:       0
new backend bytes:       0
JSON report:        36,870 bytes
Markdown report:     3,231 bytes
total new bytes:     40,101 bytes
```

Zarr and numcodecs were not installed. The benchmark itself ran in 5.358
seconds. Timings are machine-local and use the operating system's warm page
cache; they should be rerun after hardware, Python, NumPy, cache-size, or access
pattern changes.

## Artifacts

- `cache/loop13_lazy_backend_gate/gate.json`
- `cache/loop13_lazy_backend_gate/gate.md`

## Honest conclusion

Loop 13 advances local accessibility by avoiding an unnecessary dependency and
preserving a small, inspectable cache path. It does not show that NPZ is the
best backend for large-scale training. It shows only that the current bounded
S21 caches do not justify changing backends yet.

The scientifically important next step is Loop 14: deterministic sentence-text
splits, explicit session/subject boundaries, fit-on-train safeguards, and
machine-verifiable leakage reports before any real decoder comparison.
