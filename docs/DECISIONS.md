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
