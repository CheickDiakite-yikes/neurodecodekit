# Loop 34 Primary-Source Research And Confidence Decision Note

Date: 2026-07-12

Status: **Planning research complete; experiment Not Started; confidence
unavailable; no protected cache, signal, target, checkpoint, model, confidence
fit, validation scoring, or product-visible confidence is authorized**

Machine boundary: `registries/loop34_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 34

## Decision Summary

Loop 34 asks four questions that must not be collapsed into one:

1. Can a target-blind scalar rank sequence errors?
2. Can a separately fit mapping be interpreted as correctness probability?
3. Can a frozen threshold reduce accepted error at useful coverage?
4. Can a revision or delay rule improve output without hiding its latency cost?

The planning answer is:

1. Keep confidence **unavailable by default**.
2. Treat log score, entropy, margin, and prefix stability as candidate ranking
   features, not probabilities.
3. Preserve always-predict, train-only prior, fixed-random, and unreachable
   oracle controls.
4. Use a fresh target-free synthetic lane first, with disjoint calibration,
   selection, and final groups.
5. Fit probability mappings or conformal thresholds on calibration only.
6. Select exactly one score and policy on selection only.
7. Freeze every feature, mapping, threshold, policy, prediction, and hash before
   opening the final targets once.
8. Report exact-sequence 0/1 error as the primary bounded loss. Report raw CER
   separately; never silently clip it.
9. Report registered working points and generalized risk. Legacy AURC may be
   included with its limitations, but it cannot be the only selective metric.
10. Keep the existing six real validation rows out of Loop 34 confidence fitting
    and qualification.

These are research recommendations, not a preregistration. Exact seed, group
membership, risk target, failure probability, probability mapping, coverage
grid, threshold, and authorization sentence remain unfrozen.

## The Critical Evidence Finding

The current real source-validation set has six sentence instances. Those rows
are already reserved for one prospective shared Loop 26, Loop 31, and Loop 33
validation event. They cannot also provide three independent roles for Loop 34:

```text
fit a confidence mapping
  -> select a confidence source and abstention threshold
  -> qualify the frozen policy on untouched final evidence
