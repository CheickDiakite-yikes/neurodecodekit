# MARC2-VR16P Variable-Width Private Confirmation Authorization Packet

Date: 2026-08-21

Lane: `MARC2-VR16P`

Status: **All-false Tier C request prepared; no decision and no private access**

Request:
`registries/marc2_variable_width_private_confirmation_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, receives a
non-scope-changing proof closeout that is also remotely green, is identified as
the sole active Tier C gate, and is incorporated by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path wrapper around the
   remotely green VR16A variable-width adapter; and
2. only after that exact wrapper and its proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and either freeze one source-exact private cohort or consume the lane at one
   aggregate failure route.

This packet records no decision and grants no authority now. The maintainer's
current `continue` preceded this exact packet and is not retroactive Tier C
authority. Fresh unambiguous packet-bound words are required after the request
and its proof closeout are remotely green.

## Why This Is The Smallest Needle-Moving Read

Consumed VR15P localized the real structural incompatibility to run-token
width without retaining the token, path, row, identity, participant, or
cohort. VR16A then proved on generated sources that ASCII numeric run tokens
of one, two, three, six, and 64 digits, plus bundle-consistent mixed widths,
preserve the same semantic selection when leading zeroes are canonicalized.

Exact generated implementation
`6f92b84c7be67848c7d09b567f13b08a14d33f5c` passed Base Python job
`96704807926`, Optional Neuro Readers job `96704808178`, and CI
`32459984049`. Proof-only closeout
`91dd117ca582f9cc3256f7a4feb0f498be8e3956` passed Base Python job
`96706432536`, Optional Neuro Readers job `96706432846`, and CI
`32460539227` without repeating qualification or touching a private path.

The next useful question is therefore narrow: does that exact adapter accept
the immutable target-free structural inventory and produce a bounded cohort?
The packet does not open an archive member, signal sample, event, or target.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a
dependency-free wrapper that:

- validates this request, its decision, and the exact green VR16A artifacts;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, fallback,
  substitution, width, or route override;
- replays all six registered generated width variants in two orders and two
  replays through exactly one VR16A adapter call per path;
- qualifies fresh-path readiness, no-follow source handling, marker order,
  strict JSON, private/public output separation, deterministic replay, and
  fail-closed resource monitoring using only generated temporary fixtures;
- passes at least 70 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect the consumed
VR15P executor, source, readiness certificate, marker, or output root.

## Proposed One Private Confirmation

Only after the exact future wrapper and its proof-only closeout are remotely
green may one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at
   `.codex_work/marc2_machine_readiness/vr16p/readiness.v0.json`;
4. require `.codex_work/marc2_variable_width_private_confirmation/v0` to be
   absent and reject every symlink or alias;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR16A adapter once without mutating the source;
9. on success, write one mode-`0600` source-exact private cohort manifest; and
10. write one aggregate-safe mode-`0644` report containing no private identity.

The immutable source identity is copied only from committed aggregate records:

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

Packet preparation performs zero stats, resolves, hashes, opens, reads,
parses, existence checks, or writes against that path or any `.codex_work`
path.

## Frozen Terminal Routes

`MARC2VR16P-R1` is the only successful terminal route. It requires:

- a maximal contiguous prefix of 12-19 ranked subjects;
- exactly three complete semantic runs from `ses-01` and three from `ses-02`
  per selected subject;
- 72-114 selected run bundles and 288-456 source-exact core members;
- equal fit and held-out bundle counts;
- reservation at or below 8 GiB using exact UTF-8 source names;
- no later-subject inspection, skipping, substitution, backfill, or cap raise;
- a byte-stable private manifest containing selected structural rows, split
  identities, contract hashes, source hash, semantic cohort digest, and
  source-exact selected-name hash; and
- an aggregate report containing only counts, hashes, bytes, route, resource
  measurements, warnings, unavailable fields, and claim boundaries.

Public output may not contain member names, source paths, subject or
participant IDs, sessions, runs, companions, offsets, CRCs, per-item rows,
reasons, exception text, labels, targets, predictions, or scores.

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR16P-R1` | exact adapter accepted and froze one bounded structural cohort |
| `MARC2VR16P-R2` | readiness, fixed-path, or output precondition refused |
| `MARC2VR16P-R3` | source identity or strict structural envelope refused |
| `MARC2VR16P-R4` | numeric identity, task, or companion validation refused |
| `MARC2VR16P-R5` | taxonomy, selection, split, rank, or reservation refused |
| `MARC2VR16P-R6` | privacy, deterministic-output, or resource validation refused |

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
VR16A real adapter calls:                exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 2 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- authority before a separate remotely green decision;
- access to any consumed VR15P certificate, marker, source, output, executor,
  or result, or any retry or reinspection of that lane;
- archive local headers, compressed members, EEG/MEG samples, events,
  channels, geometry, quality, labels, targets, sentences, keys, or participant
  outcomes;
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
can confirm the variable-width selector and freeze a source-exact private
cohort without opening a neural payload.

Scientific claim not established: this request performs no private read, and
even future R1 would establish only structural cohort eligibility, not neural
information, decoding accuracy, language decoding, live decoding, or
thought-to-text capability.
