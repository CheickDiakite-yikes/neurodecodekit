# PhysioNet Motor Positive-Control Acquisition Authorization Packet

Date: 2026-08-09

Status: **Awaiting exact Tier C authorization**

Registration commit:
`2a7b4188553e221133d788a081b838dbbb9f41bb`

Registration CI: `31301730612`

Contract: `registries/physionet_motor_acquisition_contract.v0.json`

Preregistration: `docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md`

## Decision In Plain Language

This request is for permission to build a narrow public-file downloader using
only generated local fixtures, obtain green CI for that implementation, and
then invoke it once for one already selected PhysioNet motor-EEG bundle.

The bundle is nine exact EDF files from three people and totals 23,248,224
bytes, about 22.2 MiB. One execution may reverify public metadata, download
only those files into a new isolated folder, hash their bytes without
interpreting them, and write a small receipt. It stops there.

It may not open or parse an EDF header, annotation, or signal; fetch an
`.event` sidecar; inspect channels, sampling, events, trials, or targets; create
a split; load or train a model; score anything; substitute a file; retry; or
continue into the public motor experiment. Those are later decisions.

## Why This Is Worth Doing

NeuroDecodeKit's protected S21 MEG and historical S7 EEG classifiers both
performed worse than their no-signal comparators. The project therefore needs
a small public task with a known, easier motor contrast before spending more
protected evidence or scaling a model.

Acquisition is deliberately separated from interpretation. A clean download
would make the exact public bytes reproducibly available for a future parser
qualification, but it would not spend the event labels, train a positive
control, or establish any neural effect.

## Green Registration Evidence

Registration commit `2a7b4188553e221133d788a081b838dbbb9f41bb`
passed CI `31301730612` before this request was prepared:

- Base Python job `93215490492`: passed;
- Optional Neuro Readers job `93215490501`: passed;
- preregistration SHA-256:
  `26c3f08f88171573ca5ddb751901101a65ca84750b690806a860d9a5c4086349`;
- contract SHA-256:
  `6c81dac6a818f13c49f5df25c540e9d3ef65f21b56ecb1a5b5d15d4a3dc819d3`;
- invariant-test SHA-256:
  `7241734f8c80cdcb4807d479bd8a7ec792461f24aefeee54269e2a18ffaae535`.

The registration made ten HTTP HEAD requests across the nine selected URLs,
including one repeated first-file probe. Every response reported HTTP 200 and
transferred zero EDF body bytes. No local PhysioNet path exists under this
contract, and no EDF or `.event` payload was downloaded or opened.

## Exact Registered Bundle

```text
provider:       PhysioNet
dataset:        eegmmidb
version:        1.0.0
DOI:            10.13026/C28G6P
license:        Open Data Commons Attribution License v1.0
subjects:       S001, S002, S003
runs:           03, 07, 11
files:          9 EDF files
payload bytes:  23,248,224
```

The exact paths, sizes, official SHA-256 values, and current informational HTTP
observations are frozen in the contract. There is no wildcard, event sidecar,
backup, redirect to an unregistered host, participant/run substitution, or
partial qualifying bundle.

Runs 03 and 07 are only prospective future fit candidates. Run 11 is only a
prospective future check candidate. These names do not create or activate a
split during acquisition.

## Resource Limits

| Resource | Frozen maximum or requirement |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Concurrent numerical jobs | 1 |
| Wall time | 300 seconds |
| Peak RSS | 256 MiB |
| Metadata network | 1 MiB |
| EDF payload network | 32 MiB |
| Incremental disk peak | 64 MiB |
| Final bundle | exactly 23,248,224 bytes |
| Combined receipt output | 1 MiB |
| Acquisition invocations | 1 |
| Payload retries | 0 |
| Opaque local SHA-256 passes | exactly 1 per EDF |
| Required free disk before start | at least 2 GiB |

The final, temporary, and receipt roots must all be absent, isolated, and
non-symlinked. The implementation may clean up only temporary files created by
its own registered invocation. It may not copy over, follow, overwrite,
delete, or rename a preexisting path.

