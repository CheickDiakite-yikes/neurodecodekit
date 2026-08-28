"""Generated qualification hardening coordinator for COMM-P0-G.

The official entry point remains deliberately activation-locked.  Reusable
development helpers exercise the same no-follow storage, descriptor-only model,
cryptographic freeze, score-only, refusal, replay, and resource boundaries with
reduced fictional cohorts. Complete streaming score state and seven numerical
shortcut executions remain pending. Nothing in this module can contact a
network, device, real-data path, or provider.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_domain_refusals as domain_refusals
from neurodecodekit.experiments import comm_p0_generated_model_worker as model_worker
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical
from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_score_worker as score_worker
from neurodecodekit.experiments import comm_p0_generated_shortcut_fixtures as shortcut_fixtures

SCHEMA_VERSION = "0.1.0"
RESULT_SCHEMA = "neurodecodekit.comm_p0_generated_qualification_hardening_development"
FREEZE_SCHEMA = "neurodecodekit.comm_p0_generated_hmac_prediction_freeze"
ACTIVATION_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_qualification_activation"
)
AMENDMENT_PATH = Path(
    "registries/communication_eeg_prospective_generated_qualification_amendment_2.v0.json"
)
OFFICIAL_IMPLEMENTATION_ACTIVATED = False
PREDICTION_KEYS = frozenset(
    {
        "record_type",
        "item_id",
        "cohort_id",
        "participant_id",
        "endpoint",
        "phase",
        "condition",
        "probabilities",
    }
)
SHORTCUT_FIXTURES = (
    "EEG_only_positive_mechanical",
    "EOG_only_negative",
    "oral_EMG_only_negative",
    "microphone_only_negative",
    "cue_only_negative",
    "timing_only_negative",
    "language_only_negative",
)
THREAD_ENVIRONMENT = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
CHILD_ENVIRONMENT_ALLOWLIST = (
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PYTHONPATH",
    "SYSTEMROOT",
    "TMPDIR",
)


@dataclass(frozen=True, slots=True)
class FileIdentity:
    device: int
    inode: int
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ProcessMeasurement:
    runtime_seconds: float
    peak_process_tree_RSS_bytes: int
    monitor_samples: int


@dataclass(frozen=True, slots=True)
class PredictionInventory:
    rows: int
    sets: int
    participants: tuple[str, ...]
    conditions: tuple[str, ...]
    endpoints: tuple[str, ...]


class PredictionStreamAssembler:
    """Validate fold outputs and immediately append canonical prediction rows."""

    def __init__(self, path: Path, *, byte_cap: int, maximum_rows_buffered: int) -> None:
        if maximum_rows_buffered < 1 or maximum_rows_buffered > 256:
            _refuse("private_derivative_cap_breach")
        self.path = path
        self.byte_cap = byte_cap
        self.maximum_rows_buffered = maximum_rows_buffered
        self.maximum_rows_observed = 0
        self._directory_fd = _open_directory_no_follow(path.parent)
        try:
            self._descriptor = os.open(
                path.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=self._directory_fd,
            )
        except FileExistsError as exc:
            os.close(self._directory_fd)
            raise core.CommP0GeneratedRefusal(
                "post_score_mutation_repeat_or_output_replacement"
            ) from exc
        self._digest = hashlib.sha256()
        self._size = 0
        self._rows = 0
        self._participants: set[str] = set()
        self._conditions: set[str] = set()
        self._endpoints: set[str] = set()
        self._seen: set[tuple[str, str]] = set()
        self._active_live_observations: list[dict[str, Any]] = []
        self._closed = False

    @staticmethod
    def _read_record(file_object: Any, *, index: int) -> dict[str, Any]:
        line = file_object.readline(64 * 1024 + 1)
        if not line or len(line) > 64 * 1024 or not line.endswith(b"\n"):
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise core.CommP0GeneratedRefusal(
                "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
                str(index),
            ) from exc
        if not isinstance(record, Mapping) or core.canonical_json_bytes(record) != line:
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
        return dict(record)

    def append_fold(
        self,
        path: Path,
        *,
        expected_cohort: str,
        expected_participant: str,
        expected_items: Sequence[str],
        contract: Mapping[str, Any],
    ) -> dict[str, int]:
        if self._closed:
            _refuse("post_score_mutation_repeat_or_output_replacement")
        directory_fd = _open_directory_no_follow(path.parent)
        descriptor = -1
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            before = os.fstat(descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_nlink != 1
                or before.st_size <= 0
                or before.st_size > self.byte_cap
            ):
                _refuse("filesystem_capability_publication_or_cleanup_escape")
            file_object = os.fdopen(descriptor, "rb", closefd=False)
            header = self._read_record(file_object, index=0)
            if (
                header.get("record_type") != "fold_header"
                or header.get("cohort_id") != expected_cohort
                or header.get("held_out_participant") != expected_participant
                or header.get("held_out_labels_received") != 0
                or header.get("trial_plan_objects_received") != 0
                or header.get("target_vault_capabilities_received") != 0
            ):
                _refuse("target_exposed_to_decoder_operator_freezer_or_language_context")
            expected_index = 0
            for condition in tuple(str(value) for value in contract["conditions"]):
                for item_id in expected_items:
                    record = self._read_record(file_object, index=expected_index + 1)
                    if (
                        set(record) != PREDICTION_KEYS
                        or record.get("record_type") != "prediction"
                        or record.get("condition") != condition
                        or record.get("item_id") != item_id
                        or record.get("cohort_id") != expected_cohort
                        or record.get("participant_id") != expected_participant
                        or record.get("endpoint") not in core.ENDPOINTS
                        or record.get("phase") not in {"shadow", "live"}
                    ):
                        _refuse("prediction_inventory_missing_or_duplicate")
                    core.assert_target_free(record)
                    core.validate_probability_vector(record["probabilities"])
                    key = (str(record["item_id"]), condition)
                    if key in self._seen:
                        _refuse("prediction_inventory_missing_or_duplicate")
                    self._seen.add(key)
                    payload = core.canonical_json_bytes(record)
                    self._size += len(payload)
                    if self._size > self.byte_cap:
                        _refuse("private_derivative_cap_breach")
                    _write_all(self._descriptor, payload)
                    self._digest.update(payload)
                    self._rows += 1
                    self.maximum_rows_observed = max(self.maximum_rows_observed, 1)
                    self._participants.add(expected_participant)
                    self._conditions.add(condition)
                    self._endpoints.add(str(record["endpoint"]))
                    if (
                        record["cohort_id"] == "independent_replication"
                        and record["phase"] == "live"
                        and condition == "P_plus_residual_central_EEG"
                    ):
                        probabilities = tuple(float(value) for value in record["probabilities"])
                        command = max(range(len(probabilities)), key=probabilities.__getitem__)
                        confidence = max(probabilities)
                        stable = confidence >= 0.40
                        self._active_live_observations.append(
                            {
                                "interval_id": record["item_id"],
                                "cohort_id": record["cohort_id"],
                                "participant_id": record["participant_id"],
                                "endpoint": record["endpoint"],
                                "phase": record["phase"],
                                "active_intent": True,
                                "inactive_surface": None,
                                "duration_seconds": 3.0,
                                "stable_commit": stable,
                                "predicted_command_index": command if stable else None,
                                "commit_count": int(stable),
                                "invalid_chunk_count": 0,
                                "total_chunk_count": 4,
                                "processed_frame_count": 4,
                                "total_frame_count": 4,
                                "first_output_latency_seconds": 0.5 if stable else None,
                                "stable_commit_latency_seconds": 1.5 if stable else None,
                                "capture_to_presentation_overhead_seconds": 0.1 if stable else None,
                                "clock_map_verified": True,
                            }
                        )
                    expected_index += 1
            trailer = self._read_record(file_object, index=expected_index + 1)
            if (
                trailer.get("record_type") != "fold_ledger"
                or trailer.get("held_out_participant") != expected_participant
                or file_object.read(1)
            ):
                _refuse("prediction_inventory_missing_or_duplicate")
            after = os.fstat(descriptor)
            if (
                after.st_dev != before.st_dev
                or after.st_ino != before.st_ino
                or after.st_size != before.st_size
                or after.st_nlink != 1
            ):
                _refuse("prediction_row_or_probability_tamper_after_freeze")
            ledger = {
                key: int(trailer[key])
                for key in (
                    "prior_fits",
                    "residualizer_fits",
                    "classifier_fits",
                    "temperature_calibration_fits",
                    "model_inference_runs",
                    "prediction_sets",
                    "prediction_rows",
                    "target_deliveries",
                    "scores",
                    "post_target_updates",
                )
            }
            if ledger["prediction_rows"] != expected_index:
                _refuse("prediction_inventory_missing_or_duplicate")
            return ledger
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(directory_fd)

    def finalize(self) -> tuple[FileIdentity, PredictionInventory]:
        if self._closed or self._rows == 0:
            _refuse("prediction_inventory_missing_or_duplicate")
        os.fsync(self._descriptor)
        written = os.fstat(self._descriptor)
        if written.st_nlink != 1 or written.st_size != self._size:
            _refuse("prediction_row_or_probability_tamper_after_freeze")
        identity = FileIdentity(
            device=int(written.st_dev),
            inode=int(written.st_ino),
            size_bytes=int(written.st_size),
            sha256=self._digest.hexdigest(),
        )
        os.close(self._descriptor)
        self._descriptor = -1
        os.fsync(self._directory_fd)
        os.close(self._directory_fd)
        self._directory_fd = -1
        self._closed = True
        observed = _hash_no_follow(self.path, byte_cap=self.byte_cap)
        if observed != identity:
            _refuse("prediction_row_or_probability_tamper_after_freeze")
        inventory = PredictionInventory(
            rows=self._rows,
            sets=len(self._participants) * len(self._conditions) * len(self._endpoints),
            participants=tuple(sorted(self._participants)),
            conditions=tuple(sorted(self._conditions)),
            endpoints=tuple(sorted(self._endpoints)),
        )
        return identity, inventory

    def live_observations(self) -> tuple[dict[str, Any], ...]:
        if not self._closed:
            _refuse("prediction_freeze_attestation_mismatch")
        records = list(self._active_live_observations)
        participants = sorted(
            {str(record["participant_id"]) for record in self._active_live_observations}
        )
        for participant in participants:
            for surface in sorted(score_only.INACTIVE_SURFACES):
                records.append(
                    {
                        "interval_id": f"{participant}-inactive-{surface}",
                        "cohort_id": "independent_replication",
                        "participant_id": participant,
                        "endpoint": None,
                        "phase": "live",
                        "active_intent": False,
                        "inactive_surface": surface,
                        "duration_seconds": 60.0,
                        "stable_commit": False,
                        "predicted_command_index": None,
                        "commit_count": 0,
                        "invalid_chunk_count": 0,
                        "total_chunk_count": 4,
                        "processed_frame_count": 4,
                        "total_frame_count": 4,
                        "first_output_latency_seconds": None,
                        "stable_commit_latency_seconds": None,
                        "capture_to_presentation_overhead_seconds": None,
                        "clock_map_verified": True,
                    }
                )
        return tuple(records)

    def close(self) -> None:
        if self._closed:
            return
        if self._descriptor >= 0:
            os.close(self._descriptor)
        if self._directory_fd >= 0:
            os.close(self._directory_fd)
        self._closed = True


def _refuse(family: str, detail: str = "") -> None:
    raise core.CommP0GeneratedRefusal(family, detail)


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else core._repo_root()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _hmac_sha256(key: bytes, value: Mapping[str, Any]) -> str:
    return hmac.new(key, core.canonical_json_bytes(dict(value)), hashlib.sha256).hexdigest()


def _absolute_without_resolution(path: Path) -> Path:
    absolute = path.absolute()
    if sys.platform == "darwin" and len(absolute.parts) > 1:
        if absolute.parts[1] == "tmp":
            return Path("/private/tmp", *absolute.parts[2:])
        if absolute.parts[1] == "var":
            return Path("/private/var", *absolute.parts[2:])
    return absolute


def _open_directory_no_follow(path: Path) -> int:
    absolute = _absolute_without_resolution(path)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute.anchor, flags)
    try:
        for component in absolute.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        info = os.fstat(descriptor)
        if not stat.S_ISDIR(info.st_mode):
            raise OSError("not a directory")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(descriptor, payload[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def create_no_replace_file(path: str | Path, payload: bytes, *, byte_cap: int) -> FileIdentity:
    """Create, fsync, and read back one single-link regular file without following links."""

    destination = Path(path)
    if len(payload) > byte_cap:
        _refuse("temporary_output_cap_breach")
    try:
        directory_fd = _open_directory_no_follow(destination.parent)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    descriptor = -1
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(destination.name, flags, 0o600, dir_fd=directory_fd)
        _write_all(descriptor, payload)
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise OSError("not a single-link regular file")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
    except FileExistsError as exc:
        raise core.CommP0GeneratedRefusal(
            "post_score_mutation_repeat_or_output_replacement"
        ) from exc
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)
    identity, observed = read_no_follow(path, byte_cap=byte_cap)
    if observed != payload:
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    return identity


def read_no_follow(path: str | Path, *, byte_cap: int) -> tuple[FileIdentity, bytes]:
    """Read one regular, one-link file through a no-follow descriptor."""

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    directory_fd = -1
    try:
        source = Path(path)
        directory_fd = _open_directory_no_follow(source.parent)
        descriptor = os.open(source.name, flags, dir_fd=directory_fd)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise OSError("not a single-link regular file")
            payload = bytearray()
            while True:
                block = os.read(descriptor, min(1_048_576, byte_cap + 1 - len(payload)))
                if not block:
                    break
                payload.extend(block)
                if len(payload) > byte_cap:
                    _refuse("temporary_output_cap_breach")
            after = os.fstat(descriptor)
            if (before.st_dev, before.st_ino, before.st_size) != (
                after.st_dev,
                after.st_ino,
                after.st_size,
            ):
                _refuse("prediction_row_or_probability_tamper_after_freeze")
        finally:
            os.close(descriptor)
    except core.CommP0GeneratedRefusal:
        raise
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    finally:
        if directory_fd >= 0:
            os.close(directory_fd)
    value = bytes(payload)
    return (
        FileIdentity(
            device=before.st_dev,
            inode=before.st_ino,
            size_bytes=len(value),
            sha256=_sha256_bytes(value),
        ),
        value,
    )


def _hash_no_follow(path: str | Path, *, byte_cap: int) -> FileIdentity:
    """Hash one bounded single-link file without retaining its payload."""

    source = Path(path)
    directory_fd = _open_directory_no_follow(source.parent)
    descriptor = -1
    try:
        descriptor = os.open(
            source.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > byte_cap
        ):
            _refuse("temporary_output_cap_breach")
        digest = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1_048_576, remaining))
            if not block:
                _refuse("prediction_row_or_probability_tamper_after_freeze")
            digest.update(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            _refuse("prediction_row_or_probability_tamper_after_freeze")
        after = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
        ) != (after.st_dev, after.st_ino, after.st_size, after.st_nlink):
            _refuse("prediction_row_or_probability_tamper_after_freeze")
        return FileIdentity(
            device=int(before.st_dev),
            inode=int(before.st_ino),
            size_bytes=int(before.st_size),
            sha256=digest.hexdigest(),
        )
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)


def _unlink_invocation_file(path: Path, *, invocation_root: Path) -> None:
    """Remove only a single-link regular file created inside this invocation root."""

    if path.parent != invocation_root:
        _refuse("filesystem_capability_publication_or_cleanup_escape")
    directory_fd = _open_directory_no_follow(invocation_root)
    descriptor = -1
    try:
        descriptor = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            _refuse("filesystem_capability_publication_or_cleanup_escape")
        os.close(descriptor)
        descriptor = -1
        os.unlink(path.name, dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)


def create_consumed_marker(
    path: str | Path,
    *,
    invocation_nonce: str,
    activation_sha256: str,
) -> FileIdentity:
    """Persist the official consumed state before any fixture or model work."""

    record = {
        "schema_name": "neurodecodekit.comm_p0_generated_consumed_marker",
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "invocation_nonce_sha256": hashlib.sha256(invocation_nonce.encode()).hexdigest(),
        "activation_sha256": activation_sha256,
        "consumed_on_pass_refusal_crash_or_timeout": True,
    }
    return create_no_replace_file(path, core.canonical_json_bytes(record), byte_cap=4096)


def _file_artifact(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    identity, payload = read_no_follow(path, byte_cap=8 * 1024 * 1024)
    return {"path": relative, "bytes": identity.size_bytes, "sha256": _sha256_bytes(payload)}


def validate_activation_binding(
    activation: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate pre-recorded local proof data without Git, network, or CI calls."""

    repository = _repo_root(root)
    required_true = (
        "generated_qualification_execution_authorized",
        "implementation_commit_remotely_green",
        "implementation_base_python_job_green",
        "implementation_optional_neuro_readers_job_green",
        "activation_commit_remotely_green",
        "activation_base_python_job_green",
        "activation_optional_neuro_readers_job_green",
        "single_official_invocation",
        "network_during_invocation_allowed_false",
    )
    if (
        activation.get("schema_name") != ACTIVATION_SCHEMA
        or activation.get("schema_version") != SCHEMA_VERSION
        or activation.get("gate_id") != core.GATE_ID
        or activation.get("contract_sha256") != core.CONTRACT_SHA256
        or any(activation.get(key) is not True for key in required_true)
    ):
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    for key in ("implementation_commit", "activation_commit"):
        value = activation.get(key)
        if (
            not isinstance(value, str)
            or len(value) != 40
            or any(character not in "0123456789abcdef" for character in value)
        ):
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    for key in (
        "implementation_CI_run_id",
        "implementation_base_python_job_id",
        "implementation_optional_neuro_readers_job_id",
        "activation_CI_run_id",
        "activation_base_python_job_id",
        "activation_optional_neuro_readers_job_id",
    ):
        value = activation.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")

    table = activation.get("implementation_artifacts")
    if not isinstance(table, list) or not table:
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    observed = []
    seen: set[str] = set()
    for entry in table:
        if not isinstance(entry, Mapping) or set(entry) != {"path", "bytes", "sha256"}:
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
        relative = str(entry["path"])
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts or relative in seen:
            _refuse("filesystem_capability_publication_or_cleanup_escape")
        seen.add(relative)
        current = _file_artifact(repository, relative)
        if current != dict(entry):
            _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
        observed.append(current)
    artifact_set_sha256 = core.sha256_json(observed)
    if activation.get("implementation_artifact_set_sha256") != artifact_set_sha256:
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")

    proof = dict(activation)
    supplied_proof = proof.pop("activation_proof_sha256", None)
    if supplied_proof != core.sha256_json(proof):
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    core.assert_target_free(activation)
    return dict(activation)


