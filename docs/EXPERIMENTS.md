# Experiment Plan

## Experiment 0 — synthetic smoke loop

Purpose: prove the code path works before using real neural data.

Command:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 128 --channels 8 --times 25
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
neurodecode report --cache cache/synthetic_tiny.npz --identity-smoke --out-json cache/synthetic_report.json --out-md cache/synthetic_report.md
neurodecode prior-baseline --cache cache/synthetic_tiny.npz --out-predictions cache/prior_predictions.txt --out-json cache/prior_report.json --out-md cache/prior_report.md --run-name synthetic_prior_most_frequent --split synthetic-smoke
```

Acceptance:

- file is created
- shape is printed
- cache loads through the schema v0 loader
- metadata sidecar contains schema, dimensions, warnings, and transformations
- report command writes JSON and Markdown
- prior-only baseline writes predictions and a standard report
- metrics module works on sample text
- no heavy dependencies required except NumPy for shard creation

## Experiment 1 — path manifest

Purpose: verify data discovery and selection logic without downloading real data.

Command:

```bash
neurodecode list-hf-files --repo-id bcbl190626/SpanishBCBL --out data/spanishbcbl_files.txt
neurodecode manifest-from-paths --paths data/spanishbcbl_files.txt --out data/spanishbcbl_manifest.jsonl
neurodecode inspect-manifest --manifest data/spanishbcbl_manifest.jsonl
```

Acceptance:

- MEG raw `.fif` files are recognized
- EEG BrainVision files are recognized
- `.mat` logs are recognized
- subject IDs are inferred
- summary counts are sensible

## Experiment 2 — tiny selective download dry run

Purpose: create a safe tiny selection.

Command:

```bash
neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest.jsonl \
  --modality MEG \
  --out data/tiny_selection.json \
  --max-files 4 \
  --max-total-gb 2
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny
```

Acceptance:

- selection includes only one raw block and relevant logs
- total planned files are printed
- exact planned paths and size metadata are printed
- no data is downloaded unless the user passes `--execute`
- real execution fails safely if selected sizes are unknown and `--allow-unknown-size` is not passed

## Experiment 3 — one real block to windows

Purpose: first real neural preprocessing.

Proposed command:

```bash
neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../logs.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3
```

Acceptance:

- MNE loads the block
- event parser finds keystrokes
- output shape is [events, channels, times]
- report includes bytes before/after preprocessing
- cache loads through `neurodecode load-cache`
- metadata records source files, extraction params, warnings, and transformations

## Experiment 4 — first real baseline

Purpose: honest sanity check.

Baselines:

- majority/frequency character baseline (implemented as `prior-baseline`)
- keyboard-neighbor baseline
- template classifier
- small ConvNet only after the first three are done

Required report:

```text
CER
WER
keyboard-distance error
example predictions
storage footprint
runtime
```

Before real baselines exist, use `neurodecode report` with explicit target and
prediction files:

```bash
neurodecode report \
  --targets outputs/run_001/targets.txt \
  --predictions outputs/run_001/predictions.txt \
  --cache cache/b2qmini_s1_block1.npz \
  --out-json outputs/run_001/metrics.json \
  --out-md outputs/run_001/report.md \
  --run-name run_001 \
  --split subject-or-session
```

`--identity-smoke` is allowed only as a plumbing check. It copies targets into
predictions and is not a decoder baseline.

The prior-only baseline is the first real comparator:

```bash
neurodecode prior-baseline \
  --targets outputs/run_001/targets.txt \
  --train-targets outputs/train_targets.txt \
  --out-predictions outputs/run_001/prior_predictions.txt \
  --out-json outputs/run_001/prior_report.json \
  --out-md outputs/run_001/prior_report.md \
  --run-name run_001_prior_only \
  --split subject-or-session
```

If `--train-targets` or `--train-cache` is omitted, the command emits
`prior_fit_on_eval_targets_for_smoke_only`. That is acceptable for plumbing
smoke tests, not for real baseline claims.

The first neural-window comparator is the template baseline:

```bash
neurodecode template-baseline \
  --cache cache/b2qmini_s1_block1.npz \
  --train-fraction 0.5 \
  --out-predictions outputs/run_001/template_predictions.txt \
  --out-json outputs/run_001/template_report.json \
  --out-md outputs/run_001/template_report.md \
  --run-name run_001_template_nearest_centroid \
  --split subject-or-session-holdout
