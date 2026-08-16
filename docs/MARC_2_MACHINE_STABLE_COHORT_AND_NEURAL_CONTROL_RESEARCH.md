# MARC-2 Machine-Stable Cohort And Neural-Control Research

Date: 2026-08-16

Status: **Tier A architecture research only; no new private pass, payload,
training, prediction, target delivery, score, or claim is authorized**

Machine registry:
`registries/marc2_machine_stable_cohort_and_neural_control_research.v0.json`

## Executive Decision

Keep the same scientific path and repair the execution boundary, not the
hypothesis. `MARC2-VR3` consumed before private access because a transient
machine resource gate was coupled to the irreversible invocation. That gate
protected the computer but did not protect research throughput: a 418,755-byte
metadata pass was lost without producing a cohort or a diagnostic value.

The replacement architecture has three ordered work orders:

1. `MARC2-VR4`: separate reversible machine readiness from the one irreversible
   structural-manifest open;
2. `MARC2-FW2`: acquire and semantically qualify only the frozen cohort's
   required archive members under the maintainer's 10 GiB ceiling; and
3. `MARC2-CIL1`: run one target-firewalled within-person, held-out-session
   neural-control experiment.

This document is not the VR4 or FW2 preregistration. It freezes the design
choice needed to write those contracts honestly after the real cohort exists.

## Why VR3 Failed Without Reading Data

The exact green VR3 executor validated proof, then checked normalized
one-minute load, free disk, and process RSS in one aggregate predicate. It
returned `MARC2VDR-F01` before output-root or private-path preflight. The exact
failed predicate and value were not emitted. No later machine snapshot can
recover that observation.

The safety intent was right. The consumption boundary was wrong. Machine load
is transient and is neither data access nor scientific evidence. It should be
measured and allowed to settle before the one-shot data operation begins.

## VR4: Preconsumption Readiness Separation

VR4 will be a separately named implementation and root. It must not import,
call, edit, copy, expose, or inspect the consumed VR3 executor or any consumed
root.

The future invocation has two explicit states.

### State A: reversible machine readiness

Before an output-root or private-path operation, a standard-library readiness
function may poll only:

- the five numerical-thread environment variables;
- logical CPU count;
- one-minute load and normalized load;
- process peak RSS; and
- free disk for the repository filesystem.

It may wait for up to 600 seconds, sample no faster than once every five
seconds, and require three consecutive passing samples. Every sample must be
reported with its exact value and threshold. A timeout emits a bounded
aggregate readiness report and performs zero private or output-root operations.
Because this state has no data or outcome access, a timeout does not consume
the one registered private content open.

The proposed thresholds are one numerical thread, normalized load at or below
one runnable unit per logical CPU, process RSS below 256 MiB, and at least
15 GiB free disk. These protect the computer without converting an ephemeral
load average into an irreversible evidence result.

### State B: irreversible structural freeze

Only after readiness passes in the same process may the executor check the new
output root and fixed private path. It then writes one mode-`0600` marker before
the sole `O_NOFOLLOW` content open. From that marker onward, every route is
final and no retry, rerun, resume, repair, or fallback exists.

The source, selector, privacy, and storage invariants remain unchanged:

- exact 418,755 bytes and registered SHA-256;
- strict duplicate-key-controlled JSON;
- all 1,227 rows and all 238 bundles validated before filtering;
- dynamic `195 eligible + 43 valid ineligible` reconciliation;
- exact one call to the green VR2 adapter;
- target-free contiguous ranked prefix under the 8 GiB reservation cap;
- `ses-01` fit and `ses-02` held-out identities;
- at most a marker, private cohort manifest, aggregate report, and readiness
  report under a 4 MiB output ceiling; and
- zero archive-member, signal, event, target, channel, model, or score access.

VR4 must emit a specific machine refusal code and exact safe measurement. It
must never repeat VR3's opaque aggregate machine reason.

## FW2: Bounded Member Acquisition And Semantic Qualification

FW2 begins only after a real cohort manifest is committed as an aggregate hash
and remotely green. The private member list remains local and mode `0600`.

The future FW2 packet must bind exact member identities, source ranges,
compressed and uncompressed byte totals, local-header signatures, CRCs,
expected clocks, and output paths. If the real uncompressed or peak-disk total
cannot stay below 10 GiB, the contract must shrink by a target-free prefix rule
before any range request. It may never download or materialize the 13.59 GB
archive as a whole.

Acquisition should stream one selected member at a time, hash while writing,
and delete only invocation-created range fragments after integrity passes. A
bounded derivative may retain the minimum causal streams needed for analysis.
Network transfer, peak incremental disk, retained bytes, runtime, and RSS must
all be measured.

Semantic qualification may establish source-declared EEG, EOG, trigger,
accelerometer, sampling, session, run, generic cue, reviewed movement-onset,
and four-choice target compatibility. It may not select trials or thresholds
from held-out outcomes and may not deliver held-out targets to a model.

## CIL1: One Neural-Control Experiment

The scientific question is:

> Within the frozen people, does strictly causal pre-movement EEG improve
> held-out-session prediction of a self-chosen target beyond no-signal,
> cue/timing, and recorded peripheral controls, and beyond an item-deranged EEG
> view?

