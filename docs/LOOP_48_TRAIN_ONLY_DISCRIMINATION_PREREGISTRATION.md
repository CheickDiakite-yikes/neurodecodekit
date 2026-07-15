# Loop 48 Train-Only Failure-Discrimination Preregistration

Date: 2026-07-15

Status: **Preregistered; no implementation or protected execution is authorized**

Proof posture: **post-outcome, train-only diagnostic design with a prospective
within-execution check firewall**

Machine contract:
`registries/loop48_train_only_discrimination_contract.v0.json`

Future authorization packet: `docs/LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md`

## Decision

Loop 48 Stage A reproduced a blank-dominant, seed-sensitive failure phenotype
from committed aggregate artifacts. It did not identify a root cause. The next
highest-information action is one bounded Stage B diagnostic over the existing
55 S21 source-train rows, before acquiring another participant or designing a
larger model.

Stage B asks six questions from one shared evidence collection:

1. Can the exact 2,908-parameter causal CTC recipe optimize and fit a tiny
   subset at all?
2. Does the transformed sentence cache contain gross channel or trial defects?
3. Are predictions unusually sensitive to fixed nonwrapping time shifts?
4. Do the exact causal and linear CTC probes separate a disjoint diagnostic
   partition?
5. Does intact signal clear a train-only no-signal prior and every registered
   corruption?
6. Does check error improve as unique fit sentences increase from 8 to 44?

These mechanisms can coexist. The output is a six-row support vector with
conflicts and missing evidence, never a forced root cause.

## Why Stage B Comes Before Loop 49

Loop 49 is still required for fresh-person development evidence. It would add
roughly one gigabyte and could not by itself distinguish an optimization
collapse from weak transformed inputs, timing sensitivity, prior dominance, or
insufficient sentence diversity. Stage B reuses a 10,632,576-byte local cache,
runs sequentially on one CPU thread, and can determine which measurements and
controls Loop 49 and Loop 50 must preserve.

This is an information-order decision, not a claim that old train rows are
fresh evidence. A clean Stage B result routes directly to Loop 49. It cannot
replace Loop 49, rescue the consumed Loop 26 validation, or open S25.

## Claim-Ceiling Correction

All 55 source-train rows were used by the earlier Loop 26 model fits. Creating a
new deterministic 44/11 split now prevents leakage inside this execution, but
it does not make those 11 rows historically unseen or independently
confirmatory. The earlier design-level `E3` ceiling is therefore too high for
this exact source.

Stage B can reach at most **E2 pipeline-discriminative evidence**:

> Under one frozen post-outcome diagnostic protocol, the intact transformed
> sensor input did or did not outperform specified signal-free and corrupted
> comparators on 11 rows excluded from these new fits.

It may not call that result independent validation, neural advantage,
brain-specific origin, generalization, useful decoding, or a real-time result.
Fresh-person evidence remains behind Loops 49 and 50; a final strict zero-shot
claim remains behind Loops 51 and 52.

## Frozen Source Boundary

No cache member or ignored artifact was read while preparing this contract.
The exact source identity is inherited from the green Loop 26 contract and its
committed result:

| Field | Frozen value |
|---|---|
| Sentence cache | `cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz` |
| Cache bytes | `10,632,576` |
| Cache SHA-256 | `45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815` |
| Shape | `66 x 102 x 617`, float32, 100 Hz |
| Split report SHA-256 | `cd0001b49666352919ea137859a6948a5e96c467def2e2b9c08be8c1c94574ef` |
| Protocol SHA-256 | `503ec4e77c64dea4b30b435e48fa0ec21279b61630dde5081a2a1e917388002d` |
| Semantic membership SHA-256 | `2382bd42f09630591ccbd1405e24e3aaf9035f8fec06eb05273a2596fde17dd7` |
| Physical membership SHA-256 | `4feb3854161c7f336a73c3d3ae5d7e67ac6ec11825de6370df1387c8f949ea85` |
| Channel-order SHA-256 | `2befa0b191802432f1907e71ad727b4254f7c48f68c7572bf17df03000c50cc3` |
| Frozen scaler center / scale | `d0beb18f...` / `e67ae077...` |
| Source membership | 55 train / 6 consumed validation / 5 consumed test rows |