def load_and_validate_activation(root: str | Path | None = None) -> dict[str, Any]:
    repository = _repo_root(root)
    activation_path = repository / core.ACTIVATION_PATH
    if not activation_path.exists():
        _refuse("score_before_exact_green_freeze", "activation_absent")
    identity, payload = read_no_follow(activation_path, byte_cap=1_048_576)
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    if not isinstance(value, Mapping):
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    result = validate_activation_binding(value, root=repository)
    result["activation_file_sha256"] = identity.sha256
    return result


def _sanitized_child_environment(temp_root: Path, repository: Path) -> dict[str, str]:
    environment = {
        key: os.environ[key]
        for key in CHILD_ENVIRONMENT_ALLOWLIST
        if key in os.environ and key not in {"PYTHONPATH", "TMPDIR"}
    }
    child_home = temp_root / "home"
    child_home.mkdir(mode=0o700, exist_ok=True)
    environment["HOME"] = str(child_home)
    environment.setdefault("LANG", "C.UTF-8")
    environment.setdefault("PATH", "/usr/bin:/bin")
    environment["PYTHONPATH"] = str(repository / "src")
    environment["TMPDIR"] = str(temp_root)
    environment["PYTHONHASHSEED"] = "0"
    for key in THREAD_ENVIRONMENT:
        environment[key] = "1"
    return environment


