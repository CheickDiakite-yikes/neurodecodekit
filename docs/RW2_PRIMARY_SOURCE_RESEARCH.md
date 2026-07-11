# RW2 Primary-Source Research: Bounded Signal Readability And Quality

Date: 2026-07-10

Status: Research complete; no reader implemented and no recording opened

Proof posture: official API/specification review plus inspection of the locally
installed optional package source and signatures

## Question

What can NeuroDecodeKit safely promise when it moves from RW1 metadata-only
recognition to bounded signal readability and descriptive quality reporting?

## Local Environment

The repository still has no heavy base dependency. The existing `.venv`
contains:

- MNE-Python 1.12.1;
- NumPy 2.5.0;
- SciPy 1.18.0;
- no MNE-BIDS;
- no PyEDFlib.

The current `neuro` extra remains `mne>=1.7`, `numpy>=1.26`, and
`scipy>=1.11`. RW2 preregistration does not change it. Implementation must
either validate its exact supported range or tighten the optional extra in a
separate code commit.

## Reader Findings

### BrainVision

`mne.io.read_raw_brainvision` supports `preload=False`, explicit EOG/MISC
classification, and a scale parameter. The reader converts marker type and
description into MNE annotations, and a New Segment timestamp can populate
`info['meas_date']`. Impedance metadata may also be available on the direct
reader object. These are useful, but annotation descriptions and measurement
dates are privacy-sensitive and may contain target/task information.

RW2 implication:

- use the `.vhdr` selected and companion-validated by RW1;
- pass `eog=()`, `misc=()`, `scale=1.0`, `ignore_marker_types=False`, and
  `preload=False` explicitly;
- permit MNE to parse annotations but emit only counts and timing summaries;
- never emit marker descriptions, New Segment timestamps, or impedance values;
- record that reader calibration converts source units to MNE internal SI
  units.

Source: [MNE BrainVision reader](https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html).

### EDF And BDF

`read_raw_edf` and `read_raw_bdf` support lazy reads, but the default
`stim_channel='auto'` silently promotes channels named status or trigger.
`infer_types=True` can also rename and retype channels. EDF+ annotation
channels are converted to MNE annotations. MNE documents a more consequential
edge case: requested mixed-rate channels are upsampled to the highest loaded
sampling frequency, and sliced lazy reads can show edge artifacts.

RW2 implication:

- set `stim_channel=None`, `infer_types=False`, `exclude=()`, `include=None`,
  `units=None`, `encoding='utf8'`, and `preload=False` explicitly;
- do not silently drop channels to avoid mixed-rate behavior;
- report mixed-rate status as unavailable unless a source-header preflight can
  prove one common rate;
- cap a mixed-rate/unknown-rate file at compatibility level 1; it cannot pass
  level 2 timing validation;
- redact all annotation descriptions.

