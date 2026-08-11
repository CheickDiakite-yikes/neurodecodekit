# MARC-1 Multimodal Artifact-Resolved Movement Research

Date: 2026-08-11

Status: **Tier A primary-source research complete; no dataset payload, archive
member, signal, event, target, model, prediction, or score was accessed or
authorized**

Registry:
`registries/marc1_multimodal_artifact_resolved_movement_research.v0.json`

## Executive Decision

The next scientific lane is **MARC-1: Multimodal Artifact-Resolved Causal
Movement Qualification**.

Do not answer the positive-but-confounded WO9R result with a larger model. Test
the same compact causal low-frequency hypothesis against two complementary
public datasets:

1. **Freewill-23** supplies self-selected movement timing and target, four EOG
   channels, and synchronized wrist acceleration. It attacks visual-cue,
   ocular, and movement-onset ambiguity.
2. **Wrist-45** supplies eight forearm EMG channels and synchronized robotic
   encoder kinematics in tiny participant-level archives. It attacks muscle
   onset, movement onset, and storage ambiguity.

Neither source alone closes every confound. A positive scientific route
therefore requires the same frozen causal EEG family to survive both axes.
Passing only one axis is useful localization evidence, not a claim upgrade.

The tempting Aalborg self-paced hand dataset is not selected for execution.
Its scientific design is unusually good, but the public GitHub repository has
no declared license, the paper's data-availability statement says data are
available on request, and the linked Google Drive folder does not add an
explicit data license. Public visibility is not reuse permission.

This research used only public article, repository, and metadata surfaces. It
downloaded no EEG archive or member and opened no protected local path.

## Why This Is The Missing Comparison

WO9R established reproducible task information across twelve held-out people:
execution pooled balanced accuracy was `0.680975` and imagery was `0.728014`.
It did not establish motor-cortical origin. The early-cue condition was
stronger than the primary execution window (`0.762865`), the frontal proxy
outperformed the central subset (`0.671821` versus `0.647575`), and only 5/12
participants followed the registered physiology direction.

The scientifically useful question is no longer simply "can this model classify
the task?" It is:

> Does strictly pre-movement scalp EEG add held-out information beyond no-signal
> prevalence, elapsed time, measured eye activity, measured muscle activity,
> and measured movement onset?

That question gives every positive number a meaningful comparison. It also
turns a negative result into a diagnosis rather than another dead end.

## Primary-Source Findings

### Freewill-23: cue-reduced, ocular-instrumented onset axis

The 2025 Scientific Data descriptor reports 23 participants, 49 recordings,
and 6,808 reaching-and-grasping trials. Participants heard a generic trial
start cue, then freely chose both which of four cups to reach for and when to
begin within a 12-second interval. The target and movement onset were not
specified by the cue.

The source records 31 EEG channels, four EOG channels, one audio-trigger
channel, and three wrist-accelerometer axes on the same amplifier. Twenty-one
participants were sampled at 250 Hz and two at 1,000 Hz. The article provides
reviewed accelerometer-derived movement-onset indices. This is not a completely
cue-free recording, so every future negative window must be matched on elapsed
time from the generic audio cue.

