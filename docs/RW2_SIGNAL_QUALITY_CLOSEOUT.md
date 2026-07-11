# RW2 Synthetic Signal-Quality Closeout

Date: 2026-07-10

Status: **Passed and closed at compatibility level 2 for exact synthetic
fixtures**

Proof posture: fixture-backed, target-free, optional-neuro interface validation

Implementation commit: `2796dee`

Frozen preregistration commit: `eacb231`

## Question

Can the exact optional MNE readers frozen before implementation open bounded
windows from six generated neurodata format families, preserve source identity,
calculate deterministic descriptive quality summaries, redact sensitive fields,
prove no source mutation, enforce resources, and write strict inspectable
artifacts without touching a real recording, consumed cache, target, model, or
training path?

## Result

Yes, for the exact generated fixtures and reader configurations only.

RW2 now provides:

- a strict `neurodecodekit-signal-quality` schema at version `0.1.0`;
- deterministic JSON and Markdown artifacts plus a measured audit sidecar;
- strict create, load, validation, summary, tamper, collision, and cap behavior;
- explicit direct MNE adapters for BrainVision, EDF/EDF+, BDF, continuous
  EEGLAB external-FDT, FIF, and BIDS resolved to a direct supported reader;
- deterministic three-anchor window selection with sample and array caps;
- canonical selected-payload, source-state, contract, fixture, configuration,
  source-manifest, report, Markdown, and audit hashes;
- per-channel/window descriptive time metrics;
- median Welch PSD, band powers, and 50/60 Hz line-to-sideband ratios;
- structural warnings and non-mutating relative-RMS advisory candidates;
- channel names/types, source bads, units, reference, filters, projectors,
  compensation, geometry status/hash, aggregate annotation status, and timing;
- before/after source-state and selected-payload identity;
- privacy redaction and forbidden-field validation;
- exact access counters, resources, causality, unavailable fields, and claim
  boundaries;
- four CLI commands for fixture creation, fixture inspection, signal
  inspection, and saved-report inspection.

The base module imports without importing MNE, NumPy, SciPy, MNE-BIDS, or
Torch. The optional `neuro` extra is constrained to MNE `1.12.x`, the exact
minor line used by the frozen reader arguments and fixture evidence.

## Format Matrix

| Format family | Generated fixtures | Readable | Frozen refusals | Reader boundary |
|---|---:|---:|---:|---|
| BrainVision | 7 | 7 | 0 | `mne.io.read_raw_brainvision`, explicit companions and arguments |
| EDF/EDF+ | 5 | 5 | 0 | `mne.io.read_raw_edf`, one proven source rate |
| BDF | 5 | 5 | 0 | `mne.io.read_raw_bdf`, one proven source rate |
| EEGLAB | 8 | 7 | 1 | continuous single-trial `.set` plus external `.fdt` only |
| FIF | 7 | 7 | 0 | `mne.io.read_raw_fif`, no MaxShield, strict split behavior |
| BIDS | 8 | 7 | 1 | RW1 safe resolver, then exact direct MNE reader; no MNE-BIDS |
| **Total** | **40** | **38** | **2** | all readers remain `preload=False` after open |

The two expected refusals are:

- `eeglab_embedded_or_epoched_source_refused`;
- `bids_event_sidecar_requires_content_access`.

Four combinations are documented as ungenerated rather than silently weakened:

- EDF and BDF cannot preserve the nonfinite-sample fixture through their
  integer recording representation;
- the minimal EDF/BDF writer does not fabricate an EDF+/BDF+ annotation
  channel for the safe-annotation fixture.

## Fixture Families

The deterministic 20-second, 128 Hz fixture source has nine selected channels:

```text
Fp1 Fp2 F3 F4 C3 C4 P3 P4 EOG1
```

The generated variants are:

1. clean multitype continuous signal;
2. exact flat channel;
3. nonfinite samples;
4. relative RMS outlier;
5. injected 50/60 Hz line components;
6. missing geometry and reference;
7. safe nonsemantic annotations;
8. malformed and cap refusals.

No target text or labels are created. The complete ignored fixture tree has 207
files totaling 3,937,717 bytes, below the frozen 16 MiB aggregate cap. It
contains recording-format payloads and RW1 binding artifacts only; it is not
committed.