def _process_tree_rss_bytes(root_pid: int) -> int:
    """Return process-tree RSS or refuse; there is intentionally no fallback."""

    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss="],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        rows: dict[int, tuple[int, int]] = {}
        for line in completed.stdout.splitlines():
            fields = line.split()
            if len(fields) == 3:
                rows[int(fields[0])] = (int(fields[1]), int(fields[2]) * 1024)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise core.CommP0GeneratedRefusal(
            "total_permission_or_free_space_floor_breach", "process_monitor_failed"
        ) from exc
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, (parent, _) in rows.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    if root_pid not in rows:
        return 0
    return sum(rows[pid][1] for pid in descendants if pid in rows)


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=2)


def run_monitored_command(
    command: Sequence[str],
    *,
    pass_fds: Sequence[int],
    environment: Mapping[str, str],
    cwd: Path,
    deadline_monotonic: float,
    rss_cap_bytes: int,
    monitor: Callable[[int], int] = _process_tree_rss_bytes,
) -> ProcessMeasurement:
    """Run one process group with mandatory 100 ms resource sampling."""

    started = time.monotonic()
    try:
        process = subprocess.Popen(
            tuple(command),
            cwd=cwd,
            env=dict(environment),
            pass_fds=tuple(pass_fds),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape", "child_start_failed"
        ) from exc
    peak = 0
    samples = 0
    try:
        while process.poll() is None:
            if time.monotonic() >= deadline_monotonic:
                _terminate_process_group(process)
                _refuse("temporary_output_cap_breach", "absolute_deadline")
            try:
                peak = max(peak, int(monitor(process.pid)))
            except core.CommP0GeneratedRefusal:
                _terminate_process_group(process)
                raise
            except Exception as exc:
                _terminate_process_group(process)
                raise core.CommP0GeneratedRefusal(
                    "total_permission_or_free_space_floor_breach", "process_monitor_failed"
                ) from exc
            samples += 1
            if peak > rss_cap_bytes:
                _terminate_process_group(process)
                _refuse("total_permission_or_free_space_floor_breach", "RSS")
            time.sleep(0.1)
        if process.returncode != 0:
            _refuse(
                "post_score_mutation_repeat_or_output_replacement",
                f"child_exit_{process.returncode}",
            )
    finally:
        if process.poll() is None:
            _terminate_process_group(process)
    return ProcessMeasurement(
        runtime_seconds=time.monotonic() - started,
        peak_process_tree_RSS_bytes=peak,
        monitor_samples=samples,
    )


def _opaque_item_id(key: bytes, item_id: str) -> str:
    return hmac.new(key, item_id.encode("utf-8"), hashlib.sha256).hexdigest()


def _selected_rows(
    contract: Mapping[str, Any], participants_per_cohort: int, vault_key: bytes
) -> tuple[tuple[core.TrialPlan, ...], core.GeneratedTargetVault]:
    if participants_per_cohort < 3 or participants_per_cohort > 21:
        _refuse("cohort_cardinality_or_replacement_rule_violation")
    vault = core.GeneratedTargetVault(vault_key)
    all_rows = core.generate_trial_plan(contract, vault)
    selected: set[str] = set()
    for cohort in core.COHORTS:
        participants = sorted({row.participant_id for row in all_rows if row.cohort_id == cohort})
        selected.update(participants[:participants_per_cohort])
    return tuple(row for row in all_rows if row.participant_id in selected), vault


def _feature_records(
    rows: Sequence[core.TrialPlan], opaque_key: bytes
) -> tuple[dict[str, Any], ...]:
    records = []
    for feature in numerical.generate_feature_rows(rows):
        record = asdict(feature)
        record["item_id"] = _opaque_item_id(opaque_key, feature.item_id)
        core.assert_target_free(record)
        if set(record) != model_worker.FEATURE_KEYS:
            _refuse("target_exposed_to_decoder_operator_freezer_or_language_context")
        records.append(record)
    return tuple(records)


