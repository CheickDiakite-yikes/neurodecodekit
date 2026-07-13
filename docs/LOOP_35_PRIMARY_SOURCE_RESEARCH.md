# Loop 35 Primary-Source Research And Peripheral-Confound Decision Note

Date: 2026-07-12

Status: **Planning research complete; experiment Not Started; no protected
signal, target, model, confound fixture, peripheral stream, acquisition, device,
or brain-specific claim is authorized**

Machine boundary: `registries/loop35_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 35

## Decision Summary

Loop 35 asks a harder question than “does the model use EEG or MEG values?”:

> After target leakage, timing, key identity, eye, muscle, motion, audio,
> environment, prompt, and language shortcuts are measured, do brain-sensor
> inputs add predictive information beyond every recorded nonbrain control?

The planning answer is:

1. Keep the experiment `Not Started` and every execution flag false.
2. Keep Loop 31's “sensor-signal dependence” separate from physical origin.
3. Inventory ten confound classes and nine future synchronized stream classes.
4. Treat key identity and prompt or target content as forbidden leak sentinels,
   not eligible baselines.
5. Compare timing-only, ocular-only, distal-muscle-only, proximal-muscle-only,
   motion-only, audio/environment-only, all-peripheral, brain-sensor-only,
   train-only-residualized brain-sensor, and all-stream conditions.
6. Select the strongest peripheral comparator and one brain-sensor rule on
   selection only, then freeze all final predictions before one target open.
7. Publish a peripheral or timing explanation as a valid scientific result.
8. Make every unrecorded required control block stronger attribution. Do not
   replace missing physical measurements with zero arrays or simulations.
9. Cap the best future local claim at **incremental brain-sensor information
   beyond the recorded controls** for the exact protocol.
10. Keep absolute brain origin, no-keypress transfer, patients, population,
    real-time, at-home, assistive, and clinical claims outside this design.

These are research recommendations. Exact people, device, peripheral sensors,
durations, files, bytes, calibration methods, synchronization thresholds,
practical margins, and authorization sentences remain unfrozen.

## The Critical Local Finding

Current local evidence cannot close the peripheral firewall.

The S21 path uses 102 MEG magnetometers and `STI101`-derived event timing. Its
committed sentence cache and reports do not carry synchronized EOG, EMG, gaze,
hand motion, body motion, or microphone streams. It can support a timing-
shortcut audit after separate authorization, but it cannot compare the MEG
candidate with a complete peripheral model.

The S7 EEG source includes three named ocular channels. The working bridge
excluded them and retained 61 EEG channels. That is good channel hygiene, but
it is not proof that ocular or muscle activity is absent from the remaining
scalp channels. More importantly, S7 is a consumed negative evaluation and is
not fresh evidence for Loop 35 selection or qualification.

The two real predictive results are already negative:

| Evidence | Candidate | No-signal | Decision |
|---|---:|---:|---|
| S21 same-person cross-session MEG | corpus CER `0.917949` | corpus CER `0.775458` | candidate worse |
| S7 within-session EEG | exact key accuracy `0.009091` | exact key accuracy `0.122727` | candidate worse |

There is therefore no positive local neural result waiting for a stronger
label. Loop 35 protects a future result from earning one too easily.

## Primary-Source Findings

### 1. Brain2Qwerty v1 is overt motor decoding with known event times

Brain2Qwerty v1 records healthy volunteers typing briefly memorized sentences.
Its model uses 500 ms windows from `-0.2` to `+0.3` seconds around each known
keypress. The paper reports left/right-hand and character information around
keypresses, keyboard-layout structure in model errors and embeddings, and a
performance difference between correctly and incorrectly executed keystrokes.
It also states that the protocol cannot definitively isolate execution
precision from cognitive intent.

Source:

- Noninvasive decoding of typed sentences from human brain activity:
  https://www.nature.com/articles/s41593-026-02303-2

This is strong evidence for prompted typing from EEG and MEG. It is not
no-keypress language-intent decoding. A model can exploit cortical motor and
somatosensory activity while still failing the intended communication setting
where actual keypresses are unavailable.

The source EEG system had 61 EEG channels and three ocular channels. That
supports explicitly measuring ocular information, not assuming that removing
three named channels removes every eye-related contribution.

### 2. Brain2Qwerty v2 removes keypress alignment, not the overt task

Brain2Qwerty v2 consumes the continuous MEG sentence segment instead of windows
aligned to provided keypress onsets. That is an important mechanics advance.
The acquisition still consists of healthy, proficient typists physically
typing prompted sentences. Each sentence is first heard through headphones,
then a fixation cue starts typing, and a small central square rotates with each
keypress. The paper explicitly says patients may lack actual keypresses during
training or finetuning as well as inference.

Source:

- Accurate Decoding of Natural Sentences from Non-Invasive Brain Recordings:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

Continuous inference therefore removes one direct timing input but does not
turn overt typing into attempted movement or arbitrary thought. Audio prompt,
visual feedback, motor execution, somatosensory feedback, and behavioral timing
remain task-locked information sources that must be separated by claim.

### 3. Small eye movements can sustain MEG decoding

Mostert and colleagues revisited visual working-memory decoding and found that
small stimulus-specific eye movements could explain stable persistent MEG
decoding. The task is different from typing, but the lesson is directly
relevant: a successful classifier on MEG sensors does not identify the physical
origin of its information.

Source:

- Eye Movement-Related Confounds in Neural Decoding of Visual Working Memory
  Representations: https://pubmed.ncbi.nlm.nih.gov/30310862/

Loop 35 requires EOG or eye tracking where ocular contribution is a required
confound. A fixation instruction alone is not a measurement.

### 4. Movement artifacts can outperform intended EEG components

Kline and colleagues recorded EEG and simultaneous upper-limb and neck EMG in
movement tasks, separated estimated brain and artifact components, and trained
classifiers on both. Artifact components were consistently more informative
when available to the classifier.

Source:

- Artifacts in EEG-Based BCI Therapies: Friend or Foe?:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8747566/

This is why “EEG-only model” is not enough. Scalp EEG channels can contain
muscle and eye information. A future typing protocol needs independently
recorded peripheral streams and must report their predictive performance.

### 5. MEG can also carry task-linked movement and muscle distortion

Abbasi and colleagues recorded MEG, facial EMG, audio, and head position
simultaneously during overt speech. They found loudness-linked head movement,
strong temporal alignment among audio, EMG, head motion, and MEG distortion,
and limitations in artifact correction. Jaw and facial sources inside the
sensor array were not solved by methods that suppress external sources.

Source:

- Correcting MEG Artifacts Caused by Overt Speech:
  https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2021.682419/full

Typing is not speech, and this result cannot quantify typing artifacts. It does
show why magnetic sensors and a low-pass filter do not guarantee cortical
origin. Hand, forearm, neck, jaw, head-position, and equipment measurements
remain necessary when they can covary with target behavior.

### 6. Cleaning methods need ground-truth validation

Nordin and colleagues used an electrical head phantom, robotic motion, noise
sensors, and neck EMG to evaluate motion and muscle artifact-removal methods.
This design matters because reduction in signal amplitude is not proof that a
cleaning method recovered the intended source without distortion.

Source:

- Motion and Muscle Artifact Removal Validation Using an Electrical Head
  Phantom, Robotic Motion Platform, and Dual Layer Mobile EEG:
  https://pubmed.ncbi.nlm.nih.gov/32746290/

Loop 35 therefore reports raw and residualized conditions side by side,
including retained variance and distortion diagnostics. Artifact rejection is
not permitted to become a final-set model-selection search.

## Ten Confound Classes

| ID | Class | Examples | Treatment |
|---|---|---|---|
| `L35-T00` | Prompt/target/label leakage | target sentence, prompt identity, typed response | Forbidden from eligible features |
| `L35-T01` | Direct key identity | ASCII trigger, key code, hand label | Leak sentinel only |
| `L35-T02` | Timing and schedule | onsets, intervals, duration, count | Timing-only comparator |
| `L35-T03` | Visual/ocular | fixation, saccade, blink, keypress-linked feedback | EOG/gaze comparator |
| `L35-T04` | Hand/forearm/finger | distal EMG and kinematics | Peripheral comparator |
| `L35-T05` | Face/jaw/neck/scalp | proximal EMG and movement | Peripheral comparator |
| `L35-T06` | Head/body/sensor motion | position, orientation, contact shift | Motion comparator |
| `L35-T07` | Audio/environment/equipment | prompt, keyboard sound, vibration, line noise | Environmental comparator |
| `L35-T08` | Physiology/recording state | ECG, respiration, reference, impedance | Measured or unavailable |
| `L35-T09` | Task/context/identity | language, subject, session, block, autocomplete | Joint Loop 31 control |

The taxonomy intentionally mixes artifacts and legitimate task signals. Motor
cortex activity during typing is neural, while forearm EMG is not; both can be
highly predictive of keys. The product question decides which signal is useful.
The scientific report must still name which one carried the information.

## Three Separately Authorized Stages

### Stage A: Synthetic interface

A target-free generated fixture can prove:

- stream identity and modality typing;
- source and host clocks;
- missing intervals, packet drops, and clock resets;
- masks, lengths, timestamps, and item identity;
- condition routing and forbidden-feature refusals;
- metrics, warnings, unavailable fields, and hashes.

It cannot prove a biological confound, artifact removal, cortical origin, or
decoding result. Stage A is separately preregistered and cannot authorize real
collection.

### Stage B: Fresh synchronized multimodal local study

A real stage needs its own ethics, consent, privacy, retention, deletion,
device, stream, file, byte, and stop packet. It may support at most incremental
brain-sensor information beyond the recorded controls for the exact people,
task, device, streams, and partitions.

Recommended physical partition floors remain consistent with Loop 32:

```text
calibration: 32 unique completed sentences
selection:   16 unique completed sentences
final:       48 unique completed sentences
```

Performed-row IDs and semantic-text hashes must be disjoint. Session or block
groups must remain intact. These counts are recommendations, not an acquisition
request or power analysis.

### Stage C: No-keypress or patient translation

This requires a different task and target population where actual keypresses
are missing during training and inference. It needs separate ethics, burden,
safety, model, statistics, and claim protocols. A Stage B overt-typing result
cannot authorize or predict Stage C.

## Nine Future Stream Classes

| ID | Stream | Scientific role |
|---|---|---|
| `L35-M00` | EEG, MEG, or OPM-MEG candidate sensors | Candidate brain-sensor stream; origin not guaranteed by name |
| `L35-M01` | Keyboard events | Timing truth; key identity isolated and forbidden |
| `L35-M02` | Stimulus and prompt events | Audio/visual exposure ledger |
| `L35-M03` | EOG or gaze | Ocular-only comparator |
| `L35-M04` | Hand/forearm EMG or kinematics | Distal motor comparator |
| `L35-M05` | Face/jaw/neck EMG or kinematics | Proximal artifact comparator |
| `L35-M06` | Head/body motion and geometry | Motion and sensor-contact comparator |
| `L35-M07` | Audio and environment references | Prompt, keyboard, room, and equipment comparator |
| `L35-M08` | Cardiac, respiration, and reference state | Physiological and recording-state nuisance stream |

Exact sensors and placements cannot be selected in a documentation-only pass.
The future packet must justify them from the actual device, task, participant
burden, and consent scope.

## Thirteen Future Conditions

| ID | Condition | Role |
|---|---|---|
| `L35-E00` | Train-only no-signal prior | Signal-free floor |
| `L35-E01` | Timing/length/schedule only | Behavioral timing comparator |
| `L35-E02` | Key-identity leak sentinel | Forbidden direct-label detector |
| `L35-E03` | Prompt/target leak sentinel | Forbidden content detector |
| `L35-E04` | EOG or gaze only | Ocular comparator |
| `L35-E05` | Hand/forearm EMG or kinematics only | Distal motor comparator |
| `L35-E06` | Face/jaw/neck EMG or kinematics only | Proximal comparator |
| `L35-E07` | Motion/geometry only | Motion comparator |
| `L35-E08` | Audio/environment only | Environmental comparator |
| `L35-E09` | All recorded peripheral streams | Strongest nonbrain comparator |
| `L35-E10` | Brain-sensor only | Registered candidate sensor path |
| `L35-E11` | Train-only residualized brain-sensor | Nuisance-controlled candidate |
| `L35-E12` | All synchronized streams | Combined upper-bound system |

Every condition must use the same final items. Unrecorded controls remain
`unavailable`; zero-filled fake streams do not count as a peripheral ablation.

The strongest peripheral comparator is selected on selection only. One brain-
sensor path and one residualization rule are also selected on selection only.
All final predictions and hashes freeze before one target open.

## Estimands And Decision Rule

The primary future estimand is:

```text
macro_CER(strongest all-peripheral condition)
  - macro_CER(all synchronized streams)
