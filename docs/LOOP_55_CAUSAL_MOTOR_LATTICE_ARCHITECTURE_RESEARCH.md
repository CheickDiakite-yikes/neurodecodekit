# Loop 55 Architecture Research: Causal Motor Lattice v0

Date: 2026-08-06

Status: **additive architecture research complete; synthetic implementation not
started; every real-data and protected stage unauthorized**

Machine boundary:
`registries/loop55_causal_motor_lattice_research.v0.json`

## Executive Decision

Do not answer the current negative results by scaling the same generic temporal
encoder or by importing a foundation model. The next architecture hypothesis is
**Causal Motor Lattice v0 (`CML-v0`)**: a small, failure-addressable EEG model
whose branches correspond to three pre-keypress motor signatures and whose
outputs respect the physical hierarchy of a keyboard.

The proposed path is:

```text
strict pre-keypress EEG
  -> potential / mu / beta views
  -> rank-8 spatial mixers
  -> three causal temporal cells per view
  -> 24-dimensional shared bottleneck
  -> keyboard-primitive lattice + bounded key residual
  -> 29-key probabilities
  -> exact left/right marginal for hand-eligible keys
```

This is a NeuroDecodeKit-specific synthesis of published compact filter-bank,
motor-physiology, and keyboard-layout findings. It is not a claim that the
architecture is globally novel, superior, implemented, or validated.

The key strategic change is not merely a new model. It is a model that can
route a failure. A negative result can distinguish absent pre-movement
potential, absent mu/beta evidence, missing spatial geometry, a task-timing
shortcut, peripheral contamination, insufficient signal quality, or a failure
of the keyboard factorization. That is more useful than another opaque score.

This pass opened no EEG payload, S20 path, target, cache, checkpoint, or model.
It trained and scored nothing.

## Why Another Generic Encoder Is The Wrong Bet

The current evidence says four things at once:

1. the tiny S21 causal family was stable but worse than its no-signal prior;
2. adding temporal context helped a synthetic task, but the absolute synthetic
   gate still failed;
3. current EEG foundation-model benchmarks do not show that parameter scale
   reliably beats compact specialist models; and
4. Brain2Qwerty errors and learned features follow physical keyboard geometry.

A larger sequence model would consume more compute while preserving the most
important ambiguity: whether there is any usable pre-keypress motor signal in
this exact EEG block. `CML-v0` instead spends its parameter budget on explicit
physiological and physical structure.

## Primary-Source Synthesis

### Brain2Qwerty gives us a physical output prior, not a language prior

The 2026 Brain2Qwerty paper reports a correlation between physical keyboard
distance and character confusion (`r = 0.73`, `p = 0.02`, `n = 19`) and reports
that a two-cluster analysis of the learned convolutional representation
separates left- and right-hand keys. That motivates a keyboard lattice built
only from key geometry. It does not authorize text, sentence identity,
autocomplete, or a language model.

