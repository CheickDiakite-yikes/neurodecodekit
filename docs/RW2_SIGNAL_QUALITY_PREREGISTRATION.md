# RW2 Bounded Signal Readability And Quality Preregistration

Date: 2026-07-10

Status: **Frozen before implementation**

Contract: `registries/signal_quality_contract.v0.json`

Registration commit: `eacb231`

Proof posture: primary-source-informed protocol; no signal result exists yet

Implementation became authorized only after commit `eacb231` was pushed. That
authorization is limited to deterministic synthetic fixtures and the exact
contract below; it does not authorize a real recording, S20, or consumed data.

## Objective

Implement the smallest optional-neuro path that can prove, on deterministic
synthetic files, that a recognized recording is lazily readable within strict
sample/memory/output limits and that its channels, timing, units, geometry
availability, annotation timing, and descriptive quality statistics can be
reported without mutating or cleaning the source.

RW2 is an input-qualification gate toward a usable local Brain2Qwerty-style
system. Reliable at-home decoding is impossible if units, references, timing,
channel identity, geometry, artifacts, and resource costs are implicit. This
gate makes those fields inspectable. It is not a decoder experiment.

## Frozen Scope

### Included

- Optional MNE imports inside the RW2 command only.
- Synthetic BrainVision, EDF/EDF+, BDF, EEGLAB external-FDT, FIF, and BIDS
  fixtures.
- Lazy header opening with explicit reader arguments.
- At most three deterministic bounded signal windows.
- Exact channel/type/unit/timing/geometry-availability metadata.
- Aggregate annotation timing with descriptions redacted.
- Descriptive time-domain and Welch PSD statistics.
- Structural warnings and explicit unavailable/profile-required warnings.
- Deterministic JSON/Markdown plus a measured audit sidecar.
- Strict load/validation CLI and dependency/refusal tests.

### Excluded

- Every real recording and cache, including S7 and both S21 sessions.
- The unapproved S20 packet.
- MNE-BIDS installation or `read_raw_bids` execution.
- Full-recording preload, cache creation, waveform export, or signal upload.
- Filtering, notch filtering, resampling, rereferencing, projection,
  compensation changes, SSS/tSSS, interpolation, ICA, clipping, scaling, or
  normalization.
- Automatic channel deletion, annotation installation, or `info['bads']`
  mutation.
- Event descriptions, target text, labels, predictions, CER/WER, or models.
- Live devices, replay equivalence, end-to-end latency, GUI work, or hardware
  qualification.

## Compatibility Levels

RW2 implementation can change compatibility only for the exact synthetic item
and exact reader configuration:

| Level | Pass rule |
|---:|---|
| 0 | Existing RW1 report validates and binds the exact source manifest. |
| 1 | Explicit reader opens with `preload=False`; one or more bounded windows return expected dimensions, finite timestamps, declared SI units, and exact fixture values under the sample cap. |
| 2 | Channel names/types/order, sampling rate, duration, sample indices/times, annotation timing status, reference/filter state, geometry availability/hash, and source bad-channel state match the fixture contract. |
| 3-6 | Always unavailable in RW2. Task, model, benchmark, and live-source qualification require later gates. |

Events need not exist to pass level 2. Their status must be validated as one of
`present_aggregate_only`, `absent_by_fixture_contract`, or
`present_sidecar_not_authorized`. An uninspected or ambiguous event state
cannot pass level 2.

## Frozen Reader Matrix

