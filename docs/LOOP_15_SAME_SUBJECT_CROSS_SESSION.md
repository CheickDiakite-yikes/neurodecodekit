# Loop 15 - Same-Subject Cross-Session Gate

Status: `Stage A complete; Loop 15 closed by the synthetic Stage B gate` on
2026-07-10. See `docs/LOOP_15_STAGE_B_SYNTHETIC_ADAPTER.md`.

Proof posture: `real same-subject independent-session local evaluation; no
subject, population, adapter-benefit, real-time, or arbitrary-thought claim`.

## Decision summary

One complete second S21 recording was acquired under an exact three-file,
2.5-GiB cap at immutable SpanishBCBL revision
`88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`. MNE opens its primary and
continuation FIFF files as one 977.05-second recording. The matching MAT log
contains 66 planned trial slots, but trials 54, 58, and 60 have empty
`pr_trials.keyTrig` rows and no response. The raw stream contains exactly 63
completed ENTER-delimited sequences. Nonempty MAT trial order therefore gives
the deterministic map:

```text
raw rows 0..53 -> MAT trials 0..53
raw rows 54..56 -> MAT trials 55..57
raw row 57     -> MAT trial 59
raw rows 58..62 -> MAT trials 61..65
skipped MAT trials: 54, 58, 60
```

This fixes an extractor assumption; it does not impute or relabel unperformed
trials. The map is supported independently by response indices and sub-
millisecond trigger timing.

A 102-magnetometer, 100-Hz session-2 cache was then produced with preprocessing
identical to the strict session-1 cache. It was deliberately extracted
unscaled, then transformed with only the frozen robust statistics fitted on
the 55 session-1 train rows. The transformer verifies channel order,
preprocessing parameters, cache hashes, split hashes, statistic hashes, and
zero padding before writing.

One fixed 2,908-parameter tiny CTC was trained on those 55 source train rows.
The six source validation and five source test rows were untouched. All 63
performed session-2 rows were evaluated once. The neural baseline was worse
than the signal-free prior by 389 character edits and 0.142491 corpus CER. The
paired interval excludes zero in the harmful direction.

Decision:

```text
cross_session_protocol_valid_tiny_ctc_fails_generalization
```

Do not tune hyperparameters or adapter choices against this session-2 result.
Continue Loop 15 with synthetic/source-validation adapter development and a
pre-registered future evaluation.

## Bounded acquisition

Authoritative repository state checked before download:

```text
dataset: bcbl190626/SpanishBCBL
revision: 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
last modified: 2026-06-29T11:56:46Z
```

The selector now supports an explicit session filter, includes required
hyphen-numbered FIFF continuations in both the file list and byte cap, records
an immutable Hub revision, and defaults the downloader to one worker.

Pinned selection:

| File | Bytes |
|---|---:|
| `MEG/FIF/21_3660/231213/block1.fif` | 1,903,910,570 |
| `MEG/FIF/21_3660/231213/block1-1.fif` | 612,208,426 |
| `MEG/logs/S21-session2_block1_list2.mat` | 265,769 |
| **Total** | **2,516,384,765** |

The exact total is 2.344 GiB under a 2.5-GiB cap. The dry run printed exactly
three known-size files and no warnings. Execution used one Hub worker and
completed in about 21 seconds. Free disk moved from about 18 GiB to 16 GiB.
The approximately 262-GB dataset was not downloaded.

```bash
neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest_with_sizes.jsonl \
  --out data/s21_session2_block1_selection.json \
  --modality MEG --subject S21 --session 2 --blocks 1 \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --max-files 3 --max-total-gb 2.5

neurodecode download-selection \
  --selection data/s21_session2_block1_selection.json \
  --local-dir data/spanishbcbl_tiny \
  --dry-run --max-files 3 --max-total-gb 2.5 --max-workers 1

neurodecode download-selection \
  --selection data/s21_session2_block1_selection.json \
  --local-dir data/spanishbcbl_tiny \
  --execute --max-files 3 --max-total-gb 2.5 --max-workers 1
```

