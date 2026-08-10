# IACKD Header Inventory Audit Implementation

Date: 2026-08-10

Status: **Generated-fixture qualified; exact implementation must be committed,
pushed, and remotely green before a separate Tier C real-header decision can
be recorded.**

Lane: **IACKD-H1 Header Inventory Audit**

Registry: `registries/iackd_channel_inventory_implementation.v0.json`

## Parent Gate

The prospective registration is commit
`0e52278aaa1d15e70f4baab7b21ab1c96eb37f67`. CI run `31412667060`
passed Base Python job `93534203368` and Optional Neuro Readers job
`93534203385` before implementation began.

The implementation does not broaden
`registries/iackd_channel_inventory_contract.v0.json`. The 128-object,
161,792-byte public VHDR surface, exact response requirements, seven-name
allowlist, frozen six-route diagnostic tree, one-thread resources, no-rerun
rule, and metadata-only claim ceiling remain authoritative.

## Capability Implemented

The standard-library-only module exposes a dry-run-first CLI without changing
the central `neurodecode` CLI hashed by consumed historical evidence:

```bash
python -m neurodecodekit.preprocess.iackd_header_inventory
python -m neurodecodekit.preprocess.iackd_header_inventory \
  --fixture --out /tmp/iackd-header-fixture.json
python -m neurodecodekit.preprocess.iackd_header_inventory \
  --inspect /tmp/iackd-header-fixture.json
```

The default command reconstructs the 128-header metadata surface from the
committed inventory and reports zero network requests, zero real parses, and
zero local IACKD bundle access. Fixture mode generates target-free VHDR bytes
at every registered body size and passes them through a one-open mocked
transport. Inspect mode validates only the bounded aggregate ledger.

The parser supports strict UTF-8, UTF-8 with BOM, and declared Windows-1252.
It rejects replacement decoding, disallowed controls, a non-exact preamble,
duplicate or missing required sections and keys, unsafe sibling references,
malformed sampling declarations, channel gaps, duplicate normalized names,
and non-four-field channel rows. DataFile and MarkerFile declarations are
validated only as inert basenames; their values are never emitted or resolved.

The response boundary requires status 200, unchanged final URL, exact
Content-Length, exact ETag, identity encoding, identity transfer, one bounded
body read, one SHA-256, and one semantic parse. The real opener is sequential,
rejects redirects, sends `Accept-Encoding: identity`, and has no retry path.

Each parsed header becomes a signature containing only declared count,
ordered-name-list SHA-256, sampling declaration, and seven exact allowlisted
presence booleans. Public output contains aggregate occurrence counts and the
first deterministic signature diagnosis, never individual object paths,
unallowlisted channel names, raw text, comments, sibling names, participants,
signals, events, trajectories, labels, targets, or predictions.

## Future One-Shot Boundary

The complete real executor is present but remains unreachable without a new
tracked decision artifact. It validates the future implementation and decision
hashes, exact green commit and CI identifiers, clean tracked worktree, commit
ancestry, execution ordinal one, and all frozen authorization counters. Only
then may it write a private consumed marker before the first request and stream
the 128 public headers into one aggregate ledger.

There is currently no decision file. `--execute` either refuses missing
evidence or fails at `IACKDH-F01` before transport. The existing 7.249 GB local
IACKD bundle is never named, resolved, statted, or opened by this module.

## Measured Synthetic Qualification

One isolated generated-only qualification exercised all 128 registered body
sizes and the complete mocked response, parser, signature, router, writer, and
loader path:

| Measure | Observed |
|---|---:|
| Generated VHDR bodies | 128 |
| Generated input bytes | 161,792 |
| Body SHA-256 passes | 128 |
| Semantic parses | 128 |
| Unique signatures | 1 |
| Synthetic route | `IACKDH-R1` |
| Ledger runtime through serialization | 0.036033750 seconds |
| Runtime through return | 0.037818958 seconds |
| Peak RSS through return | 36,634,624 bytes |
| Generated ledger bytes | 4,465 |
| Network bytes | 0 |
| Real VHDR requests / parses | 0 / 0 |
| Other real or protected operation sum | 0 |
| Real-only gates correctly false | 3 |

The temporary ledger SHA-256 was
`d93043938cdd94234e3aa02b2a039012931ff7b9151884a598255058f9caf28a`.
It was removed automatically when its temporary qualification directory
closed. The synthetic `IACKDH-R1` route proves only that the test fixture was
constructed to satisfy the old combined gate; it has no scientific or
real-source meaning.

## Adversarial Coverage

Twenty-four focused tests cover:

- all strict codepage paths, malformed bytes, controls, preamble, sections,
  keys, sampling, sibling basenames, channel counts, gaps, names, and fields;
- deterministic signatures and all `IACKDH-R0` through `IACKDH-R5` routes;
- response status, redirect-equivalent URL drift, ETag, compression, length,
  row count, byte total, thread, RSS, output, overwrite, and dependency gates;
- heavy-import refusal, forbidden counter classes, raw/name/path leakage,
  duplicate JSON keys, bounded load and inspect, and immutable warnings;
- two complete 128-header deterministic aggregate replays; and
- default and missing-evidence CLI paths with network construction patched to
  fail if touched.

The base suite increased from 1,631 to 1,655 tests before the implementation
record tests were added, with the same 182 optional-dependency skips and no
regression. Final complete-suite and static verification are recorded in the
machine registry after the full implementation surface is assembled.

## Next Gate

Commit and push this exact implementation, then require both GitHub CI jobs to
pass at that commit. Only after that proof exists may one additive
authorization packet bind the implementation hash and request the single
161,792-byte public-header execution. No previous `continue` instruction can
be applied retroactively to that future Tier C operation.

Engineering capability added: NeuroDecodeKit now has a deterministic,
sibling-blind, aggregate-only audit that can identify which file-contract
assumption caused the consumed IACKD channel gate to fail without reopening
the downloaded dataset.

Scientific claim not established: no real IACKD header, EEG sample, event,
trajectory, target, model, prediction, or score was accessed, so this work
establishes no neural effect, action decoding, brain-specific origin,
generalization, real-time operation, hardware capability, assistive benefit,
or clinical use.
