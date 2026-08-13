# MARC2-FW1A Private Selection Authorization Packet

Date: 2026-08-13

Status: **All authorization flags false; request prepared but not authorized;
no retained path, private inventory, archive, payload, signal, event, target,
model, prediction, score, or provider operation occurred**

Machine request:
`registries/marc2_freewill_private_selection_authorization_request.v0.json`

## Purpose

Request one narrowly bounded Tier C sequence that converts the remotely green
generated `MARC2-FW1` selector into one proof-gated private-inventory selector.
The sequence stops after target-free member selection and aggregate byte
accounting. It does not request or open an archive member.

The packet is intentionally all false. It records a possible future authority;
it grants none. Only a fresh unambiguous maintainer instruction after this exact
packet is committed, pushed, remotely green, and identified as the sole active
Tier C gate may be quoted in a separate decision artifact.

## Green Evidence Anchor

The one registered generated closeout is exact commit
`a9a759aa5626a41812afe546f03aa324db7a534e`. It passed Base Python job
`94378074196` and Optional Neuro Readers job `94378074181` in CI
`31678418324` before this packet was prepared.

The result is consumed at `MARC2FWG-R1` with:

```text
generated selected participants:     16
generated selected bundles:          96
generated selected members:          384
generated reservation bytes:         8,105,207,776
storage boundaries:                  4 / 4
mutation refusals:                    40 / 40
retained private or real operations: 0
```

That result proves the generated interface only. It does not authorize or
predict the real selected count.

## Proposed Authorization Sequence

### Stage 1: additive wrapper implementation

Only after a separate packet-bound authorization decision is committed,
pushed, and both required CI jobs are green, implement a new standard-library
wrapper around the frozen selection logic.

The wrapper may be developed and tested only with generated manifest bodies,
mocked filesystem facts, temporary directories, and injected readers. It must
not import, call, modify, or expose the consumed `MARC1-P1A` executor. It must
not contain the retained path as a default CLI argument or provide a generic
path override.

The future module may expose exactly:

```text
plan
qualify --output-dir <new generated directory>
inspect <aggregate report>
execute --output-root <exact registered root> --proof-commit <hash> --proof-ci <id>
```

`execute` must reject every output root except the exact registered one and
must remain proof-disabled until the wrapper's exact commit has passed both
remote jobs. No participant, seed, cap, split, source path, URL, credential,
member, or model override may exist.

Generated wrapper qualification must cover the inherited 40 selector
mutations plus exactly 18 wrapper-specific refusals:

1. implementation proof commit mismatch;
2. implementation proof CI or job mismatch;
3. dirty tracked worktree or HEAD mismatch;
4. output root differs;
5. output root exists;
6. symlink output parent or destination;
7. insufficient free disk;
8. load, worker, thread, runtime, or RSS preflight failure;
9. retained path component symlink;
10. retained final path symlink or non-regular file;
11. retained owner-mode mismatch;
12. retained size mismatch;
13. retained SHA-256 mismatch;
14. no-follow open/fstat identity race;
15. strict JSON duplicate, encoding, control, or schema failure;
16. private/aggregate field leak or schema confusion;
17. output cap, mode, overwrite, atomic-write, or cleanup failure; and
18. retry, rerun, resume, old-root, network, archive, or payload attempt.

The wrapper implementation must be committed, pushed, and remotely green
before any operation on the registered retained path.

### Stage 2: one private-inventory execution

Only after the exact wrapper is remotely green, permit one no-retry execution
against this one literal path:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

Expected identity:

```text
file bytes:   418,755 exact
file mode:    0600 exact
SHA-256:      2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
schema:       neurodecodekit.marc1_central_directory_private_manifest
version:      0.1.0
entries:      1,227 exact
```

The executor must not call `resolve`, glob, list a directory, follow a symlink,
or inspect any sibling. It may perform no-follow parent/final identity checks,
one `O_NOFOLLOW` content open, one `fstat` identity reconciliation, one
sequential read, one SHA-256 pass, and one strict JSON parse over that file.

Before that content open, it must verify:

- exact green implementation proof and clean tracked HEAD;
- one CPU thread, worker, and numerical job;
- normalized one-minute load below `1.0` per logical CPU;
- pre-consumption peak RSS below 256 MiB;
- at least 15 GiB free disk;
- the exact absent, non-symlink output root; and
- no existing consumed marker.

The exact future output root is:

```text
.codex_work/marc2_freewill_prefix/live_selection_v0
```

After preflight and before private content access, atomically write one
mode-`0600` consumed marker. The invocation is final after that marker even if
the source refuses.

## Allowed Selection Work

If source identity and schema pass, apply only the remotely green frozen rule:

- public eligibility remains the same 19 participants;
- participant rank and seed remain unchanged;
- `ses-01` fit and `ses-02` held-out remain unchanged;
- use only the first three numeric complete run bundles per session;
- require exactly four declared companions per bundle;
- compute the exact per-member future reservation;
- require at least 12 participants;
- select the maximal contiguous prefix up to 19 under 8 GiB;
- stop at the first nonfitting participant; and
- never skip, substitute, backfill, change a run, tune a cap, or use content or
  outcome information.

The selector may read only these private central-directory fields:

```text
member_name
CRC32
compression_method
general_purpose_flags
compressed_size
uncompressed_size
local_header_offset
version_made_by
external_attributes
entry_kind
ZIP64_extra_used
```

They are structural declarations, not verified member integrity. The executor
may not open a ZIP local header or trust a declared CRC as verified content.

## Output Contract

At most three files may exist in the new output root:

1. mode-`0600` consumed marker;
2. mode-`0600` private exact selection manifest; and
3. aggregate public report.

The private result may retain selected member names, offsets, declared CRCs,
sizes, split roles, and source hashes. The aggregate result may include only
the already public selected participant IDs, counts, fit/held-out totals,
reservation totals, domain-separated hashes, warnings, unavailable fields,
resource measurements, access counters, and route.

The aggregate report may not expose a member name, offset, CRC, local path,
raw private row, source body, raw header, sibling identity, or private output
path. Aggregate `inspect` must reject the private schema.

## Router

1. `MARC2FWS-F00`: packet, decision, implementation, artifact, HEAD, or green-
   proof mismatch.
2. `MARC2FWS-F01`: machine, load, disk, path, output, marker, symlink, mode, or
   no-follow preflight failure.
3. `MARC2FWS-F02`: private source size, SHA-256, open/fstat identity, strict
   JSON, schema, source, field, count, or canonical identity failure.
4. `MARC2FWS-F03`: path, ZIP declaration, BIDS identity, companion, or bundle
   failure.
5. `MARC2FWS-F04`: eligibility, rank, participant, run, session, split, or
   prefix-order failure.
6. `MARC2FWS-F05`: floor, cap, reservation, maximal-prefix, or selected-count
   failure.
7. `MARC2FWS-F06`: private/public separation, mode, overwrite, output cap,
   runtime, RSS, cleanup, replay, or forbidden-operation failure.
8. `MARC2FWS-R1`: one exact target-free private selection completes.

Every route consumes the invocation. A failure cannot be retried, resumed,
repaired, or routed around.

## Resource Ceiling

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
runtime:                                 30 sec
peak RSS:                                256 MiB
private input opens / bytes:             1 / 418,755 exact
network requests / bytes:                0 / 0
archive/local-header/member bytes:       0
combined generated/live output:          <= 2 MiB
incremental disk:                        <= 4 MiB
minimum free disk:                       >= 15 GiB
selected future reservation:             <= 8 GiB
```

The 8-GiB value is reservation accounting only. This packet authorizes zero
payload bytes.

## Explicit Exclusions

This packet does not request or imply authority for:

- any action before a separate green authorization decision;
- any private path or file other than the one exact manifest;
- a second open, retry, rerun, resume, repair, replacement, or fallback;
- an old consumed selector root, marker, report, or output;
- directory listing, sibling inspection, source probing, or network access;
- archive range requests, local headers, member payloads, downloads, or
  extraction;
- VHDR, VMRK, EEG, events, signals, channels, geometry, timing, targets,
  labels, quality, onsets, or trial outcomes;
- a cache, derivative, feature, split payload, or model input;
- training, inference, prediction, freeze, target delivery, or scoring;
- MARC2-FW2, MARC2-CIL1, MARC2-ORTH1, or NDK-LANG1;
- a provider, LLM, foundation model, RW3, stream, device, or hardware;
- publication, release, participant-level protected output, or claim upgrade;
  or
- neural-effect, decoding, language, thought-to-text, real-time, portable,
  home-use, assistive, medical, or clinical claims.

## Current Authority And Counters

Every authorization flag in the machine request is `false`. Every private,
real, network, payload, neural, target, model, scoring, hardware, release, and
claim counter is zero. Preparing this packet does not perform Stage 1 or Stage
2.

## Requested Future Decision

After this exact packet is committed, pushed, and both CI jobs are green,
Codex may identify it as the sole active Tier C gate. A fresh maintainer
`continue`, `approve`, or equivalent unambiguous instruction may then bind
this exact immutable packet by reference under the approved Research Autonomy
Charter. The separate decision must quote the maintainer's actual words and
bind the packet commit, packet SHA-256, CI run, both job IDs, source identity,
output root, caps, exclusions, and claim ceiling.

The current request to work systematically and every earlier continuation are
not retroactive authority for this packet.

## Claim Boundary

Engineering capability requested: one proof-gated wrapper can turn one exact
private ZIP-directory manifest into a deterministic, storage-bounded,
target-free selection with separate private and aggregate outputs.

Scientific claim not established by this request: an all-false packet reads no
human neural data and establishes no neural effect, decoding accuracy, language
decoding, or thought-to-text result.
