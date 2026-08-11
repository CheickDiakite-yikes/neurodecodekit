# IACKD-M1A Public Snapshot Audit Result

Date: 2026-08-11

Status: **one registered request consumed; parked at
`IACKDMP-F05-snapshot-semantic-canonicalization-failure`; no retry or rerun**

Machine result:
`registries/iackd_snapshot_identity_public_result.v0.json`

Private consumed marker:
`.codex_work/iackd_snapshot_identity/public_audit_v0/execution_consumed.v0.json`

## Green Preconditions

The registered request ran only after both ordered implementation gates were
green:

```text
packet-bound decision commit:  4165c24cdad9768c7e36b5e4893602d02434be50
decision CI / Base / Optional:  31485359989 / 93759373384 / 93759373333
wrapper commit:                406bff8bbcfce7b635b0ee4d95096a24288a13e2
wrapper CI / Base / Optional:   31487183289 / 93765145883 / 93765145952
implementation registry hash:  64b53e0cfa3c55b71db7a0bb177980e1ace3adc050104d33633f705e86f3a5a4
```

The live machine gate also passed before the private marker:

```text
free disk:                     25,554,214,912 bytes
logical CPUs:                  12
one-minute load:               5.4765625
load per logical CPU:          0.4563802083333333
peak RSS before consumption:   below the 256 MiB cap
thread / worker / job values:  1 / 1 / 1
```

## What Happened

The executor wrote its 374-byte private consumed marker, sent the one frozen
355-byte POST, opened one response, read its 595,082-byte body once, and
computed one SHA-256. The transport stage completed and the same in-memory body
entered the strict green canonicalizer.

The canonicalizer then refused because the response root's exact field set was
not `{data}`. This is the only supported diagnosis. The raw response was not
persisted, so the additional top-level field or fields are deliberately
unknown and must not be guessed from this run.

The wrapper emitted a 4,352-byte aggregate failure result and stopped. It did
not emit the 1,340-row private selected manifest because no semantic identity
gate completed.

```text
route:                              IACKDMP-F05
GraphQL requests / responses:       1 / 1
response opens / reads / hashes:    1 / 1 / 1
request / response / network bytes: 355 / 595,082 / 595,437
semantic compatibility passes:     0
private consumed markers:           1
private selected manifests:         0
aggregate public reports:           1
report / marker / total bytes:      4,352 / 374 / 4,726
runtime at final serialization:     0.6231084170285612 sec
external process wall time:         0.84 sec
peak RSS at final serialization:    39,763,968 bytes
external maximum RSS:               40,353,792 bytes
S3 payload requests / bytes:        0 / 0
local IACKD / old-root operations:   0 / 0
signal / event / target reads:      0 / 0 / 0
training / inference / scores:      0 / 0 / 0
retries / reruns:                   0 / 0
```

Result SHA-256:
`79273525d3c598a97399401cfe16b1ba7e437e2ba41c53a53219df3f48b989fe`

Private marker SHA-256:
`55df71f9e6908fc38cb2e0aba538db6199879f3d3c8189524cd71c11d553b0d8`

## Important Missing Provenance

The executor computed the response SHA-256, as shown by the one hash counter,
but its aggregate failure serializer did not retain that value. The real
framing profile and Content-Length are also absent from the failure report.
Because the raw body and headers were correctly discarded, these values are
now unavailable. This means the full registered provenance gate did not pass;
the result cannot be repaired after the fact.

The stage boundary supports only the limited inference that HTTP status, final
URL, redirect, content-encoding, framing, one-read, length, and body-cap checks
completed before semantic refusal. It does not reveal the unknown root field.

## CLI Reporting Defect

After the aggregate result and marker were safely written, the module's CLI
exception path passed `sort_keys=True` to `print()` instead of `json.dumps()`.
That raised a local `TypeError` while attempting to echo the already-recorded
refusal. It did not make another request, alter the result, or bypass any
boundary. The consumed executor is preserved exactly; no post-result patch or
rerun is permitted in this lane.

## Verification

```text
focused IACKD snapshot tests:  104 passed
complete base suite:           2,139 passed / 204 skipped
complete optional suite:       2,210 passed / 35 skipped
Ruff:                          0.15.20 passed
compileall:                    passed
registry JSON validation:      157 passed
git diff --check:              passed
```

The complete suites are post-result verification only. They made no public
request and did not open the private marker or any IACKD payload.

## Verdict

IACKD-M1A is consumed and parked. It did not establish current public snapshot
compatibility. Its useful result is narrower: the bounded one-shot wrapper
failed closed at a precisely localized response-envelope boundary and did not
cascade into any payload, neural, target, model, or scoring operation.

Any follow-on must be a separately named prospective metadata-envelope design
with a new immutable contract and Tier C decision. It may not reuse this
consumed marker, request, response, or executor invocation.

## Claim Boundary

Engineering capability added: one remotely green, machine-gated wrapper made
one bounded public metadata request and localized an incompatible response
envelope without exposing or acquiring payload data.

Scientific claim not established: no neural payload was read and no model was
run, so this result establishes no neural effect, decoding accuracy,
brain-specific origin, generalization, language or thought decoding, real-time
operation, portable hardware, home use, assistive benefit, or clinical utility.