```

Reusing the same six targets across those roles would tune and test confidence
on the same evidence. Splitting six rows into even smaller groups would not fix
the problem.

The sample-size limit is visible even under an unrealistically favorable
independent Bernoulli model. If all six accepted predictions were correct, the
one-sided 95% exact upper error bound would still be:

```text
1 - 0.05^(1/6) = 0.39303776899708276
```

The actual rows are from one person, one session, and a correlated sentence
process, so the independent model is already optimistic. Six zero-error rows
would therefore not certify a useful low-risk operating point.

**Decision:** a real confidence claim is unavailable from existing partitions.
It needs fresh, physically separate calibration, selection, and final evidence.
No acquisition is authorized or recommended by this planning note.

## Existing Local Evidence

| Surface | Current evidence | Loop 34 treatment |
|---|---|---|
| Source split | 55 train / 6 reserved validation / 5 consumed source-test rows | Six validation rows stay reserved for Loops 26, 31, and 33 |
| Session 2 MEG | Consumed model worse than no-signal prior | Frozen; never reopen for confidence tuning |
| S7 EEG | Consumed classifier worse than no-signal prior | Frozen; never reopen for confidence tuning |
| Loop 23 | A sequence can stabilize and remain wrong | Stability is a revision descriptor, not correctness |
| Loop 30 | Nine clock domains and confidence-unavailable interface | Preserve clock semantics and unavailable state |
| Loop 31 | Target-blind prediction and signal-attribution firewall | Confidence cannot bypass no-signal and corruption controls |

No consumed payload, protected path, cache, target, model, checkpoint, or
prediction was opened during this research pass.

## Primary-Source Findings

### 1. Selective prediction trades coverage for risk

Selective classification adds a selection function to a predictor. Predictions
below a threshold are rejected, so accepted error may fall while coverage also
falls. Geifman and El-Yaniv frame this as risk at coverage and develop
high-probability control for a chosen operating point.

Source:

- Selective Classification for Deep Neural Networks:
  https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html

This motivates an abstention gate, but it does not make any arbitrary score a
probability. It also makes the abstain-all failure obvious: risk can be reduced
trivially by refusing every prediction. Loop 34 therefore requires a registered
minimum coverage and an always-predict baseline.

### 2. Conformal risk control needs a bounded loss and named assumptions

Conformal Risk Control extends conformal methods to expected monotone losses
and provides finite-sample calibration bounds. Its calibration tightness scales
with the calibration sample size.

Source:

- Conformal Risk Control:
  https://research.google/pubs/conformal-risk-control/

Exact-sequence error is naturally bounded in `[0, 1]`. Raw CER is not: an
insertion-heavy prediction can have CER greater than one. A future conformal
lane must therefore use exact-sequence error or a separately named
`bounded_CER = min(raw_CER, 1)`. The report must still show raw CER and may not
quietly relabel clipped CER.

Standard conformal claims also rely on exchangeability. Barber and colleagues
show ways to handle distribution drift with weighted variants, but the
assumptions and weights must be explicit.

Source:

- Conformal Prediction Beyond Exchangeability:
  https://arxiv.org/abs/2202.13415

Synthetic sequences generated in the same block or schedule may be correlated.
Loop 34 therefore groups by generation block and schedule ID. Randomly shuffling
correlated rows and calling them independent is refused.

### 3. Calibration means probability semantics

Guo and colleagues define a calibrated classifier as one whose stated
probability agrees with empirical correctness frequency. They demonstrate that
modern neural networks may be miscalibrated and that a separately fit
temperature can improve calibration.

Source:

- On Calibration of Modern Neural Networks:
  https://proceedings.mlr.press/v70/guo17a.html

Loop 34 adopts the semantic boundary, not a commitment to temperature scaling.
A raw score of `0.9` is not “90% likely correct” unless a registered mapping is
fit on calibration data and independently assessed with proper scoring rules.

### 4. ECE is secondary and design-sensitive

Nixon and colleagues show that expected calibration error conclusions can
change with class conditioning, bin count, adaptive versus fixed bins, and norm.

Source:

- Measuring Calibration in Deep Learning:
  https://arxiv.org/abs/1904.01685

Loop 34 does not compute ECE for raw ranking scores. If a future lane produces
calibrated probabilities and has enough independent final data, it must freeze
bins and report reliability data, Brier score, and negative log likelihood.
ECE may then appear as a secondary diagnostic, never as the sole proof.

### 5. A single AURC can hide selective-classification behavior

Recent work distinguishes application-specific working-point risk from
multi-threshold method evaluation and identifies monotonicity and
interpretability limitations in legacy AURC. It proposes generalized risk,
which measures the joint probability of an accepted failure, and AUGRC for
multi-threshold evaluation.

Source:

- Overcoming Common Flaws in the Evaluation of Selective Classification
  Systems: https://arxiv.org/abs/2407.01032

Loop 34 therefore requires the full risk-coverage table and registered working
points. It also reports generalized error and an AUGRC-equivalent area. Legacy
AURC remains useful for comparison, but its number cannot stand alone.

## Confidence Semantics Ladder

| Level | Meaning | May be shown as probability? |
|---|---|---:|
| `L34-S0` unavailable | Evidence or semantics are insufficient | No |
| `L34-S1` raw ranking score | Orders predictions target-blind | No |
| `L34-S2` calibrated correctness probability | Separately fit and independently evaluated mapping | Yes |
| `L34-S3` selective policy | Frozen accept, abstain, or delay rule | Not necessarily |
| `L34-S4` conformal risk control | Bounded-loss statement under named finite-sample assumptions | No |
| `L34-S5` revision policy | Stability and delay behavior | No |
| `L34-S6` product-visible confidence | Qualified user-facing value or explicit unavailable state | Only with valid semantics |

Passing a lower level does not imply a higher one. In particular:

- a stable prefix can be wrong;
- low entropy can be confidently wrong;
- a large margin can be uncalibrated;
- a useful ranking can have poor probability calibration;
- calibrated probabilities do not automatically define a useful abstention
  operating point;
- a synthetic selective result is not a real neural-confidence result.

## Recommended Synthetic Partition

The first future lane should remain an interface and metric exercise:

```text
fresh calibration sequences: 128
fresh selection sequences:    64
fresh final sequences:       256
total:                       448
decoder model training runs:   0
```

The numbers are research recommendations and remain unfrozen. Every sequence
must come from a new target-free seed. Generation may not use real target text,
typed text, prompts, labels, predictions, or consumed examples. Membership is
grouped by independent generation block and schedule ID, with no overlap.

Roles are strict:

| Partition | Allowed use |
|---|---|
| Calibration | Fit a registered probability mapping or conformal threshold |
| Selection | Choose exactly one confidence source and one operating policy |
| Final | One-time qualification after every choice and hash is frozen |

Final targets cannot alter normalization, mapping, bins, threshold, coverage,
revision timing, or missing-value rules. A favorable final subgroup cannot
replace the registered full result.

## Candidate Scores And Controls

| ID | Candidate | Role |
|---|---|---|
| `L34-F00` | Length-normalized sequence or path log score | Model-score candidate |
| `L34-F01` | Valid-frame entropy summary | Distribution-shape candidate |
| `L34-F02` | Valid-frame top-1/top-2 margin summary | Separation candidate |
| `L34-F03` | Prefix stability and delay | Revision descriptor candidate |
| `L34-F04` | Train-only prior typicality | Signal-free confidence comparator |
| `L34-F05` | Fixed random score | Ranking-control floor |
| `L34-F06` | Always predict | Coverage-one policy baseline |
| `L34-F07` | Oracle error ranking | Post-hoc unreachable diagnostic ceiling |

The oracle uses correctness, so it is never eligible for selection, deployment,
or product display. It exists only to show the best possible ranking for the
observed final errors after scoring.

No new decoder is trained for Loop 34. A future confidence mapping may fit a
small scalar calibration transform after separate authorization, with at most
six mapping fits. Confidence research may not become a hidden model-search
loop.

## Metrics And Working Points

The recommended coverage grid is:

```text
1.0, 0.9, 0.8, 0.6
recommended primary coverage: 0.8
recommended minimum coverage: 0.5
```

These values remain unfrozen until preregistration. At every registered point,
the report must show:

- accepted item count and coverage;
- accepted exact-sequence error;
- accepted raw CER;
- generalized exact-sequence error, counting accepted failures over all items;
- abstention count and rate;
- ties, missing scores, and empty accept sets.

Across thresholds, report the full table, legacy AURC with a limitation note,
AUGRC or an equivalent generalized-risk area, and failure-ranking AUROC as a
diagnostic. No single area replaces the operating points.

Probability metrics are conditional on valid probability semantics:

- Brier score;
- negative log likelihood;
- full reliability table;
- ECE only with frozen bins and adequate independent final evidence.

An abstain-all or below-minimum-coverage policy cannot pass, regardless of its
accepted error.

## Revision And Latency

Loop 23 already demonstrated that stability is not correctness. Loop 34 may use
prefix stability to choose when to revise, delay, or finalize, but it must
report the cost:

- revision count;
- time to first output;
- time to stability;
- time to finalization;
- delay added by abstention or revision policy.

All timestamps must preserve the Loop 30 clock-domain contract. Replay time,
source time, model compute time, wall time, and user-visible latency cannot be
silently substituted for one another.

No end-to-end latency was measured in this planning pass. No real-time claim is
available.

## Future Access Order

```text
close required Loop 30 and Loop 31 dependencies,
  or bind an explicit synthetic-interface-only lane
  -> freeze fresh seed, groups, partition counts, and hashes
  -> freeze scores, mappings, losses, metrics, coverage, revision, resources,
     outcomes, and claims
  -> commit and push a hash-bound preregistration
  -> obtain a separate exact authorization sentence
  -> generate disjoint calibration, selection, and final inputs
  -> fit mappings and conformal thresholds on calibration only
  -> choose one score and policy on selection only
  -> freeze every code, config, feature, mapping, threshold, policy,
     prediction, access, and payload hash
  -> open final targets once
  -> score all frozen conditions in one pass
  -> support, park, invalidate, or publish unavailable without restart
