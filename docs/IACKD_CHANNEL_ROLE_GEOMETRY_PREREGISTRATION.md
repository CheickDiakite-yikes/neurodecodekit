# IACKD Channel Role and Geometry Preregistration

Date: 2026-08-10

Status: **Frozen prospective H2 contract; generated-fixture implementation is
eligible only after this exact registration is remotely green; all real public
body, retained-bundle, sibling, signal, event, trajectory, target, model, and
score access remains unauthorized**

Contract:
`registries/iackd_channel_role_geometry_contract.v0.json`

Research basis:
`docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md`

Lane: **IACKD-H2 Channel Role and Geometry Audit**

## Objective

Determine the exact source-declared channel roles, reference declarations, and
geometry coverage needed for a future count-agnostic IACKD reader, without
opening a BrainVision triplet or the retained local bundle.

H2 is a public metadata compatibility audit. It cannot repair or rerun the
consumed IACKD-1 experiment, create an IACKD-2 split, or produce neural
evidence.

## Green Anchors

The consumed H1 result commit
`a6704898cfb09f6321bac5f15e27424f02614317` passed Base Python job
`93575925675` and Optional Neuro Readers job `93575925695` in CI
`31425445891`.

The role-aware research commit
`41ea1fcc6c31ebe67437ae4d381b4a57cf6cef54` then passed Base Python job
`93580219586` and Optional Neuro Readers job `93580219644` in CI
`31426772597` before this contract was frozen.

No H2 body or local IACKD path was requested, statted, resolved, or opened
while preparing this registration.

## Exact Public Surface

The source is OpenNeuro `ds006840` version `1.0.0`, DOI
`10.18112/openneuro.ds006840.v1.0.0`. Filter the already committed metadata
inventory by the exact roles `channels`, `eeg_sidecar`, `electrodes`, and
`coordsystem`, then sort by path.

| Role | Objects | Exact bytes | Minimum | Maximum |
|---|---:|---:|---:|---:|
| `channels` | 128 | 227,904 | 1,752 | 1,866 |
| `eeg_sidecar` | 128 | 173,312 | 1,354 | 1,354 |
| `electrodes` | 30 | 27,316 | 890 | 967 |
| `coordsystem` | 30 | 29,070 | 969 | 969 |
| **Total** | **316** | **457,602** | **890** | **1,866** |

The canonical identity serialization is 53,367 bytes with SHA-256:

```text
0a63b46395030cb967dbca05f37a1367cf2bb0bf1088befce378a3556eab2274
```

No substitution, additional object, VHDR reread, marker, EEG signal, event,
ball/Leap stream, derivative, or local copy may enter this lane.

## Ordered Evidence Sequence

1. Commit and push this exact registration and pass both CI jobs.
2. Under Tier B, implement only standard-library parsers, generated fixtures,
   mocked transport, aggregate routing, resource guards, and a module CLI.
3. Commit and push that exact implementation and pass both CI jobs.
4. Prepare one all-false Tier C authorization packet binding the green
   registration and implementation.
5. Commit and push the packet and pass both CI jobs.
6. Identify that sole packet, exact commit, CI, and scope to the maintainer.
7. Record a fresh unambiguous packet-bound maintainer decision in a separate
   commit and pass both CI jobs.
8. Run exactly one public 316-object audit without retry or rerun, route it,
   close it, and stop.

The current instruction, research autonomy charter, prior IACKD decisions, 10
GB allowance, and H1 execution do not authorize step 8.

## Transport Contract

Use Python's standard-library HTTPS stack only. For each object in canonical
path order:

1. construct only its exact registered OpenNeuro URL;
2. require status 200, no redirect, exact final URL, exact Content-Length,
   exact ETag, and identity content encoding;
3. refuse before semantic use if any response identity differs;
4. read at most 8,192 bytes and require the exact registered body size;
5. compute exactly one SHA-256 over the body;
6. strictly decode and semantically parse the body exactly once;
7. retain only the parsed aggregate contribution and body hash; and
8. discard the body before requesting the next object.

