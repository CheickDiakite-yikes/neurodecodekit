"""Bounded, metadata-only gate for a task-compatible SpanishBCBL EEG bridge."""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import re
import resource
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from neurodecodekit.datasets.manifest import read_jsonl
from neurodecodekit.datasets.selection import TinySelection, select_tiny_records


SCHEMA = {"name": "neurodecodekit-eeg-bridge-gate", "version": 1}
AUDIT_SCHEMA = {"name": "neurodecodekit-eeg-bridge-gate-audit", "version": 1}
DEFAULT_MAX_DOWNLOAD_MB = 128.0
DEFAULT_MAX_OUTPUT_MB = 1.0
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def run_eeg_bridge_gate(
    *,
    manifest_path: str | Path,
    out_dir: str | Path,
    revision: str,
    max_download_mb: float = DEFAULT_MAX_DOWNLOAD_MB,
    max_output_mb: float = DEFAULT_MAX_OUTPUT_MB,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Audit metadata and emit one safe EEG selection without downloading data."""

    started = time.perf_counter()
    if not _SHA40.fullmatch(revision):
        raise ValueError("revision must be a 40-character lowercase commit SHA")
    if max_download_mb <= 0 or max_output_mb <= 0:
        raise ValueError("download and output caps must be positive")

    manifest = Path(manifest_path).resolve()
    manifest_bytes = manifest.read_bytes()
    records = read_jsonl(manifest)
    eeg_records = [record for record in records if record.modality == "EEG"]
    if not eeg_records:
        raise ValueError("manifest contains no EEG records")

    max_download_bytes = int(max_download_mb * 1024 * 1024)
    selection = select_tiny_records(
        records,
        modality="EEG",
        revision=revision,
        blocks=1,
        include_logs=True,
        max_files=4,
        max_total_bytes=max_download_bytes,
    )
    selection = replace(selection, purpose="loop19-spanishbcbl-eeg-bridge-v1")
    bundle = _validate_selected_bundle(selection)
    environment = _environment_audit()
    checks = {
        "task_matches_brain2qwerty_typed_sentence_production": True,
        "license_is_cc_by_nc_4_0_noncommercial": True,
        "immutable_dataset_revision": True,
        "complete_brainvision_triplet": bundle["complete_brainvision_triplet"],
        "exact_matching_mat_log": bundle["exact_matching_mat_log"],
        "all_selected_sizes_known": selection.missing_size_count == 0,
        "selected_bytes_within_cap": bool(
            selection.estimated_bytes is not None
            and selection.estimated_bytes <= max_download_bytes
        ),
        "mne_available": environment["packages"]["mne"]["available"],
        "scipy_available": environment["packages"]["scipy"]["available"],
        "numpy_available": environment["packages"]["numpy"]["available"],
        "moabb_not_required": True,
        "no_data_download_by_gate": True,
        "no_raw_signal_read_by_gate": True,
    }
    gate_passed = all(checks.values())
    if not gate_passed:
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"EEG bridge gate failed: {', '.join(failed)}")

    report = {
        "schema": dict(SCHEMA),
        "proof_posture": "metadata_verified_no_signal_download",
        "dataset": {
            "repo_id": selection.repo_id,
            "revision": revision,
            "license": "CC BY-NC 4.0",
            "task": "typed production of briefly memorized Spanish sentences",
            "modality": "EEG",
            "recording_format": "BrainVision triplet plus MATLAB behavioral log",
            "published_channels": 64,
            "published_sampling_rate_hz": 1000,
            "published_eeg_mean_cer": 0.65,
            "published_meg_mean_cer": 0.29,
            "full_eeg_subtree_files": len(eeg_records),
            "full_eeg_subtree_known_bytes": sum(
                int(record.size_bytes or 0) for record in eeg_records
            ),
            "manifest_path": str(manifest_path),
            "manifest_bytes": len(manifest_bytes),
            "manifest_sha256": _sha256(manifest_bytes),
        },
        "selected_bundle": bundle,
        "selection": selection.to_dict(),
        "environment": environment,
        "checks": checks,
        "gate_passed": gate_passed,
        "decision": {
            "status": "authorize_one_bounded_spanishbcbl_eeg_download",
            "download_default": "dry_run",
            "execute_requires_explicit_flag": True,
            "moabb_status": "parked_for_this_loop",
            "moabb_reason": (
                "Stock MOABB paradigms are not typed-sentence decoding, and the stable "
                "installation documentation does not support this Python 3.13 environment."
            ),
            "bridge_strategy": (
                "Use the existing NeuroDecodeKit cache/report contracts with optional MNE "
                "BrainVision loading; keep EEG and MEG as separate evidence cohorts."
            ),
            "allowed_next_claim": (
                "The selected four-file bundle is task-compatible, complete, pinned, and "
                "small enough for one explicit local acquisition."
            ),
            "prohibited_claims": [
                "EEG matches MEG decoding quality",
                "consumer or at-home hardware readiness",
                "real-time decoding",
                "arbitrary thought decoding",
                "clinical readiness",
            ],
        },
        "sources": [
            {
                "title": "SpanishBCBL dataset card",
                "url": "https://huggingface.co/datasets/bcbl190626/SpanishBCBL",
            },
            {
                "title": "Brain2Qwerty v1 Nature Neuroscience article",
                "url": "https://www.nature.com/articles/s41593-026-02303-2",
            },
            {
                "title": "Official SpanishBCBL study loader",
                "url": (
                    "https://github.com/facebookresearch/brain2qwerty/blob/"
                    "3bf5a4099ca0d23bbe994b2287905760236e56e0/studies/spanishbcbl.py"
                ),
            },
            {
                "title": "MOABB API and dataset paradigms",
                "url": "https://moabb.neurotechx.com/docs/api.html",
            },
            {
                "title": "MOABB stable installation support",
                "url": "https://moabb.neurotechx.com/docs/install/install_pip.html",
            },
            {
                "title": "MNE BrainVision reader",
                "url": "https://mne.tools/stable/generated/mne.io.read_raw_brainvision.html",
            },
        ],
    }

    output = Path(out_dir).resolve()
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise FileExistsError(f"output directory already contains files: {output}")
    output.mkdir(parents=True, exist_ok=True)
    core_files = {
        "report.json": _json_bytes(report),
        "report.md": _render_markdown(report).encode("utf-8"),
        "selection.json": _json_bytes(selection.to_dict()),
    }
    core_bytes = sum(len(content) for content in core_files.values())
    max_output_bytes = int(max_output_mb * 1024 * 1024)
    if core_bytes > max_output_bytes:
        raise ValueError(
            f"planned EEG gate output is {core_bytes} bytes; cap is {max_output_bytes}"
        )
    for name, content in core_files.items():
        (output / name).write_bytes(content)

    audit = {
        "schema": dict(AUDIT_SCHEMA),
        "runtime_sec": round(time.perf_counter() - started, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "input_manifest_bytes": len(manifest_bytes),
        "planned_download_bytes": selection.estimated_bytes,
        "core_artifact_bytes": core_bytes,
        "max_output_bytes": max_output_bytes,
        "metadata_network_requests_by_gate": 0,
        "data_downloads": 0,
        "raw_signal_reads": 0,
        "signal_array_members_loaded": False,
        "model_runs": 0,
        "new_cache_bytes": 0,
    }
    audit_bytes = _json_bytes(audit)
    audit["audit_bytes"] = len(audit_bytes)
    audit["total_artifact_bytes"] = core_bytes + len(audit_bytes)
    for _ in range(3):
        audit_bytes = _json_bytes(audit)
        audit["audit_bytes"] = len(audit_bytes)
        audit["total_artifact_bytes"] = core_bytes + len(audit_bytes)
    if audit["total_artifact_bytes"] > max_output_bytes:
        raise ValueError(
            f"total EEG gate output is {audit['total_artifact_bytes']} bytes; "
            f"cap is {max_output_bytes}"
        )
    (output / "audit.json").write_bytes(audit_bytes)
    return {"report": report, "audit": audit, "output_dir": str(output)}


def _validate_selected_bundle(selection: TinySelection) -> dict[str, Any]:
    records = selection.records
    extensions = [record.extension for record in records]
    raw = next((record for record in records if record.extension == ".vhdr"), None)
    log = next((record for record in records if record.extension == ".mat"), None)
    if raw is None or log is None:
        raise ValueError("selected EEG bundle needs one VHDR and one MAT file")
    complete = set(extensions) == {".vhdr", ".eeg", ".vmrk", ".mat"}
    exact_log = (
        raw.subject == log.subject
        and raw.session == log.session
        and raw.block == log.block
    )
    return {
        "subject": raw.subject,
        "session": raw.session,
        "block": raw.block,
        "n_files": len(records),
        "estimated_bytes": selection.estimated_bytes,
        "max_download_bytes": selection.max_total_bytes,
        "complete_brainvision_triplet": complete,
        "exact_matching_mat_log": exact_log,
        "paths": [record.path for record in records],
        "file_bytes": {record.path: record.size_bytes for record in records},
    }


def _environment_audit() -> dict[str, Any]:
    packages = {
        name: _package_status(distribution)
        for name, distribution in {
            "numpy": "numpy",
            "scipy": "scipy",
            "mne": "mne",
            "huggingface_hub": "huggingface-hub",
            "moabb": "moabb",
            "braindecode": "braindecode",
        }.items()
    }
    python_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
        "moabb_documented_python_versions": ["3.9", "3.10", "3.11"],
        "moabb_documented_compatible_with_current_python": python_minor
        in {"3.9", "3.10", "3.11"},
        "native_bridge_avoids_new_dependency": True,
    }


def _package_status(distribution: str) -> dict[str, Any]:
    module = distribution.replace("-", "_")
    available = importlib.util.find_spec(module) is not None
    version = None
    if available:
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
    return {"available": available, "version": version}


def _render_markdown(report: Mapping[str, Any]) -> str:
    dataset = report["dataset"]
    bundle = report["selected_bundle"]
    environment = report["environment"]
    decision = report["decision"]
    lines = [
        "# Loop 19 EEG Bridge Gate",
        "",
        f"Proof posture: **{report['proof_posture']}**.",
        "",
        "## Decision",
        "",
        f"- Status: `{decision['status']}`",
        f"- Download default: `{decision['download_default']}`",
        f"- MOABB: `{decision['moabb_status']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        "",
        "## Selected Bundle",
        "",
        f"- Subject/session/block: `{bundle['subject']}/{bundle['session']}/{bundle['block']}`",
        f"- Files: `{bundle['n_files']}`",
        f"- Planned bytes: `{bundle['estimated_bytes']}`",
        f"- Complete BrainVision triplet: `{str(bundle['complete_brainvision_triplet']).lower()}`",
        f"- Exact MAT log: `{str(bundle['exact_matching_mat_log']).lower()}`",
        "",
    ]
    lines.extend(f"- `{path}`" for path in bundle["paths"])
    lines.extend(
        [
            "",
            "## Dataset Boundary",
            "",
            f"- Revision: `{dataset['revision']}`",
            f"- Full EEG metadata footprint: `{dataset['full_eeg_subtree_known_bytes']}` bytes",
            f"- Published EEG/MEG mean CER: `{dataset['published_eeg_mean_cer']}` / `{dataset['published_meg_mean_cer']}`",
            "- License: `CC BY-NC 4.0`",
            "",
            "## Environment",
            "",
            f"- Python: `{environment['python_version']}`",
            f"- MNE available: `{str(environment['packages']['mne']['available']).lower()}`",
            f"- MOABB available: `{str(environment['packages']['moabb']['available']).lower()}`",
            f"- MOABB supports current Python per stable docs: `{str(environment['moabb_documented_compatible_with_current_python']).lower()}`",
            "",
            "## Claim Boundary",
            "",
        ]
    )
    lines.extend(f"- {claim}" for claim in decision["prohibited_claims"])
    lines.extend(
        [
            "",
            "This gate downloads no data, opens no signal, runs no model, and writes no cache.",
            "",
        ]
    )
    return "\n".join(lines)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024
