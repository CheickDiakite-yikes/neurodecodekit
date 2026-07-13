# Loop 26 Shared S21 Validation Preregistration

Date: 2026-07-13

Status: **Preregistered; no implementation or protected execution is authorized**

Proof posture: **hash-bound prospective design plus legacy archive-access audit**

Machine contract: `registries/loop26_shared_validation_contract.v0.json`

Primary numbered gate: **Loop 26 Real Validation-Only Encoder Gate**

Shared planning bindings: **Loop 31 signal attribution, Loop 33 bounded data
scaling, and scientific-roadmap Loop 46**

## Decision

The project has only six S21 session-1 validation sentence instances that have
not been used for model fitting, restart selection, hyperparameter selection,
threshold choice, or predictive scoring. Spending them on Loop 26 alone would
make later Loop 31 attribution and Loop 33 scaling curves retrospective.

This preregistration therefore freezes one shared prospective event:

```text
freeze the Loop 26 model and primary gate
  -> freeze every Loop 31 signal-attribution condition
  -> freeze all Loop 33 prefix and seed predictions
  -> hash all 31 prediction sets without validation targets
  -> commit and remotely qualify the hash-only freeze record
  -> deliver the same six validation targets to one isolated scorer once
  -> report every registered condition together
  -> close or park without a restart or backup open
```

The result can become scientifically useful if it passes. It is still only a
one-person, one-session, prompted-typing validation result. The source test and
session 2 stay consumed and unavailable.

## The Archive-Access Correction

The existing Loop 14 cache is a 10,632,576-byte deflated NPZ. Its 66-by-102-by-
617 `signals.npy` member and each 66-row target member are monolithic. Deflate
compression does not permit row-selective random access.

The current `load_sentence_npz_cache` implementation copies every required
array before applying split indices. The Loop 14 tiny CTC and Loop 15 cross-
session commands therefore physically materialized all validation target bytes
even though those six rows were not passed to loss, model selection, metrics,
or reports. There are at least two prior full-cache loads; the exact historical
count is unavailable.

The old phrase "validation targets were unopened" is too strong and is
withdrawn for this experiment. The supported statement is:

> The six validation targets have not been used for model fitting,
> hyperparameter selection, restart selection, threshold choice, or predictive
> scoring.

This distinction matters. Physical byte access and algorithmic evidence use
are different claims. The new runtime must record both.

## Source Identity

No signal or target value was read while preparing this preregistration.
Filesystem stat, ZIP central-directory metadata, 12 NPY headers, and target-
free JSON sidecars supplied the following bindings.

| Field | Frozen value |
|---|---|
| Cache | `cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz` |
| Cache bytes | `10,632,576` |
| Cache SHA-256 | `45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815` |
| Cache shape | `66 x 102 x 617`, float32, 100 Hz |
| Split report SHA-256 | `cd0001b49666352919ea137859a6948a5e96c467def2e2b9c08be8c1c94574ef` |
| Protocol SHA-256 | `503ec4e77c64dea4b30b435e48fa0ec21279b61630dde5081a2a1e917388002d` |
| Group assignment SHA-256 | `ea978a8c43f627a38c3b79ecbc6e815202fc15083329b5d2f0c042e221242dba` |
| Semantic membership SHA-256 | `2382bd42f09630591ccbd1405e24e3aaf9035f8fec06eb05273a2596fde17dd7` |
| Physical membership SHA-256 | `4feb3854161c7f336a73c3d3ae5d7e67ac6ec11825de6370df1387c8f949ea85` |
| Ordered channel-name SHA-256 | `2befa0b191802432f1907e71ad727b4254f7c48f68c7572bf17df03000c50cc3` |
| Frozen scaler center SHA-256 | `d0beb18fe682042931ceda95ef5b6ba3fa66b57b93302c86fa3b11766bdb7a7d` |
| Frozen scaler scale SHA-256 | `e67ae077cc432be95d042900613b638e109843b845f50dee7fa96ecaf2807ee2` |
| Membership | 55 train / 6 validation / 5 consumed test rows |

The CTC vocabulary is blank zero, A-Z, and space. Text normalization uppercases,
collapses whitespace, strips the ends, and refuses any unsupported character.

## Causality Boundary

Loop 25 passed a target-free 1000-to-100 Hz causal mechanics gate. It did not
produce this S21 cache. The Loop 14 cache used whole-recording FFT resampling,
zero-phase filtering, sentence endpoints, and post-completion context.

