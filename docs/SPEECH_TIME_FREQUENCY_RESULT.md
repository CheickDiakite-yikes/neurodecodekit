# Higher task accuracy, but no consistent EEG increment on the primary metric

September 22, 2026. **Exploratory development result; not fresh confirmation.**

With EEG preprocessing independent of lip/eye inputs, the primary joint model
reached **89.75% minimally overt balanced accuracy**, compared with **85.62%**
for the enriched auxiliary-only model under blocked validation. BA increased
in all three people with blocked folds, but only two with random folds.
However, the predeclared class-macro log-loss improvement held in only **one
of three people**. The all-person primary criterion failed in both conditions,
and **none of the nine preset EEG views passed every control in all three
people**, under either split scheme. All 600 trials completed in **158.594 seconds**.

This is a useful distinction: top-choice accuracy improved, but consistent
improvement in probability prediction was not established. Neither metric
should be hidden, and the secondary accuracy result cannot replace the failed
primary endpoint. We have a candidate predictor worth testing under fresh
conditions, not a demonstrated neural-decoding breakthrough.

## Fixed comparison and all nine views

EEG used only its own gain correction, notch, common-average reference,
bandpass and full-trial normalization. No adaptive filter, sham or auxiliary
statistic entered EEG preprocessing. N retains the original 392 auxiliary and
timing features. A adds 300 raw/normalized per-repetition auxiliary power
features, for 692 total; it is an enriched comparator, not guaranteed to be
stronger for every person. Both remain required controls.

Each cell is equal-person **balanced accuracy (%) / class-macro log loss**;
lower log loss is better. All-band EEG has 768 features; each single band has
128. Early and late use the first and last two repetitions, respectively.

| Model | Blocked minimally overt | Blocked covert | Random minimally overt | Random covert |
|---|---:|---:|---:|---:|
| Original auxiliary N | 81.60 / 1.258781 | 28.22 / 1.580720 | 86.31 / 1.244240 | 25.02 / 1.581361 |
| Enriched auxiliary A | 85.62 / 1.256028 | 32.19 / 1.565551 | 88.75 / 1.239526 | 29.87 / 1.566080 |
| **A + full/all EEG: primary** | **89.75 / 1.252182** | **27.67 / 1.578166** | **91.03 / 1.238520** | **27.87 / 1.581350** |
| A + 2–4 Hz EEG | 84.85 / 1.271609 | 27.93 / 1.580585 | 88.88 / 1.253478 | 29.40 / 1.569789 |
| A + 4–8 Hz EEG | 83.47 / 1.262813 | 29.16 / 1.579291 | 84.49 / 1.253012 | 26.22 / 1.580279 |
| A + 8–13 Hz EEG | 85.69 / 1.264177 | 30.38 / 1.576978 | 88.73 / 1.249435 | 30.80 / 1.578747 |
| A + 13–30 Hz EEG | 88.88 / 1.253784 | 28.75 / 1.575714 | 89.53 / 1.242381 | 29.00 / 1.580580 |
| A + 30–60 Hz EEG | 85.46 / 1.255380 | 28.40 / 1.580289 | 86.32 / 1.243278 | 26.35 / 1.585421 |
| A + 60–118 Hz EEG | 85.35 / 1.249784 | 31.61 / 1.571730 | 86.23 / 1.238195 | 28.94 / 1.577421 |
| A + early EEG | 86.12 / 1.274949 | 28.54 / 1.577083 | 87.57 / 1.261528 | 27.72 / 1.580174 |
| A + late EEG | 87.72 / 1.265067 | 30.08 / 1.565335 | 88.52 / 1.251880 | 31.35 / 1.566897 |
| Primary, EEG deranged | 79.84 / 1.286804 | 30.33 / 1.572943 | 83.33 / 1.280744 | 29.51 / 1.570278 |
| Primary, training labels shuffled | 17.84 / 1.644393 | 20.94 / 1.628416 | 22.06 / 1.610495 | 20.69 / 1.634866 |
| A, training labels shuffled | 16.56 / 1.647236 | 19.23 / 1.633954 | 20.41 / 1.615564 | 19.99 / 1.634379 |
| Uniform | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 |
| Training prior | 19.09 / 1.673691 | 18.10 / 1.708487 | 19.39 / 1.657124 | 19.72 / 1.694319 |

The [complete aggregate](../registries/speech_time_frequency_result.v0.json)
retains all **51 arms, six participant/condition pairs, both schemes and every
shuffle/derangement result**. Nothing was dropped or selected as a new primary.
The full/all EEG-only scores exactly reproduce the preceding normalization-only
readout: 44.99% blocked minimally overt BA and 15.92% covert BA.

