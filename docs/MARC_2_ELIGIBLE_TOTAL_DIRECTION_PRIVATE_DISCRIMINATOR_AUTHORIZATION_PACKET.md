# MARC2-VR32P Eligible-Total Direction Private Discriminator Authorization Packet

Date: 2026-08-23

Lane: `MARC2-VR32P`

Status: **All-false Tier C request prepared; no decision or private access**

Machine request:
`registries/marc2_eligible_total_direction_private_discriminator_authorization_request.v0.json`

## Question

The consumed VR30P result establishes that the filtered eligible total differs
from 195, but it does not reveal whether the total is below or above that
public threshold. Generated VR31A now distinguishes those two directions
without returning a count or difference.

This packet asks permission for one future proof-gated target-free structural
invocation that may retain exactly one answer:

- `MARC2VR32P-R1`: filtered eligible total is below 195; or
- `MARC2VR32P-R2`: filtered eligible total is above 195.

It may not retain the observed total, difference, participant, row, path,
distribution, selection, reservation, or cohort. This is a structural cohort-
recovery question, not neural or scientific evidence.

## Requested Two-Stage Sequence

### Stage 1: generated wrapper

Only after this request and a separate packet-bound decision are committed,
pushed, and remotely green:

1. implement a standard-library fixed-path wrapper around unchanged VR31A;
2. qualify it only with the eight registered generated fixtures across two
   orders and two replays;
3. preserve exact G1/G2/R1/R2/R3 counts 4/4/4/4/16;
4. prove marker-before-open ordering and aggregate-output firewalls;
5. retain zero generated source or report bytes.

### Stage 2: one target-free private direction check

Only after exact Stage 1 and a separate proof-only closeout are each committed,
pushed, and remotely green:

1. collect three fresh readiness samples;
2. create one new consumed marker before source content access;
3. open and strict-parse exactly one registered 418,755-byte target-free
   structural JSON source once;
4. call unchanged VR31A exactly once;
5. write only one aggregate R1/R2 answer or one safe failure route;
6. consume the invocation with no retry, rerun, resume, repair, fallback,
   substitution, cleanup, amendment, or private reinspection.

## Fixed Paths

The future wrapper must expose no generic path, URL, output, route, count,
threshold, resource, retry, or substitution option. Its private paths are
fixed in the machine request. The existing private-source identity is copied
only from committed records; this packet does not stat, resolve, hash, list,
or open that path.

The new readiness and output parents must be absent before Stage 2. Existing
VR20P, VR22P, VR24P, VR26P, VR28P, and VR30P private or consumed state is
strictly forbidden.

## Resource Envelope

- one CPU thread, worker, and numerical job;
- 60 seconds for generated qualification;
- 650 seconds for the future private invocation, including readiness wait;
- less than 256 MiB peak RSS;
- at least 15 GiB free disk;
- exactly one 418,755-byte source content open;
- at most 1 MiB combined incremental output;
- zero network, download, new payload, archive-member, neural-signal, target,
  model, prediction, score, device, stream, or hardware bytes/operations;
- zero retry or rerun.

## Current Authority

Every authorization flag is false and every operation counter is zero. This
packet performs no implementation, generated qualification, readiness,
private path, archive, neural, target, model, score, network, device, release,
or claim operation.

It must be committed, pushed, and both CI jobs green, followed by a separate
proof-only request closeout that is also committed, pushed, and green. Only
then may VR32P be identified as the sole active Tier C packet. A fresh packet-
bound maintainer message and a separately green decision are still required
before Stage 1. The current `continue` predates this packet and is not
retroactive authority.

Engineering capability requested: one proof-separated aggregate-only
structural check that distinguishes below-expected from above-expected
eligible totals without exposing an observed count.

Scientific claim not established: this request accesses no neural payload,
target, model, prediction, or score and establishes no neural effect, decoding
accuracy, language decoding, unseen-person generalization, live decoding, or
thought-to-text capability.
