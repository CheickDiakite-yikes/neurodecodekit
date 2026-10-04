# Imagined-word EEG increment failed; overt peripheral prediction succeeded

## Scientific result — October 2, 2026

The single approved **INNER-SPEECH-OBSERVED-1** attempt completed and scored
once in **245.18 seconds**, including prediction-freeze commit/push and scoring.
The registered imagined-word endpoint **failed**: mean participant log-loss
gain from adding EEG to peripheral/timing features was **-0.003282 nats**,
against a required +0.02. Only **one of ten people** beat every primary control
simultaneously; nine were required. This is a completed negative result for
the fixed comparison, not a parser failure or a proof that EEG contains no
imagined-speech information.

The [complete, unmodified aggregate](../registries/inner_speech_observed_result.v0.json)
retains all ten people, all three conditions and all eight arms, including all
null comparisons and uncalibrated diagnostics. No evaluation was repeated.

## What was actually compared

Exact Status event identities, order and sample positions agreed between the
frozen reader and independent source-compatible decoder in **all ten people**.
All 2,000 nominal slots were accounted for, and all thirty split preflights
passed before any physiological windows were read. The fixed eligibility rule retained **1,993**
trials: 399 pronounced, 756 inner-speech and 838 visualization. Seven unique
incomplete core sequences were excluded: three missing cues, three missing
action markers and one missing relax marker. No word or timestamp was inferred.

Original chronology, nominal fold boundaries and both neighbour embargo levels
were preserved. P contains 77 peripheral features plus 11 timing/availability
features; its dimension normalization is explicitly different from the earlier
consumed attempts. Models, calibration, controls and primary decision stayed
fixed under the [approved protocol](INNER_SPEECH_OBSERVED_ANCHOR_TEST.md).

Each table entry below is **balanced accuracy (%) / class-macro NLL (nats)**,
first calculated per person and then averaged equally across ten people.
These are not pooled-trial accuracy rates. Lower NLL is better.

| Arm | Inner speech | Pronounced | Visualization |
|---|---:|---:|---:|
| Peripheral/timing P | 25.50 / 1.391730 | 83.69 / 0.625141 | 21.46 / 1.394729 |
| P + action EEG (joint) | 24.58 / 1.395012 | 81.44 / 0.721052 | 24.57 / 1.398123 |
| P + cue EEG | 27.28 / 1.397498 | 77.22 / 0.699798 | 24.99 / 1.386150 |
| P + matched late EEG | 23.31 / 1.392727 | 77.94 / 0.749189 | 25.32 / 1.398793 |
| P + deranged EEG | 23.23 / 1.394020 | 74.94 / 0.783251 | 23.66 / 1.398074 |
| Joint, shuffled training labels | 23.21 / 1.394515 | 19.78 / 1.402866 | 23.77 / 1.402126 |
| Uniform | 25.00 / 1.386294 | 25.00 / 1.386294 | 25.00 / 1.386294 |
| Training prior | 16.30 / 1.416898 | 10.50 / 1.478213 | 18.13 / 1.411295 |

## Primary result, without selecting favourable controls

Gain means comparator NLL minus joint NLL; positive favours the joint model.
The same people must pass all five contrasts. Individual sign-test values are
reported as registered, not combined or treated as independent evidence.

| Inner-speech comparator | Mean gain, nats | People with positive gain | One-sided sign p |
|---|---:|---:|---:|
| P | -0.003282 | 5/10 | 0.623047 |
| Deranged EEG joint | -0.000992 | 4/10 | 0.828125 |
| Shuffled-label joint | -0.000497 | 4/10 | 0.828125 |
| Uniform | -0.008718 | 1/10 | 0.999023 |
| Training prior | +0.021886 | 8/10 | 0.054688 |

Only sub-02 passed all five. Beating the training-prior arm does not rescue
failure against uniform, P and the other controls.

