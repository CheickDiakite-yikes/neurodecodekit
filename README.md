# NeuroDecodeKit Starter

**Mission:** make non-invasive neural language decoding research easier to start, reproduce, compress, and explain.

This starter repo is intentionally not a state-of-the-art Brain2Qwerty replication. It is a clean first loop for turning a huge neuroimaging release into a small, inspectable, benchmark-ready developer experience.

The first principle is simple:

```text
list files → choose tiny slice → cache small windows → run honest baselines → report CER/WER → demo errors
```

The thesis: the fastest path to value is not a giant model first. It is the access layer that lets smart builders avoid downloading hundreds of gigabytes before they can think.

## What is included

```text
neurodecodekit_starter/
  AGENTS.md                         # instructions for Codex / coding agents
  README.md                         # repo overview and quickstart
  pyproject.toml                    # package metadata and optional dependency groups
  docs/
    CODEX_HANDOFF.md                # exact next loop for Codex
    RESEARCH_BRIEF.md               # current research map and source notes
    DATA_ACCESS_PLAN.md             # selective download + manifest strategy
    EXPERIMENTS.md                  # first experiments and acceptance criteria
    RISK_AND_ETHICS.md              # non-clinical scope, privacy, licensing guardrails
    DECISIONS.md                    # architectural decisions log
  prompts/
    CODEX_START_PROMPT.md           # copy/paste prompt to continue this repo in Codex
  src/neurodecodekit/
    cli.py                          # lightweight CLI, works without heavy neuro deps
    datasets/manifest.py            # SpanishBCBL path parser + manifest schema
    datasets/hf_access.py           # optional Hugging Face listing/download helpers
    preprocess/windowing.py         # event-aligned window extraction utility
    evaluation/metrics.py           # CER/WER and Levenshtein utilities
    evaluation/keyboard.py          # simple QWERTY keyboard-distance metric
    training/synthetic.py           # synthetic shard generator for CI/dev loop
    models/template_classifier.py   # tiny no-LLM baseline for sanity checks
    demo/app.py                     # artifact-backed local Gradio evidence console
  tests/                            # pure-Python unit tests
  configs/                          # starter experiment configs
```

## Quickstart

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
```

Run the tiny local smoke loop without downloading any brain data:

```bash
neurodecode eval-text --target "HOLA MUNDO" --prediction "HOLA MUNCO"
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 64 --channels 8 --times 25
neurodecode load-cache --cache cache/synthetic_tiny.npz --metadata-out cache/synthetic_tiny.metadata.json
neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md
```

The synthetic shard is the current CI-friendly smoke loop. It verifies cache
writing, cache loading, report writing, and metric plumbing without requiring
MNE, SciPy, Hugging Face access, or any Brain2Qwerty/SpanishBCBL files.
`--identity-smoke` uses cache labels as predictions and is explicitly a
plumbing check, not a model result.

Run the optional local evidence console from compact existing artifacts:

```bash
pip install -e '.[demo]'
neurodecode demo --host 127.0.0.1 --port 7860
```

The demo shows held-out synthetic examples and aggregate-only real metrics. It
does not train or run a model, display real sentence text, fetch data, or claim
calibrated confidence. See `docs/LOOP_17_HONEST_LOCAL_DEMO.md`.

## Build notes and handoff trail

This project is being built as a sequence of small loops, with each loop leaving
behind a runnable artifact and a plain-English handoff. The current build
journal is `docs/BUILD_NOTES.md`.

That journal captures:

- loop status and local commits
- commands that were verified
- managed-workstation blockers, including blocked external push/workbook paths
- data-access guardrails
- case-study notes and next-agent closeout steps

If work is interrupted, prefer updating the journal and marking the loop
pending over implying that a loop is complete.

Inspect SpanishBCBL-style paths using a local file list:

```bash
cat > /tmp/spanishbcbl_files.txt <<'EOF'
pinet2024_public/MEG/FIF/S1/block1.fif
pinet2024_public/MEG/logs/S1_block1.mat
pinet2024_public/EEG/EEG/S2/eeg.vhdr
EOF

