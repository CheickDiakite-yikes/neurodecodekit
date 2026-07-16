# Loop 48 Stage B Train-Only Failure-Discrimination Result

Status: **Complete after one registered execution; consumed with no rerun**

Date: 2026-07-15

## Executive Verdict

Loop 48 Stage B completed its exact 44-fit/11-check train-only diagnostic under
the frozen contract. The registered result supports `H4`, **stable but
nonseparable representation**, for this transformed S21 source-train slice and
this fixed tiny model family. It also records evidence against `H3`, the
registered fixed timing-offset explanation. `H1`, `H2`, `H5`, and `H6` remain
mixed or unresolved.

The primary size-44 causal candidate reached macro sentence CER `0.953566` on
the 11 train-check rows. Its matched train-only no-signal prior reached
`0.822045`, so the candidate was worse by `0.131522` macro CER. All three
size-44 causal fits and all three size-44 linear fits were finite and stable,
but none cleared its registered prior rule.

This is an E2 post-outcome pipeline-discriminative diagnostic. It is not fresh
validation: all 55 source-train rows were used historically before this
prospective-within-execution 44/11 split was created.

## Frozen Identity

| Boundary | Exact evidence |
|---|---|
| Contract | `registries/loop48_train_only_discrimination_contract.v0.json`, SHA-256 `009e320ea4df17e9f6fa58f74053b2ab70cce73eb0a9eea3cefc5b7b14112a9a` |
| Authorization | `registries/loop48_stage_b_authorization_decision.v0.json`, SHA-256 `3baf5630e1b42905838f70b9cb1a3d1ce966501ecf90252cbf25702f10b9243a` |
| Implementation | commit `1d840e3eb10a68f25381bde16595f7d62fd515bb` |
| Implementation push CI | `29461579009`, green before protected access |
| Implementation PR CI | `29461580293`, green before protected access |
| Prediction freeze | `registries/loop48_stage_b_prediction_freeze.v0.json`, SHA-256 `2c14d25d92dbd93677515136365f9b229fbbdfaf7086fe77a36469f43085e65f` |
| Freeze commit | `00215b1f43183ff0c832bf7ba63bbd699d4a4c7b` |
| Freeze push CI | `29461934145`, green before check-target delivery |
| Freeze PR CI | `29461935560`, green before check-target delivery |
| Consumed result | `registries/loop48_train_only_discrimination_result.v0.json`, SHA-256 `ef8290eb45e755bedb2deed781e6e472aa3621c25d91a01d01626c17c96ce891` |

The prediction-freeze record contains hashes and fit telemetry, not plaintext
check predictions, targets, or scores. The same 11 check targets opened once
only after the freeze commit had passed both remote workflows.

## Access Order

| Stage | Permitted operation | Measured result |
|---|---|---|
| Static gate | Target-free split metadata, archive headers, channel names, cache metadata, source stat | Passed; zero cache hash passes and zero signal/target rows delivered |
| Isolated derivatives | One source-cache SHA-256 pass; 44 fit signals/targets; 11 check signals | Passed; check targets absent; validation and source-test derivatives zero |
| Target-blind execution | 20 fits, 35 model inferences, five priors, 41 private prediction sets | Passed and frozen; check targets and scores zero |
| Freeze qualification | Commit, push, push CI, and PR CI over hash-only freeze | Both workflows green |
| Consumed score | Deliver and score the same 11 train-check targets once | Completed once; reruns zero |

The source cache was exactly `10,632,576` bytes and matched SHA-256
`45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815` in
its single registered hash pass.

The isolated fit bundle was `7,084,125` bytes and contained exactly 44 fit
rows with targets. The isolated check-input bundle was `1,750,971` bytes and
contained exactly 11 signals with no targets. No validation, source-test,
session-2, S7, S20, S24, or S25 derivative was created.

## Primary Result

