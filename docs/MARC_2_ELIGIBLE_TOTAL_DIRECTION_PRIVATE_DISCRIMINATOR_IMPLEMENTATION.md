# MARC2-VR32P eligible-total direction private discriminator implementation

Date: 2026-08-23
Lane: `MARC2-VR32P`
Stage: 1 of 2
Status: generated wrapper qualified; private execution remains proof-gated

## Authority

The implementation is bound to the all-false request at commit
`9dc13cb29804a7adfeaa45aa821e36e160a0f6ee`, its proof-only closeout at
`41d7ef7f5ae7f2288ce3af870ae786652d0aade3`, and the maintainer's packet-bound
decision at `cb80d07b0e83c3d02d0bb3f7afae08b4ee6ba528`. Decision CI
`32630976806` passed Base Python job `97173642868` and Optional Neuro Readers
job `97173642874` before implementation began.

This stage authorizes generated fixtures only. It performs no read, stat,
resolve, hash, parse, list, or write operation on the registered private
source, any `.codex_work` path, or any consumed lane.

## Interface

`neurodecodekit.datasets.marc2_eligible_total_direction_private_discriminator`
provides four fixed commands:

- `plan` reports the frozen generated and proof gates without touching private
  state.
- `qualify` executes the registered generated matrix in temporary directories.
- `inspect` accepts no path and remains blocked before a remotely green Stage 1
  implementation proof.
- `execute` accepts no path or policy override and remains blocked before the
  same proof.

The wrapper calls unchanged VR31A once per generated path. VR31A calls
unchanged VR29A and VR25A once per path and performs the frozen direction
comparison only on its R1 family. The wrapper imports no consumed private
executor. Its fixed state machine writes a mode-0600 consumed marker before
opening a bound source, opens the source once with no-follow semantics, checks
file mode, size, SHA-256, strict JSON, and schema, writes outputs exclusively,
and inspects the canonical aggregate report through a forbidden-field
firewall.

## Generated Qualification

One measured qualification completed all eight cases in canonical and reversed
order across two exact replays:

| Measurement | Result |
| --- | ---: |
| Generated paths | 32 |
| Generated source content opens | 32 |
| VR31A / nested VR29A / nested VR25A calls | 32 / 32 / 32 |
| Nested R1 direction comparisons | 8 |
| VR32P G1 / G2 / R1 / R2 / R3 | 4 / 4 / 4 / 4 / 16 |
| Direct refusals passed | 152 |
| Fixed tracked input bytes | 92,949 |
| Generated input bytes | 14,137,216 |
| Generated output bytes written | 25,644 |
| Peak incremental output bytes | 810 |
| Aggregate report bytes | 3,422 |
| Runtime | 3.007118667010218 seconds |
| Peak RSS | 35,897,344 bytes |
| Retained generated output | 0 bytes |

Every repository-private, consumed-state, archive, signal, target, model,
prediction, score, network, provider, device, FW2/CIL1, other-project, and
scientific-claim counter remained zero.

## Failure And Privacy Behavior

- A missing remote implementation proof refuses before request loading,
  readiness, path construction, or private source access.
- Generic source, output, URL, route, threshold, count, difference, reason,
  retry, and substitution arguments do not exist.
- A future real aggregate result can expose only `MARC2VR32P-R1` below 195 or
  `MARC2VR32P-R2` above 195; an unexpected upstream class fails closed.
- No observed total, difference, distribution, predicate, value, row, path,
  identity, participant, selection, cohort, target, model output, or score is
  allowed in the report.
- An existing readiness parent, output root, marker, or report prevents reuse.

## Next Gate

The exact Stage 1 implementation commit must be pushed and both CI jobs must be
green. A proof-only closeout must then bind those exact bytes and itself become
remotely green without repeating qualification or touching private state.
Only after that barrier may the already authorized one-shot Stage 2 readiness
and target-free structural direction check occur. There is no retry or rerun.

Engineering capability added: a dependency-free, generated-qualified,
proof-gated fixed-path wrapper can distinguish below-expected from above-
expected eligible totals without exposing the count.

Scientific claim not established: no private structural source, archive
payload, neural signal, target, model, prediction, or score was accessed, so no
neural effect or decoding capability was established.
