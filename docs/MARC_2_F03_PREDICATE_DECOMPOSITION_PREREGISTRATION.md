# MARC2-VR10A F03 Predicate Decomposition Preregistration

Date: 2026-08-17

Lane: `MARC2-VR10A`

Status: **Frozen artifact-only and generated-only contract; no private access
or scientific claim**

Machine contract:
`registries/marc2_f03_predicate_decomposition_contract.v0.json`

## Why This Lane Exists

The consumed VR9P execution retained outer `MARC2VR6-F02` and nested
`MARC2VR2-F03`. F03 is useful but still broad: the current VR2 adapter maps all
row/path and companion failures, plus entry-kind drift, to one aggregate code.
A repair chosen before decomposing that class would be guesswork.

VR10A reads only exact committed source, contracts, and aggregate result
records. It must not open a private manifest, consumed root, archive, member,
signal, event, target, model, prediction, or score.

## Frozen Static Decomposition

The exact validator contains 20 leaf predicate classes before F04. Committed
producer code and the green central-directory aggregate already exclude 15:

1. row object and exact field set;
2. member path string and nonempty value;
3. NFC normalization;
4. safe relative prefix and separators;
5. absence of control characters;
6. absence of empty, dot, or parent components;
7. lowercase eight-hex CRC declaration;
8. nonboolean integer fields;
9. nonnegative size fields;
10. Boolean ZIP64 declaration;
11. unencrypted method 0 or 8;
12. exact directory shape;
13. exact regular-file shape;
14. unique full member names; and
15. exact 1,025 regular-file plus 202-directory counts.

Five classes remain unresolved because the aggregate evidence does not expose
member paths or logical grouping:

1. UTF-8 member-name length at or below 1,024 bytes;
2. suffix-bearing Freewill BIDS identity and filename/path agreement;
3. exact lowercase `task-freewill` token;
4. unique logical run companion after different parent prefixes collapse to
   the same subject/session/run/suffix key; and
5. completeness of the four required companions.

This is logical implication from committed code and aggregate counts.
It does not assert that any one of the five caused the private F03 result.

## Frozen Generated Witness Matrix

After this registration is committed, pushed, and remotely green, one
dependency-free implementation may build six full-scale generated cases:

| Case | Mutation before exact parser | Expected relay |
|---|---|---|
| `control_success` | none | VR6 success |
| `overlong_member_name` | preserve a valid core suffix under a path longer than 1,024 UTF-8 bytes | outer F02, nested F03 |
| `suffix_bearing_BIDS_identity` | mismatch path and filename identity while preserving a required suffix | outer F02, nested F03 |
| `task_token_case` | change one exact task token without changing the suffix | outer F02, nested F03 |
| `logical_companion_alias` | rename one auxiliary member to a distinct full path that maps to an existing logical companion | outer F02, nested F03 |
| `incomplete_companion_set` | move one core companion to a safe noncore auxiliary name | outer F02, nested F03 |

Every case must traverse the exact central-directory fixture builder, parser,
live producer, VR2 validator, and VR6 relay. Run canonical and reversed order,
replay the complete matrix twice, and require exactly 24 paths and 24 VR6
calls. Only case names, aggregate route codes, deterministic digests, counts,
resources, warnings, and zero counters may leave the process.

## Acceptance Gates

1. All 14 committed inputs match exact size and SHA-256.
2. The AST inventory finds exactly 20 F03 leaf classes.
3. Exactly 15 classes are supported as excluded by committed producer or
   aggregate evidence.
4. Exactly the five frozen source-dependent classes remain unresolved.
5. All 24 exact parser/producer paths replay identically.
6. Every control path succeeds and every witness path returns outer F02 plus
   nested F03.
7. No generated mutation is applied after the exact parser or producer.
8. Source objects are unchanged by refused VR6 calls.
9. At least 40 direct contract, matrix, privacy, determinism, resource, and
   output mutations refuse on the expected route.
10. No generated output is retained.
11. One thread, one worker, one numerical job, 30 seconds, less than 256 MiB
    peak RSS, 16 MiB generated input, and 1 MiB aggregate output are respected.
12. Every private, archive, signal, target, model, network, provider, hardware,
    FW2/CIL1, other-project, retry, release, and claim counter remains zero.

## Stop Rules

- If the static inventory does not produce exactly 20 leaves and the frozen
  15/5 partition, park the lane without broadening the taxonomy.
- If any witness fails before the exact parser, does not reach nested F03, or
  changes route with row order or replay, park the lane.
- Do not relax an F03 predicate, inspect the private source, or infer a failed
  value from generated behavior.
- Do not prepare a new Tier C packet until the exact implementation and result
  are committed, pushed, and remotely green.

## Claim Boundary

Engineering capability sought: distinguish all still-plausible F03 structural
mechanisms with full-scale exact-parser generated witnesses before choosing a
prospective repair or aggregate discriminator.

Scientific claim not established: artifact-only code analysis and generated
ZIP metadata establish no neural effect, decoding accuracy, language decoding,
live decoding, or thought-to-text capability.
