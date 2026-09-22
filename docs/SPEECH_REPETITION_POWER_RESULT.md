# Preserving repetition power improves prediction, but not consistently beyond peripheral controls

September 21, 2026. **Calibration discovery, not independent confirmation.**

The fixed comparison completed in **67.468 seconds**. For minimally overt
speech, preserving per-repetition power improved the adaptive EEG-derived
model from **37.73% to 46.38% balanced accuracy**; log loss improved in all
three people. Adding those features to the auxiliary model raised mean BA
from **81.60% to 84.50%**, but improved the primary log-loss metric in only
**one of three people**. The predeclared all-person criterion therefore failed.
For covert speech, adding them worsened log loss in **all three people**.

**Belief update:** waveform averaging was a real representation bottleneck in
this minimally overt comparison, but fixing it did not establish a consistent
increment beyond peripheral prediction. We have a useful small-model improvement,
not a neural-decoding breakthrough or a reason to scale model size yet.

## What was compared

All six calibration recordings and 600 original trials were retained. Matched
768-feature ridge models compared power of the average five repetition
waveforms (evoked) with the average of their separate powers (repetition).
The logarithm followed power averaging. Both conventionally preprocessed
(raw) and additionally adaptive-filtered (filtered) EEG were included.
N is the unchanged 392-feature auxiliary-plus-timing comparator.

The primary split withheld five contiguous 20-trial blocks, embargoing one
neighboring training trial at each boundary. Repetitions stayed together;
scaling used training rows only. This is retrospective within-recording
validation, potentially trained on later blocks, not future-day or online use.
The fixed stratified random split was retained as a secondary check.
See the [prospective plan](../registries/speech_repetition_power_plan.v0.json).

Each cell is equal-person **balanced accuracy (%) / class-macro log loss**.
Lower log loss is better. These are the primary blocked results, not selected
best folds or seeds.

| Model | Minimally overt | Covert |
|---|---:|---:|
| Auxiliary N | 81.60 / 1.258781 | 28.22 / 1.580720 |
| Raw evoked EEG | 37.59 / 1.549347 | 19.73 / 1.622749 |
| Raw repetition EEG | 32.96 / 1.537207 | 18.24 / 1.618908 |
| Filtered evoked EEG | 37.73 / 1.547175 | 15.75 / 1.623188 |
| Filtered repetition EEG | 46.38 / 1.500629 | 20.13 / 1.625366 |
| N + raw evoked | 83.26 / 1.276803 | 25.85 / 1.590655 |
| N + raw repetition | 84.08 / 1.263512 | 25.94 / 1.585114 |
| N + filtered evoked | 80.77 / 1.281103 | 25.50 / 1.593727 |
| **N + filtered repetition: primary** | **84.50 / 1.252961** | **26.43 / 1.597043** |
| Primary with deranged EEG | 78.49 / 1.294017 | 25.63 / 1.586578 |
| Primary with shuffled training labels | 15.48 / 1.652499 | 19.51 / 1.637946 |
| Uniform | 20.00 / 1.609438 | 20.00 / 1.609438 |
| Training prior | 19.09 / 1.673691 | 18.10 / 1.708487 |

The [complete aggregate](../registries/speech_repetition_power_result.v0.json)
preserves **all 24 arms, both split schemes, all six people/condition pairs,
every shuffle and derangement control, and all null findings**. No arm was
removed because it performed poorly. In particular, raw repetition power
improved mean minimally overt log loss while worsening BA: the metrics are
not interchangeable.

## The participant-level test is decisive

Positive gain means the primary model has lower log loss than the comparator.
The required conjunction was improvement over N, N + filtered evoked, its
deranged-EEG and shuffled-label controls, uniform, and training prior in every
person within a condition. The rule was descriptive, not a significance test.

