# MARC2-FW1C Live Selection Recovery Authorization Packet

Date: 2026-08-14

Status: **All authorization flags false; packet prepared but not authorized;
no retained path, private manifest, archive, payload, neural, target, model, or
score operation occurred**

Machine request:
`registries/marc2_live_selection_recovery_authorization_request.v0.json`

## Purpose

Request one prospective Tier C sequence that may, after separate green proof at
every stage, use the new `MARC2-FW1B` shared validator to guard one replacement
target-free private-manifest selection.

This packet grants nothing. It records a possible future authority. A fresh
unambiguous maintainer instruction is effective only after this exact packet is
committed, pushed, both CI jobs are green, and Codex identifies it as the sole
active Tier C gate.

## Green Evidence Anchor

The generated-only proof validator is exact commit:

```text
implementation commit: 6f613b339dfe8a7bd2df69a48c1ac32b72554f7b
CI run:               31768593977
Base Python job:      94669566174
Optional Neuro job:  94669566187
implementation SHA:  2b1ff6c9d41d7bae14686cbf16a2aa129d702842622ca990468a3263f68e66b6
```

That commit passed both required jobs before this packet was prepared. Its
fresh generated result validated a complete 15-field record twice and rejected
32 malformed records through the exact public function
`validate_implementation_record`. It accessed zero private or real bytes.

## Why This Is A New Lane

`MARC2-FW1A` is consumed at `MARC2FWS-F00`. Its registry omitted `lane_id`, and
its sole invocation stopped before every retained-path operation. The old
implementation, output root, and execution cannot be repaired, retried,
resumed, imported, or reused.

`MARC2-FW1B` is generated-only and has private execution limit zero. It proves
the shared proof-record interface but does not itself implement a private
selector.

The proposed live-recovery lane is therefore separately named `MARC2-FW1C`.

## Proposed Sequence

### Stage 1: additive generated/mock wrapper

Only after a separate packet-bound decision is committed, pushed, and both
jobs are green, implement a new standard-library module:

```text
neurodecodekit.datasets.marc2_freewill_private_selection_recovery
```

It may import:

- `marc2_proof_record_recovery` for the exact shared validator; and
- `marc2_freewill_prefix_selection` for the frozen pure selection rule.

It must not import, call, edit, or expose the consumed
`marc2_freewill_private_selection` module or its output root.

Development and qualification may use only generated manifests, mocked
filesystem facts, injected readers, and invocation-created temporary output.
No retained path operation is permitted during Stage 1.

### Stage 1 proof certificate

A later wrapper commit cannot claim that repository HEAD still equals the older
`MARC2-FW1B` implementation commit. To preserve honest proof semantics, Stage
1 must create two separate records:

1. a native `MARC2-FW1C` wrapper implementation registry with top-level
   `lane_id: MARC2-FW1C`; and
2. a separate FW1B-format proof certificate supplied as the hashed record input
   to `validate_implementation_record`.

The proof certificate must bind the new wrapper module, native registry,
generated tests, packet-bound decision, shared validator source, and frozen
selector. Its expected and observed proof envelopes must both describe the new
wrapper commit, CI run, job IDs, certificate hash, actual wrapper HEAD, clean
tracked state, and the green decision ancestor.

The wrapper's generated qualification must prove:

- the exact shared validator accepts that certificate at the wrapper HEAD;
- its own native registry loader accepts the actual `MARC2-FW1C` registry;
- both required `lane_id` values are present and exact;
- changing either lane, record hash, commit, CI/job, HEAD, closure, or artifact
  hash refuses before every filesystem or source operation; and
- no copied, forked, aliased, or weaker proof validator is called.

The exact wrapper commit, native registry, and proof certificate must then pass
both remote jobs before Stage 2.

### Stage 2: one private-manifest selection

Only after the exact wrapper is remotely green, permit one no-retry invocation
against one literal retained file:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

Committed expected identity:

```text
bytes:          418,755 exact
mode:           0600 exact
SHA-256:        2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
schema:         neurodecodekit.marc1_central_directory_private_manifest
schema version: 0.1.0
entries:        1,227 exact
```

Preparing this packet does not stat, resolve, open, hash, or parse that path.

The future executor must reject `resolve`, globbing, directory listing, sibling
inspection, a symlink component, a symlink final path, a non-regular file,
wrong owner or mode, and any alternate path. It may perform one no-follow
content open, one `fstat` identity reconciliation, one bounded sequential read,
one SHA-256 pass, and one strict JSON parse.

## Proof And Machine Order

Before the new output root or retained path is checked, a future invocation
must:

1. validate the packet-bound green decision;
2. call the exact shared validator on the FW1B-format wrapper certificate;
3. validate the native `MARC2-FW1C` registry;
4. require exact wrapper commit, CI, both job IDs, registry hash, certificate
   hash, clean HEAD, and decision ancestry;
5. require one CPU thread, one worker, and one numerical job;
6. require normalized one-minute load below `1.0` per logical CPU;
7. require pre-consumption peak RSS below 256 MiB; and
8. require at least 15 GiB free disk.

Any proof or machine refusal occurs before the retained path.

The exact new output root is:

```text
.codex_work/marc2_freewill_prefix/live_selection_recovery_v1
```

It must be absent, non-symlinked, and distinct from the consumed v0 root. The
packet does not stat, create, reserve, or inspect it.

After all proof, machine, output, and no-follow path preflight passes, but before
the private content open, the executor must atomically write one mode-`0600`
consumed marker. Every subsequent route is final.

## Frozen Selection Rule

If and only if source identity and schema pass, apply the unchanged green
target-free rule:

- 19 public eligible participants in the frozen rank;
- `ses-01` fit and `ses-02` held-out;
- first three numeric complete run bundles per session;
- four declared companions per bundle;
- six bundles and 24 members per participant;
- future reservation equals compressed size plus local-header, UTF-8-name, and
  maximum-extra-field allowance;
- at least 12 participants;
- maximal contiguous ranked prefix up to 19 under 8 GiB; and
- stop at the first participant that does not fit.

No skip, substitute, backfill, seed change, cap change, target, label, event,
quality, signal, channel, trial, outcome, member payload, or local-header input
is allowed.

## Output Contract

At most three files may exist in the new root:

1. mode-`0600` consumed marker;
2. mode-`0600` private selection manifest; and
3. aggregate public report.

The private result may retain selected structural rows. The aggregate result
may retain public participant IDs, counts, reservation totals, hashes,
warnings, unavailable fields, resources, counters, and route. It may not expose
a member name, offset, CRC, private row, retained path, source body, sibling,
or private output path. Aggregate inspection must reject the private schema.

## Future Routes

| Route | Meaning |
|---|---|
| `MARC2FWC-F00` | packet, decision, shared certificate, native registry, artifact, HEAD, or green proof differs |
| `MARC2FWC-F01` | machine, load, disk, output, path, marker, symlink, mode, or no-follow preflight differs |
| `MARC2FWC-F02` | source size, hash, open/fstat identity, JSON, schema, field, or count differs |
| `MARC2FWC-F03` | ZIP declaration, BIDS identity, companion, or bundle differs |
| `MARC2FWC-F04` | eligibility, rank, participant, run, session, split, or prefix differs |
| `MARC2FWC-F05` | floor, cap, reservation, maximal-prefix, or selected count differs |
| `MARC2FWC-F06` | privacy, output, mode, overwrite, cap, resource, cleanup, replay, or forbidden operation differs |
| `MARC2FWC-R1` | one exact target-free private selection completes |

Every route consumes the invocation. There is no retry, rerun, resume, repair,
fallback, path substitution, or second open.

## Resource Ceiling

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
runtime:                                 <= 30 seconds
peak RSS:                                <= 256 MiB
private input opens / bytes:             1 / 418,755 exact
network requests / bytes:                0 / 0
archive local-header/member bytes:       0
combined output:                         <= 2 MiB
incremental disk:                        <= 4 MiB
minimum free disk:                       >= 15 GiB
selected future reservation:             <= 8 GiB
```

The 8 GiB number is reservation accounting, not acquired or generated bytes.

## Explicit Exclusions

This packet does not authorize:

- wrapper implementation or qualification before a green decision;
- any retained-path operation before a green wrapper;
- the consumed FW1A module, output root, marker, report, or execution;
- an alternate path, sibling, directory listing, network request, or download;
- archive local headers, members, payloads, extraction, or range requests;
- EEG samples, signals, events, channels, geometry, targets, labels, quality,
  onset, responses, trials, or outcomes;
- derivatives, caches, feature arrays, split payloads, or NeuroTokens;
- training, parameter updates, checkpoints, inference, predictions, freezes,
  target delivery, or scoring;
- `MARC2-FW2`, `MARC2-CIL1`, `MARC2-ORTH1`, or `NDK-LANG1`;
- providers, language models, RW3, streams, devices, or hardware;
- retries, reruns, resumes, repairs, substitutions, fallbacks, or old roots;
- publication, release, or participant-level protected output; or
- neural-effect, decoding, language, thought-to-text, real-time, portable,
  home-use, assistive, medical, or clinical claim upgrades.

## Current Authority

Every authorization flag is false. Every path, private, real, network, archive,
payload, neural, target, model, score, provider, hardware, release, retry, and
claim counter is zero. The proposed wrapper, proof certificate, output root,
private selection, and result do not exist.

## Decision Gate

After this exact packet is committed, pushed, and both required jobs are green,
Codex may identify it as the sole active Tier C packet. A fresh maintainer
`continue`, `approve`, or equivalent unambiguous instruction may bind it by
reference under the approved Research Autonomy Charter. The separate decision
must quote the actual words and bind the immutable packet commit, packet hash,
CI run, both job IDs, green implementation proof, source identity, new output
root, caps, exclusions, and claim ceiling.

The `continue` that initiated the generated recovery and every earlier message
are not retroactive authority for this packet.

## Claim Boundary

Engineering capability requested: one newly proven wrapper may convert one
exact private structural manifest into a deterministic storage-bounded
target-free selection through the shared proof validator.

Scientific claim not established: this all-false packet reads no human neural
data and establishes no neural effect, decoding accuracy, language decoding,
or thought-to-text capability.
