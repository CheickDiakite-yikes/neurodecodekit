"""Zero-network capability audit for optional local EEG tooling."""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCHEMA_NAME = "neurodecodekit.local_eeg_tooling_audit"
SCHEMA_VERSION = "0.1.0"
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_OUTPUT_BYTES = 1024 * 1024
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


@dataclass(frozen=True)
class CapabilitySpec:
    module: str
    attribute: str


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    distribution: str | None
    module: str
    role: str
    capabilities: tuple[CapabilitySpec, ...]


DEFAULT_TOOL_SPECS = (
    ToolSpec(
        tool_id="numpy",
        distribution="numpy",
        module="numpy",
        role="bounded arrays and deterministic numerical plumbing",
        capabilities=(
            CapabilitySpec("numpy", "ndarray"),
            CapabilitySpec("numpy", "asarray"),
        ),
    ),
    ToolSpec(
        tool_id="scipy",
        distribution="scipy",
        module="scipy",
        role="signal processing and linear algebra",
        capabilities=(
            CapabilitySpec("scipy.signal", "butter"),
            CapabilitySpec("scipy.linalg", "eigh"),
        ),
    ),
    ToolSpec(
        tool_id="scikit_learn",
        distribution="scikit-learn",
        module="sklearn",
        role="grouped classical estimators and shrinkage baselines",
        capabilities=(
            CapabilitySpec("sklearn.discriminant_analysis", "LinearDiscriminantAnalysis"),
            CapabilitySpec("sklearn.covariance", "LedoitWolf"),
            CapabilitySpec("sklearn.pipeline", "Pipeline"),
        ),
    ),
    ToolSpec(
        tool_id="mne",
        distribution="mne",
        module="mne",
        role="EEG metadata, BrainVision reading, quality, and CSP substrate",
        capabilities=(
            CapabilitySpec("mne.io", "read_raw_brainvision"),
            CapabilitySpec("mne.decoding", "CSP"),
            CapabilitySpec("mne.preprocessing", "ICA"),
        ),
    ),
    ToolSpec(
        tool_id="pyriemann",
        distribution="pyriemann",
        module="pyriemann",
        role="covariance, MDM, and tangent-space low-data baselines",
        capabilities=(
            CapabilitySpec("pyriemann.estimation", "Covariances"),
            CapabilitySpec("pyriemann.classification", "MDM"),
            CapabilitySpec("pyriemann.tangentspace", "TangentSpace"),
        ),
    ),
    ToolSpec(
        tool_id="moabb",
        distribution="moabb",
        module="moabb",
        role="public EEG datasets and grouped benchmark protocols",
        capabilities=(
            CapabilitySpec("moabb.datasets", "PhysionetMI"),
            CapabilitySpec("moabb.paradigms", "MotorImagery"),
            CapabilitySpec("moabb.evaluations", "CrossSubjectEvaluation"),
        ),
    ),
    ToolSpec(
        tool_id="braindecode",
        distribution="braindecode",
        module="braindecode",
        role="optional compact published EEG model adapters",
        capabilities=(
            CapabilitySpec("braindecode.models", "EEGNetv4"),
            CapabilitySpec("braindecode.models", "ShallowFBCSPNet"),
        ),
    ),
)


