# MARC-1 Versioned Pagination Recovery Preregistration

Date: 2026-08-12
Lane: `MARC1-PG1`
Status: **Frozen generated-only contract; real inputs and execution remain
unauthorized**

Machine contract:
`registries/marc1_versioned_pagination_recovery_contract.v0.json`

## Objective

Qualify one explicit, version-scoped Figshare file-list request identity on
generated rows and mocked HTTP responses before any new dataset-specific body
is eligible.

The prospective request is exactly:

```text
GET https://api.figshare.com/v2/articles/29666735/versions/3/files?page=1&page_size=1000
Accept: application/json
Accept-Encoding: identity
body: none
credentials/cookies: none
```

The implementation must treat the method, scheme, host, path, query order,
query names, and values as one identity. It may not discover pagination after
seeing a response. A second page, `limit`/`offset`, article-details fallback,
current-version endpoint, alternate record, and partial cohort all refuse.

This is a same-path metadata repair between the cue-resistance control design
and any future neural payload. It is not a scientific pivot or result.

## Frozen Proof Anchors

This contract binds green research commit
`7a7883abda094eb9f202215b8b138a17cdff022e`, CI `31591022429`, Base Python
job `94095736694`, and Optional Neuro Readers job `94095736770`.

It also binds:

- research document SHA-256
  `55263a2ad42237167a1aa0504325e5763240e6029a52233ad2c1872d57ee957c`;
- research registry SHA-256
  `fb5482ab441cda1e80bc37540bfa6175e8e6ede09ab26b7a39fafe24f72706e5`;
- generated selector source SHA-256
  `072b9877bff0496ed10b10e4dbccc6751f357ec072390ce406342cc038359374`;
- generated HTTP-semantics source SHA-256
  `6ef6369244f1620af610d2bc3ff5ee4aaa5b16aba2facce428c7bc8f1690abff`;
- consumed aggregate result SHA-256
  `50a1bd4e97e6149db91d528aa0fce79e6aa5d3cedf79acdb12f03bf4a2d041f2`;
- canonical pagination-policy SHA-256
  `c4e80a99e782ac61d5e5b32e371c9cbb40580254376f518e9820a507402b1624`.

The actual consumed row count and rows remain unavailable. The contract does
not infer that the response held 10 rows.

## Generated-Only Surface

Only after this exact contract is committed, pushed, and both CI jobs are
green may an additive module be implemented at:

`src/neurodecodekit/datasets/marc1_versioned_pagination.py`

It may expose only:

- `plan`: print the exact zero-access contract summary;
- `qualify`: run generated request, response, semantic, selector, privacy, and
  resource checks;
- `inspect`: validate one aggregate generated report.

It may compose the frozen generated selector and generated HTTP-semantics
modules. It must not import a network opener, resolve DNS, accept a URL or local
source path, mention either consumed private root, expose `execute`, create a
persistent payload surface, or add a dependency.

## Exact Generated Inputs

One future generated closeout may construct only:

- one 1,227-row Freewill-style inventory;
- one exact 55-row Wrist-style version inventory;
- the exact `sub-01.zip` through `sub-45.zip` participant identity;
- ten exact supplementary rows;
- 72 Freewill run bundles, 288 Freewill core members, and 12 Wrist archives;
- one 300-row generated private selection manifest;
- four accepted mocked request/response cases;
- forty-one rejected mutations.

No generated row may be selected using size, checksum, event count, signal
quality, target, label, response, sentence, outcome, or any model result.

## Accepted Replay Matrix

Exactly four cases must pass:

1. canonical rows with absent `Content-Encoding`;
2. reversed rows with absent `Content-Encoding`;
3. canonical rows with `Content-Encoding: identity`;
4. reversed rows with mixed-case `Content-Encoding: IdEnTiTy`.

Every case must use the exact canonical query and produce identical canonical
Wrist metadata, participant, split, private-selection, and public-selection
hashes. Reversing response row order cannot change identity or selection.

## Refusal Matrix

The implementation must exercise and refuse all 41 named mutations:

1. wrong green research commit;
2. wrong research-document hash;
3. wrong research-registry hash;
4. wrong pagination-policy hash;
5. missing query;
6. missing `page`;
7. missing `page_size`;
8. `page=0`;
9. non-integer `page`;
10. `page_size=10` default-page request;
11. `page_size=1001`;
12. reversed query order;
13. duplicate `page`;
14. mixed `limit`/`offset` pagination;
15. non-200 status;
16. redirect evidence;
17. `gzip` content coding;
18. transfer coding;
19. non-JSON content type;
20. malformed content length;
21. content-length/body mismatch;
22. response body overflow;
23. malformed JSON;
24. duplicate JSON key;
25. non-array JSON root;
26. non-object row;
27. target-like extra field;
28. ten-row partial page;
29. 54-row inventory;
30. 56-row inventory;
31. duplicate row identity;
32. participant or supplementary identity mutation;
33. wrong downloader URL;
34. supplied/computed MD5 disagreement;
35. `sub-01` anchor mismatch;
36. declared-byte total mismatch;
37. private value in public output;
38. forbidden source surface;
39. output-cap breach;
40. nondeterministic replay;
41. second generated-closeout invocation.

