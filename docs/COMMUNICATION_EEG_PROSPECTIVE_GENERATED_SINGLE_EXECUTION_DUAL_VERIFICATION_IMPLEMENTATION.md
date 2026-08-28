# COMM-P0-G FS3 Dual-Verification Implementation

Date: 2026-08-28

Gate: `COMM-P0-G-FS3-v0`

Status: generated-only implementation and reduced qualification complete;
full-scale rehearsal and official qualification not executed

## Added implementation

The FS3 implementation is additive. It does not modify the frozen COMM-P0
model, features, splits, nuisance fits, thresholds, scoring rules, penalties,
official activation lock, or consumed FS2 artifacts.

It adds:

- a strict FS3 contract loader and target-free plan surface;
- a reduced qualification coordinator that launches two isolated fictional
  producer children and two separate verifier children;
- a descriptor-only verifier/scorer worker that accepts no paths and receives
  only preopened contract, trial-manifest, prediction-stream, freeze,
  target-envelope, live-observation, HMAC-key, and producer-aggregate
  descriptors;
- independent streaming reconstruction of the prediction freeze, HMAC and file
  identity verification, one separate target delivery per cohort, aggregate
  rescoring, and byte-exact comparison with the producer aggregate;
- explicit zero counters for fits, transforms, inference, calibration,
  threshold selection, prediction creation, parameter updates, and language-
  model operations inside the verifier; and
- a sidecar `plan` and `qualify-reduced` CLI with no full-scale or official run
  command.

The verifier process imports only the pure score modules and standard-library
helpers. It rejects any loaded numerical or model-worker module, wrong
descriptor mode or identity, bad HMAC, malformed stream, invalid probability,
missing/duplicate row, target-before-freeze operation, aggregate mismatch, or
row-level public output.

## Reduced qualification

The permitted generated development qualification ran exactly two isolated
producer/verifier pairs with three fictional participants per cohort. It used
one CPU thread, one worker, and one numerical job.

| Measurement | Result |
|---|---:|
| Isolated model replays | 2 |
| Isolated verifier replays | 2 |
| Prediction rows per replay | 13,056 |
| Prediction sets per replay | 204 |
| Refusal observations | 140 |
| Producer target deliveries / scores | 4 / 4 |
| Verifier target deliveries / scores | 4 / 4 |
| Runtime | 72.67009999998845 s |
| Peak process-tree RSS | 239,075,328 bytes |
| Mandatory monitor samples | 770 |
| Network requests / bytes | 0 / 0 |
| Retained generated payload bytes | 0 |
| Post-target updates | 0 |

Both producer canonical surfaces matched. Both verifier aggregate hashes
matched, and each verifier aggregate matched its producer byte for byte.
Producer and verifier process identities were distinct. The first sandboxed
launch refused before numerical work because `ps` was not permitted; the same
non-durable generated development check then ran with the mandatory read-only
process monitor available. No FS3 one-shot receipt exists, so the full-scale
run identity remains unconsumed and closed.

## Remaining barriers

This implementation and its machine record must be committed, pushed, pass
both required CI jobs, and reach GitHub `main`. A separate proof-only closeout
must then bind the exact green implementation identity. Only after that barrier
may one full-scale, generated-only FS3 rehearsal be considered. That future
attempt must create its durable receipt before work and remains one-shot.

No full 21-person-per-cohort producer ran here. No official qualification,
activation, official marker, real/private path, real EEG, human target, device,
network, provider, release, or end-to-end latency operation occurred.

Engineering capability added: NeuroDecodeKit can hand a frozen fictional
prediction transcript to a separate zero-model process that independently
verifies and reproduces its aggregate score.

Scientific claim not established: this generated qualification accessed no
real EEG or human target and establishes no communication decoding, EEG-beyond-
peripheral advantage, unseen-person generalization, independent replication,
causal live operation, hardware performance, or clinical value.
