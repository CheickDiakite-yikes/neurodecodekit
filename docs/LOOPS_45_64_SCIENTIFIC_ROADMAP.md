# Loops 45-64: Scientific Evidence Roadmap

Machine source of truth: `registries/next_scientific_loops.v0.json`

Status: **Loop 45 mechanics is complete; Loops 46-48 are consumed or parked;
Loop 53 acquisition passed once with no rerun; future interpretation, model,
participant, device, and release actions remain separately unauthorized**

## North Star

The next “eureka” moment is not a prettier synthetic demo. It is one result
that survives this sentence:

> A model frozen before target access used intact real neural-sensor data to
> beat a matched no-signal prior and every registered corrupted-signal control
> under exact paired uncertainty.

The stronger second moment is the same result on an unseen person with zero
fit or calibration rows. EEG, streaming, home acquisition, and release work
remain valuable, but they cannot substitute for those scientific gates.

## Current Evidence

- S21 session-1: tiny CTC versus prior is an inconclusive `-0.005814` CER delta
  on five test sentences.
- S21 session-2: tiny CTC is worse than the prior by `+0.142491` CER on 63
  consumed trials.
- S7 EEG: nearest centroid is worse than the prior by `-0.113636` accuracy on
  1,100 consumed key events.
- S25 remains unopened and final-only.
- Loop 25 v1 causal preprocessing passed once on 24 target-free synthetic items
  with zero right context, zero protected reads, and no rerun authorization.
- Loops 26-43 provide detailed future contracts, not execution results.

The roadmap does not erase those negative results. It uses them to stop broad
architecture search and concentrate evidence on signal dependence,
generalization, confounds, and reproducibility.

## Design Principles

1. **No target-informed architecture search.** Predictions and controls freeze
   before protected targets open.
2. **No-signal is mandatory.** Every neural result is compared with a matched
   train-only language/task prior.
3. **Intact signal must beat corruptions.** Zero signal, channel derangement,
   time displacement, and target derangement identify shortcuts.
4. **Participant is the unit of generalization.** Random sentence splits do
   not establish unseen-person transfer.
5. **S25 stays final-only.** It receives zero fit, calibration, threshold, or
   selection rows.
6. **Negative results are terminal evidence.** Failed gates are published and
   not rerun until they pass.
7. **MEG, EEG, device, and home claims stay separate.** Shared software is not
   shared scientific performance.
8. **Mechanics precede science.** Causality, identity, timing, geometry,
   privacy, and reproducibility qualify the path before stronger language.

## Phase P6 - Real Signal Truth (Loops 45-48)

### Loop 45 - Causal Source-Path Qualification

**Status: Complete.** The separately authorized Loop 25 v1 path passed its
65,537-point static response and 23-probe alias gate before seed 2501 opened.
Development froze before seed 2502 qualification opened. Across 24 target-free
items, all 168 schedule, 240 resume, and 72 future-mutation checks passed with
zero right context and zero protected reads. Total generated output was 788,967
bytes and maximum RSS was 136,806,400 bytes.

**Gate:** passed once. **Claim:** mechanics only; retained neural information
and end-to-end latency remain unmeasured. No rerun is authorized.

### Loop 46 - Reserved S21 Neural-Effect Gate

**Status: parked; registered gate failed.** Green commit `881145d` froze the
2,908-parameter candidate, 55-row train path, 31 prediction sets, and one
six-target scoring delivery. Prediction-freeze commit `54bdca9` was remotely
green before the targets opened once. Candidate macro CER was `0.938177`
versus prior `0.751235`, so the gate failed and no rerun is authorized.

**Gate:** at least `0.05` macro sentence-CER improvement over prior, exact paired
`p <= 0.05`, strict wins on all six sentences, and the complete registered
control intersection. **Ceiling:** one person, one session, source validation
only.

### Loop 47 - Neural Signal Attribution Matrix

