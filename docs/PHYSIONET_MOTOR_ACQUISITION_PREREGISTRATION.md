# PhysioNet Motor Positive-Control Acquisition Preregistration

Date: 2026-08-09

Status: **Frozen acquisition-only contract; exact Tier C authorization pending**

Contract: `registries/physionet_motor_acquisition_contract.v0.json`

Research basis: `docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`

Systematic work order: `8`

## Objective

Acquire and opaque-verify one exact, tiny public EEG motor-execution slice
without parsing an EDF, reading an annotation, creating a split, or running a
model.

This stage is not the public motor positive-control experiment. It can establish
only that the nine registered bytestrings were acquired once from the pinned
public dataset version and matched their official sizes and SHA-256 values.

## Why This Slice

The PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0 is public under the
Open Data Commons Attribution License v1.0. Its official documentation describes
64-channel, 160 Hz EDF+ recordings from 109 volunteers. MNE's official EEGBCI
run mapping identifies runs `3`, `7`, and `11` as executed left-versus-right
hand movement.

Subjects `S001`, `S002`, and `S003` provide three people and three repeated
runs while keeping the exact payload at 23,248,224 bytes. Runs `3` and `7` are
only prospective future fit candidates; run `11` is only a prospective future
check candidate. Those roles do not create or activate a split in this stage.

Primary sources:

- [PhysioNet EEGMMIDB v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)
- [Official SHA256SUMS manifest](https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt)
- [MNE EEGBCI run definitions](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)

## Registration Metadata Pass

On 2026-08-09, ten HTTP HEAD requests were made across the nine selected EDF
URLs, including one repeated first-file probe. Every response was HTTP 200,
reported `application/octet-stream`, and transferred zero body bytes. The nine
current `Content-Length` values still total exactly 23,248,224 bytes.

The official checksum manifest was read as metadata and provided one SHA-256
for each selected EDF. No EDF payload byte, event file, annotation, header,
signal sample, or target was downloaded or opened. ETags and Last-Modified
values are recorded as registration observations, not hard content identities;
dataset version, path, exact size, and official SHA-256 are the hard fields.

## Frozen Input Identity

```text
provider:       PhysioNet
dataset:        eegmmidb
version:        1.0.0
DOI:            10.13026/C28G6P
license:        Open Data Commons Attribution License v1.0
subjects:       S001, S002, S003
runs:           03, 07, 11
task:           motor execution, left versus right hand
files:          9 EDF files
payload bytes:  23,248,224
```

| File | Bytes | Official SHA-256 |
|---|---:|---|
| `S001/S001R03.edf` | 2,596,896 | `3427c8d01bff1380bc9ab9f27a35ece2af5dfadf3e291bbc05eb66e4dadbfe2e` |
| `S001/S001R07.edf` | 2,596,896 | `6320a941815eb7a0bc632e32c07c88b6e2281a0e2f177e8f49e2d0a16231145c` |
| `S001/S001R11.edf` | 2,596,896 | `d5296b9232b0ad88b7022155cbcde618df44d4b0db046ce3bec54f8f8644207a` |
| `S002/S002R03.edf` | 2,555,616 | `cbabe29620b19978454bc429f59976f6ee8f32f6392e4fcdf7e463981248072c` |
| `S002/S002R07.edf` | 2,555,616 | `cdba64ad60574903248aed651d393c148df3c611eebdc9694717a04e2e2deef3` |
| `S002/S002R11.edf` | 2,555,616 | `694bd9fbee1305dbc212ea4eecb8930750f5e08f8cc8ea45e2b94c92ac5f5a7d` |
| `S003/S003R03.edf` | 2,596,896 | `ebf184ea51d9aa3178190583f428db02f184e22412ff300a5f224776d1e8dbb4` |
| `S003/S003R07.edf` | 2,596,896 | `d8a610bf60a19c1d653a11633f7df40bd7b3eca976bebf2b525eb65017fdf044` |
| `S003/S003R11.edf` | 2,596,896 | `0563c2a26f759d849d6b99b3efb6047d1e1d288f80c0c16f5f07403bd0029271` |

No `.event`, baseline, imagery, hand-versus-feet, PDF, image, manifest, or
other participant payload may be acquired by this contract. There is no
substitution or wildcard.

## Frozen Execution Sequence

1. Verify the exact contract, authorization decision, and implementation
   commit identities.
2. Enforce one CPU thread, one worker, and one numerical job.
3. Refuse unless at least 2 GiB is free and every destination, temporary, and
   receipt root is absent, non-symlinked, and isolated.
4. Reverify v1.0.0 availability, DOI, license label, all nine HTTP paths and
   sizes, and the nine official SHA-256 entries using metadata only.
5. Abort before any EDF body request on a metadata mismatch.
6. Perform one bounded acquisition invocation for exactly the nine registered
   EDF paths into the isolated temporary root.
7. Enforce metadata, payload, wall-time, RSS, and incremental-disk caps while
   transferring.
8. Opaquely stream each local file exactly once through SHA-256 without
   decoding or parsing it.
9. Refuse the entire bundle on any size or SHA-256 mismatch, without
   substitution or rerun.
