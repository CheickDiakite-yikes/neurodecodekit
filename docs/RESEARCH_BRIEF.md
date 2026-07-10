# Research Brief — Brain2Qwerty Accessibility Layer

This brief is a starting point for modern/future-oriented research. It was
refreshed against the official Brain2Qwerty code and v2 paper on 2026-07-10.
Re-check source pages before publishing because the review and dataset status
can still change.

## What changed recently

Meta released Brain2Qwerty v2 code and a preprint on 2026-06-30. The system
decodes continuous whole-sentence MEG recorded while participants type. It uses
a Conv+Conformer character CTC encoder, word-level neural/language alignment,
and a LoRA-adapted language model. The study reports about 22,000 sentences
from nine participants recorded for about 10 hours each.

Source: https://ai.meta.com/blog/brain2qwerty-brain-ai-human-communication/

Important wording correction: v2 is asynchronous, but the paper says the
released architecture is non-causal and consumes the complete sentence. It is
not yet low-latency word-by-word streaming, and it is not arbitrary thought
reading.

Source: https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

## What is public now

The public GitHub repo contains both v1 and v2 code. V1 SpanishBCBL data is on
Hugging Face. V2 EnglishBCBL data remains under embargo, so the reported v2
result cannot currently be reproduced from public data alone.

Source: https://github.com/facebookresearch/brain2qwerty

The full v2 configuration is not a local-laptop baseline: the paper reports
8 A100 80 GB GPUs and about 19.5 hours for the staged end-to-end run. Its sensor
ablation randomly retained 230, 153, or 76 of 306 mixed MEG channels, retrained
the full pipeline for four sensor-selection seeds, and reported WER 0.467,
0.490, and 0.547 versus 0.433 for the full array. This supports low-channel
research, not a claim that magnetometer-only caches, OPM systems, or arbitrary
subsets reproduce v2 accuracy.

Source: https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

## v1 data reality

The SpanishBCBL Hugging Face dataset is the practical starting point. The dataset card says it contains non-invasive MEG/EEG recordings from healthy adults typing briefly memorized Spanish sentences on a QWERTY keyboard. It lists:

- 35 healthy adult volunteers
- Spanish sentences
- MEG: about 5.1K sentences / 193K characters
- EEG: about 4K sentences / 146K characters
- MEG recordings as `.fif`
- EEG recordings as BrainVision `.vhdr/.eeg/.vmrk`
- behavioral logs as `.mat`
- total size around 262GB
- CC BY-NC 4.0 license

Source: https://huggingface.co/datasets/bcbl190626/SpanishBCBL

## v1 model reality

The Nature Neuroscience paper reports average 29% character error rate with MEG, 65% character error rate with EEG, and 18% CER for the best participants. The model uses 0.5-second windows around keystrokes in the v1 setup, so v1 is not the same as unrestricted thought decoding or fully asynchronous language decoding.

Source: https://www.nature.com/articles/s41593-026-02303-2

## The accessibility gap

The practical bottleneck is not just model sophistication. It is:

```text
large raw files
+ specialized neuroimaging formats
+ event alignment
+ preprocessing choices
+ subject-specific data
+ unclear baselines
+ noncommercial licensing
```

The project opportunity is to make the first research loop small and reproducible.

## Current local direction

The validated public-data bridge is now:

```text
one full SpanishBCBL block
-> continuous ENTER-delimited sentence windows
-> padded signals + input lengths + typed target lengths
-> tiny optional CTC smoke model
-> CER and no-brain comparator
```

This borrows v2's asynchronous CTC interface while staying honest about the
smaller Spanish dataset, unavailable EnglishBCBL data, and missing cluster
hardware. The original 16-channel file-order cache remains a smoke artifact;
Loop 11 now adds a 102-magnetometer geometry-aware base for sensor-subset
research. A later real-time path will also require a causal model and hardware
research beyond the current cryogenic MEG setup.

