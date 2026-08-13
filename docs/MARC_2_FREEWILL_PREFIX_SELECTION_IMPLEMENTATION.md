# MARC2-FW1 Freewill Prefix Selection Implementation

Date: 2026-08-13

Status: **Generated/mock implementation complete and locally qualified; no
private inventory, archive, payload, signal, event, target, model, prediction,
score, or provider operation occurred**

Registry: `registries/marc2_freewill_prefix_selection_implementation.v0.json`

Module: `src/neurodecodekit/datasets/marc2_freewill_prefix_selection.py`

## Proof Order

Frozen contract commit `a12edebdab8b1252be546600d37fdb04503394d6`
passed Base Python job `94371385720` and Optional Neuro Readers job
`94371385628` in CI `31676261134` before implementation began.

The module pins the exact contract SHA-256:

```text
dfe614cd7ec27c54c4f03848e3878c714222db043f501b9b07e57c7dc9f5f702
```

It refuses if that file, contract identity, green proof, mutation order, or
acceptance inventory differs.

## What Was Implemented

The dependency-free module builds and validates a generated 1,227-row private
ZIP-directory manifest with the same schema and scale as the retained
Freewill inventory. It includes 1,025 regular rows, 202 directory rows, all
195 published eligible-session run bundles, and the 114 six-run candidate
bundles for the 19 public eligible participants.

The selector:

- replays the exact preserved DOI-bound 19-person rank;
- groups exactly four BIDS companions per run without opening content;
- fixes `ses-01` as fit and `ses-02` as held-out;
- takes only the first three numeric complete bundles per session;
- reserves each member's compressed size plus the fixed ZIP local-header
  prefix, UTF-8 name bytes, and the maximum extra-field length;
- enforces the 12-person floor and 19-person ceiling;
- stops at the first participant whose complete addition exceeds 8 GiB;
- cannot inspect a later candidate for admission, skip, substitute, backfill,
  reorder by size/CRC/quality, or increase the cap; and
- emits a private selection manifest plus an aggregate privacy-checked report.

The main fixture assigns 505,000,000 declared compressed bytes to each
participant's 24 selected companions. The maximal prefix is exactly:

```text
sub-08 sub-10 sub-07 sub-22 sub-19 sub-16 sub-14 sub-04
sub-05 sub-03 sub-09 sub-11 sub-12 sub-23 sub-20 sub-01
```

`sub-18` is the first nonfitting candidate. This is generated arithmetic, not
a claim that those real participants or bytes have been selected.

## Boundary Qualification

Four generated profiles are mandatory:

| Profile | Required result |
|---|---:|
| Floor | 12 participants; participant 13 does not fit |
| All eligible | All 19 fit |
| Exact cap | 12 participants reserve exactly 8,589,934,592 bytes |
| Cap plus one | the floor exceeds the cap and refuses at `MARC2FWG-F04` |

The main profile selected 16 participants, 96 run bundles, and 384 members. Its
reservation was 8,105,207,776 bytes, leaving 484,726,816 bytes. The complete
addition for `sub-18` was 506,575,486 bytes, so the selector stopped rather
than considering either later participant.

## Failure Localization

All 40 frozen mutations route into six stable classes:

```text
F00 contract, artifact, or green-proof mismatch        3
F01 generated inventory identity/schema/source         5
F02 path, ZIP, BIDS, or run-bundle failure             12
F03 eligibility, rank, split, or prefix-order failure  12
F04 floor, cap, reservation, or maximal-prefix failure  4
F05 privacy, output, resource, cleanup, or replay       4
```

The target firewall is structural. The module imports no network, MNE, NumPy,
Torch, scikit-learn, or model package; has no real path, URL, credential,
archive extractor, event parser, neuro reader, trainer, predictor, scorer, or
`execute` command; and exposes only:

```text
plan
qualify --output-dir <new generated directory>
inspect <aggregate generated report>
```

`inspect` rejects the private manifest. The aggregate walker rejects member
names, offsets, CRC fields, URLs, local paths, raw rows, raw headers, and BIDS
member values. Private output is mode `0600`; existing or symlink destinations
refuse; writes stage atomically and clean their own failed stage only.

## Measured Development Qualification

One fresh generated qualification used one CPU thread, one worker, and one
numerical job:

```text
generated input bytes:          846,690
aggregate report bytes:           7,580
private output bytes:            213,488
combined output bytes:           221,068
internal runtime:                0.21431241699974635 sec
reported peak RSS:               30,883,840 bytes
external wall time:              0.28 sec
external maximum RSS:            30,932,992 bytes
boundary profiles:               4 / 4
mutation refusals:               40 / 40
selected generated subjects:     16
selected generated bundles:      96
selected generated members:      384
```

The temporary qualification directory was created by the invocation and
removed when it exited. No repository artifact, private data, cache, or payload
was generated.

## Verification

Thirty focused implementation tests cover contract proof, full-scale fixture
shape, participant rank, prefix maximality, exact reservation arithmetic,
split identity, row-order replay, CRC independence, malformed rows, incomplete
bundles, all four byte boundaries, all 40 mutations, private/public separation,
strict inspection, output preflight, resource refusal, static import/interface
limits, and CLI help and plan.

Fourteen implementation-registry tests also bind the artifact hashes, green
proof, generated surface, measured main and boundary results, route counts,
resource measurements, zero authority, zero access, next gate, and claim
boundary. The complete dependency-light suite passes 2,990 tests with 204
expected optional skips. The complete optional-neuro suite passes 3,061 tests
with 35 skips. Both totals are exactly 44 tests above the green contract
baseline. Ruff, compile and import behavior, JSON parsing, and diff hygiene
pass locally.

The implementation is not eligible for a registered generated closeout until
its exact commit is pushed and both required remote CI jobs are green.

## Access Accounting

```text
retained private path operations / opens / bytes:   0 / 0 / 0
old consumed root operations:                       0
network requests / bytes:                           0 / 0
archive, local-header, or member payload reads:      0
real participant or member selections:              0 / 0
signal or event/target/quality/channel reads:        0 / 0
real derivative rows:                               0
training / inference / prediction / scoring:        0 / 0 / 0 / 0
provider / language-model / hardware operations:    0 / 0 / 0
retry / rerun / claim upgrades:                     0 / 0 / 0
```

## Next Gate

1. Commit and push this exact implementation.
2. Require Base Python and Optional Neuro Readers to pass at that commit.
3. Run one registered generated closeout and remove its temporary outputs.
4. Commit, push, and green the aggregate closeout.
5. Only then prepare one all-false Tier C request for one exact read of the
   retained 418,755-byte private inventory.

Do not open or stat the retained inventory, touch an old consumed root, make a
network request, open an archive/local header/member, access neural or target
data, run a model, score, or enter MARC2-FW2 from this implementation.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a strict generated-only
selector that maximizes a session-held-out participant prefix under an exact
storage ceiling without target, quality, or outcome selection.

Scientific claim not established: generated ZIP-directory metadata contain no
human neural signal, prediction, or score and establish no neural effect,
decoding accuracy, language decoding, or thought-to-text result.
