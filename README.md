# NeuroDecodeKit

Open-source, local-first, reproducible tools for turning EEG and MEG recordings
into small, inspectable neural language-decoding experiments without hiding
data access, split leakage, resource cost, or negative results.

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

## Results At A Glance

> The standout result is not an inflated decoder score. It is a complete,
> reproducible evidence chain that validates difficult engineering, preserves
> negative scientific results, and knows when a gate should stop.

### The Result Ladder

| Evidence layer | Strongest result so far | What that means now |
|---|---|---|
| Trial identity | All 66 S21 session-1 trials and all 63 performed session-2 trials reconcile to MAT provenance; empty session-2 slots remain explicit | The real MEG evidence has exact trial identity instead of fuzzy sentence matching |
| Local neurodata access | Six EEG/MEG file families are covered by 40 bounded fixtures: 38 readable and 2 exact refusals | Contributors can test metadata, readers, privacy, and caps without sharing participant recordings |
| Continuous interfaces | NeuroTokenCache preserves 553 valid synthetic frames; causal replay is exact across 5/5 schedules with zero right context | Cache and streaming contracts exist, but they do not establish useful neural representations or text decoding |
| Real predictive evidence | Both the same-person cross-session MEG model and the bounded S7 EEG classifier lose to no-signal controls | The current scientific result is negative, explicit, and frozen against post-hoc tuning |
| Local execution gate | Three exact CPU paths, two fresh target-free fixture partitions, 12 balanced timing rounds, and 30 refusals are frozen before candidate code | Loop 24 is ready for an explicit implementation decision; no precision candidate or runtime has been executed |
| Next transport layer | Stage A is specified as 90 future schedule-by-fixture cases with 30 exact refusals under a 32 MiB cap | The decision packet is review-ready; no replay runtime, socket, board, or hardware path is authorized yet |

### Detailed Engineering Scorecard

| Result | Measured evidence | Proof label | Why it matters |
|---|---|---|---|
| Complete S21 trial reconciliation | 66/66 session-1 trials; 63/63 performed session-2 trials; empty MAT slots 54, 58, and 60 preserved | real-data validated | Turns ambiguous trigger/log ordering into exact trial provenance instead of fuzzy text matching |
| Task-matched EEG bridge | 2,534 MAT triggers aligned; 2,197 windows; `2197 x 61 x 25`; 12,428,800-byte cache | real-data validated | Proves bounded BrainVision plus MAT mechanics on EEG without pretending the classifier succeeded |
| Sampling-rate characterization | identical 66-row caches at 100/50/25 Hz; 1,663,209 / 846,334 / 431,451 bytes | real-data validated | Quantifies storage and temporal feasibility without selecting a rate from unmeasured accuracy |
| Geometry-aware channel subsets | one 102-magnetometer base plus 20 exact-identity subset caches under 128 MiB | real-data validated | Makes sensor-cost tradeoffs inspectable while keeping geometry proxies separate from decoding claims |
| Precision/storage sweep | qint16 is 49.84% smaller; qint8 is 80.75% smaller with worst relative RMSE 0.9531%; no clipping | real-data cache mechanics | Measures representation distortion without calling it retained model accuracy |
| NeuroTokenCache v0 | `48 x 16 x 32`; 76,646 bytes; exact payload replay; zero target-member reads | fixture-backed interface | Establishes a strict modality/timing/mask/split/hash contract without unreleased embeddings |
| Causal frame replay | 553 canonical frames; 5/5 schedules exact; zero right context; 300-byte mutable state | synthetic mechanism only | Separates true producer causality from transport scheduling and decoder latency |
| Tiny learned causal producer | 1,130 parameters; validation and one-time test balanced accuracy 1.0 versus 0.166667 signal-free prior; 5/5 replay | synthetic mechanism only | Proves the bounded stream can carry a learned signal on an intentionally easy generated task |
| Blank calibration mechanism | validation and one-time test both 16/16 exact at CER 0; 9 test corrections; 0 regressions | synthetic mechanism only | Shows one preregistered scalar can solve a specific tail-error mechanism without post-test trimming |
| Local precision/runtime registration | 3 exact candidates; fresh seeds 2401/2402; 12 balanced selection rounds; 30 refusal IDs; 9 dependency-free invariants | preregistered, no runtime | Freezes correctness, timing, storage, memory, access, and claim gates before a candidate can be favored |
| Metadata-only local intake | 6 format families; 532 source bytes; 11,545 report bytes; 0 binary/raw/target/model/network reads | fixture-backed | Lets EEG owners start with safe structure and provenance instead of uploading a recording |
| Bounded signal-quality interface | 40 fixtures; 38 readable and 2 exact refusals across 6 format families; 3.839 sec; 76,592 output bytes | fixture-backed | Validates readers, metrics, privacy, caps, and no-mutation identity before any real quality claim |
| Replay/live-source authorization gate | 5 schedules x 18 fixture families = 90 future cases; 30 refusal IDs; 4 separately gated stages; 10 invariants | review-ready, not authorized | Binds the exact Stage A scope and caps before any source-chunk, socket, board, fixture, or hardware implementation |
| Test and release surface | 277 unittests with 3 skips; 274 pytest passes, 3 skips, and 25 subtests; 265-test zero-dependency suite also green | local shell verified | Makes the research contracts executable for contributors on ordinary hardware |

