# Loop 54 Stage A Recovery-Bound Authorization Packet

Date: 2026-08-08

Status: **exact v1 request frozen; exact user decision pending; parser and real
execution not started**

Machine request:
`registries/loop54_stage_a_recovery_authorization_request.v1.json`

This packet supersedes the historical v0 draft request. It does not modify the
frozen preregistration or contract, and it is not an authorization decision.
The exact sentence below becomes eligible for a user decision only after this
packet's own commit is pushed and remotely green.

## Recovery Binding

The original registration commit
`c1146233a6178ca5e1153b92565915abad029719` remains the scientific source. Its
three frozen artifacts remain byte-identical:

| Artifact | SHA-256 |
|---|---|
| `docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md` | `9b17d31a70c88eff3ab77d731abf1c0c759152f5c2ee6c8b3c5153bbd57875b6` |
| `registries/loop54_stage_a_vhdr_contract.v0.json` | `a0a466d845bff79e9461646f76791a3583fe7c567aeb532b6e951e570411124e` |
| `tests/test_loop54_stage_a_vhdr_contract.py` | `33591567aab4999d7f9c9bab8986147869b0a9339b0c618149a8fd60ffb86ef5` |

The exact historical commit's second CI attempt is preserved as a real failure
caused by its floating Ruff declaration. It is not called green. Instead:

- pinned-toolchain descendant `223299381036217631374d096fc842add5f6baf7`
  passed CI `31132586790` with the three artifacts byte-identical; and
- additive recovery commit `5915bdf28d96385b190f27c7743dd3df00396ced`
  passed CI `31277277711`, recording the failure classification, exact-tree
  local replay, immutable hashes, and replacement evidence rule.

The completed synthetic contact-interface work order does not authorize this
stage. It is bound only as queue state: closeout
`41370081d299442f35290ffd10ec9c6d556ef7d3` passed CI `31282657626`.

## Requested Decision

The requested decision has two ordered permissions under one exact scope:

1. after the decision commit is pushed and remotely green, implement and
   adversarially qualify a standard-library parser using synthetic local VHDR
   fixtures only; and
2. after that exact implementation commit is pushed and remotely green,
   execute the registered real VHDR stage once.

The second permission cannot occur early. A green decision does not open the
header; it only permits synthetic implementation. A green implementation does
not widen the real stage beyond the exact one-file contract.

## Exact Registered Input

The contract names one already acquired file:

```text
payload root:  data/loop53_s20_eeg/SpanishBCBL
relative path: EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr
bytes:         exactly 11,705
source Git ID: 9ab325a0f8523b675ecab1c97e16169143f1f341
subject:       S20
session:       2
block:         2
```

This packet did not stat, resolve, hash, or open that local path. There is no
wildcard, backup, alternate root, participant, session, block, or rerun.

## Exact Allowed Sequence

1. Preserve the user's exact sentence in an authorization-only decision.
2. Commit and push that decision and require both CI jobs to pass.
3. Implement the parser with the Python standard library only.
4. Test only generated synthetic VHDR strings and filesystem layouts, including
   all 22 registered refusal classes. Do not create a synthetic copy from the
   real header.
5. Commit and push the implementation and require both CI jobs to pass.
6. Refuse preexisting output and any unexpected, missing, nonregular, or
   symlinked input condition before content access.
7. Open only the exact registered 11,705-byte VHDR once with no-follow
   semantics, read at most 16,384 bytes, verify size and Git-blob identity, and
   strictly parse only allowlisted declarations.
8. Record `DataFile` and `MarkerFile` only as inert basenames. Never resolve,
   stat, hash, or open either sibling.
9. Emit one canonical target-free JSON ledger and one short summary under the
   combined 1 MiB cap, then stop before Loop 54-B.
10. Preserve one pass or park result. Do not rerun or amend after execution.

## Resource Limits

