# Loop 19 - Bounded SpanishBCBL EEG BrainVision Bridge

Status: **Done as a real-data bridge and negative baseline validation** on
2026-07-10.

Loop 19 answers a narrow question: can the existing safe-selection, cache, and
report contracts ingest one small, task-compatible EEG recording without a new
heavy dependency or a large download?

The answer is yes for the data bridge. It is no for the first transparent
decoder: the minimally processed nearest-centroid baseline is substantially
worse than its train-only no-signal prior on exact key-label accuracy.

## Proof posture

Three proof levels must remain separate:

1. `metadata_verified_no_signal_download`: the pinned repository manifest,
   license, task, complete BrainVision triplet, matching MAT log, dependency
   state, and exact byte cap passed before acquisition.
2. `real_signal_bridge_validated`: one explicitly approved 94,842,381-byte EEG
   bundle was read lazily, aligned to its MAT trigger sequence, and converted
   to a 12,428,800-byte cache.
3. `single_session_event_holdout_negative_result`: a deterministic within-file
   key-event holdout shows no nearest-centroid advantage over a no-signal
   prior. This is not session or subject generalization.

This loop does not establish EEG decoding quality, a Brain2Qwerty-v2
replication, consumer-hardware readiness, real-time decoding, arbitrary-thought
decoding, or a clinical use.

## Research and dependency gate

The SpanishBCBL dataset card describes EEG recorded during the same controlled
typed-sentence-production task as its MEG data. The EEG files use BrainVision
`.vhdr`, `.eeg`, and `.vmrk` sidecars at 1 kHz, with matching MATLAB behavioral
logs. The dataset is CC BY-NC 4.0.

The official Brain2Qwerty SpanishBCBL loader provided the compatibility rules
used here:

- a BrainVision header is the recording anchor
- all three BrainVision files are required
- EOG-named channels are excluded
- raw annotation triggers, not the absolute MAT clock, align the behavior log
- malformed participant 001 and the loader's known bad EEG stems are excluded

MOABB was researched but not installed. Its stock paradigms are motor imagery,
P300, SSVEP, and related benchmark tasks rather than typed sentence production.
Its stable install documentation also lists Python 3.9-3.11 while this local
environment is Python 3.13.5. The native MNE path reuses installed packages and
preserves the actual task.

Primary sources:

- SpanishBCBL dataset card: https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- Brain2Qwerty v1 article: https://www.nature.com/articles/s41593-026-02303-2
- official loader at the inspected commit:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
- MNE BrainVision reader:
  https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html
- MOABB API and install scope: https://moabb.neurotechx.com/docs/api.html and
  https://moabb.neurotechx.com/docs/install/install_pip.html

## Metadata-only gate

The repository was listed with sizes at immutable SpanishBCBL revision
`88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`. The complete EEG subtree contains
413 files and 12,790,560,040 known bytes. None of those signal files was read by
the gate.

```bash
neurodecode list-hf-files \
  --repo-id bcbl190626/SpanishBCBL \
  --repo-type dataset \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --with-sizes \
  --out cache/loop19_eeg_bridge/hf_files.jsonl

neurodecode manifest-from-paths \
  --paths cache/loop19_eeg_bridge/hf_files.jsonl \
  --out cache/loop19_eeg_bridge/manifest.jsonl

neurodecode eeg-bridge-gate \
  --manifest cache/loop19_eeg_bridge/manifest.jsonl \
  --out-dir cache/loop19_eeg_bridge/gate \
  --revision 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684 \
  --max-download-mb 128 --max-output-mb 1
```

The gate selected the smallest complete usable bundle: S7, session 2, block 1.

```text
BrainVision header:       11,727 bytes
BrainVision signal:   94,548,480 bytes
BrainVision markers:      82,927 bytes
matching MAT log:         199,247 bytes
total:                 94,842,381 bytes
cap:                  134,217,728 bytes
```

All 13 checks passed. The gate ran in 0.144 seconds at 27,983,872-byte peak RSS
and wrote 10,460 bytes. It performed zero data downloads, raw reads, model
runs, cache writes, or signal-array loads.

## Explicit acquisition

`download-selection` first printed the four-file, 90.4-MiB dry-run plan. Only
then was the same pinned selection executed with one worker:

```bash
neurodecode download-selection \
  --selection cache/loop19_eeg_bridge/gate/selection.json \
  --local-dir data/spanishbcbl_eeg_tiny \
  --max-workers 1

neurodecode download-selection \
  --selection cache/loop19_eeg_bridge/gate/selection.json \
  --local-dir data/spanishbcbl_eeg_tiny \
  --max-workers 1 --execute
```

No other EEG recording and no full repository snapshot was downloaded.

## Trigger alignment

MNE opens the recording lazily with `preload=False`. The file contains 64
channels, 738.66 seconds at 1,000 Hz, and 2,542 numeric `Stimulus/S` annotation
triggers. Excluding `RVEOG`, `LHEOG`, and `RHEOG` leaves 61 channels.

The MAT file has an independent Psychtoolbox clock around 1.29 million seconds,
so direct timestamp indexing would be invalid. The bridge instead parses the
MAT RSVP and pressed-key trigger codes and matches that exact ordered code
sequence as a subsequence of the raw BrainVision annotations. After estimating
one constant clock offset, residual timing is audited rather than used to force
the match.

