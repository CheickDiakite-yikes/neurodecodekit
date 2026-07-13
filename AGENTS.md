# AGENTS.md — Codex / Agent Instructions

You are continuing **NeuroDecodeKit**, a research/build starter for making Brain2Qwerty-style neural language decoding accessible.

## Product principle

Keep the core loop brutally simple:

```text
manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo
```

Do not optimize for impressiveness before reproducibility. A boring baseline that everyone can run is more valuable than a clever architecture no one can validate.

## Hard constraints

1. **Do not download the full SpanishBCBL dataset by default.** It is roughly 262GB. All code must default to dry-run, listing, manifesting, or tiny selective patterns.
2. **Do not make clinical claims.** This is a research/dev kit for non-invasive decoding experiments, not a medical product.
3. **Respect CC BY-NC 4.0 constraints.** Treat the Brain2Qwerty code and SpanishBCBL data as noncommercial unless a separate license exists.
4. **Keep heavy dependencies optional.** The base repo should run tests without MNE, Torch, Zarr, or Hugging Face. Put heavy imports inside functions and raise helpful install messages.
5. **Prefer inspectable data formats.** Manifests should be JSONL/Parquet-friendly. Metadata should be easy to diff. Cache format should be chunked and compressed once Zarr is implemented.
6. **Measure complexity.** Every new pipeline stage should report storage footprint, runtime, and a human-readable summary.
7. **Avoid LLM-only illusions.** Always keep a language-model-only baseline so we do not accidentally credit the neural decoder for autocomplete.

## Immediate next task

The first 20-loop roadmap is complete except for the deliberately parked Loop
13 backend. Post-roadmap Loops 21 and 22 validate bounded synthetic causal
replay and one tiny learned motif encoder. Loop 23 implemented the frozen
language-model-free streaming CTC gate, but its consumed test reached only 5/8
exact sequences against the preregistered 6/8 threshold. It is parked, while
Loop 23.5 is complete as a separate supervised synthetic calibration gate.
Loop 24 was preregistered at `186bb6f`, authorized separately at `b7738c7`,
and implemented at `3a5dc0b` before its registered target-free execution:

```bash
cat docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md
cat docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md
cat docs/LOOP_24_AUTHORIZATION_DECISION.md
cat docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md
python -m json.tool registries/local_precision_runtime_contract.v0.json >/dev/null
python -m json.tool registries/loop24_authorization_decision.v0.json >/dev/null
```

All 12 balanced selection rounds completed over 990 frames. Float16 preserved
every exact decoder behavior and numerical tolerance but was `1.169950x` the
float32 producer latency and `1.087904x` the full-pipeline latency. QNNPACK
qint8 used `47.10%` of the float32 numeric payload but changed behavior and was
`2.784595x`/`1.812123x` the producer/full latency. No candidate qualified, seed
2402 remained physically unopened, and the final gate parked because
65.154951 seconds exceeded the frozen 60-second cap. Retain float32. Seed 2401
is consumed; do not tune or rerun Loop 24, and do not repurpose seed 2402.

Loop 25 causal preprocessing was preregistered at commit `a36d97b`, then
superseded before authorization by the anti-alias amendment at green commit
`b6b92d8`. The v0 files remain immutable history, but their request and exact
sentence are no longer actionable. The current v1 packet adds a dedicated
causal anti-alias stage, a 65,537-point 0-500 Hz response gate, 23 alias probes,
45 refusals, 23 counters, and a static design gate before either fixture array
can open. Its replacement request keeps every `authorized_now` field false:

```bash
cat docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md
cat docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md
cat docs/LOOP_25_ANTI_ALIAS_AUDIT.md
cat docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md
cat docs/LOOP_25_AUTHORIZATION_PACKET_V1.md
python -m json.tool registries/causal_preprocessing_contract.v0.json >/dev/null
python -m json.tool registries/causal_preprocessing_contract.v1.json >/dev/null
python -m json.tool registries/loop25_authorization_request.v1.json >/dev/null
```

The next numbered decision is to authorize only v1 using its exact sentence,
amend it again, or hold. Packet preparation, roadmap approval, and general
continuation are not authorization. Do not create a Loop 25 fixture, filter
coefficients, transform, CLI, runtime, cache read, model operation, or generated
payload until a separate v1 authorization-only record is tested, committed,
pushed, and remotely green. Even then, the static filter gate must pass before
seed 2501 opens; seed 2502 stays conditional. Both remain unopened. Real or
consumed data, targets, labels, text, model inference, training, new
architectures, energy measurement, RW3, streams, devices, hardware, and Loops
26-44 execution remain unauthorized.

