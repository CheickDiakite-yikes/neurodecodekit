# MARC2-VR24P F06 Private Five-Route Discriminator Authorization Packet

Date: 2026-08-22

Lane: `MARC2-VR24P`

Status: **All-false Tier C request prepared; no decision and no private access**

Request:
`registries/marc2_f06_private_five_route_discriminator_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, receives a
non-scope-changing proof closeout that is also remotely green, is identified as
the sole active Tier C gate, and is incorporated by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path wrapper around the
   exact green VR23A five-route discriminator; and
2. only after that exact wrapper and a proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and consume the lane at one aggregate five-route F06 class or a fail-closed
   non-F06/unknown route.

This packet records no decision and grants no authority now. The maintainer's
current `continue` preceded this exact packet and is not retroactive Tier C
authority. Fresh unambiguous packet-bound words are required after the request
and its proof closeout are remotely green.

## Why This Is The Smallest Useful Read

Consumed VR22P returned only `MARC2VR22P-R4`, excluding F07 and leaving VR20A
F06. VR23A then generated-qualified five independently reachable F06 classes:
entry-kind arithmetic, complete-bundle arithmetic, taxonomy membership,
238/195/43 class arithmetic, and eligible participant-session distribution.

Exact VR23A implementation `9e1b12139ad9cd9bcd2245a1eb74b85d7a3cbeeb`
passed Base Python job `97089462251`, Optional Neuro Readers job `97089462366`,
and CI `32596999769`. Proof-only closeout
`7d6b6c59709cf069e5b119845565bb91d1f3303b` passed Base Python job
`97090919812`, Optional Neuro Readers job `97090919708`, and CI `32597604907`
without repeating qualification or touching private state.

The next useful question is narrow: which one of those five public classes
describes the exact target-free private source? This packet does not request a
cohort freeze, archive member, signal sample, event, target, model, or score.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a
dependency-free fixed-path wrapper that:

- validates this request, its future decision, and the exact green VR23A proof
  chain;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, substitution,
  route, or reason override;
- replays the six VR23A cases in two orders and two exact replays;
- calls unchanged `discriminate_generated_source` once per generated path,
  with exactly one nested unchanged VR20A call;
- qualifies fresh-path readiness, no-follow source handling, marker order,
  strict JSON, aggregate output safety, deterministic replay, and fail-closed
  resources using generated temporary fixtures only;
- passes at least 80 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect consumed
VR22P or any earlier private executor, source, certificate, marker, or output.

## Proposed One Private Discriminator

Only after the future wrapper and proof-only closeout are remotely green may
one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at the registered
   VR24P readiness path;
4. require the registered output root to be absent and reject symlinks/aliases;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call exact green VR23A once, with one nested unchanged VR20A call;
9. retain only one aggregate R1-R5 class, or park at a non-F06/unknown route;
   and
10. write one aggregate-safe mode-`0644` report containing no private identity,
    predicate, value, row, path, or failure reason.

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

Packet preparation performs zero stats, resolves, hashes, opens, reads,
parses, existence checks, or writes against that path or any `.codex_work`
path.

## Frozen Terminal Routes

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR24P-R1` | entry-kind count arithmetic class |
| `MARC2VR24P-R2` | complete-bundle count arithmetic class |
| `MARC2VR24P-R3` | participant taxonomy-membership class |
| `MARC2VR24P-R4` | 238/195/43 taxonomy-class arithmetic class |
| `MARC2VR24P-R5` | eligible participant-session distribution class |
| `MARC2VR24P-R6` | readiness, fixed-path, or output precondition refused |
| `MARC2VR24P-R7` | source identity or strict structural envelope refused |
| `MARC2VR24P-R8` | exact source did not reproduce VR20A F06 |
| `MARC2VR24P-R9` | unknown, privacy, deterministic-output, or resource refusal |

R1-R5 contain only class identity, never the failed predicate or value. R8/R9
park rather than guessing. Every route consumes the one invocation. No route
permits retry, rerun, resume, repair, fallback, substitution, private
reinspection, or post-result amendment.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 60 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
VR23A real calls:                        exactly 1
nested VR20A real calls:                 exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 1 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request consumed-state access, archive headers or members,
EEG/MEG samples, events, channels, geometry, labels, targets, sentences, keys,
models, predictions, scores, downloads, network, features, caches, NeuroTokens,
training, inference, scoring, selection, cohort creation, FW2, CIL1, RW3,
providers, streams, devices, hardware, release, publication, or scientific
claim authority.

## What Success Changes

R1-R5 would identify one aggregate structural class for a separately frozen
generated repair. It would not freeze a cohort or make FW2 eligible. R6-R9
would park the lane with a measured reason class.

Engineering capability requested: one proof-gated target-free structural read
can localize the remaining VR20A F06 blocker to one of five generated-qualified
public classes without retaining private details.

Scientific claim not established: this request performs no private read, and
even a future execution would not establish neural information, decoding
accuracy, language decoding, unseen-person generalization, live decoding, or
thought-to-text capability.