### Real-Data Scientific Scorecard

| Evaluation | Neural result | No-signal result | Honest decision |
|---|---:|---:|---|
| S21 session-1 strict five-row sentence test | 163 character edits | 164 character edits | Near-null difference; paired interval spans benefit and harm |
| S21 session-2 same-person transfer | CER `0.9179` | CER `0.7755` | Neural model is materially worse; session is consumed |
| S7 EEG within-session key events | exact accuracy `0.91%` | exact accuracy `12.27%` | Neural template is materially worse; EEG bridge is mechanics only |

**Scientific headline:** the real MEG and EEG evaluations run so far do not
show a reliable neural advantage. That negative result is preserved beside the
engineering wins, not hidden behind synthetic accuracy.

### Resource Highlights

| Gate | Runtime | Peak RSS | Persistent output |
|---|---:|---:|---:|
| Zero-dependency full unittest run | 1.440 sec | 64,290,816 bytes | temporary test output only |
| RW1 metadata intake roundtrip | 0.001659 sec | 21,643,264 bytes | 11,545 bytes |
| RW2 bounded FIF quality roundtrip | 3.839168 sec | 150,749,184 bytes | 76,592 bytes |
| RW3 contract/request invariant suite | 0.040 sec | 20,529,152 bytes | no generated payload |
| Loop 24 preregistration invariant suite | 0.110 sec | 20,742,144 bytes | no generated payload |
| Complete optional-neuro/ML test runners | 15.460 sec max | 580,567,040 bytes max | temporary test output only |

Proof labels are deliberately narrow:

- **real-data validated** means the named interface or identity claim ran on the
  exact local recording described;
- **fixture-backed** means deterministic generated files exercised the contract;
- **synthetic mechanism only** means the result cannot be transferred to brain
  data, people, or devices;
- **review-ready, not authorized** means the bounded protocol and decision packet
  exist, but their planned runtime does not;
- **preregistered, no runtime** means candidates, data independence, metrics,
  thresholds, and refusals are frozen before any candidate implementation or
  benchmark execution;
- **parked** means a registered primary gate failed and the project did not tune
  past it.

