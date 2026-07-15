# Codex Handoff - NeuroDecodeKit

> Current handoff, 2026-07-15: Loop 25 v1 and scientific Loop 45 remain complete
> at their one-time target-free mechanics boundary with no rerun. The shared
> Loop 26/31/33 contract is green at `881145d`, and the user's exact one-time
> authorization is separately green at `1c0e52c` with push/PR CI runs
> `29422150469` and `29422152661`. A bounded reader, exact 2,908/2,884-parameter
> models, controls, 31-set prediction freezer, isolated scorer, and five CLI
> stages are implemented and synthetically qualified. No real S21 cache stat,
> hash, member, signal, or target value was read during implementation. The
> next gate is to commit, push, and remotely qualify this exact implementation;
> only then may the static metadata/header gate run. Five source-test rows,
> session 2, and all post-target tuning or reruns remain closed.

> Historical pre-Loop-25-execution context, retained for audit: Loops 1-12,
> 14-22, and 23.5 are complete; Loops
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
> fields remain false and every protected access counter is zero. Loop 27
> planning research is green at `b3d61b6`: a 315-file pinned MEG metadata pass
> found 23 strict pairs and 16 eligible pairs, then selected S25 session 2 block
> 2 as the smallest eligible same-modality/task candidate. Its exact two files
> total 1,009,939,983 bytes under a future 1 GiB cap. All 18 authorization fields
> remain false; no preregistration, request, download, local MAT payload hash,
> header, signal, target, model, training, final open, or backup substitution
> exists. Loop 28 planning research now defines the T0-T3 taxonomy and strict
> zero-shot S25 final-only recommendation: zero fit rows, at least 48 final
> rows, at least 0.05 macro sentence-CER advantage, 65,535 paired assignments
> plus observed, and strict corruption-control wins. All 21 authorization
> fields are false and the experiment remains `Not Started`. Loop 29 planning
> research now selects scalp EEG as the immediate local-first lane and OPM-MEG
> as a same-modality partner/lab lane while the experiment remains `Not
> Started`. Its 15 requirements, four modality profiles, six qualification
> levels, 12 future packet gates, and 24 false authorization fields are machine
> checked. The preferred 5,000,000,000-byte and absolute 10,000,000,000-byte
> capacity limits do not authorize the selected 1,106,030,247-byte S20 plus S25
> future bundle. No download, real-data read, model, SDK, stream, device,
> partner, or hardware operation occurred. Loop 30 planning research now
> freezes a loopback-only target-free replay inspector while its experiment
> remains `Not Started`: four source modes, a 30-field trace, nine clock
> domains, six latency levels, 18 future requirements, 30 refusals, and 30
> false authorization fields. No seed, trace, fixture, UI, server, browser run,
> consumed artifact, model, stream, live source, or hardware operation exists.
> Loop 31 planning research now freezes a 10-condition encoder attribution
> matrix, a contingent 5-condition LLM/Neuro Token matrix, six claim classes,
> 18 future requirements, 24 refusals, and 19 false authorization fields while
> its experiment remains `Not Started`. The maximum future local claim is
> sensor-signal dependence; brain-specific attribution remains blocked on Loop
> 35. No cache, target, checkpoint, model, training, validation, LLM, Neuro
> Token, S20, S25, stream, device, or hardware operation exists. Loop 32
> planning research recommends one causal 32-parameter hidden affine adapter,
> four distinct calibration modes, nested `0, 2, 4, 8, 16, 32` sentence
> budgets, and physically separate 32/16/48 calibration/selection/final floors
> while its experiment remains `Not Started`. It freezes 20 future gates, 26
> refusals, and 22 false authorization fields. No candidate or mode is selected;
> S25 remains final-only, and every participant/cache/signal/label/target/model/
> adapter/training/evaluation operation is unauthorized. Loop 33 planning
> research recommends nested `8, 16, 24, 32, 44, 55` unique-sentence prefixes,
> at most three seeds and 18 candidate fits, size-matched priors, and one shared
> six-row target open after every Loop 26/31/33 prediction is hash-frozen. Its
> experiment remains `Not Started`; 23 authorization flags are false, no
> physical-repetition lane or acquisition recommendation exists, and all
> protected/model/training/scoring work is unauthorized. Loop 34 planning
> research separates seven confidence semantics, eight score/control roles,
> and recommended fresh synthetic `128/64/256` calibration/selection/final
> counts. Its experiment remains `Not Started`; confidence is unavailable, all
> 26 authorization flags are false, and fixture/fit/target/scoring/product-
> confidence work is unauthorized. Loop 35 planning research freezes ten
> confound classes, nine future synchronized stream classes, 13 conditions,
> three stages, 24 gates, 32 refusals, and 31 false authorization fields. Its
> experiment remains `Not Started`; current evidence cannot support
> incremental brain-sensor information beyond recorded controls or absolute
> brain origin.
> Loop 36 planning research freezes six representation layers, five modality
> profiles, 24 channel fields, 12 operation classes, 16 fixture families, 22
> gates, 30 refusals, and 29 false authorization fields. Its experiment remains
> `Not Started`; declared metadata compatibility is the maximum future real-
> header claim, while numerical/model/device equivalence remains unavailable.
> Loop 37 planning research freezes six export layers, five artifact profiles,
> 15 standard BIDS mappings, 16 NeuroDecodeKit extension fields, 20 fixtures,
> four stages, 24 gates, 32 refusals, and 29 false authorization fields. Its
> experiment remains `Not Started` and unauthorized; all NeuroToken/report
> payloads remain explicitly non-standard and no derivative tree exists.
> Loop 38 planning research freezes five sensitivity levels, eight artifact
> classes, ten lifecycle surfaces, 12 sensitive-field classes, 12 threats, five
> deletion-receipt levels, 24 fixtures, four stages, 26 gates, 36 refusals, and
> 32 false authorization fields. Its experiment remains `Not Started` and
> unauthorized; unknown copies remain unresolved and no fixture, scanner,
> deletion, identity attack, history rewrite, consent determination, release,
> or upload exists.
> Loop 39 planning research freezes seven qualification levels, 18 environment
> identity fields, eight output classes, six comparison classes, six required
> future cells, 20 fixtures, four stages, 28 gates, 38 refusals, and 36 false
> authorization fields. Its experiment remains `Not Started` and unauthorized;
> Python 3.10, macOS, cross-OS, dependency-lock, and built-package evidence is
> unqualified, and no fixture, manifest, matrix, install, or build exists.
> Loop 40 planning research freezes seven qualification levels, six package
> layers, four unselected backend profiles, 20 identity fields, 24 fixtures,
> 30 gates, 40 refusals, and 40 false authorization fields. Its experiment
> remains `Not Started` and unauthorized; ExecuTorch/XNNPACK is a research lead
> only, Loop 39 has not qualified the reference, and no install, export,
> package, inference, simulator, app, device, or hardware operation exists.
> Loop 41 planning research freezes six integration layers, seven clock views,
> eight anomaly classes, five schedules, five resume cuts, 18 hash bindings,
> 28 fixtures, 32 gates, 42 refusals, and 42 false authorization fields. Its
> experiment remains `Not Started` and unauthorized; all four execution
> dependencies are unsatisfied and no fixture, source chunk, adapter,
> preprocessing, token runtime, latency result, stream, device, or hardware
> operation exists.
> Loop 42 planning research selects OpenBCI Cyton base 8-channel over USB radio
> as the exact future mechanics candidate at Q0 specification level. It freezes
> 28 identity fields, 16 packet fields, seven timing observables, ten anomalies,
> four stages, 34 gates, 46 refusals, and 45 false authorization fields. Its
> experiment remains `Not Started`; no purchase, SDK, serial read, board
> connection, participant, recording, locality result, signal, latency, model,
> decoding, or hardware qualification exists. Loop 43 planning research defines
> the independent artifact-reproduction firewall while its challenge remains
> `Not Started` and unauthorized. Loop 44 artifact-only claim review is
> complete; engineering release is held and scientific performance release is
> parked.
> This does not reopen Loop 24 or authorize RW3, data, targets, models,
> validation, training, calibration, or hardware.
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
- machine-checked Loop 27 metadata research with 315 MEG entries, 23 strict
  pairs, 16 eligible pairs, selected S25 identity plus exact official file
  hashes/bytes, final-only and target-isolation recommendations, 18 false
  authorization fields, and zero candidate payload access
