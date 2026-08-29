# Ofner 2017 Motor-Imagery Source Reselection

Date: 2026-08-29

Status: **selected prospectively from public metadata; no EEG payload, event
table, annotation, target, signal sample, model, prediction, or score accessed**

Lane ID: `OFNER-C6R-1`

Machine record:

- `registries/ofner_2017_motor_imagery_source_reselection.v0.json`

Current frontier:

- `registries/current_research_frontier.v2.json`

## Decision

Select the original motor-imagery GDF representation of Ofner et al. (2017),
BNCI Horizon 2020 dataset `001-2017`, as the next prospective source for the
nuisance-controlled unseen-person question.

The selected public revision is NEMAR `nm000173` `v1.0.3`, Git tag object
`4e1329ceb93e0cc5e81d0d2d5d1839527299b251`.

The manifest endpoint is versioned but its raw response is not byte-stable: it
contains expiring signed `url` query strings. Two raw observations produced
different SHA-256 values, `c227c2e8...` and `443f8ed4...`. The frozen identity
therefore removes only each row's volatile `url` field, preserves `bytes_url`
and every scientific identity field, sorts object keys, and emits compact JSON
with one trailing newline. Two independent canonicalizations matched at
748,162 bytes with SHA-256
`5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34`.

That canonical metadata-only selector identifies exactly:

- 15 participants;
- 10 motor-imagery runs per participant;
- 150 original GDF files;
- 13,748,417,608 payload bytes (`12.8042` GiB);
- one unique SHA-256 per file; and
- one stable `data.nemar.org` bytes URL per file.

This selection fits the maintainer's 20 GiB research allowance while leaving
7,726,418,872 bytes (`7.1958` GiB) of the allowance for staging, derivatives,
and safety headroom. No file has been downloaded by this decision.

## Why This Source

The source representation reports the measurement surface needed to test a
more discriminating motor-imagery question:

- 61 scalp EEG channels with named geometry;
- three EOG channels;
- 19 data-glove channels;
- 13 exoskeleton/arm channels;
- 512 Hz sampling;
- six imagined right-arm movement classes plus rest;
- 60 trials per class in the imagery session; and
- 15 completely held-out participant units.

The planned scientific question is:

> In a completely unseen participant, does predeclared central EEG add
> predictive information about the imagined right-arm movement class beyond
> recorded EOG, recorded hand/arm kinematics, posterior EEG, cue/timing
> structure, and matched EEG derangement?

This is closer to a genuine neural-increment test than EEG-versus-chance. It
directly targets the eye and posterior shortcuts that defeated the prior BNCI
specificity claim, while the glove and exoskeleton channels can detect overt
movement or movement-correlated shortcuts.

Primary sources:

- NEMAR dataset: <https://nemar.org/dataset/nm000173>
- versioned manifest endpoint:
  <https://data.nemar.org/nm000173/v1.0.3/manifest.json>
- BNCI catalog: <https://bnci-horizon-2020.eu/database/data-sets>
- official dataset description:
  <https://lampx.tugraz.at/~bci/database/001-2017/dataset_description.pdf>
- primary paper: <https://doi.org/10.1371/journal.pone.0182578>

The release metadata declares CC BY 4.0. Every future derivative and receipt
must preserve attribution.

## Representation Trap Found

The smaller BIDS derivative is not an acceptable substitute for this question.
Its motor-imagery session is 4,578,904,696 bytes, but the inspected public
channel sidecar lists only the 61 EEG channels. The EOG and 32 movement channels
are absent from that derivative surface.

The original GDF files are therefore the only selected representation. A future
reader must verify the reported 96-channel roster from one separately governed
fixed-header observation before bulk acquisition or semantic use. It may not
silently fall back to the smaller BDF files.

## Scientific Design Boundary

The future confirmation must freeze, before any held-out outcomes are opened:

- leave-one-participant-out evaluation over all 15 people;
- one compact regularized model family;
- source-only preprocessing, residualization, and probability calibration;
- no-signal, EOG, kinematics, posterior EEG, cue/timing, pre-cue, and matched
  derangement controls;
- participant-macro log loss as the primary endpoint;
- a minimum practical EEG increment and participant-consistency threshold;
- target-derived exclusion prohibition; and
- one prediction freeze followed by one score.

Discovery work may use only a separately declared development partition. It
must never inspect or retune against the eventual frozen held-out outcomes.

## Claim Ceiling

Even a complete positive result could establish only an unseen-participant,
offline, event-locked predictive increment from selected central EEG beyond
recorded EOG, hand/arm kinematics, posterior EEG, timing, and derangement for
visually cued imagined right-arm movement classes in this dataset.

The source has no recorded EMG. Therefore it cannot establish independence
from all muscle activity, exclusive motor-cortex origin, spontaneous movement
intention, thought or language decoding, cross-dataset replication, live neural
decoding, portable hardware, home use, or clinical utility.

## Operations And Next Gate

This was Tier A public-source research. It used public manifests, repository
identity, dataset/license metadata, one public channel sidecar, one public
electrode sidecar, and primary-source documents. It made zero EEG-payload,
event-table, target, annotation, or signal requests and produced zero model or
scientific-score operations.

The raw-manifest instability check was metadata-only. It changed the future
identity rule, not the selected files: volatile signed URLs are transport
capabilities, while paths, sizes, checksums, stable bytes URLs, revision, and
license remain identity.

No Tier C packet is active. The next reversible milestone is a generated-only
manifest selector and acquisition implementation qualified against fixtures.
Any real GDF request requires a separate all-false packet, exact green proof,
fresh packet-bound maintainer decision, and ordered green implementation gate.

Engineering capability added: NeuroDecodeKit now has an exact, license-qualified, storage-feasible source selection that preserves EOG and limb-motion comparators instead of silently accepting an EEG-only derivative.

Scientific claim not established: no real Ofner GDF payload, event, target, annotation, signal, model, prediction, or score was accessed, so no neural advantage, unseen-person decoding, motor-cortex attribution, live operation, or clinical value was established.
