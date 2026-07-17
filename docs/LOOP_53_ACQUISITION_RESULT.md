# Loop 53 Fresh S20 EEG Acquisition Result

Date: 2026-07-17

Status: **Consumed; acquisition passed; no rerun; stop before Loop 54**

Public aggregate result:
`registries/loop53_acquisition_result.v0.json`

The payload and its two receipts remain Git-ignored. This document contains no
payload bytes, decoded content, target, signal sample, per-file local content
hash, or other interpretive result.

## Result

The one registered invocation acquired and opaque-verified the exact public S20
session-2 block-2 bundle:

```text
repository:          bcbl190626/SpanishBCBL
revision:            88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
license metadata:    cc-by-nc-4.0
files:               4 / 4 exact registered paths
network bytes:       96,090,264
final payload bytes: 96,090,264
status:              passed
reruns:              0 and none authorized
```

The pinned revision remained public, ungated, enabled, and licensed under the
registered CC BY-NC 4.0 metadata boundary. Every path, size, Git object identity,
LFS SHA-256 identity, and Xet provenance identity matched before and after the
opaque transfer. The complete verified directory was promoted once; no partial
bundle was promoted.

## Measured Resources

| Measurement | Result | Frozen gate |
|---|---:|---:|
| Runtime | 3.629499 seconds | <= 600 seconds |
| Peak RSS | 63,225,856 bytes | <= 536,870,912 bytes |
| Network payload | 96,090,264 bytes | <= 134,217,728 bytes |
| Peak incremental disk | 102,035,529 bytes | <= 268,435,456 bytes |
| Free disk before | 44,104,826,880 bytes | >= 2,147,483,648 bytes |
| Free disk after | 44,001,705,984 bytes | measured |
| Private receipt output | 8,265 bytes | <= 1,048,576 bytes |
| CPU threads / workers | 1 / 1 | 1 / 1 |

The private receipt consists of a 7,140-byte JSON manifest and a 1,125-byte
Markdown receipt. Their SHA-256 values are bound in the public aggregate result,
but neither private file is committed.

## Access Ledger

```text
registered acquisition invocations:             1
metadata calls / response bytes:             2 / 41,847
payload file requests / network bytes:        4 / 96,090,264
opaque local hash reads:                         4
header / marker / signal / MAT reads:        0 / 0 / 0 / 0
target or label reads:                           0
cache reads or writes / split operations:     0 / 0
checkpoint or model loads:                       0
inference / training / scoring runs:          0 / 0 / 0
language-model runs:                             0
RW3 / stream / device / hardware operations:     0
additional file / participant operations:      0 / 0
reruns:                                          0
```

No parser was called. The bytes were transferred and hashed as opaque binary
content only.

## Acceptance Gates

All ten frozen gates passed:

1. Authorization and implementation commits were pushed and green before the
   invocation.
2. Revision, public availability, and license metadata remained exact.
3. All four metadata identities matched.
4. One isolated four-file, 96,090,264-byte bundle was complete.
5. Every opaque size and integrity check passed.
6. Every runtime, memory, network, disk, thread, worker, and output cap passed.
7. Every forbidden access and operation counter remained zero.
8. Every warning and unavailable field was explicit.
9. No preexisting path was followed, overwritten, deleted, or renamed.
10. No scientific or decoding claim was promoted.

## Still Unavailable

The following were deliberately not measured: channel count or names, sampling
rate, reference scheme, sensor geometry, event count, trial count, target text,
signal quality, neural advantage, decoding accuracy, and end-to-end latency.

Loop 54 is not implicitly authorized by this pass. Header, marker, signal, MAT,
target, channel, geometry, event, and trial interpretation remain closed until a
separate exact Tier C decision for the applicable Loop 54 stage is committed,
pushed, and remotely green.

## Claim Boundary

Engineering capability added: NeuroDecodeKit acquired, opaque-verified, and
atomically retained one exact public four-file S20 EEG bundle under every frozen
identity, resource, access-order, and no-overwrite gate.

Scientific claim not established: Loop 53 produced no evidence of BrainVision
readability, EEG signal quality, trial or target validity, neural advantage,
decoding accuracy, generalization, end-to-end latency, portable hardware,
at-home use, or clinical utility.