- machine-checked Loop 28 planning research with four noninterchangeable
  transfer levels, an explicit strict-zero-shot/transductive split, zero S25
  fit rows, a 48-row/0.05-CER/65,535-assignment one-time rule, four frozen
  comparators, physically separate calibrated-transfer requirements, 21 false
  authorization fields, and zero protected access
- machine-checked Loop 29 planning research with separate cryogenic MEG,
  OPM-MEG, scalp EEG, and peripheral-control profiles; 15 requirements; six
  qualification levels; 12 future packet gates; exact 5-10 GB capacity limits;
  24 false authorization fields; and zero protected data, model, stream, device,
  partner, or hardware access; the experiment remains `Not Started`
- machine-checked Loop 30 planning research with four distinct source modes, a
  30-field target-free trace contract, nine clocks, six latency claim levels,
  18 future gates, 30 refusals, fixed loopback/file/network/browser controls,
  accessible incremental status semantics, 30 false authorization fields, and
  zero trace, UI, server, browser, protected-data, model, stream, live-source,
  device, or hardware execution; the experiment remains `Not Started`
- machine-checked Loop 31 planning research with a 10-condition encoder
  matrix, a contingent 5-condition LLM/Neuro Token matrix, exact six-row
  intersection-union inference, six claim classes, 18 future gates, 24
  refusals, 19 false authorization fields, and a Loop 35 ceiling on
  brain-specific attribution; the experiment remains `Not Started`
