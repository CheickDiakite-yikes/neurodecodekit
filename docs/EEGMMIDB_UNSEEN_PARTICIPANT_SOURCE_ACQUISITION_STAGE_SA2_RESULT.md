# EEGMMIDB-UG1 Stage S-A2 Source Acquisition Result

Date: 2026-08-24

Status: **Failed before any HTTP response; consumed and permanently parked**

Machine result:
`registries/eegmmidb_unseen_participant_source_acquisition_stage_sa2_result.v0.json`

## Ordered Proof

The live boundary did not open until every earlier barrier was remotely green.
The first activation commit, `4c7800e`, failed CI only because a new proof test
assumed full Git history in GitHub's shallow checkout. No live operation was
attempted from that commit. The test-only repair `9cc2688` preserved the
qualified module and activated proof registry byte-for-byte, passed Base job
`97467118679`, Optional Neuro Readers job `97467118486`, and CI
`32738530528`, and was the exact execution HEAD.

Before execution:

- the worktree contained only the maintainer's unrelated untracked tracker
  inspection file;
- the qualified module SHA-256 remained
  `3e6d7c8ee9b52286860d59c26061f3f52521905d91bfad166c7618feaacc7e62`;
- the activated proof-registry SHA-256 remained
  `0647482bf52d189454b7e1099967b9dea9270a62627a9d43c2631248de75b189`;
- the registered bundle, temporary directory, and consumed marker were all
  absent; and
- free disk was 100,362,612,736 bytes, above the 2 GiB minimum.

## Result

The sole registered invocation persisted its 212-byte no-clobber consumed
marker and then attempted to establish the TLS connection for the exact
official checksum-manifest request. Python 3.12's default verified SSL context
could not build the local issuer chain and raised
`ssl.SSLCertVerificationError`, surfaced through `urllib.error.URLError`.

The failure occurred during the TLS handshake, before an HTTP response, header,
or body became available. Therefore:

- checksum-manifest response bodies read: 0;
- EDF requests: 0;
- EDF payload bytes transferred: 0;
- local EDF files created or opened: 0;
- payload bundle promoted: no;
- temporary acquisition directory retained: no; and
- consumed marker retained: yes.

No certificate bypass, alternate client, proxy, retry, rerun, repair, resume,
fallback, or substitution was attempted. The registered no-retry rule applies
to failure as well as success, so Stage S-A2 is consumed and permanently
parked. We will not retry it.

## Measurements

| Measurement | Observed | Registered cap or expectation |
|---|---:|---:|
| Registered invocations | 1 | exactly 1 maximum |
| TLS transport attempts | 1 | within one-shot invocation |
| Successful HTTP responses | 0 | checksum response required for success |
| Checksum response-body bytes | 0 | <= 1,048,576 |
| EDF requests / payload bytes | 0 / 0 | 6 / 15,498,816 only on complete success |
| Logical generated output | 212 bytes | <= 1,048,576 metadata |
| Pre-execution free disk | 100,362,612,736 bytes | >= 2,147,483,648 |
| External command wall time | 0.347787333 seconds | <= 300 seconds |
| Peak process-tree RSS | unavailable | <= 268,435,456 |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 | 1 / 1 / 1 |
| Retries / reruns | 0 / 0 | exactly 0 / 0 |
| End-to-end decoding latency measured | no | unavailable |

Peak RSS, application-visible response-header bytes, and allocator-level disk
peak were unavailable because the exception occurred before the executor could
return its bounded outcome. The only retained logical output is the known
canonical consumed marker; it was not opened or reproduced after failure.

## Zero Counters

Every EDF semantic, annotation, event, sample, channel, geometry, montage,
reference, sampling, task, target, label, epoch, trial, quality, cache, split,
feature, checkpoint, model, inference, training, parameter-update, prediction,
scoring, fresh-final, retained-source, language-model, stream, device,
hardware, release, and scientific-claim counter remained zero.

## Post-Result Verification

Sixteen focused activation/result checks pass. The complete dependency-light,
one-thread suite passes 5,913 tests with 212 expected skips in 229.911 seconds,
exactly nine passing tests above the 5,904-test pre-result baseline. Both new
Python test files pass current changed-file Ruff, compilation passes, all 461
registry JSON files parse, sidecar help remains available without a live
command, and Git diff hygiene passes.

A broad run of the latest unpinned `uvx ruff` reports 1,205 pre-existing
repository-wide findings in unrelated historical files. This result does not
rewrite that debt and does not mislabel it as a regression or a clean global
latest-Ruff pass. The pushed result commit must still pass the repository's
pinned CI Ruff job and both complete remote suites.

## Next Gate

There is no repair gate for this invocation. Do not reopen, retry, replace, or
delete its consumed marker or use another TLS client to complete the same
Stage S-A2 scope. The six-file source bundle does not exist, so the dependent
UG1 source-LOSO stage cannot proceed under this lane. Any future scientific
experiment must be a genuinely separate preregistered lane with a new data
identity and a new irreversible-evidence decision, not a disguised S-A2 retry.

## Claim Boundary

Engineering capability added: the proof-gated executor failed closed at a
verified TLS trust error, retained only its durable consumed marker, and
prevented partial or unverified EEG payload acquisition.

Scientific claim not established: no EDF byte, neural signal, target, model,
prediction, or score was produced, so this result establishes no EEG effect,
decoding performance, unseen-person generalization, movement intention,
motor-cortex origin, eye independence, language or thought decoding, live
latency, hardware result, or clinical utility.