| Condition / person | Gain over N | Gain over joint evoked | Gain over deranged EEG | All six comparators passed? |
|---|---:|---:|---:|---|
| Minimally overt / 1 | -0.008632 | +0.023234 | +0.030107 | No |
| Minimally overt / 2 | -0.000372 | +0.030224 | +0.032328 | No |
| Minimally overt / 3 | +0.026464 | +0.030970 | +0.060735 | Yes |
| Covert / 1 | -0.039540 | -0.002934 | -0.036725 | No |
| Covert / 2 | -0.008494 | -0.002918 | +0.010150 | No |
| Covert / 3 | -0.000937 | -0.004095 | -0.004819 | No |

Mean gain over N was **+0.005820 minimally overt** and **-0.016323 covert**.
The favorable minimally overt mean does not override two individual failures.
The fixed random split gives the same primary conjunction outcome: only
minimally overt person 3 passes; nobody covert does. Mean gains over N there
are +0.002119 and -0.012995, respectively. Filtered repetition versus evoked
EEG log loss improves for all three minimally overt people under both splits.

Across the six bands, condition-pooled coherent/total power ratios are
approximately **19–22%** in both preprocessing branches. These target-free
ratios sum power before division. They show that waveform averaging suppresses
power, not that the suppressed power was neural, useful, or word-specific.

## Next priority: identify what the adaptive readout is using

The adaptive branch first standardizes each EEG trial and then uses EOG and
both lip channels in its NLMS filter. Thus even an EEG-only feature matrix is
not an auxiliary-independent measurement. A better score after that filter
could reflect normalization, retained EEG information, transformed peripheral
information, or mixtures. The current comparison does not separate them.

**Next cheap falsifier:** isolate trial normalization from the auxiliary-fed
filter, and include a fixed sham-EEG input through that same filter. Keep the
same calibration sources, matched readout and whole-trial blocks. If the
apparent advantage survives without informative EEG input, it cannot support
EEG-specific attribution; a negative sham result would not prove neural origin.
This is the next hypothesis to scope and freeze,
not permission from this result to rerun or tune the completed experiment.
Do not choose a winning sham construction after seeing its scores.

The separate practical lead remains the previously observed lip-channel
prediction. A low-channel, new-day, cue-resistant command-interface test would
address usefulness, but needs its own data/experimental scope. Neither this
result nor that lead demonstrates cortical origin, cue-independent thoughts,
silent communication, arbitrary text, clinical utility, prospective live use,
or unseen-person generalization. A null here does not establish an EEG ceiling.

Single label shuffles and cyclic EEG shifts are diagnostics, not calibrated
null distributions. A joint model beating N would mean an increment beyond
this fixed auxiliary representation and model, not independence from every
possible peripheral explanation. Only three people and already-used
development recordings were explored; there is no fresh confirmation.

## Execution and integrity

One invocation at **2d9c97dbd9bec526891d18fdd39c10d3a5db6fd4** after both remote
checks passed: workflow **35673536922**, Base **106575101399**, Optional Neuro
Readers **106575101539**. The preceding CI failure was resolved by preventing
generated-test mocks from retaining large arrays; scientific code and resource
gates were unchanged by that correction. No code changed during the real run.

All 1,320 small ridge fits completed; no deep model, new download, online
recording or consumed confirmation was accessed. Peak observed RSS was
**224,862,208 bytes** (~214.45 MiB); local artifacts **1,300,406 bytes**, plus
the **218,696-byte** aggregate. There is no failure marker or automatic retry.
No waveform/feature cache was retained. Per-trial probabilities remain local
and ignored; only the aggregate and documentation are published.

Result SHA256: `daa18472b86d1348d33350e0862f5eec6b51ab4504c056376e98da3503bd0245`.
The confirmation aggregate remains byte-identical at
`5ca61ce244d9d7ed65ba6a3cebd65b0af49a4782979a8b834008553329087d8c`;
the auxiliary discovery remains byte-identical at
`794711f5f1731485c8d253ec48674a5ad35971dd9ede31876338c55bed4abda9`.
