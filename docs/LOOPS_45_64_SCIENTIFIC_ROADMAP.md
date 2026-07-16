# Loops 45-64: Scientific Evidence Roadmap

Machine source of truth: `registries/next_scientific_loops.v0.json`

Status: **Loop 45 mechanics complete; every experiment in Loops 46-64 and every
download, model, participant, device, and release action remain separately
unauthorized**

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

Stage C planning research now selects `R1` temporal-context starvation as the
next falsifiable repair hypothesis. It freezes a 7,692-parameter causal
candidate with 470 ms left context against a 7,568-parameter zero-context
ablation on the same 25 Hz output grid. The next gate is synthetic mechanics
only: seed 4850, 40 rows, a 24/8/8 split, three candidate recipes, one ablation
fit, at most 1,800 optimizer steps, 600 seconds, 1 GiB peak RSS, 16 MiB output,
one thread, one worker, and zero real-data downloads. See
`docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md` and
`registries/loop48_stage_c_representation_repair_research.v0.json`. No
protected Stage C preregistration or execution exists, and synthetic success
cannot establish neural information or decoding improvement.

The exact candidate, ablation, deterministic fixture, numeric checkpoints,
bounded aggregate gate, and inspect CLI are now implemented in
`docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md` and
`registries/loop48_stage_c_synthetic_implementation.v0.json`. Local
qualification passes 13 focused tests with zero parameter updates. The
four-fit synthetic calibration remains unexecuted until the implementation
commit is pushed and remotely green.

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

Acquire only the exact previously selected S20 BrainVision/log bundle after an
explicit dry-run and `--execute` decision. Storage capacity alone is not
permission. S7 remains consumed and excluded from selection.

### Loop 54 - EEG Trial Geometry And Confound Ledger

Reconcile at least 48 trials; record channels, units, geometry, reference,
sampling, missing/bad channels, EOG/EMG/motion availability, keypress timing,
and target-isolation order. Missing peripheral controls cap later claims.

### Loop 55 - Fresh EEG Neural-Effect Gate

Test one tiny causal and one linear EEG model against a train-only prior, zero
signal, time displacement, channel derangement, keypress-timing-only, and all
available peripheral controls. Do not borrow MEG thresholds or claims.

### Loop 56 - Cross-Modality Accessibility Verdict

Compare the exact engineering and scientific requirements that survive between
cryogenic MEG and scalp EEG. Never pool scores, equate channels, or call shared
software shared performance.

## Phase P9 - Causal Local Use (Loops 57-60)

### Loop 57 - Train-Stream Causal Parity

Join qualified causal preprocessing, the frozen encoder, NeuroToken state,
decoder state, timestamps, schedules, resumes, and anomalies. Target-free
fixtures precede any authorized neural replay.

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
Loops 49-64 remain `Not Started`. Every current
`execution_authorized` flag and every global authorization field is false. The
roadmap does not authorize a Loop 45 rerun, Loop 46/47 rerun, Loop 48 protected
rerun, real-data representation-repair training, any new real-data read or
download, target opening, S24/S25 access, EEG acquisition, stream, device,
participant contact, home recording, external outreach, tag, release, archive,
DOI, or scientific claim.
