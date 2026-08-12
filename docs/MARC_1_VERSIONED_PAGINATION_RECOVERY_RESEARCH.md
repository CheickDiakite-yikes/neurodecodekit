# MARC-1 Versioned Pagination Recovery Research

Date: 2026-08-12
Lane: `MARC1-PG1`
Status: **Tier A architecture research complete; no dataset-specific response,
private path, payload, signal, target, model, or score was accessed**

Registry:
`registries/marc1_versioned_pagination_recovery_research.v0.json`

## Question

Why did the standards-aligned MARC1-HT1A request accept and parse a live Wrist
metadata body but fail the frozen 55-row rule, and what is the smallest
prospective repair that does not inspect, rerun, or amend the consumed lane?

The leading engineering hypothesis is omitted pagination. The consumed wrapper
requested the official version-files endpoint without `page` or `page_size`,
while the current official Figshare OpenAPI specifies a default page size of
10 and a maximum of 1,000. The next design should therefore make pagination an
explicit part of source identity rather than assuming one unparameterized
response contains the complete version inventory.

This hypothesis is not yet proven. The consumed body and its actual row count
were not retained, and this research does not request them again.

## Observed Boundary

MARC1-HT1A is consumed at `MARC1HTL-F04`. Its one live response passed status,
URL, content type, absent-encoding, exact `Content-Length`, 2 MiB body cap,
SHA-256, and strict JSON parsing. It accepted 2,917 bytes and then refused
because the parsed root did not contain exactly 55 rows.

The result retained no row count, row, filename, file ID, checksum, URL, or
changed field. It selected zero participants and opened zero payload bytes.
Every signal, target, derivative, model, prediction, score, retry, rerun, and
claim counter remained zero.

This research uses only that committed aggregate result, the committed wrapper
source, and public Figshare documentation and OpenAPI source. It does not open
the consumed private root or sealed upstream manifest.

## Primary-Source Findings

