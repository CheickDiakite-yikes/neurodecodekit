"""One-shot real executor for the frozen IACKD-2 dual reversal."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import resource
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence

from neurodecodekit.datasets import iackd_cue_action_acquisition as legacy_acquisition
from neurodecodekit.experiments import iackd_cue_action_dissociation as legacy
from neurodecodekit.experiments import iackd_role_aware_dual_reversal as core
from neurodecodekit.preprocess import iackd_source_semantics as semantics


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_contract.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_authorization_decision.v0.json"
)
INVENTORY_RELATIVE_PATH = Path("registries/iackd_openneuro_metadata_inventory.v0.json")
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_real_implementation.v0.json"
)
PUBLIC_RECEIPT_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_acquisition_receipt.v0.json"
)
PUBLIC_FREEZE_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_prediction_freeze.v0.json"
)
PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/iackd_role_aware_dual_reversal_result.v0.json"
)
PRIVATE_ROOT_RELATIVE_PATH = Path(
    ".codex_work/iackd_role_aware_dual_reversal/real_execution_v0"
)
CONTRACT_SHA256 = "f3b38cb2c5bf0a55e0816072ef654cc87bd2e2f36bab50df19947d66d2abdb7f"
DECISION_SHA256 = "e3ad8a2b5310f018c82b7980b047a570d9d5a2958d163ee96c4defee781163c0"
INVENTORY_SHA256 = "aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19"
DECISION_COMMIT = "2ce87fadcbb1ce3fd90d8fab4a48824b19b9fb59"
DECISION_CI_RUN_ID = 31_456_317_734
DECISION_BASE_JOB_ID = 93_670_726_013
DECISION_OPTIONAL_JOB_ID = 93_670_725_945
MAX_LOCKED_JSON_BYTES = 4 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
THREAD_ENV_KEYS = core.THREAD_ENV_KEYS
MODEL_ARRAY_KEYS = (
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
)
REFUSAL_IDS = (
    "IACKD2-F01-evidence_binding_or_green_gate_mismatch",
    "IACKD2-F02-dependency_or_configuration_drift",
    "IACKD2-F03-insufficient_free_disk",
    "IACKD2-F04-old_retained_bundle_access_attempt",
    "IACKD2-F05-metadata_identity_drift",
    "IACKD2-F06-unregistered_object_redirect_retry_or_substitution",
    "IACKD2-F07-path_link_overwrite_or_nonexclusive_root",
    "IACKD2-F08-payload_size_ETag_SHA_or_run_group_cap_failure",
    "IACKD2-F09-source_semantics_role_or_geometry_failure",
    "IACKD2-F10-marker_stream_trial_or_arm_join_failure",
    "IACKD2-F11-motion_guard_or_minimum_count_failure",
    "IACKD2-F12-target_firewall_or_fit_final_partition_leak",
    "IACKD2-F13-fit_or_prediction_inventory_incomplete",
    "IACKD2-F14-resource_or_output_cap_breach",
    "IACKD2-F15-freeze_hash_privacy_or_remote_green_failure",
    "IACKD2-F16-second_delivery_retry_rerun_or_post_target_update",
    "IACKD2-F17-preexisting_path_cleanup_attempt",
    "IACKD2-F18-public_artifact_privacy_failure",
    "IACKD2-F19-claim_boundary_breach",
)


class RealDualReversalRefusal(RuntimeError):
    """Fail before consuming a stage with a stable registered refusal ID."""

    def __init__(self, refusal_id: str, message: str) -> None:
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-2 refusal ID")
        super().__init__(f"{refusal_id}: {message}")
        self.refusal_id = refusal_id
        self.safe_reason = message


class RealDualReversalFailure(RealDualReversalRefusal):
    """Fail closed after the one-shot stage has been consumed."""


@dataclass(frozen=True)
class ImplementationEvidence:
    implementation_commit: str
    implementation_CI_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True)
class FreezeEvidence:
    freeze_commit: str
    freeze_CI_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


class FixtureResponse(io.BytesIO):
    """Small urllib-compatible response used only by mocked transport tests."""

    def __init__(
        self,
        *,
        body: bytes,
        url: str,
        etag: str,
        status: int = 200,
        content_encoding: str | None = None,
        transfer_encoding: str | None = None,
    ) -> None:
        super().__init__(body)
        self.url = url
        self.status = status
        self.headers = {
            "Content-Length": str(len(body)),
            "ETag": f'"{etag}"',
            **(
                {"Content-Encoding": content_encoding}
                if content_encoding is not None
                else {}
            ),
            **(
                {"Transfer-Encoding": transfer_encoding}
                if transfer_encoding is not None
                else {}
            ),
        }

    def geturl(self) -> str:
        return self.url

    def getcode(self) -> int:
        return self.status


URLopener = Callable[[str, int], BinaryIO]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _np():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RealDualReversalRefusal(REFUSAL_IDS[1], "NumPy is unavailable") from exc
    return np


def _signal():
    try:
        from scipy import signal
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RealDualReversalRefusal(REFUSAL_IDS[1], "SciPy is unavailable") from exc
    return signal


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _read_regular_bytes(path: Path, maximum_bytes: int) -> bytes:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "regular input is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "input is not a regular file")
    if observed.st_size < 0 or observed.st_size > maximum_bytes:
        raise RealDualReversalRefusal(REFUSAL_IDS[13], "input exceeds its byte cap")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        chunks = []
        total = 0
        while total <= maximum_bytes:
            chunk = os.read(descriptor, min(CHUNK_BYTES, maximum_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != observed.st_size or len(payload) > maximum_bytes:
        raise RealDualReversalRefusal(REFUSAL_IDS[13], "input changed during read")
    return payload


def _file_sha256(path: Path, maximum_bytes: int = MAX_LOCKED_JSON_BYTES) -> str:
    return _sha256_bytes(_read_regular_bytes(path, maximum_bytes))


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = _read_regular_bytes(path, MAX_LOCKED_JSON_BYTES)
    if _sha256_bytes(payload) != expected_sha256:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "locked JSON hash differs")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "locked JSON is malformed") from exc
    if not isinstance(value, dict):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "locked JSON root is not an object")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if (
        contract.get("schema_name")
        != "neurodecodekit.iackd_role_aware_dual_reversal_contract"
        or contract.get("contract_id")
        != "IACKD-2-role-aware-dual-reversal-contract-v0"
        or contract.get("fit_inventory", {}).get("required_parameter_update_fits")
        != 660
        or contract.get("prediction_inventory", {}).get("required_prediction_sets")
        != 900
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "contract invariants differ")
    return contract


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if (
        decision.get("schema_name")
        != "neurodecodekit.iackd_role_aware_dual_reversal_authorization_decision"
        or decision.get("authorization_parent_commit")
        != "862141f6729182f36accce38ce42a3631feb7232"
        or decision.get("user_authorization", {}).get("actual_message_verbatim")
        != "continue"
        or decision.get("green_request", {}).get("both_required_jobs_green") is not True
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "decision invariants differ")
    return decision


def load_registered_inventory(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    inventory = _load_locked_json(root / INVENTORY_RELATIVE_PATH, INVENTORY_SHA256)
    if (
        inventory.get("schema_name")
        != "neurodecodekit.iackd_openneuro_metadata_inventory"
        or len(inventory.get("selected_objects", ())) != 1340
        or inventory.get("selection", {}).get("selected_payload_bytes")
        != 7_249_113_684
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "inventory invariants differ")
    return inventory


def dependency_versions() -> dict[str, str]:
    expected = load_registered_contract()["dependency_contract"]["versions"]
    packages = {
        "numpy": "numpy",
        "scipy": "scipy",
        "mne": "mne",
        "scikit_learn": "scikit-learn",
    }
    observed = {name: metadata.version(package) for name, package in packages.items()}
    if observed != expected:
        raise RealDualReversalRefusal(
            REFUSAL_IDS[1], f"optional dependency versions differ: {observed!r}"
        )
    return observed


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    drift = {name: environ.get(name) for name in THREAD_ENV_KEYS if environ.get(name) != "1"}
    if drift:
        raise RealDualReversalRefusal(
            REFUSAL_IDS[1], f"one-thread environment differs: {drift!r}"
        )


def _safe_relative_path(value: str) -> Path:
    candidate = Path(value)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "relative path is unsafe")
    return candidate


def _assert_safe_path_chain(root: Path, path: Path) -> None:
    root = root.resolve()
    try:
        relative = path.absolute().relative_to(root)
    except ValueError as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "path escapes workspace root") from exc
    current = root
    if current.is_symlink() or not current.is_dir():
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "workspace root is not regular")
    for part in relative.parts[:-1]:
        current = current / part
        if not current.exists():
            break
        observed = os.lstat(current)
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
            raise RealDualReversalRefusal(REFUSAL_IDS[6], "path parent is not regular")


def _write_exclusive(path: Path, payload: bytes, maximum_bytes: int) -> int:
    if len(payload) > maximum_bytes:
        raise RealDualReversalRefusal(REFUSAL_IDS[13], "output exceeds its byte cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "exclusive output exists") from exc
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    return len(payload)


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def _deterministic_npz_bytes(values: Mapping[str, Any]) -> bytes:
    np = _np()
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for name in sorted(values):
            if not re.fullmatch(r"[A-Za-z0-9_]+", name):
                raise RealDualReversalRefusal(REFUSAL_IDS[11], "NPZ key is unsafe")
            array_output = io.BytesIO()
            np.lib.format.write_array(
                array_output,
                np.asarray(values[name]),
                allow_pickle=False,
            )
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, array_output.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return output.getvalue()


def _load_npz(path: Path, maximum_bytes: int) -> dict[str, Any]:
    np = _np()
    payload = _read_regular_bytes(path, maximum_bytes)
    try:
        with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
            return {name: archive[name] for name in archive.files}
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "private derivative is malformed") from exc


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact real-execution plan without local path stats or network."""

    contract = load_registered_contract(repo_root)
    load_registered_decision(repo_root)
    return {
        "schema_name": "neurodecodekit.iackd_role_aware_dual_reversal_real_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_public_request_no_local_IACKD_path_operation",
        "decision_commit": DECISION_COMMIT,
        "decision_CI_run_id": DECISION_CI_RUN_ID,
        "object_count": contract["dataset_binding"]["selected_object_count"],
        "payload_bytes": contract["dataset_binding"]["selected_payload_bytes"],
        "run_groups": contract["fresh_streaming_contract"]["run_group_count"],
        "fits": contract["fit_inventory"]["required_parameter_update_fits"],
        "prediction_sets": contract["prediction_inventory"]["required_prediction_sets"],
        "old_retained_bundle_operations": 0,
        "real_or_public_operations": 0,
        "next_gate": "exact_real_executor_implementation_must_be_remotely_green",
        "scientific_claim": False,
    }


def _run_key(row: Mapping[str, Any]) -> str | None:
    return core._run_key_from_inventory(row)


def _group_inventory(
    inventory: Mapping[str, Any],
    *,
    expected_groups: int,
    expected_objects_per_group: int,
    expected_geometry: int,
) -> tuple[list[tuple[str, list[dict[str, Any]]]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    geometry = []
    for raw in inventory.get("selected_objects", ()):
        row = dict(raw)
        _safe_relative_path(str(row.get("path", "")))
        key = _run_key(row)
        if key is None:
            geometry.append(row)
        else:
            groups.setdefault(key, []).append(row)
    ordered = [
        (key, sorted(rows, key=lambda row: str(row["path"])))
        for key, rows in sorted(groups.items())
    ]
    if (
        len(ordered) != expected_groups
        or any(len(rows) != expected_objects_per_group for _, rows in ordered)
        or len(geometry) != expected_geometry
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "streaming inventory differs")
    for _, rows in ordered:
        roles = [str(row["role"]) for row in rows]
        if len(set(roles)) != expected_objects_per_group:
            raise RealDualReversalRefusal(REFUSAL_IDS[0], "run roles are not unique")
    return ordered, sorted(geometry, key=lambda row: str(row["path"]))


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise RealDualReversalFailure(REFUSAL_IDS[5], "redirect is forbidden")


def _open_url_once(url: str, maximum_bytes: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NeuroDecodeKit-IACKD2/0.1", "Accept-Encoding": "identity"},
        method="GET",
    )
    response = urllib.request.build_opener(_RejectRedirect).open(request, timeout=120)
    length = response.headers.get("Content-Length")
    if length is not None and int(length) > maximum_bytes:
        response.close()
        raise RealDualReversalFailure(REFUSAL_IDS[7], "response exceeds byte cap")
    return response


@contextmanager
def _managed_stream(stream: BinaryIO) -> Iterator[BinaryIO]:
    try:
        yield stream
    finally:
        stream.close()


def _header(stream: BinaryIO, name: str) -> str | None:
    headers = getattr(stream, "headers", None)
    return None if headers is None else headers.get(name)


def _response_url(stream: BinaryIO) -> str | None:
    getter = getattr(stream, "geturl", None)
    return str(getter()) if callable(getter) else None


def _response_status(stream: BinaryIO) -> int | None:
    status = getattr(stream, "status", None)
    if status is not None:
        return int(status)
    getter = getattr(stream, "getcode", None)
    return int(getter()) if callable(getter) else None


def _normalized_etag(value: str) -> str:
    return value.strip().strip('"').lower()


def _validate_response(
    stream: BinaryIO,
    *,
    url: str,
    expected_bytes: int,
    expected_etag: str | None,
) -> None:
    if _response_status(stream) != 200 or _response_url(stream) != url:
        raise RealDualReversalFailure(REFUSAL_IDS[5], "response status or URL differs")
    content_length = _header(stream, "Content-Length")
    if content_length is None or int(content_length) != expected_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[7], "Content-Length differs")
    if _header(stream, "Content-Encoding") not in {None, "", "identity"}:
        raise RealDualReversalFailure(REFUSAL_IDS[5], "content encoding is not identity")
    if _header(stream, "Transfer-Encoding") not in {None, ""}:
        raise RealDualReversalFailure(REFUSAL_IDS[5], "transfer encoding is forbidden")
    if expected_etag is not None:
        observed_etag = _header(stream, "ETag")
        if observed_etag is None or _normalized_etag(observed_etag) != expected_etag:
            raise RealDualReversalFailure(REFUSAL_IDS[7], "ETag differs")


def _read_exact_response(
    stream: BinaryIO,
    *,
    expected_bytes: int,
    maximum_bytes: int,
) -> bytes:
    if expected_bytes > maximum_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "expected body exceeds cap")
    body = stream.read(expected_bytes + 1)
    if len(body) != expected_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[7], "response body length differs")
    return body


def _validate_metadata_documents(
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    bodies: Sequence[bytes],
) -> dict[str, Any]:
    if len(bodies) != 4:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "metadata body count differs")
    source = inventory["source_documents"]
    snapshot = inventory["listing_snapshot"]
    expected_hashes = (
        source["dataset_description"]["sha256"],
        source["changes"]["sha256"],
        snapshot["pages"][0]["body_sha256"],
        snapshot["pages"][1]["body_sha256"],
    )
    if tuple(_sha256_bytes(body) for body in bodies) != expected_hashes:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "metadata body hash differs")
    try:
        description = json.loads(bodies[0].decode("utf-8"))
        changes = bodies[1].decode("utf-8")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "metadata body is malformed") from exc
    binding = contract["dataset_binding"]
    if (
        description.get("BIDSVersion") != binding["bids_version"]
        or description.get("License") != binding["license"]
        or str(description.get("DatasetDOI", "")).removeprefix("doi:")
        != binding["dataset_doi"]
        or binding["version"] not in changes
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[4], "dataset identity differs")
    try:
        first, first_truncated, _ = legacy_acquisition._listing_objects(bodies[2])
        second, second_truncated, _ = legacy_acquisition._listing_objects(bodies[3])
    except legacy_acquisition.IACKDAcquisitionFailure as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "object listing is malformed") from exc
    listed = [*first, *second]
    metadata_contract = contract["metadata_reverification"]
    if (
        not first_truncated
        or second_truncated
        or len(listed) != metadata_contract["expected_listed_object_count"]
        or sum(int(row["size_bytes"]) for row in listed)
        != metadata_contract["expected_listed_total_bytes"]
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[4], "object listing identity differs")
    selected = [
        {
            "path": str(row["path"]),
            "size_bytes": int(row["size_bytes"]),
            "etag": str(row["etag"]),
            "last_modified": str(row["last_modified"]),
        }
        for row in sorted(inventory["selected_objects"], key=lambda row: str(row["path"]))
    ]
    listed_by_path = {str(row["path"]): row for row in listed}
    if [listed_by_path.get(row["path"]) for row in selected] != selected:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "selected object identity drifted")
    identity_bytes, identity_sha256 = legacy_acquisition._canonical_identity(selected)
    if identity_sha256 != metadata_contract["canonical_identity_sha256"]:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "canonical selected identity differs")
    return {
        "metadata_requests": 4,
        "metadata_body_bytes": sum(len(body) for body in bodies),
        "listed_object_count": len(listed),
        "listed_total_bytes": sum(int(row["size_bytes"]) for row in listed),
        "selected_object_count": len(selected),
        "selected_payload_bytes": sum(row["size_bytes"] for row in selected),
        "canonical_identity_bytes": identity_bytes,
        "canonical_identity_sha256": identity_sha256,
    }


def _fetch_metadata(
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    opener: URLopener,
) -> dict[str, Any]:
    cap = int(
        contract["resource_caps"]["future_acquisition_and_derivative_build"][
            "metadata_body_bytes"
        ]
    )
    source = inventory["source_documents"]
    snapshot = inventory["listing_snapshot"]
    first_url = f"{snapshot['endpoint']}?{snapshot['query']}"
    urls = [
        source["dataset_description"]["url"],
        source["changes"]["url"],
        first_url,
    ]
    expected_sizes = [
        int(source["dataset_description"]["bytes"]),
        int(source["changes"]["bytes"]),
        int(snapshot["pages"][0]["body_bytes"]),
    ]
    bodies = []
    for url, expected in zip(urls, expected_sizes, strict=True):
        with _managed_stream(opener(url, min(cap, expected))) as stream:
            _validate_response(
                stream,
                url=url,
                expected_bytes=expected,
                expected_etag=None,
            )
            bodies.append(
                _read_exact_response(stream, expected_bytes=expected, maximum_bytes=cap)
            )
    _, truncated, token = legacy_acquisition._listing_objects(bodies[2])
    if not truncated or not token:
        raise RealDualReversalFailure(REFUSAL_IDS[4], "first listing lacks continuation")
    second_url = f"{first_url}&continuation-token={urllib.parse.quote(token, safe='')}"
    second_size = int(snapshot["pages"][1]["body_bytes"])
    with _managed_stream(opener(second_url, second_size)) as stream:
        _validate_response(
            stream,
            url=second_url,
            expected_bytes=second_size,
            expected_etag=None,
        )
        bodies.append(
            _read_exact_response(stream, expected_bytes=second_size, maximum_bytes=cap)
        )
    result = _validate_metadata_documents(contract, inventory, bodies)
    if result["metadata_body_bytes"] > cap:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "metadata byte cap exceeded")
    return result


def _object_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{urllib.parse.quote(path, safe='/._-')}"


