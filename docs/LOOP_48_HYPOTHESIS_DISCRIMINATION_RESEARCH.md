# Loop 48 Hypothesis Discrimination Research

Date: 2026-07-15

Status: **Design research only; not preregistered, implemented, or authorized**

Machine boundary: `registries/loop48_hypothesis_discrimination.v0.json`

This additive research note preserves the green five-hypothesis portfolio at
commit `0ffdf47`. It does not modify the Stage A request, authorize Stage A, or
turn Stage B into an experiment.

## Why The Portfolio Needed Another Pass

The first portfolio correctly stopped treating `F5` blank-heavy instability as
a root cause. It still left three scientific ambiguities:

1. `H1` could be misread as a verdict on CTC generally instead of a diagnosis
   of the exact 2,908-parameter, 240-step recipe that failed here.
2. Data quantity and sentence diversity were folded into representation
   separability even though Brain2Qwerty v2 identifies them as independent
   performance axes for asynchronous decoding.
3. A future successful train-only probe could be overpromoted from
   sensor-signal dependence to brain-specific origin despite the overt typing
   task and missing synchronized peripheral controls.

The improved design therefore uses **six coexisting failure hypotheses** plus
one orthogonal claim-validity threat. It separates descriptive measurements
from pipeline interventions and from biological claims.

## Six Coexisting Hypotheses

| ID | Exact hypothesis | Strongest discriminating pattern | Pattern against it | Maximum local conclusion |
|---|---|---|---|---|
| `H1` | The fixed tiny CTC recipe is infeasible or fails to optimize | impossible per-item alignment, tiny-fit failure, persistent blank/loss pathology, or unstable gradients under the frozen recipe | every item is feasible and the same recipe reliably fits a tiny train-only subset | this fixed recipe failed; not that CTC is unsuitable |
| `H2` | Sensor or trial quality is insufficient for this slice | preregistered flatness, robust-amplitude, line-noise, missingness, or trial-quality failures that co-occur with failed probes | quality floors pass and stable task-locked train-only probes survive corruption controls | this slice fails declared quality floors; not that S21 lacks neural information |
| `H3` | Timing or preprocessing misplaces or removes useful information | an off-center train-only time profile or a declared paired transform contrast isolates timing or transform sensitivity | centered timing profile and paired transform agreement under the same split and probe | this pipeline is timing/transform sensitive; not that one transform is biologically correct |
| `H4` | The available representation is stable but not separable on a disjoint train-only check partition | stable fit dynamics plus failure of both simple and sequence probes to beat intact-versus-corrupted controls | a simple task-locked probe succeeds while continuous CTC fails | this representation/probe combination is not separable at the measured scale |
| `H5` | The sentence task remains prior-dominated | intact signal clears registered corruption controls but fails the frozen practical-margin or paired-uncertainty gate against a train-only no-signal prior | intact signal clears the preregistered practical margin and paired uncertainty gate against the prior and every frozen corruption on the same check rows | sensor evidence does not clear the prior for this diagnostic partition |
| `H6` | Data quantity or sentence diversity is insufficient for stable asynchronous estimation | fit succeeds, train-only check error improves with nested unique-sentence prefixes, seed dispersion shrinks, and no plateau appears | stable fit/check behavior and an early plateau that remains insensitive to additional unique rows | the observed 55-row range is non-saturated; not that more data will necessarily create an advantage |

The hypotheses may coexist. Weak quality can amplify optimization instability;
timing error can hide an otherwise separable representation; and low data can
make every other estimate noisy. The output must remain a support vector, not
a forced winner.

## Why `H6` Must Be Separate

Brain2Qwerty v2 is the clearest primary-source warning against treating a
55-sentence CTC failure as a general neural verdict:

- its asynchronous CTC encoder improved from mean CER `0.59` on the lower-data
  SpanishBCBL setting to `0.25` on the larger EnglishBCBL setting;
- performance improved log-linearly through about 90 pooled recording hours
  without an observed plateau; and
- at matched sentence count, 256 unique sentences typed once produced lower
  CER than 128 unique sentences repeated twice (`0.45` versus `0.65`).

Those are external results from a much larger, noncausal, GPU-scale system.
They make data quantity and diversity plausible mechanisms; they do **not**
transfer an exponent, threshold, architecture, or expected score to S21. A
future local `H6` result may say only whether the bounded train-only curve is
still moving and whether seed dispersion contracts inside the observed range.

## Evidence Ladder

| Level | Meaning | Permitted wording |
|---|---|---|
| `E0` | required field unavailable | unresolved |
| `E1` | aggregate or static description | observed phenotype or feasibility fact |
| `E2` | train-only pipeline discrimination under a frozen intervention | supports or weighs against one pipeline mechanism |
| `E3` | intact signal clears every registered train-only corruption and prior by the preregistered practical margin and paired uncertainty gate | bounded sensor-signal dependence on the diagnostic partition |
| `E4` | synchronized peripheral controls and a fresh prospective cohort also pass | eligible for the separate Loop 35 brain-origin review |

Stage B can reach at most `E3`, and only after a separate preregistration and
authorization. The current design is at `E0/E1`. `E4` is unavailable because
the source slice lacks the complete synchronized peripheral-control set.

## Shared Sequential Discrimination Plan

The hypotheses are compared in parallel scientifically. Numerical work remains
sequential, one-threaded, and single-worker.

