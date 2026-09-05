# A collection that can answer the motor-attribution question

Date: 2026-09-05

**Design specification, not an activated experiment or a new result.** This is
the prospective-collection fallback requested in the current handoff. It does
not reopen any consumed source, change an existing contract, authorize people
or hardware, or request approval of an unspecified acquisition. No frontier,
qualification, implementation, or additional status registry is introduced.

## The blocker established this turn

There is no currently authorized untouched cohort for the complete comparison.
The tracked activation result records zero scientific-source requests, neural
bytes, model fits, or scores. The two pre-existing workspace changes were
preserved. No other NeuroDecodeKit task was active when this file was written.

The existing [public synthesis](PUBLIC_MOTOR_CROSS_COHORT_SYNTHESIS_RESULT.md)
supports held-out-run motor-task information. Its three registered spatial
candidates did not outperform their strongest available spatial comparator;
none of those cohorts supplies the required task-relevant EMG control.

A bounded primary-literature review found no **verified eligible** fresh
cohort. This is not an exhaustive finding that no such public dataset exists:

| Candidate | Reason it cannot presently supply the complete experiment |
|---|---|
| WAY-EEG-GAL | Twelve people cannot provide five development plus ten untouched confirmation people; dedicated recorded EOG is unestablished. |
| 2026 grasping-box dataset | Fourteen people are below that split floor; the described release does not establish retained EOG and the earlier instruction/pre-instruction windows needed here. |
| 2026 sit/stand dataset | Twenty-two people and bilateral EMG are promising, but transition direction is tied to initial posture; the instruction/event scheme does not establish cue-independent action labels. |
| Jeong2020 wrist execution | Twenty-five people and all three recording modalities, but the assigned class is specified by the visual instruction. No within-instruction target-breaking derangement exists. |

Jeong2020 was the sole fresh candidate advanced to detailed paper-only review.
Its paper describes a three-second class-specific cue followed by execution.
For the **assigned** target Y and full instruction C, Y=f(C), hence H(Y|C)=0.
This is a design inference, not a measurement of participants' actual actions.
Removing C or scoring EMG-derived labels would change the question or create a
circular comparator. Two independent critics rejected acquisition for this
unchanged claim. No candidate manifest, header, signal, or target was opened.

