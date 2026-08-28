# COMM-P0-G Generated Qualification Preregistration

Date: 2026-08-27

Status: **generated-only registration pending its own remote CI; no execution
authorized**

Registration: `COMM-P0-G-v0`

Machine contract:
`registries/communication_eeg_prospective_generated_qualification_contract.v0.json`

## Purpose

`COMM-P0-SYNC-v0` freezes a prospective two-cohort communication study. Before
any person is recruited or any device is operated, this qualification must
show that the software can represent that study deterministically and refuse
the shortcuts most likely to create a false positive.

This is an engineering qualification over fictional procedural signals. It
cannot establish synchronization quality, neural information, communication
decoding, peripheral independence, unseen-person performance, live device
latency, or human benefit.

## Immutable Parents

The qualification binds:

- green parent registration `df3266ed09132017cc8a9dcc10e8a7d61ea92f61`, CI
  `33134791405`;
- green proof and Amendment 1 commit
  `478d31ed8908e29439db215f3aed01a3bcbc16fc`, CI `33135742217`;
- the authoritative 70% stable-commit coverage threshold; and
- the existing `SourceChunk` and `LiveSession` schemas without modifying or
  rerunning their consumed qualifications.

Implementation may begin only after this registration is committed, pushed,
and Base Python plus Optional Neuro Readers are green. One official generated
qualification may run only after that exact implementation is separately
committed, pushed, and both jobs are green. The invocation is consumed whether
it passes, refuses, crashes, or times out.

## Fictional Cohorts And Trials

Two disjoint fictional enrollment periods contain 22 identities each. Each
period has 21 complete participants and one target-free hardware-failure
exclusion, preserving 42 complete and 44 enrolled identities without a real
person or participant identifier.

Every complete fictional participant has the exact 256-row grammar:

| Role | Rows |
|---|---:|
| Prompted intend | 64 |
| Prompted no-intent | 32 |
| Free-choice intend | 64 |
| Free-choice no-intent | 32 |
| Rest | 32 |
| Peripheral calibration | 32 |

That yields 10,752 structural trial rows and 4,032 fixed-size free-choice
TargetVault precommits per replay. The four commands remain `yes`, `no`,
`help`, and `stop`.

Replication rows are deterministically divided before any target exists:

- shadow: 32 prompted-intend, 16 prompted-no-intent, 32 free-choice-intend,
  16 free-choice-no-intent, and 16 rest rows per participant;
- live: the same counts on distinct rows; and
- all 32 peripheral-calibration rows occur before shadow and may not fit,
  calibrate, adapt, or select a replication model.

The confirmatory replication estimand uses hidden-output shadow rows only.
Live display is a separate operational endpoint. Neither may rescue failure of
the other.

## Target Firewall

The fictional choice controller must commit each free-choice target before the
intention window into a fixed-size authenticated stand-in record. Record size,
filename, write schedule, process arguments, environment, IPC, logs, errors,
and decoder-visible metadata must be class-independent. Target keys and map
locations are absent from decoder, operator, feature, model, language,
freezer, and live-session capabilities.

The minimum washout is six seconds. Decoder and endpointer context is capped at
four seconds and may contain only post-washout source samples. Trial identity,
block identity, choice-button position, selection movement, report mapping,
and pre-washout state are forbidden. A fixture where only those pre-washout
signals predict the command must collapse to its registered control route.

Discovery predictions freeze before discovery target delivery. The complete
replication task grammar, hardware role map, preprocessing, model,
calibration, threshold, endpointer, scorer, seeds, exclusion policy, software
environment, and code hashes freeze before discovery target delivery and
before replication enrollment or data access. Discovery cannot tune the
replication protocol. Replication predictions must be committed and remotely
green before its one target delivery and one score.

## Synchronized Sensor Adapter

The 73 biosignal roles are represented as three synchronized SourceChunk
shards because SourceChunk v0 permits at most 32 channels:

1. `EEG_A`: 32 EEG channels;
2. `EEG_B`: 32 EEG channels; and
3. `PERIPHERAL`: four EOG, four bilateral oral-EMG, and one photodiode channel.

All shards share one bundle identity, sample axis, sampling rate, generation,
clock ledger, gap/reconnect ledger, and segment boundary. Microphone audio and
hardware trigger remain separately typed synchronized surfaces. Missing,
duplicated, reordered, interpolated, differently clocked, or role-drifted
members refuse before feature construction.

A 27.5-minute session is represented by 14 bounded segments: thirteen
120-second segments and one 90-second segment. No active trial may cross a
segment boundary. A four-second causal context resets only in registered
inactive time; state may not bridge a gap, reconnect, participant, cohort, or
choice washout.

