# NeuroDecodeKit

Local-first, reproducible tools for turning EEG and MEG recordings into small,
inspectable neural language-decoding experiments without hiding data access,
split leakage, resource cost, or negative results.

NeuroDecodeKit is an independent research toolkit inspired by the access and
reproducibility problems around Brain2Qwerty-style decoding. It is not an
official Brain2Qwerty project, a medical device, or a demonstrated mind-reading
system.

```text
manifest -> selective download -> tiny shard -> event/sentence cache
         -> no-signal baseline -> neural baseline -> CER/WER report
```

The core thesis is practical: before another large model matters, a researcher
should be able to identify one legal dataset slice, inspect it locally, build a
bounded cache, preserve provenance, compare against a language-only control,
and explain exactly what the result does not prove.

## Current Proof Boundary

Read this before interpreting any number in the repository.

### What Is Established

- **Base package:** dependency-free CLI, metrics, schemas, manifests, split
  audits, and report validation run without MNE, Torch, Zarr, or Hugging Face.
- **Real S21 MEG alignment:** all 66 performed session-1 trials are reconciled
  to target/response/timing provenance under the validated S21 parser.
- **Strict split mechanics:** session 1 has a deterministic 55/6/5
  train/validation/test protocol with train-only preprocessing.
- **Independent same-person session mechanics:** session 2 has 63 performed
  trials, preserves three empty MAT slots, and is bound to frozen session-1
  train statistics.
- **Real EEG bridge mechanics:** one S7 BrainVision recording and matching MAT
  log produce 2,197 lazily read key-event windows shaped `61 x 25`.
- **NeuroTokenCache v0:** a strict modality-aware continuous embedding cache
  preserves masks, lengths, timestamps, source identities, geometry status,
  splits, configuration, hashes, causality, context, resources, and warnings.
- **Causal producer mechanics:** synthetic replay proves schedule-invariant
  causal frame production with zero right context and bounded state.
- **Metadata-only neurodata intake:** BrainVision, EDF/EDF+, BDF, continuous
  EEGLAB external-FDT, FIF, and BIDS bundles can be recognized and reported at
  compatibility level 0 without reading binary samples or event content.
- **Synthetic signal-quality adapters:** RW2 exercises 38 readable fixtures and
  two frozen refusal fixtures across those six format families using bounded
  optional MNE readers, strict source binding, descriptive metrics, privacy
  redaction, and before/after no-mutation checks.

### What The Results Actually Say

- The fixed real same-person cross-session MEG CTC is **worse** than the
  no-signal prior: corpus CER `0.9179` versus `0.7755`.
- The real S7 EEG nearest-centroid classifier is **worse** than its train-only
  no-signal prior: `0.91%` versus `12.27%` exact key-label accuracy.
- Loop 13 parks a lazy-backend migration because measured NPZ access did not
  justify building a second storage backend.
- Loop 23 parks a synthetic streaming CTC gate after missing its registered
  exact-sequence threshold, even though several secondary metrics passed.
- Loop 23.5 shows that one supervised blank-logit intercept fixes one fresh
  synthetic motif/symbol task. That is a mechanism result, not brain decoding.

### What Is Not Established

There is no demonstrated:

- neural advantage on the real evaluated MEG or EEG cohorts;
- unseen-person generalization;
- useful open-vocabulary EEG sentence decoder;
- result on unreleased Brain2Qwerty v2 data or embeddings;
- end-to-end real-time text latency;
- portable, consumer, or at-home hardware result;
- arbitrary-thought decoding;
- clinical, diagnostic, or assistive efficacy.

S21 session 2, the S7 EEG evaluation, and synthetic test seeds 2203, 2303, and
2353 are consumed for the decisions they informed. They must not be reopened
for tuning and then described as fresh evidence.

The detailed risk language lives in
[docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md).

## Why This Project Exists

The practical barrier to neural language-decoding research is often not the
last model layer. It is everything before and around it:

