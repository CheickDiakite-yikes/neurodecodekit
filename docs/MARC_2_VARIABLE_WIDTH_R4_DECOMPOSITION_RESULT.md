# MARC2-VR17A Variable-Width R4 Decomposition Result

Date: 2026-08-21

Lane: `MARC2-VR17A`

Status: **Parked at H3; preregistered equivalence expectation falsified**

Machine result:
`registries/marc2_variable_width_r4_decomposition_result.v0.json`

## Green Registration

Registration `e1c9366627e26a4a81c6eff152a8779eba5aa109` passed Base
Python job `96726051438`, Optional Neuro Readers job `96726051667`, and CI
`32467147580` before the generated preflight.

## Exact Finding

VR17A-H3 incorrectly required all six VR16A width variants to classify as
VR15A R15 before passing VR16A. One generated canonical-order pass showed:

| Variant class | Count | VR15A | VR16A |
|---|---:|---|---|
| already-supported controls | 2 | `MARC2VR15A-G1` | `MARC2VR16A-G1` |
| extended-width repairs | 4 | `MARC2VR15A-R15` | `MARC2VR16A-G1` |

The two controls are `unpadded` and `two_digit_control`. The four repair cases
are `three_digit`, `six_digit`, `sixty_four_digit`, and
`bundle_consistent_mixed_width`. All six produced semantic digest
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`.

The pass made six VR15A calls and six VR16A calls over 2,651,670 generated
bytes in 0.6208636660012417 seconds at 33,390,592-byte peak RSS. It used one
thread, retained zero output, and made zero private operations.

## Disposition

The literal H3 gate failed, so the registered 24-path equivalence matrix and
20-path residual matrix were not run. VR17A is parked and will not be amended
or reinterpreted after the result.

The corrected design is narrow: preserve the two controls as G1-to-G1 and
require only the four extended-width variants to move from R15 to G1. A new
VR17B registration must freeze that 2/4 mapping before any new implementation.

No consumed VR15P/VR16P state, `.codex_work`, archive, neural payload, signal,
target, model, prediction, score, FW2/CIL1, network, provider, device,
hardware, release, or other project was touched.

## Verification

- Focused result tests: 6 passed.
- Complete dependency-light suite: 4,541 passed with 204 expected skips in
  108.271 seconds.
- Ruff 0.15.20: passed.
- Registry parse: 329 JSON registries parsed.
- `git diff --check`: passed.

Engineering insight established: the exact cross-adapter equivalence is a
two-control/four-repair partition, and all six spellings preserve one semantic
selection digest.

Scientific claim not established: generated structural equivalence establishes
no neural effect, decoding accuracy, language decoding, live decoding, or
thought-to-text capability.
