# MARC2-VR21A R5 Two-Route Discriminator Preregistration

Date: 2026-08-22

Lane: `MARC2-VR21A`

Status: **Frozen artifact-only and generated-only registration**

Machine contract:
`registries/marc2_r5_two_route_discriminator_contract.v0.json`

## Why This Is Next

The sole VR20P execution consumed at `MARC2VR20P-R5`. The frozen ordered route
table excludes proof/precondition, source-envelope, and
published-task/identity/path/companion classes for that invocation. R5 still
combines two materially different mechanisms:

1. VR20A F06: source-kind, bundle-total, participant-taxonomy, or eligibility
   arithmetic.
2. VR20A F07: downstream selection, rank, split, identity, or reservation
   arithmetic.

The private predicate and value were not retained. This lane does not guess
them. It proves that generated examples can traverse the exact unchanged
VR20A adapter and preserve only the two safe route classes needed for a later,
separately authorized question.

## Frozen Matrix

Three generated cases are fixed: one success control, one unknown-participant
taxonomy witness for F06/R1, and one semantic-run-zero witness for F07/R2.
Each runs in canonical and reversed order across two exact replays, producing
12 VR20A calls. G1, R1, and R2 must each appear exactly four times.

Static AST coverage must bind all 11 relevant VR20A call sites: two F06 sites
and nine F07 sites. At least 40 direct refusal checks cover input hashes,
route mapping, source immutability, output privacy, resource caps, and CLI
override refusal.

## Boundaries

Implementation may use the standard library, committed artifacts, and
invocation-created generated fixtures only. It has no private executor and no
path, URL, route, reason, threshold, retry, or resource override. It may not
touch `.codex_work`, readiness, consumed markers, VR20P output, an archive,
signal, event, target, label, model, prediction, score, network, provider,
stream, device, hardware, or another project.

Registration must be committed, pushed, and both CI jobs green before any
implementation begins. A passed generated discriminator would still require a
new all-false Tier C packet and fresh decision before another private read.

Engineering capability proposed: distinguish the two remaining structural
arithmetic classes through unchanged VR20A using deterministic generated
witnesses.

Scientific claim not established: this registration accesses no neural
payload, target, model, prediction, or score and establishes no neural effect,
decoding accuracy, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
