# COMM-LIVE-G0 Amendment 1: Partition, Clock, And Hash Semantics

Date: 2026-08-27

Status: **Prospective narrow amendment; implementation paused pending remote green**

Machine amendment:
`registries/communication_live_session_g0_amendment_1.v0.json`

## Reason

Two independent read-only reviews found three ambiguities in the remotely green
`COMM-LIVE-G0` registration:

1. chunk-count warm-up conflicts with required chunk-partition invariance;
2. source-capture and host-arrival clocks are not necessarily in comparable
   clock domains; and
3. the valid-payload, semantic-prefix, and self-containing envelope hashes need
   exact preimages.

This amendment narrows those mechanics before implementation. It adds no data,
adapter, device, network, model, provider, release, or claim authority.

## Fixed Sample Cadence

Transport chunks do not define processor updates. Each reconnect generation is
treated as one logical sequence of valid source samples:

- processor frame width: exactly 16 valid source samples;
- frame boundaries: generation-relative intervals `[0,16)`, `[16,32)`, and so
  on;
- warm-up: exactly 32 valid source samples, or two complete processor frames;
- first output-eligible frame: generation-relative frame index 2;
- incomplete tail: buffered until the next accepted chunk completes the frame;
  and
- one transport chunk may yield zero, one, or multiple processor frames.

The original `warmup_chunks_per_generation: 2` is superseded by
`warmup_valid_samples_per_generation: 32`. Gap, source error, disconnect, or
reconnect discards every incomplete tail and resets frame index, warm-up,
processor state, provisional hypothesis, stability, and rearm state. No tail or
state may cross a reconnect generation.

The same logical stream partitioned into one-sample, fixed, jittered, or
whole-stream chunks must produce identical semantic-prefix hashes, processor
frame events, abstentions, provisional hypotheses, stable commits, resets, and
frame-level latency records.

## Clock Domains And Availability

Ordering is checked within each declared clock domain. A source timestamp and a
host monotonic arrival time are not subtracted merely because both are numeric.
Cross-domain transport or capture-to-output latency is available only when:

- a named correction maps both values into one declared monotonic domain;
- the correction ledger hash validates;
- no unrepresented reset or regression occurred; and
- the resulting values pass monotonic and causal ordering checks.

Otherwise the latency value is `null`, its availability flag is false, and the
unavailable reason is explicit. Generated fixtures may use one shared
`synthetic_relative_monotonic` domain, but that proves arithmetic only.

Chunk-local arrival boundaries may differ across transport partitions. They are
audited but excluded from the canonical replay-equivalence payload. Frame-level
arrival and completion clocks are derived at fixed logical frame boundaries and
remain identical across partitions.

## Exact Hash Preimages

Canonical JSON is UTF-8, key-sorted, compact (`(',', ':')`), rejects NaN and
infinity, and ends in one newline.

### Valid payload

Valid values are encoded in sample-major order with channels in the frozen
channel order. Each value uses the exact declared IEEE-754 `float32` or
`float64` little-endian representation. Padding values never enter this hash.
The preimage binds a fixed domain tag, dtype, channel count, valid-sample count,
and packed valid values.

### Semantic prefix

The initial digest binds a fixed domain tag and the immutable source bindings.
Each logical sample or control event advances the chain as:

```text
H[n] = SHA256(domain || H[n-1] || uint64_be(len(element)) || element)
```

A data element binds generation, source-sample index, source and corrected
timestamp views, packet/anomaly facts at that boundary, and the channel vector
in frozen order. A control element binds its record kind, generation,
correction segment, and exact declared boundary facts. Snapshots persist the
current digest bytes and element count, never an implementation-specific hash
object.

### Chunk envelope

`chunk_envelope_sha256` is computed last over the complete canonical envelope
with only `hashes.chunk_envelope_sha256` omitted. Every other field, including
the valid-payload and semantic-prefix hashes, remains in the preimage. Unknown
fields are refused.

## Transactional Push And Snapshot

`LiveSession.push` validates and executes against a candidate copy. The live
session state changes only after envelope, hash, continuity, processor, clock,
abstention, commit, and resource checks all pass. Every refusal must leave the
serialized snapshot byte-identical.

A snapshot binds source identity, channel contract, source/config/split/adapter
hashes, processor/model/decoder/policy hashes, generation, sequence, correction
segment, next source sample, semantic digest and count, frame buffer and index,
warm-up, provisional and committed output, stability/rearm state, counters, and
its own self-excluding snapshot hash. Restore requires exact bindings and
revalidates the snapshot before creating a session.

Recursive forbidden-key scanning applies to SourceChunk records, bindings,
processor events, LiveUpdate values, and snapshots. Targets, labels, intended
or reference text, scorer state, and language-model context remain forbidden.

## Qualification Effect

The 33 registered adversarial families remain required. Combined families must
exercise every named subcase, including float32/float64 bit handling,
negative-zero padding refusal, duplicate versus conflicting duplicate,
transaction rollback, cross-domain latency unavailability, and exact-cap versus
cap-plus-one behavior.

Implementation remains paused until this amendment is committed, pushed, and
both required CI jobs are green. The one official generated qualification
remains closed until the amended implementation is separately committed,
pushed, and remotely green.

Engineering capability established now: none; this amendment only removes
ambiguity from a future generated implementation.

Scientific claim not established: no EEG, communication, unseen-person,
EEG-beyond-peripheral, live-device, or human-benefit evidence is created.
