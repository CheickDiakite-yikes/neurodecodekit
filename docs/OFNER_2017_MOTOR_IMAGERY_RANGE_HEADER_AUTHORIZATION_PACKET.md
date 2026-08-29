# Ofner 2017 Range-Only Header Authorization Packet

Date: 2026-08-29

Packet ID: `OFNER-C6R-1-HL`

Status: **request only; every authority flag remains false**

Machine request:

- `registries/ofner_2017_motor_imagery_range_header_authorization_request.v0.json`

## Why This Is The Next Gate

The fresh Ofner source is selected, the bounded acquisition design is proven,
and the dependency-free GDF 2.x parser plus no-overread range firewall are
remotely green. What remains unknown is whether one real original source GDF
actually exposes the reported 61 EEG, three EOG, 19 glove, and 13 arm channels
at 512 Hz.

That is a decisive pre-acquisition question. If the representation is absent,
downloading the 13.75 GB cohort would waste storage and the frozen nuisance-
controlled experiment would not be executable. This packet asks to inspect
only one complete header, not the 105,365,484-byte member or its EEG samples.
It grants no authority now.

## Immutable Proof Anchors

Generated header successor `ca5d1db35a34762905d4df823766a6d353516c66`
passed Base Python `99151605412`, Optional Neuro Readers `99151605230`, and CI
`33271860805` on GitHub `main`.

Proof-only closeout `6815338609176b0f1599cbb2e11b4ce3acc8bad9`
passed Base Python `99152912864`, Optional Neuro Readers `99152912757`, and CI
`33272310252` on GitHub `main`. The closeout repeated no qualification and
performed no network or real-data operation.

The machine request binds 12 exact source, contract, implementation, result,
and proof artifacts totaling 86,180 bytes.

## Exact Public Member

Only this object is proposed:

- NEMAR dataset `nm000173`, immutable revision `v1.0.3`;
- participant 1, motor-imagery run 1;
- path `sourcedata/motorimagination_subject1_run1.gdf`;
- stable URL
  `https://data.nemar.org/nm000173/v1.0.3/sourcedata/motorimagination_subject1_run1.gdf`;
- declared payload size `105,365,484` bytes; and
- manifest-declared full-payload SHA-256
  `ec334466272a936986a50c120c52c57634801f028acb0fee30705f8a2dee3087`.

The full-payload hash cannot be recomputed from a header-only read and must
never be described as verified by this checkpoint. Every other file,
participant, run, dataset, sidecar, derivative, alternate host, redirect, and
substitute remains closed.

## Requested HL1 Engineering

Only after a fresh packet-bound decision is committed, pushed, and both CI
jobs are green, Tier B may add one standard-library live wrapper around the
already proven parser. It must first pass generated fixtures and injected mock
responses, then be committed, pushed, and remotely green before any activation
can expose a real request.

The wrapper must:

1. expose no usable real command before an exact activation record is green;
2. verify the decision, implementation, and activation commits plus both CI
   jobs from fresh GitHub metadata;
3. create and sync one durable no-clobber consumed marker before constructing
   a real opener or request;
4. use verified TLS, `Accept-Encoding: identity`, no credential, cookie,
   proxy override, redirect, retry, fallback, or substitution;
5. refresh the exact NEMAR manifest once in memory, remove only each row's
   volatile `url`, and require the frozen 748,162-byte canonical manifest at
   SHA-256 `5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34`;
6. require the selected row's exact path, size, SHA-256, and stable URL;
7. request `bytes=0-255` from that stable URL and accept only an uncompressed,
   nonmultipart `206` with exact `Content-Range` and `Content-Length`;
8. parse only the allowlisted fixed-header fields and require GDF 2.x, 96
   signals, and a complete declared header no larger than 65,536 bytes;
9. request bytes 256 through the declared header end from the same URL with
   the same transport checks;
10. assemble exactly one gapless header, reject trailing bytes, and use the
    proven parser without decoding patient, recording, date, event,
    annotation, or signal fields;
