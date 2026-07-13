# NeuroDecodeKit Loops 25-44 Roadmap

Date: 2026-07-12

Status: **Loop 25 amended v1 and awaiting authorization; Loops 26-29 planning research complete; Loops 30-44 planning only; no execution is authorized**

Machine source of truth: `registries/next_20_loops.v0.json`

Research basis: `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`

## Purpose

These 20 loops are the next claim-driven tranche after the parked Loop 24
decision. They are designed to move NeuroDecodeKit from validated interfaces
and honest negative real-data results toward one defensible neural, transfer,
streaming, or device result.

The roadmap does not assume that every branch succeeds. Each loop must end in
`proceed`, `park`, or `kill`, and a negative result can be the correct closeout.

## Boundary Before Loop 25

- Loop 24 is parked after its registered target-free selection: float32 is
  retained, seed 2401 is consumed, seed 2402 qualification remains unopened,
  and 65.154951 seconds exceeded the frozen 60-second cap.
- RW3 Stage A has a prepared packet at `163ff2f`; `authorized_now` remains
  false.
- S21 session-1 source-test rows are observed, S21 session-2 and S7 EEG
  evaluation evidence are consumed, and synthetic seeds 2203, 2303, and 2353
  remain closed to selection or tuning.
- The Loop 24 park satisfies Loop 25's dependency on an explicit prior-loop
  decision, but it does not authorize Loop 25.
- Loop 25's original registration is frozen at `a36d97b`; anti-alias amendment
  v1 is frozen at green commit `b6b92d8`. The original request was superseded
  before authorization. The current v1 request remains `authorized_now: false`,
  and seeds 2501/2502 are unopened.
- This roadmap does not authorize a download, real-data read, consumed-cache
  read, target read, fixture, model run, training run, optional streaming
  import, socket, stream, board, device, or hardware session.
- The default future cap is one numerical thread, one worker, and at most 32
  MiB of generated artifacts unless a lower loop-specific cap applies.

## Phase Map

| Phase | Loops | Purpose | Exit condition |
|---|---:|---|---|
| P1 - Causal Evidence | 25-28 | Earn one causal validation and fresh transfer decision without reused evidence | Causal path is audited; neural validation either proceeds or parks; a fresh holdout is explicitly approved or unavailable |
| P2 - Translation And Generalization | 29-32 | Separate modality translation, interaction, neural attribution, and calibration | Portability requirements, replay UX, contribution ablations, and calibration claims are independently bounded |
| P3 - Reliability And Confounds | 33-36 | Measure scaling, abstention, peripheral shortcuts, and geometry failure | Positive results survive required controls or their claims are blocked |
| P4 - Reproducibility And Local Deployment | 37-40 | Standardize provenance, privacy, cross-machine behavior, and edge packaging | Artifacts reproduce and any packaging benefit is measured against a frozen reference |
| P5 - Live Translation And Release | 41-44 | Join authorized replay to tokens, qualify one device, reproduce independently, and decide claims | Only evidence-backed capabilities enter a release; unsupported claims remain unavailable or parked |

## Execution Rule

Before starting any loop, create a dedicated preregistration or implementation
packet that binds its exact inputs, outputs, access counters, metrics,
thresholds, caps, refusals, and authorization sentence. Updating this roadmap
or marking a loop as the next candidate is never execution authorization.

