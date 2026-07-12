# Loop 33 Primary-Source Research And Scaling Decision Note

Date: 2026-07-12

Status: **Planning research complete; experiment Not Started; no protected
cache, signal, target, checkpoint, model, training, validation scoring, or
additional acquisition is authorized**

Machine boundary: `registries/loop33_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 33

## Decision Summary

Loop 33 asks a narrower question than a universal scaling-law study:

> Within the existing 55 source-train sentence instances, does more unique
> training data improve one fixed 2,908-parameter causal encoder, and is the
> observed upper boundary still improving enough to justify a separate future
> acquisition decision?

The planning answer is:

1. Recommend six strictly nested unique-sentence prefixes:
   `8, 16, 24, 32, 44, 55`.
2. Keep one person, session, MEG device, 102-channel contract, 100 Hz input,
   2,908-parameter architecture, optimizer, update budget, decoding rule,
   validation membership, and metric implementation fixed.
3. Allow at most three optimization seeds and 18 candidate fits. Seeds measure
   training instability; they are not additional people or biological
   replicates.
4. Fit a train-size-matched no-signal prior at every prefix.
5. Freeze every Loop 26, Loop 31, and Loop 33 prediction before opening the six
   shared validation targets once.
6. Report unique sentences, physical trials, valid signal seconds, bytes, and
   runtime. Use minutes until at least 3,600 valid signal seconds exist.
7. Treat a physical repetition comparison as unavailable. Duplicating,
   reweighting, or augmenting one recording does not create another neural
   acquisition.
8. Do not fit or extrapolate a universal power law from six tiny prefixes and
   six validation sentences.
9. Do not recommend another download now. A preregistered upper-bound result
   could justify a later metadata-only acquisition packet, not permission to
   acquire data.

These are research recommendations. The prefix order, exact seeds, practical
margins, optimizer, stopping rule, and authorization sentence remain unfrozen.

## The Critical Access-Order Finding

Loop 26 and Loop 33 share the same six reserved source-validation sentences.
That is efficient, but only if their questions are frozen together before the
first validation target is opened.

The prospective path is:

```text
freeze Loop 26 architecture and training contract
  -> freeze Loop 33 prefixes, seeds, metrics, controls, and outcome rules
  -> commit and push both hash-bound preregistrations
  -> obtain separate exact execution authorization
  -> train every size and seed without validation targets
  -> generate every Loop 26, Loop 31, and Loop 33 validation prediction
  -> hash-freeze models, configs, prefixes, predictions, and ledgers
  -> open all six validation targets once
  -> score every condition in one pass
  -> mark source validation consumed for predictive selection
  -> support or park without a restart
