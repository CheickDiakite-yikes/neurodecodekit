# Loop 40 Primary-Source Research: Edge Runtime Packaging Gate

## Proof posture

Loop 40 planning research is complete while the experiment is `Not Started`.
No backend, target platform, target architecture, fixture, dependency, export,
conversion, package, inference, profiler, memory planner, delegate, simulator,
application, device, or hardware operation was authorized or run.

The maximum current claim is **no edge-package result**. This note defines how
one future target-free package could be evaluated without turning export
success into evidence of decoding, real-time behavior, or portable hardware.

## The local reference is not eligible yet

The only plausible frozen reference family is the Loop 22/24 float32 causal
producer and diagnostic motif probe:

| Property | Frozen value |
|---|---:|
| Parameters | 1,130 total; 1,076 encoder; 54 diagnostic probe |
| Registered float32 numeric payload | 5,210 bytes |
| Input | batch one, 5 channels by 16 samples, flattened to 80 features |
| Graph | Linear 80->12, GELU, Linear 12->8, GELU, Linear 8->6 |
| Producer | causal |
| Host normalization/state/timestamps/decoder in graph | no |

Loop 24 retained float32. Float16 preserved its registered behavior but was
`1.169950x` the float32 producer latency and `1.087904x` the full-pipeline
latency. Dynamic QNNPACK qint8 used `47.10%` of the float32 numeric payload but
changed behavior and was `2.784595x`/`1.812123x` the producer/full-pipeline
latency. The overall Loop 24 run parked after `65.154951` seconds exceeded its
60-second cap. Seed 2401 is consumed; seed 2402 stays unopened.

Loop 39 has defined, but not executed, the required cross-machine matrix. A
future Loop 40 package cannot qualify before the relevant matrix cells pass.
There is also no named target OS, architecture, ABI, or application envelope.
Those are blocking facts, not paperwork gaps.

## Primary-source findings

### ExecuTorch is the leading research candidate, not a selection