Loop 25 has completed an amended preregistration step. Its next action is the
exact decision in `docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, not
implementation.

## Loop 25 - Causal Preprocessing Audit

**Current status:** Amended preregistration at green commit `b6b92d8`; the v0
packet was superseded before authorization; the v1 request is prepared with
`execution_authorized: false`; no fixture, coefficient, seed open, transform,
partition, CLI, or runtime exists.

**Core question:** Can every transform before the causal encoder run
incrementally without future samples, evaluation-fit statistics, timestamp
drift, or chunk-boundary changes?

**Why it moves the goal:** Loop 21 proves a causal frame producer, but a
future-aware filter, whole-trial normalization, resampling shortcut, or end
padding can invalidate the full streaming claim upstream.

**Registered build:** Implement one five-channel, 1000-to-100 Hz stateful
notch/bandpass/dedicated-elliptic-antialias SOS chain, phase-locked integer
decimation, frozen normalization, and replay harness. Before seed access, audit
65,537 response points and 23 exact alias probes across the complete 50-500 Hz
folding band. Bind state, absolute sample indices, timestamps, valid lengths,
configuration, hashes, warnings, and all 23 access counters into provenance.

**Research:** Document causal versus zero-phase filtering, group delay,
resampling and trigger behavior, train-only normalization, flush semantics, and
which existing transformations are incompatible with an online path.

**Data and controls:** The future physical partitions contain 12 target-free
items each from unopened seeds 2501 and 2502 across six signal families. Seven
exact chunk schedules, ten resume cuts, three future-mutation cuts, 45 refusal
IDs, a 65,537-point response grid, and 23 alias probes are frozen. The static
full-folding-band gate occurs before development opens. Qualification opens
once only after the development report is frozen and every gate passes.

**Metrics:** right-context samples/ms; valid-sample and timestamp identity;
full 50-500 Hz attenuation and alias-map correctness; maximum offline-stream
error; schedule hashes; state bytes; runtime; peak RSS; input/output bytes;
raw/cache/target/model/training counters.

**Gate:** Before seed access, park if the dedicated anti-alias or complete chain
misses the full 50-500 Hz gate. Then proceed only with zero declared right
context, registered numerical tolerance, exact semantic identity, zero
evaluation access, and passed caps. Park any transform that needs future
samples or whose timing cannot be proven.

**Dependencies and authorization:** Loop 24 is already parked. Loop 25 now
requires the separate exact decision in
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, followed by a tested, pushed, green
authorization-only commit before
implementation. Even exact authorization excludes real/consumed data, targets,
models, training, RW3, streams, devices, and hardware. The Loop 25 cap is one
thread/worker, 4 MiB fixtures, 16 MiB working arrays, 8 MiB total generated
bytes, 45 seconds internal runtime, 4 KiB state, and 1 GiB peak RSS.

## Loop 26 - Real Validation-Only Encoder Gate

**Current status:** Planning research complete; experiment status remains `Not
Started`, no preregistration or authorization sentence exists, and all data,
target, model, training, and validation access remains unauthorized. See
`docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop26_research_boundary.v0.json`.

**Core question:** Does one fixed, small causal encoder show real neural
information above no-signal and shuffled controls on source validation without
touching test?

**Why it moves the goal:** NeuroDecodeKit has not demonstrated a real neural
advantage. This is the smallest honest predictive gate that can justify
continuing rather than scaling model complexity by instinct.

**Build:** After Loop 25 closes, freeze the tiny architecture, preprocessing,
optimizer, stopping rule, seeds, output report, and access ledger before
targets open. The research recommendation preserves the existing 2,908-
parameter ceiling by replacing the baseline's symmetric kernel-3 padding with
two samples of left padding. Fit only on authorized source-train rows and open
the six source-validation rows once under the registered sequence.

**Research:** Complete. Six rows permit exactly 64 paired sign assignments, so
the minimum attainable one-/two-sided p-values are 0.015625/0.03125 with six
nonzero pairs. These are sentence instances from one person/session, not six
biological replicates. A validation pass cannot authorize or predict source-
test, cross-session, or unseen-person performance.

**Data and controls:** Required controls are the same-split train-only no-signal
prior, zero-signal inference, one semantic-ID target derangement, nonwrapping
zero-filled time displacement, channel-name-hash derangements, and a 2,884-
parameter linear signal CTC. Time/channel corruptions are engineering
falsification controls, not exact null tests over autocorrelated samples. Five
consumed source-test rows and every consumed session-2 row stay closed.

**Metrics:** Macro per-sentence and corpus CER; every one of the six paired item
differences; the complete 64-assignment exact null; exact sequence accuracy;
WER; blank fraction; wins/ties/losses; margin over every control; parameters;
training/runtime/RSS/bytes; all raw/cache/target/model/training access counts.

**Gate:** A future preregistration must freeze the practical margin, exact
paired test, all-control rule, tie behavior, seed, schedule, and access order.
Proceed only if that registered neural-versus-prior margin and every required
control pass with no access violation. Otherwise park real-model scaling,
preserve the negative result, and do not touch test.

**Dependencies and authorization:** Requires a Loop 25 result compatible with
the exact input path plus a separate real-cache, target, training, model, and
single-validation-open authorization. Planning research is not
preregistration. The future ceiling is one thread/worker, 2,908 trainable
parameters, 20 total CPU minutes across candidate and controls, 1 GiB RSS, and
32 MiB outputs.

## Loop 27 - Fresh Holdout Preregistration

**Current status:** Planning research complete; experiment status remains `Not
Started`. S25 session 2 block 2 is the selected metadata-only MEG candidate at
exactly 1,009,939,983 bytes, but no preregistration, acquisition request,
download, local MAT hash, header/signal/target access, model run, or final open
is authorized. See `docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop27_research_boundary.v0.json`.

**Core question:** Which independent participant, session, or task-matched
recording can answer the next claim without recycling S21 session-2 or S7?

**Why it moves the goal:** A fresh one-time evaluation creates new evidence;
another analysis of an observed cohort does not.

**Build:** Create a metadata-only candidate registry and one exact acquisition
packet: files, bytes, hashes/revision, license, subject/session/task identity,
split protocol, target isolation, no-signal controls, access sequence, and
one-time decision rule.

**Research:** Complete at the planning boundary. A pinned metadata pass examined
315 MEG files, found 23 strict single-FIF/log pairs and 16 eligible pairs, and
selected S25 session 2 block 2 as the smallest eligible same-modality/task
candidate. S23 is smaller but officially excluded because of a metallic
implant; S20 is task-matched EEG and remains a separate RW4 cohort.

**Data and controls:** Public metadata and documentation only. Perform identity
overlap, repeated-text, task-match, timing, license, and redistribution audits.
Do not download, preview rows, read signals, or inspect targets.

**Metrics:** planned file and byte counts; subjects/sessions/trials; unique
sentence groups; license status; identity overlap; task-match warnings;
available/unavailable fields; all access counters.

**Gate:** A future packet is eligible only when independence, task match,
license, byte cap, split power, controls, and one-time analysis are explicit.
Ambiguity produces `hold`, not a substitute consumed cohort.

**Dependencies and authorization:** Metadata research is complete without a
prior-loop dependency. Preregistration now waits for a compatible Loop 25
result, a frozen Loop 26 source model/control package, and header and target-
isolation protocols. Loop 28 planning research now supplies the recommended
final-only T2 decision rule, but Loop 27 must still bind that rule and all
upstream hashes in a later preregistration. Any download, local MAT hash,
header, signal, target, model, training, or final access requires its own later
exact packet and authorization.

## Loop 28 - Session And Person Transfer

**Current status:** Planning research complete; experiment status remains `Not
Started`. The selected future question is T2 strict unseen-person zero-shot on
the final-only S25 candidate. No preregistration, authorization sentence,
acquisition, payload operation, model/control prediction, calibration, or final
open exists. See `docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop28_research_boundary.v0.json`.

**Core question:** Does the frozen causal system transfer to a genuinely fresh
session or person, and how much predeclared calibration is required?

**Why it moves the goal:** The current same-person session-2 result is negative.
A fresh, one-time test is required before promoting any transfer claim.

**Build:** After Loops 25-27 close, freeze the source model, split membership,
strict zero-shot path, no-signal prior, corruption controls, threshold,
randomization schedule, and report before opening the fresh holdout. Calibrated
adaptation remains a separate physically partitioned future design.

**Research:** Complete at the planning boundary. The T0-T3 taxonomy separates
same-session held-out text, same-person cross-session, unseen-person strict
zero-shot, and unseen-person supervised calibration. Unlabeled target-corpus
adaptation is separately labeled transductive and cannot count as T2. The v2
paper is asynchronous but noncausal; its joint model includes target-person
data and its leave-one-out regime finetunes on the target, so it does not
establish strict zero-shot person transfer.

**Data and controls:** A future T2 test may use only the approved Loop 27 S25
holdout, with zero candidate training, validation, calibration, target-wide
normalization, subject embedding, adapter, threshold, or unlabeled corpus-fit
rows. Compare the same-split source-train-only prior, frozen zero-shot model,
exact-zero signal, channel-name derangement, and nonwrapping time displacement
on identical final rows. Keep identity and sentence-overlap claims separate.

**Metrics:** Primary macro sentence-CER difference, prior minus model; one-sided
paired randomization p-value from 65,535 frozen sign assignments plus the
observed assignment; corpus CER; WER where justified; exact sequence accuracy;
wins/ties/losses; identity, overlap, runtime, RSS, bytes, and access counters.

**Gate:** T2 support for this one S25 person/session/task requires at least 48
eligible unique final rows, at least 0.05 absolute macro CER improvement over
the frozen prior, paired `p <= 0.05`, a strict win over every corruption
control, and zero identity/hash/access/resource failures. A tie or unavailable
required field parks the claim. One passing person is not population
generalization, and unseen text additionally requires a zero-overlap audit.

**Dependencies and authorization:** Requires Loops 25-27 plus explicit
acquisition and one-time test authorizations. Planning research resolves the
Loop 27 final-only-rule question but satisfies none of the measured upstream
dependencies. No such data or run is authorized by this document.

## Loop 29 - Portable Sensing Translation

**Current status:** Planning research complete; experiment `Not Started`.
`docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop29_research_boundary.v0.json` are the human and machine
boundaries. All 24 `authorized_now` fields are false.

**Core question:** Which validated requirements survive movement from
cryogenic MEG toward OPM-MEG or EEG, and which assumptions break?

**Why it moves the goal:** Users care about accessible sensing, but random
channel reduction, a file reader, and a vendor data sheet are not portable
device evidence. The completed research selects scalp EEG as the immediate
local-first accessibility lane, OPM-MEG as a same-modality partner/lab lane,
cryogenic MEG as the scientific reference, and peripheral wearables as controls
or separate accessibility inputs.

**Build:** Future work may implement the versioned 15-field modality matrix,
six-level qualification ladder, and 12-gate device packet validator. No Loop
29 implementation, device descriptor, acquisition packet, SDK, or runtime
exists now.

**Research:** Completed primary-source OPM-MEG and EEG review records four
separate modality profiles, measured-versus-specified evidence, task gaps,
clock/transport risks, geometry/reference requirements, home-recording limits,
and the minimum future partner/device packet. Brain2Qwerty v2's 76/153/230
random cryogenic channel subsets remain model sensitivity evidence, not OPM-
MEG or EEG device evidence.

**Data and controls:** Public specifications and existing aggregate results
only. Keep cryogenic MEG, OPM-MEG, scalp EEG, sEMG, eye, and motion evidence in
separate rows. Exclude synthetic channel subsets as modality equivalence. The
preferred incremental storage ceiling is 5,000,000,000 bytes and the absolute
ceiling is 10,000,000,000 bytes. The selected future S20 plus S25 bundles total
1,106,030,247 bytes, but capacity permission is not download permission and
Loop 29 downloaded zero bytes.

**Metrics:** requirement coverage; unavailable fields; sensor count/rate/units;
geometry and clock provenance; measured-versus-specified count; future
qualification requirements.

**Gate:** Proceed to one device-specific packet only when task, raw locality,
reference, geometry, timing, packets, privacy, licensing, repeated-session,
peripheral-control, and resource requirements are directly measurable.
Otherwise retain the research matrix without a hardware claim. Home EEG
recording mechanics do not establish home text decoding, and OPM wearability
does not establish ordinary-home operation.

**Dependencies and authorization:** Depends on Loop 27's evidence taxonomy.
The planning dependency is satisfied, but preregistration and execution remain
blocked. Research does not authorize S20, S25, a real header/signal/target read,
a model or training run, a device session, recording, download, SDK import,
socket, stream, purchase, partner session, or hardware operation.

## Loop 30 - Local Private Streaming Prototype

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop30_research_boundary.v0.json`. Every one of 30 authorization
flags is false; no trace seed, fixture, UI, server, or browser run exists.

