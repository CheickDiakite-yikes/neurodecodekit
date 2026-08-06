# Loop 54 Stage A Strict VHDR Preregistration

Date: 2026-08-06

Status: **Frozen contract; exact Tier C authorization pending**

Contract: `registries/loop54_stage_a_vhdr_contract.v0.json`

Research basis: `docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md`

Acquisition result: `registries/loop53_acquisition_result.v0.json`

## Objective

Read exactly one already acquired S20 BrainVision header and produce a bounded,
target-free ledger of its declared recording and channel fields. This is the
smallest real-content step between the completed acquisition and a later EEG
signal-quality audit.

Stage L54-A is not a signal read, trial reconstruction, model run, or decoding
experiment. Its only eligible result is a pass or park on strict VHDR
readability and declared metadata compatibility.

## Frozen Input Identity

```text
payload root:  data/loop53_s20_eeg/SpanishBCBL
relative path: EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr
role:          BrainVision header
bytes:         exactly 11,705
source Git ID: 9ab325a0f8523b675ecab1c97e16169143f1f341
subject:       S20
session:       2
block:         2
```

The path must be a regular file beneath the exact payload root. The payload
root, every parent component, and the file itself must be non-symlinked. No
wildcard, alternate root, backup file, participant, session, or block is
allowed.

## Why This Stage Is Separate

A normal BrainVision library call can resolve the marker sibling and expose
marker-derived annotations even with signal preloading disabled. The marker
file can contain response or key identity. Stage L54-A therefore uses a small
standard-library parser that opens one VHDR only and treats the referenced EEG
and VMRK names as inert basename strings.

This stage consumes no signal sample and learns no event, trial, response,
sentence, key, label, or target value.

## Frozen Parser Boundary

The future implementation must:

1. open exactly the registered VHDR with no-follow semantics;
2. refuse unless its byte count and Git-blob identity are exact;
3. read at most 16,384 bytes and decode without replacement characters;
4. accept only a frozen ASCII-compatible BrainVision codepage policy;
5. parse exact `Common Infos`, `Binary Infos`, and ordered `Channel Infos`
   declarations with duplicate-key and duplicate-channel rejection;
6. require the declared channel count to equal the complete `Ch1..ChN` table;
7. preserve channel names, declared references, resolutions, and units without
   type, magnitude, or geometry inference;
8. derive sampling rate only from a positive finite sampling interval;
9. verify the data and marker references as exact basenames without opening or
   statting either sibling; and
10. omit comments, unused sections, raw lines, and unallowlisted values from
    every output, log, warning, and exception.

Unknown channel type, measured position, coordinate frame, orientation,
ground, global acquisition reference, bad-channel status, EOG/EMG identity,
events, trials, targets, signal quality, and neural information must remain
explicitly unavailable.

## Frozen Output

One canonical JSON ledger and one short human-readable summary may be written
under `.codex_work/loop54_stage_a_vhdr/output`. Their combined size must not
exceed 1,048,576 bytes. The output may contain only:

- contract, decision, implementation, source, and payload identity hashes;
- format, codepage, data orientation, binary format, channel count, sampling
  interval, and derived sampling rate;
- the ordered allowlisted channel declaration table;
- impedance-section and filter-declaration availability booleans;
- runtime, peak RSS, input/output byte counts, thread and worker counts;
- exact access counters, warnings, unavailable fields, and gate results; and
- the L54-Q2 claim boundary.

It may not contain raw header text, comment content, local absolute paths,
marker descriptions, keycodes, responses, labels, targets, signal values, or
unregistered metadata fields. Output is fail-closed and must never overwrite a
preexisting path.

## Frozen Resources

| Resource | Cap |
|---|---:|
| CPU threads | 1 |
| Workers | 1 |
| Registered executions | 1 |
| VHDR content opens | 1 |
| Input bytes | exactly 11,705 |
| Maximum read bytes | 16,384 |
| Wall time | 30 seconds |
| Peak RSS | 268,435,456 bytes |
| Combined generated output | 1,048,576 bytes |
| Network and download bytes | 0 |
| New payload bytes | 0 |

