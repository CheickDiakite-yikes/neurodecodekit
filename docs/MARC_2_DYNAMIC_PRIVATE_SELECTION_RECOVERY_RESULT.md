# MARC2-VR7P Dynamic Private Selection Recovery Result

Date: 2026-08-16

Lane: `MARC2-VR7P`

Status: **Consumed after one integrity-checked structural read; VR6 preserved
an upstream-validation refusal, no cohort was frozen, and no retry or rerun is
open**

Machine result:
`registries/marc2_dynamic_private_selection_recovery_failure_result.v0.json`

## Green Execution Proof

Exact implementation commit
`154852c58af080904087a2e4cef71991dcb6179d` passed Base Python job
`95252133987`, Optional Neuro Readers job `95252133958`, and CI
`31982672176` before execution.

The initial aggregate result record was then committed as
`ae75423ce9e60c08599ba31fc40f3a6ea584d70e`. It passed Base Python job
`95253771315`, Optional Neuro Readers job `95253771324`, and CI
`31983281390`. That proof validates the committed failure record and full test
suites; it is not a second execution or private reinspection.

The command was invoked once with all five numerical-thread variables fixed to
one and only the four registered proof identifiers. It exposed no path, root,
source, output, cleanup, threshold, retry, dataset, participant, or model
override. The unrelated untracked tracker-inspection sidecar was not staged,
opened, modified, or deleted.

## Final Route

The one invocation emitted only this aggregate-safe refusal:

```text
MARC2VR7P-F07: dynamic live selection refused
upstream VR6 route: MARC2VR6-F02
```

Committed VR6 code defines `MARC2VR6-F02` as its upstream VR2-validation
branch. The nested VR2 route, failed predicate, private value, and any
intermediate candidate selection were deliberately not emitted or retained.
They are unavailable and must not be inferred through post-hoc private
inspection.

## Proven State-Machine Boundary

Because the refusal occurred inside the one VR6 call after the consumed marker,
the registered sequence proves these operations completed in order:

1. exact implementation, clean tracked HEAD, green CI, decision ancestry, and
   shared proof-record validation;
2. one fresh machine-readiness invocation that reached `ready=true`, wrote one
   new mode-`0600` certificate, and passed the thread/RSS/disk recheck;
3. no-follow type, owner, mode, and exact 418,755-byte source preflight;
4. creation of the new fixed output root and one mode-`0600` consumed marker;
5. one immediately following source content open, exact byte read, registered
   SHA-256 match, and strict duplicate-key-controlled JSON parse;
6. one call to the frozen VR6 adapter; and
7. one internal call to VR2 validation, which refused before VR6 returned a
   selection.

The refusal preceded cohort-invariant acceptance, private selection-manifest
serialization, aggregate-report creation, or a real cohort freeze. No archive
member or neural payload was opened.

## Measured Boundary

The command was observed running for at least `60.00228025` seconds and
completed below the registered 650-second cap. Exact external wall time,
internal runtime, peak RSS, readiness sample count, certificate bytes, marker
bytes, retained output bytes, load values, disk values, and logical CPU count
were not emitted after refusal and are unavailable. The result recorder did
not stat, open, hash, parse, rename, delete, or reuse the new readiness path,
output root, marker, or private source to reconstruct them.

Exactly 418,755 target-free structural bytes were read once. Network bytes,
archive-member bytes, signal samples, events, channels, geometry, targets,
labels, derivatives, model fits, predictions, freezes, scores, providers,
hardware operations, releases, and claim upgrades were zero.

## Disposition

`MARC2-VR7P` is consumed. There is no retry, rerun, resume, repair, fallback,
alternate source, validator relaxation, or post-result selection change. Do
not open, inspect, hash, parse, rename, delete, overwrite, or reuse the fresh
certificate, consumed output root, marker, or retained source under this lane.

No real cohort identity is available, so `MARC2-FW2` and `MARC2-CIL1` remain
ineligible. The next safe work is a separately named artifact-only analysis of
the committed VR6-to-VR2 route boundary and generated fixtures. Any additional
private read requires a new immutable packet and fresh Tier C decision;
archive-payload access, training, prediction freezing, target delivery, and
scoring remain later separate gates.

Engineering capability added: the remotely green wrapper safely crossed
machine readiness, consumed the attempt before one integrity-checked
structural open, preserved the allowlisted VR6 failure class, and failed
closed when upstream validation rejected the source.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this result establishes no neural effect, decoding
accuracy, language decoding, live decoding, or thought-to-text capability.