Sources: [MNE EDF reader](https://mne.tools/stable/generated/mne.io.read_raw_edf.html)
and [MNE 1.12 EDF source](https://github.com/mne-tools/mne-python/blob/maint/1.12/mne/io/edf/edf.py).

### EEGLAB

`read_raw_eeglab` supports `preload=False` and an external `.fdt` companion.
However, MNE 1.12.1 source shows two bounded-read hazards:

1. Event descriptions are read from the `.set` file into annotations during
   initialization.
2. If continuous data are embedded in the `.set`, the first requested segment
   loads and caches the complete embedded data matrix.

The reader also infers montage units when `montage_units='auto'`.

RW2 implication:

- support continuous, single-trial `.set` plus external `.fdt` only;
- refuse embedded-data `.set`, epoched EEGLAB, ALLEEG, and old `.dat` payloads;
- pass `eog=()`, `preload=False`, `uint16_codec=None`, and
  `montage_units='auto'` explicitly;
- report that geometry-unit inference occurred and require fixture validation;
- redact event descriptions and do not expose the raw EEGLAB event structure.

Sources: [MNE EEGLAB reader](https://mne.tools/stable/generated/mne.io.read_raw_eeglab.html)
and [MNE 1.12 EEGLAB source](https://github.com/mne-tools/mne-python/blob/maint/1.12/mne/io/eeglab/eeglab.py).

### FIF

`read_raw_fif` supports lazy reads and automatically follows split FIF files.
`on_split_missing='raise'` is the strict default. `allow_maxshield=False`
prevents direct use of internally compensated MaxShield data that generally
requires a separate SSS/tSSS decision.

RW2 implication:

- set `allow_maxshield=False`, `preload=False`,
  `on_split_missing='raise'`, and `verbose='ERROR'` explicitly;
- retain all source channel types and existing bad-channel declarations;
- do not apply projectors, Maxwell filtering, SSS/tSSS, compensation changes,
  or head transforms;
- report split count and compensation/projector state without modifying it.

Source: [MNE FIF Raw reader](https://mne.tools/stable/generated/mne.io.Raw.html).

### BIDS

`mne_bids.read_raw_bids` attempts to read `events.tsv` and `channels.tsv`,
populates annotations and `info['bads']`, can reorder or rename channels under
non-default mismatch modes, and may resolve FIF symlinks. MNE-BIDS 0.19.0 is
not installed locally.

RW2 implication:

- do not add or call MNE-BIDS in the first implementation;
- use the RW1 safe BIDS resolver to select exactly one raw file, then call its
  explicit direct MNE reader;
- parse only allowlisted non-free-text sidecar fields in a later bounded
  adapter; do not read `events.tsv`, `participants.tsv`, or `scans.tsv`;
- do not import source bad-channel status into `raw.info['bads']` in RW2;
- a BIDS recording with an event sidecar remains level 1 unless event access is
  separately authorized.

Source: [MNE-BIDS read_raw_bids](https://mne.tools/mne-bids/stable/generated/mne_bids.read_raw_bids.html).

## Units And Bounded Data Access

`Raw.get_data(start=..., stop=..., units=None)` returns channel-type-specific
SI units. It can select channels and an exact sample range without preloading
the complete recording. It includes channels already listed in
`info['bads']` when they are explicitly selected.

RW2 implication:

- group channels by type before computing metrics;
- retain SI units: volts for EEG/EOG/ECG/EMG, tesla for magnetometers, and
  tesla per meter for gradiometers;
- report reader calibration and source unit metadata separately;
- materialize float64 values only inside a global sample-value/byte cap;
- record requested start/stop indices and returned timestamps;
- never persist waveform arrays in an RW2 report.

Source: [MNE Raw.get_data](https://mne.tools/stable/generated/mne.io.Raw.html).

## Spectral Estimation

`Raw.compute_psd(method='welch')` supports explicit frequency bounds,
projection behavior, DC removal, annotation rejection, one-thread execution,
and Welch parameters. Its defaults depend on the available sample count, so a
reproducible contract must set every material parameter.

RW2 freezes per-window `psd_array_welch` with:

- 0.5 Hz to `min(100 Hz, Nyquist)`;
- 2-second segments;
- no zero padding (`n_fft == n_per_seg`);
- 50% overlap;
- Hann window;
- median segment aggregation;
- DC removal;
- one job;
- no projection, filtering, notch, resampling, rereferencing, interpolation,
  or annotation-based omission.

PSD is descriptive. It reports standard bands and 50/60 Hz line-to-sideband
ratios. It does not declare a channel bad without a separately registered
device/profile threshold.

Source: [MNE Raw.compute_psd](https://mne.tools/stable/generated/mne.io.Raw.html).

## Amplitude And Bad-Channel Semantics

MNE's `annotate_amplitude` requires explicit peak and flat thresholds. It can
return annotations and bad-channel candidates, but does not mutate the Raw
object unless the caller explicitly installs those results. Its behavior is
based on consecutive-sample differences rather than a general windowed
peak-to-peak test.

PREP and Autoreject both demonstrate that useful automated cleaning depends on
algorithmic assumptions, robust reference or cross-validation, and validation
across datasets. They are preprocessing/repair methods, not universal quality
truth. COBIDAS-MEEG further emphasizes that preprocessing order and exact
parameters affect the resulting signal and must be reported.

RW2 implication:

- the generic profile computes descriptive finite, exact-constant, amplitude,
  first-difference, RMS, robust-spread, and PSD statistics only;
- it emits structural warnings for facts such as nonfinite values, duplicate
  names, nonmonotonic timestamps, or exact-constant channels;
- it does not call `annotate_amplitude`, interpolate, rereference, filter,
  resample, mutate annotations, or add channels to `info['bads']`;
- amplitude, clipping, and line-noise thresholds remain explicitly
  unavailable until a device/task profile is preregistered;
- any future profile warning remains advisory and cannot delete data.

Sources:

- [MNE annotate_amplitude](https://mne.tools/stable/generated/mne.preprocessing.annotate_amplitude.html)
- [PREP pipeline](https://pmc.ncbi.nlm.nih.gov/articles/PMC4471356/)
- [Autoreject](https://pmc.ncbi.nlm.nih.gov/articles/PMC7243972/)
- [COBIDAS-MEEG](https://www.nature.com/articles/s41593-020-00709-0)

## BIDS Metadata And Privacy

BIDS channel tables may contain names, types, units, per-channel sampling
rates, references, filters, source quality status, and free-text status
descriptions. EEG/MEG sidecars describe sampling, power-line frequency,
reference, filters, coordinate systems, and acquisition details. Event tables
can contain stimulus, response, file, and arbitrary additional columns.

RW2 therefore defaults to local-only output and omits:

- absolute paths;
- participant tables and demographics;
- measurement/acquisition timestamps;
- subject information and experimenter/project descriptions;
- device serial numbers;
- annotation descriptions, extras, and original time;
- BIDS event rows and trial columns;
- free-text channel status descriptions;
- exact sensor coordinates and head-shape points.

The report may state whether each field exists. It may emit channel names,
types, units, counts, coordinate-frame name, finite-geometry count, and a
geometry hash because these are needed for local compatibility. Reports remain
sensitive local artifacts and are never uploaded.

Sources:

- [BIDS EEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)
- [BIDS MEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetoencephalography.html)
- [BIDS events specification](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/events.html)
- [MNE-BIDS anonymization](https://mne.tools/mne-bids/stable/generated/mne_bids.anonymize_dataset.html)

## Relevance To Brain2Qwerty v2

The official v2 report describes an offline MEG pipeline with 0.5-45 Hz
bandpass filtering, a 50 Hz notch, downsampling to 100 Hz, per-recording robust
scaling, and clipping at five robust standard deviations. These operations are
not neutral quality inspection and are not causal by default.

RW2 records this as a comparison profile only. It does not apply the v2
preprocessing chain, does not estimate scaler statistics, and does not call an
offline result real-time. A future causal preprocessing loop must separately
replace or validate every future-aware operation.

Source: [Brain2Qwerty v2 report](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf).

## Research Decision

Proceed to a separately committed RW2 synthetic implementation only under the
machine-readable contract in `registries/signal_quality_contract.v0.json` and
the preregistration in `docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`.

No real recording, S20 file, consumed S7/S21 evidence, target log, model,
training process, device, or network resource was opened in this research
pass. The research adds no compatibility level, signal result, quality result,
decoder result, or hardware claim.
