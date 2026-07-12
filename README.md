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
| Full-path causality gate | Loop 25 v1 freezes a dedicated causal anti-alias stage, a 65,537-point 0-500 Hz response audit, 23 alias probes, 7 chunk schedules, 10 resume cuts, 3 future-mutation cuts, and 45 refusals | The source-audited protocol is awaiting authorization; v0 was superseded safely, and no coefficient, fixture, seed open, or preprocessing result exists |
| Next predictive design | Loop 26 research narrows the future gate to a 2,908-parameter causal candidate, a 2,884-parameter linear comparator, six required controls, and all 64 paired sign assignments over six reserved validation sentences | The experiment is still `Not Started`; this is an identifiability and design result, not neural performance |
| Fresh transfer candidate | Loop 27 metadata research selects S25 session 2 block 2: one MEG FIF plus one protected MAT log, exactly 1,009,939,983 bytes under 1 GiB | S25 is not downloaded or qualified; preregistration waits for the causal source model, controls, and target isolation |
| Transfer decision rule | Loop 28 research separates T0-T3 evidence and recommends a strict S25 T2 zero-shot gate: zero target fit, at least 48 final rows, at least 0.05 macro-CER improvement, 65,535 paired swaps plus observed, and strict corruption-control wins | The experiment is `Not Started`; this resolves one planning dependency without authorizing S25, a model run, calibration, or final access |
| Portable sensing decision | Loop 29 research separates cryogenic MEG, partner/lab OPM-MEG, local-first scalp EEG, and non-neural controls through 15 requirements and six qualification levels | Planning research is complete while the experiment is `Not Started`; no device, download, stream, hardware session, or portable decoding result exists |
| Local replay interaction decision | Loop 30 research freezes four source modes, a 30-field target-free trace, nine clock domains, six latency levels, 18 gates, 30 refusals, and fixed loopback/browser/accessibility controls | Planning research is complete while the experiment is `Not Started`; no trace, UI, server, browser run, live source, confidence, or end-to-end latency result exists |
| Neural-attribution decision | Loop 31 research freezes a 10-condition encoder matrix, a contingent 5-condition LLM/Neuro Token matrix, exact six-row intersection-union inference, 18 gates, and 24 refusals | Planning research is complete while the experiment is `Not Started`; a future local pass can establish at most sensor-signal dependence, with brain-specific attribution reserved for Loop 35 |
| Real predictive evidence | Both the same-person cross-session MEG model and the bounded S7 EEG classifier lose to no-signal controls | The current scientific result is negative, explicit, and frozen against post-hoc tuning |
| Local execution gate | Float16 preserved exact behavior but ran `1.170x` slower on the producer; qint8 cut payload to `47.1%` but changed behavior and ran `2.785x` slower | Float32 is retained, qualification stayed unopened, and Loop 24 is parked after the full run exceeded its 60-second cap |
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
| Local precision/runtime gate | 3 exact candidates; 12/12 balanced rounds; 990 frames; float16 exact but full path `1.088x`; qint8 payload `47.1%` but full path `1.812x` and incorrect; qualification 0 opens | parked target-free synthetic result | Demonstrates why payload size, correctness, steady-state speed, and orchestration cost must be separate gates |
| Metadata-only local intake | 6 format families; 532 source bytes; 11,545 report bytes; 0 binary/raw/target/model/network reads | fixture-backed | Lets EEG owners start with safe structure and provenance instead of uploading a recording |
| Bounded signal-quality interface | 40 fixtures; 38 readable and 2 exact refusals across 6 format families; 3.839 sec; 76,592 output bytes | fixture-backed | Validates readers, metrics, privacy, caps, and no-mutation identity before any real quality claim |
| Replay/live-source authorization gate | 5 schedules x 18 fixture families = 90 future cases; 30 refusal IDs; 4 separately gated stages; 10 invariants | review-ready, not authorized | Binds the exact Stage A scope and caps before any source-chunk, socket, board, fixture, or hardware implementation |
| Causal preprocessing amendment | Pinned Brain2Qwerty -> NeuralSet 0.2.2 -> MNE 1.11 source trace; dedicated elliptic SOS; 65,537 response points; 23 alias probes; 24 future target-free items; 7 schedules; 10 resumes; 3 mutation cuts; 45 refusals; 23 counters | amended preregistration, no runtime | Corrects v0's incomplete anti-alias gate before authorization and makes the full 50-500 Hz folding band falsifiable before either seed opens |
| Loop 26 identifiability boundary | 55/6/5 source split; one person/session; 64 exact sign assignments; minimum two-sided p `0.03125`; 2,908-parameter causal recommendation; 2,884-parameter comparator; 14 false authorization fields | planning research only | Defines the smallest honest next question and the hard inferential ceiling before any protected content, target, model, or validation access |
| Loop 27 fresh-holdout boundary | 315 pinned MEG metadata entries; 23 strict single-FIF/log pairs; 16 eligible; S25 selected at 1,009,939,983 bytes; S23 excluded; 18 false authorization fields | metadata research only | Finds the smallest honest same-modality transfer candidate while keeping its local MAT payload, remote FIF, targets, and backups sealed |
| Loop 28 transfer boundary | T0-T3 taxonomy; strict zero-shot/transductive split; 48-row floor; 0.05 macro-CER margin; 65,535 paired assignments plus observed; 4 comparators; 21 false authorization fields | planning research only | Makes the future one-time S25 decision falsifiable while reserving calibrated transfer for a physically separate design |
| Loop 29 portability boundary | 15 modality requirements; 4 profiles; 6 qualification levels; 12 future packet gates; 24 false authorization fields; 5,000,000,000-byte preferred storage ceiling | planning research only | Chooses EEG as the immediate local-first lane and OPM-MEG as a partner/lab lane without treating channel ablation, vendor specifications, or home acquisition as text decoding |
| Loop 30 replay interaction boundary | 4 source modes; 30 event fields; 9 clock domains; 6 latency levels; 18 future gates; 30 refusals; 30 false authorization fields | planning research only | Defines how a future target-free local replay can show revisions, finalization, clocks, privacy, and proof posture without implying live or low-latency neural decoding |
| Loop 31 neural-attribution boundary | 10 encoder conditions; 5 contingent LLM conditions; 6 claim classes; 18 future gates; 24 refusals; 19 false authorization fields | planning research only | Separates no-signal, timing, context, corrupted-signal, language-prior, and conditional Neuro Token effects while blocking brain-specific claims until Loop 35 |
| Loop 34 confidence boundary | 7 confidence semantics; 8 score/control roles; recommended fresh `128/64/256` synthetic partitions; 20 future gates; 30 refusals; 26 false authorization fields | planning research only; confidence unavailable | Separates ranking, calibrated probability, abstention, conformal risk, revision stability, and product confidence while refusing reuse of six real validation rows |
| Test and release surface | 492 local unittests with 3 expected skips; 489 pytest passes plus 226 subtests; 460 dependency-light Python tests with 121 expected skips | Loop 34 local verification is green; remote branch and PR CI are pending | Makes research contracts, candidate selection, source bindings, access order, tamper checks, and authorization boundaries executable on ordinary hardware |

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
| Dependency-light Python unittest run | 0.71 sec wall | 53,985,280 bytes | 460 tests with 121 expected optional skips; temporary output only |
| RW1 metadata intake roundtrip | 0.001659 sec | 21,643,264 bytes | 11,545 bytes |
| RW2 bounded FIF quality roundtrip | 3.839168 sec | 150,749,184 bytes | 76,592 bytes |
| RW3 contract/request invariant suite | 0.040 sec | 20,529,152 bytes | no generated payload |
| Loop 24 authorization plus frozen-boundary suite | 0.210 sec | 21,397,504 bytes | no generated payload |
| Loop 25 v1 amendment plus immutable-v0 request suite | 0.120 sec | 22,560,768 bytes | no generated payload |
| Loop 26 research plus roadmap/Loop 25 boundary suite | 0.140 sec wall max | 22,986,752 bytes max | no generated payload |
| Loop 27 pinned metadata selector | 3.100 sec wall | 63,766,528 bytes | zero downloaded payload bytes |
| Loop 24-34 focused boundary suite | 5.34 sec wall | 314,818,560 bytes | 224 tests; no generated experiment payload |
| Loop 34 plus roadmap invariants | 0.07 sec wall | 20,496,384 bytes | 26 tests; no fixture, protected cache, signal, target, model, confidence fit, score, or product-confidence operation |
| Loop 28 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 10 web operations, 1 GitHub metadata call, zero code/data payload bytes |
| Loop 29 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 14 public web operations, zero protected data/model/device operations, zero downloaded payload bytes |
| Loop 30 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 10 public web operations, zero trace/server/browser/protected-data/model/stream operations, zero downloaded payload bytes |
| Loop 31 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 16 public network operations including 8 GitHub API requests; zero protected-data/model/training/validation/LLM operations and zero downloaded data/model bytes |
| Loop 32 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 public network operations including 2 pinned GitHub source reads; zero participant/cache/signal/target/model/adapter/training/evaluation operations |
| Loop 33 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 6 public web operations; zero protected cache/signal/target/model/training/scoring/acquisition/device operations |
| Loop 34 public-source research | external interactive runtime/RSS unavailable | unavailable by tool contract | 5 public web operations; zero fixture/protected-data/target/model/confidence-fit/scoring/product-confidence/device operations |
| Loop 24 registered selection | 65.154951 sec internal | 222,248,960 bytes max worker | 262,822 bytes fixture plus output |
| Complete optional-neuro/ML test runners | 22.64 sec unittest / 22.83 sec pytest wall | 588,234,752 bytes max | temporary test output only |

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
- **authorized, no runtime** means a separate hash-bound decision permits the
  exact frozen work after its commit is pushed, but no fixture, candidate, or
  measurement result exists yet;
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
- **Loop 24 precision/runtime execution:** the frozen target-free gate ran all
  12 balanced selection rounds over 990 frames. Float16 preserved every exact
  decoder behavior and tolerance but was slower; QNNPACK qint8 exposed the
  required operator and halved payload but failed behavior/numerical gates and
  was much slower. No candidate earned qualification, seed 2402 remained
  physically unopened, and the final gate parked at `65.154951` seconds versus
  its 60-second cap. Real data, targets, training, energy measurement, RW3,
  devices, and hardware remained outside Loop 24.
