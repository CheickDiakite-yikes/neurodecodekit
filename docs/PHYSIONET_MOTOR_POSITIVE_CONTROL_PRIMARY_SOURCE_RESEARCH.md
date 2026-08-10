# PhysioNet Motor Positive-Control Primary-Source Research

Status: **Planning complete; no EDF content opened and no experiment run**

Date: 2026-08-09

## Decision In One Sentence

The next evidence-producing work order should use the already acquired
S001-S003 motor-execution EDFs to test one frozen held-out-run question:
can a small classical EEG pipeline recover left-versus-right motor-task
information while also showing motor-compatible sensorimotor physiology and
failing fixed timing, pre-cue, spatial, and label controls?

This is the shortest route to a result that changes the research program. A
clean pass justifies an unchanged replication on more untouched public
participants. A failure localizes whether the problem is EDF intake,
preprocessing, representation, or confounding before protected S20 evidence is
spent.

## What The Public Source Establishes

The official PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0 description
states that each recording contains 64 EEG channels sampled at 160 Hz plus an
EDF+ annotation channel. Runs 3, 7, and 11 are repeated motor-execution runs in
which a participant opens and closes the left or right fist in response to a
left- or right-side visual target. In those runs, `T1` is left-fist onset and
`T2` is right-fist onset.

Primary sources:

- [PhysioNet EEGMMIDB v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)
- [BCI2000 system paper](https://doi.org/10.1109/TBME.2004.827072)
- [MNE EEGBCI run loader](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)

The official MNE CSP example is useful as an implementation reference, not as
our validation design. It reads EEGBCI EDF files, standardizes the channel
names, applies a montage and average reference, filters the signal, and trains
a four-component CSP plus LDA pipeline. It deliberately begins its training
window one second after cue onset to reduce immediate evoked-response
classification. The rendered example reports 45 task events across three
runs for one participant.

- [MNE CSP EEGBCI example](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html)
- [MNE CSP API](https://mne.tools/stable/generated/mne.decoding.CSP.html)

MNE's example uses shuffled row-level cross-validation and a zero-phase filter.
Those are reasonable tutorial choices, but they do not meet NeuroDecodeKit's
prospective held-out-run or causal-preprocessing requirements. Work order 9
therefore retains the documented CSP family while replacing row shuffling with
run grouping and replacing future-dependent filtering with a continuous
second-order-section causal filter.

## Why Accuracy Alone Is Not Enough

The class and the visual target side are coupled in this task. PhysioNet says
the target appears on the left or right and remains present while the movement
is performed. It follows that a high left/right score may contain lateralized
visual or eye-movement information in addition to movement-related activity.
The dataset has no separately acquired EOG or EMG channel that can prove the
physical origin of a classifier feature.

This is not a theoretical edge case. MNE's example explicitly delays the
classification window to avoid the immediate cue-evoked response. Primary
decoding studies also show that small task-correlated eye movements can create
apparently decodable neural patterns, and movement EEG can be contaminated by
muscle and motion artifacts.

- [Eye-movement confounds in neural decoding](https://pmc.ncbi.nlm.nih.gov/articles/PMC6179574/)
- [Motion and muscle artifact validation in EEG](https://doi.org/10.1109/TNSRE.2020.3000971)

Therefore the maximum clean result is not "brain control" or "motor intent."
It is a held-out-run motor-task EEG effect with motor-compatible physiology and
explicit residual visual, ocular, muscle, and motion caveats.

## Two Independent Evidence Axes

### 1. Predictive axis

For each of S001-S003:

1. use run 03 and run 07 only for fitting and family selection;
2. perform both directional run-grouped checks, `03 -> 07` and `07 -> 03`;
3. select between the frozen four-component CSP plus shrinkage-LDA family and
   regularized Riemannian covariance MDM using macro participant balanced
   accuracy;
4. refit the selected family on runs 03+07;
5. produce run-11 predictions without exposing run-11 targets to the fit or
   prediction process; and
6. commit, push, and obtain green CI for a hash-only prediction freeze before
   the isolated scorer receives the run-11 targets once.

The low-frequency shrinkage-LDA family remains a fixed comparator. It cannot
win the CSP-versus-Riemannian selection and cannot change the primary endpoint.

The Riemannian candidate follows the covariance-plus-MDM method introduced by
Barachant and colleagues. pyRiemann 0.12 provides the maintained implementation
and remains an optional experiment dependency.

- [Barachant et al. 2012](https://doi.org/10.1109/TBME.2011.2172210)
- [pyRiemann 0.12 documentation](https://pyriemann.readthedocs.io/en/v0.12/)

### 2. Physiology axis

The experiment separately measures fixed central-channel mu and beta power
from one second before cue onset and from one to three seconds after cue onset.
The prospective assay asks whether post-cue sensorimotor-band power decreases
in a movement-compatible direction and whether the contralateral-minus-
ipsilateral contrast has the registered sign.

Event-related desynchronization is a reduction in ongoing oscillatory activity
following an internally or externally paced event. It is an established
physiology assay, but this dataset still cannot isolate cortex from every
movement, ocular, and cue-related source.

- [Pfurtscheller and Lopes da Silva 1999](https://doi.org/10.1016/S1388-2457(99)00141-8)

The predictive and physiology axes are conjunctive. Classification without the
registered physiology is a task-signal result only. Physiology without
held-out prediction is a descriptive signal-quality result only.

## Fixed Confound And Leakage Controls

Every final control prediction must freeze before run-11 targets open:

1. train-only no-signal prior;
2. all-zero final signal;
3. pre-cue window model;
4. event-index and timing-only model;
5. fixed within-run train-label derangement;
6. fixed one-trial final signal displacement;
7. fixed validation-channel derangement;
8. fixed left/right hemisphere swap;
9. frontal-plus-occipital proxy-channel model; and
10. central sensorimotor-channel model.

The frontal/occipital result is a proxy control, not measured EOG. A weak proxy
cannot prove that eye movements are absent. A strong proxy or pre-cue/timing
result prevents a motor-compatible verdict even if the full-head classifier is
accurate.

## Prospective Outcome Ladder

| Verdict | Meaning | Route |
|---|---|---|
| `WO9-V0` | Input, event, split, resource, or prediction-freeze gate failed | Park and repair engineering without scoring another final set |
| `WO9-V1` | No held-out motor-task signal above the frozen primary gate | Stop protected model escalation and localize parser/preprocessing/model failure |
| `WO9-V2` | Predictive signal exists but physiology or confound conjunction fails | Record cue/confound-compatible task information only |
| `WO9-V3` | Prediction, physiology, and all mandatory controls pass | Record a three-person motor-compatible public EEG pilot and freeze an unchanged larger-cohort replication |

`WO9-V3` is the maximum result. It does not establish brain-specific origin,
unseen-person generalization, typing, language decoding, thought decoding,
real-time operation, wearable hardware, home use, assistive benefit, or
clinical utility.

## Why The Cohort Stays Small For This Gate

The nine already acquired EDFs are a development and qualification cohort, not
a final population estimate. Spending the user's available 10 GiB ceiling
before the family, filters, split, controls, and scorer are frozen would create
more opportunities to tune on public outcomes.

If and only if `WO9-V3` passes, the next contract should acquire a larger set of
previously untouched participants, preserve the selected family and every
threshold byte-for-byte, and estimate participant-level replication. No pass
means no expansion merely to hunt for a better-looking subset.

## Resource Design

- no network and no additional download;
- exactly the nine acquired EDFs totaling 23,248,224 bytes;
- one CPU thread, one worker, and one numerical job;
- sequential file processing;
- at most 1,800 seconds wall time;
- at most 768 MiB peak RSS;
- at most 64 MiB generated private derivatives and receipts;
- at least 2 GiB free disk before execution; and
- no model larger than the fixed classical families.

The causal 8-30 Hz view uses a fourth-order Butterworth design emitted as
second-order sections and applied with `scipy.signal.sosfilt` to each continuous
run before epoching. SciPy recommends SOS representation for numerical
stability. No resampling, ICA, target-derived channel rejection, evaluation
normalization, or post-result tuning is allowed.

- [SciPy `butter`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html)
- [SciPy `sosfilt`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html)

## Current Access Ledger

This research pass opened no local PhysioNet path and read no EDF header,
annotation, event, signal sample, target, channel, geometry, or private
receipt. It created no cache or split, imported no new model dependency, fit
no model, made no inference, scored no result, downloaded no bytes, and used no
provider, stream, device, or hardware.

Engineering capability added by this planning result: NeuroDecodeKit now has a
falsifiable, resource-bounded route from its acquired public EDF inventory to a
prediction-freeze-protected motor positive control.

Scientific claim not established by this planning result: no EDF content or
outcome was observed, so no motor-task signal, physiology, neural advantage,
generalization, decoding accuracy, latency, device, or human-benefit claim was
established.