- public neuroimaging releases can be hundreds of gigabytes;
- event and behavioral logs can use undocumented timing domains;
- participant aliases can invalidate nominal subject splits;
- preprocessing fit on evaluation rows can leak information;
- language priors can be credited to neural signal;
- a cache can silently lose channel, timing, geometry, or split identity;
- “causal,” “streaming,” “online,” and “real-time” are often collapsed;
- a successful file read can be overstated as device or decoding support.

NeuroDecodeKit turns those risks into explicit interfaces, counters, hashes,
caps, tests, and report fields.

## Quickstart

### 1. Base Install

Python 3.10 or newer is required.

```bash
git clone https://github.com/CheickDiakite-yikes/neurodecodekit.git
cd neurodecodekit
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The base install has zero runtime dependencies. Exercise pure-Python metrics:

```bash
neurodecode eval-text \
  --target "HOLA MUNDO" \
  --prediction "HOLA MUNCO"
```

Run the base-aware test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tests for unavailable optional dependencies skip cleanly. A skipped optional
test is not evidence that its MNE or Torch path passed.

### 2. Tiny Array Smoke

Install only NumPy for synthetic shards and NPZ interfaces:

```bash
python -m pip install -e '.[array]'

neurodecode make-synthetic-shard \
  --out cache/synthetic_tiny.npz \
  --samples 64 \
  --channels 8 \
  --times 25

neurodecode load-cache \
  --cache cache/synthetic_tiny.npz \
  --metadata-out cache/synthetic_tiny.metadata.json

neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md \
  --run-name synthetic_identity_plumbing \
  --split synthetic-smoke
```

`--identity-smoke` copies targets to predictions to prove report plumbing. It
is deliberately labeled as **not a model result**.

### 3. Choose Optional Capabilities

Install only what the task needs:

| Extra | Adds | Typical use |
|---|---|---|
| `array` | NumPy | synthetic shards, NPZ caches, NeuroToken interfaces |
| `neuro` | MNE 1.12.x, NumPy, SciPy | format readers, bounded signal inspection, extraction |
| `ml` | NumPy, scikit-learn, Torch | optional small baselines and synthetic learned gates |
| `hf` | Hugging Face Hub | metadata listing and explicit selective download |
| `cache` | Zarr, numcodecs, NumPy | measured storage-backend experiments |
| `demo` | Gradio | local artifact-backed evidence console |
| `dev` | Ruff, pytest | contributor checks |
| `all` | all optional groups | full local development; large |

Examples:

```bash
python -m pip install -e '.[neuro,dev]'
python -m pip install -e '.[array,demo]'
```

Heavy imports remain inside the commands that need them. Adding an optional
feature should not make `import neurodecodekit` import MNE, NumPy, or Torch.

## I Have EEG Data

You can contribute without uploading the recording.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md), especially **I Have EEG Data**.
2. Open the **EEG data compatibility** issue form.
3. Share only non-sensitive aggregate facts: format, device family, nominal
   channels/rate, reference availability, task cohort, license, and byte cap.
4. Run metadata-only intake locally.
5. Reproduce the relevant format condition with a deterministic synthetic
   fixture.
6. Request a separately frozen bounded real-read protocol only if the synthetic
   gate passes and the data terms permit it.

Do not attach raw EEG, event files, target text, participant tables, private
cloud links, derived embeddings, or subject-level predictions to an issue.

### Metadata-Only Local Intake

The base command inspects structure without opening binary signal samples or
event/target content:

```bash
neurodecode inspect-recording \
  --path /absolute/path/to/recording-or-bids-root \
  --root /absolute/path/to/allowed-root \
  --out-dir /absolute/path/to/private/intake-report \
  --modality EEG \
  --device-type "your device or amplifier"

neurodecode inspect-intake-report \
  --report /absolute/path/to/private/intake-report/intake.json
