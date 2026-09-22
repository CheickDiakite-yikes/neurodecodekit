# Word prediction survives replacement of recorded EEG by one fixed waveform

September 22, 2026. **Exploratory calibration result, not fresh confirmation.**

The sham-input falsifier passed for minimally overt speech. One identical
synthetic EEG waveform, processed using each trial's real EOG/lip signals,
reached **49.72% balanced accuracy**. It beat the fixed-sham baseline, its
training-label shuffle, uniform and training-prior controls in class-macro log
loss in **all three people** under blocked validation. No recorded EEG-channel
samples entered those sham features. The complete experiment took **82.907 seconds**.

This changes our interpretation: **this preprocessing can create word-predictive
features from auxiliary inputs without recorded EEG input**. A successful
classifier on its output is therefore not, by itself, evidence of EEG-specific
information. This does not establish that all real-EEG performance is peripheral,
that auxiliary electrodes contain no neural signal, or that adaptive filtering
generally fails.

## Decisive results and retained negatives

Each cell is equal-person **balanced accuracy (%) / class-macro log loss**.
Lower log loss is the predeclared primary metric. Blocked validation withheld
five contiguous 20-trial blocks with one adjacent training trial embargoed at
each boundary; it is retrospective, not past-to-future. The random split is
the unchanged stratified five-fold secondary check.

| Representation / model | Blocked minimally overt | Blocked covert | Random minimally overt | Random covert |
|---|---:|---:|---:|---:|
| Fixed sham, normalization only | 19.09 / 1.614194 | 18.10 / 1.615524 | 19.39 / 1.611693 | 19.72 / 1.613275 |
| **Fixed sham + real EOG/lip-fed filter: primary** | **49.72 / 1.503615** | **21.19 / 1.600827** | **49.61 / 1.499229** | **25.02 / 1.594554** |
| Primary, training labels shuffled | 20.91 / 1.608362 | 23.01 / 1.614901 | 19.32 / 1.616367 | 17.97 / 1.610189 |
| Uniform | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 |
| Training prior | 19.09 / 1.673691 | 18.10 / 1.708487 | 19.39 / 1.657124 | 19.72 / 1.694319 |
| Recorded EEG, conventional preprocessing | 32.96 / 1.537207 | 18.24 / 1.618908 | 37.18 / 1.532538 | 20.68 / 1.625370 |
| Recorded EEG, normalization only | 44.99 / 1.492797 | 15.92 / 1.623789 | 42.91 / 1.491334 | 18.53 / 1.628606 |
| Recorded EEG, original adaptive filter | 46.38 / 1.500629 | 20.13 / 1.625366 | 41.84 / 1.502765 | 20.23 / 1.624095 |
| Auxiliary/timing N | 81.60 / 1.258781 | 28.22 / 1.580720 | 86.31 / 1.244240 | 25.02 / 1.581361 |
| N + normalized recorded EEG | 85.66 / 1.250870 | 27.45 / 1.591324 | 88.57 / 1.238048 | 24.49 / 1.595703 |
| N + adaptive-filtered recorded EEG | 84.50 / 1.252961 | 26.43 / 1.597043 | 87.96 / 1.242122 | 25.17 / 1.594356 |
| N + adaptive-filtered sham | 84.71 / 1.268783 | 25.99 / 1.579891 | 86.57 / 1.256507 | 27.90 / 1.575785 |

Sham BA exceeds real adaptive-EEG BA in the minimally overt mean, but its
blocked log loss is slightly worse: **1.503615 versus 1.500629**. Do not turn
that accuracy comparison into a claim of superiority on the primary metric.

The sham's primary conjunction is evaluated per person, not rescued by a mean:

| Condition / person | Sham BA (%) | Log-loss gain over uniform | Gain over label shuffle | All four controls passed? |
|---|---:|---:|---:|---|
| Minimally overt / 1 | 52.39 | +0.119440 | +0.113425 | Yes |
| Minimally overt / 2 | 41.99 | +0.059893 | +0.057689 | Yes |
| Minimally overt / 3 | 54.79 | +0.138137 | +0.143128 | Yes |
| Covert / 1 | 21.19 | +0.023685 | +0.023773 | Yes |
| Covert / 2 | 21.37 | +0.002531 | +0.015621 | Yes |
| Covert / 3 | 21.02 | -0.000384 | +0.002828 | No |

