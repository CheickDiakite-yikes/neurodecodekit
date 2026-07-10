# Loop 21 - Causal NeuroToken Chunk/Replay Gate

Completed on 2026-07-10 as a synthetic producer and transport-contract proof.
No real MEG/EEG cache, observed holdout, target array, trained model, CTC
decoder, language model, beam search, or network service was opened or run.

## Question

Can the Loop 20 continuous frame producer consume an incrementally arriving
signal with bounded mutable state, zero future context, explicit final-chunk
semantics, and stable outputs across transport chunk boundaries?

This question comes before model quality. A noncausal whole-sentence encoder
cannot become streaming merely by calling it repeatedly on a rolling buffer.
Likewise, a causal producer does not establish prompt text emission, decoder
stability, device capture latency, or user-perceived end-to-end latency.

## Research Basis

The public Brain2Qwerty v2 method uses a 100-Hz whole-sentence encoder with a
kernel-16/stride-4 temporal convolution followed by a noncausal Conformer. Its
paper explicitly identifies a fully real-time low-latency version as future
work. The public website's use of “online sentence generation” and the paper's
use of CTC mean that keypress timestamps are no longer required; neither proves
incremental low-latency text emission.

- v2 code pinned at `3bf5a4099ca0d23bbe994b2287905760236e56e0`:
  https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2
- v2 paper, especially architecture and limitations:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

Adjacent streaming-ASR work supplies two useful contract distinctions without
being evidence about brain decoding:

- Emformer caches bounded history/memory and declares right context rather than
  silently recomputing an unbounded sequence:
  https://ai.meta.com/research/publications/emformer-efficient-memory-transformer-based-acoustic-model-for-low-latency-streaming-speech-recognition/
- FastEmit treats symbol-emission delay as a decoder/training behavior. Fast
  encoder frames alone do not prove fast text:
  https://research.google/pubs/fastemit-low-latency-streaming-asr-with-sequence-level-emission-regularization/

The neighboring emg2qwerty project also maps continuous non-invasive waveform
signals to character tokens, but it measures wrist sEMG rather than brain data
and cannot establish MEG/EEG performance or sensing accessibility:

- https://github.com/facebookresearch/emg2qwerty/tree/3200d91eeb952cbed1f278e47d0cc56928334fd1
- https://papers.neurips.cc/paper_files/paper/2024/file/a64d53074d011e49af1dfc72c332fe4b-Paper-Datasets_and_Benchmarks_Track.pdf

## Registered Contract

`CausalMockNeuroTokenProducer` owns fixed target-free projection weights.
Each independent stream owns only an overlap buffer and counters.

```text
input chunk:                 [channels, newly arrived samples]
emitted tokens:              [ready frames, embedding]
kernel / stride:             16 / 4 samples
source rate:                 100 Hz
frame timestamp reference:   frame end
right context:               0 samples
first possible frame:        160 ms after item start
normal frame step:           40 ms
flush policy:                drop incomplete final frame
mutable state invariant:     fewer than 16 samples per channel
decoder causality:           unavailable; no decoder exists in this gate
end-to-end latency:          unmeasured
```

On every push, the stream:

1. appends only newly arrived finite floating samples;
2. emits every full kernel whose final sample has arrived;
3. timestamps each token using global source-sample indices;
4. keeps only the overlap needed by the next frame;
5. refuses channel mismatch, empty/nonfinite chunks, use after flush, or any
   item/chunk/token/state cap violation.

`flush(drop-incomplete)` does not invent a zero-padded token. It reports the
overlap buffer separately from the 0-3 newly unframed tail samples and then
clears mutable state.

## Floating-Point Reproducibility Finding

The adversarial test exposed a real implementation detail. NumPy may choose a
different matrix-multiply kernel when many frames are projected together than
when one frame is projected at a time. On this fixture, the established Loop 20
batched output differs from canonical one-frame streaming at up to
`9.5367431640625e-7`, while 97.7113% of float32 elements are bitwise equal.

Loop 21 does not silently rewrite the Loop 20 artifact. Instead:

- all streaming schedules use canonical one-frame arithmetic and must be
  bitwise identical to one another;
- compatibility with Loop 20's batched v1 arithmetic is declared and tested at
  absolute tolerance `1e-6`;
- frame indices and timestamps remain bitwise exact.

This separates transport invariance from cross-kernel floating-point
compatibility and makes both assertions testable.

## Registered Schedules

The fixed 48-item, 2,870-sample synthetic source represents 28.7 seconds at
100 Hz and yields 553 frames.

