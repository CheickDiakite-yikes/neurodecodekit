# RW3 Replay And Live-Source Primary-Source Research

Date: 2026-07-10

Status: **Research complete for preregistration; no adapter executed**

Contract: `registries/replay_equivalence_contract.v0.json`

Proof posture: official documentation and maintained source review only

## Research Question

What must NeuroDecodeKit preserve and measure so that an offline recording,
BrainFlow dummy source, LSL loopback, XDF recording, and eventually a physical
device can emit one honest source-chunk interface without silently changing
payloads, sample order, timestamps, packet loss, state, or causal claims?

This is an acquisition-interface question. It is upstream of Loop 21's causal
frame producer and far upstream of text decoding. A playback API, network
stream, or smooth waveform display is not evidence of neural information or
real-time text.

## Method And Access Boundary

The review used only maintained project documentation, release metadata, and
tagged source current on 2026-07-10. It did not install or import BrainFlow,
`pylsl`, `liblsl`, or PyXDF. It did not open a socket, resolve a stream, create
an outlet/inlet, prepare a board session, read an XDF file, enumerate hardware,
or access a recording.

Local dependency inventory:

```text
brainflow: not installed
pylsl:    not installed
pyxdf:    not installed
```

Current upstream releases observed:

| Component | Version | Role in a future staged implementation |
|---|---:|---|
| BrainFlow | 5.22.2 | synthetic and playback-file boards only |
| pylsl | 1.18.2 | Python LSL binding |
| liblsl | 1.17.7 | native transport and clock implementation |
| PyXDF | 1.17.5 | raw and corrected XDF import views |

No dependency is added by RW3 preregistration. A different future version
requires a committed contract amendment before implementation.

```text
dataset downloads:                    0
device sessions:                      0
socket or stream operations:          0
raw or real-data reads:               0
consumed-cache reads:                 0
target/label reads:                   0
model/decoder/training runs:          0
generated waveform or replay bytes:  0
research runtime and peak RSS:        unavailable; not isolated
```

## Findings That Change The Contract

| Primary finding | Required RW3 response |
|---|---|
| BrainFlow playback generates new timestamps by default. | The identity path must issue `old_timestamps`; `new_timestamps` is a separate negative control. |
| BrainFlow playback/streaming shape and rate come from `master_board`. | Bind the master board, preset, descriptor, channel indices, and sampling rate in provenance. |
| BrainFlow `get_board_data` drains its ring buffer while `get_current_board_data` does not. | Count destructive and nondestructive calls separately and allow only one state-advancing read path. |
| BrainFlow timestamps are Unix timestamps, sometimes created on the host when packages arrive. | Preserve them as source time; do not call them physical sample time or capture latency. |
| BrainFlow presets can have different rates, timestamps, and packet IDs. | Treat each preset as an independent stream ID with an explicit clock relationship. |
| LSL does not synchronize timestamps by default. | Preserve the primary inlet view with `proc_none`; store correction as a separate derived view. |
| LSL postprocessing can destroy access to original timestamps. | Do not use clock-sync/dejitter/monotonize flags in the primary identity path. |
| LSL clocks are monotonic with an arbitrary epoch, not wall clocks. | Never compare them naively with Unix time; retain named clock domains and mapping ledgers. |
| LSL recovery depends on a stable `source_id`. | Require one exact source ID, record reconnect generation, and refuse ambiguous resolution. |
| LSL `pull_chunk` can return one timestamp per sample. | Require per-sample timestamps; a last-timestamp-only API is insufficient for RW3. |
| PyXDF defaults to synchronization and dejittering. | Define separate raw (`false/false`) and derived (`true/true`) import views. |
| PyXDF can detect clock resets and data breaks using configured rules. | Record every argument and correction segment; never present corrected timestamps as source timestamps. |
| Python wall-clock time can move backwards, while `monotonic_ns` cannot. | Use `monotonic_ns` for local arrival/duration and redact absolute wall-clock values. |