**Covert fails the primary all-person rule.** Person 3 does not beat uniform;
the other gains are small. All three covert people pass with random folds,
which does not override the blocked failure. No useful covert interface or
general covert decoding has been established.

The secondary real-EEG joint model fails its expanded seven-comparator
conjunction in **every person in both conditions and both split schemes**.
It beats the joint sham in all three minimally overt people, so the result
does not erase every distinction between real EEG and sham. But it fails N
in people 1 and 2, and normalization-only in people 2 and 3 under blocked
validation. No consistent conditional EEG increment is demonstrated.

Normalization alone has lower mean minimally overt log loss than the adaptive
filter, both with and without N and under both split schemes. The EEG-only
advantage holds in two of three people, not all three. There is no demonstrated
consistent NLMS-specific benefit here. N + normalization improves over N in
only two people with blocked folds (one gain is just **0.000065**) and one with
random folds; its **85.66%** mean is not a validated general improvement.

## What makes the sham informative

One Gaussian 128-by-1626 template, seed 20260922, was conventionally filtered
with zero auxiliary inputs and reused identically in every trial and recording.
It used no recorded EEG amplitude, spectrum, normalization denominator, labels,
person identifier or trial timing. The only varying input to the sham adaptive
filter was the real conventionally filtered EOG and two lip channels. Original
NLMS settings and per-trial state reset were unchanged.

Every representation then used the same 128-by-six repetition-power features,
the same tiny ridge model, train-only scaling and original-trial splits. All
five repetitions stayed together. The fixed normalized-sham features alone
were uninformative; adding them to N reproduced N's metrics, as expected.
The observed pathway is through the auxiliary-fed processing, not recorded EEG
entering the sham or a different model capacity. It is not a causal attribution
of the physical source recorded by the auxiliary electrodes.

All six calibration recordings, **600 trials, 29 arms and both split schemes**
are preserved in the [complete aggregate](../registries/speech_adaptive_attribution_result.v0.json),
including every derangement/shuffle control and negative outcome. The
[fixed plan](../registries/speech_adaptive_attribution_plan.v0.json) remains
unchanged. These already-used development recordings are not fresh confirmation;
single shuffles and cyclic shifts are diagnostics, not significance tests.

## Belief update and next priority

Before: improved adaptive-EEG power features might reflect better preservation
of recorded EEG information. After: a concrete alternative pathway has now
been demonstrated without recorded EEG samples, and simple normalization is a
competitive alternative. Do not label adaptive output as isolated brain signal.
Keep the original pipeline only where needed for faithful reference reproduction.

**Next neural test:** use preprocessing that does not consume peripheral
channels, then require its incremental prediction to survive a stronger,
matched auxiliary comparator and whole-trial temporal controls. Test a fixed
time/frequency decomposition of normalization-only EEG to ask where any
remaining increment resides; include all bands/windows rather than selecting
the best after inspection. That requires its own compact frozen discovery
scope; this result does not authorize another invocation or confirmation reuse.

The practical shortcut is still the strong low-channel peripheral lead, not
calling peripheral prediction brain decoding. A separately scoped future-day,
cue-resistant command-interface test would address real usefulness. Neither
lane yet establishes cortical origin, cue-independent thoughts, silent
communication, arbitrary text, clinical utility, prospective live operation
or unseen-person generalization.

## Execution and integrity

One invocation at **70946c7b5c1be34a670d62eda9a6735f248cd005**, after 117 local
speech tests, Ruff and independent static review. Both remote jobs passed
before execution: workflow **35737036117**, Base **106776831023**, Optional
Neuro Readers **106776830859**. No scientific code changed during the run.

All **1,620 ridge fits** completed: 900 with recorded-EEG features, 600 with
sham features and 120 auxiliary-only. Runtime **82.907 seconds**; peak observed
RSS **225,517,568 bytes** (~215.07 MiB); local artifacts **1,518,540 bytes**,
plus the **284,793-byte** aggregate. No failure marker, automatic retry, deep
model, new download, online recording, or reopening of the consumed confirmation.
No waveform/feature cache was retained; local per-trial probabilities are not
published. Only aggregate evidence and documentation are committed.

Aggregate SHA256: `9e28a48e7fbb88eafee93b9955ee11a4184a5bf762801cf6cf9bccb51496826d`.
The previous confirmation, auxiliary and repetition-power aggregates remain
byte-identical; their hashes are recorded in the new aggregate.