```text
MAT triggers matched:             2,534 / 2,534
raw annotation triggers:          2,542
unmatched raw boundary markers:   8
median absolute residual:         2.024 ms
p99 absolute residual:            19.914 ms
maximum absolute residual:        24.862 ms
allowed maximum residual:         50 ms
aligned pressed-key events:       2,200
unsupported keycodes dropped:     3
```

All 66 ENTER key events are retained. This validates the trigger bridge for
this file; it does not prove every EEG recording has the same quality.

## Streaming cache extraction

```bash
neurodecode extract-eeg-windows \
  --raw data/spanishbcbl_eeg_tiny/EEG/EEG/007_DECOMEG_S2_9910_task1.vhdr \
  --events data/spanishbcbl_eeg_tiny/EEG/logs/S7_session2_block1_list1.mat \
  --out cache/loop19_eeg_bridge/s7_session2_block1_61eeg_50hz.npz \
  --out-json cache/loop19_eeg_bridge/extraction.json \
  --sfreq 50 --tmin -0.2 --tmax 0.3 \
  --max-alignment-residual-ms 50 --max-output-mb 32
```

Each 500-ms window is read from disk independently and polyphase-resampled from
1,000 Hz to 50 Hz. The raw object is never globally preloaded.

```text
output shape:       [2,197 events, 61 channels, 25 timepoints]
dtype:              float32
label classes:      26
cache bytes:        12,428,800
runtime:            6.402 seconds
maximum RSS:        300,548,096 bytes
raw preloaded:      false
```

This is intentionally minimal preprocessing. No EEG filtering, rereferencing,
bad-channel repair, ICA, ocular-artifact rejection, or trial rejection has been
claimed. The three explicitly named EOG channels are excluded; that is not an
artifact-cleaning pipeline.

## Transparent baseline and no-signal comparator

The cache was split 50/50 by key class with seed 7. The nearest-centroid model
uses 1,097 training events and evaluates 1,100 events. Its no-signal comparator
uses only those same 1,097 training labels and predicts the most frequent class,
`SPACE`; `fit_on_eval_targets` is false.

```bash
neurodecode template-baseline \
  --cache cache/loop19_eeg_bridge/s7_session2_block1_61eeg_50hz.npz \
  --train-fraction 0.5 --seed 7 --bootstrap-iterations 2000 \
  --out-predictions cache/loop19_eeg_bridge/template_predictions.txt \
  --out-json cache/loop19_eeg_bridge/template_report.json \
  --out-md cache/loop19_eeg_bridge/template_report.md \
  --run-name loop19_s7_eeg_template \
  --split real-eeg-key-event-stratified-holdout
```

Exact key-label accuracy is the primary metric. Text CER remains in the generic
report for schema compatibility, but it is not interpretable as the primary
metric because tokens such as `SPACE` and `ENTER` contain multiple characters.

```text
nearest-centroid label accuracy:  0.009091 (10 / 1,100)
train-only prior label accuracy:  0.122727 (135 / 1,100)
accuracy delta, model - prior:    -0.113636
paired bootstrap 95% interval:   [-0.134545, -0.093636]
paired model wins/ties/losses:    9 / 957 / 134
bootstrap P(model better):        0.0
runtime / maximum RSS:            0.63 sec / 262,209,536 bytes
```

The result is a negative baseline finding. The bridge produces inspectable real
EEG windows, but this minimally processed nearest-centroid method does not
extract useful key-class signal and is materially worse than the no-signal
frequency prior.

The split is also an easy within-session event holdout: adjacent events and
sentences can appear on opposite sides. It cannot support cross-sentence,
cross-session, cross-subject, or population claims.

## What changed

- corrected SpanishBCBL EEG subject/session/block parsing against the official
  filename convention
- required complete BrainVision triplets and exact MAT logs in EEG selection
- excluded official known-bad EEG stems and malformed participant 001
- added pinned Hugging Face file-size metadata listing
- added a metadata-only EEG bridge gate with runtime/access audit
- added lazy BrainVision plus MAT-trigger extraction into B2Q-mini cache v0
- added exact trigger-sequence alignment with an independent-clock residual
  audit
- made the template baseline emit a same-split train-only prior comparator
- added exact label-accuracy paired comparison so multi-character key tokens do
  not distort the primary conclusion
- added focused parser, selector, gate, extraction, metric, and CLI tests

## Resource closeout

```text
downloaded EEG bundle:       94,842,381 bytes
derived EEG cache:           12,428,800 bytes
other Loop 19 artifacts:     under 0.4 MiB
full EEG subtree avoided:    12,790,560,040 bytes
free local disk after run:   about 17 GiB
new heavy dependencies:      none
MOABB installed:             no
```

## Decision and next gate

Loop 19 is complete as an optional native SpanishBCBL EEG bridge. Keep EEG and
MEG in separate evidence cohorts. Do not optimize the negative event classifier
against this easy holdout or present it as sentence decoding.

Loop 20 should define a small modality-aware neurotoken/cache interface over
existing arrays and synthetic embeddings. It must preserve modality, channel
geometry, timebase, mask, provenance, and split identifiers without assuming
unreleased v2 data or training a larger model.