Source: [A large electroencephalogram database of freewill reaching and
grasping tasks for brain machine interfaces](https://www.nature.com/articles/s41597-025-06039-9)

The official Figshare v1 metadata reports CC BY 4.0 and one monolithic ZIP:

```text
record:       28632599
DOI:          10.6084/m9.figshare.28632599.v1
file ID:      57518986
file:         Freewill_EEG_Reaching_Grasping.zip
bytes:        13,591,548,048
MD5:          3b7c3039c5c9fb6abf1429a830301711
```

The archive is larger than the maintainer's 10 GB incremental-data ceiling and
must never be downloaded whole. A future metadata gate may inspect only a
bounded ZIP central directory by exact HTTP byte ranges. It must park if the
server does not provide stable range semantics or if selected participant
members cannot fit the later frozen cap.

Metadata source: [Figshare record
28632599](https://api.figshare.com/v2/articles/28632599)

### Wrist-45: muscle-instrumented kinematic axis

The 2026 Scientific Data descriptor reports 45 participants with 320 wrist
pointing trials each. Eight central EEG channels and eight forearm EMG channels
were sampled together at 512 Hz. Robotic encoder values were synchronized into
the same recording and updated at 100 Hz. The four directional movements were
visually instructed, so this source cannot independently establish cue-neutral
decoding and has no dedicated EOG channel.

Its value is orthogonal: EMG and encoder streams permit a strict pre-muscle,
pre-kinematic exclusion test and an objective movement-onset audit.

Source: [An EEG-EMG-kinematics dataset from wrist pointing tasks for biomarker
research in neurorehabilitation](https://www.nature.com/articles/s41597-026-07287-z)

Official Figshare v3 metadata reports CC BY 4.0, 55 files totaling
`3,683,416,050` bytes, and participant-level archives. The smallest lexical
participant is already safely granular:

```text
record:       29666735
DOI:          10.6084/m9.figshare.29666735.v3
sub-01 ID:    62570743
sub-01 bytes: 33,690,749
sub-01 MD5:   6b01cf5bd30de0c670d2837d112a17fa
```

Metadata source: [Figshare record
29666735](https://api.figshare.com/v2/articles/29666735)

### Self-paced EEG/EOG/EMG source: scientifically preferred, legally parked

The 2023 Knowledge-Based Systems study recorded ten participants performing
self-paced hand opening and closing without timed movement cues. Nine central
EEG channels, one EOG channel, and forearm EMG were recorded on the same
amplifier at 1,200 Hz. EMG supplied movement-onset labels. The public Drive
layout is unusually efficient: the observed subject-00 files are individually
listed at approximately 3.7-12.6 MB.

Those properties make the source an excellent future replication candidate,
but not an executable one today. The linked repository reports no license and
the paper says data will be made available on request. MARC-1 records the source
as `license_unavailable_execution_parked`; it may be activated only after an
explicit data license or written reuse permission is preserved.

Sources:

- [Automated labeling and online evaluation for self-paced movement detection
  BCI](https://doi.org/10.1016/j.knosys.2023.110383)
- [Public companion repository](https://github.com/P9-MI-BCI/mind-reading-and-control)

## Frozen Scientific Hypothesis

The candidate hypothesis is deliberately sensor-level:

> A compact causal low-frequency EEG model contains held-out pre-movement
> information that exceeds matched no-signal and measured non-EEG controls on
> both a cue-reduced EOG-plus-acceleration axis and an EMG-plus-kinematics axis.

The null is that any apparent gain is explained by prevalence, elapsed time,
cue response, eye movement, muscle activity, kinematics, participant leakage,
or noncausal preprocessing.

MARC-1 does not hypothesize language, typing, imagined speech, thought content,
or clinical utility. No language model or foundation model belongs in the
evidence path.

## Common Causal Candidate

Both axes must use one frozen compact family, adapted only for source sampling
rate and declared channel availability:

- strictly past-only `0.5-4 Hz` features;
- train-only normalization and shrinkage estimation;
- a linear shrinkage-LDA head;
- no centered or zero-phase operation;
- no sample at or after the registered movement-onset guard;
- no EOG, EMG, acceleration, encoder, cue code, target identity, trial index,
  filename, participant identity, or elapsed-time feature in the candidate;
- no pretrained representation, NeuroToken, language model, or generated
  channel; and
- one CPU thread and one numerical job.

The future exact filter, window, guard interval, feature dimensions, fit count,
and participant split must be frozen after metadata qualification and before
any selected signal member opens.

## Target Firewall And Split Discipline

The future runner must separate three roles physically and structurally:

1. **Fit rows:** training-run movement onsets and labels may create training
   windows after participant/run splits are frozen.
2. **Target-blind prediction rows:** the model receives a continuous held-out
   signal stream and emits timestamped predictions without held-out onset,
   target, EOG, EMG, acceleration, or encoder values.
3. **Isolated scorer rows:** only after a hash-only prediction freeze is
   committed, pushed, and remotely green may the same held-out onset and
   control streams be delivered once to the scorer.

Overlapping windows may never cross run, session, or participant boundaries.
Window-random splitting is forbidden. Thresholds, onset detectors, artifact
ceilings, and temporal matching bins are fit-only quantities.

## Mandatory Comparators

Every participant and held-out run must emit the same primary metrics for:

1. no-signal prevalence prior;
2. elapsed-time-from-generic-cue or trial-phase model;
3. EOG-only model where EOG exists;
4. EMG-only pre-onset model where EMG exists;
5. acceleration- or encoder-only pre-onset model where kinematics exist;
6. frontal and occipital EEG proxies where those channels exist;
7. central-only EEG candidate;
8. EEG residualized against train-only EOG where EOG exists;
9. onset-shift and label-derangement controls; and
10. a future-context sentinel that must remain at chance or refuse execution.

A missing comparator is `unavailable`, never silently zero and never replaced
by another modality.

## Two-Axis Conjunction

The final router may not average away a failed control. A future top route
requires all of the following:

- Freewill-23 candidate beats the maximum of no-signal, elapsed-time, and EOG
  controls under a frozen participant-level paired test;
- Wrist-45 candidate beats the maximum of no-signal, elapsed-time, pre-onset
  EMG, and pre-onset kinematic controls;
- both axes pass exact causal replay and onset-shift/derangement checks;
- no candidate window contains measured movement, threshold-crossing EMG, or
  post-onset samples;
- each axis passes its separately frozen participant consistency floor; and
- the weaker of the two axis margins passes the primary minimum-effect gate.

The weaker-axis margin is primary. Pooling trials across participants is
descriptive only.

## Prospective Router

1. `MARC1-F00`: source identity, license, registration, or green-proof failure.
2. `MARC1-F01`: range, archive, member-path, checksum, size, or output-cap
   failure.
3. `MARC1-F02`: channel role, sampling, synchronization, geometry, or onset
   compatibility failure.
4. `MARC1-F03`: target firewall, split, causal replay, or future-sentinel
   failure.
5. `MARC1-R0`: mechanics valid; neither scientific axis beats controls.
6. `MARC1-R1`: Freewill-23 axis only passes.
7. `MARC1-R2`: Wrist-45 axis only passes.
8. `MARC1-R3`: both axes contain task information, but the mandatory
   non-EEG-control conjunction fails.
9. `MARC1-R4`: both axes pass the frozen incremental sensor-information
   conjunction.

`MARC1-R4` would support only: **pre-movement scalp-EEG sensor information
persisted beyond the measured controls in two complementary public movement
datasets**. It would not prove brain-specific origin, covert intent, imagined
movement, unseen-person generalization, online operation, typing, language,
thought decoding, portability, assistive utility, or clinical utility.

## Storage-Safe Evidence Sequence

The smallest responsible sequence is:

1. Freeze this Tier A source and hypothesis record.
2. Implement a standard-library generated-fixture ZIP range inventory and
   member-selection validator with no live URL opener.
3. Implement generated multimodal fixtures that test role separation, causal
   windows, target isolation, and every mandatory comparator interface.
4. Commit, push, and require both repository CI jobs green.
5. Prepare a separate all-false Tier C metadata packet for one bounded
   Freewill-23 archive range inventory and one Wrist-45 metadata revalidation.
6. Only after a fresh packet-bound decision, learn the exact member inventory;
   then freeze participant selection, byte budget, split, thresholds, fits,
   predictions, and score in a new preregistration.
7. Acquire only the selected members. Never download the 13.59 GB monolith.
8. Freeze predictions remotely before one target/control delivery and one
   score. No post-target update or rerun.

Prospective ceilings for later contracts are:

```text
incremental payload disk:       <= 8 GiB
incremental network payload:    <= 8 GiB
free disk before acquisition:   >= 12 GiB
generated private derivatives: <= 64 MiB
aggregate public output:        <= 1 MiB
CPU threads / workers / jobs:   1 / 1 / 1
```

These are planning ceilings, not current authorization. A later contract should
shrink them after exact archive-member inventory.

## What This Research Proves

Engineering capability added: NeuroDecodeKit now has a source-bound,
storage-aware two-axis design for distinguishing a pre-movement EEG effect from
cue, ocular, muscle, kinematic, timing, and leakage explanations.

Scientific claim not established: no real archive member, signal, event,
target, model, prediction, or score was accessed, so MARC-1 currently
establishes no new neural or decoding result.
