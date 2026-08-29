# DREYER-C5R-1 H-L1R1 Generated Qualification Implementation

Date: 2026-08-29

Status: **coordinator complete; exact commit and both CI jobs must be green
before the sole registered qualification**

Machine record:

- `registries/dreyer_c5r_1_stage_h_live_recovery_qualification_implementation.v0.json`

## What Was Added

This milestone adds a standard-library coordinator around the immutable Stage H
and H-L1R1 generated implementations. It does not change either implementation.
The coordinator freezes and checks one 65-case matrix:

1. two byte-identical valid H1 transaction replays;
2. the inherited two valid Stage H cases;
3. all 18 inherited Stage H refusals; and
4. all 43 ordered H-L1R1 successor refusals.

The H1 checks require marker-before-capability order, exactly one opener and
one request, response closure, no staging debris, and strict aggregate output.
Post-marker failures must become aggregate H0 unless the frozen case is itself
a publication refusal. Premarker objects used by the adversarial matrix are
preserved rather than misclassified as invocation debris.

The sidecar CLI exposes `plan`, `qualify`, and `inspect`. `qualify` accepts no
URL, path, EDF, network, H-L2, model, target, or score argument. Its only output
locations are fixed Git-ignored paths. The official entry point writes a
no-replace consumed marker before the matrix and refuses every later attempt.
The attempt is consumed whether it passes or fails.

## Development Qualification

The full matrix was exercised with fixed case-level clocks, RSS readers, disk
readers, and one-thread environment values so the two H1 public reports are
byte-identical. The outer measurement used the real local process clock and
peak RSS.

```text
matrix cases:                              65
valid H1 / inherited valid / inherited H0: 2 / 2 / 18
ordered successor refusals:                43
focused tests:                             6
measured matrix runtime:                   0.19743325002491474 seconds
peak process RSS:                          38,371,328 bytes
generated fixture input:                   1,452,034 bytes
temporary logical bytes:                   162,373 bytes
temporary allocated bytes:                 368,728 bytes
aggregate matrix JSON:                     6,743 bytes
retained bytes after temporary cleanup:    0
registered qualification attempts:         0
real/private path operations:              0
HTTP requests / network bytes:             0 / 0
real EDF/header/signal/target reads:        0 / 0 / 0 / 0
model/training/inference/prediction/score:  0 / 0 / 0 / 0 / 0
provider/stream/device/hardware/release:     0 / 0 / 0 / 0 / 0
producer causal:                            unavailable
required context:                          unavailable
end-to-end latency measured:                false
```

The generated fixture plus temporary surface is 1,614,407 bytes, well below
the 8 MiB generated I/O cap. Allocated temporary disk is below 16 MiB, peak
RSS is below 256 MiB, and runtime is below 30 seconds. The official result uses
fixed-point accounting that additionally includes its durable consumed marker
and final public result.

## Next Barrier

Commit and push this exact coordinator, then require Base Python and Optional
Neuro Readers to pass on GitHub `main`. Only then may the already authorized
sole `DREYER-C5R-1-HL1R1-Q0` generated qualification run. No retry, rerun,
repair, resume, substitution, or amendment is permitted after that attempt.
H-L2 and the real EDF remain closed.

Engineering capability added: the complete frozen 65-case generated recovery
matrix now has a bounded, one-shot, no-replace qualification coordinator.

Scientific claim not established: this generated-only implementation accesses
no real EEG and establishes no neural, decoding, unseen-person,
peripheral-adjusted, live, hardware, or clinical result.
