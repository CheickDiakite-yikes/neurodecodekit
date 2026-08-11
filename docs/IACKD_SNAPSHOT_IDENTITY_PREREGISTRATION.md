# IACKD-M1 Snapshot Identity Preregistration

Date: 2026-08-11

Status: **Frozen prospective contract; generated-fixture implementation only
after this exact registration is remotely green; public GraphQL access remains
unauthorized**

Contract:
`registries/iackd_snapshot_identity_contract.v0.json`

Research basis:
`docs/IACKD_SNAPSHOT_IDENTITY_RECOVERY_RESEARCH.md`

Green research proof:
commit `723c8e244ff5f414cb4859bd122d42cccfaa795f`, CI `31480538821`,
Base Python job `93744221145`, Optional Neuro Readers job `93744221059`.

## Objective

Qualify a strict, standard-library semantic canonicalizer for one generated
OpenNeuro snapshot response. It must prove that snapshot identity, recursive
file-tree identity, acquisition selection, and critical metadata can be
validated independently without using raw response bytes as the scientific
identity.

This registration is an engineering prerequisite. It is not permission to
query `ds006840`, inspect a local IACKD bundle, request an EEG payload, run a
model, open a target, or score a result.

## Exact Future Query

The future public stage, if separately authorized, may make exactly one HTTPS
POST to `https://openneuro.org/crn/graphql` with one frozen GraphQL query:

```graphql
query IackdSnapshotIdentity {
  snapshot(datasetId: "ds006840", tag: "1.0.0") {
    id
    tag
    hexsha
    description {
      id
      Name
      BIDSVersion
      License
      DatasetDOI
    }
    files(recursive: true) {
      id
      filename
      size
      directory
      annexed
      urls
    }
  }
}
```

No variables, aliases, fragments, directives, introspection, mutations,
additional fields, fallback query, pagination request, or authentication token
are allowed. The request body is canonical JSON containing only `query`, and
the exact query and request-body hashes are frozen in the machine contract.

The generated implementation must contain no URL opener, socket, HTTP client,
real endpoint, `--execute` mode, or local IACKD path. It receives generated
response bytes directly.

## Response Transport

A future real wrapper remains outside this registration. Its one response must
use HTTP 200, exact final URL, no redirect, identity content encoding, and one
unambiguous fixed-length, chunked, or close-delimited framing profile. It reads
at most 2,097,153 bytes once and refuses overflow, read error, malformed
framing, compression, or a second read. `Content-Length` and raw response
SHA-256 are recorded as transport provenance only.

Semantic parsing begins only after transport passes. JSON must be strict UTF-8
with no BOM, duplicate keys, non-finite numbers, NUL, or disallowed controls.
The top-level object contains exactly `data`; `data` contains exactly
`snapshot`; neither may be null. Any GraphQL `errors` field, even alongside
data, refuses.

## Snapshot Anchor

The snapshot object contains exactly `id`, `tag`, `hexsha`, `description`, and
`files`. Require:

```text
id:       ds006840:1.0.0
tag:      1.0.0
hexsha:   40 or 64 lowercase hexadecimal characters
```

The description contains exactly `id`, `Name`, `BIDSVersion`, `License`, and
`DatasetDOI`. Its `id` must equal the full snapshot `hexsha`. The canonical
snapshot anchor hashes accession, snapshot ID, tag, and `hexsha` with sorted
compact JSON.

## Recursive File Tree

The response must contain exactly 1,679 non-null file objects. Each contains
exactly `id`, `filename`, `size`, `directory`, `annexed`, and `urls`.

Require:

- `id` is 40 or 64 lowercase hexadecimal characters;
- `filename` is a unique NFC-normalized safe POSIX relative path;
- no empty, absolute, dot, dot-dot, backslash, repeated-separator, query,
  fragment, NUL, control, or percent-encoded path ambiguity;
- `size` is a nonnegative JSON integer or canonical unsigned decimal string,
  normalized to an integer without accepting booleans, signs, whitespace,
  leading zeros, fractions, or exponents;
- `directory` is exactly false and `annexed` is a JSON boolean; and
- `urls` contains exactly one public HTTPS S3 URL.

The URL must use host `s3.amazonaws.com`, bucket `openneuro.org`, path
`ds006840/<filename>`, no user info, port, fragment, or alternate host, and
exactly one nonempty `versionId` query parameter with no other parameters.
The version ID is treated as opaque text after strict length and character
validation.

