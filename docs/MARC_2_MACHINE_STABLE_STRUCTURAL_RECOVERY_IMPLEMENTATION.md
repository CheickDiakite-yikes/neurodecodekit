# MARC2-VR4 Machine-Stable Structural Recovery Implementation

Date: 2026-08-16

Lane: `MARC2-VR4`

Status: **Generated and machine-only implementation complete; exact commit and
both CI jobs must be green before one measured machine-readiness closeout; no
private path, structural cohort pass, payload, model, target, or score is
authorized**

Registry:
`registries/marc2_machine_stable_structural_recovery_implementation.v0.json`

## What Was Added

`neurodecodekit.datasets.marc2_machine_readiness` implements the frozen VR4
Stage A surface:

```text
plan
qualify
inspect --certificate <generated-certificate>
readiness
```

The module is standard-library only. It contains no execute command, private
source or output-root constant, network client, archive reader, neural reader,
target interface, derivative builder, trainer, predictor, freezer, or scorer.

The `readiness` command has no path, root, threshold, interval, sample-count,
wait, participant, split, or cap override. It can write only:

```text
.codex_work/marc2_machine_readiness/vr4/readiness.v0.json
```

The writer refuses alternate paths, symlink parents, non-directory parents,
an existing destination, noncanonical JSON, a mode other than `0600`, and a
certificate above 64 KiB.

## Readiness Semantics

Each sample records its exact UTC and monotonic timestamps, logical CPU count,
one-minute load, normalized one-minute load, process peak RSS, free disk,
thresholds, pass/fail checks, and exact safe refusal reasons. Readiness requires:

- all five numerical thread variables equal `1`;
- at least one logical CPU;
- normalized one-minute load at most `1.0`;
- process peak RSS strictly below 256 MiB;
- free disk at least 15 GiB; and
- three consecutive passing samples at least five seconds apart.

The sequence is capped at 121 samples and 600 seconds. A ready certificate
expires 300 seconds after its final sample. A not-ready certificate remains a
machine-state result only and does not consume the later private content open.

## Generated Qualification

One final one-thread generated qualification passed:

| Measure | Result | Cap |
|---|---:|---:|
| success scenarios | 3 / 3 | 3 |
| ordered mutations | 36 / 36 refused | 36 |
| generated machine samples | 13 | bounded fixtures |
| generated certificates | 4 | bounded fixtures |
| generated input | 18,474 bytes | small fixtures |
| retained generated output | 0 bytes | 1 MiB incremental disk |
| report | 5,184 bytes | 64 KiB |
| runtime | 0.007058667 seconds | 30 seconds |
| peak RSS | 19,038,208 bytes | 268,435,456 bytes exclusive |
| network/private/archive bytes | 0 / 0 / 0 | 0 / 0 / 0 |

The qualification covered three immediate passing samples, one failed sample
followed by three passes, exact inclusive/exclusive thresholds, a non-ready
timeout shape, byte-identical replay, strict file inspection, expiry, and all
36 frozen mutations across `MARC2RDY-F00` through `MARC2RDY-F05`.

Focused verification passed 60 tests across implementation, contract, and
research surfaces. Fresh A-M and N-Z complete shards passed 3,273 tests with
28 skips and 513 tests with seven skips, respectively, for 3,786 tests with 35
expected skips. Ruff passed for the implementation and its focused tests.

## Access Ledger

The implementation and generated qualification performed:

```text
private path operations:                              0
private content opens / input bytes:                  0 / 0
private output-root operations:                       0
network requests / bytes:                             0 / 0
archive-member reads:                                 0
signal-sample reads:                                  0
event/target/label/onset/channel/geometry reads:       0
real derivative rows:                                 0
training or parameter-update fits:                    0
model inference or prediction sets:                   0
prediction freezes / target deliveries / scores:      0
provider or language-model calls:                     0
hardware or other-project operations:                 0
scientific claim upgrades:                            0
```

Temporary generated files were removed.

## Next Gate

Commit and push this exact implementation, then require both Base Python and
Optional Neuro Readers CI jobs to pass. Only then may one measured
machine-readiness closeout run. That closeout still cannot inspect a private
path or freeze a real cohort.

After the closeout is committed, pushed, and remotely green, a separate
all-false Tier C packet may bind one new additive structural executor. A fresh
packet-bound maintainer decision is still required before its one marker and
one private content open. The current or any earlier `continue` is not
retroactive authority for that future packet.

FW2 remains ineligible until that later structural pass freezes a real cohort
identity. Neural training, prediction freezing, target delivery, and scoring
remain later gates.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can now generate and strictly
validate a deterministic, expiring machine-readiness certificate without
touching private or neural data.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this implementation establishes no neural effect or
decoding result.
