# Ofner 2017 Motor-Imagery Fixed-Header Preregistration

Date: 2026-08-29

Protocol ID: `OFNER-C6R-1-HG0`

Status: **generated-only preregistration; no real-header authority**

## Decision Question

Can a dependency-free, target-blind parser recover the exact Ofner source-GDF
measurement contract from header bytes alone, while a range firewall proves
that no event table or signal sample can enter the operation?

This is the last generated engineering question before a separately governed
one-file real-header checkpoint. It is not a decoding experiment.

## Green Basis

Generated selector/acquisition commit
`527dffd0cc18a5259eeaba796f38774bbf1f472c` passed CI run
`33267249838`. Its proof-only closeout commit
`786b1249b6f9352136328bf9f289120a300472ad` passed Base Python job
`99141069026`, Optional Neuro Readers job `99141069150`, and CI run
`33267877803` on GitHub `main`.

No generated qualification was repeated during the proof closeout.

## Exact Member

One Tier A metadata-only request reverified the immutable NEMAR
`nm000173/v1.0.3` manifest. Its raw signed-URL surface was 1,352,270 bytes with
observed SHA-256
`57f8b18f01e0738da691ff35f90ce75d39f1096ffc01c594c811a73f33f3604d`.
After deleting only each row's volatile signed `url`, the canonical manifest
remained 748,162 bytes at the already frozen SHA-256
`5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34`.

The future checkpoint is bound to exactly:

- participant 1, motor-imagery run 1;
- `sourcedata/motorimagination_subject1_run1.gdf`;
- 105,365,484 declared bytes;
- full-payload SHA-256
  `ec334466272a936986a50c120c52c57634801f028acb0fee30705f8a2dee3087`;
- stable byte URL
  `https://data.nemar.org/nm000173/v1.0.3/sourcedata/motorimagination_subject1_run1.gdf`.

The expiring signed transport URL is never committed or published. The
temporary metadata body was deleted. No GDF byte was requested.

## Primary Format Basis

The official dataset description assigns channels 1-61 to EEG, 62-64 to EOG,
65-83 to the data glove, and 84-96 to the arm/exoskeleton, with 512 Hz
sampling. NEMAR publishes the corresponding 96 normalized channel names. The
BioSig GDF specification defines a mandatory 256-byte fixed header followed by
256 bytes per signal, with header length and signal count declared in the fixed
header.

Primary sources:

- `https://lampx.tugraz.at/~bci/database/001-2017/dataset_description.pdf`
- `https://nemar.org/dataset/nm000173`
- `https://arxiv.org/abs/cs/0608052`

## Frozen Generated Implementation

After this exact preregistration is committed, pushed, and remotely green,
Tier B permits one standard-library generated implementation that:

1. parses only GDF 2.x little-endian header fields frozen in the machine
   contract;
2. decodes no patient identifier, recording identifier, birthday, date, event,
   annotation, or signal sample;
3. requires a complete header and rejects trailing bytes;
4. verifies 96 unique normalized labels partitioned as 61 EEG, three EOG, 19
   glove, and 13 arm channels;
5. verifies 512 Hz from samples-per-record and rational record duration;
6. reports finite, nonzero EEG geometry coverage without making it an H1
   requirement;
7. validates mocked HTTP `206` range transcripts with no redirect, retry,
   compression, overlap, gap, or over-read; and
8. exposes no network client or real execution command.

The generated fixture contains header bytes only. It has no event table, data
record, target, label, or biological signal. Two deterministic replays and at
least 30 named malformed/refusal cases are required.

Generated limits are one CPU thread, one worker, 30 seconds, 256 MiB peak RSS,
1 MiB public output, 1 MiB private temporary output, zero network bytes, and
zero retained generated payload bytes.

## Future Real Proposal

This preregistration does not activate the proposal below. A later all-false
Tier C packet, its proof, a fresh packet-bound maintainer decision, and a green
decision commit are required first.

The proposed real checkpoint would refresh the exact manifest once in memory,
validate the member's stable identity and signed transport, then make exactly
two non-overlapping ranged requests against that one member:

1. `bytes=0-255` to read only the fixed header; and
2. `bytes=256-(header_length-1)` only if the fixed header declares a valid
   complete header no larger than 65,536 bytes.

The two GDF response bodies together may not exceed 65,536 bytes. Each response
must be uncompressed HTTP `206` with an exact `Content-Range`; redirects,
retries, fallbacks, substitutions, whole-file requests, and signal/event reads
are forbidden. The H1 result is only technical confirmation of the frozen
source representation. Any mismatch is H0 and permanently parks this exact
member checkpoint without rerun.

## Operation And Claim Boundary

This preregistration performed one 1,352,270-byte public metadata request,
strict canonicalization, selection of one stable member identity, primary
format research, tracked-file reads, documentation, and tests. It performed
zero GDF requests or bytes, header reads, events, annotations, targets, labels,
signal samples, training runs, model runs, predictions, scores, streams,
devices, releases, or claim upgrades.

Engineering capability added: NeuroDecodeKit now has a frozen, minimal-byte
design for proving the Ofner source representation without downloading a full
GDF or allowing event and signal data into the checkpoint.

Scientific claim not established: no real EEG was accessed or analyzed, so no
neural advantage, nuisance-controlled decoding, unseen-person generalization,
movement-intention, language, live, portable, or clinical result was shown.
