# EEGMMIDB-UG1 Stage M2 Real Metadata Result

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-M2`

Status: **Passed once; consumed; result closeout pending remote green**

Machine artifacts:

- `registries/eegmmidb_unseen_participant_metadata_inventory.v0.json`
- `registries/eegmmidb_unseen_participant_metadata_stage_m2_result.v0.json`
- `docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_RECEIPT.md`

## Proof Order

Stage M1 proof-only closeout commit
`fd88d9d7ca9ffd3951eda295daa74a05ee4201a9` passed Base Python job
`97402552811`, Optional Neuro Readers job `97402552736`, and CI
`32717768039`. Only after both jobs were green was the sole Stage M2
invocation started.

## One-Shot Remote Metadata Result

All 36 frozen EEGMMIDB v1.0.0 URLs returned direct `200` responses to one
sequential `HEAD` request each. The pass observed one canonical
`Content-Length` and all three optional validators for every file. It followed
no redirect, retried nothing, read no response body, and used no fallback
request.

| Measure | Result |
|---|---:|
| Files / requests | 36 / 36 |
| Missing source-fit imagery files | 6 |
| Fresh-final files | 30 |
| Combined declared payload bytes | 92,414,976 |
| Missing source-fit declared bytes | 15,498,816 |
| Fresh-final declared bytes | 76,916,160 |
| Minimum / maximum file bytes | 2,555,616 / 2,596,896 |
| ETag / Last-Modified / Accept-Ranges present | 36 / 36 / 36 |
| Application-visible metadata value bytes | 2,088 |
| Inventory / receipt bytes | 11,698 / 281 |
| Combined output bytes | 11,979 |
| Runtime | 4.292717207921669 seconds |
| Peak process-tree RSS | 38,141,952 bytes |
| Initial free disk | 101,498,957,824 bytes |
| Redirects / retries / response-body bytes | 0 / 0 / 0 |
| EDF reads / payload downloads | 0 / 0 |
| Targets / models / training / scores | 0 / 0 / 0 / 0 |

The exact inventory SHA-256 is
`1b8f16f846a1bb3e0dccdbf71ea39f375872ad732bdffeecd100dbfc161a7dac`.
The exact receipt SHA-256 is
`a3ddfce0950fcb32d8ff2a540b42903ac4c20f24572324182108bfe34cf49837`.
Both are retained as small, inspectable provenance artifacts; no EDF payload
or local real-data path was opened.

## Interpretation

This establishes that the exact next cohort exists at the registered public
revision and that its aggregate declared size is 88.13 MiB, comfortably below
the 256 MiB cap. It also freezes direct remote validators for acquisition
integrity. This is useful real-world evidence about availability and bounded
storage, not evidence about EEG signal content.

Producer causality is not applicable to metadata identity. End-to-end latency
was not measured. Transport-level header bytes beyond the 2,088
application-visible metadata value bytes were not measured. EDF headers,
annotations, channels, samples, tasks, and signal quality remain unavailable.

## Next Gate

Commit, push, and remotely green this exact inventory, receipt, and result.
Then add a proof-only metadata closeout before any payload acquisition. The
next scientific lane remains source-first: only the six 15,498,816-byte
missing source-fit imagery files may be considered before the fresh 30-file
cohort, and no acquisition or EDF access is authorized by this result alone.

Engineering capability added: NeuroDecodeKit froze a complete, validator-
backed, size-bounded identity inventory for all 36 registered remote files
without downloading or opening an EDF.

Scientific claim not established: metadata proves availability and identity,
not a neural effect, decoding advantage, movement intention, motor-cortex
origin, or unseen-person generalization.
