# Ofner 2017 Range-Only Header Activation

Date: 2026-08-29

Packet: `OFNER-C6R-1-HL`

Status: **one exact checkpoint activates only after this activation commit is remotely green**

Machine activation:

- `registries/ofner_gdf_header_live_activation.v0.json`

## Green Basis

The packet-bound decision is remotely green at
`8ed4b7c93ad1a53c30bdacac63934a30d9f6a2f4`, CI `33275389198`, Base
Python `99161070113`, and Optional Neuro Readers `99161070207`.

The exact generated-qualified implementation is remotely green at
`b6c55dfed93d803a14df906f9c0b57c04e44cd58`, CI `33277551227`, Base
Python `99166826652`, and Optional Neuro Readers `99166826697`.

Its machine implementation record is 5,871 bytes at SHA-256
`9f012dd672f1914a835526221423674537e55ba0cc6431a9afd469b9b0318173`.
The implementation passed two deterministic generated replays, 35 named
adversarial refusals, the complete local pytest suite, and both remote suites.
It made zero real or network operation.

## Activated Operation

Only after this exact activation is committed, pushed to GitHub `main`, and
both named CI jobs are green may execution ordinal 1:

1. freshly verify the exact decision, implementation, and activation commits
   plus their six required CI jobs;
2. require a clean tracked checkout at the activation commit;
3. enforce one CPU thread, one worker, zero numerical jobs, 120 seconds,
   256 MiB peak RSS, 4 MiB incremental disk, 1 MiB public output, and at
   least 2 GiB free disk;
4. durably write and sync the unique no-clobber consumed marker;
5. construct the proxy-free, verified-TLS, no-redirect opener;
6. make one GET of the exact pinned NEMAR manifest in memory;
7. verify its exact canonical identity and the participant-1/run-1 member;
8. make `bytes=0-255` and then
   `bytes=256-(declared_header_length-1)` requests to the exact stable GDF URL;
9. parse one complete header without trailing bytes; and
10. publish one aggregate `OFNER-H1`, `OFNER-H0-REPRESENTATION`, or
    `OFNER-H0-TRANSPORT` result and stop.

The activation permits no redirect, retry, rerun, repair, resume, fallback,
substitution, alternate host, or additional member. Every post-marker outcome
consumes the packet.

## Closed Capabilities

This activation does not permit a whole-GDF request, full-payload hash,
manifest or range retention, event or annotation read, signal-sample read,
target or label read, cache, split, feature, model, checkpoint, training,
inference, prediction, score, language-model call, stream, device, hardware,
release, or scientific-claim upgrade. It does not touch another dataset,
private artifact, project, or cleanup surface.

`OFNER-H1` can establish only that one source file exposes the preregistered
fixed-header representation. It can justify a later acquisition
preregistration, but cannot authorize that acquisition.

Engineering capability activated: after this record is remotely green, one
proof-bound range-only checkpoint may verify one exact public GDF fixed-header
representation without downloading or retaining the full payload.

Scientific claim not established: this activation is not an EEG result and
establishes no neural effect, EEG beyond EOG or kinematics, unseen-person
generalization, movement intention, motor-cortex causation, thought or
language decoding, live decoding, hardware result, or clinical utility.
