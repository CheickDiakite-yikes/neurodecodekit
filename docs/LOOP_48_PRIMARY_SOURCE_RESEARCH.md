# Loop 48 Primary-Source Research And Failure-Localization Boundary

Date: 2026-07-15

Status: **Artifact-only research and diagnostic contract prepared; execution
is not authorized**

Machine contract: `registries/loop48_failure_localization_contract.v0.json`

Contract SHA-256: `ecd226f8ae8892e40ecd65c25d59e000384289e9c434886db71dabcfde9e31b1`

Roadmap row: `registries/next_scientific_loops.v0.json` Loop 48

## Decision Summary

Loop 26/31/33 and scientific Loops 46/47 produced one useful negative result:
the fixed S21 candidate lost to the train-only no-signal prior. Loop 48 must
explain what can and cannot be localized from that result before any new model,
participant, or final-only S25 path is considered.

The strongest artifact-level diagnosis is:

> **F5 - seed-sensitive output-distribution instability, with a blank-dominant
> primary checkpoint.**

This is a failure phenotype, not a proven root cause. The public artifacts
show that the registered primary candidate emitted CTC blank on `99.3477%` of
valid frames, decoded zero exact validation sentences, and was `0.186942`
macro CER worse than the no-signal prior. Across the three size-55 seeds, blank
fractions ranged from `0.523848` to `0.997146`, while every model still lost to
the same `0.751235` prior. Across all 18 trained scaling conditions, blank
fractions ranged from `0.002446` to `0.999592`.

That combination is more specific than “the model was bad.” It says the fixed
training recipe did not produce a stable output distribution, and the primary
checkpoint collapsed into near-all-blank emission. It does **not** establish
whether the instability originated in the CTC objective, fixed 240-step
optimization, frame-to-label ratio, weak sensor information, offline
preprocessing, event timing, or some interaction among them.

## Why This Is Post-Outcome Diagnosis, Not A New Performance Preregistration

The six validation outcomes are already consumed and public as aggregates.
Loop 48 cannot be prospective with respect to those outcomes. Its contract is
therefore a post-outcome, artifact-only diagnostic registration whose purpose
is to:

1. bind exact public artifact hashes;
2. make the discrepancy calculations reproducible;
3. enforce one ordered, mutually exclusive primary classification;
4. record every unavailable root-cause field;
5. stop architecture escalation and target-conditioned search.

An eventual artifact-only execution can reproduce the registered arithmetic;
it cannot create independent evidence, rescue the failed gate, or support a
neural claim.

## Exact Committed Evidence

| Artifact | SHA-256 | Role |
|---|---|---|
| `registries/loop26_shared_validation_result.v0.json` | `7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4` | consumed aggregate metrics and access ledger |
| `registries/loop26_prediction_freeze.v0.json` | `10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348` | target-blind prediction identities and resource envelope |
| `registries/loop26_shared_validation_contract.v0.json` | `c4f94b214993973ec4b4ea7e7b27174023dfef227c8dd4d9b912ac48bb98ccce` | frozen model, optimizer, CTC, split, and control definitions |
| `registries/loop25_causal_preprocessing_result.v1.json` | `5f80c4d282be79aadaf78908c151acd3949e0a754182cf58b27dcca681218ab1` | synthetic causal-mechanics prerequisite only |

No cache member, ignored derivative, checkpoint, private prediction, target
bundle, raw FIF/MAT file, or consumed session was read for this planning pass.

## Artifact-Level Evidence Matrix

| Evidence | Observation | What it supports | What it cannot prove |
|---|---:|---|---|
| Primary blank fraction | `0.993477` | primary checkpoint is blank-dominant | why it became blank-dominant |
| Primary versus prior macro CER | `0.938177` vs `0.751235` | candidate has no predictive advantage | absence of neural information in S21 |
| Primary exact sentences | `0/6` | no exact validation decode | future performance with a different design |
| Size-55 blank range | `0.473298` | strong seed sensitivity at fixed data size | optimizer is the sole root cause |
| All-condition blank range | `0.997146` | unstable emission distribution across the frozen curve | whether preprocessing or signal quality drives it |
| Prefix groups over `0.25` blank range | `6/6` | instability is not isolated to one train size | a universal CTC pathology |
| Size-55 models worse than prior | `3/3` | favorable-seed selection cannot rescue the gate | that more data or another participant cannot help |
| Zero/timing controls | each `6/6`, `p=0.015625` | intact candidate is not identical to all-blank controls | complete sensor-signal dependence |
| Full attribution conjunction | failed | no sensor-signal claim | absolute non-neural origin |
| Loop 25 mechanics | passed synthetic target-free gate | one causal transform is mechanically valid | that the Loop 14 cache used it or retained information |

## Ordered Failure Taxonomy

The classes are made mutually exclusive by precedence. The first decisive
class wins; later classes become secondary unresolved possibilities only.

| Order | ID | Class | Decisive evidence |
|---:|---|---|---|
| 1 | `F1` | identity or provenance breach | artifact, split, item, configuration, or target-firewall hash mismatch |
| 2 | `F2` | temporal or CTC infeasibility | any input length cannot represent its normalized target under CTC, or registered length identities disagree |
| 3 | `F5` | fit/output-distribution instability | integrity and feasibility pass, but primary blank dominance and same-prefix seed dispersion cross the frozen descriptive thresholds |
| 4 | `F3` | signal-quality insufficiency | complete train-only channel and trial quality summaries fail a frozen floor without F1/F2/F5 |
| 5 | `F4` | preprocessing or temporal-resolution mismatch | paired train-only causal/offline diagnostics isolate the transform or timing path without F1/F2/F5/F3 |
| 6 | `F6` | stable but nonseparable sensor representation | stable fits fail train-only signal controls after F1-F5 are excluded |
| 7 | `F7` | prior-dominated task regime | stable sensor-dependent fits remain worse than a strong train-only prior after F1-F6 are excluded |
| 8 | `U0` | unresolved | required evidence is unavailable or more than one class remains inseparable |

