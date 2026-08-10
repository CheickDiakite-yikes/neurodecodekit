# WO9R Low-Frequency Cohort Confirmation Result

Date: 2026-08-10

Status: **Complete and consumed at `WO9R-R3`; no rerun or post-target update.**

Public aggregate result:
`registries/physionet_low_frequency_cohort_confirmation_result.v0.json`

Result file SHA-256:
`d6cda8b4ce5f6da7add4a78ac8b1e74587cd8ab8eacf0dce8b806c076e85699a`

## Bottom Line

The frozen test found reproducible held-out **task information** in both motor
execution and motor imagery across the fresh S004-S015 cohort. Execution
passed every H1 gate at 123/180 correct, pooled balanced accuracy `0.680975`,
and macro-participant balanced accuracy `0.682292`. Imagery passed every H2
gate at 131/180 correct, pooled balanced accuracy `0.728014`, and macro-
participant balanced accuracy `0.728423`.

This is a positive scientific result within the registered ceiling: the
prespecified low-frequency representation carries held-out left/right task
information across twelve additional EEGMMIDB participants and across both
execution and imagery modes.

It is not evidence of a brain-specific motor signal. The motor-compatible
localization gate failed, several cue/frontal controls failed, and the frozen
router returned `WO9R-R3` rather than `WO9R-R4`.

## Evidence Order

The combined run-11 execution and run-12 imagery prediction freeze was
committed at `8cd45d74dfa3517ae53c1427a0eb06e27ad3c870`. CI
`31360781199` passed Base Python job `93369101655` and Optional Neuro Readers
job `93369101696` before the isolated scorer opened the same sealed 360-target
artifact once.

The scorer verified every private prediction hash and event/participant/run
identity, delivered the 360 targets once, applied the frozen router once, and
wrote the 8,208-byte aggregate result. Final-target deliveries and scoring
events are exactly one each. Post-target fits, selections, threshold changes,
channel changes, control changes, retries, and reruns are zero.

## Primary Gates

### H1: Execution confirmation passed

| Measure | Frozen gate | Observed |
|---|---:|---:|
| Correct events | >=117/180 | **123/180** |
| Pooled balanced accuracy | >=0.650 | **0.680975** |
| Macro-participant balanced accuracy | >=0.625 | **0.682292** |
| Participants above chance | >=9/12 | **9/12** |
| One-sided participant sign-flip p | <=0.010 | **0.002930** |
| Pooled margin over no-signal | >=0.100 | **0.190252** |
| Macro margin over no-signal | >=0.100 | **0.182292** |

The execution no-signal prior was 89/180, pooled balanced accuracy `0.490722`,
and macro balanced accuracy `0.500000`.

### H2: Imagery robustness passed

| Measure | Frozen gate | Observed |
|---|---:|---:|
| Correct events | descriptive | **131/180** |
| Pooled balanced accuracy | >=0.600 | **0.728014** |
| Macro-participant balanced accuracy | >=0.600 | **0.728423** |
| Participants above chance | >=8/12 | **12/12** |
| One-sided participant sign-flip p | <=0.050 | **0.000244** |

The imagery no-signal prior was 92/180, pooled balanced accuracy `0.507411`,
and macro balanced accuracy `0.500000`.

### Cross-task transfer was also positive

These arms were registered as diagnostics, not rescue gates:

| Direction | Correct | Pooled BA | Macro BA | Participants above chance | p |
|---|---:|---:|---:|---:|---:|
| Execution-trained -> imagery | 131/180 | **0.728261** | **0.729167** | 12/12 | 0.000244 |
| Imagery-trained -> execution | 125/180 | **0.695077** | **0.696429** | 11/12 | 0.000732 |

The bidirectional transfer strengthens the task-information result, but it
does not identify the physical source of that information.

## Why The Maximum Gate Failed

### H3: Motor-compatible localization failed

