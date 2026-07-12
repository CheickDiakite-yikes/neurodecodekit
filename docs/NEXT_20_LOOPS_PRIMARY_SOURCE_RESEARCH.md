# Next 20 Loops Primary-Source Research

Date: 2026-07-12

Status: **Research complete for roadmap design; no loop is authorized**

Machine roadmap: `registries/next_20_loops.v0.json`

Human roadmap: `docs/LOOPS_25_44_ROADMAP.md`

## Research Question

What 20 bounded loops would move NeuroDecodeKit from strong pipeline mechanics
and honest negative real-data results toward one defensible neural, transfer,
streaming, or device claim without reopening consumed evidence or expanding into
an unbounded architecture program?

The answer is not 20 model variants. The largest current gaps are causal
preprocessing, fresh evidence, neural-versus-language attribution, transfer,
peripheral confounds, timestamp semantics, reproducibility, privacy, and
device-specific qualification. The new roadmap therefore makes models only
one part of the program.

## Access Boundary

This research pass used public papers and maintained project documentation plus
the repository's existing aggregate reports. It performed:

```text
dataset downloads:                    0
raw or real-signal reads:             0
consumed-cache reads:                 0
target or label reads:                0
fixture generation:                   0
checkpoint reads or conversions:      0
model or decoder runs:                0
training runs:                        0
BrainFlow / LSL / PyXDF operations:   0
socket, stream, board, or device use: 0
Loop 24 execution operations:         0
RW3 Stage A operations:               0
```

At the time of this planning-only research pass, Loop 24 remained preregistered
and unauthorized. Its later 2026-07-12 target-free authorization does not alter
this pass's zero-operation measurements or authorize any Loop 25-44 row. RW3
Stage A remains separately unauthorized.

## Local Evidence That Drives The Roadmap

NeuroDecodeKit's strongest engineering evidence is already useful: bounded
selective data access, validated S21 alignment, strict split and cache
contracts, one EEG bridge, a target-isolated NeuroToken interface, causal
synthetic replay, transparent controls, and measured resource closeouts.

The scientific boundary is less flattering and more important:

- the fixed S21 same-person cross-session MEG model is worse than its no-signal
  prior;
- the S7 EEG nearest-centroid event classifier is worse than its no-signal
  prior;
- no unseen-person, causal real-neural, portable-device, or end-to-end
  real-time result exists;
- S21 session-2, S7 evaluation evidence, and synthetic seeds 2203, 2303, and
  2353 are consumed for the decisions they informed.

The next roadmap must create fresh information rather than manufacture a more
impressive presentation of the same evidence.

## Finding 1: Causality Must Include Preprocessing

[Brain2Qwerty v2](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf)
uses an asynchronous CTC encoder, but its published full system still processes
an entire sentence with a noncausal architecture. The authors explicitly
identify low-latency causal operation as future work. A causal local encoder
therefore does not establish a causal pipeline unless filtering, resampling,
normalization, padding, and endpoint behavior are causal too.