Canonical rows contain only normalized filename, Git object ID, integer size,
annexed status, S3 key, and version ID. Rows are sorted by filename before a
full-tree SHA-256 is computed. Raw source order is not identity.

## Historical Compatibility

Apply the frozen selection rule to the canonical tree: all files under
`sub-*/eeg/` and `sub-*/sourcedata/beh/`, excluding derivatives. Compatibility
requires the committed aggregate exactly:

```text
participants:                 15
participant-hand units:       30
BIDS runs:                   128
selected objects:          1,340
selected bytes:       7,249,113,684
all tree objects:          1,679
all tree bytes:       7,966,799,433
```

All twelve historical role counts and byte totals must match. The selected
manifest is canonicalized and hashed separately from the full tree. A future
real audit may retain one Git-ignored private manifest containing the selected
versioned acquisition rows, but public output contains only its hash, count,
bytes, and aggregate role summaries.

## Critical Metadata

The exact compatibility projection is:

```text
Name:        IACKD: Intention Action Conflict EEG-Hand Kinematics Dataset
BIDSVersion: 1.7.0
License:     CC0
DatasetDOI:  10.18112/openneuro.ds006840.v1.0.0
```

Any mismatch parks. These values cannot rescue snapshot or tree drift. Because
the current OpenNeuro resolver may repair malformed source values, the
`dataset_description.json` file row and snapshot commit remain the raw-content
identity anchors.

## Generated Qualification

After this registration commit is pushed and both CI jobs are green, Tier B
permits one generated qualification. It must construct exactly 1,679 synthetic
metadata rows that satisfy all historical counts and byte totals without
copying any real response body, signal, event, trajectory, target, label,
prediction, or participant outcome.

Required checks include:

- deterministic replay of snapshot, full-tree, selected-manifest, request,
  response, and output hashes;
- exact success route `IACKDM-R1` on the constructed compatible fixture;
- duplicate JSON key and GraphQL error refusal;
- null, unknown, missing, and wrong-type field refusal at every level;
- wrong snapshot ID, tag, `hexsha`, and description revision refusal;
- critical Name, BIDS version, license, and DOI drift refusal;
- duplicate, unsafe, non-NFC, and percent-ambiguous path refusal;
- malformed Git ID, boolean/fractional/negative/noncanonical size, directory,
  and annexed-type refusal;
- missing, duplicate, alternate-host, non-HTTPS, key-mismatched, extra-query,
  fragment, and missing-version URL refusal;
- all-tree count/byte, selected count/byte, participant, run, and each role
  summary drift refusal;
- output overwrite, symlink, cap, runtime, RSS, thread, network-construction,
  and real-path refusal; and
- metadata-only inspection that never exposes individual paths, URLs, version
  IDs, or row-level records.

The CLI is dry-run first and has only generated `qualify` and metadata-only
`inspect` modes. It has no public request mode.

## Resource Caps

```text
generated qualifications:       1
CPU threads / workers / jobs:    1 / 1 / 1
wall time:                       30 seconds
peak RSS:                        268,435,456 bytes
generated response bytes:        2,097,152 maximum
combined generated outputs:      1,048,576 bytes
network bytes:                   0
dataset-specific responses:      0
local IACKD path operations:     0
model/training/inference/score:  0 / 0 / 0 / 0
```

The future real metadata audit, if separately authorized, inherits the same
thread, time, RSS, response, and output caps and permits exactly one request,
zero retries, and zero reruns. It permits no payload body.

## Ordered Evidence Gates

1. Commit and push this preregistration, contract, and invariant test; both CI
   jobs must pass.
2. Implement and qualify only the generated standard-library canonicalizer.
3. Commit and push that exact implementation; both CI jobs must pass.
4. Prepare an all-false Tier C request binding both green milestones.
5. Commit and push that request; both CI jobs must pass.
6. Identify it as the sole active packet with exact commit, CI, one-response
   scope, caps, and stop boundary.
7. Stop. Only the maintainer's next fresh unambiguous packet-bound message may
   enter a separate decision, and that decision must become remotely green
   before any real wrapper is integrated.
8. Commit and green the exact real wrapper before the sole public response.

The current `continue` preceded this registration and cannot be applied
retroactively.

## Claim Boundary

Engineering capability proposed: one strict generated canonicalizer can bind
OpenNeuro snapshot, tree, selected-manifest, and critical-metadata identity
without conflating them with transport bytes.

Scientific claim not established: this registration accesses no
dataset-specific response, EEG, event, trajectory, target, model, prediction,
or score and establishes no neural effect or decoding result.
