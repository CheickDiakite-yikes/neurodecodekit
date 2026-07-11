# Loop 23 Preregistration - Streaming CTC Prefix Decoder

Preregistered on 2026-07-10 before creating any Loop 23 fixture, target array,
decoder implementation, or test partition.

## Proof Posture

This is a synthetic incremental-decoder mechanism gate. It may establish that
one fixed causal encoder/probe can feed a language-model-free CTC greedy and
prefix decoder with correct blank/repeat state, bounded memory, chunk-invariant
partial hypotheses, and explicit emission/stability measurements.

It cannot establish MEG/EEG decoding quality, natural text generation,
language understanding, live endpointing, user-perceived latency, portable
hardware, unseen-person transfer, arbitrary-thought decoding, or a clinical
result.

No new model architecture, parameter update, CTC training loss, language
model, real neural cache, raw recording, observed S21 holdout, S7 EEG result,
or network service may be used by this gate.

## Research Basis

The original CTC formulation adds one blank class, sums over frame paths that
collapse to a label sequence, and distinguishes best-path decoding from prefix
search. Blank-separated repeated labels must remain distinct: collapsing
`A blank A` yields `AA`, while collapsing `A A` yields `A`. Prefix search must
therefore track separate probabilities for paths ending in blank and
nonblank.

Incremental-ASR research also makes clear that final error rate is incomplete.
Partial hypotheses can be revised; stability and timeliness trade off. Loop 23
will report edit overhead, first-correct time, stable-correct time, correction
delay, and finalization separately. Stable-correct time is a retrospective
metric, not an online commitment policy.

Primary sources:

- Original CTC paper:
  https://www.cs.toronto.edu/~graves/icml_2006.pdf
- Incremental correctness, edit overhead, correction time, and stability:
  https://aclanthology.org/N09-1043/
- Streaming partial-hypothesis quality and stability:
  https://research.google/pubs/analyzing-the-quality-and-stability-of-a-streaming-end-to-end-on-device-speech-recognizer/
- Emission-latency/accuracy tradeoff:
  https://research.google/pubs/fastemit-low-latency-streaming-asr-with-sequence-level-emission-regularization/
- Brain2Qwerty v2 architecture and real-time limitation:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

Loop 23 uses these definitions for measurement only. It does not claim speech
recognition equivalence or adopt transducer-specific training methods.

## Frozen Upstream Input

The only learned source is the consumed and frozen Loop 22 checkpoint:

```text
path: cache/loop22_tiny_causal_encoder/checkpoint.npz
file SHA-256: 75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
parameter payload SHA-256: d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
config SHA-256: 8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2
selected epoch: 34
parameters: 1,130
encoder right context: 0 samples
```

The checkpoint is loaded without modification. Class `0` from its diagnostic
motif probe becomes the CTC blank. Classes `1-5` map to synthetic symbols
`A-E`. The probe was trained with frame cross entropy, not CTC loss. Any pass
therefore proves decoder mechanics on peaked synthetic frame logits, not a
CTC-trained neural representation.

The Loop 22 seed-2203 test is consumed and forbidden. Its signals, targets,
metrics, and partial outputs may not select or validate Loop 23 behavior.

## Fresh Fixture Contract

After this preregistration is committed, one command may create three new
physical NPZ partitions plus one manifest using schema
`b2q-ctc-symbol-stream-fixture` version `0`.

| Field | Registered value |
|---|---:|
| Train / validation / test items | 48 / 8 / 8 |
| Train / validation / test seeds | 2301 / 2302 / 2303 |
| Sampling rate | 100 Hz |
| Signal channels | 5 |
| Symbols | `A-E`, IDs `1-5` |
| CTC blank | ID `0` |
| Target length | 6-8 symbols |
| Motif / gap / lead / tail | 8 / 4 / 16 / 8 samples |
| Motif / adjacent-channel amplitude | 1.5 / 0.25 |
| Noise standard deviation | 0.10 |
| Per-item gain range | 0.85-1.15 |
| Per-item offset standard deviation | 0.03 |
| Encoder kernel / stride | 16 / 4 samples |
| Maximum samples / frames per item | 116 / 26 |