| Schedule | Pushes | Largest chunk | First token | Max schedule delay | Compute RTF | Result |
|---|---:|---:|---:|---:|---:|---|
| single-sample | 2,870 | 1 sample | 160 ms | 0 ms | 0.001444 | Pass |
| stride-aligned | 736 | 4 samples | 160 ms | 0 ms | 0.000346 | Pass |
| kernel-then-stride | 592 | 16 samples | 160 ms | 0 ms | 0.000355 | Pass |
| jittered | 406 | 15 samples | 160 ms | 140 ms | 0.000210 | Pass |
| whole-item | 48 | 77 samples | 420-770 ms | 610 ms | 0.000077 | Pass |

The whole-item row is an equivalence stress, not a recommended streaming
schedule. Its low compute RTF comes from efficient batching while its transport
delay is worst. This is exactly why throughput and latency must not be merged.

All five schedules have the canonical payload SHA-256:

```text
78dc8b5298064216caa854c884a69834c0959566d9ede903d44ae1cd28562389
```

An independent replay produced the same source hash, canonical stream hash,
maximum offline error, state bound, right context, schedule count, and pass
decision.

## Resource and Access Audit

```text
source cache:                         59,357 bytes
source signals loaded:                73,920 bytes
fixed mock weights:                   10,240 bytes
bounded working core arrays:          195,520 bytes
peak mutable state per stream:        300 bytes
state cap:                            1,024 bytes
total pushes:                         4,652
internal runtime:                     0.135024 sec
external wall time:                   0.22 sec
peak RSS:                             46,301,184 bytes
JSON / Markdown:                      12,734 / 1,792 bytes
free disk after run:                  about 15 GiB
```

All five numeric-thread environment variables were fixed at `1`. The selective
NPZ view opened only `metadata`, `signals`, `input_lengths`, and
`sentence_start_sec`. Target text/token/reference/response members were present
but never opened. Raw reads, real-cache reads, target-array reads, model runs,
training runs, decoder runs, network fetches, and new signal-cache writes were
all zero.

Primary report hashes:

```text
gate.json: d4b3e2df03300ea21844f39355e948503f92f00c94a787f37ed45e94b2c4ded2
gate.md:   6bf884ad489a2585b13fbf56213fa462b5f399a2b59709a4e96e1c32537d64c3
```

## Command

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
neurodecode causal-replay-gate \
  --source-cache cache/loop20_neurotoken/source_sentences.npz \
  --out-json cache/loop21_causal_replay/gate.json \
  --out-md cache/loop21_causal_replay/gate.md \
  --embedding-dim 32 --kernel-size 16 --stride 4 --seed 23 \
  --max-items 64 --max-source-mb 1 \
  --max-samples-per-item 128 --max-chunk-samples 128 \
  --max-tokens-per-item 128 --max-total-pushes 10000 \
  --max-working-mb 4 --max-state-kib 1 \
  --max-runtime-sec 5 --max-peak-rss-mb 128 --max-report-mb 1
```

## Acceptance Result

- all five registered chunk schedules: passed;
- canonical stream bits invariant across schedules: passed;
- Loop 20 batched-v1 compatibility within `1e-6`: passed;
- exact frame grid and timestamps: passed;
- every emission occurs after its frame end: passed;
- zero right context: passed;
- mutable state exactly bounded at 300 bytes: passed;
- drop-incomplete flush and use-after-close checks: passed;
- item/chunk/token/push/working/state/runtime/RSS/report caps: passed;
- target arrays unopened and no model/decoder/real-data access: passed;
- learned-representation, text-quality, text-emission, end-to-end-latency, or
  hardware claim: not made.

## Verification

```text
focused Loop 20/21 contracts: 12 tests passed
full unittest discovery: 199 tests passed, 3 skipped, 7.831 sec
full pytest: 196 passed, 3 skipped, 25 subtests passed, 7.77 sec
Ruff / compileall / root help / command help / diff check: passed
workbook formula-error scan / seven-sheet render: passed
workbook SHA-256: bd7ba4895e3afaf54b279ff240cf3377d49693dfdaeb11527c7ef7600874836c
```

Both full-suite runs pinned OpenBLAS, OpenMP, MKL, NumExpr, and Accelerate
thread counts to one. External maximum RSS was 475,774,976 bytes for unittest
and 501,366,784 bytes for pytest.

## Decision

Loop 21 is complete as a causal frame-producer contract. The next gate may
train a very small causal encoder on synthetic train rows only and require it
to emit this exact streaming interface under CPU, RAM, state, parameter, and
artifact caps. Decoder work remains blocked behind that learned-encoder gate;
real holdouts remain frozen.
