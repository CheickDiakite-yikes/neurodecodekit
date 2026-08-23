# MARC2-VR29A R1 Inventory/Distribution Discriminator Preregistration

Date: 2026-08-23

Lane: `MARC2-VR29A`

Status: **Frozen artifact-only and generated-only registration**

Machine contract:
`registries/marc2_r1_inventory_distribution_discriminator_contract.v0.json`

## Why This Is Next

The sole VR28P invocation consumed at `MARC2VR28P-R1` without freezing a
cohort. The route excludes unknown-participant taxonomy and leaves two exact
public checks inside unchanged VR2 eligibility filtering:

1. the filtered eligible total differs from 195; or
2. the total is 195 but the participant/session count map differs.

The private predicate, count, direction, participant, row, and cohort were not
retained. This lane does not guess or recover them. It proves that generated
witnesses can traverse unchanged VR25A exactly once and preserve only the two
safe R1 subclasses needed for a later, separately authorized private question.

## Frozen Matrix

Eight generated 1,227-row cases are fixed:

| Case | Expected VR25A route | Expected VR29A route |
|---|---|---|
| `exact_public_control` | `MARC2VR25A-G1` | `MARC2VR29A-G1` |
| `single_session_exclusion_removed` | `MARC2VR25A-G2` | `MARC2VR29A-G2` |
| `eligible_bundle_removed` | `MARC2VR25A-R1` | `MARC2VR29A-R1` |
| `eligible_bundle_added` | `MARC2VR25A-R1` | `MARC2VR29A-R1` |
| `eligible_distribution_shift` | `MARC2VR25A-R1` | `MARC2VR29A-R2` |
| `eligible_distribution_shift_second` | `MARC2VR25A-R1` | `MARC2VR29A-R2` |
| `unknown_participant_bundle` | `MARC2VR25A-R2` | `MARC2VR29A-R3` |
| `incomplete_companion_set` | `MARC2VR25A-R3` | `MARC2VR29A-R3` |

Each case runs in canonical and reversed order across two exact replays. The
32 paths must make exactly 32 VR25A calls. The 16 R1 paths must make exactly
16 calls to the unchanged VR2 eligible-filter helper and map only its two
frozen safe reasons. Expected VR29A route counts are G1=4, G2=4, R1=8,
R2=8, and R3=8.

Static AST coverage must bind exactly two refusal sites in
`_filter_and_validate_eligible`: `filtered eligible total differs` and
`eligible participant-session counts differ`. At least 70 direct refusal
checks cover artifact identity, route mapping, source immutability, reason
non-retention, deterministic replay, resource caps, and CLI override refusal.

## Boundaries

Implementation may use only the standard library, the eight committed inputs,
unchanged generated-safe VR25A/VR2 helpers, and invocation-created generated
fixtures. It may expose `plan` and `qualify` commands only. It must have no
private executor and no path, URL, route, reason, count, threshold, retry,
output, or resource override.

It may not touch `.codex_work`, readiness, a consumed marker, VR20P, VR22P,
VR24P, VR26P, or VR28P state, an archive, signal, event, target, label, model,
prediction, score, network, provider, stream, device, hardware, or another
project. It may not expose an upstream reason, observed total, distribution,
participant, or source detail. Generated output retention is zero.

Registration must be committed, pushed, and both CI jobs green before any
implementation begins. A passed generated discriminator would not identify
the consumed private R1 subclass. Another private read would still require a
new all-false Tier C packet, proof barriers, and a fresh packet-bound decision.

## Acceptance Gates

1. All eight fixed inputs match exact byte counts and SHA-256 digests.
2. VR28P result commit `f2b396ed99196d2a5632251390097c6990a7d8d4`
   and both jobs in CI `32618219730` are bound before implementation.
3. Static analysis binds exactly the two frozen VR2 eligible-filter refusal
   sites and no additional site.
4. All 32 paths call unchanged VR25A exactly once.
5. The 16 R1 paths call unchanged VR2 eligible filtering exactly once more for
   aggregate-only discrimination.
6. VR29A route counts are G1=4, G2=4, R1=8, R2=8, and R3=8.
7. Every call leaves its generated source byte-identical.
8. Both replays are exact and order-independent.
9. At least 70 direct refusals pass.
10. No generated source or report is retained.
11. One CPU thread, worker, and numerical job; 30 seconds; less than 256 MiB
    peak RSS; 32 MiB generated input; and 1 MiB aggregate output are respected.
12. Complete dependency-light tests, focused Ruff, registry parsing, CLI help,
    and diff hygiene pass. Repository-wide Ruff remains measured separately
    against its 1,125-finding legacy baseline.
13. Every private, archive, neural, target, model, network, hardware, FW2/CIL1,
    other-project, and claim counter remains zero.

Engineering capability proposed: distinguish eligible-total arithmetic from
participant-session distribution arithmetic through unchanged generated VR25A
and VR2 boundaries.

Scientific claim not established: this registration accesses no neural
payload, target, model, prediction, or score and establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