Loop 26 planning research is complete at commit `03605c5`, but the experiment
remains `Not Started` and has no preregistration or authorization sentence:

```bash
cat docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop26_research_boundary.v0.json >/dev/null
```

The note identifies a 2,908-parameter causal candidate recommendation, a
2,884-parameter linear signal comparator, the strict 55/6/5 source split, and
the 64 exact paired sign assignments available from six reserved validation
sentences. All 14 `authorized_now` fields are false. No real-cache content,
target, model, checkpoint, training, validation prediction, source test, or
session-2 evidence was opened. Do not turn this planning result into a Loop 26
implementation, validation run, neural result, or authorization shortcut.

Loop 27 planning research is complete at green commit `b3d61b6`, but no
preregistration or acquisition request exists:

```bash
cat docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop27_research_boundary.v0.json >/dev/null
```

The pinned metadata selector examined 315 MEG entries, found 23 strict
single-FIF/log pairs and 16 eligible pairs, and selected S25 session 2 block 2
as the smallest eligible same-modality/task candidate: exactly two files and
1,009,939,983 bytes under a 1 GiB future cap. S23 is ineligible under the
official metallic-implant exclusion; S20 remains a separate EEG cohort. All 18
Loop 27 authorization fields are false. Do not download, hash the local S25 MAT
payload, inspect a FIF header, read signal/targets, substitute a backup, or
prepare Loop 28 execution from this research result.

Loop 28 planning research now defines the transfer taxonomy and the missing
final-only decision recommendation, but the experiment remains `Not Started`:

```bash
cat docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop28_research_boundary.v0.json >/dev/null
```

The selected future claim is T2 strict unseen-person zero-shot on S25 with
zero candidate fit or calibration rows. A future pass requires at least 48
unique final rows, at least 0.05 absolute macro sentence-CER improvement over
the frozen source-train-only prior, `p <= 0.05` from 65,535 deterministic paired
assignments plus observed, and strict wins over zero-signal, channel-
derangement, and time-displacement controls. All 21 `authorized_now` fields are
false. The rule is planning research, not a Loop 27 preregistration or Loop 28
authorization. Calibrated transfer requires a different physically separated
design and can never be relabeled as zero-shot.

Loop 29 planning research is complete at green commit `f5fc740`, but its
portable-sensing experiment remains `Not Started` and every execution decision
remains separate:

```bash
cat docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop29_research_boundary.v0.json >/dev/null
```

The research selects a two-lane direction: scalp EEG is the immediate local-
first accessibility lane, OPM-MEG is a same-modality partner/lab lane, and
cryogenic MEG remains the scientific reference. It freezes 15 cross-modality
requirements, four modality profiles, six qualification levels, and an exact
storage envelope of 5,000,000,000 preferred and 10,000,000,000 absolute
incremental bytes. The selected future S20 EEG and S25 MEG bundles total
1,106,030,247 bytes, but zero bytes were downloaded. All 24 `authorized_now`
fields are false. Storage capacity is not download permission; no device is
selected, purchased, connected, or recommended, and no real header, signal,
target, model, training, SDK, stream, partner session, or hardware operation
occurred. Home EEG recording feasibility is not home text decoding, and the
Brain2Qwerty v2 cryogenic channel ablation is not OPM-MEG or EEG evidence.

Loop 30 planning research is complete on the current branch, but its local
streaming experiment remains `Not Started` and no target-free trace, UI,
server, or browser run exists:

```bash
cat docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop30_research_boundary.v0.json >/dev/null
```

The future surface is a loopback-only target-free replay inspector, not a live
decoder. The boundary freezes four source modes, a 30-field trace contract,
nine clock domains, six latency claim levels, 18 future requirements, 30
refusals, and 30 false `authorized_now` fields. A future run must use one new
target-free synthetic trace after separate authorization; consumed Loop 23/24
artifacts, S7/S21, targets, models, streams, SDKs, devices, and hardware remain
closed. Stability is not correctness or confidence, replay scheduling is not
capture latency, and a future Loop 30 authorization cannot authorize RW3 or a
live source.

Loop 31 planning research is complete while its neural-contribution experiment
remains `Not Started`:

```bash
cat docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop31_research_boundary.v0.json >/dev/null
```

