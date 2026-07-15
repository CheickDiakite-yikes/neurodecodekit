# Loop 48 Artifact-Only Failure Localization Authorization Packet

Date: 2026-07-15

Status: **Awaiting the exact user authorization sentence**

Current execution state: **Unauthorized; every `authorized_now` field is false**

Green contract commit: `83309bfc29300c542c7a7a6dc0f193baba28d42e`

Green push CI: [run 29431318268](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29431318268)

Green PR CI: [run 29431347801](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29431347801)

Machine request: `registries/loop48_authorization_request.v0.json`

Registered contract: `registries/loop48_failure_localization_contract.v0.json`

## Decision In Plain English

This is permission for one very small software-and-arithmetic audit over four
already committed JSON files. It is not permission to reopen the consumed S21
experiment, inspect private Loop 26 artifacts, run a model, or tune anything.

If separately authorized, NeuroDecodeKit may:

- implement a dependency-light artifact analyzer and synthetic isolation tests;
- verify the exact paths, byte sizes, and SHA-256 hashes of four committed JSON
  inputs;
- recompute the already public candidate/prior, blank-fraction, and seed-
  dispersion summaries;
- apply the frozen ordered eight-class diagnostic tree; and
- write one aggregate JSON report without plaintext targets or predictions.

The expected class is `F5` if all bound files remain exact. That is expected
replay of a post-outcome descriptive rule, not new independent evidence.

## Exact Input Boundary

| Input | Bytes | SHA-256 |
|---|---:|---|
| `registries/loop26_shared_validation_result.v0.json` | 83,713 | `7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4` |
| `registries/loop26_prediction_freeze.v0.json` | 31,271 | `10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348` |
| `registries/loop26_shared_validation_contract.v0.json` | 31,988 | `c4f94b214993973ec4b4ea7e7b27174023dfef227c8dd4d9b912ac48bb98ccce` |
| `registries/loop25_causal_preprocessing_result.v1.json` | 8,573 | `5f80c4d282be79aadaf78908c151acd3949e0a754182cf58b27dcca681218ab1` |

Total input bytes are exactly `155,545`. The implementation must fail closed
if any path, size, hash, schema, or no-plaintext assertion differs.

## Exact Operation Inventory

| Operation | Exact amount |
|---|---:|
| Committed JSON inputs | 4 |
| Aggregate report writes | 1 |
| CPU threads / workers | 1 / 1 |
| Model inference runs | 0 |
| Training or parameter-update runs | 0 |
| Target deliveries | 0 |
| Protected cache/member reads | 0 |
| Network calls or downloads | 0 |
| Reruns after Stage A | 0 |

Stage A must verify identities, recompute the frozen summaries, apply class
precedence, write one report, and stop. It may not choose a seed, threshold,
loss, architecture, model size, or next experiment from validation outcomes.

## Computer And Storage Envelope

| Resource | Hard cap |
|---|---:|
| Runtime | 30 seconds |
| Peak RSS | 256 MiB |
| Generated output | 1 MiB |
| CPU threads / workers | 1 / 1 |
| Network and download bytes | 0 |

Any cap breach fails and parks Stage A. The generated report must remain
aggregate, target-free, prediction-free, inspectable, and outside protected
data roots.

## Required Order

1. Record the exact sentence below in a separate authorization-only registry.
2. Test, commit, push, and obtain green CI for that authorization record.
3. Implement the analyzer and synthetic isolation tests without reading any of
   the four registered inputs through the runtime.
4. Test, commit, push, and obtain green CI for that implementation.
5. Execute Stage A once over the four exact committed JSON inputs.
6. Validate the one report, record resources and access counters, and close or
   park Loop 48 without a rerun.

## Exact Authorization Sentence

To authorize this exact scope, send the following sentence verbatim:

```text
Authorize the Loop 48 artifact-only failure-localization implementation and one Stage A execution exactly as scoped in docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md and registries/loop48_failure_localization_contract.v0.json. I authorize reading and SHA-256 verification of only the four committed JSON artifacts named by that contract; recomputation of the frozen aggregate blank/CER summaries and six fixed-prefix seed-dispersion checks; application of the ordered eight-class decision tree; and emission of one aggregate target-free JSON report under one CPU thread, one worker, 30 seconds, 256 MiB peak RSS, and 1 MiB generated output. I do not authorize any Git-ignored Loop 26 output, cache/member, train/validation array, target, checkpoint, private prediction, source-test/session-2, S7/S20/S25, raw FIF/MAT, model inference, training, parameter update, threshold/seed/architecture selection, download, language model, RW3, stream, device, hardware, scientific claim upgrade, or rerun.
```

General continuation, co-researcher autonomy, broad research permission, or
the earlier Loop 26 authorization does not substitute for this exact sentence.
The request remains immutable and unauthorized after it is green; a separate
decision record must capture the sentence if it is supplied.

## Maximum Possible Result

A clean Stage A can establish only that the four exact committed aggregate
artifacts satisfy `F5` under the frozen post-outcome decision tree.

## Still Not Established After A Pass

A pass cannot establish a causal root cause, independent evidence, prospective
validation, neural advantage, sensor-signal dependence, brain-specific origin,
decoding utility, unseen-person generalization, real-time behavior, EEG or
portable/home-device performance, assistive value, diagnostic value, or
clinical utility.

## Current Proof Boundary

The contract commit and both CI runs are green. No Loop 48 analyzer, fixture,
generated report, authorization decision, protected read, model operation,
training operation, scoring event, or scientific result exists.
