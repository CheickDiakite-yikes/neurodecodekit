# IACKD-M1A Public Snapshot Identity Audit Authorization Packet

Date: 2026-08-11

Status: **Exact packet-bound Tier C decision requested; not granted**

Lane: **IACKD-M1A Public Snapshot Identity Audit**

Green registration:
`1667e302e262ad23695f204a88d5a0997ac38270`

Green generated canonicalizer:
`7b8f47ba4b192953f4f60126521ba1839b828c85`

Green implementation CI: `31483435801` (Base Python `93753325035`;
Optional Neuro Readers `93753324999`)

Machine request:
`registries/iackd_snapshot_identity_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for a tightly ordered metadata-only sequence. After
a separate decision is remotely green, Codex may build and qualify one small
standard-library public transport wrapper using generated bodies and mocked
responses. Only after that exact wrapper is committed, pushed, and both CI jobs
are green may one fresh invocation send the registered 355-byte GraphQL POST
to OpenNeuro and read one response capped at 2 MiB.

The response may contain only the frozen snapshot ID, tag, `hexsha`, five
description fields, and the recursive file metadata rows named by the query.
The wrapper may validate HTTP status, final URL, redirects, content encoding,
body cap, one-read discipline, raw-response SHA provenance, and then hand the
same in-memory bytes to the green canonicalizer. It may emit one bounded
private selected manifest and one aggregate public report.

No EEG payload object may be requested. No local or retained IACKD bundle may
be touched. No VHDR, VMRK, EEG, EOG, event, trajectory, target, derivative,
model, prediction, score, or scientific claim is in scope.

This packet authorizes nothing by itself.

## Why A Fresh Decision Is Required

The generated canonicalizer was Tier B work. A dataset-specific OpenNeuro
GraphQL response, even metadata-only and public, is Tier C real-data access.
The current maintainer `continue` arrived before this immutable request and
cannot authorize it retroactively.

After this request is committed, pushed, and both CI jobs are green, Codex may
identify its exact commit, CI run, one-response scope, and decision boundary.
If it is the sole active Tier C packet, a fresh unambiguous `continue`,
`approve`, or `proceed` may bind it by reference. A separate decision artifact
must quote the maintainer's actual words and bind the request by SHA-256. Codex
must not fabricate a long authorization sentence as a user utterance.

## Immutable Proof

Research `723c8e244ff5f414cb4859bd122d42cccfaa795f` passed Base Python job
`93744221145` and Optional Neuro Readers job `93744221059` in CI
`31480538821`.

Registration `1667e302e262ad23695f204a88d5a0997ac38270` passed Base Python
job `93746523491` and Optional Neuro Readers job `93746523322` in CI
`31481270697`.

Exact generated implementation
`7b8f47ba4b192953f4f60126521ba1839b828c85` passed Base Python job
`93753325035` and Optional Neuro Readers job `93753324999` in CI
`31483435801`. Its implementation registry SHA-256 is
`05590a904ad8ee26d397726e1133877b0ec46218e8fc7ee37e7a26526c4b08a2`.

The final generated qualification reconciled 1,679 tree rows, all 1,340
historical selected paths, 15 participants, 30 participant-hand units, 128
runs, and twelve role summaries. It passed two deterministic replays and all
37 refusals in 0.8887734590098262 seconds at 38,436,864-byte peak RSS with
531,067 input bytes and 426,792 output bytes. Forty-nine focused, 2,084 base,
and 2,155 optional tests passed. Network, public response, local IACKD, neural,
target, model, prediction, score, retry, rerun, and claim counters were zero.

The consumed IACKD-2 and IACKD-2R executors, private roots, and markers are not
part of this lane and remain forbidden. This packet neither repairs nor reuses
either consumed attempt.

## Requested Ordered Sequence

Only after a separate decision commit is pushed and both CI jobs pass may the
following sequence begin:

1. Implement one additive standard-library transport wrapper around the green
   canonicalizer. It must use generated response bodies and mocked transport
   only; real endpoint access remains structurally closed.
2. Qualify status, URL, redirect, encoding, framing, one-read, body-cap,
   GraphQL-error, output, symlink, collision, resource, and consumed-root
   refusals without network or local IACKD access.
3. Commit and push that exact wrapper and require Base Python and Optional
   Neuro Readers CI to pass. A failed or ungreen wrapper is ineligible.
4. Before consumption, require five one-thread environment values, at least
   2 GiB free disk, and normalized one-minute load no greater than `1.0` per
   logical CPU. Refuse before a marker if any machine value is unavailable or
   outside the gate.
5. Create one new isolated Git-ignored invocation root and one private consumed
   marker. Any failure after that marker consumes IACKD-M1A.
6. Send exactly one 355-byte POST to the exact registered endpoint with no
   credentials, redirect, retry, fallback, variable, or alternate query.
7. Read at most 2,097,153 bytes once, reject overflow, discard the raw body
   after in-memory canonicalization, and never publish response headers or raw
   bytes.
8. Apply the frozen semantic canonicalizer. Snapshot, tree, selected inventory,
   critical metadata, unsafe row, or resource drift parks the lane.
9. Emit one private selected manifest and one aggregate public report under a
   combined 1 MiB cap, record all warnings and unavailable fields, and stop.

There is no retry, rerun, resume, restart, second request, alternate endpoint,
query amendment, post-result update, payload acquisition, or follow-on EEG
step in this packet.

## Exact Public Request

- provider: OpenNeuro;
- endpoint: `https://openneuro.org/crn/graphql`;
- method: `POST`;
- accession: `ds006840`;
- snapshot: `1.0.0` / `ds006840:1.0.0`;
- query UTF-8 bytes: 316;
- query SHA-256:
  `246db737c72bcd001c60191b6f31bef24d5bfc9a40ca5fa61b8ba215b30e3db0`;