```

The output includes deterministic JSON/Markdown plus a measured audit sidecar,
relative source identity, companion validation, known/unavailable fields,
warnings, access counters, hashes, runtime, RSS, and output bytes.

Review it locally before sharing. Metadata can still be sensitive.

### Compatibility Is Staged

| Level | Evidence |
|---:|---|
| 0 | File family and companions recognized |
| 1 | Bounded samples readable |
| 2 | Channels, timing, units, geometry status, and aggregate events validated |
| 3 | Deterministic preprocessing/replay validated |
| 4 | Leakage-resistant classification beats registered controls |
| 5 | Sequence metrics beat no-signal controls on a fresh split |
| 6 | Live/replay timing and end-to-end behavior measured |

A level applies only to the exact format, adapter, configuration, and evidence
cohort tested. It does not transfer automatically to another headset, dataset,
task, subject, or session.

## I Have An EEG Headset Or Board

Use the **EEG hardware qualification** issue form. Include:

- model, revision, firmware, SDK, and operating system;
- EEG/ExG channel roles, electrode placement, reference, and ground;
- nominal and measured sampling rate;
- raw API or file export;
- USB, serial, BLE, Wi-Fi, LSL, XDF, or cloud transport;
- timestamp clock, correction, packet counter, and packet-loss behavior;
- local/offline capability and SDK license;
- separate peripheral streams such as EOG, EMG, PPG, IMU, gaze, or audio.

The preferred first result is offline replay equivalence on deterministic
samples. A connected device or live waveform plot is not a language decoder.
Four-channel consumer EEG is not assumed equivalent to 64-channel research EEG
or 306-channel MEG.

The current metadata device registry is
[registries/devices.v0.json](registries/devices.v0.json). Registry presence is
not device qualification.

## Safe Workflows

### RW2 Synthetic Signal-Quality Roundtrip

This workflow requires `.[neuro]`, reads no participant data, and creates less
than the frozen 16 MiB fixture/report cap:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

neurodecode make-signal-quality-fixtures \
  --out-dir cache/rw2-fixtures \
  --contract registries/signal_quality_contract.v0.json

neurodecode inspect-signal-quality-fixtures \
  --manifest cache/rw2-fixtures/signal_quality_fixtures.json

neurodecode inspect-signal-quality \
  --path cache/rw2-fixtures/fixtures/clean_multitype_continuous__fif/source/recording_raw.fif \
  --root cache/rw2-fixtures \
  --intake-report cache/rw2-fixtures/fixtures/clean_multitype_continuous__fif/intake/intake.json \
  --fixture-manifest cache/rw2-fixtures/signal_quality_fixtures.json \
  --contract registries/signal_quality_contract.v0.json \
  --out-dir cache/rw2-quality

neurodecode inspect-signal-quality-report \
  --report cache/rw2-quality/signal_quality.json
```

RW2 reports descriptive time-domain and Welch PSD summaries, units, geometry
availability, reference status, aggregate annotation status, source filters and
projectors, bounded windows, access counts, resource measurements, warnings,
and no-mutation identity. It performs no filtering, rereferencing, bad-channel
repair, interpolation, ICA, clipping, scaling, model run, or training.

RW2 is a synthetic reader and report-interface proof. It says nothing about the
quality of a person's recording.

### Dataset Manifest Without Download

Build and inspect a manifest from an existing path list:

```bash
neurodecode manifest-from-paths \
  --paths data/file_list.txt \
  --out data/manifest.jsonl

neurodecode inspect-manifest \
  --manifest data/manifest.jsonl

neurodecode select-tiny \
  --manifest data/manifest.jsonl \
  --out data/tiny_selection.json \
  --modality EEG \
  --blocks 1 \
  --max-files 4 \
  --max-total-gb 1
```

`select-tiny` records exact paths, known bytes, unknown-size warnings,
revision, and caps.

### Selective Download Is Dry-Run First

Hugging Face access is optional:

```bash
python -m pip install -e '.[hf]'

neurodecode download-selection \
  --selection data/tiny_selection.json \
  --local-dir data/spanishbcbl_tiny
```

That command does not download by default. `--execute` is required, unknown
sizes fail closed unless explicitly allowed after review, and the default worker
count is one.

