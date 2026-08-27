# Communication EEG Replication Source Refresh

Date: 2026-08-27

Status: **Tier A public-source research only; no dataset payload, private path,
signal, target, model, prediction, score, stream, or device operation**

Machine record:
`registries/communication_eeg_replication_source_refresh.v0.json`

## Decision

Do not promote a second communication-EEG cohort into a real-data packet yet.
The public sources reviewed here do not currently verify a complete,
independently sourced cohort that preserves raw EEG, recorded eye activity,
recorded oral-muscle activity, participant identity, event timing, stable
payload identity, and usable license terms under one reproducible release.

This is a source-quality decision, not a decision to slow the scientific
program. It prevents a large download or one-shot score from answering the
wrong question. A cohort without measured eye and mouth controls can test a
partial replication, but it cannot establish that EEG contributes information
beyond both major recorded peripheral shortcuts.

## SilentSpeech-EEG: Strong Scientific Fit, Unverified Public Surface

The BrainStack paper and repository describe SilentSpeech-EEG as a large
silent-word dataset: 12 collected participants, 24 words, 16 sessions per
participant, roughly 6,000 trials per participant, high-density EEG, and
external channels. The repository README currently says ten participants are
in a public release and lists 122 EEG plus 11 extra channels.

That surface is not reproducible enough to register today:

- the repository's own availability statement says the full dataset was under
  preparation and anonymization and was not included in the submission;
- the public repository does not expose a stable dataset DOI, immutable
  revision, complete file manifest, payload hashes, or dataset license;
- an open repository issue reports that `data/dataset.py` is absent and that
  the expected data root and layout cannot be determined; and
- the README's `122 EEG + 11 extras` does not by itself establish exact raw
  EOG, oral-EMG, reference, and trigger roles for the released payload.

Therefore SilentSpeech-EEG is the most promising full-control watchlist source
identified by this pass, but it is **not operationally qualified or authorized
for acquisition**. Its reported model accuracy is also not evidence for
NeuroDecodeKit: the principal split is session-wise within-person, and the
paper's architecture or result cannot substitute for our participant-held-out,
peripheral-adjusted prediction freeze.

## Public Alternatives And Their Claim Limits

### Kara One

The University of Toronto page verifies 14 participant archives, 64-channel
EEG, four ocular electrodes, Kinect facial features, imagined and spoken
prompts, and academic nonprofit use terms. It does not verify separately
recorded oral EMG. The full archive is approximately 24 GB, above the current
10 GiB selected-raw ceiling. Kara One can support an eye/face-controlled
partial replication after a separate exact source and storage decision; it
cannot by itself support the full EEG-beyond-eye-and-mouth claim.

### Directional Word 2026

The primary descriptor reports 22 participants, 38 EEG channels, and two oral
EMG channels in only six participants. It reports no separately recorded EOG,
uses fixed word blocks, and uses right-hand key presses to mark covert
articulations. It is useful for testing oral-muscle and timing confounds in a
subset, but it cannot provide a full eye-plus-mouth adjusted replication.

### ArEEG

The primary descriptor reports 12 participants, five Arabic inner-speech
classes, 15 sessions per participant, eight EEG channels, and a public
OpenNeuro release. The article does not report EOG or EMG channels and states
that its evaluation was participant-specific rather than unseen-person. ArEEG
is an accessible low-density engineering and partial no-peripheral-control
benchmark, not a full attribution replication.

## Exact Promotion Gate

A future independent cohort may enter an acquisition packet only after public,
target-free verification of all of the following:

1. a stable dataset DOI or official host, immutable revision, and license;
2. exact participant, session, raw-file, byte-size, and checksum identities;
3. raw simultaneous EEG, EOG, and oral EMG for every selected participant;
4. source channel roles, sampling rate, geometry, and event grammar;
5. participant IDs that support zero-calibration held-out-person folds;
6. no requirement to use processed-only EEG after peripheral-correlated
   components have already been removed;
7. a deterministic target-free slice that is complete for every selected
   participant and remains at or below 10 GiB;
8. an event schedule that permits cue, time, posterior, EOG, oral-EMG, and
   participant-matched derangement controls; and
9. a public loader or sufficiently complete format description that an
   independent group can reproduce without private instructions.

Failure of any item parks the source or narrows it to an explicitly partial
replication. It does not permit substitution, payload acquisition, or claim
upgrade.

## Next Scientific Move

Keep `ds003626-v2.1.2` as the discovery cohort and complete only its already
registered source-identity sequence after the required Tier C decision. In
parallel, monitor SilentSpeech-EEG for a stable public dataset identity,
license, manifest, loader, and exact external-channel roster. If that release
qualifies before discovery scoring, freeze its replication protocol without
using discovery outcomes to select participants, preprocessing, thresholds,
or model capacity.

If it does not qualify, a partial Kara One or Directional Word result must be
reported as partial, and the full claim requires a separately approved
prospective cohort with synchronized EEG, EOG, and bilateral oral EMG.

This refresh creates no competing Tier C packet. `DREYER-C5R-1-HL` remains
the sole active Tier C gate, and all of its authority flags remain false.

## Resource And Claim Boundary

- public document reads only;
- zero payload requests and zero incremental payload bytes;
- zero private or Git-ignored path reads;
- zero EEG/EXG header, signal, event, target, or label reads;
- zero training, inference, prediction, target-delivery, or score operations;
- zero cleanup, deletion, or write outside NeuroDecodeKit;
- 20 GiB total research storage and 10 GiB selected-raw limits unchanged; and
- no scientific claim upgrade.

Engineering capability added: the replication lane now has an explicit,
machine-tested source acceptance gate that rejects incomplete peripheral
controls and ambiguous public releases before acquisition.

Scientific claim not established: this public-source pass did not test real
EEG, communication decoding, unseen-person generalization, EEG beyond eye or
mouth activity, independent replication, live decoding, or hardware use.

## Primary Sources

- [Thinking Out Loud descriptor](https://www.nature.com/articles/s41597-022-01147-2)
- [BrainStack paper](https://openaccess.thecvf.com/content/CVPR2026F/papers/Zhao_BrainStack_Neuro-MoE_with_Functionally_Guided_Expert_Routing_for_EEG-Based_Language_CVPRF_2026_paper.pdf)
- [BrainStack repository](https://github.com/Jacoo-Zhao/BrainStack)
- [BrainStack availability statement](https://github.com/Jacoo-Zhao/BrainStack/blob/main/Code_and_data_availability_statement.md)
- [BrainStack missing-loader issue](https://github.com/Jacoo-Zhao/BrainStack/issues/1)
- [Kara One official dataset page](https://www.cs.toronto.edu/~complingweb/data/karaOne/karaOne.html)
- [Directional Word descriptor](https://www.nature.com/articles/s41597-026-07809-9)
- [ArEEG descriptor](https://www.nature.com/articles/s41597-025-05387-w)
