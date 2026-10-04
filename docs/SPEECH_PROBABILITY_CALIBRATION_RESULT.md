# Confidence scaling improved prediction quality, not imagined-word decoding

September 22, 2026. **Exploratory development result; not fresh confirmation.**

One training-only nested temperature fit per readout substantially improved
minimally overt probability prediction without changing a single chosen word.
The joint model's mean blocked class-macro log loss fell **1.252182 → 0.369239**;
equally calibrated auxiliary-only A fell **1.256028 → 0.489214**. Both improved
in all three people under both split schemes. This supports a confidence-scale
limitation in these original readouts, not an absence of useful prediction.

However, the calibrated EEG increment passed all six controls in **2/3
minimally overt people**, not all three, under both schemes. Covert passed in
**1/3 with blocked folds and 0/3 with random folds**. The registered all-person
criterion still failed in both conditions. No earlier result is overturned.

## All readouts and controls

Each cell is **original → calibrated class-macro log loss**, averaged equally
over the three people; lower is better. Uniform and training-prior outputs are
unchanged. All 20 arms, six pairs, fold calibrations and both schemes are in the
[complete aggregate](../registries/speech_probability_calibration_result.v0.json).

| Readout | Blocked minimally overt | Blocked covert | Random minimally overt | Random covert |
|---|---:|---:|---:|---:|
| Original auxiliary N | 1.258781 → 0.536180 | 1.580720 → 1.552686 | 1.244240 → 0.464411 | 1.581361 → 1.542191 |
| Enriched auxiliary A | 1.256028 → 0.489214 | 1.565551 → 1.543782 | 1.239526 → 0.405516 | 1.566080 → 1.501823 |
| EEG full/all alone | 1.492797 → 1.340037 | 1.623789 → 1.608016 | 1.491334 → 1.292769 | 1.628606 → 1.614239 |
| **A + EEG: primary** | **1.252182 → 0.369239** | **1.578166 → 1.571150** | **1.238520 → 0.319636** | **1.581350 → 1.520301** |
| A + deranged EEG | 1.286804 → 0.562666 | 1.572943 → 1.532343 | 1.280744 → 0.532452 | 1.570278 → 1.498108 |
| Joint shuffled labels | 1.644393 → 1.617431 | 1.628416 → 1.613236 | 1.610495 → 1.610933 | 1.634866 → 1.624547 |
| A shuffled labels | 1.647236 → 1.623196 | 1.633954 → 1.613469 | 1.615564 → 1.614428 | 1.634379 → 1.613255 |
| N shuffled labels | 1.651751 → 1.622043 | 1.642617 → 1.616666 | 1.617265 → 1.608906 | 1.651410 → 1.614673 |
| EEG shuffled labels | 1.621060 → 1.606205 | 1.616493 → 1.609278 | 1.612927 → 1.614364 | 1.621657 → 1.618387 |
| Uniform | 1.609438 | 1.609438 | 1.609438 | 1.609438 |
| Training prior | 1.673691 | 1.708487 | 1.657124 | 1.694319 |

**Balanced accuracy did not improve through calibration.** A versus joint BA
remains 85.62% versus 89.75% for blocked minimally overt, and 32.19% versus
27.67% for blocked covert. Random-fold values remain 88.75% versus 91.03%,
and 29.87% versus 27.87%. Positive temperature preserves every argmax.

## Conditional EEG result and heterogeneity

Positive gains below mean lower log loss for calibrated A+EEG. The full
conjunction also requires beating the calibrated joint-label shuffle, uniform
and training prior. It is a descriptive consistency rule, not significance.

