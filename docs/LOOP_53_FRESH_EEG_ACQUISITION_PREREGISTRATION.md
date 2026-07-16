# Loop 53 Fresh EEG Acquisition Preregistration

Date: 2026-07-15

Status: **Frozen contract; exact Tier C authorization pending**

Contract: `registries/loop53_fresh_eeg_acquisition_contract.v0.json`

Research basis: `docs/LOOP_53_PRIMARY_SOURCE_RESEARCH.md`

## Objective

Acquire and validate one exact S20 EEG BrainVision/log bundle while preserving
S20 as fresh for every later interpretive, target-dependent, and model stage.

Loop 53 is not an EEG benchmark. The only eligible result is a pass or park on
bundle acquisition mechanics.

## Frozen Input Identity

```text
repo:       bcbl190626/SpanishBCBL
revision:   88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
license:    cc-by-nc-4.0
modality:   EEG
subject:    S20
session:    2
block:      2
task:       task2
files:      4
bytes:      96,090,264
```

The exact paths, sizes, Git object identities, LFS SHA-256 values, and Xet
provenance values are frozen in the machine contract. No wildcard is allowed.
No backup participant, session, block, or file may be substituted.

## Frozen Execution Sequence

1. Verify the contract and the future authorization decision hashes.
2. Enforce one CPU thread and one worker.
3. Refuse unless at least 2 GiB is free and the destination is absent,
   non-symlinked, and isolated to `data/loop53_s20_eeg/SpanishBCBL`.
4. Reverify revision, availability, license, four paths, sizes, and source
   identities through metadata-only calls.
5. Abort before payload download on any mismatch.
6. Perform one bounded acquisition invocation for exactly four paths into
   `.codex_work/loop53_s20_eeg_acquisition/tmp`.
7. Measure network payload bytes and peak incremental disk allocation.
8. Verify exact sizes and source identities through opaque sequential hashing.
   Do not decode or parse any payload.
9. Atomically promote only the complete verified bundle to the frozen payload
   root. Never overwrite, rename, or delete a preexisting path.
10. Emit `acquisition_manifest.json` and `acquisition_receipt.md` under the
    frozen 1 MiB combined cap.
11. Stop. Do not begin Loop 54.

## Frozen Caps

| Resource | Cap |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Wall time | 600 seconds |
| Peak RSS | 536,870,912 bytes |
| Network payload | 134,217,728 bytes |
| Incremental disk peak | 268,435,456 bytes |
| Minimum free disk before start | 2,147,483,648 bytes |
| Final payload | exactly 96,090,264 bytes |
| Receipt output | 1,048,576 bytes |
| Acquisition invocations | 1 |

The implementation must enforce the caps while operating, not only report them
afterward. A cap breach parks the gate. There is no rerun or substitution.

## Allowed After Exact Authorization

- public metadata reverification for the one pinned revision;
- transfer of only the four frozen paths;
- opaque sequential byte counting and integrity hashing;
- creation of the one isolated complete bundle;
- one bounded manifest and receipt; and
- cleanup only of temporary files created by that invocation under the frozen
  temporary root.

## Explicitly Forbidden

- parsing the VHDR, VMRK, EEG, or MAT payload;
- reading signal samples, markers, key events, sentences, labels, or targets;
- inferring channel count, channel names, sampling, reference, geometry,
  event count, trial count, or signal quality;
- creating an event/sentence cache or any split;
- reading S7, S21, S24, S25, raw FIF, or another participant;
- loading a checkpoint or running inference, training, scoring, or selection;
- language-model, RW3, stream, device, or hardware work;
- following symlinks or replacing, deleting, or renaming preexisting content;
- downloading another file after any mismatch; and
- promoting any scientific, decoding, real-time, portable, at-home, or clinical
  claim.

## Acceptance Gates

Loop 53 passes only if all conditions hold:

1. The authorization decision and implementation commits were pushed and
   remotely green before execution.
2. The pinned public revision and `cc-by-nc-4.0` metadata remain exact.
3. All four metadata records match their frozen path, size, and source identity.
4. The isolated final root contains exactly four regular files totaling exactly
   96,090,264 bytes.
5. Every size and opaque integrity check passes.
6. Every resource and output cap passes.
7. Every forbidden access and operation counter remains zero.
8. Every warning and unavailable field is explicit.
9. No preexisting path was followed, overwritten, deleted, or renamed.
10. The receipt states the acquisition-only claim ceiling.

Any failed condition parks Loop 53 without a second acquisition invocation.

## Required Receipt

The machine manifest must record contract and authorization hashes, exact source
identity, timestamps, runtime, peak RSS, disk before/after/peak, network bytes,
final bytes, every file's source identity and local content SHA-256, all access
counters, warnings, unavailable fields, individual gate outcomes, and the claim
boundary.

The following remain explicitly unavailable after a pass because payload
interpretation is outside Loop 53: channel count/names, sampling, reference,
geometry, events, trials, targets, signal quality, neural advantage, decoding
accuracy, and end-to-end latency.

## Authorization Order

This preregistration and its invariant tests must be committed, pushed, and
remotely green first. A separate authorization-only record must then quote the
user's exact decision, bind this contract by hash, be committed and pushed, and
pass remote CI. Only then may a dependency-light executor be implemented and
qualified without payload access. The registered acquisition may run once only
after that implementation is also committed, pushed, and remotely green.

General research autonomy, the 5-10 GB storage allowance, and earlier S20 or
other-loop permissions are not transitive authorization for Loop 53.

## Claim Boundary

A clean pass proves that one exact public S20 bundle can be acquired and
verified under the registered resource and access controls.

It does not prove BrainVision readability, trial identity, EEG quality, neural
information, decoding performance, unseen-person generalization, cross-modality
transfer, real-time behavior, portable hardware, home use, or clinical utility.
