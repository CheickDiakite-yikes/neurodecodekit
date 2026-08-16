# MARC2-VR3 Variable-Domain Private Recovery Authorization Packet

Date: 2026-08-16

Lane: `MARC2-VR3`

Status: **All authorization flags false; packet prepared but not authorized;
no private path, archive, neural, target, model, or score operation occurred**

Machine request:
`registries/marc2_variable_domain_private_recovery_authorization_request.v0.json`

## Purpose

Request one prospective Tier C sequence that may connect the remotely green
`MARC2-VR2` variable-domain adapter to one exact retained structural manifest.
The purpose is to determine whether the private source passes the corrected
validation order and, if it does, derive one frozen target-free participant and
member selection without opening an archive member.

This packet grants nothing. A fresh maintainer instruction becomes effective
only after this exact packet is committed, pushed, both CI jobs are green, and
Codex identifies it as the sole active Tier C gate.

## Green Evidence

The exact generated variable-domain implementation is:

```text
implementation commit: f62a3f5b9966967c569e734552cbc3f11d009401
implementation CI:     31946112252
Base Python job:       95162220059
Optional Neuro job:   95162220159
module SHA-256:        061b893180e01116dbd962826384b4071d9e952b78b593b4743f8c301e1cbbc3
```

The one generated closeout passed at `MARC2VR2-G1`. Result commit
`7b6899b987dbd64401494ff2901ade1444f1bf60` passed Base Python job
`95164134927`, Optional Neuro Readers job `95164134941`, and CI
`31946852669`. Proof addendum
`bdd34d92eb7abe743597f1a1001e4b6a296225af` then passed Base Python job
`95164988627`, Optional Neuro Readers job `95164988647`, and CI
`31947198122` before this packet was prepared.

VR2 validated eight generated live-shaped paths spanning four distinct valid
distributions of 43 ineligible bundles. Every path validated all 1,227 rows
and 238 complete bundles before classification, dynamically reconciled exactly
195 eligible plus 43 ineligible bundles, and reproduced the same 16-subject,
96-run, 384-member, 8,105,207,776-byte target-free selection. All 58 mutations
refused. VR2 accessed zero private or neural bytes.

## Why This Is A New Lane

`MARC2-LA2` is consumed at `MARC2LAR-F02`. Its one invocation opened and read
the registered structural manifest once, then stopped when the older LA1
adapter rejected the source. No selector call or archive access followed. Its
module, proof certificate, marker, output root, invocation, and result cannot
be retried, resumed, repaired, imported, called, copied, or reused.

Artifact-only localization then found that the generated validator represented
only the 195 eligible bundles while the public source domain contains 238.
VR1 repaired the validation order, and VR2 removed VR1's constructed
`12/24/7` exclusion distribution from live acceptance. Neither generated lane
has a private path or execution surface.

The proposed recovery is therefore separately named `MARC2-VR3`.

## Proposed Sequence

### Stage 1: additive generated/mock executor

Only after a separate packet-bound decision is committed, pushed, and both
jobs are green, implement a new standard-library module:

```text
neurodecodekit.datasets.marc2_variable_domain_private_recovery
```

It may import only the exact public functions needed from:

- `marc2_proof_record_recovery` for the green shared proof validator;
- `marc2_live_domain_eligibility_adapter` for
  `adapt_live_domain_source`; and
- the unchanged selector lineage already called by the VR2 adapter.

It must not import, call, edit, copy, alias, or expose any consumed private
executor, including:

- `marc2_freewill_private_selection`;
- `marc2_freewill_private_selection_recovery`; or
- `marc2_live_schema_adapter_recovery`.

Development and qualification may use only generated manifests, mocked
no-follow filesystem facts, injected readers, and invocation-created temporary
outputs. No retained path or consumed-root operation is permitted in Stage 1.

### Stage 1 proof certificate

The implementation must create:

1. a native implementation registry with top-level `lane_id: MARC2-VR3`; and
2. a distinct proof certificate supplied to the exact shared
   `validate_implementation_record` function.

