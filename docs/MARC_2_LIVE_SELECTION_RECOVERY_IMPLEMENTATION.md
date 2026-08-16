# MARC2-FW1C Live Selection Recovery Implementation

Date: 2026-08-16

Lane: `MARC2-FW1C`

Status: **Generated/mock wrapper qualified locally; exact implementation must
be committed, pushed, and pass both required CI jobs before the one registered
private structural selection may begin**

Machine records:

- `registries/marc2_live_selection_recovery_implementation.v0.json`
- `registries/marc2_live_selection_recovery_proof_certificate.v0.json`

## What Was Added

The additive standard-library module
`neurodecodekit.datasets.marc2_freewill_private_selection_recovery` implements
four fixed commands:

```text
plan -> qualify -> inspect -> execute
```

`execute` is present for the later packet-bound stage, but it refuses unless
the caller supplies exact remote-green implementation evidence. Development
and qualification performed no operation on the registered retained path or
live output root.

The module imports only:

- the frozen pure `marc2_freewill_prefix_selection` rule; and
- the exact public `validate_implementation_record` implementation from
  `marc2_proof_record_recovery`.

It does not import, call, edit, or expose the consumed FW1A wrapper or its v0
output root.

## Two-Record Proof Chain

The native implementation registry has top-level `lane_id: MARC2-FW1C`. A
separate certificate retains the strict 15-field FW1B format and top-level
`lane_id: MARC2-FW1B` required by the already-green shared validator.

The certificate binds nine tracked artifacts:

- shared validator source and contract;
- recovery wrapper source and native registry;
- both recovery test modules;
- packet-bound decision registry and document; and
- frozen selector source.

The native registry does not hash the certificate, so there is no circular
self-hash. Future green evidence binds both independent SHA-256 values. The
shared proof envelope must then bind the exact future implementation commit,
CI run, both job IDs, certificate hash, actual HEAD, clean tracked state, and
green-decision ancestry.

## Refusal Matrix

One final generated qualification passed all 90 frozen cases:

| Layer | Passed | Purpose |
|---|---:|---|
| FW1B proof record | 32/32 | malformed identity, binding, qualification, authority, closure, and remote-proof records |
| Frozen selector | 40/40 | source, bundle, rank, split, reservation, privacy, and boundary mutations |
| FW1C wrapper | 18/18 | Git proof, machine, path, no-follow, strict JSON, output, replay, and forbidden-operation mutations |
| **Total** | **90/90** | every mutation refused before a registered private-source operation |

The shared validator was called twice on the exact certificate with identical
summaries, then once for each of its 32 registered mutations. No copied,
forked, aliased, or fallback validator exists.

## Deterministic Generated Result

The final exact-artifact qualification selected the same generated structural
prefix as the frozen selector:

```text
participants:                 16
run bundles:                  96
private structural rows:      384
future reservation bytes:     8,105,207,776
reservation ceiling:          8,589,934,592
generated input bytes:        846,712
combined temporary output:    298,059
runtime:                      0.3741613749953103 seconds
peak RSS:                     38,666,240 bytes
CPU threads/workers/jobs:     1 / 1 / 1
producer causal:              not applicable, metadata only
end-to-end latency measured:  no
```

Generated aggregate report SHA-256:

```text
d84ee84fb420a0e65ba3b182198323208c0295725c50993477438875668fd440
```

That temporary report and private generated selection were inspected and then
removed. They are not committed artifacts.

Current proof identities:

```text
native FW1C registry SHA-256:
dcd95616ad65b1b44b13f3116e6a63ea77d958705f4e9bcfad12d8b74a841edc

distinct FW1B certificate SHA-256:
06668731cdb507373053bce5fe652366591f7fb83a7a0bd48f4fcd82f2610e82
```

## Access And Resource Ledger

All implementation and generated-qualification counters are zero for:

- registered private path checks, lstat, opens, reads, bytes, hashes, or parse;
- registered output-root operations or consumed markers;
- real participant or member selection;
- network or archive local-header/member access;
- signal, event, target, label, quality, onset, or channel access;
- derivative, cache, model, training, inference, prediction, freeze, delivery,
  or scoring operations;
- provider, language-model, stream, device, or hardware operations;
- old consumed-root operations, retry, rerun, resume, or claim upgrade; and
- operations on another project.

The generated result reserves 8.105 GB for a possible later acquisition
packet; it does not acquire, read, or write those bytes.

## Verification

```text
focused recovery tests:          44
complete dependency-light:       3,214 passed / 204 skipped
optional A-M process:             2,772 passed / 28 skipped
optional N-Z process:               513 passed / 7 skipped
optional total:                   3,285 passed / 35 skipped
Ruff:                             passed
compileall:                       passed
strict registry JSON files:       218 passed
CLI plan/help/qualify/inspect:     passed
```

The optional suite was split into fresh A-M and N-Z processes to avoid
cross-test RSS accumulation. The A-M shard used the established local
forkserver permission for one legacy timing-worker test. No test expanded the
registered private or real-data authority.

## Next Gate

Commit and push this exact implementation, then require both Base Python and
Optional Neuro Readers jobs to pass. Only that exact remote-green proof opens
the packet's Stage 2 sequence: one no-retry target-free structural-manifest
selection into the new v1 output root.

Until then, do not stat, resolve, open, hash, or parse the registered retained
manifest and do not create or inspect the live output root. The consumed v0
root remains forbidden throughout.

Even after a successful Stage 2 selection, archive members, payloads, EEG,
events, targets, models, scores, and `MARC2-FW2` remain closed and require a
separately named future packet.

## Claim Boundary

Engineering capability added: a native FW1C wrapper and distinct FW1B proof
certificate now guard a deterministic, storage-bounded, target-free structural
selection through one exact shared validator.

Scientific claim not established: generated structural metadata contain no
human neural signal, target, prediction, or score and establish no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
