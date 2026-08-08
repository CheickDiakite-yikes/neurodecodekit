# FM-1 Synthetic Terra Provider Implementation

**Date:** 2026-08-08
**Status:** Implemented and locally validated; not executed; exact implementation
commit and remote-green CI still required
**Provider boundary:** One authorized synthetic-only `gpt-5.6-terra` invocation

## What Was Added

NeuroDecodeKit now has a dependency-free provider layer for the frozen FM-1
contract. It rebuilds the committed FM-0 plan, verifies every source and
decision hash, compiles exactly 12 blinded Responses API requests, and either
dry-runs the matrix or consumes the separately authorized one-shot execution.

The implementation lives in:

```text
src/neurodecodekit/evaluation/foundation_model_live.py
```

The public commands are:

```bash
neurodecode foundation-model-live-smoke
neurodecode foundation-model-live-smoke \
  --execute \
  --out <new-result.json> \
  --implementation-commit <full-remotely-green-sha> \
  --implementation-push-ci-run-id <run-id>
neurodecode inspect-foundation-model-live-result --result <result.json>
```

The first command is always a zero-network dry run. It does not inspect the API
credential. `--execute` is deliberately noisy and requires a new output path,
the exact implementation commit, and its successful push-CI run ID.

## Frozen Request Shape

Each request uses the same fixed provider surface:

```text
endpoint:             https://api.openai.com/v1/responses
model:                gpt-5.6-terra
reasoning:            low
service tier:         default
store / stream:       false / false
tools:                []
structured output:    strict JSON Schema
maximum output:       256 tokens per request
requests / retries:   12 sequential / 0
```

Only the committed synthetic task context, CTC hypotheses, and compact
synthetic key-evidence rows enter the request. Condition IDs, item IDs, target
or reference fields, raw EEG/MEG, dense embeddings, NeuroTokens, participant
identities, and local paths are rejected from the provider payload.

The provider response must contain one completed message from the registered
Terra model identity. The structured payload has exactly four fields:
`decoded_text`, `abstained`, `evidence_used`, and
`unsupported_content_warning`.

## One-Shot Controls

Before reading `OPENAI_API_KEY`, the execute path verifies:

1. The contract, decision, fixture, rebuilt plan, and all request hashes.
2. The current `HEAD` equals the supplied full implementation SHA.
3. The implementation descends from the authorization decision.
4. The implementation commit exists on an `origin/*` branch.
5. The tracked worktree is clean.
6. The output does not exist and is not a symlink.
7. At least 1 GiB of free disk remains.
8. Every declared numerical thread variable is unset or equal to one.

The environment credential is then read once. It is passed directly to the
fixed HTTPS transport and is never printed, serialized, hashed, or persisted.
Provider errors are reduced to bounded categories. Raw response IDs, headers,
organization metadata, and error bodies are not retained.

No retry exists. A partial provider sequence produces a consumed, parked
receipt. Failed response bodies are represented only by byte count and
SHA-256, which keeps wire accounting exact without retaining provider content.

## Result Validation

The sanitized result binds every completed response to its exact plan request
and wire-request hashes. Validation recomputes and checks:

- request order and item-condition uniqueness;
- strict parsed-output shape and refusal consistency;
- provider model identities;
- input, cached-input, cache-write, output, and reasoning-token totals;
- standard-price estimate;
- request and response byte totals;
- per-condition summaries and fixed descriptive pairings;
- runtime, peak RSS, output, request, token, and charge caps;
- access counters, warnings, unavailable fields, and claim boundary.

The result may describe whether synthetic outputs changed between CTC-only,
matched, and deranged evidence. It cannot label any change correct, useful,
neural, or scientifically positive because the fixture contains no target.

## Local Evidence Before Provider Access

The implementation-focused suite currently passes 13 tests. It covers exact
plan replay, 12-request shape, dry-run isolation, successful fake transport,
partial failure without retry, oversized replies, provider-model mismatch,
structured-schema mismatch, malformed usage, output-token cap parking,
receipt tampering, offline result inspection, CLI gates, fixed endpoint, and
absence of heavy dependencies.

The latest zero-network dry run measured:

```text
fixture bytes:                    7,327
rebuilt plan bytes:              34,349
requests:                            12
minimum request bytes:            1,047
maximum request bytes:            1,958
total request bytes:             18,399
runtime:                       0.004587 s
peak RSS:                    33,832,960 bytes
credential reads:                       0
network / provider calls:                0 / 0
provider spend events:                   0
real or protected reads:                 0
target or reference reads:               0
training / fine-tuning / scoring:        0 / 0 / 0
```

These are local interface measurements, not provider results. The post-decision
baseline of 1,176 tests advanced to 1,193 passing tests with the same 3 expected
skips. The complete suite ran in 28.274 seconds internally and 29.30 seconds
wall time at 618,086,400-byte external peak RSS. Repository-wide Ruff,
compileall, every registry JSON, root and FM-1 CLI help, the zero-network dry
run, and `git diff --check` pass. Execution remains blocked until CI is green for that exact commit.

## Pricing Check

The standard Terra pricing snapshot was rechecked against OpenAI's official
pricing page on 2026-08-08: $2.00 per million input tokens, $0.20 per million
cached input tokens, and $12.00 per million output tokens for short-context
requests. The implementation also carries the registered $2.50 per million
cache-write estimate if the provider reports cache-write tokens. Local cost is
an estimate; provider billing remains authoritative.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can build, audit, transport, and
strictly parse the exact bounded synthetic FM-1 matrix once the implementation
commit is remotely green.

Scientific claim not established: no provider call, real neural evidence,
target, score, training run, or fine-tuning run has occurred at this
implementation milestone, so no decoding or neural result exists.
