# EEGMMIDB-UG1 Stage M Metadata Authorization Decision

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-M`

Status: **Packet-bound short-form authorization recorded; ineffective until
this exact decision is committed, pushed, and both required CI jobs are green**

Machine decision:

- `registries/eegmmidb_unseen_participant_metadata_authorization_decision.v0.json`

## Maintainer Decision

After Codex identified `EEGMMIDB-UG1-M` as the sole active Tier C packet and
reported its exact request commit, proof-closeout commit, CI evidence,
two-stage scope, and fresh-decision boundary, the maintainer's next message
was exactly:

```text
continue
```

The machine decision preserves those actual eight UTF-8 bytes and their
SHA-256. Under the approved Research Autonomy Charter short-form rule, this
unambiguous continuation binds only the unchanged, remotely green Stage M
packet by reference. It does not fabricate a long-form user utterance or
expand the registered scope.

## Green Packet Bound By This Decision

```text
request commit:       e2647d609a99997ac417dac5d8efb2dad61863a0
request CI:           32709110804
request Base job:     97376524550
request Optional job: 97376524804
proof commit:         e9c11da94730e790aace3acc818e029abcbdc165
proof CI:             32710175884
proof Base job:       97379680508
proof Optional job:   97379680751
```

Both required jobs passed for both commits. The packet and proof artifact set
contains six unchanged files totaling 29,320 bytes. The unrelated untracked
tracker inspection NDJSON remains untouched.

## Delayed Effect

This decision does not become effective merely because these files exist.
Before Stage M1 implementation or qualification, this exact decision must
pass local checks, be committed and pushed, and pass both required remote CI
jobs.

Recording the decision performs zero generated qualification, network request,
URL or local-path operation, metadata response, response-body read, EDF access,
payload download, target delivery, model operation, scoring, release, or claim
upgrade.

## Authorized Sequence After Green Decision

### Stage M1: generated/mock metadata client

After this decision is remotely green, one additive dependency-light client
may be implemented and qualified using only generated local fixtures and
mocked HTTP responses.

The client must enforce the exact ordered 36-URL allowlist, HTTPS and
`physionet.org`, `HEAD` as the only method, direct status `200`, zero redirects,
zero retries, zero fallback, zero response-body reads, required exact
nonnegative `Content-Length`, strict optional validator syntax, canonical
bounded serializers, atomic no-clobber output, and post-publication resource
checks.

Qualification may contact no network, inspect no real URL, open no local data
path, and reuse no consumed invocation. It must cover valid mocked responses
and adversarial redirects, aliases, duplicates, missing or conflicting sizes,
malformed validators, body bytes, output collisions, resource-cap breaches,
and replay attempts.

The exact implementation, generated result, and a separate proof-only
closeout must be committed, pushed, and pass both remote jobs before Stage M2.

### Stage M2: one real body-blind metadata invocation

Only after the exact Stage M1 implementation and proof closeout are remotely
green may one sequential invocation issue exactly one HTTPS `HEAD` request to
each of the 36 preregistered EEGMMIDB v1.0.0 EDF URLs in frozen order.

It may accept only direct `200` responses and must read zero response-body
bytes. `Content-Length` is mandatory. `ETag`, `Last-Modified`, and
`Accept-Ranges` may be recorded only when directly returned and syntactically
valid; absence remains explicit. The combined declared size must not exceed
268,435,456 bytes. Success requires all 36 distinct paths and one canonical
inventory plus one human receipt under 1 MiB combined.

Any mismatch, timeout, redirect, body byte, missing size, cap breach, extra
request, or output collision refuses and consumes the sole invocation. There
is no retry, rerun, substitution, repair, partial success, `GET`, or `Range`
fallback.

## Resources

```text
CPU threads / workers / jobs: <= 1 / <= 1 / <= 1
real metadata requests:       exactly 36 on a complete invocation
real wall time:               <= 300 seconds
peak process-tree RSS:        <= 256 MiB
application-visible metadata: <= 2 MiB
generated output:             <= 1 MiB
response-body/payload bytes:  0
incremental disk:             <= 1 MiB
minimum free disk:            >= 2 GiB
retry / rerun:                0 / 0
```

## Explicitly Not Authorized

This decision does not authorize Stage M1 before its own remote green proof;
Stage M2 before exact Stage M1 and proof-only closeout are remotely green;
`GET`, `Range`, redirects, retries, authentication, or provider tools; an EDF
body, header, annotation, event channel, signal, channel, geometry, sampling,
task, target, label, epoch, or trial read; `.event` sidecars; any local real-
data path operation; acquisition; source, fresh, or target stage; cache, split,
feature, derivative, checkpoint, prediction, inference, training, scoring, or
selection; another participant, run, file, or dataset; language models, RW3,
streams, devices, or hardware; release or publication; or any scientific,
decoding, neural, unseen-person, real-time, portable, home-use, assistive, or
clinical claim upgrade.

## Next Gate

Commit, push, and green this exact decision. Then implement and generated-
qualify Stage M1. Only after that exact implementation and a separate proof-
only closeout are remotely green may Stage M2 run once.

Engineering capability authorized after green decision: one strictly bounded,
body-blind metadata identity client may be qualified on mocks and later freeze
the exact remote sizes and available validators for the 36 registered files.

Scientific claim not established: this decision is authorization, not neural
data or a model result, and establishes no EEG effect, decoding performance,
or unseen-person generalization.