Source: [Noninvasive decoding of typed sentences from human brain
activity](https://www.nature.com/articles/s41593-026-02303-2)

### Multi-view compact models are appropriate under scarce, noisy EEG

FBCNet uses multiple fixed frequency views, learned spatial filters, and
variance aggregation to improve sample efficiency on motor-imagery EEG. EEGNet
uses compact depthwise and separable operations across several BCI paradigms.
These papers support a small filter-bank specialist. They do not prove that
their published windows, tasks, or accuracies transfer to pre-keypress typing.

Sources:

- [FBCNet: A Multi-view Convolutional Neural Network for Brain-Computer
  Interface](https://arxiv.org/abs/2104.01233)
- [EEGNet: A Compact Convolutional Network for EEG-based Brain-Computer
  Interfaces](https://arxiv.org/abs/1611.08024)

### Covariance geometry is valuable, but it belongs in the comparator lane

Deep Riemannian Networks combine learnable filterbanks with SPD geometry and
report strong public motor-task results. That makes a fixed Riemannian family a
serious classical comparator. It is not the first protected candidate here:
estimating and optimizing short-window covariance geometry would add a second
large design surface before S20 channel geometry, sampling, and trial counts
are qualified.

Source: [Deep Riemannian Networks for end-to-end EEG
decoding](https://pmc.ncbi.nlm.nih.gov/articles/PMC12319850/)

### Onset and signal quality can matter more than scale

A 2026 handwriting-decoding benchmark reports that withholding movement onset
reduced average four-letter accuracy from `41.3%` to `32.4%`, and that improved
test-time signal quality raised the best participant from `45%` to `78%`.
Specialist models still beat the tested foundation models. A separate 2026
channel-adaptation benchmark finds architecture-dependent adaptation and
negative transfer; a 5-million-parameter specialist beat models up to 31 times
larger on four of five tasks.

Sources:

- [Handwriting decoding as a challenging motor task for EEG Foundation
  Models](https://arxiv.org/abs/2605.15698)
- [Channel Adaptation for EEG Foundation Models: A Systematic Benchmark Across
  Architectures, Tasks, and Training Regimes](https://arxiv.org/abs/2604.23091)

Decision: qualify timing, signal, and architecture separately. Do not use model
scale as a substitute for a positive-control ladder.

### Pre-movement potential and mu/beta activity deserve separate views

The 2026 IACKD data descriptor technically validates readiness-potential and
mu/beta ERD/ERS signatures with synchronized hand kinematics. A separate 2026
EEG+EMG dataset provides 40 participants, five sessions, and repeated
right-fist closures for movement-related cortical-potential analysis.

Sources:

- [Intention-Action Conflict EEG-Hand Kinematics
  Dataset](https://doi.org/10.1038/s41597-026-07146-x)
- [EEG and EMG dataset for analyzing movement-related cortical potentials in
  hand gesture tasks](https://doi.org/10.1016/j.dib.2026.112596)

Neither source is a clean substitute for S20. IACKD uses a visible task cue and
is approximately 7.4 GB in its public BIDS release. The EEG+EMG dataset uses
only right-hand fist closure and a visual interface, so it can qualify true
pre-movement timing mechanics but not left/right typing laterality.

### Responder and session effects are part of the hypothesis

A 2025 real-time finger BCI used subject-specific EEGNet fine-tuning across an
offline and two online sessions in experienced participants. Its design and
screening reinforce a practical point: one participant and one block may be a
genuine nonresponder or an underpowered session. A negative S20 result should
trigger a measured stop, not automatic architecture expansion.

Source: [EEG-based brain-computer interface enables real-time robotic hand
control at individual finger level](https://www.nature.com/articles/s41467-025-61064-x)

## CML-v0 Input Contract

The primary candidate receives only:

- Loop 54-qualified EEG channels in source order;
- train-only channel normalization parameters;
- samples strictly before each known keypress;
- a declared analysis window recommended as `[-500, 0) ms`;
- any required left filter context, also strictly before the keypress; and
- masks needed to distinguish valid samples from padding.

The right endpoint is exclusive. A sample at the keypress or after it is
future information. Marker descriptions, event codes, key identities, target
text, sentence identity, prompt identity, timing position, EOG, EMG, and other
peripheral values are forbidden candidate inputs.

Known onset and event count remain alignment scaffolding. Their predictive
contribution is measured by the existing timing-only comparator.

## Three Physiological Views

Each view has one rank-8 learned spatial mixer. Each mixed component is reduced
into three ordered temporal cells, producing `8 x 3 = 24` values per view and
72 values overall.

Every learned spatial row is transformed to zero sum and unit L2 norm before
use. This adds no trainable parameter, makes a uniform common-reference offset
invisible to that row, and prevents scale from drifting into the spatial
weights. It does not make the model invariant to every possible reference or
prove artifact removal.

### View V0: potential shape

This view preserves slow pre-movement shape through three piecewise means after
train-only robust channel normalization. It does not claim to resolve a
`0.1-1 Hz` band from a 500 ms window. No event-centered high-pass or future
baseline may manufacture a readiness potential.

The three cells describe early, middle, and late pre-keypress potential. A
future exact implementation may use an earlier strictly causal context for
drift control, but that context and its latency must be frozen and reported.

### View V1: mu energy

This view applies a fixed one-sided `8-13 Hz` finite-support filter, then the
rank-8 spatial mixer, squaring, valid-only three-cell aggregation, and a
train-only fixed `log1p` scale. It represents mu desynchronization hypotheses.

### View V2: beta energy

This view mirrors V1 with a fixed one-sided `13-30 Hz` filter. It represents
beta desynchronization and rebound-related hypotheses, although the primary
window excludes post-keypress rebound.

For both rhythmic views, centered convolution, zero-phase filtering, reflected
future padding, circular padding, and filter reset artifacts are forbidden.
The exact future filter contract must publish coefficients, impulse response,
frequency response, group delay, required left context, valid sample count,
and anti-alias response before any real execution.

## Shared Bottleneck

The 72 view features enter one `72 -> 24` affine layer, one 24-feature layer
normalization, and one fixed activation. There is no attention, transformer,
recurrent state, sentence context, pretrained embedding, NeuroToken input, or
language model.

This small bottleneck forces the three views to negotiate a shared motor
representation while keeping the failure surface inspectable.

## Keyboard Motor Lattice

The output head is the core structural proposal.

Let `A` be a fixed, target-frequency-independent incidence matrix mapping each
of the 29 registered performed keys to at most 18 physical keyboard
primitives. Candidate primitive groups may include:

- hand side for hand-eligible keys;
- physical row;
- horizontal zone or column; and
- explicit special-key type.

The exact key list and primitive map remain unavailable until the protected
ontology is qualified. They must be frozen before training. Participant target
frequencies, intended text, model behavior, and final outcomes may not alter
the map. Ambiguous hand classes such as a special key are masked prospectively
and counted; they may not be assigned a convenient hand after outcomes are
seen.

The 24-dimensional bottleneck produces:

1. at most 18 primitive logits;
2. 29 direct residual key logits; and
3. 29 final key logits formed from the normalized fixed lattice contribution
   plus a bounded residual.

The residual preserves distinctions that a coarse physical map cannot express.
It enters as `rho * tanh(z_residual)`, where fixed `0 <= rho <= 1` is selected
only by a future synthetic contract and frozen before any public or protected
payload opens. Its norm and contribution must be reported. The bounded path
prevents the model from quietly becoming an unconstrained 29-way head.

There is **no independent trainable hand head**. For a hand-eligible event, the
left and right probabilities are exact renormalized sums of the final key
probabilities under the frozen hand map. Therefore key and hand predictions
cannot contradict one another.

The supervised loss may combine key cross-entropy, the exact hand-marginal
loss on eligible events, and primitive-group auxiliary losses. Every auxiliary
target is derived only from the performed key. Intended text and sentence
context remain unavailable. Exact weights are deferred to a synthetic-only
contract and must freeze before public or protected targets open.

## Exact Parameter Ledger

For `C` qualified EEG channels and `P <= 18` registered primitives:

| Component | Parameters |
|---|---:|
| three rank-8 spatial mixers with bias | `3 * (8C + 8)` |
| `72 -> 24` bottleneck with bias | `1,752` |
| 24-feature layer normalization | `48` |
| primitive head with bias | `25P` |
| bounded 29-key residual head with bias | `725` |
| **total** | **`24C + 2,549 + 25P`** |

At the maximum `P = 18`, the total is `24C + 2,999`. Reference totals are:

- `4,463` parameters at `C = 61`;
- `4,535` parameters at `C = 64`; and
- below the existing `10,000`-parameter ceiling for every `C <= 291`.

Fixed filters, spatial row normalization, temporal cells, incidence maps,
residual gain, probability marginals, and diagnostic masks add zero trainable
parameters. The actual count must be
recomputed from the future qualified channel and primitive counts. A mismatch
parks the implementation; it does not silently expand the ceiling.

## Geometry Policy

`CML-v0` does not invent electrode locations.

- The primary rank-8 mixers can operate from source channel order without
  geometry.
- Channel names and geometry availability are carried in provenance.
- If Loop 54 independently qualifies homologous left/right sensor pairs, a
  fixed hemisphere-mirror diagnostic may be added with zero learned
  parameters.
- If names or geometry are incomplete, the diagnostic is unavailable and the
  claim ceiling narrows.
- Spherical interpolation, source reconstruction, template coordinates, and
  automatic montage adaptation remain outside the protected primary model.

This avoids the negative-transfer risk of choosing a channel adapter before
the source montage is known.

## Same-Checkpoint Evidence Escrow

Before any selection or final targets open, one trained candidate must freeze
predictions for these target-blind same-checkpoint probes:

| Probe | Operation | Question |
|---|---|---|
| full | no mutation | reference behavior |
| potential-muted | replace V0 with its train-only neutral value | does slow shape matter? |
| mu-muted | replace V1 with its train-only neutral value | does mu energy matter? |
| beta-muted | replace V2 with its train-only neutral value | does beta energy matter? |
| all-views-muted | neutralize V0/V1/V2 | is the checkpoint using signal? |
| channel-deranged | apply the frozen channel permutation | does sensor identity matter? |
| time-displaced | apply the frozen nonwrapping displacement | does pre-key timing matter? |
| hemisphere-mirrored | fixed qualified pair swap, if available | is lateralization coherent? |

These probes use the same checkpoint and add no parameter-update run. They are
descriptive failure localizers, not parameter-matched scientific controls.
The separately trained no-signal, timing, EOG, linear, CSP/Riemannian, and
centered-window conditions retain their existing roles.

A branch ablation cannot prove that a learned feature is cortical mu, beta, or
a readiness potential. Correlated artifacts can travel through the same view.

## Two-Axis Public Qualification Ladder

The previous single-positive-control idea is incomplete. No tiny public source
reviewed here validates both left/right motor laterality and strict
pre-movement onset mechanics.

### Axis P1: laterality and pipeline control

Retain the prospective PhysioNet EEG Motor Movement/Imagery slice already
identified in the open EEG strategy: S001-S003, execution runs 3/7/11, nine
EDF files, `23,248,224` public-metadata bytes. It can test left/right execution,
reader correctness, spatial laterality, and the classical comparator lane.

It is cue aligned and off-task. It cannot qualify strict pre-keypress typing,
S20, or a thought-to-text claim. It remains undownloaded and unauthorized.

### Axis P2: pre-movement timing control

Prospectively prepare a separate tiny slice from the 2026 EEG+EMG MRCP dataset.
EMG supplies an independently measured movement-onset reference; repeated rest
periods can support timing and displacement checks.

The exact participant, files, byte sizes, license interpretation, fit/check
partition, and caps are not selected now. It is right-hand-only and visually
cued, so it cannot qualify left/right laterality or typing. No payload was
downloaded or opened, and no contract is authorized.

### Why both axes matter

- P1 pass + P2 pass: architecture mechanics are eligible for a future S20
  freeze, still without scientific transfer.
- P1 pass + P2 fail: laterality pipeline works, causal pre-movement mechanics
  do not; park before S20 model work.
- P1 fail + P2 pass: onset pipeline works, spatial laterality does not; park and
  audit channel handling.
- both fail: stop. Do not spend protected S20 evidence on this candidate.

These public controls require separate exact Tier C acquisition and execution
decisions. This document authorizes neither.

## Synthetic Factor-Isolation Gate

The next autonomous Tier B task may implement only a deterministic synthetic
fixture and the pure architecture mechanics. It should contain isolated
families for:

- potential-shape signal;
- mu-energy signal;
- beta-energy signal;
- mixed potential/mu/beta signal;
- left/right spatial reversal;
- timing-only labels with no signal relation;
- peripheral-like common-mode artifact; and
- pure noise.

The fixture must use a fresh deterministic seed, strict train/check/final
partitions, no real channel names or targets, and no external weights. The gate
should verify exact parameter accounting, causal mutation tests, replay,
padding, branch-specific ablation ordering, hand/key consistency, negative
controls, runtime, RSS, and output caps.

Passing that gate would establish implementation mechanics only. It would not
show that real EEG contains any corresponding effect.

Recommended synthetic ceiling:

- one CPU thread and one worker;
- at most four parameter-update runs inside a future exact contract;
- at most 600 wall seconds;
- at most 512 MiB peak RSS; and
- at most 4 MiB generated output.

No synthetic implementation or run occurred in this research pass.

## Hypothesis Router

| Route | Observation | Next decision |
|---|---|---|
| `CML-R0` | synthetic mechanics fail | repair mechanics once under a new bounded contract or park |
| `CML-R1` | P1 laterality fails | audit reader/channel handling; do not open protected model stage |
| `CML-R2` | P2 pre-movement timing fails | park causal CML-v0 for S20 |
| `CML-R3` | both public axes pass, Loop 54 fails | park S20; source is not qualified |
| `CML-R4` | public axes and Loop 54 pass | freeze one exact protected candidate and control inventory |
| `CML-R5` | S20 hand passes, key fails | retain bounded performed-hand sensor effect only |
| `CML-R6` | centered diagnostic passes, causal views fail | report task-aligned/post-keypress information only |
| `CML-R7` | EOG/timing/control matches candidate | no EEG-specific claim; localize shortcut |
| `CML-R8` | causal hand and key clear every gate | bounded one-block sensor-signal result only |

## Alternatives Rejected For The Protected First Pass

| Alternative | Decision |
|---|---|
| transformer, SSM, or recurrent sequence model | rejected: unnecessary context and a larger leakage/compute surface before a single-event effect exists |
| EEG foundation model | deferred: current evidence does not show scale is the binding constraint, and channel adaptation can hurt |
| end-to-end deep SPD network | comparator/watch lane: promising, but adds covariance and geometry design before S20 qualification |
| graph neural network over electrodes | deferred: local source geometry is unopened and must not be invented |
| independent hand and key heads | rejected: can contradict and wastes the known physical hierarchy |
| one monolithic learned temporal convolution | rejected: cannot distinguish potential, mu, and beta failure modes |
| intended-text or language-model correction | forbidden: can hide a weak neural encoder |
| generative channel or sample imputation | forbidden for primary evidence: generated signals are not measured observations |

## Unknowns That Must Stay Unknown

The research pass does not know and must not guess:

- S20 declared channel count, names, sample rate, reference, or geometry;
- S20 signal quality, usable trials, event ontology, or key frequencies;
- the exact 29-key list or hand eligibility of special keys;
- the exact causal FIR coefficients or required left context;
- lattice primitive count `P`, auxiliary-loss weights, optimizer, or seed;
- whether either public positive-control axis will pass;
- whether S20 contains a usable pre-keypress effect; or
- whether any effect is cortical rather than ocular, muscular, motion, cue, or
  task-timing information.

Each becomes eligible only in its ordered target-blind stage.

## Recommended Research Order

1. Keep L54-A blocked until exact registration commit `c114623` has a green
   replacement CI run and a separate exact Tier C decision.
2. Under Tier B, prospectively contract and implement the synthetic
   factor-isolation gate for `CML-v0` without real data.
3. If synthetic mechanics pass, prepare exact metadata-only contracts for the
   two public axes; do not combine their permissions.
4. Execute P1 and P2 once each only after their own green decision and
   implementation sequences.
5. Continue Loop 54 through its separately authorized A/B/C/D stages.
6. Only if both public axes and Loop 54 pass, freeze the exact S20 model,
   transforms, lattice, split, 12-fit inventory, controls, and target order.
7. Score S20 final trials once after a hash-only prediction freeze is committed,
   pushed, and remotely green.
8. Stop at the first failed qualification rung. Do not compensate with a larger
   model, more data access, a language model, or post-target tuning.

## Authorization And Access Ledger

Authorized in this pass:

- public primary-source research;
- additive documentation and a machine-readable registry;
- dependency-free invariant tests;
- coherent commit, push, and CI inspection under Tier A/B autonomy.

Not authorized in this pass:

- any S20 path stat, content read, parsing, or interpretation;
- any public EEG payload download or read;
- any target, label, marker, event, trial, cache, checkpoint, or prediction
  access;
- model implementation, inference, training, scoring, or selection;
- a Loop 55 split, preregistration, or scientific claim;
- pretrained weights, language models, RW3, streams, devices, or hardware;
- changes to frozen Loop 54/55 contracts; or
- release, home-use, clinical, neural-advantage, or decoding claims.

Every real/protected/model counter in the registry is zero.

## Closeout

Engineering capability proposed: NeuroDecodeKit now has a machine-checkable,
failure-addressable compact EEG architecture and a two-axis qualification
strategy that can separate potential, mu, beta, spatial, timing, and keyboard-
structure hypotheses before protected evidence is spent.

Scientific claim not established: no EEG payload, protected target, model, or
score was accessed, so this work establishes no EEG effect, neural advantage,
decoding accuracy, generalization, causal real-time output, portable hardware,
home use, or clinical utility.
