# Architecture Decision Log

## 0001 — Build an access layer before a model layer

Decision: start with manifesting, selective download, tiny shards, and honest baselines.

Why: the biggest early bottleneck is usability, not model cleverness.

## 0002 — Keep base install light

Decision: base install uses pure Python. Heavy packages are optional extras.

Why: tests should pass quickly in constrained environments and in Codex before GPU/neuro dependencies are installed.

## 0003 — Use JSONL manifests

Decision: use JSONL for early manifests.

Why: easy to inspect, easy to diff, Parquet-compatible later.

## 0004 — Use `.npz` before Zarr for first cache

Decision: save first tiny shard as `.npz`, then move to Zarr.

Why: `.npz` is easy for smoke tests; Zarr is better once cache dimensions and metadata stabilize.

## 0005 — Always compare to dumb baselines

Decision: every neural model must be compared to random/frequency/keyboard/LM-only baselines.

Why: text decoding can look impressive when the language prior is doing most of the work.

## 0006 - Close Loop 1 with synthetic smoke before real data

Decision: mark Loop 1 as complete for the synthetic smoke path and proceed to Loop 2.

Why: PR1's `extract-windows` command, optional dependency handling, CLI help, and synthetic cache path are in place. Real extraction remains blocked until one explicit SpanishBCBL `.fif` / `.mat` pair is intentionally selected and downloaded.

Evidence: `docs/LOOP_01_PR1_CLOSEOUT_SMOKE.md`.

## 0007 - Make manifest uncertainty explicit before selection

Decision: add manifest v1 row families, parser warnings, optional size parsing, and raw/log candidate pairing summaries before improving download selection.

Why: safe tiny-shard selection depends on knowing which files are raw, logs, EEG sidecars, localizer/tapping files, or unknowns. Ambiguity should be visible in `inspect-manifest` rather than hidden in selector heuristics.

Evidence: `docs/LOOP_02_SPANISHBCBL_MANIFEST_V1.md`.

## 0008 - Treat tiny downloads as explicit capped plans

Decision: make `select-tiny` write a capped, size-aware selection plan and make
`download-selection` print that plan before any dry-run or execution path.

Why: a tiny-shard workflow is only safe if the exact files, known bytes,
missing-size warnings, and cap overrides are visible before the user can start a
real download.

Evidence: `docs/LOOP_03_SAFE_TINY_SHARD_SELECTOR.md`.

## 0009 - Make NPZ cache schema v0 the first stable interface

Decision: treat `load_npz_cache` as the stable B2Q-mini cache loader and stamp
every `.npz` with schema, dimensions, array descriptors, warnings, and
transformations.

Why: baselines, reports, demos, and later compression sweeps need one small
cache contract that works for both synthetic smoke data and real extracted
FIF/MAT windows.

Evidence: `docs/LOOP_04_B2Q_MINI_CACHE_V0.md`.

## 0010 - Make report cards the standard experiment artifact

Decision: add `neurodecode report` as the standard JSON/Markdown artifact for
target/prediction comparisons, with optional cache metadata attached.

Why: future no-brain, template, neural, compression, and demo loops need a
common way to compare CER, WER, keyboard-distance errors, examples, runtime, and
storage context without requiring a notebook.

Evidence: `docs/LOOP_05_METRICS_ERROR_REPORT_V1.md`.

## 0011 - Require a no-brain prior comparator before neural models

Decision: add `neurodecode prior-baseline` as the first real comparator before
template classifiers or neural networks.

Why: label/text priors can create deceptively good decoding results. Every
future neural-window model should be compared against a baseline that uses no
brain signal at all.

Evidence: `docs/LOOP_06_LM_PRIOR_BASELINE.md`.

## 0012 - Add a transparent window baseline before neural nets

Decision: add `neurodecode template-baseline` as the first neural-window
comparator before any deep model.

Why: a nearest-centroid template classifier is simple enough to audit and fast
enough to run in smoke tests. It can reveal whether labels and windows contain
separable signal before adding PyTorch or more complex sequence models.

Evidence: `docs/LOOP_07_TEMPLATE_BASELINE.md`.

## 0013 - Keep the first neural baseline optional and comparator-first

Decision: add `neurodecode tiny-conv-baseline` as an optional PyTorch-backed
baseline, guarded by the `ml` extra and reported beside the prior-only and
template baselines.

Why: a tiny ConvNet is useful only after the no-brain and transparent window
floors exist. Keeping PyTorch optional preserves the lightweight developer loop
while still allowing an ML-enabled environment to train a CPU-safe synthetic
smoke baseline.

Evidence: `docs/LOOP_08_TINY_CONV_BASELINE.md`.

## 0014 - Gate real CTC work on sequence alignment evidence

Decision: add `neurodecode align-sequences` as a lightweight pre-CTC validator
and keep real-data Loop 9 gated until MAT target sequence alignment is
understood.

Why: the raw `stim-key` cache proves actual typed key windows, but CTC needs
sequence/trial boundaries and target text. The S21 pass corrected stim timing
for nonzero `raw.first_samp`, used `mat.pr_trials.sequence` as the 66-row
trial-aligned target source, reconstructed MAT-recorded responses from
`mat.pr_trials.key`, and found useful best-text matches. A follow-up MAT-only
search showed the current 621 MB `block2.fif` shard's best matches jump
backward and forward through MAT row indices, so it is not trial-order aligned.
That is enough to keep the audit artifact, but not enough to claim real target
alignment is solved.

Evidence: `docs/LOOP_08_5_REAL_SEQUENCE_ALIGNMENT.md`.

## 0015 - Clear the one-block alignment gate and start continuous-sentence CTC

Decision: mark Loop 8.5 complete for S21 session-1 block 1 and start Loop 9 as
a resource-bounded continuous-sentence CTC scaffold.

Why: the complete `block1.fif` produces 66 trigger-derived typed sequences and
66 MAT target/response rows with a strict identity mapping, zero duplicate
target indices, and zero backtracks. The separate `keyTrig` audit pairs 2,028
keypress timestamps with a 0.246 ms median absolute residual after estimating a
run-specific clock offset. Sequence-report schema v3 records that trial identity
comes from nonempty MAT `keyTrig` slots in source order; fuzzy text is retained
only as a label-quality comparison or an explicitly ineligible partial-shard
fallback. The official Brain2Qwerty v2 release independently confirms that
continuous-window CTC is the correct next architectural layer.

Limits: this clears one data-interface gate, not neural decoding performance.
EnglishBCBL is embargoed, the official full model is cluster-scale, and the
released v2 architecture is whole-sentence and non-causal rather than
low-latency streaming.

Evidence: `docs/REAL_DATA_VALIDATION_2026-07-10.md`.

## 0016 - Separate sentence caches and close Loop 9 without a real score

Decision: add `b2q-sentence-cache` schema v0 and close Loop 9 after proving
synthetic CTC training plus one real S21 sentence-cache extraction. Do not train
or report a real decoder from the single block.

Why: CTC needs continuous padded signals, input lengths, target IDs, and target
lengths; those semantics do not belong in the event-window schema. Raw typed
text, prompted text, and MAT-recorded response text are stored separately. The
synthetic report automatically includes a no-brain prior. Deterministic CTC
restarts are selected only from training-fit quality to avoid evaluation
leakage. The real 16-channel cache verifies all 66 trial rows, official-style
preprocessing, 1.6 MB storage, 6.24-second runtime, and about 515 MiB peak RSS,
but cannot prove generalization.

Accessibility boundary: local compute is now practical for the interface.
At-home sensing is not solved; EEG has a large published accuracy gap and
wearable OPM-MEG still needs substantial magnetic shielding/control.

Evidence: `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.

## 0017 - Close the sampling-rate resource gate without selecting a winner

Decision: add `neurodecode sampling-rate-sweep` and close Loop 10 after an
isolated one-thread 100/50/25 Hz comparison on the validated S21 block. Treat
the result as resource, bandwidth, timing-grid, and CTC-length evidence only.

Why: the 50 and 25 Hz caches retain 50.9% and 25.9% of the 100 Hz cache bytes,
and all 66 targets remain feasible for the current stride-one CTC contract.
However, 50 and 25 Hz cap effective bandwidth at 25 and 12.5 Hz, and 25 Hz
leaves a worst-case conservative temporal-stride ceiling of only 2. Fresh
extraction runtime and peak memory do not improve materially because raw I/O,
filtering, and fixed library/process overhead dominate. These facts support
local compression engineering, not a decoding-accuracy conclusion.

Architecture constraint: the official v2 no-padding temporal convolution uses
kernel size 16 and stride 4. Its exact output-length rule remains CTC-feasible
for 66/66 S21 rows at 100 and 50 Hz, but fails 66/66 at 25 Hz. A 25 Hz branch
must change temporal downsampling or the sequence contract rather than blindly
reuse the official reducer.

Evaluation boundary: do not choose a sampling rate or train a claimed real
decoder until a second correctly paired block/session and explicit non-leaking
split exist. Similar robust-scaled RMS values are not evidence that neural
information was preserved.

Evidence: `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

## 0018 - Carry two sensor-selection candidates without choosing a count

Decision: add geometry-aware sentence-cache provenance and
`neurodecode channel-subset-sweep`, close Loop 11 after the real S21 proxy
study, and carry both `spatial-fps` and `variance` into a future held-out
decoder test. Keep seeded-random and file-order subsets as controls.

Why: the prior first-channel smoke cache was spatially clustered and could not
support a sensor-layout conclusion. The new base contains all 102
magnetometers at 100 Hz with finite device coordinates. Twenty nested subset
caches at 76/51/25/16/8 channels preserve exact trial, text, timing, and signal
slices under a 128 MiB output cap. Spatial FPS has the best whole-array
coverage at every count, while same-block variance ranking has the largest
post-scaling marginal variance share. At 16 channels they overlap on only 2
channels, confirming that they encode distinct hypotheses rather than one
obvious winner.

Official comparison boundary: Brain2Qwerty v2 randomly retained
230/153/76 of 306 mixed MEG channels and retrained the complete multi-subject
pipeline across four sensor seeds. This local one-block, magnetometer-only,
no-model study is a resource and candidate-selection precursor, not a
reproduction of those WER results or an OPM hardware simulation.

Evaluation boundary: variance selection must be fit on training data only, and
no count or layout can be called accuracy-preserving, optimal, anatomical, or
at-home ready until a correctly paired held-out block/session/subject protocol
measures it against no-brain and neural baselines.

Evidence: `docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.

## 0019 - Separate packed storage fidelity from decoder precision claims

Decision: add `b2q-signal-representation-cache` schema v0 and
`neurodecode precision-storage-sweep`, close Loop 12 after a five-encoding
study on the fixed base/FPS-16/variance-16 caches, keep float32 as the default,
and carry qint16 plus qint8 only as candidates for a future held-out decoder
test.

Why: all 15 representations preserve exact non-signal arrays, semantic
metadata, shapes, and zero padding. No source value exceeds the fixed `[-5, 5]`
range. Across all three caches, qint16 uses 49.84% fewer compressed bytes than
the float32 representation with at most 0.003693% relative RMSE. Qint8 uses
80.75% fewer bytes with at most 0.9531% relative RMSE and at most 1.0872%
aggregate bandpower error. Qint16 is the lowest-distortion packed option;
qint8 is the smallest.

Format boundary: the official v2 paper's BF16 result describes mixed-precision
GPU training, not the physical MEG input-cache format. Local BF16 storage is
therefore a measured baseline, not a presumed official default. Integer
representations use the existing preprocessing clamp as a fixed range and
refuse implicit clipping.

Evaluation boundary: every packed cache decodes to float32 before the current
model interface. This reduces disk and load cost, not model-weight or
activation precision. No decoder was trained, so reconstruction, SNR,
correlation, and bandpower fidelity cannot establish retained CER, WER,
semantic accuracy, or generalization.

Backend boundary: Loop 13 should first measure whether compressed NPZ full
loads are actually limiting on multi-block caches. Do not add Zarr merely
because it appears next in the roadmap; keep NPZ as the simple default unless
partial-read or peak-memory evidence justifies an optional backend.

Resolved by Decision 0020: the measured gate passed, so the optional backend
was parked and Loop 14 became the next active loop.

Evidence: `docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.

## 0020 - Park optional Zarr after the measured NPZ access gate

Decision: retain one bounded NPZ file per recording block as the default and
close Loop 13 as `Parked`. Do not install or implement Zarr unless a recorded
size, full-load, partial-load, peak-memory, or repeated-subarray-workflow
trigger is reached.

Why: nine current real standard/packed caches all passed exact decoded-signal
identity and declared local budgets. The largest compressed cache is 10.1 MiB,
the slowest full-load median is 60.386 ms, the slowest partial median is 53.634
ms, and the highest worker peak RSS is 140.6 MiB. The corresponding budgets are
128 MiB, 250 ms, 100 ms, and 512 MiB.

Partial-read boundary: NPZ member access is not true chunked array access. A
one-row request materializes the complete compressed signal/payload member,
giving 66x logical amplification on these 66-row caches. The one-row operation
takes 40.8%-82.1% of a full load. This proves relative inefficiency, not a
current material bottleneck.

Complexity boundary: Zarr provides independently addressable chunks, but an
additional backend also creates dependency, schema, chunk-layout, migration,
and test obligations. Capability alone is not sufficient evidence to add it.
A failed future gate should first trigger a bounded semantic-parity comparison.

Scientific priority: the next unclosed risk is evaluation leakage, not cache
I/O. Proceed to Loop 14 Split Protocol v1 before selecting sampling, sensor, or
precision candidates from decoder scores.

Evidence: `docs/LOOP_13_LAZY_BACKEND_GATE.md`.

## 0021 - Adopt deterministic text groups without claiming strict readiness

Decision: adopt the pinned Brain2Qwerty v2/NeuralSet 0.2.2-compatible
sentence-text assignment as Split Protocol v1, preserve `official-exact` and
the stricter local `canonical-v1` as distinct modes, and keep Loop 14 active
until data-dependent preprocessing is fit on train rows and membership is wired
into neural plus no-brain reports.

Why: the first real signal-free audit assigns all 66 exact S21 reference texts
to 55 train, 6 validation, and 5 test rows. No requested group or canonical
reference crosses a partition, no semantic trial is duplicated, all partitions
are non-empty, and stable protocol, assignment, and membership hashes are
recorded. This clears the membership part of the gate at negligible local
cost.

Fit boundary: the source cache's robust scaler was fit at recording scope and
does not declare `fit_split=train`. Variance-ranked sensor candidates have the
same future requirement. Official v2 reports per-recording RobustScaler
statistics; NeuroDecodeKit intentionally tracks a stricter train-only posture
for local candidate comparisons. A valid membership table does not repair a
transform that already saw evaluation rows.

Generalization boundary: the current cache contains one session from one
canonical SpanishBCBL person group. Event splitting is plumbing only,
sentence-text splitting tests unseen text within that narrow data boundary,
and session/subject claims remain unavailable. Repeated subject IDs documented
for the same person must be canonicalized rather than counted as independent
people.

Privacy boundary: split reports omit sentence plaintext and use SHA-256 group
IDs. These hashes are stable pseudonymous identifiers, not anonymization of a
known or guessable sentence.

Evidence: `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

Resolved by Decision 0022: train-only scaling and report-bound evaluation now
pass on the fixed 102-magnetometer base.

## 0022 - Close the split protocol; keep the model conclusion near-null

Decision: close Loop 14 after replacing recording-wide scaling with train-row
fit/frozen application, binding preprocessing and evaluation to exact cache and
membership hashes, and running one fixed tiny CTC beside a signal-free prior.
Do not promote the tiny CTC as evidence of neural advantage.

Why: the replacement 66 x 102 x 617 cache preserves every non-signal array and
zero-padded sample. Its robust statistics use 23,669 valid timepoints from 55
train rows only. The strict audit reproduces 55/6/5 membership, passes its one
fit-scope finding, and verifies the cache, protocol-config, group-assignment,
semantic-membership, and physical-membership hashes before exposing indices to
training.

Model result: on five untouched test sentences, the prior makes 164 character
edits (CER 0.953488) and the 2,908-parameter tiny CTC makes 163 (CER 0.947674).
The neural-minus-prior delta is -0.005814 CER with sentence wins/ties/losses of
2/0/3. A 5,000-sample paired sentence bootstrap gives a 95% interval of
[-0.197279, 0.130653] and only 0.509 probability of a lower CTC CER.

Interpretation: the one-edit point difference, poor train CER (0.925469), high
test blank fraction (0.868132), five-row test set, and interval crossing zero
make this a near-null baseline. It does not show that neural signal beats the
language prior.

Next-data boundary: preserve the five test rows. Acquire and validate one
additional paired session under explicit caps before real session adapters or
candidate selection. Fit variance-ranked sensors on train rows before testing
that candidate. Multiple canonical people are required for a subject claim,
and a causal architecture is required before a real-time claim.

Evidence: `docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

## 0023 - Make split-FIFF completeness and performed MAT slots explicit

Decision: a tiny selection that contains a split FIFF primary must include all
matching hyphen-numbered continuations and count every part against the safety
caps. Real selections may be filtered by session and pinned to an immutable Hub
revision. Sentence extraction maps raw ENTER-delimited rows to nonempty
`pr_trials.keyTrig` slots in source order and preserves skipped MAT trial IDs.

Why: S21 session 2 is physically stored as `block1.fif` plus `block1-1.fif`.
Selecting only the primary would create an incomplete recording that can still
look plausible. Its MAT log contains 66 target slots but only 63 nonempty
`keyTrig` and response slots; trials 54, 58, and 60 were not performed. Equal
raw/target counts are therefore not a valid universal invariant.

Validation boundary: the 63 raw trials map exactly to the 63 nonempty MAT slots,
response indices match that map, and 2,529 paired keypresses have 0.296 ms
median and 0.945 ms p95 absolute timing residual after one run-specific offset.
No fuzzy target text is used to assign trial identity. Unreconciled counts,
non-monotonic maps, missing continuations, and cap violations fail closed.

Resource boundary: the pinned three-file selection is 2,516,384,765 bytes under
a 2.5-GiB cap and uses one Hub worker. The full dataset remains remote.

