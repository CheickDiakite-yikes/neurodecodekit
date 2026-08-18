# MARC2-VR12P P15 Private Confirmation Authorization Packet

Date: 2026-08-18

Lane: `MARC2-VR12P`

Status: **All-false Tier C request remotely green; proof-only closeout pending
its own remote green proof before packet identification**

Request:
`registries/marc2_p15_private_confirmation_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, identified as the
sole active Tier C gate, and incorporated by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path confirmation
   wrapper around the remotely green P15 run-index adapter; and
2. only after that exact wrapper and its proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and either freeze one private structural cohort or consume the lane at one
   aggregate failure route.

This packet records no decision and grants no authority now. The maintainer's
current instruction to complete steps 1-6 predates this exact packet and is not
retroactive Tier C authority for it. A fresh unambiguous packet-bound message
is required after the packet's own remote proof is green.

The immutable request commit
`816589473eafabdebe66be2b4e921b005f04a959` passed Base Python job
`95825074164`, Optional Neuro Readers job `95825073430`, and CI
`32171993061`. This proof-only closeout records those results and the exact
request artifact snapshots. It changes no requested scope and performs no
private, real-data, or scientific operation. The closeout itself must be
committed, pushed, and green in both required jobs before this packet can be
identified as the sole active Tier C gate.

## Why This Is The Smallest Needle-Moving Read

Consumed VR11P localized the remaining structural blocker to P15 without
retaining a failed value, path, row, person, selection, or cohort. Generated
VR12A then showed that accepting one- or two-digit numeric BIDS run indices can
preserve the same semantic selection while keeping source-exact names,
reservation arithmetic, identity, companion, split, rank, and storage gates.

Exact generated implementation
`873484aaf270bc5b1499e4b0449c9e8ef138c623` passed Base Python job
`95819297085`, Optional Neuro Readers job `95819297010`, and CI
`32170217284`. Proof-only closeout
`8f2ad163f3beacaf3cbcc0287fe305575a34b6cc` passed Base Python job
`95821386966`, Optional Neuro Readers job `95821386899`, and CI
`32170855368` without rerunning qualification or touching a private path.

The next useful question is therefore narrow: does that exact repaired adapter
accept the immutable target-free structural inventory and produce a valid
bounded cohort? The packet does not open an archive member or neural sample.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a dependency-
free wrapper that:

- validates this request, its decision, and the exact green VR12A artifacts;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, fallback, or
  substitution argument;
- replays the three registered generated source spellings in two orders and
  two replays through exactly one VR12A adapter call per path;
- qualifies fresh-path readiness, no-follow source handling, marker order,
  strict JSON, private/public output separation, deterministic replay, and
  fail-closed resource monitoring using only generated temporary fixtures;
- passes at least 50 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect the consumed
VR11P executor, result, certificate, marker, or output root.

## Proposed One Private Confirmation

Only after the exact future wrapper and its proof-only closeout are remotely
green may one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at
   `.codex_work/marc2_machine_readiness/vr12p/readiness.v0.json`;
4. require `.codex_work/marc2_p15_private_confirmation/v0` to be absent and
   reject every symlink or alias;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR12A adapter once without mutating the source;
9. on success, write one mode-`0600` source-exact private cohort manifest; and
10. write one aggregate-safe mode-`0644` report with no private identity.

The immutable source identity is copied only from committed VR11P records:

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

Packet preparation performs zero stats, resolves, hashes, opens, reads, parses,
existence checks, or writes against that path or any `.codex_work` path.

## Frozen Success Contract

`MARC2VR12P-R1` is the only successful terminal route. It requires:

- a maximal contiguous prefix of 12-19 ranked subjects;
- exactly three complete runs from `ses-01` and three from `ses-02` per
  selected subject;
- 72-114 selected run bundles and 288-456 source-exact core members;
- equal fit and held-out bundle counts;
- reservation at or below 8 GiB using exact UTF-8 source names;
- no later-subject inspection, skipping, substitution, backfill, or cap raise;
- a byte-stable private manifest containing the selected structural rows,
  split identities, contract hashes, source hash, semantic cohort digest, and
  source-exact selected-name hash; and
- an aggregate report containing only counts, hashes, bytes, route, resource
  measurements, warnings, unavailable fields, and claim boundaries.

Public output may not contain member names, source paths, subject or participant
IDs, sessions, runs, companions, offsets, CRCs, per-item rows, reasons,
exception text, labels, targets, predictions, or scores.

Safe consumed failure routes are fixed as:

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR12P-R2` | readiness, fixed-path, or output precondition failed |
| `MARC2VR12P-R3` | registered source identity or strict structural envelope failed |
| `MARC2VR12P-R4` | repaired identity, task, or companion validation refused |
| `MARC2VR12P-R5` | selection, split, rank, or reservation validation refused |
| `MARC2VR12P-R6` | privacy, deterministic-output, or resource validation refused |

Each failure consumes the one invocation. No route permits retry, rerun,
resume, repair, fallback, substitution, private reinspection, or post-result
amendment.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 45 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
VR12A real adapter calls:                exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 2 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- authority before a separate remotely green decision;
- access to any consumed VR9P/VR11P certificate, marker, output, executor, or
  result, or any retry or reinspection of those lanes;
- archive local headers, compressed members, EEG/MEG samples, events, channels,
  geometry, quality, labels, targets, sentences, keys, or participant outcomes;
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

A valid R1 result would freeze the target-free structural cohort needed to
prepare a prospective FW2 neural-payload contract. It would not authorize FW2,
open neural data, or establish a neural effect. CIL1 remains later and separate.

Engineering capability requested: one proof-gated target-free structural read
can confirm the repaired selector and freeze a source-exact private cohort
without opening a neural payload.

Scientific claim not established: this request performs no private read, and
even future R1 would establish only structural cohort eligibility, not neural
information, decoding accuracy, language decoding, live decoding, or thought-
to-text capability.
