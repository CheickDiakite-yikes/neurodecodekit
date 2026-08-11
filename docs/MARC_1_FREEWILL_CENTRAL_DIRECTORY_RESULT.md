# MARC1-CD1 Generated Central-Directory Result

Date: 2026-08-11

Status: **consumed at `MARC1CDG-R1`; generated engineering qualification
passed; no retry or rerun; no public metadata or archive access authorized**

Registry:
`registries/marc1_freewill_central_directory_result.v0.json`

## Green Implementation Gate

The one registered closeout ran only after exact implementation commit
`211fd78fba82a660c4730a586541819b2eb264fd` passed both required jobs in CI
run `31511626051`:

```text
Base Python:             93846584402
Optional Neuro Readers: 93846584527
```

The execution bound implementation registry SHA-256
`9cd010cd7bae25bb43c01e25c46169439103c66bf20292485f80da2ee701ee7a`.

## Registered Execution

Exactly one fresh Python `-S` process ran with one CPU thread, one worker, one
numerical job, `PYTHONPATH=src`, and a new output directory under the real
`/private/tmp` parent. The module had no network client, live endpoint, DNS
query, real archive path, or member reader.

The command completed once with `MARC1CDG-R1`:

```text
virtual archive bytes:             13,591,548,048
generated input bytes:                    280,249
generated output bytes:                    11,574
central-directory bytes:                  148,910
entries:                                        18
ZIP64 extended members:                          1
direct-path mock requests:                       3
redirect-path mock requests:                     5
bodyless redirects:                              2
mock body bytes per path:                   280,249
mutation refusals passed:                        32
acceptance gates passed:                         14
reported runtime seconds:       0.006544457981362939
reported peak RSS bytes:                 27,131,904
external process wall seconds:                   0.12
external maximum RSS bytes:                27,181,056
```

The aggregate report was 5,898 bytes with SHA-256
`a8bfc657ca77464292c7ab047e46a7a8cec1c66bb9876845a2ef30c7e4c355ab`.
The generated private manifest was 5,676 bytes with SHA-256
`c38c0be784f19401b08da26bdd2d0dd6a43339c34202f6845c7ca7cb6b5c4bf0`.
The aggregate report was inspected once through the registered CLI. The two
exact temporary files and their now-empty invocation directory were then
removed. No generated output is committed.

## Archive Result

The virtual archive identity remained exactly 13,591,548,048 bytes while the
fixture materialized only 280,249 bytes. The parser reconciled the decoy-
bearing classic EOCD, ZIP64 locator, and complete ZIP64 EOCD inside the fixed
128-KiB tail. The resulting 148,910-byte central directory contained:

- 18 entries: four directories and fourteen regular files;
- five stored entries and thirteen deflated entries;
- one UTF-8 path and exactly one ZIP64 extended member;
- 4,300,569,216 declared compressed member bytes;
- 5,000,886,384 declared uncompressed member bytes; and
- canonical inventory SHA-256
  `e8e46341bfab793605bafec2def82b93cae8016c58cf1a26275d8ca2cffb2c8b`.

The exact generated names and offsets existed only in the removed private
manifest. No local header or member payload existed or was opened. The
registered whole-archive MD5 was identity metadata only and was not verified
against 13.59 GB of content.

## Transport Result

Both generated paths passed:

- the direct path made three mock requests and no redirect; and
- the redirected path made five mock requests with two bodyless HTTPS
  redirects.

Each path read three generated response bodies totaling 280,249 bytes. Both
terminal range responses used exact `206`, `Content-Range`, `Content-Length`,
identity encoding, and single-part framing. The final inventory and aggregate
report replayed canonically across both independently generated fixtures and
both transport paths.

This validates generated mechanics only. Live Figshare range support, final
redirect identity, ETag, Last-Modified, response framing, and real archive
inventory remain unavailable.

## Adversarial Result

All 32 frozen mutations refused in their assigned aggregate-safe class:

```text
MARC1CDG-F00: 1
MARC1CDG-F02: 4
MARC1CDG-F03: 8
MARC1CDG-F04: 8
MARC1CDG-F05: 9
MARC1CDG-F06: 2
```

Separate implementation tests also enforce `MARC1CDG-F01` resource refusal.
All fourteen acceptance gates passed. Every live metadata, archive HEAD/range,
network redirect, whole-download, real-path, local-header, payload, signal,
event/onset, target/label, derivative, model, prediction, freeze, delivery,
score, and claim-upgrade counter remained zero.

## Warnings And Unavailable Fields

- Generated and mocked ranges contain no public or human data.
- Live range support and final transport identity are unavailable.
- Whole-archive MD5, member CRC-32, local-header consistency, and member
  payload integrity are unavailable.
- Real entry count, real member inventory, participant selection, signal,
  event, target, model result, and score are unavailable.
- End-to-end latency was not measured; the process wall time is only an
  engineering runtime observation.
- `MARC1CDG-R1` cannot authorize a live request, member acquisition, or
  scientific claim.

## Disposition

The registered generated closeout is consumed with no retry or rerun. The
implementation and result do not open a public response by themselves. The
next eligible work is one all-false Tier C authorization request binding a
future no-retry metadata and central-directory range audit. That request must
be committed, pushed, and remotely green before it may be identified as the
sole active packet; only a fresh packet-bound maintainer decision after that
identification could authorize a live response.

Even a future live `MARC1CD-R1` would establish archive inventory only. Member
acquisition, payload integrity, signal/event/target access, training,
inference, scoring, and scientific promotion remain later separately frozen
work.

Engineering capability added: a measured dependency-free generated
qualification has now demonstrated bounded range transport, decoy-resistant
EOCD and ZIP64 parsing, exact central-directory inventory, private/public
separation, deterministic replay, refusal routing, and resource accounting
without materializing the 13.59 GB archive.

Scientific claim not established: no public archive byte, member payload,
human neural signal, event, target, model, prediction, or score was accessed,
so this result establishes no neural effect, movement decoding, source
attribution, or scientific result.