```

A positive value means adding brain sensors improves prediction beyond all
recorded peripheral information. It does not prove absolute brain origin.

Two required supporting estimands are:

```text
macro_CER(strongest nonbrain condition) - macro_CER(brain-sensor only)
macro_CER(strongest nonbrain condition) - macro_CER(train-only residualized brain-sensor)
```

The research recommendation is a `0.05` practical macro-CER margin for each
required increment, with 65,535 paired random sign assignments plus the
observed assignment and an intersection-union rule. The margins are not frozen
until preregistration. A tie fails. Every item-level error and difference must
remain visible.

The combined model is allowed to perform best, but its gain is not credited to
brain sensors unless the registered brain-sensor components also pass. A model
that succeeds using peripheral streams can be a useful accessibility system;
it must be labeled peripheral or hybrid rather than brain decoding.

One participant is one biological replicate. Final sentence rows and optimizer
seeds do not create population evidence.

## Synchronization And Cleaning

Each stream must retain:

- source and host clock identity;
- sampling rate and timestamp uncertainty;
- hardware and software synchronization events;
- conversion method and residual distribution;
- dropped packets, missing intervals, and clock resets;
- source, split, configuration, transform, payload, and result hashes.

All clock conversions follow the Loop 30 clock-domain contract. A millisecond
number without an origin is not synchronized evidence.

Artifact detection, residualization, normalization, and source transforms fit
on train or calibration only. Raw and residualized results are both reported.
Final targets cannot select a cleaning method, component count, frequency band,
or regression strength.

Source localization and topography are supporting evidence. Neither is a
standalone proof of origin when peripheral sources, forward-model error, and
task correlation remain possible.

## Outcome Taxonomy

| ID | Meaning | Consequence |
|---|---|---|
| `L35-O0` | Not run | Planning only |
| `L35-O1` | Invalid | Consent, stream, sync, leakage, split, target, hash, or resource failure |
| `L35-O2` | Missing required control | Stronger attribution unavailable |
| `L35-O3` | Direct leakage | Invalidate; do not score |
| `L35-O4` | Timing or peripheral explains result | Relabel task/peripheral decoding |
| `L35-O5` | Sensor dependence without increment | Keep Loop 31 wording only |
| `L35-O6` | Bounded incremental brain-sensor information | Exact local protocol and recorded controls only |
| `L35-O7` | No-keypress and patient transfer unavailable | Separate future program |

## Resource Boundary

Stage A synthetic interface recommendation:

```text
CPU threads / workers:       1 / 1
runtime:                 120 seconds
peak RSS:                    1 GiB
generated artifacts:        16 MiB
new downloads:             0 bytes
```

Stage B analysis recommendation:

```text
CPU threads / workers:       1 / 1
analysis runtime:        1,200 seconds
peak RSS:                    1 GiB
derived artifacts:          32 MiB
acquisition bytes:     unavailable until an exact packet
```

The user's 5-10 GB incremental storage envelope is capacity, not consent,
acquisition, data-access, model, target, device, or execution authorization.

CPU time is not energy. Direct energy remains unavailable.

## Measured Research Boundary

```text
high-level public-web research operations:              6
public GitHub API operations:                           0
protected dataset/model/weight download bytes:          0
raw signal/header reads:                                0
real-cache content reads:                               0
target/prompt/typed-response reads:                     0
source-test/session-2/consumed-S7 reads:                 0
S20/S25 operations:                                     0
checkpoint/model/training/parameter-update runs:        0 / 0 / 0 / 0
confound-condition fits/runs:                           0
synthetic fixture generations:                          0
fresh recording/acquisition sessions:                   0
EOG/gaze/EMG/motion/audio/keyboard/hand operations:     0
new real-data downloads:                                0
RW3/SDK/socket/stream/device/hardware operations:        0
CPU threads / workers:                                  1 / 1
current generated planning-artifact cap:                8 MiB
```

Complete public-network response bytes, one end-to-end interactive research
runtime, interactive peak RSS, direct energy, and future acquisition bytes are
unavailable from the research tool and current protocol. They remain
unavailable rather than estimated.

## Claim Taxonomy

| ID | Claim | Available now? |
|---|---|---:|
| `L35-C0` | No new result; planning boundary only | Yes |
| `L35-C1` | Synthetic confound interface | No |
| `L35-C2` | Task or peripheral predictability | No |
| `L35-C3` | Sensor-signal dependence | No |
| `L35-C4` | Incremental brain-sensor information beyond recorded controls | No |
| `L35-C5` | No-keypress, attempted-movement, or patient transfer | No |
| `L35-C6` | Population, clinical, or product brain interface | No |

Even a future `L35-C4` result would not resolve unrecorded confounds or prove
absolute neural origin. It would apply only to the exact people, overt-typing
task, device, stream set, partitions, models, and recorded controls.

## Decision And Next Gate

Loop 35 planning research is complete. The experiment remains `Not Started`.

The immediate numbered execution gate remains Loop 25. Loop 35 first depends
on a compatible Loop 31 sensor-signal result. A later Stage A synthetic
interface needs its own preregistration and exact authorization. Real Stage B
work additionally needs a separate ethics, consent, privacy, retention, device,
stream, file, byte, and acquisition packet.

Engineering capability added: a machine-checkable ten-class confound registry,
nine-stream synchronized protocol, 13-condition matrix, staged authorization
firewall, paired estimands, 24 gates, 32 refusals, and fail-closed attribution
ladder now exist.

Scientific claim not established: no protected signal, target, model,
peripheral stream, confound condition, acquisition, or participant operation
occurred, so there is no brain-specific contribution, peripheral explanation,
no-keypress transfer, neural advantage, decoding accuracy, patient result,
real-time behavior, or portable-hardware result.
