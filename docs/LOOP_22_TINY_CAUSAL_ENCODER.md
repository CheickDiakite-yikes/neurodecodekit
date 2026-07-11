# Loop 22 - Tiny Learned Causal Encoder Gate

Completed on 2026-07-10 as a preregistered synthetic mechanism gate. The
registered synthetic test partition was opened once after validation selection
and checkpoint freeze. No real neural cache, raw recording, observed MEG/EEG
holdout, text target, decoder, language model, or network service was opened.

## Question

Can one very small train-only causal encoder learn an intentionally simple
synthetic temporal motif task while preserving Loop 21's exact incremental
state and chunk-replay contract?

This question is narrower than brain-to-text. Passing shows that the local
training, selection, serialization, access, and streaming machinery works
together under fixed caps. It does not show that the learned representation is
useful for MEG, EEG, characters, words, or real-time communication.

## Research Basis

The public Brain2Qwerty v2 implementation and paper were rechecked before the
gate. The local design preserves only a few relevant contracts:

- deterministic train/validation/test separation;
- validation-selected checkpointing before test access;
- 100 Hz input with kernel-16/stride-4 temporal frames;
- continuous encoder embeddings beside a diagnostic prediction head;
- explicit separation between asynchronous input, causal production, and
  user-visible text latency.

The public v2 encoder is much larger and uses a noncausal whole-sentence
Conformer. Its paper identifies fully low-latency operation as future work.
Loop 22 therefore uses a finite-history window MLP rather than claiming
architectural equivalence.

Primary sources:

- https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py
- https://ai.meta.com/research/publications/emformer-efficient-memory-transformer-based-acoustic-model-for-low-latency-streaming-speech-recognition/
- https://docs.pytorch.org/docs/stable/notes/randomness.html
- https://docs.pytorch.org/docs/stable/generated/torch.set_num_threads.html

The fixed protocol was committed before fixture generation in
`docs/LOOP_22_PREREGISTRATION.md` at commit `9a40c7e`. The implementation was
tested with alternate seeds and committed as `57d3ad8` before the registered
seed-2203 test file was created or opened.

## Interface Added

Loop 22 adds three bounded layers:

1. `b2q-causal-motif-fixture` version 0 stores physically separate train,
   validation, and test NPZ files plus a compact hash-bound manifest.
2. `tiny-causal-encoder-checkpoint` version 0 stores plain numeric NumPy arrays
   with `allow_pickle=False`, train-only normalization, config hash, parameter
   hash, split hashes, selected epoch, and geometry.
3. `b2q-tiny-causal-encoder-gate` version 0 records model selection, controls,
   one-time test access, five-schedule replay, resources, warnings, and the
   proceed/park decision.

The partition loader reads each NPZ file into bytes once, checks its SHA-256,
rejects extra members, validates every mask/length/label/frame relation, and
rebinds every manifest statistic to loaded content. Tests count physical test
file reads: a successful alternate-seed rehearsal reads test once, while a
forced validation failure reads it zero times.

CLI:

```bash
neurodecode make-causal-motif-fixture \
  --out-dir cache/loop22_tiny_causal_encoder/fixture \
  --max-total-mb 1

neurodecode inspect-causal-motif-fixture \
  --manifest cache/loop22_tiny_causal_encoder/fixture/manifest.json

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
neurodecode tiny-causal-encoder-gate \
  --fixture-manifest cache/loop22_tiny_causal_encoder/fixture/manifest.json \
  --checkpoint-out cache/loop22_tiny_causal_encoder/checkpoint.npz \
  --out-json cache/loop22_tiny_causal_encoder/gate.json \
  --out-md cache/loop22_tiny_causal_encoder/gate.md
```

All commands refuse to replace their registered outputs.

## Registered Fixture

The fixture was generated once after implementation rehearsal:

```text
schema / version:                  b2q-causal-motif-fixture / 0
protocol SHA-256:                  2be7ce788e651f63de9169b3616e84b42a20c43830a79460fa07e7a76ce9dc31
manifest SHA-256:                  9691566dd57314fa7e13acf8ec637725d11fe91017b2af2d79a53ad6df4c17d8
train / validation / test items:   64 / 8 / 8
train / validation / test frames:  1,273 / 161 / 164
channels / maximum samples:        5 / 112
manifest bytes:                    4,075
train / validation / test bytes:   114,677 / 16,914 / 17,117
total fixture bytes:               152,783 of 1,048,576
generation runtime / peak RSS:     0.13 sec / 42,221,568 bytes
```

Partition SHA-256 values:

```text
train:       8f0e5f2b87518e3477ce7fe57fb94077f19dd17942deed92b559c1d73e4eb2ea
validation:  e1ee33fd64d04e0e07d1be3bed8a411dbb1e94ea8dea206fb608c1f9d8f06f46
test:        e5d6891c3f15dab4e6771ba84761ca52bed0d48e0ebde68a9717dfb1f3350f45
```

The metadata-only inspection validated the registered protocol, byte
accounting, relative paths, item IDs, shapes, frame counts, class support,
seeds, and hashes without opening any partition arrays.

## Registered Model And Selection

The only model was the preregistered shared-window MLP:

```text
5 x 16 causal frame -> Linear(80,12) -> GELU
                    -> Linear(12,8)  -> GELU embedding
                    -> Linear(8,6) diagnostic motif probe
```

