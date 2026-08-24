# MARC2-VR39P Terminal Private Cohort Freeze Authorization Decision

Date: 2026-08-23

Lane: `MARC2-VR39P`

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both required CI jobs are green**

Machine decision:

- `registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `MARC2-VR39P` as the sole active Tier C packet and
reported its exact request commit, proof-closeout commit, CI evidence,
two-stage scope, scientific boundary, and fresh-decision requirement, the
maintainer's next message was exactly:

```text
continue
```

The machine decision preserves those actual eight UTF-8 bytes and their
SHA-256. Under the approved Research Autonomy Charter short-form rule, this
unambiguous continuation binds only the unchanged, remotely green VR39P packet
by reference. It does not fabricate the packet's long sentence as a user
utterance, repair wording, infer FW2/CIL1 authority, or expand any registered
path, resource, output, privacy, retry, or claim boundary.

## Green Packet Bound By This Decision

```text
request commit:       6c805a817fa44375b7b0e120abcb2c748c78ca07
request CI:           32675925646
request Base job:     97283907786
request Optional job: 97283907932
proof commit:         e581fe99d97e91e5af07e211dd75caa22a10d098
proof CI:             32677755105
proof Base job:       97288870035
proof Optional job:   97288870180
```

Both required jobs passed for both commits. The request and proof artifact set
contains six unchanged files totaling 61,722 bytes. The proof closeout also
records one repository-root listing and one `.codex_work` root-entry metadata
observation, with zero descendant/content/private-source operations. This
decision preserves that accounting and does not inspect the path again. The
unrelated untracked tracker inspection NDJSON remains untouched.

## Delayed Effect

This decision does not become effective merely because these files exist.
Before any wrapper implementation or generated qualification, this exact
decision must pass local checks, be committed and pushed, and pass both
required remote CI jobs.

Recording the decision performs zero `.codex_work`, readiness, private-source,
output-root, consumed-state, archive, neural, target, model, score, network,
device, release, or scientific-claim operation.

## Authorized Sequence After Green Decision

### Stage 1: generated/mock fixed-path wrapper

After this decision is remotely green, one additive standard-library wrapper
may be implemented and qualified using only generated structural fixtures,
injected readiness providers, deterministic nonce providers, mocked no-follow
facts, and temporary output roots.

The wrapper must expose fixed `plan`, `qualify`, `inspect`, and proof-gated
`execute` surfaces. It may expose no generic path, URL, output, count,
threshold, task, rank, cap, route, retry, nonce, readiness, or resource
override. It must not import, call, copy, modify, or inspect a consumed private
wrapper or path.

Qualification must run the 21 exact registered cases in ready and not-ready
states, canonical and reversed source order, and two exact replays. Across 168
paths it must call unchanged VR33A 168 times, make 504 provider calls and 336
sleeper calls, call unchanged VR38A 84 times only for `PPP`, create 64
temporary generated cohort outputs, return R1/R2 exactly 64/104 times, pass at
least 200 direct refusals, and retain zero generated output.

Both VR38A success routes must pass at every valid 12-19 participant
cardinality. Missing fit or heldout runs, taxonomy/companion refusal, minimum
prefix or reservation refusal, uncompressed or peak-disk failure, every
non-`PPP` pattern, source mutation, duplicate JSON keys, symlink or ancestor
swap, short write, nonce/HMAC error, output-cap breach, and crash-injection
case must fail closed to R2 without private access.

The exact implementation and generated result must then be committed, pushed,
and pass both remote jobs. A separate proof-only closeout must also be
committed, pushed, and pass both jobs before Stage 2.

### Stage 2: one terminal target-free structural attempt

Only after the exact Stage 1 implementation and its proof closeout are
remotely green may one fixed-path command:

1. create the fresh mode-0700 output root and mode-0600 consumed marker before
   readiness;
2. call unchanged VR33A once for exactly three fresh readiness samples and two
   fixed five-second sleeps;
3. consume every non-`PPP` result at R2 with zero source content opens;
4. for `PPP`, require all fixed paths and output state to pass no-follow,
   identity, mode, size, SHA-256, JSON, resource, and freshness checks;
5. read, hash, and strict-parse exactly 418,755 target-free structural bytes
   once;
6. call exact unchanged VR38A once without mutating the source;
7. on VR38A G1 or G2 only, transform generated provenance to real private
   provenance, verify all split and storage contracts, generate one private
   32-byte CSPRNG HMAC key, and write one mode-0600 source-bound cohort
   manifest for the exact selected 12-19 participant prefix;
8. write only the fixed-shape R1 or byte-identical R2 aggregate report; and
9. fsync every file and directory and write the completion marker last.

Every route consumes the one invocation. No retry, rerun, resume, repair,
backfill, fallback, substitution, overwrite, cleanup, partial-state reuse,
private reinspection, or amendment is authorized.

## Fixed Route And Privacy Contract

| Route | Maximum engineering meaning |
|---|---|
| `MARC2VR39P-R1` | One target-free, source-bound 12-19 participant cohort was privately frozen; a separate FW2 preregistration becomes eligible. |
| `MARC2VR39P-R2` | No cohort was frozen; the Freewill/CIL1 lane is permanently parked. |

Both VR38A successes collapse to R1. Every readiness, structural, taxonomy,
selection, split, provenance, storage, output, resource, privacy, or unexpected
failure collapses to byte-identical R2.

Public output is restricted to the eleven registered allowlist fields. It may
not expose the selected count, rank, identity, bundle/member/split count, path,
offset, CRC, compressed or uncompressed total, source hash, upstream route,
surplus topology, failure class, private reason, nonce, deterministic private
manifest hash, row, value, exception, readiness outcome, operation count,
runtime, RSS, or free disk. R1 may differ from R2 only through the public
secret-key HMAC-SHA-256 commitment.

## Fixed Paths And Resources

```text
private source:        .codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json
readiness certificate: .codex_work/marc2_machine_readiness/vr39p/readiness.v0.json
output root:           .codex_work/marc2_selection_sufficiency_private_cohort_freeze/v0
consumed marker:       output root / consumed.marker.v0.json
private manifest:      output root / cohort.private.v0.json
aggregate report:      output root / report.aggregate.v0.json
completion marker:     output root / complete.marker.v0.json
private source bytes:  418,755 at most once and only after PPP
CPU / workers / jobs:  1 / 1 / 1
generated runtime:     <= 120 seconds
private runtime:       <= 30 seconds
peak RSS:              < 256 MiB
minimum free disk:     >= 15 GiB
combined output:       <= 2 MiB
selected compressed:  <= 8 GiB
selected uncompressed: <= 8.75 GiB plus 1 GiB derivative and 256 MiB temp reserve
peak incremental disk: <= 10 GiB
network/new payload:   0 / 0 bytes
archive/signal/target: 0 / 0 / 0 bytes
retry/rerun/resume:    0 / 0 / 0
```

## Explicitly Not Authorized

This decision does not authorize implementation before its own remote-green
proof; Stage 2 before exact Stage 1 and closeout proof; another source, path,
project, participant, session, run, task, or dataset; operation on any named
consumed lane or the unexecuted VR37P state; archive members; EEG/MEG samples,
events, channels, geometry, quality, labels, targets, or outcomes; derivative
signal arrays, caches, features, splits, or NeuroTokens; training, inference,
prediction, scoring, tuning, foundation or language models; FW2 or CIL1
execution; streams, devices, hardware, network, downloads, release,
publication, or any scientific or clinical claim upgrade.

## Next Gate

Commit, push, and green this exact decision. Then implement and
generated-qualify Stage 1. Only after that implementation and its proof-only
closeout are remotely green may the registered target-free structural command
run once.

Engineering capability authorized after green decision: one generated-proven
terminal wrapper and one later proof-gated target-free structural attempt may
privately commit a bounded cohort or permanently park the lane.

Scientific claim not established: this decision is not neural data or a
result and establishes no neural effect, decoding performance, advantage over
no-signal or peripheral controls, language decoding, unseen-person
generalization, or live decoding.
