"""Generated-only qualification for the prospective IACKD-2 dual reversal."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import resource
import stat
import tempfile
import time
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping, Sequence

from neurodecodekit.preprocess import iackd_source_semantics as semantics


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_contract.v0.json"
)
CONTRACT_SHA256 = "f3b38cb2c5bf0a55e0816072ef654cc87bd2e2f36bab50df19947d66d2abdb7f"
REGISTRATION_COMMIT = "5bdab3055a8a1c5200b5ec6c0037e401d8c817ce"
REGISTRATION_CI_RUN_ID = 31448911258
REGISTRATION_BASE_JOB_ID = 93648969685
REGISTRATION_OPTIONAL_JOB_ID = 93648969711
REPORT_SCHEMA_NAME = "neurodecodekit.iackd_role_aware_dual_reversal_qualification"
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
FIT_IDS = (
    "whole_head_primary",
    "central_C3_C4_Cz",
    "occipital_O1_Oz_O2",
    "HEOG_VEOG_only",
    "fit_only_EOG_orthogonalized_primary",
    "early_half",
    "late_half",
    "pre_window_baseline",
    "event_index_and_timing_only",
    "fixed_train_label_derangement_seed_6841",
    "train_only_no_signal_prior",
)
CONDITION_IDS = FIT_IDS + (
    "all_zero_final_EEG_through_primary",
    "one_row_cyclic_final_feature_displacement",
    "fixed_final_only_EEG_channel_permutation_seed_6842",
    "opposite_hand_primary_without_adaptation",
)
FIXED_CONTROL_IDS = (
    "all_zero_final_EEG_through_primary",
    "fixed_train_label_derangement_seed_6841",
    "one_row_cyclic_final_feature_displacement",
    "fixed_final_only_EEG_channel_permutation_seed_6842",
    "opposite_hand_primary_without_adaptation",
)
ARM_ROWS = (
    {
        "arm_id": "C2I",
        "fit_condition": "red",
        "final_condition": "yellow",
        "fit_action_to_visual_sign": 1,
    },
    {
        "arm_id": "I2C",
        "fit_condition": "yellow",
        "final_condition": "red",
        "fit_action_to_visual_sign": -1,
    },
)
REFUSAL_IDS = (
    "IACKD2S-F01-contract-or-green-registration-mismatch",
    "IACKD2S-F02-dependency-or-thread-drift",
    "IACKD2S-F03-streaming-inventory-mismatch",
    "IACKD2S-F04-mocked-transport-path-or-status",
    "IACKD2S-F05-mocked-transport-size-etag-or-hash",
    "IACKD2S-F06-generated-reader-or-source-semantics",
    "IACKD2S-F07-causal-preprocessing-or-dimension",
    "IACKD2S-F08-split-count-or-arm-relation",
    "IACKD2S-F09-target-firewall-leak",
    "IACKD2S-F10-fit-or-prediction-inventory",
    "IACKD2S-F11-deterministic-replay",
    "IACKD2S-F12-freeze-or-router",
    "IACKD2S-F13-output-path-or-cap",
    "IACKD2S-F14-resource-cap",
    "IACKD2S-F15-report-schema-or-claim-boundary",
)


class DualReversalRefusal(RuntimeError):
    """A generated qualification invariant failed closed."""

    def __init__(self, refusal_id: str, message: str) -> None:
        super().__init__(f"{refusal_id}: {message}")
        self.refusal_id = refusal_id


@dataclass(frozen=True)
class MockResponse:
    path: str
    status: int
    body: bytes
    etag: str
    redirected: bool = False


@dataclass(frozen=True)
class _Prior:
    label: int

    def predict(self, values: Any) -> Any:
        np = _np()
        return np.full(len(values), self.label, dtype="int8")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _np():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("IACKD-2 qualification requires NumPy") from exc
    return np


def _signal():
    try:
        from scipy import signal
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("IACKD-2 qualification requires SciPy") from exc
    return signal


def _lda_class():
    try:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("IACKD-2 qualification requires scikit-learn") from exc
    return LinearDiscriminantAnalysis


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_bytes(value))


def _array_sha256(value: Any) -> str:
    np = _np()
    array = np.ascontiguousarray(value)
    return _canonical_sha256(
        {
            "dtype": array.dtype.str,
            "shape": list(array.shape),
            "bytes_sha256": _sha256_bytes(array.tobytes(order="C")),
        }
    )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if os.uname().sysname == "Darwin" else value * 1024


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the immutable green IACKD-2 registration."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _file_sha256(path) != CONTRACT_SHA256:
        raise DualReversalRefusal(REFUSAL_IDS[0], "contract SHA-256 differs")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("contract_id") != "IACKD-2-role-aware-dual-reversal-contract-v0"
        or value.get("status")
        != "prospective_registration_frozen_real_execution_unauthorized"
        or value["source_semantics_contract"].get("policy_sha256")
        != semantics.POLICY_SHA256
        or value["fit_inventory"].get("required_parameter_update_fits") != 660
        or value["prediction_inventory"].get("required_prediction_sets") != 900
    ):
        raise DualReversalRefusal(REFUSAL_IDS[0], "contract invariants differ")
    return value


def dependency_versions() -> dict[str, str]:
    """Return exact frozen optional versions or fail closed."""

    expected = load_registered_contract()["dependency_contract"]["versions"]
    packages = {
        "numpy": "numpy",
        "scipy": "scipy",
        "mne": "mne",
        "scikit_learn": "scikit-learn",
    }
    observed = {key: metadata.version(package) for key, package in packages.items()}
    if observed != expected:
        raise DualReversalRefusal(
            REFUSAL_IDS[1],
            f"optional dependency versions differ: {observed!r}",
        )
    return observed


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    drift = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if drift:
        raise DualReversalRefusal(REFUSAL_IDS[1], f"thread environment differs: {drift!r}")


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return a target-free plan without importing optional dependencies."""

    contract = load_registered_contract(repo_root)
    return {
        "schema_name": "neurodecodekit.iackd_role_aware_dual_reversal_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "generated_fixture_only_no_real_or_public_access",
        "registration": {
            "commit": REGISTRATION_COMMIT,
            "CI_run_id": REGISTRATION_CI_RUN_ID,
            "base_python_job_id": REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": contract["source_semantics_contract"]["policy_sha256"],
        "participant_hand_units": 30,
        "arm_count": 2,
        "primary_matrix_fits": 660,
        "primary_prediction_sets": 900,
        "deterministic_replay_fits": 660,
        "deterministic_replay_prediction_sets": 900,
        "generated_output_cap_bytes": contract["resource_caps"][
            "future_generated_implementation"
        ]["generated_output_bytes"],
        "CPU_threads": 1,
        "workers": 1,
        "real_or_public_payload_reads": 0,
        "old_retained_bundle_operations": 0,
        "scientific_claim": False,
    }


def _subject_runs(subject: str) -> tuple[str, ...]:
    if subject in {"sub-04", "sub-05"}:
        return ("01", "02", "03", "04", "05", "06")
    return ("01", "02", "03", "04")


def _split_kind(subject: str, run: str) -> str:
    runs = _subject_runs(subject)
    if run not in runs:
        raise DualReversalRefusal(REFUSAL_IDS[7], "run is outside the frozen split")
    return "final" if run == runs[-1] else "fit"


def _unit(subject: str, hand: str) -> str:
    return f"{subject}|{hand}"


def _prediction_key(arm: str, unit: str) -> str:
    return f"{arm}|{unit}"


def _run_key_from_inventory(row: Mapping[str, Any]) -> str | None:
    if row["role"] in {"coordsystem", "electrodes"}:
        return None
    path = str(row["path"])
    if "/eeg/" in path:
        match = re.search(
            r"(?P<subject>sub-[0-9]+).*acq-(?P<hand>left|right)_run-(?P<run>[0-9]+)",
            path,
        )
    else:
        match = re.search(
            r"(?P<subject>sub-[0-9]+).*run-(?P<run>[0-9]+)_hand-(?P<hand>left|right)",
            path,
        )
    if match is None:
        raise DualReversalRefusal(REFUSAL_IDS[2], f"inventory path is unmatched: {path}")
    return f"{match['subject']}:{match['hand']}:{match['run']}"


def validate_streaming_inventory(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Replay the storage-safe run grouping from the committed public inventory."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    binding = contract["bindings"]["committed_openneuro_inventory"]
    path = root / binding["path"]
    if _file_sha256(path) != binding["sha256"]:
        raise DualReversalRefusal(REFUSAL_IDS[2], "inventory file hash differs")
    inventory = json.loads(path.read_text(encoding="utf-8"))
    selected = inventory["selected_objects"]
    groups: dict[str, list[Mapping[str, Any]]] = {}
    geometry: list[Mapping[str, Any]] = []
    for row in selected:
        key = _run_key_from_inventory(row)
        if key is None:
            geometry.append(row)
        else:
            groups.setdefault(key, []).append(row)
    streaming = contract["fresh_streaming_contract"]
    group_sizes = {key: sum(int(row["size_bytes"]) for row in rows) for key, rows in groups.items()}
    checks = (
        len(selected) == contract["dataset_binding"]["selected_object_count"],
        sum(int(row["size_bytes"]) for row in selected)
        == contract["dataset_binding"]["selected_payload_bytes"],
        len(groups) == streaming["run_group_count"],
        all(len(rows) == streaming["objects_per_run_group"] for rows in groups.values()),
        max(group_sizes.values()) == streaming["largest_run_group_bytes"],
        max(int(row["size_bytes"]) for row in selected)
        == streaming["largest_individual_object_bytes"],
        len(geometry) == streaming["geometry_object_count"],
        sum(int(row["size_bytes"]) for row in geometry) == streaming["geometry_bytes"],
    )
    if not all(checks):
        raise DualReversalRefusal(REFUSAL_IDS[2], "streaming inventory geometry differs")
    return {
        "selected_objects": len(selected),
        "selected_payload_bytes": sum(int(row["size_bytes"]) for row in selected),
        "run_groups": len(groups),
        "objects_per_run_group": streaming["objects_per_run_group"],
        "largest_run_group_bytes": max(group_sizes.values()),
        "largest_individual_object_bytes": max(int(row["size_bytes"]) for row in selected),
        "geometry_objects": len(geometry),
        "geometry_bytes": sum(int(row["size_bytes"]) for row in geometry),
        "run_group_set_sha256": _canonical_sha256(
            [
                {
                    "run_key": key,
                    "bytes": group_sizes[key],
                    "roles": sorted(str(row["role"]) for row in groups[key]),
                }
                for key in sorted(groups)
            ]
        ),
    }


def verify_mock_response(
    response: MockResponse,
    *,
    expected_path: str,
    expected_size: int,
    expected_etag: str,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate a generated response using the future transport boundary."""

    if response.redirected or response.status != 200 or response.path != expected_path:
        raise DualReversalRefusal(REFUSAL_IDS[3], "mocked response path or status differs")
    if (
        len(response.body) != expected_size
        or response.etag != expected_etag
        or _sha256_bytes(response.body) != expected_sha256
    ):
        raise DualReversalRefusal(REFUSAL_IDS[4], "mocked body size ETag or SHA differs")
    return {
        "path_sha256": _sha256_bytes(response.path.encode("utf-8")),
        "body_bytes": len(response.body),
        "body_sha256": expected_sha256,
        "etag_sha256": _sha256_bytes(expected_etag.encode("utf-8")),
    }


def _mock_transport_qualification() -> dict[str, Any]:
    body = b"generated-IACKD2-mocked-transport-body-v0"
    path = "generated/sub-00/eeg/generated.vhdr"
    etag = "generated-etag-v0"
    sha256 = _sha256_bytes(body)
    response = MockResponse(path=path, status=200, body=body, etag=etag)
    passed = verify_mock_response(
        response,
        expected_path=path,
        expected_size=len(body),
        expected_etag=etag,
        expected_sha256=sha256,
    )
    mutations = (
        MockResponse(path=f"{path}.other", status=200, body=body, etag=etag),
        MockResponse(path=path, status=302, body=body, etag=etag),
        MockResponse(path=path, status=200, body=body, etag=etag, redirected=True),
        MockResponse(path=path, status=200, body=body + b"x", etag=etag),
        MockResponse(path=path, status=200, body=body, etag=f"{etag}-drift"),
        MockResponse(path=path, status=200, body=body[:-1] + b"x", etag=etag),
    )
    refusals: list[str] = []
    for mutation in mutations:
        try:
            verify_mock_response(
                mutation,
                expected_path=path,
                expected_size=len(body),
                expected_etag=etag,
                expected_sha256=sha256,
            )
        except DualReversalRefusal as exc:
            refusals.append(exc.refusal_id)
        else:  # pragma: no cover - guarded by fixed mutations
            raise DualReversalRefusal(REFUSAL_IDS[3], "transport mutation was accepted")
    if len(refusals) != 6 or set(refusals) != {REFUSAL_IDS[3], REFUSAL_IDS[4]}:
        raise DualReversalRefusal(REFUSAL_IDS[3], "transport refusal coverage differs")
    return {"pass": passed, "mutation_attempts": len(refusals), "refusal_ids": refusals}


def _write_exclusive(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)


def _ensure_output_preflight(path: Path, maximum_bytes: int) -> None:
    if maximum_bytes <= 0 or maximum_bytes > 8 * 1024 * 1024:
        raise DualReversalRefusal(REFUSAL_IDS[12], "output cap is outside 1 byte to 8 MiB")
    if not path.is_absolute() or path.exists() or path.is_symlink():
        raise DualReversalRefusal(REFUSAL_IDS[12], "output path must be new and absolute")
    parent = path.parent
    if not parent.is_dir():
        raise DualReversalRefusal(REFUSAL_IDS[12], "output parent is unavailable")
    current = parent
    while True:
        mode = os.lstat(current).st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise DualReversalRefusal(REFUSAL_IDS[12], "output parent chain is not regular")
        if current == current.parent:
            break
        current = current.parent


def _json_report_bytes(report: Mapping[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def _generated_brainvision_text(
    channel_names: Sequence[str], *, sample_count: int
) -> tuple[str, str]:
    channel_lines = [
        f"Ch{index}={name},,1,uV" for index, name in enumerate(channel_names, start=1)
    ]
    vhdr = "\n".join(
        (
            "Brain Vision Data Exchange Header File Version 1.0",
            "; Generated source-independent NeuroDecodeKit fixture",
            "[Common Infos]",
            "Codepage=UTF-8",
            "DataFile=generated.eeg",
            "MarkerFile=generated.vmrk",
            "DataFormat=BINARY",
            "DataOrientation=MULTIPLEXED",
            f"NumberOfChannels={len(channel_names)}",
            "SamplingInterval=976.5625",
            "[Binary Infos]",
            "BinaryFormat=IEEE_FLOAT_32",
            "[Channel Infos]",
            *channel_lines,
            "",
        )
    )
    marker_positions = (sample_count // 4, sample_count // 2, 3 * sample_count // 4)
    vmrk = "\n".join(
        (
            "Brain Vision Data Exchange Marker File, Version 1.0",
            "; Generated source-independent NeuroDecodeKit fixture",
            "[Common Infos]",
            "Codepage=UTF-8",
            "DataFile=generated.eeg",
            "[Marker Infos]",
            "Mk1=New Segment,,1,1,0",
            f"Mk2=Stimulus,S 55,{marker_positions[0]},1,0",
            f"Mk3=Stimulus,S 14,{marker_positions[1]},1,0",
            f"Mk4=Response,R 66,{marker_positions[2]},1,0",
            "",
        )
    )
    return vhdr, vmrk


def write_generated_brainvision_fixture(
    output_root: str | Path,
    *,
    include_optional_references: bool,
    sample_count: int = 4096,
) -> dict[str, Any]:
    """Write one tiny generated BrainVision/source-semantics fixture."""

    np = _np()
    root = Path(output_root)
    if root.exists() or root.is_symlink() or not root.parent.is_dir():
        raise DualReversalRefusal(REFUSAL_IDS[5], "generated fixture root is not exclusive")
    root.mkdir(mode=0o700)
    policy = semantics.load_registered_policy()["policy"]
    fixture = semantics.make_generated_fixture(
        include_optional_references=include_optional_references,
        policy=policy,
    )
    semantic_summary = semantics.validate_generated_fixture(fixture, policy)
    channel_names = [str(row["name"]) for row in fixture["channels"]]
    seed = 7201 if include_optional_references else 7200
    rng = np.random.default_rng(seed)
    values_uv = rng.normal(0.0, 0.2, size=(len(channel_names), sample_count)).astype("float32")
    time_axis = np.linspace(-math.pi, math.pi, sample_count, endpoint=False, dtype="float64")
    for name in ("C3", "C4", "Cz"):
        values_uv[channel_names.index(name)] += (0.8 * np.sin(time_axis)).astype("float32")
    vhdr, vmrk = _generated_brainvision_text(channel_names, sample_count=sample_count)
    paths = {
        "vhdr": root / "generated.vhdr",
        "vmrk": root / "generated.vmrk",
        "eeg": root / "generated.eeg",
        "semantics": root / "generated.source_semantics.json",
    }
    _write_exclusive(paths["vhdr"], vhdr.encode("utf-8"))
    _write_exclusive(paths["vmrk"], vmrk.encode("utf-8"))
    _write_exclusive(paths["eeg"], values_uv.T.astype("<f4").tobytes(order="C"))
    _write_exclusive(paths["semantics"], _json_report_bytes(fixture))
    return {
        "paths": paths,
        "semantic_summary": semantic_summary,
        "input_bytes": sum(path.stat().st_size for path in paths.values()),
        "expected_values_volts_sha256": _array_sha256(values_uv.astype("float64") * 1e-6),
    }


def _feature_row(values: Any) -> Any:
    np = _np()
    matrix = np.asarray(values, dtype="float64")
    if matrix.ndim != 2 or matrix.shape[1] < 8:
        raise DualReversalRefusal(REFUSAL_IDS[6], "feature window is malformed")
    boundaries = np.linspace(0, matrix.shape[1], 5, dtype="int64")
    means = np.stack(
        [matrix[:, boundaries[index] : boundaries[index + 1]].mean(axis=1) for index in range(4)],
        axis=1,
    )
    x = np.linspace(-0.5, 0.5, matrix.shape[1], dtype="float64")
    slopes = (matrix @ x / float(np.dot(x, x)))[:, None]
    return np.concatenate((means, slopes), axis=1).reshape(-1).astype("float32")


def _half_feature_row(values: Any) -> Any:
    np = _np()
    matrix = np.asarray(values, dtype="float64")
    if matrix.ndim != 2 or matrix.shape[1] < 8:
        raise DualReversalRefusal(REFUSAL_IDS[6], "half-window is malformed")
    midpoint = matrix.shape[1] // 2
    means = np.stack(
        (matrix[:, :midpoint].mean(axis=1), matrix[:, midpoint:].mean(axis=1)),
        axis=1,
    )
    x = np.linspace(-0.5, 0.5, matrix.shape[1], dtype="float64")
    slopes = (matrix @ x / float(np.dot(x, x)))[:, None]
    return np.concatenate((means, slopes), axis=1).reshape(-1).astype("float32")


def read_and_qualify_generated_brainvision(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Read one generated BrainVision fixture and qualify causal view construction."""

    np = _np()
    signal = _signal()
    try:
        import mne
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("IACKD-2 qualification requires MNE") from exc
    paths = fixture["paths"]
    raw = mne.io.read_raw_brainvision(paths["vhdr"], preload=True, verbose="ERROR")
    source_fixture = json.loads(paths["semantics"].read_text(encoding="utf-8"))
    policy = semantics.load_registered_policy()["policy"]
    source_summary = semantics.validate_generated_fixture(source_fixture, policy)
    source_names = [str(row["name"]) for row in source_fixture["channels"]]
    if raw.ch_names != source_names or not math.isclose(float(raw.info["sfreq"]), 1024.0):
        raise DualReversalRefusal(REFUSAL_IDS[5], "generated reader order or rate differs")
    values = raw.get_data()
    if values.shape != (len(source_names), 4096) or not np.isfinite(values).all():
        raise DualReversalRefusal(REFUSAL_IDS[5], "generated reader samples differ")
    if _array_sha256(values) != fixture["expected_values_volts_sha256"]:
        raise DualReversalRefusal(REFUSAL_IDS[5], "generated reader sample hash differs")
    expected_annotations = {"Stimulus/S 55", "Stimulus/S 14", "Response/R 66"}
    if not expected_annotations.issubset(set(raw.annotations.description)):
        raise DualReversalRefusal(REFUSAL_IDS[5], "generated marker annotations differ")

    predictive_names = source_summary["predictive_output_order"]
    predictive_indices = [source_names.index(name) for name in predictive_names]
    central_indices = [predictive_names.index(name) for name in ("C3", "C4", "Cz")]
    occipital_indices = [predictive_names.index(name) for name in ("O1", "Oz", "O2")]
    ocular_indices = [source_names.index(name) for name in ("HEOG", "VEOG")]
    predictive = values[predictive_indices]
    predictive = predictive - predictive.mean(axis=0, keepdims=True)
    ocular = values[ocular_indices]
    low_sos = signal.butter(4, (0.5, 4.0), btype="bandpass", fs=1024.0, output="sos")
    filtered = signal.sosfilt(low_sos, predictive, axis=1)
    filtered_ocular = signal.sosfilt(low_sos, ocular, axis=1)
    mutated = predictive.copy()
    mutated[:, 2048:] += 1000.0
    mutated_filtered = signal.sosfilt(low_sos, mutated, axis=1)
    if not np.array_equal(filtered[:, :2048], mutated_filtered[:, :2048]):
        raise DualReversalRefusal(REFUSAL_IDS[6], "future-tail mutation changed causal prefix")
    main = filtered[:, 1024:2048]
    prewindow = filtered[:, :1024]
    dimensions = {
        "primary": int(_feature_row(main).size),
        "central": int(_feature_row(main[central_indices]).size),
        "occipital": int(_feature_row(main[occipital_indices]).size),
        "ocular": int(_feature_row(filtered_ocular[:, 1024:2048]).size),
        "early": int(_half_feature_row(main[:, :512]).size),
        "late": int(_half_feature_row(main[:, 512:]).size),
        "prewindow": int(_feature_row(prewindow).size),
        "timing": 4,
    }
    expected_dimensions = {
        "primary": 130,
        "central": 15,
        "occipital": 15,
        "ocular": 10,
        "early": 78,
        "late": 78,
        "prewindow": 130,
        "timing": 4,
    }
    if dimensions != expected_dimensions:
        raise DualReversalRefusal(REFUSAL_IDS[6], "generated feature dimensions differ")
    return {
        "row_count": source_summary["row_count"],
        "predictive_EEG_count": len(predictive_names),
        "optional_M1_M2_present": source_summary["optional_M1_M2_present"],
        "dimensions": dimensions,
        "causal_future_tail_invariant": True,
        "right_context_seconds": 0.0,
        "annotations_verified": 3,
        "MNE_inferred_types_authoritative": False,
        "source_bindings": source_summary["bindings"],
    }


def _seed(*parts: str) -> int:
    payload = "|".join(parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _generated_feature_row(
    *,
    subject: str,
    hand: str,
    run: str,
    condition: str,
    event_index: int,
    actual: int,
    visual: int,
    predictive_names: Sequence[str],
) -> dict[str, Any]:
    np = _np()
    rng = np.random.default_rng(
        _seed("IACKD2", subject, hand, run, condition, str(event_index))
    )
    action_sign = 1.0 if actual else -1.0
    visual_sign = 1.0 if visual else -1.0
    hand_sign = 1.0 if hand == "left" else -1.0
    run_offset = float(int(run)) - 3.5
    nuisance_channels = np.linspace(-1.0, 1.0, 26, dtype="float64")
    nuisance_profile = np.asarray([0.2, -0.1, 0.3, -0.2, 0.1], dtype="float64")
    whole = 0.03 * run_offset * np.outer(nuisance_channels, nuisance_profile)
    action_profile = np.asarray([0.8, 1.1, 1.5, 1.9, 2.3])
    for name, weight in (("C3", 1.0), ("C4", -0.9), ("Cz", 0.8)):
        whole[predictive_names.index(name)] += hand_sign * action_sign * weight * action_profile
    for name, weight in (("O1", 0.18), ("Oz", -0.16), ("O2", 0.14)):
        whole[predictive_names.index(name)] += visual_sign * weight * action_profile
    whole -= whole.mean(axis=0, keepdims=True)
    central = whole[[predictive_names.index(name) for name in ("C3", "C4", "Cz")]]
    occipital = rng.normal(0.0, 0.10, size=(3, 5))
    occipital += visual_sign * np.asarray([1.0, -0.9, 0.8])[:, None] * action_profile
    ocular = rng.normal(0.0, 0.10, size=(2, 5))
    ocular += visual_sign * np.asarray([1.0, -0.8])[:, None] * action_profile
    early = rng.normal(0.0, 0.14, size=(26, 3))
    late = rng.normal(0.0, 0.12, size=(26, 3))
    half_profile = np.asarray([0.8, 1.2, 1.6])
    for name, weight in (("C3", 1.0), ("C4", -0.9), ("Cz", 0.8)):
        index = predictive_names.index(name)
        early[index] += hand_sign * action_sign * weight * 0.9 * half_profile
        late[index] += hand_sign * action_sign * weight * 1.8 * half_profile
    prewindow = rng.normal(0.0, 0.25, size=(26, 5))
    timing = np.asarray(
        [
            float(int(run)),
            float(event_index),
            1.5 + 0.01 * (event_index % 3),
            1.0 + 0.01 * (event_index % 5),
        ],
        dtype="float32",
    )
    physiology = np.asarray(
        [
            *(central.mean(axis=1).tolist()),
            float(np.mean(late**2)),
            float(np.mean(early**2)),
            float(late.mean() - early.mean()),
            30.0,
        ],
        dtype="float32",
    )
    return {
        "whole_features": whole.reshape(-1).astype("float32"),
        "central_features": central.reshape(-1).astype("float32"),
        "occipital_features": occipital.reshape(-1).astype("float32"),
        "ocular_features": ocular.reshape(-1).astype("float32"),
        "early_features": early.reshape(-1).astype("float32"),
        "late_features": late.reshape(-1).astype("float32"),
        "prewindow_features": prewindow.reshape(-1).astype("float32"),
        "timing_features": timing,
        "physiology_features": physiology,
    }


def _empty_rows(*, targets: bool) -> dict[str, list[Any]]:
    keys = [
        "item_ids",
        "subjects",
        "hands",
        "runs",
        "whole_features",
        "central_features",
        "occipital_features",
        "ocular_features",
        "early_features",
        "late_features",
        "prewindow_features",
        "timing_features",
        "physiology_features",
    ]
    if targets:
        keys.append("fit_targets")
    return {key: [] for key in keys}


def _empty_sealed() -> dict[str, list[Any]]:
    return {"item_ids": [], "actual_action": [], "cue_surrogate": []}


def _append_feature_row(destination: dict[str, list[Any]], identity: Mapping[str, str], row: Mapping[str, Any]) -> None:
    for key in ("item_ids", "subjects", "hands", "runs"):
        destination[key].append(identity[key])
    for key, value in row.items():
        destination[key].append(value)


def _array_rows(rows: Mapping[str, Sequence[Any]], *, targets: bool) -> dict[str, Any]:
    np = _np()
    value = {
        "item_ids": np.asarray(rows["item_ids"], dtype="U96"),
        "subjects": np.asarray(rows["subjects"], dtype="U8"),
        "hands": np.asarray(rows["hands"], dtype="U5"),
        "runs": np.asarray(rows["runs"], dtype="U2"),
    }
    for key in (
        "whole_features",
        "central_features",
        "occipital_features",
        "ocular_features",
        "early_features",
        "late_features",
        "prewindow_features",
        "timing_features",
        "physiology_features",
    ):
        value[key] = np.asarray(rows[key], dtype="float32")
    if targets:
        value["fit_targets"] = np.asarray(rows["fit_targets"], dtype="int8")
    return value


def _assert_target_free(value: Any) -> None:
    forbidden = (
        "target",
        "label",
        "direction",
        "signed",
        "condition",
        "color",
        "trajectory",
        "prediction",
        "probability",
        "score",
        "outcome",
    )

    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, nested in item.items():
                normalized = str(key).lower()
                if any(token in normalized for token in forbidden):
                    raise DualReversalRefusal(REFUSAL_IDS[8], f"target-free key leaks: {key}")
                walk(nested)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                walk(nested)

    walk(value)


def build_generated_derivatives(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build target-firewalled dual-arm arrays from deterministic generated features."""

    np = _np()
    contract = load_registered_contract(repo_root)
    policy = semantics.load_registered_policy(repo_root)["policy"]
    semantic_groups = [
        semantics.validate_generated_fixture(
            semantics.make_generated_fixture(
                include_optional_references=include_optional,
                policy=policy,
            ),
            policy,
        )
        for include_optional in (False, True)
    ]
    predictive_names = semantic_groups[0]["predictive_output_order"]
    fit_lists: dict[str, dict[str, list[Any]]] = {}
    final_lists: dict[str, dict[str, list[Any]]] = {}
    sealed_lists: dict[str, dict[str, list[Any]]] = {}
    generated_rows = 0
    for subject in contract["dataset_binding"]["participant_ids"]:
        for hand in contract["dataset_binding"]["moving_hand_entities"]:
            unit = _unit(subject, hand)
            for arm in ARM_ROWS:
                key = _prediction_key(str(arm["arm_id"]), unit)
                fit_lists[key] = _empty_rows(targets=True)
                final_lists[key] = _empty_rows(targets=False)
                sealed_lists[key] = _empty_sealed()
            for run in _subject_runs(subject):
                split = _split_kind(subject, run)
                for condition in ("red", "yellow"):
                    labels = np.tile(np.asarray([0, 1], dtype="int8"), 8)
                    for event_index, actual_value in enumerate(labels.tolist()):
                        actual = int(actual_value)
                        visual = actual if condition == "red" else 1 - actual
                        item_id = f"{subject}-{hand}-{run}-{condition}-{event_index:02d}"
                        identity = {
                            "item_ids": item_id,
                            "subjects": subject,
                            "hands": hand,
                            "runs": run,
                        }
                        features = _generated_feature_row(
                            subject=subject,
                            hand=hand,
                            run=run,
                            condition=condition,
                            event_index=event_index,
                            actual=actual,
                            visual=visual,
                            predictive_names=predictive_names,
                        )
                        generated_rows += 1
                        for arm in ARM_ROWS:
                            arm_id = str(arm["arm_id"])
                            key = _prediction_key(arm_id, unit)
                            if split == "fit" and condition == arm["fit_condition"]:
                                _append_feature_row(fit_lists[key], identity, features)
                                fit_lists[key]["fit_targets"].append(actual)
                            elif split == "final" and condition == arm["final_condition"]:
                                _append_feature_row(final_lists[key], identity, features)
                                cue = visual if int(arm["fit_action_to_visual_sign"]) == 1 else 1 - visual
                                if cue != 1 - actual:
                                    raise DualReversalRefusal(
                                        REFUSAL_IDS[7], "generated cue surrogate is not opposite action"
                                    )
                                sealed_lists[key]["item_ids"].append(item_id)
                                sealed_lists[key]["actual_action"].append(actual)
                                sealed_lists[key]["cue_surrogate"].append(cue)
    fit = {key: _array_rows(rows, targets=True) for key, rows in fit_lists.items()}
    final = {key: _array_rows(rows, targets=False) for key, rows in final_lists.items()}
    sealed = {
        key: {
            "item_ids": np.asarray(rows["item_ids"], dtype="U96"),
            "actual_action": np.asarray(rows["actual_action"], dtype="int8"),
            "cue_surrogate": np.asarray(rows["cue_surrogate"], dtype="int8"),
        }
        for key, rows in sealed_lists.items()
    }
    for key in sorted(final):
        _assert_target_free(final[key])
        if not np.array_equal(final[key]["item_ids"], sealed[key]["item_ids"]):
            raise DualReversalRefusal(REFUSAL_IDS[8], "sealed and target-free IDs differ")
        labels = fit[key]["fit_targets"]
        final_actual = sealed[key]["actual_action"]
        if min(np.bincount(labels, minlength=2)) < 24 or min(
            np.bincount(final_actual, minlength=2)
        ) < 8:
            raise DualReversalRefusal(REFUSAL_IDS[7], "generated unit-arm counts are insufficient")
        if not np.array_equal(sealed[key]["cue_surrogate"], 1 - final_actual):
            raise DualReversalRefusal(REFUSAL_IDS[7], "sealed target views are not opposites")
    fit_rows = sum(len(value["item_ids"]) for value in fit.values())
    final_rows = sum(len(value["item_ids"]) for value in final.values())
    if generated_rows != 4096 or fit_rows != 3136 or final_rows != 960:
        raise DualReversalRefusal(REFUSAL_IDS[7], "generated row inventory differs")
    feature_bytes = sum(
        int(array.nbytes)
        for group in (fit, final)
        for rows in group.values()
        for array in rows.values()
        if isinstance(array, np.ndarray)
    )
    split_sha256 = _canonical_sha256(
        {
            key: {
                "fit_item_ids_sha256": _array_sha256(fit[key]["item_ids"]),
                "final_item_ids_sha256": _array_sha256(final[key]["item_ids"]),
            }
            for key in sorted(fit)
        }
    )
    final_item_ids_sha256 = _canonical_sha256(
        {
            key: _array_sha256(final[key]["item_ids"])
            for key in sorted(final)
        }
    )
    return {
        "model_stage": {
            "fit": fit,
            "final": final,
            "fit_rows": fit_rows,
            "final_rows": final_rows,
            "split_sha256": split_sha256,
            "final_item_ids_sha256": final_item_ids_sha256,
        },
        "scorer_stage": {
            "sealed": sealed,
            "sealed_rows": final_rows,
            "final_item_ids_sha256": final_item_ids_sha256,
        },
        "generated_source_rows": generated_rows,
        "feature_bytes": feature_bytes,
        "semantic_groups": semantic_groups,
    }


def _fit_lda(values: Any, labels: Any) -> Any:
    np = _np()
    matrix = np.asarray(values, dtype="float64")
    target = np.asarray(labels, dtype="int8")
    if matrix.ndim != 2 or target.shape != (matrix.shape[0],) or set(target.tolist()) != {0, 1}:
        raise DualReversalRefusal(REFUSAL_IDS[9], "LDA fit arrays are malformed")
    model = _lda_class()(solver="lsqr", shrinkage=0.1, priors=np.asarray([0.5, 0.5]))
    model.fit(matrix, target)
    return model


def _fit_prior(labels: Any) -> _Prior:
    np = _np()
    counts = np.bincount(np.asarray(labels, dtype="int8"), minlength=2)
    return _Prior(label=int(counts[1] > counts[0]))


def _fixed_train_label_derangement(labels: Any, runs: Any, *, key: str) -> Any:
    np = _np()
    target = np.asarray(labels, dtype="int8")
    run_ids = np.asarray(runs)
    if (
        target.ndim != 1
        or run_ids.shape != target.shape
        or set(target.tolist()) != {0, 1}
    ):
        raise DualReversalRefusal(REFUSAL_IDS[9], "derangement labels are malformed")
    shuffled = np.empty_like(target)
    rng = np.random.default_rng(_seed("derangement", "6841", key))
    for run_id in sorted(set(run_ids.tolist())):
        run_mask = run_ids == run_id
        for source_label in (0, 1):
            indices = np.flatnonzero(run_mask & (target == source_label))
            if len(indices) % 2:
                raise DualReversalRefusal(
                    REFUSAL_IDS[9], "derangement stratum count is not even"
                )
            rng.shuffle(indices)
            midpoint = len(indices) // 2
            shuffled[indices[:midpoint]] = 0
            shuffled[indices[midpoint:]] = 1
        cross_tab = np.asarray(
            [
                [
                    int(
                        np.sum(
                            run_mask
                            & (target == source)
                            & (shuffled == assigned)
                        )
                    )
                    for assigned in (0, 1)
                ]
                for source in (0, 1)
            ]
        )
        if not np.all(cross_tab == cross_tab[0, 0]):
            raise DualReversalRefusal(
                REFUSAL_IDS[9], "derangement is not run-and-class-balanced"
            )
    return shuffled


def _eog_residuals(
    fit_eeg: Any,
    fit_eog: Any,
    final_eeg: Any,
    final_eog: Any,
) -> tuple[Any, Any]:
    np = _np()
    fit_eeg = np.asarray(fit_eeg, dtype="float64")
    final_eeg = np.asarray(final_eeg, dtype="float64")
    fit_design = np.column_stack((np.ones(len(fit_eog)), np.asarray(fit_eog, dtype="float64")))
    final_design = np.column_stack(
        (np.ones(len(final_eog)), np.asarray(final_eog, dtype="float64"))
    )
    penalty = np.eye(fit_design.shape[1], dtype="float64") * 0.001
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        fit_design.T @ fit_design + penalty,
        fit_design.T @ fit_eeg,
    )
    return fit_eeg - fit_design @ coefficients, final_eeg - final_design @ coefficients


def _predict(model: Any, values: Any) -> Any:
    np = _np()
    prediction = np.asarray(model.predict(values), dtype="int8")
    if prediction.ndim != 1 or not set(prediction.tolist()).issubset({0, 1}):
        raise DualReversalRefusal(REFUSAL_IDS[9], "model prediction is malformed")
    return prediction


def _validate_model_stage(model_stage: Mapping[str, Any]) -> None:
    expected = {
        "fit",
        "final",
        "fit_rows",
        "final_rows",
        "split_sha256",
        "final_item_ids_sha256",
    }
    if set(model_stage) != expected:
        raise DualReversalRefusal(REFUSAL_IDS[8], "model-stage schema differs")
    fit = model_stage["fit"]
    final = model_stage["final"]
    if (
        not isinstance(fit, Mapping)
        or not isinstance(final, Mapping)
        or set(fit) != set(final)
        or len(fit) != 60
        or model_stage["fit_rows"] != 3136
        or model_stage["final_rows"] != 960
        or not _is_sha256(model_stage["split_sha256"])
        or not _is_sha256(model_stage["final_item_ids_sha256"])
    ):
        raise DualReversalRefusal(REFUSAL_IDS[8], "model-stage inventory differs")
    for rows in final.values():
        _assert_target_free(rows)


def _prediction_hash_summary(
    predictions: Mapping[str, Mapping[str, Any]],
    *,
    parameter_updates: int,
    prediction_sets: int,
) -> tuple[dict[str, str], str]:
    np = _np()
    if set(predictions) != set(CONDITION_IDS):
        raise DualReversalRefusal(REFUSAL_IDS[9], "prediction conditions differ")
    key_sets = {condition: set(rows) for condition, rows in predictions.items()}
    if not key_sets or len(set(map(frozenset, key_sets.values()))) != 1:
        raise DualReversalRefusal(REFUSAL_IDS[9], "prediction unit sets differ")
    if len(next(iter(key_sets.values()))) != 60:
        raise DualReversalRefusal(REFUSAL_IDS[9], "prediction unit count differs")
    for rows in predictions.values():
        for prediction in rows.values():
            array = np.asarray(prediction)
            if array.ndim != 1 or not set(array.tolist()).issubset({0, 1}):
                raise DualReversalRefusal(REFUSAL_IDS[9], "prediction payload differs")
    hashes = {
        condition: _canonical_sha256(
            [
                {
                    "key_sha256": _sha256_bytes(key.encode("utf-8")),
                    "prediction_sha256": _array_sha256(predictions[condition][key]),
                    "count": len(predictions[condition][key]),
                }
                for key in sorted(predictions[condition])
            ]
        )
        for condition in CONDITION_IDS
    }
    private_hash = _canonical_sha256(
        {
            "condition_hashes": hashes,
            "condition_ids": list(CONDITION_IDS),
            "parameter_update_fits": parameter_updates,
            "prediction_sets": prediction_sets,
        }
    )
    return hashes, private_hash


def run_generated_model_matrix(model_stage: Mapping[str, Any]) -> dict[str, Any]:
    """Fit all 660 registered models and freeze all 900 target-blind sets."""

    np = _np()
    _validate_model_stage(model_stage)
    fit = model_stage["fit"]
    final = model_stage["final"]
    fitted: dict[str, dict[str, Any]] = {}
    parameter_updates = 0
    permutation = np.random.default_rng(6842).permutation(26)
    for key in sorted(fit):
        fit_rows = fit[key]
        final_rows = final[key]
        target = fit_rows["fit_targets"]
        eog_fit, eog_final = _eog_residuals(
            fit_rows["whole_features"],
            fit_rows["ocular_features"],
            final_rows["whole_features"],
            final_rows["ocular_features"],
        )
        shuffled = _fixed_train_label_derangement(
            target,
            fit_rows["runs"],
            key=key,
        )
        model_inputs = {
            "whole_head_primary": (fit_rows["whole_features"], target),
            "central_C3_C4_Cz": (fit_rows["central_features"], target),
            "occipital_O1_Oz_O2": (fit_rows["occipital_features"], target),
            "HEOG_VEOG_only": (fit_rows["ocular_features"], target),
            "fit_only_EOG_orthogonalized_primary": (eog_fit, target),
            "early_half": (fit_rows["early_features"], target),
            "late_half": (fit_rows["late_features"], target),
            "pre_window_baseline": (fit_rows["prewindow_features"], target),
            "event_index_and_timing_only": (fit_rows["timing_features"], target),
            "fixed_train_label_derangement_seed_6841": (
                fit_rows["whole_features"],
                shuffled,
            ),
        }
        models = {
            name: _fit_lda(values, labels)
            for name, (values, labels) in model_inputs.items()
        }
        parameter_updates += len(models)
        models["train_only_no_signal_prior"] = _fit_prior(target)
        parameter_updates += 1
        fitted[key] = {
            "models": models,
            "EOG_orthogonalized_final": eog_final,
        }
    predictions: dict[str, dict[str, Any]] = {condition: {} for condition in CONDITION_IDS}
    inference_calls = 0
    for key in sorted(final):
        final_rows = final[key]
        models = fitted[key]["models"]
        direct_inputs = {
            "whole_head_primary": final_rows["whole_features"],
            "central_C3_C4_Cz": final_rows["central_features"],
            "occipital_O1_Oz_O2": final_rows["occipital_features"],
            "HEOG_VEOG_only": final_rows["ocular_features"],
            "fit_only_EOG_orthogonalized_primary": fitted[key][
                "EOG_orthogonalized_final"
            ],
            "early_half": final_rows["early_features"],
            "late_half": final_rows["late_features"],
            "pre_window_baseline": final_rows["prewindow_features"],
            "event_index_and_timing_only": final_rows["timing_features"],
            "fixed_train_label_derangement_seed_6841": final_rows["whole_features"],
            "train_only_no_signal_prior": np.zeros((len(final_rows["item_ids"]), 1)),
        }
        for condition, values in direct_inputs.items():
            predictions[condition][key] = _predict(models[condition], values)
            inference_calls += 1
        primary = models["whole_head_primary"]
        predictions["all_zero_final_EEG_through_primary"][key] = _predict(
            primary,
            np.zeros_like(final_rows["whole_features"]),
        )
        predictions["one_row_cyclic_final_feature_displacement"][key] = _predict(
            primary,
            np.roll(final_rows["whole_features"], 1, axis=0),
        )
        permuted = final_rows["whole_features"].reshape(-1, 26, 5)[:, permutation, :]
        predictions["fixed_final_only_EEG_channel_permutation_seed_6842"][key] = _predict(
            primary,
            permuted.reshape(-1, 130),
        )
        arm, subject, hand = key.split("|", 2)
        opposite_hand = "right" if hand == "left" else "left"
        opposite_key = _prediction_key(arm, _unit(subject, opposite_hand))
        predictions["opposite_hand_primary_without_adaptation"][key] = _predict(
            fitted[opposite_key]["models"]["whole_head_primary"],
            final_rows["whole_features"],
        )
        inference_calls += 4
    prediction_sets = sum(len(values) for values in predictions.values())
    if parameter_updates != 660 or inference_calls != 900 or prediction_sets != 900:
        raise DualReversalRefusal(REFUSAL_IDS[9], "fit or prediction count differs")
    hashes, private_hash = _prediction_hash_summary(
        predictions,
        parameter_updates=parameter_updates,
        prediction_sets=prediction_sets,
    )
    return {
        "predictions": predictions,
        "condition_prediction_sha256": hashes,
        "canonical_private_prediction_sha256": private_hash,
        "parameter_update_fits": parameter_updates,
        "target_blind_inference_calls": inference_calls,
        "prediction_sets": prediction_sets,
    }


def _balanced_accuracy(targets: Any, predictions: Any) -> float:
    np = _np()
    target = np.asarray(targets, dtype="int8")
    prediction = np.asarray(predictions, dtype="int8")
    if target.shape != prediction.shape or target.ndim != 1:
        raise DualReversalRefusal(REFUSAL_IDS[11], "score arrays differ")
    recalls = []
    for label in (0, 1):
        mask = target == label
        if not np.any(mask):
            raise DualReversalRefusal(REFUSAL_IDS[11], "score target lacks a class")
        recalls.append(float(np.mean(prediction[mask] == label)))
    return sum(recalls) / 2.0


def _sign_flip_p(values: Sequence[float]) -> float:
    observed = sum(values) / len(values)
    exceed = 0
    for mask in range(1 << len(values)):
        signed = [value if mask & (1 << index) else -value for index, value in enumerate(values)]
        if sum(signed) / len(signed) >= observed - 1e-15:
            exceed += 1
    return exceed / float(1 << len(values))


def _condition_metrics(
    *,
    arm: str,
    condition: str,
    predictions: Mapping[str, Mapping[str, Any]],
    sealed: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    np = _np()
    participant_action: list[float] = []
    participant_cue: list[float] = []
    pooled_action: list[Any] = []
    pooled_cue: list[Any] = []
    pooled_prediction: list[Any] = []
    for subject_index in range(1, 16):
        subject = f"sub-{subject_index:02d}"
        action_rows = []
        cue_rows = []
        prediction_rows = []
        for hand in ("left", "right"):
            key = _prediction_key(arm, _unit(subject, hand))
            action_rows.append(sealed[key]["actual_action"])
            cue_rows.append(sealed[key]["cue_surrogate"])
            prediction_rows.append(predictions[condition][key])
        action = np.concatenate(action_rows)
        cue = np.concatenate(cue_rows)
        prediction = np.concatenate(prediction_rows)
        participant_action.append(_balanced_accuracy(action, prediction))
        participant_cue.append(_balanced_accuracy(cue, prediction))
        pooled_action.append(action)
        pooled_cue.append(cue)
        pooled_prediction.append(prediction)
    margins = [action - cue for action, cue in zip(participant_action, participant_cue, strict=True)]
    return {
        "pooled_action_balanced_accuracy": _balanced_accuracy(
            np.concatenate(pooled_action), np.concatenate(pooled_prediction)
        ),
        "pooled_cue_balanced_accuracy": _balanced_accuracy(
            np.concatenate(pooled_cue), np.concatenate(pooled_prediction)
        ),
        "macro_participant_action_balanced_accuracy": sum(participant_action) / 15.0,
        "macro_participant_cue_balanced_accuracy": sum(participant_cue) / 15.0,
        "macro_action_minus_cue_margin": sum(margins) / 15.0,
        "participants_above_0_5_action_balanced_accuracy": sum(
            value > 0.5 for value in participant_action
        ),
        "exact_action_minus_cue_sign_flip_p": _sign_flip_p(margins),
        "participant_margins_private": margins,
    }


def route_from_gate_flags(
    *,
    H0: bool,
    cue_bound_both_arms: bool,
    H1_C2I: bool,
    H1_I2C: bool,
    H2: bool,
    H3: bool,
) -> str:
    """Apply the exact ordered IACKD2-R1 through R0 router."""

    if H0 and cue_bound_both_arms:
        return "IACKD2-R1"
    if H0 and (H1_C2I != H1_I2C):
        return "IACKD2-R2"
    if H0 and H1_C2I and H1_I2C and not H2:
        return "IACKD2-R3"
    if H0 and H1_C2I and H1_I2C and H2 and not H3:
        return "IACKD2-R4"
    if H0 and H1_C2I and H1_I2C and H2 and H3:
        return "IACKD2-R5"
    return "IACKD2-R0"


def score_generated_matrix(
    matrix: Mapping[str, Any],
    model_stage: Mapping[str, Any],
    scorer_stage: Mapping[str, Any],
    freeze: Mapping[str, Any],
) -> dict[str, Any]:
    """Open generated targets only after the in-memory hash freeze and score once."""

    _validate_model_stage(model_stage)
    _validate_synthetic_freeze(matrix, model_stage, freeze)
    if (
        set(scorer_stage) != {"sealed", "sealed_rows", "final_item_ids_sha256"}
        or scorer_stage["sealed_rows"] != 960
        or scorer_stage["final_item_ids_sha256"]
        != model_stage["final_item_ids_sha256"]
        or set(scorer_stage["sealed"]) != set(model_stage["final"])
    ):
        raise DualReversalRefusal(REFUSAL_IDS[11], "scorer-stage binding differs")
    predictions = matrix["predictions"]
    sealed = scorer_stage["sealed"]
    np = _np()
    for key in sorted(sealed):
        if not np.array_equal(
            sealed[key]["item_ids"],
            model_stage["final"][key]["item_ids"],
        ):
            raise DualReversalRefusal(REFUSAL_IDS[11], "scorer item IDs differ")
        if not np.array_equal(
            sealed[key]["cue_surrogate"],
            1 - sealed[key]["actual_action"],
        ):
            raise DualReversalRefusal(REFUSAL_IDS[11], "scorer target views differ")
    metrics = {
        arm: {
            condition: _condition_metrics(
                arm=arm,
                condition=condition,
                predictions=predictions,
                sealed=sealed,
            )
            for condition in CONDITION_IDS
        }
        for arm in ("C2I", "I2C")
    }
    H1: dict[str, bool] = {}
    H2: dict[str, bool] = {}
    H3: dict[str, bool] = {}
    for arm in ("C2I", "I2C"):
        primary = metrics[arm]["whole_head_primary"]
        prior = metrics[arm]["train_only_no_signal_prior"]
        H1[arm] = all(
            (
                primary["pooled_action_balanced_accuracy"] >= 0.60,
                primary["macro_participant_action_balanced_accuracy"] >= 0.60,
                primary["participants_above_0_5_action_balanced_accuracy"] >= 12,
                primary["exact_action_minus_cue_sign_flip_p"] <= 0.01,
                primary["macro_action_minus_cue_margin"] >= 0.20,
                primary["macro_participant_cue_balanced_accuracy"] <= 0.40,
                primary["macro_participant_action_balanced_accuracy"]
                - prior["macro_participant_action_balanced_accuracy"]
                >= 0.10,
            )
        )
        eog = metrics[arm]["HEOG_VEOG_only"]
        occipital = metrics[arm]["occipital_O1_Oz_O2"]
        eog_orthogonalized = metrics[arm]["fit_only_EOG_orthogonalized_primary"]
        timing = metrics[arm]["event_index_and_timing_only"]
        prewindow = metrics[arm]["pre_window_baseline"]
        fixed_controls_pass = all(
            metrics[arm][condition]["macro_participant_action_balanced_accuracy"] <= 0.55
            and metrics[arm][condition]["macro_action_minus_cue_margin"] <= 0.10
            for condition in FIXED_CONTROL_IDS
        )
        H2[arm] = all(
            (
                primary["macro_participant_action_balanced_accuracy"]
                - eog["macro_participant_action_balanced_accuracy"]
                >= 0.05,
                primary["macro_participant_action_balanced_accuracy"]
                - occipital["macro_participant_action_balanced_accuracy"]
                >= 0.03,
                eog_orthogonalized["macro_participant_action_balanced_accuracy"] >= 0.58,
                eog_orthogonalized["macro_action_minus_cue_margin"] >= 0.16,
                eog["macro_action_minus_cue_margin"] <= 0.10,
                occipital["macro_action_minus_cue_margin"] <= 0.10,
                timing["macro_participant_action_balanced_accuracy"] <= 0.55,
                prewindow["macro_participant_action_balanced_accuracy"] <= 0.55,
                fixed_controls_pass,
            )
        )
        central = metrics[arm]["central_C3_C4_Cz"]
        H3[arm] = all(
            (
                central["macro_participant_action_balanced_accuracy"] >= 0.55,
                central["macro_action_minus_cue_margin"] >= 0.10,
                central["participants_above_0_5_action_balanced_accuracy"] >= 10,
            )
        )
    participant_minimum_margins = [
        min(c2i, i2c)
        for c2i, i2c in zip(
            metrics["C2I"]["whole_head_primary"]["participant_margins_private"],
            metrics["I2C"]["whole_head_primary"]["participant_margins_private"],
            strict=True,
        )
    ]
    central_minimum_margins = [
        min(c2i, i2c)
        for c2i, i2c in zip(
            metrics["C2I"]["central_C3_C4_Cz"]["participant_margins_private"],
            metrics["I2C"]["central_C3_C4_Cz"]["participant_margins_private"],
            strict=True,
        )
    ]
    conjunction_H1 = (
        sum(participant_minimum_margins) / 15.0 >= 0.15
        and _sign_flip_p(participant_minimum_margins) <= 0.01
    )
    conjunction_H3 = sum(central_minimum_margins) / 15.0 >= 0.08
    H0 = (
        matrix["parameter_update_fits"] == 660
        and matrix["prediction_sets"] == 900
        and model_stage["fit_rows"] == 3136
        and model_stage["final_rows"] == 960
    )
    cue_bound = all(
        metrics[arm]["whole_head_primary"]["macro_participant_cue_balanced_accuracy"]
        >= 0.60
        and metrics[arm]["whole_head_primary"]["macro_action_minus_cue_margin"] <= -0.20
        for arm in ("C2I", "I2C")
    )
    route = route_from_gate_flags(
        H0=H0,
        cue_bound_both_arms=cue_bound,
        H1_C2I=H1["C2I"] and conjunction_H1,
        H1_I2C=H1["I2C"] and conjunction_H1,
        H2=H2["C2I"] and H2["I2C"],
        H3=H3["C2I"] and H3["I2C"] and conjunction_H3,
    )
    public_metrics = {
        arm: {
            condition: {
                key: value
                for key, value in condition_metrics.items()
                if key != "participant_margins_private"
            }
            for condition, condition_metrics in arm_metrics.items()
        }
        for arm, arm_metrics in metrics.items()
    }
    return {
        "synthetic_route": route,
        "H0": H0,
        "H1": H1,
        "H1_conjunction": conjunction_H1,
        "H2": H2,
        "H3": H3,
        "H3_conjunction": conjunction_H3,
        "participant_minimum_arm_margin_mean": sum(participant_minimum_margins) / 15.0,
        "participant_minimum_arm_exact_sign_flip_p": _sign_flip_p(
            participant_minimum_margins
        ),
        "central_minimum_arm_margin_mean": sum(central_minimum_margins) / 15.0,
        "aggregate_metrics": public_metrics,
        "individual_participant_metrics_published": False,
    }


def _route_reachability() -> dict[str, str]:
    cases = {
        "cue_bound": dict(
            H0=True,
            cue_bound_both_arms=True,
            H1_C2I=False,
            H1_I2C=False,
            H2=False,
            H3=False,
        ),
        "asymmetric": dict(
            H0=True,
            cue_bound_both_arms=False,
            H1_C2I=True,
            H1_I2C=False,
            H2=False,
            H3=False,
        ),
        "control_unresolved": dict(
            H0=True,
            cue_bound_both_arms=False,
            H1_C2I=True,
            H1_I2C=True,
            H2=False,
            H3=False,
        ),
        "central_unresolved": dict(
            H0=True,
            cue_bound_both_arms=False,
            H1_C2I=True,
            H1_I2C=True,
            H2=True,
            H3=False,
        ),
        "full_conjunction": dict(
            H0=True,
            cue_bound_both_arms=False,
            H1_C2I=True,
            H1_I2C=True,
            H2=True,
            H3=True,
        ),
        "catch_all": dict(
            H0=False,
            cue_bound_both_arms=False,
            H1_C2I=False,
            H1_I2C=False,
            H2=False,
            H3=False,
        ),
    }
    observed = {name: route_from_gate_flags(**values) for name, values in cases.items()}
    if set(observed.values()) != {
        "IACKD2-R0",
        "IACKD2-R1",
        "IACKD2-R2",
        "IACKD2-R3",
        "IACKD2-R4",
        "IACKD2-R5",
    }:
        raise DualReversalRefusal(REFUSAL_IDS[11], "router reachability differs")
    return observed


def _freeze_record(matrix: Mapping[str, Any], model_stage: Mapping[str, Any]) -> dict[str, Any]:
    _validate_model_stage(model_stage)
    record = {
        "schema_name": "neurodecodekit.iackd_role_aware_dual_reversal_synthetic_freeze",
        "schema_version": SCHEMA_VERSION,
        "source_kind": "generated_source_independent_fixture",
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": semantics.POLICY_SHA256,
        "split_sha256": model_stage["split_sha256"],
        "final_item_ids_sha256": model_stage["final_item_ids_sha256"],
        "condition_prediction_sha256": matrix["condition_prediction_sha256"],
        "canonical_private_prediction_sha256": matrix[
            "canonical_private_prediction_sha256"
        ],
        "parameter_update_fits": matrix["parameter_update_fits"],
        "prediction_sets": matrix["prediction_sets"],
        "final_target_rows_visible_to_model_stage": 0,
        "individual_predictions_published": False,
        "real_or_public_data_reads": 0,
        "scientific_claim": False,
    }
    record["freeze_record_sha256"] = _canonical_sha256(record)
    return record


def _validate_synthetic_freeze(
    matrix: Mapping[str, Any],
    model_stage: Mapping[str, Any],
    freeze: Mapping[str, Any],
) -> None:
    if (
        matrix.get("parameter_update_fits") != 660
        or matrix.get("target_blind_inference_calls") != 900
        or matrix.get("prediction_sets") != 900
    ):
        raise DualReversalRefusal(REFUSAL_IDS[11], "matrix inventory differs at freeze")
    hashes, private_hash = _prediction_hash_summary(
        matrix.get("predictions", {}),
        parameter_updates=matrix["parameter_update_fits"],
        prediction_sets=matrix["prediction_sets"],
    )
    if (
        matrix.get("condition_prediction_sha256") != hashes
        or matrix.get("canonical_private_prediction_sha256") != private_hash
        or dict(freeze) != _freeze_record(matrix, model_stage)
    ):
        raise DualReversalRefusal(REFUSAL_IDS[11], "prediction freeze differs")


def validate_qualification_report(report: Mapping[str, Any]) -> None:
    """Validate a generated-only aggregate report."""

    required = {
        "schema_name",
        "schema_version",
        "status",
        "registration",
        "contract_sha256",
        "policy_sha256",
        "dependencies",
        "streaming_inventory",
        "mock_transport",
        "source_semantics",
        "generated_reader",
        "preprocessing",
        "derivatives",
        "model_matrix",
        "synthetic_freeze",
        "synthetic_score",
        "router_reachability",
        "refusal_coverage",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "claim_boundary",
    }
    if set(report) != required:
        raise DualReversalRefusal(REFUSAL_IDS[14], "report schema differs")
    if (
        report["schema_name"] != REPORT_SCHEMA_NAME
        or report["schema_version"] != SCHEMA_VERSION
        or report["status"] != "passed_generated_fixture_only_no_scientific_result"
    ):
        raise DualReversalRefusal(REFUSAL_IDS[14], "report identity differs")
    if not all(report["acceptance_gates"].values()):
        raise DualReversalRefusal(REFUSAL_IDS[14], "one or more acceptance gates failed")
    forbidden_counters = {
        key: value
        for key, value in report["access_counters"].items()
        if key.startswith("real_")
        or key.startswith("public_")
        or key.startswith("old_")
        or key
        in {
            "network_bytes",
            "provider_or_language_model_calls",
            "hardware_operations",
            "release_operations",
            "scientific_claim_upgrades",
        }
    }
    if not forbidden_counters or any(forbidden_counters.values()):
        raise DualReversalRefusal(REFUSAL_IDS[14], "forbidden access counter is nonzero")
    if "no neural effect" not in report["claim_boundary"]["scientific_claim_not_established"]:
        raise DualReversalRefusal(REFUSAL_IDS[14], "scientific boundary differs")


def run_generated_qualification(
    output_path: str | Path,
    *,
    environ: Mapping[str, str] | None = None,
    maximum_output_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    """Run one bounded generated-only end-to-end IACKD-2 qualification."""

    path = Path(output_path)
    _ensure_output_preflight(path, maximum_output_bytes)
    _check_thread_environment(os.environ if environ is None else environ)
    started = time.monotonic()
    contract = load_registered_contract()
    versions = dependency_versions()
    streaming = validate_streaming_inventory()
    transport = _mock_transport_qualification()
    policy = semantics.load_registered_policy()["policy"]
    semantic_fixtures = [
        semantics.make_generated_fixture(
            include_optional_references=include_optional,
            policy=policy,
        )
        for include_optional in (False, True)
    ]
    semantic_summaries = [
        semantics.validate_generated_fixture(fixture, policy)
        for fixture in semantic_fixtures
    ]
    semantic_mutations = semantics.run_generated_mutation_suite(semantic_fixtures[0], policy)
    generated_reader_rows = []
    generated_input_bytes = 0
    with tempfile.TemporaryDirectory(prefix="iackd2-generated-") as temporary:
        temporary_root = Path(temporary)
        for index, include_optional in enumerate((False, True)):
            fixture = write_generated_brainvision_fixture(
                temporary_root / f"group-{index}",
                include_optional_references=include_optional,
            )
            generated_input_bytes += int(fixture["input_bytes"])
            generated_reader_rows.append(read_and_qualify_generated_brainvision(fixture))
    derivatives = build_generated_derivatives()
    model_stage = derivatives["model_stage"]
    scorer_stage = derivatives["scorer_stage"]
    first_matrix = run_generated_model_matrix(model_stage)
    replay_matrix = run_generated_model_matrix(model_stage)
    deterministic_replay = (
        first_matrix["canonical_private_prediction_sha256"]
        == replay_matrix["canonical_private_prediction_sha256"]
        and first_matrix["condition_prediction_sha256"]
        == replay_matrix["condition_prediction_sha256"]
    )
    if not deterministic_replay:
        raise DualReversalRefusal(REFUSAL_IDS[10], "full model matrix replay differs")
    freeze = _freeze_record(first_matrix, model_stage)
    score = score_generated_matrix(first_matrix, model_stage, scorer_stage, freeze)
    routes = _route_reachability()
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    caps = contract["resource_caps"]["future_generated_implementation"]
    if runtime > caps["wall_time_seconds"] or peak_rss > caps["peak_RSS_bytes"]:
        raise DualReversalRefusal(REFUSAL_IDS[13], "generated qualification exceeded resources")
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_only_no_scientific_result",
        "registration": {
            "commit": REGISTRATION_COMMIT,
            "CI_run_id": REGISTRATION_CI_RUN_ID,
            "base_python_job_id": REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": semantics.POLICY_SHA256,
        "dependencies": versions,
        "streaming_inventory": streaming,
        "mock_transport": transport,
        "source_semantics": {
            "groups": semantic_summaries,
            "mutation_attempts": len(semantic_mutations),
            "distinct_refusal_classes": len(
                {row["refusal_id"] for row in semantic_mutations}
            ),
        },
        "generated_reader": {
            "groups": generated_reader_rows,
            "semantic_parses": 2,
            "BrainVision_parses": 2,
            "real_reader_validated": False,
        },
        "preprocessing": {
            "producer_is_causal_in_samples": True,
            "right_context_seconds": 0.0,
            "end_to_end_latency_measured": False,
            "future_tail_invariance_passed": all(
                row["causal_future_tail_invariant"] for row in generated_reader_rows
            ),
            "dimensions": generated_reader_rows[0]["dimensions"],
        },
        "derivatives": {
            "generated_source_rows": derivatives["generated_source_rows"],
            "fit_rows": model_stage["fit_rows"],
            "final_target_free_rows": model_stage["final_rows"],
            "feature_bytes": derivatives["feature_bytes"],
            "split_sha256": model_stage["split_sha256"],
            "final_item_ids_sha256": model_stage["final_item_ids_sha256"],
            "final_target_fields_visible_to_model_stage": 0,
        },
        "model_matrix": {
            "primary_parameter_update_fits": first_matrix["parameter_update_fits"],
            "primary_target_blind_inference_calls": first_matrix[
                "target_blind_inference_calls"
            ],
            "primary_prediction_sets": first_matrix["prediction_sets"],
            "replay_parameter_update_fits": replay_matrix["parameter_update_fits"],
            "replay_target_blind_inference_calls": replay_matrix[
                "target_blind_inference_calls"
            ],
            "replay_prediction_sets": replay_matrix["prediction_sets"],
            "deterministic_replay": deterministic_replay,
            "canonical_private_prediction_sha256": first_matrix[
                "canonical_private_prediction_sha256"
            ],
            "condition_prediction_sha256": first_matrix[
                "condition_prediction_sha256"
            ],
        },
        "synthetic_freeze": freeze,
        "synthetic_score": score,
        "router_reachability": routes,
        "refusal_coverage": {
            "source_semantics_attempts": len(semantic_mutations),
            "source_semantics_distinct_classes": len(
                {row["refusal_id"] for row in semantic_mutations}
            ),
            "mock_transport_attempts": transport["mutation_attempts"],
            "total_mutation_attempts": len(semantic_mutations)
            + transport["mutation_attempts"],
        },
        "measurements": {
            "committed_contract_input_bytes": (
                _repo_root() / CONTRACT_RELATIVE_PATH
            ).stat().st_size,
            "generated_BrainVision_input_bytes": generated_input_bytes,
            "generated_feature_bytes": derivatives["feature_bytes"],
            "output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
        },
        "access_counters": {
            "committed_contract_reads": 1,
            "committed_inventory_reads": 1,
            "generated_metadata_fixtures": 2,
            "generated_BrainVision_parses": 2,
            "generated_source_rows": derivatives["generated_source_rows"],
            "generated_fit_label_rows": model_stage["fit_rows"],
            "generated_sealed_target_rows": scorer_stage["sealed_rows"],
            "generated_parameter_update_fits": first_matrix["parameter_update_fits"]
            + replay_matrix["parameter_update_fits"],
            "generated_model_inference_calls": first_matrix[
                "target_blind_inference_calls"
            ]
            + replay_matrix["target_blind_inference_calls"],
            "generated_prediction_sets": first_matrix["prediction_sets"]
            + replay_matrix["prediction_sets"],
            "generated_target_deliveries": 1,
            "generated_scoring_runs": 1,
            "real_or_public_metadata_requests": 0,
            "real_payload_requests": 0,
            "real_payload_bytes": 0,
            "old_retained_bundle_operations": 0,
            "public_or_real_signal_sample_reads": 0,
            "public_or_real_event_or_trajectory_reads": 0,
            "public_or_real_target_or_label_reads": 0,
            "real_training_or_parameter_update_runs": 0,
            "real_model_inference_runs": 0,
            "real_prediction_sets": 0,
            "real_target_deliveries": 0,
            "real_scoring_runs": 0,
            "network_bytes": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
            "release_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "green_registration_bound": True,
            "contract_and_policy_hashes_exact": True,
            "streaming_inventory_replayed": True,
            "mock_transport_passed": True,
            "source_semantics_29_and_31_passed": True,
            "generated_BrainVision_reader_passed": True,
            "causal_preprocessing_and_dimensions_passed": True,
            "target_firewall_and_split_counts_passed": True,
            "full_660_fit_900_prediction_matrix_passed": True,
            "deterministic_full_matrix_replay_passed": deterministic_replay,
            "all_six_routes_reachable": len(set(routes.values())) == 6,
            "synthetic_full_conjunction_route_reached": score["synthetic_route"]
            == "IACKD2-R5",
            "forbidden_access_counters_zero": True,
            "resource_caps_passed": True,
            "output_cap_passed": True,
        },
        "warnings": [
            "all signal metadata trajectories labels and outcomes are generated",
            "synthetic IACKD2-R5 has no source or scientific meaning",
            "the real MNE reader public payload and old private bundle remain unvalidated and closed",
            "generated target delivery is an interface test and not a scientific score",
            "end-to-end latency is unavailable",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A generated-only dual-arm reader preprocessing firewall model freeze and "
                "scorer path now exercises the frozen IACKD-2 interfaces deterministically."
            ),
            "scientific_claim_not_established": (
                "No real or public IACKD signal event trajectory target model outcome was "
                "accessed so this establishes no neural effect action decoding brain-specific "
                "origin generalization thought decoding real-time hardware assistive or clinical result."
            ),
        },
    }
    for _ in range(8):
        payload = _json_report_bytes(report)
        if report["measurements"]["output_bytes"] == len(payload):
            break
        report["measurements"]["output_bytes"] = len(payload)
    else:  # pragma: no cover - deterministic fixed-point guard
        raise DualReversalRefusal(REFUSAL_IDS[12], "output byte accounting did not converge")
    validate_qualification_report(report)
    payload = _json_report_bytes(report)
    if len(payload) > maximum_output_bytes:
        raise DualReversalRefusal(REFUSAL_IDS[12], "qualification report exceeds cap")
    _write_exclusive(path, payload)
    return report


def load_qualification_report(path: str | Path) -> dict[str, Any]:
    """Load and strictly validate one generated qualification report."""

    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 8 * 1024 * 1024:
        raise DualReversalRefusal(REFUSAL_IDS[14], "report path is unavailable or oversized")
    value = json.loads(candidate.read_text(encoding="utf-8"))
    validate_qualification_report(value)
    if value["measurements"]["output_bytes"] != candidate.stat().st_size:
        raise DualReversalRefusal(REFUSAL_IDS[14], "report byte count differs")
    return value


def summarize_qualification(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact aggregate-only report summary."""

    validate_qualification_report(report)
    return {
        "status": report["status"],
        "synthetic_route": report["synthetic_score"]["synthetic_route"],
        "primary_parameter_update_fits": report["model_matrix"][
            "primary_parameter_update_fits"
        ],
        "primary_prediction_sets": report["model_matrix"]["primary_prediction_sets"],
        "deterministic_replay": report["model_matrix"]["deterministic_replay"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "output_bytes": report["measurements"]["output_bytes"],
        "producer_is_causal_in_samples": report["preprocessing"][
            "producer_is_causal_in_samples"
        ],
        "end_to_end_latency_measured": report["preprocessing"][
            "end_to_end_latency_measured"
        ],
        "real_or_public_payload_reads": report["access_counters"]["real_payload_requests"],
        "scientific_claim": False,
        "warnings": list(report["warnings"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or qualify the generated-only IACKD-2 dual-reversal interfaces."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--qualify", type=Path, metavar="REPORT_JSON")
    group.add_argument("--inspect", type=Path, metavar="REPORT_JSON")
    parser.add_argument(
        "--maximum-output-bytes",
        type=int,
        default=8 * 1024 * 1024,
        help="Generated report cap; maximum 8 MiB.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.qualify is not None:
        report = run_generated_qualification(
            args.qualify,
            maximum_output_bytes=args.maximum_output_bytes,
        )
        print(json.dumps(summarize_qualification(report), indent=2, sort_keys=True))
        return 0
    if args.inspect is not None:
        print(
            json.dumps(
                summarize_qualification(load_qualification_report(args.inspect)),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    print(json.dumps(registered_plan(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
