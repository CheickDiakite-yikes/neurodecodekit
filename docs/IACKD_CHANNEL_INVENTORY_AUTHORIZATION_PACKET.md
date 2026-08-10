# IACKD Header Inventory Audit Authorization Packet

Date: 2026-08-10

Status: **Exact packet-bound Tier C decision requested; not granted**

Lane: **IACKD-H1 Header Inventory Audit**

Implementation commit:
`16621cc484f4bec4a9474b9ac20d5b7d9314152f`

Green implementation CI:
`31415213841`

Machine request:
`registries/iackd_channel_inventory_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for one tiny public-header audit that can tell us
why the consumed IACKD-1 experiment rejected its first BrainVision file. It
does not reopen or inspect the retained 7.249 GB local bundle.

The future invocation would request exactly 128 public `.vhdr` bodies from the
already pinned OpenNeuro `ds006840` version `1.0.0` object URLs. Together they
total exactly 161,792 bytes, about 0.0022% of the acquired bundle. Each body is
held only in memory long enough for one SHA-256 pass and one strict declaration
parse, then discarded before the next request.

The only output is one aggregate JSON ledger. It can report declared channel
counts, ordered-name-list hashes, sampling declarations, and exact presence of
M1, M2, HEOG, VEOG, HEO, VEO, and TRIGGER. It cannot report an individual path,
an unallowlisted channel name, raw header text, comments, participant outcomes,
signals, events, trajectories, labels, targets, predictions, or scores.

This packet authorizes nothing by itself.

## Why A New Decision Is Required

The Research Autonomy Charter permits the completed Tier B implementation, but
opening public VHDR bodies is a Tier C real-content action. The earlier user
instruction to continue preceded this immutable packet and cannot authorize it
retroactively.

After this request is committed, pushed, and remotely green, Codex may identify
its exact commit, CI run, and sole scope. If this remains the only active Tier C
packet, a new unambiguous `continue`, `approve`, or `proceed` may bind it by
reference. The separate decision artifacts must quote the user's actual words
and bind this request, contract, implementation, CI evidence, and caps. Codex
must not fabricate a long authorization sentence as a user utterance.

## Immutable Proof

Registration commit `0e52278aaa1d15e70f4baab7b21ab1c96eb37f67`
passed Base Python job `93534203368` and Optional Neuro Readers job
`93534203385` in CI `31412667060`.

Exact implementation commit
`16621cc484f4bec4a9474b9ac20d5b7d9314152f` passed Base Python job
`93542494819` and Optional Neuro Readers job `93542494839` in CI
`31415213841`. Its implementation registry SHA-256 is
`2f9abb004d921088dc65ede3edcf4426d804d1016d8b0e1a0b3680f8e9965d64`.

The implementation was qualified with 32 focused tests, 1,663 base tests, and
1,734 neuro-enabled tests. Ruff, compileall, 124 registry JSON files, CLI help,
dry run, generated roundtrip, inspection, and diff checks passed. Its measured
generated roundtrip processed the same 128 body sizes and 161,792 bytes in
0.037818958 seconds at 36,634,624-byte peak RSS with 4,465 output bytes and
zero network or real/protected operations.

## Requested One-Shot Execution

Only after the decision-only commit is pushed and both CI jobs pass may one
invocation:

1. verify the exact contract, inventory, implementation registry, decision,
   commits, CI identifiers, tracked hashes, clean worktree, and ordinal one;
2. create one private Git-ignored consumed marker before the first request;
3. issue exactly 128 sequential HTTPS GETs in canonical inventory order;
4. reject redirect, retry, substitution, compression, chunking, URL drift,
   non-200 status, wrong Content-Length, wrong ETag, or bodies over 4,096 bytes;
5. read exactly 161,792 body bytes total, compute one SHA-256 per body, and
   strictly parse each VHDR declaration once in memory;
6. validate DataFile and MarkerFile only as inert basenames without constructing
   or touching a sibling path;
7. discard each raw body before the next request;
8. aggregate signatures and apply frozen route `IACKDH-R0` through
   `IACKDH-R5`; and
9. create one bounded aggregate ledger and stop.

There is no fallback, alternate alias map, parser amendment, retry, or rerun.
If any gate fails after the consumed marker, the one execution is consumed.

## Resource Caps

| Resource | Maximum |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time | 120 seconds |
| Peak RSS | 268,435,456 bytes |
| HTTPS requests | 128 |
| Expected VHDR body bytes | 161,792 |
| Network body bytes | 1,048,576 |
| Bytes read per VHDR | 4,096 |
| Incremental disk | 2,097,152 bytes |
| Public output | 1,048,576 bytes |
| Minimum free disk | 2,147,483,648 bytes |
| Retries / reruns | 0 / 0 |

No dependency installation, metadata-list refresh, provider, model, or
numerical workload is requested.

## Explicitly Not Authorized

- statting, resolving, hashing, opening, moving, deleting, or otherwise using
  the retained local IACKD bundle;
- any VMRK, EEG, channels TSV, events TSV, coordsystem, electrodes, ball, Leap,
  derivative, CURRY, participant table, sibling, or other object;
- signal samples, markers, events, trajectories, labels, targets, caches,
  splits, features, models, checkpoints, fitting, inference, predictions,
  freezes, target delivery, or scoring;
- S20, S21, S24, S25, SpanishBCBL, PhysioNet, raw FIF, or MAT access;
- additional object URLs, metadata refreshes, substitutions, redirects,
  retries, resumes, restarts, or reruns;
- package installation, MNE or another neural reader, foundation or language
  models, providers, RW3, streams, devices, or hardware;
- individual protected output, upload, publication, release, or patent/device
  implementation; and
- any scientific, decoding, neural, brain-specific, generalization, real-time,
  portable, home-use, assistive, or clinical claim upgrade.

## Outcome Meaning

- `IACKDH-R0`: a source, response, parser, resource, output, or completeness
  gate failed.
- `IACKDH-R1`: all headers share one signature and the old exact count and four
  canonical names are present, contradicting the consumed failure assumption.
- `IACKDH-R2`: a stable count-only mismatch was measured.
- `IACKDH-R3`: a stable exact-name-only mismatch was measured.
- `IACKDH-R4`: both count and exact-name assumptions mismatch.
- `IACKDH-R5`: more than one header signature exists across runs.

Every route is a file-contract diagnosis. None is a neural or decoding result,
and none reopens, rescues, or reinterprets IACKD-1. A future corrected neural
experiment would require a new prospective contract and another Tier C gate.

## Current State

Every execution authorization flag in the machine request is false. Preparing
this packet made zero network requests, real VHDR reads, local IACKD path
operations, sibling operations, sample/event/trajectory/target reads, model
runs, scores, retries, reruns, releases, or claim changes.

Engineering capability requested: one exact, resource-bounded, sibling-blind
public-header audit can replace a failed hard-coded channel assumption with a
measured aggregate compatibility diagnosis.

Scientific claim not established by this request: this all-false packet is not
data or a result and establishes no neural effect, action decoding,
brain-specific origin, generalization, real-time operation, hardware
capability, assistive benefit, or clinical use.
