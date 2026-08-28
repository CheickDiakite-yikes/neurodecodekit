# COMM-P0-G Numerical And Scorer Implementation

Date: 2026-08-28

Status: **numerical/scorer milestone pending remote CI; official generated
qualification not authorized or executed**

Machine record:
`registries/communication_eeg_prospective_generated_numerical_scorer_implementation.v0.json`

## Green Core Barrier

Core implementation commit `9378421afb0656df188fc63ca28b6009535200bd`
passed Base Python job `98746563630`, Optional Neuro Readers job
`98746563472`, and CI `33139382019`, then reached GitHub `main`. This additive
milestone leaves all core artifacts byte-identical.

## Compact Numerical Schedule

`comm_p0_generated_numerical.py` implements the exact schedule algebra without
adding a base dependency:

- 21 participant-held-out folds per cohort and 42 folds total;
- within each fold, 16 source participants for fitting, four disjoint source
  participants for scalar-temperature calibration, and one held-out person;
- two endpoint-specific source-only ridge residualizers;
- one source prior plus 15 fixed multinomial L2 logistic conditions;
- one deterministic scalar-temperature calibration per classifier;
- one source-only, no-fixed-point class rotation for the class-destroyed EEG
  conditions, while calibration and held-out EEG remain intact and
  target-blind;
- 34 prediction sets and 2,176 prediction rows per fold; and
- exact full-replay counters of 42 priors, 84 residualizers, 630 classifiers,
  630 temperature fits, 1,428 prediction sets, and 91,392 prediction rows.

The generated fixture is deliberately mechanical. Only the central EEG view
carries class information in the default positive case. EOG, oral EMG,
microphone, posterior EEG, timing, prechoice EEG, and language views contain
deterministic target-free noise or fixed context. Prompted cue information is
available only through the registered cue/peripheral conditions and is treated
as a leakage ceiling, never as neural evidence.

## Post-Freeze Scorer

`comm_p0_generated_scorer.py` derives every participant metric directly from
frozen prediction tuples. It adds:

- exact cohort, participant, item, endpoint, phase, condition, and probability
  identity on every prediction row;
- separate discovery and independent-replication aggregate scores;
- all discovery active rows treated as hidden output, with replication shadow
  and live stages kept separate;
- the exact participant-first minimum log-loss margin, strongest-control
  balanced-accuracy margin, consistency count, and exhaustive sign flip;
- a non-rescuing prompted directional check whose balanced-accuracy comparator
  excludes the known class cue and reports that cue as a leakage ceiling;
- replication live coverage, per-command coverage, false-commit, drop,
  deadline, balanced-accuracy, log-loss, abstention, and latency summaries; and
- explicit `end_to_end_latency_measured=false` because generated clocks are not
  device latency.

The scorer returns aggregate cohort records only. It emits no participant
identity, individual prediction, probability, target, or outcome.

## Development Evidence

A reduced four-participant-per-cohort schedule exercised 120 classifier fits,
120 scalar-temperature fits, 16 residualizer fits, 272 prediction sets, and
17,408 target-blind prediction rows per replay. Two deterministic schedule
replays plus scoring completed in the focused ten-test suite in approximately
4.3 seconds under one thread.

On the deliberately positive mechanical fixture, free-choice residual central
EEG reached 100% descriptive accuracy while the peripheral, posterior, cue,
timing, language, prechoice, and source-class-destroyed controls remained near
25%. This is a synthetic control result only. It demonstrates that the
software can accept a true incremental signal and reject shortcuts; it says
nothing about human EEG.

## Remaining Barrier

The official coordinator is still absent. Next implementation must add two
sequential isolated replay processes, a separate post-freeze scorer child,
real malformed mutations for all 70 refusal families, a complete 15-digest
equivalence surface, process-tree resource monitoring, activation validation,
durable consumption, no-replace publication, and invocation-owned cleanup.

No official full replay was run. Human/device operations, real/private path
operations, real signal reads, provider or network bytes, official target
deliveries, official scores, releases, and scientific claim upgrades remain
zero.

Engineering capability added: NeuroDecodeKit now has the complete compact
participant-held-out generated model schedule and an aggregate-only scorer that
keeps discovery, replication, prompted, free-choice, shadow, and live evidence
separate.

Scientific claim not established: all measurements came from deliberately
procedural synthetic features, so this milestone establishes no human
communication decoding, EEG-beyond-peripheral information, unseen-person
generalization, independent replication, real-time device performance, or
clinical value.