- **Loop 25 causal-preprocessing amendment:** the original registration at
  `a36d97b` remains immutable but was superseded before authorization by green
  v1 commit `b6b92d8`. The current contract adds a dedicated causal elliptic
  anti-alias stage, a 65,537-point 0-500 Hz response grid, 23 alias probes, 45
  refusals, and 23 access counters while preserving physical seeds 2501/2502,
  seven schedules, ten resumes, three future mutations, and the 8 MiB cap. The
  replacement request says `authorized_now: false`; no coefficient, fixture,
  seed open, numerical preprocessing, CLI, or runtime exists.
- **Loop 26 planning research:** a machine-checked boundary identifies the
  existing real model's symmetric-padding causality defect, recommends a
  parameter-identical left-padded candidate and a nearly matched linear
  comparator, enumerates six controls and all 64 paired sign assignments, and
  keeps all protected access counters at zero. The experiment remains `Not
  Started` with no preregistration or authorization sentence.
- **Loop 27 planning research:** pinned official metadata selects S25 session 2
  block 2 as the smallest eligible clean MEG candidate after excluding observed
  S21 identity, consumed S7, and the official S23 metallic-implant case. Exact
  paths, bytes, LFS hashes, identity, license, task, unavailable fields, and 18
  false authorization flags are machine checked. No candidate payload opened.
