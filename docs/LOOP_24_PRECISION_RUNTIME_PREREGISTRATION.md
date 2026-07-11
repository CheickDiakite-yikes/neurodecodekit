# Loop 24 Local Precision And Runtime Preregistration

Date: 2026-07-11

Status: **Frozen before implementation; execution is not authorized**

Machine contract: `registries/local_precision_runtime_contract.v0.json`

Primary-source research: `docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md`

Preregistration parent commit: `8190f86`

Contract SHA-256:
`58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d`

Proof posture: target-free synthetic local-runtime protocol only

## Decision Requested After This Preregistration

This document does not authorize implementation. To authorize only Loop 24 as
scoped here, use this sentence:

> Authorize Loop 24 implementation exactly as scoped in
> `docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md`. Do not authorize RW3
> Stage A, data access, or model training.

To hold it, use:

> Hold Loop 24 implementation. Keep every Loop 24 execution authorization flag
> false.

General continuation, approval of RW3 research, issue activity, silence, or a
request to improve local accessibility is not Loop 24 execution authorization.

## Question

Can either an explicit CPU float16 producer or a QNNPACK dynamic-qint8 producer
preserve every observable behavior of the frozen float32 synthetic causal
pipeline while delivering a material local resource advantage?

The question is deliberately narrower than "can Brain2Qwerty v2 run at home?"
It tests one measurement and deployment interface on one tiny synthetic model.
It does not test neural signal, text accuracy, a sensor, a person, or the full
Brain2Qwerty v2 architecture.

## Why Preregister Before Running

The model has only 1,130 parameters. Import cost, lazy initialization, Python
decoder work, thermal drift, thread pools, and timer overhead can swamp the
arithmetic under test. Float16 can reduce tensor bytes without using a faster
kernel. Dynamic int8 can store qint8 weights while accepting and returning
float32. A changed logit can leave the final string unchanged while destabilizing
the incremental prefix trace.

Without a frozen protocol, it would be easy to:

- keep whichever timing loop flatters a candidate;
- widen tolerances after seeing a disagreement;
- call storage reduction an inference speedup;
- call qint8 weights integer-only end-to-end execution;
- reuse consumed seed 2353 as a convenient test;
- hide an unsupported backend behind float32 fallback;
- turn a tiny synthetic benchmark into a home-device claim.

This preregistration removes those degrees of freedom.

## Authorization Boundary

Included now:

- primary-source research;
- one strict JSON contract;
- dependency-free invariant tests;
- source, checkpoint, scalar, decoder, candidate, fixture, benchmark, resource,
  access, refusal, and claim boundaries;
- synchronized documentation and tracker state after validation.

Not included now:

- a fixture generator or fixture files;
- a float16 or int8 candidate implementation;
- checkpoint loading or conversion;
- model inference, profiler, timing, energy, or qualification runs;
- CLI additions;
- target, label, text, real-data, or consumed-evidence access;
- training, calibration, parameter updates, architecture changes, or a larger
  model;
- any RW3 source chunk, fixture, socket, stream, board, XDF, or hardware work.

Every Loop 24 execution authorization field and every RW3 implementation flag
remain false.

## Frozen Reference

The registered result must start from the exact existing producer and decoder:

```text
producer:                           TinyCausalWindowEncoder
device:                             CPU
input geometry:                     5 channels x 16 samples = 80 values
hidden / embedding / classes:       12 / 8 / 6
trainable parameters:               1,130
encoder / probe parameters:         1,076 / 54
float32 parameter bytes:            4,520
model plus normalization bytes:     4,560
checkpoint SHA-256:                 75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
parameter payload SHA-256:          d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
model config SHA-256:               8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2
blank intercept:                    5.130175197684084 float64
blank payload SHA-256:              10ed3f4fd2bf29841aebe31b81d7726910361df5ecc10a2c29ae7de4563d174f
blank config SHA-256:               43de56b1d275c0fd5b08a92d9dabc6893f7fe7ee49e02195623f6d61caa57e47
decoder config SHA-256:             3a70a3e7890487eb8a1d5c871eb8540e8265ea524a62a5d3be8c5ac55f760544
prefix beam / max prefix / blank:   8 / 12 / 0
log-softmax and beam scores:        float64
language model / lexicon:           none / none
producer right context:             0 samples
```

