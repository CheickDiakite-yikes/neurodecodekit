# MARC1-SA1A Source-Aware Live Metadata Implementation

Date: 2026-08-13

Lane: `MARC1-SA1A`

Development route: `MARC1SAL-G1`

Status: **Generated/mock wrapper qualified; exact commit and both remote CI
jobs required before one registered metadata response**

Machine implementation:
`registries/marc1_source_aware_live_metadata_implementation.v0.json`

## Same Research Path

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

This module closes one source-identity gap. It does not replace neural
experiments with metadata work and does not convert movement metadata into
language evidence.

## Green Parent Decision

Implementation began only after decision
`ef9ab91b38ad48ef5e832b993d4ca338d889bc04` passed:

- CI run: `31670457497`
- Base Python job: `94353799568`
- Optional Neuro Readers job: `94353799602`
- decision registry SHA-256:
  `25c2e6b9e745ffb126644867e77e78558a8c3929bda12f0728a7ee776e3273c5`

The decision authorizes this generated/mock implementation and, only after
the exact implementation is committed, pushed, and remotely green, one fixed
public metadata response. It does not authorize an archive, payload, signal,
target, model, score, replication, or language-decoding operation.

## Added Surface

The additive dependency-free module is
`src/neurodecodekit/datasets/marc1_source_aware_live_metadata.py`. It imports
only standard-library modules and the green source-aware attestor. It does not
import, call, modify, probe, or expose the consumed live executor.

Its module commands are:

```text
plan      print the immutable zero-network plan
qualify   exercise generated inventories and mocked HTTP
inspect   read one aggregate report without its private peer
execute   enforce exact green proof and consume one fixed metadata check
```

There is no participant archive reader, ZIP decoder, payload path, EEG reader,
target interface, model, trainer, predictor, scorer, credential, retry,
alternate endpoint, or second-page interface.

## Safety Architecture

1. Generated qualification rejects the registered path lexically without
   statting or opening it.
2. The generated path acquires a held no-follow parent capability before proof
   reads or fixture construction.
3. The future live path acquires repository-private output authority before
   proof reads, machine checks, source setup, or network work.
4. Parent identity is bound by device, inode, directory type, held descriptor,
   and no-follow traversal. The output child must be absent.
5. The live machine gate requires one numerical thread, at least 10 GiB free,
   normalized one-minute load no greater than `1.0` per logical CPU, and peak
   RSS below 256 MiB before the consumed marker.
6. The request is exactly one unauthenticated `GET` to the registered Figshare
   record/version/query. Ambient proxies and redirects are disabled.
7. Only terminal `200` JSON is accepted. Content coding must be absent or one
   `identity` token; framing must be one exact `Content-Length`, one exact
   chunked transfer, or clean connection close.
8. The response uses a 2 MiB cap-plus-one read, records observed bytes and raw
   response SHA-256, and performs no decompression or content decoding.
9. The green attestor rejects malformed UTF-8/JSON, duplicate keys, nonfinite
   values, target-like fields, unsafe or duplicated identities, invalid URLs,
   and disagreeing MD5 provenance.
10. `MARC1SA-R1/R2` map to `MARC1SAL-R1` and may retain only the frozen
    target-free cohort. `MARC1SA-R3/R4` map to `MARC1SAL-R2` and block
    selection without coercion.
11. The mode-`0600` private manifest may retain validated source rows and the
    frozen split only when eligible. Unknown extension values are never
    retained.
12. The aggregate report contains only source identity, counts, booleans,
    historical-difference names, hashes, resources, counters, warnings, and
    claim boundaries. It is inspected exactly once.
13. Generated qualification creates exactly three allowlisted files and
    removes them plus its directory. A live result retains its marker,
    private manifest when available, and aggregate report.
14. Every live result or post-marker failure consumes the lane. There is no
    retry, rerun, resume, fallback, expectation change, or payload continuation.

## Generated And Mocked Qualification

