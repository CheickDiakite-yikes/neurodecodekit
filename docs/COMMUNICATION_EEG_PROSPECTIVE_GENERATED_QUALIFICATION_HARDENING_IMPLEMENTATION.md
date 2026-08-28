# COMM-P0-G Qualification Hardening Implementation

Date: 2026-08-28

Status: **generated-only hardening milestone pending exact commit, push, and
remote CI; official qualification remains inactive**

Machine record:
`registries/communication_eeg_prospective_generated_qualification_hardening_implementation.v0.json`

## Added Engineering Capability

The reduced generated coordinator now exercises the model and scorer through
separate process capabilities:

- model folds receive target-free features with opaque item identifiers,
  source-participant labels, the frozen contract, and a write-only prediction
  descriptor;
- canonical prediction files are created without replacement, checked through
  no-follow parent traversal, and written in batches of at most 256 rows;
- a per-invocation HMAC attestation binds the exact contract, trials,
  predictions, live observations, file identities, inventory, and one-shot
  authorization before the target surface is created;
- the score child receives only preopened descriptors and imports no numerical,
  fitting, checkpoint, subprocess, path, or network implementation;
- targets are read only after attestation verification, and the output is one
  bounded aggregate record;
- process groups are sampled every 100 ms with no self-only monitoring
  fallback; and
- no-replace consumed-marker, activation-binding, output-cap, replay, and
  domain-refusal components are present while the official entry remains
  locked.

Parent-directory symlinks, wrong descriptor access modes, non-regular or
multi-link descriptors, HMAC or inode drift, malformed canonical input,
repeated delivery, monitor failure, deadline failure, and output replacement
refuse.

## Measured Development Replay

One disposable six-participant generated replay pair used three fictional
participants per cohort and the real descriptor-only model and score children.
It completed:

| Measure | Result |
|---|---:|
| Isolated replays | 2 |
| Prediction rows per replay | 13,056 |
| Prediction sets per replay | 204 |
| Refusal observations | 140 |
| Target deliveries / scores | 2 / 2 |
| Post-target updates | 0 |
| Runtime | 23.2238 s |
| Peak process-tree RSS | 169,869,312 bytes |
| Temporary private bytes, maximum replay | 11,758,349 bytes |
| Process-monitor samples | 162 |
| Network / real-data / device operations | 0 / 0 / 0 |
| Retained generated payload | 0 bytes |

The two 15-digest replay surfaces were equivalent. The coordinator and score
worker focused suite passed 25 tests. The repository-wide post-milestone
dependency-light suite passed 6,725 tests with 270 optional skips in 259.826
seconds.

## Remaining Activation Blockers

This is deliberately not labeled the official generated qualification:

1. Development scoring still materializes the complete prediction collection;
   the official path must stream score state without retaining all 91,392 rows.
2. The seven shortcut routes are explicit accounting records, but must become
   seven actual numerical fixture executions.
3. The durable consumed marker exists but is not yet wired before the first
   official fixture or model action.
4. A full-scale nonofficial rehearsal and a separate exact-green activation
   remain required before the one consumed official invocation.

The static `OFFICIAL_IMPLEMENTATION_ACTIVATED` lock remains false. No activation
record or official result exists.

## Boundary

Engineering capability added: generated predictions can now cross a
cryptographically bound, descriptor-only model-to-score path with isolated
target delivery and aggregate-only output.

Scientific claim not established: this work used fictional procedural signals
and establishes no communication decoding, EEG information beyond peripheral
controls, unseen-person generalization, independent replication, live-device
latency, hardware performance, or benefit to a person.

No real/private data, person, recording, network, provider, device, release, or
claim operation was authorized or performed. `DREYER-C5R-1-HL` remains the sole
active Tier C gate with all authority flags false.