neurodecode manifest-from-paths --paths /tmp/spanishbcbl_files.txt --out /tmp/manifest.jsonl
neurodecode inspect-manifest --manifest /tmp/manifest.jsonl
neurodecode select-tiny --manifest /tmp/manifest.jsonl --out /tmp/tiny_selection.json --max-files 4 --max-total-gb 2
neurodecode download-selection --selection /tmp/tiny_selection.json --local-dir data/spanishbcbl_tiny
```

Manifest v1 accepts plain paths, JSONL rows with `path` and optional
`size_bytes`, or tab-separated `path<TAB>size_bytes` rows. `inspect-manifest`
prints file-family counts, explicit parser warnings for unknown rows, and
raw-to-log candidate pairing summaries before any download is attempted.
`select-tiny` is safety-capped by default and writes a planned download file
with exact paths, file-count limits, known-byte totals, and unknown-size
warnings.

Optional real Hugging Face listing, when online and authenticated if needed:

```bash
pip install -e '.[hf]'
neurodecode list-hf-files --repo-id bcbl190626/SpanishBCBL --out data/spanishbcbl_files.txt
neurodecode manifest-from-paths --paths data/spanishbcbl_files.txt --out data/spanishbcbl_manifest.jsonl
neurodecode select-tiny --manifest data/spanishbcbl_manifest.jsonl --out data/tiny_selection.json --max-files 4 --max-total-gb 2
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny  # dry-run by default
```

To actually download the selected files, first read the dry-run plan. Then run:

```bash
neurodecode download-selection --selection data/tiny_selection.json --local-dir data/spanishbcbl_tiny --execute
```

If the manifest did not contain file sizes, `--execute` fails safely until you
either rebuild the manifest with sizes or add `--allow-unknown-size` after
reviewing the exact file list and file-count cap.

## Real window extraction from one downloaded block

Once you have explicitly downloaded one `.fif` block and one matching `.mat`
behavior/log file, install the optional neuro dependencies and extract a tiny
event-aligned cache:

```bash
pip install -e '.[neuro]'

neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../S1_block1.mat \
  --out cache/b2qmini_s1_block1.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-events 200
```

`extract-windows` does not download anything. It only reads the two paths you
provide. The command reports events found, events kept, edge/max-event drops,
output shape, sampling rate, channel count, raw file size, output cache size,
and parser warnings.

The `.npz` cache contains:

```text
windows            [events, channels, timepoints] float32
labels             per-event labels when parsed, blank otherwise
event_start_sec    event timestamps in seconds
event_source_index source row/index from the parsed log
channel_names      channel names after picking/resampling
metadata           JSON with source paths, extraction params, parser notes
```

All current caches are written as B2Q-mini cache schema v0. The stable loader:

```bash
neurodecode load-cache --cache cache/b2qmini_s1_block1.npz --metadata-out cache/b2qmini_s1_block1.metadata.json
```

prints shape, dtype, label coverage, source files, warnings, and the
transformation trail. The optional JSON sidecar is intended for quick review and
experiment reports; the `.npz` remains the source of truth.

## Metrics and reports

Loop 5 is closed. The `neurodecode report` implementation and tests are present,
and the closeout verification passed on 2026-07-01.

Write a report from one-target-per-line text files:

```bash
neurodecode report \
  --targets cache/targets.txt \
  --predictions cache/predictions.txt \
  --cache cache/b2qmini_s1_block1.npz \
  --out-json outputs/run_001/metrics.json \
  --out-md outputs/run_001/report.md \
  --run-name run_001 \
  --split synthetic-smoke
```

The report includes CER, WER, exact-match rate, keyboard-distance diagnostics,
example rows, cache/storage metadata when provided, runtime, and warnings. A
real neural result should always be compared against a no-brain baseline in a
later report.

Synthetic report smoke path:

```bash
neurodecode make-synthetic-shard --out cache/synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report \
  --cache cache/synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/synthetic_report.json \
  --out-md cache/synthetic_report.md \
  --run-name synthetic_identity_smoke \
  --split synthetic-smoke
