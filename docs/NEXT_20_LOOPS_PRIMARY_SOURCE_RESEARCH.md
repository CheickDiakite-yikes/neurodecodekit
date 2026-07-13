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
cross-subject transfer or self-supervised pretraining as priorities. Its joint
model trains on all nine participants and uses a participant-index-conditioned
affine layer. Its leave-one-out comparison excludes the target participant
during pretraining but then finetunes on that participant. This is valuable
supervised calibrated transfer evidence, not strict unseen-person zero-shot
evidence. The paper also states that its healthy-volunteer typing protocol does
not answer the patient case in which physical keypresses may be unavailable
during training or finetuning.

This creates four distinct claims:

1. same-session held-out text;
2. same-person cross-session transfer;
3. unseen-person zero-shot transfer;
4. unseen-person performance after a declared calibration budget.

NeuroDecodeKit must never report claim 4 as claim 3 or healthy prompted typing
as no-keypress communication.

Roadmap response:

- Loop 28 reports each transfer level separately and treats unlabeled target-
  corpus adaptation as transductive rather than strict zero-shot;
- Loop 32 measures calibration items, minutes, compute, and no-harm behavior;
- Loop 35 keeps the no-keypress translation problem visible rather than
  assuming it away.

The dedicated Loop 28 research pass now sharpens this into one final-only rule.
S25 session 2 block 2 remains a zero-calibration T2 candidate: at least 48
eligible unique rows, at least 0.05 absolute macro sentence-CER improvement
over the frozen source-train-only prior, a one-sided paired randomization result
at `p <= 0.05` using 65,535 frozen assignments plus the observed assignment,
and a strict win over zero-signal, channel-derangement, and time-displacement
controls. Any tie, missing field, access violation, or cap failure parks the
claim. A calibrated curve requires a different physically separated design.
See `docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop28_research_boundary.v0.json`.

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
Loop 24 is parked. Loop 25's original preregistration at `a36d97b` was
superseded before authorization by the source-audited anti-alias amendment at
green commit `b6b92d8`. The current v1 request remains false, seeds 2501/2502
are unopened, and no Loop 25 coefficient, runtime, or fixture exists. Loop 26
planning research is complete while its experiment remains `Not Started`;
Loop 27 metadata research, Loop 28 transfer research, and Loop 29 portability
planning research are also complete while their experiments remain `Not
Started`; Loop 30 interaction research, Loop 31 attribution research, and Loop
32 calibration research are also complete while their experiments remain `Not
Started`; Loop 33 planning research is complete while its experiment remains
`Not Started`; Loop 34 confidence research is complete while its experiment
remains `Not Started` and confidence is unavailable; Loop 35 confound research
is complete while its experiment remains `Not Started`; Loop 36 geometry/
reference research is complete while its experiment remains `Not Started`;
Loop 37 BIDS derivative/provenance research is complete while its experiment
remains `Not Started`; Loops 38-44 remain `Not Started`.

The detailed source trace and design correction live in
`docs/LOOP_25_ANTI_ALIAS_AUDIT.md`. This addendum does not authorize execution
or upgrade the amended protocol into a filter, neural, decoding, or latency
result.

## 2026-07-12 Loop 26 Research Addendum

Loop 26 planning research is now complete at commit `03605c5`, without opening
real-cache contents, targets, a checkpoint, a model, training, source
validation predictions, consumed source test, or consumed session 2. The
experiment remains `Not Started`; no preregistration or authorization sentence
exists, and all 14 `authorized_now` fields in
`registries/loop26_research_boundary.v0.json` are false.

The local evidence has one 55/6/5 source split from one person/session. The six
reserved validation sentences permit exactly `2**6 = 64` paired sign
assignments, with minimum attainable two-sided p `0.03125` when all six paired
differences are nonzero. That resolution can support a narrow same-source
validation decision, not source-test, cross-session, unseen-person, modality,
device, population, real-time, assistive, or clinical claims.

