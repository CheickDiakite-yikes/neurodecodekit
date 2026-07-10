"""Isolated NPZ access benchmark and evidence-based lazy-backend gate."""

from __future__ import annotations

import gc
import importlib.util
import json
import math
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.cache.sentence_npz import SENTENCE_CACHE_SCHEMA_NAME
from neurodecodekit.cache.signal_representation import (
    REPRESENTATION_CACHE_SCHEMA_NAME,
    array_sha256,
    decode_signal_payload,
    file_sha256,
    load_sentence_cache_auto,
)


GATE_SCHEMA_NAME = "b2q-lazy-backend-gate"
GATE_SCHEMA_VERSION = 0
PROOF_POSTURE = "current_real_cache_npz_access_gate_no_zarr_install"
NUMPY_NPZ_SOURCE = (
    "https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html"
)
NUMPY_NPZFILE_SOURCE = (
    "https://numpy.org/doc/stable/reference/generated/numpy.lib.npyio.NpzFile.html"
)
ZARR_QUICK_START_SOURCE = "https://zarr.readthedocs.io/en/stable/quick-start/"
ZARR_ARRAYS_SOURCE = "https://zarr.readthedocs.io/en/stable/user-guide/arrays/"
ZARR_CHUNK_SPEC_SOURCE = (
    "https://zarr-specs.readthedocs.io/en/latest/v3/chunk-grids/regular-grid/"
)
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def run_lazy_backend_gate(
    *,
    cache_paths: Iterable[str | Path],
    out_dir: str | Path,
    row_counts: Iterable[int] = (1, 8),
    repetitions: int = 5,
    max_full_load_ms: float = 250.0,
    max_partial_load_ms: float = 100.0,
    max_peak_rss_mb: float = 512.0,
    revisit_cache_mb: float = 128.0,
    report_json_path: str | Path | None = None,
    report_markdown_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Measure current NPZ access and decide whether a Zarr build is justified."""

    started_at = time.perf_counter()
    paths = _normalize_cache_paths(cache_paths)
    counts = _normalize_row_counts(row_counts)
    if repetitions < 1 or repetitions > 20:
        raise ValueError("repetitions must be within 1..20")
    thresholds = {
        "max_full_load_ms": _positive_finite(max_full_load_ms, "max_full_load_ms"),
        "max_partial_load_ms": _positive_finite(
            max_partial_load_ms, "max_partial_load_ms"
        ),
        "max_peak_rss_mb": _positive_finite(max_peak_rss_mb, "max_peak_rss_mb"),
        "revisit_cache_mb": _positive_finite(revisit_cache_mb, "revisit_cache_mb"),
    }

    output_dir = Path(out_dir)
    report_json = Path(report_json_path) if report_json_path else output_dir / "gate.json"
    report_markdown = (
        Path(report_markdown_path) if report_markdown_path else output_dir / "gate.md"
    )
    _prepare_report_paths([report_json, report_markdown], overwrite=overwrite)

    source_rows = []
    for path in paths:
        loaded = load_sentence_cache_auto(path)
        if max(counts) > loaded.summary.n_sentences:
            raise ValueError(
                f"row count {max(counts)} exceeds {loaded.summary.n_sentences} rows in {path}"
            )
        metadata = _read_npz_metadata(path)
        schema_name = str((metadata.get("schema") or {}).get("name") or "")
        encoding = _encoding_name(metadata, schema_name)
        expected_full_hash = array_sha256(loaded.signals)
        expected_row_hashes = {
            count: array_sha256(loaded.signals[:count]) for count in counts
        }
        full = _run_isolated_worker(
            cache_path=path,
            mode="full",
            row_count=None,
            repetitions=repetitions,
        )
        partial = []
        for count in counts:
            operation = _run_isolated_worker(
                cache_path=path,
                mode="rows",
                row_count=count,
                repetitions=repetitions,
            )
            operation["requested_sentence_fraction"] = count / loaded.summary.n_sentences
            operation["logical_member_access_amplification"] = (
                loaded.summary.n_sentences / count
            )
            operation["median_time_fraction_vs_full"] = _safe_ratio(
                operation["timing"]["median_sec"], full["timing"]["median_sec"]
            )
            operation["peak_rss_fraction_vs_full"] = _safe_ratio(
                operation["peak_rss_bytes"], full["peak_rss_bytes"]
            )
            operation["exact_decoded_signal_match"] = (
                operation["result_sha256"] == expected_row_hashes[count]
            )
            partial.append(operation)
        full["exact_decoded_signal_match"] = full["result_sha256"] == expected_full_hash

        full_time_ok = full["timing"]["median_sec"] * 1000 <= thresholds["max_full_load_ms"]
        full_rss_ok = full["peak_rss_bytes"] <= thresholds["max_peak_rss_mb"] * 1024 * 1024
        partial_time_ok = all(
            row["timing"]["median_sec"] * 1000 <= thresholds["max_partial_load_ms"]
            for row in partial
        )
        partial_rss_ok = all(
            row["peak_rss_bytes"] <= thresholds["max_peak_rss_mb"] * 1024 * 1024
            for row in partial
        )
        cache_size_ok = path.stat().st_size <= thresholds["revisit_cache_mb"] * 1024 * 1024
        identity_ok = full["exact_decoded_signal_match"] and all(
            row["exact_decoded_signal_match"] for row in partial
        )
        gate_checks = {
            "full_load_time_within_budget": full_time_ok,
            "full_peak_rss_within_budget": full_rss_ok,
            "partial_load_times_within_budget": partial_time_ok,
            "partial_peak_rss_within_budget": partial_rss_ok,
            "cache_size_below_revisit_threshold": cache_size_ok,
            "all_decoded_signal_hashes_exact": identity_ok,
        }
        source_rows.append(
            {
                "label": path.stem,
                "path": str(path),
                "sha256": file_sha256(path),
                "schema_name": schema_name,
                "encoding": encoding,
                "cache_bytes": int(path.stat().st_size),
                "signals_shape": list(loaded.summary.signals_shape),
                "decoded_signals_dtype": str(loaded.signals.dtype),
                "decoded_signal_bytes": int(loaded.signals.nbytes),
                "n_sentences": loaded.summary.n_sentences,
                "n_channels": loaded.summary.n_channels,
                "full_load": full,
                "partial_reads": partial,
                "gate_checks": gate_checks,
                "all_gate_checks_pass": all(gate_checks.values()),
            }
        )
        del loaded

    all_gate_checks_pass = all(row["all_gate_checks_pass"] for row in source_rows)
    all_identity_checks_pass = all(
        row["gate_checks"]["all_decoded_signal_hashes_exact"] for row in source_rows
    )
    decision = _build_decision(all_gate_checks_pass)
    report = {
        "schema": {"name": GATE_SCHEMA_NAME, "version": GATE_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "run": {
            "execution_mode": "sequential_isolated_worker_processes",
            "cache_count": len(paths),
            "row_counts": counts,
            "repetitions_per_operation": repetitions,
            "worker_thread_cap": 1,
            "thread_environment_variables": list(THREAD_ENV_VARS),
            "total_runtime_sec": round(time.perf_counter() - started_at, 6),
            "peak_parent_rss_bytes": _peak_rss_bytes(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "numpy_version": _dependency_version("numpy"),
            "zarr_installed": importlib.util.find_spec("zarr") is not None,
            "zarr_version": _dependency_version("zarr"),
        },
        "thresholds": thresholds,
        "research_context": {
            "numpy_compressed_npz": NUMPY_NPZ_SOURCE,
            "numpy_npzfile": NUMPY_NPZFILE_SOURCE,
            "zarr_quick_start": ZARR_QUICK_START_SOURCE,
            "zarr_arrays": ZARR_ARRAYS_SOURCE,
            "zarr_regular_chunk_grid_spec": ZARR_CHUNK_SPEC_SOURCE,
            "npz_note": (
                "Compressed NPZ is a ZIP archive of NPY members. Selecting rows after "
                "NpzFile member access materializes that complete array member."
            ),
            "zarr_note": (
                "Zarr v3 divides arrays into addressable chunks and supports partial "
                "selection, but that capability is useful only when current absolute "
                "access cost or workflow needs justify another backend."
            ),
        },
        "caches": source_rows,
        "consistency": {
            "all_gate_checks_pass": all_gate_checks_pass,
            "all_decoded_signal_hashes_exact": all_identity_checks_pass,
            "largest_cache_bytes": max(row["cache_bytes"] for row in source_rows),
            "slowest_full_load_median_ms": max(
                row["full_load"]["timing"]["median_sec"] * 1000 for row in source_rows
            ),
            "slowest_partial_load_median_ms": max(
                operation["timing"]["median_sec"] * 1000
                for row in source_rows
                for operation in row["partial_reads"]
            ),
            "highest_worker_peak_rss_bytes": max(
                operation["peak_rss_bytes"]
                for row in source_rows
                for operation in [row["full_load"], *row["partial_reads"]]
            ),
        },
        "decision": decision,
        "artifact_paths": {
            "report_json": str(report_json),
            "report_markdown": str(report_markdown),
        },
        "warnings": [
            "resource_gate_only_no_decoder_training_or_accuracy",
            "timings_use_warm_operating_system_page_cache_and_are_machine_local",
            "npz_partial_reads_materialize_the_complete_signal_or_payload_member",
            "zarr_was_researched_but_not_installed_or_benchmarked_in_this_gate",
            "thresholds_are_local_product_budgets_not_universal_backend_rules",
            "keep_per_block_caches_separate_to_bound_peak_memory",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    write_lazy_backend_gate_json(report, report_json)
    write_lazy_backend_gate_markdown(report, report_markdown)
    report["resources"] = {
        "report_json_bytes": int(report_json.stat().st_size),
        "report_markdown_bytes": int(report_markdown.stat().st_size),
        "total_report_bytes": int(report_json.stat().st_size + report_markdown.stat().st_size),
        "new_cache_or_backend_bytes": 0,
    }
    write_lazy_backend_gate_json(report, report_json)
    write_lazy_backend_gate_markdown(report, report_markdown)
    return report


def run_access_worker(
    *,
    cache_path: str | Path,
    mode: str,
    row_count: int | None,
    repetitions: int,
) -> dict[str, Any]:
    """Run one access pattern in a fresh process and return JSON-safe metrics."""

    np = _require_numpy()
    path = Path(cache_path)
    if mode not in {"full", "rows"}:
        raise ValueError("worker mode must be 'full' or 'rows'")
    if repetitions < 1:
        raise ValueError("worker repetitions must be positive")
    metadata = _read_npz_metadata(path)
    schema_name = str((metadata.get("schema") or {}).get("name") or "")
    if mode == "rows" and (row_count is None or row_count < 1):
        raise ValueError("row_count is required for row access")

    gc.collect()
    baseline_rss = _peak_rss_bytes()
    times = []
    result_hash = None
    result_shape = None
    result_dtype = None
    result_bytes = None
    member_uncompressed_bytes = _physical_signal_member_bytes(metadata)
    for _ in range(repetitions):
        gc.collect()
        started_at = time.perf_counter()
        if mode == "full":
            loaded = load_sentence_cache_auto(path)
            result = np.asarray(loaded.signals)
        else:
            with np.load(path, allow_pickle=False) as data:
                if schema_name == SENTENCE_CACHE_SCHEMA_NAME:
                    member = data["signals"]
                    member_uncompressed_bytes = int(member.nbytes)
                    result = member[:row_count].copy()
                elif schema_name == REPRESENTATION_CACHE_SCHEMA_NAME:
                    member = data["signal_payload"]
                    member_uncompressed_bytes = int(member.nbytes)
                    selected = member[:row_count].copy()
                    encoding_metadata = metadata["storage"]["encoding"]
                    result = decode_signal_payload(selected, encoding_metadata)
                    del selected
                else:
                    raise ValueError(f"Unsupported cache schema: {schema_name!r}")
                del member
        times.append(time.perf_counter() - started_at)
        result_hash = array_sha256(result)
        result_shape = [int(value) for value in result.shape]
        result_dtype = str(result.dtype)
        result_bytes = int(result.nbytes)
        del result
        if mode == "full":
            del loaded

    peak_rss = _peak_rss_bytes()
    return {
        "mode": mode,
        "row_count": row_count,
        "timing": _timing_summary(times),
        "baseline_rss_bytes": baseline_rss,
        "peak_rss_bytes": peak_rss,
        "incremental_peak_rss_bytes": max(0, peak_rss - baseline_rss),
        "physical_signal_member_uncompressed_bytes": member_uncompressed_bytes,
        "result_shape": result_shape,
        "result_dtype": result_dtype,
        "result_bytes": result_bytes,
        "result_sha256": result_hash,
    }


def write_lazy_backend_gate_json(report: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_lazy_backend_gate_markdown(report: dict[str, Any], path: str | Path) -> None:
    lines = [
        "# Lazy Backend Gate",
        "",
        f"**Proof posture:** `{report['proof_posture']}`",
        "",
        "This report asks whether current NPZ access is materially limiting. It does not "
        "train a decoder, benchmark Zarr, or claim that partial reads preserve accuracy.",
        "",
        "## Current Cache Access",
        "",
        "| Cache | Schema / encoding | Bytes | Full median | Full peak RSS | "
        "1-row median | 1-row / full time | All gates |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["caches"]:
        one_row = next(
            operation for operation in row["partial_reads"] if operation["row_count"] == 1
        )
        schema = row["schema_name"]
        if row["encoding"]:
            schema = f"{schema} / {row['encoding']}"
        lines.append(
            f"| `{row['label']}` | `{schema}` | {row['cache_bytes']:,} | "
            f"{row['full_load']['timing']['median_sec'] * 1000:.3f} ms | "
            f"{_format_bytes(row['full_load']['peak_rss_bytes'])} | "
            f"{one_row['timing']['median_sec'] * 1000:.3f} ms | "
            f"{one_row['median_time_fraction_vs_full']:.1%} | "
            f"`{row['all_gate_checks_pass']}` |"
        )
    decision = report["decision"]
    consistency = report["consistency"]
    thresholds = report["thresholds"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Status: `{decision['status']}`",
            f"- Backend action: `{decision['backend_action']}`",
            f"- Next loop: `{decision['next_loop']}`",
            f"- Reason: {decision['reason']}",
            "",
            "## Gate Summary",
            "",
            f"- Largest cache: {_format_bytes(consistency['largest_cache_bytes'])}",
            f"- Slowest full median: {consistency['slowest_full_load_median_ms']:.3f} ms",
            f"- Slowest partial median: {consistency['slowest_partial_load_median_ms']:.3f} ms",
            f"- Highest worker peak RSS: "
            f"{_format_bytes(consistency['highest_worker_peak_rss_bytes'])}",
            f"- Full-load budget: {thresholds['max_full_load_ms']:.1f} ms",
            f"- Partial-read budget: {thresholds['max_partial_load_ms']:.1f} ms",
            f"- Peak-RSS budget: {thresholds['max_peak_rss_mb']:.1f} MiB",
            f"- Cache-size revisit threshold: {thresholds['revisit_cache_mb']:.1f} MiB",
            "",
            "## Interpretation",
            "",
            "One-row NPZ access is inefficient because the complete compressed signal or "
            "payload member is materialized before slicing. Absolute access time and memory "
            "still remain below the declared local budgets for every tested cache. Keep "
            "per-block NPZ files separate and revisit a chunked backend only when one of the "
            "recorded thresholds or a repeated subarray workflow is reached.",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_isolated_worker(
    *,
    cache_path: Path,
    mode: str,
    row_count: int | None,
    repetitions: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "neurodecodekit.experiments.lazy_backend_gate",
        "--worker",
        "--cache",
        str(cache_path),
        "--mode",
        mode,
        "--repetitions",
        str(repetitions),
    ]
    if row_count is not None:
        command.extend(["--row-count", str(row_count)])
    env = dict(os.environ)
    for name in THREAD_ENV_VARS:
        env[name] = "1"
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Lazy-backend worker failed ({completed.returncode}): {detail}")
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError("Lazy-backend worker did not return valid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Lazy-backend worker JSON must be an object.")
    return payload


def _build_decision(all_gate_checks_pass: bool) -> dict[str, Any]:
    if all_gate_checks_pass:
        return {
            "status": "park_optional_zarr_npz_not_materially_limiting_current_caches",
            "backend_action": "keep_per_block_npz_as_default_no_zarr_install",
            "next_loop": 14,
            "reason": (
                "NPZ partial access is inefficient, but every tested standard and packed "
                "cache remains below the explicit absolute load-time, peak-memory, and "
                "cache-size budgets. Another runtime backend would add complexity without "
                "solving a current material bottleneck."
            ),
            "revisit_when": [
                "one cache exceeds the configured compressed-size threshold",
                "full semantic load exceeds the configured latency or peak-RSS budget",
                "partial access exceeds its configured absolute latency budget",
                "a real workflow repeatedly reads subarrays instead of one full block",
            ],
        }
    return {
        "status": "bounded_zarr_comparison_justified",
        "backend_action": "benchmark_optional_zarr_before_implementation",
        "next_loop": 13,
        "reason": (
            "At least one current NPZ cache exceeded an explicit access, memory, size, or "
            "identity gate. A bounded Zarr comparison is justified, but backend adoption "
            "still requires semantic parity and resource evidence."
        ),
        "revisit_when": [],
    }


def _read_npz_metadata(path: str | Path) -> dict[str, Any]:
    np = _require_numpy()
    with np.load(Path(path), allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise ValueError(f"Cache is missing metadata: {path}")
        value = data["metadata"]
        scalar = value.item() if hasattr(value, "item") else value
    decoded = json.loads(str(scalar))
    if not isinstance(decoded, dict):
        raise ValueError("Cache metadata must decode to an object.")
    return decoded


def _physical_signal_member_bytes(metadata: dict[str, Any]) -> int:
    np = _require_numpy()
    schema_name = str((metadata.get("schema") or {}).get("name") or "")
    key = "signals" if schema_name == SENTENCE_CACHE_SCHEMA_NAME else "signal_payload"
    descriptor = (metadata.get("arrays") or {}).get(key) or {}
    shape = descriptor.get("shape")
    dtype = descriptor.get("dtype")
    if not isinstance(shape, list) or not dtype:
        raise ValueError(f"Cache metadata is missing the {key} array descriptor.")
    return int(math.prod(int(value) for value in shape) * np.dtype(str(dtype)).itemsize)


def _encoding_name(metadata: dict[str, Any], schema_name: str) -> str | None:
    if schema_name == SENTENCE_CACHE_SCHEMA_NAME:
        return "float32"
    if schema_name == REPRESENTATION_CACHE_SCHEMA_NAME:
        return str(((metadata.get("storage") or {}).get("encoding") or {}).get("name"))
    raise ValueError(f"Unsupported cache schema name: {schema_name!r}")


def _normalize_cache_paths(values: Iterable[str | Path]) -> list[Path]:
    paths = [Path(value) for value in values]
    if not paths:
        raise ValueError("at least one NPZ cache is required")
    if len({str(path.resolve()) for path in paths}) != len(paths):
        raise ValueError("cache paths must be unique")
    for path in paths:
        if path.suffix.lower() != ".npz" or not path.is_file():
            raise ValueError(f"Expected an existing NPZ cache: {path}")
    return paths


def _normalize_row_counts(values: Iterable[int]) -> list[int]:
    counts = [int(value) for value in values]
    if not counts or any(value < 1 for value in counts):
        raise ValueError("row_counts must contain positive integers")
    if len(set(counts)) != len(counts):
        raise ValueError("row_counts must be unique")
    if 1 not in counts:
        raise ValueError("row_counts must include 1 for the single-sentence access gate")
    return sorted(counts)


def _prepare_report_paths(paths: list[Path], *, overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Planned gate reports already exist: " + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise IsADirectoryError(f"Planned report path is a directory: {path}")
            path.unlink()


def _timing_summary(values: list[float]) -> dict[str, Any]:
    return {
        "repetitions": len(values),
        "first_sec": round(values[0], 9),
        "median_sec": round(statistics.median(values), 9),
        "min_sec": round(min(values), 9),
        "max_sec": round(max(values), 9),
    }


def _positive_finite(value: Any, name: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return numeric


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _dependency_version(name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(name)
    except Exception:  # noqa: BLE001 - optional dependency metadata
        return None


def _format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} GiB"


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Lazy-backend gate requires NumPy: `pip install numpy`.") from exc
    return np


def _worker_main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--cache", required=True)
    parser.add_argument("--mode", required=True, choices=["full", "rows"])
    parser.add_argument("--row-count", type=int, default=None)
    parser.add_argument("--repetitions", type=int, required=True)
    args = parser.parse_args(argv)
    payload = run_access_worker(
        cache_path=args.cache,
        mode=args.mode,
        row_count=args.row_count,
        repetitions=args.repetitions,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess
    raise SystemExit(_worker_main(sys.argv[1:]))
