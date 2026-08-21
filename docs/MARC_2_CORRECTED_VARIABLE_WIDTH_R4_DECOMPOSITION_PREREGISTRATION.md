# MARC2-VR17B Corrected Variable-Width R4 Decomposition Preregistration

Date: 2026-08-21

Lane: `MARC2-VR17B`

Status: **Frozen artifact-only and generated-only correction; no private access
or scientific claim**

Machine contract:
`registries/marc2_corrected_variable_width_r4_decomposition_contract.v0.json`

## Why VR17B Exists

VR17A correctly required its hypotheses to fail closed, then its first bounded
generated preflight falsified literal H3. The old VR15A adapter already accepts
`unpadded` and `two_digit_control`; only the four extended-width cases move
from VR15A R15 to VR16A success. VR17A is parked and will not be amended.

VR17B freezes the observed partition before any new run:

| Class | Variants | Required transition |
|---|---|---|
| supported controls | `unpadded`, `two_digit_control` | VR15A G1 to VR16A G1 |
| extended-width repairs | `three_digit`, `six_digit`, `sixty_four_digit`, `bundle_consistent_mixed_width` | VR15A R15 to VR16A G1 |

Every path must preserve semantic digest
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`.

## Frozen Hypotheses

1. The nonnumeric helper guard in VR16A is unreachable after the exact core
   regex has matched an ASCII numeric run token.
2. The explicit post-normalization task guard is unreachable because unchanged
   VR12A rejects a wrong task first on F04.
3. The exact 2-control/4-repair transition table replays in both source orders
   and two repetitions with one invariant semantic digest.
4. If H1-H3 pass, committed producer evidence excludes F03 from the aggregate
   candidate set without revealing or inferring a private value.

Any failed hypothesis parks VR17B. No route may be reinterpreted after the
generated result.

## Frozen Residual Classes

| Route | Generated class | Exact VR16A evidence |
|---|---|---|
| `MARC2VR17B-R1` | exact lowercase Freewill task token | F04 plus allowlisted wrong-task reason |
| `MARC2VR17B-R2` | companion lexical run spelling | F05 plus allowlisted mixed-spelling reason |
| `MARC2VR17B-R3` | normalized companion collision | F05 plus allowlisted duplicate-companion reason |
| `MARC2VR17B-R4` | four-companion completeness | F05 plus allowlisted incomplete-set reason |

`MARC2VR17B-G1` is the generated control. Safe reasons may be used only inside
generated qualification; a future private wrapper may expose only the
aggregate R1-R4 route under a new Tier C packet.

## Frozen Matrix

- Equivalence: six variants, two source orders, two replays, 24 paired paths,
  24 unchanged VR15A calls, and 24 unchanged VR16A calls.
- Residuals: one control plus four mutations, two orders, two replays, 20
  paths, and 20 unchanged VR16A calls.
- Total: 24 VR15A calls, 44 VR16A calls, deterministic replay, source
  immutability, at least 48 direct refusals, and zero retained output.

The four residual routes and G1 must each appear exactly four times. Generated
reports may contain only aggregate counts, hashes, resources, gates, warnings,
and zero-valued operation counters.

## Resource And Authority Boundary

- one CPU thread, one worker, one numerical job;
- 30 seconds maximum;
- less than 256 MiB peak RSS;
- at most 40 MiB generated input;
- at most 1 MiB aggregate output; and
- zero retained generated output.

This registration authorizes only generated implementation after its exact
commit passes both required remote CI jobs. It authorizes no `.codex_work`,
private source, consumed output, cohort, archive, neural payload, signal,
event, target, model, prediction, score, network, provider, device, hardware,
other project, FW2/CIL1, release, or scientific-claim operation.

Eight focused contract tests and all 4,550 dependency-light tests pass with
204 expected skips in 108.078 seconds. Ruff 0.15.20, strict parsing of all 330
registry JSON files, and `git diff --check` also pass.

## Next Gate

Commit, push, and green this exact registration before implementation. After a
successful generated result and separate remote proof, Tier A may prepare one
all-false private four-route discriminator request. A private read remains Tier
C and requires a fresh packet-bound decision.

Engineering capability sought: a deterministic generated reduction of the
remaining R4 structural ambiguity after correcting the control/repair map.

Scientific claim not established: this lane contains no neural data, decoding
experiment, language result, live run, or thought-to-text evidence.
