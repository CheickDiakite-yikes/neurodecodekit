# Loop 42 Primary-Source Research And One-Device Qualification Boundary

Date: 2026-07-13

Status: **Planning research complete; experiment Not Started and no SDK,
fixture, device, stream, recording, participant, model, or hardware operation is
authorized**

Machine boundary: `registries/loop42_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 42

## Decision Summary

Loop 42 selects **OpenBCI Cyton, base 8-channel board, USB-radio transport,
without Daisy or Wi-Fi Shield** as the one future mechanics candidate. The
selection is based on official specification and adapter documentation only.
It is not a purchase recommendation, hardware authorization, compatibility
result, EEG signal result, or decoding result.

This exact path is selected because it offers a useful combination for a
future bounded local qualification:

1. eight inspectable ExG channels at a nominal 250 Hz;
2. a documented 33-byte packet and 8-bit sample counter;
3. explicit ADS1299 gain, input, SRB2 reference, and BIAS configuration;
4. a USB dongle and virtual-serial path that does not require Internet access;
5. direct BrainFlow board metadata plus synthetic and playback development
   paths; and
6. local raw-file support with optional networking that can be disabled and
   audited.

Those properties make the configuration testable. They do **not** show that
eight channels are sufficient for prompted sentence decoding, imagined speech,
or thought typing. The current qualification level is only:

```text
L42-Q0_official_specification_candidate_only
```

The maximum future Loop 42 result is `L42-Q3_named_local_device_mechanics` for
the exact board, firmware, dongle, transport, adapter, host, and bounded
session. Task information, neural advantage, text decoding, repeated-session
reliability, real-time text, home usability, safety, and clinical claims remain
separate experiments.

## Why Cyton, And Why This Configuration

The existing device registry contains 13 records, seven of which expose EEG or
generic ExG channels. Loop 42 needs one path whose raw mechanics can be
interrogated before any prediction work. The frozen selection criteria require:

- scalp-EEG capability when electrodes and references are verified;
- at least eight ExG channels and 250 Hz native streaming;
- a macOS host path and raw local access;
- an inspectable packet counter;
- documented reference and BIAS behavior;
- a target-free synthetic or playback path;
- no mandatory cloud transport; and
- board-specific adapter metadata.

The Cyton base board is the best current planning fit. The Daisy module is
excluded because it changes the channel/rate behavior and packet semantics.
The Wi-Fi Shield and GUI network stream are excluded because they change the
transport and privacy boundary. Ganglion has fewer channels; Muse and Crown
use different closed or vendor-mediated paths; Galea introduces multimodal and
network complexity; and the g.tec options are better treated as partner or
research-device lanes. None of those comparisons is a signal-quality ranking.

No device is known to be present in this workspace. No price, purchase,
availability, or ownership claim is made.

## Primary-Source Findings

### 1. The packet is inspectable, but the counter is not a clock

The [OpenBCI Cyton data-format documentation](https://docs.openbci.com/Cyton/CytonDataFormat/)
describes a packet with a header, one-byte sample counter, eight 24-bit ADS
channel values, six auxiliary bytes, and a footer. That is 33 bytes. The
counter wraps modulo 256; wrap, packet loss, reset, and reconnect must therefore
be classified separately.

The packet sequence can expose missing, duplicate, and reordered packets. It
cannot by itself establish physical capture time or capture-to-host latency.
Loop 42 must never convert sample-counter continuity into an unmeasured latency
claim.

### 2. Firmware and radio state are part of the result

The [Cyton SDK](https://docs.openbci.com/Cyton/CytonSDK/) exposes firmware,
radio health/channel, board mode, and sample-rate commands. OpenBCI recommends
Cyton firmware v3.0.0 or later, but the exact future board and dongle versions
are currently unavailable. They must be queried only after a separately
authorized stage and then bound into the result.

The nominal rate is 250 Hz. Firmware commands may expose other ADS rates, but
the official documentation says the Cyton radio cannot stream above 250 Hz.
The future packet therefore refuses a substituted rate, firmware, radio mode,
or host baud setting rather than silently adapting.

### 3. ExG becomes EEG only through verified configuration

The [official EEG setup](https://docs.openbci.com/GettingStarted/Biosensing-Setups/EEGSetup/)
uses SRB2 as the common reference, BIAS for common-mode rejection, and a
default gain of 24. It also warns that the recommended negative-input/SRB2
arrangement can make saved raw polarity appear inverted.

Consequently, an eight-channel array from this board is not automatically EEG.
The future identity record must preserve every channel's input type, gain,
SRB1, SRB2, BIAS inclusion, electrode position, reference position, and
polarity rule. Unknown geometry remains unavailable. It cannot be guessed from
channel number or selected from final performance.

The [Cyton hardware specification](https://docs.openbci.com/Cyton/CytonSpecs/)
requires 3-6 V DC battery power. Any future body-connected stage is battery
only, with charging and mains physically absent.

### 4. BrainFlow normalizes access, not evidence

[BrainFlow's supported-board documentation](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html)
defines Cyton as board ID 0 and provides synthetic and playback boards. The
playback board can regenerate timestamps or preserve old timestamps, so the
chosen mode must be frozen before comparison.

[BrainFlow's data-format documentation](https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html)
says ExG values are returned in microvolts where possible. It also warns that
timestamps are board dependent and may be generated on the PC when packets
arrive. Therefore:

- adapter timestamps are not presumed to be device capture timestamps;
- package number, adapter timestamp, local arrival time, and local retrieval
  time remain separate;
- a marker timestamp is not a physical sensor event without common-clock
  validation; and
- capture-to-arrival latency stays unavailable without an instrumented event
  visible to both device and host.

The [BrainFlow MIT license](https://brainflow.readthedocs.io/en/stable/License.html)
permits software use under its terms. It does not establish participant
consent, data ownership, device safety, or authority to publish recordings.

### 5. Local-file support is not privacy proof

The [OpenBCI GUI documentation](https://docs.openbci.com/Software/OpenBCISoftware/GUIDocs/)
says recordings can be stored locally and unfiltered, while networking can be
enabled separately. That is a useful design property, not proof that a future
process opens no sockets or writes no sensitive logs.

A future locality result requires a network-off run plus an inventory of raw
files, derived reports, settings, logs, support bundles, screenshots, serials,
temporary directories, backups, sync roots, sockets, and attempted
destinations. Wi-Fi, multicast, cloud upload, remote support, and support-log
sharing are refused in Loop 42.

The [OpenBCI privacy notice](https://docs.openbci.com/FAQ/Privacy/) governs
vendor services. It cannot substitute for a measured local runtime audit.

## Frozen Device Identity

The future result must bind 28 identity fields, including:

- device/configuration IDs, vendor, product, and hardware revision;
- redacted hashes for serial port, device serial, and host;
- board, radio, and dongle firmware;
- BrainFlow version and board ID;
- host OS, architecture, transport, and battery mode;
- board mode, rate, and per-channel gain/input/SRB1/SRB2/BIAS settings;
- electrode/reference positions and geometry availability; and
- one canonical configuration hash.

The device, firmware, adapter, host, or transport may not be substituted after
a stage starts. A failure parks that exact configuration.

## Timing And Packet Boundary

Seven timing observables remain distinct:

| Observable | Meaning | Honest latency use |
|---|---|---|
| Sample counter | Device packet sequence modulo 256 | Sequence only |
| Adapter timestamp | Board- or host-dependent adapter field | Unavailable until exact origin is proven |
| Host arrival monotonic | NeuroDecodeKit receive boundary | Host receipt intervals only |
| Host retrieval monotonic | Buffer-read boundary | Buffer/scheduler delay only |
| Marker timestamp | Host or GUI marker path | Not capture time without common-clock proof |
| Physical capture time | ADS1299 sample event | Currently unavailable |
| Render/text time | Decoder/UI boundary | Out of Loop 42 scope |

Ten anomaly classes are frozen: missing, duplicate, reordered, wrapped, and
reset counters; timestamp regression; rate mismatch; buffer overflow;
disconnect; and reconnect with a new generation. Loop 42 never silently fills,
removes, sorts, or carries state across these anomalies.

## Four Independent Future Stages

Every stage needs its own hash-bound preregistration, exact authorization, and
green authorization-only commit.

| Stage | Work | Hardware | Participant | Maximum result |
|---|---|---:|---:|---|
| A | Static adapter and candidate eligibility | No | No | Q1 descriptor compatibility |
| B | Target-free synthetic and recorded playback equivalence | No | No | Q2 playback mechanics |
| C | Battery-powered, no-contact board bench with internal test signal | Yes | No | Q3 transport mechanics only |
| D | Consented battery-only local scalp mechanics session | Yes | Yes | Q3 named device mechanics |

Stage A does not authorize B. Playback does not authorize hardware. A powered
board without a participant is not EEG. A scalp session does not authorize a
task, target text, model, decoder, or second session.

Current dependencies are not satisfied: Loop 38 has no device-lifecycle
execution, Loop 41 has no stream-to-NeuroToken execution, RW3 Stage A remains
unauthorized, and no exact consent/retention packet or device exists.

## Resource And Privacy Envelope

Current experiment files, bytes, installs, SDK imports, device operations,
streams, participant sessions, and model operations are zero.

Future ceilings, which still require stage-specific authorization, are:

```text
devices / hosts:                         1 / 1
threads / workers:                       1 / 1
Stage A/B timeout:                      60 seconds
Stage C no-contact bench:              300 seconds
Stage D consented mechanics session:   600 seconds
peak RSS:                         1,073,741,824 bytes
raw session bytes:                 67,108,864
derived artifact bytes:            33,554,432
total generated bytes:            100,663,296
network stream / cloud bytes:               0 / 0
```

These caps are far below the user's available storage envelope. Storage
capacity is not authorization to buy, connect, record, or retain a device
session.

## Measured Research Boundary

```text
public web operations:                          4
public search queries:                         12
official or primary pages opened:               9
generated experiment files / bytes:           0 / 0
dependency installs / SDK imports:             0 / 0
serial, discovery, connection, hardware ops:   0 / 0 / 0 / 0
network streams / sockets / cloud ops:         0 / 0 / 0
participant contacts / recording sessions:    0 / 0
raw / real-cache / consumed-cache reads:       0 / 0 / 0
target / model / training / decoder runs:      0 / 0 / 0 / 0
end-to-end latency measurements:                0
CPU threads / workers:                         1 / 1
```

The browser tool does not expose response bytes, process runtime, or peak RSS;
those fields remain unavailable rather than estimated.

## What Moves The Scientific Goal Next

Loop 42 removes ambiguity from a future home-device mechanics test, but it does
not create a scientific neural result. The nearest result-producing gates
remain separate:

1. **Loop 25 then Loop 26:** qualify causal preprocessing, then test one frozen
   source model against no-signal and signal controls on authorized source
   evidence.
2. **Fresh S20 EEG benchmark:** if separately authorized, run the existing
   96,090,264-byte task-matched EEG packet against its frozen prior and shuffle
   controls.
3. **Only after a real signal result:** use Loop 42 mechanics to test whether an
   exact local device preserves a task-relevant signal. Device availability
   must not dictate the scientific control design.

A positive Cyton mechanics result would establish that one local acquisition
path preserves declared packets, configuration, timing boundaries, and
privacy controls. It would still leave the central scientific question open:
does that exact device carry enough task-related neural information to improve
text prediction over language-only and peripheral controls?

## Closeout Decision

```text
loop42_planning_research_complete_openbci_cyton_8ch_usb_radio_selected_for_future_mechanics_only
```

Engineering capability added: NeuroDecodeKit now has a machine-checkable,
staged qualification design for one exact local EEG acquisition candidate.

Scientific claim not established: no SDK, device, signal, target, model,
decoder, latency, or participant operation ran, so no neural advantage, text
decoding, real-time behavior, at-home usability, portability, or clinical
result exists.