- **Loop 28 planning research:** the future S25 question is T2 strict unseen-
  person zero-shot, not calibrated transfer. The frozen recommendation requires
  zero target-person fit, at least 48 final rows, at least 0.05 macro sentence-
  CER improvement over the source-train-only prior, 65,535 deterministic paired
  assignments plus observed, and strict wins over three signal corruptions.
  All 21 authorization flags remain false and the experiment is `Not Started`.
- **Loop 29 planning research:** the portability map keeps cryogenic MEG,
  OPM-MEG, scalp EEG, and peripheral inputs noninterchangeable. Scalp EEG is
  the immediate local-first research lane; OPM-MEG remains a specialist
  partner/lab lane. The exact S20 and S25 future bundles total 1,106,030,247
  bytes inside the user's 5-10 GB storage envelope, but the envelope is not
  download permission. All 24 authorization flags remain false, no device is
  selected, and the experiment is `Not Started`.
- **Loop 30 planning research:** the future product is a loopback-only target-
  free replay inspector. The boundary separates artifact, synthetic, recorded,
  and live source modes; freezes a 30-field trace, nine clocks, six latency
  levels, 18 gates, and 30 refusals; and requires fixed localhost, zero external
  browser traffic, explicit finalization, accessible status updates, and
  unavailable confidence. All 30 authorization flags remain false, no seed or
  payload exists, and the experiment is `Not Started`.
