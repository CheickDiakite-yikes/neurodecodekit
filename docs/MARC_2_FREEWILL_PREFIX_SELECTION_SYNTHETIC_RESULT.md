# MARC2-FW1 Generated Prefix Selection Result

Date: 2026-08-13

Status: **One registered generated closeout passed at `MARC2FWG-R1` and is
consumed; no retry or rerun is available**

Machine result:
`registries/marc2_freewill_prefix_selection_synthetic_result.v0.json`

## Result In One Line

The generated-only selector recovered the exact maximal 16-person contiguous
rank prefix under the frozen 8-GiB reservation, passed all storage, privacy,
replay, resource, and refusal gates, and removed its temporary outputs without
opening the retained private inventory or any real payload.

## Proof Order

Exact implementation commit
`36f87759967f03dd7ac5d543f6f5a24afb571365` passed Base Python job
`94375991713` and Optional Neuro Readers job `94375991770` in CI
`31677757466` before the sole registered closeout.

The tracked worktree was at that exact HEAD. The only unrelated workspace item
was the maintainer's pre-existing untracked tracker-inspection sidecar; it was
not opened, staged, modified, or deleted by this execution.

The closeout used one CPU thread, one worker, one numerical job, no network,
and an invocation-owned temporary directory. It opened only generated fixture
objects and its own aggregate/private generated outputs.

## Selection Result

The generated main fixture selected this exact public rank prefix:

```text
sub-08 sub-10 sub-07 sub-22 sub-19 sub-16 sub-14 sub-04
sub-05 sub-03 sub-09 sub-11 sub-12 sub-23 sub-20 sub-01
```

Aggregate counts were:

```text
eligible participants:                     19
selected participants:                     16
candidate participants examined:           17
first nonfitting participant:              sub-18
fit / held-out run bundles:                48 / 48
selected run bundles:                      96
selected core members:                     384
selected reservation bytes:                8,105,207,776
reservation cap bytes:                     8,589,934,592
remaining reservation bytes:                 484,726,816
first nonfitting reservation bytes:          506,575,486
```

The next complete participant addition exceeded the remaining allowance by
21,848,670 bytes. The selector stopped; it did not skip to either later-ranked
participant. These are generated fixture values, not a real cohort selection.

## Boundary And Refusal Result

All four registered boundaries passed:

- floor profile selected exactly 12 participants;
- all-eligible profile selected all 19;
- exact-cap profile reserved exactly 8,589,934,592 bytes; and
- cap-plus-one refused at `MARC2FWG-F04`.

All 40 mutations refused in their frozen classes:

```text
F00  3
F01  5
F02 12
F03 12
F04  4
F05  4
```

Canonical and reverse-row fixture runs produced byte-identical private outputs
and identical aggregate hashes. The public report passed its privacy walk and
the private fixture remained mode `0600` until cleanup.

## Measurements

```text
registered executions:              1
generated input bytes:              846,690
aggregate report bytes:               7,580
private generated output bytes:     213,488
combined generated output bytes:    221,068
internal runtime:                   0.21099908299947856 sec
reported peak RSS:                  32,047,104 bytes
external wall time:                 0.27 sec
external maximum RSS:               32,096,256 bytes
aggregate report SHA-256:           29eca9025cedf8dfffe69dc761cf3432c835d4dd847c4fefc7d455b5eb0cd13a
private output SHA-256:              da772ea045520a24c11b144af27d341115e7b082861b9c28299981fccd4a2bba
temporary root exists after cleanup: false
```

The private output was hashed opaquely and not parsed for this result. Only the
aggregate report was inspected. Both files and their temporary root were
removed by the invocation before result documentation began.

## Verification

Twelve result invariants bind the route, consumed status, artifact hashes,
green implementation proof, exact prefix and byte arithmetic, boundary and
mutation totals, resource measurements, output cleanup, zero access, closed
authority, next gate, and claim boundary.

The complete dependency-light suite passes 3,002 tests with 204 expected
optional skips. The complete optional-neuro suite passes 3,073 tests with 35
skips. Both totals are exactly 12 tests above the remotely green implementation
baseline. Ruff, compilation, parsing of all 208 registry JSON documents,
artifact hashes, CLI help, and diff hygiene pass. These checks read the
committed aggregate record; they do not rerun the consumed closeout.

## Access Accounting

```text
retained private path operations / opens / bytes:   0 / 0 / 0
old consumed root operations:                       0
network requests / bytes:                           0 / 0
archive, local-header, or member payload reads:      0
real participant or member selections:              0 / 0
signal sample reads:                                0
event/target/label/quality/onset/channel reads:      0
real derivative rows:                               0
training / inference / prediction / scoring:        0 / 0 / 0 / 0
provider / language-model / hardware operations:    0 / 0 / 0
retry / rerun / claim upgrades:                     0 / 0 / 0
```

Raw-data reads, real-cache reads, model runs, and training runs were zero. The
producer's causal status is not applicable to metadata-only selection.
End-to-end neural decoding latency was not measured.

## Warnings And Unavailable Fields

Warnings:

- all 1,227 inventory rows were generated and contain no human content;
- the participant rank is public and frozen, but no retained private row was
  read;
- generated sizes and CRC declarations do not verify a real archive member;
- no local header, payload, signal, event, target, quality value, model,
  prediction, or score was accessed; and
- end-to-end neural decoding latency was not measured.

Unavailable:

- real selected member identities, offsets, sizes, and integrity;
- the real selected participant count and byte reservation;
- channels, geometry, signal quality, events, targets, and movement onsets;
- neural features, predictions, scores, and latency; and
- language decoding or thought-to-text evidence.

## Disposition

This generated closeout is consumed. Do not rerun it, tune its fixture sizes,
change the seed or cap, or treat its 16-person result as a real cohort.

The next allowed Tier A step is to commit, push, and green this aggregate
result, then prepare one all-false Tier C packet for exactly one no-follow,
size-, mode-, and SHA-256-bound read of the retained 418,755-byte private
Freewill inventory. That later packet may authorize target-free selection and
aggregate output only. It cannot authorize archive requests, local headers,
member payloads, signals, events, targets, derivatives, models, predictions,
scores, MARC2-FW2, providers, hardware, release, or claim upgrades.

## Claim Boundary

Engineering capability added: NeuroDecodeKit demonstrated deterministic,
storage-bounded, privacy-preserving participant-prefix selection on a full-
scale generated inventory and cleaned its outputs exactly.

Scientific claim not established: the closeout used no human neural data,
prediction, or score and establishes no neural effect, decoding accuracy,
language decoding, or thought-to-text result.
