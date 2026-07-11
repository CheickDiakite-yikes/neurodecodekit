# RW3 Offline Replay And Live-Source Equivalence Preregistration

Date: 2026-07-10

Status: **Frozen before implementation**

Contract: `registries/replay_equivalence_contract.v0.json`

Research: `docs/RW3_PRIMARY_SOURCE_RESEARCH.md`

Registration commit: `c3d1f01`

Proof posture: primary-source-informed protocol; no source adapter, replay, or
live result exists yet

## Objective

Freeze the smallest source-chunk interface and experiment that can eventually
test whether a deterministic recording, BrainFlow dummy source, LSL loopback,
and XDF recording preserve the same signal identity, sample axis, clock views,
packet anomalies, state, and semantic stream across transport chunk schedules.

RW3 moves NeuroDecodeKit toward local, private, incremental acquisition. It
does not connect a board or decode text. It exists because “the waveform
arrived” is too weak a foundation for real-time claims: payload values can be
scaled, timestamps regenerated, samples duplicated, buffers drained twice,
clock resets hidden, or stream identity selected ambiguously while a plot still
looks plausible.

## Registration Boundary

This milestone writes documents, one JSON contract, and pure-Python invariant
tests only. It does not authorize implementation automatically.

### Included Now

- Primary-source BrainFlow, LSL, PyXDF, and Python clock research.
- A strict versioned future `neurodecodekit.source_chunk` envelope.
- Exact raw/corrected/arrival timestamp separation.
- Gap, duplicate, reorder, counter-wrap, reconnect, and clock-reset semantics.
- Five deterministic future replay schedules.
- Eighteen future synthetic fixture families.
- Future adapter stages and dependency versions.
- Exact resource, privacy, access, refusal, and claim rules.
- A dependency-free contract-invariant unit suite.

### Excluded Now

- Source-chunk implementation, save/load code, fixtures, or CLI commands.
- BrainFlow, `pylsl`, `liblsl`, or PyXDF installation/import.
- BrainFlow board preparation, start/stop, synthetic, playback, streaming, or
  physical-board sessions.
- LSL discovery, resolver, outlet, inlet, time-correction, or pull calls.
- XDF reads or writes.
- Loopback, multicast, Wi-Fi, BLE, serial, USB, or external network access.
- Hardware enumeration or connection.
- Every real recording/cache, S20, and consumed S7/S21 evidence.
- Seeds 2203, 2303, and 2353.
- Targets, labels, predictions, CER/WER, models, decoders, or training.
- Filtering, rereferencing, resampling, interpolation, cleaning, scaling, or
  unit conversion.
- GUI, waveform plot, mobile packaging, or end-to-end latency claim.

## Compatibility Boundary

RW2 closes exact synthetic file readability at compatibility level 2. RW3 does
not promote any recording or device to level 6.

A future passing RW3 Stage A can establish only the source-chunk interface on
generated arrays. A future dummy-board/loopback pass can establish adapter
mechanics for exact dependency versions. Workbench level 6 still requires a
separately preregistered physical device, recorded-versus-live comparison,
consent/privacy plan, and measured device timing.

## Four Staged Adapters

The stages are sequential. A later stage cannot be used to rescue a failed
earlier contract.

| Stage | Future adapter | Authorized by this commit? | Purpose | Hard boundary |
|---|---|---|---|---|
| A | Pure-Python synthetic replay | No | Implement envelope, state, schedules, anomalies, hashes, and reports without optional dependencies. | No sockets, board SDK, XDF, real data, targets, or model. |
| B | BrainFlow synthetic + playback boards | No | Exercise BrainFlow 5.22.2 dummy boards against Stage A. | No Streaming Board, physical board, or network. |
| C | LSL local loopback | No | Exercise one numeric pylsl 1.18.2/liblsl 1.17.7 outlet/inlet with raw and corrected time. | No external interface or ambiguous discovery; park if loopback confinement cannot be proven. |
| D | PyXDF dual view | No | Compare raw and default-corrected PyXDF 1.17.5 views. | No unknown stream selection or confusion of raw and corrected time. |

Each stage requires a separate authorization and coherent commit after the
previous stage passes.

## Source-Chunk Schema V0

Canonical payload orientation is:

```text
[channels, capacity_samples]
```

The envelope has six record kinds:

```text
stream_start
data
gap
reconnect
stream_end
source_error
```

### Identity