The research freezes a future 10-condition local encoder attribution matrix, a
separately gated 5-condition language-model and Neuro Token extension, 18
future requirements, 24 refusals, and 19 false `authorized_now` fields. A
future clean encoder result can establish at most sensor-signal dependence for
the exact source slice. Brain-specific neural contribution remains unavailable
until Loop 35 excludes peripheral and task-locked shortcuts. No cache, target,
checkpoint, model, training, validation, language model, Neuro Token, S20,
S25, stream, device, or hardware operation occurred or is authorized.

Loop 32 planning research is complete while its fresh-person calibration
experiment remains `Not Started`:

```bash
cat docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop32_research_boundary.v0.json >/dev/null
```

The research recommends one pointwise causal 32-parameter hidden affine
adapter, four noninterchangeable calibration modes, nested sentence budgets of
`0, 2, 4, 8, 16, 32`, and physically separate 32-row calibration, 16-row
selection, and 48-row final floors. It freezes 20 future requirements, 26
refusals, and 22 false `authorized_now` fields. No candidate or mode is
selected; S25 remains final-only. Participant/cache/signal/label/target access,
checkpoint/model/control runs, adapter fitting, parameter updates, training,
final evaluation, downloads, streams, devices, and hardware remain
unauthorized. Calibrated performance may never be relabeled zero-shot.

Loop 33 planning research is complete while its bounded data-scaling
experiment remains `Not Started`:

```bash
cat docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop33_research_boundary.v0.json >/dev/null
```

The research recommends strictly nested unique-sentence prefixes of
`8, 16, 24, 32, 44, 55`, at most three optimization seeds and 18 candidate
fits, size-matched no-signal priors, and one target-blind shared Loop 26/31/33
validation event. Every prediction must hash-freeze before all six validation
targets open once. Current metadata supports no physical-repetition lane;
duplicated arrays are not new acquisitions. Twenty future gates, 30 refusals,
and 23 false `authorized_now` fields are machine checked. Acquisition is not
recommended now, and all protected/model/training/scoring work is unauthorized.

Loop 34 planning research is complete while its confidence, abstention, and
revision experiment remains `Not Started` and confidence remains unavailable:

```bash
cat docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop34_research_boundary.v0.json >/dev/null
```

The research separates seven confidence semantics, eight score/control roles,
and recommended fresh synthetic calibration/selection/final counts of
`128/64/256`. The six real source-validation rows remain reserved for the
shared Loop 26/31/33 event and cannot fit and independently qualify Loop 34.
Twenty future gates, 30 refusals, and 26 false `authorized_now` fields are
machine checked. No fixture, feature, confidence fit, target open, scoring,
product-visible confidence, real-data read, or download is authorized.

Loop 35 planning research is complete while its peripheral-confound experiment
remains `Not Started` and unauthorized:

```bash
cat docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop35_research_boundary.v0.json >/dev/null
```

The boundary freezes ten confound classes, nine future synchronized stream
classes, a 13-condition comparison matrix, three separately authorized stages,
24 future gates, 32 refusals, and 31 false `authorized_now` fields. Existing
S21/S7 evidence lacks a fresh complete synchronized peripheral-control set.
Even a future local pass can establish at most incremental brain-sensor
information beyond recorded controls, not absolute brain origin. No synthetic
fixture, EOG/EMG/gaze/motion/audio acquisition, protected-data read, model,
training, scoring, no-keypress study, device, or hardware work is authorized.

Loop 36 planning research is complete while its geometry/reference experiment
remains `Not Started` and unauthorized:

```bash
cat docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md
python -m json.tool registries/loop36_research_boundary.v0.json >/dev/null
```

The boundary freezes six representation layers, five modality profiles, a
24-field future channel record, 12 operation classes, 16 fixture families, 22
gates, 30 refusals, and 29 false `authorized_now` fields. It permits a future
real-header result to claim at most declared metadata compatibility. Unknown
names, units, frames, orientations, references, compensation, or missingness
remain unavailable. No fixture, header/signal read, transform, unit conversion,
rereference, interpolation, model, training, device, or hardware operation is
authorized.

The parallel practice track has closed RW1 and RW2 at their exact synthetic
proof boundaries. RW3's replay/live-source-equivalence protocol is frozen at
commit `c3d1f01`, before any adapter, source chunk, fixture, socket, board, or
XDF operation:

```bash
cat docs/RW3_PRIMARY_SOURCE_RESEARCH.md
cat docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md
cat docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md
python -m json.tool registries/replay_equivalence_contract.v0.json >/dev/null
python -m json.tool registries/rw3_stage_a_authorization_request.v0.json >/dev/null
```

