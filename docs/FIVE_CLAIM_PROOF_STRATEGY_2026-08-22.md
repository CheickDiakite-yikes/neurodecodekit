# Five-Claim Scientific Proof Strategy

Date: 2026-08-22

Status: **Tier A research strategy; zero dataset, model, target, stream, or
hardware operations**

Machine registry:
`registries/five_claim_proof_strategy.v0.json`

## Objective

NeuroDecodeKit will pursue five claims as separate evidence targets:

1. language information from EEG;
2. pre-movement information consistent with motor-cortex contribution;
3. strict generalization to a completely unseen person;
4. live end-to-end neural decoding; and
5. incremental EEG information beyond eye, timing, muscle, and movement
   measurements.

No one accuracy score can establish all five. Each claim has a different
firewall, comparator, and failure meaning. Free-form arbitrary-thought reading
is not an eligible near-term claim because none of the selected public tasks
provides ground truth for unconstrained private thoughts.

## Current Evidence

The strongest real EEG result is `WO9R-R3`. A prespecified causal 0.5-4 Hz
whole-head model, frozen before held-out target delivery, reached balanced
accuracy `0.680975` for executed movement and `0.728014` for motor imagery
across 12 participants. The matched no-signal comparators were approximately
chance.

That result is predictive but not motor-cortex-specific. The early cue window
reached `0.762865`, the frontal proxy reached `0.671821`, and the central
sensorimotor view reached `0.647575`. The lateralization direction held for
only 5 of 12 participants. The leading explanation is therefore
class-correlated cue, visual, or ocular activity. WO9R proves that the pipeline
can recover a repeatable EEG-associated condition signal; it does not prove
movement intention, neural origin, unseen-person transfer, or live use.

The real S21 language lane remains negative: its causal sentence model was
worse than its no-signal prior. The current MARC-2 lane has performed only
target-free structural validation and has not opened a neural payload.

## Claim Scoreboard

| ID | Claim target | Status now | Evidence required for a pass |
|---|---|---|---|
| `C1` | EEG carries language-command information | Not established | A frozen held-out command model must beat cue/time, EOG, oral-EMG, no-signal, and deranged-EEG conditions. A four- or six-command pass is closed-set language evidence, not arbitrary thought-to-text. |
| `C2` | Pre-movement EEG is consistent with motor-cortex contribution | Not established | Cue-neutral pre-movement EEG must add information beyond EOG and acceleration, show a prospectively frozen central/lateralized spatial-temporal pattern, and beat frontal, occipital, shifted, reversed, and deranged controls. Scalp EEG alone cannot prove exclusive anatomical origin. |
| `C3` | The model generalizes to a completely unseen person | Not established | A model and all transforms must be frozen without any signal, target, calibration, normalization, or threshold fitting from the held-out person, then beat matched controls on that person. |
| `C4` | End-to-end decoding operates live | Not established | A real stream must be acquired, causally transformed, decoded, and displayed with measured capture-to-output latency, no known future event timing, bounded dropouts, and abstention. Offline replay alone is insufficient. |
| `C5` | EEG adds value beyond eyes and other measured non-neural signals | Not established | On identical held-out trials, `P+E` must improve participant-macro log loss over the strongest peripheral model `P`, as well as `P+D(E)`, timing-only, and no-signal controls. |

## Two Offline Tracks

### Track M: movement attribution, peripheral controls, and unseen people

Freewill-23 remains the highest-value primary source because its generic audio
cue does not identify the chosen target and it records 31 EEG channels, four
EOG channels, three wrist-accelerometer axes, and reviewed movement-onset
indices across 23 participants.

The ordered work is:

1. `MARC2-VR20P` through `MARC2-VR34P`: localize structural blockers and
   establish, under exact finite readiness, that the current task-blind
   eligible total is above 195 without exposing a count or cohort.
2. `MARC2-VR35A`: generated-only task-aware eligibility and selection repair,
   now qualified across 20 paths and explicitly separating mixed-task surplus
   from genuine target-task drift without asserting the private cause.
3. A separately authorized private confirmation may freeze one target-free
   structural cohort only if the exact-task projection and selector pass.
4. `MARC2-FW2`: acquire and semantically qualify only selected archive members
   under the existing storage ceiling.
5. `MARC2-CIL1`: test within-person held-out-session conditional EEG gain
   beyond timing, EOG, and acceleration.
6. `MARC2-ZP1`: freeze a participant-independent model and run strict
   leave-one-person-out prediction with zero held-out-person adaptation.

`CIL1` can address `C2` and `C5`. It cannot establish `C3` because its models
are fit within person. `ZP1` is a separate claim event and must not reuse a
person after observing that person's score.

### Track L: closed-set language before sentence decoding

