# Loop 48 Stage B Train-Only Failure-Discrimination Implementation

Date: 2026-07-15

Status at implementation commit `1d840e3`: **Implemented and synthetic-tested;
protected execution has not started**

Post-execution status: **Completed once and consumed.** See
`docs/LOOP_48_STAGE_B_RESULT.md` and
`registries/loop48_train_only_discrimination_result.v0.json`. This document
retains the pre-access implementation boundary for audit.

Registered design:
`docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md`

Machine contract:
`registries/loop48_train_only_discrimination_contract.v0.json`

Authorization decision:
`registries/loop48_stage_b_authorization_decision.v0.json`

## Purpose

Loop 26 established a negative result: the registered causal candidate was
worse than the source-train-only no-signal prior on the consumed six-row S21
validation set. Loop 48 Stage A then reproduced an aggregate blank-dominant,
seed-sensitive failure phenotype but did not establish a root cause.

Stage B implements the preregistered next diagnostic. It asks whether the
failure is more consistent with one or more of six mechanisms:

1. fixed tiny-CTC optimization or feasibility failure;
2. a gross defect in the transformed sentence cache;
3. timing or preprocessing sensitivity;
4. stable but nonseparable representations for the two registered probes;
5. a prior-dominated task regime; or
6. insufficient sentence quantity or diversity inside the bounded 8-44 row
   range.

The mechanisms may coexist. The scorer emits a six-row support vector and
preserves conflicts and unavailable evidence. It never forces a single root
cause.

## New Engineering Surface

The implementation adds two dependency-light modules and five staged CLI
commands.

| Surface | Responsibility |
|---|---|
| `evaluation/train_only_failure_discrimination.py` | Deterministic split, 41-condition inventory, corruption transforms, hash-only freeze validation, exact sign-flip scoring, and six-hypothesis rules |
| `experiments/train_only_failure_discrimination_gate.py` | Git/authorization/resource gates, bounded row streaming, isolated derivatives, fixed training, private predictions, freeze emission, and one-shot scoring |
| `loop48-stage-b-static-gate` | Bind authorization, implementation/CI evidence, source size, split, headers, channels, environment, disk, and 44/11 identities without signal or target delivery |
| `loop48-stage-b-create-derivatives` | Perform the cache's one SHA-256 pass and create only the 44-row fit and target-free 11-row check-input bundles |
| `loop48-stage-b-target-blind` | Run the exact 20 fits, 35 model inferences, five priors, and freeze 41 prediction sets without check targets |
| `loop48-stage-b-inspect-freeze` | Strictly validate the plaintext-free prediction and telemetry inventory |
| `loop48-stage-b-score` | After a remotely green freeze, deliver the same 11 check targets once, score all conditions together, and consume the protocol |

Heavy imports remain inside runtime functions. CLI help and the base unit suite
continue to work without NumPy, SciPy, Torch, MNE, or Zarr.

## Access Firewall

The implementation follows this irreversible order:

1. Commit, push, test, and remotely qualify this implementation using only
   synthetic arrays.
2. Run the metadata-only static gate against that exact green commit.
3. Hash the registered 10,632,576-byte cache exactly once.
4. Stream the 55 source-train rows into a 44-row fit bundle and an 11-row
   check-input bundle with no check targets.
5. Complete transformed-quality and fit-row CTC-feasibility audits.
6. Run all fixed fits, inferences, priors, and controls.
7. Commit and remotely qualify the hash-only prediction freeze.
8. Write a consumed marker before delivering the 11 check targets.
9. Score all 41 sets once and forbid every rerun or post-check update.

The implementation never requests validation rows, source-test rows, session
2, S7, S20, S25, raw FIF/MAT files, historical private predictions, or a new
download. Deflated members can require opaque traversal of excluded bytes. The
ledger reports that traversal and does not call it physical nonaccess.

The upstream sentence cache is offline/noncausal: it used whole-recording FFT
resampling, zero-phase filtering, sentence endpoints, and post-context. Only
the tiny model may be described as causal, with zero right context; no
end-to-end causal or latency claim is available.

