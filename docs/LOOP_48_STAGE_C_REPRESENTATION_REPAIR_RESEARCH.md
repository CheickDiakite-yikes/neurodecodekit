# Loop 48 Stage C Temporal-Representation Repair Research

Date: 2026-07-15

Status: **Planning research complete; synthetic calibration and implementation
not started; prospective protected diagnostic not preregistered or authorized**

Machine boundary:
`registries/loop48_stage_c_representation_repair_research.v0.json`

## Decision In Plain Language

Loop 48 Stage B gave us a useful negative diagnosis. The current transformed
S21 representation was stable, but neither a 2,908-parameter causal probe nor a
2,884-parameter pointwise linear probe separated the train-check rows better
than the no-signal prior. The simplest fixed timing offsets also failed to
explain the result.

The next hypothesis should therefore be narrow:

> The failed probe may be starved of temporal context. It mixes all 102 sensors
> at each 10 ms frame, but its only learned temporal operation sees the current
> frame and two previous frames. A compact causal encoder that represents
> roughly half a second of sensor history before 4x CTC downsampling may expose
> information that the 20 ms probe cannot separate.

This is `R1`, the **temporal-context-starvation hypothesis**. It is not yet a
result. The research selects one 7,692-parameter candidate and one
7,568-parameter zero-context ablation, then freezes a synthetic-only
calibration plan. No S21 cache, target, ignored derivative, checkpoint, private
prediction, validation row, source-test row, session 2, S24, or S25 payload was
opened for this work.

## Why This Is The Next Identifiable Question

The current `TinyCausalSentenceCTC-v0` performs:

```text
102 sensors -> pointwise 16-channel projection -> causal kernel-3 convolution
            -> pointwise 28-class CTC head
```

Its receptive field is three 100 Hz frames: 30 ms total and 20 ms of left
context. Stage B showed that this exact candidate and the pointwise linear
probe were finite and stable but nonseparable relative to the prior. That does
not distinguish "no usable information" from "useful information exists over
a longer temporal pattern."

The proposed repair changes only the temporal representation family. It does
not add a Conformer, attention, participant identity, a language model,
NeuroTokens, semantic targets, geometry-conditioned merger, calibration, or a
new person. The parameter ceiling remains below Loop 50's 10,000-parameter
planning limit.

## Primary-Source Findings

### Brain2Qwerty v2 Uses More Than Pointwise Plus 20 ms

The official Brain2Qwerty v2 paper and code use a four-layer dilated
convolutional encoder with kernel size 5 and dilation period 3, followed by a
kernel-16, stride-4 temporal reducer. The reducer turns 100 Hz features into
approximately one representation frame every 40 ms. The full published model
then uses a large noncausal Conformer and an auxiliary CTC head.

NeuroDecodeKit does **not** copy the Conformer, 1,500-channel convolutional
stack, 270 virtual sensors, per-subject affine, language model, or reported
performance. It tests only whether the small causal analogue of the
convolution-plus-downsampling idea is a better representation than the current
20 ms probe.

### The Original Brain2Qwerty Used 500 ms Keystroke Windows

The original Brain2Qwerty paper used 500 ms windows from 200 ms before to
300 ms after each known keypress. That result is not directly transferable:
the current task has no keypress timing at inference and must remain causal.
It does show that published typing decoders did not treat a 20 ms window as an
adequate representation of one key event.

### Compact Temporal And Spatial Factorization Is Plausible

EEGNet introduced compact temporal and depthwise/separable spatial
convolutions for low-sample neural-signal decoding. It is EEG classification,
not MEG sentence CTC, so its accuracy does not transfer. Its architectural
lesson is useful: temporal and sensor structure can be represented without a
large dense network.

### Causal Dilated Convolutions Are A Direct Sequence Model

The Temporal Convolutional Network study treats causal dilated convolutions as
a direct sequence-modeling baseline with explicit receptive fields. That is a
generic sequence result, not neural evidence, but it supports the mechanics of
testing longer history without recurrence or future context.

### Movement Signals Span More Than Tens Of Milliseconds

