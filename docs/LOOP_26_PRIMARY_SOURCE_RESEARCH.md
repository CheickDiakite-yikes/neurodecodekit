# Loop 26 Primary-Source Research And Identifiability Note

Date: 2026-07-12

Status: **Planning research complete; no preregistration or execution is authorized**

Machine boundary: `registries/loop26_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 26

## Decision Summary

Loop 26 remains `Not Started`. This pass answers the planning question that
must be settled before a defensible experiment can be preregistered:

> What can six reserved source-validation sentences establish, and what is the
> smallest causal text model that is meaningfully comparable with the existing
> real baseline?

The answer is deliberately narrow:

1. Six sentence instances from one person and one session can support a
   validation-only engineering gate for that exact source. They cannot support
   a subject, population, transfer, device, or clinical claim.
2. The existing 2,908-parameter `TinySentenceCTC` is the right size ceiling,
   but it is explicitly noncausal because its kernel-3 convolution uses
   symmetric padding.
3. The existing 1,130-parameter causal encoder is not a real-text candidate. It
   is bound to a synthetic motif fixture and frame labels.
4. The lowest-complexity candidate is therefore a **research recommendation**:
   preserve the 2,908 parameters and all pointwise layers, but replace the
   symmetric temporal padding with exactly two samples of left padding.
5. A 2,884-parameter one-layer linear CTC is a nearly parameter-matched signal
   comparator. It is only 24 parameters, or about 0.83%, smaller.
6. No model, control transform, practical margin, seed, optimizer schedule, or
   access sequence is frozen by this note. Those belong in a later hash-bound
   preregistration after Loop 25 closes.

This is useful progress, but it is not a loophole around Loop 25. Loop 26
depends on a completed causal-preprocessing decision and a separate explicit
authorization for real-cache reads, targets, training, model execution, and
the six-row validation open.

## Measured Research Boundary

```text
raw signal reads:                         0
real-cache content reads:                 0
target, label, or sentence reads:         0
validation prediction opens:              0
source-test opens:                        0
session-2 opens:                          0
model or checkpoint runs:                 0
training runs or parameter updates:       0
Loop 25 numerical operations:             0
RW3, stream, board, or device operations: 0
new real-data downloads:                  0
```

Only committed source, committed reports, compact machine registries, and
public primary sources were inspected. Real NPZ members and raw recordings
were not opened.

## Local Evidence Inventory

The committed Loop 14 and Loop 15 reports establish the following boundary:

| Surface | Current evidence | Loop 26 treatment |
|---|---|---|
| Source split | 55 train / 6 validation / 5 test sentence rows | Bind exact protocol and membership hashes before any future cache open |
| Preprocessing fit | Robust scaler fitted on 55 train rows only | Preserve; no validation-fit transform |
| Source validation | Reserved and unused for restart or hyperparameter selection | One future validation-only open, if separately authorized |
| Source test | Consumed in the Loop 14 near-null comparison | Frozen; no reopen |
| Session 2 | Consumed in the Loop 15 harmful cross-session comparison | Frozen; no reuse or tuning |
| Existing real model | 2,908 parameters, width 16, 60 epochs, one initialization | Size ceiling only; implementation is noncausal |
| Existing causal model | 1,130 parameters over synthetic motifs | Mechanics evidence only; not a text decoder |

The six validation rows have already participated in metadata, split, and
train-only-scaling contracts. "Reserved" therefore means not used for model
selection or predictive evaluation; it does not mean that their existence or
membership is secret.

## Finding 1: Brain2Qwerty v2 Is A Scientific Reference, Not A Local Template

The official Brain2Qwerty v2 implementation uses a large Conv + Conformer
encoder, CTC, a word-level contrastive aligner, and a LoRA-adapted language
model. Its published configuration uses 1,500 hidden convolutional channels, a
1,024-dimensional four-layer Conformer, 16 data workers, mixed precision, and
GPU-oriented training:

- paper: https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- implementation: https://github.com/facebookresearch/brain2qwerty/tree/main/brain2qwerty_v2
- experiment configuration: https://github.com/facebookresearch/brain2qwerty/blob/main/brain2qwerty_v2/config/xp_config.py
- model configuration: https://github.com/facebookresearch/brain2qwerty/blob/main/brain2qwerty_v2/config/model_config.py

The v2 paper explicitly states that the current model consumes an entire
sentence and is not causal. It also reports that fluent LLM output can improve
WER while worsening CER, and that removing MEG-derived Neuro Tokens degrades
all reported metrics. Loop 26 should therefore answer only the upstream,
language-model-free question: does a tiny causal signal path beat honest
signal-free and corrupted-signal controls?

Copying the released v2 architecture would violate the local CPU/storage goal
and would not solve causality. The purpose of the official source trace is to
preserve its evaluation lessons while shrinking the engineering surface.

## Finding 2: The Existing Tiny Real Model Needs One Causal Repair

The current real baseline is:

```text
Conv1d(102 -> 16, kernel 1)
GELU
Conv1d(16 -> 16, kernel 3, symmetric padding 1)
GELU
Conv1d(16 -> 28, kernel 1)
CTC greedy decode
```

Its exact parameter count is:

```text
102*16*1 + 16 = 1,648
 16*16*3 + 16 =   784
 16*28*1 + 28 =   476
