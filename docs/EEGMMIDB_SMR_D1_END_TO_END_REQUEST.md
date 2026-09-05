# EEGMMIDB-SMR-D1: one complete real EEG experiment

Date: 2026-09-05. Status: **proposed; no real access or execution authorized**.
Machine request: `registries/eegmmidb_smr_d1_request.v0.json`.

## The decision

Authorize one new experiment, acquisition through one final score, on the exact
40 public EDF files below. This expressly adopts a **narrower task-condition
diagnostic** because no eligible public cohort with the full synchronized
EEG/EOG/effector-EMG controls was established by the preceding bounded audit.
It tests the spatial and temporal component of the larger hypothesis; it cannot
answer the larger peripheral-independent motor-attribution question.

This is a new data identity and question outside FMSR1. EEGMMIDB remains excluded
from FMSR1. Nothing here revives UG1/SA2, Dreyer, Ofner, FMSR1-E2E, S21, S24,
COMM, any consumed attempt, or any ignored evidence. No new experiment is active
until the maintainer approves this exact remotely green request. There is one
decision for this whole route, with no later human micro-authorizations.

## Hypothesis and participants

H-SMR-D1: A fixed central EEG band-power model trained on ten people carries
unseen-person cued left/right-fist task-condition information beyond fixed
spatial, timing, derangement, metadata, and no-signal comparators.

Source: PhysioNet EEG Motor Movement/Imagery Dataset, version 1.0.0,
DOI `10.13026/C28G6P`, recorded in the existing source records as ODC-By 1.0,
64 EEG channels at 160 Hz. These properties must be verified after approval.

| Partition | People | Runs | EDF files | Use |
|---|---|---|---:|---|
| Development | S031-S040 inclusive | R03 and R07 | 20 | Within-person check, then pooled fitting |
| Confirmation | S041-S060 inclusive | R11 only | 20 | Unseen-person frozen prediction and one score |

The machine request lists every relative path. No S001-S030, other runs,
participants, sessions, or datasets may be accessed. The tracked authority
audit found no use or reservation for S031-S060; it did not inspect protected
storage and does not prove absence of unrecorded use. Newly discovered prior
target/model use or conflicting reservation stops this proposal without
replacement participants. No existing raw-data path may be searched or reused.

## Source verification and bounds

After the decision is green, contact only the official HTTPS PhysioNet
`/content/eegmmidb/1.0.0/` landing page, `/files/eegmmidb/1.0.0/SHA256SUMS.txt`,
and the forty exact EDF paths under `/files/eegmmidb/1.0.0/`.
No credentials, mirrors, range probes, general indexes, or TLS bypasses.
Verify the version, license, requested SHA-256 entries, and each file's size and
hash. If the named public checksum manifest or a required identity is absent,
stop; do not invent a validator or substitute a source. Listing unrelated
checksum entries grants no payload or semantic access to those files.

Exact sizes and hashes are currently unknown. Prior files suggest about 100 MB;
that is a planning estimate, not a measured size. Limits: two metadata GETs,
forty EDF HEADs, forty complete EDF GETs, zero retries, and zero redirects.
Metadata bodies together <=4 MiB; each EDF <=8 MiB; all EDFs <=256 MiB.
Only request EDF bodies after all forty identities and size bounds are established.
Acquire the twenty development EDFs first; acquire the twenty confirmation EDFs
only if the fixed development check passes. An incomplete requested partition
terminates the attempt. Do not replace a participant.

## Frozen preprocessing and model

T1 and T2 event onsets define left/right task trials; rest is excluded. The
broker removes the T1/T2 distinction from predictor inputs and preserves the
same ordered row identity in every arm. Duration and timing are target-blind
eligibility inputs, not class labels.
Map event onsets to the nearest sample using `floor(onset_seconds*160+0.5)`;
all window offsets are then exact integer sample offsets.

Require 160 Hz and the twelve named EEG channels below, with explicit physical
units converted to volts. Normalize channel names only by uppercasing and
removing terminal periods/whitespace. No guessed montage, channel substitution,
re-referencing, resampling, ICA, whole-recording filtering, amplitude-based
rejection, or signal-dependent parameter search.

| Spatial representation | Three fixed bipolar differences |
|---|---|
| Central | C3-FC3, CZ-FCZ, C4-FC4 |
| Posterior | P3-PO3, PZ-POZ, P4-PO4 |

