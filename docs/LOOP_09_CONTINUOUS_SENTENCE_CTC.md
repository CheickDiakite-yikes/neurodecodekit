# Loop 9 - Continuous Sentence Cache and Tiny CTC

Date: 2026-07-10 local

## Outcome

Loop 9 is complete.

NeuroDecodeKit now has a distinct variable-length sentence cache, a real
first-key-through-ENTER extraction path, and an optional CPU-safe character CTC
baseline. The synthetic model learns sequence alignment without keypress times.
The validated S21 block produces a real sentence cache with the same interface.

This does not establish real neural decoding performance. No model was trained
or evaluated on the single real block because a one-block same-session split
would be weak evidence and easy to overstate.

## Why a Separate Cache

The existing `b2q-mini-cache` stores independent event windows:

```text
windows [events, channels, timepoints]
labels  [events]
```

CTC needs variable-length continuous signals and variable-length text targets.
Reusing the event schema would make the time axis and label semantics
ambiguous, so Loop 9 adds `b2q-sentence-cache` schema v0:

```text
signals                [sentences, channels, padded_timepoints] float32
input_lengths          [sentences] int32
target_token_ids       [sentences, padded_target_length] int16
target_lengths         [sentences] int32
target_texts            raw trigger-derived typed text
reference_texts         prompted MAT sentence
mat_response_texts      MAT-recorded typed response
trial_indices           validated MAT/FIF trial index
sentence_start_sec      extraction start relative to raw recording
sentence_end_sec        extraction stop relative to raw recording
channel_names           selected channel names
metadata                schema, sources, transforms, warnings, and parameters
```

The loader rejects:

- invalid schema names or versions
- non-finite signals or timing
- nonzero signal/target padding
- duplicate trial IDs or channel names
- target IDs containing CTC blank zero
- target text/token disagreements
- signals too short for repeated-character CTC alignment

## Target Semantics

The official v2 code trains its CTC head on what the participant typed. The
local cache follows that contract:

- `target_texts` comes from raw `STI101` letter/space triggers and excludes
  ENTER.
- `reference_texts` preserves the prompted MAT sentence for linguistic error
  analysis.
- `mat_response_texts` preserves the behavioral log's reconstructed response.

These fields are not interchangeable. Replacing raw typed labels with prompts
would hide typing errors and turn the target into a less direct behavioral
measurement.

The local vocabulary has 28 classes:

```text
0      CTC blank
1..26  A..Z
27     space
```

Unsupported characters fail explicitly instead of being silently removed.

## Official v2 Contract Audit

Audited release: `facebookresearch/brain2qwerty` commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0`.

The local interface mirrors these released v2 choices:

- one continuous sentence signal per row
- padded `(batch, time, channels)`-equivalent batches with true signal lengths
- padded integer targets with true target lengths
- CTC blank ID zero
- character vocabulary plus space
- greedy repeat collapse and blank removal
- prompt text kept separately from typed labels
- deterministic text-level split to prevent duplicate sentence leakage

It does not copy the cluster-scale architecture. The official encoder uses a
large convolutional front end, temporal downsampling, a four-layer Conformer,
word-level contrastive alignment, and a LoRA language model. The local model is
a 1,372-parameter stride-one ConvNet used only to prove the interface.

Primary sources:

- https://github.com/facebookresearch/brain2qwerty
- https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- https://facebookresearch.github.io/brain2qwerty/

## Preprocessing

The real extractor follows the published v2 preprocessing order within the
limits of one local block:

```text
open without preload
-> read STI101 key triggers
-> validate 66 trial rows against MAT
-> pick and cap channels before loading samples
-> 50 Hz notch at 2048 Hz
-> 0.5-45 Hz bandpass at 2048 Hz
-> downsample to 100 Hz
-> per-channel median/IQR scaling
-> clamp to +/-5 robust units
-> slice -0.4 sec before first key through +0.45 sec after ENTER
-> zero-pad signals and targets while retaining true lengths
```

All MNE processing uses one job. The post-context is fixed at 0.45 seconds for
reproducibility; the official training pipeline samples 0.4-0.5 seconds.

## Synthetic Proof

Command:

```bash
neurodecode make-synthetic-sentence-cache \
  --out cache/loop9_synthetic_sentences.npz \
  --sentences 96 \
  --channels 6 \
  --letter-classes 4 \
  --seed 17

neurodecode tiny-ctc-baseline \
  --cache cache/loop9_synthetic_sentences.npz \
  --train-fraction 0.8 \
  --seed 17 \
  --epochs 60 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --hidden-channels 16 \
  --device cpu \
  --num-threads 1 \
  --max-restarts 3 \
  --out-predictions cache/loop9_synthetic_ctc_predictions.txt \
  --out-json cache/loop9_synthetic_ctc_report.json \
  --out-md cache/loop9_synthetic_ctc_report.md
