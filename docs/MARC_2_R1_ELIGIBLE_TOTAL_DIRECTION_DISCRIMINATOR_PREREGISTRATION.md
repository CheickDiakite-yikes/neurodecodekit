# MARC2-VR31A R1 Eligible-Total Direction Discriminator Preregistration

Date: 2026-08-23

Lane: `MARC2-VR31A`

Status: **Frozen artifact-only and generated-only registration**

Machine contract:
`registries/marc2_r1_eligible_total_direction_discriminator_contract.v0.json`

## Why This Is Next

The sole VR30P invocation consumed at `MARC2VR30P-R1` without freezing a
cohort. That route proves only that the filtered eligible total differs from
the registered public total of 195. It does not reveal the observed total,
direction, magnitude, participant, row, or cohort, and the later participant-
session distribution check was not reached.

VR31A is the smallest useful decomposition of that result. It will prove on
generated fixtures that an unchanged VR29A R1 can be mapped to exactly one of
two aggregate-safe classes:

1. filtered eligible total is below 195; or
2. filtered eligible total is above 195.

The discriminator may compare an internal generated count with the immutable
threshold only long enough to choose a route. It may never return, log, hash,
serialize, or retain the observed count or difference.

## Frozen Matrix

Eight generated 1,227-row cases are fixed:

| Case | Expected VR29A route | Expected VR31A route |
|---|---|---|
| `exact_public_control` | `MARC2VR29A-G1` | `MARC2VR31A-G1` |
| `single_session_exclusion_removed` | `MARC2VR29A-G2` | `MARC2VR31A-G2` |
| `eligible_bundle_removed` | `MARC2VR29A-R1` | `MARC2VR31A-R1` |
| `eligible_bundle_added` | `MARC2VR29A-R1` | `MARC2VR31A-R2` |
| `eligible_distribution_shift` | `MARC2VR29A-R2` | `MARC2VR31A-R3` |
| `eligible_distribution_shift_second` | `MARC2VR29A-R2` | `MARC2VR31A-R3` |
| `unknown_participant_bundle` | `MARC2VR29A-R3` | `MARC2VR31A-R3` |
| `incomplete_companion_set` | `MARC2VR29A-R3` | `MARC2VR31A-R3` |

Each case runs in canonical and reversed order across two exact replays. The
32 paths must make exactly 32 unchanged VR29A calls. Only the eight VR29A R1
paths may run the local direction comparison. Expected VR31A route counts are
G1=4, G2=4, R1=4, R2=4, and R3=16.

Static AST coverage must bind the single immutable VR2 predicate
`len(filtered) != 195` inside `_filter_and_validate_eligible`. At least 70
direct refusal checks cover artifact identity, route mapping, threshold
immutability, observed-count non-retention, deterministic replay, source
immutability, resource caps, and CLI override refusal.

## Boundaries

Implementation may use only the standard library, the eight committed inputs,
unchanged generated-safe VR29A/VR25A/VR2 helpers, and invocation-created
generated fixtures. It may expose `plan` and `qualify` commands only. It must
have no private executor and no source path, URL, route, count, threshold,
retry, output, or resource override.

It may not touch `.codex_work`, readiness, a consumed marker, VR20P, VR22P,
VR24P, VR26P, VR28P, or VR30P state, an archive, signal, event, target, label,
model, prediction, score, network, provider, stream, device, hardware, or
another project. It may not expose an observed total, difference, private
value, participant, distribution, or source detail. Generated output
retention is zero.

Registration must be committed, pushed, and both CI jobs green before any
implementation begins. A passed generated discriminator would not identify
the consumed private R1 direction. Another private read would still require a
new all-false Tier C packet, proof barriers, and a fresh packet-bound decision.

## Acceptance Gates

1. All eight fixed inputs match exact byte counts and SHA-256 digests.
2. VR30P result commit `a6e1ac5c17c2cffd4d07222c1f3eebcd05fb6a22`
   and both jobs in CI `32626086478` are bound before implementation.
3. Static analysis binds exactly one immutable `len(filtered) != 195`
   predicate in VR2 eligible filtering.
4. All 32 generated paths call unchanged VR29A exactly once.
5. Only the eight VR29A R1 paths perform one direction comparison.
6. VR31A route counts are G1 four, G2 four, R1 four, R2 four, and R3 sixteen.
7. No returned or retained object contains an observed count or difference.
8. Every call leaves its generated source byte-identical.
9. Both replays are exact and order-independent.
10. At least 70 direct refusals pass.
11. No generated source or report is retained.
12. One CPU thread, worker, and numerical job; 30 seconds; less than 256 MiB
    peak RSS; 32 MiB generated input; and 1 MiB aggregate output are respected.
13. Complete dependency-light tests, focused Ruff, registry parsing, CLI help,
    and diff hygiene pass.
14. Every private, archive, neural, target, model, network, hardware,
    FW2/CIL1, other-project, and claim counter remains zero.

Engineering capability proposed: distinguish below-expected from above-
expected filtered eligible totals through unchanged generated VR29A boundaries
without exposing an observed count or difference.

Scientific claim not established: this registration accesses no neural
payload, target, model, prediction, or score and establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
