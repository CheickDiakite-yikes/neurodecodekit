# Quiet Signal — CAMERA-T2T-1-v1

A native, local macOS experiment toward **silent thought-to-text**. The initial
vocabulary is YES / NO. This is an exploratory self-study, not a demonstrated
thought reader, EEG instrument, medical device, or free-form language decoder.
It contains no speech recognizer, microphone input, LLM, model download, or
network client. No participant result exists until a person completes the study.

## Run

Requires the local Apple Swift compiler and macOS 14 or newer. This build was
prepared on an Apple M4 Pro MacBook; it uses the Mac's built-in camera only.

```sh
cd products/quiet-signal
bash build.sh
open 'build/Quiet Signal.app'
```

The app initially leaves the camera off. Click **Start camera experiment** to
request macOS permission and begin. No footage or audio is saved. Numerical
features, self-reported word labels, and hidden predictions are stored under
`local-runs/<random-session-id>/`, ignored by Git. These remain personal data.
The build uses Apple's system frameworks and a compiler cache in
`/tmp/quiet-signal-swift-cache`; it does not add dependencies to NeuroDecodeKit.

## Frozen first experiment

Hypothesis: camera-derived forehead color features during silent YES / NO
choices can predict a later private choice after training-only adjustment for
measured facial geometry, motion, and lighting. This measures a possible
**camera/behavioral/physiological association**. Even success cannot establish
that the camera directly senses neural electrical activity.

1. Complete 24 calibration trials. Choose privately before each trial, think
   the word silently, and keep your mouth and face relaxed. Do not deliberately
   alternate or follow a fixed sequence; use both words. At least eight of each
   are required. The app never presents a target-specific visual/audio cue.
2. Every trial has three seconds of settling and three seconds of recording
   under identical screen content. Nothing is scored from the choice-entry UI.
   Only one confidently detected face is accepted. Each capture requires at
   least 15 usable frames spanning two seconds, with no tracking gap over 0.5 s.
3. The observation is written and synchronized before the app requests your
   original word. Calibration features/labels and the compiled binary's SHA-256
   identify the deterministic frozen model recipe.
4. The camera stops after calibration. Take a short break, then explicitly
   start a fresh capture session for 24 held-out trials. These labels never
   update the model. Both blocks are from the same person/visit, not independent
   replication or unseen-person validation.
5. Each held-out prediction is written and synchronized **before** label entry.
   Predictions and local-record navigation are hidden until completion. The
   disk owner can still inspect records externally; do not do so during testing.
6. Score exactly once after all 24 test trials. Missing/invalid capture, loss of
   app focus while recording, user stop, decoder refusal, or the 20-minute limit
   ends an incomplete run. No trial replacement, resumption, or selective
   dropping is provided within a run. Keep all incomplete and completed runs in any analysis.

The full task generally takes 10–15 minutes. The 20-minute experiment clock
starts with the first trial and pauses during the camera-off inter-block break.
Camera permission/setup before the first trial of each block is excluded;
label entry and time between trials within a block count. Remaining time is
visible. Numerical records are capped at 2 MiB per run; raw video/audio
retention is zero. Finished runs include runtime, process high-water RSS, and
retained-byte accounting. Partial runs include a reason and trial counts.

## Decoder and controls

Forehead patch: normalized R/G, B/G, and green intensity, summarized as three
means and three standard deviations. This is not an EEG waveform or validated
pulse estimate. Hair, exposure, face tracking, blood flow, and small movements
can affect it.

Nuisance features: face center, width/height, yaw/roll, mouth aspect, left/right
eye aspect, and whole-frame brightness; retain both means and standard
deviations (20 features). A fixed ridge regression with an intercept removes
training-predictable nuisance components from the standardized six primary
features. Standardized nearest-centroid models predict from residual features
and from nuisance features. All scaling, nuisance coefficients, feature
retention, centroids, and thresholds are fitted on calibration only. A fixed
1e-4 residual standard-deviation floor prevents amplifying numerical residue.