The smallest future candidate recommendation preserves the existing 2,908-
parameter real CTC architecture but replaces symmetric kernel-3 padding with
two left-context samples and zero right context. A 2,884-parameter pointwise
linear CTC is the nearly matched signal comparator. Required future controls
are the train-only no-signal prior, zero validation signal, one target
derangement, frozen channel derangement, nonwrapping zero-filled time
displacement, and the linear comparator. These are recommendations only; no
seed, threshold, model, transform, or access sequence is frozen.

The primary-source trace also prevents a misleading shortcut: the official
Brain2Qwerty v2 reference is a whole-sentence, noncausal, GPU-scale Conv plus
Conformer plus CTC/contrastive/LLM system. Its evaluation lessons are relevant,
but its architecture and reported results are not a local causal template or a
result on NeuroDecodeKit's six rows. The exact sources and future
preregistration prerequisites are in
`docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md`.

## 2026-07-12 Loop 27 Research Addendum

Loop 27 planning research is green at commit `b3d61b6`, without downloading or
opening a candidate payload. A one-thread pinned Hub metadata pass examined 315
MEG entries in 3.10 seconds wall with 63,766,528-byte peak RSS, found 23 strict
single-FIF/log pairs and 16 eligible pairs, and selected SpanishBCBL S25 session
2 block 2 as the smallest eligible same-modality/task candidate.

The selected raw FIF and protected MAT log total exactly 1,009,939,983 bytes,
leaving 63,801,841 bytes below a future 1 GiB cap. Their official Git blob, LFS
SHA-256, Xet, and last-commit identities are frozen in
`registries/loop27_research_boundary.v0.json`. The MAT path already exists
locally at the expected size, but its payload was neither hashed nor opened;
the raw FIF is absent. Local presence is not provenance proof or permission to
inspect content.

Selection required the prompted-typing MEG cohort, one primary FIF without a
split continuation, and one matching log. Published aliases were
canonicalized; the observed S5/S10/S21 person and consumed S7 were excluded.
S23 was smaller but rejected because the official dataset card excludes that
participant for a metallic implant. S20 remains task-matched EEG and therefore
a separate RW4 question rather than a MEG transfer holdout.

S25 is only a metadata candidate. Exact channel order, geometry, performed
trials, unique sentences, source overlap, and external target-viewing history
remain unavailable. A future final-only recommendation assigns zero S25 rows
to training, validation, or calibration, requires at least 48 performed unique
rows as a pragmatic retention floor rather than a power claim, and opens every
eligible row once only after source-model, control, target-isolation, and Loop
28 decision hashes are frozen.

All 18 authorization fields are false. No Loop 27 preregistration, acquisition
request, download selection, authorization sentence, local MAT hash, FIF
header, signal, target, model, training, final open, or backup substitution
exists. Exact research and source links are in
`docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md`.

## 2026-07-12 Loop 29 Research Addendum

Loop 29 planning research is complete while the experiment remains `Not
Started`. The primary-source review keeps cryogenic MEG, OPM-MEG, scalp EEG,
and non-neural wearables in four separate profiles. It selects scalp EEG as the
immediate local-first accessibility lane, OPM-MEG as a same-modality partner/
lab lane, and cryogenic MEG as the scientific reference. Brain2Qwerty v2's
random 76/153/230-channel cryogenic subsets are model sensitivity evidence,
not OPM-MEG or EEG qualification.

The machine boundary freezes 15 cross-modality requirements, six qualification
levels, 12 future device-packet gates, 18 source bindings, and 24 false
authorization fields. It distinguishes task evidence, units, filters,
reference, geometry, field control, contact/fit, motion and peripheral
artifacts, clocks, packets, local export, privacy, licensing, repeated sessions,
compute, and claim scope. Home EEG recording mechanics do not establish home
text decoding; OPM wearability does not establish ordinary-home operation.

