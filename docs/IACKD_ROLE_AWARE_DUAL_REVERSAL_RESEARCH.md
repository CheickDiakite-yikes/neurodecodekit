# IACKD Role-Aware Dual-Reversal Research

Date: 2026-08-10

Status: **Tier A research complete; a public channel-role audit is recommended
before a new scientific preregistration; no new public body, retained bundle,
sibling, sample, event, trajectory, target, model, prediction, or score was
accessed**

Registry:
`registries/iackd_role_aware_dual_reversal_research.v0.json`

Research sequence:

1. **IACKD-H2 Channel Role and Geometry Audit**
2. **IACKD-2 Role-Aware Dual Reversal**

## Decision In One Sentence

Measure channel roles and geometry from the 316 tiny public BIDS metadata
files, then test action-versus-cue alignment in two symmetric reversal arms so
an action-bound representation must survive both mapping changes.

## What IACKD-H1 Changed

The consumed IACKD-1 reader assumed exactly 36 declared channels and required
M1, M2, HEOG, and VEOG in every run. IACKD-H1 has now measured all 128 public
VHDR declarations:

| Headers | Declared channels | M1/M2 | HEOG/VEOG/TRIGGER | Rate |
|---:|---:|:---:|:---:|---:|
| 96 | 29 | absent | present | 1024 Hz |
| 32 | 31 | present | present | 1024 Hz |

This is a complete engineering diagnosis at `IACKDH-R5`. It does not reveal
channel types, reference, geometry, bad-channel status, or signal quality. The
29 and 31 totals must not be called EEG-channel counts.

The result commit `a6704898cfb09f6321bac5f15e27424f02614317` passed Base
Python job `93575925675` and Optional Neuro Readers job `93575925695` in CI
`31425445891` before this research record was prepared.

## The Reader Failure Was Deeper Than One Number

A target-free audit of the consumed implementation found four coupled
assumptions in
`src/neurodecodekit/experiments/iackd_cue_action_dissociation.py`:

1. `load_run_from_bundle` requires 36 source channels before reading the BIDS
   channel table.
2. `_validate_channels_tsv` accepts only 32 or 34 rows typed as EEG.
3. the constructed channel types mark every name other than M1, M2, HEOG, and
   VEOG as EEG, which would include the now-observed TRIGGER channel; and
4. the generated qualification fixture contains 32 synthetic EEG channels and
   four auxiliaries but no trigger channel.

Changing only `36` would therefore create a second silent role error. The
consumed module must remain unchanged as evidence. A future reader needs a new
role-first contract and a new module.

## Why BIDS Metadata Must Lead

The IACKD article describes a 32-channel cap and separately identifies M1, M2,
HEOG, and VEOG as non-EEG channels removed by the authors' preprocessing. It
does not reconcile that description with the converted 29/31-channel
BrainVision declarations.

The BIDS 1.7 EEG specification makes `name`, `type`, and `units` the required
channel-table fields, says channel rows should follow source order, and
explicitly distinguishes channels from physical electrodes. It also warns
that `channels.tsv` and `electrodes.tsv` need not have identical entries. The
sidecar separately carries sampling frequency, reference, and optional
channel-count declarations.

MNE 1.12.1 does not remove this ambiguity. Its BrainVision reader uses a
default EOG-name tuple that does not include IACKD's exact HEOG/VEOG names, and
its `misc="auto"` behavior infers miscellaneous channels from source units.
The corrected reader must therefore cross-check source order and use explicit
BIDS roles rather than accepting MNE's inferred types as ground truth.

Primary sources:

- [IACKD data descriptor](https://doi.org/10.1038/s41597-026-07146-x)
- [BIDS 1.7 EEG specification](https://bids-specification.readthedocs.io/en/v1.7.0/04-modality-specific-files/03-electroencephalography.html)
- [MNE 1.12.1 BrainVision reader](https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html)
- [OpenNeuro ds006840 v1.0.0](https://openneuro.org/datasets/ds006840/versions/1.0.0)

## IACKD-H2: The Smallest Decisive Audit

The committed OpenNeuro inventory contains the complete next surface:

| Role | Objects | Bytes | Per-object range |
|---|---:|---:|---:|
| `channels.tsv` | 128 | 227,904 | 1,752-1,866 |
| `eeg.json` | 128 | 173,312 | 1,354 |
| `electrodes.tsv` | 30 | 27,316 | 890-967 |
| `coordsystem.json` | 30 | 29,070 | 969 |
| **Total** | **316** | **457,602** | **890-1,866** |

The canonical identity serialization is 53,367 bytes with SHA-256
`0a63b46395030cb967dbca05f37a1367cf2bb0bf1088befce378a3556eab2274`.
The channel tables themselves have two size groups: 96 at 1,752 bytes and 32
at 1,866 bytes. That count match is a metadata observation, not proof of their
contents or run-level pairing.

The H2 audit should fetch and parse only those 316 public bodies. It should
never request a VHDR again, resolve a BrainVision sibling, or inspect the
retained local bundle.

### Strict parsers

The standard-library parser should require:

- unique normalized channel names and exact source order;
- BIDS `name`, `type`, and `units` fields in every channel row;
- only registered uppercase BIDS channel types;
- finite numeric sampling declarations and internally consistent count fields;
- unique electrode names with numeric or explicit unavailable coordinates;
- a declared EEG coordinate system and unit for every electrode table; and
- exact subject/hand/run membership from the committed metadata inventory.

It should reject duplicate JSON keys, malformed TSV quoting, unexpected
columns that alter required semantics, nonfinite numbers, control characters,
path drift, response drift, redirects, compression, oversized bodies,
duplicates, omissions, retries, and overwrites.

### Aggregate output

One public ledger may contain:

- each unique ordered `(name, type, units)` channel schema and occurrence
  count, without source paths;
- aggregate sidecar values for sampling, reference, recording type, and
  declared type counts;
- exact presence and declared roles for M1, M2, HEOG, VEOG, TRIGGER, C3, C4,
  Cz, O1, Oz, and O2;
- counts of good, bad, and unavailable source statuses without run identity;
- geometry coverage counts and hashes, never coordinate values;
- channel/electrode intersection counts, preserving the BIDS rule that the
  two tables need not be identical; and
- every warning, unavailable field, resource measure, and access counter.

Descriptions, instructions, device serials, fiducial coordinates, electrode
coordinates, individual status rows, participant outcomes, and source paths
must not be published.

### H2 diagnostic router

| Route | Meaning |
|---|---|
| `IACKDR-R0` | Source identity, response, strict parse, or completeness fails. |
| `IACKDR-R1` | BIDS channel roles or sidecar counts contradict the H1 declarations. |
| `IACKDR-R2` | Predictive scalp roles vary beyond a registered optional auxiliary set. |
| `IACKDR-R3` | Roles are stable, but central/occipital geometry or reference metadata is insufficient. |
| `IACKDR-R4` | A stable count-agnostic role map and required geometry are available for a prospective reader. |

No route opens a signal or authorizes IACKD-2.

## Role-First Sensor Contract

The future reader should produce one immutable `SensorRoleMap` before any
signal sample is materialized:

```text
source_order_hash
predictive_EEG_names
recorded_EOG_names
trigger_names
optional_reference_or_mastoid_names
source_status_mask
geometry_available_mask
reference_scheme
sampling_rate_hz
role_map_hash
```

The policy is deliberately count-agnostic:

- predictive EEG is selected by the frozen BIDS role map, not by subtracting a
  guessed number of auxiliaries;
- HEOG and VEOG remain a separate recorded peripheral control;
- TRIGGER never enters an EEG feature matrix;
- M1/M2 availability is a run property and cannot change the primary role
  policy after outcomes are known;
- geometry is required only for the registered predictive and regional EEG
  views, not for EOG, trigger, or an absent optional contact;
- channels and electrodes join by exact normalized name without requiring the
  tables to be the same size; and
- every derivative, model, prediction, and receipt binds the role-map hash.

The public H2 result, not a target, model score, or local post-failure
inspection, decides the eventual channel contract.

## IACKD-2: Symmetric Dual Reversal

The original scientific idea remains strong: direction of the hand and
direction of the visual target are forced to disagree on incongruent trials.
The improved design makes the reversal symmetric.

For each participant-hand unit, the highest-numbered run remains the only
sealed final run. Earlier runs remain the only fit runs. Two models use the
same fixed feature family and differ only in fit condition:

| Arm | Fit rows | Final rows | Fit relation | Frozen cue surrogate on final |
|---|---|---|---|---|
| `C2I` | congruent | incongruent | `action = visual` | `+visual = -action` |
| `I2C` | incongruent | congruent | `action = -visual` | `-visual = -action` |

Each model is fitted to actual hand direction in its fit partition. Final
predictive code receives no hand direction, visual direction, color-derived
label, signed ball displacement, signed Leap displacement, or outcome.

After every prediction freezes, the scorer applies two exact-opposite target
views to the same prediction:

1. actual hand direction; and
2. the visual direction transformed by the arm's frozen fit relation.

If the representation is action-bound, it must align with hand direction in
both arms. If it merely transfers the visual mapping learned in the fit
condition, it aligns with the cue surrogate and opposes the hand in both arms.
Requiring both arms prevents one color condition or one mapping direction from
carrying the conclusion.

## Fixed Scientific Views

After H2 freezes the available sensor names, one later preregistration should
define all views together:

- role-mapped whole-scalp low-frequency EEG;
- central C3/C4/Cz EEG;
- an occipital O1/Oz/O2 visual proxy if H2 confirms all three;
- HEOG/VEOG only;
- fit-only EOG-orthogonalized scalp EEG;
- early and late halves of the one-second pre-movement interval;
- pre-window, timing-only, and train-only no-signal baselines;
- all-zero, label-deranged, displaced-row, channel-permuted, and opposite-hand
  controls; and
- nonselecting readiness-potential and mu/beta summaries.

The compact 0.5-4 Hz causal feature family remains the primary continuity arm
because it is the representation implicated by WO9R. A later contract may add
one fixed mu/beta diagnostic, but no architecture search, deep network,
foundation model, language model, or post-target selection belongs in this
experiment.

## Prospective Evidence Conjunction

Exact thresholds belong in the post-H2 preregistration, but the primary logic
is fixed now:

1. both `C2I` and `I2C` must exceed chance for action direction;
2. both must prefer action over their exact-opposite cue surrogate;
3. participant-level inference, not pooled trial count, determines
   significance;
4. the central view and fit-only EOG-orthogonalized view must preserve the
   action margin;
5. EOG-only, occipital, timing, pre-window, and derangement controls may not
   explain the primary effect;
6. all predictions and controls freeze before the two final target views open
   once; and
7. neither arm may rescue failure of the other.

A useful primary statistic is the participant-level minimum of the two arm
margins:

```text
min(
  BA_C2I(actual_hand) - BA_C2I(cue_surrogate),
  BA_I2C(actual_hand) - BA_I2C(cue_surrogate)
)
```

This makes symmetry part of the estimand instead of a favorable secondary
analysis.

## Resource Strategy

The immediate H2 audit can stay within:

```text
requests / expected bytes:   316 / 457,602
network body cap:            2 MiB
incremental disk cap:        4 MiB
public output cap:           2 MiB
wall time:                   180 seconds
peak RSS:                    256 MiB
threads / workers / jobs:    1 / 1 / 1
retries / reruns:            0 / 0
minimum free disk:           2 GiB
```

IACKD-2 should reuse the already retained, isolated bundle only after a new
exact Tier C decision. It needs zero new payload bytes and should stream one
run at a time, persist no raw windows, and keep private derivatives under the
existing 512 MiB ceiling. Exact fit and inference counts remain deliberately
unfrozen until H2 establishes the sensor views.

## Ordered Next Work

1. Commit and remotely green this research record.
2. Freeze an IACKD-H2 preregistration binding exactly 316 objects and 457,602
   bytes.
3. Implement strict parsers, aggregate router, resource guards, and a module
   CLI using generated fixtures and mocked transport only.
4. Commit and remotely green that exact implementation.
5. Prepare one all-false Tier C request for the public metadata bodies.
6. After a fresh packet-bound decision is committed and remotely green, run
   H2 once and stop.
7. Use only the aggregate H2 result to freeze IACKD-2's exact role map,
   symmetric prediction matrix, gates, and resource counts.
8. Require a separate exact Tier C decision before any retained-bundle,
   sibling, signal, event, trajectory, target, model, prediction, or score
   operation.

## Claim Boundary

Engineering capability proposed: a role-first sensor contract and symmetric
dual-reversal design can replace a brittle channel count and distinguish
action alignment from transfer of a visual mapping in two opposing directions.

Scientific claim not established: no new public metadata body, retained EEG,
event, trajectory, target, model, prediction, or score was accessed, so this
research establishes no new neural effect, action decoding, brain-specific
origin, unseen-person generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.