Evidence: `docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## 0024 - Freeze session 2 after the fixed cross-session baseline fails

Decision: treat the first S21 session-2 score as a consumed independent-session
evaluation. Do not tune a normalization method, learned adapter, model,
hyperparameter, sensor subset, precision, or stopping rule against it. Continue
Loop 15 adapter development on synthetic domain shift and source
train/validation rows, then pre-register a future real holdout.

Why: session 2 was preprocessed with the same 102 channels and filters as
session 1, then scaled only with robust statistics fitted on 55 source train
rows. Six source validation and five source test rows remained unused. The
fixed 2,908-parameter tiny CTC nevertheless makes 2,506 character edits on 63
session-2 rows (CER 0.917949), versus 2,117 edits (CER 0.775458) for the
signal-free source-train prior.

Uncertainty boundary: tiny-minus-prior CER is +0.142491; the 5,000-sample paired
sentence-bootstrap interval is [+0.119386, +0.166069], and sentence
wins/ties/losses are 3/2/58. This is evidence of failed transfer under the fixed
baseline, not evidence that a more complex adapter will work.

Generalization boundary: two sessions from one canonical person support only a
same-subject session statement. They do not establish unseen-person,
population, clinical, real-time, portable-sensor, or arbitrary-thought
performance.

Evidence: `docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## 0025 - Close Loop 15 on a synthetic affine mechanism proof

Decision: select the zero-learned-parameter robust channel-affine adapter for
the next synthetic calibration study and close Loop 15. Keep the consumed S21
session-2 evaluation and five real source-test rows frozen.

Why: under a fixed 64/16/16 synthetic text-hash protocol, identity decoding
under a diagonal gain/offset shift has validation/holdout CER 0.327273/0.344828.
Unlabeled median/IQR matching is selected on validation and reaches zero CER on
all 16 frozen synthetic holdout rows. The signal-free prior has holdout CER
0.577586. The adapter stores four statistics per channel, learns no gradient
parameters, preserves exact padding, and reduces known-shift reconstruction
MAE by a factor greater than five million. The same tiny CTC training replay is
identical across all comparisons.

Boundary: this is intentionally a best-case synthetic affine inversion. It is
not evidence of real MEG adaptation, non-affine drift recovery, unseen-person
generalization, causal decoding, real-time performance, or at-home hardware.
The next experiment must vary calibration size and shift family without opening
any consumed real holdout.

Evidence: `docs/LOOP_15_STAGE_B_SYNTHETIC_ADAPTER.md` and
`cache/loop15_synthetic_adapter_gate/report.json`.

## 0026 - Keep robust affine inside its measured stationary-diagonal scope

Decision: close Loop 16 as a synthetic calibration characterization. Retain
robust channel-affine normalization only as a stationary-diagonal synthetic
candidate. Do not treat it as a general session adapter or authorize a new real
evaluation.

Why: an independent unlabeled calibration pool, six nested sizes, and three
shift seeds produce a registered one-row stationary-diagonal recommendation.
That row contains 1.26 seconds of deliberately easy synthetic motif data. On
frozen synthetic holdout, median identity/adapted CER is 0.422414/0.232759;
two seeds improve and one ties. A stricter all-seed gain sensitivity would
select two rows, but that was not the registered rule.

Failure boundary: at the same selected size, every channel-mixing holdout seed
is harmed (median identity/adapted CER 0.568966/0.862069), as is every
within-row time-varying seed (0.439655/0.603448). Static independent-channel
statistics cannot invert cross-channel rotation or track drift over time.

Resource and leakage boundary: the runner trains twice total, uses one CPU
thread, writes no cache, emits 158,256 bytes under a 4-MiB cap, and never loads
the five real source-test or 63 consumed session-2 rows. The next adapter must
pass synthetic validation for covariance or causal drift before any future real
holdout is preregistered.

Evidence: `docs/LOOP_16_SYNTHETIC_CALIBRATION_CURVE.md` and
`cache/loop16_synthetic_calibration_curve/report.json`.

## 0027 - Make the demo an artifact audit, not a live-decoding claim

Decision: close Loop 17 with a loopback-only Gradio evidence console. Show
held-out synthetic examples, aggregate real metrics, calibration state, and
local provenance. Do not display real sentence text, infer per-example
confidence, train or run a model, fetch data, or read raw neurodata.

Why: the compact Loop 9, 14, 15, and 16 artifacts already contain enough
evidence for an outsider to inspect the pipeline. Re-running either observed
real holdout for a UI would add scientific risk without adding reproducibility.
The loader instead cross-checks synthetic cache rows, predictions, report
examples and summary metrics, hashes all six source artifacts, and fails when
their contracts disagree.

Validation boundary: 19 synthetic examples are available end to end. Real rows
remain aggregate-only: the five-row strict test is near-null and the 63-row
same-person session transfer is worse than the prior. Predictive confidence is
reported as unavailable because the saved report contains a greedy CTC string,
not a calibrated posterior.

Resource boundary: the final startup audit passes 8/8 checks in 1.644 seconds
at 224,837,632-byte peak RSS. The source cache is 136,734 bytes; no new cache is
written. Desktop 1440 x 1000 and mobile 390 x 844 interaction QA pass with no
page overflow or browser-console errors. The optional Gradio environment costs
about 174.6 MiB.

Evidence: `docs/LOOP_17_HONEST_LOCAL_DEMO.md`,
`cache/loop17_demo/audit.json`, and `cache/loop17_demo/browser_qa.json`.

## 0028 - Rank only inside exact evidence cohorts

Decision: close Loop 18 with versioned report-card schema v1 and a local
artifact-only leaderboard. Rank methods only when their exact cohort explicitly
authorizes comparison. Do not calculate a global winner across tasks, units,
splits, sessions, synthetic fixtures, or fit-on-eval smoke runs.

Why: 11 historical runs can be normalized into six evidence cohorts without
retraining. The cross-session cohort shows why one score is inadequate: the
source-trained prior has lower CER than tiny CTC, while tiny CTC has slightly
lower WER. Event-key and sentence decoding are different tasks, and the old
fit-on-eval prior is not a held-out result at all.

Provenance boundary: every card hashes its compact source report and filtered
config. Historical cache hashes, SemER, code versions, method-specific resource
measurements, and uncertainty remain visibly missing when the source artifact
did not record them. The builder does not open a cache to fill those gaps.

Resource boundary: 247,440 source-report bytes produce 58 deterministic core
files and 103,789 total artifact bytes in 0.012 seconds at 21,643,264-byte peak
RSS. A second build is byte-identical outside the intentionally variable audit.
Raw reads, cache opens, signal-array loads, model runs, network fetches, and
holdout reopenings are all zero.

Evidence: `docs/LOOP_18_VERSIONED_REPORT_CARDS.md`,
`configs/loop18_leaderboard.json`, and
`cache/loop18_leaderboard/leaderboard.json`.

## 0029 - Close Loop 19 on a native task-matched EEG bridge and negative baseline

Decision: keep a native optional MNE BrainVision bridge for SpanishBCBL EEG and
park MOABB for this loop. Close Loop 19 after one pinned, explicitly approved
S7 bundle validates selection, trigger alignment, lazy extraction, cache
compatibility, and a same-split no-signal comparison. Do not tune a more complex
classifier against this within-session event holdout.

Why: the metadata-only gate selected a complete `.vhdr/.eeg/.vmrk` triplet plus
exact MAT log totaling 94,842,381 bytes under a 128-MiB cap. The real extractor
matched all 2,534 MAT trigger codes to raw BrainVision annotations with a
2.024-ms median absolute residual, retained 2,197 supported key events, and
wrote a 12,428,800-byte `2197 x 61 x 25` cache without globally preloading the
raw recording. No new dependency was needed.

Negative-result boundary: on a deterministic 1,097/1,100 within-file
key-stratified split, nearest-centroid exact label accuracy is 0.009091 versus
0.122727 for the most-frequent prior fit only on the 1,097 training labels. The
model-minus-prior accuracy delta is -0.113636 with a 2,000-sample paired
bootstrap interval of [-0.134545, -0.093636]. Text CER is non-primary because
multi-character key tokens distort character edit counts.

Scope boundary: named EOG channels are excluded, but no EEG filtering,
rereferencing, bad-channel repair, ICA, or artifact rejection is claimed. This
single-session event split does not establish sentence, session, subject,
population, real-time, portable-hardware, arbitrary-thought, or clinical
performance. EEG and MEG remain separate evidence cohorts.

Evidence: `docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md`,
`cache/loop19_eeg_bridge/gate/report.json`,
`cache/loop19_eeg_bridge/extraction.json`, and
`cache/loop19_eeg_bridge/template_report.json`.

## 0030 - Make neurotokens a continuous interface before making them a model claim

Decision: close Loop 20 with a versioned `NeuroTokenCache v0` contract and a
target-free synthetic producer. Store continuous `[items,time,embedding]`
vectors plus timing, masks, source identity, modality, geometry availability,
strict split/source hashes, resources, and explicit causality fields. Do not
call the mock vectors discrete, learned, semantic, or decoder-ready evidence.

Why: the public Brain2Qwerty v2 encoder exposes a time-major per-frame
`z_final` representation, but its English data is not public and its reference
encoder is noncausal whole-sentence. A small schema can preserve that future
boundary without importing its unavailable data or GPU-scale training recipe.
The Loop 20 producer uses fixed overlapping frames and seeded Gaussian weights
only to prove serialization and downstream interface shape.

Validation boundary: one 48-item synthetic source with a strict 37/4/7 split
produces a 76,646-byte `48 x 16 x 32` float32 cache. An independent replay has
the same token payload SHA-256
`82b478948bdcfd5b2d12643f9f912c192a8977c8f0554b9f073171cf6dfe2709`.
The NPZ contains no target-text or target-token array. Model runs, training
runs, real-data reads, and observed-holdout reads are all zero.

Streaming boundary: at 100 Hz, kernel 16 and stride 4 yield 160-ms mock frame
availability and 40-ms steps. The producer is causal at the frame boundary,
but downstream causality is unspecified and end-to-end latency is unmeasured.
The next gate is synthetic causal chunk/replay equivalence, not a larger model
or a real-data score.

Evidence: `docs/LOOP_20_NEUROTOKEN_CACHE_V0.md`,
`cache/loop20_neurotoken/neurotokens_v0.metadata.json`, and
`cache/loop20_neurotoken/neurotokens_v0.summary.json`.

## 0031 - Separate causal frame production from transport and text latency

Decision: close post-roadmap Loop 21 only after one target-free streaming
producer passes five registered synthetic chunk schedules with bounded mutable
state, zero right context, explicit drop-incomplete flush, exact frame/timing
identity, and bitwise schedule-invariant output. Keep decoder causality, symbol
emission, endpointing, capture, rendering, and end-to-end latency unavailable.

Why: Brain2Qwerty v2 removes keypress-timing dependence but its public encoder
remains a whole-sentence noncausal Conformer, and its paper identifies fully
low-latency operation as future work. Streaming-ASR references likewise
separate bounded encoder memory/right context from symbol emission delay. The
Loop 21 schedules demonstrate the practical distinction: stride-aligned chunks
add zero scheduler delay, jittered chunks add up to 140 ms, and whole-item
delivery adds up to 610 ms despite having the lowest compute RTF.

Floating-point boundary: canonical one-frame streaming is bitwise identical
across all schedules. The already-frozen Loop 20 batched matrix multiplication
differs by at most `9.5367431640625e-7`, so compatibility is declared at
absolute tolerance `1e-6` instead of silently changing the prior artifact.
Frame indices and timestamps remain bitwise exact.

Resource and access boundary: 28.7 seconds of synthetic source yields 553
frames across 4,652 pushes in 0.135024 seconds at 46,301,184-byte peak RSS.
Fixed weights use 10,240 bytes, bounded working core arrays use 195,520 bytes,
and mutable state peaks at exactly 300 bytes.
Only signal/timing/metadata NPZ members are opened. Target arrays, raw/real
data, models, training, decoders, and network access remain at zero.

Next gate: train one tiny causal encoder on synthetic train rows only, select
on validation, compare with a no-signal prior, and open one frozen synthetic
test pass under strict parameter/state/CPU/RSS/artifact caps. Do not begin CTC
prefix decoding or real-cache conversion first.

Evidence: `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`,
`docs/POST_20_ROADMAP.md`, and `cache/loop21_causal_replay/gate.json`.

## 0032 - Freeze the tiny causal encoder protocol before creating its test fixture

Decision: preregister Loop 22 before generating its dedicated synthetic test
partition. Use physically separate 64/8/8 train/validation/test motif files,
one 1,130-parameter kernel-16/stride-4 causal encoder and probe, train-only
normalization/class weights, validation-selected early stopping, one test open,
two signal-free controls, five-schedule replay, and explicit byte/runtime/RSS
caps. Do not permit architecture candidates or initialization restarts.

Why: the single Loop 20 NPZ contains every row in one compressed signal member,
so selecting row indices after loading it cannot prove that test signals stayed
unopened. Separate hash-bound files make the access boundary observable. The
public v2 methods likewise separate deterministic membership, validation model
selection, and later test evaluation, while its noncausal GPU-scale Conformer
is far beyond this local mechanism gate.

Validation decision: require balanced accuracy of at least 0.70, at least 0.35
above the train-only prior, and raw accuracy at least 0.20 above that prior.
Only then may the gate open test once. Test proceeds only if learned balanced
and raw accuracy exceed both prior and zero-signal controls by 0.35 and 0.20,
respectively, and the 2,000-resample paired item bootstrap lower bound over the
prior is positive.

Claim boundary: the motif probe is not CTC or text decoding. Passing authorizes
only a separately preregistered synthetic streaming-decoder gate. Failing parks
the branch without widening or reseeding against the same test partition.

Evidence: `docs/LOOP_22_PREREGISTRATION.md`.

## 0033 - Make target-free production an observable access boundary

Decision: a producer described as target-free must not merely ignore target
values after a general cache load. Its source reader must physically avoid
opening target-text and target-token members, record the exact members opened,
and carry explicit false access flags in output provenance.

Why: Loop 20's deterministic projection never used labels, but the original
general sentence-cache loader still materialized target arrays. That was not
numerical leakage, yet it left the access claim weaker than the split and
provenance contracts. The dedicated reader now opens only seven signal-side
members while verifying five target members exist without indexing them. A
wrapped-`numpy.load` regression test makes this boundary observable.

Validation boundary: the hardened replay keeps the exact prior payload SHA-256
and all source/split bindings. It adds 802 bytes across the cache and metadata
sidecar, remains far below 32 MiB, and performs zero raw-data, real-cache,
model, or training runs. This strengthens interface provenance only; it does
not improve or validate a representation, classifier, decoder, or latency
claim.

Evidence: `docs/LOOP_20_NEUROTOKEN_CACHE_V0.md` and
`tests/test_neurotoken.py`.

## 0034 - Proceed from learned synthetic frames to a separately preregistered decoder

Decision: close Loop 22 as a passed synthetic mechanism gate and authorize only
a new preregistered Loop 23 streaming CTC/prefix-decoder protocol. Freeze the
Loop 22 checkpoint, report, and consumed seed-2203 test; do not reuse that test
to select decoder state, thresholds, architecture, or timing rules.

Why: the single registered model selected epoch 34 on validation, opened test
once after checkpoint freeze, and reached 1.0 motif balanced accuracy versus
0.166667 for both signal-free controls. Its paired item-bootstrap lower bound
for accuracy gain over the prior was 0.630906. Five transport schedules
reproduced one 161-frame embedding payload bitwise with zero right context and
300-byte state.

Scope boundary: the generated task deliberately injects strong channel-local
motifs, so perfect classification is a plumbing and mechanism result. The
diagnostic probe is not CTC or text; no real MEG/EEG data, observed holdout,
language model, CER/WER, endpoint, or end-to-end latency was used or measured.
Loop 23 must use a new physical test and keep the no-language-model comparator
visible before any precision or real-cache gate.

Evidence: `docs/LOOP_22_TINY_CAUSAL_ENCODER.md`,
`cache/loop22_tiny_causal_encoder/gate.json`, and
`cache/loop22_tiny_causal_encoder/gate.md`.

## 0035 - Freeze streaming CTC semantics and stability metrics before targets

Decision: preregister Loop 23 before writing decoder code or generating its
fresh test. Reuse only the frozen Loop 22 checkpoint, map background to CTC
blank and motifs to five synthetic symbols, fix greedy and width-8 prefix-beam
rules without a language model, and require a new physical 48/8/8 fixture whose
targets include adjacent repeated symbols.

Why: CTC blank/repeat collapse and prefix probabilities are easy to implement
incorrectly, especially across chunk boundaries. Final CER alone would also
hide partial flicker and delayed stabilization. The protocol therefore requires
hand-built and exhaustive tiny-path oracles, frame-indexed partial traces,
edit overhead, revision events, first-correct/stable-correct/finalization time,
and transport-adjusted availability.

Access and claim boundary: alternate seeds must prove mechanics before the
registered seed-2303 test exists. Validation schedule replay happens before
test access; test gets one canonical pass only. No CTC loss, parameter update,
language model, real data, observed holdout, WER, endpoint, or end-to-end
latency claim is allowed.

Evidence: `docs/LOOP_23_PREREGISTRATION.md`.

## 0036 - Park Loop 23 after the frozen exact-sequence gate fails

Decision: retain the dependency-free CTC decoder and synthetic access gate as
an engineering mechanism, but park Loop 23 because its one registered frozen
test reaches only 5/8 exact sequences against the preregistered 6/8 threshold.
Do not rerun seed 2303 or tune a tail rule, threshold, blank bias, endpoint, or
model against its outputs.

Why: validation passed at CER 0.018182 and 7/8 exact, so the test was correctly
opened once. Test CER is 0.054545, all 10 repeated pairs are reconstructed,
both signal-free CER margins and their paired bootstrap lower bounds pass, and
all five stream schedules reproduce exact frame-indexed traces. Exact accuracy
still fails at 0.625. Every incorrect row contains the complete target followed
by one nonblank tail symbol, and greedy and width-8 prefix beam are identical.
The failure is therefore upstream score/boundary behavior, not a blank/repeat
collapse defect or beam-search improvement.

Access and resource boundary: implementation commit `08b23d7` was pushed before
seed 2303 existed. Registered train/validation/test partitions opened exactly
once in the required order; seed 2303 is now consumed. The 141,412-byte fixture,
364,912-byte report, 0.713611-second internal runtime, 226,410,496-byte external
peak RSS, 300-byte encoder state, and 290-byte prefix state all remain under
their caps with one CPU thread and zero real/raw/text/network access.

Next boundary: preregister a fresh Loop 23.5 target-independent blank/boundary
calibration gate before implementing or generating anything. Keep the
unmodified Loop 23 decoder as comparator. Forbid target-length trimming,
language models, larger encoders, precision work, seed-2303 reuse, and real
holdout access.

Evidence: `docs/LOOP_23_STREAMING_CTC_DECODER.md`,
`cache/loop23_streaming_ctc/gate.json`, and
`cache/loop23_streaming_ctc/gate.md`.

## 0037 - Freeze one intercept-only blank calibration before fresh targets