Commit `163ff2f` prepares a hash-bound Stage A authorization packet and machine
request. Both explicitly say `authorized_now: false`; preparing or reviewing
them is not authorization. RW3 Stage A and Loop 24 are two independent
decisions: the completed Loop 24 run cannot authorize RW3. Do not implement RW3
from this instruction. BrainFlow, LSL, PyXDF, sockets, live sources, device
discovery, hardware, real recordings, consumed caches, targets, and training
remain unauthorized. No further Loop 24 model operation is authorized. Keep
S7/S21 evidence and seeds 2203, 2303, 2353, and 2401 frozen; keep 2402
unopened. Any future real-data acquisition remains dry-run by default and
requires explicit byte caps plus `--execute`.

A primary-source-informed next tranche defines Loops 25-44 in
`docs/LOOPS_25_44_ROADMAP.md` and
`registries/next_20_loops.v0.json`. It contains exactly 20 planning rows across
five phases, with detailed controls, metrics, stop rules, resource caps,
dependencies, and source bindings. Loop 25 is `Amended Preregistration` with
`execution_authorized: false`; Loop 26 has completed planning research while
its experiment remains `Not Started`; Loop 27 has selected S25 in metadata
while preregistration remains blocked; Loop 28 planning research defines a T2
strict zero-shot rule while its experiment remains `Not Started`; Loop 29
planning research defines separate EEG and OPM-MEG pathways while its
experiment remains `Not Started`; Loop 30 planning research defines the local
target-free replay boundary while its experiment remains `Not Started`; Loop
31 planning research defines the sensor-signal attribution firewall while its
experiment remains `Not Started`; Loop 32 planning research defines the
32-parameter fresh-person calibration boundary while its experiment remains
`Not Started`; Loop 33 planning research defines the bounded
`8, 16, 24, 32, 44, 55` curve and shared-validation order while its experiment
remains `Not Started`; Loop 34 planning research defines a three-way confidence
firewall while its experiment remains `Not Started`; Loop 35 planning research
defines a staged peripheral-confound firewall while its experiment remains
`Not Started`; Loop 36 planning research defines the geometry/reference
identity firewall while its experiment remains `Not Started`; Loops 37-44
remain `Not Started`. All 20
execution flags are false. This roadmap does not
reopen Loop 24, authorize RW3, or permit a Loop 25-44 fixture, download, data
read, model run, training run, stream, board, or hardware operation. A broad
request to continue toward Loop 44 is a goal, not a substitute for each frozen
authorization boundary.

## Acceptance criteria for next PR

- `python -m unittest discover -s tests` passes.
- CLI has useful `--help` text.
- New numerical or model dependencies remain optional.
- No full-dataset download can happen accidentally.
- The RW3 JSON contract, authorization request, and ten dependency-free
  invariant tests remain exact.
- The Loop 24 JSON contract and nine dependency-free invariants remain exact;
  its immutable execution flags remain false, while the separate authorization
  and measured closeout preserve their hash-bound sequence.
- The Loops 25-44 roadmap contains exact IDs 25 through 44, five phases of four
  loops, row-level primary-source bindings, nine dependency-free invariants,
  and 20 false execution flags.
- The Loop 25 v0 registration remains byte-exact at `a36d97b`; the superseding
  v1 amendment remains exact at `b6b92d8` with a dedicated anti-alias stage,
  65,537 response points, 23 alias probes, seven schedules, six signal
  families, ten resume cuts, three future-mutation cuts, 45 refusal IDs, 23
  access counters, and 11 amendment invariants.
- The current Loop 25 v1 authorization request remains hash-bound to the green
  amendment, every `authorized_now` field remains false, and the v0 request is
  visibly historical and unauthorized.
- The Loop 26 planning registry remains exact with 14 false authorization
  fields, a 55/6/5 split, six validation items, 64 exact paired assignments,
  2,908/2,884-parameter recommendations, and no preregistration or runtime.
- The Loop 27 planning registry remains exact with 18 false authorization
  fields, 315 MEG metadata entries, 23 strict pairs, 16 eligible pairs, the
  two-file 1,009,939,983-byte S25 selection, official S23/S20 boundaries, and
  no preregistration, request, download, payload hash, header, signal, or target
  access.
- The Loop 28 planning registry remains exact with 21 false authorization
  fields, four noninterchangeable transfer levels, zero S25 fit/calibration
  rows, the 48-row/0.05-CER/65,535-assignment rule, four required comparators,
  physically separate calibrated-transfer requirements, and zero protected
  access.
