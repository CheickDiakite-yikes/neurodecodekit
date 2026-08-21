# MARC2-VR15P Generated Qualification Result

Date: 2026-08-21

Route: `MARC2VR15P-G1`

Status: **Stage 1 generated qualification passed; private stage closed**

## Measured Result

```text
generated cases:                 17
source orders:                   2
exact replays:                   2
generated paths:                68
VR15A classifier calls:         68
nested unchanged VR12A calls:   68
route count for G1 and R1-R16:  4 each
direct refusals:                111
generated input bytes:          29,199,868
peak temporary bytes:           429,857
aggregate output bytes:         2,681
retained output bytes:          0
runtime seconds:                3.9979423339827918
peak RSS bytes:                 50,135,040
CPU threads / workers / jobs:   1 / 1 / 1
network / new payload bytes:    0 / 0
```

Matrix digest:
`5e16552822e94724d242758212feead71abd9d66246d71251889c51117ad953c`

Refusal digest:
`692e820c41c5af8f121bfe391e6115099f3f3a8acb2e91a2f0dca44334051c71`

Every temporary path was invocation-created and removed. Private or
Git-ignored path operations, structural-source operations, prior consumed-root
operations, archive-member reads, signal/event/channel/geometry/target/label
reads, model or training operations, provider/network work, FW2/CIL1 work,
other-project operations, retries, releases, and claim upgrades were all zero.

## Acceptance

- exact green decision and fixed inputs validated;
- all 68 no-follow generated paths completed;
- every expected route appeared exactly four times;
- both replays and source orders agreed;
- source mutation count was zero;
- 111 direct refusal mutations passed;
- peak temporary and aggregate output remained below 1 MiB;
- retained output was zero; and
- private execution remained proof-gated.

Verification passed 30 focused tests and the complete dependency-free suite:
4,456 tests passed with 80 expected skips locally. Deterministic test replay
injects the frozen measured RSS value so the full runner's historical peak
cannot change the result; the production CLI continues to measure live peak
RSS, and direct refusal cases exercise the exact cap boundary.

The system Python command failed before package import and performed no
qualification. The measured result above came from the project `.venv`
interpreter under the exact one-thread environment.

Engineering capability proven: the wrapper preserves exact one-call route
semantics across all registered generated grammar classes under bounded
resources.

Scientific claim not established: this generated result is not neural data,
does not identify the private structural class, and establishes no decoding
accuracy, language decoding, live decoding, or thought-to-text capability.
