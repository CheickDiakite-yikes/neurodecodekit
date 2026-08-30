# Scientific Result Hard Decision Tree

Date: 2026-08-30

Status: active scientific router; strategy only; no data, model, score, live,
release, or claim authority

## Governing Objective

Obtain belief-changing evidence about whether central scalp EEG adds
participant-generalizing motor-task information beyond the strongest recorded
task, eye, muscle, posterior-EEG, and matched-counterfactual explanations.

The near-term claim is not thought decoding, spontaneous intention, exclusive
motor-cortex origin, or live decoding. Its ceiling is an increment from central
scalp EEG beyond recorded comparators, with temporal and spatial signatures
consistent with sensorimotor physiology.

## Adversarial Review Corrections

Four independent read-only critics examined the strategy from biostatistical,
EEG neurophysiological, replication, and resource-constrained systems
perspectives. Their corrections govern future source-specific design:

1. The FMSR1 minimum of ten complete participants is a source-admission floor,
   not automatic confirmatory power.
2. Posterior EEG is a neural spatial comparator, not a non-neural nuisance.
3. Residualization cannot prove that an EEG signal is artifact-free and must
   be accompanied by direct joint-comparator and sensitivity analyses.
4. "EEG wins" means a conjunctive improvement over both joint recorded
   controls and an equally shaped structure-preserving derangement.
5. Participant, not trial, is the inferential unit. Development, confirmation,
   and replication participants remain disjoint where the source permits.
6. Live motor success does not validate language decoding. Communication is a
   separate program with a free-choice target and LM-only baseline.

## 3D Attribution Cube Inside A 5D Evidence Map

The scientific architecture has a three-dimensional attribution core nested
inside a five-dimensional evidence map. Live operation is a separate sixth
translation dimension.

### Dimensions 1-3: What Produced The Signal

More models are not the priority. The core attribution cube crosses three axes:

```text
spatial:       central EEG vs geometry-matched posterior EEG
temporal:      motor window vs pre-cue, cue, and structure-preserving shifted windows
physiological: real central EEG vs joint EOG/EMG/metadata and deranged EEG
```

All three axes must support the same interpretation. A win on only one or two
axes is diagnostic evidence, not a neural-attribution claim. A result must
occupy the correct corner: central location, correct motor timing, and
predictive increment beyond recorded nuisance and matched counterfactuals.

### Dimensions 4-5: What The Result Means And How Far It Generalizes

4. **Task identifiability and autonomy:** externally instructed labels versus
   genuinely self-chosen actions. An instructed task can support protocol-
   condition decoding; only a target-identifiable, cue-resistant self-chosen
   design can advance toward intention.
5. **Population generalization:** same-person performance versus untouched
   participants versus an independently recruited or independent-source
   replication cohort. These are distinct claim levels and cannot be pooled.

The complete five-dimensional evidence coordinate is therefore:

```text
(spatial attribution,
 temporal attribution,
 physiological attribution,
 task autonomy,
 population generalization)
```

### Dimension 6: Whether It Works Prospectively In Time

Translation is a separate ordered dimension:

```text
offline evaluation -> causal replay -> shadow stream -> prospective live
```

Movement along dimension six cannot repair a weak coordinate in dimensions
one through five. A live protocol shortcut remains a shortcut. Conversely, a
live translation failure does not erase an otherwise valid offline scientific
result.

Live motor success also does not validate language decoding. Communication
requires a separate preregistration, free-choice task, synchronized peripheral
controls, independently scored LLM-only baseline, neural-increment test, and
independent replication.

## Capacity-Matched Cube Roles

Future source-specific preregistration must keep the three attribution axes
separable and define capacity-matched conditions:

```text
N       = cue + timing + non-neural metadata + EOG + all relevant-effector EMG
C_motor = central EEG in the registered motor window
P_motor = geometry-matched posterior EEG in the same motor window
C_pre   = central EEG in the registered pre-cue window
C_cue   = central EEG in the registered cue window
S_k(C)  = fixed, structure-preserving temporal shift k of central EEG
D_k(C)  = fixed, target-blind, structure-preserving derangement k of central EEG

MN     = model(N)
MC     = model(N + C_motor)
MP     = model(N + P_motor)
Mpre   = model(N + C_pre)
Mcue   = model(N + C_cue)
Mshift = model(N + S_k(C))
MD     = model(N + D_k(C))
```

