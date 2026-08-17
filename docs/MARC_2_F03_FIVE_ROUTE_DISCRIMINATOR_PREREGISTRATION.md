# MARC2-VR10B F03 Five-Route Discriminator Preregistration

Date: 2026-08-17

Lane: `MARC2-VR10B`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_f03_five_route_discriminator_contract.v0.json`

## Why This Lane Exists

VR10A proved that the broad nested `MARC2VR2-F03` class has five remaining
source-dependent structural mechanisms. It also produced one exact-parser
generated witness for each mechanism. That is enough to design and qualify a
coarse discriminator, but it does not identify the cause of the consumed
private F03 outcome.

VR10B freezes a deterministic first-match decision tree that can return one
of five aggregate-safe route codes. This milestone reads only committed code,
contracts, results, and generated fixtures. It has no private executor, path
reader, network client, or `--execute` mode.

## Green Prior Proof

The exact VR10A implementation commit
`84103a5fab86b7c7c8d3cf3af00c9efe3457470c` passed Base Python job
`95295212461`, Optional Neuro Readers job `95295212440`, and CI
`31998811585`. Its proof closeout commit
`92d028139573309e5636b2f520c915e66113f7aa` passed Base Python job
`95302164129`, Optional Neuro Readers job `95302164150`, and CI
`32001355120`.

Those proofs authorize generated-only discriminator development after this
registration is itself committed, pushed, and remotely green. They authorize
no private read or scientific operation.

## Frozen Ordered Routes

The discriminator evaluates the exact five unresolved classes in source-code
order and stops at the first match:

| Priority | Predicate class | Aggregate route |
|---:|---|---|
| 1 | UTF-8 member-name length above 1,024 bytes (`P03`) | `MARC2VR10B-R1` |
| 2 | suffix-bearing BIDS path or filename identity mismatch (`P15`) | `MARC2VR10B-R2` |
| 3 | non-lowercase or otherwise nonexact `task-freewill` token (`P16`) | `MARC2VR10B-R3` |
| 4 | duplicate logical run companion after path-prefix collapse (`P18`) | `MARC2VR10B-R4` |
| 5 | incomplete four-companion logical run set (`P19`) | `MARC2VR10B-R5` |

`MARC2VR10B-G1` is reserved for the generated clean control after all five
checks pass. It is not evidence that a consumed private source is valid and is
not an admissible future private-result route under this contract.

The decision tree must bind the exact committed normalization, BIDS regex,
required suffixes, grouping key, and companion set. Any unsupported row shape,
non-F03 drift, ambiguous classifier state, multiple emitted routes, or source
mutation fails closed on an implementation refusal route.

## Frozen Generated Qualification

After this registration is remotely green, one dependency-free implementation
may reuse the six exact VR10A generated cases:

1. `control_success` -> `MARC2VR10B-G1`;
2. `overlong_member_name` -> `MARC2VR10B-R1`;
3. `suffix_bearing_BIDS_identity` -> `MARC2VR10B-R2`;
4. `task_token_case` -> `MARC2VR10B-R3`;
5. `logical_companion_alias` -> `MARC2VR10B-R4`; and
6. `incomplete_companion_set` -> `MARC2VR10B-R5`.

Each case must be built before the exact central-directory parser, traverse
the exact parser and producer, and retain the existing VR6 comparison. The
matrix runs canonical and reversed source order across two complete replays:
24 exact parser/producer paths, 24 VR6 calls, and 24 discriminator calls.

All 20 witness paths must still relay outer `MARC2VR6-F02` plus nested
`MARC2VR2-F03`, while the new discriminator returns the exact corresponding
R1 through R5 route. All four clean-control paths must pass VR6 and return G1.

## Output Firewall

A discriminator decision contains one coarse class code and no failed value. Public
or retained output may contain only schema and lane identity, exact tracked
artifact hashes, aggregate route counts for generated qualification,
deterministic aggregate digests, resource measurements, warnings, acceptance
gates, and zero operation counters.

The output must never contain a member name, path, row, row index, subject,
session, run, suffix, participant or cohort identity, failed value, exception
text, source hash, private manifest, selection, signal, event, target, label,
prediction, or per-item outcome.

## Acceptance Gates

1. All ten fixed inputs match exact size and SHA-256.
2. The exact green VR10A implementation and closeout proofs match.
3. The ordered P03/P15/P16/P18/P19 route map is byte-stable.
4. All 24 exact parser and producer paths complete.
5. The 20 witness paths retain outer F02 and nested F03 at VR6.
6. The discriminator maps the 20 witness paths exactly to four copies of each
   R1 through R5 route.
7. The four control paths pass VR6 and return G1.
8. Canonical and reversed order produce the same decision for each case.
9. Both complete replays are byte-identical.
10. No classifier call mutates its source object.
11. The aggregate output firewall rejects every forbidden field recursively.
12. At least 45 direct contract, route, privacy, determinism, resource, and
    output mutations refuse on their expected route.
13. One thread, one worker, one numerical job, 45 seconds, less than 256 MiB
    peak RSS, 16 MiB generated input, 1 MiB aggregate output, and zero retained
    generated output are respected.
14. Every private, archive, neural, target, model, network, provider, hardware,
    FW2/CIL1, other-project, retry, release, and claim counter remains zero.

## Stop Rules

- If a generated witness does not retain its broad F03 relay and its exact new
  route, park the lane without changing predicate order.
- If row order or replay changes a route, park the lane.
- If a decision requires retaining a failed value, identity, row position, or
  per-item count, park the lane.
- Do not relax any F03 predicate or inspect any private source.
- Do not prepare a private Tier C packet until the exact VR10B implementation
  and generated result are committed, pushed, and remotely green.

## Claim Boundary

Engineering capability sought: add a deterministic, aggregate-safe route for
each of the five still-plausible F03 structural mechanisms and prove the route
matrix on exact-parser generated witnesses.

Scientific claim not established: this artifact-only and generated-only work
uses no private or neural data, target, model, prediction, or score and
establishes no neural effect, decoding accuracy, live decoding, language
decoding, or thought-to-text capability.
