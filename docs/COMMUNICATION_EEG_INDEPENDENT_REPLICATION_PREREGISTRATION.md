# Communication EEG Independent Replication Preregistration

**Registration:** `COMM-R0-REPLICATION-v0`
**Date:** 2026-08-27
**Status:** prospective Tier A analysis freeze; zero real-data authority
**Machine contract:**
`registries/communication_eeg_independent_replication_contract.v0.json`

## Purpose

This registration prevents a positive or negative discovery score from
changing the independent replication. Before any `COMM-T` discovery target is
delivered, NeuroDecodeKit must commit, push, and remotely prove the exact
replication source identity, immutable revision, eligible participants, claim
ceiling, feature inventory, controls, model, thresholds, and exclusions.

If that proof does not exist, discovery scoring stays closed. A convenient
post-result source choice, participant exclusion, threshold change, or larger
model is not an allowed fallback.

This document performs no source request, payload read, training, inference,
target delivery, score, provider call, stream, device, or claim operation. It
does not activate `COMM-L0-META` and does not alter the sole active all-false
Tier C packet, `DREYER-C5R-1-HL`.

## Frozen Scientific Question

In a completely unseen participant with zero calibration, does causal central
EEG retain prompted communication-class information after source-only removal
of recorded eye activity, recorded oral-muscle activity, posterior EEG, cue,
and timing information?

The primary estimand is the smaller of two participant-macro held-out log-loss
improvements:

```text
min(
  log_loss(P)            - log_loss(P + residual EEG),
  log_loss(P + D(EEG))   - log_loss(P + residual EEG)
)
```

`P` is the available recorded nuisance context. `D(EEG)` is the registered
class-destroying residual-EEG control. Both comparisons must be positive; a
gain against no-signal alone is insufficient.

## Replication Source Lock

Public, target-free facts determine the route. Discovery results never do.

The router is deterministic. At the remotely green pre-discovery source-lock
snapshot:

1. if SilentSpeech-EEG passes every full-control gate, freeze it as the only
   full-control replication and do not use a partial route to rescue that
   claim;
2. otherwise evaluate TESSCCo and Kara One for their named partial routes in
   that fixed order, freeze every route that independently qualifies, and
   report every frozen route whether positive or negative; and
3. if neither partial route qualifies, park public replication and preserve the
   prospective synchronized-sensor fallback.

Every route uses all target-free eligible participants and the
lexicographically first common complete session/run inventory that preserves
the route's required sensors and classes under 10 GiB. There is no
performance-based participant or file subset. A full route requires at least
ten participants; each partial route requires at least twelve. An unsplittable
or over-cap route parks rather than dropping participants.

### Full-control route

SilentSpeech-EEG may become the full-control source only if a public pass
verifies all nine source gates already frozen by the replication-source
refresh: stable identity and license, complete manifest and hashes, raw
simultaneous EEG/EOG/oral EMG for every selected participant, sensor roles and
event grammar, participant-held-out folds, raw rather than irreversibly
cleaned EEG, a deterministic complete slice at or below 10 GiB, compatible
controls, and a reproducible loader or complete format description.

Failure of any gate keeps this route closed. Repository claims, paper tables,
or model accuracy are not payload identity or operational qualification.

### Partial routes

If no full-control public source qualifies, two noninterchangeable partial
challenges may be frozen:

- TESSCCo may test independent prompted-command generalization, but cannot
  establish EEG beyond separately recorded eye and oral-muscle activity unless
  those channels are verified in the exact public payload.
- Kara One may test an independent eye/face-controlled imagined-speech
  challenge, but cannot establish EEG beyond separately recorded oral EMG.

Neither partial route may inherit a missing control, use a proxy as if it were
the missing sensor, or upgrade the full peripheral-adjusted claim. If no
public route qualifies, the full claim waits for a separately approved
prospective cohort with synchronized EEG, EOG, and bilateral oral EMG.

The exact source lock must include an immutable revision, license, file hashes,
participant list, session/run list, bytes, channels, geometry availability,
sampling, events, an ordered command/class inventory with raw UTF-8 IDs, a
canonical item-ID construction scheme and uniqueness proof, exclusions, and
the resulting full or partial claim ceiling.

## Frozen Cohort And Split Rules

