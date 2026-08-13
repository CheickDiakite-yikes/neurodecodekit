# MARC1-SA1A Source-Aware Live-Metadata Result

Date: 2026-08-13

Status: **Consumed at `MARC1SAL-R2`; cohort selection is blocked**

Machine result:
`registries/marc1_source_aware_live_metadata_result.v0.json`

Result registry SHA-256:
`c5412aa6018006f0bc8c05642ce8f04dce4c0379599f3426cf694f3da34a1662`

## Result In One Line

The proof-gated wrapper consumed one bounded Figshare metadata response,
completed its source-aware attestation, and routed to the frozen branch that
blocks cohort selection before every participant archive or neural payload.

This is a real metadata-compatibility result. It is not neural, decoding,
language, or thought-to-text evidence.

## Proof Order

Request `b0775501e8d7dc5b28b81692dbc7fb02d423be95` and authorization
decision `ef9ab91b38ad48ef5e832b993d4ca338d889bc04` were already green.

Exact implementation `74aff21bde6495436066c1538e229eb7be5059cc`
then passed Base Python job `94360721568` and Optional Neuro Readers job
`94360722170` in CI `31672761644`. Its implementation-registry SHA-256 was
`b909800fa0c3c3a004e2a08b311b33c4447dea1a389df94ee202f14dc4fe76d5`.

The tracked worktree was clean and HEAD matched that exact pushed commit
before execution. Free disk exceeded 10 GiB, normalized load was below `1.0`
per logical CPU, and all five numerical thread variables were `1`.

## What Happened

The executor acquired its private output capability, replayed the green proof,
passed the machine gate, wrote its mode-`0600` consumed marker, and made its
one fixed request for Figshare record `29666735`, version `3`, with query
`page=1&page_size=1000`.

The response passed bounded transport and strict source-aware attestation. The
wrapper returned `MARC1SAL-R2`, which is the preregistered blocked-selection
route for source routes R3 or R4.

```text
request attempts / redirects:         1 / 0
accepted metadata bodies:             1
wrapper route:                        MARC1SAL-R2
selected subjects:                    0
participant archive requests:         0
payload bytes:                        0
```

## What Is Unavailable

The executor inspected the aggregate report exactly once before returning.
The CLI summary exposed the wrapper route and bounded measurements, but not the
private source route, response-body byte count, predicate vector, or historical
differences. The report and private manifest were not reopened afterward.

Therefore the result does **not** claim whether the underlying source route
was R3 historical drift or R4 unknown extension. It does not infer a changed
row count, filename, ID, URL, checksum, byte total, or schema field. Those
values remain unavailable under this consumed one-inspection contract.

That is stricter than guessing, and it is enough for the registered decision:
the frozen Wrist cohort is not eligible for acquisition.

## Resource And Access Result

```text
runtime:                               0.6966645420015993 sec
peak RSS:                              33,439,744 bytes
combined output / incremental disk:    23,112 / 23,112 bytes
CPU threads / workers / jobs:          1 / 1 / 1
public metadata requests:              1
raw EEG reads / real-cache reads:      0 / 0
participant archive / payload bytes:   0 / 0
training / model / predictions:        0 / 0 / 0
target reads / scoring events:         0 / 0
provider-model / hardware calls:       0 / 0
operations on other projects:          0
retries / reruns:                      0 / 0
```

The retained output totals 23,112 bytes, far below the 2 MiB combined-output
and 4 MiB incremental-disk caps. Its hashes were exposed directly by the CLI:

- consumed marker:
  `4187b5ec8bc58c6636d74ef31c93a60f84d8f6d249e13333af6717269894096e`
- private manifest:
  `3458baea7eb97dbb3b212f29caac3f7949ab5b709c5d1294bdaf21050c49e4d0`
- aggregate report:
  `ae658003d3946481ee7901dfb83bc327232db6a9251b544adccc17a3b152c9e6`

The private root remains Git-ignored. It was not committed, deleted, renamed,
overwritten, or inspected after execution.

## Disposition

`MARC1-SA1A` is consumed. Do not retry, rerun, resume, amend the source
expectations, reopen either retained content file, or request a participant
archive under this lane.

The route-conditioned acquisition step is blocked, so the remaining steps do
not proceed against this Wrist cohort. The next safe work is Tier A comparison
of independent cue-resistant datasets and prospective designs. Any different
source request, payload acquisition, neural experiment, target delivery, or
score remains a separately frozen gate.

The research path remains:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

There is no pivot and no manufactured positive result.

## Claim Boundary

Engineering capability added: the proof-gated wrapper consumed one bounded
live metadata response, completed source-aware attestation, and correctly
blocked an ineligible cohort before every payload operation.

Scientific claim not established: no neural payload, target, model,
prediction, score, language decoding, or thought-to-text capability was
accessed or established.
