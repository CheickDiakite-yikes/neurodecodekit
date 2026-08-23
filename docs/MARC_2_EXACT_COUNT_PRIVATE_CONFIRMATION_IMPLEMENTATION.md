# MARC2-VR34P exact-count private confirmation implementation

Date: 2026-08-23
Lane: `MARC2-VR34P`
Stage: 1 of 2
Status: generated wrapper qualified; private execution remains proof-gated

## Authority

The implementation is bound to request commit
`d4215c5aa5b8e43d91ff7ff26b8ea035648f3706`, proof-only request closeout
`45cc8f18fe8fc7f5c8b9675648a4cd358617808d`, and the maintainer's packet-bound
decision at `5d6a56ecfad01f49d9e7987cc1072c4aab15bd11`. Decision CI
`32639054941` passed Base Python job `97193199080` and Optional Neuro Readers
job `97193198951` before implementation began.

This stage authorizes generated fixtures only. It performed no read, stat,
resolve, hash, parse, list, or write operation on the registered private
source, a `.codex_work` path, or a consumed lane.

## Interface

`neurodecodekit.datasets.marc2_exact_count_private_confirmation` provides four
fixed commands:

- `plan` reports the frozen generated matrix and proof barriers.
- `qualify` runs the one registered generated matrix in temporary directories.
- `inspect` accepts no path and refuses before a remotely green Stage 1 proof.
- `execute` accepts no path or policy override and refuses before that proof.

The wrapper composes only unchanged VR33A exact readiness and unchanged VR31A
eligible-total direction discrimination. It does not import or call the
consumed VR32P executor. Every generated path collects exactly three readiness
samples and performs exactly two fixed sleeper calls. A non-`PPP` pattern
writes its generated consumed state and aggregate `R3` report without creating
or opening a source and without calling VR31A. A `PPP` path writes its consumed
marker before source construction, opens one bound generated source with
no-follow semantics, and calls VR31A once.

The future private executor remains unavailable. Once its proof barrier is
green, it will use the same finite readiness primitive, consume a non-ready
invocation at `R3` without a source open, or open the one registered target-free
structural source once and retain only aggregate `R1` below 195, `R2` above
195, or a safe failure route. No total, difference, predicate, value, row,
path, identity, participant, selection, or cohort may be retained.

## Generated Qualification

The one registered qualification completed 15 conditions in each of two
orders across two exact replays:

| Measurement | Result |
| --- | ---: |
| Generated paths | 60 |
| VR33A calls / provider calls / sleeper calls | 60 / 180 / 120 |
| Source constructions / content opens | 32 / 32 |
| VR31A / nested VR29A / nested VR25A calls | 32 / 32 / 32 |
| Nested R1 direction comparisons | 8 |
| Nonpassing source constructions / VR31A calls | 0 / 0 |
| VR34P G1 / G2 / R1 / R2 / R3 | 4 / 4 / 4 / 4 / 44 |
| Direct refusals passed | 223 |
| Fixed tracked input bytes | 137,581 |
| Generated input bytes | 14,152,684 |
| Generated output bytes written | 46,332 |
| Peak incremental output bytes | 791 |
| Aggregate report bytes | 3,709 |
| Runtime | 3.024067790945992 seconds |
| Peak RSS | 37,257,216 bytes |
| Retained generated output | 0 bytes |

Every repository-private, consumed-state, archive, signal, target, model,
prediction, score, network, provider, device, FW2/CIL1, other-project, and
scientific-claim counter remained zero.

## Verification Boundary

- The qualification was executed exactly once and must not be repeated.
- Tests validate each readiness branch and source route independently without
  calling the aggregate qualification again.
- A missing implementation proof refuses before request loading, readiness,
  path construction, or private source access.
- The wrapper has no generic source, URL, output, count, threshold, difference,
  readiness, retry, route, or substitution arguments.
- The aggregate firewall rejects readiness measurements and private details.
- Existing readiness or output state prevents reuse; no cleanup path exists.

## Next Gate

The exact Stage 1 implementation commit must be pushed and both CI jobs must be
green. A proof-only closeout must bind those exact bytes and itself become
remotely green without repeating qualification or touching private state. Only
then may the already authorized one-shot Stage 2 readiness and target-free
structural confirmation run. There is no retry or rerun.

Engineering capability added: a generated-qualified fixed-path wrapper now
enforces exact finite readiness before aggregate structural discrimination and
proves that every nonpassing readiness pattern blocks source construction.

Scientific claim not established: no private structural source, archive
payload, neural signal, target, model, prediction, or score was accessed, so no
neural effect or decoding capability was established.
