# MARC2-VR28P Inventory/Taxonomy Private Discriminator Authorization Packet

Date: 2026-08-22

Lane: `MARC2-VR28P`

Status: **All-false Tier C request prepared locally; remote proof pending**

Request:
`registries/marc2_inventory_taxonomy_private_discriminator_authorization_request.v0.json`

## Decision Requested

Request one bounded two-stage sequence after, and only after, this exact packet
is committed, pushed, remotely green in both required jobs, followed by a
proof-only request closeout that is also remotely green, identification as the
sole active Tier C gate, and incorporation by a fresh maintainer decision:

1. implement and generated-qualify one additive fixed-path wrapper around the
   remotely green VR25A firewall and VR27A route map; and
2. only after that exact wrapper and its proof-only closeout are committed,
   pushed, and remotely green, perform one target-free private structural read
   and consume the lane at one aggregate inventory/taxonomy route.

This packet records no decision and grants no authority now. The maintainer's
current `continue` predates this exact packet and is not retroactive Tier C
authority. Fresh unambiguous packet-bound words are required after the packet
and its proof-only request closeout are remotely green.

## Why This Is The Smallest Useful Read

Consumed VR26P returned only `MARC2VR26P-R5`. That route means either VR25A R1
eligible-inventory or participant-session distribution drift, or VR25A R2
unknown-participant taxonomy. It retained no failed predicate, count,
direction, row, path, identity, participant, selection, or cohort and cannot
be retried or inspected.

Generated VR27A proved that those two remaining classes are separable through
the unchanged VR25A firewall. Registration
`47ceba3ed89df9610540fe3ed2ee8071ac1b84df` passed CI `32611101033`.
Exact implementation `3f74be383a672748b0781d6571d28181056865b7`
passed Base Python job `97126099642`, Optional Neuro Readers job
`97126099573`, and CI `32611864949`. Proof-only closeout
`f6b5dbf697d113c330f3fbf542fd97ad1c65d46d` passed Base Python job
`97127512656`, Optional Neuro Readers job `97127512634`, and CI
`32612454458` without repeating qualification or touching private state.

The next useful question is therefore exact and binary: does the immutable
target-free structural inventory reach VR25A R1 or R2? This packet does not
open an archive member, neural sample, event, target, or model.

## Proposed Generated Stage

Only after a separate decision is remotely green may Stage 1 add a dependency-
free wrapper that:

- validates this request, its future decision, and every exact green VR27A
  artifact;
- exposes fixed `plan`, `qualify`, `inspect`, and proof-gated `execute`
  surfaces with no generic path, URL, output, threshold, retry, fallback,
  substitution, route, or reason override;
- replays the five registered VR27A cases in two orders and two exact replays;
- calls unchanged VR25A exactly once and applies the frozen VR27A map exactly
  once per generated path;
- qualifies readiness, no-follow source handling, marker order, strict JSON,
  aggregate-only output, deterministic replay, and fail-closed resources using
  only generated temporary fixtures;
- passes at least 70 direct refusal mutations; and
- retains zero generated output and performs zero `.codex_work` operations.

The wrapper must not import, call, patch, copy, modify, or inspect any consumed
VR20P, VR22P, VR24P, VR26P, or earlier private executor, certificate, marker,
source, output, or result root.

## Proposed One Private Discriminator

Only after the exact future wrapper and its proof-only closeout are remotely
green may one command:

1. validate every exact green proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. create one fresh mode-`0600` readiness certificate only at
   `.codex_work/marc2_machine_readiness/vr28p/readiness.v0.json`;
4. require `.codex_work/marc2_inventory_taxonomy_private_discriminator/v0` to
   be absent and reject every symlink or alias;
5. no-follow preflight only the registered target-free structural source;
6. create one mode-`0600` consumed marker immediately before content open;
7. open, read, SHA-256 verify, and strict-parse exactly 418,755 bytes once;
8. call exact green VR25A once without mutating the source;
9. apply the exact frozen VR27A route map once; and
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
private count, direction, identities, and cohort: unavailable
```

Packet preparation performs zero stats, resolves, hashes, opens, reads, parses,
existence checks, or writes against that path or any `.codex_work` path.

## Frozen Terminal Routes

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR28P-R1` | eligible inventory or participant-session distribution drift |
| `MARC2VR28P-R2` | unknown participant taxonomy |
| `MARC2VR28P-R3` | readiness, fixed-path, or output precondition refused |
| `MARC2VR28P-R4` | source identity or strict structural envelope refused |
| `MARC2VR28P-R5` | unexpected upstream, privacy, deterministic-output, or resource refusal |

Only R1 and R2 answer the registered binary question. Neither route may retain
or publish the failed predicate, value, count, direction, row, path, identity,
participant, selection, or cohort. Every route consumes the one invocation.
No route permits retry, rerun, resume, repair, fallback, substitution, private
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
VR25A real firewall calls:               exactly 1
VR27A route-map calls:                   exactly 1
network / new payload bytes:             0 / 0
archive member / signal / target bytes:  0 / 0 / 0
combined incremental output:             <= 1 MiB
retries / reruns / resumes:              0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- authority before a separate remotely green packet-bound decision;
- access to any consumed private certificate, marker, executor, source,
  output, or result root, including VR26P;
- retention or inference of any private predicate, count, direction, row,
  path, identity, participant, selection, or cohort;
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

R1 would direct the next generated repair toward eligible-inventory and
participant-session distribution arithmetic. R2 would direct it toward the
unknown-participant taxonomy. Either result remains structural and cannot
freeze a cohort or open FW2 by itself.

Engineering capability requested: one proof-gated target-free structural read
can distinguish the final two generated-qualified VR26P R5 classes without
retaining private details.

Scientific claim not established: this request performs no private read, and
even a future R1 or R2 would not establish neural information, decoding
accuracy, language decoding, unseen-person generalization, or live decoding.
