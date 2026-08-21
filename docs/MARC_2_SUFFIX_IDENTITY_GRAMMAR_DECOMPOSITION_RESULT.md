# MARC2-VR15A Suffix-Identity Grammar Decomposition Result

Date: 2026-08-21

Route: `MARC2VR15A-G1`

Status: **Generated qualification passed; remote implementation proof pending**

Machine result:
`registries/marc2_suffix_identity_grammar_decomposition_result.v0.json`

## Result

The registered generated matrix passed every local acceptance gate. The
unchanged VR12A adapter was called exactly 68 times: 17 cases in canonical and
reversed order across two exact replays. G1 and each R1-R16 route appeared
exactly four times.

The fifteen single-class witnesses all reached exact VR12A route
`MARC2VR12A-F03` with the frozen P15 reason before classification. The
multiple-class witness returned R16 in both orders and replays. Both complete
replays produced digest
`a35eb9dd8f5275af6096b4a5bde7bb8e917924d7788d1788ecefacd7bea2accd`.
No generated source changed during validation.

## Measurements

- fixed tracked artifacts verified: 12 files, 224,681 bytes;
- generated input processed: 29,199,868 bytes;
- aggregate output: 6,587 bytes;
- retained generated output: 0 bytes;
- runtime: 3.9292239159694873 seconds;
- peak RSS: 49,037,312 bytes;
- threads, workers, and numerical jobs: one each;
- direct refusal mutations passed: 70; and
- raw-data reads, real-cache reads, model runs, and training runs: zero.

End-to-end latency was not measured because this was an in-memory structural
qualification, not a neural or live decoding pipeline.

## What Changed In Our Knowledge

Before VR15A, the consumed aggregate result identified only the broad P15
suffix-bearing identity class. VR15A now proves that its fifteen constituent
grammar failures and a multiple-failure state are independently reachable and
deterministically distinguishable through the unchanged adapter. A future
one-shot private discriminator can therefore ask one bounded aggregate
question instead of reopening broad structural diagnostics.

This generated result does not reveal which class occurred in the private
source. Generated reachability cannot substitute for a private observation.

## Warnings And Unavailable Fields

- The consumed private grammar class and failed value are unavailable.
- A real cohort is unavailable.
- No private member name, path, identity, row, task, run, or per-source outcome
  was retained.
- No archive member or neural payload was accessed.
- No target, label, model, prediction, or score exists in this lane.
- Generated structural routes have no scientific or decoding claim value.

## Next Gate

Commit, push, and require both CI jobs green for the exact implementation and
result. Only after that proof may an all-false one-shot private-discriminator
packet be prepared. The packet would still require a fresh Tier C decision
before any private read.

FW2 and CIL1 remain ineligible. This result establishes no neural effect,
decoding accuracy, language decoding, live decoding, thought-to-text result,
unseen-person generalization, or portable or clinical capability.