Five implementation files are bound to their Git blob and SHA-256 values in the
machine contract. Any pre-run drift requires a new preregistration amendment;
the gate may not silently benchmark changed code.

The future gate may read the frozen Loop 22 checkpoint after authorization. It
may use the documented Loop 23.5 blank scalar. It must not open any Loop 22/23/
23.5 test partition, the Loop 23.5 report, seed 2203, seed 2303, seed 2353, S7,
S21, a real cache, or a recording.

## Exact Candidate Set

### 1. Float32 eager reference

`float32_eager_reference` is not selectable. It establishes behavior and local
resource ratios.

- CPU eager execution;
- explicit float32 normalization, Linear weights, biases, input, GELU,
  embeddings, and logits;
- one float32-to-float64 cast before the unchanged decoder;
- `model.eval()` and `torch.inference_mode()`;
- no autocast, compile, accelerator, or fallback.

An untimed pass through the existing frozen path must match the benchmark
wrapper exactly before any candidate is compared.

### 2. Explicit float16 CPU

`float16_eager_cpu` is a selectable candidate.

- clone the frozen model once;
- explicitly cast all three Linear weights and biases to CPU float16;
- normalize each frame in float32, then cast it once to float16;
- run both GELUs and all Linear outputs in float16;
- cast final producer logits once to float32, then use the unchanged float64
  decoder;
- use no CPU autocast and no bfloat16;
- report hardware accumulation dtype as unavailable unless it can be proven.

If any operation is unsupported, nonfinite, or silently executes through a
different registered dtype contract, the candidate is unavailable or fails. It
may not substitute autocast or float32.

### 3. Dynamic qint8 QNNPACK

`dynamic_qint8_qnnpack` is a selectable, version-bound candidate.

- use installed PyTorch 2.13.0 only for the registered local run;
- set `torch.backends.quantized.engine` to `qnnpack` explicitly before
  conversion;
- call `torch.ao.quantization.quantize_dynamic` on all and only the three
  `torch.nn.Linear` modules with qint8;
- require all three resulting modules to be
  `torch.ao.nn.quantized.dynamic.Linear`;
- require qint8 packed weights and float32 module inputs/outputs;
- keep GELU, normalization, returned logits, and the decoder interfaces float32
  or float64 exactly as registered;
- collect one untimed CPU profiler trace and require an operator containing
  `quantized::linear_dynamic`;
- record the PyTorch migration warning.

If QNNPACK, the API, module conversion, packed dtype, or profiler operator is
unavailable, record `unavailable_no_fallback`. Do not install torchao, compile
the model, fake quantize, hand-roll int8, or use another backend.

## Excluded Candidates

This gate does not include bfloat16, autocast, static quantization, QAT,
torchao, `torch.compile`, TorchScript, ONNX Runtime, Core ML, ExecuTorch, MPS,
pruning, batching, architecture changes, or a larger model.

The exclusions do not mean those paths are bad. They mean each changes another
variable and needs its own protocol after this gate answers the smaller
question.

## Fresh Target-Free Fixture

The future fixture schema is `b2q-local-precision-runtime-fixture` version 0.
It stores only:

```text
signals:        float32 [items, 5, time]
input_lengths:  integer [items]
item_ids:       string [items]
metadata:       JSON scalar
```

It must not contain targets, target lengths, token IDs, labels, frame labels,
sample labels, text, predictions, participant identity, or recording paths.

Two physical input-only partitions are frozen before generator code:

| Partition | Seed | Items | Use |
|---|---:|---:|---|
| selection | 2401 | 48 | candidate availability, correctness, and selection |
| qualification | 2402 | 48 | one-time confirmation of one frozen replacement candidate |