## Descriptive Metrics

For each selected channel and window, RW2 reports:

- sample count;
- finite fraction;
- exact-zero fraction;
- adjacent-equal fraction;
- minimum and maximum;
- 1st, 50th, and 99th percentiles;
- median absolute deviation;
- centered RMS;
- peak-to-peak amplitude;
- maximum absolute first difference.

Welch PSD uses the frozen MNE implementation and parameters:

- median segment averaging;
- Hann windows;
- two-second segments when enough samples exist;
- 50% overlap;
- DC removal;
- 0.5 Hz to `min(100 Hz, Nyquist)`;
- delta, theta, alpha, beta, and low-gamma band summaries;
- descriptive 50 and 60 Hz line-to-sideband ratios.

No generic amplitude, clipping, flat-difference, or line-noise pass/fail
threshold is invented. Those fields remain explicitly unavailable until a
separately validated modality/device profile exists.

Warnings do not mark channels bad, drop samples, or clean the source.

## No-Mutation And Privacy

The successful FIF roundtrip records identical before/after hashes:

```text
selected payload:
8c77b46d3d2f18de4fb93d0c60643cebfc95f9195802150ba21367b278c83671

source state:
458748c58263442449ad63a7fd7e5422e19be0aeea8d40c59d80f71e34d61025
```

No filter, notch, resample, rereference, projection application, compensation
change, MaxShield/SSS, bad-channel interpolation, ICA, clipping, scaling,
annotation mutation, or bad-list mutation is performed.

Artifacts emit no:

- absolute paths;
- participant rows or subject-info payload;
- measurement/acquisition timestamps;
- event or annotation descriptions;
- exact individual event timestamps;
- device serial numbers;
- exact sensor/head-shape coordinates;
- waveform values;
- target text, labels, predictions, or decoded text.

Channel names, types, SI units, aggregate event counts, coordinate-frame names,
availability states, and hashes remain visible because they are required for
an inspectable interface.

## Measured CLI Roundtrip

The closeout reused the existing ignored fixture set to avoid another 4 MiB
copy on a nearly full volume.

Command:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
neurodecode inspect-signal-quality \
  --path .codex_work/rw2_impl/generated4/fixtures/clean_multitype_continuous__fif/source/recording_raw.fif \
  --intake-report .codex_work/rw2_impl/generated4/fixtures/clean_multitype_continuous__fif/intake/intake.json \
  --fixture-manifest .codex_work/rw2_impl/generated4/signal_quality_fixtures.json \
  --contract registries/signal_quality_contract.v0.json \
  --out-dir .codex_work/rw2_closeout/quality