Decision: preregister Loop 23.5 as one supervised synthetic frame-calibration
experiment. Fit exactly one additive blank-logit intercept by 80 iterations of
float64 bisection on fresh train-frame binary log loss. Keep the slope, encoder,
symbol logits, CTC state, beam, and flush unchanged. Validation may only open a
fresh test or park.

Why: Loop 23's errors are stable nonblank tail insertions shared by greedy and
prefix decoding. The frozen Loop 22 probe was trained with inverse-frequency
frame weights for balanced classification, but its raw blank probability was
never calibrated for natural frame prevalence. Primary calibration and logit
adjustment work support testing a low-parameter score correction; they do not
prove it will solve this generated task or transfer to neural data.

Fresh-data boundary: use new physical 64/16/16 splits with seeds
2351/2352/2353. Seed 2353 cannot exist until this preregistration and later
alternate-seed mechanics are separately committed and pushed. Fit may open
train signals/frame labels but no target IDs. The prior may separately open
train targets but no signals. Seed 2303 and every observed real holdout remain
forbidden.

Gate boundary: require at least two corrected validation/test items, no new
exact errors, no per-item CER regressions, at least two removed tail tokens,
14/16 exact accuracy, CER at most 0.03, calibration improvement, repeated-pair
preservation, signal-free margins, and exact 5/5 validation replay. No
target-length trim, endpoint, language model, temperature, per-symbol bias,
larger model, or precision candidate is allowed.

Evidence: `docs/LOOP_23_5_PREREGISTRATION.md`.

## 0038 - Close Loop 23.5 and consume seed 2353

Decision: close Loop 23.5 as a passed supervised synthetic calibration
mechanism gate. Preserve the fitted scalar, protocol, decoder, controls,
thresholds, and report as frozen evidence. Authorize Loop 24 preregistration,
but no precision implementation or comparison until that new protocol is
committed and pushed.

Why: the registered train-frame fit produces one blank-logit intercept of
`5.130175197684084`. Validation passes at 16/16 exact and CER 0, so seed 2353
opens once. Its frozen test also reaches 16/16 exact and CER 0 versus 7/16 and
CER 0.081818 for the unmodified decoder. Nine test items are corrected, no new
error or per-item CER regression appears, all 19 repeated pairs survive, and
the paired-bootstrap lower bounds for exact gain and CER reduction are
positive. Both calibrated and unmodified validation decoders replay 5/5
schedules exactly.

Access and resource boundary: implementation commit `baeea77` was pushed
before seed 2353 existed. Calibration opens train frame labels but no target
IDs; the prior uses a separate target-only view; validation precedes one test
open; no test replay or post-open fit occurs. Fixture plus reports total
969,177 bytes, internal runtime is 1.266573 seconds, peak RSS is 213,958,656
bytes, and state, working-memory, thread, and output caps all pass. There are
zero training runs, model updates, raw/real/network reads, or language-model
runs.

Claim boundary: this result identifies a sufficient score-calibration
mechanism for one generated motif/symbol task. It does not establish a learned
representation, endpoint detector, natural-text decoder, MEG/EEG transfer,
neural advantage, unseen-person performance, real-time latency, portable
hardware, arbitrary-thought decoding, or clinical utility.

Next boundary: seed 2353 is consumed. Loop 24 may not use it to choose a
candidate, set a tolerance, or claim fresh evidence. Preregister candidates,
reference arithmetic, fresh selection data, correctness tolerances, resource
caps, and kill rules before writing precision code.

Evidence: `docs/LOOP_23_5_BLANK_INTERCEPT_CALIBRATION.md`,
`cache/loop235_blank_intercept/gate.json`, and
`cache/loop235_blank_intercept/gate.md`.

## 0039 - Add a parallel practice track and keep fresh EEG approval-gated

Decision: add a Real-World Practice Track identified as RW0-RW9 without
renumbering Loop 24. Close RW0 as a primary-source metadata research gate and
authorize only RW1 level-0 metadata intake on synthetic fixtures. Keep the
first fresh S20 EEG benchmark at RW4 and blocked until the user explicitly
approves the exact packet.

Why: the existing pipeline has strong cache, alignment, causality, and report
contracts but no demonstrated neural advantage or portable-device result. A
practical local workbench needs to separate file readability, task
compatibility, benchmark authorization, and live-source qualification. It also
needs explicit evidence cohorts so reading, P300, SSVEP, motor imagery, eye
tracking, and wrist EMG are not mistaken for prompted brain-to-text.

Data decision: no unconsumed task-compatible raw EEG exists locally. The
smallest complete fresh candidate in the pinned SpanishBCBL manifest is S20
session 2 block 2: one 95,782,400-byte EEG file, an 11,705-byte VHDR, a
91,219-byte VMRK, and a 204,940-byte MAT log, totaling 96,090,264 bytes. The log
already exists locally but was not parsed in this gate. The packet freezes a
128-MiB acquisition cap, 16-MiB generated cap, one worker/thread, target-free
44/10/10 trial split, prior and shuffle controls, and event-level metrics only.

Access boundary: the research gate used filenames, sizes, official metadata,
and saved aggregate proof only. It performed zero raw reads, consumed-cache
reads, model runs, training runs, target-log parses, or downloads. Current disk
headroom is about 11 GiB but the volume is 98% full, so no speculative data or
duplicate cache is authorized.

Claim boundary: dataset/device compatibility metadata is not a benchmark.
AirPods, Vision Pro, Quest, Apple Watch, and Meta Neural Band provide
behavioral, cardiac, motion, audio, gaze, hand, or muscle signals, not EEG.
Every future multimodal result requires brain-only, peripheral-only, and
combined ablations.

Evidence: `docs/REAL_WORLD_PRACTICE_TRACK_RESEARCH.md`,
`docs/BYO_NEURODATA_WORKBENCH_SPEC.md`,
`docs/FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md`,
`registries/datasets.v0.json`, and `registries/devices.v0.json`.

## 0040 - Close RW1 at compatibility level 0

Decision: close RW1 as a passed dependency-free metadata-only interface gate.
Authorize RW2 preregistration only. Do not implement an optional MNE/MNE-BIDS
reader, open a real signal, or define a quality threshold until the bounded
read, units, reference, geometry, event, PSD, warning, privacy, resource, and
no-auto-deletion contract is committed and pushed.

Why: the scanner recognizes or safely refuses BrainVision, EDF/EDF+, BDF,
EEGLAB, FIF, BIDS, unknown files, and non-BIDS directories without opening
binary signal, event, label, or target content. It enforces resolved roots,
symlink and traversal refusal, companion roles, FIF filename continuity,
file/depth/input/text/output caps, and collision behavior. Deterministic JSON
and Markdown keep process measurements in a separate hash-validated audit
sidecar.

Measured gate: the ignored 532-byte synthetic BrainVision fixture writes
11,545 bytes under a 4-MiB cap. Scanner/report-build runtime is 0.001659
seconds and peak RSS is 21,643,264 bytes. Access counters are zero for binary
signal files/bytes, raw data, real caches, targets/labels, models, training, and
network. Eleven focused tests pass; the complete suite rises from 238 to 249
unittest tests with the same three skips and from 235 to 246 pytest tests with
the same three skips and 25 subtests.

Data and claim boundary: RW1 uses synthetic fixtures and local registry
metadata only. It does not open S7, either S21 session, S20, any real cache, or
seeds 2203/2303/2353. It establishes no signal readability, signal quality,
task compatibility, decoding, neural advantage, unseen-person, latency,
real-time, hardware, arbitrary-thought, or clinical claim.

Evidence: `docs/RW1_METADATA_ONLY_LOCAL_INTAKE.md`, implementation commit
`77dcea5`, and ignored local artifacts under `outputs/rw1-metadata-intake/`.

## 0041 - Freeze RW2 bounded signal-quality contract before implementation

Decision: freeze RW2 as a versioned, machine-readable synthetic-fixture
protocol at commit `eacb231`, then authorize only its exact implementation.
The first implementation may use optional MNE readers for generated
BrainVision, EDF/EDF+, BDF, EEGLAB external-FDT, FIF, and BIDS fixtures. It may
not open a real recording, consumed cache, S20, or MNE-BIDS, and it may not
filter, resample, rereference, clean, interpolate, delete channels, or persist
waveforms.

Why: primary-source review exposed format-specific behavior that a generic
reader contract would hide. MNE-BIDS imports event and channel sidecars into
annotations and bad-channel state; EEGLAB embedded `.set` arrays can defeat
lazy-read expectations; EDF/BDF mixed source rates can trigger upsampling; and
reader defaults can infer channel roles. RW2 therefore binds named readers and
arguments, routes BIDS through the RW1 resolver plus a direct format reader,
refuses embedded or epoched EEGLAB, and limits EDF/BDF level 2 to a proven
single source rate.

Frozen measurement boundary: at most 512 channels and three deterministic
windows may be read, with 4,194,304 channel-sample values and 32 MiB of
materialized float64 signal. Execution uses one worker/thread, a 30-second
runtime cap, 1-GiB peak-RSS cap, 4-MiB per-run output cap, and 16-MiB complete
synthetic fixture/report cap. Quality output is descriptive: robust amplitude,
finite/flat/duplicate structure, and median Welch PSD summaries with declared
settings. Generic clipping, excessive-amplitude, and line-noise pass/fail
thresholds remain unavailable without a modality/device profile. Warnings do
not mutate the source or trigger automatic cleaning.

Privacy and claim boundary: artifacts omit absolute paths, participant data,
dates, device serials, annotation/event descriptions and exact timestamps,
exact geometry, and waveform values. Preregistration accessed zero raw arrays,
real caches, targets, models, training runs, or downloads and generated no
signal artifact. A future passing synthetic gate would establish bounded
reader/report mechanics only, not real signal quality, task compatibility,
decoding, neural advantage, end-to-end latency, live hardware, arbitrary
thought reading, or clinical utility.

Evidence: `docs/RW2_PRIMARY_SOURCE_RESEARCH.md`,
`docs/RW2_SIGNAL_QUALITY_PREREGISTRATION.md`,
`registries/signal_quality_contract.v0.json`, and registration commit
`eacb231`.

## 0042 - Close RW2 at exact synthetic compatibility level 2

Decision: close RW2 as a passed fixture-backed reader, report, privacy,
no-mutation, and resource gate. Authorize RW3 preregistration only. Do not
interpret the compatibility level outside the exact generated files, MNE 1.12
minor line, reader arguments, and frozen contract.

Why: the implementation generates 40 target-free fixtures across BrainVision,
EDF/EDF+, BDF, continuous EEGLAB external-FDT, FIF, and BIDS. All 38 authorized
sources pass and the two registered unsafe/malformed sources refuse exactly.
Reader opens remain lazy, canonical selected-payload hashes match expected
format quantization, descriptive amplitude/structure/median-Welch metrics
replay, privacy fields stay absent, and before/after source and signal hashes
match. No automatic cleaning or source mutation occurs.

Measured boundary: one clean FIF roundtrip selects nine channels and three
windows with 11,520 requested/returned values, 92,160 materialized array bytes,
and six bounded signal reads. It writes 72,818 bytes of deterministic JSON,
1,734 bytes of Markdown, and a 2,040-byte audit, totaling 76,592 bytes. Internal
runtime is 3.839168 seconds and peak RSS is 150,749,184 bytes. Real data,
consumed caches, targets/labels, models, training, and network calls are zero.
Physical storage bytes read, generic warning thresholds, task/model
compatibility, live qualification, real quality, and end-to-end latency remain
unavailable.

Verification: nine focused tests pass; the full optional environment reaches
258 unittest tests with 3 skips and 255 pytest passes with 3 skips plus 25
subtests. The true zero-dependency run passes 246 tests with 118 explicit
optional skips. Ruff, compileall, CLI help, deterministic replay, malformed,
tamper, collision, privacy, cap, package-metadata, and `git diff --check` gates
pass.

Next boundary: RW3 must freeze source chunks, offline playback/synthetic
adapters, dependency policy, clock domains, timestamp correction, dropped
packets, ordering, mutable state, schedules, tolerances, privacy, resources,
and stop rules before BrainFlow, LSL, live sources, or hardware are touched.
RW4/S20 remains blocked on separate explicit approval.

Evidence: `docs/RW2_SIGNAL_QUALITY_CLOSEOUT.md`, implementation commit
`2796dee`, and ignored local fixtures/reports under `.codex_work/`.

## 0043 - Prepare a proof-first open-source collaboration surface

Decision: publish a detailed contributor-ready surface on the active review
branch while keeping repository visibility and default-branch release as
separate maintainer decisions. Use Apache-2.0 provisionally for
NeuroDecodeKit's original source and documentation, with explicit separate
CC-BY-NC-4.0 terms for Brain2Qwerty and SpanishBCBL.

Why: useful community contribution requires more than a public code dump. EEG
owners need a metadata-first path that never asks them to post recordings;
hardware owners need replay/timestamp/packet-loss criteria; predictive results
need no-signal controls and consumed-holdout disclosure; maintainers need
security, conduct, governance, citation, issue, review, and CI contracts.

Public-history audit: Git tracks only `.gitkeep` under `data/` and `cache/`;
no neural recording or cache extension was found in tracked history. The
pre-documentation object store was 6.22 MiB with a 332.37 KiB pack and a
321,169-byte largest blob. Gitleaks 8.30.0 found one documented NeuroToken
SHA-256 false positive; an exact commit/path/rule/line fingerprint suppresses
only that reviewed finding, and the complete default scan then passes.

GitHub boundary: description, 16 topics, and eight issue labels were updated.
The repository reported private at the start and public when rechecked after
those metadata-only commands, even though no visibility flag was issued.
At decision time, default `main` remained stale. PR #1 later merged the
open-source surface through `e5d89ed` at `18a705e`. Draft PR #2 now carries the
latest RW2/results closeout and the canonical Apache license-text correction;
its four base/optional-neuro push/PR checks pass. Public visibility still
requires an explicit maintainer decision, and PR #2 must not merge without
license, security, history, and proof-boundary review.

Evidence: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `GOVERNANCE.md`,
`CODE_OF_CONDUCT.md`, `THIRD_PARTY_NOTICES.md`,
`docs/OPEN_SOURCE_READINESS.md`, and commit `e5d89ed`.

## 0044 - Amend only the cross-kernel Loop 21 float tolerance for Linux

Decision: change the default absolute compatibility tolerance between Loop
20's historical batched float32 projection and Loop 21's canonical one-frame
projection from `1e-6` to `2e-6`. Keep canonical stream payloads bitwise
identical across all five schedules and keep timestamp, frame-grid, causal,
state, resource, and access gates unchanged.

Why: public GitHub Actions on Linux with Python 3.12, NumPy 2.5.1, and
one-thread OpenBLAS measured a maximum cross-kernel difference of exactly
`1.430511474609375e-6`. The same Python/NumPy versions on macOS remain at the
historical `9.5367431640625e-7`. Explicit gate diagnostics prove that no other
condition failed. This is BLAS arithmetic portability, not schedule drift.

Integrity boundary: the first CI failure was retained and diagnosed before the
tolerance changed. This amendment uses no targets, labels, model, training,
real data, consumed cache, or holdout. It does not rewrite the historical Loop
20 artifact, change its hash, relax schedule-to-schedule identity, or create a
decoding claim. A future difference above `2e-6` still fails closed and
requires another explicit review rather than automatic widening.

Evidence: failed Actions runs `29133225088`, `29133248840`, and `29133423319`;
diagnostic commit `5c212c8`; `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`.

## 0045 - Freeze RW3 source-chunk and replay-equivalence protocol before code

Decision: preregister RW3 at commit `c3d1f01` as primary-source research, one
versioned machine contract, and dependency-free invariant tests only. Do not
authorize Stage A implementation from the registration. Require separate
review for each later stage: pure-Python synthetic replay, BrainFlow
synthetic/playback boards, local LSL loopback, and PyXDF raw/corrected views.

Why: a plausible waveform plot can conceal regenerated timestamps, wrong clock
correction, duplicate drains, dropped or reordered samples, ambiguous stream
selection, silent interpolation, or transport-specific state. BrainFlow 5.22.2,
pylsl 1.18.2/liblsl 1.17.7, PyXDF 1.17.5, and Python monotonic-clock primary
sources expose different semantics that must be made explicit before one
runtime abstraction can be trusted.

Frozen contract: `neurodecodekit.replay_equivalence_contract` v0.1.0 defines a
future `neurodecodekit.source_chunk` v0.1.0, separate source/corrected/arrival
timestamps, gap/duplicate/reorder/wrap/reconnect/reset records, exact semantic
and boundary-sensitive hashes, five schedules, 18 target-free fixture families,
30 refusal IDs, and strict caps. The primary BrainFlow playback rule preserves
old timestamps; primary LSL disables automatic postprocessing; PyXDF audits raw
and corrected views separately. No interpolation, silent sorting, or
deduplication is allowed.

Measured registration boundary: seven focused invariant tests pass. Optional
dependencies installed/imported, fixtures generated, source chunks emitted,
socket/board/stream/XDF operations, real/consumed/cache/target/model/training/
decoder/network accesses, and output artifacts are all zero. This is protocol
evidence, not compatibility level 6 and not a runtime result.

Next boundary: review may authorize Stage A pure-Python synthetic replay only.
Registration cannot authorize BrainFlow, LSL, PyXDF, hardware, S20, live data,
or any signal-quality, task, neural-advantage, decoding, latency, portable, or
clinical claim.

Evidence: `docs/RW3_PRIMARY_SOURCE_RESEARCH.md`,
`docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md`,
`registries/replay_equivalence_contract.v0.json`, and commit `c3d1f01`.

## 0046 - Prepare a hash-bound RW3 Stage A decision without authorizing code

Decision: issue one human-readable authorization packet and one machine-readable
request for RW3 Stage A pure-Python synthetic replay. Keep `authorized_now`
false, preserve every implementation flag in the frozen contract as false, and
require a separate authorization-only commit before any implementation.

Why: “continue,” issue activity, or general approval is too ambiguous for a
stage that precedes sockets, boards, and acquisition adapters. The next decision
must bind the exact `c3d1f01` contract hash, future files and commands, five
schedules by 18 fixture families, all 30 refusal IDs, one-thread resource caps,
forbidden work, measurements, and proceed/park/kill rules.

Frozen request: Stage A proposes 90 target-free standard-library transport
cases, strict source-chunk save/load/validate/summary/resume mechanics, and
deterministic reports. It does not authorize BrainFlow, LSL, PyXDF, sockets,
network access, device discovery, hardware, XDF, real or consumed recordings,
targets, labels, text, models, decoders, training, filtering, cleaning,
resampling, interpolation, or Stages B-D.

Measured decision boundary: ten dependency-free contract/request invariants
pass, including exact contract-hash binding and proof that the request remains
unauthorized. Source chunks, fixtures, runtime CLI additions, optional imports,
data reads, model runs, training runs, and generated payload artifacts are zero.