The user's additional 5-10 GB allowance is recorded as a preferred
5,000,000,000-byte and absolute 10,000,000,000-byte incremental capacity
envelope, not download permission. The exact future S20 EEG and S25 MEG bundles
total 1,106,030,247 bytes, leaving 3,893,969,753 bytes below the preferred
ceiling. This research downloaded zero payload bytes and opened no real header,
signal, target, consumed evidence, model, training path, SDK, socket, stream,
device, partner session, or hardware operation. Exact sources and boundaries
are in `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop29_research_boundary.v0.json`.

## 2026-07-12 Loop 30 Research Addendum

Loop 30 planning research is complete while the target-free local replay
experiment remains `Not Started`. Brain2Qwerty v2 provides continuous
asynchronous decoding, but its published architecture still uses an entire
sentence and explicitly leaves fully real-time low-latency operation to future
work. Local Loop 21 evidence proves a causal producer only; Loop 23 shows that
a zero-revision partial trace can still be wrong. The interaction must therefore
keep asynchronous, causal producer, causal decoder, replay paced, live source,
and end-to-end latency as separate properties.

The machine boundary freezes four source modes, a 30-field deterministic
target-free trace, nine clock domains, six latency claim levels, 18 future
requirements, 30 refusals, 16 source bindings, and 30 false authorization
fields. Stability remains descriptive rather than correctness or confidence;
finalization is explicit; backend, source, browser, and user-observed clocks
cannot be subtracted without an origin mapping.

The future interface must bind exactly to `127.0.0.1`, disable sharing,
analytics, monitoring, uploads, broad paths, service workers, and external
traffic, and use one thread and worker. Browser QA must record requests,
responses, WebSockets, pages, long tasks, Event Timing availability, console
errors, screenshots, and overlap/blankness. Incremental status uses accessible
status/log semantics without focus theft or forced autoscroll.

No seed, trace, payload, UI, server, browser run, consumed artifact, real-data
read, target, model, training, calibration, SDK, socket, stream, live source,
device, or hardware operation occurred. Exact primary sources and boundaries
are in `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop30_research_boundary.v0.json`.

## 2026-07-12 Loop 31 Research Addendum

Loop 31 planning research is complete while its neural-attribution experiment
remains `Not Started`. The project currently has two negative real predictive
comparisons: the consumed S21 session-2 MEG model reaches CER `0.917949` versus
`0.775458` for its no-signal prior, and the consumed S7 EEG classifier reaches
accuracy `0.009091` versus `0.122727` for its prior. The new boundary preserves
those results and designs the next attribution question without reopening them.

The future local encoder matrix has ten conditions: full signal, train-only
prior, zero signal, whole-item derangement, channel derangement, time
displacement, timing only, conditional context only, train-pairing
derangement, and a parameter-matched linear diagnostic. A separate contingent
five-condition LLM matrix distinguishes encoder output, language-prior gain,
Neuro Token drop, item-deranged Neuro Tokens, and an LLM-only prior. No local
LLM, v2 embedding, checkpoint, or data is assumed.

The six source-validation rows imply 64 exact sign assignments when every
paired effect is nonzero. The future recommendation is an intersection-union
gate: every applicable component must pass in the registered direction, the
primary prior comparison must pass its preregistered practical margin, and all
predictions must be hash-frozen before one target open. With two zero paired
effects, the minimum one-sided p-value becomes `0.0625`, so that component
cannot pass alpha `0.05`.

The claim ceiling is deliberate. A clean future local encoder gate may support
sensor-signal dependence for one person/session/task/split. It cannot establish
brain-specific neural origin until Loop 35 excludes EOG, EMG, motion,
environmental, timing, prompt, and action shortcuts. Language gain cannot be
credited to neural input, and a Neuro Token drop result is conditional on the
same CTC text and LLM rather than total neural contribution.

The machine boundary freezes 18 future requirements, 24 refusals, six claim
classes, 14 source bindings, and 19 false authorization fields. This research
used 16 public network operations including eight GitHub API requests and zero
protected cache/target/checkpoint/model/training/validation/LLM/S20/S25/stream/
device operations. Exact sources and boundaries are in
`docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop31_research_boundary.v0.json`.

