# Loop 55 AI-Assisted Representation Research

Date: 2026-07-17

Status: **planning research addendum complete; synthetic policy tooling eligible;
Loop 54 dependent; real experiment `Not Started`; unauthorized**

Machine boundary:
`registries/loop55_ai_research_policy.v0.json`

## Decision

Introduce AI as a bounded research proposer and protocol critic, not as an
unrestricted optimizer and not as a language-model decoder.

The first scientific target remains the causal pre-keypress performed-hand
endpoint already defined by Loop 55. The harder performed-key endpoint remains
second. AI may help search for a better representation recipe inside one frozen
compact causal model family, but it may not change those endpoints, view final
outcomes, introduce target text, or broaden a passing claim.

This addendum does not preregister or authorize the real Loop 55 experiment. It
does not open the acquired S20 bundle, create a split, train a model, run
inference, or calculate a neural metric. Its currently eligible implementation
surface is a dependency-free validator for synthetic AI proposal manifests.

## Why This Is The Right AI Layer

NeuroDecodeKit's current scientific bottleneck is the neural representation,
not sentence fluency. The consumed S21 candidate and the historical S7 EEG
classifier both lost to no-signal comparators. Adding a language model to a
weak encoder could make output look better without demonstrating that the
sensor signal contributed useful information.

The useful near-term roles for AI are therefore:

1. propose a small number of causal representation recipes inside a frozen
   menu and resource budget;
2. criticize each proposal for leakage, hidden future context, confounds,
   unmatched controls, and claim inflation; and
3. support optional target-free self-supervised warm-up that never consumes
   performed labels, intended text, or pretrained external weights.

The AI never receives raw protected EEG, marker descriptions, key identities,
trial text, final predictions, or final scores. A deterministic local runner,
not the agent, owns every future data access and model operation.

## Primary-Source Basis

### 1. Constrained AI research can improve a fixed decoder pipeline

Brain2Qwerty v2 reports three coding agents optimizing validation WER from a
fixed architecture, data pipeline, loss family, and runtime. The baseline
validation WER was `0.45`; the three agents reached `0.38`, `0.36`, and `0.37`.
Their selected configurations also retained improvements in a broader
cross-subject test. Label smoothing, modality dropout, beam search, and
contrastive alignment were among the discovered changes.

The same paper reports that open-ended optimization failed: large entangled
changes frequently crashed, and agents stopped making useful progress.

Source: [Brain2Qwerty v2, Auto Research](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf)

Decision: expose only a fixed causal family, an exact parameter menu, aggregate
train-inner summaries, four proposal rounds, and a complete immutable
transcript. The agent may propose; deterministic code validates and executes.

### 2. Encoder quality remains the main scientific bottleneck

Brain2Qwerty v2 states that final performance is strongly associated with
upstream encoder quality and names cross-subject transfer and self-supervised
pretraining as priorities. It also reports that an LLM can produce fluent but
incorrect sentences when encoder and neural-token quality are weak.

Source: [Brain2Qwerty v2 discussion](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf)

Decision: optimize causal sensor representation before any language model is
eligible. Sentence fluency is not a Loop 55 objective or selection metric.

### 3. Self-supervision is plausible, but transfer is not automatic

LaBraM uses masked EEG modeling over large multi-dataset pretraining, while
BIOT uses cross-data biosignal learning designed for heterogeneous channels and
lengths. Both support the general idea that unlabeled biosignal structure can
improve learned representations.

Sources:

- [LaBraM: Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI](https://openreview.net/forum?id=QzTpTRVtrP)
- [BIOT: Biosignal Transformer for Cross-data Learning in the Wild](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f6b30f3e2dd9cb53bbf2024402d02295-Abstract-Conference.html)

Decision: borrow only the target-free learning principle. Do not import their
model scale, pretrained weights, task assumptions, or performance claims. A
future Loop 55 warm-up must use only its authorized source-train signal.

### 4. Compact causal EEG models remain the local fit

EEGNet demonstrates that depthwise and separable temporal-spatial operations
can create compact EEG classifiers across several BCI paradigms. It does not
establish superiority for this participant, typing task, or causal window.

Source: [EEGNet](https://arxiv.org/abs/1611.08024)

Decision: retain the existing Loop 55 ceiling of one compact causal family and
`10,000` trainable parameters including both performed-key and performed-hand
heads.

## Scientific Target

AI does not choose the scientific question. The ordered endpoints remain:

1. `L55-E1`, causal performed-hand prediction from `[-500, 0)` ms EEG;
2. `L55-E2`, causal 29-class performed-key prediction from the same frozen
   representation; and
3. the noncausal `[-200, +300]` ms centered diagnostic, which cannot rescue a
   causal failure.

The first credible positive outcome remains `L55-O5`: the hand endpoint clears
the no-signal, timing, corruption, and every available peripheral comparison
while the key endpoint does not. That outcome would establish at most a bounded
one-block performed-hand EEG sensor-signal effect.

## AI Roles

### `L55-AI-R1`: bounded recipe proposer

The proposer emits a strict JSON manifest. It may choose only allowlisted
values for learning rate, weight decay, dropout, temporal kernel, optional
target-free warm-up, mask fraction, and hand auxiliary-loss weight.

It may not write or alter training code during a protected execution. Any code
change belongs to a new ordinary engineering commit and must pass the same
tests and review before a future experiment contract can bind it.

### `L55-AI-R2`: adversarial protocol critic

The critic receives the proposal manifest and public policy only. It checks for
endpoint drift, future context, target leakage, language priors, pretrained
weights, hidden participant identifiers, cap expansion, unavailable controls,
and claim inflation. It emits findings, not a replacement proposal.

### `L55-AI-R3`: target-free representation warm-up

This is a future model stage, not an autonomous agent. A proposal may choose
one of:

- `none`;
- `masked_reconstruction`; or
- `contrastive_next_window`.

Warm-up may use only authorized source-train EEG values and masks. It may not
use performed keys, hand labels, marker descriptions, target text, semantic
embeddings, external weights, selection rows, or final rows. It remains part of
the same compact family and total parameter ceiling.

## Ordered Phases

### Phase A: synthetic policy rehearsal

Eligible now under Tier B:

- validate synthetic proposal manifests;
- reject malformed or out-of-policy proposals;
- prove deterministic canonical hashes;
- exercise the CLI without NumPy, MNE, Torch, a network, or participant data;
- record zero real-data, target, model, training, inference, and scoring
  counters.

Phase A establishes governance mechanics only.

### Phase B: post-Loop-54 preregistration design

Not eligible now. After Loop 54 closes with at least 48 qualified trials, a
future contract may bind:

- exact channel and sampling geometry;
- an exact causal architecture and transform;
- a fixed proposal menu and initial recipe;
- at most four train-inner AI proposal rounds;
- the aggregate summaries visible after each round;
- a deterministic winner rule and tie rule;
- the remaining model/control fit inventory; and
- the immutable transcript and hash-freeze order.

The future contract, not this addendum, must decide whether AI proposal rounds
are scientifically and computationally justified for the measured trial count.

### Phase C: future protected execution

Requires a separate exact Tier C decision after the Phase B contract and
implementation are committed, pushed, and remotely green. The agent may see
only aggregate train-inner summaries. Selection and final targets, predictions,
and scores remain unavailable to it.

Once the fourth proposal is accepted or the deterministic stop rule fires, the
recipe freezes. The agent cannot participate in selection-target opening,
final inference, final scoring, interpretation routing, or claim writing.

## Proposed Fit Budget

The existing maximum remains `12` parameter-update runs. A future exact
contract may allocate no more than:

| Purpose | Maximum runs |
|---|---:|
| AI-guided train-inner proposal rounds | 4 |
| frozen primary candidate and stability | 3 |
| train-pairing derangement | 1 |
| EOG-only or recorded peripheral comparator | 1 |
| EEG plus EOG diagnostic | 1 |
| compact linear representation comparator | 1 |
| centered noncausal diagnostic | 1 |
| **Total** | **12** |

Exact-zero, frozen-checkpoint signal corruptions, and deterministic no-signal
priors should not consume parameter-update runs. If measured geometry requires
another trained control, reduce AI rounds rather than expand the total.

Unused capacity is not permission to add a proposal, seed, model, or rerun.

## Proposal Visibility Firewall

The future AI proposer may receive:

- the committed public research policy;
- the accepted aggregate Loop 54 geometry and confound ledger;
- exact resource usage from completed train-inner rounds;
- aggregate trial-level train-inner metrics for the frozen endpoints and
  controls; and
- validator findings and unavailable-field declarations.

It may never receive:

- raw or windowed EEG values;
- VMRK or MAT content;
- key identities, hand labels, predictions, or errors for individual trials;
- intended text, marker descriptions, semantic groups, or language features;
- selection or final metrics;
- final predictions, targets, or hashes reversible through a known dictionary;
- participant payload paths or private derivative paths; or
- any instruction to maximize a publishable or positive conclusion.

The optimization target must be a preregistered train-inner decision statistic,
not "obtain a positive result."

## Deterministic Validator Requirements

Version `0` proposal validation must:

- reject unknown top-level and nested fields;
- enforce exact schema and objective identities;
- enforce the causal `[-500, 0)` window and zero right context;
- reject language models, external embeddings, pretrained weights, intended
  text, marker semantics, future samples, and protected observations;
- enforce the fixed hyperparameter menu;
- enforce one thread, one worker, one proposal run, and all byte/time/RSS caps;
- require every protected-access counter to be zero in synthetic rehearsal;
- require an engineering-only claim boundary;
- canonicalize JSON with sorted keys and compact separators; and
- emit a deterministic SHA-256 proposal identity and validation report.

The validator does not call an AI service, execute code from a proposal, train
a model, or authorize a future phase.

## Acceptance Gates

This planning and synthetic-policy milestone passes only if:

1. the research document and machine policy agree;
2. every real/protected execution flag remains false;
3. one valid synthetic proposal replays to the same hash;
4. target text, final metrics, raw EEG, noncausal context, an LLM, pretrained
   weights, unknown fields, cap expansion, and extra proposal runs are rejected;
5. CLI validation reads only the contract and named synthetic proposal;
6. the base install remains dependency-free;
7. the complete pre-existing unit suite does not regress;
8. Ruff and `git diff --check` pass; and
9. no generated model, cache, participant artifact, or inspection debris is
   committed.

## Current Access And Resource Ledger

This research pass reads public primary-source pages and committed local text
artifacts only. Current counters are:

- S20 header, EEG, VMRK, MAT, signal, and target reads: `0`;
- split creations: `0`;
- model, training, inference, and scoring runs: `0`;
- network data downloads: `0`;
- language-model decoder runs: `0`;
- device, stream, hardware, and participant operations: `0`.

Only tiny JSON policy and synthetic proposal artifacts are eligible. One CPU
thread and one worker remain mandatory. The synthetic validator output cap is
`1 MiB`.

## Claim Ceiling

Passing the synthetic policy gate establishes only that NeuroDecodeKit can
constrain, hash, inspect, and reject AI-generated research proposals before
they interact with protected evidence.

It does not establish that AI improved a representation, that self-supervision
helps S20, that EEG predicts a performed hand or key, that the signal is brain
specific, or that any decoder generalizes, operates continuously, runs in real
time, works on portable hardware, works at home, or has clinical utility.

Engineering capability added: NeuroDecodeKit gains a prospective, machine-checkable boundary for using AI as a bounded causal-representation proposer without granting it protected data or scientific decision authority.

Scientific claim not established: no S20 content, split, model, training, inference, prediction, score, or latency measurement was accessed or produced, so no AI-assisted neural advantage or EEG decoding result exists.