```

For real comparisons, prefer explicit train/eval caches when split metadata is
available:

```bash
neurodecode template-baseline \
  --train-cache cache/train_block.npz \
  --eval-cache cache/eval_block.npz \
  --out-json outputs/run_001/template_report.json \
  --out-md outputs/run_001/template_report.md
```

The first optional neural-window baseline is the tiny ConvNet:

```bash
pip install -e ".[ml]"

neurodecode tiny-conv-baseline \
  --cache cache/b2qmini_s1_block1.npz \
  --train-fraction 0.75 \
  --epochs 30 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --out-predictions outputs/run_001/tiny_conv_predictions.txt \
  --out-json outputs/run_001/tiny_conv_report.json \
  --out-md outputs/run_001/tiny_conv_report.md \
  --run-name run_001_tiny_conv \
  --split subject-or-session-holdout
```

For real comparisons, prefer explicit train/eval caches:

```bash
neurodecode tiny-conv-baseline \
  --train-cache cache/train_block.npz \
  --eval-cache cache/eval_block.npz \
  --epochs 30 \
  --out-json outputs/run_001/tiny_conv_report.json \
  --out-md outputs/run_001/tiny_conv_report.md
```

This command uses PyTorch and is intentionally optional. It should be reported
beside the no-brain prior and template baselines. A tiny synthetic win is only a
plumbing signal, not evidence of real Brain2Qwerty performance.

## Experiment 5 - continuous sentence CTC

Purpose: prove variable-length asynchronous sequence plumbing before a real
decoder experiment.

Synthetic command:

```bash
neurodecode make-synthetic-sentence-cache \
  --out cache/loop9_synthetic_sentences.npz \
  --sentences 96 \
  --channels 6 \
  --seed 17

neurodecode tiny-ctc-baseline \
  --cache cache/loop9_synthetic_sentences.npz \
  --train-fraction 0.8 \
  --epochs 60 \
  --learning-rate 0.02 \
  --num-threads 1 \
  --max-restarts 3 \
  --out-predictions cache/loop9_synthetic_ctc_predictions.txt \
  --out-json cache/loop9_synthetic_ctc_report.json \
  --out-md cache/loop9_synthetic_ctc_report.md
```

Real cache-only command:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/b2qsentence_s21_session1_block1_16ch_100hz.npz \
  --sfreq 100 \
  --picks meg \
  --max-channels 16
```

Acceptance:

- synthetic input and target lengths vary
- target IDs round-trip to target text
- text-hash split prevents sentence leakage
- CTC trains with CPU and one thread
- report includes blank fraction, CER, resources, and no-brain comparator
- 20-seed smoke matrix has no failed synthetic run
- real cache contains all 66 validated trial IDs and zero padding tails
- real extraction reports runtime, bytes, and peak memory
- no real model result is claimed from one block

Observed details: `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.

## Experiment 6 - sampling-rate resource sweep

Purpose: measure local storage, preprocessing resources, timing quantization,
signal summaries, and CTC length feasibility before using a lower sampling
rate in a model.

```bash
neurodecode sampling-rate-sweep \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out-dir cache/loop10_s21_sampling_rate_sweep \
  --rates 100 50 25 \
  --picks meg \
  --max-channels 16
```

Acceptance:

- rates execute sequentially in isolated one-thread workers
- each cache validates under `b2q-sentence-cache` v0
- trial IDs, all three text views, and channel names match exactly
- report includes effective bandwidth and sample-grid precision
- report excludes padding from signal summaries
- report computes repeated-character-aware CTC minimum lengths
- output artifacts are not overwritten silently
- no neural accuracy or rate winner is claimed from one real block

Observed:

```text
100 Hz: 1,663,209 bytes, 4.121 sec, 66/66 CTC feasible
 50 Hz:   846,334 bytes, 3.586 sec, 66/66 CTC feasible
 25 Hz:   431,451 bytes, 3.539 sec, 66/66 CTC feasible