10. Promote only the complete verified nine-file bundle to the frozen final
    root without copying, overwriting, deleting, or renaming preexisting data.
11. Emit one machine manifest and one human receipt under 1 MiB combined.
12. Stop before EDF parsing, event extraction, split creation, model work, or
    work order 9.

## Frozen Resources

| Resource | Maximum or requirement |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Concurrent numerical jobs | 1 |
| Wall time | 300 seconds |
| Peak RSS | 268,435,456 bytes |
| Metadata network bytes | 1,048,576 bytes |
| EDF payload network bytes | 33,554,432 bytes |
| Incremental disk peak | 67,108,864 bytes |
| Minimum free disk before start | 2,147,483,648 bytes |
| Final payload | exactly 23,248,224 bytes |
| Receipt output | 1,048,576 bytes |
| Acquisition invocations | 1 |
| Opaque local SHA-256 passes | exactly 1 per EDF |

The destination must not exist. The future implementation may clean up only
temporary files created by its own registered invocation under the frozen
temporary root. A cap breach parks the gate without a second invocation.

## Allowed Only After Exact Authorization And Green Implementation

- metadata-only reverification of the three official source surfaces;
- one bounded transfer of only the nine frozen EDF paths;
- one opaque local size and SHA-256 pass per selected EDF;
- creation of one new isolated complete bundle;
- one bounded manifest and receipt; and
- cleanup only of invocation-created temporary files.

## Explicitly Forbidden

- opening, decoding, or parsing any EDF header, signal, or annotation channel;
- downloading or reading any `.event` payload;
- reading T0, T1, T2, task, target, label, event, epoch, trial, channel,
  montage, reference, geometry, sampling, or signal-quality values from a file;
- creating epochs, windows, features, caches, train/check/final splits, or
  derivative arrays;
- importing MNE or another EDF reader in the acquisition executor;
- loading, fitting, selecting, inferring, or scoring any model or baseline;
- opening S20, SpanishBCBL, S7, S21, S24, S25, or another real dataset;
- downloading additional participants, runs, files, companions, or substitutes;
- using a language model, provider, pretrained model, stream, device, or
  hardware;
- uploading, publishing, releasing, overwriting, deleting, or renaming real
  payloads;
- a second invocation or retry after an acquisition receipt exists; and
- any neural, decoding, typing, language, real-time, portable, home-use,
  assistive, clinical, or superiority claim.

## Acceptance Gates

All twelve gates must pass together:

1. Registration, authorization, and implementation commits are exact, pushed,
   and remotely green in both required CI jobs before execution.
2. PhysioNet version `1.0.0`, DOI `10.13026/C28G6P`, public access, and the ODC
   Attribution 1.0 license label remain exact.
3. All nine metadata paths and sizes match the frozen records.
4. All nine official checksum-manifest entries match the frozen SHA-256 values.
5. Every output root is absent, isolated, regular-path-only, and non-symlinked.
6. The complete final root contains exactly nine regular EDF files and exactly
   23,248,224 bytes.
7. Each file passes exact size and one opaque local SHA-256 verification.
8. Metadata, payload, runtime, RSS, disk, thread, worker, and receipt caps pass.
9. Every forbidden access and operation counter remains zero.
10. No preexisting path is opened, followed, overwritten, deleted, or renamed.
11. Every warning and unavailable field is explicit in both receipts.
12. The receipt preserves the acquisition-only claim ceiling and stops before
    work order 9.

Any failure parks acquisition without a second invocation or substitution.

## Required Receipt

The machine receipt must include contract, authorization, implementation, and
source identities; start and finish timestamps; runtime; peak RSS; free disk;
metadata and EDF network bytes; incremental disk peak; exact final bytes; every
file path, size, official SHA-256, and observed local SHA-256; metadata and
payload request counts; opaque hash counts; every forbidden-access counter;
warnings; unavailable fields; individual gate outcomes; and the claim boundary.

After a clean acquisition, all of the following remain unavailable: observed
channel count, channel names, units, sampling rate, montage, reference,
geometry, annotations, events, trials, labels, target balance, signal quality,
usable epochs, model accuracy, no-signal comparison, neural advantage,
generalization, and end-to-end latency.

## Authorization Order

This preregistration, machine contract, and invariant test must be committed,
pushed, and remotely green first. Only then may an exact authorization packet
and request bind those immutable artifacts. A user decision must be recorded
in a separate authorization-only commit and become remotely green before any
executor is implemented. The exact implementation must then be fixture-tested,
committed, pushed, and remotely green before one acquisition invocation.

The Research Autonomy Charter, the earlier 5-10 GB allowance, the $50 AI
budget, and prior S20 or real-data permissions are not Tier C authorization for
this work order.

## Claim Boundary

A clean pass can prove only that nine exact public EDF bytestrings were
acquired once and matched the registered version, paths, sizes, and official
SHA-256 values within the frozen resource and access boundaries.

It cannot prove EDF readability, motor-event correctness, EEG quality, a motor
effect, model accuracy, improvement over a no-signal prior, neural origin,
typing or language decoding, transfer to S20, unseen-person generalization,
real-time behavior, portable hardware, home use, assistive value, or clinical
utility.