def _download_object(
    *,
    row: Mapping[str, Any],
    destination: Path,
    base_url: str,
    opener: URLopener,
) -> dict[str, Any]:
    expected_bytes = int(row["size_bytes"])
    expected_etag = str(row["etag"]).lower()
    url = _object_url(base_url, str(row["path"]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[6], "payload destination exists") from exc
    sha256 = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)  # noqa: S324 - source ETag integrity only
    observed_bytes = 0
    try:
        with _managed_stream(opener(url, expected_bytes)) as stream:
            _validate_response(
                stream,
                url=url,
                expected_bytes=expected_bytes,
                expected_etag=expected_etag,
            )
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                while True:
                    remaining = expected_bytes - observed_bytes
                    chunk = stream.read(min(CHUNK_BYTES, remaining + 1))
                    if not chunk:
                        break
                    observed_bytes += len(chunk)
                    if observed_bytes > expected_bytes:
                        raise RealDualReversalFailure(
                            REFUSAL_IDS[7], "payload exceeds registered size"
                        )
                    sha256.update(chunk)
                    md5.update(chunk)
                    handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    if observed_bytes != expected_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[7], "payload ended before registered size")
    if re.fullmatch(r"[0-9a-f]{32}", expected_etag) and md5.hexdigest() != expected_etag:
        raise RealDualReversalFailure(REFUSAL_IDS[7], "payload body differs from ETag")
    return {
        "path": str(row["path"]),
        "role": str(row["role"]),
        "size_bytes": observed_bytes,
        "etag": expected_etag,
        "sha256": sha256.hexdigest(),
        "SHA256_passes": 1,
        "semantic_parse_passes": 0,
    }


def _decode_utf8(payload: bytes, name: str) -> str:
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[8], f"{name} is not UTF-8") from exc


def _geometry_identity(path: str) -> tuple[str, str]:
    match = re.search(
        r"(?P<subject>sub-[0-9]{2})_acq-(?P<hand>left|right)_space-CapTrak_",
        path,
    )
    if match is None:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "geometry identity is malformed")
    return match["subject"], match["hand"]


def _parse_geometry_pair(
    electrode_payload: bytes,
    coordinate_payload: bytes,
) -> dict[str, tuple[float, float, float]]:
    try:
        coordinate = json.loads(_decode_utf8(coordinate_payload, "coordinate sidecar"))
    except json.JSONDecodeError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "coordinate sidecar is malformed") from exc
    if not isinstance(coordinate, dict):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "coordinate sidecar is not an object")
    unit = str(coordinate.get("EEGCoordinateUnits", ""))
    scales = {"m": 1.0, "cm": 0.01, "mm": 0.001}
    if unit not in scales:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "coordinate unit is unavailable")
    reader = csv.DictReader(io.StringIO(_decode_utf8(electrode_payload, "electrodes")), delimiter="\t")
    if not reader.fieldnames or not {"name", "x", "y", "z"}.issubset(reader.fieldnames):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "electrode schema differs")
    result: dict[str, tuple[float, float, float]] = {}
    seen = set()
    unavailable = {"", "n/a", "na", "none", "null"}
    for row in reader:
        name = str(row["name"]).strip()
        normalized = name.casefold()
        if not name or normalized in seen:
            raise RealDualReversalFailure(REFUSAL_IDS[8], "electrode names differ")
        seen.add(normalized)
        raw_xyz = [str(row[field]).strip() for field in ("x", "y", "z")]
        unavailable_mask = [value.casefold() in unavailable for value in raw_xyz]
        if all(unavailable_mask):
            continue
        if any(unavailable_mask):
            raise RealDualReversalFailure(
                REFUSAL_IDS[8], "electrode coordinate is partly unavailable"
            )
        try:
            xyz = tuple(float(value) * scales[unit] for value in raw_xyz)
        except (TypeError, ValueError) as exc:
            raise RealDualReversalFailure(REFUSAL_IDS[8], "electrode coordinate differs") from exc
        if not all(math.isfinite(value) for value in xyz):
            raise RealDualReversalFailure(REFUSAL_IDS[8], "electrode coordinate is nonfinite")
        result[normalized] = xyz
    if not result:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "electrode table is empty")
    return result


def _channel_table(payload: bytes) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(_decode_utf8(payload, "channels TSV")), delimiter="\t")
    if not reader.fieldnames or not {"name", "type", "units"}.issubset(reader.fieldnames):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "channel table schema differs")
    rows = []
    seen = set()
    for row in reader:
        name = str(row["name"]).strip()
        channel_type = str(row["type"]).strip()
        normalized = name.casefold()
        if not name or normalized in seen or channel_type not in {"EEG", "MISC"}:
            raise RealDualReversalFailure(REFUSAL_IDS[8], "channel declaration differs")
        seen.add(normalized)
        rows.append({"name": name, "type": channel_type})
    if len(rows) not in {29, 31}:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "channel row count differs")
    return rows


def _sidecar_semantics(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(_decode_utf8(payload, "EEG sidecar"))
    except json.JSONDecodeError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "EEG sidecar is malformed") from exc
    if not isinstance(value, dict):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "EEG sidecar is not an object")
    fields = (
        "EEGChannelCount",
        "EOGChannelCount",
        "ECGChannelCount",
        "EMGChannelCount",
        "MiscChannelCount",
        "TriggerChannelCount",
        "SamplingFrequency",
        "EEGReference",
    )
    if any(field not in value for field in fields):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "EEG sidecar semantics differ")
    return {field: value[field] for field in fields}


def _source_semantics(
    *,
    channel_payload: bytes,
    sidecar_payload: bytes,
    geometry: Mapping[str, tuple[float, float, float]],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    rows = _channel_table(channel_payload)
    fixture_rows = []
    for index, row in enumerate(rows):
        normalized = row["name"].casefold()
        fixture_rows.append(
            {
                "name": row["name"],
                "type": row["type"],
                "source_index": index,
                "geometry_m": (
                    list(geometry[normalized])
                    if normalized in geometry
                    else None
                ),
            }
        )
    fixture = {
        "schema_name": semantics.FIXTURE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "private-real-source-declaration",
        "dataset": {"BIDSVersion": "1.7.0"},
        "channels": fixture_rows,
        "eeg_sidecar": _sidecar_semantics(sidecar_payload),
        "expected_bindings": {
            field: "" for field in semantics.EXPECTED_BINDING_FIELDS
        },
    }
    policy = semantics.load_registered_policy()["policy"]
    try:
        projected = semantics.validate_generated_fixture(
            fixture,
            policy,
            check_bindings=False,
        )
        fixture["expected_bindings"] = projected["bindings"]
        summary = semantics.validate_generated_fixture(fixture, policy)
    except semantics.SourceSemanticsRefusal as exc:
        raise RealDualReversalFailure(
            REFUSAL_IDS[8], "source-declared channel policy failed"
        ) from exc
    return summary, rows


def _paths_by_role(group_root: Path, rows: Sequence[Mapping[str, Any]]) -> dict[str, Path]:
    expected = {
        "eeg_signal",
        "eeg_header",
        "eeg_marker",
        "eeg_sidecar",
        "events",
        "channels",
        "ball_stream",
        "ball_sidecar",
        "leap_stream",
        "leap_sidecar",
    }
    observed = {str(row["role"]) for row in rows}
    if observed != expected:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "run role set differs")
    return {
        str(row["role"]): group_root / _safe_relative_path(str(row["path"]))
        for row in rows
    }


def _read_text_once(path: Path, maximum_bytes: int = 32 * 1024 * 1024) -> str:
    return _decode_utf8(_read_regular_bytes(path, maximum_bytes), path.name)


def _read_json_once(path: Path, maximum_bytes: int = 1024 * 1024) -> dict[str, Any]:
    try:
        value = json.loads(_read_text_once(path, maximum_bytes))
    except json.JSONDecodeError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[9], "stream sidecar is malformed") from exc
    if not isinstance(value, dict):
        raise RealDualReversalFailure(REFUSAL_IDS[9], "stream sidecar is not an object")
    return value


def _map_legacy_failure(exc: Exception, refusal_id: str, message: str):
    raise RealDualReversalFailure(refusal_id, message) from exc


def _extract_feature_rows(
    *,
    subject: str,
    hand: str,
    run: str,
    sampling_rate_hz: float,
    source_names: Sequence[str],
    values: Any,
    trials: Sequence[legacy.TrialRecord],
    semantic_summary: Mapping[str, Any],
) -> dict[str, Any]:
    np = _np()
    signal = _signal()
    if not math.isclose(sampling_rate_hz, 1024.0, rel_tol=0.0, abs_tol=1e-9):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "sampling rate differs")
    matrix = np.asarray(values, dtype="float64")
    if matrix.shape[0] != len(source_names) or not np.isfinite(matrix).all():
        raise RealDualReversalFailure(REFUSAL_IDS[8], "signal matrix differs")
    normalized = {name.casefold(): index for index, name in enumerate(source_names)}
    predictive_names = list(semantic_summary["predictive_output_order"])
    try:
        predictive_indices = [normalized[name.casefold()] for name in predictive_names]
        ocular_indices = [normalized[name.casefold()] for name in ("HEOG", "VEOG")]
    except KeyError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[8], "required channel is unavailable") from exc
    central_indices = [predictive_names.index(name) for name in ("C3", "C4", "Cz")]
    occipital_indices = [predictive_names.index(name) for name in ("O1", "Oz", "O2")]
    predictive = matrix[predictive_indices]
    predictive = predictive - predictive.mean(axis=0, keepdims=True)
    ocular = matrix[ocular_indices]
    low_sos = signal.butter(4, (0.5, 4.0), btype="bandpass", fs=1024.0, output="sos")
    filtered = signal.sosfilt(low_sos, predictive, axis=1)
    filtered_ocular = signal.sosfilt(low_sos, ocular, axis=1)
    mu_sos = signal.butter(4, (8.0, 13.0), btype="bandpass", fs=1024.0, output="sos")
    beta_sos = signal.butter(4, (13.0, 30.0), btype="bandpass", fs=1024.0, output="sos")
    central_signal = predictive[central_indices]
    mu = signal.sosfilt(mu_sos, central_signal, axis=1)
    beta = signal.sosfilt(beta_sos, central_signal, axis=1)
    output: dict[str, list[Any]] = {
        key: []
        for key in (
            *MODEL_ARRAY_KEYS,
            "conditions",
            "actual_action",
            "visual_action",
            "readiness_traces",
            "motion_guard_milliseconds",
        )
    }
    exclusions: dict[str, int] = {}
    for trial in trials:
        try:
            if not trial.event_55_seconds < trial.event_14_seconds < trial.boundary_seconds:
                raise legacy.IACKDFailure("marker", "marker order differs")
            stop, guard_ms = legacy._motion_onset(trial)
            main_slice = legacy._sample_slice(stop - 1.0, stop, 1024.0, matrix.shape[1])
            pre_slice = legacy._sample_slice(stop - 2.0, stop - 1.0, 1024.0, matrix.shape[1])
            leap_x = np.asarray(trial.leap_xyz_mm, dtype="float64")[:, 0]
            actual = legacy._direction(leap_x, 5.0)
            visual = legacy._direction(trial.ball_x_pixels, 5.0)
            if legacy._move_direct(trial.ball_move_direct) != visual:
                raise legacy.IACKDFailure("target", "ball direction differs")
            condition = trial.condition.strip().lower()
            if condition == "red" and actual != visual:
                raise legacy.IACKDFailure("target", "red relation differs")
            if condition == "yellow" and actual == visual:
                raise legacy.IACKDFailure("target", "yellow relation differs")
            if condition not in {"red", "yellow"}:
                raise legacy.IACKDFailure("trial", "condition differs")
            main = filtered[:, main_slice]
            midpoint = main.shape[1] // 2
            central_window = main[central_indices]
            item_id = _sha256_bytes(
                f"{subject}|{hand}|{run}|{trial.trial_id}".encode("utf-8")
            )
            values_by_key = {
                "item_ids": item_id,
                "subjects": subject,
                "hands": hand,
                "runs": run,
                "whole_features": core._feature_row(main),
                "central_features": core._feature_row(main[central_indices]),
                "occipital_features": core._feature_row(main[occipital_indices]),
                "ocular_features": core._feature_row(filtered_ocular[:, main_slice]),
                "early_features": core._half_feature_row(main[:, :midpoint]),
                "late_features": core._half_feature_row(main[:, midpoint:]),
                "prewindow_features": core._feature_row(filtered[:, pre_slice]),
                "timing_features": np.asarray(
                    [
                        float(int(run)),
                        float(trial.event_index),
                        trial.event_14_seconds - trial.event_55_seconds,
                        stop - trial.event_55_seconds,
                    ],
                    dtype="float32",
                ),
                "physiology_features": np.asarray(
                    [
                        *central_window.mean(axis=1).tolist(),
                        float(np.mean(mu[:, main_slice] ** 2)),
                        float(np.mean(beta[:, main_slice] ** 2)),
                        float(
                            central_window[:, midpoint:].mean()
                            - central_window[:, :midpoint].mean()
                        ),
                        guard_ms,
                    ],
                    dtype="float32",
                ),
            }
            for key, value in values_by_key.items():
                output[key].append(value)
            output["conditions"].append(condition)
            output["actual_action"].append(actual)
            output["visual_action"].append(visual)
            output["readiness_traces"].append(central_window.astype("float32"))
            output["motion_guard_milliseconds"].append(guard_ms)
        except legacy.IACKDFailure as exc:
            if exc.stage == "target":
                _map_legacy_failure(exc, REFUSAL_IDS[9], "target relation differs")
            exclusions[exc.stage] = exclusions.get(exc.stage, 0) + 1
    if not output["item_ids"]:
        raise RealDualReversalFailure(REFUSAL_IDS[10], "run retained no trial")
    arrays: dict[str, Any] = {
        "item_ids": np.asarray(output["item_ids"], dtype="U64"),
        "subjects": np.asarray(output["subjects"], dtype="U8"),
        "hands": np.asarray(output["hands"], dtype="U5"),
        "runs": np.asarray(output["runs"], dtype="U2"),
        "conditions": np.asarray(output["conditions"], dtype="U6"),
        "actual_action": np.asarray(output["actual_action"], dtype="int8"),
        "visual_action": np.asarray(output["visual_action"], dtype="int8"),
        "readiness_traces": np.asarray(output["readiness_traces"], dtype="float32"),
        "motion_guard_milliseconds": np.asarray(
            output["motion_guard_milliseconds"], dtype="float32"
        ),
    }
    for key in MODEL_ARRAY_KEYS[4:]:
        arrays[key] = np.asarray(output[key], dtype="float32")
    arrays["exclusions"] = exclusions
    return arrays


def _read_run_group(
    *,
    group_key: str,
    group_root: Path,
    rows: Sequence[Mapping[str, Any]],
    geometry: Mapping[tuple[str, str], Mapping[str, tuple[float, float, float]]],
) -> dict[str, Any]:
    try:
        import mne
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RealDualReversalFailure(REFUSAL_IDS[1], "MNE is unavailable") from exc
    subject, hand, run = group_key.split(":", 2)
    paths = _paths_by_role(group_root, rows)
    raw = None
    try:
        channel_payload = _read_regular_bytes(paths["channels"], 1024 * 1024)
        sidecar_payload = _read_regular_bytes(paths["eeg_sidecar"], 1024 * 1024)
        semantic_summary, channel_rows = _source_semantics(
            channel_payload=channel_payload,
            sidecar_payload=sidecar_payload,
            geometry=geometry[(subject, hand)],
        )
        raw = mne.io.read_raw_brainvision(
            paths["eeg_header"],
            preload=True,
            verbose="ERROR",
        )
        source_names = [row["name"] for row in channel_rows]
        if raw.ch_names != source_names:
            raise RealDualReversalFailure(REFUSAL_IDS[8], "VHDR and channel order differ")
        if not math.isclose(float(raw.info["sfreq"]), 1024.0, rel_tol=0.0, abs_tol=1e-9):
            raise RealDualReversalFailure(REFUSAL_IDS[8], "reader sampling rate differs")
        event_trials = legacy.parse_events_tsv(_read_text_once(paths["events"]))
        annotation_trials = legacy._annotation_trials(raw)
        legacy._compare_annotation_trials(event_trials, annotation_trials, 1024.0)
        ball_scale = legacy._stream_scales(
            _read_json_once(paths["ball_sidecar"]), kind="ball"
        )
        leap_scale = legacy._stream_scales(
            _read_json_once(paths["leap_sidecar"]), kind="leap"
        )
        ball = legacy._stream_groups(
            _read_text_once(paths["ball_stream"]),
            kind="ball",
            time_scale_to_seconds=ball_scale[0],
            position_scale=ball_scale[1],
        )
        leap = legacy._stream_groups(
            _read_text_once(paths["leap_stream"]),
            kind="leap",
            time_scale_to_seconds=leap_scale[0],
            position_scale=leap_scale[1],
        )
        trials = legacy.reconcile_trials(event_trials, ball, leap)
        values = raw.get_data()
    except legacy.IACKDFailure as exc:
        _map_legacy_failure(exc, REFUSAL_IDS[9], "marker or stream reconciliation failed")
    finally:
        if raw is not None:
            raw.close()
    features = _extract_feature_rows(
        subject=subject,
        hand=hand,
        run=run,
        sampling_rate_hz=1024.0,
        source_names=source_names,
        values=values,
        trials=trials,
        semantic_summary=semantic_summary,
    )
    features["semantic_summary"] = semantic_summary
    return features


def _model_rows(arrays: Mapping[str, Any], mask: Any) -> dict[str, Any]:
    return {key: arrays[key][mask] for key in MODEL_ARRAY_KEYS}


def _prefixed_arrays(prefix: str, rows: Mapping[str, Any]) -> dict[str, Any]:
    return {f"{prefix}_{key}": value for key, value in rows.items()}


def _build_run_shards(
    *,
    arrays: Mapping[str, Any],
    split: str,
    source_binding_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]:
    np = _np()
    model_payload: dict[str, Any] = {
        "source_binding_sha256": np.asarray(source_binding_sha256, dtype="U64")
    }
    sealed_payload: dict[str, Any] = {}
    counts: dict[str, int] = {}
    for arm in core.ARM_ROWS:
        arm_id = str(arm["arm_id"])
        condition = str(
            arm["fit_condition"] if split == "fit" else arm["final_condition"]
        )
        mask = arrays["conditions"] == condition
        selected = _model_rows(arrays, mask)
        prefix = f"{arm_id}_{split}"
        model_payload.update(_prefixed_arrays(prefix, selected))
        count = len(selected["item_ids"])
        counts[f"{arm_id}_{split}_rows"] = count
        if split == "fit":
            actual = arrays["actual_action"][mask]
            visual = arrays["visual_action"][mask]
            expected_equal = int(arm["fit_action_to_visual_sign"]) == 1
            if not np.all((actual == visual) == expected_equal):
                raise RealDualReversalFailure(REFUSAL_IDS[9], "fit arm relation differs")
            model_payload[f"{prefix}_fit_targets"] = actual
        else:
            actual = arrays["actual_action"][mask]
            visual = arrays["visual_action"][mask]
            cue = visual if int(arm["fit_action_to_visual_sign"]) == 1 else 1 - visual
            if not np.array_equal(cue, 1 - actual):
                raise RealDualReversalFailure(REFUSAL_IDS[11], "final target views differ")
            sealed_payload[f"{arm_id}_item_ids"] = selected["item_ids"]
            sealed_payload[f"{arm_id}_actual_action"] = actual
            sealed_payload[f"{arm_id}_cue_surrogate"] = cue
    physiology_payload = {
        "item_ids": arrays["item_ids"],
        "readiness_traces": arrays["readiness_traces"],
        "physiology_features": arrays["physiology_features"],
        "motion_guard_milliseconds": arrays["motion_guard_milliseconds"],
    }
    return model_payload, sealed_payload or None, {
        **counts,
        "retained_source_trials": len(arrays["item_ids"]),
        "exclusions": dict(arrays["exclusions"]),
        "motion_guard_minimum_milliseconds": float(
            arrays["motion_guard_milliseconds"].min()
        ),
        "physiology_payload": physiology_payload,
    }


