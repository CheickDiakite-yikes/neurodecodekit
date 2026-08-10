# PhysioNet Low-Frequency Cohort Confirmation Primary-Source Research

Date: 2026-08-09

Status: **Tier A research complete; cohort and hypothesis selected; no new EDF
payload acquired or opened; no experiment preregistered, authorized, or run**

Machine boundary:
`registries/physionet_low_frequency_cohort_confirmation_research.v0.json`

## Decision In One Sentence

The next public-data experiment should treat the Work Order 9 `0.5-4 Hz`
result as a prospective primary hypothesis on twelve untouched participants,
pair motor-execution and motor-imagery runs, and require accuracy,
participant-level replication, temporal controls, and central-over-cue-proxy
localization to route separately.

This lane is called **WO9R**. It is additive and does not renumber work orders
10-20, reopen Work Order 9, or unblock Loop 54-B.

## Why This Is The Right Next Experiment

Work Order 9 produced one strong but scientifically ambiguous observation. Its
prespecified whole-head low-frequency comparator reached `36/45` correct,
`0.800395` pooled balanced accuracy, `0.800595` macro-participant balanced
accuracy, and `p=0.000183` on held-out run 11 for S001-S003. The result was
frozen before final-target delivery and is genuine held-out task-information
evidence.

The same result also says why a larger model is not the next move:

- the selected `8-30 Hz` primary failed;
- the central sensorimotor model reached only `0.534585` balanced accuracy;
- the frontal/occipital proxy reached `0.624506` and beat the central model;
- the motor-physiology gate failed at `p=0.108337`; and
- the task displays a class-correlated left/right visual target without
  separately recorded EOG or EMG.

The immediate uncertainty is therefore not whether a transformer, foundation
model, or LLM can increase a score. It is whether the compact slow signal
replicates in new people and whether its spatial and temporal structure is
more compatible with sensorimotor activity than with a visual, ocular, timing,
or movement shortcut.

The S001-S003 result, its private outputs, and its final targets are consumed.
They may supply the aggregate hypothesis above, but they may not be reopened,
recomputed, mixed into training, or used to select a future threshold.

## Primary-Source Synthesis

### The source dataset provides a clean untouched cohort

The official PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0 page describes
64 EEG channels sampled at 160 Hz, 14 runs per participant, and 109 participant
folders. Unilateral execution and imagery use left/right visual targets. The
official mapping makes runs `03/07/11` repeated executed left/right fist runs
and runs `04/08/12` the corresponding imagined left/right fist runs. `T1` and
`T2` mean left and right only in these unilateral runs.

Source: [PhysioNet EEGMMIDB v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)

The next cohort is the contiguous, outcome-independent range `S004-S015`.
These twelve people do not overlap the consumed S001-S003 development cohort.
The six selected runs per person yield a prospective 72-EDF inventory. No
`.event` sidecar is needed because the EDF+ annotation channel contains the
same event information. Exact paths, byte sizes, and official SHA-256 values
must be frozen in a later acquisition contract before a payload request.

### Low-frequency EEG can contain movement-related potentials

Movement-related cortical potentials and contingent negative variation are
slow time-domain changes associated with preparation and execution, while
mu/beta desynchronization provides a distinct time-frequency view. A 34-person
study comparing visually instructed and cued unilateral movement reported
MRCP and ERD effects over C3, Cz, and C4 with distinct spatial patterns.

