# Codex Handoff - NeuroDecodeKit

> Current handoff, 2026-07-12: Loops 1-12, 14-22, and 23.5 are complete; Loops
> 13, 23, and 24 are parked after measured gates. Two S21 MEG sessions support strict
> sentence-text and same-subject session protocols, but the fixed tiny CTC has
> no reliable neural advantage and loses its cross-session comparison to the
> no-signal prior. One bounded S7 EEG bridge is trigger/cache validated, but its
> nearest-centroid result is also worse than its train-only prior. Loop 20 adds
> a target-isolated NeuroTokenCache interface; Loop 21 proves schedule-invariant
> causal frame production; Loop 22 trains one 1,130-parameter synthetic causal
> producer and consumes seed 2203. Loop 23 implements a language-model-free
> greedy and width-8 prefix CTC decoder under a fresh physical split. Registered
> validation passes at CER 0.0182 and 7/8 exact, opening seed 2303 once. Frozen
> test CER is 0.0545 with all repeated pairs recovered, but exact accuracy is
> only 5/8 against a 6/8 threshold. Every failure is the correct target plus one
> false tail symbol; prefix and greedy agree. The test is consumed, the branch
> is parked, and no post-test trimming or tuning is allowed. Loop 23.5 then
> passes a separately preregistered fresh synthetic calibration gate: one
> train-frame-fitted blank intercept takes validation from 6/16 to 16/16 exact
> and the once-opened seed-2353 test from 7/16 to 16/16 exact, with zero CER,
> nine test corrections, no regressions, and all replay/resource/access gates
> passing. Seed 2353 is consumed. Loop 24 was preregistered at `186bb6f`,
> authorized at `b7738c7`, and implemented at `3a5dc0b` before one registered
> target-free selection. All 12 balanced rounds complete over 990 frames.
> Float16 preserves exact behavior but is `1.170x` the float32 producer latency
> and `1.088x` the full latency. QNNPACK qint8 uses `47.1%` of the float32
> payload but changes decoder behavior and is `2.785x`/`1.812x` the producer/
> full latency. No candidate qualifies; seed 2402 stays physically unopened.
> Runtime is 65.154951 seconds against the frozen 60-second cap, so Loop 24 is
> parked and float32 retained. Seed 2401 is consumed. No rerun or post-result
> tuning is authorized. Real/consumed data, targets, labels, text, training,
> new models, energy measurement, RW3, devices, and hardware remain unauthorized.
> A primary-source-informed Loops 25-44 roadmap is now frozen as planning only:
> 20 contiguous rows, five phases, detailed controls/metrics/stop rules, one-
> thread and byte caps, row-level sources, and 20 false execution flags. Loop 25
> causal preprocessing was registered at `a36d97b`, then superseded before
> authorization by anti-alias amendment v1 at green commit `b6b92d8`. The
> current target-free scope adds a dedicated causal elliptic anti-alias SOS,
> 65,537 response points, 23 alias probes, 45 refusal IDs, and 23 access counters
> while retaining seeds 2501/2502, seven schedules, ten resume cuts, and three
> future-mutation cuts. Its replacement request still says
> `authorized_now: false`; both seeds are unopened and no coefficient, fixture,
> transform, partition, CLI, or runtime exists. Loop 26 planning research is
> complete at `03605c5`, while its experiment remains `Not Started`: the note
> narrows the future gate to a 2,908-parameter causal recommendation, a
> 2,884-parameter linear comparator, six controls, and all 64 exact paired sign
> assignments over the reserved six-row validation slice. All 14 authorization
> fields remain false and every protected access counter is zero. Loops 27-44
> remain `Not Started`. This does not reopen Loop 24 or authorize RW3, data,
> targets, models, validation, training, or hardware.
> In parallel, RW0 closes a primary-source Real-World Practice research gate
> with eight dataset records, 13 device records, a local BYO Neurodata
> contract, and one exact S20 EEG dry-run packet. RW1 now closes a
> dependency-free level-0 metadata gate for BrainVision, EDF/EDF+, BDF,
> EEGLAB, FIF, and BIDS synthetic fixtures. Its 532-byte roundtrip writes
> 11,545 bytes with zero binary/raw/cache/target/model/training/network reads.
> RW2 now closes at exact synthetic compatibility level 2. Forty generated
> fixtures cover six format families: 38 readable sources pass and two
> malformed/unsafe layouts refuse exactly. One measured FIF report selects nine
> channels and three windows, returns 11,520 values, writes 76,592 bytes in
> 3.839168 seconds, and records 150,749,184-byte peak RSS with zero
> real/cache/target/model/training/network access. RW3's replay/live-source
> protocol is frozen at commit `c3d1f01`: five schedules, 18 future fixture
> families, 30 exact refusal IDs, four separately gated adapter stages, and
> seven dependency-free contract tests. Commit `163ff2f` adds a hash-bound
> Stage A decision packet, three authorization-binding tests, and a proposed
> 90-case matrix. Its machine request says `authorized_now: false`. No source
> chunk, fixture, CLI,
> BrainFlow/LSL/PyXDF import, socket, stream, board, or XDF operation occurred.
> Stage A remains unapproved. No real recording, consumed cache, S20
> download/read, live source, automatic cleaning, model, or training is
> authorized. The parked Loop 24 result cannot authorize RW3 Stage A.
> There is no demonstrated neural advantage, unseen-person, useful EEG,
> real-neural sequence decoder, end-to-end real-time, portable-hardware,
> arbitrary-thought, or clinical claim. See
> `docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`.

