# Foundation-Model Bridge v0

**Date:** 2026-08-06
**Stage:** FM-0 synthetic no-call bridge
**Status:** Implemented and locally validated
**Provider calls:** `0`

## What It Does

Foundation-Model Bridge v0 compiles a tiny target-free evidence fixture into
four deterministic, blinded request plans per item:

| Condition | CTC n-best | Causal key evidence | Role |
|---|---:|---:|---|
| `FM-A00` | absent | absent | language-prior and abstention control |
| `FM-A01` | matched | absent | CTC-only language repair |
| `FM-A02` | matched | matched | full hosted candidate |
| `FM-A03` | matched | fixed cyclic next item | correspondence control |

The output is a request **plan**, not an OpenAI wire request. No OpenAI client,
API credential, network transport, or executable provider path exists in v0.
The selected future candidate identity, `gpt-5.6-sol` through the Responses
API at low reasoning effort, is metadata shared by every condition.

## Why Structured Evidence

Hosted GPT-5.6 Sol accepts text and image input, not arbitrary custom hidden
embeddings. The bridge therefore exports only compact, inspectable evidence:

- uppercase CTC n-best hypotheses, rank, and log probability;
- causal per-frame top-key probability rows;
- entropy, frame start/end, and evidence-availability time;
- synthetic item and split provenance outside the blinded payload.

Raw EEG/MEG, signal samples, dense embeddings, NeuroToken vectors, participant
names, local paths, target/reference text, intended text, labels, and
post-outcome corrections are rejected. The internal continuous
`NeuroTokenCache v0` remains unchanged.

## Commands

Create a fresh synthetic evidence file:

```bash
neurodecode make-foundation-model-bridge-fixture \
  --out /tmp/fm0-evidence.json
```

Compile the four request plans without contacting a provider:

```bash
neurodecode build-foundation-model-ablation \
  --evidence /tmp/fm0-evidence.json \
  --out /tmp/fm0-plan.json
```

Validate and inspect the plan:

```bash
neurodecode inspect-foundation-model-ablation \
  --plan /tmp/fm0-plan.json
```

Every writer refuses an existing output unless `--overwrite` is explicit.
Inputs and outputs refuse symlinks and are capped at 1 MiB.

## Schema And Binding

The committed fixture uses
`neurodecodekit.foundation_model_synthetic_evidence` version `0`. It contains
three synthetic development items, six CTC hypotheses, 12 causal neural key
frames, and 24 top-key probabilities. There is no hidden ground truth.

The plan uses `neurodecodekit.foundation_model_ablation_plan` version `0` and
binds:

- the source file byte count and SHA-256;
- canonical source JSON SHA-256;
- separate CTC and neural-frame hashes for every source item;
- the fixed cyclic derangement map and its hash;
- each blinded request payload and its hash;
- one canonical plan-core SHA-256;
- all-zero network, credential, model, data, training, and scoring counters.

Condition and item identities remain outside `blinded_request_payload`. The
payload contains the same instruction, task context, response contract, and
only the evidence allowed for that arm. Inspection checks each nonempty CTC or
neural payload against its source-item hash, so recomputing the outer plan hash
cannot legitimize substituted evidence.

## Strict Refusals

The validator fails closed on:

- unknown or missing fields;
- target, reference, label, intended, or ground-truth field names;
- raw sensor, signal-sample, dense-embedding, NeuroToken, identity, or path
  fields;
- duplicate items, malformed split identity, or noncyclic derangement;
- nonfinite, unsorted, duplicated, or overfull probability rows;
- noncausal or nonmonotonic frame timestamps;
- Boolean counter tricks or any nonzero access counter;
- request, source-item, derangement, or plan hash tampering;
- oversized, symlinked, or accidentally overwritten files.

## Measured Roundtrip

One measured one-thread roundtrip used the committed fixture:

```text
source fixture bytes:             7,327
source items:                         3
source CTC hypotheses:                6
source causal key frames:            12
source top-key probabilities:        24
compiled condition plans:            12
compiled plan bytes:             34,349
build runtime:                 0.002746 s
build peak RSS:                21,495,808 bytes
inspect runtime:               0.001412 s
inspect peak RSS:              21,037,056 bytes
plan core SHA-256:             355e018f6cd33d7a0d8213fa20eb0798f571c84e4c2e5a2f84dff33ed6c47b5d
plan file SHA-256:             66f7af99c418945ac878608a64203277e1c7413680e0fd9c5af93f1b5b07d3be
```

Access counters for external network, API credentials, provider models, local
models, real/protected reads, protected annotations, training, and scoring
were all integer zero. End-to-end latency, provider latency, token usage,
cost, provider response identity, output text, and decoding accuracy remain
unavailable because no model was called.

## Tests

Focused tests cover deterministic replay, exact four-arm construction, blinded
payloads, cyclic derangement, source-item binding, committed fixture identity,
target and sensitive-field leakage, timing, probabilities, counters, unknown
fields, hash tampering, byte caps, symlinks, overwrite refusal, CLI help, and a
complete temporary-file roundtrip.

The focused strategy and implementation suite passes 35 tests. The complete
pre-change 1,129-test baseline advances to 1,164 passing tests with the same 3
expected skips. The final measured complete run took 31.172 seconds internally
and 32.28 seconds wall time at 629,456,896-byte external peak RSS under one-thread
environment limits. The module, fixture, registry, implementation note, and
two focused test files total 84,637 bytes.

## Next Gate

FM-1 would make one synthetic Sol qualification call. It requires a separate
explicit decision covering the API credential, outbound network request,
request count, spend cap, provider retention/privacy posture, and exact
synthetic payload. FM-0 does not grant that permission.

Engineering capability added: NeuroDecodeKit can now deterministically compile
and audit a four-condition foundation-model evidence experiment without
contacting a model provider.

Scientific claim not established: no language model, neural model, real
signal, protected row, target, or score was used, so FM-0 establishes no neural
advantage or decoding result.