## Exact Diagnostic Split

Only the 55 rows already assigned to source `train` are eligible. Ordering is
the SHA-256 rule frozen in the contract:

```text
SHA256(
  "neurodecodekit-loop48-stage-b-v0-fit-check" UTF-8
  || 0x00
  || semantic_row_uid_sha256 UTF-8
  || 0x00
  || row_uid_sha256 UTF-8
)
```

The first 44 rows are fit rows and the last 11 are check rows. Fit prefixes are
the strictly nested first `8, 16, 24, 32, 44` rows. Targets and prior Loop 26
metrics cannot affect this order. The implementation rejects duplicate row or
semantic IDs, count drift, overlap, or missing membership before delivery.

All 55 rows were used by historical Loop 26 fits. The 11-row partition is
withheld from this new fit and prediction process, not historically unseen and
not independent validation.

## Fit And Prediction Inventory

The implementation introduces no architecture. It instantiates the exact
2,908-parameter causal candidate and 2,884-parameter pointwise linear model
from the frozen Loop 26 source.

| Family | Fits | Check prediction sets | Model-inference calls |
|---|---:|---:|---:|
| Candidate, 5 prefixes x 3 seeds | 15 | 15 | 15 |
| Size-matched no-signal priors | 0 parameter updates / 5 fits | 5 | 0 |
| Linear, size 44 x 3 seeds | 3 | 3 | 3 |
| Zero signal | 0 | 1 | 1 |
| Check-row prediction cycle | 0 | 1 | 0 |
| Channel cycle | 0 | 1 | 1 |
| Four fine shifts x 3 seeds | 0 | 12 | 12 |
| Severe +100-sample shift | 0 | 1 | 1 |
| Timing-only fit | 1 | 1 | 1 |
| Fit-target cyclic derangement | 1 | 1 | 1 |
| **Total** | **20 parameterized + 5 priors** | **41** | **35** |

Every parameterized fit uses CPU float32, one thread, Adam at learning rate
`0.02`, at most 16 rows per batch, exactly 240 steps, final-step selection, and
no clipping, early stopping, restart, or favorable-seed selection.

The registered experiment seeds `4801`, `4802`, and `4803` drive Torch weight
initialization and NumPy batch order. The pinned Loop 26 config class permits
only its historical `2601-2603` values, so the implementation uses a
seed-2601 config object solely to instantiate the byte-bound architecture; it
does not use that field as the Stage B random seed. The freeze configuration
records the actual Stage B execution seed explicitly. Synthetic replay tests
verify byte-identical states and telemetry under repeated seed 4801 runs.

## Telemetry

Each of the 20 fits records the same six finite values at steps
`1, 8, 16, 32, 64, 120, 180, 240`:

- CTC loss;
- gradient L2 norm;
- parameter-update L2 norm;
- mean blank posterior;
- posterior entropy; and
- best-nonblank minus blank logit margin.

One post-step-240 inference combines that fit's own rows with the target-free
check inputs. This preserves one inference call while separately hashing fit
and check predictions. Fit CER and blank fraction may use fit targets. Check
CER remains unavailable until the freeze is remotely green.

## Quality Audit

Before training, the derivative stage records:

- fit-row input length, target length, adjacent repeats, minimum CTC alignment
  steps, frame-to-target ratio, and feasibility;
- fit and check nonfinite and nonzero-padding counts;
- fit-channel variance and median absolute deviation;
- per-trial RMS, median absolute amplitude, near-flat-channel fraction,
  duration, and valid samples; and
- every source, split, scaler, channel, derivative, configuration, and payload
  hash.

A gross transformed-cache concern is raised by any nonfinite value, nonzero
padding, globally near-flat fit channel at variance `<= 1e-8`, or trial with at
least 20% near-flat channels. Passing this audit cannot weigh against H2. Raw
sensor quality, line noise, bad-channel annotations, head motion, and
peripheral physiology remain unavailable.

Check target lengths remain sealed during this stage. Their CTC feasibility is
reported only after the green-freeze target delivery.

## Exact Scoring

