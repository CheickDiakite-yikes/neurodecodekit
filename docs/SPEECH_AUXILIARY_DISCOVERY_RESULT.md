# The useful calibration signal survives in lip and eye channels

September 21, 2026. **Exploratory result, not a new confirmation.**

The nine-second auxiliary ablation changes our leading explanation: useful
minimally overt word prediction is available in lip and EOG recordings without
DISPLAY, timing or EEG. Lip-only balanced accuracy was **79.98%**, EOG-only
**66.22%**, against a five-class 20% baseline. Both beat uniform, training prior
and their matched label-shuffle controls in class-macro log loss in all three
people. DISPLAY, timing and microphone models did not meet that threshold.

This supports peripheral-channel prediction as a concrete research lead. It
does not establish the causal physical source of those recordings or explain
the previously scored online result. No online file was opened or rescored.

## Complete result, including nulls

All six calibration recordings, 600 original trials, both conditions and all
18 arms completed. Primary validation withheld contiguous 20-trial blocks with
one adjacent training trial embargoed at each boundary. Repetitions stayed
together, and scaling used training rows only. This retrospective validation
can train on later blocks; it is not past-to-future or online validation.

Each cell below is **equal-person balanced accuracy (%) / class-macro log loss**.
Lower log loss is better; it is the predeclared interpretation metric. All
person-level scores, fold counts, split hashes and gains are retained in the
[complete aggregate](../registries/speech_auxiliary_discovery_result.v0.json).

| Arm | Blocked minimally overt | Blocked covert | Random minimally overt | Random covert |
|---|---:|---:|---:|---:|
| Timing T | 19.14 / 1.612423 | 18.38 / 1.616714 | 17.56 / 1.615047 | 19.85 / 1.617287 |
| DISPLAY D | 17.12 / 1.632873 | 21.44 / 1.618352 | 16.28 / 1.634576 | 21.27 / 1.618709 |
| DISPLAY + timing DT | 17.44 / 1.630253 | 21.10 / 1.617629 | 17.44 / 1.635274 | 19.88 / 1.619238 |
| Microphone M | 23.92 / 1.621667 | 18.95 / 1.633970 | 21.26 / 1.634975 | 18.08 / 1.628317 |
| EOG E | 66.22 / 1.369858 | 18.36 / 1.634433 | 65.98 / 1.355601 | 19.93 / 1.639709 |
| Lip channels L | 79.98 / 1.235862 | 31.43 / 1.557645 | 82.77 / 1.213490 | 31.50 / 1.568913 |
| Peripheral bundle P | 84.26 / 1.236515 | 28.83 / 1.574910 | 87.73 / 1.219082 | 26.72 / 1.578344 |
| All auxiliary + timing N | 81.60 / 1.258781 | 28.22 / 1.580720 | 86.31 / 1.244240 | 25.02 / 1.581361 |
| T shuffled | 22.28 / 1.611615 | 19.90 / 1.618416 | 20.68 / 1.607928 | 20.15 / 1.613038 |
| D shuffled | 19.79 / 1.625176 | 17.33 / 1.623453 | 22.76 / 1.613191 | 20.65 / 1.617973 |
| DT shuffled | 17.97 / 1.623231 | 18.19 / 1.626362 | 23.10 / 1.611601 | 20.58 / 1.616405 |
| M shuffled | 20.67 / 1.627789 | 18.18 / 1.636125 | 18.28 / 1.621782 | 17.13 / 1.640463 |
| E shuffled | 19.91 / 1.626156 | 19.42 / 1.648526 | 23.10 / 1.621016 | 19.88 / 1.668842 |
| L shuffled | 16.14 / 1.656601 | 19.10 / 1.633412 | 19.06 / 1.615754 | 21.11 / 1.629136 |
| P shuffled | 16.22 / 1.652473 | 18.03 / 1.645004 | 19.53 / 1.619322 | 17.09 / 1.654162 |
| N shuffled | 17.13 / 1.651751 | 17.81 / 1.642617 | 19.66 / 1.617265 | 20.18 / 1.651410 |
| Uniform | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 | 20.00 / 1.609438 |
| Training prior | 19.09 / 1.673691 | 18.10 / 1.708487 | 19.39 / 1.657124 | 19.72 / 1.694319 |