**Status: parked; shared attribution gate failed.** The frozen ten-condition
Loop 31 matrix ran inside the same consumed Loop 46 event. Exact-zero and
timing-only components passed individually, but the complete prior and
corrupted-signal conjunction failed. The language-model/NeuroToken extension
remained closed, and no sensor-signal-dependence claim is available.

**Gate:** intersection-union pass across every registered control. **Ceiling:**
sensor-signal dependence, not absolute brain origin.

### Loop 48 - Negative-Result Failure Localization

**Status: complete after consumed Stage A and one consumed Stage B
diagnostic.** One
hash-bound execution read four exact committed aggregate JSON artifacts totaling
155,545 bytes and selected descriptive `F5` seed-sensitive output-distribution
instability. It ran in `0.016568875` seconds, peaked at 23,429,120 bytes RSS,
and emitted 10,643 bytes. That is not a proven root cause. Authorization commit `5bae880`
and implementation commit `ca21539` were each pushed and remotely green before
the single execution.

Stage B was frozen in
`docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md` and
`registries/loop48_train_only_discrimination_contract.v0.json`. The protocol
uses a target-independent 44-fit/11-check split inside the 55 source-train
rows, prefixes `8, 16, 24, 32, 44`, seeds `4801-4803`, 20 fits, 35 target-blind
inferences, five priors, 41 prediction sets, and 2,048 exact paired sign
assignments. Predictions and telemetry must become remotely green before one
11-target scoring delivery. Because all 55 rows were used by prior Loop 26
fits, the check rows are not historically fresh; the exact Stage B ceiling is
E2 pipeline-discriminative evidence, not the earlier design-level E3 ceiling.
Raw quality, causal preprocessing, peripheral origin, independent validation,
and every generalization claim remain unavailable. Stage B received one exact
separate authorization at commit `8d17342`; implementation commit `1d840e3`
passed push CI `29461579009` and PR CI `29461580293` before protected access.
The target-blind run completed 20 fits, 4,800 optimizer steps, 35 model
inferences, five priors, and 41 prediction sets. Hash-only freeze commit
`00215b1` passed push CI `29461934145` and PR CI `29461935560` before the same
11 check targets opened once.

The primary candidate reached macro CER `0.953566` versus prior `0.822045`, a
`-0.131522` margin. All six full-size causal and linear probes were finite and
stable, but none cleared the prior rule. Stage B therefore supports `H4`
stable nonseparability and records evidence against the four fixed-shift `H3`
conditions; `H1`, `H2`, `H5`, and `H6` remain unresolved. The full intact-
signal conjunction failed. The Loop 50 router selects `L50-R05`, parking S24
acquisition for this model family. The result is consumed at E2 with no rerun,
post-check tuning, or claim upgrade. See `docs/LOOP_48_STAGE_B_RESULT.md` and
`registries/loop48_train_only_discrimination_result.v0.json`.

Stage C tested `R1` temporal-context starvation once under its frozen synthetic
boundary. After correction commit `2836ecc` passed both remote workflows, the
7,692-parameter, 470 ms causal candidate reached final CER `0.433333` and
`1/8` exact sequences versus CER `1.000000` and `0/8` exact for the
7,568-parameter zero-context ablation. Its `0.566667` relative CER improvement
passed, as did checkpoint replay, future-mutation, prefix-resume, causality,
padding, and resource checks. The candidate failed the absolute CER `<=0.10`
and exact-sequence `>=7/8` gates, so Stage C is consumed and parked without a
rerun. The run used four fits, 1,680 steps, 7.829308 seconds, 310,509,568-byte
peak RSS, 83,132 generated bytes, and zero real/protected reads or downloads.
See `docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md`,
`registries/loop48_stage_c_representation_repair_research.v0.json`,
`docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md`,
`registries/loop48_stage_c_synthetic_implementation.v0.json`,
`docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md`, and
`registries/loop48_stage_c_synthetic_result.v0.json`. No protected Stage C
preregistration or execution exists, and the synthetic contrast cannot
establish neural information or real decoding improvement.

