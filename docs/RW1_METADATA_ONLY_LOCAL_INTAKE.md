# RW1 Metadata-Only Local Intake Closeout

Date: 2026-07-10

Status: **Passed and closed**

Proof posture: dependency-free synthetic-fixture interface validation

## Question

Can a user safely identify a local BrainVision, EDF/EDF+, BDF, EEGLAB, FIF,
or BIDS recording bundle without importing MNE, opening binary signal arrays,
reading event/target content, or creating a decoding result?

## Result

Yes, at compatibility level 0 only. `neurodecode inspect-recording` now emits:

- deterministic, versioned `intake.json` and `intake.md` artifacts;
- a measured `intake.audit.json` sidecar for runtime, peak RSS, and exact
  output-byte accounting;
- relative source paths, file roles/sizes, a source-manifest hash, optional
  bounded text hashes, scanner-configuration hash, and optional registry hash;
- modality/device declarations, BIDS filename identity where available,
  known metadata, explicit unavailable fields, compatibility levels 0-6,
  warnings, refusal reasons, and claim boundaries;
- raw, binary, cache, target/label, model, training, and network access
  counters.

`neurodecode inspect-intake-report` strictly reloads the deterministic report,
checks its schema and payload/source/config hashes, verifies the Markdown and
audit artifact hashes and byte counts, and rejects tampering.

## Format Boundary

| Family | Level-0 behavior | Content deliberately not read |
|---|---|---|
| BrainVision | Parse a bounded `.vhdr`; resolve and validate exactly one `.eeg` and `.vmrk`; expose channel count/names, units, and header sampling rate when safe. | `.eeg` samples and `.vmrk` markers/events. |
| EDF/EDF+ | Recognize one regular `.edf`, record its relative path and declared bytes. | Binary header and samples; exact EDF subtype remains unavailable. |
| BDF | Recognize one regular `.bdf`, record its relative path and declared bytes. | Binary header, status channel, annotations, and samples. |
| EEGLAB | Recognize `.set`; identify a same-stem `.fdt` sibling without opening either. | MAT/object metadata, signal arrays, events, and labels. |
| FIF | Recognize `.fif`; validate common split filenames and contiguous indices. | FIFF header and signal payload; split validation is filename-only. |
| BIDS | Require `dataset_description.json`, enumerate a bounded tree, parse only allowlisted root metadata, and infer subject/session/task/run from one raw candidate filename. | `participants.tsv`, `events.tsv`, channel sidecars, annotations, and every binary recording. |

Unknown files, archives, pickle/object-bearing NumPy payloads, companion files
selected without their header/container, non-BIDS directories, and malformed
known bundles produce inspectable level-0 refusal reports. Unsafe selected
symlinks, root escapes, special files, NUL-bearing text metadata, and hard cap
violations stop before artifact creation.

## Safety And Resource Gates

The default contract is:

| Resource | Cap |
|---|---:|
| Files visited | 256 |
| Directory depth | 8 |
| Declared source bytes | 4 GiB |
| Text metadata per file | 1 MiB |
| Text metadata total | 8 MiB |
| Binary signal bytes read | 0 |
| Combined generated artifacts | 4 MiB |
| CPU threads | 1 |
| Network calls | 0 |

The implementation refuses a nonempty output directory unless `--overwrite`
is explicit. Overwrite mode replaces only the three registered artifact names
and preserves unrelated files. Absolute source paths are omitted from reports.

## Synthetic Roundtrip

The ignored fixture at `.codex_work/rw1_fixture/` contains a 283-byte VHDR,
76-byte synthetic signal placeholder, and 173-byte VMRK, totaling 532 declared
source bytes. The scanner was bound to `registries/datasets.v0.json` and run
with one thread:

```bash
PYTHONPATH=src .venv/bin/python -m neurodecodekit.cli inspect-recording \
  --path .codex_work/rw1_fixture/synthetic.vhdr \
  --root .codex_work/rw1_fixture \
  --out-dir outputs/rw1-metadata-intake \
  --registry registries/datasets.v0.json \
  --modality EEG \
  --device-type synthetic-brainvision-fixture \
  --hash-text-metadata
```

Measured result:

| Measure | Result |
|---|---:|
| Compatibility | level 0, recognized |
| Source files | 3 |
| Declared source bytes | 532 |
| Metadata files read | 2: VHDR plus dataset registry |
| Metadata text bytes read | 26,365 |
| Binary signal bytes read | 0 |
| Deterministic JSON bytes | 7,795 |
| Deterministic Markdown bytes | 2,181 |
| Measured audit bytes | 1,569 |
| Total output bytes | 11,545 of 4,194,304 |
| Scanner/report-build runtime | 0.001659 seconds |
| Process peak RSS | 21,643,264 bytes |
| End-to-end latency measured | No |

Access counters were exactly zero for binary signal files/bytes, raw-data
reads, real-cache reads, target/label reads, model runs, training runs, and
network calls. The strict inspect command revalidated all three artifacts.

Hashes:

- source manifest: `408d65a9123b69b8b1f2f50f2dd133bc037ff7b5e6698a87e5ea4439657847e0`
- dataset registry: `8b9f95498c4aebac70c98d9465b60ae2c8e4a2386df90c23fda4bf554b9cdbae`
- report payload: `112b876ca77b969631caf198a5534b912ba38d1fe4d7aef1204dfb3308de0eaf`
- deterministic JSON artifact: `58beb68d945c59d590f424e576016db76cacdc62f53485dcb84949dfff774fd6`
- deterministic Markdown artifact: `6c7728bbfa9c3fac1613cdb16e6c5ee93f9fb9fe4912c7e138f4d847180b72b0`

The generated fixture and reports remain ignored and are not committed.

## Verification

Pre-change baseline:

- unittest: 238 passed, 3 skipped;
- pytest: 235 passed, 3 skipped, 25 subtests passed.

Post-change verification:

- focused RW1: 11 passed;
- unittest: 249 passed, 3 skipped in 11.317 seconds; 496,943,104-byte
  maximum RSS from `/usr/bin/time -l`;
- pytest: 246 passed, 3 skipped, 25 subtests passed in 11.13 seconds;
  507,559,936-byte maximum RSS;
- Ruff, compileall, root/create/inspect CLI help, and `git diff --check` passed;
- no regression relative to the pre-change test baseline.

## Decision

Close RW1. It proves a strict local metadata-intake and refusal interface on
synthetic fixtures. RW2 may now be preregistered, but no optional signal reader
or quality metric is authorized until its exact sample, channel, time, output,
runtime, RSS, dependency, and no-auto-deletion boundaries are frozen and
pushed.

S20 remains dry-run-only. No consumed S7/S21 data, seeds 2203/2303/2353, real
cache, model, target log, or network acquisition was opened for RW1.

## Claim Boundary

Engineering capability added: a local, dependency-free compatibility-level-0
scanner can recognize or safely refuse common neurodata bundles and produce
hash-validated, resource-measured reports without opening signal or target
content.

Scientific claim not established: RW1 does not show signal readability,
signal quality, task compatibility, neural advantage, decoding, unseen-person
generalization, end-to-end latency, real-time operation, or portable-hardware
performance.
