# Loop 25 Causal Preprocessing Preregistration

Date: 2026-07-12

Status: **Frozen preregistration; no implementation or execution authorized**

Machine contract: `registries/causal_preprocessing_contract.v0.json`

Primary-source research: `docs/LOOP_25_PRIMARY_SOURCE_RESEARCH.md`

Preregistration parent commit: `3ae7d97`

Contract SHA-256:
`42781526225c556d0df54d1b6924fd5d9ecf95578a84c3e3922b6d5c7035050e`

Proof posture: target-free synthetic causal-preprocessing protocol only

## Decision Requested After This Commit

This document does not authorize implementation. After this preregistration is
tested, committed, pushed, and remotely green, the exact sentence that can
authorize only Loop 25 is:

> Authorize Loop 25 implementation exactly as scoped in
> `docs/LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md`. Do not authorize real
> or consumed data, targets, model inference, training, RW3 Stage A, streams,
> devices, or hardware.

To hold it, use:

> Hold Loop 25 implementation. Keep every Loop 25 execution authorization flag
> false.

General continuation toward Loop 44, approval of the roadmap, the parked Loop
24 authorization, an RW3 decision, an issue, a pull request, silence, or a
request for better real-time behavior is not Loop 25 execution authorization.

## Question

Can one explicit preprocessing path transform contiguous five-channel samples
from 1,000 Hz to 100 Hz incrementally while preserving exact sample indices,
timestamps, state, and float32 outputs across adversarial transport chunking,
resume cuts, and future-input perturbations with zero right context?

The gate answers an upstream mechanics question. It does not run an encoder,
decoder, aligner, language model, target, label, recording, or cache. It does
not ask whether the causal path preserves neural decoding accuracy.

## Why This Gate Is Necessary

Loop 21 proves that the frame producer itself can replay causally once it
receives a 100 Hz sample stream. It does not prove that the stream was produced
causally.

The current real sentence path follows the public Brain2Qwerty v2 offline
recipe: 0.5-45 Hz filtering, 50 Hz notch, 100 Hz downsampling, median/IQR
scaling, +/-5 clamping, complete sentence boundaries, and post-completion
context. MNE 1.12.1 defaults the local notch and bandpass calls to
zero-phase FIR filtering and the resampler to whole-signal FFT processing.
Those choices are legitimate for offline evidence and explicitly incompatible
with zero-lookahead claims.

Without a separate gate, it would be easy to:

- call a causal encoder “real time” after giving it zero-phase inputs;
- let every chunk restart a filter and hide boundary transients;
- shift the decimation phase when chunk sizes change;
- recompute a median/IQR with future or evaluation samples;
- compensate filter delay using samples that have not arrived;
- silently pad an unfinished sentence or stream tail;
- repair gaps or overlaps without recording a discontinuity;
- compare a new causal signal path to consumed model outputs and tune it toward
  a preferred text result;
- treat 1,000-to-100 Hz success as compatibility with arbitrary EEG hardware.

This preregistration removes those degrees of freedom before coefficients,
fixtures, or outputs exist.

## Authorization Boundary

Included now:

- public primary-source research;
- a local source audit at parent `3ae7d97`;
- one strict JSON contract;
- dependency-free invariant tests;
- exact transform, state, fixture, schedule, resume, future-mutation,
  frequency, timing, normalization, flush, resource, access, refusal, and claim
  boundaries;
- a future authorization sentence.

Not included now:

- SciPy filter design or coefficients;
- a preprocessing implementation or import;
- target-free fixture generation or fixture files;
- opening seed 2501 or 2502;
- numeric filtering, decimation, normalization, timing, or frequency-response
  execution;
- report, audit, payload, state, or CLI output;
- raw, real, cached, consumed, target, label, text, prediction, checkpoint, or
  model access;
- training, calibration, parameter updates, or architecture work;
- RW3 source chunks, BrainFlow, LSL, PyXDF, sockets, streams, boards, devices,
  or hardware.

Every execution authorization field is false. The base dependency list is
unchanged; NumPy and SciPy remain optional.

## Frozen Provenance

### Official public reference

