# MARC2-VR17B Corrected Variable-Width R4 Decomposition Result

Date: 2026-08-21

Lane: `MARC2-VR17B`

Status: **Parked after two frozen residual expectations failed**

Machine result:
`registries/marc2_corrected_variable_width_r4_decomposition_result.v0.json`

## Green Registration

Registration `cde85696de8ed998d15c79630265059264ba1f2c` passed Base
Python job `96732149989`, Optional Neuro Readers job `96732149634`, and CI
`32469173279` before generated work.

## Five-Case Preflight

One canonical-order generated preflight called unchanged VR16A exactly once for
each frozen residual case:

| Case | Frozen expectation | Observed VR16A result |
|---|---|---|
| control | success | success with the registered semantic digest |
| wrong task | F04 / `Freewill task differs` | F04 / `core identity differs` |
| mixed lexical tokens | F05 / `companion run spelling differs` | matched |
| duplicate normalized companion | F05 / `normalized run companion is duplicated` | F05 / `companion run spelling differs` |
| incomplete companion set | F05 / `run companion set is incomplete` | matched |

The wrong-task result confirms H2's reachability claim but contradicts the
frozen R1 reason. The existing duplicate witness changes run spelling before
it can reach the normalized-collision branch, so it cannot distinguish R3 from
R2. Because two exact route/reason gates failed, the 24-path equivalence matrix,
20-path residual matrix, direct-refusal suite, and report emission did not run.

## Disposition

VR17B is parked at `MARC2VR17B-P01` without amendment, reinterpretation, retry,
or full qualification. No implementation module was added.

The preflight made five VR16A calls and zero VR15A calls. External command wall
time was 0.3 seconds. Generated input bytes and peak RSS were not instrumented
by this early semantic probe and are explicitly unavailable; no retained
output was created. Every private and scientific operation counter is zero.

## Verification

- Focused VR17B contract and result tests: 14 passed.
- Complete dependency-light suite: 4,556 passed with 204 expected skips in
  107.672 seconds.
- Ruff 0.15.20: passed.
- Registry parse: 331 JSON files parsed.
- `git diff --check`: passed.

The next safe design is a separately registered `MARC2-VR17C` that:

- freezes F04 / `core identity differs` for the generated task-token class;
- preserves F05 / `companion run spelling differs` for mixed spelling;
- creates a distinct optional-entity companion with the same normalized
  subject/session/run/suffix so F05 / `normalized run companion is duplicated`
  is actually reached; and
- preserves F05 / `run companion set is incomplete` for completeness.

Engineering insight established: two generated first-failure expectations were
wrong, and the collision witness must differ lexically without changing the run
token.

Scientific claim not established: no private cohort, neural payload, decoding
experiment, language result, live run, or thought-to-text evidence was reached.
