# MARC-1 Source-Aware Inventory Attestation Research

Date: 2026-08-12

Lane: `MARC1-SA1`

Status: **Tier A architecture research complete; no dataset-specific response,
private artifact, participant archive, payload, signal, target, model, or score
was accessed**

Registry:
`registries/marc1_source_aware_inventory_attestation_research.v0.json`

## Decision

Advance **MARC1-SA1: Source-Aware Inventory Attestation** as the next
prospective metadata lane on the existing thought-to-text research path.

The previous gate correctly failed closed but compressed every downstream
inventory mismatch into `MARC1LM-F04`. The next design must produce a
privacy-preserving predicate vector and separate three different contracts:

1. what the public source officially guarantees;
2. what target-free cohort selection requires; and
3. what later payload integrity must prove from acquired bytes.

This is not permission to request the MARC-1 endpoint again. Generated-only
preregistration and implementation must become remotely green first. Any
future public response remains a new Tier C event.

## Evidence Anchor

Consumed result commit `d8595098a1a31243e0b147779ed35656a313fd8b`
passed Base Python job `94168528552` and Optional Neuro Readers job
`94168528522` in CI `31612923903` before this research.

That result establishes only these live facts:

- one 15,652-byte version-specific metadata body passed bounded transport;
- strict JSON-list parsing completed once;
- the frozen inventory validator refused at `MARC1LM-F04`;
- no cohort was selected; and
- archive, payload, signal, target, model, prediction, and score operations
  were zero.

The aggregate result does not expose the actual row count or failed predicate.
This research does not infer either.

## Primary-Source Findings

Figshare's current official [API v2 documentation](https://docs.figshare.com/)
defines the version-files endpoint and supports the `page` plus `page_size`
pagination pair. The existing request already used an explicit page size of
1,000, so omitted pagination is no longer the unresolved issue.

