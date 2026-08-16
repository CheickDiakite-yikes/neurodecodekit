# MARC2-TA1 Transport Alias Adapter Implementation

Date: 2026-08-16

Lane: `MARC2-TA1`

Status: **Generated implementation and one qualification complete; remotely green**

Contract:
`registries/marc2_transport_alias_adapter_contract.v0.json`

Module:
`src/neurodecodekit/datasets/marc2_transport_alias_adapter.py`

## Green Registration Boundary

Implementation began only after registration commit
`0c0e1c8a08ff7e68d0e4432a64dde8a85fb0274f` passed Base Python job
`95129832134`, Optional Neuro Readers job `95129832169`, and CI
`31932701989`.

No private path, retained output root, archive member, neural payload, target,
model, network, provider, device, hardware, or `MARC2-FW2` operation was opened
by that proof or this implementation.

Exact implementation/result commit
`108b869a6199b6d3aa2d87f8a59b6d8bee0c847b` subsequently passed Base Python
job `95132260089`, Optional Neuro Readers job `95132260076`, and CI
`31933692066` without changing the measured adapter module.

## Implementation

The standard-library adapter keeps the producer and selector schemas separate:

```text
generated source:  directory, metadata, tail
frozen selector:   central_directory, metadata, tail
```

It validates the complete generated source manifest before copying anything.
That validation covers the exact top-level and source-identity fields, all
1,227 entry schemas, 1,025 regular files, 202 directories, 195 source run
bundles, exact published run counts, and lowercase SHA-256 syntax.

Only after source validation does the adapter:

1. deep-copy every mutable container;
2. convert the generated-only proof and provider identity expected by the
   frozen generated selector;
3. map `directory` to `central_directory` exactly once;
4. verify that the source object is unchanged;
5. verify that source and adapted mutable objects do not alias;
6. verify byte-for-byte transport-value and hash-multiset preservation; and
7. call the unchanged, hash-bound selector.

The module exposes only `plan`, `qualify`, and `inspect`. It has no `execute`
command, source-path argument, URL client, private-root import, archive reader,
neural reader, target interface, trainer, predictor, or scorer.

## Adversarial Qualification

All 26 registered mutations refused in their frozen classes:

| Refusal class | Count |
|---|---:|
| source manifest schema | 10 |
| transport alias or digest | 9 |
| copy, value, or replay integrity | 4 |
| selector integration or result | 2 |
| forbidden-operation boundary | 1 |

The direct producer-native call to the selector refused. Canonical and reversed
source-entry orders both passed through the adapter and reproduced the exact
existing generated selector identity:

| Measurement | Result |
|---|---:|
| selected subjects | 16 |
| selected run bundles | 96 |
| selected core members | 384 |
| selected reservation bytes | 8,105,207,776 |
| selection identity SHA-256 | `dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641` |
| generated private-selection SHA-256 | `da772ea045520a24c11b144af27d341115e7b082861b9c28299981fccd4a2bba` |

These are generated integration identities, not participant measurements.

## Measured Closeout

One final generated qualification ran in a fresh one-thread process:

```text
route:                         MARC2TA-G1
generated input bytes:         846,708
aggregate output bytes:        4,931
internal runtime seconds:      0.4533158749982249
internal peak RSS bytes:       39,108,608
external wall seconds:         0.52
CPU threads/workers/jobs:      1 / 1 / 1
raw-data reads:                0
real-cache reads:              0
model runs:                    0
training runs:                 0
end-to-end latency measured:   no
producer causal status:        not applicable, metadata adapter
report mode:                   0600
report SHA-256:                40303300d396415cf6833707330303b8cbf60b1576bbe6c7b9a70825ff0af28a
temporary output retained:     no
```

The local timing wrapper could report wall, user, and system time, but its
macOS `sysctl kern.clockrate` probe was sandbox-denied. The adapter's direct
`resource.getrusage` peak-RSS measurement remained available and passed the
256 MiB cap.

Every private, Git-ignored, consumed-root, archive, signal, event, target,
label, channel, geometry, derivative, model, prediction, score, network,
provider, hardware, retry, FW2, and claim counter was zero.

## Verification

Fifty-two focused contract, behavior, implementation-record, and result tests
pass. The complete dependency-light suite passes 3,307 tests with 204 expected
skips. Optional-neuro A-M and N-Z pass 2,865 tests with 28 skips and 513 tests
with seven skips, respectively, for 3,378 optional-enabled tests with 35 skips.

Ruff, compilation, strict parsing of all 224 registry documents, module CLI
help/plan/qualify/inspect, tracked hashes, and diff hygiene pass. The optional
A-M lane ran outside the filesystem sandbox solely because an existing timing
test requires a local forkserver socket.

## Boundary

Engineering capability added: a generated producer-native manifest can now
cross one explicit value-preserving schema adapter and reach the frozen
selector without weakening source validation.

Scientific claim not established: generated archive metadata contain no neural
payload, target, prediction, or score and establish no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.

The exact implementation and result are remotely green. A live adapter,
private read, or `MARC2-FW2` entry still requires a separately frozen all-false
Tier C packet and a fresh packet-bound decision.