## BrainFlow Boundary

### Dummy Boards Are Useful But Not Equivalent

BrainFlow's Playback File Board replays files produced by another BrainFlow
board. It requires the playback board ID, a file path, and the original
`master_board`; optional auxiliary and ancillary files correspond to separate
presets. The Synthetic Board generates data without hardware.

These are appropriate future adapter mechanics tests. Neither is a device
qualification result.

The Streaming Board is intentionally excluded from the first BrainFlow stage.
It consumes multicast data and adds a network boundary that must not be mixed
with file-playback validation.

### Timestamp Modes

Playback stops at end-of-file and generates new timestamps by default. Its
configuration commands include:

```text
loopback_true
loopback_false
new_timestamps
old_timestamps
```

The primary equivalence path therefore requires `old_timestamps`. A
`new_timestamps` run is useful only to prove that the semantic hash changes and
that NeuroDecodeKit refuses to call it source-timestamp identity.

### Data Layout, Units, And Packet Identity

BrainFlow returns `[rows, samples]` double arrays. Rows can represent EXG,
motion, timestamps, markers, package counters, and board-specific channels.
The board descriptor and named index helpers, not positional guesses, identify
those rows.

BrainFlow documents EXG values in microvolts wherever possible. RW3 must retain
the declared unit rather than silently convert microvolts to volts. A later
preprocessing stage may define a conversion, but transport equivalence may not.

Unix timestamps have microsecond representation, but some devices timestamp a
package on the computer when it arrives. That timestamp can support ordering
and a declared source clock. It cannot establish sensor acquisition time or
capture-to-host latency without device-specific evidence.

### Ring-Buffer Semantics

`get_board_data` removes returned data from the ring buffer.
`get_current_board_data` returns recent data without removing it. Mixing the two
without a state rule can duplicate or skip samples. RW3 therefore records both
call counts and permits exactly one destructive primary drain sequence.

## LSL Boundary

### Original And Corrected Time Must Both Exist

LSL supplies sample timestamps plus periodic clock-offset measurements. It
does not synchronize by default. The primary inlet must use no automatic
postprocessing and retain the outlet's original timestamps.

Clock correction is a separate derived operation:

```text
corrected timestamp = source timestamp + measured offset
```

The ledger records offset, remote time, uncertainty, correction segment, and
loaded library versions. If a clock reset is detected, the adapter starts a
new segment; it never fits one mapping across that reset.

The official API warns that enabling inlet postprocessing means the original
timestamps can no longer be recovered. That makes `proc_ALL` unsuitable as the
primary proof path. `proc_clocksync`, `proc_dejitter`, and `proc_monotonize` may
be derived comparisons only after raw timestamps are bound.

### Clock Accuracy Is Not Device Latency

LSL's offset measurement resembles NTP and may achieve sub-millisecond clock
mapping on a good local network. This does not measure:

- delay from physical sampling to device timestamp;
- firmware or wireless buffering;
- when a visual or audio stimulus physically appeared;
- downstream preprocessing, encoder, decoder, rendering, or user latency.

The preregistered local-loopback correction-uncertainty cap is 5 ms. It is a
transport rehearsal threshold, not a promise for Wi-Fi or a wearable.

### Chunks, Buffers, Loss, And Recovery

`pull_chunk` can return a timestamp for every sample. The inlet's maximum
buffer and chunk sizes are explicit, and real-time applications should keep
only the backlog they actually need. Larger chunks trade latency for lower
overhead; the LSL FAQ identifies roughly 5-30 ms as a practical default range
and warns that long chunks make real-time dejittering harder.

LSL uses reliable transport and can buffer through interruptions, but that
does not prove that a device produced every physical sample. Packet loss is
zero only when a trusted sample index or packet counter proves it. Timestamp
gaps without that evidence remain inferred.

Automatic recovery requires a stable source ID. A reconnect increments the
RW3 generation counter. A clock reset, channel change, source-ID change, or
metadata change cannot be spliced into the previous stream silently.

