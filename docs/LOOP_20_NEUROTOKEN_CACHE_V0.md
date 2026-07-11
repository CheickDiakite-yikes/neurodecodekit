# Loop 20 - NeuroTokenCache v0 Interface

Completed on 2026-07-10 as a synthetic interface and serialization proof. No
real neural cache, observed holdout, model, training loop, or unreleased
Brain2Qwerty v2 data was opened.

## Question

Can NeuroDecodeKit define a small modality-aware contract for future neural
embeddings without pretending that a random projection is a learned brain
representation or that asynchronous decoding is already real-time streaming?

## Official v2 Contract Used

The implementation is pinned to the public Brain2Qwerty v2 code at commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0`:

- the data batch pads neural signals as time-major `neuros [batch,time,channel]`
  with lengths, subject/day IDs, and channel positions;
- the encoder exposes per-frame `z_final [batch,time,embedding]` beside its CTC
  output;
- the published configuration starts from 100 Hz and uses a temporal kernel of
  16 samples with stride 4;
- the public encoder is noncausal and operates on a whole sentence. Removing
  keypress alignment makes it asynchronous, but does not make it streaming;
- the EnglishBCBL training data is not public, and the full public training
  recipe assumes CUDA-scale hardware.

Primary references:

- https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/models.py
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py
- https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

The causal-streaming distinction is also consistent with the public
EMG2QWERTY paper, which discusses causal methods for streaming but measures a
different sEMG modality, not brain data:

- https://papers.neurips.cc/paper_files/paper/2024/file/a64d53074d011e49af1dfc72c332fe4b-Paper-Datasets_and_Benchmarks_Track.pdf

## NeuroTokenCache v0

`src/neurodecodekit/cache/neurotoken.py` defines a compressed NPZ schema with
continuous frame embeddings:

```text
tokens                         [items, time, embedding]
token_lengths                  [items]
token_mask                     [items, time]
token_start_sec                [items, time]
token_end_sec                  [items, time]
item_ids                       [items]
split_labels                   [items]
source_row_indices             [items]
source_trial_indices           [items]
source_input_lengths           [items]
source_start_sec               [items]
source_end_sec                 [items]
subject_ids                    [items]
session_ids                    [items]
source_channel_names           [source_channels]
source_channel_positions       [source_channels, 3]
source_channel_position_mask   [source_channels]
metadata                       JSON
```

The schema rejects inconsistent masks, nonzero padded vectors, invalid padded
timestamps, timing outside the source item, duplicate item/source indices,
invalid geometry, incomplete provenance, or a split report that is not bound
to the exact source-cache SHA-256.

Metadata separates four ideas that must not be collapsed:

1. `asynchronous_input`: token production does not require keypress timestamps.
2. `producer_causal`: this specific mock frame producer uses samples only up to
   the frame end.
3. `downstream_decoder_causality`: currently `unspecified`.
4. `end_to_end_latency_measured`: currently `false`.

Modality, device type, sampling rate, source geometry and availability mask,
subject/session IDs, strict split hashes, transformations, source hashes,
resource caps, official-v2 mapping, warnings, and claim boundaries are all
required or normalized into the artifact.

## Synthetic Producer

The smoke producer frames existing synthetic sentence signals and applies a
seeded PCG64 Gaussian projection. It performs no fitting, training, target-text
read, or target-token read. It exists only to validate the future encoder/cache
boundary.

At 100 Hz with kernel 16 and stride 4, its frame width is 160 ms and step is
40 ms. That is the producer's minimum frame-availability latency, not measured
decoder, language-model, device, or end-to-end latency.

Safety defaults and controls:

- 128 source items maximum;
- 4,096 tokens per item maximum;
- 32 MiB projected/written output maximum;
- float32 or float16 output only;
- existing cache, metadata, and summary outputs are refused unless
  `--overwrite` is explicit;
- NumPy remains optional and is imported only inside NeuroTokenCache functions.

## CLI

```bash
neurodecode make-neurotoken-cache \
  --source-cache cache/loop20_neurotoken/source_sentences.npz \
  --split-report cache/loop20_neurotoken/split/split.json \
  --out cache/loop20_neurotoken/neurotokens_v0.npz \
  --metadata-out cache/loop20_neurotoken/neurotokens_v0.metadata.json \
  --summary-json cache/loop20_neurotoken/neurotokens_v0.summary.json \
  --modality synthetic \
  --device-type synthetic-array \
  --subject-id SYN-1 \
  --session-id SESSION-1 \
  --embedding-dim 32 --kernel-size 16 --stride 4 --seed 23 \
  --max-items 64 --max-tokens-per-item 128 --max-output-mb 4

neurodecode inspect-neurotoken-cache \
  --cache cache/loop20_neurotoken/neurotokens_v0.npz
```

## Observed Smoke

```text
source sentences:                 48 x 5 x 77 float32, padded
strict split:                     37 train / 4 validation / 7 test
token cache:                      48 x 16 x 32 float32, padded
valid token frames:               553
padding fraction:                 0.279948
positioned source channels:       0 / 5, explicitly unavailable
source cache bytes:               59,357
token cache bytes:                76,646
metadata sidecar bytes:           11,369
complete primary artifact dir:    204 KiB
wall time / peak RSS:             0.09 sec / 44,564,480 bytes
model / training / real reads:    0 / 0 / 0
end-to-end latency measured:      false
```

Hashes:

```text
source cache SHA-256:
2067df679a23fa8dbe2f1a7a3d8365a21644d027a0d215216def152301fe66f8