- machine-checked Loop 32 planning research with four calibration modes, a
  causal 32-parameter adapter recommendation, six nested sentence budgets,
  32/16/48 physical split floors, six final conditions, 20 gates, 26 refusals,
  22 false authorization fields, and zero candidate, protected access, model,
  adapter-fit, training, or final evaluation; the experiment remains `Not Started`
- machine-checked Loop 33 planning research with nested
  `8, 16, 24, 32, 44, 55` prefixes, a three-seed/18-fit ceiling, one prospective
  shared validation event, four conditions, 20 gates, 30 refusals, 23 false
  authorization fields, no physical-repetition lane, no acquisition
  recommendation, and zero protected/model/training/scoring execution; the
  experiment remains `Not Started`
- machine-checked Loop 34 planning research with seven confidence semantics,
  eight score/control roles, fresh `128/64/256` partition recommendations, 20
  gates, 30 refusals, 26 false authorization fields, an exact six-row
  insufficiency bound, and zero fixture/fit/target/scoring/product-confidence
  execution; the experiment remains `Not Started` and confidence is unavailable
- machine-checked Loop 35 planning research with ten confound classes, nine
  future synchronized stream classes, 13 conditions, three independently
  authorized stages, 24 gates, 32 refusals, 31 false authorization fields, and
  a fail-closed missing-control rule; the experiment remains `Not Started`
- machine-checked Loop 36 planning research with six representation layers,
  five modality profiles, a 24-field channel record, 12 operation classes, 16
  fixture families, 22 gates, 30 refusals, 29 false authorization fields, and
  strict separation between metadata identity and data-changing transforms;
  the experiment remains `Not Started`
- machine-checked Loop 37 planning research with six export layers, five
  artifact profiles, 15 stable BIDS mappings, 16 explicit NeuroDecodeKit
  extension fields, 20 fixture families, four stages, 24 gates, 32 refusals,
  29 false authorization fields, and a no-raw-copy rule; the experiment remains
  `Not Started` and every custom payload remains non-standard
- machine-checked Loop 38 planning research with five sensitivity levels,
  eight artifact classes, ten lifecycle surfaces, 12 sensitive-field classes,
  12 threats, five deletion-receipt levels, 24 fixture families, four stages,
  26 gates, 36 refusals, 32 false authorization fields, and zero current/all-
  history neural candidate paths; the experiment remains `Not Started`,
  unknown copies remain unresolved, and execution is unauthorized