Every record preserves:

- pseudonymous stream, source, source-item, and evidence-cohort IDs;
- modality, device type, adapter ID/version, and preset/stream role;
- chunk sequence, correction segment, and reconnect generation;
- first/final record status.

A source ID or channel contract change creates a new stream. It cannot be
spliced into the old stream because the values happen to have the same shape.

### Channels

Every record binds exact:

- channel names, types, units, order, and adapter-native row indices;
- geometry-availability mask and geometry payload hash;
- device/preset descriptor hash.

Exact coordinates remain absent from public reports. A channel reorder, type
change, unit change, descriptor change, or geometry-hash change midstream is a
hard refusal.

### Payload, Length, And Padding

V0 accepts only `float32` or `float64`. The exact declared conversion target is
part of the adapter configuration. Silent downcasting is forbidden.

Every data record contains:

- shape, dtype, true valid-sample count, allocated capacity, and mask;
- exact zero in every invalid padded position;
- finite values only;
- no target, label, event description, or prediction member.

Only valid samples reach Loop 21. Padding is storage/transport structure, not
signal.

### Sample Axis

Every valid value column has a source sample index. Contiguous clean data
increments by exactly one. A gap is represented by a `gap` record before the
next data record; missing values are never filled.

The envelope records first index, exclusive stop, nominal rate, and nominal
sample period. The nominal period does not replace measured timestamps.

## Three Timestamp Views

RW3 never stores “timestamp” as one overloaded field.

### 1. Source Time

`source_timestamps_sec` is the adapter's original per-sample time, preserved
bitwise. It may be recording-relative, BrainFlow Unix time, or the LSL outlet's
steady-clock domain.

It is never smoothed, sorted, dejittered, monotonized, or replaced.

### 2. Corrected Time

`corrected_timestamps_sec` is a nullable derived view. It exists only when one
named correction method and hash-bound ledger are available. Replaying the
same source and ledger must reproduce corrected timestamp bits exactly.

For LSL, the primary inlet uses `proc_none`; offset, remote time, and
uncertainty from `time_correction` are recorded separately. Automatic inlet
postprocessing cannot own the primary path because it destroys the original
timestamps.

For XDF, the raw view disables clock synchronization and dejittering. The
derived view enables synchronization, clock-reset handling, and dejittering
with every argument recorded.

### 3. Local Arrival Time

The adapter measures chunk arrival start/end with `time.monotonic_ns`. Those
integers support local durations and scheduling delay. They are not converted
to wall-clock time.

Absolute Unix, LSL epoch, hostname, IP, and device serial values are redacted
from reports.

### Clock Resets

A reset or source restart increments correction segment and reconnect
generation. No line is fit through a reset. If the mapping cannot be rebuilt,
corrected time is unavailable and cross-stream alignment cannot pass.

## Packet And Gap Semantics

Packet loss is **proven** only by a trusted source sample index or unwrapped
packet counter. A timestamp interval alone produces an inferred gap, not a
zero-loss or exact-loss result.

Every record carries:

- raw and unwrapped counters when available;
- counter modulus and wrap count;
- exact gap-before, duplicate, and out-of-order counts;
- timestamp duplicate/regression counts;
- clock-reset and source-restart flags;
- inferred versus proven gap counts;
- `interpolation_performed=false`.

Rules:

1. Never interpolate missing samples.
2. Never silently sort out-of-order samples.
3. Never silently deduplicate repeated samples.
4. Never call missing packet evidence “zero loss.”
5. Never resume across a source/config/contract/hash collision.

## BrainFlow Rules

The future BrainFlow stage pins 5.22.2.

Primary playback must:

1. use `PLAYBACK_FILE_BOARD` with the exact `master_board`;
2. bind default/auxiliary/ancillary presets as separate streams;
3. issue `old_timestamps` before the primary run;
4. use `new_timestamps` only as a negative control;
5. use board descriptors/index helpers rather than guessed row numbers;
6. preserve BrainFlow units, including microvolts where declared;
7. count every destructive `get_board_data` call;
8. ensure nondestructive `get_current_board_data` never advances primary state;
9. refuse Streaming Board and every physical board.

BrainFlow Unix time may reflect host receipt time. It is not labeled sensor
capture time without device-specific evidence.

## LSL Rules

The future LSL stage pins pylsl 1.18.2 and loaded liblsl 1.17.7.

It must:

1. create exactly one numeric stream with one stable pseudonymized source ID;
2. refuse multiple resolution matches;
3. use `proc_none` on the primary inlet;
4. use `pull_chunk` with one returned timestamp per sample;
5. record max buffer/chunk settings and every pull count;
6. record `time_correction` offset, remote time, and uncertainty;
7. check clock resets and start a new segment;
8. treat recovery as available only with a stable source ID;
9. prove loopback-only confinement before opening sockets;
10. record pylsl, liblsl, OS, architecture, and config hashes.

The local-loopback correction uncertainty must be at most 5 ms. This is not a
device, Wi-Fi, or capture-latency threshold.

## XDF Rules

The future XDF stage pins PyXDF 1.17.5 and selects one exact stream.

Raw view:

```text
synchronize_clocks=false
dejitter_timestamps=false
```

Derived view:

```text
synchronize_clocks=true
handle_clock_resets=true
dejitter_timestamps=true
```

All remaining reset/break/winsor arguments are recorded. The raw view owns
source identity. PyXDF `playback_lsl`, which replays with current timestamps,
is not accepted as a source-timestamp identity path.

## Registered Schedules

The same semantic stream must survive five boundaries:

| Schedule | Rule | Purpose |
|---|---|---|
| `single_sample` | one sample per chunk | minimum batching-delay stress |
| `fixed_20ms` | rounded 20 ms of nominal samples | primary local schedule |
| `native_packet` | fixture/adapter packet boundaries | native boundary audit |
| `deterministic_jitter_5_to_30ms` | seeded 5-30 ms pattern | poll/transport variability |
| `whole_source` | all values in one bounded chunk | equivalence stress, never a real-time mode |

Chunk hashes should differ where boundaries differ. The semantic stream hash
must be exact across all five.

## Future Fixture Matrix

Stage A must generate exactly registered, target-free conditions:

1. clean contiguous;
2. final partial chunk;
3. bounded timestamp jitter;
4. linear clock drift;
5. proven sample gap;
6. timestamp-only inferred gap;
7. duplicate packet;
8. out-of-order packet;
9. packet counter wrap;
10. clock reset and reconnect;
11. source timestamp regression;
12. unknown clock mapping;
13. channel-order or unit mismatch;
14. nonfinite payload;
15. nonzero padding;
16. tampered hash;
17. ambiguous stream identity;
18. resource-cap violation.

No fixture contains text, token IDs, class labels, participant metadata, or a
prediction target.

## Numeric And Timing Gates

Exact:

- valid payload after the one declared dtype conversion;
- source indices and source timestamp bits;
- corrected timestamp bits when the same ledger is replayed;
- masks and zero padding;
- channels, types, units, order, and geometry hash;
- anomaly ledger;
- state resume versus uninterrupted run;
- semantic stream hash across schedules.

Bounded for the future synthetic real-time-paced rehearsal:

```text
schedule delay p95:        <= 20 ms
schedule delay maximum:    <= 100 ms
compute real-time factor:  <= 1.0
LSL correction uncertainty <= 5 ms (local loopback only)
```

No generic device timestamp-jitter, wireless latency, capture latency, or
end-to-end text latency threshold is invented in RW3.

## State And Resume

Serialized state is sorted compact JSON under 4,096 bytes and contains only
counters, last timestamp/counter bits, correction/reconnect generation,
cumulative anomaly counts, semantic prefix hash, and end state. It contains no
waveform history.

Resume must produce the same final semantic hash and anomaly ledger as an
uninterrupted run. State from another source/config/contract/prefix refuses.

## Semantic Hash

SHA-256 canonicalization includes:

- stream and channel identity;
- valid payload bits;
- source indices;
- raw and corrected timestamp bits or explicit unavailable status;
- masks;
- anomaly/reconnect ledger;
- source/config/contract/registry/split hashes.

The semantic hash excludes chunk boundaries, runtime/RSS, wall-clock values,
absolute paths, and free text. Every record carries a prefix hash so corruption
or reordering is localized.

## Privacy And Security

Reports omit:

- absolute paths, participant/demographic fields, and measurement dates;
- serials, hostnames, IP addresses, and plaintext LSL source IDs;
- free-form XML/annotations/markers;
- exact wall-clock values and geometry coordinates;
- waveform values, target text, labels, and predictions.

Allowed aggregate output includes modality/device type, pseudonymous hashes,
channel names/types/units/geometry status, relative timing, anomaly counts,
versions, resources, access counters, warnings, and unavailable fields.

