# COMM-L0 Generated Source Identity Implementation

Date: 2026-08-26

Status: **Generated-only implementation prepared; official qualification not
yet consumed; real metadata and payload access remain unauthorized**

Registration commit: `f4a30e4323834dbd53f5c3cc4abee52829ec016a`

Registration CI: `33035992877`

Base Python job: `98398680307`

Optional Neuro Readers job: `98398680155`

Machine record:
`registries/communication_eeg_source_identity_implementation.v0.json`

## Added Capability

`src/neurodecodekit/datasets/communication_eeg_source_identity.py` is an
additive, standard-library generated-response canonicalizer. It:

- binds the exact remotely green COMM-L0 registration;
- accepts generated response bytes directly and exposes no network or real
  dataset execution command;
- enforces strict UTF-8 JSON, exact GraphQL shapes, snapshot identity,
  content-addressed rows, safe NFC POSIX paths, canonical sizes, and exact
  versioned S3 keys;
- discovers rather than prefits tree counts and byte totals;
- requires exactly `sub-01` through `sub-10`, exactly three complete raw
  sessions each, and a common session-label set;
- chooses the lexicographically first common session for every participant,
  with one BDF and all direct-child companions from each selected EEG
  directory;
- rejects derivatives, processed arrays in raw-session directories, missing or
  multiple BDFs, missing companions, participant dropping, divergent sessions,
  and selected payload above 10 GiB;
- emits aggregate hashes, counts, bytes, metadata, warnings, counters, and
  claim boundaries without paths, URLs, version IDs, or row records; and
- writes a qualification result through a no-clobber hard-link publication
  after runtime, RSS, input, and output caps pass.

The module CLI has exactly `plan`, `qualify`, and `inspect`. There is no
`execute`, network, payload, or real-path mode.

## Generated Fixture Matrix

The deterministic success fixture contains ten synthetic participants, three
synthetic sessions each, one generated BDF metadata row and three generated
companion rows per session, plus a generated dataset description. It copies no
real metadata body, path inventory, participant attribute, signal, event,
target, label, prediction, or outcome.

The official qualification, once this exact implementation is remotely green,
will run two source-order replays and 20 adversarial refusals covering:

- snapshot and DOI drift;
- GraphQL errors, unknown fields, duplicate JSON keys, and invalid UTF-8;
- duplicate or unsafe paths, invalid URLs, noncanonical sizes, and directories;
- missing or extra participants and missing or divergent sessions;
- missing, multiple, or processed raw-session files;
- derivative inclusion and the 10 GiB selection cap; and
- output, thread, runtime, RSS, and privacy boundaries.

Unit tests exercise the canonicalizer and refusals but do not call the official
qualification function, create its result, or consume the registered run.

## Authority Boundary

This implementation reads only its tracked contract and generated test bytes.
It has made zero OpenNeuro request, metadata response read, payload request,
private path read, BDF header or sample read, event/target read, model run,
prediction, score, provider call, stream operation, device operation, release,
or claim upgrade.

`DREYER-C5R-1-HL` remains the sole active Tier C packet. The maintainer's 20
GiB total research-storage allowance does not authorize a dataset request and
does not increase the selected raw-data cap above 10 GiB.

## Local Verification

All 32 focused registration, canonicalizer, implementation, CLI-surface, and
hash-binding tests passed. Ruff, compilation, 509 registry JSON parses, CLI
help/plan, and diff hygiene passed.

The complete local suite reached 6,282 tests with 239 expected skips but took
1,316.194 seconds under elevated machine load. One unrelated historical MARC2
generated qualification crossed its frozen wall-time resource cap. That exact
test then passed alone in 15.322 seconds, and the COMM-L0 focused suite passed
again. No cap, code, or historical test was changed. Remote Base Python and
Optional Neuro Readers CI remain the clean implementation gate.

## Next Gate

1. Commit and push this exact implementation, tests, and record.
2. Require Base Python and Optional Neuro Readers CI to pass.
3. Only then run the one generated COMM-L0 qualification and record its exact
   aggregate result.
4. Do not query OpenNeuro or prepare a payload request in the implementation
   milestone.

## Claim Boundary

Engineering capability added: a generated-only canonicalizer can enforce the
future source identity, all-participant raw-session selection, storage, and
privacy contracts without a network or real-data surface.

Scientific claim not established: no real metadata, EEG, event, target,
model, prediction, score, communication decoding, unseen-person effect,
peripheral-adjusted effect, replication, or live result is established.
