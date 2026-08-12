# MARC-1 Versioned Pagination Generated Closeout Result

Date: 2026-08-12

Status: **Consumed at `MARC1PG-F07`; output-parent preflight failed; no retry
or rerun is available**

Lane: `MARC1-PG1`

Machine record:
`registries/marc1_versioned_pagination_failure_result.v0.json`

## Executive Verdict

The exact implementation was remotely green before the one registered
generated closeout. The invocation then refused because its requested output
directory had `/tmp` as its immediate parent, and macOS exposes `/tmp` as a
symbolic link to `private/tmp`. The strict writer correctly rejected the
symlink parent at `MARC1PG-F07`.

This was not an empty preflight. The implementation loads the contract, builds
the 1,227-row and 55-row generated inventories, validates all four accepted
request/response cases, checks their selection hashes, and constructs the
generated private manifest in memory before checking the output path. The one
registered closeout was therefore consumed. No corrected invocation is
allowed under this contract.

No output directory or file was created. No public dataset response, private
source, payload, signal, target, model, prediction, or score was accessed.

## Green Proof

Exact implementation `2c98a2ad4b3972de5c2a398b85c0cf8735db89d4`
passed Base Python job `94104455930` and Optional Neuro Readers job
`94104455857` in CI `31593790492` before the invocation.

The implementation itself was built only after contract
`ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb` passed both required jobs in
CI `31591853349`.

## Observed Failure

The registered output argument was:

```text
/tmp/neurodecodekit-marc1pg-registered-closeout-20260812
```

The filesystem identity observed after refusal was:

```text
/tmp -> private/tmp
/private/tmp is a real directory
```

The CLI emitted:

```json
{"reason":"output parent is a symlink","route":"MARC1PG-F07","status":"refused"}
```

Post-invocation verification confirmed that the requested output path did not
exist. Generated output bytes and incremental disk bytes were both zero.

## Execution Boundary

The source order establishes exactly what happened before refusal:

1. the registered contract and green implementation constants were checked;
2. one canonical 154-byte request was constructed;
3. one 1,227-row generated Freewill inventory was built;
4. one exact 55-row generated Wrist inventory was built;
5. all four accepted mocked response cases were parsed and selected;
6. accepted-case selection hashes were checked for equality;
7. one 300-row generated private manifest was constructed in memory;
8. output-path preflight refused the symlink parent;
9. the 41-case refusal matrix, report assembly, file writes, inspection, and
   aggregate `MARC1PG-G1` decision did not run.

This distinction matters. Existing repository precedent treats a path refusal
as outside a closeout only when it occurs before policy or fixture access.
Here generated fixture work had already occurred, so the registered-run count
is one and the retry/rerun count remains zero.

## Resources And Counters

| Measure | Observed |
|---|---:|
| Registered invocations | `1` |
| Corrected invocations | `0` |
| External wall time | `0.17 sec` |
| External peak RSS | `30,064,640 bytes` |
| Generated output bytes | `0` |
| Incremental disk bytes | `0` |
| Network bytes | `0` |
| Real/private input bytes | `0` |
| Dataset-specific requests | `0` |
| Payload/signal/target operations | `0` |
| Training/model/prediction/score operations | `0` |

Internal runtime, the invocation's generated-input byte count, and output
hashes are unavailable because refusal occurred before report measurement and
serialization. End-to-end latency was not measured.

## Closeout Verification

Thirty-nine focused pagination behavior, implementation, and result tests pass,
as do all 528 MARC tests. The complete dependency-light suite passes 2,667
tests with 204 expected skips in 21.601 seconds at 253,607,936-byte external
peak RSS. The optional-neuro suite passes 2,738 tests with 35 expected skips in
59.915 seconds at 800,735,232-byte external peak RSS. Both complete suites add
exactly ten tests and zero skips over the green implementation baseline.

Repository-wide Ruff, compilation, all 188 registry JSON parses, artifact-hash
checks, and `git diff --check` pass. Verification did not invoke `qualify`,
construct another generated fixture, or create an output artifact.

## Disposition

`MARC1-PG1` is consumed and parked. Do not retry with `/private/tmp`, move the
output under another parent, modify the implementation, reinterpret the failed
run as a successful qualification, or advance directly to a live metadata
packet.

A separately named prospective generated recovery may move output-path
preflight ahead of contract loading and fixture construction, bind a real
non-symlink parent, and prove that no generated operation occurs before path
acceptance. It must have its own frozen contract, green implementation, and
registered run. Any later public metadata response remains Tier C.

This is still the same research path: trustworthy cohort selection supports a
cue-resistant neural positive control, which supports held-out language
decoding and the long-term thought-to-text objective. The failed closeout is a
process defect on that path, not a pivot.

Engineering capability added: the strict writer demonstrated that it refuses
a symlink output parent without creating files or touching any real source.

Scientific claim not established: the pagination hypothesis was not tested
against a live response, and no neural signal, target, prediction, score,
language decoding, or thought-to-text result was produced.