| Family | Explicit reader/configuration | Synthetic target | Hard refusal |
|---|---|---:|---|
| BrainVision | `read_raw_brainvision(eog=(), misc=(), scale=1.0, ignore_marker_types=False, preload=False, verbose='ERROR')` | Level 2 | Missing/unsafe companions, unexpected preload, noncontinuous source. |
| EDF/EDF+ | `read_raw_edf(eog=None, misc=None, stim_channel=None, exclude=(), infer_types=False, include=None, preload=False, units=None, encoding='utf8', exclude_after_unique=False, verbose='ERROR')` | Level 2 only when one source rate is proven; otherwise level 1 | Mixed/unknown source rates at level 2, implicit channel exclusion, unexpected preload. |
| BDF | Same frozen arguments through `read_raw_bdf` | Level 2 only when one source rate is proven; otherwise level 1 | Same as EDF plus malformed status/annotation handling. |
| EEGLAB | `read_raw_eeglab(eog=(), preload=False, uint16_codec=None, montage_units='auto', verbose='ERROR')` | Level 2 for continuous external `.fdt` only | Embedded signal matrix, epoched `.set`, ALLEEG, old `.dat`, missing `.fdt`, unexpected preload. |
| FIF | `read_raw_fif(allow_maxshield=False, preload=False, on_split_missing='raise', verbose='ERROR')` | Level 2 | Missing split, MaxShield requirement, unexpected preload. |
| BIDS | RW1 resolver selects exactly one raw item; dispatch to its direct reader. No `read_raw_bids`. | Level 2 only if events are absent by fixture contract or aggregate timing comes from the raw container | Ambiguous raw item, event sidecar requiring content access, inherited sidecar ambiguity, symlink, direct reader refusal. |

The implementation must use these named readers. A generic auto-reader is not
allowed because it obscures format-specific arguments and warnings.

## Bounded Window Selection

The reader may materialize at most `4,194,304` channel-sample values, equal to
32 MiB at the expected float64 return dtype.

1. Select every supported data channel, including channels already declared
   bad, up to 512 channels. Keep EEG, MEG magnetometer, MEG gradiometer, EOG,
   ECG, EMG, and other modalities in separate groups.
2. Never select STIM, system, or miscellaneous channels as brain signal.
   Report them separately by type and count.
3. Propose three 4-second windows centered at 5%, 50%, and 95% of recording
   duration.
4. Clip each window to valid sample indices, deduplicate overlaps, and preserve
   chronological order.
5. If the proposal exceeds the sample-value cap, shorten every window equally
   using integer sample arithmetic until the total fits.
6. If fewer than 128 samples per window remain, level 1 is refused as too small
   for this quality contract.
7. Call `get_data` separately for each window and channel-type group with exact
   `start`, `stop`, `return_times=True`, and `units=None`.
8. Hash canonical little-endian float64 values, channel order, and timestamps.
   Do not persist values.

The report must distinguish requested sample values, returned sample values,
materialized array bytes, declared source bytes, and physical storage bytes
read. Physical storage bytes are `unavailable` unless a future validated I/O
instrument can measure them; they must not be inferred from array size.

## Metadata Contract

For every input, report:

- schema/contract versions and hashes;
- RW1 item/source-manifest/report hashes;
- direct reader name, complete explicit arguments, dependency versions, and
  reader warnings;
- source family, modality, device declaration, and relative paths;
- channel count/order/names/types/source bads and duplicate-name status;
- sampling rate, sample count, duration, first sample, and exact selected
  window indices/timestamps;
- MNE SI unit per channel type and source-unit availability;
- source high-pass/low-pass, line frequency, projectors, compensation grade,
  custom reference status, and every unavailable field;
- finite channel-location count, coordinate frame, geometry availability, and
  a geometry payload hash without exact coordinates;
- annotation count, unique-description count, onset/duration summaries,
  channel-specific count, and original-time presence without descriptions or
  timestamps;
- all descriptive quality metrics, warning profiles, caps, runtime/RSS/output
  measurements, and access counters;
- causal status `offline_noncausal_descriptive_audit` and
  `end_to_end_latency_measured=false`.

## Privacy Contract

Reports omit absolute paths, participant rows, demographics, measurement and
acquisition timestamps, subject-info payloads, experimenter/project/free-text
descriptions, device serial numbers, event/annotation descriptions and extras,
BIDS trial columns, free-text channel status descriptions, exact electrode or
head-shape coordinates, and waveform samples.

Presence booleans, aggregate counts, coordinate-frame names, channel names,
types, units, and hashes are allowed. Reports remain sensitive local files.
Network calls are zero.