Next boundary: the user may explicitly authorize Stage A exactly as scoped,
request an amendment, or hold it. Authorization must first be recorded, tested,
committed, and pushed without implementation. Only then may Stage A work begin.

Evidence: `docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md`,
`registries/rw3_stage_a_authorization_request.v0.json`, tests in
`tests/test_replay_equivalence_contract.py`, and commit `163ff2f`.

## 0047 - Freeze Loop 24 local precision/runtime before candidate execution

Decision: preregister Loop 24 at commit `186bb6f` as primary-source research,
one versioned machine contract, and nine dependency-free invariants only. Keep
every execution flag false. Require a separate exact authorization, amendment,
or hold before creating a fixture, implementing a candidate, loading or
converting the checkpoint, running inference, timing, profiling, energy
measurement, or qualification.

Why: the frozen synthetic producer has only 1,130 parameters, so import cost,
warmup, Python decoder work, backend choice, thread pools, and timer noise can
dominate arithmetic. Float16 tensor storage does not prove a faster CPU kernel;
dynamic qint8 packed weights still accept and return floating-point tensors;
smaller serialization does not prove lower runtime; and unchanged final text
can conceal unstable incremental decoder traces. Candidate code or measurements
before thresholds would allow the protocol to favor whichever path looked best.

Frozen contract: `neurodecodekit.local_precision_runtime_contract` v0.1.0
binds the exact Loop 23.5 reference hashes and permits only float32 eager,
explicit CPU float16, and dynamic-qint8 QNNPACK candidates. It registers fresh
target-free selection and qualification partitions at seeds 2401 and 2402,
six waveform families with eight items each, 12 balanced selection timing
rounds, exact frame/timestamp/greedy/prefix/flush behavior, numerical
tolerances, separate storage and runtime rules, one-thread resource caps, and
30 refusal IDs. Targets, labels, text, consumed evidence, real data, training,
and RW3 operations must remain at zero.

Measured registration boundary: the contract SHA-256 is
`58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d`.
Nine focused invariants pass in 0.070 seconds wall with 20,791,296-byte peak
RSS. The complete optional environment reaches 277 unittest and 274 pytest
passes, with three optional skips and 25 pytest subtests; the true zero-
dependency run reaches 265 tests with 118 expected optional skips. Candidate
implementations, fixtures, checkpoint reads, inference/model/training runs, and
generated payload artifacts are zero.

Next boundary: the user may use the exact authorization sentence in
`docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`, request an amendment, or
hold. Loop 24 authorization cannot authorize RW3 Stage A, data access, model
training, or any neural, decoding, end-to-end-latency, cross-device energy, or
portable-hardware claim.

Evidence: `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`,
`registries/local_precision_runtime_contract.v0.json`,
`tests/test_local_precision_runtime_contract.py`, and commit `186bb6f`.

## 0048 - Define Loops 25-44 as an evidence-driven planning contract

Decision: replace the earlier six-row provisional continuation with one exact
20-loop planning tranche covering IDs 25 through 44. Group the work into five
phases of four loops: causal evidence, translation/generalization,
reliability/confounds, reproducibility/local deployment, and live
translation/release. Keep every row `Not Started`,
`execution_authorized: false`, and `proof_posture: planned_not_authorized`.

Why: the project's main gap is no longer basic pipeline availability. Real S21
cross-session MEG and S7 EEG comparisons are negative, consumed evidence must
stay closed, and no neural advantage, unseen-person transfer, causal real-
neural result, end-to-end latency, or portable device has been demonstrated.
Primary sources identify causal preprocessing, data quantity versus sentence
diversity, neural-token and language ablations, participant variability,
patient/no-keypress translation, sensor/device non-equivalence, clock domains,
provenance, privacy, abstention, and independent reproduction as the work that
can move those claims.

Contract: `neurodecodekit.next_twenty_loops_roadmap` v0.1.0 records exactly 20
contiguous IDs, five phase groups, protected S7/S21 evidence and consumed seeds
2203/2303/2353, global one-thread and 32-MiB defaults, detailed build/research
deliverables, controls, primary metrics, acceptance and stop rules,
dependencies, authorization boundaries, resource caps, 12 primary sources, and
row-level source bindings. Nine dependency-free invariants protect the count,
phase structure, backward-only dependency graph, source coverage, protected
evidence, false execution flags, and human-document agreement.

Authorization boundary: this is a roadmap result only. It does not authorize
Loop 24, RW3 Stage A, a Loop 25-44 preregistration or implementation, a fixture,
download, real or consumed data read, target access, model or decoder run,
training, optional streaming import, socket, board, device, or hardware session.
General continuation and approval of the roadmap are not experiment
authorization.

Measured planning result: focused invariants pass 9/9 in 0.070 seconds wall
with 18,071,552-byte peak RSS. The optional environment reaches 286 unittest
passes with three skips and 283 pytest passes with three skips plus 105
subtests; the true zero-dependency environment reaches 274 tests with 118
expected optional skips. The new nine-sheet tracker is 75,181 bytes with
SHA-256
`775e907e63277fd42e536421715ce116adfb837b71bfdf270e70024dd39a13aa`;
tracked and delivered copies match and the render/reload/formula audit passes.

Evidence: `docs/NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOPS_25_44_ROADMAP.md`, `registries/next_20_loops.v0.json`,
`tests/test_next_20_loops_contract.py`, the `Loops 25-44` workbook sheet, and
commit `56a1c0a`.

## 0049 - Authorize only the frozen target-free Loop 24 gate

Decision: record the user's explicit Loop 24 authorization as a conservative
scope amendment bound to parent commit `4050b85` and the unchanged contract
SHA-256
`58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d`.
After this authorization-only milestone is tested, committed, pushed, and its
CI confirmed, authorize only the registered target-free fixture, frozen
checkpoint validation, three precision candidates, inference, selection,
conditional one-time qualification, reports, and CLI surface.

Why: the user also named real data and training, but adding either to Loop 24
would mutate a preregistered no-target/no-training precision experiment after
its thresholds, seeds, access counters, and candidate set were frozen. Preserve
that ambition by routing causal preprocessing to Loop 25, separately authorized
real validation-only model work to Loop 26, and metadata-only fresh-holdout
research to Loop 27. Do not reopen S21 source-test/session-2, S7, or consumed
seeds 2203, 2303, and 2353.

Authorization boundary: the immutable `186bb6f` contract retains every false
authorization field and its original hash. The separate decision makes only
eight target-free fields true. Real or consumed data, targets, labels, text,
training or parameter updates, new architectures, energy measurement, RW3,
BrainFlow/LSL/PyXDF/sockets, devices, hardware, and Loops 25-44 execution remain
false. This authorization itself creates no fixture, checkpoint read,
candidate, inference, timing, profiler, energy, or qualification result.

Measured authorization-only result: seven new invariants raise the optional
suite from 286 to 293 unittests and from 283 to 290 pytest passes, with three
skips and 105 pytest subtests unchanged. The true zero-dependency suite rises
from 274 to 281 tests with 118 expected skips. The combined 26-test Loop 24 and
RW3 boundary takes 0.210 seconds wall with 21,397,504-byte maximum RSS. Full
optional unittest/pytest wall maxima are 19.880/20.120 seconds and
565,280,768/578,502,656 bytes; the zero-dependency run takes 0.650 seconds wall
and 41,435,136 bytes. The nine-sheet tracker is 75,648 bytes with SHA-256
`4be4012eea926b2b417fca3da1665e1f192718a50d5243aebf5d38f02841afb9`;
render, reload, range, and formula-error checks pass.

Next boundary: push this authorization-only commit and confirm CI before
implementation or any registered fixture/checkpoint operation. Then execute
only the frozen selection-before-qualification order. A Loop 24 result cannot
establish neural information, real-data accuracy, retained neural accuracy,
end-to-end latency, EEG usefulness, portable hardware, assistive benefit, or
clinical utility.

Evidence: `docs/LOOP_24_AUTHORIZATION_DECISION.md`,
`registries/loop24_authorization_decision.v0.json`,
`tests/test_loop24_authorization_decision.py`, and the tracker `24-AUTH` row.

## 0050 - Park Loop 24, retain float32, and leave qualification unopened

Decision: close Loop 24 as `park_resource_cap_exceeded` after its one
preregistered target-free selection. Retain `float32_eager_reference`; consume
selection seed 2401; do not open or repurpose qualification seed 2402; do not
tune worker startup, thresholds, fixtures, candidates, or tolerances and rerun
under the same evidence claim.

Why: all 12 balanced rounds and 36 sequential workers completed over 990
frames, and the timing protocol itself passed. Float16 preserved every exact
decoder behavior and numerical tolerance, but its producer/full median latency
ratios were `1.169950`/`1.087904`, so it was slower and also missed the
storage-only rule. QNNPACK qint8 proved the required
`quantized::linear_dynamic` operator and reduced deterministic numeric payload
to `47.10%`, but it changed greedy/prefix behavior, exceeded four numerical
tolerances, and had producer/full ratios of `2.784595`/`1.812123`. Neither
candidate qualified. Complete internal runtime was 65.154951 seconds against
the frozen 60-second cap.

Resource and access boundary: the 136,888-byte fixture plus 125,934-byte gate
output totals 262,822 bytes under 4 MiB; working arrays are 455,472 bytes;
maximum worker RSS is 222,248,960 bytes under 1 GiB. Qualification opens,
training, parameter updates, target/label/text reads, real/S7/S21 reads,
consumed-seed reads, network calls, energy measurements, and RW3 operations are
all zero.

Next boundary: Loop 25 is the next numbered planning candidate because Loop 24
now has an explicit park decision. The park does not authorize Loop 25. A
separate causal-preprocessing preregistration and explicit authorization must be
recorded, tested, committed, and pushed before any fixture, transform, cache
read, model operation, runtime, or generated payload.

Evidence: `docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md`, implementation commit
`3a5dc0b`, ignored audit-bound report SHA-256
`f877b7d88b00ce93ee8dd5091a6a0ba973c28a5d33d0a6972ca4dc82405dc098`, and
the tracker `24-RUN` row.

## 0051 - Freeze Loop 25 causal preprocessing before any numerical work

Decision: preregister one target-free stateful causal preprocessing path at
commit `a36d97b`, then prepare a separate hash-bound authorization request while
keeping every execution field false. The registration snapshot is immutable;
any future authorization must be recorded in a new tested, pushed, remotely
green decision commit before filter design, fixture generation, numerical
preprocessing, partition access, CLI work, or runtime.

Why: the current real sentence path is valid offline plumbing, but its default
zero-phase filters, whole-recording resampling, whole-recording or train-fit
normalization, sentence endpointing, and post-context behavior do not prove a
causal upstream path. Loop 21's zero-lookahead frame producer therefore cannot
carry the full streaming claim by itself. The smallest useful next gate is one
explicit transform chain whose future independence, timestamps, state, and
resource behavior are falsifiable without targets or protected evidence.

Frozen registration: five float32 channels enter at 1000 Hz; one stateful 50 Hz
Q30 notch SOS and one stateful fourth-order 0.5-45 Hz Butterworth SOS run in
float64; absolute global source indices divisible by ten produce 100 Hz output;
contract-fixed center/scale values and an inclusive +/-5 clamp precede one
float32 output cast. Seeds 2501 and 2502 define physically separate 12-item
development/qualification partitions over six signal families. Seven chunk
schedules, ten resume cuts, three future-mutation cuts, 40 refusal IDs, 21
access counters, exact timing/state gates, and one-time qualification order are
frozen.

Authorization boundary: the machine request is bound to green registration
commit `a36d97b8556e95637a21c86c44095b7e8d4c4863` and contract SHA-256
`42781526225c556d0df54d1b6924fd5d9ecf95578a84c3e3922b6d5c7035050e`.
`authorized_now` and all 15 nested authorization fields are false. Even exact
authorization excludes real or consumed data, targets, labels, text,
predictions, checkpoints, model inference, training, network access, RW3,
streams, devices, hardware, and Loop 26. Seeds 2501/2502 remain unopened; seed
2402 cannot be repurposed.

Resource and verification result: the registration added 76,196 tracked bytes.
The decision packet, machine request, and request tests add 24,316 bytes; the
tracker workbook grows by 918 bytes to 77,394 bytes. The combined Loop 25 and
roadmap boundary passes 27 tests in 0.14 seconds wall with 22,216,704-byte
maximum RSS. The preregistration commit passed both GitHub CI jobs. No fixture,
filter coefficient, partition, numeric payload, cache read, target/model read,
training run, network call, RW3 operation, or device operation occurred.

Next boundary: explicitly authorize the exact packet, amend it before
authorization, or hold. A future passing Loop 25 can establish only one
target-free causal preprocessing mechanics result. It cannot establish official
Brain2Qwerty v2 equivalence, neural information, decoding accuracy, CER/WER
improvement, end-to-end latency, unseen-person transfer, EEG/MEG usefulness,
portable hardware, assistive efficacy, or clinical utility.

Evidence: `docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md`,
`registries/causal_preprocessing_contract.v0.json`,
`docs/LOOP_25_AUTHORIZATION_PACKET.md`,
`registries/loop25_authorization_request.v0.json`, the tracker `25-REG` row,
and GitHub CI run `29193935671`.

## 0052 - Supersede Loop 25 anti-alias scope before authorization

Decision: preserve every v0 registration and request byte as immutable history,
but withdraw v0 as an actionable execution scope before authorization. Replace
it with `causal_preprocessing_contract.v1.json`, whose dedicated causal
anti-alias stage and complete folding-band gate must pass before development
seed 2501 can open. Keep every v1 `authorized_now` field false and prepare a
new request bound to green amendment commit `b6b92d8`.

Why: the v0 path treated its fourth-order 0.5-45 Hz task bandpass as the
anti-alias filter for 10x decimation and checked only 60 Hz at -6 dB above the
new 50 Hz Nyquist. It left almost all of the 50-500 Hz source folding band
unbounded. The official Brain2Qwerty dependency manifest pins NeuralSet 0.2.2,
whose extractor applies notch, bandpass, a separate MNE `Raw.resample`, and
then scaling. MNE 1.11's default is an offline complete-signal FFT resampler,
so it proves a separate anti-alias responsibility but is not itself eligible
for this zero-lookahead runtime.

Amended design: add one stateful elliptic SOS created by
`scipy.signal.iirdesign` with a 45 Hz passband edge, at most 1 dB passband loss,
a 50 Hz stopband edge, and at least 60 dB designed stopband attenuation. Audit
65,537 inclusive points from 0-500 Hz, 23 exact source-to-output alias probes,
the dedicated stage, and the complete chain. Require no greater than -59.5 dB
throughout 50-500 Hz, at most 17 total SOS sections, a 1,360-byte filter-state
array, stable poles, finite impulse/step behavior, and explicit ripple,
ringing, transition-band, and frequency-dependent-delay warnings. Preserve the
seven schedules, ten resume cuts, three future-mutation cuts, seeds 2501/2502,
one thread, 8 MiB artifact cap, and 45-second internal cap. The refusal surface
grows from 40 to 45 and the access ledger from 21 to 23.

Evidence order: after a future exact v1 authorization-only commit is tested,
pushed, and green, coefficients may be designed once and hash-bound. The
static pole/response/alias/impulse/step gate then runs before fixture metadata
or arrays are opened. Any static failure parks with seeds 2501 and 2502 both
unopened. Qualification remains conditional on one frozen complete development
pass. No threshold can move after protected access.

Provenance and verification: v0 contract SHA-256
`42781526225c556d0df54d1b6924fd5d9ecf95578a84c3e3922b6d5c7035050e`
and v0 request SHA-256
`3d103a0a18bd1d9ea8b320cde9515f891e41646c51132ad9c7adea35838f04b4`
remain exact. V1 contract SHA-256 is
`ecec99a7cc505ec0256c01c3c1e8aeaa05323ab54a71528323fa6d32bd289141`.
Commit `b6b92d8ea1cdeadfd6b7cd9f4704aee018516197` passed both GitHub CI jobs in
run `29195938038`. Its local suite passed 342 tests with three expected skips;
11 new amendment invariants and the immutable-v0 checks pass. The updated
nine-sheet tracker is 78,492 bytes with SHA-256
`483fde426c8212e7956814462b0aa11b0ca8426163b3dad95f6574eb7e10eb92`;
it reloads with zero formula-error matches.