## State of the repo

This repo is a starter scaffold with working pure-Python components:

- CER/WER metrics
- simple keyboard-distance metric
- SpanishBCBL-style manifest parser
- safe tiny-selection JSON creation
- dry-run-by-default selective download command
- optional Hugging Face access helpers
- synthetic shard generator
- real `.fif` + `.mat` event-window extraction scaffold
- size-aware capped tiny-selection and dry-run download planning
- B2Q-mini NPZ cache schema v0 loader and metadata sidecar writer
- continuous sentence-cache schema v0 and real S21 extraction
- optional tiny CTC with synthetic proof, strict real sentence-text evaluation,
  and mandatory no-brain comparator
- isolated 100/50/25 Hz sampling-rate resource sweep
- geometry-aware 102-magnetometer extraction metadata
- bounded spatial/variance/random/file-order channel-subset sweep
- versioned packed signal-representation cache and standard/packed auto-loader
- bounded float32/float16/BF16/qint16/qint8 storage-fidelity sweep
- isolated standard/packed NPZ full/partial access gate with exact hashes and
  explicit lazy-backend revisit thresholds
- signal-free deterministic split membership, duplicate-row, capability, and
  preprocessing fit-scope audit
- train-row-only robust scaling with protocol/membership hash binding
- signal-free strict-split sentence prior and paired uncertainty comparison
- session-aware split-FIFF selection with pinned Hub revision and one-worker download
- nonempty-MAT-trial mapping with preserved skipped trial IDs and timing audit
- frozen source-train scaler application with cache/statistic hash validation
- same-subject cross-session tiny CTC with source holdouts explicitly reserved
- synthetic-only robust channel-affine adapter gate with frozen selection/holdout
- multi-view tiny CTC evaluation with one frozen model across target views
- six-size, three-seed synthetic calibration curve with independent calibration,
  channel-mixing, and within-row drift stress families
- artifact-backed local Gradio evidence console with audit-only startup gate,
  aggregate-only real results, provenance hashes, and responsive browser QA
- versioned artifact-only report cards with source/config hashes, completeness
  flags, cohort-local ranking, deterministic JSON/Markdown/CSV, and CLI table
- pinned metadata-only EEG bridge gate with complete-triplet/log validation
- lazy BrainVision plus MAT-trigger extraction into B2Q-mini cache v0
- exact key-label paired comparison against a same-split train-only prior
- modality-aware NeuroTokenCache v0 with continuous time-major embeddings,
  masks/timestamps, source geometry availability, strict split/source hashes,
  and explicit asynchronous/causal/latency distinctions
