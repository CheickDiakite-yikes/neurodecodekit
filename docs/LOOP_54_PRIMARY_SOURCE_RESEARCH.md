# Loop 54 Primary-Source Research: EEG Trial Geometry And Confound Ledger

Date: 2026-07-16

Status: **planning research complete; acquisition dependent; experiment `Not Started`;
unauthorized**

Machine boundary:
`registries/loop54_eeg_trial_geometry_research.v0.json`

## Decision

Do not send the current BrainVision extraction function directly into a fresh
EEG scientific gate. The existing function is a useful engineering bridge, but
it reads marker annotations, MAT labels, and EEG signal in one invocation,
removes channels whose names contain `EOG`, and writes plaintext labels into the
cache. That is incompatible with the target isolation and peripheral-control
evidence required for Loop 55.

Loop 54 will instead use four ordered future stages:

1. strict VHDR-only identity and declared-geometry metadata;
2. target-blind VHDR plus EEG signal-quality and channel-preservation audit;
3. isolated target-bearing VMRK plus MAT trial reconciliation; and
4. aggregate immutable closeout with a fail-closed claim ceiling.

Each real content stage requires its own exact Tier C decision after a clean
Loop 53 acquisition receipt. This research pass does not implement or authorize
those readers. It does not touch a local S20 path or payload.

## Why This Changes The Plan

The previous one-line roadmap description said "headers and then signal/target
members in a separately ordered pass." That is directionally correct but not
strict enough. In BrainVision, the header names the marker file, and common
readers resolve the triplet for convenience. A call that appears to read only
the `.vhdr` can therefore expose marker annotations and their descriptions.

That matters scientifically because a marker has two different roles:

- its position says **when** an event happened; and
- its type and description can say **what** happened.

For this typing task, "what" can be a key, response, condition, or trial label.
The VMRK is therefore target-bearing until inspection proves otherwise. It
cannot be grouped with target-free geometry merely because it is a small text
file.

## Current Proof Boundary

What is proven now:

- Loop 53 prospectively binds S20 session 2 block 2 at pinned revision
  `88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684`;
- the prospective bundle contains one VHDR, one EEG, one VMRK, and one MAT file
  totaling `96,090,264` bytes in public metadata;
- Loop 35 defines the peripheral and task-locked confound firewall;
- Loop 36 defines the channel, unit, geometry, transform, and reference
  firewall; and
- this pass audits the committed BrainVision extraction code and six primary
  sources without protected access.

What is not proven now:

- the S20 payload is not acquired under Loop 53;
- no local S20 path was stated, hashed, parsed, or opened;
- no S20 channel, sampling, geometry, reference, quality, event, trial, or
  target field is known from file content;
- no cache, split, model, training, inference, scoring, or latency run exists;
  and
- no neural, sensor-signal, decoding, real-time, portable, home, or clinical
  result exists.

## Primary-Source Findings

### 1. BrainVision is three linked files with different sensitivity

Brain Products defines the BrainVision Core Data Format as:

- a text `.vhdr` containing recording parameters and metadata;
- a text `.vmrk` describing events collected during recording; and
- a binary `.eeg` containing EEG and additional recorded signals.