```

`--identity-smoke` copies cache labels into predictions and emits an explicit
warning. It is useful for proving report plumbing, but it is not a decoder or a
baseline result.

Run the no-brain prior-only baseline:

```bash
neurodecode prior-baseline \
  --cache cache/synthetic_tiny.npz \
  --out-predictions cache/prior_predictions.txt \
  --out-json cache/prior_report.json \
  --out-md cache/prior_report.md \
  --run-name synthetic_prior_most_frequent \
  --split synthetic-smoke
```

`prior-baseline` deliberately ignores neural windows. It predicts from target
priors only and writes the same report format, with explicit warnings that no
neural signal was used. For real experiments, pass `--train-targets` or
`--train-cache` so the prior is fit on training labels rather than eval labels.

Run the tiny neural-window template baseline:

```bash
neurodecode template-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.5 \
  --out-predictions cache/template_predictions.txt \
  --out-json cache/template_report.json \
  --out-md cache/template_report.md \
  --run-name synthetic_template_nearest_centroid \
  --split synthetic-holdout
```

`template-baseline` uses cache windows, but no deep learning. With one cache it
creates a deterministic stratified holdout split; for cleaner real experiments,
use `--train-cache` and `--eval-cache`.

Run the optional tiny ConvNet neural-window baseline:

```bash
pip install -e ".[ml]"

neurodecode tiny-conv-baseline \
  --cache cache/synthetic_tiny.npz \
  --train-fraction 0.75 \
  --epochs 30 \
  --batch-size 16 \
  --learning-rate 0.02 \
  --out-predictions cache/tiny_conv_predictions.txt \
  --out-json cache/tiny_conv_report.json \
  --out-md cache/tiny_conv_report.md \
  --run-name synthetic_tiny_conv \
  --split synthetic-holdout
```

`tiny-conv-baseline` is behind the optional `ml` extra because it uses PyTorch.
It defaults to CPU and one Torch thread. The command is a smoke baseline for
tiny caches, not a production decoder. On a base install it should fail with a
clear `pip install -e '.[ml]'` message.

## Continuous sentence CTC

Loop 9 adds a separate variable-length sentence cache and optional CTC model.
The synthetic path requires no neuroimaging files:

```bash
neurodecode make-synthetic-sentence-cache \
  --out cache/loop9_synthetic_sentences.npz \
  --sentences 96 \
  --channels 6

neurodecode tiny-ctc-baseline \
  --cache cache/loop9_synthetic_sentences.npz \
  --epochs 60 \
  --num-threads 1 \
  --out-json cache/loop9_synthetic_ctc_report.json \
  --out-md cache/loop9_synthetic_ctc_report.md
```

The CTC report always includes a no-brain prior comparator. Synthetic token
pulses are intentionally easy and validate only sequence plumbing.

For one already downloaded and alignment-validated FIF/MAT pair:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../block1_list1.mat \
  --out cache/b2qsentence_s1_block1_16ch_100hz.npz \
  --sfreq 100 \
  --picks meg \
  --max-channels 16

neurodecode inspect-sentence-cache \
  --cache cache/b2qsentence_s1_block1_16ch_100hz.npz \
  --metadata-out cache/b2qsentence_s1_block1_16ch_100hz.metadata.json
```

This extraction uses first key through ENTER with context, 0.5-45 Hz filtering,
a 50 Hz notch, 100 Hz resampling, robust scaling, and explicit input/target
lengths. It does not download data and it does not turn one block into an
honest train/eval result. See `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.

## Sampling-rate sweep

Loop 10 compares independent 100/50/25 Hz sentence-cache extractions without
training on the single real block:

```bash
neurodecode sampling-rate-sweep \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../block1_list1.mat \
  --out-dir cache/loop10_s21_sampling_rate_sweep \
  --rates 100 50 25 \
  --picks meg \
  --max-channels 16
