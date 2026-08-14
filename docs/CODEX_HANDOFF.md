# Codex Handoff - NeuroDecodeKit

> Additive foundation-model decision, 2026-08-06: read
> `docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md` and
> `registries/foundation_model_decoder_strategy.v0.json`. The intended product
> stack is causal preprocessing, a compact trained sensor adapter, structured
> CTC/key evidence, then frozen `gpt-5.6-sol`. The hosted route cannot inject
> custom NeuroToken embeddings, so raw EEG, dense vectors, targets, identities,
> and local paths remain outside the provider packet. `FM-A02` must beat both
> CTC-only and fixed item-deranged evidence under the same Sol configuration.
> FM-0 is now implemented and locally validated through
> `docs/FOUNDATION_MODEL_BRIDGE_V0.md` and
> `registries/foundation_model_bridge_v0.json`. The committed 7,327-byte
> no-call fixture compiles into all 12 request plans and 34,349 bytes in 0.00275 seconds
> at about 21.5 MB peak RSS. FM-1 now adds a separately frozen
> synthetic-only Terra transport through
> `docs/FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md`,
> `docs/FOUNDATION_MODEL_LIVE_SMOKE_AUTHORIZATION_DECISION.md`, and
> `docs/FOUNDATION_MODEL_LIVE_SMOKE_IMPLEMENTATION.md`. Contract commit
> `7db14d5` and exact-decision commit `04fc009` are remotely green. The local
> implementation rebuilt all 12 blinded requests, totaling 18,399 bytes, in
> 0.004586541 seconds at 33,832,960-byte peak RSS; focused tests pass. The full
> post-decision baseline advances
> from 1,176 to 1,193 passing tests with 3 expected skips; Ruff, compileall,
> every registry JSON, CLI dry-run/help, and diff hygiene pass. Implementation
> commit `a1d7ccc` passed push CI `31269398670` before the one authorized live
> invocation. FM-1 is now consumed and parked: 3 calls attempted, 2 strict
> responses completed, and request index 2 returned non-completed provider
> status. `FM-A00` abstained; CTC-only `FM-A01` returned `HELLO WURLD`; no
> completed matched/deranged pair exists. Runtime was 8.406004375 seconds at
> 39,337,984-byte peak RSS. Do not rerun, retry, substitute, tune, score, or
> claim scientific evidence. Read `docs/FOUNDATION_MODEL_LIVE_SMOKE_RESULT.md`
> and `registries/foundation_model_live_smoke_result.v0.json`. FM-0 focused
> verification passes 35 tests;
> the full baseline advances from 1,129 to 1,164 passing tests with the same 3
> expected skips. Ruff, compileall, all registry JSON, CLI help/roundtrip, and
> diff hygiene pass.
>
> Budget/tooling update, 2026-08-08: the user authorized a $50 aggregate AI
> provider ceiling. Read `docs/AI_LOCAL_FIRST_R_AND_D_BUDGET_2026-08-08.md`
> and `registries/ai_local_first_rd_budget.v0.json`. Reserve the full $0.50
> FM-1 cap because third-attempt billing is unavailable. The remaining $49.50
> is a portfolio of future ceilings, not a spend target. Synthetic/public
> non-protected target-free calls still require a committed bounded packet;
> targets, protected data, scientific scoring, raw/dense uploads, hardware,
> large downloads, releases, and claims remain closed. Prefer MNE, MOABB,
> pyRiemann, and compact Braindecode work locally. Apple application
> `US20230225659A1` supports an ear-channel quality research direction but does
> not prove shipping AirPods EEG or thought-to-text.
>
> Local tooling update, 2026-08-08: read
> `docs/LOCAL_EEG_TOOLING_AUDIT_2026-08-08.md`, both
> `registries/local_eeg_tooling_audit_*.v0.json` files, and
> `docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md`. Implementation commit
> `e1de855` passed push CI `31277731869` before one zero-network audit. NumPy
> 2.5.0, SciPy 1.18.0, MNE BrainVision reading, and MNE ICA are available;
> scikit-learn, pyRiemann, MOABB, and Braindecode are absent. The 9,416-byte
> report took 14.52799025 seconds at 173,211,648-byte maximum child RSS with all
> data, target, model, training, scoring, network, provider, and hardware
> counters zero. Work orders 1-2 are complete. Continue with work order 3's
> deterministic NumPy/SciPy synthetic physiology/confound fixtures and no new
> dependency, download, S20 read, target, model, or hardware action. Work order
> 3 is now frozen in `docs/SYNTHETIC_MOTOR_FIXTURE_PREREGISTRATION.md` and
> `registries/synthetic_motor_fixture_contract.v0.json`: seed 5503, 96 paired
> items, eight factor families, 48/32/16 partitions, eight mutations, and a
> 4 MiB cap. `docs/SYNTHETIC_MOTOR_FIXTURE_IMPLEMENTATION.md` and its registry
> now bind the generator, strict loader, metadata-only inspector, mutation API,
> CLI, and tests. Exact implementation `ad361c8` passed push CI `31279302969`
> before one closeout. All 18 gates passed in 1.20 seconds at 118,177,792-byte
> peak RSS and 584,308 bytes; generated files were removed. Work order 3 is
> complete. Work order 4's classical adapter contract and symbolic planner are
> also complete. The frozen contract is
> `docs/CLASSICAL_EEG_ADAPTER_PREREGISTRATION.md` plus
> `registries/classical_eeg_adapter_contract.v0.json`: three unselected
> families, train-only fits, pair/group isolation, twelve refusals, and no
> optional import. `docs/CLASSICAL_EEG_ADAPTER_IMPLEMENTATION.md` and its
> registry bind the standard-library plan builder, validator, hash,
> save/load/summary APIs, CLI, and tests. Exact implementation `eefb7b0` passed
> CI `31280581308` before one 0.12-second measured roundtrip at 22,822,912-byte
> peak RSS. All 18 gates passed and the 27,335-byte plan was removed. Read
> `docs/CLASSICAL_EEG_ADAPTER_RESULT.md` and its registry. Continue only work
> order 5's synthetic contact-mask, noise, and missing-channel contract. That
> contract is now frozen in
> `docs/CONTACT_AWARE_EAR_CHANNEL_PREREGISTRATION.md` and
> `registries/contact_aware_ear_channel_contract.v0.json`: seed 5505, 48 items,
> 16 generic bilateral channels, six masks, a fixed maximum-four/minimum-two
> per-side policy, equal side weights, and 16 refusals. Contract commit
> `c6e216f` passed CI `31281290300` before implementation. Read
> `docs/CONTACT_AWARE_EAR_CHANNEL_IMPLEMENTATION.md` and its implementation
> registry for the locally qualified generator, policy, strict validator,
> metadata-only inspector, deterministic hashes, resource guards, refusal
> matrix, and CLI. Exact implementation `76ccc63` passed CI `31282344300`
> before one measured synthetic roundtrip. Read
> `docs/CONTACT_AWARE_EAR_CHANNEL_RESULT.md` and its result registry. All 18
> gates passed in 0.40 seconds at 55,394,304-byte peak RSS with 938,874 output
> bytes and zero retained files. Work order 5 is complete. Work order 6 then
> completed the recovery-bound Loop 54-A decision and parser qualification in
> `docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md` and
> `registries/loop54_stage_a_recovery_authorization_request.v1.json`. Every
> authorization flag remains false in those immutable snapshots. Request
> commit `19813a8` passed CI `31283297030`; exact Tier C decision commit
> `2177b36` passed CI `31286428489` before implementation. Read
> `docs/LOOP_54_STAGE_A_VHDR_IMPLEMENTATION.md` and its registry. The strict
> parser, dry-run-first CLI, bounded ledger, and all 22 refusal classes are
> qualified on generated synthetic fixtures. Exact implementation `b486fdf`
> passed CI `31287819503` before work order 7 consumed the one registered
> execution. Read `docs/LOOP_54_STAGE_A_VHDR_RESULT.md` and its result registry.
> One 11,705-byte VHDR open passed no-follow, size, Git-blob, and strict-decode
> checks, then parked at `L54A-F11` because the frozen preamble gate failed.
> Runtime was 0.20 seconds at 24,051,712-byte peak RSS. No sibling, signal,
> marker, MAT, target, model, network, hardware, or output access occurred.
> L54-Q2 was not established, no rerun is open, and Loop 54-B/C are blocked.
>
> Current handoff, 2026-08-08 after the consumed Loop 54-A execution: preserve
> registration `c114623`, pinned-toolchain proof `2232993`, request `19813a8`,
> decision `2177b36`, and implementation `b486fdf` as ordered evidence. The
> all-gates conjunction failed only at the strict required-structure gate after
> source identity and decoding passed. The raw first line and all header values
> remain unpublished and unavailable. Do not reopen S20, retry with MNE or a
> fallback parser, resolve a sibling, amend the parser from this outcome, start
> Loop 54-B/C, or promote a scientific claim. Work order 8 remains an
> independent, separately gated public-data acquisition route.
> Preserve the unrelated tracker inspection NDJSON.
>
> Current CML-v0 handoff, 2026-08-09: read the architecture research, then
> `docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_PREREGISTRATION.md`,
> `docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_IMPLEMENTATION.md`, and
> `docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md` with their matching
> registries. Contract commit `67709a3` passed CI `31294479865`; exact
> implementation `90fa467` passed CI `31295430105` before one seed-5513 run.
> The 4,535-parameter model reached `1.0` hand/key accuracy on all 16
> constructed signal-bearing check rows, localized potential/mu/beta branches,
> passed hand/key marginal-consistency and causal future-tail checks, and
> replayed its checkpoint hash exactly. Eighteen of 19 gates passed. Float32
> common-mode key-logit error `1.9073486e-6` exceeded the frozen `1e-6`
> tolerance, so the run parked at `CML-R0`; synthetic final targets stayed
> closed and there is no rerun. Runtime was 6.553 seconds at 398,737,408-byte
> peak RSS with 37,371 generated bytes. Every real/public/protected, S20,
> PhysioNet, network, provider, hardware, release, and claim counter stayed
> zero. Do not rerun seed 5513, relax the tolerance, reopen final, start Loop
> 54-B/C, or treat invented-factor accuracy as real EEG evidence. Preserve the
> unrelated tracker inspection NDJSON.
>
> Current PhysioNet work-order-8 handoff, 2026-08-09: registration commit
> `2a7b4188553e221133d788a081b838dbbb9f41bb` passed Base Python job
> `93215490492` and Optional Neuro Readers job `93215490501` in CI
> `31301730612`. Read
> `docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md`,
> `registries/physionet_motor_acquisition_contract.v0.json`,
> `docs/PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_PACKET.md`, and
> `registries/physionet_motor_acquisition_authorization_request.v0.json`.
> The request binds exactly nine EEGMMIDB v1.0.0 EDF paths, 23,248,224 bytes,
> nine official SHA-256 values, one no-retry invocation, one opaque local hash
> pass per file, one thread/worker, 300 seconds, 256 MiB RSS, 32 MiB EDF
> network, 64 MiB incremental disk, and 1 MiB receipts. Every implementation,
> metadata recheck, payload, local-path, parse, split, model, execution, rerun,
> and claim permission is false in the request. Verify the request commit is
> pushed and remotely green before accepting its exact Tier C sentence. Do not
> implement a downloader, touch a PhysioNet path, fetch an EDF or `.event`
> payload, or enter work order 9 from the packet alone. Preserve the unrelated
> tracker inspection NDJSON.
>
> Work-order-8 authorization update, 2026-08-09: the maintainer supplied the
> exact registered sentence after request `f6eb577` passed CI `31302161647`.
> Read `docs/PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_DECISION.md` and
> `registries/physionet_motor_acquisition_authorization_decision.v0.json`.
> Decision `00b91ed` passed both jobs in CI `31344104565` before fixture/mock
> implementation. Read `docs/PHYSIONET_MOTOR_ACQUISITION_IMPLEMENTATION.md`
> and `registries/physionet_motor_acquisition_implementation.v0.json`. The new
> standard-library executor, `physionet-motor-acquire` dry-run-first CLI,
> exact three-document plus nine-HEAD metadata pass, no-redirect/no-retry
> transfer, one-pass opaque hashing, atomic promotion, bounded receipts, and
> refusal matrix are locally qualified on generated bytes only. The complete
> suite passes 1,448 tests with 3 expected skips and 493 subtests. No source
> metadata, local PhysioNet path, EDF, sidecar, parser, target, model, or
> experiment operation occurred during implementation. Exact implementation
> `92760ce` then passed both jobs in CI `31345401581` before the one registered
> invocation. Read `docs/PHYSIONET_MOTOR_ACQUISITION_RESULT.md` and its result
> registry. All 12 gates passed: 442,178 metadata response-body bytes, nine EDF
> requests and exactly 23,248,224 payload bytes, nine one-pass local SHA-256
> matches, 50.682373 seconds, 55,181,312-byte peak RSS, 28,327,635-byte peak
> disk, and 16,083 private receipt bytes. Every header, annotation, event,
> signal, target, channel, split, model, training, inference, scoring, retry,
> rerun, and work-order-9 counter stayed zero. Work order 8 is complete and
> consumed with no rerun. Payload and private receipts remain Git-ignored; do
> not publish or reopen them. Work order 9 is still gated. The user's 10 GB
> ceiling remains future headroom, not permission to add files now. The
> sanitized post-result suite passes 1,455 tests with 3 expected skips and 493
> subtests. Preserve the unrelated tracker inspection NDJSON.
>
> Current PhysioNet work-order-9 registration handoff, 2026-08-09: read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md`,
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md`, and
> `registries/physionet_motor_positive_control_contract.v0.json`. The only
> eligible inventory is the existing nine S001-S003 runs 03/07/11 EDFs. A
> future exact execution would use runs 03/07 for grouped CSP-versus-Riemannian
> selection and keep the 45 run-11 events sealed until all 12 primary/control
> prediction sets are hash-frozen, committed, pushed, and remotely green. The
> maximum `WO9-V3` verdict requires the predictive, motor-compatible mu/beta,
> and confound conjunctions together; accuracy alone routes no higher than
> `WO9-V2`. One thread, 1,800 seconds, 768 MiB RSS, 64 MiB private output, zero
> network, one score, and no rerun are frozen. This registration authorizes no
> local path stat/open, EDF hash/parse, target, dependency, derivative, split,
> fit, inference, freeze, or score. First obtain green registration evidence,
> then create a separate hash-bound authorization packet and exact decision,
> and only after its green decision qualify an implementation on generated
> fixtures. Preserve the unrelated tracker inspection NDJSON.
>
> Work-order-9 request update, 2026-08-09: registration `3c00557` passed Base
> Python job `93330354031` and Optional Neuro Readers job `93330354047` in CI
> `31346882592`. Read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md` and
> `registries/physionet_motor_positive_control_authorization_request.v0.json`.
> The packet conditionally requests a generated-fixture-only implementation,
> one narrow isolated classical environment, one exact nine-EDF execution, a
> remotely green hash-only prediction freeze, and one delivery/score of the
> same 45 targets. Every current authorization field and operation counter is
> false/zero. The request commit must be pushed and remotely green before its
> exact sentence can become a separate decision. Do not implement, install,
> stat/open the bundle, or accept broad permission as a substitute. Preserve
> the unrelated tracker inspection NDJSON.
>
> Work-order-9 authorization decision update, 2026-08-09: request `c62b10a`
> passed Base Python job `93331241434` and Optional Neuro Readers job
> `93331241411` in CI `31347209691`. The maintainer supplied the exact frozen
> sentence with `64 target-blind prediction sets`. Read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_DECISION.md` and
> `registries/physionet_motor_positive_control_authorization_decision.v0.json`.
> This decision is effective only after its own commit is pushed and both jobs
> are green. Then and only then implement and qualify on generated fixtures;
> the implementation must also become remotely green before any registered
> local PhysioNet operation. Run-11 targets remain sealed until the hash-only
> prediction freeze commit is remotely green. No dependency, EDF, target,
> model, prediction, or score operation occurred in the decision milestone.
> Preserve the unrelated tracker inspection NDJSON.
>
> Work-order-9 implementation update, 2026-08-09: authorization-only commit
> `da9399c4290fc2be81834ed1036a6bede5f52154` passed Base Python job
> `93334251403` and Optional Neuro Readers job `93334251379` in CI
> `31348287824` before implementation. Read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_IMPLEMENTATION.md`,
> `registries/physionet_motor_positive_control_implementation.v0.json`, and
> `src/neurodecodekit/experiments/physionet_motor_positive_control.py`. The
> narrow isolated classical environment, sequential MNE reader, exact 90/45
> split, function/artifact target firewall, causal preprocessing, fixed
> CSP-LDA/Riemannian selection, 12 controls and per-condition hashes,
> aggregate scorer, resource guards, and two dry-run-first CLI commands are
> generated-fixture qualified. The final fixture used nine runs, 135 events,
> 33 fits, 45 target-blind inferences, 12 prediction sets, 8.961233 seconds,
> 327,647,232-byte peak RSS, and 20,825,424 bytes. All gates passed with zero
> real-data, real-target, or network reads; the disposable output was removed.
> Its synthetic `WO9-V2` has no claim value. The exact implementation must now
> be committed, pushed, and remotely green before the one real no-network
> execution. Do not stat or open the bundle before that gate. If the execution
> succeeds, commit/push its aggregate freeze and wait for both green jobs before
> opening the sealed 45-target file once. Never rerun either real stage.
> Preserve the unrelated tracker inspection NDJSON.
>
> Work-order-9 prediction-freeze update, 2026-08-09: exact implementation
> `52b9b15a64972a285efbe630f49600727e836983` passed Base Python job
> `93343718364` and Optional Neuro Readers job `93343718355` in CI
> `31351728650` before one real target-blind execution. Read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREDICTION_FREEZE.md` and
> `registries/physionet_motor_positive_control_prediction_freeze.v0.json`.
> All nine exact EDF hashes and semantic parses passed; 135 events yielded 90
> fit rows and 45 target-free final signal rows. Runs 03/07 selected CSP-LDA;
> 33 fits, 45 target-blind inferences, three priors, and 12 prediction sets
> froze in 3.054760 seconds at 460,734,464-byte peak RSS with 20,852,059
> private bytes. Network/new payload, final target, score, retry, and rerun
> counters were zero. The aggregate freeze file SHA-256 is
> `3c100daa8a6a2816ce4270c9e32cbdcc4cd30d70d1c255e37596c2ca6f665de4`
> and contains no individual output. The private execution root remains
> Git-ignored; do not inspect, stage, publish, or reopen it now. Commit/push the
> aggregate freeze, tests, and docs, and require both CI jobs green. Only then
> may the isolated scorer open the same sealed 45 targets once. No rerun or
> post-target change is authorized. Preserve the unrelated tracker inspection
> NDJSON.
>
> Work-order-9 result update, 2026-08-09: freeze
> `01eeff6e9a5ead1790e0f91aa52a443402eb397c` passed Base Python job
> `93345130576` and Optional Neuro Readers job `93345130569` in CI
> `31352250838` before one target delivery and one score. Read
> `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_RESULT.md` and
> `registries/physionet_motor_positive_control_result.v0.json`. The selected
> 8-30 Hz CSP-LDA primary reached 27/45, 0.603755 pooled BA, and `p=0.137390`
> versus 0.500 for the prior; it failed the frozen primary conjunction and
> routed `WO9-V1`. The prespecified 0.5-4 Hz comparator reached 36/45, 0.800395
> pooled BA, 0.800595 macro-participant BA, all three participants above
> chance, and `p=0.000183`. Preserve that as a strong held-out task-information
> result, not a retrospectively promoted primary or brain-specific motor
> claim. Motor physiology failed at `p=0.108337`, and central sensors
> underperformed the frontal/occipital proxy. Total registered runtime was
> 9.661659 seconds, peak RSS 460,734,464 bytes, private output 20,852,334
> bytes, public output 10,443 bytes, and every resource gate passed. Work order
> 9 is complete and consumed with no rerun. Do not reopen the private root,
> tune on these outcomes, or publish individual output. A future independent
> low-frequency replication/localization study needs untouched data, a new
> preregistration, and separate Tier C authorization. Preserve the unrelated
> tracker inspection NDJSON.
>
> Additive strategy refresh, 2026-08-06: read
> `docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md` and
> `registries/open_eeg_rd_strategy.v0.json`. Current open EEG benchmarks
> reinforce the compact specialist-first path. The next prospective upgrade is
> a separately contracted public motor positive control over nine PhysioNet
> EDF files totaling 23,248,224 bytes, followed by one public-data-selected
> classical family and a fixed causal motor-physiology assay in the future
> Loop 55 design. Local-first contributor receipts are the data-scale strategy;
> foundation models and generative imputation remain later public-data lanes.
> No PhysioNet payload, S20 path, target, model, checkpoint, training,
> inference, score, or upload opened. Do not download or implement a real-data
> adapter from the strategy alone.
>
> Current handoff, 2026-07-17 after the Loop 55 synthetic AI-policy milestone:
> policy commit `8855fae` is pushed and remotely green; implementation commit
> `bd52cce` adds a pure-standard-library validator, three CLI
> commands, a strict 1,771-byte synthetic proposal, canonical hashes, bounded
> report writing, and adversarial tests. The committed proposal validates at
> SHA-256 `146232dc22864cde88202aa70a42621d58d73f3cfc8dd31dfd07c64360cc0278`.
> One measured CLI pass read 11,949 policy bytes and 1,771 proposal bytes,
> finished in `0.000741542` seconds, and reported 21,856,256-byte peak RSS with
> zero raw-data, cache, model, training, inference, scoring, network, LLM,
> stream, device, or hardware operations. Preserve the unrelated tracker
> inspection NDJSON. The tool validates synthetic proposals only; Loop 55
> remains `Not Started`, Loop 54 dependent, and separately unauthorized. Do not
> open or interpret S20, create a split, train a model, or run a real AI proposal
> from this milestone.
> The first implementation CI exposed one historical Loop 53 CLI hash test that
> incorrectly treated the shared CLI as immutable. Repair commit `f50be96`
> preserved the consumed hash as historical evidence, retained the Loop 53
> command checks, and passed push CI `29621564301`. Final local verification
> passed 1,087 tests with 3 expected skips in 21.592 seconds at 636,977,152-byte
> external peak RSS; Ruff, compilation, focused CLI help/roundtrip, JSON
> validation, and `git diff --check` passed.
>
> Current handoff, 2026-07-17 after the one Loop 53 acquisition: authorization
> commit `2a47bbc` passed push/PR CI `29589212626` / `29589225113`, and
> implementation commit `8ec5b1b` passed `29591387642` / `29591391286` before
> the registered invocation. The exact four-file S20 session-2 block-2 bundle
> passed revision, availability, license, path, size, Git/LFS/Xet, resource,
> isolation, and receipt gates. It transferred and retained 96,090,264 bytes in
> 3.629499 seconds at 63,225,856-byte peak RSS and 102,035,529-byte peak disk;
> the private receipts total 8,265 bytes. Every header, marker, signal, MAT,
> target, cache, split, checkpoint, model, training, inference, scoring,
> language-model, RW3, stream, device, hardware, additional-file, additional-
> participant, and rerun counter is zero. Loop 53 is consumed with no rerun.
> Stop before Loop 54: the bundle remains uninterpreted and each applicable
> L54-A/B/C content stage still needs its own exact Tier C decision after its
> implementation is pushed and remotely green. Read
> `docs/LOOP_53_ACQUISITION_RESULT.md` and
> `registries/loop53_acquisition_result.v0.json`. Preserve the unrelated
> tracker inspection NDJSON and never commit the payload or private receipts.
> Final local verification passed 68 focused tests and the complete 1,062-test
> suite with 3 expected skips in 44.090 seconds; Ruff, compilation, all 65
> registry JSON files, both CLI help surfaces, workbook formula/visual checks,
> and `git diff --check` also passed.
>
> Current handoff, 2026-07-16 after Loop 56 cross-modality planning research:
> the current
> branch freezes `docs/LOOP_56_PRIMARY_SOURCE_RESEARCH.md`,
> `registries/loop56_cross_modality_accessibility_research.v0.json`, and their
> tests. Five verdict classes, 12 capability levels, 18 comparison dimensions,
> 16 claim fields, 28 gates, 34 refusals, and a 12-part at-home conjunction now
> prevent shared software from being mislabeled shared scientific evidence.
> The current provisional route is `L56-O2`, mechanics and interfaces only.
> Registered local S21 MEG and historical S7 EEG predictors remain negative
> against their no-signal comparators and are not a matched modality
> comparison; fresh S20 has acquisition evidence only and remains
> uninterpreted. Continuous input is not
> causal incremental output or measured end-to-end latency. No payload,
> target, prediction, checkpoint, model, training, score, device, home, or
> claim action occurred. The final Loop 56 verdict is `Not Started`, Loop 55
> result dependent, and requires a separate exact Tier C claim decision after
> an exact aggregate-only preregistration is green. Preserve the unrelated
> tracker inspection NDJSON.
> Planning commit `6583ca3` passed push CI `29586877054` and PR #34 CI
> `29586915269`; Base Python and Optional Neuro Readers passed in both.
>
> Current handoff, 2026-07-16 after Loop 55 planning research: commit `f3158c7`
> freezes the future fresh-EEG neural-effect question in
> `docs/LOOP_55_PRIMARY_SOURCE_RESEARCH.md` and
> `registries/loop55_eeg_neural_effect_research.v0.json`. The design uses two
> ordered endpoints from the same frozen final trials: causal pre-keypress
> performed-hand error and harder causal 29-class performed-key keypress-aligned
> CER. Performed action is primary, intended text is secondary, and the
> published `[-200,+300] ms` window is a post-keypress diagnostic only. The
> future gate requires at least 48 Loop 54-qualified trials, one grouped split,
> one `<=10,000`-parameter causal family, at most 12 fits, twelve matched
> no-signal/timing/corruption/peripheral conditions, exact trial-level tests,
> and a committed, pushed, remotely green final-prediction freeze before one
> target delivery. Hard ceilings are one thread/worker, 45 CPU minutes, 1 GiB
> RSS, and 64 MiB generated output. Focused roadmap/contract checks passed
> 24/24 plus 9 public-status subtests; the full suite passed 1007 tests with 3
> expected skips and 365 subtests in 31.88 seconds; Ruff and `git diff --check`
> passed. No S20 path, payload,
> split, target, model, checkpoint, training, inference, score, download,
> stream, device, hardware, or scientific result was accessed. Loop 53 remains
> the next irreversible decision. Loop 55 is `Not Started`, Loop 54 dependent,
> and unauthorized. Preserve the unrelated tracker inspection NDJSON.
> Documentation-sync commit `8efcb17` passed push CI `29473032843` and PR #33
> CI `29473045583`; Base Python and Optional Neuro Readers passed in both.

