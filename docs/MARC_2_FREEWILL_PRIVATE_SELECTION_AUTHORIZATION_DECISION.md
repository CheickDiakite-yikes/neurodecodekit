# MARC2-FW1A Private Selection Authorization Decision

Date: 2026-08-13

Lane: `MARC2-FW1A`

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; no wrapper implementation, retained-path operation, or
private selection has occurred**

Machine decision:
`registries/marc2_freewill_private_selection_authorization_decision.v0.json`

Frozen request commit:
`d0a6eaa391b12f04da35bf277f6409f2750d40df`

Frozen packet:
`docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_PACKET.md`

## Actual Maintainer Decision

After Codex identified `MARC2-FW1A` as the sole active Tier C packet, named
request commit `d0a6eaa391b12f04da35bf277f6409f2750d40df`, green CI
`31679428199`, Base Python job `94381244828`, Optional Neuro Readers job
`94381244902`, the target-free private-selection boundary, and the need for
fresh packet-bound words, the maintainer said:

> continue

This record preserves those exact 8 UTF-8 bytes. It does not claim that the
maintainer typed the packet's long scope. The instruction incorporates only
the immutable, remotely green `MARC2-FW1A` packet by reference.

The decision authorizes the packet's ordered two-stage sequence only. It does
not authorize `MARC2-FW2`, archive local headers or members, EEG payloads,
signals, events, targets, models, scoring, providers, hardware, release, or a
scientific claim upgrade.

## Why The Short Form Is Valid

All fail-closed conditions were satisfied before this decision:

1. `MARC2-FW1A` was the sole active Tier C packet.
2. Its packet and all-false request were committed and pushed at `d0a6eaa`.
3. Base Python job `94381244828` and Optional Neuro Readers job
   `94381244902` were green in CI `31679428199`.
4. Codex named the commit, CI proof, exact target-free scope, zero-payload
   boundary, and fresh-decision requirement.
5. The maintainer then gave the unambiguous instruction `continue`.
6. This separate record quotes the actual message and binds the immutable
   request SHA-256 without fabricating an authorization recital.
7. No later acquisition, neural, target, model, score, provider, release, or
   claim authority is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Bound Evidence

```text
authorization parent: d0a6eaa391b12f04da35bf277f6409f2750d40df
request push CI:       31679428199
Base Python job:       94381244828
Optional Neuro job:   94381244902
request SHA-256:       2795818b0517bdd66a69e4039c98d3359c0115ef78d5f0be7ff8869511e5987d
packet SHA-256:        94437f2dad9d3d9b9b1c84ca68c9a12848e9dba7e1fcd3f0a902c5e657870f98
selector SHA-256:      86fa30fbd1caed735f0fb2e627144482a2bb8e033567bb3794e3f05508005c97
user-message SHA-256:  e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad
```

The packet, request, selector, generated result, and their tests remain
immutable snapshots. Their false authorization fields are not rewritten. This
additive record supplies only packet-bound permission.

## Ordered Authorization

### Gate 1: this decision becomes remotely green

This exact decision must be tested, committed, pushed, and pass Base Python
and Optional Neuro Readers CI. Until then, implementation and private access
remain closed.

### Gate 2: generated and mocked wrapper qualification

After Gate 1, Codex may implement one additive standard-library wrapper around
the frozen selector. It may use only generated manifest bodies, mocked
filesystem facts, temporary directories, and injected readers during
qualification. It must not import, call, modify, or expose a consumed MARC1
executor or root.

The wrapper must expose only `plan`, generated `qualify`, aggregate `inspect`,
and proof-disabled `execute`. It must preserve the frozen rank, session split,
bundle rule, reservation formula, 12-person floor, maximal contiguous prefix,
and 8-GiB cap. Qualification must pass all 40 inherited selector mutations and
all 18 wrapper-specific proof, path, no-follow, privacy, output, resource, and
one-shot refusals.

The exact wrapper commit must pass both remote CI jobs before Gate 3.

### Gate 3: one private-manifest selection

After Gate 2 is remotely green, one no-retry invocation may operate on only:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

It must verify the exact 418,755-byte, mode-`0600`, SHA-256-pinned,
1,227-entry source using no-follow checks, one content open, one sequential
read, one SHA-256 pass, one `fstat` reconciliation, and one strict JSON parse.
It may create only:

```text
.codex_work/marc2_freewill_prefix/live_selection_v0/
  consumed marker
  private target-free selection
  aggregate report
```

The consumed marker must be written before private content access. Every route
consumes the invocation. There is no retry, rerun, resume, source override,
output override, repair, fallback, or post-result amendment.

## Exact Limits

```text
threads / workers / numerical jobs:      1 / 1 / 1
runtime / peak RSS:                      30 sec / 268,435,456 bytes
private input opens / bytes:             1 / 418,755 exact
network requests / bytes:                0 / 0
archive local-header/member bytes:       0
combined output / incremental disk:      <= 2 MiB / <= 4 MiB
minimum free disk:                       >= 15 GiB
selected future reservation:             <= 8 GiB accounting only
signal / event / target reads:           0 / 0 / 0
models / predictions / scores:           0 / 0 / 0
retries / reruns:                        0 / 0
```

The 8-GiB reservation is a future payload ceiling, not payload authority.

## Decision-Only Measurements

```text
GitHub CI verification calls:                   1
private path operations / private bytes:        0 / 0
network requests / payload bytes:               0 / 0
archive local-header or member reads:           0
real participant/member selections:             0 / 0
signal / event / target reads:                   0 / 0 / 0
models / predictions / freezes / scores:         0 / 0 / 0 / 0
dependency installs / cleanup operations:        0 / 0
provider-model / hardware / release operations:  0 / 0 / 0
scientific claim upgrades:                       0
end-to-end latency measured:                     false
```

## Claim Boundary

Engineering capability authorized for testing: one exact additive,
standard-library wrapper may be qualified and, after its own green proof, turn
one exact private ZIP-directory manifest into a deterministic,
storage-bounded, target-free selection with separate private and aggregate
outputs.

Scientific claim not established: this decision is not neural data or a
result. It establishes no neural effect, decoding accuracy, brain-specific
origin, language decoding, or thought-to-text capability.

Research objective preserved: this is the final cohort-selection checkpoint
before a separately frozen `MARC2-FW2` payload-acquisition packet on the same
path toward conditional neural-information testing. It is not a pivot.
