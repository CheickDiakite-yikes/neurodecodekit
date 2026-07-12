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
Loop 24 was preregistered at commit `186bb6f`, before any candidate, fixture,
checkpoint read, inference, timing, or qualification run. The user's 2026-07-12
authorization is recorded conservatively as a target-free scope amendment:

```bash
cat docs/LOOP_24_PRIMARY_SOURCE_RESEARCH.md
cat docs/LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md
cat docs/LOOP_24_AUTHORIZATION_DECISION.md
python -m json.tool registries/local_precision_runtime_contract.v0.json >/dev/null
python -m json.tool registries/loop24_authorization_decision.v0.json >/dev/null
```

Its machine contract freezes three exact CPU candidates, fresh target-free
seeds 2401 and 2402, 12 balanced selection timing rounds, 30 refusal IDs, and
strict behavior/resource/claim gates. The immutable preregistration keeps every
authorization flag false; the separate hash-bound decision authorizes only the
registered target-free fixture, checkpoint, candidate, inference, selection,
conditional qualification, report, and CLI work after the authorization-only
commit is tested and pushed. Real or consumed data, targets, labels, text,
training, new architectures, energy measurement, RW3, devices, hardware, and
Loops 25-44 execution remain unauthorized. Do not begin Loop 24 implementation
until the authorization-only commit is pushed and its CI is confirmed.

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
decisions: authorizing one cannot authorize the other. Do not implement RW3
from this instruction. BrainFlow, LSL, PyXDF, sockets, live sources, device
discovery, hardware, real recordings, consumed caches, targets, and training
remain unauthorized. The only model operation authorized after the Loop 24
authorization commit is pushed is the frozen contract's target-free candidate
inference; no parameter update is allowed. Keep S7/S21 evidence and seeds 2203,
2303, and 2353 frozen. Any future real-data acquisition remains dry-run by
default and requires explicit byte caps plus `--execute`.

A primary-source-informed next tranche now defines Loops 25-44 in
`docs/LOOPS_25_44_ROADMAP.md` and
`registries/next_20_loops.v0.json`. It contains exactly 20 planning rows across
five phases, with detailed controls, metrics, stop rules, resource caps,
dependencies, and source bindings. Every row is `Not Started` and
`execution_authorized: false`. This roadmap does not change the immediate
decision order, authorize Loop 24 or RW3, or permit a Loop 25-44 fixture, data
read, model run, training run, stream, board, or hardware operation. A broad
request to continue toward Loop 44 is a goal, not a substitute for each frozen
authorization boundary.

## Acceptance criteria for next PR

- `python -m unittest discover -s tests` passes.
- CLI has useful `--help` text.
- New numerical or model dependencies remain optional.
- No full-dataset download can happen accidentally.
- The RW3 JSON contract, authorization request, and ten dependency-free
  invariant tests remain exact.
- The Loop 24 JSON contract and nine dependency-free invariants remain exact;
  its immutable execution flags remain false. The separate authorization
  decision and seven invariants must bind the exact contract hash, permit only
  the registered target-free work, and stay effective only after its own
  tested commit is pushed.
- The Loops 25-44 roadmap contains exact IDs 25 through 44, five phases of four
  loops, row-level primary-source bindings, nine dependency-free invariants,
  and 20 false execution flags.
- No RW3 implementation, fixture, CLI, optional import, socket, stream, board,
  XDF operation, real-data read, target access, model run, or training run exists.
- No Loop 24 runtime module, fixture, CLI, checkpoint read, candidate
  conversion, inference, benchmark, profiler, or generated payload exists
  before the authorization-only commit is pushed and CI is confirmed. Energy,
  target access, real or consumed data, and model training remain forbidden
  throughout Loop 24.
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
