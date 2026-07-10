# Loop 22 Preregistration - Tiny Learned Causal Encoder

Preregistered on 2026-07-10 before creating or opening the dedicated Loop 22
synthetic test partition.

## Proof Posture

This is a synthetic causal-representation mechanism gate. It may establish
that one very small supervised encoder learns an intentionally simple motif
task and replays the same embeddings across transport chunks. It cannot
establish MEG/EEG decoding quality, text production, user-perceived latency,
sensor portability, unseen-person transfer, arbitrary-thought decoding, or a
clinical result.

No CTC loss, prefix decoder, beam search, language model, real neural cache,
raw recording, observed S21 holdout, S7 EEG result, or network service may be
opened by the gate.

## Research Basis

The public Brain2Qwerty v2 code remains pinned at commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0` as of 2026-07-10. Its encoder uses
a large convolutional front end, kernel-16/stride-4 temporal downsampling, and
a four-layer Conformer. The paper explicitly says the current architecture is
noncausal and works on complete sentences; fully low-latency operation remains
future work. It also describes deterministic train/validation/test membership,
validation checkpoint selection, and test access only after tuning.

Loop 22 preserves only the useful local contract: shared temporal weights,
`16/4` frames, explicit finite history, a validation-selected checkpoint, and
a frozen test. It does not claim architectural or performance equivalence to
the public model.

Primary sources:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Brain2Qwerty v2 model configuration:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py
- Generic causal temporal convolution baseline:
  https://openreview.net/forum?id=rk8wKk-R-
- Emformer bounded-memory streaming reference:
  https://ai.meta.com/research/publications/emformer-efficient-memory-transformer-based-acoustic-model-for-low-latency-streaming-speech-recognition/
- PyTorch reproducibility note:
  https://docs.pytorch.org/docs/2.13/notes/randomness.html
- PyTorch CPU thread control:
  https://docs.pytorch.org/docs/2.13/generated/torch.set_num_threads.html

## Fixture Contract

The fixture command will create three independent NPZ files plus one manifest.
The files use schema `b2q-causal-motif-fixture` version `0`; no text or real
neural array is stored.

| Field | Registered value |
|---|---:|
| Train / validation / test items | 64 / 8 / 8 |
| Sampling rate | 100 Hz |
| Signal channels | 5 |
| Motif classes | 5 plus background |
| Motifs per item | 5-8 |
| Motif / gap / lead / tail width | 8 / 4 / 16 / 4 samples |
| Motif / adjacent-channel amplitude | 1.5 / 0.25 |
| Noise standard deviation | 0.10 |
| Per-item gain range | 0.85-1.15 |
| Per-item offset standard deviation | 0.03 |
| Kernel / stride | 16 / 4 samples |
| Train / validation / test seeds | 2201 / 2202 / 2203 |

Each item includes every motif class at least once. Frame labels describe the
synthetic state at the final sample of each complete causal frame. Padded
labels use `-1`; padding is excluded from every fit and metric.

Partition names are encoded in item IDs and metadata. The manifest must bind
each path, SHA-256, byte count, schema, generation seed, shape, class count,
and frame count. Item IDs must be disjoint. Total fixture bytes must remain at
or below 1 MiB.

## Access Sequence

The training gate must record these semantic-access events in order:

1. validate the compact fixture manifest;
2. open the train partition once;
3. open the validation partition once;
4. fit normalization and model parameters from train only;
5. choose the checkpoint from validation metrics and freeze its config/hash;
6. open the test partition exactly once only if the validation gate passes;
7. evaluate the frozen checkpoint and comparators once, without further fit.

If validation fails, the test partition must remain unopened and the decision
is `park`. Test metrics may never select an epoch, architecture, threshold,
normalizer, seed, or retry.

## Registered Model

One model and one initialization are allowed:

```text
causal frame [5 x 16]
  -> flatten [80]
  -> Linear(80, 12) + GELU
  -> Linear(12, 8) + GELU
  -> continuous embedding [8]
  -> training/evaluation-only Linear(8, 6) motif probe
