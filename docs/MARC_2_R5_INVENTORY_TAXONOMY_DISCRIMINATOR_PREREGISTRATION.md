# MARC2-VR27A R5 Inventory/Taxonomy Discriminator Preregistration

Date: 2026-08-22

Lane: `MARC2-VR27A`

Status: **Frozen artifact-only and generated-only registration**

Machine contract:
`registries/marc2_r5_inventory_taxonomy_discriminator_contract.v0.json`

## Why This Is Next

The sole VR26P invocation consumed at `MARC2VR26P-R5` without freezing a
cohort. Its frozen route table leaves two public possibilities from unchanged
VR25A:

1. `MARC2VR25A-R1`: the exact eligible bundle total or participant/session
   distribution differs.
2. `MARC2VR25A-R2`: a recognized complete bundle belongs to a participant
   outside the frozen taxonomy.

The private predicate, value, count, direction, participant, and row were not
retained. This lane does not guess or recover them. It proves that generated
witnesses can traverse the exact unchanged VR25A adapter and preserve only the
two safe diagnostic classes needed for a later, separately authorized private
question.

## Frozen Matrix

Five generated 1,227-row cases are fixed:

| Case | Expected VR25A route | Expected VR27A route |
|---|---|---|
| `exact_public_control` | `MARC2VR25A-G1` | `MARC2VR27A-G1` |
| `eligible_bundle_removed` | `MARC2VR25A-R1` | `MARC2VR27A-R1` |
| `eligible_bundle_added` | `MARC2VR25A-R1` | `MARC2VR27A-R1` |
| `eligible_distribution_shift` | `MARC2VR25A-R1` | `MARC2VR27A-R1` |
| `unknown_participant_bundle` | `MARC2VR25A-R2` | `MARC2VR27A-R2` |

Each case runs in canonical and reversed order across two exact replays. The
twenty paths must make exactly twenty VR25A calls and return route counts
G1=4, R1=12, and R2=4. Static AST coverage must bind the two independent VR25A
refusal call sites. At least fifty direct refusal checks cover contract and
artifact identity, route mapping, source immutability, privacy, deterministic
replay, resource caps, and CLI override refusal.

## Boundaries

Implementation may use only the standard library, the nine committed inputs,
and invocation-created generated fixtures. It may expose `plan` and `qualify`
commands only. It must have no private executor and no path, URL, route,
reason, count, threshold, retry, output, or resource override.

It may not touch `.codex_work`, readiness, a consumed marker, VR26P output,
an archive, signal, event, target, label, model, prediction, score, network,
provider, stream, device, hardware, or another project. It may not expose an
upstream reason or source detail. Generated output retention is zero.

Registration must be committed, pushed, and both CI jobs green before any
implementation begins. A passed generated discriminator would not identify
the consumed private branch. Another private read would still require a new
all-false Tier C packet, proof barriers, and a fresh packet-bound decision.

## Acceptance Gates

1. All nine fixed inputs match exact byte counts and SHA-256 digests.
2. VR26P result commit `878148a7adaede8d871f181ad535a2c730a86f93`
   and both jobs in CI `32610456792` are bound before implementation.
3. Static analysis binds exactly one independent VR25A R1 site and one R2
   site.
4. All twenty paths call unchanged VR25A exactly once.
5. G1 appears four times, R1 twelve times, and R2 four times.
6. Every call leaves its generated source byte-identical.
7. Both replays are exact and order-independent.
8. At least fifty direct refusals pass.
9. No generated source or report is retained.
10. One CPU thread, worker, and numerical job; 30 seconds; less than 256 MiB
    peak RSS; 32 MiB generated input; and 1 MiB aggregate output are respected.
11. Complete dependency-light tests, Ruff, registry parsing, CLI help, and
    diff hygiene pass.
12. Every private, archive, neural, target, model, network, hardware, FW2/CIL1,
    other-project, and claim counter remains zero.

Engineering capability proposed: distinguish eligible-inventory drift from
unknown-participant taxonomy through the unchanged generated VR25A boundary.

Scientific claim not established: this registration accesses no neural
payload, target, model, prediction, or score and establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
