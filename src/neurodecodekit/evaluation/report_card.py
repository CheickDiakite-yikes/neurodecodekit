"""Versioned, deterministic report cards for saved NeuroDecodeKit runs."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import resource
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


REPORT_CARD_SCHEMA = {"name": "neurodecodekit-report-card", "version": 1}
LEADERBOARD_SCHEMA = {"name": "neurodecodekit-leaderboard", "version": 1}
SPEC_SCHEMA = {"name": "neurodecodekit-leaderboard-spec", "version": 1}
MAX_SOURCE_REPORT_BYTES = 1 * 1024 * 1024
DEFAULT_MAX_CARDS = 32
DEFAULT_MAX_OUTPUT_MB = 2.0

_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
_CONFIG_KEYS = (
    "kind",
    "model_name",
    "strategy",
    "causal",
    "uses_neural_windows",
    "uses_continuous_sentence_signals",
    "uses_deep_learning",
    "fit_on_eval_targets",
    "n_train_rows",
    "n_eval_rows",
    "n_channels",
    "n_classes",
    "seed",
    "epochs",
    "batch_size",
    "learning_rate",
    "hidden_channels",
    "num_threads",
    "parameter_count",
    "parameter_bytes_float32",
    "split_mode",
    "device",
    "train_fraction",
)
_METRIC_KEYS = (
    "n_examples",
    "corpus_cer",
    "corpus_wer",
    "exact_match_rate",
    "mean_keyboard_distance",
    "char_edits",
    "word_edits",
)
_REQUIRED_CARD_PATHS = (
    "schema.name",
    "schema.version",
    "run.run_id",
    "run.cohort_id",
    "run.source_created_at_utc",
    "evaluation.proof_posture",
    "evaluation.comparison_authorized",
    "method.family",
    "method.name",
    "method.uses_neural_signal",
    "method.uses_deep_learning",
    "metrics.n_examples",
    "metrics.corpus_cer",
    "metrics.corpus_wer",
    "config.sha256",
    "cache.signal_array_members_loaded",
    "source_artifact.report_sha256",
    "proof.holdout_reopened",
    "proof.raw_data_reads",
    "proof.model_runs_triggered",
    "proof.network_fetches",
)
_RECOMMENDED_CARD_PATHS = (
    "metrics.semantic_error_rate",
    "comparison.paired_bootstrap_delta_ci95",
    "method.parameter_count",
    "resources.method_runtime_sec",
    "resources.peak_rss_bytes",
    "cache.sha256",
    "provenance.code_version",
)


@dataclass(frozen=True)
class CohortSpec:
    cohort_id: str
    payload: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CohortSpec":
        payload = dict(value)
        cohort_id = _required_string(payload, "cohort_id")
        _validate_id(cohort_id, "cohort_id")
        if not isinstance(payload.get("comparison_authorized"), bool):
            raise ValueError(f"cohort {cohort_id!r} needs boolean comparison_authorized")
        _required_string(payload, "proof_posture")
        return cls(cohort_id=cohort_id, payload=payload)


@dataclass(frozen=True)
class CardSpec:
    run_id: str
    cohort_id: str
    source_report: str
    selector: dict[str, Any]
    payload: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CardSpec":
        payload = dict(value)
        run_id = _required_string(payload, "run_id")
        cohort_id = _required_string(payload, "cohort_id")
        source_report = _required_string(payload, "source_report")
        _validate_id(run_id, "run_id")
        _validate_id(cohort_id, "cohort_id")
        selector = payload.get("selector")
        if not isinstance(selector, dict):
            raise ValueError(f"card {run_id!r} needs an object selector")
        if selector.get("kind") not in {
            "report-primary",
            "report-comparator",
            "adapter-holdout",
        }:
            raise ValueError(f"card {run_id!r} has unsupported selector kind")
        return cls(
            run_id=run_id,
            cohort_id=cohort_id,
            source_report=source_report,
            selector=dict(selector),
            payload=payload,
        )


def build_leaderboard(
    *,
    spec_path: str | Path,
    out_dir: str | Path,
    project_root: str | Path = ".",
    max_cards: int = DEFAULT_MAX_CARDS,
    max_output_mb: float = DEFAULT_MAX_OUTPUT_MB,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Build deterministic cards and leaderboard files from compact saved reports."""
    started = time.perf_counter()
    if max_cards < 1:
        raise ValueError("max_cards must be positive")
    if max_output_mb <= 0:
        raise ValueError("max_output_mb must be positive")

    root = Path(project_root).resolve()
    spec_file = Path(spec_path).resolve()
    spec = _read_json_object(spec_file, max_bytes=MAX_SOURCE_REPORT_BYTES)
    _validate_schema(spec.get("schema"), SPEC_SCHEMA, "leaderboard spec")
    leaderboard_id = _required_string(spec, "leaderboard_id")
    _validate_id(leaderboard_id, "leaderboard_id")

    cohort_specs = [CohortSpec.from_mapping(item) for item in _required_list(spec, "cohorts")]
    cohorts = _unique_by_id(cohort_specs, "cohort_id")
    card_specs = [CardSpec.from_mapping(item) for item in _required_list(spec, "cards")]
    if len(card_specs) > max_cards:
        raise ValueError(f"spec requests {len(card_specs)} cards; cap is {max_cards}")
    _unique_by_id(card_specs, "run_id")
    if not card_specs:
        raise ValueError("leaderboard spec must contain at least one card")

    cards = []
    source_bytes_read = 0
    for card_spec in card_specs:
        cohort = cohorts.get(card_spec.cohort_id)
        if cohort is None:
            raise ValueError(
                f"card {card_spec.run_id!r} references unknown cohort {card_spec.cohort_id!r}"
            )
        source_path = _resolve_inside_root(root, card_spec.source_report)
        source_size = source_path.stat().st_size
        if source_size > MAX_SOURCE_REPORT_BYTES:
            raise ValueError(
                f"source report {card_spec.source_report!r} exceeds "
                f"{MAX_SOURCE_REPORT_BYTES} bytes"
            )
        source_bytes = source_path.read_bytes()
        source_bytes_read += len(source_bytes)
        source_report = _decode_json_object(source_bytes, source_path)
        card = _build_card(
            card_spec=card_spec,
            cohort=cohort,
            source_report=source_report,
            source_bytes=source_bytes,
        )
        validate_report_card(card)
        cards.append(card)

    validate_report_card_set(cards)
    leaderboard = _build_leaderboard_document(
        leaderboard_id=leaderboard_id,
        cards=cards,
        cohorts=cohort_specs,
        research_sources=spec.get("research_sources", []),
    )
    core_files = _render_core_files(cards, leaderboard)
    max_output_bytes = int(max_output_mb * 1024 * 1024)
    core_bytes = sum(len(content) for content in core_files.values())
    if core_bytes > max_output_bytes:
        raise ValueError(
            f"planned deterministic output is {core_bytes} bytes; cap is {max_output_bytes}"
        )

    output = _resolve_output_inside_root(root, out_dir)
    if output.exists():
        if not overwrite:
            raise FileExistsError(f"output directory already exists: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for relative_path, content in core_files.items():
        destination = output / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    core_sha256 = _artifact_set_sha256(core_files)
    audit = {
        "schema": {"name": "neurodecodekit-leaderboard-audit", "version": 1},
        "leaderboard_id": leaderboard_id,
        "proof_posture": "local_artifact_only",
        "runtime_sec": round(time.perf_counter() - started, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "source_report_count": len(card_specs),
        "source_report_bytes_read": source_bytes_read,
        "deterministic_core_files": len(core_files),
        "deterministic_core_bytes": core_bytes,
        "deterministic_core_sha256": core_sha256,
        "max_output_bytes": max_output_bytes,
        "raw_data_reads": 0,
        "signal_array_members_loaded": False,
        "cache_files_opened": 0,
        "model_runs_triggered": 0,
        "network_fetches": 0,
        "holdouts_reopened": 0,
        "audit_excluded_from_deterministic_core": True,
    }
    audit_bytes = _json_bytes(audit)
    audit["audit_bytes"] = len(audit_bytes)
    audit["total_artifact_bytes"] = core_bytes + len(audit_bytes)
    for _ in range(4):
        audit_bytes = _json_bytes(audit)
        audit["audit_bytes"] = len(audit_bytes)
        audit["total_artifact_bytes"] = core_bytes + len(audit_bytes)
    if audit["total_artifact_bytes"] > max_output_bytes:
        shutil.rmtree(output)
        raise ValueError(
            f"total output is {audit['total_artifact_bytes']} bytes; cap is {max_output_bytes}"
        )
    (output / "audit.json").write_bytes(audit_bytes)
    return {"leaderboard": leaderboard, "audit": audit, "output_dir": str(output)}


def validate_report_card(card: Mapping[str, Any]) -> None:
    """Reject malformed or unsupported report cards."""
    _validate_schema(card.get("schema"), REPORT_CARD_SCHEMA, "report card")
    missing = [path for path in _REQUIRED_CARD_PATHS if _get_path(card, path) is None]
    if missing:
        raise ValueError(f"report card missing required fields: {', '.join(missing)}")
    run_id = str(_get_path(card, "run.run_id"))
    _validate_id(run_id, "run_id")
    metrics = card.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError(f"report card {run_id!r} metrics must be an object")
    n_examples = metrics.get("n_examples")
    if not isinstance(n_examples, int) or isinstance(n_examples, bool) or n_examples <= 0:
        raise ValueError(f"report card {run_id!r} n_examples must be a positive integer")
    for key in ("corpus_cer", "corpus_wer"):
        value = metrics.get(key)
        if not _finite_nonnegative_number(value):
            raise ValueError(f"report card {run_id!r} {key} must be finite and nonnegative")
    for path in (
        "method.uses_neural_signal",
        "method.uses_deep_learning",
        "evaluation.comparison_authorized",
        "cache.signal_array_members_loaded",
        "proof.holdout_reopened",
    ):
        if not isinstance(_get_path(card, path), bool):
            raise ValueError(f"report card {run_id!r} {path} must be boolean")
    if _get_path(card, "cache.signal_array_members_loaded"):
        raise ValueError(f"report card {run_id!r} claims signal arrays were loaded")
    if _get_path(card, "proof.holdout_reopened"):
        raise ValueError(f"report card {run_id!r} reopens an observed holdout")


def validate_report_card_set(cards: Iterable[Mapping[str, Any]]) -> None:
    """Validate a card collection and reject mixed schema versions or duplicate IDs."""
    card_list = list(cards)
    declared_versions = {
        (card.get("schema", {}).get("name"), card.get("schema", {}).get("version"))
        for card in card_list
        if isinstance(card, Mapping) and isinstance(card.get("schema"), Mapping)
    }
    if len(declared_versions) > 1:
        raise ValueError(
            f"mixed report-card schema versions are not allowed: {sorted(declared_versions)}"
        )
    versions: set[tuple[Any, Any]] = set()
    run_ids: set[str] = set()
    for card in card_list:
        validate_report_card(card)
        schema = card["schema"]
        versions.add((schema.get("name"), schema.get("version")))
        run_id = str(card["run"]["run_id"])
        if run_id in run_ids:
            raise ValueError(f"duplicate report card run_id: {run_id}")
        run_ids.add(run_id)
    if len(versions) > 1:
        raise ValueError(f"mixed report-card schema versions are not allowed: {sorted(versions)}")


def format_leaderboard_table(leaderboard: Mapping[str, Any]) -> str:
    """Render the sortable cohort-local leaderboard as a dependency-free table."""
    headers = ("cohort", "rank", "method", "CER", "WER", "n", "proof")
    rows = []
    for row in leaderboard.get("rows", []):
        rows.append(
            (
                str(row["cohort_id"]),
                str(row["rank"]) if row["rank"] is not None else "-",
                str(row["method_name"]),
                f"{row['corpus_cer']:.6f}",
                f"{row['corpus_wer']:.6f}",
                str(row["n_examples"]),
                str(row["proof_posture"]),
            )
        )
    widths = [len(value) for value in headers]
    for row in rows:
        widths = [max(widths[index], len(value)) for index, value in enumerate(row)]
    lines = ["  ".join(value.ljust(widths[index]) for index, value in enumerate(headers))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend(
        "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return "\n".join(lines)


def _build_card(
    *,
    card_spec: CardSpec,
    cohort: CohortSpec,
    source_report: Mapping[str, Any],
    source_bytes: bytes,
) -> dict[str, Any]:
    summary, baseline, comparison = _select_result(source_report, card_spec)
    run = _required_mapping(source_report, "run")
    display_name = str(card_spec.payload.get("display_name") or card_spec.run_id)
    family = _required_string(card_spec.payload, "method_family")
    method_name = _required_string(card_spec.payload, "method_name")
    config = {key: baseline[key] for key in _CONFIG_KEYS if key in baseline}
    if card_spec.selector["kind"] == "adapter-holdout" and method_name == "robust_channel_affine":
        adapter = source_report.get("adapter", {})
        if isinstance(adapter, Mapping):
            for key in (
                "epsilon",
                "learned_parameter_count",
                "fitted_state_scalar_count",
                "source_fit_rows",
                "target_fit_rows",
                "target_labels_used",
            ):
                if key in adapter:
                    config[f"adapter_{key}"] = adapter[key]
    overrides = card_spec.payload.get("config_overrides", {})
    if not isinstance(overrides, Mapping):
        raise ValueError(f"card {card_spec.run_id!r} config_overrides must be an object")
    config.update(overrides)
    config = _json_safe_mapping(config, f"card {card_spec.run_id!r} config")

    cache = source_report.get("cache")
    cache_summary = _cache_provenance(cache)
    source_report_path = card_spec.source_report
    uses_neural_signal = _required_bool(card_spec.payload, "uses_neural_signal")
    uses_deep_learning = _required_bool(card_spec.payload, "uses_deep_learning")
    causal = card_spec.payload.get("causal", baseline.get("causal"))
    if causal is not None and not isinstance(causal, bool):
        raise ValueError(f"card {card_spec.run_id!r} causal must be boolean or null")
    fit_on_eval_targets = card_spec.payload.get(
        "fit_on_eval_targets", baseline.get("fit_on_eval_targets", False)
    )
    if not isinstance(fit_on_eval_targets, bool):
        raise ValueError(f"card {card_spec.run_id!r} fit_on_eval_targets must be boolean")

    resources = _resources(source_report, baseline, card_spec.selector["kind"])
    parameter_count = baseline.get("parameter_count")
    metrics = {key: summary.get(key) for key in _METRIC_KEYS}
    metrics["semantic_error_rate"] = None
    normalized_comparison = _normalize_comparison(comparison, card_spec)
    source_warnings = _collect_warnings(source_report, baseline)
    proof_posture = cohort.payload["proof_posture"]

    card: dict[str, Any] = {
        "schema": dict(REPORT_CARD_SCHEMA),
        "run": {
            "run_id": card_spec.run_id,
            "display_name": display_name,
            "cohort_id": card_spec.cohort_id,
            "source_run_name": run.get("name"),
            "source_created_at_utc": run.get("created_at_utc"),
        },
        "evaluation": {
            key: value
            for key, value in cohort.payload.items()
            if key != "cohort_id"
        },
        "method": {
            "family": family,
            "name": method_name,
            "description": card_spec.payload.get("description", baseline.get("description")),
            "uses_neural_signal": uses_neural_signal,
            "uses_deep_learning": uses_deep_learning,
            "causal": causal,
            "fit_on_eval_targets": fit_on_eval_targets,
            "parameter_count": parameter_count,
        },
        "metrics": metrics,
        "comparison": normalized_comparison,
        "resources": resources,
        "config": {"values": config, "sha256": _sha256(_json_bytes(config))},
        "cache": cache_summary,
        "source_artifact": {
            "report_path": source_report_path,
            "report_bytes": len(source_bytes),
            "report_sha256": _sha256(source_bytes),
            "selector": dict(card_spec.selector),
        },
        "proof": {
            "posture": proof_posture,
            "holdout_reopened": False,
            "raw_data_reads": 0,
            "model_runs_triggered": 0,
            "network_fetches": 0,
            "cache_files_opened": 0,
            "signal_array_members_loaded": False,
            "allowed_claims": cohort.payload.get("allowed_claims", []),
            "prohibited_claims": cohort.payload.get("prohibited_claims", []),
        },
        "provenance": {
            "builder": "neurodecodekit.evaluation.report_card",
            "code_version": None,
            "source_warnings": source_warnings,
        },
    }
    missing_recommended = [
        path for path in _RECOMMENDED_CARD_PATHS if _get_path(card, path) is None
    ]
    card["completeness"] = {
        "required_fields_present": True,
        "missing_required_fields": [],
        "missing_recommended_fields": missing_recommended,
        "recommended_fields_present": len(_RECOMMENDED_CARD_PATHS) - len(missing_recommended),
        "recommended_fields_total": len(_RECOMMENDED_CARD_PATHS),
        "warnings": _completeness_warnings(card, missing_recommended),
    }
    return card


def _select_result(
    source_report: Mapping[str, Any], card_spec: CardSpec
) -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any] | None]:
    kind = card_spec.selector["kind"]
    comparison = None
    if kind == "report-primary":
        summary = _required_mapping(source_report, "summary")
        baseline = _required_mapping(source_report, "baseline")
    elif kind == "report-comparator":
        name = _required_string(card_spec.selector, "name")
        comparator = _required_mapping(_required_mapping(source_report, "comparators"), name)
        summary = _required_mapping(comparator, "summary")
        baseline = _required_mapping(comparator, "baseline")
    else:
        name = _required_string(card_spec.selector, "name")
        summary = _required_mapping(_required_mapping(source_report, "holdout"), name)
        if name == "prior_only":
            baseline = {
                "kind": "prior-only",
                "strategy": "most-frequent-source-train",
                "uses_neural_windows": False,
                "uses_deep_learning": False,
                "fit_on_eval_targets": False,
                "n_eval_rows": summary.get("n_examples"),
            }
        else:
            baseline = _required_mapping(source_report, "model")
    comparison_spec = card_spec.payload.get("comparison")
    if comparison_spec is not None:
        if not isinstance(comparison_spec, Mapping):
            raise ValueError(f"card {card_spec.run_id!r} comparison must be an object")
        source_key = _required_string(comparison_spec, "source_key")
        container_name = "holdout" if kind == "adapter-holdout" else "comparisons"
        comparison = _required_mapping(_required_mapping(source_report, container_name), source_key)
    return summary, baseline, comparison


def _normalize_comparison(
    comparison: Mapping[str, Any] | None, card_spec: CardSpec
) -> dict[str, Any] | None:
    if comparison is None:
        return None
    spec = card_spec.payload["comparison"]
    return {
        "comparator_run_id": _required_string(spec, "comparator_run_id"),
        "corpus_cer_delta_method_minus_comparator": comparison.get(
            "corpus_cer_delta_a_minus_b"
        ),
        "char_edit_delta_method_minus_comparator": comparison.get("char_edit_delta_a_minus_b"),
        "paired_bootstrap_delta_ci95": comparison.get("paired_bootstrap_delta_ci95"),
        "bootstrap_probability_method_better": comparison.get("bootstrap_probability_a_better"),
        "n_paired_sentences": comparison.get("n_paired_sentences"),
        "interpretation_boundary": comparison.get("interpretation_boundary"),
    }


def _cache_provenance(cache: Any) -> dict[str, Any]:
    if not isinstance(cache, Mapping):
        return {
            "present_in_source_report": False,
            "path": None,
            "schema_name": None,
            "schema_version": None,
            "kind": None,
            "bytes": None,
            "signals_shape": None,
            "source_files": {},
            "sha256": None,
            "cache_file_opened": False,
            "signal_array_members_loaded": False,
        }
    source_files = cache.get("source_files", {})
    if not isinstance(source_files, Mapping):
        source_files = {}
    signals_shape = cache.get("signals_shape", cache.get("windows_shape"))
    return {
        "present_in_source_report": True,
        "path": cache.get("path"),
        "schema_name": cache.get("schema_name"),
        "schema_version": cache.get("schema_version"),
        "kind": cache.get("kind"),
        "bytes": cache.get("bytes"),
        "signals_shape": signals_shape,
        "source_files": {
            key: source_files[key] for key in ("raw", "events") if key in source_files
        },
        "sha256": None,
        "cache_file_opened": False,
        "signal_array_members_loaded": False,
    }


def _resources(
    source_report: Mapping[str, Any], baseline: Mapping[str, Any], selector_kind: str
) -> dict[str, Any]:
    run = source_report.get("run", {})
    source_resources = source_report.get("resources", {})
    report_runtime = run.get("runtime_sec") if isinstance(run, Mapping) else None
    if selector_kind == "report-primary":
        method_runtime = baseline.get("runtime_sec")
        peak_rss = baseline.get("peak_rss_bytes")
        scope = "method_if_recorded_plus_source_report_total"
    elif selector_kind == "adapter-holdout":
        method_runtime = None
        peak_rss = source_resources.get("peak_rss_bytes") if isinstance(source_resources, Mapping) else None
        scope = "shared_experiment_total_not_variant_specific"
    else:
        method_runtime = None
        peak_rss = None
        scope = "source_report_total_only_not_comparator_specific"
    return {
        "measurement_scope": scope,
        "method_runtime_sec": method_runtime,
        "source_report_total_runtime_sec": report_runtime,
        "peak_rss_bytes": peak_rss,
        "source_report_total_artifact_bytes": (
            source_resources.get("total_artifact_bytes")
            if isinstance(source_resources, Mapping)
            else None
        ),
    }


def _build_leaderboard_document(
    *,
    leaderboard_id: str,
    cards: list[dict[str, Any]],
    cohorts: list[CohortSpec],
    research_sources: Any,
) -> dict[str, Any]:
    if not isinstance(research_sources, list):
        raise ValueError("research_sources must be a list")
    rows = []
    cards_by_cohort: dict[str, list[dict[str, Any]]] = {}
    for card in cards:
        cards_by_cohort.setdefault(card["run"]["cohort_id"], []).append(card)
    cohort_documents = []
    ranked_cohorts = 0
    for cohort in cohorts:
        cohort_cards = cards_by_cohort.get(cohort.cohort_id, [])
        can_rank = bool(cohort.payload["comparison_authorized"] and len(cohort_cards) >= 2)
        if can_rank:
            ranked_cohorts += 1
        sorted_cards = sorted(
            cohort_cards,
            key=lambda card: (
                card["metrics"]["corpus_cer"],
                card["metrics"]["corpus_wer"],
                card["run"]["run_id"],
            ),
        )
        for index, card in enumerate(sorted_cards, start=1):
            rows.append(
                {
                    "cohort_id": cohort.cohort_id,
                    "rank": index if can_rank else None,
                    "run_id": card["run"]["run_id"],
                    "method_family": card["method"]["family"],
                    "method_name": card["method"]["name"],
                    "uses_neural_signal": card["method"]["uses_neural_signal"],
                    "n_examples": card["metrics"]["n_examples"],
                    "corpus_cer": card["metrics"]["corpus_cer"],
                    "corpus_wer": card["metrics"]["corpus_wer"],
                    "semantic_error_rate": card["metrics"]["semantic_error_rate"],
                    "proof_posture": card["evaluation"]["proof_posture"],
                    "missing_recommended_fields": len(
                        card["completeness"]["missing_recommended_fields"]
                    ),
                }
            )
        cohort_documents.append(
            {
                "cohort_id": cohort.cohort_id,
                "card_count": len(cohort_cards),
                "ranking_performed": can_rank,
                "ranking_key": ["corpus_cer", "corpus_wer", "run_id"] if can_rank else None,
                "comparison_authorized": cohort.payload["comparison_authorized"],
                "proof_posture": cohort.payload["proof_posture"],
                "prohibited_claims": cohort.payload.get("prohibited_claims", []),
            }
        )
    rows.sort(key=lambda row: (row["cohort_id"], row["rank"] or 0, row["run_id"]))
    return {
        "schema": dict(LEADERBOARD_SCHEMA),
        "leaderboard_id": leaderboard_id,
        "proof_posture": "local_artifact_only",
        "summary": {
            "card_count": len(cards),
            "cohort_count": len(cohorts),
            "ranked_cohort_count": ranked_cohorts,
            "cross_cohort_ranking_performed": False,
            "global_best_run": None,
            "raw_data_reads": 0,
            "signal_array_members_loaded": False,
            "model_runs_triggered": 0,
            "network_fetches": 0,
            "holdouts_reopened": 0,
        },
        "research_sources": research_sources,
        "cohorts": cohort_documents,
        "rows": rows,
        "interpretation_boundary": (
            "Ranks exist only inside exact cohorts explicitly authorized for comparison. "
            "No global ordering across different tasks, splits, sessions, units, or proof postures."
        ),
    }


def _render_core_files(
    cards: list[dict[str, Any]], leaderboard: dict[str, Any]
) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for card in sorted(cards, key=lambda item: item["run"]["run_id"]):
        run_id = card["run"]["run_id"]
        base = f"cards/{run_id}"
        files[f"{base}/card.json"] = _json_bytes(card)
        files[f"{base}/metrics.json"] = _json_bytes(card["metrics"])
        files[f"{base}/config.json"] = _json_bytes(card["config"])
        files[f"{base}/cache_metadata.json"] = _json_bytes(card["cache"])
        files[f"{base}/report.md"] = _render_card_markdown(card).encode("utf-8")
    files["leaderboard.json"] = _json_bytes(leaderboard)
    files["leaderboard.csv"] = _render_leaderboard_csv(leaderboard).encode("utf-8")
    files["leaderboard.md"] = _render_leaderboard_markdown(leaderboard).encode("utf-8")
    return files


def _render_card_markdown(card: Mapping[str, Any]) -> str:
    method = card["method"]
    metrics = card["metrics"]
    comparison = card.get("comparison")
    lines = [
        f"# {card['run']['display_name']}",
        "",
        f"- Run ID: `{card['run']['run_id']}`",
        f"- Cohort: `{card['run']['cohort_id']}`",
        f"- Proof posture: `{card['evaluation']['proof_posture']}`",
        f"- Method: `{method['name']}` (`{method['family']}`)",
        f"- Neural signal used: `{'yes' if method['uses_neural_signal'] else 'no'}`",
        f"- Deep learning used: `{'yes' if method['uses_deep_learning'] else 'no'}`",
        "",
        "## Metrics",
        "",
        "| Examples | CER | WER | SemER | Exact match |",
        "| ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {metrics['n_examples']} | {metrics['corpus_cer']:.6f} | "
            f"{metrics['corpus_wer']:.6f} | {_format_optional(metrics['semantic_error_rate'])} | "
            f"{_format_optional(metrics['exact_match_rate'])} |"
        ),
    ]
    if comparison:
        lines.extend(
            [
                "",
                "## Comparator",
                "",
                f"- Comparator run: `{comparison['comparator_run_id']}`",
                (
                    "- CER delta (method minus comparator): "
                    f"`{_format_optional(comparison['corpus_cer_delta_method_minus_comparator'])}`"
                ),
                (
                    "- Paired 95% CI: "
                    f"`{_format_optional(comparison['paired_bootstrap_delta_ci95'])}`"
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"- Source report: `{card['source_artifact']['report_path']}`",
            f"- Source report SHA-256: `{card['source_artifact']['report_sha256']}`",
            f"- Config SHA-256: `{card['config']['sha256']}`",
            "- Cache opened: `no`",
            "- Signal arrays loaded: `no`",
            "- Holdout reopened: `no`",
            "",
            "## Completeness",
            "",
            "Missing recommended fields:",
        ]
    )
    missing = card["completeness"]["missing_recommended_fields"]
    lines.extend(f"- `{item}`" for item in missing)
    if not missing:
        lines.append("- None")
    prohibited = card["proof"].get("prohibited_claims", [])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in prohibited)
    if not prohibited:
        lines.append("- No additional cohort-specific prohibitions recorded.")
    return "\n".join(lines) + "\n"


def _render_leaderboard_csv(leaderboard: Mapping[str, Any]) -> str:
    fields = (
        "cohort_id",
        "rank",
        "run_id",
        "method_family",
        "method_name",
        "uses_neural_signal",
        "n_examples",
        "corpus_cer",
        "corpus_wer",
        "semantic_error_rate",
        "proof_posture",
        "missing_recommended_fields",
    )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(leaderboard["rows"])
    return stream.getvalue()


def _render_leaderboard_markdown(leaderboard: Mapping[str, Any]) -> str:
    lines = [
        "# NeuroDecodeKit Leaderboard",
        "",
        "This is a cohort-local evidence index, not a global model ranking.",
        "",
        "| Cohort | Rank | Method | Signal | n | CER | WER | SemER | Proof |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in leaderboard["rows"]:
        rank = row["rank"] if row["rank"] is not None else "-"
        lines.append(
            f"| {row['cohort_id']} | {rank} | {row['method_name']} | "
            f"{'yes' if row['uses_neural_signal'] else 'no'} | {row['n_examples']} | "
            f"{row['corpus_cer']:.6f} | {row['corpus_wer']:.6f} | "
            f"{_format_optional(row['semantic_error_rate'])} | {row['proof_posture']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            leaderboard["interpretation_boundary"],
            "",
            "No raw data or signal arrays were read, no model was run, and no holdout was reopened.",
            "",
        ]
    )
    return "\n".join(lines)


def _completeness_warnings(card: Mapping[str, Any], missing: list[str]) -> list[str]:
    warnings = [f"missing_recommended:{path}" for path in missing]
    if card["method"]["fit_on_eval_targets"]:
        warnings.append("fit_on_eval_targets_smoke_only")
    if card["method"]["causal"] is False:
        warnings.append("noncausal_method")
    if card["metrics"]["semantic_error_rate"] is None:
        warnings.append("semantic_error_rate_not_measured")
    return warnings


def _collect_warnings(
    source_report: Mapping[str, Any], baseline: Mapping[str, Any]
) -> list[str]:
    values: list[str] = []
    for container in (source_report, baseline):
        warnings = container.get("warnings", [])
        if isinstance(warnings, list):
            values.extend(str(item) for item in warnings)
    return list(dict.fromkeys(values))


def _json_safe_mapping(value: Mapping[str, Any], label: str) -> dict[str, Any]:
    try:
        encoded = json.dumps(value, allow_nan=False, sort_keys=True)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not finite JSON data") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{label} must be an object")
    return decoded