- deterministic target-free synthetic embedding producer with item/token/byte
  caps, collision refusal, create/inspect CLI, exact payload replay, and
  access-tracked exclusion of every source target member
- bounded causal mock frame stream with zero look-ahead, explicit
  drop-incomplete flush, global sample timestamps, and cap refusal
- five-schedule causal replay gate with bitwise stream invariance, declared
  Loop 20 floating compatibility tolerance, scheduling-delay/compute-RTF
  separation, selective signal-only NPZ access, and no decoder
- physically separate hash-bound synthetic motif train/validation/test fixtures
- optional-Torch 1,130-parameter causal window encoder plus diagnostic motif
  probe, train-only normalization, validation checkpointing, and safe NPZ state
- one-time synthetic test access audit, mandatory prior/zero-signal controls,
  paired item bootstrap, and five-schedule learned-embedding replay
- dependency-free incremental greedy and log-space prefix-beam CTC decoding,
  exhaustive tiny-path oracles, blank/repeat tests, and bounded decoder state
- strict synthetic symbol-stream partitions, target-only train access,
  validation-before-test gating, partial timing/stability metrics, and
  five-schedule frame-indexed decoder replay
- dependency-free one-scalar blank-logit calibration with frame-only fit
  access, separate target-only prior access, paired no-harm/bootstrap metrics,
  exact calibrated/unmodified replay, and one-time frozen-test gating
- implemented Loop 24 local precision/runtime gate with physical target-free
  selection/qualification partitions, exact float32/float16/QNNPACK-qint8
  candidates, balanced isolated timing, backend-profiler proof, strict
  artifact inspection, and a measured park that retains float32 while leaving
  qualification unopened
- versioned primary-source dataset and device compatibility registries with
  separate task/evidence cohorts and explicit unavailable fields
- local-first BYO Neurodata workbench contract with compatibility levels 0-6,
  safe file-family rules, privacy caps, refusal behavior, and replay/live source
  boundaries
- exact unapproved S20 EEG acquisition packet with four files, byte/resource
  caps, target-free split, prior/shuffle controls, and one-time test rules
- dependency-free local recording metadata scanner for BrainVision, EDF/EDF+,
  BDF, EEGLAB, FIF, and BIDS with safe roots, companion validation, hard caps,
  explicit compatibility levels, warnings, and inspectable refusal reports
- deterministic local-intake JSON/Markdown, measured runtime/RSS audit
  sidecar, source/config/registry/artifact hashes, strict reload/tamper checks,
  and zeroed binary/raw/cache/target/model/training/network counters
- frozen RW2 signal-quality contract for six synthetic format adapters with
  explicit reader arguments, bounded windows/arrays/resources, descriptive
  time-domain and Welch PSD metrics, privacy redaction, source no-mutation, and
  exact kill/park/proceed gates
- fixture-backed RW2 implementation with 38 readable and two exact-refusal
  sources, strict RW1/contract binding, six lazy direct-reader adapters,
  deterministic JSON/Markdown/audit artifacts, load/validate/summary APIs,
  malformed/privacy/tamper/collision/cap coverage, and four CLI commands
- frozen RW3 source-chunk and replay-equivalence registration with separate
  raw/corrected/arrival clocks, explicit packet anomalies and resume state,
  five schedules, 18 future target-free fixture families, 30 refusal IDs,
  four sequential adapter stages, resource/access caps, and invariant tests;
  no runtime source-chunk or adapter implementation
- hash-bound RW3 Stage A authorization packet with 90 proposed
  schedule-by-fixture cases, all 30 refusal IDs, exact resource/access caps,
  and an explicit authorization-only commit sequence; authorization remains
  false and no Stage A implementation exists
- open-source collaboration surface with Apache-2.0 license, third-party/data
  boundaries, detailed README, EEG data/hardware contribution paths, security,
  governance, citation, issue forms, pull-request checks, and one-thread CI
