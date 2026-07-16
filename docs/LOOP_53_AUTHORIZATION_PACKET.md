# Loop 53 Fresh S20 EEG Acquisition Authorization Packet

Date: 2026-07-15

Status: **Awaiting exact Tier C authorization**

Registration commit:
`bccd36790317b5f58ca62083c6b3019d1983176c`

Contract: `registries/loop53_fresh_eeg_acquisition_contract.v0.json`

Preregistration:
`docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md`

Research: `docs/LOOP_53_PRIMARY_SOURCE_RESEARCH.md`

## Decision In Plain Language

This request is for permission to build a narrow downloader and run it once for
one already selected S20 EEG bundle. The bundle has four exact public files and
totals 96,090,264 bytes, about 91.6 MiB.

The run may verify public metadata, download those files into a new isolated
folder, count bytes, hash them without interpreting them, and write a tiny
receipt. It stops there.

It may not inspect the BrainVision header, markers, EEG samples, MAT fields,
sentences, key events, labels, or targets. It may not create a cache or split,
load or train a model, score anything, substitute another file/person, or run
twice. Those are later decisions.

## Why This Is Worth Doing

The project has technically validated an EEG bridge on consumed S7 data, but
that classifier performed worse than its no-signal prior. A fresh EEG cohort is
the most direct path toward a genuinely new accessible-modality verdict. Loop
53 does not spend that verdict. It only establishes that the exact fresh bundle
can be acquired reproducibly and safely enough for a later, separately ordered
identity/confound pass.

The historical S20 approval packet combined acquisition, parsing, splitting,
training, and scoring. This request supersedes it for future S20 work with a
smaller acquisition-only decision.

## Exact Registered Bundle

```text
repository: bcbl190626/SpanishBCBL
revision:   88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
license:    cc-by-nc-4.0
subject:    S20
session:    2
block:      2
files:      4
bytes:      96,090,264
```

The exact paths, sizes, Git object IDs, LFS SHA-256 values, and Xet provenance
values are frozen in the contract. There is no wildcard, backup, or subject
substitution.

## Resource Limits

| Resource | Frozen maximum |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Wall time | 600 seconds |
| Peak RSS | 512 MiB |
| Network payload | 128 MiB |
| Incremental disk peak | 256 MiB |
| Final bundle | exactly 96,090,264 bytes |
| Receipt output | 1 MiB |
| Acquisition invocations | 1 |
| Required free disk before start | at least 2 GiB |

The destination must not exist. The implementation must refuse symlinks and
must not overwrite, delete, rename, or follow any preexisting path. It may
clean up only temporary files created by its own registered invocation inside
the frozen temporary root.

## Execution Order After Authorization

Authorization does not immediately download data. The order is:

1. Record the user's exact sentence in a separate authorization-only decision.
2. Test, commit, push, and obtain green push and PR CI for that decision.
3. Implement the dependency-light acquisition tool without downloading or
   opening any payload.
4. Qualify metadata, collision, cap, hash, malformed-response, and target-
   leakage refusals with synthetic/local fixture bytes only.
5. Commit, push, and obtain green push and PR CI for the implementation.
6. Execute the registered acquisition once.
7. Retain its pass or park receipt without rerun.
8. Stop before Loop 54.

## Exact Authorization Sentence

To approve this exact scope, send the following sentence unchanged:

> Authorize the Loop 53 fresh S20 EEG acquisition implementation and one registered acquisition exactly as scoped in docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md and registries/loop53_fresh_eeg_acquisition_contract.v0.json. I authorize metadata reverification for the pinned public revision; one bounded acquisition invocation for only the four named S20 session-2 block-2 files totaling exactly 96,090,264 bytes; opaque sequential size and integrity hashing; creation of one new isolated complete bundle; cleanup only of temporary files created by that invocation; and one manifest and receipt under 1 MiB using one CPU thread, one worker, 600 seconds, 512 MiB peak RSS, 128 MiB network payload, 256 MiB incremental disk, and at least 2 GiB free disk. I do not authorize parsing or interpreting VHDR, VMRK, EEG, or MAT content; reading headers, markers, signal samples, targets, labels, sentences, key events, channels, geometry, sampling, events, or trials; creating caches or splits; model or checkpoint access; inference; training; scoring; S7/S21/S24/S25 or raw FIF access; additional files, participants, substitutions, downloads, or reruns; language models; RW3; streams; devices; hardware; release; or scientific, decoding, real-time, portable, home-use, or clinical claim upgrades.

## What A Clean Pass Would Prove

A clean pass would prove that the exact four-file public S20 bundle was
acquired once and matched its registered source identities within the resource,
storage, license, and access-order caps.

It would establish no EEG signal quality, target validity, neural information,
decoding accuracy, improvement over a no-signal prior, cross-person or cross-
modality generalization, real-time latency, portable-hardware performance,
at-home result, or clinical claim.

## Current Counters

At this request boundary:

```text
public metadata API operations:              4
remote payload bytes read:                   0
payload download invocations:                0
local S20 path stats or hashes:              0
header / marker / signal / MAT reads:         0 / 0 / 0 / 0
target or label reads:                       0
cache / split operations:                    0 / 0
model inference / training / scoring runs:   0 / 0 / 0
device or hardware operations:               0
generated experiment bytes:                  0
```

Every execution authorization remains false until the exact sentence is
received and recorded in a separately green decision commit.