## 2026-07-12 Loop 32 Research Addendum

Loop 32 planning research is complete while its fresh-person calibration
experiment remains `Not Started`. Brain2Qwerty v2 motivates person-specific
adaptation, but its leave-one-participant-out regime finetunes on the held-out
participant and therefore measures supervised calibrated transfer rather than
strict zero-shot transfer. CORAL and Euclidean Alignment motivate target-label-
free alignment, but target signal still influences the transform, so that lane
is transductive unlabeled calibration rather than zero-shot.

The future recommendation is one pointwise causal hidden affine transform over
the 16-wide proposed Loop 26 encoder: 16 scales plus 16 biases, exactly 32
target-trainable values, with all 2,908 source-model values frozen. Strict zero-
shot, unlabeled, label-light, and supervised modes remain separate. Their
nested sentence schedule is `0, 2, 4, 8, 16, 32`; label-light is capped at
eight labeled calibration sentences and supervised calibration at 32, with
all labeled selection rows also counted in human burden.

One future candidate needs physically distinct, row-disjoint, and semantic-
text-disjoint recordings with at least 32 calibration, 16 selection, and 48
final unique completed sentences. S25 block 2 remains Loop 28 final-only and
cannot be repurposed. Strict zero-shot final predictions must hash-freeze before
any target-person calibration access; one mode, adapter, and budget must then
freeze before every adapted/control final prediction and one final-target open.

The future decision recommends at least `0.05` macro-CER gain versus both frozen
zero-shot and the source-train-only prior, 65,535 paired random sign assignments
plus the observed assignment, and strict wins over every applicable identity,
normalization, and label-derangement control. The practical margins remain
unfrozen until preregistration. A selection gain cannot override final harm,
and one participant cannot support population inference.

The machine boundary freezes four modes, six budgets, six conditions, seven
claim classes, 20 future requirements, 26 refusals, and 22 false authorization
fields. This research used six public network operations, one thread/worker,
and zero candidate selection, protected payload, signal, target, checkpoint,
model, adapter-fit, training, control-prediction, final-evaluation, stream,
device, or hardware operation. Exact sources and boundaries are in
`docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop32_research_boundary.v0.json`.

## 2026-07-12 Loop 33 Research Addendum

Loop 33 planning research is complete while its bounded local data-scaling
experiment remains `Not Started`. Brain2Qwerty v2 reports a five-condition
log-linear relationship between asynchronous encoder CER and approximately
10-90 pooled recording hours, and a separate matched-trial comparison where
256 unique sentences outperformed 128 sentences repeated twice. Those findings
motivate measuring quantity and language variety separately; they do not make
the reported exponent transferable to one local person, six validation
sentences, and a 2,908-parameter encoder.

Two additional primary studies reinforce the boundary. A multi-dataset image-
decoding study reports strong within-subject recording-scale effects across 84
volunteers and 498 hours, but uses different tasks and modalities. A 175-hour
single-person overt-speech EEG study uses audio supervision, EMG/EOG handling,
large GPU compute, and increasing lexical overlap. Neither is local typed-
sentence MEG evidence. Learning-curve extrapolation is therefore treated as a
separate model-based procedure, not a free conclusion from six tiny points.

The future recommendation is a strictly nested
`8, 16, 24, 32, 44, 55` unique-source-sentence schedule, at most three fresh
optimization seeds and 18 candidate fits, one fixed Loop 26 architecture, and
a train-size-matched no-signal prior at every point. Unique sentences,
physical trials, valid seconds or minutes, cache bytes, runtime, RSS, and
artifacts remain separate axes. Hours cannot be reported below 3,600 valid
signal seconds, and CPU time cannot be called energy.

Access order is the central result. Loop 33 should freeze with Loop 26 before
the first source-validation target open. Every Loop 26/31/33 model, config,
prefix, prediction, and ledger must hash-freeze before all six shared targets
open once and every condition scores in one pass. If Loop 26 scores first, the
later curve is exploratory unless a new physical validation partition is
separately approved.