def _read_json_object(path: Path, *, max_bytes: int) -> dict[str, Any]:
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"JSON file {path} exceeds {max_bytes} bytes")
    return _decode_json_object(path.read_bytes(), path)


def _decode_json_object(content: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _resolve_inside_root(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"source report escapes project root: {value}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"source report does not exist: {value}")
    return path


def _resolve_output_inside_root(root: Path, value: str | Path) -> Path:
    requested = Path(value)
    path = requested.resolve() if requested.is_absolute() else (root / requested).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"output directory escapes project root: {value}") from exc
    if path == root or ".git" in relative.parts:
        raise ValueError(f"refusing unsafe output directory: {path}")
    return path


def _validate_schema(value: Any, expected: Mapping[str, Any], label: str) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} needs a schema object")
    if value.get("name") != expected["name"] or value.get("version") != expected["version"]:
        raise ValueError(
            f"unsupported {label} schema: {value.get('name')} v{value.get('version')}"
        )


def _validate_id(value: str, label: str) -> None:
    if not _SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} must match {_SAFE_ID.pattern}: {value!r}")


def _required_string(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return item


def _required_bool(value: Mapping[str, Any], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ValueError(f"{key} must be boolean")
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ValueError(f"{key} must be a list")
    return item


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ValueError(f"{key} must be an object")
    return item


def _unique_by_id(values: Iterable[Any], attribute: str) -> dict[str, Any]:
    output = {}
    for value in values:
        item_id = getattr(value, attribute)
        if item_id in output:
            raise ValueError(f"duplicate {attribute}: {item_id}")
        output[item_id] = value
    return output


def _get_path(value: Mapping[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _finite_nonnegative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value >= 0
    )


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _artifact_set_sha256(files: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _format_optional(value: Any) -> str:
    if value is None:
        return "not measured"
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, list):
        return "[" + ", ".join(_format_optional(item) for item in value) + "]"
    return str(value)
