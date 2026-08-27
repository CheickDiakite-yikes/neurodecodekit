# COMM-G1 Generated Experiment Amendment 1

**Date:** 2026-08-27  
**Scope:** generated-only control correction before implementation or qualification  
**Scientific value:** none

## Why this amendment is necessary

The remotely green v0 contract defined the negative-control derangement within
source participant, session, **and class**. A class-preserving permutation does
not break the relationship between an EEG feature and its class. It therefore
cannot distinguish a real residual-EEG increment from a control that still
carries the same class information.

No COMM-G1 implementation, qualification, prediction freeze, target delivery,
or score existed when this defect was found. This amendment is prospective. It
does not reinterpret a result or modify the immutable v0 files.

## Frozen correction

Only the derangement rule changes:

1. Derangement is fitted and applied only to source rows.
2. Source rows are grouped by participant, session, and repeat index.
3. Each complete four-class group is sorted by source class.
4. Residual-EEG feature vectors are reassigned by a one-class cyclic rotation:
   class 0 receives class 1, class 1 receives class 2, class 2 receives class 3,
   and class 3 receives class 0.
5. The transform has no fixed point, preserves row count, feature dimension,
   participant, session, repeat, and marginal feature values, and never reads a
   held-out target.
6. Held-out residual-EEG rows are not permuted. The control classifier is fit on
   source rows whose EEG-to-class relationship has been deliberately broken,
   then evaluated on the same untouched held-out signal used by the candidate.
7. An incomplete group, duplicate class, missing source target, held-out target,
   or any target outside the four frozen classes is a hard refusal.

The source targets used to construct this negative control are already inside
the source-only fold capability. They are not used by the feature producer,
residualizer, held-out transform, or any selection rule.

## Unchanged boundaries

The cohort geometry, causal feature definition, residualizer, classifier,
conditions, fit/inference schedule, participant firewall, frozen router,
resource caps, one-shot generated qualification, and all claim boundaries are
unchanged. All real-data, private-path, network, provider, device, release, and
scientific-claim authority remains false. `DREYER-C5R-1-HL` remains the sole
active Tier C packet.

## Next gate

This amendment must be committed, pushed, and remotely green before COMM-G1
implementation. The implementation must bind both the original contract and
this amendment. Its official generated qualification remains closed until the
exact implementation is independently committed, pushed, and remotely green.