Comparators are nuisance-only, calibration-majority with no camera, and
chronological trial position. These are diagnostic comparisons; their
capacities differ. There is no language model that could supply the answer.
The primary score is held-out accuracy; balanced accuracy, class counts, a
fixed-marginal one-sided permutation reference, and Wilson intervals are also
reported. Nuisance comparisons are descriptive, without a claim of a measured
incremental neural contribution. Fewer than six test examples of either word
is explicitly inconclusive. No user-facing confidence probability is invented.

The permutation reference assumes exchangeable labels, and the Wilson interval
assumes independent trials. Self-chosen words and serial dependence can violate
these assumptions. Neither a small p-value nor beating nuisance-only is proof
of thought reading: unmeasured behavior and nonlinear confounding remain.
No novel sensor, patentable invention, physiological effect, or scientific
breakthrough is claimed by a successful software build.

## What Apple's patent contributes

Apple's [US20230225659A1 application](https://patents.google.com/patent/US20230225659A1/en)
describes active and reference electrodes on an ear-worn device and circuitry
that selects electrode subsets for biosignal measurements, including EEG.
It supports investigating ear-contact acquisition hardware. It does not
demonstrate that stock AirPods expose EEG, that software can activate such a
sensor, or that electrode measurements decode unrestricted thoughts.
[Current AirPods sensor specifications](https://www.apple.com/airpods-pro/specs/)
do not list EEG acquisition. No AirPods modification or patented circuit is
implemented here. AirPods are not used in this first camera baseline.

Camera access and face geometry use Apple's
[AVFoundation permission API](https://developer.apple.com/documentation/avfoundation/avcapturedevice/requestaccess(for:completionhandler:))
and [Vision landmarks](https://developer.apple.com/documentation/vision/vndetectfacelandmarksrequest).

## Next decision follows the result

If the assay fails technically, the stored blocker identifies what prevented
measurement; that is not a biological null. If accuracy stays near baseline,
report that result for this representation and participant. If there is a
promising association, freeze the current result and propose a separately
defined, fresh-session replication with stronger nuisance and randomization
controls before changing the decoder or increasing the vocabulary. Never tune
on this held-out block or present repeated attempts' best result alone.

This separate local prototype follows the user's explicit 2026-09-09 request
to pursue this experiment. It accesses no historical participant data and
does not activate, reopen, or reinterpret any consumed NeuroDecodeKit lane.

## Verification at handoff

### Timing repair and saved calibration

The first v0 user run completed 24 calibration trials and froze its model, but
the original wall-clock cap expired before any held-out trial. The v1 UI/timing
successor preserves that run unchanged and incomplete. **Use saved calibration**
offers a new test block with the same calibration, not a resumption of v0.
The source hash, frozen-record hash, and parent session ID are logged in the new
run. No prior score exists. Core.swift and Camera.swift are unchanged.

Import is deliberately limited to the exact shipped v0 binary and a verified
51-event calibration-only timeout with zero held-out operations. It validates
the hash chain, ordered captures/labels, saved calibration, and frozen record.
The latest session alone is considered; the app never searches older runs for
better results. New calibration is always available through **Return to start**
after a stopped run. Camera activation still requires an explicit user action.

### Original build verification

Repair verification is recorded in `build/verification-v1.json`: 43 core,
14 pipeline, and 15 timing/recovery checks passed. The actual saved calibration
was restored through the native UI into a new test block. The model-frozen
screen and **Begin blinded test** button were visually verified with the camera
off. The original event log remained byte-identical. No held-out score was
computed during this repair.

The native build and signature verification passed. All 43 generated decoder
checks and 14 generated capture/journal checks passed. The actual app start
screen was opened and visually inspected, including a correction to button
contrast. Camera and microphone were off. `build/verification.json` binds the
final executable hash and artifact size. No real participant trials have run;
camera permission, actual face tracking, and the human experiment still require
the first user session. Software checks provide no thought-decoding evidence.