The central sensorimotor model itself was above chance at 117/180 and pooled
balanced accuracy `0.647575`. That was not enough. The frozen gate required
central channels to exceed the strongest frontal/occipital/asymmetry proxy by
at least `0.05` in pooled and macro balanced accuracy.

The strongest pooled proxy was frontal at `0.671821`, so the observed central
minus proxy margin was **`-0.024245`**, not `+0.05`. The paired participant
sign-flip p-value was `0.713867`, not <=`0.05`.

The independent lateralization assay also failed: only 5/12 participants moved
in the registered direction, with one-sided p=`0.706299`. Therefore the result
does not support motor-compatible central localization.

### Mandatory controls failed

The most informative failure was the early cue window:

| Condition | Pooled BA | Frozen ceiling | Decision |
|---|---:|---:|---|
| Early cue, 0 to +1 s | **0.762865** | <=0.600 | Failed |
| Frontal proxy | **0.671821** | <=0.600 | Failed |
| Frontal asymmetry | **0.661677** | <=0.600 | Failed |
| Pre-cue, -2 to 0 s | 0.498516 | <=0.600 | Passed |
| Timing only | 0.491712 | <=0.600 | Passed |
| Label derangement | 0.512123 | <=0.600 | Passed |
| One-trial displacement | 0.402647 | <=0.600 | Passed |
| Channel derangement | 0.502350 | <=0.600 | Passed |

The two participant-specific no-signal priors had macro balanced accuracy
exactly `0.5`, but their pooled values were `0.490722` and `0.507411`. The
frozen control required both pooled and macro values to equal `0.5` exactly,
so those components also failed. This exact-equality behavior is preserved as
registered; it does not change the route because localization and the strong
early/frontal controls independently fail.

## Interpretation

The positive result is real but narrower than “neural motor decoding.” The
model generalizes task labels across held-out runs, twelve new participants,
execution, imagery, and both cross-task directions. At the same time, the
early cue window outperforms the primary execution window, frontal information
is at least as strong as central information, and the lateralization assay is
negative.

The most plausible next hypothesis is therefore that visual cue processing,
cue-locked eye activity, or another broadly distributed task response carries
substantial information. The current data lack dedicated EOG, EMG, measured
movement onset, and a cue-neutral condition, so those alternatives cannot be
separated here. Scaling the same classifier would not answer that question.

## Resource And Privacy Closeout

- Acquisition: 72 files, 184,252,032 payload bytes, 518.051205 seconds,
  73,089,024-byte peak RSS, no EDF interpretation.
- Target-blind analysis: 1,080 events, 144 fits, 216 prediction sets,
  19.864386 seconds, 303,153,152-byte peak RSS, 4,206,464 private bytes.
- Scoring: one 360-target delivery, one score, zero post-target updates.
- CPU threads, workers, and numerical jobs: one each.
- No individual prediction, probability, target, participant metric, or
  participant outcome is committed.
- No additional payload, model, checkpoint, provider, language model, stream,
  device, hardware, retry, or rerun was used.

## Disposition

WO9R is complete and consumed at `WO9R-R3`. Do not rerun it, reopen its sealed
targets, change a threshold, add a model, or reinterpret `R3` as `R4`.

The needle-moving next experiment is not a larger classifier. It is a fresh,
cue-neutral or independently instrumented design with synchronized EOG/EMG and
measured movement onset, preregistered to distinguish cue/ocular information
from central motor physiology. Until such evidence exists, NeuroDecodeKit can
claim robust low-frequency task information in this EEGMMIDB protocol, not a
brain-specific motor or thought-decoding effect.

Engineering capability added: NeuroDecodeKit completed a leakage-resistant,
resource-bounded, multi-person public-EEG confirmation with a remotely green
prediction freeze and one aggregate score.

Scientific result established: the prespecified low-frequency representation
contains held-out left/right task information across twelve fresh participants
and both execution and imagery, while motor-compatible localization and the
confound-control conjunction were not established.