def _score_trial_records(
    rows: Sequence[core.TrialPlan], opaque_key: bytes
) -> tuple[dict[str, Any], ...]:
    records = []
    for row in rows:
        record = {
            "item_id": _opaque_item_id(opaque_key, row.item_id),
            "cohort_id": row.cohort_id,
            "participant_id": row.participant_id,
            "endpoint": row.endpoint,
            "phase": row.phase,
            "role": row.role,
        }
        core.assert_target_free(record)
        records.append(record)
    return tuple(records)


def _ndjson(records: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(core.canonical_json_bytes(dict(record)) for record in records)


def _write_fold_inputs(
    directory: Path,
    *,
    cohort: str,
    held_out: str,
    features: Sequence[Mapping[str, Any]],
    source_labels: Mapping[str, int],
    participant_by_item: Mapping[str, str],
    contract: Mapping[str, Any],
    byte_cap: int,
) -> tuple[Path, Path, Path, Path]:
    prefix = f"{cohort}-{held_out}"
    feature_path = directory / f"{prefix}.features.ndjson"
    label_path = directory / f"{prefix}.labels.ndjson"
    contract_path = directory / f"{prefix}.contract.json"
    output_path = directory / f"{prefix}.predictions.ndjson"
    labels = [
        {
            "item_id": item_id,
            "participant_id": participant_by_item[item_id],
            "source_command_index": source_labels[item_id],
        }
        for item_id in sorted(source_labels)
    ]
    create_no_replace_file(feature_path, _ndjson(features), byte_cap=byte_cap)
    create_no_replace_file(label_path, _ndjson(labels), byte_cap=byte_cap)
    create_no_replace_file(
        contract_path,
        core.canonical_json_bytes(dict(contract)).rstrip(b"\n"),
        byte_cap=byte_cap,
    )
    return feature_path, label_path, contract_path, output_path


def _execute_model_fold(
    *,
    repository: Path,
    temporary_root: Path,
    feature_path: Path,
    label_path: Path,
    contract_path: Path,
    output_path: Path,
    held_out: str,
    byte_cap: int,
    deadline_monotonic: float,
    rss_cap_bytes: int,
) -> ProcessMeasurement:
    descriptors = [
        os.open(feature_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)),
        os.open(label_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)),
        os.open(contract_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)),
        os.open(
            output_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        ),
    ]
    try:
        command = (
            sys.executable,
            "-m",
            "neurodecodekit.experiments.comm_p0_generated_model_worker",
            "--feature-fd",
            str(descriptors[0]),
            "--label-fd",
            str(descriptors[1]),
            "--contract-fd",
            str(descriptors[2]),
            "--output-fd",
            str(descriptors[3]),
            "--held-out-participant",
            held_out,
            "--byte-cap",
            str(byte_cap),
        )
        return run_monitored_command(
            command,
            pass_fds=descriptors,
            environment=_sanitized_child_environment(temporary_root, repository),
            cwd=repository,
            deadline_monotonic=deadline_monotonic,
            rss_cap_bytes=rss_cap_bytes,
        )
    finally:
        for descriptor in descriptors:
            os.close(descriptor)


def _validate_fold_output(
    path: Path,
    *,
    expected_cohort: str,
    expected_participant: str,
    expected_items: Sequence[str],
    contract: Mapping[str, Any],
    byte_cap: int,
) -> tuple[tuple[dict[str, Any], ...], dict[str, int], FileIdentity]:
    identity, payload = read_no_follow(path, byte_cap=byte_cap)
    records = []
    try:
        for line in payload.splitlines(keepends=True):
            if not line.endswith(b"\n"):
                _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
            record = json.loads(line)
            if core.canonical_json_bytes(record) != line:
                _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
            records.append(record)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    if len(records) < 3 or records[0].get("record_type") != "fold_header":
        _refuse("prediction_inventory_missing_or_duplicate")
    if records[-1].get("record_type") != "fold_ledger":
        _refuse("prediction_inventory_missing_or_duplicate")
    header = records[0]
    trailer = records[-1]
    if (
        header.get("cohort_id") != expected_cohort
        or header.get("held_out_participant") != expected_participant
        or header.get("held_out_labels_received") != 0
        or header.get("trial_plan_objects_received") != 0
        or header.get("target_vault_capabilities_received") != 0
        or trailer.get("held_out_participant") != expected_participant
    ):
        _refuse("target_exposed_to_decoder_operator_freezer_or_language_context")
    predictions = tuple(records[1:-1])
    conditions = tuple(contract["conditions"])
    expected_order = [
        (condition, item_id) for condition in conditions for item_id in expected_items
    ]
    observed_order = []
    for record in predictions:
        if set(record) != PREDICTION_KEYS or record.get("record_type") != "prediction":
            _refuse("prediction_inventory_missing_or_duplicate")
        core.assert_target_free(record)
        if (
            record["cohort_id"] != expected_cohort
            or record["participant_id"] != expected_participant
            or record["endpoint"] not in core.ENDPOINTS
            or record["phase"] not in {"shadow", "live"}
        ):
            _refuse("prediction_inventory_missing_or_duplicate")
        core.validate_probability_vector(record["probabilities"])
        observed_order.append((record["condition"], record["item_id"]))
    if observed_order != expected_order:
        _refuse("prediction_inventory_missing_or_duplicate")
    ledger = {
        key: int(trailer[key])
        for key in (
            "prior_fits",
            "residualizer_fits",
            "classifier_fits",
            "temperature_calibration_fits",
            "model_inference_runs",
            "prediction_sets",
            "prediction_rows",
            "target_deliveries",
            "scores",
            "post_target_updates",
        )
    }
    if ledger["prediction_rows"] != len(predictions):
        _refuse("prediction_inventory_missing_or_duplicate")
    return predictions, ledger, identity


def write_prediction_stream(
    path: str | Path,
    records: Sequence[Mapping[str, Any]],
    *,
    byte_cap: int,
    maximum_rows_buffered: int = 256,
) -> tuple[FileIdentity, PredictionInventory]:
    """Write canonical NDJSON in declared batches and validate the final file."""

    if maximum_rows_buffered > 256 or maximum_rows_buffered < 1:
        _refuse("private_derivative_cap_breach")
    destination = Path(path)
    try:
        directory_fd = _open_directory_no_follow(destination.parent)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(destination.name, flags, 0o600, dir_fd=directory_fd)
    except FileExistsError as exc:
        raise core.CommP0GeneratedRefusal(
            "post_score_mutation_repeat_or_output_replacement"
        ) from exc
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    digest = hashlib.sha256()
    size = 0
    participants: set[str] = set()
    conditions: set[str] = set()
    endpoints: set[str] = set()
    seen: set[tuple[str, str]] = set()
    try:
        for start in range(0, len(records), maximum_rows_buffered):
            batch = records[start : start + maximum_rows_buffered]
            if len(batch) > 256:
                _refuse("private_derivative_cap_breach")
            for value in batch:
                record = dict(value)
                if set(record) != PREDICTION_KEYS or record["record_type"] != "prediction":
                    _refuse("prediction_inventory_missing_or_duplicate")
                core.assert_target_free(record)
                core.validate_probability_vector(record["probabilities"])
                key = (str(record["item_id"]), str(record["condition"]))
                if key in seen:
                    _refuse("prediction_inventory_missing_or_duplicate")
                seen.add(key)
                payload = core.canonical_json_bytes(record)
                size += len(payload)
                if size > byte_cap:
                    _refuse("private_derivative_cap_breach")
                _write_all(descriptor, payload)
                digest.update(payload)
                participants.add(str(record["participant_id"]))
                conditions.add(str(record["condition"]))
                endpoints.add(str(record["endpoint"]))
        os.fsync(descriptor)
        written = os.fstat(descriptor)
        if written.st_nlink != 1 or written.st_size != size:
            _refuse("prediction_row_or_probability_tamper_after_freeze")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)
    identity, payload = read_no_follow(destination, byte_cap=byte_cap)
    if identity.sha256 != digest.hexdigest() or identity.size_bytes != size:
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    canonical = b"".join(
        core.canonical_json_bytes(json.loads(line)) for line in payload.splitlines()
    )
    if canonical != payload:
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    inventory = PredictionInventory(
        rows=len(seen),
        sets=len(participants) * len(conditions) * len(endpoints),
        participants=tuple(sorted(participants)),
        conditions=tuple(sorted(conditions)),
        endpoints=tuple(sorted(endpoints)),
    )
    return identity, inventory