def _remove_invocation_group(root: Path, group: Path) -> None:
    try:
        group.absolute().relative_to(root.absolute())
    except ValueError as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[16], "cleanup path escapes invocation") from exc
    if group.is_symlink() or not group.is_dir():
        raise RealDualReversalFailure(REFUSAL_IDS[16], "cleanup path is not a regular group")
    for current, directories, filenames in os.walk(group, topdown=False, followlinks=False):
        current_path = Path(current)
        for name in filenames:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                raise RealDualReversalFailure(REFUSAL_IDS[16], "cleanup file is not regular")
            path.unlink()
        for name in directories:
            path = current_path / name
            if path.is_symlink() or not path.is_dir():
                raise RealDualReversalFailure(REFUSAL_IDS[16], "cleanup directory differs")
            path.rmdir()
    group.rmdir()


def _directory_bytes(path: Path) -> int:
    total = 0
    for current, directories, filenames in os.walk(path, followlinks=False):
        current_path = Path(current)
        for name in directories:
            if (current_path / name).is_symlink():
                raise RealDualReversalFailure(REFUSAL_IDS[6], "private tree has a symlink")
        for name in filenames:
            candidate = current_path / name
            if candidate.is_symlink() or not candidate.is_file():
                raise RealDualReversalFailure(REFUSAL_IDS[6], "private file is not regular")
            total += candidate.stat().st_size
    return total


def _validate_public_receipt(receipt: Mapping[str, Any]) -> None:
    required = {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "contract_sha256",
        "decision_sha256",
        "implementation_commit",
        "dataset",
        "measurements",
        "derivatives",
        "target_firewall",
        "resource_limits",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
        "receipt_sha256",
    }
    if set(receipt) != required:
        raise RealDualReversalFailure(REFUSAL_IDS[17], "public receipt schema differs")
    unhashed = dict(receipt)
    observed_hash = unhashed.pop("receipt_sha256")
    if observed_hash != _canonical_sha256(unhashed):
        raise RealDualReversalFailure(REFUSAL_IDS[17], "public receipt hash differs")
    text = json.dumps(receipt, sort_keys=True)
    forbidden = (
        "/Users/",
        "/private/",
        "individual_prediction",
        "signed_trajectory",
        "actual_action_values",
        "cue_surrogate_values",
        "coefficient_values",
    )
    if any(token in text for token in forbidden):
        raise RealDualReversalFailure(REFUSAL_IDS[17], "public receipt leaks protected detail")
    counters = receipt["access_counters"]
    if (
        counters.get("old_retained_bundle_operations") != 0
        or counters.get("retries") != 0
        or counters.get("reruns") != 0
        or counters.get("model_runs") != 0
        or counters.get("training_runs") != 0
        or counters.get("scoring_runs") != 0
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[17], "public counters differ")


