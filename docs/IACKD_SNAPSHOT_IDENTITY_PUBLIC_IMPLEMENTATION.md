# IACKD-M1A Public Snapshot Wrapper Implementation

Date: 2026-08-11

Status: **generated and mocked wrapper qualification passed; exact wrapper
commit and remote CI are still required before one public request**

Machine record:
`registries/iackd_snapshot_identity_public_implementation.v0.json`

Authorization decision:
`docs/IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_DECISION.md`

## Green Entry Gate

Packet-bound decision commit
`4165c24cdad9768c7e36b5e4893602d02434be50` passed CI `31485359989` before
this implementation began:

```text
Base Python:             93759373384  success
Optional Neuro Readers: 93759373333  success
```

The implementation therefore uses the decision's narrow additive permission:
generated response fixtures, mocked transport, and standard-library wrapper
qualification only. This document does not say that a public request has run.

## Capability Added

`src/neurodecodekit/datasets/iackd_snapshot_identity_public.py` adds a
source-independent wrapper around the green snapshot canonicalizer. It:

1. reconstructs and hashes the frozen 316-byte query and 355-byte request;
2. validates the exact green decision and immutable canonicalizer source;
3. requires a clean exact Git HEAD and externally verified wrapper CI evidence
   before the real executor can proceed;
4. measures the five one-thread environment values, free disk, logical CPUs,
   normalized one-minute load, and peak RSS before consumption;
5. creates a new exclusive private root and marker before the first request;
6. permits one POST to one endpoint with no credentials, redirects, retries,
   alternate query, endpoint, or response read;
7. accepts only HTTP 200, the exact final URL, identity encoding, and one of
   the registered fixed-length, chunked, or close-delimited framing profiles;
8. reads at most 2,097,153 bytes once and accepts at most 2,097,152 bytes;
9. passes the same in-memory body once to the green strict semantic
   canonicalizer and then drops the raw body reference;
10. separates the private 1,340-row selected manifest from an aggregate-only
    public result; and
11. emits a sanitized consumed-failure result if any post-marker transport or
    semantic gate refuses.

The module has `plan`, `qualify`, `inspect`, and evidence-gated `execute`
commands. `plan`, default help, and `qualify` have no usable public-data path.
There is no local IACKD input argument, credential argument, S3 downloader,
payload loop, model path, target path, or dependency beyond the standard
library and the already green canonicalizer.

## Generated And Mocked Qualification

One formal generated qualification used the same deterministic 1,679-object
response fixture as IACKD-M1. The HTTP opener was an in-memory single-use
fixture. No socket, provider, public body, local IACKD path, old consumed root,
EEG sample, target, model, or score was accessed.

```text
route:                                  IACKDMP-R0 constructed
generated response bytes:               531,067
generated response SHA-256:             3059505bcc0d8a22d1f3c1d350fce16b20b3272dc32854945667c1c0ccfd20b3
query / request bytes:                  316 / 355
mock opens / body reads:                1 / 1
deterministic semantic replays:         2
wrapper refusal mutations:              20 / 20
tree / selected rows:                   1,679 / 1,340
selected declared payload bytes:        7,249,113,684 metadata only
runtime:                                0.09886470879428089 sec
peak RSS:                               46,563,328 bytes
free disk before qualification:         25,560,076,288 bytes
one-minute load / logical CPUs:         7.11669921875 / 12
normalized one-minute load:             0.5930582682291666
aggregate report bytes:                 6,151
private manifest bytes:                 423,279
combined generated output:              429,430 bytes
public GraphQL / S3 requests:           0 / 0
local IACKD / old-root operations:       0 / 0
signal / target / model / score runs:    0 / 0 / 0 / 0
producer causal:                        unavailable
end-to-end latency measured:            false
```

The temporary generated output is not tracked and remains under
`/private/tmp`; it is not a public result and has no source or scientific
meaning.

## Adversarial Coverage

The wrapper refuses non-200 status, final-URL drift, redirects, compression,
unsupported or conflicting framing, duplicate or noncanonical Content-Length,
declared or observed body overflow, length mismatch, read failure, non-byte
bodies, opener failure, wrong thread settings, low disk, excessive or missing
load, runtime overflow, RSS overflow, output collision, private-row leakage,
nonzero forbidden counters, malformed green proof, pre-marker machine failure,
and attempted rerun after a consumed marker.

Generated tests also exercise success through all three registered framing
profiles and the consumed semantic-failure report. The prior green
canonicalizer separately retains its 37 semantic refusal mutations; this
wrapper imports that exact source by SHA-256 rather than duplicating or
loosening it.

## Remaining Ordered Gate

This exact implementation must now be tested, committed, pushed, and pass both
remote CI jobs. Only then may the operator independently verify the exact
commit and job IDs, apply the live machine gate, and invoke `execute` once.

The private marker must precede the request. Any failure after that marker
consumes IACKD-M1A. There is no retry, rerun, alternate endpoint, query change,
fallback, payload acquisition, or post-result update.

No EEG payload is authorized by this implementation or by a future metadata
compatibility result.

## Claim Boundary

Engineering capability added: one bounded, dependency-free wrapper can
separate transport provenance from snapshot, tree, selected-inventory, and
critical-metadata identities while keeping individual object rows private.

Scientific claim not established: generated metadata and zero neural reads
establish no neural effect, decoding accuracy, brain-specific origin,
generalization, language or thought decoding, real-time operation, portable
hardware, home use, assistive benefit, or clinical utility.
