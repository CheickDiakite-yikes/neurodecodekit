# Real Data Acquisition + Validation Pass - 2026-07-03 Local

> Historical pass. Superseded by `docs/REAL_DATA_VALIDATION_2026-07-10.md`:
> S21 `block1.fif` is now validated 66/66 in strict trial order, Loop 9 has
> started, and the official loader confirms S21 block 2 must use
> `block2_2.fif`, not `block2_1.fif`.

At the time of this pass, Loop 9 was paused. This document records the first
real SpanishBCBL acquisition and the then-current proof boundary; the status
and next action below are historical rather than current instructions.

## Source Discovery

Current Hugging Face file-tree metadata for `bcbl190626/SpanishBCBL` was
queried through `huggingface_hub`.

Observed tree:

- 731 files
- 280,382,552,015 total bytes
- 231 `.fif` files
- 146 `.mat` logs
- 117 each of `.eeg`, `.vhdr`, `.vmrk`

The current Dataset Viewer is not usable for row-style access because the
dataset consists of raw neuroimaging files. File-tree metadata is the right
entrypoint for this repo.

## Parser/Selector Fixes

The current public MEG paths use recording directories such as:

```text
MEG/FIF/21_3660/231204/block2.fif
```

The earlier parser expected clearer `S21`-style raw paths. This pass added:

- subject inference from MEG/FIF recording directory prefixes, e.g. `21_3660`
  -> `S21`
- session assignment from each subject's sorted recording-date folders
- selection ranking that prefers primary FIF files over split-continuation
  files such as `block2-1.fif`

## Downloaded Tiny Shard

The selector produced a capped, exact, known-size two-file plan:

```text
MEG/FIF/21_3660/231204/block2.fif                 621,506,838 bytes
MEG/logs/S21-session1_block2_list2.mat                280,082 bytes
```

Total selected size: 621,786,920 bytes, under the 2 GB cap.

Dry-run was verified before execution. The files were downloaded to:

```text
data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block2.fif
data/spanishbcbl_tiny/MEG/logs/S21-session1_block2_list2.mat
```

## Real File Validation

FIF header read with MNE:

```text
sfreq: 2048 Hz
n_times: 490,500
duration: 239.501953125 sec
channels: 312
stim channels: STI101, STI201, STI301
```

MAT log loaded with SciPy. The existing MAT parser found candidate key rows, but
selected absolute Psychtoolbox-style times around 938,579 seconds. Running the
existing MAT event extraction produced:

```text
events found: 115
events kept: 0
events dropped: 115
reason: after_end / max_events
```

This is an important real-data finding: direct MAT timing alignment remains
unresolved and should not be treated as validated.

## Trigger-Derived Cache

The raw `STI101` channel contained 910 trigger events. A conservative
trigger-derived mode was added for uppercase ASCII letter triggers only
(`A`-`Z`), excluding ambiguous low integer trial/space/enter codes.

Extraction command:

```bash
neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block2.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block2_list2.mat \
  --out cache/b2qmini_s21_session1_block2_stim_letter.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-channels 16 \
  --max-events 120 \
  --event-source stim-letter \
  --stim-channel STI101
```

Observed result:

```text
events found: 477
events kept: 120
events dropped: 357
output shape: (120, 16, 25)
sampling rate: 50 Hz
output file size: 37.3 KB
```

Cache proof:

```text
neurodecode load-cache --cache cache/b2qmini_s21_session1_block2_stim_letter.npz
```

The cache loads through schema v0 with 120 events, 16 channels, 25 timepoints,
and 26 unique uppercase letter labels.

## Typed-Key Trigger Cache

A follow-up pass added `--event-source stim-key` for typed key triggers. This
mode keeps uppercase letters plus explicit `SPACE` and `ENTER` labels. It also
drops the short initial ASCII trigger sweep when the first compact segment has
the expected alphabet-like shape.

Extraction command:

```bash
neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block2.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block2_list2.mat \
  --out cache/b2qmini_s21_session1_block2_stim_key.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --event-source stim-key \
  --stim-channel STI101
```

Observed result:

```text
events found: 568
events kept: 540
events dropped: 28
drop reason: initial_ascii_sweep
output shape: (540, 306, 25)
sampling rate: 50 Hz
output file size: 3.4 MB
```

Cache proof:

```text
neurodecode load-cache \
  --cache cache/b2qmini_s21_session1_block2_stim_key.npz \
  --metadata-out cache/b2qmini_s21_session1_block2_stim_key.metadata.json
```

