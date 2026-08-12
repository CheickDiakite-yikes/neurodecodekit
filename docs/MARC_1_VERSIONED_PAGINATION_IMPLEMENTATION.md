# MARC-1 Versioned Pagination Generated Implementation

Date: 2026-08-12
Lane: `MARC1-PG1`
Status: **Generated-only implementation qualified; registered generated
closeout not executed**

Machine record:
`registries/marc1_versioned_pagination_implementation.v0.json`

## Green Contract Gate

Contract commit `ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb` passed Base
Python job `94098410925` and Optional Neuro Readers job `94098410868` in CI
`31591853349` before implementation began. The exact contract SHA-256 is
`22f7e3ba36f0c92af600d5a00a90581c44338609de19105cf6be374b5fad7a9b`.

## What Was Implemented

The additive standard-library module
`src/neurodecodekit/datasets/marc1_versioned_pagination.py` implements:

- exact in-memory serialization of the one frozen `GET` request with
  `page=1&page_size=1000`;
- strict mocked terminal-response validation with absent or inert identity
  content encoding and zero decoding or decompression;
- duplicate-key-safe UTF-8 JSON parsing and a recursive target-field firewall;
- exact 55-row, 45-participant, ten-supplementary, declared-byte, URL, MD5, and
  `sub-01` semantic validation;
- row-order-independent canonical source identity;
- target-free 12+12 participant selection and exact split replay using the
  frozen generated selector;
- a 41-mutation router covering all eight preregistered refusal classes;
- AST source inspection for network, DNS/transport, and `execute` surfaces;
- mode-`0600` generated private output and aggregate-only public output;
- bounded `plan`, `qualify`, and `inspect` CLI commands.

The module has no network client, DNS call, live URL argument, local source
argument, private-root name, automatic pagination, second-page loop, retry,
fallback, `execute`, payload, signal, target, model, prediction, or scorer
surface. It adds no dependency and runs under `python -S`.

## Exact Request Identity

The generated serializer emits 154 bytes for:

```text
GET /v2/articles/29666735/versions/3/files?page=1&page_size=1000 HTTP/1.1
Host: api.figshare.com
Accept: application/json
Accept-Encoding: identity
```

Its SHA-256 is
`95b490f61ee3f563b39344ac09414ff83b06b61339426a4260693c5c567b3b45`.
Ten query mutations refuse before response parsing, including an omitted
query, missing parameter, default-sized page, oversized page, duplicate page,
reordered query, and mixed pagination style.

## Generated Qualification

One disposable final-source development qualification returned
`MARC1PG-G1`:

| Measurement | Observed |
|---|---:|
| accepted cases | 4 / 4 |
| refusal mutations | 41 / 41 |
| refusal routes covered | 8 / 8 |
| acceptance gates | 18 / 18 |
| generated input | 1,019,776 bytes |
| aggregate output | 7,681 bytes |
| private output | 175,674 bytes |
| combined/incremental output | 183,355 bytes |
| internal runtime | 0.08925708406604826 seconds |
| reported peak RSS | 40,091,648 bytes |
| external wall time | 0.21 seconds |
| external maximum RSS | 40,108,032 bytes |
| network bytes | 0 |
| real/private input bytes | 0 |

The aggregate report SHA-256 was
`7895ffa73b94ccf1ac7fc979469092c9657b48feab9ba6fbef2b8c784392c369`.
The mode-`0600` private-manifest SHA-256 was
`e835e41a2494268c7795ca72e2e6ef9f01d0494767c9c70b4e76c382c6e609b4`.
The aggregate was inspected once. Both outputs and their temporary parent were
then removed; neither is committed.

The refusal distribution was:

```text
MARC1PG-F00  4
MARC1PG-F01  10
MARC1PG-F02  8
MARC1PG-F03  4
MARC1PG-F04  5
MARC1PG-F05  4
MARC1PG-F06  3
MARC1PG-F07  3
```

Four accepted row-order and content-encoding cases produced one semantic and
selection identity. Generated 10-, 54-, and 56-row inventories all refused.
The accepted 55-row inventory preserved the exact 45/10 role counts,
3,683,416,050 declared bytes, `sub-01` anchor, 12+12 selection, 72 Freewill run
bundles, 288 Freewill core members, 12 Wrist archives, and zero fit/held-out
overlap.

## Access Ledger

The development run performed only generated fixture construction, committed
contract/source verification, and in-memory validation. These counters stayed
zero:

- dataset-specific requests and response bytes;
- private Freewill or consumed-root operations;
- payload requests and bytes;
- signal, event, target, label, quality, or channel reads;
- cache, epoch, feature, model, training, prediction, freeze, or score work;
- provider, language-model, stream, device, hardware, release, or publication
  work;
- retry, rerun, scientific-claim, or other-project operations.

## Next Gate

Commit and push this exact implementation and require both remote CI jobs to
pass. Only that exact green implementation may run one registered generated
closeout. The closeout must use a fresh temporary directory, fixed contract
identity, one thread, no network/private input, one aggregate inspection, and
complete output removal.

No live metadata body, private inventory, payload, signal, target, model, or
score is eligible. A later live attempt still requires a separate all-false
Tier C request and fresh packet-bound decision after the generated result is
committed, pushed, and green.

MARC1-PG1 is not a pivot away from thought-to-text. It repairs one source-
identity gate on the same path to a cue-resistant neural positive control and
then held-out language decoding.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can now deterministically prove
on generated inputs that one explicit version-page request preserves the full
55-row selection identity and refuses partial-page adaptation.

Scientific claim not established: no dataset body, neural signal, target,
prediction, score, language decoding, or thought-to-text result was produced.
