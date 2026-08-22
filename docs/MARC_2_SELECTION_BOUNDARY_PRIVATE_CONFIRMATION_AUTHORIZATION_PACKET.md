# MARC2-VR26P Selection-Boundary Private Confirmation Authorization Packet

Date: 2026-08-22

Lane: `MARC2-VR26P`

Status: **All-false Tier C request prepared locally; remote proof pending**

Request:
`registries/marc2_selection_boundary_private_confirmation_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, followed by a
proof-only request closeout that is also remotely green, identification as the
sole active Tier C gate, and incorporation by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path confirmation
   wrapper around the remotely green VR25A selection-boundary firewall; and
2. only after that exact wrapper and its proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and either freeze one exact private cohort or consume the lane at one
   aggregate failure route.

This packet records no decision and grants no authority now. The maintainer's
current `continue` predates this exact packet and is not retroactive Tier C
authority. A fresh unambiguous packet-bound message is required after the
packet and its proof-only request closeout are remotely green.

## Why This Is The Smallest Needle-Moving Read

Consumed VR24P established only that the recognized complete-bundle total
differs from the frozen public 238 assumption. It did not retain the observed
count, direction, row, identity, selection, or cohort. Generated VR25A then
proved that this full-source compatibility arithmetic can be separated from
the invariants that protect the experiment: exact rows and companion groups,
the exact 195 eligible participant/session distribution, known-ineligible
quarantine, and one unchanged 16-subject selection.

VR25A registration `ad8be2197e58d4d3e0e1fe4f344de1c608930f73` passed CI
`32603540967`. Exact implementation
`891245d73d8e11304d4a98e841ead6f57ad68ff8` passed Base Python job
`97108121455`, Optional Neuro Readers job `97108121321`, and CI
`32604761988`. Proof-only closeout
`378e863641418e0e538f3159d073dd4bcd9c8899` passed Base Python job
`97109778233`, Optional Neuro Readers job `97109778216`, and CI
`32605475758` without repeating qualification or touching private state.

The next useful question is narrow: does that exact firewall accept the
immutable target-free structural inventory and freeze the exact cohort while
keeping the unavailable full-bundle count private? The packet does not open
an archive member or neural sample.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a dependency-
free wrapper that:

- validates this request, its decision, and every exact green VR25A artifact;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, fallback, or
  substitution argument;
- replays the ten registered VR25A generated cases in two orders and two exact
  replays through exactly one VR25A firewall call per path;
- maps VR25A G1 and G2 to separate safe success classes and maps R1-R4 into
  fixed aggregate private-wrapper refusal classes;
- qualifies readiness, no-follow source handling, marker order, strict JSON,
  private/public output separation, deterministic replay, and fail-closed
  resource monitoring using only generated temporary fixtures;
- passes at least 90 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect any consumed
VR22P or VR24P executor, certificate, marker, result root, or private output.

## Proposed One Private Confirmation

Only after the exact future wrapper and its proof-only closeout are remotely
green may one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at
   `.codex_work/marc2_machine_readiness/vr26p/readiness.v0.json`;
4. require `.codex_work/marc2_selection_boundary_private_confirmation/v0` to
   be absent and reject every symlink or alias;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR25A firewall once without mutating the source;
9. on G1 or G2, write one mode-`0600` source-exact private cohort manifest;
10. write one aggregate-safe mode-`0644` report with no private identity; and
11. consume the invocation with no retry, rerun, resume, or repair.

The immutable source identity is copied only from already committed private-
lane records:

```text
path:        .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
mode:        0600
bytes:       418,755
SHA-256:     2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
rows:        1,227
files:       1,025
directories: 202
eligible:    exactly 195 bundles required by VR25A
full total:  unavailable and not inferred
```

Packet preparation performs zero stats, resolves, hashes, opens, reads, parses,
existence checks, or writes against that path or any `.codex_work` path.

Fifteen request-specific tests, 45 combined VR25A/VR26P tests, and all 4,988
dependency-light tests pass with 204 expected skips and zero failures, 15 tests
above the 4,973-test pre-request baseline. Ruff, compilation, request JSON, and
`git diff --check` pass. No generated qualification or private operation ran.

## Frozen Success Contract

`MARC2VR26P-R1` and `MARC2VR26P-R2` are the only successful terminal routes.
Both require exactly:

- 16 selected subjects from one maximal contiguous target-free rank prefix;
- three complete `ses-01` fit runs and three complete `ses-02` held-out runs
  per selected subject;
- 96 selected run bundles, split 48 fit and 48 held-out;
- 384 source-exact core members;
- reservation at or below 8 GiB using exact UTF-8 source names;
- no later-subject inspection, skipping, substitution, backfill, or cap raise;
- a byte-stable private manifest containing selected structural rows, split
  identities, contract hashes, source hash, semantic cohort digest, and
  source-exact selected-name hash; and
- an aggregate report containing only counts, hashes, bytes, route, the
  compatibility boolean, resource measurements, warnings, unavailable fields,
  and claim boundaries.

R1 means the public-total compatibility boolean is true. R2 means it is false
and the exact cohort still passed every stronger invariant. Neither route may
publish or retain the observed full-bundle count, difference, direction, or a
private ineligible inventory outside the protected manifest.

Public output may not contain member names, source paths, subject or
participant IDs, sessions, runs, companions, offsets, CRCs, per-item rows,
reasons, exception text, labels, targets, predictions, or scores.

Safe consumed failure routes are fixed as:

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR26P-R3` | readiness, fixed-path, or output precondition failed |
| `MARC2VR26P-R4` | source identity, row, entry-kind, or companion integrity failed |
| `MARC2VR26P-R5` | participant taxonomy or exact eligible inventory failed |
| `MARC2VR26P-R6` | selection, split, rank, reservation, or final identity failed |
| `MARC2VR26P-R7` | privacy, deterministic-output, or resource validation failed |

Each failure consumes the one invocation. No route permits retry, rerun,
resume, repair, fallback, substitution, private reinspection, or post-result
amendment.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 60 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
VR25A real firewall calls:               exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 2 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- authority before a separate remotely green packet-bound decision;
- access to any consumed VR22P/VR24P certificate, marker, output, executor, or
  private result root, or any retry or reinspection of those lanes;
- publication or inference of the observed private full-bundle count,
  difference, direction, identity, or known-ineligible inventory;
- archive local headers, compressed members, EEG/MEG samples, events, channels,
  geometry, quality, labels, targets, sentences, keys, or outcomes;
- data acquisition, download, network access, or more than zero new payload
  bytes;
- feature extraction, cache creation, NeuroTokens, training, inference,
  prediction, freezing, target delivery, scoring, model selection, threshold
  selection, or post-result tuning;
- FW2, CIL1, RW3, language models, providers, streams, devices, hardware,
  release, or publication; or
- any neural, decoding, language, thought, live, real-time, portable, home-use,
  assistive, clinical, or unseen-person claim.

## What Success Changes

A valid R1 or R2 result would freeze the exact target-free structural cohort
needed to prepare a prospective FW2 neural-payload contract.
It would not authorize FW2, open neural data, or establish a neural effect.
CIL1 remains later and separate.

Engineering capability requested: one proof-gated target-free structural read
can confirm the selection-boundary firewall and freeze one exact source-bound
private cohort without opening a neural payload.

Scientific claim not established: this request performs no private read, and
even future R1 or R2 would establish only structural cohort eligibility, not
neural information, decoding accuracy, language decoding, live decoding, or
thought-to-text capability.