The consumed Stage A verified hashes, reproduced aggregate blank/CER summaries,
applied the ordered tree, and emitted one target-free aggregate report. Do not
rerun it or use validation targets to select a seed, threshold, loss, or larger
architecture.

**Gate:** one evidence-backed failure class or an explicit unresolved set.

## Phase P7 - Unseen-Person Verdict (Loops 49-52)

### Loop 49 - Fresh Development-Person Intake

Planning research in `docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop49_research_boundary.v0.json` now selects **S24 session 2 block
2** as the preferred development-only MEG person from pinned public metadata:
one FIF plus one protected MAT log, exactly `1,048,579,727` bytes. S24 costs
`29,701,559` bytes more than S18 but avoids the published S1/S18 identity alias;
S25 stays final-only. The metadata pass used one thread and worker, took `3.51`
seconds, peaked at `62,685,184` bytes RSS, downloaded zero payload bytes, and
did not inspect any S24 local path or content.

The future research recommendation reserves 16 canonical sentence groups for
development selection and assigns every remaining usable unique group to fit,
with a minimum `16 + 32 = 48` gate. Identical text stays in one partition
across people, and any S21 source-train row matching future S24 selection text
must be excluded from fit. The 48-row floor, channels, geometry, duration,
signal, targets, and source-text overlap remain unavailable, so Loop 49 is
still `Not Started`, unqualified, unpreregistered, and unauthorized. Decision
0083 kept any new acquisition after the separately gated Loop 48 Stage B. The
consumed Stage B now applies `L50-R05`, so S24 acquisition is parked for this
model family.
Planning commit `5afa61e` passed push CI `29454969710` and PR #27 CI
`29455166081`; both required jobs are green.

**Gate:** one eligible nonfinal person or an explicit no-candidate result.

### Loop 50 - Multi-Source Frozen Encoder

Planning research in `docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop50_research_boundary.v0.json` now defines the future experiment
without opening protected data. It combines a global canonical-text firewall,
five-fold historical S21 out-of-fold diagnostics, one 16-group S24 development
qualification, a fixed `0.5/0.5` participant-balanced CTC loss, one shared
causal candidate family, primary seed `5001`, two nonselectable stability seeds,
ten fixed candidate/prior/corruption conditions, and an exact 20-parameter-
update inventory. Participant ID may index only sampling and metrics; it may not
enter a model, scaler, affine, adapter, checkpoint, or decoder. The four-run
margin below the 24-run ceiling is not rerun permission.

The future primary gate is per-person and worst-person, never pooled-only. The
primary seed must beat the strongest no-signal prior by at least `0.05` macro
CER and strictly beat exact-zero, channel, time, timing-only, and linear
conditions separately on S21 and S24. S24 must improve over the S21-only neural
comparator while S21 degrades by no more than `0.02`; stability seeds may not
replace the primary. S24 selection remains development evidence, S21 remains
historically used, and S25 remains the one-time final-only person.

Loop 50 is still `Not Started`, unpreregistered, and unauthorized. Loop 48
Stage B has closed at `L50-R05`, which parks this same-family S24 acquisition
path. Any future representation repair must be separately preregistered before
another intake decision can be considered. All 31 authorization fields in the
planning snapshot remain false and every protected/model/training/scoring
counter in that snapshot is zero.
Planning commit `085f341` passed push CI `29458102674` and PR #28 CI
`29458116994`, with both required jobs green in both workflows.

**Gate:** positive prior/control ordering on both development people, with no
pooled rescue, seed substitution, target-corpus normalization, or post-target
rerun.

### Loop 51 - S25 Final-Only Freeze Packet

Freeze source commit, environment, model, checkpoint, preprocessing,
comparators, control predictions, exact S25 files and bytes, target-isolation
order, 48-row minimum, `0.05` margin, and 65,535 paired assignments plus the
observed assignment. Independent review must find zero target-dependent choice.