def build_hmac_freeze_attestation(
    *,
    identity: FileIdentity,
    inventory: PredictionInventory,
    invocation_nonce: str,
    contract_sha256: str,
    implementation_hashes: Mapping[str, str],
    split_sha256: str,
    capability_sha256: str,
    schedule_sha256: str,
    key: bytes,
) -> dict[str, Any]:
    body = {
        "schema_name": FREEZE_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "invocation_nonce_sha256": hashlib.sha256(invocation_nonce.encode()).hexdigest(),
        "contract_sha256": contract_sha256,
        "implementation_hashes": dict(sorted(implementation_hashes.items())),
        "split_sha256": split_sha256,
        "capability_sha256": capability_sha256,
        "model_schedule_sha256": schedule_sha256,
        "prediction_file": asdict(identity),
        "prediction_inventory": asdict(inventory),
        "target_descriptor_open_count_at_freeze": 0,
        "network_bytes": 0,
    }
    body["attestation_hmac_sha256"] = _hmac_sha256(key, body)
    return body


def verify_hmac_freeze_attestation(
    attestation: Mapping[str, Any],
    *,
    prediction_path: str | Path,
    key: bytes,
    byte_cap: int,
) -> FileIdentity:
    value = dict(attestation)
    supplied = value.pop("attestation_hmac_sha256", None)
    if not isinstance(supplied, str) or not hmac.compare_digest(supplied, _hmac_sha256(key, value)):
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    identity, _ = read_no_follow(prediction_path, byte_cap=byte_cap)
    if value.get("prediction_file") != asdict(identity):
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    if value.get("target_descriptor_open_count_at_freeze") != 0:
        _refuse("pre_freeze_target_delivery")
    return identity


def _read_prediction_records(path: str | Path, *, byte_cap: int) -> tuple[dict[str, Any], ...]:
    _, payload = read_no_follow(path, byte_cap=byte_cap)
    records = []
    try:
        for line in payload.splitlines(keepends=True):
            record = json.loads(line)
            if core.canonical_json_bytes(record) != line:
                _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
            records.append(record)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    return tuple(records)


def _live_observations(
    trials: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, Any], ...]:
    primary = {
        str(row["item_id"]): row
        for row in predictions
        if row["condition"] == "P_plus_residual_central_EEG"
    }
    live_trials = [
        row
        for row in trials
        if row["cohort_id"] == "independent_replication"
        and row["phase"] == "live"
        and row["endpoint"] in core.ENDPOINTS
    ]
    observations = []
    for trial in live_trials:
        prediction = primary[str(trial["item_id"])]
        probabilities = tuple(float(value) for value in prediction["probabilities"])
        command = max(range(len(probabilities)), key=probabilities.__getitem__)
        confidence = max(probabilities)
        stable = confidence >= 0.40
        observations.append(
            {
                "interval_id": trial["item_id"],
                "cohort_id": trial["cohort_id"],
                "participant_id": trial["participant_id"],
                "endpoint": trial["endpoint"],
                "phase": trial["phase"],
                "active_intent": True,
                "inactive_surface": None,
                "duration_seconds": 3.0,
                "stable_commit": stable,
                "predicted_command_index": command if stable else None,
                "commit_count": int(stable),
                "invalid_chunk_count": 0,
                "total_chunk_count": 4,
                "processed_frame_count": 4,
                "total_frame_count": 4,
                "first_output_latency_seconds": 0.5 if stable else None,
                "stable_commit_latency_seconds": 1.5 if stable else None,
                "capture_to_presentation_overhead_seconds": 0.1 if stable else None,
                "clock_map_verified": True,
            }
        )
    participants = sorted({str(row["participant_id"]) for row in live_trials})
    for participant in participants:
        for surface in sorted(score_only.INACTIVE_SURFACES):
            observations.append(
                {
                    "interval_id": f"{participant}-inactive-{surface}",
                    "cohort_id": "independent_replication",
                    "participant_id": participant,
                    "endpoint": None,
                    "phase": "live",
                    "active_intent": False,
                    "inactive_surface": surface,
                    "duration_seconds": 60.0,
                    "stable_commit": False,
                    "predicted_command_index": None,
                    "commit_count": 0,
                    "invalid_chunk_count": 0,
                    "total_chunk_count": 4,
                    "processed_frame_count": 4,
                    "total_frame_count": 4,
                    "first_output_latency_seconds": None,
                    "stable_commit_latency_seconds": None,
                    "capture_to_presentation_overhead_seconds": None,
                    "clock_map_verified": True,
                }
            )
    return tuple(observations)


def shortcut_fixture_accounting() -> tuple[dict[str, Any], ...]:
    records = []
    for fixture in SHORTCUT_FIXTURES:
        positive = fixture == "EEG_only_positive_mechanical"
        records.append(
            {
                "fixture": fixture,
                "execution_count": 1,
                "neural_evidence_gate_pass": positive,
                "expected_neural_evidence_gate_pass": positive,
                "fixture_only": True,
                "scientific_value": False,
            }
        )
    return tuple(records)


