# MARC2-VR4P Machine-Stable Private Recovery Authorization Packet

Date: 2026-08-16

Lane: `MARC2-VR4P`

Status: **All authorization fields false; no private path, expired-certificate
deletion, fresh readiness invocation, output root, marker, structural read,
cohort freeze, payload, target, model, prediction, or score is authorized**

Request:
`registries/marc2_machine_stable_private_recovery_authorization_request.v0.json`

## Decision Requested

After this exact packet is committed, pushed, and both required CI jobs are
green, request one future two-stage sequence:

1. implement and qualify an additive generated/mock-only private wrapper; and
2. only after that exact implementation is committed, pushed, and both CI jobs
   are green, run one machine-stable target-free structural cohort pass.

The current and earlier `continue` messages are not retroactive authority for
this packet. Once it is the sole named green Tier C gate, a fresh unambiguous
maintainer `continue`, `approve`, or `proceed` may bind it by reference under
the Research Autonomy Charter.

## Bound Green Proof

The packet binds:

```text
VR4 registration:     3af2e3d654b91c13aefce76e74b38ae19b2a3d6f
registration CI:      31965823863
VR4 implementation:   9fdda316441fef4f245544c90dc0a373993140e0
implementation CI:    31967145837
readiness result:     0a4a7fbe43238465ebd3ebbd97a20801e42f76c8
result CI:            31967501519
result Base job:      95214802865
result Optional job:  95214802846
```

The green machine result establishes only that the readiness mechanism works.
It did not inspect the retained structural manifest.

## Exact Expired Artifact Handling

The measured closeout left one now-expired machine-only certificate:

```text
path:    .codex_work/marc2_machine_readiness/vr4/readiness.v0.json
mode:    0600
bytes:   4,551
SHA-256: 5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e
```

The future real executor may, before any private-path operation:

1. no-follow check every certificate path component;
2. require the exact regular-file owner, mode, byte count, SHA-256, schema,
   implementation commit, contract hash, timestamps, and expired state;
3. open and read exactly those 4,551 machine-only bytes once;
4. unlink exactly that file; and
5. create no alternate, backup, renamed, or copied artifact.

Deletion authority is limited to that exact path and identity. It grants zero
authority to delete, rename, overwrite, move, or inspect another file,
directory, project, cache, payload, or consumed root.

The same future command must then obtain a fresh three-pass readiness
certificate. It must bind the exact remotely green future executor commit
provided by its proof record, not ambient branch HEAD. Readiness still occurs
before output-root or private-source operations. A machine refusal writes no
marker and performs zero private operations; this packet allows no retry or
rerun.

## Proposed Generated Stage

After a separate decision is remotely green, Stage 1 may implement only:

- exact request, decision, and future implementation proof validation;
- exact expired-certificate verification and generated cleanup fixtures;
- fresh machine-certificate generation and validation;
- no-follow fixed-root and fixed-source preflight;
- one marker-before-open state machine;
- one strict JSON structural read;
- one VR2 adapter call and cohort identity freeze;
- private and aggregate output validation; and
- generated fixtures, mutations, CLI help, resource monitors, and receipts.

Generated qualification uses only temporary generated fixtures. It cannot read
the real readiness artifact, retained manifest, another `.codex_work` root, an
archive member, or a neural value. The real command must not exist until the
separate decision is green, and it must remain proof-gated until its own exact
implementation is remotely green.

## Proposed One Real Structural Pass

The future command binds the existing no-follow, owner-only structural source:

```text
path:       .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
mode:       0600
bytes:      418,755
SHA-256:    2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
rows:       1,227
files:      1,025
directories: 202
bundles:    238
```

After fresh readiness passes, the executor may create only a new, absent,
fixed output root:

```text
.codex_work/marc2_machine_stable_private_recovery/v0
```

It must write a new mode-`0600` consumed marker immediately before one
no-follow content open of the structural source. It may then read and hash
exactly 418,755 bytes once, strict-parse the JSON, call the remotely green VR2
adapter exactly once, and freeze:

```text
source bundles:            238
eligible / ineligible:     195 / 43
selected subjects:         16
selected bundles:          96
selected members:          384
selected declared bytes:   8,105,207,776
```

The 8,105,207,776-byte value is selection metadata and an 8 GiB reservation
calculation. The command may not allocate, download, materialize, open, or read
those archive bytes. It writes only one mode-`0600` private selection manifest
and one aggregate-safe report plus the marker, under 4 MiB combined.

## Resource Limits

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
maximum command duration:                 650 seconds
peak RSS:                                < 256 MiB
minimum free disk before marker:         15 GiB
fresh readiness wait:                    <= 600 seconds
private source read:                     exactly 418,755 bytes once
network bytes:                           0
archive-member or payload bytes:          0
generated/private output:                <= 4 MiB
selection reservation ceiling:           8 GiB metadata only
retries / reruns / resumes:               0 / 0 / 0
```

## Explicitly Not Requested

This packet does not request:

- any operation before a separate green authorization decision;
- deletion or overwrite beyond the exact expired 4,551-byte certificate;
- another consumed executor/root, source substitution, generic path, or
  fallback;
- archive-member, ZIP range, EEG, MEG, channel, geometry, signal, event,
  onset, sentence, key, label, target, or payload access;
- a download, network request, S7/S20/S21/S24/S25, session 2, raw FIF/MAT, or
  another participant;
- derivative creation, split creation, training, parameter updates, model or
  checkpoint access, inference, prediction, freeze, target delivery, scoring,
  threshold selection, or post-result tuning;
- a language model, provider, RW3, stream, device, or hardware operation;
- release, publication, or any scientific, decoding, neural, real-time,
  portable, home-use, assistive, or clinical claim upgrade; or
- FW2 or CIL1 execution.

## Success And Failure Meaning

Success would establish only that a real target-free structural manifest can
be transformed into a frozen cohort identity under exact proof, machine,
privacy, and resource controls. It would make a separate FW2 preregistration
eligible.

Failure before the marker would consume no private content open but would not
permit a retry under this packet. Failure after the marker would consume the
one structural pass with no retry, rerun, resume, repair, or fallback.

## Claim Boundary

Engineering capability requested: one proof-gated, machine-stable,
target-free structural manifest pass that freezes a real cohort without
opening archive or neural payloads.

Scientific claim not established: even a successful structural cohort freeze
would access no neural payload, target, prediction, or score and would
establish no neural effect or decoding result.
