# MARC2-VR15A Suffix-Identity Grammar Decomposition Implementation

Date: 2026-08-21

Lane: `MARC2-VR15A`

Status: **Generated qualification passed locally; remote implementation proof
pending**

Frozen contract:
`registries/marc2_suffix_identity_grammar_decomposition_contract.v0.json`

Machine implementation record:
`registries/marc2_suffix_identity_grammar_decomposition_implementation.v0.json`

## Green Registration Boundary

Registration commit `185fbc54366fd0eaf0ed4e994511e4485514b53e`
passed Base Python job `96670618009` and Optional Neuro Readers job
`96670617843` in CI `32447836662` before implementation began. The fixed
contract SHA-256 is
`10644f5487069c3143a55f1910d07f7e7572bcd6ed21fdc2620a8a649b26a058`.

No private or Git-ignored source was opened while waiting for or verifying
that proof.

## Implemented Surface

`src/neurodecodekit/datasets/marc2_suffix_identity_grammar_decomposition.py`
adds a standard-library-only, generated-only diagnostic interface that:

- verifies all 11 fixed tracked inputs by exact size and SHA-256;
- AST-binds the unchanged VR12A repaired-member regex and exact P15 guard;
- builds one clean control, 15 isolated single-class witnesses, and one
  multiple-class witness from the existing 1,227-row generated source;
- calls `vr12a.adapt_repaired_source` exactly once for every matrix path;
- requires every single-class witness to reach exact `MARC2VR12A-F03` with
  `P15 suffix-bearing BIDS identity differs` before classification;
- emits only G1 or R1-R16 aggregate routes, counts, and digests;
- rejects member names, paths, identities, rows, targets, predictions, and
  private-manifest fields from public output;
- checks 70 direct contract, proof, artifact, classifier, matrix, privacy,
  resource, and thread refusals; and
- exposes `plan`, `inspect`, and `qualify` commands with no path, output, or
  execute option.

The module has no private executor, archive reader, signal reader, network
client, model, scorer, or retained generated-output path. VR12A and every
consumed predecessor remain unchanged.

## Witness Isolation

Each R1-R15 fixture changes one generated member name while preserving the
required EEG/events suffix and the rest of the 1,227-row envelope. The
classifier evaluates the frozen grammar in order: tail depth, prefix, subject
and session directories, modality, filename subject and session identities,
task shape, optional entities, and run presence, position, character class,
and width.

R16 changes two generated rows into two distinct valid P15 grammar classes.
The route is selected only from the set of aggregate classes after the one
VR12A call, so canonical and reversed source order agree. No generated member
name or per-source result is retained.

## Measured Qualification

One fresh-process qualification completed route `MARC2VR15A-G1`:

| Measure | Result |
|---|---:|
| Generated cases | 17 |
| Orders / replays | 2 / 2 |
| Exact paths / VR12A calls | 68 / 68 |
| G1 and R1-R16 count each | 4 |
| Single-class / multiple-class P15 paths | 60 / 4 |
| Direct refusals | 70 |
| Fixed tracked artifacts | 12 files, 224,681 bytes |
| Generated input | 29,199,868 bytes |
| Aggregate output | 6,587 bytes |
| Retained generated output | 0 bytes |
| Runtime | 3.9292239159694873 seconds |
| Peak RSS | 49,037,312 bytes |
| Threads / workers / numerical jobs | 1 / 1 / 1 |
| Raw-data / real-cache reads | 0 / 0 |
| Model / training runs | 0 / 0 |

Both replays produced internal matrix digest
`a35eb9dd8f5275af6096b4a5bde7bb8e917924d7788d1788ecefacd7bea2accd`.
No VR12A call changed its generated source.

## Verification

- 26 focused registration, implementation, and record tests passed in 10.484
  seconds.
- The complete dependency-free suite passed 4,380 tests with 204 expected
  skips in 120.503 seconds.
- The pre-implementation registration baseline was 4,359 tests, so the change
  adds 21 behavior and record tests with zero new failure.
- Pinned Ruff 0.15.20 passed the complete repository; the owned module and
  tests also pass in isolation.
- Compileall, CLI help, inspection, and diff hygiene passed.
- The fresh-process qualification stayed below every frozen runtime, RSS,
  generated-input, aggregate-output, and retention cap.

## Boundary

This implementation proves generated reachability and deterministic aggregate
discrimination of 15 suffix-identity grammar classes plus a multiple-class
route. It does not identify the consumed private failure, freeze a real cohort,
or authorize a new private read.

No archive member, neural payload, signal sample, target, model, prediction,
score, FW2/CIL1 operation, provider, hardware, release, or scientific claim
was opened. A future one-shot private discriminator remains a separately
frozen Tier C packet and fresh packet-bound decision after the exact
implementation is remotely green.