Each partition contains eight items from each of six bounded numerical
families:

1. sinusoid mixtures;
2. linear chirps;
3. impulse trains;
4. piecewise ramps;
5. piecewise constants;
6. seeded Gaussian mixtures.

Values are finite float32 in `[-4, 4]`; lengths range from 64 through 128 in
multiples of four. Fixture generation is independent of model output. These are
numeric stress signals, not simulated brain recordings.

Manifest inspection may validate relative paths, shapes, bytes, seeds, family
counts, item IDs, and hashes without opening either signal array. Selection and
qualification item IDs must be disjoint.

## Exact Access Sequence

The registered implementation must record these events in order:

1. validate contract and environment without checkpoint or fixture arrays;
2. inspect the manifest without array members;
3. validate and load the exact frozen checkpoint once;
4. open the selection input-only partition once;
5. construct each candidate once without training or parameter updates;
6. run untimed reference-repeat and candidate correctness checks;
7. run untimed profiler provenance checks;
8. run 12 balanced selection timing rounds in fresh sequential workers;
9. freeze and hash the selection report and candidate decision;
10. open qualification once only if a nonreference replacement candidate was
    selected;
11. compare only float32 and the frozen selected candidate on qualification;
12. write reports without reopening a partition.

If no replacement candidate is selected, qualification remains physically
unopened. A storage-only candidate does not consume qualification because it
cannot replace the default in this gate.

## Behavioral Correctness Gate

The float32 reference runs three untimed replays. On the registered host its
payload hashes must be bitwise exact across repeats.

Every available candidate must match the float32 reference exactly for every
item and frame:

- item IDs and lengths;
- frame counts, start/end samples, and token timestamps;
- embedding and logit shapes;
- greedy path class at each frame;
- greedy partial hypothesis at each frame;
- top prefix-beam hypothesis at each frame;
- greedy and prefix final hypotheses;
- flush behavior;
- zero right context;
- warnings and access ledger.

All inputs, embeddings, logits, blank margins, log probabilities, and beam
scores must be finite.

The frozen numerical diagnostics are:

| Quantity | Threshold against float32 |
|---|---:|
| Embedding maximum absolute error | <= 0.10 |
| Embedding relative RMSE | <= 0.02 |
| Embedding cosine similarity | >= 0.995 |
| Logit maximum absolute error | <= 0.10 |
| Logit relative RMSE | <= 0.02 |
| Blank-margin maximum absolute error | <= 0.15 |
| Log-probability maximum absolute error | <= 0.15 |

Relative RMSE uses a denominator floor of `1e-12`. Exact observable behavior is
the primary gate; passing numerical thresholds cannot excuse a changed prefix
or final output.

Cosine similarity uses a norm floor of `1e-12`. If both vectors are below that
floor, similarity is `1.0` only when maximum absolute error also passes. If only
one vector is below the floor, similarity is `0.0`.

Candidates, fixture rows, and thresholds cannot change after selection opens.

## Timing Protocol

All candidates use CPU, `model.eval()`, `torch.inference_mode()`, one intra-op
thread, one inter-op thread, and these environment values:

```text
OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
```

Steady-state measurement uses
`torch.utils.benchmark.Timer.adaptive_autorange` with:

```text
IQR / median stop threshold:   0.10
minimum run time:              0.05 sec
maximum run time:              0.25 sec
Timer threads:                 1
selection rounds:              12
```

The six candidate permutations are executed twice. Each candidate-round runs
in a fresh child process, with at most one worker alive at a time. This gives
each candidate every order position four times.

The same round worker records imported-empty RSS, candidate construction, and
first-frame time before warmup; those measurements do not spawn extra workers.

Three paths are measured separately:

1. producer frame normalization, encode, and probe;
2. unchanged float64 decoder frame update;
3. full incremental frame pipeline.

Report I/O, candidate construction, process startup, and profiler overhead are
excluded from steady-state timing. Checkpoint validation/candidate construction
and first-frame time are reported separately.