Current metadata does not establish eligible physical repetitions. Duplicated,
reweighted, augmented, or resliced arrays are not new acquisitions. A future
repetition-efficiency lane would require distinct performed recordings of the
same prompt, matched total physical trials, and its own metadata review,
preregistration, and authorization.

The machine boundary freezes four conditions, seven outcome classes, seven
claim classes, 20 future requirements, 30 refusals, and 23 false authorization
fields. This research used six public web operations, one thread/worker, and
zero protected cache/signal/target, model, training, scoring, S20/S25, stream,
device, or hardware operations. No acquisition is recommended now. Exact
sources and boundaries are in `docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop33_research_boundary.v0.json`.

## 2026-07-12 Loop 34 Research Addendum

Loop 34 planning research is complete while its confidence, abstention, and
revision experiment remains `Not Started`; confidence is unavailable. The
primary-source review separates selective error ranking, correctness-
probability calibration, fixed abstention operating points, conformal bounded-
risk control, revision stability, and product-visible confidence. Passing one
level does not imply another.

Selective prediction motivates risk at coverage, but abstain-all is a trivial
failure and therefore cannot pass. Conformal Risk Control motivates finite-
sample bounded-loss guarantees, while work beyond exchangeability requires
drift, grouping, and weighting assumptions to be explicit. Exact-sequence
0/1 error is the primary bounded loss. Raw CER remains unclipped; an optional
`min(raw_CER, 1)` loss must be separately named bounded CER.

Calibration research makes a raw score/probability firewall necessary. Log
score, entropy, margin, and prefix stability may rank outputs but are not
correctness probabilities. Probability claims require a mapping fit only on
calibration and independent Brier, log-loss, and reliability reporting. ECE is
secondary because its conclusion depends on binning and other measurement
choices. Legacy AURC is reported with limitations and cannot replace registered
working points or generalized-risk area.

The existing six source-validation sentences cannot provide independent
calibration, selection, and final roles, and remain reserved for the shared
Loop 26/31/33 event. Even six observed successes give an optimistic one-sided
95% upper error bound of approximately `0.393` before accounting for their
within-person dependence. No real confidence claim is available from current
partitions.

The future synthetic-interface recommendation uses fresh target-free
`128/64/256` calibration/selection/final sequence counts, grouped by generation
block and schedule. It compares eight score/control roles, selects exactly one
score and policy on selection, freezes all mappings, thresholds, predictions,
and hashes, then opens final targets once. A synthetic pass remains synthetic
and cannot establish real confidence.

The machine boundary freezes seven confidence semantics, eight score/control
roles, eight outcomes, seven claim classes, 20 future requirements, 30
refusals, and 26 false authorization fields. This research used five public web
operations, one thread/worker, and zero fixture generation, protected data,
target, checkpoint, model, confidence fit, scoring, product-confidence, S20,
S25, stream, device, or hardware operation. Exact sources and boundaries are
in `docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop34_research_boundary.v0.json`.

## 2026-07-12 Loop 35 Research Addendum

Loop 35 planning research is complete while its peripheral-confound experiment
remains `Not Started` and unauthorized. Brain2Qwerty v1 uses 500 ms windows
centered on known keypresses during physical typing, while Brain2Qwerty v2
removes explicit keypress timing at inference but still studies overt prompted
typing with audio, visual, motor, and somatosensory context. Neither protocol
by itself establishes that predictive sensor information originates in the
brain or transfers to no-keypress and patient use.

Primary MEG and EEG sources sharpen the risk. Small task-specific eye movements
can sustain MEG decoding; EMG and other artifact components can outperform the
intended signal in movement classification; overt movement can induce head,
jaw, neck, and muscle artifacts in MEG; and phantom-plus-EMG designs are used
to validate artifact-removal behavior. Artifact rejection and a channel label
therefore cannot replace synchronized comparator streams.