Loop 9 now proves that bridge locally: a 1,372-parameter optional CTC model
trains in about one second on synthetic variable-length signals, while one
validated 66-sentence S21 cache extracts in 6.24 seconds with about 515 MiB peak
RSS and a 1.6 MB output. Those are interface/resource results, not real decoding
accuracy.

Loop 10 measures the first compute-accessibility tradeoff on that same source.
The 50 and 25 Hz caches use 50.9% and 25.9% of the 100 Hz bytes, and all 66
targets remain valid for the stride-one CTC contract. The lower rates do not
materially reduce fresh extraction time or memory because fixed MNE import,
raw-I/O, and filtering overhead dominate. More importantly, they cap effective
bandwidth at 25 and 12.5 Hz and coarsen the sample grid to 20 and 40 ms. This is
compression evidence, not retained-accuracy evidence. See
`docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

The pinned v2 implementation adds a sharper architecture boundary: its
no-padding kernel-16, stride-4 temporal reducer remains CTC-length feasible for
all 66 local rows at 100 and 50 Hz, but for none at 25 Hz. A 25 Hz local model
must reduce temporal stride, lengthen segments, or change the target contract;
it cannot be a parameter-only port of the official encoder.

Loop 16 now establishes an adapter-scope boundary before another real-data
attempt. An independent unlabeled synthetic calibration pool is swept at
1/2/4/8/16/32 sentences over three shift seeds. Static robust channel-affine
normalization helps the stationary diagonal family, but it harms every frozen
channel-mixing and within-row time-varying seed. This agrees with the broader
domain-adaptation distinction between independent first-order scaling and
covariance-aware alignment, and with MEG work treating non-stationarity as a
time-dependent problem. The next adapter research should therefore compare a
regularized covariance map and causal rolling statistics on synthetic
validation, not reopen the consumed real session.

Sources:

- https://doi.org/10.1609/aaai.v30i1.10306
- https://doi.org/10.1109/TBME.2019.2913914
- https://doi.org/10.1186/1687-6180-2012-129
- https://arxiv.org/abs/2012.03533

Loop 11 measures the next hardware/compute proxy without inventing a model
score. One 66 x 102 x 617 S21 magnetometer cache extracts in 12.0 seconds with
about 1.56 GiB peak RSS and a 10.1 MiB output. A cache-only sweep writes 20
nested 76/51/25/16/8-channel variants for spatial farthest-point sampling,
same-block variance, seed-17 random, and file-order controls in 70.3 MiB.

The result is deliberately two-sided. Spatial FPS has the lowest whole-array
coverage distance at every count; variance ranking has the highest
post-scaling marginal variance share. At 16 channels the FPS and variance sets
overlap on only 2 sensors. They are therefore two candidates for a future
held-out decoder experiment, not a basis for selecting a count today. Device
coordinates are not cortical ROIs, variance must be fit on training data only,
and 102 cryogenic magnetometers are not an OPM helmet. See
`docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.