- **Loop 31 planning research:** the attribution firewall separates a future
  10-condition encoder matrix from a contingent 5-condition LLM/Neuro Token
  matrix. Exact six-row intersection-union inference, target-blind prediction
  freezing, timing/context controls, 18 gates, and 24 refusals are machine
  checked. All 19 authorization flags remain false, the experiment is `Not
  Started`, and brain-specific attribution remains blocked on Loop 35; the
  maximum future local claim is sensor-signal dependence.
- **Loop 32 planning research:** the fresh-person calibration firewall
  recommends one causal 32-parameter hidden affine adapter, four distinct
  zero-shot/unlabeled/label-light/supervised modes, six nested sentence
  budgets, 32/16/48 physical partition floors, six controls, 20 gates, and 26
  refusals. All 22 authorization flags remain false, no candidate is selected,
  and the experiment is `Not Started`; S25 remains final-only.
- **Loop 33 planning research:** the bounded local scaling firewall recommends
  nested `8, 16, 24, 32, 44, 55` unique-sentence prefixes, at most three seeds
  and 18 candidate fits, size-matched no-signal priors, and one shared six-row
  validation open only after every Loop 26/31/33 prediction is hash-frozen.
  Twenty gates, 30 refusals, and 23 false authorization flags are machine
  checked. The experiment is `Not Started`; physical-repetition evidence is
  unavailable, acquisition is not recommended, and all protected work is
  unauthorized.
- **Loop 34 planning research:** the confidence firewall separates seven
  semantics from raw ranking through product-visible confidence, eight
  score/control roles, and recommended fresh target-free synthetic
  calibration/selection/final counts of `128/64/256`. It requires registered
  working points, generalized risk, bounded losses, revision-delay reporting,
  and one final-target open only after every choice and hash freezes. The six
  real validation rows cannot fit and independently qualify confidence. Twenty
  gates, 30 refusals, and 26 false authorization flags are machine checked.
  The experiment is `Not Started`; confidence is unavailable and all fixture,
  fit, target, scoring, product-confidence, and real-data work is unauthorized.

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
- Loop 24 retains float32. Float16 passes correctness but misses every runtime
  replacement threshold; qint8 is smaller but fails correctness and runtime;
  the complete target-free gate parks on its 60-second orchestration cap.
- Loop 25 has a green amended preregistration and a review-ready v1 packet, not
  a causal-preprocessing result. Its anti-alias, phase/ringing, right-context,
  timing, schedule, resume, and resource claims remain proposed gates.
- Loop 26 has a green planning-research packet, not a model, training run,
  validation result, or neural advantage. Six sentence instances from one
  person and session cannot establish transfer or population generalization.
- Loop 27 identifies an acquisition candidate, not an acquired holdout. Exact
  channels, performed trials, sentence overlap, target freshness, transfer
  behavior, and one-time performance remain unavailable.
- Loop 28 defines a falsifiable strict zero-shot rule, not a transfer result.
  Brain2Qwerty v2's joint and target-finetuned evidence does not establish
  strict unseen-person zero-shot behavior, and one future S25 pass could not
  establish population generalization.
- Loop 29 defines the evidence needed to translate modalities, not a portable
  sensing result. Brain2Qwerty v2's 76/153/230-channel cryogenic ablations are
  not OPM-MEG or EEG device qualification, and repeated at-home EEG recording
  mechanics are not at-home text decoding.
- Loop 30 defines the evidence needed for a trustworthy replay interaction,
  not a running streaming decoder. A stable partial can be wrong, replay time
  is not capture time, and a localhost label without network and file-exposure
  QA is not a measured privacy result.
