# Loop 54 Stage A Recovery-Bound Authorization Decision

Date: 2026-08-08

Status: **exact Tier C decision recorded; effective only after this record is
tested, committed, pushed, and remotely green; no implementation or execution
has started**

Machine decision:
`registries/loop54_stage_a_recovery_authorization_decision.v1.json`

Frozen request:
`registries/loop54_stage_a_recovery_authorization_request.v1.json`

Frozen contract: `registries/loop54_stage_a_vhdr_contract.v0.json`

## Exact User Decision

The maintainer supplied the registered sentence verbatim:

> Authorize the Loop 54 Stage A recovery-bound strict S20 VHDR implementation and one registered execution exactly as scoped in docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md, docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md, registries/loop54_stage_a_recovery_authorization_request.v1.json, and registries/loop54_stage_a_vhdr_contract.v0.json. I bind the immutable registration commit c1146233a6178ca5e1153b92565915abad029719 and its three registered artifact hashes, the pinned green proof anchor 223299381036217631374d096fc842add5f6baf7 with CI 31132586790, and the green recovery commit 5915bdf28d96385b190f27c7743dd3df00396ced with CI 31277277711. I authorize, only after this decision is committed, pushed, and remotely green, a standard-library parser implementation and adversarial qualification using generated synthetic VHDR fixtures; and only after that exact implementation is committed, pushed, and remotely green, no-follow validation of the registered local path plus one size, Git-blob, strict-read, and allowlisted-parse pass over only the named 11,705-byte S20 session-2 block-2 VHDR. I authorize recording its inert DataFile and MarkerFile basenames without resolving, statting, hashing, or opening either sibling, and creation of one target-free canonical ledger and one summary under 1 MiB using one CPU thread, one worker, 30 seconds, 256 MiB peak RSS, one VHDR content open, one registered execution, zero network bytes, and zero new payload bytes. I do not authorize opening, statting, resolving, hashing, or parsing the VMRK, EEG, MAT, any sibling, or any other participant file; signal samples; markers; events; trials; responses; keys; sentences; labels; targets; raw-header or comment publication; channel deletion or inferred type, impedance, reference, or geometry; cache or split creation; feature extraction; model or checkpoint access; inference; training; scoring; selection; downloads; language models; RW3; streams; devices; hardware; release; rerun; substitution; overwrite; deletion; rename; post-result amendment; or any scientific, decoding, neural, real-time, portable, home-use, or clinical claim upgrade.

This exact decision authorizes two strictly ordered stages. It is not a direct
instruction to open the header now.

## Bound Green Request

```text
request commit:         19813a86d7822954219976e4c119d1dd6693d4b3
request push CI:        31283297030
Base Python:            success
Optional Neuro Readers: success
packet SHA-256:         6417ae947641bd7e1135dab323477d3a9b1cb26109081f33aa55c97f3316c47e
request SHA-256:        62a8107ca404f51bcdd36fa6879161fd2a32db42ee9c16c7bc81e1cd14b2a52b
contract SHA-256:       a0a466d845bff79e9461646f76791a3583fe7c567aeb532b6e951e570411124e
```

The preregistration, contract, recovery record, packet, and request remain
immutable snapshots. Their pending and false authorization fields are not
rewritten; this separate record captures the later decision.

## Stage 1 After This Decision Is Green

The implementation may:

1. add a Python-standard-library VHDR parser and bounded CLI surface;
2. generate synthetic VHDR strings and synthetic filesystem layouts from the
   frozen specification, never from the real header;
3. test strict decoding, allowlisted parsing, canonicalization, output caps,
   no-follow handling, and all 22 refusal classes; and
4. report synthetic implementation runtime, peak RSS, output bytes, and zero
   protected-access counters.

Stage 1 may not stat, resolve, hash, or open the registered S20 path. Its exact
commit must be pushed and both CI jobs must pass before Stage 2.

## Stage 2 After The Implementation Is Green

The single registered execution may:

1. validate the exact registered path without following symlinks;
2. open only the named 11,705-byte VHDR once with no-follow semantics;
3. read at most 16,384 bytes and verify size and Git-blob identity;
4. strictly parse only allowlisted declarations;
5. record `DataFile` and `MarkerFile` only as inert basenames without touching
   either referenced sibling; and
6. atomically emit one target-free canonical ledger and one summary under the
   combined 1 MiB cap.

There is no second execution, substitution, overwrite, deletion, rename, or
post-result amendment. Stop before Loop 54-B.

## Resource Boundary

```text
CPU threads / workers:       1 / 1
wall time:                   <= 30 seconds
peak RSS:                    <= 268,435,456 bytes
registered real executions: 1
VHDR content opens:          1
expected input:              exactly 11,705 bytes
maximum read:                16,384 bytes
combined generated output:   <= 1,048,576 bytes
network / download bytes:    0 / 0
new payload bytes:           0
```

## Authorization-Only Measurements

```text
S20 path stat / resolve / hash / open:               0 / 0 / 0 / 0
VHDR parse runs / output writes:                     0 / 0
VMRK / EEG / MAT / other sibling accesses:           0 / 0 / 0 / 0
signal / marker / event / trial / target reads:      0 / 0 / 0 / 0 / 0
cache / split / feature / representation operations: 0 / 0 / 0 / 0
model / inference / training / scoring runs:         0 / 0 / 0 / 0
network / provider / language-model operations:      0 / 0 / 0
RW3 / stream / device / hardware operations:         0 / 0 / 0 / 0
generated experiment bytes:                          0
end-to-end latency measured:                         false
```

## Claim Boundary

**Engineering capability authorized for testing:** one strict standard-library
parser may be qualified on generated synthetic fixtures and, only after its
exact implementation is remotely green, used for one bounded compatibility
check of the exact registered VHDR.

**Scientific claim not established:** this authorization record is not a
parser result or an S20 result. It establishes no header readability, EEG
signal quality, event or trial validity, target correctness, neural advantage,
decoding accuracy, generalization, latency, device performance, home use, or
clinical utility.
