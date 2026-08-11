# IACKD-M1 Snapshot-Scoped Identity Recovery Research

Date: 2026-08-11

Status: **Tier A architecture research complete; no `ds006840` dataset body,
GraphQL dataset response, local IACKD path, EEG, target, model, or score was
accessed or authorized**

Registry:
`registries/iackd_snapshot_identity_recovery_research.v0.json`

## Question

How can a future IACKD experiment bind the intended OpenNeuro version without
letting harmless HTTP or JSON maintenance invalidate the run, and without
letting a real scientific change pass unnoticed?

The answer is to stop treating one mutable root-object byte stream as the
dataset-version identity. A future metadata-only audit should bind the
versioned OpenNeuro snapshot commit, its recursive content-addressed file tree,
the selected acquisition objects, and a small critical-metadata projection as
four distinct evidence layers.

## Observed Boundary

IACKD-2R is consumed and parked. Its first metadata response returned exactly
1,178 bytes but failed the preregistered raw SHA-256 before parsing. The body,
observed digest, framing profile, and changed fields were not retained. No
selected payload, EEG, trajectory, target, derivative, fit, prediction,
freeze, delivery, or score followed.

That result proves only that the live root metadata bytes differed from the
previously inventoried bytes. It does not establish whether the difference was
formatting, descriptive maintenance, or a scientific dataset change. This
research does not request the body again and does not infer its contents.

## Primary-Source Findings

1. OpenNeuro's [API examples](https://docs.openneuro.org/api.html) distinguish
   dataset-level metadata from a particular snapshot. A snapshot can be
   selected by dataset accession and tag, and its file tree exposes `id`,
   `filename`, `size`, `directory`, and `annexed` fields. Recursive traversal is
   supported.
2. OpenNeuro's [retention policy](https://docs.openneuro.org/policy/data_retention.html)
   says each snapshot creates a Git tag, synchronizes its files to S3, and uses
   Git/git-annex content addressing for integrity. Draft data is explicitly
   different from versioned snapshot data.
3. OpenNeuro's [architecture documentation](https://docs.openneuro.org/architecture.html)
   says a version or commit is a tree of content hashes and that tree-hash
   access is preferred because it is stable across working-tree state.
