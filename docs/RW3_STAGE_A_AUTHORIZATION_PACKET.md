# RW3 Stage A Authorization Packet

Date: 2026-07-11

Status: **Awaiting explicit user authorization; no implementation authorized**

Target stage: **A - pure-Python synthetic replay only**

Frozen contract: `registries/replay_equivalence_contract.v0.json`

Authorization request:
`registries/rw3_stage_a_authorization_request.v0.json`

Contract binding:

```text
registration commit:       c3d1f01
contract schema:           neurodecodekit.replay_equivalence_contract 0.1.0
contract SHA-256:          6e4ef54049d9a6f77f64e7b6cfd6b911bd97b5693386f16b62f9d466f66b0469
contract Git blob SHA-1:   b407d1f1f0255ee2c46ef603b54e72e2c282bafe
request authorized now:   false
```

## Decision Requested

To authorize only this stage, use this sentence:

> Authorize RW3 Stage A exactly as scoped in
> `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`. Do not authorize Stages B-D.

To hold it, use:

> Hold RW3 Stage A. Keep every RW3 implementation authorization flag false.

General continuation, silence, a request to keep researching, or approval of a
different loop is **not** Stage A authorization.

## Why This Packet Exists

RW3 already freezes the semantics needed before local acquisition: source
identity, channel order and units, payload values, sample indices, three clock
views, packet anomalies, reconnect state, semantic hashes, chunk schedules,
privacy, resources, refusals, and claim boundaries. It deliberately authorizes
no code.

Stage A is the smallest implementation that can test those rules without
optional dependencies, sockets, devices, recordings, targets, or models. This
packet makes the next permission exact enough that “continue” cannot silently
turn into hardware or data access.

## What Authorization Would Do

Authorization would first permit one **authorization-only commit**. Before any
implementation, that commit must:

1. bind this request to the current contract hash;
2. change contract status to `stage_A_authorized_no_implementation_yet`;
3. set `authorization.preregistration_only` to `false`;
4. set only source-chunk implementation and synthetic-fixture generation to
   `true`;
5. set only Stage A's `implementation_authorized_now` field to `true`;
6. leave every optional dependency, socket, network, device, real-data, target,
   model, training, decoder, cleaning, and Stage B-D flag false;
7. pass and push the contract invariants before implementation begins.

Authorization does not allow implementation in the same unrecorded step. The
authorization commit must exist first.

## Exact Stage A Scope

Stage A may implement only a standard-library, target-free transport harness:

- strict `neurodecodekit.source_chunk` v0.1.0 records;
- save, load, validate, summarize, and deterministic hash APIs;
- bounded stream state save/load and exact resume;
- deterministic synthetic numeric transport fixtures with no neural meaning;
- all five registered chunk schedules;
- all 18 registered fixture families;
- explicit clean-equivalence versus expected-refusal outcomes;
- deterministic JSON, Markdown, and audit reports;
- collision, tamper, unsafe-path, privacy, and resource refusals;
- four CLI commands for fixture creation, inspection, replay, and report
  inspection.

Planned commands:

```text
neurodecode make-replay-equivalence-fixtures
neurodecode inspect-replay-equivalence-fixtures
neurodecode replay-equivalence-gate
neurodecode inspect-replay-equivalence-report
```

Planned ownership:

```text
src/neurodecodekit/streaming/source_chunk.py
src/neurodecodekit/streaming/replay_equivalence.py
src/neurodecodekit/streaming/replay_fixtures.py
src/neurodecodekit/experiments/replay_equivalence_gate.py
src/neurodecodekit/cli.py
tests/test_source_chunk.py
tests/test_replay_equivalence_gate.py
docs/RW3_STAGE_A_SYNTHETIC_REPLAY_CLOSEOUT.md
```

This is a scoped implementation map, not permission to create those files yet.

## Case Matrix

The implementation must execute every registered fixture family under every
registered schedule:

```text
5 schedules x 18 fixture families = 90 cases
```

Schedules:

1. `single_sample`
2. `fixed_20ms`
3. `native_packet`
4. `deterministic_jitter_5_to_30ms`
5. `whole_source`

Fixture families:

1. `clean_contiguous`
2. `final_partial_chunk`
3. `bounded_timestamp_jitter`
4. `linear_clock_drift`
5. `proven_sample_gap`
6. `timestamp_only_inferred_gap`
7. `duplicate_packet`
8. `out_of_order_packet`
9. `packet_counter_wrap`
10. `clock_reset_and_reconnect`
11. `source_timestamp_regression`
12. `unknown_clock_mapping`
13. `channel_order_or_unit_mismatch`
14. `nonfinite_payload`
15. `nonzero_padding`
16. `tampered_hash`
17. `ambiguous_stream_identity`
18. `resource_cap_violation`

A harness pass means the case matched its registered outcome. It does not mean
all cases are clean-equivalent. An anomaly or malformed case must produce its
exact warning/refusal instead of being silently repaired or dropped.

## Acceptance Gates

Stage A may be called complete only if:

1. save/load/validate/summary/resume APIs are strict and versioned;
2. all 90 schedule-by-fixture cases match their frozen outcomes;
3. semantic stream hashes are exact across schedules;
4. chunk hashes remain boundary-sensitive;
5. resumed and uninterrupted streams have identical semantic hashes and
   anomaly ledgers;
6. payload, sample indices, source timestamp bits, padding, channel identity,
   and provenance remain exact;
7. interpolation, silent sorting, and silent deduplication are zero;
8. every one of the 30 registered refusal IDs is reachable by a deterministic
   negative test;
9. collisions and unsafe paths refuse before output is written;
10. two clean-workdir runs produce byte-identical core artifacts;
11. every cap and access counter passes;
12. focused and complete tests, Ruff, compileall, links, Gitleaks, CLI help,
    deterministic replay, and `git diff --check` pass;
13. documentation and the tracker report measured resources and every warning;
14. the implementation commit is pushed before any Stage B request.

## Resource Envelope

| Resource | Hard cap |
|---|---:|
| CPU threads / workers | 1 / 1 |
| Channels / nominal sampling rate | 512 / 4,096 Hz |
| Valid samples per stream | 262,144 |
| Channel-sample values | 4,194,304 |
| Samples per chunk / chunks per run | 4,096 / 100,000 |
| Source files / source bytes | 64 / 16 MiB |
| Materialized payload | 32 MiB |
| Serialized state | 4,096 bytes |
| Output per run | 4 MiB |
| Complete fixture plus reports | 16 MiB |
| Hard generated-artifact total | 32 MiB |
| Runtime / peak RSS | 30 seconds / 1 GiB |

Generated files must remain under ignored `cache/`, `outputs/`, or
`.codex_work/` roots. No generated fixture/report debris enters Git.

## Access Ledger

Every Stage A run must report zero for:

```text
external network calls
real data reads
consumed cache reads
target, label, prediction, or text reads
model runs
training runs
decoder runs
BrainFlow calls
LSL calls
XDF reads or writes
socket calls
device discovery or hardware sessions
```

The producer must be causal, emit only received samples, require zero right
context, and state that end-to-end text latency was not measured.

## Forbidden Even After Stage A Authorization

- installing or importing BrainFlow, `pylsl`, `liblsl`, or PyXDF;
- opening any socket or network interface;
- resolving an LSL stream;
- starting a synthetic, playback, streaming, or physical board;
- enumerating or connecting hardware;
- reading or writing XDF;
- opening S20, S7, S21, another recording, or any consumed cache;
- creating or reading targets, labels, text, predictions, or participant data;
- running a model, decoder, training, filtering, cleaning, resampling, or
  interpolation;
- implementing Stage B, C, or D;
- claiming useful signal, decoding, real-time behavior, or device support.

## Stop Rules

**Proceed:** all 90 cases and every acceptance gate pass. The only next action
is a separate Stage B authorization request.

**Park:** one optional or platform-specific mechanic is unavailable, but core
semantics remain fail-closed and inspectable. Record the measured reason.

**Kill:** payload, time, order, identity, gaps, state, or privacy changes
silently, or any forbidden data, dependency, socket, network, device, model, or
training access occurs.

## Claim Boundary

**Engineering capability this authorization could permit:** a future
dependency-free harness can prove that generated source chunks preserve exact
payload, time, order, anomaly, state, and semantic identity across transport
schedule boundaries.

**Scientific or decoding claim not established:** this packet and any future
Stage A pass cannot establish signal quality, neural information, decoded text,
real-time behavior, physical-device reliability, portable or at-home use,
arbitrary-thought decoding, assistive efficacy, diagnosis, or clinical utility.

## Current Decision

```text
authorized:          false
implementation:     absent
fixtures:           absent
CLI additions:      absent
optional imports:   absent
data/model access:  zero
next action:        explicit user decision on Stage A only
```