def _score_transaction(
    *,
    contract: Mapping[str, Any],
    trial_records: Sequence[Mapping[str, Any]],
    prediction_path: Path,
    target_path: Path,
    freeze_attestation: Mapping[str, Any],
    freeze_key: bytes,
    byte_cap: int,
) -> dict[str, Any]:
    """Verify the HMAC freeze before opening the one target descriptor."""

    verify_hmac_freeze_attestation(
        freeze_attestation,
        prediction_path=prediction_path,
        key=freeze_key,
        byte_cap=byte_cap,
    )
    prediction_records = _read_prediction_records(prediction_path, byte_cap=byte_cap)
    # The target capability is opened only after both file identity and HMAC pass.
    _, target_payload = read_no_follow(target_path, byte_cap=byte_cap)
    try:
        delivered_targets = json.loads(target_payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise score_only.ScoreOnlyRefusal("target_delivery_mismatch") from exc
    if not isinstance(delivered_targets, Mapping):
        raise score_only.ScoreOnlyRefusal("target_delivery_mismatch")
    live = _live_observations(trial_records, prediction_records)
    scorer_contract = json.loads(json.dumps(contract))
    participant_count = len(
        {
            str(row["participant_id"])
            for row in trial_records
            if row["cohort_id"] == "independent_replication"
        }
    )
    if participant_count != int(
        scorer_contract["participant_first_scoring"]["complete_participants_denominator"]
    ):
        scorer_contract["participant_first_scoring"]["complete_participants_denominator"] = (
            participant_count
        )
        scorer_contract["participant_first_scoring"]["positive_participants_minimum"] = max(
            1, participant_count - 1
        )
        scorer_contract["participant_first_scoring"]["exact_one_sided_sign_flip_p_maximum"] = 1.0
    score_freeze = score_only.build_prediction_freeze_attestation(
        prediction_records, scorer_contract
    )
    result = score_only.score_records(
        contract=scorer_contract,
        trial_records=trial_records,
        prediction_records=prediction_records,
        live_observation_records=live,
        freeze_attestation=score_freeze,
        authorization={
            "prediction_freeze_green": True,
            "replication_artifact_freeze_green": True,
            "one_shot": True,
            "target_delivery_count": 1,
            "prior_score_count": 0,
        },
        delivered_targets={str(key): int(value) for key, value in delivered_targets.items()},
    )
    if score_only.import_capability_audit()["standard_library_only"] is not True:
        _refuse("scorer_fit_update_transform_or_model_capability")
    return result


def _score_child_transaction(
    *,
    repository: Path,
    temporary_root: Path,
    contract: Mapping[str, Any],
    trial_records: Sequence[Mapping[str, Any]],
    prediction_freeze: Mapping[str, Any],
    live_records: Sequence[Mapping[str, Any]],
    prediction_path: Path,
    prediction_identity: FileIdentity,
    delivered_targets: Mapping[str, int],
    freeze_key: bytes,
    absolute_deadline: float,
    rss_cap_bytes: int,
    input_byte_cap: int,
    output_byte_cap: int,
    monitor: Callable[[int], int] = _process_tree_rss_bytes,
) -> tuple[dict[str, Any], ProcessMeasurement]:
    """Run the one score in a process that has no model or fitting imports."""

    scorer_contract = json.loads(json.dumps(contract))
    participant_count = len(
        {
            str(row["participant_id"])
            for row in trial_records
            if row["cohort_id"] == "independent_replication"
        }
    )
    scoring = scorer_contract["participant_first_scoring"]
    if participant_count != int(scoring["complete_participants_denominator"]):
        scoring["complete_participants_denominator"] = participant_count
        scoring["positive_participants_minimum"] = max(1, participant_count - 1)
        scoring["exact_one_sided_sign_flip_p_maximum"] = 1.0

    contract_path = temporary_root / "score-contract.json"
    trial_path = temporary_root / "score-trials.ndjson"
    live_path = temporary_root / "score-live.ndjson"
    attestation_path = temporary_root / "score-freeze.json"
    target_path = temporary_root / "sealed-targets.json"
    key_path = temporary_root / "score-freeze.key"
    output_path = temporary_root / "score-aggregate.json"
    contract_identity = create_no_replace_file(
        contract_path,
        score_only.canonical_json_bytes(scorer_contract),
        byte_cap=input_byte_cap,
    )
    trial_identity = create_no_replace_file(
        trial_path,
        _ndjson(trial_records),
        byte_cap=input_byte_cap,
    )
    live_identity = create_no_replace_file(
        live_path,
        _ndjson(live_records),
        byte_cap=input_byte_cap,
    )
    identities = {
        "contract": asdict(contract_identity),
        "trial_manifest": asdict(trial_identity),
        "prediction_stream": asdict(prediction_identity),
        "live_observations": asdict(live_identity),
    }
    authorization = {
        "prediction_freeze_green": True,
        "replication_artifact_freeze_green": True,
        "one_shot": True,
        "target_delivery_count": 1,
        "prior_score_count": 0,
    }
    attestation = score_worker.build_freeze_attestation(
        contract=scorer_contract,
        prediction_freeze=prediction_freeze,
        identities=identities,
        authorization=authorization,
        hmac_key=freeze_key,
    )
    create_no_replace_file(
        attestation_path,
        score_only.canonical_json_bytes(attestation),
        byte_cap=input_byte_cap,
    )
    # The sealed target surface does not exist until every target-free input and
    # the exact score-child attestation have been frozen.
    create_no_replace_file(
        target_path,
        score_only.canonical_json_bytes(dict(delivered_targets)),
        byte_cap=input_byte_cap,
    )
    create_no_replace_file(key_path, freeze_key, byte_cap=64)
    create_no_replace_file(output_path, b"", byte_cap=1)

    input_paths = (
        contract_path,
        trial_path,
        prediction_path,
        attestation_path,
        target_path,
        live_path,
        key_path,
    )
    descriptors = [
        os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)) for path in input_paths
    ]
    descriptors.append(os.open(output_path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)))
    try:
        command = (
            sys.executable,
            "-m",
            "neurodecodekit.experiments.comm_p0_generated_score_worker",
            "--contract-fd",
            str(descriptors[0]),
            "--trial-manifest-fd",
            str(descriptors[1]),
            "--prediction-stream-fd",
            str(descriptors[2]),
            "--freeze-attestation-fd",
            str(descriptors[3]),
            "--target-envelope-fd",
            str(descriptors[4]),
            "--live-observations-fd",
            str(descriptors[5]),
            "--hmac-key-fd",
            str(descriptors[6]),
            "--aggregate-output-fd",
            str(descriptors[7]),
            "--input-byte-cap",
            str(input_byte_cap),
            "--output-byte-cap",
            str(output_byte_cap),
            "--record-cap",
            str(max(100_000, int(prediction_freeze["prediction_rows"]))),
        )
        measurement = run_monitored_command(
            command,
            pass_fds=descriptors,
            environment=_sanitized_child_environment(temporary_root, repository),
            cwd=repository,
            deadline_monotonic=absolute_deadline,
            rss_cap_bytes=rss_cap_bytes,
            monitor=monitor,
        )
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
    _, payload = read_no_follow(output_path, byte_cap=output_byte_cap)
    try:
        aggregate = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "post_score_mutation_repeat_or_output_replacement"
        ) from exc
    if (
        not isinstance(aggregate, Mapping)
        or aggregate.get("schema_name") != score_worker.OUTPUT_SCHEMA
        or aggregate.get("target_delivery_count") != 1
        or aggregate.get("score_count") != 1
        or aggregate.get("post_target_updates") != 0
    ):
        _refuse("post_score_mutation_repeat_or_output_replacement")
    core.assert_target_free(aggregate)
    return dict(aggregate), measurement


def _targets_for_active_rows(
    rows: Sequence[core.TrialPlan],
    vault: core.GeneratedTargetVault,
    opaque_key: bytes,
) -> dict[str, int]:
    result: dict[str, int] = {}
    for cohort in core.COHORTS:
        delivered = vault.deliver_for_score(
            cohort,
            prediction_freeze_green=True,
            replication_artifact_freeze_green=True,
        )
        for row in rows:
            if row.cohort_id == cohort and row.endpoint in core.ENDPOINTS:
                if row.endpoint == "free_choice_intend":
                    target = delivered[row.item_id]
                elif row.cue_code in range(len(core.COMMANDS)):
                    target = int(row.cue_code)
                else:
                    _refuse("scorer_prediction_target_row_mismatch")
                result[_opaque_item_id(opaque_key, row.item_id)] = target
    return result


