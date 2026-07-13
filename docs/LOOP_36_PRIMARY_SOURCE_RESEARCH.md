# Loop 36 Primary-Source Research: Geometry And Reference Harmonization

Date: 2026-07-12

Status: **planning research complete; experiment `Not Started`; unauthorized**

Machine boundary:
`registries/loop36_research_boundary.v0.json`

## Decision

Prepare a metadata-first identity and transform ledger, not a hidden
harmonization algorithm. A future Stage A may prove only that target-free
synthetic channel metadata can be normalized, refused, hashed, and replayed
under an exact schema. Real headers, signal-unit scaling, rereferencing,
compensation, interpolation, model transfer, and accuracy remain separate
authorization and claim levels.

The design has six representation layers, five modality profiles, a 24-field
future channel record, 12 operation classes, 16 future fixture families;
22 acceptance gates, 30 exact refusals, and 29 false authorization fields.

No fixture, real header, signal array, target, prompt, coordinate transform,
unit conversion, rereference, interpolation, model, training run, stream,
device, or hardware operation was opened by this research pass.

## Why This Loop Matters

NeuroDecodeKit currently has two conservative behaviors:

1. sentence caches preserve ordered channel names and selected MEG channel
   descriptions; and
2. cross-session evaluation requires exact ordered channel-name identity.

That prevents silent remapping, but it does not make heterogeneous files
comparable. The same label can refer to a different physical sensor, electrode,
reference, coordinate frame, or derived signal. Conversely, the same physical
location can be represented with different names, coordinate units, frames,
and channel order. Treating either case as obvious equivalence can manufacture
transfer or hide a real incompatibility.

Loop 36 therefore asks a narrower question than decoding: **Can exact identity,
units, geometry, transforms, reference state, and missingness be preserved and
compared without guessing?**

## Primary-Source Findings

### 1. Channel identity, electrode identity, and order are different fields

The [BIDS EEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)
requires channel name, type, and unit in the order represented in the recording.
It also separates recorded channels from physical electrodes: one bipolar EOG
channel may be derived from two electrodes, and auxiliary channels need not
have electrode rows. A channel ontology must therefore preserve both the
recorded signal identity and the physical sensor/electrode identity rather than
collapsing them into one name.

The [BIDS MEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetoencephalography.html)
distinguishes magnetometers, axial and planar gradiometers, MEG reference
sensors, EEG, EOG, EMG, triggers, audio, gaze, and other channel types. Equal
array length or a shared `MEG` label cannot justify mixing those types.

Decision:

- preserve the source index and source name;
- require source names and canonical names to be unique;
- allow canonical aliases only through an explicit, versioned, bijective map;
- never case-fold, strip punctuation, or map by position automatically; and
- refuse one-to-many, many-to-one, collision, and type-changing aliases.

### 2. Coordinate-system identity and coordinate units are separate