**Core question:** Can a user inspect incremental hypotheses, revisions,
timing, provenance, and refusals locally without confusing replay with live
decoding?

**Why it moves the goal:** A final sentence hides when output appeared, how
often it changed, what source produced it, and whether confidence exists.

**Build:** After separate authorization, implement a loopback-only target-free
replay inspector with partial hypotheses, explicit revisions and finalization,
source identity, nine clock domains, six latency claim levels, resource
telemetry, warnings, hashes, proof posture, and inspectable local artifacts.

**Research:** Completed. Four source modes, a 30-field target-free trace, nine
clocks, six latency levels, fixed localhost/file/network controls, accessible
status semantics, 18 future gates, and 30 refusal IDs are frozen before any
implementation.

**Data and controls:** A future run may generate one new target-free synthetic
trace from a seed frozen before payload creation. Do not reopen consumed Loop
23/24 arrays or S7/S21 evidence. Show source, proof posture, producer/decoder
causality, confidence unavailable, and the no-signal comparator. Separate cold
start, scheduling, queue, producer, decoder, transport, browser receive,
render, and finalization. No cloud, target, model, socket, stream, hardware, or
raw real signal.

**Metrics:** first partial, first committed token, and finalization by available
clock domain; revision count, edit overhead, prefix commitment, and stable
duration; W3C long-task count and Event Timing availability; runtime/RSS/bytes;
network/WebSocket/raw/cache/consumed/target/model/training/calibration/stream/
hardware counters; desktop/mobile accessibility and render QA.

**Gate:** Close only as a local replay interface when all 18 requirements and
30 refusals pass, every source/causality/latency/confidence/proof label stays
visible, clocks retain their origins, browser QA sees zero non-loopback traffic
and zero 50-ms long tasks, and resource/access caps pass. Park any UI that
implies a live, neural, confidence, or end-to-end real-time result its artifact
does not prove.

**Dependencies and authorization:** Depends on Loop 25. Planning research only;
the experiment remains `Not Started`. Trace generation, implementation, server
launch, and replay need a separate Loop 30 authorization. That decision cannot
authorize RW3, a recorded/live source, real data, targets, models, training,
calibration, SDKs, devices, or hardware.

## Loop 31 - Neural Contribution Ablation

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop31_research_boundary.v0.json`. Every one of 19 authorization
flags is false; no cache, target, checkpoint, model, training, validation, LLM,
Neuro Token, or experiment fixture was opened or created.

**Core question:** When a predictive system improves, how much comes from
sensor signal rather than text priors, timing, declared context, broken
correspondence, or pipeline artifacts?

**Why it moves the goal:** This is the claim firewall against crediting
autocomplete or event structure to brain activity.

**Build:** After separate authorization, execute the frozen 10-condition local
encoder matrix with full signal, no-signal prior, exact-zero input, item,
channel, time, timing-only, context-only, train-pairing, and linear diagnostic
conditions. Keep the separately gated 5-condition LLM/Neuro Token extension
unavailable unless an authorized language-assisted system actually exists.

**Research:** Completed. Five estimands separate encoder signal dependence,
language-prior gain, conditional Neuro Token gain, total-system gain, and the
currently unavailable brain-specific increment. Six claim classes cap a clean
local encoder result at sensor-signal dependence until Loop 35 passes.

**Data and controls:** Future authorized six-row source validation only. Freeze
item, channel, temporal, and train-pairing transforms before protected content;
produce and hash every prediction target-blind before one target open. Keep
consumed source test, session 2, S7, S20, and S25 closed. A prompt or sentence
list is forbidden; if exposed, its context-only baseline becomes mandatory.

**Metrics:** macro sentence control-minus-full CER; exact one-sided paired
component tests; intersection-union decision; primary practical margin;
language-prior and conditional Neuro Token gains; per-item edits and
wins/ties/losses; condition-specific access/model/training/runtime/RSS/byte/
hash/warning ledgers.

**Gate:** A future sensor-signal dependence result exists only if every
applicable required condition passes the exact six-item intersection-union
gate, the primary no-signal practical margin, target-blind freeze order,
ledgers, hashes, and resources. A tie fails. Brain-specific attribution remains
unavailable until Loop 35 excludes peripheral and task-locked shortcuts.

**Dependencies and authorization:** Depends on an actual Loop 26 result, which
itself depends on Loop 25. Planning research only; the experiment remains `Not
Started`. Preregistration, cache/target/checkpoint/model/training/validation,
LLM/Neuro Token, S20/S25, stream, device, and hardware operations each remain
unauthorized. The future local envelope is one thread/worker, 2,908 parameters,
1,200 seconds training, 32 MiB artifacts, 1 GiB RSS, and zero new data/model
downloads.

## Loop 32 - New-Subject Calibration And Adaptation

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop32_research_boundary.v0.json`. Every one of 22 authorization
flags is false; no candidate, participant payload, calibration signal, label,
checkpoint, adapter fit, training run, or final evaluation was opened.

**Core question:** What is the smallest honest calibration budget that improves
a fresh person without training on their final rows?

**Why it moves the goal:** Participant variability is a central barrier, and a
calibrated result must never be presented as zero-shot transfer.

**Build:** After separate candidate-specific preregistration and authorization,
test one pointwise causal 32-parameter hidden diagonal-affine adapter over the
frozen 2,908-parameter Loop 26 source encoder. Keep strict zero-shot, unlabeled,
label-light, and supervised modes separate. Use the nested `0, 2, 4, 8, 16,
32` unique-sentence schedule and update only the adapter's 16 scales plus 16
biases.

**Research:** Completed. The claim ladder separates a pre-calibration strict
zero-shot reference from unlabeled transductive calibration, at-most-eight-row
label-light calibration, and at-most-32-row supervised calibration. The human
burden ledger includes unique/repeated items, active/task/setup/break minutes,
labels and corrections, selection labels, compute, and the measured or
unavailable maintenance interval. Synthetic seconds cannot be reported as
human calibration time.

**Data and controls:** One future approved fresh participant with three
physically distinct, row-disjoint, and semantic-text-disjoint recordings:
at least 32 calibration, 16 selection, and 48 final unique completed sentences.
Compare frozen zero-shot, exact-identity adapter, selected mode adapter,
source-train-only no-signal prior, robust normalization-only, and same-budget
label derangement where labels are used. S25 block 2 remains Loop 28 final-only
and is ineligible.

**Metrics:** macro sentence CER gain versus zero-shot and prior; gain per item,
active second, total minute, and label; 65,535 random sign assignments plus the
observed assignment; practical margins; no-harm items and wins/ties/losses;
selection-to-final generalization; human burden; runtime, RSS, bytes, updates,
warnings, unavailable fields, and hashes.