The native registry and certificate must bind the packet-bound decision, the
new module and tests, the exact VR2 contract/module/implementation/result, the
shared proof validator, the frozen selector lineage, and the consumed LA2
failure boundary. Expected and observed proof envelopes must bind the new
wrapper HEAD, clean tracked state, exact CI and job IDs, decision ancestry, and
every artifact hash.

Generated qualification must exercise at least 32 proof-certificate mutations
and 32 wrapper mutations. It must include canonical/reversed live-shaped
sources, all four VR2 exclusion profiles, exact one-call integration,
deterministic replay, malformed private-source fixtures, no-follow path
refusals, output privacy, caps, and forbidden consumed-module/root operations.
The complete repository suite must independently rerun the 58 VR2 mutations
and inherited selector tests. A copied, forked, aliased, or weaker proof
validator or adapter must refuse before every path operation.

The exact Stage 1 implementation must be committed, pushed, and pass both jobs
before Stage 2.

### Stage 2: one private structural selection

Only after the exact Stage 1 implementation is remotely green, permit one
no-retry invocation against this literal retained file:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

Committed identity inherited from the consumed integrity-checked pass:

```text
bytes:             418,755 exact
mode:              0600 exact
SHA-256:           2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
schema:            neurodecodekit.marc1_central_directory_private_manifest
schema version:    0.1.0
entries:           1,227 exact
regular entries:  1,025 exact
directory entries: 202 exact
```

Preparing this packet does not stat, resolve, list, open, hash, parse, rename,
delete, or otherwise operate on that path or inspect any sibling.

The future executor must reject path resolution, globbing, directory listing,
sibling inspection, a symlink component, a symlink final path, a non-regular
file, wrong owner or mode, and any alternate path. It may perform one
no-follow content open, one open/fstat identity reconciliation, one bounded
sequential read, one SHA-256 pass, and one strict duplicate-key-controlled JSON
parse.

## Proof And Machine Order

Before the new output root or retained path is checked, a future invocation
must:

1. validate the packet-bound green decision;
2. validate the native `MARC2-VR3` implementation registry;
3. call the exact shared validator on the distinct proof certificate;
4. require exact wrapper commit, CI, job IDs, hashes, clean HEAD, and decision
   ancestry;
5. verify the exact green VR2 adapter, contract, result, and selector hashes;
6. require one CPU thread, one worker, and one numerical job;
7. require normalized one-minute load below `1.0` per logical CPU;
8. require pre-consumption peak RSS below 256 MiB; and
9. require at least 15 GiB free disk.

Any proof or machine refusal occurs before the retained path.

The exact new output root is:

```text
.codex_work/marc2_live_domain_private_recovery/v0
```

It must be absent, non-symlinked, and distinct from every consumed MARC2 root.
This packet does not stat, create, reserve, inspect, delete, or rename any
root.

After all proof, machine, output, and no-follow path preflight passes, but
before the private content open, the executor must atomically write one
mode-`0600` consumed marker. Every later route is final.

## Frozen Processing

If and only if source identity and strict JSON pass:

1. preserve a byte-canonical digest of the parsed source object;
2. call VR2's exact public `adapt_live_domain_source` once;
3. require the source object to remain byte-canonically unchanged;
4. require source and result objects to share no mutable container;
5. validate all 1,227 rows and all 238 complete bundles before filtering;
6. require exactly 195 eligible and 43 valid ineligible bundles without an
   exact ineligible predicate split;
7. preserve the frozen public participant taxonomy and eligible session map;
8. accept only the unchanged target-free selector result returned by VR2; and
9. validate a contiguous ranked prefix of 12 to 19 participants under the
   frozen 8 GiB reservation cap.

The selector remains fixed at `ses-01` fit, `ses-02` held-out, first three
complete numeric runs per session, four companions per run, six bundles and 24
members per participant, and stop at the first nonfitting participant. No
skip, substitution, backfill, seed change, cap change, target, label, event,
quality, signal, channel, trial, outcome, archive member, or local-header input
is allowed.

The real source predicate distribution and real selection identity are not
assumed from generated qualification. They must be derived once under the
frozen rules and recorded without tuning.

## Output Contract