split report SHA-256:
90b31b706e1c9f60712410066db19aa2a3ca5f9581b8267c30491db7740cabc1

token payload SHA-256:
82b478948bdcfd5b2d12643f9f912c192a8977c8f0554b9f073171cf6dfe2709
```

An independent replay produced the same token payload hash. Whole NPZ bytes
differ because measured runtime/resource metadata is intentionally variable;
the numerical payload and semantic membership are stable.

The NPZ contains 17 typed arrays plus metadata. It contains no `target_texts`
or `target_token_ids` member.

## Post-Closeout Selective-Access Audit

A later access-level audit found that the original synthetic producer used the
general sentence-cache loader. The projection never consumed target values,
but that loader still opened the source target arrays in memory. Commit
`389efe3` replaces it with a projection-only reader that opens exactly these
seven NPZ members:

```text
metadata
signals
input_lengths
trial_indices
sentence_start_sec
sentence_end_sec
channel_names
```

The reader verifies that the five required target members exist in the source
contract without indexing or loading them: `target_token_ids`,
`target_lengths`, `target_texts`, `reference_texts`, and
`mat_response_texts`. A regression test wraps `numpy.load`, records every
source-member access across two deterministic projections, and fails if any
target member is opened. The saved metadata now records both member lists and
sets `target_text_array_opened` and `target_token_array_opened` to `false`.

An independent bounded replay was written to the ignored local audit directory
without replacing the primary Loop 20 artifact:

```text
input cache bytes:                 59,357
token cache / metadata bytes:      76,825 / 11,992
token shape / valid frames:        48 x 16 x 32 / 553
padding fraction:                  0.279948
runtime / internal peak RSS:       0.069754 sec / 43,401,216 bytes
external maximum RSS:              43,548,672 bytes
raw / real-cache reads:            0 / 0
synthetic source-cache reads:      1
model / training runs:             0 / 0
producer causal:                   true
end-to-end latency measured:       false
payload replay:                    exact
```

The source, split-report, and payload hashes remain exactly the values above.
The remaining configuration/provenance hashes are:

```text
semantic configuration SHA-256:
df21cf660e07d24720e152585220b0eb4f8e1a3134aac110da1302f2d786fd7c

projection weights SHA-256:
662294774579675dcb838f41bdc998a103aa79bd68d4686daf4f1d9c7c20ba8d

split protocol config SHA-256:
503ec4e77c64dea4b30b435e48fa0ec21279b61630dde5081a2a1e917388002d

split semantic membership SHA-256:
23841cce0cb31057788385f039c91f797c5f169fc9a17b37ba24e3e597704fe1
```

All validate on load. The cache-plus-sidecar increase is 802 bytes and the
total remains far below the declared 32 MiB cap.

The complete replay warning set is:

- `continuous_neurotokens_are_not_discrete_codes`
- `mock_random_projection_is_not_a_learned_neural_representation`
- `mock_projection_uses_no_target_text_or_target_labels`
- `source_target_members_verified_present_but_not_opened`
- `cache_contract_does_not_establish_decoding_accuracy`
- `official_v2_reference_encoder_is_noncausal_whole_sentence`
- `real_time_requires_a_causal_decoder_and_measured_end_to_end_latency`
- `not_arbitrary_thought_decoding`
- `some_or_all_source_channel_geometry_unavailable`
- `synthetic_source_only_no_real_neural_representation_claim`

Clean-commit verification at `389efe3` preserved the pre-change totals: 199
unittest tests passed with 3 skipped; pytest reported 196 passed, 3 skipped,
and 25 subtests passed. Full Ruff, compileall, root and Loop 20 CLI help, the
bounded create/inspect round trip, and `git diff --check` also passed under
one-thread numeric limits.

## Acceptance Result

- stable continuous embedding, timing, mask, identity, split, geometry, and
  provenance contract: passed;
- exact official-v2 `z_final` layout mapping documented: passed;
- strict source/split hash binding: passed;
- deterministic target-free synthetic producer: passed;
- hard item/token/byte caps and collision refusal: passed;
- synthetic CLI create/inspect round trip: passed;
- no real holdout, model, training, or network access: passed;
- learned-neurotoken or decoding-value claim: not made;
- streaming decoder or end-to-end latency claim: not made.

Full closeout verification: 191 unittest tests passed with 3 skipped; pytest
reported 188 passed, 3 skipped, and 21 subtests passed. Ruff, compileall,
dependency-light import, CLI help, artifact reconciliation, `git diff --check`,
workbook formula scan, and all-seven-sheet visual QA passed. The tracked and
delivered workbook SHA-256 is
`dce9e92f02e5937d5e822f9facd6f659d2f840182c05be6e1dd912c79fa3bd59`.

## Decision

Loop 20 is complete as an interface proof. `NeuroTokenCache v0` is a useful
future encoder boundary, but the saved vectors are mock continuous embeddings,
not discrete neural words and not a trained representation.

The next research gate should test a genuinely causal chunk/replay contract on
synthetic streams: fixed chunk boundaries, exact offline-versus-streaming
equivalence where promised, declared right context, bounded state, and measured
producer latency. A learned encoder, real-cache conversion, or decoder score
should remain separate until that interface gate passes.

That gate subsequently passed in post-roadmap Loop 21 with five schedules,
zero right context, 300-byte mutable state, and explicit transport-delay versus
compute accounting. See `docs/LOOP_21_CAUSAL_CHUNK_REPLAY.md`.
