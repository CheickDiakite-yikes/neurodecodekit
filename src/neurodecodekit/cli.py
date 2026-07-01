"""Command-line interface for the NeuroDecodeKit starter."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from neurodecodekit.datasets.manifest import (
    build_manifest_from_paths,
    read_jsonl,
    summarize_manifest,
    write_jsonl,
)
from neurodecodekit.evaluation.keyboard import aligned_keyboard_distance
from neurodecodekit.evaluation.metrics import summarize_text_metrics


def _cmd_eval_text(args: argparse.Namespace) -> int:
    metrics = summarize_text_metrics(args.target, args.prediction)
    metrics["keyboard_distance"] = aligned_keyboard_distance(args.target, args.prediction)
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from neurodecodekit.evaluation.report import (
        build_text_report,
        labels_to_text_rows,
        read_text_rows,
        write_report_json,
        write_report_markdown,
    )

    start = time.perf_counter()
    cache_summary = None
    cache_labels = None
    warnings: list[str] = []
    if args.cache:
        from neurodecodekit.cache.npz_cache import load_npz_cache

        cache = load_npz_cache(args.cache)
        cache_summary = cache.summary.to_dict()
        cache_labels = labels_to_text_rows(cache.labels)

    if args.targets:
        targets = read_text_rows(args.targets)
    elif cache_labels is not None:
        targets = cache_labels
        warnings.append("targets_loaded_from_cache_labels")
    else:
        raise ValueError("--targets is required unless --cache supplies labels.")

    if args.predictions:
        predictions = read_text_rows(args.predictions)
    elif args.identity_smoke:
        predictions = list(targets)
        warnings.append("identity_smoke_predictions_equal_targets_not_model_result")
    else:
        raise ValueError("--predictions is required unless --identity-smoke is used.")

    report = build_text_report(
        targets=targets,
        predictions=predictions,
        cache_summary=cache_summary,
        run_name=args.run_name,
        split=args.split,
        max_examples=args.max_examples,
        warnings=warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - start, 6)

    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.out_json:
        print(f"Wrote report JSON to {args.out_json}")
    if args.out_md:
        print(f"Wrote report Markdown to {args.out_md}")
    return 0


def _cmd_prior_baseline(args: argparse.Namespace) -> int:
    from neurodecodekit.evaluation.report import (
        build_text_report,
        labels_to_text_rows,
        read_text_rows,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.models.prior_baseline import run_prior_baseline

    start = time.perf_counter()
    if args.train_targets and args.train_cache:
        raise ValueError("use only one of --train-targets or --train-cache.")

    cache_summary = None
    eval_targets: list[str] | None = None
    if args.cache:
        from neurodecodekit.cache.npz_cache import load_npz_cache

        cache = load_npz_cache(args.cache)
        cache_summary = cache.summary.to_dict()
        if not args.targets:
            eval_targets = labels_to_text_rows(cache.labels)

    if args.targets:
        eval_targets = read_text_rows(args.targets)
    if eval_targets is None:
        raise ValueError("--targets is required unless --cache supplies labels.")

    train_targets = None
    if args.train_targets:
        train_targets = read_text_rows(args.train_targets)
    elif args.train_cache:
        from neurodecodekit.cache.npz_cache import load_npz_cache

        train_targets = labels_to_text_rows(load_npz_cache(args.train_cache).labels)

    baseline = run_prior_baseline(
        eval_targets=eval_targets,
        train_targets=train_targets,
        strategy=args.strategy,
        seed=args.seed,
    )

    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)

    report = build_text_report(
        targets=eval_targets,
        predictions=baseline.predictions,
        cache_summary=cache_summary,
        run_name=args.run_name or f"prior_baseline_{args.strategy}",
        split=args.split,
        max_examples=args.max_examples,
        warnings=baseline.warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - start, 6)
    report["baseline"] = baseline.metadata()

    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.out_predictions:
        print(f"Wrote prior predictions to {args.out_predictions}")
    if args.out_json:
        print(f"Wrote report JSON to {args.out_json}")
    if args.out_md:
        print(f"Wrote report Markdown to {args.out_md}")
    return 0


def _cmd_template_baseline(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.npz_cache import load_npz_cache
    from neurodecodekit.evaluation.report import (
        build_text_report,
        labels_to_text_rows,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.models.template_baseline import (
        run_template_baseline,
        run_template_baseline_from_single_cache,
    )

    start = time.perf_counter()
    if args.cache and (args.train_cache or args.eval_cache):
        raise ValueError("use --cache for a single-cache holdout, or --train-cache with --eval-cache.")
    if not args.cache and not (args.train_cache and args.eval_cache):
        raise ValueError("--cache is required unless both --train-cache and --eval-cache are provided.")

    if args.cache:
        cache = load_npz_cache(args.cache)
        cache_summary = cache.summary.to_dict()
        baseline = run_template_baseline_from_single_cache(
            windows=cache.windows,
            labels=labels_to_text_rows(cache.labels),
            train_fraction=args.train_fraction,
            seed=args.seed,
        )
    else:
        train_cache = load_npz_cache(args.train_cache)
        eval_cache = load_npz_cache(args.eval_cache)
        cache_summary = eval_cache.summary.to_dict()
        baseline = run_template_baseline(
            train_windows=train_cache.windows,
            train_labels=labels_to_text_rows(train_cache.labels),
            eval_windows=eval_cache.windows,
            eval_labels=labels_to_text_rows(eval_cache.labels),
            split_mode="separate-cache",
            seed=args.seed,
        )

    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)

    report = build_text_report(
        targets=baseline.targets,
        predictions=baseline.predictions,
        cache_summary=cache_summary,
        run_name=args.run_name or "template_baseline_nearest_centroid",
        split=args.split,
        max_examples=args.max_examples,
        warnings=baseline.warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - start, 6)
    report["baseline"] = baseline.metadata()

    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.out_predictions:
        print(f"Wrote template predictions to {args.out_predictions}")
    if args.out_json:
        print(f"Wrote report JSON to {args.out_json}")
    if args.out_md:
        print(f"Wrote report Markdown to {args.out_md}")
    return 0


def _cmd_tiny_conv_baseline(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.npz_cache import load_npz_cache
    from neurodecodekit.evaluation.report import (
        build_text_report,
        labels_to_text_rows,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.models.tiny_conv_baseline import (
        run_tiny_conv_baseline,
        run_tiny_conv_baseline_from_single_cache,
    )

    start = time.perf_counter()
    if args.cache and (args.train_cache or args.eval_cache):
        raise ValueError("use --cache for a single-cache holdout, or --train-cache with --eval-cache.")
    if not args.cache and not (args.train_cache and args.eval_cache):
        raise ValueError("--cache is required unless both --train-cache and --eval-cache are provided.")

    if args.cache:
        cache = load_npz_cache(args.cache)
        cache_summary = cache.summary.to_dict()
        baseline = run_tiny_conv_baseline_from_single_cache(
            windows=cache.windows,
            labels=labels_to_text_rows(cache.labels),
            train_fraction=args.train_fraction,
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            hidden_channels=args.hidden_channels,
            device=args.device,
            num_threads=args.num_threads,
        )
    else:
        train_cache = load_npz_cache(args.train_cache)
        eval_cache = load_npz_cache(args.eval_cache)
        cache_summary = eval_cache.summary.to_dict()
        baseline = run_tiny_conv_baseline(
            train_windows=train_cache.windows,
            train_labels=labels_to_text_rows(train_cache.labels),
            eval_windows=eval_cache.windows,
            eval_labels=labels_to_text_rows(eval_cache.labels),
            split_mode="separate-cache",
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            hidden_channels=args.hidden_channels,
            device=args.device,
            num_threads=args.num_threads,
        )

    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)

    report = build_text_report(
        targets=baseline.targets,
        predictions=baseline.predictions,
        cache_summary=cache_summary,
        run_name=args.run_name or "tiny_conv_baseline",
        split=args.split,
        max_examples=args.max_examples,
        warnings=baseline.warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - start, 6)
    report["baseline"] = baseline.metadata()

    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.out_predictions:
        print(f"Wrote tiny-conv predictions to {args.out_predictions}")
    if args.out_json:
        print(f"Wrote report JSON to {args.out_json}")
    if args.out_md:
        print(f"Wrote report Markdown to {args.out_md}")
    return 0


def _cmd_manifest_from_paths(args: argparse.Namespace) -> int:
    paths = Path(args.paths).read_text(encoding="utf-8").splitlines()
    records = build_manifest_from_paths(paths, repo_id=args.repo_id)
    write_jsonl(records, args.out)
    print(f"Wrote {len(records)} records to {args.out}")
    print(json.dumps(summarize_manifest(records), indent=2, sort_keys=True))
    return 0


def _cmd_inspect_manifest(args: argparse.Namespace) -> int:
    records = read_jsonl(args.manifest)
    print(json.dumps(summarize_manifest(records), indent=2, sort_keys=True))
    return 0


def _cmd_list_hf_files(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.hf_access import list_repo_files, write_file_list

    paths = list_repo_files(args.repo_id, repo_type=args.repo_type)
    write_file_list(paths, args.out)
    print(f"Wrote {len(paths)} HF paths to {args.out}")
    print("Next: neurodecode manifest-from-paths --paths", args.out, "--out data/manifest.jsonl")
    return 0


def _cmd_make_synthetic_shard(args: argparse.Namespace) -> int:
    from neurodecodekit.training.synthetic import save_synthetic_npz

    summary = save_synthetic_npz(
        args.out,
        samples=args.samples,
        channels=args.channels,
        times=args.times,
        classes=args.classes,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_load_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.npz_cache import load_npz_cache, write_cache_metadata_sidecar

    loaded = load_npz_cache(args.cache)
    print(json.dumps(loaded.summary.to_dict(), indent=2, sort_keys=True))
    if args.metadata_out:
        write_cache_metadata_sidecar(args.cache, args.metadata_out)
        print(f"Wrote cache metadata sidecar to {args.metadata_out}")
    return 0


def _cmd_extract_windows(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.fif_mat_extraction import extract_fif_mat_windows

    summary = extract_fif_mat_windows(
        raw_path=args.raw,
        events_path=args.events,
        out_path=args.out,
        tmin=args.tmin,
        tmax=args.tmax,
        sfreq=args.sfreq,
        picks=args.picks,
        max_events=args.max_events,
        max_channels=args.max_channels,
    )
    print("Extracted event windows")
    print(f"  raw: {summary.raw_path}")
    print(f"  events: {summary.events_path}")
    print(f"  out: {summary.out_path}")
    print(f"  events found: {summary.n_events_found}")
    print(f"  events kept: {summary.n_events_kept}")
    print(f"  events dropped: {summary.n_events_dropped}")
    if summary.dropped_by_reason:
        print("  dropped by reason:")
        for reason, count in sorted(summary.dropped_by_reason.items()):
            print(f"    - {reason}: {count}")
    print(f"  output shape: {summary.output_shape} [events, channels, timepoints]")
    print(f"  sampling rate: {summary.sfreq:g} Hz")
    print(f"  channels: {len(summary.channel_names)}")
    if summary.raw_bytes is not None:
        print(f"  raw file size: {_format_bytes(summary.raw_bytes)}")
    print(f"  output file size: {_format_bytes(summary.output_bytes)}")
    if summary.warnings:
        print("  warnings:")
        for warning in summary.warnings:
            print(f"    - {warning}")
    return 0


def _format_bytes(n_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024


def _write_text_rows(path: str | Path, rows: list[str]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(str(row) for row in rows) + "\n", encoding="utf-8")


def _cmd_select_tiny(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.selection import (
        gb_to_bytes,
        select_tiny_from_manifest,
        write_selection,
    )

    selection = select_tiny_from_manifest(
        args.manifest,
        modality=args.modality,
        subject=args.subject,
        blocks=args.blocks,
        include_logs=not args.no_logs,
        max_files=args.max_files,
        max_total_bytes=gb_to_bytes(args.max_total_gb),
    )
    write_selection(selection, args.out)
    print(f"Wrote tiny selection with {len(selection.records)} files to {args.out}")
    _print_selection_plan(selection, heading="Tiny selection plan")
    print(json.dumps(selection.to_dict(), indent=2, sort_keys=True))
    return 0


def _cmd_download_selection(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.hf_access import selective_snapshot_download
    from neurodecodekit.datasets.selection import (
        DEFAULT_MAX_FILES,
        DEFAULT_MAX_TOTAL_BYTES,
        gb_to_bytes,
        read_selection,
        validate_selection_limits,
    )

    selection = read_selection(args.selection)
    max_files = args.max_files if args.max_files is not None else selection.max_files
    if max_files is None:
        max_files = DEFAULT_MAX_FILES
    if args.max_total_gb is not None:
        max_total_bytes = gb_to_bytes(args.max_total_gb)
    else:
        max_total_bytes = selection.max_total_bytes
    if max_total_bytes is None:
        max_total_bytes = DEFAULT_MAX_TOTAL_BYTES

    safety_warnings = validate_selection_limits(
        selection.records,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
        require_known_sizes=args.execute and not args.allow_unknown_size,
    )
    selection = replace(
        selection,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
        safety_warnings=safety_warnings,
    )
    _print_selection_plan(selection, heading="Download plan")
    dry_run = not args.execute
    if dry_run:
        print("Safety default: dry-run. Pass --execute to download selected files.")
    else:
        print("Executing selective download. Confirm you are not downloading the full dataset.")
    selective_snapshot_download(
        repo_id=selection.repo_id,
        allow_patterns=selection.allow_patterns,
        local_dir=args.local_dir,
        dry_run=dry_run,
    )
    return 0


def _print_selection_plan(selection: Any, *, heading: str) -> None:
    from neurodecodekit.datasets.selection import format_bytes

    print(heading)
    print(f"  repo: {selection.repo_id}")
    print(f"  files: {selection.n_files}")
    print(f"  estimated size: {format_bytes(selection.estimated_bytes)}")
    if selection.missing_size_count:
        print(
            f"  known size: {format_bytes(selection.known_bytes)} "
            f"({selection.missing_size_count} file(s) missing size metadata)"
        )
    print(f"  max files: {selection.max_files if selection.max_files is not None else 'unlimited'}")
    print(f"  max total size: {format_bytes(selection.max_total_bytes)}")
    if selection.safety_warnings:
        print("  safety warnings:")
        for warning in selection.safety_warnings:
            print(f"    - {warning}")
    print("  files:")
    for idx, record in enumerate(selection.records, start=1):
        family = record.family or record.kind or "unknown"
        print(f"    {idx}. {record.path} ({format_bytes(record.size_bytes)}; {family})")


def build_parser() -> argparse.ArgumentParser:
    from neurodecodekit.datasets.selection import DEFAULT_MAX_FILES, DEFAULT_MAX_TOTAL_GB

    parser = argparse.ArgumentParser(
        prog="neurodecode",
        description="Small, reproducible research loops for neural language decoding.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("eval-text", help="Score target vs predicted text with CER/WER.")
    p.add_argument("--target", required=True)
    p.add_argument("--prediction", required=True)
    p.set_defaults(func=_cmd_eval_text)

    p = sub.add_parser("report", help="Write a JSON/Markdown text decoding report.")
    p.add_argument("--targets", default=None, help="Text file with one target per line.")
    p.add_argument("--predictions", default=None, help="Text file with one prediction per line.")
    p.add_argument("--cache", default=None, help="Optional B2Q-mini NPZ cache for labels/storage metadata.")
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--split", default=None, help="Split/protocol label, e.g. synthetic-smoke or subject.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10.")
    p.add_argument(
        "--identity-smoke",
        action="store_true",
        help="Use targets as predictions for plumbing tests. This is not a model result.",
    )
    p.set_defaults(func=_cmd_report)

    p = sub.add_parser("prior-baseline", help="Run a no-brain label/text prior baseline.")
    p.add_argument("--targets", default=None, help="Eval targets, one row per example.")
    p.add_argument("--cache", default=None, help="Optional B2Q-mini NPZ cache; labels become targets if --targets is absent.")
    p.add_argument("--train-targets", default=None, help="Optional train targets used to fit the prior.")
    p.add_argument("--train-cache", default=None, help="Optional train cache whose labels fit the prior.")
    p.add_argument(
        "--strategy",
        default="most-frequent",
        choices=["most-frequent", "frequency-sample", "uniform-random"],
        help="No-brain prediction strategy. Default: most-frequent.",
    )
    p.add_argument("--seed", type=int, default=7, help="Seed for sampling strategies. Default: 7.")
    p.add_argument("--out-predictions", default=None, help="Optional one-prediction-per-line output path.")
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--split", default=None, help="Split/protocol label, e.g. synthetic-smoke or subject.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10.")
    p.set_defaults(func=_cmd_prior_baseline)

    p = sub.add_parser("template-baseline", help="Run a tiny nearest-centroid baseline over cache windows.")
    p.add_argument("--cache", default=None, help="Single B2Q-mini cache to split into train/eval rows.")
    p.add_argument("--train-cache", default=None, help="Optional train cache for separate-cache evaluation.")
    p.add_argument("--eval-cache", default=None, help="Optional eval cache for separate-cache evaluation.")
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.5,
        help="Single-cache stratified train fraction. Default: 0.5.",
    )
    p.add_argument("--seed", type=int, default=7, help="Seed for deterministic holdout split. Default: 7.")
    p.add_argument("--out-predictions", default=None, help="Optional one-prediction-per-line output path.")
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--split", default=None, help="Split/protocol label, e.g. synthetic-holdout or session.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10.")
    p.set_defaults(func=_cmd_template_baseline)

    p = sub.add_parser(
        "tiny-conv-baseline",
        help="Run an optional CPU-safe tiny ConvNet baseline over cache windows. Requires [ml].",
    )
    p.add_argument("--cache", default=None, help="Single B2Q-mini cache to split into train/eval rows.")
    p.add_argument("--train-cache", default=None, help="Optional train cache for separate-cache evaluation.")
    p.add_argument("--eval-cache", default=None, help="Optional eval cache for separate-cache evaluation.")
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.5,
        help="Single-cache stratified train fraction. Default: 0.5.",
    )
    p.add_argument("--seed", type=int, default=7, help="Seed for deterministic holdout/training. Default: 7.")
    p.add_argument("--epochs", type=int, default=20, help="Training epochs. Default: 20.")
    p.add_argument("--batch-size", type=int, default=16, help="Mini-batch size. Default: 16.")
    p.add_argument("--learning-rate", type=float, default=0.01, help="Adam learning rate. Default: 0.01.")
    p.add_argument("--hidden-channels", type=int, default=8, help="Conv hidden channels. Default: 8.")
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Torch device. Default: cpu.")
    p.add_argument("--num-threads", type=int, default=1, help="Torch CPU threads. Default: 1.")
    p.add_argument("--out-predictions", default=None, help="Optional one-prediction-per-line output path.")
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--split", default=None, help="Split/protocol label, e.g. synthetic-holdout or session.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10.")
    p.set_defaults(func=_cmd_tiny_conv_baseline)

    p = sub.add_parser("manifest-from-paths", help="Build JSONL manifest from a newline path list.")
    p.add_argument("--paths", required=True, help="Text file containing one repo path per line.")
    p.add_argument("--out", required=True, help="Output manifest JSONL path.")
    p.add_argument("--repo-id", default="bcbl190626/SpanishBCBL")
    p.set_defaults(func=_cmd_manifest_from_paths)

    p = sub.add_parser("inspect-manifest", help="Summarize a manifest JSONL file.")
    p.add_argument("--manifest", required=True)
    p.set_defaults(func=_cmd_inspect_manifest)

    p = sub.add_parser("list-hf-files", help="List files in a Hugging Face repo. Requires [hf].")
    p.add_argument("--repo-id", required=True)
    p.add_argument("--repo-type", default="dataset")
    p.add_argument("--out", required=True)
    p.set_defaults(func=_cmd_list_hf_files)

    p = sub.add_parser("make-synthetic-shard", help="Create a tiny synthetic NPZ shard for smoke tests.")
    p.add_argument("--out", required=True)
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--channels", type=int, default=8)
    p.add_argument("--times", type=int, default=25)
    p.add_argument("--classes", type=int, default=8)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=_cmd_make_synthetic_shard)

    p = sub.add_parser("load-cache", help="Load and summarize a B2Q-mini NPZ cache.")
    p.add_argument("--cache", required=True, help="Path to a .npz cache.")
    p.add_argument(
        "--metadata-out",
        default=None,
        help="Optional JSON sidecar path containing cache summary and metadata.",
    )
    p.set_defaults(func=_cmd_load_cache)

    p = sub.add_parser(
        "extract-windows",
        help="Extract event-aligned windows from one FIF block and one MAT log. Requires [neuro].",
    )
    p.add_argument("--raw", required=True, help="Path to one downloaded .fif MEG block.")
    p.add_argument("--events", required=True, help="Path to one matching .mat behavioral/log file.")
    p.add_argument("--out", required=True, help="Output .npz cache path.")
    p.add_argument("--tmin", type=float, required=True, help="Window start in seconds relative to event.")
    p.add_argument("--tmax", type=float, required=True, help="Window end in seconds relative to event.")
    p.add_argument("--sfreq", type=float, required=True, help="Target sampling rate in Hz.")
    p.add_argument(
        "--picks",
        default=None,
        help="Optional MNE channel pick or comma-separated channel names, e.g. meg or MEG0111,MEG0112.",
    )
    p.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="Optional cap for smoke extraction from a large event log.",
    )
    p.add_argument(
        "--max-channels",
        type=int,
        default=None,
        help="Optional cap using the first N channels after channel picking.",
    )
    p.set_defaults(func=_cmd_extract_windows)

    p = sub.add_parser("select-tiny", help="Create a tiny safe selection from a manifest.")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--modality", default="MEG", choices=["MEG", "EEG", "meg", "eeg"])
    p.add_argument("--subject", default=None, help="Optional subject ID like S1. Defaults to first detected subject.")
    p.add_argument("--blocks", type=int, default=1, help="Number of raw blocks to select. Default: 1.")
    p.add_argument("--no-logs", action="store_true", help="Do not include behavioral logs.")
    p.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Safety cap on selected files. Default: {DEFAULT_MAX_FILES}.",
    )
    p.add_argument(
        "--max-total-gb",
        type=float,
        default=DEFAULT_MAX_TOTAL_GB,
        help=f"Safety cap on known selected bytes in GB. Default: {DEFAULT_MAX_TOTAL_GB:g}.",
    )
    p.set_defaults(func=_cmd_select_tiny)

    p = sub.add_parser("download-selection", help="Dry-run or execute selective HF download from a selection JSON.")
    p.add_argument("--selection", required=True)
    p.add_argument("--local-dir", required=True)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="Actually download. Default is dry-run only.")
    mode.add_argument("--dry-run", action="store_true", help="Explicitly keep dry-run mode. This is the default.")
    p.add_argument("--max-files", type=int, default=None, help="Override the selection file-count safety cap.")
    p.add_argument(
        "--max-total-gb",
        type=float,
        default=None,
        help="Override the selection total-size safety cap in GB.",
    )
    p.add_argument(
        "--allow-unknown-size",
        action="store_true",
        help="Permit --execute when selected files are missing size metadata after reviewing the plan.",
    )
    p.set_defaults(func=_cmd_download_selection)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001 - CLI should show friendly errors
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