Primary movement-related cortical-potential work reports activity beginning
hundreds of milliseconds before movement, with later components near movement
onset. This does not prove that the present MEG typing cache contains decodable
preparation signals. It makes a 470 ms causal lookback physiologically
plausible and keeps the hypothesis narrower than a multi-second memory model.

### CTC Still Needs An Exact Length Gate

CTC sums over alignments containing labels and blanks; after downsampling, every
output sequence must still be long enough for the target and adjacent repeats.
NeuroDecodeKit Loop 10 already proved that the exact kernel-16/stride-4 output
length is feasible for all 66 S21 session-1 rows when starting at 100 Hz. The
future Stage C gate must recheck the exact 44 allowed rows and fail before any
fit if identity or feasibility differs.

## Selected Candidate: TinyCausalTemporalCTC-v0

Input contract: `102 x T` float32 magnetometer values at 100 Hz, with true
lengths and zero padding. Existing train-only robust-scaler provenance remains
required.

| Layer | Exact operation | Parameters | Temporal effect |
|---|---|---:|---|
| Spatial projection | `Conv1d(102,16,k=1,bias=True)` | `1,648` | pointwise |
| Residual block 1 | `Conv1d(16,16,k=5,dilation=1)` plus per-time channel LayerNorm | `1,328` | adds 40 ms left history |
| Residual block 2 | same, dilation `2` | `1,328` | adds 80 ms |
| Residual block 3 | same, dilation `4` | `1,328` | adds 160 ms |
| Residual block 4 | same, dilation `1` | `1,328` | adds 40 ms |
| Temporal reducer | depthwise `Conv1d(16,16,k=16,stride=4,groups=16,bias=False)` | `256` | adds 150 ms and emits at 25 Hz |
| CTC head | `Conv1d(16,28,k=1,bias=True)` | `476` | pointwise |
| **Total** | no attention, recurrence, subject layer, or LM | **`7,692`** | **480 ms receptive field** |

Every temporal convolution is left-padded only. Each residual block applies
per-time LayerNorm across channels, GELU, and a fixed `0.1` residual scale.
LayerNorm may not aggregate over time. The temporal reducer is a learned
feature operator, not an anti-aliased waveform resampler; its output must not
be described as a reconstructed 25 Hz sensor signal.

The output length is:

```text
output_length = ceil(input_length / 4) = (input_length + 3) // 4
```

Output frame `j` is timestamped at source frame `4*j`. It may depend only on
source frames through that timestamp. The total receptive field is 48 source
frames, so required left context is 47 frames or 470 ms. Right context is
exactly zero.

## Parameter-Matched Ablation

`TinyCausalTemporalAblation-v0` keeps the 4x output grid and four residual
blocks but removes learned temporal history:

- pointwise spatial projection `102 -> 29`;
- four kernel-1 residual blocks with per-time channel LayerNorm;
- depthwise kernel-1, stride-4 decimation;
- pointwise `29 -> 28` CTC head.

It has exactly `7,568` trainable parameters, only `124` fewer than the primary
candidate, a `1.612070%` gap. Its receptive field is one source frame and its
right context is zero. A candidate win over this ablation would support the
value of the registered temporal representation, not merely a wider parameter
budget. It would still not prove brain-specific origin or fresh decoding.

## Frozen Synthetic-Only Calibration Plan

The next autonomous Tier A milestone may implement both models and run one
synthetic calibration after the implementation commit is pushed and remotely
green.

The fixture is fixed before implementation results:

- seed `4850`;
- 40 target-free-from-real-data synthetic rows at 100 Hz and 102 channels;
- `24/8/8` physically separate synthetic train/selection/final partitions;
- variable sequence lengths and explicit zero padding;
- synthetic temporal motifs whose identity depends on ordered history rather
  than a single frame;
- no real target text, real signal statistic, real prediction, or target-
  derived feature;
- future-mutation tests proving zero right context;
- exact output-length, padding, timestamp, checkpoint, and replay hashes.

Three optimizer recipes are frozen for synthetic calibration only:

| ID | Optimizer | Learning rate | Weight decay | Steps |
|---|---|---:|---:|---:|
| `L48C-SYN-OPT0` | Adam | `0.003` | `0.0` | `360` |
| `L48C-SYN-OPT1` | AdamW | `0.001` | `0.01` | `480` |
| `L48C-SYN-OPT2` | AdamW | `0.003` | `0.01` | `480` |