- machine-checked Loop 39 planning research with seven qualification levels,
  18 environment identity fields, eight output classes, six comparison classes,
  six required future cells, 20 fixtures, four stages, 28 gates, 38 refusals,
  and 36 false authorization fields; the experiment remains `Not Started`,
  current declared support is not cross-machine qualified, and execution is
  unauthorized
- machine-checked Loop 40 planning research with seven qualification levels,
  six package layers, four backend profiles, 20 identity fields, 24 fixtures,
  four stages, 30 gates, 40 refusals, and 40 false authorization fields; the
  experiment remains `Not Started`, no target/backend is selected, and all
  packaging, inference, simulator, device, and hardware work is unauthorized
- machine-checked Loop 41 planning research with six integration layers, seven
  clock views, eight anomaly classes, five schedules, five resume cuts, 18
  identity/hash bindings, 28 fixtures, four stages, 32 gates, 42 refusals, and
  42 false authorization fields; the experiment remains `Not Started` and
  unauthorized, with no stream-to-NeuroToken runtime or latency result
- machine-checked Loop 42 planning research selecting OpenBCI Cyton base
  8-channel USB-radio at Q0 only, with 28 identity fields, 16 packet fields,
  seven timing observables, ten anomalies, ten privacy surfaces, ten safety
  requirements, four separately authorized stages, 30 fixtures, 34 gates, 46
  refusals, and 45 false authorization fields; no device is present or
  qualified, and no SDK, participant, recording, signal, or decoding operation
  exists
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

Current Loop 42 local verification passes 616 unittests with 3 expected skips
in 24.31 seconds wall and 612,483,072-byte maximum RSS; pytest reports 613
passed, 3 skipped, and 277 subtests in 23.34 seconds wall with
625,065,984-byte maximum RSS. The focused Loop 42 plus roadmap slice has 24
passing tests, and the Loop 25-42 planning-boundary discovery has 263 passing
tests in 1.99 seconds wall with 88,997,888-byte maximum RSS. Dependency-light
discovery is green at 584 tests with 121 optional skips in 2.57 seconds wall
and 106,840,064-byte maximum RSS. Each full count is 15 above the Loop 41
closeout. No Loop 25-42 fixture, coefficient,
preprocessing run, candidate selection/download, local MAT payload hash,
header/signal/target/validation/model read, adapter fit, training run,
calibration or confidence fit, learning-curve or confidence score, peripheral
recording, residualization fit, physical-repetition study, product-confidence
surface, geometry transform, unit conversion, rereference, interpolation,
exporter, derivative tree, validator run, raw copy, release, upload,
environment manifest, dependency lock, cross-machine matrix job, package build,
runtime install, export, conversion, packaged inference, profiler, delegate,
simulator, app, source chunk, stream-to-NeuroToken adapter, resume state,
clock correction, anomaly fixture, token runtime, end-to-end latency result,
language-model/Neuro Token run, protected network payload download, RW3
operation, SDK import, playback, serial read, discovery, stream, board,
participant contact, recording, device, partner, or hardware operation
occurred. The tracked workbook is 99,626 bytes with SHA-256
`7ac856e73b7e4b985f3becbf3372e1b973074959eb4973213a53a1452249c2a8`;
all nine sheets render, the export reloads with exact key ranges, and the
formula scan has zero matches. Ruff lint, touched-file format checks,
compileall, 31 source JSON and two TOML parses, 72 checked local Markdown links
with zero missing, four exercised CLI help surfaces, 55 registered commands,
unauthorized Loop 42 runtime absence, the 86-commit Gitleaks scan, and
`git diff --check` pass. Repository-wide `ruff format --check src tests` still
reports the pre-existing 96-file formatting backlog and was not applied as an
unrelated rewrite. Research commit `9188157` passes push CI run `29237366884`
and draft PR #21 CI run `29237382715`; both Base Python and Optional Neuro
Readers jobs are green.

## The north star

Build a developer experience layer for non-invasive neural language decoding:

```text
huge raw neurodata → tiny selected shard → reproducible cache → baseline decoder → honest report
```

This is not primarily a model repo. It is a **research loop repo**.

## Current Next Work

1. **Loop 26 / roadmap Loop 46 - remotely qualify the exact implementation.**
   Read `docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md`,
   `docs/LOOP_26_AUTHORIZATION_DECISION.md`,
   `docs/LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md`, and the Loop 26 v0
   registries. Authorization commit `1c0e52c` is green. Commit and push the
   synthetic implementation, wait for both remote jobs, and only then run the
   static metadata/header gate. Keep validation targets closed until the later
   hash-only freeze commit is separately green.
2. **RW3 - decide on the prepared Stage A packet only.** Review
   `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` and
   `registries/rw3_stage_a_authorization_request.v0.json`. The request is bound
   to commit `c3d1f01` and its exact contract hash, but `authorized_now` remains
   false. Do not implement Stage A without an explicit user decision followed
   by a pushed authorization-only commit; BrainFlow, LSL, PyXDF, sockets, live
   sources, hardware, and Stages B-D remain later independent gates.
3. **Use Loops 26-44 and 46-64 as future evidence queues, not blanket
   authorization.**
   Read `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
   `docs/LOOPS_25_44_ROADMAP.md`, and
   `registries/next_20_loops.v0.json`. For Loop 26, also read the green shared
   preregistration, separate authorization, and synthetic implementation. It
   still has no protected runtime, cache-value/target delivery, real model run,
   prediction freeze, or validation result. For Loop 27,
   read `docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop27_research_boundary.v0.json`: S25 is selected in metadata,
   but the source model, controls, target isolation, and staged permissions are
   absent, so preregistration and acquisition remain blocked. For Loop 28, read
   `docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop28_research_boundary.v0.json`. Its planning research supplies
   the strict zero-shot final rule, but no preregistration, model prediction,
   calibration, final open, or authorization exists. For Loop 29, read
   `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop29_research_boundary.v0.json`. Its planning research supplies
   a two-lane EEG/OPM-MEG pathway and a 5-10 GB capacity boundary, but no device
   selection, preregistration, download, SDK, stream, hardware session, or
   portable decoding result exists. For Loop 30, read
   `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop30_research_boundary.v0.json`. Its planning research defines
   the target-free local replay interaction, but no seed, trace, fixture, UI,
   server, browser run, model, stream, live source, or latency result exists.
   For Loop 31, read `docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop31_research_boundary.v0.json`. Its planning research defines
   the 10-condition encoder and contingent 5-condition LLM attribution
   firewall, but no cache, target, checkpoint, model, training, validation,
   LLM, Neuro Token, or sensor-signal result exists; Loop 35 is still required
   for brain-specific attribution.
   For Loop 32, read `docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop32_research_boundary.v0.json`. Its planning research defines
   one 32-parameter adapter family, four claim modes, six nested budgets,
   physical partition floors, access order, human burden, and one-time final
   gates, but no participant, candidate, preregistration, signal, label,
   checkpoint, adapter fit, training, or calibrated result exists.
   For Loop 33, read `docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop33_research_boundary.v0.json`. Its planning research defines
   the `8, 16, 24, 32, 44, 55` prefixes and prospective shared-validation
   order, but the experiment is `Not Started` and no protected access,
   training, scoring, physical-repetition study, or acquisition is authorized.
   For Loop 34, read `docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop34_research_boundary.v0.json`. Its planning research defines
   confidence semantics, fresh three-way synthetic partitions, target leakage
   refusals, generalized-risk and revision-latency reporting, and a real-data
   unavailable boundary. The experiment is `Not Started`; no fixture,
   confidence fit, target open, scoring, or product-visible confidence is
   authorized.
   For Loop 35, read `docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop35_research_boundary.v0.json`. Its planning research defines
   the peripheral-control matrix and caps any future local claim at incremental
   brain-sensor information beyond recorded controls. The experiment is `Not
   Started`; no fixture, acquisition, protected-data read, model, training,
   scoring, no-keypress study, device, or hardware work is authorized.
   For Loop 36, read `docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop36_research_boundary.v0.json`. Its planning research defines
   channel, unit, frame, transform, reference, compensation, interpolation,
   and missingness boundaries. The experiment is `Not Started`; no fixture,
   header/signal read, transform, rereference, interpolation, model, training,
   or device operation is authorized. Declared metadata compatibility is not
   numerical compatibility or model/device equivalence.
   For Loop 37, read `docs/LOOP_37_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop37_research_boundary.v0.json`. Its planning research defines
   the BIDS envelope, portable source identity, standard/non-standard field
   firewall, path/privacy redaction, no-raw-copy audit, validator ceiling, and
   release dependencies. The experiment is `Not Started` and unauthorized; no
   fixture, exporter, derivative tree, validator, payload copy, release, or
   upload exists.
   For Loop 38, read `docs/LOOP_38_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop38_research_boundary.v0.json`. Its planning research pins
   NIST PF 1.0, treats neural derivatives and stable hashes as potentially
   linkable, inventories local/Git/remote/CI/release copy surfaces, and
   separates local receipts from media sanitization. The experiment is `Not
   Started` and unauthorized; no fixture, scanner, deletion, protected-root
   scan, identity attack, history rewrite, consent determination, release, or
   upload exists. Unknown copies remain unresolved.
   For Loop 39, read `docs/LOOP_39_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop39_research_boundary.v0.json`. Its planning research defines
   seven qualification levels, 18 environment fields, exact semantic/discrete
   identity, field-specific float policies, six future cells, and the boundary
   between maintainer-run CI, independent reproduction, and scientific
   replication. The experiment is `Not Started` and unauthorized; no fixture,
   manifest, matrix job, dependency lock/install, package build, protected
   read, model, training, edge, stream, device, or hardware operation exists.
   Each future loop still requires its own packet before execution.
4. **Keep the GitHub history reviewable.** PR #3 carries the validated Loop
   8-24 evidence stack and is green. Draft PR #4 carries the separately stacked
   Loop 25 v0 history, v1 amendment, and still-false decision packet so
   preregistration and authorization remain auditable. The
   `codex/loop-26-research` branch stacks the planning-only Loop 26 evidence on
   top. The `codex/loop-27-preregistration` branch then stacks only the
   metadata-only Loop 27 boundary. The `codex/loop-28-transfer-research` branch
   stacks the transfer decision research without S25 access or execution. Keep
   `codex/loop-29-portable-sensing-research` stacks only the portability
   research boundary without data, device, or hardware access. The
   `codex/loop-30-local-streaming-research` branch stacks only the target-free
   replay interaction boundary without UI or runtime execution. The
   `codex/loop-31-neural-contribution-research` branch stacks only the
   attribution research boundary without protected or model execution. The
   `codex/loop-32-calibration-research` branch stacks only the fresh-person
   calibration planning boundary without a candidate or protected execution. Keep each
   independently reviewable; do not merge until CI, license, privacy, history,
   and proof-boundary review is complete.

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
request remain immutable history. Its v1 audit and completed result surface are
`docs/LOOP_25_ANTI_ALIAS_AUDIT.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`,
`registries/causal_preprocessing_contract.v1.json`,
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, and
`registries/loop25_authorization_request.v1.json`, plus
`registries/loop25_authorization_decision.v1.json`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_RESULT.md`, and
`registries/loop25_causal_preprocessing_result.v1.json`. The next 20-loop research,
work orders, and machine
contract are in `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOPS_25_44_ROADMAP.md`, and
`registries/next_20_loops.v0.json`. Loop 29's research note and machine boundary
are `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop29_research_boundary.v0.json`. Loop 30's research note and
machine boundary are `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop30_research_boundary.v0.json`. Loop 31's research note and
machine boundary are `docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop31_research_boundary.v0.json`. Loop 32's research note and
machine boundary are `docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop32_research_boundary.v0.json`. RW1 evidence is in
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