Loop 12 isolates numeric storage from decoder precision. Five representations
were written for the fixed 102-mag base, FPS-16, and variance-16 caches. All 15
artifacts preserve exact target/text/timing/channel arrays, semantic metadata,
shapes, and zero padding. No source value exceeded the fixed preprocessing
range. Qint16 reduces aggregate compressed cache bytes by 49.84% versus the
float32 representation with at most 0.003693% relative RMSE; qint8 reduces
bytes by 80.75% with at most 0.9531% relative RMSE and 1.0872% aggregate
bandpower error. These are storage/fidelity candidates, not retained-accuracy
results. Every packed cache currently decodes to float32 before model input,
so model weights, activation precision, causal latency, and sensor access are
unchanged. See `docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.

The official v2 paper's BF16 result concerns mixed-precision model training on
eight A100 GPUs. It does not define the physical MEG cache format. Keeping that
distinction explicit prevents a GPU training optimization from being presented
as evidence for a local input representation.

Loop 13 tests whether another local cache backend is needed now. Across nine
real standard/packed caches, the slowest full-load median is 60.386 ms, the
slowest partial median is 53.634 ms, the highest worker peak RSS is 140.6 MiB,
and all decoded-signal hashes match exactly. One-row NPZ access is inefficient
because it materializes the complete compressed member, but current absolute
cost remains below the declared budgets. Zarr was researched but not installed
or benchmarked. Keep per-block NPZ and revisit chunked storage only at a
recorded threshold or repeated-subarray workflow. See
`docs/LOOP_13_LAZY_BACKEND_GATE.md`.

Loop 14 makes the evaluation boundary machine-readable and resolves the first
fit-scope failure. The pinned official-exact splitter assigns the 66 unique S21
references to 55/6/5 train/validation/test rows with zero group crossings. A
replacement cache fits robust statistics on valid train-row samples only and
binds preprocessing plus training to the exact cache/protocol/membership
hashes. Its strict audit passes.

The first fixed model comparison is useful precisely because it is negative.
On five test sentences, prior-only CER is 0.953488 and tiny-CTC CER is 0.947674,
just one character edit apart. The tiny model's train CER is 0.925469 and its
test output is 86.8% blank. A paired sentence-bootstrap interval for the CER
delta spans -0.197279 to +0.130653. This is not evidence that neural signal
beats the prior. It says the protocol works and the 2,908-parameter baseline is
not learning enough from one session. See `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

Loop 15 adds the first real same-subject independent-session check without
changing that model after observing the holdout. The complete S21 session-2
recording has 63 performed trials and three explicit empty MAT slots. Its
102-magnetometer cache is transformed only with frozen session-1 train
statistics. Source validation/test rows remain unused, and both typed targets
and reference prompts have zero exact overlap between source train and session
2.