| Metric | Primary causal candidate | Matched no-signal prior |
|---|---:|---:|
| Condition | `candidate_size44_seed4801` | `prior_size44` |
| Macro sentence CER | `0.953566` | `0.822045` |
| Corpus CER | `0.955801` | `0.803867` |
| Corpus WER | `0.963636` | `0.927273` |
| Exact sentences | `0/11` | `0/11` |
| Blank fraction | `0.996316` | unavailable/not applicable |

The primary candidate-minus-prior macro-CER improvement was `-0.131522`.
The candidate won on 2 rows and lost on 9, with one-sided greater p-value
`0.980957` over all `2,048` exact sign assignments. This is evidence against
the candidate beating the prior, not a near miss.

The other full-size causal seeds also lost to the matched prior by `0.081519`
and `0.168241` macro CER. The three linear probes lost by `0.138104`,
`0.091335`, and `0.141008`. All six fits were finite and stable.

## Registered Controls

The primary candidate beat exact-zero and timing-only predictions on all
`11/11` check rows by mean macro CER `0.046434`, one-sided p-value
`0.000488`. It also beat the severe `+100`-sample displacement by mean
`0.022738`, one-sided p-value `0.015625`, with six wins and five ties.

Those isolated components do not satisfy the registered intact-signal
conjunction. The primary candidate did not clear the no-signal prior, channel
derangement, check-row derangement, fit-target derangement, or every other
corruption rule. The complete conjunction therefore failed, and no
sensor-signal-dependence claim is available.

| Comparator | Mean candidate improvement | One-sided p | Registered conclusion |
|---|---:|---:|---|
| No-signal prior | `-0.131522` | `0.980957` | Failed |
| Exact zero signal | `0.046434` | `0.000488` | Isolated component only |
| Timing-only fit | `0.046434` | `0.000488` | Isolated component only |
| Channel derangement | `0.010371` | `0.214844` | Failed |
| Check-row derangement | `-0.002091` | `0.562500` | Failed |
| Fit-target derangement | `0.003122` | `0.375000` | Failed |
| Severe +100-sample displacement | `0.022738` | `0.015625` | Isolated component only |

## Hypothesis Verdicts

| ID | Frozen explanation | Verdict | Why |
|---|---|---|---|
| `H1` | Fixed tiny CTC feasibility or optimization failure | Mixed or unresolved | All fit/check rows were CTC-feasible and telemetry was finite, but the exact size-8 blank-collapse support rule did not pass and the against rule was not met |
| `H2` | Sensor or trial quality insufficiency | Unresolved; evidence against unavailable | The transformed cache had no gross nonfinite, padding, flat-channel, or CTC-feasibility defect, but it cannot assess raw sensor quality, head motion, line noise, or peripheral physiology |
| `H3` | Timing or preprocessing information mismatch | Evidence against | None of `-50`, `-25`, `+25`, or `+50` samples improved all three seeds in one direction under the corrected rule; no shift was selected |
| `H4` | Stable but nonseparable representation | Supported | All three causal and all three linear size-44 fits were finite/stable, and none cleared its prior margin and p-value |
| `H5` | Prior-dominated task regime | Mixed or unresolved | The prior beat the primary intact candidate, but the full intact-versus-corruption conjunction also failed, so the exact support rule was not satisfied |
| `H6` | Data quantity or sentence diversity insufficiency | Mixed or unresolved | Median CER was nonmonotonic across `8,16,24,32,44`, seed slopes disagreed, and the registered nonsaturation rule did not pass |

The nested median macro CER values were `0.970658`, `1.073121`, `0.934910`,
`0.877250`, and `0.953566` for prefix sizes `8`, `16`, `24`, `32`, and `44`.
The size-32 result did not continue improving at size 44, and the three
log2-size slopes were `0.001604`, `-0.219283`, and `-0.006720`. No scaling or
data-sufficiency extrapolation is justified.

## Outcome Router

The frozen Loop 50 router selects `L50-R05`:

```text
stable nonseparability -> park S24 acquisition for this model family
```

