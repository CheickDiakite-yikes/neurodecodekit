# Codex Handoff - NeuroDecodeKit

> Current handoff, 2026-07-10: Loops 1-12, 14-22, and 23.5 are complete; Loops
> 13 and 23 are parked after measured gates. Two S21 MEG sessions support strict
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
> passing. Seed 2353 is consumed. Loop 24 is unblocked for preregistration only.
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
> seven dependency-free invariant tests. No source chunk, fixture, CLI,
> BrainFlow/LSL/PyXDF import, socket, stream, board, or XDF operation occurred.
> Stage A remains unapproved. No real recording, consumed cache, S20
> download/read, live source, automatic cleaning, model, or training is
> authorized.
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
- open-source collaboration surface with Apache-2.0 license, third-party/data
  boundaries, detailed README, EEG data/hardware contribution paths, security,
  governance, citation, issue forms, pull-request checks, and one-thread CI
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

Current verification after the RW3 registration/documentation milestone on
2026-07-10: 265 unittest tests pass with 3 skipped in 13.124 seconds
(13.920 seconds wall, 569,720,832-byte maximum RSS); pytest reports 262 passed,
3 skipped, and 25 subtests passed in 12.16 seconds (13.120 seconds wall,
579,354,624-byte maximum RSS). All 7 focused RW3 invariant tests pass in 0.040
seconds wall with 18,022,400-byte maximum RSS. A separate true zero-dependency
run passes 253 tests with 118 explicit optional skips in 0.340 seconds wall and
40,419,328-byte maximum RSS. The pre-RW3 baseline was 258 unittest and 255
pytest passes with the same three optional-environment skips/subtests, so RW3
adds seven tests without regression. Full Ruff lint, compileall, root CLI help,
JSON/TOML parsing, 39 local Markdown links, workbook formulas/renders, and
`git diff --check` pass; Gitleaks is rerun on the final commit before push.
The tracked and delivered workbook hashes match at
`fdb6d38217682e29033eeb623ffe46f20debd12e82ade4866a6b58d06d80daa9`.
The tracked workbook is 56,304 bytes and its eight-sheet visual/formula audit
passes.

## The north star

Build a developer experience layer for non-invasive neural language decoding:

```text
huge raw neurodata → tiny selected shard → reproducible cache → baseline decoder → honest report
```

This is not primarily a model repo. It is a **research loop repo**.

## Current Next Work

1. **RW3 - review the frozen registration and decide on Stage A only.** Commit
   `c3d1f01` already freezes the source-chunk, clock, anomaly, schedule, state,
   privacy, resource, refusal, and stop rules. Do not implement Stage A without
   explicit authorization; BrainFlow, LSL, PyXDF, sockets, live sources, and
   hardware remain later independent gates.
2. **Loop 24 - preregister local precision/runtime independently.** Freeze
   candidates, reference arithmetic, tolerances, fresh selection data, and
   resource rules before code. Seed 2353 cannot select anything.
3. **Review draft PR #2 before publishing the latest evidence on `main`.** PR #1
   has merged the open-source community surface through `e5d89ed`; PR #2 carries
   the RW2 closeout, README results dashboard, canonical Apache license text,
   Linux float32 portability record, and RW3 registration. Do not merge until
   CI, license, issue-form, security, history, visibility, and proof-boundary
   review is complete.

RW4 is not next: S20 acquisition remains blocked until explicit approval names
revision `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`, exactly four files, the
128-MiB download cap, 16-MiB output cap, and one-time 44/10/10 protocol.

Loop 23's preregistration and parked result are in
`docs/LOOP_23_PREREGISTRATION.md` and
`docs/LOOP_23_STREAMING_CTC_DECODER.md`. Loop 23.5's frozen design and closeout
are in `docs/LOOP_23_5_PREREGISTRATION.md` and
`docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`. Loop 22 evidence is in
`docs/LOOP_22_TINY_CAUSAL_ENCODER.md`; the post-20 sequence is in
`docs/POST_20_ROADMAP.md`; RW1 evidence is in
`docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`; RW2 evidence is in
`docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`,
`docs/RW2_PRIMARY_SOURCE_RESEARCH.md`, and
`docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`. RW3 research and registration are in
`docs/RW3_PRIMARY_SOURCE_RESEARCH.md`,
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`, and
`registries/replay_equivalence_contract.v0.json`. Open-source release gates are
in `docs/OPEN_SOURCE_READINESS.md`.

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
