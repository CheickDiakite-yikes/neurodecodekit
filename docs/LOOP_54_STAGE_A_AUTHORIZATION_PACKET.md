# Loop 54 Stage A Strict S20 VHDR Draft Authorization Packet

Date: 2026-08-06

Status: **Draft; registration CI infrastructure-blocked; not actionable**

Registration commit:
`c1146233a6178ca5e1153b92565915abad029719`

Registration CI:
`31127199848` (cancelled before any step started during the 2026-08-06
GitHub Actions major outage)

Contract: `registries/loop54_stage_a_vhdr_contract.v0.json`

Preregistration: `docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md`

## Decision In Plain Language

This request permits NeuroDecodeKit to build a small strict text parser and run
it once on one already acquired 11,705-byte BrainVision header. It may report
only declared recording fields and the ordered channel declaration table.

The parser may read the VHDR's references to its EEG and VMRK siblings as inert
filenames. It may not resolve, stat, hash, or open those files. It may not read
the MAT log, any signal sample, marker, event, trial, response, key, sentence,
label, or target.

This is a one-file compatibility check, not an EEG experiment.

## Why This Is The Next Useful Move

Loop 53 already acquired and opaque-verified the exact four-file S20 bundle.
Loop 55 cannot run honestly until we know whether the block has a readable,
internally consistent header and later qualifies for target-blind signal and
isolated trial reconciliation stages.

L54-A is the narrowest real-data step that removes one uncertainty without
spending the signal, markers, targets, or final scientific test. It gives the
project an immediate execution path while retaining the controls needed for a
credible result.

## Exact Registered Input

```text
payload root:  data/loop53_s20_eeg/SpanishBCBL
relative path: EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr
bytes:         exactly 11,705
source Git ID: 9ab325a0f8523b675ecab1c97e16169143f1f341
subject:       S20
session:       2
block:         2
```

There is no wildcard, backup, alternate root, or participant substitution.

## Allowed Work After Exact Authorization

1. Implement the dependency-light parser and validate it with synthetic local
   VHDR fixtures only.
2. Commit and push that implementation and obtain remotely green CI.
3. Validate the registered local path without following symlinks.
4. Open the exact VHDR once, verify its size and Git-blob identity, strictly
   decode it, and parse only the frozen allowlist.
5. Record the referenced EEG and VMRK basenames without touching those files.
6. Create one canonical target-free ledger and short summary under the combined
   1 MiB cap.
7. Stop before L54-B.

## Resource Limits

| Resource | Frozen maximum |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Wall time | 30 seconds |
| Peak RSS | 256 MiB |
| Registered executions | 1 |
| VHDR content opens | 1 |
| Input bytes | exactly 11,705 |
| Maximum bytes read | 16,384 |
| Combined output | 1 MiB |
| Network, download, and new payload bytes | 0 |

The implementation must fail before content access when identity or resource
preconditions do not hold. The real execution cannot be repeated.

## Explicitly Outside This Decision

- any VMRK, EEG, MAT, sibling, or other participant stat or content access;
- signal, marker, event, trial, response, key, sentence, label, or target reads;
- raw VHDR text, comments, unknown values, or absolute local paths in output;
- inferred channel type, measured geometry, EOG/EMG role, or missing reference;
- channel deletion, rereferencing, filtering, ICA, interpolation, or resampling;
- cache, split, model, checkpoint, inference, training, scoring, or selection;
- network, download, language-model, RW3, stream, device, or hardware work;
- overwrite, deletion, rename, substitution, rerun, or post-result amendment;
  and
- scientific, neural, decoding, real-time, portable, at-home, or clinical claim
  promotion.

## Required Evidence Order

Authorization does not open the header immediately. The order is:

1. Record the user's exact sentence in an authorization-only decision.
2. Commit, push, and obtain remotely green CI for that decision.
3. Implement and adversarially test the parser with synthetic fixtures only.
4. Commit, push, and obtain remotely green CI for the implementation.
5. Execute the exact registered VHDR stage once.
6. Preserve one pass or park result with no rerun.
7. Stop before L54-B, which remains a separate Tier C decision.

## Exact Authorization Sentence

The following sentence is a draft. It becomes actionable only after the exact
registration commit receives remotely green CI and a follow-up commit freezes
this packet. Do not use it as authorization before then.

> Authorize the Loop 54 Stage A strict S20 VHDR implementation and one registered execution exactly as scoped in docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md and registries/loop54_stage_a_vhdr_contract.v0.json. I authorize no-follow validation of the registered local path; one size, Git-blob, strict-read, and allowlisted-parse pass over only the named 11,705-byte S20 session-2 block-2 VHDR; recording its inert DataFile and MarkerFile basenames without resolving, statting, hashing, or opening either sibling; and creation of one target-free canonical ledger and summary under 1 MiB using one CPU thread, one worker, 30 seconds, 256 MiB peak RSS, one VHDR content open, one registered execution, zero network bytes, and zero new payload bytes. I authorize implementation and synthetic-fixture qualification before that execution. I do not authorize opening, statting, resolving, hashing, or parsing the VMRK, EEG, MAT, any sibling, or any other participant file; signal samples; markers; events; trials; responses; keys; sentences; labels; targets; raw-header or comment publication; channel deletion or inferred type or geometry; cache or split creation; model or checkpoint access; inference; training; scoring; selection; downloads; language models; RW3; streams; devices; hardware; release; rerun; substitution; post-result amendment; or any scientific, decoding, neural, real-time, portable, home-use, or clinical claim upgrade.

## What A Clean Pass Would Prove

A clean pass would prove only that the exact acquired S20 VHDR is strictly
readable and that its allowlisted declared recording and channel fields are
internally consistent under L54-Q2.

It would not establish EEG signal quality, event or trial validity, target
correctness, sensor-signal or neural advantage, decoding accuracy,
generalization, end-to-end latency, portable hardware, at-home use, or clinical
utility.

## Current Counters

At this request boundary:

```text
local S20 path stats:                         0
VHDR content opens / hashes / parses:       0 / 0 / 0
VMRK stats or reads:                          0
EEG stats or signal reads:                    0
MAT stats or reads:                           0
target or label reads:                        0
output ledger writes:                         0
cache / split operations:                   0 / 0
model loads / inference / training / score: 0 / 0 / 0 / 0
network or download operations:               0
language-model runs:                          0
RW3 / stream / device / hardware:             0
reruns / generated experiment bytes:        0 / 0
```

Every execution authorization remains false until the exact sentence is
made actionable by a green registration snapshot, then received and preserved
in a separate remotely green decision commit.