total: 2.80 MiB caches, 11.778 sec, about 586 MiB peak worker RSS
decision: resource_characterized_no_rate_selected
official v2 k16/s4 feasibility: 100 Hz 66/66; 50 Hz 66/66; 25 Hz 0/66
```

Full method and interpretation: `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

## Experiment 7 - channel/sensor subset resource and proxy sweep

Purpose: replace the arbitrary first-channel smoke subset with an inspectable
whole-head magnetometer base, then compare storage, device-coordinate coverage,
post-scaling marginal variance, and selection overlap without training on one
real block.

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --sfreq 100 \
  --picks mag \
  --max-channels 102 \
  --summary-json cache/loop11_s21_channel_subset/base_102mag_100hz.extraction.json

neurodecode channel-subset-sweep \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --out-dir cache/loop11_s21_channel_subset/subsets \
  --counts 76 51 25 16 8 \
  --strategies spatial-fps variance random first \
  --seed 17 \
  --max-output-mb 128
```

Acceptance:

- raw extraction picks channels before loading signal samples
- every base channel records finite device-coordinate geometry
- all strategies are deterministic and nested
- original base channel order is preserved inside written caches
- preflight refuses projected output above the explicit cap
- all 20 subset caches validate under `b2q-sentence-cache` v0
- trial IDs, three text views, targets, timing, and exact signal slices match
- variance excludes padding and is labeled as same-block/post-scaling
- geometry is labeled as device coverage, not cortical localization
- no decoder, channel-count winner, or OPM-equivalence claim is produced

Observed:

```text
base: 66 x 102 x 617, 10,602,568 bytes, 12.004 sec, 1.56 GiB peak RSS
subsets: 20 caches, 70.3 MiB cache+sidecar bytes, 3.492 sec, 258 MiB peak RSS
16ch FPS:      14.8% variance; 34.9/69.8 mm mean/max coverage
16ch variance: 21.3% variance; 56.6/140.3 mm mean/max coverage
16ch first:    14.7% variance; 102.2/219.3 mm mean/max coverage
FPS/variance overlap at 16 channels: 2 channels, Jaccard 0.067
decision: carry_two_candidates_to_future_accuracy_test
```

Full method and interpretation:
`docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.

## Experiment 8 - precision/storage representation sweep

Purpose: compare physical cache representations on fixed, already validated
sentence signals while keeping reconstruction distortion, decoder accuracy,
and model arithmetic as separate claims.

```bash
neurodecode precision-storage-sweep \
  --cache \
    cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
    cache/loop11_s21_channel_subset/subsets/subset_spatial-fps_16ch.npz \
    cache/loop11_s21_channel_subset/subsets/subset_variance_16ch.npz \
  --out-dir cache/loop12_s21_precision_storage \
  --variants float32 float16 bfloat16 qint16 qint8 \
  --clip-abs 5 \
  --repetitions 3 \
  --max-output-mb 96
```

Acceptance:

- float32 is required as the lossless reference
- at least one packed candidate is required
- preflight refuses projected artifacts above the explicit cap
- integer encodings use an explicit fixed range and refuse implicit clipping
- packed payload dtype, scale, rounding, and provenance are inspectable
- every artifact decodes to the semantic sentence-cache interface
- every non-signal array and semantic metadata object matches exactly
- zero padding remains exact after decode
- valid-region numeric, temporal-difference, per-channel, and bandpower errors
  are reported
- encode, write, decode, load, bytes, and peak RSS are reported
- no decoder or retained-accuracy claim is produced

Observed:

```text
15 representations, 34.4 MiB caches+sidecars, 3.789 sec, 367.5 MiB peak RSS
qint16: 49.84% smaller than float32; worst relative RMSE 0.003693%
qint8: 80.75% smaller than float32; worst relative RMSE 0.9531%
source values outside fixed range: 0
decision: float32 default; qint16/qint8 future held-out-test candidates
```

