# Loop 24 Primary-Source Research: Local Precision And Runtime

Date: 2026-07-11

Status: **Research complete for preregistration; no candidate executed**

Evidence posture: public primary-source documentation plus local environment
metadata. No checkpoint, fixture array, target, consumed partition, model, or
training path was opened.

## Question

What is the smallest honest experiment that can determine whether the frozen
Loop 23.5 synthetic causal pipeline should keep float32 execution or use an
explicit float16 or dynamic-int8 CPU producer on one local machine?

This is a deployment-mechanics question. It is not a new decoding experiment,
an accuracy contest, or evidence that the tiny synthetic producer represents
Brain2Qwerty v2's scientific performance.

## Why This Gate Is Narrow

Brain2Qwerty v2 is not a tiny three-layer MLP. Its public paper describes a
spatial channel merger, a four-layer dilated convolutional encoder, temporal
downsampling, a four-layer Conformer, character CTC heads, word alignment, and
a neuro-conditioned 4B-parameter language model. The public project page also
states that practical accuracy and accessible sensing hardware remain open
challenges.

NeuroDecodeKit's frozen local reference has only 1,130 trainable parameters and
an eight-dimensional embedding. It is useful for testing the measurement and
deployment interface because it is causal and bounded. A speed or size result
on it cannot be extrapolated to the full Brain2Qwerty v2 system, a new person,
MEG acquisition, EEG, or a home device.

Primary sources:

