# COMM-LIVE-G0 Generated LiveSession Preregistration And RW3 Stage A Review

Date: 2026-08-27

Status: **Prospective Tier B generated-engineering registration and narrow RW3 Stage A review**

Machine contract:
`registries/communication_live_session_g0_contract.v0.json`

## Purpose

The communication program already has causal frame production and incremental
decoder components, but it does not yet have the session boundary required to
call any future run live. `COMM-LIVE-G0` freezes that missing boundary before
implementation: transport identity, loss and reconnect semantics, source-only
activation, persistent causal state, abstention, stable commits, and separate
capture-to-presentation clocks.

This gate uses generated fictional streams and deterministic fake processors
only. It cannot establish neural information, communication decoding,
unseen-person generalization, real-time performance, device compatibility, or
human usability.

## Existing SourceChunk Binding

`COMM-LIVE-G0` does not define a second transport envelope. It consumes the
existing `neurodecodekit.source_chunk` schema frozen in
`registries/replay_equivalence_contract.v0.json`, including its nested
identity, sequence, channels, payload, sample-axis, timestamp, packet,
anomaly, causality, provenance, hash, warning, and unavailable-field records.
RW3 continues to own transport representation; `LiveSession` begins only after
strict `SourceChunk` validation.

The prior RW3 contract deliberately left pure-Python Stage A implementation
and synthetic fixture generation unauthorized pending separate review. This
document is that additive review. After this exact registration is committed,
pushed, and remotely green, it permits only:

- a dependency-free validator/factory for the existing SourceChunk v0 schema;
- generated SourceChunk fixtures under the stricter caps below; and
- the downstream generated-only `LiveSession` implementation.

It does not change the SourceChunk schema or authorize BrainFlow, LSL, XDF,
loopback sockets, network discovery, playback, physical hardware, real files,
targets, models, cleaning, resampling, or any later RW3 adapter stage.

## Frozen Live Interface

The minimum interface is:

```text
LiveSession.push(SourceChunk) -> LiveUpdate
LiveSession.snapshot() -> LiveSessionState
LiveSession.restore(LiveSessionState, exact bindings) -> LiveSession
```

### Source chunk

The session accepts only a validated SourceChunk record. Raw arrays, alternate
chunk dictionaries, and silently upgraded schemas are refused. Targets,
labels, intended text, reference text, probabilities supplied by a scorer, and
language-model context are forbidden from this capability.

### Session state

The state machine is:

```text
created -> active -> degraded -> active(new generation) -> closed
```

The first accepted chunk opens generation zero at sequence zero. Within a
generation, both sequence identity and source sample position must be exact.
Duplicate, reordered, or silently missing input is refused. An explicit gap or
disconnect clears hypothesis stability, marks output invalid, resets every
processor state, and enters `degraded`. No later chunk is accepted until an
explicit reconnect advances the generation by exactly one. Reconnect never
bridges model, preprocessor, endpointer, or decoder state across the gap.

### Causal processor output

The processor receives only source samples and prior source-derived state. For
each accepted chunk it may return one candidate symbol plus:

- source-active state;
- signal-quality validity;
- confidence;
- preprocessing-complete and model-complete clocks; and
- a bounded declared mutable-state size.

It has zero right context. It cannot receive a known trial end, held-out target,
reference text, scorer state, future chunk, or language-model output.

Each `LiveUpdate` binds the generation, correction segment, accepted sample
interval, semantic-prefix hash, provisional hypothesis, append-only committed
delta, invalid-output mask, warm-up boundary, abstention/anomaly reasons,
separate clocks, exact config/model/decoder/policy hashes, and bounded state
counters. Provisional output is revocable; committed output is not.

### Abstention and stable commit

No visible hypothesis or commit is eligible unless source activation is true,
quality is valid, confidence meets the frozen threshold, the generation has
completed its warm-up, and all clock checks pass. A stable commit requires the
same eligible nonblank symbol on three consecutive processor updates. Gap,
disconnect, low quality, low confidence, blank output, or inactive source
clears the stability run. A committed symbol is emitted once and cannot be
committed again until the processor first returns blank or inactive source.

### Clocks and latency

The session records these clocks separately:

1. capture start;
2. capture end;
3. host arrival;
4. preprocessing complete;
5. model complete;
6. first eligible output;
7. stable commit; and
8. presentation.