Each target contains all five symbols at least once and at least one adjacent
repeated-symbol pair. Generation shuffles one copy of `A-E`, duplicates one
selected symbol immediately beside itself, then inserts zero to two additional
symbols without splitting the guaranteed pair. The signal contains one motif
per target symbol with a four-sample background gap; this gap is necessary for
CTC to preserve adjacent repeated symbols.

Each partition stores signals, valid sample/frame lengths, frame labels,
target token IDs and lengths, item IDs, motif boundaries, and metadata. Padding
is exactly zero for signals and `-1` for labels/targets. No natural-language
text is stored.

The manifest binds path, schema, byte count, SHA-256, seed, item IDs, shape,
frame count, target count, repeated-pair count, and protocol hash. Item IDs are
disjoint. Complete fixture bytes must remain at or below 1 MiB.

## Access Sequence

The gate must record these semantic events in order:

1. validate the compact Loop 23 manifest without opening partition arrays;
2. validate and load the exact frozen Loop 22 checkpoint;
3. open only train target/item members once, never train signals;
4. fit the signal-free prior from train targets only;
5. open validation arrays once and run the fixed encoder/decoders/controls;
6. apply the registered validation rule and freeze the decoder config/hash;
7. open the fresh seed-2303 test exactly once only if validation passes;
8. run one canonical frozen test evaluation and both controls without fitting;
9. write reports without reopening any partition.

Streaming schedule equivalence is proven on validation before test access. The
test is not replayed under multiple schedules. If validation fails, test stays
unopened and the decision is `park`.

## Registered Decoders

### Greedy CTC comparator

At each frame, select the maximum-logit class with lowest-ID tie breaking.
Maintain the previous path class. Emit a nonblank symbol only when it differs
from the previous path class; blank resets the repeat state. This must be
bitwise and textually equivalent to offline argmax-then-CTC-collapse.

### Prefix beam primary

- beam width: `8`;
- alphabet: blank plus `A-E`;
- input: float64 log-softmax of frozen probe logits;
- state per prefix: separate log probabilities ending blank/nonblank;
- score: log-add-exp of blank and nonblank paths;
- pruning: top eight prefixes after every frame, no score threshold;
- language-model score / insertion bonus: absent / `0`;
- maximum prefix length: `12`;
- ties: descending score, then lexicographic token tuple;
- updates: exactly one frame at a time even when transport yields a batch;
- flush: finalize the current top prefix without adding a frame or symbol.

The implementation must handle repeated labels using the standard CTC rule:
extending a prefix with its final symbol is allowed from blank-ending paths;
nonblank repeats that do not cross blank remain in the same collapsed prefix.

Unit tests must include hand-built blank/repeat paths and exhaustive path
enumeration on tiny alphabets/sequences. A wide-beam prefix result must equal
the exhaustive summed-probability oracle. Registered beam width remains eight.

## Partial Hypothesis Trace

For every emitted encoder frame, save:

- frame index, frame end sample/time, and transport availability sample/time;
- greedy hypothesis;
- top prefix-beam hypothesis and score;
- beam size and deterministic state-payload bytes;
- longest common prefix with the final hypothesis;
- edit operations from the preceding partial hypothesis.

The frame-indexed trace must be identical across Loop 21's five transport
schedules: single-sample, stride-aligned, kernel-then-stride, jittered, and
whole-item. Transport-adjusted availability times may differ and are reported
separately.

No online symbol is called committed. All partials remain revocable until the
known synthetic item end triggers `flush`; no endpoint detector is present.

## Metrics

Final synthetic-symbol metrics:

- corpus CER (aggregate edit distance / aggregate target symbols);
- exact sequence accuracy;
- per-item CER and exactness;
- repeated-adjacent-pair reconstruction rate;
- greedy-versus-prefix final comparison;
- confusion is unavailable because decoding is sequence-level.

Incremental metrics are computed against the final prefix hypothesis and the
known synthetic motif boundaries:

- `first_emission`: first frame at which any symbol occupies a final position;
- `first_correct`: first frame at which the final symbol occupies that position;
- `stable_correct`: earliest frame from which the prefix through that position
  remains equal to the final hypothesis through flush;
- `correction_delay`: stable-correct time minus first-correct time;
- `finalization`: item flush time, reported separately from stable-correct;
- `revision_events`: partial changes that are not pure suffix appends;
- `edit_overhead`: spurious edit operations divided by all partial edit
  operations, with necessary edits equal to final hypothesis length;
- prefix-correct frame fraction and longest-common-prefix trajectory.

Each timing metric is reported in encoder-frame time and transport-availability
time. Delays relative to the corresponding motif end are also reported. None
includes sensor capture, real preprocessing, endpoint detection, rendering, or
human perception.

## Signal-Free Controls

Two controls are fixed:

1. **Train-only sequence prior.** Predict the most frequent complete train
   target for every item; ties choose the lexicographically smallest sequence.
   It opens no signal or checkpoint array.
2. **Zero-signal frozen pipeline.** For each validation/test frame count, feed
   the frozen encoder its train-mean raw frame so normalization produces zero,
   then run the same prefix decoder.

Greedy CTC is an algorithmic comparator, not a signal-free control. No
dictionary, n-gram, neural language model, beam lexicon, or target-conditioned
postprocessing is allowed.

## Validation Rule

Validation opens test only when every condition passes:

```text
prefix corpus CER <= 0.10
prefix exact sequence accuracy >= 0.75
repeated-pair reconstruction rate >= 0.75
CER reduction versus each signal-free control >= 0.40
exact-accuracy gain over the stronger signal-free control >= 0.50
prefix CER <= greedy CER
5/5 schedule final outputs and frame-indexed partial traces identical
zero decoder right context and all state/resource caps pass
```

No validation result may change beam width, tie breaking, vocabulary, prior,
threshold, metric, checkpoint, or fixture protocol.

## Frozen Test Rule

The one-time test passes only when every condition passes:

```text
prefix corpus CER <= 0.10
prefix exact sequence accuracy >= 0.75
repeated-pair reconstruction rate >= 0.75
CER reduction versus each signal-free control >= 0.40
exact-accuracy gain over the stronger signal-free control >= 0.50
prefix CER <= greedy CER
95% paired item-bootstrap lower bound for CER reduction vs prior > 0
95% paired item-bootstrap lower bound for CER reduction vs zero-signal > 0
```

The paired bootstrap uses 2,000 item resamples and seed `2322`. Test performs
one canonical encoder/decoder pass only. A failure parks the branch without a
new beam width, checkpoint, fixture seed, test pass, or language model.

## Resource Caps

| Resource | Hard cap |
|---|---:|
| Complete fresh fixture | 1 MiB |
| Items / samples per item / total frames | 64 / 128 / 2,048 |
| Frozen model parameters | exactly 1,130 |
| New trainable parameters / training runs | 0 / 0 |
| Prefix beam width / maximum prefix | 8 / 12 |
| Encoder overlap state | 1 KiB |
| Decoder numeric/prefix payload state | 4 KiB |
| Working arrays before framework overhead | 16 MiB |
| Total gate runtime | 20 sec |
| Process peak RSS | 768 MiB |
| Reports/config artifacts | 1 MiB |
| CPU numerical threads | 1 |
| Fresh test semantic opens | 1 |

Report fixed model bytes, encoder and decoder state separately, Python object
overhead separately where measurable, fixture/report bytes, runtime, peak RSS,
canonical and schedule RTF, push count, partial-trace bytes, and every access
event.

## Decision Rule

`proceed` means only that a frozen synthetic frame classifier can drive a
bounded incremental CTC decoder on a deliberately easy generated symbol task.
It authorizes Loop 24's local precision/runtime comparison on this same frozen
synthetic pipeline.

`park` preserves the result and stops decoder expansion. Neither outcome
authorizes a language model, real-cache conversion, real validation score, or
real-time brain-to-text claim. Those remain separate later gates.