> Current handoff, 2026-07-16 after Loop 54 planning research: commit `aec440a`
> freezes the acquisition-dependent EEG qualification design in
> `docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md` and
> `registries/loop54_eeg_trial_geometry_research.v0.json`. Six primary sources
> and the committed extractor were audited without S20 access. The future path
> is L54-A strict VHDR-only metadata with no MNE or sibling-file resolution;
> L54-B target-blind VHDR+EEG quality with every source channel retained and no
> transform; L54-C isolated target-bearing VMRK+MAT reconciliation with no
> plaintext protected values in public output; and L54-D aggregate closeout.
> At least 48 unique performed trials must reconcile, event windows are not
> independent trials, and Loop 54 creates no split or model. The boundary has
> 22 gates, 30 refusals, one thread/worker, at most 1 GiB RSS per stage, and at
> most 32 MiB combined public output. The complete local suite passed 996 tests
> with three expected skips in 30.312 seconds; focused 22/22, Ruff, JSON, and
> `git diff --check` also passed. Loop 53 remains the next irreversible
> decision and is still unauthorized. Do not implement or open L54-A until a
> clean Loop 53 receipt exists and a separate exact L54-A decision is recorded,
> pushed, and remotely green. No S20 local stat/hash, header, marker, signal,
> MAT, target, split, model, training, inference, score, or scientific result
> occurred. The unrelated tracker inspection NDJSON remains untouched.
> Documentation-sync commit `b6785d7` passed push CI `29471589279` and PR #32
> CI `29471598364`; Base Python and Optional Neuro Readers passed in both.

> Current handoff, 2026-07-15 after Loop 53 registration: the accessible EEG
> lane is now preregistered at an acquisition-only boundary. Registration
> commit `bccd367` binds S20 session 2 block 2 at pinned revision
> `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`: one BrainVision triplet plus
> one MAT log, four exact files, and 96,090,264 bytes. Push CI `29469813041`
> and PR #31 CI `29469829357` passed Base Python and Optional Neuro Readers.
> The exact request is `docs/LOOP_53_AUTHORIZATION_PACKET.md` plus
> `registries/loop53_authorization_request.v0.json`; every execution flag is
> false. No S20 payload download, local path stat/hash, header, marker, signal,
> MAT, target, cache, split, model, training, or score occurred. The next
> decision is whether the user sends the exact sentence unchanged. If received,
> record a separate authorization-only decision and obtain green push/PR CI
> before implementation. Then implement and fixture-qualify without payload
> access, commit/push/green again, and only then perform the one registered
> acquisition. Stop before Loop 54. Do not revive the older broad S20 packet.

> Current handoff, 2026-07-15 after Loop 48 Stage B: the one-shot train-only
> diagnostic is complete and consumed. Implementation commit `1d840e3` passed
> push CI `29461579009` and PR CI `29461580293` before protected access.
> Hash-only prediction-freeze commit `00215b1` passed push CI `29461934145`
> and PR CI `29461935560` before the same 11 train-check targets opened once.
> The primary causal candidate reached macro CER `0.953566` versus `0.822045`
> for the train-only prior. All three full-size causal and all three full-size
> linear fits were finite and stable, but none cleared the prior rule. The
> registered support vector therefore supports `H4` stable nonseparability,
> records evidence against fixed-shift `H3`, and leaves `H1/H2/H5/H6`
> unresolved. The complete signal-control conjunction failed; no neural
> advantage or sensor-signal dependence was established. The frozen Loop 50
> router selects `L50-R05`, parking S24 acquisition for this model family.
> S24 remains metadata-only and unopened; S25 remains sealed and final-only.
> Stage B used one thread, 20 fits, 4,800 optimizer steps, 35 inferences, five
> priors, 41 frozen sets, `190.140486` cumulative execution seconds through
> freeze, `483,540,992`-byte maximum RSS, and `9,623,773` generated bytes.
> Stage B has no rerun, post-check tuning, larger-model escalation, or claim
> upgrade. The machine result is
> `registries/loop48_train_only_discrimination_result.v0.json`; the readable
> closeout is `docs/LOOP_48_STAGE_B_RESULT.md`.

> Historical handoff immediately before Stage B execution: Loop 25 v1 and scientific Loop 45 remain complete
> at their one-time target-free mechanics boundary. The shared Loop 26/31/33
> event is now consumed and parked after its registered scientific gates
> failed. Prediction-freeze commit `54bdca9` was pushed and remotely green
> before the six targets opened once. The fixed candidate reached macro CER
> `0.938177` versus `0.751235` for the train-only prior, a `-0.186942` margin;
> the attribution conjunction and scaling gate also failed. Engineering,
> access-order, one-thread, 1 GiB RSS, and 32 MiB artifact gates all passed.
> Five source-test rows, session 2, post-target tuning, and any rerun remain
> closed. Loop 48 completed exactly one artifact-only Stage A after separate
> authorization commit `5bae880` and implementation commit `ca21539` were each
> pushed and remotely green. The frozen tree selected descriptive `F5`
> output-distribution instability from four committed aggregate JSON files.
> Internal runtime was `0.016568875` seconds, peak RSS was 23,429,120 bytes,
> and the consumed report is 10,643 bytes at SHA-256
> `dbfb4c7cc6163ff31fa216c1b33e7510a87b0b843ef714754037d37275924659`.
> This is not a proven root cause, and no rerun is authorized.
> Closeout commit `6322635` passed push CI `29446438743` and PR CI
> `29446440355`.
> The additive six-hypothesis pass has now advanced to one exact Stage B
> preregistration: 44 fit rows, 11 target-withheld check rows, five nested
> sizes, three fixed seeds, 20 fits, 35 target-blind inferences, five priors,
> 41 prediction sets, and 2,048 exact sign assignments. All 55 rows were used
> historically, so the check partition is not independent confirmation and
> the result ceiling is E2 diagnostic evidence. Preregistration commit
> `0ee0ab7` passed push CI `29452286159` and PR CI `29452288520`. The separate
> packet and machine request are prepared at
> `docs/LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md` and
> `registries/loop48_stage_b_authorization_request.v0.json`. The exact
> one-run decision is now recorded in
> `docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md` and
> `registries/loop48_stage_b_authorization_decision.v0.json`, effective only
> after its authorization-only commit is remotely green. No implementation,
> protected read, model operation, or score exists yet.
> Loop 49 planning research now selects S24 session 2 block 2 as the preferred
> permanently development-only MEG person from pinned public metadata. The
> exact two-file bundle is `1,048,579,727` bytes; S24 avoids the S1/S18 alias
> while S25 remains final-only. No S24 path or payload was opened, the `>=48`
> unique-row and compatibility gates remain unproven, and Loop 49 remains `Not
> Started`, unpreregistered, and unauthorized. Planning commit `5afa61e` passed
> push CI `29454969710` and PR #27 CI `29455166081`; both required jobs are
> green.
> Loop 50 planning research is now complete while its experiment remains `Not
> Started`. The design freezes global text grouping, five historical S21
> out-of-fold folds, a 16-group S24 development gate, equal-person loss, one
> shared candidate family, ten conditions, primary seed `5001`, two
> nonselectable stability seeds, an exact 20-update inventory, and a worst-
> person gate. All 31 authorization fields are false; no exact model, protected
> read, training, inference, prediction, or scoring event exists. Stage B
> remains the next protected decision, S24 remains unopened, and S25 remains
> final-only.
> Planning commit `085f341` passed push CI `29458102674` and PR #28 CI
> `29458116994`; both required jobs are green in both workflows.

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

Governance note: `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md` is the byte-identical
approved charter snapshot and `docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md` is
its activation record. After that decision is remotely green, Tier A routine
work and Tier B bounded development experiments proceed autonomously. Tier C
irreversible evidence, real-data, hardware, destructive, release, and claim
actions still require a separate exact decision; no existing narrow contract
is loosened.

1. **Loop 48 - qualify the exact Stage B authorization before implementation.**
   Read `docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md` for the
   descriptive `F5` Stage A result; do not rerun or tune it. Stage B is now
   frozen in `docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md` and
   `registries/loop48_train_only_discrimination_contract.v0.json`: 44 fit rows,
   11 check rows, 20 fits, 35 target-blind inferences, five priors, 41 prediction
   sets, and an E2 ceiling. The exact one-run authorization is separately
   recorded in `docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md`; no
   implementation or protected access may begin until that decision commit is
   remotely green. Check targets remain sealed until the later prediction-
   freeze commit is also remotely green.
2. **Loop 49 - preserve the metadata-only S24 development decision.** Read
   `docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop49_research_boundary.v0.json`. S24 session 2 block 2 is the
   clean-identity candidate at 1,048,579,727 bytes; S25 stays final-only. The
   future recommendation is 16 canonical sentence groups for selection and at
   least 32 for fit, with matching S21 selection text excluded from fit. No S24
   path or content was opened. Decision 0083 requires Stage B to close or park
   before acquisition; the trial floor, channels, geometry, duration, and text
   overlap remain unavailable. Do not prepare or execute acquisition, open a
   backup, or claim person transfer from metadata selection.
3. **Loop 50 - preserve the planning-only multi-source boundary.** Read
   `docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md` and
   `registries/loop50_research_boundary.v0.json`. It freezes global text
   grouping, five historical S21 out-of-fold folds, equal-person loss, one
   shared candidate family, ten conditions, one primary plus two nonselectable
   stability seeds, an exact 20-update inventory, and a both-person/worst-person
   gate. The experiment is `Not Started`; do not select an exact model, access
   S24/S25, read the S21 cache, train, infer, freeze predictions, or score from
   this boundary.
4. **RW3 - decide on the prepared Stage A packet only.** Review
   `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md` and
   `registries/rw3_stage_a_authorization_request.v0.json`. The request is bound
   to commit `c3d1f01` and its exact contract hash, but `authorized_now` remains
   false. Do not implement Stage A without an explicit user decision followed
   by a pushed authorization-only commit; BrainFlow, LSL, PyXDF, sockets, live
   sources, hardware, and Stages B-D remain later independent gates.
5. **Use Loops 27-44 and 48-64 as future evidence queues, not blanket
   authorization.**
   Read `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
   `docs/LOOPS_25_44_ROADMAP.md`, and
   `registries/next_20_loops.v0.json`. Loop 26/31/33 and scientific Loops 46/47
   are consumed negative results with no rerun. For Loop 27,
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

The critical sequence has stopped at the failed Loop 46/47 S21 gate. Loop 48
completed one artifact-only Stage A and selected descriptive `F5`, but did not
establish a root cause. Its result is consumed and no rerun is authorized. The
additive H1-H6 discrimination map remains design-only and preserves an `E3`
ceiling below brain-specific origin; only a separately designed non-S25
development-person path could
later reopen the predictive branch before Loop 52's one-time S25 verdict. S21
session 2 and S7 stay consumed; S25 stays unopened and final-only. EEG,
streaming, device, home, reproduction, and release phases remain downstream
and separately authorized.

Loop 49 planning research now provides that development-person metadata
decision without opening data. S24 session 2 block 2 is the preferred clean-
identity candidate: two pinned files totaling 1,048,579,727 bytes, 293,597,553
bytes below the future 1.25 GiB cap. S24 is selected over the 29,701,559-byte-
smaller S18 pair to avoid the S1/S18 alias. The future text-grouped split
reserves 16 unique sentence groups for selection, requires at least 32 fit
groups, and excludes matching S21 selection text from future fit. All 25
authorization fields and every protected/model counter remain false. The
`>=48` trial floor and every header/signal/target compatibility field are still
unavailable, so Loop 49 remains experimentally `Not Started` and cannot support
a transfer or decoding claim.

Loop 50 planning research now provides the corresponding model-design boundary
without opening data. It requires one global text assignment across people,
five-fold historical S21 out-of-fold behavior, one 16-group S24 development
qualification, equal participant loss, no participant-conditioned path, ten
fixed candidate/control conditions, an exact 20-update inventory, and separate
per-person and worst-person passes. Primary seed 5001 is immutable and cannot
be replaced by stability seeds 5002/5003. All 31 authorization fields and every
protected/model counter remain false, so this is not a preregistration,
execution, or result.

The tracker has ten sheets, including `Loops 45-64`. After the consumed Loop 48
Stage A closeout it is 117,187 bytes at SHA-256
`7e6424cd5f69d29f78ea7335d1cf277d293eeac4071668991f66d37d7679d4c3`.
The dashboard, decision `48-R5`, evidence-roadmap summary, and scientific Loop
48 row passed focused visual review. All ten sheets received a post-edit visual
pass, the formula-error scan found zero matches, and ZIP integrity passed. The
final artifact-tool update/export took 11.04 seconds and reached
1,572,667,392-byte maximum RSS; do not repeat full workbook imports casually.
The adjacent user-owned inspection sidecar was not read, modified, staged, or
committed during this closeout.

Current local acceptance passes 86 focused Loop 48/roadmap tests plus five
autonomy-charter invariants, 781 dependency-light tests with 142 expected
skips, and 828 optional-neuro tests with 3 expected skips. The final
dependency-light run took 1.318 seconds at 110,821,376-byte maximum RSS; the
final optional-neuro run took 26.177 seconds at 611,926,016-byte maximum RSS.
Ruff lint, changed-file formatting, compileall,
every registry JSON, root and Loop 48 CLI help, result inspection,
`git diff --check`, workbook inspection/render/formula/ZIP checks, and the
staged secret scan are the closeout gates. Repository-wide `ruff format
--check .` still reports 106 historical files outside this closeout; those
unrelated files were deliberately not reformatted.

Closeout commit `6322635` passed push CI `29446438743` and PR CI
`29446440355`; both Base Python and Optional Neuro Readers jobs were green.

## Loop 48 Stage B Handoff

Loop 48 Stage B is complete after one registered execution. The exact machine
result is `registries/loop48_train_only_discrimination_result.v0.json` at
SHA-256 `ef8290eb45e755bedb2deed781e6e472aa3621c25d91a01d01626c17c96ce891`.
The readable closeout is `docs/LOOP_48_STAGE_B_RESULT.md`.

The access order passed exactly:

1. Authorization commit `8d17342` became remotely green.
2. Implementation commit `1d840e3` passed push CI `29461579009` and PR CI
   `29461580293` before protected access.
3. One source-cache hash pass delivered 44 fit signal/target rows and 11 check
   signal rows; check targets remained absent.
4. Twenty fits, 4,800 optimizer steps, 35 target-blind inferences, five priors,
   and 41 prediction sets completed under one CPU thread.
5. Hash-only freeze commit `00215b1` passed push CI `29461934145` and PR CI
   `29461935560` with zero check-target delivery and zero score.
6. The same 11 check targets opened once and one score completed. No validation,
   source test, session 2, S24, S25, post-check update, or rerun occurred.

The primary causal candidate reached macro CER `0.953566`; its matched
train-only prior reached `0.822045`. All six full-size causal and linear probes
were finite and stable, but none cleared the prior rule. `H4` stable
nonseparability is supported. No fixed `-50/-25/+25/+50` shift improved all
three seeds, so `H3` has evidence against it. `H1`, `H2`, `H5`, and `H6` remain
unresolved. The exact-zero and timing-only component wins remain diagnostic
only because the primary failed the prior and complete corrupted-signal
conjunction.

The applied Loop 50 route is `L50-R05`: park S24 acquisition for this model
family. Do not prepare S24 acquisition, substitute another person, open S25,
rerun Stage B, tune from the 11 check outcomes, or promote a scientific claim.
S24 remains metadata-only. S25 remains physically unopened and final-only.

The next reversible work is Tier A representation-repair research and contract
design only. A real-data repair run, new parameter update based on this
post-outcome diagnosis, new participant acquisition, or any sealed-target event
is Tier C and still requires a separate exact maintainer decision under the
Research Autonomy Charter.

Measured execution stayed bounded: `190.140486` cumulative seconds through
freeze, `483,540,992`-byte maximum peak RSS, `9,623,773` generated bytes, one
`10,632,576`-byte cache hash pass, zero downloads, and more than 41 GB free disk
at the static gate. The model has two frames of left context and zero right
context, but the upstream cache is offline/noncausal and end-to-end latency is
unmeasured.

Local closeout acceptance passes 63 focused Stage B tests in 6.758 seconds
internal time and 7.39 seconds wall time at 316,719,104-byte maximum RSS. The
complete dependency-light suite passes 887 tests with 149 expected skips in
1.377 seconds internal time and 1.63 seconds wall time at 124,157,952-byte
maximum RSS. The complete optional-neuro suite passes 934 tests with 3 expected
skips in 29.827 seconds internal time and 30.79 seconds wall time at
609,648,640-byte maximum RSS. Both complete suites add exactly nine result and
closeout invariants over their 878/925-test implementation baselines without
losing a prior test. Result closeout commit `ad4410c` passed push CI
`29464527230` and PR CI `29464529524`, with Base Python and Optional Neuro
Readers green in both workflows.

## Loop 48 Stage C Representation-Repair Handoff

Stage C planning research and its one synthetic execution are complete in
`docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md` and
`registries/loop48_stage_c_representation_repair_research.v0.json`, with the
result in `docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md` and
`registries/loop48_stage_c_synthetic_result.v0.json`. Research selected
one narrow, falsifiable explanation for the Stage B failure: the original
candidate's 20 ms learned left context may be too short to represent relevant
temporal structure. The consumed synthetic result supports only the narrow
mechanics contrast described below.

The exact comparison is frozen before implementation: a 7,692-parameter
`TinyCausalTemporalCTC-v0` with 470 ms left context versus a 7,568-parameter
`TinyCausalTemporalAblation-v0` with no learned temporal history. Both emit on
the same 25 Hz grid and have zero right context. The candidate contains four
causal kernel-5 blocks with dilations `1,2,4,1` and a learned depthwise
kernel-16/stride-4 feature reducer; the reducer is not an anti-aliased waveform
resampler.

After correction commit `2836ecc` passed push CI `29467415680` and PR CI
`29467416894`, the one seed-4850, 40-row, 24/8/8 synthetic calibration ran.
The candidate reached final CER `0.433333` and `1/8` exact sequences versus
ablation CER `1.000000`. The `0.566667` relative CER improvement, causality,
length, padding, checkpoint replay, mutation, resume, and resource checks
passed. The absolute CER `<=0.10` and exact-sequence `>=7/8` gates failed.
Stage C is consumed and parked without tuning or rerun.

No protected Stage C contract exists. Do not stat, hash, or read the S21 cache;
do not reuse its 44 fit rows or reopen its 11 consumed check rows; do not touch
validation, source test, session 2, S24, or S25; and do not perform a real model
operation or promote a scientific claim without a separate exact Tier C
decision.

Implementation is recorded in
`docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md` and
`registries/loop48_stage_c_synthetic_implementation.v0.json`. The exact models,
fixture, bounded gate, numeric checkpoints, and two CLI commands passed their
zero-update qualification before execution. The consumed run used four fits,
1,680 optimizer steps, 7.829308 seconds, 310,509,568-byte peak RSS, 83,132
generated bytes, and zero real-data, real-cache, real-target, download, S24,
S25, stream, device, or hardware operations. Do not rerun it or promote its
synthetic candidate-ablation difference into a real neural result.

## WO9R Low-Frequency Cohort-Confirmation Handoff

Work Order 9 remains complete and consumed at `WO9-V1`; do not reopen its
private output or 45 final targets. Its prespecified `0.5-4 Hz` comparator is a
valid held-out lead at 36/45, 0.800395 pooled balanced accuracy, and
`p=0.000183`, but central localization and motor physiology failed.

Tier A follow-up research is now recorded in
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PRIMARY_SOURCE_RESEARCH.md`
and
`registries/physionet_low_frequency_cohort_confirmation_research.v0.json`.
The additive lane is called `WO9R` so work orders 10-20 are not renumbered.
It selects the contiguous untouched S004-S015 cohort and execution
`03/07 -> 11` plus imagery `04/08 -> 12`, for a prospective 72 EDFs and 360
sealed-final events.

