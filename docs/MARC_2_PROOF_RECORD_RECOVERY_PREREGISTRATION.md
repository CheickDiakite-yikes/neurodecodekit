# MARC2-FW1B Proof-Record Recovery Preregistration

Date: 2026-08-13

Status: **Frozen generated-only contract; no private source, payload, neural,
target, model, or score access is authorized**

Registry:
`registries/marc2_proof_record_recovery_contract.v0.json`

## Purpose

The sole `MARC2-FW1A` private-selection invocation failed closed at
`MARC2FWS-F00` before its machine gate or any retained-path operation. The
executor required a top-level implementation-record field:

```json
"lane_id": "MARC2-FW1A"
```

but the committed implementation registry omitted that field. The old lane is
consumed and cannot be edited, retried, repaired, resumed, or reused.

`MARC2-FW1B` addresses only that proof-record defect. It freezes an explicit
schema for a new implementation record and requires the exact same validator
entry point to accept a generated candidate before that validator can ever be
placed behind a future private-data decision.

## Question

Can one dependency-free validator strictly accept the complete canonical
`MARC2-FW1B` implementation record, reject 32 ordered malformed variants, bind
every tracked artifact without circular self-hashing, and prove that generated
qualification and a future additive live wrapper use the same validation entry
point?

This is an engineering-interface question. It is not an EEG experiment.

## Frozen Record Identity

The generated candidate implementation record must contain every required
top-level field exactly once:

1. `schema_name`
2. `schema_version`
3. `lane_id`
4. `implementation_id`
5. `recorded_at_local`
6. `status`
7. `predecessor_proof`
8. `tracked_file_hashes`
9. `implementation_surface`
10. `generated_qualification`
11. `execution_state`
12. `authorization_flags`
13. `access_counters`
14. `next_gate`
15. `claim_boundary`

The exact identity values are:

```text
schema_name:      neurodecodekit.marc2_proof_record_recovery_implementation
schema_version:   0.1.0
lane_id:          MARC2-FW1B
implementation_id:MARC-2-FW1B-proof-record-recovery-implementation-v0
status:           generated_shared_proof_validator_qualified_no_private_authority
```

Unknown top-level fields fail closed. Strict JSON rejects duplicate keys, a
UTF-8 BOM, NUL bytes, non-finite numbers, non-object roots, malformed UTF-8,
and trailing content.

## Predecessor Boundary

The validator binds the consumed `MARC2-FW1A` result, not its reusable
implementation:

```text
result commit:       4f08553eaa27c83e3f9ace9226dce64d933be1d4
CI run:              31766526262
Base Python job:     94663482811
Optional Neuro job: 94663482786
result registry SHA: 56ccc534ce682b45a3dcea6f4e301261a060ccf0ebd6f8f34a7dbed9071899c5
```

The predecessor remains consumed. The recovery cannot call its executor,
modify its registry, create its output root, or inspect its retained source.

## Tracked-Artifact Rules

Every candidate binding must use a unique normalized repository-relative path
and a lowercase 64-character SHA-256. Absolute paths, `~`, `.` or `..`
components, duplicate paths, symlinks, non-regular files, missing files, and
hash mismatches refuse.

The candidate implementation registry cannot bind itself. This explicit
anti-self-binding rule avoids a circular digest that can never be satisfied.
The registry is instead supplied as the separately hashed input to the shared
validator. Every other declared tracked artifact is verified from bytes.

## Shared-Validator Rule

The future module may expose only `plan`, `qualify`, and `inspect`. It must not
expose `execute`, a private path, a URL, a network client, an archive reader, a
signal reader, a target interface, or a model interface.

One public function is the proof authority:

```text
validate_implementation_record
```

The generated qualification must call this exact function. A future additive
live wrapper must import and call the same function by its frozen module and
symbol identity; it may not copy, fork, weaken, alias around, or reimplement
the validator. This contract does not implement or authorize that wrapper.

## Generated Qualification

The canonical generated record must pass twice with byte-identical canonical
summary output. The second pass is deterministic replay, not a second real
execution. Qualification must report:

