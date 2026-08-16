# MARC2-VR4P Machine-Stable Private Recovery Result

Date: 2026-08-16

Lane: `MARC2-VR4P`

Status: **Consumed at the frozen VR2 adapter; the exact structural source was
read once, but no cohort was frozen and no retry or rerun is open**

Machine result:
`registries/marc2_machine_stable_private_recovery_failure_result.v0.json`

## Green Execution Proof

Exact implementation commit
`24f7379301b03c8f5eff796afb3398b11e58ece9` passed Base Python job
`95223010696`, Optional Neuro Readers job `95223010631`, and CI
`31970865212`. The tracked HEAD remained exact and clean before invocation;
the unrelated untracked tracker-inspection sidecar was not staged, opened,
modified, or deleted.

The command was invoked once with all five numerical-thread variables fixed to
one and only the four registered proof identifiers. There was no path, root,
source, output, cleanup, threshold, wait, retry, dataset, participant, or model
override.

## Final Route

The one invocation returned exactly:

```text
MARC2MSP-F07: VR2 structural adapter refused
```

The route is aggregate-safe. The underlying VR2 predicate and any intermediate
candidate selection were deliberately not emitted or retained, so they are
unavailable and must not be inferred after target-free private access.

## Proven State-Machine Boundary

The route proves the following registered operations completed in order:

1. exact implementation and remote-green proof validation;
2. no-follow identity, mode, owner, size, SHA-256, canonical JSON, semantic,
   and expiry validation of the 4,551-byte old readiness certificate;
3. one unlink of only that exact expired certificate;
4. one fresh readiness invocation that reached `ready=true`, wrote a new
   mode-`0600` certificate, and passed the pre-marker thread/RSS/disk recheck;
5. no-follow preflight of the exact mode-`0600`, 418,755-byte source;
6. creation of the new fixed output root and one mode-`0600` consumed marker;
7. one immediately following source content open, exact byte read, registered
   SHA-256 match, and strict duplicate-key-controlled JSON parse; and
8. one call to the frozen VR2 adapter, which refused before returning a valid
   adapted selection.

The adapter refusal occurred before cohort-invariant acceptance, private
selection-manifest serialization, aggregate-report creation, or a real cohort
freeze. No archive member was opened and the selected 8,105,207,776-byte value
was never allocated or read.

## Measured Boundary

The externally observed invocation wall time was approximately
`220.675729043` seconds, below the registered 650-second cap. Internal runtime,
peak RSS, exact readiness sample count, exact fresh-certificate bytes, exact
marker bytes, retained output bytes, load samples, and free-disk samples were
not emitted after refusal and are unavailable. The result recorder did not
open the new certificate, marker, output root, or private source to reconstruct
them after the fact.

Exactly 4,551 old-certificate bytes and 418,755 target-free structural bytes
were read. Network bytes, archive-member bytes, signal samples, events,
channels, geometry, targets, labels, derivatives, model fits, predictions,
freezes, scores, providers, hardware, releases, and claim upgrades were all
zero.

## Disposition

`MARC2-VR4P` is consumed. There is no retry, rerun, resume, repair, fallback,
alternate source, adapter relaxation, or post-result selection change. Do not
open, inspect, hash, parse, rename, delete, overwrite, or reuse the fresh
certificate, consumed output root, marker, or retained private source under
this lane.

No real cohort identity is available, so `MARC2-FW2` and `MARC2-CIL1` remain
ineligible. The next safe work is a separately named artifact-only mismatch
localization using committed contracts, code, generated fixtures, and this
aggregate route only. Any new private read or structural recovery requires a
new immutable packet and fresh Tier C decision; archive payload access,
training, prediction freezing, target delivery, and scoring remain later
separate boundaries.

Engineering capability added: the exact remotely green executor safely
crossed machine readiness, consumed the attempt before one integrity-checked
structural open, and failed closed when the frozen VR2 adapter rejected the
real source.

Scientific claim not established: no neural payload, target, prediction, or
score was accessed, so this result establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