- Loop 31 defines the evidence needed for sensor-signal dependence, not a
  neural advantage result. Language gain and conditional Neuro Token gain stay
  separate, and brain-specific attribution remains blocked on Loop 35 even if
  the future local matrix passes.
- Loop 32 defines the evidence needed for honest one-person calibration, not a
  calibrated result. The 32-parameter adapter is a planning recommendation,
  unlabeled adaptation remains transductive rather than zero-shot, and one
  future participant could not establish population or device generalization.

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

Loop 24 used one numerical thread and one sequential worker at a time, 48
target-free items per partition, 455,472 working-array bytes, 262,822 total
generated bytes, and at most 222,248,960 worker-RSS bytes. It stayed below every
storage, memory, concurrency, and access cap but took 65.154951 seconds against
the frozen 60-second runtime cap. Seed 2401 is consumed; seed 2402 remains
unopened and closed. Real data, targets, training, energy, RW3, and hardware
remain outside the gate.

Generated artifacts belong in ignored `cache/` or `outputs/`, not in Git.

## Project Status And Roadmap

The original numbered development sequence has reached:

- Loops 1-12: completed;
- Loop 13: parked after measured lazy-backend gate;
- Loops 14-22: completed at their exact proof boundaries;
- Loop 23: parked after the frozen synthetic decoder test missed its primary
  threshold;
- Loop 23.5: completed as a supervised synthetic calibration mechanism;
- Loop 24: parked after one registered target-free selection at implementation
  commit `3a5dc0b`; float32 is retained, no replacement or storage-only candidate
  passed, seed 2401 is consumed, seed 2402 qualification stayed unopened, and
  runtime was 65.154951 seconds versus the 60-second cap;