- primary-source-informed Loops 25-44 planning contract with five phases,
  acceptance and stop rules, resource/authorization boundaries, row-level
  sources, a dedicated spreadsheet sheet, and dependency-free invariants; Loop
  25 is amended and preregistered while all future-loop execution remains
  unauthorized
- hash-bound Loop 25 v1 causal-preprocessing amendment and decision packet with
  a dedicated anti-alias stage, 65,537 response points, 23 alias probes, seven
  chunk schedules, ten resume cuts, three future-mutation cuts, 45 refusals, 23
  access counters, lower resource caps, and zero runtime operations
- machine-checked Loop 26 planning research with the 55/6/5 source protocol,
  six-item exact-inference ceiling, causal padding repair, 2,884-parameter
  linear comparator, six required controls, 14 false authorization fields, and
  zero protected access; no experiment or model implementation exists
- JSON/Markdown metrics report command
- CLI smoke commands
- unit tests

Two real S21 MEG sessions and MAT logs are alignment, timing, and
sentence-cache validated. Session 1 supports strict unseen-sentence-text
membership; session 2 supports one independent same-subject evaluation. One
real S7 EEG BrainVision recording is trigger/cache validated and has one
negative within-session event comparison. None is a decoder success. Do not
turn these results, a variance ranking, or a geometry proxy into unseen-person
or population generalization.

Current verification after the Loop 26 public closeout: 366 unittests pass with
3 expected skips in 21.53 seconds wall and 575,389,696-byte maximum RSS; pytest
reports 363 passed, 3 skipped, and 170 subtests in 21.44 seconds wall with
584,957,952-byte maximum RSS. The focused Loop 25/26/roadmap boundary has 41
passing tests in at most 0.14 seconds wall and 22,986,752-byte maximum RSS.
Dependency-light Python 3.12 discovery is green at 334 tests with 121 optional
skips in 0.75 seconds wall and 45,170,688-byte maximum RSS. The optional,
pytest, and dependency-light counts are each 13 above the Loop 25 v1 baseline;
the final public-status invariant is one test above the green `03605c5`
research milestone. No Loop 25/26 fixture, coefficient, preprocessing run,
cache/target/validation/model read, training run, network call, RW3 operation,
stream, board, device, or hardware operation occurred. The tracked workbook is
79,856 bytes with SHA-256
`255b51b8d083db92030c389f8d40cf001b256dbe0345748c9120e35b993bdb15`;
all nine sheets render, reload, and pass the formula scan with zero matches.
Loop 26 research commit `03605c5` passed both GitHub CI jobs in run
`29197895836`.

## The north star

Build a developer experience layer for non-invasive neural language decoding:

```text
huge raw neurodata → tiny selected shard → reproducible cache → baseline decoder → honest report
```

This is not primarily a model repo. It is a **research loop repo**.

## Current Next Work

1. **Loop 25 - authorize only the amended v1 target-free gate, amend it again,
   or hold.** Read `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md` and
   `registries/loop25_authorization_request.v1.json`. The amendment is green,
   but `authorized_now` remains false. Any authorization must first become a
   tested, pushed, green v1 authorization-only commit. The static filter gate
   must then pass before seed 2501 opens; no fixture, coefficient, transform,
   partition open, CLI, or runtime can exist from this handoff alone.
2. **RW3 - decide on the prepared Stage A packet only.** Review
   `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` and
   `registries/rw3_stage_a_authorization_request.v0.json`. The request is bound
   to commit `c3d1f01` and its exact contract hash, but `authorized_now` remains
   false. Do not implement Stage A without an explicit user decision followed
   by a pushed authorization-only commit; BrainFlow, LSL, PyXDF, sockets, live
   sources, hardware, and Stages B-D remain later independent gates.