The machine boundary inventories ten confound classes and nine future stream
classes. Its 13-condition matrix includes no-signal and timing baselines,
direct-leak sentinels, ocular, distal/proximal muscle, motion,
audio/environment, all-peripheral, brain-sensor-only, train-only residualized,
and all-stream comparisons. Missing controls remain unavailable rather than
being imputed as zero or replaced by synthetic traces.

The recommended fresh protocol uses physically and semantically disjoint floors
of 32 calibration, 16 selection, and 48 final sentences. The strongest
peripheral condition and one brain candidate are selected before all final
predictions and hashes freeze. Final targets then open once. The primary
estimand asks whether all synchronized streams beat the strongest peripheral
condition; the secondary asks whether brain-sensor-only beats the strongest
nonbrain condition. Both recommend a 0.05 practical margin, 65,535 paired sign
assignments plus observed, an intersection-union decision, and a fail on ties.

Current S21/S7 evidence cannot provide the complete comparison. S21's committed
path has 102 magnetometers and timing but no synchronized EOG, EMG, gaze,
motion, or audio. The consumed S7 source named three ocular channels, but its
61-channel cache contains none. A future clean local result can therefore claim
at most incremental brain-sensor information beyond recorded controls for the
exact protocol. Absolute brain origin, language intent, no-keypress transfer,
patient benefit, population generalization, real-time behavior, portable
hardware, at-home use, and clinical efficacy remain unavailable.

Stage A synthetic interface work, Stage B fresh consented multimodal evidence,
and Stage C no-keypress/patient work are independent authorization decisions.
The boundary freezes 24 future gates, 32 refusal IDs, and 31 false authorization
fields. This research used six public web operations and zero protected data,
target, model, training, acquisition, S20/S25, stream, device, or hardware
operations. Exact sources and boundaries are in
`docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop35_research_boundary.v0.json`.

## 2026-07-12 Loop 36 Research Addendum

Loop 36 planning research is complete while its geometry/reference experiment
remains `Not Started` and unauthorized. BIDS separates ordered channel name,
type, and signal units from physical electrode identity and separately records
coordinate-system semantics and coordinate units. MNE distinguishes device,
head, and MRI frames and represents directional transforms explicitly. A bare
name, channel count, integer frame code, or visual layout is not equivalence.

EEG reference and MEG compensation/projector state are part of the signal
definition. Bad-channel and sensor-to-template interpolation estimate values
from other sensors and geometry. Rereference, compensation, signal scaling,
interpolation, and zero-fill therefore remain data-changing operations rather
than metadata identity.

The machine boundary freezes six representation layers, five modality
profiles, a 24-field future channel record, 12 operation classes, 16 fixture
families, eight outcomes, seven claims, 22 gates, 30 refusals, and 29 false
authorization fields. Aliases must be explicit, versioned, bijective, and
collision-free. Signal and coordinate units stay separate. A future rigid
transform must name direction, frames, origin/axes/handedness, pass
orthogonality and determinant `+1`, preserve orientation without translation,
and roundtrip synthetic positions within `1e-9 m`.

Current S21 metadata exposes channel names, types, positions in metres, integer
frame/unit codes, and coil types but lacks a complete exchange-frame,
orientation, transform, and compensation ledger. Loop 11's within-cache
spatial selection is not cross-device evidence. The consumed S7 cache lacks a
qualified measured electrode and acquisition-reference contract. No real
header, cache, or signal was opened for this research.

Future Stage A is target-free synthetic metadata only. A separately authorized
Stage B may inspect exact named headers under file/byte/privacy caps without
signals. Stage C is required for signal scaling, rereference, compensation, or
interpolation. The maximum future real-header claim is declared metadata
compatibility. Numerical compatibility, model transfer, device equivalence,
neural advantage, and scientific performance remain separate.

This research used three high-level public web operations, one thread/worker,
and zero fixture, protected header/signal/cache/target, transform, conversion,
rereference, interpolation, model, training, S20/S25, stream, device, or
hardware operations. Exact sources and boundaries are in
`docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop36_research_boundary.v0.json`.

## 2026-07-12 Loop 37 Research Addendum