Resolution may return multiple matching streams. RW3 refuses ambiguity rather
than choosing the newest stream, because that would make source identity depend
on network timing.

### Network Confinement

LSL resolution uses network sockets. A future loopback stage is not authorized
until its configuration proves that discovery and transport cannot reach a
non-loopback interface. If the installed LSL version cannot make that boundary
auditable, the LSL stage parks; the project does not weaken the local-only
contract to obtain a demo.

## XDF Boundary

XDF is the preferred recorded LSL container because it can retain stream
metadata, source timestamps, and clock-offset history. PyXDF 1.17.5 exposes
the necessary controls:

Primary raw view:

```python
load_xdf(
    path,
    select_streams=exact_stream,
    synchronize_clocks=False,
    dejitter_timestamps=False,
)
```

Derived corrected view:

```python
load_xdf(
    path,
    select_streams=exact_stream,
    synchronize_clocks=True,
    handle_clock_resets=True,
    dejitter_timestamps=True,
)
```

The raw view owns source identity. The derived view is useful for offline
multi-stream alignment but must record every clock-reset and jitter-break
argument. PyXDF's `playback_lsl` command uses current timestamps, so it is not
a source-timestamp identity path.

No XDF file is read in this preregistration.

## Canonical Source-Chunk Consequences

The machine contract selects `[channels, samples]` because it matches existing
NeuroDecodeKit and BrainFlow signal orientation. LSL sample-major arrays must
be transposed explicitly and record that transformation.

Every data chunk carries:

- pseudonymous stream/source/item identity and adapter version;
- immutable channel order, types, units, geometry status, and row indices;
- exact payload dtype, shape, true length, capacity, mask, and zero padding;
- source sample indices;
- raw source timestamps, optional corrected timestamps, and local monotonic
  arrival bounds as three separate views;
- raw/unwrapped packet counters and exact gap/duplicate/reorder/wrap/reset
  accounting;
- causality and read-ahead availability;
- source/config/contract/registry/split/adapter hashes;
- a chunk-boundary-sensitive hash plus a boundary-invariant semantic prefix
  hash.

No target, label, prediction, or model member exists in this contract.

## Unavailable Fields

The following remain explicitly unavailable after research:

- physical capture-to-timestamp latency for any device;
- generic EEG timestamp-jitter threshold;
- generic wireless transport-latency threshold;
- verified LSL loopback confinement on this machine;
- BrainFlow/PyLSL/PyXDF import or runtime behavior in this environment;
- physical packet-loss detectability for boards without a trusted counter;
- cross-device clock mapping;
- end-to-end text latency;
- task/model/benchmark compatibility;
- physical-device or at-home qualification.

## Decision

Freeze RW3 before implementation. The registration itself authorizes no code
adapter or fixture. A separate review may authorize Stage A, the pure-Python
synthetic source-chunk gate. BrainFlow, LSL, XDF, loopback sockets, and hardware
remain independently gated after Stage A passes.

## Primary Sources

BrainFlow:

- https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
- https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html
- https://brainflow.readthedocs.io/en/stable/UserAPI.html
- https://github.com/brainflow-dev/brainflow/releases/tag/5.22.2

LSL:

- https://github.com/sccn/labstreaminglayer
- https://labstreaminglayer.readthedocs.io/info/time_synchronization.html
- https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/inlet.html
- https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html
- https://labstreaminglayer.readthedocs.io/info/faqs.html
- https://github.com/labstreaminglayer/pylsl/releases/tag/v1.18.2
- https://github.com/sccn/liblsl/releases/tag/v1.17.7

XDF and local clock:

- https://github.com/xdf-modules/pyxdf/blob/v1.17.5/src/pyxdf/pyxdf.py
- https://github.com/xdf-modules/pyxdf/releases/tag/v1.17.5
- https://docs.python.org/3/library/time.html#time.monotonic_ns