```

If Loop 26 opens the targets before Loop 33 is frozen, a later Loop 33 curve on
those rows is no longer a clean prospective test. It may be reported as an
exploratory observed validation curve, but it cannot authorize acquisition or
support the registered scaling claim. A new prospective claim would require a
fresh, physically separate validation partition and separate approval.

This ordering is the main high-value result of the planning pass. It prevents
the project from spending its final unused local validation evidence twice.

## Existing Local Evidence

| Surface | Current evidence | Loop 33 treatment |
|---|---|---|
| Source split | 55 train / 6 reserved validation / 5 consumed source-test sentence rows | Use only train and one future shared validation open after exact authorization |
| Session 2 | Consumed harmful cross-session result | Frozen; never reopen or tune on it |
| Existing predictive claim | Prior MEG and EEG classifiers were worse than no-signal comparators | Do not assume a neural advantage or that more data will fix the branch |
| Loop 26 | Planning recommends one 2,908-parameter causal Conv-CTC model | Bind the curve to that exact family; do not scale architecture and data together |
| Loop 31 | Planning defines the signal-attribution firewall | A positive curve is only predictive until Loop 31 supports sensor-signal wording |
| Loop 29 | 5-10 GB user storage capacity, no current acquisition recommendation | Spend zero additional bytes now |

No consumed S7 or S21 payload and no protected path, cache, target, or payload
hash was opened during this research pass.

## Primary-Source Findings

### 1. Brain2Qwerty v2 shows two distinct data effects

The public Brain2Qwerty v2 paper reports five training-fraction conditions on
EnglishBCBL, with a fixed test set. Across roughly 10 to 90 pooled recording
hours, asynchronous encoder CER follows a strong log-linear association:
`r = -0.99`, `R2 = 0.98`, and a reported slope of `-0.39 CER per log10 hour`.
The curve showed no saturation at that study's approximately 90-hour ceiling.

The same paper separately matched total sentence count and compared 128 unique
sentences repeated twice with 256 unique sentences typed once. The unique
condition had lower CER (`0.45` versus `0.65`). That result is directly useful
for experimental design: recording quantity and sentence variety are different
axes.

Source:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

It is not valid to transplant that slope into NeuroDecodeKit. The public result
uses nine people, much more data, English sentences, a substantially larger
asynchronous system, and a different training regime. Our proposed curve has
one person, six validation sentences, a 2,908-parameter model, and at most 55
training sentence instances.

### 2. More within-person recording can matter, but task and modality matter

Banville and colleagues aggregate eight public brain-imaging datasets, 84
volunteers, 498 hours, and 2.3 million image responses. Their results report
log-linear improvements and find that additional within-subject data often
matters more than simply adding subjects.

Source:

- Scaling laws for decoding images from brain activity:
  https://arxiv.org/abs/2501.15322

That evidence motivates measuring within-person data amount explicitly. It
does not supply a transferable exponent for typed-sentence MEG, and it cannot
turn a one-person curve into population evidence.

### 3. A long EEG curve can hide task, supervision, and compute differences

Sato and colleagues study 175 hours from one participant during overt speech.
Their pipeline uses speech audio correspondence, EMG/EOG artifact channels,
and large GPU training. They also note that lexical overlap grows with data
duration, which can make additional hours change both neural sample count and
language coverage.

Source:

- Scaling Law in Neural Data: Non-Invasive Speech Decoding with 175 Hours of
  EEG Data: https://arxiv.org/abs/2407.07595

This source reinforces two Loop 33 rules: report unique language content as
well as time, and never treat a different task, modality, supervision path, or
compute regime as a local result.

### 4. Extrapolation is a model, not a free conclusion

Learning-curve methods can fit explicit functions to observed points and use
them to estimate performance at larger sample sizes. That is a separate
modeling procedure with assumptions and uncertainty; it is not what Loop 33's
tiny descriptive curve is designed to do.

Source:

- Predicting sample size required for classification performance:
  https://pubmed.ncbi.nlm.nih.gov/22336388/

Small validation samples can also let test uncertainty obscure a learning
curve. Six sentence instances are enough for exact paired bookkeeping but are
not a population-level scaling dataset.

Source:

- Sample size planning for classification models:
  https://pubmed.ncbi.nlm.nih.gov/28655633/

Loop 33 therefore refuses a fitted power-law exponent, asymptote, or forecast
beyond 55 sentences. It reports only what happens inside the observed range.

## Recommended Local Curve

```text
unique source-train sentence instances: 8, 16, 24, 32, 44, 55
maximum optimization seeds:             3
maximum candidate fits:                18
validation sentence instances:          6, fixed for every condition
candidate parameters:               2,908, fixed for every condition
candidate model: TinyCausalSentenceCTC, proposed by Loop 26
```

The future preregistration should sort source-train members by:

```text
sha256(future_contract_hash | semantic_id | performed_row_id)
```

and then take strict prefixes. The final prefix must equal all 55 source-train
rows exactly. Character, text, and length coverage must be reported, but target
or validation results cannot change the order.

The exact contract hash and optimization seeds remain `null` until
preregistration. Reusing Loop 25 or other frozen seeds would couple unrelated
questions, so Loop 33 needs fresh seeds chosen before protected access.

## Unique Sentences Are Not Repeated Acquisitions

The committed local metadata does not establish eligible physical repetitions
inside the 55 source-train rows. The first bounded experiment can therefore
answer only the unique-sentence prefix question.

These operations do **not** create a physical repetition:

- duplicating an array row;
- sampling the same row twice;
- increasing its loss weight;
- adding noise or another augmentation;
- slicing the same trial into two examples.

A future physical repetition lane requires two or more distinct performed-row
IDs and recordings of the same normalized prompt. The repeated and unique
conditions must match total physical trial count, person, session policy,
device, channels, model, optimizer, and validation set. That lane needs its own
metadata review, preregistration, acquisition or data-access approval, and
claim boundary.

The absence of this lane does not invalidate the unique-sentence curve. It does
invalidate any statement about the relative value of another physical repeat.

## Conditions And Controls

| ID | Condition | Role |
|---|---|---|
| `L33-S00` | Fixed signal candidate at all six prefixes and up to three seeds | Primary bounded curve |
| `L33-S01` | Train-size-matched, train-only no-signal prior at every prefix | Primary signal-free comparator |
| `L33-S02` | Loop 31 full-size attribution binding | Required before sensor-signal wording |
| `L33-S03` | Future matched physical repetition lane | Unavailable now; separately authorized if suitable data exist |

The no-signal prior must be fit using only the target texts belonging to each
training prefix. A full-55-row prior compared with an eight-row candidate would
not be size matched.

Loop 31 need not multiply its full corruption matrix across all six sizes.
Loop 33 asks whether one fixed predictive path changes with data amount. The
full-size attribution result remains the gate for calling that path dependent
on sensor signal rather than language, timing, context, or pipeline artifacts.

## Recommended Decision Rules

At each size, compute macro sentence CER for each seed and the matched prior.
The primary curve is the median seed macro CER plotted against
`log2(unique_train_sentences)`. Report the ordinary least-squares CER slope for
each seed as a descriptive stability diagnostic.

The research recommendations are:

```text
smallest band: 8 and 16 sentences
upper band:   44 and 55 sentences
minimum practical smallest-to-upper macro-CER gain: 0.05
minimum practical upper-band gain over matched prior: 0.05
stable bounded trend: every registered seed slope is negative
every adjacent size must improve: false
```

The two `0.05` margins and exact seed rule are not frozen until
preregistration. Every adjacent delta, item error, seed result, tie, reversal,
and failed fit must remain visible. Favorable endpoints cannot hide an unstable
middle or a failed seed.

There is no formal slope p-value in this design. The three seeds share the same
data, and the six validation sentences come from one person and one session.
A descriptive interval may show sensitivity; it cannot manufacture biological
replication or population inference.

## Outcome Taxonomy

| ID | Meaning | Consequence |
|---|---|---|
| `L33-O0` | Not run | Planning only |
| `L33-O1` | Invalid | Fix the protocol without using the exposed targets, or park |
| `L33-O2` | Full-size branch below the matched prior | Park predictive scaling |
| `L33-O3` | No stable bounded trend | Report noise, flatness, or seed dependence; no acquisition case |
| `L33-O4` | Bounded positive unique-sentence trend | Report only inside 8-55 sentences |
| `L33-O5` | Local plateau within observed range | Do not claim saturation beyond 55 |
| `L33-O6` | Upper boundary still improving | May justify a separate metadata-only acquisition packet |

`L33-O6` is not a download authorization. The later packet would have to name
the exact candidate files, bytes, license, consent, retention, expected new
unique sentences or physical repeats, split role, stop rule, and authorization
sentence.

## Resource Boundary

A future separately authorized curve must fit inside the existing Loop 26
envelope:

```text
CPU threads / workers:                      1 / 1
candidate parameters:                      2,908
candidate training runs:                   at most 18
no-signal prior fits:                      at most 6
total parameter-update runtime:            1,200 seconds
peak RSS:                                  1 GiB
generated artifacts:                      32 MiB
new data or model downloads:               0 bytes
direct energy measurement:                 unavailable
```

If 18 candidate fits cannot complete inside 1,200 seconds, the future
preregistration must reduce seeds or prefixes before protected access. It must
not silently increase compute after timing a favorable result.

CPU time is not energy. Unless a direct, platform-appropriate measurement tool
is preregistered and available, the report must mark energy unavailable rather
than presenting an "energy proxy" as consumption.

The user's 5-10 GB incremental storage envelope remains capacity, not data
access, acquisition, model, training, target, or execution authorization.

## Measured Research Boundary

```text
high-level public-web research operations:          6
public GitHub API operations:                       0
protected dataset/model/weight download bytes:      0
raw signal/header reads:                            0
real-cache content reads:                           0
source-train signal/target reads:                   0 / 0
source-validation signal/target reads:              0 / 0
source-test/session-2 reads:                        0
S20/S25 operations:                                 0
checkpoint/model/training/parameter-update runs:    0 / 0 / 0 / 0
no-signal/control/prediction/scoring runs:           0 / 0 / 0 / 0
new real-data downloads:                            0
RW3/SDK/socket/stream/device/hardware operations:    0
CPU threads / workers:                              1 / 1
current generated planning-artifact cap:            8 MiB
```

Complete public-network response bytes, one end-to-end interactive research
runtime, interactive peak RSS, and direct energy are unavailable from the
research tool contracts. They remain unavailable rather than estimated.

## Claim Taxonomy

| ID | Claim | Available now? |
|---|---|---:|
| `L33-C0` | No new result; planning boundary only | Yes |
| `L33-C1` | Resource curve by local prefix | No |
| `L33-C2` | Bounded predictive curve on six named validation sentences | No |
| `L33-C3` | Bounded gain over size-matched no-signal priors | No |
| `L33-C4` | Bounded one-person sensor-signal-dependent unique-sentence curve | No |
| `L33-C5` | Physical repetition efficiency | No |
| `L33-C6` | Universal scaling, population, or guaranteed acquisition value | No |

Even a future `L33-C4` result would be limited to one person, one session, one
MEG device and channel set, one 2,908-parameter model, six validation sentence
instances, and the observed 8-55 unique-sentence range. It would not establish
a Brain2Qwerty v2 exponent, unseen-person generalization, real-time text,
portable hardware, at-home use, arbitrary-thought typing, assistive efficacy,
diagnosis, or clinical utility.

## Decision And Next Gate

Loop 33 planning research is complete. The experiment remains `Not Started`.
No acquisition is recommended now.

The immediate numbered execution gate remains Loop 25. If Loop 25 closes with
a compatible causal preprocessing result, Loop 26 and Loop 33 should be
preregistered together before the shared source-validation targets are opened.
That preserves one honest validation event for the encoder, attribution, and
bounded learning-curve questions.

Engineering capability added: a machine-checkable six-prefix local scaling
design, target-blind shared-validation sequence, unique-versus-repetition
firewall, no-signal controls, resource ledger, outcome taxonomy, and
acquisition decision boundary now exist.

Scientific claim not established: no protected data, model, training, target,
or acquisition was accessed, so there is no learning curve, neural advantage,
scaling law, repetition-efficiency result, saturation finding, acquisition
value, unseen-person generalization, real-time behavior, or portable-hardware
result.