------------------------
total                 = 2,908
```

Symmetric padding gives the kernel-3 layer one future 100 Hz sample. The
recommended causal variant uses `left_pad=2`, `right_pad=0`, and `padding=0`
inside the convolution. It preserves output length, parameters, 100 Hz output
cadence, and greedy CTC compatibility while reducing model right context to
zero. Its mutable temporal state is two hidden frames:

```text
2 frames * 16 hidden values * 4 float32 bytes = 128 bytes
```

This is a design calculation, not a model implementation or measured replay
result. A later preregistration must bind the exact tensor semantics and prove
chunk-equivalent output before real validation.

## Finding 3: A Fair Small Comparator Is Available

A one-layer signal comparator can use:

```text
Conv1d(102 -> 28, kernel 1)
```

Its parameter count is `102*28 + 28 = 2,884`, only 24 below the proposed
causal candidate. Training it with the same CTC loss, rows, batch schedule,
seed policy, and CPU cap would separate the value of the temporal nonlinear
path from mere parameter budget.

This comparator still consumes neural signal. It is distinct from the
required no-signal prior and zero-signal inference controls.

## Finding 4: Six Rows Impose A Hard Inferential Ceiling

SciPy's exact paired `permutation_test` exchanges the two observations inside
each pair. With six pairs, the complete null has exactly:

```text
2**6 = 64 assignments
minimum attainable one-sided p = 1/64 = 0.015625
minimum attainable two-sided p = 2/64 = 0.03125
```

If one paired difference is exactly zero and the effective sign count falls to
five, the minimum two-sided resolution is `2/32 = 0.0625`. This is why a
future pass cannot be defined by a smooth-looking bootstrap interval alone.

Primary statistical references:

- exact paired permutations: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- paired bootstrap mechanics: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- classifier label permutations: https://jmlr.org/beta/papers/v11/ojala10a.html
- small-sample decoding uncertainty: https://pubmed.ncbi.nlm.nih.gov/28655633/

The six observations are unique sentence instances, not six independent
people. Any future exact p-value describes only those paired sentence errors
under its exchangeability assumption. It cannot promote a one-person result
into biological replication.

## Finding 5: Corruption Controls Need Different Interpretations

| Control | Question | Required future rule |
|---|---|---|
| Train-only sentence-target derangement | Can the same training pipeline fit useful signal/target structure after correspondence is destroyed? | Freeze one semantic-ID-derived derangement before targets open; never search permutations on validation |
| Zero validation signal | Does the trained model emit a learned text prior without input information? | Same checkpoint and lengths; replace valid samples with exact zero; keep padding exact |
| No-signal sentence prior | Does signal beat a target-only baseline? | Fit only from source-train targets; evaluate the same six rows |
| Channel derangement | Does sensor identity matter? | Freeze channel-name-hash derangements before signal arrays open; preserve values, lengths, and padding |
| Time displacement | Is output tied to registered timing? | Freeze non-wrapping, zero-filled offsets and report boundary loss; treat as a falsification control, not an exact null test |
| Linear CTC | Does the nonlinear temporal path help beyond nearly matched capacity? | Same rows, loss, schedule, and one initialization; 2,884 parameters |

Naively permuting time points is not a valid exact test for autocorrelated
signals. Permutation validity depends on exchangeability, and time-series
dependence breaks that assumption in general:
https://onlinelibrary.wiley.com/doi/10.1111/jtsa.12638

For that reason, future time and channel corruptions are engineering controls.
The exact paired sentence test applies to model-versus-control error vectors,
not to shuffled signal samples as though they were independent.

## Recommended Future Estimands

These are research recommendations, not frozen acceptance thresholds:

1. Primary effect: macro mean per-sentence CER difference,
   `control CER - candidate CER`, on the six validation rows.
2. Primary comparison: candidate versus same-split no-signal prior.
3. Required directional controls: zero signal, target derangement, frozen time
   displacement, frozen channel derangement, and the linear CTC comparator.
4. Exact uncertainty: enumerate all 64 paired sign assignments for the primary
   six-item contrast and disclose the complete null distribution.
5. Descriptive uncertainty: paired bootstrap over sentence indices may be
   reported, but it cannot replace the exact enumeration or the six-item table.
6. Secondary metrics: corpus CER, exact sentence count, WER, blank fraction,
   candidate/control wins-ties-losses, and per-item edit counts.
7. Practical margin candidate: at least 0.05 absolute macro CER improvement
   over the prior. This number is not frozen and must be justified or changed
   before preregistration, never after validation opens.

Requiring the candidate to win on every validation sentence would be a very
strict but transparent route to the minimum two-sided exact p-value. Whether
that becomes the gate is a future decision; this note does not choose it.

## What Six Validation Rows Can And Cannot Establish

| Claim | Availability after a hypothetical clean pass |
|---|---|
| Exact pipeline mechanics and zero model right context | Available only after separate synthetic replay proof |
| Lower CER than controls on these six reserved sentences | Potentially available |
| Signal dependence for this one S21 session-1 validation slice | Potentially available, with all corruption controls passing |
| Source-test performance | Unavailable; the five rows are consumed and frozen |
| Cross-session performance | Unavailable; session 2 is consumed and already negative |
| Unseen-person or population generalization | Unavailable; one canonical person |
| Brain2Qwerty v2 equivalence | Unavailable; different data, architecture, scale, and causal objective |
| Real-time end-to-end text latency | Unavailable; preprocessing/model mechanics are not a live system |
| EEG, OPM-MEG, wearable, or home-device performance | Unavailable |
| Thought, imagined-speech, assistive, diagnostic, or clinical capability | Unavailable |

## Preregistration Prerequisites

Do not create a Loop 26 experiment authorization request until all of these are
resolved in one hash-bound contract:

1. Loop 25 closes with a result compatible with the exact Loop 26 input path.
2. The source cache, split report, scaler, protocol, membership, channel order,
   and physical file hashes are named without opening protected arrays.
3. The exact causal model tensor contract and 2,908-parameter count are frozen.
4. The linear comparator, prior, zero-signal path, target derangement, time
   offsets, and channel derangements are frozen.
5. One model seed, one initialization, optimizer, epoch count, batch size, CTC
   vocabulary, decode rule, and no-restart policy are frozen.
6. The primary estimand, exact test, practical margin, all-control rule, and
   tie/failure behavior are frozen.
7. The physical access order opens train before validation and never opens
   source test or session 2.
8. Runtime, RSS, working-memory, artifact, and access-ledger caps are frozen.
9. The exact authorization sentence explicitly names real-cache, targets,
   training, model runs, and one validation open while excluding test,
   session 2, downloads, larger models, language models, RW3, and devices.

## Resource Recommendation

Retain the roadmap ceiling unless the future preregistration makes it lower:

```text
CPU threads/workers:       1 / 1
model-size ceiling:        2,908 trainable parameters
future training wall cap:  20 minutes total across candidate and controls
future peak RSS cap:       1 GiB
future generated cap:      32 MiB
new real-data downloads:   0
source-test/session-2 use: 0
```

The future 20-minute cap must include every candidate and control training run,
not reset per model.

## Closeout Decision

```text
loop26_planning_research_complete_preregistration_waits_for_loop25
```

This note adds a falsifiable design and an honest identifiability boundary. It
does not authorize or establish a causal encoder, neural information, decoding
advantage, validation performance, source-test performance, real-time text,
portable hardware, at-home use, assistive efficacy, or clinical utility.
