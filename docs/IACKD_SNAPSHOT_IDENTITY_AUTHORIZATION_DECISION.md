# IACKD-M1A Public Snapshot Audit Authorization Decision

Date: 2026-08-11

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; no wrapper implementation or OpenNeuro request has
occurred**

Machine decision:
`registries/iackd_snapshot_identity_authorization_decision.v0.json`

Frozen request commit:
`ce847383ab1e327523cbc172bb6d3be417b46a11`

Frozen packet:
`docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_PACKET.md`

## Actual Maintainer Decision

After Codex identified IACKD-M1A as the sole active Tier C packet, named
request commit `ce847383ab1e327523cbc172bb6d3be417b46a11`, green CI
`31484273623`, both required green jobs, the one-wrapper/one-response scope,
the 2 MiB response cap, zero-payload boundary, and need for a fresh decision,
the maintainer said:

> keep going, move the needle, continue, you approved to go on

This record preserves those exact 60 UTF-8 bytes. It does not claim that the
maintainer typed the packet's long scope. The short instruction incorporates
the immutable, remotely green packet by reference without widening it.

Every endpoint, query, byte, response, resource, privacy, no-payload,
no-retry, no-rerun, and claim boundary remains unchanged.

## Why The Short Form Is Valid

All fail-closed conditions were satisfied before the instruction:

1. IACKD-M1A was the sole active Tier C packet.
2. The packet and all-false request were committed and pushed at `ce84738`.
3. Base Python job `93755977352` and Optional Neuro Readers job `93755977235`
   were green in CI `31484273623`.
4. Codex named the packet, commit, CI proof, exact metadata-only scope, and
   decision boundary.
5. The maintainer then unambiguously included `continue` in a direct instruction
   to keep this work moving.
6. This separate record quotes the actual message and binds every immutable
   scope artifact.
7. No EEG payload, release, hardware, destructive action, model, score, or
   scientific upgrade is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Bound Evidence

```text
authorization parent:  ce847383ab1e327523cbc172bb6d3be417b46a11
request push CI:        31484273623
Base Python job:        93755977352
Optional Neuro job:    93755977235
contract SHA-256:      fa7bed69bb70022b3e61c6839b01a2fa7f3e4f77a40629dc62ab9b4873681e2a
implementation SHA:    05590a904ad8ee26d397726e1133877b0ec46218e8fc7ee37e7a26526c4b08a2
request SHA-256:       ae725915fa264bbc2db6f68fc0ae01df26bdcedae45f920b571ab2beb5dc4d83
packet SHA-256:        de4f1d5c6402b6e000ab5f04a1b094895d82fe9ed41fb9d3128629eea7af3b07
user-message SHA-256:  c97c7d04ef3fb6e70265325d4805026948a1474554de1725374ae47c64a19371
```

The research, registration, canonicalizer, packet, request, and tests remain
immutable snapshots. Their pending fields are not rewritten after approval.
This additive record supplies the packet-bound permission.

## Ordered Authorization

### Gate 1: this decision must become remotely green

This exact decision must be tested, committed, pushed, and pass Base Python
and Optional Neuro Readers CI. Until then, implementation and access remain
closed.

### Gate 2: generated and mocked wrapper qualification

After Gate 1, Codex may implement the one additive standard-library wrapper
named by the packet. It may use only generated response bodies and mocked
transport. It must import the green canonicalizer, expose no usable real
endpoint until proof validation, refuse consumed roots and local IACKD paths,
implement the pre-consumption machine gate, and preserve the exact request and
output contracts.

The existing environment may be reused. Dependency installation, resolution,
substitution, tooling network, public OpenNeuro access, and local IACKD access
remain closed during implementation. The exact wrapper commit must pass both
remote CI jobs before Gate 3.

### Gate 3: one public metadata response

After Gate 2 is remotely green, first require all five numerical thread values
to equal one, at least 2,147,483,648 bytes free, and normalized one-minute load
no greater than `1.0` per logical CPU. Any unavailable or failed measure
refuses before the new private consumed marker.

One no-retry invocation may then:

1. create the new isolated Git-ignored root and consumed marker;
2. send exactly one 355-byte POST to
   `https://openneuro.org/crn/graphql` with the frozen query;
3. accept only HTTP 200, the exact final URL, zero redirects, identity content
   encoding, and one response of at most 2,097,152 bytes;
4. record the raw response SHA-256 as provenance, not acceptance identity;
5. canonicalize the same in-memory body once against the frozen snapshot,
   tree, selected-inventory, and critical-metadata gates;
6. emit one private selected manifest and one aggregate public report under a
   combined 1 MiB cap; and
7. discard the raw body and stop.

Any failure after the marker consumes IACKD-M1A. There is no retry, rerun,
resume, restart, second request, alternate endpoint, query amendment, fallback,
or follow-on payload step.

## Exact Limits

```text
provider / dataset / snapshot:       OpenNeuro / ds006840 / 1.0.0
query / request bytes:               316 / 355
GraphQL requests / responses:        1 / 1
accepted response bytes:             <= 2,097,152
overflow read limit:                 2,097,153
S3 payload requests / bytes:         0 / 0
tree / selected rows:                1,679 / 1,340
selected declared payload bytes:     7,249,113,684 metadata only
public execution wall / RSS:         30 sec / 268,435,456 bytes
combined private/public output:      <= 1,048,576 bytes
incremental disk:                    <= 4,194,304 bytes
minimum free disk:                   2,147,483,648 bytes
maximum load per logical CPU:        1.0
threads / workers / jobs:            1 / 1 / 1
retries / reruns / substitutions:    0 / 0 / 0
models / predictions / scores:       0 / 0 / 0
```

The selected payload-byte total is metadata describing the future inventory;
this decision authorizes no transfer of those payload bytes.

## Decision-Only Measurements

```text
GitHub CI verification calls:                    1
OpenNeuro GraphQL / S3 requests:                 0 / 0
OpenNeuro response / payload bytes:              0 / 0
local IACKD / consumed-root operations:          0 / 0
EEG / EOG / event / trajectory / target reads:   0 / 0 / 0 / 0 / 0
wrapper implementations / generated artifacts:  0 / 0
models / predictions / freezes / scores:         0 / 0 / 0 / 0
dependency installs / cleanup operations:        0 / 0
provider / hardware / release operations:        0 / 0 / 0
scientific claim upgrades:                       0
end-to-end latency measured:                     false
```

## Claim Boundary

Engineering capability authorized for testing: one exact standard-library,
machine-gated wrapper may be qualified and, after its own green proof, test the
current public snapshot identity once.

Scientific claim not established: this decision is not EEG data or a result.
Even a future metadata pass would establish no neural effect, decoding
accuracy, brain-specific origin, generalization, language or thought decoding,
real-time operation, portable hardware, home use, assistive benefit, or
clinical utility.