| Resource | Frozen maximum |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Wall time | 30 seconds |
| Peak RSS | 268,435,456 bytes |
| Registered real executions | 1 |
| VHDR content opens | 1 |
| Expected input | exactly 11,705 bytes |
| Maximum read | 16,384 bytes |
| Combined output | 1,048,576 bytes |
| Network, download, and new payload bytes | 0 |

## Explicit Refusals

This request does not permit:

- statting, resolving, hashing, opening, or parsing the VMRK, EEG, MAT, any
  sibling, or any other participant file;
- reading a signal sample, marker, event, trial, response, key, sentence,
  label, target, or raw-header comment;
- publishing raw header text, comments, unknown values, or absolute local
  paths;
- guessing channel type, measured geometry, EOG/EMG identity, ground, global
  reference, bad-channel state, impedance, event count, trial count, signal
  quality, or neural information;
- deleting channels, rereferencing, filtering, ICA, interpolation, resampling,
  cache creation, split creation, feature extraction, or representation work;
- loading a model or checkpoint, inference, training, scoring, selection,
  provider calls, language models, RW3, streams, devices, or hardware;
- downloads, network payloads, releases, substitutions, overwrite, deletion,
  rename, rerun, or post-result amendment; or
- any scientific, neural, decoding, real-time, portable, at-home, or clinical
  claim upgrade.

## Exact Authorization Sentence

To authorize this stage, send the following sentence exactly after this
packet's commit is confirmed remotely green:

> Authorize the Loop 54 Stage A recovery-bound strict S20 VHDR implementation and one registered execution exactly as scoped in docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md, docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md, registries/loop54_stage_a_recovery_authorization_request.v1.json, and registries/loop54_stage_a_vhdr_contract.v0.json. I bind the immutable registration commit c1146233a6178ca5e1153b92565915abad029719 and its three registered artifact hashes, the pinned green proof anchor 223299381036217631374d096fc842add5f6baf7 with CI 31132586790, and the green recovery commit 5915bdf28d96385b190f27c7743dd3df00396ced with CI 31277277711. I authorize, only after this decision is committed, pushed, and remotely green, a standard-library parser implementation and adversarial qualification using generated synthetic VHDR fixtures; and only after that exact implementation is committed, pushed, and remotely green, no-follow validation of the registered local path plus one size, Git-blob, strict-read, and allowlisted-parse pass over only the named 11,705-byte S20 session-2 block-2 VHDR. I authorize recording its inert DataFile and MarkerFile basenames without resolving, statting, hashing, or opening either sibling, and creation of one target-free canonical ledger and one summary under 1 MiB using one CPU thread, one worker, 30 seconds, 256 MiB peak RSS, one VHDR content open, one registered execution, zero network bytes, and zero new payload bytes. I do not authorize opening, statting, resolving, hashing, or parsing the VMRK, EEG, MAT, any sibling, or any other participant file; signal samples; markers; events; trials; responses; keys; sentences; labels; targets; raw-header or comment publication; channel deletion or inferred type, impedance, reference, or geometry; cache or split creation; feature extraction; model or checkpoint access; inference; training; scoring; selection; downloads; language models; RW3; streams; devices; hardware; release; rerun; substitution; overwrite; deletion; rename; post-result amendment; or any scientific, decoding, neural, real-time, portable, home-use, or clinical claim upgrade.

General research autonomy, storage allowance, Loop 53 acquisition permission,
Work Order 5 completion, or competitive urgency is not this exact decision.

## Proof Boundary

This packet proves only that the recovered one-file decision surface is exact,
bounded, hash-bound, and ready for a separate user decision after remote-green
CI. It does not prove parser behavior or real header readability.

Engineering capability proposed: NeuroDecodeKit can qualify and then execute a
strict one-file BrainVision-header compatibility check under a recovery-bound,
no-sibling, one-shot evidence order.

Scientific claim not established: no S20 path or content was accessed, so this
packet establishes no header readability, EEG signal quality, event or trial
validity, target correctness, neural advantage, decoding accuracy,
generalization, latency, device performance, home use, or clinical result.