The official [Public File Presenter](https://docs.figshare.com/old_docs/api/presenters/file/)
documents five public core fields:

```text
id
name
size
is_link_only
download_url
```

It describes `supplied_md5` and `computed_md5` as additions in the private file
presenter. In tension with that schema page, Figshare's current
[API usage guide](https://info.figshare.com/user-guide/how-to-use-the-figshare-api/)
shows a public full-metadata example whose file rows include both MD5 fields.
The safe conclusion is not that checksums are absent or present in the consumed
body. The safe conclusion is that those fields are observed extensions and are
not a stable public-core guarantee across all documented surfaces.

The API documentation also recommends conditional requests using `ETag` and
`Last-Modified`. Those headers are useful transport provenance, but they do
not replace version, canonical row identity, or an acquired-payload hash.

## Code Audit

The current generated pagination helper defines `WRIST_FIELDS` as exactly
seven names: the five public core fields plus `supplied_md5` and
`computed_md5`. Its validator requires exact set equality for every row before
checking counts, participant grammar, URLs, checksums, the `sub-01` anchor, or
declared bytes.

The live wrapper catches any exception from that helper and emits the single
safe reason `frozen inventory validation refused`. This was appropriate for a
one-bit acceptance gate, but it cannot distinguish:

- public-core schema incompatibility;
- optional-extension presence or absence;
- row or participant count drift;
- duplicate IDs or names;
- unsafe names or URLs;
- historical anchor drift;
- declared-byte drift; or
- checksum absence, malformed values, or disagreement.

This audit identifies an architectural coupling. It does **not** prove which
predicate failed in the consumed response.

## Proposed Three-Rung Provenance Ladder

### Rung 1 - Public source identity

Require the five documented public core fields with strict types, safe NFC
basenames, unique positive IDs, positive sizes, non-link-only files, and exact
HTTPS downloader URL construction. Reject duplicate JSON keys and recursively
reject target-like field names before retaining anything.

Treat `supplied_md5` and `computed_md5` as known optional extensions. When
present, each must be a lowercase 32-hex value and the pair must agree. Their
absence is explicit `unavailable`, not a public-core schema failure.

Any other field is not silently trusted. The future attestor may record only
an aggregate unknown-key count and a domain-separated key-set hash. Unknown
values are excluded from the private canonical manifest and prevent cohort
selection until prospectively reviewed.

### Rung 2 - Target-free cohort identity

Only after Rung 1 passes may the attestor classify safe basenames under the
frozen participant grammar. It computes row count, participant count,
supplementary count, duplicate counts, declared bytes, historical-anchor
comparisons, and the frozen 12-subject selection predicates.

Names, IDs, URLs, and per-row outcomes remain private. The public result may
expose aggregate counts, booleans, and domain-separated hashes because those
are sufficient to localize compatibility without publishing participant rows.

### Rung 3 - Payload integrity

Metadata selection does not prove payload integrity. A later separately
authorized acquisition must stream each chosen archive once, enforce the
declared size, and compute SHA-256 from the received bytes. A provider MD5, if
available, is an additional cross-check; it is not substituted for the
observed SHA-256.

If public MD5 is unavailable, payload acquisition remains blocked unless a
new prospective quarantine protocol explicitly authorizes one opaque download
whose hash is committed and remotely green before any archive parse. MARC1-SA1
does not authorize that protocol.

## Independent Predicate Vector

After structural and target-firewall safety passes, the future attestor must
evaluate every non-sensitive predicate independently instead of stopping at
the first ordinary mismatch:

```text
public_core_fields_present_all
known_optional_MD5_keysets_only
unknown_extra_field_rows
row_count
unique_ID_count
unique_name_count
safe_filename_count
valid_downloader_URL_count
non_link_only_count
participant_archive_count
supplementary_row_count
declared_byte_total
historical_row_count_matches
historical_participant_count_matches
historical_supplementary_count_matches
historical_declared_bytes_match
historical_sub01_anchor_matches
supplied_MD5_present_count
computed_MD5_present_count
MD5_pair_agreement_count
target_like_field_count
```

The vector may publish aggregate integer counts and booleans. It must not
publish a filename, file ID, URL, checksum, row, participant-level result, or
unknown-field value.

## Domain-Separated Identity Layers

One hash cannot explain which layer changed. MARC1-SA1 therefore proposes:

```text
transport_body_sha256       raw accepted response bytes; provenance only
public_core_sha256          canonical sorted five-field rows
optional_extension_sha256   canonical optional MD5 availability and values
row_shape_sha256            canonical per-row key-set signatures
classification_sha256       private participant/supplementary role mapping
selection_sha256            private frozen 12-subject selection and split
predicate_vector_sha256     aggregate compatibility vector
```

The public report may expose all seven hashes plus aggregate counts. The
private manifest retains only allowlisted source-core and optional-extension
values. Raw response bytes are not persisted.

## Prospective Router

```text
MARC1SA-F00  proof, contract, source, or output identity failure
MARC1SA-F01  transport, redirect, encoding, body-cap, or timeout failure
MARC1SA-F02  malformed JSON, duplicate key, or non-list/non-object shape
MARC1SA-F03  target-like key, unsafe name, invalid type, duplicate, or bad URL
MARC1SA-F04  output privacy, hash replay, overwrite, or resource failure
MARC1SA-R1   public core and historical inventory match; MD5 pair complete
MARC1SA-R2   public core and historical inventory match; MD5 unavailable/partial
MARC1SA-R3   safe public core but one or more historical predicates differ
MARC1SA-R4   unknown non-target schema extension observed; selection blocked
MARC1SA-G1   generated source-aware attestation qualification passes
```

`R1` through `R4` are aggregate engineering routes. None opens a participant
archive or constitutes a scientific result. Only a future `R1` could support
a later separately frozen selection packet. `R2` needs an integrity decision;
`R3` needs a new inventory identity decision; and `R4` needs source-schema
review.

## Generated Qualification Plan

The next Tier B contract should require generated fixtures for:

- the documented five-field public presenter;
- the seven-field observed extension;
- full, partial, malformed, and disagreeing MD5 extensions;
- reordered rows and reordered object keys;
- every independent historical-predicate drift;
- multiple simultaneous drifts to prove non-short-circuit evaluation;
- unknown scalar and nested fields;
- every target-like key at every nesting depth;
- unsafe names, IDs, sizes, URLs, duplicates, links, and JSON constants;
- deterministic private/public replay; and
- output-capability, symlink, overwrite, resource, and cleanup refusals.

The generated module must be standard-library only and have no URL opener,
dataset-specific execute command, registered-path operation, payload interface,
or import of a consumed executor.

## Resource And Authorization Boundary

Generated work is capped at one CPU thread, one worker, one numerical job, 30
seconds, 256 MiB peak RSS, 2 MiB generated input, and 2 MiB output. A possible
future metadata request remains one body capped at 2 MiB and 4 MiB incremental
disk with at least 10 GiB free.

This research authorizes no generated implementation before a frozen contract,
no MARC-1 endpoint request, no private or consumed-root operation, no archive
request, no payload byte, no signal or target read, no model or score, no retry
or rerun, and no scientific claim upgrade.

## Verification

Twelve focused research invariants and all 680 MARC tests pass. The complete
dependency-light suite passes 2,819 tests with 204 expected skips in 23.971
seconds at 219,365,376-byte external peak RSS. The isolated neuro-enabled suite
passes 2,875 tests with 34 expected skips in 115.768 seconds at 541,999,104-byte
external peak RSS.

Ruff, compilation, strict parsing of all 197 registry JSON documents, artifact
binding replay, and `git diff --check` pass. All numerical thread variables
were fixed to one for the complete suites.

## Same Research Path

MARC1-SA1 is not a pivot. It repairs the current cohort-identity gate in this
unchanged sequence:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

Engineering capability added: the next MARC-1 metadata gate now separates
official public source semantics, target-free selection identity, and observed
payload integrity while preserving aggregate privacy and one-shot evidence.

Scientific claim not established: this research accessed no dataset-specific
body, neural payload, signal, target, model, prediction, or score and therefore
adds no neural, language-decoding, or thought-to-text result.
