# Loop 23.5 Preregistration - Blank Intercept Calibration

Preregistered on 2026-07-10 before writing any Loop 23.5 implementation,
creating any fresh target array, fitting any calibration value, or creating the
registered seed-2353 test partition.

## Decision Question

Can one target-length-independent scalar correction to the frozen CTC blank
logit suppress synthetic tail insertions on fresh physical splits without
making any item worse, changing the encoder, changing prefix search, using an
endpoint, or using a language model?

This is a narrow calibration mechanism gate. It is not CTC retraining, a new
neural representation, natural-text decoding, real neural decoding, or a
real-time system.

## Prior Evidence And Protected Boundaries

Loop 23 is parked. Its registered validation passed, then its seed-2303 test
opened once and failed exact sequence accuracy at `5/8` against a `6/8` gate.
Every wrong row contained the complete correct target followed by one nonblank
tail symbol. Greedy and width-8 prefix outputs were identical. Seed 2303 is
consumed and forbidden for calibration fitting, threshold selection, endpoint
design, implementation tests, reruns, or fresh evaluation.

The Loop 22 seed-2203 test is also consumed. All observed S21 MEG holdouts,
S21 session 2, and the S7 EEG result remain frozen. Loop 23.5 may open none of
them.

The only learned source is the frozen Loop 22 checkpoint:

```text
path: cache/loop22_tiny_causal_encoder/checkpoint.npz
file SHA-256: 75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
parameter payload SHA-256: d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
config SHA-256: 8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2
parameters: 1,130
right context: 0 samples
```

No checkpoint value may change.

## Research Basis

The original CTC formulation defines a frame-level blank probability and sums
paths with different blank placements into sequence probabilities. Its prefix
search discussion also treats high blank probability as a meaningful boundary
signal. Loop 23.5 does not adopt the original threshold heuristic, because a
post-hoc endpoint threshold would answer a different question and could hide a
tail error.

Post-hoc calibration research shows that low-parameter logit transformations
can improve probability calibration without retraining a representation.
Logit-adjustment research gives statistical grounding for additive class
offsets when class frequencies and the training objective affect score
interpretation. Blank-regularized CTC work separately shows that blank occupancy
is an explicit modeling lever, although it changes training and is not the
method tested here.

The Loop 22 probe used inverse-frequency class-weighted frame cross entropy.
That was appropriate for balanced motif discrimination, but its raw logits were
never validated as deployment-frequency probabilities. This motivates a fresh
calibration test; it does not prove that miscalibration caused Loop 23.

Primary sources:

- Original CTC: https://www.cs.toronto.edu/~graves/icml_2006.pdf
- Post-hoc neural-network calibration:
  https://proceedings.mlr.press/v70/guo17a.html
- Post-hoc class-frequency logit adjustment:
  https://arxiv.org/abs/2007.07314
- Blank-regularized CTC:
  https://www.isca-archive.org/interspeech_2023/yang23l_interspeech.html
- Incremental correctness and stability:
  https://aclanthology.org/N09-1043/
- Brain2Qwerty v2 real-time limitation:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

Loop 23.5 is an independent, deliberately smaller intercept-only experiment.
It does not claim to reproduce those papers or transfer their ASR findings to
neural decoding.

## Fresh Registered Fixture

After this document is committed and pushed, implementation and tests must use
alternate seeds. The registered fixture cannot be generated until alternate
mechanics, a full-size rehearsal, the complete suite, and static checks pass and
are committed and pushed.

The registered fixture reuses the Loop 23 signal/target generation geometry but
has new identities and larger evaluation partitions:

| Field | Registered value |
|---|---:|
| Train / validation / test items | 64 / 16 / 16 |
| Train / validation / test seeds | 2351 / 2352 / 2353 |
| Protocol SHA-256 | `ac8b0dfa1ee512dd55645356546a068bc6b7e145f945a2e947d63dcf87185cc9` |
| Sampling rate | 100 Hz |
| Channels / symbols | 5 / `A-E` |
| Blank ID | 0 |
| Target length | 6-8 symbols |
| Motif / gap / lead / tail | 8 / 4 / 16 / 8 samples |
| Motif / adjacent amplitude | 1.5 / 0.25 |
| Noise standard deviation | 0.10 |
| Gain range / offset SD | 0.85-1.15 / 0.03 |
| Encoder kernel / stride | 16 / 4 samples |
| Maximum samples / frames per item | 116 / 26 |

