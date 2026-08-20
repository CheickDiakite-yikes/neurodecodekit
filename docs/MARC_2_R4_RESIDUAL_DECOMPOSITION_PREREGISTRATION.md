# MARC2-VR13A R4 Residual Decomposition Preregistration

Date: 2026-08-20

Lane: `MARC2-VR13A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_r4_residual_decomposition_contract.v0.json`

## Why This Lane Exists

The sole VR12P execution called the exact VR12A adapter on the registered
418,755-byte target-free structural source and consumed at aggregate route
`MARC2VR12P-R4`. That proves the one- or two-digit run-index repair was not
sufficient. It does not reveal which remaining predicate failed.

R4 currently collapses VR12A routes F01 through F06. Committed proof and the
earlier VR11P pass over the same registered source identity exclude contract
drift and the outer live-envelope class. VR10A's committed producer audit also
excludes generic row-shape, path-safety, CRC, integer, ZIP, entry-kind, and
full-name-duplication failures. The unresolved first-failure classes begin at
the repaired suffix-bearing identity and continue through task, companion,
bundle-total, and taxonomy validation.

This lane must not inspect VR12P output, reopen the private source, or infer a
private value. It asks only whether generated witnesses can exercise every
remaining exact branch deterministically.

## Frozen Residual Classes

The exact ordered classes are:

| Route | Frozen class | Exact VR12A branch |
|---|---|---|
| `MARC2VR13A-R1` | residual suffix-bearing BIDS identity | F03 P15 identity after one/two-digit run repair |
| `MARC2VR13A-R2` | exact Freewill task token | F04 P16 task spelling |
| `MARC2VR13A-R3` | companion run-token inconsistency | F05 P18 lexical run spelling |
| `MARC2VR13A-R4` | normalized companion collision | F05 P18 duplicate normalized companion |
| `MARC2VR13A-R5` | incomplete companion set | F05 P19 four-companion completeness |
| `MARC2VR13A-R6` | repaired bundle-total mismatch | F06 source kind or run-bundle total |
| `MARC2VR13A-R7` | taxonomy or eligibility mismatch | F06 classification/filter arithmetic |

`MARC2VR13A-G1` is reserved for generated controls that pass the unchanged
VR12A adapter. The order above is first-failure order, not a claim about the
consumed private source.

## Frozen Generated Matrix

After this exact registration is committed, pushed, and both remote jobs are
green, one dependency-free implementation may build eight full-scale generated
cases:

| Case | Generated mutation | Expected VR13A route |
|---|---|---|
| `control_success` | none | `MARC2VR13A-G1` |
| `residual_bids_identity` | preserve a required suffix while breaking repaired filename/path identity | `MARC2VR13A-R1` |
| `wrong_task_token` | replace exact lowercase `task-freewill` | `MARC2VR13A-R2` |
| `mixed_run_tokens` | use padded and unpadded tokens inside one logical bundle | `MARC2VR13A-R3` |
| `duplicate_normalized_companion` | create two source-exact names for one normalized run/suffix key | `MARC2VR13A-R4` |
| `incomplete_companion_set` | move one required companion to a safe auxiliary name | `MARC2VR13A-R5` |
| `extra_complete_bundle` | transform four auxiliary rows into one extra complete valid bundle | `MARC2VR13A-R6` |
| `unknown_subject_taxonomy` | move one complete bundle to a syntactically valid unknown subject | `MARC2VR13A-R7` |

Each case runs in canonical and reversed order across two exact replays: 32
VR12A calls total, with four G1 control paths and four paths for each R1-R7
route. Mutations occur before VR12A. The implementation emits only case names,
route counts, deterministic digests, resources, warnings, and zero counters.

## Acceptance Gates

1. All 15 committed inputs match exact byte size and SHA-256.
2. Static AST analysis finds the exact 23 F01-F06 refusal call sites and their
   frozen route/reason pairs.
3. Committed evidence excludes only F01, F02, and the previously proven generic
   F03 producer invariants; no private value is inferred.
4. Exactly seven ordered residual classes remain.
5. All 32 generated paths call the unchanged VR12A adapter exactly once.
6. Every route appears exactly four times and both complete replays match.
7. Generated source objects remain unchanged by validation.
8. At least 50 direct contract, route, privacy, determinism, resource, and
   output mutations refuse on the expected route.
9. No generated output is retained.
10. One thread, one worker, one numerical job, 30 seconds, less than 256 MiB
    peak RSS, 24 MiB generated input, and 1 MiB aggregate output are respected.
11. Every private, ignored-path, archive, signal, target, model, provider,
    hardware, FW2/CIL1, retry, release, and claim counter remains zero.

## Stop Rules

- If the AST inventory differs from the frozen 23 call sites, park the lane.
- If a witness reaches the wrong exact VR12A route, changes with row order, or
  changes across replay, park the lane.
- Do not modify VR12A, relax a predicate, inspect a consumed output, or open a
  private path.
- Do not prepare a private discriminator packet until the exact generated
  implementation and result are committed, pushed, and remotely green.
- A later private discriminator would still be one new Tier C decision and
  could establish only one aggregate structural class, not a cohort or neural
  result.

## Claim Boundary

Engineering capability sought: prove that every residual VR12P R4 structural
class is independently reachable and distinguishable through the unchanged
VR12A adapter using only generated manifests.

Scientific claim not established: artifact-only source analysis and generated
structural manifests establish no neural effect, decoding accuracy, language
decoding, live decoding, or thought-to-text capability.