The result is more decisively negative than the five-row sentence test: tiny
CTC corpus CER is 0.917949 versus 0.775458 for the no-signal prior. The paired
tiny-minus-prior interval is +0.119386 to +0.166069, with 3/2/58 sentence
wins/ties/losses. This validates the local session protocol and exposes a model
failure. It does not validate an adapter, unseen-person transfer, or useful
brain-to-text performance. See
`docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## Accessibility is four separate problems

1. Developer access: safe selection, small caches, tests, and report artifacts.
2. Local compute: sampling, sensors, precision, causal inference, and latency.
3. Portable sensing: EEG is available in SpanishBCBL but the published v1
   average CER is about 65%, versus 29% for MEG.
4. Wearable MEG: OPMs can operate near room temperature and move with the head,
   but environmental magnetic interference and shielding remain core barriers.

Useful primary sources for the hardware branch:

- https://www.nist.gov/publications/new-generation-magnetoencephalography-room-temperature-measurements-using-optically
- https://pubmed.ncbi.nlm.nih.gov/39302788/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10465235/

This makes the near-term roadmap concrete: the optional lazy backend is parked,
deterministic sentence-text membership and train-only scaling are validated,
and a bounded second session now exposes failed transfer. Loop 19 separately
validates the first native SpanishBCBL EEG bridge without installing MOABB. One
94,842,381-byte S7 BrainVision-plus-MAT bundle yields 2,197 aligned key windows
after all 2,534 MAT trigger codes match the raw annotations. The trigger bridge
is sound for that file, but the minimally processed nearest-centroid result is
negative: 0.91% exact key-label accuracy versus 12.27% for a train-only prior.
This is not an EEG decoding-quality or hardware-portability result.

Loop 20 now defines that modality-aware interface as continuous
`[items,time,embedding]` vectors with masks, timestamps, source identity,
timebase, geometry availability, strict split hashes, and explicit causality
and resource metadata. Its only producer is a deterministic target-free
synthetic projection; the exact payload replays, but no learned representation
or decoding value is established. The next gate is causal chunk/replay behavior
on synthetic streams, including state, right context, flush semantics, and
offline-versus-streaming equivalence. Causal MEG/EEG preprocessing, learned
encoders, and adapter research remain separate future gates. Treat OPM-MEG as
a hardware research partnership rather than a consumer-product assumption.

## Loop 21 causal streaming decision

The first post-roadmap gate now distinguishes five layers that are often
collapsed in “real-time” claims:

1. **Frame causality:** a token depends only on samples through its frame end.
2. **Right context:** additional future samples explicitly required by the
   producer; Loop 21 uses zero.
3. **Transport scheduling:** when a complete frame is actually delivered to
   the producer; fixed chunks can add delay even with a causal model.
4. **Decoder emission:** when a stable character/word hypothesis appears; not
   measured because no decoder ran.
5. **End-to-end latency:** capture through UI, including preprocessing,
   scheduling, model, decoding, endpointing, and rendering; not measured.

On 28.7 seconds of synthetic signals, five chunk schedules emit the same 553
canonical frames bitwise with exact timestamps and at most 300 bytes of mutable
state. Aligned chunks add zero scheduling delay, jittered chunks up to 140 ms,
and whole-item delivery up to 610 ms. The public Brain2Qwerty v2 model remains
noncausal whole-sentence, while Emformer and FastEmit respectively motivate
bounded/right-context encoder contracts and separate symbol-emission metrics.
Those speech results structure the audit; they do not prove brain-decoding
quality.

The next legitimate step is a tiny learned causal encoder on synthetic
train/validation/test partitions, not direct deployment of the v2 architecture
or a real-time label. See `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md` and
`docs/POST_20_ROADMAP.md`.

## Loop 19 EEG ecosystem decision

MOABB remains useful for standardized EEG benchmark paradigms, but its stock
motor-imagery/P300/SSVEP-style tasks do not preserve the typed sentence
production contract needed here. Its stable install documentation also does
not list this Python 3.13 environment. The Loop 19 bridge therefore uses the
already installed MNE BrainVision reader with `preload=False`, the official
Brain2Qwerty loader's filename/channel rules, and the existing NeuroDecodeKit
cache/report contracts. This avoids claiming that success on an unrelated EEG
paradigm transfers to brain-to-text.

## Future-facing bet

The durable abstraction may be:

```text
raw neural stream → calibrated neurotokens → text/action model
```

For now, “neurotokens” are a research interface, not a solved standard. Loop
20's v0 artifact stores continuous frame embeddings rather than discrete
codes, and its synthetic mock producer is deliberately not learned.

## Useful ecosystem

- MNE-Python / MNE-BIDS for MEG/EEG loading and BIDS-compatible workflows: https://mne.tools/mne-bids/stable/index.html
- Braindecode for PyTorch-based EEG/ECoG/MEG deep-learning baselines: https://braindecode.org/
- Hugging Face Hub helpers for listing/selective download: https://huggingface.co/docs/huggingface_hub/
- Hugging Face streaming docs are useful conceptually, though SpanishBCBL does not expose a normal dataset viewer because the files are raw neuroimaging formats: https://huggingface.co/docs/datasets/en/stream
- Zarr for chunked, compressed N-dimensional arrays: https://zarr.dev/

## High-signal research loops

### 1. Accessibility/compression loop

Question: how small can the dataset slice/cache become while preserving meaningful decoding signal?

Metrics:

- bytes downloaded
- bytes cached
- seconds to first batch
- CER/WER
- accuracy retained per GB

### 2. Baseline honesty loop

Question: how much performance comes from neural signal vs language prior?

Required baselines:

- random character baseline
- frequency baseline
- keyboard-neighbor baseline
- language-model-only baseline
- neural-only tiny classifier
- neural + simple language cleanup

### 3. Subject adaptation loop

Question: how many minutes of data are needed for a new subject?

Metrics:

- CER/WER vs calibration minutes
- train-on-A, adapt-to-B performance
- adapter-only fine-tuning performance

### 4. Hardware realism loop

Question: can the workflow generalize beyond lab MEG?

Treat this as research only. Do not imply consumer-readiness.

Measure three branches separately:

- cryogenic MEG algorithm compression
- public EEG transfer and calibration cost
- OPM-MEG shielding, channel geometry, and motion robustness