## Execution Order After Authorization

Authorization does not immediately download data. The order is:

1. Record the maintainer's exact sentence in a separate authorization-only
   human and machine decision.
2. Test, commit, push, and obtain green Base Python and Optional Neuro Readers
   CI for that decision.
3. Implement the dependency-light downloader without requesting or opening an
   EDF payload.
4. Qualify metadata, redirects, path collisions, symlinks, caps, hashes,
   malformed responses, sidecar leakage, retries, and overclaims using only
   generated local fixture bytes and mocked network responses.
5. Commit, push, and obtain green Base Python and Optional Neuro Readers CI for
   the exact implementation.
6. Execute the registered acquisition once with no retry.
7. Retain its pass or park receipt without rerun.
8. Stop before EDF parsing or work order 9.

## Exact Authorization Sentence

To approve this exact scope, send the following sentence unchanged:

> Authorize the work order 8 PhysioNet motor positive-control acquisition implementation and one registered acquisition exactly as scoped in docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md and registries/physionet_motor_acquisition_contract.v0.json. I bind registration commit 2a7b4188553e221133d788a081b838dbbb9f41bb and green CI run 31301730612. I authorize, only after a separate authorization-only decision is committed, pushed, and remotely green, a dependency-light acquisition implementation qualified only with generated local fixtures and mocked network responses; and only after that exact implementation is committed, pushed, and remotely green, metadata-only reverification of the three registered official source surfaces and one no-retry acquisition invocation for only the nine named PhysioNet EEGMMIDB v1.0.0 EDF files totaling exactly 23,248,224 bytes; one opaque local size and SHA-256 pass per EDF; creation of one new isolated complete bundle; cleanup only of temporary files created by that invocation; and one machine manifest and one human receipt under 1 MiB combined using one CPU thread, one worker, one numerical job, 300 seconds, 256 MiB peak RSS, 1 MiB metadata network, 32 MiB EDF payload network, 64 MiB incremental disk, and at least 2 GiB free disk. I do not authorize opening, decoding, or parsing any EDF header, annotation, event channel, or signal; downloading or reading any .event sidecar; reading task, target, label, event, epoch, trial, channel, montage, reference, geometry, sampling, or signal-quality values from a payload; creating epochs, windows, features, caches, splits, or derivative arrays; importing MNE or another EDF reader in the acquisition executor; model or checkpoint access; inference; training; scoring; S20, SpanishBCBL, S7, S21, S24, S25, or another real dataset; additional files, participants, runs, companions, substitutions, retries, or reruns; language models or providers; RW3; streams; devices; hardware; upload; publication; release; work order 9; or any scientific, decoding, neural, real-time, portable, home-use, assistive, or clinical claim upgrade.

## What A Clean Pass Would Prove

A clean pass would prove that the exact nine-file public bundle was acquired
once and matched the registered version, paths, sizes, and official SHA-256
values within the frozen resource, storage, network, and access-order limits.

It would establish no EDF readability, channel or event correctness, signal
quality, motor effect, model accuracy, improvement over a no-signal prior,
neural origin, typing or language decoding, cross-person generalization,
real-time latency, portable-hardware performance, at-home result, assistive
value, or clinical claim.

## Current Counters

At this request boundary:

```text
official metadata documents read:            3
HTTP HEAD requests / body bytes:             10 / 0
EDF payload GET requests / network bytes:    0 / 0
local PhysioNet path stats / opens / hashes: 0 / 0 / 0
header / annotation / signal reads:          0 / 0 / 0
target or label reads:                       0
cache / split operations:                    0 / 0
model access / inference / training / score: 0 / 0 / 0 / 0
provider / device / hardware operations:     0 / 0 / 0
generated experiment bytes:                  0
```

Every implementation, metadata-reverification, payload, local-path, parsing,
model, execution, rerun, and claim authorization remains false until the exact
sentence is received and recorded in a separately green decision commit.
