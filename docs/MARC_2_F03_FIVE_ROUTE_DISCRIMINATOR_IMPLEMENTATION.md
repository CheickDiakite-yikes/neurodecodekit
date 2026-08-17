# MARC2-VR10B F03 Five-Route Discriminator Implementation

Date: 2026-08-17

Lane: `MARC2-VR10B`

Status: **Exact generated-only implementation qualified locally; remote proof
pending**

Machine implementation record:
`registries/marc2_f03_five_route_discriminator_implementation.v0.json`

## Green Implementation Gate

Registration commit `d642eae988bdf5200429fb992e7ff25d778ce949`
passed Base Python job `95308775711`, Optional Neuro Readers job
`95308775577`, and CI `32003674374` before implementation began. The module
binds contract SHA-256
`465032260d1e07c7302645e4106ddceb6e755b68b7061b71e9b9d13c7ac0bfc7`.

## Added Surface

`src/neurodecodekit/datasets/marc2_f03_five_route_discriminator.py` adds:

- exact no-follow verification of ten fixed inputs plus the registration
  document and contract test;
- verification of the green VR10A implementation and result records;
- an in-memory `DiscriminatorDecision` that contains only one route field;
- ordered first-match classification for P03, P15, P16, P18, and P19;
- exact reuse of the VR10A pre-parser fixture, parser, producer, VR2, and VR6
  path for generated qualification;
- deterministic canonical/reversed and two-replay comparison;
- a recursive aggregate-output firewall and 60 direct refusal probes;
- resource measurement and zero-operation counters; and
- `plan` and `qualify` module commands with no path, output, or execute option.

There is no private executor, local-source reader, network client, archive
payload reader, model, scorer, provider call, or hardware interface.

## Decision Order

The implementation validates exact envelope and nonclassifier invariants, then
stops on the first unresolved class:

1. `MARC2VR10B-R1`: member-name UTF-8 length class;
2. `MARC2VR10B-R2`: suffix-bearing BIDS identity class;
3. `MARC2VR10B-R3`: exact task-token class;
4. `MARC2VR10B-R4`: logical-companion uniqueness class; and
5. `MARC2VR10B-R5`: four-companion completeness class.

`MARC2VR10B-G1` is generated-control success only. Unsupported non-F03 drift
returns a generic refusal rather than a class route. No failed value, identity,
row position, or per-item outcome is attached to a decision.

## Generated Qualification

The exact six-case matrix ran in canonical and reversed order across two
complete replays. It completed 24 parser/producer paths, 24 VR6 calls, 24
discriminator calls, and 29,448 parser-entry visits.

All four clean-control paths passed VR6 and returned G1. All 20 witness paths
retained outer `MARC2VR6-F02` plus nested `MARC2VR2-F03`; the new classifier
returned four copies each of R1, R2, R3, R4, and R5. The two complete internal
matrices were byte-identical with digest
`e2c184bbe53c6a1d298cfcd4fef86f0910450b2557e906404816c1175b5a21df`.

## Measurements

| Measure | Observed | Cap |
|---|---:|---:|
| Fixed tracked artifacts | 13 / 417,533 bytes | exact hashes required |
| Generated cases | 6 | 6 |
| Exact paths | 24 | 24 |
| VR6 calls | 24 | 24 |
| Discriminator calls | 24 | 24 |
| Parser-entry visits | 29,448 | 29,448 |
| Direct refusals | 60 | at least 45 |
| Generated input | 6,979,708 bytes | 16,777,216 bytes |
| Aggregate output | 7,515 bytes | 1,048,576 bytes |
| Retained output | 0 bytes | 0 bytes |
| Runtime | 2.725759166991338 seconds | 45 seconds |
| Peak RSS | 44,564,480 bytes | 268,435,456 bytes |

The pass used one CPU thread, one worker, and one numerical job. Raw-data
reads, real-cache reads, model runs, training runs, private operations, archive
payload operations, network operations, and operations on other projects were
all zero. End-to-end latency was not measured because this is structural
metadata classification, not a decoder.

## Verification

- 32 focused registration, behavior, and result tests pass in 5.831 seconds.
- The complete base suite passes 4,074 tests with 204 expected skips and zero
  failures in 64.504 seconds.
- Pinned Ruff 0.15.20 passes the full repository.
- Python compilation, every registry JSON file, diff hygiene, and CLI help/plan
  pass.
- Remote CI remains required before closeout.

## Boundary

No private path, consumed VR9P state, archive payload, signal, event, target,
label, derivative, model, prediction, or score was accessed. A generated route
cannot identify which class occurred in the consumed private source.

Engineering capability added: an exact-parser generated source can now be
classified into one of five deterministic F03 structural routes without
retaining a failed value or source identity.

Scientific claim not established: no private or neural data, target, model,
prediction, or score was used, so this establishes no neural effect or decoding
performance.