OpenNeuro `ds003626` remains the primary controlled language source. It has ten
native Spanish participants, randomized four-command trials, 128 EEG channels,
eight external channels, inner-speech, pronounced-speech, and visualized-
direction conditions. Its visualized condition, EOG, and oral-EMG channels make
the cue and articulation alternatives testable rather than merely discussable.

The first endpoint is only four-command inner-speech information beyond cue,
visualized-direction, EOG, oral-EMG, and deranged-EEG controls. A later model
may receive the frozen command probabilities, but it must beat both an
identical language-model-only condition and an item-deranged neural condition.

Two 2026 sources are reserves, not automatic downloads:

- TESSCCo offers 21 native Spanish participants, three non-native Spanish
  participants, five overt/covert TV commands, 32 EEG channels, and 7,936
  epochs. Exact payload identity, license, cue controls, and peripheral roles
  still require qualification.
- The Directional Word dataset offers 22 Russian/Spanish participants, 38 EEG
  channels, and exploratory EMG in a subset, but its predominantly fixed word
  order, word-block design, right-hand marker press, protocol variants, and
  5.0 GB single archive create strong block, time, motor, and storage
  confounds. It is unsuitable as the first word-decoding claim.

Brain2Qwerty v1 remains the direct typed-sentence reference. The official 2026
release reports average CER `0.65` for EEG and `0.29` for MEG, but its full
training path is a multi-GPU reproduction target. Brain2Qwerty v2 code is open,
while its nine-participant training data remain unavailable to this project.
NeuroDecodeKit will not equate a small local scaffold with that result.

Primary sources:

- [Brain2Qwerty Nature Neuroscience article](https://www.nature.com/articles/s41593-026-02303-2)
- [Official Brain2Qwerty code](https://github.com/facebookresearch/brain2qwerty)
- [Freewill-23 data descriptor](https://www.nature.com/articles/s41597-025-06039-9)
- [Inner Speech-10 data descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [TESSCCo data descriptor](https://www.nature.com/articles/s41597-026-07745-8)
- [Directional Word data descriptor](https://www.nature.com/articles/s41597-026-07809-9)
- [Directional Word Zenodo record](https://zenodo.org/records/20374418)

## Live Comes After Signal Attribution

The live path has two required stages:

1. `NDK-STREAM1`: exact offline-versus-incremental parity on a frozen model,
   including clocks, buffering, dropped chunks, resume, and abstention.
2. `NDK-LIVE1`: one real device stream with capture-to-output latency and no
   event-onset oracle.

Neither stage is useful as scientific evidence until an offline candidate has
passed its applicable neural and confound gates. A live display of a cue- or
eye-driven classifier would be a live confound, not live neural decoding.

## Resource Order

- one CPU thread, one worker, and one numerical job by default;
- at most 10 GiB incremental research payload at any time;
- one real-data track active at a time;
- no whole 13.59 GB Freewill archive;
- no larger model before the compact registered families fail for a measured
  representation reason;
- no provider or language-model call before a neural prediction freeze; and
- no live hardware purchase or connection without a separate Tier C decision.

## Immediate Gate

Protocol-conforming `MARC2-VR34P` is consumed at aggregate R2: the current
task-blind eligible total is above 195, but the count, task distribution,
identity, participant, selection, and cohort remain unavailable.

Generated-only `MARC2-VR35A` now qualifies exact published-task projection
before eligibility arithmetic. Its 20-path matrix removes mixed-task surplus,
preserves genuine target-task drift, reproduces the baseline semantic cohort,
and selects zero non-target rows. This establishes the repair mechanism on
generated fixtures, not the private cause of VR34P R2.

VR35A proof closeout `6744568` passed both required jobs in CI `32645704669`.
All-false VR36P now requests one future target-free task-aware cohort
confirmation. Exact request `8ec87ce` passed both required jobs in CI
`32646648532`; request proof closeout `2813d60` passed both jobs in CI
`32647453505`. After sole-packet identification, the maintainer's exact
`coninue` authorized only that unchanged two-stage packet by reference.
Decision `fd08dd6` passed both jobs in CI `32648347577`; the sole generated
Stage 1 qualification then passed all 40 routes and 111 direct refusals with
zero private operation. Exact Stage 1 `8179f6f` passed both jobs in CI
`32650171033`; its proof-only closeout is now prepared without requalification
or private access. The sole private confirmation is authorized but not
eligible until that closeout is remotely green; FW2 work is not authorized.

## Claim Boundary

Engineering capability added: the five desired outcomes are now separated
into executable evidence targets with exact comparators, ordering, resource
limits, and failure meanings.

Scientific claim not established: this strategy performed no real-data read,
training, inference, scoring, streaming, or hardware operation and establishes
none of the five target claims.
