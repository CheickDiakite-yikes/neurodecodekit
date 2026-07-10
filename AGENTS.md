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
13 backend. Post-roadmap Loops 21 and 22 have validated bounded synthetic
causal replay and one tiny learned motif encoder. Loop 23 is preregistered;
implement it with alternate seeds before creating its registered test:

```bash
cat docs/LOOP_22_TINY_CAUSAL_ENCODER.md
cat docs/LOOP_23_PREREGISTRATION.md
cat docs/POST_20_ROADMAP.md
```

Freeze the Loop 22 checkpoint, report, and consumed seed-2203 test. Preserve
the registered CTC blank/repeat handling, incremental greedy/prefix state,
partial hypotheses, revision counts, first/stable/final timing, controls, and
caps exactly. Implement and rehearse with alternate seeds, then commit before
creating the fresh seed-2303 test. Keep the decoder language-model-free and
both observed S21 MEG holdouts plus the S7 EEG result frozen. Any future
real-data acquisition remains dry-run by default and requires explicit byte
caps plus `--execute`.

## Acceptance criteria for next PR

- `python -m unittest discover -s tests` passes.
- CLI has useful `--help` text.
- New numerical or model dependencies remain optional.
- No full-dataset download can happen accidentally.
- The committed decoder protocol remains unchanged and the registered test is
  not generated before alternate-seed mechanics pass.
- Blank/repeat state and partial hypotheses cover multiple chunk boundaries
  and final partial chunks.
- Reports separate encoder availability, first/stable/final symbol emission,
  endpointing, rendering, and measured end-to-end latency.
- Runtime, peak memory, state bytes, and artifact bytes stay under explicit caps.
- Training/selection/test partitions, a new one-time test, and the no-signal
  comparator are explicit.
- Docs explain exactly what was verified and what remains synthetic or untested.

## Style

- Small functions, explicit names, low magic.
- Use dataclasses for records.
- Use pathlib over string path manipulation.
- Pure-Python first; optional NumPy/MNE/Torch/Zarr only where needed.
- Include tests for each assumption about filenames, metrics, and shape transformations.
