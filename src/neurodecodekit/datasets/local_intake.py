"""Dependency-free, metadata-only intake for local neurophysiology recordings."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_NAME = "neurodecodekit-local-intake"
SCHEMA_VERSION = "0.1.0"
AUDIT_SCHEMA_NAME = "neurodecodekit-local-intake-audit"
ARTIFACT_JSON = "intake.json"
ARTIFACT_MARKDOWN = "intake.md"
ARTIFACT_AUDIT = "intake.audit.json"

_MIB = 1024 * 1024
_ARCHIVE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tbz2",
    ".tar.xz",
    ".txz",
    ".7z",
    ".rar",
)
_PICKLE_SUFFIXES = (".pickle", ".pkl", ".joblib", ".npy", ".npz")
_EXECUTABLE_SUFFIXES = (".exe", ".dll", ".dylib", ".so", ".sh", ".bat", ".cmd")
_RAW_CANDIDATE_SUFFIXES = {".vhdr", ".edf", ".bdf", ".set", ".fif"}
_FORBIDDEN_REPORT_KEYS = {"target_text", "labels", "prediction", "decoded_text"}


@dataclass(frozen=True)
class IntakeLimits:
    """Hard limits for one metadata-only scan."""

    max_files: int = 256
    max_depth: int = 8
    max_declared_input_bytes: int = 4 * 1024 * _MIB
    max_text_file_bytes: int = 1 * _MIB
    max_text_total_bytes: int = 8 * _MIB
    max_output_bytes: int = 4 * _MIB

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")


@dataclass
class _AccessTracker:
    metadata_files_read: int = 0
    metadata_text_bytes_read: int = 0

    def report_dict(self) -> dict[str, int]:
        return {
            "metadata_files_read": self.metadata_files_read,
            "metadata_text_bytes_read": self.metadata_text_bytes_read,
            "binary_signal_files_opened": 0,
            "binary_signal_bytes_read": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "network_calls": 0,
            "target_or_label_files_read": 0,
        }


@dataclass(frozen=True)
class IntakeResult:
    """A deterministic report plus process measurements kept in a sidecar."""

    report: dict[str, Any]
    scan_runtime_sec: float
    peak_rss_bytes: int | None


def inspect_local_recording(
    source_path: str | Path,
    *,
    root_path: str | Path | None = None,
    modality: str | None = None,
    device_type: str | None = None,
    registry_path: str | Path | None = None,
    hash_text_metadata: bool = False,
    limits: IntakeLimits | None = None,
) -> IntakeResult:
    """Inspect local recording metadata without opening binary signal content."""

    started_at = time.perf_counter()
    limits = limits or IntakeLimits()
    declared_modality = _clean_optional_label(modality, field="modality")
    declared_device = _clean_optional_label(device_type, field="device_type")
    source, root = _resolve_source_and_root(source_path, root_path=root_path)
    tracker = _AccessTracker()
    warnings = [
        "metadata_only_no_binary_signal_read",
        "neural_recordings_and_derived_metadata_may_be_sensitive",
        "source_paths_are_relative_and_absolute_paths_are_omitted",
        "no_signal_quality_prediction_or_decoding_claim",
    ]

    if source.is_dir():
        inspected = _inspect_bids_directory(
            source,
            root=root,
            tracker=tracker,
            limits=limits,
            hash_text_metadata=hash_text_metadata,
        )
    else:
        inspected = _inspect_single_file(
            source,
            root=root,
            tracker=tracker,
            limits=limits,
            hash_text_metadata=hash_text_metadata,
        )

    registry = _inspect_registry(
        registry_path,
        tracker=tracker,
        limits=limits,
    )
    if not registry["bound"]:
        warnings.append("dataset_registry_not_bound")

    files = sorted(inspected["files"], key=lambda row: row["path"])
    _validate_file_rows(files, limits=limits)
    declared_input_bytes = sum(int(row["size_bytes"]) for row in files)
    source_manifest_sha256 = _sha256_json(files)
    selected_relative = _relative_path(source, root)
    scanner_config = {
        "schema_version": SCHEMA_VERSION,
        "path_policy": "resolved_local_paths_reported_relative_to_selected_root",
        "hash_text_metadata": bool(hash_text_metadata),
        "declared_modality": declared_modality,
        "declared_device_type": declared_device,
        "registry_bound": bool(registry["bound"]),
        "limits": asdict(limits),
    }
    scanner_config_sha256 = _sha256_json(scanner_config)
    item_id_sha256 = _sha256_json(
        {
            "format_family": inspected["format_family"],
            "selected_path": selected_relative,
            "source_manifest_sha256": source_manifest_sha256,
        }
    )
    level_zero_passed = not inspected["refusals"]
    compatibility = _compatibility_report(
        level_zero_passed=level_zero_passed,
        level_zero_refusals=inspected["refusals"],
    )
    inferred_modality = inspected.get("inferred_modality")
    resolved_modality = declared_modality or inferred_modality or "unknown"
    if declared_modality and inferred_modality and declared_modality != inferred_modality:
        warnings.append("declared_modality_differs_from_filename_inference")

    report: dict[str, Any] = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": "metadata_only_synthetic_fixture_compatible",
        "status": "recognized" if level_zero_passed else "refused",
        "item": {
            "item_id_sha256": item_id_sha256,
            "subject_id": inspected["identity"].get("subject_id"),
            "session_id": inspected["identity"].get("session_id"),
            "task_id": inspected["identity"].get("task_id"),
            "run_id": inspected["identity"].get("run_id"),
            "trial_id": None,
            "split_id": None,
            "identity_source": inspected["identity"].get("identity_source", "unavailable"),
        },
        "source": {
            "selected_path": selected_relative,
            "root_exposure": "relative_paths_only",
            "format_family": inspected["format_family"],
            "file_count": len(files),
            "files": files,
            "source_manifest_sha256": source_manifest_sha256,
            "binary_content_hash_status": "unavailable_without_binary_signal_read",
        },
        "recording": {
            "modality": resolved_modality,
            "modality_source": (
                "user_declared"
                if declared_modality
                else "bids_filename"
                if inferred_modality
                else "unavailable"
            ),
            "device_type": declared_device or "unknown",
            "device_type_source": "user_declared" if declared_device else "unavailable",
            "raw_family": inspected.get("raw_family") or inspected["format_family"],
            "channel_count": inspected["metadata"].get("channel_count"),
            "channel_names": inspected["metadata"].get("channel_names", []),
            "channel_types": inspected["metadata"].get("channel_types", []),
            "sampling_rate_hz": inspected["metadata"].get("sampling_rate_hz"),
            "duration_sec": None,
            "reference": inspected["metadata"].get("reference"),
            "source_filters": inspected["metadata"].get("source_filters"),
            "units": inspected["metadata"].get("units", []),
            "geometry": {
                "available": False,
                "status": "unavailable_at_metadata_only_level",
            },
            "events": {
                "available": False,
                "status": "not_read_target_and_event_files_excluded_from_rw1",
            },
            "companions": inspected.get("companions", []),
            "format_metadata": inspected["metadata"].get("format_metadata", {}),
        },
        "causality": {
            "producer_causal": None,
            "status": "not_applicable_raw_recording_no_producer",
            "required_left_context_samples": None,
            "required_right_context_samples": None,
            "end_to_end_latency_measured": False,
        },
        "compatibility": compatibility,
        "authorization": {
            "benchmark_authorized": False,
            "signal_read_authorized": False,
            "split_bound": False,
            "status": "metadata_inspection_only",
        },
        "provenance": {
            "scanner_config": scanner_config,
            "scanner_config_sha256": scanner_config_sha256,
            "registry": registry,
            "source_manifest_sha256": source_manifest_sha256,
            "payload_hash": None,
            "payload_hash_status": "unavailable_without_binary_signal_read",
        },
        "access_counts": tracker.report_dict(),
        "resources": {
            "declared_input_bytes": declared_input_bytes,
            "metadata_text_bytes_read": tracker.metadata_text_bytes_read,
            "binary_signal_bytes_read": 0,
            "output_bytes": None,
            "output_bytes_status": "measured_in_intake_audit_sidecar",
            "caps": asdict(limits),
        },
        "measurements": {
            "runtime_sec": None,
            "peak_rss_bytes": None,
            "measurement_sidecar": ARTIFACT_AUDIT,
            "scope": "scan_and_report_build_measured_outside_deterministic_core",
            "end_to_end_latency_measured": False,
        },
        "artifacts": {
            "deterministic_json": ARTIFACT_JSON,
            "deterministic_markdown": ARTIFACT_MARKDOWN,
            "measured_audit_sidecar": ARTIFACT_AUDIT,
        },
        "unavailable_fields": sorted(
            {
                "binary_content_hash",
                "duration_sec",
                "end_to_end_latency",
                "event_contents",
                "geometry",
                "payload_hash",
                "split_id",
                "trial_id",
            }
            | set(inspected.get("unavailable_fields", []))
        ),
        "warnings": sorted(set(warnings + inspected["warnings"])),
        "refusals": sorted(set(inspected["refusals"])),
        "claim_boundary": {
            "allowed": [
                "local metadata format recognition",
                "bounded companion and path validation",
                "level_0 compatibility reporting",
            ],
            "prohibited": [
                "binary signal readability",
                "signal quality",
                "task compatibility",
                "model compatibility",
                "benchmark authorization",
                "prediction or decoding",
                "neural advantage",
                "real-time or portable hardware performance",
            ],
        },
        "hashes": {"report_payload_sha256": None},
    }
    report["hashes"]["report_payload_sha256"] = _report_payload_sha256(report)
    validate_intake_report(report)
    return IntakeResult(
        report=report,
        scan_runtime_sec=round(time.perf_counter() - started_at, 6),
        peak_rss_bytes=_peak_rss_bytes(),
    )


def write_intake_artifacts(
    result: IntakeResult,
    out_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write deterministic JSON/Markdown plus a measured audit sidecar."""

    validate_intake_report(result.report)
    output_dir = Path(out_dir).expanduser()
    _validate_output_directory(output_dir, overwrite=overwrite)
    report_bytes = _json_bytes(result.report)
    markdown_bytes = render_intake_markdown(result.report).encode("utf-8")
    max_output_bytes = int(result.report["resources"]["caps"]["max_output_bytes"])
    audit = {
        "schema": {"name": AUDIT_SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": "measured_metadata_only_audit_not_deterministic_core",
        "measurements": {
            "runtime_sec": result.scan_runtime_sec,
            "runtime_scope": "metadata_scan_and_deterministic_report_build",
            "peak_rss_bytes": result.peak_rss_bytes,
            "peak_rss_scope": "process_high_water_mark",
            "end_to_end_latency_measured": False,
        },
        "access_counts": dict(result.report["access_counts"]),
        "resources": {
            "declared_input_bytes": result.report["resources"]["declared_input_bytes"],
            "metadata_text_bytes_read": result.report["resources"][
                "metadata_text_bytes_read"
            ],
            "binary_signal_bytes_read": 0,
            "deterministic_json_bytes": len(report_bytes),
            "deterministic_markdown_bytes": len(markdown_bytes),
            "audit_json_bytes": 0,
            "total_output_bytes": 0,
            "max_output_bytes": max_output_bytes,
            "output_cap_passed": True,
        },
        "artifacts": {
            ARTIFACT_JSON: {
                "bytes": len(report_bytes),
                "sha256": _sha256_bytes(report_bytes),
            },
            ARTIFACT_MARKDOWN: {
                "bytes": len(markdown_bytes),
                "sha256": _sha256_bytes(markdown_bytes),
            },
            ARTIFACT_AUDIT: {"bytes": 0, "sha256": None},
        },
        "warnings": [
            "runtime_and_peak_rss_are_measured_and_excluded_from_deterministic_core",
            "audit_sidecar_does_not_self_hash",
        ],
    }
    for _ in range(12):
        audit_bytes = _json_bytes(audit)
        audit_size = len(audit_bytes)
        total_size = len(report_bytes) + len(markdown_bytes) + audit_size
        if (
            audit["resources"]["audit_json_bytes"] == audit_size
            and audit["resources"]["total_output_bytes"] == total_size
            and audit["artifacts"][ARTIFACT_AUDIT]["bytes"] == audit_size
        ):
            break
        audit["resources"]["audit_json_bytes"] = audit_size
        audit["resources"]["total_output_bytes"] = total_size
        audit["artifacts"][ARTIFACT_AUDIT]["bytes"] = audit_size
    else:  # pragma: no cover - integer byte fields converge quickly
        raise RuntimeError("Intake audit byte accounting did not converge.")
    audit_bytes = _json_bytes(audit)
    total_output_bytes = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
    if total_output_bytes > max_output_bytes:
        raise ValueError(
            "Planned intake artifacts exceed output cap: "
            f"{total_output_bytes} > {max_output_bytes} bytes."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_artifact(output_dir / ARTIFACT_JSON, report_bytes, overwrite=overwrite)
    _write_artifact(output_dir / ARTIFACT_MARKDOWN, markdown_bytes, overwrite=overwrite)
    _write_artifact(output_dir / ARTIFACT_AUDIT, audit_bytes, overwrite=overwrite)
    return {
        "status": result.report["status"],
        "format_family": result.report["source"]["format_family"],
        "compatibility_level": result.report["compatibility"]["current_level"],
        "declared_input_bytes": result.report["resources"]["declared_input_bytes"],
        "metadata_text_bytes_read": result.report["resources"][
            "metadata_text_bytes_read"
        ],
        "binary_signal_bytes_read": 0,
        "runtime_sec": result.scan_runtime_sec,
        "peak_rss_bytes": result.peak_rss_bytes,
        "total_output_bytes": total_output_bytes,
        "max_output_bytes": max_output_bytes,
        "output_cap_passed": True,
        "raw_data_reads": 0,
        "real_cache_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "network_calls": 0,
        "end_to_end_latency_measured": False,
        "producer_causal": None,
        "warnings": result.report["warnings"],
        "refusals": result.report["refusals"],
        "artifacts": [ARTIFACT_JSON, ARTIFACT_MARKDOWN, ARTIFACT_AUDIT],
    }


def load_intake_report(
    report_path: str | Path,
    *,
    audit_path: str | Path | None = None,
    max_report_bytes: int = 4 * _MIB,
) -> dict[str, Any]:
    """Load and strictly validate an intake report and optional audit sidecar."""

    report_file = _safe_report_file(report_path, max_bytes=max_report_bytes)
    report_bytes = report_file.read_bytes()
    try:
        report = json.loads(report_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid intake report JSON: {report_file.name}") from exc
    validate_intake_report(report)

    selected_audit: Path | None
    if audit_path is not None:
        selected_audit = _safe_report_file(audit_path, max_bytes=max_report_bytes)
    else:
        candidate = report_file.with_name(ARTIFACT_AUDIT)
        selected_audit = candidate if candidate.is_file() and not candidate.is_symlink() else None
    audit = None
    if selected_audit is not None:
        audit_bytes = selected_audit.read_bytes()
        try:
            audit = json.loads(audit_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid intake audit JSON: {selected_audit.name}") from exc
        _validate_intake_audit(
            audit,
            report_file=report_file,
            report_bytes=report_bytes,
            audit_file=selected_audit,
            audit_bytes=audit_bytes,
        )
    return {
        "schema": dict(report["schema"]),
        "status": report["status"],
        "item_id_sha256": report["item"]["item_id_sha256"],
        "format_family": report["source"]["format_family"],
        "modality": report["recording"]["modality"],
        "file_count": report["source"]["file_count"],
        "compatibility_level": report["compatibility"]["current_level"],
        "report_payload_sha256": report["hashes"]["report_payload_sha256"],
        "source_manifest_sha256": report["source"]["source_manifest_sha256"],
        "registry_sha256": report["provenance"]["registry"]["sha256"],
        "access_counts": dict(report["access_counts"]),
        "resources": dict(report["resources"]),
        "measurements": audit["measurements"] if audit else None,
        "output": audit["resources"] if audit else None,
        "warnings": list(report["warnings"]),
        "refusals": list(report["refusals"]),
        "audit_validated": audit is not None,
    }


def validate_intake_report(report: dict[str, Any]) -> None:
    """Strictly validate one deterministic metadata-only report."""

    if not isinstance(report, dict):
        raise ValueError("Intake report must be a JSON object.")
    required = {
        "schema",
        "status",
        "item",
        "source",
        "recording",
        "causality",
        "compatibility",
        "authorization",
        "provenance",
        "access_counts",
        "resources",
        "measurements",
        "warnings",
        "refusals",
        "claim_boundary",
        "hashes",
    }
    missing = sorted(required - set(report))
    if missing:
        raise ValueError(f"Intake report is missing required fields: {missing}")
    if report["schema"] != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported intake report schema.")
    if any(key in _FORBIDDEN_REPORT_KEYS for key in _all_mapping_keys(report)):
        raise ValueError("Intake report contains a forbidden target or prediction field.")

    files = report["source"].get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Intake report source files must be a nonempty list.")
    limits_payload = report["resources"].get("caps")
    try:
        limits = IntakeLimits(**limits_payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("Intake report contains invalid resource caps.") from exc
    _validate_file_rows(files, limits=limits)
    if report["source"].get("file_count") != len(files):
        raise ValueError("Source file_count does not match source files.")
    expected_declared = sum(int(row["size_bytes"]) for row in files)
    if report["resources"].get("declared_input_bytes") != expected_declared:
        raise ValueError("Declared input bytes do not match source file sizes.")
    expected_manifest_hash = _sha256_json(files)
    if report["source"].get("source_manifest_sha256") != expected_manifest_hash:
        raise ValueError("Source manifest hash mismatch.")
    if report["provenance"].get("source_manifest_sha256") != expected_manifest_hash:
        raise ValueError("Provenance source manifest hash mismatch.")
    scanner_config = report["provenance"].get("scanner_config")
    if report["provenance"].get("scanner_config_sha256") != _sha256_json(scanner_config):
        raise ValueError("Scanner configuration hash mismatch.")
    if not isinstance(scanner_config, dict) or scanner_config.get("limits") != limits_payload:
        raise ValueError("Scanner configuration limits do not match resource caps.")

    selected_path = report["source"].get("selected_path")
    _validate_relative_report_path(selected_path)
    if selected_path != "." and selected_path not in {row["path"] for row in files}:
        raise ValueError("Selected source path is absent from the source manifest.")
    expected_item_id = _sha256_json(
        {
            "format_family": report["source"].get("format_family"),
            "selected_path": selected_path,
            "source_manifest_sha256": expected_manifest_hash,
        }
    )
    if report["item"].get("item_id_sha256") != expected_item_id:
        raise ValueError("Item identity hash mismatch.")

    registry = report["provenance"].get("registry")
    if not isinstance(registry, dict) or not isinstance(registry.get("bound"), bool):
        raise ValueError("Registry provenance is malformed.")
    if scanner_config.get("registry_bound") != registry["bound"]:
        raise ValueError("Scanner and registry binding flags disagree.")
    registry_bytes = registry.get("bytes_read")
    if registry["bound"]:
        if not isinstance(registry.get("schema_name"), str) or not isinstance(
            registry.get("schema_version"), str
        ):
            raise ValueError("Bound registry is missing schema metadata.")
        if not isinstance(registry.get("record_count"), int) or registry["record_count"] < 0:
            raise ValueError("Bound registry has an invalid record count.")
        if not isinstance(registry_bytes, int) or not 0 <= registry_bytes <= limits.max_text_file_bytes:
            raise ValueError("Bound registry has an invalid byte count.")
        if not re.fullmatch(r"[0-9a-f]{64}", str(registry.get("sha256"))):
            raise ValueError("Bound registry has an invalid SHA-256.")
    elif registry_bytes != 0 or registry.get("sha256") is not None:
        raise ValueError("Unbound registry cannot declare bytes or a hash.")

    access = report["access_counts"]
    zero_fields = (
        "binary_signal_files_opened",
        "binary_signal_bytes_read",
        "raw_data_reads",
        "real_cache_reads",
        "model_runs",
        "training_runs",
        "network_calls",
        "target_or_label_files_read",
    )
    if any(access.get(field) != 0 for field in zero_fields):
        raise ValueError("Metadata-only intake reports must keep all forbidden access counts at zero.")
    if access.get("metadata_text_bytes_read") != report["resources"].get(
        "metadata_text_bytes_read"
    ):
        raise ValueError("Metadata byte counters disagree.")
    readable_roles = {"brainvision_header", "bids_dataset_description"}
    read_rows = [row for row in files if row["content_read"]]
    if any(row["role"] not in readable_roles for row in read_rows):
        raise ValueError("A binary or non-allowlisted source file is marked as content-read.")
    if any(row["size_bytes"] > limits.max_text_file_bytes for row in read_rows):
        raise ValueError("A text metadata source exceeds its configured per-file cap.")
    if any(row["content_sha256"] is not None for row in files if not row["content_read"]):
        raise ValueError("Unread source files cannot declare content hashes.")
    if scanner_config.get("hash_text_metadata") and any(
        row["content_sha256"] is None for row in read_rows
    ):
        raise ValueError("Configured text hashing is missing a source metadata hash.")
    expected_metadata_files_read = len(read_rows) + int(registry["bound"])
    if access.get("metadata_files_read") != expected_metadata_files_read:
        raise ValueError("Metadata file read counter does not match allowlisted inputs.")
    expected_metadata_bytes_read = sum(row["size_bytes"] for row in read_rows) + int(
        registry_bytes
    )
    if access.get("metadata_text_bytes_read") != expected_metadata_bytes_read:
        raise ValueError("Metadata byte counter does not match allowlisted inputs.")
    if access.get("metadata_text_bytes_read", -1) > limits.max_text_total_bytes:
        raise ValueError("Metadata text byte counter exceeds configured cap.")
    if report["resources"].get("binary_signal_bytes_read") != 0:
        raise ValueError("Binary signal bytes must remain zero in RW1.")

    compatibility = report["compatibility"]
    levels = compatibility.get("levels")
    if not isinstance(levels, list) or [row.get("level") for row in levels] != list(range(7)):
        raise ValueError("Compatibility report must contain ordered levels 0 through 6.")
    level_zero_passed = bool(levels[0].get("passed"))
    expected_level = 0 if level_zero_passed else -1
    if compatibility.get("current_level") != expected_level:
        raise ValueError("Compatibility current level is inconsistent with level 0.")
    if any(row.get("passed") for row in levels[1:]):
        raise ValueError("RW1 cannot pass compatibility levels above 0.")
    if any(not row.get("refusal_reason") for row in levels[1:]):
        raise ValueError("Every unavailable higher compatibility level needs a refusal reason.")
    expected_status = "recognized" if level_zero_passed else "refused"
    if report["status"] != expected_status:
        raise ValueError("Report status is inconsistent with level-0 compatibility.")
    if report["authorization"].get("benchmark_authorized") is not False:
        raise ValueError("RW1 reports cannot authorize a benchmark.")
    if report["authorization"].get("signal_read_authorized") is not False:
        raise ValueError("RW1 reports cannot authorize a signal read.")
    if report["causality"].get("end_to_end_latency_measured") is not False:
        raise ValueError("RW1 cannot claim measured end-to-end latency.")
    if report["causality"].get("producer_causal") is not None:
        raise ValueError("Raw metadata intake cannot declare a producer causality result.")
    if report["measurements"].get("runtime_sec") is not None or report[
        "measurements"
    ].get("peak_rss_bytes") is not None:
        raise ValueError("Measured values must stay outside the deterministic core report.")
    if report["resources"].get("output_bytes") is not None:
        raise ValueError("Output bytes must be measured in the audit sidecar.")
    if report["provenance"].get("payload_hash") is not None:
        raise ValueError("RW1 cannot declare a binary payload hash.")
    if report["warnings"] != sorted(set(report["warnings"])):
        raise ValueError("Warnings must be sorted and unique.")
    if report["refusals"] != sorted(set(report["refusals"])):
        raise ValueError("Refusals must be sorted and unique.")
    for companion in report["recording"].get("companions", []):
        path = companion.get("path")
        if path is not None:
            _validate_relative_report_path(path)
    report_hash = report["hashes"].get("report_payload_sha256")
    if report_hash != _report_payload_sha256(report):
        raise ValueError("Intake report payload hash mismatch.")


def render_intake_markdown(report: dict[str, Any]) -> str:
    """Render the deterministic human-readable level-0 report."""

    validate_intake_report(report)
    recording = report["recording"]
    resources = report["resources"]
    access = report["access_counts"]
    lines = [
        "# Local Neurodata Intake Report",
        "",
        f"- Schema: `{report['schema']['name']} {report['schema']['version']}`",
        f"- Status: **{report['status']}**",
        f"- Compatibility level: `{report['compatibility']['current_level']}`",
        f"- Format family: `{report['source']['format_family']}`",
        f"- Modality: `{recording['modality']}`",
        f"- Device type: `{recording['device_type']}`",
        f"- Item ID: `{report['item']['item_id_sha256']}`",
        "",
        "## Recording Metadata",
        "",
        f"- Subject: `{_markdown_value(report['item']['subject_id'])}`",
        f"- Session: `{_markdown_value(report['item']['session_id'])}`",
        f"- Task: `{_markdown_value(report['item']['task_id'])}`",
        f"- Run: `{_markdown_value(report['item']['run_id'])}`",
        f"- Channels: `{_markdown_value(recording['channel_count'])}`",
        f"- Sampling rate: `{_markdown_value(recording['sampling_rate_hz'])}` Hz",
        f"- Geometry: `{recording['geometry']['status']}`",
        f"- Events: `{recording['events']['status']}`",
        "",
        "## Source Files",
        "",
        "| Relative path | Role | Bytes | Content read |",
        "|---|---|---:|---|",
    ]
    for row in report["source"]["files"]:
        lines.append(
            f"| `{row['path']}` | `{row['role']}` | {row['size_bytes']} | "
            f"{str(row['content_read']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Resource And Access Audit",
            "",
            f"- Declared input bytes: `{resources['declared_input_bytes']}`",
            f"- Metadata text bytes read: `{resources['metadata_text_bytes_read']}`",
            "- Binary signal bytes read: `0`",
            f"- Metadata files read: `{access['metadata_files_read']}`",
            "- Raw data reads: `0`",
            "- Real-cache reads: `0`",
            "- Model runs: `0`",
            "- Training runs: `0`",
            "- Network calls: `0`",
            "- Runtime and peak RSS: measured in `intake.audit.json`",
            "- End-to-end latency measured: `false`",
            "",
            "## Provenance",
            "",
            f"- Source manifest SHA-256: `{report['source']['source_manifest_sha256']}`",
            f"- Scanner config SHA-256: `{report['provenance']['scanner_config_sha256']}`",
            f"- Registry SHA-256: `{_markdown_value(report['provenance']['registry']['sha256'])}`",
            f"- Report payload SHA-256: `{report['hashes']['report_payload_sha256']}`",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    lines.extend(["", "## Refusals", ""])
    if report["refusals"]:
        lines.extend(f"- `{refusal}`" for refusal in report["refusals"])
    else:
        lines.append("- None at compatibility level 0.")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This report proves local metadata recognition and bounded path/companion",
            "validation only. It does not prove signal readability, signal quality, task",
            "compatibility, prediction, decoding, neural advantage, or real-time behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def _inspect_single_file(
    source: Path,
    *,
    root: Path,
    tracker: _AccessTracker,
    limits: IntakeLimits,
    hash_text_metadata: bool,
) -> dict[str, Any]:
    _ensure_regular_file(source, label="selected source")
    disallowed = _disallowed_input_refusal(source)
    if disallowed is not None:
        family, reason = disallowed
        return _refused_file_inspection(source, root=root, family=family, reason=reason)
    suffix = source.suffix.lower()
    if suffix in {".eeg", ".vmrk"}:
        return _refused_file_inspection(
            source,
            root=root,
            family="brainvision_companion",
            reason="select_brainvision_vhdr_instead_of_companion",
        )
    if suffix == ".fdt":
        return _refused_file_inspection(
            source,
            root=root,
            family="eeglab_companion",
            reason="select_eeglab_set_instead_of_fdt_companion",
        )
    if suffix == ".vhdr":
        return _inspect_brainvision(
            source,
            root=root,
            tracker=tracker,
            limits=limits,
            hash_text_metadata=hash_text_metadata,
        )
    if suffix == ".edf":
        return _simple_binary_inspection(source, root=root, family="edf_or_edf_plus")
    if suffix == ".bdf":
        return _simple_binary_inspection(source, root=root, family="bdf")
    if suffix == ".set":
        return _inspect_eeglab(source, root=root)
    if suffix == ".fif":
        return _inspect_fif(source, root=root)
    return _refused_file_inspection(
        source,
        root=root,
        family="unsupported",
        reason=(
            "unsupported_recording_format_expected_vhdr_edf_bdf_set_fif_or_bids_root"
        ),
    )


def _refused_file_inspection(
    source: Path,
    *,
    root: Path,
    family: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "format_family": family,
        "raw_family": family,
        "files": [_file_row(source, root=root, role=f"{family}_input_not_read")],
        "companions": [],
        "metadata": _empty_metadata(),
        "identity": _empty_identity(),
        "inferred_modality": None,
        "warnings": ["input_content_not_read"],
        "refusals": [reason],
        "unavailable_fields": [
            "channel_count",
            "channel_names",
            "sampling_rate_hz",
            "reference",
        ],
    }


def _simple_binary_inspection(source: Path, *, root: Path, family: str) -> dict[str, Any]:
    return {
        "format_family": family,
        "raw_family": family,
        "files": [_file_row(source, root=root, role="binary_signal_container")],
        "companions": [],
        "metadata": _empty_metadata(),
        "identity": _empty_identity(),
        "inferred_modality": None,
        "warnings": [
            "binary_header_not_opened_at_metadata_only_level",
            "exact_subtype_and_signal_metadata_unavailable_without_optional_reader",
        ],
        "refusals": [],
        "unavailable_fields": [
            "channel_count",
            "channel_names",
            "sampling_rate_hz",
            "reference",
        ],
    }


def _inspect_brainvision(
    header: Path,
    *,
    root: Path,
    tracker: _AccessTracker,
    limits: IntakeLimits,
    hash_text_metadata: bool,
) -> dict[str, Any]:
    text, raw, encoding = _read_bounded_text(
        header,
        tracker=tracker,
        limits=limits,
        purpose="brainvision_header",
    )
    parsed = _parse_brainvision_header(text)
    warnings: list[str] = [
        "brainvision_marker_content_not_read",
        "brainvision_binary_signal_content_not_read",
    ]
    refusals: list[str] = []
    companions: list[dict[str, Any]] = []
    rows = [
        _file_row(
            header,
            root=root,
            role="brainvision_header",
            content_read=True,
            content_sha256=_sha256_bytes(raw) if hash_text_metadata else None,
        )
    ]
    role_specs = (
        ("datafile", ".eeg", "brainvision_signal"),
        ("markerfile", ".vmrk", "brainvision_marker"),
    )
    resolved_companions: dict[str, Path] = {}
    for key, expected_suffix, role in role_specs:
        values = parsed["keys"].get(key, [])
        if len(values) != 1:
            reason = (
                f"brainvision_missing_{key}"
                if not values
                else f"brainvision_duplicate_{key}_role"
            )
            refusals.append(reason)
            companions.append(
                {
                    "role": role,
                    "path": None,
                    "exists": False,
                    "status": reason,
                }
            )
            continue
        try:
            companion = _resolve_companion_path(
                header,
                values[0],
                root=root,
                expected_suffix=expected_suffix,
            )
        except ValueError as exc:
            reason = f"brainvision_unsafe_{key}: {exc}"
            refusals.append(reason)
            companions.append(
                {"role": role, "path": None, "exists": False, "status": reason}
            )
            continue
        relative = _relative_path_non_strict(companion, root)
        if not companion.exists():
            reason = f"brainvision_missing_companion_{role}"
            refusals.append(reason)
            companions.append(
                {"role": role, "path": relative, "exists": False, "status": reason}
            )
            continue
        _ensure_regular_file(companion, label=f"BrainVision {role}")
        resolved_companions[role] = companion.resolve(strict=True)
        rows.append(_file_row(companion, root=root, role=role))
        companions.append(
            {"role": role, "path": relative, "exists": True, "status": "present"}
        )
    if len(set(resolved_companions.values())) != len(resolved_companions):
        refusals.append("brainvision_duplicate_companion_roles")

    channel_count = _parse_positive_int(parsed["single"].get("numberofchannels"))
    sampling_interval_us = _parse_positive_float(
        parsed["single"].get("samplinginterval")
    )
    channel_names = parsed["channel_names"]
    if channel_count is not None and channel_names and len(channel_names) != channel_count:
        warnings.append("brainvision_channel_name_count_mismatch")
    units = sorted(set(parsed["units"]))
    metadata = _empty_metadata()
    metadata.update(
        {
            "channel_count": channel_count,
            "channel_names": channel_names,
            "sampling_rate_hz": (
                round(1_000_000.0 / sampling_interval_us, 9)
                if sampling_interval_us
                else None
            ),
            "units": units,
            "format_metadata": {
                "text_encoding": encoding,
                "data_format": parsed["single"].get("dataformat"),
                "data_orientation": parsed["single"].get("dataorientation"),
            },
        }
    )
    return {
        "format_family": "brainvision",
        "raw_family": "brainvision",
        "files": rows,
        "companions": companions,
        "metadata": metadata,
        "identity": _empty_identity(),
        "inferred_modality": None,
        "warnings": warnings,
        "refusals": refusals,
        "unavailable_fields": [
            "channel_types",
            "duration_sec",
            "geometry",
            "reference",
            "source_filters",
        ],
    }


def _inspect_eeglab(source: Path, *, root: Path) -> dict[str, Any]:
    matching_fdt: list[Path] = []
    for sibling in source.parent.iterdir():
        if sibling.name.casefold() == f"{source.stem}.fdt".casefold():
            if sibling.is_symlink():
                raise ValueError("EEGLAB companion cannot be a symlink.")
            _ensure_regular_file(sibling, label="EEGLAB .fdt companion")
            matching_fdt.append(sibling)
    rows = [_file_row(source, root=root, role="eeglab_set_container")]
    refusals: list[str] = []
    companions: list[dict[str, Any]] = []
    warnings = ["eeglab_set_content_not_read_at_metadata_only_level"]
    if len(matching_fdt) > 1:
        refusals.append("eeglab_duplicate_fdt_companion_role")
    elif matching_fdt:
        companion = matching_fdt[0]
        rows.append(_file_row(companion, root=root, role="eeglab_fdt_signal"))
        companions.append(
            {
                "role": "eeglab_fdt_signal",
                "path": _relative_path(companion, root),
                "exists": True,
                "status": "present_by_sibling_name_not_set_declaration",
            }
        )
    else:
        warnings.append("eeglab_external_fdt_requirement_unavailable_without_set_read")
        companions.append(
            {
                "role": "eeglab_fdt_signal",
                "path": None,
                "exists": False,
                "status": "not_declared_or_missing_metadata_only_unknown",
            }
        )
    return {
        "format_family": "eeglab",
        "raw_family": "eeglab",
        "files": rows,
        "companions": companions,
        "metadata": _empty_metadata(),
        "identity": _empty_identity(),
        "inferred_modality": None,
        "warnings": warnings,
        "refusals": refusals,
        "unavailable_fields": [
            "channel_count",
            "channel_names",
            "sampling_rate_hz",
            "reference",
        ],
    }


def _inspect_fif(source: Path, *, root: Path) -> dict[str, Any]:
    selected_stem = source.stem
    bids_match = re.match(
        r"^(?P<prefix>.*)_split-(?P<index>\d+)(?P<suffix>_.+)$",
        selected_stem,
        flags=re.IGNORECASE,
    )
    standard_match = re.match(r"^(?P<prefix>.*)-(?P<index>\d+)$", selected_stem)
    candidates: list[tuple[Path, int | None, str]] = []
    refusals: list[str] = []
    if bids_match:
        prefix = bids_match.group("prefix")
        suffix = bids_match.group("suffix")
        pattern = re.compile(
            rf"^{re.escape(prefix)}_split-(\d+){re.escape(suffix)}$",
            flags=re.IGNORECASE,
        )
        for sibling in source.parent.iterdir():
            match = pattern.match(sibling.stem) if sibling.suffix.lower() == ".fif" else None
            if match:
                if sibling.is_symlink():
                    raise ValueError("FIF split member cannot be a symlink.")
                _ensure_regular_file(sibling, label="FIF split member")
                candidates.append((sibling, int(match.group(1)), "fif_split_member"))
        indices = sorted(index for _, index, _ in candidates if index is not None)
        if not indices or indices != list(range(1, max(indices) + 1)):
            refusals.append("fif_bids_split_indices_not_contiguous_from_1")
        split_status = "bids_split_filename_family"
    else:
        prefix = standard_match.group("prefix") if standard_match else selected_stem
        continuation_pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
        primary: Path | None = None
        for sibling in source.parent.iterdir():
            if sibling.suffix.lower() != ".fif":
                continue
            role: str | None = None
            index: int | None = None
            if sibling.stem == prefix:
                role = "fif_primary"
                primary = sibling
            else:
                match = continuation_pattern.match(sibling.stem)
                if match:
                    role = "fif_split_continuation"
                    index = int(match.group(1))
            if role:
                if sibling.is_symlink():
                    raise ValueError("FIF split member cannot be a symlink.")
                _ensure_regular_file(sibling, label="FIF split member")
                candidates.append((sibling, index, role))
        continuation_indices = sorted(
            index for _, index, _ in candidates if index is not None
        )
        if continuation_indices and continuation_indices != list(
            range(1, max(continuation_indices) + 1)
        ):
            refusals.append("fif_split_continuation_indices_not_contiguous_from_1")
        if standard_match and primary is None:
            refusals.append("fif_split_primary_missing")
        split_status = (
            "standard_split_filename_family"
            if continuation_indices or standard_match
            else "single_file_no_split_detected"
        )
    if not candidates:
        candidates = [(source, None, "fif_primary")]
    rows = [
        _file_row(path, root=root, role=role)
        for path, _, role in sorted(candidates, key=lambda row: row[0].name)
    ]
    return {
        "format_family": "fif",
        "raw_family": "fif",
        "files": rows,
        "companions": [],
        "metadata": {
            **_empty_metadata(),
            "format_metadata": {"split_status": split_status},
        },
        "identity": _empty_identity(),
        "inferred_modality": None,
        "warnings": [
            "fif_binary_header_not_opened_at_metadata_only_level",
            "split_completeness_validated_from_filenames_only",
        ],
        "refusals": refusals,
        "unavailable_fields": [
            "channel_count",
            "channel_names",
            "sampling_rate_hz",
            "reference",
        ],
    }


def _inspect_bids_directory(
    source: Path,
    *,
    root: Path,
    tracker: _AccessTracker,
    limits: IntakeLimits,
    hash_text_metadata: bool,
) -> dict[str, Any]:
    if source.resolve(strict=True) != root:
        raise ValueError("A BIDS directory scan must use the selected directory as its root.")
    paths = _walk_bounded_directory(source, limits=limits)
    description = source / "dataset_description.json"
    if description not in paths:
        if not paths:
            raise ValueError("Cannot inspect an empty directory as a recording bundle.")
        return {
            "format_family": "directory_not_bids",
            "raw_family": None,
            "files": [
                _file_row(path, root=root, role="unrecognized_directory_file_not_read")
                for path in paths
            ],
            "companions": [],
            "metadata": _empty_metadata(),
            "identity": _empty_identity(),
            "inferred_modality": None,
            "warnings": ["directory_contents_not_read"],
            "refusals": ["bids_dataset_description_json_missing"],
            "unavailable_fields": [
                "channel_count",
                "channel_names",
                "sampling_rate_hz",
                "reference",
            ],
        }
    text, raw, encoding = _read_bounded_text(
        description,
        tracker=tracker,
        limits=limits,
        purpose="bids_dataset_description",
    )
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("BIDS dataset_description.json is malformed.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("BIDSVersion"), str):
        raise ValueError("BIDS dataset_description.json must declare BIDSVersion.")

    raw_candidates = [path for path in paths if path.suffix.lower() in _RAW_CANDIDATE_SUFFIXES]
    rows = [
        _file_row(
            path,
            root=root,
            role=_bids_file_role(path),
            content_read=path == description,
            content_sha256=(
                _sha256_bytes(raw)
                if path == description and hash_text_metadata
                else None
            ),
        )
        for path in paths
    ]
    warnings = [
        "bids_dataset_name_omitted_for_privacy",
        "bids_sidecars_except_dataset_description_not_read",
    ]
    if any(
        path.name == "participants.tsv" or path.name.endswith("_events.tsv")
        for path in paths
    ):
        warnings.append("bids_participant_or_event_content_present_but_not_read")
    refusals: list[str] = []
    metadata = _empty_metadata()
    metadata["format_metadata"] = {
        "bids_version": payload["BIDSVersion"],
        "dataset_type": payload.get("DatasetType"),
        "dataset_description_encoding": encoding,
        "recording_candidate_count": len(raw_candidates),
    }
    identity = _empty_identity()
    inferred_modality = None
    raw_family = None
    companions: list[dict[str, Any]] = []
    unavailable_fields = [
        "channel_count",
        "channel_names",
        "sampling_rate_hz",
        "reference",
    ]
    if not raw_candidates:
        refusals.append("bids_no_supported_recording_candidate")
    elif len(raw_candidates) > 1:
        warnings.append("bids_multiple_recordings_require_explicit_file_selection")
    else:
        selected = raw_candidates[0]
        subinspection = _inspect_single_file(
            selected,
            root=root,
            tracker=tracker,
            limits=limits,
            hash_text_metadata=hash_text_metadata,
        )
        overlay = {row["path"]: row for row in subinspection["files"]}
        rows = [overlay.get(row["path"], row) for row in rows]
        metadata.update(subinspection["metadata"])
        metadata["format_metadata"] = {
            **metadata.get("format_metadata", {}),
            "bids_version": payload["BIDSVersion"],
            "dataset_type": payload.get("DatasetType"),
            "dataset_description_encoding": encoding,
            "recording_candidate_count": 1,
            "selected_raw_family": subinspection["format_family"],
        }
        companions = subinspection.get("companions", [])
        warnings.extend(subinspection["warnings"])
        refusals.extend(subinspection["refusals"])
        unavailable_fields.extend(subinspection.get("unavailable_fields", []))
        identity = _bids_identity(selected.relative_to(root).as_posix())
        inferred_modality = _bids_modality(selected.name)
        raw_family = subinspection["format_family"]
    return {
        "format_family": "bids",
        "raw_family": raw_family,
        "files": rows,
        "companions": companions,
        "metadata": metadata,
        "identity": identity,
        "inferred_modality": inferred_modality,
        "warnings": warnings,
        "refusals": refusals,
        "unavailable_fields": sorted(set(unavailable_fields)),
    }


def _inspect_registry(
    registry_path: str | Path | None,
    *,
    tracker: _AccessTracker,
    limits: IntakeLimits,
) -> dict[str, Any]:
    if registry_path is None:
        return {
            "bound": False,
            "schema_name": None,
            "schema_version": None,
            "record_count": None,
            "bytes_read": 0,
            "sha256": None,
            "status": "unavailable_no_registry_supplied",
        }
    path = Path(registry_path).expanduser()
    _ensure_regular_file(path, label="dataset registry")
    text, raw, _ = _read_bounded_text(
        path,
        tracker=tracker,
        limits=limits,
        purpose="dataset_registry",
    )
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Dataset registry JSON is malformed.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Dataset registry must be a JSON object.")
    schema_name = payload.get("schema_name")
    schema_version = payload.get("schema_version")
    records = payload.get("records")
    if not isinstance(schema_name, str) or not isinstance(schema_version, str):
        raise ValueError("Dataset registry must declare schema_name and schema_version.")
    if not isinstance(records, list):
        raise ValueError("Dataset registry records must be a list.")
    return {
        "bound": True,
        "schema_name": schema_name,
        "schema_version": schema_version,
        "record_count": len(records),
        "bytes_read": len(raw),
        "sha256": _sha256_bytes(raw),
        "status": "metadata_registry_hash_bound_no_task_match_performed",
    }


def _compatibility_report(
    *,
    level_zero_passed: bool,
    level_zero_refusals: list[str],
) -> dict[str, Any]:
    levels = [
        {
            "level": 0,
            "name": "metadata_recognized",
            "passed": level_zero_passed,
            "refusal_reason": (
                None
                if level_zero_passed
                else "; ".join(sorted(set(level_zero_refusals)))
            ),
        },
        {
            "level": 1,
            "name": "signal_readable",
            "passed": False,
            "refusal_reason": "binary_signal_read_not_authorized_in_rw1",
        },
        {
            "level": 2,
            "name": "channels_timing_events_validated",
            "passed": False,
            "refusal_reason": "bounded_signal_and_event_adapter_not_run",
        },
        {
            "level": 3,
            "name": "registered_task_compatible",
            "passed": False,
            "refusal_reason": "task_registry_match_not_performed",
        },
        {
            "level": 4,
            "name": "model_geometry_preprocessing_compatible",
            "passed": False,
            "refusal_reason": "model_and_preprocessing_contract_not_supplied",
        },
        {
            "level": 5,
            "name": "benchmark_authorized",
            "passed": False,
            "refusal_reason": "split_protocol_and_explicit_benchmark_approval_unavailable",
        },
        {
            "level": 6,
            "name": "live_source_qualified",
            "passed": False,
            "refusal_reason": "recorded_live_equivalence_not_tested",
        },
    ]
    return {
        "current_level": 0 if level_zero_passed else -1,
        "maximum_authorized_level": 0,
        "levels": levels,
    }


def _resolve_source_and_root(
    source_path: str | Path,
    *,
    root_path: str | Path | None,
) -> tuple[Path, Path]:
    source = Path(source_path).expanduser()
    if source.is_symlink():
        raise ValueError("Selected source cannot be a symlink.")
    if not source.exists():
        raise FileNotFoundError(f"Selected source does not exist: {source}")
    source_resolved = source.resolve(strict=True)
    source_stat = source_resolved.stat()
    if not (stat.S_ISREG(source_stat.st_mode) or stat.S_ISDIR(source_stat.st_mode)):
        raise ValueError("Selected source must be a regular file or directory.")
    if root_path is None:
        root = source_resolved if source_resolved.is_dir() else source_resolved.parent
    else:
        requested_root = Path(root_path).expanduser()
        if requested_root.is_symlink():
            raise ValueError("Selected root cannot be a symlink.")
        if not requested_root.is_dir():
            raise NotADirectoryError(f"Selected root is not a directory: {requested_root}")
        root = requested_root.resolve(strict=True)
    try:
        source_resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Selected source escapes the declared root.") from exc
    return source_resolved, root


def _walk_bounded_directory(root: Path, *, limits: IntakeLimits) -> list[Path]:
    files: list[Path] = []
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        entries = sorted(directory.iterdir(), key=lambda path: path.name.casefold())
        for entry in entries:
            if entry.is_symlink():
                raise ValueError(
                    f"BIDS metadata scan refuses symlinks: {_relative_path_non_strict(entry, root)}"
                )
            entry_stat = entry.stat()
            if stat.S_ISDIR(entry_stat.st_mode):
                next_depth = depth + 1
                if next_depth > limits.max_depth:
                    raise ValueError(
                        f"Directory depth exceeds cap {limits.max_depth}: "
                        f"{_relative_path_non_strict(entry, root)}"
                    )
                stack.append((entry, next_depth))
            elif stat.S_ISREG(entry_stat.st_mode):
                files.append(entry.resolve(strict=True))
                if len(files) > limits.max_files:
                    raise ValueError(
                        f"Directory file count exceeds cap {limits.max_files}."
                    )
            else:
                raise ValueError(
                    "Metadata scan refuses special filesystem nodes: "
                    f"{_relative_path_non_strict(entry, root)}"
                )
    files.sort(key=lambda path: _relative_path(path, root))
    declared = sum(path.stat().st_size for path in files)
    if declared > limits.max_declared_input_bytes:
        raise ValueError(
            "Declared input bytes exceed cap: "
            f"{declared} > {limits.max_declared_input_bytes}."
        )
    return files


def _read_bounded_text(
    path: Path,
    *,
    tracker: _AccessTracker,
    limits: IntakeLimits,
    purpose: str,
) -> tuple[str, bytes, str]:
    _ensure_regular_file(path, label=purpose)
    size = path.stat().st_size
    if size > limits.max_text_file_bytes:
        raise ValueError(
            f"Text metadata file exceeds per-file cap: {size} > {limits.max_text_file_bytes}."
        )
    if tracker.metadata_text_bytes_read + size > limits.max_text_total_bytes:
        raise ValueError(
            "Text metadata reads exceed total cap: "
            f"{tracker.metadata_text_bytes_read + size} > {limits.max_text_total_bytes}."
        )
    with path.open("rb") as handle:
        raw = handle.read(size + 1)
    if len(raw) != size:
        raise ValueError(f"Metadata file changed during scan: {path.name}")
    if b"\x00" in raw:
        raise ValueError(f"Text metadata contains NUL bytes: {path.name}")
    tracker.metadata_files_read += 1
    tracker.metadata_text_bytes_read += len(raw)
    try:
        return raw.decode("utf-8-sig"), raw, "utf-8"
    except UnicodeDecodeError:
        return raw.decode("latin-1"), raw, "latin-1"


def _parse_brainvision_header(text: str) -> dict[str, Any]:
    section = ""
    keys: dict[str, list[str]] = {}
    channel_names: list[str] = []
    units: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().casefold()
            continue
        key, separator, value = line.partition("=")
        if not separator:
            continue
        normalized_key = key.strip().casefold()
        cleaned_value = value.strip()
        keys.setdefault(normalized_key, []).append(cleaned_value)
        if section == "channel infos" and re.fullmatch(r"ch\d+", normalized_key):
            fields = [field.strip() for field in cleaned_value.split(",")]
            if fields and fields[0] and len(channel_names) < 4096:
                channel_names.append(fields[0][:128])
            if len(fields) >= 4 and fields[3] and len(units) < 4096:
                units.append(fields[3][:64])
    single = {key: values[0] for key, values in keys.items() if len(values) == 1}
    return {
        "keys": keys,
        "single": single,
        "channel_names": channel_names,
        "units": units,
    }


def _resolve_companion_path(
    header: Path,
    declared_value: str,
    *,
    root: Path,
    expected_suffix: str,
) -> Path:
    normalized = declared_value.strip().strip('"').strip("'").replace("\\", "/")
    if not normalized or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError("companion path must be a nonempty relative path")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError("companion path cannot be absolute or contain traversal")
    if pure.suffix.lower() != expected_suffix:
        raise ValueError(f"companion must use {expected_suffix} extension")
    candidate = header.parent.joinpath(*pure.parts)
    parent = candidate.parent.resolve(strict=True)
    try:
        parent.relative_to(root)
    except ValueError as exc:
        raise ValueError("companion path escapes selected root") from exc
    if candidate.is_symlink():
        raise ValueError("companion cannot be a symlink")
    if candidate.exists():
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("companion resolves outside selected root") from exc
        return resolved
    return candidate


def _file_row(
    path: Path,
    *,
    root: Path,
    role: str,
    content_read: bool = False,
    content_sha256: str | None = None,
) -> dict[str, Any]:
    _ensure_regular_file(path, label=role)
    return {
        "path": _relative_path(path, root),
        "role": role,
        "size_bytes": int(path.stat().st_size),
        "content_read": bool(content_read),
        "content_sha256": content_sha256,
    }


def _validate_file_rows(files: list[dict[str, Any]], *, limits: IntakeLimits) -> None:
    if len(files) > limits.max_files:
        raise ValueError(f"Source file count exceeds cap {limits.max_files}.")
    seen_paths: set[str] = set()
    seen_roles: set[tuple[str, str]] = set()
    for row in files:
        if not isinstance(row, dict):
            raise ValueError("Source file rows must be objects.")
        path = row.get("path")
        role = row.get("role")
        size = row.get("size_bytes")
        _validate_relative_report_path(path)
        if path in seen_paths:
            raise ValueError(f"Duplicate source path in report: {path}")
        seen_paths.add(path)
        if not isinstance(role, str) or not role:
            raise ValueError("Every source file needs a role.")
        role_pair = (path, role)
        if role_pair in seen_roles:
            raise ValueError(f"Duplicate source role in report: {path} / {role}")
        seen_roles.add(role_pair)
        if not isinstance(size, int) or size < 0:
            raise ValueError(f"Invalid source file size for {path}.")
        if row.get("content_read") not in {True, False}:
            raise ValueError(f"Invalid content_read flag for {path}.")
        content_hash = row.get("content_sha256")
        if content_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", content_hash):
            raise ValueError(f"Invalid content hash for {path}.")
    declared = sum(int(row["size_bytes"]) for row in files)
    if declared > limits.max_declared_input_bytes:
        raise ValueError(
            f"Declared input bytes exceed cap: {declared} > {limits.max_declared_input_bytes}."
        )
    if files != sorted(files, key=lambda row: row["path"]):
        raise ValueError("Source file rows must be sorted by relative path.")


def _validate_output_directory(path: Path, *, overwrite: bool) -> None:
    if path.is_symlink():
        raise ValueError("Output directory cannot be a symlink.")
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to write into nonempty output directory: {path}")
    if path.exists():
        for name in (ARTIFACT_JSON, ARTIFACT_MARKDOWN, ARTIFACT_AUDIT):
            candidate = path / name
            if candidate.is_symlink():
                raise ValueError(f"Output artifact cannot be a symlink: {name}")
            if candidate.exists() and not candidate.is_file():
                raise ValueError(f"Output artifact path is not a regular file: {name}")


def _write_artifact(path: Path, payload: bytes, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to replace output artifact: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists():
        raise FileExistsError(f"Temporary output path already exists: {temporary.name}")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _validate_intake_audit(
    audit: dict[str, Any],
    *,
    report_file: Path,
    report_bytes: bytes,
    audit_file: Path,
    audit_bytes: bytes,
) -> None:
    if audit.get("schema") != {"name": AUDIT_SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported intake audit schema.")
    artifacts = audit.get("artifacts")
    resources = audit.get("resources")
    if not isinstance(artifacts, dict) or not isinstance(resources, dict):
        raise ValueError("Intake audit is missing artifact or resource metadata.")
    report_row = artifacts.get(ARTIFACT_JSON, {})
    if report_row.get("bytes") != len(report_bytes):
        raise ValueError("Intake JSON byte count mismatch.")
    if report_row.get("sha256") != _sha256_bytes(report_bytes):
        raise ValueError("Intake JSON artifact hash mismatch.")
    audit_row = artifacts.get(ARTIFACT_AUDIT, {})
    if audit_row.get("bytes") != len(audit_bytes):
        raise ValueError("Intake audit byte count mismatch.")
    markdown_file = report_file.with_name(ARTIFACT_MARKDOWN)
    if not markdown_file.is_file() or markdown_file.is_symlink():
        raise ValueError("Intake Markdown artifact is missing or unsafe.")
    markdown_bytes = markdown_file.read_bytes()
    markdown_row = artifacts.get(ARTIFACT_MARKDOWN, {})
    if markdown_row.get("bytes") != len(markdown_bytes):
        raise ValueError("Intake Markdown byte count mismatch.")
    if markdown_row.get("sha256") != _sha256_bytes(markdown_bytes):
        raise ValueError("Intake Markdown artifact hash mismatch.")
    total = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
    if resources.get("total_output_bytes") != total:
        raise ValueError("Intake total output byte count mismatch.")
    if total > int(resources.get("max_output_bytes", -1)):
        raise ValueError("Intake artifacts exceed their declared output cap.")
    if resources.get("output_cap_passed") is not True:
        raise ValueError("Intake audit does not record a passing output cap.")
    if audit_file.name != ARTIFACT_AUDIT:
        raise ValueError("Audit sidecar must use the registered filename.")


def _safe_report_file(path: str | Path, *, max_bytes: int) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("Report files cannot be symlinks.")
    _ensure_regular_file(candidate, label="intake report")
    if candidate.stat().st_size > max_bytes:
        raise ValueError("Intake report exceeds the inspection byte cap.")
    return candidate


def _ensure_regular_file(path: Path, *, label: str) -> None:
    if path.is_symlink():
        raise ValueError(f"{label} cannot be a symlink.")
    if not path.exists():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError(f"{label} must be a regular file.")


def _disallowed_input_refusal(path: Path) -> tuple[str, str] | None:
    lowered = path.name.casefold()
    if lowered.endswith(_ARCHIVE_SUFFIXES):
        return "archive", "archives_are_not_recording_formats"
    if lowered.endswith(_PICKLE_SUFFIXES):
        return "pickle_or_object_payload", "pickle_and_object_numpy_payloads_are_refused"
    if lowered.endswith(_EXECUTABLE_SUFFIXES):
        return "executable", "executable_files_are_refused_as_recording_inputs"
    return None


def _relative_path(path: Path, root: Path) -> str:
    resolved = path.resolve(strict=True)
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Resolved source path escapes selected root.") from exc
    return relative.as_posix() or "."


def _relative_path_non_strict(path: Path, root: Path) -> str:
    try:
        return path.absolute().relative_to(root).as_posix() or "."
    except ValueError:
        return path.name


def _validate_relative_report_path(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError("Report paths must be nonempty relative strings.")
    if value == ".":
        return
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"Unsafe path in intake report: {value}")
    if re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"Drive-qualified path in intake report: {value}")


def _bids_file_role(path: Path) -> str:
    name = path.name
    if name == "dataset_description.json":
        return "bids_dataset_description"
    if path.suffix.lower() in _RAW_CANDIDATE_SUFFIXES:
        return "bids_recording_candidate"
    if name.endswith("_events.tsv"):
        return "bids_events_sidecar_not_read"
    if name == "participants.tsv":
        return "bids_participants_sidecar_not_read"
    if name.endswith("_channels.tsv"):
        return "bids_channels_sidecar_not_read"
    if path.suffix.lower() in {".json", ".tsv"}:
        return "bids_metadata_sidecar_not_read"
    return "bids_other_file_not_read"


def _bids_identity(relative_path: str) -> dict[str, Any]:
    def match_value(prefix: str) -> str | None:
        match = re.search(rf"(?:^|[/_]){prefix}-([A-Za-z0-9]+)", relative_path)
        return match.group(1) if match else None

    values = {
        "subject_id": match_value("sub"),
        "session_id": match_value("ses"),
        "task_id": match_value("task"),
        "run_id": match_value("run"),
    }
    values["identity_source"] = (
        "bids_relative_filename" if any(values.values()) else "unavailable"
    )
    return values


def _bids_modality(name: str) -> str | None:
    lowered = name.casefold()
    if "_eeg." in lowered or lowered.endswith("_eeg.fif"):
        return "EEG"
    if "_meg." in lowered or lowered.endswith("_meg.fif"):
        return "MEG"
    if "_ieeg." in lowered:
        return "iEEG"
    return None


def _empty_metadata() -> dict[str, Any]:
    return {
        "channel_count": None,
        "channel_names": [],
        "channel_types": [],
        "sampling_rate_hz": None,
        "reference": None,
        "source_filters": None,
        "units": [],
        "format_metadata": {},
    }


def _empty_identity() -> dict[str, Any]:
    return {
        "subject_id": None,
        "session_id": None,
        "task_id": None,
        "run_id": None,
        "identity_source": "unavailable",
    }


def _clean_optional_label(value: str | None, *, field: str) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError(f"{field} cannot be empty when supplied.")
    if len(cleaned) > 128 or any(ord(character) < 32 for character in cleaned):
        raise ValueError(f"{field} contains invalid characters or exceeds 128 characters.")
    return cleaned


def _parse_positive_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if 0 < parsed <= 4096 else None


def _parse_positive_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _report_payload_sha256(report: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(report, ensure_ascii=True))
    hashes = payload.get("hashes")
    if isinstance(hashes, dict):
        hashes["report_payload_sha256"] = None
    return _sha256_json(payload)


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode(
        "utf-8"
    )


def _all_mapping_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_all_mapping_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_all_mapping_keys(child))
    return keys


def _markdown_value(value: Any) -> str:
    return "unavailable" if value is None else str(value).replace("`", "'")


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, OSError, ValueError):  # pragma: no cover - platform-dependent
        return None
    return value if sys.platform == "darwin" else value * 1024