Do not use this example as authorization to download SpanishBCBL. Check the
dataset license, exact revision, local disk, protocol, and approval boundary.

### Event-Window Extraction

For an explicitly acquired, legally usable, validated FIF/MAT pair:

```bash
python -m pip install -e '.[neuro]'

neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../logs.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-events 200
```

This command does not download data. It reports source bytes, events found,
kept and dropped events, shape, rate, channels, parser warnings, runtime, and
output bytes.

Generic MAT schemas do not inherit the validated S21 trial-ordering claim.

### Honest Baselines

Run the no-brain comparator before interpreting a neural model:

```bash
neurodecode prior-baseline \
  --cache cache/synthetic_tiny.npz \
  --out-predictions cache/prior_predictions.txt \
  --out-json cache/prior_report.json \
  --out-md cache/prior_report.md \
  --run-name synthetic_prior \
  --split synthetic-smoke

neurodecode template-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/template_predictions.txt \
  --out-json cache/template_report.json \
  --out-md cache/template_report.md \
  --run-name synthetic_template \
  --split synthetic-holdout
```

Synthetic separability proves plumbing and model mechanics only. A real neural
result must use train-only fitting, frozen split identity, a no-signal prior,
and uncertainty appropriate to the evaluation unit.

## CLI Map

The CLI intentionally exposes small auditable stages:

| Area | Commands |
|---|---|
| Text metrics/reports | `eval-text`, `report`, `build-leaderboard` |
| No-signal/small baselines | `prior-baseline`, `sentence-prior-baseline`, `template-baseline`, `tiny-conv-baseline` |
| Discovery/download | `manifest-from-paths`, `inspect-manifest`, `select-tiny`, `list-hf-files`, `download-selection` |
| Local intake | `inspect-recording`, `inspect-intake-report` |
| Synthetic quality | `make-signal-quality-fixtures`, `inspect-signal-quality-fixtures`, `inspect-signal-quality`, `inspect-signal-quality-report` |
| Event/sentence extraction | `extract-windows`, `extract-eeg-windows`, `extract-sentence-cache`, `align-sequences` |
| Cache interfaces | `make-synthetic-shard`, `load-cache`, `make-synthetic-sentence-cache`, `inspect-sentence-cache`, `make-neurotoken-cache`, `inspect-neurotoken-cache` |
| Split/session controls | `split-protocol`, `apply-frozen-scaler`, `cross-session-ctc` |
| Resource experiments | `sampling-rate-sweep`, `channel-subset-sweep`, `precision-storage-sweep`, `inspect-representation-cache`, `lazy-backend-gate` |
| Synthetic causal gates | `causal-replay-gate`, `make-causal-motif-fixture`, `tiny-causal-encoder-gate`, `make-ctc-symbol-stream-fixture`, `streaming-ctc-gate`, `make-blank-calibration-fixture`, `blank-intercept-gate` |
| Research/demo | `eeg-bridge-gate`, `synthetic-adapter-gate`, `synthetic-calibration-curve`, `demo` |

Use `neurodecode COMMAND --help` for exact arguments and safety defaults.

## Architecture

```text
src/neurodecodekit/
  datasets/       manifests, local intake, safe selection, optional Hub access
  preprocess/     format readers, event alignment, window/sentence extraction
  cache/          NPZ schemas, packed representations, NeuroToken interfaces
  models/         prior, template, tiny Conv/CTC, causal encoder components
  training/       deterministic synthetic fixtures and bounded runners
  evaluation/     CER/WER, controls, reports, splits, uncertainty, report cards
  experiments/    preregistered resource, session, causal, and EEG gates
  demo/           artifact-backed local evidence console
```

The CLI defers heavy imports into individual commands. Source modules use strict
schemas and dataclasses where structured records cross boundaries.

## Stable Interfaces

### B2Q-Mini Event Cache v0

An event cache stores:

```text
windows             [events, channels, timepoints]
labels              per-event labels when validated
event_start_sec     event timing
event_source_index  source row or trigger identity
channel_names       ordered selected channels
metadata            schema, source, transforms, warnings, hashes
```

