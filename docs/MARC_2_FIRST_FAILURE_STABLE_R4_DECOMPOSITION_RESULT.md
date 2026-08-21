# MARC2-VR17C First-Failure-Stable R4 Decomposition Result

Date: 2026-08-21

Route: `MARC2VR17C-G1`

Status: **Generated qualification passed; remote implementation proof pending**

Machine result:
`registries/marc2_first_failure_stable_r4_decomposition_result.v0.json`

## Result

The registered generated matrices passed every acceptance gate. The
equivalence matrix reproduced two supported VR15A G1-to-VR16A G1 controls and
four extended-width VR15A R15-to-VR16A G1 repairs in both source orders and
two exact replays. All 24 paired paths preserved one semantic digest.

The residual matrix then ran five generated cases in both orders and two exact
replays. Control plus four first-failure-stable routes each appeared exactly
four times:

| Route | Localized generated class |
|---|---|
| `MARC2VR17C-G1` | accepted control |
| `MARC2VR17C-R1` | core task or identity differs |
| `MARC2VR17C-R2` | companion run spelling differs |
| `MARC2VR17C-R3` | normalized companion collision |
| `MARC2VR17C-R4` | companion set incomplete |

This corrects both false frozen expectations that parked VR17B without
amending, rerunning, or reinterpreting that consumed lane.

## Measurements

- fixed tracked inputs verified: 139,348 bytes;
- generated input processed: 19,213,944 bytes;
- aggregate output: 2,719 bytes;
- retained generated output: 0 bytes;
- runtime: 3.7416582500445656 seconds;
- peak RSS: 36,569,088 bytes;
- threads, workers, and numerical jobs: one each;
- direct adversarial refusals: 50; and
- raw-data reads, real-cache reads, model runs, and training runs: zero.

End-to-end latency was not measured because this is an in-memory structural
qualification, not a neural or live pipeline.

## Verification

Twenty focused tests and all 4,576 dependency-light tests pass with 204
expected skips. Ruff 0.15.20, Python compilation, strict parsing of all 334
registry JSON files, CLI help and plan, and `git diff --check` also pass.
Remote implementation proof remains pending.

## What Changed In Our Knowledge

VR16P left three broad possibilities after its one consumed target-free read:
numeric identity, exact task token, or companion validation. VR17C now gives a
generated, first-failure-stable classifier for the four remaining task and
companion classes that can be used in a future one-shot private discriminator.

That is useful engineering evidence, not real-cohort evidence. The private
cause remains unknown until a new packet is frozen, authorized, implemented,
proved remotely green, and executed once.

## Warnings And Unavailable Fields

- The consumed private predicate, value, filename, path, row, identity, and
  participant remain unavailable.
- A real cohort is not established.
- No archive member or neural payload was accessed.
- No target, label, model, prediction, or score exists in this lane.
- The generated result has no scientific or decoding claim value.

## Next Gate

Commit, push, and require both CI jobs green for the exact implementation and
result. Then close the exact implementation proof without repeating the
qualification or touching private state. Only after that proof is green may
Tier A prepare an all-false private-discriminator authorization packet; the
future private read still requires a fresh Tier C decision.

FW2 and CIL1 remain ineligible. This result establishes no neural effect,
decoding accuracy, language decoding, live decoding, thought-to-text result,
unseen-person generalization, or portable or clinical capability.
