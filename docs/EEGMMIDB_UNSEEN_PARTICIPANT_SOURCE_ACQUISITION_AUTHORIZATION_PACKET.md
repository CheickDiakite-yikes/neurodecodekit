# EEGMMIDB-UG1 Stage S-A Source Acquisition Authorization Packet

Date: 2026-08-24

Status: **All authority false; request only**

Machine request:

- `registries/eegmmidb_unseen_participant_source_acquisition_authorization_request.v0.json`

## Purpose

Stage M is consumed and remotely green. It established the exact public remote
identity of all 36 preregistered EDF paths without reading an EDF body. The next
scientifically useful dependency is smaller: obtain only the six missing
source-fit files for S001-S003 runs 04 and 08 so the already-frozen source LOSO
gate can eventually run before any fresh participant is touched.

This packet grants no authority. `S-A` is acquisition only; it is not the
broader Stage S source-LOSO, training, or checkpoint-freeze gate. It proposes a
future generated qualification and one source-only acquisition behind a fresh
packet-bound Tier C decision and two remote-green implementation barriers.

## Immutable Proof Anchor

Stage M2 proof closeout commit
`00f795f860762a6e828b210cee52808e69571d53` passed Base Python job
`97409224259`, Optional Neuro Readers job `97409224710`, and CI
`32720013549`. This request binds eleven exact Stage M, UG1 contract, and
existing generated-acquisition artifacts totaling 116,444 bytes. The machine
request freezes every size, SHA-256, Git blob, and the canonical artifact-set
hash `9e4c5ed1c4910f642fa6e91e1b0010e3eb6646e9c3661bb5be5c58917b4e3600`.
UG1 Amendment 1 is controlling wherever older packet language differs. File
identity may exist in acquisition provenance but may never enter a future
predictive feature, normalization, model, control transform, or threshold.

## Exact Source Boundary

Only these six public files are in scope:

| Path | Frozen bytes | Frozen ETag |
|---|---:|---|
| `S001/S001R04.edf` | 2,596,896 | `"4a82c43f-27a020"` |
| `S001/S001R08.edf` | 2,596,896 | `"4a82c444-27a020"` |
| `S002/S002R04.edf` | 2,555,616 | `"4a82c452-26fee0"` |
| `S002/S002R08.edf` | 2,555,616 | `"4a82c458-26fee0"` |
| `S003/S003R04.edf` | 2,596,896 | `"4a82c465-27a020"` |
| `S003/S003R08.edf` | 2,596,896 | `"4a82c46c-27a020"` |

The success total must be exactly 15,498,816 body and final payload bytes.
Every URL, participant, run, partition, size, ETag, Last-Modified value, and
Accept-Ranges value is copied from the immutable Stage M inventory. There is no
wildcard, sidecar, companion, alternate host, redirect, substitution, retry,
partial bundle, or participant expansion.

The 30 S016-S030 run-11/run-12 fresh-final files totaling 76,916,160 declared
bytes and the 54 already-retained S001-S015 source files are explicitly outside
this request. No request, path operation, local copy, open, hash, parse, or
acquisition may touch them.

These six EDF payloads contain embedded annotations and are therefore sealed,
target-bearing bytes even though they are public. Acquisition may store and
hash them opaquely, but it may not semantically read any portion of them.

## Requested Stage S-A1: Generated Qualification

Only after a future authorization decision is committed, pushed, and both CI
jobs are green, add an isolated source-acquisition module and sidecar CLI. The
proof-bound Stage G acquisition module, central CLI, contracts, amendments,
metadata implementation, and consumed results must remain byte-identical.

The new implementation must:

- expose dry `plan` and generated `qualify` commands only;
- have no public live-execution CLI command;
- use only the standard library in the base installation;
- accept exactly six generated sentinel payloads from an injected mock opener;
- freeze the real executor behind exact remote-green implementation evidence;
- validate direct status, URL, headers, body framing, byte caps, and order;
- stream in chunks no larger than 1 MiB without loading a complete EDF;
- hash during transfer and perform exactly one opaque no-follow local size and
  SHA-256 pass per completed file;
- publish only a complete six-file bundle through atomic no-replace rename;
- produce bounded canonical private-manifest and aggregate-receipt serializers;
- refuse aliases, symlinks, hardlinks, traversal, collisions, redirects,
  compression, partial or oversized bodies, header drift, target-like output,
  cap breaches, a second invocation, and any fresh-final path; and