The implementation must enforce these limits before or during execution. A
resource breach parks the stage without rerun.

## Registered Execution Order

1. Verify the immutable Loop 53 result, Loop 54 research, contract, decision,
   and implementation identities.
2. Verify that the authorization-only decision and implementation commits were
   pushed and remotely green before execution.
3. Enforce one CPU thread, one worker, the time limit, and output cap.
4. Refuse a preexisting output path or any unexpected or symlinked input path.
5. Open exactly the one registered VHDR with no-follow semantics.
6. Verify exact size and Git-blob identity before semantic parsing.
7. Strictly decode, parse, validate, and canonicalize only the allowlisted
   fields.
8. Verify all sibling, target, signal, model, and network access counters remain
   zero.
9. Atomically emit the bounded ledger and summary.
10. Stop before L54-B.

## Explicitly Forbidden

- opening, statting, hashing, resolving, or parsing the VMRK, EEG, or MAT files;
- MNE, SciPy, Torch, Zarr, Hugging Face, or another heavy reader dependency;
- signal, marker, event, trial, response, key, sentence, label, or target access;
- channel deletion, typing, rereferencing, interpolation, filtering, ICA, or
  resampling;
- writing raw VHDR content, comments, unknown fields, or absolute local paths;
- cache, split, model, checkpoint, inference, training, scoring, or selection;
- S7, S21, S24, S25, raw FIF, another participant, or another S20 file;
- network, download, language-model, RW3, stream, device, or hardware work;
- overwriting, deleting, renaming, or following preexisting content;
- rerun, substitution, or post-result amendment; and
- scientific, decoding, real-time, portable, home-use, or clinical claim
  promotion.

## Acceptance Gates

L54-A passes only if all frozen gates hold:

1. Every dependency and source identity matches.
2. Exact authorization and implementation commits were remotely green first.
3. Exactly one regular non-symlinked 11,705-byte VHDR is opened once.
4. Its Git-blob identity matches the registered source identity.
5. No sibling path is resolved, statted, or opened.
6. No MNE or heavy dependency is imported.
7. Strict codepage detection and decoding succeeds without replacement.
8. Every required section and key is unique and internally consistent.
9. DataFile and MarkerFile are exact inert basenames.
10. `NumberOfChannels` exactly matches one ordered `Ch1..ChN` table.
11. Channel names are nonempty and unique after documented escape decoding.
12. References, resolutions, and units are preserved without guessing.
13. Sampling interval is positive and sampling rate is deterministically
    derived.
14. Unknown type, geometry, reference, confound, event, trial, and target fields
    remain explicitly unavailable.
15. No raw text, comments, targets, or unallowlisted values enter outputs or
    diagnostics.
16. Every forbidden access and operation counter remains zero.
17. Every resource, output, thread, worker, and no-overwrite gate passes.
18. The result remains at or below L54-Q2 declared-header compatibility.

Any failed gate parks L54-A. There is no second real execution.

## Authorization Order

This preregistration and its invariant tests must be committed, pushed, and
remotely green first. A separate authorization packet will then bind the green
registration commit and exact artifact hashes. The user's exact Tier C decision
must be recorded in an authorization-only commit and become remotely green
before implementation starts.

The parser must then be implemented and qualified entirely with synthetic local
fixtures, committed, pushed, and remotely green before the one registered VHDR
execution. General research autonomy, earlier S20 permissions, storage
allowances, or competitive urgency are not transitive authorization.

## Claim Boundary

Engineering capability proposed: a strict dependency-light reader can turn one
exact BrainVision VHDR into a bounded declared-channel ledger without resolving
or exposing its signal, marker, MAT, or target siblings.

Scientific claim not established: this preregistration reads no S20 content and
establishes no header readability, EEG quality, trial validity, neural
advantage, decoding accuracy, generalization, latency, portable hardware,
at-home use, or clinical utility.
