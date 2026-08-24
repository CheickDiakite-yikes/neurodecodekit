# EEGMMIDB-UG1 Stage S-A1 Generated Source-Acquisition Result

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-SA1`

Status: **Passed once; consumed; one non-scientific mock-counter schema
discrepancy documented; proof-only closeout pending remote green**

Machine result:

- `registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_result.v0.json`

## Proof Order

The packet-bound decision `1b5c9195f384e5867f18131aa7d669f7c9cd0e2b`
was remotely green before implementation. The corrected implementation commit
`37808bef8c59bc862345f342fd932aa04373b3fd` then passed Base Python job
`97441967842`, Optional Neuro Readers job `97441968304`, and CI
`32730673153` before the one registered qualification was invoked.

The qualified source-acquisition module, implementation document, and machine
implementation record remain byte-for-byte unchanged after execution. The
qualification is consumed and may not be retried or rerun.

## One-Shot Result

All 27 frozen generated/mock cases passed in order. They covered complete
six-file publication, exact replay, checksum-manifest attacks, request-order
and missing-response failures, response identity and framing failures,
short/oversized/non-byte bodies, output collisions, second invocation,
resource limits, and refusal of a fresh-final path.

| Measure | Result |
|---|---:|
| Generated body bytes read | 67,199,028 |
| Successful generated bundles | 3 |
| Successful generated payload bytes | 46,496,448 |
| Generated metadata bytes | 11,232 |
| Aggregate output bytes | 1,901 |
| Aggregate output SHA-256 | `f2fbba2e102858d3e4328960b7772b3f5b6b83c3907266e99de45f19b7e7239e` |
| Mock requests | 56 |
| Opaque post-write passes | 18 |
| Maximum stream read | 1,048,576 bytes |
| Peak visible response headers | 755 bytes |
| Peak incremental disk | 15,523,840 bytes |
| Runtime | 0.4758401670260355 seconds |
| Peak process-tree RSS | 71,696,384 bytes |
| Initial free disk | 100,570,861,568 bytes |
| Retained generated output | 0 bytes |
| Real requests / network bytes | 0 / 0 |
| EDF semantic reads | 0 |
| Targets / model runs / training / scores | 0 / 0 / 0 / 0 |

The aggregate route was `EEGMMIDBUG1SA1-G1`. The generated source fixture had
SHA-256
`a864f0a57bfbc44fa3733199f2cd3b7e3d3dd23d1caad9765a22b20b20e8b6a4`.
The temporary aggregate is bound by exact size and SHA-256 and is not committed
to the repository.

Local verification passed 24 focused checks and the complete dependency-light
suite passed 5,891 tests with 212 expected optional-dependency skips. The
pre-result baseline was 5,884 passing tests, so the seven new result-contract
tests account exactly for the increase. Changed-file Ruff, compilation, all
registry parses, CLI help, and `git diff --check` also passed.

## Counter Correction

The raw aggregate's authoritative top-level `mock_requests` field correctly
reported 56. Its generic nested `operation_counters` block incorrectly
serialized `mock_checksum_requests` and `mock_EDF_requests` as zero. Those two
nested subtype fields are non-authoritative for this result.

The immutable 27-case flow determines the exact decomposition without another
execution: 21 checksum-manifest mock requests plus 35 EDF mock requests equals
the observed total of 56. This is a reporting-schema discrepancy only. It does
not create execution ambiguity, affect acquisition mechanics, change any real
or scientific counter, or justify a rerun. The raw aggregate remains preserved
by its exact 1,901-byte size and SHA-256 above.

## Interpretation

This proves that the dependency-light gate can enforce the registered checksum,
transport, streaming, complete-bundle, persistence, cleanup, and resource
contracts under adversarial generated transport. It does not prove that a real
EDF was acquired, that any payload contains usable EEG, or that a model can
generalize to an unseen participant.

Producer causality is not applicable to opaque acquisition transport.
End-to-end decoding latency was not measured. Real transfer checksums, bundle
identity, EDF content, targets, and every neural-performance field remain
unavailable.

## Next Gate

Commit, push, and remotely green this exact result. Then add a separate
proof-only closeout that binds the unchanged implementation and measured result
without repeating qualification. Stage S-A2 remains closed until that
proof-only closeout is also pushed and both required CI jobs pass.

Engineering capability added: the checksum-bound streaming source-acquisition
gate passed its sole registered 27-case generated qualification with exact
replay, complete-bundle publication, and bounded resource use.

Scientific claim not established: no real request, EEG payload, target, model,
or score was accessed, so this result establishes no neural effect, decoding
advantage, movement intention, motor-cortex origin, eye independence, language
decoding, live performance, or unseen-person generalization.
