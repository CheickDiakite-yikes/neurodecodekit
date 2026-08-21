# MARC2-VR20R Published Task-Identity Research

Date: 2026-08-21

Lane: `MARC2-VR20R`

Status: **Tier A primary-source research complete; no private or dataset
payload operation performed**

Registry: `registries/marc2_published_task_identity_research.v0.json`

## Executive Finding

The Freewill dataset's scientific concept and its BIDS task identity are not
the same string.

- The experiment is described as freewill reaching and grasping.
- The official archive is named `Freewill_EEG_Reaching_Grasping.zip`.
- The published raw BIDS files use the task entity
  `task-reachingandgrasping`.
- NeuroDecodeKit's MARC2 selectors instead require `task-freewill`.

That mismatch is the strongest evidence-backed explanation for the consumed
`MARC2VR18P-R4` result. VR19A proved from exact committed code that R4 implies
a task token other than lowercase `freewill`; the primary descriptor now
identifies the public dataset-wide token as `reachingandgrasping`.

This is a public-source diagnosis, not a private-source disclosure. The
consumed private manifest was not opened, listed, hashed, parsed, or inferred
row by row.

## Primary Sources

The 2025 Scientific Data descriptor gives the exact raw-file template:

```text
sub-xx/ses-yy/eeg/
sub-xx_ses-yy_task-reachingandgrasping_run-zzzz_eeg.eeg
sub-xx_ses-yy_task-reachingandgrasping_run-zzzz_eeg.vhdr
sub-xx_ses-yy_task-reachingandgrasping_run-zzzz_eeg.vmrk
sub-xx_ses-yy_task-reachingandgrasping_run-zzzz_events.tsv
```

It also names `task-reachingandgrasping_events.json`, uses four-digit examples
such as `run-0003`, and names derived session files
`sub-xx_ses-yy_task-reachingandgrasping_eeg.mat`.

Source: [Scientific Data descriptor](https://www.nature.com/articles/s41597-025-06039-9)

The official Figshare API confirms record `28632599`, version 1, DOI
`10.6084/m9.figshare.28632599.v1`, file `57518986`, archive name
`Freewill_EEG_Reaching_Grasping.zip`, 13,591,548,048 bytes, supplied and
computed MD5 `3b7c3039c5c9fb6abf1429a830301711`, and CC BY 4.0.

Source: [Figshare public metadata API](https://api.figshare.com/v2/articles/28632599)

The BIDS entity specification requires one `task-<label>` to remain
consistent across subjects and sessions. BIDS does not require that label to
equal the paper's colloquial paradigm name.

Source: [BIDS task entity](https://bids-specification.readthedocs.io/en/stable/appendices/entities.html#task)

## Local Causal Chain

The exact committed VR16A validator captures any alphanumeric task label, but
then normalizes each candidate through an older helper that requires
`freewill`. When the captured task is not `freewill`, that failed normalization
is translated to F04 / `core identity differs`.

The evidence chain is therefore:

1. VR18P consumed once at R4 after one target-free structural read.
2. VR19A proved R4 is produced by the non-`freewill` task guard, not by the
   identity counterexamples tested there.
3. The primary descriptor publishes `reachingandgrasping` as the exact task
   label for every raw quartet.
4. The old selector's `freewill` requirement is dataset-inaccurate.

The remaining uncertainty is no longer which public task label should be
accepted. It is whether an additive corrected selector can preserve every
source-exact identity, reservation byte, split, cap, and refusal invariant and
then pass one separately authorized private structural confirmation.

## Repair Decision

Do not edit or reinterpret consumed VR18P or any earlier frozen module. Build
an additive generated-only repair with these invariants:

1. Require exact lowercase `reachingandgrasping` as the dataset task entity.
2. Preserve source-exact task and run spellings in selected member names.
3. Accept the published four-digit run form and the already justified numeric
   BIDS run-index widths without normalized collisions.
4. Keep subject/session agreement, four-companion completeness, source
   immutability, deterministic rank/splits, and the 8 GiB reservation cap.
5. Reject `task-freewill`, case variants, generic alternate tasks, mixed task
   tokens, collisions, and incomplete bundles.
6. Add no private reader, executor, archive reader, model, scorer, or network
   client.

Only after an exact generated implementation and proof closeout are remotely
green may a separate Tier C packet request one target-free private structural
confirmation. A pass may freeze a cohort and make FW2 preregistration
eligible. It does not itself authorize archive members, neural signals,
targets, models, training, inference, or scoring.

## Boundary

Engineering insight established: NeuroDecodeKit's MARC2 blocker is a
dataset-task identity mismatch between inherited `task-freewill` logic and the
published `task-reachingandgrasping` BIDS filenames.

Scientific claim not established: no neural payload, target, model,
prediction, or score was accessed, so this research establishes no neural
effect, decoding accuracy, language decoding, live decoding, or thought-to-
text capability.
