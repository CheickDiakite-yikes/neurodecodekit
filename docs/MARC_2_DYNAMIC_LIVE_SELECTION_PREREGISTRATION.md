# MARC2-VR6 Dynamic Live Selection Preregistration

Date: 2026-08-16

Lane: `MARC2-VR6`

Status: **Frozen generated-only repair contract; implementation pending**

Contract:
`registries/marc2_dynamic_live_selection_contract.v0.json`

## Why This Lane Exists

MARC2-VR5A proved two integration defects without reopening the consumed
private source. The one-shot VR4P wrapper discarded VR2's nested refusal route,
and VR2 compared every measured live selection with one exact generated
16-subject result. It also wrote generated-fixture source labels into rows
derived from a live-shaped source.

VR6 is the smallest additive repair. It does not modify or reuse VR4P, and it
does not reopen VR2's consumed private input. It qualifies a general selection
invariant over generated live-shaped structural manifests only.

## Frozen Hypothesis

A source can be validated before selection and then accepted without a
fixture-specific expected result when all of the following are true:

1. the selected participants are the maximal contiguous prefix of the frozen
   target-free participant rank;
2. the selected count is from 12 through 19;
3. each selected participant contributes exactly three fit-session and three
   heldout-session run bundles with four structural companions per run;
4. fit and heldout identities do not overlap;
5. measured reservation bytes do not exceed the unchanged 8 GiB cap;
6. either all 19 eligible participants fit, or the exact next ranked
   participant is measured and does not fit;
7. no target, label, quality value, outcome, or neural payload influences the
   selection; and
8. live-derived private rows use live source identity, proof posture, and hash
   vocabulary.

The measured subject count, reservation bytes, and selection identity hash are
outputs. They are not expected constants and cannot be compared with the VR2
generated fixture.

## Generated Success Matrix

The implementation must create five deterministic reservation regimes from
the existing full-scale generated live-shaped source:

| Profile | Expected prefix | Boundary |
| --- | ---: | --- |
| `minimum_exact_cap` | 12 | selected prefix exactly fills the cap; participant 13 does not fit |
| `lower_middle` | 14 | positive remaining bytes; participant 15 does not fit |
| `reference_middle` | 16 | positive remaining bytes; participant 17 does not fit |
| `upper_middle` | 18 | positive remaining bytes; participant 19 does not fit |
| `all_eligible_exact_cap` | 19 | all eligible participants fit and exactly fill the cap |

Every profile must pass in canonical and reversed row order, for ten success
paths. Their measured selection identities must be deterministic within a
profile and distinct across subject-count profiles. No profile-specific
selection value becomes a live expected value.

## Source And Route Semantics

The implementation may call VR2's exact full-source validation function, but
it must not call VR2's exact-result assertion. Selection must run only after
validation succeeds.

If upstream VR2 validation refuses, the additive boundary may retain only its
allowlisted route code (`MARC2VR2-F01` through `MARC2VR2-F08`). It must discard
the reason, predicate value, participant identity, member name, path, and all
other private context. Unknown upstream routes fail closed.

Generated qualification may create private-shaped rows in memory, but no row,
participant identity, member name, offset, CRC, or private hash may enter the
aggregate report. Retained output is zero.

## Required Refusals

The generated qualification must cover at least 24 direct mutations,
including:

- source or bound-contract drift;
- source mutation or output aliasing;
- unknown or reason-bearing upstream routes;
- fewer than 12 or more than 19 selected participants;
- a non-prefix or non-maximal selection;
- wrong fit, heldout, bundle, member, or overlap arithmetic;
- cap overflow, remaining-byte mismatch, or false next-participant boundary;
- selection identity mismatch or nondeterministic replay;
- generated source labels retained on a live-derived row;
- target, label, quality, outcome, or neural fields in selection provenance;
- private fields in aggregate output; and
- thread, runtime, RSS, input, output, or retention cap violations.

## Execution And Authorization Boundary

This registration authorizes generated fixtures and fixed committed artifact
reads only after the registration commit is pushed and both required CI jobs
are green. There is no `execute` command, generic path, private root, URL,
network client, archive reader, neural reader, target interface, trainer,
predictor, freezer, or scorer.

Any later private structural pass requires all of the following as a separate
sequence:

1. exact VR6 generated implementation committed, pushed, and remotely green;
2. one separately named private wrapper and immutable all-false Tier C packet;
3. a fresh packet-bound maintainer decision after that packet is remotely
   green; and
4. one no-retry execution with a new output root and consumed marker.

The current `continue` authorizes this generated-only Tier B work. It cannot be
used retroactively for that future Tier C event.

## Resource Limits

```text
CPU threads / workers / jobs:  1 / 1 / 1
runtime:                           30 sec
peak RSS:                         256 MiB
generated input:                   16 MiB
aggregate output:                   1 MiB
retained output:                     0 B
private or Git-ignored bytes:        0 B
network bytes:                       0 B
incremental disk:                    1 MiB
```

## Claim Boundary

Engineering capability specified: NeuroDecodeKit can validate a dynamic,
target-free, maximal live-selection prefix and preserve an aggregate upstream
route without binding a real source to generated outcome values.

Scientific claim not established: generated structural metadata contain no
neural payload, target, prediction, or score and establish no neural effect,
decoding accuracy, brain-specific origin, language decoding, or thought-to-text
capability.
