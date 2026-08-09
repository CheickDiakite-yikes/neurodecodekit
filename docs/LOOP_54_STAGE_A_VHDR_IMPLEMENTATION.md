# Loop 54 Stage A Strict VHDR Implementation

Date: 2026-08-08
Status: Implemented and synthetic-qualified; exact implementation commit must become remotely green before one registered execution

## Authorization binding

Implementation began only after recovery request commit
`19813a86d7822954219976e4c119d1dd6693d4b3` passed CI run
`31283297030` and exact decision commit
`2177b36f56464361bc51b2656406da7575ff1a1f` passed CI run
`31286428489`. Its Base Python job `93176025548` and Optional Neuro Readers
job `93176025560` both passed. The immutable preregistration and recovery
artifacts remain unchanged.

This milestone implements and tests only the parser and one-shot runner. It
does not execute the registered S20 pass. The exact implementation commit,
push CI run, Base Python job, and Optional Neuro Readers job must all be known
and green before `--execute` is eligible.

## Capability implemented

`src/neurodecodekit/preprocess/vhdr_ledger.py` adds:

- bounded loaders for the immutable contract, exact authorization decision,
  and implementation source manifest;
- strict UTF-8/BOM and explicitly declared Windows-1252 decoding without
  replacement characters;
- required-section and required-key validation with duplicate rejection;
- exact inert `DataFile` and `MarkerFile` basename validation without sibling
  path construction;
- deterministic decimal sampling-rate derivation;
- complete, ordered channel declarations with BrainVision `\1` comma escape
  decoding and no inferred channel type, reference, unit, or geometry;
- no-follow component checks, one regular-file descriptor open, one bounded
  read, and Git-blob identity verification;
- a target-free canonical JSON ledger and Markdown summary under a combined
  1 MiB ceiling;
- metadata-only ledger inspection; and
- stable refusals for all 22 registered failure classes.

The CLI adds `loop54-vhdr-ledger`, which is dry-run by default and does not
stat the registered S20 path, plus `inspect-loop54-vhdr-ledger`. Execution
requires four explicit implementation-green identifiers and a clean tracked
worktree at the exact implementation commit.

## Output transaction

Both output byte strings are completed and capped in memory before any output
file is created. The registered output root must not exist. The summary is
created first with exclusive no-follow semantics and fsynced; the canonical
ledger is then created and fsynced as the final commit marker. No preexisting
path is read, followed, overwritten, deleted, or renamed. A partial output
cannot contain a canonical pass ledger, and its existence consumes the
one-shot path rather than enabling a rerun.

## Synthetic qualification

Generated VHDR bytes and temporary filesystem layouts exercised:

- UTF-8, UTF-8 BOM, and explicit Windows-1252;
- documented channel-name escape decoding;
- missing, unsupported, and conflicting codepages;
- invalid bytes, replacement risk, and control characters;
- missing, duplicate, and malformed required declarations;
- unsafe sibling references;
- channel-count, channel-index, channel-name, and tuple failures;
- nonfinite and nonpositive sampling intervals;
- missing, nonregular, and symlinked inputs;
- size and Git-blob mismatch;
- output collision, symlink, and output-cap failures;
- forbidden sibling, protected-data, model, training, scoring, network, and
  hardware counters;
- heavy-dependency import drift;
- rerun or amendment evidence; and
- claim-ceiling or acceptance-gate mutation.

The focused suite passed 24 tests and 24 mutation subchecks. Temporary fixture
files were removed by their test contexts. No generated payload is retained or
committed.

The final implementation verification passed 61 combined Loop 54 route and
implementation tests with 33 subchecks. The complete one-thread repository
suite passed 1,351 tests with three expected skips and 493 subtests in 35.10
seconds external wall time at 670,728,192-byte peak RSS. Ruff 0.15.20,
compileall, all 92 registry JSON files, both command-help surfaces, the guarded
no-stat dry run, and `git diff --check` passed. Complete-suite RSS is a
development measurement, not the future one-VHDR execution measurement.

## Access and operation ledger

| Operation | Count |
|---|---:|
| Registered S20 path stats or resolutions | 0 |
| Registered VHDR content opens, hash reads, or parse runs | 0 |
| VMRK, EEG, MAT, sibling, or other-participant stats/reads | 0 |
| Signal, marker, event, trial, response, key, sentence, label, or target reads | 0 |
| Cache, split, feature, model, inference, training, scoring, or selection runs | 0 |
| Network, download, provider, language-model, RW3, stream, device, or hardware operations | 0 |
| Real registered executions | 0 |
| Retained generated experiment bytes | 0 |

## Resource boundary

The registered wrapper enforces one CPU thread, one worker, 30 seconds,
268,435,456-byte peak RSS, one 11,705-byte VHDR content open, at most 16,384
read bytes, and at most 1,048,576 combined output bytes. It imports no MNE,
NumPy, SciPy, Torch, scikit-learn, pyRiemann, MOABB, Braindecode, Zarr, or
Hugging Face package. The complete repository suite is a development
measurement and is not the future single-pass RSS measurement.

## Next gate

1. Commit and push this exact implementation.
2. Confirm both CI jobs are green at that exact commit.
3. Run `loop54-vhdr-ledger --execute` exactly once with those green identifiers.
4. Do not rerun, substitute, amend, or continue into Loop 54-B.

Engineering capability added: a strict, bounded, sibling-blind VHDR parser and
one-shot compatibility-ledger interface are locally synthetic-qualified.

Scientific claim not established: no S20 content was opened and no EEG signal
quality, event or trial validity, neural advantage, decoding accuracy,
generalization, latency, portable hardware, home-use, or clinical result was
established.