def _assert_resource_state(
    *,
    started: float,
    caps: Mapping[str, Any],
    rss_reader: Callable[[], int],
) -> None:
    if time.monotonic() - started > float(caps["wall_time_seconds"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "wall-time cap exceeded")
    if rss_reader() > int(caps["peak_RSS_bytes"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "peak RSS cap exceeded")


def run_streaming_derivative_build(
    *,
    workspace_root: str | Path,
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    opener: URLopener,
    environ: Mapping[str, str],
    private_root_relative: str | Path,
    public_receipt_relative: str | Path,
    strict_registered: bool,
    implementation_commit: str,
    minimum_free_disk_bytes: int | None = None,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Consume one stream and promote target-firewalled per-run derivatives."""

    np = _np()
    _check_thread_environment(environ)
    root = Path(workspace_root).resolve()
    private_root = root / _safe_relative_path(str(private_root_relative))
    public_receipt_path = root / _safe_relative_path(str(public_receipt_relative))
    _assert_safe_path_chain(root, private_root)
    _assert_safe_path_chain(root, public_receipt_path)
    if strict_registered:
        if contract != load_registered_contract(root) or inventory != load_registered_inventory(root):
            raise RealDualReversalRefusal(REFUSAL_IDS[0], "registered inputs differ")
        if Path(private_root_relative) != PRIVATE_ROOT_RELATIVE_PATH:
            raise RealDualReversalRefusal(REFUSAL_IDS[6], "private root differs")
        if Path(public_receipt_relative) != PUBLIC_RECEIPT_RELATIVE_PATH:
            raise RealDualReversalRefusal(REFUSAL_IDS[6], "public receipt path differs")
    if private_root.exists() or private_root.is_symlink():
        raise RealDualReversalRefusal(REFUSAL_IDS[5], "execution is already consumed")
    if public_receipt_path.exists() or public_receipt_path.is_symlink():
        raise RealDualReversalRefusal(REFUSAL_IDS[5], "public receipt already exists")
    caps = contract["resource_caps"]["future_acquisition_and_derivative_build"]
    streaming = contract["fresh_streaming_contract"]
    selected = inventory["selected_objects"]
    if (
        len(selected) != int(caps["payload_requests"])
        or sum(int(row["size_bytes"]) for row in selected) != int(caps["payload_bytes"])
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "payload inventory differs")
    required_free = (
        int(caps["minimum_free_disk_bytes"])
        if minimum_free_disk_bytes is None
        else int(minimum_free_disk_bytes)
    )
    if shutil.disk_usage(root).free < required_free:
        raise RealDualReversalRefusal(REFUSAL_IDS[2], "free disk is below the minimum")
    groups, geometry_rows = _group_inventory(
        inventory,
        expected_groups=int(streaming["run_group_count"]),
        expected_objects_per_group=int(streaming["objects_per_run_group"]),
        expected_geometry=int(streaming["geometry_object_count"]),
    )
    largest_group = max(
        sum(int(row["size_bytes"]) for row in rows) for _, rows in groups
    )
    if largest_group > int(caps["largest_raw_run_group_bytes"]):
        raise RealDualReversalRefusal(REFUSAL_IDS[7], "run group exceeds its cap")
    started = time.monotonic()
    private_root.mkdir(parents=True, exist_ok=False)
    consumed_path = private_root / "execution_consumed.v0.json"
    _write_exclusive(
        consumed_path,
        _json_bytes(
            {
                "schema_name": "neurodecodekit.iackd2_execution_consumed",
                "schema_version": SCHEMA_VERSION,
                "started_at_UTC": _utc_now(),
                "implementation_commit": implementation_commit,
                "retry_allowed": False,
                "rerun_allowed": False,
            }
        ),
        64 * 1024,
    )
    temporary_root = private_root / "temporary"
    model_root = private_root / "derivatives" / "model"
    sealed_root = private_root / "derivatives" / "sealed"
    physiology_root = private_root / "derivatives" / "physiology"
    for path in (temporary_root, model_root, sealed_root, physiology_root):
        path.mkdir(parents=True, exist_ok=False)
    peak_incremental_disk = _directory_bytes(private_root)
    metadata_summary = _fetch_metadata(contract, inventory, opener)
    _assert_resource_state(started=started, caps=caps, rss_reader=rss_reader)
    base_url = inventory["dataset"]["object_base_url"]
    source_records: list[dict[str, Any]] = []
    geometry_bodies: dict[tuple[str, str], dict[str, bytes]] = {}
    peak_raw_group_bytes = 0
    cleanup_operations = 0
    for index, row in enumerate(geometry_rows):
        body_root = temporary_root / f"geometry_{index:03d}"
        body_root.mkdir(exist_ok=False)
        destination = body_root / _safe_relative_path(str(row["path"])).name
        record = _download_object(
            row=row,
            destination=destination,
            base_url=base_url,
            opener=opener,
        )
        payload = _read_regular_bytes(destination, int(row["size_bytes"]))
        peak_incremental_disk = max(
            peak_incremental_disk,
            _directory_bytes(private_root),
        )
        record["semantic_parse_passes"] = 1
        source_records.append(record)
        identity = _geometry_identity(str(row["path"]))
        geometry_bodies.setdefault(identity, {})[str(row["role"])] = payload
        _remove_invocation_group(temporary_root, body_root)
        cleanup_operations += 1
    if any(set(value) != {"electrodes", "coordsystem"} for value in geometry_bodies.values()):
        raise RealDualReversalFailure(REFUSAL_IDS[8], "geometry pairs are incomplete")
    geometry = {
        identity: _parse_geometry_pair(value["electrodes"], value["coordsystem"])
        for identity, value in geometry_bodies.items()
    }
    geometry_binding_sha256 = _canonical_sha256(
        {
            f"{subject}|{hand}": {
                name: [round(number, 12) for number in xyz]
                for name, xyz in sorted(values.items())
            }
            for (subject, hand), values in sorted(geometry.items())
        }
    )
    run_summaries = []
    fit_class_counts: dict[str, list[int]] = {}
    final_class_counts: dict[str, list[int]] = {}
    total_retained_trials = 0
    for index, (group_key, rows) in enumerate(groups):
        group_root = temporary_root / f"run_group_{index:03d}"
        group_root.mkdir(exist_ok=False)
        group_bytes = sum(int(row["size_bytes"]) for row in rows)
        peak_raw_group_bytes = max(peak_raw_group_bytes, group_bytes)
        try:
            for row in rows:
                destination = group_root / _safe_relative_path(str(row["path"]))
                source_records.append(
                    _download_object(
                        row=row,
                        destination=destination,
                        base_url=base_url,
                        opener=opener,
                    )
                )
            peak_incremental_disk = max(
                peak_incremental_disk,
                _directory_bytes(private_root),
            )
            arrays = _read_run_group(
                group_key=group_key,
                group_root=group_root,
                rows=rows,
                geometry=geometry,
            )
            for record in source_records[-len(rows) :]:
                record["semantic_parse_passes"] = 1
            subject, hand, run = group_key.split(":", 2)
            split = core._split_kind(subject, run)
            binding = {
                **arrays["semantic_summary"]["bindings"],
                "dataset_BIDS_version": "1.7.0",
                "reference": "average",
                "sampling_frequency_hz": 1024,
                "policy_name": "IACKD-SourceSemanticsPolicy",
                "policy_version": "0.1.0",
                "policy_sha256": semantics.POLICY_SHA256,
                "geometry_binding_sha256": geometry_binding_sha256,
            }
            binding_sha256 = _canonical_sha256(binding)
            model_payload, sealed_payload, summary = _build_run_shards(
                arrays=arrays,
                split=split,
                source_binding_sha256=binding_sha256,
            )
            model_bytes = _deterministic_npz_bytes(model_payload)
            model_path = model_root / f"group_{index:03d}.npz"
            _write_exclusive(model_path, model_bytes, int(caps["private_derivative_bytes"]))
            sealed_sha256 = None
            if sealed_payload is not None:
                sealed_bytes = _deterministic_npz_bytes(sealed_payload)
                sealed_path = sealed_root / f"group_{index:03d}.npz"
                _write_exclusive(
                    sealed_path,
                    sealed_bytes,
                    int(caps["private_derivative_bytes"]),
                )
                sealed_sha256 = _sha256_bytes(sealed_bytes)
            physiology_payload = summary.pop("physiology_payload")
            physiology_bytes = _deterministic_npz_bytes(physiology_payload)
            physiology_path = physiology_root / f"group_{index:03d}.npz"
            _write_exclusive(
                physiology_path,
                physiology_bytes,
                int(caps["private_derivative_bytes"]),
            )
            unit = f"{subject}|{hand}"
            for arm in ("C2I", "I2C"):
                condition = next(
                    row for row in core.ARM_ROWS if row["arm_id"] == arm
                )[
                    "fit_condition" if split == "fit" else "final_condition"
                ]
                mask = arrays["conditions"] == condition
                counts = np.bincount(arrays["actual_action"][mask], minlength=2).tolist()
                destination_counts = (
                    fit_class_counts if split == "fit" else final_class_counts
                )
                current = destination_counts.setdefault(f"{arm}|{unit}", [0, 0])
                current[0] += int(counts[0])
                current[1] += int(counts[1])
            total_retained_trials += int(summary["retained_source_trials"])
            run_summaries.append(
                {
                    "group_key_sha256": _sha256_bytes(group_key.encode("utf-8")),
                    "group_bytes": group_bytes,
                    "model_shard_sha256": _sha256_bytes(model_bytes),
                    "sealed_shard_sha256": sealed_sha256,
                    "physiology_shard_sha256": _sha256_bytes(physiology_bytes),
                    "source_binding_sha256": binding_sha256,
                    **summary,
                }
            )
        finally:
            if group_root.exists() and not group_root.is_symlink():
                _remove_invocation_group(temporary_root, group_root)
                cleanup_operations += 1
        peak_incremental_disk = max(
            peak_incremental_disk,
            _directory_bytes(private_root),
        )
        _assert_resource_state(started=started, caps=caps, rss_reader=rss_reader)
    if any(temporary_root.iterdir()):
        raise RealDualReversalFailure(REFUSAL_IDS[16], "temporary root is not empty")
    temporary_root.rmdir()
    expected_unit_arms = int(contract["dataset_binding"]["participant_hand_unit_count"]) * 2
    if (
        set(fit_class_counts) != set(final_class_counts)
        or len(fit_class_counts) != expected_unit_arms
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[10], "unit-arm inventory differs")
    minimum_fit = min(min(values) for values in fit_class_counts.values())
    minimum_final = min(min(values) for values in final_class_counts.values())
    if strict_registered and (minimum_fit < 24 or minimum_final < 8):
        raise RealDualReversalFailure(REFUSAL_IDS[10], "minimum class count failed")
    source_hash_set_sha256 = _canonical_sha256(
        [
            {
                "path_sha256": _sha256_bytes(record["path"].encode("utf-8")),
                "size_bytes": record["size_bytes"],
                "sha256": record["sha256"],
            }
            for record in source_records
        ]
    )
    derivative_set_sha256 = _canonical_sha256(
        [
            {
                key: value
                for key, value in summary.items()
                if key.endswith("sha256")
            }
            for summary in run_summaries
        ]
    )
    private_manifest = {
        "schema_name": "neurodecodekit.iackd2_private_derivative_manifest",
        "schema_version": SCHEMA_VERSION,
        "status": "complete_target_firewalled_derivatives",
        "contract_sha256": CONTRACT_SHA256 if strict_registered else None,
        "decision_sha256": DECISION_SHA256 if strict_registered else None,
        "implementation_commit": implementation_commit,
        "source_records": source_records,
        "run_summaries": run_summaries,
        "source_hash_set_sha256": source_hash_set_sha256,
        "derivative_set_sha256": derivative_set_sha256,
        "geometry_binding_sha256": geometry_binding_sha256,
        "minimum_fit_rows_per_class_per_unit_arm": minimum_fit,
        "minimum_final_rows_per_class_per_unit_arm": minimum_final,
    }
    manifest_payload = _json_bytes(private_manifest)
    manifest_path = private_root / "private_derivative_manifest.v0.json"
    _write_exclusive(manifest_path, manifest_payload, int(caps["private_receipt_bytes"]))
    private_bytes = _directory_bytes(private_root)
    peak_incremental_disk = max(peak_incremental_disk, private_bytes)
    if private_bytes > int(caps["private_derivative_bytes"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "private derivative cap exceeded")
    runtime = time.monotonic() - started
    if peak_incremental_disk > int(caps["peak_incremental_disk_bytes"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "incremental disk cap exceeded")
    receipt = {
        "schema_name": "neurodecodekit.iackd2_acquisition_derivative_receipt",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_complete_target_firewalled_derivatives",
        "proof_posture": "aggregate_only_one_fresh_stream_no_model_or_score",
        "contract_sha256": CONTRACT_SHA256 if strict_registered else None,
        "decision_sha256": DECISION_SHA256 if strict_registered else None,
        "implementation_commit": implementation_commit,
        "dataset": {
            "provider": contract["dataset_binding"]["provider"],
            "accession": contract["dataset_binding"]["accession"],
            "version": contract["dataset_binding"]["version"],
            "participant_count": contract["dataset_binding"]["participant_count"],
            "participant_hand_units": contract["dataset_binding"][
                "participant_hand_unit_count"
            ],
        },
        "measurements": {
            **metadata_summary,
            "payload_requests": len(source_records),
            "payload_bytes": sum(record["size_bytes"] for record in source_records),
            "SHA256_passes": sum(record["SHA256_passes"] for record in source_records),
            "semantic_parse_passes": sum(
                record["semantic_parse_passes"] for record in source_records
            ),
            "run_groups": len(run_summaries),
            "peak_concurrent_raw_run_groups": 1,
            "largest_raw_run_group_bytes": peak_raw_group_bytes,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss_reader(),
            "peak_incremental_disk_bytes": peak_incremental_disk,
            "private_generated_bytes": private_bytes,
            "public_generated_bytes": 0,
            "retained_source_trials": total_retained_trials,
            "producer_is_causal_in_samples": True,
            "end_to_end_latency_measured": False,
        },
        "derivatives": {
            "model_shards": len(run_summaries),
            "sealed_target_shards": sum(
                summary["sealed_shard_sha256"] is not None for summary in run_summaries
            ),
            "physiology_shards": len(run_summaries),
            "source_hash_set_sha256": source_hash_set_sha256,
            "derivative_set_sha256": derivative_set_sha256,
            "geometry_binding_sha256": geometry_binding_sha256,
            "minimum_fit_rows_per_class_per_unit_arm": minimum_fit,
            "minimum_final_rows_per_class_per_unit_arm": minimum_final,
        },
        "target_firewall": {
            "fit_labels_available_to_fit_partition_only": True,
            "final_target_values_visible_to_predictive_code": 0,
            "final_signed_trajectories_visible_to_predictive_code": 0,
            "sealed_final_target_views": 2,
            "same_final_predictions_required_for_both_views": True,
        },
        "resource_limits": dict(caps),
        "access_counters": {
            "old_retained_bundle_operations": 0,
            "metadata_requests": metadata_summary["metadata_requests"],
            "payload_requests": len(source_records),
            "raw_signal_run_parses": len(run_summaries),
            "target_builder_runs": len(run_summaries),
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "scoring_runs": 0,
            "temporary_group_cleanup_operations": cleanup_operations,
            "retries": 0,
            "reruns": 0,
            "post_target_updates": 0,
            "provider_or_language_model_calls": 0,
            "stream_device_or_hardware_operations": 0,
        },
        "warnings": [
            "final targets remain sealed until a remotely green aggregate freeze",
            "offline oracle alignment is causal in samples but is not a real-time result",
            "no model fit inference score or scientific verdict occurred in this stage",
        ],
        "unavailable_fields": [
            "end_to_end_latency",
            "individual_participant_outcomes",
            "brain_specific_origin",
        ],
        "claim_boundary": {
            "engineering_capability": "one fresh storage-bounded public stream produced complete target-firewalled private derivatives",
            "scientific_claim_not_established": "this acquisition and derivative receipt alone establishes no neural effect action decoding brain-specific origin generalization real-time hardware assistive or clinical result",
        },
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    for _ in range(8):
        receipt_payload = _json_bytes(receipt)
        measured = len(receipt_payload)
        if receipt["measurements"]["public_generated_bytes"] == measured:
            break
        receipt["measurements"]["public_generated_bytes"] = measured
        receipt.pop("receipt_sha256", None)
        receipt["receipt_sha256"] = _canonical_sha256(receipt)
    else:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "receipt byte measure did not converge")
    _validate_public_receipt(receipt)
    _write_exclusive(public_receipt_path, receipt_payload, int(caps["public_receipt_bytes"]))
    return receipt


def _brainvision_payloads(
    *,
    subject: str,
    hand: str,
    run: str,
    include_optional_references: bool,
) -> dict[str, tuple[str, bytes]]:
    np = _np()
    policy = semantics.load_registered_policy()["policy"]
    semantic_fixture = semantics.make_generated_fixture(
        include_optional_references=include_optional_references,
        policy=policy,
    )
    names = [row["name"] for row in semantic_fixture["channels"]]
    trial_rows = (
        ("trial-1", "red", 0, 1.0),
        ("trial-2", "red", 1, 4.0),
        ("trial-3", "yellow", 0, 7.0),
        ("trial-4", "yellow", 1, 10.0),
    )
    sample_count = 13 * 1024
    rng = np.random.default_rng(8100 + int(run))
    values_uv = rng.normal(0.0, 0.15, size=(len(names), sample_count)).astype("float32")
    x = np.linspace(-math.pi, math.pi, sample_count, endpoint=False)
    for name, weight in (("C3", 0.8), ("C4", -0.7), ("Cz", 0.6)):
        values_uv[names.index(name)] += (weight * np.sin(x)).astype("float32")
    eeg_name = f"{subject}_task-ihc_acq-{hand}_run-{run}_eeg.eeg"
    vmrk_name = f"{subject}_task-ihc_acq-{hand}_run-{run}_eeg.vmrk"
    channel_lines = [
        f"Ch{index}={name},,1,uV" for index, name in enumerate(names, start=1)
    ]
    vhdr = "\n".join(
        (
            "Brain Vision Data Exchange Header File Version 1.0",
            "[Common Infos]",
            "Codepage=UTF-8",
            f"DataFile={eeg_name}",
            f"MarkerFile={vmrk_name}",
            "DataFormat=BINARY",
            "DataOrientation=MULTIPLEXED",
            f"NumberOfChannels={len(names)}",
            "SamplingInterval=976.5625",
            "[Binary Infos]",
            "BinaryFormat=IEEE_FLOAT_32",
            "[Channel Infos]",
            *channel_lines,
            "",
        )
    ).encode()
    marker_lines = [
        "Brain Vision Data Exchange Marker File, Version 1.0",
        "[Common Infos]",
        "Codepage=UTF-8",
        f"DataFile={eeg_name}",
        "[Marker Infos]",
        "Mk1=New Segment,,1,1,0",
    ]
    marker_index = 2
    for _, _, _, event_55 in trial_rows:
        for marker_type, description, onset in (
            ("Stimulus", "S 55", event_55),
            ("Stimulus", "S 14", event_55 + 1.0),
            ("Response", "R 66", event_55 + 2.0),
        ):
            position = int(round(onset * 1024.0)) + 1
            marker_lines.append(
                f"Mk{marker_index}={marker_type},{description},{position},1,0"
            )
            marker_index += 1
    vmrk = ("\n".join((*marker_lines, ""))).encode()
    channels = "name\ttype\tunits\n" + "".join(
        f"{row['name']}\t{row['type']}\tuV\n" for row in semantic_fixture["channels"]
    )
    sidecar = json.dumps(
        {
            **semantic_fixture["eeg_sidecar"],
            "TaskName": "ihc",
            "PowerLineFrequency": 60,
            "SoftwareFilters": "n/a",
        },
        sort_keys=True,
    ).encode()
    event_lines = ["onset\tvalue\ttrial_id\tcondition"]
    ball_lines = ["trial_id\ttimestamp\tx\tcondition\tmove_direct"]
    leap_lines = ["trial_id\ttimestamp\tx\ty\tz\tcondition"]
    for trial_id, condition, actual_direction, event_55 in trial_rows:
        event_lines.extend(
            (
                f"{event_55:.1f}\t55\t{trial_id}\t{condition}",
                f"{event_55 + 1.0:.1f}\t14\t{trial_id}\t{condition}",
                f"{event_55 + 2.0:.1f}\t66\t{trial_id}\t{condition}",
            )
        )
        times = np.linspace(event_55, event_55 + 2.0, 101)
        actual_sign = 1.0 if actual_direction == 1 else -1.0
        actual_x = np.where(
            times < event_55 + 1.10,
            0.0,
            actual_sign * (times - (event_55 + 1.10)) * 30.0,
        )
        visual_direction = (
            actual_direction if condition == "red" else 1 - actual_direction
        )
        visual_sign = 1.0 if visual_direction == 1 else -1.0
        ball_x = visual_sign * np.abs(actual_x)
        move = "right" if visual_direction == 1 else "left"
        ball_lines.extend(
            f"{trial_id}\t{timestamp:.4f}\t{position:.6f}\t{condition}\t{move}"
            for timestamp, position in zip(times, ball_x, strict=True)
        )
        leap_lines.extend(
            f"{trial_id}\t{timestamp:.4f}\t{position:.6f}\t0\t0\t{condition}"
            for timestamp, position in zip(times, actual_x, strict=True)
        )
    event = ("\n".join((*event_lines, ""))).encode()
    ball = "\n".join((*ball_lines, ""))
    leap = "\n".join((*leap_lines, ""))
    eeg_prefix = f"{subject}/eeg/{subject}_task-ihc_acq-{hand}_run-{run}"
    behavior_prefix = f"{subject}/sourcedata/beh/{subject}_task-ihc_run-{run}_hand-{hand}"
    return {
        "eeg_header": (f"{eeg_prefix}_eeg.vhdr", vhdr),
        "eeg_signal": (
            f"{eeg_prefix}_eeg.eeg",
            values_uv.T.astype("<f4").tobytes(order="C"),
        ),
        "eeg_marker": (f"{eeg_prefix}_eeg.vmrk", vmrk),
        "channels": (f"{eeg_prefix}_channels.tsv", channels.encode()),
        "eeg_sidecar": (f"{eeg_prefix}_eeg.json", sidecar),
        "events": (f"{eeg_prefix}_events.tsv", event),
        "ball_stream": (f"{behavior_prefix}_ball.tsv", ball.encode()),
        "ball_sidecar": (
            f"{behavior_prefix}_ball.json",
            b'{"timestamp":{"Units":"seconds"},"x":{"Units":"pixels"}}',
        ),
        "leap_stream": (f"{behavior_prefix}_leap.tsv", leap.encode()),
        "leap_sidecar": (
            f"{behavior_prefix}_leap.json",
            b'{"timestamp":{"Units":"seconds"},"palm_position":{"Units":"mm"}}',
        ),
    }


def _mock_contract_inventory_transport() -> tuple[
    dict[str, Any],
    dict[str, Any],
    URLopener,
]:
    payloads: dict[str, bytes] = {}
    rows = []
    timestamp = "2026-08-10T00:00:00.000Z"
    for run, optional in (("01", False), ("04", True)):
        for role, (path, payload) in _brainvision_payloads(
            subject="sub-01",
            hand="left",
            run=run,
            include_optional_references=optional,
        ).items():
            payloads[path] = payload
            rows.append(
                {
                    "path": path,
                    "subject": "sub-01",
                    "role": role,
                    "size_bytes": len(payload),
                    "etag": hashlib.md5(payload, usedforsecurity=False).hexdigest(),  # noqa: S324
                    "last_modified": timestamp,
                }
            )
    policy = semantics.load_registered_policy()["policy"]
    fixture = semantics.make_generated_fixture(
        include_optional_references=True,
        policy=policy,
    )
    electrode_rows = "name\tx\ty\tz\n" + "".join(
        (
            f"{row['name']}\t{0.01 + index / 1000:.6f}\t"
            f"{0.02 + index / 1000:.6f}\t0.50\n"
            if row["type"] == "EEG"
            else f"{row['name']}\tn/a\tn/a\tn/a\n"
        )
        for index, row in enumerate(fixture["channels"])
    )
    geometry_payloads = {
        "electrodes": (
            "sub-01/eeg/sub-01_acq-left_space-CapTrak_electrodes.tsv",
            electrode_rows.encode(),
        ),
        "coordsystem": (
            "sub-01/eeg/sub-01_acq-left_space-CapTrak_coordsystem.json",
            b'{"EEGCoordinateSystem":"CapTrak","EEGCoordinateUnits":"m"}',
        ),
    }
    for role, (path, payload) in geometry_payloads.items():
        payloads[path] = payload
        rows.append(
            {
                "path": path,
                "subject": "sub-01",
                "role": role,
                "size_bytes": len(payload),
                "etag": hashlib.md5(payload, usedforsecurity=False).hexdigest(),  # noqa: S324
                "last_modified": timestamp,
            }
        )
    rows.sort(key=lambda row: row["path"])
    identity_bytes, identity_sha256 = legacy_acquisition._canonical_identity(rows)
    description = json.dumps(
        {
            "Name": "Generated IACKD2 transport fixture",
            "BIDSVersion": "1.7.0",
            "License": "CC0",
            "DatasetDOI": "doi:10.18112/openneuro.ds006840.v1.0.0",
        },
        sort_keys=True,
    ).encode()
    changes = b"1.0.0 generated fixture\n"
    first_page, second_page = legacy_acquisition.synthetic_listing_pages(
        rows,
        split_at=len(rows) // 2,
    )
    source = {
        "dataset_description": {
            "url": "https://fixture.invalid/dataset_description.json",
            "bytes": len(description),
            "sha256": _sha256_bytes(description),
        },
        "changes": {
            "url": "https://fixture.invalid/CHANGES",
            "bytes": len(changes),
            "sha256": _sha256_bytes(changes),
        },
    }
    listing = {
        "endpoint": "https://fixture.invalid/list",
        "query": "list-type=2&prefix=ds006840/&max-keys=1000",
        "pages": [
            {"body_bytes": len(first_page), "body_sha256": _sha256_bytes(first_page)},
            {"body_bytes": len(second_page), "body_sha256": _sha256_bytes(second_page)},
        ],
    }
    selected_bytes = sum(int(row["size_bytes"]) for row in rows)
    run_keys = {_run_key(row) for row in rows}
    run_keys.discard(None)
    contract = {
        "dataset_binding": {
            "provider": "generated_mock",
            "accession": "ds006840",
            "version": "1.0.0",
            "dataset_doi": "10.18112/openneuro.ds006840.v1.0.0",
            "license": "CC0",
            "bids_version": "1.7.0",
            "participant_count": 1,
            "participant_hand_unit_count": 1,
        },
        "metadata_reverification": {
            "expected_listed_object_count": len(rows),
            "expected_listed_total_bytes": selected_bytes,
            "canonical_identity_sha256": identity_sha256,
        },
        "fresh_streaming_contract": {
            "run_group_count": 2,
            "objects_per_run_group": 10,
            "geometry_object_count": 2,
        },
        "resource_caps": {
            "future_acquisition_and_derivative_build": {
                "payload_requests": len(rows),
                "payload_bytes": selected_bytes,
                "largest_raw_run_group_bytes": max(
                    sum(row["size_bytes"] for row in rows if _run_key(row) == key)
                    for key in run_keys
                ),
                "minimum_free_disk_bytes": 1,
                "metadata_body_bytes": 2 * 1024 * 1024,
                "wall_time_seconds": 60,
                "peak_RSS_bytes": 512 * 1024 * 1024,
                "peak_incremental_disk_bytes": 64 * 1024 * 1024,
                "private_derivative_bytes": 16 * 1024 * 1024,
                "public_receipt_bytes": 1024 * 1024,
                "private_receipt_bytes": 1024 * 1024,
                "retries": 0,
                "reruns": 0,
            }
        },
    }
    inventory = {
        "source_documents": source,
        "listing_snapshot": listing,
        "dataset": {
            "object_base_url": "https://fixture.invalid/objects/",
        },
        "selected_objects": rows,
        "selection": {
            "canonical_identity_bytes": identity_bytes,
            "canonical_identity_sha256": identity_sha256,
        },
    }
    first_url = f"{listing['endpoint']}?{listing['query']}"
    second_url = f"{first_url}&continuation-token=fixture-token"
    documents = {
        source["dataset_description"]["url"]: description,
        source["changes"]["url"]: changes,
        first_url: first_page,
        second_url: second_page,
    }
    etags: dict[str, str] = {}
    for row in rows:
        url = _object_url(inventory["dataset"]["object_base_url"], row["path"])
        documents[url] = payloads[row["path"]]
        etags[url] = row["etag"]
    calls: list[str] = []

    def opener(url: str, maximum_bytes: int) -> BinaryIO:
        if url not in documents or url in calls or len(documents[url]) > maximum_bytes:
            raise RealDualReversalFailure(REFUSAL_IDS[5], "mock request differs")
        calls.append(url)
        return FixtureResponse(
            body=documents[url],
            url=url,
            etag=etags.get(url, "fixture-metadata"),
        )

    opener.calls = calls  # type: ignore[attr-defined]
    return contract, inventory, opener


def _regular_files(path: Path, *, suffix: str) -> list[Path]:
    if path.is_symlink() or not path.is_dir():
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "private directory differs")
    files = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise RealDualReversalRefusal(REFUSAL_IDS[6], "private entry differs")
            candidate = Path(entry.path)
            if candidate.suffix != suffix:
                raise RealDualReversalRefusal(REFUSAL_IDS[11], "private file suffix differs")
            files.append(candidate)
    return sorted(files)


def _expected_prediction_keys(contract: Mapping[str, Any]) -> set[str]:
    return {
        core._prediction_key(arm, core._unit(subject, hand))
        for arm in ("C2I", "I2C")
        for subject in contract["dataset_binding"]["participant_ids"]
        for hand in contract["dataset_binding"]["moving_hand_entities"]
    }


def _expected_feature_dimensions(contract: Mapping[str, Any]) -> dict[str, int]:
    model = contract["model_contract"]
    return {
        "whole_features": int(model["primary_feature_dimension"]),
        "central_features": int(model["central_feature_dimension"]),
        "occipital_features": int(model["occipital_feature_dimension"]),
        "ocular_features": int(model["ocular_feature_dimension"]),
        "early_features": int(model["half_window_feature_dimension"]),
        "late_features": int(model["half_window_feature_dimension"]),
        "prewindow_features": int(model["pre_window_feature_dimension"]),
        "timing_features": int(model["timing_feature_dimension"]),
        "physiology_features": 7,
    }


def _validate_row_block(
    rows: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    key: str,
    split: str,
) -> None:
    np = _np()
    expected = set(MODEL_ARRAY_KEYS)
    if split == "fit":
        expected.add("fit_targets")
    if set(rows) != expected:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "model row schema differs")
    item_ids = np.asarray(rows["item_ids"])
    count = len(item_ids)
    if item_ids.ndim != 1 or count == 0 or len(set(item_ids.tolist())) != count:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "model item identities differ")
    for name in ("subjects", "hands", "runs"):
        array = np.asarray(rows[name])
        if array.shape != (count,):
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "identity array differs")
    arm, subject, hand = key.split("|", 2)
    if arm not in {"C2I", "I2C"}:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "arm identity differs")
    if set(rows["subjects"].tolist()) != {subject} or set(rows["hands"].tolist()) != {hand}:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "unit identity differs")
    if any(core._split_kind(subject, str(run)) != split for run in rows["runs"].tolist()):
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "strict split binding differs")
    for name, dimension in _expected_feature_dimensions(contract).items():
        array = np.asarray(rows[name])
        if array.shape != (count, dimension) or not np.isfinite(array).all():
            raise RealDualReversalRefusal(
                REFUSAL_IDS[11], f"feature dimensions differ: {name}"
            )
    if split == "fit":
        targets = np.asarray(rows["fit_targets"])
        if targets.shape != (count,) or set(targets.tolist()) != {0, 1}:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "fit labels differ")
        minimum = int(
            contract["split_contract"][
                "minimum_fit_rows_per_action_direction_per_unit_per_arm"
            ]
        )
        if int(np.bincount(targets.astype("int8"), minlength=2).min()) < minimum:
            raise RealDualReversalRefusal(REFUSAL_IDS[10], "fit class minimum failed")
    else:
        try:
            core._assert_target_free(rows)
        except core.DualReversalRefusal as exc:
            raise RealDualReversalRefusal(
                REFUSAL_IDS[11], "final model block contains a forbidden field"
            ) from exc


def _validate_target_free_model_stage(
    model_stage: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> None:
    required = {
        "fit",
        "final",
        "fit_rows",
        "final_rows",
        "split_sha256",
        "final_item_ids_sha256",
    }
    if set(model_stage) != required:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "model-stage schema differs")
    fit = model_stage["fit"]
    final = model_stage["final"]
    expected_keys = _expected_prediction_keys(contract)
    if (
        not isinstance(fit, Mapping)
        or not isinstance(final, Mapping)
        or set(fit) != expected_keys
        or set(final) != expected_keys
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "model-stage unit inventory differs")
    fit_rows = 0
    final_rows = 0
    fit_ids = set()
    final_ids = set()
    for key in sorted(expected_keys):
        _validate_row_block(fit[key], contract=contract, key=key, split="fit")
        _validate_row_block(final[key], contract=contract, key=key, split="final")
        fit_rows += len(fit[key]["item_ids"])
        final_rows += len(final[key]["item_ids"])
        fit_ids.update(fit[key]["item_ids"].tolist())
        final_ids.update(final[key]["item_ids"].tolist())
    if (
        fit_ids & final_ids
        or len(fit_ids) != fit_rows
        or len(final_ids) != final_rows
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "fit and final identities overlap")
    split_sha256 = _canonical_sha256(
        {
            key: {
                "fit_item_ids_sha256": _array_sha256(fit[key]["item_ids"]),
                "final_item_ids_sha256": _array_sha256(final[key]["item_ids"]),
            }
            for key in sorted(expected_keys)
        }
    )
    final_item_ids_sha256 = _canonical_sha256(
        {
            key: _array_sha256(final[key]["item_ids"])
            for key in sorted(expected_keys)
        }
    )
    maximums = contract["split_contract"]["maximum_pre_quality_control_counts"]
    if (
        model_stage["fit_rows"] != fit_rows
        or model_stage["final_rows"] != final_rows
        or fit_rows > int(maximums["both_arms_fit_rows"])
        or final_rows > int(maximums["both_arms_final_rows"])
        or model_stage["split_sha256"] != split_sha256
        or model_stage["final_item_ids_sha256"] != final_item_ids_sha256
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "model-stage binding differs")


def load_target_free_model_stage(
    *,
    private_root: str | Path,
    contract: Mapping[str, Any],
    public_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Load model shards without opening or listing the sealed-target directory."""

    np = _np()
    root = Path(private_root)
    if root.is_symlink() or not root.is_dir():
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "private root differs")
    manifest_path = root / "private_derivative_manifest.v0.json"
    manifest_payload = _read_regular_bytes(manifest_path, 4 * 1024 * 1024)
    try:
        manifest = json.loads(manifest_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "private manifest differs") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_name")
        != "neurodecodekit.iackd2_private_derivative_manifest"
        or manifest.get("status") != "complete_target_firewalled_derivatives"
        or manifest.get("source_hash_set_sha256")
        != public_receipt["derivatives"]["source_hash_set_sha256"]
        or manifest.get("derivative_set_sha256")
        != public_receipt["derivatives"]["derivative_set_sha256"]
        or manifest.get("minimum_final_rows_per_class_per_unit_arm", 0)
        < contract["split_contract"][
            "minimum_final_rows_per_action_direction_per_unit_per_arm"
        ]
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "private manifest binding differs")
    model_files = _regular_files(root / "derivatives" / "model", suffix=".npz")
    run_summaries = manifest.get("run_summaries", [])
    if len(model_files) != 128 or len(run_summaries) != 128:
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "model shard inventory differs")
    fit_lists: dict[str, dict[str, list[Any]]] = {}
    final_lists: dict[str, dict[str, list[Any]]] = {}
    source_bindings = []
    for path, summary in zip(model_files, run_summaries, strict=True):
        payload = _read_regular_bytes(path, int(contract["resource_caps"]["future_acquisition_and_derivative_build"]["private_derivative_bytes"]))
        if _sha256_bytes(payload) != summary.get("model_shard_sha256"):
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "model shard hash differs")
        try:
            with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
                shard = {name: archive[name] for name in archive.files}
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "model shard is malformed") from exc
        binding = np.asarray(shard.pop("source_binding_sha256", None))
        if binding.shape != () or not re.fullmatch(r"[0-9a-f]{64}", str(binding.item())):
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "source binding differs")
        source_bindings.append(str(binding.item()))
        has_fit = any(name.startswith("C2I_fit_") for name in shard)
        has_final = any(name.startswith("C2I_final_") for name in shard)
        if has_fit == has_final:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "shard split differs")
        split = "fit" if has_fit else "final"
        expected_names = set()
        for arm in ("C2I", "I2C"):
            prefix = f"{arm}_{split}_"
            names = {f"{prefix}{name}" for name in MODEL_ARRAY_KEYS}
            if split == "fit":
                names.add(f"{prefix}fit_targets")
            expected_names.update(names)
            rows = {name: shard[f"{prefix}{name}"] for name in MODEL_ARRAY_KEYS}
            if split == "fit":
                rows["fit_targets"] = shard[f"{prefix}fit_targets"]
            subject_values = set(np.asarray(rows["subjects"]).tolist())
            hand_values = set(np.asarray(rows["hands"]).tolist())
            if len(subject_values) != 1 or len(hand_values) != 1:
                raise RealDualReversalRefusal(REFUSAL_IDS[11], "shard unit differs")
            key = core._prediction_key(
                arm,
                core._unit(next(iter(subject_values)), next(iter(hand_values))),
            )
            destination = fit_lists if split == "fit" else final_lists
            block = destination.setdefault(key, {name: [] for name in rows})
            if set(block) != set(rows):
                raise RealDualReversalRefusal(REFUSAL_IDS[11], "shard row schema drifts")
            for name, value in rows.items():
                block[name].append(value)
        if set(shard) != expected_names:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "shard contains an extra field")

    def combine(groups: Mapping[str, Mapping[str, Sequence[Any]]]) -> dict[str, Any]:
        return {
            key: {
                name: np.concatenate(values, axis=0)
                for name, values in rows.items()
            }
            for key, rows in groups.items()
        }

    fit = combine(fit_lists)
    final = combine(final_lists)
    model_stage = {
        "fit": fit,
        "final": final,
        "fit_rows": sum(len(rows["item_ids"]) for rows in fit.values()),
        "final_rows": sum(len(rows["item_ids"]) for rows in final.values()),
        "split_sha256": _canonical_sha256(
            {
                key: {
                    "fit_item_ids_sha256": _array_sha256(fit[key]["item_ids"]),
                    "final_item_ids_sha256": _array_sha256(final[key]["item_ids"]),
                }
                for key in sorted(fit)
            }
        ),
        "final_item_ids_sha256": _canonical_sha256(
            {
                key: _array_sha256(final[key]["item_ids"])
                for key in sorted(final)
            }
        ),
    }
    _validate_target_free_model_stage(model_stage, contract=contract)
    return {
        "model_stage": model_stage,
        "provenance": {
            "private_manifest_sha256": _sha256_bytes(manifest_payload),
            "source_binding_set_sha256": _canonical_sha256(sorted(source_bindings)),
            "source_hash_set_sha256": manifest["source_hash_set_sha256"],
            "derivative_set_sha256": manifest["derivative_set_sha256"],
            "model_shard_reads": len(model_files),
            "model_shard_bytes": sum(path.stat().st_size for path in model_files),
        },
    }


