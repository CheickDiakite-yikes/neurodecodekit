# Loop 31 Primary-Source Research And Neural-Attribution Firewall

Date: 2026-07-12

Status: **Planning research complete; experiment `Not Started`**

Machine boundary: `registries/loop31_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 31

## Decision Summary

Loop 31 asks the question that every apparently successful decoder must answer:

> Did the predictive improvement come from the measured sensor signal, or from
> language regularities, timing, prompts, sentence lists, broken split logic,
> or another shortcut?

This research pass defines a strict attribution firewall without opening any
protected evidence or running any model.

1. The future local encoder study has ten named conditions. Seven corrupted or
   signal-free controls are unconditionally required, one context-only control
   becomes required if a prompt or sentence list is exposed, and one linear
   signal model is an architecture diagnostic rather than a claim blocker.
2. A separate five-condition language-model matrix isolates language-prior
   gain and incremental Neuro Token gain. It is contingent because no
   authorized local LLM, Brain2Qwerty v2 checkpoint, v2 embedding, or v2 data
   exists.
3. Every condition must predict the same validation rows before target text is
   opened. Predictions, configurations, transforms, and payloads are hashed
   before one scorer opens all targets once.
4. The six source-validation sentences permit only 64 sign assignments when
   all paired effects are nonzero. The future overall claim is conjunctive: all
   applicable controls must pass an exact one-sided component test and the
   primary no-signal practical margin.
5. Even a clean pass can establish only **sensor-signal dependence** for one
   person, session, task, split, and model. It cannot establish brain-specific
   neural origin until Loop 35 excludes ocular, muscular, motion, environmental,
   prompt, and action shortcuts.

Loop 31 depends on an actual Loop 26 result, and Loop 26 remains blocked on
Loop 25 plus separate authorization. This note is not a preregistration or an
authorization packet.

## Measured Research Boundary

```text
raw signal reads:                              0
real-cache content reads:                      0
target, label, or sentence reads:              0
source-validation prediction opens:            0
source-test opens:                              0
session-2 opens:                                0
checkpoint or model runs:                      0
training runs or parameter updates:            0
language-model or Neuro Token runs:             0
external model or weight downloads:            0
new real-data downloads:                        0
S20 or S25 operations:                          0
RW3, stream, device, or hardware operations:    0
```

The pass inspected committed source and reports, public primary sources, and
the official Brain2Qwerty repository at commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0`. It used 16 high-level public
network research operations, including eight GitHub API requests. The tools do
not expose exact transferred research bytes, so that value is unavailable
rather than guessed. No external source was written into the repository.

## The Existing Evidence Is Negative, Not Empty

The project already has two real comparisons against no-signal baselines. They
are scientifically useful because both prevent a later interface or language
model from laundering a weak signal path into an impressive sentence.

| Evidence | Neural path | No-signal path | Exact result | Treatment |
|---|---:|---:|---|---|
| S21 session-2 same-person MEG, 63 sentences | corpus CER `0.917949` | corpus CER `0.775458` | neural minus prior `+0.142491`; wins/ties/losses `3/2/58` | consumed, harmful direction |
| S7 within-session EEG, 1,100 key events | accuracy `0.009091` | accuracy `0.122727` | neural minus prior `-0.113636`; wins/ties/losses `9/957/134` | consumed, harmful direction |

Neither result says neural decoding is impossible. Both say the tested model
failed to beat information available without signal. Session 2 and S7 must not
be reopened or tuned against.

Loop 18 also proved that unlike cohorts cannot be merged into one leaderboard.
Loop 26 then identified six unused S21 session-1 validation sentences and a
2,908-parameter causal candidate recommendation, but did not create or run it.
Loop 31 therefore designs an attribution gate around that future candidate
rather than inventing a result.

## Finding 1: Prediction Is Not Attribution

A final prediction can improve for several incompatible reasons:

- the measured sensor signal contains task-linked information;
- input duration or padding reveals sentence length;
- a prompt or closed candidate list narrows the answer space;
- a language model repairs plausible text without using the signal;
- a split leak exposes repeated or similar sentences;
- the model exploits eye, muscle, motion, keyboard, or environmental artifacts;
- the evaluation code treats missing conditions as zero rather than unavailable.

Snoek, Miletić, and Scholte show that decoding performance is ambiguous under
confounding and that confound regression itself can become biased if it is not
performed inside the cross-validation routine:
https://doi.org/10.1016/j.neuroimage.2018.09.074

Görgen et al.'s Same Analysis Approach recommends applying the actual analysis
to design variables, simulated confounds, null data, and controls rather than
trusting one headline model:
https://arxiv.org/abs/1703.06670

The consequence here is simple: every attribution condition uses the same row
membership, target normalization, scoring code, and condition ledger. A
different analysis pipeline for the control would answer a different question.

## Finding 2: Brain2Qwerty Separates Language Gain From Signal Gain

Brain2Qwerty v1 trains a convolutional encoder, a sentence-level transformer,
and a pretrained 9-gram language model. Its published ablations separately
report convolution-only, convolution-plus-transformer, and final
language-model-assisted output:
https://www.nature.com/articles/s41593-026-02303-2

That progression demonstrates architecture and language gains. It does not
make the language-model increment a neural increment. The task is also
keypress-aligned prompted typing, with 500-ms windows around known keypresses,
so timing and motor information remain central to the evidence.

Brain2Qwerty v2 makes a more targeted comparison. Its LLM receives CTC text and
MEG-derived word embeddings called Neuro Tokens. Appendix Figure S4 compares
the same Qwen3-0.6B backbone with and without the Neuro Tokens:

| Metric | CTC text plus LLM, no Neuro Tokens | CTC text plus Neuro Tokens and LLM | Absolute change |
|---|---:|---:|---:|
| CER | `0.38` | `0.34` | `-0.04` |
| WER | `0.49` | `0.43` | `-0.06` |
| SemER | `0.067` | `0.064` | `-0.003` |

Primary paper:
https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf

The inspected official module builds one LLM prefix from CTC text plus the
projected neural words. That source trace is pinned to commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0`:
https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2

This gives Loop 31 an exact interpretation:

- encoder-only versus CTC-text-plus-LLM measures language-prior gain;
- CTC-text-plus-LLM versus the same LLM plus Neuro Tokens measures incremental
  token gain conditional on the CTC text;
- neither contrast alone measures total neural contribution;
- no local v2 embedding, checkpoint, data, or LLM result can be assumed.

In short, a Neuro Token drop contrast does not prove total neural contribution.

## Finding 3: The Encoder Matrix Needs Ten Named Conditions

The future encoder matrix is fixed at the research-design level below. Exact
seeds, transforms, thresholds, and model hashes remain for a later
preregistration.

| ID | Condition | Question | Claim role |
|---|---|---|---|
| `L31-E00` | full registered signal and candidate | What does the candidate predict? | reference |
| `L31-E01` | train-only no-signal sentence prior | Does signal beat target frequency alone? | required primary comparator |
| `L31-E02` | exact-zero valid signal, same checkpoint | What does the checkpoint emit without input information? | required, with OOD warning |
| `L31-E03` | whole validation rows deranged by item ID | Does each prediction depend on its own signal row? | required |
| `L31-E04` | channel-name-hash derangement | Does registered sensor identity matter? | required falsification |
| `L31-E05` | nonwrapping zero-filled time displacement | Does registered temporal position matter? | required falsification |
| `L31-E06` | timing-only train-fit baseline | Can nonneural runtime metadata explain the result? | required |
| `L31-E07` | declared prompt or sentence-list only | Can exposed context explain the result? | required if context exists |
| `L31-E08` | train signal-target pairing derangement | Does the same training budget work after correspondence is destroyed? | required |
| `L31-E09` | 2,884-parameter linear signal CTC | Is the nonlinear temporal path useful beyond similar capacity? | diagnostic, not attribution blocker |

Ojala and Garriga distinguish label permutation from restricted feature
permutation and show that these controls answer different questions:
https://www.jmlr.org/papers/v11/ojala10a.html

The controls therefore cannot be collapsed into one generic "shuffle."
Evaluation-row derangement preserves each signal row and breaks item
correspondence. Train-pairing derangement creates a separately trained model
with broken train correspondence. Channel and time transforms probe registered
structure but are not exact neural-null distributions.

Zero signal is also an out-of-distribution input. If the model degrades under
zeros, that shows input dependence, not useful neural information by itself.
The required conclusion comes only from all applicable controls together.

## Finding 4: Timing And Context Need An Explicit Threat Model

The timing-only condition may use only metadata the candidate legitimately has
at inference:

```text
source valid length in samples
source padding mask
source sampling rate
relative sample timestamps available to the candidate
```

It may not use key identities, key trigger codes, typed text, target text, MAT
responses, evaluation target frequencies, or target character count unless
that count is genuinely derivable from the same runtime input. This matters
because response duration and padding can reveal sentence length even when
signal values are absent.

The SpanishBCBL prompt is presented to the participant, not to the decoder. A
closed sentence list or prompt must therefore remain unavailable to the model.
If any future system does expose that context, `L31-E07` becomes mandatory and
the claim must name the exposure. "No context control" is not equivalent to a
zero context effect; absence needs machine evidence.

## Finding 5: Six Rows Make The Gate Exact And Severe

Loop 26 reserves six unique validation sentence instances. With nonzero paired
differences, exact sign-flip enumeration has:

```text
six nonzero pairs: 2**6 = 64 assignments
minimum one-sided p: 1/64 = 0.015625
minimum two-sided p: 2/64 = 0.03125