Dataset source: https://huggingface.co/datasets/bcbl190626/SpanishBCBL

Pinned recording tree:
https://huggingface.co/datasets/bcbl190626/SpanishBCBL/tree/88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684/MEG/FIF/21_3660/231213

## FIFF continuity proof

MNE was opened with `on_split_missing='raise'` for the audit and loaded no MEG
signal samples:

```text
FIFF parts: 2
channels: 312
sampling rate: 2048 Hz
first sample: 36,000
last sample: 2,036,999
samples: 2,001,000
duration: 977.05078125 sec
STI101 events: 3,524
event samples strictly increasing: true
```

The cache metadata now reports both raw part paths and their combined
2,516,118,996 bytes instead of reporting only the primary FIFF file.

## The three missing MAT trials

After removing the 28-event ASCII calibration sweep:

```text
keyboard-like stim candidates: 2,821
retained key rows: 2,793
retained ENTER events: 63
raw typed sequences: 63
MAT target slots: 66
MAT nonempty keyTrig slots: 63
MAT response rows: 63
empty keyTrig / missing response slots: [54, 58, 60]
```

The MAT response source indices exactly equal the nonempty `keyTrig` indices.
All 63 raw sequences align in strictly increasing order to those indices. The
response comparison gives 63 high-confidence matches, 56 exact rows, and mean
CER 0.002918. Small differences are expected where the MAT keyboard response
applies edits that are not represented by the retained A-Z/SPACE/ENTER stim
codes.

The target comparison gives 58 high, 4 moderate, and 1 low-confidence row with
mean CER 0.047743. The low target row is raw sequence 34 / MAT trial 34; its
MAT-recorded response still maps to trial 34 with CER 0.025. Target CER measures
participant typing versus the prompt, not neural decoding and not trial order.

The earlier 13-sequence audit came from S21 session-1's short, officially
unusable root `block2.fif` shard. Its three low-confidence text matches should
not be repaired by forced matching. The complete session-1 block-1 audit
already replaced that evidence with a 66/66 identity mapping. The three empty
session-2 MAT slots described here are a separate, explicitly observed issue.

## Trigger timing proof

The timing audit compares raw key trials to only the corresponding nonempty MAT
slots:

```text
trials compared: 63
equal-key-count trials: 57
key-count mismatch raw-row indices: [6, 18, 29, 34, 39, 50]
paired keypresses: 2,529
run-specific clock offset: 3245.28971668875 sec
median absolute residual: 0.296139 ms
p95 absolute residual: 0.944984 ms
residuals within 1 ms: 2,427 / 2,529 (95.97%)
```

The run-specific offset must not be reused. The residuals are independent
support for the nonempty-slot order; they are not a decoder metric.

## Session-2 caches

Unscaled extraction:

```bash
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231213/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session2_block1_list2.mat \
  --out cache/loop15_s21_cross_session/session2_unscaled_102mag_100hz.npz \
  --sfreq 100 --picks mag --max-channels 102 \
  --no-robust-scale --scaler-fit-scope recording
```

Observed:

```text
shape: 63 x 102 x 1,636
valid lengths: 366..1,636
cache bytes: 14,179,453
cache SHA-256: 0f81d32e35deb62403966804df0003fa052bacd59c5442a0582d34641ca99d62
runtime: 14.228 sec
peak RSS: about 2.1 GB
```

The 1,636-sample padded width comes from one slow approximately 16-second
typing trial. It is not a second recording concatenated into a row.

All 102 channel names and these parameters match the session-1 fit cache
exactly: 100 Hz, 0.4/0.45-second context, magnetometers, 0.5-45 Hz bandpass,
50-Hz notch, and `STI101` boundaries.

Frozen scaling:

```bash
neurodecode apply-frozen-scaler \
  --source-cache cache/loop15_s21_cross_session/session2_unscaled_102mag_100hz.npz \
  --fit-cache cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --out cache/loop15_s21_cross_session/session2_session1_train_scaled_102mag_100hz.npz
```