Loopback is not synonymous with private. The LSL stage parks if interface
confinement cannot be proven.

## Resource Caps

```text
CPU threads / workers:                   1 / 1
channels / nominal rate:                 512 / 4,096 Hz
valid samples per stream:                262,144
total channel-sample values:             4,194,304
samples per chunk / chunks per run:      4,096 / 100,000
source files / source bytes:             64 / 16 MiB
materialized payload:                    32 MiB
serialized adapter state:                4 KiB
output per run:                          4 MiB
complete fixtures plus reports:          16 MiB
hard generated-artifact ceiling:         32 MiB
runtime / peak RSS:                      30 sec / 1 GiB
external network, real, cache, target,
model, decoder, and training operations: 0
```

Physical storage bytes read remain unavailable unless validated
instrumentation measures them. Array size is not disk I/O.

## Access Counters

Future reports count metadata and synthetic files/bytes, payload values,
BrainFlow session/start/destructive/nondestructive calls by board kind, LSL
resolve/outlet/inlet/pull/correction/reset calls, loopback/external network
operations, XDF files/bytes, and real/cache/target/model/training/decoder
access.

An unavailable counter is not zero. A pass requires every required zero count
to be measured or guaranteed structurally.

## Exact Refusal Classes

The machine contract freezes 30 refusal IDs spanning:

- identity/config/contract collisions;
- ambiguous stream resolution;
- channel, dtype, shape, nonfinite, and padding violations;
- unrepresented gaps, duplicates, reordering, wraps, resets, and reconnects;
- overwritten timestamps or missing correction ledgers;
- unavailable packet-loss proof where required;
- dependency version mismatch;
- external network, unproven loopback, live hardware, and forbidden BrainFlow
  board use;
- LSL automatic timestamp postprocessing in the primary path;
- wrong PyXDF raw-view arguments;
- resource caps and unsafe output collisions.

Implementations must return the exact registered ID, not a generic exception
that hides which proof failed.

## Registration Acceptance Gates

RW3 preregistration passes only if:

1. research and contract identify maintained primary sources;
2. JSON parses and a pure-Python test validates every frozen invariant;
3. no optional dependency is added, installed, imported, or executed;
4. no fixture, waveform, cache, socket, board, stream, or XDF artifact exists;
5. no real/consumed/target/model/training/decoder access occurs;
6. docs, tracker, decision log, handoff, workbook, and continuation prompt
   agree that implementation is not authorized;
7. complete tests, Ruff, compileall, links, secrets, and diff checks pass;
8. the registration commit is pushed before any Stage A code exists.

## Future Stage A Acceptance Gates

Stage A, if separately authorized, must satisfy every machine-contract gate,
including all five schedules, all 18 fixture families, strict save/load/resume,
exact hashes, malformed/tamper/collision/cap tests, measured resources, and
zero optional/real/target/model/network access.

It may then request Stage B authorization. It may not skip directly to LSL or
hardware.

## Proceed, Park, And Kill Rules

**Proceed from registration:** request authorization for Stage A only.

**Park an optional adapter:** it cannot preserve original values/timestamps,
prove source identity, bind dependency/native-library versions, enforce local
network boundaries, or stay within caps.

**Kill the path:** it silently changes payload/time/order/channels/gaps, hides
an anomaly, opens unapproved hardware/network/data, or presents replay/live
connectivity as decoding evidence.

## Warnings And Unavailable Fields

Always show:

- no adapter exists yet;
- playback may regenerate timestamps;
- BrainFlow Unix time may be host receipt time;
- LSL is unsynchronized by default;
- automatic LSL/PyXDF correction changes timestamps;
- reliable transport does not prove no device loss;
- replay pacing is not capture or end-to-end latency;
- source causality is not decoder causality;
- dummy/loopback success is not device qualification;
- no real-time, portable, arbitrary-thought, or clinical claim.

## Claim Boundary

**Engineering capability this registration prepares:** a future adapter can be
judged against one strict, modality-aware, source-preserving chunk/clock/gap/
state contract before hardware access.

**Scientific or decoding claim not established:** preregistration does not
establish signal quality, neural advantage, task compatibility, decoded text,
unseen-person transfer, physical-device reliability, real-time behavior,
at-home usefulness, arbitrary-thought decoding, or clinical efficacy.
