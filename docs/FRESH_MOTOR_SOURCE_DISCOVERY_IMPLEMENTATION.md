# Fresh Motor Source Discovery Implementation

Date: 2026-08-30

Implementation: `FMSR1-DISCOVERY-M0-G1`

Status: **generated implementation and qualification complete locally; public
metadata execution is parked because the current packet did not freeze exact
official-index revisions or an externally authenticated CI attestation**

Machine record:
[`fresh_motor_source_discovery_implementation.v0.json`](../registries/fresh_motor_source_discovery_implementation.v0.json)

## What Was Added

NeuroDecodeKit now has a dependency-free generated source-discovery planner,
strict response reader, redirect and pagination firewall, candidate
canonicalizer, deterministic router, resource ledger, generated qualification,
and CLI:

```bash
PYTHONPATH=src python -m neurodecodekit.fmsr1_discovery_cli plan
PYTHONPATH=src python -m neurodecodekit.fmsr1_discovery_cli qualify-generated
```

The planner emits exactly 17 roots: four exact queries each for OpenNeuro,
NEMAR, PhysioNet, and GigaDB, plus the complete BNCI motor/EEG catalogue
surface. It binds the exact HTTPS endpoint path, method, host set, query-key
grammar, parser profile, and 30-second maximum request timeout for every root.
The callable page reader accepts only the exact generated fixture transport and
mock resolver. It has no caller-selected real-network mode. The retained
`execute` command fails closed before evidence verification, marker creation,
DNS, or HTTP because all five packet-bound official revisions are absent.

## Complete Or Park

A candidate may be ranked only after every root and every discovered page has
completed. Repeated request identities, repeated page identities or bodies,
pagination cycles, ambiguous terminal state, unknown schema, revision mismatch,
malformed or truncated bodies, cap breaches, and endpoint drift fail closed.
Partial candidates are never ranked.

OpenNeuro requires the exact registered GraphQL `data.datasets.edges` and
`pageInfo` shape. Other JSON requires an explicit results container and an
explicit terminal or next-page state. HTML requires an explicit result surface
or no-results marker and an explicit pagination declaration with an
unambiguous next or terminal state whenever a candidate is present. JSON-LD
alone cannot establish completeness. These profiles are implementation
declarations, not official index revisions and not claims that the live
endpoints were contacted or verified.

## Candidate Firewall

Missing or ambiguous facts are false. A generated passing candidate must make
all of the following explicit:

- synchronized EEG, recorded EOG, and EMG for every named task effector;
- at least ten complete participants;
- named EEG channels, geometry, and a constructible posterior comparator;
- reference, sampling, events, targets, and decision semantics, with cue
  identity explicitly unable to equal the target;
- at least two non-cue motor classes;
- immutable release identity and reusable payload license;
- complete member sizes and hashes available without payload access;
- no more than 12 GiB of selected payload;
- documented format and reader; and
- all six type-checked deterministic sort fields with internally consistent
  participant and storage arithmetic.

Canonical IDs use NFKC normalization, surrounding ASCII trimming, explicit
component types, and a non-ambiguous `::` separator. All six frozen consumed-
source IDs and their known index aliases are excluded, including BNCI
`001-2014`. Target-like keys are rejected
after NFKC normalization except the one required boolean target-semantics flag.
Payload URLs and forbidden retained fields are rejected recursively. Every
retained candidate fact requires an allowlisted provenance entry.

## Resource And Authority Controls

The generated implementation enforces one worker and one CPU thread, 128 requests,
separate 32 MiB cumulative wire and decoded-body ceilings, an 8 MiB page
ceiling, an 8 MiB retained-report ceiling, a 300-second monotonic deadline,
256 MiB peak RSS, three redirects per request, identity encoding, zero retries,
and cap-plus-one reads. Redirect, error, and unsupported-content-type bodies
count. Unsupported encodings are refused before body consumption. Every
fixture request receives a monotonic whole-request deadline; redirects cannot
change method, endpoint path, or frozen query. Resolved addresses must be
globally routable and may not be multicast, reserved, or unspecified.
Because `ru_maxrss` is process-lifetime state, in-process unit calls enforce the
256 MiB ceiling against additional peak RSS above entry; the standalone
qualification measurement below reports the absolute process peak.

The generated verifier can check tracked local artifact identities, commit
ancestry, and a proof record, but that record cannot authenticate GitHub by
asserting its own run and job fields. More importantly, the governing packet
required every official index revision to be bound before execution, while the
registration froze only parser-profile names and runtime revision-header
requirements. Accepting an arbitrary runtime `ETag` or `Last-Modified` value
would be post-registration admission, not packet binding.

The implementation therefore does not expose a real transport path. The
future live route requires an additive, all-false correction that freezes an
exact revision-admission mechanism and externally verifies the exact GitHub
run before any new execution decision. This milestone creates no such packet
or authority.

## Generated Qualification Result

One local qualification completed two deterministic 17-root mock-HTTP replays.
Both selected the same fictional candidate and produced deterministic digest
`7e22a12594b8c9229f0534ed045d3f470f46faca5b3d460a8a8b50297e23b18e`.
The run made 34 mock HTTP calls and passed 25 adversarial refusal cases,
including cap-plus-one, truncation, unsupported transfer/content encoding,
off-surface and same-host endpoint drift, POST rewrite, duplicate JSON keys,
Unicode/plural target leakage, retained-field leakage, identity conflict,
duplicate pages, pagination cycles, ambiguous pagination, incomplete traversal,
runtime, non-global resolution, unsupported-content accounting, HTML terminal
ambiguity, generated-transport bypass, and authority checks.

Measured locally:

| Measurement | Result | Cap |
|---|---:|---:|
| Runtime | 0.0161428339779377 s | 300 s |
| Peak RSS | 52,510,720 bytes | 268,435,456 bytes |
| Aggregate qualification report | 4,761 bytes | 8,388,608 bytes |
| Real network requests / bytes | 0 / 0 | 0 before green proof |
| Payload or header reads | 0 | 0 |
| Signal/event/annotation/target/label reads | 0 | 0 |
| Model / training / prediction / score runs | 0 / 0 / 0 / 0 | 0 |
| Provider / stream / device / hardware runs | 0 / 0 | 0 |
| Cleanup or deletion operations | 0 | 0 |

The fictional candidate demonstrates routing mechanics only. It is not a real
source and is not evidence for any point in the 3D attribution cube or outer
5D evidence map.

## Next Ordered Barrier

Commit and push this exact generated implementation, then require Base Python
and Optional Neuro Readers to pass on GitHub `main`. Record that exact green
state as a proof-only closeout, with no live activation. The next scientific
step is not to execute this packet: it is to design an additive revision-
admission and remote-attestation correction, subject it to independent review,
and obtain a fresh exact decision before any public metadata contact.

Engineering capability added: a deterministic, complete-or-park generated metadata-discovery engine now exists and has passed adversarial qualification while refusing an inexact live gate.

Scientific claim not established: no public discovery request, real EEG, source-specific metadata, payload, model, score, unseen-person result, nuisance-resistant neural effect, language result, or live decoding result was produced.
