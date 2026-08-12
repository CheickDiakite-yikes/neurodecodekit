# MARC1-HT1 HTTP Identity Semantics Recovery Research

Date: 2026-08-12

Status: **Artifact-only research complete; no implementation or real access is
authorized**

Machine record:
`registries/marc1_http_identity_semantics_recovery_research.v0.json`

## Purpose

`MARC1-P1A` consumed at `MARC1PS-F03` after one private inventory read and one
Wrist response open. The frozen terminal rule required the response to contain
an explicit `Content-Encoding: identity` field. The raw response header was
not retained, so the repository cannot claim whether that field was absent or
contained another value. Its value must not be inferred.

This research asks a narrower question: what terminal content-encoding rule
matches HTTP semantics while still guaranteeing that NeuroDecodeKit never
accepts a compressed or otherwise coded body in this metadata lane?

The thought-to-text objective is unchanged. This is a same-path transport
repair needed before the confound-resolved positive-control cohort can be
selected; it is not a new scientific direction.

## Primary Sources

### RFC 9110 Section 8.4: Content-Encoding

The current HTTP Semantics standard defines `Content-Encoding` as the list of
content codings applied to a representation. A sender that applies one or more
codings must generate the field. The same section says that the `identity`
coding is reserved for its role in `Accept-Encoding` and should not be placed
in `Content-Encoding`.

Source:
<https://www.rfc-editor.org/rfc/rfc9110.html#section-8.4>

### RFC 9110 Section 12.5.3: Accept-Encoding

The standard defines `identity` in `Accept-Encoding` as a synonym for no
encoding. A representation with no content coding is acceptable by default
unless the request explicitly excludes identity.

Source:
<https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.3>

## Diagnosis

The old rule conflated two separate surfaces:

```text
request preference:       Accept-Encoding: identity
response representation:  Content-Encoding absent when no coding was applied
```

Requiring the response to repeat `identity` in `Content-Encoding` is not the
standards-preferred way to prove that the representation is unencoded. This is
a prospective contract diagnosis. It does not reveal the live response's
unretained header and does not amend, retry, or reinterpret MARC1-P1A.

## Candidate MARC1-HT1 Rule

The future generated validator should classify terminal responses as follows:

| Response state | Candidate decision | Reason |
|---|---|---|
| `Content-Encoding` absent | accept as no applied content coding | standards-preferred unencoded representation |
| one case-insensitive `identity` token | accept only as a narrow compatibility tolerance | preserves an inert legacy form without enabling decoding |
| empty present field | refuse | ambiguous malformed presence |
| `gzip`, `br`, `deflate`, `compress`, or another token | refuse | a content coding was declared |
| a list containing `identity` and another token | refuse | at least one real coding was declared |
| duplicate `Content-Encoding` field lines | refuse | critical-header ambiguity |
| any `Transfer-Encoding` field | refuse | unchanged framing boundary |

The request continues to send `Accept-Encoding: identity`. The implementation
must not decompress, decode, normalize, or retry a coded response.

## Unchanged Protections

MARC1-HT1 may change only the terminal content-encoding predicate. It must
preserve all of these MARC1-P1A protections byte for byte or behaviorally:

1. The exact Figshare record, version, endpoint, participant archive names,
   seven-field row schema, `sub-01` anchor, and declared record byte total.
2. One terminal JSON body capped at 2 MiB, one body read, strict UTF-8 and JSON,
   and exact row validation before selection.
3. Automatic redirects disabled; at most two bodyless HTTPS redirects, three
   total attempts, global-address checks, no credentials, and no proxy use.
4. Duplicate critical headers, non-JSON media type, malformed length, oversized
   body, alternate endpoint, fallback, retry, rerun, or substitution refusal.
5. One no-follow/open/read/hash/parse of the exact private Freewill manifest,
   but only in a future separately authorized real execution.
6. Consumed marker before any future private or public input; private/public
   output separation; no raw body, raw header, URL, participant row, or path in
   the aggregate report.
7. One CPU thread, one worker, one numerical job, 120 seconds, 256 MiB peak
   RSS, 32 MiB incremental disk, 1 MiB public output, 8 MiB combined output,
   and at least 12 GiB free disk.
8. No payload, local header, signal, event, target, quality, derivative,
   training, inference, prediction, score, provider-model, hardware, release,
   or claim interface.

## Prospective Qualification

After this research record is committed, pushed, and both CI jobs are green,
a separate preregistration may freeze generated and mocked fixtures for:

- absent `Content-Encoding` success;
- explicit lower-, upper-, and mixed-case identity success;
- empty, whitespace, comma-list, parameterized, and duplicate-field refusal;
- `gzip`, `br`, `deflate`, `compress`, wildcard, and unknown-token refusal;
- unchanged transfer-encoding, content-type, content-length, overflow,
  redirect, DNS, privacy, target-firewall, output-cap, and no-rerun refusals;
- deterministic replay producing the exact same 12+12 aggregate selection;
- source inspection proving that no decompressor or decoder is imported or
  called.

The generated implementation must have no URL or private-path executor until
its own exact commit is remotely green. A later real wrapper must be additive;
it cannot import or call the consumed MARC1-P1A executor and cannot operate on
its private root.

## Gates

`MARC1HT-R1` may mean only that generated response semantics pass and every
forbidden operation remains zero. It has no source or scientific value.

One future real metadata invocation would require all of the following:

1. This research record remotely green.
2. A separate frozen contract remotely green.
3. A generated/mock implementation and measured closeout remotely green.
4. An all-false Tier C request remotely green and identified as the sole active
   packet.
5. A fresh packet-bound maintainer decision remotely green.
6. A new private root and consumed marker; the old MARC1-P1A root is forbidden.

No current or earlier `continue`, approval, or authorization is retroactive to
that future request.

## Verification

Ten focused research tests and all 349 MARC tests pass. The complete
dependency-light suite passes 2,488 tests with 204 expected skips in 20.420
seconds at 281,296,896-byte external peak RSS. The optional-neuro suite passes
2,559 tests with 35 expected skips in 57.130 seconds at 771,407,872-byte
external peak RSS. Both complete suites add exactly ten tests and zero skips
over the green consumed-result baseline.

Ruff, compileall, strict parsing of every registry JSON document, canonical
policy-hash replay, and `git diff --check` also pass.

## Claim Boundary

Engineering capability proposed: a standards-aligned, fail-closed predicate
can distinguish an unencoded HTTP representation from every declared content
coding without weakening the existing metadata, privacy, or machine gates.

Scientific claim not established: this artifact-only transport research reads
no neural signal, target, prediction, or score and establishes no neural
effect, language decoding, or thought-to-text capability.
