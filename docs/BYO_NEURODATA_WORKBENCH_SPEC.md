# Bring Your Own Neurodata Workbench Specification

Version: 0.1

Status: Product and safety contract; only metadata intake is authorized

Default posture: local-only, explicit refusal, no silent upload

## Product Goal

Provide one local workbench for recordings a user already possesses, public
dataset slices they explicitly approve, recorded device replays, and future
live sources. The workbench should make compatibility and failure reasons more
visible than model output.

This is an operational tool, not a marketing page and not a general
brain-to-text promise.

## First Screen

The first screen is the usable workspace and exposes five actions:

1. **Open local recording** - choose a supported recording or bundle.
2. **Open BIDS dataset** - choose a BIDS root and then a subject/session/run.
3. **Connect live device** - disabled until an optional adapter passes its
   device-specific qualification gate.
4. **Replay sample recording** - use a synthetic fixture or an authorized
   local recording through the same source contract as live acquisition.
5. **View previous benchmark reports** - open local JSON/Markdown report cards
   without reading raw data.

The primary workspace has unframed tabs for Overview, Channels, Waveform, PSD,
Events, Preprocessing, Compatibility, Benchmark, and Provenance. A persistent
proof strip shows modality, task cohort, compatibility level, authorization,
and the strongest allowed claim.

## Compatibility Levels

| Level | Name | Required evidence |
|---:|---|---|
| 0 | Metadata recognized | Safe path, recognized format, companion files, declared bytes, and metadata report. No signal read. |
| 1 | Signal readable | Optional reader opens headers and bounded samples with units and dimensions. |
| 2 | Channels, timing, events validated | Channel names/types, rate, duration, geometry availability, event clock, and companion consistency pass. |
| 3 | Registered task compatible | Dataset/task registry entry matches required labels and event semantics. |
| 4 | Model geometry/preprocessing compatible | Frozen channel mapping, rate, causal status, reference, and preprocessing contract match. |
| 5 | Benchmark authorized | Exact split, comparators, metrics, caps, and one-time test rule are frozen and approved. |
| 6 | Live source qualified | Recorded replay and live stream are equivalent within registered timestamp, packet, payload, and latency tolerances. |

Compatibility is monotonic only within one exact recording, configuration,
task, and model. A file can be readable but not benchmarkable. The workbench
must never fabricate target text, labels, or a decoding result for an unknown
or incompatible recording.

## Initial File Families

| Family | Level-0 bundle rule | Optional level-1 adapter |
|---|---|---|
| BrainVision | One `.vhdr` plus referenced `.vmrk` and `.eeg`; names are resolved from header text after strict path validation. | `mne.io.read_raw_brainvision` |
| EDF/EDF+ | One `.edf`; annotations may be internal. | `mne.io.read_raw_edf` |
| BDF | One `.bdf`; status/annotation semantics remain device-specific. | `mne.io.read_raw_bdf` |
| EEGLAB | One `.set`; if external data are declared, one sibling `.fdt`. | `mne.io.read_raw_eeglab` |
| FIF | One `.fif` or valid split-FIFF family; split completeness must be explicit. | `mne.io.read_raw_fif` |
| BIDS EEG/MEG | Valid root metadata plus a selected recording and inherited sidecars; `events.tsv` is optional but its absence is visible. | `mne_bids.read_raw_bids` plus MNE readers |

Archives are not recording formats. `.zip`, `.tar`, `.tar.gz`, `.tgz`,
`.tar.bz2`, and similar inputs are refused by the initial workbench. Pickle and
object-bearing NumPy payloads are refused.

## Local Architecture

```text
user-selected path
  -> safe metadata scanner (base install, no signal arrays)
  -> compatibility report v0 (JSON + Markdown)
  -> optional MNE/MNE-BIDS bounded reader
  -> signal-quality contract
  -> task registry + frozen split authorization
  -> transparent baselines and controls
  -> local report-card store

recorded source -> replay adapter -> source chunks -> same inference contract
live device     -> device adapter -> source chunks -> same inference contract
```

Heavy imports remain inside optional adapter functions. The base package must
recognize metadata and explain the required extra without importing MNE,
NumPy, SciPy, BrainFlow, LSL, Torch, or Gradio.

## Metadata Contract

Every intake report records:

- schema/version, item ID, source root, relative files, sizes, and hashes where
  hashing was explicitly enabled;
- modality and device if declared, otherwise `unknown`;
- subject/session/task/run values only from safe filename/BIDS metadata;
- raw family, companions, and missing/ambiguous files;
- channel count/names/types, sampling rate, duration, reference, filters,
  units, geometry, and events as either known values or explicit unavailable
  fields;
- compatibility level and one refusal reason per failed higher level;
- local-only status, PII warning, authorization status, and claim boundary;
- scanner configuration/hash, registry version/hash, runtime, peak RSS, input
  bytes declared, bytes actually read, and output bytes;
