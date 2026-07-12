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
