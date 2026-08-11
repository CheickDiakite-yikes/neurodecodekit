# IACKD-T1 Transport-Stable Recovery Implementation

Date: 2026-08-11

Status: **Generated-fixture qualified; exact implementation must be committed,
pushed, and remotely green before an all-false Tier C request is prepared**

Registry:
`registries/iackd_transport_stable_recovery_implementation.v0.json`

Module:
`src/neurodecodekit/datasets/iackd_transport_stable.py`

Green registration:
`ee0f62adf74afd390052694142090ccc0395c539`

Green registration CI:
`31472269070` (Base Python `93717995481`; Optional Neuro Readers
`93717995427`)

## What Was Built

The implementation is a standalone Python standard-library validator. It has
no URL opener, `--execute` flag, local dataset path, MNE import, numerical
dependency, model code, target interface, or scorer.

Its public interface provides:

- `ResponseSpec`, a strict fixture-only expected identity;
- `AuditedResponse`, a one-use wrapper that enforces read, hash, and parse
  ordering;
- `validate_and_parse_response`, with separate `metadata` and `payload`
  policies;
- three metadata framing profiles: fixed length, chunked, and clean close;
- exact cap-plus-one body reads and SHA-256 checks before parsing;
- advisory exact/different/unavailable metadata `Content-Length` states;
- exact payload `Content-Length` and ETag checks;
- a 22-mutation refusal matrix;
- deterministic generated replay, strict aggregate report validation, and an
  exclusive 1 MiB writer; and
- default plan, `--fixture`, `--inspect`, and `--help` CLI surfaces.

The module does not integrate with the consumed IACKD-2 executor. That
separation prevents generated implementation work from becoming an accidental
public request.

## Adversarial Coverage

The generated suite accepts:

1. exact fixed-length metadata;
2. valid but different fixed-length metadata only when observed bytes and
   SHA-256 are exact;
3. exact chunked metadata;
4. clean close-delimited metadata; and
5. exact fixed-length plus exact ETag payload mode.

It refuses all 22 registered mutations, including ambiguous length and
transfer coding, malformed/negative/comma-joined/over-cap length, unsupported
coding, compression, status/URL/redirect drift, body underflow/overflow/read
error/hash drift, read/hash/parse reuse or reordering, missing payload length
or ETag, unknown mode, non-generated source, and output cap breach.

Tests also cover case-insensitive header lookup, weak/different ETags, payload
length drift, strict spec fields, forbidden fixture terms, report mutation,
symlink input, output collision, wrong thread settings, runtime/RSS caps,
byte-identical replay, and default CLI closure. The module source contains no
`urllib.request`, socket operation, public executor, or `--execute` option.

## Measured Generated Qualification

One final generated qualification ran after the registration was remotely
green:

| Measure | Result |
|---|---:|
| Accepted validations across two replays | 10 |
| Refusal mutations | 22 |
| Generated input bytes | 848 |
| Generated output bytes | 5,540 |
| Runtime | 0.001049624988809228 seconds |
| Peak RSS | 20,332,544 bytes |
| CPU threads / workers / jobs | 1 / 1 / 1 |
| Network bytes | 0 |
| Public or real body reads | 0 |
| Local IACKD path operations | 0 |
| Model / training / inference / score runs | 0 / 0 / 0 / 0 |

The report SHA-256 was:

```text
c15fc798312e4117523e2b6732f8cf464f11e5b336fcc6feef3c615f737d1ea5
```

The bounded `--inspect` roundtrip reproduced the same aggregate summary. The
temporary report is not a tracked artifact and is removed after its
measurements and hash are recorded.

`producer_is_causal` is unavailable because this module validates transport,
not a signal producer. End-to-end latency was not measured. Real response
headers, framing, body identity, signal/target identity, and derivative
causality remain unavailable.

## Verification

- 17 implementation tests pass;
- 16 registration/research invariant tests pass;
- Ruff `0.15.20` passes the module and tests;
- Python compilation passes;
- both new registries parse as strict JSON;
- CLI help, default plan, fixture, and inspect paths pass; and
- `git diff --check` is clean.

The complete local suite is deliberately not launched while the workstation
load is above 100. The exact implementation commit must instead pass the full
Base Python and Optional Neuro Readers suites in remote CI before the next
milestone.

The first pushed implementation candidate, commit `6b89b7d`, ran in CI
`31473610218`. Base Python job `93722204649` passed, while Optional Neuro
Readers job `93722204707` failed one CLI test after the full suite had already
loaded MNE and raised the parent test process peak RSS to 383,049,728 bytes.
The standalone generated qualification measured 20,332,544 bytes; the failure
therefore exposed test-process contamination, not a validator body, network,
or identity failure.

The first repair candidate, commit `8d7be6a`, ran in CI `31474043386`. Base
Python job `93723535823` passed, while Optional Neuro Readers job `93723535798`
showed that a child created from the dependency-loaded test process could still
cross the frozen absolute RSS ceiling before its command-line module started.
The final repair therefore keeps deterministic injected resource monitors in
the unit path, tests command-line dispatch separately, and leaves absolute
peak RSS to the already completed fresh-process qualification. Neither failed
run can serve as green implementation proof.

## Next Gate

1. Commit and push this exact implementation.
2. Require Base Python and Optional Neuro Readers CI to pass.
3. Only then prepare an all-false Tier C packet binding the green registration
   and exact green implementation.
4. Stop after that packet is remotely green and identify it to the maintainer.

No current message authorizes real-executor integration, a public metadata
request, a 1,340-object stream, model fitting, prediction, target delivery, or
scoring.

Engineering capability added: a dependency-free, adversarially qualified
validator now separates metadata framing from exact body identity while
retaining strict large-payload length and ETag behavior.

Scientific claim not established: only generated response bodies were used,
so this implementation establishes no neural effect, action decoding,
brain-specific origin, language or thought decoding, real-time operation,
hardware capability, assistive benefit, home use, or clinical use.