Source: [Combining Movement-Related Cortical Potentials and Event-Related
Desynchronization to Study Movement Preparation and Execution](https://doi.org/10.3389/fneur.2018.00822)

That literature makes the WO9 slow-potential result plausible. It does not
identify the source of this dataset's classifier score, and it does not justify
retrospective filtering, channel selection, or movement-intention wording.

### Visual cues can materially alter low-frequency movement decoding

A 2024 executed-movement study directly compared cue designs and self-paced
movement. Cue alignment changed MRCP shape, timing, topography, and
classification behavior; the authors explicitly warn that visual-cue activity
can obscure movement-related dynamics.

Source: [EEG Analyses of visual cue effects on executed
movements](https://doi.org/10.1016/j.jneumeth.2024.110241)

EEGMMIDB's left/right visual target remains visible during the task. Therefore
an execution score alone cannot distinguish motor activity from lateralized
visual processing or gaze behavior. An early cue window and separate frontal
and occipital proxy models are mandatory, not optional post hoc plots.

### Small systematic eye movements can masquerade as neural decoding

Mostert and colleagues showed that stimulus-specific eye movements could
contaminate multivariate neural decoding and support an apparently meaningful
result. Their task and modality differ from EEGMMIDB, but the methodological
lesson applies directly: task-correlated gaze must be considered during study
design, and a weak proxy cannot prove that ocular contamination is absent.

Source: [Eye Movement-Related Confounds in Neural Decoding of Visual Working
Memory Representations](https://doi.org/10.1523/ENEURO.0401-17.2018)

EEGMMIDB has frontal scalp channels but no dedicated EOG channel. WO9R can
measure an ocular-sensitive frontal asymmetry proxy; it cannot turn that proxy
into measured gaze or claim complete ocular removal.

### Execution and imagery provide a useful matched diagnostic

The official protocol repeats the same left/right target structure during
overt execution and imagined movement. A 28-person task-transfer study reports
that execution-trained EEG models can transfer to imagery, supporting a
prospective cross-task diagnostic.

Source: [Motor task-to-task transfer learning for motor imagery brain-computer
interfaces](https://doi.org/10.1016/j.neuroimage.2024.120906)

Imagery is not a cue-only negative control: it can itself contain motor-related
activity. However, it removes overt fist motion. Native and cross-task results
can therefore separate an execution-only effect from a task-mode-shared effect
while retaining explicit visual and ocular caveats.

## Prospective Cohort And Split

The future exact contract should freeze this inventory without substitution:

```text
participants:                  S004-S015 inclusive (12)
execution fit runs:            03 and 07
execution sealed-final run:    11
imagery fit runs:              04 and 08
imagery sealed-final run:      12
prospective EDF count:         72
event sidecars:                0
expected task events/file:     15, subject to fail-closed verification
expected fit events:           720
expected sealed-final events:  360
```

The participant and run are the grouping units. There is no row-random split.
Each participant receives a separate model. All run-11 and run-12 predictions,
including controls, must freeze before either final target set opens. Opening
one final set to revise the other is forbidden.

No participant, channel, epoch, or trial may be excluded from a predictive
analysis because of a target, prediction, or final outcome. Any input,
annotation, event-count, channel, geometry, or finite-signal mismatch parks the
one-shot execution without replacement.

## Frozen Primary Model Template

WO9R promotes no retrospective winner inside Work Order 9. It creates a new
prospective hypothesis by carrying the exact prespecified comparator forward
unchanged:

```text
reference:             instantaneous common average over all 64 retained EEG channels
filter:                fourth-order Butterworth 0.5-4 Hz, second-order sections
application:           causal continuous-run scipy.signal.sosfilt before epoching
decision window:       +1.0 through +3.0 seconds from cue onset
features/channel:      four consecutive 500 ms means plus one whole-window slope
feature dimension:     5C = 320 at C=64
classifier:            participant-specific LDA with fixed shrinkage 0.1
fit state:             designated fit runs only
right context:         0 seconds relative to the +3.0 second decision
selection candidates:  1
hyperparameter search: 0
```

This is cue-causal, not pre-movement and not asynchronous. Actual movement
onset is unavailable. No ICA, resampling, target-derived bad-channel removal,
evaluation normalization, pretrained model, deep network, language model,
provider, or foundation model belongs in this confirmation test.

## Four Prediction Questions

Every participant produces four frozen whole-head prediction sets:

1. **Execution native:** fit runs 03+07, predict run 11. This is the primary
   confirmation endpoint.
2. **Imagery native:** fit runs 04+08, predict run 12. This tests whether a
   matched task-mode signal also exists without overt movement.
3. **Execution to imagery:** fit runs 03+07, predict run 12. This measures
   cross-task transfer without adaptation.
4. **Imagery to execution:** fit runs 04+08, predict run 11. This measures the
   reverse transfer without adaptation.

Neither cross-task direction may update a model, threshold, channel set, or
normalizer on its destination run.

## Mandatory Localization And Confound Views

The same frozen low-frequency feature/classifier recipe should also produce:

- central sensorimotor-only predictions;
- frontal-polar ocular-sensitive predictions;
- occipital visual-sensitive predictions;
- a one-dimensional left-minus-right frontal asymmetry proxy;
- an early cue-window whole-head model;
- a pre-cue model;
- an event-index/timing-only model;
- a train-only no-signal prior;
- an all-zero final-signal prediction;
- a fixed train-label derangement;
- a fixed one-trial final-signal displacement;
- a fixed channel derangement; and
- a fixed left/right hemisphere swap.

Channel lists, asymmetry signs, windows, permutations, and seeds must be
literal in the future contract. The central, frontal, and occipital models use
fixed anatomical groups; they are not selected from data. The frontal proxy
is not EOG, and the occipital proxy is not a source-localization solution.

The physiology axis should replace the previous primary emphasis on mu/beta
with a low-frequency lateralized-potential assay aligned to the new
hypothesis. It should baseline against a fixed pre-cue interval and compare
contralateral with ipsilateral central channels. Mu/beta ERD may remain a
separate descriptive assay, but it cannot select or rescue the low-frequency
model.

## Recommended Frozen Gates

These values should become immutable in the later preregistration unless a
new primary-source or synthetic-qualification finding justifies a documented
change before any selected payload opens.

### H1: independent-cohort task confirmation

For the 180 expected execution-final events:

- at least `117/180` correct;
- pooled balanced accuracy at least `0.65`;
- macro-participant balanced accuracy at least `0.625`;
- at least `9/12` participants above `0.50` balanced accuracy;
- exact participant-level sign-flip `p <= 0.01` versus `0.50`; and
- pooled and macro margins of at least `0.10` over the train-only no-signal
  prior.

The participant-level test is decisive. Treating 180 correlated trials as 180
independent people is forbidden.

### H2: task-mode robustness

The imagery-native arm should require pooled and macro balanced accuracy at
least `0.60`, at least `8/12` participants above `0.50`, and an exact
participant-level `p <= 0.05`. Cross-task transfer is diagnostic and must be
reported in both directions; it cannot replace a failed execution-native
primary.

### H3: motor-compatible localization

The central execution model should reach at least `0.60` pooled and macro
balanced accuracy, exceed the strongest frontal, occipital, or frontal-
asymmetry proxy by at least `0.05`, and pass an exact paired participant-level
sign-flip test at `p <= 0.05`. The low-frequency central lateralization assay
should have its registered direction in at least `8/12` participants and pass
its paired sign-flip test at `p <= 0.05`.

The early-cue, pre-cue, timing-only, deranged-label, displaced-trial,
deranged-channel, and proxy models must remain below their frozen ceilings.
No single failed proxy proves a cortical source; the conjunction is required
only for the stronger motor-compatible route.

## Prospective Verdict Router

| Verdict | Frozen meaning | Maximum claim |
|---|---|---|
| `WO9R-R0` | Integrity, event, split, resource, access-order, or freeze gate fails | Invalid or incomplete registered execution |
| `WO9R-R1` | The execution-native low-frequency primary fails H1 | The three-person effect did not confirm under this frozen cohort test |
| `WO9R-R2` | H1 passes but task-mode or localization/confound gates fail | Low-frequency left/right task information confirmed in a new cohort, still cue/confound-compatible |
| `WO9R-R3` | H1 and H2 pass but H3 fails | Low-frequency task information is robust across execution and imagery, but motor localization remains unsupported |
| `WO9R-R4` | H1, H2, H3, and all negative controls pass | Multi-person, held-out, motor-compatible low-frequency EEG task effect within EEGMMIDB |

`WO9R-R4` is deliberately not brain-specific proof. The dataset still lacks
dedicated EOG/EMG, measured movement onset, a cue-neutral condition, a new
recording platform, and an independent research team. A future synchronized
EEG+EMG MRCP study remains the correct route for true pre-movement timing and
peripheral discrimination.

## Resource And Safety Envelope

The later acquisition and execution contracts should stay small:

- only 72 named EDFs from S004-S015 and six named runs;
- no `.event` sidecars or whole-dataset archive;
- expected payload below 256 MiB, with the exact byte total frozen before
  authorization;
- at least 20 GiB free disk before any new download or real execution;
- one CPU thread, one worker, and one numerical job;
- sequential participant/file traversal;
- at most 1 GiB peak RSS and 1,800 seconds for the model stage;
- at most 64 MiB private generated derivatives and receipts;
- no persistent process, retry, rerun, or post-final update; and
- no new broad dependency stack.

The existing 200 MiB isolated classical environment can be reused only after
its exact dependency identities are reverified. The user's 10 GiB data
allowance is a ceiling, not a target; this design should consume only a small
fraction of it.

## Required Evidence Order

1. Freeze exact public metadata, paths, sizes, SHA-256 values, and acquisition
   caps in a separate contract.
2. Commit, push, and obtain green CI for an all-false Tier C request packet.
3. Obtain the maintainer's exact acquisition/experiment decision.
4. Qualify downloader and analysis changes using generated fixtures and mocked
   network responses only.
5. Commit, push, and obtain green CI for the exact implementation.
6. Acquire and opaque-verify the exact absent bundle once.
7. Run one target-blind analysis, creating all native, transfer, localization,
   and control predictions while both final target sets remain sealed.
8. Commit and push one aggregate hash-only prediction freeze and require both
   CI jobs green.
9. Deliver and score the same run-11 and run-12 targets once, then apply the
   frozen router without update or rerun.

The acquisition and final scoring are Tier C. This research record authorizes
none of them.

## Current Access Ledger

This research pass used only public documentation, public metadata surfaces,
the committed aggregate Work Order 9 result, and tracked source code. It opened
no local PhysioNet bundle or private Work Order 9 artifact. It downloaded no
EDF, read no EDF header, annotation, event, sample, target, channel, or
geometry, created no split or derivative, imported or fit no model, made no
inference, scored no target, and used no provider, stream, device, or hardware.

Exact research-tool transfer bytes for public HTML, paper, and checksum
metadata are unavailable. EDF payload bytes and new local payload bytes are
exactly zero.

## Claim Boundary

Engineering capability added by this research result: NeuroDecodeKit now has
a falsifiable, resource-bounded route from its strongest real EEG lead to an
untouched-cohort confirmation with matched execution/imagery and explicit
cue, ocular, timing, and topographic diagnostics.

Scientific claim not established: no new participant payload or target was
opened and no model was run, so this planning result establishes no cohort
replication, brain-specific motor origin, unseen-person decoder, typing,
language or thought decoding, real-time behavior, portable hardware, home use,
assistive benefit, or clinical utility.