Windows relative to each cue onset: task `[2,4)` s; earlier `[-2,0)` s;
cue `[0,2)` s; shifted `[-4,-2)` s. A single shared, target-blind mask requires
all four windows inside the recording, task duration >=4 s, finite samples in
all twelve channels, and no window crossing another task onset. The latter
check applies to interiors, excluding the index onset itself. Earlier/shifted
windows are not assumed to be signal-free. No exclusion may depend on class,
performance, or which arm would benefit. Require >=12 retained trials per run;
development also requires >=4 trials/class/run. Confirmation class sufficiency
is checked only by the final scorer, with no feedback to preprocessing.

For each bipolar window, use Welch power density: 160-sample periodic Hann,
80-sample overlap, 160-point FFT, constant segment detrending, arithmetic mean
periodograms, one-sided density. Sum density times 1 Hz over `[8,12)`,
`[12,20)`, and `[20,30]` Hz, then natural-log after flooring at `1e-24 V^2`.
This gives nine features. No continuous filter can import later samples.

M is two metadata features: cue onset divided by run duration, and retained
zero-based trial ordinal divided by `max(1, retained_trial_count-1)`. It contains no class,
participant identity, run number, cue category, or raw annotation string.
**M is not the full EOG/EMG nuisance bundle N. Those channels are absent.**

Arms: M+central task, M alone, M+posterior task, M+central earlier,
M+central cue, M+central shifted, M+deranged central task, and no signal.
Derangement is one target-blind Sattolo permutation of complete nine-feature
rows within each retained participant/run: chronological input order,
`random.Random(0)`, descending indices, `j=randrange(i)` for each `i>0`.
Restart the generator for each run; preserve M and target row order. It is a
negative control, not a permutation p-value. No mapping changes after scoring.

Every fitted arm uses training-only weighted mean/population-SD scaling (zero SD ->1),
then binary L2 logistic regression with intercept, C=0.1, lbfgs,
max_iter=1000, tol=1e-8. Training weights give each person equal total weight
and each class equal weight within person; normalize weights to mean one.
No calibration fit or hyperparameter search. No-signal probability is the
weighted training class prior. The six EEG-containing arms have identical
feature counts and model settings. M alone and no signal are smaller nested
controls; do not call them equal-dimensional or claim effective capacity is
proven equal by using the same regularization.

## Within-person check, then confirmation

First, for each of the ten development people, train the central arm on R03
and evaluate R07, using only that person's R03 transform. The fixed adequacy
rule is mean participant balanced accuracy >=0.55 and at least six of ten
people showing class-macro log-loss improvement >0.020 nats versus their
training-only prior. This is a diagnostic check, not a discovery search or a
confirmatory significance claim. Failure stops before confirmation EDF GETs,
with a measured model/measurement blocker; no tuning or substitute model.

If adequate, fit all seven logistic arms once on all development R03+R07 rows.
The no-signal arm needs no optimizer. At most seventeen optimizer fits total.
Development outcomes cannot change channels, bands, windows, weights, masks,
participants, thresholds, models, or controls. Numerical nonconvergence or an
invalid row/feature count stops before confirmation prediction.

## Target firewall and one score

Implement only the minimal dedicated acquisition/broker, fixed predictor, and
scorer needed here. Reuse pure numerical primitives where appropriate, never
predecessor coordinators, markers, or live verifiers. The existing
`SealedTargetVault` convention alone is not an operating-system firewall.

The broker alone reads confirmation EDF annotations, seals T1/T2 labels, and
emits label-free features, masks, and opaque row/group IDs. The predictor must
run in an OS-enforced read allowlist with network denied, no child execution,
and no access to raw EDFs, broker memory/files, sealed labels, old data, or
the invoking assistant's unrelated checkout files. Raw annotation strings and
digital/status channels never become features. Demonstrate these access
denials with small generated canaries before real contact; ordinary Python
attribute privacy is insufficient. If this isolation is unavailable, report
that concrete blocker without touching data.

Before first source contact, commit the implementation and fixed dependency
versions; require Base Python and Optional Neuro Readers green. Then execute
directly. This is an automatic evidence check within the approved route, not
another authorization packet, proof closeout, synthetic benchmark, or request.
Freeze the currently installed local Python 3.13.5, NumPy 2.5.2, SciPy 1.18.0,
MNE 1.12.1, and scikit-learn 1.9.0 for execution. Package metadata was checked
without opening data. This request permits no dependency download, version
substitution, paid compute, provider call, or background service.