The sole primary template is the unchanged Work Order 9 low-frequency
comparator: causal continuous `0.5-4 Hz`, common-average reference, a `+1` to
`+3` second cue-aligned window, four means plus one slope per channel, and
fixed shrinkage-LDA `0.1`. Native execution, native imagery, execution-to-
imagery, and imagery-to-execution predictions must freeze together. Central,
frontal, occipital, ocular-sensitive asymmetry, early/pre-cue, timing,
no-signal, label, displacement, channel, and hemisphere controls are mandatory.

The future router is `WO9R-R0` through `WO9R-R4`. `R2` can honestly establish
new-cohort task-information confirmation even if cue/localization gates fail;
`R4` requires execution, imagery, participant-level, central-lateralization,
and all control gates. Even `R4` is not brain-specific because the dataset has
no dedicated EOG/EMG or measured movement onset.

The exact metadata and preregistration step is now complete. Contract commit
`716e5432498052b78cb799c9f4e3bfbae68e3ad2` passed Base Python job
`93351737101` and Optional Neuro Readers job `93351737088` in CI
`31354565966`. It freezes 72 exact paths and official SHA-256 values totaling
184,252,032 bytes, 720 expected fit rows, 360 jointly sealed final rows, 144
fit ceilings, 18 conditions, 216 target-blind participant-condition prediction
sets, literal controls, participant-level gates, one combined target delivery,
and no rerun. The registration read 13 public metadata bodies totaling 340,703
bytes from the official S3 listings and checksum manifest, with zero EDF URL
requests or payload bytes.

The all-false request is prepared in
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md` and
`registries/physionet_low_frequency_cohort_confirmation_authorization_request.v0.json`.
Request commit `580708fa1f24772a2f9d7cfd572a421b860a1f14` passed Base Python
job `93353672957` and Optional Neuro Readers job `93353672996` in CI
`31355270896`. The maintainer then explicitly declined further long-form
recital and directed the currently presented WO9R packet to continue. Preserve
the actual message and packet-bound interpretation in
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_DECISION.md`
and its machine registry; do not claim the maintainer typed the long packet
sentence. The separate decision-only commit must become remotely green before
fixture implementation. Decision commit
`1efeac7f0b7b316bb94effb1a2eeeb1bbf99f50a` passed Base Python job
`93355535398` and Optional Neuro Readers job `93355535361` in CI
`31355944651` before fixture work began.

The exact implementation is now recorded in
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_IMPLEMENTATION.md` and
`registries/physionet_low_frequency_cohort_confirmation_implementation.v0.json`.
It adds dry-run-first acquisition, analysis, and scoring CLIs; a no-redirect
standard-library acquisition stream; strict sequential EDF parsing; compact
causal 5C features; a 720-row fit derivative; a 360-row target-free prediction
derivative; a separate sealed-target artifact; exactly 144 participant-specific
fits and 216 target-blind prediction sets; a combined aggregate hash-only
freeze; and an aggregate one-shot scorer. Analysis is marked consumed before
the first bundle inspection, and scoring is marked consumed before the first
private or sealed-target hash/open.

One generated 72-run qualification passed all engineering gates in 12.083017
seconds at 260,784,128-byte peak RSS with 4,215,687 generated bytes, zero
network, zero real reads, and zero real targets. The synthetic router produced
`WO9R-R3`, which has no scientific meaning. All generated files were removed.
Twenty-nine focused tests now cover the complete roundtrip, deterministic
replay, malformed metadata/payload/cache/freeze/private predictions, target
leakage, exact counts, output/resource caps, symlink refusal, dry-run CLIs, and
both consumed-before-access invariants.

Implementation `8242674e5821b2c923c0c79baa3a6ea20a27d838` passed Base
Python job `93365527795` and Optional Neuro Readers job `93365527849` in CI
`31359548779` before the one real acquisition and target-blind execution. All
72 official EDF hashes matched over 184,252,032 bytes. Acquisition used
518.051205 seconds and 73,089,024-byte peak RSS. The analysis accepted 1,080
events, created 720 fit rows and 360 target-free final rows, completed 144 fits
and 216 prediction sets, and emitted the combined aggregate freeze in
19.864386 seconds at 303,153,152-byte peak RSS. No final target reached the
model stage.

Read `docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREDICTION_FREEZE.md`
and its public ledger. Freeze commit
`8cd45d74dfa3517ae53c1427a0eb06e27ad3c870` passed Base Python job
`93369101655` and Optional Neuro Readers job `93369101696` in CI
`31360781199` before the isolated scorer opened the same 360 targets once.

Read `docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_RESULT.md` and
`registries/physionet_low_frequency_cohort_confirmation_result.v0.json`.
Execution passed H1 at 123/180, pooled balanced accuracy `0.680975`, macro
`0.682292`, 9/12 participants above chance, and `p=0.002930`. Imagery passed H2
at 131/180, pooled `0.728014`, macro `0.728423`, 12/12 above chance, and
`p=0.000244`. Both cross-task transfer diagnostics were positive.

The frozen verdict is `WO9R-R3`. Central-over-proxy localization failed,
physiology was positive in only 5/12 participants, and early-cue, frontal, and
frontal-asymmetry controls exceeded their ceilings. This is robust held-out
task-information evidence across twelve fresh participants and two task modes,
not brain-specific motor decoding. The target delivery and score are consumed;
there is no retry, rerun, or post-target update. Preserve the unrelated
untracked tracker inspection NDJSON and every Git-ignored private artifact.

Next route: use Tier A research to specify a cue-neutral or independently
instrumented replication with synchronized EOG/EMG and measured movement
onset. Do not scale this classifier or reopen WO9R to answer the source-
localization question.

## 2026-08-10 IACKD-1 Implementation Gate

WO9R is complete and consumed at `WO9R-R3`. Do not reopen its private outputs,
targets, or models. The next source-attribution question is IACKD-1, not a
WO9R rerun or a larger classifier.

Read, in order:

1. `docs/IACKD_CUE_ACTION_DISSOCIATION_PRIMARY_SOURCE_RESEARCH.md`
2. `registries/iackd_openneuro_metadata_inventory.v0.json`
3. `docs/IACKD_CUE_ACTION_DISSOCIATION_PREREGISTRATION.md`
4. `registries/iackd_cue_action_dissociation_contract.v0.json`
5. `docs/IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_PACKET.md`
6. `registries/iackd_cue_action_dissociation_authorization_request.v0.json`
7. `docs/IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_DECISION.md`
8. `registries/iackd_cue_action_dissociation_authorization_decision.v0.json`
9. `docs/IACKD_CUE_ACTION_DISSOCIATION_IMPLEMENTATION.md`
10. `registries/iackd_cue_action_dissociation_implementation.v0.json`

Research `d6f955e` passed CI `31399402403`. Registration
`e42b79961d1fafe5cf406beaf868388ecbcbfb09` passed Base Python
`93493810963` and Optional Neuro Readers `93493811025` in CI `31400450392`.
The frozen design binds 1,340 objects, 7,249,113,684 bytes, 30
participant-hand units, congruent-to-incongruent reversal, direct EOG and Leap
controls, one model family, 300 fits, 420 prediction sets, and one score after
a green prediction freeze.

Request `ef78c06` passed CI `31401738032`. The maintainer's actual words,
`keep going, move the needle, continue, you approved to go on`, are recorded
without a fabricated long-form recital in decision `1f48b30`; it passed Base
Python `93502398308` and Optional Neuro Readers `93502398753` in CI
`31403012709` before implementation.

The implementation adds a strict standard-library acquisition layer,
one-run-at-a-time BrainVision/event/ball/Leap reconciliation, causal 0.5-4 Hz
features, a sealed dual-target firewall, 300 fixed fits, 420 target-blind
prediction sets, a strict aggregate freeze, and isolated scorer. Exact
implementation `f5c36ba` passed both jobs in CI `31409141349` before the one
real sequence.

Read `docs/IACKD_CUE_ACTION_DISSOCIATION_RESULT.md` and its registry. The one
acquisition passed: 1,340 objects, 7,249,113,684 bytes, 1,340 stream hashes,
679.749484 seconds, 126,205,952-byte peak RSS, and zero content parses. The one
analysis completed its 1,340-object integrity pass, then failed closed at
`IACKD-F10` on the first lazy BrainVision parse because the combined `32+4`
channel gate did not hold. The observed count and names were not retained.
No signal sample, channels TSV, geometry, event, ball/Leap stream, target,
derivative, fit, inference, prediction, freeze, or score followed. IACKD-1 is
consumed and parked with no rerun. Preserve the private bundle and unrelated
tracker-inspection NDJSON; do not reopen, delete, move, relax, or infer.

Do not touch the unrelated untracked
`docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx.inspect.ndjson`.

## 2026-08-10 IACKD-H1 Header Inventory Registration

Read `docs/IACKD_CHANNEL_INVENTORY_PRIMARY_SOURCE_RESEARCH.md`,
`registries/iackd_channel_inventory_research.v0.json`,
`docs/IACKD_CHANNEL_INVENTORY_PREREGISTRATION.md`, and
`registries/iackd_channel_inventory_contract.v0.json`.

The published paper reports a 32-channel cap and separately names M1, M2,
HEOG, and VEOG, but does not assert that every BrainVision file has exactly 36
channels. At upstream commit `c0b595d`, the authors' premovement code deletes
M1/M2/HEOG/VEOG/TRIGGER if present, while their execution code deletes
HEO/VEO/HEOG/VEOG/TRIGGER. This supports count, alias, and heterogeneity
hypotheses without establishing which one caused the consumed failure.

The new prospective contract filters the committed metadata inventory to all
128 VHDR objects and 161,792 bytes. It freezes sequential in-memory retrieval,
strict standard-library parsing, no sibling resolution, seven allowlisted
public-code name flags, aggregate signature hashes, six diagnostic routes, one
thread, 256 MiB RSS, 1 MiB network body, 2 MiB disk, 1 MiB output, and zero
retry or rerun. No real VHDR request, local bundle access, dependency, sample,
event, trajectory, target, model, prediction, or score has occurred.

After the registration commit is pushed and both CI jobs are green, implement
only generated fixtures and mocked transport under Tier B. Commit, push, and
obtain both green jobs for that exact implementation before preparing the sole
Tier C real-header packet. Do not treat any older `continue` as a retroactive
decision for that future packet, and never reopen the retained local bundle.

## 2026-08-10 IACKD-H1 Synthetic Implementation

Registration `0e52278aaa1d15e70f4baab7b21ab1c96eb37f67` passed Base Python
job `93534203368` and Optional Neuro Readers job `93534203385` in CI
`31412667060` before implementation.

Read `docs/IACKD_CHANNEL_INVENTORY_IMPLEMENTATION.md`,
`registries/iackd_channel_inventory_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_header_inventory.py`, and both
`tests/test_iackd_header_inventory*.py` files. The dependency-free module now
implements strict VHDR decoding, inert sibling validation, exact response
identity, sequential one-pass hashing and parsing, aggregate-only signatures,
all six frozen routes, bounded atomic output, a metadata-only inspector, and a
future decision-gated real executor.

Use the module CLI because the consumed IACKD-1 registry binds the unchanged
central `src/neurodecodekit/cli.py`:

```bash
PYTHONPATH=src python -m neurodecodekit.preprocess.iackd_header_inventory
```

Twenty-four core tests pass. One isolated generated qualification exercised all
128 registered sizes and 161,792 bytes in 0.037818958 seconds at 36,634,624-byte
peak RSS, producing 4,465 temporary output bytes. Network and all real or
protected counters were zero. The synthetic `IACKDH-R1` route has no real-data
or claim value.

Next gate: commit and push this exact implementation and require both CI jobs
green. Then prepare one packet binding that exact implementation. Do not fetch
a real header, touch the retained bundle, create a decision from old user
words, or run `--execute` before the later packet-bound Tier C decision is
committed, pushed, and remotely green.

## 2026-08-10 IACKD-H1 Authorization Request Prepared

Exact implementation `16621cc484f4bec4a9474b9ac20d5b7d9314152f`
passed Base Python job `93542494819` and Optional Neuro Readers job
`93542494839` in CI `31415213841`. The next files are
`docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_PACKET.md`,
`registries/iackd_channel_inventory_authorization_request.v0.json`, and
`tests/test_iackd_header_inventory_authorization_request.py`.

The request is all false. It asks for one later sequential audit of exactly 128
public OpenNeuro VHDR bodies and 161,792 bytes, with one SHA and one strict
parse per body, aggregate-only output, one thread, 120 seconds, 256 MiB RSS,
1 MiB network body, 2 MiB disk, 1 MiB output, and zero retry or rerun. It does
not permit the retained local IACKD bundle, siblings, samples, events,
trajectories, targets, models, inference, or scoring.

Next gate: commit and push the request, require both CI jobs green, then
identify that exact request commit, CI run, and sole scope to the maintainer.
Only a fresh unambiguous `continue`, `approve`, or `proceed` after that
identification may be quoted in a separate hash-bound decision. Do not use the
earlier continuation retroactively, fabricate a long user sentence, create the
decision early, or issue a real header request.

## 2026-08-10 IACKD-H1 Packet-Bound Decision Recorded

Request `56531c64b6733f93c9def80ad57125e0ee998fd8` passed Base Python
job `93546632359` and Optional Neuro Readers job `93546632280` in CI
`31416489006`. After Codex identified that sole packet, exact proof, scope, and
gate, the maintainer supplied a fresh instruction containing `continue`.

Read `docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_DECISION.md`,
`registries/iackd_channel_inventory_authorization_decision.v0.json`, and
`tests/test_iackd_header_inventory_authorization_decision.py`. The decision
quotes the complete actual message, binds the immutable contract,
implementation, request, packet, and green evidence, and authorizes exactly
one later 128-header/161,792-byte public audit with zero retry or rerun.

No real operation occurred while recording the decision. Next gate: test,
commit, push, and require both remote CI jobs green for the exact decision.
Only then run the module CLI once with the exact decision SHA and green commit/
job evidence. Never touch the retained local bundle, resolve a sibling, amend
the parser, or infer a scientific result from a header diagnosis.

## 2026-08-10 IACKD-H1 Consumed R5 Result

Decision `04f2706b56315186fac0c9a82686e9a360dbaf1e` passed Base Python
job `93572439094` and Optional Neuro Readers job `93572439047` in CI
`31424361969` before the sole execution.

Read `docs/IACKD_CHANNEL_INVENTORY_RESULT.md` and
`registries/iackd_channel_inventory_result.v0.json`. All eleven gates passed.
The audit made 128 public VHDR requests for 161,792 bytes, hashed and strictly
parsed each response once, and retained only a 5,515-byte aggregate ledger and
a 244-byte consumed marker. Runtime was 23.576352333 seconds and peak RSS was
94,650,368 bytes.

The result is `IACKDH-R5`: 96 headers declare 29 channels without M1/M2, and
32 declare 31 channels with M1/M2. All 128 include HEOG, VEOG, and TRIGGER and
declare 1024 Hz. The old exact-36 global invariant was wrong, and one global
channel list cannot describe all runs. The 29/31 totals are declarations, not
known EEG-channel counts.

No retained local bundle, sibling, signal, marker, event, trajectory, target,
feature, model, prediction, or score was accessed. The invocation is consumed
with no retry or rerun. Preserve both ignored receipts and the unrelated
tracker-inspection NDJSON. The next useful work is a separately named,
prospective count-agnostic cue-versus-action design; no retained-bundle step is
open without a new exact Tier C gate.

## 2026-08-10 IACKD Role-Aware Dual-Reversal Research

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md` and
`registries/iackd_role_aware_dual_reversal_research.v0.json`.

H1 closeout `a6704898cfb09f6321bac5f15e27424f02614317` passed Base Python
job `93575925675` and Optional Neuro Readers job `93575925695` in CI
`31425445891` before this Tier A pass. The pass used only committed aggregates,
the committed metadata inventory, public primary sources, and source code.

The consumed reader has more than a bad total-count constant: its BIDS check
expects 32/34 EEG rows, TRIGGER would fall through to EEG, and its fixture omits
the real trigger role. Do not amend it. The next bounded lane is IACKD-H2 over
128 channel tables, 128 EEG sidecars, 30 electrode tables, and 30 coordinate
systems: 316 objects and 457,602 bytes total, no local bundle.

The later IACKD-2 design is symmetric. `C2I` and `I2C` must both prefer actual
hand direction over the cue surrogate induced by the fit mapping. The weaker
participant-level arm margin is primary, so one arm cannot rescue the other.
At that research commit, no H2 preregistration, implementation, public-body
decision, local access, or IACKD-2 scientific gate existed. The next section
supersedes only the H2 preregistration part of that status.

## 2026-08-10 IACKD-H2 Role And Geometry Preregistered

Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_PREREGISTRATION.md`,
`registries/iackd_channel_role_geometry_contract.v0.json`, and
`tests/test_iackd_channel_role_geometry_contract.py`.

The prospective contract selects exactly 316 committed OpenNeuro BIDS metadata
objects and 457,602 bytes: 128 channel tables, 128 EEG sidecars, 30 electrode
tables, and 30 coordinate-system files. It freezes source-declared predictive
EEG, EOG, trigger, optional M1/M2, reference, status, and geometry semantics;
explicit unavailable values; one-pass bounded transport; aggregate-only
output; and routes `IACKDR-R0` through `IACKDR-R4`.

No H2 body or local IACKD path was opened. Next gate: test, commit, push, and
require both CI jobs green for this exact registration. Only then implement
the parser, mocked transport, router, resource guards, writer, inspector, and
module CLI on generated fixtures. Do not prepare a Tier C decision or make a
real request until that implementation is separately committed, pushed, and
remotely green.

## 2026-08-10 IACKD-H2 Synthetic Implementation Qualified

Registration `228ccd03f5e0b5d02ba104e13b77b04f2032df78` passed Base
Python job `93583989913` and Optional Neuro Readers job `93583989996` in CI
`31427931578` before implementation.

Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_IMPLEMENTATION.md`,
`registries/iackd_channel_role_geometry_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_channel_roles.py`, and
`tests/test_iackd_channel_roles.py`. The strict standard-library module now
covers all four metadata roles, one-pass mocked responses, private run and
geometry pairing, H1/sidecar reconciliation, aggregate role/geometry hashes,
all five routes, resource guards, exclusive output, bounded inspection, and a
dry-run-first module CLI.

One final generated qualification processed all 316 registered sizes and
457,602 bytes in 0.054679625 seconds at 34,996,224-byte peak RSS, emitting
8,282 bytes. Constructed `IACKDR-R4` has no real-source or scientific meaning.
Forty-seven focused, 1,751 base, and 1,822 optional tests pass locally.