The official Brain2Qwerty repository is bound at commit
`3bf5a4099ca0d23bbe994b2287905760236e56e0`. The public paper says the MEG
preprocessing was offline. Its config records 0.5-45 Hz, 50 Hz notch, 100 Hz,
per-recording robust scaling, and clamp 5. The public model file receives a
complete sentence tensor and exposes no streaming state or causal attention
mask in that file.

Loop 25 preserves those facts as provenance. It does not call the new path an
official reproduction or assume the unreleased EnglishBCBL dataset.

### Local source bindings

| Path | Git blob at parent | SHA-256 at parent |
|---|---|---|
| `src/neurodecodekit/preprocess/sentence_extraction.py` | `8a2f64de3d24a462ef4e66b4894daac690091c62` | `da2b51853e1c0bc1c0d8e6263b268b346fe7711a471dc361b44897e6a5af639b` |
| `src/neurodecodekit/preprocess/fif_mat_extraction.py` | `63d361fe4ccb92b3650d3730a9f762917cefc1ea` | `ac97eca1192c0601ea1fbb2e732d18354322be477942d1ed27e6e1df4841f58d` |
| `src/neurodecodekit/preprocess/brainvision_extraction.py` | `ee19bb28c8cd499f7774fcd89b08be86e2937e0b` | `6aa8fcfff84a165cd88432bfd27ced3bab36af254261b28642ae12d9529ef7e9` |
| `src/neurodecodekit/cache/neurotoken_stream.py` | `735ea4c1cf9468e52591921fc4f1dedac8a3ce22` | `d8c9cd1104c2fa21f0d74b2b25a1e6e6942fa180bc7a57204f2d9182d6b29be0` |
| `src/neurodecodekit/experiments/causal_replay_gate.py` | `c96ecde60d2ca473e5c34f2fa7db84ff6278c5ed` | `a55156af95f7b6521d1e30e08ae2191efb68d4d4e208c1d277f85d7a613160fd` |

Any drift in these files before a future registered run requires an explicit
amendment. Loop 25 may add new modules after authorization; it may not silently
rewrite the offline extraction semantics to make an audit pass.

## Exact Planned Pipeline

```text
input: contiguous float32 [5, time] at exactly 1,000 Hz

1. validate finite values, shape, dtype, and expected absolute source index
2. cast the incoming chunk once to float64
3. apply stateful 50 Hz notch SOS
4. apply stateful fourth-order 0.5-45 Hz Butterworth bandpass SOS
5. keep filtered global source indices 0, 10, 20, ...
6. apply contract-frozen center and scale per channel
7. clamp to [-5, +5]
8. cast once to float32
9. emit values, absolute source indices, and float64 timestamps at 100 Hz
```

### Filter design

| Component | Frozen design |
|---|---|
| Notch | `scipy.signal.iirnotch(50.0, Q=30.0, fs=1000.0)` then `tf2sos` |
| Bandpass | `scipy.signal.butter(4, [0.5, 45.0], btype="bandpass", fs=1000.0, output="sos")` |
| Application | `scipy.signal.sosfilt`, float64 compute and state |
| Initial state | combined `sosfilt_zi` step-steady-state scaled by each channel's first source sample |
| Phase | forward only; no backward pass, centering, or delay compensation |

Coefficient generation occurs once after development seed 2501 opens and is
immediately hash-bound. The order, cutoffs, Q, API, dtype, initial-state rule,
and acceptance thresholds cannot change after development opens.

### Decimation and timing

- Source sampling rate is exactly 1,000 Hz.
- Output sampling rate is exactly 100 Hz.
- The global decimation phase is anchored at absolute source sample zero.
- Kept source indices are `0, 10, 20, ...` below the true input length.
- Output count is `floor((input_length - 1) / 10) + 1` for a nonempty item.
- Timestamp is `source_start_sec + source_index / 1000`.
- Timestamp tolerance is `1e-12` seconds.
- No interpolation, phase recentering, padding, or tail completion is allowed.

Rates not exactly 1,000 Hz are refused in v0. This is a scope boundary, not a
claim that 1,000 Hz is universally best or that home EEG devices are supported.

### Frozen normalization

```text
center = [-0.25, -0.125, 0.0, 0.125, 0.25]
scale  = [ 0.75,  0.875, 1.0, 1.125, 1.25]
clamp  = [-5.0, +5.0]
```

