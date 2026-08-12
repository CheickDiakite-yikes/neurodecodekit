# MARC1-LM1 Paginated Live-Metadata Implementation

Date: 2026-08-12
Lane: `MARC1-LM1`
Development route: `MARC1LM-G1`
Status: generated/mock implementation qualified; exact commit and both remote
CI jobs required before one registered metadata request

## Why This Is On The Same Path

NeuroDecodeKit still follows one research path:

```text
trustworthy multimodal cohort
  -> cue-resistant neural positive control
  -> held-out language decoding
  -> progressively stronger thought-to-text evidence
```

This implementation closes a cohort-integrity gap. It can bind the complete,
versioned Wrist metadata inventory and frozen target-free participant/split
selection before a later payload experiment. It is not a pivot, and metadata
does not count as neural or language evidence.

## Green Parent Decision

Implementation began only after packet-bound decision
`060a365a24e75da4297a5c4a3422ff730467ec36` passed:

- CI run: `31604608307`
- Base Python job: `94140250333`
- Optional Neuro Readers job: `94140250412`
- decision registry SHA-256:
  `f66a79adb60656de8a09ef40b56ae5389ac1fbb664a515fe424333c6fecdf366`

The decision authorizes one generated/mock implementation and, only after that
exact implementation is committed, pushed, and remotely green, one registered
public metadata response. It does not authorize participant ZIP requests,
payload bytes, neural data, targets, models, scores, or a claim upgrade.

## Added Surface

The additive dependency-free module is
`src/neurodecodekit/datasets/marc1_paginated_live_metadata.py`. Its four module
commands are:

```text
plan      print the immutable one-response plan without opening a source
qualify   exercise generated inventory, mocked transport, and output lifecycle
inspect   read exactly one aggregate report, never its marker or private peer
execute   enforce green proof and consume the one registered metadata request
```

Heavy dependencies remain absent. The module has no payload reader, archive
decoder, EEG interface, target interface, model, scorer, provider credential,
retry, automatic pagination, fallback endpoint, or claim-upgrade surface.

## Safety And Identity

The implementation:

1. Refuses the registered output path in generated qualification without
   statting or opening it.
2. Acquires a process-local parent-directory capability before repository,
   fixture, parser, or network work.
3. Verifies every output ancestor with no-follow semantics, binds parent
   device/inode/type, revalidates identity, and requires an absent child.
4. Creates only one mode-`0700` directory and three allowlisted files through
   held descriptors with `O_EXCL | O_NOFOLLOW`.
5. Uses mode `0600` for the consumed marker and private manifest and `0644` for
   the aggregate report.
6. Serializes one exact GET identity for
   `page=1&page_size=1000`, rejects request bodies and URL/header drift, and
   disables redirects and ambient proxy routing.
7. Accepts only terminal `200` JSON with the exact final URL, identity or absent
   content coding, and one unambiguous length/chunked/close framing mode.
8. Reads at most 2 MiB plus one overflow byte and performs no content decoding
   or decompression.
9. Rejects duplicate JSON keys, non-finite constants, schema drift, duplicate
   file IDs/names, checksum disagreement, target-like fields, and inventory
   identity drift.
10. Requires exactly 55 rows, 45 participant archives, ten supplementary rows,
    and 3,683,416,050 declared bytes.
11. Applies only the frozen 12-subject Wrist selection and runs 1-6 fit versus
    runs 7-8 held out. Size, checksum, quality, label, target, and outcome do
    not select a subject or split.
12. Keeps all 55 validated source rows in one private manifest while publishing
    only aggregate counts, byte totals, domain-separated hashes, counters,
    warnings, unavailable fields, and claim boundaries.
13. Writes an aggregate failure receipt after the consumed marker whenever a
    later failure can still be reported without overwrite.
14. Refuses retry, rerun, resume, substitution, second-page fetches, or
    post-response expectation changes.

The implementation hash-verifies and defer-imports only pure helpers from the
consumed pagination module. It never calls the consumed qualifier, output
guard, CLI, or any consumed live executor.

## Adversarial Qualification

One final nonregistered generated qualification accepted all four registered
transport forms:

- clean connection close with no `Content-Length`
- one canonical `Content-Length`
- case-insensitive single `Content-Encoding: identity` plus length
- one exact `Transfer-Encoding: chunked`

All four produced the same inventory and selection identities. All 36 required
mutations refused on their registered route, including request drift,
redirects, response coding/framing ambiguity, overflow, malformed or duplicate
JSON, target leakage, row/count/checksum/anchor drift, cohort/split drift,
public-private leakage, output races, cap breaches, retry, and rerun.

