# MARC2-VR28P inventory/taxonomy private discriminator implementation

Date: 2026-08-22  
Lane: `MARC2-VR28P`  
Stage: 1 of 2  
Status: generated wrapper qualified; private execution remains proof-gated

## Authority

The implementation is bound to the all-false request at commit
`4e5895fc0fc8bc3cf2c91f5211406115a8e2e6d5`, its proof-only closeout at
`87d4b30ca846d7481c45631ec7625d500e0f9595`, and the maintainer's packet-bound
decision at `718c3de6ddb0030b1ba39fa0e42250e97db01072`. Decision CI
`32614796767` passed Base Python job `97133595196` and Optional Neuro Readers
job `97133595235` before implementation began.

This stage authorizes generated fixtures only. It does not authorize a read,
stat, resolve, hash, parse, or listing operation on the registered private
source or any consumed lane.

## Interface

`neurodecodekit.datasets.marc2_inventory_taxonomy_private_discriminator`
provides four fixed commands:

- `plan` reports the frozen generated and proof gates without touching private
  state.
- `qualify` executes the registered generated matrix in temporary directories.
- `inspect` accepts no path and remains blocked before a remotely green Stage 1
  implementation proof.
- `execute` accepts no path or policy override and remains blocked before the
  same proof.

The wrapper uses the unchanged VR25A firewall once and the unchanged VR27A
route map once per generated path. It imports no consumed private executor.
The shared state machine creates a mode-0600 consumed marker before opening a
bound source, opens the source once with no-follow semantics, checks file mode,
size, SHA-256, strict JSON, and schema, writes output exclusively, and inspects
the canonical aggregate report through a forbidden-field firewall.

## Generated qualification

One measured qualification completed all five cases in canonical and reversed
order across two exact replays:

| Measurement | Result |
| --- | ---: |
| Generated paths | 20 |
| Generated source content opens | 20 |
| VR25A calls | 20 |
| VR27A map calls | 20 |
| VR27A G1 / R1 / R2 | 4 / 12 / 4 |
| Direct refusals passed | 110 |
| Generated input bytes | 8,836,136 |
| Generated output bytes written | 15,618 |
| Peak incremental output bytes | 785 |
| Aggregate report bytes | 3,047 |
| Runtime | 1.097564124967903 seconds |
| Peak RSS | 34,177,024 bytes |
| Retained generated output | 0 bytes |

Every repository-private, consumed-state, archive, signal, target, model,
prediction, score, network, provider, device, FW2/CIL1, other-project, and
scientific-claim counter remained zero.

## Failure and privacy behavior

- A missing remote implementation proof refuses before readiness or private
  path construction.
- Generic source, output, URL, route, threshold, reason, retry, and substitution
  arguments do not exist.
- The real aggregate result can expose only `MARC2VR28P-R1` or
  `MARC2VR28P-R2`; an unexpected upstream class fails closed.
- No predicate, value, count, direction, row, path, identity, participant,
  selection, cohort, target, model output, or score is allowed in the report.
- An existing readiness parent, output root, marker, or report prevents reuse.

## Next gate

The exact Stage 1 implementation commit must be pushed and both CI jobs must be
green. A proof-only closeout must then bind those exact bytes and itself become
remotely green without repeating qualification or touching private state.
Only after that barrier may the already authorized one-shot Stage 2 readiness
and target-free structural read occur. There is no retry or rerun.

Engineering capability added: a dependency-free, generated-qualified,
proof-gated fixed-path wrapper now isolates the frozen inventory-versus-taxonomy
route classes without retaining private detail.

Scientific claim not established: no private structural source, archive
payload, neural signal, target, model, prediction, or score was accessed, so no
neural effect or decoding capability was established.
