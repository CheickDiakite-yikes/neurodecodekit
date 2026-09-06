# A positive reference before another word-decoder invention

September 6, 2026. **Research selection completed; neural reproduction not run.**
One proposed end-to-end experiment: `SPEECH-REPRO-1`. This is the response to
the maintainer's request to carry out steps 1–3 systematically. It does not
reactivate a historical motor, communication, or consumed evaluation route.
The earlier PCA proposal is parked.

## 1. Find a positive result worth reproducing

| Candidate | What the source actually supports | Decision |
|---|---|---|
| Brain2Qwerty v1 | Strong overt-typing result; known keystroke times; full model needs substantial GPU training. | Reference for the longer-term text goal, not our next imagined-word experiment. |
| Thinking Out Loud | Useful matched-arrow inner-speech/visualization conditions and recorded eye/lip signals. Published word-classification references have reproducibility limitations described below. | Retain for task-specificity research; do not assume a strong positive word benchmark. |
| Kara One | Original results concern binary phonological categories, not eleven-way word recognition. The channel called EMG is a colour sensor; imagery-period facial recording is not established. | Reject as the immediate positive anchor. |
| Sato et al., ultra-high-density speech EEG, ds007591 | A small model, separate calibration and historical online recordings, and simultaneous auxiliary signals. The reported positive concerns minimally overt speech; covert online performance is near chance. | **Select a bounded within-person reproduction challenge.** |

Two concrete findings change the selection. The Gallo/Corchs author notebook
evaluates its test set each epoch and reports the highest accuracy; two initial
attention blocks also receive batch-first tensors with sequence-first defaults.
The Radwan author notebook searches random trees using the same labels on which
it reports the winner. Neither released invocation supplies an independent final
test for that selection. These are public-code findings, not proof that all
reported effects are artifacts or that EEG lacks word information.