`N` must not silently absorb posterior EEG because posterior EEG is the spatial
neural comparator. The no-signal prior remains a mandatory sanity baseline, but
beating it alone cannot establish any attribution coordinate.

Temporal shifts and derangements preserve participant, run, cue/timing stratum,
feature shape, spectral statistics, missingness, and nuisance magnitude while
breaking the registered timing or target alignment. Their fixed offset and seed
sets and aggregation rules freeze before confirmation.

The compact default family is forward-only fixed slow-potential, mu, and beta
features; geometry-normalized homologous central contrasts; training-fold
robust scaling; L2 logistic regression; and source-only calibration. A larger
model may not replace a failed compact test on the same confirmation target.

## Primary Scientific Estimand

For each untouched confirmation participant `i`, let `L_i(M)` be participant-
balanced natural-log loss. The attribution cube requires every registered edge
to point toward the central motor-window model:

```text
dN_i     = L_i(MN) - L_i(MC)
dD_i     = mean_k(L_i(MD_k)) - L_i(MC)
dP_i     = L_i(MP) - L_i(MC)
dpre_i   = L_i(Mpre) - L_i(MC)
dcue_i   = L_i(Mcue) - L_i(MC)
dshift_i = mean_k(L_i(Mshift_k)) - L_i(MC)

theta_attribution = min(
    mean_participants(dN),
    mean_participants(dD),
    mean_participants(dP),
    mean_participants(dpre),
    mean_participants(dcue),
    mean_participants(dshift),
)
```

The source-specific confirmation must freeze an intersection-union decision
over those edges and its minimum meaningful effects. One strong edge cannot
average away another failed edge. Participant-macro natural-log loss is
primary. Balanced accuracy, Brier score, calibration error, bands, windows,
and individual nuisance conditions are secondary and cannot rescue failed
primary log loss.

The minimum meaningful effect, powered participant count, confidence method,
intersection-union test, participant-consistency rule, probability clipping,
and exclusions must be justified on development data and frozen before
confirmation. `0.020` nats/trial is the inherited reference effect, not an
automatic threshold for every source.

Ten participants can support source admission or a labeled pilot. A
confirmatory label requires prospective participant-level power; fewer than
the powered count routes to `INCONCLUSIVE_UNDERPOWERED`. Prefer a surface that
can reserve disjoint development and confirmation cohorts, with an independent
replication source or recruitment wave fixed before the first result is seen.

## Three Positive-Control Gates

Confirmation remains sealed unless all three pass on development data:

1. **Sensor control:** registered EOG and all-effector EMG calibration signals
   are recoverable and synchronized.
2. **Neural sensitivity:** central mu/beta activity shows the preregistered
   within-person motor effect with the expected temporal order.
3. **Pipeline sensitivity:** an injected plausible neural effect survives the
   complete preprocessing and scoring path while label rotation and displaced
   windows fail.

Positive-control failure is `INVALID_SENSITIVITY`, never evidence that neural
information is absent. Confirmation participants cannot be selected or
excluded using their positive-control outcomes.

## Ordered Scientific Ladder

1. **Source discovery:** exactly one complete-or-park FMSR1 pass.
2. **Transport admission:** candidate metadata, tiny opaque canary, then one
   fixed header before bulk scientific acquisition.
3. **Measurement admission:** verify roles, geometry, synchronization, task
   identifiability, events, exact bytes, and reusable license.
4. **Power and cohort reservation:** freeze development, confirmation, and
   replication boundaries before signal or target use.
5. **Sensitivity qualification:** pass all three positive-control gates.
6. **Bounded discovery:** log every attempted representation and select one
   compact family under a frozen development budget.
7. **Scientific freeze:** freeze every transform, exclusion, model, seed,
   comparator, metric, threshold, test, stopping rule, and claim route.