The [BIDS coordinate-system appendix](https://bids-specification.readthedocs.io/en/stable/appendices/coordinate-systems.html)
separately records origin/orientation through a named coordinate-system field
and distance units through a coordinate-units field. CTF, Neuromag/Elekta/
MEGIN, 4D/BTi, KIT/Yokogawa, CapTrak, and EEGLAB systems do not share one
implicit origin and axis convention. `Other` needs a description.

The [BIDS units appendix](https://bids-specification.readthedocs.io/en/stable/appendices/units.html)
recommends SI-compatible unit encoding. This supports exact declared conversion
factors, not magnitude-based guessing.

Decision:

- preserve original signal-unit and coordinate-unit strings separately;
- canonicalize coordinate distance only from declared `m`, `cm`, or `mm`;
- store the exact factor to metres;
- require signal units to be dimensionally compatible with channel type;
- never infer volts versus microvolts, tesla versus femtotesla, or metres versus
  millimetres from numerical magnitude; and
- keep unknown/custom units unavailable until their definition exists.

### 3. Device, head, and MRI coordinates need directional transforms

MNE's [source-alignment and coordinate-frame tutorial](https://mne.tools/1.8/auto_tutorials/forward/20_source_alignment.html)
distinguishes the MEG device frame, digitized head frame, and MRI frame. The
device-to-head relation comes from head-position information; the head-to-MRI
relation comes from coregistration. An identity matrix between unlike frames is
an incorrect assumption, not a neutral fallback.

The [`Transform` API](https://mne.tools/stable/generated/mne.transforms.Transform.html)
represents an explicit source frame, destination frame, and 4-by-4 matrix.
MNE also stores some frame identities as integer constants, so a bare integer
without its semantic mapping is insufficient for an exchange format.

Decision: a future rigid transform must record:

- source frame, destination frame, and direction;
- source standard/description, origin, axes, handedness, and units;
- the full homogeneous 4-by-4 matrix;
- transform source, method, fit partition, software/config, and hash;
- rotation orthogonality and determinant near `+1`;
- a forward/inverse position residual no larger than `1e-9 m` for synthetic
  fixtures; and
- separate application to positions and orientations, with no translation
  applied to orientation vectors.

A reflection, unexplained axis swap, unknown integer frame, missing orientation,
or ambiguous transform direction refuses.

### 4. Standard montages and measured positions are not interchangeable

MNE's [`DigMontage` documentation](https://mne.tools/stable/generated/mne.channels.DigMontage.html)
uses channel positions and fiducials and can transform a montage into the head
frame when sufficient landmarks exist. That operation depends on actual
coordinate semantics. A standard montage name can describe a nominal layout;
it does not prove where electrodes were placed for one recording.

Decision:

- retain whether coordinates are measured, nominal/template, transformed, or
  unavailable;
- never replace measured positions with a template silently;
- never claim measured geometry from a standard montage name alone; and
- preserve finite-value masks and missingness reasons per position and
  orientation component.

### 5. EEG reference is part of the signal definition

The [`mne.set_eeg_reference` documentation](https://mne.tools/stable/generated/mne.set_eeg_reference.html)
supports single-electrode, multi-electrode, average, REST, and channel-specific
references. Average and REST handling also depends on which channels are marked
bad. Rereferencing changes signal values; it is not a metadata rename.

Decision: preserve acquisition reference, ground, channel-specific exceptions,
bad-channel state, every derived reference operator, and whether the operator
was applied or stored as a projection. Unknown reference state blocks numerical
equivalence. A future rereference requires signal access and separate
authorization.

### 6. Interpolation is model-based imputation, not identity

MNE's [bad-channel interpolation example](https://mne.tools/stable/auto_examples/preprocessing/interpolate_bad_channels.html)
uses geometry and a declared EEG or MEG method to estimate missing signals. It
can fit an origin and construct a mapping matrix. This may be scientifically
useful, but it creates values that were not recorded by the missing channel.

Decision:

- interpolation and sensor-to-template remapping are data-changing operations;
- the original missing/bad status must survive after an interpolated value is
  created;
- the method, fit inputs, geometry, operator, and hash must be retained;
- zero-fill may encode missingness but may never be labeled equivalent signal;
  and
- no mapping may be selected by validation or final accuracy.

## Current Local Evidence

The current source tree and committed aggregate documents support the following
without reopening a protected payload:

| Local path | What exists | What remains unavailable |
|---|---|---|
| S21 sentence extraction | channel name, MNE type, `position_m`, integer coordinate frame, coil type, integer unit | named exchange-frame semantics, transform chain, orientation contract, compensation/projector equivalence |
| Loop 11 subset caches | within-cache spatial selection from the same six/102-channel geometry | cross-session or cross-device geometry equivalence |
| S21 cross-session runner | exact ordered channel-name equality requirement | any alias, reorder, reference, transform, or interpolation behavior |
| Consumed S7 EEG cache | 61 ordered EEG channel names | qualified measured electrode coordinates, acquisition reference/ground, derived reference chain |
| Loop 20 NeuroTokenCache | source names, position array, position mask, geometry availability | complete frame, orientation, unit, reference, and transform semantics |

No real cache or header was read to write this table. It is an audit of code,
committed contracts, and aggregate documentation.

## Future Representation

The proposed channel record has 24 fields covering:

- source/canonical identities and alias rule;
- channel type, status, sensor/electrode role;
- original and canonical signal units plus exact SI scale;
- position, orientation/baseline, component validity masks, and coil/electrode
  type;
- original/canonical coordinate units and source/destination frames;
- reference, ground, compensation, projector, and transform-chain identities;
- missingness reason; and
- source metadata hash.

Six representation layers keep source identity, channel identity, units,
geometry, coordinate transforms, and reference/linear mixing independently
inspectable. A higher layer cannot be synthesized from a lower layer.

## Operation Classes

| Operation | Classification |
|---|---|
| Exact unique reorder with explicit inverse | identity-preserving metadata operation |
| Explicit bijective alias | metadata compatibility only |
| Coordinate `m`/`cm`/`mm` scaling | identity-preserving with declared factor |
| Signal `V`/`mV`/`uV` or `T`/`fT` scaling | data transform requiring signal access |
| Known rigid frame transform | geometry identity for exact sensors and named frames |
| Reflection or unexplained axis swap | refusal |
| EEG rereference | data-changing linear operator |
| MEG compensation/projector change | data-changing linear operator |
| Bad-channel interpolation | model-based imputation |
| Sensor-to-template interpolation | model-based remapping |
| Missing-channel zero fill | missingness encoding only |
| Accuracy-selected mapping | forbidden evaluation leakage |

## Future Stages

### Stage A: target-free synthetic metadata

After a separate preregistration and authorization-only green commit, generate
16 small fixture families covering exact roundtrip, safe permutation, aliases,
units, rigid transforms, reflections, missing orientation/frame/reference,
interpolation provenance, and leakage refusals. Maximum claim: synthetic schema
and refusal identity.

Cap: one CPU thread, 120 seconds, 1 GiB peak RSS, 16 MiB generated artifacts,
zero downloads, zero model/training operations.

### Stage B: separately authorized real headers

Inspect only named header fields under exact file/byte/privacy caps without
opening signal arrays. Maximum claim: declared metadata compatibility or an
explicit unavailable/incompatible result. S20, S25, and consumed S7/S21 remain
closed unless their own exact packet authorizes a named header operation.

### Stage C: separately authorized signal transforms

Only when a frozen compatibility decision requires signal-unit scaling,
rereferencing, compensation, or interpolation may a new packet authorize a
named data-changing operation. It must bind fit scope, operator, missingness,
hashes, controls, resources, and downstream claim. Maximum result: protocol-
specific numerical compatibility. It does not establish model transfer.

## Acceptance And Stop Boundary

A future Stage A must pass all 22 gates and all 30 exact refusals. It must
report runtime, RSS, generated bytes, one-thread state, access counters,
warnings, unavailable fields, and source/config/transform/payload hashes.

Stop and publish unavailable or incompatible when:

- an alias is ambiguous, colliding, type-changing, or not bijective;
- units are absent, custom but undefined, or inferred from magnitude;
- a frame, transform direction, orientation, reference, compensation, or
  projector state is unknown;
- a transform is non-homogeneous, non-orthogonal, reflective, or fails
  roundtrip;
- a template replaces measured geometry;
- interpolation or zero-fill is presented as identity;
- evaluation accuracy selects a mapping; or
- any access, resource, hash, or claim cap fails.

## Measured Research Boundary

| Counter | Value |
|---|---:|
| High-level public web research operations | 3 |
| Protected dataset/model download bytes | 0 |
| Real headers read | 0 |
| Real signal/cache/target reads | 0 |
| Synthetic fixtures generated | 0 |
| Transforms or unit conversions applied | 0 |
| Rereference/interpolation/model/training runs | 0 |
| Device/stream/hardware operations | 0 |
| CPU threads used for local contract work | 1 |
| Generated experiment artifact bytes | 0 |

Public-network response bytes, browser runtime, and browser peak RSS are
unavailable from the research-tool contract. CPU time is not energy. The
user's 5-10 GB storage envelope is capacity only, not authorization.

## Claim Ladder

1. `L36-C0`: no new result, available now.
2. `L36-C1`: target-free synthetic schema/refusal identity, future Stage A.
3. `L36-C2`: declared real-header metadata compatibility, future Stage B.
4. `L36-C3`: coordinate/geometry compatibility for exact named sensors and an
   explicit transform chain.
5. `L36-C4`: protocol-specific numerical compatibility after a separately
   authorized signal transform.
6. `L36-C5`: cross-session or cross-device model transfer, not established by
   harmonization.
7. `L36-C6`: neural, device, population, or clinical equivalence, unavailable
   from this design.

## Exact Closeout Sentences

Engineering capability added: a machine-checkable planning boundary now
separates channel identity, units, geometry, coordinate transforms, reference,
interpolation, missingness, and compatibility claim levels.

Scientific claim not established: no fixture, real header, signal, transform,
rereference, interpolation, model, training run, target, or score was accessed,
so there is no geometry-compatibility, numerical-compatibility, model-transfer,
neural-advantage, cross-device, real-time, or portable-hardware result.
