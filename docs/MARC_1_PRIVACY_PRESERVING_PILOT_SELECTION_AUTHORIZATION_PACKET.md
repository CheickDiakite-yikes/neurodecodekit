# MARC1-P1A Real Metadata Pilot Selection Authorization Packet

Date: 2026-08-12

Status: **exact packet-bound Tier C decision requested; not granted**

Lane: **MARC1-P1A Real Metadata Pilot Selection**

Green generated result:
`fd246294db3defecdc11460e41945f64794b21cf`

Green result CI: `31572950727` (Base Python `94038664052`; Optional Neuro
Readers `94038664104`)

Machine request:
`registries/marc1_privacy_preserving_pilot_selection_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission to turn the frozen generated selector into one
strict real-metadata selector and, only after that exact implementation is
remotely green, run it once.

The future invocation may verify and read exactly one already sealed
418,755-byte Freewill central-directory manifest and accept exactly one
bounded public Figshare v3 Wrist metadata body. It may then choose only the 12
participants per axis already fixed by DOI-bound hashes and write one private
selection manifest plus one aggregate report. It may not open a ZIP local
header, member, participant archive, signal, event, target, or model.

This packet authorizes nothing by itself.

## Why A Fresh Decision Is Required

`MARC1PSG-R1` is remotely green generated engineering evidence. It used no
real manifest row and made no public request. Opening the retained private
inventory and requesting a current dataset-specific metadata body are Tier C
operations even though neither contains signal samples.

The maintainer's current `continue` preceded this immutable request and cannot
authorize it retroactively. After this exact request is committed, pushed,
and both CI jobs are green, Codex may identify its commit, CI run, two-input
scope, and decision boundary. If it is the sole active Tier C packet, a fresh
unambiguous `continue`, `approve`, or `proceed` may bind it by reference. A
separate decision artifact must quote the maintainer's actual words and bind
the request SHA-256. Codex must not fabricate a longer authorization sentence
as a user utterance.

## Immutable Proof

Pilot-selection contract `d1218066e64dea502d263acf0c096ed7eab55a11`
passed Base Python job `94028013357` and Optional Neuro Readers job
`94028013230` in CI `31569417204`.

Exact generated implementation
`0c0a6982c6b9c65d6c51413d1baa8b577e00a194` passed Base Python job
`94034790262` and Optional Neuro Readers job `94034790315` in CI
`31571668853` before the one registered closeout.

Consumed generated result `fd246294db3defecdc11460e41945f64794b21cf`
passed Base Python job `94038664052` and Optional Neuro Readers job
`94038664104` in CI `31572950727`. `MARC1PSG-R1` processed 873,348 generated
input bytes, selected 12 participants per axis, bound 72 Freewill run bundles,
288 Freewill members, and 12 Wrist archives, and passed all 36 refusals and 15
gates in 0.22733404207974672 seconds at 32,374,784-byte reported peak RSS.
Every real, neural, model, score, and claim counter was zero.

The retained Freewill inventory is bound only through the green aggregate
`MARC1CD-R1` result. The future expected private identity is exactly 418,755
bytes, mode `0600`, and SHA-256
`2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031`.
Preparing this packet did not stat, open, hash, or parse that private file.

## Requested Ordered Sequence

Only after a separate decision commit is pushed and both CI jobs pass may the
following sequence begin:

1. Implement one additive standard-library real-metadata wrapper. All input
   tests before its green commit must use generated private manifests, mocked
   HTTP responses, injected name resolution, and fresh temporary paths.
2. Freeze the exact Wrist participant-name parser, metadata schema, transport
   policy, private no-follow reader, source hashes, selection hashes, public
   firewall, output writer, machine gate, consumed marker, and router before
   any real path or public request is available.
3. Qualify malformed JSON, alias-resistant privacy, symlink and mode refusal,
   wrong source hash, duplicate or missing rows, ambiguous participant names,
   altered cohort/split, cap overflow, overwrite, redirect, body overflow,
   target-leakage vocabulary, and consumed-failure behavior with generated or
   mocked bytes only.
4. Commit and push that exact wrapper and require Base Python and Optional
   Neuro Readers CI to pass. A changed, failed, or ungreen implementation is
   ineligible.
5. Before consumption, require all exact green hashes, one-thread environment
   values, at least 12 GiB free disk, and normalized one-minute load no greater
   than `1.0` per logical CPU. Refuse before a marker if any value is missing
   or outside the gate.
6. Create one new isolated Git-ignored invocation root and one new consumed
   marker. Any later failure consumes MARC1-P1A.
7. Validate the named retained manifest with no-follow path checks, require a
   regular mode-`0600` file of exactly 418,755 bytes, then make exactly one
   content open, one bounded strict read, one SHA-256 pass, and one JSON parse.
8. Send one unauthenticated `GET` to the exact Figshare v3 files endpoint.
   Permit at most two bodyless HTTPS redirects to globally routable hosts and
   accept exactly one terminal `200` JSON body using a cap-plus-one read of no
   more than 2 MiB.
9. Validate exactly 55 file rows, 45 unique participant archives, ten
   supplementary rows, the 3,683,416,050-byte record total, and the exact
   participant-name rule frozen in the green wrapper. Any mismatch parks; no
   substitution, fallback parser, or post-response amendment is allowed.
10. Run only the frozen target-free selector. Require the exact preregistered
    participant ranks, sessions, runs, member suffixes, split identities, and
    source and joint byte caps.
11. Write one mode-`0600` Git-ignored private selection manifest and one
    aggregate public report, discard the public response body from memory, and
    stop.

There is no retry, rerun, resume, restart, second manifest open, second
metadata body, alternate record/version/provider, participant substitution,
payload acquisition, local-header request, member/archive open, model, or
score in this packet.

## Exact Input Identities

### Freewill private inventory

```text
relative path: .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
bytes:         418,755 exact
mode:          0600 exact
SHA-256:       2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
source DOI:    10.6084/m9.figshare.28632599.v1
rows:          1,227
regular files: 1,025
directories:   202
content opens: 1
payload opens: 0
```

### Wrist public metadata

```text
provider:          Figshare
record/version:    29666735 / 3
DOI:               10.6084/m9.figshare.29666735.v3
license:           CC BY 4.0
metadata endpoint: https://api.figshare.com/v2/articles/29666735/versions/3/files
accepted bodies:   1
body cap:          2,097,152 bytes
expected rows:     55
participant rows:  45
supplementary:     10
record bytes:      3,683,416,050
payload requests:  0
```

Raw metadata-body SHA-256 and transport headers are provenance, not frozen
source identity. Content is accepted only after bounded transport and exact
semantic validation. The green implementation's participant-name rule is
immutable before this endpoint can be called; if the current body differs,
the sole run parks without interpretation or amendment.

## Frozen Selection And Privacy Boundary

The participant IDs are already public because they were preregistered. The
real selector may not alter either rank:

```text
Freewill: sub-08 sub-10 sub-07 sub-22 sub-19 sub-16
          sub-14 sub-04 sub-05 sub-03 sub-09 sub-11