**Gate:** every execution field hash-bound before any S25 payload opens.

### Loop 52 - S25 Strict Zero-Shot Verdict

Run the frozen source model on pinned S25 session 2 block 2 with zero target-
person fit or calibration. Open final targets once and retain every outcome.

**Gate:** at least 48 unique rows, at least `0.05` absolute macro-CER gain over
the frozen prior, paired `p <= 0.05`, and strict wins over zero-signal, channel-
deranged, and time-displaced controls. A failure is the final negative result;
S25 then becomes consumed forever.

## Phase P8 - Accessible EEG Evidence (Loops 53-56)

### Loop 53 - Fresh S20 EEG Acquisition Gate

**Status: consumed; acquisition passed; no rerun.** The frozen contract is
`registries/loop53_fresh_eeg_acquisition_contract.v0.json`. It binds revision
`88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`, one S20 session 2 block 2
BrainVision triplet plus companion MAT log, four exact files, and 96,090,264
bytes. Authorization `2a47bbc` and implementation `8ec5b1b` were separately
green before the one invocation acquired and opaque-verified the complete
bundle. It did not parse a header, marker, signal, or MAT field; read a target;
create a cache/split; or run a model. Header audit and cache planning belong to
Loop 54.

**Gate:** exact revision/license/path/size/hash identity, a complete isolated
bundle, 128 MiB network and 256 MiB incremental-disk caps, one thread/worker,
and zero forbidden access counters. All gates passed in 3.629499 seconds at
63,225,856-byte peak RSS and 102,035,529-byte peak incremental disk. The result
is in `registries/loop53_acquisition_result.v0.json`; S7 remains consumed and
excluded.

### Loop 54 - EEG Trial Geometry And Confound Ledger

**Status: planning research complete; acquisition passed; L54-A preregistered;
exact authorization pending.**
All content stages unauthorized until their exact decision and green
implementation gates pass.
`docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop54_eeg_trial_geometry_research.v0.json` now replace the coarse
"header then signal/target" idea with four ordered stages. L54-A parses exactly
one VHDR without MNE or sibling-file resolution. L54-B opens only VHDR+EEG,
retains every source channel, and emits bounded target-blind quality summaries
without rereference, interpolation, ICA, filtering, resampling, target-aligned
windowing, or a raw-signal derivative. L54-C opens only VHDR+VMRK+MAT in an
isolated process and emits opaque trial commitments and aggregate alignment
facts while protecting marker descriptions, keycodes, responses, and targets.
L54-D reads only the aggregate public ledgers and returns eligibility or a
measured park reason.

The source audit found that the current Loop 19 extractor is not eligible for
this future claim path: it attaches BrainVision marker annotations, loads the
MAT payload, excludes EOG-named channels, reads signal, and writes plaintext
labels in one invocation. That historical engineering result remains valid at
its original boundary.

**Gate:** at least 48 unique performed trials with unambiguous identity, strict
stage isolation, all channels retained, and every channel, geometry, reference,
quality, and recorded-confound field known or explicitly unavailable. Event
windows are not independent trials. Loop 54 creates no split, model, training,
inference, score, or scientific result. Loop 53 has finished cleanly, but each
real content stage still requires a separate exact Tier C decision.

L54-A is now frozen in
`registries/loop54_stage_a_vhdr_contract.v0.json` at registration commit
`c114623`. It binds exactly one 11,705-byte VHDR, no sibling resolution or MNE,
18 acceptance gates, 22 refusals, one content open, one registered execution,
and one thread/worker under 30 seconds, 256 MiB RSS, and 1 MiB output. No S20
path was statted and no payload was opened during preregistration. Registration
CI `31127199848` was cancelled before any test step during the Actions outage;
a replacement run over exact commit `c114623` must become green before its
exact Tier C packet is frozen. Implementation and execution remain
unauthorized.

