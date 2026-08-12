# MARC1-HT1 HTTP Identity Semantics Result

Date: 2026-08-12

Status: **registered generated closeout passed and consumed; no retry or rerun;
real inputs and payloads remain closed**

Registry: `registries/marc1_http_identity_semantics_result.v0.json`

## Same Research Path

MARC1-HT1 is a transport repair on the existing MARC-1 positive-control path,
not a pivot away from thought-to-text. It removes one avoidable metadata gate
before a later, separately authorized EEG positive-control experiment. It does
not replace the later requirement for a held-out language decoder that beats
both no-signal and language-model controls.

## Evidence Order

Exact implementation commit
`b2cb48cc1c630cf2d22186732e8258619db0a930` passed both required jobs in
CI `31583931303` before the registered closeout:

```text
Base Python:             94073234688
Optional Neuro Readers: 94073234607
```

The closeout used that exact committed module and contract. No implementation,
threshold, response rule, cohort rank, split, resource cap, or output schema
changed after green proof and before execution.

## Registered Execution

Exactly one `python -S` qualification ran with one CPU thread, one worker, one
numerical job, zero network access, and a new temporary output directory. It
constructed only the registered 1,227-row Freewill fixture, 55-row Wrist
fixture, and mocked HTTP responses.

The aggregate report was inspected exactly once through the module CLI. The
aggregate and private outputs were then size- and SHA-256-measured and the
invocation-created directory was removed. The closeout is consumed with no
retry or rerun.

## Result

Constructed route `MARC1HT-G1` passed every registered gate:

```text
accepted response forms:                  4 / 4
refusal mutations:                       20 / 20
acceptance gates:                        16 / 16
selected participants:                    12 + 12
Freewill bundles / core members:          72 / 288
Wrist archives / private rows:            12 / 300
fit / held-out overlap:                           0
generated input bytes:                  923,052 / 2 MiB
aggregate report bytes:                   7,063 / 1 MiB
private manifest bytes:                 175,618
combined/incremental output bytes:      182,681 / 2 MiB / 4 MiB
internal runtime seconds:     0.1119600001256913 / 30
reported peak RSS bytes:               33,079,296 / 256 MiB
external wall seconds:                         0.24
external maximum RSS bytes:             33,095,680
network and real/private input bytes:             0
```

Aggregate report SHA-256:
`865e69d4b263dd311c48ad301e29dadc2050962f871bf87405193aa77c394299`.

Private manifest SHA-256:
`e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831`.

The private hash exactly replays the frozen MARC1-P1 generated selection. The
aggregate size differs by one byte from the development qualification only
because runtime and RSS measurements are part of the report; fixed-measurement
tests prove byte-identical deterministic replay.

## What Passed

The closeout proves that the standards-aligned response predicate composes with
the unchanged target-free selector. Absent `Content-Encoding` and one lone
identity token in any registered casing produce the same canonical body and
selection identities. Every actual coding, list, duplicate, empty field,
transfer coding, malformed envelope, target-like field, output breach, and
second invocation refuses under the frozen route classes.

It also proves exact cohort and split replay, strict output privacy, no-follow
inspection, mode-`0600` private output, output-byte reconciliation, one-thread
resource enforcement, and zero decompression or decoding.

## What Did Not Happen

The run made zero private Freewill reads, public Wrist requests, DNS queries,
network-body reads, participant selections from a live source, payload
requests, EEG reads, event or target reads, cache or feature operations, model
runs, training runs, prediction sets, scores, provider calls, hardware
operations, retries, releases, or claim upgrades.

The consumed MARC1-P1A header remains unavailable and was not inferred. This
result does not prove that a new live response will pass, that either payload
cohort remains available, that its recordings are usable, or that a neural
effect exists.

## Verification

Eleven result invariants plus the 29 implementation invariants pass, along with
all 400 MARC tests. The complete dependency-light suite passes 2,539 tests with
204 expected skips in 21.592 seconds at 278,380,544-byte external maximum RSS.
The optional-neuro suite passes 2,610 tests with 35 expected skips in 57.182
seconds at 773,505,024-byte external maximum RSS. Both complete suites add
exactly 11 result tests and zero skips over the green implementation baseline.

Ruff, compilation, parsing of all 180 registry JSON documents, CLI inspection,
and `git diff --check` pass.

## Next Gate

1. Test, commit, push, and green this consumed aggregate result.
2. Only after that green proof, prepare one all-false Tier C request for a new
   additive live wrapper and one new metadata attempt.
3. Require that request and a fresh packet-bound maintainer decision to become
   separately green before any private read or public request.

Payload acquisition remains ineligible. The old private root remains forbidden,
and no live wrapper may be implemented from this result alone.

Engineering capability added: the registered generated closeout proves that
the repaired uncoded-response predicate, frozen target-free selector, strict
privacy boundary, and resource caps replay together end to end.

Scientific claim not established: no live metadata, EEG payload, neural
signal, target, prediction, score, language decoding, or thought-to-text result
was produced.