Next gate: finish static/CLI verification, commit and push the exact
implementation, and require both remote CI jobs green. Only then prepare one
all-false H2 Tier C request. Do not fetch any public H2 body, inspect the local
bundle, or enter IACKD-2 before that later packet sequence.

## 2026-08-10 IACKD-H2 All-False Request Prepared

Exact implementation `9f6fef9540ae0a1fe52cbf24b17b0af89147beae`
passed Base Python job `93591323731` and Optional Neuro Readers job
`93591323646` in CI `31430151368`.

Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_PACKET.md`,
`registries/iackd_channel_role_geometry_authorization_request.v0.json`, and
`tests/test_iackd_channel_role_geometry_authorization_request.py`. The request
binds one possible later sequential pass over exactly 316 public metadata
bodies and 457,602 bytes. Every execution flag is false; preparing it made no
request, parse, local-path operation, model run, score, or claim change.

Next gate: test, commit, push, and require both remote CI jobs green for the
exact packet. Then identify the sole IACKD-H2 packet, commit, CI run, 316-body
scope, and decision boundary to the maintainer. Only a fresh unambiguous
`continue`, `approve`, or `proceed` after that identification may be quoted in
a separate decision. Do not reuse the current continuation retroactively and
do not run the audit from the packet alone.

## 2026-08-10 IACKD-H2 Packet-Bound Decision Recorded

Request `86174bc86123bc010bac2f40a9d72147dc8aef05` passed Base Python job
`93594327147` and Optional Neuro Readers job `93594327069` in CI
`31431064259`. After Codex identified it as the sole active Tier C packet and
named the exact 316-body/457,602-byte scope, the maintainer replied
`continue :)`.

Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_DECISION.md`,
`registries/iackd_channel_role_geometry_authorization_decision.v0.json`, and
`tests/test_iackd_channel_role_geometry_authorization_decision.py`. The record
quotes the actual words and binds the packet without widening it. All
decision-only metadata, local-bundle, signal, target, model, score, retry,
rerun, and claim counters remain zero.

Next gate: run focused and complete verification, commit and push the exact
decision, and require both remote CI jobs green. Only at that exact HEAD may
the one registered execution write its private consumed marker and begin the
316 sequential requests. Do not edit the implementation or make a request
before that proof.

## 2026-08-10 IACKD-H2 Consumed Result

Decision `f6eb5ab650a0232a17d2f8f56c582c90bf0cf420` passed Base Python
job `93634720183` and Optional Neuro Readers job `93634720191` in CI
`31444154297` before the one execution.

Read `docs/IACKD_CHANNEL_ROLE_GEOMETRY_RESULT.md`,
`registries/iackd_channel_role_geometry_result.v0.json`, and
`tests/test_iackd_channel_role_geometry_result.py`. All 316 registered bodies
and 457,602 bytes passed response identity, one-hash, one-parse, resource,
privacy, and aggregate replay gates. Runtime was 55.592999708 seconds at
86,769,664-byte peak RSS; retained output is 10,027 bytes.

The consumed route is `IACKDR-R1`. There is one stable 26-channel EEG core,
1024 Hz sampling, average reference, and complete C3/C4/Cz and O1/Oz/O2
geometry in all 30 groups. The frozen contract rejected HEOG and VEOG because
the source types both as `MISC`, then disagreed with sidecars by counting the
`MISC` Trigger separately from their three-MISC total. The source declarations
are mutually consistent; the frozen role taxonomy is not.

Do not rerun H2, amend its parser/router, approve its candidate role-map hash,
or open the existing local bundle. The next safe research step is a new
prospective source-type-first control policy, using only this aggregate result
and frozen before any signal, event, target, model, or outcome access.

## 2026-08-10 IACKD-H3 Source Semantics Research

Read `docs/IACKD_SOURCE_DECLARED_CONTROL_POLICY_RESEARCH.md`,
`registries/iackd_source_declared_control_policy_research.v0.json`, and
`tests/test_iackd_source_declared_control_policy_research.py`. The policy uses
only the committed H2 aggregate after `580f11f` passed CI `31444931063`; all
Git-ignored, network, local-bundle, signal, target, model, and score counters
are zero.

Candidate hash
`1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`
keeps source type, functional role, and model inclusion separate. It reconciles
sidecar counts by exact BIDS 1.7.0 source type first, preserving 26/28 EEG and
three MISC rows, then assigns the fixed 26 EEG core as predictive, M1/M2 as
optional nonpredictive EEG, and HEOG/VEOG/Trigger as nonpredictive controls.

Next gate after this research commit is remotely green: implement one bounded
standard-library generated-fixture qualification under 30 seconds, 256 MiB
RSS, and 2 MiB output. Do not read a public body or local bundle, implement a
real reader, or enter IACKD-2 from this research record.

## 2026-08-10 IACKD-H3 Generated-Fixture Implementation

Research `ed5ce8292c2c1dc842898023cfe8cb608e9d4476` passed Base Python
job `93639606343` and Optional Neuro Readers job `93639606403` in CI
`31445790741` before implementation.

Read `docs/IACKD_SOURCE_SEMANTICS_IMPLEMENTATION.md`,
`registries/iackd_source_semantics_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_source_semantics.py`, and the two H3
implementation test files. The module is standard-library only, has no real
executor, and validates generated 29/31-row signatures with a fixed 26-channel
predictive core, five derivative hashes, deterministic replay, a target
firewall, and 13 mutations covering 12 refusal classes.

Next gate: complete verification, commit and push the exact implementation,
and require both remote CI jobs green. Then run one measured generated-fixture
closeout under 30 seconds, 256 MiB RSS, and 2 MiB output. Do not touch a public
body, the retained bundle, signals, events, targets, models, scores, or
IACKD-2.

## 2026-08-10 IACKD-H3 Measured Result

Implementation `8c5784ad3e664f816899e2f1139600b2c66a8232` passed Base
Python job `93642969190` and Optional Neuro Readers job `93642969143` in CI
`31446902756` before the closeout.

Read `docs/IACKD_SOURCE_SEMANTICS_RESULT.md`,
`registries/iackd_source_semantics_result.v0.json`, and
`tests/test_iackd_source_semantics_result.py`. One preflight refused a symlink
output parent before policy or fixture access. One semantic qualification then
passed all 13 gates: 6,093 generated input bytes, 6,834 output bytes,
0.007473916979506612 seconds, 20,250,624-byte peak RSS, 13 mutations, and 12
distinct refusal classes. Every real/public/local-data, signal, target, model,
network, and score counter stayed zero. The temporary report was removed.

H3 is complete as an engineering mechanics result. It does not validate a real
reader, EEG effect, or decoding result. The next safe work is a separately
named prospective IACKD experiment contract that binds the H3 policy hash; no
payload or signal stage opens without a new Tier C decision.

## 2026-08-10 IACKD-2 Prospective Registration

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_PREREGISTRATION.md`,
`registries/iackd_role_aware_dual_reversal_contract.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_contract.py`.

The contract binds the green research record, consumed IACKD-1 and H2
outcomes, generated-only H3 policy result, and committed OpenNeuro inventory.
It requires both `C2I` and `I2C` arms to favor measured action over the exact
cue-derived opposite. The participant's weaker arm margin is primary. The
fixed matrix has 11 fits and 15 prediction sets per arm and participant-hand
unit: 660 fits and 900 prediction sets total.

The future storage path is new and sequential. It may process only one of 128
ten-object run groups at a time, whose measured maximum is 82,064,564 bytes,
and may retain no second raw bundle. Peak incremental disk is 1 GiB and minimum
free disk is 10 GiB. The existing Git-ignored bundle is explicitly forbidden.

Registration `5bdab30` passed Base Python job `93648969685` and Optional Neuro
Readers job `93648969711` in CI `31448911258` before Tier B implementation.

## 2026-08-10 IACKD-2 Generated-Only Implementation

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_IMPLEMENTATION.md`,
`registries/iackd_role_aware_dual_reversal_implementation.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal.py`.

The implementation has no real execute, network, or old-bundle path. It
validates the immutable inventory, generated 29/31-row source semantics,
causal features, exact split counts, 660 fits, 900 target-blind prediction
sets, a second exact replay, a hash-only freeze, and all six routes. The model
stage and generated scorer stage are separate objects; the scorer recomputes
every prediction hash and final-item binding before generated target access.

One disposable development roundtrip passed in 4.768072 seconds at
257,146,880-byte peak RSS and emitted 30,169 bytes before removal. Every
real/public/private/network counter stayed zero. Its constructed
`IACKD2-R5` is interface mechanics only.

Gate at this implementation record, now superseded by the closeout below:
complete verification, commit and push the exact implementation, require both
CI jobs green, and only then run one registered generated-only closeout. A
future real sequence still needs a separate all-false request, fresh
packet-bound Tier C decision, green real implementation, and green hash-only
prediction freeze.

## 2026-08-10 IACKD-2 Registered Generated Closeout

The first implementation push `25a569216db805db068265744b12e84df9fd7b64`
failed CI `31451058136` only because a new test hardcoded macOS `/private/tmp`.
Ruff and compile passed, and no registered closeout followed that failure.
Portability correction `af7488ab1e8f49854733425a96bbdc9c222ef02b`
then passed Base Python job `93655939217` and Optional Neuro Readers job
`93655939167` in CI `31451262840`.

Only after that green proof, one registered generated closeout passed all 15
gates in 5.024801375111565 seconds at 257,130,496-byte peak RSS with 30,170
output bytes. It completed the 660-fit/900-prediction primary matrix and exact
replay, causal future-tail check, structural target firewall, hash freeze,
aggregate scorer, 19 mutation attempts, and all six routes. Every real/public/
private-data, network, provider, hardware, release, and claim counter stayed
zero. The aggregate report was inspected once and removed.

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_SYNTHETIC_RESULT.md`,
`registries/iackd_role_aware_dual_reversal_synthetic_result.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_synthetic_result.py`. Constructed
`IACKD2-R5` is planted interface behavior with zero scientific value. The
generated closeout is consumed and not rerunnable. No real operation opens
without a separate all-false request, fresh packet-bound Tier C decision, and
the later green implementation and prediction-freeze sequence.

## 2026-08-10 IACKD-2 All-False Real-Execution Request Prepared

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_PACKET.md`,
`registries/iackd_role_aware_dual_reversal_authorization_request.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_authorization_request.py`.

The request binds green registration `5bdab30`, green generated implementation
`af7488a`, and green closeout `7bc45c9` with CI `31452614232`. It asks for one
future ordered sequence: a separately green decision, generated qualification
of a distinct real executor, one fresh 1,340-object/7,249,113,684-byte stream,
one-run-at-a-time private derivatives, exactly 660 fits and 900 target-blind
prediction sets, one remotely green aggregate freeze, and one combined target
delivery and score.

Peak incremental disk is 1 GiB with 10 GiB free required. Only one of 128 raw
run groups may exist at once, the largest is 82,064,564 bytes, and only
invocation-created temporary raw groups may be removed after derivative
promotion. The old retained bundle and every preexisting path are forbidden.

Every action authorization flag and current real-operation counter is false.
Preparing the request made no network, local-data, signal, target, model,
cleanup, release, or claim operation. Next gate: complete verification, commit
and push the packet, and require both CI jobs green. Only after Codex identifies
that exact commit and CI as the sole active Tier C packet may a fresh
maintainer `continue`, `approve`, or `proceed` bind it by reference.

## 2026-08-11 IACKD-2 Packet-Bound Decision

Request `862141f6729182f36accce38ce42a3631feb7232` passed Base Python job
`93664349787` and Optional Neuro Readers job `93664349786` in CI
`31454131606`. Codex identified it as the sole active Tier C packet with the
exact scope and next decision gate. The maintainer then replied `continue`.

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_DECISION.md`,
`registries/iackd_role_aware_dual_reversal_authorization_decision.v0.json`,
and its invariant test. The record quotes the actual word and incorporates the
green packet by reference without fabricating its long recital or expanding
scope. Decision `2ce87fadcbb1ce3fd90d8fab4a48824b19b9fb59` passed Base
Python job `93670726013` and Optional Neuro Readers job `93670725945` in CI
`31456317734` before implementation began.

## 2026-08-11 IACKD-2 Real Executor Generated Qualification

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md`,
`registries/iackd_role_aware_dual_reversal_real_implementation.v0.json`,
`src/neurodecodekit/experiments/iackd_role_aware_dual_reversal_real.py`, and
the two matching test modules.

The new module is dry-run first and does not accept an old-bundle path. Its
future stream reverifies four pinned metadata documents, rejects redirects and
retries, checks every exact object length and ETag-compatible body identity,
parses one 10-object run group at a time, and removes only that invocation-
created temporary group after derivative promotion. It permits full explicit
geometry unavailability for nonpredictive controls but refuses partial
coordinates and requires finite geometry for the fixed 26 predictive channels.

Model, sealed scorer, and target-free physiology shards are separate. The
model loader never enumerates the sealed directory. The fixed matrix performs
exactly 660 fits and 900 target-blind inference sets; prediction serialization
and replay are deterministic. The aggregate freeze binds provenance, split,
item, condition, and private-prediction hashes. Final scoring remains
unreachable until that freeze is tracked at a remotely green commit.

One final generated qualification passed all 15 gates in
5.60445004189387 seconds at 270,745,600-byte peak RSS with 3,257,217 input
bytes, 327,611 peak temporary generated bytes, 192,358 private prediction
bytes, and 4,523 report bytes. It exercised 660 primary fits, 900 primary
prediction sets, a complete exact replay, one generated score, and seven
mutation attempts. Network, public/real payload, old-bundle, real-model,
provider, hardware, release, and claim counters were zero. Its temporary
report SHA-256 was
`a5db8afe33865ef132639c5b019a2c1911214fe0a19d56cc6874d061ce2bb864`.
Constructed `IACKD2-R5` has zero scientific value.

Local verification passed 26 focused tests, 1,929 base tests with 196 skips,
1,985 optional-neuro tests with 34 skips, Ruff 0.15.20, compilation, 142 JSON
registries, CLI help/default/qualify/inspect, and `git diff --check`.

Immediate next gate: commit and push this exact implementation and require both
CI jobs green. Only then run the single fresh public stream. Never touch the
old retained bundle. After the stream, commit its aggregate receipt before the
one target-blind analysis. After analysis, commit and remotely green the
aggregate freeze before delivering and scoring both target views once. There
is no retry or rerun.

## 2026-08-11 IACKD-2 Stream Consumed At Metadata Transport Gate

Exact implementation `dab5dd47ee47f285430311e4fe0f38f457d1118a`
passed Base Python job `93686690177` and Optional Neuro Readers job
`93686690138` in CI `31461818620` before the sole stream invocation.

Read `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_STREAM_RESULT.md`,
`registries/iackd_role_aware_dual_reversal_stream_failure_result.v0.json`, and
its invariant test. The invocation wrote its 267-byte consumed marker at
`2026-08-11T05:51:05.419830Z`, created only empty invocation-owned derivative
and temporary directories, and opened the first registered dataset-description
response. Exact HTTP status and final URL passed. The next guard refused
because `Content-Length` was absent or did not equal the registered 1,178
bytes. The actual header value was not retained.

No body was read or hashed, no metadata JSON was parsed, no second metadata
response or selected object was requested, and no VHDR, VMRK, EEG, events,
channel, geometry, ball, Leap, signal, trajectory, target, derivative, model,
prediction, freeze, delivery, or score was reached. Runtime, peak RSS, and wire
bytes are unavailable. Public metadata response opens equal one; every
protected/model/target/claim counter equals zero.

IACKD-2 is consumed and parked at `IACKD2-F08`. Do not rerun, retry, resume,
delete or rename its private marker, probe the URL, amend the expected length,
or continue into analysis or scoring. The useful architecture lesson is that
metadata content identity should come from a bounded observed body length and
SHA-256, while `Content-Length` should be recorded as transport metadata. Any
recovery needs a separately named prospective contract, implementation proof,
fresh Tier C decision, and new invocation identity.

## 2026-08-11 IACKD-T1 Transport-Stable Registration And Implementation

Read `docs/IACKD_TRANSPORT_STABLE_RECOVERY_RESEARCH.md`,
`registries/iackd_transport_stable_recovery_research.v0.json`,
`docs/IACKD_TRANSPORT_STABLE_RECOVERY_PREREGISTRATION.md`, and
`registries/iackd_transport_stable_recovery_contract.v0.json`.

The new lane permits three standards-valid framing profiles for only the four
small metadata bodies: fixed length, exact chunked transfer, and clean close-
delimited response. `Content-Length` is optional advisory transport evidence.
Acceptance still requires an exact `registered_bytes + 1` bounded read, exact
observed byte count, and registered SHA-256 before one semantic parse. Both
length and transfer coding, malformed or over-cap length, compression,
redirect, underflow, overflow, read failure, or hash drift refuse.

All 1,340 large objects retain exact length, ETag, observed-byte, and one-pass
SHA-256 gates. All participant, split, source-role, causal preprocessing,
control, model, freeze, target, scorer, router, and claim fields remain bound
to the frozen IACKD-2 parent. Focused contract tests pass 16/16. Registration
`ee0f62a` passed Base Python job `93717995481` and Optional Neuro Readers job
`93717995427` in CI `31472269070` before implementation.

Read `docs/IACKD_TRANSPORT_STABLE_RECOVERY_IMPLEMENTATION.md`,
`registries/iackd_transport_stable_recovery_implementation.v0.json`, and
`src/neurodecodekit/datasets/iackd_transport_stable.py`. The standard-library
module contains no URL opener, public executor, local IACKD path, or
`--execute` mode. Forty-one focused tests pass. One final generated closeout
passed 10 accepted validations across two deterministic replays and all 22
refusal mutations. It used 848 generated input bytes, emitted 5,540 bytes, ran
in 0.001049624988809228 seconds, and peaked at 20,332,544 bytes RSS. Every
network, public/real, data, target, model, and score counter is zero.

Two pushed candidates, `6b89b7d` and `8d7be6a`, each passed Base Python but
failed Optional Neuro Readers because a CLI resource test inherited the
dependency-loaded suite's RSS history. Both failures remain preserved and are
ineligible as proof. The final repair separates deterministic resource
monitoring from CLI dispatch. Exact implementation `93a067c` passed Base
Python job `93724709807` and Optional Neuro Readers job `93724709840` in CI
`31474412246`.

Read `docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/iackd_transport_stable_recovery_authorization_request.v0.json`,
and its test. The IACKD-2R request is all false and binds one possible future
additive executor, one new 4-metadata/1,340-object no-retry stream, unchanged
660-fit/900-prediction science, one green aggregate freeze, and one combined
target delivery and score. A new pre-consumption gate requires 10 GiB free,
one numerical thread, and no more than one runnable process per logical CPU.

Next: verify, commit, push, and obtain both green CI jobs for the all-false
request, then stop and identify its exact commit and scope. The current
maintainer `continue` preceded the packet and is not retroactive. No
`ds006840` request, real-executor integration, local IACKD path operation,
old-root access, model run, target delivery, or score is open.

Request `525e97e` then passed Base Python job `93727674791` and Optional Neuro
Readers job `93727674875` in CI `31475356506`. Codex identified IACKD-2R as the
sole active Tier C packet with its exact scope and gate. The maintainer's next
message was exactly `continue`. Read
`docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_DECISION.md`, its registry,
and test. The additive decision binds the green request and preserves the
actual word without fabricating a recital. Next: commit, push, and require both
decision CI jobs green. Generated/mock-only executor implementation remains
closed until then; all public, local-data, model, target, and score operations
remain zero.

## 2026-08-11 IACKD-2R Additive Executor Generated Qualification

Decision `feef8f721c5441f98829099a63a20dd264c98204` passed Base Python job
`93730242015` and Optional Neuro Readers job `93730242090` in CI
`31476158747` before implementation began.

Read `docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md`,
`registries/iackd_transport_stable_dual_reversal_real_implementation.v0.json`,
`src/neurodecodekit/experiments/iackd_transport_stable_dual_reversal_real.py`,
and `tests/test_iackd_transport_stable_dual_reversal_real.py`.

The executor is additive and self-contained. It does not import, call, or
modify `iackd_role_aware_dual_reversal_real.py`, whose SHA-256 remains
`7490896f799a2e576f24d1d612765141dc9bdb881ec1c87ffd2aca02c3c9b173`.
It exposes no old-root or retained-bundle argument and names a new isolated
Git-ignored root. The four metadata bodies use the green transport validator
after an independent real final-URL/status check. Payload objects retain exact
fixed-length, ETag, observed-byte, and full-stream SHA-256 checks.

The production stream wrapper validates exact green implementation evidence,
then measures the five one-thread environment values, free disk, logical CPUs,
and one-minute load. It refuses before calling the streaming builder or writing
a consumed marker unless at least 10,737,418,240 bytes are free and normalized
load is at most `1.0`; unavailable load also refuses.

One measured generated qualification passed all 18 gates in
4.939357291907072 seconds at 261,488,640-byte peak RSS. It processed 3,257,217
generated input bytes, emitted 5,825 report bytes, accepted fixed-exact,
fixed-different, chunked, and close-delimited metadata, completed 4/4/4
metadata read/hash/parse calls, replayed 660 fits and 900 predictions exactly,
and refused 13 mutations. Every public, real, network, old-root, target,
provider, hardware, release, and claim counter remained zero. Its synthetic
`IACKD2-R5` route has no scientific value, and the temporary report was
removed.

Immediate next gate: finish complete base and optional-suite verification,
freeze tracked hashes, commit and push this exact additive implementation, and
require both CI jobs green. Before that proof, do not request public metadata
or payloads, inspect any local IACKD path, create real derivatives, fit a real
model, freeze predictions, deliver targets, or score.

## 2026-08-11 IACKD-2R Stream Consumed At Metadata Content Identity

