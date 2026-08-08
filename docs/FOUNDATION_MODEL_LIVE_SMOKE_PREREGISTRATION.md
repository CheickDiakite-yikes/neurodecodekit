# FM-1 Synthetic Provider Qualification Preregistration

**Date:** 2026-08-08
**Status:** Preregistered; not authorized, implemented, or executed
**Provider candidate:** OpenAI `gpt-5.6-terra`
**Evidence:** The committed 7,327-byte FM-0 synthetic fixture only

## Question

Can NeuroDecodeKit transport its blinded four-arm synthetic evidence matrix
through the OpenAI Responses API, obtain strict structured outputs, and measure
language-prior, abstention, cost, latency, and evidence-sensitivity behavior
without sending targets, real neural data, identities, or dense NeuroTokens?

This is an engineering and behavioral smoke test. There is no reference text
in the fixture, so it cannot measure decoding accuracy or establish a neural
advantage.

## Why Terra

The long-term architecture keeps `gpt-5.6-sol` as the quality-first hosted
candidate. FM-1 instead selects `gpt-5.6-terra` for this bounded synthetic
qualification because OpenAI documents Terra as the balanced lower-cost member
of the GPT-5.6 family. Luna remains a possible later high-volume comparator but
is not part of this one-shot contract. Adding it now would double calls without
answering the transport question.

The pricing snapshot checked on 2026-08-08 is $2.00 per million short-context
input tokens, $0.20 per million cached input tokens, and $12.00 per million
output tokens for standard Terra requests. Pricing must be reverified before
execution. The contract caps the estimated standard provider charge at $0.50.

Primary OpenAI sources:

- https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6
- https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md
- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/docs/guides/structured-outputs

## Frozen Source

FM-1 must rebuild the existing FM-0 plan from:

```text
fixtures/foundation_model_bridge_synthetic_evidence.v0.json
```

The execution must verify all of these identities before any credential read or
network call:

```text
fixture bytes:          7,327
fixture file SHA-256:   12f1b68f3241c80e4ba54872a3c97769e666ad2342f84328b1a5df91f0089bdb
plan bytes:             34,349
plan file SHA-256:      66f7af99c418945ac878608a64203277e1c7413680e0fd9c5af93f1b5b07d3be
plan-core SHA-256:      355e018f6cd33d7a0d8213fa20eb0798f571c84e4c2e5a2f84dff33ed6c47b5d
items:                  3
condition requests:     12
```

The original FM-0 plan remains a no-call Sol artifact. FM-1 is an additive
execution contract that applies the exact blinded payloads to Terra; it does
not rewrite FM-0 or relabel its historical model metadata.

## Frozen Matrix

Each synthetic item produces exactly four independent requests:

| ID | CTC evidence | Structured neural evidence | Diagnostic role |
|---|---:|---:|---|
| `FM-A00` | absent | absent | language-prior and abstention control |
| `FM-A01` | matched | absent | CTC-only language repair |
| `FM-A02` | matched | matched | full synthetic evidence |
| `FM-A03` | matched | fixed cyclic derangement | correspondence control |

The model receives neither condition identity nor item identity. Model,
instructions, schema, reasoning, service tier, tools, storage setting, and
output budget remain identical across all 12 requests.

## API Contract

```text
endpoint:                  https://api.openai.com/v1/responses
model:                     gpt-5.6-terra
reasoning effort:          low
service tier:              default
store:                     false
stream:                    false
tools/search:              none
conversation state:        none
structured output:         strict JSON Schema
max output per request:    256 tokens
requests:                  exactly 12, sequential
retries:                   zero
```

The credential may be read once from the existing `OPENAI_API_KEY` process
environment only after every local and remote-green gate passes. Its value may
never be printed, serialized, hashed, persisted, or included in an exception.

## Resource Envelope

```text
CPU threads/workers:               1 / 1
wall time:                         420 seconds
peak RSS:                          256 MiB
timeout per request:               30 seconds
wire request per call:             16 KiB
wire response per call:            256 KiB
total wire request bytes:          192 KiB
total wire response bytes:         3 MiB
generated result:                  2 MiB
total output tokens:               3,072
estimated standard provider cost:  $0.50 maximum
minimum free disk before execute:  1 GiB
```

Execution is one-shot and has no retry. A failed or partial invocation consumes
FM-1 and must be parked rather than rerun or repaired against observed outputs.

## Required Result

The sanitized result must retain request hashes, parsed structured outputs,
response hashes, provider-reported model identities, completion/refusal/schema
status, token usage, wire bytes, per-request latency, total runtime, peak RSS,
estimated standard cost, condition-level descriptive summaries, warnings, and
all access counters. It must not retain the credential, authorization header,
raw HTTP headers, raw provider response IDs, organization metadata, or local
paths.

No target opens after the run. There is no accuracy score, model selection, or
post-output tuning. Descriptive comparisons may report whether outputs changed
between CTC-only, matched, and deranged evidence, but may not call that change
correct, neural, or beneficial.

## Ordered Gate

1. Commit and remotely qualify this contract without provider access.
2. Record the exact separate authorization sentence from the contract.
3. Commit and remotely qualify a synthetic-fixture-only implementation.
4. Rebuild and verify the exact FM-0 plan in a zero-network dry run.
5. Execute one 12-request invocation and write one bounded sanitized result.
6. Mark FM-1 consumed whether it passes or parks.

The current request authorizes API integration work and reuse of the existing
credential. It does not replace the charter's post-contract exact Tier C
execution decision, so no provider call occurs from this preregistration.

## Claim Boundary

Engineering capability potentially established after a clean run: the exact
synthetic evidence matrix can traverse the provider boundary and return through
the strict schema with measured cost and latency.

Scientific claim not established: FM-1 has no target and no real neural
evidence, so it cannot establish decoding accuracy, neural advantage,
brain-specific information, generalization, real-time operation, portable
hardware, home use, or clinical utility.
