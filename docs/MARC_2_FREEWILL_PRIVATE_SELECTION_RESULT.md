# MARC2-FW1A Private Selection Result

Date: 2026-08-13

Status: **Consumed failure at `MARC2FWS-F00`; no retained private path was
checked or opened, and no retry or rerun is available**

Registry:
`registries/marc2_freewill_private_selection_failure_result.v0.json`

## Green Implementation Proof

Exact wrapper commit `d9a38530974ceab8e7f79b1f7a79b8fff57069e9`
passed Base Python job `94661484721` and Optional Neuro Readers job
`94661484713` in CI `31765857313` before the one registered invocation.

The implementation registry SHA-256 supplied to the executor was:

```text
68bcfba4d1ceca2612756118c6087046b3ac8e469a637d43c6f5d6ebe7966895
```

## Pre-Invocation Machine Snapshot

The tracked worktree was clean and the exact registered output root was
absent. A separate non-private machine snapshot observed:

```text
free disk bytes:                  40,852,090,880
logical CPUs:                    12
one-minute load:                 6.49
load per logical CPU:            0.5408333333333334
thread / worker / numerical job: 1 / 1 / 1
```

This snapshot was outside the executor. It is not substituted for a passed
in-executor machine gate because proof validation refused first.

## Registered Outcome

The executor exited with code `2` after 8.5260585 external wall seconds and
emitted only:

```text
MARC2FWS-F00: implementation record differs
```

Execution order stopped inside `verify_green_implementation` while validating
the committed implementation registry. It did not reach the machine gate,
output-parent creation, retained source path, source preflight, consumed
marker, content open, read, hash, parse, selection, or output writers.

Consequently:

```text
registered private path component checks: 0
registered private final lstats:           0
private content opens / bytes:             0 / 0
private hashes / parses:                    0 / 0
real participant / member selections:      0 / 0
consumed markers:                           0
private selection manifests:               0
aggregate execution reports:               0
network / archive member bytes:             0 / 0
signal / target / model / score operations: 0 / 0 / 0 / 0
generated output bytes:                     0
```

Peak RSS and in-executor runtime are unavailable because no execution report
was created before proof refusal. The registered output root remains absent.

## Artifact-Only Diagnosis

After the refusal, an artifact-only comparison read only committed source and
registry files. It did not call `execute`, inspect an output root, or touch the
retained manifest.

The implementation loader requires:

```json
"lane_id": "MARC2-FW1A"
```

The committed implementation registry has no top-level `lane_id`; its observed
value is absent. Its schema name, version, status, green-decision proof,
qualification counts, ordered mutation keys, unconsumed pre-execution state,
and zero access counters otherwise match the validator.

This explains the aggregate `F00` route. It does not justify changing the
consumed implementation or repeating the invocation.

## Verification

Twelve focused result tests bind the route, green implementation proof,
pre-invocation snapshot, zero-access counters, exact artifact-only diagnosis,
consumed disposition, unavailable measurements, and claim boundary.

The complete dependency-light suite passes 3,083 tests with 204 expected
optional skips. The complete optional-neuro inventory passes 3,154 tests with
35 skips across fresh A-M and N-Z processes: 2,641 tests with 28 skips and 513
tests with seven skips. The A-M process used sandbox permission only for an
existing local multiprocessing forkserver test; it made no network or real-
data access.

Ruff, compilation, strict JSON parsing, artifact hashes, registry JSON, and
diff hygiene pass locally. Remote CI remains pending for this closeout commit.

## Disposition

`MARC2-FW1A` is consumed. Do not:

- add the missing field to the consumed implementation and rerun it;
- create its output root manually;
- stat, open, hash, parse, or inspect the retained private manifest;
- use a new path, fallback, repair, resume, or old output;
- request an archive local header or member payload; or
- enter `MARC2-FW2`, neural analysis, targets, models, scoring, or language
  work from this result.

A recovery must be separately named and prospective. It should first freeze a
machine-checkable implementation-record schema, prove that schema through a
generated invocation with the exact same verifier entry point, and then use a
new all-false Tier C packet for any later private-manifest access.

## Claim Boundary

Engineering capability demonstrated: the remote-green executor failed closed
on a committed proof-record mismatch before any private source or payload
access.

Scientific claim not established: no human EEG, event, target, prediction, or
score was accessed, so this result establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