### Loop 55 - Fresh EEG Neural-Effect Gate

Planning research is complete in `docs/LOOP_55_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop55_eeg_neural_effect_research.v0.json`; the experiment remains
`Not Started` and unauthorized. The primary question is no longer one vague
"EEG decoding" score. It is split prospectively into two ordered endpoints
from the same frozen final trials:

1. causal pre-keypress performed-hand prediction; and
2. causal pre-keypress 29-class performed-key prediction, reported as macro
   trial keypress-aligned CER.

The future candidate uses only EEG samples strictly before each known keypress,
zero right context, and no language model. The published `[-200,+300] ms`
window is a noncausal diagnostic only because it includes post-keypress motor
execution and somatosensory feedback. Intended sentence text is secondary;
performed key and hand are the primary targets.

**Gate:** after Loop 53 and Loop 54 close cleanly, freeze one grouped trial-level
split, one `<=10,000`-parameter causal family, at most 12 fits, and twelve
matched conditions. Each causal endpoint must clear its practical margin over
the strongest train-only no-signal prior and strictly beat every applicable
zero, row, channel, timing, train-pairing, timing-only, and peripheral control
under exact paired final-trial tests. A final prediction hash must be committed,
pushed, and remotely green before the same final targets open once. One thread,
45 CPU minutes, 1 GiB RSS, and 64 MiB generated output remain hard ceilings.
No S20 read, split, target, model, training, inference, or score is authorized
now.

An additive AI-assisted representation policy is now implemented for synthetic
proposal governance only. It freezes one compact causal family, exact causal
window and resource checks, a small hyperparameter menu, canonical proposal
hashes, protected-content refusals, and at most four future train-inner proposal
rounds inside the same 12-fit ceiling. AI may eventually propose recipes from
aggregate train-inner summaries, but it may never receive raw protected EEG,
individual labels/predictions, intended text, selection/final outcomes, an LLM,
or claim authority. The real phase remains Loop 54 dependent and separately
unauthorized. See `docs/LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md` and
`registries/loop55_ai_research_policy.v0.json`.

The additive 2026-08-06 open EEG strategy refresh leaves this frozen planning
boundary intact while sharpening the pre-execution ladder. Current open
foundation-model benchmarks support retaining specialist models at this data
and compute scale. Before a future protected Loop 55 freeze, the recommended
path is one separately authorized public motor-execution positive control,
selection of at most one classical CSP/Riemannian family on that public lane,
and a fixed causal pre-keypress motor-physiology assay beside the compact model.
The exact public prospect is nine PhysioNet EDF files from S001-S003, runs
3/7/11, totaling 23,248,224 bytes under a future 32 MiB network cap. No file was
downloaded and no execution is authorized. Foundation models and generative
EEG imputation remain separate, later, public-data-only research lanes. See
`docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md` and
`registries/open_eeg_rd_strategy.v0.json`.

The additive architecture pass in
`docs/LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md` and
`registries/loop55_causal_motor_lattice_research.v0.json` selects `CML-v0` as
the next source-independent hypothesis. It uses separate potential, causal mu,
and causal beta views, one rank-8 spatial mixer per view, a 24-dimensional
bottleneck, and a fixed physical-key lattice. Hand probability is an exact
marginal of the 29-key distribution, so the two endpoints cannot silently
contradict. The reference at 64 channels and 18 primitives has 4,535 trainable
parameters. Eight same-checkpoint probes localize failure without replacing
the registered scientific controls.

The public ladder now has two noninterchangeable axes: the existing PhysioNet
slice tests left/right execution mechanics, while a future bounded EEG+EMG MRCP
slice would test strictly pre-movement timing against measured EMG onset. Both
are unauthorized. Synthetic CML-v0 implementation is also `Not Started`; this
research does not amend the frozen Loop 55 gate or authorize S20 work.

