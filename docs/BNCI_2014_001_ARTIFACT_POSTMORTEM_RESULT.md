# BNCI-C3C5-1 Aggregate Artifact Postmortem Result

Date: 2026-08-25

Status: **Completed once. This was a post-outcome, aggregate-only descriptive
analysis, not a fresh scientific test.**

## Plain-Language Result

The earlier held-out BNCI experiment contained real protocol information, but
the committed aggregate result does not support an EEG-specific explanation.
Posterior EEG slightly outperformed the preselected EEG candidate, the
candidate's log loss was worse than an equal-probability prior, and the small
increment obtained by adding EEG to recorded EOG was not consistent across
participants.

This localizes the next experiment's job. It must prospectively separate
central EEG from visual/posterior, recorded-EOG, peripheral-muscle, timing, and
probability-calibration shortcuts in a fresh cohort. It should not respond to
this result by increasing model size.

## Frozen Diagnostic Map

| ID | Question | Result |
|---|---|---|
| D1 | Was aggregate protocol information present? | Supported descriptively |
| D2 | Was the candidate spatially specific against posterior EEG? | Failed; posterior EEG was better |
| D3 | Were candidate probabilities reliable? | Failed; log loss was worse than the equal prior |
| D4 | Was EEG incremental beyond recorded EOG? | Weak directional result only; not validated |
| D5 | Was the primary effect consistent across held-out people? | Failed |
| D6 | Was a brain-specific causal source established? | Unavailable from the aggregate artifact |

The ordered replication priorities are:

1. distinguish selected EEG from posterior/visual information;
2. estimate the EEG increment after source-only nuisance removal;
3. freeze probability calibration using source participants only; and
4. test participant consistency in a fresh independent cohort.

## Why The Prior Gates Failed

The selected EEG candidate reached `0.38349` participant-macro balanced
accuracy, above equal-prior chance (`0.25`) and timing (`0.29668`). Posterior
EEG reached `0.39236`, however, so the result did not localize information to
the intended sensor set. Candidate log loss was `1.61026`, worse than the
equal-prior value `1.38629`, showing that its errors were poorly calibrated.

Adding selected EEG to recorded EOG improved aggregate log loss by `0.02552`;
the corresponding advantage over deranged EEG was `0.01843`. Both changes were
directionally favorable but below their frozen `0.03` thresholds, positive in
only 6 of 9 participants, and nonsignificant under the exact sign-flip tests.
These are design signals, not positive scientific endpoints.

## Integrity And Resources

The executor read exactly one committed 4,951-byte Stage T aggregate result and
one governance contract. It read zero private artifacts, predictions,
participant outcomes, targets, labels, EEG/MAT payloads, models, or
checkpoints. Training, inference, scoring, downloads, scientific reruns, and
claim upgrades were all zero.

The run completed in `1.822619083` seconds at `23,216,128` bytes peak process
RSS and emitted one 6,091-byte public JSON result with SHA-256
`b211f894658beb642cebc40e54dba9c33a9bd3cf7664b91a6170b086dfd96c8a`.
The implementation commit `67f2189e178f752e8a19edff1f7d4cb151a0f443`
passed Base Python job `98049230269`, Optional Neuro Readers job
`98049230184`, and CI run `32926111990` before the analytical input was read.

## Claim Boundary

Engineering capability established: NeuroDecodeKit can reproduce a strict,
proof-bound diagnostic map from one committed aggregate scientific result
without reopening consumed private evidence.

Scientific claim not established: this post-outcome description does not prove
a causal root source, fresh replication, unseen-person EEG decoding, EEG
beyond EOG, movement intention, language decoding, live behavior, hardware
performance, or clinical utility.