Exact additive implementation `b32dc25e94efc15bcb4288db9bb5a4c0d4172ed5`
passed Base Python job `93736708777` and Optional Neuro Readers job
`93736708868` in CI `31478167292` before the sole registered invocation.

Read `docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_STREAM_RESULT.md`,
`registries/iackd_transport_stable_dual_reversal_stream_failure_result.v0.json`,
and its invariant test. The pre-consumption machine gate passed. The executor
then wrote the new 268-byte marker at `2026-08-11T09:35:45.049689Z` and opened
the first dataset-description response.

Status, exact final URL, redirect, framing, identity encoding, and exact
1,178-byte observed-length checks passed. One SHA-256 computation then differed
from the pinned digest, so the executor refused at `IACKD2R-F05` with nested
`IACKDT-F07` before semantic parsing. The raw body, observed digest, framing
profile, `Content-Length` state, and changed fields were not retained.

Exactly one metadata response was opened, one body and 1,178 bytes were read,
and one hash was computed. No second metadata response, selected object, VHDR,
VMRK, EEG, channel, geometry, event, signal, ball/Leap trajectory, target,
derivative, fit, inference, prediction, freeze, target delivery, or score was
reached. The new private root contains only the consumed marker.

IACKD-2R is consumed and parked with no retry, rerun, resume, restart,
analysis, freeze, delivery, or score. Do not request or parse the changed body,
compute another hash, alter the marker, or amend the identity under this
contract. Any future metadata-version diagnosis must be a separately named
prospective lane with fresh identity and permission.

## 2026-08-11 IACKD-M1 Snapshot-Scoped Identity Research

Read `docs/IACKD_SNAPSHOT_IDENTITY_RECOVERY_RESEARCH.md`,
`registries/iackd_snapshot_identity_recovery_research.v0.json`, and its
invariant test.

Official OpenNeuro documentation and pinned source commit
`ead8d9394570c64ba4a62b94b85bc3f37a90e809` establish a better prospective
identity surface. A named snapshot exposes `hexsha`; its recursive file tree is
rooted at that revision and returns full relative paths, Git object IDs, sizes,
annexed status, and public S3 URLs with `versionId`.

The future validator must keep four gates separate: snapshot anchor, recursive
tree, selected acquisition inventory, and critical scientific metadata. Raw
GraphQL bytes, HTTP framing, ETag, and last-modified values are provenance and
cannot replace snapshot identity. Compatibility still requires 15
participants, 128 runs, 1,340 selected objects, 7,249,113,684 bytes, and exact
Name/BIDSVersion/License/DatasetDOI values.

This record made zero dataset-specific GraphQL or S3 requests and touched no
local IACKD path. The next Tier B task is to freeze and implement a generated-
only standard-library canonicalizer. A later real audit remains a separate
Tier C gate: exactly one public GraphQL response, 2 MiB input, 1 MiB output,
one thread, no retry, no EEG payload. Never reuse the consumed `continue` as
permission for that future response.

## 2026-08-11 IACKD-M1 Snapshot Identity Registration

Research `723c8e2` is remotely green in CI `31480538821` with Base Python job
`93744221145` and Optional Neuro Readers job `93744221059`.

Read `docs/IACKD_SNAPSHOT_IDENTITY_PREREGISTRATION.md`,
`registries/iackd_snapshot_identity_contract.v0.json`, and its test. The
contract freezes one exact GraphQL POST body and strict semantic schema. A
compatible generated response has exactly 1,679 content-addressed,
snapshot-versioned rows totaling 7,966,799,433 bytes; the selected manifest
has exactly 1,340 rows and 7,249,113,684 bytes with all twelve historical role
summaries.

The generated implementation is eligible only after this exact registration
is committed, pushed, and both CI jobs are green. It must have no URL opener,
socket, HTTP client, endpoint, execute mode, or local IACKD path. It may emit a
bounded generated private manifest and public aggregate only. A real one-
response audit is still Tier C and is not authorized by the current or any
earlier `continue`.

## 2026-08-11 IACKD-M1 Generated Snapshot Canonicalizer

Registration `1667e302e262ad23695f204a88d5a0997ac38270` is remotely green in
CI `31481270697`, with Base Python job `93746523491` and Optional Neuro Readers
job `93746523322`.

Read `docs/IACKD_SNAPSHOT_IDENTITY_IMPLEMENTATION.md`,
`registries/iackd_snapshot_identity_implementation.v0.json`,
`src/neurodecodekit/datasets/iackd_snapshot_identity.py`, and both matching
tests. The module is standard-library only and exposes generated `qualify` and
aggregate `inspect` commands. It has no network opener, real endpoint,
`--execute` mode, provider key, local IACKD path, or consumed-executor import.

The strict canonicalizer separates snapshot anchor, recursive tree, selected
manifest, and critical metadata identities. It accepts only safe NFC paths,
canonical object IDs and sizes, and exact versioned public S3 keys. It keeps
1,340 individual rows in a private bounded manifest while the public report is
aggregate-only. The generated selected path set exactly equals the committed
historical set.

One final generated closeout passed `IACKDM-R1`, all 37 refusals, and two
deterministic replays. It processed 531,067 bytes and emitted 426,792 bytes in
0.8887734590098262 seconds at 38,436,864-byte peak RSS. Forty-nine focused,
2,084 base, and 2,155 optional tests pass, as do Ruff, compileall, all 153
registries, CLI help/roundtrip, and diff checks. Every public, real, neural,
target, model, score, retry, rerun, and claim counter remains zero.
Two untracked generated-only outputs totaling 853,584 bytes remain in OS
temporary storage because cleanup was not approved; they contain no real or
protected data.

Immediate next gate: commit and push this exact implementation and require
both CI jobs green. Only then prepare an all-false Tier C request binding the
one exact GraphQL body and one 2 MiB-capped response. A fresh packet-bound
decision and a separately green real wrapper are still required; the current
or any earlier `continue` authorizes neither that response nor an EEG payload.

## 2026-08-11 IACKD-M1A All-False Public Metadata Request

Exact canonicalizer `7b8f47ba4b192953f4f60126521ba1839b828c85` passed Base
Python job `93753325035` and Optional Neuro Readers job `93753324999` in CI
`31483435801`.

Read `docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_PACKET.md`,
`registries/iackd_snapshot_identity_authorization_request.v0.json`, and its
test. The request binds one possible future standard-library transport wrapper
and, only after that exact wrapper is remotely green, one 355-byte OpenNeuro
GraphQL POST with one response capped at 2 MiB. It requires a 2 GiB free-disk
gate, normalized one-minute load at most `1.0` per logical CPU, one thread,
30 seconds, 256 MiB RSS, and 1 MiB output.

Every current implementation, network, public response, S3 payload, local
IACKD, consumed-root, neural, target, model, score, retry, rerun, release, and
claim authorization is false. The packet authorizes nothing.

Immediate next gate: run complete verification, commit and push the exact
packet, and require both CI jobs green. Only then identify its commit, CI,
one-response scope, and boundary as the sole active Tier C packet and stop for
a fresh maintainer decision. Do not implement the wrapper or access a public
body from this packet or an earlier `continue`.

## 2026-08-11 IACKD-M1A Packet-Bound Decision

Request `ce847383ab1e327523cbc172bb6d3be417b46a11` is remotely green in CI
`31484273623`, with Base Python job `93755977352` and Optional Neuro Readers
job `93755977235`.

After Codex identified IACKD-M1A as the sole active Tier C packet and named its
one-wrapper/one-response scope, the maintainer said exactly `keep going, move
the needle, continue, you approved to go on`. Read
`docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_DECISION.md`,
`registries/iackd_snapshot_identity_authorization_decision.v0.json`, and its
test. The decision quotes all 60 UTF-8 bytes and binds only the immutable green
request and packet by hash.

The decision is ineffective until its own commit is pushed and both CI jobs
pass. Before that proof, wrapper implementation and OpenNeuro access remain
closed. After green decision, only generated/mock wrapper work may begin; the
one public response remains gated on a separately green exact wrapper. EEG
payload, local IACKD, consumed roots, targets, models, scores, retries, reruns,
and claim upgrades remain unauthorized.

Immediate next gate: complete decision verification, commit, push, and require
both CI jobs green. Do not implement or access from the ungreen decision.

## 2026-08-11 IACKD-M1A Generated/Mock Public Wrapper

Decision `4165c24cdad9768c7e36b5e4893602d02434be50` is remotely green in
CI `31485359989`, with Base Python job `93759373384` and Optional Neuro Readers
job `93759373333`.

Read `docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_IMPLEMENTATION.md`,
`registries/iackd_snapshot_identity_public_implementation.v0.json`,
`src/neurodecodekit/datasets/iackd_snapshot_identity_public.py`, and both new
tests. The standard-library wrapper binds the exact request and decision,
requires clean exact green-wrapper evidence for execution, checks computer
load before consumption, rejects redirects/compression/framing drift, reads
one capped response once, and separates private rows from aggregate output.

One generated/mock qualification passed 20 wrapper refusals and two semantic
replays in 0.09886470879428089 seconds at 46,563,328-byte peak RSS. It emitted
429,430 bytes and made zero public GraphQL or S3 requests. All local IACKD,
old-root, neural, target, model, score, retry, rerun, and claim counters remain
zero.

Immediate next gate: finish complete local tests and static checks, commit and
push the exact wrapper, and require both CI jobs green. Do not run `execute`
before that proof. After green wrapper, apply the pre-consumption machine gate
and make at most the one registered metadata request; stop without payload
acquisition or scientific promotion.

## 2026-08-11 IACKD-M1A Public Snapshot Audit Result

Exact wrapper `406bff8bbcfce7b635b0ee4d95096a24288a13e2` passed CI
`31487183289`, including Base Python `93765145883` and Optional Neuro Readers
`93765145952`, before the one registered request.

Read `docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_RESULT.md` and
`registries/iackd_snapshot_identity_public_result.v0.json`. The machine gate
passed. One private marker, one 355-byte POST, one 595,082-byte response read,
and one response hash occurred. Strict semantic processing then refused at
`IACKDMP-F05` because the root field set differed from exact `{data}`.

The raw body was discarded. Do not infer the additional root field. No private
selected manifest, S3 payload, local IACKD, old consumed root, signal, event,
target, model, prediction, or score operation followed. The aggregate result
is 4,352 bytes and the marker is 374 bytes. The failure serializer did not
retain the computed response hash or real framing; they are unavailable.

The CLI raised a reporting-only `TypeError` after the aggregate result was
written. Do not patch or rerun the consumed executor. IACKD-M1A is terminal.
The next eligible work is Tier A design of a separately named metadata-envelope
diagnostic. Any new public response or EEG payload remains a new Tier C gate.

## 2026-08-11 MARC-1 Multimodal Artifact-Resolved Movement Handoff

Read `docs/MARC_1_MULTIMODAL_ARTIFACT_RESOLVED_MOVEMENT_RESEARCH.md`,
`registries/marc1_multimodal_artifact_resolved_movement_research.v0.json`, and
`tests/test_marc1_multimodal_artifact_resolved_movement_research.py`.

MARC-1 is the current prospective scientific lane. It answers the central
WO9R ambiguity with two complementary licensed sources rather than a larger
classifier. Freewill-23 contributes self-selected target/onset timing, 31 EEG,
four EOG, and three synchronized accelerometer channels. Wrist-45 contributes
eight central EEG, eight forearm EMG, and synchronized robotic encoders. The
same compact causal `0.5-4 Hz` shrinkage-LDA family must beat every available
non-EEG comparator on both axes, and the weaker axis margin is primary.

The official Freewill-23 ZIP is 13,591,548,048 bytes and exceeds the user
ceiling. Never download it whole. The next eligible Tier B work is a
standard-library generated-fixture ZIP range inventory plus multimodal role,
causal-window, target-firewall, and comparator-interface qualification with no
live opener. A later exact Tier C packet may propose one bounded central-
directory range inventory only after that implementation is committed, pushed,
and green.

The Aalborg self-paced hand source is scientifically attractive and highly
granular, but its dataset license is unavailable. Keep it parked unless an
explicit license or written permission is preserved. Do not infer reuse rights
from the public Drive link or the article's CC BY license.

Current counters are zero for archive payload requests, member opens, local
real paths, signals, events/onsets, labels/targets, derivatives, fits,
inferences, predictions, freezes, deliveries, scores, and claim upgrades.
The untracked workbook inspection sidecar predates this work and must remain
untouched.

## 2026-08-11 MARC-1 Generated Qualification Contract Handoff

Read `docs/MARC_1_GENERATED_QUALIFICATION_PREREGISTRATION.md`,
`registries/marc1_generated_qualification_contract.v0.json`, and
`tests/test_marc1_generated_qualification_preregistration.py`.

The contract freezes generated-only Tier B work. Its future module may expose
only `plan`, `qualify --output-dir`, and aggregate-report `inspect`; it has no
live URL, archive-path, participant, target, model, provider, or `execute`
surface. The generated archive contains exactly 14 safe members and one forced
ZIP64 member. It must be inventoried by `zipfile.ZipFile` through an
instrumented seekable adapter with zero member-content or payload-interval
reads.

The generated multimodal plan keeps source type, functional control role, and
model inclusion separate for Freewill-like EEG/EOG/acceleration/audio and
Wrist-like EEG/EMG/encoder/trigger profiles. It freezes a past-only
`[-1.5, -0.2)` interface window, physical fit/prediction/scorer separation,
twelve comparator roles, 24 mutations, deterministic replay, 30-second and
256-MiB caps, and one aggregate report plus one generated private manifest.

All authorization flags are false and all access counters are zero. Commit,
push, and require both CI jobs green before implementation. Generated success
will not authorize a HEAD request, byte range, archive member, signal, event,
onset, target, model, score, or scientific claim.

## 2026-08-11 MARC-1 Generated Implementation Handoff

Read `docs/MARC_1_GENERATED_QUALIFICATION_IMPLEMENTATION.md`,
`registries/marc1_generated_qualification_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_generated_qualification.py`, and
`tests/test_marc1_generated_qualification_implementation.py`.

Contract `4494d57bd3853ebb2e198747861c908cdb2a0bb1` passed Base Python
job `93814507482` and Optional Neuro Readers job `93814507355` in CI
`31502115918` before implementation. The new module remains dependency-free
and generated-only. It has no URL opener, network client, real path, member
content reader, participant selector, model, provider, or live execution mode.

The archive fixture is 14 members with one forced ZIP64 local record. A
maximum-length deterministic comment keeps `zipfile` EOCD reads in metadata;
the writer records compressed-payload intervals independently, and the reader
fails if any returned range intersects one. The implementation validates exact
members, paths, types, flags, methods, sizes, ratios, range caps, private/public
separation, two deterministic replays, and all 24 mutations.

The multimodal plan separately validates source type, functional role, model
inclusion, geometry, clocks, synchronization, the causal `[-1.5, -0.2)`
interface window, fit-only normalization, physical target roles, strict split
binding, and twelve comparator states. No model exists. Thirty-nine focused
contract/implementation tests pass in 0.446 seconds; the complete suite passes
2,261 tests with 35 expected skips in 56.908 seconds.

Immediate next gate: commit and push this exact implementation and obtain both
green CI jobs. Only then run one measured generated `qualify` roundtrip and
record its aggregate closeout. Do not make a public request or treat generated
`MARC1G-R1` as neural evidence.

First push `ff34a9e` passed Base Python job `93821044692` but failed Optional
Neuro Readers job `93821044782` in CI `31504059513`: only the three CLI child
processes returned `MARC1G-F06`; no report was written. The pending correction
runs those dependency-free child probes with Python `-S`. It changes no source
logic or cap. Require both jobs green on the correction before closeout.

Correction `fdc55ec` still failed those three children because the Linux
optional parent had already reached a 401,321,984-byte RSS high-water mark.
The final pending harness uses an injected RSS probe for deterministic
roundtrip/privacy tests, keeps a real subprocess qualification when its parent
is below cap, skips only exact inherited-high-water `MARC1G-F06`, and directly
tests over-cap refusal. Do not weaken the production 256-MiB guard.

## 2026-08-11 MARC-1 Generated Result Handoff

Read `docs/MARC_1_GENERATED_QUALIFICATION_RESULT.md`,
`registries/marc1_generated_qualification_result.v0.json`, and
`tests/test_marc1_generated_qualification_result.py`.

Exact implementation `e35a58743766ba404ae16f63804481a5f51531c9`
passed Base Python job `93826102571` and Optional Neuro Readers job
`93826102044` in CI `31505555044` before the one closeout. The fresh generated
run passed `MARC1G-R1` in 0.006588957970961928 seconds at 23,511,040-byte peak
RSS. It used 81,139 generated input bytes, emitted 7,813 bytes, and made 14
range calls returning 202,529 metadata bytes. Zero reads overlapped compressed
member payloads.

All 14 members, the forced ZIP64 record, two deterministic replays, both
modality profiles, 18 channel records, the causal window, 4/4/4 target roles,
twelve comparators, all 24 mutations, and all 14 acceptance gates passed. No
network, real path, human signal, event, target, derivative, model, prediction,
score, or claim operation occurred. The temporary report and generated private
manifest were removed after their hashes were recorded.

Twelve result invariants pass; the combined focused MARC-1 suite passes 51
tests, and the complete repository suite passes 2,273 tests with 35 expected
skips in 56.275 seconds.

The result is consumed with no retry or rerun. Next safe work is Tier A design
of a separately named metadata-only central-directory range audit for the
13.59 GB Freewill archive. Do not issue a HEAD or range request from this
result; live metadata remains a new exact Tier C decision.

## 2026-08-11 MARC-1 Freewill Central-Directory Research Handoff

Read `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESEARCH.md`,
`registries/marc1_freewill_central_directory_research.v0.json`, and
`tests/test_marc1_freewill_central_directory_research.py`.

`MARC1-CD1` is the next archive-mechanics lane. It is bound to Figshare record
`28632599` version 1 and exact file `57518986`, size `13,591,548,048`, MD5
`3b7c3039c5c9fb6abf1429a830301711`. It never permits a whole-archive fallback.

The future conditional audit has at most three response bodies totaling at
most 17,039,360 bytes: one 128-KiB versioned metadata response, one exact
128-KiB final archive range, and one central-directory range capped at 16 MiB.
The tail must contain a reconciled classic EOCD, ZIP64 locator, and complete
ZIP64 EOCD. If not, park without an exploratory request. HTTP `206`, exact
`Content-Range`, exact length, identity encoding, single-disk ZIP64 bounds,
safe unique paths, supported file kinds/methods, and strict output privacy are
mandatory.

This Tier A record made no public request. The next eligible work is a frozen
generated/mock-only preregistration, followed after green proof by a standard-
library implementation with no live endpoint or `execute` mode. Do not prepare
or bind a Tier C decision until that exact implementation is remotely green.
Even a future `MARC1CD-R1` would inventory metadata only; whole-archive MD5,
member CRC verification, local headers, payload content, and every neural
claim would remain unavailable.