Every target contains all five symbols and at least one adjacent repeated pair.
No natural-language text is stored. Item IDs are split- and seed-bound and must
be disjoint. The manifest binds every path, schema, hash, byte count, item ID,
shape, frame count, target count, repeated-pair count, seed, and protocol hash.

Alternate full-size rehearsal seeds are fixed at `9351/9352/9353`. Unit tests
use other nonregistered seeds. None may reuse 2203, 2301, 2302, or 2303.

## Calibration Fit

For frozen frame logits `z` with blank class `0`, define the uncalibrated
blank-vs-nonblank log odds:

```text
r = z[0] - logsumexp(z[1:6])
```

For a scalar intercept `b`, the calibrated blank probability is:

```text
q_blank(b) = sigmoid(r + b)
```

This is exactly equivalent to adding `b` to the blank logit and leaving all
five symbol logits unchanged before the existing float64 log-softmax and CTC
decoders.

Fit one and only one scalar:

```text
b* = argmin_b mean(binary_negative_log_likelihood(blank_label, q_blank(b)))
```

The fit contract is frozen:

```text
fit split:                 fresh train frames only
fit inputs:                train signals, valid frame geometry, frame blank/nonblank labels
forbidden fit inputs:      target token IDs, target lengths, validation, test
slope / temperature:       fixed at 1.0 / absent
intercept bracket:         [-8.0, 8.0]
solver:                    exactly 80 float64 bisection iterations
derivative:                mean(q_blank(b) - blank_label)
root requirement:          derivative(-8) <= 0 <= derivative(8)
regularization:            none
candidates / restarts:     1 / 0
calibration config hash:   43de56b1d275c0fd5b08a92d9dabc6893f7fe7ee49e02195623f6d61caa57e47
```

If the derivative is not bracketed, any value is nonfinite, the fitted value is
outside the bracket, or train blank negative log likelihood does not strictly
decrease, park before validation. Do not clip, widen the bracket, add a slope,
or switch objectives.

The calibration uses supervised synthetic frame labels during fitting. It is
target-length independent at inference, not label-free training.

## Fixed Decoder And Comparators

The primary decoder is the exact Loop 23 width-8 prefix beam after adding `b*`
to every frame's blank logit. Its blank/repeat update, float64 log-softmax,
beam width, maximum prefix length, tie ordering, lack of score threshold, and
flush behavior are unchanged.

Required comparators:

1. the unmodified Loop 23 width-8 prefix beam (`b = 0`);
2. calibrated and unmodified greedy CTC;
3. train-target-only most-frequent complete sequence prior;
4. zero-signal frozen pipeline using the calibrated decoder;
5. zero-signal frozen pipeline using the unmodified decoder.

There is no language model, lexicon, insertion bonus, endpoint detector,
target-length trim, expected-length model, silence detector, temperature,
per-symbol bias, or architecture candidate.

## Access Sequence

The gate must record these events in order:

1. validate only the compact manifest;
2. validate and load the exact frozen checkpoint;
3. open train signal/frame members once without target arrays;
4. run the frozen producer on train frames and fit `b*` once;
5. freeze and hash the scalar/config;
6. reopen only train target/item members once for the sequence prior;
7. open validation arrays once and run calibrated/unmodified decoders and both
   signal-free controls;
8. replay calibrated and unmodified validation traces under all five schedules;
9. apply the registered validation rule;
10. open seed-2353 test exactly once only if validation passes;
11. run one canonical frozen test evaluation without fit or replay;
12. write reports without reopening a partition.

Train has two explicit semantic opens with disjoint indexed member sets. The
calibration open must not index target IDs or lengths. The prior open must not
index signals or frame labels. Test has at most one semantic and physical open.

## Metrics

Frame-level blank calibration metrics, before and after:

- binary negative log likelihood;
- Brier score;
- 10-bin equal-width expected calibration error;
- empirical blank fraction and mean predicted blank probability;
- blank/nonblank confusion at probability 0.5, reported but not used to fit.

