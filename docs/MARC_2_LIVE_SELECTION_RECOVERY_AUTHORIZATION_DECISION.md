# MARC2-FW1C Live Selection Recovery Authorization Decision

Date: 2026-08-16

Lane: `MARC2-FW1C`

Status: **Packet-bound short-form authorization recorded; ineffective until
this decision is committed, pushed, and both required CI jobs are green; no
private path, output root, archive, payload, neural, target, model, or score
operation occurred**

Machine decision:
`registries/marc2_live_selection_recovery_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `MARC2-FW1C` as the sole active Tier C packet, named its
exact commit, CI run, two required jobs, packet/request hashes, two-stage scope,
and fresh-decision boundary, the maintainer's next message was exactly:

```text
continue
```

The decision record preserves those actual eight UTF-8 bytes and their
SHA-256. It does not fabricate the packet's long scope as a maintainer
utterance. Under the approved Research Autonomy Charter, this unambiguous fresh
short form binds only the immutable remotely green `MARC2-FW1C` packet by
reference.

## Green Request Bound By This Decision

```text
request commit:       7804c3e87a26574a93c5dfda831e44e9d06806ca
CI run:               31769518851
Base Python job:      94672387003
Optional Neuro job:  94672386941
packet SHA-256:       f517f0b4d88f1adcb181e1f8ae1896747f45e416497e269aea80c492614bd84d
request SHA-256:      2dfd45c9e9b607f6f7f442e60c6a359b4d5f550d07f4cb4b8a474a8469d147c0
```

The request commit and local branch HEAD matched before this decision was
written. GitHub reported both jobs successful. The only unrelated worktree
entry was the pre-existing untracked tracker inspection sidecar; it was not
opened, modified, staged, or deleted.

## Delayed Effect

This decision is not effective merely because this file exists. Before any
wrapper implementation or retained-path operation, the exact decision must:

1. pass its focused and complete local verification;
2. be committed as one coherent decision-only milestone;
3. be pushed on the current branch; and
4. pass both required remote CI jobs.

Until all four conditions hold, implementation and private access remain
closed.

## Authorized Sequence After Green Decision

### Stage 1: generated/mock wrapper

After this exact decision is remotely green, one additive standard-library
wrapper may be implemented and qualified:

```text
neurodecodekit.datasets.marc2_freewill_private_selection_recovery
```

The wrapper may use only generated manifests, mocked filesystem facts,
injected readers, and invocation-created temporary output during development.
It must import the exact green shared validator and frozen pure selector. It
must not import, call, edit, or expose the consumed `MARC2-FW1A` wrapper or its
v0 output root.

The wrapper must preserve two distinct proof records:

1. a native implementation registry with `lane_id: MARC2-FW1C`; and
2. a distinct FW1B-format proof certificate passed to the exact
   `validate_implementation_record` symbol.

The proof certificate's expected and observed envelopes must bind the future
wrapper commit and actual future HEAD, not the older shared-validator HEAD. It
must bind the packet-bound decision, wrapper module, native registry, tests,
shared validator, and frozen selector without a self-hash or copied validator.

Generated qualification must exercise all 90 frozen mutations:

```text
proof-record mutations: 32
selector mutations:     40
wrapper mutations:      18
total:                   90
```

The actual native registry must pass its own loader, the actual proof
certificate must pass the exact shared validator, and canonical replay must be
byte-identical. Every mutation must refuse before a retained-path operation.

The exact wrapper implementation, tests, native registry, certificate, and
generated qualification must then be committed, pushed, and pass both remote
jobs. Stage 1 does not access the retained manifest.

### Stage 2: one target-free structural selection

Only after the exact wrapper is remotely green may one no-retry invocation use
the registered structural source:

```text
.codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
```

Bound identity:

```text
bytes:          418,755
mode:           0600
SHA-256:        2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
schema:         neurodecodekit.marc1_central_directory_private_manifest
schema version: 0.1.0
entries:        1,227
```

The new output root is exactly:

```text
.codex_work/marc2_freewill_prefix/live_selection_recovery_v1
```

The consumed v0 root remains forbidden. The future invocation must apply the
packet's proof, machine, no-follow, owner/mode/size, open/fstat, hash, strict
JSON, privacy, maximal-prefix, output, and consumption gates in their frozen
order. It may perform one content open, one sequential read, one SHA-256 pass,
one strict parse, and one target-free selection. It may write at most one
mode-`0600` consumed marker, one mode-`0600` private selection manifest, and one
aggregate report. Every route consumes the invocation.

## Frozen Selection And Resource Boundary

The target-free rule remains unchanged: 19 ranked eligible participants,
minimum 12, maximum 19, `ses-01` fit, `ses-02` held out, six run bundles and 24
members per participant, maximal contiguous prefix, first non-fitting stop, and
an 8 GiB reservation ceiling. Targets, labels, events, quality, signals,
channels, outcomes, archive members, and local headers cannot influence the
selection.

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
runtime:                                 <= 30 seconds per registered invocation
peak RSS:                                <= 256 MiB
private input opens / bytes:             1 / 418,755 exact
network requests / bytes:                0 / 0
archive local-header/member bytes:       0
combined output:                         <= 2 MiB
incremental disk:                        <= 4 MiB
minimum free disk:                       >= 15 GiB
selected future reservation:             <= 8 GiB
retry / rerun / resume:                  0 / 0 / 0
```

The 8 GiB number is accounting for a possible later payload packet. This
decision neither acquires nor reads those payload bytes.

## Explicitly Not Authorized

This decision does not authorize:

- implementation before this decision is remotely green;
- private access before the exact wrapper is remotely green;
- repair, retry, import, reuse, or output access for consumed `MARC2-FW1A`;
- another path, sibling, directory listing, URL, network request, or download;
- archive local headers, members, payloads, extraction, or range requests;
- EEG samples, signals, events, channels, geometry, targets, labels, quality,
  responses, trials, or outcomes;
- derivatives, caches, features, split payloads, or NeuroTokens;
- training, checkpoints, inference, predictions, freezes, target delivery, or
  scoring;
- `MARC2-FW2`, `MARC2-CIL1`, `MARC2-ORTH1`, or `NDK-LANG1`;
- providers, language models, RW3, streams, devices, or hardware;
- retries, reruns, resumes, substitutions, fallbacks, or amendments;
- pre-existing cleanup, overwrite, move, rename, or deletion;
- operation on another project;
- release, publication, participant-level output, or scientific claim upgrade;
  or
- neural-effect, decoding, language, thought-to-text, real-time, portable,
  home-use, assistive, medical, or clinical claims.

## Current Counters

At decision recording, one GitHub CI verification was performed. Every private
path, private byte, output-root, archive, payload, neural, target, derivative,
model, score, provider, hardware, retry, cleanup, release, and claim counter is
zero. End-to-end latency was not measured.

## Next Gate

Verify this decision, commit it, push it, and require both CI jobs green. Only
then may Stage 1 generated/mock wrapper implementation begin. Stage 2 remains
closed until the exact wrapper implementation is separately committed, pushed,
and remotely green.

## Claim Boundary

Engineering capability authorized after green decision: one exact additive
wrapper may be generated-qualified and, only after its own green proof, convert
one exact private structural manifest into a deterministic storage-bounded
target-free selection.

Scientific claim not established: this decision is not neural data or a result
and establishes no neural effect, decoding accuracy, brain-specific origin,
language decoding, or thought-to-text capability.
