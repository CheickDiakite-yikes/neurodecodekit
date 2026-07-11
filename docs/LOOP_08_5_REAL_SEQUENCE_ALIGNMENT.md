# Loop 8.5 - Real Typed-Key Sequence Alignment

> Follow-up: `docs/REAL_DATA_VALIDATION_2026-07-10.md` clears this gate for the
> complete S21 session-1 `block1.fif`: 66/66 strict identity-ordered trial
> matches, zero duplicate target indices, zero backtracks, and 2,028 paired
> `keyTrig` timestamps with a 0.246 ms median absolute residual. The 13-sequence
> partial-shard result below remains as historical failure evidence. Loop 9 has
> since closed; see `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`.

> Report schema v3 records the assignment mechanism itself. Complete runs use
> nonempty MAT `keyTrig` slots in source order; incomplete shards fall back to
> explicitly labeled fuzzy text search and cannot clear the real-data gate.

Date: 2026-07-04 local

## Purpose

At the time of this loop, Loop 9 stayed paused until real typed key events could
be grouped into sequences and compared against MAT target sentences without
loading more raw FIF data. The follow-up banner above records the cleared gate.

This loop is intentionally lightweight:

- no new FIF downloads
- no model training
- no full-window array read for sequence grouping
- only tiny MAT logs inspected

## Implementation

Added:

```text
neurodecode align-sequences
```

The command reads only `labels`, `event_start_sec`, and metadata from an NPZ
cache, groups typed labels by `ENTER`, extracts target sequences from the MAT
log, and writes JSON/Markdown alignment artifacts.

The sequence grouping uses actual typed key triggers from the validated
`stim-key` cache. It does not use neural predictions.

Follow-up fixes:

- stim-derived event times now subtract `raw.first_samp = 51000`
- MAT target extraction now prefers `mat.pr_trials.sequence`, the 66-row target
  list aligned with `mat.pr_trials.key`
- the report also aligns raw trigger text against MAT-recorded typed responses
  reconstructed from `mat.pr_trials.key`
- the report now warns when best text matches are not monotonic in MAT trial
  order

## Real Run

Command:

```bash
neurodecode align-sequences \
  --cache cache/b2qmini_s21_session1_block2_stim_key.npz \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block2_list2.mat \
  --out-json cache/s21_stim_key_sequence_alignment.json \
  --out-md cache/s21_stim_key_sequence_alignment.md \
  --run-name s21_stim_key_sequence_alignment
```

Result:

```text
key sequences: 13
target sequences: 66
exact matches: 5
usable high/moderate matches: 10
mean CER: 0.14497806541284802
confidence counts: {'low': 3, 'high': 9, 'moderate': 1}
low-confidence indices: [0, 1, 10]
assignment strategy: best_text_similarity
keyTrig timing audit: unavailable without a strict MAT trial map
recorded-response mean CER: 0.16635701838126604
warnings:
  - strict_mat_trial_mapping_unavailable: 13 raw rows vs 66 performed MAT rows
  - best_mat_target_matches_are_not_monotonic_in_trial_order
  - best_mat_response_matches_are_not_monotonic_in_trial_order
```

Artifacts:

```text
cache/s21_stim_key_sequence_alignment.json   47,208 bytes
cache/s21_stim_key_sequence_alignment.md      5,053 bytes
```

The regenerated schema-v3 fallback audit completed in 0.458 seconds and did
not load the raw FIF. These sizes are diagnostic overhead, not new signal
storage.

Two additional S21 MEG candidate logs were downloaded for cheap pairing checks
only:

```text
data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat   211 KB
data/spanishbcbl_tiny/MEG/logs/S21-session2_block1_list2.mat   260 KB
```

No additional FIF files were downloaded.

Follow-up on 2026-07-05 expanded the MAT-only search to all 146 dataset `.mat`
logs, about 33.8 MB total. No additional raw signal files were downloaded.

That pass found:

- key sequence 0 is a real official target from another log:
  `ESTOS AIRES DE LA FRONTERA SON MALOS` in
  `MEG/logs/S14-session1_block1_list1.mat`
- key sequence 1 is a real official target present exactly in multiple logs,
  including `MEG/logs/S24-session1_block1_list1.mat` and
  `MEG/logs/S3-session2_block2_list1.mat`
- key sequence 10 is closer to the shorter/list-1 style target
  `los arboles estimulan la secrecion` than to the selected S21 block-2 target
  `el arbol con la compensacion estimula la secrecion`

The selected S21 MAT log is chronological by `keyTrig`, but the current best
target matches jump across row indices:

```text
[1, 25, 55, 40, 26, 18, 39, 50, 21, 30, 37, 54, 38]
```

So the current 13-sequence artifact validates trigger grouping and text-search
plumbing, not MAT trial-order alignment.

The likely acquisition issue at the time was that the selected raw file was the short
`MEG/FIF/21_3660/231204/block2.fif` shard, 621 MB, while the same folder
contains larger underscore block segments such as `block2_1.fif` and
`block2_2.fif`. The official loader later established that S21 block 2 must use
`block2_2.fif`; the current selector rejects both `block2.fif` and
`block2_1.fif` for this recording.

## Proof Boundary

Verified:

- typed key labels can be grouped into 13 `ENTER`-delimited sequences
- MAT target sequences can be extracted from `mat.pr_trials.sequence`
- MAT-recorded typed responses can be reconstructed from `mat.pr_trials.key`
- best text matching can be reproduced without loading the raw FIF
- the report now flags non-monotonic MAT target/response index order
- output artifacts are small and reproducible

Not verified in this historical pass:

- direct MAT event timing
- target-vs-typed trial-order alignment for the current 621 MB `block2.fif`
  shard
- whether a complete correctly paired block resolves the order mismatch
- real CTC sequence decoding

## Decision

This pass produced the needed sequence-alignment artifact, but did not yet
clear the real-data gate for Loop 9. The subsequent full-block audit did.

Historical next choices:

1. Start Loop 9 only as a synthetic CTC scaffold, with real data explicitly
   marked pending.
2. Or keep Loop 9 paused and validate a complete correctly paired S21 raw
   shard before claiming real sequence readiness.

Choice 2 was completed with `block1.fif`; see the follow-up note linked above.
