# COMM-P0-SYNC Amendment 1: Stable-Commit Coverage

Date: 2026-08-27

Status: **prospective correction pending its own remote CI; no operation
authorized**

Parent registration: `COMM-P0-SYNC-v0`

Machine amendment:
`registries/communication_eeg_prospective_synchronized_cohort_amendment_1.v0.json`

## Defect

The immutable human preregistration states a 60% minimum stable-commit coverage
at line 148. The immutable machine contract and its test both state 70%.
Leaving those values unresolved would let an implementation choose the easier
threshold after seeing generated or real behavior.

## Correction

The authoritative minimum is **70%**. The 60% sentence in the parent human
document is superseded only for this one field. Every other parent protocol,
sensor, cohort, target-firewall, control, statistical, live, storage, privacy,
authority, and claim boundary remains byte-for-byte unchanged.

The stricter value was already frozen in:

- `live_acceptance.stable_commit_coverage_fraction_minimum` in the machine
  contract; and
- the matching contract test.

Generated qualification design and implementation remain paused until this
amendment and the registration proof closeout are committed, pushed, and both
required CI jobs are green on the same exact commit.

## Non-Operation

This amendment performs no generated execution, recruitment, consent,
recording, device or voice operation, real/private access, signal or target
read, model run, training, inference, prediction freeze, scoring, provider
call, release, or scientific claim upgrade.

Engineering capability added: the live acceptance surface now has one
unambiguous stable-commit coverage threshold.

Scientific claim not established: a prospective threshold correction provides
no evidence of communication decoding, EEG information beyond peripheral
controls, unseen-person generalization, independent replication, causal live
decoding, hardware performance, or clinical value.