### Continuous Sentence Cache v0

Sentence caches preserve variable true lengths, trial identity, target/response
provenance, source sampling rate, channel order, geometry availability, split
binding, fit scope, and transformation history.

### NeuroTokenCache v0

NeuroTokenCache is shaped `[items, time, embedding]` and preserves:

- modality and device type;
- item, subject, session, trial, and split identities;
- source rate and token timestamps;
- true lengths and padding masks;
- channel names and available geometry;
- causal/noncausal status and required context;
- source-cache, split-protocol, configuration, and payload hashes;
- warnings, unavailable fields, access counters, and claim boundaries.

The current Loop 20 producer is a deterministic target-free projection from
synthetic signals. It is not a learned representation or decoding result.

## Evaluation Discipline

NeuroDecodeKit separates:

- language-only priors from neural models;
- train/validation/test/calibration membership;
- split membership from preprocessing fit scope;
- event classification from sentence decoding;
- within-recording, cross-session, and unseen-person evidence;
- EEG from MEG and peripheral modalities;
- producer causality from decoder causality;
- intrinsic context, transport delay, compute time, and end-to-end latency;
- synthetic mechanisms from real-data results;
- fresh tests from consumed evaluations.

Every report should name the dataset/revision, task, modality, subject/session
scope, split, fit rows, metrics, controls, runtime, RSS, input/output bytes,
access counts, warnings, and unavailable fields.

CER and WER are not enough by themselves. Tiny test sets need paired examples
and uncertainty; key-event tasks may need exact label accuracy; sequence tasks
need blank/repeat diagnostics and exact-sequence counts.

## Data And Privacy

Neural recordings and derived features are sensitive, even when filenames are
de-identified.

- Raw data and caches are ignored by Git.
- Reports should use relative identity and hashes, not absolute paths.
- Participant rows, free-text annotations, target sentences, serial numbers,
  exact acquisition timestamps, and exact head/sensor coordinates are omitted
  from shareable intake/quality reports.
- Prediction/error reports can reveal typed text and should remain local unless
  dataset terms and disclosure have been reviewed.
- Hashes are integrity tools, not anonymization.
- Do not attempt participant identification.

See [SECURITY.md](SECURITY.md) for private reporting and
[docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md) for the complete scope.

## Resource Discipline

The repository is designed for bounded local work:

- one worker/thread where applicable;
- dry-run downloads by default;
- explicit file and byte caps;
- no full SpanishBCBL download;
- optional dependencies;
- small synthetic fixtures;
- measured runtime, peak RSS, input bytes, output bytes, and access counts;
- no new backend or larger model without a measured reason.

RW2 freezes at most 512 selected channels, three windows, 4,194,304
channel-sample values, 32 MiB of materialized float64 arrays, 30 seconds, 1 GiB
peak RSS, 4 MiB of report output per run, and 16 MiB for the complete synthetic
fixture/report set.

Generated artifacts belong in ignored `cache/` or `outputs/`, not in Git.

## Project Status And Roadmap

The original numbered development sequence has reached:

- Loops 1-12: completed;
- Loop 13: parked after measured lazy-backend gate;
- Loops 14-22: completed at their exact proof boundaries;
- Loop 23: parked after the frozen synthetic decoder test missed its primary
  threshold;
- Loop 23.5: completed as a supervised synthetic calibration mechanism;
- Loop 24: preregistration only; consumed seed 2353 cannot select candidates.

The parallel Real-World Practice track has reached:

- RW0: primary-source dataset/device research and bounded acquisition planning;
- RW1: dependency-free metadata-only local intake, fixture-backed;
- RW2: bounded synthetic signal-read and descriptive quality-report interface,
  fixture-backed;
- RW3+: not authorized by RW2 alone;
- proposed S20 acquisition: dry-run only until exact approval.

The roadmap is not a promise of positive decoding performance. Gates can close,
park, or kill a direction.