The predictor fits on development only and writes all eight arms' probabilities
for all twenty confirmation people, together with model/configuration, row-mask,
input and output hashes. Commit and push only a hash-only freeze, excluding
payloads, features, predictions, and targets. Require that exact freeze's two
CI jobs green before a separate scorer receives the sealed targets exactly
once. The scorer cannot fit, select, calibrate, exclude, retry, or change a
prediction. The assistant receives only aggregate results and validity flags.

Any person with fewer than four confirmation trials in either class makes the
whole final experiment incomplete. Report all twenty people and missingness;
never improve the result by dropping someone after target delivery.

Primary loss is participant class-macro natural-log loss with probabilities
clipped to `[1e-6,1-1e-6]`. For each of seven controls define
`d_person = loss_control - loss_central`. The primary conjunction requires
**at least 15 of 20 people with d >0.020 nats on every edge separately**:
the exact one-sided binomial sign-test tail at 15/20 is 0.0206947327 under
P(d>0.020)<=0.5. Ties and nonpositive increments count against passage.
The intersection-union decision tests all seven edges at alpha=.05; it does
not assert the same majority of people wins every edge or test a population
mean. No familywise claim for individual secondary results.

Report every arm's participant balanced accuracy, macro loss, Brier score,
fixed five-bin reliability counts, mean and median paired increments, and
descriptive 95% percentile intervals from 10,000 participant bootstraps using
`random.Random(0)`. Resample the same participant indices across arms.
These intervals are conditional on this fitted development model and are not
independent-cohort replication. Report every edge, not just significant ones.

At scoring, also report each person's fraction of labels preserved by the
fixed derangement. If its mean across people is >=0.75, call that control
ineffective and the conjunction inconclusive regardless of scores. Do not
redraw it. Class-specific visual cues, eye/muscle artifacts, and prior-trial
activity remain unresolved explanations even when every edge passes.

## Resources, consumption, and output

One CPU thread, one worker, one numerical process at a time. Peak process-tree
RSS <=1 GiB; acquisition wall <=30 min; numerical processing <=30 min;
end-to-end wall <=4 h including CI waits. Incremental on-disk cap is 512 MiB:
256 MiB raw +4 MiB source metadata +32 MiB features/targets/predictions
+32 MiB logs/runtime artifacts +128 MiB invocation temporary space +60 MiB
unused headroom. No other data may be duplicated. Generated fixtures <=32 MiB.
Keep total NeuroDecodeKit storage <=20 GiB with the existing 3 GiB untouched
reserve; therefore existing measured allocation +512 MiB +3 GiB must fit.
Require at least 20 GiB filesystem free before acquisition. These smaller
limits do not increase the existing global ceiling. Do not delete old files
to create capacity. Report runtime, peak RSS, GET/body counts, retained/input/
output bytes, trial missingness, and disk use alongside scientific results.

Create one new invocation root exclusively. Before first source contact,
durably record the request/decision/implementation identities and consumption
of EEGMMIDB-SMR-D1-R0. Failure after that boundary is terminal, including
transport, source identity, positive-control, runtime, or firewall failure.
Do not rerun, resume, repair into another real attempt, substitute data, or
reinterpret a transport failure as a biological null. Pure preparation failures
before any durable arm/contact may be corrected only to implement this same
frozen protocol; no model/design changes or new qualification workstream.

One combined final score at most. Keep new raw/derived private evidence within
the invocation root for audit; clean only manifest-listed temporary files
created by this invocation. Do not delete protected evidence or consumption
records. Public repository output is limited to protocol/code, hash-only freeze,
and sanitized aggregate result tables/figures and validity flags. No public
participant rows, raw data, target text, predictions, release, paper submission,
outreach, clinical claim, or claim-promotion action is authorized.

If all edges pass, the strongest new claim is preliminary unseen-person
**cued task-condition information in these EEG features** beyond these seven
specified controls. If an edge fails, the proposed conjunction is unsupported;
report the failed comparisons without calling them proof of causal confounding
or proof that EEG lacks motor information. Neither outcome establishes
peripheral independence, motor intention, language decoding, real-time use,
clinical utility, independent replication, or improvement over historical
low-frequency models evaluated on different people.

## Approval interface

The request and its all-false machine record must first be committed, pushed,
and green in both required jobs. After the assistant names this sole request,
its exact commit and CI, one unambiguous **approve**, **continue**, or **proceed**
binds it. Record the actual words in one additive decision and make that
decision green before implementation/access. Then proceed through the entire
sequence above without another human gate. No maintainer approval has yet
been received for this packet; the earlier general request for results is not
fabricated as approval of its newly narrowed scope.