Loop 26 may therefore call only the **model** causal. It may not call the
source cache, preprocessing path, complete decoder, or user experience causal,
online, streaming, real time, or low latency.

The model contract is:

```text
input [batch, 102 channels, time], float32
Conv1d(102 -> 16, kernel 1, bias)        1,648 parameters
GELU(approximate="none")                    0 parameters
left zero pad 2, right zero pad 0            0 parameters
Conv1d(16 -> 16, kernel 3, bias)            784 parameters
GELU(approximate="none")                    0 parameters
Conv1d(16 -> 28, kernel 1, bias)            476 parameters
---------------------------------------------------------------
total                                        2,908 parameters
```

Output length equals input length. Model right context is zero. Two hidden
frames, 20 ms at 100 Hz, form the left history. A streaming implementation
would need 128 bytes of float32 hidden state, but this experiment consumes
complete offline sentence tensors and does not measure streaming latency.

The required linear comparator is one `Conv1d(102 -> 28, kernel 1, bias)` with
2,884 parameters.

## Isolated Derivatives

The registered implementation may not call the legacy full-array loader. It
must use a bounded row-streaming NPY reader over `zipfile.ZipExtFile`:

1. Validate the cache, split, scaler, channel, code, and environment bindings.
2. Stream the physical cache SHA-256 exactly once.
3. Parse each NPY header before values and reject object dtype.
4. Derive allowed row indices from the precommitted split report.
5. Read fixed-size rows into one reusable byte buffer.
6. Deliver only allowed rows and overwrite discarded buffers before reuse.
7. Never create any source-test derivative.

Before scoring, it may create only:

- a 55-row train bundle containing signals and train targets; and
- a six-row validation-input bundle containing signals, lengths, IDs, and no
  targets.

After every prediction is frozen and its hash-only record is committed, pushed,
and remotely green, the same reader may make one second target-member traversal
that delivers only the six validation targets to the scorer. Deflate still
requires opaque traversal of excluded bytes. The runtime must report that
truth; it may not rename archive traversal physical nonaccess.

Every derivative stays under `.codex_work/loop26`, remains ignored, and records
its hash, bytes, shape, dtype, row-ID hash, membership hash, warnings, and
access counters. No cache, target bundle, checkpoint, or prediction payload may
enter Git.

## Training Contract

Execution is CPU-only with one numerical thread and one worker. Environment
drift from Python 3.13.5, NumPy 2.5.0, Torch 2.13.0, or SciPy 1.18.0 requires an
amendment before protected access.

Every parameterized fit uses:

```text
optimizer: Adam
learning rate: 0.02
betas: (0.9, 0.999)
epsilon: 1e-8
weight decay: 0
AMSGrad: false
batch-size ceiling: 16
optimizer steps: exactly 240
CTC blank: 0
CTC reduction: mean
zero_infinity: false
gradient clipping: none
early stopping: none
restart: none
checkpoint: state after step 240 only
```

The reader cycles deterministic epoch permutations until the exact 240th
optimizer step. Each prefix therefore has the same update count, while the
report records its actual example presentations. Nonfinite loss or an
impossible CTC alignment fails the gate without a restart.

Torch deterministic algorithms are required with `warn_only=False`. This
provides same-software-and-hardware determinism where supported; it is not a
cross-machine reproducibility claim.

## Shared Run Budget

Fresh seeds are `2601`, `2602`, and `2603`. Seed 2601 is the primary Loop 26
candidate. There is no favorable-seed selection.

| Family | Fits |
|---|---:|
| Six nested candidate prefixes x three seeds | 18 |
| Full-size train-target derangement | 1 |
| Full-size timing-only model | 1 |
| Full-size linear signal comparator | 1 |
| **Total parameter-update runs** | **21** |
| Train-only no-signal prior fits | 6 |
| Total optimizer steps | 5,040 |

The full-size seed-2601 candidate is reused as Loop 31 `E00`; it is not trained
again. Zero-signal, channel-deranged, and time-displaced conditions reuse that
checkpoint. Whole-row derangement remaps an already frozen prediction vector
and performs no model run.

The exact target-blind inventory is:

```text
18 candidate curve prediction sets
 6 size-matched no-signal prior sets
 7 additional Loop 31 control prediction sets
------------------------------------------------
31 prediction sets, each containing the same six ordered item IDs
```