3. **Use Loops 25-44 as the future evidence queue, not blanket authorization.**
   Read `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
   `docs/LOOPS_25_44_ROADMAP.md`, and
   `registries/next_20_loops.v0.json`. For Loop 26, also read
   `docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop26_research_boundary.v0.json`. Its planning research is
   complete, but it has no preregistration, authorization sentence, runtime,
   cache/target open, model, training run, or validation result. Each future
   loop still requires its own preregistration or bounded implementation packet
   before execution.
4. **Keep the GitHub history reviewable.** PR #3 carries the validated Loop
   8-24 evidence stack and is green. Draft PR #4 carries the separately stacked
   Loop 25 v0 history, v1 amendment, and still-false decision packet so
   preregistration and authorization remain auditable. The
   `codex/loop-26-research` branch stacks the planning-only Loop 26 evidence on
   top and must remain independently reviewable. Do not merge until CI, license,
   privacy, history, and proof-boundary review is complete.

RW4 is not next: S20 acquisition remains blocked until explicit approval names
revision `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`, exactly four files, the
128-MiB download cap, 16-MiB output cap, and one-time 44/10/10 protocol.

Loop 23's preregistration and parked result are in
`docs/LOOP_23_PREREGISTRATION.md` and
`docs/LOOP_23_STREAMING_CTC_DECODER.md`. Loop 23.5's frozen design and closeout
are in `docs/LOOP_23_5_PREREGISTRATION.md` and
`docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`. Loop 22 evidence is in
`docs/LOOP_22_TINY_CAUSAL_ENCODER.md`; Loop 24 research, protocol, and machine
contract are in `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`, and
`registries/local_precision_runtime_contract.v0.json`; authorization is in
`docs/LOOP_24_AUTHORIZATION_DECISION.md`, the measured park is in
`docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`, and the post-20 sequence is in
`docs/POST_20_ROADMAP.md`. Loop 25's v0 research, preregistration, contract, and
request remain immutable history. Its current evidence and decision surface are
`docs/LOOP_25_ANTI_ALIAS_AUDIT.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`,
`registries/causal_preprocessing_contract.v1.json`,
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, and
`registries/loop25_authorization_request.v1.json`. The next 20-loop research,
work orders, and machine
contract are in `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOPS_25_44_ROADMAP.md`, and
`registries/next_20_loops.v0.json`. RW1 evidence is in
`docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`; RW2 evidence is in
`docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`,
`docs/RW2_PRIMARY_SOURCE_RESEARCH.md`, and
`docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`. RW3 research and registration are in
`docs/RW3_PRIMARY_SOURCE_RESEARCH.md`,
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`, and
`registries/replay_equivalence_contract.v0.json`. The separate Stage A decision
surface is `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` plus
`registries/rw3_stage_a_authorization_request.v0.json`. Open-source release
gates are in `docs/OPEN_SOURCE_READINESS.md`.

## Historical original PR plan

The sections below preserve the starter's original first-three-PR plan. Those
scaffold milestones have been superseded by the numbered loop tracker above.

### PR 1 — Real event/window extraction for one downloaded block

Use MNE only inside optional functions:

```bash
pip install -e '.[neuro]'
```

Implemented scaffold:

```text
load_mat_events(path) -> event rows
extract_fif_mat_windows(raw, events, tmin=-0.2, tmax=0.3, sfreq=50) -> windows
neurodecode extract-windows -> `.npz` cache and extraction report
```

Acceptance criteria:

- Works on one block if the user has selectively downloaded it.
- Saves a tiny `.npz` first; Zarr can be PR 3.
- Emits shape summary: samples x channels x timepoints.
- Emits storage summary before/after preprocessing.

### PR 2 — Baseline + report

Implement a tiny baseline:

```text
template classifier / ridge / tiny conv if torch available
```

Report:

```text
CER
WER
keyboard distance
examples: target vs prediction
storage footprint
runtime
```

Acceptance criteria:

- One-command run on synthetic shard.
- One-command run on real tiny shard if available.
- Baseline is explicitly marked as a sanity check, not SOTA.

### PR 3 — Zarr cache + visual demo

