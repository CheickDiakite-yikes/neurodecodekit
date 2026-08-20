# MARC2-VR13A R4 Residual Decomposition Implementation

Date: 2026-08-20

Lane: `MARC2-VR13A`

Status: **Generated implementation and measured result complete; remote
implementation proof pending**

Registration:
`registries/marc2_r4_residual_decomposition_contract.v0.json`

Implementation record:
`registries/marc2_r4_residual_decomposition_implementation.v0.json`

## Registration Barrier

Registration commit `1177174c1d466cf357ef3a81a4d96b39321af063`
passed Base Python job `96604083183` and Optional Neuro Readers job
`96604083100` in CI `32424688012` before implementation began. The module
hard-codes that proof and the exact contract SHA-256
`b51472e609d5355bac9902b3c70f37ea7ba3bd39231910e1507926be953e4b55`.

## Added Surface

`src/neurodecodekit/datasets/marc2_r4_residual_decomposition.py` is a
standard-library wrapper around the unchanged VR12A adapter. It provides:

- strict contract, proof, fixed-input, and registration-artifact validation;
- an AST inventory of the exact 23 registered F01-F06 refusal call sites;
- eight generated cases in canonical and reversed order over two replays;
- one-field `ResidualDecision(route)` outputs;
- recursive aggregate-output and forbidden-key validation;
- 54 direct refusal mutations;
- one-thread runtime, RSS, input, output, and zero-retention enforcement; and
- `plan`, `inspect`, and `qualify` CLI commands with no path, output, or
  execute argument.

The implementation has no private executor, network client, archive reader,
signal reader, model, scorer, or retained generated-output path.

## Witness Isolation

The implementation reused existing VR12A generated fixtures and changed only
generated rows before the adapter call. Two first-failure details required
careful isolation:

1. The old duplicate witness mixed padded and unpadded run tokens, so it
   correctly failed earlier at run-spelling inconsistency. VR13A instead adds
   an inert BIDS entity while preserving the same lexical run token, reaching
   the normalized-companion collision branch.
2. `run-04` already exists for the first generated subject/session. The
   bundle-total witness finds the first absent one- or two-digit run and
   converts four existing auxiliary regular-file rows into one complete bundle,
   preserving the 1,227-row and file-kind envelope.

The taxonomy witness moves one complete generated bundle to a syntactically
valid unknown generated subject. None of these fixtures describes the consumed
private source.

## Measured Qualification

One fresh-process qualification completed route `MARC2VR13A-G1`:

| Measure | Result |
|---|---:|
| Generated cases | 8 |
| Orders / replays | 2 / 2 |
| Exact paths / VR12A calls | 32 / 32 |
| G1 and R1-R7 count each | 4 |
| AST refusal call sites | 23 |
| Direct refusals | 54 |
| Generated input | 13,741,736 bytes |
| Aggregate output | 5,514 bytes |
| Retained generated output | 0 bytes |
| Runtime | 2.401633999950718 seconds |
| Peak RSS | 36,978,688 bytes |
| Threads / workers / numerical jobs | 1 / 1 / 1 |
| Raw-data / real-cache reads | 0 / 0 |
| Model / training runs | 0 / 0 |

Both replays produced internal matrix digest
`56430e51b8f97f8c34a2c2fc95706316f2bbf058d7c25b8b8fc2b6a74bf1ae05`.
No adapter call changed its generated source.

## Verification

- 23 focused registration and implementation tests passed in 4.611 seconds.
- The complete dependency-light suite passed 4,246 tests with 204 expected
  skips in 476.120 seconds, 13 tests above the 4,233-test registration
  baseline and with zero new failures.
- The complete-suite runtime was materially higher than the prior 127.106
  seconds; no local rerun was spent. Focused runtime and remote clean-host CI
  are retained as the bounded implementation checks.
- Ruff 0.15.20 passed the module and behavior test.
- The measured CLI qualification respected every registered cap.

## Boundary

This implementation proves generated reachability and deterministic
discrimination of seven structural classes. It does not identify the consumed
private R4 cause, freeze a real cohort, or authorize another private read.

No archive member, neural payload, signal sample, target, model, prediction,
score, FW2/CIL1 operation, provider, hardware, release, or scientific claim
was opened. A future private discriminator remains a separately frozen Tier C
packet and fresh packet-bound decision after this exact implementation and
result are remotely green.