```

Observed cache:

```text
shape:                 (96, 6, 78)
input lengths:         41..78
target lengths:        5..9
padding fraction:      0.2333
file bytes:            136,734
```

Observed model/report:

```text
parameters:            1,372
float32 parameter bytes: 5,488
train rows:            77
eval rows:             19
initial loss:          19.91679843
final loss:            0.00060536
eval blank fraction:   0.41784452
eval corpus CER:       0.0
eval corpus WER:       0.0
no-brain prior CER:    0.70676692
training runtime:      0.969894 sec
external wall time:    1.79 sec
external max RSS:      314,671,104 bytes (about 300 MiB)
```

The synthetic pulses are intentionally easy. Zero CER proves CTC batching,
loss, decoding, splitting, and reporting, not brain-to-text capability.

### Blank-collapse regression

A first 20-seed sweep found one all-blank collapse. A fixed output bias and
short warmup schedules both made other seeds worse, so they were rejected.

The implemented safeguard allows at most three deterministic initializations.
It retries only when training CER remains above 0.05 and selects a candidate by
training CER/final loss. Evaluation predictions are computed only after that
selection, so the restart does not tune on the evaluation set.

Final 20-seed sweep:

```text
runs:                   20
max eval CER:           0.0
mean eval CER:          0.0
runs needing restart:   1 (seed 4; selected initialization seed 1013)
failures above 0.25:    0
```

## Real S21 Cache Proof

Command:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/b2qsentence_s21_session1_block1_16ch_100hz.npz \
  --sfreq 100 \
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

Observed result:

```text
sentences:              66
trial indices:          exactly 0..65
shape:                  (66, 16, 617)
valid input lengths:    329..617 at 100 Hz
target lengths:         22..44 characters
valid timepoints:       28,397
padding fraction:       0.302662
signal absolute max:    5.0
all padding zero:       True
target token roundtrip: True
file bytes:             1,663,209
runtime:                6.243 sec
external max RSS:       539,951,104 bytes (about 515 MiB)
```

Behavioral consistency remains visible:

```text
typed vs prompted text:     43/66 exact, corpus CER 0.02372093
typed vs MAT response text: 61/66 exact, corpus CER 0.00233427
```

No real CTC score is reported. The block is a schema and preprocessing proof.

## Optional Dependency Cost

PyTorch remains behind `.[ml]`. On this Apple Silicon environment, installing
Torch 2.13 used a 111.2 MB wheel with no retained pip cache. The complete venv
grew from about 304 MB to about 942 MB. The base package still imports without
Torch, and missing-dependency tests remain present for lightweight installs.

## Accessibility Research Ladder

The next work should separate four meanings of "accessible":

1. **Developer accessible:** selective downloads, small caches, one-command
   reports, and CPU-safe smoke models. This loop materially advances that goal.
2. **Compute accessible:** sampling-rate, channel-count, precision, causal
   architecture, and latency sweeps on local hardware.
3. **Sensor accessible:** EEG is cheaper and portable, but the published v1
   result reports about 65% average CER for EEG versus 29% for MEG. It is an
   important research branch, not a drop-in replacement.
4. **Wearable MEG accessible:** OPM-MEG sensors operate near room temperature
   and can be head-mounted, but current systems remain highly sensitive to
   environmental fields and depend on passive/active magnetic shielding.

Primary accessibility sources:

- Brain2Qwerty v1 MEG/EEG comparison:
  https://www.nature.com/articles/s41593-026-02303-2
- Room-temperature OPM-MEG demonstration:
  https://www.nist.gov/publications/new-generation-magnetoencephalography-room-temperature-measurements-using-optically
- Wearable MEG in a lightly shielded environment:
  https://pubmed.ncbi.nlm.nih.gov/39302788/
- Active shielding for ambulatory OPM-MEG:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10465235/

An at-home claim is not supported today. The credible path is to measure each
reduction in compute and sensing burden while preserving an explicit accuracy
and noise cost.

## Files Added

```text
src/neurodecodekit/preprocess/ctc_text.py
src/neurodecodekit/cache/sentence_npz.py
src/neurodecodekit/preprocess/sentence_extraction.py
src/neurodecodekit/training/synthetic_sentences.py
src/neurodecodekit/models/tiny_ctc.py
tests/test_ctc_text.py
tests/test_sentence_npz.py
tests/test_sentence_extraction.py
tests/test_synthetic_sentences.py
tests/test_tiny_ctc.py
tests/test_cli_sentence_cache.py
```

## Next Gate

Loop 10 is the sampling-rate sweep. It should first compare the same real S21
sentence extraction at 100, 50, and 25 Hz for bytes, runtime, input/target CTC
feasibility, and signal summaries. A real model comparison should wait for a
second correctly paired block or session so evaluation is not a single-block
holdout dressed up as generalization.

Update: that resource gate is now complete. See
`docs/LOOP_10_SAMPLING_RATE_SWEEP.md`; no rate winner was selected.