Detailed evidence is linked from the
[documentation map](#documentation-map), including
[the RW2 closeout](docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md).

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
- **RW3 protocol registration:** a versioned, machine-checked contract freezes
  source identity, raw/corrected/arrival timestamps, gaps, duplicates,
  reordering, reconnects, state, five schedules, 18 future fixture families,
  30 refusal IDs, and four separately gated adapter stages. No source-chunk or
  adapter runtime exists yet.
- **RW3 Stage A decision packet:** a hash-bound request now defines 90 future
  schedule-by-fixture cases, all 30 deterministic refusals, one-thread resource
  caps, and the exact authorization sequence. The request says
  `authorized_now: false`; preparing it did not authorize implementation.
- **Loop 24 precision/runtime registration:** a versioned contract freezes the
  float32 eager reference, explicit CPU float16, and dynamic-qint8 QNNPACK
  candidates; fresh target-free seeds 2401 and 2402; 12 balanced timing rounds;
  exact behavior, resource, and claim gates; and 30 refusal IDs. Commit
  `186bb6f` contains protocol evidence only: no fixture, checkpoint read,
  candidate conversion, inference, timing, energy, or qualification run exists.

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
- Loop 24 freezes how local CPU precision and runtime would be compared, but it
  has not yet produced a float16, qint8, speed, memory, storage, or energy result.

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

Replay and hardware contributions must begin from the frozen
[RW3 preregistration](docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md) and
[machine contract](registries/replay_equivalence_contract.v0.json). The
[Stage A authorization packet](docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md) and its
[machine request](registries/rw3_stage_a_authorization_request.v0.json) make the
next permission exact, but both still say that Stage A is unauthorized. A
hardware contribution, issue, or pull request cannot substitute for that
decision; each runtime stage requires a separate review.

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

Loop 24, if separately authorized, freezes one thread and worker, at most 48
fresh target-free items per partition, 32 MiB of materialized arrays, 4 MiB of
total generated artifacts, 60 seconds of internal runtime, and 1 GiB peak RSS
per worker. Its registration authorizes none of those operations yet.

Generated artifacts belong in ignored `cache/` or `outputs/`, not in Git.

## Project Status And Roadmap

The original numbered development sequence has reached:

- Loops 1-12: completed;
- Loop 13: parked after measured lazy-backend gate;
- Loops 14-22: completed at their exact proof boundaries;
- Loop 23: parked after the frozen synthetic decoder test missed its primary
  threshold;
- Loop 23.5: completed as a supervised synthetic calibration mechanism;
- Loop 24: preregistered at `186bb6f` with contract SHA-256
  `58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d`;
  implementation and execution remain unauthorized, and consumed seed 2353
  cannot select candidates;
- Loops 25-44: a new primary-source-informed planning tranche spans causal
  evidence, translation/generalization, reliability/confounds,
  reproducibility/local deployment, and live translation/release. All 20 rows
  are `Not Started`, `execution_authorized: false`, and subordinate to the
  current Loop 24 decision.

The parallel Real-World Practice track has reached:

- RW0: primary-source dataset/device research and bounded acquisition planning;
- RW1: dependency-free metadata-only local intake, fixture-backed;
- RW2: bounded synthetic signal-read and descriptive quality-report interface,
  fixture-backed;
- RW3: replay/live-source equivalence preregistered at `c3d1f01`; the Stage A
  decision packet is ready for explicit review, while Stage A and all runtime
  adapters remain unauthorized;
- RW4+: not authorized by RW3 registration;
- proposed S20 acquisition: dry-run only until exact approval.

The next tranche is a claim graph, not a feature wish list. A failed real
validation gate parks model scaling; a failed neural ablation blocks neural
attribution; a failed replay gate blocks device work. Negative results remain
valid closeouts. Roadmap approval and general continuation are not execution
authorization.

See [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) and
[docs/LOOPS_25_44_ROADMAP.md](docs/LOOPS_25_44_ROADMAP.md), plus the separate
[real-world practice track](docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md).

## Documentation Map

| Document | Purpose |
|---|---|
| [START_HERE.md](START_HERE.md) | shortest current orientation |
| [docs/CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md) | exact continuation boundary for coding agents |
| [docs/BUILD_NOTES.md](docs/BUILD_NOTES.md) | chronological measured build journal |
| [docs/DECISIONS.md](docs/DECISIONS.md) | consequential architecture and research decisions |
| [docs/NEXT_20_LOOPS_TRACKER.md](docs/NEXT_20_LOOPS_TRACKER.md) | original 20-loop tracker, current post-roadmap gate, and planning-only Loops 25-44 summary |
| [docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx](docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx) | nine-sheet working tracker with separate original-roadmap, current-gate, practice-track, and Loops 25-44 views |
| [docs/POST_20_ROADMAP.md](docs/POST_20_ROADMAP.md) | closed/current post-NeuroToken gates plus links to the next tranche |
| [docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md](docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md) | Brain2Qwerty, MNE, BIDS, MOABB, LSL, privacy, uncertainty, and edge-runtime research behind Loops 25-44 |
| [docs/LOOPS_25_44_ROADMAP.md](docs/LOOPS_25_44_ROADMAP.md) | detailed goals, controls, metrics, acceptance gates, stop rules, dependencies, caps, and authorization boundaries for the next 20 loops |
| [registries/next_20_loops.v0.json](registries/next_20_loops.v0.json) | machine-readable five-phase roadmap with 20 false execution flags and row-level primary-source bindings |
| [docs/REAL_DATA_VALIDATION_2026-07-10.md](docs/REAL_DATA_VALIDATION_2026-07-10.md) | S21 alignment, session, and upstream audit |
| [docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md](docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md) | real EEG bridge and negative classifier result |
| [docs/LOOP_20_NEUROTOKEN_CACHE_V0.md](docs/LOOP_20_NEUROTOKEN_CACHE_V0.md) | NeuroTokenCache schema and synthetic interface proof |
| [docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md) | PyTorch precision, timing, memory, and energy primary-source review |
| [docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md](docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md) | frozen Loop 24 candidates, fresh fixtures, measurements, thresholds, caps, and decision language |
| [registries/local_precision_runtime_contract.v0.json](registries/local_precision_runtime_contract.v0.json) | machine-readable Loop 24 identities, schedules, refusals, access rules, and false authorization flags |
| [docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md](docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md) | metadata-only file intake closeout |
| [docs/RW2_PRIMARY_SOURCE_RESEARCH.md](docs/RW2_PRIMARY_SOURCE_RESEARCH.md) | reader/quality primary-source review |
| [docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md](docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md) | frozen RW2 protocol |
| [docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md](docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md) | measured six-format RW2 implementation result |
| [docs/RW3_PRIMARY_SOURCE_RESEARCH.md](docs/RW3_PRIMARY_SOURCE_RESEARCH.md) | BrainFlow, LSL, PyXDF, and clock primary-source review |
| [docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md](docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md) | frozen replay/live-source protocol; no implementation |
| [registries/replay_equivalence_contract.v0.json](registries/replay_equivalence_contract.v0.json) | machine-readable RW3 schedules, fixtures, refusals, caps, and authorization flags |
| [docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md](docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md) | exact Stage A scope, acceptance gates, caps, forbidden work, and decision language |
| [registries/rw3_stage_a_authorization_request.v0.json](registries/rw3_stage_a_authorization_request.v0.json) | hash-bound machine request; currently `authorized_now: false` |
| [docs/BYO_NEURODATA_WORKBENCH_SPEC.md](docs/BYO_NEURODATA_WORKBENCH_SPEC.md) | staged local neurodata workbench contract |
| [docs/OPEN_SOURCE_READINESS.md](docs/OPEN_SOURCE_READINESS.md) | licensing, history, privacy, GitHub, and release gates |
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

| You have | Best first contribution | Keep private or gated |
|---|---|---|
| An EEG recording | Run metadata-only intake locally and share a redacted compatibility summary | Waveforms, event text, participant paths, demographics, and unreviewed derived caches |
| An EEG headset or board | Document channels, reference, clocks, transport, packet counters, export formats, and SDK license | Live connection details, private endpoints, credentials, and unapproved recordings |
| No EEG hardware | Add deterministic fixtures, malformed cases, refusal tests, docs, or no-signal controls | No real data is needed for these high-value paths |

Precision or local-runtime contributions must begin with the frozen Loop 24
protocol. A benchmark pull request is not execution authorization, smaller
weights are not proof of faster inference, and neither result is evidence of
brain decoding or end-to-end text latency.

The project deliberately treats an exact refusal, a privacy-preserving metadata
report, or a reproducible negative result as a meaningful contribution. See
[I Have EEG Data](#i-have-eeg-data) and
[I Have An EEG Headset Or Board](#i-have-an-eeg-headset-or-board) for the
step-by-step routes.

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
