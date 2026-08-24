# EEGMMIDB-UG1 Stage M Metadata Authorization Packet

Date: 2026-08-24

Status: **All authority false; request only**

Machine request:

- `registries/eegmmidb_unseen_participant_metadata_authorization_request.v0.json`

## Purpose

Stage G is consumed and remotely green. Stage M is the next independent gate:
freeze the exact byte size and available HTTP validator fields for only the 36
already-preregistered EEGMMIDB EDF paths without opening or downloading an EDF
body.

This packet does not authorize implementation or network access. It defines a
future two-stage operation that requires a fresh packet-bound maintainer
decision after this exact request and its proof-only closeout are remotely
green.

## Immutable Proof Anchor

Stage G closeout commit `5cc3e0e9fd5739e8836ddb91252f18ca7849c824`
passed Base Python job `97373297588`, Optional Neuro Readers job
`97373297708`, and CI `32708050897`. The request binds 20 exact research,
contract, decision, amendment, implementation, result, code, and test artifacts
totaling 305,662 bytes under canonical artifact-set SHA-256
`20d3106a66e78053bc73798762aed11b3713a5d4f414bd45528cc2c2f834bea6`.

## Requested Stage 1: Generated Implementation

Only after a future decision is itself committed, pushed, and both CI jobs are
green, implement and adversarially qualify a dependency-light metadata client
using generated local fixtures and mocked HTTP responses only.

The implementation must provide:

- exact ordered 36-URL validation;
- standard-library HTTPS with certificate verification;
- `HEAD` as the only method;
- exact host, path, status, redirect, header, size, and validator checks;
- zero response-body reads;
- one request per path, zero retries, and zero fallback;
- canonical bounded inventory and human receipt serializers;
- atomic no-clobber output and post-publication resource checks; and
- refusals for redirects, aliases, duplicates, missing or conflicting sizes,
  malformed validators, body bytes, output collisions, cap breaches, and a
  second invocation.

Generated implementation qualification may not contact a network, inspect a
real URL, open a local data path, or reuse the consumed Stage G invocation.
The exact implementation must be committed, pushed, and remotely green before
Stage 2.

## Requested Stage 2: One Metadata Invocation

Only after the exact implementation is remotely green, make one sequential
invocation over the 36 named URLs under these rules:

- request exactly once per path, in frozen order;
- use only HTTPS `HEAD` to `physionet.org`;
- accept only direct `200` responses;
- follow zero redirects and perform zero retries;
- read zero response-body bytes;
- require one nonnegative exact `Content-Length` per path;
- record `ETag`, `Last-Modified`, and `Accept-Ranges` only when directly
  returned and syntactically valid;
- preserve absent optional validators as unavailable rather than inferring
  them;
- require 36 distinct paths and a combined size no greater than 268,435,456
  bytes; and
- emit one canonical inventory and one human receipt under 1 MiB combined.

Any mismatch, missing required size, redirect, response body, extra request,
timeout, cap breach, or filesystem collision refuses without retry,
substitution, acquisition, or repair. A failed or successful real invocation
consumes Stage M.

## Resource Envelope

Stage 1 and Stage 2 each use one CPU thread, one worker, and one numerical job.
Stage 2 is capped at 36 requests, 300 seconds, 268,435,456-byte peak RSS,
2,097,152 application-visible metadata bytes, 1,048,576 generated output
bytes, zero payload bytes, and at least 2 GiB free disk. TLS and transport
overhead not exposed by the standard library are reported unavailable; the
zero-body contract and request count are the enforceable network-payload
boundary.

## Explicit Exclusions

This request does not authorize:

- `GET`, `Range`, redirects, retries, authentication, or provider tools;
- EDF body, header, annotation, event channel, signal, channel, geometry,
  sampling, task, target, label, epoch, or trial access;
- `.event` sidecars or any additional participant, run, or file;
- local real-data path listing, statting, resolving, hashing, or opening;
- acquisition, derivative, split, feature, cache, checkpoint, prediction,
  inference, training, scoring, target delivery, or model selection;
- S20, S21, S24, S25, SpanishBCBL, Freewill, IACKD, or another dataset;
- language models, providers, RW3, streams, devices, hardware, release, or
  publication; or
- any scientific, decoding, neural, unseen-person, real-time, portable,
  home-use, assistive, or clinical claim.

## Decision Boundary

Every authority flag in the machine request is false. After this request and a
separate proof-only closeout are remotely green, it may be named as the sole
active Tier C packet. Only the maintainer's next unambiguous packet-bound words
may authorize its exact two-stage maximum.

Engineering capability proposed: an exact, body-blind metadata identity gate
for the 36 preregistered EEGMMIDB files.

Scientific claim not established: this all-false request performs no network
or data operation and establishes no EEG, decoding, unseen-person, causal,
live, hardware, or clinical result.