- Use every target-free eligible participant in the frozen source slice.
- Full-control replication requires at least ten complete participants.
- Each partial replication requires at least twelve complete participants.
- Every outer fold holds out one participant; there is no row-random split.
- Held-out-person signal may be transformed and predicted but contributes zero
  fit, normalization, residualization, calibration, threshold-selection, or
  adaptation rows.
- Source-only calibration uses participant-grouped inner folds. No held-out
  session or participant state may enter a fitted transform.
- Missing required rows, duplicated identities, participant collisions,
  incomplete class inventories, or post-lock exclusions park the fold or lane
  according to the future exact source contract; they never trigger silent
  imputation or substitution.

## Frozen Offline Event-Locked Feature Family

The feature producer is sample-causal but offline event-locked: one second of
left context, zero right context, and a decision timestamp recorded for every
row. The timestamp is the source event onset plus one fixed offset selected
from public protocol timing and frozen in the exact source lock. The event
onset, offset, and feature-availability timestamp must be recorded. Trial
membership and event boundaries may come from offline annotations, so this
stage explicitly uses a trial-boundary oracle and cannot establish continuous,
self-endpointed, real-time, or live decoding. `NDK_STREAM` must later replace
that oracle prospectively.

The window uses a periodic Hann transform and log relative power in 4-8, 8-13,
13-20, and 20-30 Hz, normalized by 2-40 Hz power with epsilon `1e-18`.

Source-only fold standardization is required. Future samples, ICA, channel
deletion, interpolation, target-derived rejection, held-out normalization, and
row-random splitting are forbidden. The source-specific channel map may select
central, posterior, EOG, and bilateral oral-EMG roles only from public
target-free metadata and must freeze with the source lock.

Central EEG is residualized using a source-only ridge model with `alpha=10`,
an intercept, and predictors from available recorded EOG, oral EMG, posterior
EEG, cue, and timing. An unavailable EOG or oral-EMG modality is recorded as
unavailable and lowers the claim ceiling; it is not replaced with zero-filled
features.

## Frozen Conditions

Every full-control fold produces these target-blind prediction sets:

1. equal prior;
2. source class prior;
3. cue only;
4. timing only;
5. EOG only;
6. oral EMG only;
7. combined nuisance context `P`;
8. selected central EEG only;
9. posterior EEG only;
10. `P + residual EEG`; and
11. `P + class-destroyed residual EEG`.

Partial routes preserve every available arm and explicitly mark unavailable
arms. They cannot pass the full-control router.

The negative control is fitted on source rows only. Let `K` be the exact frozen
command inventory for the selected source. Within each complete, class-balanced
participant/session/repeat block, sort classes by their frozen UTF-8 IDs and
construct the `K - 1` cyclic shifts from `+1` through `+(K - 1)`. Fit the
control once for each shift and average its held-out probabilities. Across the
ensemble, every class receives every other class exactly once and no single
invertible rotation defines the control. This works without selecting four
classes from a five- or 24-class source. Held-out signal remains untouched and
held-out targets remain sealed. `K < 2`, an incomplete block, or unequal class
counts refuses.

## Frozen Model And Language Controls

The neural classifier is one multinomial L2 logistic family: `C=0.1`, `lbfgs`,
`max_iter=1000`, `tol=1e-6`, no class weights, source-only standardization,
and probabilities clipped to `[1e-6, 0.999999]`. There is no hyperparameter
search. Nonconvergence parks the affected registered route; it does not permit
more iterations after target delivery.

This fixed-command replication permits no external or generative language
model. Its language context is exactly the source-only class prior, which is
frozen before held-out prediction. The following arms are evaluated from the
same neural prediction freeze:

- `language_only`;
- `neural_only`;
- `neural_plus_language`; and
- `item_deranged_neural_plus_language`.

`language_only` is the source class prior. `neural_only` is the frozen candidate
probability. `neural_plus_language` is the normalized elementwise product of
candidate probability and source prior. `item_deranged_neural_plus_language`
uses the same product after a target-blind, SHA-256-keyed, no-fixed-point
permutation of held-out prediction vectors within participant and session.
Within each group, sort item IDs by raw UTF-8 bytes, hash
`COMM-R0-REPLICATION-v0|item-derangement|<source_id>|<session_id>|<item_id>`,
sort by `(digest, item_id)`, and rotate the ordered prediction vectors by one.
Groups with fewer than two items refuse. Participant identity defines the
isolation group but is not an input to the hash, model, or provider. Neither
labels nor target text enter the transform.

