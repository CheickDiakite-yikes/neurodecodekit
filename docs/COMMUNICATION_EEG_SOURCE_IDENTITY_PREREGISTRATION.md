# COMM-L0 Communication EEG Source Identity Preregistration

Date: 2026-08-26

Status: **Frozen prospective contract; generated-fixture implementation only
after this exact registration is remotely green; dataset-specific GraphQL
access remains unauthorized**

Contract:
`registries/communication_eeg_source_identity_contract.v0.json`

Parent program:
`docs/COMMUNICATION_EEG_SCIENTIFIC_CLAIM_PROGRAM.md`

## Objective

Qualify a strict, standard-library metadata canonicalizer and a deterministic,
target-free selector for OpenNeuro `ds003626` snapshot `2.1.2`. The future
metadata result must establish an immutable snapshot anchor, recursive file
tree, aggregate participant/session structure, and the smallest
peripheral-preserving discovery slice that retains all ten participants under
the 10 GiB cap.

This registration does not query OpenNeuro, download a file, inspect a local
path, read a BDF header or sample, parse an event, expose a target, create a
split, fit a model, freeze a prediction, score a result, or change the active
Tier C gate.

## Primary-Source Constraints

The source paper reports ten participants recorded in one day across three
sessions. Each session contains one pronounced-speech run, two inner-speech
runs, and two visualized-direction runs. Trial classes are randomized among
four Spanish directional commands.

Each raw session BDF contains the continuous 128 EEG channels, eight external
channels, and synchronized event tags. EXG1/EXG2 are reference channels,
EXG3-EXG6 record horizontal and vertical eye activity, and EXG7/EXG8 record
orbicularis-oris mouth activity. The paper's processed EEG applies ICA and
removes components correlated with EXG channels. Processed EEG therefore
cannot be the sole input to a claim that EEG adds information beyond eye and
mouth activity.

The metadata pass verifies file identity and structure only. Paper-reported
channel roles, event grammar, sampling rate, and trial counts remain
unverified source claims until a separately authorized semantic stage reads
the registered raw files.

## Exact Future Query

A separately authorized public metadata stage may make exactly one HTTPS POST
to `https://openneuro.org/crn/graphql` with this query:

```graphql
query CommunicationSourceIdentity {
  snapshot(datasetId: "ds003626", tag: "2.1.2") {
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
fallbacks, pagination, authentication, or additional fields are allowed. The
canonical request body contains only `query`. Its exact byte lengths and
SHA-256 hashes are frozen in the machine contract.

The generated implementation must not contain a URL opener, socket, HTTP
client, endpoint, `--execute` mode, or local dataset path. It accepts generated
response bytes directly.

## Transport And Strict JSON

The future wrapper remains outside this registration. It permits one direct
HTTP 200 response from the exact endpoint, identity encoding, no redirect,
retry, rerun, substitution, proxy, or response-body persistence, and a
2,097,152-byte body cap. Raw body hash and length are transport provenance,
not semantic identity.

JSON must be strict UTF-8 without BOM, duplicate keys, non-finite numbers,
NUL, or disallowed controls. The top level contains exactly `data`; `data`
contains exactly `snapshot`; and neither may be null. Any GraphQL `errors`
field refuses.

## Snapshot And Tree Projection

The snapshot must contain exactly `id`, `tag`, `hexsha`, `description`, and
`files`. Require snapshot ID `ds003626:2.1.2`, tag `2.1.2`, a 40- or
64-character lowercase hexadecimal commit, and a description revision equal to that
commit. The critical description fields are retained as observed metadata;
they do not silently rescue snapshot or tree drift.

Each recursive file object contains exactly `id`, `filename`, `size`,
`directory`, `annexed`, and `urls`. Normalize and validate unique safe NFC
POSIX relative paths, canonical nonnegative integer sizes, boolean directory
and annexed values, content-addressed IDs, and exactly one public HTTPS S3 URL
whose key matches `ds003626/<filename>` and whose sole query parameter is a
nonempty `versionId`. Canonical rows are source-order independent and sorted
by filename before hashing.

The first real metadata result may discover, but must not preregistration-fit,
the exact file count, total bytes, participant/session counts, description
values, tree hash, and selected-manifest hash. Public output contains only
aggregate counts, bytes, hashes, route, warnings, and unavailable fields.
Individual paths, URLs, version IDs, and row-level records remain private and
Git-ignored if later authority permits their retention.

## Deterministic Bounded Selection

The selector applies only to canonical metadata and never reads events,
labels, targets, BDF headers, or signal samples.

1. Discover participant IDs from canonical `sub-*` paths and require exactly
   `sub-01` through `sub-10` with no missing or additional participant.
2. Discover raw recording units by participant and session. A complete unit
   is one `sub-XX/ses-YY/eeg/` directory containing exactly one direct-child
   raw `.bdf` file preserving EEG plus EXG. Its selected companion set is every
   other direct-child file in that same directory, sorted by canonical path.
   No role is guessed from file contents.
3. Require exactly three complete raw sessions for every participant, as
   described by the primary paper, and require a common session-label set
   across all ten participants.
4. Choose the lexicographically first common complete session label for all
   ten participants. Never select participants or sessions by payload size,
   target count, class balance, signal quality, model result, or convenience.
5. Include all ten selected raw BDFs and every direct-child companion in each
   selected `eeg/` directory. Exclude derivatives and processed EEG/EXG arrays
   outside those raw session directories from the primary slice.
6. Require exactly ten participants, one common session each, ten raw BDFs,
   no duplicate role, and total selected bytes at or below 10,737,418,240.
7. If paths do not support this interpretation, a participant or role is
   missing, session labels differ, the same earliest session is not complete
   for all ten, or the selected bytes exceed the cap, park without a fallback
   or a second query.

This rule preserves the participant-held-out design while reducing payload
before any scientific result exists. It does not claim the slice is sufficient
for a final analysis. Trial counts and condition completeness remain later
semantic gates.

## Generated Qualification

Only after this registration is committed, pushed, and both required CI jobs
are green may Tier B implement and execute one generated qualification. It
must exercise:

- deterministic replay under shuffled source rows;
- exact query and request hashes;
- strict JSON, snapshot, path, size, URL, and version-ID refusals;
- all-ten participant identity and three-session completeness;
- lexicographically first common-session selection;
- no participant dropping or size-based substitution;
- required raw BDF and same-session sidecar completeness;
- processed-only, derivative-only, mixed-session, and missing-role refusals;
- selected-byte cap and output cap enforcement;
- no-clobber, symlink, runtime, RSS, thread, network-construction, and real-path
  refusals; and
- aggregate inspection that cannot expose individual paths, URLs, version IDs,
  target counts, or participant outcomes.

The generated fixture contains no copied real response, participant metadata,
signal, event, target, label, prediction, or outcome. It has zero scientific
value.

## Resource And Authority Boundary

```text
generated qualifications now:           0
future generated qualifications:         1 after green registration
CPU threads / workers / jobs:             1 / 1 / 1
wall time:                                30 seconds
peak RSS:                                 268,435,456 bytes
generated or future response cap:         2,097,152 bytes
combined public/generated output cap:     1,048,576 bytes
future metadata requests:                 1 after separate Tier C decision
future metadata body bytes:               2,097,152 maximum
payload network bytes:                    0
incremental payload bytes:                0
future selected raw payload cap:           10,737,418,240 bytes
total incremental research storage cap:    21,474,836,480 bytes
model / training / inference / score:     0 / 0 / 0 / 0
```

The maintainer increased the total research-storage allowance to 20 GiB while
requiring careful management and no damage to the computer or other projects.
The selected raw-data cap remains the more conservative 10 GiB. The remaining
allowance is reserved for bounded derivatives, invocation-owned temporary
files, and atomic publication overhead; it cannot expand the selected cohort.
At registration time the data volume reported approximately 73 GiB available.
A future payload contract must recompute free space, reserve its full projected
footprint before consumption, and fail before transfer if it cannot preserve a
separate system-safety margin.

Every current authority flag remains false. `DREYER-C5R-1-HL` remains the sole
active Tier C packet. This parallel registration cannot be used as a maintainer
decision, a retroactive authorization, or permission to change that gate.

## Ordered Evidence Gates

1. Commit, push, and remotely green this preregistration, machine contract,
   and invariant tests.
2. Implement and run one generated-only canonicalizer and selector
   qualification.
3. Commit, push, and remotely green its exact implementation and result.
4. Prepare and remotely green an all-false Tier C metadata authorization
   packet without displacing another active Tier C packet.
5. After the active gate is clear, identify the one-response packet with its
   exact commit, CI, request hash, caps, and stop boundary.
6. Stop. Only a fresh packet-bound maintainer decision may authorize one real
   metadata wrapper and response.
7. Freeze the aggregate metadata result before preparing any payload
   acquisition contract.

## Claim Boundary

Engineering capability proposed: a strict source-identity layer can select one
complete peripheral-preserving raw session for every discovery participant
without inspecting scientific content or adapting the slice to outcomes.

Scientific claim not established: no dataset-specific response, payload,
signal, event, target, model, prediction, score, unseen-person result,
peripheral-adjusted EEG result, communication decoding result, or live result
is established.

## Primary Sources

- [Thinking Out Loud descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [OpenNeuro `ds003626`](https://openneuro.org/datasets/ds003626/versions/2.1.2)