The fixtures are procedural and streamed one trial at a time. They may not
materialize a dense 44-person raw recording or a full float32 backup.

## Frozen Conditions And Numerical Schedule

Exactly 17 conditions retain their parent identities: equal/source priors,
cue, timing, EOG, oral EMG, microphone, all peripheral `P`, central EEG,
posterior EEG, `P + residual central EEG`, `P + class-destroyed residual EEG`,
prechoice/early EEG, null/rest, language only, neural plus language, and
deranged-neural plus language.

Each complete participant is a zero-calibration holdout. Prompted and
free-choice prediction inventories are separate, yielding 1,428 prediction
sets and 91,392 prediction rows per replay. The fixed compact source-scaled
forward bandpower plus multinomial L2 logistic schedule is the only eligible
family. Probability calibration is scalar temperature calibration fit only on
source-participant out-of-fold predictions. Same-row, held-out-person,
replication, shadow, live, or post-target calibration refuses.

Seven shortcut fixtures are required: one EEG-only positive mechanical
fixture and six negative fixtures where only EOG, oral EMG, microphone, cue,
timing, or language context carries the command. These routes test control
logic only and are not scientific outcomes.

## Scoring And Live Semantics

For participant `i`, the primary margin is:

```text
m_i = min(LL_P_i - LL_P_plus_EEG_i,
          LL_P_plus_deranged_EEG_i - LL_P_plus_EEG_i)
```

The cohort gate uses the unweighted mean of the 21 margins, `m_i > 0` for the
15-of-21 consistency gate, and exhaustive one-sided sign flipping of the same
21 values with ties included conservatively. Balanced accuracy is aggregated
participant-first and must clear its parent margin. Pooled rows cannot rescue
a participant-macro failure, and the cohorts cannot rescue one another.

Every assigned active-intent row must freeze a four-class probability vector.
A missing, invalid, or nonfinite vector receives the frozen maximum log loss,
zero accuracy credit, and uncovered status; it is never dropped. Abstention is
scored separately from the probability vector.

Coverage is the participant-macro fraction of all assigned active-intent
episodes producing a stable commit by the frozen deadline, correct or not.
Invalid trials count uncovered. Overall coverage must reach 70%, every command
must reach at least 50%, and command-conditional coverage is reported.

Every stable commit during washout, prompted/free-choice no-intent, rest, and
registered inactive intertrial time is false. Repeated commits after the first
in one episode are chatter and also false. Dropped or invalid inactive time
remains in the denominator.

Stable-commit latency runs from photodiode-confirmed generic intention-window
onset to presentation. Processing overhead runs from the newest contributing
source sample to presentation. Missing clock maps fail. Noncommits are
right-censored and remain represented through the separate coverage gate.

## Adversarial Qualification

Two clean child-process replays must be byte-equivalent after removing only
explicit volatile resource measurements. Each replay executes every registered
refusal family once with the exact `COMM-P0-G:<family>` wrapper identity.

The 70 refusal families cover:

- target leakage and side channels;
- causality, context, partition invariance, gaps, and state reset;
- sensor roles, geometry, synchronized sharding, microphone, trigger, and
  photodiode;
- participant/cohort overlap, exclusions, calibration, and pooled rescue;
- clocks, samples, correction ledgers, deadlines, and latency ordering;
- raw, derivative, temporary, public, free-space, publication, and cleanup
  caps;
- voice, identity, path, secret, and individual-output privacy;
- protocol/prediction hashes, inventory, probability, freeze, and replay;
- scorer capability, row matching, delivery order, and one-shot behavior; and
- coverage, false commits, dropped chunks, latency, unchanged live state, and
  accuracy-only overclaim.

Acceptance requires 140 exact refusal observations, zero malformed accepts,
zero wrong-wrapper accepts, zero post-refusal mutation, two target deliveries
and scores per replay, and zero post-target update, rerun, or substitution.

## Resource Envelope

- one CPU thread, one worker, one numerical job;
- 180 seconds wall time;
- 512 MiB peak process-tree RSS;
- 128 MiB generated input;
- 128 MiB private generated output;
- 256 MiB temporary disk;
- 1 MiB public aggregate output;
- zero network bytes; and
- zero retained generated payload after proof publication.

Any cap breach refuses and consumes the invocation. Only invocation-created
temporary generated files may be removed.

## Claim Boundary

A pass would establish only that fictional study mechanics are deterministic,
bounded, target-firewalled, causal by construction, and fail closed under the
registered attacks.

It would not establish real synchronization, signal quality, communication
decoding, EEG information beyond peripheral signals, unseen-person
generalization, independent replication, actual live latency, device
performance, portability, home use, clinical value, or benefit to a person.