```

Rates run sequentially in isolated one-thread processes. The JSON/Markdown
report verifies exact trial/text/channel identity and compares bytes, runtime,
peak RSS, effective bandwidth, timing quantization, signal summaries, and exact
CTC length margins. The real S21 result reduces cache bytes to 50.9% at 50 Hz
and 25.9% at 25 Hz, but it intentionally selects no rate without a second
block/session accuracy protocol. The exact official v2 kernel-16, stride-4
temporal reducer is CTC-length feasible for all 66 rows at 100 and 50 Hz, but
none at 25 Hz; a 25 Hz branch needs an architecture change. See
`docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

## Channel/sensor subset sweep

Loop 11 replaces the arbitrary first-channel smoke subset with a geometry-aware
102-magnetometer base and cache-only nested subset comparisons:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/.../block1.fif \
  --events data/spanishbcbl_tiny/.../block1_list1.mat \
  --out cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --sfreq 100 \
  --picks mag \
  --max-channels 102

neurodecode channel-subset-sweep \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --out-dir cache/loop11_s21_channel_subset/subsets \
  --counts 76 51 25 16 8 \
  --strategies spatial-fps variance random first \
  --seed 17 \
  --max-output-mb 128
```

The real S21 run writes 20 validated subset caches plus metadata sidecars in
70.3 MiB. Spatial farthest-point sampling has the best whole-array coverage at
every count; same-block variance ranking retains the largest post-scaling
marginal variance share. At 16 channels their overlap is only 2 channels, so
both remain candidates for a future held-out decoder test. No channel count,
CER/WER result, anatomical ROI, or OPM-equivalence claim is made. See
`docs/LOOP_11_CHANNEL_SENSOR_SUBSET_SWEEP.md`.

## Precision/storage sweep

Loop 12 compares five physical signal representations on the fixed 102-
magnetometer base plus the FPS-16 and variance-16 candidates. It does not
download data or train a decoder:

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

The real run writes 15 validated representation caches plus inspectable
sidecars in 34.4 MiB. Qint16 is about 50% smaller than the float32
representation with at most 0.0037% relative RMSE; qint8 is about 81% smaller
with at most 0.9531% relative RMSE. All non-signal arrays, semantic metadata,
shapes, and zero padding match exactly, and no source value falls outside the
fixed integer range. Float32 remains the default because reconstruction
fidelity is not retained CER/WER. Packed caches decode to float32 for the
current model interface, so this is storage/load evidence, not integer-only
inference. See `docs/LOOP_12_PRECISION_STORAGE_SWEEP.md`.

## Lazy-backend gate

Loop 13 measures whether current NPZ access justifies another cache backend.
It reuses nine real standard/packed S21 caches and runs complete, 1-row, and
8-row access in isolated one-thread workers:

```bash
neurodecode lazy-backend-gate \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
          cache/loop12_s21_precision_storage/base_102mag_100hz__qint16.npz \
          cache/loop12_s21_precision_storage/base_102mag_100hz__qint8.npz \
  --out-dir cache/loop13_lazy_backend_gate
```

The largest tested cache is 10.1 MiB, the slowest full-load median is 60.386
ms, the slowest partial median is 53.634 ms, and the highest worker peak RSS is
140.6 MiB. Every decoded-signal hash matches exactly. NPZ partial access is
relatively inefficient because the complete compressed signal member is
materialized before slicing, but current absolute costs remain below the
declared budgets. Zarr was not installed or benchmarked. Keep bounded per-block
NPZ files and revisit a chunked backend only when a recorded threshold or
repeated subarray workflow is reached. See
`docs/LOOP_13_LAZY_BACKEND_GATE.md`.

## Split protocol v1

Loop 14 mirrors
the released Brain2Qwerty v2 deterministic sentence-text assignment while
recording the exact algorithm, ratios, float seed, text-normalization mode,
and stable membership hashes. It now assigns membership before robust scaling
and fits scaler statistics on train sentence rows only:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --picks mag --max-channels 102 \
  --scaler-fit-scope train \
  --split-text-normalization official-exact
```

The current 66 unique reference texts partition into 55 train, 6 validation,
and 5 test rows with zero requested-group or canonical-text crossings. The
replacement cache passes strict fit-scope validation. A signal-free prior and
one fixed 2,908-parameter CTC run use exactly the same membership. Test CER is
0.9535 for the prior and 0.9477 for CTC, a one-character difference whose
paired 95% interval spans -0.1973 to +0.1307. This near-null five-row result is
not a neural advantage or generalization claim. See
`docs/LOOP_14_SPLIT_PROTOCOL_V1.md`.

