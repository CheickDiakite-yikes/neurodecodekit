# Loop 32 Primary-Source Research And Calibration Decision Note

Date: 2026-07-12

Status: **Planning research complete; experiment Not Started; no candidate,
participant data, calibration signal, labels, checkpoint, adapter fit, training,
or final evaluation is authorized**

Machine boundary: `registries/loop32_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 32

## Decision Summary

Loop 32 answers the protocol question before anyone sees a fresh person's
recording:

> What is the smallest honest calibration budget that improves one fresh
> person without using that person's final rows for fitting, normalization,
> model selection, stopping, or thresholding?

The planning answer is deliberately small:

1. Recommend one pointwise, causal, 32-parameter hidden affine adapter over the
   proposed frozen 16-wide Loop 26 causal encoder.
2. Keep strict zero-shot, unlabeled, label-light, and supervised calibration as
   four different modes and four different claims.
3. Recommend nested calibration budgets of `0, 2, 4, 8, 16, 32` unique
   completed sentences. The zero row is the strict zero-shot reference.
4. Require physically distinct calibration, selection, and final recordings,
   with disjoint performed-row IDs and semantic text hashes.
5. Require at least 32 calibration, 16 selection, and 48 final unique completed
   sentences for the full future curve.
6. Hash-freeze zero-shot final predictions before opening any target-person
   calibration data. Freeze one adapted model and budget before one final-target
   open.
7. Promote only when the selected adapter passes practical and paired
   randomization gates against both zero-shot and the train-only no-signal prior,
   and strictly beats every applicable normalization and label-derangement
   control.
8. Count the human burden honestly: task time, setup, practice, breaks, labels,
   label correction, selection labels, compute, and the maintenance interval.
9. Keep S25 session 2 block 2 final-only for Loop 28. It cannot be quietly
   repurposed as Loop 32 calibration data.

These are research recommendations, not a frozen preregistration. No fresh
participant or recording has been selected.

## Why Calibration Is A Separate Claim

Brain2Qwerty v2 reports a leave-one-participant-out regime that pretrains
without the held-out participant and then finetunes on that participant while
keeping the Conformer frozen. That is useful evidence for supervised calibrated
transfer. It is not strict unseen-person zero-shot decoding because target-
participant labels and recordings influence the final model.

The distinction is operational:

```text
strict zero-shot
  = no target-person signal, labels, statistics, fit, or selection before the
    frozen zero-shot prediction

unlabeled calibration
  = target-person calibration signal influences 32 adapter values, but no
    target label selects the budget, stopping point, or threshold

label-light calibration
  = at most 8 labeled calibration sentences, plus every labeled selection item
    reported in the burden ledger

supervised calibration
  = up to 32 labeled calibration sentences, plus every labeled selection item,
    while the 2,908-parameter source model remains frozen
