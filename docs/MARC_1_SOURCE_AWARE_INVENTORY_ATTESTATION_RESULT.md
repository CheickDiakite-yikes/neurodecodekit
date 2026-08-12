# MARC1-SA1 Source-Aware Inventory Attestation Result

Date: 2026-08-12

Status: **registered generated closeout passed and consumed; no retry or rerun;
live metadata and payloads remain closed**

Registry:
`registries/marc1_source_aware_inventory_attestation_result.v0.json`

## Same Research Path

MARC1-SA1 is cohort-integrity work on the existing thought-to-text research
path, not a pivot. The path remains:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

This closeout makes the next public inventory check more diagnostic. It does
not substitute metadata mechanics for EEG evidence or language decoding.

## Evidence Order

Exact implementation commit
`feb3b839e879d2a9edcdcfe664c68b3c4ba236d6` passed both required jobs in
CI `31619037335` before the registered closeout:

```text
Base Python:             94188922905
Optional Neuro Readers: 94188922771
```

The closeout used that exact committed module and frozen contract. No source
rule, predicate, route, fixture, hash domain, threshold, resource cap, output
schema, or claim boundary changed between green proof and execution.

## Registered Execution

Exactly one fresh-process `qualify` invocation ran under the real system
temporary tree with one CPU thread, one worker, one numerical job, zero
network access, and zero real or private input. It generated only the six
registered fixture families and the 52 registered refusal cases.

The module acquired the output capability before repository or fixture work,
created exactly two temporary mode-`0600` files, inspected the aggregate
report exactly once, removed both files and its output directory, and returned
success. The caller then removed its empty invocation-created parent. The
closeout is consumed with no retry or rerun.

## Result

Constructed route `MARC1SA-G1` passed every registered gate:

```text
semantic families:                   6 / 6
aggregate predicates:              21 / 21
identity domains:                    7 / 7
refusal cases:                     52 / 52
acceptance gates:                  25 / 25
generated input bytes:             732,811 / 2 MiB
private output bytes:               95,392
public output bytes:                14,197
combined/incremental output bytes: 109,589 / 2 MiB / 4 MiB
internal runtime seconds:        0.053358083 / 30
reported peak RSS bytes:          27,885,568 / 256 MiB
external wall seconds:                  0.13
external maximum RSS bytes:       27,983,872
network bytes:                             0
payload bytes:                             0
retained output files:                     0
```

The deterministic private manifest hash remained
`dd267efdce39ae20002d4e251f19cac439ce316c61c7f9c1bda2bd9e41e2a7c5`.
The minimal CLI intentionally did not emit the ephemeral public report hash,
and exact cleanup completed before caller access. That hash is recorded as
unavailable instead of being reconstructed through an unauthorized rerun.

## Family Outcomes

| Generated family | Route | Meaning |
|---|---|---|
| documented five-field public core | `MARC1SA-R2` | structurally usable without requiring MD5 |
| observed seven-field extension | `MARC1SA-R1` | supplied and computed MD5 provenance agrees |
| partial optional MD5 extension | `MARC1SA-R2` | missing optional MD5 remains explicit and nonblocking |
| one historical drift | `MARC1SA-R3` | the declared-byte mismatch is localized |
| multiple historical drifts | `MARC1SA-R3` | every frozen cohort mismatch is reported together |
| unknown non-target extension | `MARC1SA-R4` | selection is blocked without retaining its value |

All 52 malformed-input, proof, target-firewall, row, URL, MD5, output, and
resource mutations refused in their registered route class. Row and key
reordering preserved semantic identity. The raw transport hash remained
provenance-only and separate from the six semantic identity domains.

## What This Proves

The generated attestor can distinguish source-schema compatibility, optional
checksum provenance, target-free cohort identity, and later acquired-byte
integrity without publishing rows, names, IDs, URLs, checksums, participants,
or outcomes. It fails closed on unknown extensions and localizes ordinary
historical drift instead of collapsing every mismatch into one opaque error.

The output-capability, strict-JSON, recursive target-firewall, deterministic
replay, aggregate privacy, one-thread resource, and exact-cleanup mechanisms
all compose end to end on generated inputs.

## What Did Not Happen

The run made zero Figshare requests, DNS queries, network-body reads, private
or consumed-root operations, participant-archive reads, payload reads, EEG
reads, channel, geometry, event, target, or label reads, cache operations,
feature extraction, model runs, training runs, prediction sets, scores,
provider calls, hardware operations, retries, reruns, releases, or claim
upgrades. It did not contact another project.

No live source inventory was checked. Acquired payload SHA-256, signal quality,
neural effect, cue resistance, held-out language accuracy, model advantage,
unseen-person generalization, real-time behavior, portable hardware, and
thought-to-text performance remain unavailable.

## Verification

- Eleven result-record invariants pass.
- The focused contract/behavior/implementation/result slice passes 53 tests
  and 36 subtests.
- All MARC tests pass 733 tests and 801 subtests.
- The complete dependency-light suite passes 2,908 tests with 35 expected
  skips and 1,614 subtests in 70.37 seconds of pytest runtime and 72.21
  seconds external wall time at 701,775,872-byte maximum RSS.
- The isolated optional-neuro suite passes 2,896 tests with 47 expected skips
  and 1,621 subtests in 77.47 seconds of pytest runtime and 78.39 seconds
  external wall time at 589,152,256-byte maximum RSS.
- Both comparable complete suites add exactly 11 result tests and zero skips
  over the green implementation baseline.
- Ruff, compilation, all registry JSON parsing, CLI help/plan, immutable
  artifact bindings, and `git diff --check` pass.

## Next Gate

1. Test, commit, push, and require both remote CI jobs green for this consumed
   aggregate result.
2. Only after that proof, prepare one all-false Tier C packet for a separately
   implemented source-aware live metadata wrapper and one bounded response.
3. Require a fresh packet-bound maintainer decision and green wrapper before
   any source request.

Payload acquisition remains ineligible. The consumed MARC1-LM1 root remains
forbidden, and no live response, archive, EEG payload, target, model, or score
may be opened from this result alone.

Engineering capability added: the registered generated closeout proves that
source-aware schema handling, optional checksum provenance, aggregate drift
localization, privacy controls, and resource caps replay together end to end.

Scientific claim not established: no live metadata, EEG payload, neural
signal, target, model prediction, score, language decoding, or thought-to-text
result was produced.