### Loop 56 - Cross-Modality Accessibility Verdict

**Status: planning research complete; Loop 55 result dependent; final verdict
`Not Started`; unauthorized.** The exact boundary is in
`docs/LOOP_56_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop56_cross_modality_accessibility_research.v0.json`.

The design freezes five verdict classes, from shared proven artifact through
prohibited inference; 12 non-skippable capability levels, from source identity
through assistive or clinical utility; 18 comparison dimensions; a 16-field
claim sentence; and a 12-part at-home conjunction. It keeps published v1/v2
results external, local S21 and S7 negatives unmatched, and fresh S20 evidence
unavailable. Continuous input, causal incremental output, measured end-to-end
latency, device mechanics, and repeated home feasibility are separate gates.

**Gate:** after Loop 55 closes, preregister the exact committed aggregate
allowlist and hashes, then obtain a separate exact Tier C scientific-claim
decision. The future verdict may count classes and satisfied capability levels
only. It may not open payloads, ignored artifacts, caches, targets, predictions,
checkpoints, or models; recompute scores; pool modality or participant values;
inherit thresholds; equate channels or representations; or extrapolate to a
device, home, patient, or clinical result. Until then, the provisional route is
`L56-O2`: mechanics and interfaces only.

## Phase P9 - Causal Local Use (Loops 57-60)

### Loop 57 - Train-Stream Causal Parity

Join qualified causal preprocessing, the frozen encoder, NeuroToken state,
decoder state, timestamps, schedules, resumes, and anomalies. Target-free
fixtures precede any authorized neural replay.

An additive decoder strategy now assigns the hosted language role to frozen
`gpt-5.6-sol` downstream of a compact causal sensor adapter. Hosted requests
receive structured CTC and key evidence, not raw EEG or custom hidden
embeddings. The future parity surface must preserve all four matched arms,
including full `FM-A02` and fixed item-deranged `FM-A03`, under one model and
prompt. FM-0 remains the deterministic no-call bridge. FM-1 is now separately
preregistered and exactly authorized for one synthetic-only
`gpt-5.6-terra` provider qualification, but it cannot execute until its exact
implementation commit is pushed and remotely green. This does not authorize
real replay, target delivery, scoring, training, tuning, or scientific claim
promotion. See
`docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md` and
`registries/foundation_model_decoder_strategy.v0.json`, plus
`docs/FOUNDATION_MODEL_LIVE_SMOKE_IMPLEMENTATION.md`. FM-0 is locally
implemented: 7,327 synthetic input bytes compiled into 12 plans and 34,349
output bytes in 0.00275 seconds at about 21.5 MB peak RSS. The implementation
now also includes the bounded FM-1 transport and strict result inspector. Its
zero-network dry run compiled 12 blinded wire requests totaling 18,399 bytes
in 0.004586541 seconds at 33,832,960-byte peak RSS. All provider, credential,
spend, protected-read, target, training, and scoring counters remain zero, and
Loop 57's real-integration status remains `Not Started`.

### Loop 58 - Local Capture And Device Mechanics

Progress OpenBCI Cyton through synthetic/playback, battery no-contact bench,
and only later a separately consented scalp stage. Keep packet counters, host
timestamps, physical capture time, locality, safety, and privacy distinct.

### Loop 59 - End-To-End Latency And Stability Gate

Instrument common-clock source events through arrival, preprocessing, frames,
decode, render, revisions, finalization, and abstention. Replay scheduling is
not capture latency. Report p50/p95/max and failure traces.

### Loop 60 - At-Home EEG Feasibility Pilot

One separately consented participant may test battery-only, network-off,
local-only setup burden, channel quality, artifacts, repeated-session identity,
privacy, retention, and safety. This is acquisition feasibility, not home text
decoding.

## Phase P10 - Independent Evidence And Release (Loops 61-64)

### Loop 61 - Versioned Reproducible Artifact

