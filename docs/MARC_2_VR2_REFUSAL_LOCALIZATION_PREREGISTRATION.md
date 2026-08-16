# MARC2-VR5A VR2 Refusal Localization Preregistration

Date: 2026-08-16

Lane: `MARC2-VR5A`

Status: **Frozen artifact-only contract; implementation pending**

Contract:
`registries/marc2_vr2_refusal_localization_contract.v0.json`

## Why This Lane Exists

The sole `MARC2-VR4P` structural execution reached the frozen VR2 adapter and
stopped at outer route `MARC2MSP-F07`. VR2 already has eight aggregate-safe
refusal routes, but the wrapper caught the exception and retained only the
generic text `VR2 structural adapter refused`. The exact nested route and
predicate are therefore unavailable, and the consumed private source cannot
be reopened to reconstruct them.

The next safe step is not another private attempt. It is a fixed artifact-only
audit of the exact committed producer, VR2 adapter, selection code, contracts,
generated results, prior localizations, wrapper, and consumed aggregate result.

## Frozen Questions

The audit must answer five narrow engineering questions:

1. Did VR4P preserve or discard VR2's aggregate-safe nested route?
2. Which VR2 routes are actually reachable from the strict-JSON call path
   after the same contracts have already loaded successfully?
3. Does VR2 validate general live-selection invariants, or does it require a
   real source to reproduce exact generated-fixture outputs?
4. Are rows produced for a live source labeled with live or generated source
   semantics?
5. What is the smallest prospective repair that would make one later
   structural attempt both diagnosable and live-compatible?

## Known Boundary

The audit may read only eleven hash-bound committed files totaling less than
one MiB plus this contract. It may parse Python with the standard-library AST
and JSON with duplicate-key rejection. It has no path, URL, private root,
execute, archive, neural, target, model, prediction, or score interface.

The audit must not claim the hidden VR2 route. In particular, finding a defect
that *could* produce `MARC2VR2-F06` does not prove that the consumed private
attempt reached `F06`; an earlier `F02`, `F03`, or `F04` refusal may have
occurred.

## Frozen Selection Audit

The committed VR2 contract records one generated result:

```text
selected subjects:                 16
selected run bundles:              96
selected core members:            384
selected reservation bytes: 8,105,207,776
reservation cap bytes:       8,589,934,592
selection identity SHA-256: dee065bf...d9f641
```

The implementation audit must verify whether `_assert_selection` compares
those exact generated values against every adapted source. It must also inspect
whether `_select_from_filtered` hardcodes generated source identity, proof
posture, or source-hash vocabulary into rows derived from a live source.

These are contract-compatibility questions, not statements about the private
manifest's actual values.

## Required Outcome Classes

- `MARC2VR5-R1`: no diagnostic-collapse or generated-identity defect is found.
- `MARC2VR5-R2`: both the nested-route collapse and generated-selection
  overconstraint are proven, while the private predicate remains unavailable.
- `MARC2VR5-R3`: only one of those two defects is proven.
- `MARC2VR5-F01` through `F04`: fixed-artifact, AST, aggregate-boundary, or
  resource refusal.

## Prospective Repair Boundary

If `R2` is reached, a separately named generated-only repair may be specified.
It must:

- preserve only the nested VR2 route code, never its private reason or value;
- keep exact source validation before selection;
- validate a measured maximal contiguous participant prefix between 12 and 19
  subjects under the unchanged 8 GiB reservation cap;
- stop requiring real selection bytes, count, or identity to equal the
  generated fixture;
- emit a real source ID and live structural proof posture for real rows;
- freeze the measured real selection hash only after a successful future pass;
  and
- qualify variable reservation boundaries on generated inputs before any new
  private request.

No consumed executor may be patched or reused. Any future private read remains
a new Tier C action requiring a separate all-false packet, fresh packet-bound
maintainer decision, exact implementation proof, and one no-retry execution.

## Resource Limits

```text
CPU threads / workers / jobs:  1 / 1 / 1
runtime:                           30 sec
peak RSS:                         128 MiB
fixed input bytes:              <= 1 MiB
aggregate output:               <= 1 MiB
retained output:                     0 B
private or Git-ignored bytes:        0 B
network bytes:                       0 B
incremental disk:                <= 1 MiB
```

## Claim Boundary

Engineering capability specified: a deterministic artifact-only audit can
separate an opaque wrapper diagnosis from a live-selection contract defect and
freeze a safer future interface.

Scientific claim not established: this contract accesses no neural payload,
target, prediction, or score and establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