The final generated measurement was:

| Measure | Observed | Cap |
|---|---:|---:|
| Generated response bytes read | 184,466 | 2,097,152 per response |
| Transient combined output | 19,030 | 2,097,152 |
| Incremental disk | 19,030 | 4,194,304 |
| Reported runtime | 0.030280291102826595 sec | 30 sec |
| External wall time | 0.11 sec | 30 sec |
| Reported peak RSS | 43,057,152 bytes | 268,435,456 |
| External peak RSS | 43,089,920 bytes | 268,435,456 |
| Output files created / removed | 3 / 3 | 3 / exact cleanup |
| Public inspections | 1 | 1 |

The generated run made 30 mock HTTP calls and 18 bounded in-memory response
reads across accepted and adversarial cases. It made zero real network
requests, participant-archive requests, payload reads, signal reads, target
reads, training runs, model runs, prediction sets, scoring events, provider
calls, hardware operations, other-project operations, retries, reruns, or
claim upgrades. The temporary output directory no longer exists.

## Hashes

The final generated identities are domain-separated:

- inventory: `47f3a328b57c5aed0b4990af944c1780cc5a88d0f1695f5f716719d2fe3f37e6`
- target-free selection: `49423fb153c4d58795c0f729c1fab788dbc0211ab25bf1eec2b163f760e45d03`
- generated response body: `b2dbca16be6bf148e0c31af17a8fe77cb693e483340eb522bc039ab6185f6b0f`
- generated private manifest: `35fe721c6ca99049dd10a39adbf5c9d974b124df1727d22f88b0e3d4140c9865`
- generated consumed marker: `83ed4d5f6baa9b7ddaba16e7f7be695e102265b94128348f6dc61c947c24ba81`
- generated public report: `9304c18050a0ea5beaa1a7f30b0dd0021c61628108e115ec841fc9a74fab99d2`

These generated identities prove deterministic interface behavior only. They
are not hashes of a live Figshare response or participant payload.

## Verification And Next Gate

Focused behavior tests cover request identity, all accepted transport modes,
the 36-mutation matrix, duplicate-key and target firewalls, deterministic
selection, capability races, output modes, aggregate failure receipts, public-
only inspection, machine caps, forbidden retries, and rejection of ungreen
implementation evidence. Repository-wide tests, Ruff, compilation, CLI help,
JSON replay, and diff hygiene must all pass before the implementation commit.
Generated unit tests inject a fixed clock and RSS reader so an earlier test's
process-wide peak cannot falsely fail this lane; the standalone measurement
above uses the real process clock and peak-RSS reader.

Final local verification passes 21 behavior tests, 12 implementation-record
tests, and all 658 MARC tests. The corrected dependency-light suite passes
2,797 tests with 204 expected skips in 25.003 seconds at 315,179,008-byte
external peak RSS. The corrected isolated optional environment passes 2,853
tests with 34 expected skips in 70.327 seconds at 717,783,040-byte external
peak RSS. Before the portability correction, the canonical optional
environment passed 2,868 tests with 35 expected skips.

Two canonical optional reruns after the correction reached all 2,868 tests but
failed one and then two older late-process mechanical rehearsals. The same
`tiny_causal_encoder_gate` and `streaming_ctc_gate` tests passed immediately in
fresh isolated processes, and the exact corrected source passed the complete
isolated optional environment. No unrelated gate was relaxed or changed. Fresh
remote Base Python and Optional Neuro Readers jobs remain the decisive
cross-platform gate. Complete-suite RSS describes the whole long-lived test
process, not this lane's standalone execution.

The first implementation push, `8f67af2`, failed Base Python job
`94153342511` and Optional Neuro Readers job `94153342668` in CI
`31608450681` because seven generated tests assumed macOS `/private/tmp`,
which does not exist on the Linux runner. No registered path, network, source,
payload, neural, target, model, or score operation occurred. The correction
uses the canonical real path of `tempfile.gettempdir()` only for generated and
test temporary parents. The exact registered real-execution path is unchanged.

Next, commit and push this exact implementation and require both CI jobs to be
green. Only then may the one registered `/private/tmp` output and one Figshare
metadata response be consumed. Any post-marker failure parks the lane, and a
successful response still stops before every participant ZIP or neural-data
operation.

Engineering capability added: a capability-first, target-firewalled,
privacy-preserving wrapper can deterministically validate and bind the complete
Wrist inventory and frozen cohort from one bounded metadata response.

Scientific claim not established: generated and metadata-only qualification
contains no neural signal, target, prediction, decoding score, language result,
or thought-to-text evidence.