Execute Loops 37-39 for a no-participant-payload release candidate. Freeze
source, package, environment, semantic manifests, field-specific tolerances,
supported OS/Python cells, privacy lifecycle, license, tests, resources, and
failure records.

### Loop 62 - Independent Artifact Reproduction

One qualifying external contributor executes the public target-free artifact
under Loop 43's commit-reveal, public-help, record-don't-fix, unprivileged CI,
and immutable discrepancy protocol.

### Loop 63 - Independent Scientific Replication Packet

Prepare a separately governed protocol for an independent implementation and
qualifying new participants. Author-artifact reproduction cannot substitute.
No local participant payload is transferred by default.

### Loop 64 - Scientific Claim Promotion And Release v1

Update the Loop 44 matrix. Promote only claims whose cohort, split, comparator,
uncertainty, control, privacy, license, reproducibility, and governance gates
pass. Keep engineering and science in separate sentences. A release can remain
an engineering alpha even if scientific performance is negative.

## Critical Kill Branches

| Trigger | Mandatory response |
|---|---|
| Loop 45 result is invalidated | Keep all real training sealed; amend mechanics only. |
| Loop 46 fails | Park scaling; run Loop 48; do not open source test or S25. |
| Loop 47 finds a shortcut | Block neural-contribution wording; prioritize confound repair. |
| No Loop 49 development person | Keep S25 final-only and hold transfer. |
| Loop 50 fails one person | Do not freeze or open S25. |
| Loop 52 fails | Publish negative zero-shot result; consume S25; no calibration. |
| Loop 55 fails or remains confounded | Keep EEG as mechanics/access evidence; no home decoding. |
| Loop 58 fails | Park the exact device/transport; no substitution. |
| Loop 60 fails safety/privacy/quality | Stop home pilot; retain feasibility limits. |
| Loop 61/62 fails | Hold release; retain the discrepancy. |

## Resource Posture

- one CPU thread and one worker by default;
- no larger model merely because a gate failed;
- preferred incremental real-data envelope remains 5 GB and absolute maximum
  remains 10 GB;
- S25's pinned bundle remains exactly 1,009,939,983 bytes;
- generated artifacts are capped per loop and excluded from Git unless
  explicitly reviewed for release;
- no consumed S21 session-2, S7, or protected seed is reopened for tuning;
- no cloud, live stream, participant, device, or release operation occurs
  without its own exact authorization.

## Primary-Source Basis

The roadmap uses Brain2Qwerty v1/v2 for the task and performance ceiling;
Varoquaux et al. for grouped cross-validation and circularity risk; Ojala and
Garriga for permutation controls; EMG/EOG artifact literature for peripheral
firewalls; Model Cards and Datasheets for reporting; NIST AI RMF for documented
test and risk governance; FAIR4RS for versioned software identity; and ACM for
repeatability, reproduction, and replication terminology. Exact URLs live in
the machine registry.

## Authorization Boundary

This document is a research roadmap. Loop 45 is complete at its target-free
mechanics boundary; Loops 46/47 are consumed and parked; Loop 48 Stage A is
consumed at descriptive `F5`, and Stage B is consumed at `H4` stable
nonseparability with `L50-R05` parking S24 for this model family. Stage C
research permits only a green-bound synthetic implementation and calibration
under the approved charter; it does not open a protected roadmap experiment.
Loop 53 acquisition mechanics passed once and are consumed without a rerun;
Loops 49-52 and 54-64 remain `Not Started` at their experiment boundaries.
Every current `execution_authorized` flag and every global authorization field
is false because no future action is presently open. The roadmap does not
authorize a Loop 45 rerun, Loop 46/47 rerun, Loop 48 protected rerun, Loop 53
rerun, S20 content interpretation, real-data representation-repair training,
any new real-data read or download, target opening, S24/S25 access, stream,
device, participant contact, home recording, external outreach, tag, release,
archive, DOI, or scientific claim.