```

Calling any of the last three modes "zero-shot" would erase the main scientific
question Loop 32 is meant to answer.

## Evidence Boundary Before Loop 32

Local evidence does not justify immediate execution:

| Evidence | What it says | What it cannot say |
|---|---|---|
| Loop 15 consumed S21 session 2 | The existing same-person cross-session MEG model was worse than its no-signal prior. | It does not identify a useful adapter or authorize another look. |
| Loop 16 synthetic curve | Robust channel-affine matching repairs an easy stationary diagonal shift. | It harms channel-mixing and time-varying shifts and gives no human calibration-time estimate. |
| Loop 28 research | Strict zero-shot and calibrated transfer need different access rules. | Its selected S25 block has no separate calibration or selection recording. |
| Loop 31 research | Sensor dependence must be separated from timing, language, context, and pipeline effects. | The attribution experiment has not run and no sensor-signal advantage exists. |
| Brain2Qwerty v2 | Per-participant components and held-out-participant finetuning can help a large public research system. | It does not provide a local fresh-person cache, released Neuro Tokens, strict zero-shot result, or at-home device claim. |

No consumed S7 or S21 payload was reopened during this research pass.

## Primary-Source Findings

### 1. V2 motivates calibration but does not define our zero-shot gate

The public Brain2Qwerty v2 paper and pinned implementation use participant-
specific model components. The leave-one-out appendix then adapts to the held-
out participant. This motivates a carefully labeled calibrated-person lane,
but it does not allow NeuroDecodeKit to call finetuned performance zero-shot or
to assume access to the unreleased EnglishBCBL data or Neuro Token payloads.

Sources:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- pinned official code:
  https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2

### 2. Unlabeled adaptation is useful but still transductive

CORAL aligns second-order source and target statistics without target labels.
Euclidean Alignment applies a computationally light unsupervised alignment to
EEG trials without new-subject labels. Both sources motivate an unlabeled lane.
Neither makes target-person access disappear: the target distribution changes
the fitted transform, so the result must be called unlabeled or transductive
calibration rather than strict zero-shot transfer.

Sources:

- CORAL:
  https://ojs.aaai.org/index.php/AAAI/article/view/10306
- Euclidean Alignment:
  https://pubmed.ncbi.nlm.nih.gov/31034407/

The proposed v0 adapter remains diagonal rather than covariance-aware. That is
intentional: it is small, inspectable, and consistent with the Loop 16
mechanism test. It also preserves the known failure boundary instead of hiding
it. A future covariance adapter would be a different registered family, not a
post-access patch.

### 3. Fewer current-session trials can matter, but task and population do too

Long-term BCI work has evaluated reducing current-session calibration by using
earlier sessions. That evidence comes from a motor-imagery rehabilitation
setting with a different population, task, signal objective, and evaluation
surface. It supports measuring calibration burden and maintenance over time;
it does not supply a sentence-decoding budget for NeuroDecodeKit.

Source:

- long-term BCI calibration reduction:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10790953/

This is why the future packet must report actual minutes and repeat attempts.
The `1.26` synthetic signal seconds associated with Loop 16's one-row result
must never be translated into "1.26 seconds of human calibration."

### 4. Selection and final evidence must be physically separated

Predictive neuroimaging guidance emphasizes that model assessment and tuning
must remain separated. Loop 32 therefore treats calibration, selection, and
final evidence as three different physical identities, not three slices chosen
after reading one recording.

Source:

- brain-decoder cross-validation guidance:
  https://pubmed.ncbi.nlm.nih.gov/27989847/

The final partition is not a reservoir for normalization, confidence fitting,
endpoint tuning, or budget selection. Even target-wide unlabeled statistics
from final rows would make the final comparison transductive and invalidate the
registered design.

## Recommended Adapter Family

The proposed source model from Loop 26 has a 16-wide final hidden state and a
2,908-parameter causal Conv-CTC architecture. Loop 32 recommends inserting one
diagonal affine transform immediately before the 28-class projection:

```text
adapted_hidden[t, j] = scale[j] * hidden[t, j] + bias[j]