Implement chunked cache writing after the `.npz` loop works. Then make the Gradio demo show target text, predicted text, CER/WER, keyboard-distance error, and a small neural-window visualization.

Acceptance criteria:

- Existing `.npz` path remains supported.
- Zarr writes metadata and source manifest.
- Demo can run on synthetic cache without real data.

## Recommended architecture

Keep the project layers clean:

```text
datasets/       file listings, manifests, download selection
preprocess/     MNE loading, event alignment, window extraction
cache/          NPZ first, Zarr later
models/         honest small baselines
training/       synthetic + real shard runners
evaluation/     metrics and reports
demo/           Gradio visualization
```

## Research questions to keep alive

1. How small can a useful Brain2Qwerty-like shard be?
2. Which preprocessing steps preserve the most accuracy per GB?
3. How much accuracy comes from the neural signal vs the language prior?
4. How much subject-specific calibration is truly needed?
5. Can a reusable “neurotoken” cache become the common interface?

## Important caveats

- SpanishBCBL is from healthy Spanish-speaking skilled typists, not locked-in patients.
- v1 is keystroke-aligned; v2 is more real-time/asynchronous, but v2 data is still embargoed according to the public repo.
- MEG is not consumer hardware. Treat hardware realism as a separate research track.
- The license is noncommercial.

## Build notes and managed-environment constraints

Use `docs/BUILD_NOTES.md` as the durable working journal for future agents. It
records the loop timeline, local verification commands, environment blockers,
and case-study notes.

Current workstation constraints to preserve:

- Do not retry GitHub push/export from this Bain-managed workstation unless the
  user explicitly re-approves and the repository privacy/trust status is clear.
- An earlier Loop 5 workbook/tracker closeout path was interrupted by an
  admin/tooling block. The final closeout succeeded with the bundled
  spreadsheet runtime in `.codex_work/loop5_tracker_closeout/`.
- Keep tests and synthetic smoke paths independent of real SpanishBCBL data.
- Keep all real downloads explicit, capped, and dry-run first.
- Keep `.codex_work/` and any local helper artifacts out of commits.

## PR 1 status update

The real extraction path is now scaffolded as:

```bash
neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../S1_block1.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-events 200
```

Implementation notes:

- MNE, SciPy, and NumPy are imported only inside the real extraction path.
- Missing optional dependencies raise an install hint: `pip install -e '.[neuro]'`.
- The `.mat` parser supports common shapes: record lists, parallel time/label arrays, and numeric event matrices.
- Parser warnings are saved in metadata and printed when timestamps or labels are heuristic or absent.
- The command never downloads data; `download-selection` remains dry-run by default and still requires `--execute` for a real fetch.

Recommended next validation:

1. Run the synthetic smoke loop and unit tests.
2. Use `download-selection --execute` only for the tiny selected files.
3. Run `extract-windows` on one real `.fif` + `.mat` pair.
4. Inspect the `.npz` metadata warnings and confirm which `.mat` fields are the true keystroke timestamps/labels.

Next PR recommendation: build the PR 2 baseline/report loop on top of both `cache/synthetic_tiny.npz` and a real extracted `.npz` when available.

## Loop 3 status update

The safe tiny-shard selector is now closed for local planning:

```bash
neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest.jsonl \
  --out data/tiny_selection.json \
  --max-files 4 \
  --max-total-gb 2

neurodecode download-selection \
  --selection data/tiny_selection.json \
  --local-dir data/spanishbcbl_tiny
```

Implementation notes:

- `select-tiny` persists safety limits, known bytes, missing-size counts, and warnings.
- Known-size selections prefer the smallest exact raw+log candidate.
- `download-selection` prints exact files and size estimates before dry-run or execution.
- `download-selection --execute` refuses unknown-size selections unless the user also passes `--allow-unknown-size`.

## Loop 4 status update