For every comparator and check row:

```text
d_i = comparator_CER_i - candidate_CER_i
```

Positive differences favor the candidate. The scorer enumerates all
`2^11 = 2,048` sign assignments and reports exact one-sided and two-sided
p-values. The intact-signal conjunction requires at least `0.05` macro-CER
improvement and one-sided `p <= 0.05` against the size-44 prior and all six
registered corruptions. Fine shifts use the frozen Bonferroni threshold
`p <= 0.0125` plus the same direction across all seeds.

The public result contains aggregate metrics, per-item edit counts keyed only
by hashed item IDs, the support vector, counters, resources, warnings, and
unavailable fields. It contains no plaintext target or prediction.

## Resource Enforcement

The code fails closed at the frozen caps:

- one CPU thread, one worker, and one numerical job;
- 20 parameter-update runs and 4,800 steps;
- 35 model-inference calls and 41 prediction sets;
- 600 seconds of parameter-update runtime and 900 seconds cumulative runtime;
- 1 GiB peak RSS and 128 MiB conservative working-array bound;
- 4 MiB checkpoints, 4 MiB private predictions, and 32 MiB all generated
  artifacts;
- at least 20 GiB free disk before execution; and
- zero network calls, downloads, model weights, language models, NeuroTokens,
  streams, devices, or hardware operations.

The quality-audit bound includes the resident derivatives, streamed source
rows, one float32 concatenation, and four fit-signal-sized float64 temporary
buffers. The target-blind bound includes resident derivatives, the largest
combined fit/check inference copy, and two largest-transform copies.

## Synthetic Qualification

No registered cache, split report, target, checkpoint, or ignored historical
output was opened during implementation or tests.

The focused optional test lane exercises:

- deterministic 44/11 assignment and target-independence;
- malformed freeze, plaintext leakage, counter drift, and target-before-freeze
  refusals;
- nonwrapping positive and negative shifts;
- fixed-point-free channel, row, and fit-target cycles;
- timing-only signal independence;
- exact 2,048-assignment scoring;
- byte-identical replay of two complete 240-step seed-4801 synthetic fits; and
- one complete synthetic 44/11 orchestration over all 20 fits, 4,800 steps, 35
  inferences, five priors, and 41 frozen sets.

The complete synthetic orchestration took 5.37 seconds on tiny eight-frame
arrays during implementation. It is interface and control-flow evidence only;
it is not representative real-cache runtime or scientific evidence.

## Registered Runbook

After this implementation commit and both CI workflows are green:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

neurodecode loop48-stage-b-static-gate \
  --repo-root . \
  --implementation-commit <green-implementation-commit> \
  --implementation-push-ci-run-id <green-push-run> \
  --implementation-pr-ci-run-id <green-pr-run>

neurodecode loop48-stage-b-create-derivatives --repo-root .

neurodecode loop48-stage-b-target-blind \
  --repo-root . \
  --implementation-commit <green-implementation-commit>

neurodecode loop48-stage-b-inspect-freeze \
  --freeze-record registries/loop48_stage_b_prediction_freeze.v0.json
```

The freeze must then be tested, committed, pushed, and remotely green. Only
after that gate may the consumed scorer run:

```bash
neurodecode loop48-stage-b-score \
  --repo-root . \
  --freeze-record registries/loop48_stage_b_prediction_freeze.v0.json \
  --green-freeze-commit <green-freeze-commit> \
  --freeze-push-ci-run-id <green-push-run> \
  --freeze-pr-ci-run-id <green-pr-run>
```

## Claim Boundary

Engineering capability added: NeuroDecodeKit can now execute one hash-bound,
single-thread, prediction-frozen train-only protocol that evaluates six
coexisting failure hypotheses while keeping check targets sealed until a
remotely green freeze.

Scientific claim not established: this implementation and its synthetic tests
do not establish a Stage B result, root cause, independent validation, neural
advantage, brain-specific origin, useful decoding, unseen-person
generalization, causal preprocessing, real-time behavior, EEG or home-device
performance, assistive value, diagnostic value, or clinical utility.