Only the 55 rows already assigned to `train` are eligible. Validation, source
test, session 2, S7, S20, S25, raw FIF/MAT files, and every private Loop 26
checkpoint or prediction are excluded.

The source is a monolithic deflated NPZ. A future reader may traverse excluded
bytes opaquely while returning only allowed rows. The project will not claim
physical nonaccess. It will report exactly which rows reached fitting,
inference, interpretation, and scoring code.

## Deterministic 44/11 Diagnostic Split

The split is target-value independent and frozen before any protected read.
For every one of the 55 source-train rows, compute:

```text
SHA256(
  "neurodecodekit-loop48-stage-b-v0-fit-check" UTF-8
  || 0x00
  || semantic_row_uid_sha256 UTF-8
  || 0x00
  || row_uid_sha256 UTF-8
)
```

Sort ascending by that digest and then by source row index. The first 44 rows
are `fit`; the remaining 11 are `check`. The same order defines strictly nested
fit prefixes of `8, 16, 24, 32, 44` rows.

The static gate requires 55 unique row IDs and 55 unique semantic sentence IDs.
Any duplicate, missing membership, identity drift, or count other than 44/11
parks the experiment before signal or target delivery.

The 11 check targets are logically withheld from every fit, model inference,
prediction transformation, threshold, and stopping decision. Because their
values existed in earlier training workflows, the supported phrase is
`withheld from this registered prediction process`, not `never previously
seen`.

## Isolated Runtime Order

The future implementation must use the bounded row-streaming NPY reader. It may
not call the legacy whole-array sentence-cache loader.

Before check scoring, it may create only:

- a 44-row fit bundle containing signals, lengths, IDs, and targets; and
- an 11-row check-input bundle containing signals, lengths, IDs, and no target
  values.

Both remain under `.codex_work/loop48_stage_b/`, stay Git-ignored, and record
source, split, configuration, shape, dtype, size, and SHA-256 bindings. No
validation or source-test derivative may exist.

Only after all 41 prediction sets and every telemetry/configuration hash are
committed in a plaintext-free freeze record, pushed, and remotely green may one
isolated scorer receive the 11 check targets once.

## Static And Quality Audit

Before parameter updates, Stage B records:

- CTC input length, target length, adjacent-repeat count, minimum feasible
  alignment length, and frame-to-target ratio for each allowed row;
- nonfinite and nonzero-padding counts;
- per-channel variance and median absolute deviation on valid transformed
  samples;
- per-trial RMS, median absolute amplitude, and near-flat channel fraction;
- sentence duration and transformed valid-sample count; and
- every source, membership, split, scaler, channel, and configuration hash.

Gross transformed-cache defects are frozen as:

- any nonfinite value;
- any nonzero padded value;
- any channel with variance at or below `1e-8` across fit valid samples; or
- any trial with at least 20% of channels at variance at or below `1e-8`.

These checks can identify a malformed or grossly degenerate transformed cache.
They cannot assess raw sensor noise, bad-channel annotations, acquisition-room
interference, 50 Hz line noise at a 100 Hz Nyquist boundary, head motion,
peripheral physiology, or whether preprocessing removed neural information.
Passing them cannot weigh against `H2`; failing them supports only an `E1`
transformed-cache quality concern.

## Frozen Model And Fit Inventory

No new architecture is introduced. The exact model, optimizer, vocabulary,
and greedy CTC decoder are inherited from Loop 26.

```text
candidate: 2,908 parameters, causal right context 0, left context 2 frames
linear:    2,884 parameters, pointwise Conv1d(102 -> 28, kernel 1)
optimizer: Adam(lr=0.02, betas=(0.9, 0.999), eps=1e-8)
steps:     exactly 240 per fit
batch:     at most 16
loss:      torch.nn.CTCLoss(blank=0, mean, zero_infinity=false)
selection: final state after step 240 only
restarts:  zero
```

Seeds are exactly `4801`, `4802`, and `4803`; seed 4801 is primary. There is no
favorable-seed selection.

