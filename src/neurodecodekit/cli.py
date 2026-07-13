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
        compare_paired_label_predictions,
        labels_to_text_rows,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.models.prior_baseline import run_prior_baseline
    from neurodecodekit.models.template_baseline import (
        run_template_baseline,
        run_template_baseline_from_single_cache,
    )

    start = time.perf_counter()
    if args.cache and (args.train_cache or args.eval_cache):
        raise ValueError(
            "use --cache for a single-cache holdout, or --train-cache with --eval-cache."
        )
    if not args.cache and not (args.train_cache and args.eval_cache):
        raise ValueError(
            "--cache is required unless both --train-cache and --eval-cache are provided."
        )

    if args.cache:
        cache = load_npz_cache(args.cache)
        cache_summary = cache.summary.to_dict()
        cache_labels = labels_to_text_rows(cache.labels)
        baseline = run_template_baseline_from_single_cache(
            windows=cache.windows,
            labels=cache_labels,
            train_fraction=args.train_fraction,
            seed=args.seed,
        )
        if baseline.train_indices is None:
            raise RuntimeError("single-cache template split did not preserve train indices")
        train_targets = [cache_labels[index] for index in baseline.train_indices]
    else:
        train_cache = load_npz_cache(args.train_cache)
        eval_cache = load_npz_cache(args.eval_cache)
        cache_summary = eval_cache.summary.to_dict()
        train_targets = labels_to_text_rows(train_cache.labels)
        baseline = run_template_baseline(
            train_windows=train_cache.windows,
            train_labels=train_targets,
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
    report["baseline"] = baseline.metadata()
    label_accuracy = sum(
        target == prediction
        for target, prediction in zip(baseline.targets, baseline.predictions, strict=True)
    ) / len(baseline.targets)
    report["summary"].update(
        {
            "primary_metric": "label_accuracy",
            "label_accuracy": label_accuracy,
            "label_error_count": len(baseline.targets) - round(label_accuracy * len(baseline.targets)),
        }
    )
    report["baseline"]["eval_accuracy"] = label_accuracy
    report["warnings"].extend(
        [
            "primary_metric_is_exact_key_label_accuracy",
            "text_cer_is_non_primary_for_multi_character_key_tokens",
        ]
    )
    prior = run_prior_baseline(
        eval_targets=baseline.targets,
        train_targets=train_targets,
        strategy="most-frequent",
        seed=args.seed,
    )
    prior_report = build_text_report(
        targets=baseline.targets,
        predictions=prior.predictions,
        max_examples=1,
        warnings=prior.warnings,
    )
    prior_accuracy = sum(
        target == prediction
        for target, prediction in zip(baseline.targets, prior.predictions, strict=True)
    ) / len(baseline.targets)
    prior_report["summary"].update(
        {
            "primary_metric": "label_accuracy",
            "label_accuracy": prior_accuracy,
            "label_error_count": len(baseline.targets)
            - round(prior_accuracy * len(baseline.targets)),
        }
    )
    report["comparators"] = {
        "prior_only": {
            "baseline": prior.metadata(),
            "summary": prior_report["summary"],
        }
    }
    report["comparisons"] = {
        "template_vs_prior_only": compare_paired_label_predictions(
            targets=baseline.targets,
            predictions_a=baseline.predictions,
            predictions_b=prior.predictions,
            label_a="template",
            label_b="prior_only",
            bootstrap_iterations=args.bootstrap_iterations,
            seed=args.seed,
        )
    }
    report["run"]["runtime_sec"] = round(time.perf_counter() - start, 6)

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
        raise ValueError(
            "use --cache for a single-cache holdout, or --train-cache with --eval-cache."
        )
    if not args.cache and not (args.train_cache and args.eval_cache):
        raise ValueError(
            "--cache is required unless both --train-cache and --eval-cache are provided."
        )

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


def _cmd_inspect_recording(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.local_intake import (
        IntakeLimits,
        inspect_local_recording,
        write_intake_artifacts,
    )

    mib = 1024 * 1024
    limits = IntakeLimits(
        max_files=args.max_files,
        max_depth=args.max_depth,
        max_declared_input_bytes=int(args.max_input_mb * mib),
        max_text_file_bytes=int(args.max_text_file_mb * mib),
        max_text_total_bytes=int(args.max_text_total_mb * mib),
        max_output_bytes=int(args.max_output_mb * mib),
    )
    result = inspect_local_recording(
        args.path,
        root_path=args.root,
        modality=args.modality,
        device_type=args.device_type,
        registry_path=args.registry,
        hash_text_metadata=args.hash_text_metadata,
        limits=limits,
    )
    summary = write_intake_artifacts(result, args.out_dir, overwrite=args.overwrite)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_intake_report(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.local_intake import load_intake_report

    summary = load_intake_report(
        args.report,
        audit_path=args.audit,
        max_report_bytes=int(args.max_report_mb * 1024 * 1024),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_make_signal_quality_fixtures(args: argparse.Namespace) -> int:
    from neurodecodekit.training.synthetic_signal_quality import (
        make_signal_quality_fixtures,
    )

    summary = make_signal_quality_fixtures(
        args.out_dir,
        contract_path=args.contract,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_signal_quality_fixtures(args: argparse.Namespace) -> int:
    from neurodecodekit.training.synthetic_signal_quality import (
        load_signal_quality_fixture_manifest,
    )

    summary = load_signal_quality_fixture_manifest(
        args.manifest,
        max_bytes=int(args.max_manifest_mb * 1024 * 1024),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_signal_quality(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.signal_quality import (
        SignalQualityLimits,
        inspect_signal_quality,
        write_signal_quality_artifacts,
    )

    mib = 1024 * 1024
    limits = SignalQualityLimits(
        max_channels=args.max_channels,
        max_channel_sample_values=args.max_sample_values,
        max_materialized_signal_array_bytes=int(args.max_array_mb * mib),
        max_runtime_seconds=args.max_runtime_sec,
        max_peak_rss_bytes=int(args.max_rss_mb * mib),
        max_output_bytes=int(args.max_output_mb * mib),
    )
    result = inspect_signal_quality(
        args.path,
        root_path=args.root,
        intake_report_path=args.intake_report,
        fixture_manifest_path=args.fixture_manifest,
        contract_path=args.contract,
        limits=limits,
    )
    summary = write_signal_quality_artifacts(
        result,
        args.out_dir,
        overwrite=args.overwrite,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_signal_quality_report(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.signal_quality import load_signal_quality_report

    summary = load_signal_quality_report(
        args.report,
        audit_path=args.audit,
        max_report_bytes=int(args.max_report_mb * 1024 * 1024),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_list_hf_files(args: argparse.Namespace) -> int:
    from neurodecodekit.datasets.hf_access import (
        list_repo_file_records,
        list_repo_files,
        write_file_list,
        write_file_record_list,
    )

    if args.with_sizes:
        revision, records = list_repo_file_records(
            args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
        )
        write_file_record_list(records, args.out)
        print(f"Wrote {len(records)} HF file metadata rows to {args.out}")
        print(f"Resolved revision: {revision}")
    else:
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
        event_source=args.event_source,
        stim_channel=args.stim_channel,
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
    print(f"  runtime: {summary.runtime_sec:.3f} sec")
    if summary.warnings:
        print("  warnings:")
        for warning in summary.warnings:
            print(f"    - {warning}")
    return 0


def _cmd_extract_eeg_windows(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.brainvision_extraction import (
        extract_brainvision_mat_windows,
    )

    summary = extract_brainvision_mat_windows(
        raw_path=args.raw,
        events_path=args.events,
        out_path=args.out,
        sfreq=args.sfreq,
        tmin=args.tmin,
        tmax=args.tmax,
        max_events=args.max_events,
        max_channels=args.max_channels,
        max_alignment_residual_sec=args.max_alignment_residual_ms / 1000.0,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    payload = summary.to_dict()
    if args.out_json:
        output = Path(args.out_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.out_json:
        print(f"Wrote extraction JSON to {args.out_json}")
    return 0


def _cmd_align_sequences(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.sequence_alignment import (
        align_key_sequences_by_trial_map,
        align_key_sequences_to_targets,
        build_mat_trial_index_map,
        build_sequence_alignment_report,
        load_key_event_time_sequences_from_npz_cache,
        load_key_sequences_from_npz_cache,
        load_mat_key_trigger_time_sequences,
        load_mat_sequence_sources,
        summarize_key_trigger_timing,
        TrialMappingUnavailableError,
        write_sequence_alignment_json,
        write_sequence_alignment_markdown,
    )

    started_at = time.perf_counter()
    key_sequences, cache_summary = load_key_sequences_from_npz_cache(args.cache)
    cache_time_sequences = load_key_event_time_sequences_from_npz_cache(args.cache)
    target_sequences, response_sequences, warnings = load_mat_sequence_sources(args.events)
    mat_time_sequences, timing_warnings = load_mat_key_trigger_time_sequences(args.events)
    trial_index_map = None
    try:
        trial_index_map = build_mat_trial_index_map(
            key_sequences,
            target_sequences,
            response_sequences,
            mat_time_sequences,
        )
    except TrialMappingUnavailableError as exc:
        warnings.append(f"strict_mat_trial_mapping_unavailable:{exc}")

    if trial_index_map is not None:
        mapped_indices = trial_index_map.raw_to_mat_trial_indices
        alignments = align_key_sequences_by_trial_map(
            key_sequences,
            target_sequences,
            mapped_indices,
            high_confidence_cer=args.high_confidence_cer,
            moderate_confidence_cer=args.moderate_confidence_cer,
        )
        response_alignments = (
            align_key_sequences_by_trial_map(
                key_sequences,
                response_sequences,
                mapped_indices,
                high_confidence_cer=args.high_confidence_cer,
                moderate_confidence_cer=args.moderate_confidence_cer,
            )
            if response_sequences
            else []
        )
        mapped_mat_time_sequences = [mat_time_sequences[index] for index in mapped_indices]
        key_trigger_timing_audit = summarize_key_trigger_timing(
            cache_time_sequences,
            mapped_mat_time_sequences,
        )
    else:
        alignments = align_key_sequences_to_targets(
            key_sequences,
            target_sequences,
            high_confidence_cer=args.high_confidence_cer,
            moderate_confidence_cer=args.moderate_confidence_cer,
        )
        response_alignments = align_key_sequences_to_targets(
            key_sequences,
            response_sequences,
            high_confidence_cer=args.high_confidence_cer,
            moderate_confidence_cer=args.moderate_confidence_cer,
        )
        key_trigger_timing_audit = None
    processing_runtime_sec = time.perf_counter() - started_at
    report = build_sequence_alignment_report(
        cache_path=args.cache,
        events_path=args.events,
        key_sequences=key_sequences,
        target_sequences=target_sequences,
        alignments=alignments,
        response_sequences=response_sequences,
        response_alignments=response_alignments,
        trial_index_map=trial_index_map,
        key_trigger_timing_audit=key_trigger_timing_audit,
        cache_summary=cache_summary,
        warnings=[*warnings, *timing_warnings],
        run_name=args.run_name,
        runtime_sec=processing_runtime_sec,
        high_confidence_cer=args.high_confidence_cer,
        moderate_confidence_cer=args.moderate_confidence_cer,
    )
    if args.out_json:
        write_sequence_alignment_json(report, args.out_json)
    if args.out_md:
        write_sequence_alignment_markdown(report, args.out_md)

    summary = report["summary"]
    print("Aligned typed key sequences")
    print(f"  cache: {args.cache}")
    print(f"  events: {args.events}")
    print(f"  key sequences: {summary['n_key_sequences']}")
    print(f"  target sequences: {summary['n_target_sequences']}")
    print(f"  exact matches: {summary['exact_match_count']}")
    print(f"  usable high/moderate matches: {summary['usable_high_or_moderate_count']}")
    print(f"  mean CER: {summary['mean_cer']}")
    print(f"  confidence counts: {summary['confidence_counts']}")
    print(f"  low-confidence indices: {summary['low_confidence_key_indices']}")
    print(f"  target index order monotonic: {summary['target_index_order_is_monotonic']}")
    print(f"  target index mapping identity: {summary['target_index_mapping_is_identity']}")
    print(f"  target index duplicates: {summary['target_index_duplicate_count']}")
    print(f"  target index backtracks: {summary['target_index_backtrack_count']}")
    print(f"  assignment strategy: {report['assignment']['strategy']}")
    print(f"  processing runtime: {report['resources']['runtime_sec']:.3f} sec")
    if report["trial_index_map"]:
        print(
            "  skipped MAT trial indices: "
            f"{report['trial_index_map']['skipped_mat_trial_indices']}"
        )
    if key_trigger_timing_audit:
        print(
            "  keyTrig exact-length trials: "
            f"{key_trigger_timing_audit['n_exact_length_trials']}/"
            f"{key_trigger_timing_audit['n_trials_compared']}"
        )
        print(f"  keyTrig paired keypresses: {key_trigger_timing_audit['n_keypress_pairs']}")
        if key_trigger_timing_audit["median_abs_residual_ms"] is not None:
            print(
                "  keyTrig median absolute residual: "
                f"{key_trigger_timing_audit['median_abs_residual_ms']:.3f} ms"
            )
            print(
                "  keyTrig p95 absolute residual: "
                f"{key_trigger_timing_audit['p95_abs_residual_ms']:.3f} ms"
            )
    else:
        print("  keyTrig timing audit: unavailable without a strict MAT trial map")
    if report.get("response_summary"):
        response_summary = report["response_summary"]
        print(f"  response exact matches: {response_summary['exact_match_count']}")
        print(
            f"  response usable high/moderate matches: {response_summary['usable_high_or_moderate_count']}"
        )
        print(f"  response mean CER: {response_summary['mean_cer']}")
        print(f"  response confidence counts: {response_summary['confidence_counts']}")
        print(
            f"  response low-confidence indices: {response_summary['low_confidence_key_indices']}"
        )
        print(
            f"  response target index order monotonic: {response_summary['target_index_order_is_monotonic']}"
        )
        print(
            f"  response target index mapping identity: {response_summary['target_index_mapping_is_identity']}"
        )
        print(
            f"  response target index duplicates: {response_summary['target_index_duplicate_count']}"
        )
        print(
            f"  response target index backtracks: {response_summary['target_index_backtrack_count']}"
        )
    if args.out_json:
        print(f"  wrote JSON: {args.out_json}")
        print(f"  JSON bytes: {Path(args.out_json).stat().st_size}")
    if args.out_md:
        print(f"  wrote Markdown: {args.out_md}")
        print(f"  Markdown bytes: {Path(args.out_md).stat().st_size}")
    if report["warnings"]:
        print("  warnings:")
        for warning in report["warnings"]:
            print(f"    - {warning}")
    return 0


def _cmd_make_synthetic_sentence_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.training.synthetic_sentences import save_synthetic_sentence_npz

    summary = save_synthetic_sentence_npz(
        args.out,
        sentences=args.sentences,
        channels=args.channels,
        letter_classes=args.letter_classes,
        min_word_length=args.min_word_length,
        max_word_length=args.max_word_length,
        token_width=args.token_width,
        gap_width=args.gap_width,
        sfreq=args.sfreq,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_sentence_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.sentence_npz import (
        load_sentence_npz_cache,
        write_sentence_cache_metadata_sidecar,
    )

    loaded = load_sentence_npz_cache(args.cache)
    print(json.dumps(loaded.summary.to_dict(), indent=2, sort_keys=True))
    if args.metadata_out:
        write_sentence_cache_metadata_sidecar(args.cache, args.metadata_out)
        print(f"Wrote sentence-cache metadata sidecar to {args.metadata_out}")
    return 0


def _cmd_inspect_representation_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.signal_representation import (
        load_signal_representation_cache,
        write_signal_representation_metadata_sidecar,
    )

    loaded = load_signal_representation_cache(args.cache)
    payload = {
        "representation": loaded.representation_summary.to_dict(),
        "semantic_sentence_cache": loaded.summary.to_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.metadata_out:
        write_signal_representation_metadata_sidecar(args.cache, args.metadata_out)
        print(f"Wrote representation metadata sidecar to {args.metadata_out}")
    return 0


def _cmd_make_neurotoken_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.neurotoken import project_sentence_cache_to_neurotokens

    if args.summary_json:
        summary_path = Path(args.summary_json)
        if summary_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to replace summary JSON: {summary_path}")
    result = project_sentence_cache_to_neurotokens(
        source_cache_path=args.source_cache,
        split_report_path=args.split_report,
        out_path=args.out,
        metadata_sidecar=args.metadata_out,
        modality=args.modality,
        device_type=args.device_type,
        subject_id=args.subject_id,
        session_id=args.session_id,
        source_sampling_rate_hz=args.source_sfreq,
        embedding_dim=args.embedding_dim,
        kernel_size=args.kernel_size,
        stride=args.stride,
        seed=args.seed,
        token_dtype=args.token_dtype,
        max_items=args.max_items,
        max_tokens_per_item=args.max_tokens_per_item,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    if args.summary_json:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_neurotoken_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.neurotoken import (
        load_neurotoken_cache,
        write_neurotoken_metadata_sidecar,
    )

    loaded = load_neurotoken_cache(args.cache)
    print(json.dumps(loaded.summary.to_dict(), indent=2, sort_keys=True))
    if args.metadata_out:
        write_neurotoken_metadata_sidecar(args.cache, args.metadata_out)
        print(f"Wrote neurotoken metadata sidecar to {args.metadata_out}")
    return 0


def _cmd_causal_replay_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.causal_replay_gate import run_causal_replay_gate

    report = run_causal_replay_gate(
        source_cache_path=args.source_cache,
        out_json_path=args.out_json,
        out_markdown_path=args.out_md,
        source_sampling_rate_hz=args.source_sfreq,
        embedding_dim=args.embedding_dim,
        kernel_size=args.kernel_size,
        stride=args.stride,
        seed=args.seed,
        token_dtype=args.token_dtype,
        compatibility_atol=args.compatibility_atol,
        max_items=args.max_items,
        max_source_mb=args.max_source_mb,
        max_samples_per_item=args.max_samples_per_item,
        max_chunk_samples=args.max_chunk_samples,
        max_tokens_per_item=args.max_tokens_per_item,
        max_total_pushes=args.max_total_pushes,
        max_working_mb=args.max_working_mb,
        max_state_kib=args.max_state_kib,
        max_runtime_sec=args.max_runtime_sec,
        max_peak_rss_mb=args.max_peak_rss_mb,
        max_report_mb=args.max_report_mb,
        overwrite=args.overwrite,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_make_causal_motif_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.causal_motifs import prepare_causal_motif_fixture

    manifest = prepare_causal_motif_fixture(
        args.out_dir,
        max_total_mb=args.max_total_mb,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_causal_motif_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.causal_motifs import (
        PARTITION_NAMES,
        load_causal_motif_manifest,
    )

    manifest = load_causal_motif_manifest(args.manifest)
    summary = {
        "schema": manifest["schema"],
        "proof_posture": manifest["proof_posture"],
        "registered_protocol_match": manifest["registered_protocol_match"],
        "protocol_sha256": manifest["protocol_sha256"],
        "metadata_only_no_partition_arrays_opened": True,
        "artifacts": manifest["artifacts"],
        "partitions": {
            split: {
                key: manifest["partitions"][split][key]
                for key in (
                    "path",
                    "sha256",
                    "bytes",
                    "items",
                    "signals_shape",
                    "valid_samples",
                    "valid_frames",
                    "n_classes",
                    "class_support",
                    "seed",
                )
            }
            for split in PARTITION_NAMES
        },
        "warnings": manifest["warnings"],
        "claim_boundaries": manifest["claim_boundaries"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_tiny_causal_encoder_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.tiny_causal_encoder_gate import (
        run_tiny_causal_encoder_gate,
    )

    report = run_tiny_causal_encoder_gate(
        fixture_manifest_path=args.fixture_manifest,
        checkpoint_out_path=args.checkpoint_out,
        out_json_path=args.out_json,
        out_markdown_path=args.out_md,
    )
    summary = {
        "proof_posture": report["proof_posture"],
        "gate_passed": report["gate_passed"],
        "decision": report["decision"],
        "registered_protocol_match": report["registered_protocol_match"],
        "validation_gate": report["selection"]["validation_gate"],
        "frozen_test": {
            "opened": report["frozen_test"]["opened"],
            "semantic_open_count": report["frozen_test"]["semantic_open_count"],
            "gate": report["frozen_test"]["gate"],
        },
        "streaming_replay_passed": (
            report["streaming_replay"]["passed"]
            if report["streaming_replay"]
            else False
        ),
        "resources": report["resources"],
        "artifacts": report["artifacts"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_make_ctc_symbol_stream_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.ctc_symbol_stream import (
        prepare_ctc_symbol_stream_fixture,
    )

    manifest = prepare_ctc_symbol_stream_fixture(
        args.out_dir,
        max_total_mb=args.max_total_mb,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_ctc_symbol_stream_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.ctc_symbol_stream import (
        PARTITION_NAMES,
        load_ctc_symbol_stream_manifest,
    )

    manifest = load_ctc_symbol_stream_manifest(args.manifest)
    summary = {
        "schema": manifest["schema"],
        "proof_posture": manifest["proof_posture"],
        "registered_protocol_match": manifest["registered_protocol_match"],
        "protocol_sha256": manifest["protocol_sha256"],
        "metadata_only_no_partition_arrays_opened": True,
        "artifacts": manifest["artifacts"],
        "partitions": {
            split: {
                key: manifest["partitions"][split][key]
                for key in (
                    "path",
                    "sha256",
                    "bytes",
                    "items",
                    "signals_shape",
                    "valid_samples",
                    "valid_frames",
                    "target_tokens",
                    "repeated_pair_count",
                    "seed",
                )
            }
            for split in PARTITION_NAMES
        },
        "warnings": manifest["warnings"],
        "claim_boundaries": manifest["claim_boundaries"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_streaming_ctc_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.streaming_ctc_gate import (
        run_streaming_ctc_gate,
    )

    report = run_streaming_ctc_gate(
        fixture_manifest_path=args.fixture_manifest,
        checkpoint_path=args.checkpoint,
        out_json_path=args.out_json,
        out_markdown_path=args.out_md,
    )
    summary = {
        "proof_posture": report["proof_posture"],
        "gate_passed": report["gate_passed"],
        "decision": report["decision"],
        "registered_protocol_match": report["registered_protocol_match"],
        "registered_checkpoint_match": report["registered_checkpoint_match"],
        "validation_gate": report["validation"]["gate"],
        "frozen_test": {
            "opened": report["frozen_test"]["opened"],
            "semantic_open_count": report["frozen_test"]["semantic_open_count"],
            "gate": report["frozen_test"]["gate"],
        },
        "streaming_replay_passed": report["streaming_replay"]["passed"],
        "resources": report["resources"],
        "artifacts": report["artifacts"],
        "warnings": report["warnings"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_make_blank_calibration_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.ctc_symbol_stream import (
        prepare_blank_calibration_fixture,
    )

    manifest = prepare_blank_calibration_fixture(
        args.out_dir,
        max_total_mb=args.max_total_mb,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _cmd_inspect_blank_calibration_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.ctc_symbol_stream import (
        PARTITION_NAMES,
        load_blank_calibration_manifest,
    )

    manifest = load_blank_calibration_manifest(args.manifest)
    summary = {
        "schema": manifest["schema"],
        "proof_posture": manifest["proof_posture"],
        "registered_protocol_match": manifest["registered_protocol_match"],
        "protocol_sha256": manifest["protocol_sha256"],
        "metadata_only_no_partition_arrays_opened": True,
        "access_contract": manifest["access_contract"],
        "artifacts": manifest["artifacts"],
        "partitions": {
            split: {
                key: manifest["partitions"][split][key]
                for key in (
                    "path",
                    "sha256",
                    "bytes",
                    "items",
                    "signals_shape",
                    "valid_samples",
                    "valid_frames",
                    "target_tokens",
                    "repeated_pair_count",
                    "seed",
                )
            }
            for split in PARTITION_NAMES
        },
        "warnings": manifest["warnings"],
        "claim_boundaries": manifest["claim_boundaries"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_blank_intercept_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.blank_intercept_gate import (
        run_blank_intercept_gate,
    )

    report = run_blank_intercept_gate(
        fixture_manifest_path=args.fixture_manifest,
        checkpoint_path=args.checkpoint,
        out_json_path=args.out_json,
        out_markdown_path=args.out_md,
    )
    summary = {
        "proof_posture": report["proof_posture"],
        "gate_passed": report["gate_passed"],
        "decision": report["decision"],
        "registered_protocol_match": report["registered_protocol_match"],
        "registered_checkpoint_match": report["registered_checkpoint_match"],
        "calibration": {
            "intercept": report["calibration"]["intercept"],
            "config_sha256": report["calibration"]["config_sha256"],
            "parameter_payload_sha256": report["calibration"][
                "parameter_payload_sha256"
            ],
            "train_metrics_before": report["calibration"]["train_metrics_before"],
            "train_metrics_after": report["calibration"]["train_metrics_after"],
        },
        "validation_gate": report["validation"]["gate"],
        "frozen_test": {
            "opened": report["frozen_test"]["opened"],
            "semantic_open_count": report["frozen_test"]["semantic_open_count"],
            "gate": report["frozen_test"]["gate"],
        },
        "streaming_replay_passed": report["streaming_replay"]["passed"],
        "resources": report["resources"],
        "artifacts": report["artifacts"],
        "warnings": report["warnings"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_make_precision_runtime_fixture(args: argparse.Namespace) -> int:
    _set_loop24_thread_environment()
    from neurodecodekit.training.precision_runtime_fixture import (
        prepare_precision_runtime_fixture,
        summarize_precision_runtime_manifest,
    )

    manifest = prepare_precision_runtime_fixture(args.out_dir)
    print(json.dumps(summarize_precision_runtime_manifest(manifest), indent=2, sort_keys=True))
    return 0


def _cmd_inspect_precision_runtime_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.precision_runtime_fixture import (
        load_precision_runtime_manifest,
        summarize_precision_runtime_manifest,
    )

    manifest = load_precision_runtime_manifest(args.manifest)
    print(json.dumps(summarize_precision_runtime_manifest(manifest), indent=2, sort_keys=True))
    return 0


def _cmd_local_precision_runtime_gate(args: argparse.Namespace) -> int:
    _set_loop24_thread_environment()
    from neurodecodekit.experiments.local_precision_runtime_gate import (
        inspect_local_precision_runtime_report,
        run_local_precision_runtime_gate,
    )

    report = run_local_precision_runtime_gate(
        fixture_manifest_path=args.fixture_manifest,
        checkpoint_path=args.checkpoint,
        out_dir=args.out_dir,
    )
    summary = inspect_local_precision_runtime_report(Path(args.out_dir) / "gate.json")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_inspect_local_precision_runtime_report(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.local_precision_runtime_gate import (
        inspect_local_precision_runtime_report,
    )

    summary = inspect_local_precision_runtime_report(args.report)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_make_causal_preprocessing_fixture(args: argparse.Namespace) -> int:
    _set_loop25_thread_environment()
    from neurodecodekit.training.causal_preprocessing_fixture import (
        prepare_causal_preprocessing_fixture,
        summarize_causal_preprocessing_manifest,
    )

    manifest = prepare_causal_preprocessing_fixture(
        args.out_dir,
        static_filter_bundle_path=args.static_filter_bundle,
    )
    print(json.dumps(summarize_causal_preprocessing_manifest(manifest), indent=2, sort_keys=True))
    return 0


def _cmd_inspect_causal_preprocessing_fixture(args: argparse.Namespace) -> int:
    from neurodecodekit.training.causal_preprocessing_fixture import (
        load_causal_preprocessing_manifest,
        summarize_causal_preprocessing_manifest,
    )

    manifest = load_causal_preprocessing_manifest(args.manifest)
    print(json.dumps(summarize_causal_preprocessing_manifest(manifest), indent=2, sort_keys=True))
    return 0


def _cmd_causal_preprocessing_gate(args: argparse.Namespace) -> int:
    _set_loop25_thread_environment()
    from neurodecodekit.experiments.causal_preprocessing_gate import (
        inspect_causal_preprocessing_report,
        run_causal_preprocessing_gate,
        run_static_causal_preprocessing_gate,
    )

    if args.static_only:
        if args.fixture_manifest or args.filter_bundle:
            raise ValueError("--static-only cannot be combined with fixture or filter inputs")
        report = run_static_causal_preprocessing_gate(out_dir=args.out_dir)
        report_path = Path(args.out_dir) / "static_gate.json"
    else:
        if not args.fixture_manifest or not args.filter_bundle:
            raise ValueError(
                "full gate requires --fixture-manifest and --filter-bundle; "
                "use --static-only for the prerequisite design gate"
            )
        report = run_causal_preprocessing_gate(
            fixture_manifest_path=args.fixture_manifest,
            filter_bundle_path=args.filter_bundle,
            out_dir=args.out_dir,
        )
        report_path = Path(args.out_dir) / "gate.json"
    summary = inspect_causal_preprocessing_report(report_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["gate_passed"] else 1


def _cmd_inspect_causal_preprocessing_report(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.causal_preprocessing_gate import (
        inspect_causal_preprocessing_report,
    )

    summary = inspect_causal_preprocessing_report(args.report)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _set_loop24_thread_environment() -> None:
    import os

    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[name] = "1"


def _set_loop25_thread_environment() -> None:
    import os

    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[name] = "1"


def _cmd_extract_sentence_cache(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.sentence_extraction import extract_fif_mat_sentence_cache

    summary = extract_fif_mat_sentence_cache(
        raw_path=args.raw,
        events_path=args.events,
        out_path=args.out,
        sfreq=args.sfreq,
        pre_context_sec=args.pre_context,
        post_context_sec=args.post_context,
        picks=args.picks,
        max_channels=args.max_channels,
        stim_channel=args.stim_channel,
        l_freq=args.l_freq,
        h_freq=args.h_freq,
        notch_freq=args.notch_freq,
        robust_scale=not args.no_robust_scale,
        clamp=args.clamp,
        scaler_fit_scope=args.scaler_fit_scope,
        split_text_normalization=args.split_text_normalization,
        max_sentences=args.max_sentences,
    )
    print("Extracted continuous sentence cache")
    print(f"  raw: {summary.raw_path}")
    print(f"  events: {summary.events_path}")
    print(f"  out: {summary.out_path}")
    print(f"  key events after sweep: {summary.n_key_events_after_sweep}")
    print(f"  sentences: {summary.n_sentences}")
    print(
        "  signal shape: "
        f"({summary.n_sentences}, {summary.n_channels}, {summary.max_timepoints}) "
        "[sentences, channels, padded timepoints]"
    )
    print(f"  valid input lengths: {summary.min_input_length}..{summary.max_input_length}")
    print(f"  target lengths: {summary.min_target_length}..{summary.max_target_length}")
    print(f"  sampling rate: {summary.sfreq:g} Hz")
    print(f"  scaler fit scope: {summary.scaler_fit_scope}")
    print(f"  trial mapping: {summary.trial_index_mapping_strategy}")
    if summary.skipped_mat_trial_indices:
        print(f"  skipped empty MAT trials: {summary.skipped_mat_trial_indices}")
    if summary.split_partition_counts is not None:
        print(f"  split partitions: {summary.split_partition_counts}")
    print(f"  output file size: {_format_bytes(summary.output_bytes)}")
    print(f"  runtime: {summary.runtime_sec:.3f} sec")
    if summary.peak_rss_bytes is not None:
        print(f"  process peak RSS: {_format_bytes(summary.peak_rss_bytes)}")
    if summary.warnings:
        print("  warnings:")
        for warning in summary.warnings:
            print(f"    - {warning}")
    if args.summary_json:
        summary_path = Path(args.summary_json)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"  wrote extraction summary: {summary_path}")
    return 0


def _cmd_apply_frozen_scaler(args: argparse.Namespace) -> int:
    from neurodecodekit.preprocess.frozen_scaler import (
        apply_frozen_train_scaler_to_cache,
    )

    summary = apply_frozen_train_scaler_to_cache(
        source_cache_path=args.source_cache,
        fit_cache_path=args.fit_cache,
        output_path=args.out,
        overwrite=args.overwrite,
    )
    print("Applied frozen train scaler")
    print(f"  source cache: {summary.source_cache}")
    print(f"  fit cache: {summary.fit_cache}")
    print(f"  output cache: {summary.output_cache}")
    print(f"  signal shape: {summary.signals_shape}")
    print(f"  output file size: {_format_bytes(summary.output_bytes)}")
    print(f"  runtime: {summary.runtime_sec:.3f} sec")
    print(f"  center SHA-256: {summary.center_sha256}")
    print(f"  scale SHA-256: {summary.scale_sha256}")
    if args.summary_json:
        summary_path = Path(args.summary_json)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"  wrote scaler summary: {summary_path}")
    return 0


def _cmd_sampling_rate_sweep(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.sampling_rate_sweep import run_sampling_rate_sweep

    report = run_sampling_rate_sweep(
        raw_path=args.raw,
        events_path=args.events,
        out_dir=args.out_dir,
        rates_hz=args.rates,
        pre_context_sec=args.pre_context,
        post_context_sec=args.post_context,
        picks=args.picks,
        max_channels=args.max_channels,
        stim_channel=args.stim_channel,
        l_freq=args.l_freq,
        h_freq=args.h_freq,
        notch_freq=args.notch_freq,
        robust_scale=not args.no_robust_scale,
        clamp=args.clamp,
        max_sentences=args.max_sentences,
        report_json_path=args.out_json,
        report_markdown_path=args.out_md,
        overwrite=args.overwrite,
    )
    print("Completed sampling-rate sweep")
    print(f"  proof posture: {report['proof_posture']}")
    for row in report["rates"]:
        print(
            f"  {row['rate_hz']:g} Hz: {_format_bytes(row['cache_bytes'])}, "
            f"{row['extraction_runtime_sec']:.3f} sec, "
            f"CTC feasible {row['ctc_feasible_rows_stride_1']}/{row['n_sentences']}"
        )
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    print(f"  decision: {report['decision']['status']}")
    return 0


def _cmd_channel_subset_sweep(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.channel_subset_sweep import run_channel_subset_sweep

    report = run_channel_subset_sweep(
        cache_path=args.cache,
        out_dir=args.out_dir,
        channel_counts=args.counts,
        strategies=args.strategies,
        seed=args.seed,
        max_output_mb=args.max_output_mb,
        report_json_path=args.out_json,
        report_markdown_path=args.out_md,
        overwrite=args.overwrite,
    )
    print("Completed channel-subset sweep")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  base channels: {report['base_cache']['n_channels']}")
    print(f"  subset caches: {len(report['rows'])}")
    print(
        "  subset caches + sidecars: "
        f"{_format_bytes(report['resources']['subset_cache_and_sidecar_bytes'])}"
    )
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    print(f"  decision: {report['decision']['status']}")
    return 0


def _cmd_precision_storage_sweep(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.precision_storage_sweep import (
        run_precision_storage_sweep,
    )

    report = run_precision_storage_sweep(
        cache_paths=args.cache,
        out_dir=args.out_dir,
        variants=args.variants,
        clip_abs=args.clip_abs,
        repetitions=args.repetitions,
        max_output_mb=args.max_output_mb,
        allow_clipping=args.allow_clipping,
        report_json_path=args.out_json,
        report_markdown_path=args.out_md,
        overwrite=args.overwrite,
    )
    print("Completed precision/storage sweep")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  source caches: {report['run']['source_cache_count']}")
    print(f"  representation artifacts: {report['run']['artifact_count']}")
    print(
        "  representation caches + sidecars: "
        f"{_format_bytes(report['resources']['representation_cache_and_sidecar_bytes'])}"
    )
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    print(f"  decision: {report['decision']['status']}")
    return 0


def _cmd_lazy_backend_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.lazy_backend_gate import run_lazy_backend_gate

    report = run_lazy_backend_gate(
        cache_paths=args.cache,
        out_dir=args.out_dir,
        row_counts=args.row_counts,
        repetitions=args.repetitions,
        max_full_load_ms=args.max_full_load_ms,
        max_partial_load_ms=args.max_partial_load_ms,
        max_peak_rss_mb=args.max_peak_rss_mb,
        revisit_cache_mb=args.revisit_cache_mb,
        report_json_path=args.out_json,
        report_markdown_path=args.out_md,
        overwrite=args.overwrite,
    )
    consistency = report["consistency"]
    print("Completed lazy-backend gate")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  caches: {report['run']['cache_count']}")
    print(f"  slowest full load: {consistency['slowest_full_load_median_ms']:.3f} ms")
    print(
        f"  highest worker peak RSS: {_format_bytes(consistency['highest_worker_peak_rss_bytes'])}"
    )
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    print(f"  decision: {report['decision']['status']}")
    return 0


def _cmd_split_protocol(args: argparse.Namespace) -> int:
    from neurodecodekit.evaluation.split_protocol import run_split_protocol

    report = run_split_protocol(
        cache_paths=args.cache,
        out_dir=args.out_dir,
        split_type=args.split_type,
        text_source=args.text_source,
        text_normalization=args.text_normalization,
        ratios={
            "train": args.train_ratio,
            "val": args.val_ratio,
            "test": args.test_ratio,
        },
        seed=args.seed,
        report_json_path=args.out_json,
        report_markdown_path=args.out_md,
        overwrite=args.overwrite,
    )
    membership = report["membership"]
    print("Completed split-protocol audit")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  source caches: {report['run']['source_cache_count']}")
    print(f"  rows: {report['run']['row_count']}")
    print(f"  partitions: {membership['partition_row_counts']}")
    print(f"  requested split usable: {membership['requested_split_usable']}")
    print(f"  strict training ready: {membership['strict_training_ready']}")
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    print(f"  decision: {report['decision']['status']}")
    return 0


def _cmd_sentence_prior_baseline(args: argparse.Namespace) -> int:
    from neurodecodekit.evaluation.report import (
        build_text_report,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.evaluation.split_protocol import (
        load_sentence_text_columns,
        load_training_partitions,
    )
    from neurodecodekit.models.prior_baseline import run_prior_baseline

    started_at = time.perf_counter()
    partitions = load_training_partitions(
        args.split_report,
        args.cache,
        eval_partition=args.eval_partition,
    )
    text_columns = load_sentence_text_columns(args.cache)
    if text_columns["source_cache_sha256"] != partitions.source_cache_sha256:
        raise ValueError("Text-only cache read does not match the split-report source hash.")
    targets = text_columns["target_texts"]
    train_targets = [targets[index] for index in partitions.train_indices]
    eval_targets = [targets[index] for index in partitions.eval_indices]
    baseline = run_prior_baseline(
        eval_targets=eval_targets,
        train_targets=train_targets,
        strategy=args.strategy,
        seed=args.seed,
    )
    baseline_metadata = baseline.metadata()
    baseline_metadata.update(
        {
            "split_mode": "split-protocol-v1-explicit-membership",
            "uses_neural_windows": False,
            "signal_array_members_loaded": False,
        }
    )
    report = build_text_report(
        targets=eval_targets,
        predictions=baseline.predictions,
        cache_summary={
            "path": str(args.cache),
            "bytes": Path(args.cache).stat().st_size,
            "kind": "sentence-cache-text-members-only",
            "signals_shape": None,
            "warnings": [],
        },
        run_name=args.run_name or "sentence_prior_split_protocol_v1",
        split=f"split-protocol-v1-{args.eval_partition}",
        max_examples=args.max_examples,
        warnings=[
            *baseline.warnings,
            "sentence_prior_reader_loaded_no_signal_array",
            "one_session_one_person_sentence_text_evaluation_only",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
        ],
        runtime_sec=round(time.perf_counter() - started_at, 6),
    )
    report["baseline"] = baseline_metadata
    report["split_protocol"] = partitions.metadata()
    report["text_reader"] = {
        "signal_member_names": text_columns["signal_member_names"],
        "signal_array_members_loaded": text_columns["signal_array_members_loaded"],
    }
    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)
    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _cmd_tiny_ctc_baseline(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.signal_representation import load_sentence_cache_auto
    from neurodecodekit.evaluation.report import (
        build_text_report,
        compare_paired_predictions,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.evaluation.split_protocol import load_training_partitions
    from neurodecodekit.models.prior_baseline import run_prior_baseline
    from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline_from_cache

    started_at = time.perf_counter()
    partitions = (
        load_training_partitions(
            args.split_report,
            args.cache,
            eval_partition=args.eval_partition,
        )
        if args.split_report
        else None
    )
    cache = load_sentence_cache_auto(args.cache)
    baseline = run_tiny_ctc_baseline_from_cache(
        cache,
        train_fraction=args.train_fraction,
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_channels=args.hidden_channels,
        device=args.device,
        num_threads=args.num_threads,
        max_restarts=args.max_restarts,
        partition_indices=(
            {
                "train": partitions.train_indices,
                "val": partitions.validation_indices,
                "test": partitions.test_indices,
            }
            if partitions is not None
            else None
        ),
        eval_partition=args.eval_partition,
        split_metadata=(partitions.metadata() if partitions is not None else None),
    )
    warnings = list(baseline.warnings)
    if cache.summary.kind.startswith("synthetic"):
        warnings.append("ctc_trained_on_synthetic_cache_only")
    else:
        warnings.extend(
            [
                "single_session_sentence_text_result_not_session_or_subject_generalization",
            ]
        )
        if baseline.n_eval_rows < 20:
            warnings.append("small_eval_partition_too_uncertain_for_a_performance_claim")
    report = build_text_report(
        targets=baseline.targets,
        predictions=baseline.predictions,
        cache_summary=cache.summary.to_dict(),
        run_name=args.run_name or "tiny_ctc_sentence_baseline",
        split=(
            args.split
            or (
                f"split-protocol-v1-{args.eval_partition}"
                if partitions is not None
                else "deterministic-text-hash-holdout"
            )
        ),
        max_examples=args.max_examples,
        warnings=warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - started_at, 6)
    report["baseline"] = baseline.metadata()
    if partitions is not None:
        report["split_protocol"] = partitions.metadata()

    train_targets = [cache.target_texts[index] for index in baseline.train_indices]
    prior = run_prior_baseline(
        eval_targets=baseline.targets,
        train_targets=[str(value) for value in train_targets],
        strategy="most-frequent",
        seed=args.seed,
    )
    prior_report = build_text_report(
        targets=baseline.targets,
        predictions=prior.predictions,
        max_examples=1,
        warnings=prior.warnings,
    )
    report["comparators"] = {
        "prior_only": {
            "baseline": prior.metadata(),
            "summary": prior_report["summary"],
        }
    }
    report["comparisons"] = {
        "tiny_ctc_vs_prior_only": compare_paired_predictions(
            targets=baseline.targets,
            predictions_a=baseline.predictions,
            predictions_b=prior.predictions,
            label_a="tiny_ctc",
            label_b="prior_only",
            bootstrap_iterations=5000,
            seed=17,
        )
    }

    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)
    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.out_predictions:
        print(f"Wrote tiny-CTC predictions to {args.out_predictions}")
    if args.out_json:
        print(f"Wrote report JSON to {args.out_json}")
    if args.out_md:
        print(f"Wrote report Markdown to {args.out_md}")
    return 0


def _cmd_cross_session_ctc(args: argparse.Namespace) -> int:
    from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
    from neurodecodekit.evaluation.cross_session import (
        summarize_text_overlap,
        validate_cross_session_contract,
    )
    from neurodecodekit.evaluation.report import (
        build_text_report,
        compare_paired_predictions,
        write_report_json,
        write_report_markdown,
    )
    from neurodecodekit.evaluation.split_protocol import load_training_partitions
    from neurodecodekit.models.prior_baseline import run_prior_baseline
    from neurodecodekit.models.tiny_ctc import run_tiny_ctc_cross_session

    started_at = time.perf_counter()
    partitions = load_training_partitions(
        args.train_split_report,
        args.train_cache,
        eval_partition="test",
    )
    train_cache = load_sentence_npz_cache(args.train_cache)
    eval_cache = load_sentence_npz_cache(args.eval_cache)
    contract = validate_cross_session_contract(
        train_cache=train_cache,
        eval_cache=eval_cache,
        partitions=partitions,
    )
    source_partitions = {
        "train": partitions.train_indices,
        "val": partitions.validation_indices,
        "test": partitions.test_indices,
    }
    baseline = run_tiny_ctc_cross_session(
        train_signals=train_cache.signals,
        train_input_lengths=train_cache.input_lengths,
        train_target_token_ids=train_cache.target_token_ids,
        train_target_lengths=train_cache.target_lengths,
        train_target_texts=train_cache.target_texts.tolist(),
        eval_signals=eval_cache.signals,
        eval_input_lengths=eval_cache.input_lengths,
        eval_target_token_ids=eval_cache.target_token_ids,
        eval_target_lengths=eval_cache.target_lengths,
        eval_target_texts=eval_cache.target_texts.tolist(),
        source_partitions=source_partitions,
        split_metadata=partitions.metadata(),
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_channels=args.hidden_channels,
        device=args.device,
        num_threads=args.num_threads,
        max_restarts=args.max_restarts,
    )
    train_targets = [str(train_cache.target_texts[index]) for index in partitions.train_indices]
    prior = run_prior_baseline(
        eval_targets=baseline.targets,
        train_targets=train_targets,
        strategy="most-frequent",
        seed=args.seed,
    )
    warnings = [
        *baseline.warnings,
        "one_subject_two_sessions_result_not_population_generalization",
        "eval_cache_scaled_with_source_train_statistics_only",
        "source_sentence_validation_and_test_rows_never_used_by_cross_session_model",
        "empty_mat_trials_excluded_by_nonempty_keyTrig_trial_mapping",
        "cross_session_result_does_not_establish_real_time_decoding",
        "real_cache_records_physical_typing_not_arbitrary_thoughts",
    ]
    report = build_text_report(
        targets=baseline.targets,
        predictions=baseline.predictions,
        cache_summary=eval_cache.summary.to_dict(),
        run_name=args.run_name or "s21_session1_train_to_session2_eval_tiny_ctc",
        split="same-subject-independent-session-holdout",
        max_examples=args.max_examples,
        warnings=warnings,
    )
    report["run"]["runtime_sec"] = round(time.perf_counter() - started_at, 6)
    report["baseline"] = baseline.metadata()
    report["cross_session_protocol"] = contract
    report["text_overlap"] = {
        "typed_targets": summarize_text_overlap(
            train_texts=train_targets,
            eval_texts=baseline.targets,
        ),
        "reference_prompts": summarize_text_overlap(
            train_texts=[
                str(train_cache.reference_texts[index]) for index in partitions.train_indices
            ],
            eval_texts=[str(value) for value in eval_cache.reference_texts.tolist()],
        ),
    }
    prior_report = build_text_report(
        targets=baseline.targets,
        predictions=prior.predictions,
        max_examples=1,
        warnings=prior.warnings,
    )
    report["comparators"] = {
        "prior_only": {
            "baseline": prior.metadata(),
            "summary": prior_report["summary"],
        }
    }
    report["comparisons"] = {
        "tiny_ctc_vs_prior_only": compare_paired_predictions(
            targets=baseline.targets,
            predictions_a=baseline.predictions,
            predictions_b=prior.predictions,
            label_a="tiny_ctc_cross_session",
            label_b="prior_only_source_train",
            bootstrap_iterations=5000,
            seed=17,
        )
    }
    if args.out_predictions:
        _write_text_rows(args.out_predictions, baseline.predictions)
    if args.out_json:
        write_report_json(report, args.out_json)
    if args.out_md:
        write_report_markdown(report, args.out_md)

    comparison = report["comparisons"]["tiny_ctc_vs_prior_only"]
    print("Completed same-subject cross-session CTC evaluation")
    print(f"  source train rows: {baseline.n_train_rows}")
    print(f"  reserved source validation rows: {baseline.n_reserved_validation_rows}")
    print(f"  reserved source test rows: {baseline.n_reserved_test_rows}")
    print(f"  independent session eval rows: {baseline.n_eval_rows}")
    print(f"  train CER: {baseline.train_cer:.6f}")
    print(f"  eval corpus CER: {report['summary']['corpus_cer']:.6f}")
    print(f"  prior corpus CER: {prior_report['summary']['corpus_cer']:.6f}")
    print(f"  tiny minus prior CER: {comparison['corpus_cer_delta_a_minus_b']:.6f}")
    print(f"  runtime: {report['run']['runtime_sec']:.3f} sec")
    if args.out_json:
        print(f"  wrote JSON: {args.out_json}")
    if args.out_md:
        print(f"  wrote Markdown: {args.out_md}")
    return 0


def _cmd_synthetic_adapter_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.synthetic_adapter_gate import (
        run_synthetic_adapter_gate,
    )

    report = run_synthetic_adapter_gate(
        out_dir=args.out_dir,
        sentences=args.sentences,
        channels=args.channels,
        letter_classes=args.letter_classes,
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_channels=args.hidden_channels,
        num_threads=args.num_threads,
        min_validation_cer_gain=args.min_validation_cer_gain,
        bootstrap_iterations=args.bootstrap_iterations,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    print("Completed synthetic session-adapter gate")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  partition rows: {report['protocol']['partition_counts']}")
    print(f"  selected adapter: {report['validation']['selected_adapter']}")
    print(
        "  validation identity/adapted CER: "
        f"{report['validation']['identity']['corpus_cer']:.6f}/"
        f"{report['validation']['robust_channel_affine']['corpus_cer']:.6f}"
    )
    print(
        "  holdout identity/adapted/prior CER: "
        f"{report['holdout']['identity']['corpus_cer']:.6f}/"
        f"{report['holdout']['robust_channel_affine']['corpus_cer']:.6f}/"
        f"{report['holdout']['prior_only']['corpus_cer']:.6f}"
    )
    print(f"  runtime: {report['run']['runtime_sec']:.3f} sec")
    print(f"  artifact bytes: {report['resources']['total_artifact_bytes']}")
    print(f"  decision: {report['decision']['status']}")
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    return 0


def _cmd_synthetic_calibration_curve(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.synthetic_calibration_curve import (
        run_synthetic_calibration_curve,
    )

    report = run_synthetic_calibration_curve(
        out_dir=args.out_dir,
        sentences=args.sentences,
        calibration_sentences=args.calibration_sentences,
        channels=args.channels,
        letter_classes=args.letter_classes,
        seed=args.seed,
        calibration_sizes=args.calibration_sizes,
        shift_seeds=args.shift_seeds,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_channels=args.hidden_channels,
        num_threads=args.num_threads,
        min_stationary_validation_cer_gain=(
            args.min_stationary_validation_cer_gain
        ),
        bootstrap_iterations=args.bootstrap_iterations,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    selected = report["decision"]["selected_calibration_rows"]
    print("Completed synthetic calibration-size and shift-stress study")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  calibration sizes: {report['run']['calibration_sizes']}")
    print(f"  shift seeds: {report['run']['shift_seeds']}")
    print(f"  shift families: {report['run']['shift_families']}")
    print(f"  selected stationary calibration rows: {selected}")
    for row in report["holdout"]["aggregate"]:
        print(
            f"  {row['shift_family']} holdout identity/adapted CER: "
            f"{row['median_identity_cer']:.6f}/{row['median_adapted_cer']:.6f}"
        )
    print(f"  runtime: {report['run']['runtime_sec']:.3f} sec")
    print(f"  artifact bytes: {report['resources']['total_artifact_bytes']}")
    print(f"  decision: {report['decision']['status']}")
    print(f"  report JSON: {report['artifact_paths']['report_json']}")
    print(f"  report Markdown: {report['artifact_paths']['report_markdown']}")
    return 0


def _cmd_eeg_bridge_gate(args: argparse.Namespace) -> int:
    from neurodecodekit.experiments.eeg_bridge_gate import run_eeg_bridge_gate

    result = run_eeg_bridge_gate(
        manifest_path=args.manifest,
        out_dir=args.out_dir,
        revision=args.revision,
        max_download_mb=args.max_download_mb,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    report = result["report"]
    audit = result["audit"]
    bundle = report["selected_bundle"]
    print("Completed metadata-only EEG bridge gate")
    print(f"  proof posture: {report['proof_posture']}")
    print(f"  selected: {bundle['subject']} session {bundle['session']} {bundle['block']}")
    print(f"  files/bytes: {bundle['n_files']}/{bundle['estimated_bytes']}")
    print(f"  gate passed: {report['gate_passed']}")
    print(f"  decision: {report['decision']['status']}")
    print(f"  data downloads: {audit['data_downloads']}")
    print(f"  raw signal reads: {audit['raw_signal_reads']}")
    print(f"  runtime: {audit['runtime_sec']:.3f} sec")
    print(f"  peak RSS: {audit['peak_rss_bytes']} bytes")
    print(f"  artifact bytes: {audit['total_artifact_bytes']}")
    print(f"  output: {result['output_dir']}")
    return 0


def _cmd_build_leaderboard(args: argparse.Namespace) -> int:
    from neurodecodekit.evaluation.report_card import (
        build_leaderboard,
        format_leaderboard_table,
    )

    result = build_leaderboard(
        spec_path=args.spec,
        out_dir=args.out_dir,
        project_root=args.project_root,
        max_cards=args.max_cards,
        max_output_mb=args.max_output_mb,
        overwrite=args.overwrite,
    )
    leaderboard = result["leaderboard"]
    audit = result["audit"]
    print(format_leaderboard_table(leaderboard))
    print("Completed artifact-only report-card build")
    print(f"  cards/cohorts: {leaderboard['summary']['card_count']}/{leaderboard['summary']['cohort_count']}")
    print(f"  cross-cohort ranking: {leaderboard['summary']['cross_cohort_ranking_performed']}")
    print(f"  raw data reads: {audit['raw_data_reads']}")
    print(f"  signal arrays loaded: {audit['signal_array_members_loaded']}")
    print(f"  model runs: {audit['model_runs_triggered']}")
    print(f"  runtime: {audit['runtime_sec']:.3f} sec")
    print(f"  peak RSS: {audit['peak_rss_bytes']} bytes")
    print(f"  artifact bytes: {audit['total_artifact_bytes']}")
    print(f"  output: {result['output_dir']}")
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    from neurodecodekit.demo.app import audit_demo, launch_demo

    if args.audit_only:
        report = audit_demo(args.project_root)
        if args.out_json:
            output = Path(args.out_json)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print("Completed local demo startup audit")
        print(f"  proof posture: {report['proof_posture']}")
        print(f"  Gradio: {report['gradio_version']}")
        print(f"  examples: {report['display_examples']}")
        print(f"  evidence load: {report['load_evidence_sec']:.3f} sec")
        print(f"  total build: {report['build_total_sec']:.3f} sec")
        print(f"  peak RSS: {report['peak_rss_bytes']} bytes")
        print(f"  gate passed: {report['gate_passed']}")
        if args.out_json:
            print(f"  wrote JSON: {args.out_json}")
        return 0 if report["gate_passed"] else 1

    launch_demo(
        args.project_root,
        server_name=args.host,
        server_port=args.port,
        inbrowser=args.inbrowser,
    )
    return 0


def _comma_separated_ints(value: str) -> tuple[int, ...]:
    try:
        values = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated integers") from exc
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


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
        session=args.session,
        revision=args.revision,
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
        revision=selection.revision,
        max_workers=args.max_workers,
        dry_run=dry_run,
    )
    return 0


def _print_selection_plan(selection: Any, *, heading: str) -> None:
    from neurodecodekit.datasets.selection import format_bytes

    print(heading)
    print(f"  repo: {selection.repo_id}")
    print(f"  revision: {selection.revision or 'unpinned'}")
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
    p.add_argument(
        "--cache", default=None, help="Optional B2Q-mini NPZ cache for labels/storage metadata."
    )
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--split", default=None, help="Split/protocol label, e.g. synthetic-smoke or subject."
    )
    p.add_argument(
        "--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10."
    )
    p.add_argument(
        "--identity-smoke",
        action="store_true",
        help="Use targets as predictions for plumbing tests. This is not a model result.",
    )
    p.set_defaults(func=_cmd_report)

    p = sub.add_parser("prior-baseline", help="Run a no-brain label/text prior baseline.")
    p.add_argument("--targets", default=None, help="Eval targets, one row per example.")
    p.add_argument(
        "--cache",
        default=None,
        help="Optional B2Q-mini NPZ cache; labels become targets if --targets is absent.",
    )
    p.add_argument(
        "--train-targets", default=None, help="Optional train targets used to fit the prior."
    )
    p.add_argument(
        "--train-cache", default=None, help="Optional train cache whose labels fit the prior."
    )
    p.add_argument(
        "--strategy",
        default="most-frequent",
        choices=["most-frequent", "frequency-sample", "uniform-random"],
        help="No-brain prediction strategy. Default: most-frequent.",
    )
    p.add_argument("--seed", type=int, default=7, help="Seed for sampling strategies. Default: 7.")
    p.add_argument(
        "--out-predictions", default=None, help="Optional one-prediction-per-line output path."
    )
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--split", default=None, help="Split/protocol label, e.g. synthetic-smoke or subject."
    )
    p.add_argument(
        "--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10."
    )
    p.set_defaults(func=_cmd_prior_baseline)

    p = sub.add_parser(
        "template-baseline", help="Run a tiny nearest-centroid baseline over cache windows."
    )
    p.add_argument(
        "--cache", default=None, help="Single B2Q-mini cache to split into train/eval rows."
    )
    p.add_argument(
        "--train-cache", default=None, help="Optional train cache for separate-cache evaluation."
    )
    p.add_argument(
        "--eval-cache", default=None, help="Optional eval cache for separate-cache evaluation."
    )
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.5,
        help="Single-cache stratified train fraction. Default: 0.5.",
    )
    p.add_argument(
        "--seed", type=int, default=7, help="Seed for deterministic holdout split. Default: 7."
    )
    p.add_argument(
        "--out-predictions", default=None, help="Optional one-prediction-per-line output path."
    )
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--split", default=None, help="Split/protocol label, e.g. synthetic-holdout or session."
    )
    p.add_argument(
        "--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10."
    )
    p.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=2000,
        help="Paired holdout bootstrap samples. Default: 2000.",
    )
    p.set_defaults(func=_cmd_template_baseline)

    p = sub.add_parser(
        "tiny-conv-baseline",
        help="Run an optional CPU-safe tiny ConvNet baseline over cache windows. Requires [ml].",
    )
    p.add_argument(
        "--cache", default=None, help="Single B2Q-mini cache to split into train/eval rows."
    )
    p.add_argument(
        "--train-cache", default=None, help="Optional train cache for separate-cache evaluation."
    )
    p.add_argument(
        "--eval-cache", default=None, help="Optional eval cache for separate-cache evaluation."
    )
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.5,
        help="Single-cache stratified train fraction. Default: 0.5.",
    )
    p.add_argument(
        "--seed", type=int, default=7, help="Seed for deterministic holdout/training. Default: 7."
    )
    p.add_argument("--epochs", type=int, default=20, help="Training epochs. Default: 20.")
    p.add_argument("--batch-size", type=int, default=16, help="Mini-batch size. Default: 16.")
    p.add_argument(
        "--learning-rate", type=float, default=0.01, help="Adam learning rate. Default: 0.01."
    )
    p.add_argument(
        "--hidden-channels", type=int, default=8, help="Conv hidden channels. Default: 8."
    )
    p.add_argument(
        "--device", default="cpu", choices=["cpu", "cuda"], help="Torch device. Default: cpu."
    )
    p.add_argument("--num-threads", type=int, default=1, help="Torch CPU threads. Default: 1.")
    p.add_argument(
        "--out-predictions", default=None, help="Optional one-prediction-per-line output path."
    )
    p.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--split", default=None, help="Split/protocol label, e.g. synthetic-holdout or session."
    )
    p.add_argument(
        "--max-examples", type=int, default=10, help="Maximum examples to include. Default: 10."
    )
    p.set_defaults(func=_cmd_tiny_conv_baseline)

    p = sub.add_parser(
        "tiny-ctc-baseline",
        help="Train an optional CPU-safe CTC model over continuous sentence signals. Requires [ml].",
    )
    p.add_argument("--cache", required=True, help="Validated B2Q sentence-cache NPZ path.")
    p.add_argument(
        "--split-report",
        default=None,
        help=(
            "Strict-ready Split Protocol v1 JSON bound to this cache. When set, "
            "its train/eval indices replace the legacy holdout."
        ),
    )
    p.add_argument(
        "--eval-partition",
        choices=["val", "test"],
        default="test",
        help="Explicit split-report partition to evaluate. Default: test.",
    )
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.8,
        help="Fraction of unique sentence texts assigned to train. Default: 0.8.",
    )
    p.add_argument("--seed", type=int, default=7, help="Deterministic split/training seed.")
    p.add_argument("--epochs", type=int, default=60, help="Training epochs. Default: 60.")
    p.add_argument("--batch-size", type=int, default=16, help="Mini-batch size. Default: 16.")
    p.add_argument(
        "--learning-rate",
        type=float,
        default=0.02,
        help="Adam learning rate. Default: 0.02.",
    )
    p.add_argument("--hidden-channels", type=int, default=16, help="Temporal ConvNet width.")
    p.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "mps", "cuda"],
        help="Torch device. Default: cpu.",
    )
    p.add_argument("--num-threads", type=int, default=1, help="Torch CPU threads. Default: 1.")
    p.add_argument(
        "--max-restarts",
        type=int,
        default=3,
        help="Maximum deterministic restarts after a degenerate training fit. Default: 3.",
    )
    p.add_argument("--out-predictions", default=None, help="Optional text predictions path.")
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--split", default=None, help="Protocol label for the report.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum report examples.")
    p.set_defaults(func=_cmd_tiny_ctc_baseline)

    p = sub.add_parser(
        "cross-session-ctc",
        help=(
            "Train tiny CTC on strict source-session train rows and evaluate an "
            "independent frozen-scaled session. Requires [ml]."
        ),
    )
    p.add_argument("--train-cache", required=True, help="Strict split-bound source cache.")
    p.add_argument(
        "--train-split-report",
        required=True,
        help="Strict-ready Split Protocol v1 JSON bound to the source cache.",
    )
    p.add_argument(
        "--eval-cache",
        required=True,
        help="Independent session cache scaled with the source train statistics.",
    )
    p.add_argument("--seed", type=int, default=7, help="Training seed. Default: 7.")
    p.add_argument("--epochs", type=int, default=60, help="Training epochs. Default: 60.")
    p.add_argument("--batch-size", type=int, default=16, help="Mini-batch size. Default: 16.")
    p.add_argument(
        "--learning-rate",
        type=float,
        default=0.02,
        help="Adam learning rate. Default: 0.02.",
    )
    p.add_argument("--hidden-channels", type=int, default=16, help="Temporal ConvNet width.")
    p.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "mps", "cuda"],
        help="Torch device. Default: cpu.",
    )
    p.add_argument("--num-threads", type=int, default=1, help="Torch CPU threads. Default: 1.")
    p.add_argument(
        "--max-restarts",
        type=int,
        default=1,
        help="Maximum training-fit-selected initializations. Default: 1.",
    )
    p.add_argument("--out-predictions", default=None, help="Optional text predictions path.")
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument("--max-examples", type=int, default=10, help="Maximum report examples.")
    p.set_defaults(func=_cmd_cross_session_ctc)

    p = sub.add_parser(
        "synthetic-adapter-gate",
        help=(
            "Test unlabeled robust channel-affine session alignment on a bounded "
            "synthetic shift. Never loads real caches. Requires [ml]."
        ),
    )
    p.add_argument("--out-dir", required=True, help="Directory for compact gate artifacts.")
    p.add_argument("--sentences", type=int, default=96, help="Synthetic rows. Default: 96.")
    p.add_argument("--channels", type=int, default=6, help="Synthetic channels. Default: 6.")
    p.add_argument(
        "--letter-classes", type=int, default=4, help="Synthetic letters. Default: 4."
    )
    p.add_argument("--seed", type=int, default=23, help="Protocol/training seed. Default: 23.")
    p.add_argument("--epochs", type=int, default=50, help="Tiny CTC epochs. Default: 50.")
    p.add_argument("--batch-size", type=int, default=16, help="Batch size. Default: 16.")
    p.add_argument(
        "--learning-rate", type=float, default=0.02, help="Adam rate. Default: 0.02."
    )
    p.add_argument(
        "--hidden-channels", type=int, default=16, help="Tiny CTC width. Default: 16."
    )
    p.add_argument(
        "--num-threads",
        type=int,
        default=1,
        choices=[1],
        help="Torch CPU threads. Fixed at 1.",
    )
    p.add_argument(
        "--min-validation-cer-gain",
        type=float,
        default=0.10,
        help="Absolute validation CER gain required to select adaptation. Default: 0.10.",
    )
    p.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=2000,
        help="Paired holdout bootstrap samples. Default: 2000.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=2.0,
        help="Hard cap for reports and predictions. Default: 2 MiB.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing gate report and prediction artifacts.",
    )
    p.set_defaults(func=_cmd_synthetic_adapter_gate)

    p = sub.add_parser(
        "synthetic-calibration-curve",
        help=(
            "Measure an unlabeled robust-affine calibration curve across stationary, "
            "channel-mixing, and time-varying synthetic shifts. Never loads real caches."
        ),
    )
    p.add_argument("--out-dir", required=True, help="Directory for compact study artifacts.")
    p.add_argument("--sentences", type=int, default=96, help="Source rows. Default: 96.")
    p.add_argument(
        "--calibration-sentences",
        type=int,
        default=48,
        help="Independent unlabeled calibration-pool rows. Default: 48.",
    )
    p.add_argument("--channels", type=int, default=6, help="Synthetic channels. Default: 6.")
    p.add_argument(
        "--letter-classes", type=int, default=4, help="Synthetic letters. Default: 4."
    )
    p.add_argument("--seed", type=int, default=23, help="Source/model seed. Default: 23.")
    p.add_argument(
        "--calibration-sizes",
        type=_comma_separated_ints,
        default=(1, 2, 4, 8, 16, 32),
        help="Five or more nested row counts. Default: 1,2,4,8,16,32.",
    )
    p.add_argument(
        "--shift-seeds",
        type=_comma_separated_ints,
        default=(101, 211, 307),
        help="Two or more shift seeds. Default: 101,211,307.",
    )
    p.add_argument("--epochs", type=int, default=50, help="Tiny CTC epochs. Default: 50.")
    p.add_argument("--batch-size", type=int, default=16, help="Batch size. Default: 16.")
    p.add_argument(
        "--learning-rate", type=float, default=0.02, help="Adam rate. Default: 0.02."
    )
    p.add_argument(
        "--hidden-channels", type=int, default=16, help="Tiny CTC width. Default: 16."
    )
    p.add_argument(
        "--num-threads",
        type=int,
        default=1,
        choices=[1],
        help="Torch CPU threads. Fixed at 1.",
    )
    p.add_argument(
        "--min-stationary-validation-cer-gain",
        type=float,
        default=0.10,
        help="Median validation CER gain needed for a row-count recommendation. Default: 0.10.",
    )
    p.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=1000,
        help="Paired holdout bootstrap samples per shift seed. Default: 1000.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=4.0,
        help="Hard cap for JSON/Markdown/CSV artifacts. Default: 4 MiB.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing study artifacts.",
    )
    p.set_defaults(func=_cmd_synthetic_calibration_curve)

    p = sub.add_parser(
        "eeg-bridge-gate",
        help=(
            "Select one complete task-compatible SpanishBCBL EEG bundle from local "
            "metadata. Downloads no data and opens no signal."
        ),
    )
    p.add_argument("--manifest", required=True, help="Sized SpanishBCBL manifest JSONL.")
    p.add_argument("--out-dir", required=True, help="Output directory for gate artifacts.")
    p.add_argument("--revision", required=True, help="Pinned 40-character dataset commit SHA.")
    p.add_argument(
        "--max-download-mb",
        type=float,
        default=128.0,
        help="Maximum planned four-file EEG bundle size in MiB. Default: 128.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=1.0,
        help="Maximum gate artifact size in MiB. Default: 1.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the gate's named files in an existing output directory.",
    )
    p.set_defaults(func=_cmd_eeg_bridge_gate)

    p = sub.add_parser(
        "demo",
        help=(
            "Launch the local artifact-backed evidence console or audit its startup. "
            "Requires [demo]; never trains a model or fetches data."
        ),
    )
    p.add_argument(
        "--project-root",
        default=".",
        help="Repository root containing compact cache/report artifacts. Default: current directory.",
    )
    p.add_argument("--host", default="127.0.0.1", help="Local bind host. Default: 127.0.0.1.")
    p.add_argument("--port", type=int, default=7860, help="Local port. Default: 7860.")
    p.add_argument("--inbrowser", action="store_true", help="Open the local URL in a browser.")
    p.add_argument(
        "--audit-only",
        action="store_true",
        help="Load evidence and build the UI without starting a server.",
    )
    p.add_argument(
        "--out-json",
        default=None,
        help="Optional audit JSON path; used only with --audit-only.",
    )
    p.set_defaults(func=_cmd_demo)

    p = sub.add_parser("manifest-from-paths", help="Build JSONL manifest from a newline path list.")
    p.add_argument("--paths", required=True, help="Text file containing one repo path per line.")
    p.add_argument("--out", required=True, help="Output manifest JSONL path.")
    p.add_argument("--repo-id", default="bcbl190626/SpanishBCBL")
    p.set_defaults(func=_cmd_manifest_from_paths)

    p = sub.add_parser("inspect-manifest", help="Summarize a manifest JSONL file.")
    p.add_argument("--manifest", required=True)
    p.set_defaults(func=_cmd_inspect_manifest)

    p = sub.add_parser(
        "inspect-recording",
        help=(
            "Create a bounded level-0 local recording report without opening "
            "binary signal, event, label, or target content."
        ),
    )
    p.add_argument(
        "--path",
        required=True,
        help="Local .vhdr/.edf/.bdf/.set/.fif file or BIDS root directory.",
    )
    p.add_argument(
        "--root",
        default=None,
        help="Optional security root; the resolved source and companions must stay inside it.",
    )
    p.add_argument("--out-dir", required=True, help="Directory for intake.json/.md/audit.json.")
    p.add_argument(
        "--registry",
        default=None,
        help="Optional local dataset-registry JSON to bind by schema/version/SHA-256.",
    )
    p.add_argument("--modality", default=None, help="Optional explicit modality label.")
    p.add_argument("--device-type", default=None, help="Optional explicit device description.")
    p.add_argument(
        "--hash-text-metadata",
        action="store_true",
        help="Hash text metadata that the scanner already reads; binary files remain unopened.",
    )
    p.add_argument("--max-files", type=int, default=256, help="File cap. Default: 256.")
    p.add_argument("--max-depth", type=int, default=8, help="Directory-depth cap. Default: 8.")
    p.add_argument(
        "--max-input-mb",
        type=float,
        default=4096.0,
        help="Declared source-byte cap in MiB. Default: 4096.",
    )
    p.add_argument(
        "--max-text-file-mb",
        type=float,
        default=1.0,
        help="Per-text-metadata read cap in MiB. Default: 1.",
    )
    p.add_argument(
        "--max-text-total-mb",
        type=float,
        default=8.0,
        help="Total text-metadata read cap in MiB. Default: 8.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=4.0,
        help="Combined JSON/Markdown/audit cap in MiB. Default: 4.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the three registered artifacts in a nonempty output directory.",
    )
    p.set_defaults(func=_cmd_inspect_recording)

    p = sub.add_parser(
        "inspect-intake-report",
        help="Strictly validate a saved local-intake report and measured audit sidecar.",
    )
    p.add_argument("--report", required=True, help="Path to deterministic intake.json.")
    p.add_argument(
        "--audit",
        default=None,
        help="Optional intake.audit.json; defaults to the report directory when present.",
    )
    p.add_argument(
        "--max-report-mb",
        type=float,
        default=4.0,
        help="Per-report inspection cap in MiB. Default: 4.",
    )
    p.set_defaults(func=_cmd_inspect_intake_report)

    p = sub.add_parser(
        "make-signal-quality-fixtures",
        help=(
            "Create the bounded target-free RW2 synthetic fixture set for six "
            "optional MNE format adapters. Requires [neuro]."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="New empty directory for generated sources, RW1 bindings, and manifest.",
    )
    p.add_argument(
        "--contract",
        required=True,
        help="Frozen registries/signal_quality_contract.v0.json path.",
    )
    p.set_defaults(func=_cmd_make_signal_quality_fixtures)

    p = sub.add_parser(
        "inspect-signal-quality-fixtures",
        help="Strictly validate an RW2 synthetic fixture manifest without reading signals.",
    )
    p.add_argument("--manifest", required=True, help="signal_quality_fixtures.json path.")
    p.add_argument(
        "--max-manifest-mb",
        type=float,
        default=4.0,
        help="Manifest inspection cap in MiB. Default: 4.",
    )
    p.set_defaults(func=_cmd_inspect_signal_quality_fixtures)

    p = sub.add_parser(
        "inspect-signal-quality",
        help=(
            "Read bounded windows from one manifest-authorized synthetic recording "
            "and write a redacted descriptive RW2 report. Requires [neuro]."
        ),
    )
    p.add_argument(
        "--path",
        required=True,
        help="Generated .vhdr/.edf/.bdf/.set/.fif file or generated BIDS root.",
    )
    p.add_argument(
        "--root",
        default=None,
        help="Optional security root; all RW1-bound source files must remain inside it.",
    )
    p.add_argument(
        "--intake-report",
        required=True,
        help="Exact generated fixture's validated RW1 intake.json.",
    )
    p.add_argument(
        "--fixture-manifest",
        required=True,
        help="Generator-produced signal_quality_fixtures.json authorization manifest.",
    )
    p.add_argument(
        "--contract",
        required=True,
        help="Frozen registries/signal_quality_contract.v0.json path.",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="Directory for signal_quality.json/.md/.audit.json.",
    )
    p.add_argument(
        "--max-channels",
        type=int,
        default=512,
        help="Selected-channel cap, no larger than frozen 512. Default: 512.",
    )
    p.add_argument(
        "--max-sample-values",
        type=int,
        default=4_194_304,
        help="Channel-sample value cap, no larger than frozen 4,194,304.",
    )
    p.add_argument(
        "--max-array-mb",
        type=float,
        default=32.0,
        help="Materialized float64-array cap in MiB, no larger than 32.",
    )
    p.add_argument(
        "--max-runtime-sec",
        type=float,
        default=30.0,
        help="Runtime cap in seconds, no larger than 30.",
    )
    p.add_argument(
        "--max-rss-mb",
        type=float,
        default=1024.0,
        help="Process peak-RSS cap in MiB, no larger than 1024.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=4.0,
        help="Combined report artifact cap in MiB, no larger than 4.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the three registered artifacts in a nonempty output directory.",
    )
    p.set_defaults(func=_cmd_inspect_signal_quality)

    p = sub.add_parser(
        "inspect-signal-quality-report",
        help="Strictly validate a saved RW2 report and measured audit sidecar.",
    )
    p.add_argument("--report", required=True, help="Path to signal_quality.json.")
    p.add_argument(
        "--audit",
        default=None,
        help="Optional audit path; defaults to signal_quality.audit.json beside the report.",
    )
    p.add_argument(
        "--max-report-mb",
        type=float,
        default=4.0,
        help="Per-report inspection cap in MiB. Default: 4.",
    )
    p.set_defaults(func=_cmd_inspect_signal_quality_report)

    p = sub.add_parser("list-hf-files", help="List files in a Hugging Face repo. Requires [hf].")
    p.add_argument("--repo-id", required=True)
    p.add_argument("--repo-type", default="dataset")
    p.add_argument("--out", required=True)
    p.add_argument(
        "--revision",
        default=None,
        help="Optional branch, tag, or commit for metadata listing.",
    )
    p.add_argument(
        "--with-sizes",
        action="store_true",
        help="Write JSONL with path and size_bytes and print the resolved immutable revision.",
    )
    p.set_defaults(func=_cmd_list_hf_files)

    p = sub.add_parser(
        "make-synthetic-shard", help="Create a tiny synthetic NPZ shard for smoke tests."
    )
    p.add_argument("--out", required=True)
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--channels", type=int, default=8)
    p.add_argument("--times", type=int, default=25)
    p.add_argument("--classes", type=int, default=8)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=_cmd_make_synthetic_shard)

    p = sub.add_parser(
        "make-synthetic-sentence-cache",
        help="Create variable-length continuous synthetic signals for CTC plumbing.",
    )
    p.add_argument("--out", required=True)
    p.add_argument("--sentences", type=int, default=96)
    p.add_argument("--channels", type=int, default=6)
    p.add_argument("--letter-classes", type=int, default=4)
    p.add_argument("--min-word-length", type=int, default=2)
    p.add_argument("--max-word-length", type=int, default=4)
    p.add_argument("--token-width", type=int, default=5)
    p.add_argument("--gap-width", type=int, default=3)
    p.add_argument("--sfreq", type=float, default=50.0)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=_cmd_make_synthetic_sentence_cache)

    p = sub.add_parser("load-cache", help="Load and summarize a B2Q-mini NPZ cache.")
    p.add_argument("--cache", required=True, help="Path to a .npz cache.")
    p.add_argument(
        "--metadata-out",
        default=None,
        help="Optional JSON sidecar path containing cache summary and metadata.",
    )
    p.set_defaults(func=_cmd_load_cache)

    p = sub.add_parser(
        "inspect-sentence-cache",
        help="Validate and summarize a B2Q continuous sentence-cache NPZ.",
    )
    p.add_argument("--cache", required=True)
    p.add_argument("--metadata-out", default=None, help="Optional JSON metadata sidecar path.")
    p.set_defaults(func=_cmd_inspect_sentence_cache)

    p = sub.add_parser(
        "inspect-representation-cache",
        help="Decode, validate, and summarize a packed sentence-signal representation.",
    )
    p.add_argument("--cache", required=True)
    p.add_argument("--metadata-out", default=None, help="Optional JSON metadata sidecar path.")
    p.set_defaults(func=_cmd_inspect_representation_cache)

    p = sub.add_parser(
        "make-neurotoken-cache",
        help=(
            "Create a bounded target-free continuous embedding cache for interface "
            "validation. Requires NumPy."
        ),
    )
    p.add_argument("--source-cache", required=True, help="Validated sentence-cache NPZ path.")
    p.add_argument(
        "--split-report",
        required=True,
        help="Strict-ready Split Protocol v1 JSON bound to the source cache.",
    )
    p.add_argument("--out", required=True, help="Output NeuroTokenCache v0 NPZ path.")
    p.add_argument("--metadata-out", default=None, help="Optional full metadata sidecar path.")
    p.add_argument("--summary-json", default=None, help="Optional compact run-summary JSON path.")
    p.add_argument("--modality", required=True, help="Source modality, for example MEG or EEG.")
    p.add_argument("--device-type", required=True, help="Source sensor/device description.")
    p.add_argument("--subject-id", required=True, help="Subject identifier stored per item.")
    p.add_argument("--session-id", required=True, help="Session identifier stored per item.")
    p.add_argument(
        "--source-sfreq",
        type=float,
        default=None,
        help="Source sampling rate override when cache metadata does not provide it.",
    )
    p.add_argument("--embedding-dim", type=int, default=32, help="Embedding width. Default: 32.")
    p.add_argument("--kernel-size", type=int, default=16, help="Frame width. Default: 16 samples.")
    p.add_argument("--stride", type=int, default=4, help="Frame stride. Default: 4 samples.")
    p.add_argument("--seed", type=int, default=23, help="Projection seed. Default: 23.")
    p.add_argument(
        "--token-dtype",
        choices=["float32", "float16"],
        default="float32",
        help="Stored embedding dtype. Default: float32.",
    )
    p.add_argument("--max-items", type=int, default=128, help="Hard source-item cap. Default: 128.")
    p.add_argument(
        "--max-tokens-per-item",
        type=int,
        default=4096,
        help="Hard per-item token cap. Default: 4096.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=32.0,
        help="Hard projected and written output cap in MiB. Default: 32.",
    )
    p.add_argument("--overwrite", action="store_true", help="Replace planned outputs.")
    p.set_defaults(func=_cmd_make_neurotoken_cache)

    p = sub.add_parser(
        "inspect-neurotoken-cache",
        help="Validate and summarize a continuous NeuroTokenCache v0 NPZ.",
    )
    p.add_argument("--cache", required=True)
    p.add_argument("--metadata-out", default=None, help="Optional JSON metadata sidecar path.")
    p.set_defaults(func=_cmd_inspect_neurotoken_cache)

    p = sub.add_parser(
        "causal-replay-gate",
        help=(
            "Audit bounded synthetic NeuroToken replay across registered chunk "
            "schedules without a decoder."
        ),
    )
    p.add_argument("--source-cache", required=True, help="Synthetic sentence-cache NPZ path.")
    p.add_argument("--out-json", required=True, help="Machine-readable gate report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown gate report path.")
    p.add_argument(
        "--source-sfreq",
        type=float,
        default=None,
        help="Sampling-rate override when source metadata does not provide it.",
    )
    p.add_argument("--embedding-dim", type=int, default=32, help="Embedding width. Default: 32.")
    p.add_argument("--kernel-size", type=int, default=16, help="Frame width. Default: 16 samples.")
    p.add_argument("--stride", type=int, default=4, help="Frame stride. Default: 4 samples.")
    p.add_argument("--seed", type=int, default=23, help="Projection seed. Default: 23.")
    p.add_argument(
        "--token-dtype",
        choices=["float32", "float16"],
        default="float32",
        help="Streaming token dtype. Default: float32.",
    )
    p.add_argument(
        "--compatibility-atol",
        type=float,
        default=2e-6,
        help=(
            "Absolute tolerance against Loop 20 batched arithmetic. "
            "Default: 2e-6 after the documented Linux float32 portability audit."
        ),
    )
    p.add_argument("--max-items", type=int, default=64, help="Source-item cap. Default: 64.")
    p.add_argument(
        "--max-source-mb",
        type=float,
        default=4.0,
        help="Source-cache cap in MiB. Default: 4.",
    )
    p.add_argument(
        "--max-samples-per-item",
        type=int,
        default=128,
        help="Per-item source-sample cap. Default: 128.",
    )
    p.add_argument(
        "--max-chunk-samples",
        type=int,
        default=128,
        help="Transport-chunk cap. Default: 128 samples.",
    )
    p.add_argument(
        "--max-tokens-per-item",
        type=int,
        default=128,
        help="Per-item output-token cap. Default: 128.",
    )
    p.add_argument(
        "--max-total-pushes",
        type=int,
        default=100_000,
        help="Complete audit push-call cap. Default: 100000.",
    )
    p.add_argument(
        "--max-working-mb",
        type=float,
        default=16.0,
        help="Signal/fixed/output working-array cap in MiB. Default: 16.",
    )
    p.add_argument(
        "--max-state-kib",
        type=float,
        default=8.0,
        help="Per-stream mutable-state cap in KiB. Default: 8.",
    )
    p.add_argument(
        "--max-runtime-sec",
        type=float,
        default=10.0,
        help="Complete audit runtime gate. Default: 10 seconds.",
    )
    p.add_argument(
        "--max-peak-rss-mb",
        type=float,
        default=256.0,
        help="Process peak-RSS gate in MiB. Default: 256.",
    )
    p.add_argument(
        "--max-report-mb",
        type=float,
        default=1.0,
        help="Per-report output cap in MiB. Default: 1.",
    )
    p.add_argument("--overwrite", action="store_true", help="Replace planned reports.")
    p.set_defaults(func=_cmd_causal_replay_gate)

    p = sub.add_parser(
        "make-causal-motif-fixture",
        help=(
            "Create the fixed three-partition Loop 22 synthetic motif fixture. "
            "Requires NumPy; creates no text or neural data."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="New output directory for manifest plus train/validation/test NPZ files.",
    )
    p.add_argument(
        "--max-total-mb",
        type=float,
        default=1.0,
        help="Hard complete-fixture cap in MiB. Default: 1.",
    )
    p.set_defaults(func=_cmd_make_causal_motif_fixture)

    p = sub.add_parser(
        "inspect-causal-motif-fixture",
        help=(
            "Validate the registered Loop 22 manifest without opening partition arrays."
        ),
    )
    p.add_argument("--manifest", required=True, help="Registered fixture manifest JSON.")
    p.set_defaults(func=_cmd_inspect_causal_motif_fixture)

    p = sub.add_parser(
        "tiny-causal-encoder-gate",
        help=(
            "Run the preregistered one-thread synthetic learned-encoder gate. "
            "Requires [ml] and opens test only after validation passes."
        ),
        description=(
            "Run the fixed Loop 22 synthetic gate. Set OMP_NUM_THREADS, "
            "OPENBLAS_NUM_THREADS, MKL_NUM_THREADS, VECLIB_MAXIMUM_THREADS, "
            "and NUMEXPR_NUM_THREADS to 1 before launch. The test partition is "
            "opened only after validation selection and checkpoint freeze."
        ),
    )
    p.add_argument(
        "--fixture-manifest",
        required=True,
        help="Registered causal-motif manifest JSON.",
    )
    p.add_argument(
        "--checkpoint-out",
        required=True,
        help="New safe numeric NPZ checkpoint path.",
    )
    p.add_argument("--out-json", required=True, help="New machine-readable gate report.")
    p.add_argument("--out-md", required=True, help="New human-readable gate report.")
    p.set_defaults(func=_cmd_tiny_causal_encoder_gate)

    p = sub.add_parser(
        "make-ctc-symbol-stream-fixture",
        help=(
            "Create the fixed three-partition Loop 23 synthetic symbol fixture. "
            "Requires NumPy; creates no natural text or neural data."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="New output directory for manifest plus train/validation/test NPZ files.",
    )
    p.add_argument(
        "--max-total-mb",
        type=float,
        default=1.0,
        help="Hard complete-fixture cap in MiB. Default: 1.",
    )
    p.set_defaults(func=_cmd_make_ctc_symbol_stream_fixture)

    p = sub.add_parser(
        "inspect-ctc-symbol-stream-fixture",
        help=(
            "Validate the registered Loop 23 manifest without opening partition arrays."
        ),
    )
    p.add_argument("--manifest", required=True, help="Registered fixture manifest JSON.")
    p.set_defaults(func=_cmd_inspect_ctc_symbol_stream_fixture)

    p = sub.add_parser(
        "streaming-ctc-gate",
        help=(
            "Run the preregistered language-model-free streaming CTC decoder gate. "
            "Requires [ml] and opens test only after validation passes."
        ),
        description=(
            "Run the fixed Loop 23 synthetic gate with the frozen Loop 22 checkpoint. "
            "Set OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS, "
            "VECLIB_MAXIMUM_THREADS, and NUMEXPR_NUM_THREADS to 1 before launch. "
            "No target-aware trimming, language model, or decoder fitting is performed."
        ),
    )
    p.add_argument(
        "--fixture-manifest",
        required=True,
        help="Registered Loop 23 symbol-stream manifest JSON.",
    )
    p.add_argument(
        "--checkpoint",
        required=True,
        help="Exact frozen Loop 22 tiny causal encoder checkpoint.",
    )
    p.add_argument("--out-json", required=True, help="New machine-readable gate report.")
    p.add_argument("--out-md", required=True, help="New human-readable gate report.")
    p.set_defaults(func=_cmd_streaming_ctc_gate)

    p = sub.add_parser(
        "make-blank-calibration-fixture",
        help=(
            "Create the fixed Loop 23.5 synthetic blank-calibration fixture. "
            "Requires NumPy; creates no natural text or neural data."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="New output directory for manifest plus train/validation/test NPZ files.",
    )
    p.add_argument(
        "--max-total-mb",
        type=float,
        default=1.0,
        help="Hard complete-fixture cap in MiB. Default: 1.",
    )
    p.set_defaults(func=_cmd_make_blank_calibration_fixture)

    p = sub.add_parser(
        "inspect-blank-calibration-fixture",
        help=(
            "Validate the registered Loop 23.5 manifest without opening partition arrays."
        ),
    )
    p.add_argument("--manifest", required=True, help="Registered fixture manifest JSON.")
    p.set_defaults(func=_cmd_inspect_blank_calibration_fixture)

    p = sub.add_parser(
        "blank-intercept-gate",
        help=(
            "Run the preregistered one-scalar synthetic blank-calibration gate. "
            "Requires [ml] and opens test only after validation passes."
        ),
        description=(
            "Fit one additive blank-logit intercept from fresh train frames, "
            "then compare calibrated and unmodified CTC decoders. Set "
            "OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS, "
            "VECLIB_MAXIMUM_THREADS, and NUMEXPR_NUM_THREADS to 1. No target "
            "length, endpoint, language model, or model update is used."
        ),
    )
    p.add_argument(
        "--fixture-manifest",
        required=True,
        help="Registered Loop 23.5 fixture manifest JSON.",
    )
    p.add_argument(
        "--checkpoint",
        required=True,
        help="Exact frozen Loop 22 tiny causal encoder checkpoint.",
    )
    p.add_argument("--out-json", required=True, help="New machine-readable gate report.")
    p.add_argument("--out-md", required=True, help="New human-readable gate report.")
    p.set_defaults(func=_cmd_blank_intercept_gate)

    p = sub.add_parser(
        "make-precision-runtime-fixture",
        help=(
            "Create the registered target-free Loop 24 selection and qualification "
            "fixture under an authorized ignored root. Requires NumPy."
        ),
        description=(
            "Generate exact seeds 2401 and 2402 as separate input-only NPZ files. "
            "The fixture contains no targets, labels, text, participant data, model "
            "outputs, or neural recordings and is capped at 512 KiB."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help=(
            "New nested directory under cache/loop24, outputs/loop24, or "
            ".codex_work/loop24."
        ),
    )
    p.set_defaults(func=_cmd_make_precision_runtime_fixture)

    p = sub.add_parser(
        "inspect-precision-runtime-fixture",
        help=(
            "Validate the registered Loop 24 manifest and hashes without opening "
            "either partition array."
        ),
    )
    p.add_argument(
        "--manifest",
        required=True,
        help="Registered Loop 24 target-free fixture manifest JSON.",
    )
    p.set_defaults(func=_cmd_inspect_precision_runtime_fixture)

    p = sub.add_parser(
        "local-precision-runtime-gate",
        help=(
            "Run the authorized frozen target-free Loop 24 CPU precision/runtime gate. "
            "Requires [ml]."
        ),
        description=(
            "Compare the exact float32, CPU float16, and dynamic QNNPACK qint8 "
            "candidates with one CPU thread, twelve balanced selection rounds, and "
            "conditional one-time seed-2402 qualification. No real data, targets, "
            "training, parameter update, energy measurement, network call, or RW3 "
            "operation is permitted."
        ),
    )
    p.add_argument(
        "--fixture-manifest",
        required=True,
        help="Exact registered Loop 24 manifest produced by the fixture command.",
    )
    p.add_argument(
        "--checkpoint",
        default="cache/loop22_tiny_causal_encoder/checkpoint.npz",
        help=(
            "Exact frozen Loop 22 checkpoint. Default: "
            "cache/loop22_tiny_causal_encoder/checkpoint.npz."
        ),
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help=(
            "New nested directory under cache/loop24, outputs/loop24, or "
            ".codex_work/loop24."
        ),
    )
    p.set_defaults(func=_cmd_local_precision_runtime_gate)

    p = sub.add_parser(
        "inspect-local-precision-runtime-report",
        help=(
            "Strictly validate a Loop 24 report, access ledger, artifacts, hashes, "
            "caps, and measured audit sidecar."
        ),
    )
    p.add_argument("--report", required=True, help="Path to a saved Loop 24 gate.json.")
    p.set_defaults(func=_cmd_inspect_local_precision_runtime_report)

    p = sub.add_parser(
        "make-causal-preprocessing-fixture",
        help=(
            "Create the registered target-free Loop 25 development and physically "
            "separate qualification fixture after a passing static filter gate."
        ),
        description=(
            "Generate exact synthetic seeds 2501 and 2502 without real data, targets, "
            "labels, text, predictions, models, or training. The combined fixture is "
            "capped at 4 MiB and may be written only under an authorized Loop 25 root."
        ),
    )
    p.add_argument(
        "--static-filter-bundle",
        required=True,
        help="Exact filter_bundle.json produced by a passing Loop 25 static gate.",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help=(
            "New nested directory under cache/loop25, outputs/loop25, or "
            ".codex_work/loop25."
        ),
    )
    p.set_defaults(func=_cmd_make_causal_preprocessing_fixture)

    p = sub.add_parser(
        "inspect-causal-preprocessing-fixture",
        help=(
            "Validate Loop 25 fixture identities, hashes, ZIP members, splits, and caps "
            "without opening signal arrays."
        ),
    )
    p.add_argument("--manifest", required=True, help="Registered Loop 25 manifest JSON.")
    p.set_defaults(func=_cmd_inspect_causal_preprocessing_fixture)

    p = sub.add_parser(
        "causal-preprocessing-gate",
        help="Run the authorized target-free Loop 25 static or complete mechanics gate.",
        description=(
            "Use --static-only exactly once to design and audit the registered filter. "
            "After that pass, omit --static-only and supply the bound fixture manifest "
            "and saved filter bundle. The complete gate opens seed 2502 only after seed "
            "2501 passes and its report is frozen. One CPU thread and the 8 MiB total "
            "artifact cap are enforced."
        ),
    )
    p.add_argument(
        "--static-only",
        action="store_true",
        help="Run only the pre-fixture coefficient, pole, response, alias, and transient gate.",
    )
    p.add_argument(
        "--fixture-manifest",
        help="Registered target-free fixture manifest; required for the complete gate.",
    )
    p.add_argument(
        "--filter-bundle",
        help="Passing static filter_bundle.json; required for the complete gate.",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help=(
            "New nested directory under cache/loop25, outputs/loop25, or "
            ".codex_work/loop25."
        ),
    )
    p.set_defaults(func=_cmd_causal_preprocessing_gate)

    p = sub.add_parser(
        "inspect-causal-preprocessing-report",
        help="Strictly validate a Loop 25 report, audit hashes, counters, and resource caps.",
    )
    p.add_argument(
        "--report",
        required=True,
        help="Path to static_gate.json or gate.json.",
    )
    p.set_defaults(func=_cmd_inspect_causal_preprocessing_report)

    p = sub.add_parser(
        "extract-windows",
        help="Extract event-aligned windows from one FIF block and one MAT log. Requires [neuro].",
    )
    p.add_argument("--raw", required=True, help="Path to one downloaded .fif MEG block.")
    p.add_argument("--events", required=True, help="Path to one matching .mat behavioral/log file.")
    p.add_argument("--out", required=True, help="Output .npz cache path.")
    p.add_argument(
        "--tmin", type=float, required=True, help="Window start in seconds relative to event."
    )
    p.add_argument(
        "--tmax", type=float, required=True, help="Window end in seconds relative to event."
    )
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
    p.add_argument(
        "--event-source",
        default="mat",
        choices=["mat", "stim-letter", "stim-key"],
        help=(
            "Use MAT-parsed events, uppercase letter triggers, or typed key triggers "
            "from a raw stim channel. Default: mat."
        ),
    )
    p.add_argument(
        "--stim-channel",
        default="STI101",
        help="Stim channel for raw stim event sources. Default: STI101.",
    )
    p.set_defaults(func=_cmd_extract_windows)

    p = sub.add_parser(
        "extract-eeg-windows",
        help=(
            "Stream key-aligned windows from one BrainVision EEG triplet and matching MAT "
            "log. Requires [neuro]."
        ),
    )
    p.add_argument("--raw", required=True, help="BrainVision .vhdr path.")
    p.add_argument("--events", required=True, help="Matching SpanishBCBL MAT log.")
    p.add_argument("--out", required=True, help="Output B2Q-mini NPZ cache path.")
    p.add_argument("--out-json", default=None, help="Optional extraction summary JSON.")
    p.add_argument("--sfreq", type=float, default=50.0, help="Output Hz. Default: 50.")
    p.add_argument("--tmin", type=float, default=-0.2, help="Window start sec. Default: -0.2.")
    p.add_argument("--tmax", type=float, default=0.3, help="Window end sec. Default: 0.3.")
    p.add_argument("--max-events", type=int, default=None, help="Optional event cap.")
    p.add_argument("--max-channels", type=int, default=None, help="Optional channel cap.")
    p.add_argument(
        "--max-alignment-residual-ms",
        type=float,
        default=50.0,
        help="Fail when aligned clock residual exceeds this value. Default: 50 ms.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=64.0,
        help="Uncompressed float32 window cap in MiB. Default: 64.",
    )
    p.add_argument("--overwrite", action="store_true", help="Replace the output cache.")
    p.set_defaults(func=_cmd_extract_eeg_windows)

    p = sub.add_parser(
        "extract-sentence-cache",
        help="Extract continuous first-key-through-ENTER sentence signals. Requires [neuro].",
    )
    p.add_argument("--raw", required=True, help="One validated downloaded FIF block.")
    p.add_argument("--events", required=True, help="Matching MAT behavioral log.")
    p.add_argument("--out", required=True, help="Output sentence-cache NPZ path.")
    p.add_argument("--sfreq", type=float, default=100.0, help="Target rate. Default: 100 Hz.")
    p.add_argument("--pre-context", type=float, default=0.4, help="Seconds before first key.")
    p.add_argument("--post-context", type=float, default=0.45, help="Seconds after ENTER.")
    p.add_argument("--picks", default="meg", help="MNE channel pick. Default: meg.")
    p.add_argument("--max-channels", type=int, default=16, help="Channel cap. Default: 16.")
    p.add_argument("--stim-channel", default="STI101", help="Key trigger channel.")
    p.add_argument("--l-freq", type=float, default=0.5, help="High-pass Hz. Default: 0.5.")
    p.add_argument("--h-freq", type=float, default=45.0, help="Low-pass Hz. Default: 45.")
    p.add_argument("--notch-freq", type=float, default=50.0, help="Notch Hz. Default: 50.")
    p.add_argument("--clamp", type=float, default=5.0, help="Robust units clamp. Default: 5.")
    p.add_argument("--no-robust-scale", action="store_true", help="Disable median/IQR scaling.")
    p.add_argument(
        "--scaler-fit-scope",
        choices=["recording", "train"],
        default="recording",
        help=(
            "Fit robust statistics on the complete recording or deterministic "
            "train sentence rows. Default: recording for backward compatibility."
        ),
    )
    p.add_argument(
        "--split-text-normalization",
        choices=["official-exact", "canonical-v1"],
        default="official-exact",
        help="Text grouping used by train-fit scaling. Default: official-exact.",
    )
    p.add_argument("--max-sentences", type=int, default=None, help="Optional leading-trial cap.")
    p.add_argument(
        "--summary-json",
        default=None,
        help="Optional machine-readable extraction summary path.",
    )
    p.set_defaults(func=_cmd_extract_sentence_cache)

    p = sub.add_parser(
        "apply-frozen-scaler",
        help="Apply train-only scaler statistics to an independent unscaled sentence cache.",
    )
    p.add_argument(
        "--source-cache",
        required=True,
        help="Independent sentence cache with robust scaling explicitly disabled.",
    )
    p.add_argument(
        "--fit-cache",
        required=True,
        help="Sentence cache containing verified train-only robust scaler statistics.",
    )
    p.add_argument("--out", required=True, help="Output scaled sentence-cache NPZ path.")
    p.add_argument(
        "--summary-json",
        default=None,
        help="Optional machine-readable frozen-scaler summary path.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output cache.",
    )
    p.set_defaults(func=_cmd_apply_frozen_scaler)

    p = sub.add_parser(
        "sampling-rate-sweep",
        help=(
            "Compare isolated sentence-cache extractions across sampling rates. Requires [neuro]."
        ),
    )
    p.add_argument("--raw", required=True, help="One validated downloaded FIF block.")
    p.add_argument("--events", required=True, help="Matching MAT behavioral log.")
    p.add_argument("--out-dir", required=True, help="Directory for caches and reports.")
    p.add_argument(
        "--rates",
        type=float,
        nargs="+",
        default=[100.0, 50.0, 25.0],
        help="Unique target rates. Default: 100 50 25.",
    )
    p.add_argument("--pre-context", type=float, default=0.4, help="Seconds before first key.")
    p.add_argument("--post-context", type=float, default=0.45, help="Seconds after ENTER.")
    p.add_argument("--picks", default="meg", help="MNE channel pick. Default: meg.")
    p.add_argument("--max-channels", type=int, default=16, help="Channel cap. Default: 16.")
    p.add_argument("--stim-channel", default="STI101", help="Key trigger channel.")
    p.add_argument("--l-freq", type=float, default=0.5, help="High-pass Hz. Default: 0.5.")
    p.add_argument("--h-freq", type=float, default=45.0, help="Low-pass Hz. Default: 45.")
    p.add_argument("--notch-freq", type=float, default=50.0, help="Notch Hz. Default: 50.")
    p.add_argument("--clamp", type=float, default=5.0, help="Robust units clamp. Default: 5.")
    p.add_argument("--no-robust-scale", action="store_true", help="Disable median/IQR scaling.")
    p.add_argument("--max-sentences", type=int, default=None, help="Optional leading-trial cap.")
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing planned sweep artifacts.",
    )
    p.set_defaults(func=_cmd_sampling_rate_sweep)

    p = sub.add_parser(
        "channel-subset-sweep",
        help=(
            "Compare deterministic channel subsets from one geometry-aware sentence cache. "
            "Requires [neuro]."
        ),
    )
    p.add_argument("--cache", required=True, help="Geometry-aware base sentence-cache NPZ.")
    p.add_argument("--out-dir", required=True, help="Directory for subset caches and reports.")
    p.add_argument(
        "--counts",
        type=int,
        nargs="+",
        default=[76, 51, 25, 16, 8],
        help="Unique subset sizes below the base count. Default: 76 51 25 16 8.",
    )
    p.add_argument(
        "--strategies",
        nargs="+",
        choices=["spatial-fps", "variance", "random", "first"],
        default=["spatial-fps", "variance", "random", "first"],
        help="Nested selection strategies. Default: all four.",
    )
    p.add_argument("--seed", type=int, default=17, help="Random-control seed. Default: 17.")
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=128.0,
        help="Refuse projected subset artifacts above this cap. Default: 128 MiB.",
    )
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing planned subset artifacts.",
    )
    p.set_defaults(func=_cmd_channel_subset_sweep)

    p = sub.add_parser(
        "precision-storage-sweep",
        help=(
            "Compare bounded packed signal representations without training a decoder. "
            "Requires NumPy."
        ),
    )
    p.add_argument(
        "--cache",
        nargs="+",
        required=True,
        help="One or more validated sentence-cache NPZ inputs.",
    )
    p.add_argument("--out-dir", required=True, help="Directory for representations and reports.")
    p.add_argument(
        "--variants",
        nargs="+",
        choices=["float32", "float16", "bfloat16", "qint16", "qint8"],
        default=["float32", "float16", "bfloat16", "qint16", "qint8"],
        help="Unique representations. Default: all five.",
    )
    p.add_argument(
        "--clip-abs",
        type=float,
        default=5.0,
        help="Fixed symmetric integer range inherited from preprocessing. Default: 5.",
    )
    p.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Warm load/decode timing repetitions. Default: 3.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=96.0,
        help="Refuse projected artifacts above this cap. Default: 96 MiB.",
    )
    p.add_argument(
        "--allow-clipping",
        action="store_true",
        help="Allow and count source values outside the fixed integer range.",
    )
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing planned representation artifacts.",
    )
    p.set_defaults(func=_cmd_precision_storage_sweep)

    p = sub.add_parser(
        "lazy-backend-gate",
        help=(
            "Measure isolated NPZ full/partial access and decide whether a Zarr "
            "comparison is justified."
        ),
    )
    p.add_argument(
        "--cache",
        nargs="+",
        required=True,
        help="Standard or packed sentence-cache NPZ paths.",
    )
    p.add_argument("--out-dir", required=True, help="Directory for JSON/Markdown reports.")
    p.add_argument(
        "--row-counts",
        type=int,
        nargs="+",
        default=[1, 8],
        help="Unique leading-row access sizes including 1. Default: 1 8.",
    )
    p.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Per-worker access repetitions. Default: 5.",
    )
    p.add_argument(
        "--max-full-load-ms",
        type=float,
        default=250.0,
        help="Median full-load revisit budget. Default: 250 ms.",
    )
    p.add_argument(
        "--max-partial-load-ms",
        type=float,
        default=100.0,
        help="Median partial-read revisit budget. Default: 100 ms.",
    )
    p.add_argument(
        "--max-peak-rss-mb",
        type=float,
        default=512.0,
        help="Per-worker peak-RSS revisit budget. Default: 512 MiB.",
    )
    p.add_argument(
        "--revisit-cache-mb",
        type=float,
        default=128.0,
        help="Per-cache compressed-size revisit threshold. Default: 128 MiB.",
    )
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing planned gate reports.",
    )
    p.set_defaults(func=_cmd_lazy_backend_gate)

    p = sub.add_parser(
        "split-protocol",
        help=(
            "Audit deterministic train/validation/test membership and preprocessing "
            "fit scope without loading signal arrays."
        ),
    )
    p.add_argument(
        "--cache",
        nargs="+",
        required=True,
        help="Standard or packed sentence-cache NPZ paths.",
    )
    p.add_argument("--out-dir", required=True, help="Directory for JSON/Markdown reports.")
    p.add_argument(
        "--split-type",
        choices=["event", "sentence-text", "session", "subject"],
        default="sentence-text",
        help="Grouping unit assigned to partitions. Default: sentence-text.",
    )
    p.add_argument(
        "--text-source",
        choices=["reference", "target", "mat-response"],
        default="reference",
        help="Text field used for sentence-text groups. Default: reference.",
    )
    p.add_argument(
        "--text-normalization",
        choices=["canonical-v1", "official-exact"],
        default="canonical-v1",
        help=(
            "Text grouping semantics: safer canonical grouping or exact official-v2 "
            "strings. Default: canonical-v1."
        ),
    )
    p.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Train partition ratio. Default: 0.8.",
    )
    p.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="Validation partition ratio. Default: 0.1.",
    )
    p.add_argument(
        "--test-ratio",
        type=float,
        default=0.1,
        help="Test partition ratio. Default: 0.1.",
    )
    p.add_argument(
        "--seed",
        type=float,
        default=0.0,
        help="Float seed matching NeuralSet 0.2.2 behavior. Default: 0.0.",
    )
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing planned split reports.",
    )
    p.set_defaults(func=_cmd_split_protocol)

    p = sub.add_parser(
        "sentence-prior-baseline",
        help=(
            "Run a signal-free no-brain sentence prior on a strict-ready split "
            "report. Requires NumPy but never loads signal arrays."
        ),
    )
    p.add_argument("--cache", required=True, help="Validated sentence-cache NPZ path.")
    p.add_argument(
        "--split-report",
        required=True,
        help="Strict-ready Split Protocol v1 JSON bound to the cache.",
    )
    p.add_argument(
        "--eval-partition",
        choices=["val", "test"],
        default="test",
        help="Partition to evaluate. Default: test.",
    )
    p.add_argument(
        "--strategy",
        choices=["most-frequent", "frequency-sample", "uniform-random"],
        default="most-frequent",
        help="No-brain prediction strategy. Default: most-frequent.",
    )
    p.add_argument("--seed", type=int, default=7, help="Prediction seed. Default: 7.")
    p.add_argument("--out-predictions", default=None, help="Optional predictions path.")
    p.add_argument("--out-json", default=None, help="Optional JSON report path.")
    p.add_argument("--out-md", default=None, help="Optional Markdown report path.")
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--max-examples",
        type=int,
        default=10,
        help="Maximum report examples. Default: 10.",
    )
    p.set_defaults(func=_cmd_sentence_prior_baseline)

    p = sub.add_parser(
        "align-sequences",
        help="Group typed key labels from a cache and align them to MAT target sequences. Requires [neuro].",
    )
    p.add_argument("--cache", required=True, help="Typed-key NPZ cache path.")
    p.add_argument("--events", required=True, help="Matching .mat behavioral/log file.")
    p.add_argument("--out-json", default=None, help="Optional sequence alignment JSON report path.")
    p.add_argument(
        "--out-md", default=None, help="Optional sequence alignment Markdown report path."
    )
    p.add_argument("--run-name", default=None, help="Human-readable run name.")
    p.add_argument(
        "--high-confidence-cer",
        type=float,
        default=0.15,
        help="CER threshold for high-confidence target matches. Default: 0.15.",
    )
    p.add_argument(
        "--moderate-confidence-cer",
        type=float,
        default=0.35,
        help="CER threshold for moderate target matches. Default: 0.35.",
    )
    p.set_defaults(func=_cmd_align_sequences)

    p = sub.add_parser(
        "build-leaderboard",
        help=(
            "Build versioned report cards and cohort-local rankings from compact saved reports. "
            "Does not load cache arrays or run models."
        ),
    )
    p.add_argument("--spec", required=True, help="Versioned leaderboard spec JSON path.")
    p.add_argument("--out-dir", required=True, help="Output directory for cards and tables.")
    p.add_argument(
        "--project-root",
        default=".",
        help="Root used to resolve bounded source-report paths. Default: current directory.",
    )
    p.add_argument(
        "--max-cards",
        type=int,
        default=32,
        help="Safety cap on report cards. Default: 32.",
    )
    p.add_argument(
        "--max-output-mb",
        type=float,
        default=2.0,
        help="Safety cap on all generated artifacts in MiB. Default: 2.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the requested output directory when it already exists.",
    )
    p.set_defaults(func=_cmd_build_leaderboard)

    p = sub.add_parser("select-tiny", help="Create a tiny safe selection from a manifest.")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--modality", default="MEG", choices=["MEG", "EEG", "meg", "eeg"])
    p.add_argument(
        "--subject",
        default=None,
        help="Optional subject ID like S1. Defaults to first detected subject.",
    )
    p.add_argument(
        "--session",
        default=None,
        help="Optional inferred session ID such as 2. Requires session metadata.",
    )
    p.add_argument(
        "--revision",
        default=None,
        help="Optional immutable Hub commit SHA recorded in the selection.",
    )
    p.add_argument(
        "--blocks", type=int, default=1, help="Number of raw blocks to select. Default: 1."
    )
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

    p = sub.add_parser(
        "download-selection", help="Dry-run or execute selective HF download from a selection JSON."
    )
    p.add_argument("--selection", required=True)
    p.add_argument("--local-dir", required=True)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--execute", action="store_true", help="Actually download. Default is dry-run only."
    )
    mode.add_argument(
        "--dry-run", action="store_true", help="Explicitly keep dry-run mode. This is the default."
    )
    p.add_argument(
        "--max-files", type=int, default=None, help="Override the selection file-count safety cap."
    )
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
    p.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum concurrent Hub download workers. Default: 1.",
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