def _registered_train_derangement(labels: Any, runs: Any, *, key: str) -> Any:
    """Assign a deterministic near-balanced null label within each run/class stratum."""

    np = _np()
    target = np.asarray(labels, dtype="int8")
    run_ids = np.asarray(runs)
    if target.ndim != 1 or run_ids.shape != target.shape or set(target.tolist()) != {0, 1}:
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "derangement inputs differ")
    shuffled = np.empty_like(target)
    for run_id in sorted(set(run_ids.tolist())):
        for source_label in (0, 1):
            indices = np.flatnonzero((run_ids == run_id) & (target == source_label))
            if not len(indices):
                raise RealDualReversalRefusal(REFUSAL_IDS[12], "derangement stratum empty")
            rng = np.random.default_rng(
                int.from_bytes(
                    hashlib.sha256(
                        f"6841|{key}|{run_id}|{source_label}".encode("utf-8")
                    ).digest()[:8],
                    "big",
                )
            )
            rng.shuffle(indices)
            offset = int(rng.integers(0, 2))
            assigned = (np.arange(len(indices), dtype="int8") + offset) % 2
            shuffled[indices] = assigned
            counts = np.bincount(assigned, minlength=2)
            if abs(int(counts[0]) - int(counts[1])) > 1:
                raise RealDualReversalRefusal(
                    REFUSAL_IDS[12], "derangement stratum is not near-balanced"
                )
    return shuffled


