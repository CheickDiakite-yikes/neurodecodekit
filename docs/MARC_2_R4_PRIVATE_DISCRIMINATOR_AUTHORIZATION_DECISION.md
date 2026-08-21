# MARC2-VR13P R4 Private Discriminator Authorization Decision

Date: 2026-08-20

Lane: `MARC2-VR13P`

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both required CI jobs are green**

Machine decision:
`registries/marc2_r4_private_discriminator_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `MARC2-VR13P` as the sole active Tier C packet and
reported its exact request, proof head, CI run, two required jobs, two-stage
scope, and scientific boundary, the maintainer's next message was exactly:

```text
continue
```

The machine decision preserves those actual eight UTF-8 bytes and their
SHA-256. The detailed scope below comes only from the unchanged remotely green
packet by reference; it is not represented as a longer maintainer utterance.

## Green Packet Bound By This Decision

```text
request commit:       d55371e8d95c562dc0e4eff7f3ea27820e2af7d0
request CI:           32428583270
request Base job:     96615486644
request Optional job: 96615486542
proof head:           bff3d3fc344291f57c5ef90c6affb8077e57d7c0
proof CI:             32429569470
proof Base job:       96618310916
proof Optional job:   96618311046
```

Both required jobs passed for both exact heads. Proof attempt `ae54ffc` failed
only because its test required parent Git history that the default shallow CI
checkout did not contain. Final proof head `bff3d3f` replaced that historical
lookup with `git hash-object` over the same byte-, SHA-256-, and Git-blob-bound
request artifacts. It changed no request scope and performed no private or
scientific operation.

The unrelated tracker inspection NDJSON was not opened, modified, staged, or
deleted.

## Delayed Effect

This decision does not become effective because its files exist. Before any
wrapper implementation, generated qualification, readiness operation, output
root operation, or private source path check, this exact decision must:

1. pass focused local verification;
2. be committed as a decision-only milestone;
3. be pushed on the current branch; and
4. pass both required remote CI jobs.

Until all four conditions hold, implementation and private access remain
closed.

## Authorized Sequence After Green Decision

### Stage 1: generated fixed-path wrapper

After this exact decision is remotely green, one additive standard-library
wrapper may be implemented and qualified using only invocation-created
generated source fixtures, injected readiness samples, mocked no-follow
filesystem facts, and temporary generated output roots.

The wrapper must expose fixed `plan`, `qualify`, `inspect`, and proof-gated
`execute` surfaces. It may not accept generic source, output-root, URL,
threshold, retry, resume, fallback, route, or arbitrary execution overrides.
It may not import, call, patch, copy, modify, or inspect consumed VR11P or VR12P
executors, readiness state, markers, outputs, or private results.

Qualification must send all eight VR13A cases through canonical and reversed
orders with two exact replays: 32 paths, one exact VR12A call per path, no
residual-map call on success, one residual-map call on a failed path, and at
least 80 direct refusal mutations. Retained generated output must be zero and
all real, private, archive, neural, target, model, score, network, hardware,
FW2/CIL1, other-project, and claim counters must be zero.

The exact Stage 1 implementation must be committed, pushed, and pass both
remote CI jobs. A separate proof-only closeout must then be committed, pushed,
and pass both jobs before Stage 2.

### Stage 2: one target-free private structural discriminator

Only after the exact Stage 1 implementation and proof closeout are remotely
green may one fixed command:

1. verify every bound proof and the one-thread environment;
2. obtain three consecutive passing readiness samples;
3. create one fresh mode-`0600` readiness certificate;
4. require the fixed output root to be absent and reject aliases/symlinks;
5. no-follow preflight only the registered structural source;
6. write one mode-`0600` consumed marker immediately before content open;
7. read, hash, and strict-parse exactly 418,755 target-free bytes once;
8. call the exact green VR12A adapter once;
9. call the exact green VR13A residual map at most once if VR12A refuses;
10. on R1 only, write one mode-`0600` source-exact cohort manifest; and
11. write one aggregate-safe mode-`0644` R1-R8 report.

The aggregate report may retain only route, counts, nonreversible hashes,
exact proof identities, bounded measurements, warnings, unavailable fields,
zero forbidden-operation counters, and claim boundaries. It may not retain an
exception, reason, predicate, failed value, row, member, source path, offset,
CRC, source hash, subject, participant, session, run, task, companion,
candidate, selection, signal, event, target, label, model, prediction, score,
or participant outcome.

## Fixed Route Contract

| Aggregate route | Maximum engineering meaning |
|---|---|
| `MARC2VR13P-R1` | VR12A passed and one target-free structural cohort was frozen |
| `MARC2VR13P-R2` | residual suffix-bearing BIDS identity class |
| `MARC2VR13P-R3` | exact Freewill task-token class |
| `MARC2VR13P-R4` | companion run-token inconsistency class |
| `MARC2VR13P-R5` | normalized companion-collision class |
| `MARC2VR13P-R6` | incomplete companion-set class |
| `MARC2VR13P-R7` | repaired bundle-total mismatch class |
| `MARC2VR13P-R8` | taxonomy or eligibility mismatch class |

Every route consumes the one invocation. No route permits retry, rerun,
resume, repair, fallback, substitution, private reinspection, or post-result
amendment. An unknown or leaking route parks the lane.

## Conditional R1 Cohort Envelope

R1 may retain one target-free structural cohort with 12-19 selected subjects,
72-114 selected run bundles, 288-456 selected core members, `ses-01` as fit,
`ses-02` as held out, zero overlap, source-exact names, and reservation at or
below 8 GiB. Selection must remain target-, quality-, and outcome-free.

R1 makes a separate prospective FW2 preregistration eligible. It does not
authorize FW2 implementation or execution, open an archive member or neural
payload, or make CIL1 eligible.

## Fixed Paths And Resources

```text
readiness certificate: .codex_work/marc2_machine_readiness/vr13p/readiness.v0.json
new output root:        .codex_work/marc2_r4_private_discriminator/v0
private source:         .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
private source bytes:   418,755 exactly once
private source SHA-256: 2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
CPU / workers / jobs:   1 / 1 / 1
generated runtime:      <= 60 seconds
private runtime:        <= 650 seconds
peak RSS:               <= 256 MiB
minimum free disk:      >= 15 GiB
combined output:        <= 2 MiB
network / new payload:  0 / 0 bytes
archive/signal/target:  0 / 0 / 0 bytes
retry/rerun/resume:     0 / 0 / 0
```

A pre-marker refusal opens zero private content and still consumes the one
registered invocation. Cleanup is limited to invocation-created temporary
files.

## Explicitly Not Authorized

This decision does not authorize implementation before its own remote green;
private operation before exact Stage 1 and proof-closeout green; operation on
consumed VR11P/VR12P state; another file, source, output root, project,
dataset, participant, session, or run; network or download; archive local
header or member payload; EEG, MEG, signal, event, onset, channel, geometry,
sentence, key, label, target, response, trial, or quality access; derivative,
cache, feature, split, or NeuroToken creation; training, parameter update,
checkpoint access, inference, prediction, freeze, target delivery, scoring,
tuning, or language-model use; FW2 or CIL1 execution; provider, RW3, stream,
device, or hardware work; release or publication; or a scientific, decoding,
neural, real-time, portable, home-use, assistive, or clinical claim upgrade.

## Next Gate

After this decision is remotely green, implement and generated-qualify the
fixed-path wrapper. After its exact implementation and proof closeout are both
remotely green, perform the one registered structural discriminator. Stop
after the aggregate result. Only R1 may unlock a separate FW2 preregistration.

Engineering capability authorized after green decision: one proof-gated
target-free structural read can either freeze the cohort required to
preregister FW2 or isolate the residual structural blocker class.

Scientific claim not established: this decision is not neural data or a
result and establishes no neural effect, decoding performance, language
decoding, live decoding, or thought-to-text capability.