All six frozen source-aware families reached their exact routes:

| Generated family | Source route | Wrapper policy |
|---|---|---|
| documented five-field core | `MARC1SA-R2` | cohort eligible |
| complete agreeing MD5 | `MARC1SA-R1` | cohort eligible |
| partial optional MD5 | `MARC1SA-R2` | cohort eligible |
| one historical difference | `MARC1SA-R3` | selection blocked |
| multiple historical differences | `MARC1SA-R3` | selection blocked |
| unknown non-target extension | `MARC1SA-R4` | selection blocked |

Qualification exercised close-delimited, exact-length, and chunked response
forms. Row/key-order replay preserved every semantic hash. Thirty-one named
adversarial cases covered capability order, path races, request drift,
credentials, status/final-URL drift, coding and framing ambiguity, overflow,
malformed JSON, target leakage, missing core fields, checksum disagreement,
public/private leakage, resource caps, malformed green evidence, and second
invocation.

The final fresh-process candidate measured:

| Measure | Observed | Cap |
|---|---:|---:|
| Generated accepted response bytes | 84,422 | 14,680,064 across seven fixture responses |
| Transient combined output | 24,064 | 2,097,152 |
| Reported runtime | 0.009288083 sec | 30 sec |
| External wall time | 0.10 sec | 30 sec |
| Reported peak RSS | 37,552,128 bytes | 268,435,456 |
| External maximum RSS | 37,617,664 bytes | 268,435,456 |
| Generated/mock HTTP calls | 7 | generated only |
| Adversarial cases | 31 | 31 |
| Output files created / removed | 3 / 3 | exact cleanup |
| Real public requests / payload bytes | 0 / 0 | 0 / 0 |

Generated hashes from that measured candidate:

- marker:
  `9d130c565b9e918768a84387c411cb8614c90b054827e658c00664974056c010`
- private manifest:
  `28098678a903a362aa24507dc99ebdfde0ae3b5f8568369077b573e33cedaeb6`
- aggregate report:
  `5542b379a1ab23aa8f05baf6494c6eca6a284c9d0bfc2dce42072052ef75426a`

The report hash includes measured runtime and RSS. The marker and private
identity replay exactly under fixed inputs. These are generated artifacts,
not hashes of a live source response or participant payload.

## Verification And Next Gate

Focused behavior tests cover the source surface, zero-payload plan, exact
request, all accepted framing forms, transport refusals, all source-aware
routes, strict target/JSON handling, deterministic qualification, output
modes, one-shot success, drift-blocked selection, post-marker failure receipt,
machine refusal, public privacy, resource caps, and CLI no-network behavior.

The final local gate passed 30 focused tests, all 765 MARC tests, and all
2,904 dependency-light tests with 204 expected optional skips. Ruff,
compilation, JSON validation, registry replay, CLI help, and diff hygiene also
pass. The complete optional environment executed 2,975 tests with 35 skips;
one historical tiny-encoder rehearsal read the process-global RSS high-water
after earlier memory-heavy tests and failed its 768 MiB self-check. That exact
test passes in a fresh one-thread process, while the 30 wrapper tests peak at
50,495,488 bytes. No historical or production resource gate was changed.

This exact implementation must now be committed, pushed, and pass fresh Base
Python and Optional Neuro Readers jobs. Those Linux jobs, rather than a local
order-sensitive high-water reading, are the final complete-suite eligibility
gate.

Only after that proof may one registered live invocation occur. A successful
R1/R2 result would make a target-free cohort identity available for a new,
separately authorized selective-acquisition packet. R3/R4 or any failure must
block selection and preserve only its aggregate diagnosis.

Engineering capability added: a capability-first source-aware wrapper can
turn one bounded metadata response into a private cohort identity or
failure-localized aggregate diagnosis without opening a neural payload.

Scientific claim not established: generated and mocked metadata work contains
no neural signal, target, prediction, score, language result, or
thought-to-text evidence.