Provider calls, prompt text, intended or reference text before freeze,
participant metadata, file paths, raw EEG, dense embeddings, and held-out
labels are forbidden. A future generative LLM layer requires a separate
pre-result contract after neural evidence exists. A language gain without a
neural gain does not pass the neural router.

## Frozen Scientific Gates

The full-control route passes only if all gates pass independently in the
discovery cohort and again in the frozen replication cohort:

1. participant-macro primary estimand is at least `0.03` nats per item;
2. both component log-loss margins are positive in at least 70% of complete
   participants;
3. an exact one-sided participant sign-flip test on the per-participant minimum
   margin has `p <= 0.05`;
4. `P + residual EEG` participant-macro balanced accuracy exceeds the maximum
   of equal prior, source prior, cue-only, timing-only, and posterior-only by at
   least `0.05` absolute;
5. candidate participant-macro log loss is better than equal prior;
6. every required control, participant fold, prediction set, and target row is
   complete; and
7. there is zero held-out fit, post-target update, rerun, or unregistered
   exclusion.

The minimum-margin estimand makes the two primary comparisons one conjunction,
not two chances to pass. Exhaust all `2^n` participant sign patterns when
`n <= 20`; enumerate integer masks from zero through `2^n - 1`, with bit `j`
giving the sign for participant `j` in raw UTF-8 participant-ID order. For
larger cohorts, draw exactly 1,000,000 patterns with replacement. For draw `i`
and participant rank `j`, SHA-256 the ASCII bytes
`COMM-R0-REPLICATION-v0|sign-flip|<source_id>|<i>|<j>`; the least-significant
bit of the final digest byte selects `+1` when set and `-1` otherwise. The
one-sided p-value is `(1 + count(T_draw >= T_observed)) / 1,000,001`. No
library PRNG is used, and no discovery outcome may alter this schedule or the
gates.

A partial source uses the same minimum-margin, 70% consistency, accuracy,
completeness, and one-score gates over its exactly available nuisance set, but
reports only its named partial endpoint. When both partial routes qualify, both
must run and their sign-flip p-values use a two-hypothesis Holm correction;
neither route may be omitted after scoring. A partial route cannot pass the
full-control router, even if every available numerical gate is positive.
Independent replication is established only by a separately sourced cohort
that passes its frozen claim ceiling; a second split of the discovery dataset
is not independent replication.

## Prediction Freeze And One Score

Each fold receives source signal and source targets plus held-out signal. Its
capability cannot enumerate another fold or any held-out target envelope. The
public prediction freeze is aggregate and hash-only: it contains no individual
prediction, probability, target, participant result, row path, or capability
path.

The exact replication protocol and source lock must be committed, pushed, and
remotely green before the discovery scorer can receive targets. Replication
predictions are then frozen before one delivery of the same registered
replication targets and one score. Post-target updates and reruns are zero.

## Resources And Refusal Boundary

- one CPU thread, one worker, and one numerical job by default;
- 20 GiB maximum total incremental research storage;
- 10 GiB maximum selected raw communication payload;
- 300 seconds, 768 MiB peak process-tree RSS, 32 MiB generated input, 64 MiB
  private generated output, 128 MiB temporary disk, and 1 MiB public output for
  generated qualification;
- 3,600 seconds, 1 GiB peak process-tree RSS, 5 GiB private derivative and
  prediction output, 768 parameter-update fits, 768 inference/prediction sets,
  and 1,000,000 prediction rows across one future registered real replication
  execution;
- zero analysis-time network or provider bytes;
- no write outside the NeuroDecodeKit checkout;
- this registration performs zero cleanup or deletion; a future executor may
  remove only inode-verified temporary files created by that invocation; and
- no real operation under this preregistration.

The future generated qualification must exercise identity, split, target,
causality, channel-role, missing-control, derangement, prediction-tamper,
pre-freeze delivery, repeated-delivery, no-clobber, symlink, deterministic
replay, output-cap, RSS, and timeout refusals before any real execution packet.

## What This Adds

Engineering capability added: the independent replication can no longer be
chosen or redesigned after seeing the discovery score, and a partial source is
machine-barred from a full peripheral-adjusted claim.

Scientific claim not established: this registration accessed no real EEG,
trained no model, opened no target, produced no score, and established no
communication decoding, EEG-beyond-peripheral effect, unseen-person
generalization, independent replication, causal live decoding, or clinical
result.