Every clock is monotonic and ordered. Capture-to-first-output,
capture-to-stable-commit, capture-to-presentation, transport, preprocessing,
model, and presentation delay are reported independently. Generated replay may
prove arithmetic and ordering only; it is not a measurement of device or human
latency.

## Frozen Generated Qualification

After this registration commit is pushed and both required CI jobs are green,
implementation may add one dependency-free module, one sidecar CLI, generated
fixtures, and tests. After that exact implementation is separately committed,
pushed, and remotely green, one official generated qualification may run.

The qualification must perform two deterministic replays over four fictional
sessions and three transport schedules:

1. contiguous jittered chunks;
2. explicit gap, disconnect, and generation-bounded reconnect; and
3. low-quality and low-confidence abstention.

The replays must agree on canonical event, abstention, commit, reset, and
latency-accounting payloads. The contiguous schedule must be invariant to
chunk partition. The reconnect schedule must prove that no stability or state
crosses a generation boundary.

Exactly these 33 adversarial families are required:

1. source identity mismatch;
2. modality or device drift;
3. channel contract drift;
4. sampling-rate drift;
5. identical duplicate record;
6. duplicate sequence with conflicting payload;
7. partial source-sample overlap;
8. reordered sequence;
9. hidden sample gap;
10. timestamp-only inferred gap without an explicit anomaly record;
11. unrepresented clock reset;
12. correction-ledger tampering;
13. generation rollback;
14. generation skip;
15. old-generation record after reconnect;
16. chunk after disconnect;
17. reconnect without a generation increment;
18. reconnect while not degraded;
19. capture/arrival clock-order violation;
20. arrival-monotonic rollback;
21. nonfinite, nonzero-padding, or hash-invalid payload;
22. chunk-size cap breach;
23. session-sample cap breach;
24. processor-state cap breach;
25. snapshot tampering;
26. snapshot from another source, config, model, or semantic prefix;
27. quality-gate bypass;
28. confidence-gate bypass;
29. stability carried across a gap;
30. repeated stable commit;
31. target, label, intended-text, or reference-text leakage;
32. deadline-expired or abstain-all positive-control acceptance; and
33. use after close.

Every malformed case must fail closed with its registered refusal ID. No
generated target or expected output may enter the runtime session capability.

## Resource Envelope

- one CPU thread, one worker, and one numerical job;
- standard library only for the base implementation;
- at most 4 fictional sessions, 32 channels, 4,096 samples per chunk, 65,536
  samples per session, 4,096 events, and 64 explicit gaps;
- at most 4 KiB serialized SourceChunk adapter state and 1 MiB mutable
  processor/session state;
- at most 16 MiB temporary generated bytes;
- at most 1 MiB public result bytes;
- at most 30 seconds wall time and 256 MiB peak process-tree RSS;
- zero network, provider, model download, real/private path, stream, device,
  release, or cleanup outside invocation-created temporary files; and
- zero retry or rerun after the official generated qualification.

## Acceptance Route

`COMM-LIVE-G0-R1` requires:

- exact interface and state-machine validation;
- both deterministic replays equivalent;
- all three schedules passing;
- all 33 adversarial families refused;
- no hidden gap or state bridge;
- abstention and repeated-commit gates enforced;
- complete ordered latency accounting;
- every resource cap passing; and
- every real, private, provider, device, scientific, and release counter zero.

Any failure routes to `COMM-LIVE-G0-R0`, consumes the generated invocation, and
parks this exact qualification without rerun.

## Authority And Claim Boundary

The approved research-autonomy charter permits this bounded generated
implementation and later generated qualification after their own green proof
barriers. This explicit Stage A review changes only the two prior RW3 flags for
pure-Python SourceChunk implementation and synthetic fixture generation, with
delayed effect after this registration is remotely green. It does not activate
the implementation or qualification before that barrier.

`DREYER-C5R-1-HL` remains the sole active Tier C packet. This lane does not
authorize a Dreyer request, real EEG access, target delivery, scoring, a
provider call, a physical stream, a device, a human recording, release, or a
scientific claim upgrade.

Engineering capability sought: a deterministic, fail-closed, source-clocked
session boundary that can later host a frozen causal neural decoder.

Scientific claim not established: generated transport and state-machine proof
cannot establish communication decoding, unseen-person generalization, EEG
beyond peripheral controls, live device latency, or human benefit.