```

Measured result:

| Measurement | Value |
|---|---:|
| Format / fixture | FIF / `clean_multitype_continuous__fif` |
| Declared source bytes | 94,292 |
| Sampling rate | 128 Hz |
| Duration / source samples | 20.0 sec / 2,560 |
| Selected channels | 9 |
| Selected windows | 3 |
| Window sample counts | 384, 512, 384 |
| Requested / returned values | 11,520 / 11,520 |
| Bounded signal read calls | 6 |
| Materialized float64 array bytes | 92,160 |
| Deterministic JSON bytes | 72,818 |
| Deterministic Markdown bytes | 1,734 |
| Audit sidecar bytes | 2,040 |
| Combined output bytes | 76,592 |
| Internal runtime | 3.839168 sec |
| Internal peak RSS | 150,749,184 bytes |
| External wall time | 4.15 sec |
| External maximum RSS | 150,978,560 bytes |
| Structural warnings | 0 |
| Advisory candidates | 0 |
| New signal-cache bytes | 0 |
| Output cap | 4,194,304 bytes |
| Runtime / RSS caps | 30 sec / 1,073,741,824 bytes |
| Cap result | passed |

The first closeout command intentionally supplied a broader `--root` than the
RW1 report had bound. The command refused with:

```text
Selected source does not match the RW1 report.
```

It stopped before a successful raw-reader open and created no report artifact.
The successful command omitted that override and used the exact fixture-bound
source root. This is evidence that root/provenance identity cannot be widened
silently.

## Access Accounting

Successful roundtrip:

```text
metadata header files read:                 1
annotation metadata files read:             0
raw reader opens:                            1
bounded signal read calls:                   6
requested/returned sample values:            11,520 / 11,520
materialized signal array bytes:             92,160
physical storage bytes read:                 unavailable
real data reads:                             0
consumed cache reads:                        0
target/label values emitted or used:         0
model runs:                                  0
training runs:                               0
network calls:                               0
```

Physical storage bytes read remain unavailable because validated OS/MNE I/O
instrumentation was deliberately not invented. Declared source bytes,
requested values, returned values, read-call counts, and materialized array
bytes are measured separately.

## Causality And Unavailable Fields

Producer status:

```text
offline noncausal descriptive audit
producer causal: false
required left context: unavailable
required right context: unavailable
end-to-end latency measured: false
```

Every unavailable field in the measured report:

- benchmark authorization;
- end-to-end latency;
- generic amplitude threshold;
- generic clipping threshold;
- generic flat-difference threshold;
- generic line-noise-ratio threshold;
- live-source qualification;
- model compatibility;
- physical storage bytes read;
- real-recording quality;
- task compatibility.

Warnings emitted by the clean fixture report:

- neural recordings and derived features are sensitive;
- no prediction or decoding result;
- quality metrics are descriptive, not diagnostic;
- synthetic fixture only, with no real recording authorized.

## Verification

Focused RW2 suite:

```text
9 tests passed
38 readable fixtures exercised
2 frozen refusals exercised
base import isolation passed
deterministic replay passed
malformed/tamper/privacy/collision/cap tests passed
CLI create/inspect/collision roundtrip passed
```

Complete optional-neuro/ML environment:

```text
unittest: 258 tests, 3 skipped, 21.283 sec
unittest external maximum RSS: 492,044,288 bytes
pytest: 255 passed, 3 skipped, 25 subtests passed, 23.77 sec
pytest external maximum RSS: 523,501,568 bytes
```

Zero-dependency environment:

```text
unittest: 246 tests, 118 explicit optional skips, 0.285 sec
maximum RSS: 40,845,312 bytes
```

The preregistration baseline was 249 unittest tests with 3 skips and 246 pytest
tests with 3 skips plus 25 subtests. RW2 adds nine focused tests with no
optional-environment regression. The base run initially exposed five old
optional-test collection/guard defects; those tests now skip only when their
dependency path genuinely cannot run, and the same paths execute in the
optional-neuro environment.

Additional gates:

- Ruff passed over the full repository;
- `compileall` passed over `src` and `tests`;
- root and all four RW2 CLI help paths passed;
- deterministic fixture-manifest replay passed;
- `git diff --check` passed;
- Gitleaks default history scan passed after one exact reviewed artifact-hash
  fingerprint;
- generated fixture/report artifacts remain ignored and uncommitted.

## Decision

Close RW2 at exact synthetic compatibility level 2.

Authorize **RW3 preregistration only**. RW3 must freeze its source-chunk schema,
offline replay source, BrainFlow/LSL dependency boundary, clocks, timestamp
correction, packet-loss representation, ordering, state, chunk schedules,
tolerances, privacy fields, resources, and kill/park/proceed rules before an
adapter or live source is implemented.

RW2 does not authorize:

- a real recording read;
- S20 acquisition or access;
- reopening S7 or either S21 session;
- MNE-BIDS installation/use;
- automatic cleaning or preprocessing;
- model training or inference;
- live hardware or network streaming;
- collection from a participant.

RW4 remains separately blocked on explicit approval of the exact four-file,
96,090,264-byte S20 packet and its one-time protocol.

## Closeout Boundary

**Engineering capability added:** NeuroDecodeKit can now generate, read,
validate, summarize, and strictly replay bounded target-free synthetic
BrainVision, EDF/EDF+, BDF, EEGLAB, FIF, and BIDS signal-quality reports while
preserving provenance, privacy, resources, and source identity.

**Scientific or decoding claim not established:** RW2 does not establish real
recording quality, artifact validity on people or devices, preprocessing
benefit, neural advantage, task compatibility, unseen-person generalization,
real-time decoding, portable EEG performance, arbitrary-thought decoding, or
clinical utility.