## Loop 43 Handoff

Loop 43 planning research is complete while the independent-reproduction
challenge remains `Not Started` and unauthorized. The selected future lane is
one target-free NeuroToken causal-replay software artifact under a commit-
reveal protocol; the current artifact is not eligible because Loop 37 release,
Loop 38 lifecycle, and Loop 39 matrix/independent-handoff execution dependencies
remain open. The machine contract freezes seven qualification levels, 16
independence fields, 28 packet fields, 34 submission fields, eight comparison
classes, 12 discrepancy classes, four stages, 32 fixture families, 36 gates,
48 refusals, and 48 false authorization fields. No packet, oracle, outreach,
contributor, submission, adjudication, archive, release, protected operation,
or scientific result exists. Loop 44 artifact review is now complete; the
current execution gate remains the separately controlled Loop 25 v1 decision.

Local Loop 43 acceptance passes 631 unittests with three expected skips, 628
pytest tests with three skips and 277 subtests, and 599 dependency-light tests
with 121 optional skips. Research commit `81798e0` is pushed on
`codex/loop-43-independent-reproduction-research`; push CI `29240649149` and
draft PR #22 CI `29240665109` both pass Base Python and Optional Neuro Readers.
The user-owned workbook inspection sidecar remains untracked and byte-exact.