Full method and interpretation:
`docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.

## Experiment 9 - measured NPZ access / lazy-backend gate

Purpose: decide whether current complete or partial NPZ access is materially
limiting before adding another cache backend.

```bash
neurodecode lazy-backend-gate \
  --cache \
    cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
    cache/loop11_s21_channel_subset/subsets/subset_spatial-fps_16ch.npz \
    cache/loop11_s21_channel_subset/subsets/subset_variance_16ch.npz \
    cache/loop12_s21_precision_storage/base_102mag_100hz__qint16.npz \
    cache/loop12_s21_precision_storage/base_102mag_100hz__qint8.npz \
    cache/loop12_s21_precision_storage/subset_spatial-fps_16ch__qint16.npz \
    cache/loop12_s21_precision_storage/subset_spatial-fps_16ch__qint8.npz \
    cache/loop12_s21_precision_storage/subset_variance_16ch__qint16.npz \
    cache/loop12_s21_precision_storage/subset_variance_16ch__qint8.npz \
  --out-dir cache/loop13_lazy_backend_gate \
  --row-counts 1 8 \
  --repetitions 5
```

Acceptance:

- each operation runs in a fresh subprocess with numerical threads capped at 1
- standard and packed caches use the same semantic signal interface
- complete, one-row, and eight-row decoded signals match exact SHA-256 values
- full and partial median time, peak RSS, and compressed bytes are reported
- thresholds are explicit local budgets, not universal format rules
- existing reports are not overwritten silently
- no raw FIF, decoder training, or neural-accuracy claim is involved
- Zarr is compared only if at least one declared gate fails

Observed:

```text
9/9 caches pass all gates and exact decoded-signal identity
largest cache: 10.1 MiB
slowest full median: 60.386 ms
slowest partial median: 53.634 ms
highest worker peak RSS: 140.6 MiB
runtime: 5.358 sec
new backend/cache bytes: 0
decision: park optional Zarr; retain bounded per-block NPZ
```

Full method and interpretation: `docs/LOOP_13_LAZY_BACKEND_GATE.md`.

## Experiment 10 - Split Protocol v1 membership and fit-scope audit

Purpose: reproduce deterministic sentence-text membership, expose unsupported
generalization levels, and detect preprocessing leakage before a real decoder
comparison.

```bash
neurodecode split-protocol \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --out-dir cache/loop14_s21_split_protocol \
  --text-normalization official-exact
```

Acceptance:

- match pinned NeuralSet 0.2.2 float-seed assignment semantics
- record algorithm, ratios, seed, normalization mode, and durable hashes
- keep repeated sentence groups inside one partition
- detect duplicate semantic rows across standard/packed representations
- label event, sentence, session, and canonical-subject capabilities separately
- audit robust scaling and variance selection for train-only fit declarations
- read no signal array and write no signal cache
- produce no decoder, CER, WER, or retained-accuracy claim

Observed:

```text
66 unique exact reference groups
train/validation/test: 55/6/5
requested/canonical text crossings: 0/0
duplicate semantic rows: 0
session/person groups: 1/1, both unavailable for 3-way evaluation
signal members loaded: false
runtime: 0.039339 sec
report bytes: 63,438
decision: membership_valid_strict_fit_scope_not_ready
```

Full method and interpretation: `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

## Experiment 11 - train-only cache and strict paired baselines

Purpose: resolve Experiment 10's fit-scope failure and measure the first fixed
neural baseline against a no-signal comparator without selecting on test rows.

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --picks mag --max-channels 102 \
  --scaler-fit-scope train \
  --split-text-normalization official-exact
```

Acceptance:

- assign split membership before any data-dependent scaler fit
- fit median/IQR on valid train-row samples only
- preserve exact zero padding and all non-signal arrays
- bind scaler provenance to protocol and semantic-membership hashes
- require a strict-ready report and exact physical-cache hash before training
- reserve validation rows and keep one fixed CTC initialization/configuration
- run the same train/test membership through a signal-free prior
- report paired uncertainty and refuse a neural advantage claim when unresolved

Observed:

```text
strict fit finding: 1 pass, 0 unresolved/failed
train/validation/test: 55/6/5
train scaler fit: 23,669 valid timepoints; 102 channels; 0 zero-IQR
cache: 10,632,576 bytes; 10.969796 sec; 1,746,010,112 bytes peak RSS
prior test: 164 edits; CER 0.953488
tiny CTC test: 163 edits; CER 0.947674
tiny train CER / test blank fraction: 0.925469 / 0.868132
tiny-minus-prior CER delta: -0.005814
paired bootstrap 95% interval: [-0.197279, 0.130653]
decision: close protocol; model conclusion near-null
```

Full method and interpretation: `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

