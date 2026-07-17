# Loop 55 Primary-Source Research: Fresh EEG Neural-Effect Gate

Date: 2026-07-16

Status: **planning research complete; Loop 54 dependent; experiment `Not Started`;
unauthorized**

Machine boundary:
`registries/loop55_eeg_neural_effect_research.v0.json`

Additive AI research boundary, 2026-07-17:
`docs/LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md` and
`registries/loop55_ai_research_policy.v0.json` now define a synthetic-only,
dependency-free proposal guard. It permits AI to emit bounded recipe manifests
and protocol criticism, but it grants no S20 access, split, target, model,
training, inference, scoring, or claim authority. The real experiment remains
Loop 54 dependent, `Not Started`, and separately unauthorized.

## Decision

Do not treat the future S20 block as a miniature reproduction of the published
Brain2Qwerty headline. The available task is overt typing with known keypress
times, one participant, one session, and at most one newly qualified block. A
clean experiment can ask whether EEG values immediately before an observed
keypress improve prediction of the performed motor action. It cannot ask
whether arbitrary thoughts can be decoded, whether keypresses can be found in
a continuous stream, or whether the result transfers to another person,
session, device, patient, or home environment.

Loop 55 therefore needs two prospectively ordered endpoints from the same
frozen final trials and the same compact model:

1. **causal hand endpoint:** does pre-keypress EEG improve left-versus-right
   hand prediction over every applicable no-signal, timing, corruption, and
   peripheral control? This is the higher-power motor-effect gate;
2. **causal key endpoint:** does the same pre-keypress EEG improve 29-class
   performed-key prediction, aggregated as macro trial keypress-aligned CER,
   over the same controls? This is the harder key-level decoding gate.

The model must predict performed keys, not corrected intended text, as its
primary target. Intended sentence text may be reported only as a separately
identified secondary target after all primary predictions are frozen. It may
never create features, choose a model, choose a checkpoint, or upgrade a hand
effect into a key-decoding claim.

The published `[-200, +300] ms` keypress-centered window is retained only as a
diagnostic noncausal positive control. The primary candidate must use signal
strictly before the keypress, recommended as `[-500, 0) ms`, with zero right
context and causal preprocessing. If only the centered-window diagnostic
passes, the result is task-aligned or post-keypress sensor information, not a
causal decoding result.

This pass is planning research. It creates no split, opens no S20 file, reads
no target, implements no model, and authorizes no experiment.

## Current Proof Boundary

What is proven now:

- Loop 53 prospectively identifies exactly four S20 session-2 block-2 files,
  but acquisition remains separately unauthorized;
- Loop 54 defines a target-isolated VHDR, EEG, VMRK, and MAT qualification
  sequence, a 48-unique-trial floor, and a complete recorded-confound ledger;
- Loop 31 defines matched no-signal and signal-corruption controls plus a
  conjunctive all-controls decision rule;
- Loop 35 defines why ocular, muscular, motion, environmental, timing, and
  task-context information must not be relabeled as brain-specific evidence;
- Loop 48 shows that the existing tiny causal model family failed on S21 and
  that a synthetic representation repair missed its absolute gates; and
- this pass compares those local boundaries with six primary research sources.

What is not proven now:

- no S20 payload has been acquired, stated, hashed, parsed, or opened;
- no S20 channel, sample, event, performed key, intended sentence, or usable
  trial count is known from file content;
- no train, selection, or final identity exists;
- no EEG transform, model, checkpoint, prediction, training run, score, or
  latency measurement exists; and
- there is no neural advantage, key-decoding accuracy, brain-specific origin,
  generalization, real-time operation, portable-hardware result, home result,
  or clinical evidence.

## Primary-Source Findings

### 1. The published EEG task is overt and keypress aligned

The Brain2Qwerty paper reports 61 EEG and three ocular channels sampled at
1 kHz. Its decoder receives 500 ms windows from 200 ms before to 300 ms after
each known keypress. Linear hand and character classification peak around
40 ms after the keypress, where motor execution and somatosensory feedback
converge. The paper also states that the current method is not real time and
depends on known keystroke onsets.

