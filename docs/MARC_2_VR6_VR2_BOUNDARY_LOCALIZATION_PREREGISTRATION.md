# MARC2-VR8A VR6-to-VR2 Boundary Localization Preregistration

Date: 2026-08-16

Lane: `MARC2-VR8A`

Status: **Frozen artifact-only contract; implementation pending**

Contract:
`registries/marc2_vr6_vr2_boundary_localization_contract.v0.json`

## Why This Lane Exists

The sole `MARC2-VR7P` structural pass reached VR6 and stopped at wrapper route
`MARC2VR7P-F07` with upstream route `MARC2VR6-F02`. That is useful: it proves
the failure occurred inside VR6's call to VR2 validation, before dynamic
selection returned. It is still one level too coarse because VR6 had already
stored the exact allowlisted VR2 route in `exc.upstream_route`, while VR7P
retained only `exc.route`.

The consumed source cannot be reopened. The next safe step is a fixed audit of
committed code, contracts, public aggregate results, and earlier artifact-only
diagnoses. The audit must determine how far those artifacts can narrow the
remaining failure class and whether the generated success path ever exercised
the exact producer's row morphology.

## Frozen Questions

1. Does VR6 preserve the nested VR2 route while VR7P discards it?
2. Which VR2 routes are reachable after the exact contract has already loaded
   and before selection or resource reporting begins?
3. Do the producer module and its public aggregate result satisfy VR2's full
   envelope predicate without reading the retained source?
4. Which row predicates are guaranteed by the ZIP central-directory parser,
   and which BIDS path, companion, bundle, or taxonomy predicates remain
   source-dependent?
5. Does the VR2 generated success fixture traverse the exact producer/parser,
   or does it begin from a selector-authored synthetic manifest?
6. What is the smallest new diagnostic relay that preserves two route codes
   without publishing reasons or weakening source validation?

## Candidate Boundary

VR2 defines eight refusal classes. The audit must classify every one as
reachable, excluded, or ambiguous on the exact call path.

The preregistered hypothesis is that contract-only, selection-only, aggregate-
output, and resource-only routes are incompatible with the observed stage.
The exact producer appears to match VR2's schema, source identity, transport
digests, top-level fields, and 1,227-row envelope. If the audit proves that
lineage completely, route `MARC2VR8A-R1` leaves only:

- `MARC2VR2-F03`: BIDS path, run-companion, or structural row grouping; and
- `MARC2VR2-F04`: 238/195/43 bundle, participant, session, or taxonomy
  arithmetic.

If the producer envelope cannot be proven from committed evidence alone,
`MARC2VR8A-R2` must retain `F02` alongside `F03` and `F04`. The audit must not
claim the consumed nested route, private predicate, member path, participant,
session, run, or value.

## Producer And Fixture Check

The exact producer's private manifest is formed from the central-directory
parser output and then receives its live schema, proof posture, source identity,
and transport digest map. The public result binds only aggregate values.

VR2's current generated source begins from the selector's generated 1,227-row
manifest and then fabricates all 238 run bundles. The audit must explicitly
check whether that path ever calls the exact central-directory parser or the
producer's `_private_manifest` function. Internal agreement among generated
builders and validators is not producer-integration coverage.

## Required Routes

- `MARC2VR8A-R1`: route relay loss is proven; producer evidence excludes F02;
  only F03 and F04 remain compatible.
- `MARC2VR8A-R2`: route relay loss is proven; F02, F03, and F04 remain
  compatible.
- `MARC2VR8A-R3`: relay loss is proven, but committed artifacts are
  inconsistent or insufficient for sound narrowing.
- `MARC2VR8A-F01` through `F04`: fixed-artifact, AST, aggregate-boundary, or
  resource refusal.

## Prospective Repair Boundary

If the audit reaches R1 or R2, a later generated-only lane may qualify a new
diagnostic relay. It must preserve only:

```text
outer route:  MARC2VR6-F02
nested route: one allowlisted MARC2VR2-F01 through F08 code
```

It must discard exception text, private values, member paths, participant and
run identities, and traceback context. It must exercise generated `F02`, `F03`,
and `F04` failures through the complete relay. It may not relax F03 or F04
before an observed route supports a separately frozen repair.

No consumed executor may be patched, reused, retried, resumed, or inspected.
Any future 418,755-byte private read remains a new Tier C action requiring its
own all-false packet, fresh packet-bound maintainer decision, exact remotely
green implementation, and one no-retry execution.

## Resource Limits

```text
CPU threads / workers / jobs:  1 / 1 / 1
runtime:                           30 sec
peak RSS:                         128 MiB
fixed committed inputs:          <= 1 MiB
aggregate output:                <= 1 MiB
retained generated output:            0 B
private or Git-ignored bytes:          0 B
network bytes:                         0 B
incremental disk:                  <= 1 MiB
```

## Claim Boundary

Engineering capability specified: a deterministic artifact audit can identify
where a safe nested refusal code was lost, classify route reachability, and
measure missing producer-to-validator fixture coverage.

Scientific claim not established: this contract accesses no neural payload,
target, prediction, or score and establishes no neural effect, decoding
accuracy, language decoding, live decoding, or thought-to-text capability.