| Fit family | Exact runs |
|---|---:|
| Candidate at 5 prefixes x 3 seeds | 15 |
| Linear comparator at 44 rows x 3 seeds | 3 |
| Fit-target cyclic derangement at 44 rows, seed 4801 | 1 |
| Timing-only input at 44 rows, seed 4801 | 1 |
| **Parameter-update runs** | **20** |
| **Optimizer steps** | **4,800** |
| Size-matched no-signal prior fits | **5** |

The target derangement uses one fixed-point-free cycle ordered by SHA-256 with
salt `neurodecodekit-loop48-stage-b-v0-fit-target-cycle`. The timing-only input
preserves each row's shape and length, places a constant in channel 0, a
normalized linear time ramp in channel 1, and zero in all other values.

## Fit Telemetry

Every parameterized fit records the same fields at steps
`1, 8, 16, 32, 64, 120, 180, 240`:

- CTC loss;
- gradient L2 norm;
- parameter-update L2 norm;
- mean blank posterior;
- posterior entropy; and
- best-nonblank minus blank logit margin.

After step 240, one target-blind batched inference over that fit's own prefix
plus the same 11 check inputs records greedy blank fraction and prediction
hashes. Fit metrics may then be computed from fit targets. Check metrics remain
unavailable until the freeze record is remotely green.

Nonfinite loss, gradient, update, posterior, entropy, or margin parks the run
without restart.

## Exact Prediction Inventory

The target-blind stage performs exactly 35 model-inference runs and freezes 41
prediction sets:

| Prediction family | Sets | Model runs |
|---|---:|---:|
| Candidate prefixes x seeds | 15 | 15 |
| Size-matched no-signal priors | 5 | 0 |
| Size-44 linear comparator x seeds | 3 | 3 |
| Exact-zero check signal, primary checkpoint | 1 | 1 |
| Whole-row prediction derangement | 1 | 0 |
| Channel-name-hash derangement, primary checkpoint | 1 | 1 |
| Fine shifts `-50, -25, +25, +50` x 3 checkpoints | 12 | 12 |
| Severe `+100` shift, primary checkpoint | 1 | 1 |
| Timing-only fit | 1 | 1 |
| Fit-target derangement fit | 1 | 1 |
| **Total** | **41** | **35** |

All shifts are nonwrapping and zero-filled. A positive offset delays signal
values; a negative offset advances them and is explicitly offline diagnostic
only. The channel derangement is a fixed-point-free cycle ordered with salt
`neurodecodekit-loop48-stage-b-v0-channel-cycle`. Whole-row derangement cycles
the already frozen primary predictions using salt
`neurodecodekit-loop48-stage-b-v0-check-row-cycle`.

The freeze record contains hashes, numerical telemetry, resource measurements,
and warnings. It contains no target or prediction text.

## Exact Statistical Rules

For each of the 11 check rows and comparator:

```text
d_i = comparator_CER_i - candidate_CER_i
```

Positive values favor the candidate. The scorer enumerates all `2^11 = 2,048`
sign assignments, including the observed assignment, and uses the mean paired
difference as its statistic. It reports the exact one-sided and two-sided
p-values; no random Monte Carlo approximation is used.

The primary practical threshold is `0.05` absolute macro sentence-CER. The
primary candidate is size 44, seed 4801.

### Diagnostic intact-signal conjunction

The primary candidate clears this conjunction only if it has at least `0.05`
macro-CER improvement and one-sided exact `p <= 0.05` against every one of:

1. size-44 no-signal prior;
2. exact-zero check signal;
3. whole-row prediction derangement;
4. channel derangement;
5. severe `+100` sample displacement;
6. timing-only fit; and
7. fit-target derangement fit.

This is an intersection-union rule. Every component must pass; a favorable
subset cannot rescue a failure. The conclusion remains E2 diagnostic evidence,
not an independent neural advantage.

### Registered-probe separability rule

`H4` uses only the already-frozen size-44 prediction sets. It compares all
three candidate seeds and all three linear seeds with the same size-44
train-only prior. `H4` receives support only when all six fits have finite,
stable telemetry and none of the six clears both the `0.05` macro-CER margin
and one-sided exact `p <= 0.05` against that prior. Evidence weighs against
`H4` only when either probe family clears both thresholds for all three seeds,
including primary seed 4801. Every other pattern is mixed or unresolved.