The unrelated untracked workbook inspection sidecar remains untouched at
SHA-256 `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.

## 2026-08-11 MARC1-CD1 Generated Contract Handoff

Read `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_PREREGISTRATION.md`,
`registries/marc1_freewill_central_directory_contract.v0.json`, and
`tests/test_marc1_freewill_central_directory_preregistration.py`.

Research `93faf36` passed Base Python job `93834276391` and Optional Neuro
Readers job `93834276150` in CI `31507965329` before the contract was frozen.
The future module exposes only `plan`, generated/mock `qualify`, and aggregate
`inspect`; it must contain no real URL opener or execute mode.

The generated fixture represents the exact 13,591,548,048-byte archive with
only metadata ranges. It has an exact 128-KiB tail, complete ZIP64 records, an
EOCD decoy inside a comment, and an 18-entry central directory with four safe
directories, fourteen regular files, UTF-8 and CP437 paths, methods 0/8, and
one ZIP64 extended member. It contains zero local-header and payload bytes.

Implementation must use injected mock transport plus standard-library
`struct`, pass direct and two-bodyless-redirect paths, refuse all 32 mutations,
and keep exact member inventory private. Commit and push this contract and
require both CI jobs green before implementation. Public metadata, archive
ranges, member acquisition, neural data, targets, models, and scores remain
closed Tier C work.

## 2026-08-11 MARC1-CD1 Generated Implementation Handoff

Read `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_IMPLEMENTATION.md`,
`registries/marc1_freewill_central_directory_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_central_directory_audit.py`, and
`tests/test_marc1_freewill_central_directory_implementation.py`.

Contract `cf6304385f61fc7713ae7fd4526d86e45e4c03e5` passed Base Python
job `93837415016` and Optional Neuro Readers job `93837415174` in CI
`31508903399` before implementation. The module is standard-library and
generated-only. Its CLI has only `plan`, `qualify --output-dir`, and aggregate
`inspect`; there is no live opener, DNS query, real archive path, member-open
surface, or execute mode.

The fixture represents 13,591,548,048 virtual bytes with 280,249 materialized
bytes: one 128-KiB tail and one 148,910-byte central directory. It includes an
EOCD comment decoy, complete in-tail ZIP64 records, eighteen entries, methods
0/8, one UTF-8 path, and one ZIP64 member. No local header or payload byte
exists. The parser uses `struct`, enforces exact range and redirect semantics,
strict path/file-kind/flag/extra-field validation, private exact inventory,
aggregate-only output, deterministic replay, atomic no-overwrite output, and
all 32 frozen refusals.

The latest development-only qualification passed constructed `MARC1CDG-R1`
in 0.00740712508559227 seconds at 26,181,632-byte peak RSS, emitted 11,573
bytes, and removed its two exact temporary files and directory. It is not the
registered closeout. Forty-two implementation tests pass; the complete suite
passes 2,343 tests with 35 expected skips under one-thread limits.

Immediate next gate: commit and push the exact implementation and require both
CI jobs green. Then run one registered generated closeout exactly once, bind
its aggregate measurements, remove its exact temporary outputs, and push that
result. Only after the closeout is remotely green may an all-false Tier C
packet be prepared. Do not issue a live request, download the monolith, read a
member or signal, run a model, score, or call this scientific evidence.

The unrelated untracked workbook inspection sidecar remains untouched at
SHA-256 `b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6`.

## 2026-08-11 MARC1-CD1 Generated Result Handoff

Read `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESULT.md`,
`registries/marc1_freewill_central_directory_result.v0.json`, and
`tests/test_marc1_freewill_central_directory_result.py`.

Exact implementation `211fd78fba82a660c4730a586541819b2eb264fd`
passed Base Python job `93846584402` and Optional Neuro Readers job
`93846584527` in CI `31511626051` before the one registered closeout. A fresh
Python `-S` process with one thread, one worker, and one numerical job passed
`MARC1CDG-R1` in 0.006544457981362939 seconds at 27,131,904-byte reported peak
RSS.

The run represented the exact 13,591,548,048-byte identity with 280,249
generated bytes, parsed the 128-KiB tail and 148,910-byte directory, inventoried
18 generated entries, validated the direct and two-bodyless-redirect paths,
and passed all 32 mutations and all 14 gates. It wrote 5,898 aggregate bytes
and 5,676 generated-private bytes. Their exact hashes are bound in the result
registry; the aggregate was inspected once, and both files plus the empty
invocation directory were removed.

All public request, network, real archive, local-header, payload, signal,
event, target, model, prediction, score, and claim counters remained zero.
`MARC1CDG-R1` is consumed with no retry or rerun and is engineering evidence
only. It does not establish the real archive inventory, verify whole-archive
MD5 or member integrity, or add neural evidence.

Twelve result invariants pass; all 82 focused MARC1-CD1 tests pass; and the
complete repository suite passes 2,355 tests with 35 expected skips in 54.687
seconds.

Immediate next gate: prepare one all-false Tier C authorization packet for the
frozen no-retry metadata/tail/directory sequence. Commit, push, and require
both jobs green before identifying it as the sole active packet. Only a fresh
packet-bound maintainer decision after that identification could authorize a
live response. Do not use an earlier `continue`, issue a request, download the
monolith, select participants, read signals, or run a model from this result.

## 2026-08-11 MARC1-CD1A Live-Audit Request Handoff

Read `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_PACKET.md`,
`registries/marc1_freewill_central_directory_authorization_request.v0.json`,
and
`tests/test_marc1_freewill_central_directory_authorization_request.py`.

Generated result `431ee8dc14118e4de5f5a3a9ae6e34a202cc238e`
passed Base Python job `93849853477` and Optional Neuro Readers job
`93849853538` in CI `31512598915` before the all-false request was prepared.
The request binds the complete research, contract, implementation, result,
packet, and test hashes. Eleven request invariants pass.

The possible future sequence is deliberately staged: a fresh decision must
be remotely green before generated/mock live-wrapper implementation; the exact
wrapper must then be committed, pushed, and remotely green before one public
invocation. That invocation may accept exactly one bounded version-metadata
body, one exact 131,072-byte tail, and one conditional central-directory body
no larger than 16 MiB. Accepted body bytes are capped at 17,039,360, request
attempts at five, and bodyless tail redirects at two. There is no HEAD, retry,
rerun, exploratory range, whole download, or member access.

Every current authorization flag and operation counter is false. Preparing
the packet made no network, public-body, local-path, member, signal, event,
target, model, score, cleanup, release, or claim operation. The packet itself
authorizes nothing.

Eleven request invariants pass; all 93 focused MARC1-CD1 tests pass; and the
complete repository suite passes 2,366 tests with 35 expected skips in 54.936
seconds.

Request `950796d123272a459eedf1e431ba99f22a0c582e` passed Base Python job
`93853089748` and Optional Neuro Readers job `93853089786` in CI
`31513578445`. Codex then identified MARC1-CD1A as the sole active Tier C
packet and named its exact scope and remaining decision boundary.

The maintainer's next message was exactly `keep going, move the needle,
continue, you approved to go on`. Read
`docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_DECISION.md`,
`registries/marc1_freewill_central_directory_authorization_decision.v0.json`,
and
`tests/test_marc1_freewill_central_directory_authorization_decision.py`. The
separate decision preserves those 60 UTF-8 bytes and binds the unchanged
green request, packet, contract, generated implementation, generated result,
and parser hashes. It does not fabricate the packet recital as user words or
expand the scope.

Immediate next gate: test, commit, push, and obtain both green CI jobs for the
exact decision. Before that green proof, do not implement the live wrapper,
issue a public request, create a consumed marker, download the monolith, or
access a member. After green decision proof, only generated/mock wrapper work
is eligible; the one public sequence remains closed until that exact wrapper
is separately committed, pushed, and remotely green.

Local decision verification is complete: 12 decision invariants, 23 combined
request/decision invariants, and all 168 MARC1 tests pass. The comparable
optional-neuro suite passes 2,378 tests with 35 expected skips, exactly 12
tests above the 2,366-test request baseline. The dependency-light suite also
passes 2,307 tests with 204 expected skips. Ruff, compilation, JSON parsing,
and diff checks are clean. These local results do not activate the decision;
both remote jobs are still mandatory.

## 2026-08-11 MARC1-CD1A Live-Wrapper Implementation Handoff

Decision `624cc4e99a4aa600b68a333c1bcd84e6cebb9dcd` passed Base Python
job `93871192638` and Optional Neuro Readers job `93871192713` in CI
`31519016891` before implementation. Read
`docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_IMPLEMENTATION.md`,
`registries/marc1_freewill_central_directory_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_central_directory_live.py`,
`tests/test_marc1_freewill_central_directory_live.py`, and
`tests/test_marc1_freewill_central_directory_live_implementation.py`.

The additive module imports but does not modify the green generated parser. It
binds the exact request and decision hashes, requires exact clean-HEAD wrapper
evidence, gates on five one-thread variables, 12 GiB free disk, normalized
load, and RSS, then supports only the fixed three-body sequence. Automatic
redirects are disabled. Tail redirects must be bodyless, HTTPS, loop-free,
and globally routable under injected DNS. The directory may not redirect.
Critical duplicate headers, transfer encoding, range drift, cap overflow, and
URL drift refuse closed.

One final fresh `python -S` qualification passed constructed `MARC1CDL-G1` in
0.006050459109246731 seconds at 40,763,392-byte reported peak RSS. It parsed
280,249 generated bytes, inventoried 18 entries, passed 32 inherited parser
refusals, 8 wrapper refusals, and all 14 gates, and emitted 5,995 aggregate
plus 6,187 private bytes. The output hashes are bound in the implementation
registry, and the exact temporary files were removed. Network-client calls and
all public, member, neural, model, score, and claim counters were zero.

Thirty wrapper/registry tests and all 198 MARC1 tests pass locally. The
dependency-light suite passes 2,337 tests with 204 expected skips in
16.718 seconds. The comparable optional-neuro suite passes 2,408 tests with 35
expected skips in 54.949 seconds, exactly 30 tests above the green decision
baseline. Ruff, compile, JSON, CLI help, and diff checks pass.

## 2026-08-11 MARC1-CD1A Live Archive Inventory Handoff

Exact wrapper `5dfa3c4c8cd7f0e990b7b1db7b35c4df8694171f` passed Base Python
job `93879378282` and Optional Neuro Readers job `93879378362` in CI
`31521510374` before the one registered invocation. Read
`docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_RESULT.md`,
`registries/marc1_freewill_central_directory_live_result.v0.json`, and
`tests/test_marc1_freewill_central_directory_live_result.py`.

The invocation passed `MARC1CD-R1` in 2.7274372498504817 seconds at
43,974,656-byte reported peak RSS. It made four HTTP attempts with one
bodyless HTTPS redirect and accepted exactly three bodies: 304 metadata bytes,
the exact 131,072-byte tail, and the exact 175,382-byte central directory.
From those 306,758 bytes it inventoried 1,227 entries in the current
13,591,548,048-byte public ZIP. Whole-archive downloads, local-header requests,
member requests, and member payload bytes were all zero.

The exact 418,755-byte member inventory and 450-byte consumed marker remain
private under `.codex_work/marc1_central_directory/live_audit_v0/`, both mode
`0600`. Do not inspect member rows, publish either private file, alter the
marker, or rerun the lane. The committed 6,118-byte result exposes only
aggregate counts, hashes, warnings, and unavailable fields. Its SHA-256 is
`fee969818b4e3e2ef7aee86096ad676c9bd70f80d19f2fd6dbe0e8069175257b`.

All 11 result invariants and all 209 MARC1 tests pass. The dependency-light
suite passes 2,348 tests with 204 expected skips; the optional-neuro suite
passes 2,419 tests with 35 expected skips. Both add exactly 11 tests over the
green wrapper baseline.

MARC-1 Task 3 is complete as metadata-only archive inventory. The next
scientifically useful step is a separately frozen Task 4 design that selects a
small, representative Freewill pilot without exposing private member rows or
moving the monolith. That design must become a new Tier C packet before any
private-inventory inspection, member access, local-header read, payload
acquisition, participant selection, signal processing, model run, or score.
The current lane is consumed and cannot supply that authority.

Engineering capability added: NeuroDecodeKit can safely inventory the current
13.59 GB public Freewill ZIP from 306,758 bounded metadata bytes without
downloading the archive or opening a member.

Scientific claim not established: archive metadata contain no neural signal,
event, target, model prediction, or score, so this result establishes no
neural effect or decoding capability.

## 2026-08-12 MARC1-P1 Pilot Selection Contract Handoff

Read `docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_PREREGISTRATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_contract.v0.json`, and
`tests/test_marc1_privacy_preserving_pilot_selection_preregistration.py`.

The contract is anchored to green `MARC1CD-R1` commit `7aee128` and freezes a
12-person cohort on each axis using DOI-bound SHA-256 ranks. Freewill uses the
first three complete session-1 bundles as fit and session-2 bundles as held
out: 72 bundles and 288 opaque members. Wrist uses runs 1-6 as fit and 7-8 as
held out across 12 participant archives. Joint future network and disk are
capped at 8 GiB with no substitution or budget fallback.

Selection is forbidden from using size or CRC except for refusal after the
cohort and runs are fixed. It cannot read an event, target, bad-trial flag,
movement onset, signal, quality value, or outcome. Exact member/archive fields
stay private; preregistered subject IDs and aggregate hashes/counts may be
public.

Seventeen contract invariants pass. The complete dependency-light suite passes
2,365 tests with 204 expected skips in 18.273 seconds and 248,332,288-byte
external maximum RSS. The optional-neuro suite passes 2,436 tests with 35
expected skips in 54.977 seconds and 696,320,000-byte external maximum RSS.
Ruff, compilation, 170 registry parses, and diff checks pass.

Immediate next gate: commit and push the exact contract and require both CI
jobs green. Only then implement `marc1_pilot_selection` with generated fixtures
and `plan`, `qualify`, and aggregate `inspect` commands. Do not read the sealed
Freewill inventory or request Wrist metadata. A later all-false Tier C packet
and fresh decision are mandatory before either real metadata operation.

This lane targets a first confound-resistant EEG effect. Thought-to-text is a
separate language-specific goal and must not be inferred from movement data.

## 2026-08-12 MARC1-P1 Generated Implementation Handoff

Contract `d1218066e64dea502d263acf0c096ed7eab55a11` passed Base Python job
`94028013357` and Optional Neuro Readers job `94028013230` in CI
`31569417204` before implementation. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_IMPLEMENTATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_pilot_selection.py`, and the two matching
tests.

The standard-library module has only `plan`, generated `qualify`, and
aggregate `inspect`. It builds 1,227 generated Freewill rows and 55 generated
Wrist rows, replays both frozen 12-person cohorts and exact splits under row
reversal, emits 300 exact private rows mode `0600`, and refuses all 36 frozen
mutations. It has no real path, network, archive, event, signal, target,
quality, model, score, retry, rerun, or fallback interface.

Disposable development `MARC1PSG-R1` processed 873,348 generated bytes in
0.2268019998446107 seconds at 32,833,536-byte reported peak RSS. The aggregate
report/private manifest were 6,945/175,618 bytes. They were inspected,
hash-bound in the implementation record, and removed. All real, neural,
target, model, score, and claim counters stayed zero.

All 37 implementation/record tests, 263 MARC tests, 2,402 dependency-light
tests with 204 expected skips, and 2,473 optional-neuro tests with 35 expected
skips pass. Ruff, compilation, 171 registry parses, CLI checks, and diff
hygiene pass.

Immediate next gate: commit, push, and obtain both green jobs for this exact
implementation. Only then run one registered generated closeout and record it
as consumed. Do not inspect the sealed Freewill inventory or request Wrist
metadata. A later real selection still requires one all-false Tier C packet,
its remote-green proof, and a fresh packet-bound maintainer decision.

This remains a supporting rung on the thought-to-text path, not a pivot. No
movement result may be promoted into a language-decoding claim.

## 2026-08-12 MARC1-P1 Generated Result Handoff

Exact implementation `0c0a6982c6b9c65d6c51413d1baa8b577e00a194`
passed Base Python job `94034790262` and Optional Neuro Readers job
`94034790315` in CI `31571668853` before the one registered closeout. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_RESULT.md`,
`registries/marc1_privacy_preserving_pilot_selection_result.v0.json`, and
`tests/test_marc1_pilot_selection_result.py`.

The sole generated run passed `MARC1PSG-R1` over 873,348 input bytes in
0.22733404207974672 seconds at 32,374,784-byte reported peak RSS. It replayed
the exact two 12-person ranks, 72 Freewill bundles/288 opaque members, 12
Wrist archives, 300 private rows, fixed held-out splits, all 36 refusals, and
all 15 acceptance gates. Every real, neural, model, score, and claim counter
stayed zero.

The 6,946-byte aggregate report and mode-`0600` 175,618-byte private manifest
were hash-bound, inspected once, and removed with their invocation directory.
The registered generated closeout is consumed with no retry or rerun.

Eleven result invariants and all 274 MARC tests pass. The dependency-light
suite passes 2,413 tests with 204 expected skips; the locally comparable
optional-neuro suite passes 2,484 tests with 35 expected skips. Both add
exactly 11 tests and zero skips over the green implementation baseline.

Immediate next gate: prepare one all-false Tier C request binding a future
single read of the exact 418,755-byte sealed Freewill inventory and one Wrist
metadata body capped at 2 MiB. Test, commit, push, and green that request, then
identify it as the sole active Tier C packet and stop. Do not open the sealed
inventory, request Wrist metadata, access a payload, or infer authorization
from any current or earlier continuation. A fresh packet-bound maintainer
message is required for a separate decision.

This is the same thought-to-text research path. MARC-1 resolves attribution
and positive-control risk before a later language-specific held-out experiment;
movement evidence itself is not language evidence.

## 2026-08-12 MARC1-P1A Real Metadata Request Handoff

Generated-result commit `fd246294db3defecdc11460e41945f64794b21cf`
passed Base Python job `94038664052` and Optional Neuro Readers job
`94038664104` in CI `31572950727`. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_PACKET.md`,
`registries/marc1_privacy_preserving_pilot_selection_authorization_request.v0.json`,
and `tests/test_marc1_pilot_selection_authorization_request.py`.

The request is all false. It binds one future generated/mock-only real-selector
implementation and, only after that exact implementation is remotely green,
one selection from a single 418,755-byte sealed Freewill-manifest content open
plus one Wrist metadata body capped at 2 MiB. It authorizes no operation now,
permits no payload bytes, and does not expose the retained inventory.

All 12 request tests and 38 subtests, 286 MARC tests, 2,425 dependency-light
tests with 204 expected skips, and 2,496 optional-neuro tests with 35 expected
skips pass. Both complete suites add exactly 12 tests and zero skips over the
green result baseline. Exact source identities, participant ranks, splits,
no-follow/private modes, transport, parser freeze, privacy, machine caps,
no-rerun behavior, and zero counters are machine-checkable.

Immediate next gate: commit and push this exact request, require Base Python
and Optional Neuro Readers green, identify it as the sole active Tier C packet,
and stop. Only a fresh unambiguous maintainer message after that identification
may be recorded in a separate decision. Current and earlier continuations are
not retroactive. Do not implement the wrapper, open the sealed manifest,
request Wrist metadata, or acquire a payload from this request alone.

MARC1-P1A remains a control and attribution step on the same thought-to-text
path, not a pivot. It produces no movement or language evidence.

## 2026-08-12 MARC1-P1A Authorization Decision Handoff

Request `7f1ba0936e4e0266c0210648aa641feab63cd0eb` passed Base Python
job `94041819046` and Optional Neuro Readers job `94041819022` in CI
`31573969646` before the maintainer supplied the fresh words `approved,
continue, achieve a scientific claim, achieve thought to text 😎`. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_DECISION.md`,
its machine registry, and the matching decision test.

The decision quotes the actual 76-byte message and binds only request
`8eebf5f34294bc266e81552d31ff376cb81240d2ee18b2fc6857600fbd3aba85`.
It preserves the final scientific objective without treating it as an observed
result. Twelve decision tests plus 48 subtests pass; all decision-only real,
payload, neural, target, model, score, and claim counters remain zero.

All 298 MARC tests, 2,437 dependency-light tests with 204 expected skips, and
2,508 optional-neuro tests with 35 expected skips pass. Each complete suite
adds exactly 12 tests and zero skips over the green request baseline.

Immediate next gate: test, commit, push, and green this exact decision. Only
then implement the generated/mock real selector. Do not touch the retained
Freewill manifest or Wrist endpoint until that exact implementation is also
remotely green. After both green milestones, the one registered metadata
selection may run with no retry and no payload access.

## 2026-08-12 MARC1-P1A Live Selector Implementation Handoff

Decision `9726d07ab08e9c2815dbe68398659f454693be5e` passed Base Python
job `94044627592` and Optional Neuro Readers job `94044627647` in CI
`31574870204` before implementation. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_IMPLEMENTATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_pilot_selection_live.py`, and the two
matching live-selector test modules.

The additive standard-library wrapper freezes the exact private input and one
public Figshare v3 endpoint. It requires one no-follow/open/read/hash/parse of
the 418,755-byte mode-`0600` Freewill manifest, exactly 55 seven-field Wrist
rows totaling 3,683,416,050 bytes, `sub-01.zip` through `sub-45.zip`, and the
known public `sub-01` identity anchor. It refuses target-like fields, automatic
or private-address redirects, malformed framing, alternate sources, fallback,
retry, and rerun. Its private marker precedes every real input.

Final generated `MARC1PSL-G1` passed all 15 gates and 26 refusals over 866,578
input bytes in 0.1832679167855531 seconds at 50,905,088-byte reported peak
RSS. It selected the exact 12+12 cohorts and 300 private rows, reserved
1,223,853,749 future payload bytes, emitted 214,553 temporary bytes, and made
zero real or network operations. The outputs were removed. Thirty-one focused,
329 MARC, 2,468 dependency-light, and 2,539 optional-neuro tests pass with no
new skips.

## 2026-08-12 MARC1-P1A Consumed Result Handoff

Exact selector `702e61377d41fd1d95939d5e4047be59e4631d4d` passed Base
Python job `94056321843` and Optional Neuro Readers job `94056321914` in CI
`31578614616` before the one registered invocation. Read
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_RESULT.md`,
`registries/marc1_privacy_preserving_pilot_selection_live_result.v0.json`, and
the matching result test.

The executor passed its machine gate, wrote the private consumed marker, and
read/hashed/parsed the exact 418,755-byte Freewill inventory once. It opened
one Wrist response and failed closed at `MARC1PS-F03` before reading its body
because the frozen explicit identity-encoding condition was not met. The
public result is 4,706 bytes with SHA-256
`3c526ac52f8185f3fe29b8f3843fd808cd9646b5011e9638d6bf55f5a459153a`.

No participant, bundle, archive, or private selection row was selected. No
public body, archive payload, signal, event, target, model, prediction, score,
or claim operation occurred. MARC1-P1A is consumed with no retry, rerun,
resume, or amendment. Do not inspect the retained private material.

Immediate next gate: specify and remotely green a separately named generated/
mocked transport-semantics recovery. Another real metadata request or private-
inventory read requires a new Tier C decision; payload acquisition is not yet
eligible. This is still the same thought-to-text research path, not a pivot.

## 2026-08-12 MARC1-HT1 Research Handoff

Read `docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_RESEARCH.md`,
`registries/marc1_http_identity_semantics_recovery_research.v0.json`, and the
matching research test. The primary-source review uses RFC 9110 Sections 8.4
and 12.5.3 to separate absent response content coding from the request-side
identity token.

Candidate policy
`ac1b98eed57af7e545b925f1529ebf38de72b4277ea54a473ae1d6f7fe0cd3a6`
accepts an absent `Content-Encoding` or one case-insensitive identity token and
refuses every other present value. It preserves all existing redirect, body,
schema, privacy, output, machine, consumed-marker, and payload firewalls. The
actual live header was not retained and must not be inferred.

Immediate next gate: commit, push, and green this artifact-only research.
Afterward, freeze a separate generated-only contract. Do not implement a real
executor, access either metadata source, touch the consumed private root, or
acquire a payload from this research record.

## 2026-08-12 MARC1-HT1 Contract Handoff

Research `f515b36cfdd2b297bcbba9885af92e59ead066a7` passed Base Python
job `94062432262` and Optional Neuro Readers job `94062432241` in CI
`31580575669` before the generated recovery contract was frozen. Read
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_http_identity_semantics_recovery_contract.v0.json`, and its
matching contract test.

