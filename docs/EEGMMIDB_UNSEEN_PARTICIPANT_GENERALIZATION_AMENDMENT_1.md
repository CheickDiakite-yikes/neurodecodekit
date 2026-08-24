# EEGMMIDB-UG1 Amendment 1: Executable Control And Firewall Contract

Date: 2026-08-24

Status: **Frozen pre-execution narrowing amendment; ineffective until this
exact amendment is committed, pushed, and both CI jobs are green**

Machine amendment:

- `registries/eegmmidb_unseen_participant_generalization_amendment_1.v0.json`

## Why This Amendment Exists

Two independent target-free reviews were completed after authorization was
recorded and before any generated implementation or real operation. They found
that UG1's scientific question and maximum authority were clear, but several
details still allowed accidental implementation choices:

- temporal and spatial controls were named but not conjunctive success gates;
- participant identity was not explicitly isolated from predictive math;
- prediction-freeze serialization and scorer verification were incomplete;
- imagery completeness and several control transforms were not exact;
- causal state, early-window features, and checkpoint serialization were not
  executable from the contract alone; and
- resource enforcement lacked wall-time, process-tree RSS, atomic-write, and
  redirect semantics.

No result motivated these changes. No EDF, retained data, target, model,
prediction, or score was opened. This amendment is additive and hash-changing,
but only narrows or clarifies the already-authorized maximum. The original
research, preregistration, request, proof, and authorization decision remain
byte unchanged.

## Fixed Implementation Boundary

UG1 owns three additive modules instead of depending on private helpers from a
previous experiment:

```text
datasets/eegmmidb_unseen_participant_acquisition.py
experiments/eegmmidb_unseen_participant_generalization.py
evaluation/eegmmidb_unseen_participant_score.py
```

Existing WO9/WO9R code may be used as an implementation pattern. UG1 may not
call private underscored functions from those modules or inherit their old
participant counts, paths, contract hashes, fit schedules, or target state.

## Exact Signal Contract

The exact 64-channel order is frozen in the machine amendment. Channel names,
order, 160 Hz sampling, standard-1005 geometry availability, T0/T1/T2
annotation vocabulary, and regular no-follow file identity must match exactly.
No channel deletion, interpolation, ICA, resampling, epoch rejection, baseline
correction, or target-derived exclusion is allowed.

Processing uses float64 throughout:

1. read one complete run in time order;
2. compute instantaneous common average over all 64 channels;
3. apply the literal four-section SOS matrix in the machine amendment with
   `scipy.signal.sosfilt`, zero initial state, and one reset per run;
4. carry `zf` only across chunks from the same run if chunking is used;
5. window by exact rounded sample indices without padding; and
6. compute four contiguous means plus one normalized linear slope per channel.

`sosfiltfilt`, reverse filtering, event-wise filtering, reflection padding,
future samples, cross-run filter state, and post-window baseline correction are
forbidden. A future impulse must not change an earlier output, and full-run and
state-carrying chunked execution must replay exactly within `1e-12` absolute
tolerance.

The windows are:

| Condition | Window | Four bins | Features |
|---|---:|---:|---:|
| Primary and spatial views | `[+1,+3)` | 4 x 500 ms | `5C` |
| Pre-cue | `[-2,0)` | 4 x 500 ms | `5C` |
| Early-cue | `[0,+1)` | 4 x 250 ms | `5C` |

The slope uses `linspace(-1, 1, samples)` and the dot-product denominator from
that same vector. Whole-head dimension is 320; central is 90; frontal and
occipital are 40 each. Common-average reference always occurs over all 64
channels before a spatial subset is selected.

## Exact Predictive Firewall

Participant identity is available only to orchestration for split validation,
completeness, private row attachment, and participant-level scoring. It may not
be passed to feature extraction, normalization, a classifier, threshold logic,
or any condition transform. Predictors receive only an ordered feature matrix
and a frozen model or fixed control rule, then return one hard T1/T2 prediction
per row.

Fresh target identity is isolated before predictive code runs. Predictive code
may receive signal, cue sample, task family, and opaque row position, but not
T1/T2 identity, class count, target-derived ordering, target-derived exclusion,
participant calibration statistic, or final-set normalization. Swapping every
fresh T1/T2 target while holding target-free input fixed must leave every
prediction byte, model hash, condition hash, log, shape, and exception path
unchanged.

