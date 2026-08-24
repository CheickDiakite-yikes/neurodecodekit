# BNCI 2014-001 Cross-Participant EEG-Gain Primary-Source Research

Date: 2026-08-24

Status: **Tier A public-metadata research complete; no neural payload, event
table, target, model, prediction, or score was opened**

Machine record:
`registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json`

## Decision

Select the original BNCI 2014-001 motor-imagery distribution mirrored by
NEMAR `nm000139` at tag `v1.0.2` as the next independent scientific lane.
The future experiment is `BNCI-C3C5-1`.

It asks two linked questions under one participant-independent protocol:

1. can one compact model predict four-class motor-imagery condition in a
   completely held-out person with zero calibration; and
2. does adding scalp EEG improve held-out-person log loss over the strongest
   recorded-EOG-only model and a size-matched deranged-EEG fusion?

This is an independent route. It is not a repair, retry, resume, fallback, or
substitution for consumed EEGMMIDB-UG1 Stage S-A2.

## Why This Source

The current WO9R result proves that NeuroDecodeKit can recover repeatable
held-out-run task information, but it does not generalize across people and
its early-cue and frontal controls are stronger than its central view. The
next dataset therefore needs both participant separation and an ocular
comparator.

BNCI 2014-001 is the smallest well-established source found in this pass that
offers all of the following together:

- nine people;
- two sessions per person;
- six runs per session;
- four motor-imagery classes;
- 22 consistently placed EEG channels;
- three separately recorded EOG channels;
- 250 Hz sampling; and
- an original-distribution slice below 800 MiB.

Larger movement sources can test richer attribution. Ofner 2017 has 15
participants, 61 EEG channels, three EOG channels, and movement measurements,
but the current NEMAR mirror is about 34 GB and exceeds the active 10 GB data
ceiling. Freewill-23 and EEGMMIDB-UG1 are consumed or parked. OpenNeuro
`ds003626` remains the preferred closed-set language source, but it answers a
different first question and needs its own exact size and target-firewall
qualification.

## Pinned Public Identity

The official BNCI catalog identifies `001-2014` as BCI Competition IV dataset
2a with nine participants, 22 EEG channels, three EOG channels, and a
CC BY-ND 4.0 license. The NEMAR mirror is pinned as:

```text
dataset:                   nm000139
version tag:               v1.0.2
annotated tag object:      919bf4e0b613f6504258762e092a629e8bcde3a1
peeled commit:             15cf4f87975f4b5ee2ac39f703b9ac85b0ff97dc
manifest records:          769
full mirror bytes:         1,485,047,253
original MAT files:        18
original MAT bytes:        779,873,919
participants represented:  9
license:                   CC-BY-ND-4.0
```

NEMAR's source provenance says the 18 MAT files were retrieved through MOABB
1.5.0, retain their upstream names, and are byte-for-byte as retrieved. The
future acquisition should use only those 18 original files plus small pinned
provenance records. It should not acquire the duplicate 108-file BDF
conversion, HTML neural-signature derivatives, or both representations.

This research pass read the public manifest and source-provenance metadata.
It did not request any `.mat` or `.bdf` body, inspect an event table, or retain
the fetched response bodies. Only the bounded identity, size, hash, and source
facts in the machine record were retained.

Primary sources:

- [BNCI Horizon 2020 dataset catalog](https://bnci-horizon-2020.eu/database/data-sets)
- [BCI Competition IV dataset page](https://www.bbci.de/competition/iv/)
- [BCI Competition IV review](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2012.00055/full)
- [NEMAR nm000139](https://nemar.org/dataset/nm000139?v=v1.0.2)
- [Pinned NEMAR repository](https://github.com/nemarDatasets/nm000139/tree/v1.0.2)
- [Pinned NEMAR manifest](https://data.nemar.org/nm000139/v1.0.2/manifest.json)
- [MOABB cross-subject evaluation contract](https://moabb.neurotechx.com/docs/generated/moabb.evaluations.CrossSubjectEvaluation.html)

## Exact Future Payload Slice

The payload candidate is exactly the 18 `sourcedata/A??[TE].mat` files in the
machine record. Their aggregate size is `779,873,919` bytes. Every file has a
published SHA-256 digest.

A later acquisition packet must freeze all 18 paths, sizes, and hashes before
any payload request. The acquisition stage must remain opaque: size and hash
only, no MATLAB parsing, signal, event, trial, label, or target read. Semantic
qualification and target isolation are later stages with separate barriers.

Because the license forbids redistribution of adapted material, no source
payload, row-level derivative, epoch array, checkpoint, individual
prediction, or participant outcome may be committed. Code, source citations,
aggregate measurements, and bounded non-identifying reports remain the public
surfaces unless a later license review establishes a wider boundary.

## Frozen Scientific Unit

The scientific unit is the participant. The nominal source contains four
classes: left hand, right hand, feet, and tongue. Four-class evaluation is the
primary endpoint. A later left-versus-right analysis may be prespecified as a
secondary diagnostic, but it cannot rescue a failed four-class gate or upgrade
the claim.

The outer protocol has nine folds. In fold `i`:

- both sessions, every signal sample, every target, and every normalization
  statistic from participant `i` are forbidden during fitting, selection,
  calibration, and threshold creation;
- the other eight participants are the only source domain;
- the final prediction is made on participant `i` session `1test`; and
- no participant-specific calibration, covariance alignment, normalization,
  adaptation, rejection threshold, or abstention threshold is allowed.

Each fold is an isolated capability. A participant target may train a
different fold where that person is in the source domain, but it can never be
visible to the fold that predicts that participant. All nine fold predictions
must be frozen before the one aggregate scoring delivery.

## Conditional Fusion Architecture

The recommended compact architecture is a cross-fitted conditional stack,
not a deep network:

```text
P:       strongest fixed EOG-only probability model
E:       source-only EEG probability model
P+E:     source-cross-fitted fusion over P and E logits
P+D(E):  identical fusion with fixed target-blind EEG trial displacement
```

Within each outer fold, source-person cross-fitting creates out-of-person base
logits for the fusion model. Base models are then refit on all eight source
people. No held-out-person signal is used to fit a scaler, covariance
reference, spatial filter, calibrator, fusion weight, or threshold.

The future preregistration should qualify a small fixed classical family on
generated fixtures before choosing exact dimensions:

- one-pass causal filtering with state reset only at run boundaries;
- source-only referencing and standardization;
- motor-band EEG log-power or trace-normalized covariance features;
- low-frequency EOG temporal summaries over identical decision windows;
- fixed ridge or shrinkage classification;
- one completed-trial decision point; and
- no neural network, pretrained checkpoint, foundation model, language model,
  or target-text feature.

The fusion is the main architectural idea: instead of asking only whether EEG
predicts a visually cued class, it asks whether EEG adds held-out-person
information after the recorded eye signal has already made its best source-
trained prediction.

## Required Controls

Every future prediction freeze must include:

- equal-prior no-signal;
- source-only empirical prior;
- timing and trial-order only;
- EOG-only `P`;
- EEG-only `E`;
- fused `P+E`;
- size-matched `P+D(E)`;
- exact-zero EEG;
- fixed EEG channel permutation;
- fixed nonwrapping EEG trial displacement within run;
- fixed source-label derangement;
- pre-cue and early-cue windows; and
- central, frontal, and posterior EEG views.

Exclusion, quality, and artifact rules must be target-blind and frozen from
source data. No target-derived row removal is allowed. Exact trial counts and
event semantics remain unavailable until a separately authorized structural
qualification.

## Recommended Endpoints

The exact thresholds remain preregistration work, but the research decision
freezes the direction and inference unit.

### C3: unseen-person protocol-condition prediction

Primary descriptive metric: participant-macro four-class balanced accuracy.
The frozen candidate must beat the stronger matched no-signal and timing
controls on the same participant rows. Participant-level paired statistics,
not pooled trial count, determine the pass.

### C5-partial: EEG beyond recorded eyes

Primary metric:

```text
delta_EOG = participant_macro_log_loss(P)
          - participant_macro_log_loss(P+E)
```

`delta_EOG` must be positive with a preregistered effect-size floor, an exact
paired participant test, and a matched win over `P+D(E)`. Accuracy alone is
not sufficient because added EEG may improve probability quality without
changing the winning class.

Even a clean pass is only incremental scalp-EEG sensor information beyond the
three recorded EOG channels. The dataset has no synchronized EMG or movement
sensor, so it cannot close the broader claim against every peripheral source.

## Staged Evidence Order

1. Commit and remotely green this Tier A decision.
2. Freeze an all-false preregistration and acquisition request.
3. Qualify manifest, transport, size/hash, and fail-closed behavior using only
   generated fixtures and mocked responses.
4. After a new exact Tier C decision and green proof barriers, acquire the 18
   original MAT files once and verify them opaquely.
5. Separately qualify a target-firewalled MAT reader using generated fixtures.
6. Run target-blind structural and signal-quality qualification.
7. Train the nine isolated source-only folds and freeze every candidate and
   control prediction.
8. Commit, push, and remotely green the aggregate hash-only freeze.
9. Deliver the same fold-scoped targets once and score once.
10. Stop without tuning, rerun, target reuse, or claim expansion.

## Resource Envelope

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
future original MAT payload bytes:        779,873,919
future incremental disk maximum:          2 GiB
future private derivatives maximum:       512 MiB
future public artifacts maximum:          2 MiB
future peak RSS maximum:                   1 GiB
network during modeling/scoring:           0 bytes
final aggregate target deliveries:         1
final scoring events:                      1
reruns / post-target updates:              0 / 0
```

The selected payload is less than 8% of the maintainer's current 10 GB data
allowance. The larger allowance is a ceiling, not a target.

## Claim Boundary

The maximum future combined result is participant-independent four-class
BNCI protocol-condition prediction plus incremental EEG information beyond
the dataset's three recorded EOG channels.

It would not establish arbitrary thought reading, language decoding, executed
movement intention, exclusive motor-cortex origin, freedom from EMG or other
unrecorded artifacts, clinical utility, portable hardware, or live decoding.

Engineering capability added: the next independent real-data lane now has a
pinned sub-800-MiB source, a zero-calibration participant firewall, and a
conditional EOG-versus-EEG architecture.

Scientific claim not established: this research opened no neural payload,
event table, row target, per-trial label, model, prediction, or score, so C3,
C5, and every other new scientific claim remain unproven.