```

The existing source-validation rows do not enter this sequence. A later real
lane needs a new partition packet and separate authorization.

## Outcome Taxonomy

| ID | Meaning | Consequence |
|---|---|---|
| `L34-O0` | Not run | Confidence remains unavailable |
| `L34-O1` | Invalid | Access, partition, target, hash, resource, or control failure |
| `L34-O2` | Insufficient independent evidence | Publish unavailable |
| `L34-O3` | No error ranking | Score does not beat frozen controls |
| `L34-O4` | Ranking only | Report raw ranking; no probability or selective claim |
| `L34-O5` | Bounded synthetic selective policy | Lower independent final error at registered useful coverage |
| `L34-O6` | Bounded synthetic conformal control | Named bounded risk passes under explicit assumptions |
| `L34-O7` | Real confidence unavailable | Synthetic interface result does not transfer to real data |

## Resource Boundary

A separately authorized synthetic pass must stay inside:

```text
CPU threads / workers:              1 / 1
decoder model training runs:            0
decoder parameter updates:              0
confidence mapping fits:        at most 6
total runtime:                  120 seconds
peak RSS:                            1 GiB
generated artifacts:               16 MiB
new data or model downloads:       0 bytes
direct energy measurement:     unavailable
```

The user's 5-10 GB storage envelope remains capacity, not permission. Loop 34
requires no new real-data or model download.

CPU time is not energy. Energy stays unavailable unless a separate direct
measurement protocol is preregistered.

## Measured Research Boundary

```text
high-level public-web research operations:          5
public GitHub API operations:                       0
protected dataset/model/weight download bytes:      0
raw signal/header reads:                            0
real-cache content reads:                           0
source-train signal/target reads:                   0 / 0
source-validation signal/target reads:              0 / 0
source-test/session-2 reads:                        0
S20/S25 operations:                                 0
checkpoint/model/training/parameter-update runs:    0 / 0 / 0 / 0
confidence/calibration fits:                        0
no-signal/control/prediction/scoring runs:           0 / 0 / 0 / 0
synthetic fixture generations:                      0
new real-data downloads:                            0
RW3/SDK/socket/stream/device/hardware operations:    0
CPU threads / workers:                              1 / 1
current generated planning-artifact cap:            8 MiB
```

Complete public-network response bytes, one end-to-end interactive research
runtime, interactive peak RSS, direct energy, and end-to-end latency are
unavailable from the research tool contracts. They remain unavailable rather
than estimated.

## Claim Taxonomy

| ID | Claim | Available now? |
|---|---|---:|
| `L34-C0` | No new result; planning boundary only | Yes |
| `L34-C1` | Target-blind raw score exists | No |
| `L34-C2` | Bounded synthetic error ranking | No |
| `L34-C3` | Bounded synthetic calibrated probability | No |
| `L34-C4` | Bounded synthetic abstention and revision result | No |
| `L34-C5` | Bounded synthetic selective risk control | No |
| `L34-C6` | Real, product, or population confidence | No |

Even a future `L34-C5` pass would apply only to the named synthetic generator,
seed, grouping, partitions, loss, score, mapping, coverage points, and
finite-sample assumptions. It would not establish a real neural advantage,
real confidence, decoding accuracy, unseen-person generalization, end-to-end
latency, portable hardware, at-home use, arbitrary-thought typing, assistive
efficacy, diagnosis, clinical utility, or product safety.

## Decision And Next Gate

Loop 34 planning research is complete. The experiment remains `Not Started`,
and confidence remains `unavailable`.

The immediate numbered execution gate remains Loop 25. Loop 34 should not
consume the six shared source-validation targets. After its dependencies are
closed, it may receive a separate synthetic-interface preregistration and exact
authorization. A real confidence lane waits for fresh physical evidence.

Engineering capability added: a machine-checkable confidence semantics ladder,
three-way partition firewall, target-leakage rules, selective-risk metrics,
revision-latency contract, resource ledger, outcome taxonomy, and explicit
unavailable state now exist.

Scientific claim not established: no protected data, model, confidence fit,
target, scoring, or product surface was accessed, so there is no calibrated
confidence, abstention benefit, selective-risk guarantee, neural advantage,
decoding accuracy, real-time behavior, or portable-hardware result.