**Gate:** Hash-freeze strict zero-shot final predictions before any target-
person calibration access. Freeze exactly one mode, adapter, and budget before
adapted final predictions. Open final targets once. The future recommendation
requires at least `0.05` macro-CER gain versus both zero-shot and prior, the
paired one-sided `p <= 0.05` gates, and strict wins over every applicable
control; the margins remain unfrozen until preregistration. Any tie, final harm,
split/hash/access/resource failure, or selection-to-final reversal parks the
claim without restart.

**Dependencies and authorization:** Depends on compatible Loop 25 and 26
results, Loop 28's transfer taxonomy, Loop 31 for sensor-signal wording, and an
approved fresh-person protocol. Planning research only; the experiment remains
`Not Started`. No candidate or mode is selected, all protected operations are
unauthorized, and the future cap is one thread/worker, 32 target-trainable
values, 1,200 adapter-fit seconds, 1 GiB RSS, 32 MiB artifacts, and zero new
data/model downloads before separate authorization.

## Loop 33 - Data Scaling And Sample Efficiency

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop33_research_boundary.v0.json`. Every one of 23 authorization
flags is false; no protected cache, signal, target, model, training, score,
physical-repetition study, or acquisition exists.

**Core question:** Within the existing 55 source-train sentence instances,
does additional unique training data improve one fixed tiny causal encoder,
and is its observed upper boundary still improving enough to justify a
separate future acquisition decision?

**Why it moves the goal:** A prospective bounded curve can guide whether a
metadata-only acquisition packet is worth preparing without guessing,
reopening consumed evidence, or transferring Brain2Qwerty v2's 90-hour slope.

**Build:** After separate authorization, run strictly nested
`8, 16, 24, 32, 44, 55` unique-sentence prefixes with at most three fresh
optimization seeds and 18 candidate fits. Keep the 2,908-parameter architecture,
person, session, device, channels, sampling rate, optimizer, stopping, decode
rule, validation membership, and metric code fixed.

**Research:** Completed. The primary sources separate recording quantity from
sentence variety and show why a tiny one-person curve cannot inherit an
exponent from 90-hour typed-sentence MEG, 175-hour overt-speech EEG, or
multi-dataset image decoding. Formal power-law extrapolation is refused.

**Data and controls:** Future execution may use only separately authorized 55
source-train and six reserved validation rows. Fit a train-size-matched,
train-only no-signal prior at each prefix. Hash-freeze every Loop 26/31/33
prediction before opening all six validation targets once. Source test,
session 2, S7, S20, S25, and new data remain closed. Duplicated, reweighted, or
augmented arrays are not physical repetitions; an eligible repeated-acquisition
lane would require distinct performed recordings and separate authorization.

**Metrics:** Macro sentence CER by item, seed, size, and matched prior;
descriptive slope versus `log2(unique sentences)`; every adjacent delta;
smallest-band to upper-band and upper-band-over-prior practical gains; unique
sentences, physical trials, valid signal seconds or minutes, bytes, runtime,
RSS, warnings, unavailable fields, access counters, and hashes. CPU time is not
energy.

**Gate:** A future bounded curve needs all 20 gates, target-blind access order,
negative slopes for every registered seed, the recommended `0.05` practical
smallest-to-upper and upper-over-prior gains, and Loop 31 attribution before
sensor-signal wording. Report only the observed 8-55 range. A clean upper-bound
result may justify a separate metadata-only acquisition packet, not a download.

**Dependencies and authorization:** Depends on Loops 26 and 31. Loop 33 should
be preregistered with Loop 26 before the first validation-target open. The
future envelope remains one thread/worker, 18 candidate fits, 1,200 seconds
total training, 1 GiB RSS, 32 MiB artifacts, and zero new downloads. Planning
does not authorize any protected read, model run, training, scoring, or
acquisition.

## Loop 34 - Confidence, Abstention, And Revision

**Current state:** Planning research complete; experiment `Not Started` and
confidence unavailable. See `docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop34_research_boundary.v0.json`. Every one of 26 authorization
flags is false; no fixture, feature, probability mapping, threshold, target
open, score, product confidence, or real-data operation exists.

**Core question:** Can a target-blind score rank sequence errors, support a
preregistered abstention rule on an independent partition, and keep revision
stability separate from calibrated correctness?

**Why it moves the goal:** Reliable refusal is more useful than fluent output
whose error risk is unknown.

**Build:** After separate authorization, implement seven noninterchangeable
confidence semantics, eight score/control roles, full registered working-point
and generalized-risk reporting, a bounded-loss selective policy, revision-
latency accounting, and an explicit `unavailable` state.

**Research:** Completed. Primary sources distinguish raw ranking from
correctness probability, selective operating points, conformal bounded-risk
control, revision stability, and product-visible confidence. ECE is secondary
and bin-sensitive; legacy AURC cannot be the only selective metric.

**Data and controls:** Recommend a fresh target-free synthetic lane with
`128/64/256` calibration/selection/final sequences grouped by independent
generation block and schedule. Compare normalized log score, entropy, margin,
stability, train-only prior, fixed-random, always-predict, and post-hoc oracle
roles. Select one score and policy on selection only; freeze all mappings,
thresholds, predictions, and hashes before one final-target open. The oracle is
never deployable.

**Metrics:** Exact-sequence 0/1 error as primary bounded loss; raw CER and
separately named bounded CER; full risk-coverage table; accepted and
generalized error at registered coverage; legacy AURC with limitations;
AUGRC-equivalent area; abstention; Brier/log loss/reliability only for
calibrated probabilities; revisions and first-output/stability/finalization/
added-delay times in Loop 30 clock domains.

**Gate:** A future synthetic claim needs all 20 gates, disjoint groups, target-
blind generation, one selected score and policy, one final open, ranking above
prior/random controls, useful minimum coverage, bounded conformal loss, named
dependence assumptions, and complete access/resource/hash ledgers. Otherwise
confidence remains unavailable. A synthetic pass cannot establish real
confidence.

**Dependencies and authorization:** Depends on Loops 30 and 31. The six real
source-validation rows stay reserved for the shared Loop 26/31/33 event and
cannot fit and independently qualify Loop 34. A real claim needs fresh physical
calibration, selection, and final evidence. Future synthetic work remains one
thread/worker, zero decoder training, at most six scalar mapping fits, 120
seconds, 1 GiB RSS, 16 MiB artifacts, and zero downloads. Planning research is
not authorization.

## Loop 35 - Peripheral Confound Firewall

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop35_research_boundary.v0.json`. Every one of 31 authorization
fields is false.

**Core question:** Does a candidate add predictive information beyond every
recorded timing and peripheral control, or can key timing, prompt/target
leakage, ocular activity, distal/proximal muscle, motion, audio/environment,
physiology, equipment, or task identity explain the result?

**Why it moves the goal:** Brain2Qwerty v1 decodes 500 ms windows centered on
known keypresses during physical typing. Brain2Qwerty v2 removes explicit
keypress timing at inference but still studies overt prompted typing with
audio, visual, motor, and somatosensory context. MEG and EEG literature shows
that small eye movements, EMG, head/jaw motion, and other task-linked artifacts
can be strongly predictive. A positive sensor score alone is not an origin
claim.

**Build recommendation:** Freeze ten confound classes, nine typed synchronized
streams, and 13 conditions: no-signal, timing-only, two direct-leak sentinels,
ocular-only, distal-muscle-only, proximal-muscle-only, motion-only,
audio/environment-only, combined-peripheral, brain-sensor-only, train-only
residualized brain-sensor, and all-stream. Missing controls remain unavailable;
they may not be represented as zero, clean, or synthetic real controls.