## No-Mutation Contract

Before and after metrics, hash or serialize:

- selected window payload;
- channel names/types/order;
- `info['bads']`;
- annotations onsets/durations/descriptions in memory;
- projector activation/state;
- custom reference and compensation state;
- sampling rate and sample count;
- geometry payload.

Every before/after identity must match. Annotation descriptions may be hashed
inside the process for mutation checking but cannot be written to artifacts.
No method with an in-place data or Info effect is allowed.

## Descriptive Time-Domain Metrics

Compute per channel and selected window in SI units:

- returned sample count;
- finite fraction;
- exact-zero fraction;
- adjacent-equal fraction;
- minimum, 1st percentile, median, 99th percentile, and maximum;
- median absolute deviation around the median;
- centered RMS;
- peak-to-peak amplitude;
- maximum absolute first difference.

Aggregate each metric with count, minimum, median, maximum, and unavailable
count by channel type. Do not emit raw arrays or per-sample values.

## Frozen Welch PSD

For each channel/window with at least 128 samples:

- call `mne.time_frequency.psd_array_welch` on the already bounded array;
- `fmin=0.5`;
- `fmax=min(100.0, sfreq / 2.0)`;
- `n_per_seg=min(round(2.0 * sfreq), n_window_samples)`;
- `n_fft=n_per_seg`;
- `n_overlap=floor(n_per_seg / 2)`;
- `window='hann'`;
- `average='median'`;
- `remove_dc=True`;
- `n_jobs=1`;
- `output='power'`.

Report absolute and relative power for `[0.5,4)`, `[4,8)`, `[8,13)`,
`[13,30)`, and `[30,45]` Hz where resolvable. Report 50 and 60 Hz
line-to-sideband ratios using the center band `line +/- 1 Hz` and sidebands
`[line-5,line-2]` plus `[line+2,line+5]`. A ratio is unavailable when Nyquist
or bin coverage is insufficient.

No default ratio is a pass/fail threshold.

## Warning Semantics

### Structural Warnings

These are deterministic facts, not diagnoses:

- nonfinite samples present;
- exact-constant channel/window;
- duplicate channel names;
- nonmonotonic or wrong-length timestamps;
- unsupported/unknown units;
- reference unknown;
- geometry unavailable or partially finite;
- source bad-channel declarations present;
- source filters or projectors present;
- mixed-rate EDF/BDF unresolved;
- reader unexpectedly preloaded;
- sample/resource/output cap reached;
- before/after mutation mismatch.

### Advisory Candidates

When at least eight channels of one type exist, report a channel whose log
centered-RMS robust z-score exceeds 6 as
`relative_rms_outlier_candidate`. This is not a bad-channel declaration.

Amplitude, clipping, flat-difference, and line-noise threshold warnings are
`unavailable_profile_required` in the generic profile. The first implementation
must not call `annotate_amplitude`. A future profile must freeze physical SI
thresholds, device/reference/task scope, and validation data before it can add
advisory warnings.

No warning may delete, interpolate, filter, rereference, or mark a channel bad.

## Synthetic Fixtures

The later implementation must create fresh deterministic fixtures without
target text:

| Fixture | Purpose |
|---|---|
| Clean multitype continuous | Exact channels, units, timing, bounded values, geometry, no structural warning. |
| Exact flat channel | One exact-constant warning; no automatic mutation. |
| Nonfinite samples | Finite-fraction warning and deterministic unavailable metrics. |
| Relative RMS outlier | One advisory candidate among at least eight same-type channels. |
| 50/60 Hz components | PSD peaks and line ratios within one frequency bin; no generic bad declaration. |
| Missing geometry/reference | Explicit unavailable warnings without reader failure. |
| Safe nonsemantic annotations | Aggregate timing/count only; descriptions absent from every artifact. |
| Malformed/cap fixtures | Symlink/root/companion/split/embedded-EEGLAB/preload/sample/output refusals. |

