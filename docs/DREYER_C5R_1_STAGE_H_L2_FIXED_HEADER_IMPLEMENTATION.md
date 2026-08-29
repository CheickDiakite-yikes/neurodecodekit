# DREYER-C5R-1 H-L2 Fixed-Header Implementation

Date: 2026-08-29

Status: **implementation and generated qualification complete; exact commit,
push, and remote-green proof required before activation**

Machine record:

- `registries/dreyer_c5r_1_stage_h_l2_fixed_header_implementation.v0.json`

Implementation ID: `DREYER-C5R-1-HL2-I0`

## What Was Built

This additive standard-library adapter implements the one-file H-L2 transaction
authorized by decision `DREYER-C5R-1-HL2-A0-D0`. It freezes the remotely green
decision and recovery artifacts, requires a later exact activation record, and
exposes three CLI surfaces:

1. `plan` inspects the bounded contract without touching private state;
2. `qualify-generated` exercises generated fixtures only; and
3. `execute` remains fail-closed until a later activation hash, commit, CI run,
   and both required job IDs are supplied and verified.

The transaction writes a durable consumed marker before constructing an opener
or request. It enforces one direct proxy-free HTTPS GET, verified TLS, identity
encoding, no redirect, exact final URL and content length, bounded streaming,
EOF, exact payload SHA-256, one fixed-header semantic parse, strict sensor and
sampling contracts, fixed-header-to-payload geometry, no-replace promotion,
response closure, invocation-owned cleanup, and bounded aggregate publication.

Only an exact H1 outcome may retain the private Git-ignored EDF. Any eligible
post-marker failure publishes an aggregate H0 and removes invocation-owned
unaccepted payload. Publication failure also removes an accepted payload. The
adapter never exposes annotations, signal samples, targets, labels, trials,
models, predictions, scoring, provider calls, devices, or claim upgrades.

## Generated Qualification

The complete generated matrix ran through temporary isolated workspaces under
one-thread environment variables. Two H1 replays produced the same stable
report digest. The remaining 31 attempts exercised every registered refusal
surface, including preconsumption proof/resource failures, transport and
payload drift, fixed-header and geometry failures, resource caps, teardown,
preexisting private-payload refusal, publication races, and consumed-rerun
refusal.

```text
transaction cases:                           32
generated attempts:                          33
matching H1 replays:                          2
aggregate H0 outcomes:                       21
raised fail-closed refusals:                  10
total refusal observations:                  31
stable H1 replay SHA-256:                     76d12f5a8142520d99716c72149ef42d5048034e431719373ba234782eb7362b
qualification runtime:                        0.599492667010054 seconds
peak process RSS:                             39,141,376 bytes
generated logical bytes across attempts:      151,858 bytes
maximum single-attempt logical bytes:          45,675 bytes
retained generated payload bytes:                   0 bytes
network bytes:                                      0 bytes
real/private operations:                            0
model runs / training runs:                         0 / 0
target or label reads:                              0
scientific claim established:                       false
```

Focused implementation tests passed 8/8 in 1.300 seconds. Ruff passed for the
module, CLI, and focused tests. The generated run is interface and transaction
qualification only; it is not a real-data attempt and has no scientific value.

## Next Barrier

This exact implementation must be committed, pushed to GitHub `main`, and pass
Base Python and Optional Neuro Readers. Only afterward may the no-authority
activation record bind this exact green implementation. That activation must
also become remotely green before the already authorized sole real invocation.
Until then, the activation, consumed marker, network request, real EDF, and
fixed-header read remain closed.

Engineering capability added: a bounded activation-locked adapter can now
prove the complete one-file fixed-header transaction and refusal behavior with
generated fixtures.

Scientific claim not established: no real EEG was accessed, so this milestone
establishes no neural information, decoding, unseen-person generalization,
peripheral-adjusted effect, live operation, hardware value, or clinical value.
