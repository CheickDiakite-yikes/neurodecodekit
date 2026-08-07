# Foundation-Model Decoder Strategy

**Date:** 2026-08-06  
**Status:** Additive architecture decision; synthetic no-call bridge eligible;
external inference and scientific execution not authorized  
**Selected hosted candidate:** OpenAI `gpt-5.6-sol` through the Responses API  
**Claim ceiling:** Software-interface and experimental-design evidence only

## Decision

NeuroDecodeKit will use a two-layer decoding architecture:

```text
EEG or MEG
  -> causal preprocessing
  -> compact trained sensor adapter
  -> CTC hypotheses plus causal structured neural evidence
  -> frozen foundation-model decoder
  -> text, abstention, and uncertainty record
```

The compact neural model is not the final language model. Its job is to turn
sensor samples into bounded, time-aligned evidence. A pretrained foundation
model supplies language reasoning downstream. The first hosted candidate is
`gpt-5.6-sol`; NeuroDecodeKit is not attempting to train a GPT-scale model.

This decision is additive. It does not amend the frozen Loop 55 neural-effect
gate, which must remain language-model-free so that a language prior cannot
hide whether causal EEG contributes useful information. It also does not
reopen the consumed Loop 31 execution. The existing Loop 31 five-condition
matrix remains research history and motivates the new matched controls.

## Current State

There is no language-model execution in NeuroDecodeKit today:

- OpenAI client dependencies: `0`;
- hosted foundation-model calls: `0`;
- local foundation-model loads: `0`;
- model-weight downloads: `0`;
- LLM fine-tuning runs: `0`;
- protected rows sent to any provider: `0`;
- raw EEG or MEG bytes sent to any provider: `0`.

Codex is used as a research and engineering collaborator. That is separate
from the decoder runtime and cannot be counted as a decoding result.

## Why A Bridge Is Still Required

GPT-5.6 Sol accepts text and image input and returns text. The hosted API does
not expose arbitrary hidden-state or custom embedding-prefix injection. A
continuous NeuroToken array therefore cannot be passed directly into Sol as if
it were one of Sol's native token embeddings.

The hosted path must use a compact structured evidence packet containing only:

- causal CTC n-best hypotheses and scores;
- causal per-frame top-key probabilities and entropy;
- source-relative frame timestamps and availability timestamps;
- explicit missingness, causality, and uncertainty fields.

The packet must not contain raw sensor samples, dense source embeddings,
absolute local paths, subject names, target text, reference text, intended
sentences, performed labels, or post-outcome corrections. A future local
open-weight model may support a learned continuous neural-prefix adapter, but
that is a different transport and requires its own model, license, resource,
privacy, and evidence decision.

## Model Posture

The initial hosted route is intentionally frozen and simple:

| Field | Initial decision |
|---|---|
| Provider | OpenAI |
| Model | `gpt-5.6-sol` |
| Endpoint | Responses API |
| Reasoning effort | `low` candidate baseline; must remain identical across matched arms |
| Output | strict structured text result |
| Fine-tuning | none |
| Tools | none |
| Web or file search | none |
| Conversation memory | none; one item per independent request |
| Raw neural upload | forbidden |

The current GPT-5.6 Sol API surface does not support fine-tuning. More
importantly, fine-tuning is unnecessary for the first question. Prompting and a
strict evidence schema can test whether the frozen model uses the adapter's
information. If later evidence justifies adaptation, NeuroDecodeKit will
choose a separately supported model or a local open-weight decoder rather than
silently changing this candidate.

Primary OpenAI sources:

- model card and modality surface:
  https://developers.openai.com/api/docs/models/gpt-5.6-sol
- model and prompting guidance:
  https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6-sol

## Four Matched Conditions

Every future item must produce four requests with the same model, instruction,
output schema, reasoning effort, decoding settings, and compute budget:

| ID | CTC evidence | Structured neural evidence | Purpose |
|---|---:|---:|---|
| `FM-A00` | no | no | language-prior and abstention control |
| `FM-A01` | matched | no | language repair from CTC text alone |
| `FM-A02` | matched | matched item | full hosted reference |
| `FM-A03` | matched | fixed cyclically deranged item | correspondence control |