8. **Untouched confirmation:** freeze predictions before one target delivery
   and score; no post-target repair or rerun.
9. **Independent replication:** repeat the unchanged scientific question in a
   distinct dataset, laboratory, or recruitment wave selected without outcome
   shopping.
10. **Translation:** move separately through offline, causal replay, shadow
    stream, and then one prospective live motor test. Language remains a
    separately preregistered program with an independently scored LLM-only
    baseline.

## Hard Decision Tree

| Observation | Mandatory route |
|---|---|
| Complete search finds no qualifying source | Stop public-source hunting and preregister a motor-specific synchronized EEG/EOG/EMG prospective cohort |
| Search is incomplete or hits a cap | `DISCOVERY_CAP_PARK`; do not infer that no source exists |
| Transport or header admission fails | Engineering refusal; no biological interpretation and no payload escalation |
| Sensor control fails | Repair measurement, not the model |
| Neural or injected-effect control fails | `INVALID_SENSITIVITY`; confirmation remains sealed |
| Within-person passes but unseen-person fails | Test at most one preregistered geometry/alignment hypothesis on a separate development surface |
| `MC` fails against `M0` | No central-EEG increment beyond the recorded joint comparator under this method |
| `MC` beats `M0` but not `MD` | Association without matched EEG identity; leakage or protocol structure remains viable |
| Both primary contrasts pass but spatial or temporal specificity fails | Unexplained protocol-related EEG increment, not motor-specific evidence |
| Attribution cube passes only on an externally instructed task | Decoding of a protocol condition; do not call it self-chosen intention |
| Attribution and autonomy pass only within person | Within-person result; do not claim untouched-person generalization |
| Confirmation passes once | Preliminary nuisance-resistant unseen-person central-scalp EEG result |
| Independent replication fails | `FAILED_TO_REPLICATE`; preserve the first result as cohort-specific |
| Confirmation and independent replication both pass | Replicated nuisance-resistant unseen-person central-scalp EEG increment |
| Causal shadow fails | Offline result remains; translation claim fails |
| Live motor test passes | Begin a separate communication program; do not inherit the motor claim |

## Prospective Fallback If No Public Source Qualifies

The fallback is a smaller motor-specific study, not the existing ambitious
communication protocol. Its primary task should be self-chosen left versus
right movement:

- a generic visual signal carries no side identity;
- the participant freely chooses a side;
- bilateral EMG and force or kinematics determine and seal the target after
  movement;
- the primary neural window ends before the earliest peripheral onset with a
  prospectively frozen safety margin;
- EEG, EOG, bilateral EMG, force or kinematics, triggers, geometry, and known
  reference are synchronized; and
- a pre-peripheral margin curve tests whether information appears before
  measured movement.

A provisional efficient design is a small pilot followed by separate powered
confirmation and replication waves. Exact sample size, channel count, duration,
packed storage, consent, hardware, and live protocol require a separate
prospective registration and authority. This document grants none.

## Claim Ladder

| Level | Maximum permitted statement |
|---|---|
| `M0` | The source can support the registered experiment; no neural evidence |
| `S1` | The pipeline recovered an expected within-person effect; exploratory sensitivity only |
| `A1` | EEG sensors predicted an instructed task condition; no source attribution |
| `C1` | Central scalp EEG added information beyond recorded joint controls in untouched people; preliminary |
| `R1` | The preregistered increment replicated in an independent cohort or source; belief-changing |
| `T1` | The frozen effect survived sample-causal replay at measured latency; not live |
| `T2` | The frozen decoder prospectively decoded the motor-task condition online; not automatically intention or motor cortex |
| `L1` | EEG added free-choice communication information beyond LM-only and peripheral baselines; separate replicated evidence required |

## Immediate Route

`FMSR1-DISCOVERY-M0-D0` is the sole current decision. Only after that decision
and its exact implementation are separately remotely green may one metadata-
only discovery execution return one source, `NO_QUALIFYING_SOURCE`, or a park
or refusal. No third path of indefinite dataset hunting is allowed.