- clean only invocation-created temporary files after a failure.

One registered generated qualification may run with mock responses only. It
must be recorded, committed, pushed, and remotely green, followed by a
proof-only closeout that is also remotely green, before Stage S-A2 exists.

## Requested Stage S-A2: One Source Acquisition

Only after those barriers, one no-retry invocation may first make one bounded
HTTPS `GET` of the exact versioned official `SHA256SUMS.txt`. It must strictly
parse exactly one checksum for each of the six allowlisted paths and freeze
those values before an EDF request. Missing, duplicate, malformed, or
conflicting entries consume and park the invocation.

The invocation may then make exactly six sequential EDF `GET` requests in the
frozen order. Each request must use
`Accept-Encoding: identity`, the frozen strong ETag as `If-Match`, and the
frozen modification time as `If-Unmodified-Since`. The response must be a
direct `200` from the exact URL, with no `Content-Range`, no content encoding,
and exact frozen `Content-Length`, ETag, Last-Modified, and Accept-Ranges
values before the body is consumed.

Each body remains opaque. The executor may write and integrity-check bytes, but
may not parse even an EDF header. Every observed file must match its official
manifest SHA-256 before promotion. The executor may create one new isolated
Git-ignored source bundle, one private machine manifest, one durable no-clobber
consumed marker, and one aggregate public receipt. The marker must be persisted
and synced immediately before the checksum request so a crash cannot silently
restore authority. Payloads and the private manifest must never be staged,
committed, uploaded, published, or moved into another project. A pass or
failure consumes Stage S-A2; there is no retry, rerun, repair, resume, fallback,
or substitution.

## Resource Envelope

| Resource | Frozen maximum or requirement |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time per stage | 300 seconds |
| Peak process-tree RSS | 256 MiB |
| Checksum / payload requests | exactly 1 / 6 |
| Checksum-manifest body cap | 1 MiB |
| Successful payload body bytes | exactly 15,498,816 |
| Payload-network cap | 16 MiB |
| Incremental disk peak | 64 MiB |
| Generated/private/public metadata combined | 1 MiB |
| Stream chunk size | at most 1 MiB |
| Required free disk before execution | at least 2 GiB |
| Payload retries / reruns | 0 / 0 |

Transport header and TLS bytes unavailable to the standard library must be
reported unavailable. The enforceable network boundary is exact request count,
zero redirects/retries, direct response identity, and counted body bytes.

## Explicit Exclusions

This request does not authorize implementation, qualification, network access,
payload acquisition, or local real-data access now. Its proposed maximum also
excludes:

- any S016-S030 fresh-final file, any already-retained source EDF, or any
  additional file, run, participant, sidecar, dataset, download, or
  substitution;
- EDF header, annotation, event channel, sample, channel, geometry, montage,
  reference, sampling, task, target, label, epoch, trial, or quality reads;
- MNE or another EDF reader in the acquisition executor;
- split, cache, derivative, feature, checkpoint, model, inference, training,
  prediction, target delivery, selection, or scoring operations;
- S20, S21, S24, S25, SpanishBCBL, Freewill, IACKD, or another real payload;
- a language model or provider, RW3, stream, device, hardware, upload,
  publication, or release; and
- any scientific, neural, decoding, unseen-person, movement-intention,
  motor-cortex, eye-independent, language, live, portable, home-use, assistive,
  or clinical claim upgrade.

## Decision Boundary

Every authority flag in the machine request is false. After this request and a
separate proof-only closeout are remotely green, `EEGMMIDB-UG1-SA` may be named
as the sole active Tier C packet. The maintainer's next unambiguous
packet-bound `approve`, `continue`, or `proceed` may then authorize only this
exact two-stage maximum under the research-autonomy charter.

Engineering capability proposed: a six-file, source-only, opaque acquisition
gate that preserves the fresh-participant firewall and produces an immutable
integrity manifest without parsing EEG.

Scientific claim not established: this all-false request performs no network
or data operation and establishes no EEG effect, decoding advantage,
movement-intention signal, motor-cortex origin, eye independence, language
decoding, live performance, or unseen-person generalization.