- raw reads, real-cache reads, model runs, training runs, and network calls.

Level 0 may inspect bounded text headers and BIDS TSV/JSON sidecars. It must not
read binary signal samples.

## Signal Quality Contract

After level 1 is separately authorized, bounded signal inspection should show:

- waveform and robust amplitude summaries by channel;
- PSD with declared method, segment length, overlap, and line frequency;
- flat, clipped, disconnected, excessive-amplitude, high-line-noise, and
  missing/duplicate-channel warnings;
- event raster and inter-event timing;
- channel locations and explicit missing-geometry states;
- reference, units, source filters, resampling, and every fitted
  transformation.

Thresholds must be modality/device/configuration specific and preregistered.
A warning is not an automatic bad-channel deletion.

## Benchmark Contract

A benchmark panel remains locked below level 5. Authorization requires:

- one exact task/evidence cohort from the dataset registry;
- immutable subject/session/trial membership and split hashes;
- train-only fitted preprocessing;
- a no-signal prior for every predictive result;
- a deterministic signal-shuffle control;
- an applicable transparent neural baseline;
- CER/WER only for genuine sequence labels under a valid sequence protocol;
- runtime, RSS, stage latency, storage, raw/cache/model/training counters;
- uncertainty and a proceed/park/kill rule written before test access.

An incompatible recording produces an inspection report and refusal reasons,
not generated text.

## Replay And Live Equivalence

Recorded replay is the first live-source test. Both adapters must emit the same
versioned chunk structure:

- source ID, modality, device, channel names/types/geometry;
- source sampling rate and monotonic sample/timestamp indices;
- chunk start/end, valid samples, dropped-sample markers, and clock domain;
- causal/noncausal state and required left/right context;
- source, device configuration, preprocessing, and payload hashes.

Live qualification requires bounded differences for payload values, timestamp
ordering, chunk-schedule invariance, dropped-packet handling, state size,
compute latency, transport latency, and end-to-end latency. LSL clock
correction and BrainFlow board descriptors are recorded, never assumed.

## Multimodal Accessibility Lane

EEG, eye tracking, EOG, EMG, PPG, IMU, microphone, and hand tracking keep
separate stream IDs and modality labels. Every multimodal predictive result
requires:

1. Brain-only input.
2. Device/peripheral-only input.
3. Combined input.
4. Label-shuffle and no-signal controls.

Meta Neural Band is wrist sEMG. Vision Pro and Quest eye/hand tracking are
behavioral input. AirPods and Apple Watch provide audio, cardiac, and motion
context. These signals can make a communication system more accessible, but
their contribution cannot be attributed to EEG.

## Privacy And Security

- Processing is local by default; network calls are zero unless the user
  explicitly starts an approved acquisition.
- Neural recordings and derived features are sensitive even when de-identified.
- Reports omit absolute source paths by default and warn before exposing BIDS
  participant fields, measurement dates, free-text annotations, or device
  serial numbers.
- Resolve every selected path, reject symlink escapes, reject special files,
  and do not follow links outside the selected root.
- Reject archives, pickle payloads, executable files, malformed JSON/TSV, NUL
  bytes in text metadata, duplicate bundle roles, and companion paths that use
  absolute paths or `..` traversal.
- Never overwrite a nonempty output directory without an explicit flag.
- Never upload, call a cloud SDK, or enable device broadcast discovery during
  a metadata-only scan.

## Default Caps

| Resource | Metadata intake v0 | Later bounded signal stage |
|---|---:|---:|
| Files visited | 256 | Frozen per protocol |
| Directory depth | 8 | Frozen per protocol |
| Declared input bytes | 4 GiB | Explicit approval required above this |
| Text sidecar bytes read | 8 MiB total, 1 MiB each | Same unless protocol changes |
| Binary signal bytes read | 0 | Explicit bounded window or reader contract |
| Channels | metadata only | 512 default maximum |
| Generated artifacts | 4 MiB | 32 MiB hard maximum unless separately approved |
| CPU threads | 1 | 1 by default |
| Network calls | 0 | Explicit acquisition/device action only |

The first S20 proposal is stricter: 128 MiB acquisition and 16 MiB generated
artifacts.

## Initial Implementation Slice

`RW1` implements only level-0 metadata recognition on local synthetic
fixtures:

- recognize the six initial file families;
- validate companions and safe paths;
- emit deterministic JSON/Markdown reports with hashes, caps, counters,
  warnings, and refusal reasons;
- provide useful CLI help;
- prove that no binary signal, target, model, or network access occurs.

Waveforms, PSD, signal-quality thresholds, MNE reads, live devices, a GUI, and
predictive output are explicitly out of scope for `RW1`.

RW1 is closed with deterministic JSON/Markdown, a measured audit sidecar, 11
focused tests, and one 532-byte synthetic roundtrip. See
`docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`. Every compatibility level above 0
still requires a separate preregistration and implementation gate.
