# MARC-1 Paginated Live-Metadata Result

Date: 2026-08-12

Status: **Consumed at `MARC1LM-F04`; no retry or rerun is available**

Machine result:
`registries/marc1_paginated_live_metadata_failure_result.v0.json`

Result registry SHA-256:
`6e3e488976eb78228f4ffe66d1ac7fc8332ca42a0512d165cbb517be140a2086`

## Result In One Line

The registered wrapper accepted and parsed one bounded 15,652-byte Figshare
metadata body, then failed closed when the live rows did not satisfy the
frozen inventory validator. It selected no cohort and opened no participant
archive.

This is an aggregate metadata-compatibility result. It is not neural,
decoding, language, or thought-to-text evidence.

## Proof Order

The request packet was already green at commit `4d3eb19`. The packet-bound
authorization decision was already green at commit
`060a365a24e75da4297a5c4a3422ff730467ec36`.

The exact corrected implementation
`f9a1eceb8ee432e57e19c6af2db355aadd53b1e3` then passed Base Python job
`94164152160` and Optional Neuro Readers job `94164152302` in CI
`31611639130` before the sole invocation. Its implementation-registry SHA-256
was `1943fbfdb90a2b8ae455db277e39434f38e0aa6bbc279c443c47355213a498a2`.

The tracked worktree was clean and local HEAD matched its pushed upstream. The
unrelated untracked tracker-inspection sidecar was not staged, changed, or
deleted.

## What Happened

The pre-consumption machine gate passed:

```text
free disk:                         24,907,935,744 bytes
logical CPUs:                     12
one-minute load:                  5.06396484375
load per logical CPU:             0.4219970703125
pre-consumption peak RSS:         29,818,880 bytes
CPU threads / workers / jobs:     1 / 1 / 1
```

The executor then wrote its mode-`0600` consumed marker and made exactly one
request for Figshare record `29666735`, version `3`, using
`page=1&page_size=1000`. The response passed the bounded transport and strict
JSON-list checks. One metadata parse reached the frozen inventory validator,
which refused at `MARC1LM-F04`.

```text
request attempts / redirects:     1 / 0
accepted body reads / bytes:      1 / 15,652
metadata parses:                  1
decompression operations:         0
selected subjects:                0
participant archive requests:     0
payload bytes:                    0
```

The marker SHA-256 exposed by the aggregate receipt is
`761622c444334a2934c8c841ba6028a058e93eaa0c9c4db65a009dc774b9489b`.
No inventory, selection, response-body, or private-manifest identity became
available.

## What The Failure Means

The live body differed from at least one predicate in the frozen 55-row,
45-participant-archive, ten-supplementary-row inventory contract. The safe
reason is exactly `frozen inventory validation refused`.

The aggregate result does **not** identify the failed predicate. The actual row
count, names, file IDs, URLs, checksums, byte totals, raw rows, and response body
were not published. Therefore this closeout does not call the failure a row-count
change, checksum drift, filename drift, or API-schema change.

This distinction matters: the run proved that the one-shot system failed
closed, but it did not establish a new immutable metadata identity that could
authorize payload acquisition.

## Resource And Access Result

```text
runtime:                           1.0945040830411017 sec
peak RSS:                          33,996,800 bytes
network body:                      15,652 bytes
public output:                     3,948 bytes
combined output / disk:            4,207 / 4,207 bytes
raw EEG reads / real-cache reads:  0 / 0
training / model / predictions:    0 / 0 / 0
target reads / scoring events:     0 / 0
provider-model / hardware calls:   0 / 0
operations on other projects:      0
retries / reruns:                  0 / 0
```

Only the aggregate public report was inspected, exactly once. The private
manifest was not opened after execution, no raw response or row was
published, and the isolated consumed root was neither committed nor deleted.
End-to-end decoding latency was not measured; causality is not applicable to
this metadata-only operation.

## Disposition

`MARC1-LM1` is consumed. Do not retry, rerun, resume, amend its parser, reopen
the private manifest, probe the registered root, or request a participant ZIP
under this lane.

The next work remains on the same research path. It must be a separately named
prospective current-inventory identity lane that learns only enough aggregate
structure to bind a stable metadata snapshot, then freezes the cohort before
any payload. Any new public response or payload remains a new Tier C event.

The sequence remains:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

There is no pivot.

## Claim Boundary

Engineering capability added: the one-shot wrapper accepted and parsed one
bounded live metadata body, then failed closed at the frozen inventory
validator with an aggregate consumed receipt.

Scientific claim not established: this metadata failure establishes no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