Source/fresh overlap, duplicate rows, aliases, symlinks, hardlinks, forbidden
source run 11/12, an unexpected participant/run, and any target key on the
predictive side refuse before fitting or prediction.

Within each run, the target-isolation process converts annotation onset to cue
sample with `round(onset_seconds * 160)`, sorts by cue sample and then original
annotation ordinal, discards T0, and assigns usable event ordinals 0 through
14. A duplicate cue sample refuses. Reordering the input annotations must
produce the same canonical rows. Timing-only previous interval uses only these
canonically ordered usable cue samples, never a future event or target value.

## Exact Model And Controls

Every fitted condition uses source-only population mean and standard deviation
with `ddof=0`; an exact zero standard deviation maps to scale `1.0`. The sole
classifier is scikit-learn shrinkage LDA with `solver="lsqr"`,
`shrinkage=0.1`, and equal priors. Ties resolve to T1. There is one candidate,
one configuration, and no seed search.

The twelve fresh conditions are exact:

1. `primary_whole_head`: fitted whole-head primary model.
2. `equal_prior_no_signal`: constant T1; no fit and no input feature read.
3. `timing_only`: source-fitted LDA over event ordinal divided by 14, seconds
   since run start, and previous inter-event interval with the first fixed to
   zero.
4. `exact_zero`: exact-zero whole-head rows passed to the primary model.
5. `fixed_channel_permutation`: the literal 64-index permutation is applied to
   the filtered channel axis before primary feature extraction.
6. `nonwrapping_event_displacement`: within participant/task/run, row `j>0`
   receives the primary features from row `j-1`; row zero is exact zero.
7. `fixed_source_label_derangement`: a separate model uses the literal
   15-index label permutation independently within every source participant
   and source run.
8. `pre_cue`: separately fitted whole-head pre-cue model.
9. `early_cue`: separately fitted whole-head early-cue model.
10. `central_view`: separately fitted 18-channel model.
11. `frontal_view`: separately fitted eight-channel model.
12. `occipital_view`: separately fitted eight-channel model.

All literal channel sets and permutations are in the machine amendment. None
is generated from targets. The provenance seed label `5909` documents the
already-frozen literals but is not executed as a random generator.

## Exact Fit And Prediction Counts

Before LOSO, every source participant/run must contain exactly fifteen usable
T1/T2 rows with both classes present: 450 execution rows and 450 imagery rows
overall. A mismatch routes R0 before any source fit and before fresh acquisition.

Source LOSO uses fifteen folds. Each execution fold fits primary and timing
models on exactly fourteen participants and produces primary, timing, and
no-signal predictions for the held-out participant. Imagery LOSO is descriptive
and fits only its primary model; it cannot open the fresh gate or rescue a
failed execution gate.

After a passing source gate, the full source checkpoint contains eight fitted
models per task: primary, timing, source-label derangement, pre-cue, early-cue,
central, frontal, and occipital. Zero, channel permutation, and displacement
reuse the primary model; no-signal has no fit.

The complete maximum is therefore 61 parameter-update fits and 420
participant-condition prediction sets, below the original caps of 300 and 640.
Any additional fit or prediction set refuses.

## Exact Completeness And Statistics

Fresh execution must contain exactly 15 participants and exactly 225 T1/T2
rows. Fresh imagery must independently contain exactly 15 participants and
exactly 225 T1/T2 rows. Every participant/task must contain exactly 15 usable
rows with both classes present. The sealed target input contains exactly 450
unique row identities. Missing, duplicate, extra, aliased, or mismatched rows
route R0; no exclusion, replacement, or partial score is allowed.

Participant-macro balanced accuracy and pooled balanced accuracy are mandatory.
Ordinary pooled accuracy is descriptive only. Exact one-sided sign-flip tests
enumerate all 32,768 assignments over fifteen participant values, include the
observed assignment, retain zeros under both signs, and count values at least
the observed statistic with `1e-12` comparison tolerance.

For participant `i`:

```text
B_i = max(no-signal, timing-only)
C_i = max(zero, channel permutation, displacement, label derangement)
A_i = max(pre-cue, early-cue, central, frontal, occipital)
```

