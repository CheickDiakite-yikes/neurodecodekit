# Loop 14 - Split Protocol v1

Status: `Done` on 2026-07-10.

Proof posture: `strict one-session sentence-text test; five test rows; no
session, subject, real-time, or arbitrary-thought claim`.

## Decision summary

The official-v2-compatible sentence-text contract produces 55 train, 6
validation, and 5 test rows with no group crossing. The first audit correctly
rejected the old recording-scaled cache. A replacement 102-magnetometer cache
now assigns membership before scaling, fits median/IQR statistics on 55 train
rows only, freezes them for validation/test, and binds preprocessing to the
exact protocol and semantic-membership hashes.

The corrected cache passes strict training readiness. The signal-free prior
and tiny CTC then consume the same report-bound row indices. The tiny CTC is a
near-null baseline: it makes 163 character edits versus the prior's 164 across
only five test sentences. The paired uncertainty interval spans substantial
benefit and harm, so no neural advantage is claimed.

Decision:

```text
strict_protocol_pass_model_near_null
```

Loop 14 closes the evaluation contract, not the decoding problem. Session and
subject evaluation remain unavailable because the cache contains one session
from one canonical person group.

## Question

Can train, validation, and test membership be deterministic and inspectable
without accidentally splitting repeated sentence text or fitting a
data-dependent transform on evaluation rows?

## Why sentence grouping matters

If the same sentence appears in both train and test, a model can benefit from
sentence repetition without demonstrating unseen-text decoding. Brain2Qwerty
v2 therefore assigns unique sentence texts to deterministic 80/10/10
partitions and keeps repeated instances of each text in the same partition.

The local protocol additionally distinguishes four possible claims:

| Split type | What it can test | Current S21 status |
|---|---|---|
| Event | Row-level plumbing only | Structurally available, not a text-generalization claim |
| Sentence text | Unseen text inside available session/person groups | Available |
| Session | Unseen session for an available person | Unavailable: one session group |
| Subject | Unseen canonical person | Unavailable: one person group |

SpanishBCBL subject aliases documented as repeated recordings of the same
person are canonicalized before subject grouping: S1/S18, S4/S14, and
S5/S10/S21.

## Exact assignment contract

`official-exact` reproduces the released NeuralSet 0.2.2 splitter semantics:

```text
SHA-256(exact sentence string)
-> base-16 integer
-> random.Random(hashed_integer + float_seed).random()
-> first cumulative split ratio above the score
```

The default seed is the float `0.0`, and the ordered ratios are train 0.8,
validation 0.1, and test 0.1. The float behavior is preserved intentionally;
changing it to an integer seed changes membership because Python converts the
large digest-derived integer during addition.

`canonical-v1` is a stricter local grouping option. It applies Unicode NFKC,
case folding, whitespace collapse, and trim before hashing. It can prevent
superficial spelling-format variants from crossing partitions, but it is not
bit-identical to the official exact-string split.

## Implementation

Loop 14 adds:

- `neurodecodekit.evaluation.split_protocol`
- `neurodecode split-protocol`
- standard and packed sentence-cache support
- deterministic protocol, group-assignment, and row-membership hashes
- duplicate semantic-row detection across signal representations
- canonical SpanishBCBL person aliases
- explicit event/sentence/session/subject capability labels
- preprocessing fit-scope findings
- train-row-only robust-scaler fit/apply functions that preserve zero padding
- scaler center/scale values, hashes, fit rows, and valid-fit-timepoint counts
- strict report-to-cache SHA-256 validation for training partition loading
- explicit-membership tiny CTC training and evaluation
- `neurodecode sentence-prior-baseline`, which never loads signal arrays
- paired neural-versus-prior edit deltas and sentence-bootstrap uncertainty
- overwrite protection and exact report-byte accounting
- JSON and Markdown reports that omit sentence plaintext

The loader reads only these NPZ members:

```text
target_texts
reference_texts
mat_response_texts
trial_indices
metadata
```

It never indexes or decompresses `signals` or `signal_payload`. The complete
cache file is streamed once for its physical SHA-256 provenance hash.

## Stage A - initial membership audit

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
neurodecode split-protocol \
  --cache cache/loop11_s21_channel_subset/base_102mag_100hz.npz \
  --out-dir cache/loop14_s21_split_protocol \
  --split-type sentence-text \
  --text-source reference \
  --text-normalization official-exact