There are 24 logical target-blind model-inference runs. All 31 prediction sets
must exist before target scoring.

## Loop 31 Conditions

| ID | Condition | Fit or reuse | Gate role |
|---|---|---|---|
| `L31-E00` | Full signal, size 55, seed 2601 | reuse curve checkpoint | primary candidate |
| `L31-E01` | Train-only most-frequent sentence prior | no neural fit | primary signal-free comparator |
| `L31-E02` | Exact-zero valid signal | reuse E00 | required |
| `L31-E03` | Whole validation rows deranged | remap E00 predictions | required |
| `L31-E04` | Channel-name-hash derangement | reuse E00 | required |
| `L31-E05` | +100-sample nonwrapping time displacement | reuse E00 | required |
| `L31-E06` | Timing-only train-fit candidate | separate fit | required |
| `L31-E07` | Prompt or sentence-list only | unavailable; assert absent | conditional, forbidden here |
| `L31-E08` | Train signal-target pairing derangement | separate fit | required |
| `L31-E09` | 2,884-parameter linear signal CTC | separate fit | required architecture comparator |

The exact cyclic derangements, salts, fixed-point rules, timing construction,
zero fill, and boundary-loss accounting are frozen in the machine contract.
No validation target may choose a permutation, offset, channel map, or timing
feature.

Even if every condition passes, the result can establish at most **sensor-
signal dependence** for this exact slice. It cannot establish brain-specific
origin before Loop 35 records synchronized peripheral controls.

## Loop 33 Curve

The nested unique-sentence prefixes are:

```text
8, 16, 24, 32, 44, 55
```

Rows are ordered by a frozen SHA-256 key over the prefix salt, semantic row ID,
and performed-row ID. The final prefix must equal all 55 train rows. Targets or
validation metrics may not change the order.

At every size, report each seed and the size-matched no-signal prior. The
primary curve is median seed macro sentence CER versus
`log2(unique_train_sentences)`.

The bounded curve passes only if:

- the mean of the size-8 and size-16 median CERs exceeds the mean of the size-
  44 and size-55 median CERs by at least 0.05;
- the size-55 median candidate beats its matched prior by at least 0.05; and
- every registered seed's ordinary least-squares CER slope is negative.

Adjacent points need not all improve. No formal slope p-value, power-law fit,
asymptote, extrapolation, physical-repetition claim, or acquisition permission
is available.

## Scoring Gate

For each validation sentence and comparator:

```text
d_i = comparator CER_i - candidate CER_i
```

Positive values favor the candidate. The scorer enumerates all 64 sign flips
of the six differences in binary order and uses their mean as the statistic.
It reports the exact one-sided greater p-value and the corresponding two-sided
value.

The primary candidate-versus-prior gate requires all of:

1. macro sentence CER improvement of at least 0.05;
2. six strict candidate sentence wins;
3. one-sided exact `p <= 0.05`;
4. every required Loop 31 exact component also has one-sided `p <= 0.05`;
5. candidate macro CER is strictly lower than the linear comparator; and
6. every access, hash, resource, and prediction-freeze gate passes.

This is an intersection-union decision: no favorable subset can rescue one
failed required control. A missing condition is a failure, not zero or
unavailable performance.

The report also includes corpus CER, corpus WER, exact sentences, blank
fraction, wins/ties/losses, all six per-item edits and CERs, all 64 null
statistics, runtime, RSS, bytes, and every unavailable field. Committed reports
contain hashed item IDs and numerical errors, never target or prediction text.

## Access Order

The execution order is immutable:

1. This preregistration is tested, committed, pushed, and remotely green.
2. The exact authorization sentence is recorded in a separate tested commit,
   pushed, and remotely green.
3. Implementation and synthetic isolation tests are committed, pushed, and
   remotely green before any real-cache content read.
4. The static identity, archive, split, scaler, channel, code, environment, and
   resource gate passes.
5. One source-cache hash pass occurs.
6. The isolated train bundle and target-free validation-input bundle are made.
7. All 21 fits, 24 target-blind model inferences, six prior fits, and 31
   prediction sets complete.
8. Every checkpoint, transform, configuration, item order, prediction payload,
   length vector, warning, and access ledger is hash-frozen.
9. A hash-only freeze record is tested, committed, pushed, and remotely green.
10. Exactly six validation targets are delivered to one scorer once.
11. Every condition is scored together and the protocol is marked consumed.
12. The branch closes or parks without restart, retuning, backup open, source-
    test open, session-2 open, or rerun.

