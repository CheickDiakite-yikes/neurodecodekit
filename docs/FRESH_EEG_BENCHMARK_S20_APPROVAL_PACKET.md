# Fresh EEG Benchmark Approval Packet: S20 Session 2 Block 2

Version: 0.1

Prepared: 2026-07-10

Status: **NOT AUTHORIZED - DRY RUN ONLY**

## Question

Can one fresh, task-matched SpanishBCBL EEG block pass the existing
BrainVision/MAT alignment and event-classification pipeline and show any
signal-linked key-label advantage over both a train-only no-signal prior and a
deterministic signal-shuffle control?

This first benchmark does not test sentence CER/WER, unseen-person
generalization, portable hardware, online inference, or clinical utility.

## Why This Recording

The pinned official manifest contains no unconsumed task-compatible raw EEG
locally. S20 session 2 block 2 is the smallest fresh complete typing bundle
after excluding consumed S7, known unusable records, incomplete bundles, and
localizer/tapping files.

Dataset: `bcbl190626/SpanishBCBL`

Revision: `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`

License: CC-BY-NC-4.0

Nominal identity: subject S20, session 2, task block 2

Cohort: prompted Spanish sentence typing, EEG

## Exact Files

| Remote path | Role | Bytes | Local state |
|---|---|---:|---|
| `EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr` | BrainVision header | 11,705 | Absent |
| `EEG/EEG/020_DECOMEG_S2_11966_task2.eeg` | Binary EEG signal | 95,782,400 | Absent |
| `EEG/EEG/020_DECOMEG_S2_11966_task2.vmrk` | BrainVision marker file | 91,219 | Absent |
| `EEG/logs/S20_session2_block2_list1.mat` | Behavioral log | 204,940 | Present locally; not parsed in this gate |
| **Total bundle** |  | **96,090,264** | 204,940 bytes already present |

Maximum network transfer is 96,090,264 bytes. Expected new allocation is
95,885,324 bytes if the existing log passes exact path/size/source-revision
verification. The executor must fail closed on any mismatch; it must not
silently substitute, expand, or redownload unrelated files.

## Storage And Compute Caps

Snapshot at proposal time: 11 GiB free on a 460 GiB data volume, 98% used.

```text
selected remote files:          exactly 4
acquisition cap:                128 MiB
new generated-artifact cap:      16 MiB
worker count:                     1
CPU threads:                      1
peak RSS cap:                     2 GiB
wall-clock cap:                  20 minutes
network calls after download:     0
larger-model training runs:       0
```

No second block, participant, localizer, or whole-subtree operation is
authorized. Do not delete existing data or caches to make room; stop if the
preflight reports less than 2 GiB free.

## Frozen Access Order

1. **Approval check**: require an explicit user instruction naming this packet
   and authorizing the four files.
2. **Metadata dry run**: verify revision, paths, exact sizes, license, disk
   headroom, no path collisions, and one-worker configuration. Stop on change.
3. **Acquisition**: fetch only absent approved files. Write an access log and
   verify final file sizes before opening content.
4. **Level-0 intake**: companion validation and metadata report.
5. **Bounded signal extraction**: one raw open, one MAT open, alignment audit,
   and one event cache under the artifact cap.
6. **Split binding**: derive stable performed trial IDs without target text;
   sort by SHA-256 of
   `revision|S20|session2|block2|source_trial_id`. Assign the first 44 to train,
   next 10 to validation, and last 10 to test. If there are not exactly 64
   usable trials, stop and issue a revised preregistration before prediction.
7. **Train/validation**: fit preprocessing and fixed baselines on train only.
   Validation is diagnostic; it cannot select architecture, features,
   channels, thresholds, or hyperparameters.
8. **One-time test**: open the ten bound test trials once only if every
   mechanical/alignment/resource gate passes. Write the final report and mark
   the test consumed.

Target text, typed text, and key labels are prohibited from feature creation,
channel selection, preprocessing fit, split creation, and quality thresholds.

## Frozen Analysis

Input representation:

- existing BrainVision-plus-MAT event extraction contract;
- EEG channels only; EOG/misc channels remain typed and excluded from the
  primary neural baseline;
- 50 Hz output rate and the existing fixed event window unless a pre-open
  mechanical incompatibility forces the benchmark to park;
- train-only robust scaling;
- no learned encoder and no sequence decoder.

Predictors:

1. **No-signal prior**: most frequent train key label, applied unchanged.
2. **Signal-shuffle control**: same transparent classifier trained after one
   fixed train-only permutation that breaks signal/label pairing.
3. **Neural baseline**: existing deterministic nearest-centroid key-label
   classifier on flattened event windows.

No hyperparameter search, channel sweep, rate sweep, precision sweep, language
model, target text, test calibration, or larger model is permitted.

## Metrics

Primary:

- exact key-label accuracy for neural, prior, and shuffle predictors;
- paired neural-minus-prior and neural-minus-shuffle accuracy differences;
- 2,000-resample paired bootstrap intervals at the sentence-trial group level.

Secondary diagnostics:

- macro recall and per-class support;
- alignment count and timing residuals;
- flat/noisy/missing channel warnings from the separately frozen quality
  contract if available;
- runtime, peak RSS, input/output bytes, cache shape, padding fraction;
- raw reads, real-cache reads, model runs, training runs, and network calls.

CER/WER must be `unavailable` because this packet does not authorize sequence
prediction. End-to-end latency must be `not measured`. Producer causality must
be reported from the actual extraction contract; the existing symmetric event
window is expected to be noncausal.

## Mechanical Gates

All must pass before test access:

- four exact files at the pinned revision and exact total bytes;
- one complete BrainVision bundle and one matching MAT log;
- exactly 64 usable performed trials and no ambiguous trial mapping;
- finite EEG samples, stable rate, nonempty channel set, and unique channel
  names;
- zero split overlap and stable split/membership hashes;
- train-only preprocessing provenance;
- prior, shuffle, and neural predictors all present;
- one-thread execution and every resource/output cap;
- no consumed S7/S21 array, seed 2203/2303/2353, or network service opened.

Any failure parks the benchmark before prediction or before test, with the
measured reason. It does not authorize changing the split or model.

## Scientific Decision Rule

This is a first transparent benchmark, not a neural-advantage confirmation
study. Report the point estimates and paired intervals without declaring a
success threshold after seeing them.

- If the neural baseline does not beat both controls in point estimate, record
  a negative result and park model expansion.
- If it beats both controls but either paired interval includes zero, record an
  inconclusive signal and require a new participant-level preregistration.
- If it beats both controls and both lower bounds exceed zero, record evidence
  of within-recording event-label advantage only. Do not claim sentence
  decoding, new-person transfer, or portable-device performance.

## Expected Artifacts

All generated artifacts stay under 16 MiB combined:

- acquisition manifest and access audit JSON;
- level-0 intake JSON/Markdown;
- one bounded event cache;
- extraction/alignment JSON/Markdown;
- split membership and hash sidecar;
- comparator predictions and final benchmark JSON/Markdown report.

Raw data and caches remain ignored and are never committed. Only a compact,
de-identified aggregate closeout may be committed.

## Explicit Approval Gate

No current instruction authorizes acquisition. A future approval must be
substantively equivalent to:

> Approve the S20 session-2 block-2 packet at revision
> 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 for exactly the four listed files,
> at most 128 MiB downloaded and 16 MiB generated, with one worker and one CPU
> thread. Run the frozen 44/10/10 protocol once and do not touch consumed data.

Until then, the correct action is metadata-only inspection and no download.