There are no temporary payload files. The aggregate writer is exclusive,
atomic, canonical JSON. It refuses overwrite. A private consumed marker must
be created atomically before the first real request.

## Channel Table Contract

Each `channels.tsv` body must:

- decode as strict UTF-8 with optional UTF-8 BOM and no NUL or disallowed
  control character;
- contain one TSV header with `name`, `type`, and `units` as the first three
  columns in that exact order;
- contain no duplicate column name;
- contain 1-64 data rows with exactly the header width;
- contain nonempty names unique after Unicode NFC, trim, and case-insensitive
  alphanumeric normalization;
- use an exact uppercase registered BIDS channel type;
- contain a nonempty unit or exact `n/a`;
- use only `good`, `bad`, or `n/a` when a status field is present;
- use a positive finite sampling frequency or `n/a` when that field is
  present; and
- preserve unknown optional column names only as a hash while publishing none
  of their values.

Descriptions and status descriptions are parsed only for shape and control-
character safety, then discarded.

The semantic role policy is fixed before results:

- predictive EEG candidate: type `EEG`, excluding exact names M1 and M2;
- recorded EOG control: exact names HEOG and VEOG with compatible `HEOG`,
  `VEOG`, or generic `EOG` type;
- trigger: exact name TRIGGER with compatible `TRIG` or `MISC` type;
- optional mastoid/reference candidate: exact M1 or M2, with its source type
  reported rather than inferred; and
- no name, count, unit, geometry, target, or score may override the source type
  silently.

To test stability, remove only exact M1/M2 rows and compare the remaining
ordered `(name, type, units)` core schema across all 128 runs. H2 does not
assume in advance that the core contains 26 EEG channels.

## EEG Sidecar Contract

Each `eeg.json` body must be a duplicate-key-free top-level JSON object. It
must contain the BIDS-required task, EEG reference, sampling frequency, power
line frequency, and software-filter fields. Sampling frequency must be finite
and positive.

Only these values may enter the public aggregate:

- SamplingFrequency;
- EEGReference;
- PowerLineFrequency;
- RecordingType;
- EEGChannelCount;
- EOGChannelCount;
- ECGChannelCount;
- EMGChannelCount;
- MiscChannelCount; and
- TriggerChannelCount.

Software filters may contribute one canonical hash, never free text. Task
descriptions, instructions, institutions, device serials, artifact narratives,
and unregistered values are excluded from public output.

When a type-count field is present, the router compares it with the parsed
channel table. Missing recommended count fields remain explicit unavailable
values; they are not invented and do not cause a parse failure.

## Electrode And Coordinate Contract

Each `electrodes.tsv` body must contain `name`, `x`, `y`, and `z` as its first
four columns, unique normalized names, and rows of exact header width. Each
coordinate is either finite numeric text or exact `n/a`. No coordinate value
may enter public output.

Each paired `coordsystem.json` must be duplicate-key-free and contain a
nonempty EEG coordinate system plus units in `m`, `cm`, or `mm`. Fiducial and
anatomical landmark coordinates, descriptions, and device details are never
retained publicly.

The audit joins channel and electrode names by exact registered normalization
within the 30 participant-hand geometry groups. It does not require channel
and electrode tables to have equal rows. It reports only:

- electrode count and finite-coordinate count;
- predictive-EEG geometry coverage count;
- finite C3/C4/Cz coverage;
- finite O1/Oz/O2 coverage;
- channel/electrode intersection counts;
- coordinate-system and unit groups; and
- hashes of ordered names and coordinate bytes.

No source path, participant identifier, per-run status, or coordinate appears
in the public ledger.

## Cross-Source Reconciliation

The completed audit must compare:

1. the channel-row count multiset with H1's frozen 96-by-29 and 32-by-31
   declaration groups;
2. HEOG, VEOG, TRIGGER, M1, and M2 presence with H1's aggregate result;
3. parsed BIDS type counts with sidecar count fields when available;
4. per-channel sampling declarations with sidecar sampling when available;
5. all sidecar sampling values with H1's 1024 Hz declaration; and
6. each channel core schema with the other 127 core schemas after removing
   only M1/M2.