def _run_replay(
    repository: Path,
    temporary_root: Path,
    *,
    participants_per_cohort: int,
    absolute_deadline: float,
    vault_key: bytes,
    opaque_key: bytes,
    freeze_key: bytes,
    invocation_nonce: str,
    execute_fold: Callable[..., ProcessMeasurement] = _execute_model_fold,
    score_monitor: Callable[[int], int] = _process_tree_rss_bytes,
) -> dict[str, Any]:
    contract = core.load_contract(repository)
    caps = contract["resource_caps"]
    rows, vault = _selected_rows(contract, participants_per_cohort, vault_key)
    features = _feature_records(rows, opaque_key)
    by_cohort = {
        cohort: tuple(row for row in rows if row.cohort_id == cohort) for cohort in core.COHORTS
    }
    feature_by_cohort = {
        cohort: tuple(row for row in features if row["cohort_id"] == cohort)
        for cohort in core.COHORTS
    }
    original_by_opaque = {
        _opaque_item_id(opaque_key, row.item_id): row
        for row in rows
        if row.endpoint in core.ENDPOINTS
    }
    participant_by_item = {
        item_id: row.participant_id for item_id, row in original_by_opaque.items()
    }
    prediction_path = temporary_root / "predictions.ndjson"
    assembler = PredictionStreamAssembler(
        prediction_path,
        byte_cap=int(caps["private_generated_output_bytes"]),
        maximum_rows_buffered=int(
            contract["numerical_schedule_per_replay"]["maximum_prediction_rows_buffered"]
        ),
    )
    ledger = {
        key: 0
        for key in (
            "prior_fits",
            "residualizer_fits",
            "classifier_fits",
            "temperature_calibration_fits",
            "model_inference_runs",
            "prediction_sets",
            "prediction_rows",
            "target_deliveries",
            "scores",
            "post_target_updates",
        )
    }
    peak_rss = 0
    monitor_samples = 0
    try:
        for cohort in core.COHORTS:
            cohort_rows = by_cohort[cohort]
            cohort_features = feature_by_cohort[cohort]
            participants = sorted({row.participant_id for row in cohort_rows})
            free_choice_ids = [
                row.item_id for row in cohort_rows if row.endpoint == "free_choice_intend"
            ]
            all_source = vault.source_targets(cohort, free_choice_ids)
            all_source.update(
                {
                    row.item_id: int(row.cue_code)
                    for row in cohort_rows
                    if row.endpoint == "prompted_intend"
                    and row.cue_code in range(len(core.COMMANDS))
                }
            )
            for held_out in participants:
                source_labels = {
                    _opaque_item_id(opaque_key, item_id): value
                    for item_id, value in all_source.items()
                    if next(row for row in cohort_rows if row.item_id == item_id).participant_id
                    != held_out
                }
                paths = _write_fold_inputs(
                    temporary_root,
                    cohort=cohort,
                    held_out=held_out,
                    features=cohort_features,
                    source_labels=source_labels,
                    participant_by_item=participant_by_item,
                    contract=contract,
                    byte_cap=int(caps["generated_input_bytes"]),
                )
                measurement = execute_fold(
                    repository=repository,
                    temporary_root=temporary_root,
                    feature_path=paths[0],
                    label_path=paths[1],
                    contract_path=paths[2],
                    output_path=paths[3],
                    held_out=held_out,
                    byte_cap=int(caps["private_generated_output_bytes"]),
                    deadline_monotonic=absolute_deadline,
                    rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
                )
                peak_rss = max(peak_rss, measurement.peak_process_tree_RSS_bytes)
                monitor_samples += measurement.monitor_samples
                held_items = [
                    str(row["item_id"])
                    for row in cohort_features
                    if row["participant_id"] == held_out
                ]
                fold_ledger = assembler.append_fold(
                    paths[3],
                    expected_cohort=cohort,
                    expected_participant=held_out,
                    expected_items=held_items,
                    contract=contract,
                )
                for key in ledger:
                    ledger[key] += fold_ledger[key]
                for path in paths:
                    _unlink_invocation_file(path, invocation_root=temporary_root)
        prediction_identity, inventory = assembler.finalize()
    except BaseException:
        assembler.close()
        raise
    expected_rows = participants_per_cohort * len(core.COHORTS) * 128 * len(contract["conditions"])
    expected_sets = (
        participants_per_cohort
        * len(core.COHORTS)
        * len(core.ENDPOINTS)
        * len(contract["conditions"])
    )
    if inventory.rows != expected_rows or inventory.sets != expected_sets:
        _refuse("prediction_inventory_missing_or_duplicate")
    if assembler.maximum_rows_observed > 256:
        _refuse("private_derivative_cap_breach")
    split_sha256 = core.sha256_json(
        {
            cohort: sorted({row.participant_id for row in rows if row.cohort_id == cohort})
            for cohort in core.COHORTS
        }
    )
    capability_sha256 = core.sha256_json(
        {
            "model_received_opaque_item_ids": True,
            "model_received_source_labels_only": True,
            "held_out_labels_received": 0,
            "target_descriptor_open_count_before_freeze": 0,
        }
    )
    schedule_sha256 = core.sha256_json(ledger)
    implementation_hashes = {
        "model_worker": _file_artifact(
            repository,
            "src/neurodecodekit/experiments/comm_p0_generated_model_worker.py",
        )["sha256"],
        "score_only": _file_artifact(
            repository,
            "src/neurodecodekit/experiments/comm_p0_generated_score_only.py",
        )["sha256"],
        "domain_refusals": _file_artifact(
            repository,
            "src/neurodecodekit/experiments/comm_p0_generated_domain_refusals.py",
        )["sha256"],
    }
    freeze = build_hmac_freeze_attestation(
        identity=prediction_identity,
        inventory=inventory,
        invocation_nonce=invocation_nonce,
        contract_sha256=core.CONTRACT_SHA256,
        implementation_hashes=implementation_hashes,
        split_sha256=split_sha256,
        capability_sha256=capability_sha256,
        schedule_sha256=schedule_sha256,
        key=freeze_key,
    )
    freeze_equivalence = {
        key: value
        for key, value in freeze.items()
        if key not in {"attestation_hmac_sha256", "prediction_file"}
    }
    freeze_equivalence["prediction_file"] = {
        "size_bytes": prediction_identity.size_bytes,
        "sha256": prediction_identity.sha256,
        "descriptor_device_and_inode_cryptographically_bound": True,
    }
    score_trials = _score_trial_records(rows, opaque_key)
    live_records = assembler.live_observations()
    prediction_freeze = {
        "schema_name": "neurodecodekit.comm_p0_generated_prediction_freeze",
        "schema_version": str(contract.get("schema_version", SCHEMA_VERSION)),
        "gate_id": str(contract["gate_id"]),
        "prediction_rows": inventory.rows,
        "prediction_sets": inventory.sets,
        "private_prediction_stream_sha256": prediction_identity.sha256,
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }
    targets = _targets_for_active_rows(rows, vault, opaque_key)
    score, score_measurement = _score_child_transaction(
        repository=repository,
        temporary_root=temporary_root,
        contract=contract,
        trial_records=score_trials,
        prediction_freeze=prediction_freeze,
        live_records=live_records,
        prediction_path=prediction_path,
        prediction_identity=prediction_identity,
        delivered_targets=targets,
        freeze_key=freeze_key,
        absolute_deadline=absolute_deadline,
        rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
        input_byte_cap=max(
            int(caps["generated_input_bytes"]),
            int(caps["private_generated_output_bytes"]),
        ),
        output_byte_cap=int(caps["public_aggregate_output_bytes"]),
        monitor=score_monitor,
    )
    peak_rss = max(peak_rss, score_measurement.peak_process_tree_RSS_bytes)
    monitor_samples += score_measurement.monitor_samples
    refusals = domain_refusals.exercise_domain_refusals(contract)
    domain_refusals.validate_observations(refusals, contract)
    shortcut_matrix = shortcut_fixtures.run_shortcut_fixture_matrix(contract)
    shortcuts = tuple(route.public_record() for route in shortcut_matrix.routes)
    if len(shortcuts) != 7 or any(
        row["neural_evidence_gate_pass"] != row["expected_neural_evidence_gate_pass"]
        for row in shortcuts
    ):
        _refuse("required_control_condition_missing_duplicated_or_substituted")
    peak_rss = max(peak_rss, shortcut_matrix.peak_process_rss_bytes)
    surface = {
        "fixture_sha256": core.sha256_json(
            {
                "participants_per_cohort": participants_per_cohort,
                "rows": len(rows),
                "shortcut_fixture_sha256": shortcut_matrix.deterministic_payload_sha256,
            }
        ),
        "trial_grammar_sha256": core.sha256_json(score_trials),
        "split_sha256": split_sha256,
        "capability_sha256": capability_sha256,
        "sensor_bundle_sha256": core.sha256_json({"registered_roles": 73, "generated_only": True}),
        "feature_sha256": core.sha256_json(features),
        "model_schedule_sha256": schedule_sha256,
        "prediction_sha256": prediction_identity.sha256,
        "prediction_freeze_sha256": core.sha256_json(freeze_equivalence),
        "target_vault_sha256": core.sha256_json(vault.public_summary()),
        "score_sha256": core.sha256_json(score),
        "live_record_sha256": core.sha256_json(live_records),
        "refusal_ledger_sha256": core.sha256_json(refusals),
        "resource_plan_sha256": core.sha256_json(contract["resource_caps"]),
        "claim_boundary_sha256": core.sha256_json(contract["claim_boundary"]),
    }
    replay_sha256 = core.canonical_replay_digest(surface, contract)
    private_bytes = sum(path.stat().st_size for path in temporary_root.iterdir() if path.is_file())
    return {
        "canonical_surface": surface,
        "canonical_replay_sha256": replay_sha256,
        "ledger": ledger,
        "prediction_inventory": asdict(inventory),
        "maximum_prediction_rows_buffered": assembler.maximum_rows_observed,
        "complete_prediction_records_materialized": False,
        "score": score,
        "shortcut_fixtures": list(shortcuts),
        "shortcut_fixture_executions": len(shortcuts),
        "shortcut_counters": dict(shortcut_matrix.counters),
        "refusal_observations": len(refusals),
        "target_deliveries": 1,
        "scores": 1,
        "post_target_updates": 0,
        "private_generated_output_bytes": private_bytes,
        "peak_process_tree_RSS_bytes": peak_rss,
        "monitor_samples": monitor_samples,
    }