Wrist:    sub-08 sub-11 sub-09 sub-23 sub-20 sub-16
          sub-42 sub-38 sub-36 sub-30 sub-45 sub-21
```

Freewill must select the first three complete numeric run bundles from
`ses-01` as fit and `ses-02` as held out: 72 bundles and 288 core members.
Wrist must select exactly one archive per frozen participant and bind runs 1-6
as future fit and 7-8 as future held out. Size and checksums may enforce caps
after selection but may not influence participant, session, run, or split.

Exact member names, archive names, file IDs, offsets, CRCs, sizes, checksums,
and download URLs remain private. The public report may contain the
preregistered participant IDs, aggregate counts and byte totals, split totals,
domain-separated hashes, resource measurements, counters, warnings,
unavailable fields, route, and claim boundary only.

The public report must contain no non-preregistered participant identity,
member/archive name, file ID, offset, checksum, URL, response header, local
path, raw manifest row, raw response body, event, target, signal value,
prediction, or secret.

## Resource Caps

| Stage | Wall time | Peak RSS | Input/body bytes | Generated output |
| --- | ---: | ---: | ---: | ---: |
| Generated/mock wrapper qualification | 30 s | 268,435,456 | generated only | 2,097,152 |
| One real metadata selection | 30 s | 268,435,456 | 418,755 local + 2,097,152 network | 2,097,152 |

Both stages use one CPU thread, one worker, and one numerical job. The real
stage permits one private content open, one accepted network body, at most
three HTTP attempts including two bodyless redirects, 4 MiB incremental disk,
and one new Git-ignored invocation root. At least 12 GiB free disk is required
before the consumed marker. An overflow-detection byte may be read but never
accepted or retained. Retries and reruns are zero.

The selected future payload reservation must remain at or below 6 GiB for
Freewill, 2 GiB for Wrist, and 8 GiB jointly. Passing this metadata gate does
not authorize moving any of those payload bytes.

## Explicitly Not Authorized

- any action before a separate packet-bound decision is remotely green;
- any real path or public request before the exact additive wrapper is
  remotely green;
- opening, statting, hashing, parsing, moving, renaming, deleting, or changing
  any other private file, consumed root, cache, dataset, project, or sidecar;
- a second manifest open, metadata body, redirect beyond the cap, retry,
  rerun, resume, restart, fallback parser, substitution, or amendment;
- a ZIP local header, member payload, participant archive, extraction,
  decompression, CRC verification, whole-file MD5 pass, or payload download;
- any signal, channel, geometry, EOG, EMG, acceleration, encoder, audio, event,
  onset, target, label, trial, response, sentence, key, or quality read;
- any cache, epoch, window, feature, derivative array, training, inference,
  prediction, freeze, target delivery, score, threshold, model, seed,
  architecture, or hyperparameter operation;
- any dependency installation, language or foundation model, provider call,
  RW3, stream, device, hardware, upload, publication, release, or destructive
  action; and
- any scientific, decoding, brain-specific, language, thought-to-text,
  real-time, portable, home-use, assistive, or clinical claim upgrade.

## Current State

Every implementation, private-read, public-request, payload, neural, target,
model, score, release, cleanup, and claim authorization flag in the machine
request is false. Preparing this packet made zero private-path operations,
public requests, DNS queries, body reads, payload reads, signal/event/target
reads, model runs, predictions, scores, retries, reruns, deletions, or claim
changes.

Twelve request invariants plus 38 hash/scope subtests pass. All 286 MARC tests
plus 208 subtests pass. The dependency-light suite passes 2,425 tests with 204
expected skips in 19.516 seconds at 214,335,488-byte external maximum RSS;
the locally comparable optional-neuro suite passes 2,496 tests with 35
expected skips in 56.867 seconds at 720,027,648-byte external maximum RSS.
Each complete suite adds exactly 12 tests and zero skips over the remotely
green generated-result baseline.

This packet stays on the same research path. It reduces selection and
attribution risk before the future language-specific thought-to-text test; it
does not replace that test with movement decoding.

Engineering capability requested: one proof-gated standard-library wrapper
can bind the exact real two-axis pilot from 418,755 local metadata bytes and no
more than 2,097,152 public metadata bytes without opening a neural payload.

Scientific claim not established by this request: this all-false packet is
not a neural experiment and establishes no neural effect, movement decoding,
source attribution, language decoding, or thought-to-text capability.
