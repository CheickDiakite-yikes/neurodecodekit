# MARC1-SA1A Source-Aware Live Metadata Authorization Packet

Date: 2026-08-12

Lane: `MARC1-SA1A`

Status: **Exact packet-bound Tier C decision requested; not granted**

Machine request:
`registries/marc1_source_aware_live_metadata_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for one additive, standard-library source-aware
live-metadata wrapper and, only after that exact wrapper is committed, pushed,
and both CI jobs are green, one no-retry request:

```text
GET https://api.figshare.com/v2/articles/29666735/versions/3/files?page=1&page_size=1000
```

The future wrapper may read at most one 2-MiB metadata body, apply the already
green five-field-core and optional-MD5 attestor, retain one private canonical
metadata manifest, and publish one aggregate route report. It may select the
frozen 12-subject cohort only if every historical inventory predicate matches.
Any historical drift or unknown extension blocks selection while preserving a
target-free aggregate diagnosis.

This packet authorizes nothing by itself.

## Same Path, Not A Pivot

`MARC1-SA1A` remains one integrity gate on the existing path:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

The purpose is to stop losing one-shot metadata attempts to an opaque all-or-
nothing schema check. This does not replace neural evidence with metadata,
movement with language, or engineering readiness with a scientific result.

## Why This Gate Is Now Eligible

The consumed `MARC1-LM1` wrapper accepted and strictly parsed one 15,652-byte
version-3 metadata body, then parked at `MARC1LM-F04` because its frozen
validator required exact seven-field set equality. It retained no actual row
count, changed field, inventory identity, or cohort and has no retry.

`MARC1-SA1` then separated the official five-field public core from optional
MD5 provenance, target-free cohort identity, and later acquired-byte SHA-256.
Its generated attestor evaluates 21 aggregate predicates and seven separated
identity domains. Exact implementation `feb3b83` passed CI `31619037335`
before one registered generated closeout. Consumed result `094b6cb` then passed
Base Python job `94193898391` and Optional Neuro Readers job `94193898482` in
CI `31620515340`.

That generated result is the eligibility proof for this packet. It is not
permission to contact Figshare.

## Fresh Decision Rule

The maintainer's current and prior messages preceded this immutable request
and cannot authorize it retroactively. After this exact request is committed,
pushed, and both CI jobs are green, Codex may identify its commit, CI run,
scope, and boundary. If it is the sole active Tier C packet, a fresh
unambiguous `continue`, `approve`, or `proceed` may bind it by reference.

The separate decision record must quote the maintainer's actual words and bind
the request commit, both CI jobs, and request SHA-256. Codex must not fabricate
a long authorization sentence as a user utterance.

## Requested Ordered Sequence

Only after a separate authorization decision is committed, pushed, and both
CI jobs are green may this sequence begin:

1. Implement a new additive module at
   `src/neurodecodekit/datasets/marc1_source_aware_live_metadata.py`.
2. Import only the green source-aware attestor; do not import, call, modify,
   probe, or expose any consumed live executor or root.
3. Qualify the wrapper only with generated inventories, mocked transport,
   injected failures, and temporary nonregistered paths.
4. Prove authorization/hash checks, capability-first output, exact request
   serialization, bounded HTTP framing, strict JSON, target rejection, all
   source-aware routes, private/public separation, consumed-marker behavior,
   deterministic replay, and resource caps.
5. Commit and push that exact wrapper and require both CI jobs green. Any
   changed, failed, or ungreen wrapper is ineligible for source access.
6. On the sole registered invocation, acquire the output-parent capability
   before repository reads, source setup, or network work.
7. Verify the exact decision, request, green result, contract, implementation,
   and wrapper hashes; one-thread environment; at least 10 GiB free disk; and
   normalized one-minute load no greater than `1.0` per logical CPU.
8. Create one new isolated root at
   `.codex_work/marc1_source_aware_inventory/live_metadata_v0`, write one
   mode-`0600` consumed marker, and make exactly one unauthenticated HTTPS GET.
9. Read at most 2 MiB plus one overflow byte. Accept only one terminal `200`
   JSON response with the exact final URL, no redirect, no content decoding,
   and one registered standard HTTP framing form.
10. Parse with duplicate-key and nonfinite-value rejection, apply the target
    firewall, and pass the body once to the exact green source-aware attestor.
11. Retain one mode-`0600` canonical private manifest containing validated
    public-core rows, optional MD5 values when present, unknown-key hashes but
    no unknown values, route, predicates, and selection only when eligible.
12. Write one aggregate report, inspect it once, and stop before any archive
    or payload operation.

Any outcome consumes the lane. There is no retry, rerun, resume, second page,
redirect, alternate endpoint, fallback parser, expectation change, post-body
amendment, or payload continuation.

## Exact Source Identity

```text
provider:          Figshare
record/version:    29666735 / 3
DOI:               10.6084/m9.figshare.29666735.v3
license:           CC BY 4.0
method:            GET
path:              /v2/articles/29666735/versions/3/files
query:             page=1&page_size=1000
request attempts:  1
redirects:         0
accepted bodies:   1
body cap:          2,097,152 bytes
payload requests:  0
payload bytes:     0
```

The historical identity is a comparison target, not permission to coerce the
live body:

```text
file rows:             55
participant archives: 45
supplementary rows:    10
declared record bytes: 3,683,416,050
selected participants: 12 only on complete historical match
fit runs:              1-6 only on complete historical match
held-out runs:         7-8 only on complete historical match
fit/held-out overlap:  0
```

## Frozen Source-Aware Routes

| Attestor result | Wrapper route | Selection |
|---|---|---|
| `MARC1SA-R1` complete agreeing MD5 | `MARC1SAL-R1` | frozen cohort available |
| `MARC1SA-R2` unavailable or partial MD5 | `MARC1SAL-R1` | frozen cohort available; payload SHA-256 still required later |
| `MARC1SA-R3` historical differences | `MARC1SAL-R2` | blocked |
| `MARC1SA-R4` unknown non-target extension | `MARC1SAL-R2` | blocked |

Structural, target, transport, proof, output, privacy, or resource failures use
`MARC1SAL-F00` through `MARC1SAL-F04` and stop. The wrapper may not turn an
R3/R4 diagnosis into selection, weaken a predicate, drop a row, or change a
cohort after seeing the response.

## Transport Contract

The future wrapper must use standard-library HTTPS, disable automatic
redirects, and refuse credentials, cookies, request bodies, proxy
substitution, alternate hosts, query drift, and non-HTTPS URLs.

`Content-Encoding` may be absent or one case-insensitive `identity` token.
All other codings, lists, duplicates, decoding, and decompression are refused.

The response may be exact `Content-Length`, exact chunked transfer without
`Content-Length`, or a clean close-delimited body. Every form uses a cap-plus-
one accepted-byte read. Duplicate/conflicting framing, malformed length,
overflow, early close under a declared length, non-JSON content type, non-200
status, redirect, or final-URL drift consumes the failure route.

The raw response SHA-256 and observed byte count are provenance only. They do
not replace semantic identity or later SHA-256 over acquired payload bytes.

## Output And Privacy Boundary

The new root may contain only:

```text
execution_consumed.v0.json
marc1_source_aware_live_metadata.private.v0.json
marc1_source_aware_live_metadata_result.v0.json
```

The marker and private manifest use mode `0600`. The private manifest is
Git-ignored and may retain validated public fields needed for a later
separately authorized acquisition: ID, name, declared size, link-only state,
download URL, optional MD5, classification, semantic hashes, and frozen split
only when selection is eligible. Unknown extension values and raw bodies are
never persisted.

The aggregate report may publish only source identity, route, aggregate
counts, byte totals, booleans, historical-difference names, domain-separated
hashes, resource measurements, counters, warnings, unavailable fields, and
claim boundary. It may not publish an individual row, ID, filename, URL, MD5,
participant identity, raw header, raw body, local path, signal, target,
prediction, secret, or unknown-field value.

No preexisting path may be overwritten, moved, renamed, deleted, or cleaned.
Generated qualification may remove only its own temporary outputs. The one
live invocation retains its new marker and reports for a later separate gate.

## Resource Caps

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
generated qualification wall time:      30 seconds
real invocation wall time:               30 seconds
peak RSS:                                268,435,456 bytes
network request attempts:                1
accepted network body:                   2,097,152 bytes maximum
aggregate report:                        1,048,576 bytes maximum
combined output:                         2,097,152 bytes maximum
incremental disk:                        4,194,304 bytes maximum
minimum free disk before consumption:    10,737,418,240 bytes
retries / reruns:                        0 / 0
```