Source: [Noninvasive decoding of typed sentences from human brain
activity](https://www.nature.com/articles/s41593-026-02303-2)

Decision: a centered window is scientifically useful but noncausal for this
project's real-time direction. It cannot be the primary Loop 55 evidence.
Known event count and timing must be disclosed as task scaffolding.

### 2. Performed and intended keys are different estimands

The same paper aligns what the participant pressed with what should have been
pressed and usually trains on the intended target. It reports that typing
errors have different interkey timing and are decoded less well. The protocol
cannot definitively separate execution precision from cognitive intent.

Source: [Brain2Qwerty text preprocessing and typing-error
analysis](https://www.nature.com/articles/s41593-026-02303-2)

Decision: the primary Loop 55 label is the performed key because the physical
action generated the keypress-aligned motor and peripheral signal. Corrected
intended text is a distinct secondary question. A model that predicts the
intended sentence may be helped by memorized language structure even when it
does not identify the performed action.

### 3. Compact EEG-specific spatial and temporal models are reasonable

EEGNet introduced depthwise and separable convolutions as a compact way to
learn temporal and spatial EEG features across multiple BCI paradigms,
including movement-related cortical potentials. The paper emphasizes compact
parameterization and limited-data use, not universal superiority.

Source: [EEGNet: A Compact Convolutional Network for EEG-based
Brain-Computer Interfaces](https://arxiv.org/abs/1611.08024)

Decision: the future primary model should be one fixed compact causal
spatiotemporal family under 10,000 trainable parameters, with a shared encoder
and separate key and hand heads. EEGNet is architectural precedent, not a
license to grid-search a larger family or claim that a compact CNN is already
validated for S20.

### 4. A control must use the same analysis path

The Same Analysis Approach recommends applying the main analysis to design
variables, simulated confounds, null data, and control data. This catches
unexpected interactions between the experimental design, cross-validation,
and the decoder.

Source: [The Same Analysis
Approach](https://arxiv.org/abs/1703.06670)

Decision: exact-zero, whole-trial derangement, channel derangement, time
displacement, timing-only, train-pairing derangement, and available peripheral
conditions use the same partition, target normalization, metric code, and
prediction-freeze protocol. A control that quietly changes the unit of
analysis or compute budget is not matched evidence.

### 5. Permutation evidence tests a defined exchangeability claim

Ojala and Garriga distinguish label permutations, which test whether a
classifier found class structure, from restricted feature permutations, which
probe whether feature dependencies carry information.

Source: [Permutation Tests for Studying Classifier
Performance](https://www.jmlr.org/papers/v11/ojala10a.html)

Decision: Loop 55 will use an exact paired sign-flip test over final-trial
error differences. It will not permute keypress windows as if thousands of
events were independent biological replicates. Corruption controls answer
separate falsification questions and cannot be described as perfect neural
nulls.

### 6. Small predictive samples require an explicit uncertainty ceiling

Varoquaux shows that cross-validation error can have large uncertainty in
small neuroimaging samples and that variation across folds underestimates the
true error. More event windows do not create more independent trials or more
participants.

Source: [Cross-validation failure: Small sample sizes lead to large error
bars](https://pubmed.ncbi.nlm.nih.gov/28655633/)

Decision: the performed trial is the inference unit, macro metrics weight
trials equally, all final-trial effects are reported, and biological replicate
count remains one. A positive local effect cannot support population
inference.

## Scientific Question And Estimands

### Endpoint E1: causal hand effect

For each final trial, calculate hand error rate from the frozen candidate and
each comparator. The primary hand estimand is:

```text
mean_i(HER_strongest_no_signal_i - HER_causal_EEG_i)
```

Positive values favor EEG. A future preregistration should require:

- at least `0.03` absolute mean macro-trial HER improvement over the strongest
  train-only no-signal comparator;
- exact one-sided paired sign-flip `p <= 0.05` against that comparator; and
- a strict candidate win with exact one-sided paired `p <= 0.05` against every
  other applicable required control.

Passing E1 establishes at most a bounded pre-keypress EEG sensor-signal effect
for left-versus-right performed-hand prediction in this one block.

### Endpoint E2: causal performed-key effect

The model emits exactly one of 29 registered key classes for each known
keypress. Within a trial the predicted sequence length therefore equals the
observed event count. The primary key metric is called **keypress-aligned CER**
to expose that insertions, deletions, and event detection are not tested.

The primary key estimand is:

```text
mean_i(CER_strongest_no_signal_i - CER_causal_EEG_i)
```

A future preregistration should require:

- at least `0.05` absolute mean macro-trial keypress-aligned CER improvement
  over the strongest train-only no-signal comparator;
- exact one-sided paired sign-flip `p <= 0.05` against that comparator; and
- a strict candidate win with exact one-sided paired `p <= 0.05` against every
  other applicable required control.

Passing E2 establishes at most bounded key-level sensor-signal dependence for
the exact S20 task and block. It is not continuous text decoding because event
onsets and output count are supplied.

### Ordered interpretation

E1 and E2 are both frozen before final targets open. They are not
interchangeable endpoints selected after seeing the result:

| E1 hand | E2 key | Interpretation |
|---:|---:|---|
| fail | fail | no detected causal EEG sensor-signal advantage |
| pass | fail | bounded causal performed-hand sensor effect only |
| fail | pass | internally inconsistent; audit before any claim |
| pass | pass | bounded causal performed-key sensor effect, still not brain-specific |

The noncausal centered-window diagnostic never rescues either causal endpoint.

## Hypothesis Portfolio

The future one-shot result should route among these coexisting explanations:

| ID | Hypothesis | Discriminating observation |
|---|---|---|
| `L55-H0` | no usable EEG advantage | causal candidate does not clear strongest no-signal and controls |
| `L55-H1` | pre-keypress EEG carries performed-action information | causal E1 and/or E2 clears the complete matched-control conjunction |
| `L55-H2` | useful information is post-keypress or feedback locked | centered diagnostic passes while causal endpoint fails |
| `L55-H3` | ocular or other peripheral activity explains prediction | peripheral-only control matches or beats EEG, or required control is unavailable |
| `L55-H4` | event count, position, or timing explains prediction | timing-only or no-signal comparator matches or beats EEG |
| `L55-H5` | the fixed compact representation is insufficient | linear comparator passes while compact candidate fails, or both remain stable but negative |
| `L55-H6` | target, marker, or split leakage invalidates the run | any semantic marker, key identity, target text, or final target enters a forbidden stage |

Several hypotheses can be discriminated with one frozen final event. That is
more efficient than rerunning the block after each explanation is considered,
and it avoids post-target architecture search.

## Future Target And Feature Firewall

### Allowed primary model inputs

- EEG channels qualified by Loop 54 and explicitly classified as candidate
  brain-sensor channels;
- samples strictly before each known keypress;
- source channel order and train-only normalization parameters; and
- padding masks needed for a fixed tensor shape.

### Forbidden primary model inputs

- marker type or description;
- keycode, performed key, hand label, or intended key in any input field;
- target or typed sentence text;
- prompt identity, canonical sentence ID, semantic group, or split hash with
  label meaning;
- future signal samples at or after the keypress;
- EOG, EMG, gaze, motion, audio, or timing fields in the EEG-only candidate;
- pretrained language models, character language models, autocomplete, or
  target-derived embeddings; and
- participant, session, or block identifiers that vary with target class.

Known keypress onset and event count are allowed only as alignment scaffolding,
not as hidden evidence. Their complete predictive contribution is measured by
the timing-only comparator.

### Primary and secondary targets

- `performed_key_29`: primary key label;
- `performed_hand_2`: primary hand label derived deterministically from the
  performed key under a preregistered keyboard map;
- `intended_sentence`: protected secondary target, unavailable to fitting and
  selection unless a future contract explicitly authorizes a separate
  secondary score after the primary freeze.

Backspace is absent in the source task. Space and registered special classes
must be mapped explicitly. Unknown, ambiguous, or unmapped key events cause a
trial-level refusal under a frozen rule; they may not be silently dropped after
targets are visible.

## Future Split Recommendation

Loop 54 must first report the target-blind count of usable unique performed
trials. Exact identities and counts are not frozen now.

After that count is known, but before target values, model operations, or
training, a future Loop 55 preregistration should freeze one deterministic
grouped assignment rule:

- if `48 <= N < 60`: `10` final, `8` selection, and all remaining trials train;
- if `N >= 60`: `10` final, `10` selection, and all remaining trials train;
- if `N < 48`: park without splitting or training.

For the expected but unverified `N = 64`, that yields `44/10/10`.

Every event from one trial stays in one partition. Exact and semantically
similar intended sentences must stay in one partition through an isolated
target-bearing grouper whose algorithm is frozen before text is delivered.
The grouper may emit only opaque group commitments and memberships. Target
values, class frequencies, signal quality, and model behavior may not choose a
partition.

The ten final trials provide `2^10 = 1,024` exact sign assignments when all
paired effects are nonzero. Zero differences reduce the effective resolution
and must be reported rather than jittered or discarded.

## Future Model Recommendation

The exact implementation remains a future preregistration decision after Loop
54 reveals the real channel count and sampling declarations. The planning
recommendation is intentionally narrow:

- one EEG-only compact causal spatiotemporal candidate;
- one shared trainable encoder with a 29-key head and a two-hand auxiliary
  head;
- depthwise or low-rank temporal and spatial operations inspired by EEGNet;
- `<=10,000` trainable parameters including both heads;
- no transformer, recurrent language context, n-gram, LLM, NeuroToken input,
  pretrained weight, or external embedding;
- train-only normalization and no target-derived transform;
- zero right context, no zero-phase filter, and no baseline interval touching
  the keypress or future samples;
- one fixed primary seed plus at most two nonselectable stability seeds; and
- one deterministic parameter-matched or smaller linear comparator.

The recommended execution inventory is at most 12 parameter-update runs. The
future preregistration must enumerate every fit, checkpoint, inference set,
seed, and selection action exactly. Unused capacity is not permission to add a
model after targets open.

## Required Control Matrix

| ID | Condition | Role | Claim blocker? |
|---|---|---|---:|
| `L55-E00` | causal pre-keypress EEG-only candidate | reference candidate | yes |
| `L55-E01` | strongest train-only no-signal prior | primary comparator | yes |
| `L55-E02` | exact-zero signal, padding unchanged | same-checkpoint no-information probe | yes |
| `L55-E03` | whole final-trial EEG row derangement | trial correspondence control | yes |
| `L55-E04` | channel derangement | sensor identity control | yes |
| `L55-E05` | nonwrapping pre-keypress time displacement | timing relation control | yes |
| `L55-E06` | timing/count/position-only model | task-structure comparator | yes |
| `L55-E07` | train signal-target pairing derangement | training correspondence control | yes |
| `L55-E08` | EOG-only model | ocular comparator when qualified | if available |
| `L55-E09` | EEG plus EOG model | diagnostic upper bound | no |
| `L55-E10` | compact linear EEG comparator | representation diagnostic | no |
| `L55-E11` | centered `[-200,+300] ms` EEG model | noncausal positive diagnostic | no |

The strongest no-signal comparator is selected on train only from:

1. a global performed-key and performed-hand prior; and
2. a position-and-length-conditioned prior with smoothing frozen before
   selection targets open.

The timing-only condition may use only event count, event position, elapsed
trial time, preceding interkey interval, and total duration fields available
at that causal point. It receives no signal value, channel field, marker
description, key identity, sentence identity, or target-derived statistic.

EOG-only is mandatory if Loop 54 qualifies ocular channels. Missing EOG, EMG,
motion, gaze, or audio does not create a passing control; it narrows the claim
ceiling and remains an explicit unavailable field.

## Matched Analysis And Exact Decision

Every applicable condition must share:

- identical train, selection, and final trial identities;
- identical primary targets and 29-key map;
- identical causal event inclusion and trial exclusion rules;
- identical metric implementation and macro-trial aggregation;
- the same final prediction-freeze and one-shot scoring order;
- the same seed, optimizer, step, batch, and checkpoint budget when a condition
  is separately trained; and
- explicit parameter, compute, access, runtime, RSS, and output counters.

For each endpoint, the scientific claim is an intersection-union conjunction:
every applicable required comparison must pass. No multiplicity adjustment is
needed to claim the conjunction because rejecting the union null requires
rejecting every component null. Individual cherry-picked component claims are
not allowed; secondary families need their own adjustment or descriptive
label.

All ten final-trial errors and paired differences must be emitted in protected
result form. A bootstrap may summarize uncertainty but cannot replace the
exact paired decision.

## Ordered Future Access Protocol

1. Complete Loop 53 acquisition under its exact decision and receipt.
2. Complete authorized Loop 54 stages and obtain at least 48 unambiguous unique
   performed trials with a frozen confound and claim ceiling.
3. Commit, push, and remotely green an exact Loop 55 preregistration that binds
   hashes, usable count, split algorithm, architecture, transforms, seeds,
   run inventory, endpoints, controls, exclusions, caps, and refusal rules.
4. Record a separate exact Tier C authorization decision.
5. Run an isolated target-bearing grouper once; freeze opaque train, selection,
   and final identities before any model or label delivery.
6. Deliver train signal and performed-key targets only to the training stage.
7. Freeze every selection prediction before selection targets open once; apply
   only the preregistered checkpoint rule.
8. Produce every final-condition prediction without final target access.
9. Commit and push a hash-only final prediction-freeze record and wait for all
   required remote CI jobs to pass.
10. Deliver the same final targets once to an isolated scorer, score once, and
    park with no rerun or post-final tuning.

No final target, target hash with a known dictionary, plaintext prediction, or
trial text may appear in Git, stdout, CI, logs, exceptions, or public metadata.

## Outcome Router

| Outcome | Required observation | Action |
|---|---|---|
| `L55-O0` planning only | no protected execution | retain `Not Started` |
| `L55-O1` invalid | leakage, ordering, split, hash, cap, or target-freeze failure | park without scientific score |
| `L55-O2` no causal effect | E1 and E2 fail complete conjunction | retain negative result; proceed to Loop 56 boundary synthesis |
| `L55-O3` post-keypress only | centered diagnostic passes, causal endpoints fail | report task-aligned/post-keypress information only |
| `L55-O4` timing or peripheral explanation | required nonbrain comparator matches or beats candidate | report confounded or nonneural predictive route |
| `L55-O5` causal hand effect only | E1 passes, E2 fails | claim one-block performed-hand EEG sensor dependence only |
| `L55-O6` causal key effect | E1 and E2 pass | claim one-block performed-key EEG sensor dependence only |
| `L55-O7` representation diagnostic | linear passes while compact candidate fails | identify architecture-specific failure without rerun |

An E2 pass with E1 failure is internally inconsistent because each key maps to
a hand. It triggers an audit and no claim until the discrepancy is explained
without opening targets again.

## Claim Ceiling

The strongest possible clean Loop 55 result is:

> On the preregistered final trials from one S20 overt-typing block, a frozen
> compact model using only causal pre-keypress EEG values improved performed-key
> prediction over every registered available no-signal, timing, corruption,
> and peripheral comparator under exact trial-level paired tests.

That sentence still does not establish:

- brain-specific physical origin, because ocular and unrecorded peripheral
  activity can contaminate scalp EEG;
- intended-language or thought decoding, because the primary target is the
  performed key in an overt movement task;
- continuous decoding, because keypress onsets and event count are supplied;
- unseen sentence, session, participant, or device generalization beyond the
  exact grouped split and block;
- online or end-to-end latency;
- portable, home, patient, clinical, or product performance; or
- superiority to the published Brain2Qwerty architecture.

## Resource Boundary

Future execution remains bounded by:

- one CPU thread and one worker;
- at most 10,000 trainable parameters per model;
- at most 12 parameter-update runs;
- at most 45 CPU minutes total;
- at most 1 GiB peak RSS;
- at most 64 MiB generated output, including ignored protected derivatives;
- zero new downloads;
- no S7, S21, S24, or S25 access;
- no session substitution or second block;
- no language model, larger model, pretrained weight, RW3, stream, device, or
  hardware operation; and
- no rerun after final scoring.

The future closeout must report input and output bytes, runtime, peak RSS,
parameter count, event and trial counts, padding, every fit and inference run,
raw and derivative reads, target deliveries, causal status, right context,
whether end-to-end latency was measured, warnings, and unavailable fields.

## Current Access Ledger

This planning pass used six public primary-source pages and committed local
research artifacts only. Counters for S20 paths, headers, signals, markers,
MAT, targets, caches, splits, models, inference, training, scoring, downloads,
streams, devices, and hardware are all zero.

## Next Gate

Do not preregister Loop 55 yet. The next irreversible action remains the exact
Loop 53 acquisition authorization already prepared in
`docs/LOOP_53_AUTHORIZATION_PACKET.md`. After Loop 53 and Loop 54 close cleanly,
replace every unavailable S20 field in this recommendation with measured,
hash-bound facts and write one exact Loop 55 execution contract.

Engineering capability added: a machine-checkable prospective design now separates causal hand evidence, causal key evidence, post-keypress diagnostics, timing shortcuts, peripheral controls, and leakage failures before any fresh EEG target or signal is opened.

Scientific claim not established: no S20 payload, split, target, model, prediction, training run, score, or latency measurement was accessed or produced, so there is still no demonstrated EEG neural advantage or decoding result.
