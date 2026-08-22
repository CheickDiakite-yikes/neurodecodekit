# MARC2-VR23A F06 Five-Route Decomposition Preregistration

Date: 2026-08-22

Lane: `MARC2-VR23A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_f06_five_route_decomposition_contract.v0.json`

## Why This Lane Exists

The sole VR22P invocation called the exact VR20A adapter on the registered
418,755-byte target-free structural source, applied the VR21A map, and
consumed at `MARC2VR22P-R4`. This excludes VR20A F07 selection, split, rank,
and reservation arithmetic for that invocation. It retains only VR20A F06.

F06 has two wrapper call sites, but static analysis of the unchanged VR20A and
VR2 helpers exposes five independently reachable first-failure classes. Two
additional defensive raises are not independent hypotheses under the frozen
contract: `bundle taxonomy is unclassified` is unreachable after membership
in the fixed taxonomy union and its exhaustive branches, while `filtered
eligible total differs` follows directly from the earlier exact P01 count and
the filter definition. The implementation must prove those implications from
the exact source AST rather than merely asserting them.

This lane must not reopen VR22P, inspect ignored output, or infer a private
value. It asks only whether generated witnesses can distinguish every
reachable F06 class through the unchanged public adapter.

## Frozen Routes

| Route | Reachable class | Public predicate |
|---|---|---|
| `MARC2VR23A-G1` | accepted control | all VR20A checks pass |
| `MARC2VR23A-R1` | entry-kind arithmetic | exact regular-file/directory counts |
| `MARC2VR23A-R2` | complete-bundle arithmetic | exact 238 grouped run bundles |
| `MARC2VR23A-R3` | participant taxonomy membership | every grouped subject belongs to one fixed taxonomy class |
| `MARC2VR23A-R4` | taxonomy class arithmetic | exact 238/195/43 classification totals |
| `MARC2VR23A-R5` | participant-session distribution | exact published eligible count map |

These routes are aggregate structural classes. None may expose a source row,
member name, participant, count vector, private value, or failure detail.

## Frozen Generated Matrix

Six generated 1,227-row cases run in canonical and reversed order across two
exact replays, for 24 paths and 24 unchanged VR20A calls:

| Case | Mutation | Expected route |
|---|---|---|
| `control_success` | none | `MARC2VR23A-G1` |
| `entry_kind_count_drift` | replace one generated directory row with one unique valid auxiliary regular row | `MARC2VR23A-R1` |
| `extra_complete_bundle` | transform four auxiliary rows into one additional valid bundle | `MARC2VR23A-R2` |
| `unknown_participant_taxonomy` | move one complete bundle to a syntactically valid unknown subject | `MARC2VR23A-R3` |
| `classification_arithmetic_drift` | move one eligible bundle to a known ineligible subject under a collision-free run | `MARC2VR23A-R4` |
| `eligible_session_distribution_drift` | move one eligible bundle to a different eligible participant/session under a collision-free run | `MARC2VR23A-R5` |

Every mutation occurs before validation. The diagnostic preflight must use the
same exact VR20A grouping and VR2 classification helpers, then call unchanged
VR20A exactly once and require its route to agree with the preflight. Source
bytes before and after each call must match.

## Acceptance Gates

1. All 14 fixed inputs match exact byte size and SHA-256.
2. Result commit `6920576a2bc9ad94cf854112c19712ee42bc0c94`
   and both jobs in CI `32595422650` are bound before implementation.
3. Static AST analysis finds exactly two VR20A F06 wrapper call sites and all
   seven bound VR2 safe reasons.
4. Static proof verifies that the two defensive reasons are not independent
   reachable first-failure classes under the frozen contract.
5. All 24 generated paths call unchanged VR20A exactly once.
6. G1 and R1-R5 each appear exactly four times across exact replays.
7. Every diagnostic route agrees with the unchanged VR20A aggregate route.
8. Source bytes remain unchanged across every success and refusal.
9. At least 60 direct contract, AST, route, privacy, replay, resource, and
   output mutations refuse on an exact VR23A refusal route.
10. No generated output is retained.
11. One thread, one worker, one numerical job, 45 seconds, less than 256 MiB
    peak RSS, 24 MiB generated input, 2 MiB temporary output, and 1 MiB
    aggregate output are respected.
12. Every private, ignored-path, consumed-state, archive, signal, target,
    model, provider, hardware, FW2/CIL1, retry, release, and claim counter
    remains zero.

## Stop Rules

- If the AST inventory or logical implication proof differs, park the lane.
- If any witness reaches a different route, changes with row order, changes
  across replay, or mutates its source, park the lane.
- Do not edit VR20A or VR2, relax a predicate, inspect consumed VR22P state, or
  open a private path.
- Do not prepare another private discriminator until the exact generated
  implementation, result, and proof closeout are remotely green.
- A future private discriminator remains a new Tier C packet and could
  establish only one aggregate structural class, not a cohort or neural
  result.

Engineering capability sought: deterministic generated discrimination of all
five reachable VR20A F06 structural classes while proving two defensive guards
are redundant under the frozen public contract.

Scientific claim not established: artifact analysis and generated manifests
establish no neural effect, decoding accuracy, language decoding, unseen-
person generalization, live decoding, or thought-to-text capability.
