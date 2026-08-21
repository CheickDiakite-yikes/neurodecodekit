# MARC2-VR17C First-Failure-Stable R4 Decomposition Preregistration

Date: 2026-08-21

Lane: `MARC2-VR17C`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_first_failure_stable_r4_decomposition_contract.v0.json`

## Why VR17C Exists

VR17A parked a false equivalence expectation. VR17B corrected the equivalence
map but parked when two residual first-failure expectations proved false. Both
lanes remain immutable.

VR17C freezes the exact behavior observed from unchanged VR16A:

- wrong-task reaches F04 / `core identity differs` before the later explicit
  task guard;
- mixed run spelling reaches F05 / `companion run spelling differs`;
- a normalized collision must preserve the same run token while using a unique
  full name; and
- a removed companion reaches F05 / `run companion set is incomplete`.

## Frozen Collision Construction

Start from a generated `three_digit` source without changing its 1,227-row
envelope. Select the first core row and the first auxiliary regular-file row
that is not a core companion. Replace the auxiliary row with a deep copy of the
core row, insert `_acq-copy` immediately before `_run-` in its member name, and
increment the copied local-header offset by one.

This creates two distinct full names with the same subject, session, task,
numeric run, exact run-token spelling, and required suffix. A generated
development check reached F05 / `normalized run companion is duplicated`.
The full matrix must independently replay that behavior in both source orders.

## Frozen Hypotheses

1. The nonnumeric helper guard remains unreachable after the core regex has
   matched an ASCII numeric run token.
2. Wrong-task deterministically reaches F04 / `core identity differs`; the
   later `Freewill task differs` guard remains unreachable.
3. Two supported controls replay VR15A G1 to VR16A G1, and four extended-width
   repairs replay VR15A R15 to VR16A G1, all with one semantic digest.
4. The four first-failure-stable residual classes are distinct under both row
   orders and two replays.

Any failed hypothesis parks VR17C.

## Frozen Routes And Matrix

| Route | Case | Exact VR16A result |
|---|---|---|
| `MARC2VR17C-G1` | control | success |
| `MARC2VR17C-R1` | wrong task | F04 / `core identity differs` |
| `MARC2VR17C-R2` | mixed run spelling | F05 / `companion run spelling differs` |
| `MARC2VR17C-R3` | normalized collision | F05 / `normalized run companion is duplicated` |
| `MARC2VR17C-R4` | incomplete set | F05 / `run companion set is incomplete` |

- Equivalence: six variants, two orders, two replays, 24 paired paths, 24
  unchanged VR15A calls, and 24 unchanged VR16A calls.
- Residuals: five cases, two orders, two replays, 20 paths and 20 unchanged
  VR16A calls; G1 and R1-R4 must each occur four times.
- Total: 24 VR15A calls, 44 VR16A calls, deterministic replay, source
  immutability, at least 50 direct refusals, and zero retained output.

## Resource And Authority Boundary

- one CPU thread, one worker, one numerical job;
- 30 seconds maximum;
- less than 256 MiB peak RSS;
- at most 40 MiB generated input;
- at most 1 MiB aggregate output; and
- zero retained generated output.

Implementation may begin only after this exact registration commit passes both
required CI jobs. The lane authorizes no `.codex_work`, private source,
consumed output, cohort, archive, neural payload, signal, event, target, model,
prediction, score, network, provider, device, hardware, other project,
FW2/CIL1, release, or scientific-claim operation.

Eight focused contract tests and all 4,564 dependency-light tests pass with
204 expected skips in 108.295 seconds. Ruff 0.15.20, strict parsing of all 332
registry JSON files, and `git diff --check` also pass.

## Next Gate

Commit, push, and green this registration before implementation. A successful
generated result may justify preparation of an all-false private discriminator
packet, but that future read remains Tier C and separately decision-bound.

Engineering capability sought: deterministic first-failure localization of
the remaining generated task and companion ambiguity.

Scientific claim not established: this lane contains no neural data, decoding
experiment, language result, live run, or thought-to-text evidence.