## Same-subject cross-session gate

Loop 15 Stage A safely acquires S21 session 2 as one complete split FIFF
recording plus its MAT log. The pinned three-file plan is 2,516,384,765 bytes,
uses one download worker, and remains far below a full-dataset snapshot. The
selector now supports `--session`, includes required FIFF continuations, and
records an immutable Hub revision.

The MAT log has 66 planned slots but three explicitly empty `keyTrig`/response
rows at trials 54, 58, and 60. The raw stream has 63 completed trials. The
extractor now maps raw rows to nonempty MAT slots in order, preserves the
gapped trial IDs, and records trigger-timing evidence instead of forcing equal
counts or fuzzy text order.

```bash
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

The session-2 cache uses the exact 102 source channel names and preprocessing,
but its robust scaling comes only from the 55 session-1 train rows. Six source
validation and five source test rows remain unused. On all 63 performed
session-2 trials, the fixed tiny CTC records corpus CER 0.9179 versus 0.7755 for
the signal-free prior. The paired tiny-minus-prior interval is +0.1194 to
+0.1661. This is a clear negative generalization result. Session 2 is now a
consumed evaluation set and must not be used for adapter tuning. See
`docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

Loop 15 Stage B closes the synthetic adapter gate without opening either real
holdout. The `synthetic-adapter-gate` command creates a deterministic diagonal
gain/offset shift, fits an unlabeled per-channel median/IQR map on synthetic
calibration signals, selects identity versus adaptation on validation, and
evaluates the selected contract on a frozen synthetic holdout beside the
no-signal prior.

```bash
neurodecode synthetic-adapter-gate \
  --out-dir cache/loop15_synthetic_adapter_gate \
  --sentences 96 --channels 6 --letter-classes 4 \
  --seed 23 --epochs 50 --num-threads 1 \
  --min-validation-cer-gain 0.10 --bootstrap-iterations 2000
```

The fixed gate selects robust channel-affine normalization: holdout CER moves
from 0.3448 to 0.0000 while the no-signal prior is 0.5776. This is a best-case
synthetic affine inversion, not real-MEG adapter evidence. See
`docs/LOOP_15_STAGE_B_SYNTHETIC_ADAPTER.md`.

Loop 16 measures that adapter across six nested calibration sizes, three shift
seeds, an independent unlabeled calibration pool, and three shift families.
The multi-view CTC path fits once for all validation views and replays once for
the post-selection holdout rather than retraining for every point.

```bash
neurodecode synthetic-calibration-curve \
  --out-dir cache/loop16_synthetic_calibration_curve \
  --sentences 96 --calibration-sentences 48 \
  --calibration-sizes 1,2,4,8,16,32 \
  --shift-seeds 101,211,307 --epochs 50 --num-threads 1
```

The registered median rule selects one synthetic sentence (`1.26` seconds) for
the stationary diagonal shift. On holdout, median identity/adapted CER is
`0.4224/0.2328`, but only two seeds improve and one ties. The same adapter is
harmful under channel mixing (`0.5690/0.8621`) and within-row drift
(`0.4397/0.6034`). The one-row result is not a human calibration estimate and
does not authorize real-session evaluation. See
`docs/LOOP_16_SYNTHETIC_CALIBRATION_CURVE.md`.

Loop 17 packages those compact artifacts into an honest local Gradio console.
It validates cache/report/prediction agreement, shows 19 held-out synthetic
examples with signal traces and editable CER/WER inspection, keeps real results
aggregate-only, exposes all source hashes, and labels predictive confidence
unavailable. The final startup audit passes 8/8 checks in 1.644 seconds at a
224,837,632-byte peak RSS; desktop and mobile interaction QA pass with no
browser-console errors. Launching the demo performs no raw-data read, network
fetch, real model run, or cache write. See
`docs/LOOP_17_HONEST_LOCAL_DEMO.md`.

