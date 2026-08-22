# MARC2-VR23A F06 Five-Route Decomposition Implementation

Date: 2026-08-22

Lane: `MARC2-VR23A`

Status: **Generated qualification passed; remote implementation proof pending**

Machine records:

- `registries/marc2_f06_five_route_decomposition_implementation.v0.json`
- `registries/marc2_f06_five_route_decomposition_result.v0.json`

## Exact Registration Proof

Registration `cee91b0473cd97a91feab22d7fd420e0b550b99f` passed Base
Python job `97087038676`, Optional Neuro Readers job `97087038522`, and CI
`32596045581` before implementation. The module verifies the exact
10,459-byte contract and all 14 bound inputs before qualification.

## Implementation

The additive standard-library module exposes only `plan` and `qualify`. It
does not edit VR20A or VR2 and has no private executor. For each generated
path it:

1. validates the exact registration, fixed inputs, thread environment, source
   AST inventory, and proof anchor;
2. proves that the unclassified-taxonomy and filtered-total guards are not
   independent hypotheses under the frozen contract;
3. runs an aggregate-only diagnostic through the exact VR20A grouping and VR2
   taxonomy helpers;
4. calls unchanged VR20A exactly once and requires aggregate-route agreement;
   and
5. compares canonical source bytes before and after the call.

The five reachable classes are entry-kind counts, complete-bundle count,
participant taxonomy membership, 238/195/43 class arithmetic, and eligible
participant-session distribution. The report contains only case names,
routes, hashes, resources, warnings, unavailable fields, and zero counters.

## Measured Qualification

`MARC2VR23A-G1` passed all 24 generated paths. G1 and R1-R5 each appeared four
times across six cases, two orders, and two exact replays. VR20A was called 24
times: four accepted controls and 20 F06 refusals. Diagnostic and VR20A routes
agreed on every path, source mutations were zero, and 62 direct refusals
passed.

The static proof bound exactly two VR20A F06 wrapper sites and seven VR2 helper
reasons. It exhaustively classified 69 known subject/session combinations and
confirmed the 195-item eligible-filter implication.

The fresh process handled 10,603,766 generated input bytes in
2.4120343329850584 seconds at 39,944,192-byte peak RSS. Aggregate output was
6,458 bytes; temporary and retained output were zero. One CPU thread, one
worker, and one numerical job were used. Network, new payload, private,
archive, neural, target, model, prediction, score, FW2/CIL1, other-project,
and claim operations were zero.

## Boundary And Next Gate

This proves the five public F06 classes are independently diagnosable on
generated full-scale manifests and that two apparent extra branches are
defensive redundancy, not separate hypotheses. It does not determine which
class caused the consumed private R4 result.

Commit, push, and green the exact implementation and result, then add a
proof-only closeout without repeating qualification. Only after that may Tier
A prepare an all-false Tier C packet for one future aggregate private
discriminator. That packet would still require a fresh maintainer decision.

Engineering capability added: deterministic generated discrimination of all
five independently reachable VR20A F06 structural classes with exact upstream
agreement and source immutability.

Scientific claim not established: no real cohort, neural payload, target,
model, prediction, or score was accessed, so this establishes no neural
effect, decoding accuracy, language decoding, unseen-person generalization,
live decoding, or thought-to-text capability.