Sources: [Brain2Qwerty](https://www.nature.com/articles/s41593-026-02303-2),
[Thinking Out Loud](https://www.nature.com/articles/s41597-022-01147-2),
[Kara One paper](https://www.cs.toronto.edu/~complingweb/data/karaOne/ZhaoRudzicz15.pdf),
[Gallo notebook](https://github.com/ignaziogallo/gallo-IJCNN2024/blob/main/innerspeach-raw-data-classification.ipynb),
[Radwan notebook](https://github.com/yradwan147/InnerSpeechMLPipeline/blob/c68294d526672455f392bd04f4f7f364aeb8e85e/eeg-inner-speech-classification-pipeline.ipynb).

The selected study is a **2024 preprint**, not established clinical evidence.
Its three minimally overt EEGNet participant rows are above the 20% five-class
baseline. Do not target a particular rounded paper average: repeated sessions
and participant weighting must be reported separately. Its authors report a
substantial decline for covert speech in the online setting.
[Preprint](https://doi.org/10.1101/2024.05.09.591996),
[accessible primary manuscript](https://www.researchgate.net/publication/380933941_Delineating_neural_contributions_to_electroencephalogram-based_speech_decoding).

## 2. Ask an experiment that can distinguish explanations

**Primary question:** on later recordings of the same people, does recorded EEG
add five-word label information beyond the simultaneously measured eyes, lips,
microphone, display signal and target-free timing metadata?

Minimally overt speech supplies the positive-reference condition. Covert speech
is a predeclared separate challenge, not a replacement if the first fails.
Report both. Separate unadjusted reference prediction from conditional EEG
attribution: successful reference classification without an EEG increment can
mean that auxiliaries already explain the available information. A compact
method's predictive limitation requires poorer word prediction on matched
inputs and metrics; conditional failure alone does not establish it. If both
decoders fail to predict words, the reproduction is unsuccessful; signal
absence is not established. A positive reference matched by auxiliary controls
establishes usable task information without EEG-specific attribution. A
surviving incremental EEG advantage merits independent replication. No result
triggers post-test tuning here.

## 3. Verify measurements and select a bounded source

Public source metadata was inspected at OpenNeuro tag `1.0.1`, commit
`034af61aba855c58450977bf1c1916085c586cd6`. The dataset declares CC0 and 128 EEG
channels plus bipolar display, microphone, EOG, upper-lip and lower-lip pairs,
and a trigger. It defines event labels as the colour word spoken. The public
converter copies a word-list CSV; it does not document the original annotation
procedure. Thus release-label prediction can be evaluated, but independently
verified private intention cannot be claimed. This is a disclosed provenance
limit, not evidence that labels are historical decoder predictions.

Use all three participants, the earliest session of each participant for each
of `minimallyovert` and `covert`, its calibration file and all associated online
files. Filename-only selection yields **13 EDF files: six calibration and seven
online**, **1,035,519,408 signal bytes**, and **45,137 event-sidecar bytes**.
The largest EDF is 118,885,586 bytes. Sizes and SHA-256 identities were read from
Git-annex pointer metadata; no EDF header, waveform or trial row was opened.
The exact selection is in
[`speech_reproduction_source_manifest.v0.json`](../registries/speech_reproduction_source_manifest.v0.json).

This is a left-hemisphere speech montage, not the earlier whole-head central
versus posterior experiment. Cue identity is not counterbalanced against word
identity. Display voltage is not a complete interface-state log; the recorded
eye/lip channels do not cover every peripheral source. Neither this dataset nor
Thinking Out Loud can establish cue-independent thought content. That stronger
test needs multiple/remapped cues per word, independently recorded intentions,
matched no-imagery trials, randomized condition order, and synchronized relevant
peripheral measurements. This proposal collects no new human data.

Public definitions: [dataset README](https://github.com/OpenNeuroDatasets/ds007591/blob/034af61aba855c58450977bf1c1916085c586cd6/README),
[event definitions](https://github.com/OpenNeuroDatasets/ds007591/blob/034af61aba855c58450977bf1c1916085c586cd6/events.json),
[license](https://github.com/OpenNeuroDatasets/ds007591/blob/034af61aba855c58450977bf1c1916085c586cd6/dataset_description.json).

## Complete proposed execution scope

Approval of `SPEECH-REPRO-1` covers source verification, exact selective public
acquisition, minimal implementation, preprocessing, calibration, prediction
freeze, one final scoring invocation, aggregate reporting, and removal only of
invocation-created temporary files. No additional human micro-gate is proposed.
No other source, participant, condition, historical root, or hardware is admitted.

1. Verify the pinned manifest, declared channel roles, units, timing and
   calibration-to-online mapping. Retrieve only the selected files and their
   schema/channel/geometry sidecars from the official public release. Verify
   signal hashes and pinned Git identities. Reject missing pairs, changed
   identity, nonfinite signals or irreconcilable timing; no silent replacement.
   Require one label per complete original trial. If source evidence identifies
   online values as predictions rather than produced-word labels, stop before
   fitting or scoring. Do not infer labels from microphone, model output or UI.
2. Keep online trial values in a separate scorer-only local file. Preprocessing
   and prediction receive signals, onsets, anonymous IDs and acquisition roles,
   not online labels. Use calibration labels only for training/validation.
   Whitelist only the 128 declared EEG channels and the named bipolar EOG,
   upper-lip, lower-lip, microphone and display pairs for numerical features.
   Exclude trigger, status and annotation channels from every numerical arm;
   only the data broker may read these to extract timing and isolate targets.
   Keep all five repetitions and all augmentations of a trial together. No
   online adaptation, class-based exclusion or test-label balancing.
3. Reproduce the published EEGNet family from author code commit
   `0dca00584c528b288392684dcec0d496b6aa4951`: 128 channels, 320 samples after
   averaging five 1.25-second repetitions, 12,293 parameters, source notch/CAR/
   2–118 Hz and adaptive EOG/lip filtering. Use **100 epochs from the manuscript**
   rather than the current YAML's 1,000, batch 16, AdamW learning rate 1e-4 and
   weight decay 0.01. Ten stratified calibration folds; seed 20260906. Save each
   fold's lowest validation-loss epoch, then ensemble its four best folds using
   the source z-score-and-mean rule. Calibration-only selection, deterministic
   evaluation without jitter; training jitter at most ±0.1 s. Report these
   implementation choices as a reproduction with explicit deviations, not an
   exact numerical replay. Preserve calibration-only preprocessing state;
   reset adaptive filters per trial so they cannot carry information between
   held-out and training examples.
4. Alongside the reference, fit a fixed compact conditional model on identical
   calibration trials. For each averaged channel use 64 temporal bin means and
   log powers in six bands (2–4, 4–8, 8–13, 13–30, 30–60, 60–118 Hz).
   Auxiliary features additionally retain unaveraged full-trial band powers,
   RMS and peak-to-peak, avoiding cancellation of lip activity by repetition
   averaging. Timing features are trial index and elapsed recording time only.
   Standardize on calibration data, normalize EEG and auxiliary feature blocks
   by the square root of their dimensions, and fit multiclass ridge regression
   to one-hot labels, penalty 1.0 and unpenalized intercept. Softmax its outputs
   without test calibration. This is an explicit compact comparator, not the
   published decoder.
5. Freeze every compact arm: joint auxiliaries `N`; `N + raw EEG` (before
   adaptive filtering); `N + adaptive-filtered EEG` (primary); `N + pre-action
   EEG`; and `N + deranged EEG`. Preserve the identical `N` in every arm and
   identical EEG feature dimensions in all populated EEG slots. Derangement is
   a one-trial cyclic reassignment of the primary adaptive-filtered EEG
   features within each recording, separately for train and test, independent
   of labels. Include a shuffled-calibration-label primary joint arm, with the
   same fixed seed and within-recording permutation, plus uniform and
   training-word-prior baselines. Raw EEG is a processing ablation, not a null.
   Pre-action EEG uses the same channel/filter recipe on the 1.25 s preceding
   the five repetitions, with no repetition averaging. Its preprocessing may
   use only the recording prefix ending at that window's boundary, so filtering
   cannot borrow action samples. Disclose its shorter sampling support. It is
   a timing comparison, not a cue-only or signal-free control: preparation and
   cue responses may be present. Do not use a circular-shift control, which
   merely permutes these temporal features for a refitted ridge model. None of
   the arms uses an LLM or generated sentences.
6. Commit all prediction hashes and the model/feature/split settings before
   releasing online labels to one scorer. The primary endpoint is equal-person
   mean class-macro log-loss improvement of `N + adaptive-filtered EEG` over
   `N` in minimally overt speech. Report its paired edges over every other
   compact arm, all reference accuracies and balanced accuracies, and the
   corresponding covert results. Pool online runs within a calibration pair,
   then average within person; never count repetitions as independent people.
   Require positive increments over `N`, the deranged and shuffled-label joint
   controls, uniform and the training-word prior in all three people for a
   descriptive conditional success designation. Raw EEG and pre-action EEG are
   interpretation comparisons outside this conjunction; report their outcomes
   even if they match or outperform the primary arm. Reference reproduction is
   assessed separately as five-class balanced accuracy above 20% in each person,
   with its distance from each published participant result disclosed. With
   three people, the smallest one-sided
   sign-flip p-value is 0.125; there is no population-significance claim.
   If a class is absent in evaluation, mark that person's five-class endpoint
   incomplete rather than silently changing the class set or denominator.
7. Return the complete result, including nulls and any unavailable comparison.
   A positive outcome supports a small offline reproduction on release labels
   within known people and beyond the measured comparators. It does not prove
   cortical origin, cue independence, transfer to new people, arbitrary text,
   clinical benefit, or our own prospective live operation. Keep raw data,
   labels, predictions and weights local; commit only code and aggregates.

## Resource feasibility and stopping

A target-free CPU probe of the reviewed reference class measured **0.1296 s
per batch training step**, **765,345,792-byte peak RSS**, using one thread and
Torch 2.13.0. This was twelve Gaussian-input steps, not a neural experiment.
At six batches per epoch, 60 fits of 100 epochs imply about **78 minutes of
training alone**. Preprocessing/validation add time; this is an estimate.

Proposed cap: **two hours total execution**, 15 minutes per acquisition,
preprocessing or individual-fit stage, one worker/thread, 4 GiB peak RSS.
If the complete schedule cannot fit, stop without scoring partial predictions;
do not shorten training or discard participants based on partial results.

New retained-plus-temporary disk is capped at **1.5 GiB**, partitioned as
1,024 MiB raw/source sidecars + 128 MiB download temporary + 256 MiB derivatives
+ 64 MiB checkpoints + 64 MiB predictions/reports/code metadata. Process one
calibration pair at a time and remove only its newly created intermediate
arrays after feature/prediction hashes are saved. Preserve all pre-existing
files. The measured data/cache/.codex_work footprint was 16,427,315,200 bytes;
adding the full increment and untouched 3 GiB reserve remains below 20 GiB.
Existing interpreter and Git history are not research-payload allocations.
Recheck that arithmetic and the 20 GiB free-filesystem floor before acquisition.

The single remaining authorization is the repository's new-source Tier C
decision. `approve`, `continue`, or `proceed` can bind this complete named scope
after its exact commit is remotely green. Public metadata and the compute probe
above do not constitute that authorization or a new decoding result.