Loop 18 standardizes existing saved results as versioned, deterministic report
cards and cohort-local leaderboard rows. It reads compact JSON reports only:
no raw data, cache array, model, network, or observed holdout is opened.

```bash
neurodecode build-leaderboard \
  --spec configs/loop18_leaderboard.json \
  --project-root . \
  --out-dir cache/loop18_leaderboard \
  --max-cards 16 --max-output-mb 2
```

The build emits 11 cards across six exact cohorts and four method families.
Only four internally comparable cohorts receive ranks; event-level holdout and
fit-on-eval smoke results remain separate, and no global winner is calculated.
SemER, cache hashes, method-specific resources, uncertainty, or code versions
that historical reports did not record are explicitly flagged as missing.
The deterministic core contains 58 files and reproduces byte-for-byte; the
complete output is 103,789 bytes. See
`docs/LOOP_18_VERSIONED_REPORT_CARDS.md`.

Loop 19 adds a bounded native BrainVision EEG path without installing MOABB or
downloading the 12.79-GB EEG subtree. A metadata-only gate pins the dataset
revision, requires a complete `.vhdr/.eeg/.vmrk` triplet plus exact MAT log,
and selects one 94,842,381-byte S7 bundle under a 128-MiB cap.

```bash
neurodecode eeg-bridge-gate \
  --manifest cache/loop19_eeg_bridge/manifest.jsonl \
  --out-dir cache/loop19_eeg_bridge/gate \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --max-download-mb 128

neurodecode extract-eeg-windows \
  --raw data/spanishbcbl_eeg_tiny/EEG/EEG/007_DECOMEG_S2_9910_task1.vhdr \
  --events data/spanishbcbl_eeg_tiny/EEG/logs/S7_session2_block1_list1.mat \
  --out cache/loop19_eeg_bridge/s7_session2_block1_61eeg_50hz.npz \
  --sfreq 50 --tmin -0.2 --tmax 0.3 --max-output-mb 32
```

The lazy extractor aligns all 2,534 MAT trigger codes to raw annotations with a
2.024-ms median absolute residual, then writes 2,197 key windows shaped
`61 x 25` in 12,428,800 bytes. The first within-session nearest-centroid result
is negative: exact label accuracy is 0.91% versus 12.27% for a train-only
no-signal prior. Text CER is explicitly non-primary for key tokens such as
`SPACE`. EEG and MEG remain separate evidence cohorts. See
`docs/LOOP_19_EEG_BRAINVISION_BRIDGE.md`.

Loop 20 adds `NeuroTokenCache v0`, a modality-aware continuous embedding
contract shaped `[items,time,embedding]`. It preserves lengths, masks, frame
timestamps, source rows/trials, subject/session IDs, modality, sampling rate,
channel geometry plus availability, strict split/source hashes, resource caps,
and separate asynchronous/producer-causal/end-to-end-latency fields. The
bounded smoke uses only synthetic signals and a deterministic target-free
projection:

```bash
neurodecode make-neurotoken-cache \
  --source-cache cache/loop20_neurotoken/source_sentences.npz \
  --split-report cache/loop20_neurotoken/split/split.json \
  --out cache/loop20_neurotoken/neurotokens_v0.npz \
  --metadata-out cache/loop20_neurotoken/neurotokens_v0.metadata.json \
  --summary-json cache/loop20_neurotoken/neurotokens_v0.summary.json \
  --modality synthetic --device-type synthetic-array \
  --subject-id SYN-1 --session-id SESSION-1 \
  --embedding-dim 32 --kernel-size 16 --stride 4 \
  --max-items 64 --max-tokens-per-item 128 --max-output-mb 4
```

The result is a 76,646-byte `48 x 16 x 32` cache with exact numerical-payload
replay and zero model, training, real-data, or holdout reads. These are mock
continuous embeddings, not learned neurotokens, a decoder score, or a measured
streaming system. See `docs/LOOP_20_NEUROTOKEN_CACHE_V0.md`.

Loop 5 closeout checks:

```bash
python -m unittest tests.test_report tests.test_cli_report
python -m unittest discover -s tests
neurodecode report --help
```

Closeout smoke artifact:

```bash
neurodecode make-synthetic-shard --out cache/loop5_synthetic_tiny.npz --samples 32 --channels 4 --times 12
neurodecode report \
  --cache cache/loop5_synthetic_tiny.npz \
  --identity-smoke \
  --out-json cache/loop5_synthetic_report.json \
  --out-md cache/loop5_synthetic_report.md \
  --run-name loop5_synthetic_identity_smoke \
  --split synthetic-smoke
```

Current limitations:

- The inspected S21 sentence path maps raw rows to nonempty MAT `keyTrig` slots
  and fails closed on unreconciled counts. Unknown MAT schemas still use the
  generic heuristic parser and must not inherit S21's validation claim.
- Generic event-window labels may remain blank when an unsupported log lacks a
  clear target field; the two validated S21 sentence caches have explicit
  target, response, trial-map, and timing provenance.
- Event-window extraction remains minimally processed; sentence extraction has
  filtering and robust scaling but no automated artifact rejection.
- The first neural-window classifier is a nearest-centroid template baseline;
  it is transparent and intentionally small. On the Loop 19 EEG event holdout,
  its 0.91% key-label accuracy is worse than the 12.27% train-only prior.
- The EEG cache is minimally processed: named EOG channels are excluded, but
  filtering, rereferencing, bad-channel repair, ICA, and artifact rejection are
  not implemented. Its within-session event split is not a generalization test.
- The tiny ConvNet baseline is optional and requires `pip install -e ".[ml]"`.
  It should be compared against the prior-only and template baselines before any
  performance claim.
- `.npz` remains the measured default for current bounded caches. Zarr is a
  conditional option only when a recorded size, latency, memory, or repeated
  subarray-access trigger is reached.
- The tiny CTC is non-causal and not a real-time decoder. Its first strict real
  five-row test is near-null, and its independent-session result is materially
  worse than the prior.
- NeuroTokenCache v0 validates an embedding interface, not representation
  quality. Its Loop 20 vectors are deterministic random projections from
  synthetic signals; producer causality and 160-ms frame availability do not
  establish downstream-decoder causality or end-to-end latency.
- The local demo displays synthetic example text and aggregate-only real
  metrics. It is an evidence console, not a live real-MEG decoder; predictive
  confidence remains unavailable.
- Two S21 sessions are now validated for a same-subject session holdout. This
  does not establish unseen-person or population generalization, and session 2
  must not become a tuning set after its result was observed.
- Train-only robust scaling now passes on the fixed 102-channel base. The older
  recording-scaled and variance-selected caches remain unsuitable for strict
  candidate scoring until their data-dependent steps are train-only.
- Lower sampling rates are resource variants, not accuracy results; 25 Hz also
  limits effective bandwidth to 12.5 Hz and coarsens boundaries to a 40 ms grid.
- Channel subsets are resource/geometry proxies, not retained-accuracy
  results. Variance selection is fit on the same S21 block, device-coordinate
  coverage is not cortical localization, and magnetometer-only subsets are not
  equivalent to an OPM helmet.

## Why this wedge matters

Brain2Qwerty v1/v2 are exciting, but the current practical barrier is large:
the public v1 SpanishBCBL dataset is around 262GB, while the v2 code is public
but the EnglishBCBL dataset remains under embargo. A developer-access layer can
create real leverage by giving people tiny curated shards, event-aligned
windows, reproducible baselines, and clear metrics before they ever touch the
full data.

## Non-goals for v0

- No clinical claims.
- No consumer EEG hype.
- No attempt to identify people from neural data.
- No full Brain2Qwerty v2 reproduction until v2 data is public.
- No commercial use of CC BY-NC data unless rights are separately cleared.

## First useful milestone

**B2Q-mini v0:** one participant, one MEG block, downsampled/cacheable event windows, one tiny baseline, and one report with CER/WER + storage footprint.

Success looks like this:

```text
A new builder can run a real or synthetic end-to-end loop in minutes,
see where errors come from,
and know exactly what to try next.
```
