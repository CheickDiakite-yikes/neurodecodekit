# BNCI-C3C5-1 Artifact-Only Postmortem Protocol

Date: 2026-08-25

Status: **Frozen Tier A post-outcome descriptive analysis. It authorizes no
private artifact access, real-data operation, model run, score, or claim
upgrade.**

Contract:

- `registries/bnci_2014_001_artifact_postmortem_contract.v0.json`

## Purpose

The consumed Stage T result contains enough aggregate evidence to identify
which questions a fresh replication must answer. This postmortem converts that
evidence into a deterministic failure map without reopening any private Stage
Q, P, or T artifact.

The analysis is explicitly post-outcome and descriptive. It cannot establish a
causal root cause, select a better model from consumed targets, or strengthen a
scientific claim.

## Exact Input

The sole analytical input is the committed 4,951-byte aggregate Stage T result:

`registries/bnci_2014_001_stage_t_result.v0.json`

Its required SHA-256 is
`e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2`.
The analyzer refuses a byte, schema, status, route, or contract mismatch. It
also verifies from fresh Git remote and GitHub Actions metadata that its exact
implementation commit is the remote branch head and both required CI jobs are
green before reading the analytical input. It never reads
individual targets, predictions, probabilities, participant outcomes, private
derivatives, checkpoints, MAT files, or ignored paths.

## Frozen Questions

1. Did the selected late EEG candidate carry aggregate protocol information
   beyond no-signal and timing controls?
2. Was that information spatially specific relative to posterior, central, and
   frontal views?
3. Was late activity stronger than pre-cue and early-cue activity?
4. Did channel, trial, and source-label derangements destroy the candidate
   signal?
5. Were its probabilities reliable relative to no-signal and timing models?
6. Did EEG add a sufficiently large and consistent increment beyond recorded
   EOG and deranged EEG?

The report applies the six fixed diagnostic rules in the contract. Multiple
failure patterns may coexist; no single pattern is promoted to causal root
cause.

## Resource And Claim Boundary

The pass is limited to one CPU thread, one worker, 30 seconds, 256 MiB peak
RSS, and 1 MiB public output. Only the pre-analysis Git/GitHub metadata proof
may use the network. Analysis network, downloads, training, inference, scoring,
target delivery, reruns, and scientific claim upgrades are all zero.

Maximum meaning: a reproducible descriptive map of one already committed
aggregate result. No unseen-person EEG decoding, EEG information beyond EOG,
brain-specific origin, movement intention, language decoding, live behavior,
hardware result, or clinical utility can be established.
