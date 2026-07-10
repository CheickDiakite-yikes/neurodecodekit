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
