# Loop 28 Primary-Source Research And Transfer Decision Note

Date: 2026-07-12

Status: **Planning research complete; no preregistration, data access, model
operation, calibration, or final evaluation is authorized**

Machine boundary: `registries/loop28_research_boundary.v0.json`

Roadmap row: `registries/next_20_loops.v0.json` Loop 28

## Decision Summary

Loop 28 remains `Not Started`. This pass resolves the transfer question that
Loop 27 needs before its selected S25 candidate can ever become a defensible
preregistration:

> What exact claim can a final-only recording from one unseen person test, and
> what result would count without fitting anything to that person?

The answer is narrower and more useful than a generic transfer experiment:

1. S25 session 2 block 2 is eligible only for a future **strict unseen-person
   zero-shot** test of one canonical person under the same nominal MEG system
   and prompted-typing task.
2. S25 must contribute zero training, validation, calibration, threshold,
   normalization-fit, model-selection, or unlabeled corpus-adaptation rows.
3. Every eligible performed row is final-only, with a minimum floor of 48
   unique performed rows. The floor is a retention check, not a power claim.
4. A practical pass requires at least 0.05 absolute macro sentence-CER
   improvement over the frozen source-train-only no-signal prior, a
   preregistered one-sided paired randomization result at `p <= 0.05`, and a
   strict win over every frozen signal-corruption control.
5. Exact ties, unavailable required fields, access violations, hash drift,
   control failures, or resource-cap failures produce `park`.
6. Any use of S25 labels, target text, target-wide signal statistics, or
   parameter updates before final scoring changes the claim to calibrated or
   transductive transfer. It cannot be called zero-shot.
7. A calibrated-transfer curve requires a different physically separated
   design. The selected final-only S25 block cannot answer both questions.

This rule completes one planning dependency for Loop 27. It does not satisfy
Loop 25, create the Loop 26 source model, qualify S25 channels, authorize an
acquisition, or prepare a Loop 28 experiment packet.

## Measured Research Boundary

```text
public-source web research operations:    10
GitHub metadata API operations:             1
remote code or data payload downloads:      0
S25 local payload metadata checks:           0
S25 local MAT payload hashes:                0
S25 FIF header or signal reads:              0
S25 MAT content or target reads:             0
consumed S7/S21 evidence reads:              0
model or checkpoint runs:                    0
training or parameter updates:               0
calibration or final evaluations:            0
RW3, stream, board, or device operations:    0
CPU threads / workers:                     1 / 1
```

Only committed project metadata and public primary sources were inspected.
The external browser tool does not expose meaningful process-level peak RSS or
end-to-end research latency, so those fields remain explicitly unavailable
rather than invented.

## Finding 1: Asynchronous Is Not Yet Causal Or Low-Latency

Brain2Qwerty v2 is now the correct scientific reference for continuous
sentence input. Its public paper and implementation replace keystroke-aligned
windows with a continuous sentence recording and a CTC encoder. That is a major
interface advance.

It is not, however, an online low-latency decoder. The paper's limitations
section explicitly says the architecture is noncausal, consumes an entire
sentence, and cannot display a word before the sentence ends. The public model
also exposes no streaming state or causal attention mask. Therefore:

```text
continuous sentence input != causal inference
asynchronous decoding     != incremental text
recorded in real time      != end-to-end latency measured
```

This distinction matters to NeuroDecodeKit because its local goal is harder
than merely accepting an unsegmented recording: the preprocessing, encoder,
endpointing, decoder, and display path must eventually expose bounded right
context and measured latency.

Primary sources:

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- official project page:
  https://facebookresearch.github.io/brain2qwerty/
- official code at the reviewed commit:
  https://github.com/facebookresearch/brain2qwerty/tree/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2

## Finding 2: V2 Does Not Establish Strict Unseen-Person Zero-Shot Decoding

The v2 paper provides valuable transfer evidence, but the claim must be named
correctly:

- the primary joint model trains on all nine participants and uses a
  participant-index-conditioned affine layer after geometry-aware spatial
  channel merging;
- reported cross-subject means average per-participant results, but do not by
  themselves mean that the evaluated participant was absent from training;
- the leave-one-out experiment excludes the target participant during
  pretraining, then finetunes on that participant with the Conformer frozen;
- the paper reports that this target-participant finetuning closes much of the
  gap to joint training;
- the public EnglishBCBL v2 dataset remains embargoed, even though the code and
  preprint are public.

That leave-one-out plus finetune result is **supervised calibrated transfer**.
It is not strict zero-shot transfer. The v2 authors themselves identify
cross-subject transfer and self-supervised pretraining as future priorities
because substantial inter-participant variability remains.

This is precisely why S25 is scientifically useful: it can test a smaller but
currently missing question without pretending to reproduce the v2 system.

## Transfer Taxonomy

The word "transfer" is too broad to be a proof label. Loop 28 uses four primary
levels:

| ID | Evidence level | Target-person information allowed before final scoring | Claim boundary |
|---|---|---|---|
| T0 | Same-session held-out text | Source-person training rows from the same session; no held-out text leakage | Generalization to held-out text for that person/session only |
| T1 | Same-person cross-session | Earlier-session labels and signals; no evaluation-session fit | Session transfer for that person only |
| T2 | Unseen-person strict zero-shot | Deterministic header/geometry compatibility only; no target corpus signal statistics, labels, targets, or updates | Zero-shot transfer to one unseen canonical person |
| T3 | Unseen-person calibrated | A preregistered, physically separate target calibration partition | Calibrated transfer at the exact reported budget |

Unlabeled target-corpus adaptation is tracked separately as **transductive
zero-label adaptation**. It may be useful, but it is not T2 strict zero-shot
because the target distribution influenced the system before final scoring.

The current local evidence maps as follows:

| Evidence | Level | Status |
|---|---|---|
| S21 session 1 | T0 candidate | Source test consumed; no fresh claim |
| S21 session 2 | T1 | Consumed negative result; worse than no-signal prior |
| S25 session 2 block 2 | T2 candidate | Metadata-only selection; unopened and unauthorized |
| Calibrated unseen person | T3 | No physically separated design selected |

## Why S25 Must Stay Final-Only

Loop 27 selected one S25 block because it is the smallest strict clean
same-modality candidate under the 1 GiB cap. Its scientific value is
independence from the observed S21 canonical person. Splitting this small block
into calibration, selection, and final pieces would weaken the only fresh
test, introduce new choices, and make the zero-shot claim unavailable.

The future S25 allocation therefore remains:

```text
candidate training rows:             0
candidate validation rows:           0
candidate calibration rows:          0
candidate target-wide fit rows:       0
candidate final rows:                 all eligible performed unique rows
minimum final rows:                  48
```

Header fields may be used only to prove deterministic sensor compatibility.
No target-wide median, IQR, covariance, alignment, normalization, subject
embedding, affine layer, adapter, prompt, threshold, or confidence parameter
may be fitted from S25. Per-item causal state may update only from samples that
have already arrived within that same item under a separately proven Loop 25
contract.

## Final-Only Estimand

The future primary effect is:

```text
delta_macro_CER =
    mean(sentence_CER(source_train_only_prior))
  - mean(sentence_CER(frozen_zero_shot_model))
```

Positive values favor the neural model. Sentence CER is computed independently
for each final sentence, then averaged so one long sentence cannot dominate the
primary effect. Corpus CER, WER, exact-sequence accuracy, edit counts, and
wins/ties/losses remain secondary descriptive metrics.

The practical minimum is frozen at the research level as:

```text
delta_macro_CER >= 0.05
```

This matches the Loop 26 planning recommendation and prevents a tiny favorable
fluctuation from being promoted merely because it is positive. It is not a
clinical threshold, a population effect size, or a prospective power result.

## One-Time Statistical Rule

Exact enumeration of every sign assignment is practical for Loop 26's six
source-validation sentences (`2**6 = 64`) but not for at least 48 S25 final
sentences. The future Loop 28 packet should therefore bind:

```text
paired unit:                    unique final sentence
statistic:                      mean paired sentence-CER difference
alternative:                    frozen model better than prior
random sign assignments:       65,535
observed assignment included:  yes
total reference statistics:    65,536
randomization seed:             derived from frozen contract hash
decision p-value:               <= 0.05
```

Predictions for the model, prior, and every corruption control must be written
and hash-frozen before target text opens. The one-time scorer then opens the
final targets once, computes every paired metric in one pass, writes one
append-only report, and permanently consumes the candidate.

The randomization result characterizes stability across this fixed sentence
set under its paired exchangeability assumption. It is not biological
replication and cannot turn one person into a population claim. A paired
bootstrap interval may be included descriptively, but cannot override the
effect, control, or randomization gates.

Methodological sources:

- cross-subject MEG as a domain-shift problem:
  https://arxiv.org/abs/1404.4175
- trustworthy BCI benchmark and identical evaluation contexts:
  https://arxiv.org/abs/1805.06427
- brain-decoder cross-validation caveats:
  https://pubmed.ncbi.nlm.nih.gov/27989847/
- classifier permutation tests:
  https://www.jmlr.org/papers/v11/ojala10a.html

## Required Controls

The future final scorer must compare predictions on exactly the same final
rows and target strings:

1. Source-train-only no-signal sentence prior.
2. Frozen checkpoint with valid S25 signal replaced by exact zeros.
3. Frozen channel-name-hash derangement preserving lengths and values.
4. Frozen nonwrapping, zero-filled time displacement preserving item length.

The strict gate is conjunctive. The frozen model must beat the no-signal prior
by the practical and randomization thresholds **and** have strictly lower macro
CER than each corruption control. A control tie fails. Secondary control
comparisons are falsification checks rather than four extra claims, so the
report must not publish them as independently selected hypothesis tests.