| Stage | Shared evidence collected once | Primary hypotheses | Current state |
|---|---|---|---|
| `D0` | exact committed-artifact integrity and aggregate arithmetic | provenance plus existing `F5` phenotype | Stage A requested, not authorized |
| `D1` | per-item CTC feasibility, target/input ratios, channel/trial quality, timing uncertainty, and hashes | `H1`, `H2`, `H3` | not preregistered |
| `D2` | frozen-step loss, gradient/update norms, blank posterior, entropy, margins, and tiny-fit metrics | `H1`, `H6` | not preregistered |
| `D3` | one disjoint train-only check bundle for a simple task-locked probe, linear sequence probe, and fixed tiny CTC recipe | `H1`, `H4`, `H6` | not preregistered |
| `D4` | prior, exact-zero, label/row/channel derangement, nonwrapping displacement, and any declared paired transform | `H2`, `H3`, `H4`, `H5` | not preregistered |
| `D5` | support vector, conflicts, evidence completeness, resources, and smallest next falsifier | all hypotheses plus claim firewall | not preregistered |

No stage may create a fresh prediction bundle after seeing check labels. Shared
predictions freeze before check-label interpretation. No favorable seed,
threshold, model, time offset, or transform may be selected.

## Discriminating Result Patterns

| Observed pattern | Interpretation | What remains unresolved |
|---|---|---|
| static CTC infeasibility | supports `H1` directly | signal quality and biological information |
| feasible lengths but tiny-fit failure | supports fixed-recipe `H1` | whether scale, quality, or timing caused the optimization failure |
| tiny-fit success, task-locked probe success, continuous check failure | weighs toward `H1`/`H3` over `H2` | objective versus exact timing contribution |
| quality-floor failure plus failed simple and sequence probes | supports `H2` | whether quality is the sole cause |
| centered quality-passing probe but off-center time-shift peak | supports `H3` | preprocessing versus event-timing source |
| stable intact signal clears corruptions but not the prior margin/uncertainty gate | supports `H5`; it does not reach `E3` | useful decoding, bounded sensor dependence, and brain-specific origin |
| fit succeeds and unique-sentence curve improves without plateau | supports `H6` | extrapolated benefit of unobserved data |
| all declared evidence passes but check performance remains null | supports `H4` or an unresolved low-effect regime | proof of absence and behavior on a fresh person |

## Non-Identifiability Rules

Some outcomes cannot uniquely identify one mechanism:

- blank dominance alone cannot distinguish `H1`, `H2`, `H3`, or `H6`;
- a failed simple probe cannot distinguish weak quality from weak information
  without the quality audit;
- an improving learning curve cannot prove that more data will cross the prior;
- an offline-versus-causal difference cannot identify which individual
  preprocessing operation caused it; and
- intact-signal superiority over corruptions does not establish brain-specific
  origin in an overt typing task.

Conflicting support must be retained. The report may return multiple supported
hypotheses or `unresolved`; it may never manufacture a single root cause for a
clean narrative.

## Orthogonal Claim Threat `T1`

`T1` is peripheral or task-locked shortcut dependence. Brain2Qwerty v1 and v2
both show strong motor-linked information during overt typing. A future simple
probe or intact-versus-corrupted win would therefore be scientifically useful,
but it would not show that the discriminating information originates in brain
activity rather than eye, muscle, head-motion, acoustic, behavioral-timing, or
other task-locked channels.

Any positive Stage B sensor-dependence result must route to the separately
authorized Loop 35 firewall. Stage B cannot satisfy that firewall by itself.

## What Remains Deliberately Unfrozen

The following cannot be chosen from this research note:

- exact train-only fit/check row counts;
- exact subset or optimizer seeds;
- support thresholds or quality floors;
- model and probe inventory;
- number of fits, inferences, predictions, or checkpoints;
- runtime, RSS, and generated-output caps; and
- any interpretation or stopping rule that depends on consumed validation.

These fields require the exact Stage A sequence and a separately authorized
dependency-light static prototype before a Stage B preregistration can be
honest about resource costs. The eventual split must remain entirely inside
the 55 source-train rows, grouped by normalized sentence identity.

## Primary Sources

- Brain2Qwerty v2 preprint, asynchronous CTC, scale, diversity, architecture,
  and noncausal limitation:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Brain2Qwerty v1, task-locked linear probes before sentence decoding:
  https://www.nature.com/articles/s41593-026-02303-2
- CTC peaky behavior and the input-to-target ratio:
  https://arxiv.org/abs/2105.14849
- Data quantity, task, modality, and averaging effects in non-invasive word
  decoding:
  https://www.nature.com/articles/s41467-025-65499-0
- Systematic preprocessing sensitivity and artifact-interpretation risk:
  https://arxiv.org/abs/2410.14453

These sources motivate the hypotheses. None identifies the cause of the local
Loop 26 result.

## Authorization And Claim Boundary

This note authorizes nothing. No fixture, split, prototype, cache, array,
signal, target, model, training, prediction, checkpoint, score, download,
stream, device, or hardware operation occurred. Stage A authorization cannot
transfer to any `D1-D5` operation.

Engineering capability proposed: a six-hypothesis discrimination map now
separates fixed-recipe failure, quality, timing, representation, prior, and
data-regime explanations while reusing one future train-only evidence bundle.

Scientific claim not established: no hypothesis is confirmed, no new neural
evidence exists, and neural advantage, useful decoding, brain-specific origin,
generalization, causal real-time operation, EEG portability, home use, and
clinical utility remain unestablished.