Execution R3 requires every original gate plus:

- macro primary-minus-`A_i` at least `0.02`;
- paired sign-flip against `A_i` at most `0.05`; and
- paired sign-flip against `B_i` at most `0.05`.

Imagery R4 requires the same counts, accuracy floors, no-signal/timing margin,
derangement margin, temporal/spatial margin, at least 11/15 above chance, and
paired p-value ceilings. Its chance sign-flip ceiling remains `0.05`. It cannot
rescue execution. These are stricter success requirements, not new claims.

## Canonical Checkpoint And Prediction Freeze

Pickle and joblib are forbidden. A checkpoint is a directory containing
canonical JSON plus individual NumPy `.npy` arrays saved with
`allow_pickle=False`. It records task, condition, source split, exact package
versions, channel order/subset, SOS, windows, scaler mean/scale, LDA classes,
coefficients/intercept, code/config/contract/amendment/source-payload hashes,
and a SHA-256 for every member. Loading revalidates every field, shape, dtype,
member hash, and aggregate manifest hash before prediction.

Private predictions use canonical UTF-8 JSONL sorted by task, participant, run,
event ordinal, then condition. Each row contains schema version, opaque row ID,
task, participant, run, event ordinal, cue sample, condition, and exactly one
hard T1/T2 prediction. It contains no target, probability, or free-form field.

The public freeze records only per-task/per-condition row counts and SHA-256
values plus aggregate checkpoint, configuration, code, prediction-set, and
canonical-row-order hashes. The scorer must rehash the exact private file,
reconstruct the canonical order, verify every condition count and commitment,
and reject any row, order, prediction, checkpoint, configuration, or target-file
mutation before opening target values.

## Resource And Filesystem Semantics

The original byte/request/RSS caps remain maxima. The amendment adds narrower
wall-time caps: Stage G 900 seconds, M 300, S 1,800, F 1,800, and T 300.
Process-tree peak RSS, cumulative network bytes, cumulative new payload bytes,
temporary plus final output bytes, and free disk are measured. A breach refuses
without fallback.

Every output uses an invocation-owned temporary file in the destination
directory, exclusive creation, flush and fsync, then one atomic rename only
after validation. A pre-existing destination, symlink, hardlink alias, path
traversal, redirect, partial response, short write, crash before rename, disk
cap, RSS cap, wall cap, or second invocation refuses. Cleanup may remove only
temporary files created by that invocation. Network is zero during Stage G and
all analysis stages.

## Stage G Acceptance Matrix

One generated/mock qualification must cover at least these fixed classes:

- exact valid replay, source immutability, and deterministic output;
- target swap/canary and participant relabel invariance;
- split overlap, alias, symlink, hardlink, duplicate, and forbidden-run refusal;
- future-impulse causality, chunk replay, run reset, and acausal-filter refusal;
- every literal permutation, displacement, derangement, window, channel view,
  and common-average ordering;
- missing, duplicate, extra, and reordered annotation handling;
- exact execution and imagery count checks;
- checkpoint, configuration, prediction, row-order, and freeze mutation refusal;
- exact sign-flip ties and every router threshold boundary; and
- atomic crash, destination, traversal, redirect, output, RSS, wall, and
  second-invocation refusal.

Stage G may use generated arrays, generated reader-surface fixtures, and mocked
transport only. It may not list, stat, resolve, hash, open, or parse a real,
retained, ignored, private, or consumed data root. Its result must report input
and output bytes, runtime, peak process-tree RSS, fits, prediction sets, real
path reads, network bytes, model runs, target deliveries, scores, and every
warning. Qualification cannot be repeated.

## Authority And Claim Boundary

This amendment performs zero generated qualification, network, real-path, EDF,
signal, annotation, target, fit, inference, prediction, score, release, or claim
operation. Stage G remains unavailable until the exact amendment commit is
pushed and both CI jobs pass. Stages M through T retain every prior barrier.

Engineering capability added after remote green: UG1 will have an executable,
leakage-resistant specification whose controls and prediction freeze can be
implemented without result-dependent choices.

Scientific claim not established: this amendment observes no neural data or
result, so it establishes no unseen-person generalization, neural advantage,
movement intention, motor-cortex origin, eye-independent effect, language or
thought decoding, live decoding, or hardware result.
