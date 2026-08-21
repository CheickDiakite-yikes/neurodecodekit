# MARC2-VR17C First-Failure-Stable R4 Decomposition Implementation

Date: 2026-08-21

Lane: `MARC2-VR17C`

Status: **Generated implementation and measured qualification complete; remote
implementation proof pending**

Registration:
`registries/marc2_first_failure_stable_r4_decomposition_contract.v0.json`

Implementation record:
`registries/marc2_first_failure_stable_r4_decomposition_implementation.v0.json`

## Registration Barrier

Registration commit `a34896d1d0e4ebc548f4b92bcbd80a70355dc8c2`
passed Base Python job `96737040056` and Optional Neuro Readers job
`96737040177` in CI `32470828824` before implementation began. The module
binds that exact proof and contract SHA-256
`8fdef358e31450be74d8eaf280bb4957d891a19e2364188d5b3d9afc92a26fcc`.

## Added Surface

`src/neurodecodekit/datasets/marc2_first_failure_stable_r4_decomposition.py`
is a standard-library, generated-only composition over the unchanged VR15A
and VR16A adapters. It provides:

- exact contract, remote-proof, and ten-file input validation;
- 24 paired width-equivalence paths over two orders and two replays;
- 20 residual paths over five cases, two orders, and two replays;
- a row-count-stable same-token collision witness using an inert `_acq-copy`
  entity;
- exact generated discrimination of four ordered task or companion classes;
- source immutability and deterministic replay checks;
- recursive aggregate-output, thread, resource, and retention guards;
- 50 direct adversarial refusals; and
- `plan` and `qualify` CLI commands with no path, output, or `execute` surface.

The module has no private executor, network client, archive reader, signal
reader, model, scorer, or retained generated-output path.

## First-Failure Stability

VR17C keeps the two prior parked lanes immutable and tests the behavior that
falsified them. The generated matrix establishes this ordered map:

| Route | Generated case | Unchanged VR16A evidence |
|---|---|---|
| `MARC2VR17C-G1` | control | success |
| `MARC2VR17C-R1` | wrong task | F04 / `core identity differs` |
| `MARC2VR17C-R2` | mixed run spelling | F05 / `companion run spelling differs` |
| `MARC2VR17C-R3` | same-token distinct-name collision | F05 / `normalized run companion is duplicated` |
| `MARC2VR17C-R4` | incomplete set | F05 / `run companion set is incomplete` |

The collision witness preserves all 1,227 rows and the exact numeric run token
while making the full companion name distinct. It therefore reaches the
normalized-collision guard without first triggering a lexical run-spelling
mismatch.

## Measured Qualification

One fresh-process qualification completed route `MARC2VR17C-G1`:

| Measure | Result |
|---|---:|
| Equivalence paths / VR15A calls / VR16A calls | 24 / 24 / 24 |
| Residual paths / VR16A calls | 20 / 20 |
| G1 and R1-R4 count each | 4 |
| Direct refusals | 50 |
| Fixed tracked input | 139,348 bytes |
| Generated input | 19,213,944 bytes |
| Aggregate output | 2,719 bytes |
| Retained generated output | 0 bytes |
| Runtime | 3.7416582500445656 seconds |
| Peak RSS | 36,569,088 bytes |
| Threads / workers / numerical jobs | 1 / 1 / 1 |
| Raw-data / real-cache reads | 0 / 0 |
| Model / training runs | 0 / 0 |

Both equivalence replays produced digest
`09c43c87e186e98a543b173cadf9b0c1edfe278a8e1b3fcf895791402455caed`.
Both residual replays produced digest
`72afc47d8c396ea457d99701c2d3eef34a6200e6232824bc3712dd878d1f735f`.
All six width variants preserved semantic digest
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`.

## Verification

- 20 focused contract, behavior, and record-integrity tests passed.
- The complete dependency-light suite passed 4,576 tests with 204 expected
  skips in 116.003 seconds, 12 tests above the 4,564-test registration
  baseline and with zero new failures.
- The first integrated attempt exposed that macOS `ru_maxrss` is a lifetime
  process high-water mark: an unrelated earlier test raised it above VR17C's
  cap. The unit test now injects the measured fresh-process RSS; the CLI still
  measures and enforces live RSS, and direct cap refusals remain active.
- Ruff 0.15.20 passed the four VR17C Python files.
- Python compilation, strict parsing of all 334 registry JSON files, CLI help
  and plan, and `git diff --check` passed before closeout.
- The measured fresh-process CLI qualification respected every registered cap.

Both remote CI jobs must pass before the implementation proof can close.

## Boundary

This implementation proves deterministic generated first-failure localization
for four structural task or companion classes. It does not identify which
class caused the consumed private R4 result, freeze a real cohort, or authorize
another private read.

No archive member, neural payload, signal sample, target, model, prediction,
score, FW2/CIL1 operation, provider, hardware, release, or scientific claim
was opened. A future private discriminator remains a separately frozen Tier C
packet and fresh packet-bound decision after this exact implementation and
result are remotely green.