At most three files may exist in the new root:

1. mode-`0600` consumed marker;
2. mode-`0600` private structural selection manifest; and
3. aggregate public report.

The private result may retain selected structural rows. The aggregate result
may retain public participant IDs, aggregate predicate counts, bundle/member
counts, reservation totals, canonical hashes, warnings, unavailable fields,
resources, counters, and route. It may not expose a member name, offset, CRC,
private row, retained path, source body, sibling, or private output path.
Aggregate inspection must reject the private schema.

## Frozen Routes

| Route | Meaning |
|---|---|
| `MARC2VDR-F00` | packet, decision, certificate, registry, artifact, HEAD, ancestry, or green proof differs |
| `MARC2VDR-F01` | machine, load, disk, output, path, marker, symlink, mode, or no-follow preflight differs |
| `MARC2VDR-F02` | source size, hash, open/fstat identity, JSON, schema, field, row, or bundle validation differs |
| `MARC2VDR-F03` | VR2 classification, taxonomy, eligible map, immutability, alias, or exact-call count differs |
| `MARC2VDR-F04` | selector rank, split, bundle, prefix, cap, reservation, or determinism differs |
| `MARC2VDR-F05` | private/public output, identity leakage, overwrite, mode, or cleanup differs |
| `MARC2VDR-F06` | runtime, RSS, input/output cap, replay, consumed dependency, or forbidden operation differs |
| `MARC2VDR-R1` | one exact target-free private structural selection completes |

Every route consumes the invocation. There is no retry, rerun, resume, repair,
fallback, path substitution, adapter substitution, or second open.

## Resource Ceiling

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
runtime per stage:                       <= 30 seconds
peak RSS:                               <= 256 MiB
private input opens / bytes:             1 / 418,755 exact
network requests / bytes:                0 / 0
archive local-header/member bytes:       0
combined output:                         <= 2 MiB
incremental disk:                        <= 4 MiB
minimum free disk:                       >= 15 GiB
selected future reservation:             <= 8 GiB
```

The 8 GiB value is selection accounting only. This sequence downloads and
opens zero archive payload bytes.

## Explicit Exclusions

This packet does not authorize:

- a decision, executor, qualification, path operation, or output now;
- either consumed private manifest, executor, root, marker, report, or result;
- an alternate path, sibling, directory listing, network request, or download;
- archive local headers, members, payloads, extraction, or range requests;
- EEG samples, signals, events, channels, geometry, targets, labels, quality,
  onsets, responses, trials, or outcomes;
- derivatives, caches, feature arrays, split payloads, or NeuroTokens;
- training, parameter updates, checkpoints, inference, predictions, freezes,
  target delivery, or scoring;
- `MARC2-FW2`, `MARC2-CIL1`, `MARC2-ORTH1`, or `NDK-LANG1`;
- providers, language models, RW3, streams, devices, or hardware;
- retries, reruns, resumes, repairs, substitutions, fallbacks, cleanup of an
  existing path, or old-root operations;
- publication, release, or participant-level protected output; or
- neural-effect, decoding, language, thought-to-text, real-time, portable,
  home-use, assistive, medical, or clinical claim upgrades.

## Current Authority

Every authorization flag is false. Every path, private, network, archive,
payload, neural, target, model, score, provider, hardware, release, retry, and
claim counter is zero. The proposed executor, proof certificate, new output
root, private selection, and aggregate result do not exist.

## Decision Gate

After this exact packet is committed, pushed, and both required jobs are green,
Codex may identify it as the sole active Tier C packet. Only a fresh,
unambiguous maintainer instruction after that identification may be quoted in
a separate decision artifact. That decision must bind the packet commit and
both packet hashes and itself become remotely green before Stage 1 begins.

The current `continue to eureka` and every earlier `continue` are not
retroactive authority.

Engineering capability requested: one newly proven additive executor may
apply the exact green variable-domain adapter to one exact private structural
manifest and derive a frozen target-free selection without opening an archive
member.

Scientific claim not established: this all-false packet reads no neural data
and establishes no neural effect, decoding accuracy, language decoding, or
thought-to-text capability.