These constants are deliberately nontrivial and independent of both fixture
partitions, targets, and model output. Loop 25 permits no statistics fit.

## Mutable State

The future state schema stores:

- contract and pipeline hashes;
- source start sample;
- source samples seen and output samples emitted;
- SOS coefficient hash;
- float64 filter delays shaped `[channels, sos_sections, 2]`;
- initialized and closed flags.

The semantic state hash must be deterministic. State is limited to 4,096 bytes.
A changed configuration, source start, coefficient hash, shape, dtype, or
nonfinite delay is refused. A resumed stream must match uninterrupted output,
indices, timestamps, flush summary, and final semantic state hash.

## Fresh Target-Free Fixture

The future fixture schema is `b2q-causal-preprocessing-fixture` version 0. It
contains only:

```text
signals:               float32 [items, 5, time]
input_lengths:         int [items]
item_ids:              string [items]
source_start_samples:  int64 [items]
metadata:              JSON scalar
```

Forbidden members include targets, target lengths, token IDs, labels, frame or
sample labels, text, predictions, participant/subject/session identity,
recording paths, model outputs, and checkpoints.

| Partition | Seed | Items | Role |
|---|---:|---:|---|
| development | 2501 | 12 | implementation and complete gate development |
| qualification | 2502 | 12 | one-time confirmation after every development gate passes |

The partitions are separate physical files with disjoint item IDs. Lengths are
exactly 1,024 through 4,096 samples at the 12 registered values. Each partition
contains two rows from each family:

1. bounded passband/stopband multisine;
2. bounded linear chirp;
3. bounded interior/boundary impulse;
4. bounded step and plateau;
5. bounded drift and piecewise ramp;
6. bounded seeded noise with an outlier.

All values are finite float32 in `[-4, 4]`. These are numerical stress signals,
not simulated neural recordings. No expected output or model-derived value can
create or select a row.

## Exact Chunk Schedules

Every item must run through all seven schedules:

| ID | Rule |
|---|---|
| `whole_item` | all remaining samples |
| `single_sample` | repeat 1 |
| `fixed_seven` | repeat 7 |
| `decimation_boundaries` | cycle 9, 1, 10, 11, 19, 20 |
| `frame_boundaries` | cycle 15, 1, 4, 16, 3, 64 |
| `powers_of_two` | cycle 1, 2, 4, 8, 16, 32, 64, 128 |
| `seeded_irregular` | uniform integers 1-257 with seed 2511 |

The whole-item call is the canonical **causal** path. It is not the official
zero-phase reference. All other schedules must match it bitwise on the
registered host and within `atol=rtol=1e-6` across supported environments.

## Resume And Future-Mutation Controls

State export/import is tested after source samples:

```text
1, 9, 10, 15, 16, 159, 160, 161, 511, 997
```

At each cut, resumed output after the cut and final state must match one
uninterrupted run exactly.

Future mutation cuts are:

```text
160, 512, 1000
```

For each cut, two inputs are identical before the cut and differ only after it.
Every emitted value and state attributable to samples before the mutation must
remain bitwise identical. This is a direct causality test, not merely a declared
`causal=True` field.

## Frequency And Time-Domain Gate

The pipeline must pass all of these before schedule replay can qualify:

- every pole magnitude is strictly below 1;
- DC gain is at most -20 dB;
- gain at 5, 10, 20, and 35 Hz is between -3 and +0.5 dB;
- gain at 50 Hz is at most -20 dB;
- gain at 60 Hz is at most -6 dB;
- the impulse response and all fixture outputs are finite;
- frequency-dependent phase delay is measured and reported.

The filter's phase delay is not one scalar latency and cannot be called
capture-to-text or user-perceived latency. A failed frequency gate parks this
design; it does not permit changing the order, Q, cutoff, or threshold after
development data opens.

## Exact Access Sequence

1. Validate contract, source bindings, and environment without importing a
   filter implementation, designing coefficients, or opening fixture arrays.
2. Inspect the manifest without opening either partition.
3. Open development seed 2501 once.
4. Generate the exact registered coefficients once.
5. Freeze and hash coefficients, pipeline configuration, and state schema.
6. Run development causality, replay, resume, future-mutation, frequency,
   timing, normalization, flush, resource, and access gates.
