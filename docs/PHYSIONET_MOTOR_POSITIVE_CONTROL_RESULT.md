# PhysioNet Motor Positive-Control Result

Date: 2026-08-09

Status: **Complete and consumed at `WO9-V1`; no retry, rerun, post-target
selection, or claim upgrade**

Public aggregate result:
`registries/physionet_motor_positive_control_result.v0.json`

Result file SHA-256:
`017c62162774b5cd32a635f58bb4c503f903a8e901cb2b696efa0890a1040579`

## Evidence Order

The required sequence completed without inversion:

1. Registration `3c00557` became remotely green.
2. The exact Tier C request and authorization became remotely green.
3. Implementation `52b9b15a64972a285efbe630f49600727e836983`
   passed Base Python `93343718364` and Optional Neuro Readers `93343718355`
   in CI `31351728650` before real access.
4. One target-blind execution created 12 per-condition prediction hashes and
   stopped before scoring.
5. Freeze commit `01eeff6e9a5ead1790e0f91aa52a443402eb397c`
   passed Base Python `93345130576` and Optional Neuro Readers `93345130569`
   in CI `31352250838` before the sealed target file opened.
6. The same 45 frozen run-11 targets were delivered and scored once.

No prediction, parameter, threshold, family, channel set, control, exclusion,
or claim rule changed after target delivery.

## Registered Verdict

The ordered router returned **`WO9-V1`** because the selected 8-30 Hz primary
model failed the frozen predictive gate.

```text
selected family:                            fixed_8_to_30_hz_csp_lda
correct:                                    27 / 45
pooled balanced accuracy:                   0.603755
macro participant balanced accuracy:        0.592262
minimum participant balanced accuracy:      0.437500
participants above 0.5:                     2 / 3
one-sided within-participant p:              0.137390
train-only no-signal pooled BA:              0.500000
```

The primary did beat the no-signal prior, but it missed all three decisive
frozen floors: at least 30 correct, pooled balanced accuracy at least 0.65,
and permutation `p <= 0.05`. Its macro participant score also missed the 0.60
floor. This is suggestive above-prior performance, not a positive primary
result.

## Strong Prespecified Secondary Signal

The fixed 0.5-4 Hz shrinkage-LDA comparator produced the strongest held-out
result:

```text
correct:                                    36 / 45
pooled balanced accuracy:                   0.800395
macro participant balanced accuracy:        0.800595
minimum participant balanced accuracy:      0.732143
participants above 0.5:                     3 / 3
one-sided within-participant p:              0.000183
```

This arm was prespecified, fit only on runs 03/07, frozen before run-11 target
delivery, and scored under the same one-shot protocol. It is therefore real
evidence that the held-out EEG recordings contain reproducible low-frequency
information about the left-versus-right task condition for these three people.

It is **not** the registered primary model and is not promoted after seeing the
targets. Its features use all 64 channels, the task is driven by a class-
correlated left/right visual cue, separate EOG and EMG are unavailable, and the
localization/physiology conjunction failed. The result could reflect a mixture
of slow cortical potentials, cue-evoked activity, eye movement, movement, and
other task-locked physiology. It does not identify a brain-specific motor
source.

## Complete Condition Ranking

| Condition | Correct | Pooled BA | Permutation p | Interpretation |
|---|---:|---:|---:|---|
| Low-frequency shrinkage LDA | 36/45 | 0.800395 | 0.000183 | Strong prespecified task-information signal; confound-compatible |
| Frontal/occipital proxy | 28/45 | 0.624506 | 0.093201 | Elevated but below primary significance/accuracy gates |
| Selected 8-30 Hz primary | 27/45 | 0.603755 | 0.137390 | Above prior; registered primary failed |
| Pre-cue model | 26/45 | 0.576087 | 0.157867 | Below 0.60 confound ceiling |
| One-trial displacement | 25/45 | 0.559289 | 0.343231 | Below 0.60 confound ceiling |
| Hemisphere swap | 24/45 | 0.542490 | 0.323029 | Failed the primary gate as required |
| Train-label derangement | 24/45 | 0.538538 | 0.417664 | Below 0.60 confound ceiling |
| Central sensorimotor model | 24/45 | 0.534585 | 0.508881 | Did not localize the strong signal centrally |
| All-zero final signal | 23/45 | 0.514822 | 1.000000 | Deterministic negative control |
| Train-only no-signal prior | 22/45 | 0.500000 | 1.000000 | Frozen no-signal reference |
| Validation-channel derangement | 21/45 | 0.476285 | 0.876495 | Failed the primary gate as required |
| Timing-only model | 21/45 | 0.467391 | 0.763184 | Below 0.60 confound ceiling |