The cache loads through schema v0 with 540 events, all 306 MEG channels, 25
timepoints, and 25 unique key labels. The reconstructed key stream is
sentence-like after the ASCII sweep is dropped. It has 13 `ENTER` events and 15
time-gap segments; two target sentences split across long pauses, so later CTC
or sequence grouping must model trial boundaries deliberately.

This validates raw trigger-derived actual key events. It does not validate MAT
target sentence timing, target-vs-actual typing alignment, or decoding
performance.

Follow-up correction: MNE event samples are absolute FIF sample numbers. This
block starts at `raw.first_samp = 51000`, so stim-derived event times must use
`(event_sample - raw.first_samp) / sfreq`. The `stim-letter` and `stim-key`
caches were regenerated with this correction, and metadata now records
`raw_first_samp`.

## Sequence Alignment Audit

Loop 8.5 added a lightweight sequence audit command:

```bash
neurodecode align-sequences \
  --cache cache/b2qmini_s21_session1_block2_stim_key.npz \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block2_list2.mat \
  --out-json cache/s21_stim_key_sequence_alignment.json \
  --out-md cache/s21_stim_key_sequence_alignment.md \
  --run-name s21_stim_key_sequence_alignment
```

This command reads only cache labels, event times, and metadata; it does not
load the full window array and does not touch the raw FIF file.

Observed result:

```text
key sequences: 13
target sequences: 66
exact matches: 5
usable high/moderate matches: 10
mean CER: 0.14497806541284802
confidence counts: {'low': 3, 'high': 9, 'moderate': 1}
low-confidence indices: [0, 1, 10]
recorded-response mean CER: 0.16635701838126604
```

This validates grouping actual typed keys into `ENTER`-delimited sequences and
matching most typed sequences to MAT targets and MAT-recorded responses.
`mat.pr_trials.sequence` is used as the 66-row target list aligned with
`mat.pr_trials.key`; `mat.pr_trials.sequences` is a 64-row sequence pool and is
not the right source for trial-aligned target rows.

The remaining blocker is now specific:

- sequence 0 (`ESTOS AIRES...`) is absent from both selected MAT targets and
  MAT-recorded responses
- sequence 1 (`LA PROGRESION...`) is absent from both selected MAT targets and
  MAT-recorded responses
- sequence 10 (`LOS ABRBOLES...`) remains low-confidence against both target
  and recorded response, and the raw trigger stream around it does not contain a
  backspace/edit trigger that would repair the text

The alignment still uses text similarity rather than direct MAT timing.

## Low-Confidence Follow-Up - 2026-07-05 Local

The earlier "3 low-confidence rows" framing was too narrow. A MAT-only expansion
downloaded and searched all 146 `.mat` logs from the dataset, totaling about
33.8 MB. No additional raw FIF/EEG signal files were downloaded.

Findings:

- sequence 0 is a real official target, not trigger garbage:
  `ESTOS AIRES DE LA FRONTERA SON MALOS` appears in
  `MEG/logs/S14-session1_block1_list1.mat` at `mat.pr_trials.sequence[0]`
  with CER 0.028 against the raw typed text
  `ESTOS AIRES DE LA FRONTERA LSON MALOS`
- sequence 1 is also a real official target:
  `LA PROGRESION DE LA PATOLOGIA ES LENTA` appears exactly in multiple logs,
  including `MEG/logs/S24-session1_block1_list1.mat`,
  `MEG/logs/S3-session2_block2_list1.mat`,
  `EEG/logs/S12_session1_block2_list1.mat`, and
  `EEG/logs/S20_session2_block2_list1.mat`
- sequence 10 is closest to a shorter/list-1 style target such as
  `los arboles estimulan la secrecion`, while the selected S21 block-2 log has
  the longer target `el arbol con la compensacion estimula la secrecion`

The selected S21 MAT log's chronological `keyTrig` trial order is rows 0..65,
but the best text matches for the 13 raw typed sequences jump across row
indices:

```text
[1, 25, 55, 40, 26, 18, 39, 50, 21, 30, 37, 54, 38]
```

That means the 10/13 number is only a best-text-match score. It is not a
validated MAT trial-order alignment.

The likely acquisition issue is the raw file choice. The downloaded file:

```text
MEG/FIF/21_3660/231204/block2.fif          621,506,838 bytes
```

is a short/partial-looking S21 block-2 file. The same folder also contains:

```text
MEG/FIF/21_3660/231204/block2_1.fif      1,812,162,350 bytes
MEG/FIF/21_3660/231204/block2_2.fif      1,903,915,362 bytes
MEG/FIF/21_3660/231204/block2_2-1.fif      312,688,098 bytes
```

At this point in the investigation, the selector demoted a root `blockN.fif`
when same-folder underscore segments existed and produced this plan:

```text
MEG/FIF/21_3660/231204/block1.fif
MEG/FIF/21_3660/231204/block2_1.fif
MEG/logs/S21-session1_block1_list1.mat
MEG/logs/S21-session1_block2_list2.mat
```

estimated at 3,624,823,050 bytes. A one-block S21 plan now chooses
`block1.fif` plus its matching log, estimated at 1,812,380,618 bytes.

That two-block choice was later proven wrong by the official loader. The
current selector rejects S21 `block2.fif` and `block2_1.fif` and chooses
`block2_2.fif`; see the 2026-07-10 validation note.

Two extra S21 MEG MAT logs were downloaded for cheap pairing checks only:

```text
data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat
data/spanishbcbl_tiny/MEG/logs/S21-session2_block1_list2.mat
```

They are small log files only; no additional FIF files were downloaded.

## Baseline Smoke

These are validation artifacts, not performance claims.

Letter-cache no-brain prior smoke:

```text
exact_match_rate: 0.10833333333333334
corpus_cer: 0.8916666666666667
```

Template baseline smoke:

```text
exact_match_rate: 0.03571428571428571
corpus_cer: 0.9642857142857143
```

The low template score is acceptable for this pass. The extracted cache uses
only the first 16 MEG channels, a small event cap, and trigger-derived single
letter labels. It is a pipeline validation, not a decoder result.

Typed-key full-channel no-brain prior smoke:

```text
exact_match_rate: 0.14074074074074075
corpus_cer: 2.369419642857143
top_target: SPACE
```

Typed-key full-channel template baseline smoke:

```text
exact_match_rate: 0.007434944237918215
corpus_cer: 1.1224944320712695
```

The typed-key reports treat `SPACE` and `ENTER` as printable key labels, so the
CER values are key-classification smoke metrics, not sentence-decoding metrics.

## Artifacts

Ignored local data/artifacts:

```text
data/spanishbcbl_files_with_sizes.tsv
data/spanishbcbl_manifest_with_sizes.jsonl
data/tiny_selection.json
data/spanishbcbl_tiny/
cache/b2qmini_s21_session1_block2_stim_letter.npz
cache/b2qmini_s21_session1_block2_stim_letter.metadata.json
cache/s21_prior_report.json
cache/s21_prior_report.md
cache/s21_template_report.json
cache/s21_template_report.md
cache/b2qmini_s21_session1_block2_stim_key.npz
cache/b2qmini_s21_session1_block2_stim_key.metadata.json
cache/s21_stim_key_prior_predictions.txt
cache/s21_stim_key_prior_report.json
cache/s21_stim_key_prior_report.md
cache/s21_stim_key_template_predictions.txt
cache/s21_stim_key_template_report.json
cache/s21_stim_key_template_report.md
cache/s21_stim_key_sequence_alignment.json
cache/s21_stim_key_sequence_alignment.md
```

## Verification

```text
.venv/bin/python -m unittest discover -s tests -v
Ran 82 tests
OK (skipped=2)

.venv/bin/pytest -q
80 passed, 2 skipped

.venv/bin/ruff check .
All checks passed

.venv/bin/neurodecode extract-windows --help
shows --event-source {mat,stim-letter,stim-key}
```

The two skipped tests are Torch training smoke tests; Torch was not installed.

## Current Proof Boundary

- Real file acquisition: verified.
- Real FIF header load: verified.
- Real MAT load: verified.
- Direct MAT event-time alignment: not verified.
- Trigger-derived real letter-window cache: verified.
- Trigger-derived real typed-key full-channel cache: verified.
- Actual typed key sequence grouping: verified.
- Target-vs-actual typed sequence alignment: not trial-order verified for the
  current 621 MB `block2.fif` shard. Best text matching gives 10/13 usable
  rows, but the matched MAT row indices are not monotonic in trial order.
- MAT trial target source: corrected to `mat.pr_trials.sequence`; the 64-row
  `mat.pr_trials.sequences` field is a sequence pool, not the aligned trial
  target list.
- Baseline report plumbing on real cache: verified.
- Neural decoding performance: not claimed.

## Historical Next Recommended Action

This was the recommendation before the 2026-07-10 pass:

1. Treat the current 621 MB S21 `block2.fif` cache as a trigger-plumbing shard,
   not as a target-aligned CTC training shard.
2. Run the next real-data validation on `block1.fif` and its matching log.
3. Keep Loop 9 real-data CTC gated until a raw shard's typed sequences align
   monotonically to MAT trial order, or explicitly scope Loop 9 as synthetic-only.

That recommendation is complete: `block1.fif` passed the stricter identity
mapping and timing audit, and Loop 9 subsequently closed with the continuous
sentence-cache and synthetic CTC proofs.