- Loops 25-44: a primary-source-informed tranche spans causal
  evidence, translation/generalization, reliability/confounds,
  reproducibility/local deployment, and live translation/release. Loop 25 is
  `Amended Preregistration` at `b6b92d8` with a hash-bound v1 request awaiting
  explicit authorization; v0 is historical and was never authorized. Loop 26
  planning research is complete at `03605c5`, while the experiment remains
  `Not Started`. Loop 27 planning research is green at `b3d61b6` and selects
  S25 metadata, while preregistration and acquisition remain blocked. Loop 28
  planning research defines the strict zero-shot final-only rule while its
  experiment remains `Not Started`. Loop 29 planning research at green commit
  `f5fc740` defines a local-first EEG lane, a partner/lab OPM-MEG lane, and a bounded 5-10 GB
  capacity envelope while its experiment remains `Not Started`. Loop 30
  planning research now freezes the local target-
  free replay interaction boundary while its experiment remains `Not Started`.
  Loop 31 planning research defines a 10-condition encoder and contingent
  5-condition LLM attribution firewall while its experiment remains `Not
  Started`. Loop 32 planning research defines a causal 32-parameter adapter,
  four calibration modes, and physically separate calibration/selection/final
  evidence while its experiment remains `Not Started`. Loop 33 planning
  research defines the bounded `8, 16, 24, 32, 44, 55` unique-sentence curve,
  one target-blind shared validation event, and no acquisition now while its
  experiment remains `Not Started`; Loop 34 planning research defines the
  three-way confidence, abstention, and revision firewall while its experiment
  remains `Not Started` and confidence is unavailable; Loops 35-44 remain `Not
  Started`. All 20
  execution flags are false. Loop 24's parked result does not authorize Loop
  25, and later research cannot authorize an earlier or later experiment.

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
| [docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md) | six-item identifiability limit, causal candidate repair, parameter-matched comparator, control design, and exact no-execution boundary |
| [registries/loop26_research_boundary.v0.json](registries/loop26_research_boundary.v0.json) | machine-readable Loop 26 planning evidence, recommendations, zero access counters, and 14 false authorization fields |
| [docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md) | official metadata ranking, selected S25 MEG candidate, exact bytes/hashes, target-isolation design, and preregistration blockers |
| [registries/loop27_research_boundary.v0.json](registries/loop27_research_boundary.v0.json) | machine-readable Loop 27 candidate identity, unavailable fields, resource boundary, zero payload access, and 18 false authorization fields |
| [docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md) | v2 transfer audit, T0-T3 taxonomy, strict zero-shot/transductive distinction, final-only rule, and calibrated-design boundary |
| [registries/loop28_research_boundary.v0.json](registries/loop28_research_boundary.v0.json) | machine-readable Loop 28 estimand, controls, access order, resource limits, dependencies, zero protected access, and 21 false authorization fields |
| [docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md) | primary-source OPM-MEG and EEG review, two-lane portability decision, storage allocation, qualification ladder, and result-oriented real-data path |
| [registries/loop29_research_boundary.v0.json](registries/loop29_research_boundary.v0.json) | machine-readable modality requirements, device gates, storage ceilings, source bindings, zero protected access, and 24 false authorization fields |
| [docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md) | primary-source calibration taxonomy, 32-parameter adapter recommendation, physical split and burden contract, access order, controls, and one-time final gate |
| [registries/loop32_research_boundary.v0.json](registries/loop32_research_boundary.v0.json) | machine-readable four-mode calibration boundary, six-point budget, 32/16/48 partition floors, zero protected operations, and 22 false authorization fields |
| [docs/REAL_DATA_VALIDATION_2026-07-10.md](docs/REAL_DATA_VALIDATION_2026-07-10.md) | S21 alignment, session, and upstream audit |
| [docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md](docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md) | real EEG bridge and negative classifier result |
| [docs/LOOP_20_NEUROTOKEN_CACHE_V0.md](docs/LOOP_20_NEUROTOKEN_CACHE_V0.md) | NeuroTokenCache schema and synthetic interface proof |
| [docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md) | PyTorch precision, timing, memory, and energy primary-source review |
| [docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md](docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md) | frozen Loop 24 candidates, fresh fixtures, measurements, thresholds, caps, and decision language |
| [registries/local_precision_runtime_contract.v0.json](registries/local_precision_runtime_contract.v0.json) | machine-readable Loop 24 identities, schedules, refusals, access rules, and false authorization flags |
| [docs/LOOP_24_AUTHORIZATION_DECISION.md](docs/LOOP_24_AUTHORIZATION_DECISION.md) | scope-narrowed Loop 24 authorization, execution order, zero-runtime boundary, and real-data/training routing |
| [registries/loop24_authorization_decision.v0.json](registries/loop24_authorization_decision.v0.json) | hash-bound authorization record for the consumed target-free Loop 24 execution; every data/training/RW3/device flag remains false |
| [docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md](docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md) | measured float32/float16/qint8 result, unopened qualification proof, resources, access ledger, and parked decision |
| [docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md](docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md) | original official Brain2Qwerty, MNE, SciPy, and local-pipeline audit separating offline preprocessing from causal proof |
| [docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md](docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md) | immutable historical v0 registration, superseded before authorization |
| [registries/causal_preprocessing_contract.v0.json](registries/causal_preprocessing_contract.v0.json) | immutable historical v0 machine contract; never authorized |
| [docs/LOOP_25_ANTI_ALIAS_AUDIT.md](docs/LOOP_25_ANTI_ALIAS_AUDIT.md) | pinned Brain2Qwerty-to-NeuralSet-to-MNE execution trace and full folding-band defect analysis |
| [docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md](docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md) | current v1 dedicated anti-alias design, static pre-seed gate, timing semantics, and supersession boundary |
| [registries/causal_preprocessing_contract.v1.json](registries/causal_preprocessing_contract.v1.json) | current machine-readable Loop 25 amendment with every execution flag false |
| [docs/LOOP_25_AUTHORIZATION_PACKET_V1.md](docs/LOOP_25_AUTHORIZATION_PACKET_V1.md) | current exact bounded decision language and the work still forbidden even after authorization |
| [registries/loop25_authorization_request.v1.json](registries/loop25_authorization_request.v1.json) | green-amendment-bound replacement request; currently `authorized_now: false` |
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

Precision or local-runtime contributions should begin by reviewing the parked
Loop 24 closeout and proposing a fresh hash-bound protocol. A benchmark pull
request is not authorization to retune seed 2401 or open seed 2402, smaller
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
