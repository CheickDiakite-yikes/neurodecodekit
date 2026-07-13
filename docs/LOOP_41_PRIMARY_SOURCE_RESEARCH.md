# Loop 41 Primary-Source Research

Date: 2026-07-13

Status: **planning research complete; experiment is `Not Started`; execution is unauthorized**

Machine boundary: `registries/loop41_research_boundary.v0.json`

## Question

Can a future authorized RW3 source-chunk replay pass through causal
preprocessing into NeuroTokenCache without losing source identity, clocks,
gaps, state, schedule independence, or provenance?

Loop 41 is the first proposed composition of acquisition mechanics and the
token interface. It is not a decoder experiment. This research created no
fixture, source chunk, adapter, preprocessing output, NeuroToken payload,
model result, stream, or device result.

## Current Gap

Three useful pieces exist, but they do not yet form the claimed path:

1. RW3 preregisters a strict `neurodecodekit.source_chunk` v0.1.0 envelope,
   five schedules, anomaly accounting, a 4 KiB source-state cap, and semantic
   replay hashes. Stage A remains unauthorized and no source-chunk
   implementation exists.
2. Loop 20 provides NeuroTokenCache v0 with modality, device, item,
   subject, session, trial, split, time, mask, geometry, causality, and
   provenance fields.
3. Loop 21 proves that one target-free mock producer emits the same tokens
   under five synthetic chunk schedules. It has no RW3 envelope, correction
   ledger, gap/reconnect semantics, or serialized resume state.

Loop 25 causal preprocessing, Loop 37 derivative execution, and the relevant
Loop 39 matrix are also unexecuted. Therefore the complete join is absent and
cannot be inferred from the component contracts.

## Primary-Source Findings

### Synchronization is a transform, not a timestamp replacement