The official Figshare
[article API documentation](https://docs.figshare.com/old_docs/api/articles/)
defines both a version-specific article endpoint and a version-specific files
endpoint. A public version is addressed by article ID and version number.

At pinned official documentation commit
[`751101d`](https://github.com/digital-science/figshare-user-documentation/tree/751101d87c8fcea45556492bc627499ff49b0f2b),
the OpenAPI source specifies:

1. `GET /articles/{article_id}/versions/{version_id}/files` is the official
   `article_version_files` operation.
2. Its `page` parameter has range 1 through 5,000.
3. Its `page_size` parameter has range 1 through 1,000 and default 10.
4. `limit` and `offset` are a separate alternative pagination pair.
5. The response is an array of `PublicFile` objects.
6. `GET /articles/{article_id}/versions/{version_id}` returns an
   `ArticleComplete`, but that object's embedded `files` field is explicitly
   limited to at most 10 entries. It therefore cannot establish a complete
   55-file inventory.

Figshare's [versioning guidance](https://info.figshare.com/user-guide/us-funder-user-guide/)
says file changes create a new versioned DOI, the base DOI resolves to the
newest version, and previous versions remain available. The existing Wrist
identity already binds record `29666735`, version `3`, and DOI
`10.6084/m9.figshare.29666735.v3`; the missing control was explicit list
pagination, not a need to switch to the newest version.

The inspected OpenAPI bodies were 72,752 and 123,417 bytes. No dataset-specific
Figshare endpoint, download URL, file body, or private artifact was requested
while establishing these findings.

## Failure Hypotheses

The ordered hypotheses are deliberately separated from conclusions:

### H1 - Omitted pagination

The unparameterized request may have returned only the API's default first
page. This is the leading hypothesis because the official default is 10 and the
consumed wrapper supplied neither supported pagination pair.

Support: source documentation plus the exact committed request URL.

Not proven: the live row count was not retained, so it cannot be claimed to
have been 10.

### H2 - Version inventory drift

The version-scoped inventory may no longer contain the historical 55 rows.
This remains possible until one explicitly paginated response is semantically
validated. A changed inventory must park; it must not trigger a version
substitution, partial cohort, or updated expected count.

### H3 - Provider behavior differs from current OpenAPI

The deployed endpoint may cap, ignore, or reject documented pagination. A
future request must fail closed if `page_size=1000` does not yield the exact
registered 55-row semantic identity. No second page, alternate pagination
style, or fallback endpoint may be tried after observing the result.

## Prospective Request Identity

The candidate request is exactly:

```text
method: GET
scheme/host: https://api.figshare.com
path: /v2/articles/29666735/versions/3/files
query: page=1&page_size=1000
Accept: application/json
Accept-Encoding: identity
request body: none
credentials/cookies: none
```

The query order, names, and values are part of the request identity. `limit`,
`offset`, a second page, an article-details fallback, a current-version
endpoint, and a user-selected URL are forbidden.

A page size of 1,000 is larger than the frozen expected inventory of 55 and is
within the official maximum. If the response contains exactly the same 55
strict rows, the complete expected inventory fits in that one page. If it
contains any other number, the lane parks without learning or publishing the
actual count.

## Semantic Identity

Transport bytes are not enough. A future generated-qualified parser must still
require:

```text
rows:                         55 exact
participant archives:        45 exact
supplementary rows:           10 exact
participant names:           sub-01.zip through sub-45.zip exactly once
declared record bytes:        3,683,416,050 exact
sub-01 file ID:               62,570,743 exact
sub-01 bytes:                 33,690,749 exact
sub-01 MD5:                   6b01cf5bd30de0c670d2837d112a17fa exact
target-like fields:           forbidden
```

Every row must retain the existing seven-field schema, exact downloader URL
construction, supplied/computed MD5 agreement, unique ID and name, safe
basename rules, and target firewall. Canonical row-order-independent hashes
remain the source identity. Raw response SHA-256, `Content-Length`, timestamp,
and response order are transport provenance only.

Only after all 55 rows pass may the frozen target-free 12-participant Wrist
selection run. Freewill remains a separate sealed input and must not be opened
by generated pagination qualification or by this research.

## Generated Qualification Before Live Access

The smallest next evidence sequence is:

1. Freeze a generated-only `MARC1-PG1` contract after this research commit is
   pushed and both CI jobs are green.
2. Implement a standard-library `plan`/`qualify`/`inspect` harness with no URL
   opener, private path, payload interface, or `execute` command.
3. Prove exact request canonicalization, default-page refusal, explicit
   1,000-row capacity, row-order replay, target firewall, output privacy,
   resource caps, and malformed-pagination refusals on generated fixtures.
4. Commit, push, and require both CI jobs green.
5. Run one registered generated closeout and green its aggregate result.
6. Only then prepare an all-false Tier C packet for a new additive wrapper and
   one new metadata attempt. The packet opens nothing by itself.

No future live wrapper may import, call, modify, or reuse either consumed live
executor or inspect either consumed private root. A new root and consumed
marker are mandatory. Any future attempt remains one-shot with no retry.

## Prospective Router

```text
MARC1PG-F00  proof, source-commit, contract, or request identity mismatch
MARC1PG-F01  malformed query, mixed pagination styles, or hidden override
MARC1PG-F02  generated HTTP envelope, encoding, redirect, or body-cap failure
MARC1PG-F03  JSON root, duplicate key, field, or type failure
MARC1PG-F04  exact 55-row, participant-name, or supplementary-count failure
MARC1PG-F05  URL, MD5, sub-01 anchor, declared-byte, or selected-byte failure
MARC1PG-F06  target leakage, private-output leak, old-root, or payload boundary
MARC1PG-F07  runtime, RSS, thread, output, overwrite, retry, or replay failure
MARC1PG-G1   generated pagination semantics and exact selector replay pass
```

No success route in this research is scientific. Even a later live metadata
success would establish only a valid target-free pilot selection.

## Resource And Authorization Boundary

Generated work is capped at one CPU thread, one worker, one numerical job, 30
seconds, 256 MiB peak RSS, 2 MiB generated input, and 2 MiB output. A possible
future live metadata request would retain the existing 2 MiB network-body, 4
MiB incremental-disk, 12 GiB free-disk, and normalized-load gates.

This Tier A record authorizes no generated implementation before a green
contract, no dataset-specific request, no private-manifest operation, no
consumed-root operation, no payload acquisition, no signal or target read, no
model or score, no retry or rerun, and no claim upgrade.

## Same Research Path

This is not a pivot. MARC1-PG1 repairs the exact metadata gate blocking the
same sequence:

```text
version-scoped pilot identity
-> bounded cue-resistant positive-control payload
-> target-firewalled neural/control comparison
-> held-out language decoding
-> long-term non-invasive thought-to-text objective
```

Engineering capability added: the next MARC-1 gate now has an official-source-
bound, explicit-pagination identity design that can distinguish a partial API
page from a true version-inventory mismatch without weakening any selector or
payload control.

Scientific claim not established: no dataset-specific body, neural payload,
signal, target, model, prediction, or score was accessed, so this research
establishes no neural effect, language decoding, or thought-to-text result.