The packet adds no dependency and changes no base-install requirement.

## Explicitly Not Authorized

- implementation or operation before a separate packet-bound decision is
  remotely green;
- a live request before the exact additive wrapper is remotely green;
- any access to the consumed `MARC1-LM1` root or wrapper;
- a second request, page, response, redirect, retry, rerun, resume, restart,
  substitution, fallback, expectation change, or post-result update;
- a participant archive, ZIP header, member, payload, download, extraction,
  decompression, CRC pass, payload checksum, or neural signal read;
- a channel, geometry, EOG, EMG, event, onset, trial, response, target, label,
  sentence, key, quality, movement, audio, or trajectory read;
- cache, split changes, epoch, window, feature, derivative, model, training,
  inference, prediction, freeze, target delivery, scoring, threshold, seed,
  architecture, or hyperparameter work;
- dependency installation, language/foundation model, provider call, RW3,
  stream, device, hardware, upload, publication, release, destructive action,
  or another-project operation; and
- any scientific, neural, decoding, language, thought-to-text, real-time,
  portable, home-use, assistive, clinical, or product claim upgrade.

## Current State

Every current implementation, output, network, source, selection, payload,
neural, target, model, score, cleanup, release, and claim authorization flag
in the machine request is false. Packet preparation made zero DNS queries,
network requests, live body reads, private-path operations, output writes,
archive or payload reads, signal or target reads, model runs, scores, retries,
reruns, deletions, or claim changes.

This packet must be tested, committed, pushed, and pass both remote CI jobs
before it can be identified as the sole active Tier C gate.

Local verification passed:

```text
focused request tests:                    14 / 14
all MARC tests:                          747 / 747
MARC subtests:                           801 / 801
dependency-light suite:                2,922 passed / 35 skipped
dependency-light subtests:             1,614 passed
dependency-light runtime / peak RSS:    92.87 sec / 622,968,832 bytes
optional-neuro suite:                  2,910 passed / 47 skipped
optional-neuro subtests:               1,621 passed
optional-neuro runtime / peak RSS:       89.73 sec / 681,934,848 bytes
```

The packet adds exactly 14 tests and zero skips to both comparable complete
suites. Ruff, compilation, all 201 registry JSON parses, bound-artifact hash
replay, and `git diff --check` pass. Verification made no live, private,
payload, neural, target, model, score, or claim operation.

Engineering capability requested: one proof-gated source-aware wrapper can
turn a single bounded public metadata response into a privacy-preserving,
failure-localized cohort identity without weakening payload integrity.

Scientific claim not established by this request: this all-false packet reads
no neural signal and establishes no neural effect, decoding accuracy, language
decoding, or thought-to-text capability.