- The Loop 29 planning registry remains exact with 24 false authorization
  fields, 15 cross-modality requirements, four modality profiles, six
  qualification levels, 12 future device-packet gates, zero protected access,
  and no preregistration, runtime, device selection, download, or generated
  payload. Its 5,000,000,000-byte preferred and 10,000,000,000-byte absolute
  storage envelope is capacity only; the selected S20 plus S25 future bundles
  total exactly 1,106,030,247 bytes.
- The Loop 30 planning registry remains exact with 30 false authorization
  fields, four source modes, a 30-field target-free trace schema, nine clock
  domains, six latency levels, 18 future requirements, 30 refusal IDs, fixed
  loopback/privacy/accessibility/browser-QA settings, zero protected access,
  and no preregistration, seed, fixture, UI, server, browser run, model,
  stream, live source, or generated experiment payload.
- The Loop 31 planning registry remains exact with 19 false authorization
  fields, a 10-condition encoder matrix, a contingent 5-condition LLM matrix,
  18 future requirements, 24 refusal IDs, and a Loop 35 ceiling on
  brain-specific attribution; no protected input, model, training, validation,
  LLM, Neuro Token, or experiment payload exists.
- The Loop 32 planning registry remains exact with 22 false authorization
  fields, four calibration modes, six nested budgets, one 32-parameter adapter
  recommendation, 32/16/48 physical partition floors, six conditions, 20
  future requirements, 26 refusal IDs, and zero candidate, protected access,
  model, adapter-fit, training, or evaluation operation.
- The Loop 33 planning registry remains exact with 23 false authorization
  fields, six nested `8, 16, 24, 32, 44, 55` prefixes, at most three seeds and
  18 candidate fits, one shared six-target open, four conditions, 20 future
  requirements, 30 refusals, no physical-repetition lane, no acquisition
  recommendation, and zero protected/model/training/scoring operations.
- The Loop 34 planning registry remains exact with 26 false authorization
  fields, seven confidence semantics, eight score/control roles, recommended
  `128/64/256` fresh synthetic partitions, 20 future requirements, 30
  refusals, an explicit unavailable state, no eligible existing real confidence
  partition, and zero fixture/fit/target/scoring/product-confidence operations.
- The Loop 35 planning registry remains exact with 31 false authorization
  fields, ten confound classes, nine future synchronized stream classes, 13
  conditions, three separately authorized stages, 24 future gates, and 32
  refusals. Missing real peripheral controls fail closed; the maximum future
  local claim is incremental brain-sensor information beyond recorded controls,
  not absolute brain origin.
- The Loop 36 planning registry remains exact with 29 false authorization
  fields, six representation layers, five modality profiles, a 24-field channel
  record, 12 operation classes, 16 fixture families, 22 gates, and 30 refusals.
  Metadata compatibility remains separate from signal transforms, model
  transfer, device equivalence, and scientific claims.
- No RW3 implementation, fixture, CLI, optional import, socket, stream, board,
  XDF operation, real-data read, target access, model run, or training run exists.
- The ignored Loop 24 fixture and report remain outside Git. Selection seed
  2401 is not rerun or tuned, qualification seed 2402 remains unopened, and
  real/consumed data, targets, energy, training, and RW3 counters remain zero.
- No Loop 25-44 runtime, fixture, filter-design run, numerical preprocessing,
  data/cache read, model run, training run, validation open, or generated
  payload exists without its own preregistration and authorization.
- All public docs agree that the registration freezes five schedules, 18 future
  fixture families, 30 refusal IDs, and four separately authorized stages, and
  that the Stage A packet proposes 90 future cases without authorizing them.
- Stage A remains a separate authorization decision and cannot imply Stage B-D,
  physical-device qualification, useful signal, decoding, or real-time behavior.
- Loop 24 remains a parked target-free local result and establishes no speedup,
  integer-only execution, retained neural accuracy, end-to-end text latency,
  cross-device energy efficiency, or portable-hardware behavior.
- Loop 25 remains an amended preregistered mechanics proposal and establishes
  no filter result, official preprocessing equivalence, neural information,
  decoding, latency, transfer, or device result.
- Resource, privacy, access, timestamp, anomaly, hash, and claim boundaries stay
  explicit and machine-checkable.

## Style

- Small functions, explicit names, low magic.
- Use dataclasses for records.
- Use pathlib over string path manipulation.
- Pure-Python first; optional NumPy/MNE/Torch/Zarr only where needed.
- Include tests for each assumption about filenames, metrics, and shape transformations.