The eight ordered failure routes remain:

```text
MARC1PG-F00  proof, source-commit, contract, or request identity mismatch
MARC1PG-F01  malformed query, mixed pagination styles, or hidden override
MARC1PG-F02  generated HTTP envelope, encoding, redirect, or body-cap failure
MARC1PG-F03  JSON root, duplicate key, field, or type failure
MARC1PG-F04  exact 55-row, participant-name, or supplementary-count failure
MARC1PG-F05  URL, MD5, sub-01 anchor, declared-byte, or selected-byte failure
MARC1PG-F06  target leakage, private-output leak, old-root, or payload boundary
MARC1PG-F07  runtime, RSS, thread, output, overwrite, retry, or replay failure
```

## Unchanged Semantic Identity

The generated parser and selector must require:

```text
record/version/DOI:              29666735 / 3 / 10.6084/m9.figshare.29666735.v3
file rows:                       55 exact
participant archives:           45 exact
supplementary rows:              10 exact
participant names:              sub-01.zip through sub-45.zip exactly once
declared record bytes:           3,683,416,050 exact
sub-01 file ID:                  62,570,743 exact
sub-01 bytes:                    33,690,749 exact
sub-01 MD5:                      6b01cf5bd30de0c670d2837d112a17fa exact
target-like extra fields:        refused
partial page or cohort:          refused
```

Transport-body SHA-256, `Content-Length`, response order, and timestamp are
provenance, not semantic identity. The canonical semantic hash must be row-
order independent.

## Source And Privacy Audit

Source inspection must prove the absence of:

- `urllib.request`, `http.client`, `socket`, `requests`, `aiohttp`, or another
  network client;
- DNS, redirect traversal, automatic pagination, retry, fallback, or resume;
- `.codex_work`, consumed executor imports, consumed-root names, a local input
  path, a real endpoint opener, or an `execute` command;
- decompression, payload, signal, event, target, feature, model, prediction,
  scoring, provider, stream, device, hardware, release, or publication logic.

Only a mode-`0600` generated private manifest may contain selected row-level
identities. The public report may contain aggregate counts and SHA-256 values,
never participant IDs, file names, URLs, MD5 values, private paths, rows, or
targets.

## Resource Contract

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
runtime:                                  30 seconds
peak RSS:                                 256 MiB
generated input:                          2 MiB
public output:                            1 MiB
private + public output:                  2 MiB
incremental disk:                         4 MiB
network bytes:                            0
real/private input bytes:                 0
```

The closeout must use a fresh temporary output directory, write exclusively,
measure and hash both outputs, inspect the public report once, then remove all
generated outputs. Nothing generated may be committed.

## Acceptance Gates

Constructed route `MARC1PG-G1` requires all 18 gates:

1. exact green research proof;
2. exact contract and frozen-source hashes;
3. exact canonical pagination-policy hash;
4. exact byte-for-byte request serialization;
5. all four accepted cases pass;
6. all accepted cases have identical semantic and selection hashes;
7. all 41 mutations refuse under the registered routes;
8. the generated ten-row default page refuses;
9. exactly 55 rows pass and 54/56 rows refuse;
10. exact participant, supplementary, total-byte, and `sub-01` identity;
11. exact 12+12 participant selection;
12. exact 72-bundle/288-member/12-archive split binding and zero overlap;
13. selection remains target-, quality-, size-, checksum-, and outcome-free;
14. private/public output separation passes;
15. source audit finds no real, network, consumed-root, payload, or model
    surface;
16. every real, private, neural, target, model, score, and claim counter is
    zero;
17. thread, runtime, RSS, input, output, and disk caps pass;
18. aggregate and private output hashes replay deterministically.

`MARC1PG-G1` is generated engineering evidence only. It cannot establish that
the live endpoint will return 55 rows, that any payload is available, or that
EEG contains a recoverable neural effect.

## Evidence Order

1. Commit and push this exact contract.
2. Require Base Python and Optional Neuro Readers green.
3. Implement only the additive generated/mock surface.
4. Commit and push the exact implementation; require both jobs green.
5. Run one measured generated closeout.
6. Commit and push its aggregate result; require both jobs green.
7. Only then prepare an all-false Tier C packet for a new additive wrapper and
   one new metadata-only response.

No current or previous authorization opens step 7. Payload acquisition remains
ineligible.

## Verification

Eleven focused contract tests and all 489 MARC tests pass. The complete
dependency-light suite passes 2,628 tests with 204 expected skips in 20.743
seconds at 250,806,272-byte external peak RSS. The optional-neuro suite passes
2,699 tests with 35 expected skips in 59.124 seconds at 809,107,456-byte
external peak RSS. Both complete suites add exactly 11 tests and zero skips
over the green research baseline.

Ruff, compileall, strict registry JSON parsing, CLI help, bound-hash replay,
canonical policy-hash replay, and `git diff --check` also pass.

## Claim Boundary

Engineering capability proposed: a deterministic generated harness can prove
that an explicit one-page version request preserves the full frozen 55-row
identity and refuses partial-page adaptation.

Scientific claim not established: this contract authorizes no dataset body,
neural signal, target, prediction, score, language decoding, or thought-to-text
claim.