The task remains four-way chosen-target prediction. Session 1 is fit and
development. Session 2 is a consumed held-out evaluation set. Models are
within-person; no unseen-person claim is available.

### Primary and secondary families

- Primary `H-LF`: causal 0.5-4 Hz potential features with train-only scaling
  and shrinkage LDA or an equivalent frozen regularized linear head.
- Secondary `H-SMR`: causal train-only mu/beta covariance or log-power features
  with one frozen regularized linear or Riemannian head.

No deep network, transformer, foundation model, pretrained checkpoint, model
search, restart, or final-target family selection is eligible. Exact feature
windows and regularization values must be frozen after semantic qualification
and before held-out signal inference.

### Required matched conditions

1. `B0 no-signal`: session-1 class prior only.
2. `B1 timing`: generic-cue time, elapsed trial time, run position, and trial
   schedule only; no signal sample.
3. `P peripheral`: causal EOG and wrist-acceleration history available at the
   prediction timestamp, with EOG-only and acceleration-only summaries.
4. `E signal`: EEG-only candidate.
5. `P+E matched signal`: the same peripheral model augmented with EEG.
6. `P+D(E) derangement`: the same peripheral model augmented with a fixed,
   target-independent, no-fixed-point within-participant EEG item derangement.
7. `future sentinel`: an intentionally forbidden future-context view that must
   be detectable and excluded from scientific scoring.

The four maintainer-requested anchors are therefore explicit: `P+E` is signal,
`P+D(E)` is derangement, `B1` is timing, and `B0` is no-signal.

The derangement mapping is derived from the frozen cohort/split hash before any
held-out target opens. It preserves participant, session, run, shape, and time
coverage, has no fixed points, and uses no class label or quality value.

### Causality and timing firewall

The producer emits continuous held-out probability streams on a frozen grid
using only samples at or before each prediction timestamp. Reviewed held-out
movement onsets are not model inputs. They remain sealed with held-out targets
until scoring, when the scorer samples the already frozen streams at the fixed
pre-movement offsets. This distinguishes causal signal production from
non-real-time event-aligned evaluation.

No centered filter, zero-phase operation, future normalization, post-onset
sample, held-out calibration, test-time adaptation, or target-derived exclusion
is allowed.

### Primary endpoint and positive route

The primary endpoint is participant-macro conditional log-loss gain:

```text
delta_EEG_given_P = log_loss(P) - log_loss(P+E)
```

The future preregistration must freeze the exact participant count, trial count,
minimum meaningful gain, participant-consistency floor, and one-sided exact
paired sign-flip test after cohort and semantic qualification but before
held-out inference. The present candidates are a mean gain of at least 0.02
nats per trial, at least two-thirds of participants positive, and `p <= 0.05`.
They are design candidates, not yet registered thresholds.

A positive top route must satisfy all of these on the same frozen predictions:

- `P+E` improves log loss over `P`, `B1`, and `B0`;
- `P+E` improves over `P+D(E)`;
- the participant-level test and consistency floor pass;
- no future-context sentinel reaches scientific scoring;
- onset-shift, EOG-only, acceleration-only, frontal, and occipital summaries
  are reported without post-target selection; and
- the secondary family is multiplicity-controlled and cannot rescue a failed
  primary by model selection.

Balanced accuracy, macro F1, calibration error, and confusion matrices are
secondary. Pooled-trial significance is descriptive only.

## Target Firewall And Freeze Order

The future executor must physically separate:

1. session-1 signals, controls, onsets, and targets for fitting;
2. session-2 target-blind signal/control streams for inference;
3. one aggregate hash-only prediction freeze with no individual prediction or
   participant outcome; and
4. one combined delivery of the same sealed session-2 onsets and targets to an
   isolated scorer only after the freeze commit is remotely green.

The scorer may read predictions but the model stage may never read the scorer
input. A final target delivery consumes the experiment. Post-target updates,
threshold changes, reruns, and additional families are zero.

## Compute And Storage Posture

The future experiment remains compact:

- one CPU thread, one worker, one numerical job;
- primary plus one secondary classical family;
- no more than 304 fits if the cohort reaches the 19-person selector maximum;
- no more than 512 target-blind prediction sets across all controls;
- no more than 1,800 seconds and 768 MiB peak RSS for analysis;
- no more than 10 GiB network transfer or peak incremental disk for FW2;
- no more than 2 GiB retained derivative and 64 MiB model/prediction artifacts;
  and
- zero provider, language-model, stream, device, or hardware operations.

Exact counts must be reduced and frozen after the real cohort and source
semantics are known. These are ceilings, not authorization.

## Claim Boundary

The strongest possible pass would establish within-person, held-out-session
pre-movement scalp-sensor information about a self-chosen reaching target that
adds value beyond the recorded timing, EOG, and wrist-acceleration controls.

It would not establish exclusively brain-generated origin because EMG and
other peripheral activity remain incompletely observed. It would not establish
typing, language, thought decoding, unseen-person generalization, real-time
operation, portable hardware, home use, assistive utility, or a clinical
result.

Engineering capability specified: NeuroDecodeKit now has a concrete design
for separating reversible machine readiness from one-shot data consumption and
for routing a frozen cohort into a bounded target-firewalled control ladder.

Scientific claim not established: this architecture research reads no neural
payload, target, prediction, or score and establishes no neural effect or
decoding result.
