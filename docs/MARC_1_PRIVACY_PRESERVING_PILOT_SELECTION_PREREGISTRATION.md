# MARC1-P1 Privacy-Preserving Pilot Selection Preregistration

Date: 2026-08-12

Status: **Generated-fixture-only contract frozen; implementation not started;
the sealed Freewill inventory and Wrist metadata remain unopened**

Registry:
`registries/marc1_privacy_preserving_pilot_selection_contract.v0.json`

## Decision

Task 4 will use a **12-person, two-axis pilot** selected before any private
archive row, target, event, or signal is inspected.

The pilot is intentionally larger than an eight-person convenience sample.
Twelve participant-level margins permit an exact exhaustive 4,096-assignment
sign-flip analysis, match the size of the positive WO9R confirmation cohort,
and remain compatible with the existing 8-GiB acquisition ceiling.

This contract does not read or authorize the real inventories. It freezes the
selector that must be qualified with generated rows before one later, separate
Tier C metadata-selection decision can exist.

## Green Evidence Anchor

The design is downstream of the one consumed `MARC1CD-R1` inventory. Exact
commit `7aee1287d1b5e4c91fde206e5a86cdee30df7ebf` passed Base Python job
`93883797813` and Optional Neuro Readers job `93883797816` in CI
`31522799476`.

The public result binds:

```text
Freewill archive bytes:         13,591,548,048
central-directory entries:     1,227
regular files / directories:   1,025 / 202
private inventory SHA-256:     2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031
canonical inventory SHA-256:   da0270a2d8f86106fe25e2246c1b969be448084b1a40c492c885580992c48d69
whole/member payload bytes:    0 / 0
```

The exact member rows remain private. This preregistration derives participant
eligibility only from the published source table and derives ranks only from
the two frozen DOI strings.

## Scientific Purpose

The pilot asks whether strictly pre-movement low-frequency scalp EEG carries
four-way movement-target information beyond timing and measured non-EEG
controls on both complementary axes:

- Freewill-23: target and movement time are self-selected after a generic
  audio cue; EOG and wrist acceleration are synchronized on the same
  amplifier.
- Wrist-45: direction is visually instructed; EMG and robotic encoders provide
  independent muscle and mechanical onset controls.

The future conjunction uses the weaker participant-level control-adjusted
margin. One-axis success cannot become the top scientific route.

## Cohort Rank Algorithm

Participant selection must not depend on member size, compression ratio, CRC,
run count beyond eligibility, signal quality, event count, target balance, or
an outcome.

For each source, compute:

```text
SHA256(UTF8(selection_seed) || 0x00 || UTF8(subject_id))
```

Sort by lowercase hexadecimal digest and then by subject ID. Select the first
12 eligible IDs. A different seed, separator, encoding, digest, case, tie
breaker, or post-hoc replacement refuses.

### Freewill-23

Selection seed:

```text
MARC1-P1|10.6084/m9.figshare.28632599.v1|participant-rank-v0
```

Published eligibility requires 250-Hz acquisition and at least two sessions
with at least three runs in both session 1 and session 2. This excludes the
single-session participants `sub-02` and `sub-17`, and the 1,000-Hz
participants `sub-13` and `sub-15`.

The frozen selected IDs, in hash-rank order, are:

```text
sub-08 sub-10 sub-07 sub-22 sub-19 sub-16
sub-14 sub-04 sub-05 sub-03 sub-09 sub-11
```

### Wrist-45

Selection seed:

```text
MARC1-P1|10.6084/m9.figshare.29666735.v3|participant-rank-v0
```

All source-declared IDs `sub-01` through `sub-45` are eligible before the
future metadata reconciliation. The frozen selected IDs are:

```text
sub-08 sub-11 sub-09 sub-23 sub-20 sub-16
sub-42 sub-38 sub-36 sub-30 sub-45 sub-21
```

The real selector must park rather than substitute if any selected participant
archive is absent, duplicated, malformed, or exceeds a frozen cap.

## Freewill Member And Split Contract

The future selector may inspect only the already retained, hash-bound private
central-directory manifest. It may not open a ZIP local header or payload.

For each selected participant:

- `ses-01` is the fit session;
- `ses-02` is the target-blind held-out session;
- sessions after `ses-02` are ignored;
- select the first three numerically ordered **complete** run bundles in each
  session; and
- never backfill a missing companion with a later run.

One complete run bundle has exactly four opaque members sharing one BIDS run
stem:

```text
_eeg.eeg
_eeg.vhdr
_eeg.vmrk
_events.tsv
```

This produces exactly 36 fit run bundles, 36 held-out run bundles, and 288
selected core members across 12 participants. The selector checks names,
types, compression metadata, sizes, CRC declarations, and offsets only. It
does not read an event row, header byte, marker byte, signal sample, target,
trial flag, comment, or movement onset.

Runs are selected by numeric run ID only. Member size and CRC may enforce the
cap after selection but may never change the cohort, session, run, or split.

## Wrist Member And Split Contract

The future metadata selector may accept one separately authorized, bounded
Figshare v3 metadata body. It selects exactly one participant-level archive
for each frozen ID and no derivative-only, code-only, or replacement archive.

Within each later acquired participant archive:

- runs 1 through 6 are fit runs;
- runs 7 and 8 are target-blind held-out runs; and
- the source-declared balance yields 240 fit and 80 held-out trials per
  participant, with 60 fit and 20 held-out trials per direction.

Across the pilot this is 72 fit runs, 24 held-out runs, 2,880 expected fit
trials, and 960 expected held-out trials. These are source-design
expectations, not permission to open an archive or target.