## Resource Caps

| Resource | Frozen cap |
|---|---:|
| CPU threads / workers | 1 / 1 |
| Candidate parameters | 2,908 |
| Parameter-update runtime | 1,200 sec total |
| End-to-end runtime | 1,500 sec total |
| Peak RSS | 1 GiB |
| Working arrays | 128 MiB |
| Checkpoints | 4 MiB total |
| Prediction payloads | 2 MiB total |
| All generated artifacts | 32 MiB total |
| New data/model downloads | 0 bytes |

Direct energy measurement is unavailable. CPU time is not reported as energy.

## Exact Authorization Sentence

The future request must reproduce this sentence exactly:

```text
Authorize the Loop 26/31/33 shared S21 validation implementation and one registered execution exactly as scoped in docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md and registries/loop26_shared_validation_contract.v0.json. I authorize one hash pass over the named monolithic S21 session-1 cache; opaque streaming traversal of its deflated row members; delivery of exactly 55 train signal/target rows and six validation signal rows into isolated derivatives; 21 bounded training runs, 24 target-blind model-inference runs, six train-only no-signal prior fits, 31 frozen prediction sets, and one conditional scoring delivery of the same six validation targets only after the prediction-freeze hash record is committed, pushed, and remotely green. I do not authorize delivery or scoring of the five source-test rows or session 2, raw FIF/MAT reads, S7/S20/S25, downloads, larger models, restarts, language models, RW3, streams, devices, hardware, post-target tuning, or any rerun after validation scoring.
```

Reviewing, merging, planning, continuing, or granting general research autonomy
does not substitute for that exact execution decision. The future authorization
record must hash-bind this green contract.

## Preregistration Access Ledger

```text
source-cache stat reads:                    1
ZIP central-directory reads:                1
successful NPY header reads:               12
signal value reads:                         0
target value reads:                         0
raw FIF/MAT reads:                          0
model/checkpoint runs:                      0
training runs / parameter updates:          0 / 0
validation/source-test/session-2 scoring:   0 / 0 / 0
external data or model download bytes:      0
generated experiment payload bytes:         0
```

Six high-level public-web operations inspected the pinned Brain2Qwerty source,
PyTorch 2.13 CTC and deterministic-algorithm documentation, and SciPy 1.18
exact permutation semantics. Exact transferred web bytes are unavailable.

One broad local documentation search displayed lines from the user-owned,
untracked workbook inspection sidecar. The file was not modified, staged, or
used as scientific evidence. All later searches explicitly exclude it.

## Outcome Rules

- If any static identity or isolation gate fails, do not open cache values.
- If target-blind training or prediction freeze fails, keep validation scoring
  unavailable and park.
- If any primary or required control gate fails, park real-model scaling and
  move to Loop 48 failure localization without opening test, session 2, or S25.
- A positive curve does not authorize a download.
- No outcome authorizes a larger model, language model, RW3, device, hardware,
  participant, or home recording.

## What This Preregistration Proves

It proves that the next scarce validation event has a complete, auditable
design before any new model, protected cache value, target score, or scientific
result exists. It also corrects the legacy physical-access wording and gives
future code a stricter isolation boundary.

## What It Does Not Prove

There is still no positive neural advantage, sensor-signal dependence, brain-
specific contribution, bounded scaling result, source-test performance,
cross-session benefit, unseen-person generalization, causal end-to-end path,
real-time decoding, EEG or portable-device result, at-home use, arbitrary-
thought decoding, assistive efficacy, or clinical capability.

## Primary Sources

- Brain2Qwerty v2 source at pinned commit `3bf5a4099ca0d23bbe994b2287905760236e56e0`:
  https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2
- PyTorch 2.13 CTC loss:
  https://docs.pytorch.org/docs/2.13/generated/torch.nn.CTCLoss.html
- PyTorch 2.13 deterministic algorithms:
  https://docs.pytorch.org/docs/2.13/generated/torch.use_deterministic_algorithms.html
- SciPy 1.18 exact permutation test:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- Intersection-union tests: https://doi.org/10.1214/ss/1032280304
- Label and feature permutation controls:
  https://www.jmlr.org/papers/v11/ojala10a.html
- Confound-aware decoding interpretation:
  https://doi.org/10.1016/j.neuroimage.2018.09.074
