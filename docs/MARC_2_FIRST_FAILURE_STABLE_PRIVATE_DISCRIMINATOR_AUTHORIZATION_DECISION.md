# MARC2-VR18P First-Failure-Stable Private Discriminator Authorization Decision

Date: 2026-08-21

Lane: `MARC2-VR18P`

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both required CI jobs are green**

Machine decision:
`registries/marc2_first_failure_stable_private_discriminator_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `MARC2-VR18P` as the sole active Tier C packet and
reported its exact request commit, proof-closeout commit, CI run, two green
jobs, two-stage order, and fresh-decision boundary, the maintainer's next
message was exactly:

```text
continue
```

The machine decision preserves those actual eight UTF-8 bytes and their
SHA-256. It does not fabricate the packet's long scope as a maintainer
utterance. Under the approved Research Autonomy Charter short-form rule, this
message binds only the unchanged, remotely green `MARC2-VR18P` packet by
reference and cannot expand it by inference.

## Green Packet Bound By This Decision

```text
request commit:       521f1de1f3141f3f970710447d072608253c2cca
request CI:           32474183647
request Base job:     96747013517
request Optional job: 96747013910
proof commit:         ea5b4c70f2a00db225351d3eabc7821ff3f48678
proof CI:             32474864890
proof Base job:       96749006185
proof Optional job:   96749006544
```

Both jobs passed for both exact commits. The proof closeout binds the three
unchanged request artifacts totaling 32,886 bytes. This decision binds those
artifacts plus the three proof artifacts, six files totaling 43,769 bytes.
The unrelated untracked tracker inspection NDJSON was not opened, modified,
staged, or deleted.

## Delayed Effect

This decision does not become effective merely because these files exist.
Before wrapper implementation, readiness, output-root work, or private-source
path access, this exact decision must pass focused local checks, be committed,
pushed, and pass both required remote CI jobs.

Recording this decision performs zero `.codex_work`, private-source,
readiness, output-root, archive, neural, target, model, score, network,
hardware, release, or scientific-claim operation.

## Authorized Sequence After Green Decision

### Stage 1: generated/mock fixed-path wrapper

After this decision is remotely green, one additive standard-library wrapper
may be implemented and qualified using only invocation-created generated
fixtures, injected machine samples, mocked no-follow facts, and temporary
output roots.

The wrapper must expose fixed `plan`, `qualify`, `inspect`, and proof-gated
`execute` surfaces. It may expose no generic source, output, path, URL,
threshold, cap, route, retry, resume, fallback, or substitution override. It
must not touch any `.codex_work` path during qualification or import, call,
patch, copy, modify, or inspect consumed VR15P/VR16P or parked VR17A/VR17B
state.

Qualification must replay the five registered residual cases in two orders
and two exact replays, making exactly one VR16A call per path. The exact VR17C
map may be consulted once on each failure path and zero times on each success
path. All 20 paths and at least 80 direct refusal mutations must pass under the
frozen caps, with zero retained generated output and every private or
scientific counter at zero.

The exact implementation must then be committed, pushed, and pass both remote
jobs. A separate proof-only closeout must also be committed, pushed, and pass
both jobs before Stage 2.

### Stage 2: one target-free structural discriminator

Only after the exact Stage 1 implementation and proof closeout are remotely
green may one command:

1. validate every exact proof and the one-thread environment;
2. obtain three consecutive passing machine-readiness samples;
3. write one fresh mode-`0600` certificate at the fixed VR18P path;
4. require the fixed output root to be absent and reject symlinks or aliases;
5. no-follow preflight only the registered target-free source;
6. write one mode-`0600` consumed marker immediately before content open;
7. read, hash, and strict-parse exactly 418,755 bytes once;
8. call the exact green VR16A adapter once without source mutation;
9. consult the frozen VR17C route map at most once on failure;
10. on R1 only, write one mode-`0600` source-exact private cohort manifest; and
11. write one aggregate-safe mode-`0644` R1-R8 report.

Every route consumes the one invocation. No retry, rerun, resume, repair,
fallback, substitution, private reinspection, or post-result amendment is
authorized.

## Fixed Route Contract

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR18P-R1` | exact adapter accepted and froze one bounded structural cohort |
| `MARC2VR18P-R2` | readiness, fixed-path, or output precondition refused |
| `MARC2VR18P-R3` | source identity or strict structural envelope refused |
| `MARC2VR18P-R4` | generated-qualified core task or identity class |
| `MARC2VR18P-R5` | generated-qualified companion run spelling class |
| `MARC2VR18P-R6` | generated-qualified normalized companion collision class |
| `MARC2VR18P-R7` | generated-qualified incomplete companion set class |
| `MARC2VR18P-R8` | unknown, privacy, deterministic-output, or resource refusal |

R1 alone may freeze a maximal contiguous 12-19-subject structural cohort with
72-114 selected run bundles, 288-456 source-exact core members, equal fit and
held-out counts, and no more than 8 GiB reserved. R1 may make a separate FW2
preregistration eligible; it does not authorize FW2 or CIL1.

## Fixed Paths And Resources

```text
readiness certificate: .codex_work/marc2_machine_readiness/vr18p/readiness.v0.json
output root:           .codex_work/marc2_first_failure_stable_private_discriminator/v0
private source:        .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
source bytes:          418,755 exactly once
source SHA-256:        2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
CPU / workers / jobs:  1 / 1 / 1
generated runtime:     <= 60 seconds
private runtime:       <= 650 seconds
peak RSS:              < 256 MiB
minimum free disk:     >= 15 GiB
combined output:       <= 2 MiB
network/new payload:   0 / 0 bytes
archive/signal/target: 0 / 0 / 0 bytes
retry/rerun/resume:    0 / 0 / 0
```

Public output may contain only aggregate route, counts, hashes, byte totals,
resource measurements, warnings, unavailable fields, zero counters, and claim
boundaries. It may not contain member names, source paths, participant
identity, sessions, runs, tasks, companions, offsets, CRCs, rows, reasons,
exception text, labels, targets, predictions, or scores.

## Explicitly Not Authorized

This decision does not authorize implementation before its own remote green
proof; Stage 2 before exact Stage 1 and closeout proof; consumed or parked
VR15P/VR16P/VR17A/VR17B access; another source, path, project, participant,
session, run, or dataset; network or download; archive members; EEG/MEG
samples, events, channels, geometry, quality, labels, targets, or outcomes;
derivatives, caches, features, or NeuroTokens; training, inference, prediction,
scoring, tuning, or language models; FW2, CIL1, RW3, streams, devices,
hardware, release, publication, or any scientific or clinical claim upgrade.

## Next Gate

Commit, push, and green this exact decision. Then implement and generated-
qualify Stage 1. Only after that implementation and its proof-only closeout
are remotely green may the single registered structural discriminator run
once.

Engineering capability authorized after green decision: one proven fixed-path
wrapper may either freeze a bounded source-exact target-free cohort or retain
one aggregate generated-qualified first-failure class.

Scientific claim not established: this decision is not neural data or a
result and establishes no neural effect, decoding performance, language
decoding, live decoding, or thought-to-text capability.
