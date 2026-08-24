# EEGMMIDB-UG1 Unseen-Participant Generalization Research

Date: 2026-08-24

Status: **Tier A research complete; no new EDF metadata or payload requested,
no retained source payload opened, and no model trained or scored**

Machine record:

- `registries/eegmmidb_unseen_participant_generalization_research.v0.json`

## Decision

Freeze one participant-independent low-frequency model using only S001-S015
fit runs, then evaluate it once on run 11/12 from S016-S030 with zero
held-out-person calibration, normalization fitting, threshold fitting,
selection, or update.

This is the shortest credible path to a new result that directly tests one of
the project's five open claims: generalization to completely unseen people.
It is not a motor-intention or cortical-origin experiment.

## Why This Is Next

WO9R established the strongest real EEG result in the repository: execution
balanced accuracy `0.680975` and imagery `0.728014` across twelve held-out-run
participants, both above approximately chance no-signal controls. But every
participant received a separately fitted model. WO9R therefore established
repeatable within-person task information, not transfer to an unseen person.

The same result also exposed its main confound. Early-cue accuracy was
`0.762865`, the frontal proxy reached `0.671821`, and the central view reached
`0.647575`. A positive unseen-person result may still be driven by visual cue,
ocular, or broadly distributed task signals. The claim ceiling must say
exactly that.

The alternative IACKD reversal remains scientifically stronger for action
versus cue attribution because it records EOG and reverses visual and action
direction. It is not the immediate lane: its live metadata path has twice
failed closed before payload analysis, and its selected acquisition is
7,249,113,684 bytes. EEGMMIDB-UG1 reuses a proven small public source and needs
at most 36 additional EDFs under a 256 MiB cap.

## Primary-Source Basis

PhysioNet EEGMMIDB v1.0.0 contains 64 EEG channels sampled at 160 Hz plus EDF+
annotations. In unilateral fist runs, T1 denotes left-fist movement or imagery
and T2 denotes right-fist movement or imagery. Runs 03/07/11 are executed
left/right fist trials; runs 04/08/12 are imagined left/right fist trials.

Source: [PhysioNet EEGMMIDB v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)

The dataset is public under the Open Data Commons Attribution License v1.0.
This research made no EDF request and did not inspect any local retained
payload.

## Frozen Cohorts

| Role | Participants | Execution runs | Imagery runs | Maximum rows |
| --- | --- | --- | --- | ---: |
| Source fit | S001-S015 | 03, 07 | 04, 08 | 450 + 450 |
| Fresh final | S016-S030 | 11 | 12 | 225 + 225 |

Only T1/T2 rows enter the task-direction study. T0 is excluded. Participant is
the inference unit. The previously scored S001-S015 run-11/run-12 targets are
forbidden from source fitting, qualification, checkpoint creation, or model
selection.

Tracked acquisition records cover 54 of the 60 source-fit EDFs totaling
138,333,504 bytes. The only missing source files are S001-S003 runs 04/08.
The fresh final set contains S016-S030 runs 11/12. Exact remote sizes and
local hashes are deliberately not invented; a later authorized metadata stage
must freeze them before payload acquisition.

## Fixed Model

Separate execution and imagery models use one nonselecting family:

```text
reference:          instantaneous common average over exact 64-channel order
filter:             fourth-order causal Butterworth 0.5-4 Hz SOS
application:        continuous run before event windowing
decision window:    [+1.0, +3.0) seconds from cue onset
features/channel:   four 500 ms means plus one whole-window slope
feature dimension:  320
standardization:    fit only on S001-S015 source rows
classifier:         pooled shrinkage LDA
solver/shrinkage:   lsqr / 0.1
class priors:       equal
model candidates:   1
fresh calibration:  none
```

Participant identity, filename, run identity, event ordinal, elapsed time, and
previous interval are forbidden primary features. No ICA, covariance
alignment, test-person normalization, channel rejection, hyperparameter
search, checkpoint selection, or fallback is allowed.

## Source-Only Stop Gate

Before acquiring S016-S030, run 15-fold leave-one-source-participant-out
qualification. Every fold refits its scaler and classifier using fourteen
source participants. The one candidate proceeds only if execution source-LOSO:

- participant-macro balanced accuracy is at least `0.57`;
- the macro margin over the stronger of no-signal and timing-only is at least
  `0.07`;
- at least 10/15 source participants are strictly above `0.50`; and
- the exact one-sided participant sign-flip p-value is at most `0.05`.

Failure parks UG1 before any fresh-participant payload request. Imagery is
reported but cannot rescue failed source execution.

## Frozen Controls

Primary and controls must freeze together:

- source-only equal-prior no-signal;
- timing-only from event ordinal, elapsed run time, and previous interval;
- exact-zero final features;
- one fixed 64-channel permutation;
- one nonwrapping event displacement with zero fill;
- one fixed source-label derangement;
- pre-cue `[-2,0)`;
- early-cue `[0,+1)`; and
- fixed central, frontal, and occipital channel views.

For participant `i`:

```text
B_i = max(no-signal BA, timing-only BA)
C_i = max(zero BA, channel-deranged BA,
          displaced BA, deranged-label BA)
```

## Fresh Final Gates

Execution is primary and must satisfy every gate:

- exactly 15 unseen participants and 225 run-11 T1/T2 events;
- pooled and participant-macro balanced accuracy at least `0.60`;
- macro primary-minus-`B_i` margin at least `0.10`;
- at least 11/15 participants strictly above `0.50`;
- exact one-sided participant sign-flip p-value at most `0.01`;
- macro primary-minus-`C_i` margin at least `0.02`;
- exact paired participant sign-flip against `C_i` at most `0.05`; and
- zero integrity, target-firewall, freeze, resource, or protocol violations.

Imagery is a prespecified upgrade gate with the same accuracy and margin floors
and participant p-value at most `0.05`. It cannot rescue failed execution.

## Evidence Order

1. Generated and mocked-transport implementation qualification only.
2. One metadata-only pass over the 36 exact missing/fresh paths.
3. Conditional acquisition of six missing source-fit EDFs only.
4. Source-only LOSO, full source refit, checkpoint/control freeze, commit,
   push, and two green CI jobs.
5. Only then acquire the 30 fresh S016-S030 final EDFs.
6. Isolate T1/T2 targets while target-blind code receives timing and signal.
7. Produce every primary/control prediction with zero adaptation.
8. Commit and remotely green an aggregate hash-only prediction freeze.
9. Deliver the same 450 sealed targets once and score once.
10. Stop without rerun or post-target update.

## Outcome Router

| Route | Maximum meaning |
| --- | --- |
| `EEGMMIDBUG1-R0` | Integrity, metadata, payload, firewall, freeze, or resource failure. |
| `EEGMMIDBUG1-R1` | Source-only cross-person gate failed; fresh payload was not acquired. |
| `EEGMMIDBUG1-R2` | Fresh execution did not beat no-signal and fixed controls. |
| `EEGMMIDBUG1-R3` | Execution task direction generalized with zero calibration to 15 unseen participants. |
| `EEGMMIDBUG1-R4` | The same strict unseen-participant result held for execution and imagery. |

Even R4 proves only participant-independent EEGMMIDB protocol-condition
prediction. It does not establish movement intention, motor-cortex origin,
neural information beyond eyes or peripheral signals, independent-dataset
replication, language or thought decoding, live operation, or portable
hardware.

## Resource Envelope

```text
threads / workers / jobs:     1 / 1 / 1
new payload requests:         at most 36, no retry
new payload bytes:            at most 256 MiB
incremental disk:             at most 512 MiB
private derivatives:          at most 128 MiB
public artifacts:             at most 2 MiB
peak RSS:                     below 1 GiB
model parameter-update fits:  at most 300
prediction sets:              at most 640
network during analysis:      0 bytes
final target deliveries:      1
final scoring events:         1
reruns / post-target updates: 0 / 0
```

Engineering capability added: a source-train/fresh-person architecture now
turns the existing participant-specific EEG effect into a strict
zero-calibration generalization test with a pre-acquisition stop gate.

Scientific claim not established: no new metadata, payload, target, model,
prediction, or score was accessed, so unseen-person generalization and every
other new scientific claim remain untested.