```

This first audit opened no raw FIF, installed no dependency, wrote no signal
cache, and trained no model. Its purpose was to expose the old fit-scope defect.

## Initial result

Source:

```text
cache/loop11_s21_channel_subset/base_102mag_100hz.npz
SHA-256: 70f6d54441d2abdd6dab8cb7ce8410fd674ac28e75b0645102197de99157d19d
rows: 66
unique exact reference-text groups: 66
canonical person group: spanishbcbl-person-s5-s10-s21
session groups: 1
subject/person groups: 1
```

Membership:

| Partition | Rows | Sentence groups |
|---|---:|---:|
| Train | 55 | 55 |
| Validation | 6 | 6 |
| Test | 5 | 5 |

Integrity checks:

```text
missing group rows: 0
empty partitions: 0
requested-group cross-split count: 0
canonical reference-text cross-split count: 0
duplicate semantic row IDs: 0
signal array members loaded: false
```

Durable identities:

```text
protocol config SHA-256:
503ec4e77c64dea4b30b435e48fa0ec21279b61630dde5081a2a1e917388002d

group assignment SHA-256:
ea978a8c43f627a38c3b79ecbc6e815202fc15083329b5d2f0c042e221242dba

membership SHA-256:
50471fe9c3d30efea3ca15aa8a91d6ba979580accbb520e01c1d87b4ac103733
```

Resources for the final run:

```text
runtime: 0.039339 sec
peak process RSS: 46,825,472 bytes
JSON report: 60,219 bytes
Markdown report: 3,219 bytes
total report bytes: 63,438
new signal-cache bytes: 0
```

Evidence:

- `cache/loop14_s21_split_protocol/split.json`
- `cache/loop14_s21_split_protocol/split.md`

## Fit-scope result

The cache declares an enabled `per_channel_robust_scaler` but does not declare
`fit_split=train`. The audit therefore reports:

```text
requested split usable: true
strict train-only fit ready: false
strict training ready: false
```

The required next change is to compute data-dependent scaler statistics from
train rows only and freeze them for validation/test, or explicitly document a
transductive per-recording protocol. Variance-ranked channel selection has the
same requirement: rank channels on train rows, then freeze the selected list.

That initial blocker is preserved as evidence above. It was resolved for the
fixed 102-magnetometer base as follows.

## Stage B - train-only preprocessing

The replacement extraction assigns reference-text membership before fitting
the scaler:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
neurodecode extract-sentence-cache \
  --raw data/spanishbcbl_tiny/MEG/FIF/21_3660/231204/block1.fif \
  --events data/spanishbcbl_tiny/MEG/logs/S21-session1_block1_list1.mat \
  --out cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --sfreq 100 --picks mag --max-channels 102 \
  --scaler-fit-scope train \
  --split-text-normalization official-exact
```

The scaler concatenates valid, unpadded timepoints from the 55 train rows only.
It records 23,669 fit timepoints, all 55 row/trial indices, all 102 centers and
scales, and deterministic hashes of the statistics. Frozen statistics are then
applied to train, validation, and test rows while padded samples remain exactly
zero.

Observed extraction:

```text
shape: 66 x 102 x 617
train/validation/test rows: 55/6/5
cache bytes: 10,632,576
runtime: 10.969796 sec
peak RSS: 1,746,010,112 bytes
zero-IQR channels: 0
new cache versus old cache: +30,008 bytes
```

Validation against the old cache:

```text
all non-signal arrays: exact
all zero padding: exact
largest absolute train-channel median: 0
train-channel IQR range: 0.99999991 to 1.00000009
old/new valid-signal correlation: 0.998018
```

The old/new signal difference is expected because the estimator population is
different. Correlation is a transformation sanity check, not retained-decoder
evidence.

## Stage C - strict audit and report binding

The same official-exact audit on the replacement cache reports:

```text
requested split usable: true
strict train-only fit ready: true
strict training ready: true
fit findings: 1 pass, 0 unresolved/failed
decision: ready_for_training_protocol_integration
```

Durable identities:

```text
cache SHA-256:
45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815

protocol config SHA-256:
503ec4e77c64dea4b30b435e48fa0ec21279b61630dde5081a2a1e917388002d

group assignment SHA-256:
ea978a8c43f627a38c3b79ecbc6e815202fc15083329b5d2f0c042e221242dba

semantic membership SHA-256:
2382bd42f09630591ccbd1405e24e3aaf9035f8fec06eb05273a2596fde17dd7

physical membership SHA-256:
4feb3854161c7f336a73c3d3ae5d7e67ac6ec11825de6370df1387c8f949ea85
```

Training and prior commands refuse a report whose physical cache hash differs,
whose rows do not cover the cache exactly once, or whose strict-readiness flag
is false.

## Stage D - first strict test baselines

Both baselines use the same 55 train rows and five test rows. Six validation
rows are reserved and are not used for restart or hyperparameter selection.

The prior reader loads only text/trial NPZ members:

```bash
neurodecode sentence-prior-baseline \
  --cache cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz \
  --split-report cache/loop14_s21_split_aware/split/split.json \
  --eval-partition test \
  --strategy most-frequent
```

The tiny CTC uses the existing fixed local defaults except for one explicit
initialization to avoid a hidden search: 60 epochs, batch 16, learning rate
0.02, width 16, seed 7, CPU, one thread, and one restart maximum.

| Metric | Prior only | Tiny CTC |
|---|---:|---:|
| Test sentences | 5 | 5 |
| Character edits | 164 | 163 |
| Corpus CER | 0.953488 | 0.947674 |
| Corpus WER | 1.4 | 1.0 |
| Exact sentences | 0 | 0 |
| Train CER | n/a | 0.925469 |
| Test blank fraction | n/a | 0.868132 |
| Parameters | 0 neural | 2,908 |
| Model runtime | signal-free | 6.475226 sec |
| Model peak RSS | signal-free | 462,913,536 bytes |

Paired tiny-CTC-minus-prior result:

```text
CER delta: -0.005814
character-edit delta: -1
sentence wins/ties/losses: 2/0/3
5,000-sample paired sentence-bootstrap 95% interval: [-0.197279, 0.130653]
bootstrap probability tiny CTC is better: 0.509
```

This is a near-null result. The model barely fits train, emits mostly blanks,
beats the prior by one character edit, loses on three of five sentences, and
has an uncertainty interval spanning meaningful benefit and harm. It does not
support a neural-signal advantage claim.

Final evidence:

- `cache/loop14_s21_split_aware/extraction_summary.json`
- `cache/loop14_s21_split_aware/split/split.json`
- `cache/loop14_s21_split_aware/prior/report.json`
- `cache/loop14_s21_split_aware/tiny_ctc/report.json`

## Normalization sensitivity

A temporary signal-free comparison using `canonical-v1` produced 54/6/6
instead of 55/6/5. All 66 current references remain unique under both modes;
the difference comes from hashing normalized rather than exact strings. The
official-exact artifact is retained as the official-v2 parity result. Future
reports must name the normalization mode rather than treating the two
memberships as interchangeable.

## Privacy boundary

Sentence values are not written to the split reports. Group IDs are SHA-256
digests. Those digests are stable identifiers, not anonymization: a known or
guessable sentence can be hashed for comparison. Keep local source paths and
membership reports under the same data-handling posture as derived dataset
metadata.

## Acceptance status

Loop 14 acceptance is complete:

- official-v2-compatible deterministic assignment has reference tests
- every report records algorithm, version, ratios, seed, and normalization
- repeated text groups cannot cross requested partitions
- duplicate underlying rows across cache representations are detected
- session/subject limitations are machine-readable
- robust scaling is fitted on train rows and hash-bound to audited membership
- CTC and prior reports consume the exact same physical-cache membership
- the paired model comparison includes uncertainty rather than only point scores
- reports are signal-free and storage-bounded

Remaining gates after Loop 14, updated after Loop 15 Stage A:

- fit variance sensor selection on train rows before evaluating that candidate
- same-subject second-session acquisition is complete; the fixed baseline fails
  transfer and that observed session must remain frozen
- acquire multiple canonical people before a subject-level claim
- improve the near-null neural baseline on synthetic/source validation without
  selecting on the five source test rows or 63 session-2 rows
- design and measure a causal model before any real-time claim

See `docs/LOOP_15_SAME_SUBJECT_CROSS_SESSION.md`.

## Verification snapshot

Run sequentially with numerical thread caps on 2026-07-10:

```text
python -m unittest discover -s tests
  147 tests passed; 3 skipped

python -m pytest -q
  144 passed; 3 skipped; 21 subtests passed

ruff check .
  clean

python -m compileall -q src tests
  clean

git diff --check
  clean

neurodecode --help
neurodecode extract-sentence-cache --help
neurodecode split-protocol --help
neurodecode sentence-prior-baseline --help
neurodecode tiny-ctc-baseline --help
  clean

workbook visual QA
  7/7 sheets rendered; 0 formula-error matches
```

## Claim boundary

This result proves a strict unseen-sentence-text protocol and records one tiny
real-cache CER/WER comparison. Five test sentences from one recording are too
few for a stable performance estimate, and the neural delta is near zero. It
is not a session or subject generalization result and is not evidence of
low-latency, at-home, or arbitrary-thought decoding.

## Primary sources

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Official v2 split transform at the pinned source commit:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/transforms.py
- Official v2 split ratios at the pinned source commit:
  https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/xp_config.py
- SpanishBCBL dataset card and repeated-subject mapping:
  https://huggingface.co/datasets/bcbl190626/SpanishBCBL