**Staged evidence:** Stage A is a target-free synthetic interface test with no
biological claim. Stage B is a separately consented and authorized fresh
multimodal local protocol with synchronized brain sensors, keyboard timing,
prompt events, EOG/gaze, distal and proximal EMG/kinematics, motion/geometry,
audio/environment, and physiology/equipment streams. Stage C is a separate
ethics, task, population, and model program for no-keypress, attempted-movement,
or patient evidence. No stage authorizes the next.

**Partition and statistics recommendation:** Require disjoint performed-row and
semantic-text identities with floors of 32 calibration, 16 selection, and 48
final sentences. Select the strongest peripheral comparator and one brain
candidate on selection only, hash-freeze every prediction and ledger, then
open final targets once. The primary estimand is all-stream macro sentence-CER
gain over the strongest peripheral condition; the secondary estimand compares
brain-sensor-only with the strongest nonbrain condition. Recommend a 0.05
practical margin for each, 65,535 paired random sign assignments plus observed,
and intersection-union success. Ties fail; one person cannot support population
inference.

**Claim boundary:** Current S21 has 102 MEG magnetometers and trigger timing but
no synchronized EOG, EMG, gaze, motion, or audio in the committed cache path.
S7's source named three ocular channels, but its consumed 61-channel cache
contains none. These facts can support future timing audits after separate
authorization, not a complete peripheral firewall. The maximum future local
claim is incremental brain-sensor information beyond recorded controls for the
exact people, task, device, streams, and split. Absolute brain origin,
language-intent decoding, no-keypress transfer, patient benefit, real-time
behavior, portable hardware, and clinical use remain unavailable.

**Dependencies and authorization:** Loop 31 must first establish sensor-signal
dependence. Stage A, Stage B acquisition/access, and Stage C each require their
own preregistration, exact authorization-only record, tested commit, push, and
green CI. Stage B additionally requires ethics/consent, retention, device/file/
byte caps, synchronization, privacy, and anomaly packets. Current planning
authorizes none of them.

## Loop 36 - Geometry And Reference Harmonization

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop36_research_boundary.v0.json`. All 29 authorization fields are
false.

**Core question:** Can source/channel identities, signal and coordinate units,
sensor/electrode geometry, directional transforms, reference state,
compensation, interpolation, and missingness be preserved and compared without
guessing or selecting a mapping by accuracy?

**Why it moves the goal:** The same channel label can refer to a different
physical sensor, reference, frame, or derived signal; the same physical sensor
can have different names, order, units, and frames. A hidden mapping can
manufacture transfer, while exact-name refusal alone prevents legitimate
declared comparisons.

**Build recommendation:** Use six independent representation layers and five
modality profiles. A 24-field future channel record preserves source and
canonical identities, type/status, signal units, sensor/electrode role,
position/orientation masks, coordinate units and frames, coil/electrode type,
reference/ground, compensation/projectors, transform-chain IDs, missingness,
and source hashes.

**Operation boundary:** Twelve operation classes separate exact reorder,
explicit bijective aliases, coordinate-unit scaling, signal-unit scaling,
known rigid transforms, reflections/axis swaps, EEG rereference, MEG
compensation/projectors, bad-channel interpolation, sensor-to-template mapping,
zero-fill, and accuracy-selected mappings. Only exact reorder, declared
coordinate-unit conversion, and a known right-handed transform can preserve
metadata/geometry identity. Signal scaling, rereference, compensation, and
interpolation are data-changing operations.

**Future fixtures:** After separate preregistration and authorization, 16
target-free families cover exact roundtrip, safe permutation, duplicate and
ambiguous aliases, coordinate and signal units, unknown units, known rigid
transforms, wrong direction, reflection, missing orientation/frame/reference,
interpolation provenance, and evaluation-leakage refusal.

**Gate:** Pass all 22 requirements and 30 refusals. Require unique explicit
aliases, separate signal/coordinate units, named frame origin/axes/handedness,
directional 4-by-4 transforms, orthogonality and determinant `+1`, at most
`1e-9 m` synthetic inverse residual, orientation-without-translation, complete
reference/compensation state, original and harmonized metadata, hashes,
resources, warnings, access counters, and claim-level reporting. Unknown fields
remain unavailable.

**Current evidence:** S21 caches expose names, MNE types, positions in metres,
integer frame/unit codes, and coil types but no complete exchange-frame,
orientation, transform, or compensation ledger. Loop 11 is within-cache subset
selection, not cross-device equivalence. The consumed S7 61-channel cache has
no qualified measured electrode/reference contract. No real header or cache
was opened for this research.

**Dependencies and authorization:** Depends on Loop 29's modality matrix, Loop
30 for time-varying geometry clocks, and Loop 35 for motion-geometry confounds.
Stage A synthetic metadata, Stage B named real headers, and Stage C signal
transforms each need a separate preregistration, authorization-only tested
commit, push, and green CI. Future Stage A is one thread, 120 seconds, 1 GiB
RSS, 16 MiB artifacts, and zero downloads. The maximum future real-header
claim is declared metadata compatibility, not numerical compatibility, model
transfer, device equivalence, or scientific performance.

## Loop 37 - BIDS Derivative And Provenance Export

**Current state:** Planning research complete; experiment `Not Started`. See
`docs/LOOP_37_PRIMARY_SOURCE_RESEARCH.md` and
`registries/loop37_research_boundary.v0.json`. All 29 authorization fields are
false. No fixture, exporter, derivative tree, validator, payload copy, or
release exists.

**Core question:** Can caches, tokens, reports, and splits be exported as
inspectable derivatives without copying raw data or losing source identity?

**Why it moves the goal:** A standards-aware derivative lowers the barrier for
external reproduction while preserving local raw-data ownership.

**Research result:** Stable BIDS 1.11.1 requires `Name` and `BIDSVersion` in
every `dataset_description.json` and `GeneratedBy` in a derivative dataset.
`DatasetType: derivative` makes the envelope explicit. File-level `Sources`
identify direct inputs with BIDS URIs; deprecated relative paths and
`RawSources` do not meet the future contract. A named BIDS URI requires a
truthful `DatasetLinks` entry. Required source metadata propagates only while
it remains semantically valid after processing.

BIDS permits additional and non-compliant files inside derivative trees. A
valid envelope therefore cannot standardize NeuroToken NPZ caches, split
reports, report cards, or manifests that have no stable BIDS derivative suffix.
The maximum future Stage B claim is a validator-assessed standard envelope with
explicitly non-standard NeuroDecodeKit payloads, not a BIDS-compliant
NeuroToken derivative.

**Build after separate authorization:** Implement six layers:

1. dataset envelope: `dataset_description.json`, UTF-8 `README`, BIDS version,
   derivative type, pipeline identity, and truthful source dataset links;
2. identity tree: portable, collision-safe subject/session/task/run/split/item
   paths with no direct identifiers;
3. standard metadata: only stable BIDS fields such as `Description`,
   `Sources`, relevant source entities, `desc`, and still-valid required
   metadata;
4. NeuroDecodeKit extension metadata: an explicit non-standard versioned
   object/file for schema, hashes, timing, masks, geometry, causality,
   resources, warnings, and claim boundaries;
5. payload/hash manifest: every allowlisted file, byte count, SHA-256, source
   relation, duplicate status, and standardization status;
6. audit/release ledger: raw-copy, path, redaction, privacy, license, validator,
   resource, access, and claim checks.

Five artifact profiles keep NeuroToken caches, signal/sentence caches, split
protocols, report cards, and the standard dataset envelope separate. Fifteen
stable-field mappings and 16 explicit NeuroDecodeKit extension fields are
frozen. Proposed BIDS provenance fields are not treated as stable 1.11.1
requirements.

**Data and controls:** Future Stage A may use only target-free synthetic
metadata/refusal fixtures. Twenty fixture families cover valid standalone and
nested trees plus missing dataset descriptions, malformed `GeneratedBy`,
pipeline mismatch, missing README, unresolved BIDS URIs, deprecated paths,
absolute-path/user leaks, traversal, case/subject collisions, raw-name/content
duplicates, symlink/hardlink aliases, overwrite, license failure, target/free-
text leakage, unknown payloads, and hash/roundtrip drift.

The exporter may never recursively copy a source tree. Known raw extensions,
raw-permissible filenames, sampled or full byte duplicates, shared inodes,
symlinks, hardlinks, aliases, targets, prompts, responses, and unrestricted
free text refuse. A source without a truthful resolvable BIDS URI keeps only an
opaque hash in the non-standard record and marks standard `Sources`
unavailable. Absolute paths, usernames, home directories, drive letters, and
`file://` URIs remain forbidden.

