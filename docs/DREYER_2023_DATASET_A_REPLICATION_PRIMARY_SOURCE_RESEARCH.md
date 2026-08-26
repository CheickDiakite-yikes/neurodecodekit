# Dreyer Dataset A Independent Replication Research Decision

Date: 2026-08-25

Status: **Fresh cohort selected conditionally. No EDF payload, header,
annotation, signal sample, target, or label was read.**

Lane ID: `DREYER-C5R-1`

## Decision

Use Dataset A from Dreyer et al. (2023) as the next independent motor-imagery
replication, conditional on one exact source-EDF header preflight confirming
that the source representation preserves all recorded nuisance sensors.

The selected surface is deliberately narrow:

- participants `sub-01` through `sub-60`;
- source EDF representation only;
- calibration runs `R1` and `R2` only;
- 120 exact files;
- `1,779,763,388` payload bytes (`1.6575` GiB); and
- no use of runs `R3` through `R6`.

The exact member identities, sizes, SHA-256 values, and direct NEMAR URLs are
frozen in
`registries/dreyer_2023_dataset_a_r1_r2_payload_manifest.v0.json`.

## Why This Cohort

The primary paper reports 60 Dataset A participants, 27 scalp EEG electrodes,
three right-eye EOG electrodes, two wrist EMG electrodes, 512 Hz acquisition,
and left-versus-right hand motor-imagery trials. Each selected run contains 40
trials, 20 per condition. That combination directly addresses the prior BNCI
failure map:

1. 60 completely fresh people make participant consistency testable rather
   than anecdotal.
2. Recorded EOG permits an explicit eye-information baseline and source-only
   EEG residualization.
3. Wrist EMG permits a peripheral-muscle control that the prior lane lacked.
4. Named sensor locations permit fixed central, frontal, and posterior
   comparisons.
5. Two 40-trial calibration runs provide 4,800 trials while keeping the four
   later runs untouched for a genuinely independent future replication.

The paper is the authoritative semantic source:

- article: <https://doi.org/10.1038/s41597-023-02445-z>
- NEMAR dataset: <https://nemar.org/dataset/nm000250>
- official revision manifest:
  <https://data.nemar.org/nm000250/v1.0.4/manifest.json>

The data are listed under CC BY 4.0. NeuroDecodeKit must retain source and
license attribution in every derivative receipt.

## The Important Confound

This is not a covert-intention dataset. A lateralized red arrow identifies the
requested hand at 3 seconds, and target-side visual feedback begins at 4.25
seconds. During R1/R2 the feedback magnitude is sham, but its side still
matches the instructed class. Eye movement, posterior visual activity, trial
timing, and wrist muscle activity can therefore predict the label without
establishing a sensorimotor EEG contribution.

For that reason the proposed primary comparison is not EEG versus chance. It
is a source-only calibrated nuisance model versus the same model plus central
EEG features that were residualized against EOG, EMG, posterior EEG, and
timing. A within-run derangement of those residual EEG features is the matched
negative control.

## Source-Representation Preflight

The NEMAR BIDS conversion sidecars expose 27 EEG channels but do not expose the
paper's EOG and EMG channels. The source EDF files are therefore selected, but
their sensor roster remains unverified.

Before any bulk acquisition, one separately authorized preflight may inspect
only the fixed EDF header of:

`sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf`

The registered identity is 14,805,604 bytes with SHA-256
`a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185`.
The preflight passes only if the header exposes exactly the 27 named EEG
electrodes from the paper, three distinct EOG channels, two distinct EMG
channels, 512 Hz sampling, and no duplicate signal labels after canonical
normalization. Raw header text and participant metadata may not be published.

If any required sensor or sampling property is absent or ambiguous, the lane
parks before the remaining 119 payloads are requested. A different dataset may
then be proposed in a new prospective decision; no substitution is implicit.

## Structural Rules Frozen Before Targets

- Every selected participant contributes exactly R1 and R2.
- Every run must contain exactly 40 trial starts and 40 class cues, balanced
  20 left and 20 right.
- Segmentation uses trial-start and cue events, never end-of-trial markers.
  This makes the published missing end markers in participant A1 irrelevant
  only if all required start/cue invariants pass.
- No participant is excluded after looking at targets or model outcomes.
- Any structural mismatch parks the entire registered execution before model
  fitting or held-out prediction.
- R3-R6 and all other datasets remain unopened by this lane.

## Alternative Retained

Ofner et al. 2017 / BNCI 2017-001 remains the fallback candidate because it
reports 15 participants, 61 EEG channels, three EOG channels, and detailed
motor tasks. It was not selected for this lane because Dreyer Dataset A offers
four times as many fresh participants, explicit wrist EMG, a simpler binary
target, and a much smaller exact R1/R2 payload surface. The fallback is not
authorized or acquired by this decision.

## Claim Ceiling

Even a complete pass could establish only participant-independent information
about visually cued left-versus-right motor-imagery protocol conditions, with
an incremental contribution from predeclared central EEG sensors beyond the
recorded EOG, wrist EMG, posterior EEG, timing, and derangement controls in
this dataset.

It could not establish spontaneous movement intention, exclusive motor-cortex
origin, eye-independent causation, thought or language decoding, live neural
decoding, portable hardware, home use, or clinical utility.
