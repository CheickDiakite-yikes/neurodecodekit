# Loop 26/31/33 Shared Validation Authorization Packet

Date: 2026-07-13

Status: **Awaiting the exact user authorization sentence**

Current execution state: **Unauthorized; every `authorized_now` field is false**

Green preregistration commit: `881145d865b1e25e3982b758c5fd2e519d16933b`

Green CI: [run 29282661766](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29282661766)

Machine request: `registries/loop26_authorization_request.v0.json`

Registered contract: `registries/loop26_shared_validation_contract.v0.json`

## Decision In Plain English

This is the permission gate for one carefully bounded scientific attempt on
the existing S21 session-1 MEG sentence cache. It is not a request for more
data, a larger model, or a broad research license.

An authorization would permit the project to:

- isolate exactly 55 training rows and six target-free validation-signal rows;
- fit one 2,908-parameter causal model family across six nested training sizes
  and three fixed seeds;
- run the preregistered signal, zero-signal, derangement, timing, and linear
  controls;
- freeze 31 six-row prediction sets before any validation target reaches the
  prediction process or scorer; and
- after that hash-only freeze record is committed, pushed, and remotely green,
  deliver the same six validation targets to one isolated scorer exactly once.

It would not authorize the five consumed source-test rows, consumed session 2,
S25, raw FIF/MAT files, downloads, a larger model, a restart, language-model
assistance, RW3, streaming, devices, or hardware.

## Why One Shared Event

Loop 26 asks whether the small causal model beats a train-only no-signal prior.
Loop 31 asks whether that result actually depends on sensor-signal structure.
Loop 33 asks whether performance improves across 8, 16, 24, 32, 44, and 55
unique training sentences.

Those questions all depend on the same six validation sentences. Scoring Loop
26 first and designing the controls afterward would make the later analyses
retrospective. The registered protocol therefore freezes every prediction for
all three loops and scores them in one exposure.

## Exactly What Runs

| Operation | Exact amount |
|---|---:|
| Source-cache hash passes | 1 |
| Training signal/target rows | 55 |
| Validation signal rows | 6 |
| Validation target rows after green freeze | 6 |
| Source-test or session-2 rows delivered | 0 |
| Parameter-update runs | 21 |
| Optimizer steps | 5,040 |
| Target-blind model-inference runs | 24 |
| Train-only prior fits | 6 |
| Frozen prediction sets | 31 |
| Validation scoring deliveries | 1 |
| CPU threads / workers | 1 / 1 |
| New download bytes | 0 |

Seeds are exactly `2601`, `2602`, and `2603`. There are no restarts, early
stopping choices, favorable-seed selection, or post-target reruns.

## Computer And Storage Envelope

| Resource | Hard cap |
|---|---:|
| End-to-end runtime | 1,500 seconds |
| Parameter-update runtime | 1,200 seconds |
| Peak RSS | 1 GiB |
| Working arrays | 128 MiB |
| Checkpoints | 4 MiB total |
| Prediction payloads | 2 MiB total |
| All generated artifacts | 32 MiB total |
| New data/model downloads | 0 bytes |

The runtime must use one CPU thread and one worker. Any cap violation fails and
parks the event. Generated cache derivatives, checkpoints, and prediction text
stay under `.codex_work/loop26`, remain Git-ignored, and are never committed.

## Important Archive Correction

The old Loop 14 cache is a monolithic deflated NPZ. Its legacy loader copied
whole target arrays before selecting rows, so at least two historical commands
physically materialized all six validation-target rows. Those rows were not
used for loss, model selection, threshold choice, predictive scoring, or a
reported metric.

The phrase "validation targets were physically unopened" is therefore
withdrawn. The accurate boundary is:

> The six validation targets have not been used for model fitting,
> hyperparameter selection, restart selection, threshold choice, or predictive
> scoring.

The new runtime must use bounded row streaming and isolated derivatives. Since
deflate still forces opaque traversal of excluded bytes, the report must say so
instead of relabeling traversal as physical nonaccess.

## Required Order

1. Record the exact sentence below in a separate authorization-only registry.
2. Test, commit, push, and obtain green CI for that authorization record.
3. Implement and synthetically test the bounded reader, model, controls,
   prediction freezer, and scorer without opening real cache values.
4. Test, commit, push, and obtain green CI for the implementation.
5. Pass every static identity, archive, split, scaler, channel, environment,
   and resource gate.
6. Create only the 55-row train and six-row target-free validation-input
   derivatives.
7. Run all registered fits, controls, priors, inferences, and prediction sets.
8. Commit and remotely qualify a hash-only prediction-freeze record.
9. Deliver the same six validation targets to one scorer once.
10. Report every registered condition and close or park without a rerun.

## Exact Authorization Sentence

To authorize this exact scope, send the following sentence verbatim:

```text
Authorize the Loop 26/31/33 shared S21 validation implementation and one registered execution exactly as scoped in docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md and registries/loop26_shared_validation_contract.v0.json. I authorize one hash pass over the named monolithic S21 session-1 cache; opaque streaming traversal of its deflated row members; delivery of exactly 55 train signal/target rows and six validation signal rows into isolated derivatives; 21 bounded training runs, 24 target-blind model-inference runs, six train-only no-signal prior fits, 31 frozen prediction sets, and one conditional scoring delivery of the same six validation targets only after the prediction-freeze hash record is committed, pushed, and remotely green. I do not authorize delivery or scoring of the five source-test rows or session 2, raw FIF/MAT reads, S7/S20/S25, downloads, larger models, restarts, language models, RW3, streams, devices, hardware, post-target tuning, or any rerun after validation scoring.
```

General continuation, co-researcher autonomy, roadmap approval, silence, or the
earlier Loop 25 and RW3 decisions do not substitute for this exact sentence.
The request remains immutable and unauthorized after it is green; a separate
decision record will capture the sentence if and when it is supplied.

## Possible Result

If every primary and control gate passes, the maximum supported result is a
bounded same-person, same-session predictive advantage that depends on the
available sensor-signal structure for this exact task, split, preprocessing,
and model, plus the registered 8-to-55-sentence scaling description.

## Still Not Established After A Pass

A pass would not establish brain-specific neural origin, source-test or cross-
session performance, unseen-person or population generalization, end-to-end
causal or real-time decoding, Brain2Qwerty v2 equivalence or improvement, EEG,
OPM, wearable, portable, or at-home performance, arbitrary-thought decoding,
assistive efficacy, diagnostic value, or clinical capability.

## Current Proof Boundary

The preregistration is green and hash-bound. No Loop 26 implementation, real
cache value read, target delivery, model run, training run, prediction,
validation score, or new scientific result exists.