**Metrics:** standard/non-standard/required/propagated/omitted/unavailable
field counts; BIDS URI resolution; source/split/config/payload/code/manifest/
bundle hash coverage; path and identity roundtrip; input/output/duplicate/raw-
copy/generated bytes; files; validator errors/warnings/ignored files; runtime;
peak RSS; threads/workers; network; and all access counters.

**Four stages:** Stage A freezes dependency-free target-free synthetic
metadata/refusal behavior. Stage B adds one bounded synthetic payload and one
pinned optional offline validator. Stage C may inspect named local real-derived
metadata only after Loop 38 privacy, identifier, license, and lifecycle gates.
Stage D is a separate public-release decision after Loops 38, 39, and 44.
Authorization of one stage never authorizes another.

**Gate:** Future Stage A passes only if all 24 gates and 32 refusals are exact,
paths and identities roundtrip, targets/local paths are absent, every output is
hashed, raw-copy counts remain zero, and two clean output roots are identical.
Stage B additionally preserves every issue from pinned validator `2.4.1`. A
validator success cannot establish custom-payload standardization, source-hash
truth, privacy, license, scientific provenance, reproducibility, or decoding.

**Stop rule:** Publish `invalid`, `unavailable`, `non-standard`, or `blocked`
on any source URI, metadata validity, path, collision, raw-copy, target, hash,
privacy, license, validator, resource, access, or claim failure. Never invent
metadata, auto-repair a failed tree, weaken gates, hide issues, or rerun until
a passing variant appears.

**Dependencies and authorization:** Depends on Loop 36 planning. Loop 38 is
required before real/public metadata export, Loop 39 before cross-machine
reproducibility, and Loop 44 before release wording. Stage A is capped at one
thread/worker, 120 seconds, 1 GiB RSS, 16 MiB, 128 files, zero network/download
bytes, zero raw-copy bytes, and no base dependency. Export code, fixtures,
validator install/run, protected reads, external writes, or release require an
exact separate Loop 37 authorization-only commit and green CI.

## Loop 38 - Neural Data Privacy And Lifecycle

**Core question:** Can the project prove where sensitive recordings and
embeddings live, who can access them, and how they are retained or deleted?

**Why it moves the goal:** Neural signals and embeddings can expose identity;
local-first behavior needs a verifiable lifecycle, not only a README promise.

**Planning result:** Research is complete while the experiment remains `Not
Started` and unauthorized. The future interface freezes five sensitivity
levels, eight artifact classes, ten lifecycle surfaces, 12 sensitive-field
classes, 12 threat scenarios, five deletion-receipt levels, and four separately
authorized stages. Pseudonyms, stable hashes, embeddings, and de-identified
neural payloads remain potentially linkable.

**Build after separate authorization:** Create a target-free synthetic data
inventory, sensitivity labels, approved local roots, retention policy,
redaction scanner, and narrow deletion receipts. Keep raw, derived, report,
log, temporary, backup/sync, Git/LFS/history, remote clone/PR, CI, and release
copies separate.

**Research:** The stable pin is NIST Privacy Framework 1.0 because 1.1 remains
an initial public draft. NISTIR 8062 contributes predictability,
manageability, and disassociability; PRAM structures the risk analysis; SP
800-88 Rev. 2 separates application path receipts from media sanitization.
GitHub history guidance, Open Brain Consent, EEG identity research, and OECD
neurotechnology stewardship define clone, consent, identity, and anti-hype
boundaries.

**Data and controls:** This research used repository metadata and public sources
only. A future Stage A is target-free synthetic fixtures only. Test absolute
paths, aliases, timestamps, serials, secrets, consent/IRB IDs, targets/free
text, rare rows, stable hashes, neural-derived suffixes, temporary files,
backups, aliases, tracked history, force-add, clones, and CI copies. Do not run
a real identity attack or touch a protected root.

**Metrics:** artifact and lifecycle coverage; fixture redaction recall and
public precision; policy violations; current and all-ref tracked neural paths
and bytes; receipt level; deleted/skipped/failed/unresolved copies; runtime,
RSS, bytes, files, threads, workers, network, and mutation counts.

**Gate:** Every artifact class needs an owner, sensitivity, location, retention,
redaction, sharing, and deletion policy. Every copy surface is checked, blocked,
unavailable, or unresolved. Prohibited survivor bytes and tracked neural
payloads are zero. Unknown copies remain unresolved. Block anonymity,
privacy-safe, secure-deletion, sharing, and release claims when consent,
license, lifecycle, receipt level, or media evidence is unclear.

**Dependencies and authorization:** Depends on Loop 37. Stage A synthetic,
Stage B read-only local metadata, Stage C named real-derived lifecycle, and
Stage D release are independent decisions. Loop 39 is required for cross-
machine copy claims, Loop 42 for device lifecycle, and Loop 44 plus external
governance for release. No fixture, scanner, deletion, protected-root scan,
identity attack, history rewrite, remote cleanup, consent/legal determination,
release/upload, model, training, stream, device, or hardware work is authorized.

**Resources:** Current generated experiment bytes are zero. Future Stage A is
standard-library-first, one thread/worker, 120 seconds, 512 MiB RSS, 8 MiB
reports, 128 files, zero network/download/upload bytes, zero real signal reads,
and zero nonfixture destructive mutations.

## Loop 39 - Cross-Machine Reproducibility Matrix

**Core question:** Which outputs are bitwise stable across supported Python and
OS combinations, and which require explicit numerical tolerances?

**Why it moves the goal:** Contributors need to distinguish a semantic
regression from expected backend arithmetic or an unsupported environment.
Later edge, live, device, independent-reproduction, and release claims are not
credible when one maintainer's environment is the hidden reference.

**Build:** Future separately authorized work adds a sanitized environment
manifest, canonical semantic comparator, six-cell CI matrix, golden semantic
hashes, field-specific tolerance registry, stable diagnostic diff, and per-cell
resource report. No implementation or workflow mutation exists now.

**Research:** Planning research is complete. ACM terminology separates
same-team repeatability, different-team same-setup reproduction, and different-
team different-setup replication. Reproducible Builds requires same source,
environment, and instructions for bit-identical specified artifacts. Python,
pip, PyPA, NumPy, PyTorch, GitHub runner, MNE, and Scientific Python sources
define the environment and numerical boundaries.