P contains microphone, EOG and both lip channels. N adds DISPLAY and timing.
Random means the fixed stratified five-fold scheme, not a selected best seed.
One matched training-label shuffle per fold is a diagnostic, not a p-value.

Under blocked validation, E, L, P and N clear all three controls in all three
minimally overt participants. T, D, DT and M each have worse log loss than
uniform in every participant. The same four-arm success set holds with random
folds; the minimally overt peripheral signal does not disappear when random
trial mixing is removed.

**Covert remains unresolved:** no modality passes the all-three-person rule
under either split scheme. Blocked lip-only BA is 48.63%, 24.80% and 20.85% for
people 1–3; its log loss is worse than uniform in person 3. Its 31.43% mean must
not be presented as a general covert-speech result. In minimally overt speech,
lip-only BA is 92.55%, 77.57% and 69.84%; EOG is 61.30%, 63.00% and 74.37%.

## Belief update and next scientific priority

Before this test, display/time structure and peripheral physiology were both
plausible explanations for the strong auxiliary comparator. **Within these
calibration recordings and fixed features, the latter is now the stronger
lead.** This is not causal attribution: EOG may record task-linked gaze or other
activity, and lip channels may mix signals. Weak DISPLAY features do not rule
out visual-task effects in other channels; weak microphone features do not prove
silence. The physical DISPLAY sensor is still unverified.

There is a second, testable shortcut worth pursuing before another large model:
the prior compact EEG features were computed after averaging five repetition
waveforms, while auxiliary features also retained full-trial energy. See
`feature_matrices` in `scripts/run_speech_reproduction.py`. That asymmetry leaves
an untested explanation for the EEG null: averaging can discard activity that
is not phase-aligned across repetitions.

**Next cheap scientific test:** on development calibration only, compare power
of the averaged EEG waveform with average per-repetition EEG power, using
matched feature counts, fixed small ridge models and whole-trial blocked folds.
Require an EEG increment over the complete auxiliary baseline and a
deranged-EEG control. This is a hypothesis, not a result or execution authority
from this document; freeze its own bounded scope first. It must not retune or
rescore the consumed online evaluation. A null would reduce the case for an
architecture escalation; a consistent increment would justify fresh confirmation.

Separately, the lip-only result makes a low-channel peripheral command interface
a plausible translation direction to investigate. It is not demonstrated
silent communication, clinical utility, arbitrary text or a deployable device.
New-day, cue-resistant confirmation and any human/hardware work require their
own scope. The neural goal remains information beyond cheaper peripheral
explanations, not relabeling peripheral success as brain decoding.

Model dimensions and dimension-normalized regularization differ across these
modality arms, so rankings do not measure unique information. P has higher mean
BA than L, but L has marginally lower mean log loss; neither establishes a
population-level winner. Only three people were explored, on already-used
development recordings. No significance or unseen-person claim is made.

## Execution and integrity

One invocation at implementation **b705dc59a52aea4a73bd0aa758a433192ee03ae1**;
95 generated speech regression tests and Ruff passed. Both remote CI jobs
passed before execution: workflow **35667592071**, Base **106556674375** and
Optional Neuro Readers **106556674627**. No scientific code changed during
execution. The [prospective plan](SPEECH_AUXILIARY_DISCOVERY.md) remains retained.

Runtime through result construction: **8.828 seconds**; peak observed RSS
**216,961,024 bytes** (~206.91 MiB); local generated artifacts **959,088 bytes**,
plus the **168,474-byte** committed aggregate. The 960 tiny ridge fits, held-out
predictions and metric calculations took about **0.326 seconds** in total;
source extraction took about **4.610 seconds**. All work stayed within the
ten-minute / 1 GiB / 32 MiB envelope. No new downloads, EEG fits or online reads.
Libraries: NumPy 2.3.5, SciPy 1.18.1, MNE 1.12.1, scikit-learn 1.9.1.

Only aggregate results are publishable here; local per-trial probabilities are
ignored and not uploaded. There is no failure marker or automatic retry.
Discovery aggregate SHA256:
`794711f5f1731485c8d253ec48674a5ad35971dd9ede31876338c55bed4abda9`.
The previous confirmation aggregate remained byte-identical:
`5ca61ce244d9d7ed65ba6a3cebd65b0af49a4782979a8b834008553329087d8c`.