The B2Q-mini cache schema v0 path is now present:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 64 --channels 8 --times 25
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
```

Implementation notes:

- `save_npz_cache` validates `windows`, `labels`, and optional event/channel arrays.
- `load_npz_cache` is the stable one-function loader for B2Q-mini `.npz` caches.
- Cache metadata is normalized with schema name/version, dimensions, array descriptors, warnings, and transformations.
- Synthetic caches are explicitly marked as not-real-neural data.
- Real extracted caches record source files, extraction params, parser warnings, and preprocessing transformations.
- `load-cache` prints a compact summary and can write a JSON sidecar for reports.

## Loop 5 status update - done

The metrics and error report path is implemented and Loop 5 is closed as of
2026-07-01.

Implemented command:

```bash
neurodecode report \
  --targets outputs/run_001/targets.txt \
  --predictions outputs/run_001/predictions.txt \
  --cache cache/synthetic_tiny.npz \
  --out-json outputs/run_001/metrics.json \
  --out-md outputs/run_001/report.md \
  --run-name run_001 \
  --split synthetic-smoke
```

Synthetic plumbing smoke is explicit:

```bash
neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md
```

Implementation notes:

- Reports include CER, WER, exact-match rate, keyboard distance, example rows,
  runtime, warnings, and optional cache/storage metadata.
- `--identity-smoke` copies targets into predictions and warns that the result is not a model output.
- Real predictions should be supplied as one prediction per line and compared with explicit target rows.
- Report JSON and Markdown are both written from the same report dictionary.

Closeout verification:

```bash
python -m unittest tests.test_report tests.test_cli_report
python -m unittest discover -s tests
neurodecode report --help
neurodecode make-synthetic-shard --out cache/loop5_synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report --cache cache/loop5_synthetic_tiny.npz --identity-smoke --out-json cache/loop5_synthetic_report.json --out-md cache/loop5_synthetic_report.md --run-name loop5_synthetic_identity_smoke --split synthetic-smoke
```

Observed result:

```text
Ran 8 tests
OK

Ran 45 tests
OK

Report JSON and Markdown were written with explicit identity-smoke warnings.
```

Loop 6 has since been completed; see the Loop 6 status update below.

## Loop 6 status update - done

The no-brain prior-only baseline is implemented and Loop 6 is closed as of
2026-07-01.

Implemented command:

```bash
neurodecode prior-baseline \
  --cache cache/synthetic_tiny.npz \
  --out-predictions cache/prior_predictions.txt \
  --out-json cache/prior_report.json \
  --out-md cache/prior_report.md \
  --run-name synthetic_prior_most_frequent \
  --split synthetic-smoke
```

Implementation notes:

- The command uses no neural signal and warns with `prior_baseline_no_neural_signal`.
- It supports `most-frequent`, `frequency-sample`, and `uniform-random` strategies.
- It reads eval targets from text rows or cache labels.
- It can fit priors from separate train targets or train-cache labels.
- If no train source is provided, it fits on eval labels and warns with
  `prior_fit_on_eval_targets_for_smoke_only`.
- Reports include a `baseline` metadata block in JSON and Markdown.

Closeout verification:

```bash
python -m unittest tests.test_prior_baseline tests.test_cli_prior_baseline tests.test_report
python -m unittest discover -s tests
neurodecode prior-baseline --help
neurodecode make-synthetic-shard --out cache/loop6_synthetic_tiny.npz --samples 32 --channels 4 --times 12 --classes 8
neurodecode prior-baseline --cache cache/loop6_synthetic_tiny.npz --out-predictions cache/loop6_prior_predictions.txt --out-json cache/loop6_prior_report.json --out-md cache/loop6_prior_report.md --run-name loop6_prior_most_frequent --split synthetic-smoke
```

Observed result:

```text
Ran 15 tests
OK

Ran 55 tests
OK

Prior-only smoke report wrote predictions, JSON, and Markdown.
exact_match_rate=0.1875
corpus_cer=0.8125
corpus_wer=0.8125
```

Historical next recommendation from Loop 6: Loop 7, Template /
Nearest-Centroid Baseline. Loop 7 has since been completed; see the status
update below.

## Loop 7 status update - done

The template / nearest-centroid baseline is implemented and Loop 7 is closed as
of 2026-07-01.

Implemented command:

```bash
neurodecode template-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/template_predictions.txt \
  --out-json cache/template_report.json \
  --out-md cache/template_report.md \
  --run-name synthetic_template_nearest_centroid \
  --split synthetic-holdout
