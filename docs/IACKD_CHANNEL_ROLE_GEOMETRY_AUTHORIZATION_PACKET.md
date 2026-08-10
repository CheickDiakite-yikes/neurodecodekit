# IACKD Channel Role and Geometry Authorization Packet

Date: 2026-08-10

Status: **Exact packet-bound Tier C decision requested; not granted**

Lane: **IACKD-H2 Channel Role and Geometry Audit**

Implementation commit:
`9f6fef9540ae0a1fe52cbf24b17b0af89147beae`

Green implementation CI: `31430151368`

Machine request:
`registries/iackd_channel_role_geometry_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for one small public-metadata audit that can replace
the failed global channel-count assumption with an observed source-declared
sensor-role and geometry contract. It does not inspect or reopen the retained
7.249 GB local IACKD bundle.

The future invocation would request exactly 316 already inventoried OpenNeuro
`ds006840` version `1.0.0` bodies: 128 channel tables, 128 EEG sidecars, 30
electrode tables, and 30 coordinate-system files. Together they total exactly
457,602 bytes. Each body remains in memory for one SHA-256 pass and one strict
semantic parse, then is discarded before the next request.

The only public output is one aggregate JSON ledger. It may group channel
schemas, status counts, allowlisted sidecar values, one role-map candidate,
geometry coverage, source reconciliation, warnings, unavailable fields,
measures, and route R0-R4. It may not publish any source path, participant,
per-run row, coordinate, free text, signal, event, trajectory, target, model,
prediction, or score.

This packet authorizes nothing by itself.

## Why A Fresh Decision Is Required

The Research Autonomy Charter permitted the completed Tier B generated-fixture
implementation. Opening public metadata bodies is a Tier C real-content action.
The maintainer's earlier instruction to continue preceded this immutable packet
and cannot authorize it retroactively.

After this packet is committed, pushed, and both CI jobs are green, Codex may
identify its exact commit, CI run, sole scope, and decision boundary. If it is
still the only active Tier C packet, a fresh unambiguous `continue`, `approve`,
or `proceed` may bind it by reference. The separate decision artifacts must
quote the maintainer's actual words and bind this request, contract,
implementation, proof, and caps. Codex must not fabricate a long authorization
sentence as a user utterance.

## Immutable Proof

Registration commit `228ccd03f5e0b5d02ba104e13b77b04f2032df78`
passed Base Python job `93583989913` and Optional Neuro Readers job
`93583989996` in CI `31427931578`.

Exact implementation commit
`9f6fef9540ae0a1fe52cbf24b17b0af89147beae` passed Base Python job
`93591323731` and Optional Neuro Readers job `93591323646` in CI
`31430151368`. Its implementation registry SHA-256 is
`b3989d4489c2f3b95d4ca70b6caf0505a413b13e2bebdec6a6aad8b52d124acb`.

The implementation passed 47 focused tests, 1,751 base tests, and 1,822
optional-neuro tests. Ruff, compilation, all 130 registry JSON files, CLI help,
dry run, generated roundtrip, inspection, missing-evidence refusal, and diff
checks passed. The final generated traversal covered the same 316 body sizes
and 457,602 bytes in 0.054679625 seconds at 34,996,224-byte peak RSS with
8,282 output bytes and zero network or real/protected operations.

## Requested One-Shot Execution

Only after a separate decision commit is pushed and both CI jobs pass may one
invocation:

1. verify the exact contract, inventory, implementation registry, packet,
   decision, commits, CI identifiers, tracked hashes, clean worktree, and
   execution ordinal one;
2. create one private Git-ignored consumed marker before the first request;
3. issue exactly 316 sequential HTTPS GETs in canonical inventory order;
4. reject redirect, retry, substitution, compression, chunking, URL drift,
   non-200 status, wrong Content-Length, wrong ETag, or a body over 8,192 bytes;
5. read exactly 457,602 body bytes total, hash and semantically parse each body
   exactly once, then discard it before the next request;
6. pair channel tables with sidecars by private run identity and electrode
   tables with coordinate systems by private participant/hand identity;
7. reconcile H1 declarations, source BIDS roles, sidecar counts and sampling,
   reference declarations, and central/occipital geometry coverage;
8. validate that paths, identities, rows, coordinates, free text, and all
   forbidden fields remain absent from public output;
9. emit one bounded aggregate ledger, apply `IACKDR-R0` through `IACKDR-R4`,
   and stop.

There is no alternate object, metadata refresh, parser amendment, fallback,
retry, or rerun. If any gate fails after the consumed marker is written, the
one execution is consumed.

## Resource Caps

| Resource | Maximum |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time | 180 seconds |
| Peak RSS | 268,435,456 bytes |
| HTTPS requests | 316 |
| Expected body bytes | 457,602 |
| Network body bytes | 2,097,152 |
| Bytes read per object | 8,192 |
| Incremental disk | 4,194,304 bytes |
| Public output | 2,097,152 bytes |
| Minimum free disk | 2,147,483,648 bytes |
| Retries / reruns | 0 / 0 |

No dependency installation, metadata-list refresh, provider, model, or
numerical workload is requested.

## Explicitly Not Authorized

- statting, resolving, hashing, opening, moving, deleting, or otherwise using
  the retained local IACKD bundle;
- any VHDR, VMRK, EEG payload, events TSV, ball, Leap, derivative, CURRY,
  participant table, sibling, or unregistered object;
- signal samples, markers, events, trajectories, labels, targets, caches,
  splits, features, models, checkpoints, fitting, inference, predictions,
  freezes, target delivery, or scoring;
- S20, S21, S24, S25, SpanishBCBL, PhysioNet, raw FIF, or MAT access;
- additional object URLs, inventory refreshes, substitutions, redirects,
  retries, resumes, restarts, or reruns;
- package installation, MNE or another neural reader, foundation or language
  models, providers, RW3, streams, devices, or hardware;
- individual or protected output, upload, publication, release, or
  patent/device implementation; and
- IACKD-2 preregistration/execution or any scientific, decoding, neural,
  brain-specific, generalization, real-time, portable, home-use, assistive, or
  clinical claim upgrade.

## Outcome Meaning

- `IACKDR-R0`: response, parser, membership, resource, output, or completeness
  failure prevented a compatibility conclusion.
- `IACKDR-R1`: H1, BIDS role, sidecar count, or sampling declarations
  contradict, so no role map is admissible.
- `IACKDR-R2`: roles reconcile but the core name/type/unit schema varies beyond
  optional M1/M2.
- `IACKDR-R3`: roles are stable but reference or finite central geometry is
  incomplete.
- `IACKDR-R4`: one count-agnostic role map is compatible with all registered
  declarations and all 30 geometry groups have finite C3/C4/Cz.

Every route is a metadata compatibility result. Even R4 does not establish
signal quality, neural origin, action decoding, or any model result; it only
permits a separately preregistered future reader to bind one role-map hash.

## Current State

Every execution authorization flag in the machine request is false. Preparing
this packet made zero network requests, real metadata reads, local IACKD path
operations, VHDR/sibling operations, signal/event/trajectory/target reads,
model runs, scores, retries, reruns, releases, or claim changes.

Engineering capability requested: one exact, resource-bounded public metadata
audit can freeze whether a count-agnostic source-declared sensor-role and
geometry contract is compatible with all registered IACKD files.

Scientific claim not established by this request: this all-false packet is not
data or a result and establishes no neural effect, action decoding,
brain-specific origin, generalization, real-time operation, hardware
capability, assistive benefit, or clinical use.
