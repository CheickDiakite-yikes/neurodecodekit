# IACKD Source Semantics Generated-Fixture Result

Date: 2026-08-10

Status: **H3 generated-fixture qualification complete; prospective policy
mechanics passed; no real reader or scientific result**

Lane: **IACKD-H3 Source Semantics Policy**

Registry: `registries/iackd_source_semantics_result.v0.json`

## Green Proof Chain

Research `ed5ce8292c2c1dc842898023cfe8cb608e9d4476` passed Base Python
job `93639606343` and Optional Neuro Readers job `93639606403` in CI
`31445790741` before implementation.

Exact implementation `8c5784ad3e664f816899e2f1139600b2c66a8232` then passed
Base Python job `93642969190` and Optional Neuro Readers job `93642969143`
in CI `31446902756` before the measured closeout.

## Preflight Record

The first CLI invocation used a parent presented by macOS as a symbolic link.
The exclusive writer refused it at `IACKDS-F14` before loading the policy,
building a fixture, or creating output. This is a passed fail-closed preflight,
not a semantic qualification or partial result.

The output was moved to a regular temporary directory. One semantic
qualification then ran successfully. There was no retry or rerun after any
fixture was built or validated.

## Measured Qualification

The one successful closeout produced and validated two deterministic,
target-free metadata fixtures:

| Fixture | Rows | Source EEG | Source MISC | Predictive EEG | Geometry available |
|---|---:|---:|---:|---:|---:|
| generated-29-row-v0 | 29 | 26 | 3 | 26 | 26 |
| generated-31-row-v0 | 31 | 28 | 3 | 26 | 28 |

Both fixtures preserved the fixed 26-channel predictive output order. The
31-row fixture added M1/M2 as source-typed EEG with finite geometry but kept
both out of the predictive mask. HEOG, VEOG, and Trigger remained source-typed
MISC and nonpredictive.

Five derivative bindings were created independently for each fixture:

- source order;
- source-type counts and BIDS version;
- functional roles;
- model-inclusion mask; and
- geometry-availability mask.

The replayed aggregate summaries were byte-semantically identical, with
summary-set SHA-256
`8e0532571cec9fa17b30549342d3cd03b2ea299d4c19fa5d758ac993f845900e`.

## Adversarial Result

All 13 generated mutations reached their registered refusal. They covered 12
distinct classes because BIDS-version drift and newer MISC count spelling both
correctly route to the same version/count-field refusal. The suite separately
rejected malformed fixture structure, source-order drift, duplicate identity,
source-type drift, sidecar-count drift, reference drift, required-geometry
loss, derivative-hash drift, target leakage, functional-role overlap, and
predictive-mask drift.

## Resources

- generated input: 6,093 bytes;
- generated report: 6,834 bytes;
- generated channel rows: 60;
- semantic validation passes: 4;
- mutation attempts: 13;
- distinct refusal classes: 12;
- runtime through report build: 0.007473916979506612 seconds;
- peak RSS through report build: 20,250,624 bytes;
- CPU threads/workers/numerical jobs: 1/1/1;
- network bytes: 0;
- real or public metadata requests: 0;
- local IACKD path operations: 0;
- signal/event/trajectory/target operations: 0;
- feature/model/training/inference/prediction/score operations: 0; and
- provider/device/hardware/release/claim operations: 0.

Producer causality is not applicable to this metadata policy qualification.
End-to-end latency was not measured. The temporary report had SHA-256
`2efe33591838f1434a3bcc8d65f3e91dd7eaf6cbba10c66ddf741c98ad75d8c2`
and was removed after validation and evidence capture; it is not committed.

## What Passed

All 13 acceptance gates passed:

1. green research was bound;
2. the canonical policy hash was exact;
3. BIDS version and count-field spelling were exact;
4. both 29-row and 31-row groups passed;
5. both groups kept exactly 26 predictive EEG channels;
6. source type, functional role, and model inclusion stayed separate;
7. all five derivative bindings were present;
8. deterministic replay passed;
9. twelve distinct refusal classes passed;
10. target leakage was refused;
11. forbidden access counters stayed zero;
12. runtime and RSS caps passed; and
13. the output cap passed.

## What This Resolves

H3 resolves the engineering ambiguity left by H2: a channel may remain
source-typed MISC for BIDS count reconciliation while receiving a separate
ocular-control or trigger-control function and remaining outside the predictive
matrix. The policy no longer needs to rewrite source truth from channel names.

This does not retroactively change H2's `IACKDR-R1` route or make its rejected
candidate hash admissible. Generated source-order hashes demonstrate binding
mechanics only; no exact real IACKD source order was asserted.

## Next Evidence Gate

A future corrected IACKD experiment must be separately named, prospective, and
bind the H3 policy hash before any signal-bearing access. It must use a new
Tier C decision for any public or local payload, preserve the fixed 26-channel
predictive matrix, keep M1/M2 and all three controls nonpredictive, and retain
the dual-reversal action-over-cue controls. H3 itself opens no reader, data,
model, target, or score surface.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a measured,
deterministic, version-aware source-semantics validator that preserves BIDS
source counts before functional-role and model-mask assignment and fails
closed across twelve generated error classes.

Scientific claim not established: no real or public IACKD body, local bundle,
signal, event, trajectory, target, model, prediction, or score was accessed,
so H3 establishes no neural effect, action decoding, brain-specific origin,
generalization, typing, language or thought decoding, real-time operation,
hardware capability, assistive benefit, or clinical use.
