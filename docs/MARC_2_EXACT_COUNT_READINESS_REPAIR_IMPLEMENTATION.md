# MARC2-VR33A Exact-Count Readiness Repair Implementation

Date: 2026-08-23

Lane: `MARC2-VR33A`

Status: **Generated qualification passed; remote implementation proof pending**

Machine records:

- `registries/marc2_exact_count_readiness_repair_implementation.v0.json`
- `registries/marc2_exact_count_readiness_repair_result.v0.json`

## Proof Before Implementation

Exact registration `23adf07a328824d3b671e8fd8edf3c9b8d1f15ba` passed Base
Python job `97181894886`, Optional Neuro Readers job `97181895045`, and CI
`32634409230` before implementation began.

The implementation binds the unchanged five-file, 75,965-byte registered
input set and exact contract SHA-256
`db8e43a81d7f14b5c438bbd39c8dd7e87d8fbe12e9934f9df8598699d1b590b7`.

## Implemented Surface

The dependency-free module
`src/neurodecodekit/datasets/marc2_exact_count_readiness.py` exposes only:

- `plan`: inspect the frozen generated-only execution plan;
- `qualify`: run the exact 16-path generated matrix.

There is no `execute` or `inspect` command and no path, URL, sample-count,
interval, timeout, route, output, retry, or resource override.

The reusable collector uses a bounded three-step `for` loop. It calls an
injected provider with sequences 1, 2, and 3, sleeps exactly twice for the
fixed five-second interval, validates every strict generated mapping, and
copies each accepted value into a frozen dataclass. It returns ready only when
all three samples pass. The collector has no filesystem operation and imports
or calls no consumed wrapper.

## Measured Qualification

The sole fresh-process qualification under one CPU thread, one worker, and one
numerical job passed:

- eight pass/fail patterns across two exact replays, for 16 paths;
- exactly 48 provider calls and 48 returned samples;
- exactly 32 sleeper calls;
- two ready paths, both `PPP`, and 14 not-ready paths;
- exact replay digest
  `67298e33712fcfc3046b356ab3d6416968325b5b9311bfc4f968ad0ff4d39195`;
- 67 direct refusals;
- zero source mutations and zero retained output.

It processed 4,136 generated input bytes in 0.004203916992992163 seconds at
24,215,552-byte peak RSS. The canonical aggregate report was 2,390 bytes.
Raw-data reads, real-cache reads, model runs, training runs, network bytes, and
new-payload bytes were zero.

## Boundary

The qualification read only the five committed artifacts frozen by the
contract. It did not open `.codex_work`, readiness state, consumed markers,
private paths, consumed output, archive members, neural signal, targets,
labels, models, predictions, scores, providers, streams, devices, hardware, or
another project.

VR32P remains consumed, byte-identical, and not fully protocol-conforming. The
VR33A result does not repair or reinterpret its R2 observation. The next gate
is exact implementation commit, push, and both green CI jobs, followed by a
proof-only closeout that repeats no qualification. Any future private adoption
requires a separately frozen Tier C packet and decision.

Engineering capability added: future proof-gated wrappers can collect an
exact finite readiness budget instead of using an open-ended consecutive-pass
loop.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
