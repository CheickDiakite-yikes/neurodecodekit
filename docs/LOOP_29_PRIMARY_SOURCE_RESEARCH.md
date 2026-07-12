# Loop 29 Primary-Source Research And Portable Sensing Decision

Date: 2026-07-12

Status: **Planning research complete; no data download, recording read, model,
training, stream, device, partner session, or hardware operation is authorized**

Machine boundary: `registries/loop29_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 29

## Decision Summary

Loop 29 remains `Not Started`. The research result is a two-lane portability
strategy rather than a claim that one reduced sensor array solves deployment:

1. **Scalp EEG is the immediate local-first research lane.** It has practical
   local hardware, established open file and adapter paths, an existing
   NeuroDecodeKit bridge, and evidence that repeated dry-EEG sessions can be
   self-administered at home. It also has a severe task-specific performance
   gap, reference and placement dependence, motion and muscle contamination,
   and device timestamp risks. Home recording is not home text decoding.
2. **OPM-MEG is the same-modality partner/lab lane.** It operates near room
   temperature, can move with the head, and has measured speech-tracking and
   real-time evoked-response evidence. Current human systems still depend on
   specialized magnetic shielding, active field control, sensor geometry,
   motion tracking, and interference suppression. Wearable does not yet mean
   at home.
3. **Cryogenic MEG remains the scientific reference.** Brain2Qwerty v2's
   76/153/230-channel ablations are useful model sensitivity evidence, but the
   sensors still come from the same 306-channel cryogenic system. They do not
   reproduce an OPM or EEG device.
4. **EOG, EMG, IMU, gaze, audio, hand, and cardiac wearables remain controls or
   separate accessibility inputs.** They cannot be relabeled as brain signal.

No device is selected or recommended for purchase. A named device requires a
future Loop 42 packet after its raw-locality, task, geometry, reference, clock,
packet, privacy, repeated-session, and signal-quality requirements can be
measured directly.

## Storage Envelope And Selected Real-Data Path

The user approved up to an additional 5-10 GB of local capacity. Loop 29 binds
that as a conservative storage envelope, not an instruction to fill it:

```text
preferred incremental ceiling:        5,000,000,000 bytes
absolute incremental ceiling:        10,000,000,000 bytes
current Loop 29 downloads:                         0 bytes
current Loop 29 generated cap:             8,388,608 bytes
```

The two highest-value future bundles already fit comfortably:

| Candidate | Role | Exact bytes | Current status |
|---|---|---:|---|
| S20 session 2 block 2 EEG | First fresh task-matched EEG result under the existing 44/10/10 packet | 96,090,264 | Exact packet prepared; not authorized |
| S25 session 2 block 2 MEG | Final-only T2 unseen-person transfer test | 1,009,939,983 | Metadata selected; no acquisition packet or authorization |
| **Combined** |  | **1,106,030,247** | Zero bytes downloaded here |

That leaves 3,893,969,753 bytes below the preferred ceiling and 8,893,969,753
bytes below the absolute ceiling. No additional source block should be selected
merely because space remains. Existing S21 source-train material should answer
the first bounded source-model question at zero new download cost. Additional
source data belongs behind Loop 33 sample-efficiency evidence.

The storage statement is not permission to open S20, S25, S21, S7, targets, or
models. The exact S20 packet remains
`docs/FRESH_EEG_BENCHMARK_S20_APPROVAL_PACKET.md`; S25 requires a later staged
packet after the source model and transfer controls freeze.

## Measured Research Boundary

```text
high-level public web operations:          14
GitHub metadata API operations:             0
remote code/data payload downloads:         0
local real-data path or hash checks:         0
real header/signal/target reads:             0
consumed-evidence reads:                     0
model/checkpoint/training/calibration runs:  0
SDK imports, sockets, or streams:            0
device purchases or hardware sessions:       0
partner or participant outreach:             0
CPU threads / workers:                     1 / 1
```

The external browser tool does not expose process-level peak RSS or one
end-to-end research runtime. Both are explicitly unavailable rather than
estimated.

## Finding 1: Sensor Count Is Not A Modality

Brain2Qwerty v2 records 306 channels at 1 kHz on a MEGIN system: 102
magnetometers and 204 planar gradiometers. Its sensor study retrains the same
pipeline on random subsets of 76, 153, and 230 channels across four subset
seeds. The measured degradation is important evidence that the model is not
equally dependent on every cryogenic channel.

It is not an OPM-MEG experiment. The ablation preserves the original sensor
technology, room, coordinate system, noise field, acquisition electronics,
filters, clocks, and participant protocol. It also is not EEG evidence: scalp
voltages require an electrical reference and ground, have a different forward
model, and exhibit different artifact and spatial-mixing behavior.

The v2 paper itself calls low-channel OPM sentence decoding a future question.
Loop 29 therefore records the published 150-sensor extrapolation as a
hypothesis, not a portable result.

Primary source:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

## Finding 2: OPM-MEG Preserves Modality, Not Environment

OPMs are magnetometers that operate near room temperature and can be mounted
close to the scalp. This removes cryogenic cooling and permits a participant to
move with the array. It does not remove the fact that neural magnetic fields
are tiny relative to environmental fields.

Measured human evidence currently includes:

- cortical tracking of listened speech with 45-46 OPMs in four adults during
  nine minutes of speech;
- online ERP and SSVEP neural-interface demonstrations;
- full-head and low-count sensor arrays for sensory and motor tasks;
- improved operation in lighter shielding when combined with interference
  suppression.

These are meaningful steps. None is prompted sentence production or
brain-to-text. The speech-tracking experiment used a room specifically built
for OPM-MEG, head/helmet coregistration, and interference removal. Field-control
research shows that head movement through even a very low residual field
creates low-frequency artifacts. The lightly shielded result still uses a
specialized room; the paper contrasts it with state-of-the-art shields over
3 m tall and over 10,000 kg rather than with an ordinary home.

An OPM partner packet must therefore bind sensor positions and axes per
session, gain and crosstalk, reference sensors, residual field and gradients,
passive shielding, active nulling, motion tracking, raw/corrected signal
provenance, clocks, triggers, task, and data export. Without those fields,
`OPM-MEG` is only a label.

Primary sources:

- OPM speech tracking:
  https://www.sciencedirect.com/science/article/pii/S1053811921002469
- OPM in a lightly shielded environment:
  https://pubmed.ncbi.nlm.nih.gov/39302788/
- precision field mapping and nulling:
  https://pubmed.ncbi.nlm.nih.gov/34273527/
- interference suppression:
  https://pubmed.ncbi.nlm.nih.gov/34933122/
- practical real-time OPM interface:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8356471/
- MNE's current OPM processing boundary:
  https://mne.tools/stable/auto_tutorials/preprocessing/80_opm_processing.html

## Finding 3: EEG Is Accessible And Scientifically Hard

Brain2Qwerty v1 provides the most relevant EEG comparison because it uses the
same prompted typing task. Its 64-channel, 1-kHz EEG cohort reached mean CER
0.65 versus 0.29 for 306-channel MEG. The local S7 bridge also produced a
negative transparent result: nearest-centroid key accuracy 0.91% versus 12.27%
for the no-signal prior. Neither result means EEG is hopeless. Both mean a
portable EEG claim must be earned rather than inferred from accessibility.

Other language-facing EEG results answer different questions. Large-cohort
perceived-speech work reports EEG above random but materially below MEG after
matching channels, duration, and participants. DeWave maps EEG recorded during
displayed natural reading to text with a pretrained language model; it is not
unprompted thought typing, and displayed text, eye behavior, and language
priors require explicit controls.

Home EEG mechanics are more encouraging. Two cohorts totaling 80 people
self-administered repeated dry-EEG oddball and Flanker tasks at home over
multiple weeks. Aggregating repeated sessions improved evoked-response quality.
That is evidence for repeated local acquisition, not language decoding.
Independent dry-electrode benchmarking also warns that reliability below 6 Hz
and resistance to jaw/head movement can be worse than standard wet EEG.

The near-term scientific lane is therefore:

```text
task-matched research EEG -> fresh controlled result -> recorded replay
-> named local device mechanics -> repeated task signal -> text evaluation
```

Skipping directly from a four- or eight-channel product page to text generation
would be a claim error.

Primary sources:

- Brain2Qwerty v1 EEG/MEG comparison:
  https://www.nature.com/articles/s41593-026-02303-2
- non-invasive perceived-speech comparison:
  https://www.nature.com/articles/s42256-023-00714-5
- DeWave:
  https://openreview.net/forum?id=WaLI8slhLw
- repeated self-administered home EEG:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9372279/
- dry-electrode reliability benchmark:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12480468/

## Finding 4: Metadata Needed Before Any Device Claim

BIDS EEG requires the sampling frequency and reference scheme, and supports
channel-specific references, units, electrode positions, coordinate systems,
ground, hardware/software filters, and channel quality. BIDS MEG similarly
requires sampling, units, filters, coordinate frames, and head-localization
metadata. These are a minimum provenance vocabulary, not proof that a device is
accurate.

The official OpenBCI documentation illustrates why exact transport matters.
Cyton exposes eight 24-bit ExG channels at 250 Hz with packet/sample identity
and optional board time. Cyton+Daisy exposes 16 channels through alternating
averaged packets with an effective 125-Hz per-channel rate and a documented
sample delay. BrainFlow normalizes ExG units to microvolts where possible, but
some device timestamps are created on the host when packets arrive and each
preset can have its own rate, timestamp, and packet ID. A nominal `256 Hz` or
`250 Hz` label cannot stand in for a measured clock and gap audit.

Official specifications used as representative evidence:

- BIDS EEG:
  https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html
- BIDS MEG:
  https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetoencephalography.html
- OpenBCI hardware:
  https://docs.openbci.com/FAQ/HardFAQ/
- Cyton packets, units, timestamps, and Daisy behavior:
  https://docs.openbci.com/Cyton/CytonDataFormat/
- BrainFlow units and timestamps:
  https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html
- representative research wireless EEG specification:
  https://www.gtec.at/product/gnautilus-research-wireless-eeg-system/

Vendor specifications are tagged as specifications. They cannot qualify signal
quality, task performance, privacy, latency, or decoding.

## Modality Requirement Matrix

The machine registry freezes 15 cross-modality requirements. The condensed
human view is:

| Requirement | Cryogenic MEG | OPM-MEG | Scalp EEG | Peripheral controls |
|---|---|---|---|---|
| Units | T and T/m | T plus gain/axis calibration | V or uV plus gain/reference | Modality-specific |
| Geometry | Device/head transform | Per-session position and axis | Electrode coordinates or unavailable | Separate namespace |
| Reference | Magnetic reference channels | Reference sensors and field model | Raw reference, ground, rereference | Modality-specific |
| Environment | MSR and compensation | MSR, residual field, gradients, active nulling | Power-line/electrical context | Measured separately |
| Contact/fit | Head-to-dewar distance | Helmet and sensor-to-scalp fit | Contact, impedance, cap fit | Modality-specific |
| Motion | Head localization | Head pose plus field-motion model | EOG/EMG/IMU/contact motion | Retained as controls |
| Time | Device clock and triggers | Sensor sync, motion, trigger clocks | Board/host origin and triggers | Separate clock domain |
| Transport | Acquisition-specific | Acquisition-specific | Packet loss/reorder/reconnect | Packet audit |
| Privacy | Local research export | Partner/license gate | Local raw path, network-off audit | Disclosed separately |
| Task proof | Typed-sentence reference | Unavailable | Research EEG exists; portable unavailable | Cannot define neural proof |

No universal channel count or sampling rate is declared sufficient for text.
The device-specific packet must show that its actual rate and analog filters can
support the chosen retained band and causal anti-alias transform. Geometry,
reference, and missing channels may never be selected from final accuracy.

## Qualification Ladder

Loop 29 defines six levels that cannot be collapsed:

| Level | Evidence | Maximum honest claim |
|---:|---|---|
| 0 | Official specification or file metadata | Recognized, not qualified |
| 1 | Bounded recorded signal quality | Named file/device signal mechanics |
| 2 | Recorded replay transport equivalence | Replay mechanics only |
| 3 | Named live device mechanics | Connectivity, packets, clocks, locality |
| 4 | Task signal above artifact controls | Exact task/device signal evidence |
| 5 | Independent text result above no-signal and peripheral controls | Exact person/session/task/device/split only |

A device listing, SDK import, waveform plot, or successful file read cannot
skip levels. A negative result remains a result and blocks promotion rather
than inviting post-hoc relabeling.

## Next Result-Oriented Gates

Two independent decisions can move the science while respecting the proof
boundary:

1. **S20 fresh EEG benchmark:** the existing packet selects exactly four files
   and 96,090,264 bytes. It can test whether a transparent classifier beats a
   no-signal prior and a frozen signal-shuffle control on one fresh task-matched
   recording. It cannot test sentence CER, portability, or unseen-person
   transfer.
2. **Loop 25 then Loop 26:** the causal mechanics gate remains synthetic by
   design; after it passes, a separate Loop 26 packet can use only authorized
   S21 source-train/validation rows to produce one frozen source model before
   S25 opens.

S20 and Loop 25 are independent authorization decisions. Neither authorizes
S25, hardware, a device purchase, or the other decision.

## Remaining Blockers

Before any named portable-device packet can be prepared:

1. Select one exact device only after raw-locality, license, task, geometry,
   reference, clock, packet, and privacy fields are verifiable.
2. Freeze playback/replay equivalence before a live source.
3. Name the exact consent, retention, deletion, network, file, byte, session,
   and stop boundaries.
4. Measure setup, contact/fit, bad channels, packet behavior, and repeated
   sessions before prediction.
5. Preserve EOG, EMG, IMU, timing, and other peripheral controls or mark neural
   specificity unavailable.
6. Keep device mechanics, signal quality, task information, and text decoding
   as separate decisions.

## Closeout Decision

```text
loop29_planning_research_complete_two_lane_portability_ready_execution_blocked
```

This work adds a machine-checkable path from cryogenic MEG toward local EEG and
partner OPM-MEG, plus a measured storage allocation for the first fresh real-
data results. It does not establish OPM sentence production, portable EEG text
decoding, arbitrary-thought typing, end-to-end real-time text, at-home device
performance, assistive benefit, diagnosis, or clinical utility.