`H4` is supported, no candidate or linear family clears the prior rule, and
`H6` does not establish registered nonsaturation. The result therefore does
not justify spending roughly 1.05 GB on S24 to extend the same model family.
S24 remains metadata-only and unopened. S25 remains physically unopened and
final-only.

This route is a decision to park acquisition for the current family, not a
claim that S24 lacks neural information and not an authorization to acquire a
backup participant. Any representation-repair experiment must receive its own
prospective contract and any Tier C post-outcome or protected-data operation
still needs a separate exact decision.

## Resource Ledger

| Stage | Runtime | Peak RSS | Generated/output bytes |
|---|---:|---:|---:|
| Static identity gate | `0.956671` sec | `209,305,600` | report only |
| Derivative creation | `0.599360` sec | `150,568,960` | `8,854,787` before report |
| Parameter updates | `185.354233` sec | included below | `261,811` checkpoint bytes |
| Target-blind stage | `188.584455` sec | `483,540,992` | `9,260,264` before freeze |
| Cumulative execution through freeze | `190.140486` sec | `483,540,992` maximum | `87,503` private prediction bytes |
| One-shot score | `0.112110` sec | `52,199,424` | `174,849` public result bytes |
| Total generated execution artifacts | n/a | below 1 GiB cap | `9,623,773` bytes |

Free disk before execution was `41,714,499,584` bytes, above the registered
20 GiB floor. The maximum measured peak RSS was `483,540,992` bytes, below the
1 GiB cap. Total generated output was below the 32 MiB cap. The run used one
CPU thread, one worker, no download, and no concurrent numerical job.

The exact execution ledger records:

- 15 causal-candidate training runs;
- 3 linear training runs;
- 2 control training runs;
- 20 checkpoint writes and zero checkpoint reads;
- 4,800 optimizer steps;
- 35 target-blind model-inference runs;
- 5 train-only no-signal prior fits;
- 41 frozen prediction sets;
- 1 check-scoring run;
- 11 check targets delivered after the remotely green freeze;
- 0 check targets delivered before the remotely green freeze;
- 0 validation, source-test, session-2, raw FIF/MAT, network, language-model,
  NeuroToken, RW3, stream, device, or hardware operations;
- 0 post-check parameter updates, configuration changes, or reruns.

The model is causal with two frames of left context and zero right context.
The upstream sentence cache is offline/noncausal, so end-to-end causality and
latency were not measured. Direct energy use is unavailable.

## What Was Proven

The engineering path proved that a protected train-only diagnostic can enforce
one hash pass, deterministic split binding, target-withheld prediction freeze,
remote-green target release, exact paired scoring, bounded resources, and a
machine-checkable no-rerun ledger.

The scientific diagnostic established only that, under this one frozen
post-outcome protocol, the fixed transformed representation was stably
nonseparable for both the tiny causal and linear probe families relative to
the train-only prior. It also weighed against the four registered fixed timing
offsets as the main explanation.

## What Remains Unproven

This result does not establish:

- neural advantage or useful text decoding;
- sensor-signal dependence or brain-specific origin;
- raw MEG signal quality or exclusion of ocular, muscular, motion, auditory,
  or task-locked shortcuts;
- independent validation or unseen-person generalization;
- causal preprocessing of the source cache;
- real-time end-to-end latency;
- EEG, portable, home-device, assistive, diagnostic, or clinical performance;
- that a larger model, another representation, more data, or S24 would fail.

## Final Disposition

Loop 48 Stage B is complete and consumed. Do not rerun any fit, inference,
prediction, target delivery, or score; do not tune from the 11 check outcomes;
and do not reopen validation, source test, session 2, S7, S20, S24, or S25.

Engineering capability added: NeuroDecodeKit now has a one-shot,
target-firewalled train-only failure-discrimination path with exact provenance,
resource accounting, hypothesis decisions, and a remotely green prediction
freeze.

Scientific claim not established: the run did not show neural advantage,
brain-specific decoding, independent generalization, real-time performance, or
portable/home EEG performance.
