# MARC2-FW1C Live Selection Recovery Result

Date: 2026-08-16

Lane: `MARC2-FW1C`

Route: `MARC2FWC-F02`

Status: **Consumed strict source-identity failure; no retry, rerun, resume,
repair, or selection result is available**

Machine result:
`registries/marc2_live_selection_recovery_failure_result.v0.json`

## Green Proof Before Access

Exact Stage 1 implementation:

```text
commit:                  7b924bee1f10217bccf911ccb4e380485226d50c
CI run:                  31930051249
Base Python job:         95123374369
Optional Neuro job:     95123374211
native registry SHA:     dcd95616ad65b1b44b13f3116e6a63ea77d958705f4e9bcfad12d8b74a841edc
FW1B certificate SHA:    06668731cdb507373053bce5fe652366591f7fb83a7a0bd48f4fcd82f2610e82
```

Both remote jobs passed before the only registered Stage 2 invocation. The
executor validated the green packet-bound decision, exact FW1B certificate,
native FW1C registry, exact clean HEAD, decision ancestry, one-thread machine
gate, new output identity, and registered no-follow source preflight in their
frozen order.

## What Happened

The sole invocation performed exactly one bounded no-follow content open of
the registered 418,755-byte structural manifest. Size, owner/mode, open/fstat
identity, full SHA-256, strict UTF-8 JSON parsing, and the registered byte count
passed because execution reached the frozen `target_free_prefix_selection`
stage.

The strict live source-identity validator then refused with:

```text
MARC2FWC-F02: live source identity differs
```

The aggregate record intentionally does not retain which private field or
shape predicate differed. No private-body comparison, field probe, output-root
listing, sibling inspection, or retry followed. This result therefore supports
only the aggregate conclusion that the committed strict live identity did not
match the exact registered source object.

## Measured Execution

```text
input opens / reads:               1 / 1
input bytes:                       418,755
SHA-256 passes / strict parses:    1 / 1
runtime:                           0.09137429200200131 seconds
peak RSS:                          25,280,512 bytes
pre-consumption RSS:               23,166,976 bytes
free disk before consumption:      167,501,524,992 bytes
logical CPUs:                      12
one-minute load:                   5.2421875
load per logical CPU:              0.4368489583333333
CPU threads / workers / jobs:      1 / 1 / 1
combined output bytes:             6,944
aggregate report bytes:            6,540
aggregate report SHA-256:          f3c9d1d8a10de32975824422a809f8d408e0924f65916bf3b92ed513e29af8fc
end-to-end latency measured:       no
producer causal:                   not applicable, metadata only
```

The generated 8 GiB reservation ceiling was not allocated or acquired.

## Access Ledger

```text
registered parent component checks:     3
registered final lstats:                 2
content opens / reads:                   1 / 1
private bytes / hashes / parses:         418,755 / 1 / 1
consumed markers / aggregate reports:    1 / 1
private selection manifests:             0
selected participants / members:         0 / 0
network requests / bytes:                0 / 0
archive local-header/member reads:        0
signal samples:                           0
event/target/label/quality/channel reads: 0
derivative rows:                          0
training fits / model predictions:        0 / 0
prediction freezes/deliveries/scores:     0
provider/LLM calls / hardware operations: 0 / 0
old consumed-root operations:             0
retries/reruns/resumes:                    0
scientific claim upgrades:                0
```

No selected subject identity, member name, offset, CRC, raw source body,
private row, retained path, private output path, or failure-field detail is
published.

## Verification

The post-result closeout passed:

```text
focused recovery tests:            56
dependency-light tests:            3,226 passed / 204 skipped
optional-neuro A-M tests:           2,784 passed / 28 skipped
optional-neuro N-Z tests:           513 passed / 7 skipped
optional-neuro combined:            3,297 passed / 35 skipped
registry JSON files validated:      219
Ruff:                               passed
compileall:                         passed
git diff --check:                   passed
```

Both complete suites ran with one numerical thread. No verification step
reopened the private source, consumed marker, aggregate report, or either
output root.

## Gate Verdict

Passed safety gates:

- packet-bound green decision and frozen artifact identity;
- exact shared FW1B certificate and native FW1C registry;
- all 32 proof, 40 selector, and 18 wrapper generated refusals;
- one no-follow private open only;
- target/quality/outcome-free selection design;
- private/aggregate output separation;
- zero archive-member, neural, target, model, prediction, or score access;
- runtime, RSS, disk, output, and one-thread caps; and
- preserved claim boundary.

Failed completion gates:

- exact live source schema/identity;
- deterministic completed selection identity; and
- maximal contiguous prefix under the 8 GiB reservation ceiling.

There is no selection result to carry into `MARC2-FW2`.

## Disposition

`MARC2-FW1C` is consumed. Do not retry, rerun, resume, repair, amend, substitute
another path, inspect the private source, inspect the consumed marker, list the
output root, or reopen the aggregate report for tuning.

The next safe work is a separately named artifact-only source-schema lineage
audit using committed producer code, contracts, and aggregate records only. It
may determine whether the prospective schema was specified incorrectly, but it
cannot identify a private field value or authorize another read. Any future
live recovery requires a fresh generated contract, remotely green
implementation, all-false Tier C request, and packet-bound decision.

Archive members, payload acquisition, EEG, targets, models, scores,
`MARC2-FW2`, provider calls, hardware, release, and scientific claim upgrades
remain closed.

## Claim Boundary

Engineering capability added: the remotely qualified wrapper performed one
bounded structural-manifest validation and failed closed with an aggregate,
resource-measured, privacy-preserving consumed result.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this metadata identity failure establishes no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