## Loop 44 Handoff

Loop 44 artifact-only claim review is complete. The machine source of truth is
`registries/loop44_claim_release_matrix.v0.json`; the research and decision
notes are `docs/LOOP_44_PRIMARY_SOURCE_RESEARCH.md` and
`docs/LOOP_44_CLAIM_PROMOTION_AND_RELEASE_DECISION.md`.

The matrix freezes 16 claim cards, seven evidence levels, five model cards,
four dataset cards, 14 release gates, and eight risks. Three engineering claims
are promoted; three negative or inconclusive real-data results are retained;
two claims remain fixture-backed; two measured paths remain parked; five
desired claims remain unavailable; clinical/arbitrary-thought wording is
prohibited. Engineering release is held and scientific performance release is
parked.

No tag, GitHub release, archive, DOI, participant payload, protected data,
consumed evaluation, target, model, training, stream, device, or hardware
operation occurred. One overbroad documentation search displayed the untracked
tracker inspection sidecar once; artifact-tool later overwrote it during export,
after which the exact prior bytes were recovered and restored. It remains
untracked and unstaged. The next roadmap must target the evidence gaps without
reopening consumed S21/S7 data or turning general continuation into experiment
authorization.

Local acceptance passes 24 focused Loop 44 and Loops 45-64 invariants, 655
unittests with three expected skips, 652 pytest tests with three skips and 277
subtests, and 623 dependency-light tests with 121 optional skips. Ruff lint,
compileall, JSON/TOML validation, three CI CLI help surfaces, diff hygiene, and
the tracked-history secret scan also pass. Research commit `90d8919` is pushed
on `codex/loop-44-claim-release-research`; push CI `29243833014` and draft PR
#23 CI `29243844680` both pass Base Python and Optional Neuro Readers.

## Loops 45-64 Handoff

The next scientific tranche is in
`docs/LOOPS_45_64_SCIENTIFIC_ROADMAP.md` and
`registries/next_scientific_loops.v0.json`: contiguous IDs 45-64, five phases
of four, ten sources, ten kill branches, 20 false execution flags, and nine
false global authorization fields.

The critical sequence is Loop 45 causal mechanics, Loop 46's six reserved S21
validation rows, Loop 47 intact-signal attribution, one non-S25 development
person, a complete freeze, and Loop 52's one-time S25 zero-shot verdict. S21
session 2 and S7 stay consumed; S25 stays unopened and final-only. EEG,
streaming, device, home, reproduction, and release phases remain downstream
and separately authorized.

The tracker now has ten sheets, including `Loops 45-64`. It is 114,652 bytes at
SHA-256 `83606898dc58201e016f1f44ca156c1817f3719a8a401b2619e20d7f349f91ae`.
All sheets rendered, key ranges reloaded, and the formula-error scan found zero
matches. The user-owned inspection sidecar was restored byte-exact and remains
untracked and unstaged.