This rule does not call the linear model a simple task-locked character probe,
and it does not reuse the candidate-only corruption conjunction as if those
linear control predictions existed. A failure supports only nonseparability for
these two registered sequence probes at this sample size.

### Timing-sensitivity rule

Each of the four fine shifts is compared with zero shift. An off-center shift
supports `H3` only when:

- its primary-seed macro CER improves by at least `0.05`;
- its exact one-sided paired p-value is at most `0.0125`;
- the same CER direction holds for seeds 4802 and 4803; and
- no model, threshold, or future transform is selected from that result.

The `0.0125` threshold is the frozen Bonferroni correction for four shifts. A
positive result diagnoses timing sensitivity; it does not validate the shifted
or noncausal transform.

### Bounded data-regime rule

The primary curve is median-seed macro check CER against
`log2(8, 16, 24, 32, 44)`. `H6` receives support only when:

- the mean of size-8 and size-16 median CER exceeds the mean of size-32 and
  size-44 median CER by at least `0.05`; and
- every seed's ordinary-least-squares CER slope is negative.

Adjacent points need not all improve. Seed dispersion, blank fraction, and
size-32 to size-44 change are reported. No power law, asymptote, extrapolation,
or claim that more data will create an advantage is allowed.

## Frozen Hypothesis Interpretation

| ID | Support rule | Evidence against | Maximum result |
|---|---|---|---|
| `H1` | infeasible alignment, nonfinite telemetry, or all three size-8 seeds fail to improve fit CER over their prior by 0.05 while remaining at least 98% blank | all rows feasible and all three size-8 seeds improve fit CER by 0.05 with finite telemetry and below 98% blank | fixed recipe concern only |
| `H2` | a gross transformed-cache defect occurs | unavailable in this source because raw quality and task-locked simple-probe evidence are absent | E1 transformed-cache concern |
| `H3` | the corrected fine-shift rule passes | all four corrected comparisons fail with no consistent seed direction | timing sensitivity of this pipeline |
| `H4` | all three candidate and all three linear size-44 fits are stable, but none clears the prior margin and p-value | either probe family clears the prior margin and p-value for all three seeds | registered-probe nonseparability |
| `H5` | intact signal clears corruptions but fails the prior margin or p-value | intact clears the full conjunction including prior | prior dominance on this check split |
| `H6` | the bounded data-regime rule passes | small-to-large gain is below 0.02 and every seed slope magnitude is at most 0.01 CER per log2 unit | non-saturation or plateau only inside 8-44 rows |

Any other pattern is `mixed_or_unresolved`. Multiple hypotheses may receive
support. `T1` peripheral or task-locked shortcut dependence remains unresolved
under every possible Stage B outcome.

## Access Order

1. This preregistration and contract are tested, committed, pushed, and
   remotely green.
2. The exact authorization sentence is recorded in a separate tested commit,
   pushed, and remotely green.
3. The implementation and synthetic isolation tests are committed, pushed,
   and remotely green without protected input access.
4. A static gate binds the source, split, code, environment, resources, and
   44/11 membership without signal or target delivery.
5. The source cache receives exactly one SHA-256 pass.
6. The 44-row fit and 11-row target-free check-input derivatives are created.
7. Static quality and feasibility summaries complete.
8. Exactly 20 fits, 35 model inferences, five priors, and 41 prediction sets
   complete without check-target delivery.
9. One hash-only freeze record is tested, committed, pushed, and remotely
   green.
10. Exactly 11 check targets are delivered to one isolated scorer once.
11. Every hypothesis, control, curve, warning, resource, and unavailable field
    is emitted together, and the check partition is marked consumed for this
    protocol.
12. The run closes or parks without restart, post-check tuning, or rerun.

## Resource Caps

