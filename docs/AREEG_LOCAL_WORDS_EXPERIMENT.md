# ArEEG local imagined-word experiment

This is a new experiment authorized by the maintainer's September 5, 2026
instruction to build the closest feasible locally testable thought-to-text
system. It does not reopen any predecessor experiment.

Question: can a small, personally calibrated EEG decoder predict five prompted
imagined command words in a held-out recording session better than no-signal
controls? This is a discovery experiment, not independent confirmation.

Source: OpenNeuro ds005262 release 1.0.1, Git revision
`4ba1bb516d6cc98917143b0dfca23947935c7b15`, CC0. Select all twelve participants
sub-0 through sub-11. Sessions 0–4 are calibration; session 5 is the sole held-out
recording session (numbering does not establish date order). No other payload is selected. Individual files must match the release's
annex SHA256 and byte count. Raw acquisition ceiling: 320 MiB; total invocation
ceiling: 512 MiB, one numerical worker/thread, 1 GiB numerical RSS. Preserve the
existing global 20 GiB ceiling, 3 GiB untouched reserve and 20 GiB free-disk floor.

Protocol fixed before signal acquisition:

- Five words: down, left, right, select, up; output their literal label, without
  language-model rewriting. Training-only categorical prior is the independent
  language-only baseline for this finite vocabulary.
- Whole recording sessions are separated. No trial fragments cross partitions.
  All complete, finite five-second word events are included without performance
  dependent rejection. Events too short for the entire prescribed window are excluded using duration
  alone, with every exclusion counted. Actual event counts are recorded; the
  paper's nominal 25 events are not assumed to be exact.
- Use all eight EEG channels, with a fixed 1–30 Hz fourth-order Butterworth
  filter applied separately within each two-second interval. Primary interval
  is 2–4 seconds after the word event; diagnostic cue interval is 0–2 seconds.
  Zero-phase filtering means this is an offline completed-window decoder.
- One model per person: covariance with 0.1 trace shrinkage, symmetric matrix
  logarithm, 36 spatial features, training-only standardization, L2 multinomial
  logistic regression with C=1. No hyperparameter selection on held-out data.
- Compare actual EEG, early cue EEG, independently fitted shuffled EEG,
  independently fitted matched Gaussian noise, training-only class prior, and
  metadata-only logistic regression. Metadata is normalized trial position,
  its square, and a 25-position one-hot vector plus an overflow category; signal predictors receive neither event codes nor text nor order.
  Shuffling is a fixed, label-blind derangement separately within each recording
  session. Noise scales are computed from calibration EEG only.
- A separate broker reads the raw annotations and saves signal-only inputs plus
  separate targets. The predictor is OS-restricted to calibration labels and
  signal inputs; held-out annotations/targets/raw files are denied. Freeze
  prediction hashes in Git before the one target-scoring operation. Never tune
  or rerun this held-out evaluation after scoring.
- Primary endpoint: equal-person mean of class-macro log-loss improvement over
  each designated null control (prior, metadata, shuffled, noise). Also report
  all participant outcomes, balanced accuracy, exact-word accuracy, confusion
  matrix and descriptive paired participant bootstrap intervals. Twelve people
  and one held-out session per person do not establish independent replication.

The source asks participants to read a cue and close their eyes while imagining
the word; the cue remains on screen. It has no dedicated EOG or EMG recordings.
Success therefore supports prompted-task predictive utility, not isolated inner
speech, self-chosen thoughts, new-person generalization, free sentences, or
prospective live operation. A failed comparison remains a valid local result.

Scientific basis: [ArEEG, Scientific Data 2025](https://www.nature.com/articles/s41597-025-05387-w),
[EEG-to-text evaluation critique, Scientific Reports 2025](https://www.nature.com/articles/s41598-025-29587-x),
[Brain2Qwerty v2, 2026](https://arxiv.org/html/2608.18114v1), and
[COFETT, ACL 2026](https://aclanthology.org/2026.acl-long.61/).
The latter two motivate separating neural evidence from language/readout
performance; their results are not results of this implementation.

Pre-prediction review strengthened the metadata control with a one-hot trial-position
vector to detect arbitrary repeated schedules, before any fitting or test scoring.

Source-format corrections before fitting: the header stores 4000.0 microseconds;
event counts vary, and two calibration recordings contain an event shorter than
the prescribed window. The broker retains all complete events and records
duration-only exclusions. No test labels or scores were inspected by the predictor.

Before fitting, a source-completeness audit found that sub-2/ses-5 contains only
Rest and WarmUp annotations, with no word events. It is unscorable and is
excluded without choosing a replacement session. Sub-4/ses-5 has 24 word events.
The scored population is therefore the eleven participants with annotated test
word events, 274 test trials. Calibration contains 1,498 complete events, of
which 1,373 belong to those eleven participants. This availability-driven
revision happened before prediction or scoring; the result is exploratory.