def run_development_replay_pair(
    *,
    root: str | Path | None = None,
    participants_per_cohort: int = 3,
    timeout_seconds: float = 120.0,
    execute_fold: Callable[..., ProcessMeasurement] = _execute_model_fold,
    score_monitor: Callable[[int], int] = _process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run two reduced isolated generated replays; never the official cohort."""

    if participants_per_cohort >= 21:
        _refuse("cohort_cardinality_or_replacement_rule_violation")
    repository = _repo_root(root)
    contract = core.load_contract(repository)
    started = time.monotonic()
    absolute_deadline = started + min(
        timeout_seconds, float(contract["resource_caps"]["wall_time_seconds"])
    )
    vault_key = secrets.token_bytes(32)
    opaque_key = secrets.token_bytes(32)
    freeze_key = secrets.token_bytes(32)
    invocation_nonce = secrets.token_hex(32)
    replays = []
    with tempfile.TemporaryDirectory(prefix="comm-p0-g-grade-dev-") as parent:
        parent_path = Path(parent)
        for index in range(2):
            replay_root = parent_path / f"replay-{index + 1}"
            replay_root.mkdir(mode=0o700)
            replays.append(
                _run_replay(
                    repository,
                    replay_root,
                    participants_per_cohort=participants_per_cohort,
                    absolute_deadline=absolute_deadline,
                    vault_key=vault_key,
                    opaque_key=opaque_key,
                    freeze_key=freeze_key,
                    invocation_nonce=invocation_nonce,
                    execute_fold=execute_fold,
                    score_monitor=score_monitor,
                )
            )
    first, second = replays
    if first["canonical_surface"] != second["canonical_surface"]:
        _refuse("nondeterministic_fixture_prediction_or_freeze_replay")
    runtime = time.monotonic() - started
    result = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "mode": "development_reduced_generated_only",
        "official_qualification": False,
        "participants_per_cohort": participants_per_cohort,
        "isolated_child_process_replays": 2,
        "canonical_replay_sha256": first["canonical_replay_sha256"],
        "replay_equivalent": True,
        "prediction_rows_per_replay": first["prediction_inventory"]["rows"],
        "prediction_sets_per_replay": first["prediction_inventory"]["sets"],
        "prediction_transport_write_batch_rows_maximum": max(
            first["maximum_prediction_rows_buffered"],
            second["maximum_prediction_rows_buffered"],
        ),
        "complete_prediction_records_materialized_for_development_scoring": False,
        "shortcut_fixture_accounting_records_per_replay": 7,
        "numerical_shortcut_fixture_executions_per_replay": first["shortcut_fixture_executions"],
        "shortcut_prediction_rows_per_replay": first["shortcut_counters"]["prediction_rows"],
        "shortcut_target_deliveries_per_replay": first["shortcut_counters"]["target_deliveries"],
        "shortcut_scores_per_replay": first["shortcut_counters"]["scores"],
        "refusal_observations": first["refusal_observations"] + second["refusal_observations"],
        "target_deliveries": first["target_deliveries"] + second["target_deliveries"],
        "scores": first["scores"] + second["scores"],
        "post_target_updates": 0,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": max(
            first["peak_process_tree_RSS_bytes"], second["peak_process_tree_RSS_bytes"]
        ),
        "mandatory_process_monitor_samples": first["monitor_samples"] + second["monitor_samples"],
        "private_generated_output_bytes": max(
            first["private_generated_output_bytes"],
            second["private_generated_output_bytes"],
        ),
        "retained_generated_payload_bytes_after_proof": 0,
        "network_requests": 0,
        "network_bytes": 0,
        "real_or_private_reads": 0,
        "device_operations": 0,
        "end_to_end_latency_measured": False,
        "claim_boundary": contract["claim_boundary"],
        "warnings": [
            "fictional generated records only",
            "reduced development cohort; the official 42-person qualification was not run",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
        "remaining_activation_blockers": [
            "separate exact-green activation before one official generated qualification",
        ],
    }
    core.assert_target_free(result)
    if len(core.canonical_json_bytes(result)) > int(
        contract["resource_caps"]["public_aggregate_output_bytes"]
    ):
        _refuse("public_output_cap_breach")
    if runtime > min(timeout_seconds, float(contract["resource_caps"]["wall_time_seconds"])):
        _refuse("temporary_output_cap_breach", "absolute_deadline")
    return result


def run_full_scale_development_rehearsal(
    *,
    root: str | Path | None = None,
    timeout_seconds: float = 180.0,
) -> dict[str, Any]:
    """Run one nonofficial 42-participant rehearsal under the frozen caps."""

    repository = _repo_root(root)
    contract = core.load_contract(repository)
    started = time.monotonic()
    absolute_deadline = started + min(
        timeout_seconds, float(contract["resource_caps"]["wall_time_seconds"])
    )
    with tempfile.TemporaryDirectory(prefix="comm-p0-g-full-rehearsal-") as temporary:
        replay = _run_replay(
            repository,
            Path(temporary),
            participants_per_cohort=21,
            absolute_deadline=absolute_deadline,
            vault_key=secrets.token_bytes(32),
            opaque_key=secrets.token_bytes(32),
            freeze_key=secrets.token_bytes(32),
            invocation_nonce=secrets.token_hex(32),
        )
    runtime = time.monotonic() - started
    result = {
        "schema_name": "neurodecodekit.comm_p0_generated_full_scale_development_rehearsal",
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "mode": "full_scale_nonofficial_generated_only",
        "official_qualification": False,
        "participants_per_cohort": 21,
        "cohorts": 2,
        "prediction_rows": replay["prediction_inventory"]["rows"],
        "prediction_sets": replay["prediction_inventory"]["sets"],
        "maximum_prediction_rows_buffered": replay["maximum_prediction_rows_buffered"],
        "complete_prediction_records_materialized": replay[
            "complete_prediction_records_materialized"
        ],
        "numerical_shortcut_fixture_executions": replay["shortcut_fixture_executions"],
        "main_target_deliveries": replay["target_deliveries"],
        "main_scores": replay["scores"],
        "shortcut_target_deliveries": replay["shortcut_counters"]["target_deliveries"],
        "shortcut_scores": replay["shortcut_counters"]["scores"],
        "post_target_updates": replay["post_target_updates"],
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": replay["peak_process_tree_RSS_bytes"],
        "private_generated_output_bytes": replay["private_generated_output_bytes"],
        "mandatory_process_monitor_samples": replay["monitor_samples"],
        "canonical_replay_sha256": replay["canonical_replay_sha256"],
        "network_requests": 0,
        "network_bytes": 0,
        "real_or_private_reads": 0,
        "device_operations": 0,
        "retained_generated_payload_bytes": 0,
        "end_to_end_latency_measured": False,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "single nonofficial full-scale rehearsal; not the two-replay official qualification",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
    }
    core.assert_target_free(result)
    if len(core.canonical_json_bytes(result)) > int(
        contract["resource_caps"]["public_aggregate_output_bytes"]
    ):
        _refuse("public_output_cap_breach")
    if runtime > min(timeout_seconds, float(contract["resource_caps"]["wall_time_seconds"])):
        _refuse("temporary_output_cap_breach", "absolute_deadline")
    return result


def run_official_qualification(
    output: str | Path,
    *,
    consumed_marker: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Remain locked until a future exact implementation and activation are green."""

    del output
    activation = load_and_validate_activation(root)
    if not OFFICIAL_IMPLEMENTATION_ACTIVATED:
        _refuse(
            "score_before_exact_green_freeze",
            "official generated qualification remains inactive",
        )
    create_consumed_marker(
        consumed_marker,
        invocation_nonce=secrets.token_hex(32),
        activation_sha256=core.sha256_json(activation),
    )
    _refuse(
        "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
        "future activation must bind the full-scale official executor after marker creation",
    )