7. Freeze and hash the development report.
8. Open qualification seed 2502 once only if every development gate passed.
9. Run the unchanged complete gate once on qualification.
10. Freeze the final proceed or park decision.
11. Write artifacts without reopening a partition.
12. Strictly inspect artifacts without data, target, model, network, or RW3
    access.

If development fails, qualification remains physically unopened. A failure is
not permission to tune and rerun seed 2501.

## Exact Acceptance Decision

Loop 25 proceeds only when all of these are true on both partitions:

- zero declared and empirically tested right context;
- all seven schedule outputs, indices, timestamps, flush summaries, and final
  state identities pass;
- all ten resume cuts pass;
- all three future-mutation cuts pass;
- filter stability and frequency-response gates pass;
- decimation count, phase, and timestamp formulas pass;
- frozen normalization and clamp gates pass with zero fit operations;
- no padding, invented sample, interpolation, silent reset, gap repair, or
  overlap repair occurs;
- every resource, privacy, access, provenance, artifact, and refusal gate
  passes.

Success decision:

```text
loop25_causal_preprocessing_mechanics_passed_ready_for_separate_loop26_decision
```

Failure decision:

```text
park_loop25_and_block_loop26_real_model_gate
```

Even a pass does not authorize Loop 26. A Loop 26 real-cache, target, model,
training, and validation packet remains a separate decision.

## Resource Caps

| Resource | Cap |
|---|---:|
| Numerical threads / concurrent workers | 1 / 1 |
| Items per partition | 12 |
| Channels | 5 |
| Source samples per item | 4,096 |
| Source values per partition | 245,760 |
| Complete fixture | 4 MiB |
| Materialized working arrays | 16 MiB |
| Mutable state | 4 KiB |
| One report | 1 MiB |
| All generated artifacts | 8 MiB |
| Internal runtime | 45 sec |
| Peak RSS | 1 GiB |
| Network, real/consumed/cache/target/checkpoint/model/training/RW3/device ops | 0 |

Every stage reports input/output bytes, runtime, peak RSS, state bytes, input
and output shape, valid sample counts, output rate, right context, filter delay
diagnostics, warnings, unavailable fields, and all 21 access counters.

## Refusal Surface

The machine contract freezes 40 refusal IDs covering:

- missing authorization, contract/source/config drift, and unsupported APIs;
- unsafe paths, output collisions, partition overlap, forbidden members, or
  target/model-derived fixture rows;
- wrong seeds, shapes, rates, channels, lengths, dtype, finite/value bounds;
- empty/oversized chunks and source gap/overlap/duplicate/reorder;
- filter instability, noncausal phase, state tamper, configuration mismatch,
  silent reset, or decimation-phase drift;
- timestamp, normalization, output, replay, future-mutation, resume, and flush
  failures;
- premature qualification, resource overflow, or forbidden access.

Refusals are deterministic report outcomes. The implementation may not catch a
failure and continue with a fallback transform.

## Planned Implementation After Authorization

No file below exists at this preregistration milestone:

```text
src/neurodecodekit/preprocess/causal_preprocessing.py
src/neurodecodekit/training/causal_preprocessing_fixture.py
src/neurodecodekit/experiments/causal_preprocessing_gate.py
tests/test_causal_preprocessing.py
tests/test_causal_preprocessing_fixture.py
tests/test_causal_preprocessing_gate.py
```

Planned CLI names are frozen but do not exist:

```text
make-causal-preprocessing-fixture
inspect-causal-preprocessing-fixture
causal-preprocessing-gate
inspect-causal-preprocessing-report
```

Implementation can begin only after the preregistration commit and a separate
authorization-only commit are each tested, pushed, and remotely green.

## Claim Boundary

A future pass may establish only that one target-free, 1,000-to-100 Hz causal
preprocessing implementation preserves its own registered outputs, timing, and
state across chunking and resume while passing synthetic frequency and resource
gates.

It cannot establish official offline equivalence, retained neural information,
real-data quality, CER/WER improvement, model or decoder causality, sentence
endpointing, end-to-end latency, arbitrary-rate or portable-device support,
EEG/MEG/OPM equivalence, unseen-person generalization, arbitrary-thought
decoding, assistive efficacy, diagnosis, or clinical utility.