five nonzero pairs: 2**5 = 32 assignments
minimum one-sided p: 1/32 = 0.03125

four nonzero pairs: 2**4 = 16 assignments
minimum one-sided p: 1/16 = 0.0625
```

At alpha `0.05`, two zero paired differences make even the smallest possible
one-sided p-value too large. Each applicable component is therefore allowed at
most one exact tie if it is to pass the statistical recommendation. Every one
of the six per-item effects must be printed.

The overall claim is an intersection-union test: full signal must pass every
applicable required component in the registered direction. Under the
intersection-union principle, the conjunctive overall claim does not need a
Bonferroni-style penalty because success requires all component nulls to be
rejected rather than selecting any favorable result. It is conservative and
does not permit independent claims about whichever control looks best.

Primary statistical reference:
https://doi.org/10.1214/ss/1032280304

Exact permutation mechanics:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html

Small-sample decoding uncertainty:
https://pubmed.ncbi.nlm.nih.gov/28655633/

The future preregistration must still decide whether to retain the recommended
`0.05` absolute macro-CER margin against the no-signal prior. That margin is not
frozen by this research note.

## Finding 6: The LLM Matrix Is Separate And Contingent

No local LLM or Neuro Token execution exists. If a later authorization creates
one, five conditions are required:

| ID | CTC text | Neuro Tokens | LLM | Purpose |
|---|---:|---:|---:|---|
| `L31-L00` | yes | no | no | encoder-only output |
| `L31-L01` | yes | matched | yes | full language-assisted reference |
| `L31-L02` | yes | dropped | same | language gain without Neuro Tokens |
| `L31-L03` | yes | item-deranged | same | token-to-item correspondence control |
| `L31-L04` | no | no | same | language-prior-only diagnostic |

An incremental Neuro Token result requires `L31-L01` to beat both `L31-L02`
and `L31-L03` with identical CTC text, rows, LLM, decoding, and compute budget.
All predictions must be frozen before targets open. That result would remain
conditional on CTC text and would not prove total neural contribution.

Language models can move CER, WER, and semantic error in different directions.
All metrics remain separate; there is no blended success score. CER is primary
for the local character-decoding gate. WER is secondary only when tokenization
is valid, and SemER remains unavailable unless separately implemented and
authorized.

## Claim Taxonomy

| Claim | Minimum evidence | Available now? |
|---|---|---:|
| `L31-C0` no new result | planning or incomplete gate | yes |
| `L31-C1` same-slice predictive gain | full signal beats the train-only no-signal prior | no |
| `L31-C2` sensor-signal dependence | every applicable encoder control and exact gate passes | no |
| `L31-C3` brain-specific neural contribution | `C2` plus Loop 35 peripheral-only, brain-only, timing-only, and combined controls | no |
| `L31-C4` incremental Neuro Token gain conditional on CTC text | authorized LLM drop and item-derangement matrix passes | no |
| `L31-C5` generalized or deployable neural decoding | fresh people/sessions/devices plus causal end-to-end qualification | no |

This is the central wording rule: Loop 31 alone may eventually support
**sensor-signal dependence**. It may not call that effect brain-specific until
Loop 35 also passes.

## Prediction Freeze And Access Order

A future authorized run must use this order:

1. Close Loop 25 with a result compatible with the Loop 26 signal path.
2. Preregister and separately authorize Loop 26.
3. Produce one frozen Loop 26 candidate without opening source test or session
   2.
4. Freeze every Loop 31 condition, transform, estimand, threshold, seed, budget,
   and configuration hash.
5. Record a separate exact Loop 31 authorization sentence.
6. Open source-train inputs and targets only for registered fits.
7. Produce every six-row validation prediction target-blind and hash it.
8. Open all six validation targets once and score every condition in one pass.
9. Write one append-only report and mark this validation protocol consumed.
10. Close as support or park without restart, threshold changes, or a backup
    open.

The scorer must record per-condition raw/cache/target reads, checkpoint/model
runs, training runs, parameter updates, runtime, peak RSS, input/output bytes,
parameter count, prediction hash, transform hash, warnings, and unavailable
fields. A missing counter or hash is a gate failure.

## Future Gates And Refusals

The machine boundary freezes 18 future requirements and 24 refusal IDs. The
requirements cover dependency, authorization, membership, target-blind
prediction, all conditions, transform freeze, lengths/masks, timing/context,
matched analysis, separate estimands, exact inference, practical effect,
condition ledgers, claim ceiling, LLM contingency, resources, and closeout.

Refusals include:

- any consumed source-test or session-2 access;
- any S20 or S25 access;
- target-informed transforms, fixtures, or best-of-many permutations;
- target opening before all prediction hashes exist;
- hidden prompts, sentence lists, or forbidden timing fields;
- missing conditions, ledgers, hashes, masks, or boundary-loss reports;
- post-validation restarts, threshold changes, or backup opens;
- relabeling language gain as neural gain;
- relabeling a Neuro Token drop as total neural contribution;
- relabeling sensor dependence as brain-specific before Loop 35;
- any generalized, real-time, portable, assistive, diagnostic, or clinical
  claim.

## Resource Recommendation

Retain the existing local envelope:

```text
CPU threads/workers:                    1 / 1
candidate parameter ceiling:            2,908
future total training wall cap:         1,200 sec
future peak RSS cap:                    1 GiB
future generated artifact cap:          32 MiB
future real-data downloads:             0 bytes
future external model/weight downloads: 0 bytes
source-test/session-2 reads:             0 / 0
```

The ten encoder rows do not imply ten training runs. Most corruption conditions
reuse the same checkpoint. Separately trained paths are limited to the full
candidate, train-pairing derangement, timing-only baseline, and linear
comparator, all under the one-thread total cap. The no-signal prior is
dependency-free.

The LLM matrix has no execution budget because it is unavailable and would
require its own model, weight, privacy, license, and authorization decision.

## What This Research Proves

Engineering capability added by this milestone: a machine-checkable design
can now keep signal dependence, language gain, incremental Neuro Token gain,
brain-specific origin, and generalized deployment as distinct evidence claims.

Scientific claim not established by this milestone: no protected validation
row, target, checkpoint, model, language model, or Neuro Token was opened or
run, so there is still no demonstrated neural advantage, sensor-signal
dependence, brain-specific contribution, unseen-person generalization,
portable-device result, or real-time decoding result.
