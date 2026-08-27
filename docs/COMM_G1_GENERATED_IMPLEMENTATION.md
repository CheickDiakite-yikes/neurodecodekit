# COMM-G1 Generated Implementation

**Date:** 2026-08-27  
**Status:** implementation ready; official qualification waits for exact remote-green proof  
**Scientific value:** none

## What was implemented

COMM-G1 now has an isolated generated-only control plane:

- `src/neurodecodekit/experiments/comm_g1_generated.py` implements strict
  generated rows, causal spectral features, participant-held-out capabilities,
  source-only nuisance residualization, Amendment 1 derangement, ten frozen
  control arms, a compact classifier, a sealed target vault, aggregate
  prediction freeze, isolated scorer, no-clobber output, resource gates, and 35
  independently triggered refusal cases.
- `src/neurodecodekit/comm_g1_cli.py` exposes only `plan`, `qualify`, and
  aggregate `inspect`. It has no real path, URL, request, download, stream,
  provider, device, or real-scoring command.
- `tests/test_comm_g1_generated_implementation.py` covers deterministic fictional
  arrays, identities, masks, timestamps, channel roles and geometry, causal
  feature signatures, strict split binding, no-fixed-point derangement, exact
  schedules, shortcut placement, target ordering, tamper detection, output
  limits, and claim boundaries.

NumPy and scikit-learn remain optional and are imported only inside numerical
functions. The dependency-free base package can import the module and use the
planning CLI without either dependency.

## Generated fixture and model boundary

The fictional cohort contains six participants, three sessions, four classes,
and two repeats per class and session. Each row contains 128 samples at 128 Hz
from eight fictional EEG, four EOG, and two oral-EMG channels. Channel names,
roles, available fictional geometry, timing, true length, and padding mask are
validated before feature extraction. No target or label parameter exists on
the causal feature producer.

One positive fixture injects class information into residual central EEG. Seven
negative fixtures place information only in EOG, oral EMG, posterior EEG, cue,
timing, nowhere, or a mixed nuisance path without a residual increment. Only
the positive fixture executes the registered 60-update model schedule. Negative
fixtures receive deterministic source-placement checks, so they cannot silently
expand the registered schedule to 480 fits.

Amendment 1 is enforced exactly: source residual EEG is grouped by participant,
session, and repeat, then cyclically rotated across all four source classes with
no fixed points. Held-out rows remain untouched and held-out targets remain
sealed.

## Development measurement

One disposable local development measurement used a fake green-proof callback
and a temporary output that was removed on completion. It is not the official
qualification:

| Measure | Observed |
|---|---:|
| Runtime | 20.24995545798447 s |
| Peak process-tree RSS | 178,176,000 bytes |
| Generated input | 33,030,144 bytes |
| Maximum private generated prediction payload | 244,033 bytes |
| Aggregate output | 6,227 bytes |
| Residualizer fits | 6 |
| Classifier or prior fits | 54 |
| Total parameter updates | 60 |
| Model inference runs / prediction sets | 60 / 60 |
| Prediction rows | 1,440 |
| Synthetic target deliveries / scores | 1 / 1 |
| Post-target updates | 0 |
| Adversarial refusals | 35 |
| Positive generated route | COMM-G1-R1 |

The reported generated input includes both deterministic replay copies of all
eight fixtures. It is 524,288 bytes below the 32 MiB cap. The producer is
causal with one second of left context and zero right context. End-to-end
latency was not measured.

## Proof boundary

This implementation accessed no real or private path, EEG, EOG, EMG, event,
target, label, participant, payload, provider, stream, or device. It made zero
network calls, real fits, real inference runs, releases, and claim upgrades.

The generated COMM-G1-R1 route proves only that the software can recover an
effect deliberately injected into fictional arrays while rejecting registered
shortcuts. It does not establish communication decoding, EEG information beyond
peripheral controls, unseen-person generalization, independent replication,
live decoding, hardware performance, or a clinical result.

## Next gate

Commit and push this exact implementation and require Base Python and Optional
Neuro Readers to pass remotely. Only then may `qualify` run once with fresh
remote proof. Do not commit its private working predictions. The eventual
public result must remain aggregate, under 1 MiB, and scientifically explicit
that it is generated engineering only.