```

The shared-window MLP is equivalent to a small temporal convolution evaluated
on complete causal frames. It has 1,130 trainable parameters: 1,076 in the
encoder and 54 in the motif probe. The probe is not a CTC or text decoder.

Fixed per-channel mean and standard deviation are fit on valid train samples
only. Inference normalizes each complete frame with those frozen values. The
only mutable array state is the raw overlap buffer: at most
`5 x (16 - 1) x 4 = 300` bytes. Python object overhead and the fixed model are
reported separately from this buffer payload.

## Registered Training

- framework: optional PyTorch, CPU only;
- model seed: `2221`;
- optimizer: Adam;
- learning rate: `0.01`;
- weight decay: `0.0001`;
- batch size: `64` frames;
- maximum epochs: `60`;
- early-stopping patience: `8` epochs;
- loss: train-frequency-weighted frame cross entropy;
- deterministic algorithms: required;
- Torch intra-op / inter-op threads: `1 / 1`;
- architecture candidates: `1`;
- initialization restarts: `0`.

The selected epoch maximizes validation balanced accuracy, then minimizes
validation loss, then chooses the earliest epoch. No training row may enter a
validation metric, and no validation or test row may fit normalization, class
weights, optimizer state, or model parameters.

## Comparators And Metrics

The primary metric is frame balanced accuracy, which prevents the background
class from dominating the result. Secondary metrics are frame accuracy,
macro-F1, per-class recall, confusion matrix, and per-item accuracy.

Two signal-free controls are mandatory:

- most-frequent frame label fit on train labels only;
- the frozen learned model evaluated on train-mean input, which becomes zero
  after the registered normalization.

Validation opens the test gate only when both conditions pass:

```text
balanced_accuracy >= 0.70
balanced_accuracy - prior_balanced_accuracy >= 0.35
accuracy - prior_accuracy >= 0.20
```

The frozen test proceeds to Loop 23 only when all conditions pass:

```text
balanced_accuracy - max(prior, zero-signal) balanced_accuracy >= 0.35
accuracy - max(prior, zero-signal) accuracy >= 0.20
95% paired bootstrap lower bound for per-item accuracy gain over prior > 0
```

The paired bootstrap uses 2,000 item resamples and seed `2222`. A failed test
parks the learned branch; it does not authorize another seed, wider model, or
test rerun.

## Streaming Acceptance

After checkpoint selection, continuous embeddings must be replayed under the
same five schedules registered in Loop 21:

- single-sample;
- stride-aligned;
- kernel-then-stride;
- jittered;
- whole-item.

Acceptance requires bitwise-identical embeddings, frame indices, timestamps,
and drop-incomplete tails across schedules. Every emission must occur at or
after its frame end; right context must remain zero. Batched Torch output may
differ from canonical one-frame inference by at most `1e-6`, but all streaming
schedules use the same one-frame arithmetic and must match bitwise.

## Resource Caps

| Resource | Hard cap |
|---|---:|
| Total fixture bytes | 1 MiB |
| Items / samples per item / total frames | 80 / 128 / 2,048 |
| Trainable parameters | 2,048 |
| Float32 parameter bytes | 16 KiB |
| Checkpoint bytes | 64 KiB |
| Per-stream mutable array state | 1 KiB |
| Working arrays before framework overhead | 16 MiB |
| Total gate runtime | 30 sec |
| Process peak RSS | 768 MiB |
| Total report/checkpoint artifacts | 1 MiB |
| CPU numerical threads | 1 |

The report must distinguish fixture bytes, NumPy working arrays, Torch runtime
RSS, trainable parameters, fixed normalization values, overlap-buffer payload,
checkpoint bytes, report bytes, training time, canonical inference RTF, and
transport delay.

## Decision Rule

`proceed` means only that the tiny synthetic encoder gate passed and Loop 23
may test an incremental CTC prefix decoder on a newly preregistered synthetic
protocol. `park` means preserve the negative result and do not enlarge the
model against the same test partition.

In either outcome, real MEG/EEG evaluation remains forbidden until the later
causal preprocessing and validation-only real-data gates.