[MNE's `Raw.resample` documentation](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.resample)
warns that downsampling continuous raw data can jitter trigger timing and
documents algorithm, padding, stim-channel, and event-resampling choices. Those
choices belong in the cache contract and replay test, not in an undocumented
preprocessing helper.

Roadmap response:

- Loop 25 audits the complete preprocessing state and future context;
- Loop 30 keeps scheduling, compute, and rendering latency separate;
- Loop 41 preserves source, corrected, arrival, token, and render clocks.

## Finding 2: Fresh Evidence Is More Valuable Than A Larger Local Model

Brain2Qwerty v2 reports 22,000 sentences from nine participants across 90
sessions and finds a strong relationship between recording volume and encoder
performance. It also reports that sentence diversity contributes independently
from repeated examples. Those results do not imply that scaling NeuroDecodeKit's
small SpanishBCBL experiment will succeed, but they do show that data amount,
unique text, and subject diversity are separate experimental variables.

The local project has already consumed its independent S21 session-2 comparison.
Tuning a larger model on source validation and then reusing session 2 would not
create new generalization evidence.

Roadmap response:

- Loop 26 asks one narrow validation-only neural question with the existing
  small-model class;
- Loop 27 identifies and preregisters a genuinely fresh holdout before any
  acquisition;
- Loop 28 opens one fresh transfer test only after the complete decision rule
  is frozen;
- Loop 33 separates hours, trials, repetitions, and unique sentences in a
  bounded scaling curve.

## Finding 3: Language And Neural Contributions Must Be Separable

[Brain2Qwerty v1](https://www.nature.com/articles/s41593-026-02303-2.pdf)
shows that prompted typing produces strong motor-related signals and that a
language model can substantially change sentence errors. Brain2Qwerty v2 goes
further by comparing the full system with a condition that removes MEG tokens
from the language-model input. Its paper also shows that fluent generation can
improve WER or semantic metrics while making character-level errors worse.

A single final string therefore cannot establish that the brain signal caused
an improvement. A credible result needs encoder-only output, a no-signal prior,
neural-token ablation, corrupted-signal controls, and identical evaluation
membership.

Roadmap response:

- Loop 31 makes neural contribution a dedicated ablation gate;
- Loop 35 blocks neural claims when timing or peripheral channels explain the
  result;
- Loop 44 refuses to promote a performance claim without its comparator and
  evidence cohort.

## Finding 4: Transfer And Calibration Are Different Claims

Brain2Qwerty v2 reports substantial participant variability and identifies
cross-subject transfer or self-supervised pretraining as priorities. It also
states that its healthy-volunteer typing protocol does not answer the patient
case in which physical keypresses may be unavailable during training or
finetuning.

This creates four distinct claims:

1. same-session held-out text;
2. same-person cross-session transfer;
3. unseen-person zero-shot transfer;
4. unseen-person performance after a declared calibration budget.

NeuroDecodeKit must never report claim 4 as claim 3 or healthy prompted typing
as no-keypress communication.

Roadmap response:

- Loop 28 reports each transfer level separately;
- Loop 32 measures calibration items, minutes, compute, and no-harm behavior;
- Loop 35 keeps the no-keypress translation problem visible rather than
  assuming it away.

## Finding 5: Sensor Reduction Is Not Portable-Hardware Qualification

Brain2Qwerty v2 includes random sensor-count ablations and discusses OPM-MEG as
a future direction. Its primary experiment still uses a 306-sensor cryogenic
MEG system, and the paper frames low-channel OPM sentence decoding as an open
question. A random subset of cryogenic MEG channels does not reproduce OPM
noise, placement, motion, reference, shielding, bandwidth, firmware, or clock
behavior. EEG is a separate modality again.

Roadmap response:

- Loop 29 builds a modality-specific requirement matrix;
- Loop 36 preserves geometry, reference, units, and missing-channel identity;
- Loop 42 can qualify one named device and firmware only after replay and
  privacy gates pass.

## Finding 6: Reproducibility Must Include Environment And Runtime

The [MOABB benchmark](https://arxiv.org/abs/2404.15319) evaluates 30 pipelines
across 36 public EEG datasets and explicitly includes statistical comparison,
runtime, and environmental considerations. Its results also reinforce that
deep-learning competitiveness depends on data volume and that participant and
dataset variation matter.

NeuroDecodeKit should not build a broad EEG leaderboard from one prompted-
typing file. It should adopt MOABB's reproducibility posture: exact task
cohorts, environment capture, transparent baselines, statistical uncertainty,
and resource reporting.

Roadmap response:

- Loop 33 reports sample efficiency instead of only a best score;
- Loop 39 defines semantic versus numerical cross-machine reproduction;
- Loop 43 asks an independent contributor to reproduce a bounded artifact.

## Finding 7: Timing Domains Cannot Be Collapsed

[Lab Streaming Layer's time-synchronization documentation](https://labstreaminglayer.readthedocs.io/info/time_synchronization.html)
distinguishes sample timestamps from clock-offset measurements and says
synchronization is not performed by default. It also distinguishes online low
latency from applications that require synchronized event timing. Offline
import can use the full recording to correct clocks and smooth jitter, while a
causal online path cannot silently borrow that future information.

Roadmap response:

- Loop 25 registers causal preprocessing and event behavior;
- Loop 41 propagates raw, corrected, and arrival clocks separately;
- Loop 42 measures only the device and host timing boundaries it can observe;
- Loop 44 blocks an end-to-end latency claim unless every stage is measured.

## Finding 8: Derivatives Need Source-Bound Provenance

The [BIDS derivatives specification](https://bids-specification.readthedocs.io/en/stable/derivatives/introduction.html)
requires derivative datasets to remain distinguishable from source data and
defines machine-readable provenance. The current
[`dataset_description.json` specification](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/dataset-description.html)
includes `GeneratedBy` and `SourceDatasets` fields for the process and source
datasets.

NeuroDecodeKit already records source, split, configuration, and payload hashes.
The next useful interoperability step is a standards-aware derivative export
that preserves those fields without copying or redistributing raw recordings.

Roadmap response:

- Loop 37 creates a tiny synthetic BIDS-derivative interface;
- Loop 38 adds lifecycle and redaction controls;
- Loop 43 uses the derivative and report contract for independent reproduction.

## Finding 9: Neural Data Needs An Explicit Privacy Lifecycle

[User Identity Protection in EEG-based Brain-Computer Interfaces](https://arxiv.org/abs/2412.09854)
reviews identity leakage from EEG representations across BCI workflows. The
[NIST Privacy Framework](https://www.nist.gov/privacy-framework/privacy-framework)
provides a risk-management structure for identifying data, governing
processing, controlling access, and communicating privacy risk.

Local-only storage is helpful but incomplete. Temporary arrays, logs, absolute
paths, backups, embeddings, device serials, and deletion behavior also need an
owner and policy.

Roadmap response:

- Loop 38 inventories and tests the complete local lifecycle;
- Loop 42 makes device locality, consent, and retention qualification gates;
- Loop 43 forbids neural-recording uploads in the reproduction path.

## Finding 10: Confidence And Packaging Need Their Own Gates

[Selective Classification for Deep Neural Networks](https://arxiv.org/abs/1705.08500)
formalizes the tradeoff between coverage and risk when a model can abstain.
That framing is useful only if thresholds are selected without the final test
and the sample size supports the claim.

[ExecuTorch](https://docs.pytorch.org/executorch/stable/index.html) provides an
edge-oriented export/runtime stack plus profiling, debugging, operator, and
memory-planning tools. It is a candidate only after a frozen model and runtime
reference exist; exporting a model is not evidence of hardware usefulness.

Roadmap response:

- Loop 34 exposes confidence only if it ranks independent errors;
- Loop 40 evaluates one chosen edge backend against a frozen reference;
- Loop 44 keeps packaging evidence separate from neural, device, and real-time
  claims.

## Finding 11: Release Documentation Is Part Of The Scientific Result

[Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) proposes
documenting intended use, evaluation conditions, performance variation, and
limitations. [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
similarly covers motivation, composition, collection, recommended use, and
maintenance.

NeuroDecodeKit already treats negative results and proof labels as first-class.
The final loop should turn those records into a release decision that can
promote an engineering capability while leaving a scientific claim parked.

Roadmap response:

- Loop 43 tests whether an outsider can reproduce the documented artifact;
- Loop 44 creates the evidence matrix, cards, claim diff, and release decision.

## Prioritization Method

Each proposed loop was scored qualitatively against six questions:

| Criterion | High-value meaning |
|---|---|
| Missing claim | Answers a claim the current repo explicitly cannot make |
| Falsifiability | Has a primary threshold and a real stop rule |
| Fresh information | Avoids reopening a consumed evaluation |
| Reuse | Strengthens multiple later loops or contributor workflows |
| Boundedness | Fits one-thread, explicit-byte, optional-dependency discipline |
| Claim safety | Makes neural, modality, latency, privacy, or device boundaries clearer |

P0 loops protect the evidence chain or decide whether a predictive branch
deserves to continue. P1 loops add high-leverage translation, reliability, or
reproduction capability. P2 loops depend on earlier evidence and must not jump
the queue merely because they make a better demo.

## Why This Order

```text
causal correctness
  -> validation-only neural gate
  -> fresh holdout registration
  -> transfer decision
  -> neural/peripheral attribution
  -> sample efficiency and confidence
  -> provenance, privacy, and cross-machine reproduction
  -> replay-to-token integration
  -> one-device qualification
  -> independent reproduction
  -> claim promotion or hold
```

The order is a claim graph, not a promise that every branch proceeds. A failed
Loop 26 can park real-model scaling while provenance, privacy, and contributor
work continue. A failed Loop 41 blocks live/device work without invalidating
the offline cache interfaces. A negative Loop 42 remains a useful qualification
result if it is measured and preserved.

## Decision

Create Loops 25-44 as a detailed planning-only roadmap with five phases of four
loops. Every loop starts `Not Started`, `execution_authorized: false`, and
`proof_posture: planned_not_authorized`. The current numbered gate remains Loop
24, and RW3 Stage A remains a separate decision.

No result, runtime, data access, model execution, training, or device behavior
is established by this research pass.

## 2026-07-12 Status Addendum

The roadmap's initial planning decision above is preserved as historical
provenance. The current numbered gate has since advanced to Loop 25 planning:
Loop 24 is parked, and Loop 25 research plus preregistration are frozen at
`a36d97b` with green CI. The separate authorization request remains false, no
Loop 25 runtime or fixture exists, and Loops 26-44 remain `Not Started`.

This addendum changes tracker state only. It does not upgrade any primary-source
finding or authorize execution.