Sequence metrics for calibrated and unmodified greedy/prefix decoders:

- corpus CER, exact sequence accuracy, and repeated-pair reconstruction;
- per-item CER/exactness;
- corrected items: unmodified wrong, calibrated exact;
- new-error items: unmodified exact, calibrated wrong;
- per-item CER regressions;
- strict tail-insertion items and inserted tail-token count, where the complete
  target is an exact proper prefix of the prediction;
- train-only prior and zero-signal comparisons;
- 2,000-resample paired item bootstrap intervals with seed 2354 for calibrated
  minus unmodified exact accuracy and unmodified minus calibrated CER.

Incremental first/stable/final timing, revisions, edit overhead, frame time,
transport availability, and known-end flush remain as defined in Loop 23.
Stability is reported separately from correctness.

## Validation Rule

Validation opens test only when all conditions pass:

```text
calibrated prefix corpus CER <= 0.03
calibrated prefix exact accuracy >= 0.875 (14/16)
calibrated repeated-pair reconstruction >= 0.875
calibrated exact gain over unmodified >= 0.125 (at least 2/16)
corrected items >= 2
new-error items = 0
items with worse calibrated CER = 0
strict tail inserted-token reduction >= 2
blank NLL and Brier both strictly improve
CER reduction versus each calibrated signal-free control >= 0.40
exact gain over the stronger calibrated signal-free control >= 0.50
calibrated prefix CER <= calibrated greedy CER
calibrated and unmodified final outputs and frame traces are exact under 5/5 schedules
all fit, access, causality, state, runtime, RSS, working, and artifact gates pass
```

The threshold/config dictionary SHA-256 is
`7b2c7c061d1a286b1dc051677c19f4395601e5cbb3e80c5b8f3c991ee912ac58`.

Validation may only decide `open fresh test` or `park`. It may not change `b*`,
the solver, a decoder rule, target generation, or a threshold.

## Frozen Test Rule

The same point thresholds apply to the one canonical test pass. In addition:

```text
bootstrap lower bounds for exact gain and CER reduction >= 0
calibration/model/decoder fit after test open = false
test schedule replay = 0
test semantic open count = 1
```

`proceed` means only that one supervised synthetic blank-intercept mechanism
generalized to a fresh generated split. Any failed condition yields `park`.
The test is consumed regardless of result.

## Resource Caps

```text
numeric threads:                    1
fixture bytes:                      <= 1 MiB
fixture items:                      <= 96
samples per item:                   <= 128
total fixture frames:               <= 3,000
calibration parameters/state:       1 / 8 bytes
encoder mutable state:              <= 1 KiB
each decoder mutable state:         <= 4 KiB
working core arrays:                <= 16 MiB
internal gate runtime:              <= 20 sec
peak RSS:                           <= 768 MiB
JSON plus Markdown reports:         <= 1 MiB
all Loop 23.5 generated artifacts:  <= 2 MiB
total pushes:                       <= 100,000
raw/real data reads:                0
network fetches:                    0
encoder training/model updates:     0
calibration fits:                   exactly 1
```

If a cap fails, park rather than increase it.

## Required Tests

- analytic tiny examples and an independent dense-grid oracle for the fitted
  intercept and convex objective;
- deterministic replay and exact config/payload hashes;
- malformed/nonfinite logits and labels, unbracketed roots, cap refusal, and
  output collision;
- calibration access never indexes target members;
- prior access never indexes signal/frame members;
- validation failure physically leaves test unopened;
- mechanical pass opens test exactly once and never fits afterward;
- calibrated greedy/prefix hand examples preserve blank-separated repeats;
- strict registered protocol binding and rejection of Loop 23 seeds;
- no eager NumPy, Torch, or MNE import in the base module path;
- CLI parser/help for create, inspect, and gate commands.

## Claim Boundaries

Even a pass would not establish:

- CTC-trained representations or natural-language decoding;
- MEG, EEG, OPM-MEG, or other neural-signal performance;
- neural advantage over a language prior on real data;
- endpoint detection, online commitment, or end-to-end latency;
- unseen-session/person/population transfer;
- portable, at-home, arbitrary-thought, or clinical operation.

Loop 24 precision work remains blocked until this fresh correctness gate passes.