- canonical request bytes: 355;
- request SHA-256:
  `913b033e430cbbb28ae14850dd744a50bd0418ecb64206645f4367d32ddd8896`;
- requests: exactly one;
- retries, redirects, substitutions, fallbacks, and credentials: zero; and
- response body cap: 2,097,152 bytes plus one byte solely for overflow
  detection.

The query and serialization are byte-frozen in
`registries/iackd_snapshot_identity_contract.v0.json`. This packet does not
permit an alias, variable, fragment, directive, introspection field, mutation,
or second request.

## Validation And Output Boundary

The wrapper must require HTTP 200, exact final URL, zero redirects, identity
content encoding, and one bounded body read. Fixed-length, valid chunked, and
clean close-delimited framing may be recorded. `Content-Length` is transport
evidence, not scientific identity. The raw response SHA-256 is provenance, not
an acceptance substitute for the canonical snapshot/tree/selection/critical
gates.

The private manifest may include exact selected filenames, Git object IDs,
sizes, annexed flags, S3 keys, version IDs, and roles. It must remain in the
new Git-ignored invocation root. The public report may include only aggregate
counts, role summaries, canonical hashes, measurements, counters, warnings,
unavailable fields, and the claim boundary. It must not contain an individual
filename, path, URL, version ID, row, participant outcome, neural value, target,
prediction, or secret.

## Resource Caps

| Stage | Wall time | Peak RSS | Network | Generated output |
| --- | ---: | ---: | ---: | ---: |
| Generated/mock wrapper qualification | 30 s | 268,435,456 bytes | 0 | 1,048,576 bytes |
| One public metadata invocation | 30 s | 268,435,456 bytes | 2,097,507 bytes | 1,048,576 bytes |

The public network cap consists of the 355-byte request and a 2,097,152-byte
response. One overflow-detection byte may be read but never accepted or
retained. Both stages use one CPU thread, one worker, and one numerical job.
At least 2,147,483,648 free bytes are required before the consumed marker.

## Explicitly Not Authorized

- any action before a separate packet-bound decision is remotely green;
- any public request before the exact additive wrapper is remotely green;
- any second GraphQL request, retry, rerun, redirect, fallback, alternate
  endpoint, query, variable, credential, API key, or provider;
- any S3 object request, payload byte, download, acquisition, cache, or split;
- any operation on a consumed IACKD-2/IACKD-2R root, bundle, marker, executor,
  result, or changed metadata body;
- any local IACKD path operation or another project operation;
- any VHDR, VMRK, EEG, EOG, channel, geometry, event, signal, trajectory,
  target, label, response, key, sentence, or trial read;
- any derivative, feature, model, checkpoint, training, inference, prediction,
  freeze, target delivery, score, threshold, seed, architecture, or selection;
- any dependency installation, language or foundation model, RW3, stream,
  device, hardware, upload, publication, release, or destructive action;
- any raw response body/header publication or individual private-manifest row;
  and
- any scientific, decoding, brain-specific, real-time, portable, home-use,
  assistive, or clinical claim upgrade.

## Current State

Every wrapper, public-data, local-data, payload, neural, target, model, scoring,
release, and claim authorization flag in the machine request is false.
Preparing this packet made zero network requests, public or local body reads,
signal/event/trajectory/target reads, model runs, predictions, scores, retries,
reruns, releases, or claim changes.

Engineering capability requested: one small, machine-gated transport wrapper
can test the current public snapshot identity once without conflating HTTP body
bytes with the snapshot, tree, selected-manifest, or critical-metadata layers.

Scientific claim not established by this request: this all-false packet is not
EEG data or a result and establishes no neural effect or decoding capability.