11. retain no manifest or GDF body and publish only one aggregate result plus
    resource and operation counters; and
12. clean up only invocation-created temporary files on failure.

Generated qualification is engineering evidence only. It may not contact
NEMAR, read a real path, or create scientific evidence.

## Requested HL2 One-Shot Checkpoint

Only after the exact HL1 implementation and an activation record are remotely
green may one irreversible invocation:

1. confirm at least 2 GiB free disk without scanning another project;
2. write and sync the unique consumed marker;
3. perform one bounded manifest GET;
4. perform the two exact GDF range GETs;
5. parse the assembled header once; and
6. emit one aggregate terminal result.

`OFNER-H1` requires exactly 24,832 header bytes, 96 unique normalized channel
labels partitioned as 61 EEG, three EOG, 19 glove, and 13 arm channels, 512 Hz
on every channel, and finite geometry with the nonzero EEG-geometry count
reported diagnostically.

`OFNER-H0-REPRESENTATION` means the validly transported and parsed header does
not satisfy that frozen representation. `OFNER-H0-TRANSPORT` means the
checkpoint refused before a valid complete header. Either terminal result
consumes this exact packet and permits no retry, rerun, repair, resume,
fallback, or substitution. A transport H0 has no biological interpretation.
An H1 permits only a future full-cohort acquisition preregistration; it does
not authorize acquisition, signals, targets, models, or scoring.

## Resource Envelope

| Resource | Frozen maximum or requirement |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 0 |
| Wall time | 120 seconds |
| Peak process-tree RSS | 256 MiB |
| Manifest GETs | 1 on success |
| GDF range GETs | 2 on success |
| Manifest body bytes | 2 MiB |
| Combined GDF body bytes | 65,536 |
| Total enforceable response-body bytes | 2,162,688 |
| Incremental disk peak | 4 MiB |
| Public output | 1 MiB |
| Required free disk | 2 GiB |
| Redirects / retries / reruns | 0 / 0 / 0 |

TLS and transport-header bytes unavailable to the standard library must be
reported as unavailable. No unavailable field may be silently imputed.

## Explicit Exclusions

This request authorizes no implementation, generated qualification,
activation, network request, real path, GDF byte, or header read now. Its
proposed ceiling also excludes:

- the other 149 selected GDFs, any sidecar, derivative, alternate participant,
  run, file, dataset, host, redirect, retry, fallback, or substitution;
- a whole-file request, full-payload SHA pass, resume, cache, split, epoch,
  window, feature, derivative, checkpoint, or model input;
- patient, recording, date, event-table, annotation, signal-sample, trial,
  task, target, label, quality, reference, or individual-outcome access or
  publication beyond the frozen aggregate channel-role contract;
- model or checkpoint access, training, inference, calibration, selection,
  prediction, target delivery, or scoring;
- any consumed BNCI, Dreyer, S20, S21, S24, S25, SpanishBCBL, or other private
  payload or artifact;
- language models or providers, RW3, streams, devices, hardware, upload,
  release, publication, cleanup, deletion, or another project; and
- any scientific, neural, decoding, unseen-person, movement-intention,
  motor-cortex, eye-independent, language, live, portable, home-use,
  assistive, or clinical claim upgrade.

## Decision Boundary

Every authority flag in the machine request is false. This request and a
separate proof-only closeout must first be committed, pushed, and remotely
green. Only afterward may `OFNER-C6R-1-HL` be identified as the sole active
Tier C packet for fresh maintainer words. Earlier instructions are not
retroactive.

Engineering capability requested: add a proof-bound range-only live wrapper
and use it once to verify one real Ofner source header before spending 13.75 GB
on the cohort.

Scientific claim not established: this all-false request performs no real-data
operation and establishes no EEG effect, neural advantage, unseen-person
generalization, EEG beyond nuisance sensors, movement intention, language,
live, portable, or clinical result.
