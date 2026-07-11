# Real Data Alignment Gate - 2026-07-10

## Outcome

The real-data alignment gate is cleared for one complete SpanishBCBL MEG
recording: S21, session 1, block 1.

This was enough to begin Loop 9 as a resource-bounded continuous-sentence CTC
scaffold. Loop 9 has since closed with a synthetic CTC proof and one real
sentence-cache extraction; see `docs/LOOP_09_CONTINUOUS_SENTENCE_CTC.md`. Neither
result is evidence of real neural decoding performance, a reproduction of
Brain2Qwerty v2, low-latency streaming, or thought-only text generation.

## Bounded Acquisition

The selector generated and dry-ran this exact two-file plan before execution:

```text
MEG/FIF/21_3660/231204/block1.fif              1,812,164,730 bytes
MEG/logs/S21-session1_block1_list1.mat               215,888 bytes
total                                          1,812,380,618 bytes
cap                                            2,147,483,648 bytes
```

Command:

```bash
.venv/bin/neurodecode select-tiny \
  --manifest data/spanishbcbl_manifest_with_sizes.jsonl \
  --out data/s21_session1_block1_selection.json \
  --modality MEG \
  --subject S21 \
  --blocks 1 \
  --max-files 2 \
  --max-total-gb 2

.venv/bin/neurodecode download-selection \
  --selection data/s21_session1_block1_selection.json \
  --local-dir data/spanishbcbl_tiny \
  --dry-run \
  --max-files 2 \
  --max-total-gb 2

.venv/bin/neurodecode download-selection \
  --selection data/s21_session1_block1_selection.json \
  --local-dir data/spanishbcbl_tiny \
  --execute \
  --max-files 2 \
  --max-total-gb 2
```

No other raw signal file was downloaded in this pass. The full approximately
262 GB dataset remains remote. After the pass, `data/spanishbcbl_tiny` is about
2.3 GB and the machine has about 29 GiB free.

## Raw Header Proof

MNE opened the full block without preloading signal samples:

```text
sampling rate: 2048 Hz
channels: 312
samples: 1,444,500
duration: 705.32177734375 sec
raw.first_samp: 745,500
stim channels: STI101, STI201, STI301
```

`STI101` contains 2,814 events, including 67 ENTER codes. One ENTER belongs to
the initial ASCII calibration sweep, leaving 66 completed typing trials.

## Resource-Bounded Extraction

The extractor previously used `preload=True` before channel selection. That
loaded all 312 channels even when `--max-channels 16` was requested. This pass
changed the order to:

```text
open FIF without preload -> find stim events -> pick/cap channels -> load data
-> resample -> extract windows
```

Regression coverage now verifies that the channel cap is applied before
`load_data()`.

Command:

```bash
/usr/bin/time -l .venv/bin/neurodecode extract-windows \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/b2qmini_s21_session1_block1_stim_key.npz \
  --sfreq 50 \
  --tmin -0.2 \
  --tmax 0.3 \
  --picks meg \
  --max-channels 16 \
  --event-source stim-key \
  --stim-channel STI101
```

Observed result:

```text
candidate key events: 2,233
initial sweep removed: 28
events kept: 2,205
shape: (2205, 16, 25)
cache bytes: 749,991
reported processing runtime: 3.432 sec
wall time: 3.84 sec
maximum resident set size: 533,495,808 bytes (about 509 MiB)
```

The MAT parser warning list is now deduplicated. This reduced noisy metadata
without hiding distinct warnings.

## Strict Trial-Order Alignment

Command:

```bash
.venv/bin/neurodecode align-sequences \
  --cache cache/b2qmini_s21_session1_block1_stim_key.npz \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out-json cache/s21_session1_block1_sequence_alignment.json \
  --out-md cache/s21_session1_block1_sequence_alignment.md \
  --run-name s21_session1_block1_sequence_alignment
```

Observed target result:

```text
typed sequences: 66
MAT target sequences: 66
usable high/moderate matches: 66
exact target matches: 43
mean target CER: 0.02105898040037825
target index order monotonic: True
target index mapping identity: True
target index duplicates: 0
target index backtracks: 0
assignment strategy: nonempty_mat_keyTrig_trial_order
skipped MAT trial indices: []
```

The matched target indices are exactly `0..65`. This is stronger than merely
being monotonic: no target row is duplicated, skipped, or reordered. Schema v3
stores this assignment strategy and the complete raw-to-MAT index map in the
report rather than asking readers to infer it from the text-match summary.

The metadata-only audit completed in 0.257 seconds while reading a 749,991-byte
NPZ cache and 215,888-byte MAT log. Its schema-v3 outputs are 97,883 bytes of
JSON and 13,387 bytes of Markdown. It did not read the 1.7 GB FIF signal.

Observed MAT-recorded response result:

```text
usable high/moderate matches: 66
exact response matches: 61
mean response CER: 0.002257526121162485
response index mapping identity: True
response index duplicates: 0
response index backtracks: 0
```

The target CER is not a model score. It measures the participant's raw typed
text against the prompted sentence. Trial 8 is the only moderate target match;
its raw typed phrase is substantially reworded, but it still maps to trial 8
and matches the MAT-recorded response exactly.

## The Five Trigger/Log Differences

The five non-exact raw-trigger versus MAT-response rows are trials
`[20, 25, 28, 52, 54]`. They also are the five trials whose cache key count and
MAT `keyTrig` count differ.

- Trial 20: MAT records a leading backslash that is not present in the raw
  trigger stream.
- Trials 25, 28, and 54: the MAT keyboard log records semicolon for the Spanish
  `n`-with-tilde key, while the stim stream does not emit a corresponding
  retained letter trigger.
- Trial 52: the stim stream contains the raw typo `PAPSO`; the MAT response is
  the corrected `PASO`, with no matching backspace trigger in the retained stim
  stream.

These are acquisition-channel differences, not three unexplained bad target
matches. The code preserves them instead of rewriting labels to improve a
score.

## MAT `keyTrig` Clock Audit

Sequence report schema v3 assigns raw sequences by nonempty
`mat.pr_trials.keyTrig` trial slots before comparing text. It also separately
compares cache-relative raw key times to `keyTrig`; only trials with equal key
counts contribute to the clock estimate. Text similarity is therefore a label
quality audit, not the mechanism that establishes trial identity.

```text
cache trials: 66
MAT keyTrig trials: 66
equal-length trials: 61
length-mismatch trials: [20, 25, 28, 52, 54]
paired keypresses: 2,028
run-specific clock offset: 2415.8814523212504 sec
median absolute residual: 0.2461537496856181 ms
p95 absolute residual: 0.7887316252890737 ms
maximum absolute residual: 11.966272500103514 ms
residuals within 1 ms: 2,009 / 2,028 (99.06%)
```

The offset is specific to this recording and must not be reused globally. The
sub-millisecond residuals on 2,028 ordered pairs are strong timing evidence for
this FIF/MAT pair. Target assignment remains order- and text-audited rather than
silently replacing raw times with absolute MAT timestamps.

## Official Loader Correction for S21 Block 2

