# MARC2-LA1 Live-Schema Adapter Preregistration

Date: 2026-08-16

Lane: `MARC2-LA1`

Status: **Frozen generated/mock contract; implementation pending remote green**

Machine contract:
`registries/marc2_live_schema_adapter_contract.v0.json`

## Why This Lane Exists

`MARC2-FW1C` consumed its only private read after strict source validation
expected `central_directory`. Artifact-only `MARC2-SL1` established that the
green producer actually emits `directory`, and generated `MARC2-TA1` proved
that one value-preserving alias adapter can reach the frozen selector.

The missing proof is narrower than another private read: the exact live-shaped
source envelope must cross the already-green generated adapter without
changing entries or transport digests. This lane qualifies that composition on
generated data only.

## Frozen Composition

The future standard-library implementation must:

1. Build a generated 1,227-row manifest with the exact committed live source
   envelope and source-native transport keys `directory`, `metadata`, and
   `tail`.
2. Validate the complete live envelope before copying or bridging anything.
3. Deep-copy the source and change only the four identity values required by
   the green generated adapter: proof posture, provider, file ID, and registered
   MD5.
4. Preserve every entry, declared byte count, record/version identity, boolean
   safety flag, transport key, and transport digest through that bridge.
5. Call the exact remotely green public `adapt_generated_source` function once.
6. Preserve the source object, prevent mutable aliasing, and map only
   `directory` to `central_directory` inside the green adapter.
7. Call the unchanged frozen selector and replay the existing generated
   16-subject, 96-bundle, 384-member, 8,105,207,776-byte result in canonical
   and reversed entry orders.

Direct delivery of the live-shaped source to the selector must refuse. The
implementation must also refuse all 30 registered mutations covering live
schema/identity, transport vocabulary and digests, entry drift, bridge
integrity, direct-selector bypass, and forbidden operations.

The four-value identity bridge is not evidence conversion. It exists only to
exercise the already-green generated adapter with a source object that was
first validated against the exact committed live envelope.

## Surface And Resources

The module may expose only `plan`, `qualify`, and `inspect`. It may not expose
`execute`, a file or URL input, a private root, an output-root identity, a
network client, archive access, neural data, targets, models, predictions,
scores, or `MARC2-FW2`.

```text
CPU threads / workers / jobs:  1 / 1 / 1
runtime:                        30 seconds
peak RSS:                       256 MiB
generated output:               2 MiB
incremental disk:               2 MiB
network bytes:                  0
private or Git-ignored bytes:   0
```

The base dependency delta is zero.

## Gate Order

1. Commit and push this exact registration.
2. Require Base Python and Optional Neuro Readers to pass remotely.
3. Only then implement and run one generated/mock qualification.
4. Commit and push that exact implementation and result; require both jobs
   green.
5. Only after that proof may an all-false Tier C packet be prepared for a new
   additive executor and one future private structural read.
6. Stop for fresh packet-bound maintainer authority.

This registration authorizes no private path operation, consumed-root access,
archive member read, payload, EEG, target, model, score, network, provider,
hardware, release, retry, rerun, or scientific claim upgrade.

## Claim Boundary

Engineering claim if successful: an exact live-shaped producer envelope can
cross a generated identity bridge and the remotely green one-key adapter to
reach the frozen selector without source mutation or digest drift.

Scientific claim not established: generated structural metadata contain no
neural payload, target, prediction, or score and establish no neural effect,
decoding accuracy, language decoding, or thought-to-text capability.