The contract permits only a future additive standard-library
`plan`/`qualify`/`inspect` module. It binds four accepted uncoded forms, 20
refusals, five routes, 16 gates, 1,227 + 55 generated rows, exact 12+12 cohort
replay, no network/private bytes, and no decompressor or real executor.

Immediate next gate: commit, push, and green this exact contract. Only then
implement and measure the generated/mock harness. Real metadata, the old
private root, payloads, signals, targets, models, scores, and Tier C execution
remain closed.

## 2026-08-12 MARC1-HT1 Generated Implementation Handoff

Contract `1f99d0a8c5609dae992fa0e245f179c2f417038f` passed Base Python
job `94065047494` and Optional Neuro Readers job `94065047277` in CI
`31581395690` before implementation. Read
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_IMPLEMENTATION.md`,
`registries/marc1_http_identity_semantics_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_http_identity_semantics.py`, and the two
matching tests.

The standard-library module exposes only `plan`, `qualify`, and `inspect`. It
accepts absent `Content-Encoding` as uncoded and one case-insensitive identity
token as a narrow compatibility form. Every actual coding, list, duplicate,
empty field, transfer coding, malformed envelope, target-like field, output
breach, or second invocation refuses. It contains no network client, private
path, consumed executor, decoder, neural interface, model, scorer, or retry.

Development `MARC1HT-G1` passed four accepted forms, 20 refusals, 16 gates,
exact 12+12 target-free cohort and split replay, and deterministic output
replay. It processed 923,052 generated input bytes in 0.10857224999926984
seconds at 32,440,320-byte reported peak RSS and emitted 182,682 temporary
bytes. The output was inspected once and removed. All 389 MARC, 2,528 base,
and 2,599 optional-neuro tests pass with no new skips.

Immediate next gate: commit, push, and green this exact implementation. Only
then run the one registered generated closeout, remove its outputs, and record
and green the aggregate result. Do not open any real/private source or prepare
a live executor from this implementation milestone. A later live attempt is a
new Tier C sequence. This is the same thought-to-text path, not a pivot.

## 2026-08-12 MARC1-HT1 Consumed Generated Result Handoff

Exact implementation `b2cb48cc1c630cf2d22186732e8258619db0a930` passed
Base Python job `94073234688` and Optional Neuro Readers job `94073234607` in
CI `31583931303` before the one registered closeout. Read
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RESULT.md`,
`registries/marc1_http_identity_semantics_result.v0.json`, and its matching
result test.

The closeout passed `MARC1HT-G1` with four accepted response forms, all 20
refusals, all 16 gates, exact 12+12 target-free cohort and split replay, and
zero live or network operations. It used 923,052 generated input bytes in
0.1119600001256913 seconds at 33,079,296-byte reported peak RSS. The 7,063-byte
aggregate report and 175,618-byte private manifest were inspected/hash-bound
and removed. The closeout is consumed with no retry or rerun.

All 400 MARC, 2,539 dependency-light, and 2,610 optional-neuro tests pass with
no new skips. Immediate next gate: commit, push, and green this result. Only
then prepare one all-false Tier C request for a new live wrapper and one new
metadata attempt. Do not implement that wrapper, touch the old root, request a
source, or acquire a payload from this result. This is the same thought-to-text
path and remains engineering evidence only.

## 2026-08-12 MARC1-HT1A Live Recovery Request Handoff

Generated result `5344d73bb74431e9bba05e3608c2a1523a84cd00` passed Base
Python job `94075586323` and Optional Neuro Readers job `94075586171` in CI
`31584662864` before this all-false request was prepared. Read
`docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc1_http_identity_live_recovery_authorization_request.v0.json`,
and its matching request test.

The request proposes one additive standard-library wrapper, generated/mock
qualification, an independently green implementation, and then one fresh
metadata-only attempt. The future attempt is bounded to one exact no-follow
read of the 418,755-byte upstream Freewill inventory and one Wrist response
capped at 2 MiB in a new isolated root. It forbids importing or reusing the
consumed `MARC1-P1A` executor, opening its old root, acquiring a payload,
reading signal or targets, or running a model or score. All current permissions
are false and every current operation counter is zero.

Twelve focused request tests, all 412 MARC tests, 2,551 dependency-light tests,
and 2,622 optional-neuro tests pass with no new skips. Immediate next gate:
commit, push, and require both CI jobs green. Then identify MARC1-HT1A as the
sole active Tier C packet and wait for a fresh packet-bound maintainer message.
Do not use the current or an earlier `continue` retroactively. This is the same
path toward a controlled neural positive control and held-out language
decoding, not a pivot, and it establishes no scientific result.

## 2026-08-12 MARC1-HT1A Authorization Decision Handoff

Request `27f39aee5f056eafc81b615cec4a178a41a6c5d2` passed Base Python
job `94080678529` and Optional Neuro Readers job `94080678738` in CI
`31586256906`. After Codex identified it as the sole active Tier C packet, the
maintainer supplied the fresh words `approved, continue, achieve a scientific
claim, achieve thought to text 😎`.

Read `docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc1_http_identity_live_recovery_authorization_decision.v0.json`,
and its matching test. The record quotes the actual 76-byte message and binds
the unchanged packet. It interprets the scientific language as the enduring
objective, not a predeclared result or permission to widen scope.

Immediate next gate: test, commit, push, and obtain both green CI jobs for the
decision. Only then implement and qualify the new additive wrapper on generated
and mocked inputs. Do not touch the sealed inventory, public endpoint, consumed
executor, old root, or payload before the exact wrapper is also remotely green.

## 2026-08-12 MARC1-HT1A Additive Wrapper Handoff

Decision `9c7bd48541fbcebabcb9a783cb9047c7f2a2f57a` passed Base Python
job `94083644849` and Optional Neuro Readers job `94083644932` in CI
`31587195405` before implementation. Read
`docs/MARC_1_HTTP_IDENTITY_LIVE_IMPLEMENTATION.md`,
`registries/marc1_http_identity_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_http_identity_live.py`, and both matching
test modules.

The new wrapper is additive and standard-library-only. It composes the green
HTTP-identity semantics and frozen target-free selector, uses AST inspection
to forbid the consumed executor import, and lexically refuses the old consumed
root without statting or opening it. It accepts absent response encoding or
one case-insensitive identity token, refuses every actual coding, duplicate,
list, empty value, and transfer coding, and exposes no decoder, decompressor,
payload, signal, target, model, scorer, retry, or alternate-source interface.

Measured generated `MARC1HTL-G1` passed 21/21 gates and 31/31 refusals across
four accepted transport forms. It processed 892,922 generated input bytes in
0.2482517089229077 seconds at 52,117,504-byte reported peak RSS and produced
an 8,951-byte aggregate plus a 206,509-byte private manifest. The outputs were
removed, and every real/network/forbidden counter remained zero.

Immediate next gate: finish full local verification, commit and push the exact
wrapper, and require both CI jobs green. Only afterward may the one registered
metadata attempt read the sealed upstream inventory once and accept one Wrist
body capped at 2 MiB. Do not open payloads or the old root. This is the same
thought-to-text path, not a pivot, and no scientific result has changed.

## 2026-08-12 MARC1-HT1A Consumed Result Handoff

Exact wrapper `68ade0d4f6a58c19dbaae954a608080bdc6f128a` passed Base Python
job `94089099869` and Optional Neuro Readers job `94089099850` in CI
`31588920988` before the one registered invocation. Read
`docs/MARC_1_HTTP_IDENTITY_LIVE_RESULT.md`,
`registries/marc1_http_identity_live_result.v0.json`, and the matching result
test.

The corrected HTTP predicate accepted one 2,917-byte Wrist body with absent
`Content-Encoding`, matching `Content-Length`, no redirects, and zero decoding
or decompression. This resolves the prior explicit-identity transport blocker.
The strict parser then routed `MARC1HTL-F04` because the live file-list row
count differed from the frozen 55-row contract. The actual row count and rows
were not retained or published.

The invocation read the exact 418,755-byte sealed Freewill inventory once,
selected zero participants, opened zero payload bytes, and performed zero
signal, target, derivative, model, prediction, score, retry, rerun, or claim
operations. Internal runtime was 0.5396664168220013 seconds at 38,223,872-byte
reported peak RSS. The 5,006-byte public result has SHA-256
`50a1bd4e97e6149db91d528aa0fce79e6aa5d3cedf79acdb12f03bf4a2d041f2`.

Immediate next gate: verify, commit, push, and green this aggregate result.
Afterward, design only a separately named metadata-snapshot identity recovery
from aggregate evidence. Do not inspect the retained private root or request
another public body under this consumed lane. The work remains on the same
thought-to-text path and has not established a scientific result.

## 2026-08-12 MARC1-PG1 Pagination Recovery Research Handoff

Consumed-result commit `1337a91ca2dd1f988ddcfc36631b7a1a8d832b0f`
passed Base Python job `94091696454` and Optional Neuro Readers job
`94091696340` in CI `31589739739` before this Tier A research. Read
`docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_RESEARCH.md`,
`registries/marc1_versioned_pagination_recovery_research.v0.json`, and its
matching test.

Pinned official Figshare OpenAPI commit
`751101d87c8fcea45556492bc627499ff49b0f2b` defines the version-files
operation with `page_size` default 10 and maximum 1,000. The consumed wrapper
omitted pagination, so an API-default partial page is the leading engineering
hypothesis for the 55-row refusal. It is not proven: the actual live count and
rows were not retained and must not be inferred as 10. Inventory drift and
deployed-provider divergence remain explicit alternatives.

The smallest prospective repair binds exactly
`GET /v2/articles/29666735/versions/3/files?page=1&page_size=1000` and
retains the complete 55-row semantic identity. It forbids a second page,
fallback, version substitution, partial cohort, and post-result expectation
change. Research access was limited to the committed aggregate result,
committed wrapper source, and 196,169 bytes of pinned official OpenAPI source;
dataset-specific, private, payload, neural, target, model, and score counters
are zero.

Immediate next gate: test, commit, push, and green this exact research record.
Only then freeze a generated-only pagination contract and qualify a harness
with no URL opener or execute mode. A new live body remains a later separate
Tier C decision. This is the same thought-to-text path, not a pivot, and no
scientific result has changed.

## 2026-08-12 MARC1-PG1 Generated Contract Handoff

Research `7a7883abda094eb9f202215b8b138a17cdff022e` passed Base Python
job `94095736694` and Optional Neuro Readers job `94095736770` in CI
`31591022429` before this contract. Read
`docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_versioned_pagination_recovery_contract.v0.json`, and its
matching test.

The contract freezes exact request serialization for
`page=1&page_size=1000`, four equivalent generated row-order/encoding cases,
41 mutations, eight refusal routes, 18 acceptance gates, and the unchanged
55-row semantic identity. It composes only the frozen generated selector and
HTTP-semantics source after hash verification. The future module is limited to
`plan`, `qualify`, and `inspect`; it cannot expose a network opener, URL or
local-source argument, `execute`, private-root name, automatic pagination,
fallback, payload, signal, target, model, or score interface.

Eleven focused contract tests, all 489 MARC tests, 2,628 dependency-light
tests with 204 expected skips, and 2,699 optional-neuro tests with 35 expected
skips pass. Ruff, compile, 186 registry JSON parses, CLI help, hash replay,
policy replay, and diff checks pass.

Immediate next gate: commit, push, and obtain both green CI jobs for this exact
contract. Only then implement the generated-only harness. A new dataset body
remains a later Tier C action; generated `MARC1PG-G1` would establish no neural
or language result. This remains the same thought-to-text path.

## 2026-08-12 MARC1-PG1 Generated Implementation Handoff

Exact contract `ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb` passed Base
Python job `94098410925` and Optional Neuro Readers job `94098410868` in CI
`31591853349` before implementation. Read
`docs/MARC_1_VERSIONED_PAGINATION_IMPLEMENTATION.md`,
`registries/marc1_versioned_pagination_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_versioned_pagination.py`, and both matching
test modules.

Generated `MARC1PG-G1` passes 4/4 accepted cases, all 41 refusals across eight
routes, and all 18 gates. It preserves the exact 55-row semantic inventory and
12+12 target-free selection across response order and safe JSON encoding
variation. One measured development run processed 1,019,776 generated input
bytes in 0.08925708406604826 seconds at 40,091,648-byte reported peak RSS,
emitted 183,355 temporary bytes, and removed both outputs. All real, network,
private-source, payload, signal, target, model, score, claim, and other-project
counters stayed zero.

Immediate next gate: finish repository verification, commit and push this exact
implementation, and require both CI jobs green. Only then run the one
registered generated closeout. A new live metadata response remains a later
all-false Tier C packet and fresh decision; payload acquisition remains closed.
This is the same thought-to-text path, not a pivot.

## 2026-08-12 MARC1-PG1 Consumed Closeout Handoff

Exact implementation `2c98a2ad4b3972de5c2a398b85c0cf8735db89d4`
passed Base Python job `94104455930` and Optional Neuro Readers job
`94104455857` in CI `31593790492` before the one registered generated
invocation. Read `docs/MARC_1_VERSIONED_PAGINATION_GENERATED_RESULT.md`,
`registries/marc1_versioned_pagination_failure_result.v0.json`, and its
matching result test.

The command requested
`/tmp/neurodecodekit-marc1pg-registered-closeout-20260812`; `/tmp` is a symlink
to `private/tmp` on this host. The strict writer refused `MARC1PG-F07` with
`output parent is a symlink`. Contract loading, both generated inventories,
four accepted cases and selections, selection-hash equality, and generated
private-manifest construction had already run in memory. The registered run is
therefore consumed with no retry or corrected-path invocation.

No output path or file was created. External wall time was 0.17 seconds and
external peak RSS was 30,064,640 bytes. Generated output, incremental disk,
network, real/private input, payload, signal, target, model, score, and claim
bytes or operations were zero.

Immediate next gate: verify, commit, push, and green this aggregate failure
result. Then specify a separately named generated recovery whose path preflight
precedes contract and fixture work. Do not rerun MARC1-PG1, use `/private/tmp`
as a substitution, prepare a live packet, or access any payload. This remains
the same thought-to-text path, not a pivot, and no scientific result changed.

## 2026-08-12 MARC1-OP1 Output-Capability Research Handoff

Consumed result `a4dcaea784f4c3a62547fd4f73bb3e2a5528100a` passed Base
Python job `94107907276` and Optional Neuro Readers job `94107907246` in CI
`31594881048` before this research. Read
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESEARCH.md`,
`registries/marc1_output_capability_recovery_research.v0.json`, and its test.

The root cause is operation order: MARC1-PG1 checked output safety only after
generated inventories, four selections, and private-manifest construction. The
candidate recovery obtains a held no-follow parent-directory capability first,
binds device/inode identity, refuses every symlink ancestor, then uses
parent-relative exclusive creation and cleanup. Missing primitives fail closed.

One local standard-library introspection occurred; fixture, qualify,
registered-path, network, private, payload, signal, target, model, and score
operations were zero. Immediate next gate: verify, commit, push, and green this
research. Only then freeze a generated-only MARC1-OP1 contract. Do not rerun
MARC1-PG1 or prepare a live packet. This remains the same thought-to-text path.

## 2026-08-12 MARC1-OP1 Generated Contract Handoff

Research `d02830b95c76bc428a297c6415db933452af5cbb` passed Base Python
job `94111539407` and Optional Neuro Readers job `94111539431` in CI
`31595996923` before this contract. Read
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_output_capability_recovery_contract.v0.json`, and its test.

The frozen design has six accepted cases, 32 refusals, ten routes, and 20
gates. It allows one future path-only probe at the exact `/private/tmp` output
path, then one qualifier only after `MARC1OP-P0`. Capability acquisition is
first; all writes are parent-relative and exclusive; the consumed qualifier
and source modification are forbidden.

Immediate next gate: verify, commit, push, and green this exact contract. Only
then implement the generated/mock wrapper. Do not stat the registered path,
run a probe, import the consumed module eagerly, contact a dataset endpoint, or
access any payload. The scientific objective and claim boundary are unchanged.

## 2026-08-12 MARC1-OP1 Generated Implementation Handoff

Contract `baade51146309bd3b3fa6c1750a36482669a0ff2` passed Base Python
job `94115807028` and Optional Neuro Readers job `94115807008` in CI
`31597291352` before implementation. Read
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_IMPLEMENTATION.md`,
`registries/marc1_output_capability_recovery_implementation.v0.json`, and its
two implementation test modules.

The additive dependency-free wrapper acquires the output capability first,
holds and revalidates parent device/inode/type, defer-imports only hash-bound
pure pagination helpers, writes two files exclusively through held directory
descriptors, inspects only the public file, and cleans up exactly. Development
`MARC1OP-G1` passed six accepted cases, 32 refusals, and 20 gates in 0.095795
seconds at 33,767,424-byte reported RSS with 184,173 temporary bytes and zero
real/private or neural/model operations. Thirty-six new tests pass.

Immediate next gate: commit, push, and obtain both green CI jobs for this exact
implementation. Only then operate once on the exact registered `/private/tmp`
path: one path-only preflight, followed only after `MARC1OP-P0` by one generated
qualifier. Any refusal parks without retry. Do not contact Figshare, open a
private root or payload, or infer a scientific result. This is the same path.

## 2026-08-12 MARC1-OP1 Registered Result Handoff

Exact implementation `fcedcc308c1038c765605571c19ba24eb4f7603f`
passed Base Python job `94125013790` and Optional Neuro Readers job
`94125013956` in CI `31600085119` before the registered sequence. Read
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESULT.md`,
`registries/marc1_output_capability_recovery_result.v0.json`, and its test.

The sole path-only preflight reached `MARC1OP-P0` in 0.10 external seconds at
25,280,512-byte peak RSS with every experiment-work counter zero. The sole
conditional qualifier then reached `MARC1OP-G1` in 0.097943 reported seconds
at 33,882,112-byte reported RSS. All six accepted cases, 32 refusals, and 20
gates passed; 184,173 temporary bytes were written, publicly inspected once,
and removed exactly. Network, live/private, neural, target, model, score, and
claim operations were zero.

Both registered invocations are consumed with no retry or rerun. Immediate
next gate: verify, commit, push, and green this aggregate result. Only then
prepare one all-false Tier C request for a bounded live metadata response. The
request itself cannot contact Figshare, and a live call still needs a fresh
packet-bound maintainer decision. This remains the same scientific path.

## 2026-08-12 MARC1-LM1 Paginated Live-Metadata Request Handoff

Capability result `ca4679a` is remotely green in CI `31601329375` with Base
Python job `94129199903` and Optional Neuro Readers job `94129199993`.

Read `docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_PACKET.md`,
`registries/marc1_paginated_live_metadata_authorization_request.v0.json`, and
`tests/test_marc1_paginated_live_metadata_authorization_request.py`. The new
request is all false. It proposes one future additive generated/mock wrapper
and, only after that implementation is committed, pushed, and both jobs are
green, one exact no-retry Figshare request for
`page=1&page_size=1000`. The sole body is capped at 2 MiB; payload bytes are
zero; outputs are capped at 4 MiB incremental disk.

Thirteen focused, 612 MARC, 2,751 base, and 2,822 optional tests pass locally.
Packet preparation made no private, network, payload, neural, target, model,
score, deletion, or claim operation.

Next: commit and push this exact request and wait for both CI jobs. Then
identify its commit, CI, one-response scope, and no-payload boundary as the
sole Tier C gate. Only a fresh unambiguous maintainer message after that
identification may be recorded in a separate authorization decision. Do not
use any earlier `continue` retroactively and do not implement or contact
Figshare from the request alone.

This is a cohort-integrity step on the same path to a cue-resistant neural
positive control and held-out language decoding, not a pivot.

## 2026-08-12 MARC1-LM1 Packet-Bound Decision Handoff

Green request `4d3eb19` passed CI `31603530015` with Base Python job
`94136577454` and Optional Neuro Readers job `94136577639`. The maintainer then
sent the exact 76-byte instruction `approved, continue, achieve a scientific
claim, achieve thought to text 😎`.

Read `docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_DECISION.md`,
`registries/marc1_paginated_live_metadata_authorization_decision.v0.json`, and
its test. The decision binds only the green packet's one-response, 2 MiB,
zero-payload scope. It is ineffective until its own commit is pushed and both
CI jobs are green.

Thirteen decision, 26 combined, 625 MARC, 2,764 base, and 2,835 optional tests
pass locally. Every real/private/network/neural/target/model/score/claim
counter is zero.

Next: commit, push, and green the decision. Then implement only the additive
generated/mock wrapper. Commit, push, and green that exact wrapper before one
registered path or Figshare operation. Do not infer payload access or a
scientific outcome from the user's aspirational wording.

## 2026-08-12 MARC1-LM1 Generated Implementation Handoff

Decision `060a365a24e75da4297a5c4a3422ff730467ec36` passed Base Python
job `94140250333` and Optional Neuro Readers job `94140250412` in CI
`31604608307` before implementation. Read
`docs/MARC_1_PAGINATED_LIVE_METADATA_IMPLEMENTATION.md`,
`registries/marc1_paginated_live_metadata_implementation.v0.json`, and its two
test modules.

The additive dependency-free wrapper now holds output authority first,
validates the exact one-response transport and 55-row target-free inventory,
replays the frozen 12-subject split, separates private rows from aggregate
output, and emits an aggregate failure receipt after a consumed marker. Final
generated `MARC1LM-G1` passed four transport cases, 36 refusals, and 20 gates
over 184,466 generated response bytes. It created and removed 19,030 temporary
bytes in 0.030280 seconds at 43,057,152-byte reported RSS. Every real, payload,
neural, target, model, score, retry, and claim counter remained zero.

First push `8f67af2` failed both jobs in CI `31608450681` because generated
tests used macOS `/private/tmp`, absent on Linux. The corrected generated/test
parent is canonical and portable; the registered real path remains unchanged
and untouched.