| Blocked condition / person | Gain over calibrated A | Gain over calibrated N | Gain over deranged EEG | All six controls, blocked | All six controls, random |
|---|---:|---:|---:|---|---|
| Minimally overt / 1 | -0.046371 | +0.066417 | +0.045965 | No | No |
| Minimally overt / 2 | +0.147342 | +0.049828 | +0.159782 | Yes | Yes |
| Minimally overt / 3 | +0.258953 | +0.384578 | +0.374533 | Yes | Yes |
| Covert / 1 | -0.091363 | -0.051047 | -0.118277 | No | No |
| Covert / 2 | -0.000072 | -0.005486 | -0.005132 | No | No |
| Covert / 3 | +0.009330 | +0.001139 | +0.006988 | Yes | No |

Mean gain over calibrated A is **+0.119975 minimally overt / -0.027368 covert**
with blocked folds, and **+0.085880 / -0.018478** with random folds. Person 1
still favors the auxiliary-only probability prediction in minimally overt
speech. Better group means cannot erase that failure. Covert joint prediction
is worse on average than both calibrated A and the deranged-EEG control.

For covert speech, A's calibration gain is positive in only two people under
blocked validation; the predeclared all-person readout diagnosis fails there
too. Flattening weak predictions toward uniform can improve log loss without
recovering additional word information. This is particularly relevant to the
covert EEG-only and shuffled arms; preserve those null results.

## Why this changes our belief, and what happens next

The original ridge-plus-softmax probabilities were a material limitation for
minimally overt prediction: inner-training fits selected inverse temperatures
above one for every A and joint fold, and outer-fold probability scores improved
in all three people. This is evidence for that narrow explanation, not proof
of perfect calibration. The EEG increment is heterogeneous even after the
same opportunity is given to the peripheral comparator.

**Close this calibration branch.** Do not widen temperature bounds, change the
endpoint, select a new band or add another model based on these outcomes.
Carry training-only probability calibration forward as a fixed candidate
method, with equal treatment of controls and fresh validation still required.

The next thought-to-text milestone is a fresh imagined-word study beyond
peripheral, cue and timing alternatives. The [source decision](SPEECH_NEXT_COHORT_DECISION.md)
identifies the existing ten-person Thinking Out Loud candidate as a practical
new-cohort, same-day study, not new-day confirmation. Exact new-source access
remains separately authorized; no dataset acquisition occurred in this run.

These results do not establish cortical origin, cue-independent thoughts,
silent communication, arbitrary text, unseen-person generalization, prospective
live use or clinical utility. The three-person development cohort has been
repeatedly explored, so these estimates are not untouched confirmation. The
earlier online evaluation remains closed. Whole-trial preprocessing and
retrospective folds are not causal streaming, and single label shuffles/EEG
shifts are diagnostics rather than calibrated null distributions.

## Execution and integrity

One invocation at `80a80d5f0c6974011922613db72062d20fb98857` after 133 local
speech checks, Ruff and independent static review. Both remote jobs passed:
workflow `35767739344`, Base `106881437743`, Optional Neuro `106881437203`.

All six nested-split preflights passed before fitting. All 600 original trials,
2,700 small ridge fits and 540 scalar fits completed in **45.328 seconds**,
with peak observed RSS **217,493,504 bytes**. Local artifacts occupy 1,843,703
bytes; the aggregate occupies 765,328 bytes. No failures, retries, new downloads,
online reads, deep models or private payload uploads occurred.

Across 540 fits, 203 reached the lower inverse-temperature bound and two the
upper bound. Both upper hits were random-fold minimally overt person 1
(one A and one joint fit). Bounds were not expanded. The convex calibration
objective uses unclipped log-softmax while historical scoring keeps a 1e-15
floor; **zero** scored true-class probabilities fell below that floor.

All 132 shared uncalibrated metric objects exactly match the prior result;
every original top-choice prediction is preserved by positive temperature.
Independent review reconciled all 240 endpoints, 180 reported gains, 108
calibrated/raw accuracy pairs and 60 unchanged outer-fold identities.
All five preceding scientific aggregate hashes remain unchanged. Per-trial
predictions stay local; only aggregate evidence and documentation are committed.
Result SHA256: `f19fde04edc9d4d63b5f478f90426d41831294a5aea7aee5bdec5bdb9214782a`.