hidden width:                    16
scale values:                    16
bias values:                     16
target-trainable values:         32
frozen base values:           2,908
total values with adapter:    2,940
extra right context:              0 samples
extra history:                    0 samples
identity initialization:          scale=1, bias=0
```

The adapter is pointwise, so it does not change mechanical causality. Causality
of the complete model still depends on Loop 25 and Loop 26 actually passing.

For unlabeled calibration, the recommended fit is robust source-train versus
calibration-only hidden median/IQR matching. For label-light and supervised
calibration, only the same 32 values may be optimized with CTC; the source
encoder and output head remain frozen.

The family cannot generally fix:

- rotated or mixed sensor spaces;
- missing or renamed channels;
- incompatible device geometry;
- within-sentence drift;
- timing misalignment;
- language-prior or prompt leakage;
- peripheral or motor confounds.

These are explicit failure boundaries, not implementation details to tune away
after target access.

## Calibration Modes

| Mode | Target signal before adapted final prediction | Target labels before final target open | Selection rule | Maximum local claim |
|---|---:|---:|---|---|
| `L32-M0` strict zero-shot | No | 0 | No calibration selection | One-person zero-shot reference |
| `L32-M1` unlabeled | Calibration only | 0 | Budget fixed before access or by a frozen label-free criterion | One-person unlabeled calibrated improvement |
| `L32-M2` label-light | Calibration only | At most 8 calibration sentences, plus declared selection labels | One budget selected on the separate selection partition | One-person label-light calibrated improvement |
| `L32-M3` supervised | Calibration only | At most 32 calibration sentences, plus declared selection labels | One budget selected on the separate selection partition | One-person supervised calibrated improvement |

Only one mode may be selected in a future authorization. Running all three
calibration modes and reporting only the best final result would be hidden
model selection.

For `L32-M1`, target selection labels are forbidden. If target labels influence
the budget, stopping rule, transform, or threshold, the result is label-
informed and must move to `L32-M2` or `L32-M3`.

## Budget And Physical Partition

Recommended nested calibration schedule:

```text
unique completed calibration sentences: 0, 2, 4, 8, 16, 32
label-light eligible sizes:               2, 4, 8
supervised eligible sizes:                2, 4, 8, 16, 32
full calibration recording floor:        32 unique completed sentences
selection recording floor:               16 unique completed sentences
one-time final recording floor:           48 unique completed sentences
```

The three floors imply at least 96 unique completed rows for a full candidate.
Repeated attempts, dropped rows, restarts, and unusable recordings do not
silently disappear: they count toward participant burden even when they do not
count toward the unique completed-row floor.

The future metadata packet must prove:

- three distinct physical block or session IDs;
- disjoint performed-row IDs;
- disjoint normalized semantic text hashes;
- one person, device configuration, and prompted-typing task;
- exact source revision, license, consent, retention, and bytes;
- no source-model person overlap;
- no target-wide final statistics used by the adapter.

S25 session 2 block 2 fails the first requirement because Loop 28 reserves it
as a final-only zero-shot candidate. A new physically separated acquisition or
an independently suitable existing candidate would need its own metadata-only
review and exact authorization.

## Conditions And Controls

Every future final comparison uses identical rows and metric code:

| ID | Condition | Purpose |
|---|---|---|
| `L32-A00` | Frozen strict zero-shot source model | Primary uncalibrated reference |
| `L32-A01` | Identity affine adapter | Must reproduce `A00` predictions exactly |
| `L32-A02` | Selected mode-specific adapter | Primary calibrated candidate |
| `L32-A03` | Source-train-only no-signal prior | Signal-free comparator |
| `L32-A04` | Unlabeled robust normalization-only | Unlabeled candidate or comparator for labeled modes |
| `L32-A05` | Calibration-label derangement | Same 32 parameters and budget for labeled-mode correspondence control |

The label-derangement condition applies to label-light and supervised modes.
It is not meaningful for the zero-label fit. Identity mismatch is a plumbing
failure, not a tolerable numerical difference.

Loop 31 remains the upstream attribution firewall. Even a clean Loop 32 gain is
not automatically a brain-specific result; it could still depend on motor,
ocular, muscular, timing, environmental, prompt, or other task-locked signal.

## Freeze And Access Order

The future sequence is fail-closed:

1. Complete the compatible Loop 25 and Loop 26 gates without reopening source
   test or session 2.
2. Select one metadata-only fresh-person candidate with three physical
   partitions.
3. Freeze the source checkpoint, adapter family, one calibration mode, budgets,
   split hashes, controls, statistics, resources, and claim wording.
4. Commit and push the hash-bound preregistration, then prepare a separate exact
   authorization request.
5. After exact authorization, generate and hash-freeze zero-shot predictions on
   final signal before any target-person calibration signal or label is opened.
6. Open only the authorized calibration partition and only the labels allowed
   by the chosen mode.
7. Fit only the 32 adapter values and registered controls.
8. Use selection labels only for label-light or supervised modes, then freeze
   exactly one adapter and budget.
9. Generate and hash-freeze every adapted, prior, and control prediction on the
   same final rows while final targets remain closed.
10. Open final targets once, score every condition in one pass, write an
    append-only report, and mark the final partition consumed.
11. Close as support or park. No restart, mode change, budget change, adapter
    search, or backup candidate follows a disappointing result.

This ordering preserves both comparisons: zero-shot predictions are genuinely
pre-calibration, while calibrated predictions use only the declared calibration
and selection evidence.

## Statistical Recommendation

The primary adaptation effect is:

```text
delta_adaptation = mean_i(CER_zero_shot_i - CER_selected_adapter_i)
```

The signal-free comparison is:

```text
delta_prior = mean_i(CER_prior_i - CER_selected_adapter_i)
```

Positive values favor the adapter. With at least 48 unique final sentences, the
future contract should use 65,535 preregistered random sign assignments plus
the observed assignment, for 65,536 reference statistics total. The one-sided
paired alpha recommendation is `0.05`.

The current practical recommendations are:

```text
macro CER gain versus zero-shot >= 0.05
macro CER gain versus prior     >= 0.05
strict win over every applicable normalization/derangement control
control tie passes              = false
selection gain overrides final harm = false
```

The two `0.05` margins are not frozen until preregistration. The overall future
decision is conjunctive: every applicable component must pass. A descriptive
paired bootstrap may show uncertainty but cannot replace the registered
decision or create biological replication from one participant.

## Human Burden Ledger

"Eight calibration sentences" is not enough reporting. The future closeout
must include:

- unique calibration sentences and repeated attempts;
- active signal seconds;
- prompt or listening seconds;
- typing or response seconds;
- setup, practice, breaks, and total wall minutes;
- sentence, character, and key labels exposed;
- label verification and correction minutes;
- selection sentences and labels exposed;
- adapter runtime, peak RSS, artifact bytes, and working bytes;
- elapsed time from calibration to final evaluation;
- measured recalibration or maintenance interval, or an explicit unavailable
  field.

The label-light ceiling counts only calibration rows, but the headline burden
must also count every labeled selection row. Otherwise the protocol would hide
supervision in model selection.

## Measured Research Boundary

```text
high-level public-web research operations:         4
public GitHub API source reads:                     2
public network operations total:                    6
protected dataset/model download bytes:             0
local real path or payload-hash reads:               0
raw signal or header reads:                          0
real-cache content reads:                            0
calibration/selection/final signal reads:            0 / 0 / 0
calibration/selection/final target reads:            0 / 0 / 0
consumed evidence reads:                             0
checkpoint/model/adapter-fit/training runs:          0 / 0 / 0 / 0
parameter updates:                                   0
control prediction/final evaluation runs:            0 / 0
RW3, SDK, socket, stream, device, hardware ops:       0
CPU threads / workers:                               1 / 1
current planning artifact cap:                       8 MiB
```

Complete public-network response bytes, one end-to-end interactive research
runtime, and interactive peak RSS are unavailable from the browser/API tool
contracts. Candidate-specific calibration minutes are unavailable because no
candidate or task timing pilot exists. These fields remain unavailable rather
than being estimated.

A future separately authorized run remains bounded to one thread and worker,
32 target-trainable values, 2,940 total values, 1,200 seconds of adapter fits,
1 GiB peak RSS, and 32 MiB generated artifacts. The user's 5-10 GB incremental
storage envelope remains capacity, not data-access or execution authorization.

## Claim Taxonomy

| ID | Claim | Available now? |
|---|---|---:|
| `L32-C0` | No new result; planning boundary only | Yes |
| `L32-C1` | Strict zero-shot reference for one fresh person | No |
| `L32-C2` | Unlabeled calibrated improvement for one person | No |
| `L32-C3` | Label-light calibrated improvement for one person | No |
| `L32-C4` | Supervised calibrated improvement for one person | No |
| `L32-C5` | Cross-session calibration maintenance | No |
| `L32-C6` | Population, device, or brain-specific generalization | No |

Even a future `C2-C4` pass would remain person-, task-, device-, partition-,
mode-, and budget-specific. It would not establish arbitrary-thought typing,
portable hardware, at-home performance, real-time behavior, assistive efficacy,
diagnosis, or clinical utility.

## Decision And Next Gate

Loop 32 planning research is complete. The experiment remains `Not Started`.
The immediate numbered execution gate remains Loop 25, whose amended
preregistration still requires its exact authorization sentence. Loop 26 then
needs a compatible source result, and Loop 31 needs an actual attribution gate
before neural wording is available.

Only after those dependencies exist should a Loop 32 metadata-only candidate
search ask whether a fresh person already has three physically separated
recordings. That search, a candidate-specific preregistration, and execution
authorization are separate future decisions.

Engineering capability added: a machine-checkable calibration taxonomy,
32-parameter adapter recommendation, physical split contract, access order,
burden ledger, controls, and promotion gate now exist for a future fresh-person
study.

Scientific claim not established: no participant payload, adapter, or final
target was accessed, so there is no zero-shot or calibrated-person improvement,
sensor-signal dependence, neural advantage, population generalization,
real-time behavior, or portable-hardware result.
