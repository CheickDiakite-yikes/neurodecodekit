# MARC1-HT1 HTTP Identity Semantics Implementation

Date: 2026-08-12

Status: **generated-only implementation complete; development qualification
passed; registered generated closeout not executed; real inputs remain closed**

Registry:
`registries/marc1_http_identity_semantics_implementation.v0.json`

## Same Research Path

MARC1-HT1 is not a pivot away from thought-to-text. It repairs one transport
predicate on the MARC-1 positive-control path so a later, separately authorized
run can test whether the selected EEG cohorts contain a controlled sensor-level
effect without weakening the target firewall, held-out splits, privacy, or
storage limits.

Movement or sensor-task evidence would still not establish language decoding.
Thought-to-text remains a later held-out language experiment requiring neural
input, linguistic targets, no-signal and language-model controls, a frozen
prediction boundary, and a score that beats those controls.

## Green Contract Boundary

Implementation began only after exact contract commit
`1f99d0a8c5609dae992fa0e245f179c2f417038f` passed both required jobs in CI
`31581395690`:

```text
Base Python:             94065047494
Optional Neuro Readers: 94065047277
```

The implementation is bound to contract SHA-256
`a8b86c56b2ea540715dc09a4a34e0de93f969e3e30dd0ea2d055d366d0c5e73d`
and candidate policy SHA-256
`ac1b98eed57af7e545b925f1529ebf38de72b4277ea54a473ae1d6f7fe0cd3a6`.

## Implemented Surface

The additive standard-library module is
`neurodecodekit.datasets.marc1_http_identity_semantics`. It exposes only:

```text
python -m neurodecodekit.datasets.marc1_http_identity_semantics plan
python -m neurodecodekit.datasets.marc1_http_identity_semantics qualify --output-dir PATH
python -m neurodecodekit.datasets.marc1_http_identity_semantics inspect REPORT
```

There is no `execute` command, URL argument, private-input argument, network
opener, DNS resolver, decompressor, decoder, consumed-executor import, signal
reader, target interface, model, scorer, retry, rerun, fallback, or release
surface. The source inspector uses an explicit import allowlist, forbidden-call
set, and exact command inventory. Contract, research, consumed-result, and
frozen-selector files are verified by no-follow SHA-256 reads before fixture
construction.

## Exact Predicate

The generated terminal-response validator implements one semantic change:

```text
Content-Encoding absent             -> accept as uncoded
one identity token, any casing       -> accept as compatibility tolerance
every other present value            -> refuse
```

`Transfer-Encoding` remains forbidden. Status, terminal endpoint, JSON content
type, ASCII `Content-Length`, exact body length, strict UTF-8/JSON, duplicate
keys, the 2 MiB cap, and the recursive target-like-field firewall all remain
strict. Accepted bytes are never decompressed or decoded.

All four registered accepted forms produce one canonical Wrist body hash and
the same generated selection. All 20 mutations refuse under their frozen
routes:

```text
MARC1HT-F01 proof/contract identity:                  0 runtime mutations
MARC1HT-F02 content-encoding semantics:              10
MARC1HT-F03 HTTP envelope/source schema:              8
MARC1HT-F04 resource/output/privacy/replay boundary:  1
MARC1HT-F05 forbidden operation/second invocation:   1
```

`MARC1HT-F01` is exercised by bound-artifact and contract tests rather than by
mutating a registered artifact during qualification.

## Selection, Privacy, And Replay

The harness reuses the unchanged generated MARC1-P1 selector. It constructs
1,227 Freewill-style rows and 55 Wrist-style rows, then reproduces the frozen
12+12 participant ranks, 72 Freewill run bundles, 288 Freewill core members,
12 Wrist archives, 300 private rows, and zero fit/held-out overlap. Selection
never uses target, response, event count, quality, size, CRC, or outcome data.

Reversing both row orders leaves the cohort, split, byte, and selection
identities unchanged. Two qualifications with fixed runtime and RSS inputs emit
byte-identical aggregate reports and mode-`0600` private manifests. Aggregate
inspection uses no-follow reads, strict JSON, exact top-level and nested
invariants, output-byte reconciliation, and a recursive private-field firewall.
The public report is mode `0644`; its containing directory is mode `0700`.

## Development Qualification

One disposable development qualification passed constructed route
`MARC1HT-G1`:

```text
generated input bytes:                  923,052 / 2 MiB
aggregate report bytes:                   7,064 / 1 MiB
private manifest bytes:                 175,618
combined/incremental bytes:             182,682 / 2 MiB / 4 MiB
accepted forms / refusals / gates:        4 / 20 / 16
selected participants:                    12 + 12
Freewill bundles / members:               72 / 288
Wrist archives / private rows:            12 / 300
internal runtime seconds:     0.10857224999926984 / 30
reported peak RSS bytes:               32,440,320 / 256 MiB
external wall seconds:                         0.22
external maximum RSS bytes:             32,669,696
network and real/private input bytes:             0
```

Aggregate report SHA-256:
`adbe2ffd269edbaaaf82113924df361de0e62f45e9fb4a481ecbae7bb0e39beb`.

Private manifest SHA-256:
`e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831`.

The aggregate was inspected exactly once. Both generated files and their
invocation-created temporary directory were removed. Nothing generated by the
qualification is committed.

## Verification

Eighteen focused implementation tests and all 378 MARC tests pass. They cover
the four accepted encodings, all 20 refusals, exact bound-artifact hashes,
strict headers and JSON, target leakage, private redirects, source-surface
mutation, thread limits, output modes and byte arithmetic, one-shot output,
tampered-report refusal, row-order replay, and byte-identical fixed-measurement
replay.

The complete dependency-light suite passes 2,528 tests with 204 expected skips
in 20.780 seconds at 288,702,464-byte external maximum RSS. The optional-neuro
suite passes 2,599 tests with 35 expected skips in 58.044 seconds at
771,457,024-byte external maximum RSS. Both add exactly 29 tests and zero skips
over the green contract baseline.

Ruff, compilation, parsing of all 179 registry JSON documents, CLI help and
plan, the bounded roundtrip, and `git diff --check` pass.

Every private/live metadata, network, payload, signal, event, target, model,
training, prediction, score, provider, hardware, retry, release, and claim
counter remains zero.

## Next Gate

1. Commit and push this exact implementation and require both CI jobs green.
2. Run one fresh registered generated closeout and remove its outputs.
3. Record, test, commit, push, and green the consumed generated result.
4. Only then prepare one all-false Tier C request for a new additive live
   wrapper and one new metadata attempt.

No current or earlier continuation authorizes step 4. The consumed MARC1-P1A
root remains forbidden, and payload acquisition remains ineligible.

Engineering capability added: NeuroDecodeKit can deterministically validate
the standards-aligned uncoded HTTP response predicate while preserving the
frozen target-free pilot selection and every safety boundary.

Scientific claim not established: no live metadata, EEG payload, neural
signal, target, prediction, score, language decoding, or thought-to-text result
was produced.