```text
encoder / probe / total parameters:  1,076 / 54 / 1,130
parameter bytes:                     4,520
fixed model plus normalization:      4,560 bytes
model seed / candidates / restarts:  2221 / 1 / 0
selected epoch / epochs run:         34 / 42, early stopped
config SHA-256:                      8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2
checkpoint bytes:                    7,894 of 65,536
checkpoint SHA-256:                  75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
parameter payload SHA-256:           d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
```

Normalization, class weights, optimizer updates, and model parameters used
train rows only. Validation selected the epoch. Test metrics did not select or
change anything.

## Validation And Frozen Test

```text
                                      validation       frozen test
learned accuracy                      1.000000         1.000000
learned balanced accuracy             1.000000         1.000000
train-only prior accuracy             0.366460         0.365854
train-only prior balanced accuracy    0.166667         0.166667
zero-signal accuracy                  0.366460         0.365854
zero-signal balanced accuracy         0.166667         0.166667
accuracy gain over stronger control   0.633540         0.634146
balanced gain over stronger control   0.833333         0.833333
```

The frozen test's paired 2,000-resample item bootstrap accuracy-gain interval
over the prior was `[0.630906, 0.635766]`; its lower bound is positive. All
registered validation and test thresholds passed.

This near-trivial result is expected: the generated task places strong,
channel-specific motifs directly in each frame and exists to test mechanism,
not representation difficulty. It must not be compared with CER, WER, MEG,
EEG, or human communication performance.

## Causal Replay

The validation embeddings were replayed under all five Loop 21 schedules:

```text
frames / schedules / pushes:          161 / 5 passed / 1,194
embedding payload SHA-256:            dc0456d2fab5f51bd6ffb8058b7672bb7fd7ee509c56d92b539ca2464dfd5708
schedule embedding bits:              identical
frame indices and availability:       exact and causal
right context:                        0 samples
maximum mutable array state:          300 bytes of 1,024
batch/canonical embedding error:      0.0 at 1e-6 tolerance
batch/canonical logit error:          0.0 at 1e-6 tolerance
```

Maximum scheduling delay was 0 ms for single-sample, stride-aligned, and
kernel-then-stride delivery; 140 ms for jittered delivery; and 960 ms for
whole-item delivery. The highest measured producer compute RTF was 0.002041.
The canonical validation inference RTF was 0.000820. These exclude sensor
capture, causal preprocessing, character decoding, endpointing, rendering,
and user-perceived latency.

## Resources And Access

```text
training / pre-report runtime:         4.354204 / 5.105284 sec
external total wall time:              5.50 sec of 30
internal / external peak RSS:          307,724,288 / 313,982,976 bytes
working core arrays:                   700,432 bytes of 16 MiB
checkpoint / JSON / Markdown:          7,894 / 34,849 / 1,458 bytes
total report artifacts:                44,201 bytes of 1 MiB
fixture plus report artifacts:         196,984 bytes
numeric threads:                       1
training runs / model candidates:      1 / 1
initialization restarts:               0
train / validation / test opens:       1 / 1 / 1
raw / real / text-target reads:        0 / 0 / 0
network fetches:                       0
free disk before run:                  about 15 GiB
```

Access events are ordered and saved: manifest validation, train open,
validation open, train-only fit, validation selection, checkpoint freeze, test
open, frozen test evaluation. The seed-2203 test is now consumed and must not
be reopened for tuning or rerun as a fresh evaluation.

## Warnings And Claim Boundaries

Every saved warning:

- `synthetic_supervised_motif_task_only`
- `tiny_model_mechanism_gate_not_brain_decoding_quality`
- `probe_metrics_are_frame_classification_not_cer_or_wer`
- `checkpoint_npz_contains_plain_numeric_weights_no_pickle`
- `end_to_end_latency_unmeasured`
- `real_neural_holdouts_remain_frozen`

Unavailable or unproven:

- character, word, CTC, or language-model decoding;
- CER, WER, semantic accuracy, and partial-hypothesis stability;
- causal real-neural preprocessing;
- real MEG/EEG representation quality or neural advantage;
- same-person or unseen-person transfer;
- capture, endpoint, render, and end-to-end text latency;
- portable, OPM-MEG, at-home, clinical, or arbitrary-thought operation.

## Verification

- focused Loop 22 fixture/model/gate tests: 10 passed;
- full unittest discovery: 209 passed and 3 skipped;
- full pytest: 206 passed, 3 skipped, and 25 subtests passed;
- full Ruff, compileall, dependency-light imports, root CLI help, all three
  Loop 22 command helps, and `git diff --check`: passed;
- dependency-light imports loaded no NumPy, Torch, or MNE;
- a full-size alternate-seed rehearsal passed every mechanical and resource
  gate before the registered run;
- the registered fixture create, metadata-only inspect, and one-time gate
  passed without download or real-data access;
- all later tests use alternate seeds and do not reopen the registered fixture.

## Decision

Loop 22 passes as a synthetic learned-encoder mechanism gate. It authorizes
only a separately preregistered Loop 23 synthetic streaming CTC/prefix-decoder
gate using a new protocol and frozen model contract.

It does not authorize real-cache conversion, reuse of the consumed Loop 22
test, a larger architecture, a language model, or any brain-decoding claim.