For each path and candidate, report median, p25, p75, p95, IQR/median,
nanoseconds per frame, paired ratio to same-round float32, a 2,000-resample
paired 95% interval using seed 2404, and compute real-time factor against the
synthetic signal duration.

Qualification, if opened, uses six alternating reference/selected order rounds.
It cannot select a different candidate or change a threshold.

## Storage And Memory Accounting

Report these as separate quantities:

- logical parameter count;
- raw tensor payload bytes by dtype;
- deterministic serialized numeric payload bytes;
- source checkpoint bytes;
- candidate construction temporary bytes;
- absolute worker peak RSS;
- imported-empty-worker peak RSS;
- worker peak-RSS delta;
- mutable encoder and decoder state;
- working arrays;
- report and total generated bytes.

The deterministic numeric payload is an inspectable comparison artifact. It is
not called a deployable package unless a later packaging gate proves that.

Storage reduction is not runtime reduction. Tensor dtype is not hardware
accumulation proof. Framework RSS is not model-weight size.

## Energy Proxy

Energy is unavailable by default and is not a pass/fail field. The gate must not
prompt for `sudo`.

If the user separately supplies an already authorized noninteractive
`powermetrics` path, the optional workload must last at least ten seconds per
balanced candidate measurement and report command, sampler, duration, ambient
caveats, and every unavailable field. The result is a rough within-device
optimization proxy only. It cannot compare devices or select a candidate by
itself. This separately authorized measurement is outside the primary
60-second gate cap.

## Selection Rules

A candidate is ineligible if provenance, behavior, numerical, causality,
resource, or access gates fail. An unsupported candidate is recorded as
`unavailable_no_fallback`; that does not make the other candidates fail.

Float32 remains the default unless one candidate passes selection and
qualification and satisfies all replacement thresholds:

```text
producer median latency ratio:                 <= 0.80
full-pipeline median latency ratio:            <= 0.90
full-pipeline p95 latency ratio:               <= 0.95
full-pipeline paired ratio 95% upper bound:    <= 0.98
serialized numeric payload ratio:              <= 1.00
worker peak-RSS delta over float32:             <= 32 MiB
```

A candidate may be labeled storage-only when it passes correctness and:

```text
serialized payload ratio:             <= 0.50
absolute payload savings:             >= 2,048 bytes
full-pipeline median/p95 ratio:        <= 1.05 / 1.05
```

Storage-only status does not replace float32 and does not open qualification.

If multiple candidates satisfy replacement rules, rank them by:

1. lowest full-pipeline p95 ratio;
2. lowest full-pipeline median ratio;
3. lowest producer-only median ratio;
4. lowest serialized numeric payload bytes;
5. candidate ID.

Qualification failure retains float32 and rejects the candidate. No material
candidate retains float32 with decision `retain_float32_no_material_gain`.

## Resource Caps

```text
CPU / inter-op threads:              1 / 1
concurrent workers:                  1
worker processes spawned:            <= 48
fixture files / bytes:               <= 3 / 512 KiB
checkpoint bytes:                    <= 64 KiB
candidate serialized bytes each:     <= 64 KiB
working arrays:                      <= 32 MiB
reports:                             <= 1 MiB
all generated artifacts:             <= 4 MiB
internal runtime:                    <= 60 sec
peak RSS per worker:                 <= 1 GiB
external network calls:              0
real-data reads:                     0
consumed-evidence reads:             0
target/label/text reads:             0
training runs / parameter updates:   0 / 0
RW3 operations:                      0
```

Generated files must stay under ignored `cache/`, `outputs/`, or
`.codex_work/` roots. No fixture, candidate payload, timing report, checkpoint,
recording, or consumed artifact enters Git.

## Required Reports

The future gate must write deterministic JSON, Markdown, and measured audit
artifacts containing:

- contract, source, checkpoint, scalar, decoder, fixture, and environment
  identities;
- candidate availability and exact conversion provenance;
- every dtype, module class, packed-weight scheme, scale/zero-point summary,
  and profiler operator;
