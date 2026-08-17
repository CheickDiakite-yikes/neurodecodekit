# MARC2-VR11P F03 Private Discriminator Authorization Packet

Date: 2026-08-17

Lane: `MARC2-VR11P`

Status: **Request commit `6e72c8f797201359777454a750b1dea9704665c0`
is remotely green. All authorization fields remain false; this proof closeout
must also become remotely green before a fresh packet-bound decision**

Request:
`registries/marc2_f03_private_discriminator_authorization_request.v0.json`

## Decision Requested

Request commit `6e72c8f797201359777454a750b1dea9704665c0` passed Base
Python job `95326004060`, Optional Neuro Readers job `95326004145`, and CI
`32009557248`. After this non-scope-changing proof closeout is also remotely
green, and only after the packet is identified as the sole active Tier C gate,
request one future two-stage sequence:

1. implement and generated-qualify a new additive fixed-path wrapper; and
2. only after that exact implementation is committed, pushed, and both CI jobs
   are green, perform one target-free structural read that emits one coarse
   F03 class route.

This packet records no decision and grants no authority now. The current and
every earlier `continue`, `approve`, or `proceed` message is not retroactive
authority for a packet that did not yet exist. A fresh unambiguous packet-bound
maintainer message is required after the request and its proof closeout are
remotely green.

## Why This Is The Smallest Useful Next Read

Consumed VR9P read and strict-parsed the fixed 418,755-byte target-free
structural manifest once. It retained outer `MARC2VR6-F02` and nested
`MARC2VR2-F03`, excluding F04 for that exact execution while revealing no
failed value, row, path, identity, selection, or cohort.

Artifact-only VR10A then partitioned F03 into 20 leaf predicates. Fifteen are
excluded by committed producer invariants or the retained aggregate counts;
five remain source-dependent. Generated-only VR10B now separates those five
mechanisms with one coarse route each. Exact implementation/result
`61bb801689eb2885b1e96aa4b56c86658dc3b333` passed Base Python job
`95320325187`, Optional Neuro Readers job `95320325136`, and CI
`32007641751`. Proof closeout
`808e8ed300b9b9ea315ee3fa62231ae8d3f545d2` passed Base Python job
`95322252607`, Optional Neuro Readers job `95322252650`, and CI
`32008293036`.

The proposed read asks only which one of those five frozen structural classes
the immutable manifest reaches. It does not repair a predicate, select a
cohort, open an archive member, or inspect neural data.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 implement:

- exact request, decision, implementation, and proof-record validation;
- a fixed-path readiness and no-follow state machine using generated fixtures;
- one clean control and all five exact VR10B witness classes in canonical and
  reversed order across two exact replays;
- exactly one VR6 consistency call and one VR10B discriminator call per path;
- a strict aggregate-output firewall exposing only G1/R1-R5 during generated
  qualification;
- at least 70 direct refusal mutations across proof, path, race, hash, JSON,
  route, leakage, replay, resource, and forbidden-operation boundaries; and
- CLI help, deterministic replay, bounded resources, and zero retained output.

The future module must expose no generic path, URL, output, threshold, retry,
resume, fallback, substitution, or arbitrary execute override. Generated
qualification must not stat, resolve, hash, open, alter, delete, or reuse any
real `.codex_work` path. It must not import, call, patch, copy, or modify the
consumed VR9P executor.

## Proposed One Private Diagnostic

Only after the exact future implementation is remotely green may one command:

1. validate its exact green implementation proof;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` certificate only at
   `.codex_work/marc2_machine_readiness/vr11p/readiness.v0.json`;
4. require `.codex_work/marc2_f03_private_discriminator/v0` to be absent;
5. no-follow preflight the registered structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, hash, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR6 adapter once and require outer F02 plus nested F03;
9. call the exact green VR10B discriminator once; and
10. write at most one aggregate-safe report containing one R1-R5 route.

The immutable source identity is copied only from committed records:

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

Packet preparation performs zero path checks, stats, resolves, hashes, opens,
reads, or parses against that source or any consumed VR9P surface.

## Frozen Route Contract

The private diagnostic has only five accepted observations:

| Aggregate route | Maximum engineering meaning |
|---|---|
| `MARC2VR11P-R1` | the structural manifest reaches frozen class P03 |
| `MARC2VR11P-R2` | the structural manifest reaches frozen class P15 |
| `MARC2VR11P-R3` | the structural manifest reaches frozen class P16 |
| `MARC2VR11P-R4` | the structural manifest reaches frozen class P18 |
| `MARC2VR11P-R5` | the structural manifest reaches frozen class P19 |

VR6 must still produce outer F02 plus nested F03. VR10B G1, another broad
route, a missing or unknown route, source mutation, or leakage consumes and
parks the lane. No result may relax an F03 predicate, retain an in-memory
candidate cohort, or authorize a repair.

The aggregate report may contain only schema and lane identity, status, one
coarse result route, green-proof identity, resource measurements, zero
forbidden-operation counters, warnings, unavailable fields, and claim
boundaries. It may not contain reasons, exception text, predicates, failed
values, source rows, member names, paths, offsets, CRCs, private hashes,
subject IDs, participant IDs, sessions, runs, companion identities, or
candidate selections.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 45 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
VR6 calls / VR10B calls:                 1 / 1
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
  consumed VR9P certificate, marker, output root, executor, or private result;
- a second source open, retry, rerun, resume, repair, fallback, substitution,
  post-result reinspection, or F03 rule relaxation;
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

An R1-R5 observation would choose the subject of a later prospective generated
repair. It would not authorize that repair. A separate repair contract and
Tier C sequence would still be required before another source read. FW2 and
CIL1 remain ineligible because no real cohort has been frozen.

## Current Verification

- Sixteen committed predecessor artifacts total 295,028 bytes and are bound by
  exact path, size, and SHA-256.
- The request test suite verifies all-false authority, zero operations, exact
  proof identity, five-route allowlists, path separation, resources, failure
  semantics, and the scientific ceiling.
- No `.codex_work` path, private source, archive, payload, neural value, target,
  model, prediction, or score is accessed while preparing this packet.
- Exact request commit `6e72c8f797201359777454a750b1dea9704665c0`
  passed both required jobs in CI `32009557248`. This proof closeout changes no
  requested scope and performs no private, real, or scientific operation. It
  must itself become remotely green before the packet may be identified as the
  sole active Tier C gate.

Engineering capability requested: one proof-gated target-free structural open
can distinguish the five remaining F03 classes while retaining only one coarse
route code.

Scientific claim not established: this request performs no private read, and
even a future diagnostic would access no archive or neural payload, target,
prediction, or score, so it establishes no neural effect, decoding accuracy,
language decoding, live decoding, or thought-to-text capability.