Twenty-one behavior, 12 implementation-record, 658 MARC, and 2,797 corrected
base tests pass. The corrected isolated optional environment passes 2,853
tests/34 skips. Two canonical optional attempts exposed only older
late-process mechanical rehearsal sensitivity; each affected test passes in a
fresh process, and no unrelated gate changed.

Immediate next gate: commit, push, and obtain both green CI jobs for this exact
implementation. Only then run the one registered metadata invocation. Any
post-marker failure consumes and parks; success stops before every participant
ZIP and adds no scientific result.

## 2026-08-12 MARC1-LM1 Consumed Live-Metadata Result Handoff

Corrected implementation `f9a1eceb8ee432e57e19c6af2db355aadd53b1e3`
passed Base Python job `94164152160` and Optional Neuro Readers job
`94164152302` in CI `31611639130` before the one registered request.

The request accepted and parsed one 15,652-byte Figshare metadata body, then
the frozen inventory validator refused at `MARC1LM-F04`. Runtime was
1.0945040830411017 seconds at 33,996,800-byte peak RSS; combined output was
4,207 bytes. Only the aggregate report was inspected once. The private
manifest was not opened after execution. No cohort, participant archive,
payload, signal, target, model, prediction, score, or claim was reached.

The exact failed inventory predicate is unavailable. Do not infer row-count,
filename, ID, URL, checksum, byte-total, or schema drift from the response size
or broad route. `MARC1-LM1` is consumed with no retry or rerun.

Immediate next safe task: specify a separately named prospective current-
inventory identity lane using only the aggregate result. Another public body
or any participant payload requires a new Tier C decision. The research path
is unchanged: trustworthy multimodal cohort, cue-resistant neural evidence,
held-out language decoding, then progressively stronger thought-to-text
evidence.

## 2026-08-12 MARC1-SA1 Source-Aware Attestation Research Handoff

Consumed result `d859509` passed Base Python job `94168528552` and Optional
Neuro Readers job `94168528522` in CI `31612923903` before this Tier A work.
Read `docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_RESEARCH.md` and its
registry and test.

The source pass found that official Figshare surfaces document a five-field
public file core but show MD5 fields on some public full-metadata examples.
The current frozen helper instead requires exact seven-field set equality.
This is a proven contract coupling, not proof that MD5 shape caused the
consumed `MARC1LM-F04` result.

`MARC1-SA1` separates public source identity, target-free cohort identity, and
later acquired-byte integrity. It proposes 21 independently evaluated
aggregate predicates and seven domain-separated hashes. Names, IDs, URLs,
checksums, rows, and participant-level outcomes remain private.

Immediate next gate: commit, push, and green this exact research. Then freeze
a generated-only, standard-library preregistration. No URL opener, execute
mode, new metadata response, private path, archive, payload, model, or score is
authorized by this research.

Twelve focused, 680 MARC, 2,819 dependency-light, and 2,875 isolated optional-
neuro tests pass. The complete suites retain one-thread operation and add 12
tests without changing skip counts.

## 2026-08-12 MARC1-SA1 Generated-Only Contract Handoff

Research `aa805038cc28c64ad75ddcb0e14768fdcb3cd96e` passed Base
Python job `94173234952` and Optional Neuro Readers job `94173234944` in CI
`31614330447` before registration. Read
`docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_PREREGISTRATION.md`,
`registries/marc1_source_aware_inventory_attestation_contract.v0.json`, and
its contract test.

The frozen contract requires six generated semantic families, 21 aggregate
predicates, seven domain-separated hashes, 52 refusals, 25 gates, deterministic
row/key reorder replay, strict private/public separation, and exact cleanup.
Allowed commands are exactly `plan`, `qualify`, and `inspect` under one thread,
30 seconds, 256 MiB peak RSS, 2 MiB input/output caps, and zero network bytes.

Thirteen focused and all 693 MARC tests pass. The complete locally installed
suite passes 2,868 tests/35 skips; a clean narrow optional-neuro stack passes
2,856/47. A broader merged environment triggered only historical
process-global RSS self-checks after collection; the first five affected tests
pass together in a fresh 64,520,192-byte process. Treat fresh remote Base
Python and Optional Neuro Readers jobs as the cross-platform eligibility gate.

Immediate next gate: commit, push, and obtain both green CI jobs for this exact
contract. Then implement only the additive standard-library generated harness.
Do not add a URL opener or execute mode, touch a registered/consumed path,
request a dataset body, or access payload, signal, target, model, prediction,
or score. A future live response remains a new Tier C sequence. This is the
same path to cue-resistant neural evidence and held-out language decoding, not
a pivot.

## 2026-08-12 MARC1-SA1 Generated Implementation Handoff

Contract `8f64ccb6dd33df8c81382a9dafd2e84590f50061` passed Base Python
job `94180673330` and Optional Neuro Readers job `94180673125` in CI
`31616551270` before implementation. Read
`docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_IMPLEMENTATION.md`, its
registry, source module, and two implementation test modules.

The dependency-free module exposes only `plan`, `qualify`, and `inspect`. It
implements strict source-core and optional-MD5 semantics, target rejection,
21 predicates, seven identity layers, six family routes, 52 refusals,
capability-held private/public output, deterministic replay, and exact cleanup.

Final development `MARC1SA-G1` passed all 25 gates using 732,811 generated
input and 109,589 temporary output bytes in 0.052419791 seconds at
27,426,816-byte peak RSS. All forbidden counters stayed zero. Twenty-nine
focused tests and 33 subtests pass. The complete dependency-light suite passes
2,897 tests with 35 skips and 1,614 subtests; the isolated optional-neuro suite
passes 2,885 tests with 47 skips and 1,621 subtests. Their measured maximum RSS
was 659,668,992 and 448,299,008 bytes respectively. A late in-process CLI test
initially inherited the complete suite's high-water RSS and correctly refused
the producer cap; the test now uses an injected bounded probe, while a separate
fresh-process qualification passes the real monitor at 27,394,048-byte peak
RSS. No production limit was weakened.

Immediate next gate: run complete verification, commit, push, and obtain both
green CI jobs for this exact implementation. Only then run one registered
generated closeout. Do not contact Figshare, inspect the consumed root, or
access any archive, payload, signal, target, model, prediction, or score. A
future live response remains a new Tier C packet and decision. The research
path is unchanged.

## 2026-08-12 MARC1-SA1 Registered Generated Result Handoff

Implementation `feb3b839e879d2a9edcdcfe664c68b3c4ba236d6` passed Base
Python job `94188922905` and Optional Neuro Readers job `94188922771` in CI
`31619037335` before the sole generated closeout. Read
`docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_RESULT.md`, its result
registry, and result test.

The one fresh-process `MARC1SA-G1` run passed six family routes, 21 predicates,
seven hashes, 52 refusals, and 25 gates. It consumed 732,811 generated input
bytes and 109,589 temporary output bytes in 0.053358083 seconds at 27,885,568-
byte reported peak RSS. Both mode-`0600` outputs and the invocation directory
were removed. The closeout is consumed with no retry or rerun. Every live,
private, payload, neural, target, model, score, and claim counter is zero.

Eleven result tests, 53 focused tests plus 36 subtests, and all 733 MARC tests
plus 801 subtests pass. The complete dependency-light suite passes 2,908 tests
with 35 skips; the isolated optional-neuro suite passes 2,896 with 47 skips.

Immediate next gate: test, commit, push, and green this aggregate result. Only
after that proof may Tier A work prepare one all-false Tier C packet for a new
source-aware live wrapper and one bounded public metadata response. Do not
contact Figshare, touch the consumed root, or access an archive or EEG payload
from this result. The path remains cohort integrity, cue-resistant neural
positive control, held-out language decoding, then stronger thought-to-text
evidence.

## 2026-08-12 MARC1-SA1A All-False Request Handoff

Generated result `094b6cb7358c5d44b6d8c2ce7a087e16ec4e17c3` passed Base
Python job `94193898391` and Optional Neuro Readers job `94193898482` in CI
`31620515340` before packet preparation. Read
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_PACKET.md`, its request
registry, and request test.

The packet binds one future additive standard-library wrapper, one exact
version-3 Figshare GET, one response capped at 2 MiB, one private canonical
manifest, one aggregate report, and zero archive or payload bytes. Exact green
source-aware routes R1/R2 may expose only the frozen target-free cohort; R3/R4
block selection. The old wrapper and root remain forbidden. One thread,
30 seconds, 256 MiB RSS, 4 MiB disk, and a 10-GiB free-space precondition are
frozen.

Every current permission and real-operation counter is false or zero. The
current and earlier maintainer messages are not retroactive authorization.
Fourteen request tests, all 747 MARC tests, 2,922 dependency-light tests with
35 skips, and 2,910 optional-neuro tests with 47 skips pass locally.
Immediate next gate: test, commit, push, and green this request. Only then
identify its commit, CI, exact scope, and claim boundary as the sole active
Tier C packet and wait for fresh packet-bound words.

## 2026-08-13 MARC1-SA1A Packet-Bound Decision Handoff

Request `b0775501e8d7dc5b28b81692dbc7fb02d423be95` passed Base Python
job `94198174069` and Optional Neuro Readers job `94198173901` in CI
`31621794066`. Read
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_DECISION.md`, its
decision registry, and decision test.

The decision quotes the maintainer's exact 31-byte instruction and binds only
the immutable `MARC1-SA1A` packet. Thirteen decision tests, 27 combined
request/decision tests, 760 MARC tests plus 856 subtests, 2,874 dependency-light
CI-style tests with 204 skips, and 2,945 optional-neuro CI-style tests with 35
skips pass. Every decision-time real-operation counter remains zero.

Immediate next gate: commit, push, and require both remote CI jobs green for
this exact decision. Only then implement the additive wrapper using generated
inventories and mocked transport. Do not contact Figshare until that exact
wrapper also becomes remotely green. Do not acquire an archive, access a
payload, run a neural model, deliver a target, score, replicate, or begin
language work under this decision.

## 2026-08-13 MARC1-SA1A Source-Aware Wrapper Handoff

Decision `ef9ab91b38ad48ef5e832b993d4ca338d889bc04` passed Base Python
job `94353799568` and Optional Neuro Readers job `94353799602` in CI
`31670457497` before implementation. Read
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_IMPLEMENTATION.md`, its registry,
source module, and two implementation test modules.

The additive dependency-light wrapper exposes `plan`, `qualify`, `inspect`,
and a strict `execute` command. Live execution requires externally supplied
green proof for a clean exact HEAD. It can make only one fixed 2-MiB-capped
metadata request, route the green attestor's R1-R4 result, write one private
manifest plus aggregate receipt, and stop before participant archives.

Generated `MARC1SAL-G1` passed all six semantic families, three framing forms,
31 refusals, and 20 gates over 84,422 generated response bytes. It created and
removed 24,064 transient bytes in 0.009288083 seconds at 37,552,128-byte
reported peak RSS. All real, payload, neural, target, model, score, retry,
rerun, and claim counters stayed zero.

Thirty focused, 765 MARC, and 2,904 dependency-light tests pass. One old
tiny-encoder rehearsal failed only its process-global RSS reading late in the
2,975-test local optional process and passes alone. Do not alter that gate;
fresh remote Base Python and Optional Neuro Readers jobs decide eligibility.

Immediate next gate: commit and push this exact implementation, then require
both jobs green. Only afterward run the sole registered metadata check once,
without retry. Do not inspect the private manifest after execution. Read only
the aggregate result, stop before payload, and route R1/R2 to a new all-false
selective-acquisition packet or R3/R4/failure to a blocked diagnosis.

## 2026-08-13 MARC1-SA1A Consumed Result Handoff

Exact wrapper `74aff21bde6495436066c1538e229eb7be5059cc` passed Base
Python job `94360721568` and Optional Neuro Readers job `94360722170` in CI
`31672761644` before the sole request. Read
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_RESULT.md`, its registry, and result
test.

The one request completed source-aware attestation and returned
`MARC1SAL-R2`, so the frozen Wrist cohort is unavailable. Runtime was
0.6966645420015993 seconds at 33,439,744-byte peak RSS with 23,112 retained
Git-ignored bytes. Selected subjects, archive requests, payload bytes, signal
reads, targets, fits, predictions, and scores were zero.

The executor already performed the one aggregate inspection. Do not open the
aggregate report or private manifest now. The CLI did not expose whether the
source route was R3 or R4, nor body bytes or historical differences; preserve
those as unavailable. Do not probe the retained root, retry, amend the parser,
or use the output as acquisition authority.

Ten result, 775 MARC, and 2,914 dependency-light tests pass locally. Immediate
next gate: commit, push, and green this closeout. Afterward, Task 4 remains a
research objective but this Wrist branch is closed. Compare independent cue-
resistant cohorts and synchronized EOG/EMG designs without requesting data;
any new real operation requires a separately green Tier C packet.

## 2026-08-13 MARC-2 Confound Triangulation Handoff

The consumed `MARC1SAL-R2` Wrist result is now replaced prospectively, not
reopened, by the five-work-order design in
`docs/MARC_2_CONFOUND_TRIANGULATION_RESEARCH.md` and
`registries/marc2_confound_triangulation_research.v0.json`. The retained Wrist
outputs and the retained private Freewill inventory were not touched.

`CIL-v0` makes participant-macro held-out conditional log-loss gain the
primary endpoint: EEG receives credit only if `P+E` improves over the strongest
available cue, timing, EOG, EMG, and kinematic model `P`, while also surviving
deranged-EEG and causal controls. The compact low-frequency, mu/beta covariance,
and `CML-v0` families remain separate hypotheses with no final-target winner
selection.

The exact order is `MARC2-FW1` target-free Freewill selection, `MARC2-FW2`
bounded range acquisition and semantic qualification, `MARC2-CIL1` one
target-firewalled Freewill experiment, `MARC2-ORTH1` one independently selected
peripheral-control cohort, and `NDK-LANG1` one Spanish inner-speech control
ladder. No LLM may receive neural evidence before a remotely green neural
prediction freeze, and it must beat both LLM-only and item-deranged-neural
conditions.

Immediate next gate: test, commit, push, and green this Tier A research record.
After that, freeze a generated/mock-only `MARC2-FW1` selector contract. Do not
open the retained private inventory, request an archive member, download a
payload, access signal or targets, run a model, score, or call a provider
without the later exact gate.

## 2026-08-13 MARC2-FW1 Contract Handoff

MARC-2 research `ae4d43aabbbe058658c1d77057431f7de331c958` passed Base
Python job `94368928633` and Optional Neuro Readers job `94368928658` in CI
`31675452031` before this generated-only contract was frozen. Read
`docs/MARC_2_FREEWILL_PREFIX_SELECTION_PREREGISTRATION.md`, its registry, and
contract test.

The contract preserves the earlier DOI-bound rank, holds the original 12
participants as a hard floor, and permits expansion only as the maximal
contiguous prefix under an exact 8-GiB reservation. It stops at the first
nonfitting participant; no size-based reorder, skip, substitution, later-
session backfill, quality filter, event read, or outcome use is allowed. The
main generated case must select 16 participants, 96 bundles, and 384 members.

Immediate next gate: commit, push, and require both CI jobs green for this
exact contract. Only then implement `plan`, generated `qualify`, and aggregate
`inspect` with no `execute` surface. Do not open the retained 418,755-byte
private inventory, touch an old consumed root, make a network request, open an
archive/local header/member, access neural or target data, run a model, or
score under this contract.

## 2026-08-13 MARC2-FW1 Implementation Handoff

Contract `a12edebdab8b1252be546600d37fdb04503394d6` passed Base Python
job `94371385720` and Optional Neuro Readers job `94371385628` in CI
`31676261134` before the standalone generated-only selector was implemented.
Read `docs/MARC_2_FREEWILL_PREFIX_SELECTION_IMPLEMENTATION.md`, its registry,
module, and two implementation test modules.

The main fixture selects 16 frozen-rank participants, 96 bundles, and 384
members at 8,105,207,776 reserved bytes. All four byte profiles and all 40
refusals pass. A measured qualification ran in 0.21431241699974635 seconds at
30,883,840-byte reported peak RSS and emitted 221,068 temporary bytes. Thirty
functional and 14 registry tests pass. Every private/real operation counter is
zero.

Immediate next gate: commit, push, and require both jobs green for this exact
implementation. Only then execute one registered generated closeout, delete
only its invocation-created temporary outputs, and record the aggregate result.
Do not open the retained private inventory or enter real selection, MARC2-FW2,
payload, neural, target, model, scoring, or language work.

## 2026-08-13 MARC2-FW1 Generated Result Handoff

Exact implementation `36f87759967f03dd7ac5d543f6f5a24afb571365`
passed Base Python job `94375991713` and Optional Neuro Readers job
`94375991770` in CI `31677757466` before one registered closeout. Read
`docs/MARC_2_FREEWILL_PREFIX_SELECTION_SYNTHETIC_RESULT.md`, its registry, and
result test.

The closeout passed `MARC2FWG-R1`: 16 participants, 96 bundles, 384 members,
8,105,207,776 reserved bytes, 4/4 storage boundaries, and 40/40 refusals. It
ran in 0.21099908299947856 seconds at 32,047,104-byte reported peak RSS. The
221,068-byte generated output was hashed, its aggregate side was inspected,
and the invocation-owned temporary root was removed. Every real/private access
counter is zero. The closeout is consumed with no rerun.

Immediate next gate: commit, push, and green this aggregate result. Only then
prepare one all-false Tier C packet for one exact read of the retained private
inventory. Do not perform that read, select real members, request an archive
byte, enter MARC2-FW2, or access neural data, targets, models, scores, or
language providers until the later packet itself is green and freshly approved.

## 2026-08-13 MARC2-FW1A Private Selection Request Handoff

Generated result `a9a759aa5626a41812afe546f03aa324db7a534e` passed Base
Python job `94378074196` and Optional Neuro Readers job `94378074181` in CI
`31678418324` before the all-false request was prepared. Read
`docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_PACKET.md`, its registry,
and its request test.

The request binds one future generated/mock wrapper and, only after that exact
wrapper is separately green, one no-follow read of the pinned 418,755-byte,
mode-`0600`, 1,227-entry private manifest. It fixes a new output root, one-shot
consumption, 58 total refusal probes, a 2-MiB output cap, zero network bytes,
and zero archive/member payload bytes. Even future route `MARC2FWS-R1` stops at
target-free selection and cannot enter acquisition or neural analysis.

Every current authorization flag is false and every operation counter is zero;
the retained path was not touched while preparing this packet. Fifteen focused,
3,017 dependency-light, and 3,088 optional-neuro tests pass locally; Ruff,
compilation, all 209 registry JSON documents, artifact bindings, and diff
hygiene are clean. Immediate next gate: commit, push, and require both CI jobs
green. Then identify this exact request as the sole active Tier C packet and
wait for fresh packet-bound maintainer words. Do not implement the wrapper,
inspect the private manifest, or enter MARC2-FW2 from this all-false request
alone.

## 2026-08-13 MARC2-FW1A Authorization Decision Handoff

Request `d0a6eaa391b12f04da35bf277f6409f2750d40df` passed Base Python
job `94381244828` and Optional Neuro Readers job `94381244902` in CI
`31679428199`. After Codex identified it as the sole active Tier C packet, the
maintainer supplied the fresh exact message `continue`. Read
`docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_DECISION.md`, its
registry, and decision test.

The additive decision binds only the green packet. It permits generated/mock
wrapper work after this decision is remotely green, and one private-manifest
selection only after that exact wrapper is separately remotely green. It does
not authorize archive members, payloads, signals, targets, models, scores,
providers, or `MARC2-FW2`. At decision recording, one CI verification occurred
and every private or scientific operation counter remained zero.

Immediate next gate: test, commit, push, and require both CI jobs green for
this exact decision. Only then implement the wrapper and its 58-refusal
qualification using generated manifests and mocked filesystem facts. Do not
operate on the retained path before the exact wrapper commit is also green.
Locally, 3,031 dependency-light tests pass, and all 3,102 optional tests pass
across two fresh-process shards. The monolithic optional process tripped two
legacy resource gates only after process-wide RSS carryover; those eight module
tests pass fresh, and no historical test or cap changed.

## 2026-08-13 MARC2-FW1A Wrapper Handoff

Decision `ad1e4064256f963b2d03daeb27e4a4779b32415f` passed Base Python
job `94656172494` and Optional Neuro Readers job `94656172528` in CI
`31764052451` before implementation. Read
`docs/MARC_2_FREEWILL_PRIVATE_SELECTION_IMPLEMENTATION.md`, its registry,
module, and two implementation tests.

The additive standard-library wrapper binds the exact 418,755-byte retained
manifest identity but has not statted or opened it. It exposes only fixed
`plan`, generated `qualify`, aggregate `inspect`, and exact-proof `execute`.
The live path requires clean green HEAD proof, one-thread machine gates,
literal no-follow owner/mode/size/hash/schema validation, one bounded read/hash/
parse pass, a pre-content consumed marker, private/public output separation,
and an aggregate-only consumed failure receipt. It cannot retry, use an old
root, access a sibling, contact a network, or open an archive member.

Generated `MARC2FWS-G1` passed all 40 inherited and 18 wrapper refusals. It
selected 16 fixture participants, 96 bundles, and 384 members at
8,105,207,776 reservation bytes in 0.2679154590005055 seconds at 36,126,720-
byte peak RSS, emitting 296,659 bytes. Forty focused, 3,071 base, and 3,142
optional-neuro tests pass. Every retained-private, payload, neural, target,
model, score, provider, retry, and claim counter is zero.

Immediate next gate: commit and push this exact wrapper, then require both
remote jobs green. Only afterward perform the one already authorized private-
manifest selection once. Inspect only its aggregate result and record the
consumed route; never inspect the private output or rerun. `MARC2-FW2`, archive
members, EEG samples, events, targets, models, scores, language work, and
scientific claims remain closed.