## Exact Decision Table

| Condition | Decision |
|---|---|
| Fewer than 48 eligible unique performed rows | Park before model or final-target open |
| Any candidate-side fit, calibration, or corpus adaptation | Zero-shot claim invalid; park T2 |
| Model/prior/control predictions not frozen before target open | Park |
| `delta_macro_CER < 0.05` | Park |
| One-sided paired randomization `p > 0.05` | Park |
| Candidate ties or loses to any required corruption control | Park |
| Hash, identity, split, access, privacy, or resource violation | Park |
| All gates pass | Support T2 for this one S25 person/session/task only |

No failure authorizes a restart, threshold change, new seed, calibration pass,
or automatic substitution of S24, S18, or another candidate.

## Identity And Text Claims Stay Separate

S25 is provisionally an unseen canonical person relative to the S5/S10/S21
alias group. That supports a future person-transfer question. It says nothing
about sentence novelty.

Before final scoring, a separately authorized redacted audit may disclose only
the count of candidate sentence hashes that overlap source train, validation,
or consumed test partitions. The resulting labels are:

- overlap count `0`: unseen-person and unseen-text candidate;
- overlap count `>0`: unseen-person with familiar-text exposure disclosed;
- overlap unavailable: unseen-person only, text novelty unavailable.

Plaintext may not be emitted by the audit. No sentence may be removed because
it looks difficult or overlaps; the overlap result changes the claim label, not
the final membership after the preregistered eligibility rules run.

## Calibrated Transfer Is A Separate Future Design

Brain2Qwerty v2 provides a strong reason to study calibration: leave-one-out
pretraining followed by target-participant finetuning improves performance.
It also provides the reason not to blur the evidence. A future T3 calibration
curve must have:

- a target person absent from source fitting;
- physically separate calibration and final recordings or blocks;
- nested, predeclared calibration budgets;
- one fixed adapter family and optimizer selected without final data;
- a zero-shot prediction from the same source checkpoint;
- the same final rows for zero-shot and every calibrated budget;
- calibration examples, seconds, runtime, RSS, and parameter updates reported;
- no relabeling of calibrated performance as zero-shot.

No such candidate or acquisition is selected here. S25 block 2 remains T2
final-only. Loop 32 may later implement T3 only after a new metadata and
authorization chain.

## Future Access Sequence

1. Loop 25 closes with a compatible causal preprocessing result.
2. Loop 26 preregisters, is separately authorized, and freezes one source model
   plus every control before any S25 content opens.
3. Loop 27 binds the exact S25 files, target-isolation code, header protocol,
   this T2 rule, resources, and staged access permissions.
4. Separate authorization is recorded before acquisition or local MAT hashing.
5. Header compatibility is tested without signal samples.
6. Redacted eligibility and overlap audits run without plaintext output.
7. If every pre-open gate passes, model/prior/control predictions are produced
   without opening final target text and are hash-frozen.
8. The final scorer opens all eligible target strings once, emits one report,
   and marks S25 consumed regardless of outcome.
9. The exact result closes as support or park; no tuning or backup opens.

## Resource Recommendation

```text
current downloaded payload:            0 bytes
current planning-artifact cap:         8 MiB

future CPU threads / workers:          1 / 1
future model-size ceiling:             frozen Loop 26 checkpoint
future language-model runs:            0
future target-person parameter updates: 0
future generated-artifact cap:        32 MiB
future peak RSS cap:                    1 GiB
future random sign assignments:       65,535 plus observed
future automatic backup candidates:    0
```

The final runtime cap cannot be frozen until Loop 26 produces a measured
checkpoint runtime. It must be set before S25 signal or targets open and must
include the model, prior, all controls, scoring, and report generation.

## Remaining Preregistration Blockers

Loop 28 planning research is complete, but experiment preregistration remains
blocked by:

1. A compatible measured Loop 25 result.
2. A frozen and successful Loop 26 source checkpoint and control package.
3. A Loop 27 staged acquisition/header/signal/target authorization chain.
4. Exact S25 sensor compatibility and performed-row eligibility.
5. Implemented, tested, and hash-bound redacted overlap and target isolation.
6. A frozen Loop 26-derived runtime cap and all prediction/report hashes.
7. A separate exact Loop 28 authorization sentence.

## Closeout Decision

```text
loop28_planning_research_complete_strict_zero_shot_rule_ready_execution_blocked
```

This note adds the final-only transfer rule needed for future S25
preregistration. It does not establish an acquired or compatible holdout,
causal preprocessing, a source model, neural information, transfer, unseen
text, population generalization, calibrated adaptation, Brain2Qwerty v2
equivalence, low-latency text, portable sensing, at-home use, assistive
benefit, diagnosis, or clinical utility.