Authorization and claim boundary: the replacement request remains an
authorization request only. All 16 request-level authorization flags are
false. No coefficient, fixture, seed, numerical preprocessing, raw/cache/data,
target/label/text/prediction, checkpoint, model, training, network, RW3,
stream, device, or hardware operation occurred. The next numbered decision is
to authorize v1 with the exact sentence in
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`, amend again, or hold. Neither this
amendment nor a future mechanics pass establishes official numeric equivalence,
acceptable filter phase/ringing for neural decoding, neural information,
CER/WER improvement, end-to-end latency, transfer, portable sensing,
assistive efficacy, diagnosis, or clinical utility.

Evidence: `docs/LOOP_25_ANTI_ALIAS_AUDIT.md`,
`docs/LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md`,
`registries/causal_preprocessing_contract.v1.json`,
`docs/LOOP_25_AUTHORIZATION_PACKET_V1.md`,
`registries/loop25_authorization_request.v1.json`, tracker row `25-AA`, and
GitHub CI run `29195938038`.

## 0053 - Close Loop 26 planning research without preregistering execution

Decision: mark Loop 26 planning research complete while leaving the experiment
status `Not Started`, its Loop 25 dependency unsatisfied, and every one of its
14 `authorized_now` fields false. Do not create a Loop 26 experiment contract,
authorization request, runtime module, model, fixture, or payload from this
decision.

Why: the existing source protocol has only six reserved validation sentence
instances from one person and one session. It can support exactly 64 paired
sign assignments, giving a minimum attainable two-sided p-value of 0.03125
when all six differences are nonzero. It cannot support source-test,
cross-session, unseen-person, population, modality, device, or clinical claims.
The official Brain2Qwerty v2 reference is whole-sentence, noncausal, and
GPU-scale; copying it would neither fit this repository's bounded local goal nor
prove causality.

Future design recommendation: preserve the existing 2,908-parameter real CTC
size ceiling while replacing its symmetric kernel-3 padding with two left
samples and zero right context. Compare it with a 2,884-parameter linear signal
CTC plus the train-only no-signal prior, zero signal, target derangement,
channel derangement, and nonwrapping zero-filled time displacement. These are
recommendations, not frozen architecture, thresholds, seeds, or access order.

Access and resource boundary: this pass performs zero raw-signal, real-cache,
target, validation-prediction, source-test, session-2, checkpoint, model,
training, network, RW3, stream, board, device, or hardware operations. A future
preregistration may retain one thread, a 2,908-parameter ceiling, 20 total CPU
minutes across all candidate/control training, 1 GiB RSS, 32 MiB generated
bytes, and zero new downloads, but must freeze or amend those values before any
protected content opens.

Evidence: `docs/LOOP_26_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop26_research_boundary.v0.json`,
`tests/test_loop26_research_boundary.py`, roadmap commit `03605c5`, tracker row
`26-R1`, and GitHub CI run `29197895836`.

## 0054 - Select S25 metadata for Loop 27 and hold preregistration

Decision: select SpanishBCBL MEG S25 session 2 block 2 as the smallest strict
eligible same-modality/task holdout candidate, while leaving Loop 27
`Not Started`, preregistration unprepared, and all 18 authorization fields
false. Do not prepare an acquisition request until the source model, controls,
target-isolation procedure, and Loop 28 final decision rule are hash frozen.

Why: a one-thread pinned metadata selector examined 315 MEG entries, found 23
clean single-FIF/log pairs and 16 eligible pairs, and ranked exact bytes after
canonical identity and cohort exclusions. S21 block 2 is smaller but observed.
S23 is also smaller but the official dataset card excludes that participant for
a metallic implant. S20 is task-matched EEG, not a compatible transfer holdout
for the 102-magnetometer source model. S25 is the first eligible pair and has no
published alias with the observed S5/S10/S21 person.

Selected identity: `MEG/FIF/25_12032/240530/block2.fif` is 1,009,713,753
bytes and `MEG/logs/S25-session2_block2_list1.mat` is 226,230 bytes. Their
exact total is 1,009,939,983 bytes, leaving 63,801,841 bytes under a future 1
GiB cap. Official Git blob, LFS SHA-256, Xet, and last-file-commit identities
are frozen in the research registry. The local MAT path is present at the
expected size but was not hashed or opened; the raw FIF is absent.

Future design boundary: use S25 final-only with zero candidate training,
validation, or calibration rows. Require at least 48 performed unique rows as
a pragmatic retention floor, not a prospective power claim. Freeze the source
model and no-signal/corrupted-signal controls before candidate content. An
unseen-person claim may disclose familiar sentence overlap; an unseen-text
claim requires a future zero-overlap audit. Any S25 failure parks without
automatic S18, S24, or S22 substitution.

Resource and access result: the measured selector took 3.10 seconds wall and
63,766,528-byte peak RSS using one thread/worker. Candidate payload downloads,
local MAT payload hashes, FIF header/signal reads, MAT/target reads, source
consumed-evidence reads, model/checkpoint runs, training updates, RW3, streams,
boards, devices, and hardware operations are all zero.

Evidence: `docs/LOOP_27_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop27_research_boundary.v0.json`,
`tests/test_loop27_research_boundary.py`, roadmap commit `b3d61b6`, tracker row
`27-R1`, and GitHub CI run `29199178320`.

## 0055 - Reserve S25 for strict zero-shot and separate calibration

Decision: close Loop 28 planning research while leaving its experiment `Not
Started`, its Loops 25-27 dependencies unsatisfied, and all 21
`authorized_now` fields false. Reserve the selected S25 block for a future T2
strict unseen-person zero-shot test with zero target-person fit, validation,
calibration, target-wide normalization, subject embedding, adapter, threshold,
or unlabeled corpus-adaptation rows. A calibrated-transfer curve requires a
different physically separated design and may never be relabeled as zero-shot.

Why: Brain2Qwerty v2 is an important asynchronous continuous-sentence
reference, but its paper explicitly says the current architecture is
whole-sentence and noncausal. Its main joint model includes each target
participant during training and uses a participant-index-conditioned affine
layer. Its leave-one-out comparison excludes the target participant during
pretraining and then finetunes on that participant. Those results support
participant-aware and calibrated transfer research, not strict unseen-person
zero-shot decoding. Public cross-subject MEG and BCI benchmarking work likewise
shows that participant/session domain shift and evaluation context must be
named rather than averaged away.

Future T2 rule: require at least 48 eligible unique performed S25 rows. Freeze
the source checkpoint, source-train-only no-signal prior, exact-zero signal,
channel-name-hash derangement, nonwrapping zero-filled time displacement, all
predictions, and the scorer before final target text opens. Pass only with at
least 0.05 absolute macro sentence-CER improvement over the prior, one-sided
paired `p <= 0.05` from 65,535 deterministic sign assignments plus observed,
and strictly lower macro CER than every corruption control. Ties, missing
fields, threshold misses, control failures, hash/access/resource violations,
or fewer than 48 rows park T2. Failure permits no restart, calibration,
threshold change, or backup substitution.

Claim boundary: a future pass can support only T2 for this one S25 canonical
person/session/task. It cannot establish population generalization. It can add
an unseen-text label only if a separately authorized redacted hash audit finds
zero source overlap. Unlabeled target-corpus adaptation is transductive, not
strict zero-shot. Brain2Qwerty v2 equivalence, low-latency operation, portable
sensing, at-home use, assistive efficacy, diagnosis, and clinical utility all
remain unestablished.

Access and resource result: this planning pass used ten high-level public-web
research operations and one GitHub metadata call, downloaded zero code/data
payload bytes, and performed zero S25 metadata/path/hash/header/signal/MAT/
target, consumed-evidence, model, training, calibration, final, RW3, stream,
board, device, or hardware operations. The 14 Loop 28 invariants pass in 0.08
seconds wall with 19,513,344-byte maximum RSS. External browser peak RSS and
end-to-end interactive research runtime are unavailable by tool contract.

Evidence: `docs/LOOP_28_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop28_research_boundary.v0.json`,
`tests/test_loop28_research_boundary.py`, and tracker row `28-R1`.

## 0056 - Choose local-first EEG and partner OPM-MEG lanes; hold execution

Decision: close Loop 29 planning research while leaving the portable-sensing
experiment `Not Started`, every one of its 24 `authorized_now` fields false,
and no device selected. Use scalp EEG as the immediate local-first
accessibility research lane, OPM-MEG as a same-modality partner/lab lane,
cryogenic MEG as the scientific reference, and non-neural wearables as controls
or separate accessibility inputs.

Why: Brain2Qwerty v2's random 76/153/230-channel subsets come from the same
306-channel cryogenic MEGIN system and preserve its room, electronics, clocks,
geometry, and noise field. They are model sensitivity evidence, not OPM-MEG or
EEG qualification. OPM-MEG has measured speech tracking and real-time evoked-
response mechanics, but current human systems still require specialist
shielding, field control, geometry, motion tracking, and interference
suppression. Scalp EEG has practical local hardware and repeated at-home
recording evidence, but task-matched Brain2Qwerty EEG remains substantially
weaker than MEG and dry systems carry reference, placement, low-frequency,
motion, muscle, and clock risks. Home recording is not home text decoding.

Future evidence boundary: preserve a 15-field cross-modality matrix, four
modality profiles, six noncollapsible qualification levels, and 12 minimum
future device-packet gates. A named device may proceed only when task, units,
filters, reference, geometry, clocks, packets, locality, privacy, repeated-
session, peripheral-control, licensing, and resource requirements can be
measured directly. Vendor specifications, SDK imports, waveform plots, and
successful file reads cannot skip qualification levels.

Storage and real-data boundary: record the user's additional capacity as
5,000,000,000 preferred and 10,000,000,000 absolute incremental bytes. This is
capacity permission, not download permission. The separately gated S20 EEG
packet is 96,090,264 bytes and the selected S25 MEG pair is 1,009,939,983
bytes, for exactly 1,106,030,247 bytes combined and 3,893,969,753 bytes of
preferred-capacity margin. Existing authorized S21 source material should
answer the first source question before any additional source block is
selected; unused space is not a collection target.

Access and resource result: this research used 14 high-level public-web
operations, one CPU thread and worker, and zero remote code/data payload
downloads. It performed zero S20/S25 or consumed-data path/hash/header/signal/
target reads; checkpoint/model/training/calibration runs; SDK imports; sockets;
streams; device purchases; participant/partner outreach; or hardware sessions.
External interactive runtime and peak RSS are unavailable from the research
tool contract and are reported as unavailable rather than estimated.

Evidence: `docs/LOOP_29_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop29_research_boundary.v0.json`,
`tests/test_loop29_research_boundary.py`, roadmap row 29, tracker decision
`29-R1`, risk `R34`, research commit `f5fc740`, push CI run `29204700023`, and
draft PR #8 CI run `29204804483`.

## 0057 - Define a target-free local replay inspector; hold execution

Decision: close Loop 30 planning research while leaving its local streaming
experiment `Not Started`, every one of its 30 `authorized_now` fields false,
and no seed, trace, fixture, UI, server, or browser run created. Define the
future product as a loopback-only target-free replay inspector. Artifact,
synthetic, recorded, and live source modes remain distinct; only artifact and
new synthetic replay may enter a future Loop 30 packet.

Why: Brain2Qwerty v2 is continuous but still whole-sentence and noncausal, so
asynchronous output is not a low-latency end-to-end result. Loop 21 proves a
causal producer without a text or capture-latency claim. Loop 23 then shows
that a zero-revision trace can remain wrong: the consumed registered test
reached 5/8 exact against 6/8 while its partials recorded zero revisions.
Stability therefore cannot stand in for correctness or confidence.

Future interaction boundary: freeze a deterministic 30-field target-free
trace, nine clock domains, six latency claim levels, 18 pass requirements, and
30 exact refusals before implementation. Finalization is explicit rather than
inferred from no change. Source, backend, browser, and user-observed clocks keep
their origins and may not be subtracted without a measured mapping. Confidence
remains unavailable pending separate Loop 34 calibration, and the no-signal
comparator plus producer/decoder causality remain visible.

Privacy, accessibility, and browser boundary: bind exactly to `127.0.0.1` with
no host override, public share, analytics, monitoring, uploads, allowed
directory, static root, service worker, popup, or external network dependency.
Use one thread/worker and two sessions. Browser QA must record every request,
response, WebSocket, page, console error, 50-ms W3C long task, Event Timing
availability, screenshot, and overlap/blankness result. Incremental state uses
textual source/proof labels, status/log semantics, polite announcements,
keyboard access, stable focus, no forced autoscroll, and reduced motion.

Access and resource result: this planning pass used ten high-level public-web
research operations, one CPU thread and worker, and zero remote payload bytes,
real path/hash/header/signal/cache/target/consumed-artifact reads, checkpoint/
model/training/calibration runs, trace generations, server launches, browser
QA runs, SDK imports, sockets, streams, or hardware sessions. External browser
peak RSS and one end-to-end research runtime are unavailable by tool contract.
The current planning cap is 8 MiB; a future separately authorized prototype
remains under 32 MiB generated artifacts and 1 GiB peak RSS.

Claim boundary: this decision adds no running interface, live neural source,
causal end-to-end decoder, confidence, neural advantage, decoding accuracy,
unseen-person generalization, capture-to-user latency, portable hardware,
arbitrary-thought, assistive, diagnostic, or clinical result. A future Loop 30
authorization cannot authorize RW3, real data, a model, training, a device, or
hardware.

Evidence: `docs/LOOP_30_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop30_research_boundary.v0.json`,
`tests/test_loop30_research_boundary.py`, roadmap row 30, research commit
`958ac4e`, push CI run `29206964418`, and draft PR #9 CI run `29206972221`.

## 0058 - Separate sensor dependence, language gain, and neural origin

Decision: close Loop 31 planning research while leaving its attribution
experiment `Not Started`, all 19 `authorized_now` fields false, and no cache,
target, checkpoint, model, training, validation, language model, Neuro Token,
or fixture opened or created. Define a future 10-condition encoder matrix and a
separately gated 5-condition LLM/Neuro Token extension.

Why: the consumed S21 session-2 MEG model and S7 EEG classifier both lose to
their no-signal priors. A later language model could still produce fluent text
without repairing that upstream scientific failure. Brain2Qwerty v1 separates
encoder/transformer output from language-model correction, while v2 compares
the same LLM with and without MEG-derived Neuro Tokens. Those contrasts answer
different questions and must not be collapsed into one neural score.

Future encoder boundary: require full signal, train-only prior, exact-zero
signal, whole-item derangement, channel derangement, nonwrapping time
displacement, timing-only, conditional context-only, and train-pairing
derangement conditions on identical validation rows. Keep the nearly
parameter-matched linear signal CTC as an architecture diagnostic. Freeze all
transforms and prediction hashes before one target open; no validation target
may select a transform, fixture, condition, threshold, or restart.

Inference boundary: six validation sentences provide 64 exact sign assignments
when all paired effects are nonzero. Use an exact one-sided component test and
an intersection-union decision that requires every applicable control to pass.
At most one zero paired effect can still attain alpha `0.05`; two zeros make
the minimum one-sided p-value `0.0625`. Keep the recommended `0.05` primary
macro-CER margin unfrozen until preregistration, and print all six item effects.

Claim boundary: a future clean local encoder result may establish
sensor-signal dependence only for the exact person, session, task, split,
candidate, and conditions. Brain-specific neural contribution remains
unavailable until Loop 35 excludes EOG, EMG, motion, environmental, timing,
prompt, and action shortcuts. Language-prior gain is not neural gain, and a
Neuro Token drop result is conditional on identical CTC text and LLM context,
not total neural contribution.

Access and resource result: this research used 16 public network operations,
including eight GitHub API requests, one CPU thread/worker, and zero protected
cache/target/checkpoint/model/training/validation/LLM/S20/S25/stream/device
operations or downloaded data/model bytes. External research network bytes and
interactive peak RSS are unavailable from the tool contracts. A future run
retains one thread/worker, 2,908 parameters, 1,200 seconds total training, 32
MiB artifacts, 1 GiB RSS, and zero new data/model downloads.

Evidence: `docs/LOOP_31_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop31_research_boundary.v0.json`,
`tests/test_loop31_research_boundary.py`, roadmap row 31, research commit
`5455340`, push CI run `29208510571`, and draft PR #10 CI run `29208529886`.

## 0059 - Count calibration information, not just adapter parameters

Decision: close Loop 32 planning research while leaving its fresh-person
calibration experiment `Not Started`, all 22 `authorized_now` fields false,
and no candidate, participant payload, signal, label, checkpoint, adapter fit,
training run, or final evaluation opened. Recommend one pointwise causal
32-parameter hidden diagonal-affine adapter over the proposed frozen 16-wide
Loop 26 source encoder.

Why: participant adaptation is scientifically useful only when strict zero-
shot, unlabeled, label-light, and supervised information are not mixed.
Brain2Qwerty v2's leave-one-participant-out regime finetunes on the held-out
participant, so it is calibrated transfer rather than strict zero-shot.
CORAL and Euclidean Alignment use no target labels, but target signal still
influences their transforms; this is unlabeled transductive calibration. Loop
16 further shows that diagonal affine matching can repair an easy stationary
shift while harming channel-mixing and time-varying shifts.

Future mechanism boundary: use exactly 16 scales plus 16 biases before the
28-class projection, identity initialized, with zero additional temporal
context and all 2,908 base values frozen. The nested recommendation is `0, 2,
4, 8, 16, 32` unique completed calibration sentences. Label-light is capped at
eight labeled calibration sentences; supervised at 32. Any labeled selection
row counts in the headline supervision burden. Unlabeled mode may not use
target labels to select a budget, stopping rule, or threshold.

Future evidence boundary: require physically distinct calibration, selection,
and final recordings with at least 32, 16, and 48 unique completed sentences,
respectively, plus disjoint performed-row IDs and semantic text hashes. S25
session 2 block 2 stays final-only for Loop 28 and is ineligible. Hash-freeze
strict zero-shot final predictions before target-person calibration access,
then freeze one mode, adapter, and budget before one final-target open.

Future decision boundary: compare the selected adapter with frozen zero-shot,
an exact identity adapter, the source-train-only no-signal prior, robust
normalization-only, and label derangement where applicable. Recommend at least
`0.05` macro-CER gain versus both zero-shot and prior, a one-sided paired rule
with 65,535 random sign assignments plus observed, and strict wins over every
applicable control. The margins remain recommendations until preregistration.
Any tie, final harm, split/hash/access/resource failure, or selection-to-final
reversal parks the claim without restart.

Access and resource result: this research used six public network operations,
including two pinned GitHub source reads, one CPU thread/worker, and zero
protected payload, signal, target, model, adapter, training, evaluation, stream,
device, or hardware operations. Public transport bytes, end-to-end interactive
research runtime, peak RSS, and candidate-specific calibration minutes remain
unavailable. A future run stays under one thread/worker, 32 target-trainable
values, 1,200 adapter-fit seconds, 1 GiB RSS, and 32 MiB outputs. The user's
5-10 GB capacity envelope is not authorization.

Claim boundary: this decision creates no zero-shot, calibrated-person, sensor-
signal, brain-specific, population, real-time, portable-device, at-home,
assistive, diagnostic, or clinical result. Even a future clean one-person pass
must be labeled by its exact mode and burden.

Evidence: `docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop32_research_boundary.v0.json`,
`tests/test_loop32_research_boundary.py`, roadmap row 32, research commit
`8109b10`, push CI run `29209987034`, and draft PR #11 CI run `29209996914`.

## 0060 - Spend the shared validation event once

Decision: close Loop 33 planning research while leaving the bounded data-
scaling experiment `Not Started`, all 23 `authorized_now` fields false, and no
protected cache, signal, target, checkpoint, model, training, score, physical-
repetition study, or acquisition opened. Recommend strictly nested source-
train prefixes of `8, 16, 24, 32, 44, 55` unique sentence instances, at most
three optimization seeds and 18 candidate fits, and a size-matched train-only
no-signal prior at every point.

Why: the six reserved source-validation sentences are the project's remaining
prospective local predictive evidence. Loop 26, Loop 31, and Loop 33 can answer
their compatible questions in one target open only if all architectures,
prefixes, seeds, controls, predictions, and payload hashes freeze first. If
Loop 26 opens those targets before Loop 33 freezes, a later curve is exploratory
and cannot support the registered scaling or acquisition decision.

Scientific boundary: Brain2Qwerty v2 reports a five-condition log-linear trend
through approximately 90 pooled hours and a matched advantage for 256 unique
sentences over 128 sentences repeated twice. Image-decoding and long-duration
overt-speech EEG studies also report data-scale effects. Their people, tasks,
modalities, supervision, language coverage, models, and compute differ. No
published exponent or saturation point is transferred to one local person,
six validation sentences, and a 2,908-parameter model.

Repetition boundary: current metadata supports a unique-sentence prefix curve
only. Duplicating, resampling, reweighting, augmenting, or reslicing one array
does not create a physical repeated acquisition. A repetition-efficiency claim
requires distinct performed recordings of the same normalized prompt, matched
physical trial counts, and its own metadata review, preregistration, and exact
authorization.

Future decision boundary: report macro sentence CER by item, seed, size, and
matched prior; every adjacent delta; descriptive slopes against `log2(unique
sentences)`; and exact resource/access/hash ledgers. Recommend a `0.05`
smallest-band to upper-band gain, a `0.05` upper-band gain over matched priors,
and negative slopes for every registered seed. Those rules remain unfrozen
until preregistration. Do not fit a formal power law, call optimizer seeds
biological replicates, or extrapolate beyond 55 sentences.

Access and resource result: this research used six public web operations, one
CPU thread/worker, and zero protected payload, signal, target, model, training,
scoring, S20/S25, stream, device, or hardware operations. Future execution
stays under one thread/worker, 18 candidate fits, 1,200 total training seconds,
1 GiB RSS, 32 MiB outputs, and zero new downloads. CPU time is not energy. The
user's 5-10 GB capacity envelope is not access or acquisition authorization.

Claim boundary: no learning curve, neural advantage, universal scaling law,
repetition-efficiency result, saturation finding, acquisition value, unseen-
person generalization, real-time behavior, portable hardware, at-home use,
assistive efficacy, diagnosis, or clinical result exists.

Evidence: `docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop33_research_boundary.v0.json`,
`tests/test_loop33_research_boundary.py`, roadmap row 33, research commit
`25724de`, push CI run `29211291337`, and draft PR #12 CI run `29211306722`.

## 0061 - Keep confidence unavailable until independent evidence exists

Decision: close Loop 34 planning research while leaving the confidence,
abstention, and revision experiment `Not Started`, confidence unavailable, all
26 `authorized_now` fields false, and no fixture, feature, mapping, threshold,
target, scoring, product-confidence, protected-data, or download operation
opened. Separate seven confidence semantics and eight score/control roles.

Why: the six real source-validation sentences remain reserved for one shared
Loop 26/31/33 target open. They cannot also fit a confidence map, select a
score and abstention policy, and independently qualify that policy. Even six
observed successes give an optimistic one-sided 95% exact upper error bound of
approximately `0.393`, before accounting for within-person dependence.

Scientific boundary: raw log score, entropy, margin, or prefix stability may
rank predictions but is not a correctness probability. Calibration requires a
separately fit mapping and independent proper-scoring evaluation. Selective
risk, conformal bounded-risk control, revision stability, and product-visible
confidence are different claims. A synthetic pass cannot establish real
confidence.

Future design: recommend fresh target-free synthetic calibration, selection,
and final counts of `128/64/256`, grouped by generation block and schedule.
Fit probability or conformal mappings on calibration only; choose exactly one
score and policy on selection only; hash-freeze all code, mappings, thresholds,
predictions, and ledgers before opening final targets once. Exact-sequence
0/1 error is primary. Raw CER stays unclipped; optional bounded CER must be
separately named.

Metric boundary: report every registered working point, accepted and
generalized error, abstention, legacy AURC with its limitations, and an AUGRC-
equivalent area. ECE is secondary and unavailable for raw scores. An
abstain-all or below-minimum-coverage policy cannot pass. Revision count and
added delay must preserve Loop 30 clock domains.

Access and resource result: this research used five public web operations, one
CPU thread/worker, and zero protected payload, signal, target, model,
confidence fit, scoring, S20/S25, stream, device, or hardware operations.
Future synthetic execution remains under one thread/worker, zero decoder
training, six scalar mapping fits, 120 seconds, 1 GiB RSS, 16 MiB outputs, and
zero downloads. The user's 5-10 GB capacity envelope is not authorization.

Claim boundary: no calibrated confidence, abstention benefit, selective-risk
guarantee, neural advantage, decoding accuracy, unseen-person generalization,
real-time behavior, portable hardware, at-home use, assistive efficacy,
diagnosis, clinical result, or product-safety claim exists.

Evidence: `docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop34_research_boundary.v0.json`,
`tests/test_loop34_research_boundary.py`, roadmap row 34, research commit
`ad9d647`, push CI run `29213220777`, and draft PR #13 CI run `29213242970`.

## 0062 - Require recorded peripheral controls before bounded neural attribution

Decision: close Loop 35 planning research while leaving the peripheral-
confound experiment `Not Started`, all 31 `authorized_now` fields false, and no
fixture, synchronized peripheral acquisition, protected-data read, model,
training, scoring, device, or hardware operation opened. Freeze ten confound
classes, nine future synchronized stream classes, 13 comparison conditions,
three independently authorized stages, 24 future gates, and 32 refusal IDs.

Why: Brain2Qwerty v1 centers windows on known keypresses during physical typing.
Brain2Qwerty v2 removes that explicit timing at inference but still studies
overt prompted typing with audio, visual, motor, and somatosensory context.
Primary MEG/EEG evidence shows that task-linked eye, muscle, head/jaw motion,
and other artifact streams can carry predictive information. Calling an input
EEG or MEG, or artifact-rejecting it, does not prove physical origin.

Current-evidence boundary: S21's committed cache path has 102 magnetometers and
trigger timing but no synchronized EOG, EMG, gaze, motion, or audio stream. S7
source metadata names three ocular channels, but its consumed 61-channel cache
contains none. Current evidence can support a separately authorized timing
audit, not a complete peripheral firewall. Consumed S7/S21 evidence remains
closed and cannot become fresh Loop 35 qualification data.

Future design: recommend 32 physically and semantically distinct calibration
sentences, 16 selection sentences, and 48 final sentences. Select the strongest
peripheral comparator and one brain candidate on selection only, hash-freeze
every prediction/config/access ledger, then open final targets once. The
primary estimand compares all synchronized streams against the strongest
peripheral condition; the secondary compares brain-sensor-only against the
strongest nonbrain condition. Recommend a 0.05 practical margin for both,
65,535 paired sign assignments plus observed, an intersection-union decision,
and failure on ties. These recommendations are not yet preregistered.

Staging boundary: Stage A is target-free synthetic interface validation and
cannot claim biology. Stage B requires a new consented, synchronized multimodal
protocol and can establish at most incremental brain-sensor information beyond
recorded controls for the exact local protocol. Stage C no-keypress, attempted-
movement, or patient work is a separate ethics, population, task, and model
program. No stage self-authorizes the next, and missing controls may not be
imputed as zero, clean, or synthetic real evidence.

Access and resource result: this research used six public web operations, one
CPU thread/worker, and zero protected dataset/model bytes, real-cache reads,
target reads, model runs, training runs, acquisitions, S20/S25 operations,
streams, devices, or hardware operations. Public-network response bytes, tool
runtime, and tool RSS are unavailable from the browser contract. The user's
5-10 GB storage envelope is capacity, not access or acquisition permission.

Claim boundary: no peripheral-control result, incremental brain-sensor result,
absolute brain origin, language-intent decoding, no-keypress transfer, patient
benefit, population generalization, real-time behavior, portable hardware,
at-home use, assistive efficacy, diagnosis, clinical result, or product-safety
claim exists.

Evidence: `docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop35_research_boundary.v0.json`,
`tests/test_loop35_research_boundary.py`, roadmap row 35, research commit
`6f48363`, push CI run `29214860306`, and draft PR #14 CI run `29214881916`.

## 0063 - Treat harmonization as an explicit operator, not hidden equivalence

Decision: close Loop 36 planning research while leaving the geometry/reference
experiment `Not Started`, all 29 `authorized_now` fields false, and no fixture,
real header, signal, transform, unit conversion, rereference, compensation,
interpolation, model, training, stream, device, or hardware operation opened.
Freeze six representation layers, five modality profiles, a 24-field future
channel record, 12 operation classes, 16 fixture families, 22 gates, and 30
refusal IDs.

Why: BIDS separates channels from electrodes, signal units from coordinate
units, and coordinate-system semantics from coordinates. MNE separates device,
head, and MRI frames and treats rereference and interpolation as data-changing
operations. A matching label, channel count, standard montage name, integer
frame code, or visually similar layout cannot prove equivalence.

Identity boundary: allow only unique explicit reorder, versioned bijective
aliases, exact declared unit factors, and directional right-handed rigid
transforms as candidate identity-preserving metadata operations. Require frame
names, origin, axes, handedness, transform direction, orthogonality,
determinant `+1`, orientation-without-translation, source/config/transform
hashes, and a `1e-9 m` synthetic inverse-roundtrip ceiling. Unknown or custom
units, unknown frames, reflections, missing orientation, and ambiguous aliases
refuse rather than guess.

Signal boundary: EEG rereference, MEG compensation/projectors, signal-unit
scaling, bad-channel interpolation, sensor-to-template mapping, and zero-fill
change or synthesize signal values. They require signal access, their own
operator provenance, preserved missingness, frozen fit scope, and separate
authorization. Evaluation accuracy may not select a mapping.

Current-evidence boundary: S21 caches preserve names, MNE types, positions in
metres, integer frame/unit codes, and coil types but not a complete exchange-
frame, orientation, transform, and compensation ledger. Loop 11's within-cache
subsets are not cross-device evidence. The consumed S7 cache lacks a qualified
measured electrode and acquisition-reference contract. None was reopened.

Staging boundary: future Stage A is target-free synthetic metadata and can
establish only schema/refusal identity. Stage B is an exact real-header packet
with file, byte, field, and privacy caps and can establish at most declared
metadata compatibility. Stage C is a separately authorized signal-transform
protocol and can establish at most named protocol-specific numerical
compatibility. No stage establishes model transfer or device equivalence.

Access and resource result: this research used three high-level public web
operations, one CPU thread/worker, and zero protected download bytes, real
headers, signal/cache/target reads, fixtures, transforms, conversions,
rereference/interpolation, model/training runs, S20/S25 operations, streams,
devices, or hardware operations. Public-network response bytes and browser
runtime/RSS are unavailable. The user's 5-10 GB envelope is capacity only.

Claim boundary: no synthetic schema result, real metadata compatibility,
geometry compatibility, numerical compatibility, model transfer, device
equivalence, neural advantage, unseen-person generalization, real-time
behavior, portable hardware, at-home use, patient benefit, or clinical result
exists.

Evidence: `docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop36_research_boundary.v0.json`,
`tests/test_loop36_research_boundary.py`, roadmap row 36, research commit
`4d5c7d2`, push CI run `29216381237`, and draft PR #15 CI run `29216397245`.

## 0064 - Separate the BIDS envelope from non-standard NeuroDecodeKit payloads

Decision: close Loop 37 planning research while leaving the derivative export
experiment `Not Started`, all 29 `authorized_now` fields false, and no fixture,
exporter, derivative tree, validator install/run, protected payload, payload
hash, subject mapping, raw copy, external write, release/upload, model,
training, stream, device, or hardware operation opened. Freeze six export
layers, five artifact profiles, 15 standard-field mappings, 16 explicit
NeuroDecodeKit extension fields, 20 fixture families, four independently
authorized stages, 24 gates, and 32 refusal IDs.

Standard boundary: pin the researched interface to stable BIDS 1.11.1. Every
future derivative envelope needs exact `Name`, `BIDSVersion`, `DatasetType`,
`GeneratedBy`, and README behavior. File-level direct inputs use BIDS URIs;
named datasets resolve through `DatasetLinks`. Relative source paths and
`RawSources` are deprecated. Required source metadata propagates only while it
remains valid after processing.

Extension boundary: NeuroToken NPZ caches, signal/sentence caches, split
reports, report cards, and manifests have no stable BIDS derivative suffix.
They may live as explicitly non-standard versioned files inside a BIDS-
organized envelope, but the envelope cannot standardize them. Proposed BIDS
provenance fields are not treated as stable 1.11.1 requirements.

Identity and privacy boundary: replace local paths with resolvable BIDS URIs or
an opaque source hash plus an unavailable standard-source warning. Absolute
paths, usernames, home roots, traversal, case collisions, subject/session/item
collisions, overwrite, symlinks, hardlinks, shared inodes, direct identifiers,
and unreviewed source labels refuse. Loop 38 must qualify privacy, license,
identifier, retention, and lifecycle behavior before real or public export.

Payload boundary: future export is schema- and stage-allowlisted, never a
recursive copy. Known raw extensions, raw-permissible filenames, full or
sampled raw-byte duplicates, targets, prompts, responses, sentence text,
unrestricted free text, unknown payloads, and incompatible licenses refuse.
Raw copy files, duplicate bytes, and shared inodes must remain zero.

Validator boundary: future Stage B may pin official validator `2.4.1` as an
optional offline tool after separate authorization. Its complete issue ledger
must be retained. A passing validator can establish only the standard-envelope
behavior it checks; it cannot standardize custom payloads or validate source
hashes, privacy, license, scientific provenance, cross-machine
reproducibility, neural advantage, or decoding accuracy.

Staging boundary: Stage A is target-free synthetic metadata/refusal behavior.
Stage B adds one bounded synthetic payload and optional validator. Stage C is
named local real-derived metadata only after Loop 38. Stage D is public release
only after privacy/license, cross-machine, and claim-promotion gates. No stage
self-authorizes the next.

Access and resource result: this research used seven high-level public web
operations including two official GitHub repository reads, one CPU
thread/worker, and zero generated derivative bytes, tracked neural/model binary
candidate files, protected downloads, real header/cache/signal/target reads,
payload hashes, fixtures, validator runs, raw copies, releases, uploads, models,
training runs, streams, devices, or hardware operations. Public-network
response bytes and browser runtime/RSS are unavailable. Future Stage A remains
capped at 120 seconds, 1 GiB RSS, 16 MiB, 128 files, zero network/download
bytes, zero raw-copy bytes, and no base dependency.

Claim boundary: no BIDS-organized synthetic bundle, validator-assessed
envelope, source-bound real provenance bundle, privacy/license qualification,
cross-machine reproduction, public release, neural advantage, decoding
accuracy, unseen-person generalization, real-time behavior, or portable-
hardware result exists.

Evidence: `docs/LOOP_37_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop37_research_boundary.v0.json`,
`tests/test_loop37_research_boundary.py`, roadmap row 37, research commit
`ef31efc`, push CI run `29226436884`, and draft PR #16 CI run `29226853455`.

## 0065 - Keep Neural-Data Privacy, Deletion, And Sharing Claims Separate

Decision: close Loop 38 planning research while leaving the privacy/lifecycle
experiment `Not Started`, all 32 `authorized_now` fields false, and no fixture,
scanner, deletion, protected-root scan, identity attack, consent or legal
determination, Git history rewrite, remote cleanup, public release/upload,
model, training, stream, device, or hardware operation opened. Freeze five
sensitivity levels, eight artifact classes, ten lifecycle surfaces, 12
sensitive-field classes, 12 threat scenarios, five deletion-receipt levels, 24
fixture families, four independently authorized stages, 26 gates, and 36
refusal IDs.

Framework boundary: pin stable NIST Privacy Framework 1.0 because 1.1 remains
an initial public draft. Map future controls to NISTIR 8062 predictability,
manageability, and disassociability and use PRAM as a risk method, never a
certificate. Treat OECD stewardship and anti-hype guidance as governance, not
proof of local compliance.

Sensitivity boundary: raw signals, windows, continuous caches, embeddings,
Neuro Tokens, checkpoints, and individual predictions default sensitive.
Subject/session/trial identity, high-resolution timing, geometry, stable
hashes, pseudonyms, and small individual rows remain potentially linkable.
Compression, feature extraction, hashing, or technical de-identification does
not automatically lower sensitivity or create sharing authority.

Lifecycle boundary: separately inventory approved raw/cache/run roots, OS
temporary files, logs, backups/sync/trash/snapshots, Git worktree/index/history/
LFS, origin/forks/clones/PR refs, CI logs/caches/artifacts, and release/download
copies. A clean current tree cannot establish another surface is clean.
Unknown copies remain `unresolved`.

Deletion boundary: distinguish no claim, scoped path absence, local manifest
rescan, repository/remote coordination, and external media sanitization. A
future application receipt is dry-run by default, exact-root and manifest
bound, does not follow links, never deletes unrelated work, and cannot prove
SP 800-88 Rev. 2 media sanitization. Broad cleanup and history rewrite remain
separate explicit decisions.

Governance boundary: consent, license, de-identification, technical redaction,
retention, deletion, and public sharing authority are independent. Open Brain
Consent is a template, CC BY-NC is not participant consent, and a BIDS or
privacy-tool pass is not legal or institutional release clearance.

Access and resource result: six high-level public web operations and eight
official or primary source page opens informed the planning record. Public
response bytes and web runtime/RSS are unavailable. The metadata-only local
audit found zero current tracked neural/model candidate files and bytes and
zero candidate paths across all-ref Git history. Protected reads, fixtures,
scanners, deletions, history rewrites, identity attacks, models, training runs,
releases, uploads, streams, devices, and hardware operations remain zero.

Claim boundary: no synthetic privacy interface, named local-root coverage,
real-artifact lifecycle qualification, anonymous neural representation,
privacy-safe dataset, verified media sanitization, shareable release, neural
advantage, decoding accuracy, unseen-person generalization, real-time behavior,
or portable-hardware result exists.

Evidence: `docs/LOOP_38_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop38_research_boundary.v0.json`,
`tests/test_loop38_research_boundary.py`, roadmap row 38, research commit
`c82c3fa`, push CI run `29228686142`, and draft PR #17 CI run `29228698759`.

## 0066 - Separate Replay, Compatibility, Reproduction, And Replication

Decision: close Loop 39 planning research while leaving the cross-machine
reproducibility experiment `Not Started`, all 36 `authorized_now` fields false,
and no fixture, environment manifest, matrix job, dependency lock, package
build, protected payload, model, training run, independent reproducer, edge
runtime, device, or hardware operation opened. Freeze seven qualification
levels, 18 environment identity fields, eight output classes, six comparison
classes, six future matrix cells, 20 fixture families, four independently
authorized stages, 28 gates, and 38 refusal IDs.

Claim boundary: deterministic replay on one machine is not bitwise identity;
bitwise identity is not exact semantic identity; numerical compatibility is
not cross-machine reproduction; same-team reproduction is not independent
reproduction; and independent reproduction is not scientific replication.
Each claim requires its own named evidence and failures remain visible.

Environment boundary: every future cell binds OS name/version/architecture,
Python implementation/version, NeuroDecodeKit revision, dependency manifest,
optional profile, thread variables, `PYTHONHASHSEED`, locale, time zone,
filesystem, machine/runner identity, processor, BLAS/backend information, and
hardware accelerator state. Human-readable diagnostics are evidence, not a
portable lock or proof of compatibility.

Comparison boundary: compare schemas, metadata, identities, arrays, floating
values, reports, and package artifacts by their declared class. Require exact
hashes for canonical bytes and exact semantic fields; allow only
preregistered absolute/relative tolerance for floating arrays, with NaN,
infinity, dtype, shape, and mask handling explicit. A wheel or source archive
hash mismatch does not by itself imply behavioral incompatibility, and a
passing numerical tolerance does not imply package reproducibility.

Support result: the current repository declares Python 3.10-3.12 and OS
independence but runs two `ubuntu-latest` Python 3.12 CI profiles, zero explicit
cross-OS cells, no tracked lockfile, and no reproducible package-build job. Two
tests directly import `tomllib`, so the complete Python 3.10 test surface is
currently unqualified. The local diagnostics-only host is Darwin 25.6.0 arm64,
CPython 3.13.5 with NeuroDecodeKit 0.1.0, NumPy 2.5.0, SciPy 1.18.0, MNE 1.12.1,
and Torch 2.13.0; this is not a completed matrix cell.

Future resource boundary: at most two parallel jobs, one thread per worker, 20
minutes and 1 GiB peak RSS per cell, 4 MiB generated artifacts per cell, and 24
MiB total generated artifacts. Protected reads, model runs, training runs,
downloads, package releases, streams, devices, and hardware operations remain
zero until separately authorized.

Claim boundary: no cross-machine reproduction, independent reproduction,
scientific replication, neural advantage, decoding accuracy, unseen-person
generalization, real-time behavior, edge-runtime qualification, or portable-
hardware result exists.

Evidence: `docs/LOOP_39_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop39_research_boundary.v0.json`,
`tests/test_loop39_research_boundary.py`, roadmap row 39, research commit
`efbf764`, push CI run `29230660807`, and draft PR #18 CI run `29230681661`.
Local verification passes 256 focused planning tests, 25 strict Loop
39/roadmap tests, 574 optional unittests, 571 pytest tests plus 261 subtests,
and 542 dependency-light tests.

## 0067 - Require A Named Target And Complete Package Boundary Before Edge Export

Decision: close Loop 40 planning research while leaving its experiment `Not
Started`, all 40 `authorized_now` fields false, and no target/backend selection,
fixture, install, export, conversion, package, inference, profiler, memory
planner, delegate, simulator, app, device, or hardware operation open. Freeze
seven qualification levels, six package layers, four backend profiles, 20
identity fields, eight output classes, six comparison classes, 24 fixture
families, four stages, 30 gates, and 40 refusal IDs.

Reference boundary: the only plausible future reference is the retained
1,130-parameter, 5,210-byte float32 Loop 22/24 producer and diagnostic probe.
Its torch graph excludes normalization, causal stream state, timestamps, frame
scheduling, decoder behavior, and app integration. Loop 24 seed 2401 remains
consumed, seed 2402 remains unopened, and neither may be reused to choose an
edge path.

Backend decision: keep ExecuTorch/XNNPACK as a research lead only because the
source is PyTorch and the official stack exposes CPU delegation, memory
planning, profiling, and mobile integration. Preserve ONNX Runtime Mobile,
LiteRT, and Core ML as alternatives. Select none until a target OS/version,
architecture, ABI, minimum deployment target, and application envelope are
frozen and the relevant Loop 39 matrix cells pass.

Measurement boundary: compare exact discrete/state/timestamp/provenance
behavior, field-specific floating rules, delegated/undelegated/fallback/
unsupported operators, complete model/runtime/kernel/app bytes, startup/load/
warmup/steady/teardown latency, RSS, and planned memory. Model bytes alone are
not deployment size; desktop or simulator execution is not physical-device
qualification; package latency is not capture-to-text latency.

Future authorization boundary: Stage A static eligibility, Stage B local
target-free export/parity, Stage C cross-machine package parity, and Stage D
simulator/app integration require separate decisions. Loop 42 is required for
physical-device evidence and Loop 44 for release. One backend, one thread, one
worker, 60 seconds per measurement worker, 1 GiB RSS, and 32 MiB generated
package/report bytes are the future ceilings; any install needs its own byte
cap.

Claim boundary: no edge package, runtime benefit, neural advantage, decoding
accuracy, unseen-person generalization, end-to-end latency, or portable-
hardware result exists.

Evidence: `docs/LOOP_40_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop40_research_boundary.v0.json`,
`tests/test_loop40_research_boundary.py`, and roadmap row 40.

## 0068 - Preserve Every Clock And Anomaly Across The Stream-To-Token Join

Decision: close Loop 41 planning research while leaving its integration
experiment `Not Started`, all 42 `authorized_now` fields false, and no fixture,
source chunk, correction, preprocessing, adapter, state, token runtime, stream,
device, latency measurement, or generated experiment payload open. Freeze six
integration layers, seven clock views, eight anomaly classes, five inherited
schedules, five resume cuts, 18 identity/hash bindings, 28 future fixture
families, four separately authorized stages, 32 gates, and 42 refusals.

Clock decision: source timestamps are immutable evidence. Corrected timestamps
are derived, segmented, reversible, and hash-bound. Arrival, preprocessing-
ready, token-available, decoder-emission, and render-presented times remain
separate. Subtract only clocks in one named monotonic domain. Replay has no
physical capture event; decoder and render operations do not exist, so capture-
to-arrival and end-to-end latency remain unavailable.

Anomaly and state decision: never silently interpolate gaps, deduplicate
samples, sort reordered samples, or carry state across a reset without a new
segment. The complete future state is capped at 64 KiB, may not contain payload
history, and must reproduce uninterrupted outputs, state, provenance, and
semantic hashes across five resume cuts.

Dependency decision: Loop 20/21 component evidence is not the missing join.
Compatible Loop 25, Loop 37, Loop 39, and RW3 Stage A execution closeouts are
all required and currently unsatisfied. A future Loop 41 preregistration and
authorization remain separate after those close.

Claim boundary: no stream-to-NeuroToken integration, live capture, neural
advantage, decoding accuracy, unseen-person generalization, end-to-end real-
time latency, device qualification, or portable-hardware result exists.

Evidence: `docs/LOOP_41_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop41_research_boundary.v0.json`,
`tests/test_loop41_research_boundary.py`, and roadmap row 41.

## 0069 - Select One Inspectable Local Device Path Without Promoting It

Decision: close Loop 42 planning research while leaving its device experiment
`Not Started`, all 45 `authorized_now` fields false, and no purchase, fixture,
install, SDK import, playback, serial read, discovery, firmware operation,
connection, hardware, participant, electrode, recording, network, signal,
model, decoding, latency, or release operation open.

Candidate decision: select OpenBCI Cyton base 8-channel over USB radio as the
one future mechanics candidate at Q0 official-specification level. Exclude
Daisy, Wi-Fi Shield, GUI network streaming, cloud, targets, and models. The
candidate has an official 33-byte packet, 8-bit counter, eight ExG channels at
250 Hz, firmware/radio commands, ADS1299/SRB2/BIAS identity, battery-only
power, local-file support, and a direct BrainFlow descriptor. This makes it
inspectable, not scientifically superior and not recommended for purchase.

Identity and timing decision: freeze 28 device/configuration fields, 16 packet
fields, seven timing observables, and ten anomalies. Generic ExG becomes EEG
only after exact scalp/reference/BIAS/gain/geometry verification. Sample
counter, adapter timestamp, local arrival, local retrieval, marker, physical
capture, and render/text clocks may not be collapsed. Host-generated adapter
timestamps cannot establish capture latency; an instrumented common-clock
event is required.

Stage decision: A static adapter eligibility, B target-free playback, C
battery-powered no-contact board bench, and D separately consented battery-only
scalp mechanics each require their own hash-bound preregistration,
authorization-only commit, and green CI. Loop 38, Loop 41, and RW3 execution
dependencies remain unsatisfied. A failed stage parks the exact configuration
without device, firmware, transport, adapter, host, or gate substitution.

Privacy and safety decision: freeze ten lifecycle/network surfaces and ten
safety/consent rules. Local recording support is not locality or privacy proof;
future work must run network-off and inventory raw, derived, settings, logs,
support, screenshot, temp, backup, sync, identity, and socket surfaces. Any
body-connected stage is battery only, with charging and mains absent.

Claim boundary: current evidence establishes only that one officially
documented device configuration is eligible for a future staged mechanics
packet. No EEG quality, neural advantage, task information, decoding,
reliability, real-time text, portability, at-home usability, safety, clinical,
or population result exists.

Evidence: `docs/LOOP_42_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop42_research_boundary.v0.json`,
`tests/test_loop42_research_boundary.py`, roadmap row 42, and the unchanged
13-record device registry.

## 0070 - Separate Independent Artifact Reproduction From Scientific Replication

Decision: close Loop 43 planning research while leaving its challenge `Not
Started`, all 48 `authorized_now` fields false, and every packet, oracle,
fixture, workflow, outreach, contributor, submission, adjudication, archive,
release, model, stream, device, and experiment runtime operation at zero.

Terminology decision: a maintainer clean-root rerun is repeatability. A
different eligible team reproducing an author-supplied software artifact is
independent artifact reproduction. Scientific replication requires an
independently developed implementation and a separately frozen protocol. One
external environment never establishes person, platform, device, or population
generalization.

Protocol decision: select one future target-free NeuroToken causal-replay
artifact lane with commit-reveal ordering, public communication, record-dont-
fix checking, retained negative outcomes, unprivileged fork execution, and no
contributor-owned EEG upload. Freeze seven qualification levels, 16
independence fields, 28 packet fields, 34 submission fields, eight comparison
classes, 12 discrepancy classes, four separately authorized stages, 32 fixture
families, 36 gates, and 48 refusals.

Dependency decision: the artifact is not currently eligible. Compatible Loop
37 release-envelope execution, Loop 38 public-artifact lifecycle execution, and
the Loop 39 required matrix plus independent handoff must close before a public
challenge. Loop 44 claim review remains separate.

Verification-incident decision: a local acceptance command validated every
local `*.json` path instead of only Git-tracked source JSON. It read 603 paths,
parsed 602, touched 136 cache JSON files, and included 11 known consumed S21
session-2 report/metadata files. No raw arrays, FIF/MAT payloads, model
operation, inference, scoring, tuning, training, or claim selection occurred.
The zero-consumed-read claim is withdrawn; the incident is retained and future
validation is Git-tracked-only.

Claim boundary: planning research adds no independent result, scientific
replication, neural advantage, decoding accuracy, unseen-person
generalization, real-time latency, device qualification, home-use, or clinical
evidence.

Evidence: `docs/LOOP_43_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop43_research_boundary.v0.json`,
`tests/test_loop43_research_boundary.py`, and roadmap row 43.

## 0071 - Hold Engineering Release And Park Scientific Performance

Decision: close Loop 44's artifact-only claim review with no new experiment,
release mutation, or scientific claim upgrade. Freeze 16 claim cards, seven
evidence levels, five model cards, four dataset cards, 14 release gates, and
eight risks in `registries/loop44_claim_release_matrix.v0.json`.

Promotion decision: retain bounded access, NeuroToken interface, and validated
trial-identity claims as engineering capability. Preserve the S21 session-1
near-null, S21 session-2 harmful cross-session, and S7 EEG harmful results as
real scientific evidence. Keep synthetic mechanisms explicitly synthetic.

Release decision: hold the engineering source release until the current stack
is reviewed onto `main`, exact-candidate privacy/security checks pass, and
Loops 38, 39, and 43 execute. Park scientific performance until a frozen real
neural model beats no-signal and neural-derangement controls. Prohibit clinical
and arbitrary-thought wording.

Claim boundary: no tag, GitHub release, archive, DOI, participant payload,
protected read, model operation, training, unseen-person result, real-time
result, portable/home hardware result, independent reproduction, scientific
replication, or clinical evidence exists.

Evidence: `docs/LOOP_44_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_44_CLAIM_PROMOTION_AND_RELEASE_DECISION.md`,
`registries/loop44_claim_release_matrix.v0.json`, and
`tests/test_loop44_claim_release_matrix.py`.

## 0072 - Target Real Signal Truth Before Model Scale

Decision: freeze Loops 45-64 as five four-loop phases with every experiment and
global authorization field false. The first scientific gate is not a larger
model: it is a 2,908-parameter S21 source-validation candidate that must beat a
matched no-signal prior and every registered corrupted-signal control.

Transfer decision: qualify one non-S25 development person, freeze the complete
model and statistical packet, and only then open S25 once for a strict zero-fit,
zero-calibration unseen-person verdict. A failed S25 gate is retained as the
negative result and S25 becomes consumed.

Accessibility decision: fresh S20 EEG, local device mechanics, end-to-end
clocks, and at-home acquisition feasibility are separate downstream claims.
None may borrow a MEG result or be called home text decoding by default.

Evidence: `docs/LOOPS_45_64_SCIENTIFIC_ROADMAP.md`,
`registries/next_scientific_loops.v0.json`,
`tests/test_next_scientific_loops.py`, and the `Loops 45-64` tracker sheet.

## 0073 - Accept Loop 25 Causal Mechanics And Keep Science Closed

Decision: close Loop 25 and scientific-roadmap Loop 45 after one registered,
target-free execution. Preserve the immutable v0 history, green v1 amendment
`b6b92d8`, separate green authorization commit `1e7296a`, and green
implementation commit `439f151` as the required execution chain. No rerun or
post-result tuning is authorized.

Mechanics decision: accept the exact stateful 1000-to-100 Hz implementation.
Its 65,537-point static response and 23-probe alias gate passed before either
partition opened. Development seed 2501 passed and froze before qualification
seed 2502 opened once and passed unchanged. All 24 items, 168 schedule checks,
240 resume checks, and 72 future-mutation controls passed with zero right
context and exact timestamp, padding, resume-state, and output identity.

Resource and access decision: accept the run under its frozen caps. Static plus
complete-gate internal runtime was 5.542175 seconds, maximum peak RSS was
136,806,400 bytes, mutable state was 720 bytes, and all generated artifacts
totaled 788,967 bytes. Every real-data, real-cache, consumed-evidence, target,
checkpoint, model, training, parameter-update, network, RW3, stream, device,
and hardware counter was zero.

Claim decision: this result establishes target-free synthetic causal-
preprocessing mechanics only. It does not establish official MNE equivalence,
retained neural information, neural advantage, decoding accuracy, unseen-
person generalization, end-to-end latency, real-time operation, portable/home
hardware, or clinical utility. Loop 26 and roadmap Loop 46 require a new hash-
bound preregistration and separate authorization.

Evidence: `docs/LOOP_25_CAUSAL_PREPROCESSING_RESULT.md`,
`registries/loop25_causal_preprocessing_result.v1.json`,
`registries/loop25_authorization_decision.v1.json`, and
`tests/test_loop25_causal_preprocessing_result.py`.

## 0074 - Share The Six S21 Validation Targets Across Loops 26, 31, And 33

Decision: preregister one prospective Loop 26/31/33 and scientific-Loop-46
event instead of scoring the scarce six-row S21 validation slice separately.
Freeze the primary causal model, all encoder-attribution controls, all bounded
data-scaling predictions, and 31 prediction sets before one target delivery.

Model and compute decision: retain one 2,908-parameter left-padded causal
candidate and one 2,884-parameter linear comparator. Permit only a future exact
inventory of 21 parameter-update runs, 24 target-blind model inferences, six
train-only prior fits, 5,040 optimizer steps, three fixed seeds, one CPU thread,
1 GiB peak RSS, and 32 MiB generated artifacts. No restart, favorable-seed
selection, or post-target rerun is available.

Access decision: withdraw the old phrase that validation targets were
physically unopened. The legacy deflated NPZ loader materialized complete
target arrays in at least two historical commands, although the six validation
rows were not used for fitting, hyperparameter/restart/threshold selection, or
predictive scoring. Future execution must use bounded row streaming, isolate a
55-row train derivative and six-row target-free validation-input derivative,
and deliver validation targets only after a hash-only prediction-freeze commit
is pushed and remotely green. Five source-test rows and session 2 stay closed.

Statistical decision: require at least 0.05 macro sentence-CER improvement over
the train-only prior, six strict sentence wins, one-sided exact `p <= 0.05`
from all 64 sign assignments, the complete registered control intersection,
and a strict win over the linear comparator. The bounded scaling result must
also satisfy the frozen small-to-upper and size-55-over-prior margins plus
negative slopes for every seed.

Authorization decision: green preregistration commit `881145d` and CI run
`29282661766` establish design only. The separate request remains unauthorized
with every `authorized_now` field false. General continuation, co-researcher
autonomy, roadmap approval, and Loop 25/RW3 decisions are not the exact one-time
protected execution sentence.

Claim boundary: even a complete pass can establish at most a bounded same-
person, same-session predictive advantage and sensor-signal dependence for the
exact slice, task, preprocessing, and model. It cannot establish brain-specific
origin, source-test/cross-session behavior, unseen-person generalization,
end-to-end causality or real-time decoding, Brain2Qwerty v2 equivalence, EEG or
portable/home performance, arbitrary-thought decoding, or clinical utility.

Evidence: `docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md`,
`docs/LOOP_26_AUTHORIZATION_PACKET.md`,
`registries/loop26_shared_validation_contract.v0.json`,
`registries/loop26_authorization_request.v0.json`, and their dependency-light
invariant suites.

## 0075 - Implement The Shared Validation Gate Before Protected Access

Decision: accept a staged implementation of the frozen Loop 26/31/33 contract
only after synthetic isolation and malformed-input tests pass. Keep real S21
cache values closed until this exact implementation commit is pushed and both
remote CI jobs are green.

Access decision: require bounded forward NPZ member traversal, one later cache
hash pass, isolated 55-row train and six-row target-free validation derivatives,
and a separate scorer that refuses to open targets until the hash-only freeze
record exists in the remotely green `HEAD`. Create the consumed marker before
the first validation-target read so interruption cannot create an accidental
rerun path.

Execution decision: enforce the exact inventory of 21 fits, 5,040 optimizer
steps, 24 target-blind model inferences, six train-only priors, 21 checkpoints,
and 31 prediction sets. Bind each private prediction to its file, item order,
lengths, configuration, checkpoint identity, transform, and prediction hashes.

Resource decision: preserve one thread, one worker, 2,908/2,884 parameters,
128 MiB working arrays, 4 MiB checkpoints, 2 MiB private predictions, 32 MiB
all generated artifacts, 1,200 seconds parameter runtime, 1,500 seconds total
runtime, 1 GiB RSS, and zero downloads.

Claim boundary: this implementation milestone uses synthetic fixtures only. It
creates no real neural result and establishes no neural advantage, signal
dependence, decoding accuracy, cross-session or unseen-person generalization,
real-time behavior, EEG or hardware performance, or clinical utility.

Evidence: `docs/LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md`, the bounded
reader, causal model, shared evaluator, staged experiment gate, five CLI
commands, and their focused synthetic and dependency-light invariant tests.

## 0076 - Park The Shared S21 Gate After Its Registered Negative Result

Decision: accept the one-shot result exactly as observed and park Loops 26,
31, and 33. Do not tune around the failed gate, increase model size, reopen the
six validation targets, or substitute source test, session 2, S7, S20, or S25.

Scientific decision: the fixed candidate's macro sentence CER of `0.938177`
is worse than the train-only prior's `0.751235`; its registered margin is
`-0.186942`, with zero wins, one tie, five losses, and one-sided exact
`p = 1.0`. The primary neural-effect gate failed. Although exact-zero and
timing-only controls passed individually, the complete attribution conjunction
failed. Although all three scaling slopes were negative, the 55-row model
failed its matched-prior rule. These components are diagnostics, not claims.

Engineering decision: retain the implementation and access-ledger machinery.
It preserved the one-cache-hash, 55/6 train/validation split, remote-green
prediction freeze before one six-target delivery, zero source-test/session-2
access, zero post-target changes, one-thread execution, 1 GiB RSS cap, and
32 MiB artifact cap.

Next-step decision: Loop 48 artifact-first failure localization is the next
research work order. Planning may use committed aggregate artifacts; any
train-array diagnostic, protected cache read, target read, model operation, or
implementation requires a separate exact authorization.

Claim boundary: no neural advantage, sensor-signal dependence, brain-specific
origin, decoding utility, unseen-person generalization, real-time result,
portable/home hardware result, assistive result, diagnostic result, or clinical
claim is available.

Evidence: `docs/LOOP_26_SHARED_VALIDATION_RESULT.md`,
`registries/loop26_shared_validation_result.v0.json`, prediction-freeze commit
`54bdca9`, and the consumed private scoring marker outside Git.

## 0077 - Preregister Artifact-Only Failure Localization Before New Experiments

Decision: classify the consumed Loop 26/31/33 discrepancy first from four exact
committed aggregate artifacts. Freeze an ordered eight-class tree and treat
`F5` model-fit/output-distribution instability as the leading observed
phenotype because the primary checkpoint is blank-dominant and every fixed
prefix has substantial three-seed blank-fraction dispersion.

Interpretation decision: do not promote `F5` into a causal explanation. The
public artifacts lack loss and gradient trajectories, train-only decoding,
input-to-target length ratios, signal-quality summaries, timing residuals, and
paired causal/offline representations. CTC behavior, weak signal, preprocessing,
temporal alignment, and their interactions remain unresolved.

Execution decision: prepare only a post-outcome artifact-only contract. A
future Stage A may verify four committed JSON hashes, reproduce aggregate
arithmetic, apply the frozen tree, and emit one target-free JSON report under
one thread, 30 seconds, 256 MiB RSS, and 1 MiB output. Implementation and
execution remain unauthorized until a separate request binds a remotely green
contract commit.

Access decision: this planning pass read no source cache, ignored derivative,
checkpoint, private prediction, target bundle, source-test row, session 2, S7,
S20, S25, raw FIF/MAT, stream, device, or hardware payload. It ran no model,
training, scoring, download, or network operation.

Claim boundary: the leading evidence is an unstable output phenotype, not a
proven failure mechanism. It establishes no neural advantage, sensor-signal
dependence, brain-specific origin, decoding utility, transfer, real-time
behavior, EEG result, portable/home hardware result, or clinical result.

Evidence: `docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop48_failure_localization_contract.v0.json`, and
`tests/test_loop48_failure_localization_contract.py`.

## 0078 - Request One Artifact-Only Stage A Without Opening Train Diagnostics

Decision: after green contract commit `83309bf`, push CI `29431318268`, and PR
CI `29431347801`, prepare one immutable authorization request for a
dependency-light analyzer and one artifact-only Stage A execution.

Scope decision: permit a future authorized run to read only four exact
committed JSON files totaling 155,545 bytes, verify their hashes, reproduce
frozen aggregate arithmetic, apply the ordered eight-class tree, and write one
target-free aggregate report. Cap it at one thread, one worker, 30 seconds,
256 MiB RSS, and 1 MiB output.

Firewall decision: keep every authorization false until the exact sentence is
captured in a separate green decision record. This request excludes ignored
outputs, caches, arrays, targets, checkpoints, private predictions, model
inference, training, parameter updates, seed/threshold/architecture selection,
source test, session 2, S7, S20, S25, raw FIF/MAT, downloads, language models,
RW3, streams, devices, hardware, scientific claim upgrades, and reruns.

Claim boundary: even a clean Stage A can establish only that the exact public
aggregate artifacts satisfy `F5` under the frozen post-outcome tree. It cannot
establish a root cause or any positive neural, decoding, transfer, real-time,
EEG, device, assistive, diagnostic, or clinical result.

Evidence: `docs/LOOP_48_AUTHORIZATION_PACKET.md`,
`registries/loop48_authorization_request.v0.json`, and
`tests/test_loop48_authorization_request.py`.

## 0079 - Evaluate Multiple Failure Hypotheses From One Shared Train-Only Bundle

Decision: do not treat the artifact-level `F5` phenotype as the only hypothesis
or force one root-cause winner. Design future Stage B around five hypotheses
that may coexist: CTC feasibility/optimization, sensor/trial quality,
timing/preprocessing mismatch, representation separability, and prior
dominance.

Efficiency decision: collect static feasibility, quality, timing, fit telemetry,
simple-probe, transform, and corruption-control measurements once, then reuse
them across the five hypothesis rows. “Parallel” means parallel scientific
comparison; physical numerical execution remains sequential, one-threaded, and
single-worker.

Leakage decision: any future diagnostic fit/check partition must live entirely
inside the 55 source-train rows and be grouped by sentence identity. Validation,
source test, session 2, S7, S20, and S25 remain excluded. Exact split counts,
seeds, thresholds, model inventory, runtime, RSS, and output caps remain
unfrozen pending Stage A and a separately authorized static prototype.

Authorization decision: the portfolio is design research only. It does not
inherit a future Stage A authorization and currently permits no fixture,
prototype, train/cache/signal/target read, model, training, prediction,
checkpoint, scoring, download, stream, device, or hardware operation.

Evidence: `docs/LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md`,
`registries/loop48_hypothesis_portfolio.v0.json`, and
`tests/test_loop48_hypothesis_portfolio.py`. Request/portfolio commit
`0ffdf47` passed push CI `29433294092` and PR CI `29433297546`; this qualifies
the decision surface without changing any false authorization field.

## 0080 - Separate Data-Regime Failure From The Fixed CTC Recipe

Decision: preserve the green five-hypothesis portfolio byte-for-byte and add an
independent six-hypothesis discrimination map. Narrow `H1` from a general CTC
question to the exact 2,908-parameter, 240-step recipe, and add `H6` for data
quantity and unique-sentence diversity. Brain2Qwerty v2 makes scale and
diversity plausible mechanisms, but its much larger noncausal GPU setting does
not transfer a threshold, exponent, architecture, or expected score to S21.

Evidence decision: compare the six mechanisms through one shared train-only
bundle and return a support vector, including conflicts and unresolved fields.
Descriptive evidence is `E1`; a frozen pipeline intervention can reach `E2`;
bounded sensor dependence requires intact signal to clear every registered
prior/corruption by both a preregistered practical margin and paired uncertainty
gate. A lucky aggregate win is not sufficient.

Claim-firewall decision: track peripheral or task-locked shortcut dependence as
orthogonal threat `T1`, not as a seventh explanation for model failure. Even a
future Stage B pass stops at `E3` and routes to the separately authorized Loop
35 firewall; it cannot establish brain-specific origin during overt typing.

Resource and authorization decision: “parallel” means parallel scientific
comparison over shared evidence. Numerical execution remains sequential with
one thread, one worker, and one job. Exact splits, seeds, inventory, thresholds,
fits, predictions, checkpoints, resource caps, and stopping rules remain
unfrozen. No protected payload, model, training, prediction, scoring, download,
stream, device, or hardware operation occurred or is authorized.

Evidence: `docs/LOOP_48_HYPOTHESIS_DISCRIMINATION_RESEARCH.md`,
`registries/loop48_hypothesis_discrimination.v0.json`, and
`tests/test_loop48_hypothesis_discrimination.py`.

## 0081 - Consume One Artifact-Only Failure-Localization Pass

Authorization decision: bind the user's exact Stage A sentence to the frozen
Loop 48 contract in a separate decision record. Authorization commit `5bae880`
passed push CI `29442914090` and PR CI `29442916230` before implementation.
Implementation commit `ca21539` then passed push CI `29444008688` and PR CI
`29444012075` before any registered input opened.

Execution decision: run the dependency-light analyzer exactly once over the
four named committed aggregate JSON artifacts. Verify all four SHA-256
identities, reproduce the frozen blank/CER summaries and six seed-dispersion
checks, apply the ordered eight-class tree, and emit one aggregate report. The
run used one thread and one worker, took `0.016568875` seconds internally,
peaked at 23,429,120 bytes RSS, and wrote 10,643 bytes. Every resource gate
passed.

Scientific decision: retain `F5` as a descriptive output-distribution
instability phenotype because the primary condition was `0.993477` blank, all
six prefix groups crossed the frozen `0.25` dispersion threshold, and all three
size-55 seeds were worse than the train-only prior. Do not call `F5` a root
cause. Temporal feasibility, signal quality, preprocessing, representation,
prior dominance, and interactions remain unresolved.

Firewall decision: the pass read no ignored output, cache member, array,
target, checkpoint, private prediction, source-test or session-2 payload, S7,
S20, S25, raw FIF/MAT, stream, device, or hardware source. It ran no model,
training, parameter update, selection, download, language model, or RW3
operation. The result is consumed; no rerun, tuning, architecture escalation,
or scientific claim upgrade is authorized.

Evidence: `docs/LOOP_48_AUTHORIZATION_DECISION.md`,
`registries/loop48_authorization_decision.v0.json`,
`docs/LOOP_48_FAILURE_LOCALIZATION_RESULT.md`,
`registries/loop48_failure_localization_result.v0.json`, and
`tests/test_loop48_failure_localization_result.py`.

## 0082 - Draft Standing Autonomy Around Reversible Work

Decision: replace repeated permission requests for routine work with a proposed
three-tier charter. Tier A covers research, documentation, code, tests,
synthetic fixtures, target-free aggregate analysis, preregistration, commits,
pushes, and CI. Tier B covers bounded development experiments only when the
development partition, hypotheses, metrics, thresholds, seeds, stop rules,
resource caps, and claim ceiling are frozen before execution.

Irreversibility decision: retain exact one-time permission for Tier C events:
new real participant payloads, sealed targets, final or unseen-person scoring,
consumed-evaluation reuse, post-outcome protocol changes, real downloads,
hardware or participant recording, destructive operations, releases, and claim
promotion. These stops protect evidence validity and the user's machine; they
are not a judgment about the co-researcher's competence.

Resource decision: propose a standing default of one thread, one worker, one
numerical job, 1 GiB RSS, 32 MiB generated artifacts per loop, no new real-data
download, no persistent process, and no deletion outside the repository. A
loop-specific contract may tighten but cannot silently loosen these limits.

Activation decision: the charter is a draft and grants no authorization. It
becomes active only after the exact sentence in
`docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md` is supplied and captured in a separate
committed decision. Approval is prospective and cannot reopen Loop 48, S25,
RW3, or another consumed or independently gated experiment.

Evidence: `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md` and
`tests/test_research_autonomy_charter.py`.

## 0083 - Preregister Train-Only Failure Discrimination Before New Acquisition

Sequence decision: run one bounded Loop 48 Stage B diagnostic design before a
new Loop 49 participant acquisition. The existing 10,632,576-byte sentence
cache can distinguish optimization collapse, gross transformed-cache defects,
timing sensitivity, registered-probe nonseparability, prior dominance, and
bounded data-regime effects with materially less storage and compute than a
new download. Loop 49 remains required and is not replaced.

Historical-use decision: all 55 source-train rows contributed to earlier Loop
26 fits. A new target-independent 44-fit/11-check split therefore creates an
internal prediction firewall but not historically fresh or independently
confirmatory evidence. Correct the exact claim ceiling from the design-level
E3 concept to E2 pipeline-discriminative evidence.

Protocol decision: freeze five nested prefixes, three seeds, 20 parameter-
update runs, 35 target-blind model inferences, five train-only priors, 41
prediction sets, and exact 2,048-assignment paired inference. Freeze one
candidate corruption conjunction and a separate six-set candidate/linear
prior rule; do not imply that uncomputed linear corruption controls or a
task-locked character probe exist.

Resource and access decision: retain one thread, one worker, one numerical job,
1 GiB peak RSS, 32 MiB total output, a 20 GiB free-disk floor, and zero new
downloads. Keep validation, source test, session 2, S7, S20, S25, raw FIF/MAT,
private Loop 26 outputs, training, inference, and check scoring closed. The
preregistration grants no authorization and requires a separate exact decision
before implementation or protected access.

Evidence: `docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md`,
`registries/loop48_train_only_discrimination_contract.v0.json`, and
`tests/test_loop48_train_only_discrimination_contract.py`.

## 0084 - Prepare A Green-Bound Stage B Decision Surface

Decision: prepare one human-readable packet and one machine request only after
the exact Stage B preregistration was committed, pushed, and independently
green on push and pull-request workflows. Bind commit
`0ee0ab7cd3abae4ce654af9954854a6e236c8a0e`, push CI `29452286159`, PR CI
`29452288520`, and the immutable document, contract, and invariant-test hashes.

Scope decision: request exactly one cache hash pass, 44 fit signal/target rows,
11 pre-freeze target-free check inputs, 20 parameter-update runs, 35 target-
blind inferences, five priors, 41 prediction sets, and one post-green-freeze
11-target scoring delivery. Preserve the E2 ceiling, zero downloads, one-thread
resource envelope, and every excluded partition and operation.

Authorization decision: preparing or remotely qualifying the request grants no
permission. Every `authorized_now` field remains false. A future decision must
reproduce the exact sentence, bind the green request commit, and itself become
green before implementation. General continuation, co-researcher status, the
draft autonomy charter, Stage A, and Loop 26 are not transitive authorization.

Evidence: `docs/LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md`,
`registries/loop48_stage_b_authorization_request.v0.json`, and
`tests/test_loop48_stage_b_authorization_request.py`.

## 0085 - Preserve Separate Development And Final People

Decision: select SpanishBCBL MEG S24 session 2 block 2 as the preferred future
Loop 49 development-only person from pinned public metadata. Preserve S25 as
the final-only person selected by Loop 27. S24 is one exact FIF/log pair totaling
1,048,579,727 bytes, which is 293,597,553 bytes below the 1.25 GiB future cap.

Identity decision: prefer S24 over the 29,701,559-byte-smaller S18 pair because
S18 belongs to the published S1/S18 alias group. The small storage premium buys
a cleaner canonical-person ledger. S23 remains ineligible under the official
metallic-implant exclusion; S21 is the observed source; S7 is consumed EEG;
S20 remains a separate accessible-EEG lane. No backup may open automatically.

Split decision: recommend a deterministic canonical-sentence-group split only
after a separately authorized redacted audit proves at least 48 usable unique
rows. Reserve the first 16 salt-hash-ordered groups for development selection
and assign the remainder to development fit, producing a minimum 16/32 split.
Keep identical text in one partition across people and exclude every matching
S21 source-train selection text from future fit. Persist no plaintext or raw
sentence hashes. S24 is permanently development-only after first protected
access and can never become final evidence.

Evidence decision: the current pass establishes only metadata selection. It
does not establish the trial floor, channels, geometry, duration, signal or
target quality, sentence overlap, model performance, neural advantage, person
generalization, real-time behavior, or portable/home-device behavior. The
48-row floor is pragmatic, not a prospective power calculation.

Sequence and authorization decision: retain Decision 0083, which places the
separately gated Loop 48 Stage B before new Loop 49 acquisition. No S24 local
path was inspected and no payload, header, signal, MAT content, target, source
hash set, derivative, model, training, prediction, or score was opened. Loop 49
remains `Not Started`, unpreregistered, unqualified, and unauthorized; all 25
authorization fields are false.

Evidence: `docs/LOOP_49_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop49_research_boundary.v0.json`, and
`tests/test_loop49_research_boundary.py`.

## 0086 - Freeze A Two-Person Development Design Before S24 Access

Decision: complete Loop 50 primary-source planning while keeping the experiment
`Not Started`. Freeze a global canonical-sentence firewall, five-fold
historical S21 out-of-fold diagnostic, one 16-group S24 development
qualification, equal `0.5/0.5` participant loss, one shared causal candidate
family, ten fixed candidate/prior/control conditions, primary seed 5001, two
nonselectable stability seeds, an exact 20-parameter-update inventory, and
separate per-person plus worst-person gates. The four-run margin below the
absolute cap is not rerun permission.

Leakage decision: identical text may never cross a fit/evaluation boundary
through another participant. Any S21 row matching S24 selection text is removed
from all fits, normalizers, priors, and diagnostics. For each S21 out-of-fold
fold, matching S24 fit text is also excluded. Participant ID may index only the
sampler, metric, and access ledgers; it may not enter a model, scaler, affine,
adapter, checkpoint, or decoder. S21 out-of-fold results remain historically
used development evidence and may never be relabeled fresh validation.

Model and gate decision: choose no exact model before Loop 48 Stage B closes or
parks. A later preregistration may choose one <=10,000-parameter, zero-right-
context shared model with no language model or participant-conditioned path.
Primary seed 5001 must beat the strongest no-signal prior by at least 0.05 macro
CER and strictly beat registered corruptions separately on both people. S24
must improve over the S21-only neural comparator while S21 degrades by no more
than 0.02. Pooled gain and stability seeds cannot rescue a failed primary or
person.

Sequence decision: retain Decision 0083. A future Stage B result must first
apply the six-route repair/proceed/park table. S24 then needs separate
acquisition, header, redacted audit, split, channel, geometry, and >=48-group
qualification. All predictions must be committed, pushed, and remotely green
before the same 16 S24 selection targets open once. Failure parks Loop 50 and
blocks Loop 51 without rerun. S25 remains final-only and receives zero Loop 50
fit, normalization, selection, or scoring rows.

Evidence and authorization decision: all 31 authorization fields are false and
every protected/model/training/inference/scoring counter is zero. This planning
boundary establishes no neural advantage, decoding accuracy, unseen-person
generalization, brain-specific origin, real-time behavior, EEG or home-device
performance, assistive value, or clinical result.

Evidence: `docs/LOOP_50_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop50_research_boundary.v0.json`, and
`tests/test_loop50_research_boundary.py`.
