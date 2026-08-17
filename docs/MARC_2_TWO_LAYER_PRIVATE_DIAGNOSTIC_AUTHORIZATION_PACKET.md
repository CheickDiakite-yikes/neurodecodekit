# MARC2-VR9P Two-Layer Private Diagnostic Authorization Packet

Date: 2026-08-16

Lane: `MARC2-VR9P`

Status: **Request commit `de8e6dcfb60d78b52429d32c6bdd5f9656ab2d58`
is remotely green. All authorization fields remain false; a fresh packet-bound
maintainer decision is still required**

Request:
`registries/marc2_two_layer_private_diagnostic_authorization_request.v0.json`

## Decision Requested

The immutable request passed Base Python job `95277554517`, Optional Neuro
Readers job `95277554619`, and CI `31992178980`. After this additive proof
record is also remotely green and the packet is identified as the sole active
Tier C gate, request one future two-stage sequence:

1. implement and qualify a new additive generated/mock-only fixed-path wrapper;
   and
2. only after that exact implementation is committed, pushed, and both CI jobs
   are green, perform one target-free structural diagnostic that retains only
   the outer VR6 and nested VR2 route codes.

This packet does not record a decision and grants no authority now. The current
and every earlier `continue`, `approve`, or `proceed` message is not retroactive
authority for a packet that did not yet exist. A fresh unambiguous packet-bound
message is required after the request is remotely green and named as the sole
Tier C gate.

## Why This Is The Smallest Useful Next Read

Consumed VR7P verified and strict-parsed the 418,755-byte structural manifest,
then called VR6 once. VR6 reported outer `MARC2VR6-F02`, but VR7P dropped the
nested safe route. Artifact-only VR8A excluded nested F02 and left exactly two
compatible classes:

- `MARC2VR2-F03`: BIDS path, run-companion, or structural-grouping refusal;
- `MARC2VR2-F04`: bundle, participant, session, or taxonomy-arithmetic refusal.

Generated VR8B then proved, through all 1,227 exact parser/producer rows, that a
new relay can preserve outer F02 plus nested F03 or F04 while discarding the
reason and private context. Exact implementation
`d7ce48baca29547ff2385ffe53d247563139439f` passed Base Python job
`95271230358`, Optional Neuro Readers job `95271230485`, and CI `31989817593`.
Proof closeout `1d2ac3a3fb15ebdc01d8aaa23ae8dc74372b85b8` then passed Base
job `95272233005`, Optional job `95272232926`, and CI `31990197181`.

The new request asks only which frozen structural class the same immutable
manifest reaches. It does not attempt a repair, cohort selection, archive open,
or neural experiment.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 implement:

- exact request, decision, implementation, and proof-record validation;
- a fixed-path machine-readiness and no-follow state machine using generated
  source fixtures only;
- generated F03 and F04 cases in canonical and reversed order, replayed twice;
- exactly one VR6 call per generated diagnostic path;
- the exact VR8B rule that exposes only outer and nested allowlisted codes;
- a strict aggregate-output firewall;
- at least 64 direct refusal mutations across proof, path, race, hash, JSON,
  route, leakage, replay, resource, and forbidden-operation boundaries; and
- CLI help, deterministic replay, bounded resources, and zero retained output.

The future module must expose no generic path, URL, output, threshold, retry,
resume, fallback, substitution, or arbitrary execute override. Generated
qualification must not stat, resolve, hash, open, alter, delete, or reuse any
real `.codex_work` path.

## Proposed One Private Diagnostic

Only after the exact future implementation is remotely green may one command:

1. validate its exact green implementation proof;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` certificate only at
   `.codex_work/marc2_machine_readiness/vr9p/readiness.v0.json`;
4. require `.codex_work/marc2_two_layer_private_diagnostic/v0` to be absent;
5. no-follow preflight the registered structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, hash, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR6 adapter once; and
9. write at most one aggregate-safe report.

The immutable source identity, copied only from committed records, is:

```text
path:        .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
mode:        0600
bytes:       418,755
SHA-256:     2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
rows:        1,227
files:       1,025
directories: 202
bundles:     238 total / 195 eligible / 43 valid ineligible
```

Packet preparation performs zero path checks, stats, hashes, opens, reads, or
parses against that source.

## Frozen Route Contract

The real diagnostic has only two accepted observations:

| Observation | Maximum engineering meaning |
|---|---|
| outer `MARC2VR6-F02` + nested `MARC2VR2-F03` | the retained structural manifest reaches the frozen path/run-companion/grouping class |
| outer `MARC2VR6-F02` + nested `MARC2VR2-F04` | the retained structural manifest reaches the frozen bundle/participant/session/taxonomy class |

Nested F02 is forbidden because VR8A excluded the envelope class. VR6 success,
a missing or unknown nested route, another route, source mutation, or leakage
consumes and parks the lane. No success path may retain or promote an in-memory
candidate cohort.

The aggregate report may contain only schema and lane identity, status, route,
the two allowlisted route codes, green-proof identity, resource measurements,
zero access counters, warnings, unavailable fields, and claim boundaries. It
may not contain reasons, exception text, predicates, failed values, source rows,
member names, paths, offsets, CRCs, private hashes, subject IDs, participant
IDs, sessions, runs, companion identities, or candidate selections.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 30 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
network bytes:                           0
archive-member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 1 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- implementation, decision recording, or any operation before separate green
  request and decision barriers;
- a stat, resolve, read, hash, unlink, rename, overwrite, cleanup, or reuse of a
  consumed certificate, marker, output root, executor, or private result;
- a second source open, retry, rerun, resume, repair, fallback, substitution, or
  post-result reinspection;
- an archive local-header or member-payload read;
- EEG, MEG, signal, event, onset, channel, geometry, sentence, key, label,
  target, quality, or participant-level output access;
- a cohort freeze, derivative, cache, split, feature, NeuroToken, training,
  parameter update, model, checkpoint, inference, prediction, freeze, target
  delivery, scoring, threshold selection, or post-result tuning;
- a download, network request, language model, provider, RW3, stream, device,
  or hardware operation;
- FW2 or CIL1 implementation or execution; or
- release, publication, or any scientific, decoding, neural, real-time,
  portable, home-use, assistive, or clinical claim upgrade.

## Failure Semantics

A failure before the marker performs zero private content opens and still
consumes the one registered invocation. A failure after the marker consumes the
one diagnostic. Neither case permits a retry, rerun, resume, repair, fallback,
substitution, or private reinspection.

An observed F03 or F04 would choose the subject of a later prospective repair;
it would not authorize that repair. A separate generated repair, contract, and
Tier C sequence would still be required before any new source read.
FW2 and CIL1 remain ineligible because no real cohort has been frozen.

## Current Verification

- Seventeen committed predecessor artifacts total 328,581 bytes and are bound
  by exact path, size, and SHA-256.
- The request test suite verifies all-false authority, zero operations, exact
  proof identity, route allowlists, path separation, resources, failure
  semantics, and the scientific ceiling.
- No `.codex_work` path, private source, archive, payload, neural value, target,
  model, prediction, or score is accessed while preparing this packet.
- Immutable request commit `de8e6dcfb60d78b52429d32c6bdd5f9656ab2d58`
  passed both required jobs in CI `31992178980`; this additive proof record does
  not change the request scope or authorize an operation.

Engineering capability requested: one proof-gated target-free structural open
can preserve the exact nested F03 or F04 route through VR6 without retaining
reasons, rows, paths, identities, values, or a cohort.

Scientific claim not established: this request performs no private read, and
even a future diagnostic would access no archive or neural payload, target,
prediction, or score, so it establishes no neural effect, decoding accuracy,
language decoding, live decoding, or thought-to-text capability.
