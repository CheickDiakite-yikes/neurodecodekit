# MARC2-LA1 Live-Schema Adapter Implementation

Date: 2026-08-16

Lane: `MARC2-LA1`

Status: **Generated/mock implementation and one qualification complete;
exact implementation remotely green**

Contract:
`registries/marc2_live_schema_adapter_contract.v0.json`

Module:
`src/neurodecodekit/datasets/marc2_live_schema_adapter.py`

## Green Registration Boundary

Implementation began only after registration commit
`62e465e0600622444b0868d5dcf19678504d20c4` passed Base Python job
`95134785476`, Optional Neuro Readers job `95134785489`, and CI
`31934737967`.

That proof opened generated/mock implementation only. It did not authorize a
private path, consumed output root, archive member, neural payload, target,
model, prediction, score, network operation, or `MARC2-FW2`.

## Composition

The standard-library module constructs a 1,227-row generated fixture with the
exact committed live source envelope:

```text
proof posture: live_archive_private_central_directory_metadata_only
provider:      Figshare
record/version/file: 28632599 / 1 / 57518986
transport:     directory, metadata, tail
```

It validates the full envelope, every entry schema, file/directory count, 195
run bundles, public run counts, and lowercase transport digests before any
copy. It then deep-copies the object and changes only:

1. proof posture;
2. provider;
3. file ID; and
4. registered MD5.

Those four values become the exact generated identity required by the green
TA1 adapter. All entries, record/version identity, declared bytes, safety
flags, transport keys, and transport digests remain unchanged. The source and
bridged objects cannot share mutable containers.

Only then does the module call TA1's exact public `adapt_generated_source`
function once per success path. TA1 deep-copies again, maps only `directory`
to `central_directory`, preserves every digest, and validates the selector
schema. The unchanged selector reproduces its existing generated result.

There is no import of the consumed FW1C executor. The CLI exposes only `plan`,
`qualify`, and `inspect`; it has no `execute`, path-input, URL, private-root,
archive-reader, neural, target, model, prediction, score, or network surface.

## Adversarial Qualification

All 30 registered mutations refused in their frozen classes:

| Refusal class | Count |
|---|---:|
| live envelope, identity, or entry schema | 17 |
| source transport alias or digest | 9 |
| identity bridge copy or value integrity | 2 |
| direct selector bypass | 1 |
| forbidden operation boundary | 1 |

Canonical and reversed source-entry orders both passed. Each success path
called the green adapter exactly once and reproduced:

| Measurement | Result |
|---|---:|
| selected generated subjects | 16 |
| selected run bundles | 96 |
| selected core members | 384 |
| selected reservation bytes | 8,105,207,776 |
| selection identity SHA-256 | `dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641` |

These are generated structural identities, not participant measurements.

## Measured Closeout

One final qualification ran in a fresh one-thread process:

```text
route:                         MARC2LA-G1
generated input bytes:         846,696
aggregate output bytes:        5,366
internal runtime seconds:      0.4889211250047083
internal peak RSS bytes:       38,387,712
external wall seconds:         0.57
CPU threads/workers/jobs:      1 / 1 / 1
raw-data reads:                0
real-cache reads:              0
model runs:                    0
training runs:                 0
producer causal status:        not applicable, metadata adapter
end-to-end latency measured:   no
report mode:                   0600
report SHA-256:                8353c641634cc628663f40932140805bbb2f051fd83ba917695e9cf20a457df7
temporary output retained:     no
```

Every private, Git-ignored, consumed-root, archive, signal, event, target,
label, channel, geometry, derivative, model, prediction, score, network,
provider, hardware, retry, FW2, and claim counter is zero.

## Verification

Fifty-three contract, behavior, implementation-record, and result-record tests
pass. The complete dependency-free suite passes 3,360 tests with 204 expected
skips. Fresh optional-neuro A-M and N-Z processes pass 2,918 tests with 28
skips and 513 tests with seven skips, respectively, for 3,431 optional-enabled
tests with 35 skips.

Ruff, compilation, strict parsing of the new registries, standard parsing of
all 227 registry documents, CLI help/plan/qualify/inspect, tracked hashes, and
diff hygiene pass locally. Exact implementation commit
`3e3f8b86cfb8ac6f23730fb2fcc9fc5da549aac7` passed Base Python job
`95137289730`, Optional Neuro Readers job `95137289704`, and CI
`31935754822`.

## Boundary

Engineering capability added: an exact live-shaped source envelope can cross
a strictly validated four-value generated identity bridge and the remotely
green one-key adapter to reach the frozen selector without source mutation or
digest drift.

Scientific claim not established: generated structural metadata contain no
neural payload, target, prediction, or score and establish no neural effect,
decoding accuracy, language decoding, or thought-to-text capability.

The generated qualification is consumed. A private read, live executor, or
`MARC2-FW2` entry remains closed. The next eligible work is one all-false Tier C
request for a separately implemented additive executor and one exact private
structural read after this proof-record closeout is remotely green; that
request itself grants no live access.