**Current audit:** `pyproject.toml` declares Python 3.10-3.12 and OS Independent,
but public CI currently exercises only `ubuntu-latest` with Python 3.12 for base
and optional-neuro profiles. There is no cross-OS cell, dependency lock,
environment-manifest schema, central tolerance registry, or wheel/sdist
reproducibility job. Two tests import standard-library `tomllib`, unavailable
in Python 3.10 without a fallback, so the declared minimum remains unqualified.
This local Darwin arm64 Python 3.13.5 pass is diagnostic only.

**Future matrix:** Six required cells are Ubuntu 24.04 x64 with Python
3.10/3.11/3.12 base; macOS 15 arm64 with Python 3.12 base; and Ubuntu 24.04 plus
macOS 15 with Python 3.12 optional-neuro. Windows, GPU, Python 3.13+, edge,
stream, device, and hardware cells remain separate.

**Data and controls:** Repository metadata and public sources only now. Future
Stage A uses new target-free dependency-free synthetic fixtures. Eighteen
environment fields bind source/workflow, runner image, OS/CPU, Python ABI,
dependency graph, BLAS/LAPACK, SIMD, Torch/MNE, threads, locale, paths, and
resources. Exact IDs, timestamps, indices, lengths, masks, splits, causal
state, dtypes, shapes, discrete values, and warning codes never receive float
tolerances.

**Comparisons:** Eight output classes and six comparison classes separate
canonical semantic hashes, discrete arrays, floating arrays, containers,
human reports, resources, and failures. Every floating field requires a frozen
maximum absolute, maximum relative, ULP, NaN/Inf, signed-zero, dtype, and shape
policy. There is no global `allclose` threshold. Runtime and RSS are descriptive
unless a registered resource cap fails.

**Metrics:** required-cell outcome; semantic-hash and discrete identity;
field-level numerical drift; install/test/comparison runtime and RSS;
dependency, package, and artifact bytes; unavailable fields; unsupported reason;
and claim ceiling.

**Gate:** All 28 future gates and 38 refusals pass. Every required cell either
reproduces exact semantics plus its preregistered numerical policy or emits one
explicit unsupported reason. Matrix fail-fast is false, silent continue-on-
error is forbidden, and Python 3.10 must collect the complete suite or the
support claim fails. A tolerance can change only under a new version after a
public failure record and before fresh evidence, never after protected or
consumed result access.

**Stop rule:** One failing required cell blocks the corresponding claim. Never
convert one host, one OS, matching rounded metrics, a dependency range, or an
editable-install pass into cross-machine reproduction. Preserve and diagnose
the failure instead of excluding the cell or widening a threshold.

**Dependencies and authorization:** Depends on Loop 37 and Loop 38 planning.
Stages A fixture/manifest, B base matrix, C optional-neuro matrix, and D Loop 43
handoff are separately authorized. Loop 40 requires the relevant matrix pass;
Loop 43 remains required for independent-team reproduction; Loop 44 remains
required for release. No fixture, manifest implementation, CI job, lockfile,
install, build/upload, protected read, model, training, edge, stream, device,
or hardware operation is authorized.

**Resources:** Current generated experiment bytes, jobs, installs, builds, and
protected operations are zero. Future work is capped at two parallel jobs, one
thread/worker per cell, 20 minutes, 1 GiB RSS, 4 MiB artifacts per cell, 24 MiB
total artifacts, and zero large-cache/protected/model/training access.

## Loop 40 - Edge Runtime Packaging Gate

**Current status:** Planning research complete; experiment `Not Started` and
unauthorized. The machine boundary is
`registries/loop40_research_boundary.v0.json`, and the official-source decision
note is `docs/LOOP_40_PRIMARY_SOURCE_RESEARCH.md`.

**Core question:** Can one already qualified frozen pipeline be packaged for an
edge runtime while preserving outputs, state, timestamps, and resources?

**Why it moves the goal:** Edge packaging matters only after correctness and
local runtime gates; otherwise export complexity is deployment theater.

**Build:** A future separately authorized pass may select one named target and
backend, freeze its export/operator contract, validate the package against
eager reference behavior, and report startup, steady-state, memory planning,
delegation, fallback, and complete package/runtime/app bytes. No build exists.

**Research:** Official-source comparison covers ExecuTorch/XNNPACK, ONNX
Runtime Mobile, LiteRT, and Core ML. ExecuTorch/XNNPACK is the leading future
research candidate because the source is PyTorch and the stack exposes CPU
delegation, memory planning, profiling, and mobile integration. It is not
selected: the relevant Loop 39 matrix has not run, and no target OS,
architecture, ABI, minimum deployment target, or app envelope is frozen.

**Data and controls:** Current access is repository source, recorded Loop 24/39
evidence, and official public documentation only. Future data is one frozen
target-free synthetic fixture. Keep the retained 1,130-parameter,
5,210-byte float32 causal reference and seeds 2401/2402 closed. Separate six
layers: source reference, exported graph, numeric payload, runtime/kernels,
host normalization/state/timestamps/decoder, and app/device envelope.

**Metrics:** Exact semantics, state, timestamps, and provenance; field-specific
numerical drift; delegated/undelegated/fallback/unsupported operators; graph,
payload, runtime, kernel, app, temporary, and total bytes; startup, load, first
inference, warmup, steady state, and teardown; RSS and planned mutable,
constant, and scratch memory; explicit failures, warnings, and claim ceiling.

**Gate:** All 30 future gates and 40 refusals pass. Adopt only if the relevant
Loop 39 cells qualify the reference, one named target/backend preserves the
registered float32 outputs/state/timestamps/provenance, fallback is fully
visible, all resource caps hold, and a preregistered complete deployment
benefit passes. Model bytes alone are not a deployment benefit.

**Stop rule:** Park on missing prerequisites, unsupported export, hidden
fallback, post-hoc tolerance, dtype/quantization drift, retraining,
architecture/checkpoint changes, resource overflow, or no complete benefit.
Do not tune a failed candidate on the same fixture.

**Dependencies and authorization:** The Loop 24 hold is recorded, but its seeds
stay closed. The Loop 39 planning dependency exists while execution remains
unsatisfied. Stages A static eligibility, B local export/parity, C cross-machine
package matrix, and D simulator/app integration each need separate
preregistration and authorization. Loop 42 is required for physical-device
qualification and Loop 44 for release. No target/backend selection, fixture,
dependency install, export, conversion, package, inference, profiler, memory
planner, delegate, fallback, simulator, app, device, or hardware operation is
authorized.

**Resources:** Current generated experiment bytes and execution operations are
zero. Future work is capped at one backend, one thread, one worker, 60 seconds
per measurement worker, 1 GiB peak RSS, and 32 MiB generated package/report
bytes. Any dependency install needs a separate explicit byte cap.

## Loop 41 - RW3 Stream-To-NeuroToken Integration

**Current status:** Planning research complete; experiment `Not Started` and
unauthorized. Six integration layers, seven clock views, eight anomaly classes,
five inherited schedules, five resume cuts, 18 hash bindings, 28 future fixture
families, four stages, 32 gates, 42 refusals, and 42 false authorization fields
are frozen in `registries/loop41_research_boundary.v0.json`.

**Core question:** Can an authorized source-chunk replay pass through causal
preprocessing into NeuroTokenCache without timestamp, gap, state, or schedule
drift?

**Why it moves the goal:** This is the first honest join between acquisition
mechanics and the model interface, while remaining upstream of hardware and
decoding claims.

**Build:** Future only. Compose the RW3 source-chunk envelope, an authorized
Loop 25 causal preprocessor, the causal NeuroToken producer, NeuroTokenCache,
bounded serialized state, anomaly propagation, schedule/resume matrices, and
end-to-end provenance hashes. Decoder and render layers remain unavailable.

