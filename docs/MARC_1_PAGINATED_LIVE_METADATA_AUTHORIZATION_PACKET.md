# MARC-1 Paginated Live Metadata Authorization Packet

Date: 2026-08-12

Lane: `MARC1-LM1`

Status: **Exact packet-bound Tier C decision requested; not granted**

Machine request:
`registries/marc1_paginated_live_metadata_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for one additive, standard-library live-metadata
wrapper and, only after that exact wrapper is committed, pushed, and both CI
jobs are green, one no-retry request for the complete version-3 Wrist file
inventory:

```text
GET https://api.figshare.com/v2/articles/29666735/versions/3/files?page=1&page_size=1000
```

The future execution may read and hash one response body capped at 2 MiB,
strictly validate the frozen 55-row public inventory, apply the already frozen
target-free Wrist cohort rule, and retain one small private metadata manifest
plus one aggregate report. It may not request or open any participant archive,
signal, event, target, model, prediction, or score.

This packet authorizes nothing by itself.

## Same Path, Not A Pivot

`MARC1-LM1` is one checkpoint on the existing research path:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> stronger non-invasive thought-to-text evidence
```

The metadata inventory is needed so a later experiment can select the exact
same participants and held-out runs without learning from outcomes. This does
not replace language decoding with movement decoding, and it does not create a
scientific result.

## Why This Gate Exists

The earlier live wrapper reached the Figshare source but omitted explicit
pagination. It accepted and parsed one 2,917-byte body, then consumed at
`MARC1HTL-F04` because the row count differed from the frozen 55-row identity.
The actual count and rows were not retained, and that lane has no retry.

Official-interface research then identified the version-files pagination rule.
The generated `MARC1-PG1` stack proved byte-for-byte
`page=1&page_size=1000` semantics and exact 55-row validation, but its sole
registered closeout correctly refused a symlink output parent. `MARC1-OP1`
then repaired the operation order and output authority. Its one path preflight
reached `MARC1OP-P0`; its one conditional generated qualifier reached
`MARC1OP-G1`; and exact result `ca4679a95e3567a5d47094cc4282a63fa6986959`
passed CI `31601329375` before this packet was prepared.

The remaining question is narrow and real: does the immutable public version-3
inventory satisfy the frozen complete-page identity when the canonical query
is actually sent?

## Fresh Decision Rule

The maintainer's current and prior messages preceded this immutable request and
cannot authorize it retroactively. After this exact request is committed,
pushed, and both CI jobs are green, Codex may identify its commit, CI run,
scope, and boundary. If it is the sole active Tier C packet, a fresh
unambiguous `continue`, `approve`, or `proceed` may bind it by reference.

The separate decision record must quote the maintainer's actual words and bind
the request commit, CI jobs, and request SHA-256. Codex must not fabricate a
long authorization sentence as a user utterance.

## Requested Ordered Sequence

Only after a separate authorization decision is committed, pushed, and both CI
jobs are green may the following sequence begin:

1. Implement a new additive standard-library module at
   `src/neurodecodekit/datasets/marc1_paginated_live_metadata.py`.
2. Qualify it only with generated inventories, mocked transport, injected
   failures, and temporary nonregistered output paths.
3. Prove capability-first output handling, exact request serialization,
   bounded transport, strict JSON/schema validation, target leakage refusal,
   deterministic private/public manifests, consumed-marker behavior, and all
   resource and privacy gates.
4. Commit and push that exact implementation and require both CI jobs to pass.
   A changed, failed, or ungreen implementation is ineligible for live access.
5. On the registered invocation, acquire and hold the output-parent capability
   before repository reads, contract loads, network setup, or response work.
6. Verify the exact decision, request, result, implementation, pagination, and
   output-capability hashes; the one-thread environment; at least 10 GiB free
   disk; and normalized one-minute load no greater than `1.0` per logical CPU.
7. Create one new isolated output at
   `/private/tmp/neurodecodekit-marc1lm1-live-metadata-20260812`, write one
   consumed marker, and make exactly one unauthenticated HTTPS `GET` with the
   exact path and query above.
8. Read at most 2 MiB plus one overflow-detection byte. Accept only one terminal
   `200` JSON response with the exact final URL, no redirect, no content coding,
   and standard bounded HTTP framing.
9. Parse with duplicate-key rejection, enforce the exact seven-field row
   schema, reject target-like fields, and require 55 rows, 45 participant ZIPs,
   ten supplementary rows, and 3,683,416,050 declared bytes.
10. Apply only the frozen 12-subject Wrist selection and runs 1-6 fit versus
    runs 7-8 held-out split. Size, checksum, quality, target, and outcome may
    not choose a participant or split.
11. Write one mode-`0600` private metadata manifest and one aggregate report
    through held descriptors, record hashes and measurements, and stop.

Any failure after the consumed marker parks the lane. There is no retry,
rerun, resume, second page, automatic pagination, alternate endpoint,
substitution, fallback parser, or post-response amendment.

## Exact Source Identity

```text
provider:          Figshare
record/version:    29666735 / 3
DOI:               10.6084/m9.figshare.29666735.v3
license:           CC BY 4.0
method:            GET
path:              /v2/articles/29666735/versions/3/files
query:             page=1&page_size=1000
full URL:           https://api.figshare.com/v2/articles/29666735/versions/3/files?page=1&page_size=1000
request attempts:  1
accepted bodies:   1
body cap:          2,097,152 bytes
payload requests:  0
payload bytes:     0
```

Expected immutable inventory identity:

```text
file rows:             55
participant archives: 45
supplementary rows:    10
declared record bytes: 3,683,416,050
selected participants: 12
fit runs:              1-6
held-out runs:         7-8
fit/held-out overlap:  0
```

If any identity differs, the one attempt must park. The implementation may not
change the expectation, fetch another page, truncate the cohort, or choose a
replacement row.

## Transport Contract

The future wrapper must disable automatic redirects and content decoding. It
must refuse credentials, cookies, request bodies, proxy substitution,
alternate hosts, and non-HTTPS URLs.

`Content-Encoding` may be absent or one case-insensitive `identity` token. All
other codings, lists, duplicates, decoding, and decompression are forbidden.

Response framing may be either:

- one absent or single canonical decimal `Content-Length`, with a bounded
  cap-plus-one read and an exact count match when length is present; or
- one exact case-insensitive `chunked` transfer-coding with no
  `Content-Length`, relying only on standard-library transport deframing plus
  the same cap-plus-one accepted-byte bound.

Any duplicate or conflicting framing header, transfer-coding list or
extension, malformed length, overflow, early close under a declared length,
non-JSON content type, non-200 status, redirect, or final-URL drift parks the
lane. Raw headers and the raw body may not be published or retained after the
private canonical manifest is written.

## Output And Privacy Boundary

The exact future directory may contain only:

```text
execution_consumed.v0.json
marc1_paginated_live_metadata.private.v0.json
marc1_paginated_live_metadata_result.v0.json
```

The marker and private manifest use mode `0600`. The private manifest may
retain only the validated public source fields needed to bind later payload
identity: file ID, filename, declared size, supplied/computed MD5, link-only
flag, and download URL. It may also retain the frozen cohort/split assignment
and domain-separated hashes. It is Git-ignored and must never be committed.

The aggregate report may contain only source identity, counts, byte totals,
domain-separated hashes, selected-count and split summaries, transport class,
resource measurements, counters, warnings, unavailable fields, route, and
claim boundary. It may not contain an individual file ID, filename, URL,
checksum, non-preregistered participant identity, raw row, raw header, raw
body, local path, signal, event, target, prediction, or secret.

No preexisting path may be overwritten, moved, renamed, deleted, or cleaned.
Generated qualification may remove only its own temporary files. The one real
invocation retains its marker and outputs for a later separately authorized
payload decision.

## Resource Caps

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
generated qualification wall time:      30 seconds
real invocation wall time:               30 seconds
peak RSS:                                268,435,456 bytes
network request attempts:                1
accepted network body:                   2,097,152 bytes maximum
aggregate report:                        1,048,576 bytes maximum
combined generated/live output:          2,097,152 bytes maximum
incremental disk:                        4,194,304 bytes maximum
minimum free disk before consumption:    10,737,418,240 bytes
retries / reruns:                        0 / 0
```

The packet adds no dependency and changes no base-install requirement.

## Explicitly Not Authorized

- any implementation or operation before a separate packet-bound decision is
  remotely green;
- any live request before the exact additive implementation is remotely green;
- importing, calling, modifying, or rerunning the consumed live or generated
  executors;
- opening, statting, hashing, parsing, moving, renaming, deleting, or changing
  an old invocation root, retained bundle, cache, dataset, sidecar, or another
  project;
- a second request, page, response body, redirect, retry, rerun, resume,
  restart, fallback, substitution, expectation change, or parser amendment;
- a participant archive, ZIP header, member, payload, download, extraction,
  decompression, CRC pass, whole-file checksum pass, or signal read;
- a channel, geometry, EOG, EMG, acceleration, encoder, audio, event, onset,
  trial, response, target, label, sentence, key, or quality read;
- a cache, epoch, window, feature, derivative, training run, inference run,
  prediction set, freeze, target delivery, score, threshold, model, seed,
  architecture, or hyperparameter operation;
- a dependency install, language or foundation model, provider call, RW3,
  stream, device, hardware, upload, publication, release, or destructive
  action; and
- any scientific, neural, decoding, language, thought-to-text, real-time,
  portable, home-use, assistive, clinical, or product claim upgrade.

## Current State

Every implementation, network, source, output, payload, neural, target, model,
score, cleanup, release, and claim authorization flag in the machine request is
false. Preparing this packet made zero DNS queries, network requests, body
reads, private-path operations, output writes, payload reads, signal reads,
target reads, model runs, predictions, scores, retries, reruns, deletions, or
claim changes.

Local verification passed:

```text
focused request tests:                 13 / 13
all MARC tests:                       612 / 612
MARC runtime / external peak RSS:     6.460 sec / 67,076,096 bytes
dependency-light suite:               2,751 passed / 204 skipped
dependency-light runtime / peak RSS:  22.595 sec / 256,131,072 bytes
optional-neuro suite:                 2,822 passed / 35 skipped
optional-neuro runtime / peak RSS:    61.051 sec / 813,072,384 bytes
```

Times and RSS above are the maxima observed across the two complete local
passes. The packet adds thirteen tests and zero skips. Repository-wide Ruff, source
and test compilation, all 193 registry JSON parses, artifact hash replay, and
`git diff --check` pass. Verification made no live, private, payload, neural,
target, model, score, or claim operation.

This packet must now be committed, pushed, and pass both remote CI jobs before
it can be identified as the sole active Tier C gate.

Engineering capability requested: one proof-gated standard-library wrapper can
bind the complete immutable Wrist metadata inventory through an exact
pagination request and preserve a small target-free manifest for later work.

Scientific claim not established by this request: this all-false packet reads
no neural signal and establishes no neural effect, decoding accuracy, language
decoding, or thought-to-text capability.