Secondary conditions also fail to establish a consistent EEG increment.
Pronounced gain over P is **-0.095911 nats**, positive in 2/10; only sub-01
passes every contrast. Visualization gain is **-0.003394**, positive in 3/10;
only sub-04 passes every contrast. Pronounced joint nevertheless beats uniform,
training prior and label shuffle in 10/10, and deranged EEG in 9/10. Those
positive controls show task information is detectable in that condition,
but do not override the stronger P comparator or establish cortical origin.

Training-only calibration also does not hide a successful imagined-word result.
Uncalibrated mean P/joint NLL is **1.397208 / 1.402017** for inner speech,
**1.114259 / 1.144262** for pronounced, and **1.421600 / 1.413496** for
visualization. These remain diagnostics, not alternative primary endpoints.
The matched late-versus-cue NLL gains are +0.004771, -0.049391 and -0.012643
respectively; they are secondary and do not establish neural origin.

## Belief update and next priority

**Lower confidence in this shortcut:** whole-window channel-band power plus a
small calibrated ridge model did not deliver reliable imagined-word information
beyond peripheral/timing and null controls in this fresh ten-person cohort.
The strong overt P result supports continued interest in peripheral task
prediction as a separate interface direction, not as evidence of thought-to-text.
P includes timing and multiple peripheral channels; this is not a lip-only or
real-time communication demonstration.

**Do not infer an EEG ceiling.** There is no EEG-only arm here, and successful
overt peripheral prediction is not a positive control for neural sensitivity.
The tested spectral representation discards waveform phase and does not retain
an ordered trajectory within the action window. Whether temporal structure
contains useful information is an untested hypothesis, not the explanation of
this negative result.

**Next bounded scientific question:** can one fixed time-resolved EEG
representation recover reproducible word information that the coarse spectral
representation misses, while still beating matched peripheral/timing controls?
Before committing another imagined-word confirmation, demonstrate sensitivity
on a separately authorized development partition with an EEG-only cue/response
positive control. Successful EEG-channel cue decoding would show sensitivity
to a reproducible recorded response, not prove cortical attribution or thought
decoding.
Predeclare one compact temporal model, EEG-only/P-only/joint comparisons,
label-shuffle and EEG-derangement controls, then reserve an untouched partition
for the delayed imagined-word endpoint. No model sweep, language-model rescue
or selection of today's best participant. A cue-decoupled/new-day claim requires
a source that actually supports that design; this dataset slice does not.

This is the next hypothesis to specify, **not an authorized new run**. The
current 1,993 scored trials are consumed confirmation evidence, not a tuning set.
No further data access, fitting or scoring was performed after this result.

## Boundaries and execution evidence

Structural exclusions are not proven missing-at-random; 0.35% excluded does not
bound selection bias. This same-day, within-person, four-word offline comparison
does not prove cortical origin, cue-independent thoughts, arbitrary text,
unseen-person transfer, new-day robustness, prospective usability or clinical
benefit. Both positive and negative findings stay within those limits.

- Implementation: `94c8f16019177461c9500e737eed52c44857cc6c`; both remote CI jobs
  passed before launch ([workflow](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37012256858)).
- Prediction-only freeze: `989ad07f73b25d1aebe562330d988e61bca3f463`, remotely
  verified before scoring; exactly that hash file changed before the score.
- Predictions completed in 127.51 seconds; full attempt in 245.18 seconds;
  recorded peak RSS 68,935,680 bytes. All 2,880 ridge and 720 temperature fits
  completed; one scoring invocation, no failure marker, no retry.
- All 240 arm/condition/person metric groups have finite reported BA and NLL;
  no missing metric was filled with zero. Prior private evidence is unchanged.
- Published aggregate matches the locally completed aggregate byte-for-byte:
  SHA-256 `158d76894bd246842a6c9339563be381cfaf8d13de16283626d767aeadba9eac`.
- Data-quality checks settled decoder agreement and structural eligibility;
  they do not establish biological attribution. Raw recordings, event rows,
  targets, per-trial predictions and model weights remain local.