**Research:** Complete at the planning boundary. Source timestamps remain
immutable; corrected timestamps are derived, segmented, reversible, and hash-
bound. Arrival, preprocessing-ready, token-available, decoder-emission, and
render-presented time remain separate. Only clocks in a shared named monotonic
domain may be subtracted. Replay capture latency, decoder time, render time,
and end-to-end latency are unavailable.

**Data and controls:** Only future authorized target-free RW3 synthetic replay.
Compare canonical offline and every schedule; include gaps, duplicates,
reorder, reconnect, reset, and interrupted/resumed state. Keep clocks distinct.

**Metrics:** source/preprocessing/token hashes; timestamps/lengths; anomaly
propagation; state bytes; resume identity; scheduling and stage runtime; RSS;
output bytes.

**Gate:** After separately closed dependencies, preregistration, and
authorization, every schedule, anomaly, and resume path must preserve the
registered source, preprocessing, token, state, and provenance semantics under
the frozen numerical policy. Any silent interpolation/deduplication/reordering,
clock collapse, cross-gap token, schedule drift, resume mismatch, hidden
unavailable latency, or resource overflow parks the join.

**Dependencies and authorization:** Loop 20/21 interface evidence is available
but is not Loop 41 runtime evidence. Compatible Loop 25, Loop 37, Loop 39, and
RW3 Stage A execution closeouts are all unsatisfied. A future Loop 41
preregistration and exact authorization remain separate after those close.
This roadmap authorizes no seed, fixture, source chunk, clock correction,
preprocessing, adapter, state, schedule matrix, token runtime, protected read,
target, model, training, decoder, language model, server, browser, socket,
stream, SDK, device, hardware, generated payload, or latency claim.

**Resources:** Current generated experiment bytes and execution operations are
zero. Future work is capped at one thread, one worker, 60 seconds per worker,
1 GiB RSS, 4 KiB RW3 state, 64 KiB complete integration state, and 32 MiB total
generated fixtures/states/caches/reports with zero network, protected reads,
targets, model runs, and training runs.

## Loop 42 - One-Device Qualification

**Core question:** Can one named device preserve declared channels, units,
clocks, packets, and privacy from recorded replay through one bounded session?

**Why it moves the goal:** One measured device/firmware/host claim is more
credible than broad support inferred from an SDK import.

**Build:** Create a device descriptor, consent/locality checklist,
recorded-versus-live equivalence packet, packet-loss/reconnect stress report,
retention audit, and compatibility-level decision.

**Research:** Review device-specific timestamps, units, reference, geometry,
firmware, transports, cloud behavior, and data ownership from primary sources.

**Data and controls:** One separately approved board or headset. Start with SDK
synthetic/playback, then one consented local qualification session if approved.
Compare recorded/live paths and test loss, reconnect, clock reset, buffer drain,
and network-off behavior.

**Metrics:** channel/unit/rate/packet identity; offset/jitter/gaps/duplicates/
reorder; observed capture-to-arrival boundary; runtime/RSS/bytes/drops; privacy
and retention violations.

**Gate:** Qualify only the exact device, firmware, transport, host, and tested
compatibility level. Connectivity does not qualify signal quality, useful
neural signal, decoding, portability, or clinical use.

**Dependencies and authorization:** Depends on Loops 29, 38, and 41 plus exact
device, ethics, consent, retention, file, session, and byte authorization. No
SDK import, discovery, socket, board, or hardware is authorized now.

## Loop 43 - Independent Reproduction Challenge

**Core question:** Can an independent contributor reproduce a bounded claim
without private guidance or sharing neural recordings?

**Why it moves the goal:** An outside reproduction tests setup, contracts,
documentation, privacy, and evidence quality better than another maintainer run.

**Build:** Publish a challenge packet with tiny fixture manifest, environment
capture, expected semantic checks, optional blinded submission hash, result
card, and discrepancy triage.

**Research:** Distinguish exact replication, computational reproduction, and an
extension on contributor-owned data. Define what each outcome can claim.

**Data and controls:** Public code and tiny synthetic fixtures by default.
Contributors keep EEG local and may submit metadata/aggregate reports only.
Record independent environments and preserve failed/negative reproductions.

**Metrics:** semantic/numerical reproduction rate; setup time; command count;
environment completeness; discrepancy class; artifact bytes; privacy findings.

**Gate:** At least one independent environment must reproduce the registered
artifact contract, with discrepancies resolved or documented without moving
the claim boundary.

**Dependencies and authorization:** Depends on Loops 37-39 plus contributor and
challenge review. This roadmap does not authorize outreach, external data
exchange, or execution.

## Loop 44 - Claim Promotion And Release Decision

**Core question:** Which engineering and scientific claims have earned a
release, and which remain fixture-backed, negative, unavailable, parked, or
killed?

**Why it moves the goal:** A roadmap should end in an evidence decision, not a
pile of features and progressively softer language.

**Build:** Produce a machine-readable evidence matrix, model cards, dataset
cards, release checklist, claim diff, risk register, and explicit proceed,
park, or kill record.

**Research:** Apply model-card, datasheet, privacy, licensing, and
reproducibility principles to every public claim and intended use.

**Data and controls:** Artifact-only synthesis of closed reports. Every claim
must link to cohort, task, split, comparator, uncertainty, resource, access,
privacy, and license evidence. Preserve negative results and unavailable fields.

**Metrics:** promoted/parked/killed/unavailable claims; evidence completeness;
unresolved privacy/license/security/reproduction blockers; link integrity;
tests and CI.

**Gate:** Release only the supported subset. Engineering capability and
scientific performance stay in separate sentences. Clinical, arbitrary-
thought, portable-hardware, and real-time claims default to unestablished.

**Dependencies and authorization:** Depends on Loops 38, 39, and 43 plus a
maintainer release decision. It cannot retroactively authorize or upgrade an
earlier experiment.

## Cross-Loop Kill Branches

| Trigger | Required response |
|---|---|
| Loop 26 fails neural controls | Park real-model scaling; continue provenance, privacy, and contributor tooling only |
| No eligible Loop 27 holdout | Hold Loops 28 and 32; do not reuse session-2 or S7 |
| Loop 31 finds a shortcut | Block neural claim; prioritize Loop 35 and split/confound repair |
| Loop 34 confidence does not rank errors | Keep confidence unavailable in the UI and reports |
| Loop 39 cannot reproduce semantic identity | Block edge packaging and external challenge until diagnosed |
| Loop 41 loses timestamps/state/anomalies | Block live and device work |
| Loop 42 fails locality or timing | Park that exact device; do not generalize to another board |
| Loop 43 depends on private maintainer state | Hold claim promotion and repair reproducibility |

## Required Closeout For Every Loop

Every closeout must report:

- exact inputs, outputs, hashes, and generated bytes;
- runtime, peak RSS, thread/worker count, and host/dependency versions;
- raw, real-cache, consumed-cache, target, model, training, network, stream,
  and device access counters;
- split, participant, session, task, modality, and device identity where
  applicable;
- no-signal and shortcut controls for every predictive result;
- every warning and unavailable field;
- causal/right-context status and whether end-to-end latency was measured;
- the exact engineering capability added;
- the exact scientific or decoding claim not established;
- proceed, park, or kill with the next authorization boundary.

## Current Decision

Loops 25-44 are detailed and ready for review as a future work queue. They are
not approved experiments. The current numbered execution gate is Loop 24 under
its separate target-free authorization; that decision does not change any of
the 20 false roadmap flags. The next practice-track decision remains the
separately unauthorized RW3 Stage A.
