# MARC2-VR30P inventory/distribution private discriminator implementation

Date: 2026-08-23
Lane: `MARC2-VR30P`
Stage: 1 of 2
Status: generated wrapper qualified; private execution remains proof-gated

## Authority

The implementation is bound to the all-false request at commit
`8e49ac080ca31fe9788ebfdfe9fc355a9a58218c`, its proof-only closeout at
`44dc8ac5d2090c072332fe000e7c506da9b18e28`, and the maintainer's packet-bound
decision at `2bd811e30991997b8b7616e4c9451899f579dc94`. Decision CI
`32623171395` passed Base Python job `97154390311` and Optional Neuro Readers
job `97154390379` before implementation began.

This stage authorizes generated fixtures only. It does not authorize a read,
stat, resolve, hash, parse, list, or write operation on the registered private
source, any `.codex_work` path, or any consumed lane.

## Interface

`neurodecodekit.datasets.marc2_inventory_distribution_private_discriminator`
provides four fixed commands:

- `plan` reports the frozen generated and proof gates without touching private
  state.
- `qualify` executes the registered generated matrix in temporary directories.
- `inspect` accepts no path and remains blocked before a remotely green Stage 1
  implementation proof.
- `execute` accepts no path or policy override and remains blocked before the
  same proof.

The wrapper calls unchanged VR29A once per generated path. VR29A calls
unchanged VR25A once per path and, for its R1 family, the unchanged VR2
eligible filter once. The wrapper imports no consumed private executor. Its
fixed state machine writes a mode-0600 consumed marker before opening a bound
source, opens the source once with no-follow semantics, checks file mode,
size, SHA-256, strict JSON, and schema, writes outputs exclusively, and
inspects the canonical aggregate report through a forbidden-field firewall.

## Generated qualification

One measured qualification completed all eight cases in canonical and reversed
order across two exact replays:

| Measurement | Result |
| --- | ---: |
| Generated paths | 32 |
| Generated source content opens | 32 |
| VR29A calls | 32 |
| Nested VR25A calls | 32 |
| Nested VR2 eligible-filter calls | 16 |
| VR30P G1 / G2 / R1 / R2 / R3 | 4 / 4 / 8 / 8 / 8 |
| Direct refusals passed | 151 |
| Fixed tracked input bytes | 161,574 |
| Generated input bytes | 14,137,216 |
| Generated output bytes written | 25,452 |
| Peak incremental output bytes | 804 |
| Aggregate report bytes | 3,395 |
| Runtime | 2.467852458008565 seconds |
| Peak RSS | 34,127,872 bytes |
| Retained generated output | 0 bytes |

Every repository-private, consumed-state, archive, signal, target, model,
prediction, score, network, provider, device, FW2/CIL1, other-project, and
scientific-claim counter remained zero.

## Failure and privacy behavior

- A missing remote implementation proof refuses before request loading,
  readiness, path construction, or private source access.
- Generic source, output, URL, route, threshold, reason, retry, and substitution
  arguments do not exist.
- A future real aggregate result can expose only `MARC2VR30P-R1` or
  `MARC2VR30P-R2`; an unexpected upstream class fails closed.
- No predicate, value, count, direction, distribution, row, path, identity,
  participant, selection, cohort, target, model output, or score is allowed in
  the report.
- An existing readiness parent, output root, marker, or report prevents reuse.

## Next gate

The exact Stage 1 implementation commit must be pushed and both CI jobs must be
green. A proof-only closeout must then bind those exact bytes and itself become
remotely green without repeating qualification or touching private state.
Only after that barrier may the already authorized one-shot Stage 2 readiness
and target-free structural read occur. There is no retry or rerun.

Engineering capability added: a dependency-free, generated-qualified,
proof-gated fixed-path wrapper can distinguish the final eligible-total versus
participant-session distribution classes without retaining private detail.

Scientific claim not established: no private structural source, archive
payload, neural signal, target, model, prediction, or score was accessed, so no
neural effect or decoding capability was established.