## Why the primary failed despite better accuracy

Positive gain means lower primary log loss than the comparator. Success
required beating A, N, the joint deranged-EEG and label-shuffle controls,
uniform and training prior in every person within a condition.

| Blocked condition / person | A BA (%) | Joint BA (%) | Log-loss gain over A | Gain over N | All six controls passed? |
|---|---:|---:|---:|---:|---|
| Minimally overt / 1 | 92.45 | 94.36 | -0.021164 | -0.003503 | No |
| Minimally overt / 2 | 82.25 | 85.13 | -0.001384 | -0.016640 | No |
| Minimally overt / 3 | 82.15 | 89.75 | +0.034087 | +0.039938 | Yes |
| Covert / 1 | 48.57 | 41.04 | -0.031891 | -0.002889 | No |
| Covert / 2 | 25.76 | 18.64 | -0.014334 | +0.005342 | No |
| Covert / 3 | 22.25 | 23.34 | +0.008382 | +0.005209 | Yes |

Mean primary gain over A was **+0.003846 minimally overt** and **-0.012614
covert**. Under random folds, gains were +0.001006 and -0.015269; the full
conjunction passed only minimally overt person 3 and no covert person.
Log loss evaluates the probabilities, not just the highest-ranked label.
These aggregates do not diagnose why top-choice accuracy and log loss diverged, and no
post-outcome probability calibration or endpoint switch was attempted.

No individual band or repetition-position view supplies an all-person rescue.
The late/covert view passes in two people under blocked folds, but only one
under random folds; it remains a negative all-person result. The enriched
auxiliary model itself improves log loss over N in two people per condition,
not all three. Its 32.19% covert BA is not a general covert-decoding result.

## Belief update and next scientific priority

The earlier [sham result](SPEECH_ADAPTIVE_ATTRIBUTION_RESULT.md) exposed a
predictive auxiliary-to-processed-feature pathway. Removing that pathway here
did not eliminate the minimally overt task-accuracy lead, but neither broad
nor preset narrower EEG views establish a consistent increment on the primary
metric. Auxiliary-independent preprocessing removes that particular confound;
it does not remove physiological artifacts already recorded in EEG electrodes.

**Stop expanding band/window/model searches on this cohort.** The next useful
milestone is a fixed auxiliary-only versus auxiliary-independent EEG-plus-
auxiliary comparison under a genuinely new recording context/day and controlled
cue conditions. Retain both accuracy and proper probability scoring; freeze
their roles before any new outcomes. This tests whether the observed accuracy
gain transfers, rather than making this reused benchmark look progressively
better. Fresh data/evaluation needs its own exact scope and authorization;
the already-consumed online recordings remain closed.

The peripheral-only command-interface route remains a separate practical lead.
Neither route yet demonstrates cortical origin, cue-independent thoughts,
silent communication, arbitrary text, clinical utility, prospective live use
or unseen-person generalization. These small, repeatedly explored calibration
data cannot establish an EEG information ceiling.

Blocked folds are retrospective contiguous 20-trial holds with one adjacent
training trial embargoed per boundary, not past-to-future. Early/late features
share whole-trial noncausal filtering and normalization; they do not localize
when a signal arose. Different band feature counts alter regularization
geometry. The nine comparisons are descriptive, not multiplicity-adjusted
inference, and single shuffles/shifts are not calibrated null distributions.

## Execution and integrity

One invocation at **dd8ca3c1c512fe75dd982aca21a2e3e26fe90b9e** after 124 local
speech tests, Ruff, independent static review and both remote jobs: workflow
**35746004097**, Base **106807687887**, Optional Neuro Readers **106807688343**.
Scientific code stayed unchanged during execution.

All **2,940 small ridge fits** completed; runtime **158.594 seconds**, peak
observed RSS **226,095,104 bytes** (~215.62 MiB), local artifacts **2,769,522
bytes** plus the **409,248-byte** aggregate. No failure, retry, deep training,
new download, online-file access, or confirmation reopening. Waveforms/features
were not cached; per-trial probabilities remain local and are not uploaded.

Independent aggregate review verified all 612 endpoints and 828 reported gains.
All 72 shared baseline/EEG metric objects and 60 fold records match the prior
run exactly. All four earlier scientific aggregates remain byte-identical.
Result SHA256: `127a1dd0ac98281d8a486c104847f701019f27c5cef8fc3062802eadb90a9553`.