- [Brain2Qwerty project page](https://facebookresearch.github.io/brain2qwerty/)
- [Brain2Qwerty v2 paper](https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf)
- [Brain2Qwerty v2 model configuration at the reviewed commit](https://github.com/facebookresearch/brain2qwerty/blob/3bf5a4099ca0d23bbe994b2287905760236e56e0/brain2qwerty_v2/config/model_config.py)

## Frozen Local Reference

Loop 24 must compare candidates against the already frozen behavior, not train
or recalibrate anything:

```text
producer:                       TinyCausalWindowEncoder
trainable parameters:           1,130
encoder / probe parameters:     1,076 / 54
checkpoint SHA-256:             75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1
parameter payload SHA-256:      d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98
model config SHA-256:           8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2
normalization:                  frozen float32 train-fit vectors
blank intercept:               5.130175197684084, frozen float64
blank payload SHA-256:          10ed3f4fd2bf29841aebe31b81d7726910361df5ecc10a2c29ae7de4563d174f
decoder config SHA-256:         3a70a3e7890487eb8a1d5c871eb8540e8265ea524a62a5d3be8c5ac55f760544
decoder:                        width-8 prefix CTC, float64 scores
language model / lexicon:       none / none
right context:                  0 samples
```

The producer contains exactly three `Linear` modules with GELU after the first
two. Loop 24 may change only those producer execution dtypes. Train-fit
normalization remains float32; the blank intercept, float64 log-softmax, CTC
state, beam width, tie ordering, and flush behavior remain unchanged.

Seed 2353 is consumed. Loop 24 may use the documented frozen scalar and hashes,
but it must not open the Loop 23.5 fixture, gate report, validation/test arrays,
targets, labels, or frame traces.

## Finding 1: Floating-Point Equivalence Is Behavioral, Not Bitwise By Default

PyTorch explicitly warns that mathematically equivalent floating-point
operations are not guaranteed to be bitwise identical across batched versus
slice execution, releases, platforms, or backends. Reduced precision also has
format range and accumulation details that can differ by kernel.

Loop 24 therefore needs two distinct gates:

1. exact application behavior: frame grids, timestamps, greedy paths, prefix
   traces, and final hypotheses;
2. bounded numerical drift: embeddings, logits, blank margins, and log
   probabilities.

Neither `allclose` alone nor an unchanged final string is sufficient.

Primary sources:

- [PyTorch numerical accuracy note](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html)
- [PyTorch floating-point type information](https://docs.pytorch.org/docs/stable/type_info.html)

## Finding 2: Float16 Tensor Dtype Does Not Prove Faster CPU Arithmetic

PyTorch exposes float16 tensors and `Linear` operations, but a tensor dtype does
not by itself prove the hardware accumulation dtype, kernel family, or speed.
The CPU autocast default is bfloat16 rather than float16, and autocast can mix
operator dtypes. That makes autocast a different experiment from an explicit
float16 producer.

The registered float16 candidate must therefore:

- cast all three `Linear` weights and biases to float16 explicitly;
- cast the already normalized frame to float16 exactly once;
- keep GELU and the three Linear outputs in float16;
- cast final producer logits once to float32 before the unchanged float64
  decoder;
- use no autocast and no silent float32 fallback;
- report hardware accumulation dtype as unavailable unless the backend can
  prove it.

The candidate can be unsupported or slower. That is a valid result.

Primary sources:

- [PyTorch automatic mixed precision](https://docs.pytorch.org/docs/stable/amp.html)
- [PyTorch Linear](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html)
- [PyTorch inference mode](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html)

## Finding 3: Dynamic Int8 Needs Backend And API Provenance

PyTorch's dynamic quantized `Linear` accepts floating-point input and returns
floating-point output while quantizing weights ahead of time and activations at
runtime. The older eager quantization surface remains documented, but PyTorch
now directs new quantization development toward torchao.

The local environment currently reports:

```text
PyTorch:                         2.13.0
torchao installed:              no
legacy quantize_dynamic:        available
supported quantized engines:    qnnpack only
current quantized engine:       none
```

Torchao's current ARM dynamic-int8 paths are described as experimental and its
published examples use `torch.compile` on large language models. Adding
torchao, compilation, or a second int8 implementation would confound this tiny
three-candidate gate.

The registered int8 candidate will use the already installed, version-bound
`torch.ao.quantization.quantize_dynamic` path with QNNPACK explicitly selected.
Every `Linear` must become a dynamic quantized module with qint8 packed weights,
and an untimed CPU profiler trace must contain the registered quantized Linear
operator. If the API or QNNPACK path is unavailable, the candidate is recorded
as unavailable. It may not fall back to float32, fake quantization, torchao,
manual NumPy int8, or another backend.

This is a local compatibility decision, not an endorsement of a deprecated API
for a future production product.

Primary sources:

- [PyTorch quantization migration notice](https://docs.pytorch.org/docs/stable/quantization.html)
- [PyTorch quantization API reference](https://docs.pytorch.org/docs/stable/quantization-support)
- [PyTorch dynamic quantization recipe](https://docs.pytorch.org/tutorials/recipes/recipes/dynamic_quantization.html)
- [Torchao quantization API](https://docs.pytorch.org/ao/stable/api_reference/api_ref_quantization.html)
- [Torchao quantized inference support](https://docs.pytorch.org/ao/stable/workflows/inference.html)

## Finding 4: Tiny Runtime Measurements Need Warmup And Replicates

For a 1,130-parameter model, process startup, lazy initialization, timer
overhead, thread pools, thermal state, and the Python decoder can be larger than
the producer work itself. A single wall-clock duration would be misleading.

PyTorch's benchmark `Timer` performs warmup, controls threadpool size, and
supports replicated adaptive measurement. Loop 24 should measure three paths
separately:

1. producer-only frame normalization, encoder, and probe;
2. fixed float64 blank/log-softmax/prefix-decoder work;
3. the full incremental frame pipeline.

Candidate order must be balanced across fresh processes. Process startup and
candidate construction are measured separately from steady-state inference.
All timing uses a monotonic high-resolution counter, one intra-op thread, one
inter-op thread, and the same item/frame schedule.

Primary sources:

- [PyTorch benchmark utilities](https://docs.pytorch.org/docs/stable/benchmark_utils.html)
- [PyTorch benchmark recipe](https://docs.pytorch.org/tutorials/recipes/recipes/benchmark.html)
- [PyTorch `set_num_threads`](https://docs.pytorch.org/docs/stable/generated/torch.set_num_threads.html)
- [PyTorch `set_num_interop_threads`](https://docs.pytorch.org/docs/stable/generated/torch.set_num_interop_threads.html)
- [PyTorch threading environment variables](https://docs.pytorch.org/docs/stable/threading_environment_variables.html)
- [Python `perf_counter_ns`](https://docs.python.org/3/library/time.html#time.perf_counter_ns)

## Finding 5: Storage, Memory, And Compute Are Different Claims

An int8 weight file can be smaller while the runtime still accepts and returns
float32 tensors. A float16 checkpoint can be half the parameter bytes while the
framework RSS remains unchanged. Neither observation proves lower latency or
lower energy.

Loop 24 must report separately:

- logical parameter count;
- raw tensor payload bytes by dtype;
- deterministic serialized numeric payload bytes;
- framework/process peak RSS and delta from an empty imported worker;
- producer-only and full-pipeline latency;
- real-time factor against synthetic signal duration;
- output behavior and numerical drift.

The candidate payload is an inspectable measurement artifact, not necessarily
a deployable package. Peak RSS must be measured in an isolated child because
`ru_maxrss` is a process high-water mark and its units are platform-dependent.

Primary source:

- [Python resource usage documentation](https://docs.python.org/3/library/resource.html)

## Finding 6: Mac Energy Is An Optional Within-Device Proxy

The local `powermetrics(1)` manual says its average power values are estimated,
may be inaccurate, must not be compared between devices, and can be used only
to help optimize one application. It also exposes a rough process-energy
impact number with platform-specific weighting.

Loop 24 will not request `sudo`, fail because power access is unavailable, or
select a candidate from energy alone. If the user separately supplies an
already authorized measurement path, the report may include a long-running,
balanced, within-machine energy proxy with the command, sampler, duration,
ambient caveats, and unavailable fields. Otherwise energy remains explicitly
unavailable.

Local primary source:

```text
man powermetrics
powermetrics --help
```

## Registered Candidate Set

| ID | Producer arithmetic | Decoder arithmetic | Why included |
|---|---|---|---|
| `float32_eager_reference` | explicit float32 Linear/GELU | unchanged float64 | frozen behavioral and timing reference |
| `float16_eager_cpu` | explicit float16 Linear/GELU, no autocast | unchanged float64 | tests whether half-size tensors help on this CPU without hidden mixed precision |
| `dynamic_qint8_qnnpack` | QNNPACK dynamic qint8 Linear, float32 interfaces/GELU | unchanged float64 | tests actual registered integer Linear operators without training |

The following are not candidates in this gate:

- bfloat16 or CPU autocast;
- static activation quantization or calibration;
- quantization-aware training;
- torchao, `torch.compile`, TorchScript, ONNX, Core ML, ExecuTorch, or MPS;
- weight pruning, architecture changes, batching, speculative decoding, or a
  larger model;
- any new endpoint, language-model, lexicon, or beam-search rule.

Each could become a later preregistered experiment. Adding one now would prevent
Loop 24 from answering its narrow question.

## Local Preregistration Snapshot

The snapshot establishes where a future registered result may apply. It does
not guarantee candidate support or performance.

```text
parent commit:                    8190f86
host model:                       Mac16,8
CPU:                              Apple M4 Pro, arm64, 12 physical/logical cores
memory:                           25,769,803,776 bytes
OS:                               macOS 26.6, build 25G5028f
Python:                           3.13.5
NumPy:                            2.5.0
PyTorch:                          2.13.0
PyTorch CPU flags observed:       fp16_arith, bf16, dot, i8mm, neon
free disk at research snapshot:   about 4.7 GiB
```

Hardware capability flags show that an instruction family is exposed to
PyTorch. They do not prove that this model invokes that instruction family.
The future profiler and timing gates must establish the executed path.

## Research Decision

Proceed to one preregistration-only commit for the three candidates above. Do
not implement or execute the gate from this research note.

The preregistration must freeze target-free fresh fixtures, source-code and
checkpoint identities, exact correctness checks, balanced timing rounds,
resource caps, selection and qualification order, unsupported-candidate
handling, and a default-retention rule. Float32 remains the default unless a
candidate passes every behavioral gate and demonstrates a material measured
advantage.

## Claim Boundary

**Engineering capability this research prepares:** a future bounded experiment
can determine whether one frozen synthetic causal producer has a behaviorally
equivalent and materially better local CPU execution path.

**Scientific or decoding claim not established:** this research does not show
neural information, better CER/WER, unseen-person transfer, real-time text,
Brain2Qwerty v2 parity, portable sensing, at-home usability, energy efficiency,
or clinical value.