- the input and output byte counts;
- runtime and peak RSS;
- exactly one CPU thread, one worker, and one numerical job;
- the validator module, symbol, and source SHA-256;
- all 32 ordered mutation outcomes;
- zero private, real, network, payload, neural, target, model, and score
  counters; and
- explicit unavailable fields and claim boundaries.

No generated artifact is scientific evidence.

## Ordered Mutation Matrix

The implementation must reject these exact cases in this order:

1. `schema_name_missing`
2. `schema_name_wrong`
3. `schema_version_wrong`
4. `lane_id_missing`
5. `lane_id_wrong`
6. `implementation_id_wrong`
7. `status_wrong`
8. `predecessor_commit_wrong`
9. `predecessor_CI_or_job_wrong`
10. `predecessor_result_hash_wrong`
11. `tracked_files_empty`
12. `tracked_path_absolute`
13. `tracked_path_traversal`
14. `tracked_path_duplicate`
15. `tracked_hash_malformed`
16. `tracked_hash_mismatch`
17. `registry_self_binding`
18. `qualification_all_gates_false`
19. `qualification_selector_count_wrong`
20. `qualification_wrapper_count_wrong`
21. `qualification_mutation_order_wrong`
22. `execution_already_consumed`
23. `execution_limit_wrong`
24. `retry_limit_nonzero`
25. `access_counter_nonzero`
26. `private_authority_enabled`
27. `payload_or_MARC2_FW2_authority_enabled`
28. `next_gate_wrong`
29. `claim_boundary_missing`
30. `proof_commit_malformed_or_HEAD_mismatch`
31. `proof_CI_job_or_registry_hash_mismatch`
32. `generated_closure_uses_different_validator`

## Routes

| Route | Meaning |
|---|---|
| `MARC2FWR-F00` | schema or fixed identity differs |
| `MARC2FWR-F01` | strict JSON or tracked-artifact binding differs |
| `MARC2FWR-F02` | predecessor or remote-green proof differs |
| `MARC2FWR-F03` | generated qualification or deterministic replay differs |
| `MARC2FWR-F04` | execution state, authority, access counter, or next gate differs |
| `MARC2FWR-F05` | shared-validator closure or claim boundary differs |
| `MARC2FWR-G1` | generated candidate, 32 refusals, and shared-validator identity pass |

There is no real/private success route in this lane.

## Resource Envelope

```text
CPU threads:              1
workers:                  1
numerical jobs:           1
runtime:                  <= 30 seconds
peak RSS:                 <= 256 MiB
generated input:          <= 1 MiB
generated output:         <= 1 MiB
incremental disk:         <= 2 MiB
network bytes:            0
private or real bytes:    0
```

Temporary generated output must be removed after inspection. No dependency is
added to the base install.

## Evidence Order

1. Commit and push this contract.
2. Require Base Python and Optional Neuro Readers jobs to pass remotely.
3. Implement only the generated validator and qualification surface.
4. Run the canonical case, exact replay, all 32 mutations, focused tests, the
   complete base and optional suites, Ruff, compile checks, strict JSON checks,
   CLI help, and diff hygiene.
5. Commit and push the exact implementation and require both remote jobs green.
6. Only then may a new all-false Tier C packet propose an additive live wrapper
   and one new private-manifest selection.
7. A fresh packet-bound maintainer decision must become remotely green before
   any retained-path operation.

The current or any earlier `continue` is not retroactive authority for step 7.

## Explicit Non-Authorization

This contract authorizes no retained-path check, private-manifest read, output
root, network request, archive local-header or member access, download, payload,
EEG sample, event, target, label, quality field, channel field, derivative,
cache, split, feature, training, inference, prediction, freeze, target delivery,
score, provider, language model, stream, device, hardware, publication,
release, rerun, claim upgrade, `MARC2-FW2`, `MARC2-CIL1`, `MARC2-ORTH1`, or
`NDK-LANG1` operation.

## Claim Boundary

Engineering capability sought: a strict reusable implementation-record
validator whose generated qualification and future live gate share one exact
code path.

Scientific claim not established: generated proof records contain no human
neural data, targets, predictions, or scores and cannot establish a neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