```

Implementation notes:

- The command uses cache windows and warns with `template_baseline_uses_neural_windows`.
- It uses nearest-centroid templates, not deep learning.
- The one-cache path uses deterministic stratified holdout by label.
- Real comparisons can use `--train-cache` and `--eval-cache`.
- Reports include baseline metadata in JSON and Markdown.

Closeout verification:

```bash
python -m unittest tests.test_template_baseline tests.test_cli_template_baseline tests.test_report
python -m unittest discover -s tests
neurodecode template-baseline --help
neurodecode make-synthetic-shard --out cache/loop7_synthetic_tiny.npz --samples 64 --channels 4 --times 12 --classes 4
neurodecode template-baseline --cache cache/loop7_synthetic_tiny.npz --train-fraction 0.5 --out-predictions cache/loop7_template_predictions.txt --out-json cache/loop7_template_report.json --out-md cache/loop7_template_report.md --run-name loop7_template_nearest_centroid --split synthetic-holdout
```

Observed result:

```text
Ran 13 tests
OK

Ran 62 tests
OK

Template smoke report wrote predictions, JSON, and Markdown.
exact_match_rate=1.0
corpus_cer=0.0
corpus_wer=0.0
```

The perfect synthetic score is expected because the synthetic cache has clear
class bump patterns. It validates plumbing, not real Brain2Qwerty performance.

Historical next recommendation from Loop 7: Loop 8, Tiny Conv / EEGNet-style
Baseline. Loop 8 has since been completed; see the status update below.

## Loop 8 status update - done

The optional tiny Conv / EEGNet-style baseline is implemented and Loop 8 is
closed as of 2026-07-01.

Implemented command:

```bash
neurodecode tiny-conv-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.75 \
  --epochs 30 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --out-predictions cache/tiny_conv_predictions.txt \
  --out-json cache/tiny_conv_report.json \
  --out-md cache/tiny_conv_report.md \
  --run-name synthetic_tiny_conv \
  --split synthetic-holdout
```

Implementation notes:

- PyTorch is imported only inside the real training path.
- The base install remains lightweight.
- The command defaults to CPU and one Torch thread.
- It shares the same single-cache holdout and train/eval-cache modes as
  `template-baseline`.
- Reports include model name, deep-learning flag, train/eval accuracy, loss
  history, and warnings.
- Missing Torch produces: `pip install -e '.[ml]'`.

Closeout verification:

```bash
python -m unittest tests.test_tiny_conv_baseline tests.test_cli_tiny_conv_baseline tests.test_report
python -m unittest discover -s tests
neurodecode --help
neurodecode tiny-conv-baseline --help
neurodecode make-synthetic-shard --out cache/loop8_synthetic_tiny.npz --samples 64 --channels 4 --times 12 --classes 4
neurodecode tiny-conv-baseline --cache cache/loop8_synthetic_tiny.npz --epochs 2
```

Observed local result:

```text
Focused tests: Ran 15 tests, OK (skipped=2)
Full tests: Ran 71 tests, OK (skipped=2)
CLI help: OK
Tiny-conv command on base venv: helpful missing optional dependency error
```

That historical Bain-managed environment did not have Torch. The current macOS
workspace already has Torch available and ran the bounded Loop 14 CPU baseline;
no new heavy dependency was installed for it.

Historical recommendation from Loop 8: Loop 9, CTC Character Decoder Scaffold.
Loops 9-12 are complete and Loop 13 is parked after a passing measured gate.
NPZ remains the default until a recorded revisit trigger is reached. Loop 14
is complete with strict train-only preprocessing and a near-null first real
test. Qint16/qint8 remain representation candidates, not retained-accuracy
results.