## Target Firewall

Pilot selection is target-free. The selector must have no event parser,
neurophysiology reader, archive extraction method, model, or scorer.

A later analysis must physically separate:

1. fit signals and fit targets;
2. held-out signals without held-out targets or control streams;
3. hash-frozen predictions; and
4. one isolated delivery of the same held-out targets and controls after the
   prediction freeze is committed, pushed, and remotely green.

No target, event count, bad-trial flag, movement onset, file content, signal
quality value, or technical-validation outcome may influence selection.

## Storage And Computer Budget

The future metadata-selection audit remains tiny:

```text
private Freewill manifest reads:    1
private Freewill manifest bytes:    418,755 exact
Wrist metadata response bodies:     1
Wrist metadata body cap:            2 MiB
member/local-header/payload reads:  0
generated/private output cap:       2 MiB
aggregate public output cap:        1 MiB
runtime / peak RSS:                 30 sec / 256 MiB
CPU threads / workers / jobs:       1 / 1 / 1
```

A later acquisition is eligible only if the frozen selected payload fits all
of these ceilings without substitution:

```text
Freewill network allocation:        <= 6 GiB
Wrist network allocation:           <= 2 GiB
combined network payload:           <= 8 GiB
combined incremental disk:          <= 8 GiB
free disk before acquisition:       >= 12 GiB
private derivatives:                <= 64 MiB
```

For each Freewill member, the network reservation includes compressed size
plus `30 + UTF-8 name bytes + 65,535` bytes for the still-unread local header.
There is no optimistic compression assumption. If either source or the joint
cap fails, route to a measured refusal; do not reduce the cohort, swap a
participant, drop a companion, or increase the budget.

## Privacy Contract

The generated selector and a future real selector produce two surfaces:

- a private mode-`0600` exact selection manifest containing member/archive
  identities, offsets, sizes, CRC declarations, and source hashes; and
- an aggregate public result containing the preregistered participant IDs,
  counts, byte totals, split totals, canonical hashes, warnings, and route.

The public result may not expose a Freewill member name, local-header offset,
CRC, raw URL, Wrist file ID, Wrist archive name, local path, raw response body,
or raw header. The selected participant IDs are public because this document
freezes them before metadata access.

## Generated Qualification

After this exact contract is committed, pushed, and both CI jobs are green, a
dependency-free Tier B implementation may use only generated inputs:

- exactly 1,227 generated Freewill inventory rows;
- exactly 55 generated Wrist metadata rows;
- all 19 published Freewill-eligible and 45 Wrist IDs;
- exactly 72 selected Freewill run bundles and 288 core members;
- exactly 12 selected Wrist participant archives;
- deterministic replay under irrelevant row reordering;
- cap-boundary and privacy checks; and
- exactly 36 adversarial mutations.

The generated module may expose only `plan`, `qualify`, and aggregate
`inspect`. It may not expose a real path, URL, host, participant override,
seed override, size override, execute, archive-open, target, model, or score
argument.

## Router

1. `MARC1PSG-F00`: contract, artifact, or green-proof mismatch.
2. `MARC1PSG-F01`: private inventory identity, schema, count, or mode failure.
3. `MARC1PSG-F02`: unsafe path, unsupported member, or incomplete run bundle.
4. `MARC1PSG-F03`: eligibility, hash rank, participant count, run, or split
   failure.
5. `MARC1PSG-F04`: source or joint byte-cap failure.
6. `MARC1PSG-F05`: Wrist metadata identity, participant archive, or count
   failure.
7. `MARC1PSG-F06`: privacy, output, overwrite, runtime, RSS, or replay failure.
8. `MARC1PSG-R1`: every generated selection gate passes.

`MARC1PSG-R1` is implementation evidence only. It does not authorize the
private manifest read, Wrist metadata request, member access, acquisition,
signal processing, target delivery, training, inference, or scoring.

## Acceptance Gates

The generated closeout is eligible only if:

- both DOI-bound participant rankings replay exactly;
- the Freewill fixture has 1,227 rows and the Wrist fixture has 55 rows;
- exactly 12 participants are selected per source;
- exactly 72 complete Freewill bundles and 288 members are selected;
- Freewill fit/held-out sessions and Wrist fit/held-out runs are exact;
- selection is invariant to irrelevant row ordering;
- sizes and CRCs cannot affect rank or split;
- no event, target, local header, payload, signal, model, or score interface
  exists;
- all source and joint caps pass or refuse without fallback;
- private and aggregate outputs remain separated;
- all 36 mutations refuse in the intended class;
- deterministic replay is byte-identical;
- runtime, RSS, output, and one-thread caps pass; and
- every real-data, neural, target, model, score, and claim counter is zero.

## Next Gate

1. Commit and push this exact contract.
2. Require Base Python and Optional Neuro Readers to pass at that commit.
3. Implement and qualify the generated-only selector.
4. Commit and push the exact implementation and require both jobs green.
5. Only then prepare an all-false Tier C packet for one private Freewill
   manifest read and one bounded Wrist metadata body.

The current maintainer continuation is not retroactive authority for step 5.
A fresh packet-bound decision is required after one exact packet is green and
identified as the sole active Tier C gate.

## Claim Boundary

Engineering capability added if successful: NeuroDecodeKit can choose a
scientifically meaningful, storage-bounded two-axis pilot deterministically
without using target, signal, quality, or outcome information.

Scientific claim not established even if successful: generated selection
metadata contain no human neural signal, model prediction, or score and
establish no neural effect or decoding capability.
