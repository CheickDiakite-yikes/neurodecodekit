# AGENTS.md — Codex / Agent Instructions

You are continuing **NeuroDecodeKit**, a research/build starter for making Brain2Qwerty-style neural language decoding accessible.

## Product principle

Keep the core loop brutally simple:

```text
manifest → selective download → tiny shard → event windows → baseline → CER/WER report → demo
```

Do not optimize for impressiveness before reproducibility. A boring baseline that everyone can run is more valuable than a clever architecture no one can validate.

## Hard constraints

1. **Do not download the full SpanishBCBL dataset by default.** It is roughly 262GB. All code must default to dry-run, listing, manifesting, or tiny selective patterns.
2. **Do not make clinical claims.** This is a research/dev kit for non-invasive decoding experiments, not a medical product.
3. **Respect CC BY-NC 4.0 constraints.** Treat the Brain2Qwerty code and SpanishBCBL data as noncommercial unless a separate license exists.
4. **Keep heavy dependencies optional.** The base repo should run tests without MNE, Torch, Zarr, or Hugging Face. Put heavy imports inside functions and raise helpful install messages.
5. **Prefer inspectable data formats.** Manifests should be JSONL/Parquet-friendly. Metadata should be easy to diff. Cache format should be chunked and compressed once Zarr is implemented.
6. **Measure complexity.** Every new pipeline stage should report storage footprint, runtime, and a human-readable summary.
7. **Avoid LLM-only illusions.** Always keep a language-model-only baseline so we do not accidentally credit the neural decoder for autocomplete.

## Immediate next task

The first 20-loop roadmap is complete except for the deliberately parked Loop
13 backend. Post-roadmap Loops 21 and 22 validate bounded synthetic causal
replay and one tiny learned motif encoder. Loop 23 implemented the frozen
language-model-free streaming CTC gate, but its consumed test reached only 5/8
exact sequences against the preregistered 6/8 threshold. It is parked, while
Loop 23.5 is complete as a separate supervised synthetic calibration gate.
Loop 24 is now preregistered at commit `186bb6f`, before any candidate,
fixture, checkpoint read, inference, timing, or qualification run:

```bash
cat docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md
cat docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md
python -m json.tool registries/local_precision_runtime_contract.v0.json >/dev/null
```

Its machine contract freezes three exact CPU candidates, fresh target-free
seeds 2401 and 2402, 12 balanced selection timing rounds, 30 refusal IDs, and
strict behavior/resource/claim gates. Every Loop 24 execution authorization
flag is false. The next Loop 24 decision is explicit authorization using the
exact sentence in the preregistration, an amendment, or a hold. General
continuation is not authorization.

The parallel practice track has closed RW1 and RW2 at their exact synthetic
proof boundaries. RW3's replay/live-source-equivalence protocol is frozen at
commit `c3d1f01`, before any adapter, source chunk, fixture, socket, board, or
XDF operation:

```bash
cat docs/RW3_PRIMARY_SOURCE_RESEARCH.md
cat docs/RW3_REPLAY_LIVE_EQUIVALENCE_PREREGISTRATION.md
cat docs/RW3_STAGE_A_AUTHORIZATION_PACKET.md
python -m json.tool registries/replay_equivalence_contract.v0.json >/dev/null
python -m json.tool registries/rw3_stage_a_authorization_request.v0.json >/dev/null
```

Commit `163ff2f` prepares a hash-bound Stage A authorization packet and machine
request. Both explicitly say `authorized_now: false`; preparing or reviewing
them is not authorization. RW3 Stage A and Loop 24 are two independent
decisions: authorizing one cannot authorize the other. Do not implement either
from this instruction. BrainFlow, LSL, PyXDF, sockets, live sources, device
discovery, hardware, real recordings, consumed caches, targets, models, and
training remain unauthorized. Keep S7/S21 evidence and seeds 2203, 2303, and
2353 frozen. Any future real-data acquisition remains dry-run by default and
requires explicit byte caps plus `--execute`.

## Acceptance criteria for next PR

- `python -m unittest discover -s tests` passes.
- CLI has useful `--help` text.
- New numerical or model dependencies remain optional.
- No full-dataset download can happen accidentally.
- The RW3 JSON contract, authorization request, and ten dependency-free
  invariant tests remain exact.
- The Loop 24 JSON contract and nine dependency-free invariants remain exact;
  all execution flags stay false unless the exact authorization decision is
  separately recorded, tested, committed, and pushed.
- No RW3 implementation, fixture, CLI, optional import, socket, stream, board,
  XDF operation, real-data read, target access, model run, or training run exists.
- No Loop 24 runtime module, fixture, CLI, checkpoint read, candidate
  conversion, inference, benchmark, profiler, energy measurement, target
  access, model training, or generated payload exists before authorization.
- All public docs agree that the registration freezes five schedules, 18 future
  fixture families, 30 refusal IDs, and four separately authorized stages, and
  that the Stage A packet proposes 90 future cases without authorizing them.
- Stage A remains a separate authorization decision and cannot imply Stage B-D,
  physical-device qualification, useful signal, decoding, or real-time behavior.
- Loop 24 remains a separate authorization decision and cannot establish a
  speedup, integer-only execution, retained neural accuracy, end-to-end text
  latency, cross-device energy efficiency, or portable-hardware behavior.
- Resource, privacy, access, timestamp, anomaly, hash, and claim boundaries stay
  explicit and machine-checkable.

## Style

- Small functions, explicit names, low magic.
- Use dataclasses for records.
- Use pathlib over string path manipulation.
- Pure-Python first; optional NumPy/MNE/Torch/Zarr only where needed.
- Include tests for each assumption about filenames, metrics, and shape transformations.