4. At pinned OpenNeuro source commit
   [`ead8d939`](https://github.com/OpenNeuroOrg/openneuro/tree/ead8d9394570c64ba4a62b94b85bc3f37a90e809),
   the snapshot GraphQL type exposes `id`, `tag`, `hexsha`, `description`, and
   recursive `files`. The resolver roots recursive file traversal at
   `snapshot.hexsha`.
5. The same pinned source reconstructs recursive results with full relative
   paths. Each file carries its Git object ID, size, annexed status, and URL.
   Public S3 URLs include an explicit `versionId`, so a future acquisition can
   address a snapshot object rather than an unversioned bucket key.
6. The snapshot description resolver reads `dataset_description.json` at the
   snapshot revision, but it also repairs missing or malformed values before
   returning them. Its fields are therefore a compatibility projection, not a
   substitute for the file's content-addressed identity.

No dataset-specific OpenNeuro API query, S3 request, local retained-bundle
operation, or protected-data read was made during this research. Only public
OpenNeuro documentation and pinned platform source code were inspected.

## Four-Layer Identity Model

### 1. Snapshot anchor

Require one exact snapshot lookup for accession `ds006840` and tag `1.0.0`.
The response must contain:

- snapshot ID `ds006840:1.0.0`;
- tag `1.0.0`;
- one full hexadecimal `hexsha` of 40 or 64 characters; and
- a description revision ID equal to that same `hexsha`.

The canonical snapshot anchor is the sorted JSON projection of accession,
snapshot ID, tag, and full `hexsha`. Response-body order, whitespace, HTTP
framing, cache headers, and the raw response SHA-256 are provenance fields, not
scientific-content identity.

### 2. Recursive snapshot tree

Request only the fields needed to identify the snapshot tree:

```text
id, filename, size, directory, annexed, urls
```

The validator must reject GraphQL errors, null lists or items, duplicate or
unsafe paths, directories in a recursive file result, malformed object IDs,
negative or non-integral sizes, unknown fields, and non-HTTPS URLs. It then
canonicalizes every file as:

```text
filename + git_object_id + size_bytes + annexed + s3_key + s3_version_id
```

Rows are sorted by full relative path before hashing. URL hosts, bucket/key
mapping, and version IDs are validated separately from expiring or transport
query details. A raw GraphQL body hash is retained only as an observation.

### 3. Selected acquisition inventory

Apply the already frozen target-blind selection rule to the recursive tree:
all files under `sub-*/eeg/` and `sub-*/sourcedata/beh/`, excluding
derivatives. Compatibility with the historical inventory requires exactly:

```text
participants:                 15
BIDS runs:                   128
selected objects:          1,340
selected payload bytes: 7,249,113,684
```

Every selected row must have a unique path, Git object ID, exact size, and one
snapshot-versioned public S3 URL. The future acquisition manifest is derived
from these version-scoped rows. It must not silently fall back to the old
unversioned root URLs, ETags, or last-modified timestamps.

### 4. Critical scientific metadata

The separate compatibility projection contains only fields that affect reuse
of the frozen scientific design:

```text
Name
BIDSVersion
License
DatasetDOI
```

For the historical `1.0.0` design these must equal the already committed
inventory values. Authors, acknowledgements, funding, links, display text,
JSON formatting, and field order are descriptive provenance. Changes there do
not establish scientific compatibility and do not invalidate it by
themselves. They may be recorded only after the four critical fields, snapshot
anchor, full tree, and selected inventory all pass.

Because OpenNeuro's GraphQL resolver repairs some description values, the
content-addressed `dataset_description.json` file row remains the raw-content
anchor. The compatibility projection cannot override a changed snapshot
commit or tree.

## Ordered Router

The prospective router is intentionally asymmetric:

1. `IACKDM-F00`: registration, source commit, query, or green-proof mismatch.
2. `IACKDM-F01`: HTTP, redirect, compression, body-cap, or GraphQL error.
3. `IACKDM-F02`: response shape, duplicate key, unknown field, or type failure.
4. `IACKDM-F03`: accession, tag, snapshot ID, `hexsha`, or description revision
   mismatch.
5. `IACKDM-F04`: recursive tree path, object ID, size, URL, or version-ID
   failure.
6. `IACKDM-F05`: historical participant, run, selected-object, selected-byte,
   or role-count incompatibility.
7. `IACKDM-F06`: critical Name, BIDS version, license, or DOI mismatch.
8. `IACKDM-F07`: output, runtime, RSS, thread, retry, or overwrite failure.
9. `IACKDM-R1`: one current snapshot identity is safely frozen and all legacy
   compatibility gates pass.

`IACKDM-R1` is an engineering compatibility result. It would authorize
nothing by itself. It cannot revive IACKD-2 or IACKD-2R, and it cannot prove a
neural effect.

## Smallest Next Evidence Sequence

1. Freeze an IACKD-M1 metadata-only contract with an exact GraphQL query,
   generated fixtures, mutation classes, one response, one thread, no retries,
   a 2 MiB body cap, 30-second runtime, 256 MiB RSS, and 1 MiB output.
2. Implement a standard-library semantic canonicalizer with no real URL opener
   and qualify it on generated responses only.
3. Commit, push, and require both CI jobs green.
4. Prepare one all-false Tier C packet for exactly one public GraphQL response.
5. Only after a fresh packet-bound decision and a second green implementation
   gate may the response be requested once and reduced to aggregate hashes,
   counts, version IDs, compatibility fields, warnings, and route.
6. If and only if `IACKDM-R1` passes, design a separately named acquisition and
   analysis lane using the newly frozen version-scoped URLs. Never amend or
   rerun either consumed IACKD invocation.

The metadata audit would transfer at most 2 MiB, write less than 1 MiB, and
touch no EEG payload. It is the cheapest legitimate way to determine whether
the intended public snapshot still supports the frozen experiment before
spending another 7.25 GB of network and disk.

## Claim Boundary

Engineering capability added: a snapshot-scoped, content-addressed identity
architecture now separates immutable dataset content, selected acquisition
objects, critical scientific metadata, and raw transport provenance.

Scientific claim not established: no dataset-specific metadata response, EEG,
event, trajectory, target, derivative, model, prediction, or score was
accessed, so this research establishes no neural effect or decoding result.