- exact behavior and numerical comparisons;
- raw timing measurements and aggregate statistics;
- storage, state, working bytes, RSS, runtime, and output bytes;
- access counters and ordered events;
- producer causality and required context;
- energy status;
- every warning and unavailable field;
- selection, qualification, and final decision;
- claim boundary.

Reports must not contain fixture waveform values, model weights, target-like
content, absolute private paths, hostnames, user names, IP addresses, or raw
profiler traces.

## Planned Implementation Surface

Only after explicit authorization may a future implementation add:

```text
src/neurodecodekit/training/precision_runtime_fixture.py
src/neurodecodekit/models/precision_candidates.py
src/neurodecodekit/experiments/local_precision_runtime_gate.py
tests/test_precision_runtime_fixture.py
tests/test_precision_candidates.py
tests/test_local_precision_runtime_gate.py
docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md
```

Planned CLI commands:

```text
neurodecode make-precision-runtime-fixture
neurodecode inspect-precision-runtime-fixture
neurodecode local-precision-runtime-gate
neurodecode inspect-local-precision-runtime-report
```

No new base or optional dependency is authorized. Unit tests must use tiny
generated mechanics and fakes; the registered selection and qualification
partitions remain unopened until the authorized execution sequence.

## Acceptance Gates

Loop 24 may be called complete only if:

1. implementation began only after a separate authorization commit;
2. source, checkpoint, scalar, decoder, contract, and environment identities
   match;
3. fixture generation is deterministic, target-free, physically split, and
   under caps;
4. selection/qualification access order is exact;
5. all three candidate statuses are explicit, with no fallback;
6. available candidates pass every behavior and numerical gate or are rejected;
7. timing uses the frozen 12-round balanced protocol and raw measurements;
8. storage, runtime, decoder time, RSS, state, energy, and unavailable fields
   stay separate;
9. float32 changes only after a material selection and one-time qualification
   pass;
10. every refusal, collision, tamper, privacy, cap, and determinism test passes;
11. focused and complete tests, Ruff, compileall, links, CLI help, Gitleaks, and
    `git diff --check` pass;
12. docs, tracker, workbook, and PR report the exact measured result;
13. no data, consumed evidence, target, training, RW3, real-time, device, or
    scientific boundary is crossed.

## Proceed, Park, And Kill Rules

**Proceed with replacement:** one candidate passes all selection and
qualification correctness/resource thresholds and the material runtime rule.
Replace only this tiny synthetic pipeline's local default in a later commit.

**Record storage-only:** a candidate halves numeric payload under the no-slowdown
rule but does not meet runtime replacement thresholds. Keep float32 default.

**Retain float32:** no candidate demonstrates a material reliable advantage.
This is a successful negative optimization result, not a reason to tune the
gate.

**Park:** the registered backend or profiler mechanic is unavailable, but the
gate fails closed and records exact platform evidence.

**Kill:** any candidate silently falls back, changes observable behavior,
opens forbidden evidence, trains or updates parameters, changes thresholds
after selection, violates privacy/resources, or is presented as neural or
home-device evidence.

## Current Decision

```text
research:                        complete for preregistration
contract:                        written
implementation authorized:      false
fixture generation:             absent and unauthorized
checkpoint reads:               0
candidate conversions:          0
model inference runs:           0
training / parameter updates:   0 / 0
target / consumed / real reads: 0 / 0 / 0
RW3 operations:                 0
next action:                    explicit Loop 24 implementation decision
```

## Claim Boundary

**Engineering capability this preregistration prepares:** a future bounded gate
can compare behavior, numerical drift, storage, memory, and steady-state CPU
runtime for three exact execution paths around one frozen synthetic causal
pipeline.

**Scientific or decoding claim not established:** this preregistration creates
no runtime result and cannot establish neural information, better CER/WER,
Brain2Qwerty v2 reproduction, unseen-person transfer, real-time text latency,
portable sensing, at-home usefulness, energy efficiency, arbitrary-thought
decoding, assistive efficacy, diagnosis, or clinical utility.
