# MARC-2 Confound Triangulation And Language Bridge Research

Date: 2026-08-13

Status: **Tier A primary-source research complete; no dataset metadata body,
private manifest, archive member, payload, signal, event, target, model,
prediction, score, or provider call was accessed or authorized**

Registry: `registries/marc2_confound_triangulation_research.v0.json`

## Executive Decision

Continue the same scientific path, but retire the failed requirement that the
Wrist-45 source must be one of two conjunctive datasets. The source-aware
Wrist metadata check returned frozen route `MARC1SAL-R2`, selected zero
participants, and moved zero payload bytes. That branch is consumed and may
not be retried, repaired, or routed around.

The replacement is **MARC-2: Confound Triangulation**. It assigns a different
question to each future cohort instead of asking one dataset to answer every
confound:

1. Freewill-23 tests target choice without a target-specific cue and measures
   eye activity plus wrist acceleration.
2. One independently selected multimodal cohort tests whether EEG adds
   information after measured peripheral signals.
3. A raw Spanish inner-speech cohort tests whether any control-adjusted sensor
   result survives the transition from movement to language commands.

The core endpoint is not raw accuracy. It is held-out **conditional
information gain**: does adding EEG improve a proper scoring rule after the
best available cue, timing, eye, muscle, and kinematic model has already been
fit? This makes a positive result interpretable and a negative result useful.

No larger model, language model, or new download is justified before the
Freewill gate. The next executable engineering unit is only a generated/mock
Freewill-only selector, after a separately green contract. Any read of the
retained private archive inventory is a later Tier C decision.

## Why MARC-1 Could Not Simply Continue

The MARC-1 two-axis hypothesis was scientifically reasonable: Freewill-23
reduced target-cue ambiguity and Wrist-45 supplied EMG plus encoder timing.
The engineering lane correctly refused the Wrist source after a single
source-aware metadata response. The aggregate result does not reveal whether
the private source route was R3 or R4, and the retained files must not be
reopened or inspected.

That is a source-eligibility failure, not evidence against the neural
hypothesis. It does mean the old top route, which required both named axes,
cannot be reached. MARC-2 therefore changes the prospective evidence design,
not the observed outcome and not the scientific destination.

Bound consumed result:
`registries/marc1_source_aware_live_metadata_result.v0.json`

## The Scientific Question

The next question is:

> On held-out sessions or people, does causal scalp EEG improve prediction of
> a self-selected action or inner-speech command after a model already has the
> available non-EEG timing and peripheral measurements?

The strongest future sensor-level result requires all of these properties:

- the target is not specified by an immediately preceding class-specific cue,
  or that cue is modeled by a matched control;
- the candidate uses no post-onset sample and no centered or zero-phase
  operation;
- fit, prediction, and scoring targets are physically separated;
- no-signal, timing, EOG, EMG, and kinematic controls are explicit where the
  source provides them;
- the candidate improves held-out log loss beyond the strongest available
  non-EEG model, not merely beyond chance;
- onset-shift, label-derangement, future-context, and spatial-control tests do
  not explain the gain; and
- participant-level effects, rather than pooled trial counts, drive the
  inference.

Even a complete pass would establish incremental information in scalp-sensor
measurements beyond recorded controls. It would not establish an exclusively
brain-generated origin.

## Primary-Source Update

### Freewill-23 remains the primary positive-control axis

The 2025 Scientific Data descriptor reports 23 participants, 49 recordings,
and 6,808 trials. Participants chose one of four targets and chose when to
move after a generic audio trial-start cue. The cue did not specify either the
target or movement onset. The source includes 31 EEG channels, four EOG
channels, one trigger channel, and three wrist-accelerometer axes, with
reviewed accelerometer-derived movement-onset indices.