Export the clean and injected variants to every supported format where the
toolchain permits. Each format fixture must preserve a source-independent
canonical signal payload so reader equivalence can be tested.

## Access Counters

Every run records:

- metadata/header files read;
- annotation metadata files read;
- raw reader opens;
- bounded signal read calls;
- requested and returned sample values;
- materialized signal array bytes;
- physical storage bytes read or explicit unavailable status;
- real-data reads;
- consumed-cache reads;
- target/label values emitted or used;
- model runs;
- training runs;
- network calls;
- output bytes.

For the synthetic gate, real-data, consumed-cache, target/label, model,
training, and network counters must all be zero.

## Resource Caps

| Resource | Hard cap |
|---|---:|
| Workers / numerical threads | 1 / 1 |
| Source files / directory depth | 256 / 8 |
| Declared source bytes | 4 GiB |
| Channels | 512 |
| Selected windows | 3 |
| Requested channel-sample values | 4,194,304 |
| Materialized float64 signal arrays | 32 MiB |
| Runtime | 30 seconds |
| Process peak RSS | 1 GiB |
| Generated artifacts | 4 MiB |
| New signal cache bytes | 0 |
| Network calls | 0 |

Current disk is 98% full with about 8.9 GiB available. The synthetic fixture
set plus reports must stay below 16 MiB even though the per-run artifact cap is
4 MiB. No duplicate real recording or cache is allowed.

## Acceptance Gates

RW2 implementation passes only if all are true:

1. The base install imports and all base tests pass without MNE/NumPy/SciPy.
2. Optional imports are lazy and the missing-extra error is actionable.
3. All six format families produce the registered synthetic compatibility
   result or their exact preregistered refusal.
4. No reader unexpectedly preloads; embedded EEGLAB is refused before signal
   access.
5. Canonical selected values match fixture truth within `1e-12` absolute
   float64 tolerance after declared unit scaling.
6. Channel order/type/unit, sfreq, sample indices/times, duration, event status,
   geometry availability/hash, reference/filter/projector state, and source
   bads match fixture truth.
7. PSD injected peaks are recovered within one realized frequency bin and all
   power/ratio formulas replay deterministically.
8. Every injected structural warning appears; the clean fixture has none;
   profile-required warnings remain unavailable rather than guessed.
9. Source data, annotations, bads, projectors, reference, compensation, sfreq,
   and geometry are unchanged before/after.
10. Event descriptions, timestamps, participant data, serials, exact geometry,
    and waveform values do not appear in artifacts.
11. Deterministic JSON/Markdown replay byte-for-byte; measured audit hashes and
    byte counts validate; tampering and collisions are refused.
12. Every cap and access counter passes with one thread and no signal cache.
13. Focused tests, complete unittest and pytest suites, Ruff, compileall, CLI
    help, `git diff --check`, and one bounded synthetic roundtrip pass.
14. Generated artifacts remain ignored and under their declared cap.
15. Documentation says exactly what was proven and what remains unavailable.

## Kill, Park, Proceed

- **Kill the implementation path** if any artifact exposes annotation/target
  descriptions, participant data, exact timestamps, serials, exact geometry,
  or waveform values.
- **Park a format adapter** if MNE cannot enforce bounded lazy access, hidden
  resampling/type mutation cannot be audited, or the reader requires a full
  preload. Other formats may proceed only with the parked format explicit.
- **Park all of RW2** if deterministic values, no-mutation identity, resource
  caps, or base-install isolation fail.
- **Proceed after a passing synthetic gate** only to a separately approved
  real-read packet. Do not automatically open S7, S21, or S20.

## Frozen Claim Boundary

A passing RW2 synthetic implementation would prove bounded reader mechanics,
metadata/timing identity, descriptive quality calculations, privacy redaction,
and resource behavior on generated fixtures.

It would not prove that a real recording is good, that a warning identifies an
artifact correctly, that any preprocessing improves decoding, that neural
signal beats a prior, or that Brain2Qwerty v2 works in real time or on an
at-home device.