def run_target_blind_model_matrix(
    model_stage: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Fit exactly 660 models and produce exactly 900 target-blind prediction sets."""

    np = _np()
    _validate_target_free_model_stage(model_stage, contract=contract)
    fit = model_stage["fit"]
    final = model_stage["final"]
    fitted: dict[str, dict[str, Any]] = {}
    parameter_updates = 0
    permutation = np.random.default_rng(6842).permutation(26)
    try:
        for key in sorted(fit):
            fit_rows = fit[key]
            final_rows = final[key]
            target = fit_rows["fit_targets"]
            eog_fit, eog_final = core._eog_residuals(
                fit_rows["whole_features"],
                fit_rows["ocular_features"],
                final_rows["whole_features"],
                final_rows["ocular_features"],
            )
            shuffled = _registered_train_derangement(
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
                name: core._fit_lda(values, labels)
                for name, (values, labels) in model_inputs.items()
            }
            parameter_updates += len(models)
            models["train_only_no_signal_prior"] = core._fit_prior(target)
            parameter_updates += 1
            fitted[key] = {
                "models": models,
                "EOG_orthogonalized_final": eog_final,
            }
        predictions: dict[str, dict[str, Any]] = {
            condition: {} for condition in core.CONDITION_IDS
        }
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
                "fixed_train_label_derangement_seed_6841": final_rows[
                    "whole_features"
                ],
                "train_only_no_signal_prior": np.zeros(
                    (len(final_rows["item_ids"]), 1)
                ),
            }
            for condition, values in direct_inputs.items():
                predictions[condition][key] = core._predict(models[condition], values)
                inference_calls += 1
            primary = models["whole_head_primary"]
            predictions["all_zero_final_EEG_through_primary"][key] = core._predict(
                primary,
                np.zeros_like(final_rows["whole_features"]),
            )
            predictions["one_row_cyclic_final_feature_displacement"][key] = (
                core._predict(primary, np.roll(final_rows["whole_features"], 1, axis=0))
            )
            permuted = final_rows["whole_features"].reshape(-1, 26, 5)[
                :, permutation, :
            ]
            predictions["fixed_final_only_EEG_channel_permutation_seed_6842"][
                key
            ] = core._predict(primary, permuted.reshape(-1, 130))
            arm, subject, hand = key.split("|", 2)
            opposite = "right" if hand == "left" else "left"
            opposite_key = core._prediction_key(arm, core._unit(subject, opposite))
            predictions["opposite_hand_primary_without_adaptation"][key] = core._predict(
                fitted[opposite_key]["models"]["whole_head_primary"],
                final_rows["whole_features"],
            )
            inference_calls += 4
    except core.DualReversalRefusal as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[12], "model matrix failed") from exc
    prediction_sets = sum(len(rows) for rows in predictions.values())
    if parameter_updates != 660 or inference_calls != 900 or prediction_sets != 900:
        raise RealDualReversalFailure(REFUSAL_IDS[12], "fit or prediction count differs")
    try:
        condition_hashes, private_hash = core._prediction_hash_summary(
            predictions,
            parameter_updates=parameter_updates,
            prediction_sets=prediction_sets,
        )
    except core.DualReversalRefusal as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[12], "prediction hashes differ") from exc
    return {
        "predictions": predictions,
        "condition_prediction_sha256": condition_hashes,
        "canonical_private_prediction_sha256": private_hash,
        "parameter_update_fits": parameter_updates,
        "target_blind_inference_calls": inference_calls,
        "prediction_sets": prediction_sets,
    }


def _validate_matrix(
    matrix: Mapping[str, Any],
    *,
    model_stage: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    _validate_target_free_model_stage(model_stage, contract=contract)
    required = {
        "predictions",
        "condition_prediction_sha256",
        "canonical_private_prediction_sha256",
        "parameter_update_fits",
        "target_blind_inference_calls",
        "prediction_sets",
    }
    if set(matrix) != required:
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "matrix schema differs")
    if (
        matrix["parameter_update_fits"]
        != contract["fit_inventory"]["required_parameter_update_fits"]
        or matrix["target_blind_inference_calls"]
        != contract["prediction_inventory"]["maximum_target_blind_inference_calls"]
        or matrix["prediction_sets"]
        != contract["prediction_inventory"]["required_prediction_sets"]
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "matrix counts differ")
    try:
        hashes, private_hash = core._prediction_hash_summary(
            matrix["predictions"],
            parameter_updates=matrix["parameter_update_fits"],
            prediction_sets=matrix["prediction_sets"],
        )
    except core.DualReversalRefusal as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "matrix payload differs") from exc
    if (
        hashes != matrix["condition_prediction_sha256"]
        or private_hash != matrix["canonical_private_prediction_sha256"]
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "matrix hashes differ")
    for condition in core.CONDITION_IDS:
        for key, values in matrix["predictions"][condition].items():
            if len(values) != len(model_stage["final"][key]["item_ids"]):
                raise RealDualReversalRefusal(
                    REFUSAL_IDS[12], "prediction row count differs"
                )


def _private_prediction_bytes(
    matrix: Mapping[str, Any],
    *,
    model_stage: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> bytes:
    _validate_matrix(matrix, model_stage=model_stage, contract=contract)
    np = _np()
    conditions = list(core.CONDITION_IDS)
    keys = sorted(model_stage["final"])
    arrays: dict[str, Any] = {
        "condition_ids": np.asarray(conditions, dtype="U64"),
        "unit_arm_keys": np.asarray(keys, dtype="U32"),
        "parameter_update_fits": np.asarray(matrix["parameter_update_fits"], dtype="int64"),
        "target_blind_inference_calls": np.asarray(
            matrix["target_blind_inference_calls"], dtype="int64"
        ),
        "prediction_sets": np.asarray(matrix["prediction_sets"], dtype="int64"),
    }
    for key_index, key in enumerate(keys):
        arrays[f"item_ids_{key_index:02d}"] = model_stage["final"][key]["item_ids"]
        for condition_index, condition in enumerate(conditions):
            arrays[f"prediction_{condition_index:02d}_{key_index:02d}"] = matrix[
                "predictions"
            ][condition][key]
    return _deterministic_npz_bytes(arrays)


def _load_private_predictions(
    path: Path,
    *,
    expected_sha256: str,
    maximum_bytes: int,
    model_stage: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _np()
    payload = _read_regular_bytes(path, maximum_bytes)
    if _sha256_bytes(payload) != expected_sha256:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "private predictions hash differs")
    try:
        with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
            arrays = {name: archive[name] for name in archive.files}
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "private predictions differ") from exc
    conditions = list(core.CONDITION_IDS)
    keys = sorted(model_stage["final"])
    expected_names = {
        "condition_ids",
        "unit_arm_keys",
        "parameter_update_fits",
        "target_blind_inference_calls",
        "prediction_sets",
        *(f"item_ids_{index:02d}" for index in range(len(keys))),
        *(
            f"prediction_{condition_index:02d}_{key_index:02d}"
            for condition_index in range(len(conditions))
            for key_index in range(len(keys))
        ),
    }
    if (
        set(arrays) != expected_names
        or arrays["condition_ids"].tolist() != conditions
        or arrays["unit_arm_keys"].tolist() != keys
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[14], "prediction inventory differs")
    predictions: dict[str, dict[str, Any]] = {condition: {} for condition in conditions}
    for key_index, key in enumerate(keys):
        if not np.array_equal(
            arrays[f"item_ids_{key_index:02d}"],
            model_stage["final"][key]["item_ids"],
        ):
            raise RealDualReversalFailure(REFUSAL_IDS[14], "prediction item IDs differ")
        for condition_index, condition in enumerate(conditions):
            predictions[condition][key] = arrays[
                f"prediction_{condition_index:02d}_{key_index:02d}"
            ]
    matrix = {
        "predictions": predictions,
        "condition_prediction_sha256": {},
        "canonical_private_prediction_sha256": "",
        "parameter_update_fits": int(arrays["parameter_update_fits"].item()),
        "target_blind_inference_calls": int(
            arrays["target_blind_inference_calls"].item()
        ),
        "prediction_sets": int(arrays["prediction_sets"].item()),
    }
    try:
        hashes, private_hash = core._prediction_hash_summary(
            predictions,
            parameter_updates=matrix["parameter_update_fits"],
            prediction_sets=matrix["prediction_sets"],
        )
    except core.DualReversalRefusal as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "prediction payload differs") from exc
    matrix["condition_prediction_sha256"] = hashes
    matrix["canonical_private_prediction_sha256"] = private_hash
    _validate_matrix(matrix, model_stage=model_stage, contract=contract)
    return matrix


def load_target_free_physiology_summary(
    *,
    private_root: str | Path,
    contract: Mapping[str, Any],
    expected_shards: int = 128,
) -> dict[str, Any]:
    """Reduce target-free physiology shards to aggregate records and hashes."""

    np = _np()
    root = Path(private_root)
    manifest = json.loads(
        _read_regular_bytes(
            root / "private_derivative_manifest.v0.json", 4 * 1024 * 1024
        ).decode("utf-8")
    )
    summaries = manifest.get("run_summaries", [])
    paths = _regular_files(root / "derivatives" / "physiology", suffix=".npz")
    if len(paths) != expected_shards or len(summaries) != expected_shards:
        raise RealDualReversalRefusal(REFUSAL_IDS[12], "physiology inventory differs")
    trace_sum = np.zeros((3, 1024), dtype="float64")
    feature_sum = np.zeros(7, dtype="float64")
    guard_values = []
    row_count = 0
    content_rows = []
    cap = int(
        contract["resource_caps"]["future_acquisition_and_derivative_build"][
            "private_derivative_bytes"
        ]
    )
    for path, summary in zip(paths, summaries, strict=True):
        payload = _read_regular_bytes(path, cap)
        digest = _sha256_bytes(payload)
        if digest != summary.get("physiology_shard_sha256"):
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "physiology hash differs")
        try:
            with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
                arrays = {name: archive[name] for name in archive.files}
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "physiology shard differs") from exc
        if set(arrays) != {
            "item_ids",
            "readiness_traces",
            "physiology_features",
            "motion_guard_milliseconds",
        }:
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "physiology schema differs")
        count = len(arrays["item_ids"])
        if (
            arrays["item_ids"].shape != (count,)
            or arrays["readiness_traces"].shape != (count, 3, 1024)
            or arrays["physiology_features"].shape != (count, 7)
            or arrays["motion_guard_milliseconds"].shape != (count,)
            or not all(
                np.isfinite(arrays[name]).all()
                for name in (
                    "readiness_traces",
                    "physiology_features",
                    "motion_guard_milliseconds",
                )
            )
        ):
            raise RealDualReversalRefusal(REFUSAL_IDS[11], "physiology arrays differ")
        trace_sum += arrays["readiness_traces"].sum(axis=0, dtype="float64")
        feature_sum += arrays["physiology_features"].sum(axis=0, dtype="float64")
        guard_values.append(arrays["motion_guard_milliseconds"].astype("float64"))
        row_count += count
        content_rows.append({"sha256": digest, "rows": count})
    if row_count == 0:
        raise RealDualReversalRefusal(REFUSAL_IDS[11], "physiology rows are empty")
    mean_trace = trace_sum.mean(axis=0) / row_count
    boundaries = np.linspace(0, len(mean_trace), 5, dtype="int64")
    readiness_bins = [
        float(mean_trace[boundaries[index] : boundaries[index + 1]].mean())
        for index in range(4)
    ]
    feature_means = feature_sum / row_count
    guards = np.concatenate(guard_values)
    summary = {
        "source": "target_free_nonselecting_frozen_before_score",
        "shards": len(paths),
        "rows": row_count,
        "content_set_sha256": _canonical_sha256(content_rows),
        "readiness_trace_sha256": _array_sha256(mean_trace.astype("float32")),
        "readiness_four_bin_mean_volts": readiness_bins,
        "central_8_to_13_Hz_causal_power_mean": float(feature_means[3]),
        "central_13_to_30_Hz_causal_power_mean": float(feature_means[4]),
        "early_vs_late_central_negativity_mean": float(feature_means[5]),
        "motion_guard_milliseconds": {
            "minimum": float(guards.min()),
            "median": float(np.median(guards)),
            "mean": float(guards.mean()),
        },
        "individual_or_participant_records_published": False,
        "selects_model_or_threshold": False,
    }
    if summary["motion_guard_milliseconds"]["minimum"] < 30.0 - 1e-6:
        raise RealDualReversalRefusal(REFUSAL_IDS[10], "motion guard minimum differs")
    return summary


def load_sealed_scorer_stage(
    *,
    private_root: str | Path,
    contract: Mapping[str, Any],
    model_stage: Mapping[str, Any],
) -> dict[str, Any]:
    """Deliver all sealed final targets in one scorer-only invocation."""

    np = _np()
    _validate_target_free_model_stage(model_stage, contract=contract)
    root = Path(private_root)
    manifest = json.loads(
        _read_regular_bytes(
            root / "private_derivative_manifest.v0.json", 4 * 1024 * 1024
        ).decode("utf-8")
    )
    run_summaries = manifest.get("run_summaries", [])
    expected_by_name = {
        f"group_{index:03d}.npz": summary["sealed_shard_sha256"]
        for index, summary in enumerate(run_summaries)
        if summary.get("sealed_shard_sha256") is not None
    }
    paths = _regular_files(root / "derivatives" / "sealed", suffix=".npz")
    if {path.name for path in paths} != set(expected_by_name):
        raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed shard inventory differs")
    identity_to_key = {}
    for key, rows in model_stage["final"].items():
        for item_id in rows["item_ids"].tolist():
            if item_id in identity_to_key:
                raise RealDualReversalFailure(REFUSAL_IDS[14], "final identity collides")
            identity_to_key[item_id] = key
    sealed: dict[str, dict[str, Any]] = {}
    cap = int(
        contract["resource_caps"]["future_acquisition_and_derivative_build"][
            "private_derivative_bytes"
        ]
    )
    for path in paths:
        payload = _read_regular_bytes(path, cap)
        if _sha256_bytes(payload) != expected_by_name[path.name]:
            raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed shard hash differs")
        try:
            with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
                arrays = {name: archive[name] for name in archive.files}
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed shard differs") from exc
        expected = {
            f"{arm}_{name}"
            for arm in ("C2I", "I2C")
            for name in ("item_ids", "actual_action", "cue_surrogate")
        }
        if set(arrays) != expected:
            raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed schema differs")
        for arm in ("C2I", "I2C"):
            item_ids = arrays[f"{arm}_item_ids"]
            actual = arrays[f"{arm}_actual_action"]
            cue = arrays[f"{arm}_cue_surrogate"]
            if (
                item_ids.ndim != 1
                or actual.shape != item_ids.shape
                or cue.shape != item_ids.shape
                or not np.array_equal(cue, 1 - actual)
                or set(actual.tolist()) != {0, 1}
            ):
                raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed targets differ")
            keys = {identity_to_key.get(item_id) for item_id in item_ids.tolist()}
            if None in keys or len(keys) != 1:
                raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed identity differs")
            key = next(iter(keys))
            if not key.startswith(f"{arm}|") or key in sealed:
                raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed arm differs")
            if not np.array_equal(item_ids, model_stage["final"][key]["item_ids"]):
                raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed order differs")
            minimum = int(
                contract["split_contract"][
                    "minimum_final_rows_per_action_direction_per_unit_per_arm"
                ]
            )
            if int(np.bincount(actual.astype("int8"), minlength=2).min()) < minimum:
                raise RealDualReversalFailure(REFUSAL_IDS[10], "final class minimum failed")
            sealed[key] = {
                "item_ids": item_ids,
                "actual_action": actual,
                "cue_surrogate": cue,
            }
    if set(sealed) != set(model_stage["final"]):
        raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed unit inventory differs")
    sealed_rows = sum(len(rows["item_ids"]) for rows in sealed.values())
    if sealed_rows != model_stage["final_rows"]:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "sealed row count differs")
    return {
        "sealed": sealed,
        "sealed_rows": sealed_rows,
        "final_item_ids_sha256": model_stage["final_item_ids_sha256"],
        "sealed_shard_reads": len(paths),
    }

def build_prediction_freeze(
    *,
    source_kind: str,
    matrix: Mapping[str, Any],
    model_stage: Mapping[str, Any],
    contract: Mapping[str, Any],
    implementation_commit: str,
    acquisition_receipt_sha256: str,
    provenance: Mapping[str, Any],
    physiology_summary: Mapping[str, Any],
    private_prediction_payload_sha256: str,
    measurements: Mapping[str, Any],
    access_counters: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one aggregate hash-only prediction freeze."""

    _validate_matrix(matrix, model_stage=model_stage, contract=contract)
    if source_kind not in {"generated_fixture", "real_public_IACKD2"}:
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze source differs")
    hashes = (
        acquisition_receipt_sha256,
        provenance.get("private_manifest_sha256"),
        provenance.get("source_binding_set_sha256"),
        provenance.get("source_hash_set_sha256"),
        provenance.get("derivative_set_sha256"),
        private_prediction_payload_sha256,
    )
    if not all(_is_sha256(value) for value in hashes):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze provenance differs")
    record = {
        "schema_name": "neurodecodekit.iackd2_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "status": "frozen_target_blind_predictions_targets_sealed",
        "source_kind": source_kind,
        "proof_posture": "aggregate_hash_only_no_final_target_delivery_or_score",
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": semantics.POLICY_SHA256,
        "decision_sha256": DECISION_SHA256,
        "implementation_commit": implementation_commit,
        "acquisition_receipt_sha256": acquisition_receipt_sha256,
        "private_manifest_sha256": provenance["private_manifest_sha256"],
        "source_binding_set_sha256": provenance["source_binding_set_sha256"],
        "source_hash_set_sha256": provenance["source_hash_set_sha256"],
        "derivative_set_sha256": provenance["derivative_set_sha256"],
        "split_sha256": model_stage["split_sha256"],
        "final_item_ids_sha256": model_stage["final_item_ids_sha256"],
        "condition_prediction_sha256": dict(matrix["condition_prediction_sha256"]),
        "canonical_private_prediction_sha256": matrix[
            "canonical_private_prediction_sha256"
        ],
        "private_prediction_payload_sha256": private_prediction_payload_sha256,
        "inventory": {
            "participant_hand_units": 30,
            "arms": 2,
            "fit_rows": model_stage["fit_rows"],
            "target_free_final_rows": model_stage["final_rows"],
            "parameter_update_fits": matrix["parameter_update_fits"],
            "target_blind_inference_calls": matrix["target_blind_inference_calls"],
            "prediction_sets": matrix["prediction_sets"],
        },
        "target_firewall": {
            "final_target_rows_visible_to_model_stage": 0,
            "final_target_deliveries": 0,
            "scoring_events": 0,
            "individual_predictions_published": False,
            "participant_outcomes_published": False,
            "same_predictions_bound_to_both_future_target_views": True,
            "freeze_must_be_remotely_green_before_score": True,
            "post_target_updates": 0,
        },
        "physiology": dict(physiology_summary),
        "measurements": dict(measurements),
        "access_counters": dict(access_counters),
        "warnings": [
            "offline_oracle_aligned_causal_in_samples_not_real_time",
            "end_to_end_latency_not_measured",
            "final_targets_remain_sealed",
            "target_firewall_is_a_function_and_artifact_boundary_not_an_OS_sandbox",
        ],
        "unavailable_fields": [
            "synchronized_EMG",
            "independent_movement_onset_instrument",
            "end_to_end_latency",
            "brain_specific_origin",
        ],
        "claim_boundary": {
            "engineering_state": "target_blind_predictions_frozen_not_scored",
            "scientific_claim": False,
        },
    }
    record["freeze_record_sha256"] = _canonical_sha256(record)
    validate_public_freeze(record)
    return record


def validate_public_freeze(freeze: Mapping[str, Any]) -> None:
    required = {
        "schema_name",
        "schema_version",
        "status",
        "source_kind",
        "proof_posture",
        "contract_sha256",
        "policy_sha256",
        "decision_sha256",
        "implementation_commit",
        "acquisition_receipt_sha256",
        "private_manifest_sha256",
        "source_binding_set_sha256",
        "source_hash_set_sha256",
        "derivative_set_sha256",
        "split_sha256",
        "final_item_ids_sha256",
        "condition_prediction_sha256",
        "canonical_private_prediction_sha256",
        "private_prediction_payload_sha256",
        "inventory",
        "target_firewall",
        "physiology",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
        "freeze_record_sha256",
    }
    if set(freeze) != required:
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze schema differs")
    unhashed = dict(freeze)
    observed_hash = unhashed.pop("freeze_record_sha256")
    digest_fields = (
        observed_hash,
        freeze["contract_sha256"],
        freeze["policy_sha256"],
        freeze["decision_sha256"],
        freeze["acquisition_receipt_sha256"],
        freeze["private_manifest_sha256"],
        freeze["source_binding_set_sha256"],
        freeze["source_hash_set_sha256"],
        freeze["derivative_set_sha256"],
        freeze["split_sha256"],
        freeze["final_item_ids_sha256"],
        freeze["canonical_private_prediction_sha256"],
        freeze["private_prediction_payload_sha256"],
    )
    if (
        freeze["schema_name"] != "neurodecodekit.iackd2_prediction_freeze"
        or freeze["schema_version"] != SCHEMA_VERSION
        or freeze["status"] != "frozen_target_blind_predictions_targets_sealed"
        or freeze["source_kind"] not in {"generated_fixture", "real_public_IACKD2"}
        or freeze["contract_sha256"] != CONTRACT_SHA256
        or freeze["policy_sha256"] != semantics.POLICY_SHA256
        or freeze["decision_sha256"] != DECISION_SHA256
        or not all(_is_sha256(value) for value in digest_fields)
        or observed_hash != _canonical_sha256(unhashed)
        or set(freeze["condition_prediction_sha256"]) != set(core.CONDITION_IDS)
        or not all(
            _is_sha256(value)
            for value in freeze["condition_prediction_sha256"].values()
        )
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze identity differs")
    inventory = freeze["inventory"]
    firewall = freeze["target_firewall"]
    zero_counter_names = (
        "final_target_deliveries",
        "scoring_runs",
        "post_target_updates",
        "old_retained_bundle_operations",
        "network_bytes",
        "retries",
        "reruns",
    )
    if (
        inventory.get("participant_hand_units") != 30
        or inventory.get("arms") != 2
        or inventory.get("parameter_update_fits") != 660
        or inventory.get("target_blind_inference_calls") != 900
        or inventory.get("prediction_sets") != 900
        or firewall
        != {
            "final_target_rows_visible_to_model_stage": 0,
            "final_target_deliveries": 0,
            "scoring_events": 0,
            "individual_predictions_published": False,
            "participant_outcomes_published": False,
            "same_predictions_bound_to_both_future_target_views": True,
            "freeze_must_be_remotely_green_before_score": True,
            "post_target_updates": 0,
        }
        or freeze["claim_boundary"] != {
            "engineering_state": "target_blind_predictions_frozen_not_scored",
            "scientific_claim": False,
        }
        or any(freeze["access_counters"].get(name, 0) != 0 for name in zero_counter_names)
        or freeze["measurements"].get("producer_is_causal_in_samples") is not True
        or freeze["measurements"].get("end_to_end_latency_measured") is not False
        or freeze["physiology"].get("selects_model_or_threshold") is not False
        or freeze["physiology"].get("individual_or_participant_records_published")
        is not False
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze firewall differs")
    rendered = json.dumps(freeze, sort_keys=True)
    if any(token in rendered for token in ("/Users/", "/private/", "individual_outcome")):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "freeze leaks protected detail")


def validate_freeze_against_matrix(
    freeze: Mapping[str, Any],
    *,
    matrix: Mapping[str, Any],
    model_stage: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    validate_public_freeze(freeze)
    _validate_matrix(matrix, model_stage=model_stage, contract=contract)
    if (
        freeze["condition_prediction_sha256"]
        != matrix["condition_prediction_sha256"]
        or freeze["canonical_private_prediction_sha256"]
        != matrix["canonical_private_prediction_sha256"]
        or freeze["split_sha256"] != model_stage["split_sha256"]
        or freeze["final_item_ids_sha256"]
        != model_stage["final_item_ids_sha256"]
        or freeze["inventory"]["fit_rows"] != model_stage["fit_rows"]
        or freeze["inventory"]["target_free_final_rows"]
        != model_stage["final_rows"]
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze matrix binding differs")


def score_frozen_matrix(
    *,
    matrix: Mapping[str, Any],
    model_stage: Mapping[str, Any],
    scorer_stage: Mapping[str, Any],
    freeze: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Score the same frozen predictions against action and exact-opposite cue views."""

    np = _np()
    validate_freeze_against_matrix(
        freeze,
        matrix=matrix,
        model_stage=model_stage,
        contract=contract,
    )
    if (
        set(scorer_stage)
        != {"sealed", "sealed_rows", "final_item_ids_sha256", "sealed_shard_reads"}
        or scorer_stage["sealed_rows"] != model_stage["final_rows"]
        or scorer_stage["final_item_ids_sha256"]
        != model_stage["final_item_ids_sha256"]
        or set(scorer_stage["sealed"]) != set(model_stage["final"])
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[14], "scorer-stage binding differs")
    sealed = scorer_stage["sealed"]
    for key in sorted(sealed):
        if (
            not np.array_equal(
                sealed[key]["item_ids"], model_stage["final"][key]["item_ids"]
            )
            or not np.array_equal(
                sealed[key]["cue_surrogate"], 1 - sealed[key]["actual_action"]
            )
        ):
            raise RealDualReversalFailure(REFUSAL_IDS[14], "scorer targets differ")
    try:
        metrics = {
            arm: {
                condition: core._condition_metrics(
                    arm=arm,
                    condition=condition,
                    predictions=matrix["predictions"],
                    sealed=sealed,
                )
                for condition in core.CONDITION_IDS
            }
            for arm in ("C2I", "I2C")
        }
    except core.DualReversalRefusal as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "aggregate scoring failed") from exc
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
        projected = metrics[arm]["fit_only_EOG_orthogonalized_primary"]
        timing = metrics[arm]["event_index_and_timing_only"]
        prewindow = metrics[arm]["pre_window_baseline"]
        controls_pass = all(
            metrics[arm][condition]["macro_participant_action_balanced_accuracy"]
            <= 0.55
            and metrics[arm][condition]["macro_action_minus_cue_margin"] <= 0.10
            for condition in core.FIXED_CONTROL_IDS
        )
        H2[arm] = all(
            (
                primary["macro_participant_action_balanced_accuracy"]
                - eog["macro_participant_action_balanced_accuracy"]
                >= 0.05,
                primary["macro_participant_action_balanced_accuracy"]
                - occipital["macro_participant_action_balanced_accuracy"]
                >= 0.03,
                projected["macro_participant_action_balanced_accuracy"] >= 0.58,
                projected["macro_action_minus_cue_margin"] >= 0.16,
                eog["macro_action_minus_cue_margin"] <= 0.10,
                occipital["macro_action_minus_cue_margin"] <= 0.10,
                timing["macro_participant_action_balanced_accuracy"] <= 0.55,
                prewindow["macro_participant_action_balanced_accuracy"] <= 0.55,
                controls_pass,
            )
        )
        central = metrics[arm]["central_C3_C4_Cz"]
        H3[arm] = all(
            (
                central["macro_participant_action_balanced_accuracy"] >= 0.55,
                central["macro_action_minus_cue_margin"] >= 0.10,
                central["participants_above_0_5_action_balanced_accuracy"] >= 10,
                freeze["physiology"].get("selects_model_or_threshold") is False,
                freeze["physiology"].get("shards", 0) > 0,
            )
        )
    participant_minimum = [
        min(c2i, i2c)
        for c2i, i2c in zip(
            metrics["C2I"]["whole_head_primary"]["participant_margins_private"],
            metrics["I2C"]["whole_head_primary"]["participant_margins_private"],
            strict=True,
        )
    ]
    central_minimum = [
        min(c2i, i2c)
        for c2i, i2c in zip(
            metrics["C2I"]["central_C3_C4_Cz"]["participant_margins_private"],
            metrics["I2C"]["central_C3_C4_Cz"]["participant_margins_private"],
            strict=True,
        )
    ]
    try:
        minimum_p = core._sign_flip_p(participant_minimum)
    except core.DualReversalRefusal as exc:
        raise RealDualReversalFailure(REFUSAL_IDS[14], "sign-flip test failed") from exc
    conjunction_H1 = sum(participant_minimum) / 15.0 >= 0.15 and minimum_p <= 0.01
    conjunction_H3 = sum(central_minimum) / 15.0 >= 0.08
    H0 = all(
        (
            matrix["parameter_update_fits"] == 660,
            matrix["prediction_sets"] == 900,
            scorer_stage["sealed_rows"] == model_stage["final_rows"],
            freeze["target_firewall"]["final_target_deliveries"] == 0,
            freeze["target_firewall"]["scoring_events"] == 0,
            freeze["target_firewall"]["post_target_updates"] == 0,
        )
    )
    cue_bound = all(
        metrics[arm]["whole_head_primary"][
            "macro_participant_cue_balanced_accuracy"
        ]
        >= 0.60
        and metrics[arm]["whole_head_primary"]["macro_action_minus_cue_margin"]
        <= -0.20
        for arm in ("C2I", "I2C")
    )
    route = core.route_from_gate_flags(
        H0=H0,
        cue_bound_both_arms=cue_bound,
        H1_C2I=H1["C2I"] and conjunction_H1,
        H1_I2C=H1["I2C"] and conjunction_H1,
        H2=H2["C2I"] and H2["I2C"],
        H3=H3["C2I"] and H3["I2C"] and conjunction_H3,
    )
    maximum_claim = next(
        row["maximum_claim"]
        for row in contract["ordered_router"]
        if row["route"] == route
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
        "route": route,
        "maximum_claim": maximum_claim,
        "H0": H0,
        "H1": H1,
        "H1_conjunction": conjunction_H1,
        "H2": H2,
        "H3": H3,
        "H3_conjunction": conjunction_H3,
        "cue_bound_both_arms": cue_bound,
        "participant_minimum_arm_margin_mean": sum(participant_minimum) / 15.0,
        "participant_minimum_arm_exact_sign_flip_p": minimum_p,
        "central_minimum_arm_margin_mean": sum(central_minimum) / 15.0,
        "aggregate_metrics": public_metrics,
        "physiology": freeze["physiology"],
        "individual_participant_metrics_published": False,
        "one_arm_rescue_allowed": False,
    }


def _git_head(root: Path) -> str:
    result = _git(root, "rev-parse", "HEAD")
    if result.returncode:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "Git HEAD is unavailable")
    return result.stdout.strip()


def _tracked_at_head(root: Path, relative: Path) -> bool:
    return _git(root, "cat-file", "-e", f"HEAD:{relative.as_posix()}").returncode == 0


def _validate_implementation_registry(
    *,
    repo_root: Path,
    evidence: ImplementationEvidence,
    require_exact_head: bool,
) -> dict[str, Any]:
    head = _git_head(repo_root)
    if require_exact_head and head != evidence.implementation_commit:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "HEAD differs from implementation")
    if (
        len(evidence.implementation_commit) != 40
        or min(
            evidence.implementation_CI_run_id,
            evidence.base_python_job_id,
            evidence.optional_neuro_job_id,
        )
        <= 0
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation evidence differs")
    if _git(repo_root, "merge-base", "--is-ancestor", DECISION_COMMIT, head).returncode:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "decision is not an ancestor")
    if _git(
        repo_root,
        "merge-base",
        "--is-ancestor",
        evidence.implementation_commit,
        head,
    ).returncode:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation is not an ancestor")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "tracked worktree is not clean")
    if not _tracked_at_head(repo_root, IMPLEMENTATION_RELATIVE_PATH):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation registry is untracked")
    path = repo_root / IMPLEMENTATION_RELATIVE_PATH
    try:
        registry = json.loads(_read_regular_bytes(path, 4 * 1024 * 1024).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation registry differs") from exc
    if (
        registry.get("schema_name")
        != "neurodecodekit.iackd_role_aware_dual_reversal_real_implementation"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("status")
        != "generated_fixture_qualified_exact_real_executor_requires_remote_green_before_public_access"
        or registry.get("green_authorization_decision")
        != {
            "commit": DECISION_COMMIT,
            "push_CI_run_id": DECISION_CI_RUN_ID,
            "base_python_job_id": DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        }
        or registry.get("fixture_qualification", {}).get("all_gates_passed") is not True
        or any(registry.get("implementation_real_access_counters", {}).values())
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation proof differs")
    for row in registry.get("tracked_file_hashes", []):
        tracked = repo_root / _safe_relative_path(str(row.get("path", "")))
        if _file_sha256(tracked) != row.get("sha256"):
            raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation file hash differs")
    if registry.get("optional_environment", {}).get("qualified_versions") != dependency_versions():
        raise RealDualReversalRefusal(REFUSAL_IDS[1], "implementation environment differs")
    return registry


def _load_public_receipt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read_regular_bytes(path, 4 * 1024 * 1024).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "public receipt differs") from exc
    if not isinstance(value, dict):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "public receipt root differs")
    _validate_public_receipt(value)
    return value


def run_registered_streaming_execution(
    *,
    repo_root: str | Path,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
    opener: URLopener = _open_url_once,
) -> dict[str, Any]:
    """Perform the sole registered fresh IACKD-2 stream after green implementation."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    inventory = load_registered_inventory(root)
    _check_thread_environment(environ)
    _validate_implementation_registry(
        repo_root=root,
        evidence=evidence,
        require_exact_head=True,
    )
    return run_streaming_derivative_build(
        workspace_root=root,
        contract=contract,
        inventory=inventory,
        opener=opener,
        environ=environ,
        private_root_relative=PRIVATE_ROOT_RELATIVE_PATH,
        public_receipt_relative=PUBLIC_RECEIPT_RELATIVE_PATH,
        strict_registered=True,
        implementation_commit=evidence.implementation_commit,
    )


def _finalize_freeze_bytes(
    freeze: dict[str, Any],
    *,
    maximum_bytes: int,
) -> bytes:
    for _ in range(8):
        freeze.pop("freeze_record_sha256", None)
        freeze["freeze_record_sha256"] = _canonical_sha256(freeze)
        payload = _json_bytes(freeze)
        if freeze["measurements"].get("public_freeze_bytes") == len(payload):
            break
        freeze["measurements"]["public_freeze_bytes"] = len(payload)
    else:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "freeze bytes did not converge")
    validate_public_freeze(freeze)
    payload = _json_bytes(freeze)
    if len(payload) > maximum_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "freeze exceeds output cap")
    return payload


def run_registered_target_blind_analysis(
    *,
    repo_root: str | Path,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Consume the sole 660-fit/900-prediction run and stop at a target-free freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    _validate_implementation_registry(
        repo_root=root,
        evidence=evidence,
        require_exact_head=False,
    )
    if not _tracked_at_head(root, PUBLIC_RECEIPT_RELATIVE_PATH):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "acquisition receipt is not tracked")
    receipt_path = root / PUBLIC_RECEIPT_RELATIVE_PATH
    receipt = _load_public_receipt(receipt_path)
    if (
        receipt["contract_sha256"] != CONTRACT_SHA256
        or receipt["decision_sha256"] != DECISION_SHA256
        or receipt["implementation_commit"] != evidence.implementation_commit
        or receipt["measurements"]["payload_requests"] != 1340
        or receipt["measurements"]["payload_bytes"] != 7_249_113_684
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "acquisition receipt binding differs")
    private_root = root / PRIVATE_ROOT_RELATIVE_PATH
    consumed_path = private_root / "analysis_consumed.v0.json"
    prediction_path = private_root / "private_predictions.v0.npz"
    freeze_path = root / PUBLIC_FREEZE_RELATIVE_PATH
    for path in (consumed_path, prediction_path, freeze_path):
        if path.exists() or path.is_symlink():
            raise RealDualReversalRefusal(REFUSAL_IDS[15], "analysis is already consumed")
    _write_exclusive(
        consumed_path,
        _json_bytes(
            {
                "schema_name": "neurodecodekit.iackd2_analysis_consumed",
                "schema_version": SCHEMA_VERSION,
                "started_at_UTC": _utc_now(),
                "implementation_commit": evidence.implementation_commit,
                "retry_allowed": False,
                "rerun_allowed": False,
            }
        ),
        64 * 1024,
    )
    started = time.monotonic()
    loaded = load_target_free_model_stage(
        private_root=private_root,
        contract=contract,
        public_receipt=receipt,
    )
    model_stage = loaded["model_stage"]
    physiology = load_target_free_physiology_summary(
        private_root=private_root,
        contract=contract,
    )
    matrix = run_target_blind_model_matrix(model_stage, contract=contract)
    prediction_payload = _private_prediction_bytes(
        matrix,
        model_stage=model_stage,
        contract=contract,
    )
    caps = contract["resource_caps"]["future_fit_freeze_and_score"]
    _write_exclusive(
        prediction_path,
        prediction_payload,
        int(caps["private_generated_output_bytes"]),
    )
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    private_bytes = _directory_bytes(private_root)
    if (
        runtime > float(caps["wall_time_seconds_through_prediction_freeze"])
        or peak_rss > int(caps["peak_RSS_bytes"])
        or private_bytes > int(caps["private_generated_output_bytes"])
    ):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "analysis resource cap exceeded")
    receipt_sha256 = _file_sha256(receipt_path)
    freeze = build_prediction_freeze(
        source_kind="real_public_IACKD2",
        matrix=matrix,
        model_stage=model_stage,
        contract=contract,
        implementation_commit=evidence.implementation_commit,
        acquisition_receipt_sha256=receipt_sha256,
        provenance=loaded["provenance"],
        physiology_summary=physiology,
        private_prediction_payload_sha256=_sha256_bytes(prediction_payload),
        measurements={
            "input_payload_bytes": receipt["measurements"]["payload_bytes"],
            "model_shard_input_bytes": loaded["provenance"]["model_shard_bytes"],
            "private_prediction_bytes": len(prediction_payload),
            "private_execution_bytes": private_bytes,
            "public_freeze_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "producer_is_causal_in_samples": True,
            "end_to_end_latency_measured": False,
        },
        access_counters={
            "raw_data_reads": 0,
            "real_cache_reads": loaded["provenance"]["model_shard_reads"] + 128,
            "model_parameter_update_fits": matrix["parameter_update_fits"],
            "target_blind_model_inference_calls": matrix[
                "target_blind_inference_calls"
            ],
            "prediction_sets": matrix["prediction_sets"],
            "sealed_target_shard_reads": 0,
            "final_target_deliveries": 0,
            "scoring_runs": 0,
            "post_target_updates": 0,
            "network_bytes": 0,
            "retries": 0,
            "reruns": 0,
            "old_retained_bundle_operations": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
        },
    )
    freeze_payload = _finalize_freeze_bytes(
        freeze,
        maximum_bytes=int(caps["public_freeze_and_result_bytes"]),
    )
    _write_exclusive(
        freeze_path,
        freeze_payload,
        int(caps["public_freeze_and_result_bytes"]),
    )
    return freeze


def _finalize_result_bytes(
    result: dict[str, Any],
    *,
    maximum_bytes: int,
) -> bytes:
    for _ in range(8):
        result.pop("result_record_sha256", None)
        result["result_record_sha256"] = _canonical_sha256(result)
        payload = _json_bytes(result)
        if result["measurements"].get("public_result_bytes") == len(payload):
            break
        result["measurements"]["public_result_bytes"] = len(payload)
    else:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "result bytes did not converge")
    validate_public_result(result)
    payload = _json_bytes(result)
    if len(payload) > maximum_bytes:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "result exceeds output cap")
    return payload