The ranking is descriptive. The router did not select the best final arm after
target opening, and this table does not authorize doing so.

## Physiology And Confounds

The independently frozen mu/beta physiology effect had the registered negative
contralateral-minus-ipsilateral direction in two of three participants and a
pooled effect of `-0.083918`, but the paired sign-flip `p=0.108337` exceeded
the 0.05 gate. The motor-compatible physiology gate failed.

Nine of ten fixed confound components passed. The failed component was the
required central-minus-frontal/occipital balanced-accuracy margin of at least
0.05:

```text
central sensorimotor pooled BA:              0.534585
frontal/occipital proxy pooled BA:           0.624506
central minus proxy:                        -0.089921
required central minus proxy:               >= 0.050000
```

The proxy itself did not cross the complete primary gate, but it outperformed
the central-only model. Combined with the low-frequency whole-head result,
this is exactly why the evidence ceiling must remain task-linked and
confound-compatible rather than neural or motor-specific.

## What We Learned

1. The pipeline can recover a strong held-out task-linked signal from real
   public EEG under strict group, target, hash, and resource controls.
2. The originally selected 8-30 Hz CSP-LDA route was not strong enough on the
   frozen final run.
3. The useful signal appears concentrated in the prespecified slow-potential
   comparator rather than the selected mu/beta model.
4. The registered motor-physiology assay was directionally encouraging but
   inconclusive at three participants.
5. Central sensorimotor localization did not beat the frontal/occipital proxy;
   a brain-specific motor interpretation is therefore unsupported.

This is a meaningful narrowing of the research problem. NeuroDecodeKit is no
longer asking only whether its public EEG machinery works. It now has evidence
that a compact, causal, low-frequency route can carry held-out task information
and a precise reason not to call that signal motor-neural yet.

## Next Hypothesis

Do not rerun, tune, or reopen this three-person final set. The next
needle-moving experiment should be a separately preregistered independent
replication/localization study that treats the low-frequency result as the
hypothesis, not as a retrospective winner. A clean design should:

- use new participants or untouched runs;
- freeze the 0.5-4 Hz whole-head model before final targets;
- compare central, frontal, occipital, and EOG-sensitive channel subsets;
- add cue-side, eye-movement, and response-timing controls where available;
- retain participant/run grouping and a no-signal prior;
- require replication of accuracy and topographic/physiological specificity;
  and
- keep individual outputs private and the result aggregate.

That future study needs its own contract and real-data authorization. It cannot
be manufactured from these consumed outcomes.

## Resources And Access

```text
input payload bytes:                         23,248,224
private generated output bytes:              20,852,334
public result bytes:                         10,443
runtime through freeze:                      3.049897 seconds
scoring runtime:                             6.611857 seconds
total registered runtime:                    9.661659 seconds
peak RSS across stages:                      460,734,464 bytes
classical fits / target-blind inferences:    33 / 45
prediction sets:                             12
raw EDF semantic reads:                      9
real cache reads:                            0
final target deliveries / scoring events:   1 / 1
CPU threads / workers / numerical jobs:      1 / 1 / 1
network bytes / new payload bytes:           0 / 0
retries / reruns:                            0 / 0
producer causal / right context:             yes / 0.0 seconds
decision latency from cue:                   3.0 seconds
end-to-end latency measured:                 no
```

Every resource gate passed. The result publishes no individual prediction,
probability, target, or participant outcome. The private execution artifacts
remain Git-ignored and must not be committed or published.

Final verification passed 45 focused Work Order 9 checks with two expected
optional skips in the broad environment. The complete broad suite ran 1,521
tests with five expected skips, and the isolated registered-classical suite
ran 1,506 tests with 34 expected skips. Ruff, compileall, JSON parsing, result-
hash checks, and diff hygiene passed. Verification did not reopen the private
artifacts or perform another target delivery, score, fit, inference, retry, or
rerun.

## Claim Boundary

Engineering capability added: NeuroDecodeKit completed one preregistered,
resource-bounded, leakage-resistant public EEG experiment from exact payload
verification through remotely green prediction freeze and one aggregate final
score.

Scientific result established: a prespecified causal 0.5-4 Hz whole-head
comparator recovered held-out left-versus-right task information in this
three-person dataset at 0.800 pooled balanced accuracy and `p=0.000183`.

Scientific claim not established: the registered 8-30 Hz primary gate,
motor-compatible physiology gate, and central-over-proxy localization
conjunction failed, so brain-specific motor origin, unseen-person
generalization, typing, language or thought decoding, real-time performance,
portable hardware, home use, assistive benefit, and clinical utility remain
unestablished.