The model must not be told which condition it is receiving. Derangement is
fixed before any model output or target opens. Each request is independently
hashable, and all outputs must freeze before any target-bearing score is
delivered.

An incremental structured-neural result requires `FM-A02` to beat both
`FM-A01` and `FM-A03` on the same frozen items. Improvement over `FM-A00` alone
is not neural evidence because CTC text may carry the gain. Fluency, plausibility,
or a lower error rate from Sol alone is a product-language result, not a neural
result.

## Output Contract

Each eventual model response must validate against a strict schema with:

- `decoded_text`: the text supported by supplied evidence;
- `abstained`: whether evidence was insufficient;
- `evidence_used`: one of `none`, `ctc`, or `ctc_and_neural`;
- `unsupported_content_warning`: whether the response may add content not
  supported by the packet.

The prompt instructs the model to abstain instead of inventing names, facts,
or missing words. The application must preserve the raw structured response,
provider model identity, request hash, response hash, token usage, latency,
cost, refusal state, and validation outcome. A successful schema parse is not
a correct decoding result.

## Ordered Stages

### FM-0: Synthetic No-Call Bridge

Eligible now under bounded Tier B development. Build and validate deterministic
synthetic evidence, the four request arms, derangement provenance, canonical
hashes, strict leakage checks, and output caps. Do not contact a provider.

### FM-1: One Synthetic Sol Qualification

Requires a separate explicit network, credential, and spend decision. Use only
new synthetic evidence with no real participant or target content. Measure
request and response bytes, API token usage, latency, cost, refusal state,
schema validity, and deterministic replay limits. This stage cannot establish
decoding accuracy.

### FM-2: Public Development Evidence

Requires a separate exact contract binding a public, licensed development-only
slice, frozen evidence exporter, privacy policy, model settings, request count,
spend cap, and no-target freeze order. It cannot use S20, consumed S21
evaluation rows, S25, or any final-only participant.

### FM-3: Protected Scientific Evaluation

Requires clean upstream signal evidence, a frozen adapter, all four conditions,
a committed and remotely green prediction freeze, and a separate Tier C target
and scientific-claim decision. No tuning may occur after target delivery.

## Synthetic FM-0 Caps

```text
CPU threads/workers:             1 / 1
input JSON maximum:              1 MiB
generated JSON maximum:          1 MiB
wall time maximum:               30 seconds
peak RSS maximum:                256 MiB
network calls:                   0
model calls:                     0
training runs:                   0
real or protected reads:         0
target or label reads:           0
```

FM-0 must fail closed on malformed probabilities, noncausal timestamps,
unknown fields, target-like fields, raw-signal fields, dense embedding fields,
identity leakage, duplicate items, invalid derangement, cap expansion, or a
nonzero access counter.

## Relationship To Existing Work

- **Loop 20:** `NeuroTokenCache v0` remains the continuous internal cache
  contract. The hosted packet is a bounded export view, not a replacement.
- **Loop 31:** preserves the central matched-LLM logic: compare the same LLM
  with matched, absent, and deranged neural evidence.
- **Loop 55:** remains the language-model-free causal EEG effect gate. CML-v0
  is one possible compact sensor adapter, not the final decoder.
- **Loop 57:** is the eventual integration home for causal preprocessing,
  adapter state, evidence export, foundation-model request state, timestamps,
  schedules, resumes, and anomalies. Target-free bridge fixtures precede any
  real replay.

## What Is Proven

Engineering capability established by this decision: NeuroDecodeKit now has a
precise architecture and proof plan for placing GPT-5.6 Sol downstream of a
compact causal neural adapter without treating language fluency as neural
evidence.

Scientific claim not established: no LLM, neural model, real signal, target,
or protected row was run or scored, so this decision establishes no neural
advantage, decoding accuracy, generalization, real-time output, portable use,
home use, or clinical utility.