## Experiment 12 - pinned second session and fixed cross-session baseline

Purpose: validate one complete same-subject second recording, apply only frozen
source-train normalization, and measure the unchanged tiny CTC against a
signal-free prior without touching source validation/test rows.

```bash
neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest_with_sizes.jsonl \
  --out data/s21_session2_block1_selection.json \
  --modality MEG --subject S21 --session 2 \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --max-files 3 --max-total-gb 2.5

neurodecode apply-frozen-scaler \
  --source-cache cache/loop15_s21_cross_session/session2_unscaled_102mag_100hz.npz \
  --fit-cache cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --out cache/loop15_s21_cross_session/session2_session1_train_scaled_102mag_100hz.npz

neurodecode cross-session-ctc \
  --train-cache cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --train-split-report cache/loop14_s21_split_aware/split/split.json \
  --eval-cache cache/loop15_s21_cross_session/session2_session1_train_scaled_102mag_100hz.npz \
  --num-threads 1 --max-restarts 1
```

Acceptance:

- pin the dataset revision and exact known-size file plan
- include required FIFF split continuations under the same byte/file caps
- verify MNE opens all pieces as one continuous recording
- reconcile raw completed trials with nonempty MAT `keyTrig` slots without
  fuzzy text assignment or trial imputation
- preserve skipped MAT trial IDs in the sentence cache
- require exact channel/preprocessing compatibility before frozen scaling
- verify fit-cache, source-cache, split, semantic-membership, center, and scale
  hashes
- train only on source train rows; reserve source validation and test rows
- evaluate every independent-session performed row once
- compare with a no-signal prior and record paired uncertainty
- stop and preserve the negative result rather than tuning on the holdout

Observed:

```text
download: 3 files; 2,516,384,765 bytes; one worker; 2.5-GiB cap
recording: 2 FIFF parts; 977.051 sec; 312 channels; 3,524 stim events
trial map: 63 raw rows -> 63 nonempty slots; skipped MAT [54, 58, 60]
timing: 2,529 pairs; median/p95 0.296/0.945 ms
unscaled cache: 63 x 102 x 1,636; 14,179,453 bytes; 14.228 sec
frozen-scaled cache: 13,543,399 bytes; 0 session-2 fit rows
source train/validation/test: 55/6/5; validation/test unused
session-2 eval: 63 rows; zero exact train-text or prompt overlap
prior: 2,117 edits; CER 0.775458
tiny CTC: 2,506 edits; CER 0.917949; train CER 0.925469
tiny-minus-prior: +0.142491 CER; paired CI [+0.119386, +0.166069]
decision: protocol passes; fixed model fails cross-session generalization
```

Full method and interpretation:
`docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## Experiment 13 - synthetic robust channel-affine adapter gate

Purpose: test the lightest unlabeled session-normalization contract without
reopening the consumed real session or the five real source-test rows.

```bash
neurodecode synthetic-adapter-gate \
  --out-dir cache/loop15_synthetic_adapter_gate \
  --sentences 96 --channels 6 --letter-classes 4 \
  --seed 23 --epochs 50 --num-threads 1 \
  --min-validation-cer-gain 0.10 --bootstrap-iterations 2000
```

Acceptance:

- use disjoint 64/16/16 synthetic train/validation/holdout rows
- fit the CTC on source train only
- fit target robust statistics without labels
- select identity versus adaptation on validation before holdout
- keep real source-test and session-2 rows unloaded
- require at least 0.10 absolute validation CER gain
- improve the frozen synthetic holdout and preserve zero padding
- report a no-signal prior, paired uncertainty, resources, and exact limits

Observed:

```text
validation identity/adapted CER: 0.327273 / 0.000000
holdout identity/adapted/prior CER: 0.344828 / 0.000000 / 0.577586
adapted-minus-identity paired CI: [-0.408696, -0.286957]
adapted-to-identity reconstruction MAE ratio: 1.87e-7
runtime / artifacts / new cache: 2.498 sec / 21,354 bytes / 0 bytes
decision: synthetic_gate_passed_select_robust_channel_affine
```

Full method and interpretation:
`docs/LOOP_15_STAGE_B_SYNTHETIC_ADAPTER.md`.

## Experiment 14 - synthetic calibration curve and drift stress

Purpose: estimate the smallest unlabeled synthetic calibration set for the
robust channel-affine adapter and identify where its diagonal/stationary
assumptions fail, without opening any real holdout.

```bash
neurodecode synthetic-calibration-curve \
  --out-dir cache/loop16_synthetic_calibration_curve \
  --sentences 96 --calibration-sentences 48 \
  --calibration-sizes 1,2,4,8,16,32 \
  --shift-seeds 101,211,307 \
  --epochs 50 --num-threads 1 \
  --min-stationary-validation-cer-gain 0.10 \
  --bootstrap-iterations 1000 --max-output-mb 4
