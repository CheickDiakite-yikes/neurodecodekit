# Architecture Decision Log

## 0001 — Build an access layer before a model layer

Decision: start with manifesting, selective download, tiny shards, and honest baselines.

Why: the biggest early bottleneck is usability, not model cleverness.

## 0002 — Keep base install light

Decision: base install uses pure Python. Heavy packages are optional extras.

Why: tests should pass quickly in constrained environments and in Codex before GPU/neuro dependencies are installed.

## 0003 — Use JSONL manifests

Decision: use JSONL for early manifests.

Why: easy to inspect, easy to diff, Parquet-compatible later.

## 0004 — Use `.npz` before Zarr for first cache

Decision: save first tiny shard as `.npz`, then move to Zarr.

Why: `.npz` is easy for smoke tests; Zarr is better once cache dimensions and metadata stabilize.

## 0005 — Always compare to dumb baselines

Decision: every neural model must be compared to random/frequency/keyboard/LM-only baselines.

Why: text decoding can look impressive when the language prior is doing most of the work.

## 0006 - Close Loop 1 with synthetic smoke before real data

Decision: mark Loop 1 as complete for the synthetic smoke path and proceed to Loop 2.

Why: PR1's `extract-windows` command, optional dependency handling, CLI help, and synthetic cache path are in place. Real extraction remains blocked until one explicit SpanishBCBL `.fif` / `.mat` pair is intentionally selected and downloaded.

Evidence: `docs/LOOP_01_PR1_CLOSEOUT_SMOKE.md`.

## 0007 - Make manifest uncertainty explicit before selection

Decision: add manifest v1 row families, parser warnings, optional size parsing, and raw/log candidate pairing summaries before improving download selection.

Why: safe tiny-shard selection depends on knowing which files are raw, logs, EEG sidecars, localizer/tapping files, or unknowns. Ambiguity should be visible in `inspect-manifest` rather than hidden in selector heuristics.

Evidence: `docs/LOOP_02_SPANISHBCBL_MANIFEST_V1.md`.

## 0008 - Treat tiny downloads as explicit capped plans

Decision: make `select-tiny` write a capped, size-aware selection plan and make
`download-selection` print that plan before any dry-run or execution path.

Why: a tiny-shard workflow is only safe if the exact files, known bytes,
missing-size warnings, and cap overrides are visible before the user can start a
real download.

Evidence: `docs/LOOP_03_SAFE_TINY_SHARD_SELECTOR.md`.

## 0009 - Make NPZ cache schema v0 the first stable interface

Decision: treat `load_npz_cache` as the stable B2Q-mini cache loader and stamp
every `.npz` with schema, dimensions, array descriptors, warnings, and
transformations.

Why: baselines, reports, demos, and later compression sweeps need one small
cache contract that works for both synthetic smoke data and real extracted
FIF/MAT windows.

Evidence: `docs/LOOP_04_B2Q_MINI_CACHE_V0.md`.

## 0010 - Make report cards the standard experiment artifact

Decision: add `neurodecode report` as the standard JSON/Markdown artifact for
target/prediction comparisons, with optional cache metadata attached.

Why: future no-brain, template, neural, compression, and demo loops need a
common way to compare CER, WER, keyboard-distance errors, examples, runtime, and
storage context without requiring a notebook.

Evidence: `docs/LOOP_05_METRICS_ERROR_REPORT_V1.md`.

## 0011 - Require a no-brain prior comparator before neural models

Decision: add `neurodecode prior-baseline` as the first real comparator before
template classifiers or neural networks.

Why: label/text priors can create deceptively good decoding results. Every
future neural-window model should be compared against a baseline that uses no
brain signal at all.

Evidence: `docs/LOOP_06_LM_PRIOR_BASELINE.md`.