Loop 37 planning research is complete while its BIDS derivative/provenance
experiment remains `Not Started` and unauthorized. Stable BIDS 1.11.1 requires
the derivative dataset envelope to identify the dataset, standard version, and
generating pipeline. File-level direct inputs use BIDS URIs resolved through
the current dataset or `DatasetLinks`. Relative source paths and `RawSources`
are deprecated, and required source metadata propagates only while still valid.

NeuroToken NPZ caches, NeuroDecodeKit split reports, report cards, and manifests
have no stable BIDS derivative suffix. BIDS permits additional/non-compliant
files, but a standards-valid envelope cannot make those payloads standard. The
future ceiling is therefore a validator-assessed BIDS envelope with explicitly
non-standard NeuroDecodeKit payloads. Validator success cannot establish
privacy, license, hash truth, cross-machine reproducibility, scientific
provenance, or decoding accuracy.

The machine boundary freezes six export layers, five artifact profiles, 15
stable-field mappings, 16 explicit NeuroDecodeKit extension fields, 20 future
fixture families, four separately authorized stages, eight outcomes, six
claims, 24 gates, 32 refusals, and 29 false authorization fields. Absolute
paths, usernames, traversal, case/identity collisions, overwrite, symlinks,
hardlinks, shared inodes, raw filenames/content copies, unknown payloads,
target/free-text leakage, incompatible licenses, incomplete privacy evidence,
and overclaiming all refuse.

The current tracked inventory contains zero neural/model binary candidate files
and zero such payload bytes. No artifact payload was opened. This research used
seven high-level public web operations, including two official GitHub
repository reads, and zero fixture, exporter, derivative tree, validator,
protected payload, raw copy, release, upload, model, training, stream, device,
or hardware operations. Exact sources and boundaries are in
`docs/LOOP_37_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop37_research_boundary.v0.json`.

## 2026-07-13 Loop 38 Research Addendum

Loop 38 planning research is complete while its privacy/lifecycle experiment
remains `Not Started` and unauthorized. NIST Privacy Framework 1.0 is the
stable pin because 1.1 remains an initial public draft. NISTIR 8062 provides
predictability, manageability, and disassociability; PRAM structures the risk
analysis; SP 800-88 Rev. 2 prevents an application-level path receipt from
being relabeled physical-media sanitization.

Published EEG identity results justify treating raw signals, derived arrays,
embeddings, Neuro Tokens, stable hashes, and individual rows as potentially
linkable. They do not establish a local identity attack result. Open Brain
Consent is a sharing-consent template, not local legal clearance. GitHub's
history guidance makes worktree deletion, `.gitignore`, and a clean current
tree insufficient evidence for clones, forks, pull-request refs, LFS, CI, or
other remote copies.

The machine boundary freezes five sensitivity levels, eight artifact classes,
ten lifecycle surfaces, 12 sensitive-field classes, 12 threat scenarios, five
deletion-receipt levels, 24 fixture families, four separately authorized
stages, eight outcomes, six claims, 26 gates, 36 refusals, and 32 false
authorization fields. Consent, license, de-identification, redaction, deletion,
and sharing authority remain separate decisions. Unknown copies remain
`unresolved` rather than being inferred clean.

The local metadata-only audit found zero current tracked neural/model candidate
files and bytes and zero candidate paths across all-ref Git history. It opened
no ignored cache, signal, embedding, target, consent, or protected MAT payload.
This research used six high-level public web operations, eight official or
primary source page opens, one thread/worker, and zero fixture, scanner,
deletion, history rewrite, identity attack, model, training, release, upload,
stream, device, or hardware operations. Exact sources and boundaries are in
`docs/LOOP_38_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop38_research_boundary.v0.json`.

## 2026-07-13 Loop 39 Research Addendum

Loop 39 planning research is complete while its cross-machine reproducibility
experiment remains `Not Started` and unauthorized. ACM terminology separates
same-team repeatability, different-team same-setup reproduction, and different-
team different-setup replication. Reproducible Builds adds a narrower bitwise
artifact definition tied to the same source, environment, and instructions.
Neither definition permits one maintainer's green CI to stand in for
independent reproduction or scientific replication.

