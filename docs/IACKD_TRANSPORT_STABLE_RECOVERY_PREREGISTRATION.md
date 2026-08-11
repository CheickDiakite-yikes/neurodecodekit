# IACKD-T1 Transport-Stable Recovery Preregistration

Date: 2026-08-11

Status: **Frozen prospective contract; generated-fixture implementation only
after remote green; every public dataset request and real execution remains
unauthorized**

Contract:
`registries/iackd_transport_stable_recovery_contract.v0.json`

Research basis:
`docs/IACKD_TRANSPORT_STABLE_RECOVERY_RESEARCH.md`

## Objective

Qualify a strict standard-library response validator that separates HTTP
framing evidence from content identity for the four small IACKD metadata
bodies, while preserving the stronger exact-length policy for large selected
objects and every scientific field in the consumed IACKD-2 contract.

This lane is an engineering recovery prerequisite. It is not a metadata
request, acquisition, model run, rerun, target delivery, score, or scientific
result.

## Immutable Parents

The contract binds:

- the frozen IACKD-2 scientific contract;
- the exact real executor that consumed its one stream invocation;
- the committed `IACKD2-F08` failure result and green CI proof;
- the committed OpenNeuro inventory containing the four metadata body sizes
  and hashes plus the 1,340-object selected inventory; and
- this research record and invariant tests.

The consumed invocation and old retained bundle may not be reopened, renamed,
deleted, copied, inspected, or used as input. A future recovery uses a new
module, new root, and new consumed marker.

## Frozen Metadata Policy

Exactly four future metadata responses are in scope, in this order:

| Body | Registered bytes | Registered SHA-256 |
|---|---:|---|
| dataset description | 1,178 | `275cf1d24f93832ed17fd32d46a589286453042f8d2788b4f3dc1933c6523d93` |
| CHANGES | 164 | `1a80dbb236a969a6006924fa4c19f9a120b00830c38f2a8b5d3a8de5b7252792` |
| listing page 1 | 355,831 | `c4aa840256c6d91e9a24feccb71bc5e9ed8d1514d1568059d63003f79daeca78` |
| listing page 2 | 238,227 | `612503c610851c7e52e5a5d3d5257f71b8b03d59c6eb090323aba199e122e5d8` |

Each response must pass in this order:

1. exact allowlisted requested URL;
2. HTTP 200 and exact final URL;
3. no redirect and identity `Content-Encoding`;
4. one unambiguous framing profile;
5. one `read(registered_size + 1)` call;
6. exact observed byte count;
7. exact registered SHA-256; and
8. one strict semantic parse only after identity passes.

Accepted framing profiles are `fixed_length`, `chunked`, and
`close_delimited`. A metadata `Content-Length` is optional and advisory. When
present, it must be one non-negative decimal integer no greater than the
per-body cap; exact and differing values are recorded separately. Both
`Content-Length` and `Transfer-Encoding`, any malformed length, or any transfer
coding except exact `chunked` refuses. A valid differing length can never
override observed body-size or hash drift.

The public aggregate may report only counts of framing profiles, exact versus
differing declared-length groups, warnings, unavailable fields, input/output
bytes, runtime, RSS, and access counters. It may not publish raw headers,
header values, bodies, URLs, paths, tokens, participant records, or protected
content.

## Frozen Payload Policy

Future large selected-object transport is not loosened. All 1,340 payload
responses still require the registered URL, status, exact `Content-Length`,
exact ETag, identity encoding, exact observed bytes, and one full-stream
SHA-256. Transfer coding, compression, redirect, retry, substitution, partial
promotion, or concurrent groups refuse.

The exact 7,249,113,684-byte selected surface, canonical identity hash, 128
ten-object run groups, 60 geometry objects, one-run-at-a-time cleanup, and 10
GiB free-space preflight remain unchanged. This preregistration does not
authorize any one of those operations.

## Frozen Scientific Policy

Every scientific and target-firewall field is inherited byte-for-byte in
meaning from `IACKD-2-role-aware-dual-reversal-contract-v0`. The recovery may
not change participants, arms, runs, splits, source-role policy, channels,
sampling, windows, filters, motion guard, features, estimator, controls,
seeds, fit count, prediction count, freeze ordering, target delivery, scorer,
router, thresholds, resource caps, or claim ceiling.

The implementation must refuse if a bound parent hash differs or if it cannot
prove that the only semantic delta is the metadata framing policy.

## Fixture Qualification

After this exact registration is committed, pushed, and both CI jobs are
green, Tier B permits one dependency-free generated qualification with zero
network bytes. It must cover:

- exact `fixed_length`, `chunked`, and `close_delimited` acceptance;
- valid differing metadata `Content-Length` accepted only when observed bytes
  and SHA-256 remain exact;
- missing, exact, differing, malformed, negative, comma-joined, and over-cap
  declared lengths;
- ambiguous length plus transfer coding;
- unsupported transfer coding and content encoding;
- status, final-URL, redirect, underflow, overflow, read-error, and hash drift;
- exact one-read, one-hash, one-parse ordering and no parse on identity failure;
- payload mode retaining exact declared length and ETag;
- deterministic replay and aggregate-only inspection; and
- default CLI closure against network construction and real paths.

No fixture may use a downloaded source body. Generated bytes must not encode
participant, event, trajectory, target, label, sentence, or prediction data.

## Resource Caps

```text
generated qualifications:       1
CPU threads / workers / jobs:    1 / 1 / 1
wall time:                       30 seconds
peak RSS:                        268,435,456 bytes
generated output:                1,048,576 bytes
network bytes:                   0
real/public body reads:          0
local IACKD path operations:     0
model/training/inference/score:  0 / 0 / 0 / 0
```

A future real executor and public stream retain the older IACKD-2 caps. They
are outside the current authorization state.

## Ordered Evidence Gates

1. Commit and push this research, preregistration, contract, and invariant
   tests; pass Base Python and Optional Neuro Readers CI.
2. Build and qualify only the generated-fixture transport module.
3. Commit and push that exact implementation; pass both CI jobs.
4. Prepare one all-false Tier C request binding both green milestones.
5. Commit and push the request; pass both CI jobs.
6. Identify its exact packet, commit, CI, scope, and boundary to the
   maintainer.
7. Stop. Only a fresh unambiguous packet-bound decision may unlock a distinct
   real-executor integration, and that decision must itself become remotely
   green before implementation.

The current instruction is not step 7 authorization because the packet does
not yet exist.

## Claim Boundary

Engineering capability added: a strict, testable contract now distinguishes
small-body transport framing from hash-verified content identity without
loosening large-object or scientific gates.

Scientific claim not established: this registration accesses no public body,
EEG, event, trajectory, target, model, prediction, or score and establishes no
neural effect or decoding result.