[ExecuTorch's overview](https://docs.pytorch.org/executorch/stable/intro-overview.html)
defines a PyTorch-native export and runtime stack for mobile, wearable,
embedded, and microcontroller targets. Its
[getting-started guide](https://docs.pytorch.org/executorch/stable/getting-started.html)
requires a PyTorch model, example inputs, and one or more named target hardware
backends; it identifies XNNPACK for Arm/x86 CPU and gives separate mobile
backend guidance.

This is a strong match to the source framework and the tiny Linear/GELU graph.
It is not evidence that the graph exports, delegates completely, runs faster,
or produces a smaller deployable application. The target must be named first.

ExecuTorch also provides useful future audit surfaces. Its
[memory-planning documentation](https://docs.pytorch.org/executorch/stable/compiler-memory-planning.html)
describes planning mutable tensor lifetimes into fixed arenas before program
emission. Its
[delegate model](https://docs.pytorch.org/executorch/stable/compiler-delegate-and-partitioner.html)
separates ahead-of-time preprocessing from runtime initialization and
execution. Its
[runtime overview](https://docs.pytorch.org/executorch/stable/runtime-overview.html)
separates PTE loading, instruction execution, memory, operator dispatch,
delegation, and optional profiling. Those surfaces make hidden fallback and
incomplete memory accounting testable in a future authorized run.

### ONNX Runtime Mobile is a serious cross-platform alternative

[ONNX Runtime Mobile](https://onnxruntime.ai/docs/tutorials/mobile/) requires an
ONNX model and provides CPU/XNNPACK plus platform-specific execution providers.
Its documentation warns that unsupported operators can partition a graph and
degrade performance. The
[ORT format](https://onnxruntime.ai/docs/performance/model-optimizations/ort-format-models.html)
supports reduced builds and emits a required-operator configuration, but adds
an ONNX-to-ORT conversion boundary and version compatibility obligations.

Its [fixed-shape helper](https://onnxruntime.ai/docs/tutorials/mobile/helpers/make-dynamic-shape-fixed.html)
notes that batch one can improve mobile provider eligibility. That fits the
canonical stream, but fixed shape is a contract choice that must be frozen and
tested, not inferred from one example.

### LiteRT is direct but still a conversion experiment

The official [PyTorch-to-LiteRT guide](https://developers.google.com/edge/litert/conversion/pytorch/overview)
requires a `torch.export`-compliant source and sample inputs, then compares
converted and PyTorch outputs. It is a credible future path. It still requires
an optional converter/runtime install, an operator audit, exact version pins,
and NeuroDecodeKit's stricter semantic, state, timestamp, fallback, byte, and
resource gates.

### Core ML is Apple-specific and has a dtype trap

[Core ML Tools](https://apple.github.io/coremltools/docs-guides/source/target-conversion-formats.html)
accepts TorchScript or `ExportedProgram` sources and recommends ML Program for
current Apple targets. It cannot establish cross-platform portability.

The [input/output contract](https://apple.github.io/coremltools/docs-guides/source/model-input-and-output-types.html)
requires an input shape for PyTorch conversion and documents float16 defaults
for newer ML Program deployment targets. Loop 24 retained float32, so a future
Core ML attempt must explicitly pin float32 or create a separately authorized,
preregistered dtype amendment. Silent conversion to float16 is a refusal.

## The package boundary has six layers

1. Frozen source graph and eager reference.
2. Exported graph, operators, shapes, dtypes, and lowering metadata.
3. Weights, biases, normalization constants, and hashes.
4. Runtime binary, kernels, delegates, build flags, and linkage.
5. Host normalization, causal state, timestamps, schedule, decoder, and gaps.
6. Named OS/architecture/ABI plus simulator, app, or device envelope.

The torch module covers only part of layers 1-3. A graph parity result cannot
stand in for host state/timestamp parity or end-to-end pipeline behavior.

## Frozen future decision

Four alternatives remain visible: ExecuTorch/XNNPACK, ONNX Runtime
Mobile/CPU-or-XNNPACK, LiteRT Torch, and Core ML ML Program. ExecuTorch/XNNPACK
is the **leading future research candidate only** because it keeps the source
path PyTorch-native and exposes the audit tools this project needs. No backend
is selected until all of these exist:

- a named target OS, version, architecture, ABI, and minimum deployment target;
- the relevant successful Loop 39 matrix cells;
- one separately committed preregistration and authorization per stage;
- exact exporter/runtime/delegate versions and package layers;
- a target-free fixture frozen before package outputs open;
- a deployment-benefit rule over complete relevant bytes and resources.

## Future stages

| Stage | Work | Maximum claim |
|---|---|---|
| A | Static target, source, export, operator, dtype, and shape decision | One path is statically eligible |
| B | Local target-free export and eager/package parity | One package preserves registered behavior on one qualified host |
| C | Relevant Loop 39 package matrix | One package preserves behavior across the registered cells |
| D | Named simulator or application envelope | One exact envelope preserves behavior and measured resources |

Every stage needs a separate decision. Physical-device qualification belongs
to Loop 42, not Loop 40.

## Acceptance and stop rules

The machine contract freezes 7 qualification levels, 6 package layers, 4
backend profiles, 20 identity fields, 8 output classes, 6 comparison classes,
24 fixture families, 4 stages, 30 gates, 40 refusals, and 40 false execution
authorizations.

A future package passes only if semantic behavior, numerical policy, state,
timestamps, provenance, delegation/fallback accounting, byte accounting, and a
preregistered deployment benefit all pass within one backend, one thread, one
worker, 60 seconds per measurement worker, 1 GiB RSS, and 32 MiB generated
package/report bytes.

Park immediately if export requires retraining, an architecture/checkpoint
change, hidden fallback, post-hoc tolerance, unregistered dtype conversion,
more resources without benefit, or tuning on the same fixture. Model bytes
alone are not deployment size; startup is not steady-state latency; simulator
execution is not physical-device qualification.

## Measured research access

| Counter | Value |
|---|---:|
| Public web operations | 3 |
| Official/primary pages opened | 12 |
| Generated experiment bytes | 0 |
| Fixtures / installs / exports / packages | 0 / 0 / 0 / 0 |
| Eager/package inference and training runs | 0 / 0 / 0 |
| Real/cache/target reads | 0 / 0 / 0 |
| Simulator/device/hardware operations | 0 / 0 / 0 |
| End-to-end latency measured | no |

Public response bytes, web runtime, and web peak RSS are unavailable from the
research tool contract. Every other unavailable field remains explicit in the
machine boundary.

## Closeout

Engineering capability added: NeuroDecodeKit now has a machine-checkable,
target-aware decision boundary for comparing one future edge package against a
frozen float32 causal reference without hiding host state, fallback, or total
deployment cost.

Scientific claim not established: No package or inference ran, so this work
establishes no neural advantage, decoding accuracy, unseen-person
generalization, real-time capture-to-text latency, portable-hardware behavior,
or other scientific result.