The current audit found a meaningful support gap. The project declares Python
3.10-3.12 and OS Independent, but public CI runs only `ubuntu-latest` with
Python 3.12. There is no macOS cell, exact OS pin, dependency lock,
environment-manifest schema, central tolerance registry, or wheel/sdist
reproducibility job. Two tests import standard-library `tomllib`, which is not
available in Python 3.10 without a fallback. Python 3.10 therefore remains
unqualified until the complete suite runs or the support declaration changes.

The machine boundary freezes seven qualification levels, 18 environment
identity fields, eight output classes, six comparison classes, six required
future cells, 20 fixture families, four separately authorized stages, eight
outcomes, seven claims, 28 gates, 38 refusals, and 36 false authorization
fields. Exact IDs, timestamps, lengths, masks, splits, state, dtypes, shapes,
and discrete values stay exact. Floating fields require preregistered absolute,
relative, ULP, finite, and signed-zero policies; no global tolerance exists.

The future matrix covers Ubuntu 24.04 with Python 3.10/3.11/3.12 base, macOS 15
arm64 with Python 3.12 base, and separate Ubuntu/macOS Python 3.12 optional-
neuro cells. It is capped at two parallel jobs, one thread/worker per cell, 20
minutes, 1 GiB RSS, 4 MiB per cell, and 24 MiB total artifacts. Runtime and RSS
remain descriptive rather than semantic identity.

This research used six public web operations and eight official or primary
page opens. It created zero fixture, manifest, matrix, lockfile, install,
package, upload, protected read, model, training, edge, stream, device, or
hardware operations. Exact sources and boundaries are in
`docs/LOOP_39_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop39_research_boundary.v0.json`.

## 2026-07-13 Loop 40 Research Addendum

Loop 40 planning research is complete while its edge-runtime packaging
experiment remains `Not Started` and unauthorized. The detailed source audit is
in `docs/LOOP_40_PRIMARY_SOURCE_RESEARCH.md`; the dependency-free contract is
`registries/loop40_research_boundary.v0.json`.

The retained Loop 22/24 reference is a 1,130-parameter float32 causal producer
and diagnostic probe with 5,210 registered numeric bytes. The torch graph is
only Linear/GELU computation: normalization, stream state, timestamps, frame
scheduling, decoder behavior, and app integration remain host responsibilities.
The relevant Loop 39 matrix has not run, so the reference is not eligible for
package qualification.

Official documentation supports four future profiles:

- [ExecuTorch](https://docs.pytorch.org/executorch/stable/getting-started.html)
  with XNNPACK is the leading research candidate because the source is PyTorch
  and the stack exposes target lowering, delegates, profiling, memory planning,
  and mobile bindings;
- [ONNX Runtime Mobile](https://onnxruntime.ai/docs/tutorials/mobile/) offers a
  cross-platform CPU/XNNPACK path and reduced operator builds but adds ONNX/ORT
  conversion and compatibility boundaries;
- [LiteRT Torch](https://developers.google.com/edge/litert/conversion/pytorch/overview)
  offers direct `torch.export`-compliant conversion but still requires exact
  converter/runtime/operator and host-integration qualification;
- [Core ML Tools](https://apple.github.io/coremltools/docs-guides/source/target-conversion-formats.html)
  is Apple-specific, requires explicit input shape, and has newer float16
  defaults that cannot silently replace the retained float32 reference.

No backend is selected because no target OS, architecture, ABI, minimum
deployment target, or app envelope is named. The boundary freezes seven
qualification levels, six package layers, four backend profiles, 20 identity
fields, eight output classes, six comparison classes, 24 fixture families,
four separately authorized stages, 30 gates, 40 refusals, and 40 false
authorization fields. A future Loop 40 pass can establish at most parity and
measured resources for one exact named host or simulator. Physical devices
remain Loop 42 work; packaging cannot establish decoding or neural science.