[LSL time synchronization](https://labstreaminglayer.readthedocs.io/info/time_synchronization.html)
separates sample timestamps from periodic clock-offset measurements. It leaves
the mapping algorithm to the consumer, and its import path can additionally
smooth regular timestamps. Loop 41 therefore preserves source timestamps
byte-for-byte and records corrected timestamps as a derived, segmented,
hash-bound view. Automatic correction, smoothing, interpolation, sorting, or
deduplication is never invisible.

The same source explains that online work often needs low latency rather than
cross-stream synchronization. Those are different claims. A corrected sample
time does not measure when a chunk arrived, when preprocessing completed, or
when a token became available.

### Transport recovery is not loss-free semantic identity

The [LSL introduction](https://labstreaminglayer.readthedocs.io/info/intro.html)
distinguishes samples, chunks, metadata, buffering, retransmission, recovery,
and clock synchronization. Its
[FAQ](https://labstreaminglayer.readthedocs.io/info/faqs.html) also makes clear
that the steady clock has an arbitrary origin and cannot be naively treated as
wall time. Loop 41 must preserve gaps, duplicates, reorder, resets, and
reconnect generations even if a transport offers recovery.

The
[liblsl postprocessing flags](https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html)
show that clock sync, dejitter, monotonic timestamp forcing, and thread-safe
processing are selectable transformations. The future primary path leaves
them off unless a later preregistration names the exact operation and its
comparison rule.

### Duration evidence needs a monotonic clock

The [W3C High Resolution Time specification](https://www.w3.org/TR/hr-time-3/)
separates monotonic duration measurement from clocks that can adjust with wall
time. Python's
[`time.monotonic_ns`](https://docs.python.org/3/library/time.html#time.monotonic_ns)
provides an integer nanosecond interface to a monotonic clock, but its clock
identity and resolution must still be captured.

Loop 41 freezes seven views: source, corrected, arrival, preprocessing-ready,
token-available, decoder-emission, and render-presented. Only values in a
shared named monotonic domain may be subtracted. Decoder and render times are
unavailable. Replay has no physical capture event, so capture-to-arrival and
capture-to-text latency are unavailable too.

### A derivative must point back to its source

The [BIDS Derivatives introduction](https://bids-specification.readthedocs.io/en/stable/derivatives/introduction.html)
requires derived data to retain source provenance. Its
[common derivative metadata](https://bids-specification.readthedocs.io/en/stable/derivatives/common-data-types.html)
supports source-dataset and generated-by records. NeuroToken NPZ remains a
non-standard payload, so a future BIDS-organized envelope must label it as
such while binding source, preprocessing, producer, split, environment, and
complete-integration hashes.

## Frozen Composition Boundary

The future path has six layers:

1. RW3 source-chunk envelope.
2. Causal preprocessing and its state.
3. Causal NeuroToken producer and interval map.
4. NeuroTokenCache envelope.
5. Provenance, resources, access counters, warnings, and unavailable fields.
6. Decoder/render boundary, explicitly unavailable in Loop 41.

The contract freezes seven clock views, eight anomaly classes, five inherited
RW3 schedules, five resume cuts, 18 identity/hash bindings, 28 future fixture
families, four separately authorized stages, 32 gates, 42 refusals, and
exactly 42 false execution authorization fields.

## State And Resume

The future state must include source, clock correction, causal preprocessing,
token producer, segment/anomaly, semantic-prefix, and resource/access state.
It may not retain payload history. The RW3 portion remains capped at 4 KiB;
the complete composed state is capped at 64 KiB.

An uninterrupted run and every registered resume must produce the same
outputs, state, provenance, and semantic hashes under the preregistered
numerical policy. Five cuts exercise empty state, mid-preprocessing context,
immediately after token emission, immediately after a gap/reconnect, and
before final-tail handling.

## Anomaly Rules

- Gaps remain missing. They are never interpolated or hidden.
- Duplicates remain recorded. They are never silently deduplicated.
- Reordered samples remain recorded. They are never silently sorted.
- Counter wraps preserve raw and unwrapped values.
- Clock resets start new correction segments.
- Reconnects increment generation and explicitly choose continuation or a new
  stream.
- Non-finite payloads and source errors fail closed.
- Partial tails bind valid length, mask, zero padding, and flush policy.

A token may not silently span a forbidden gap or reset. Token semantic time is
the represented source interval; token availability time is when computation
finished. They are different fields.

## Future Stages And Dependencies

| Stage | Future work | Maximum claim |
|---|---|---|
| A | Freeze a hash-bound preregistration after dependencies close | Static design eligibility |
| B | Implement one target-free pure-Python composition | One path preserves registered semantics |
| C | Run all schedules, anomalies, and resume cuts | Target-free replay integration equivalence |
| D | Reproduce the registered result in the relevant Loop 39 cell | One reproduced replay-integration contract |

Execution is blocked until Loop 25, Loop 37, Loop 39, and RW3 Stage A each
have compatible executed closeouts. Loop 20 and Loop 21 are useful evidence,
not substitutes. Every Loop 41 stage then needs its own preregistration and
authorization.

## Resource Boundary

Future work is capped at one thread, one worker, 60 seconds per worker, 1 GiB
peak RSS, 4 KiB RW3 state, 64 KiB complete integration state, and 32 MiB total
generated fixtures, states, caches, and reports. Network bytes, protected
reads, target reads, model runs, and training runs remain zero.

## Measured Research Access

| Counter | Value |
|---|---:|
| High-level public web operations | 2 |
| Public search queries | 4 |
| Official/primary pages opened | 8 |
| Generated experiment bytes | 0 |
| Fixtures / source chunks / synthetic seed opens | 0 / 0 / 0 |
| Adapter / preprocessing / token producer runs | 0 / 0 / 0 |
| Schedule-matrix / resume runs | 0 / 0 |
| Real/cache/target reads | 0 / 0 / 0 |
| Model / training / decoder / language-model runs | 0 / 0 / 0 / 0 |
| Server / browser / socket / stream runs | 0 / 0 / 0 / 0 |
| Device / hardware operations | 0 / 0 |
| End-to-end latency measurements | 0 |

Public response bytes, web runtime, and web peak RSS are unavailable from the
research tool contract.

## Closeout

Engineering capability added: NeuroDecodeKit now has a machine-checkable
future stream-to-NeuroToken composition boundary covering clocks, anomalies,
causal state, schedules, resume identity, provenance, resources, and refusal
rules.

Scientific claim not established: No integration runtime or neural data was
opened, so this work establishes no neural advantage, decoding accuracy,
unseen-person generalization, live capture, end-to-end real-time latency,
device qualification, or portable-hardware result.