The current leading class is `F5` because integrity records are exact and the
known emission statistics cross the descriptive F5 rules. `F5` is deliberately
worded as an observable fit/output phenotype. It does not say the optimizer is
the sole causal mechanism.

## Primary-Source Interpretation

### CTC can become pathologically peaky

Zeyer, Schluter, and Ney formally analyze CTC's tendency toward dominant-label
peaks and show that gradient descent can converge to a suboptimal, high-error
solution even in a simple learnable setting. They also show that a larger
input-to-target length ratio amplifies peaky behavior and slows convergence.
That makes blank fraction, frame-to-target ratio, loss trajectory, and seed
dispersion legitimate diagnostics. It does not allow us to infer CTC collapse
from blank fraction alone.

Sources:

- https://arxiv.org/abs/2105.14849
- https://distill.pub/2017/ctc/

### Brain2Qwerty v1 is not this tiny CTC experiment

The published Brain2Qwerty v1 decoder uses keystroke-aligned 0.5-second windows,
a high-dimensional convolutional encoder, a sentence transformer, and a
character language model. Its model inputs are explicitly aligned to keystroke
onsets, and its reported system is sentence-level rather than an end-to-end
real-time decoder. The Loop 26 candidate instead used a 2,908-parameter causal
CTC model over an offline, noncausal sentence cache with no language model.
The v1 result is therefore a scientific reference and architecture contrast,
not a performance expectation for NeuroDecodeKit's tiny gate.

Source:

- https://doi.org/10.1038/s41593-026-02303-2

### Brain2Qwerty v2 changes several axes at once

Meta's June 2026 primary publication page reports that Brain2Qwerty v2 uses
about 22,000 sentences from nine participants with ten recording hours each,
learned event detection, character/word/sentence representations, and
fine-tuned language components. Those differences make data scale, event
detection, representation capacity, and language modeling serious future
research axes. They do not authorize importing v2 claims, unreleased payloads,
or large-model requirements into this consumed S21 diagnosis.

Source:

- https://ai.meta.com/research/publications/accurate-decoding-of-natural-sentences-from-non-invasive-brain-recordings/

## What The Public Artifacts Do Not Contain

The following root-cause fields are unavailable:

- per-step or per-epoch training loss;
- gradient norms, parameter-update norms, and nonblank-logit margins;
- train-only CER and exact sequence accuracy;
- input-length to target-length ratios by train item;
- posterior entropy or blank posterior trajectories;
- per-channel variance, robust amplitude, PSD, line-noise, flat-channel, and
  bad-trial summaries;
- event-timing residuals and per-item alignment uncertainty;
- paired offline-versus-causal train-only representations;
- an independently aligned keystroke-window baseline;
- any fresh development-person evidence.

Without those fields, Loop 48 cannot separate CTC optimization from weak signal,
preprocessing mismatch, or temporal misalignment. The contract records that
uncertainty instead of using validation targets to search for a better model.

## Frozen Artifact-Only Stage A

A future separately authorized Stage A may read only the four committed JSON
artifacts named above. It may:

1. verify exact bytes and SHA-256 identities;
2. recompute the frozen aggregate blank and CER summaries;
3. apply the ordered decision tree;
4. emit one JSON report with no per-item text or prediction;
5. stop with either one primary phenotype or `U0`.

It may not read Git-ignored Loop 26 outputs, caches, derivatives, targets,
checkpoints, private predictions, source test, session 2, S7, S20, or S25. It
may not run a model, train, tune, select a seed, alter a threshold, or recommend
a larger architecture from the six validation outcomes.

Stage A is capped at one CPU thread, one worker, 30 seconds, 256 MiB RSS, and
1 MiB generated output. All protected, model, training, download, network,
stream, device, and hardware counters must remain zero.

## Later Train-Only Diagnostics Are Not Yet Preregistered

The minimum useful follow-up would be a physically separate, train-only
diagnostic stage that measures CTC feasibility, loss and blank trajectories,
gradient/update norms, train-only decoding, and signal-quality summaries. It
would use no validation targets and would freeze its own stop rules before any
train-array read or model run.

That stage is not specified or authorized here. Choosing its exact model-run
inventory now would outrun the available evidence and risk turning the consumed
validation result into a tuning set. If artifact-only Stage A confirms `F5`, the
next decision is either a separately preregistered train-only diagnostic or a
fresh development-person design. It is not a Loop 26 rerun.

## Authorization Boundary

This planning pass authorizes nothing. Every `authorized_now` field in the
machine contract is false. No implementation, CLI, generated diagnostic report,
authorization request, train-array read, cache read, target read, model run,
training run, new participant, acquisition, download, S25 operation, language
model, RW3, stream, device, or hardware operation exists.

The next permitted milestone is to commit and remotely qualify the exact
artifact-only contract. Only then may a separate authorization packet bind that
green commit and ask for one Stage A execution.

## Claim Boundary

Engineering capability proposed: a hash-bound diagnostic tree can make the
consumed negative result mechanically classifiable without reopening protected
data.

Scientific claim not established: this research does not prove why the model
failed, that S21 lacks decodable neural information, that CTC or preprocessing
is the sole cause, or that another model, participant, modality, real-time path,
or home device will succeed.