| Resource | Frozen cap |
|---|---:|
| CPU threads / workers / concurrent jobs | 1 / 1 / 1 |
| Candidate parameters | 2,908 |
| Parameter-update runs / steps | 20 / 4,800 |
| Model-inference runs / prediction sets | 35 / 41 |
| Parameter-update runtime | 600 sec total |
| End-to-end runtime | 900 sec total |
| Peak RSS | 1 GiB |
| Working arrays | 128 MiB |
| Checkpoints | 4 MiB total |
| Private prediction payloads | 4 MiB total |
| All generated artifacts | 32 MiB total |
| Required free disk before execution | 20 GiB |
| New data/model downloads | 0 bytes |

Loop 26 completed 21 fits and 24 inferences in 184.05 seconds at 522,797,056
bytes peak RSS with 10,126,825 generated bytes. The Stage B caps provide ample
measured headroom without expanding model size or storage. A cap breach parks
the run and cannot authorize cleanup or a retry.

## Exact Authorization Sentence

The future request must reproduce this sentence exactly:

```text
Authorize the Loop 48 Stage B train-only failure-discrimination implementation and one registered execution exactly as scoped in docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md and registries/loop48_train_only_discrimination_contract.v0.json. I authorize one SHA-256 pass over the named 10,632,576-byte S21 session-1 sentence cache; target-free reading of the bound split metadata; opaque sequential traversal of its deflated members; delivery of exactly 44 source-train signal/target rows and 11 source-train check signal rows into isolated derivatives; 20 bounded parameter-update runs, 35 target-blind model-inference runs, five train-only no-signal prior fits, 41 frozen prediction sets, and one conditional delivery and scoring of the same 11 source-train check targets only after the hash-only prediction-freeze record is committed, pushed, and remotely green. I authorize no validation or source-test row delivery or scoring, session 2, S7/S20/S25, raw FIF/MAT reads, new downloads, larger or additional models, restarts, language models, NeuroTokens, RW3, streams, devices, hardware, post-check tuning, claim upgrade beyond the registered E2 diagnostic ceiling, or rerun after check scoring.
```

General continuation, co-researcher status, the draft autonomy charter, the
consumed Stage A authorization, and the earlier Loop 26 authorization do not
substitute for this sentence.

## Primary-Source Basis

- Brain2Qwerty v2 reports that asynchronous CTC performance improved with both
  recording quantity and sentence diversity, while explicitly stating that
  its current full-sentence architecture is noncausal:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Brain2Qwerty v1 establishes task-locked motor and character information before
  sentence decoding and warns that overt typing and sentence-level processing
  do not establish real-time assistive use:
  https://www.nature.com/articles/s41593-026-02303-2
- Zeyer, Schlueter, and Ney show why CTC can converge to peaky blank-dominant
  behavior and why input-to-target ratio is diagnostically relevant:
  https://arxiv.org/abs/2105.14849
- Kessler, Enge, and Skeide show that preprocessing can materially change EEG
  decoding and that artifact-correlated performance can weaken biological
  interpretation:
  https://www.nature.com/articles/s42003-025-08464-3
- Varoquaux shows that predictive estimates from small neuroimaging samples
  have large uncertainty, motivating the explicit 11-row ceiling rather than
  treating it as a final test:
  https://pubmed.ncbi.nlm.nih.gov/28655633/
- Winkler et al. provide the exchangeability and sign-flipping basis for exact
  permutation inference in neuroimaging:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4010955/

These sources justify the questions and controls. They do not predict the Stage
B outcome or transfer Brain2Qwerty v2's large-data results to S21.

## Preregistration Access Ledger

```text
committed registry/document reads:          yes
public primary-source documents consulted:  6
ignored path-name listings:                 1
ignored file-content reads:                 0
source-cache stat/hash/member reads:         0
signal reads:                               0
target reads:                               0
checkpoint/private-prediction reads:         0
model inference runs:                       0
training or parameter-update runs:           0
generated experiment artifacts:             0
new download bytes:                         0
```

## Claim Boundary

Engineering capability preregistered: one bounded, single-thread, prediction-
frozen train-only protocol can discriminate six coexisting failure hypotheses
while keeping consumed validation, final-only participants, and private
historical outputs closed.

Scientific claim not established: no Stage B execution or result exists, and
this design establishes no neural advantage, independent validation,
brain-specific origin, decoding utility, unseen-person generalization,
real-time behavior, EEG or home-device performance, assistive value, or
clinical utility.
