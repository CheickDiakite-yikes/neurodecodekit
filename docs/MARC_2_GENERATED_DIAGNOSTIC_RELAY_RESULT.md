# MARC2-VR8B Full-Scale Generated Diagnostic Relay Result

Date: 2026-08-16

Lane: `MARC2-VR8B`

Status: **Generated qualification complete at `MARC2VR8B-G1`; exact
implementation remotely green**

## Result

The missing full-scale integration path now exists and passes. All 1,227
generated rows traverse the exact central-directory parser and live manifest
producer before VR2 and VR6. The complete success/F02/F03/F04 matrix passes in
canonical and reversed order and replays exactly.

The safe diagnostic relay is now proven end to end:

```text
forced envelope failure  -> outer MARC2VR6-F02 + nested MARC2VR2-F02
forced path failure      -> outer MARC2VR6-F02 + nested MARC2VR2-F03
forced taxonomy failure  -> outer MARC2VR6-F02 + nested MARC2VR2-F04
```

No reason, path, identity, source row, or value survives the relay. This is the
capability the consumed VR7P wrapper lacked.

## Order Insight

Canonical and reversed paths select the same generated cohort: 16 subjects and
96 run bundles. Their original VR6 provenance hashes differ because those
hashes bind the ordered live source. VR8B leaves those hashes unchanged and
adds a separate order-neutral generated-cohort identity:

```text
812ecbe8f402ae49eab22f166964390b8024639e0afc8b793f9fe89105f20923
```

That distinction is intentional. Transport provenance answers which exact
ordered source was processed; the normalized cohort identity answers whether
the selected structural cohort is the same.

## Measurements

```text
route:                              MARC2VR8B-G1
fixed artifact count / bytes:          20 / 648,432
generated paths:                    8 x 2 replays
exact parser entry visits:                19,632
generated input bytes:                  4,650,480
runtime:                        2.421215000 seconds
peak RSS:                          59,310,080 bytes
aggregate output:                      6,101 bytes
retained output:                           0 bytes
threads / workers / jobs:                1 / 1 / 1
raw reads / real-cache reads:             0 / 0
model runs / training runs:               0 / 0
causal producer:                 not applicable
end-to-end latency measured:                  no
```

The largest materialized path was 291,285 bytes. The two replays materialized
4,650,480 bytes in total, below the 8 MiB cap. Peak RSS remained below 256 MiB,
runtime below 30 seconds, and aggregate output below 1 MiB.

## Acceptance

All 16 frozen gates passed. Twenty-nine direct mutations exercise all six VR8B
refusal routes, including:

- contract and artifact hash drift;
- parser entry/kind drift and unsafe local intervals;
- unexpected synthetic normalization;
- unknown, missing, or wrong nested routes;
- deterministic replay and matrix mismatch;
- reason, path, person, and field leakage;
- thread, runtime, RSS, input, output, and retention caps; and
- nonzero forbidden-operation counters.

The focused contract, behavior, and result suite passes 29 tests. Exact call
spies observe 16 parser calls, 16 generated producer calls, 16 manifest
compositions, and 16 VR6 calls. Fixed-probe qualification output replays
byte-identically.

The dependency-light suite passes 3,948 tests with 204 expected skips. Fresh
optional A-M and N-Z processes pass 3,506 and 513 tests respectively, with 35
expected skips in total, for a complete 4,019-test optional inventory. Both
inventories are exactly 21 tests above the green registration baseline. A
monolithic optional replay reproduced the repository's known sandboxed
forkserver denial and two late process-state/RSS-sensitive gates; those exact
three tests pass under their required fresh or non-sandboxed process
conditions. New failures versus baseline are zero.

Exact implementation `d7ce48baca29547ff2385ffe53d247563139439f` passed Base
Python job `95271230358`, Optional Neuro Readers job `95271230485`, and CI
`31989817593`. This closes the generated implementation gate only; it does not
authorize a private source open.

## What Remains Unknown

This generated result does not reveal whether the consumed private source
would produce F03 or F04. It does not reveal the failed private predicate,
member path, participant, session, run, cohort reservation, or selection hash.
It does not authorize another source read.

The next evidence-bearing action, if pursued, is a separately frozen all-false
Tier C packet for one new structural diagnostic using this exact remotely green
relay behavior. That packet must preserve only the nested code, cannot relax
F03 or F04, and must become a separate green decision before any private open.

FW2 and CIL1 remain closed because no real cohort has been frozen. No archive
member, neural signal, event, target, derivative, model, prediction, or score
was touched.

## Boundary

Engineering capability added: NeuroDecodeKit can now exercise the exact
full-scale parser/producer path and preserve an aggregate F02/F03/F04 nested
diagnostic through VR6 without exposing private context.

Scientific claim not established: this generated structural result used no
neural payload, target, model, prediction, or score and establishes no neural
effect, decoding performance, language decoding, live decoding, or
thought-to-text capability.
