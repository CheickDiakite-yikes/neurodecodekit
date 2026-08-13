# MARC1-SA1A Source-Aware Live Metadata Authorization Decision

Date: 2026-08-13

Lane: `MARC1-SA1A`

Status: **Authorized only after this decision is tested, committed, pushed,
and remotely green; no wrapper implementation or source access has occurred**

Machine decision:
`registries/marc1_source_aware_live_metadata_authorization_decision.v0.json`

Frozen request commit:
`b0775501e8d7dc5b28b81692dbc7fb02d423be95`

Frozen packet:
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_PACKET.md`

## Actual Maintainer Decision

After Codex identified `MARC1-SA1A` as the sole active Tier C packet, named
request commit `b0775501e8d7dc5b28b81692dbc7fb02d423be95`, green CI
`31621794066`, Base Python job `94198174069`, Optional Neuro Readers job
`94198173901`, the one-response 2 MiB metadata scope, the zero-payload
boundary, and the need for fresh packet-bound words, the maintainer said:

> let’s do those 5 systemically

This record preserves those exact 31 UTF-8 bytes, including the maintainer's
wording. It does not claim that the maintainer typed the packet's long scope.
The instruction incorporates only the immutable, remotely green
`MARC1-SA1A` packet by reference.

The five-step research objective remains metadata integrity, selective
acquisition, cue-resistant positive control, frozen scoring, and later
replication plus language decoding.

Only the first packeted sequence is authorized here. Future archive
acquisition, neural access, target delivery, scoring, replication, and
language work still require their own prospective contracts and Tier C
decisions.

## Why The Short Form Is Valid

All fail-closed conditions were satisfied before this decision:

1. `MARC1-SA1A` was the sole active Tier C packet.
2. Its packet and all-false request were committed and pushed at `b077550`.
3. Base Python job `94198174069` and Optional Neuro Readers job `94198173901`
   were green in CI `31621794066`.
4. Codex named the commit, CI proof, exact metadata-only scope, zero-payload
   boundary, and fresh-decision requirement.
5. The maintainer then unambiguously directed execution of the identified
   five-step sequence.
6. This separate record quotes the actual message and binds the immutable
   request SHA-256 without fabricating an authorization recital.
7. No later packet, participant archive, neural signal, target, model, score,
   release, or claim authority is inferred.

The decision is ineffective until its own commit passes both remote CI jobs.

## Bound Evidence

```text
authorization parent: b0775501e8d7dc5b28b81692dbc7fb02d423be95
request push CI:       31621794066
Base Python job:       94198174069
Optional Neuro job:   94198173901
request SHA-256:       f5421681fe5ceb6a4b154de692bff81619c87338c832e4e04640bfcad9ca4659
packet SHA-256:        94a4c294db0177d0eb6b7320eb0f4874557e595dbfb26fe7b9a1022996b47162
attestor SHA-256:      36a06958009f3ac42af6eb69d464a61db6f004bc51fa4f3b73420538cf29a482
user-message SHA-256:  0c3c79426ed20b5720db1b09ca50280dff0033e75024297a394a92a8c1c66185
```

The packet, request, tests, generated attestor, and consumed generated result
remain immutable snapshots. Their pending fields are not rewritten. This
additive record supplies only packet-bound permission.

## Ordered Authorization

### Gate 1: this decision becomes remotely green

This exact decision must be tested, committed, pushed, and pass Base Python
and Optional Neuro Readers CI. Until then, implementation and access remain
closed.

### Gate 2: generated and mocked wrapper qualification

After Gate 1, Codex may implement the additive standard-library module at
`src/neurodecodekit/datasets/marc1_source_aware_live_metadata.py`. It may
import only the green source-aware attestor and must not import, call, modify,
probe, or expose the consumed live executor or root.

Qualification may use generated inventories, mocked transport, injected
failures, and fresh temporary nonregistered paths. It must prove exact proof
hashes, capability-first output, one bounded response, duplicate-key and
nonfinite JSON rejection, the target firewall, all source-aware routes,
private/public separation, deterministic replay, consumed-marker behavior,
and resource caps. The exact wrapper commit must pass both remote CI jobs
before Gate 3.

### Gate 3: one source-aware live metadata response

After Gate 2 is remotely green, require one numerical thread, at least
10,737,418,240 bytes free, and normalized one-minute load no greater than
`1.0` per logical CPU. Any failed or unavailable machine measure refuses
before the consumed marker.

One no-retry invocation may then:

1. acquire a held no-follow output-parent capability before repository or
   network work;
2. validate the exact decision, request, result, contract, implementation,
   and wrapper hashes;
3. create only `.codex_work/marc1_source_aware_inventory/live_metadata_v0`
   and one mode-`0600` consumed marker;
4. make exactly one unauthenticated HTTPS `GET` to
   `https://api.figshare.com/v2/articles/29666735/versions/3/files?page=1&page_size=1000`;
5. read at most 2,097,152 bytes plus one overflow byte under the frozen
   uncoded, terminal-200, no-redirect framing rules;
6. apply the exact green source-aware attestor once;
7. retain one mode-`0600` private manifest and one aggregate report; and
8. stop before every archive or payload operation.

Any result or failure consumes the lane. There is no second request, retry,
rerun, resume, fallback, expectation change, or post-response amendment.

## Source-Aware Routes

| Attestor route | Wrapper route | Cohort selection | Payload |
|---|---|---:|---:|
| `MARC1SA-R1` | `MARC1SAL-R1` | available | unavailable |
| `MARC1SA-R2` | `MARC1SAL-R1` | available | unavailable |
| `MARC1SA-R3` | `MARC1SAL-R2` | blocked | unavailable |
| `MARC1SA-R4` | `MARC1SAL-R2` | blocked | unavailable |

Structural, proof, transport, target, privacy, output, or resource failures
use `MARC1SAL-F00` through `MARC1SAL-F04` and stop.

## Exact Limits

```text
metadata requests / redirects:          1 / 0
accepted bodies / bytes:                1 / <= 2,097,152
historical rows / participant archives: 55 / 45
frozen selected subjects:               12 only on complete historical match
payload requests / bytes:               0 / 0
live execution wall / RSS:              30 sec / 268,435,456 bytes
aggregate / combined output:            <= 1,048,576 / <= 2,097,152 bytes
incremental disk / minimum free:         <= 4,194,304 / >= 10,737,418,240 bytes
threads / workers / jobs:               1 / 1 / 1
retries / reruns:                        0 / 0
signals / targets / models / scores:     0 / 0 / 0 / 0
```

## Decision-Only Measurements

```text
GitHub CI verification calls:                   1
DNS queries / network requests / body bytes:    0 / 0 / 0
private path operations / output writes:        0 / 0
participant archive / payload requests:         0 / 0
signal / event / target reads:                   0 / 0 / 0
models / predictions / freezes / scores:         0 / 0 / 0 / 0
dependency installs / cleanup operations:        0 / 0
provider-model / hardware / release operations:  0 / 0 / 0
scientific claim upgrades:                       0
end-to-end latency measured:                     false
```

## Claim Boundary

Engineering capability authorized for testing: one exact additive,
standard-library, source-aware wrapper may be qualified and, after its own
green proof, turn one bounded public metadata response into a
privacy-preserving cohort identity or aggregate drift diagnosis.

Scientific claim not established: this decision is not neural data or a
result. It establishes no neural effect, decoding accuracy, brain-specific
origin, language decoding, or thought-to-text capability.

Research objective preserved: this is the cohort-integrity checkpoint on the
same path toward a cue-resistant neural effect, properly frozen scoring,
replication, and held-out language decoding. It is not a pivot.