_PROBE_SCRIPT = r"""
import contextlib
import hashlib
import importlib
import io
import json
import resource
import socket
import sys
import time

network_attempts = 0


def blocked(*args, **kwargs):
    global network_attempts
    network_attempts += 1
    raise RuntimeError("network_disabled_by_neurodecodekit_audit")


class NoNetworkSocket(socket.socket):
    def connect(self, *args, **kwargs):
        return blocked(*args, **kwargs)

    def connect_ex(self, *args, **kwargs):
        return blocked(*args, **kwargs)


socket.socket = NoNetworkSocket
socket.create_connection = blocked
socket.getaddrinfo = blocked

module_name = sys.argv[1]
capabilities = json.loads(sys.argv[2])
captured = io.StringIO()
started = time.perf_counter()
available = []
missing = []
status = "import_ready"
error_type = None

try:
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        importlib.import_module(module_name)
        for module_path, attribute in capabilities:
            try:
                module = importlib.import_module(module_path)
                getattr(module, attribute)
                available.append(f"{module_path}.{attribute}")
            except (AttributeError, ImportError):
                missing.append(f"{module_path}.{attribute}")
        if missing:
            status = "import_ready_capability_incomplete"
except Exception as exc:
    status = "import_failed"
    error_type = type(exc).__name__

raw_peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
peak_rss_bytes = raw_peak if sys.platform == "darwin" else raw_peak * 1024
captured_bytes = captured.getvalue().encode("utf-8", errors="replace")
print(json.dumps({
    "status": status,
    "available_capabilities": available,
    "missing_capabilities": missing,
    "error_type": error_type,
    "runtime_seconds": round(time.perf_counter() - started, 9),
    "peak_rss_bytes": peak_rss_bytes,
    "blocked_network_attempts": network_attempts,
    "captured_output_bytes": len(captured_bytes),
    "captured_output_sha256": hashlib.sha256(captured_bytes).hexdigest(),
}, sort_keys=True))
"""