Source: [A large electroencephalogram database of freewill reaching and
grasping tasks for brain machine interfaces](https://www.nature.com/articles/s41597-025-06039-9)

The official archive is CC BY 4.0 and 13,591,548,048 bytes. NeuroDecodeKit has
already inventoried its 1,227 central-directory entries from 306,758 metadata
bytes without downloading the archive or opening a member. The exact private
manifest is retained mode `0600` under a Git-ignored path. Its SHA-256 is
`2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031`.

Bound inventory result:
`registries/marc1_freewill_central_directory_live_result.v0.json`

The archive may never be downloaded whole. A future selector may open the
retained private manifest only under a new exact decision, validate its bound
hash, select target-free member identities, emit aggregate byte totals, and
stop before any archive member request.

### Biomed-SPC-9 is the most complete compact peripheral-control candidate

The 2025 Mendeley record reports nine participants performing elbow flexion
and extension under four active/resistive conditions. It provides 28 EEG
channels plus four EOG electrodes at 250 Hz, 32-channel high-density biceps
EMG at 2,000 Hz, and wrist IMU at 100 Hz. The 3.35 GB dataset is CC BY 4.0.

Source: [Biomed_SPC: Measuring SMR during Active and Resistive
Movement](https://data.mendeley.com/datasets/zmrbzpnggr/1)

This source is not cue-neutral. Each trial includes a fixation period followed
by a class-specific movement cue. Its role is therefore peripheral attribution,
not independent proof of covert intent. It is valuable only if the exact
signals can support a cue/time model, EOG-only model, EMG-only model, IMU-only
model, EEG-only model, and peripheral-plus-EEG model on the same held-out
trials.

### PhysioNet Gait-59 is the scale and held-out-person reserve

The 2026 PhysioNet release reports 59 healthy adults walking for one minute at
each of three treadmill speeds. It provides 19 dry-electrode EEG channels at
300 Hz, 12 lower-limb EMG channels, 17-sensor IMU kinematics, and bilateral
force-plate measurements. The release is CC BY 4.0, approximately 4.5 GB as a
ZIP and 6.5 GB uncompressed, with modality-specific participant files.

Source: [A multimodal gait dataset of brain activity, muscle activity,
kinematics and ground forces in young adults](https://www.physionet.org/content/multimodal-gait-dataset/1.0.0/)

This source has no dedicated EOG and records continuous movement, where scalp
motion is a serious confound. It cannot replace Freewill-23. It can provide a
larger participant-held-out test of whether EEG adds anything after EMG, IMU,
force, speed, and head-motion proxies. It remains a reserve until a metadata-
only utility-per-byte gate chooses it over Biomed-SPC-9.

### WAY-EEG-GAL is a warning, not a new download target

WAY-EEG-GAL contains 12 participants, 3,528 usable grasp-and-lift trials, 32
EEG channels, five EMG channels, kinematics, force, and task events. A 2026
leave-one-subject-out study found EEG-only decoding near chance for weight and
surface while EMG-only models carried the useful signal. Adding EEG sometimes
reduced performance.

Sources:

- [WAY-EEG-GAL data descriptor](https://www.nature.com/articles/sdata201447)
- [Architecture-data matching for EEG-EMG decoding](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2026.1874302/full)

That result directly motivates the conditional-information endpoint. MARC-2
must never call a fused model a neural result unless EEG adds held-out value
after peripheral modalities. No WAY payload is proposed.

### Voluntary Finger Tapping-14 is legally open but causally limited

The University of Reading archive reports 14 participants, 120 trials each,
19 EEG channels at 1,024 Hz, and two tap-device channels. The 721 MB archive
is CC BY 4.0 and uses voluntary asynchronous left tap, right tap, and rest
conditions.

Source: [EEG Data for Voluntary Finger Tapping
Movement](https://researchdata.reading.ac.uk/117/)

Only six-second trials after preprocessing and ICA are described. Unless raw
continuous data and a causal preprocessing history are independently
available, this source cannot enter a causal top route. It remains a low-cost
diagnostic or external replication reference, not the selected MARC-2
experiment.

### Inner Speech-10 is the selected future language-control source

The 2022 Scientific Data descriptor reports ten native Spanish speakers,
5,640 trials, and more than nine hours of continuous recording. The raw BDF
contains 128 EEG and eight external channels at 1,024 Hz. Four external
channels measure horizontal and vertical EOG and two measure oral EMG. The
participants performed four commands under inner-speech, pronounced-speech,
and visualized-direction conditions. Raw recordings and events are available
as OpenNeuro `ds003626` version `2.1.0`.

Source: [Thinking out loud, an open-access EEG-based BCI dataset for inner
speech recognition](https://www.nature.com/articles/s41597-022-01147-2)

This is still a visually cued closed-set task. Its value is that the same
command identities appear under three mental or overt conditions while EOG
and mouth EMG are recorded. A future result must separate cue identity,
spatial visualization, and oral movement from inner-speech evidence. Four-way
command classification is not open-vocabulary thought-to-text.

Newer sentence and bilingual sources are promising but are not selected for
execution here. Chisco has deep per-person sentence data but only three
participants. TESSCCo has 21 native Spanish participants plus three non-native
participants and five bilingual commands, but its exact payload identity,
dataset license, cue controls, and storage remain unqualified. They are later
replication candidates, not reasons to broaden the current task.

## CIL-v0: Conditional Information Ladder

Every future real experiment must fit the same ordered ladder on identical
splits:

1. `B0`: no-signal prevalence or class prior.
2. `B1`: cue identity, elapsed time, trial phase, and schedule only.
3. `P`: all available non-EEG peripheral streams, with EOG, EMG, and kinematic
   contributions also reported separately.
4. `E`: EEG-only candidate.
5. `P+E`: the same peripheral model augmented with EEG.
6. `P+D(E)`: the peripheral model augmented with a frozen deranged EEG view.

The primary endpoint is participant-macro held-out conditional log-loss gain:

```text
delta_EEG_given_P = log_loss(P) - log_loss(P+E)
```

Balanced accuracy, macro F1, calibration error, and confusion matrices are
secondary. Pooled trial accuracy is descriptive only. The future contract
must freeze a minimum meaningful effect, participant-consistency floor,
one-sided paired randomization test, and multiplicity policy before any final
target opens.

The top scientific route requires positive `delta_EEG_given_P`, not merely
`E > B0`. If peripheral modalities already explain the task, the correct
result is confound localization.

## Three Frozen Candidate Families, Not A Model Search

MARC-2 may test three compact hypotheses in parallel, but they are separate
registered families rather than a winner-take-all search:

1. `H-LF`: causal 0.5-4 Hz potential features with shrinkage LDA.
2. `H-SMR`: causal train-only mu/beta covariance features with a regularized
   linear or Riemannian head.
3. `H-CML`: the existing compact potential/mu/beta `CML-v0` family under its
   10,000-parameter ceiling.

The future preregistration must name one primary family, apply multiplicity to
the other two, and forbid final-target family selection. No transformer,
pretrained neural representation, foundation model, or larger architecture is
eligible in the sensor-evidence path.

## Five Ordered Work Orders

### 1. MARC2-FW1: Freewill-only target-free selection

Build and qualify a generated/mock selector first. A later exact Tier C run
may open only:

`.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json`

It must verify the bound 418,755-byte private identity and SHA-256, apply a
DOI-bound target-free participant rank, require complete session/run bundles,
emit only aggregate counts, hashes, and byte totals, and stop. It may not
request an archive byte, open a member, read a signal, event, target, or
participant outcome, or reuse the consumed MARC1-P1 executor.

### 2. MARC2-FW2: bounded member acquisition and semantic qualification

After selection is frozen and remotely green, preregister exact member names,
ranges, compressed and uncompressed byte totals, local-header checks, CRC and
SHA-256 rules, output paths, and cleanup. Acquire only selected members by
range. Never materialize the 13.59 GB archive.

The qualification phase may validate channel roles, source clocks, geometry,
session/run identity, generic cue events, EOG, acceleration, reviewed onset
indices, and target-cardinality compatibility. It must not expose final
session targets to a model or choose quality thresholds from final outcomes.

### 3. MARC2-CIL1: one Freewill target-firewalled experiment

The prospective primary task is four-way chosen-target prediction. Session 1
is fit/development; session 2 is held out within participant. The candidate
must emit continuous target-blind probability streams. Held-out movement
onsets and target identities are delivered only to the isolated scorer after
the aggregate prediction freeze is committed, pushed, and remotely green.

The primary analysis samples predictions in a frozen strictly pre-movement
window, provisionally ending at least 200 ms before reviewed acceleration
onset. Exact windows, filters, thresholds, fit counts, participants, and trial
counts are frozen after semantic qualification and before held-out targets.

Required controls include B0/B1/P/E/P+E, EOG-only, frontal and occipital EEG,
train-only EOG residualization, onset shifts, label derangement, temporal
reversal, and a future-context sentinel. A positive result can support only
pre-movement scalp-sensor target information beyond measured cue, timing,
ocular, and kinematic controls.

### 4. MARC2-ORTH1: one orthogonal peripheral-control cohort

Only if MARC2-CIL1 passes its conditional-information gate, run a metadata-only
utility-per-byte router between Biomed-SPC-9 and a bounded PhysioNet Gait-59
subset. The router is fixed before any outcome access and scores license,
participant granularity, synchronized control completeness, cue ambiguity,
raw/causal compatibility, expected bytes, and held-out-person support.

Exactly one source may be acquired in this work order. Biomed-SPC supplies the
cleaner complete EOG/EMG/IMU control stack; PhysioNet supplies the stronger
participant count and force/kinematic scale. Neither may be used to rewrite
the Freewill hypothesis after its score.

### 5. NDK-LANG1: Spanish inner-speech control ladder, then optional LLM

Only if a movement result survives measured controls, qualify a bounded
OpenNeuro `ds003626` subset and freeze a separate language experiment. The
first endpoint is four-command inner-speech sensor information beyond cue,
visualized-condition, EOG, and oral-EMG controls. Overt speech is a transfer
condition, not clean neural ground truth.

Any hosted language model is downstream of a remotely green neural prediction
freeze. It receives only calibrated command probabilities and timing, never
raw EEG, participant identity, local paths, final targets, or reference text.
The matched conditions are:

1. neural evidence only;
2. language model only;
3. language model plus frozen neural evidence; and
4. language model plus item-deranged neural evidence.

The combined system must beat both language-model-only and deranged-evidence
conditions. On a four-command vocabulary, the language model is only a
renderer/reranker and cannot establish thought-to-text. Open-vocabulary CER
or WER requires a later fresh sentence-level cohort and contract.

## Target Firewall

Future runners must separate four deliveries:

1. fit signals, controls, onsets, and targets;
2. held-out target-blind signal streams;
3. held-out target-blind timing/control streams needed for matched comparator
   predictions; and
4. one final held-out target delivery after the aggregate freeze is green.

No final target, reference text, intended command, corrected response, or
participant outcome may influence filtering, thresholding, trial exclusion,
family selection, calibration, or stopping. A final-target open consumes the
experiment. Post-target updates and reruns are zero.

## Prospective Router

1. `MARC2-F00`: source, license, identity, private capability, or green-proof
   failure.
2. `MARC2-F01`: member, range, checksum, size, clock, role, or output-cap
   failure.
3. `MARC2-F02`: split, causal replay, target firewall, or future-sentinel
   failure.
4. `MARC2-R0`: mechanics valid; EEG does not beat no-signal or timing controls.
5. `MARC2-R1`: EEG beats simple controls but adds no information beyond the
   strongest measured peripheral model.
6. `MARC2-R2`: Freewill EEG adds held-out conditional information beyond its
   measured controls.
7. `MARC2-R3`: Freewill passes, but the orthogonal cohort does not support a
   consistent incremental EEG effect.
8. `MARC2-R4`: movement cohorts support a consistent incremental scalp-sensor
   effect beyond their measured controls.
9. `MARC2-R5`: the separately frozen inner-speech command experiment also
   passes its cue/EOG/oral-EMG conjunction.

`MARC2-R5` remains closed-set command evidence. No route in this research
establishes free-form thought-to-text.

## Resource And Storage Policy

Current generated or downloaded bytes from this research are zero. Later
contracts may not exceed the maintainer's 10 GB ceiling and should target a
smaller envelope:

```text
maximum simultaneous incremental payload:  <= 8 GiB
minimum free disk before payload work:      >= 15 GiB
private derivatives per experiment:         <= 64 MiB
aggregate public output per experiment:      <= 1 MiB
CPU threads / workers / numerical jobs:      1 / 1 / 1
provider budget in this research:            $0
```

Every acquisition contract must shrink its cap to exact selected bytes. No
whole Freewill archive, duplicate raw bundle, model download, or large
checkpoint is eligible. Temporary cleanup may remove only files created by
the same registered invocation.

## Immediate Next Gate

1. Commit, push, and require both repository CI jobs green for this research.
2. Freeze a generated/mock `MARC2-FW1` selector contract under Tier A.
3. Implement and qualify only generated fixtures under Tier B after that
   contract is remotely green.
4. Prepare an all-false Tier C request only after the exact selector is
   remotely green.
5. Require a fresh packet-bound maintainer decision before the one retained
   private-manifest read.

No current message authorizes that read. The consumed Wrist result, Freewill
private inventory, archive members, real signals, targets, models, scores,
replication sources, and language sources remain closed.

## What This Research Proves

Engineering capability added: NeuroDecodeKit now has a five-work-order,
storage-bounded architecture that measures EEG's conditional contribution
instead of confusing multimodal or language-model performance with neural
evidence.

Scientific claim not established: no new real signal, target, model,
prediction, or score was accessed, so this research establishes no new neural
effect, language decoding, thought-to-text, unseen-person, real-time,
portable-hardware, assistive, or clinical result.