The official Brain2Qwerty SpanishBCBL loader at commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0` explicitly skips S21
`block2.fif` and `block2_1.fif` and uses `block2_2.fif`.

The local selector rejects the two unusable S21 paths and never chooses a
hyphen continuation as a standalone primary. After Loop 15's split-FIFF safety
fix, it automatically includes a matching continuation beside the selected
primary. A two-block session-1 dry run selects:

```text
MEG/FIF/21_3660/231204/block1.fif
MEG/FIF/21_3660/231204/block2_2.fif
MEG/FIF/21_3660/231204/block2_2-1.fif
MEG/logs/S21-session1_block1_list1.mat
MEG/logs/S21-session1_block2_list2.mat
estimated total: 4,029,264,160 bytes
```

No block-2 raw file was downloaded in this pass.

## Brain2Qwerty v2 Reference Audit

The official v2 code became public on 2026-06-30. It confirms that the real
architectural step after synchronous key windows is continuous sentence-level
decoding:

```text
continuous MEG window -> Conv + Conformer -> character CTC
-> word-level neural/language alignment -> LoRA language model
```

Important constraints from the official code and paper:

- EnglishBCBL, the v2 training dataset, is still embargoed.
- The published preprocessing uses 0.5-45 Hz filtering, a 50 Hz notch,
  RobustScaler, value clamping, and 100 Hz signals.
- Full training used 8 A100 80 GB GPUs for about 19.5 hours.
- The sensor ablation used 76, 153, and 230 of 306 sensors for 25%, 50%, and
  75% settings. Our 16-channel cache is therefore extraction plumbing, not a
  meaningful reproduction of that ablation.
- The released v2 architecture is asynchronous but non-causal: it processes a
  complete sentence and cannot display each word with low latency. A causal
  streaming model remains future work.
- Both public studies decode activity recorded while people physically type.
  They do not establish arbitrary thought reading or a home-device result.

This changes the NeuroDecodeKit roadmap without changing its operating rule:
use the public SpanishBCBL data to build an inspectable local CTC interface,
then scale channels, sampling, data, and model complexity only when each smaller
artifact is verified.

## Loop 9 Follow-Through

Loop 9 completed this contract on 2026-07-10:

1. Built a sentence-level cache from continuous first-key-through-ENTER signal
   ranges, not a stack of isolated key windows.
2. Stored padded signals plus `input_lengths`, token targets,
   `target_lengths`, trial indices, source paths, and preprocessing metadata.
3. Proved the interface with synthetic variable-length sequences first.
4. Ran one S21 block-1 real-cache shape/label smoke with CPU-safe defaults.
5. Kept Torch optional and preserved the no-brain comparator.
6. Reported bytes, runtime, peak memory, CTC blank rate, and CER.
7. Made no neural performance claim from one block or a training-on-eval smoke.

## Loop 10 Follow-Through

The same validated FIF/MAT pair was re-extracted at 100, 50, and 25 Hz in
sequential isolated one-thread workers. All three caches preserve exact trial,
typed-target, prompt, MAT-response, and channel identity across 66 rows.

```text
100 Hz: 1,663,209 bytes, 4.121 sec, 66/66 CTC-feasible
 50 Hz:   846,334 bytes, 3.586 sec, 66/66 CTC-feasible
 25 Hz:   431,451 bytes, 3.539 sec, 66/66 CTC-feasible
```

The sweep proves resource and sequence-length behavior only. The 25 Hz cache
has a 12.5 Hz Nyquist ceiling and a 40 ms sample grid; no retained-accuracy or
real-time claim follows. It is stride-one CTC-feasible, but 0/66 rows remain
feasible under the exact official v2 kernel-16, stride-4 temporal reducer. Full
evidence: `docs/LOOP_10_SAMPLING_RATE_SWEEP.md`.

## Artifacts

```text
data/s21_session1_block1_selection.json
data/s21_two_block_selection_official.json
data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif
data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat
cache/b2qmini_s21_session1_block1_stim_key.npz
cache/b2qmini_s21_session1_block1_stim_key.metadata.json
cache/s21_session1_block1_sequence_alignment.json
cache/s21_session1_block1_sequence_alignment.md
cache/b2qsentence_s21_session1_block1_16ch_100hz.npz
cache/b2qsentence_s21_session1_block1_16ch_100hz.metadata.json
cache/loop9_real_sentence_validation.json
cache/loop10_s21_sampling_rate_sweep/sweep.json
cache/loop10_s21_sampling_rate_sweep/sweep.md
```

## Primary Sources

- Official project and code: https://github.com/facebookresearch/brain2qwerty
- Audited official commit: https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0
- Official v2 paper: https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Official project explanation: https://facebookresearch.github.io/brain2qwerty/
- SpanishBCBL dataset card and license: https://huggingface.co/datasets/bcbl190626/SpanishBCBL
- Official SpanishBCBL loader: https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py