```

Acceptance:

- use at least five nested calibration sizes and multiple shift seeds
- use an independent calibration text pool with zero source overlap
- pass no target labels to adapter fitting
- include stationary diagonal, non-diagonal channel-mixing, and within-row
  time-varying shifts
- select calibration size on validation before one holdout pass
- fit the decoder once for all validation views and replay identically for
  holdout
- preserve exact padding; keep real holdouts unloaded
- report CER curves, paired uncertainty, runtime, memory, bytes, and limits

Observed:

```text
calibration sizes / shift seeds / families: 6 / 3 / 3
registered stationary selection: 1 row = 1.26 synthetic sec
stationary holdout identity/adapted/prior CER: 0.422414 / 0.232759 / 0.577586
stationary seed outcomes: 2 improve, 1 tie
channel-mixing holdout identity/adapted CER: 0.568966 / 0.862069; 0/3 non-harm
time-varying holdout identity/adapted CER: 0.439655 / 0.603448; 0/3 non-harm
runtime / peak RSS / artifacts / new cache: 1.897 sec / 309,493,760 bytes / 158,256 bytes / 0
decision: loop16_complete_select_1_unlabeled_rows_for_stationary_diagonal_synthetic_shift
```

Full method and interpretation:
`docs/LOOP_16_SYNTHETIC_CALIBRATION_CURVE.md`.

## Experiment 15 - honest local artifact-backed demo

Purpose: determine whether one local command can make the existing proof
boundary understandable without model training, raw-data access, or real
sentence disclosure.

```bash
neurodecode demo --audit-only --out-json cache/loop17_demo/audit.json
neurodecode demo --host 127.0.0.1 --port 7860
```

Acceptance:

- load and hash the six compact Loop 9/14/15/16 artifacts
- reject cache/prediction/report disagreement
- expose at least one signal, target, prediction, and CER/WER example
- make synthetic, aggregate-only real, noncausal, task-specific, and
  confidence-unavailable boundaries visible
- trigger no network fetch, real model run, raw-neurodata read, or cache write
- measure startup time and peak RSS under bounded threads
- exercise example selection, edited rescoring, restore, evidence, and
  provenance paths in a real browser
- pass desktop and 390 px mobile layout checks with no console errors

Observed:

```text
held-out synthetic examples: 19
aggregate evidence rows / provenance artifacts: 6 / 6
startup build / peak RSS: 1.644 sec / 224,837,632 bytes
source cache: 136,734 bytes
components / callbacks: 27 / 4
startup checks: 8/8 passed
desktop/mobile page overflow: false / false
browser console errors or warnings: 0
new cache / real model runs / raw reads / network fetches: 0 / 0 / 0 / 0
decision: loop17_complete_artifact_evidence_console
```

Full method and interpretation:
`docs/LOOP_17_HONEST_LOCAL_DEMO.md`.

## Experiment 16 - versioned report cards and cohort-local leaderboard

Purpose: determine whether compact saved experiments can become a reproducible
evidence index without model reruns, cache access, or invalid cross-task ranks.

```bash
neurodecode build-leaderboard \
  --spec configs/loop18_leaderboard.json \
  --project-root . \
  --out-dir cache/loop18_leaderboard \
  --max-cards 16 --max-output-mb 2