```text
fit cache SHA-256: 45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815
center SHA-256: d0beb18fe682042931ceda95ef5b6ba3fa66b57b93302c86fa3b11766bdb7a7d
scale SHA-256: e67ae077cc432be95d042900613b638e109843b845f50dee7fa96ecaf2807ee2
scaled cache SHA-256: 4b1595f3c7b215c327e0ab4c301c5d8830f9344c5ea9f800805ec6425b33f9cd
scaled cache bytes: 13,543,399
runtime: 0.605 sec
session-2 rows used to fit scaler: 0
```

## Fixed cross-session baseline

```bash
neurodecode cross-session-ctc \
  --train-cache cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --train-split-report cache/loop14_s21_split_aware/split/split.json \
  --eval-cache cache/loop15_s21_cross_session/session2_session1_train_scaled_102mag_100hz.npz \
  --seed 7 --epochs 60 --batch-size 16 --learning-rate 0.02 \
  --hidden-channels 16 --device cpu --num-threads 1 --max-restarts 1
```

Protocol:

```text
source train rows: 55
source validation rows reserved/unused: 6
source test rows reserved/unused: 5
independent session-2 eval rows: 63
unique typed-target overlap: 0 / 63
unique reference-prompt overlap: 0 / 63
parameters: 2,908
model initializations: 1
```

Results:

| Metric | Signal-free prior | Tiny CTC |
|---|---:|---:|
| Session-2 rows | 63 | 63 |
| Character edits | 2,117 | 2,506 |
| Corpus CER | 0.775458 | 0.917949 |
| Corpus WER | 1.032184 | 1.000000 |
| Exact sentences | 0 | 0 |
| Source-train CER | n/a | 0.925469 |
| Eval blank fraction | n/a | 0.677081 |

Paired tiny-CTC-minus-prior result:

```text
CER delta: +0.142491
character-edit delta: +389
sentence wins/ties/losses: 3/2/58
5,000-sample paired sentence-bootstrap 95% interval: [+0.119386, +0.166069]
bootstrap probability tiny CTC is better: 0.000
total command runtime: 7.353 sec
model runtime: 6.682 sec
peak RSS: 549,896,192 bytes
```

The model mostly emits repetitions of `L` and a few other characters. Its poor
source-train fit already indicates under-capacity or optimization failure. The
independent-session result shows no useful generalization and is materially
worse than the no-signal comparator. It must not be described as a neural
decoding success.

## Resource ledger

```text
new downloaded files: 2,516,384,765 bytes
new Loop 15 cache/report artifacts: about 26 MiB
free disk immediately after acquisition and artifacts: about 16 GiB
free disk after safe cache cleanup and final verification: about 17 GiB
download workers: 1
numeric/Torch threads: 1
raw extraction peak RSS: about 2.1 GB
CTC peak RSS: about 524 MiB
```

## Evidence

- `data/s21_session2_block1_selection.json`
- `cache/loop15_s21_cross_session/session2_unscaled_summary.json`
- `cache/loop15_s21_cross_session/frozen_scaler_summary.json`
- `cache/loop15_s21_cross_session/tiny_ctc/report.json`
- `cache/loop15_s21_cross_session/tiny_ctc/report.md`

## Next gate

Stage B has now completed items 1 and 2 below without opening either frozen
real evaluation. Loop 16 owns the calibration-size study; any future real test
still requires the pre-registration and acquisition controls below.

Session 2 is now a consumed evaluation set. The next adapter work must:

1. Create a synthetic domain-shift benchmark and prove that normalization or a
   tiny adapter can help without evaluation leakage.
2. Use only session-1 train rows for fitting and session-1 validation rows for
   model or adapter selection. Keep the five source test rows frozen.
3. Pre-register the chosen adapter, hyperparameters, sensor set, precision, and
   stopping rule before another real held-out session/person evaluation.
4. Acquire any further raw data only through pinned revision, exact file list,
   split-FIFF completeness, byte cap, dry run, explicit execute, and one-worker
   controls.
5. Require multiple canonical people before any subject-generalization claim
   and a causal model plus streaming latency measurements before a real-time
   claim.
