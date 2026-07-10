# Risk, Ethics, and Scope

## Scope

NeuroDecodeKit is a research/developer tool for making non-invasive neural decoding datasets easier to inspect and benchmark. It is not a medical device, not a clinical diagnostic system, and not a consumer “mind reading” product.

## Important limitations

- Brain2Qwerty v1 data comes from healthy adult volunteers typing briefly memorized sentences.
- v1 uses keystroke-aligned windows, so the system is partly tied to motor execution and timing.
- MEG hardware is specialized and not consumer-ready.
- EEG is more accessible but substantially noisier for this task in the published v1 results.
- The validated S7 EEG bridge is minimally processed and uses a within-session
  key-event holdout. Its nearest-centroid accuracy is worse than a train-only
  prior. It must not be described as useful EEG decoding, consumer-device
  evidence, or session/subject generalization.
- The released v2 architecture is whole-sentence and non-causal; asynchronous
  decoding is not the same as low-latency streaming.
- The public studies record people physically typing memorized or prompted
  sentences. They do not demonstrate arbitrary thought decoding.
- Wearable OPM-MEG removes cryogenic sensor cooling, but current systems still
  require significant environmental field suppression and should not be called
  an at-home device.
- Lower-rate or lower-channel caches improve compute access but can remove
  neural bandwidth or spatial information. Resource reductions must not be
  described as retained decoding quality until a leakage-resistant evaluation
  measures that claim.
- A geometry proxy is not an anatomical ROI, and a 102-magnetometer cryogenic
  array is not an OPM or at-home device simulation.
- Variance-ranked sensors selected from one block leak test information if the
  same block is later used for evaluation. Fit data-dependent selection on the
  training partition only and preserve random/file-order controls.
- Low numeric reconstruction error from float16, BF16, or integer cache storage
  is not evidence of retained decoding accuracy. Packed representations must be
  evaluated on the same leakage-resistant held-out split as float32.
- Integer input storage is not integer-only model inference. The current packed
  caches decode to float32 and do not establish lower model RAM, energy,
  latency, or consumer-device readiness.
- Values on a quantizer rail must be reported separately from values clipped
  outside the declared range. Silent, data-fitted clipping can leak evaluation
  information and hide signal loss.
- Parking Zarr is a conditional local decision, not a universal rejection of
  chunked storage. Preserve the Loop 13 thresholds and rerun the access gate as
  cache scale or access patterns change; otherwise a future NPZ bottleneck can
  be hidden by an outdated decision.
- Deterministic sentence-text membership does not make preprocessing
  leakage-safe. Fit scaling, variance ranking, calibration, and learned
  transforms on train rows only, then freeze them for validation/test, or label
  an explicitly transductive protocol.
- Event and sentence-text splits inside one recording do not establish unseen
  session or unseen-person generalization. Canonicalize SpanishBCBL aliases that
  document repeated recordings of the same person.
- The first strict sentence-text test has only five rows. Its one-character
  neural-versus-prior difference and paired interval crossing zero are not a
  stable model ranking. Freeze those rows and do not iterate architecture or
  hyperparameters against them.
- A non-causal tiny CTC that emits mostly blanks is not a real-time decoder.
  Train-only preprocessing fixes leakage, not model quality, causal latency, or
  sensor accessibility.
- A same-subject second session is not an unseen-person result. The first fixed
  session-2 tiny CTC is materially worse than the signal-free prior; report it
  as failed transfer rather than evidence that the neural pipeline works.
- Once an independent-session score has been observed, that session is a
  consumed evaluation set. Do not tune adapters, hyperparameters, sensors,
  precision, or stopping rules against it and then report it as untouched.
- A calibration curve on synthetic token motifs is not a human calibration-time
  estimate. One sentence contains many time samples, and a static per-channel
  affine can improve diagonal drift while materially harming channel mixing or
  within-sentence drift. Report each shift family and seed; never present the
  best synthetic row count as a general session-adapter recommendation.
- A local evidence console is not a live neural decoder. Synthetic exact
  examples and aggregate real metrics must remain visibly labeled; do not infer
  calibrated confidence, causal streaming, arbitrary-thought reading, or
  at-home hardware readiness from the demo.
- A leaderboard row is not automatically comparable to every other row. Rank
  only inside an exact task, unit, dataset, split, subject scope, and proof
  posture that explicitly authorizes comparison. Keep event-level,
  sentence-level, synthetic, real, fit-on-eval, and consumed-holdout cohorts
  separate; do not invent a global score when CER, WER, and SemER can disagree.
- Empty behavioral trial slots are not missing labels to impute. Preserve the
  session-2 gaps at MAT trials 54, 58, and 60, map only performed `keyTrig`
  slots, and fail closed when raw/performed counts do not reconcile.

## Privacy posture

Treat brain data as highly sensitive even when de-identified.

Rules:

- Do not attempt subject identification.
- Do not upload derived neural features by default.
- Do not include raw data in Git.
- Do not publish subject-level examples without checking dataset terms.
- Prefer aggregate reports unless a subject-level analysis is necessary.
- Treat sentence-group hashes as pseudonymous metadata, not anonymization. A
  known or guessable sentence can be re-hashed and matched to a report.
- Unlike plaintext-free split reports, prediction/error reports can contain
  typed sentences. Keep those reports local unless dataset terms and example
  disclosure have been reviewed.

## Licensing posture

The public Brain2Qwerty code and SpanishBCBL dataset are released under CC BY-NC 4.0 according to their public pages. Treat all work using those artifacts as noncommercial research unless separate rights are obtained.

The Loop 19 EEG bundle inherits the same noncommercial posture. Its local cache
contains derived physiological windows and event labels; keep it local unless
the dataset terms, participant-data handling, and derived-data sharing posture
have been reviewed explicitly.

## Communication posture

Use careful language:

Good:

```text
"decodes typed sentence production signals from MEG/EEG under a controlled task"
```

Avoid:

```text
"reads arbitrary thoughts"
"consumer mind-reading"
"clinical-ready communication restoration"
"works at home with thoughts alone"
```