```

Acceptance:

- versioned spec, report-card, leaderboard, and audit contracts
- metrics, cohort/split/proof, method, comparator, resources, config, cache
  metadata, source hash, and missing-field flags
- at least three saved baselines with no retraining
- deterministic JSON/Markdown/CSV and dependency-free CLI table
- malformed, duplicate, capped, existing-output, and mixed-version failures
- no global rank across incomparable cohorts
- no raw/cache/signal access, model run, network fetch, or holdout reopening

Observed:

```text
cards / exact cohorts / method families: 11 / 6 / 4
internally ranked / unranked cohorts: 4 / 2
source report bytes read: 247,440
deterministic core files / bytes: 58 / 103,013
total artifact bytes: 103,789
runtime / peak RSS: 0.012 sec / 21,643,264 bytes
raw reads / cache opens / signal loads: 0 / 0 / 0
model runs / network fetches / holdout reopenings: 0 / 0 / 0
cross-cohort ranking: false
deterministic replay: byte-identical outside audit.json
```

Full method and interpretation:
`docs/LOOP_18_VERSIONED_REPORT_CARDS.md`.

## Experiment 17 - bounded SpanishBCBL EEG BrainVision bridge

Purpose: validate one task-matched real EEG path under explicit metadata,
download, output, dependency, alignment, and interpretation gates.

```bash
neurodecode eeg-bridge-gate \
  --manifest cache/loop19_eeg_bridge/manifest.jsonl \
  --out-dir cache/loop19_eeg_bridge/gate \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --max-download-mb 128 --max-output-mb 1

neurodecode extract-eeg-windows \
  --raw data/spanishbcbl_eeg_tiny/EEG/EEG/007_DECOMEG_S2_9910_task1.vhdr \
  --events data/spanishbcbl_eeg_tiny/EEG/logs/S7_session2_block1_list1.mat \
  --out cache/loop19_eeg_bridge/s7_session2_block1_61eeg_50hz.npz \
  --sfreq 50 --tmin -0.2 --tmax 0.3 \
  --max-alignment-residual-ms 50 --max-output-mb 32

neurodecode template-baseline \
  --cache cache/loop19_eeg_bridge/s7_session2_block1_61eeg_50hz.npz \
  --train-fraction 0.5 --seed 7 --bootstrap-iterations 2000 \
  --out-json cache/loop19_eeg_bridge/template_report.json \
  --out-md cache/loop19_eeg_bridge/template_report.md
```

Acceptance:

- pin an immutable dataset revision and verify CC BY-NC 4.0/task compatibility
- select one complete BrainVision triplet and exact MAT log under 128 MiB
- make the gate metadata-only and keep acquisition dry-run by default
- install no new heavy dependency; park MOABB when it does not match the task
- open BrainVision lazily and refuse unmatched trigger codes or residuals above
  50 ms
- stream a bounded B2Q-mini cache without raw global preload
- compare the transparent classifier to a prior fit on the exact train split
- use exact key-label accuracy, not token-string CER, as the primary metric
- keep EEG and MEG in separate cohorts and state all interpretation limits

Observed:

```text
selected files / bytes / cap: 4 / 94,842,381 / 134,217,728
gate runtime / peak RSS / artifacts: 0.144 sec / 27,983,872 bytes / 10,460 bytes
MAT/raw trigger match: 2,534 / 2,534; median/p99 residual 2.024/19.914 ms
cache shape / bytes: 2197 x 61 x 25 / 12,428,800
extraction runtime / peak RSS: 6.402 sec / 300,548,096 bytes
template/prior label accuracy: 0.009091 / 0.122727
model-minus-prior paired interval: [-0.134545, -0.093636]
baseline runtime / peak RSS: 0.63 sec / 262,209,536 bytes
MOABB/new dependency/full EEG subtree: parked / none / not downloaded
decision: bridge validated; transparent decoder result negative
```

Full method and interpretation:
`docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md`.

## Experiment 18 - NeuroTokenCache v0 synthetic interface proof

Purpose: define and exercise a future encoder-output contract without opening
real neural caches, observed holdouts, or unreleased Brain2Qwerty v2 data, and
without training or evaluating a model.

```bash
neurodecode make-neurotoken-cache \
  --source-cache cache/loop20_neurotoken/source_sentences.npz \
  --split-report cache/loop20_neurotoken/split/split.json \
  --out cache/loop20_neurotoken/neurotokens_v0.npz \
  --metadata-out cache/loop20_neurotoken/neurotokens_v0.metadata.json \
  --summary-json cache/loop20_neurotoken/neurotokens_v0.summary.json \
  --modality synthetic --device-type synthetic-array \
  --subject-id SYN-1 --session-id SESSION-1 \
  --embedding-dim 32 --kernel-size 16 --stride 4 --seed 23 \
  --max-items 64 --max-tokens-per-item 128 --max-output-mb 4
