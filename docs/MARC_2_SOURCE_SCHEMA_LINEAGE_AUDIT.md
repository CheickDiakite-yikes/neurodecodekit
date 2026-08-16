# MARC2-SL1 Source-Schema Lineage Audit

Date: 2026-08-16

Lane: `MARC2-SL1`

Route: `MARC2SL-R2`

Status: **Exact committed transport-key alias mismatch diagnosed; artifact-only
result with no private reinspection or live authority**

Contract:
`registries/marc2_source_schema_lineage_contract.v0.json`

Result:
`registries/marc2_source_schema_lineage_result.v0.json`

## Short Answer

`MARC2-FW1C` failed because our generated interface and our real producer used
two names for the same transport component.

```text
exact MARC-1 producer:       directory, metadata, tail
generated selector fixture: central_directory, metadata, tail
selector validator:         central_directory, metadata, tail
FW1C live validator:        central_directory, metadata, tail
```

The producer-only key is `directory`. The consumer-only key is
`central_directory`. The other two keys match.

This exact one-key vocabulary mismatch is sufficient to explain why the
418,755-byte manifest passed size, SHA-256, and strict JSON, then stopped at
`MARC2FWC-F02` with `live source identity differs` before any participant or
member was selected.

## Why Generated Tests Missed It

The generated manifest builder and both consumer validators agreed with each
other on `central_directory`. Their tests therefore proved internal
consistency, but they never checked the generated transport vocabulary against
the exact committed producer vocabulary.

The MARC-1 producer assigns the live central-directory response the internal
kind `directory`, records that name in `response_body_sha256`, and copies the
map unchanged into the private manifest's `transport_body_sha256` field. Its
public aggregate result independently records the same three keys. The exact
producer module hash still matches its green implementation registry.

This is a source-contract integration defect, not evidence that the retained
manifest, archive, or EEG is malformed.

## Audit Method

The standard-library auditor read only nine fixed, hash-bound repository
artifacts plus its contract:

- three Python modules parsed with `ast`;
- six implementation, contract, and aggregate-result registries parsed with a
  duplicate-key-rejecting JSON loader; and
- the audit contract itself.

It verified the producer's exact module lineage and manifest forwarding, the
public live transport keys, the generated fixture keys, both consumer
validator key sets, the shared 418,755-byte source binding, and the consumed
failure route. It accepted no source path argument and had no private-root,
network, archive, neural, model, or score interface.

## Measured Audit

```text
fixed committed artifacts:          10 including the contract
input bytes:                         310,015
Python AST parses:                   3
strict JSON parses:                  7
runtime:                             0.02764545800164342 seconds
peak RSS:                            35,717,120 bytes
CPU threads / workers / jobs:        1 / 1 / 1
aggregate output bytes:              5,454
raw-data reads:                      0
real-cache reads:                    0
model runs / training runs:          0 / 0
end-to-end latency measured:         no
producer causal:                     not applicable, artifact only
```

The aggregate report was inspected in memory and not retained as generated
debris. The machine-readable committed result records the diagnosis and exact
counters.

## Verification

```text
focused auditor/result tests:       28
dependency-light tests:             3,254 passed / 204 skipped
optional-neuro A-M tests:            2,812 passed / 28 skipped
optional-neuro N-Z tests:            513 passed / 7 skipped
optional-neuro combined:             3,325 passed / 35 skipped
registry JSON files validated:       221
Ruff:                                passed
compileall:                          passed
CLI help / plan / audit:             passed
git diff --check:                    passed
```

## Prospective Repair

A future, separately named recovery must preserve two explicit schemas:

1. Validate an unmodified source manifest against producer-native keys
   `directory`, `metadata`, and `tail`.
2. Only after that validation, create a new selector input and map
   `directory` to `central_directory` once.
3. Preserve all three SHA-256 values byte for byte.
4. Refuse a missing key, duplicate key, preexisting second alias, extra key, or
   any mutation during adaptation.
5. Qualify a producer-to-adapter-to-selector fixture path, not only a fixture
   emitted directly in the selector's internal schema.

The consumed FW1C executor must not be patched, retried, resumed, or reused.
The adapter above is a frozen design recommendation, not an implementation and
not authorization for another private read. A future live attempt requires a
new generated contract, exact implementation, remotely green proof, all-false
Tier C request, and packet-bound decision.

## Access Boundary

The audit performed zero operations on:

- the private manifest or any Git-ignored path;
- either consumed marker or output root;
- archive local headers or member payloads;
- EEG signals, channels, geometry, events, targets, labels, or quality;
- derivatives, features, splits, NeuroTokens, models, or scores;
- network, providers, language models, streams, devices, or hardware; and
- `MARC2-FW2`, release, publication, or scientific claim upgrades.

No private field value was observed. The diagnosis comes from exact committed
producer code, public aggregate keys, consumer code, and hash-bound lineage.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can now statically reconcile an
exact producer schema with generated fixtures and live validators, and it
identified one deterministic transport-key alias mismatch without private
reinspection.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this audit establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
