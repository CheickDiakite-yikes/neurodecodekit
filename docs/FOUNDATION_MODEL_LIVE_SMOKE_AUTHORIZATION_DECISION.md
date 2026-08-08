# FM-1 Synthetic Provider Qualification Authorization Decision

**Date:** 2026-08-08
**Status:** Authorized; implementation and execution not started
**Contract commit:** `7db14d51cbe8bde5a5d7ac43479b20e575e9ae7c`
**Contract CI:** `31267860543` passed Base Python and Optional Neuro Readers

## Decision

The user supplied the exact authorization sentence frozen in
`registries/foundation_model_live_smoke_contract.v0.json`:

> Authorize one FM-1 synthetic GPT-5.6 Terra provider qualification exactly as scoped in docs/FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md and registries/foundation_model_live_smoke_contract.v0.json. I authorize one read of the existing usable OPENAI_API_KEY environment variable, exactly 12 sequential Responses API calls to gpt-5.6-terra over only the committed 7,327-byte synthetic fixture and its four blinded conditions, standard service, low reasoning, strict structured output, no tools, store false, no retries, at most 3,072 output tokens, 420 seconds, 256 MiB peak RSS, 2 MiB generated output, and 0.50 USD estimated standard provider charge. I do not authorize real or protected data, targets, labels, reference or intended text, raw EEG or MEG, dense embeddings or NeuroTokens, participant identities, local paths, training, fine-tuning, model downloads, search tools, additional models, additional calls, substitutions, reruns, scientific scoring, or claim upgrades.

This decision binds contract SHA-256
`30dd5fc7475f4985e97f496166792a65d0f2e9353230652cb5c2526c74f86eae`.
It cannot be applied to an amended contract, another fixture, another model, a
different request count, or a rerun.

## Ordered Effect

This authorization becomes executable only after:

1. this decision-only commit is pushed and remotely green;
2. the synthetic-fixture-only provider implementation is committed, pushed,
   and remotely green;
3. a zero-network dry run reconstructs the exact 34,349-byte FM-0 plan;
4. the current implementation commit and clean tracked worktree are verified.

Only then may the runner read `OPENAI_API_KEY` once and consume the single
12-request invocation. The invocation is consumed even if it fails or parks.

## Current Counters

At this decision boundary:

```text
external network calls:        0
API credential reads:          0
provider spend events:         0
provider model calls:          0
real or protected reads:       0
target or reference reads:     0
raw or dense neural uploads:   0
training/fine-tuning runs:      0 / 0
scientific scoring runs:       0
```

Engineering authorization granted: one bounded synthetic provider transport
qualification after all ordered implementation gates pass.

Scientific claim not established: an authorization record is not evidence of
decoding accuracy, neural advantage, brain-specific information,
generalization, real-time operation, portable hardware, home use, or clinical
utility.
