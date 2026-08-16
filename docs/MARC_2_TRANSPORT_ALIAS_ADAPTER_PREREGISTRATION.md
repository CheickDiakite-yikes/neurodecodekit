# MARC2-TA1 Transport Alias Adapter Preregistration

Date: 2026-08-16

Lane: `MARC2-TA1`

Status: **Frozen generated-only contract; implementation pending remote green**

Machine contract:
`registries/marc2_transport_alias_adapter_contract.v0.json`

## Why This Exists

Artifact-only `MARC2-SL1` established one exact integration mismatch:

```text
producer-native:  directory, metadata, tail
selector-internal: central_directory, metadata, tail
```

The adapter should not make source validation looser. It should make the schema
boundary explicit.

## Frozen Design

The future generated-only implementation must:

1. Build a 1,227-row producer-native generated manifest with no human content.
2. Validate the untouched source object against exact producer-native keys.
3. Deep-copy the source object without aliasing or mutation.
4. Rename only `directory` to `central_directory` in the copy.
5. Preserve the three SHA-256 values byte for byte.
6. Convert only the generated proof/source identity needed by the existing
   frozen generated selector.
7. Run the unchanged selector after adapter validation.
8. Reproduce the existing 16-person, 96-bundle, 384-member,
   8,105,207,776-byte generated selection.

Direct delivery of the producer-native object to the selector must refuse. A
missing key, extra key, preexisting consumer alias, both aliases, malformed
digest, value mutation, object alias, entry drift, selector-result drift, or
nondeterministic replay must also refuse.

## Qualification Matrix

The implementation must exercise 26 named mutations and two success paths:
canonical source order and reversed source-entry order. Entry order may differ,
but canonical selection identity and adapted transport values must replay
exactly.

The qualification is limited to:

```text
CPU threads / workers / jobs:  1 / 1 / 1
runtime:                        30 seconds
peak RSS:                       256 MiB
generated output:               2 MiB
incremental disk:               2 MiB
network bytes:                  0
private or Git-ignored bytes:   0
```

The base install remains dependency-free. The future module may expose only
`plan`, `qualify`, and `inspect`; it may not expose `execute`, a generic source
path or URL, a private root, a consumed FW1C import, an archive reader, neural
data, targets, models, scores, or a network client.

## Gate Order

1. Commit and push this exact registration.
2. Require Base Python and Optional Neuro Readers to pass remotely.
3. Only then implement and run one generated qualification.
4. Commit and push the exact implementation and result, then require both jobs
   green.
5. Stop. A live adapter or another private read remains a new Tier C event.

The current registration does not authorize a live adapter, private manifest
access, output-root access, retry, `MARC2-FW2`, payload, EEG, target, model,
provider, device, hardware, release, or claim operation.

## Claim Boundary

Engineering claim if successful: a generated producer-native manifest can
cross one explicit value-preserving schema adapter and reach the frozen
selector without weakening source validation.

Scientific claim not established: generated archive metadata contain no neural
payload, target, prediction, or score and establish no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