```

Acceptance:

- continuous time-major embedding schema compatible with the public v2
  `z_final` boundary
- explicit lengths, masks, frame timestamps, source rows/trials, modality,
  timebase, subject/session, geometry availability, and transformations
- strict split/source hash binding and deterministic semantic identity
- target-free synthetic producer with item, token, and byte caps
- collision refusal plus create/inspect CLI round trip
- asynchronous input, producer causality, decoder causality, and measured
  end-to-end latency represented separately
- no learned-token, decoding, real-time, unseen-person, hardware, or clinical
  claim

Observed:

```text
source / token shapes: 48 x 5 x 77 / 48 x 16 x 32
strict split: 37 train / 4 validation / 7 test
valid frames / padding fraction: 553 / 0.279948
source / token / metadata bytes: 59,357 / 76,646 / 11,369
primary artifact directory: 204 KiB
wall time / peak RSS: 0.09 sec / 44,564,480 bytes
model / training / real reads: 0 / 0 / 0
payload replay: exact
end-to-end latency measured: false
decision: interface validated; representation and decoding value untested
```

Full method and interpretation:
`docs/LOOP_20_NEUROTOKEN_CACHE_V0.md`.

## Experiment 19 - causal NeuroToken chunk/replay gate

Purpose: prove a bounded zero-lookahead frame-producer contract across
transport boundaries before training a causal encoder or implementing a text
decoder.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
neurodecode causal-replay-gate \
  --source-cache cache/loop20_neurotoken/source_sentences.npz \
  --out-json cache/loop21_causal_replay/gate.json \
  --out-md cache/loop21_causal_replay/gate.md \
  --embedding-dim 32 --kernel-size 16 --stride 4 --seed 23 \
  --max-items 64 --max-source-mb 1 \
  --max-samples-per-item 128 --max-chunk-samples 128 \
  --max-tokens-per-item 128 --max-total-pushes 10000 \
  --max-working-mb 4 --max-state-kib 1 \
  --max-runtime-sec 5 --max-peak-rss-mb 128 --max-report-mb 1
```

Acceptance:

- five registered single-sample/aligned/jittered/whole-item schedules
- zero future context, global sample timestamps, and drop-incomplete flush
- mutable overlap state smaller than one kernel and under explicit byte cap
- bitwise stream-schedule output identity and exact frame/timestamp identity
- explicit tolerance against the established batched Loop 20 arithmetic
- algorithmic frame availability, scheduler delay, compute time, and RTF
  reported separately
- signal-only selective NPZ access; no targets, real data, model, decoder,
  training, or network access
- no text-emission, end-to-end-latency, hardware, or clinical claim

Observed:

```text
schedules passed: 5 / 5
source duration / samples / frames: 28.7 sec / 2,870 / 553
right context / mutable state: 0 samples / 300 bytes
canonical stream hash: 78dc8b5298064216caa854c884a69834c0959566d9ede903d44ae1cd28562389
max Loop 20 offline difference / tolerance: 9.536743e-7 / 1e-6
public Linux CI difference / amended tolerance: 1.430511e-6 / 2e-6
aligned / jittered / whole-item max scheduling delay: 0 / 140 / 610 ms
internal runtime / peak RSS: 0.135024 sec / 46,301,184 bytes
fixed weights / bounded working core: 10,240 / 195,520 bytes
JSON / Markdown artifacts: 12,734 / 1,792 bytes
target / model / training / decoder / real reads: 0 / 0 / 0 / 0 / 0
decision: causal frame replay passed; learned encoder gate next
```

Full method and interpretation:
`docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`.

## Anti-goals

Do not do these until the earlier experiments pass:

- v2 reproduction
- large distributed training
- LLM fine-tuning
- claims about clinical use
- consumer headset claims