Sources: [WAY descriptor](https://www.nature.com/articles/sdata201447),
[grasping-box descriptor](https://www.nature.com/articles/s41597-026-07242-y),
[sit/stand descriptor](https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giag065/8698245),
[Jeong2020 experimental paradigm](https://pmc.ncbi.nlm.nih.gov/articles/PMC7539536/).

## Minimum proposed measurement

Recruit 50 healthy consenting adults through an appropriately approved lab:
10 development and 40 confirmation people, assigned before recording by a
fixed enrollment order. Confirmation people contribute nothing to fitting,
scaling, thresholds, feature selection, or calibration. Independent replication
is a later cohort, never a new split of these same people.

Use a generic go cue that contains no left/right instruction. With both arms
supported, the participant chooses a left or right index-button press three
to five seconds later. Separate physical switches provide action identity and
time; neither comes from EEG or EMG. Collect 120 twelve-second trials in six
blocks and five minutes of calibration/rest recording per person. Encourage
varied choices without a deterministic alternation or target-specific feedback.
Do not promise balanced classes from voluntary choice.

Record 32 scalp EEG channels, including fixed bilateral central and posterior
coverage, four EOG channels, and eight bipolar EMG channels covering both
active hands/forearms. A proposed EMG roster is bilateral flexor digitorum
superficialis, extensor indicis, flexor carpi radialis, and extensor carpi
radialis. A lab must confirm electrode placement, synchronization and sensor
availability before the protocol is executable. Record actual coordinates,
units, hardware reference and clock timing. Do not use common-average
rereferencing that mixes the compared scalp regions. Recorded EMG coverage
does not establish absence of every possible muscle artifact.

Use 500 Hz EEG/EOG and 1,000 Hz EMG. Candidate EEG is the half-second window
from 750 to 250 ms before switch closure. This is **offline switch-locked**
information; the future switch time is supplied to every arm. It is neither
a continuous decoder nor automatically a pre-EMG or intention measurement.

## One comparison, one scoring event

Keep the seven requested arms: N+C, N, N+posterior, N+pre-cue,
N+cue, N+shifted-C, and N+deranged-C, plus a training-only no-signal prior.
N is identical in every arm: joint EOG and EMG features from the union of
all compared windows, generic cue timing, action latency and trial ordinal.
Switch identity, target-coded events and participant identity are not features.

Use equal-duration EEG windows, equal-dimensional spatial blocks, train-only
scaling and one fixed L2 logistic model (C=0.1); no model or seed search.
Pre-cue is [-0.5,0) seconds relative to go; cue is [0,0.5). The shifted arm
uses continuous EEG 1.5 seconds earlier than the candidate window. Preserve
the common row set and N. Derangement must preserve person and block while
breaking row correspondence with a frozen minimum displacement; never choose
its mapping from target agreement. Exact channel pairs, feature extraction,
derangement, missingness, positive-control thresholds and software identity
must be frozen in the one complete execution packet, not improvised after
outcomes. They are intentionally not claimed to be implemented here.

A separate restricted broker must strip target-coded events and digital
channels, expose only allowlisted signals and target-free structural IDs, and
seal confirmation labels from both predictors and adaptive analysis. Freeze
all ordered probability vectors and their hashes before a single scorer reads
confirmation labels. No refitting, target-conditioned exclusion or rescoring.
Use development-only held-run positive controls; failed sensitivity stops
before confirmation. Class shortages and missingness must never be repaired
by dropping unfavorable confirmation people.

Primary inference: for each person and each of six edges, compute the
comparator minus candidate class-balanced natural-log loss. For each edge
separately, require a one-sided exact sign-test p <= 0.05 for participant
increments above 0.020 nats, counting ties as nonpositive; all six tests must
pass. This tests a majority separately on each edge, not necessarily the same
majority on all edges, and does not test a population-mean effect. Report mean
increments and bootstrap intervals
separately, alongside participant-balanced accuracy, Brier score, calibration,
class counts, missingness and resource measurements. A failed edge prevents
the conjunction; it does not by itself prove a confound caused the failure.

Exact planning arithmetic (not empirical power): with 10 confirmation people,
9 must exceed the margin, giving 37.581% per-edge power if the true
person-success probability is 0.8. With 40 people, 26 must exceed it: 99.208%
per-edge power and at least 95.250% for all six edges by a union bound, without
assuming edge independence. The 0.8 effect-consistency assumption remains
unproven; ten development people cannot establish it precisely.

## Resources and the concrete external dependency

At float32 storage, the proposed signal rate is
4*((32+4)*500+8*1000)=104,000 bytes/second. Fifty people at
(120*12+300)=1,740 seconds each require **9,048,000,000 signal bytes**
(8.427 GiB). This excludes file headers, timestamps and unexpected overhead;
their exact measured total must fit the unchanged 12 GiB payload allocation.
The remaining allocations stay 2 GiB temporary, 2 GiB derivatives/predictions,
1 GiB atomic output and 3 GiB untouched reserve. Preserve the separate 20 GiB
filesystem-free floor. Use one numerical worker/thread, no paid compute, and
the existing 4 GiB RSS/24-hour analysis ceiling. Lab acquisition time, cost
and human-participant approval are separate requirements, not hidden inside
the compute allowance. Delete only newly created temporary files when allowed.

The next result-bearing action is this synchronized collection followed by
the frozen comparison. A lab, equipment access, applicable ethics/consent
approval, recruitment feasibility and a concrete budget are not yet supplied.
Those facts are necessary to prepare an honest single end-to-end Tier C
decision; a short-form approval cannot create them. Once they are available,
one packet should cover source verification/collection, bounded acquisition,
preprocessing, the firewall, compact fitting, prediction freeze, one score and
temporary cleanup, with no further human micro-gates inside that scope.

Success would support only preliminary participant-generalizing central-scalp
action information beyond these recorded controls under this method. Brain
origin, intention, language decoding, independent replication and live utility
would remain unproven. No new neural evidence was produced in this turn.