def validate_public_result(result: Mapping[str, Any]) -> None:
    required = {
        "schema_name",
        "schema_version",
        "status",
        "source_kind",
        "contract_sha256",
        "decision_sha256",
        "implementation_commit",
        "freeze_evidence",
        "freeze_record_sha256",
        "acquisition_receipt_sha256",
        "score",
        "inventory",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
        "result_record_sha256",
    }
    if set(result) != required:
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "result schema differs")
    unhashed = dict(result)
    observed_hash = unhashed.pop("result_record_sha256")
    contract = load_registered_contract()
    routes = {
        row["route"]: row["maximum_claim"] for row in contract["ordered_router"]
    }
    freeze_evidence = result["freeze_evidence"]
    score = result["score"]
    inventory = result["inventory"]
    measurements = result["measurements"]
    counters = result["access_counters"]
    claim_boundary = result["claim_boundary"]
    mappings = (
        freeze_evidence,
        score,
        inventory,
        measurements,
        counters,
        claim_boundary,
    )
    if not all(isinstance(value, Mapping) for value in mappings):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "result fields differ")
    expected_freeze_evidence = {
        "commit",
        "push_CI_run_id",
        "base_python_job_id",
        "optional_neuro_job_id",
        "both_required_jobs_green",
    }
    expected_inventory = {
        "participants",
        "participant_hand_units",
        "arms",
        "fit_rows",
        "final_rows",
        "parameter_update_fits",
        "prediction_sets",
    }
    expected_measurements = {
        "input_payload_bytes",
        "acquisition_runtime_seconds",
        "target_blind_runtime_seconds",
        "scoring_runtime_seconds",
        "peak_RSS_bytes",
        "public_result_bytes",
        "producer_is_causal_in_samples",
        "end_to_end_latency_measured",
    }
    expected_counters = {
        "raw_payload_reads",
        "real_signal_run_parses",
        "scorer_model_cache_reads",
        "sealed_target_shard_reads",
        "model_parameter_update_fits",
        "target_blind_model_inference_calls",
        "prediction_sets",
        "final_target_deliveries",
        "scoring_runs",
        "post_target_updates",
        "network_bytes_during_analysis_and_score",
        "retries",
        "reruns",
        "old_retained_bundle_operations",
        "provider_or_language_model_calls",
        "hardware_operations",
    }
    caps = contract["resource_caps"]
    scoring_caps = caps["future_fit_freeze_and_score"]
    acquisition_caps = caps["future_acquisition_and_derivative_build"]
    split = contract["split_contract"]
    maximum_counts = split["maximum_pre_quality_control_counts"]
    minimum_fit_rows = (
        int(split["participant_hand_unit_count"])
        * int(split["arm_count"])
        * 2
        * int(split["minimum_fit_rows_per_action_direction_per_unit_per_arm"])
    )
    minimum_final_rows = (
        int(split["participant_hand_unit_count"])
        * int(split["arm_count"])
        * 2
        * int(split["minimum_final_rows_per_action_direction_per_unit_per_arm"])
    )
    zero_counter_names = (
        "post_target_updates",
        "network_bytes_during_analysis_and_score",
        "retries",
        "reruns",
        "old_retained_bundle_operations",
        "provider_or_language_model_calls",
        "hardware_operations",
    )
    if (
        result["schema_name"] != "neurodecodekit.iackd2_result"
        or result["schema_version"] != SCHEMA_VERSION
        or result["status"] != "complete_one_frozen_score_no_rerun"
        or result["source_kind"] != "real_public_IACKD2"
        or result["contract_sha256"] != CONTRACT_SHA256
        or result["decision_sha256"] != DECISION_SHA256
        or re.fullmatch(r"[0-9a-f]{40}", str(result["implementation_commit"]))
        is None
        or set(freeze_evidence) != expected_freeze_evidence
        or re.fullmatch(r"[0-9a-f]{40}", str(freeze_evidence.get("commit"))) is None
        or min(
            int(freeze_evidence.get("push_CI_run_id", 0)),
            int(freeze_evidence.get("base_python_job_id", 0)),
            int(freeze_evidence.get("optional_neuro_job_id", 0)),
        )
        <= 0
        or freeze_evidence.get("both_required_jobs_green") is not True
        or not _is_sha256(result["freeze_record_sha256"])
        or not _is_sha256(result["acquisition_receipt_sha256"])
        or not _is_sha256(observed_hash)
        or observed_hash != _canonical_sha256(unhashed)
        or score.get("route") not in routes
        or score.get("maximum_claim") != routes[score.get("route")]
        or score.get("individual_participant_metrics_published") is not False
        or score.get("one_arm_rescue_allowed") is not False
        or set(inventory) != expected_inventory
        or inventory.get("participants") != 15
        or inventory.get("participant_hand_units")
        != int(split["participant_hand_unit_count"])
        or inventory.get("arms") != int(split["arm_count"])
        or not minimum_fit_rows
        <= int(inventory.get("fit_rows", -1))
        <= int(maximum_counts["both_arms_fit_rows"])
        or not minimum_final_rows
        <= int(inventory.get("final_rows", -1))
        <= int(maximum_counts["both_arms_final_rows"])
        or inventory.get("parameter_update_fits")
        != int(scoring_caps["required_parameter_update_fits"])
        or inventory.get("prediction_sets")
        != int(scoring_caps["required_prediction_sets"])
        or set(measurements) != expected_measurements
        or measurements.get("input_payload_bytes")
        != int(acquisition_caps["payload_bytes"])
        or min(
            float(measurements.get("acquisition_runtime_seconds", 0.0)),
            float(measurements.get("target_blind_runtime_seconds", 0.0)),
            float(measurements.get("scoring_runtime_seconds", 0.0)),
        )
        <= 0.0
        or int(measurements.get("peak_RSS_bytes", -1))
        > max(
            int(acquisition_caps["peak_RSS_bytes"]),
            int(scoring_caps["peak_RSS_bytes"]),
        )
        or not 0 < int(measurements.get("public_result_bytes", 0)) <= int(
            scoring_caps["public_freeze_and_result_bytes"]
        )
        or measurements.get("producer_is_causal_in_samples") is not True
        or measurements.get("end_to_end_latency_measured") is not False
        or set(counters) != expected_counters
        or counters.get("raw_payload_reads") != int(acquisition_caps["payload_requests"])
        or counters.get("real_signal_run_parses") != 128
        or counters.get("scorer_model_cache_reads") != 128
        or counters.get("sealed_target_shard_reads") != 128
        or counters.get("model_parameter_update_fits")
        != int(scoring_caps["required_parameter_update_fits"])
        or counters.get("target_blind_model_inference_calls")
        != int(scoring_caps["maximum_target_blind_inference_calls"])
        or counters.get("prediction_sets")
        != int(scoring_caps["required_prediction_sets"])
        or counters.get("final_target_deliveries")
        != int(scoring_caps["target_deliveries"])
        or counters.get("scoring_runs") != int(scoring_caps["scoring_events"])
        or any(counters.get(name) != 0 for name in zero_counter_names)
        or claim_boundary.get("registered_scientific_outcome")
        != score.get("maximum_claim")
        or claim_boundary.get("not_established")
        != "brain_specific_origin_unseen_person_generalization_language_or_thought_decoding_real_time_hardware_home_use_assistive_or_clinical_result"
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "result identity differs")
    rendered = json.dumps(result, sort_keys=True)
    if any(token in rendered for token in ("/Users/", "/private/", "participant_margins_private")):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "result leaks protected detail")


