# Real-World Practice Track Research Gate

Date: 2026-07-10

Status: Research gate passed; acquisition remains unapproved

Evidence posture: primary-source metadata review plus local filesystem metadata

## Decision

Add a parallel Real-World Practice Track identified as `RW0` through `RW9`.
It does not renumber or replace Loop 24. The track begins with local metadata
intake and replay contracts, while the causal-decoder sequence can continue
under its own consumed-seed and holdout rules.

The first proposed fresh task is one new SpanishBCBL EEG typing block, S20
session 2 block 2. It is the smallest complete unconsumed BrainVision typing
bundle in the pinned official manifest: 96,090,264 bytes across four files.
This decision is only a dry-run proposal. No signal file was downloaded or
opened, and no label file was parsed during this gate.

## Proof Boundary

- S21 MEG session 2 and the existing S7 EEG evaluation are consumed.
- Seeds 2203, 2303, and 2353 are consumed.
- Existing MEG and EEG predictive results do not show a neural advantage over
  their no-signal priors.
- No public portable-device, live, real-time, unseen-person, arbitrary-thought,
  or clinical result exists in this repository.
- A dataset or device registry entry is metadata evidence, not compatibility
  proof or download authorization.

## Research Method

The pass used official dataset pages, data descriptors, official adapter
documentation, and vendor/developer specifications current on 2026-07-10.
Unknown values remain `null` in the registries with an explicit reason. No
secondary blog or retailer specification is used as the sole support for a
compatibility claim.

Local inventory was limited to filenames, sizes, repository metadata, and
saved aggregate reports. It did not parse raw signal payloads, consumed NPZ
arrays, or target logs.

```text
network downloads:       0
raw signal reads:        0
consumed cache reads:    0
model runs:              0
training runs:           0
new real-data bytes:     0
research runtime/RSS:    not isolated; unavailable
```

The missing isolated runtime/RSS measurement is an explicit warning. The later
metadata-intake command must measure both.

## Local Inventory

| Local evidence | Bytes | Status | Allowed use |
|---|---:|---|---|
| S21 session-1 MEG raw and caches | approximately 2.3 GiB raw | consumed/observed | Existing saved evidence and permitted train-only rows under their original protocols |
| S21 session-2 MEG raw and caches | approximately 2.4 GiB raw | consumed evaluation | Aggregate saved report only; no tuning or fresh evaluation |
| S7 session-2 block-1 EEG BrainVision bundle | 94,842,381 | consumed evaluation | Aggregate saved report only; do not reopen raw or cache for selection |
| Other SpanishBCBL MAT logs | small | signal partner absent | Filename/size inventory only; do not parse targets during research |
| S20 session-2 block-2 MAT log | 204,940 | locally present, unopened in this gate | Reuse only after acquisition approval and protocol freeze |

There is no unconsumed task-compatible raw EEG signal locally. The pinned
manifest contains 731 files totaling 280,382,552,015 known bytes; its EEG
subtree is 413 files and 12,790,560,040 bytes. Only the exact proposed bundle
is in scope for a future approval.

Current disk snapshot:

```text
filesystem capacity: 460 GiB
used:                393 GiB
available:            11 GiB
data directory:      4.7 GiB
cache directory:     177 MiB
```

The proposed bundle is small relative to current headroom, but the machine is
98% full. A later approved run must enforce the 128 MiB acquisition ceiling,
16 MiB generated-artifact ceiling, one worker, and one CPU thread. It must not
expand to another subject or create duplicate caches automatically.

## Evidence Cohorts

The complete field-level matrix is
`registries/datasets.v0.json`. These cohorts answer different questions:

| Cohort | Registered sources | Valid first-order question | Invalid comparison |
|---|---|---|---|
| Prompted typing | SpanishBCBL EEG/MEG | Can a frozen event or sequence pipeline use neural activity above a no-signal control while a person types a memorized prompt? | Do not merge EEG and MEG or reuse consumed S21/S7 holdouts. |
| Inner/imagined speech | OpenNeuro ds003626, Kara One | Can a small fixed prompted class be distinguished under subject/condition controls? | Four commands or eleven phonological units are not open-vocabulary text. |
| Natural reading | ZuCo 1.0 | Can EEG and gaze be aligned during reading, and what survives eye-only ablation? | Displayed text is a stimulus, not decoded language production. |
| P300 | MOABB BI2015a | Can event timing and imbalanced ERP classification be reproduced? | P300 symbol selection is not natural typing. |
| SSVEP | MOABB Lee2019 SSVEP | Can frequency-domain signal and replay handling be reproduced? | Visual frequency classification is not language decoding. |
| Motor imagery | BNCI2014-001, PhysioNet EEGMMIDB | Can EDF/GDF/MAT intake and session-aware classification be reproduced? | Motor imagery does not qualify speech or typing. |