Source: [BrainVision Core Data Format 1.0](https://www.brainproducts.com/support-resources/brainvision-core-data-format-1-0/)

Decision: preserve the triplet relationship, but authorize and audit each
content role separately. A complete triplet is a file-integrity requirement,
not permission to parse all three members together.

### 2. Marker descriptions encode event meaning

Brain Products documents marker number, type, description, position, size, and
channel number. Type and description express what happened; position expresses
when it happened on the EEG timeline.

Source: [How to design trigger codes to obtain accurate markers](https://pressrelease.brainproducts.com/trigger-code-design/)

Decision: marker position is task-locked timing and marker description is
potentially a protected behavior or target. Both are outside target-free Stage
A and Stage B. Public Loop 54 output may report aggregate counts and residuals,
but not plaintext descriptions, keycodes, responses, sentences, or trial text.

### 3. `preload=False` does not make MNE marker-blind

MNE's official `read_raw_brainvision` documentation says BrainVision marker
type and description become annotations on the returned `RawBrainVision`.
`preload=False` controls signal preloading; it does not promise a VHDR-only
metadata operation. MNE also uses channel names and header units to designate
EOG and miscellaneous channels.

Source: [`mne.io.read_raw_brainvision`](https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html)

Decision: MNE is disallowed in Stage L54-A. It needs a small strict text parser that
opens exactly one authorized VHDR path, refuses external or symlinked sibling
resolution, and records only an allowlisted field set. MNE remains an optional
dependency elsewhere in the project.

### 4. Channels, electrodes, references, and geometry are not synonyms

BIDS EEG requires channel name, type, and unit, recommends preserving channel
order, and keeps electrode positions in a separate table. It also distinguishes
global acquisition reference from channel-specific reference and separates EEG,
EOG, EMG, trigger, gaze, and other channel types.

Source: [BIDS EEG specification 1.11.1](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)

Decision:

- retain source index and source name exactly;
- separate declared type from inferred type and record the evidence for either;
- preserve resolution, unit, and reference strings without magnitude guessing;
- do not synthesize measured geometry from a standard montage name;
- keep coordinate frame, orientation, global reference, ground, and bad status
  unavailable unless directly declared; and
- retain every channel through the confound audit.

### 5. Event timing and event content remain separate fields

BIDS describes events as stimuli, participant responses, or other incidents and
permits them in one event table. Onset and duration describe timing, while
condition, response, and additional columns can carry behavioral content.

Source: [BIDS Events specification 1.11.1](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/events.html)

Decision: a future public reconciliation ledger can expose opaque trial IDs,
event counts, and timing residual summaries. The raw marker descriptions,
keycodes, typed responses, target sentences, and label arrays stay in an
ignored isolated derivative and never enter Git, stdout, logs, exceptions, or
public cache metadata.

### 6. Published cohort facts are not S20 file evidence

The Brain2Qwerty paper reports an actiCAP slim system with 64 channels: 61 EEG
and three ocular channels, sampled at 1 kHz. It reports two blocks of 64 unique
sentences per session and 500 ms windows around known keypresses. EEG averaged
65% CER versus 29% for MEG in the published large model; the best and worst EEG
participants were still reported at 61% and 69% CER.

Source: [Noninvasive decoding of typed sentences from human brain activity](https://www.nature.com/articles/s41593-026-02303-2)

Decision: use those values only as cohort and method context. Do not prefill the
S20 ledger with 64 channels, three ocular channels, 1 kHz, 64 trials, or any
performance expectation. Every S20-specific field stays unavailable until its
authorized stage reads the exact file.

## Current Code Audit

Audited path:
`src/neurodecodekit/preprocess/brainvision_extraction.py`

Frozen audit identity:

```text
SHA-256: 6aa8fcfff84a165cd88432bfd27ced3bab36af254261b28642ae12d9529ef7e9
Git blob: ee19bb28c8cd499f7774fcd89b08be86e2937e0b
```

The current `extract_brainvision_mat_windows` function:

- calls `mne.io.read_raw_brainvision(..., preload=False)` at line 206;
- removes names containing `EOG` at line 212;
- reads MNE annotations and MAT events in one invocation at lines 218-219;
- calls `scipy.io.loadmat` over the MAT payload at line 428; and
- writes plaintext labels and trial indices into the output at lines 374-379.

This was acceptable for the consumed Loop 19 engineering bridge. It is not a
fraud or a bug in that historical proof boundary. It is simply not eligible for
the future Loop 54/55 claim path.

The future replacement must have four properties:

1. a dependency-light VHDR parser that cannot open VMRK or EEG siblings;
2. a bounded direct EEG reader driven only by validated binary metadata;
3. complete channel preservation with declared, inferred, and unavailable
   types separated; and
4. an isolated VMRK/MAT reconciler whose public output cannot reveal targets.

## Sensitivity Classes

| Class | Content | Target-bearing? | Public output rule |
|---|---|---:|---|
| `L54-D0` | contract hashes, paths, caps | no | allowed |
| `L54-D1` | VHDR binary and channel declarations | no | allowlist only |
| `L54-D2` | EEG samples and quality summaries | samples sensitive, not targets | aggregate summaries only |
| `L54-D3` | marker positions and response timing | yes, task-locked | aggregate or opaque IDs only |
| `L54-D4` | marker descriptions, keycodes, responses, sentences | yes | protected isolated derivative only |

"Target-free" is not the same as "nonsensitive." Raw EEG remains sensitive
neural data even when it contains no target text. Loop 38 privacy and lifecycle
rules continue to apply.

## Future Stage L54-A: Strict VHDR Ledger

### Inputs

Exactly one authorized VHDR regular file. No sibling path may be resolved or
opened. The referenced data and marker basenames may be recorded as strings but
not followed.

### Allowed fields

- format version and text encoding declaration;
- data and marker basenames;
- data format and orientation;
- binary format;
- declared channel count;
- sampling interval and derived sampling rate;
- ordered channel names;
- channel-specific declared reference, resolution, and unit;
- impedance section availability; and
- filter metadata availability.

### Forced unavailable fields

Unless directly declared in the one VHDR, channel type, measured position,
coordinate frame, orientation, global acquisition reference, ground, bad status,
EOG/EMG identity, event count, trial count, and target text stay unavailable.

### Caps

One thread, one worker, 30 seconds, 256 MiB peak RSS, and 1 MiB output.

## Future Stage L54-B: Target-Blind Signal Quality

### Inputs

The accepted VHDR ledger plus exactly the VHDR and EEG files. VMRK and MAT are
forbidden. The reader must use validated binary orientation, sample width,
channel count, and scale without resolving the marker file.

### Required behavior

- retain every channel, including every possible ocular or auxiliary channel;
- stream or memory-map within the 1 GiB RSS limit;
- report sample count, duration, finite and exact-zero fractions;
- report per-channel min, max, mean, standard deviation, RMS, median, MAD, and
  peak-to-peak values;
- report flat, extreme-outlier, clipping, and 50/60 Hz line-noise evidence;
- report three fixed target-blind temporal probe summaries; and
- emit no raw signal derivative.

### Forbidden transformations

No EOG exclusion, channel deletion, rereference, interpolation, ICA, filtering,
resampling, baseline correction, or target-aligned windowing. This is a source
quality audit, not preprocessing selection.

### Caps

One thread, one worker, 120 seconds, 1 GiB peak RSS, and 8 MiB output.

## Future Stage L54-C: Isolated Trial Reconciliation

### Inputs

Exactly VHDR, VMRK, and MAT in an isolated process. EEG signal is forbidden.
The trial and event rules must be frozen before this stage opens.

### Public result

- opaque trial identity commitments;
- event and trial counts;
- timing-residual summaries;
- per-trial event counts;
- alignment status;
- warnings, unavailable fields, hashes, and resource/access counters.

### Protected result

Marker descriptions, keycodes, typed responses, target sentences, trial text,
and label arrays may exist only in an ignored isolated derivative needed for a
future separately preregistered Loop 55. They may not appear in stdout, public
JSON, Markdown, Git, logs, exception text, filenames, or cache metadata.

### Caps

One thread, one worker, 120 seconds, 512 MiB peak RSS, and 8 MiB output.

## Future Stage L54-D: Qualification Closeout

Stage D reads only the aggregate public outputs from A, B, and C. It opens no
raw payload and no protected derivative. It emits one immutable result and one
of two decisions:

- `eligible_for_prospective_loop55_preregistration`; or
- `park_with_measured_reason`.

It does not create a split, choose a model, train, infer, score, or upgrade a
claim.

## Trial And Split Firewall

Loop 54 accepts only if at least 48 unique performed trials have unambiguous
identity. A keypress window is not an independent trial. All windows from one
trial must remain grouped in every future partition and uncertainty calculation.

Loop 54 does **not** create train, validation, or final splits. Exact Loop 55
counts cannot be frozen until the target-blind usable-trial count exists. Once
that count is known, Loop 55 needs a separate prospective contract that freezes:

- exact trial-group counts;
- semantic text grouping rules;
- model and comparator identities;
- target-access order;
- prediction-freeze order;
- paired uncertainty at the trial unit; and
- terminal pass/fail rules.

If fewer than 48 unique performed trials survive, Loop 55 parks without
training. If the count or ordering requires a protocol change, the amendment
must be committed, pushed, and remotely green before targets or models open.

## Geometry And Confound Ceiling

The future ledger records 21 channel fields and ten confound fields. It inherits
the Loop 35 and Loop 36 rule that unknown means unavailable, never harmless.

Required confound status includes:

- EOG recording and exact channel identity;
- EMG availability;
- motion availability;
- gaze availability;
- audio availability;
- trigger or response timing;
- keypress identity;
- visual feedback schedule;
- overt typing task status; and
- every known unmeasured confound.

Missing EOG, EMG, motion, gaze, or audio does not necessarily make a future
sensor-signal test impossible. It does block a brain-specific attribution.
Even a positive Loop 55 could then claim at most dependence on the recorded EEG
sensor array beyond the controls that were actually measured.

## Acceptance Gates

The machine registry freezes 22 future gates. The decisive conjunction is:

- clean Loop 53 receipt first;
- separate exact authorization for every real content stage;
- no hidden file resolution;
- no MNE in Stage A;
- all channels retained in Stage B;
- no VMRK/MAT access before Stage C;
- no plaintext protected values in public output;
- at least 48 unambiguous trial identities;
- all geometry, reference, and confound fields known or unavailable;
- no split, model, training, inference, scoring, or claim selection;
- one thread and one worker;
- at most 1 GiB peak RSS per stage;
- at most 32 MiB combined public generated output; and
- claim language no stronger than trial and confound qualification.

Any failed gate parks the affected stage. A missing peripheral stream narrows
the future claim; an identity, target-isolation, or trial-count failure blocks
Loop 55 entirely.

## Relationship To The Scientific Goal

Loop 54 does not chase a result. It makes a future result interpretable.

The closest honest next scientific claim remains:

> On one fresh person's S20 EEG block, a model frozen before final target access
> beats a matched train-only no-signal prior and every registered available
> timing, corruption, and peripheral control at the trial unit.

That would be a bounded within-person EEG sensor-signal advantage. It would not
yet be unseen-person generalization, brain-specific origin, arbitrary-thought
decoding, real-time decoding, portable hardware, or home use.

## Next Decision

The next irreversible step is still Loop 53, not Loop 54. If the exact Loop 53
authorization sentence is supplied unchanged, the repository must record an
authorization-only decision, obtain green remote CI, implement and fixture-test
the bounded acquisition path, obtain green remote CI again, and only then run
the one registered acquisition.

After a clean acquisition receipt exists, prepare the exact L54-A parser
contract and separate authorization packet. Do not implement or run L54-A from
this planning boundary.

Engineering capability added: NeuroDecodeKit now has a source-backed,
machine-checkable design for separating EEG header metadata, target-blind
signal quality, and target-bearing trial reconciliation before any classifier
claim.

Scientific claim not established: No S20 payload was accessed and no neural
advantage, decoding accuracy, brain-specific attribution, real-time operation,
portable hardware, home-use result, or clinical utility was demonstrated.
