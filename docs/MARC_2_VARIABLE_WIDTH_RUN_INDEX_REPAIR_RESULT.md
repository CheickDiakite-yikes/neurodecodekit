# MARC2-VR16A Variable-Width Run-Index Repair Result

Date: 2026-08-21

Route: `MARC2VR16A-G1`

Status: **Generated qualification passed; remote implementation proof pending**

Machine result:
`registries/marc2_variable_width_run_index_repair_result.v0.json`

## Result

The registered generated matrix passed all acceptance gates. Six source
spellings ran in canonical and reversed order over two exact replays, producing
24 successful paths:

| Generated spelling | Meaning |
|---|---|
| `unpadded` | one digit for generated runs |
| `two_digit_control` | established two-digit control |
| `three_digit` | three-digit zero padding |
| `six_digit` | six-digit zero padding |
| `sixty_four_digit` | 64-digit zero padding |
| `bundle_consistent_mixed_width` | width varies by logical bundle |

All six raw source hashes and all six selected-name hashes were distinct, but
the normalized semantic cohort digest was identical. This demonstrates that
lexical zero-padding width no longer changes semantic run identity, selection,
split, or reservation accounting in the generated pipeline.

The qualification also passed 50 direct refusals spanning syntax, source
envelope, row schema, task identity, companion spelling, normalized collision,
selection, output firewall, thread environment, and resource caps.

## Measurements

- fixed tracked inputs verified: 121,238 bytes;
- generated input processed: 17,532,166 bytes;
- temporary peak: 917,845 bytes;
- aggregate output: 2,843 bytes;
- retained generated output: 0 bytes;
- runtime: 2.224372999975458 seconds;
- peak RSS: 34,717,696 bytes;
- threads, workers, and numerical jobs: one each; and
- raw-data reads, real-cache reads, model runs, and training runs: zero.

End-to-end latency was not measured because this is an in-memory structural
qualification, not a neural or live pipeline.

## What Changed In Our Knowledge

VR15P established only that the real target-free structural source did not fit
the old one-or-two-digit width assumption. VR16A now shows that a
standards-aligned, source-preserving variable-width parser can recover the
same frozen selection semantics across a deliberately broad generated width
matrix without weakening companion, split, storage, privacy, or claim guards.

This does not establish that width is the only remaining issue in the real
source. That requires one new, preregistered target-free private confirmation.

## Warnings And Unavailable Fields

- The actual private run token, filename, path, row, identity, and participant
  remain unavailable.
- A real cohort is not established.
- No archive member or neural payload was accessed.
- No target, label, model, prediction, or score exists in this lane.
- The generated result has no scientific or decoding claim value.

## Next Gate

Commit, push, and require both CI jobs green for the exact implementation and
result. Only then may an all-false private-confirmation authorization packet be
prepared. That packet would still require a fresh Tier C decision before one
new target-free structural read.

FW2 and CIL1 remain ineligible. This result establishes no neural effect,
decoding accuracy, language decoding, live decoding, thought-to-text result,
unseen-person generalization, or portable/clinical capability.