No second public EEG dataset with the same prompted-sentence typing and
keystroke-label contract as SpanishBCBL was verified. The honest registry gap
is preferable to relabeling a P300 speller or reading task as equivalent.

## Dataset Decision

SpanishBCBL S20 session 2 block 2 is preferred because it:

1. Matches the existing BrainVision, MAT-trigger, event-window, and key-label
   contracts.
2. Is a different nominal participant from consumed S7 and S21 evidence.
3. Fits under a 128 MiB acquisition cap.
4. Supports a target-independent 44/10/10 trial split before labels are used
   for fitting.
5. Allows the same transparent nearest-centroid baseline, train-only prior,
   and signal-shuffle control as the previous EEG bridge.

It is not authorized yet. Exact files, caps, split, controls, metrics, failure
rules, and approval wording are frozen in
`docs/FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md` and
`registries/first_fresh_eeg_benchmark.v0.json`.

PhysioNet EEGMMIDB is the smallest alternate qualification source: one
two-minute run is about 2.5 MB. It is not selected because it would validate a
motor-imagery/EDF path rather than the task-matched typing claim.

## Device Decision

The field-level device matrix is `registries/devices.v0.json`.

- OpenBCI Cyton/Ganglion/Galea, Muse 2, g.tec Unicorn, g.Nautilus, and
  Neurosity Crown can provide EEG when configured and validated correctly.
- BrainFlow is the preferred first board-neutral adapter because it exposes
  real, playback, streaming, and synthetic boards through one optional API.
- LSL is the preferred multimodal transport candidate, but its clock offsets,
  timestamp correction, packet loss, and XDF import path must be measured.
- AirPods, Apple Watch, Vision Pro, Quest, and Meta Neural Band may provide
  useful audio, cardiac, gaze, hand, motion, or muscle-intent signals. None is
  an EEG device.
- Meta Neural Band is wrist surface EMG. Its name does not make it brain
  activity, and no public raw-sEMG API was verified.

No live device is qualified in NeuroDecodeKit. Qualification requires offline
replay equivalence, timestamp and packet-loss audits, explicit consent and
retention behavior, then a task-appropriate signal control.

## File And Repository Compatibility

Official MNE readers cover BrainVision, EDF/EDF+, BDF, EEGLAB, and FIF. BIDS
defines EEG sidecars, channels, electrode coordinates, and `events.tsv`; MNE-
BIDS can load supported BIDS recordings. These are adapter capabilities, not
proof that an arbitrary file has valid channel types, geometry, reference,
units, events, or labels.

The first implementation slice is therefore compatibility level 0 only:
recognize metadata and companions without loading signal arrays. Signal reads,
quality metrics, plots, and optional MNE imports belong to later gates.

## Primary Sources

Datasets:

- https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
- https://openneuro.org/datasets/ds003626/versions/2.1.2
- https://www.nature.com/articles/s41597-022-01147-2
- https://ww2.nemar.org/
- https://www.nature.com/articles/sdata2018291
- https://osf.io/q3zws/
- https://www.cs.toronto.edu/~complingweb/data/karaOne/karaOne.html
- https://moabb.neurotechx.com/docs/generated/moabb.datasets.BI2015a.html
- https://moabb.neurotechx.com/docs/generated/moabb.datasets.Lee2019_SSVEP.html
- https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_001.html
- https://physionet.org/content/eegmmidb/1.0.0/

Formats and transports:

- https://mne.tools/stable/api/reading_raw_data.html
- https://mne.tools/stable/auto_tutorials/io/20_reading_eeg_data.html
- https://mne.tools/mne-bids/stable/use.html
- https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html
- https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/events.html
- https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
- https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html
- https://github.com/sccn/labstreaminglayer
- https://labstreaminglayer.readthedocs.io/info/time_synchronization.html

Device sources are recorded per entry in `registries/devices.v0.json`.

## Gate Result

`RW0` passes as a research and planning milestone. It authorizes a bounded,
synthetic-fixture metadata-intake implementation. It does not authorize the
S20 download, signal reading, model training, or a predictive benchmark.