def audit_local_eeg_tooling(
    *,
    tool_specs: Sequence[ToolSpec] = DEFAULT_TOOL_SPECS,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Inspect optional EEG libraries without network, data, or model operations."""

    if not tool_specs:
        raise ValueError("tool_specs must not be empty")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if max_output_bytes <= 0:
        raise ValueError("max_output_bytes must be positive")
    tool_ids = [spec.tool_id for spec in tool_specs]
    if len(tool_ids) != len(set(tool_ids)):
        raise ValueError("tool_ids must be unique")

    optional_modules_before = {
        spec.module for spec in tool_specs if spec.module in sys.modules
    }
    started = time.perf_counter()
    tools = [
        _inspect_tool(spec, timeout_seconds=timeout_seconds)
        for spec in tool_specs
    ]
    optional_modules_after = {
        spec.module for spec in tool_specs if spec.module in sys.modules
    }
    installed = sum(row["distribution_installed"] for row in tools)
    available = sum(row["module_available"] for row in tools)
    import_ready = sum(row["probe_status"].startswith("import_ready") for row in tools)
    capability_complete = sum(row["probe_status"] == "import_ready" for row in tools)
    blocked_attempts = sum(row["blocked_network_attempts"] for row in tools)
    probed = sum(row["probe_executed"] for row in tools)
    missing_tools = [row["tool_id"] for row in tools if not row["module_available"]]
    failed_tools = [
        row["tool_id"]
        for row in tools
        if row["probe_status"] in {"import_failed", "timeout", "malformed_probe_output"}
    ]
    warnings = [f"optional_tool_not_installed:{name}" for name in missing_tools]
    warnings.extend(f"optional_tool_probe_failed:{name}" for name in failed_tools)
    for row in tools:
        if row["probe_status"] == "import_ready_capability_incomplete":
            warnings.append(
                "optional_tool_capability_incomplete:"
                f"{row['tool_id']}:{','.join(row['missing_capabilities'])}"
            )
        if row["captured_output_bytes"]:
            warnings.append(
                f"optional_tool_emitted_sanitized_output:{row['tool_id']}:"
                f"{row['captured_output_bytes']}_bytes"
            )

    report: dict[str, Any] = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "operation": "zero_network_local_eeg_tooling_audit",
        "environment": {
            "python_version": platform.python_version(),
            "platform_system": platform.system(),
            "platform_machine": platform.machine(),
            "worker_count": 1,
            "thread_environment": dict(THREAD_ENVIRONMENT),
            "base_process_optional_modules_present_before": sorted(
                optional_modules_before
            ),
            "base_process_optional_modules_present_after": sorted(
                optional_modules_after
            ),
            "base_process_imported_optional_tools": bool(
                optional_modules_after - optional_modules_before
            ),
        },
        "tools": tools,
        "summary": {
            "tool_count": len(tools),
            "installed_distribution_count": installed,
            "available_module_count": available,
            "isolated_probe_count": probed,
            "import_ready_count": import_ready,
            "capability_complete_count": capability_complete,
            "missing_tool_ids": missing_tools,
            "failed_tool_ids": failed_tools,
            "array_signal_core_ready": _ready(tools, "numpy") and _ready(tools, "scipy"),
            "brainvision_reader_ready": _capability_ready(
                tools, "mne", "mne.io.read_raw_brainvision"
            ),
            "ocular_ica_substrate_ready": _capability_ready(
                tools, "mne", "mne.preprocessing.ICA"
            ),
            "mne_csp_substrate_ready": _capability_ready(
                tools, "mne", "mne.decoding.CSP"
            ),
            "brainvision_quality_substrate_ready": (
                _capability_ready(tools, "mne", "mne.io.read_raw_brainvision")
                and _capability_ready(tools, "mne", "mne.preprocessing.ICA")
            ),
            "classical_ml_substrate_ready": _ready(tools, "scikit_learn"),
            "riemannian_substrate_ready": _ready(tools, "pyriemann"),
            "public_benchmark_harness_ready": _ready(tools, "moabb"),
            "compact_neural_adapter_ready": _ready(tools, "braindecode"),
        },
        "access_counters": {
            "distribution_metadata_reads": sum(
                spec.distribution is not None for spec in tool_specs
            ),
            "isolated_import_probes": probed,
            "blocked_network_attempts": blocked_attempts,
            "successful_network_operations": 0,
            "downloads": 0,
            "real_or_protected_data_reads": 0,
            "target_or_label_reads": 0,
            "raw_signal_reads": 0,
            "model_loads": 0,
            "training_runs": 0,
            "inference_runs": 0,
            "scoring_runs": 0,
            "provider_calls": 0,
            "device_or_hardware_operations": 0,
        },
        "resources": {
            "runtime_seconds": round(time.perf_counter() - started, 9),
            "peak_rss_bytes": _peak_rss_bytes(),
            "maximum_child_peak_rss_bytes": max(
                (row["peak_rss_bytes"] for row in tools),
                default=0,
            ),
            "timeout_seconds_per_probe": timeout_seconds,
            "maximum_output_bytes": max_output_bytes,
            "output_bytes": 0,
        },
        "warnings": warnings,
        "unavailable_fields": [
            "dataset_compatibility",
            "real_signal_quality",
            "runtime_model_accuracy",
            "neural_advantage",
            "device_compatibility",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "Installed optional EEG libraries and selected import surfaces are "
                "inspectable under isolated zero-network probes."
            ),
            "scientific_claim_not_established": (
                "Library availability establishes no data quality, neural signal, "
                "decoding accuracy, generalization, latency, device, or clinical result."
            ),
        },
    }
    _stabilize_output_bytes(report)
    validate_local_eeg_tooling_report(report)
    return report


def write_local_eeg_tooling_report(path: str | Path, report: dict[str, Any]) -> int:
    """Validate and atomically create one bounded JSON audit report."""

    validate_local_eeg_tooling_report(report)
    payload = _json_bytes(report)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(payload)
    return len(payload)


def validate_local_eeg_tooling_report(report: dict[str, Any]) -> None:
    """Strictly validate the bounded audit schema and forbidden counters."""

    if report.get("schema_name") != SCHEMA_NAME:
        raise ValueError("unexpected local EEG tooling schema name")
    if report.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected local EEG tooling schema version")
    tools = report.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("tools must be a nonempty list")
    tool_ids = [row.get("tool_id") for row in tools]
    if any(not isinstance(value, str) or not value for value in tool_ids):
        raise ValueError("every tool requires a nonempty tool_id")
    if len(tool_ids) != len(set(tool_ids)):
        raise ValueError("tool_ids must be unique")
    allowed_statuses = {
        "not_installed",
        "import_ready",
        "import_ready_capability_incomplete",
        "import_failed",
        "timeout",
        "malformed_probe_output",
    }
    for row in tools:
        if row.get("probe_status") not in allowed_statuses:
            raise ValueError(f"unexpected probe status for {row.get('tool_id')}")
        if row.get("blocked_network_attempts", 0) < 0:
            raise ValueError("blocked network attempts cannot be negative")
        if row.get("temporary_files_created", 0) < 0:
            raise ValueError("temporary file count cannot be negative")
        if row.get("temporary_bytes_created", 0) < 0:
            raise ValueError("temporary byte count cannot be negative")
    counters = report.get("access_counters", {})
    for field in (
        "successful_network_operations",
        "downloads",
        "real_or_protected_data_reads",
        "target_or_label_reads",
        "raw_signal_reads",
        "model_loads",
        "training_runs",
        "inference_runs",
        "scoring_runs",
        "provider_calls",
        "device_or_hardware_operations",
    ):
        if counters.get(field) != 0:
            raise ValueError(f"forbidden counter must remain zero: {field}")
    resources = report.get("resources", {})
    if resources.get("output_bytes", 0) > resources.get("maximum_output_bytes", -1):
        raise ValueError("local EEG tooling report exceeds output cap")
    if resources.get("runtime_seconds", -1) < 0:
        raise ValueError("runtime_seconds must be nonnegative")
    claim = report.get("claim_boundary", {})
    if not claim.get("engineering_capability") or not claim.get(
        "scientific_claim_not_established"
    ):
        raise ValueError("claim boundary is incomplete")


def tool_specs_as_dicts() -> list[dict[str, Any]]:
    """Return the fixed public tool matrix without importing optional packages."""

    return [asdict(spec) for spec in DEFAULT_TOOL_SPECS]


def _inspect_tool(spec: ToolSpec, *, timeout_seconds: float) -> dict[str, Any]:
    module_available = importlib.util.find_spec(spec.module) is not None
    distribution_version = _distribution_version(spec.distribution)
    base = {
        "tool_id": spec.tool_id,
        "distribution": spec.distribution,
        "module": spec.module,
        "role": spec.role,
        "distribution_installed": distribution_version is not None,
        "distribution_version": distribution_version,
        "module_available": module_available,
        "requested_capabilities": [
            f"{capability.module}.{capability.attribute}"
            for capability in spec.capabilities
        ],
        "probe_executed": False,
        "probe_status": "not_installed",
        "available_capabilities": [],
        "missing_capabilities": [],
        "error_type": None,
        "runtime_seconds": 0.0,
        "peak_rss_bytes": 0,
        "blocked_network_attempts": 0,
        "captured_output_bytes": 0,
        "captured_output_sha256": hashlib.sha256(b"").hexdigest(),
        "temporary_files_created": 0,
        "temporary_bytes_created": 0,
    }
    if not module_available:
        return base

    capability_payload = [
        [capability.module, capability.attribute]
        for capability in spec.capabilities
    ]
    command = [
        sys.executable,
        "-I",
        "-c",
        _PROBE_SCRIPT,
        spec.module,
        json.dumps(capability_payload, separators=(",", ":")),
    ]
    environment = os.environ.copy()
    environment.update(THREAD_ENVIRONMENT)
    environment.update(
        {
            "MPLBACKEND": "Agg",
            "MNE_DONTWRITE_HOME": "true",
            "MNE_LOGGING_LEVEL": "ERROR",
            "PYTHONNOUSERSITE": "1",
        }
    )
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-eeg-audit-") as temp_dir:
        environment.update(
            {
                "HOME": temp_dir,
                "MPLCONFIGDIR": temp_dir,
                "XDG_CACHE_HOME": temp_dir,
                "XDG_CONFIG_HOME": temp_dir,
            }
        )
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            temporary_files, temporary_bytes = _directory_usage(Path(temp_dir))
            return {
                **base,
                "probe_executed": True,
                "probe_status": "timeout",
                "error_type": "TimeoutExpired",
                "runtime_seconds": timeout_seconds,
                "temporary_files_created": temporary_files,
                "temporary_bytes_created": temporary_bytes,
            }
        temporary_files, temporary_bytes = _directory_usage(Path(temp_dir))
    captured_process_bytes = (
        completed.stdout.encode("utf-8", errors="replace")
        + completed.stderr.encode("utf-8", errors="replace")
    )
    try:
        result = json.loads(completed.stdout)
        _validate_probe_result(result)
        if completed.returncode != 0:
            raise ValueError("isolated probe returned a nonzero status")
    except (json.JSONDecodeError, TypeError, ValueError):
        return {
            **base,
            "probe_executed": True,
            "probe_status": "malformed_probe_output",
            "error_type": "InvalidProbeResult",
            "captured_output_bytes": len(captured_process_bytes),
            "captured_output_sha256": hashlib.sha256(captured_process_bytes).hexdigest(),
            "temporary_files_created": temporary_files,
            "temporary_bytes_created": temporary_bytes,
        }
    return {
        **base,
        "probe_executed": True,
        "probe_status": result["status"],
        "available_capabilities": result["available_capabilities"],
        "missing_capabilities": result["missing_capabilities"],
        "error_type": result["error_type"],
        "runtime_seconds": result["runtime_seconds"],
        "peak_rss_bytes": result["peak_rss_bytes"],
        "blocked_network_attempts": result["blocked_network_attempts"],
        "captured_output_bytes": result["captured_output_bytes"],
        "captured_output_sha256": result["captured_output_sha256"],
        "temporary_files_created": temporary_files,
        "temporary_bytes_created": temporary_bytes,
    }


def _validate_probe_result(result: Any) -> None:
    if not isinstance(result, dict):
        raise TypeError("probe result must be an object")
    if result.get("status") not in {
        "import_ready",
        "import_ready_capability_incomplete",
        "import_failed",
    }:
        raise ValueError("unexpected probe result status")
    for field in ("available_capabilities", "missing_capabilities"):
        value = result.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise TypeError(f"{field} must be a list of strings")
    for field in (
        "runtime_seconds",
        "peak_rss_bytes",
        "blocked_network_attempts",
        "captured_output_bytes",
    ):
        value = result.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise TypeError(f"{field} must be nonnegative numeric data")
    digest = result.get("captured_output_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise TypeError("captured_output_sha256 must be a SHA-256 hex digest")


def _directory_usage(root: Path) -> tuple[int, int]:
    files = [path for path in root.rglob("*") if path.is_file()]
    return len(files), sum(path.stat().st_size for path in files)


def _distribution_version(distribution: str | None) -> str | None:
    if distribution is None:
        return None
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _ready(tools: Sequence[dict[str, Any]], tool_id: str) -> bool:
    return any(
        row["tool_id"] == tool_id and row["probe_status"] == "import_ready"
        for row in tools
    )


def _capability_ready(
    tools: Sequence[dict[str, Any]], tool_id: str, capability: str
) -> bool:
    return any(
        row["tool_id"] == tool_id and capability in row["available_capabilities"]
        for row in tools
    )


def _stabilize_output_bytes(report: dict[str, Any]) -> None:
    for _ in range(8):
        size = len(_json_bytes(report))
        if report["resources"]["output_bytes"] == size:
            return
        report["resources"]["output_bytes"] = size
    raise RuntimeError("local EEG tooling output size did not stabilize")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024
