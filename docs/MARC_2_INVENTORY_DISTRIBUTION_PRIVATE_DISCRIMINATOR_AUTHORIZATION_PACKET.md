# MARC2-VR30P Inventory/Distribution Private Discriminator Authorization Packet

Date: 2026-08-23

Lane: `MARC2-VR30P`

Status: **All-false Tier C request prepared locally; remote proof pending**

Request:
`registries/marc2_inventory_distribution_private_discriminator_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, followed by a
proof-only request closeout that is also remotely green, identification as the
sole active Tier C gate, and incorporation by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path wrapper around the
   remotely green VR29A discriminator; and
2. only after that exact wrapper and its proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and consume the lane at one aggregate inventory/distribution route.

This packet records no decision and grants no authority now. The maintainer's
current `continue` predates this exact packet and is not retroactive Tier C
authority. Fresh unambiguous packet-bound words are required after the packet
and its proof-only request closeout are remotely green.

## Why This Is The Smallest Useful Read

Consumed VR28P returned only `MARC2VR28P-R1`. That route excludes unknown-
participant taxonomy and leaves exactly two public validator classes:
filtered eligible-total arithmetic or participant-session distribution
arithmetic. It retained no failed predicate, value, count, direction,
distribution, row, path, identity, participant, selection, or cohort and
cannot be retried or inspected.

Generated VR29A proved that these two remaining classes are separable through
unchanged VR25A and VR2 code. Registration
`fcd088cc2eef6556f36ed596c6d9bb6c7ee9d7c3` passed CI `32618866986`.
Exact implementation `2e73c9176d243b5deccbf8416bb59fdf053ba762`
passed Base Python job `97146675300`, Optional Neuro Readers job
`97146675166`, and CI `32620018855`. Proof-only closeout
`80badb9c1410c1661403aae966b1ea31fa0a45f1` passed Base Python job
`97148293434`, Optional Neuro Readers job `97148293619`, and CI
`32620685817` without repeating qualification or touching private state.

The next useful question is therefore exact and binary: does the immutable
target-free structural inventory fail eligible-total arithmetic or
participant-session distribution arithmetic? This packet does not open an
archive member, neural sample, event, target, or model.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a dependency-
free wrapper that:

- validates this request, its future decision, and every exact green VR29A
  artifact;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, fallback,
  substitution, route, or reason override;
- replays the eight registered VR29A cases in two orders and two exact replays;
- calls unchanged VR29A exactly once per generated path and retains only its
  aggregate route;
- qualifies readiness, no-follow source handling, marker order, strict JSON,
  aggregate-only output, deterministic replay, and fail-closed resources using
  only generated temporary fixtures;
- passes at least 90 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect any consumed
VR20P, VR22P, VR24P, VR26P, VR28P, or earlier private executor, certificate,
marker, source, output, or result root.

## Proposed One Private Discriminator

Only after the exact future wrapper and its proof-only closeout are remotely
green may one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at
   `.codex_work/marc2_machine_readiness/vr30p/readiness.v0.json`;
4. require `.codex_work/marc2_inventory_distribution_private_discriminator/v0`
   to be absent and reject every symlink or alias;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call exact green VR29A once without mutating the source;
9. retain only the mapped R1 or R2 aggregate route; and
10. write one aggregate-safe mode-`0644` report containing only R1 or R2, or a
    safe consumed failure route, with no private detail.

The immutable source identity is copied only from committed records:

```text
path:        .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
mode:        0600
bytes:       418,755
SHA-256:     2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
rows:        1,227
files:       1,025
directories: 202
private predicate, count, distribution, and cohort: unavailable
```

Packet preparation performs zero stats, resolves, hashes, opens, reads, parses,
existence checks, or writes against that path or any `.codex_work` path.

## Frozen Terminal Routes

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR30P-R1` | filtered eligible-total arithmetic differs |
| `MARC2VR30P-R2` | participant-session distribution arithmetic differs |
| `MARC2VR30P-R3` | readiness, fixed-path, or output precondition refused |
| `MARC2VR30P-R4` | source identity or strict structural envelope refused |
| `MARC2VR30P-R5` | unexpected upstream, privacy, deterministic-output, or resource refusal |

Only R1 and R2 answer the registered binary question. Neither route may retain
or publish the failed predicate, value, count, direction, distribution, row,
path, identity, participant, selection, or cohort. Every route consumes the
one invocation. No route permits retry, rerun, resume, repair, fallback,
substitution, private reinspection, or post-result amendment.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification:                 <= 60 seconds
future private command:                  <= 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
VR29A real discriminator calls:          exactly 1
VR25A calls nested inside VR29A:          exactly 1
VR2 eligible-filter calls if R1:         exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 1 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- authority before a separate remotely green packet-bound decision;
- access to any consumed private certificate, marker, executor, source,
  output, or result root, including VR28P;
- retention or inference of any private predicate, value, count, direction,
  distribution, row, path, identity, participant, selection, or cohort;
- archive headers or members, EEG/MEG samples, events, channels, geometry,
  quality, labels, targets, sentences, keys, or outcomes;
- data acquisition, download, network access, or new payload bytes;
- feature extraction, cache creation, NeuroTokens, training, inference,
  prediction, freezing, target delivery, scoring, model or threshold selection,
  or post-result tuning;
- FW2, CIL1, RW3, language models, providers, streams, devices, hardware,
  release, publication, or replication; or
- any neural, decoding, language, thought, live, real-time, portable, home-use,
  assistive, clinical, or unseen-person claim.

## What Success Changes

R1 would localize the structural blocker to filtered eligible-total arithmetic.
R2 would localize it to participant-session distribution arithmetic. Either
result remains structural, does not reveal the private value, and cannot freeze
a cohort or open FW2 by itself.

Engineering capability requested: one proof-gated target-free structural read
can distinguish the final two generated-qualified VR28P R1 classes without
retaining private details.

Scientific claim not established: this request performs no private read, and
even a future R1 or R2 would not establish neural information, decoding
accuracy, language decoding, unseen-person generalization, or live decoding.