The aggregate result may identify contradictions but may not adapt the policy
after seeing them.

## Public Ledger

The one public ledger may contain:

- provenance and proof posture;
- exact aggregate input/output/runtime/RSS measures;
- body-hash-set and canonical-source hashes;
- unique ordered `(name, type, units)` channel schemas with occurrence counts;
- aggregate status and sidecar groups;
- one candidate role map and its hash when deterministically available;
- geometry coverage groups without coordinates;
- H1 reconciliation results;
- every warning and unavailable field;
- all access counters and acceptance gates; and
- one diagnostic route and claim boundary.

It may not contain raw bodies, source URLs or paths, local paths, free text,
coordinate values, device serials, individual status rows, participant-level
records, signals, events, trajectories, targets, features, models,
predictions, or outcomes.

## Diagnostic Router

Apply the first matching route:

| Route | Frozen condition |
|---|---|
| `IACKDR-R0` | Any source identity, response, parse, membership, resource, or completeness gate fails. |
| `IACKDR-R1` | H1 row counts/name presence, BIDS role counts, sidecar counts, or sampling declarations contradict. |
| `IACKDR-R2` | More than one core `(name,type,units)` schema remains after removing only M1/M2, or a retained name changes role. |
| `IACKDR-R3` | Roles are stable, but reference declarations vary or are unavailable, coordinate metadata is invalid, or any geometry group lacks finite C3/C4/Cz. |
| `IACKDR-R4` | Roles are stable, H1 and sidecars reconcile, reference and sampling are stable, and all 30 groups have finite C3/C4/Cz geometry. |

Occipital O1/Oz/O2 geometry is reported but does not gate `R4`; its complete
availability separately determines whether IACKD-2 may preregister the
occipital visual proxy.

## Resource Caps

```text
registered executions:       1
threads / workers / jobs:    1 / 1 / 1
wall time:                   180 seconds
peak RSS:                    268,435,456 bytes
requests:                    316
expected body bytes:         457,602
network body cap:            2,097,152 bytes
maximum body bytes:          8,192
incremental disk cap:        4,194,304 bytes
public output cap:           2,097,152 bytes
minimum free disk:           2,147,483,648 bytes
retries / reruns:            0 / 0
```

Producer causality is not applicable to static metadata, and end-to-end
decoding latency is not measured.

## Acceptance Gates

All must pass for a completed route:

1. green registration, implementation, request, and decision precede access;
2. exactly 316 registered responses and 457,602 body bytes are consumed;
3. each response passes identity, one hash, and one semantic parse;
4. all 128 channel tables and sidecars and all 30 geometry pairs reconcile;
5. aggregate schemas, role map, geometry groups, and router replay exactly;
6. local-bundle, VHDR, sibling, sample, event, trajectory, target, model,
   prediction, and score counters remain zero;
7. every resource and output cap passes;
8. no forbidden public field appears; and
9. the metadata-only claim ceiling is preserved.

## Refusal Boundary

The future executor must fail closed on version or inventory drift, redirect,
retry, status/URL/size/ETag/encoding mismatch, malformed UTF-8/TSV/JSON,
duplicate key/name/column, invalid role/unit/status/number, incomplete geometry
pair, path disclosure, overwrite, cap breach, ungreen proof, second execution,
or forbidden access.

No failure permits substitution, parser relaxation, new object, local bundle
fallback, VHDR reread, scientific model work, retry, or rerun.

## Claim Boundary

Engineering capability proposed: a strict BIDS role-and-geometry audit can
freeze a count-agnostic sensor contract before a future IACKD reader touches
signals.

Scientific claim not established: this preregistration opened no new public
body or retained EEG and ran no model or score, so it establishes no neural
effect, action decoding, brain-specific origin, unseen-person generalization,
typing, language or thought decoding, real-time operation, hardware capability,
assistive benefit, or clinical use.
