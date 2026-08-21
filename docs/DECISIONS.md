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
`tests/test_loop50_research_boundary.py`. Planning commit `085f341` passed push
CI `29458102674` and PR #28 CI `29458116994`, with both required jobs green in
both workflows.

## 0087 - Activate Tier A And Tier B Research Autonomy

Decision: accept the exact standing sentence in the 2026-07-15 Research
Autonomy Charter. Preserve `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md` byte-for-
byte at SHA-256
`c9381bfc729dfca4aaab03929a6623f23c3cf06eb33fbae5379b0517981dcb64`;
use the separate activation document and registry as the prospective decision
record.

Standing scope decision: after this decision is tested, committed, pushed, and
remotely green, Tier A routine research engineering and Tier B fully frozen,
bounded development experiments may proceed without repeated permission,
including coherent commits, pushes, and CI inspection. Retain the default one-
thread, one-worker, one-job, 1 GiB RSS, 32 MiB output, zero-real-download, and
20 GiB free-disk envelope unless a narrower registered contract applies.

Irreversibility decision: Tier C remains separately gated. The charter does not
reopen consumed evidence; authorize a new real participant payload, sealed or
final target, consumed-evaluation reuse, post-outcome change, download, cap
increase, hardware, destructive action, release, or scientific claim only by a
separate exact decision. It does not itself authorize Loop 48 Stage B, RW3, or
S25. The separately supplied Loop 48 Stage B sentence must receive its own
authorization-only record and remote-green gate.

Evidence: `docs/RESEARCH_AUTONOMY_CHARTER_DRAFT.md`,
`docs/RESEARCH_AUTONOMY_CHARTER_DECISION.md`,
`registries/research_autonomy_charter_decision.v0.json`, and
`tests/test_research_autonomy_charter_decision.py`.

## 0088 - Authorize One Registered Loop 48 Stage B Execution

Decision: record the maintainer's exact Loop 48 Stage B sentence in a separate
authorization-only document and registry. Bind it to preregistration commit
`0ee0ab7`, request commit `1de3fa3`, contract SHA-256
`009e320ea4df17e9f6fa58f74053b2ab70cce73eb0a9eea3cefc5b7b14112a9a`,
and request SHA-256
`c23030f655fd662128dbc70f879a7a7a7d062f861ec279779b53852521d08c38`.

Authorized scope: after this decision commit is remotely green, implement the
synthetic-qualified bounded path and execute once over exactly 44 source-train
fit rows plus 11 target-withheld source-train check inputs. Allow one cache
hash pass, 20 parameter-update runs, 4,800 optimizer steps, 35 target-blind
inferences, five train-only priors, 41 prediction sets, and one later delivery
and scoring of the same 11 check targets only after a plaintext-free prediction
freeze is committed, pushed, and remotely green.

Refusal decision: keep validation, source test, session 2, S7/S20/S25, raw
FIF/MAT, downloads, larger or additional models, restarts, language models,
NeuroTokens, RW3, streams, devices, hardware, post-check tuning, claim promotion
beyond E2, and reruns closed. All 55 rows were used historically, so the result
cannot become independent validation or neural advantage.

Evidence: `docs/LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md`,
`registries/loop48_stage_b_authorization_decision.v0.json`, and
`tests/test_loop48_stage_b_authorization_decision.py`.

## 0089 - Close Loop 48 At Stable Nonseparability And Park Same-Family S24

Decision: accept the one-shot Loop 48 Stage B result at its registered E2
post-outcome train-only ceiling. The primary size-44 causal candidate reached
macro sentence CER `0.953566` versus `0.822045` for the train-only no-signal
prior, a `-0.131522` margin. All three size-44 causal fits and all three
size-44 linear fits had finite, stable telemetry, but none cleared the frozen
prior margin and exact-p rule.

Hypothesis decision: support `H4`, stable but nonseparable representation, for
this transformed S21 source-train slice and fixed tiny model family. Record
evidence against `H3` because none of the `-50`, `-25`, `+25`, or `+50`
sample offsets improved all three seeds under the corrected rule. Keep `H1`,
`H2`, `H5`, and `H6` unresolved. The transformed-cache quality audit found no
gross defect, but raw sensor quality and peripheral physiology remain
unavailable. The nested size curve was nonmonotonic and does not support a
data-scaling extrapolation.

Control decision: preserve the exact-zero, timing-only, and severe-displacement
component wins as diagnostic facts only. The candidate failed the prior and
complete corruption conjunction, so those isolated wins do not establish
sensor-signal dependence, neural advantage, brain-specific origin, or useful
decoding.

Access decision: implementation commit `1d840e3` passed push CI `29461579009`
and PR CI `29461580293` before one source-cache hash pass or protected row
delivery. Hash-only freeze commit `00215b1` passed push CI `29461934145` and PR
CI `29461935560` before the same 11 check targets opened once. The run used
exactly 44 fit rows, 11 target-withheld check signals, 20 fits, 4,800 optimizer
steps, 35 target-blind inferences, five priors, 41 prediction sets, and one
check score. Validation, source test, session 2, S7/S20/S24/S25, raw FIF/MAT,
downloads, post-check changes, and reruns remained zero.

Resource decision: accept `190.140486` cumulative execution seconds through
freeze, `483,540,992`-byte maximum peak RSS, and `9,623,773` generated bytes as
passing the one-thread, 900-second, 1 GiB, and 32 MiB caps. The producer has two
frames of left context and zero right context, but the upstream cache is
offline/noncausal and end-to-end latency is unmeasured.

Routing decision: apply frozen Loop 50 route `L50-R05`. Stable
nonseparability, no prior-clearing probe family, and no registered `H6`
nonsaturation mean S24 acquisition is parked for this model family. S24 remains
metadata-only and unopened; S25 remains physically unopened and final-only.
This does not claim that S24 lacks information or that another representation
must fail. A future representation-repair experiment requires a new prospective
contract, and any Tier C post-outcome or protected-data operation still needs a
separate exact decision.

Disposition: Loop 48 Stage B is complete and consumed. No fit, inference,
prediction, target delivery, score, tuning, or rerun is open. Maximum wording
remains E2 pipeline-discriminative failure localization, not independent
validation or scientific claim promotion.

Evidence: `docs/LOOP_48_STAGE_B_RESULT.md`,
`registries/loop48_stage_b_prediction_freeze.v0.json`,
`registries/loop48_train_only_discrimination_result.v0.json`, and
`tests/test_loop48_stage_b_result.py`.

## 0090 - Test Temporal Context Before Reopening Protected Evidence

Decision: select `R1`, temporal-context starvation, as the next falsifiable
representation-repair hypothesis after Loop 48 Stage B. The failed
`TinyCausalSentenceCTC-v0` mixed sensors pointwise and exposed only 20 ms of
learned left context. Compare one 7,692-parameter causal temporal candidate
with 470 ms left context against one 7,568-parameter zero-context ablation on
the same 25 Hz output grid. The 124-parameter gap is 1.612070% of the candidate,
so a future difference can test registered temporal context more cleanly than
an unmatched capacity increase.

Mechanics decision: implement and calibrate on a synthetic ordered-motif
fixture before preparing any protected contract. Freeze seed 4850, 40 rows, a
24/8/8 train/selection/final split, three candidate optimizer recipes, one
ablation fit, one final opening, at most four training runs, 1,800 optimizer
steps, 600 seconds, 1 GiB peak RSS, 16 MiB generated output, one thread, one
worker, and zero real-data downloads. Require deterministic checkpoint replay,
zero right context, exact length/timestamp/padding behavior, resume equivalence,
and a candidate-versus-ablation final CER margin.

Scientific boundary: synthetic success can establish only that the registered
causal interface can learn ordered temporal motifs under its exact mechanics.
It cannot establish that S21 contains usable neural information, that longer
context improves real decoding, or that S24/S25 should open. Primary-source
architecture and physiology findings provide rationale, not transferred
accuracy.

Authorization decision: the Research Autonomy Charter allows implementation
after this research milestone is pushed and remotely green, and one synthetic
calibration after the implementation milestone is pushed and remotely green.
No S21 cache stat, hash, member, target, 44-row reuse, 11-row reopen,
validation, source test, session 2, S24, S25, real model operation, download,
device, hardware, or claim upgrade is authorized. Any protected Stage C
diagnostic remains Tier C and needs its own exact preregistration and decision.

Evidence: `docs/LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md`,
`registries/loop48_stage_c_representation_repair_research.v0.json`, and
`tests/test_loop48_stage_c_representation_repair_research.py`.

## 0091 - Implement Stage C Without Spending The Synthetic Gate

Decision: implement the exact Stage C candidate, ablation, deterministic
fixture, bounded gate, safe numeric checkpoints, and inspect CLI after research
commit `9579be9` passed push CI `29466218879` and PR CI `29466225955`. Keep
NumPy and Torch optional and imported only inside the functions that need them.

Mechanics decision: preserve all frozen architecture and fixture identity. The
candidate has 7,692 parameters, 470 ms left context, zero right context, and a
25 Hz output grid. The ablation has 7,568 parameters, no learned temporal
history, zero right context, and the same grid. The seed-4850 fixture has 40
unique rows, 102 channels, 1,699,920 array bytes, strict 24/8/8 identities,
zero signal/target padding, and a stable SHA-256. Every source frame visible to
the ablation is zero; motif identity lives in the ordered past.

Qualification decision: test shape, parameter, causality, padding, split,
hash, checkpoint, cap, CLI, and forbidden-import behavior without a parameter
update. Accept 13 focused tests, 910 dependency-light tests with 156 expected
skips, and 957 optional-neuro tests with 3 expected skips. No persistent
generated artifact, real read, download, or model training occurred.

Execution decision: this implementation does not spend the registered four-fit
synthetic gate. The one calibration may run only after the implementation
commit passes both push and PR CI. It must use one thread, one worker, at most
1,800 optimizer steps, 600 seconds, 1 GiB RSS, 16 MiB generated output, at
least 20 GiB free disk, one final opening, and no restart.

Scientific boundary: an eventual synthetic pass can establish only mechanics.
No protected Stage C contract, S21 cache operation, S24/S25 operation, real
model run, or scientific claim is opened by implementation.

Evidence: `docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md`,
`registries/loop48_stage_c_synthetic_implementation.v0.json`,
`src/neurodecodekit/models/tiny_causal_temporal_ctc.py`,
`src/neurodecodekit/training/temporal_motif_sentences.py`,
`src/neurodecodekit/experiments/temporal_representation_gate.py`, and
`tests/test_loop48_stage_c_synthetic_implementation.py`.

## 0092 - Fail Closed Before Spending The Stage C Calibration

Decision: classify the first post-green Stage C command refusal as a static
implementation preflight failure, not a calibration execution or scientific
outcome. The validator looked for `seed`; the frozen registry names the field
`fixture_seed`. The command stopped in 0.12 seconds at 21,954,560-byte peak RSS
before output-directory creation, fixture generation, model construction,
inference, training, checkpoint writing, or result writing.

Counter decision: record zero fixture rows, model runs, optimizer steps,
checkpoints, results, protected reads, cache reads, target reads, and download
bytes. The calibration did not start and remains unspent. Do not retry from the
already green implementation commit.

Correction decision: change only the validator field name, add a regression
test that validates the exact committed research registry, recompute source
hashes, and require a new commit plus fresh push and PR CI before execution.
The corrected baseline is 14 focused tests, 911 dependency-light tests with 156
expected skips, and 958 optional-neuro tests with 3 expected skips.

Evidence: `docs/LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md`,
`registries/loop48_stage_c_synthetic_implementation.v0.json`, and
`tests/test_loop48_stage_c_synthetic_implementation.py`.

## 0093 - Consume And Park The Stage C Synthetic Gate

Decision: accept the one Stage C synthetic execution only after correction
commit `2836ecc` passed push CI `29467415680` and PR CI `29467416894`. Record
the run as consumed and prohibit rerun, final-outcome tuning, threshold changes,
recipe substitution, added steps, fixture changes, or protected escalation from
this result.

Outcome decision: select `L48C-SYN-OPT0` by the frozen selection rule. The
7,692-parameter temporal candidate reached final macro CER `0.433333` and
`1/8` exact sequences; the 7,568-parameter zero-context ablation reached CER
`1.000000` and `0/8` exact. The `0.566667` candidate-ablation CER improvement
passed, as did deterministic checkpoint replay, future-mutation,
prefix-resume, causality, padding, and every resource check. The candidate
failed the absolute CER `<=0.10` and exact-sequence `>=7/8` gates, so the
aggregate gate failed.

Resource decision: accept four training runs, 1,680 optimizer steps, eight
model-inference runs, 7.829308 seconds internal runtime, 310,509,568-byte
internal peak RSS, and 83,132 generated bytes as within the frozen caps. Raw-
data, real-cache, real-signal, real-target, download, S24/S25, stream, device,
hardware, and RW3 counters remained zero. The producer was causal with zero
right context; end-to-end latency was not measured.

Scientific boundary: the candidate-ablation difference establishes only that
the registered temporal model used ordered history on this purpose-built
synthetic fixture. It does not establish usable neural information, neural
advantage, sensor-signal dependence, brain-specific origin, real decoding
improvement, generalization, real-time performance, or portable/home EEG
performance. It does not justify opening S21, acquiring S24, or opening S25.

Evidence: `docs/LOOP_48_STAGE_C_SYNTHETIC_RESULT.md`,
`registries/loop48_stage_c_synthetic_result.v0.json`, and
`tests/test_loop48_stage_c_synthetic_result.py`.

## 0094 - Separate Fresh EEG Acquisition From Interpretation

Decision: advance the independent accessible-EEG lane through Loop 53 while
keeping the failed MEG model-family branch parked. Select the previously
identified S20 session 2 block 2 bundle at pinned SpanishBCBL revision
`88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`: one BrainVision triplet plus one
companion MAT log, four exact files, and 96,090,264 bytes.

Staging decision: replace the historical broad S20 packet for future work with
an acquisition-only gate. A future authorized Loop 53 execution may reverify
public metadata, transfer the four files once into a new isolated destination,
perform opaque size/integrity hashes, emit a receipt, and clean up only its own
temporary files. It may not parse a header, marker, EEG sample, or MAT field;
read targets or events; create a cache/split; or access a model.

Resource decision: freeze one CPU thread, one worker, 600 seconds, 512 MiB peak
RSS, 128 MiB network payload, 256 MiB incremental disk, 1 MiB receipt output,
and a 2 GiB free-disk floor. Any identity/license mismatch, destination
collision, partial transfer, cap breach, forbidden read, substitution, or hash
failure parks without rerun.

Registration decision: commit `bccd367` passed push CI `29469813041` and PR
CI `29469829357`, with 929 dependency-light tests/156 expected skips and 961
optional-neuro tests/29 expected skips remotely green. Prepare a separate
hash-bound request, but leave every execution authorization false until the
user supplies its exact Tier C sentence and the decision is separately
committed, pushed, and green. General autonomy and the 5-10 GB storage allowance
are not transitive acquisition permission.

Scientific boundary: acquisition mechanics cannot establish BrainVision
readability, EEG quality, target validity, neural advantage, decoding accuracy,
generalization, real-time behavior, portable/home hardware, or clinical utility.

Evidence: `docs/LOOP_53_PRIMARY_SOURCE_RESEARCH.md`,
`docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md`,
`registries/loop53_fresh_eeg_acquisition_contract.v0.json`,
`docs/LOOP_53_AUTHORIZATION_PACKET.md`, and
`registries/loop53_authorization_request.v0.json`.

## 0095 - Separate EEG Header, Signal, And Target-Bearing Event Access

Decision: complete Loop 54 planning research without implementing or executing
an S20 reader. Replace the coarse header-then-signal idea with four ordered
future stages: strict VHDR-only identity metadata, target-blind VHDR+EEG signal
quality, isolated VMRK+MAT trial reconciliation, and aggregate closeout.

Reader decision: prohibit MNE in the VHDR-only stage because the standard
BrainVision reader attaches marker-derived annotations. Preserve the current
Loop 19 extractor as valid historical engineering evidence, but make it
ineligible for the future Loop 54/55 claim path because it co-loads annotations,
MAT labels, and signal, excludes EOG-named channels, and writes plaintext
labels. A future path must use a dependency-light one-file VHDR parser, a direct
bounded EEG reader, all-channel preservation, and an isolated protected
reconciler.

Inference-unit decision: require at least 48 unique performed trials and treat
the trial, not each keypress window, as the future unit of partitioning and
paired uncertainty. Loop 54 creates no train, validation, or final split. Exact
Loop 55 counts remain unavailable until the target-blind usable-trial count is
known, then must freeze prospectively before target values or model operations.

Resource and authorization decision: freeze 22 gates, 30 refusals, one thread
and worker, at most 1 GiB peak RSS per future stage, and at most 32 MiB combined
public generated output. Loop 53 must complete first. L54-A, L54-B, and L54-C
each require a separate exact Tier C decision after a hash-bound implementation
is pushed and remotely green. No current real-stage permission is granted.

Scientific boundary: a future clean Loop 54 closeout may establish only the
identity, quality, event reconciliation, geometry, reference, and recorded-
confound ceiling of one S20 block. It cannot establish neural advantage,
brain-specific origin, decoding accuracy, real-time behavior, portable or home
hardware, or clinical utility.

Evidence: `docs/LOOP_54_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop54_eeg_trial_geometry_research.v0.json`, and
`tests/test_loop54_eeg_trial_geometry_research.py`.

## 0096 - Separate Causal Hand Evidence From Key-Level EEG Decoding

Decision: complete Loop 55 planning research without preregistering,
implementing, or executing an S20 model. Replace one ambiguous EEG-decoding
endpoint with two prospectively ordered endpoints from the same future final
trials: causal pre-keypress performed-hand prediction and causal pre-keypress
29-class performed-key prediction.

Target decision: make the performed key and its deterministic hand mapping the
primary targets because the overt physical action generates the keypress-
aligned motor and peripheral signal. Keep corrected intended sentence text as
a protected secondary target that cannot create features, choose a model or
checkpoint, or upgrade a hand effect into a key-decoding claim.

Causality decision: require EEG samples strictly before each known keypress,
zero right context, causal anti-aliasing, train-only normalization, and no
future-touching baseline or zero-phase transform. Retain the published
`[-200,+300] ms` keypress-centered window only as a noncausal post-keypress and
task-aligned diagnostic. It cannot rescue a causal failure.

Inference decision: treat the performed trial as the split and paired-
inference unit. Require a future grouped `44/10/10` split only if the currently
unverified usable count is 64, with deterministic alternatives for 48-59 and
60-plus trials. Every causal endpoint must clear its practical margin over the
strongest train-only no-signal prior and strictly beat every applicable
zero-signal, whole-trial, channel, timing, train-pairing, timing-only, and
peripheral control under exact one-sided paired sign-flip tests. A hand pass
without a key pass remains a hand effect only.

Model and resource decision: recommend one shared compact causal EEG encoder
with key and hand heads, one fixed linear comparator, at most 10,000 trainable
parameters per model, at most 12 parameter-update runs, one thread and worker,
45 CPU minutes, 1 GiB peak RSS, 64 MiB total generated output, zero downloads,
and no language model, pretrained weight, larger model, stream, device, or
hardware operation. The exact run inventory remains a future preregistration.

Authorization decision: Loop 53 and all required Loop 54 stages must close
cleanly first. A future Loop 55 run needs its own exact preregistration,
separate exact Tier C decision, green implementation, isolated grouped split,
selection-prediction freeze before selection targets, and committed, pushed,
remotely green final-prediction freeze before the same final targets open once.
No current execution permission is granted.

Scientific boundary: the strongest future clean result can establish only a
bounded within-person pre-keypress EEG sensor-signal effect for performed hand
or key prediction on one overt-typing block with known event onsets. It cannot
establish brain-specific origin, intended-thought decoding, continuous event
detection, unseen-person/session/device generalization, real-time operation,
portable hardware, home use, or clinical utility.

Evidence: `docs/LOOP_55_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop55_eeg_neural_effect_research.v0.json`, and
`tests/test_loop55_eeg_neural_effect_research.py`.

## 0097 - Shared Interfaces Are Not Shared EEG/MEG Evidence

Decision: complete Loop 56 planning research with a five-class verdict instead
of one cross-modality score. The classes are shared proven artifact, shared
interface only, modality-specific requalification, unavailable, and prohibited
inference. A dependency-free metric implementation may be shared; a signal,
score, threshold, channel ontology, preprocessing transform, representation,
weight set, causal behavior, latency, or device capability may not transfer
without an independent experiment.

Capability decision: freeze 12 non-skippable levels from source identity and
bounded reading through signal quality, trial integrity, sensor-signal effect,
prediction, continuous input, causal incremental output, measured end-to-end
latency, local device mechanics, repeated at-home feasibility, and assistive or
clinical utility. Passing a later software level cannot fill an earlier
physical or scientific level. In particular, continuous whole-sentence input
is not causal incremental output or measured real-time latency.

Evidence decision: retain the registered local S21 MEG and historical S7 EEG
negative results with their exact cohorts, models, and metrics. They are not a
matched modality comparison. Keep published Brain2Qwerty v1/v2 results external
and prevent them from setting local thresholds or reversing local negatives.
Fresh S20 qualification and neural-effect evidence remains unavailable.

Accessibility decision: require a 12-part conjunction for any future at-home
claim, including named device mechanics, EEG reference and channel roles,
locality, clock and packet behavior, target-blind quality, repeated setup,
task integrity, sensor-signal effect, causal parity, measured latency, privacy,
and safety/usability. An OpenBCI packet specification satisfies none of that
conjunction as a complete result.

Authorization decision: the final Loop 56 verdict remains `Not Started` and
waits for Loop 55 to close. It requires an exact hash-bound aggregate-only
preregistration and a separate exact Tier C scientific-claim decision. No raw,
ignored, protected, cache, target, prediction, checkpoint, model, score
recomputation, download, network, stream, device, participant, home, release,
or claim operation is authorized by this planning boundary.

Evidence: `docs/LOOP_56_PRIMARY_SOURCE_RESEARCH.md`,
`registries/loop56_cross_modality_accessibility_research.v0.json`, and
`tests/test_loop56_cross_modality_accessibility_research.py`.

## 0098 - Consume Loop 53 At Acquisition Mechanics Only

Decision: accept the one registered Loop 53 invocation as a clean acquisition-
mechanics pass and consume the gate with no rerun. Authorization commit
`2a47bbc` passed push CI `29589212626` and PR CI `29589225113`;
implementation commit `8ec5b1b` passed push CI `29591387642` and PR CI
`29591391286` before the registered paths or metadata network were opened.

Identity decision: retain exactly the four S20 session-2 block-2 files at
revision `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`, CC BY-NC 4.0 metadata,
and 96,090,264 total bytes. The pinned revision remained public, ungated, and
enabled; every path, size, Git object, LFS SHA-256, and Xet identity matched.
No substitute file, participant, session, block, or retry was used.

Resource decision: record 3.629499 seconds runtime, 63,225,856-byte peak RSS,
96,090,264 network bytes, 102,035,529-byte peak incremental disk,
44,104,826,880 free bytes before execution, and 8,265 private receipt bytes.
All frozen thread, worker, time, memory, network, disk, free-space, and output
caps passed.

Access decision: preserve zero header, marker, signal, MAT, target, cache,
split, checkpoint, model, inference, training, scoring, language-model, RW3,
stream, device, hardware, additional-file, additional-participant, and rerun
counters. The four local reads were opaque integrity hashes only. Keep the
payload and both receipts ignored and outside Git; publish only aggregate
mechanics and the two receipt hashes.

Next-gate decision: Loop 53 creates no permission for Loop 54. Do not reopen,
parse, interpret, split, model, or score S20 from this result. Each applicable
L54-A/B/C content stage still requires its own exact Tier C decision after a
hash-bound implementation is committed, pushed, and remotely green.

Scientific boundary: this pass proves only that one exact public S20 bundle was
acquired and opaque-verified within the registered controls. It does not prove
BrainVision readability, channel or geometry facts, signal quality, event or
trial validity, target correctness, neural advantage, decoding accuracy,
generalization, end-to-end latency, portable hardware, at-home use, or clinical
utility. It does not upgrade the Loop 56 cross-modality evidence class.

Evidence: `docs/LOOP_53_ACQUISITION_RESULT.md`,
`registries/loop53_acquisition_result.v0.json`, and
`tests/test_loop53_acquisition_result.py`.

## 0099 - Use AI As A Bounded Research Proposer, Not An Outcome Optimizer

Decision: introduce AI into the Loop 55 research process through a strict
proposal interface and adversarial protocol review. Keep the causal performed-
hand endpoint first and the harder performed-key endpoint second. An agent may
not choose the question after seeing outcomes or receive an instruction to
obtain a positive result.

Representation decision: retain one compact causal spatiotemporal family under
10,000 trainable parameters. Permit future target-free warm-up choices of none,
masked reconstruction, or contrastive next-window prediction without external
weights, text, performed labels, or future samples. Keep LLMs ineligible because
fluent correction can hide a weak neural encoder.

Search decision: reserve at most four future AI-guided train-inner proposal
rounds inside the existing 12-run total. Freeze the menu, aggregate summaries,
winner rule, transcript, and stop rule prospectively after Loop 54. A new
trained control reduces proposal capacity; it cannot expand the total. The
agent never sees raw EEG, individual labels/predictions/errors, intended text,
selection/final outcomes, private paths, or reversible protected hashes.

Implementation decision: add a dependency-free versioned policy, deterministic
canonical hashes, strict unknown-field rejection, a tiny synthetic fixture,
bounded report I/O, and inspect/make/validate CLI commands. Treat every proposal
as untrusted data and never execute code from it. Current eligibility stops at
synthetic policy rehearsal with every real/protected/model counter at zero.

Authorization decision: this additive engineering policy does not preregister
or authorize Loop 55. Loop 54 must close with at least 48 qualified trials, then
an exact Loop 55 contract, separate Tier C decision, green implementation,
protected split order, prediction freeze, and one-shot scoring remain required.

Scientific boundary: passing the synthetic guard establishes AI proposal
governance mechanics only. It does not establish representation improvement,
self-supervised transfer, EEG hand/key information, brain-specific origin,
generalization, continuous or real-time decoding, portable/home use, or
clinical utility.

Evidence: `docs/LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md`,
`registries/loop55_ai_research_policy.v0.json`,
`src/neurodecodekit/evaluation/ai_research_policy.py`,
`fixtures/loop55_ai_synthetic_proposal.v0.json`, and
`tests/test_ai_research_policy.py`.

## 0100 - Advance The Fresh EEG Lane Through One Strict Header Stage

Decision: preregister L54-A as the smallest real-content step after the
consumed Loop 53 acquisition. Bind exactly one 11,705-byte S20 VHDR and do not
combine it with signal quality, marker interpretation, target reconciliation,
or model work.

Parser decision: require a standard-library implementation with no-follow path
validation, one content open, exact size and Git-blob verification, strict
codepage decoding, duplicate rejection, complete ordered channel declarations,
and deterministic sampling-rate derivation. Record DataFile and MarkerFile only
as exact inert basenames; never resolve, stat, hash, or open either sibling.

Evidence-order decision: freeze 18 gates, 22 refusals, one real execution, one
thread/worker, 30 seconds, 256 MiB RSS, 1 MiB output, and no network or new
payload. First green the contract, then record an exact Tier C decision, then
green a synthetic-fixture-only implementation, and only then open the VHDR
once. Any failed real gate parks the stage without rerun.

Ordering clarification: for L54-A this decision supersedes only the ambiguous
older phrase that placed the exact decision after implementation. It does not
loosen any access rule. The exact decision authorizes bounded implementation
and one execution, while the implementation must still be committed, pushed,
and remotely green before the registered VHDR can open.

Authorization decision: registration commit `c114623` alone grants no local
path stat or content access. CI run `31127199848` was retried at that exact
commit on 2026-08-08. Optional Neuro Readers passed, while Base Python installed
Ruff `0.16.2` from the historical floating declaration and stopped on 400
later repository-wide findings. The frozen preregistration, contract, and
invariant test are byte-identical at pinned-toolchain commit `2232993`, whose
CI `31132586790` passed both jobs; exact-tree Ruff `0.15.20` replay passed 1,095
tests with three skips. The additive recovery record retires repeated
unbounded-toolchain reruns without calling the failed exact run green. A new
recovery-bound request and exact Tier C decision remain required. Earlier
acquisition permission, Tier A/B autonomy, storage allowance, and competitive
urgency are not transitive Tier C decisions.

Scientific boundary: a future clean L54-A pass can establish only strict
readability and internal consistency of allowlisted declared header fields
under L54-Q2. It cannot establish signal quality, event/trial/target validity,
sensor-signal or brain-specific information, decoding accuracy, generalization,
real-time latency, portable or at-home operation, or clinical utility.

Evidence: `docs/LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md`,
`registries/loop54_stage_a_vhdr_contract.v0.json`, and
`tests/test_loop54_stage_a_vhdr_contract.py`.

## 0101 - Keep The Specialist EEG Path And Add A Known-Effect Ladder

Decision: retain the staged Loop 54 qualification and compact Loop 55 model
path. Current 2026 EEG foundation-model benchmarks do not support replacing a
small controlled experiment with a larger model by default: specialist models
remain competitive, linear probes are often insufficient, and parameter scale
does not consistently improve generalization.

Positive-control decision: prepare a separate future contract for the public
PhysioNet EEG Motor Movement/Imagery dataset before protected S20 model work.
The prospective slice is S001-S003, motor-execution runs 3/7/11, exactly nine
EDF files totaling 23,248,224 bytes by public HTTP metadata. Runs 3 and 7 are
prospective fit data and run 11 is the prospective frozen check. No download or
payload access is authorized by this decision.

Model decision: use the public positive control to choose at most one classical
spatial/covariance family between fixed CSP-LDA and a Riemannian alternative.
Carry that family, fixed low-frequency shrinkage LDA, one compact causal
EEGNet-style family, and an interpretable pre-keypress motor-physiology assay
into the future Loop 55 design refresh without changing the existing
10,000-parameter and 12-fit ceilings. S20 selection or final targets may not
choose the family.

Validity decision: preserve all channels until qualification, freeze causal
preprocessing before protected scoring, and compare minimal causal processing
with at most one nonselectable artifact-attenuated diagnostic. Higher accuracy
from EOG, EMG, timing, or structured noise narrows or invalidates the claim; it
does not become neural evidence.

Foundation-model decision: keep pretrained EEG models in a separate later
public-data benchmark lane. OpenEEGBench is a useful adapter target, but its
multi-dataset downloads must be explicitly capped. ZUNA or another generative
imputer may never create primary input samples that are then called measured
evidence.

Community decision: pursue local-first cohort receipts rather than centralized
raw-data collection. Contributors keep raw EEG and plaintext targets locally
and may eventually share only redacted, hash-bound aggregate compatibility and
benchmark evidence. Consent, license, raw release, and matched scientific
aggregation remain separate decisions.

Authorization decision: this is additive Tier A/B research and documentation.
It does not amend frozen Loop 54/55 artifacts or authorize S20 access,
PhysioNet acquisition, another real-data read, model/checkpoint access,
training, inference, scoring, pretrained weights, raw upload, hardware, or a
scientific claim.

Evidence: `docs/OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md`,
`registries/open_eeg_rd_strategy.v0.json`, and
`tests/test_open_eeg_rd_strategy.py`.

## 0102 - Select A Failure-Addressable Causal Motor Lattice Before More Scale

Decision: select `CML-v0` as the next source-independent Loop 55 architecture
hypothesis. Use three explicit pre-keypress views for potential shape, causal
mu energy, and causal beta energy; one rank-8 spatial mixer and three temporal
cells per view; and one 24-dimensional shared bottleneck. Do not answer current
negative evidence with a larger transformer, foundation model, or language
model.

Spatial decision: transform each learned spatial row to zero sum and unit L2
norm before use. This adds no trainable parameter, reduces common-reference and
scale ambiguity, and does not claim universal reference or artifact invariance.

Output decision: map the shared bottleneck through at most 18 fixed physical
keyboard primitives plus a 29-key residual. Derive hand probability exactly by
marginalizing the final key distribution under a frozen hand-eligibility map.
Do not train an independent hand head that can contradict the key prediction.
Intended text, sentence context, and target frequency may not construct the
lattice. Bound the residual as `rho * tanh(z_residual)` with fixed
`0 <= rho <= 1`; choose and freeze `rho` only under a future synthetic contract
before public or protected payload access.

Complexity decision: use the exact formula `24C + 2,549 + 25P`, where `C` is
the qualified EEG channel count and `P <= 18` is the frozen primitive count.
The 64-channel/18-primitive reference is 4,535 parameters. A future mismatch or
cap breach parks the design instead of expanding the existing 10,000-parameter
ceiling.

Causality decision: publish exact one-sided filter coefficients, response,
group delay, left context, valid sample count, and anti-alias behavior before
any real execution. A 500 ms potential view may describe slow shape but may not
claim narrow `0.1-1 Hz` resolution. Centered filters, zero-phase processing,
future padding, and filter-reset artifacts remain forbidden.

Qualification decision: split the public positive control into two axes.
Retain the undownloaded 23,248,224-byte PhysioNet prospect for left/right
execution mechanics. Prepare a separate future bounded EEG+EMG MRCP prospect
for pre-movement timing against measured EMG onset. They are
noninterchangeable, off-task controls and each needs a separate exact Tier C
contract. Either failed axis parks the protected architecture path.

Diagnostic decision: freeze full, potential-muted, mu-muted, beta-muted,
all-muted, channel-deranged, time-displaced, and conditionally hemisphere-
mirrored predictions from the same checkpoint. These add no training run and
localize failure, but they do not replace matched scientific controls or prove
cortical physiology.

Authorization decision: architecture research, documentation, tests, commit,
push, and CI inspection are authorized under Tier A/B. No synthetic model was
implemented or run. No public or S20 payload, target, split, checkpoint, model,
training, inference, scoring, hardware, release, or claim action is authorized.
Frozen Loop 54/55 artifacts remain unchanged, and exact L54-A commit `c114623`
still needs replacement remote-green evidence before its Tier C packet can
freeze.

Scientific boundary: this decision proposes a falsifiable and resource-bounded
research architecture. It establishes no EEG effect, neural advantage,
decoding accuracy, generalization, brain-specific origin, causal real-time
output, portable hardware, home use, or clinical utility.

Evidence: `docs/LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md`,
`registries/loop55_causal_motor_lattice_research.v0.json`, and
`tests/test_loop55_causal_motor_lattice_research.py`.

## 0103 - Put A Frozen Foundation Model Downstream Of The Sensor Adapter

Decision: NeuroDecodeKit will not train a GPT-scale language model. Preserve a
small causal trained model only as the sensor-to-evidence adapter, then use a
frozen foundation model for downstream language reasoning. Select
`gpt-5.6-sol` as the first hosted candidate through the Responses API.

Transport decision: hosted Sol receives only bounded CTC n-best text, causal
top-key probabilities, entropy, relative timestamps, availability timestamps,
missingness, and uncertainty. Do not send raw EEG/MEG, dense NeuroToken
vectors, participant identities, absolute local paths, target/reference text,
intended sentences, performed target labels, or post-outcome corrections. The
hosted API cannot inject arbitrary custom hidden embeddings. A future local
continuous-prefix adapter is a separate architecture and decision.

Control decision: freeze four matched conditions under the same model, prompt,
reasoning effort, output schema, and compute: language-only `FM-A00`, CTC-only
`FM-A01`, matched CTC plus neural evidence `FM-A02`, and fixed cyclically
item-deranged neural evidence `FM-A03`. Incremental neural evidence requires
`FM-A02` to beat both `FM-A01` and `FM-A03` after predictions freeze and before
targets open. Fluency or improvement over language-only is not enough.

Fine-tuning decision: use no LLM fine-tuning for v0. The selected hosted model
does not currently expose fine-tuning, and prompting plus structured evidence
is sufficient for the first falsifiable question. Any later supported model,
local weights, adapter training, or fine-tuning is a separate model, resource,
license, privacy, and evidence decision.

Stage decision: only FM-0 deterministic synthetic no-call bridge work is
eligible now under Tier B. FM-1 needs a separate network, API-credential, and
spend decision; FM-2 needs a public development-data contract; FM-3 needs clean
upstream evidence, a frozen adapter, a remotely green prediction freeze, and a
separate Tier C target and scientific-claim decision.

Scientific boundary: this strategy and FM-0 planning establish no provider
behavior, neural effect, decoding accuracy, generalization, real-time output,
portable hardware, home use, or clinical utility.

Evidence: `docs/FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md`,
`registries/foundation_model_decoder_strategy.v0.json`, and
`tests/test_foundation_model_decoder_strategy.py`.

## 0104 - Implement FM-0 As A No-Call Compiler

Decision: implement only FM-0 from Decision 0103. The dependency-free bridge
creates strict synthetic evidence, compiles `FM-A00` through `FM-A03`, freezes
cyclic item derangement, binds source evidence and every request by SHA-256,
and validates the result without contacting a provider.

Leakage decision: fail closed on target/reference/label/intended fields, raw
sensor samples, dense embeddings, NeuroToken vectors, identities, paths,
noncausal timestamps, malformed probabilities, unknown fields, nonzero access
counters, source substitution, derangement drift, symlinks, cap expansion, and
accidental overwrite.

Measurement: the committed 7,327-byte fixture contains 3 synthetic items, 6
CTC hypotheses, 12 causal frames, and 24 top-key probabilities. It compiled to
12 conditions and 34,349 bytes in 0.002745583 seconds at 21,495,808-byte peak
RSS. Inspection took 0.001411584 seconds at 21,037,056-byte peak RSS. The plan
core SHA-256 is
`355e018f6cd33d7a0d8213fa20eb0798f571c84e4c2e5a2f84dff33ed6c47b5d`.

Authorization decision: code, synthetic fixture, tests, documentation, commit,
push, and CI inspection are authorized under Tier B. External provider calls,
API credentials, spending, model inference, real/protected reads, annotations,
training, scoring, fine-tuning, and claim promotion remain unauthorized.

Scientific boundary: a deterministic provider-free request plan is an
engineering artifact. It is not evidence that GPT-5.6 Sol follows the schema,
that a neural adapter contains useful information, or that any text was
decoded.

Evidence: `docs/FOUNDATION_MODEL_BRIDGE_V0.md`,
`registries/foundation_model_bridge_v0.json`,
`src/neurodecodekit/evaluation/foundation_model_bridge.py`, and
`tests/test_foundation_model_bridge.py`.

## 0105 - Qualify Terra Once On The Frozen Synthetic Matrix

Decision: preserve `gpt-5.6-sol` as the quality-first product candidate while
using lower-cost `gpt-5.6-terra` for one bounded FM-1 provider qualification.
The question is whether the exact FM-0 matrix can traverse the Responses API
and return through a strict schema, not whether any text is correct.

Ordering decision: bind the provider surface and source hashes first, then
record the user's exact execution decision separately, then commit and remotely
qualify the implementation before any credential read or provider call.
Contract commit `7db14d5` passed push CI `31267860543`; authorization commit
`04fc009` passed push CI `31268358553`. The implementation milestone remains
unexecuted until its own exact SHA is remotely green.

Transport decision: issue at most the frozen 12 independent sequential
requests to `https://api.openai.com/v1/responses` with model
`gpt-5.6-terra`, low reasoning, default service, strict JSON Schema, no tools,
`store=false`, `stream=false`, 256 output tokens per request, and zero retries.
Read the existing `OPENAI_API_KEY` once only after every preflight gate passes.
Never serialize, hash, persist, or surface the credential.

Privacy decision: transmit only the committed synthetic task context, CTC
hypotheses, and compact synthetic key evidence. Reject targets, references,
labels, intended text, raw EEG/MEG, dense embeddings, NeuroTokens, identities,
and local paths. Retain parsed structured outputs and bounded hashes, not raw
provider IDs, headers, organization metadata, or error bodies.

Receipt decision: bind every response to its frozen request and recompute all
usage, price, byte, condition-summary, warning, and access-counter aggregates.
A failed or partial invocation parks and consumes FM-1 without retry. Failed
reply bodies survive only as byte count and SHA-256 so accounting remains exact
without retaining provider content.

Local measurement: the zero-network dry run rebuilt 12 requests totaling
18,399 bytes in 0.004586541 seconds at 33,832,960-byte peak RSS. Thirteen
focused implementation tests pass. Credential, network, model, spend,
protected-read, target, training, fine-tuning, and scoring counters remain zero.

Scientific boundary: FM-1 has no target and no real neural evidence. Even a
clean provider run can establish only bounded transport, strict parsing,
measured cost/latency, and descriptive behavior on this exact synthetic
fixture. It cannot establish decoding accuracy, neural advantage,
brain-specific information, generalization, real-time operation, portable
hardware, home use, or clinical utility.

Evidence: `docs/FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md`,
`registries/foundation_model_live_smoke_contract.v0.json`,
`docs/FOUNDATION_MODEL_LIVE_SMOKE_AUTHORIZATION_DECISION.md`,
`registries/foundation_model_live_smoke_authorization_decision.v0.json`,
`docs/FOUNDATION_MODEL_LIVE_SMOKE_IMPLEMENTATION.md`, and
`registries/foundation_model_live_smoke_implementation.v0.json`.

## 0106 - Park FM-1 After The First Non-Completed Matched Response

Decision: classify the one FM-1 invocation as consumed and parked. Exact
implementation commit `a1d7ccc` passed push CI `31269398670` before credential
access. The runner then attempted three sequential Terra calls, accepted two
completed strict responses, and stopped at request index 2 when the provider
status was not completed. Do not rerun, retry only missing rows, increase the
budget, substitute another model, or tune prompts from the observed outputs.

Behavior record: language-only `FM-A00` abstained with empty text and
`evidence_used=none`. CTC-only `FM-A01` returned `HELLO WURLD` with
`evidence_used=ctc`. No matched `FM-A02` response completed and no `FM-A03`
derangement response ran. Matched-versus-deranged behavior is unavailable.

Measurement: three calls and spend events followed one credential read. The
two completed responses reported 339 input, 143 output, and 62 reasoning
tokens. Their local standard-price estimate is $0.002394. Third-attempt usage
and actual total billing are unavailable. Runtime was 8.406004375 seconds,
peak RSS was 39,337,984 bytes, wire request/response totals were 4,179/13,502
bytes, and the sanitized receipt was 5,882 bytes.

Failure boundary: preserve only terminal category
`provider_response_not_completed`, request index, response byte count, and
SHA-256. The receipt cannot distinguish token limit, capacity, policy, or
another provider-side cause, so no root cause is selected.

Scientific boundary: two synthetic strict responses and fail-closed parking
are engineering evidence. The incomplete four-arm matrix, absent target, and
absent real neural evidence support no decoding or neural claim.

Evidence: `docs/FOUNDATION_MODEL_LIVE_SMOKE_RESULT.md` and
`registries/foundation_model_live_smoke_result.v0.json`.

## 0107 - Spend The $50 AI Ceiling Through Local-First Gates

Decision: accept the user's $50 aggregate AI-provider budget as a ceiling, not
a spending target. Reserve the full $0.50 FM-1 contract cap because the third
attempt's provider billing is unavailable. Allocate the conservative $49.50
remainder across independent transport recovery, synthetic Sol/Terra controls,
public target-free integration, later target-bearing and protected evaluation,
and contingency ceilings. Unused budget remains unspent.

Standing scope: synthetic or public non-protected target-free provider calls
may proceed only under a committed machine contract with fixed model, call,
cost, retry, privacy, and receipt rules. This budget does not authorize an FM-1
rerun, protected data, targets, raw EEG/MEG, dense embeddings, scientific
scoring, hardware, purchases, large downloads, releases, or claim promotion.

Local-first decision: reuse MNE for file/QC/preprocessing/decoding, MOABB for
grouped public benchmarks, pyRiemann for serious low-data covariance baselines,
and compact Braindecode architectures before buying more hosted inference.
These remain optional dependencies and one-thread/bounded work where practical.

Ear-worn decision: treat Apple application `US20230225659A1` as evidence that
an earbud-form dynamic electrode-selection interface is technically relevant.
It names EEG and contact-aware active/reference electrode selection, but it is
a pending application, does not mention AirPods, and proves neither a shipping
EEG product nor thought-to-text. Begin only with generic synthetic contact,
noise, missingness, and channel-subset fixtures. Hardware and commercial
freedom-to-operate remain separate.

Scientific boundary: a budget allocation, patent application, toolbox, model
catalog, or hardware prospect establishes no neural advantage or decoding
result.

Evidence: `docs/AI_LOCAL_FIRST_R_AND_D_BUDGET_2026-08-08.md` and
`registries/ai_local_first_rd_budget.v0.json`.

## 0108 - Measure Before Installing The EEG Stack

Decision: inventory the existing local EEG environment through fixed isolated
zero-network imports before adding optional packages. Bind the retained result
to a remotely green implementation and report every missing capability,
warning, resource measurement, temporary write, unavailable field, and access
counter.

Result: implementation commit `e1de855` passed push CI `31277731869` before the
measured run. NumPy 2.5.0 and SciPy 1.18.0 provide the immediate array/signal
core. MNE 1.12.1 provides BrainVision reading and ICA, while its CSP surface is
incomplete in this environment. scikit-learn, pyRiemann, MOABB, and Braindecode
are absent. Runtime was 14.52799025 seconds, maximum child RSS was 173,211,648
bytes, and retained output was 9,416 bytes under 1 MiB.

Route: do not install a broad stack. Build deterministic synthetic motor,
timing, ocular, line-noise, dropout, and channel-corruption fixtures with
NumPy/SciPy first. Add optional adapter contracts before deciding which missing
library earns an install. PhysioNet and S20 remain behind their exact Tier C
boundaries.

Scientific boundary: availability and imports are engineering evidence only.
They establish no dataset quality, neural effect, model accuracy,
generalization, real-time latency, portable hardware, home use, or clinical
utility.

Evidence: `docs/LOCAL_EEG_TOOLING_AUDIT_2026-08-08.md`,
`registries/local_eeg_tooling_audit_result.v0.json`,
`registries/local_eeg_tooling_audit_receipt.v0.json`, and
`docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md`.

## 0109 - Separate Synthetic Factor Fixtures From CML-v0

Decision: freeze a reusable factor-isolation fixture before implementing any
architecture. Use seed 5503 for 96 paired items spanning the eight factors
already selected by the CML research, with strict train/check/final groups and
deterministic shortcut/corruption transforms.

Boundary: this is reversible Tier B infrastructure under the active autonomy
charter and systematic execution request. Synthetic design classes are allowed
only as generator controls. No text target, real identity, protected path,
public payload, architecture, fit, model, inference, score, or claim is in
scope. The frozen CML research artifact remains unchanged.

Route: implement a lazy NumPy/SciPy generator, strict validator, metadata-only
inspector, deterministic mutation surface, and CLI. Retain no generated array
payload in Git. CML-v0 remains work order 13 and every real-data action remains
Tier C.

Evidence: `docs/SYNTHETIC_MOTOR_FIXTURE_PREREGISTRATION.md` and
`registries/synthetic_motor_fixture_contract.v0.json`.

## 0110 - Qualify Fixture Mechanics Before Retaining A Measurement

Decision: implement the frozen work-order-3 fixture as one deterministic NPZ,
one inspectable sidecar, a strict full loader, a metadata-only inspector, eight
fixed mutations, and two CLI commands. Keep NumPy and SciPy optional and lazy.

Reason: the public EEG and protected S20 paths should not pay for basic schema,
timing, pairing, padding, corruption, or leakage mistakes. Exact synthetic
relations let those failures be caught cheaply without fitting a model or
opening evidence.

Gate: local tests may use disposable fixture replays. One retained aggregate
measurement may occur only after the exact implementation commit is pushed and
both remote CI jobs pass. Retain hashes and aggregate metrics, never the NPZ or
sidecar. A failed replay, resource cap, or validator parks the work order rather
than widening it.

Boundary: invented factors can qualify software mechanics only. CML-v0,
PhysioNet, S20, targets, models, training, inference, scoring, hardware, and
scientific claims remain outside this decision.

Evidence: `docs/SYNTHETIC_MOTOR_FIXTURE_IMPLEMENTATION.md` and
`registries/synthetic_motor_fixture_implementation.v0.json`.

## 0111 - Close Work Order 3 And Advance To Adapter Contracts

Decision: accept the one post-green synthetic closeout. All 18 registered gates
passed under the frozen time, memory, output, leakage, causality, and access
limits. Remove the generated NPZ and sidecar after hashing and retain only the
aggregate result and documentation.

Measured basis: implementation `ad361c8` passed CI `31279302969` before one
1.20-second execution at 118,177,792-byte peak RSS. Total output was 584,308
bytes for `[96, 8, 256]`, 20,448 valid samples, and `0.16796875` padding. All
prohibited counters were zero.

Route: mark work order 3 complete and activate work order 4. Freeze interfaces
for optional classical EEG baselines, grouped-fit semantics, and leakage tests
without installing a library, opening real data, fitting a real model, or
scoring a scientific endpoint.

Scientific boundary: successful synthetic mechanics do not establish EEG
physiology, neural origin, decoding, generalization, latency, device behavior,
home use, or clinical utility.

Evidence: `docs/SYNTHETIC_MOTOR_FIXTURE_RESULT.md` and
`registries/synthetic_motor_fixture_result.v0.json`.

## 0112 - Freeze Classical Adapter Interfaces Before Dependencies

Decision: define three optional classical EEG adapter families as symbolic,
strictly validated plans before installing or importing their backends. Keep
low-frequency shrinkage LDA, causal CSP-LDA, and Riemannian MDM all registered
and unselected.

Reason: a public positive control should determine whether CSP or Riemannian
geometry earns the future protected slot. Synthetic behavior and S20 outcomes
must not choose the family. Formal train-group-only fit scopes and explicit
refusals make leakage errors visible before data or compute is spent.

Route: after this contract commit is remotely green, implement a
standard-library plan builder, validator, canonical hash, and synthetic mutation
tests only. Use the prior tooling receipt for availability; do not install,
probe, import, fit, infer, score, or select an optional adapter.

Scientific boundary: a valid adapter plan is engineering evidence only. Public
or protected execution remains Tier C and cannot inherit authorization from
this work order.

Evidence: `docs/CLASSICAL_EEG_ADAPTER_PREREGISTRATION.md` and
`registries/classical_eeg_adapter_contract.v0.json`.

## 0113 - Implement Symbolic Adapter Plans Without Backends

Decision: implement only the standard-library work-order-4 planning layer. A
plan contains all three registered families, exact grouped identities, six fit
scopes, dependency routes, target and causality firewalls, zero-access counters,
warnings, claims, and a canonical hash.

Reason: leakage and dependency-substitution failures can be qualified without
an estimator or neural payload. This keeps the public positive-control choice
unspent and prevents package availability from silently changing the selected
scientific path.

Gate: require exact-commit green CI before one measured symbolic plan creation
and inspection. Retain only hashes and aggregate measurements. Any refusal,
resource, or replay failure parks work order 4 without installing or running a
backend.

Scientific boundary: the plan layer is not a baseline result. Public or
protected feature extraction, fit, inference, selection, and scoring remain
Tier C.

Evidence: `docs/CLASSICAL_EEG_ADAPTER_IMPLEMENTATION.md` and
`registries/classical_eeg_adapter_implementation.v0.json`.

## 0114 - Close Symbolic Adapter Plans And Advance To Contact Semantics

Decision: accept the one post-green symbolic create/inspect roundtrip. All 18
registered gates passed under the frozen time, memory, output, leakage,
dependency, causality, and access limits. Retain only aggregate hashes and
measurements; remove the generated plan.

Measured basis: exact implementation
`eefb7b066810c2a6b87417b105bdb746218e87dc` passed CI `31280581308` before one
0.12-second execution at 22,822,912-byte peak RSS. The 27,335-byte serialized
plan replayed canonical hash
`66800348e76d03b9b994a460b2e78fbe569c450fdb289be5948cecbcea860bf1`.
Creation and inspection agreed; no plan file was retained.

Route: mark work order 4 complete and activate work order 5 only at a
synthetic interface boundary. Freeze exact contact-mask, channel-noise, and
missing-channel semantics for an ear-channel adapter before implementing them.
Do not infer capability from a patent, current earbuds, or invented geometry.

Scientific boundary: no adapter backend was imported, selected, fitted,
inferred, or scored. The result establishes no EEG effect, neural origin,
decoding, generalization, latency, device performance, home use, or clinical
utility.

Evidence: `docs/CLASSICAL_EEG_ADAPTER_RESULT.md` and
`registries/classical_eeg_adapter_result.v0.json`.

## 0115 - Freeze A Generic Contact-Aware Ear-Channel Interface

Decision: define Work Order 5 as a synthetic post-acquisition adapter, not a
device controller. Preserve all 16 generic bilateral source channels and their
reference state while keeping observed, present, contact-valid, eligible,
selected, and adapted-observed masks distinct.

Reason: ear-centered research systems and the cited patent make variable
contact and channel subsets credible engineering concerns, but a patent is not
an implementation license or product result. A fixed quality rule can qualify
missingness and provenance semantics without copying hardware topology,
installing a package, or touching a signal.

Frozen policy: require valid contact score at least `0.6`, noise score at most
`0.4`, and at least `95%` observed pre-event samples. Select at most four and at
least two channels per side with a fixed tie break and equal `0.5/0.5` side
weight. If either side is insufficient, select none. Unknown impedance and
measured geometry remain unavailable.

Gate: commit, push, and obtain remote-green CI for the exact contract before
implementing a lazy-NumPy synthetic fixture. Require a second green
implementation commit before one measured synthetic roundtrip. No real data,
hardware, physical switching, model, fit, inference, score, or claim is
authorized.

Scientific boundary: passing masks and selection mechanics establishes no real
ear-EEG quality, brain-specific source, decoding, portability, home use, or
clinical utility.

Evidence: `docs/CONTACT_AWARE_EAR_CHANNEL_PREREGISTRATION.md` and
`registries/contact_aware_ear_channel_contract.v0.json`.

## 0116 - Implement Contact Semantics Before Any Ear-Hardware Path

Decision: implement only the frozen synthetic post-acquisition interface after
contract commit `c6e216f` passed CI `31281290300`. Preserve the source arrays
and reference identity while deriving explicit eligibility, selection, weights,
and adapted transport masks under the registered target-blind rule.

Reason: contact loss, unknown quality, channel noise, and missing samples can
be represented and refused without copying hardware topology, inventing
impedance or anatomy, installing a backend, or touching a real signal. Exact
configuration, source-order, subset/weight, metadata, and payload hashes make
those semantics replayable and inspectable.

Gate: commit and push the locally qualified implementation, require both CI
jobs to pass for that exact commit, then run at most one measured synthetic
create/metadata-inspect roundtrip under the registered time, RSS, disk, output,
thread, and file caps. Remove both generated files and retain only aggregate
measurements and hashes. Any failed gate parks work order 5 without a rerun or
scope expansion.

Scientific boundary: deterministic contact and mask mechanics are engineering
evidence only. They establish no real ear-EEG quality, brain-specific source,
decoding accuracy, generalization, latency, consumer-earbud capability, home
use, or clinical utility.

Evidence: `docs/CONTACT_AWARE_EAR_CHANNEL_IMPLEMENTATION.md` and
`registries/contact_aware_ear_channel_implementation.v0.json`.

## 0117 - Close Synthetic Contact Semantics And Gate Loop 54-A

Decision: accept the one post-green work-order-5 create/inspect roundtrip. All
18 registered gates passed under the frozen time, memory, free-disk, output,
file, causality, mask, provenance, refusal, and access limits. Retain only the
aggregate receipt and remove both generated fixture files.

Measured basis: exact implementation
`76ccc63bdb62b7695dd12ead6ae629c3ab73bb53` passed CI `31282344300` before
one 0.40-second execution at 55,394,304-byte peak RSS. The 923,980-byte payload
and 14,894-byte sidecar replayed all registered hashes; 46,367,866,880 free
bytes were available before execution, and zero generated files remain.

Route: mark work order 5 complete. Activate work order 6 only to bind the
immutable Loop 54-A registration, pinned green descendant, and remotely green
recovery record into a new exact decision surface, then qualify a parser on
synthetic fixtures after that decision. Do not open or stat S20, resolve its
siblings, or infer real header readability from the synthetic interface.

Scientific boundary: this result validates software representation and refusal
mechanics only. It establishes no real ear EEG or S20 content quality, neural
origin, decoding accuracy, generalization, latency, hardware capability, home
use, or clinical utility.

Evidence: `docs/CONTACT_AWARE_EAR_CHANNEL_RESULT.md` and
`registries/contact_aware_ear_channel_result.v0.json`.

## 0118 - Freeze The Recovery-Bound Loop 54-A Decision Surface

Decision: supersede the historical non-actionable v0 request with a new v1
request that binds the immutable `c114623` registration, green pinned-toolchain
anchor `2232993`, green additive recovery commit `5915bdf`, and completed work
order 5. Preserve the historical exact-run Ruff failure rather than calling it
green or rewriting the frozen registration.

Evidence order: the v1 request commit must first be pushed and remotely green.
Only then may the user send its exact Tier C sentence. That sentence must be
preserved in a separate authorization-only commit and become remotely green
before generated synthetic parser implementation. The implementation commit
must then become remotely green before one registered 11,705-byte VHDR open.

Boundary: every implementation, path-stat, VHDR, sibling, target, model,
network, hardware, rerun, and claim authorization remains false in the request.
No S20 path was resolved, statted, hashed, or opened while preparing it.

Engineering capability proposed: NeuroDecodeKit can qualify and then execute a
strict one-file BrainVision-header compatibility check under a recovery-bound,
no-sibling, one-shot evidence order.

Scientific claim not established: no S20 path or content was accessed, so this
request establishes no header readability, EEG signal quality, trial validity,
neural advantage, decoding accuracy, generalization, latency, device, home-use,
or clinical result.

Evidence: `docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md` and
`registries/loop54_stage_a_recovery_authorization_request.v1.json`.

## 0119 - Record The Exact Recovery-Bound Loop 54-A Decision

Decision: accept the maintainer's exact registered sentence after request
commit `19813a8` passed both jobs in CI `31283297030`. Preserve the frozen
request and contract as all-false snapshots; record authorization in separate
human and machine decision artifacts.

Stage order: after this authorization-only commit becomes remotely green,
implement and adversarially qualify the strict standard-library parser using
only generated synthetic VHDR fixtures. Keep every S20 path operation at zero.
Only after the exact implementation commit becomes remotely green may the one
registered 11,705-byte VHDR execution proceed.

Boundary: the conditional real stage allows one no-follow content open, at most
16,384 read bytes, strict allowlisted parsing, inert sibling basenames, and one
target-free ledger plus summary under 1 MiB. VMRK, EEG, MAT, siblings, targets,
models, training, scoring, network, hardware, rerun, and claims remain closed.

Engineering capability authorized for testing: one strict standard-library
parser may be qualified on generated synthetic fixtures and later used for one
bounded compatibility check after both green gates.

Scientific claim not established: this decision is not a parser or S20 result
and establishes no header readability, EEG quality, neural advantage, decoding
accuracy, generalization, latency, hardware, home-use, or clinical result.

Evidence: `docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_DECISION.md` and
`registries/loop54_stage_a_recovery_authorization_decision.v1.json`.

## 0120 - Qualify The Strict VHDR Parser Before Any S20 Access

Decision: after exact authorization commit `2177b36` passed Base Python and
Optional Neuro Readers in CI `31286428489`, implement the L54-A parser with the
Python standard library and qualify it only on generated VHDR bytes and
temporary synthetic filesystem layouts.

Implementation boundary: require strict declared UTF-8, UTF-8 BOM, or explicit
Windows-1252; reject replacement decoding, malformed or duplicate declarations,
unsafe sibling references, incomplete or duplicate channels, invalid sampling,
source drift, symlinks, output collisions, forbidden counters, reruns, and
overclaims. Keep `DataFile` and `MarkerFile` as inert basenames. Precompute and
cap both outputs, create the summary exclusively first, and create the canonical
JSON ledger last as the no-overwrite commit marker. Add no base dependency.

Evidence order: the exact implementation must be committed, pushed, and have
both CI jobs green before the one registered 11,705-byte VHDR pass. The
implementation milestone performs zero S20 path stats, VHDR opens, sibling
operations, target reads, model runs, network operations, or retained fixture
writes.

Engineering capability added: NeuroDecodeKit now has a strict, bounded,
sibling-blind VHDR compatibility interface that covers all 22 registered
refusal classes on synthetic fixtures.

Scientific claim not established: no S20 content was opened, so there is still
no header-readability result, EEG signal-quality evidence, event or trial
validation, neural advantage, decoding accuracy, generalization, latency,
portable-hardware, home-use, or clinical result.

Evidence: `docs/LOOP_54_STAGE_A_VHDR_IMPLEMENTATION.md` and
`registries/loop54_stage_a_vhdr_implementation.v0.json`.

## 0121 - Park Loop 54-A At The Strict Preamble Gate

Decision: preserve the one registered execution as consumed after exact
implementation `b486fdf` passed Base Python and Optional Neuro Readers in CI
`31287819503`. The invocation opened and read the exact 11,705-byte VHDR once,
passed no-follow, regular-file, size, Git-blob, and strict-decoding checks, and
then returned the registered `L54A-F11` refusal because the frozen format
preamble requirement was not satisfied.

Evidence boundary: the command returned `2` in 0.20 seconds external wall time
at 24,051,712-byte peak RSS. It wrote zero registered output bytes and did not
resolve, stat, hash, or open VMRK, EEG, MAT, or any sibling. It did not publish
the raw first line or any header value. Every signal, marker, target, cache,
split, model, training, inference, scoring, network, provider, device,
hardware, release, rerun, and claim-upgrade counter remained zero.

Route: L54-Q2 declared-header compatibility was not established. Do not rerun,
amend the parser from the observed outcome, use a fallback reader, reopen S20,
or start Loop 54-B/C. Those routes remain blocked or separately unauthorized.

Engineering capability added: NeuroDecodeKit executed one exact, bounded,
sibling-blind VHDR compatibility gate and preserved its failure without leaking
raw or sibling content.

Scientific claim not established: no EEG signal, event, trial, target, or model
was accessed, so this result establishes no neural advantage, decoding
accuracy, generalization, real-time, portable-hardware, home-use, or clinical
result.

Evidence: `docs/LOOP_54_STAGE_A_VHDR_RESULT.md` and
`registries/loop54_stage_a_vhdr_result.v0.json`.

## 0122 - Park The One CML-v0 Synthetic Run At The Exact Check Gate

Decision: preserve the seed-5513 work-order-13 execution as consumed after
contract `67709a3` passed CI `31294479865` and exact implementation `90fa467`
passed CI `31295430105`. The 4,535-parameter model completed the one frozen
600-step fit and reached `1.0` hand and key accuracy on all 16 constructed
signal-bearing check rows.

Evidence boundary: potential, mu, and beta matching ablations localized their
constructed factors; the hand/key marginal, future-tail causality checks, and
checkpoint replay passed. Eighteen of 19 check gates passed. The maximum
float32 key-logit difference after the registered uniform common-mode mutation
was `1.9073486328125e-6`, exceeding the frozen `1e-6` tolerance by
`9.073486328125e-7`.

Route: park at `CML-R0`. Do not waive or relax the tolerance, change the seed,
reuse seed 5513, rerun the gate, or deliver the 16 synthetic final targets.
Final scoring events remain zero. The run used 6.5530732499901205 seconds,
398,737,408-byte peak RSS, and 37,371 generated bytes; all resource gates
passed. The generated checkpoint and report are represented by size and hash
only and are removed after closeout.

Engineering capability added: the exact compact CML-v0 implementation can fit,
localize, causally probe, and deterministically replay the deliberately
constructed factor suite under a strict check-before-final protocol.

Scientific claim not established: no real or protected EEG was accessed, the
synthetic conjunction failed, and no neural advantage, decoding accuracy,
brain-specific origin, generalization, real-time, portable-hardware, home-use,
assistive, or clinical result was established.

Evidence: `docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md` and
`registries/causal_motor_lattice_synthetic_result.v0.json`.

## 0123 - Freeze A Tiny Public Motor Acquisition Before Any EDF Read

Decision: register work order 8 as one acquisition-only PhysioNet EEGMMIDB
v1.0.0 gate. Bind exactly nine EDF paths from S001-S003 and runs 03/07/11,
exactly 23,248,224 payload bytes, and the nine official SHA-256 values. Preserve
runs 03/07 as prospective future fit candidates and run 11 as a prospective
future check candidate without creating or activating a split.

Registration evidence: official PhysioNet dataset and checksum metadata plus
the official MNE task mapping were reverified on 2026-08-09. Ten HTTP HEAD
requests were made across the nine selected paths, including one repeated
first-file probe. All reported HTTP 200 and transferred zero EDF body bytes.
ETag, Last-Modified, and Content-Type remain informational observations;
version, path, exact bytes, and official SHA-256 are the hard identities.

Prospective execution boundary: after a separate exact Tier C decision and a
remotely green fixture-qualified implementation, allow at most one no-retry
acquisition invocation, one opaque local SHA-256 pass per file, 300 seconds,
one thread and worker, 256 MiB peak RSS, 1 MiB metadata network, 32 MiB EDF
payload network, 64 MiB incremental disk, 2 GiB minimum free disk, and 1 MiB
combined receipts. Do not parse EDF, fetch `.event` files, create a split, load
a model, train, infer, score, substitute a path, or continue into work order 9.

Evidence order: this registration commit must be pushed and remotely green
before a hash-bound authorization packet and request are created. That request
must independently become remotely green before the exact user decision. The
decision must become remotely green before implementation, and the exact
implementation must become remotely green before one acquisition. Every
execution flag is currently false.

Engineering capability proposed: NeuroDecodeKit can acquire and opaque-verify
one tiny, exact public motor-EEG bundle under deterministic identity, storage,
network, access-order, and no-retry controls.

Scientific claim not established: no EDF payload was opened, so this
registration establishes no EDF readability, event correctness, signal
quality, motor effect, neural advantage, model accuracy, generalization,
real-time behavior, portable hardware, home use, assistive value, or clinical
result.

Evidence: `docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md`,
`registries/physionet_motor_acquisition_contract.v0.json`, and
`tests/test_physionet_motor_acquisition_contract.py`.

## 0124 - Bind The Public Motor Acquisition To One Exact Tier C Request

Decision: after registration commit
`2a7b4188553e221133d788a081b838dbbb9f41bb` passed both jobs in CI
`31301730612`, create one additive authorization packet and all-false machine
request. Bind the preregistration, contract, invariant test, packet, and request
test by exact SHA-256 and Git blob identity without modifying the immutable
registration.

Requested scope: after a separate exact decision is remotely green, qualify a
dependency-light implementation only with generated local fixtures and mocked
network responses. After that exact implementation is also remotely green,
allow one no-retry invocation for the nine registered EDF paths, one opaque
local SHA-256 pass per file, one complete isolated 23,248,224-byte bundle, and
bounded receipts. Preserve every registered thread, wall-time, RSS, network,
disk, free-space, no-substitution, and no-overwrite limit.

Evidence order: this request commit must first be pushed and remotely green.
Only then may the maintainer's exact sentence be accepted into a separate
authorization-only decision. That decision must become remotely green before
implementation; implementation must become remotely green before acquisition.
The request itself grants no implementation, metadata recheck, download,
local-path, parse, model, rerun, or claim permission.

Engineering capability proposed: NeuroDecodeKit has a byte-bound decision
surface for one tiny public motor-EEG acquisition and can reject drift before
any EDF payload is requested.

Scientific claim not established: the request opened no EDF payload and
establishes no readability, event correctness, signal quality, motor effect,
neural advantage, model accuracy, generalization, real-time behavior,
portable-hardware performance, home use, assistive value, or clinical result.

Evidence: `docs/PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_PACKET.md`,
`registries/physionet_motor_acquisition_authorization_request.v0.json`, and
`tests/test_physionet_motor_acquisition_authorization_request.py`.

## 0125 - Record The Exact Public Motor Acquisition Decision

Decision: accept the maintainer's exact registered sentence after request
commit `f6eb577fdd8c168a4af229248dc56960e3ba75d8` passed Base Python job
`93216583586` and Optional Neuro Readers job `93216583625` in CI
`31302161647`. Preserve the contract and request as immutable pending/all-false
snapshots; record the later authorization in separate human and machine
decision artifacts.

Evidence order: this authorization-only commit must become remotely green
before any implementation begins. Implementation may use only generated local
fixture bytes and mocked network responses, with no source request or local
PhysioNet path operation. That exact implementation must then become remotely
green before metadata reverification and the single no-retry acquisition.

Authorized boundary: exactly nine EEGMMIDB v1.0.0 EDF paths, 23,248,224 final
bytes, one opaque local SHA-256 pass per file, one acquisition invocation, zero
payload retries, one thread/worker/job, 300 seconds, 256 MiB RSS, 1 MiB metadata
network, 32 MiB EDF network, 64 MiB incremental disk, 2 GiB minimum free disk,
and 1 MiB combined receipts. EDF parsing, `.event` access, signals, targets,
splits, models, training, inference, scoring, additional files, work order 9,
reruns, release, and claims remain unauthorized.

Storage clarification: the maintainer separately offered up to 10 GB for future
data work. Treat that as unused prospective headroom, not an amendment to this
immutable 23,248,224-byte scope. Any larger acquisition needs its own measured
contract and applicable exact Tier C decision.

Engineering capability authorized for testing: one dependency-light,
hash-bound acquisition implementation and one exact public-data invocation may
proceed through the two ordered green gates.

Scientific claim not established: this authorization is not an EDF or EEG
result and establishes no readability, event correctness, signal quality,
motor effect, neural advantage, model accuracy, generalization, real-time
behavior, portable hardware, home use, assistive value, or clinical result.

Evidence: `docs/PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_DECISION.md`,
`registries/physionet_motor_acquisition_authorization_decision.v0.json`, and
`tests/test_physionet_motor_acquisition_authorization_decision.py`.

## 0126 - Qualify The Public Motor Acquirer Before Source Access

Decision: after authorization decision `00b91edd213112fd186711d06369ae4f836b2243`
passed Base Python job `93322699209` and Optional Neuro Readers job
`93322699259` in CI `31344104565`, implement one separate standard-library
executor and `physionet-motor-acquire` CLI. Keep dry-run as the default and
require exact current implementation and remote-green evidence for execution.

Metadata boundary: the future registered invocation may GET only the dataset
page, checksum manifest, and MNE run mapping, then HEAD only the nine exact EDF
URLs. Require exact version, DOI, public availability, license label, run
mapping, path, size, and official SHA-256 before the first EDF body request.
Reject every redirect, sidecar, wildcard, substitution, retry, extra member,
collision, symlink, and unregistered host.

Payload boundary: stream the nine opaque bytestrings into one isolated temporary
tree, enforce all frozen resource caps, open each local EDF exactly once for
size and SHA-256, atomically promote only a complete verified directory, and
emit the two bounded private receipts. Expose no EDF parser or downstream
stage. Cleanup is restricted to invocation-created temporary paths.

Qualification evidence: 23 dedicated adversarial tests and 68 focused tests
pass using generated invalid-UTF-8 bytes and mocked responses. The full
one-thread suite passes 1,448 tests with three expected skips and 493 subtests.
The consumed CML registry remains unchanged; its shared-CLI hash is preserved
as historical evidence while current command presence remains tested.

Execution order: commit and push this exact implementation, obtain green Base
Python and Optional Neuro Readers jobs, and only then perform the one registered
metadata/acquisition invocation. No source metadata, local PhysioNet path, EDF,
sidecar, event, signal, target, split, model, training, inference, scoring,
provider, hardware, work-order-9, or rerun operation occurred during this
milestone. The separate 10 GB allowance remains unused future headroom.

Engineering capability added: one strict standard-library path can reverify,
acquire, opaque-hash, atomically promote, and privately receipt the exact
registered nine-EDF bundle after the ordered remote-green gates.

Scientific claim not established: fixture-only implementation establishes no
EDF readability, event correctness, signal quality, motor effect, neural
advantage, model accuracy, unseen-person generalization, real-time latency,
portable hardware, home use, assistive value, or clinical result.

Evidence: `docs/PHYSIONET_MOTOR_ACQUISITION_IMPLEMENTATION.md`,
`registries/physionet_motor_acquisition_implementation.v0.json`,
`src/neurodecodekit/datasets/physionet_motor_acquisition.py`, and
`tests/test_physionet_motor_acquisition.py`.

## 0127 - Close The One Public Motor Acquisition At Engineering Evidence

Decision: after exact implementation `92760ce7e3123058f15127b9afd8d5e4bae75321`
passed Base Python job `93326279510` and Optional Neuro Readers job
`93326279396` in CI `31345401581`, consume the one registered work-order-8
invocation without retry or substitution.

Result: all 12 gates passed. Twelve metadata requests consumed 442,178 response-
body bytes. Nine EDF body requests transferred exactly 23,248,224 bytes. Each
file received exactly one opaque local size/SHA-256 pass, all nine hashes
matched the official identities, and the complete directory promoted. Runtime
was 50.682373 seconds, peak RSS 55,181,312 bytes, incremental disk peak
28,327,635 bytes, and combined private receipts 16,083 bytes.

Access result: every EDF header, annotation, event, signal, task, target, label,
channel, montage, reference, geometry, sampling, quality, cache, split, model,
checkpoint, training, inference, scoring, provider, hardware, upload, retry,
rerun, and work-order-9 counter remained zero. End-to-end latency was not
measured. The payload and generated receipts remain Git-ignored and are bound
only by aggregate receipt hashes in the sanitized closeout.

Next gate: work order 8 is complete and consumed with no rerun. Work order 9
remains separately gated; acquisition success does not authorize EDF parsing,
annotation extraction, target delivery, model work, or scoring. The separate
10 GB allowance remains future headroom and did not expand this invocation.

Engineering capability added: NeuroDecodeKit acquired and opaque-verified one
exact, isolated nine-file public EEGMMIDB bundle under the registered identity,
access-order, network, runtime, memory, storage, and no-retry controls.

Scientific claim not established: no EDF content was parsed and no event,
signal, target, model, or score was produced, so this result establishes no
motor-EEG effect, neural advantage, decoding accuracy, unseen-person
generalization, real-time latency, portable hardware, home use, assistive
value, or clinical result.

Evidence: `docs/PHYSIONET_MOTOR_ACQUISITION_RESULT.md`,
`registries/physionet_motor_acquisition_result.v0.json`, and
`tests/test_physionet_motor_acquisition_result.py`.

## 0128 - Make Work Order 9 A Three-Axis Falsification Gate

Decision: the next evidence-producing step is one bounded public motor-task EEG
positive control over the already acquired S001-S003 runs 03/07/11 inventory.
Do not spend the separate 10 GiB headroom before the model family, causal view,
controls, prediction freeze, scorer, and thresholds are fixed on this
qualification cohort.

Scientific design: require held-out run-11 prediction, fixed central mu/beta
physiology, and confound/leakage controls together. Runs 03 and 07 alone may
select between four-component CSP plus shrinkage LDA and regularized Riemannian
MDM. Accuracy without the physiology and confound conjunction cannot exceed
`WO9-V2` because the dataset's left/right class is coupled to a left/right
visual target and it lacks separate EOG and EMG measurements.

Evidence order: isolate run-11 targets during extraction; freeze every primary,
comparator, no-signal, zero-signal, pre-cue, timing, label-deranged,
trial-displaced, channel-deranged, hemisphere-swapped, frontal/occipital, and
central prediction; commit and push a hash-only ledger; require both CI jobs
green; then deliver and score the same 45 run-11 targets once. No individual
target, prediction, probability, or participant result enters Git.

Resource decision: no network or new payload, one thread/worker/job, 1,800
seconds, 805,306,368-byte peak RSS, 67,108,864-byte private output, at most 40
classical fits and 64 prediction sets, one final score, and no retry or rerun.

Maximum result: `WO9-V3` is a three-person held-out-run motor-task EEG pilot
with motor-compatible sensorimotor physiology under proxy controls. It is not
brain-specific origin, unseen-person generalization, typing, language or
thought decoding, real-time performance, portable hardware, home use,
assistive benefit, or clinical utility. A clean pass prospectively routes to
an unchanged larger-cohort replication; a failure routes to the frozen failure
class without adding participants to hunt for a better result.

Authorization boundary: this registration is Tier C planning only. It permits
no local PhysioNet operation, EDF hash/parse, header, annotation, signal,
target, dependency import, derivative, split, fit, inference, prediction
freeze, score, or claim. A separate hash-bound exact decision and remotely
green synthetic-only implementation remain mandatory.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md`,
`docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md`,
`registries/physionet_motor_positive_control_contract.v0.json`, and
`tests/test_physionet_motor_positive_control_contract.py`.

## 0129 - Request One Conditional Work Order 9 Execution

Decision: after registration `3c00557ecfb09c80e30843589ae295a09feec97c`
passed Base Python job `93330354031` and Optional Neuro Readers job
`93330354047` in CI `31346882592`, prepare one separate exact Tier C request.
The request itself authorizes nothing.

Implementation request: after a separately green authorization-only decision,
allow generated-fixture-only implementation and one narrow Git-ignored
classical environment containing only the registered NumPy, SciPy, MNE,
scikit-learn, and pyRiemann families. Keep the base install dependency-free and
exclude Torch and broad EEG stacks. Require the exact implementation to be
committed, pushed, and remotely green before local PhysioNet access.

Execution request: one no-network pass over only the acquired nine EDFs, with
one no-follow identity/hash pass and one semantic parse each; target-firewalled
runs-03/07 fit data and run-11 signal/target isolation; at most 40 fits and 64
target-blind prediction sets; then a hash-only prediction freeze committed,
pushed, and remotely green before one delivery and one score of the same 45
targets. Retain the frozen one-thread, 1,800-second, 768 MiB RSS, 64 MiB private
output, zero-new-payload, no-retry, and no-rerun boundary.

Claim decision: the ceiling remains `WO9-V3`, a three-person held-out-run
motor-task EEG pilot with motor-compatible physiology under proxy controls.
No sentence in the packet authorizes a replication cohort or upgrades the
brain-specific, generalization, language, real-time, hardware, assistive, or
clinical claims.

Next evidence order: commit and push this request and require both CI jobs
green. Only then may the exact sentence be accepted from the maintainer and
recorded in separate decision artifacts. Until that sequence completes, every
implementation, dependency, EDF, target, model, freeze, score, and claim flag
remains false.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md`,
`registries/physionet_motor_positive_control_authorization_request.v0.json`,
and `tests/test_physionet_motor_positive_control_authorization_request.py`.

## 0130 - Authorize One Ordered Work Order 9 Execution

Decision: after request `c62b10a6e9dae8d92e5ff54d17403e1054a0ac76`
passed Base Python job `93331241434` and Optional Neuro Readers job
`93331241411` in CI `31347209691`, accept the maintainer's exact registered
sentence into a separate additive authorization record. Preserve the frozen
contract and all-false request as immutable historical snapshots.

Order: the decision commit must become remotely green before generated-fixture
implementation or one isolated optional classical environment. The exact
implementation must then become remotely green before any local PhysioNet
operation. One real execution may make one size/SHA-256 pass and one semantic
parse per exact EDF, use runs 03/07 for fit and family selection, and create
target-blind run-11 predictions. A public aggregate hash-only freeze must be
committed, pushed, and remotely green before the same 45 run-11 targets are
delivered and scored once.

Limits: one execution, no retry or rerun, nine existing EDFs and no new
payload, one thread/worker/job, 1,800 seconds, 805,306,368-byte peak RSS,
67,108,864 private generated bytes, 40 fits, 64 prediction sets, zero real-
execution network bytes, and zero post-target update. Every `.event` sidecar,
additional participant/run/dataset, larger or additional model, provider,
device, hardware, release, replication cohort, and claim beyond `WO9-V3`
remains unauthorized.

Current evidence: this authorization milestone performed one GitHub CI proof
read and zero dependency, local PhysioNet, EDF, target, derivative, model,
freeze, scoring, provider, or hardware operations. It creates no scientific
result.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_DECISION.md`,
`registries/physionet_motor_positive_control_authorization_decision.v0.json`,
and `tests/test_physionet_motor_positive_control_authorization_decision.py`.

## 0131 - Freeze The Exact Work Order 9 Implementation Before Real Access

Decision: after authorization commit
`da9399c4290fc2be81834ed1036a6bede5f52154` passed Base Python job
`93334251403` and Optional Neuro Readers job `93334251379` in CI
`31348287824`, implement only the generated-fixture and bounded environment
surface allowed by that decision. Do not inspect the acquired bundle while
building or qualifying it.

Environment: retain an empty base dependency list and add one narrow optional
`classical` extra for the registered NumPy, SciPy, MNE, scikit-learn, and
pyRiemann families. Bind future execution to the exact qualified versions and
one-thread environment. Do not add Torch, Braindecode, MOABB, a deep model, a
foundation model, a checkpoint, or an alternate backend.

Data boundary: future extraction may parse the exact run-11 T1/T2 annotations
once to create the sealed target artifact, but the model stage opens only the
runs-03/07 target-bearing fit derivative and target-free run-11 prediction
derivative. Describe this honestly as a function and artifact firewall, not an
operating-system sandbox. Run-11 targets cannot participate in fitting,
selection, threshold, channel, parameter, prediction, or control operations.

Evidence binding: require every one of the 12 45-row condition sets to have a
separate SHA-256 in the public freeze. Also bind the private payload, three
derivatives, source manifest, split protocol, configuration, implementation
registry, tracked code hashes, selected family, dependency versions, operation
counters, and resources. The scorer must recompute all condition hashes before
opening the sealed artifact.

Scientific routing: freeze the negative contralateral-minus-ipsilateral
mu/beta direction and require the hemisphere-swap condition to fail the primary
gate for `WO9-V3`. These are implementation clarifications made without real
outcomes. Keep the preregistered `WO9-V0` through `WO9-V3` router and claim
ceiling unchanged.

Qualification: the final generated nine-run, 135-event roundtrip passed all
implementation gates with 33 fits, 45 target-blind inferences, 12 prediction
sets, 8.961233 seconds, 327,647,232-byte peak RSS, and 20,825,424 generated
bytes. Real-data, real-target, and network counters were zero. The synthetic
`WO9-V2` branch has no claim value and the generated artifacts were removed.

Next evidence order: commit and push the implementation and require both CI
jobs green at that exact commit. Only then may one real target-blind execution
begin. Do not score even after a successful run until its aggregate freeze is
separately committed, pushed, and remotely green.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_IMPLEMENTATION.md`,
`registries/physionet_motor_positive_control_implementation.v0.json`,
`src/neurodecodekit/experiments/physionet_motor_positive_control.py`, and the
two Work Order 9 implementation test modules.

## 0132 - Freeze Work Order 9 Predictions Before Any Final Target Opens

Decision: after exact implementation
`52b9b15a64972a285efbe630f49600727e836983` passed Base Python job
`93343718364` and Optional Neuro Readers job `93343718355` in CI
`31351728650`, consume the single authorized no-network target-blind execution
and stop before scoring.

Observed integrity: the private acquisition manifest matched, all nine exact
EDFs passed one size/SHA-256 traversal and one semantic parse, all 64 channels
and available geometry were retained, 160 Hz and T0/T1/T2 were exact, and all
135 task events passed without target-derived exclusion or substitution.

Observed model stage: runs 03/07 alone selected CSP-LDA. The frozen inventory
is 33 classical parameter-update fits, 45 target-blind model inferences, three
train-only prior fits, and 12 complete 45-row prediction/control sets. The
model stage received 45 run-11 signal rows and zero run-11 target rows.

Freeze boundary: commit only aggregate hashes, counts, dependencies,
provenance, split/configuration identities, resource measurements, warnings,
and claim limits. Keep individual IDs, predictions, probabilities, targets,
participant metrics, participant outcomes, derivatives, and the private
prediction payload Git-ignored. Require the future scorer to verify every
condition hash before target scoring.

Resources: execution used 3.054760 seconds, 460,734,464-byte peak RSS, and
20,852,059 private generated bytes under one thread, worker, and numerical job.
Network bytes, new payload bytes, additional files, sidecars, final target
deliveries, scores, retries, and reruns were zero.

Next evidence order: commit and push the aggregate freeze SHA-256
`3c100daa8a6a2816ce4270c9e32cbdcc4cd30d70d1c255e37596c2ca6f665de4`
with its document, invariants, and status updates. Require both CI jobs green
at that exact commit. Only then may the isolated scorer open the same sealed
45 targets once and route `WO9-V0` through `WO9-V3`. No post-target update,
retry, or rerun is permitted.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREDICTION_FREEZE.md`,
`registries/physionet_motor_positive_control_prediction_freeze.v0.json`, and
`tests/test_physionet_motor_positive_control_prediction_freeze.py`.

## 0133 - Close Work Order 9 At WO9-V1 And Preserve The Low-Frequency Lead

Decision: after freeze `01eeff6e9a5ead1790e0f91aa52a443402eb397c`
passed Base Python job `93345130576` and Optional Neuro Readers job
`93345130569` in CI `31352250838`, deliver and score the same sealed 45 targets
once. Apply the frozen router and make no post-target change.

Primary verdict: the selected 8-30 Hz CSP-LDA reached 27/45 correct, 0.603755
pooled balanced accuracy, 0.592262 macro-participant balanced accuracy, and
`p=0.137390`. It beat the train-only no-signal prior but failed the frozen
primary threshold conjunction. Route `WO9-V1` and do not retry, rerun, tune,
or promote another arm to the registered primary.

Secondary evidence: preserve the prespecified 0.5-4 Hz shrinkage-LDA result of
36/45, 0.800395 pooled balanced accuracy, 0.800595 macro-participant balanced
accuracy, minimum participant 0.732143, all three participants above chance,
and `p=0.000183`. This is legitimate held-out task-information evidence
because it was fixed, trained on runs 03/07, frozen, and scored once.

Interpretation ceiling: do not call the low-frequency arm brain-specific motor
decoding. The task has a lateralized visual cue, EOG/EMG are unavailable,
motor-compatible mu/beta physiology failed at `p=0.108337`, and the central
sensorimotor model underperformed the frontal/occipital proxy. The result
supports a slow task-linked signal and a new localization hypothesis only.

Resource closeout: one target delivery, one score, 9.661659 total seconds,
460,734,464-byte peak RSS, 20,852,334 private bytes, 10,443 public bytes, one
thread/worker/job, and zero network, new payload, retry, or rerun. Every
resource gate passed and no individual protected output is public.

Next decision: work order 9 is complete and consumed. Any independent slow-
potential replication must use untouched participants or runs, prospectively
freeze the low-frequency model and cue/ocular/localization controls, and obtain
a new contract plus exact real-data authorization. These consumed targets
cannot be used to select that future design beyond the aggregate hypothesis
already recorded here.

Evidence: `docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_RESULT.md`,
`registries/physionet_motor_positive_control_result.v0.json`, and
`tests/test_physionet_motor_positive_control_result.py`.

## 0134 - Turn The Slow-Potential Lead Into WO9R Cohort Confirmation

Decision: preserve the Work Order 9 `WO9-V1` verdict and consumed S001-S003
boundary, while treating its prespecified `0.5-4 Hz` secondary result as a new
prospective hypothesis. Do not promote that arm inside Work Order 9 or reopen
its private artifacts. Use a separately named additive lane, `WO9R`, so work
orders 10-20 and Loop 54 dependencies remain unchanged.

Cohort: select the contiguous untouched S004-S015 range before payload access.
Prospectively pair execution fit runs 03/07 with sealed run 11 and imagery fit
runs 04/08 with sealed run 12. The candidate inventory is 12 participants and
72 EDFs with no `.event` sidecars. Exact paths, sizes, and official SHA-256
values remain a future metadata-bound contract; no substitution is allowed.

Model: carry the existing prespecified comparator forward byte-for-behavior as
the sole primary template: continuous causal fourth-order `0.5-4 Hz` SOS,
common-average reference over all retained channels, a `+1` to `+3` second cue-
aligned window, four temporal means plus one slope per channel, and fixed
shrinkage-LDA `0.1`. No architecture, channel, threshold, hyperparameter, deep
model, foundation model, or LLM selection belongs in this confirmation test.

Falsification: freeze execution-native, imagery-native, and bidirectional
transfer predictions together. Require participant-level statistics and fixed
central, frontal ocular-sensitive, occipital visual-sensitive, frontal-
asymmetry, early/pre-cue, timing, no-signal, label, displacement, channel, and
hemisphere controls. Route `WO9R-R0` through `WO9R-R4`, with `R4` capped at a
within-dataset, multi-person, motor-compatible low-frequency EEG task effect.
Dedicated EOG/EMG, measured movement onset, cue neutrality, brain-specific
origin, and independent-team replication remain unavailable.

Safety: later contracts must use one thread/worker/job, at most 1 GiB RSS,
1,800 seconds, 64 MiB private output, an expected payload below 256 MiB, at
least 20 GiB free disk, and zero retry/rerun/post-final update. The user's
10 GiB allowance is a ceiling, not a spending target.

Current evidence: this Tier A pass read public documentation and committed
aggregate evidence only. It performed zero local PhysioNet or private Work
Order 9 operations, EDF payload requests, header/event/signal/target reads,
splits, model runs, scores, provider calls, or hardware operations.

Next gate: prepare an exact metadata-bound acquisition/experiment
preregistration and all-false Tier C request. Do not touch a selected payload
before that request, a separate exact decision, fixture-only implementation,
and remote-green implementation evidence exist in order.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PRIMARY_SOURCE_RESEARCH.md`,
`registries/physionet_low_frequency_cohort_confirmation_research.v0.json`, and
`tests/test_physionet_low_frequency_cohort_confirmation_research.py`.

## 0135 - Freeze WO9R Metadata, Experiment, And Combined Target Firewall

Decision: convert the WO9R research design into one exact preregistration
without opening or requesting an EDF. Registration commit
`716e5432498052b78cb799c9f4e3bfbae68e3ad2` passed Base Python job
`93351737101` and Optional Neuro Readers job `93351737088` in CI
`31354565966`. Preserve that tree as the immutable experiment boundary.

Metadata identity: use twelve public `ListObjectsV2` responses from
PhysioNet's official `physionet-open` bucket for exact object paths and sizes,
plus the official v1.0.0 checksum manifest for SHA-256 identities. The retained
registration bodies are 340,703 bytes across 13 GETs. No request was sent to an
EDF URL. Freeze exactly 72 S004-S015 files for runs 03/04/07/08/11/12 totaling
184,252,032 bytes; no `.event` sidecar, wildcard, replacement, or extra file is
allowed.

Experiment: carry only the exact prespecified `0.5-4 Hz` shrinkage-LDA
template. Bind execution 03/07 to sealed 11, imagery 04/08 to sealed 12, 720
expected fit rows, 360 jointly sealed final rows, 144 participant-specific fit
ceilings, 18 condition families, 216 target-blind inference/prediction sets,
literal spatial/temporal/derangement controls, participant-level exact tests,
and `WO9R-R0` through `WO9R-R4`. Both final target sets must freeze and open
together; one cannot tune the other.

Target reality: the future EDF reader will necessarily materialize annotation
values. The firewall must immediately isolate final labels into a sealed scorer
artifact and expose only target-free features and identities to predictive
code. This is a function-and-artifact boundary, not a claim that target bytes
remain physically unopened.

Resources: acquisition remains one-shot at exactly 184,252,032 payload bytes,
one thread/worker/job, 900 seconds, 256 MiB RSS, 384 MiB incremental disk, and
at least 20 GiB free. Analysis remains one-shot at one thread/worker/job, 1,800
seconds through freeze, 1 GiB RSS, 64 MiB private output, zero network/new
payload, one final delivery/score, and zero retry/rerun/post-target update.

Authorization posture: prepare a separate all-false request that binds the
green registration proof and one exact sentence. The request is not a decision.
No implementation, dependency installation, acquisition, local PhysioNet
operation, fit, inference, target delivery, scoring, cleanup, rerun, or claim
promotion is authorized before that request is committed, pushed, remotely
green, and followed by a separate exact Tier C decision-only commit that also
becomes remotely green.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREREGISTRATION.md`,
`registries/physionet_low_frequency_cohort_confirmation_contract.v0.json`,
`tests/test_physionet_low_frequency_cohort_confirmation_contract.py`,
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md`,
`registries/physionet_low_frequency_cohort_confirmation_authorization_request.v0.json`,
and
`tests/test_physionet_low_frequency_cohort_confirmation_authorization_request.py`.

## 0136 - Accept Short-Form Approval Only As An Immutable Packet Reference

Decision: honor the maintainer's explicit instruction, "i dont want to type
out exact auth sentences anymore -- keep going, move the needle, continue, you
approved to go on", as authorization for the sole currently presented WO9R
packet. Preserve those actual words and do not claim the maintainer typed the
long-form paragraph. The immediately preceding response named the packet,
request commit `580708fa1f24772a2f9d7cfd572a421b860a1f14`, green CI
`31355270896`, and the one remaining Tier C decision gate, so the reference is
unambiguous.

Scope rule: waive only repetitive recital. Incorporate the immutable green
packet by reference, including all 72 file identities, 184,252,032 payload
bytes, S004-S015 participants, runs, target firewall, fixed model, 18
conditions, 144-fit and 216-inference limits, resources, no-retry/no-rerun
rules, and claim ceiling. No extra data, dependency installation, model,
selection, retry, release, hardware, or claim permission may be inferred from
"continue".

Prospective interface: short approval is acceptable only when exactly one
green packet is the active Tier C gate, the assistant has just identified its
packet/commit/CI/scope, the maintainer unambiguously approves continuation, and
a separate decision quotes the real message and binds immutable hashes. That
decision must itself become remotely green before implementation or access.
Ambiguity, multiple packets, changed scope, or absent green evidence fails
closed. Separate Tier C decisions remain required; boilerplate recital does
not.

Current evidence: the decision stage made one GitHub CI verification read and
zero metadata, EDF, local-path, dependency, implementation, derivative, model,
target, score, provider, stream, device, or hardware operations. The unrelated
tracker inspection NDJSON remains untouched.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_DECISION.md`,
`registries/physionet_low_frequency_cohort_confirmation_authorization_decision.v0.json`,
and
`tests/test_physionet_low_frequency_cohort_confirmation_authorization_decision.py`.

## 0137 - Consume Before Access And Freeze The Complete WO9R Interface

Decision: implement the authorized WO9R packet as one small, explicit chain:
metadata-first opaque acquisition, sequential strict EDF interpretation,
compact causal features, target-firewalled derivatives, fixed participant-
specific shrinkage LDA, all 18 registered conditions, one combined aggregate
hash freeze, and one isolated aggregate scorer. Reuse the exact existing
classical environment and add no dependency or model family.

Access-order rule: create the real-analysis consumed marker before the first
bundle inspection or EDF operation. Create the scoring consumed marker before
the first private prediction, target-free derivative, or sealed-target
hash/open. After either marker, any integrity, target-firewall, dependency,
resource, or output failure parks the stage; it never creates a retry. Before
either marker, only immutable Git/CI/registry checks and absent-output preflight
are allowed.

Data-minimization rule: never persist raw windows. Retain only four temporal
means and one slope per channel, identities, timings, geometry, and provenance.
The model stage receives 720 labeled fit rows and 360 target-free final rows.
The final annotations may be materialized once by the firewall into a separate
sealed artifact, but no final target reaches model, selection, threshold,
normalization, or channel code. Public freeze output contains hashes, not
individual predictions, probabilities, targets, or participant outcomes.

Qualification result: one generated 72-run roundtrip completed exactly 144
fits and 216 target-blind participant-condition prediction sets in 12.083017
seconds at 260,784,128-byte peak RSS with 4,215,687 generated bytes. All
engineering gates passed; network, real-data, and real-target reads were zero;
generated files were removed. Its synthetic `WO9R-R3` route is not scientific
evidence.

Current boundary: implementation must be committed, pushed, and pass both
required CI jobs before any registered acquisition or local PhysioNet access.
The combined final targets remain closed until the later aggregate prediction
freeze is committed, pushed, and remotely green. Even a future `WO9R-R4`
cannot establish brain-specific origin or independent replication.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_IMPLEMENTATION.md`,
`registries/physionet_low_frequency_cohort_confirmation_implementation.v0.json`,
`src/neurodecodekit/datasets/physionet_low_frequency_acquisition.py`,
`src/neurodecodekit/experiments/physionet_low_frequency_cohort_confirmation.py`,
`tests/test_physionet_low_frequency_acquisition.py`, and
`tests/test_physionet_low_frequency_cohort_confirmation.py`.

## 0138 - Freeze Execution And Imagery Together Before Any WO9R Score

Decision: consume the single registered acquisition and target-blind analysis
only after exact implementation `8242674` passed both required jobs in CI
`31359548779`. Keep run-11 execution and run-12 imagery predictions in one
combined freeze so neither final target set can influence the other arm,
control interpretation, routing, or publication.

Result: all 72 official hashes matched over 184,252,032 bytes. The analysis
accepted 1,080 events, produced 720 fit rows and 360 target-free final rows,
completed exactly 144 fits and 216 participant-condition prediction sets, and
exposed zero final targets to the model stage. Runtime through freeze was
19.864386 seconds at 303,153,152-byte peak RSS with 4,206,464 private bytes,
one thread, and zero network or new payload bytes.

Publication rule: commit only the aggregate 23,174-byte freeze. It may contain
per-condition and per-participant prediction hashes, but no prediction,
probability, target, participant metric, or participant outcome. Keep every
private derivative and prediction under the Git-ignored execution root.

Current boundary: the freeze is not a scientific result. The same combined 360
targets may open exactly once only after this exact freeze commit is pushed and
both CI jobs are remotely green. Scoring then applies the frozen router without
any refit, selection, threshold, channel, control, or claim change.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREDICTION_FREEZE.md`,
`registries/physionet_low_frequency_cohort_confirmation_prediction_freeze.v0.json`,
and
`tests/test_physionet_low_frequency_cohort_confirmation_prediction_freeze.py`.

## 0139 - Close WO9R At Robust Task Information Without Source Inflation

Decision: after combined freeze
`8cd45d74dfa3517ae53c1427a0eb06e27ad3c870` passed both required jobs in CI
`31360781199`, deliver and score the same 360 sealed execution and imagery
targets exactly once. Preserve the registered `WO9R-R0` through `WO9R-R4`
router and every threshold, model, channel view, control, and participant-level
test without post-target change.

Result: execution passed H1 at 123/180 correct, pooled balanced accuracy
`0.680975`, macro-participant balanced accuracy `0.682292`, 9/12 participants
above chance, and one-sided participant sign-flip `p=0.002930`. Imagery passed
H2 at 131/180, pooled `0.728014`, macro `0.728423`, 12/12 above chance, and
`p=0.000244`. Both registered cross-task transfer directions were positive.

Boundary: do not call the result brain-specific or motor-localized. Central
sensorimotor balanced accuracy `0.647575` did not beat the frontal proxy at
`0.671821`; early-cue accuracy reached `0.762865`; physiology followed the
registered direction in only 5/12 participants; and the mandatory-control
conjunction failed. The exact frozen route is `WO9R-R3`: robust low-frequency
task information across execution and imagery, with motor-compatible
localization unsupported.

Disposition: WO9R is complete and consumed. Final-target deliveries and
scoring events are one each; post-target updates, retries, and reruns are zero.
The next evidence-bearing question requires a fresh cue-neutral or independently
instrumented EOG/EMG-plus-movement-onset design, not a WO9R rerun or larger
classifier.

Evidence:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_RESULT.md`,
`registries/physionet_low_frequency_cohort_confirmation_result.v0.json`, and
`tests/test_physionet_low_frequency_cohort_confirmation_result.py`.

## 0140 - Turn The WO9R Cue Ambiguity Into A Mapping Reversal

Decision: select OpenNeuro IACKD `ds006840` version `1.0.0` as the next
evidence-bearing public-EEG lane. Fit one fixed low-frequency family only on
congruent trials where visual and hand directions agree. Freeze it on held-out
incongruent runs where those directions are opposites, then score the same
predictions against both target views.

Reason: WO9R established robust task information but failed source
localization; early-cue and frontal performance were stronger than the central
motor view. A cue-to-action reversal tests that exact ambiguity more directly
than a larger classifier, another EEGMMIDB split, or a retrospective proxy.

Data decision: bind the 1,340 raw EEG, marker, event, ball, and Leap objects
totaling 7,249,113,684 bytes. Exclude published MATLAB derivatives because
they remove EOG, use zero-phase preprocessing, and package labels with
features. Retain HEOG/VEOG and signed Leap/ball displacement behind a target
firewall. Metadata observation is complete; payload acquisition is not
authorized.

Evidence:
`docs/IACKD_CUE_ACTION_DISSOCIATION_PRIMARY_SOURCE_RESEARCH.md`,
`registries/iackd_cue_action_dissociation_research.v0.json`, and
`registries/iackd_openneuro_metadata_inventory.v0.json`.

## 0141 - Freeze IACKD-1 Before Any Real Content Operation

Decision: freeze 30 participant-hand units, earlier congruent fit runs, one
held-out incongruent run per unit, a target-blind 30 ms kinematic guard, one
causal 0.5-4 Hz shrinkage-LDA family, direct HEOG/VEOG controls, 300 maximum
fits, exactly 420 prediction sets, one combined target delivery, and one
aggregate score. Route reliable visual alignment to `IACKD-R1` before generic
null so a cue-bound result remains scientifically useful.

Access order: preregistration `e42b799` passed both jobs in CI `31400450392`.
The separate authorization request remains all-false. Its own commit and both
CI jobs must become green before a new packet-bound user decision can be
accepted. The decision commit must then become green before generated-fixture
implementation; the implementation must become green before one 7.25 GB
acquisition; and the prediction freeze must become green before targets open.

Boundary: the user's earlier `continue` and 10 GB allowance are not
retroactive authorization. No IACKD content, dependency, model, target, score,
rerun, release, or claim operation exists from this decision record.

Evidence:
`docs/IACKD_CUE_ACTION_DISSOCIATION_PREREGISTRATION.md`,
`registries/iackd_cue_action_dissociation_contract.v0.json`, and
`docs/IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_PACKET.md`.

## 0142 - Implement IACKD-1 Behind Two Remote-Green Barriers

Decision: after packet-bound decision `1f48b30` passed both jobs in CI
`31403012709`, implement the exact IACKD acquisition, parser, target firewall,
fixed participant-hand models, controls, prediction freezer, and scorer using
only generated run records and mocked transport. Reuse the exact existing
NumPy, SciPy, MNE, and scikit-learn environment without an install or base
dependency change.

Access-order rule: acquisition consumes before metadata or payload access;
analysis consumes before bundle inspection; the model stage never opens or
rehashes sealed final targets; and scoring consumes before any private or
target artifact access. The real acquisition cannot begin until this exact
implementation commit passes both CI jobs. The two opposite target views
cannot open until the later aggregate prediction freeze is remotely green.

Qualification result: one generated 128-run and 2,048-trial roundtrip created
1,568 fit rows and 480 target-free final rows, completed exactly 300 fits and
420 target-blind prediction sets, and exercised all five router outcomes. It
used 8.674020 seconds, 263,618,560-byte peak RSS, and 5,683,285 generated bytes.
All output was removed; every real IACKD, target, network, dependency, and claim
counter remained zero. The synthetic `IACKD-R2` outcome has no claim value.

Evidence: `docs/IACKD_CUE_ACTION_DISSOCIATION_IMPLEMENTATION.md`,
`registries/iackd_cue_action_dissociation_implementation.v0.json`,
`src/neurodecodekit/datasets/iackd_cue_action_acquisition.py`, and
`src/neurodecodekit/experiments/iackd_cue_action_dissociation.py`.

## 0143 - Park IACKD-1 At The Frozen Channel Gate

Decision: preserve the successful one-shot acquisition, but consume and park
the analysis at registered refusal `IACKD-F10` when the first lazy BrainVision
reader does not satisfy the combined exact-36-channel and M1/M2/HEOG/VEOG-name
gate. Do not relax aliases, inspect the channel list after failure, or rerun.

Result: all 1,340 selected objects and 7,249,113,684 bytes passed metadata,
response, streaming SHA-256, promotion, membership, and a second full local
hash pass. Acquisition took 679.749484 seconds at 126,205,952-byte peak RSS.
The failing analysis stopped before `raw.get_data()`, channels TSV, geometry,
events, ball/Leap streams, targets, derivatives, fits, inferences, predictions,
freeze, or score. The actual observed channel count and names were not retained
and remain unavailable. No `IACKD-R0` through `IACKD-R4` route applies.

Disposition: this is a useful integrity-contract failure, not a null neural
result. IACKD-1 has no retry or rerun. Retain the private acquired bundle
without reopening, moving, deleting, uploading, or publishing it. A future
channel-inventory audit requires a new prospective, metadata-minimal Tier C
gate.

Evidence: `docs/IACKD_CUE_ACTION_DISSOCIATION_RESULT.md`,
`registries/iackd_cue_action_dissociation_result.v0.json`, and
`tests/test_iackd_cue_action_dissociation_result.py`.

## 0144 - Measure The IACKD Header Contract Before Another Analysis

Decision: do not guess which half of the consumed IACKD-1 `32+4` gate failed.
Use a new IACKD-H1 metadata lane to audit every public VHDR declaration while
keeping the retained local bundle and all linked content closed.

Basis: the article reports a 32-channel cap and separately names M1, M2, HEOG,
and VEOG, but does not establish an exact 36-channel file invariant. The
authors' pinned public premovement pipeline deletes M1/M2/HEOG/VEOG/TRIGGER if
present, while the execution pipeline deletes HEO/VEO/HEOG/VEOG/TRIGGER.
Count, alias, and run-heterogeneity explanations are therefore plausible but
remain unobserved hypotheses.

Design: select the exact 128 VHDR members and 161,792 bytes already bound by
the committed metadata inventory. Parse them sequentially in memory with the
standard library, resolve no sibling, retain no raw header, and publish only
aggregate signature hashes, counts, and seven public-code alias flags. The
router must preserve contradiction, count-only, name-only, combined, and
heterogeneous outcomes rather than forcing a correction.

Boundary: after this registration is remotely green, generated-fixture and
mocked-transport implementation may proceed under Tier B. Real header network
access remains Tier C and requires a separate packet-bound decision after the
implementation is remotely green. No route reopens or rescues IACKD-1.

Evidence: `docs/IACKD_CHANNEL_INVENTORY_PRIMARY_SOURCE_RESEARCH.md`,
`registries/iackd_channel_inventory_research.v0.json`,
`docs/IACKD_CHANNEL_INVENTORY_PREREGISTRATION.md`, and
`registries/iackd_channel_inventory_contract.v0.json`.

## 0145 - Implement IACKD-H1 Without Rewriting Consumed CLI Evidence

Decision: after registration `0e52278` passed both jobs in CI `31412667060`,
implement the header audit under Tier B using generated VHDR bodies and mocked
transport only. Expose it through a module CLI instead of changing the central
`src/neurodecodekit/cli.py`, whose exact bytes remain bound by the consumed
IACKD-1 implementation record.

Design: require strict standard-library parsing, inert sibling basenames,
status/URL/length/ETag/encoding response identity, one body hash and one parse,
aggregate-only signatures, all six frozen routes, atomic exclusive output,
one-thread resources, and a future real executor that cannot pass without a
new exact decision file and green evidence.

Qualification: 24 focused tests pass. One isolated generated roundtrip covered
all 128 registered sizes and 161,792 bytes in 0.037818958 seconds at
36,634,624-byte peak RSS, producing a 4,465-byte ledger. Every network,
real-header, local-bundle, sibling, sample, event, trajectory, target, model,
prediction, scoring, provider, device, and claim counter remained zero.

Boundary: the synthetic `IACKDH-R1` route is fixture mechanics only. Commit,
push, and obtain both green CI jobs for the exact implementation before
preparing one separate Tier C request. No prior continuation authorizes that
future real-header pass.

Evidence: `docs/IACKD_CHANNEL_INVENTORY_IMPLEMENTATION.md`,
`registries/iackd_channel_inventory_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_header_inventory.py`, and
`tests/test_iackd_header_inventory.py`.

## 0146 - Request One Public IACKD Header Audit After Green Implementation

Decision: after exact implementation `16621cc` passed Base Python job
`93542494819` and Optional Neuro Readers job `93542494839` in CI
`31415213841`, prepare one all-false Tier C request for the smallest useful
real-content follow-up. Do not treat the request itself or any earlier
maintainer continuation as authorization.

Requested scope: one sequential HTTPS request for each of the 128 exact public
VHDR objects already in the committed OpenNeuro inventory, totaling 161,792
expected body bytes. Validate exact response identity, hash and strictly parse
each body once in memory, discard it before the next request, and emit one
aggregate-only compatibility ledger. Retain zero raw body, path, unallowlisted
name, participant outcome, sibling, sample, event, trajectory, target, model,
prediction, or score.

Boundary: the request must first be committed, pushed, and remotely green.
Codex must then identify that exact commit, CI, and sole scope before a fresh
unambiguous maintainer `continue`, `approve`, or `proceed` can bind it by
reference in a separate decision record quoting the maintainer's actual words.
Only after that decision commit is remotely green may the one no-retry,
no-rerun header audit start. Every possible route remains an engineering file-
contract diagnosis, never a scientific or decoding result.

Evidence: `docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_PACKET.md`,
`registries/iackd_channel_inventory_authorization_request.v0.json`, and
`tests/test_iackd_header_inventory_authorization_request.py`.

## 0147 - Bind The Fresh Maintainer Continue To IACKD-H1 Only

Decision: accept the maintainer's fresh post-packet instruction as the short-
form decision for the sole active IACKD-H1 Tier C packet. Preserve the complete
actual message verbatim and do not fabricate the packet's long scope as a user
utterance.

Basis: request `56531c6` passed Base Python job `93546632359` and Optional
Neuro Readers job `93546632280` in CI `31416489006`. Codex then identified the
packet, commit, CI, sole 128-header/161,792-byte scope, and need for a new
decision before the maintainer unambiguously said `continue`.

Boundary: this record authorizes exactly one future sequential public VHDR
audit under the frozen caps, no-retry/no-rerun rule, aggregate-only output, and
zero local-bundle or sibling access. It is ineffective until its own commit is
pushed and both CI jobs are green. No real header, local path, signal, event,
trajectory, target, model, score, provider, hardware, release, or claim action
occurs while recording it.

Evidence: `docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_DECISION.md`,
`registries/iackd_channel_inventory_authorization_decision.v0.json`, and
`tests/test_iackd_header_inventory_authorization_decision.py`.

## 0148 - Close IACKD-H1 At Two Header Signatures

Decision: accept the sole public-header audit as complete and consumed at
`IACKDH-R5`. Replace the disproven exact-36 global declaration assumption with
the measured two-signature compatibility fact; do not reopen, rerun, or amend
the result.

Result: all eleven gates passed over 128 public VHDR bodies and 161,792 bytes.
Ninety-six declarations contain 29 channels without M1/M2, and 32 contain 31
channels with M1/M2. Every declaration contains HEOG, VEOG, and TRIGGER and
reports 1024 Hz. Runtime was 23.576352333 seconds, peak RSS was 94,650,368
bytes, and retained generated output was 5,759 bytes. The declared totals are
not established EEG-channel counts.

Boundary: retained-bundle, sibling, sample, event, trajectory, target, feature,
model, prediction, and score operations remained zero. This is a complete
engineering diagnosis and no neural result. A future cue-versus-action study
must prospectively freeze a count-agnostic, presence-based role policy and
treat M1/M2 availability as a run property before a new exact Tier C decision.

Evidence: `docs/IACKD_CHANNEL_INVENTORY_RESULT.md`,
`registries/iackd_channel_inventory_result.v0.json`, and
`tests/test_iackd_header_inventory_result.py`.

## 0149 - Measure Roles Before Rebuilding IACKD And Require Dual Reversal

Decision: do not repair the consumed IACKD-1 reader by replacing its exact-36
check. First measure the source-declared BIDS roles and geometry in a separate
IACKD-H2 lane, then use that aggregate result to define a new role-map hash and
a separately preregistered IACKD-2 experiment.

Basis: H1 measured 29-channel and 31-channel declarations, all with HEOG,
VEOG, and TRIGGER and only the latter group with M1/M2. The target-free source
audit found that the consumed reader would also classify TRIGGER as EEG,
expects 32/34 BIDS EEG rows, and validates a synthetic source without a
trigger. BIDS makes channel role explicit and does not require channel and
electrode tables to have equal membership; MNE's default type inference is not
a substitute for that contract.

Design: H2 covers exactly 316 committed public metadata objects and 457,602
bytes without using the retained bundle. The future IACKD-2 design requires
both congruent-to-incongruent and incongruent-to-congruent arms. Each arm's
frozen prediction is scored against actual hand direction and the exact-
opposite cue surrogate induced by its fit mapping. The weaker participant-level
arm margin is the prospective primary statistic.

Boundary: this Tier A record authorizes no H2 body, retained path, sibling,
sample, event, trajectory, target, model, prediction, or score. H2 and IACKD-2
each retain their own prospective and Tier C sequence.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md`,
`registries/iackd_role_aware_dual_reversal_research.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_research.py`.

## 0150 - Freeze IACKD-H2 Role And Geometry Audit

Decision: freeze the smallest public metadata audit that can replace the
disproven global channel count with a source-declared sensor-role contract.
Select exactly 128 channel tables, 128 EEG sidecars, 30 electrode tables, and
30 coordinate-system files from the committed OpenNeuro inventory: 316 objects
and 457,602 expected bytes. Do not use or inspect the retained local bundle.

Contract: parse BIDS channel roles strictly, exclude TRIGGER and recorded EOG
controls from predictive EEG, treat M1/M2 as optional source-declared
properties, preserve unavailable reference and geometry fields, and compare
the ordered core schema after removing only exact M1/M2. Publish only aggregate
schemas, counts, coverage, hashes, warnings, measures, and one ordered
`IACKDR-R0` through `IACKDR-R4` route. Occipital coverage is reported but
cannot rescue the central C3/C4/Cz geometry gate.

Sequence: this exact registration must first be committed, pushed, and pass
both CI jobs. Only then may Tier B generated-fixture parsers, mocked transport,
resource guards, writer, inspector, and module CLI be implemented. A separate
all-false packet, fresh packet-bound maintainer decision, and green decision
commit remain mandatory before one no-retry, no-rerun public-body audit.

Boundary: no H2 body, local IACKD path, sibling, signal, marker, event,
trajectory, target, feature, model, prediction, score, provider, hardware,
release, or claim operation is authorized by this registration. H2 is an
engineering compatibility gate and cannot establish a neural effect.

Evidence: `docs/IACKD_CHANNEL_ROLE_GEOMETRY_PREREGISTRATION.md`,
`registries/iackd_channel_role_geometry_contract.v0.json`, and
`tests/test_iackd_channel_role_geometry_contract.py`.

## 0151 - Implement IACKD-H2 As An Aggregate Role Audit

Decision: after registration `228ccd0` passed both required jobs in CI
`31427931578`, implement H2 under Tier B using only generated exact-size BIDS
metadata and mocked responses. Keep the consumed IACKD-1 reader unchanged and
preserve zero real metadata, local-bundle, sibling, signal, target, model, and
score operations.

Implementation: add one standard-library module with strict UTF-8, TSV, JSON,
channel-role, sidecar-count, sampling, electrode, coordinate-system, response,
resource, output, and one-shot decision boundaries. Pair channel/sidecar runs
and electrode/coordinate groups using private keys, then publish only grouped
schemas, aggregate status, allowlisted sidecar groups, one role-map hash,
aggregate geometry, H1 reconciliation, measures, and routes R0-R4.

Qualification: one final generated traversal processed all 316 registered
sizes and 457,602 bytes, performed 316 hashes and 316 semantic parses, and
emitted 8,282 bytes in 0.054679625 seconds at 34,996,224-byte peak RSS. It
routed constructed `IACKDR-R4` with one core schema and 30 complete fixture
geometry groups. Forty-seven focused, 1,751 base, and 1,822 optional tests pass
locally.

Boundary: the synthetic route has no real-source or scientific meaning. The
exact implementation must be committed, pushed, and pass both CI jobs before
one all-false Tier C packet may be prepared. No earlier maintainer message
authorizes a public metadata request, retained-bundle operation, or IACKD-2
experiment.

Evidence: `docs/IACKD_CHANNEL_ROLE_GEOMETRY_IMPLEMENTATION.md`,
`registries/iackd_channel_role_geometry_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_channel_roles.py`, and
`tests/test_iackd_channel_roles.py`.

## 0152 - Request One Public IACKD Role And Geometry Audit

Decision: after exact implementation `9f6fef9` passed both required jobs in CI
`31430151368`, prepare one all-false Tier C request for the smallest observation
that can freeze a count-agnostic sensor-role map. Do not treat the packet or an
earlier maintainer continuation as authorization.

Requested scope: exactly 316 already inventoried OpenNeuro bodies totaling
457,602 bytes: 128 channel tables, 128 EEG sidecars, 30 electrode tables, and
30 coordinate-system files. Request them sequentially, validate exact response
identity, hash and parse each once in memory, discard each before the next,
pair only through private keys, and emit one aggregate compatibility ledger.

Boundary: retain zero raw body, path, participant, per-run row, coordinate,
free text, signal, event, trajectory, target, feature, model, prediction, or
score. The retained bundle, VHDR/VMRK/EEG, every unregistered object, IACKD-2,
dependencies, providers, hardware, retries, reruns, releases, and claim
upgrades remain unauthorized.

Sequence: the request must first be committed, pushed, and both CI jobs must
pass. Codex must then identify that exact commit, CI, sole scope, and gate
before a fresh unambiguous maintainer `continue`, `approve`, or `proceed` may
bind it by reference in a separate decision quoting the actual words. Only a
green decision commit can open the one execution.

Evidence: `docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_PACKET.md`,
`registries/iackd_channel_role_geometry_authorization_request.v0.json`, and
`tests/test_iackd_channel_role_geometry_authorization_request.py`.

## 0153 - Bind The Fresh Maintainer Continuation To IACKD-H2

Decision: record the maintainer's exact words `continue :)` as a short-form
authorization for the sole remotely green IACKD-H2 packet. Do not fabricate
the packet recital as maintainer language and do not expand its scope.

Basis: request `86174bc86123bc010bac2f40a9d72147dc8aef05` passed Base Python
job `93594327147` and Optional Neuro Readers job `93594327069` in CI
`31431064259`. Codex then identified the packet, proof, exact 316-body and
457,602-byte scope, and need for fresh words before the maintainer continued.

Authorized after this decision is remotely green: one sequential public
metadata audit, one hash and semantic parse per registered body, one private
consumed marker, and one aggregate ledger under the frozen 180-second, 256 MiB
RSS, 2 MiB network-body, 4 MiB disk, 2 MiB output, and zero-retry/rerun caps.

Boundary: local IACKD files, VHDR/VMRK/EEG, signals, events, trajectories,
targets, labels, derivatives, models, training, inference, scoring, additional
objects, providers, hardware, releases, and claim upgrades remain forbidden.
This record is ineffective until its exact commit is pushed and both CI jobs
pass.

Evidence: `docs/IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_DECISION.md`,
`registries/iackd_channel_role_geometry_authorization_decision.v0.json`, and
`tests/test_iackd_channel_role_geometry_authorization_decision.py`.

## 0154 - Consume H2 At The Frozen Control-Taxonomy Mismatch

Decision: preserve the completed execution and route `IACKDR-R1` without a
retry, rerun, parser change, router change, or role-map approval.

Evidence: decision `f6eb5ab650a0232a17d2f8f56c582c90bf0cf420` passed both
jobs in CI `31444154297` before one 316-request/457,602-byte execution. Every
response, hash, parse, resource, privacy, output, and aggregate replay gate
passed. Runtime was 55.592999708 seconds at 86,769,664-byte peak RSS.

Diagnosis: all 128 tables share one 26-channel predictive EEG core after
optional M1/M2 removal; sampling is 1024 Hz; reference is average; and all 30
geometry groups cover finite central and occipital sensors. The frozen contract
still fails because HEOG, VEOG, and Trigger are source-typed `MISC`: its EOG
predicate rejects the first two, and its trigger-separated count disagrees
with sidecars that report all three as MISC.

Interpretation: this is a prospective role-taxonomy error, not evidence that
the source is malformed. The candidate role-map hash is inadmissible under R1.
A separately named source-type-first policy may be designed from the aggregate
result, but it must be frozen before any signal or scientific outcome access.

Evidence: `docs/IACKD_CHANNEL_ROLE_GEOMETRY_RESULT.md`,
`registries/iackd_channel_role_geometry_result.v0.json`, and
`tests/test_iackd_channel_role_geometry_result.py`.

## 0155 - Separate Source Type From Functional Sensor Role

Decision: create a new artifact-only `IACKD-H3` policy instead of amending the
consumed H2 parser or router. Reconcile BIDS counts from exact source types
first; only then assign functional roles and model-inclusion masks.

Basis: the dataset pins BIDS 1.7.0; the H2 aggregate reports 26/28 EEG plus
three MISC rows; controls can be functional while remaining source-typed MISC;
M1/M2 are optional and nonpredictive; and the fixed 26-channel EEG core is the
only prospective predictive set.

Policy hash:
`1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`.

Boundary: do not amend H2, approve its old candidate hash, read source or local
data, implement a real reader, or enter IACKD-2. One generated-fixture Tier B
qualification may follow only after this research commit is remotely green.

Evidence: `docs/IACKD_SOURCE_DECLARED_CONTROL_POLICY_RESEARCH.md`,
`registries/iackd_source_declared_control_policy_research.v0.json`, and
`tests/test_iackd_source_declared_control_policy_research.py`.

## 0156 - Qualify H3 On Generated Metadata Before Any Reader

Decision: implement the H3 policy as a dependency-free generated-fixture
validator with no real-data executor. Hold one measured closeout until this
exact implementation is committed, pushed, and both CI jobs pass.

Basis: research `ed5ce82` passed both jobs in CI `31445790741`. The H2
aggregate did not publish an exact real source order, so generated source-order
hashes qualify binding mechanics only and cannot be represented as observed
source evidence.

Interface: validate 29-row and 31-row target-free signatures, preserve exact
source counts before assigning roles, keep one 26-channel predictive output
order, emit five separate derivative hashes, replay deterministically, reject
target fields, and exercise at least twelve distinct refusal classes. Expose
only plan, generated-fixture, and inspect module CLI modes.

Boundary: no public or local IACKD body, retained bundle, real reader, signal,
event, trajectory, target, derivative, model, prediction, score, provider,
hardware, release, IACKD-2 entry, or claim upgrade. A green implementation may
open only one measured generated closeout under the registered caps.

Evidence: `docs/IACKD_SOURCE_SEMANTICS_IMPLEMENTATION.md`,
`registries/iackd_source_semantics_implementation.v0.json`,
`src/neurodecodekit/preprocess/iackd_source_semantics.py`, and
`tests/test_iackd_source_semantics.py`.

## 0157 - Close H3 As Generated Policy Mechanics

Decision: accept the one measured generated qualification after exact
implementation `8c5784a` passed both jobs in CI `31446902756`. Close H3 as an
engineering mechanics result without promoting a real-reader or scientific
claim.

Preflight: one symbolic-link output parent refused at `IACKDS-F14` before a
policy read, fixture build, semantic pass, or output. One qualification then
completed; there was no retry or rerun after fixture access.

Result: both 29/31-row groups, one 26-channel predictive core, five derivative
hashes, deterministic replay, target firewall, 13 mutations spanning 12
refusal classes, all forbidden counters, resources, and output passed. Runtime
was 0.007473916979506612 seconds at 20,250,624-byte peak RSS over 6,093 input
and 6,834 output bytes.

Boundary: generated order hashes are mechanics evidence only. H2 remains
`IACKDR-R1`; its candidate hash remains inadmissible. No real reader, public or
local payload, signal, event, trajectory, target, derivative, model, score,
IACKD-2 execution, or scientific claim is opened. Any next evidence-bearing
experiment needs a separately named prospective contract and Tier C decision.

Evidence: `docs/IACKD_SOURCE_SEMANTICS_RESULT.md`,
`registries/iackd_source_semantics_result.v0.json`, and
`tests/test_iackd_source_semantics_result.py`.

## 0158 - Freeze IACKD-2 As A Symmetric, Storage-Safe Dual Reversal

Decision: preregister two disjoint mapping-transfer arms rather than repair or
rerun IACKD-1. `C2I` fits congruent and predicts held-out incongruent rows;
`I2C` fits incongruent and predicts held-out congruent rows. Both must favor
action over the exact cue-derived opposite, and the weaker participant arm
margin is primary.

Sensor basis: bind H3 policy
`1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`,
the fixed 26-channel predictive core, source-typed MISC ocular/trigger controls,
optional nonpredictive M1/M2, 1024 Hz, average reference, and complete central
and occipital views. MNE inference cannot replace source declarations.

Evidence matrix: one fixed causal 0.5-4 Hz shrinkage-LDA family, 11 fits and 15
prediction sets per arm and participant-hand unit, 660 exact fits, 900 exact
prediction sets, participant-level sign flips, registered peripheral, visual,
timing, displacement, permutation, derangement, hand-swap, and physiology
controls, one green hash-only freeze, one target delivery, and one score.

Storage decision: never reopen the consumed local bundle. A future separately
authorized sequence must stream the exact 1,340 public objects once, process
one ten-object run group at a time, retain no second raw bundle, remain under
1 GiB incremental disk, and require 10 GiB free disk. The committed inventory
measures the largest run group at 82,064,564 bytes.

Boundary: this is registration only. Tier B generated-fixture implementation
is conditional on the registration becoming remotely green. Public payload,
local path, real reader, signal, event, trajectory, target, training,
prediction, freeze, score, cleanup, rerun, and claim upgrade remain
unauthorized until their later exact gates.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_PREREGISTRATION.md`,
`registries/iackd_role_aware_dual_reversal_contract.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_contract.py`.

## 0159 - Separate IACKD-2 Model Inputs From Generated Scorer Targets

Decision: implement the remotely green IACKD-2 registration only on generated
BrainVision fixtures, generated arrays, and mocked transport. Give the model
stage a strict object containing fit labels and target-free final features;
place generated final action and cue views in a separate scorer-stage object.

Basis: registration `5bdab30` passed both jobs in CI `31448911258`. Merely
avoiding a sealed-target key inside model code is weaker than preventing the
model function from receiving the target-bearing container at all. The scorer
must therefore recompute all 900 prediction-set hashes, the canonical private
hash, split identity, and final-item binding before it may inspect generated
target views.

Qualification: use generated 29/31-row source declarations, causal future-tail
checks, exact 4,096/3,136/960 row inventories, 660 fits, 900 target-blind
prediction sets, one exact replay, all six routes, and strict malformed-input
refusals. A disposable development roundtrip may debug the interface, but the
one registered generated closeout remains held until the exact implementation
commit is pushed and both CI jobs pass.

Boundary: constructed `IACKD2-R5` has no scientific value. Do not access a
public payload, the old retained bundle, signal, event, trajectory, real target,
real model, prediction, or score. Any real sequence still requires a separate
all-false packet, fresh Tier C decision, green implementation, green freeze,
and one target delivery.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_IMPLEMENTATION.md`,
`registries/iackd_role_aware_dual_reversal_implementation.v0.json`,
`src/neurodecodekit/experiments/iackd_role_aware_dual_reversal.py`, and
`tests/test_iackd_role_aware_dual_reversal.py`.

## 0160 - Close IACKD-2 Generated Mechanics Without A Scientific Upgrade

Decision: accept the one registered generated closeout as deterministic
interface-mechanics evidence and consume its no-rerun gate. The first
implementation push `25a5692` failed only a nonportable test path and did not
open the closeout. Correction `af7488a` passed both jobs in CI `31451262840`
before the sole qualification ran.

Result: all 15 gates passed in 5.024801375111565 seconds at 257,130,496-byte
peak RSS with 30,170 output bytes. The 660-fit/900-prediction matrix replayed
exactly, the model/scorer target firewall and freeze checks held, all six
routes were reachable, and every forbidden counter remained zero. The
temporary report was inspected and removed.

Boundary: constructed `IACKD2-R5`, balanced accuracies, margins, and generated
sign-flip value are planted fixture properties with zero scientific meaning.
Do not rerun or tune this closeout, access public or retained IACKD data, or
promote a neural claim. Any real sequence requires a separate all-false Tier C
request, fresh packet-bound decision, and later green implementation and
prediction-freeze gates.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_SYNTHETIC_RESULT.md`,
`registries/iackd_role_aware_dual_reversal_synthetic_result.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_synthetic_result.py`.

## 0161 - Request One Storage-Safe Real IACKD-2 Dual Reversal

Decision: prepare an all-false Tier C request for the frozen real IACKD-2
sequence. The request itself authorizes no implementation, environment use,
public or local content operation, model execution, target delivery, score,
cleanup, release, or claim change.

Scope requested after a fresh green decision: qualify one separate real
executor on generated fixtures; stream exactly 1,340 public objects and
7,249,113,684 payload bytes in 128 one-at-a-time run groups; promote bounded
private derivatives; complete 660 fits and 900 target-blind prediction sets;
commit and remotely green one aggregate freeze; then deliver and score the two
final target views once.

Resource decision: use one thread, one worker, and one numerical job. Keep
peak incremental disk at or below 1 GiB, require 10 GiB free, keep private
derivatives and generated outputs at or below 512 MiB each, and permit zero
retry, rerun, second delivery, second score, or post-target update. The old
retained IACKD bundle and every preexisting path remain forbidden.

Sequence: this request must first be committed, pushed, and pass both CI jobs.
Codex must then identify the exact commit, CI, sole scope, and boundary. Only a
fresh later maintainer `continue`, `approve`, or `proceed` may bind it by
reference in a separate decision quoting the actual words. The current message
cannot be used retroactively.

Boundary: even future `IACKD2-R5` would establish only within-IACKD
pre-movement action-direction information surviving symmetric cue reversals
and registered controls with motor-compatible central support. It would not
prove brain-specific origin, external replication, thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_PACKET.md`,
`registries/iackd_role_aware_dual_reversal_authorization_request.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_authorization_request.py`.

## 0162 - Accept The Fresh Packet-Bound IACKD-2 Continuation

Decision: bind the maintainer's actual fresh message, `continue`, to the sole
green IACKD-2 request without inventing a long-form utterance or expanding the
registered scope. Request `862141f` passed both jobs in CI `31454131606` before
the response. Decision `2ce87fa` then passed both jobs in CI `31456317734`
before implementation.

Boundary: the decision opens only the packet's ordered sequence. The real
executor must first qualify on generated fixtures and become remotely green.
The public stream may then run once; the target-blind analysis may run once
after complete derivatives; final targets may open only after the aggregate
freeze is committed, pushed, and remotely green. The old bundle, retries,
reruns, post-target updates, additional models/data, hardware, release, and
claim expansion remain forbidden.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_DECISION.md`,
`registries/iackd_role_aware_dual_reversal_authorization_decision.v0.json`,
and its invariant test.

## 0163 - Require Green Exact Proof For The IACKD-2 Real Executor

Decision: accept the generated qualification as implementation evidence only
and require the exact implementation commit plus both CI jobs to become green
before the first public metadata or payload request.

Basis: the distinct executor passed all 15 generated gates, including exact
660-fit/900-prediction execution, deterministic replay, structural target
isolation, aggregate freeze, isolated scorer, source-semantics variants,
geometry handling, storage accounting, and strict refusals. Runtime was
5.60445004189387 seconds, peak RSS was 270,745,600 bytes, retained output was
4,523 bytes, and every real/public/old-bundle operation counter was zero.

Sequence: after green implementation, run exactly one fresh 1,340-object
stream and commit its aggregate receipt. Then run the target-blind analysis
once and commit its aggregate freeze. Only after the freeze commit and both CI
jobs are green may the same sealed target rows be delivered together and
scored once. Stop after any consumed-stage failure; no retry or rerun exists.

Boundary: generated `IACKD2-R5` is planted mechanics and has zero scientific
value. No neural effect, action decoding, brain-specific origin, unseen-person
generalization, language or thought decoding, real-time, hardware, assistive,
home-use, or clinical result has been established.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md`,
`registries/iackd_role_aware_dual_reversal_real_implementation.v0.json`,
`src/neurodecodekit/experiments/iackd_role_aware_dual_reversal_real.py`, and
the two matching test modules.

## 0164 - Consume IACKD-2 At The First Metadata Transport Failure

Decision: classify the sole public stream as consumed and parked at
`IACKD2-F08`. Exact implementation `dab5dd4` passed both jobs in CI
`31461818620` before launch. The first response passed status and final URL but
failed the frozen exact `Content-Length` check for 1,178 bytes.

Evidence boundary: the actual header value was not retained, the response body
was not read or hashed, and no second metadata response or selected object was
requested. There were zero signal, trajectory, target, derivative, model,
prediction, freeze, target-delivery, scoring, post-target, old-bundle,
provider, hardware, release, and claim operations.

Consequence: do not rerun, retry, resume, restart, delete or rename the consumed
marker, probe the same URL, alter the expected byte count, or continue into
analysis or score. Conditional downstream permissions are unreachable because
no complete derivative exists.

Future design: a separately named prospective lane may make bounded observed
body length and SHA-256 authoritative for metadata content while recording
`Content-Length` as transport metadata. It still requires a new registration,
implementation proof, Tier C decision, and invocation identity. This decision
does not authorize it.

Evidence: `docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_STREAM_RESULT.md`,
`registries/iackd_role_aware_dual_reversal_stream_failure_result.v0.json`, and
`tests/test_iackd_role_aware_dual_reversal_stream_failure_result.py`.

## 0165 - Treat Small Metadata Framing As Transport Evidence

Decision: in the prospective IACKD-T1 lane, do not use `Content-Length` as the
cryptographic identity of a small metadata body. Permit one unambiguous HTTP
framing profile, read at most the registered size plus one byte, and require
the exact observed byte count and registered SHA-256 before semantic parsing.

Reason: RFC 9112 permits fixed-length, chunked, and close-delimited response
bodies. The consumed IACKD-2 stop observed only a failed header gate and read
no body, so this correction is prospective and outcome-free.

Boundary: large selected objects retain exact length and ETag plus observed
bytes and full-stream SHA-256. No scientific design field changes, and no
public request or real execution is authorized by this decision record.

Evidence: `docs/IACKD_TRANSPORT_STABLE_RECOVERY_RESEARCH.md`,
`registries/iackd_transport_stable_recovery_research.v0.json`,
`docs/IACKD_TRANSPORT_STABLE_RECOVERY_PREREGISTRATION.md`, and
`registries/iackd_transport_stable_recovery_contract.v0.json`.

## 0166 - Keep The Transport Validator Incapable Of Real Access

Decision: implement IACKD-T1 as a standalone standard-library validator with
generated response objects, no URL opener, no local IACKD path, and no
`--execute` CLI mode.

Reason: the registration can qualify framing, body caps, hashing, ordering,
payload strictness, replay, and aggregate outputs without making public access
possible before a separate Tier C decision.

Boundary: the generated closeout has no scientific value. A future real
executor must be separately integrated only after an exact all-false packet,
fresh packet-bound decision, and remotely green decision commit.

Evidence: `docs/IACKD_TRANSPORT_STABLE_RECOVERY_IMPLEMENTATION.md`,
`registries/iackd_transport_stable_recovery_implementation.v0.json`,
`src/neurodecodekit/datasets/iackd_transport_stable.py`, and its tests.

## 0167 - Separate IACKD-2R From The Consumed Invocation

Decision: request one separately named IACKD-2R sequence instead of amending,
reopening, or rerunning consumed IACKD-2. The future executor must be additive,
use a new invocation identity and root, and inherit every scientific field
unchanged. The only semantic correction is the four-body metadata framing
policy qualified by IACKD-T1.

Order: the all-false request must first be committed, pushed, and pass both CI
jobs. A fresh packet-bound decision must then become remotely green before
generated/mock-only executor integration. That exact executor must become
remotely green before one public stream. One target-blind prediction freeze
must become remotely green before the sole target delivery and score.

Machine boundary: refuse before writing the new consumed marker unless at
least 10 GiB is free, all numerical execution is single-threaded, and one-
minute system load is no greater than one runnable process per logical CPU.
This strengthens execution safety and changes no scientific field.

Evidence boundary: this decision record and packet are all false. The current
maintainer `continue` preceded the immutable packet and is not retroactive. No
public body, local IACKD path, EEG, event, trajectory, target, model,
prediction, freeze, score, retry, rerun, release, or claim operation is open.

Evidence: `docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/iackd_transport_stable_recovery_authorization_request.v0.json`,
and `tests/test_iackd_transport_stable_recovery_authorization_request.py`.

## 0168 - Bind The Fresh Maintainer Continue To IACKD-2R

Decision: preserve the maintainer's exact word `continue` as a short-form
packet-bound Tier C decision for the sole active IACKD-2R request at
`525e97e`, green in both jobs under CI `31475356506`.

Reason: Codex identified the immutable packet, commit, CI proof, exact scope,
machine-safety boundary, and fresh-decision gate immediately before the
maintainer's unambiguous instruction. The approved charter permits this
short-form reference when one green packet is active.

Boundary: do not claim that the maintainer typed the packet's long recital,
and infer no expansion. This decision is ineffective until its own commit and
both CI jobs are green. Only generated/mock-only additive executor work opens
then; public access waits for a second green implementation gate. Release,
hardware, destructive work, scientific claim upgrades, retries, reruns, and
operations on old roots or other projects remain forbidden.

Evidence: `docs/IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/iackd_transport_stable_recovery_authorization_decision.v0.json`,
and `tests/test_iackd_transport_stable_recovery_authorization_decision.py`.

## 0169 - Isolate IACKD-2R And Gate Consumption On Machine State

Decision: implement IACKD-2R as one self-contained additive executor. Do not
import, call, modify, or expose an interface to the consumed IACKD-2 executor.
Use a new private root and new receipt, freeze, and result identities.

Transport decision: pass the four small metadata response streams through the
remotely green IACKD-T1 validator after independently checking their real
status and final URL. Accept fixed-length, valid chunked, and clean close-
delimited framing only when one bounded read yields the exact registered byte
count and SHA-256 before parsing. Preserve strict fixed-length, ETag, byte, and
full-stream SHA-256 checks for all 1,340 payload objects.

Machine decision: validate exact green implementation evidence before the
real mode can open a URL. Then measure one-thread configuration, free disk,
logical CPU count, and one-minute load before invoking the streaming builder.
Refuse before the consumed marker below 10 GiB free, above load/logical CPU
`1.0`, or when a load metric is unavailable.

Reason: this fixes the observed transport assumption without changing the
frozen scientific design and makes the user's computer state an explicit
pre-consumption condition. Keeping the old executor immutable prevents an
accidental rerun of consumed evidence.

Evidence boundary: one generated qualification passed 18/18 gates with all
three framing profiles, deterministic 660-fit/900-prediction replay, 13
mutations, 4.939357 seconds runtime, 261,488,640-byte peak RSS, and zero real,
public, network, target, or claim operations. It is engineering evidence only.

Evidence: `docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md`,
`registries/iackd_transport_stable_dual_reversal_real_implementation.v0.json`,
`src/neurodecodekit/experiments/iackd_transport_stable_dual_reversal_real.py`,
and `tests/test_iackd_transport_stable_dual_reversal_real.py`.

## 0170 - Park IACKD-2R On Pinned Metadata Content Drift

Decision: consume and park IACKD-2R at `IACKD2R-F05` after the sole invocation
passed its machine gate but the first 1,178-byte metadata body failed the
registered SHA-256 before semantic parsing.

Reason: the transport correction deliberately makes observed body bytes and
SHA-256 authoritative. A matching byte count cannot rescue a changed digest,
and parsing changed content would violate the frozen identity contract. The
validator therefore produced the correct fail-closed result.

Boundary: do not retry, rerun, resume, re-request, hash, or parse the changed
body; do not alter the consumed marker or amend the expected identity after the
fact. No selected object, EEG, event, trajectory, target, derivative, model,
prediction, freeze, delivery, or score was reached. Downstream IACKD-2R stages
are unreachable.

Next research option: only a separately named prospective metadata-version
reverification lane may determine what changed and freeze a fresh public
identity. It requires its own Tier C gate and cannot upgrade a scientific claim
from this failure.

Evidence: `docs/IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_STREAM_RESULT.md`,
`registries/iackd_transport_stable_dual_reversal_stream_failure_result.v0.json`,
and `tests/test_iackd_transport_stable_dual_reversal_stream_failure_result.py`.

## 0171 - Bind Future IACKD Access To A Versioned Snapshot Tree

Decision: use a named OpenNeuro snapshot commit and its recursive
content-addressed file tree as the primary identity for any future IACKD lane.
Do not use the raw bytes, ETag, last-modified value, or `Content-Length` of one
unversioned root metadata response as a substitute for snapshot identity.

Reason: IACKD-2R observed an exact 1,178-byte response with a changed SHA-256,
but its frozen order correctly prevented parsing. OpenNeuro's official API and
pinned platform source expose a stronger prospective anchor: snapshot
`hexsha`, full-path file IDs, sizes, annexed status, and S3 `versionId` URLs.
Those fields identify the intended version without depending on JSON field
order or HTTP framing.

Compatibility boundary: separately gate the snapshot anchor, recursive tree,
historical 1,340-object/7,249,113,684-byte selection, and the critical Name,
BIDS version, CC0 license, and DOI projection. Snapshot, tree, selected
inventory, or critical-field drift always parks. Noncritical descriptive drift
may be recorded only after every identity and compatibility gate passes.

Execution boundary: this is Tier A research only. No dataset-specific GraphQL
response, S3 body, local IACKD path, EEG, target, model, score, retry, rerun, or
claim operation is authorized. The smallest next real gate is one separately
authorized, one-response, 2 MiB metadata audit after a green generated-only
validator.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_RECOVERY_RESEARCH.md`,
`registries/iackd_snapshot_identity_recovery_research.v0.json`, and
`tests/test_iackd_snapshot_identity_recovery_research.py`.

## 0172 - Freeze One Exact Snapshot Identity Query Before Implementation

Decision: register one exact GraphQL query over snapshot `ds006840:1.0.0` and
permit only a generated-response canonicalizer after the registration commit
passes both CI jobs. The query selects snapshot ID, tag, `hexsha`, five narrow
description fields, and recursive file ID/path/size/annexed/URL fields.

Canonicalization: require exactly 1,679 safe, unique, version-scoped file rows;
derive the exact 1,340-object/7,249,113,684-byte acquisition selection; and
hash snapshot, full tree, selected manifest, and critical metadata separately.
The private selected manifest may exist only in a bounded Git-ignored future
execution root. Public output contains aggregate hashes and counts, never
individual paths, URLs, or S3 version IDs.

Boundary: the generated implementation must expose no URL opener, socket, HTTP
client, real endpoint, execute mode, or local IACKD path. A public GraphQL
request remains Tier C and requires a later all-false packet, fresh decision,
green real wrapper, and one no-retry invocation. The current `continue` is not
retroactive.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_PREREGISTRATION.md`,
`registries/iackd_snapshot_identity_contract.v0.json`, and
`tests/test_iackd_snapshot_identity_contract.py`.

## 0173 - Keep Snapshot Identity Canonicalization Generated And Layered

Decision: implement IACKD-M1 as a standard-library generated-response
canonicalizer with four independent identities: snapshot anchor, recursive
tree, selected acquisition manifest, and critical metadata. Do not add a
network client, real endpoint, execute mode, local IACKD path, or integration
with either consumed executor.

Privacy decision: keep all 1,340 individual selected paths, object IDs, S3
keys, and version IDs in a bounded private manifest. Publish only aggregate
counts, role summaries, and canonical hashes. Reject any row-level path, URL,
or version-ID leakage from the public report.

Qualification decision: require exact historical selected-path compatibility,
two canonical replays, all 37 registered refusals, exclusive atomic output,
one-thread controls, and the frozen time/RSS/input/output caps. The final
generated route `IACKDM-R1` passed those gates in 0.8887734590098262 seconds at
38,436,864-byte peak RSS with 531,067 input and 426,792 output bytes.

Boundary: this is engineering evidence only. After the exact implementation is
committed, pushed, and both CI jobs are green, the next allowed artifact is an
all-false Tier C request. A public GraphQL response still requires a fresh
packet-bound decision and a separately green wrapper; metadata success would
not authorize an EEG payload or scientific claim.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_IMPLEMENTATION.md`,
`registries/iackd_snapshot_identity_implementation.v0.json`,
`src/neurodecodekit/datasets/iackd_snapshot_identity.py`, and
`tests/test_iackd_snapshot_identity.py`.

## 0174 - Request One Public Snapshot Audit Without Payload Access

Decision: prepare an all-false IACKD-M1A packet for one future public metadata
audit. Bind one exact 355-byte GraphQL POST and one response capped at 2 MiB.
Keep S3 payload requests, local IACKD paths, consumed roots, neural data,
targets, derivatives, models, predictions, scores, retries, reruns, releases,
and claim upgrades outside the packet.

Ordering decision: a fresh packet-bound decision must become remotely green
before generated/mock transport-wrapper implementation. That exact wrapper
must then become remotely green before one machine gate, private consumed
marker, and public request. A metadata success stops after one private manifest
and one aggregate report; it does not cascade into EEG acquisition.

Machine decision: refuse before consumption unless all thread values equal
one, at least 2 GiB is free, normalized one-minute load is no greater than
`1.0` per logical CPU, and every machine value is available. Limit the public
stage to 30 seconds, 256 MiB RSS, and 1 MiB output.

Boundary: the request authorizes nothing. Commit, push, and green the packet,
then identify it as the sole active Tier C request. Only a fresh unambiguous
maintainer message after that identification may be recorded in a separate
decision; the current `continue` is not retroactive.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_PACKET.md`,
`registries/iackd_snapshot_identity_authorization_request.v0.json`, and
`tests/test_iackd_snapshot_identity_authorization_request.py`.

## 0175 - Bind The Fresh Maintainer Continue To IACKD-M1A

Decision: accept the maintainer's exact message `keep going, move the needle,
continue, you approved to go on` as the fresh packet-bound Tier C decision for
the sole active IACKD-M1A request at `ce84738`, not as a fabricated recital of
the packet's long scope.

Reason: the request and packet were already committed, pushed, and green in
both CI jobs; Codex had identified the exact commit, CI, one-wrapper/
one-response scope, 2 MiB cap, zero-payload boundary, and fresh-decision gate.
The new message unambiguously directs that named work to continue. The
separate decision quotes all 60 bytes and binds the request and packet hashes.

Ordering: the decision must first become remotely green. Only then may the
generated/mock wrapper be implemented. That exact wrapper must separately
become remotely green before one machine-gated public metadata response.

Boundary: do not infer an EEG payload, local IACKD operation, consumed-root
fallback, model, target, score, dependency install, retry, rerun, release,
hardware, destructive action, or scientific claim upgrade. A metadata success
must stop without acquisition.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_DECISION.md`,
`registries/iackd_snapshot_identity_authorization_decision.v0.json`, and
`tests/test_iackd_snapshot_identity_authorization_decision.py`.

## 0176 - Separate Public Transport From Snapshot Identity

Decision: implement IACKD-M1A as an additive standard-library wrapper around
the immutable green canonicalizer. Treat HTTP status, final URL, framing,
Content-Length, body bytes, and raw response hash as transport provenance;
require snapshot anchor, recursive tree, selected inventory, and critical
metadata as separate semantic gates.

Safety decision: require all one-thread values, 2 GiB free disk, available CPU
and load metrics, normalized one-minute load at most `1.0`, and RSS below 256
MiB before writing the consumed marker. After the marker, one request and one
body read are terminal. Emit an aggregate refusal if possible and never retry.

Privacy decision: retain 1,340 object rows only in a Git-ignored private
manifest. Publish no individual path, object ID, S3 URL, or version ID. Keep
the raw response in memory only through one canonicalization.

Qualification decision: generated/mock `IACKDMP-R0` must pass all three
framing profiles, 20 wrapper refusal mutations, two semantic replays, strict
output limits, and zero public, neural, target, model, or score counters. The
measured run passed in 0.09886470879428089 seconds at 46,563,328-byte peak RSS
with 429,430 output bytes.

Boundary: this exact wrapper must be committed, pushed, and remotely green
before one public request. Metadata compatibility cannot authorize an EEG
payload or establish a scientific or decoding result.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_IMPLEMENTATION.md`,
`registries/iackd_snapshot_identity_public_implementation.v0.json`, and the
two `test_iackd_snapshot_identity_public*.py` files.

## 0177 - Park IACKD-M1A At The Exact Response Envelope

Decision: classify the one consumed public request as
`IACKDMP-F05-snapshot-semantic-canonicalization-failure`. The response passed
the transport stage, but its root field set was not exact `{data}`. Because the
raw body was discarded, do not guess the additional field or recover it from
an unregistered source.

Evidence decision: preserve the 4,352-byte aggregate result and 374-byte
private marker. Record one request, open, read, and hash over a 595,082-byte
response. Also record that the failure serializer omitted the computed hash
and framing profile, making those fields unavailable rather than silently
reconstructing them.

Execution decision: no retry, rerun, source amendment, serializer repair, or
post-result executor patch is allowed in IACKD-M1A. The CLI reporting
`TypeError` occurred after result creation and does not justify another
request.

Boundary: zero S3 payload, local IACKD, signal, event, trajectory, target,
model, prediction, and score operations occurred. The result is an
engineering envelope incompatibility, not snapshot compatibility or a neural
or decoding result. A future diagnosis needs a new prospective contract and
Tier C decision.

Evidence: `docs/IACKD_SNAPSHOT_IDENTITY_PUBLIC_RESULT.md`,
`registries/iackd_snapshot_identity_public_result.v0.json`, and
`tests/test_iackd_snapshot_identity_public_result.py`.

## 0178 - Replace The Next Larger Model With A Two-Axis Artifact Test

Decision: select MARC-1 as the next scientific effect lane. Preserve WO9R as
positive held-out task-information evidence, but do not upgrade its source
interpretation while early cue and frontal proxy controls remain stronger than
the registered motor-localization conjunction.

Source decision: pair two complementary licensed public datasets. Freewill-23
provides self-selected target and movement timing, four EOG channels, and
synchronized wrist acceleration. Wrist-45 provides eight forearm EMG channels,
synchronized robotic encoders, and participant-level archives. Require both
axes to pass with one compact causal low-frequency family; make the weaker
axis margin primary.

License decision: park the scientifically attractive Aalborg self-paced
EEG/EOG/EMG source. Its public repository declares no license and its paper
says data are available on request. Public visibility does not authorize reuse.

Storage decision: forbid a whole download of the 13,591,548,048-byte
Freewill-23 ZIP. Any future execution must first prove bounded byte-range ZIP
inventory, select only exact participant members, remain below an 8 GiB
incremental payload ceiling, and preserve at least 12 GiB free disk.

Boundary: this Tier A record authorizes generated-fixture development only. It
does not authorize a live archive HEAD or range, payload member, signal, event,
onset, target, derivative, model, prediction, score, rerun, release, or claim
upgrade.

Evidence: `docs/MARC_1_MULTIMODAL_ARTIFACT_RESOLVED_MOVEMENT_RESEARCH.md`,
`registries/marc1_multimodal_artifact_resolved_movement_research.v0.json`, and
`tests/test_marc1_multimodal_artifact_resolved_movement_research.py`.

## 0179 - Freeze Generated Mechanics Before Any MARC-1 Public Request

Decision: qualify archive inventory and multimodal firewalls entirely on
generated bytes before asking for public metadata or payload access. Use the
standard library's ZIP parser over an instrumented random-access adapter;
inventories may inspect metadata but must never open or extract a member.

Interface decision: expose only `plan`, generated `qualify --output-dir`, and
aggregate-report `inspect`. Do not add a URL, host, archive path, participant,
target, model, provider, or live execution option.

Scientific-interface decision: keep source type, functional control role, and
model inclusion separate. Freeze a generated past-only `[-1.5, -0.2)` window,
physical fit/prediction/scorer roles, all twelve MARC-1 comparators, 24
adversarial mutations, deterministic replay, and one-thread resource caps.
The window qualifies an interface and does not preselect the later real-data
window.

Boundary: generated `MARC1G-R1` is engineering evidence only. It cannot
authorize a public response, archive range, member payload, signal, onset,
target, model, score, release, or claim upgrade. Implementation may begin only
after this exact contract is committed, pushed, and both required CI jobs are
green.

Evidence: `docs/MARC_1_GENERATED_QUALIFICATION_PREREGISTRATION.md`,
`registries/marc1_generated_qualification_contract.v0.json`, and
`tests/test_marc1_generated_qualification_preregistration.py`.

## 0180 - Implement ZIP Inventory Without A Member-Content Surface

Decision: implement MARC-1 generated qualification only after green contract
`4494d57`. Use `zipfile.ZipFile` over a read-only seekable adapter and record
payload intervals from the writer rather than inferring them from archive
strings. Add a maximum-length deterministic ZIP comment so the standard
library's EOCD search stays in archive metadata for the tiny fixture.

Privacy decision: keep member names and local offsets only in the generated
private manifest. The aggregate report may expose counts, bytes, methods,
hashes, measurements, warnings, unavailable fields, refusal summaries, and
claim boundaries. Aggregate `inspect` must refuse the private manifest.

Scientific-interface decision: validate modality semantics and causal/target
contracts as metadata only. Do not implement a classifier. Generated feature
values are identity-derived and target-independent; peripheral streams remain
nonpredictive controls, not EEG substitutes.

Execution decision: development tests may exercise generated fixtures and
temporary CLI outputs. The one registered measured closeout is a separate
event and may occur only after this exact implementation commit is pushed and
both CI jobs are green. Public archive access remains a later exact Tier C
decision.

Evidence: `docs/MARC_1_GENERATED_QUALIFICATION_IMPLEMENTATION.md`,
`registries/marc1_generated_qualification_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_generated_qualification.py`, and
`tests/test_marc1_generated_qualification_implementation.py`.

## 0181 - Consume MARC1G-R1 As Engineering Proof Only

Decision: accept the one post-green generated closeout at `MARC1G-R1`. It
demonstrates deterministic bounded ZIP metadata inventory and multimodal
firewall mechanics, including 24/24 adversarial refusals, without reading a
member payload.

Resource decision: preserve the measured 0.006588957970961928-second runtime,
23,511,040-byte peak RSS, 81,139 generated input bytes, 7,813 output bytes, 14
range calls, and 202,529 returned metadata bytes. Preserve the failed CI
attempts as test-harness history; they were not registered closeout runs and
did not alter the production source or 256-MiB cap.

Artifact decision: retain only aggregate measurements plus SHA-256 identities
for the 5,018-byte aggregate report and 2,795-byte generated private manifest.
Remove the exact invocation-created temporary directory. Do not commit either
generated output as inspection debris.

Boundary: consume the closeout with no retry or rerun. `MARC1G-R1` is not
human-neural evidence and authorizes no public request. The next eligible work
is Tier A metadata-range-audit design; one live request requires a separately
named Tier C packet and exact maintainer decision.

Evidence: `docs/MARC_1_GENERATED_QUALIFICATION_RESULT.md`,
`registries/marc1_generated_qualification_result.v0.json`, and
`tests/test_marc1_generated_qualification_result.py`.

## 0182 - Inventory The Freewill Monolith Through Three Bounded Bodies

Decision: advance `MARC1-CD1` as a metadata-only range-audit lane. Do not
download the 13,591,548,048-byte Freewill archive to discover its contents.
Use one version-specific Figshare metadata response, one exact 131,072-byte
tail range, and at most one exact central-directory range no larger than 16
MiB.

Archive decision: require the classic EOCD, ZIP64 locator, and complete ZIP64
EOCD to reconcile inside the fixed tail before the central-directory request.
Park if ZIP64 requires another exploratory read, the directory is larger than
16 MiB, the archive is split or encrypted, range framing is not an exact
single-part `206`, or any offset is not proven in bounds.

Privacy decision: exact member names, offsets, and checksums belong only in a
Git-ignored private manifest. Aggregate output may contain counts, byte totals,
role summaries, canonical hashes, measurements, warnings, and unavailable
states, but no member name, offset, download/redirect URL, response header, or
per-member checksum.

Integrity decision: a central-directory audit does not verify the registered
whole-archive MD5, member CRC-32 values, local headers, or member payloads.
Those states remain explicitly unavailable until a later separately frozen
acquisition.

Boundary: this Tier A design authorizes no public response or archive range.
First freeze a generated/mock contract, implement it without a live endpoint,
and require both CI jobs green. Only then may an all-false Tier C request be
prepared for one no-retry audit capped at 17,039,360 response-body bytes.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESEARCH.md`,
`registries/marc1_freewill_central_directory_research.v0.json`, and
`tests/test_marc1_freewill_central_directory_research.py`.

## 0183 - Qualify MARC1-CD1 With A Virtual 13.59 GB Archive

Decision: freeze a generated/mock-only contract before implementing any live
transport. Represent the bound 13,591,548,048-byte archive with only a small
metadata body, 128-KiB tail, and sub-1-MiB generated central directory. Never
allocate a sparse or complete monolith for qualification.

Transport decision: inject a strict mock transport and resolver. Exercise a
direct terminal `206` and up to two bodyless HTTPS redirects under exact
request ordering, range, encoding, framing, length, and cap-plus-one checks.
The production module must contain no URL opener or `execute` command.

Parser decision: use standard-library `struct` and bounded slices instead of
`zipfile`, because the future live path will have only trailer and directory
ranges. Freeze 18 generated entries, a comment-embedded EOCD decoy, complete
in-tail ZIP64, safe directory/regular kinds, strict ZIP64 extras, private exact
inventory, aggregate-only inspection, deterministic replay, and 32 mutation
refusals.

Boundary: contract success `MARC1CDG-R1` is generated engineering proof only.
Implementation may start only after this contract commit passes both remote CI
jobs. A later generated closeout still cannot authorize one live response,
member acquisition, signal/event/target read, model operation, score, or claim
upgrade.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_PREREGISTRATION.md`,
`registries/marc1_freewill_central_directory_contract.v0.json`, and
`tests/test_marc1_freewill_central_directory_preregistration.py`.

## 0184 - Implement MARC1-CD1 Without A Live Archive Surface

Decision: accept a dependency-free generated implementation only after
contract `cf63043` passed both required CI jobs. The module exposes `plan`,
generated `qualify`, and aggregate `inspect`, but no execute mode, network
opener, DNS query, URL argument, local archive path, or member-content reader.

Archive decision: represent the exact 13,591,548,048-byte identity with one
128-KiB generated tail and one 148,910-byte generated central directory.
Structurally parse a comment-embedded EOCD decoy, the classic EOCD, ZIP64
locator, full ZIP64 EOCD, and all eighteen entries using `struct`. Materialize
no local header or payload byte.

Transport decision: exercise exact direct and two-bodyless-redirect response
queues with injected destination resolution. Require terminal `206`, exact
single-part ranges and lengths, identity encoding, body caps, safe HTTPS
destinations, strict ordering, and no retry, exploratory range, or full-file
fallback.

Privacy and validation decision: keep names and offsets only in the generated
private manifest. Permit aggregate counts, hashes, measurements, warnings,
unavailable fields, and claim boundaries in public output. Require canonical
replay, atomic no-overwrite output, and all 32 frozen refusal mutations. A
development qualification can debug these mechanics but is not the one
registered closeout.

Boundary: commit, push, and require both remote CI jobs green for the exact
implementation before one registered generated closeout. Do not prepare an
all-false live packet from development output. Public metadata or archive
ranges, member payloads, neural signals, events, targets, models, scores, and
claim upgrades remain unauthorized.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_IMPLEMENTATION.md`,
`registries/marc1_freewill_central_directory_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_central_directory_audit.py`, and
`tests/test_marc1_freewill_central_directory_implementation.py`.

## 0185 - Consume MARC1CDG-R1 As Archive-Mechanics Proof Only

Decision: accept the one post-green generated closeout at `MARC1CDG-R1`.
Exact implementation `211fd78` passed both jobs in CI `31511626051` before one
fresh Python `-S` qualification. No development run substitutes for this
registered execution.

Result decision: record 280,249 generated input bytes, 11,574 generated output
bytes, 0.006544457981362939-second runtime, 27,131,904-byte reported peak RSS,
18 parsed entries, one ZIP64 member, both frozen transport paths, all 32
refusals, and all 14 acceptance gates. Retain only aggregate measurements and
SHA-256 identities for the 5,898-byte report and 5,676-byte generated private
manifest.

Cleanup decision: inspect the aggregate report once, remove only the two
invocation-created files and their empty temporary directory, and commit no
generated inventory. The exact generated member names and offsets remain
absent from Git.

Boundary: consume the closeout with no retry or rerun. `MARC1CDG-R1` proves
generated transport and ZIP64 directory mechanics only. It does not prove live
range support, the real archive inventory, whole-file MD5, member CRC or local
headers, payload integrity, human signals, events, targets, models, scores, or
any scientific claim.

Next gate: prepare one all-false Tier C request for the frozen live metadata,
tail, and central-directory sequence. The request must become remotely green
before it may be identified as the sole active packet. Only a fresh packet-
bound maintainer decision after that identification could authorize one live
execution.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_RESULT.md`,
`registries/marc1_freewill_central_directory_result.v0.json`, and
`tests/test_marc1_freewill_central_directory_result.py`.

## 0186 - Request One Three-Body MARC1-CD1A Live Audit

Decision: prepare an all-false Tier C request only after generated result
`431ee8d` passed both jobs in CI `31512598915`. The request itself authorizes
nothing and cannot incorporate the maintainer's earlier `continue`
retroactively.

Staging decision: after a fresh packet-bound decision becomes remotely green,
permit only generated/mock development of one additive standard-library live
wrapper. Require the exact wrapper commit to pass both remote jobs before any
public request.

Transport decision: the possible future live invocation may accept one
bounded version-files metadata body, one exact 131,072-byte archive tail, and
one conditional central-directory body no larger than 16 MiB. Cap accepted
body bytes at 17,039,360 and request attempts at five. Only the tail may follow
up to two bodyless HTTPS redirects; the directory must reuse the terminal URL
without redirect. Forbid HEAD, retry, rerun, exploratory range, fallback, and
whole-file download.

Privacy and resource decision: keep exact inventory only in a Git-ignored
private manifest and public output aggregate-only. Require one thread, one
worker, one numerical job, 120 seconds, 256 MiB RSS, 12 GiB free disk, 32 MiB
incremental disk, and 8 MiB combined output. A success remains archive
inventory evidence only and cannot authorize member acquisition.

Boundary: commit, push, and require both jobs green for this exact request.
Only then may Codex identify it as the sole active Tier C packet and accept a
fresh unambiguous maintainer short form by reference. Before a separate green
decision, do not implement the live wrapper, issue a public request, create a
consumed marker, write a private manifest, perform cleanup, touch a real path,
read a member or signal, run a model, score, or upgrade a claim.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_PACKET.md`,
`registries/marc1_freewill_central_directory_authorization_request.v0.json`,
and
`tests/test_marc1_freewill_central_directory_authorization_request.py`.

## 0187 - Bind The Fresh Maintainer Continuation To MARC1-CD1A

Decision: record the maintainer's actual words `keep going, move the needle,
continue, you approved to go on` only after request `950796d` passed Base
Python job `93853089748` and Optional Neuro Readers job `93853089786` in CI
`31513578445`, and after Codex identified MARC1-CD1A as the sole active Tier C
packet with its exact scope and remaining gate.

Authenticity decision: preserve the exact 60 UTF-8 bytes and their SHA-256.
Incorporate the immutable green packet by reference. Do not fabricate its long
scope as a maintainer utterance, infer wider authority, amend the frozen
request, or reuse the words for another packet.

Staging decision: this decision is ineffective until its own exact commit is
tested, pushed, and both remote CI jobs are green. Only after that proof may
one additive standard-library wrapper be implemented and qualified using
generated fixtures, injected DNS, and mocked HTTP responses. Require that
exact wrapper commit to pass both jobs before one public invocation.

Execution boundary: the later invocation remains exactly one bounded
version-metadata body, one exact 131,072-byte tail with at most two bodyless
HTTPS redirects, and one conditional central-directory body no larger than 16
MiB without redirect. Keep the 17,039,360-byte accepted-body cap, five-attempt
cap, private exact inventory, aggregate-only public report, one-thread limits,
12 GiB free-space gate, no retry/rerun, no whole download, and no member
access.

Claim boundary: this record is permission routing, not data or a result. It
adds no neural, decoding, brain-specific, language, real-time, hardware,
assistive, home-use, or clinical evidence.

Evidence:
`docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_DECISION.md`,
`registries/marc1_freewill_central_directory_authorization_decision.v0.json`,
and
`tests/test_marc1_freewill_central_directory_authorization_decision.py`.

## 0188 - Implement MARC1-CD1A As A Proof-Gated Range Wrapper

Decision: after packet-bound decision `624cc4e` passed both jobs in CI
`31519016891`, implement one additive standard-library wrapper around the
unchanged green central-directory parser. Expose only fixed `plan`, generated
`qualify`, aggregate `inspect`, and proof-gated `execute` modes. Add no base
dependency and no user-selected provider, URL, file, range, credential, or
archive path.

Transport decision: disable automatic redirects and proxies; manually permit
at most two bodyless HTTPS tail redirects after loop and globally-routable DNS
checks; permit no directory redirect. Require exact critical framing, identity
encoding, bounded cap-plus-one reads, exact ranges, at most five attempts,
exactly three accepted bodies, and no more than 17,039,360 accepted bytes.

Machine and output decision: verify the exact green decision, request, parser,
implementation registry, clean HEAD, and externally supplied wrapper CI proof
before the machine gate. Require five one-thread values, 12 GiB free disk,
normalized one-minute load no greater than one, 256 MiB executor RSS, a private
pre-request consumed marker, mode-`0600` exact inventory, aggregate-only public
result, and exclusive no-overwrite writes.

Failure decision: after the marker, emit one aggregate route if possible and
consume the invocation. Do not provide retry, rerun, resume, alternate range,
whole-download, local-header, member, extraction, participant, neural, target,
model, or score interfaces.

Qualification decision: accept generated `MARC1CDL-G1` only as implementation
proof. The one registered closeout passed 14/14 gates, all 40 refusal checks,
and zero public or forbidden counters in 0.006050 seconds at 40,763,392-byte
peak RSS. Its 12,182 temporary output bytes were hash-bound and removed.

Boundary: commit, push, and require both jobs green for this exact wrapper
before one public request is eligible. The generated result adds no archive-
content, human-neural, or decoding evidence.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_IMPLEMENTATION.md`,
`registries/marc1_freewill_central_directory_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_central_directory_live.py`, and the two
matching test modules.

## 0189 - Consume MARC1-CD1A As Aggregate Archive-Inventory Evidence

Decision: accept one `MARC1CD-R1` result only because exact wrapper
`5dfa3c4c8cd7f0e990b7b1db7b35c4df8694171f` passed Base Python job
`93879378282` and Optional Neuro Readers job `93879378362` in CI
`31521510374` before execution, and the executor then passed all 14 frozen
gates without opening the whole archive or a member.

Evidence decision: record that four HTTP attempts yielded exactly three
accepted bodies totaling 306,758 bytes: 304 bytes of version metadata, the
exact 131,072-byte archive tail, and a 175,382-byte central directory. Accept
the aggregate inventory of 1,227 entries, including 1,025 regular files and
202 directories, for the 13,591,548,048-byte virtual archive. Do not treat the
registered whole-file MD5, member CRCs, local headers, decompression, or member
payload integrity as verified.

Privacy and lifecycle decision: retain exact member rows only in the
Git-ignored mode-`0600` private manifest and commit only aggregate counts,
hashes, warnings, and unavailable fields. Preserve the private consumed marker
and manifest without publishing, deleting, renaming, or inspecting their
member rows. The one invocation is consumed with no retry or rerun.

Next-step decision: this result completes MARC-1 Task 3 as storage-safe
metadata inventory. It does not authorize Task 4. Any member-level eligibility
analysis, selection, local-header read, payload acquisition, or downstream
experiment requires a separately named prospective contract and Tier C
decision before the private inventory is inspected or any archive member is
accessed.

Claim boundary: this is a real public-archive engineering result, not a neural
or decoding result. Archive metadata contain no participant signal, event,
target, model prediction, or score and cannot establish a neural effect.

Evidence: `docs/MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_RESULT.md`,
`registries/marc1_freewill_central_directory_live_result.v0.json`, and
`tests/test_marc1_freewill_central_directory_live_result.py`.

## 0190 - Freeze A Twelve-Person Two-Axis Pilot Before Inventory Inspection

Decision: use 12 participants per MARC-1 axis, selected by a NUL-separated
DOI-bound SHA-256 rank before any private archive row, Wrist metadata row,
event, target, signal-quality value, or outcome is inspected. Twelve supports
an exhaustive 4,096-assignment participant sign-flip analysis and matches the
WO9R confirmation cohort without approaching the full source archives.

Split decision: for Freewill, use the first three complete numeric run bundles
from session 1 as fit and session 2 as held out, yielding 36 fit and 36 held-
out bundles across 12 people. For Wrist, use runs 1-6 as fit and 7-8 as held
out, yielding 72 fit and 24 held-out runs. Forbid row-random splits,
substitution, backfill, post-hoc cohort reduction, and participant or run
selection by size or CRC.

Storage decision: cap later Freewill and Wrist network allocations at 6 GiB
and 2 GiB, with 8 GiB combined network and incremental disk, 12 GiB minimum
free space, one thread/worker/job, and no fallback budget expansion. Metadata-
only selection must remain below 2 MiB private and 1 MiB public output.

Privacy decision: generated and future real selectors keep exact member and
archive identities private and publish only preregistered participant IDs,
aggregate counts, byte totals, split totals, hashes, warnings, and route. The
selector has no event parser, neuro reader, extractor, target, model, or
scorer.

Boundary: commit, push, and green this exact contract before generated-only
implementation. A generated success does not authorize the sealed Freewill
inventory read, Wrist metadata request, payload acquisition, signal/event/
target access, training, inference, scoring, or a scientific claim. Movement
evidence cannot establish thought-to-text.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_PREREGISTRATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_contract.v0.json`, and
`tests/test_marc1_privacy_preserving_pilot_selection_preregistration.py`.

## 0191 - Implement The Full-Scale Generated Selector Before Metadata Access

Decision: accept a standard-library generated-only implementation after exact
contract `d1218066e64dea502d263acf0c096ed7eab55a11` passed both jobs in CI
`31569417204`. Keep the interface limited to `plan`, generated `qualify`, and
aggregate `inspect`; do not add an execute command, network client, real input
path, override, archive reader, event/signal/target reader, model, or scorer.

Qualification decision: require 1,227 generated Freewill-style rows and 55
generated Wrist-style rows, both frozen DOI-bound ranks, exact bundle/run
splits, conservative byte reservations, 300 private rows mode `0600`, complete
input-order replay, and all 36 refusal mutations. Accept development
`MARC1PSG-R1` only as implementation evidence: 873,348 generated input bytes,
182,563 output bytes, 0.226802 seconds, 32,833,536-byte reported peak RSS, 15
passed gates, and zero real, neural, model, score, or claim operations.

Lifecycle decision: remove the development outputs and do not call them the
registered closeout. Commit, push, and green this exact implementation before
one fresh registered generated closeout. A green generated result may support
one later all-false Tier C request but cannot authorize the sealed Freewill
manifest read, Wrist metadata request, payload acquisition, analysis, or
scientific promotion.

Research-path decision: MARC1-P1 remains a confound-resolution rung toward the
same thought-to-text objective. Movement evidence cannot itself establish
thought-to-text and must not replace the later language-specific held-out
experiment and its no-signal and language-model controls.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_IMPLEMENTATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_pilot_selection.py`, and the two matching
test modules.

## 0192 - Consume The Generated Pilot Selection Before Any Real Metadata

Evidence-order decision: accept the one registered generated closeout only
after exact implementation `0c0a6982c6b9c65d6c51413d1baa8b577e00a194`
passed both required jobs in CI `31571668853`. Record `MARC1PSG-R1` as the
consumed generated result: 873,348 input bytes, 182,564 output bytes, 0.227334
seconds, 32,374,784-byte reported peak RSS, 15 passed gates, 36 passed
refusals, and zero real or scientific operations.

Privacy and lifecycle decision: retain only the aggregate measurements and
SHA-256 identities. Remove the 6,946-byte aggregate report and mode-`0600`
175,618-byte generated private manifest after one registered inspection. Do
not commit, retry, or rerun either output.

Research-path decision: MARC1-P1 remains a confound-resolution and positive-
control rung on the same thought-to-text path. It is not a pivot. Its purpose
is to make a later neural attribution claim harder to fool before returning to
language-specific held-out evaluation. Movement evidence remains insufficient
for thought-to-text and cannot replace no-signal or language-model-only
controls.

Next-step decision: one all-false Tier C request may now be prepared for a
future single read of the exact 418,755-byte sealed Freewill manifest and one
Wrist metadata body capped at 2 MiB. The packet itself authorizes nothing. It
must become remotely green and be identified as the sole active Tier C gate
before a fresh maintainer message may be recorded in a separate decision.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_RESULT.md`,
`registries/marc1_privacy_preserving_pilot_selection_result.v0.json`, and
`tests/test_marc1_pilot_selection_result.py`.

## 0193 - Request One Real Metadata Selection Without Payload Access

Decision: prepare one all-false `MARC1-P1A` Tier C request only after consumed
generated result `fd246294db3defecdc11460e41945f64794b21cf` passed both jobs
in CI `31572950727`. The request itself authorizes no implementation, private
path, public request, selection, output, payload, neural, target, model, score,
or claim operation.

Scope decision: bind a future staged standard-library wrapper followed, only
after that exact wrapper is committed, pushed, and remotely green, by one
no-follow/content-open/hash/parse of the exact 418,755-byte mode-`0600`
Freewill inventory and one Figshare Wrist v3 metadata body capped at 2 MiB.
Require exact frozen participant ranks and splits, zero payload bytes, 30
seconds, 256 MiB peak RSS, 4 MiB incremental disk, one thread/worker/job, 12
GiB free disk, and no retry or rerun.

Failure decision: freeze the Wrist participant-name parser before public
access. A source mismatch parks the sole run; it cannot trigger a fallback,
post-response parser change, participant substitution, or budget expansion.

Research-path decision: this is not a pivot. The metadata gate reduces
selection and confound-attribution risk on the same thought-to-text path, but
movement metadata and any later movement result remain insufficient as
language evidence.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_PACKET.md`,
`registries/marc1_privacy_preserving_pilot_selection_authorization_request.v0.json`,
and `tests/test_marc1_pilot_selection_authorization_request.py`.

## 0194 - Bind The Fresh Approval Without Predeclaring A Result

Decision: record the maintainer's exact words `approved, continue, achieve a
scientific claim, achieve thought to text 😎` only after all-false request
`7f1ba0936e4e0266c0210648aa641feab63cd0eb` passed both jobs in CI
`31573969646` and Codex identified MARC1-P1A as the sole active Tier C packet.
Incorporate the immutable packet by reference; do not fabricate its long scope
as user speech.

Scope decision: after this exact decision is remotely green, permit one
generated/mock-only additive real-selector implementation. Only after that
exact implementation is separately remotely green may one invocation read the
418,755-byte sealed Freewill manifest once and accept one Wrist metadata body
under 2 MiB. Payload, signal, event, target, model, score, retry, rerun, and
claim operations remain forbidden.

Epistemic decision: preserve thought-to-text as the full research objective,
but do not convert that objective into a promised scientific outcome.
Metadata selection can establish only that the frozen pilot exists and fits
the caps. A scientific claim still requires neural payloads, controls,
preregistered held-out scoring, and a positive observed result.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_DECISION.md`,
`registries/marc1_privacy_preserving_pilot_selection_authorization_decision.v0.json`,
and `tests/test_marc1_pilot_selection_authorization_decision.py`.

## 0195 - Freeze The Real Metadata Selector Before Opening Either Source

Evidence-order decision: implement the additive live selector only after
decision `9726d07ab08e9c2815dbe68398659f454693be5e` passed both jobs in CI
`31574870204`. Keep the retained 418,755-byte Freewill manifest and public
Wrist endpoint unavailable during implementation and generated qualification.

Source decision: freeze Wrist participants as exactly `sub-01.zip` through
`sub-45.zip`, with public `sub-01` file ID `62570743`, size `33,690,749`, and
MD5 `6b01cf5bd30de0c670d2837d112a17fa` as an independent anchor. Accept only the
seven source fields `id`, `name`, `size`, `is_link_only`, `download_url`,
`supplied_md5`, and `computed_md5`. Any schema or naming mismatch parks; no
post-response fallback or parser amendment is allowed.

Firewall decision: refuse target-like fields; disable automatic redirects;
require globally routable HTTPS redirect destinations; accept one terminal
JSON body; and create a private consumed marker before any real input. Reuse
the frozen generated selector's rank, split, completeness, privacy, and byte-
cap rules without modifying it. Expose no payload, event, signal, target,
model, score, alternate source, retry, or rerun interface.

Qualification decision: accept generated `MARC1PSL-G1` only as engineering
proof after exact 12+12 cohort selection, 300 private rows, deterministic
replay, 26/26 refusals, 15/15 gates, 866,578 generated input bytes, 214,553
temporary output bytes, 0.183268-second runtime, 50,905,088-byte reported peak
RSS, and zero real/scientific counters. Remove the generated outputs.

Next-step decision: commit, push, and green this exact wrapper before the one
registered metadata invocation. A future `MARC1PS-R1` may establish only that
the frozen source identities exist and fit the caps. Payload acquisition and a
controlled neural effect remain later gates; language decoding and thought-to-
text remain later still on the same research path.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_IMPLEMENTATION.md`,
`registries/marc1_privacy_preserving_pilot_selection_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_pilot_selection_live.py`, and the two
matching test modules.

## 0196 - Preserve The Consumed Transport Refusal As Evidence

Execution decision: run the one MARC1-P1A metadata invocation only after exact
selector `702e61377d41fd1d95939d5e4047be59e4631d4d` passed both jobs in CI
`31578614616`. Treat the attempt as consumed immediately after its private
marker, regardless of success or failure.

Result decision: route `MARC1PS-F03` is a transport-contract refusal. The
executor read and verified the 418,755-byte private inventory exactly once,
opened one Wrist response, accepted zero public-body bytes, and selected zero
participants. It performed zero payload, signal, target, model, score, retry,
rerun, or claim operations. Do not interpret this as evidence for or against a
neural effect or the preregistered cohort.

Recovery decision: do not amend or reopen MARC1-P1A. A separately named
prospective lane must define and adversarially qualify absent versus explicit
identity content-encoding semantics before a new Tier C decision can authorize
another private read or public request. Payload acquisition remains ineligible.
This preserves MARC-1 as a confound-resolution rung on the same thought-to-text
path rather than a pivot.

Evidence:
`docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_RESULT.md`,
`registries/marc1_privacy_preserving_pilot_selection_live_result.v0.json`, and
`tests/test_marc1_pilot_selection_live_result.py`.

## 0197 - Repair The Predicate Without Inventing The Live Header

Standards decision: use RFC 9110 Sections 8.4 and 12.5.3 to separate response
content codings from request-side identity preference. A future terminal
predicate may accept an absent `Content-Encoding` as uncoded and one lone
case-insensitive identity token as a narrow compatibility tolerance. Refuse
every other present value and perform no decompression or decoding.

Epistemic decision: the MARC1-P1A raw header was not retained. Do not claim it
was absent, coded, malformed, or changed. The standards mismatch exists in the
old predicate independently of that unavailable observation.

Scope decision: preserve every existing source, redirect, size, schema,
target-firewall, privacy, output, machine, consumed-marker, no-rerun, and
payload prohibition. MARC1-HT1 is artifact-only research with all 17 current
authorization flags false. It must be remotely green before a separate
generated-only contract is frozen; a future real request remains Tier C.

Path decision: this is a transport repair on the existing MARC-1 positive-
control path toward later held-out language decoding, not a pivot and not a
scientific result.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_RESEARCH.md`,
`registries/marc1_http_identity_semantics_recovery_research.v0.json`, and
`tests/test_marc1_http_identity_semantics_research.py`.

## 0198 - Freeze One Predicate Change And Nothing Else

Contract decision: after MARC1-HT1 research `f515b36` passed both jobs in CI
`31580575669`, freeze one semantic delta only: absent `Content-Encoding` is an
uncoded representation; one identity token is a compatibility tolerance; all
other present values refuse. The request still advertises identity, and no
decompressor or decoder may exist.

Surface decision: a future generated module may expose only `plan`, `qualify`,
and `inspect`. It may not import a network client or the consumed executor,
name a private path or old root, expose `execute`, or alter the frozen
generated selector.

Qualification decision: require four accepted response cases, 20 refusals,
five failure classes, 16 gates, exact 12+12 cohort and split replay, zero
network/private bytes, and all forbidden counters zero under one thread and
small output caps.

Evidence-order decision: the exact contract must be remotely green before
generated implementation. The exact generated implementation and closeout
must then be independently green before an all-false Tier C request can be
prepared. Real metadata and payload acquisition remain closed.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_http_identity_semantics_recovery_contract.v0.json`, and
`tests/test_marc1_http_identity_semantics_contract.py`.

## 0199 - Prove The Predicate In Memory Before Reopening A Source

Implementation decision: after contract `1f99d0a` passed both required jobs in
CI `31581395690`, implement only the additive standard-library MARC1-HT1
`plan`/`qualify`/`inspect` surface. Bind every upstream artifact by no-follow
SHA-256, keep the frozen selector unchanged, and expose no network, private
path, consumed executor, decoder, neural interface, model, scorer, or retry.

Qualification decision: accept the four registered absent/identity forms,
refuse all 20 registered mutations, enforce exact cohort and split replay,
strict aggregate privacy, one-thread resource caps, and byte-identical outputs
under fixed measurements. Development `MARC1HT-G1` passed all 16 gates over
923,052 generated input bytes and emitted 182,682 temporary bytes; every live,
payload, neural, target, model, score, and claim counter remained zero.

Evidence-order decision: this development run is not the one registered
generated closeout. Commit, push, and green the exact implementation first;
only then run and remove one closeout output. A real metadata wrapper or request
remains a new Tier C sequence after the generated result is remotely green.

Path decision: this is a fail-closed transport repair on the same
positive-control-to-language path, not a pivot. It establishes no live-source
compatibility, neural effect, language decoding, or thought-to-text result.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_IMPLEMENTATION.md`,
`registries/marc1_http_identity_semantics_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_http_identity_semantics.py`, and the two
matching implementation tests.

## 0200 - Consume One Generated Closeout Before A New Live Gate

Execution decision: after exact implementation `b2cb48c` passed both required
jobs in CI `31583931303`, run the one registered MARC1-HT1 generated closeout
with one thread, zero network bytes, a new temporary directory, one aggregate
inspection, and no retry or rerun.

Result decision: `MARC1HT-G1` passed all four accepted forms, 20 refusals, 16
gates, exact 12+12 cohort and split replay, output privacy, and resource caps.
It processed 923,052 generated input bytes in 0.1119600001256913 seconds at
33,079,296-byte reported peak RSS. Both 182,681 temporary output bytes were
hash-bound and removed. Every real, payload, neural, target, model, score, and
claim counter remained zero.

Consumption decision: the registered generated closeout is consumed with no
retry or rerun. Require this result to become remotely green before preparing
one all-false Tier C request. That later packet may propose, but cannot itself
authorize, a new live wrapper and one new metadata attempt. The old consumed
root and payload acquisition remain forbidden.

Path decision: passing the generated transport stack is necessary cleanup on
the same positive-control-to-language path. It proves no live compatibility,
neural effect, language decoding, or thought-to-text result.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_SEMANTICS_RESULT.md`,
`registries/marc1_http_identity_semantics_result.v0.json`, and
`tests/test_marc1_http_identity_semantics_result.py`.

## 0201 - Require A Fresh Root And A New Green Wrapper For Live Recovery

Recovery decision: after generated result `5344d73` passed both jobs in CI
`31584662864`, prepare one all-false `MARC1-HT1A` request. The packet may
propose an additive standards-aligned live wrapper and one later metadata-only
attempt, but it authorizes no operation by itself.

Isolation decision: the retained 418,755-byte `MARC1CD-R1` upstream inventory
is a separately bound sealed artifact. A future decision may permit exactly one
new no-follow read of it. The consumed `MARC1-P1A` wrapper, invocation root,
and retained private material remain forbidden and cannot be reopened, reused,
or treated as the new attempt.

Evidence-order decision: first green this request. Then identify its commit,
CI, exact two-input scope, and claim boundary as the sole active Tier C packet.
Only a fresh maintainer message after that identification may be recorded in a
separate decision. If that decision becomes remotely green, only generated and
mocked wrapper implementation is eligible. Real input remains closed until the
exact additive wrapper also passes both remote jobs.

Scope decision: a later live invocation may read one exact private manifest,
accept one Wrist metadata body under the green absent-or-identity semantics,
run the frozen target-free selector, write one private manifest and one
aggregate result, and stop. Payload, signal, target, model, prediction, score,
retry, rerun, release, and claim operations remain forbidden.

Path decision: this is a control and attribution checkpoint on the same route
to a controlled neural positive control and held-out language decoding. It is
not a pivot and establishes no neural effect, language decoding, or
thought-to-text result.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc1_http_identity_live_recovery_authorization_request.v0.json`,
and `tests/test_marc1_http_identity_live_recovery_authorization_request.py`.

## 0202 - Bind The Fresh Approval Without Predeclaring The Result

Authorization decision: request `27f39ae` passed both required jobs in CI
`31586256906` and was identified as the sole active Tier C packet before the
maintainer supplied `approved, continue, achieve a scientific claim, achieve
thought to text 😎`. Record those exact words and incorporate only the green
`MARC1-HT1A` packet by reference.

Interpretation decision: treat achieving a scientific claim and thought-to-
text as the persistent research objective. Do not interpret it as evidence,
predeclare a positive result, weaken a comparator, skip a held-out gate, or
authorize any operation omitted by the packet.

Evidence-order decision: this exact decision must be committed, pushed, and
pass both CI jobs before additive wrapper work. The exact wrapper must then be
committed, pushed, and pass both jobs before one real metadata input is
eligible. No private read, network request, or consumed marker is authorized
before those proofs.

Isolation decision: the new wrapper may compose the green HTTP-semantics module
and target-free selector but cannot import, call, modify, or expose the
consumed `MARC1-P1A` executor. The future attempt must use only the new
`marc1_http_identity/live_recovery_v0` root; the old root remains forbidden.

Scope decision: the authorization stops after one sealed-manifest read, one
bounded Wrist metadata response, one target-free selection, one private
manifest, and one aggregate result. It permits zero payload, signal, target,
model, prediction, score, retry, rerun, release, or claim operations.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc1_http_identity_live_recovery_authorization_decision.v0.json`,
and `tests/test_marc1_http_identity_live_recovery_authorization_decision.py`.

## 0203 - Apply The Standards Repair Without Changing The Research Path

Implementation decision: after decision `9c7bd48` passed both jobs in CI
`31587195405`, implement a new additive wrapper. Compose only the green HTTP-
identity semantics module and frozen target-free selector. Do not import, call,
modify, or expose the consumed `MARC1-P1A` executor.

Transport decision: accept an uncoded response only when `Content-Encoding` is
absent or is one case-insensitive identity token. Refuse empty, duplicate,
list, transfer-coded, and actually coded responses. Perform no decoding or
decompression and retain every existing status, redirect, host, body-cap,
schema, target-firewall, privacy, and output rule.

Isolation decision: use only the new
`.codex_work/marc1_http_identity/live_recovery_v0` invocation root. Refuse the
old consumed root lexically without statting or opening it. A future marker
must precede the first real input, and any post-marker outcome consumes the
sole attempt.

Qualification decision: accept generated `MARC1HTL-G1` only as implementation
evidence. All four accepted response forms replayed one identical target-free
selection; all 21 gates and 31 refusals passed under the 30-second, 256-MiB,
2-MiB output, one-thread, and zero-real-operation boundary.

Evidence-order decision: complete all local verification, then commit, push,
and require both remote jobs green. Only that exact green wrapper may use the
already-recorded decision for one metadata-only attempt. No payload, signal,
target, model, prediction, score, retry, rerun, release, or claim operation is
eligible.

Path decision: MARC-1 is a control and attribution rung on the same route to a
controlled neural positive control, held-out language decoding, and the
long-term thought-to-text objective. It is not a pivot. Generated qualification
establishes no scientific result.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_LIVE_IMPLEMENTATION.md`,
`registries/marc1_http_identity_live_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_http_identity_live.py`, and the two matching
tests.

## 0204 - Preserve The Deeper Semantic Failure Without Rerun

Execution decision: run the one metadata-only `MARC1-HT1A` invocation only
after exact wrapper `68ade0d` passed both jobs in CI `31588920988`. Treat the
attempt as consumed regardless of success or failure.

Transport result decision: the correction passed its live boundary. One
2,917-byte body with absent `Content-Encoding` was accepted under exact length,
JSON, cap, and privacy rules with zero decoding/decompression operations. This
resolves the previous explicit-identity transport blocker.

Semantic result decision: preserve `MARC1HTL-F04` as a strict row-count
identity refusal. The live file list differs from the frozen 55-row contract.
Do not retain or infer the actual count or rows, fall back to another version,
select a partial cohort, or amend the rule after observing the failure.

Consumption decision: the lane has no retry, rerun, resume, restart, parser
amendment, or second source operation. Do not inspect the new private root,
reopen the sealed upstream manifest, or request the endpoint again under this
contract.

Scientific decision: selected participants, payload bytes, signals, targets,
models, predictions, and scores all remain zero. The result diagnoses metadata
snapshot drift, not the MARC-1 neural hypothesis. It adds no scientific claim.

Next-step decision: first green the exact aggregate result. A later Tier A
record may specify a separately named metadata-snapshot identity recovery using
only aggregate evidence. Any new public response remains a new Tier C event;
payload acquisition is still ineligible. This is the same thought-to-text path,
not a pivot.

Evidence:
`docs/MARC_1_HTTP_IDENTITY_LIVE_RESULT.md`,
`registries/marc1_http_identity_live_result.v0.json`, and
`tests/test_marc1_http_identity_live_result.py`.

## 0205 - Make Pagination Part Of Version Identity

Evidence-order decision: begin MARC1-PG1 only after consumed-result commit
`1337a91` passed Base Python job `94091696454` and Optional Neuro Readers job
`94091696340` in CI `31589739739`. Use only committed aggregate evidence,
committed source, and pinned official documentation; do not reopen either
private root or request the dataset endpoint.

Diagnosis decision: omitted pagination is the leading engineering hypothesis
for `MARC1HTL-F04` because the consumed URL supplied neither supported
pagination pair and official Figshare OpenAPI commit `751101d` gives
`page_size` a default of 10. This is not proof that the consumed response held
10 rows. Preserve version-inventory drift and deployed-provider divergence as
live alternatives.

Identity decision: the smallest prospective request is exactly one
version-specific response with `page=1&page_size=1000`. Preserve the frozen
55 rows, 45 participant archives, 10 supplementary rows, declared byte sum,
and `sub-01` anchor. Refuse a second page, alternate pagination pair, article-
details fallback, current-version substitution, partial cohort, or changed
expectation.

Sequencing decision: green this Tier A record before freezing a generated-only
contract. Then require a separately green generated implementation and one
registered generated closeout before an all-false Tier C live-wrapper packet.
The research authorizes no new dataset-specific body, private input, payload,
signal, target, model, score, retry, rerun, or claim action.

Path decision: pagination recovery is a metadata control on the same MARC-1
route to a cue-resistant neural positive control and later held-out language
decoding. It is not a pivot and establishes no scientific result.

Evidence:
`docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_RESEARCH.md`,
`registries/marc1_versioned_pagination_recovery_research.v0.json`, and
`tests/test_marc1_versioned_pagination_recovery_research.py`.

## 0206 - Freeze One Explicit Page Before Any New Source Contact

Evidence-order decision: after research `7a7883a` passed Base Python job
`94095736694` and Optional Neuro Readers job `94095736770` in CI
`31591022429`, freeze a generated-only MARC1-PG1 contract. Do not implement
from an ungreen contract and do not contact the dataset source.

Request decision: bind method, versioned path, exact ordered query
`page=1&page_size=1000`, request headers, one response body, zero second pages,
and zero fallbacks. Refuse missing, default-sized, oversized, duplicate,
reordered, mixed-style, or hidden pagination controls.

Semantic decision: preserve all 55 rows, 45 participant archives, ten
supplementary rows, declared byte sum, `sub-01` anchor, target firewall,
canonical source identity, 12+12 selection, and splits. Response order is not
identity; a partial page or changed expected count is not acceptable.

Qualification decision: require four equivalent generated cases, all 41
mutations, eight routes, 18 gates, deterministic output replay, private/public
separation, source-surface audit, and one-thread resource caps. The only future
commands are `plan`, `qualify`, and `inspect`; no `execute` surface exists.

Scope decision: every real, private, payload, signal, target, model, score,
retry, rerun, release, and claim authorization remains false. A generated pass
would qualify mechanics only. A new dataset-specific body remains Tier C.

Path decision: this is a metadata control on the same cue-resistance to neural-
positive-control to held-out-language route, not a pivot.

Evidence:
`docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_versioned_pagination_recovery_contract.v0.json`, and
`tests/test_marc1_versioned_pagination_recovery_contract.py`.

## 0207 - Qualify Pagination Mechanics Before Another Live Attempt

Evidence-order decision: begin implementation only after exact contract
`ccb3ba8` passed Base Python job `94098410925` and Optional Neuro Readers job
`94098410868` in CI `31591853349`.

Implementation decision: keep the module additive and standard-library-only.
Expose only `plan`, `qualify`, and `inspect`; provide no URL, local-source,
private-root, `execute`, automatic-pagination, retry, fallback, decoder,
payload, signal, target, model, or scorer interface.

Qualification decision: require all four equivalent generated response cases,
41 adversarial refusals across all eight routes, 18 acceptance gates, exact
55-row semantic identity, exact 12+12 target-free selection replay, private/
public output separation, deterministic fixed-measurement replay, and the
frozen one-thread resource envelope.

Sequencing decision: the implementation must be committed, pushed, and both
CI jobs green before one registered generated closeout. That closeout must
also become remotely green before an all-false Tier C packet may propose one
new live metadata response. No current source contact or payload operation is
authorized.

Path decision: this is a metadata prerequisite on the same cue-resistant
neural-positive-control to held-out-language path. It is not a pivot and adds
no scientific evidence.

Evidence:
`docs/MARC_1_VERSIONED_PAGINATION_IMPLEMENTATION.md`,
`registries/marc1_versioned_pagination_implementation.v0.json`,
`src/neurodecodekit/datasets/marc1_versioned_pagination.py`, and the two
matching test modules.

## 0208 - Consume The Closeout At The Output-Path Failure

Evidence-order decision: invoke the one registered closeout only after exact
implementation `2c98a2a` passed Base Python job `94104455930` and Optional
Neuro Readers job `94104455857` in CI `31593790492`.

Failure decision: preserve `MARC1PG-F07` exactly. The requested output parent
`/tmp` is a symlink on this macOS host, and the strict writer refused it. Do not
reinterpret safe file refusal as successful qualification.

Consumption decision: this invocation spent the registered run because output
preflight occurs after contract loading, both generated inventory builds, four
accepted-case validations and selections, selection-hash equality, and private
manifest construction. Existing precedent for an unspent path preflight does
not apply. Do not retry under `/private/tmp`, substitute a path, amend the
implementation, or run the 41-case matrix after the fact.

Evidence decision: record external wall time 0.17 seconds, peak RSS 30,064,640
bytes, zero emitted/incremental/network/real-private bytes, zero files, and all
real, neural, target, model, score, and claim counters at zero. Internal
runtime, generated-input bytes, and output hashes are unavailable because
report measurement never began.

Next-step decision: green this aggregate result, then design a separately
named generated output-preflight recovery. Its output path check must happen
before contract loading or fixture construction. No live metadata request or
payload action is eligible from this result.

Path decision: this is a process failure on the same cue-resistant neural-
positive-control to held-out-language path, not a pivot and not scientific
evidence.

Evidence:
`docs/MARC_1_VERSIONED_PAGINATION_GENERATED_RESULT.md`,
`registries/marc1_versioned_pagination_failure_result.v0.json`, and
`tests/test_marc1_versioned_pagination_failure_result.py`.

## 0209 - Make Safe Output Authority The First Operation

Evidence-order decision: begin MARC1-OP1 only after consumed result `a4dcaea`
passed Base Python job `94107907276` and Optional Neuro Readers job
`94107907246` in CI `31594881048`.

Root-cause decision: classify MARC1-PG1 as a guard-ordering defect. The guard
worked, but only after generated experiment operations began. Preserve the
consumed result and do not amend or rerun it.

Architecture decision: replace string-only repeated path trust with a held
parent-directory capability. Validate every ancestor, refuse symlinks, open the
parent no-follow, bind device/inode/type, require output absence, and retain the
descriptor. Acquire it before any repository read, contract load, deferred
pagination import, fixture, or selection.

Write decision: revalidate the held descriptor, create the output directory
and files parent-relatively with exclusive no-follow operations, and clean up
only allowlisted generated objects through held descriptors. Missing primitive
support must refuse; no fallback is permitted.

Sequencing decision: green this research before freezing a generated-only
contract. Then require separate green contract, implementation, and one
registered generated result before considering a Tier C metadata packet.

Path decision: this is process hardening on the same neural-positive-control
to held-out-language route, not a scientific pivot or result.

Evidence:
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESEARCH.md`,
`registries/marc1_output_capability_recovery_research.v0.json`, and
`tests/test_marc1_output_capability_recovery_research.py`.

## 0210 - Freeze A Probe-Then-Qualify Capability Sequence

Evidence-order decision: freeze MARC1-OP1 only after research `d02830b` passed
Base Python job `94111539407` and Optional Neuro Readers job `94111539431` in
CI `31595996923`.

Surface decision: allow only an additive standard-library `plan`, `preflight`,
`qualify`, and `inspect` module. Ban eager consumed-pagination imports, calls to
its qualifier/output guard/CLI, source modification, network, private input,
payload, model, and absolute-path writes.

Capability decision: require all-ancestor no-follow checks, a held parent
descriptor, device/inode/type binding, child absence at acquisition and
pre-write, and parent-relative exclusive creation of exactly two files.

Sequence decision: after implementation green, run one exact path-only probe.
Only `MARC1OP-P0` opens one qualifier. A failed probe or any post-capability
failure parks without retry, rerun, substitution, or amendment.

Qualification decision: require six accepted cases, 32 refusals, ten routes,
20 gates, deterministic replay, unchanged pagination/selection identity,
resource caps, zero forbidden counters, and exact cleanup.

Path decision: this remains generated process recovery on the same route to a
controlled neural effect and held-out language decoding. It is not scientific
evidence.

Evidence:
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_PREREGISTRATION.md`,
`registries/marc1_output_capability_recovery_contract.v0.json`, and
`tests/test_marc1_output_capability_recovery_contract.py`.

## 0211 - Implement Capability-First Generated Recovery

Evidence-order decision: begin implementation only after frozen contract
`baade51` passed Base Python job `94115807028` and Optional Neuro Readers job
`94115807008` in CI `31597291352`.

Composition decision: add a new standard-library wrapper and leave consumed
MARC1-PG1 byte-identical. Defer-import its hash-bound pure helpers only after
capability acquisition; never call its qualifier, output guard, or CLI.

Capability decision: make acquisition the first call in `preflight` and
`qualify`, attach zero-work snapshots to refusals, hold and revalidate parent
device/inode/type, and permit only two parent-relative exclusive no-follow
writes followed by public-only inspection and exact relative cleanup.

Qualification decision: accept development `MARC1OP-G1` only after all six
accepted cases, 32 refusals, 20 gates, deterministic replay, unchanged 55-row
and 12+12 selection identity, resource caps, and zero forbidden counters pass.

Sequence decision: green the exact implementation before one registered path-
only probe. Only `MARC1OP-P0` opens one registered generated qualifier; any
failure parks without retry. Live metadata remains a later Tier C decision.

Path decision: this is another engineering rung on the same path to controlled
neural attribution and held-out language decoding, not a pivot or result.

Evidence:
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_IMPLEMENTATION.md`,
`registries/marc1_output_capability_recovery_implementation.v0.json`, and the
two matching implementation test modules.

## 0212 - Consume MARC1-OP1 At The Registered Generated Pass

Evidence-order decision: touch the exact registered path only after
implementation `fcedcc3` passed Base Python job `94125013790` and Optional
Neuro Readers job `94125013956` in CI `31600085119`.

Sequence decision: spend one path-only preflight first. Its `MARC1OP-P0` result
with seven zero experiment-work counters opened exactly one generated
qualifier. No path substitution or extra probe was permitted.

Result decision: accept `MARC1OP-G1` after six accepted cases, 32 refusals, 20
gates, exact semantic/split replay, parent-relative exclusive writes, public-
only inspection, resource caps, zero forbidden counters, and cleanup passed.

Consumption decision: close both registered invocations permanently. Do not
rerun, retry, resume, substitute, or amend MARC1-OP1.

Next-gate decision: green the aggregate result before preparing one all-false
Tier C live-metadata request. A request is not permission to contact Figshare;
the live response requires a fresh packet-bound maintainer decision.

Path decision: this successful process gate advances the same controlled-
neural-effect to held-out-language path but adds no scientific evidence.

Evidence:
`docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESULT.md`,
`registries/marc1_output_capability_recovery_result.v0.json`, and
`tests/test_marc1_output_capability_recovery_result.py`.

## 0213 - Request One Exact Paginated Live-Metadata Response

Evidence-order decision: prepare the request only after capability result
`ca4679a` passed Base Python job `94129199903` and Optional Neuro Readers job
`94129199993` in CI `31601329375`.

Scope decision: request one future additive standard-library wrapper and, only
after its exact implementation is remotely green, one no-retry GET to the
Figshare version-3 files endpoint with byte-for-byte query
`page=1&page_size=1000`. Permit one response body capped at 2 MiB and zero
payload requests.

Identity decision: retain the frozen exact 55 rows, 45 participant archives,
ten supplementary rows, 3,683,416,050 declared bytes, 12-subject Wrist cohort,
and runs 1-6 fit versus runs 7-8 held out. Park rather than amend on mismatch.

Output decision: acquire a held no-follow output capability before work,
create one consumed marker, one mode-`0600` private inventory, and one
aggregate report through exclusive relative writes, and touch no preexisting
path. Keep incremental disk under 4 MiB.

Authorization decision: this packet is all false and authorizes nothing. Green
its exact commit first, identify it as the sole Tier C gate, and require a
fresh packet-bound maintainer message before a separate decision may open
implementation. Current and prior messages are not retroactive.

Path decision: this is the next cohort-integrity rung on the same route to a
cue-resistant neural positive control and held-out language decoding. Metadata
success would still not be neural or language evidence.

Evidence:
`docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_PACKET.md`,
`registries/marc1_paginated_live_metadata_authorization_request.v0.json`, and
`tests/test_marc1_paginated_live_metadata_authorization_request.py`.

## 0214 - Bind The Fresh MARC1-LM1 Short Approval

Eligibility decision: accept short form only because `MARC1-LM1` was the sole
active Tier C packet, request `4d3eb19` passed both jobs in CI `31603530015`,
and Codex identified its exact one-response, 2 MiB, zero-payload boundary before
the maintainer replied.

Quotation decision: preserve the exact 76-byte instruction `approved,
continue, achieve a scientific claim, achieve thought to text 😎` and its
SHA-256. Do not fabricate the packet's long scope as a user utterance.

Scope decision: authorize generated/mock wrapper implementation only after
this decision is remotely green, and one live metadata invocation only after
that exact wrapper is separately green. Do not infer payload, neural, target,
model, score, release, or claim authority.

Evidence decision: treat the scientific aspiration as the persistent research
objective, not a positive result. The path remains cohort integrity, controlled
neural evidence, held-out language decoding, then stronger thought-to-text
evidence.

Evidence:
`docs/MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_DECISION.md`,
`registries/marc1_paginated_live_metadata_authorization_decision.v0.json`, and
`tests/test_marc1_paginated_live_metadata_authorization_decision.py`.

## 0215 - Qualify The Capability-First MARC1-LM1 Wrapper

Evidence-order decision: begin only after packet-bound decision `060a365`
passed both required jobs in CI `31604608307`; keep the registered path and
Figshare closed until the exact implementation is separately green.

Architecture decision: use one additive standard-library module with held
parent capability, exact request serialization, bounded no-redirect transport,
strict JSON and target firewalls, deterministic private inventory, aggregate
public output, and one post-marker failure receipt. Import only hash-bound pure
pagination helpers after capability acquisition and never call a consumed
entrypoint.

Qualification decision: accept `MARC1LM-G1` after all four transport forms, 36
refusals, and 20 gates pass with exact 55/45/10 inventory, frozen 12-subject
cohort, zero split overlap, deterministic hashes, bounded resources, public-
only inspection, and exact cleanup.

Next-gate decision: commit, push, and green this exact implementation before
one registered metadata request. Any post-marker outcome consumes. Metadata
success stops before payload and cannot upgrade a scientific claim.

Path decision: this is cohort-integrity work on the same controlled-neural-
effect to held-out-language to thought-to-text route, not a pivot.

Evidence:
`docs/MARC_1_PAGINATED_LIVE_METADATA_IMPLEMENTATION.md`,
`registries/marc1_paginated_live_metadata_implementation.v0.json`,
`tests/test_marc1_paginated_live_metadata.py`, and
`tests/test_marc1_paginated_live_metadata_implementation.py`.

## 0216 - Repair Generated Temporary-Parent Portability

Failure decision: do not treat implementation push `8f67af2` as eligible for
live access. Base Python job `94153342511` and Optional Neuro Readers job
`94153342668` both failed in CI `31608450681` because seven generated tests
assumed macOS `/private/tmp`, which is absent on the Linux runner.

Scope decision: change only generated and test temporary-parent selection to
the canonical real path of the platform's `tempfile.gettempdir()`. Preserve the
exact registered `/private/tmp/neurodecodekit-marc1lm1-live-metadata-20260812`
path and every request, payload, resource, privacy, and no-rerun boundary.

Evidence decision: record zero registered-path, network, source, payload,
signal, target, model, prediction, score, retry, rerun, and claim operations
for the failed push. Requalify generated behavior and require a new commit and
both green jobs before the one live request.

## 0217 - Consume MARC1-LM1 At Frozen Inventory Validation

Evidence-order decision: treat corrected implementation `f9a1ece` as eligible
only because Base Python job `94164152160` and Optional Neuro Readers job
`94164152302` were green in CI `31611639130` before the sole request.

Result decision: record one accepted and parsed 15,652-byte metadata body and
route `MARC1LM-F04` with safe reason `frozen inventory validation refused`.
Do not narrow that aggregate failure to a row-count, filename, ID, URL,
checksum, byte-total, or schema change because the exact predicate is not
available on the public evidence surface.

Disposition decision: consume and park `MARC1-LM1` without retry, rerun,
resume, private-manifest inspection, parser amendment, participant archive, or
payload. Specify any current-inventory recovery prospectively under a new lane
and a new Tier C decision before another public response.

Path decision: cohort identity remains the current gate on the same route to a
cue-resistant neural positive control, held-out language decoding, and
progressively stronger thought-to-text evidence. This is not a pivot.

Evidence: `docs/MARC_1_PAGINATED_LIVE_METADATA_RESULT.md`,
`registries/marc1_paginated_live_metadata_failure_result.v0.json`, and
`tests/test_marc1_paginated_live_metadata_failure_result.py`.

## 0218 - Separate Public Source, Cohort, And Payload Integrity

Research decision: advance `MARC1-SA1` after consumed result `d859509` passed
both jobs in CI `31612923903`. Use only the committed aggregate result and
official Figshare documentation; do not request the dataset endpoint again.

Schema decision: require the documented five-field public file core. Treat
`supplied_md5` and `computed_md5` as known optional extensions that must be
valid and agree when present. Their absence is unavailable provenance, not a
public-core schema failure.

Evidence decision: evaluate all safe inventory predicates independently after
structural and target-firewall gates. Publish only aggregate counts, booleans,
and domain-separated hashes; keep names, IDs, URLs, checksums, rows, and
participant-level results private.

Integrity decision: no metadata checksum substitutes for SHA-256 over bytes
from a later separately authorized acquisition. Metadata attestation and
cohort selection do not authorize payload.

Path decision: this is the next cohort-identity repair on the unchanged route
to cue-resistant neural evidence, held-out language decoding, and progressively
stronger thought-to-text evidence. It is not a pivot.

Evidence: `docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_RESEARCH.md`,
`registries/marc1_source_aware_inventory_attestation_research.v0.json`, and
`tests/test_marc1_source_aware_inventory_attestation_research.py`.

## 0219 - Freeze Source-Aware Attestation Before Implementation

Evidence-order decision: freeze `MARC1-SA1` only after research `aa80503`
passed Base Python job `94173234952` and Optional Neuro Readers job
`94173234944` in CI `31614330447`.

Contract decision: bind six generated semantic families, the exact 21-field
aggregate predicate vector, seven distinct hash domains, 52 named refusals,
25 acceptance gates, deterministic reorder replay, strict private/public
separation, and exact cleanup under one-thread and small-byte caps.

Boundary decision: expose only `plan`, `qualify`, and `inspect`. A future
implementation may have no URL opener, execute mode, dataset-specific body,
registered or consumed path, archive, payload, signal, target, model,
prediction, or score interface.

Next-gate decision: commit, push, and require both CI jobs green before Tier B
generated-only implementation. A live metadata response remains a separately
named Tier C packet and decision after a green implementation.

Path decision: this is prospective cohort-integrity work on the same route to
cue-resistant neural evidence, held-out language decoding, and progressively
stronger thought-to-text evidence. It is not a pivot.

Evidence:
`docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_PREREGISTRATION.md`,
`registries/marc1_source_aware_inventory_attestation_contract.v0.json`, and
`tests/test_marc1_source_aware_inventory_attestation_contract.py`.

## 0220 - Implement Source-Aware Attestation Without A Live Surface

Evidence-order decision: begin only after contract `8f64ccb` passed Base
Python job `94180673330` and Optional Neuro Readers job `94180673125` in CI
`31616551270`.

Architecture decision: use one self-contained standard-library module with
capability-first output, strict JSON and target firewalls, a five-field public
core, optional agreeing MD5 provenance, 21 aggregate predicates, seven
domain-separated hashes, private selection, and aggregate public output. Do
not import or call the consumed live wrapper.

Qualification decision: accept development `MARC1SA-G1` after six semantic
families, 52 refusals, 25 gates, row/key-order replay, public/private privacy,
resource caps, one public inspection, and exact cleanup pass. The final
candidate used 732,811 input and 109,589 output bytes in 0.052419791 seconds at
27,426,816-byte peak RSS.

Next-gate decision: commit, push, and require both CI jobs green before one
registered generated closeout. A live metadata body remains closed behind a
new Tier C packet and decision after any generated result.

Path decision: source-aware cohort identity is still the current step on the
same route to cue-resistant neural evidence, held-out language decoding, and
progressively stronger thought-to-text evidence. It is not a pivot.

Evidence:
`src/neurodecodekit/datasets/marc1_source_aware_inventory_attestation.py`,
`docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_IMPLEMENTATION.md`,
`registries/marc1_source_aware_inventory_attestation_implementation.v0.json`,
and the two matching implementation test modules.

## 0221 - Consume Source-Aware Generated Attestation Before A Live Request

Evidence-order decision: run the sole registered generated closeout only after
exact implementation `feb3b839e879d2a9edcdcfe664c68b3c4ba236d6` passed
Base Python job `94188922905` and Optional Neuro Readers job `94188922771` in
CI `31619037335`.

Result decision: accept `MARC1SA-G1` after all six semantic families, 21
aggregate predicates, seven identity domains, 52 refusals, 25 gates, privacy
checks, resource caps, one public inspection, and exact cleanup passed. The
one run used 732,811 generated input and 109,589 temporary output bytes in
0.053358083 seconds at 27,885,568-byte reported peak RSS.

Honesty decision: record the ephemeral public report SHA-256 as unavailable
because the minimal CLI did not emit it before exact cleanup. Do not rerun or
reconstruct it. The deterministic private hash remains bound, and all real,
private, payload, neural, model, score, retry, and claim counters remain zero.

Consumption decision: the generated closeout is consumed with no retry or
rerun. Require this aggregate result to become remotely green before preparing
one all-false Tier C packet for a separately implemented source-aware live
wrapper. The packet itself cannot authorize a request or payload.

Path decision: this remains the same route from trustworthy multimodal cohort
through cue-resistant neural evidence and held-out language decoding to
progressively stronger thought-to-text evidence. It is not a pivot.

Evidence: `docs/MARC_1_SOURCE_AWARE_INVENTORY_ATTESTATION_RESULT.md`,
`registries/marc1_source_aware_inventory_attestation_result.v0.json`, and
`tests/test_marc1_source_aware_inventory_attestation_result.py`.

## 0222 - Request One Source-Aware Metadata Response Without Payload Authority

Eligibility decision: prepare `MARC1-SA1A` only after generated result
`094b6cb` passed Base Python job `94193898391` and Optional Neuro Readers job
`94193898482` in CI `31620515340`.

Scope decision: request one future additive standard-library wrapper and one
exact Figshare version-3 files GET with one request, zero redirects, one body
capped at 2 MiB, one private canonical manifest, one aggregate report, and
zero participant archive or payload bytes.

Source decision: bind the exact green five-field-core and optional-MD5
attestor. R1/R2 may retain only the frozen target-free cohort. Historical drift
or unknown extensions route R3/R4 and block selection. Provider MD5 never
substitutes for SHA-256 over later acquired payload bytes.

Isolation decision: use a new absent root, acquire output authority first,
refuse any import or operation on the consumed live wrapper/root, use one
thread under small metadata caps, and consume every result or failure without
retry, rerun, parser amendment, or payload continuation.

Authorization decision: this request is all false and authorizes no
implementation or operation. Commit, push, and require both CI jobs green;
then identify it as the sole active Tier C packet and require fresh unambiguous
packet-bound maintainer words. Current and prior messages are not retroactive.

Path decision: this is the next cohort-integrity gate on the same route to
cue-resistant neural evidence, held-out language decoding, and progressively
stronger thought-to-text evidence. It is not a pivot.

Evidence: `docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_PACKET.md`,
`registries/marc1_source_aware_live_metadata_authorization_request.v0.json`,
and `tests/test_marc1_source_aware_live_metadata_authorization_request.py`.

## 0223 - Bind The Fresh Maintainer Instruction Only To MARC1-SA1A

Eligibility decision: accept the maintainer's fresh instruction only after
request `b077550` passed Base Python job `94198174069` and Optional Neuro
Readers job `94198173901` in CI `31621794066`, and after Codex named the sole
packet, scope, zero-payload boundary, and fresh-decision rule.

Verbatim decision: preserve `let’s do those 5 systemically` as the actual
31-byte maintainer message. Do not fabricate a long authorization recital or
silently correct the quoted wording.

Scope decision: bind the instruction only to the immutable `MARC1-SA1A`
packet. After this decision is remotely green, generated/mock wrapper work may
begin. One live metadata response remains conditional on that exact wrapper
also becoming remotely green.

Future-work decision: the broader five-step objective does not itself open
participant archives, payloads, neural data, targets, model training,
prediction, scoring, replication, or language decoding. Freeze and authorize
those later steps prospectively as they become technically eligible.

Path decision: source-aware cohort identity remains the current checkpoint on
the same path to cue-resistant neural evidence and held-out language decoding.
It is not a scientific result or a pivot.

Evidence:
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_DECISION.md`,
`registries/marc1_source_aware_live_metadata_authorization_decision.v0.json`,
and `tests/test_marc1_source_aware_live_metadata_authorization_decision.py`.

## 0224 - Implement The Source-Aware Wrapper Before Its One Metadata Check

Evidence-order decision: begin only after authorization decision `ef9ab91`
passed Base Python job `94353799568` and Optional Neuro Readers job
`94353799602` in CI `31670457497`.

Architecture decision: use one additive dependency-light wrapper that imports
only the green source-aware attestor. Require capability-first output, exact
green commit/CI/registry proof, a clean tracked worktree, one fixed request,
bounded uncoded transport, strict JSON and target firewalls, private/public
separation, and one-shot consumption. Expose no archive or neural payload
interface.

Qualification decision: accept development `MARC1SAL-G1` after six semantic
families, three transport forms, 31 refusals, 20 gates, deterministic semantic
replay, exact cleanup, and resource checks pass. The final measured candidate
used 84,422 generated response bytes and 24,064 transient output bytes in
0.009288083 seconds at 37,552,128-byte reported peak RSS.

Verification decision: preserve the local optional-suite high-water finding
without weakening an old test or resource cap. The exact old rehearsal passes
fresh; require both remote Linux jobs to pass this exact wrapper before any
registered output or public request.

Next-gate decision: after exact commit, push, and both green CI jobs, allow
only the one packeted metadata check. R1/R2 stops with a target-free cohort
identity; R3/R4 or failure blocks selection. Archive acquisition, neural
analysis, targets, scoring, replication, and language decoding remain later
prospective gates.

Evidence: `src/neurodecodekit/datasets/marc1_source_aware_live_metadata.py`,
`docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_IMPLEMENTATION.md`,
`registries/marc1_source_aware_live_metadata_implementation.v0.json`, and the
two matching implementation test modules.

## 0225 - Block The Wrist Cohort After The Consumed Source-Aware Result

Evidence-order decision: execute only after exact wrapper `74aff21` passed
Base Python job `94360721568` and Optional Neuro Readers job `94360722170` in
CI `31672761644`.

Result decision: accept `MARC1SAL-R2` as the frozen blocked-selection outcome.
One metadata response completed attestation in 0.696664542 seconds at
33,439,744-byte peak RSS with 23,112 retained bytes. Zero subjects, archives,
payload bytes, signals, targets, models, predictions, or scores followed.

Unavailability decision: do not reopen the internally inspected aggregate
report or private manifest. The CLI did not emit the private R3-versus-R4
route, body byte count, predicate vector, or historical differences. Preserve
those values as unavailable and do not infer a source-change explanation.

Consumption decision: close `MARC1-SA1A` with no retry, rerun, resume, parser
amendment, expectation change, or Wrist acquisition. The later steps in the
five-part objective are not executable against an ineligible cohort.

Next-work decision: use Tier A work to compare independent cue-resistant
datasets and prospective synchronized EOG/EMG designs. Any new metadata
request, archive, payload, neural experiment, target delivery, or score needs
its own frozen scope and Tier C decision.

Evidence: `docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_RESULT.md`,
`registries/marc1_source_aware_live_metadata_result.v0.json`, and
`tests/test_marc1_source_aware_live_metadata_result.py`.

## 0226 - Replace The Failed Wrist Conjunction With Conditional-Information Triangulation

Predecessor decision: preserve `MARC1SAL-R2` as the consumed Wrist
source-eligibility result. Do not reopen its retained outputs, infer R3 versus
R4, retry, repair, or route around the failed source.

Scientific decision: make participant-macro held-out conditional log-loss gain
the primary endpoint. A fused system counts as EEG evidence only when adding
EEG improves over the strongest available cue, timing, EOG, EMG, and kinematic
model. Raw accuracy above chance is insufficient.

Source decision: keep Freewill-23 as the cue-reduced primary axis. Rank
Biomed-SPC-9 and a bounded PhysioNet Gait-59 subset by a future target-free
utility-per-byte rule for exactly one orthogonal cohort. Reserve OpenNeuro
`ds003626-v2.1.0` for a later Spanish inner-speech command-control experiment.

Architecture decision: permit three compact causal hypotheses, low-frequency
LDA, mu/beta covariance, and `CML-v0`, as separately registered families with
no final-target winner selection. Keep any hosted language model downstream of
a remotely green neural freeze and require it to beat both language-model-only
and item-deranged-neural conditions.

Sequence decision: order the work as `MARC2-FW1`, `MARC2-FW2`, `MARC2-CIL1`,
`MARC2-ORTH1`, and `NDK-LANG1`. Only Tier A design of the first selector is
eligible now. Real private, metadata, payload, neural, target, score,
replication, language, and provider operations remain separately gated.

Evidence: `docs/MARC_2_CONFOUND_TRIANGULATION_RESEARCH.md`,
`registries/marc2_confound_triangulation_research.v0.json`, and
`tests/test_marc2_confound_triangulation_research.py`.

## 0227 - Maximize Freewill Participant Power With A Frozen Contiguous Prefix

Prerequisite decision: begin only after MARC-2 research commit
`ae4d43aabbbe058658c1d77057431f7de331c958` passed both required jobs in CI
`31675452031`.

Rank decision: preserve the exact `MARC1-P1` Freewill DOI seed and all 19
publicly eligible participant ranks. Do not invent a new seed after metadata
history or permit private rows to alter eligibility or rank.

Power decision: keep the old first 12 as a hard floor, then admit participants
13 through 19 only as the maximal contiguous rank prefix whose exact six-run
bundle reservation stays at or below 8 GiB. Stop at the first nonfit. Never
skip, substitute, solve a size knapsack, drop a companion, change a run, or
increase the cap.

Split decision: use the first three numerically ordered complete bundles in
`ses-01` for fit and `ses-02` for held-out data. Member metadata may enforce
structure and storage only. Event, target, timing, channel, signal, quality,
model, and outcome values remain forbidden.

Proof decision: require a 16-participant generated main case, four explicit
byte boundaries, 40 refusals, private/public separation, deterministic replay,
one-thread resource caps, and zero real-operation counters before any later
private-read packet can be prepared.

Evidence: `docs/MARC_2_FREEWILL_PREFIX_SELECTION_PREREGISTRATION.md`,
`registries/marc2_freewill_prefix_selection_contract.v0.json`, and
`tests/test_marc2_freewill_prefix_selection_preregistration.py`.

## 0228 - Separate Private Selection From Every Archive And Neural Operation

Prerequisite decision: prepare the request only after generated-result commit
`a9a759aa5626a41812afe546f03aa324db7a534e` passed both required jobs in CI
`31678418324`. Treat `MARC2FWG-R1` as consumed and do not rerun its generated
closeout.

Boundary decision: bind one exact retained private manifest identity without
touching it. A future target-free selection may read that file only after a
separate packet-bound authorization decision and a separately green additive
wrapper. It may never open an archive local header or member payload.

Implementation decision: require the future wrapper to be standard-library,
proof-disabled by default, fixed to one source and one absent output root, and
qualified on generated manifests plus mocked filesystem facts. Preserve the
40 selector refusals and add 18 proof, path, no-follow, privacy, output, and
one-shot refusals.

Evidence-boundary decision: a successful private selection establishes only
which frozen-rank participant prefix fits the storage cap. It does not qualify
payloads, signals, events, targets, models, scores, language decoding, or any
scientific claim, and it does not authorize `MARC2-FW2`.

Authorization decision: this request is all false. Commit, push, and green it,
then identify it as the sole active Tier C packet and require fresh maintainer
words before recording a separate decision. The current systematic-work
instruction and every earlier continuation are not retroactive authority.

Evidence: `docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_PACKET.md`,
`registries/marc2_freewill_private_selection_authorization_request.v0.json`,
and `tests/test_marc2_freewill_private_selection_authorization_request.py`.

## 0229 - Bind The Fresh Continue Only To MARC2-FW1A

Proof decision: verify request `d0a6eaa391b12f04da35bf277f6409f2750d40df`
at successful CI `31679428199`, Base Python job `94381244828`, and Optional
Neuro Readers job `94381244902` before recording permission.

Communication decision: preserve the maintainer's exact eight-byte message
`continue`. Incorporate only the already identified, immutable, remotely green
packet by reference; do not fabricate a long-form utterance or infer broader
payload or scientific authority.

Order decision: make this decision ineffective until its exact commit passes
both remote jobs. Then permit generated/mock wrapper implementation. Require
that exact wrapper to become remotely green before one private-manifest read
or target-free selection.

Scope decision: keep all archive local-header/member/payload, network, EEG,
signal, event, target, model, prediction, score, provider, `MARC2-FW2`, retry,
rerun, release, and scientific-claim operations closed.

Evidence: `docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_DECISION.md`,
`registries/marc2_freewill_private_selection_authorization_decision.v0.json`,
and `tests/test_marc2_freewill_private_selection_authorization_decision.py`.

## 0230 - Prove The Private Selector Wrapper Before One Manifest Read

Prerequisite decision: begin only after packet-bound decision `ad1e406` passed
Base Python job `94656172494`, Optional Neuro Readers job `94656172528`, and CI
`31764052451`.

Interface decision: expose only fixed `plan`, generated `qualify`, aggregate
`inspect`, and exact-proof `execute` commands. Do not expose source, subject,
seed, cap, split, member, URL, credential, payload, target, or model overrides,
and do not import a consumed MARC1 executor.

Safety decision: require clean remote-green implementation proof, one-thread
machine gates, literal no-follow path checks, exact owner/mode/size/hash/schema,
one bounded sequential content pass, a pre-content consumed marker, separate
private/aggregate outputs, and an aggregate-only failure receipt after
consumption. Preserve zero retries, reruns, resumes, repairs, or fallbacks.

Qualification decision: accept the final generated route `MARC2FWS-G1` after
all 40 inherited selector refusals and all 18 wrapper refusals pass. The
fixture-selected 16 participants, 96 bundles, 384 members, and 8,105,207,776
reservation bytes remain synthetic interface evidence only.

Evidence-boundary decision: require this exact wrapper commit to pass both
remote jobs before one already authorized private-manifest read. Even a future
`MARC2FWS-R1` success stops before archive local headers, members, payloads,
signals, targets, models, scores, `MARC2-FW2`, or a scientific claim.

Evidence: `docs/MARC_2_FREEWILL_PRIVATE_SELECTION_IMPLEMENTATION.md`,
`registries/marc2_freewill_private_selection_implementation.v0.json`,
`src/neurodecodekit/datasets/marc2_freewill_private_selection.py`, and the two
matching implementation test modules.

## 0231 - Consume MARC2-FW1A At Its Pre-Private Proof Refusal

Evidence-order decision: execute only after exact wrapper `d9a3853` passed
Base Python job `94661484721`, Optional Neuro Readers job `94661484713`, and CI
`31765857313`.

Route decision: accept `MARC2FWS-F00` as the final registered outcome. The
executor refused the committed implementation record before the machine gate,
retained source path, consumed marker, content open, hash, parse, selection, or
output writer.

Diagnosis decision: record the tracked-artifact-only finding that the
implementation registry omitted required top-level `lane_id: MARC2-FW1A`.
This is an engineering registration defect. It is not a private-data,
dataset-quality, neural, or scientific result.

Consumption decision: treat the sole invocation as consumed even though no
marker or output root was created. Do not add the missing field to the consumed
implementation, retry, rerun, resume, repair, substitute, or route around it.

Next-work decision: keep `MARC2-FW2` closed. Any recovery must be separately
named, prospectively freeze and test the verifier/record identity on generated
artifacts, and use a new all-false Tier C packet before private access.

Evidence: `docs/MARC_2_FREEWILL_PRIVATE_SELECTION_RESULT.md`,
`registries/marc2_freewill_private_selection_failure_result.v0.json`, and
`tests/test_marc2_freewill_private_selection_result.py`.

## 0232 - Freeze MARC2-FW1B As Generated Proof-Record Recovery

Recovery decision: create a separately named lane and do not edit, import,
call, retry, or route around the consumed `MARC2-FW1A` implementation.

Schema decision: require `lane_id: MARC2-FW1B` among 15 exact top-level fields,
strict JSON, unique normalized repository-relative artifact bindings, and an
explicit prohibition on a candidate registry binding its own digest.

Closure decision: designate
`neurodecodekit.datasets.marc2_proof_record_recovery.validate_implementation_record`
as the single future proof authority. Generated qualification must call that
exact symbol, and any later additive live wrapper must do the same without a
copy, fork, alias, or weaker reimplementation.

Qualification decision: require canonical pass plus byte-identical replay and
32 ordered malformed-record refusals under six failure routes. Keep all work
generated-only, dependency-free, one-threaded, and within 30 seconds, 256 MiB
RSS, and 1 MiB input/output caps.

Authority decision: set private execution limit to zero. A future live wrapper
and one new private selection require a new all-false Tier C packet and fresh
packet-bound decision after the exact generated implementation is remotely
green. `MARC2-FW2` remains closed.

Evidence: `docs/MARC_2_PROOF_RECORD_RECOVERY_PREREGISTRATION.md`,
`registries/marc2_proof_record_recovery_contract.v0.json`, and
`tests/test_marc2_proof_record_recovery_contract.py`.

## 0233 - Qualify One Shared MARC2-FW1B Proof Validator

Proof-separation decision: make expected implementation proof and observed
repository proof separate immutable inputs to one public validator. Require
their exact agreement, observed HEAD equality, clean tracked state, green
ancestor, positive CI/job identities, and the actual registry-byte hash.

Record decision: validate the actual implementation registry, not only a
fixture shaped like it. Require all 15 fields, top-level `lane_id`, six exact
non-self bindings, all-false authority, zero access counters, zero private
execution limit, and an explicit non-scientific claim boundary.

Portability decision: use the canonical package module identity rather than
runtime `__name__`, because `python -m` legitimately runs as `__main__`. Treat
the pre-fix generated CLI refusal as development evidence only; it accessed no
private or real input and created no output.

Qualification decision: accept generated `MARC2FWR-G1` after two canonical
summaries replay byte-identically and all 32 registered mutations refuse on
their exact routes. Record 84,701 input bytes, 6,711 removed output bytes,
0.016927125 seconds, and 27,099,136-byte peak RSS.

Authority decision: require the exact implementation commit to pass both
remote jobs before preparing a new all-false Tier C request. Do not infer live
wrapper authority, retained-path authority, `MARC2-FW2` eligibility, or any
scientific result from generated validation.

Evidence: `docs/MARC_2_PROOF_RECORD_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_proof_record_recovery_implementation.v0.json`,
`src/neurodecodekit/datasets/marc2_proof_record_recovery.py`, and the two
matching implementation tests.

## 0234 - Prepare MARC2-FW1C As An All-False Two-Stage Recovery

Lane decision: do not reopen or repair consumed `MARC2-FW1A`, and do not turn
generated-only `MARC2-FW1B` into a live executor. Name the possible replacement
wrapper and selection `MARC2-FW1C`.

Proof decision: require a native `MARC2-FW1C` wrapper registry plus a distinct
FW1B-format proof certificate supplied to the exact green shared validator.
Both expected and observed proof envelopes must bind the future wrapper HEAD;
the older validator commit cannot be substituted as current HEAD.

Sequence decision: permit no work from this all-false request. A future
packet-bound decision must become remotely green before generated/mock wrapper
implementation. That exact wrapper must then become remotely green before one
no-retry, target-free read of the exact 418,755-byte structural manifest.

Safety decision: use a new absent output root, one no-follow open, 15 GiB free
disk, one thread, 30 seconds, 256 MiB RSS, 2 MiB output, 4 MiB incremental disk,
and zero network or archive-member bytes. Preserve 32 proof, 40 selector, and
18 wrapper refusal mutations. Keep every current authority flag false and
every operation counter zero.

Authority decision: require this request commit, push, and both remote jobs to
be green before identifying it as the sole active Tier C packet. The current
or any earlier `continue` is not retroactive authority. `MARC2-FW2`, payload,
neural, target, model, score, provider, hardware, release, and claim work stay
closed.

Evidence: `docs/MARC_2_LIVE_SELECTION_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc2_live_selection_recovery_authorization_request.v0.json`, and
`tests/test_marc2_live_selection_recovery_authorization_request.py`.

## 0235 - Bind The Fresh Continue Only To MARC2-FW1C

Message decision: preserve the maintainer's actual fresh word `continue` as
eight UTF-8 bytes and its SHA-256. Do not fabricate the packet's long sentence
as a maintainer utterance.

Scope decision: incorporate only remotely green request `7804c3e`, CI
`31769518851`, Base Python job `94672387003`, Optional Neuro Readers job
`94672386941`, packet SHA `f517f0b...`, and request SHA `2dfd45c...` by
reference. Infer no `MARC2-FW2`, payload, neural, model, score, provider,
hardware, release, or claim authority.

Proof decision: keep a native future `MARC2-FW1C` registry distinct from its
FW1B-format certificate. Require the exact shared validator to compare expected
and observed proof against the future wrapper HEAD, not the older validator
HEAD. Preserve all 32 proof, 40 selector, and 18 wrapper mutations.

Order decision: make this decision ineffective until committed, pushed, and
both jobs are green. Only then may generated/mock wrapper implementation begin.
Keep the registered private source and new output root closed until that exact
wrapper is separately committed, pushed, and remotely green.

Safety decision: retain one no-follow private open, 418,755 exact input bytes,
one thread, 30 seconds, 256 MiB RSS, 2 MiB output, 4 MiB incremental disk, 15
GiB free disk, zero network, zero archive-member bytes, and no retry or rerun.
At decision recording, every private, payload, neural, target, model, score,
provider, hardware, release, and claim counter is zero.

Evidence: `docs/MARC_2_LIVE_SELECTION_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc2_live_selection_recovery_authorization_decision.v0.json`, and
`tests/test_marc2_live_selection_recovery_authorization_decision.py`.

## 0236 - Implement MARC2-FW1C With Two Non-Circular Proof Records

Implementation decision: add a new standard-library recovery module without
importing, calling, editing, or exposing the consumed FW1A wrapper or v0 output
root.

Proof decision: keep the native `MARC2-FW1C` implementation registry separate
from the strict FW1B-format certificate consumed by the already-green shared
validator. The native registry does not hash the certificate; future green
evidence binds both independent hashes and the exact wrapper commit, CI jobs,
HEAD, clean tracked state, and decision ancestry.

Qualification decision: accept generated `MARC2FWC-G1` after the shared
validator accepts the exact certificate twice with identical summaries and all
32 proof-record, 40 selector, and 18 wrapper mutations pass. Record 846,712
generated input bytes, 298,059 removed temporary output bytes,
0.3741613749953103 seconds, and 38,666,240-byte peak RSS.

Authority decision: require the exact implementation commit to pass both
remote jobs before the one registered target-free structural selection. Do not
infer archive-member, neural payload, target, model, score, `MARC2-FW2`, retry,
release, or claim authority from generated qualification.

Evidence: `docs/MARC_2_LIVE_SELECTION_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_live_selection_recovery_implementation.v0.json`,
`registries/marc2_live_selection_recovery_proof_certificate.v0.json`, the
additive module, and its two test modules.

## 0237 - Consume MARC2-FW1C At Strict Live Source Identity

Execution decision: accept exact remote-green wrapper `7b924be` as satisfying
the Stage 2 gate, then invoke the one registered structural selection exactly
once with the frozen native registry and FW1B certificate hashes.

Result decision: route `MARC2FWC-F02` is final after one exact 418,755-byte
open/read/hash/strict parse reached target-free selection and the strict live
source identity differed. Retain only aggregate stage, counters, resources,
warnings, and unavailable fields; do not retain or infer the differing private
field or value.

Disposition decision: consume the lane with zero selected participants or
members, no private selection manifest, no retry/rerun/resume/repair, and no
`MARC2-FW2` eligibility. Do not inspect the consumed marker, probe the private
source, list the output root, or use the failure for tuning.

Next-design decision: permit only a separately named artifact-only
committed-schema lineage audit under routine authority. Any future live read
requires a fresh generated contract, green implementation, all-false Tier C
request, and packet-bound decision.

Evidence: `docs/MARC_2_LIVE_SELECTION_RECOVERY_RESULT.md`,
`registries/marc2_live_selection_recovery_failure_result.v0.json`, and
`tests/test_marc2_live_selection_recovery_result.py`.

## 0238 - Diagnose MARC2-FW1C With Committed Schema Lineage Only

Audit decision: use only fixed, hash-bound producer code, selector code,
consumer code, contracts, and aggregate registries. Do not inspect the private
manifest, consumed marker, output root, archive, neural data, target, model, or
score.

Diagnosis decision: accept `MARC2SL-R2`. The producer's exact forwarded
transport map uses `directory`, `metadata`, and `tail`; the generated fixture
and both validators use `central_directory`, `metadata`, and `tail`. This
single alias mismatch is sufficient to explain the consumed F02 structural
refusal and does not imply malformed source data.

Repair-design decision: preserve the producer schema. A future adapter must
validate source-native keys first, then map `directory` to
`central_directory` exactly once while preserving values and refusing missing,
duplicate, dual-alias, extra-key, or value mutation cases.

Disposition decision: do not patch, retry, resume, or reuse FW1C. Generated
adapter qualification may proceed under bounded development authority. Any
future private read or `MARC2-FW2` entry requires a new Tier C packet and
decision.

Evidence: `docs/MARC_2_SOURCE_SCHEMA_LINEAGE_AUDIT.md`,
`registries/marc2_source_schema_lineage_contract.v0.json`,
`registries/marc2_source_schema_lineage_result.v0.json`, the auditor module,
and its two test modules.

## 0239 - Freeze A Generated Producer-Native Transport Adapter

Design decision: preserve the source producer's `directory` vocabulary and the
selector's existing `central_directory` vocabulary as separate schemas. Allow
one explicit value-preserving map only after exact source validation.

Integrity decision: require deep-copy object independence, unchanged digest
values, direct unadapted selector refusal, exact existing selection replay, 26
mutations, and canonical/reversed entry-order success paths.

Scope decision: registration and later generated qualification are Tier B.
The future module has no execute command, generic path, network client, private
root, consumed FW1C import, archive reader, neural input, target, model, or
score interface.

Gate decision: commit and push this registration and require both CI jobs green
before implementation. A live adapter, private read, or `MARC2-FW2` entry
remains a separately named Tier C event.

Evidence: `docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_PREREGISTRATION.md`,
`registries/marc2_transport_alias_adapter_contract.v0.json`, and
`tests/test_marc2_transport_alias_adapter_contract.py`.

## 0240 - Accept The Generated Alias Adapter And Keep Live Use Closed

Implementation decision: validate the complete producer-native generated
manifest before any copy or alias map. Preserve the producer's `directory`
vocabulary and the frozen selector's `central_directory` vocabulary, with one
explicit deep-copy translation between them.

Integrity decision: accept `MARC2TA-G1`. All 26 frozen mutations, both entry
orders, transport-value preservation, source immutability, mutable-object
independence, direct unadapted refusal, and exact existing selector identity
replay passed.

Evidence decision: treat the 0.4533158749982249-second, 39,108,608-byte peak
RSS qualification as generated engineering evidence only. Its 4,931-byte
aggregate was removed, every forbidden counter is zero, and no neural payload,
target, prediction, or score was accessed.

Gate decision: exact implementation/result
`108b869a6199b6d3aa2d87f8a59b6d8bee0c847b` passed both jobs in CI
`31933692066`. Treat generated `MARC2-TA1` as complete and consumed. Do not
patch or reuse FW1C, read a private manifest, access an archive member, or enter
`MARC2-FW2`. Any live adapter is a new Tier C lane with its own all-false
packet and fresh packet-bound decision.

Evidence: `docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_IMPLEMENTATION.md`,
`registries/marc2_transport_alias_adapter_implementation.v0.json`,
`registries/marc2_transport_alias_adapter_result.v0.json`, the adapter module,
and its behavior, implementation, and result tests.

## 0241 - Freeze The Generated Live-Schema Adapter Composition

Architecture decision: add `MARC2-LA1` as a generated/mock composition instead
of patching or importing the consumed FW1C executor. Validate the exact
committed live envelope first, then deep-copy and bridge only proof posture,
provider, file ID, and registered MD5 into TA1's exact generated input.

Integrity decision: require the remotely green public
`adapt_generated_source` call exactly once per success path. Preserve entries,
record/version identity, declared bytes, safety flags, source transport keys,
all digest values, source immutability, and mutable-object independence. Require
canonical/reversed replay of the existing frozen selector result and 30 named
refusals.

Scope decision: keep the future surface at `plan`, `qualify`, and `inspect`,
with zero private, Git-ignored, archive, neural, target, model, network, score,
or FW2 authority and no base dependency delta.

Gate decision: require this exact registration to pass both remote jobs before
generated implementation. Only after that implementation is separately green
may an all-false Tier C request be prepared. The current `continue` is not
retroactive authority for a private read or live executor.

Evidence: `docs/MARC_2_LIVE_SCHEMA_ADAPTER_PREREGISTRATION.md`,
`registries/marc2_live_schema_adapter_contract.v0.json`, and
`tests/test_marc2_live_schema_adapter_contract.py`.

## 0242 - Accept The Generated Live-Schema Composition Locally

Implementation decision: validate the exact live-shaped envelope, all 1,227
entry schemas, run bundles, public run counts, and transport digests before any
copy. Deep-copy and change only the four registered identity values, then call
TA1's exact green public adapter once per success path.

Evidence decision: accept local `MARC2LA-G1`. All 30 mutations and 16 gates
passed; canonical/reversed entry orders reproduced the frozen 16-subject,
96-bundle, 384-member, 8,105,207,776-byte generated selection identity. The
0.4889211250047083-second run used 38,387,712-byte peak RSS and emitted a
5,366-byte mode-0600 aggregate that was removed.

Verification decision: accept 53 focused, 3,360 dependency-free, and 3,431
optional-enabled tests plus Ruff, compilation, 227 registry parses, CLI
checks, tracked hashes, and diff hygiene as the local gate.

Authority decision at this local checkpoint: the implementation was not yet
remotely green. Decision 0243 records the later exact green proof. No private
read, live executor, archive member, neural payload, target, model, score,
network operation, FW2 entry, or claim upgrade opened at either checkpoint.

Evidence: `docs/MARC_2_LIVE_SCHEMA_ADAPTER_IMPLEMENTATION.md`, both LA1
implementation/result registries, the additive module, and its four tests.

## 0243 - Accept The Remote-Green Live-Schema Composition

Proof decision: exact implementation
`3e3f8b86cfb8ac6f23730fb2fcc9fc5da549aac7` passed Base Python job
`95137289730`, Optional Neuro Readers job `95137289704`, and CI
`31935754822`. Accept `MARC2-LA1` as complete and consumed.

Boundary decision: remote green proves the generated composition and its
refusals, not a private source or scientific result. Every private, archive,
neural, target, model, score, network, FW2, and claim authority remains false.

Next-gate decision: permit Tier A preparation of one all-false Tier C packet
for a new additive executor and one exact private structural read only after
this proof-record closeout is remotely green. The packet must then become
remotely green and receive fresh packet-bound maintainer authority before
implementation or access; the current `continue` is not retroactive authority
for that later event.

## 0244 - Prepare An All-False Live Adapter Recovery Packet

Architecture decision: name the prospective recovery `MARC2-LA2` and require a
new additive standard-library executor. It may call exact public functions from
the green proof validator, LA1 adapter, and frozen selector, but it may not
import, edit, call, copy, or inspect either consumed private executor or root.

Scope decision: propose only generated/mock Stage 1 qualification followed,
after separate green proof, by one no-retry read of the exact 418,755-byte
structural manifest. Stop before archive local headers, members, payloads,
signals, events, targets, models, scores, network, FW2, or claim work.

Safety decision: use one thread, one open, a new v2 output root, 30 seconds per
stage, 256 MiB RSS, 2 MiB output, 4 MiB incremental disk, zero network bytes,
and at least 15 GiB free disk. Write the consumed marker before content access;
every route is final.

Authority decision: preserve this request as all false. Require packet commit,
push, and both remote jobs green, then identify it as the sole active Tier C
gate. Only fresh maintainer words after that identification may be recorded in
a separate decision. The current `continue` is not retroactive authority.

Evidence: `docs/MARC_2_LIVE_ADAPTER_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc2_live_adapter_recovery_authorization_request.v0.json`, and
`tests/test_marc2_live_adapter_recovery_authorization_request.py`.

## 0245 - Bind Fresh Short-Form Authority To The Green LA2 Packet

Authorization decision: request
`f9f24a37d840e3408c19dc00830096f6c24b8e03` passed Base Python job
`95140483613`, Optional Neuro Readers job `95140483638`, and CI
`31937038394` before the maintainer supplied the fresh exact message
`continue`. Preserve those actual eight UTF-8 bytes and their SHA-256; do not
fabricate the packet's long scope as the maintainer's words or infer expansion.

Order decision: this record is ineffective until committed, pushed, and both
remote jobs are green. Only then may generated/mock Stage 1 implementation
begin. One retained-manifest read and structural selection remain closed until
that exact executor is separately committed, pushed, and remotely green.

Boundary decision: bind one new additive executor, 56 direct generated
mutations, one later no-retry 418,755-byte structural read, the new v2 output
root, one thread, zero network/archive payload bytes, and the existing resource
and route ceilings. Stop before archive members, neural signals, targets,
models, scores, FW2, release, or claim work. Current operation counters are
zero except one request-CI verification.

Evidence: `docs/MARC_2_LIVE_ADAPTER_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc2_live_adapter_recovery_authorization_decision.v0.json`, and
`tests/test_marc2_live_adapter_recovery_authorization_decision.py`.

## 0246 - Qualify The Additive LA2 Executor Before Private Use

Order decision: accept green authorization decision `b445df2`, CI
`31937743296`, as the prerequisite for generated/mock implementation only.
Preserve the second barrier: the exact executor itself must be committed,
pushed, and pass both remote jobs before any retained-path operation.

Architecture decision: use a new standard-library module that composes the
exact shared proof validator, LA1 adapter, and frozen selector. Do not import,
call, copy, edit, or expose either consumed executor or root. Bind one literal
private source, one new v2 output root, one consumed marker, one no-follow
content open, one LA1 call, one selector call, and no retry or fallback.

Evidence decision: accept generated `MARC2LAR-G1`. All 32 proof-certificate and
24 executor mutations plus ten gates passed. Canonical/reversed fixtures
replayed 16 subjects, 96 runs, 384 members, and 8,105,207,776 reserved bytes in
0.27368504100013524 seconds at 37,978,112-byte peak RSS. The 221,863 generated
output bytes were inspected, hashed, and removed. Every private, archive,
neural, target, model, score, network, retry, and claim counter remained zero.

Boundary decision: generated composition is engineering evidence only. Before
remote green, do not stat, resolve, list, open, hash, or parse the retained
418,755-byte manifest. After green, permit exactly one target-free structural
selection; stop regardless of route before archive members, payloads, neural
data, targets, models, scores, `MARC2-FW2`, release, or claim work.

Evidence: `docs/MARC_2_LIVE_ADAPTER_RECOVERY_IMPLEMENTATION.md`, both LA2
implementation/result registries, the distinct FW1B proof certificate, the
additive module, and its three tests.

## 0247 - Consume LA2 At The First LA1 Refusal

Order decision: accept exact implementation `5390e06`, Base job `95146470514`,
Optional job `95146470539`, and CI `31939483560` as the completed second green
barrier before private access.

Execution decision: record one consumed invocation. It passed the machine and
proof gates, wrote one consumed marker, checked the exact path and source
identity, then opened, read, hashed, and strict-parsed 418,755 structural bytes
once. LA1 refused the source at `live_adapter_and_frozen_selector`; route
`MARC2LAR-F02` is final.

Evidence decision: selected subjects, runs, members, reservation bytes, and
private selections are zero. No LA1 success or selector call occurred. Runtime
was 0.06782554200617597 seconds at 29,425,664-byte peak RSS. Preserve both the
5,695-byte observed aggregate and its 6,096-byte internal output measurement;
do not inspect the marker to resolve the 401-byte discrepancy.

Inference decision: the retained aggregate-safe reason is only `LA1 adapter
refused source`. Do not infer the nested predicate from that reason, reopen the
private manifest, or reinterpret the generated 16-subject prefix as a real
selection.

Boundary decision: LA2 has no retry, rerun, resume, repair, fallback, private
reinspection, or root operation. `MARC2-FW2` remains ineligible. Archive,
payload, neural, target, model, score, network, release, and claim work remain
closed. A new artifact-only diagnosis over committed code and aggregate
artifacts is eligible; any private read needs a new prospective Tier C gate.

Evidence: `docs/MARC_2_LIVE_ADAPTER_RECOVERY_RESULT.md`,
`registries/marc2_live_adapter_recovery_failure_result.v0.json`, and its result
test.

## 0248 - Localize The Generated Source-Domain Coverage Blind Spot

Order decision: require green LA2 closeout `b19a6e2`, Base job `95147662770`,
Optional job `95147662795`, and CI `31939990034` before interpreting its
aggregate refusal through committed artifacts. Do not touch the retained
manifest, marker, or output root.

Evidence decision: accept artifact-only `MARC2VL-R2`. The public source registry
binds 23 participants and 238 runs, while the eligibility map contains 19
participants and 195 session-1/2 runs. The generated fixture creates only those
195 Freewill-shaped bundles, or 780 required companion rows, then fills its
remaining 245 regular rows with generic auxiliaries. It therefore omits 43
published run slots and 172 four-companion slots from the source-shaped test
domain.

Architecture decision: the live validator's global exact 195-group check occurs
before eligibility lookup. Separate future source validity from selection
eligibility: validate every row safely, filter eligible participants/sessions,
then compare the 195-run eligible inventory. Generated qualification must
represent all 43 omitted published run slots as Freewill-shaped adversaries.

Inference decision: the exact private LA1 predicate remains unavailable. The
coverage defect is consistent with the F02 class and sufficient to explain why
generated certification was incomplete; it does not prove which private leaf
fired or that private source data are malformed.

Boundary decision: VL1 authorizes no LA2 patch, retry, rerun, resume, private
read, archive payload, neural data, target, model, score, network operation,
FW2 entry, release, or claim upgrade. A separately named generated-only repair
is eligible under Tier B; any future private read remains Tier C.

Evidence: `docs/MARC_2_VALIDATION_COVERAGE_LOCALIZATION.md`, its contract,
result, module, and two focused tests.

## 0249 - Freeze Source Validity Before Selection Eligibility

Order decision: require green localization head `953692f`, Base Python job
`95151661005`, Optional Neuro Readers job `95151660910`, and CI `31941668496`
before registering the prospective repair. The registration itself must be
committed, pushed, and pass both remote jobs before implementation begins.

Architecture decision: validate all 1,227 generated structural rows and 238
complete Freewill-shaped run bundles before classification. Treat 195 bundles
as eligible and 43 constructed bundles as source-valid but ineligible. Filter
participants and sessions before asserting the exact eligible inventory, then
apply the unchanged rank, session split, reservation formula, contiguous
prefix, and 8 GiB cap.

Qualification decision: represent all 43 omitted source slots through three
generated predicate families: 12 single-session-exclusion bundles, 24
sampling-tier-exclusion bundles, and seven extra-session bundles. Require
canonical/reversed replay, 36 refusal mutations, aggregate-only predicate
counts, and the frozen 16-subject, 96-run, 384-member selection identity.

Boundary decision: this registration has every authorization flag false. It
permits no generated implementation before remote green, and never permits a
private path, consumed root, archive member, neural value, target, model,
score, network operation, LA2 reuse, FW2 entry, release, or claim upgrade. Any
future private read remains a separately named Tier C decision.

Evidence: `docs/MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_PREREGISTRATION.md`,
`registries/marc2_source_validity_eligibility_repair_contract.v0.json`, and its
registration test.

## 0250 - Separate Implementation Proof From The Measured VR1 Closeout

Order decision: accept registration `9dedfe6`, Base Python job `95153164447`,
Optional Neuro Readers job `95153164463`, and CI `31942316544` as the green
barrier before implementation. Require the exact implementation commit to pass
both remote jobs before the one registered measured generated closeout.

Architecture decision: start from the frozen 1,227-row selector fixture and
replace exactly 172 generic auxiliary rows with 43 complete generated
Freewill-shaped adversary bundles. Validate all 238 bundles before
classification, filter to the exact 195 eligible bundles, then apply the
frozen rank, split, reservation, and contiguous-prefix mechanics.

Evidence decision: accept local generated preflight only. It reproduces 16
subjects, 96 runs, 384 members, and 8,105,207,776 reserved bytes with zero
ineligible candidates. All 36 mutations refuse and all eight route classes are
exercised. This is not yet the registered measured closeout.

Boundary decision: the implementation has no execute command, private root,
archive reader, neural interface, target, model, score, network, provider, or
hardware surface. Remote proof and a generated closeout cannot authorize a
private read; that remains a separately named Tier C decision. LA2 is consumed
and `MARC2-FW2` remains closed.

Evidence: `docs/MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_IMPLEMENTATION.md`,
its implementation registry, module, and two implementation tests.

## 0251 - Consume VR1 At Generated Full-Domain Success

Order decision: accept exact implementation `4d587df`, Base Python job
`95155811373`, Optional Neuro Readers job `95155811384`, and CI `31943437003`
as the completed remote barrier before the registered closeout.

Evidence decision: accept `MARC2VR-G1`. All 1,227 rows and 238 complete bundles
passed source validation before aggregate classification. Counts
`195/12/24/7` reconciled, 43 generated adversaries remained ineligible, and
the frozen 16-subject, 96-run, 384-member, 8,105,207,776-byte selection replayed
with zero ineligible candidates. All 36 mutations refused across all eight
routes.

Measurement decision: record 858,844 generated input bytes, 4,680 aggregate
stdout bytes, 0.20698016599635594 seconds, and 32,391,168-byte peak RSS under
one thread. Retained output, network bytes, private bytes, raw reads, caches,
models, and training are zero. Do not rerun merely to reconstruct the
deliberately unretained stdout SHA-256.

Boundary decision: VR1 closes the generated validator blind spot only. It does
not prove that a private source passes and establishes no neural or decoding
result. The closeout is consumed with no rerun. A future private attempt needs
a separately named prospective contract, green one-shot executor, Tier C
request, and fresh packet-bound decision. LA2 and `MARC2-FW2` remain closed.

Evidence: `docs/MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_RESULT.md`, its
result registry, and result-record test.

Proof update: result commit `05fc2b529df54cf9a94d5957402f2136bdf3bbe4`
passed Base Python job `95157101038`, Optional Neuro Readers job
`95157100988`, and CI `31943963317`.

## 0252 - Do Not Freeze A Synthetic Exclusion Mix Into Live Acceptance

Order decision: require the remotely green VR1 proof addendum
`f70d54923c5a0443ee179d6d580aafde94250589`, Base Python job
`95157571747`, Optional Neuro Readers job `95157571692`, and CI
`31944164607` before registering the live-domain adapter. Require this exact
VR2 registration to become remotely green before implementation.

Architecture decision: preserve source validation before eligibility
filtering, but freeze only live-supported invariants: 238 complete bundles,
195 exact eligible session-1/2 bundles, 43 valid ineligible bundles, and the
public 23-participant taxonomy. Classify every noneligible bundle exactly once
without requiring VR1's constructed `12/24/7` predicate split.

Qualification decision: require four generated ineligible distributions in
canonical and reversed order. Every path must reproduce the unchanged
16-subject, 96-run, 384-member, 8,105,207,776-byte selection identity. At
least 44 mutations must cover unknown and overlapping taxonomy, count drift,
exact-breakdown overconstraint, prefilter equality, selection drift, leakage,
and resource boundaries.

Boundary decision: this registration is generated-only and all authority
flags remain false. It permits no private or Git-ignored path, consumed-root
operation, archive member, neural value, target, model, score, network access,
FW2 entry, release, or claim upgrade. The current `continue to eureka` is not
retroactive Tier C authority for a later private attempt.

Evidence: `docs/MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_PREREGISTRATION.md`,
`registries/marc2_live_domain_eligibility_adapter_contract.v0.json`, and its
registration test.

## 0253 - Qualify Variable Exclusion Layouts Without A Profile Input

Order decision: accept registration `384373e0ffcfe999ae0ae188087f7e84f09720ca`,
Base Python job `95159734989`, Optional Neuro Readers job `95159734967`, and CI
`31945086852` as the completed barrier before generated implementation. Keep
the one registered measured closeout closed until this exact implementation is
also remotely green.

Architecture decision: expose one in-memory adapter with no profile argument.
Validate the exact live envelope and all 238 bundles, classify from the public
participant taxonomy, require `195 + 43`, verify the exact eligible map, then
apply the green VR1 selection mechanics. A generated profile name is test
orchestration only and cannot influence live acceptance.

Evidence decision: accept the local development preflight. Four distributions
in two row orders all reproduce the frozen 16-subject, 96-run, 384-member,
8,105,207,776-byte selection identity. All 58 mutations refuse across all eight
routes. The preflight used 3,435,280 generated bytes, 0.5113776249927469
seconds, and 35,356,672-byte peak RSS with zero retained output.

Verification decision: accept 32 focused tests, 3,575 dependency-light tests
with 204 skips, and 3,646 optional-enabled tests with 35 skips. Ruff,
compilation, 240 registry parses, CLI help/plan/inspect, and diff hygiene are
the local implementation gate.

Boundary decision: this is generated engineering evidence only. Do not run the
registered closeout before remote green; do not access either consumed root,
private metadata, archive payload, neural data, targets, models, scores,
network, FW2, release, or claims. Any later private attempt remains a new Tier
C packet and fresh decision.

Evidence: `docs/MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_IMPLEMENTATION.md`,
`registries/marc2_live_domain_eligibility_adapter_implementation.v0.json`, the
additive module, and its two implementation tests.

## 0254 - Consume VR2 At Generated Variable-Domain Success

Order decision: accept exact implementation
`f62a3f5b9966967c569e734552cbc3f11d009401`, Base Python job
`95162220059`, Optional Neuro Readers job `95162220159`, and CI
`31946112252` as the completed remote barrier before the registered closeout.

Evidence decision: accept `MARC2VR2-G1`. Four distinct valid distributions of
the 43 ineligible bundles, each in canonical and reversed order, validated the
full 1,227-row and 238-bundle source before classification. Every path
reconciled `195 + 43` and replayed the same 16-subject, 96-run, 384-member,
8,105,207,776-byte target-free selection with zero ineligible candidates. All
58 mutations refused across all eight routes.

Measurement decision: record 3,435,280 generated input bytes, 4,748 aggregate
stdout bytes, 0.5122641660127556 seconds, and 32,620,544-byte peak RSS under
one thread. Retained output, network bytes, private bytes, raw reads, caches,
models, and training are zero. Do not rerun merely to reconstruct the
deliberately unretained stdout SHA-256.

Boundary decision: VR2 proves that generated live-domain acceptance does not
depend on VR1's constructed `12/24/7` exclusion mix. It does not prove that a
private source passes and establishes no neural or decoding result. The
closeout is consumed with no rerun. A future private attempt needs a separately
named prospective contract, green one-shot executor, Tier C request, and fresh
packet-bound decision. LA2 and `MARC2-FW2` remain closed, and `continue to
eureka` is not retroactive authority for that future packet.

Evidence: `docs/MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_RESULT.md`, its result
registry, and result-record test.

Proof update: result commit `7b6899b987dbd64401494ff2901ade1444f1bf60`
passed Base Python job `95164134927`, Optional Neuro Readers job
`95164134941`, and CI `31946852669`.

## 0255 - Request A New Variable-Domain Private Structural Recovery

Order decision: require green VR2 proof addendum
`bdd34d92eb7abe743597f1a1001e4b6a296225af`, Base Python job
`95164988627`, Optional Neuro Readers job `95164988647`, and CI
`31947198122` before preparing this request. Require this exact packet to be
committed, pushed, and both jobs green before it may be identified as the sole
active Tier C gate.

Architecture decision: create a separately named `MARC2-VR3` sequence rather
than patching LA2. After a future green packet-bound decision, Stage 1 may
implement only a new generated/mock standard-library wrapper around the exact
shared proof validator and VR2 `adapt_live_domain_source`. It must refuse all
consumed executors and roots. Only after the exact wrapper is remotely green
may Stage 2 perform one no-follow read of the already registered 418,755-byte
structural manifest.

Validation decision: require all 1,227 rows and 238 complete bundles to pass
before dynamic eligibility classification, require exactly 195 eligible plus
43 valid ineligible bundles without an exact predicate split, and accept only
the unchanged target-free selector result returned by VR2. Generated wrapper
qualification must cover at least 32 proof mutations, 32 wrapper mutations,
four profiles, two row orders, exact one-call integration, no-follow failures,
output privacy, caps, and consumed-dependency refusals.

Safety decision: write a new consumed marker before the one content open, cap
the future sequence at one thread, 30 seconds per stage, 256 MiB peak RSS,
418,755 private input bytes, 2 MiB output, 4 MiB incremental disk, zero network
bytes, and zero archive-member bytes. Every route consumes the invocation.
There is no retry, rerun, resume, repair, substitution, fallback, old-root
operation, or FW2 authority.

Boundary decision: every current authorization flag is false and every real
operation counter is zero. The current `continue to eureka` is not retroactive
Tier C authority. Only fresh maintainer words after the remotely green packet
is identified may be quoted in a separate decision. The request has no neural
or scientific value.

Evidence:
`docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc2_variable_domain_private_recovery_authorization_request.v0.json`,
and its request test.

## 0256 - Record The Packet-Bound MARC2-VR3 Decision

Authorization decision: preserve the maintainer's actual three-line message,
240 UTF-8 bytes with SHA-256
`b104fe21f692a84f6b9aef74f5d7b0f80f025ea2d5b103798efec4246eff618f`.
Bind its fresh `continue` and structural-manifest direction only to green
request `328faa8`, CI `31947928896`, Base Python job `95166799271`, Optional
Neuro Readers job `95166799305`, and the exact request/packet hashes.

Scope decision: authorize Stage 1 generated/mock wrapper work only after this
decision is remotely green, and one no-retry structural-manifest pass only
after that exact wrapper is separately remotely green. Preserve the requested
FW2 signal, derangement, timing-only, and no-signal experiment as the next
Tier A preregistration after successful cohort freeze.

Boundary decision: the current message cannot authorize real FW2 execution
because no immutable FW2 cohort identity, model matrix, target firewall,
prediction-freeze protocol, score boundary, or resource cap exists yet. Do not
open an archive member, neural value, target, or consumed root; do not train,
predict, freeze, score, rerun, clean up, or promote a claim from this decision.

Evidence:
`docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc2_variable_domain_private_recovery_authorization_decision.v0.json`,
and its focused decision test.

## 0257 - Require Exact Remote Proof Before The VR3 Structural Pass

Implementation decision: add a new standard-library wrapper that composes the
exact shared FW1B proof validator and green VR2 adapter. Keep native VR3 and
FW1B proof records distinct, fix the private source and output root in code,
and expose no generic path, URL, archive, neural, target, model, prediction, or
score interface.

Integrity decision: preserve both a deterministic sorted source digest and an
order-preserving structural fingerprint. Reject any in-place mutation, mutable
alias, adapter call-count change, dynamic `195 + 43` arithmetic drift, split
drift, aggregate private-field leak, resource breach, or nonzero forbidden
counter. Require the exact implementation HEAD, clean tracked state, decision
ancestry, certificate identity, and both green CI jobs before path preflight.

Execution decision: after remote proof, permit exactly one no-follow open and
sequential strict parse of the registered 418,755-byte structural manifest.
Write the consumed marker first, produce at most one private cohort file and
one aggregate report, and allow no retry or rerun. A success freezes only the
target-free cohort; a refusal parks VR3.

Boundary decision: the generated implementation performed zero private,
archive, neural, target, model, prediction, score, or claim operations. A
successful VR3 closeout may support FW2 preregistration, but it cannot authorize
FW2 payload access, training, prediction freezing, target delivery, scoring,
or scientific promotion.

Evidence:
`docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_variable_domain_private_recovery_implementation.v0.json`,
`registries/marc2_variable_domain_private_recovery_proof_certificate.v0.json`,
the additive module, and its two focused tests.

## 0258 - Consume VR3 At Machine Resource Preflight

Result decision: record `MARC2VDR-F01` as the final route for the sole VR3
invocation. Exact implementation proof passed, but aggregate machine resource
preflight refused before output-root preparation or retained-path preflight.
Preserve normalized load, free disk, process RSS, and the exact failed
predicate as unavailable because the executor emitted only the aggregate safe
reason.

Access decision: record zero output-root operations, private path checks,
content opens, private input bytes, hashes, parses, markers, adapter calls, real
cohort selections, output files, archive reads, neural values, targets, models,
predictions, freezes, scores, retries, and claim upgrades. Do not infer a real
cohort from generated VR2 replay.

Disposition decision: consume VR3 with no retry, rerun, resume, repair,
fallback, alternate path, or root reuse. Keep FW2 ineligible because no real
cohort identity exists. The next safe work is a separately named machine-stable
structural recovery and target-free FW2 architecture research; any new private
pass remains a fresh Tier C decision.

Evidence:
`docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_RESULT.md`,
`registries/marc2_variable_domain_private_recovery_failure_result.v0.json`,
and its focused result test.

## 0259 - Separate Machine Readiness From Scientific Consumption

Architecture decision: use `MARC2-VR4 -> MARC2-FW2 -> MARC2-CIL1`. Treat
machine-only load, RSS, disk, and thread checks as reversible readiness, not as
private data access or scientific evidence. Begin irreversible consumption only
at the marker immediately before one private content open. Require exact safe
measurements and a specific refusal reason rather than another opaque aggregate
machine route.

Acquisition decision: after a real cohort hash is remotely green, permit only a
future exact selected-member range design under 10 GiB network and peak-disk
ceilings. Keep whole-archive download forbidden. Freeze member identity,
compressed/uncompressed totals, CRC, SHA-256, roles, clocks, sessions, generic
cues, reviewed onsets, and target cardinality before neural inference.

Scientific design decision: use causal 0.5-4 Hz linear features as primary and
one causal mu/beta family as multiplicity-controlled secondary. Require matched
`P+E` signal, target-independent `P+D(E)` derangement, `B1` timing, and `B0`
no-signal conditions. Freeze continuous held-out target-blind predictions
before one isolated onset/target delivery and participant-level score.

Boundary decision: candidate effect thresholds remain research values, not a
preregistration. The record grants no private, archive, neural, target, model,
prediction, scoring, provider, hardware, release, or claim authority.

Evidence:
`docs/MARC_2_MACHINE_STABLE_COHORT_AND_NEURAL_CONTROL_RESEARCH.md`,
`registries/marc2_machine_stable_cohort_and_neural_control_research.v0.json`,
and its focused research test.

## 0260 - Freeze A Nonconsuming Machine-Readiness Contract

Contract decision: implement readiness separately from a future private
executor. Freeze three consecutive passing samples, five-second minimum sample
interval, 600-second maximum wait, 121-sample maximum, normalized load at most
1.0, process RSS below 256 MiB, 15 GiB free disk, and all numerical thread
variables set to one.

Certificate decision: write only one fixed mode-0600 certificate under 64 KiB,
bind implementation commit and contract hash, report every exact safe value and
threshold, and expire after 300 seconds. A generated or machine-only
`ready=true` result grants no private authority.

Boundary decision: expose no execute command or private source constant in
Stage A. Keep the future executor behind a separate all-false Tier C packet and
fresh decision. Its eventual marker, not machine polling, begins the one-shot
private operation. Do not add a second opaque normalized-load consuming gate.

Evidence:
`docs/MARC_2_MACHINE_STABLE_STRUCTURAL_RECOVERY_PREREGISTRATION.md`,
`registries/marc2_machine_stable_structural_recovery_contract.v0.json`, and its
focused contract test.

## 0261 - Implement Readiness Without Opening A Private Surface

Implementation decision: expose only `plan`, `qualify`, `inspect`, and
`readiness` in a standard-library module. Fix the certificate path, thresholds,
interval, sample count, wait, expiry, mode, and output cap in code. Resolve the
current Git commit without a network call and refuse alternate paths, symlinks,
existing destinations, malformed samples, stale certificates, counter leaks,
and claim upgrades.

Qualification decision: require three generated success scenarios, an
explicit non-ready timeout shape, canonical deterministic replay, strict file
inspection, and all 36 ordered mutations on their six frozen routes. Preserve
exact load/RSS/disk values and refusal reasons in every sample.

Boundary decision: the implementation contains no private source or output
root, execute command, archive or neural reader, target interface, derivative
builder, trainer, predictor, freezer, or scorer. Its exact commit and both CI
jobs must be green before one measured machine-only readiness closeout. A
private structural pass still requires a later all-false Tier C packet and
fresh packet-bound decision; FW2 and CIL1 remain ineligible.

Evidence:
`docs/MARC_2_MACHINE_STABLE_STRUCTURAL_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_machine_stable_structural_recovery_implementation.v0.json`,
the dependency-free module, and its two focused implementation tests.

## 0262 - Close Machine Readiness Without Advancing The Evidence Boundary

Execution decision: after exact implementation `9fdda31` passed both required
jobs in CI `31967145837`, run one fixed `readiness` command under the all-one
thread environment. Record all three exact load, RSS, disk, and timing samples
and one fixed certificate identity.

Result decision: accept `MARC2RDY-G1`. Three consecutive samples passed, the
maximum normalized load was `0.5420735677083334`, peak RSS was 18,055,168
bytes, and minimum free disk was 158,861,668,352 bytes. The mode-0600
certificate is 4,551 bytes with SHA-256
`5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e`.

Boundary decision: machine readiness is engineering evidence only. Record zero
private path operations, content opens, archive reads, neural samples, target
operations, derivatives, model fits, predictions, freezes, deliveries, and
scores. The transient certificate grants no later private authority. Require a
separate all-false Tier C structural packet and fresh packet-bound decision,
including exact safe handling of the expired certificate, before one private
content open. Keep FW2 and CIL1 ineligible.

Evidence: `docs/MARC_2_MACHINE_READINESS_RESULT.md`,
`registries/marc2_machine_readiness_result.v0.json`, and its focused result
test.

## 0263 - Request One Machine-Stable Target-Free Structural Pass

Packet decision: after readiness result `0a4a7fb` passed both jobs in CI
`31967501519`, freeze one all-false `MARC2-VR4P` request. Separate a future
generated/mock implementation from one later real invocation, and require the
exact implementation to be remotely green before the real sequence.

Artifact decision: limit cleanup to the exact expired mode-0600, 4,551-byte
readiness certificate and its SHA-256. Require no-follow identity validation,
one machine-only content read, and one unlink before a fresh certificate. Bind
the fresh certificate to the future exact proof record rather than ambient
branch HEAD. Authorize no other deletion, rename, overwrite, copy, path, root,
project, or consumed artifact.

Structural decision: after fresh readiness, place a new marker immediately
before one 418,755-byte source open. Preserve 1,227 rows, 238 bundles, dynamic
`195 + 43`, one VR2 call, and the target-free 16-subject/96-bundle/384-member
selection. Treat 8,105,207,776 selected bytes as reservation metadata only;
network, archive-member, payload, signal, target, model, prediction, and score
limits remain zero.

Authority decision: keep every request flag false. Require the request itself
to be committed, pushed, and remotely green, then require a fresh
packet-bound maintainer message and separate green decision. The current and
earlier `continue` messages do not authorize implementation or access.

Evidence:
`docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc2_machine_stable_private_recovery_authorization_request.v0.json`,
and its focused request test.

## 0264 - Bind Fresh Short-Form Approval Only To MARC2-VR4P

Authorization decision: after request `a5b73d6` passed Base Python job
`95215825208`, Optional Neuro Readers job `95215825263`, and CI `31967933217`,
and after Codex named it as the sole active Tier C packet, preserve the
maintainer's next message exactly as `continue`. Bind its eight UTF-8 bytes and
SHA-256 to the immutable request and packet hashes. Do not claim the long
packet text as a user utterance and do not infer broader authority.

Delayed-effect decision: this decision grants no immediate implementation or
private operation. Require the decision itself to be tested, committed,
pushed, and green in both required jobs before additive executor work. Require
that exact executor implementation to be separately committed, pushed, and
green before any expired-certificate or retained-manifest operation.

Execution-order decision: preserve one exact registered sequence: validate and
unlink only the known expired certificate, obtain fresh proof-bound readiness,
create the new marker immediately before one 418,755-byte structural content
open, call VR2 once, and write one private cohort manifest plus one
aggregate-safe report. Preserve zero retry/rerun, one thread, 256 MiB RSS, 15
GiB free disk, 4 MiB output, and zero network/archive-payload boundaries.

Evidence-boundary decision: this decision does not authorize archive payload,
neural values, derivatives, training, inference, prediction freeze, target
delivery, scoring, FW2/CIL1 execution, release, or claim upgrade. A successful
structural result may make an all-false FW2 preregistration eligible; it is not
a scientific result.

Evidence:
`docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc2_machine_stable_private_recovery_authorization_decision.v0.json`,
and its focused decision test.

## 0265 - Count The Fresh Certificate In The Recovery Output Cap

Implementation decision: after decision `eac3726` passed both required jobs in
CI `31969063955`, implement the authorized executor additively and exercise the
entire sequence only on generated/mock fixtures. Keep all real certificate,
private source, output-root, archive, neural, target, model, and score counters
at zero until the exact implementation is remotely green.

Accounting decision: interpret the 4 MiB incremental-output ceiling
conservatively. Count the freshly written readiness certificate together with
the consumed marker, private selection manifest, and aggregate report. Require
the report's own byte count to converge before any private or aggregate output
is written.

Safety decision: preserve exact fixed paths, no-follow identities, owner/mode/
size/hash/inode checks, one source open, marker-before-open ordering, one VR2
call, zero retry/rerun/resume/fallback, and the no-override CLI. Do not import or
operate on a consumed executor or root.

Evidence boundary: generated `MARC2MSP-R1` is interface and refusal evidence
only. The exact implementation must be committed, pushed, and green in both
jobs before the sole real structural pass. FW2 payload access and CIL1 neural
training/scoring remain separate Tier C decisions.

Evidence: `docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_machine_stable_private_recovery_implementation.v0.json`, the
distinct proof registry, implementation module, and two focused test modules.

## 0266 - Consume VR4P At The Frozen VR2 Adapter Boundary

Execution decision: after exact implementation `24f7379` passed both jobs in
CI `31970865212`, invoke the registered fixed-path command once under the
all-one thread environment. Permit no retry, rerun, parallel research process,
or post-result private inspection.

Result decision: accept `MARC2MSP-F07`. Proof validation, old-certificate
cleanup, fresh readiness, pre-marker machine checks, marker-before-open order,
one 418,755-byte source read, registered SHA-256, and strict JSON parse all
completed. The frozen VR2 adapter refused before returning a valid cohort.

Epistemic decision: retain only the aggregate-safe reason. The underlying
adapter route, predicate, and any intermediate candidate selection were not
emitted and must not be inferred from a later private read. Record internal
runtime, RSS, readiness samples, load/disk values, and retained output bytes as
unavailable rather than reconstructing them from the fresh certificate or
consumed root.

Boundary decision: freeze zero real cohorts and keep FW2/CIL1 ineligible. Do
not open, inspect, alter, delete, or reuse the fresh certificate, marker,
output root, or retained source under this lane. Permit only separately named
artifact-only mismatch localization until a new immutable Tier C packet and
fresh decision authorize any private operation.

Evidence: `docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_RESULT.md`,
`registries/marc2_machine_stable_private_recovery_failure_result.v0.json`, and
its focused result test.
## 0267 - Localize VR2 Without Reopening The Consumed Source

Execution decision: after the VR4P aggregate result and closeout were remotely
green, freeze one artifact-only audit over exact committed code, contracts,
generated results, prior diagnoses, and the aggregate consumed result. Permit
zero ignored/private path operations, network, archive payload, neural values,
targets, models, scores, or retained output.

Diagnostic decision: classify the VR4P catch as defective because it maps all
eight `LiveDomainEligibilityRefusal` routes to outer `MARC2MSP-F07` without
retaining the aggregate-safe nested route. Preserve the nested reason and all
private values as unavailable.

Selection decision: reject exact generated outcome values as live invariants.
The current path requires nine generated outputs, including fixed subject
count, reservation bytes, and identity hash, and emits generated source
semantics. A future live-compatible contract must instead validate a measured
maximal contiguous rank prefix within frozen bounds and freeze its identity
only after success.

Epistemic decision: do not infer that the consumed attempt reached F06. The
exact nested route remains unavailable; F02/F03/F04 or another source-reachable
route may have fired earlier. Treat VR5A as engineering diagnosis only.

Evidence: `docs/MARC_2_VR2_REFUSAL_LOCALIZATION_PREREGISTRATION.md`,
`docs/MARC_2_VR2_REFUSAL_LOCALIZATION_IMPLEMENTATION.md`, their three
registries, module, and focused tests.

## 0268 - Make Live Selection Invariant-Based, Not Fixture-Identical

Design decision: selected participant count, reservation bytes, and selection
identity are measured outputs. A live source must not reproduce the generated
16-subject fixture or its exact byte total and hash.

Acceptance decision: preserve the frozen rank, full-source validation, 12-19
subject bounds, six run bundles and 24 core members per subject, disjoint
fit/heldout sessions, unchanged 8 GiB cap, and maximal-prefix proof. Accept
either all 19 participants or the exact next ranked participant failing the
cap.

Diagnostic decision: propagate only an allowlisted upstream VR2 route code.
Discard the reason and every private predicate value. Unknown routes fail
closed.

Qualification decision: require generated 12/14/16/18/19-subject boundaries
in two row orders and at least 24 mutations before any private request. Live
rows must use live source semantics. Consumed executors remain immutable.

Evidence: `docs/MARC_2_DYNAMIC_LIVE_SELECTION_PREREGISTRATION.md`,
`registries/marc2_dynamic_live_selection_contract.v0.json`, and its contract
test.

## 0269 - Qualify Dynamic Selection Across Measured Cohort Boundaries

Implementation decision: after registration `71d7cec` passed both required
jobs in CI `31974405202`, implement VR6 as an additive generated-only module.
Expose only `plan` and `qualify`; do not add a private path, URL, output root,
network client, archive reader, neural reader, model, or score interface.

Acceptance decision: validate the complete source before selection, omit the
fixture-exact result assertion, and accept only a measured maximal contiguous
12-19-subject rank prefix. Recompute bundle/member arithmetic, every row's
reservation, the aggregate byte cap, live source hashes, selection identity,
and private-manifest hash. Require either the exact next ranked subject to
overflow the remaining cap or all 19 subjects to fit.

Privacy decision: normalize live-derived rows into a deep-copied manifest,
retain only an allowlisted upstream route code, and discard the upstream reason
and private value. Refuse target, label, quality, outcome, neural, prediction,
or score fields and every aggregate private identifier.

Qualification decision: require five subject-count boundaries in two row
orders and at least 24 direct mutations. The measured run passed ten replay
paths and 34 mutations under one thread with zero retained output and zero
private or scientific operations.

Evidence boundary: generated `MARC2VR6-G1` is interface evidence only. Require
the exact implementation/result commit and both CI jobs green before specifying
a separate private wrapper. A future private read remains a new Tier C packet
and fresh decision; FW2/CIL1 remain ineligible until a real cohort is frozen.

Evidence: `docs/MARC_2_DYNAMIC_LIVE_SELECTION_IMPLEMENTATION.md`,
`registries/marc2_dynamic_live_selection_implementation.v0.json`,
`registries/marc2_dynamic_live_selection_result.v0.json`, module, and tests.

## 0270 - Close VR6 After Exact Remote Proof

Proof decision: exact implementation
`482dad55e91e2abf48b6a59a417ebca191c0cd68` passed Base Python job
`95234487830`, Optional Neuro Readers job `95234487789`, and CI `31975600088`.
Promote only the generated engineering result to remotely green.

Disposition decision: close VR6 at `MARC2VR6-G1`. Tier A/B may specify a
separately named fixed-path wrapper and all-false Tier C request. Do not reuse
the maintainer's current `continue` for the later private decision.

Evidence boundary: no private route became available and no real cohort,
archive payload, neural value, target, model, prediction, score, FW2/CIL1
execution, or scientific claim exists. A private structural pass remains a
fresh packet-bound Tier C action.

## 0271 - Prepare VR7P As A New Dynamic Private-Recovery Request

Lane decision: do not amend or reuse consumed VR4P. Define `MARC2-VR7P` with a
new readiness path, output root, marker, future implementation, and proof
record. Forbid any operation on named consumed paths.

Selection decision: bind exact green VR6 and accept only a measured maximal
contiguous 12-19-subject prefix. Generated subject count, reservation bytes,
and selection hash are not live expected values.

Sequence decision: request a generated/mock wrapper only after a separate
green decision. Request one private structural pass only after that exact
implementation is committed, pushed, and both jobs are green. Freeze one
readiness invocation, one marker-before-open, one 418,755-byte read, one strict
parse, one VR6 call, no retry/rerun/resume/fallback, and bounded outputs.

Authority decision: keep every requested authorization flag false and every
current counter zero. The packet must be committed, pushed, and both jobs green
before it is identified as the sole Tier C gate. The current `continue` is not
retroactive authority.

Evidence: `docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_AUTHORIZATION_PACKET.md`,
`registries/marc2_dynamic_private_selection_recovery_authorization_request.v0.json`,
and its focused test.

Remote proof: immutable request
`9d42bac29b695a97639c4a197812865f0ac4f7d5` passed Base Python job
`95236917861`, Optional Neuro Readers job `95236917836`, and CI `31976595268`.
VR7P is now the sole active Tier C packet. Every authorization flag remains
false; only fresh packet-bound maintainer words may become a decision.

## 0272 - Bind Fresh Continue Only To The Green VR7P Packet

Eligibility decision: accept the maintainer's exact fresh word `continue` only
because VR7P was the sole active Tier C packet, immutable request `9d42bac`
passed both jobs in CI `31976595268`, proof closeout `ecaa2ab` passed both jobs
in CI `31976872160`, and Codex had identified the scope and fresh-decision gate.

Scope decision: quote only the actual eight UTF-8 bytes and incorporate the
green packet by reference. Do not fabricate a long maintainer utterance or
infer FW2, CIL1, archive payload, neural data, training, prediction, scoring,
live operation, or claim authority.

Ordering decision: this decision must be committed, pushed, and pass both CI
jobs before generated wrapper implementation. The exact wrapper must then be
committed, pushed, and pass both jobs before one readiness invocation or
private structural operation.

Evidence: `docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_AUTHORIZATION_DECISION.md`,
`registries/marc2_dynamic_private_selection_recovery_authorization_decision.v0.json`,
and its focused test.

## 0273 - Implement VR7P Without Reusing Consumed VR4P

Eligibility decision: begin generated/mock implementation only after decision
`a318521cf9adb057617e839ead0003d89c3cab84` passed Base Python job
`95244335512`, Optional Neuro Readers job `95244335508`, and CI
`31979669507`.

Architecture decision: add an independent standard-library wrapper. Do not
import, call, patch, alias, or modify consumed VR4P. Bind the new readiness
path, output root, marker-before-open transition, exact no-follow source
identity, shared proof validator, and one green VR6 call in one fixed command
with no path, URL, retry, resume, fallback, or substitution argument.

Selection decision: accept only VR6's measured maximal 12-19-subject prefix.
Do not compare a real outcome with any generated selected count, reservation,
source hash, selection hash, or private-manifest hash. Preserve raw input
provenance while requiring canonical and reversed rows to normalize to the
same private cohort identity within each generated profile.

Qualification decision: require ten generated profile/order paths, two exact
replays per path, all 34 VR6 refusals, and at least 38 wrapper refusals. The
measured implementation passed 85 total direct refusals, 5.951104625 seconds,
54,280,192-byte peak RSS, zero retained generated bytes, and zero real or
scientific operations.

Evidence boundary: this is generated engineering proof only. Require the exact
implementation commit, push, and both remote jobs green before one readiness
or private structural operation. FW2, archive payload, neural data, training,
prediction, target delivery, scoring, live decoding, and claims remain closed.

Evidence: `docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_IMPLEMENTATION.md`,
`registries/marc2_dynamic_private_selection_recovery_implementation.v0.json`,
the distinct proof record, module, and focused tests.

## 0274 - Consume VR7P At The Preserved Upstream-Validation Route

Execution decision: invoke the registered command once only after exact
implementation `154852c58af080904087a2e4cef71991dcb6179d` passed Base Python
job `95252133987`, Optional Neuro Readers job `95252133958`, and CI
`31982672176`.

Evidence decision: retain only wrapper `MARC2VR7P-F07` and allowlisted upstream
VR6 `MARC2VR6-F02`. The latter identifies VR6's upstream VR2-validation branch
but does not reveal the nested VR2 route, failed predicate/value, or candidate
selection. Do not infer those unavailable private facts.

Consumption decision: the route followed one readiness pass, marker, exact
418,755-byte integrity-checked structural open, strict parse, and VR6 call.
Consume the lane with no retry, rerun, resume, repair, fallback, output-root
inspection, or source reinspection. No cohort was frozen, so FW2 and CIL1
remain ineligible.

Claim decision: this is a target-free structural engineering refusal. No
archive member, neural payload, target, model, prediction, score, live decoder,
or scientific claim was reached.

Evidence: `docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_RESULT.md`,
`registries/marc2_dynamic_private_selection_recovery_failure_result.v0.json`,
and its focused test.

Remote proof: initial result commit `ae75423ce9e60c08599ba31fc40f3a6ea584d70e`
passed Base Python job `95253771315`, Optional Neuro Readers job
`95253771324`, and CI `31983281390`. This verified the committed aggregate
record and full suites; it performed no second execution or private operation.

## 0275 - Freeze VR8A As An Artifact-Only Two-Layer Boundary Audit

Lane decision: do not spend another private read while VR7P has retained only
the outer VR6 validation class. Freeze `MARC2-VR8A` as a standard-library audit
of 17 exact committed artifacts totaling 575,582 bytes.

Localization decision: trace the VR7P-to-VR6-to-VR2 exception attributes and
classify all eight VR2 routes by exact call-stage reachability. Test whether
the committed producer module and public result are sufficient to exclude the
VR2 envelope route without opening the 418,755-byte retained source.

Fixture decision: distinguish parser-guaranteed row fields and ZIP safety from
source-dependent BIDS path, companion, bundle, and taxonomy rules. Verify
whether the VR2 generated success source traverses the exact central-directory
producer or begins from a selector-authored synthetic manifest.

Evidence decision: permit only tracked artifact reads, AST and strict JSON
parses, aggregate output under one MiB, one thread, and zero retention. The
exact private route, predicate, member path, participant, session, run, and
value remain unavailable and must not be reconstructed.

Prospective decision: a later generated-only relay may preserve both the outer
VR6 and nested allowlisted VR2 codes while discarding all reasons and private
context. It may not relax F03 or F04. Another private read remains a new Tier C
packet and decision; FW2 and CIL1 stay closed.

Evidence: `docs/MARC_2_VR6_VR2_BOUNDARY_LOCALIZATION_PREREGISTRATION.md`,
`registries/marc2_vr6_vr2_boundary_localization_contract.v0.json`, and its
focused invariant test.

## 0276 - Localize The Remaining VR2 Boundary To F03 Versus F04

Eligibility decision: implement VR8A only after registration
`d33eaf397a8f8444db4d7abd777bf2e9b3333e43` passed Base Python job
`95256950555`, Optional Neuro Readers job `95256950656`, and CI
`31984475999`.

Evidence decision: accept artifact-only route `MARC2VR8A-R1`. Exact producer
lineage, envelope identity, transport digests, row counts, and the prior strict
source verification exclude VR2 F02 without reopening the 418,755-byte source.
The only compatible classes are now F03 path/run-companion structure and F04
bundle/taxonomy arithmetic. The exact private branch remains unavailable and
must not be inferred.

Architecture decision: record that VR6 stores the nested allowlisted VR2 code
in `upstream_route`, while VR7P forwarded only the outer `route`. Also record
that generated VR2 success begins from a selector-authored full-scale manifest
and bypasses the exact producer; the producer's generated parser fixture has
only 18 rows.

Repair decision: require a separately named generated-only diagnostic relay
that preserves both allowlisted route codes but no exception reason or private
context. Do not relax F03 or F04 before an observed safe route. Another private
read or cohort freeze remains a fresh Tier C packet and decision; FW2 and CIL1
remain closed.

## 0318 - Decompose P15 As A Generated Identity Grammar

Decision: the recovered R2 class is still too broad for another private
question. Freeze `MARC2-VR15A` as an artifact-only/generated-only ordered
grammar over path tail, prefix, directory entities, filename subject/session,
task, optional entities, and run presence, position, numeric form, and width.

Matrix decision: use 15 single-failure witnesses, one multiple-class witness,
one control, two row orders, and two replays for 68 unchanged VR12A calls.

Boundary decision: registration and future generated qualification access no
private or ignored state. A private discriminator remains a new Tier C packet
and fresh decision.

Claim decision: this is an engineering localization only. It establishes no
real cohort, neural effect, decoding accuracy, language decoding, live
decoding, or thought-to-text capability.

Remote proof: exact implementation/result
`1addd5df9fdccda6e716f71f9e6624f199677713` passed Base Python job
`95261271737`, Optional Neuro Readers job `95261271709`, and CI
`31986089529`.

## 0277 - Freeze VR8B As A Full-Scale Generated Diagnostic Relay

Eligibility decision: begin registration only after VR8A proof closeout
`8bbb8e36406a5043fdbf1a2e285b070d1bdfc0db` passed Base Python job
`95262067116`, Optional Neuro Readers job `95262067131`, and CI
`31986401715`.

Architecture decision: require all 1,227 generated live-shaped entries to
traverse the exact central-directory parser and live manifest composer before
VR2/VR6. Permit one explicit synthetic normalization of only the three
registered transport digests; entries, schema, version, posture, and source
identity may not change.

Diagnostic decision: run canonical and reversed success plus F02, F03, and F04
cases. Preserve only the outer VR6 and nested allowlisted VR2 codes. Discard
exception text, reasons, rows, paths, person/session/run identities, and values.
Do not import, call, patch, or reuse consumed VR7P.

Evidence decision: cap generated input at 8 MiB, output at 1 MiB, runtime at 30
seconds, and RSS at 256 MiB under one thread with zero retention. No private,
network, archive-payload, neural, target, model, score, FW2, CIL1, retry, or
claim operation is authorized.

Prospective decision: implementation may begin only after this exact
registration is committed, pushed, and both jobs are green. A later private
diagnostic remains a separate all-false Tier C packet and fresh decision.

## 0278 - Accept VR8B Generated Full-Scale Relay At G1

Eligibility decision: implement only after registration
`5607fe895faaacce80bdd14474d211b09d1656d4` passed Base Python job
`95263869003`, Optional Neuro Readers job `95263869149`, and CI
`31987093865`.

Architecture decision: require every one of the 1,227 generated rows to pass
through the exact central-directory parser and live manifest producer before
VR2/VR6. Materialize no member local header or payload. Permit synthetic
normalization of only `transport_body_sha256` and keep consumed VR7P outside
the import and call graph.

Diagnostic decision: accept generated route `MARC2VR8B-G1`. Canonical and
reversed success, F02, F03, and F04 paths preserve only outer
`MARC2VR6-F02` plus the exact allowlisted nested VR2 code. The two complete
replays and 29 direct mutations pass without publishing reasons, rows, paths,
identities, or values.

Identity decision: keep VR6's existing source-provenance hash order-sensitive.
Add a separate generated-cohort digest that excludes source order, local
offsets, and source hashes while binding the selected structural members and
summaries. Do not silently redefine upstream provenance semantics.

Evidence decision: record 4,650,480 generated bytes, 2.421215000009397 seconds,
59,310,080-byte peak RSS, 6,101 aggregate output bytes, one thread, and zero
retention. Every private, neural, model, score, FW2, CIL1, retry, and claim
counter remains zero.

Verification decision: accept the 3,948-test dependency-light suite with 204
skips and the fresh-process 4,019-test optional inventory with 35 skips. Both
are exactly 21 tests above the green registration baseline, and new failures
are zero.

Prospective decision: commit, push, and obtain both green jobs for this exact
implementation before preparing any private diagnostic packet. Do not infer or
relax the consumed F03/F04 branch. Another private read remains a new Tier C
request and fresh packet-bound decision; FW2 and CIL1 remain closed until a
real cohort is frozen.

Proof decision: exact implementation
`d7ce48baca29547ff2385ffe53d247563139439f` passed Base Python job
`95271230358`, Optional Neuro Readers job `95271230485`, and CI `31989817593`.
The generated implementation gate is satisfied. Tier A/B may prepare a new
all-false packet, but no private access exists until that packet is remotely
green and receives a fresh packet-bound decision.

Claim decision: this is generated integration evidence only. It establishes
no real cohort, neural effect, decoding accuracy, language decoding, live
decoding, or thought-to-text capability.

## 0279 - Freeze VR9P As An All-False Two-Layer Private Diagnostic Request

Eligibility decision: prepare the request only after exact VR8B implementation
`d7ce48baca29547ff2385ffe53d247563139439f` passed Base Python job
`95271230358`, Optional Neuro Readers job `95271230485`, and CI `31989817593`,
and proof closeout `1d2ac3a3fb15ebdc01d8aaa23ae8dc74372b85b8` passed Base job
`95272233005`, Optional job `95272232926`, and CI `31990197181`.

Scope decision: bind one future two-stage sequence. A separately green
packet-bound decision must precede generated/mock wrapper work. That exact
wrapper must then be committed, pushed, and green in both jobs before one
target-free read of the registered 418,755-byte structural manifest.

Diagnostic decision: preserve only outer `MARC2VR6-F02` and nested
`MARC2VR2-F03` or `MARC2VR2-F04`. Reject and consume on success, F02, missing
or unknown nested route, source drift, leakage, or another route. Never retain
the reason, row, path, identity, value, private hash, candidate selection, or
cohort.

Resource decision: cap the future command at one thread, one worker, one
numerical job, 650 seconds, less than 256 MiB RSS, at least 15 GiB free disk,
418,755 source bytes, 1 MiB combined output, and zero network, archive-member,
signal, or target bytes. Retries, reruns, resumes, repairs, fallbacks, and
substitutions remain zero.

Authority decision: every request flag is false and every current operation
counter is zero. The current and every earlier `continue` is not retroactive.
Only a fresh message after sole-packet identification may be recorded in a
separate decision. No wrapper, private path, cohort, FW2, CIL1, or claim action
is authorized now.

Proof decision: immutable request
`de8e6dcfb60d78b52429d32c6bdd5f9656ab2d58` passed Base Python job
`95277554517`, Optional Neuro Readers job `95277554619`, and CI `31992178980`.
The request scope is unchanged and every authority flag and operation counter
remains false/zero. Commit, push, and green this additive proof record before
naming VR9P as the sole active Tier C packet.

Claim decision: the request itself performs no private read. Even the future
diagnostic would open no archive member or neural payload and would establish
no neural effect, decoding accuracy, language decoding, live decoding, or
thought-to-text capability.

## 0280 - Bind Fresh Continue Only To The Green VR9P Packet

Eligibility decision: accept the maintainer's exact fresh word `continue` only
because VR9P was the sole active Tier C packet, immutable request `de8e6dc`
passed both jobs in CI `31992178980`, proof closeout `ddc5e85` passed both jobs
in CI `31992563746`, and Codex had identified the exact scope and fresh-decision
gate.

Authenticity decision: preserve the actual eight UTF-8 bytes and SHA-256
`e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad`.
Incorporate the green packet by reference. Do not claim the packet's long text
as a maintainer utterance or infer any broader authority.

Delayed-effect decision: no implementation or private access opens from this
record alone. First commit, push, and green this exact decision in both jobs.
Then generated/mock fixed-path wrapper work may begin. Only after that exact
wrapper is committed, pushed, and green in both jobs may one registered
418,755-byte target-free structural read and one VR6 call occur.

Privacy decision: retain only outer `MARC2VR6-F02` and nested
`MARC2VR2-F03` or `MARC2VR2-F04`. Never retain reason, exception, predicate,
failed value, source row, path, identity, private hash, candidate selection,
private manifest, or cohort. F02, success, missing/unknown nested route, drift,
or leakage consumes and parks the lane.

Boundary decision: no archive member, neural payload, target, derivative,
model, training, prediction, freeze, score, provider, hardware, FW2, CIL1,
release, or scientific claim is authorized. Decision recording performed zero
private or scientific operations.

## 0281 - Implement VR9P As A New Route-Only Fixed-Path Wrapper

Eligibility decision: begin generated implementation only after decision
`4cdd3d3` passed Base Python job `95280728093`, Optional Neuro Readers job
`95280728134`, and CI `31993388608`.

Architecture decision: build a new standard-library module that composes green
VR8B generated parser/producer sources, invokes green VR6 directly, and reuses
the shared proof and readiness validators. Do not import, call, copy, patch,
edit, or proof-bind the consumed VR7P executor.

Qualification decision: require F03 and F04 in canonical and reversed order,
two exact replays, one VR6 call per path, at least 64 direct refusals, no real
or ignored path, and zero retained output. The final matrix made eight VR6
calls and passed 70 direct refusals.

Output decision: permit only a readiness certificate, consumed marker, and
aggregate outer-F02 plus nested-F03/F04 report after exact implementation green
proof. Forbid reason, private context, candidate, selection, private manifest,
and cohort output.

Measured decision: accept generated route `MARC2VR9P-G1` at 1.2402790839987574
seconds, 63,799,296-byte peak RSS, 3,407,792 generated source bytes, 53,528
transient generated output bytes, 6,541 report bytes, and zero retained bytes.

Boundary decision: generated qualification is interface evidence only. It
establishes no real structural route, cohort, neural effect, decoding accuracy,
language decoding, live decoding, or thought-to-text capability. The exact
implementation must pass both remote jobs before one private structural read.

## 0282 - Accept VR9P F03 Localization And Consume The Lane

Execution decision: run only after exact implementation `0dd113a` passed Base
Python job `95285174846`, Optional Neuro Readers job `95285174911`, and CI
`31995078475`. Wait outside the executor until machine load was below the
registered ceiling; do not stop or alter unrelated processes.

Evidence decision: accept aggregate route `MARC2VR9P-R1`, outer
`MARC2VR6-F02`, and nested `MARC2VR2-F03` after one 418,755-byte integrity-
checked strict JSON read and one VR6 call. Interpret F03 only as the committed
row-path/ZIP-BIDS/run-companion/structural-grouping class. Exclude F04 for this
exact execution, but do not infer the failed predicate, value, row, path,
identity, candidate, selection, or cohort.

Resource decision: accept three passing readiness samples, 10.044833040999947
seconds runtime, 39,075,840-byte peak RSS, 6,674 combined output bytes, one
thread, one worker, one numerical job, and zero network or archive payload.

Disposition decision: consume VR9P with no retry, rerun, resume, repair,
fallback, substitution, private reinspection, or output-root reuse. FW2 and
CIL1 remain ineligible. The next safe work is a separately named artifact-only
F03 predicate-decomposition and generated-coverage lane; any new private read
requires a new immutable packet and fresh Tier C decision.

Claim decision: this is an engineering failure-localization result only. No
neural payload, target, model, prediction, or score was accessed, so it proves
no neural effect, decoding accuracy, language decoding, live decoding, or
thought-to-text capability.

## 0283 - Freeze F03 Into Twenty Leaf Predicates Before Any Repair

Eligibility decision: begin only after VR9P result closeout `e7883d4` passed
Base Python job `95288426925`, Optional Neuro Readers job `95288426850`, and CI
`31996295214`. Treat VR9P and all of its private state as consumed.

Evidence decision: bind 14 exact committed inputs totaling 453,477 bytes and
derive only logical implications from tracked code and aggregate records. Do
not open, stat, hash, parse, or infer from a private or ignored path.

Taxonomy decision: freeze exactly 20 F03 leaf predicates. Mark 15 excluded by
committed producer guarantees or exact live entry-kind counts. Preserve five
as unresolved: maximum UTF-8 member-name length, suffix-bearing BIDS identity,
exact lowercase task token, logical companion uniqueness, and four-companion
completeness. Unresolved does not mean observed cause.

Qualification decision: after this registration is remotely green, require a
six-case full-scale generated matrix through the exact parser, producer, VR2,
and VR6 paths. Run canonical and reversed order across two complete replays for
24 calls and 29,448 parser-entry visits, with at least 40 direct refusals and
zero retained generated output.

Resource decision: cap the future generated pass at one thread, one worker,
one numerical job, 30 seconds, less than 256 MiB peak RSS, 16 MiB generated
input, and 1 MiB aggregate output.

Boundary decision: VR10A is artifact-only and generated-only. It authorizes no
private access, consumed-state reuse, archive payload, signal, event, target,
model, training, prediction, score, FW2/CIL1, network, provider, hardware,
release, or scientific claim. Any later private discriminator requires a new
green packet and fresh Tier C decision.

## 0284 - Accept Five Generated F03 Witnesses Without Inferring Private Cause

Eligibility decision: begin only after registration `80175a7` passed Base
Python job `95290665076`, Optional Neuro Readers job `95290665173`, and CI
`31997129703`.

Architecture decision: use a new standard-library module that AST-binds the 20
registered leaves and imports only the green generated relay. Apply each
witness mutation before ZIP construction, then traverse the exact parser,
producer, VR2, and VR6 path. Do not import, call, inspect, or modify VR9P.

Evidence decision: accept local `MARC2VR10A-G1`. Four control paths succeed;
all 20 witness paths return outer `MARC2VR6-F02` and nested `MARC2VR2-F03`
across two orders and two exact replays. This proves witness coverage for all
five unresolved classes, not which class occurred privately.

Resource decision: accept 24 calls, 29,448 parser-entry visits, 6,979,708
generated input bytes, 10,751 aggregate bytes, zero retained bytes,
1.8363693330029491 seconds, 45,072,384-byte peak RSS, one thread, one worker,
and one numerical job.

Verification decision: require 47 direct refusals, 31 focused tests, the
complete 4,042-test local suite with 204 expected skips, Ruff, compilation,
strict registry JSON, and diff hygiene before commit. Remote proof remains
pending until both CI jobs pass the exact implementation commit.

Boundary decision: do not infer a failed private value, row, path, identity,
selection, or cohort from generated behavior. No private, archive, neural,
target, model, prediction, score, FW2/CIL1, network, hardware, release, or
scientific authority opens. A future aggregate-safe discriminator may be
designed only after this exact implementation/result is remotely green.

## 0285 - Close VR10A On Remote Proof And Keep Private Access Closed

Proof decision: accept exact implementation
`84103a5fab86b7c7c8d3cf3af00c9efe3457470c` after Base Python job
`95295212461`, Optional Neuro Readers job `95295212440`, and CI `31998811585`
all passed.

Non-reexecution decision: record remote proof without repeating the generated
qualification or touching any private, ignored, consumed, archive, neural,
target, model, prediction, score, network, hardware, or other-project surface.

Next-design decision: Tier A/B may freeze and generated-qualify a separately
named aggregate-safe five-route discriminator over the exact P03, P15, P16,
P18, and P19 witnesses. Its output ceiling is one predicate-class code plus
aggregate counts, digests, resources, warnings, and zero counters.

Boundary decision: remote green proves implementation integrity, not private
causation or science. No private invocation, F03 relaxation, VR9P reuse, FW2,
CIL1, neural payload, target, model, score, release, or claim is authorized.
Any future private discriminator requires a new green Tier C packet and fresh
decision after the generated discriminator itself is remotely green.

## 0286 - Freeze One Coarse Route For Each Remaining F03 Mechanism

Eligibility decision: begin only after VR10A implementation `84103a5` passed
Base Python job `95295212461`, Optional Neuro Readers job `95295212440`, and CI
`31998811585`, and proof closeout `92d0281` passed Base Python job
`95302164129`, Optional Neuro Readers job `95302164150`, and CI `32001355120`.

Architecture decision: preserve exact validator order and stop at the first
matching unresolved predicate. Bind P03, P15, P16, P18, and P19 to aggregate
routes `MARC2VR10B-R1` through `MARC2VR10B-R5`. Reserve
`MARC2VR10B-G1` for generated clean controls only. Unsupported drift or
ambiguous state refuses instead of publishing another route or a reason.

Qualification decision: after this registration is remotely green, reuse the
six exact VR10A pre-parser cases in canonical and reversed order across two
replays. Require 24 exact parser/producer paths, 24 VR6 calls, 24 discriminator
calls, four copies of every result route, four controls, exact replay, source
immutability, and at least 45 direct refusals.

Privacy decision: output at most one coarse class code plus approved aggregate
hashes, counts, resources, warnings, acceptance gates, and zero counters. Never
emit a value, path, row, row index, subject, session, run, suffix, identity,
selection, cohort, exception text, or per-item outcome.

Boundary decision: VR10B registration is artifact-only and generated-only.
No private executor, consumed-state reuse, F03 relaxation, archive payload,
neural data, target, model, prediction, score, FW2/CIL1, network, hardware,
release, or scientific claim is authorized. Any future private discriminator
requires exact generated implementation/result proof followed by a new frozen
Tier C packet and fresh decision.

## 0287 - Accept Generated Five-Route Separation Without Inferring Private Cause

Eligibility decision: begin only after VR10B registration
`d642eae988bdf5200429fb992e7ff25d778ce949` passed Base Python job
`95308775711`, Optional Neuro Readers job `95308775577`, and CI `32003674374`.

Architecture decision: use a standard-library classifier at the exact
generated parser/producer boundary, preserve registered first-match order, and
expose only G1/R1-R5. Do not add a local-path argument, private wrapper,
network client, model, scorer, or execute mode.

Evidence decision: accept local `MARC2VR10B-G1`. Each of G1 and R1-R5 appears
exactly four times across six cases, two orders, and two replays. The matrix
completed 24 parser/producer paths, 24 VR6 calls, 24 discriminator calls, and
29,448 parser-entry visits with exact replay and source immutability.

Resource decision: accept 6,979,708 generated input bytes, 7,515 aggregate
output bytes, zero retained output, 2.725759166991338 seconds, 44,564,480-byte
peak RSS, and 60 direct refusals under one thread, one worker, and one numerical
job.

Verification decision: require 32 focused tests, the complete 4,074-test base
suite with 204 expected skips, full Ruff, compilation, strict registry JSON,
CLI help/plan, and diff hygiene before commit. Remote proof remains pending
until both CI jobs pass the exact implementation/result commit.

Boundary decision: the result proves generated route separability only. It
does not identify the consumed private F03 cause and opens no private,
consumed-state, archive, neural, target, model, prediction, score, FW2/CIL1,
network, provider, hardware, release, or scientific authority. A future
private discriminator requires a new green Tier C packet and fresh decision
after exact generated implementation/result proof.

## 0288 - Close VR10B On Remote Proof And Keep Private Cause Unknown

Proof decision: accept exact implementation/result
`61bb801689eb2885b1e96aa4b56c86658dc3b333` after Base Python job
`95320325187`, Optional Neuro Readers job `95320325136`, and CI `32007641751`
all passed.

Non-reexecution decision: record remote proof without repeating the generated
qualification or touching any private, ignored, consumed, archive, neural,
target, model, prediction, score, network, hardware, or other-project surface.

Evidence decision: preserve the measured 24-path matrix, four copies of each
G1/R1-R5 route, 60 refusals, replay digest, resources, and zero counters
unchanged. Remote green proves implementation integrity and reproducibility,
not which class occurred privately.

Boundary decision: no private invocation, F03 relaxation, VR9P reuse, FW2,
CIL1, neural payload, target, model, score, release, or scientific claim opens.
Any future private discriminator requires a new immutable Tier C packet and
fresh decision.

## 0289 - Freeze One Future Private Read To Distinguish Five F03 Classes

Eligibility decision: begin only after VR10B implementation `61bb801` passed
Base Python job `95320325187`, Optional Neuro Readers job `95320325136`, and CI
`32007641751`, and proof closeout `808e8ed` passed Base Python job
`95322252607`, Optional Neuro Readers job `95322252650`, and CI `32008293036`.

Scope decision: request one future two-stage sequence. Stage 1 may implement
only a generated/mock fixed-path wrapper after a separate green decision.
Stage 2 may perform one 418,755-byte target-free structural read only after the
exact implementation is remotely green. It may call VR6 once, call VR10B once,
and retain one aggregate R1-R5 route.

Resource decision: freeze one thread, one worker, one numerical job, less than
256 MiB peak RSS, 15 GiB minimum free disk, 650 seconds, 1 MiB combined output,
zero network/archive-member/signal/target bytes, and no retry, rerun, resume,
repair, fallback, or substitution.

Authority decision: this record is an all-false request, not permission. No
decision, implementation, readiness state, private path, consumed VR9P state,
archive payload, neural data, target, model, prediction, score, FW2/CIL1,
release, or claim operation opens. The request and a separate proof closeout
must both become remotely green before the packet may be identified as the
sole Tier C gate. The current and every earlier `continue` is not retroactive.

## 0290 - Record VR11P Request Proof Without Opening Authority

Evidence decision: exact all-false request commit
`6e72c8f797201359777454a750b1dea9704665c0` passed Base Python job
`95326004060`, Optional Neuro Readers job `95326004145`, and CI
`32009557248`. Bind the request-time packet, registry, and test sizes and
SHA-256 values in the request registry.

Scope decision: this is a proof-only metadata update. It changes no requested
path, byte count, route, resource cap, refusal, privacy rule, or future
sequence. All 17 authorization flags remain false and all 18 operation counters
remain zero.

Barrier decision: this proof-closeout commit must itself be pushed and both
required CI jobs must pass before VR11P may be identified as the sole active
Tier C packet. Only a fresh, unambiguous packet-bound maintainer message after
that identification may support separate decision artifacts. The current and
every earlier `continue` remains nonretroactive.

Boundary decision: do not implement the wrapper, create readiness or output
state, touch any private or ignored path, inspect consumed VR9P state, access an
archive member or neural payload, use a target, run a model, predict, score,
open FW2/CIL1, contact a provider or device, release, or upgrade a scientific
claim.

## 0291 - Bind Fresh Short Form To VR11P Without Scope Expansion

Eligibility decision: proof closeout
`136f7b999d3514bd8d62f8dc9e7d7c01b89662f7` passed Base Python job
`95330380822`, Optional Neuro Readers job `95330380918`, and CI
`32011020786` after request `6e72c8f` and CI `32009557248` were already green.
Codex then identified VR11P as the sole active Tier C packet and stated that a
fresh short-form message was required.

Authorization decision: preserve the maintainer's next exact message,
`okay lets continue`, as 18 UTF-8 bytes with SHA-256
`19f24839ccfed02765fd956171b6a3c0bbeea7ba140ca1e130e7d846f0efe436`.
Bind it only to the unchanged packet by reference; do not fabricate a long-form
utterance or infer FW2, CIL1, archive, neural, model, score, hardware, release,
or claim authority.

Order decision: after this exact decision is committed, pushed, and both jobs
are green, Stage 1 may implement and generated-qualify one fixed-path wrapper.
Only after that exact implementation is remotely green may Stage 2 perform one
418,755-byte target-free structural read, one VR6 call, one VR10B call, and one
aggregate R1-R5 report.

Boundary decision: recording this decision performs zero implementation,
readiness, private-path, consumed-state, archive, neural, target, model,
prediction, score, network, hardware, other-project, retry, release, or claim
operations. The decision is ineffective until both remote jobs pass.

## 0292 - Keep VR11P Implementation Proof Separate From Private Execution

Eligibility decision: decision `4fa277121f24dde3f6f7c917ef6c2bb7506134d6`
passed Base Python job `95414004791`, Optional Neuro Readers job `95414004814`,
and CI `32038683203` before the generated/mock implementation began.

Implementation decision: add one standard-library wrapper that reuses the
exact green VR6 and VR10B functions for 24 generated paths and separately
qualifies the fixed readiness/marker/no-follow/report state machine with one
temporary exact-size generated fixture. Do not import, call, patch, copy, or
modify consumed VR9P.

Proof decision: keep `remote_implementation_proof` null in the implementation
milestone. `execute_registered` must refuse before readiness or private-path
operations until a later proof-only closeout binds the exact pushed commit and
both green job IDs. The proof closeout performs no second qualification and no
private operation.

Boundary decision: Stage 1 generated qualification authorizes no fixed private
source access, archive member, neural payload, target, model, prediction,
score, FW2/CIL1, network, hardware, release, or scientific claim. Stage 2 may
proceed only after the separate implementation-proof barrier already required
by decision 0291.

## 0293 - Bind Exact Green VR11P Implementation Before Stage 2

Proof decision: bind final exact implementation
`2093ad542d5043c97e2a3b0cabb605009e66600e`, CI `32041540553`, Base Python
job `95421634020`, and Optional Neuro Readers job `95421633971`. Both jobs are
green, including full base and neuro-enabled suites.

Closeout decision: update only the implementation registry and public handoff
surfaces. Do not rerun generated qualification or alter the module, behavior
test, tracked implementation document, route map, fixed paths, resource caps,
or authorization scope.

Order decision: this proof-only closeout must itself be committed, pushed, and
both jobs green before the one registered Stage 2 structural command. Stage 2
has no retry, rerun, resume, repair, fallback, or substitution.

Boundary decision: proof binding performs zero readiness, ignored-path,
private-source, consumed-VR9P, archive, neural, target, model, prediction,
score, network, hardware, other-project, release, or claim operations. FW2 and
CIL1 remain closed.

## 0294 - Consume VR11P At R2 Without Opening Neural Work

Eligibility decision: proof closeout
`e569bcccfde9bcf5e1116de1b892fed79373c137` passed Base Python job
`95422480212`, Optional Neuro Readers job `95422480363`, and CI
`32041863346` after exact implementation `2093ad5` was already green.

Execution decision: perform the registered Stage 2 command exactly once under
the one-thread, readiness, 256 MiB RSS, 15 GiB free-disk, 650-second, one-read,
and 1 MiB output gates. No retry, rerun, resume, repair, fallback, or
substitution is permitted.

Result decision: record only aggregate route `MARC2VR11P-R2`. Apply the frozen
maximum meaning that R2 reaches F03 class P15, the suffix-bearing BIDS identity
class. Do not retain or infer the failed private value, source row, path,
person, candidate selection, or cohort.

Boundary decision: R2 is a structural engineering result. It opens no archive
member, neural payload, target, model, prediction, score, FW2/CIL1, network,
hardware, release, or scientific claim. A future P15 repair requires a new
prospective artifact-only/generated-only contract before any implementation or
another private read.

## 0295 - Repair Numeric Run Width Without Weakening P15

Standards decision: bind BIDS 1.11.1, whose `run-<index>` entity is numeric and
does not require two-character zero padding. Treat the existing exact-two-digit
selector regex as a prospective generated engineering defect, not as evidence
that the consumed private value used an unpadded run index.

Scope decision: VR12A accepts only one or two ASCII run digits and groups by
base-10 integer. It preserves source-exact selected names and reservation
bytes, exact two-digit Freewill subject/session labels, path/filename identity,
lowercase task, four companions, one lexical run form per companion set,
normalized collision refusal, public 238/195/43 arithmetic, deterministic
split/rank, and the 8 GiB cap.

Order decision: commit, push, and green the registration before implementation.
Then generated-qualify three source spellings in both orders and two replays,
plus at least 36 direct refusals. Only after the exact implementation and
generated result are remotely green may an all-false Tier C confirmation
packet be prepared.

Boundary decision: registration performs zero private, consumed-state, archive,
neural, target, cohort, model, prediction, score, network, provider, hardware,
other-project, FW2/CIL1, release, or scientific-claim operations.

## 0296 - Bind Generated P15 Repair Before Any Private Confirmation

Evidence decision: generated route `MARC2VR12A-G1` passed all 12 registered
success paths and 36 direct refusals. Padded, unpadded, and bundle-consistent
mixed-width sources preserve one semantic selection while retaining distinct
raw and source-exact-name provenance hashes.

Proof decision: exact implementation
`873484aaf270bc5b1499e4b0449c9e8ef138c623` passed Base Python job
`95819297085`, Optional Neuro Readers job `95819297010`, and CI
`32170217284`. Bind those IDs in a proof-only closeout without rerunning the
generated qualification.

Order decision: the proof-only closeout must itself be committed, pushed, and
green in both remote jobs before one all-false Tier C structural-confirmation
packet is prepared. That future packet needs a fresh packet-bound maintainer
decision before any private read. FW2/CIL1 remain later, separate gates.

Boundary decision: this proof closeout performs zero private, consumed-state,
archive, neural, target, cohort, model, prediction, score, network, provider,
hardware, other-project, FW2/CIL1, release, or scientific-claim operations.

## 0297 - Ask One Structural Question Before FW2

Sequence decision: request one two-stage `MARC2-VR12P` lane. A generated/mock
fixed-path wrapper must be implemented and remotely green first. Only then may
one target-free private structural confirmation call the exact VR12A adapter
once and consume at one registered route.

Success decision: R1 may freeze one source-exact private structural cohort
manifest containing 12-19 ranked subjects, 72-114 run bundles, and 288-456 core
members under the unchanged 8 GiB reservation cap. Public output remains
aggregate counts and hashes only.

Resource decision: one thread, one worker, one numerical job, less than 256 MiB
peak RSS, at least 15 GiB free disk, exactly 418,755 private structural bytes,
zero network and new payload bytes, at most 2 MiB output, and zero retry or
rerun.

Boundary decision: packet preparation is all false. R1 would make a separate
FW2 preregistration eligible but does not authorize FW2, CIL1, archive access,
neural data, targets, models, scores, release, or scientific claims.

## 0298 - Bind Fresh Short Form Only To Green VR12P

Authority decision: after request `8165894` and final proof head `5e4354a`
passed both required remote jobs, Codex identified `MARC2-VR12P` as the sole
active Tier C packet and stated its exact two-stage scope and boundaries. Bind
the maintainer's next exact message, `continue`, only to that unchanged packet
by reference. Do not fabricate the packet text as a user utterance or infer
any broader authority.

Order decision: this decision has delayed effect. Commit, push, and green both
required CI jobs before Stage 1 implementation. Then commit, push, and green
the exact generated wrapper and a separate proof-only closeout before one
readiness invocation or private path operation.

Execution decision: after those barriers, permit one 418,755-byte target-free
structural read, one VR12A call, one R1-only private structural cohort manifest,
and one aggregate R1-R6 report under the packet's one-thread, 256 MiB RSS,
15 GiB free-disk, 2 MiB output, zero-network, and zero-rerun limits.

Boundary decision: R1 may make a new FW2 preregistration eligible but does not
authorize FW2 execution. No archive member, neural payload, target, training,
prediction, score, CIL1, release, or scientific claim is authorized.

## 0299 - Keep VR12P Stage 1 Generated And Stage 2 Proof-Gated

Implementation decision: build one dependency-free fixed-path wrapper that
binds the exact green request, decision, and VR12A artifacts. Qualify all three
generated run-index spellings in two orders and two replays, require at least
50 direct refusals, and retain zero generated output.

Failure decision: after a future consumed marker, R2-R6 may emit one aggregate
route and measured counters but no failure detail or private identity. A
private cohort manifest is created only on R1. The private runtime uses its
frozen 650-second cap; generated qualification retains the 45-second cap.

Proof decision: leave `remote_implementation_proof` null in the Stage 1 record.
Commit, push, and green the exact implementation, then separately commit, push,
and green a proof-only closeout before readiness or any private-path operation.

Boundary decision: Stage 1 performs zero real/private, archive, neural, target,
model, prediction, score, FW2/CIL1, network, hardware, other-project, release,
or claim operations. R1 would make a new FW2 preregistration eligible, not
authorize FW2 execution.

Proof-hardening decision: do not use initial green implementation `c76fe20` as
a Stage 2 anchor. Require the proof parser to bind positive CI and job IDs,
the generated G1 route, unchanged scope, no repeated qualification during the
future closeout, zero closeout private operations, the preproof registry
identity, and the exact current artifact-set digest. Requalify generated Stage
1 and re-green the superseding implementation before proof closeout.

## 0300 - Bind Only The Final Proof-Transition-Ready VR12P Bytes

Evidence decision: final implementation `d98a011` passed both required jobs in
CI `32197145780`. Bind its exact commit, job IDs, preproof registry identity,
canonical artifact-set digest, and artifact Git blobs in a proof-only closeout.

Transition decision: the closeout may change only proof state and additive
frontier documentation/tests. It must not change or requalify the wrapper,
implementation artifacts, route table, fixed paths, source identity, caps, or
claim boundary.

Order decision: commit, push, and green this closeout in both jobs before one
readiness invocation or private-path operation. After green, the already
authorized Stage 2 command may run once with no retry.

Boundary decision: proof closeout performs zero private, archive, neural,
target, model, prediction, score, FW2/CIL1, network, hardware, other-project,
release, or claim operations.

## 0301 - Consume VR12P At Aggregate Structural Route R4

Order decision: proof-only closeout `4280aa6` passed Base Python job
`95905146777`, Optional Neuro Readers job `95905146692`, and CI `32197772060`
before the sole registered Stage 2 invocation.

Evidence decision: accept aggregate route `MARC2VR12P-R4` after one exact
418,755-byte target-free structural read, one strict parse, and one VR12A call.
Apply only the frozen maximum meaning: the repaired source refused within the
identity, task, or companion-validation layer. Do not retain or infer the
failed predicate, value, row, path, person, task spelling, companion state,
selection, or cohort.

Repair decision: accepting one- or two-digit run indices was insufficient for
this exact source. Do not patch a consumed executor, relax a predicate, reopen
the source, or rerun the command after seeing R4. A residual-predicate
decomposition must be separately frozen, artifact-only, and generated-only.

Boundary decision: no private cohort manifest exists, so FW2 and CIL1 remain
ineligible. Archive payload, neural signal, targets, models, predictions,
scores, release, and scientific claims remain closed. Another private read is
a new Tier C packet and fresh packet-bound decision.

## 0302 - Freeze Seven Residual R4 Classes Before Another Private Question

Evidence decision: use only committed artifacts to partition VR12P R4. Bind
all 23 exact VR12A F01-F06 refusal call sites, exclude only contract drift, the
live envelope, and generic producer invariants already excluded by committed
proof, and retain seven ordered residual first-failure classes. These classes
are logical possibilities, not observations about the consumed private source.

Qualification decision: after this exact registration is pushed and both CI
jobs are green, permit one dependency-free generated-only implementation with
one success control and seven witnesses in two orders across two replays. It
must make exactly 32 unchanged VR12A calls, observe each route four times,
pass at least 50 direct refusals, retain zero output, and stay within the
frozen resource caps.

Order decision: do not implement before registration proof. Do not prepare a
private discriminator packet before the exact generated implementation and
result are themselves committed, pushed, and remotely green.

Boundary decision: VR13A authorizes no private or ignored path, consumed-state
reuse, archive, neural signal, target, model, prediction, score, provider,
hardware, FW2/CIL1, release, or scientific claim. A later private read remains
a separately frozen Tier C packet and fresh packet-bound decision.

## 0303 - Accept Generated Seven-Route Coverage Without Inferring Private Cause

Order decision: registration `1177174` passed both required jobs in CI
`32424688012` before implementation. Bind only that exact remotely green
registration and the unchanged VR12A adapter.

Implementation decision: accept the generated 32-call matrix after correcting
two witness-order mistakes found by fail-closed qualification. Preserve one
lexical run token for the duplicate-companion route, choose the first absent
run for the bundle-total route, and leave every predecessor byte unchanged.

Evidence decision: accept `MARC2VR13A-G1` as generated engineering evidence.
G1 and R1-R7 each occurred four times across two orders and two replays; all
54 direct refusals passed and no adapter call changed its source. This proves
generated reachability and discrimination only. It does not select a class for
the consumed private R4 result.

Resource decision: accept 13,741,736 generated input bytes, 5,514 aggregate
output bytes, zero retention, 2.401633999950718 seconds, and 36,978,688-byte
peak RSS under one thread/worker/job. Every private and scientific counter is
zero.

Boundary decision: keep remote implementation proof null until this exact
artifact set is committed, pushed, and both jobs are green. No private packet,
private read, cohort, archive, neural signal, target, model, score, FW2/CIL1,
release, or claim is authorized by the generated result.

## 0304 - Bind Exact VR13A Remote Proof Without Repeating Qualification

Proof decision: exact implementation `63a0b8e` passed Base Python job
`96610793887`, Optional Neuro Readers job `96610793714`, and CI
`32426975815`. Bind that commit, both jobs, and the six exact implementation
and preproof-registry Git blobs.

Transition decision: change only remote-proof/status fields, the matching
proof test, and additive frontier documentation. Do not alter or rerun the
module, behavior test, witnesses, route map, measured documents, result,
registration, or resource caps.

Boundary decision: proof closeout performs zero generated qualification,
private, consumed-state, archive, neural, target, model, prediction, score,
provider, hardware, FW2/CIL1, release, or claim operations. After the closeout
itself is remotely green, Tier A may prepare an all-false private discriminator
packet; private access still requires a fresh Tier C decision.

## 0305 - Request Cohort-Or-Class Resolution Without Opening Neural Payload

Sequence decision: prepare one all-false `MARC2-VR13P` two-stage request. Stage
1 is generated/mock fixed-path wrapper qualification only. Stage 2 is one
future target-free structural read only after exact Stage 1 and proof-closeout
green barriers.

Outcome decision: freeze eight aggregate routes before access. R1 means VR12A
passed and may create one private target-free cohort manifest; R2-R8 map the
seven remotely green VR13A residual classes and create no cohort. An unknown,
leaking, inconsistent, or over-budget result consumes and parks the lane.

Resource decision: request one thread/worker/job, 650 private seconds, less
than 256 MiB peak RSS, at least 15 GiB free disk, exactly one 418,755-byte
source open, one VR12A call, at most one residual-map call, 2 MiB output, zero
network/new payload, and no retry, rerun, or resume.

Boundary decision: packet preparation is all false and performs zero private
or ignored-path operations. R1 makes only a separate FW2 preregistration
eligible. No implementation, private read, archive, neural signal, target,
model, score, FW2/CIL1 execution, release, or claim is authorized without a
fresh packet-bound Tier C decision after exact request proof.

## 0306 - Prove The Exact VR13P Request Without Changing Scope

Proof decision: exact request `d55371e` passed Base Python job `96615486644`,
Optional Neuro Readers job `96615486542`, and CI `32428583270`. Bind the three
unchanged request artifacts totaling 30,310 bytes by SHA-256 and Git blob.

Transition decision: add only a proof document, machine proof record, proof
test, and frontier notes. Do not edit the request or authorize either stage.
The closeout has delayed effect until its own commit is pushed and both jobs
are green.

Boundary decision: request proof performs zero implementation, generated
qualification, private, readiness, consumed-state, archive, neural, target,
model, score, FW2/CIL1, release, or claim operations. Only after closeout green
may VR13P be named as the sole active Tier C packet for a fresh decision.

## 0307 - Bind The Fresh Short-Form Decision Only To VR13P

Authorization decision: final proof head `bff3d3f` passed Base Python job
`96618310916`, Optional Neuro Readers job `96618311046`, and CI
`32429569470`. After VR13P was identified as the sole active Tier C packet,
the maintainer's next exact message was `continue`. Preserve those actual eight
UTF-8 bytes and incorporate only the unchanged packet by reference.

Order decision: this decision has delayed effect until its own commit, push,
and two-job green proof. Then Stage 1 may implement and generated-qualify the
fixed wrapper. The exact Stage 1 implementation and a separate proof closeout
must each become remotely green before the one private structural read.

Boundary decision: no archive payload, signal, target, model, prediction,
score, FW2/CIL1 execution, retry, rerun, release, or claim is authorized. R1
makes only a separate FW2 preregistration eligible; R2-R8 retain one aggregate
structural blocker class.

## 0308 - Implement VR13P As A One-Call Generated-Qualified Wrapper

Implementation decision: after decision `fe16400` passed both jobs in CI
`32439821302`, add a new standard-library wrapper without importing or calling
consumed VR11P/VR12P executors. Call VR12A exactly once per source and call the
exact green VR13A residual mapper only after refusal.

Qualification decision: require eight cases, two orders, two replays, 32
matrix paths, one temporary fixed-path success path, all route counts equal,
at least 80 direct refusals, zero retained output, and every real/private or
scientific counter zero. Measured route `MARC2VR13P-G1` passes with 81 direct
refusals under all caps.

Gate decision: keep `remote_implementation_proof` null in the Stage 1 record.
Commit, push, and green the exact implementation, then bind that proof in a
separate proof-only closeout and green it before any readiness or private path
operation.

## 0309 - Harden The VR13P Proof-State Transition Before Closeout

Audit decision: exact implementation `36556e6` passed Base Python job
`96652101274`, Optional Neuro Readers job `96652101052`, and CI
`32441208021`, but the implementation-record test accepted only null proof.
A closeout would therefore fail CI and mutate an allegedly immutable artifact.

Hardening decision: change only that test to accept null or the exact green-
proof shape and update its registry byte binding. Keep the remote proof null.
Do not alter or repeat the wrapper, generated qualification, source identity,
route table, caps, or claim boundary.

Boundary decision: green this hardening before creating the proof closeout.
Qualification, readiness, private, archive, neural, target, model, score,
FW2/CIL1, release, and claim operations remain zero.

## 0310 - Park VR13P After An Invalid Preproof Test Invocation

Context decision: proof-state-hardened implementation `4fb2424` passed Base
Python job `96654430846`, Optional Neuro Readers job `96654430654`, and CI
`32442008002`. During uncommitted local closeout preparation, the focused F01
test mocked readiness and preflight but the executor trusted local proof fields
and returned instead of refusing.

Evidence decision: record only known operations: one 418,755-byte target-free
structural read, one strict parse, and one VR12A call. Do not inspect ignored
output, infer the unretained route, or treat the invalid invocation as evidence.

Disposition decision: restore proof to null and mark VR13P consumed invalid.
No retry, rerun, resume, cleanup, output inspection, FW2/CIL1 eligibility, or
claim is open. Any recovery requires a new frozen Tier C packet and decision.

## 0311 - Request Aggregate-Only Recovery Without Reopening The Source

Scope decision: prepare all-false `MARC2-VR14P` for only the existing aggregate
report. Bind the green incident head and six exact tracked artifacts. Do not
touch `.codex_work` while preparing the request.

Sequence decision: after a fresh packet-bound decision, require generated/mock
wrapper qualification, exact implementation remote proof, and a separate green
proof closeout before one no-follow aggregate-report open capped at 65,536
bytes. No generic path override or retry exists.

Boundary decision: forbid structural source, readiness, marker, private
manifest, archive, neural, target, model, score, FW2/CIL1, network, hardware,
other-project, release, and claim work. R1 would make only a separate private-
manifest recovery packet eligible; R2-R8 recover one structural class.

## 0312 - Prove The Exact VR14P Request Without Changing Scope

Proof decision: exact request `d920e8e` passed Base Python job `96657974654`,
Optional Neuro Readers job `96657974564`, and CI `32443248466`. Bind the three
unchanged request artifacts totaling 13,334 bytes by SHA-256 and Git blob.

Transition decision: add only a proof document, machine proof record, proof
test, and frontier notes. Do not edit the request, authorize either stage, or
touch `.codex_work`. The closeout has delayed effect until its own commit is
pushed and both jobs are green.

Boundary decision: proof closeout performs zero implementation, generated
qualification, ignored-path, aggregate-report, structural-source, private-
manifest, archive, neural, target, model, score, FW2/CIL1, release, or claim
operations. Only after closeout green may VR14P be named as the sole active
Tier C packet for a fresh decision.

## 0313 - Bind Fresh Maintainer Words Only To VR14P

Authorization decision: proof closeout `3274a72` passed Base Python job
`96659529617`, Optional Neuro Readers job `96659529824`, and CI `32443804353`.
After sole-gate identification, preserve the maintainer's exact 96 UTF-8 bytes
and bind only the unchanged VR14P packet by reference.

Scope decision: the message's continuous-approval wording does not authorize a
future packet, neural payload, target, model, score, release, or claim. First
green this decision; then generated-qualify and green the fixed aggregate
reader; then green a separate proof closeout before the one aggregate open.

Boundary decision: decision recording performs zero implementation, generated
qualification, ignored-path, aggregate-report, structural-source, private-
manifest, archive, neural, target, model, score, FW2/CIL1, release, or claim
operations. R1 makes only a separate private-manifest packet eligible.

## 0314 - Implement VR14P With A One-Shot Pre-Path Gate

Implementation decision: after decision `60b97ea` passed both jobs in CI
`32444425790`, add a standard-library fixed `plan`, `qualify`, `inspect`, and
`execute` module for the exact VR13P aggregate schema and R1-R8 route allowlist.

Safety decision: require explicit one-shot arming before proof loading, then a
tracked clean proof registry and exact owned-artifact verification before any
ignored path. This prevents ordinary focused or CI tests from reproducing the
VR13P preproof incident merely because proof metadata exists locally.

Qualification decision: require 32 deterministic route/order/replay paths,
strict canonical JSON, all eight routes exactly four times, at least 80 direct
refusals, one temporary fixed-path roundtrip, zero retained output, and zero
real/private/scientific operations. Measured `MARC2VR14P-G1` passes 89 direct
refusals under every cap.

## 0315 - Separate VR14P Implementation Proof From Execution Activation

Proof decision: exact implementation `046013a` passed Base Python job
`96664169190`, Optional Neuro Readers job `96664169147`, and CI `32445483857`.
Bind its registry and five owned artifacts totaling 68,625 bytes without
rerunning qualification or touching `.codex_work`.

Activation decision: after this proof closeout itself is remotely green, add a
separate tracked-clean activation proof that binds both green heads. Green that
record before one-shot arming. This makes local uncommitted proof edits
insufficient and keeps CI tests unable to access ignored output.

Boundary decision: proof closeout performs zero aggregate-report, recovery-
output, source, private-manifest, archive, neural, target, model, score,
FW2/CIL1, retry, release, or claim operations.

## 0316 - Activate VR14P Only Through A Tracked Clean Record

Proof decision: closeout `f352c1b` passed Base Python job `96665759734`,
Optional Neuro Readers job `96665759548`, and CI `32446071998`. Bind those
exact proofs in the fixed implementation-proof path expected by the reader.

Delayed-effect decision: merely creating or committing the activation record
does not open the aggregate. Its exact commit must be pushed and both jobs must
pass before explicit one-shot arming.

Scope decision: activation performs zero ignored-path operations. The later
one-shot may open only the registered aggregate report once and write one
receipt; structural source, private manifest, archive, neural, target, model,
score, FW2/CIL1, retry, release, and claim work remain closed.

## 0317 - Consume VR14P At Aggregate Route R2

Execution decision: activation `6bfff69` passed Base Python job
`96667351062`, Optional Neuro Readers job `96667350910`, and CI
`32446635433`. The sole armed command then opened and strict-parsed exactly
1,543 aggregate bytes once and wrote one 1,945-byte receipt.

Result decision: `MARC2VR13P-R2` means only the suffix-bearing BIDS identity
structural class. It does not expose the failed value, predicate, row, path,
identity, person, run, task, selection, or cohort.

Boundary decision: VR14P is consumed without retry or reinspection. The next
safe lane is artifact-only and generated-only decomposition; private manifest,
source, archive, neural, target, model, score, FW2/CIL1, release, and claims
remain closed.

## 0318 - Decompose P15 With Generated Grammar Witnesses

Proof decision: registration `185fbc5` passed Base Python job `96670618009`,
Optional Neuro Readers job `96670617843`, and CI `32447836662` before
implementation. Bind the exact repaired regex and P15 guard without modifying
VR12A.

Implementation decision: classify fifteen ordered suffix-identity grammar
failures plus one multiple-class state using only generated 1,227-row sources.
Require 68 exact VR12A calls, exact F03/P15 reachability for every single-class
witness, order/replay agreement, source immutability, and at least 70 direct
refusals. Local `MARC2VR15A-G1` passes every gate under all resource caps.

Boundary decision: generated route reachability does not identify the consumed
private class. Keep private and ignored paths, structural source, archives,
neural payloads, targets, models, predictions, scores, FW2/CIL1, release, and
claims closed. Remote-proof the exact implementation before preparing any new
all-false Tier C packet.

## 0319 - Close VR15A With Exact Remote Proof

Proof decision: exact implementation `bfb0dcb` passed Base Python job
`96674484190`, Optional Neuro Readers job `96674484279`, and CI
`32449260503`. Bind the exact commit and seven Git blobs in both machine
records.

Zero-repeat decision: update only proof metadata, completed status, the proof
test, and frontier notes. Do not rerun the generated qualification or perform
any ignored-path, private-source, archive, neural, target, model, prediction,
score, FW2/CIL1, network, hardware, release, or claim operation.

Boundary decision: remote proof makes only an all-false private discriminator
packet eligible for Tier A preparation. It does not authorize its future
private read, identify the consumed class, freeze a cohort, or establish any
scientific result.

## 0320 - Request One Sixteen-Route P15 Private Discriminator

Scope decision: prepare all-false `MARC2-VR15P` for one future two-stage
sequence. Stage 1 may later implement a generated/mock fixed-path wrapper;
Stage 2 may later read the exact 418,755-byte target-free structural source once
and emit only one R1-R16 aggregate grammar class.

Sequence decision: require the request and a non-scope-changing request proof
to be remotely green before sole-gate identification and a fresh maintainer
decision. After that decision, require exact Stage 1 and proof-closeout green
barriers before the one private open. Earlier or standing approvals are not
retroactive.

Boundary decision: packet preparation performs zero ignored/private path,
source, archive, neural, target, model, prediction, score, FW2/CIL1, network,
hardware, retry, release, or claim operations. It requests no cohort creation
and grants no authority now.

## 0321 - Remote-Prove The Unchanged VR15P Request

Proof decision: exact all-false request `08cef4b` passed Base Python job
`96677085658`, Optional Neuro Readers job `96677085404`, and CI
`32450174692`. Bind its three unchanged artifacts totaling 29,112 bytes by
size, SHA-256, and Git blob.

Zero-operation decision: this closeout does not edit the request, implement or
qualify a wrapper, inspect readiness, or touch a private/Git-ignored path.
Every request authorization field remains false and every operation counter
remains zero.

Sequence decision: the closeout has delayed effect until its own exact commit
is pushed and both jobs are green. Only then identify VR15P as the sole Tier C
packet for fresh packet-bound maintainer words; standing approval is not
retroactive. FW2, CIL1, archive, neural, target, model, score, release, and
claim work remain closed.

## 0322 - Bind Fresh Short-Form Authorization To VR15P Only

Authorization decision: after proof head `8873796` passed Base Python job
`96678759155`, Optional Neuro Readers job `96678759451`, and CI
`32450773951`, Codex identified VR15P as the sole active Tier C packet. The
maintainer's next exact message was the eight UTF-8 bytes `continue`.

Scope decision: bind those actual bytes only to the unchanged green two-stage
packet. Stage 1 may implement and generated-qualify the fixed wrapper after
this decision is remotely green. Stage 2 may perform its sole target-free
418,755-byte structural read only after exact Stage 1 and a separate proof
closeout are each remotely green.

Boundary decision: standing or future authority is not inferred. At decision
recording, implementation, readiness, private/ignored-path, archive, neural,
target, model, prediction, score, FW2/CIL1, network, hardware, release, and
claim operations remain zero.

## 0323 - Implement The VR15P Generated Private Discriminator

Proof decision: decision `fc694a6` passed Base Python job `96680587357`,
Optional Neuro Readers job `96680587199`, and CI `32451448725` before Stage 1.
Bind only the exact green two-stage packet and keep private execution closed.

Implementation decision: add one standard-library fixed-path wrapper with
`plan`, `qualify`, `inspect`, and `execute` surfaces. Generated qualification
must cover 17 cases, two source orders, two replays, 68 exact VR15A calls, all
G1/R1-R16 routes four times each, and 111 direct refusals without retaining a
generated source or output.

Boundary decision: `execute` requires exact implementation and proof-closeout
records, a tracked-clean tree, and explicit one-shot arming before readiness or
private preflight. Stage 1 performs zero private/ignored-path, structural-source,
archive, neural, target, model, prediction, score, FW2/CIL1, network, hardware,
other-project, release, or claim operation.

## 0324 - Make VR15P Resource Replay Runner-Independent

Failure decision: preproof commit `1f7a6a2` did not cross the remote barrier.
Both CI suites rejected the qualification replay because a live process RSS
high-water mark is runner-dependent, even when the replay uses a child Python
process. Treat CI `32453575446` as failed proof and keep Stage 2 closed.

Correction decision: inject the frozen measured 50,135,040-byte RSS value only
into deterministic test replay. Keep the production CLI's live RSS reader and
the direct exact-cap refusal mutations unchanged. This changes no generated
matrix, private contract, route, threshold, source, or scientific boundary.

Sequence decision: rerun focused and complete local verification, commit and
push the corrected exact artifacts, and require a fresh green Base and Optional
CI pair. Do not reuse the failed proof or perform any private operation.

## 0325 - Close VR15P Stage 1 With Exact Remote Proof

Proof decision: corrected exact Stage 1 `28a734d` passed Base Python job
`96688236516`, Optional Neuro Readers job `96688236752`, and CI `32454196219`.
Bind the proof-state registry and its five owned artifacts by exact path, byte
count, SHA-256, and Git blob: six artifacts totaling 77,152 bytes.

Zero-repeat decision: transition only the implementation proof metadata, its
record test, and its tracked inspection-state assertion. Do not rerun generated
qualification, arm `execute`, inspect readiness, or perform any private/ignored-
path or scientific operation.

Sequence decision: this closeout has delayed effect until its own exact commit
passes both remote jobs. Then create and remotely prove one separate tracked-
clean activation record before the sole armed private command. FW2 and CIL1
remain closed.

## 0326 - Bind The VR15P Tracked-Clean Activation

Proof decision: exact closeout `2acfb33` passed Base Python job `96690180933`,
Optional Neuro Readers job `96690181096`, and CI `32454892777`. Bind its three
exact artifacts totaling 9,513 bytes by size, SHA-256, and Git blob.

Activation decision: transition the tracked implementation proof state to both
green barriers and freeze one later exact one-shot command: one 418,755-byte
target-free structural read, one strict parse, one VR15A call, one nested VR12A
call, and one aggregate R1-R16 route. No route may freeze a cohort.

Boundary decision: activation itself performs zero private/ignored-path,
readiness, structural-source, archive, neural, target, model, prediction,
score, FW2/CIL1, network, hardware, release, or claim operation. Its effect is
delayed until this exact activation commit passes both remote jobs.

## 0327 - Make VR15P Historical Proof Tests Shallow-Checkout Safe

Failure decision: activation commit `64fa114` did not cross the remote barrier.
Base Python and Optional Neuro Readers in CI `32455530795` both passed the
VR15P implementation tests, then failed two proof-history tests because the
default GitHub Actions checkout does not contain parent commit `2acfb33`.
Treat that run as failed activation proof and keep the private stage closed.

Correction decision: assert the already frozen role, path, byte, SHA-256, and
Git-blob tuples directly in the two historical proof tests. The exact tuple
values remain unchanged; the correction removes only an accidental dependency
on historical Git objects being present in a shallow checkout.

Boundary decision: change no implementation/runtime byte, route, threshold,
source, authorization, output, or scientific contract. Require a fresh green
Base and Optional CI pair before the sole private command.

## 0328 - Consume VR15P At The Run-Token Width Class

Proof decision: portable activation `a9ebef4` passed Base Python job
`96694803139`, Optional Neuro Readers job `96694803152`, and CI `32456531938`.
Only then issue the exact one-shot arm.

Result decision: record consumed route `MARC2VR15P-R15` as the run-token width
class. This falsifies only VR12A's one-or-two-ASCII-digit width assumption; do
not infer or retain the private token, filename, path, row, identity,
participant, selection, or cohort.

Boundary decision: VR15P has no retry or reinspection and creates no cohort.
The next safe lane is an artifact-only/generated-only variable-width numeric
run-index repair. Any private, neural, target, model, score, FW2, or CIL1 work
still requires a separate Tier C packet and decision.

## 0329 - Preregister The Standards-Aligned Variable-Width Repair

Standards decision: bind BIDS 1.11.1's numeric-index semantics and arbitrary
leading-zero allowance. Treat lexical run width as distinct from semantic run
identity, while retaining the dataset's semantic runs 1/2/3.

Repair decision: add a new generated-only VR16A adapter rather than modify a
consumed executor. Accept `[0-9]+` only inside the existing 1,024-byte name
cap, canonicalize before integer conversion, preserve source-exact names, and
retain mixed-spelling and normalized-collision refusals.

Sequence decision: require the exact registration commit to pass Base and
Optional CI before implementation. Do not touch private or consumed state,
freeze a cohort, or open neural/FW2/CIL1 work.

## 0330 - Qualify The Variable-Width Repair On Generated Sources

Proof decision: registration `7dba59355ca45c8ab5eafb9d8b7757edfc9755c5`
passed Base Python job `96699811237`, Optional Neuro Readers job
`96699811051`, and CI `32458280634` before implementation.

Domain decision: permit every syntactically valid numeric run in the complete
source inventory, then enforce semantic runs 1/2/3 only on the frozen selected
fit/held-out rows. This corrects an implementation-stage conflation without
changing the registered selected split or BIDS numeric-index rule.

Result decision: record generated `MARC2VR16A-G1` after 24/24 paths, 50 direct
refusals, deterministic semantic identity, source-exact names and reservations,
2.224372999975458 seconds, 34,717,696-byte peak RSS, and zero retention.

Boundary decision: this is generated engineering evidence only. Require exact
remote implementation proof before preparing a separate all-false private
confirmation packet. Real/private, cohort, archive, neural, target, model,
score, FW2/CIL1, release, and scientific-claim authority remain absent.

## 0331 - Close VR16A With Exact Remote Proof

Proof decision: exact implementation `6f92b84c7be67848c7d09b567f13b08a14d33f5c`
passed Base Python job `96704807926`, Optional Neuro Readers job
`96704808178`, and CI `32459984049`. Bind the six implementation artifacts by
their exact Git blobs without rerunning qualification.

Boundary decision: change only proof metadata and frontier documentation.
Perform zero private/ignored-path, consumed-state, structural-source, archive,
neural, target, model, score, FW2/CIL1, network, hardware, release, or claim
operation.

Sequence decision: commit, push, and green this proof-only closeout. Only then
may Tier A prepare an all-false private structural-confirmation packet; the
future private read itself remains Tier C and separately decision-bound.

## 0332 - Prepare The VR16P All-False Confirmation Request

Scope decision: bind one future two-stage sequence around the exact green
VR16A adapter. Stage 1 may later build and generated-qualify a fixed-path
wrapper; Stage 2 may later make one target-free structural open and one VR16A
call only after exact green implementation and proof closeout.

Outcome decision: permit only R1 to freeze a bounded source-exact cohort.
R2-R6 retain aggregate precondition, source, identity/companion,
selection/storage, or privacy/resource failure classes and consume with no
retry or reinspection.

Authority decision: keep every request authorization false and every
preparation counter zero. The current `continue` is not retroactive authority.
Require request and proof-closeout remote green, sole-gate identification, and
fresh packet-bound maintainer words before implementation.

## 0333 - Close The VR16P Request With Exact Remote Proof

Proof decision: exact request `619469a795a7044a4bbb77cef8986e0a7744473f`
passed Base Python job `96709074413`, Optional Neuro Readers job
`96709074203`, and CI `32461465238`. Bind the three unchanged request artifacts
totaling 32,234 bytes by exact byte count, SHA-256, and Git blob.

Boundary decision: this closeout changes no request, implements no wrapper,
and performs zero readiness, ignored-path, private-source, archive, neural,
target, model, score, FW2/CIL1, network, release, or claim operation.

Sequence decision: require the closeout's own exact commit to pass both remote
jobs. Only then identify VR16P as the sole Tier C packet; require the
maintainer's next fresh packet-bound words and a remotely green decision before
Stage 1 implementation.
