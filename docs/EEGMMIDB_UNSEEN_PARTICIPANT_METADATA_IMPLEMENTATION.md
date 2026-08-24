# EEGMMIDB-UG1 Stage M1 Metadata Client Implementation

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-M1`

Status: **Implementation ready; generated qualification not executed; exact
implementation commit must be remotely green first**

Machine implementation record:

- `registries/eegmmidb_unseen_participant_metadata_implementation.v0.json`

## Green Authority

Authorization decision `021bf8a1f2f12a8e7388a561535328cd0dc0dba2`
passed Base Python job `97385926125`, Optional Neuro Readers job
`97385926444`, and CI `32712235191` before this implementation began.

The implementation binds only Stage M1. It does not activate Stage M2 or
perform a live metadata request.

## Added Capability

The new isolated
`src/neurodecodekit/datasets/eegmmidb_unseen_participant_metadata.py` module
provides:

- an exact ordered allowlist for the 36 preregistered PhysioNet EEGMMIDB
  v1.0.0 EDF URLs inherited without modifying the proof-bound Stage G module;
- strict HTTPS host, path, query, fragment, port, and credential validation;
- `HEAD`-only `urllib` request construction with identity encoding;
- a certificate-verifying standard-library HTTPS opener with automatic
  redirects disabled;
- injected generated/mock transport for network-free qualification;
- direct status `200`, unchanged final URL, one canonical nonnegative
  `Content-Length`, and strict optional `ETag`, `Last-Modified`, and
  `Accept-Ranges` validation;
- zero application response-body reads and explicit body-byte refusals in
  generated fixtures;
- canonical target-free JSON inventory and human receipt serializers;
- one-thread, request, payload-size, metadata, output, wall-time, RSS, and free-
  disk caps; and
- atomic no-replace publication with collision refusal.

A new isolated metadata sidecar CLI exposes only `plan` and `qualify`. The
proof-bound Stage G sidecar remains byte-identical. There is deliberately no
`execute` command, so the present commit cannot initiate Stage M2.

## Qualification Design

The registered Stage M1 pass is a 20-case matrix:

1. complete optional validators;
2. all optional validators unavailable;
3. deterministic replay;
4. redirect refusal;
5. status refusal;
6. missing `Content-Length` refusal;
7. duplicate `Content-Length` refusal;
8. malformed `Content-Length` refusal;
9. malformed `ETag` refusal;
10. malformed `Last-Modified` refusal;
11. malformed `Accept-Ranges` refusal;
12. observed body-byte refusal;
13. request-order refusal;
14. missing-response refusal;
15. combined declared-byte-cap refusal;
16. output-collision refusal;
17. thread-environment refusal;
18. free-disk refusal;
19. peak-RSS refusal; and
20. wall-time refusal.

Unit tests exercise the same component contracts, but the one registered
aggregate qualification has not run. It may run only after this exact
implementation commit is pushed and both required CI jobs pass.

## Current Operation Ledger

```text
registered generated qualifications: 0
network requests:                    0
real URL or local data-path access:  0
response-body reads / bytes:         0 / 0
EDF content reads:                   0
payload download bytes:              0
targets / model / training / score:  0 / 0 / 0 / 0
release / claim upgrades:            0 / 0
```

## Boundaries

This implementation does not authorize or perform the one real metadata
invocation, a local real-data path operation, EDF content access, payload
acquisition, source/fresh/target stages, a model run, training, scoring,
release, or scientific claim upgrade. The live standard-library transport is
code under qualification, not an executed network surface.

## Next Gate

Run focused checks, commit, push, and require both CI jobs green for this exact
implementation. Then run the one registered 20-case generated/mock
qualification and record its measured aggregate result. Stage M2 remains
closed until that result and a separate proof-only closeout are remotely
green.

Engineering capability added: a strict, dependency-light, body-blind
metadata client can now be qualified without contacting PhysioNet or opening
an EDF.

Scientific claim not established: no real URL, EEG payload, target, model, or
score was accessed, so this implementation establishes no neural effect or
unseen-person generalization.