def score_registered_execution(
    *,
    repo_root: str | Path,
    evidence: FreezeEvidence,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Deliver both target views together once after the freeze commit is green."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    if (
        _git_head(root) != evidence.freeze_commit
        or len(evidence.freeze_commit) != 40
        or min(
            evidence.freeze_CI_run_id,
            evidence.base_python_job_id,
            evidence.optional_neuro_job_id,
        )
        <= 0
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze evidence differs")
    if _git(root, "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD").returncode:
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "decision is not a freeze ancestor")
    if _git(root, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "tracked worktree is not clean")
    if not _tracked_at_head(root, PUBLIC_FREEZE_RELATIVE_PATH):
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze is not tracked")
    freeze_path = root / PUBLIC_FREEZE_RELATIVE_PATH
    freeze = json.loads(_read_regular_bytes(freeze_path, 4 * 1024 * 1024).decode("utf-8"))
    validate_public_freeze(freeze)
    if freeze["source_kind"] != "real_public_IACKD2":
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "real scorer refuses fixture freeze")
    implementation_commit = str(freeze["implementation_commit"])
    if _git(root, "merge-base", "--is-ancestor", implementation_commit, "HEAD").returncode:
        raise RealDualReversalRefusal(REFUSAL_IDS[14], "implementation is not an ancestor")
    private_root = root / PRIVATE_ROOT_RELATIVE_PATH
    consumed_path = private_root / "scoring_consumed.v0.json"
    result_path = root / PUBLIC_RESULT_RELATIVE_PATH
    if consumed_path.exists() or consumed_path.is_symlink() or result_path.exists() or result_path.is_symlink():
        raise RealDualReversalRefusal(REFUSAL_IDS[15], "score is already consumed")
    _write_exclusive(
        consumed_path,
        _json_bytes(
            {
                "schema_name": "neurodecodekit.iackd2_scoring_consumed",
                "schema_version": SCHEMA_VERSION,
                "started_at_UTC": _utc_now(),
                "freeze_commit": evidence.freeze_commit,
                "retry_allowed": False,
                "rerun_allowed": False,
            }
        ),
        64 * 1024,
    )
    started = time.monotonic()
    receipt_path = root / PUBLIC_RECEIPT_RELATIVE_PATH
    receipt = _load_public_receipt(receipt_path)
    loaded = load_target_free_model_stage(
        private_root=private_root,
        contract=contract,
        public_receipt=receipt,
    )
    model_stage = loaded["model_stage"]
    matrix = _load_private_predictions(
        private_root / "private_predictions.v0.npz",
        expected_sha256=freeze["private_prediction_payload_sha256"],
        maximum_bytes=int(
            contract["resource_caps"]["future_fit_freeze_and_score"][
                "private_generated_output_bytes"
            ]
        ),
        model_stage=model_stage,
        contract=contract,
    )
    validate_freeze_against_matrix(
        freeze,
        matrix=matrix,
        model_stage=model_stage,
        contract=contract,
    )
    scorer_stage = load_sealed_scorer_stage(
        private_root=private_root,
        contract=contract,
        model_stage=model_stage,
    )
    score = score_frozen_matrix(
        matrix=matrix,
        model_stage=model_stage,
        scorer_stage=scorer_stage,
        freeze=freeze,
        contract=contract,
    )
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    caps = contract["resource_caps"]["future_fit_freeze_and_score"]
    if peak_rss > int(caps["peak_RSS_bytes"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "scorer RSS cap exceeded")
    result = {
        "schema_name": "neurodecodekit.iackd2_result",
        "schema_version": SCHEMA_VERSION,
        "status": "complete_one_frozen_score_no_rerun",
        "source_kind": "real_public_IACKD2",
        "contract_sha256": CONTRACT_SHA256,
        "decision_sha256": DECISION_SHA256,
        "implementation_commit": implementation_commit,
        "freeze_evidence": {
            "commit": evidence.freeze_commit,
            "push_CI_run_id": evidence.freeze_CI_run_id,
            "base_python_job_id": evidence.base_python_job_id,
            "optional_neuro_job_id": evidence.optional_neuro_job_id,
            "both_required_jobs_green": True,
        },
        "freeze_record_sha256": freeze["freeze_record_sha256"],
        "acquisition_receipt_sha256": _file_sha256(receipt_path),
        "score": score,
        "inventory": {
            "participants": 15,
            "participant_hand_units": 30,
            "arms": 2,
            "fit_rows": model_stage["fit_rows"],
            "final_rows": model_stage["final_rows"],
            "parameter_update_fits": 660,
            "prediction_sets": 900,
        },
        "measurements": {
            "input_payload_bytes": receipt["measurements"]["payload_bytes"],
            "acquisition_runtime_seconds": receipt["measurements"]["runtime_seconds"],
            "target_blind_runtime_seconds": freeze["measurements"]["runtime_seconds"],
            "scoring_runtime_seconds": runtime,
            "peak_RSS_bytes": max(peak_rss, freeze["measurements"]["peak_RSS_bytes"]),
            "public_result_bytes": 0,
            "producer_is_causal_in_samples": True,
            "end_to_end_latency_measured": False,
        },
        "access_counters": {
            "raw_payload_reads": receipt["measurements"]["payload_requests"],
            "real_signal_run_parses": receipt["access_counters"]["raw_signal_run_parses"],
            "scorer_model_cache_reads": loaded["provenance"]["model_shard_reads"],
            "sealed_target_shard_reads": scorer_stage["sealed_shard_reads"],
            "model_parameter_update_fits": freeze["inventory"]["parameter_update_fits"],
            "target_blind_model_inference_calls": freeze["inventory"][
                "target_blind_inference_calls"
            ],
            "prediction_sets": freeze["inventory"]["prediction_sets"],
            "final_target_deliveries": 1,
            "scoring_runs": 1,
            "post_target_updates": 0,
            "network_bytes_during_analysis_and_score": 0,
            "retries": 0,
            "reruns": 0,
            "old_retained_bundle_operations": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
        },
        "warnings": [
            "source_has_no_synchronized_EMG_or_independent_movement_onset_instrument",
            "controls_do_not_prove_brain_specific_origin",
            "offline_oracle_aligned_causal_in_samples_not_real_time",
            "within_dataset_participant_specific_result_not_unseen_person_generalization",
        ],
        "unavailable_fields": list(freeze["unavailable_fields"]),
        "claim_boundary": {
            "registered_scientific_outcome": score["maximum_claim"],
            "not_established": "brain_specific_origin_unseen_person_generalization_language_or_thought_decoding_real_time_hardware_home_use_assistive_or_clinical_result",
        },
    }
    payload = _finalize_result_bytes(
        result,
        maximum_bytes=int(caps["public_freeze_and_result_bytes"]),
    )
    _write_exclusive(result_path, payload, int(caps["public_freeze_and_result_bytes"]))
    return result


def _expect_generated_refusal(
    operation: Callable[[], Any],
    *,
    expected_id: str,
) -> dict[str, str]:
    try:
        operation()
    except RealDualReversalRefusal as exc:
        if exc.refusal_id != expected_id:
            raise RealDualReversalRefusal(
                REFUSAL_IDS[13], "generated mutation reached a different refusal"
            ) from exc
        return {"refusal_id": exc.refusal_id}
    raise RealDualReversalRefusal(REFUSAL_IDS[13], "generated mutation was accepted")


def _generated_refusal_suite(
    *,
    model_stage: Mapping[str, Any],
    matrix: Mapping[str, Any],
    freeze: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> list[dict[str, str]]:
    np = _np()
    url = "https://fixture.invalid/object"
    body = b"fixture"
    etag = hashlib.md5(body, usedforsecurity=False).hexdigest()  # noqa: S324
    mutations = [
        _expect_generated_refusal(
            lambda: _validate_response(
                FixtureResponse(body=body, url=url, etag=etag, status=500),
                url=url,
                expected_bytes=len(body),
                expected_etag=etag,
            ),
            expected_id=REFUSAL_IDS[5],
        ),
        _expect_generated_refusal(
            lambda: _validate_response(
                FixtureResponse(body=body, url=f"{url}/redirect", etag=etag),
                url=url,
                expected_bytes=len(body),
                expected_etag=etag,
            ),
            expected_id=REFUSAL_IDS[5],
        ),
        _expect_generated_refusal(
            lambda: _validate_response(
                FixtureResponse(body=body, url=url, etag=etag),
                url=url,
                expected_bytes=len(body) + 1,
                expected_etag=etag,
            ),
            expected_id=REFUSAL_IDS[7],
        ),
        _expect_generated_refusal(
            lambda: _validate_response(
                FixtureResponse(body=body, url=url, etag="0" * 32),
                url=url,
                expected_bytes=len(body),
                expected_etag=etag,
            ),
            expected_id=REFUSAL_IDS[7],
        ),
        _expect_generated_refusal(
            lambda: _validate_response(
                FixtureResponse(body=body, url=url, etag=etag, content_encoding="gzip"),
                url=url,
                expected_bytes=len(body),
                expected_etag=etag,
            ),
            expected_id=REFUSAL_IDS[5],
        ),
    ]
    leaked = dict(model_stage)
    leaked_final = dict(model_stage["final"])
    first_key = sorted(leaked_final)[0]
    leaked_rows = dict(leaked_final[first_key])
    leaked_rows["actual_action"] = np.zeros(len(leaked_rows["item_ids"]), dtype="int8")
    leaked_final[first_key] = leaked_rows
    leaked["final"] = leaked_final
    mutations.append(
        _expect_generated_refusal(
            lambda: _validate_target_free_model_stage(leaked, contract=contract),
            expected_id=REFUSAL_IDS[11],
        )
    )
    altered_freeze = dict(freeze)
    altered_freeze["canonical_private_prediction_sha256"] = "0" * 64
    mutations.append(
        _expect_generated_refusal(
            lambda: validate_freeze_against_matrix(
                altered_freeze,
                matrix=matrix,
                model_stage=model_stage,
                contract=contract,
            ),
            expected_id=REFUSAL_IDS[14],
        )
    )
    return mutations


def _qualification_output_preflight(path: Path, maximum_bytes: int) -> None:
    if maximum_bytes <= 0 or maximum_bytes > 8 * 1024 * 1024:
        raise RealDualReversalRefusal(REFUSAL_IDS[13], "qualification cap differs")
    if path.exists() or path.is_symlink():
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "qualification output exists")
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise RealDualReversalRefusal(REFUSAL_IDS[6], "qualification parent differs")


def run_generated_real_executor_qualification(
    output_path: str | Path,
    *,
    environ: Mapping[str, str] | None = None,
    maximum_output_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    """Qualify the real executor with generated payloads and mocked transport only."""

    path = Path(output_path)
    _qualification_output_preflight(path, maximum_output_bytes)
    environment = os.environ if environ is None else environ
    _check_thread_environment(environment)
    started = time.monotonic()
    contract = load_registered_contract()
    load_registered_decision()
    versions = dependency_versions()
    with tempfile.TemporaryDirectory(prefix="iackd2-real-executor-generated-") as temporary:
        workspace = Path(temporary)
        fixture_contract, fixture_inventory, opener = _mock_contract_inventory_transport()
        receipt = run_streaming_derivative_build(
            workspace_root=workspace,
            contract=fixture_contract,
            inventory=fixture_inventory,
            opener=opener,
            environ=environment,
            private_root_relative="private",
            public_receipt_relative="receipt.json",
            strict_registered=False,
            implementation_commit="generated-fixture",
        )
        private_root = workspace / "private"
        physiology = load_target_free_physiology_summary(
            private_root=private_root,
            contract=contract,
            expected_shards=2,
        )
        manifest_payload = _read_regular_bytes(
            private_root / "private_derivative_manifest.v0.json",
            4 * 1024 * 1024,
        )
        manifest = json.loads(manifest_payload.decode("utf-8"))
        provenance = {
            "private_manifest_sha256": _sha256_bytes(manifest_payload),
            "source_binding_set_sha256": _canonical_sha256(
                sorted(row["source_binding_sha256"] for row in manifest["run_summaries"])
            ),
            "source_hash_set_sha256": receipt["derivatives"]["source_hash_set_sha256"],
            "derivative_set_sha256": receipt["derivatives"]["derivative_set_sha256"],
        }
        generated = core.build_generated_derivatives()
        model_stage = generated["model_stage"]
        scorer_stage = {**generated["scorer_stage"], "sealed_shard_reads": 0}
        first_matrix = run_target_blind_model_matrix(model_stage, contract=contract)
        replay_matrix = run_target_blind_model_matrix(model_stage, contract=contract)
        deterministic_replay = (
            first_matrix["canonical_private_prediction_sha256"]
            == replay_matrix["canonical_private_prediction_sha256"]
            and first_matrix["condition_prediction_sha256"]
            == replay_matrix["condition_prediction_sha256"]
        )
        if not deterministic_replay:
            raise RealDualReversalFailure(REFUSAL_IDS[12], "matrix replay differs")
        prediction_payload = _private_prediction_bytes(
            first_matrix,
            model_stage=model_stage,
            contract=contract,
        )
        prediction_path = workspace / "predictions.npz"
        _write_exclusive(prediction_path, prediction_payload, 8 * 1024 * 1024)
        replayed_private = _load_private_predictions(
            prediction_path,
            expected_sha256=_sha256_bytes(prediction_payload),
            maximum_bytes=8 * 1024 * 1024,
            model_stage=model_stage,
            contract=contract,
        )
        freeze = build_prediction_freeze(
            source_kind="generated_fixture",
            matrix=replayed_private,
            model_stage=model_stage,
            contract=contract,
            implementation_commit="generated-fixture",
            acquisition_receipt_sha256=_file_sha256(workspace / "receipt.json"),
            provenance=provenance,
            physiology_summary=physiology,
            private_prediction_payload_sha256=_sha256_bytes(prediction_payload),
            measurements={
                "public_freeze_bytes": 0,
                "producer_is_causal_in_samples": True,
                "end_to_end_latency_measured": False,
            },
            access_counters={
                "real_or_public_reads": 0,
                "old_retained_bundle_operations": 0,
                "final_target_deliveries": 0,
                "scoring_runs": 0,
            },
        )
        score = score_frozen_matrix(
            matrix=replayed_private,
            model_stage=model_stage,
            scorer_stage=scorer_stage,
            freeze=freeze,
            contract=contract,
        )
        mutations = _generated_refusal_suite(
            model_stage=model_stage,
            matrix=replayed_private,
            freeze=freeze,
            contract=contract,
        )
        peak_temporary_bytes = _directory_bytes(workspace)
        mocked_calls = len(opener.calls)  # type: ignore[attr-defined]
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    caps = contract["resource_caps"]["future_generated_implementation"]
    if runtime > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_RSS_bytes"]):
        raise RealDualReversalFailure(REFUSAL_IDS[13], "qualification resource cap exceeded")
    report = {
        "schema_name": "neurodecodekit.iackd2_real_executor_qualification",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_only_no_scientific_result",
        "decision": {
            "commit": DECISION_COMMIT,
            "push_CI_run_id": DECISION_CI_RUN_ID,
            "base_python_job_id": DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": semantics.POLICY_SHA256,
        "dependencies": versions,
        "mock_stream": {
            "payload_requests": receipt["measurements"]["payload_requests"],
            "payload_bytes": receipt["measurements"]["payload_bytes"],
            "metadata_and_payload_calls": mocked_calls,
            "BrainVision_parses": receipt["measurements"]["run_groups"],
            "source_row_signatures": [29, 31],
            "retained_trials": receipt["measurements"]["retained_source_trials"],
            "peak_concurrent_raw_run_groups": receipt["measurements"][
                "peak_concurrent_raw_run_groups"
            ],
            "temporary_raw_groups_retained": 0,
        },
        "target_firewall": {
            "fit_labels_in_fit_blocks_only": True,
            "target_fields_in_final_model_blocks": 0,
            "sealed_views_structurally_separate": True,
            "private_prediction_roundtrip_hash": replayed_private[
                "canonical_private_prediction_sha256"
            ],
            "freeze_hash": freeze["freeze_record_sha256"],
        },
        "model_matrix": {
            "primary_parameter_update_fits": first_matrix["parameter_update_fits"],
            "primary_prediction_sets": first_matrix["prediction_sets"],
            "replay_parameter_update_fits": replay_matrix["parameter_update_fits"],
            "replay_prediction_sets": replay_matrix["prediction_sets"],
            "deterministic_replay": deterministic_replay,
        },
        "synthetic_score": {
            "route": score["route"],
            "all_H0_H1_H2_H3_gates": all(
                (
                    score["H0"],
                    all(score["H1"].values()),
                    score["H1_conjunction"],
                    all(score["H2"].values()),
                    all(score["H3"].values()),
                    score["H3_conjunction"],
                )
            ),
            "has_scientific_value": False,
        },
        "refusal_coverage": {
            "mutation_attempts": len(mutations),
            "refusal_ids": sorted({row["refusal_id"] for row in mutations}),
        },
        "measurements": {
            "input_bytes": receipt["measurements"]["payload_bytes"],
            "private_prediction_bytes": len(prediction_payload),
            "peak_temporary_generated_bytes": peak_temporary_bytes,
            "output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "producer_is_causal_in_samples": True,
            "end_to_end_latency_measured": False,
        },
        "access_counters": {
            "generated_BrainVision_parses": 2,
            "generated_parameter_update_fits": 1320,
            "generated_target_blind_inference_calls": 1800,
            "generated_target_deliveries": 1,
            "generated_scoring_runs": 1,
            "real_or_public_metadata_requests": 0,
            "real_or_public_payload_requests": 0,
            "real_or_public_payload_bytes": 0,
            "old_retained_bundle_operations": 0,
            "real_signal_event_trajectory_or_target_reads": 0,
            "real_parameter_update_fits": 0,
            "real_model_inference_calls": 0,
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
            "green_decision_bound": True,
            "mocked_transport_and_stream_passed": True,
            "source_semantics_29_and_31_passed": True,
            "one_raw_group_at_a_time_passed": True,
            "causal_dimensions_and_motion_guard_passed": True,
            "target_firewall_passed": True,
            "exact_660_fit_900_prediction_matrix_passed": True,
            "deterministic_replay_passed": deterministic_replay,
            "private_prediction_roundtrip_passed": True,
            "aggregate_freeze_passed": True,
            "isolated_scorer_and_router_passed": score["route"] == "IACKD2-R5",
            "registered_refusals_exercised": len(mutations) >= 7,
            "resource_caps_passed": True,
            "output_cap_passed": True,
            "forbidden_access_counters_zero": True,
        },
        "warnings": [
            "all_signal_event_trajectory_label_and_outcome_values_are_generated",
            "synthetic_IACKD2_R5_has_zero_scientific_value",
            "no_public_request_or_old_bundle_operation_occurred",
            "end_to_end_latency_is_unavailable",
        ],
        "claim_boundary": {
            "engineering_capability_added": "the exact real executor interfaces pass generated transport reader firewall model freeze and scorer qualification",
            "scientific_claim_not_established": "no real or public IACKD observation was accessed so this establishes no neural effect action decoding brain specific origin or downstream capability",
        },
    }
    for _ in range(8):
        payload = _json_bytes(report)
        if report["measurements"]["output_bytes"] == len(payload):
            break
        report["measurements"]["output_bytes"] = len(payload)
    else:
        raise RealDualReversalFailure(REFUSAL_IDS[13], "qualification bytes differ")
    validate_qualification_report(report)
    payload = _json_bytes(report)
    if len(payload) > maximum_output_bytes:
        raise RealDualReversalRefusal(REFUSAL_IDS[13], "qualification output cap failed")
    _write_exclusive(path, payload, maximum_output_bytes)
    return report


def validate_qualification_report(report: Mapping[str, Any]) -> None:
    required = {
        "schema_name",
        "schema_version",
        "status",
        "decision",
        "contract_sha256",
        "policy_sha256",
        "dependencies",
        "mock_stream",
        "target_firewall",
        "model_matrix",
        "synthetic_score",
        "refusal_coverage",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "claim_boundary",
    }
    if set(report) != required:
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "qualification schema differs")
    forbidden_counters = {
        name: value
        for name, value in report["access_counters"].items()
        if name.startswith("real_")
        or name.startswith("real_or_")
        or name.startswith("old_")
        or name
        in {
            "network_bytes",
            "provider_or_language_model_calls",
            "hardware_operations",
            "release_operations",
            "scientific_claim_upgrades",
        }
    }
    if (
        report["schema_name"]
        != "neurodecodekit.iackd2_real_executor_qualification"
        or report["schema_version"] != SCHEMA_VERSION
        or report["status"] != "passed_generated_fixture_only_no_scientific_result"
        or not all(report["acceptance_gates"].values())
        or not forbidden_counters
        or any(forbidden_counters.values())
        or report["synthetic_score"]["has_scientific_value"] is not False
        or "no neural effect" not in report["claim_boundary"][
            "scientific_claim_not_established"
        ]
    ):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "qualification gates differ")


def load_qualification_report(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    payload = _read_regular_bytes(candidate, 8 * 1024 * 1024)
    try:
        report = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "qualification JSON differs") from exc
    validate_qualification_report(report)
    if report["measurements"]["output_bytes"] != len(payload):
        raise RealDualReversalRefusal(REFUSAL_IDS[17], "qualification byte count differs")
    return report


def summarize_qualification(report: Mapping[str, Any]) -> dict[str, Any]:
    validate_qualification_report(report)
    return {
        "status": report["status"],
        "synthetic_route": report["synthetic_score"]["route"],
        "parameter_update_fits": report["model_matrix"]["primary_parameter_update_fits"],
        "prediction_sets": report["model_matrix"]["primary_prediction_sets"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "output_bytes": report["measurements"]["output_bytes"],
        "real_or_public_payload_reads": report["access_counters"][
            "real_or_public_payload_requests"
        ],
        "scientific_claim": False,
        "warnings": list(report["warnings"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan, qualify, or execute the frozen IACKD-2 real pipeline."
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--qualify", type=Path, metavar="NEW_REPORT_JSON")
    modes.add_argument("--inspect", type=Path, metavar="REPORT_JSON")
    modes.add_argument("--execute-stream", action="store_true")
    modes.add_argument("--execute-analysis", action="store_true")
    modes.add_argument("--score", action="store_true")
    parser.add_argument("--implementation-commit")
    parser.add_argument("--implementation-ci-run-id", type=int)
    parser.add_argument("--freeze-commit")
    parser.add_argument("--freeze-ci-run-id", type=int)
    parser.add_argument("--base-python-job-id", type=int)
    parser.add_argument("--optional-neuro-job-id", type=int)
    parser.add_argument(
        "--maximum-output-bytes",
        type=int,
        default=8 * 1024 * 1024,
    )
    return parser


def _implementation_evidence_from_args(args: argparse.Namespace) -> ImplementationEvidence:
    values = (
        args.implementation_commit,
        args.implementation_ci_run_id,
        args.base_python_job_id,
        args.optional_neuro_job_id,
    )
    if any(value is None for value in values):
        raise RealDualReversalRefusal(REFUSAL_IDS[0], "implementation evidence is required")
    return ImplementationEvidence(
        implementation_commit=args.implementation_commit,
        implementation_CI_run_id=args.implementation_ci_run_id,
        base_python_job_id=args.base_python_job_id,
        optional_neuro_job_id=args.optional_neuro_job_id,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.qualify is not None:
        report = run_generated_real_executor_qualification(
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
    if args.execute_stream:
        receipt = run_registered_streaming_execution(
            repo_root=_repo_root(),
            evidence=_implementation_evidence_from_args(args),
            environ=os.environ,
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    if args.execute_analysis:
        freeze = run_registered_target_blind_analysis(
            repo_root=_repo_root(),
            evidence=_implementation_evidence_from_args(args),
            environ=os.environ,
        )
        print(json.dumps(freeze, indent=2, sort_keys=True))
        return 0
    if args.score:
        values = (
            args.freeze_commit,
            args.freeze_ci_run_id,
            args.base_python_job_id,
            args.optional_neuro_job_id,
        )
        if any(value is None for value in values):
            raise RealDualReversalRefusal(REFUSAL_IDS[14], "freeze evidence is required")
        result = score_registered_execution(
            repo_root=_repo_root(),
            evidence=FreezeEvidence(
                freeze_commit=args.freeze_commit,
                freeze_CI_run_id=args.freeze_ci_run_id,
                base_python_job_id=args.base_python_job_id,
                optional_neuro_job_id=args.optional_neuro_job_id,
            ),
            environ=os.environ,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    print(json.dumps(registered_plan(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