See [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) and
[docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md](docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md).

## Documentation Map

| Document | Purpose |
|---|---|
| [START_HERE.md](START_HERE.md) | shortest current orientation |
| [docs/CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md) | exact continuation boundary for coding agents |
| [docs/BUILD_NOTES.md](docs/BUILD_NOTES.md) | chronological measured build journal |
| [docs/DECISIONS.md](docs/DECISIONS.md) | consequential architecture and research decisions |
| [docs/NEXT_20_LOOPS_TRACKER.md](docs/NEXT_20_LOOPS_TRACKER.md) | original loop tracker |
| [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) | post-NeuroToken causal/evaluation roadmap |
| [docs/REAL_DATA_VALIDATION_2026-07-10.md](docs/REAL_DATA_VALIDATION_2026-07-10.md) | S21 alignment, session, and upstream audit |
| [docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md](docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md) | real EEG bridge and negative classifier result |
| [docs/LOOP_20_NEUROTOKEN_CACHE_V0.md](docs/LOOP_20_NEUROTOKEN_CACHE_V0.md) | NeuroTokenCache schema and synthetic interface proof |
| [docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md](docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md) | metadata-only file intake closeout |
| [docs/RW2_PRIMARY_SOURCE_RESEARCH.md](docs/RW2_PRIMARY_SOURCE_RESEARCH.md) | reader/quality primary-source review |
| [docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md](docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md) | frozen RW2 protocol |
| [docs/BYO_NEURODATA_WORKBENCH_SPEC.md](docs/BYO_NEURODATA_WORKBENCH_SPEC.md) | staged local neurodata workbench contract |
| [registries/datasets.v0.json](registries/datasets.v0.json) | task-separated dataset candidates |
| [registries/devices.v0.json](registries/devices.v0.json) | device and modality metadata, not qualification |
| [docs/RISK_AND_ETHICS.md](docs/RISK_AND_ETHICS.md) | privacy, licensing, ethics, and communication boundary |

Loop-specific closeouts in `docs/LOOP_*.md` preserve exact commands, metrics,
resources, failures, and claims.

## Contributing

Contributions are welcome, especially:

- deterministic format fixtures and malformed cases;
- metadata-only compatibility reports;
- EEG reference, geometry, timing, and unit validation;
- offline device replay and packet-loss audits;
- no-signal controls and split-leakage tests;
- accessibility, setup, and documentation improvements;
- small CPU-bounded baselines with honest negative reporting.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). It contains dedicated safe paths
for people with EEG recordings and people with EEG headsets or boards.

Community files:

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Governance](GOVERNANCE.md)
- [Support](SUPPORT.md)
- [Security](SECURITY.md)

## License And Third-Party Terms

NeuroDecodeKit's original source code and documentation are licensed under the
[Apache License 2.0](LICENSE).

That license does not relicense Brain2Qwerty, SpanishBCBL, participant data,
models, papers, device SDKs, or optional dependencies. Brain2Qwerty and the
SpanishBCBL release are separately identified as `CC-BY-NC-4.0`; work using
them must respect their noncommercial and attribution terms.

Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before using upstream code,
data, or assets.

## Citation And Acknowledgments

Use [CITATION.cff](CITATION.cff) to cite NeuroDecodeKit. Cite every dataset,
paper, and upstream implementation separately; a software citation does not
replace participant-data attribution.

NeuroDecodeKit builds on the public research ecosystem around Brain2Qwerty,
SpanishBCBL/DECOMEG, MNE-Python, BIDS, and the broader EEG/MEG community. It is
independent and is not endorsed by those projects or institutions.

## Plain-English Bottom Line

**Engineering capability:** NeuroDecodeKit provides a bounded, local,
reproducible path from neurodata discovery and file qualification through
caches, controls, small baselines, causal interface tests, and inspectable
reports.

**Scientific claim not established:** the repository has not shown that neural
signal beats language-only controls for practical text decoding, generalizes to
new people, runs end to end in real time, or works on portable EEG hardware.