All use batch size `8`, float32 CPU, one thread, seed `4850`, no restart, no
early stopping, and final-step checkpoints. Selection is lowest synthetic
selection CER; ties use fewer optimizer steps, then lexical recipe ID. The
selected candidate checkpoint and one ablation checkpoint may open the eight
synthetic final rows once. Every recipe and failure remains reported.

The synthetic gate is:

1. selected candidate final CER `<=0.10`;
2. at least `7/8` exact synthetic sequences;
3. candidate final CER at least `0.10` below the ablation;
4. bitwise deterministic replay from the saved checkpoint;
5. every future-mutation and resume check passes;
6. at most four parameter-update runs, 1,800 optimizer steps, 600 seconds,
   1 GiB peak RSS, and 16 MiB generated output.

This gate selects only an optimizer for synthetic mechanics. It cannot select
a scientific architecture winner, predict real-data benefit, or authorize an
S21 run.

## Recommended Future Protected Diagnostic

The future protected Stage C contract is deliberately **not frozen yet**. It
may be prepared only after the synthetic gate closes. The current recommendation
is:

- use exactly the 44 Stage B fit rows and none of the consumed 11 check rows;
- use five target-independent semantic-hash folds;
- generate out-of-fold predictions so each row is predicted by a checkpoint
  that did not fit that row's target;
- fit the primary candidate under three nonselectable seeds across all five
  folds, plus one primary-seed ablation across all five folds: 20 total fits;
- fit fold-local no-signal priors and reuse primary checkpoints for exact-zero,
  channel-cycle, and positive time-displacement controls;
- freeze every out-of-fold prediction hash before aggregate scoring;
- keep validation, source test, the consumed 11 Stage B check rows, session 2,
  S7, S20, S24, and S25 closed; and
- cap any result at E2 historical development diagnosis.

This recommendation is not authorization and not yet a preregistration. Exact
fold identities, implementation hashes, optimizer choice, inference counts,
statistics, resource caps, and authorization wording remain unavailable until
the synthetic milestone is complete.

## Prospective Outcome Router

| Outcome | Next action |
|---|---|
| Candidate fails its fold-local prior | Park this representation and S24; prioritize raw-quality and causal-source audits |
| Candidate clears prior but not the parameter-matched ablation | Park S24; the evidence does not isolate temporal representation |
| Candidate clears prior and ablation but fails signal corruptions | Park S24; prioritize shortcut/confound work |
| Candidate clears prior, ablation, and every registered corruption under all seed rules | Permit preparation, not execution, of a versioned Loop 49/S24 amendment |
| Mixed, unstable, infeasible, or over-cap | Park without a restart, backup person, or threshold change |

No route automatically downloads S24, opens S25, promotes a claim, or permits
another S21 run.

## Sources

1. Brain2Qwerty v2 paper:
   <https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf>
2. Official v2 model configuration:
   <https://github.com/facebookresearch/brain2qwerty/blob/main/brain2qwerty_v2/config/model_config.py>
3. Original Brain2Qwerty paper:
   <https://www.nature.com/articles/s41593-026-02303-2>
4. EEGNet:
   <https://arxiv.org/abs/1611.08024>
5. Temporal Convolutional Networks:
   <https://arxiv.org/abs/1803.01271>
6. Original CTC paper:
   <https://www.cs.toronto.edu/~graves/icml_2006.pdf>
7. Movement-related cortical potentials:
   <https://pubmed.ncbi.nlm.nih.gov/8168458/>
8. Internal 100 Hz stride-4 feasibility audit:
   `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`

## Boundary

Engineering capability prepared: one exact, parameter-controlled causal
temporal-representation hypothesis and one synthetic-only calibration path can
now be implemented without touching protected evidence.

Scientific claim not established: no model was implemented or run, no real
signal or target was opened, and no neural advantage, sensor-signal dependence,
brain-specific origin, decoding improvement, generalization, real-time result,
EEG result, or device result exists from this research pass.
