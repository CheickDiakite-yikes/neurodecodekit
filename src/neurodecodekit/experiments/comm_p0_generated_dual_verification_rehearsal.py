"""One-shot generated-only COMM-P0 FS3 full resource rehearsal wrapper."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_dual_verification as FS3
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification
from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as FS2
from neurodecodekit.experiments import comm_p0_generated_strict_verifier_worker as strict_verifier


GATE_ID = FS3.GATE_ID
RUN_ID = FS3.RUN_ID
SCHEMA_VERSION = FS3.SCHEMA_VERSION
PROOF_PATH = Path(
    "registries/communication_eeg_prospective_generated_single_execution_"
    "dual_verification_full_rehearsal_implementation_proof.v0.json"
)
PROOF_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_single_execution_"
    "dual_verification_full_rehearsal_implementation_proof"
)
ACTIVATION_PATH = Path(
    "registries/communication_eeg_prospective_generated_single_execution_"
    "dual_verification_full_rehearsal_digest_activation.v0.json"
)
ACTIVATION_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_single_execution_"
    "dual_verification_full_rehearsal_digest_activation"
)
RECEIPT_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_single_execution_"
    "dual_verification_rehearsal_receipt"
)
RESULT_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_single_execution_"
    "dual_verification_rehearsal_result"
)
IMPLEMENTATION_ARTIFACT_ALLOWLIST = (
    "src/neurodecodekit/experiments/comm_p0_generated_dual_verification_rehearsal.py",
    "src/neurodecodekit/experiments/comm_p0_generated_strict_verifier_worker.py",
    "src/neurodecodekit/comm_p0_FS3_rehearsal_cli.py",
    "tests/test_comm_p0_generated_dual_verification_rehearsal.py",
    "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_SINGLE_EXECUTION_DUAL_VERIFICATION_FULL_REHEARSAL_IMPLEMENTATION.md",
    "registries/communication_eeg_prospective_generated_single_execution_dual_verification_full_rehearsal_implementation.v0.json",
)
STRICT_IDENTITY_PATHS = (
    str(FS3.CONTRACT_PATH),
    "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_SINGLE_EXECUTION_DUAL_VERIFICATION_AMENDMENT_1.md",
    "registries/communication_eeg_prospective_generated_single_execution_dual_verification_amendment_1.v0.json",
    "src/neurodecodekit/experiments/comm_p0_generated_verifier_worker.py",
    "src/neurodecodekit/experiments/comm_p0_generated_score_worker.py",
    "src/neurodecodekit/experiments/comm_p0_generated_score_only.py",
    "src/neurodecodekit/experiments/comm_p0_generated_streaming_score.py",
    "src/neurodecodekit/experiments/comm_p0_generated_strict_verifier_worker.py",
)
STRICT_SOCKET_GUARD = """\
import socket

def _blocked(*args, **kwargs):
    raise RuntimeError("COMM-P0-G:FS3-forbidden_operation_nonzero:network")

class _BlockedSocket(socket.socket):
    def connect(self, *args, **kwargs):
        return _blocked(*args, **kwargs)
    def connect_ex(self, *args, **kwargs):
        return _blocked(*args, **kwargs)

socket.socket = _BlockedSocket
socket.create_connection = _blocked
socket.getaddrinfo = _blocked
"""
HEX_40 = frozenset("0123456789abcdef")
ACTIVATION_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "implementation_proof_sha256",
        "implementation_proof_commit",
        "implementation_proof_CI_run_id",
        "implementation_proof_base_python_job_id",
        "implementation_proof_optional_neuro_readers_job_id",
        "proof_remotely_green_on_GitHub_main",
        "one_FS3_rehearsal_activated",
        "full_scale_FS3_attempts_before_activation",
        "official_real_private_network_device_release_or_claim_authorized",
        "activation_record_sha256",
    }
)
PROOF_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "contract_sha256",
        "registration_commit",
        "prior_implementation_commit",
        "prior_proof_closeout_commit",
        "full_wrapper_implementation_commit",
        "full_wrapper_CI_run_id",
        "full_wrapper_base_python_job_id",
        "full_wrapper_optional_neuro_readers_job_id",
        "all_ordered_parents_remotely_green_on_GitHub_main",
        "both_required_full_wrapper_jobs_green",
        "one_FS3_rehearsal_authorized_under_Tier_B",
        "official_qualification_activated",
        "official_marker_operations_authorized",
        "real_private_network_device_or_release_authorized",
        "full_scale_FS3_attempts_before_proof",
        "implementation_artifacts",
        "implementation_artifact_set_sha256",
        "proof_sha256",
    }
)
RECEIPT_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "attempt_status",
        "contract_sha256",
        "implementation_proof_sha256",
        "started_at_unix_ns",
        "failure_timeout_refusal_or_cap_breach_consumes_attempt",
        "official_marker_schema",
    }
)
PUBLIC_FAILURE_FAMILIES = frozenset(
    {
        "FS3-parent_hash_or_green_proof_drift",
        "FS3-duplicate_or_missing_rehearsal_receipt",
        "FS3-official_capability_or_marker_access",
        "FS3-producer_schedule_or_counter_drift",
        "FS3-producer_verifier_process_not_isolated",
        "FS3-verifier_output_invalid",
        "FS3-aggregate_score_mismatch",
        "FS3-resource_or_monitor_failure",
        "FS3-forbidden_operation_nonzero",
        "FS3-publication_collision_partial_write_or_cleanup_escape",
        "FS3-claim_boundary_violation",
    }
)
RESULT_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "route",
        "mode",
        "official_qualification",
        "attempt_consumed",
        "contract_sha256",
        "implementation_proof_sha256",
        "rehearsal_receipt_sha256",
        "completed_full_producer_runs",
        "completed_independent_verifier_runs",
        "distinct_producer_and_verifier_PIDs",
        "aggregate_scores_exactly_match",
        "producer_canonical_replay_sha256",
        "verifier_aggregate_sha256",
        "registered_schedule",
        "observed_generated_counters",
        "runtime_seconds",
        "peak_process_tree_RSS_bytes",
        "mandatory_process_monitor_samples",
        "observed_free_disk_bytes_before_reservation",
        "observed_free_disk_bytes_after_reservation",
        "failure_family",
        "post_target_updates",
        "official_activation_reads",
        "official_marker_operations",
        "real_or_private_path_operations",
        "real_signal_reads",
        "real_target_or_label_reads",
        "real_data_training_or_inference_runs",
        "human_operations",
        "device_stream_microphone_operations",
        "provider_or_network_operations",
        "network_bytes",
        "release_operations",
        "end_to_end_device_latency_measured",
        "retained_generated_payload_bytes",
        "scientific_claim_established",
        "warnings",
    }
)


class _GeneratedMockExecutor:
    """Result-only test double that cannot invoke a producer or verifier."""

    def __init__(self, result: Mapping[str, Any]) -> None:
        self._result = json.loads(core.canonical_json_bytes(result))
        self.calls = 0
        self.deadlines: list[float] = []

    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        self.calls += 1
        self.deadlines.append(float(kwargs["absolute_deadline"]))
        return json.loads(core.canonical_json_bytes(self._result))


def _refuse(family: str, detail: str = "") -> None:
    raise core.CommP0GeneratedRefusal(f"FS3-{family}", detail)


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else core._repo_root()


def _is_commit(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and set(value) <= HEX_40


def validate_implementation_proof(
    proof: Mapping[str, Any], *, root: str | Path | None = None
) -> dict[str, Any]:
    """Validate a future exact-green wrapper proof without Git or network."""

    repository = _repo_root(root)
    if set(proof) != PROOF_KEYS:
        _refuse("parent_hash_or_green_proof_drift")
    if (
        proof.get("schema_name") != PROOF_SCHEMA
        or proof.get("schema_version") != SCHEMA_VERSION
        or proof.get("gate_id") != GATE_ID
        or proof.get("run_id") != RUN_ID
        or proof.get("contract_sha256") != FS3.CONTRACT_SHA256
        or proof.get("full_scale_FS3_attempts_before_proof") != 0
        or proof.get("all_ordered_parents_remotely_green_on_GitHub_main") is not True
        or proof.get("both_required_full_wrapper_jobs_green") is not True
        or proof.get("one_FS3_rehearsal_authorized_under_Tier_B") is not True
        or proof.get("official_qualification_activated") is not False
        or proof.get("official_marker_operations_authorized") is not False
        or proof.get("real_private_network_device_or_release_authorized") is not False
        or any(
            not _is_commit(proof.get(key))
            for key in (
                "registration_commit",
                "prior_implementation_commit",
                "prior_proof_closeout_commit",
                "full_wrapper_implementation_commit",
            )
        )
        or proof.get("registration_commit")
        != "d42650897317b0dc353d3607a25e71f2e0d4e7c9"
        or proof.get("prior_implementation_commit")
        != "a3b561b118d606ee009c413d2f2419e976d4bc3d"
        or proof.get("prior_proof_closeout_commit")
        != "ccabfafb411e219292b103ce2327568112056286"
        or any(
            not isinstance(proof.get(key), int) or proof[key] <= 0
            for key in (
                "full_wrapper_CI_run_id",
                "full_wrapper_base_python_job_id",
                "full_wrapper_optional_neuro_readers_job_id",
            )
        )
    ):
        _refuse("parent_hash_or_green_proof_drift")
    rows = proof.get("implementation_artifacts")
    if not isinstance(rows, list) or [row.get("path") for row in rows] != list(
        IMPLEMENTATION_ARTIFACT_ALLOWLIST
    ):
        _refuse("parent_hash_or_green_proof_drift")
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
            _refuse("parent_hash_or_green_proof_drift")
        identity, _ = qualification.read_no_follow(
            repository / str(row["path"]), byte_cap=8 * 1024 * 1024
        )
        if identity.size_bytes != row["bytes"] or identity.sha256 != row["sha256"]:
            _refuse("parent_hash_or_green_proof_drift")
    if proof.get("implementation_artifact_set_sha256") != core.sha256_json(rows):
        _refuse("parent_hash_or_green_proof_drift")
    canonical = dict(proof)
    supplied = canonical.pop("proof_sha256")
    if supplied != core.sha256_json(canonical):
        _refuse("parent_hash_or_green_proof_drift")
    return dict(proof)


def validate_digest_activation(
    activation: Mapping[str, Any], *, expected_proof_sha256: str
) -> dict[str, Any]:
    """Validate the separately committed proof-digest activation record."""

    if set(activation) != ACTIVATION_KEYS:
        _refuse("parent_hash_or_green_proof_drift", "activation_schema")
    if (
        activation.get("schema_name") != ACTIVATION_SCHEMA
        or activation.get("schema_version") != SCHEMA_VERSION
        or activation.get("gate_id") != GATE_ID
        or activation.get("run_id") != RUN_ID
        or activation.get("implementation_proof_sha256")
        != expected_proof_sha256
        or not _is_commit(activation.get("implementation_proof_commit"))
        or activation.get("proof_remotely_green_on_GitHub_main") is not True
        or activation.get("one_FS3_rehearsal_activated") is not True
        or activation.get("full_scale_FS3_attempts_before_activation") != 0
        or activation.get(
            "official_real_private_network_device_release_or_claim_authorized"
        )
        is not False
        or any(
            not isinstance(activation.get(key), int) or activation[key] <= 0
            for key in (
                "implementation_proof_CI_run_id",
                "implementation_proof_base_python_job_id",
                "implementation_proof_optional_neuro_readers_job_id",
            )
        )
    ):
        _refuse("parent_hash_or_green_proof_drift", "activation_binding")
    canonical = dict(activation)
    supplied = canonical.pop("activation_record_sha256")
    if supplied != core.sha256_json(canonical):
        _refuse("parent_hash_or_green_proof_drift", "activation_hash")
    return dict(activation)


def load_digest_activation(
    repository: Path, *, expected_proof_sha256: str
) -> dict[str, Any]:
    path = repository / ACTIVATION_PATH
    if not os.path.lexists(path):
        _refuse("parent_hash_or_green_proof_drift", "proof_activation_absent")
    try:
        _, payload = qualification.read_no_follow(path, byte_cap=1_048_576)
        value = json.loads(payload)
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-parent_hash_or_green_proof_drift", "proof_activation_invalid"
        ) from exc
    if not isinstance(value, Mapping):
        _refuse("parent_hash_or_green_proof_drift", "proof_activation_invalid")
    return validate_digest_activation(value, expected_proof_sha256=expected_proof_sha256)


def load_implementation_proof(root: str | Path | None = None) -> dict[str, Any]:
    repository = _repo_root(root)
    if not os.path.lexists(repository / ACTIVATION_PATH):
        _refuse("parent_hash_or_green_proof_drift", "proof_activation_absent")
    path = repository / PROOF_PATH
    if not os.path.lexists(path):
        _refuse("parent_hash_or_green_proof_drift", "full_wrapper_proof_absent")
    try:
        identity, payload = qualification.read_no_follow(path, byte_cap=1_048_576)
    except FileNotFoundError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-parent_hash_or_green_proof_drift", "full_wrapper_proof_absent"
        ) from exc
    del identity
    try:
        proof = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-parent_hash_or_green_proof_drift"
        ) from exc
    if not isinstance(proof, Mapping):
        _refuse("parent_hash_or_green_proof_drift")
    validated = validate_implementation_proof(proof, root=repository)
    load_digest_activation(
        repository, expected_proof_sha256=str(validated["proof_sha256"])
    )
    return validated


def plan(root: str | Path | None = None) -> dict[str, Any]:
    contract = FS3.load_contract(root)
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_FS3_full_rehearsal_plan",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "mode": "generated_only_one_full_producer_plus_independent_verifier",
        "full_wrapper_implementation_proof_present": bool(
            (_repo_root(root) / PROOF_PATH).is_file()
            and (_repo_root(root) / ACTIVATION_PATH).is_file()
        ),
        "registered_attempts_maximum": 1,
        "full_producer_schedule": contract["full_producer_schedule"],
        "independent_verifier_scorer_schedule": _corrected_verifier_schedule(
            contract
        ),
        "resource_caps": contract["resource_caps"],
        "official_qualification_activated": False,
        "real_or_private_operations_authorized": False,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "run remains fail-closed until the exact wrapper proof and activation are green",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
    }


def _corrected_verifier_schedule(contract: Mapping[str, Any]) -> dict[str, Any]:
    schedule = dict(contract["independent_verifier_scorer_schedule"])
    schedule.update(
        {
            "prediction_stream_validation_passes": 2,
            "prediction_rows_verified": 91_392,
            "prediction_sets_verified": 1_428,
            "rows_per_prediction_set": 64,
            "physical_target_envelope_descriptors": 1,
            "logical_target_partitions": 2,
            "exact_identity_descriptors": 9,
        }
    )
    return schedule


def _normalize_destinations(
    output: Path, receipt: Path, *, repository: Path
) -> tuple[Path, Path, Path]:
    output = qualification._absolute_without_resolution(output)
    receipt = qualification._absolute_without_resolution(receipt)
    if output == receipt or output.parent != receipt.parent:
        _refuse("publication_collision_partial_write_or_cleanup_escape")
    activation_path = qualification._absolute_without_resolution(
        repository / core.ACTIVATION_PATH
    )
    if output == activation_path or receipt == activation_path:
        _refuse("official_capability_or_marker_access")
    try:
        descriptor = qualification._open_directory_no_follow(output.parent)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    else:
        os.close(descriptor)
    if os.path.lexists(output) or os.path.lexists(receipt):
        _refuse("duplicate_or_missing_rehearsal_receipt")
    return output, receipt, output.parent


def _create_receipt(
    path: Path, *, proof_sha256: str, started_at_unix_ns: int
) -> qualification.FileIdentity:
    record = {
        "schema_name": RECEIPT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "attempt_status": "consumed_before_full_producer",
        "contract_sha256": FS3.CONTRACT_SHA256,
        "implementation_proof_sha256": proof_sha256,
        "started_at_unix_ns": started_at_unix_ns,
        "failure_timeout_refusal_or_cap_breach_consumes_attempt": True,
        "official_marker_schema": False,
    }
    if set(record) != RECEIPT_KEYS:
        _refuse("claim_boundary_violation")
    core.assert_target_free(record)
    return qualification.create_no_replace_file(
        path, core.canonical_json_bytes(record), byte_cap=4096
    )


def _validate_full_producer(
    producer: Mapping[str, Any], contract: Mapping[str, Any], *, repository: Path
) -> dict[str, Any]:
    validated = FS2._validate_replay(producer, FS2.load_contract(repository))
    expected = contract["full_producer_schedule"]
    ledger = validated["ledger"]
    inventory = validated["prediction_inventory"]
    for key in (
        "prior_fits",
        "residualizer_fits",
        "classifier_fits",
        "temperature_calibration_fits",
        "model_inference_runs",
        "prediction_sets",
        "prediction_rows",
        "post_target_updates",
    ):
        if ledger.get(key) != expected[key]:
            _refuse("producer_schedule_or_counter_drift")
    if (
        inventory.get("rows") != expected["prediction_rows"]
        or inventory.get("sets") != expected["prediction_sets"]
        or validated.get("shortcut_fixture_executions")
        != expected["numerical_shortcut_fixture_executions"]
        or validated.get("refusal_observations") != expected["refusal_observations"]
        or validated.get("target_deliveries")
        != expected["cohort_target_deliveries"]
        or validated.get("scores") != expected["cohort_scores"]
        or validated.get("post_target_updates") != 0
        or validated.get("complete_prediction_records_materialized") is not False
        or validated.get("maximum_prediction_rows_buffered", 257)
        > expected["maximum_prediction_rows_buffered"]
    ):
        _refuse("producer_schedule_or_counter_drift")
    return validated


def _open_regular_at(directory_fd: int, name: str) -> tuple[int, tuple[int, int, int]]:
    if not name or name in {".", ".."} or "/" in name:
        _refuse("verifier_output_invalid", "invalid_descriptor_basename")
    before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        _refuse("verifier_output_invalid", "nonregular_or_hardlinked_input")
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=directory_fd,
    )
    opened = os.fstat(descriptor)
    signature = (int(opened.st_dev), int(opened.st_ino), int(opened.st_size))
    if (
        signature != (int(before.st_dev), int(before.st_ino), int(before.st_size))
        or opened.st_nlink != 1
        or not stat.S_ISREG(opened.st_mode)
    ):
        os.close(descriptor)
        _refuse("verifier_output_invalid", "input_inode_substitution")
    return descriptor, signature


def _open_identity_descriptor(path: Path) -> tuple[int, tuple[int, int, int]]:
    directory_fd = qualification._open_directory_no_follow(path.parent)
    try:
        return _open_regular_at(directory_fd, path.name)
    finally:
        os.close(directory_fd)


def _assert_descriptor_stable(
    directory_fd: int,
    name: str,
    descriptor: int,
    signature: tuple[int, int, int],
) -> None:
    opened = os.fstat(descriptor)
    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if (
        (int(opened.st_dev), int(opened.st_ino), int(opened.st_size)) != signature
        or (int(current.st_dev), int(current.st_ino), int(current.st_size))
        != signature
        or opened.st_nlink != 1
        or current.st_nlink != 1
        or not stat.S_ISREG(current.st_mode)
    ):
        _refuse("verifier_output_invalid", "input_inode_substitution")


def _write_verifier_capsule(
    verifier_root: Path, identity_descriptors: Sequence[int]
) -> tuple[Path, Path]:
    if len(identity_descriptors) != len(STRICT_IDENTITY_PATHS) + 1:
        _refuse("verifier_output_invalid", "identity_allowlist_cardinality")
    guard_root = FS2._create_owned_directory(verifier_root, "network-guard")
    qualification.create_no_replace_file(
        guard_root / "sitecustomize.py",
        STRICT_SOCKET_GUARD.encode("ascii"),
        byte_cap=16_384,
    )
    capsule_root = FS2._create_owned_directory(verifier_root, "code-capsule")
    package_root = FS2._create_owned_directory(capsule_root, "neurodecodekit")
    experiments_root = FS2._create_owned_directory(package_root, "experiments")
    qualification.create_no_replace_file(
        package_root / "__init__.py", b"", byte_cap=1
    )
    qualification.create_no_replace_file(
        experiments_root / "__init__.py", b"", byte_cap=1
    )
    module_rows = (
        (3, "comm_p0_generated_verifier_worker.py"),
        (4, "comm_p0_generated_score_worker.py"),
        (5, "comm_p0_generated_score_only.py"),
        (6, "comm_p0_generated_streaming_score.py"),
        (7, "comm_p0_generated_strict_verifier_worker.py"),
    )
    for index, name in module_rows:
        descriptor = identity_descriptors[index]
        info = os.fstat(descriptor)
        if info.st_nlink != 1 or info.st_size <= 0 or info.st_size > 1_048_576:
            _refuse("verifier_output_invalid", "capsule_identity_invalid")
        payload = os.pread(descriptor, info.st_size, 0)
        if len(payload) != info.st_size:
            _refuse("verifier_output_invalid", "capsule_identity_short_read")
        qualification.create_no_replace_file(
            experiments_root / name, payload, byte_cap=1_048_576
        )
    return guard_root, capsule_root


def _execute_strict_verifier_child(
    *,
    repository: Path,
    producer_root: Path,
    verifier_root: Path,
    proof_path: Path,
    proof_sha256: str,
    absolute_deadline: float,
    rss_cap_bytes: int,
    input_byte_cap: int,
    output_byte_cap: int,
    record_cap: int,
) -> dict[str, Any]:
    producer_directory_fd = qualification._open_directory_no_follow(producer_root)
    producer_descriptors: list[int] = []
    producer_signatures: list[tuple[int, int, int]] = []
    identity_descriptors: list[int] = []
    output_descriptors: list[int] = []
    try:
        for name in FS3.PRODUCER_INPUTS:
            descriptor, signature = _open_regular_at(producer_directory_fd, name)
            producer_descriptors.append(descriptor)
            producer_signatures.append(signature)
        for relative in STRICT_IDENTITY_PATHS:
            descriptor, _ = _open_identity_descriptor(repository / relative)
            identity_descriptors.append(descriptor)
        proof_descriptor, _ = _open_identity_descriptor(proof_path)
        identity_descriptors.append(proof_descriptor)

        score_output = verifier_root / "independent-score.json"
        verification_output = verifier_root / "verification-result.json"
        qualification.create_no_replace_file(score_output, b"", byte_cap=1)
        qualification.create_no_replace_file(verification_output, b"", byte_cap=1)
        output_descriptors.extend(
            (
                os.open(score_output, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)),
                os.open(
                    verification_output,
                    os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
                ),
            )
        )
        command: list[str] = [
            sys.executable,
            "-m",
            "neurodecodekit.experiments.comm_p0_generated_strict_verifier_worker",
        ]
        descriptor_names = (
            "contract-fd",
            "trial-manifest-fd",
            "prediction-stream-fd",
            "freeze-attestation-fd",
            "target-envelope-fd",
            "live-observations-fd",
            "hmac-key-fd",
            "producer-aggregate-fd",
        )
        for name, descriptor in zip(
            descriptor_names, producer_descriptors, strict=True
        ):
            command.extend((f"--{name}", str(descriptor)))
        command.extend(
            (
                "--verifier-score-output-fd",
                str(output_descriptors[0]),
                "--verification-output-fd",
                str(output_descriptors[1]),
            )
        )
        for descriptor in identity_descriptors:
            command.extend(("--identity-fd", str(descriptor)))
        command.extend(
            (
                "--expected-proof-sha256",
                proof_sha256,
                "--input-byte-cap",
                str(input_byte_cap),
                "--output-byte-cap",
                str(output_byte_cap),
                "--record-cap",
                str(record_cap),
            )
        )
        guard_root, capsule_root = _write_verifier_capsule(
            verifier_root, identity_descriptors
        )
        environment = qualification._sanitized_child_environment(
            verifier_root, repository
        )
        environment.pop("PYTHONPATH", None)
        environment["NDK_FS3_GUARD_DIR"] = str(guard_root)
        environment["NDK_FS3_CAPSULE_DIR"] = str(capsule_root)
        bootstrap = (
            "import runpy,sys;"
            "sys.path[:0]=[sys.argv.pop(1),sys.argv.pop(1)];"
            "import sitecustomize;"
            "runpy.run_module('neurodecodekit.experiments."
            "comm_p0_generated_strict_verifier_worker',run_name='__main__',"
            "alter_sys=True)"
        )
        command[:3] = [
            sys.executable,
            "-S",
            "-c",
            bootstrap,
            str(guard_root),
            str(capsule_root),
        ]
        all_descriptors = (
            *producer_descriptors,
            *identity_descriptors,
            *output_descriptors,
        )
        measurement = FS2._run_monitored_tree_command(
            command,
            pass_fds=all_descriptors,
            environment=environment,
            cwd=verifier_root,
            deadline_monotonic=absolute_deadline,
            rss_cap_bytes=rss_cap_bytes,
        )
        for name, descriptor, signature in zip(
            FS3.PRODUCER_INPUTS,
            producer_descriptors,
            producer_signatures,
            strict=True,
        ):
            _assert_descriptor_stable(
                producer_directory_fd, name, descriptor, signature
            )
    finally:
        for descriptor in (
            *producer_descriptors,
            *identity_descriptors,
            *output_descriptors,
        ):
            os.close(descriptor)
        os.close(producer_directory_fd)
    _, payload = qualification.read_no_follow(
        verification_output, byte_cap=output_byte_cap
    )
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal("FS3-verifier_output_invalid") from exc
    if (
        not isinstance(value, Mapping)
        or value.get("schema_name") != strict_verifier.OUTPUT_SCHEMA
        or value.get("aggregate_scores_exactly_match") is not True
        or value.get("prediction_stream_validation_passes") != 2
        or value.get("prediction_rows") != 91_392
        or value.get("prediction_sets") != 1_428
        or value.get("target_deliveries") != 2
        or value.get("scores") != 2
        or value.get("identity_verification", {}).get(
            "exact_identity_artifacts_verified"
        )
        != 9
        or value.get("physical_target_envelope_descriptors") != 1
        or value.get("logical_target_partitions")
        != ["discovery", "independent_replication"]
        or value.get("model_fits") != 0
        or value.get("model_inference_runs") != 0
        or value.get("parameter_updates") != 0
    ):
        _refuse("verifier_output_invalid")
    core.assert_target_free(value)
    result = dict(value)
    result["peak_process_tree_RSS_bytes"] = measurement.peak_process_tree_RSS_bytes
    result["mandatory_process_monitor_samples"] = measurement.monitor_samples
    return result


def _sample_parent_tree_rss() -> int:
    rows = FS2._process_rows()
    members = FS2._descendants(rows, os.getpid())
    return sum(rows[pid][1] for pid in members if pid in rows)


def _parent_rss_checkpoint(
    sample: Callable[[], int], *, cap_bytes: int, peak_bytes: int, samples: int
) -> tuple[int, int]:
    observed = int(sample())
    if observed <= 0 or observed > cap_bytes:
        _refuse("resource_or_monitor_failure", "parent_RSS")
    return max(peak_bytes, observed), samples + 1


def _stage_fsync_and_promote(
    output: Path,
    result: Mapping[str, Any],
    *,
    byte_cap: int,
    started: float,
    absolute_deadline: float,
    monotonic: Callable[[], float],
    sample_parent_rss: Callable[[], int],
    rss_cap_bytes: int,
) -> dict[str, Any]:
    """Publish one canonical result with a stable decisecond post-fsync runtime."""

    directory_fd = qualification._open_directory_no_follow(output.parent)
    stage_name = f".comm-p0-g-fs3-result-{secrets.token_hex(16)}.tmp"
    descriptor = -1
    linked = False
    try:
        descriptor = os.open(
            stage_name,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        candidate = dict(result)
        stage_rss = int(sample_parent_rss())
        if stage_rss <= 0 or stage_rss > rss_cap_bytes:
            _refuse("resource_or_monitor_failure", "parent_RSS_before_staging")
        candidate["peak_process_tree_RSS_bytes"] = max(
            int(candidate.get("peak_process_tree_RSS_bytes") or 0), stage_rss
        )
        candidate["mandatory_process_monitor_samples"] = int(
            candidate.get("mandatory_process_monitor_samples") or 0
        ) + 2
        runtime = round(max(0.0, monotonic() - started), 1)
        for _ in range(16):
            candidate["runtime_seconds"] = runtime
            payload = core.canonical_json_bytes(candidate)
            if len(payload) > byte_cap:
                _refuse(
                    "publication_collision_partial_write_or_cleanup_escape",
                    "output_cap",
                )
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    _refuse(
                        "publication_collision_partial_write_or_cleanup_escape",
                        "staged_result_short_write",
                    )
                view = view[written:]
            os.fsync(descriptor)
            after_fsync = round(max(0.0, monotonic() - started), 1)
            if after_fsync == runtime:
                break
            runtime = after_fsync
        else:
            _refuse("resource_or_monitor_failure", "runtime_endpoint_unstable")
        if monotonic() >= absolute_deadline:
            _refuse("resource_or_monitor_failure", "deadline_before_promotion")
        os.link(
            stage_name,
            output.name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
            follow_symlinks=False,
        )
        linked = True
        os.fsync(directory_fd)
        os.unlink(stage_name, dir_fd=directory_fd)
        os.fsync(directory_fd)
        finished_rss = int(sample_parent_rss())
        if (
            finished_rss <= 0
            or finished_rss > rss_cap_bytes
            or finished_rss > int(candidate["peak_process_tree_RSS_bytes"])
        ):
            current = os.stat(
                output.name, dir_fd=directory_fd, follow_symlinks=False
            )
            opened = os.fstat(descriptor)
            if current.st_dev == opened.st_dev and current.st_ino == opened.st_ino:
                os.unlink(output.name, dir_fd=directory_fd)
                os.fsync(directory_fd)
                linked = False
            _refuse("resource_or_monitor_failure", "parent_RSS_after_promotion")
        if monotonic() >= absolute_deadline:
            current = os.stat(
                output.name, dir_fd=directory_fd, follow_symlinks=False
            )
            opened = os.fstat(descriptor)
            if current.st_dev == opened.st_dev and current.st_ino == opened.st_ino:
                os.unlink(output.name, dir_fd=directory_fd)
                os.fsync(directory_fd)
                linked = False
            _refuse("resource_or_monitor_failure", "deadline_after_promotion")
        return candidate
    except FileExistsError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-publication_collision_partial_write_or_cleanup_escape",
            "no_replace_promotion",
        ) from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if not linked:
            try:
                os.unlink(stage_name, dir_fd=directory_fd)
                os.fsync(directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


def _public_failure_family(exc: BaseException) -> str:
    if isinstance(exc, core.CommP0GeneratedRefusal):
        if exc.family in PUBLIC_FAILURE_FAMILIES:
            return exc.family
        lowered = str(exc).lower()
        if "aggregate_score_mismatch" in lowered:
            return "FS3-aggregate_score_mismatch"
        if any(token in lowered for token in ("deadline", "rss", "monitor", "space")):
            return "FS3-resource_or_monitor_failure"
        if any(token in lowered for token in ("target", "network", "provider", "device")):
            return "FS3-forbidden_operation_nonzero"
        if any(token in lowered for token in ("filesystem", "publication", "replace")):
            return "FS3-publication_collision_partial_write_or_cleanup_escape"
        if "verifier" in lowered:
            return "FS3-verifier_output_invalid"
        if any(token in lowered for token in ("schedule", "counter", "replay")):
            return "FS3-producer_schedule_or_counter_drift"
    return "FS3-resource_or_monitor_failure"


def _aggregate_result(
    *,
    route: str,
    contract: Mapping[str, Any],
    proof_sha256: str,
    receipt_sha256: str,
    runtime_seconds: float,
    observed_free_before: int,
    observed_free_after_reservation: int | None,
    peak_rss_bytes: int,
    monitor_samples: int,
    producer: Mapping[str, Any] | None,
    verifier: Mapping[str, Any] | None,
    failure_family: str | None,
    retained_generated_payload_bytes: int | None,
) -> dict[str, Any]:
    if failure_family is not None and failure_family not in PUBLIC_FAILURE_FAMILIES:
        _refuse("claim_boundary_violation", "unregistered_failure_family")
    observed = None
    if route == "FS3_PASS" and producer is not None and verifier is not None:
        ledger = producer["ledger"]
        observed = {
            "prior_fits": ledger["prior_fits"],
            "residualizer_fits": ledger["residualizer_fits"],
            "classifier_fits": ledger["classifier_fits"],
            "temperature_calibration_fits": ledger["temperature_calibration_fits"],
            "model_inference_runs": ledger["model_inference_runs"],
            "prediction_sets": producer["prediction_inventory"]["sets"],
            "prediction_rows": producer["prediction_inventory"]["rows"],
            "producer_target_deliveries": producer["target_deliveries"],
            "producer_scores": producer["scores"],
            "verifier_model_fits": verifier["model_fits"],
            "verifier_model_inference_runs": verifier["model_inference_runs"],
            "verifier_prediction_stream_traversals": verifier[
                "prediction_stream_validation_passes"
            ],
            "verifier_prediction_sets": verifier["prediction_sets"],
            "verifier_prediction_rows": verifier["prediction_rows"],
            "verifier_identity_artifacts_verified": verifier[
                "identity_verification"
            ]["exact_identity_artifacts_verified"],
            "physical_target_envelope_descriptors": verifier[
                "physical_target_envelope_descriptors"
            ],
            "logical_target_partitions": verifier["logical_target_partitions"],
            "verifier_target_deliveries": verifier["target_deliveries"],
            "verifier_scores": verifier["scores"],
            "post_target_updates": 0,
        }
    result = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "route": route,
        "mode": "generated_only_one_full_producer_plus_independent_verifier",
        "official_qualification": False,
        "attempt_consumed": True,
        "contract_sha256": FS3.CONTRACT_SHA256,
        "implementation_proof_sha256": proof_sha256,
        "rehearsal_receipt_sha256": receipt_sha256,
        "completed_full_producer_runs": 1 if producer is not None else 0,
        "completed_independent_verifier_runs": 1 if verifier is not None else 0,
        "distinct_producer_and_verifier_PIDs": True if route == "FS3_PASS" else None,
        "aggregate_scores_exactly_match": True if route == "FS3_PASS" else None,
        "producer_canonical_replay_sha256": (
            producer.get("canonical_replay_sha256") if producer is not None else None
        ),
        "verifier_aggregate_sha256": (
            verifier.get("verifier_aggregate_sha256") if verifier is not None else None
        ),
        "registered_schedule": {
            "full_producer": contract["full_producer_schedule"],
            "independent_verifier": _corrected_verifier_schedule(contract),
        },
        "observed_generated_counters": observed,
        "runtime_seconds": runtime_seconds,
        "peak_process_tree_RSS_bytes": peak_rss_bytes or None,
        "mandatory_process_monitor_samples": monitor_samples or None,
        "observed_free_disk_bytes_before_reservation": observed_free_before,
        "observed_free_disk_bytes_after_reservation": observed_free_after_reservation,
        "failure_family": failure_family,
        "post_target_updates": 0,
        "official_activation_reads": 0,
        "official_marker_operations": 0,
        "real_or_private_path_operations": 0,
        "real_signal_reads": 0,
        "real_target_or_label_reads": 0,
        "real_data_training_or_inference_runs": 0,
        "human_operations": 0,
        "device_stream_microphone_operations": 0,
        "provider_or_network_operations": 0,
        "network_bytes": 0,
        "release_operations": 0,
        "end_to_end_device_latency_measured": False,
        "retained_generated_payload_bytes": retained_generated_payload_bytes,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "this is not the official generated qualification",
            "generated runtime is not end-to-end device latency",
            "not scientific evidence",
        ],
    }
    if set(result) != RESULT_KEYS:
        _refuse("claim_boundary_violation", "public_result_schema")
    core.assert_target_free(result)
    return result


def _run_with_dependencies(
    output: Path,
    receipt: Path,
    *,
    root: str | Path | None,
    proof: Mapping[str, Any] | None,
    execute_producer: Callable[..., dict[str, Any]],
    execute_verifier: Callable[..., dict[str, Any]],
    free_disk_bytes: Callable[[Path], int],
    reserve_disk: Callable[[Path, int], None],
    resize_reservation: Callable[[Path, int], None],
    monotonic: Callable[[], float],
    time_ns: Callable[[], int],
    sample_parent_rss: Callable[[], int] = _sample_parent_tree_rss,
) -> dict[str, Any]:
    started = monotonic()
    repository = _repo_root(root)
    real_callbacks = (
        execute_producer is FS2._execute_replay_child_fs2,
        execute_verifier is _execute_strict_verifier_child,
    )
    mock_callbacks = (
        type(execute_producer) is _GeneratedMockExecutor,
        type(execute_verifier) is _GeneratedMockExecutor,
    )
    if all(real_callbacks):
        if proof is not None:
            _refuse("parent_hash_or_green_proof_drift", "real_callback_gate")
        proof = load_implementation_proof(repository)
    elif all(mock_callbacks):
        if proof is None:
            _refuse("parent_hash_or_green_proof_drift", "mock_proof_absent")
    else:
        _refuse("parent_hash_or_green_proof_drift", "callback_identity")
    contract = FS3.load_contract(repository)
    validated_proof = validate_implementation_proof(proof, root=repository)
    proof_sha256 = str(validated_proof["proof_sha256"])
    output, receipt, destination_root = _normalize_destinations(
        output, receipt, repository=repository
    )
    caps = contract["resource_caps"]
    observed_before = free_disk_bytes(destination_root)
    if observed_before < caps["free_bytes_required_before_reservation"]:
        _refuse("resource_or_monitor_failure", "free_space_preflight")
    absolute_deadline = started + float(caps["wall_time_seconds"])
    peak_rss, monitor_samples = _parent_rss_checkpoint(
        sample_parent_rss,
        cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
        peak_bytes=0,
        samples=0,
    )
    receipt_identity = _create_receipt(
        receipt, proof_sha256=proof_sha256, started_at_unix_ns=time_ns()
    )
    peak_rss, monitor_samples = _parent_rss_checkpoint(
        sample_parent_rss,
        cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
        peak_bytes=peak_rss,
        samples=monitor_samples,
    )
    producer: dict[str, Any] | None = None
    verifier: dict[str, Any] | None = None
    observed_after_reservation: int | None = None
    failure_family: str | None = None
    retained_generated_payload_bytes: int | None = None
    temporary_root: Path | None = None
    try:
        temporary_root = FS2._create_owned_directory(
            destination_root, f".comm-p0-g-fs3-{secrets.token_hex(16)}"
        )
        reservation_path = temporary_root / "disk-reservation.bin"
        reserve_disk(reservation_path, int(caps["aggregate_incremental_disk_bytes"]))
        observed_after_reservation = free_disk_bytes(destination_root)
        if observed_after_reservation < caps["free_bytes_required_after_reservation"]:
            _refuse("resource_or_monitor_failure", "free_space_after_reservation")
        if qualification._temporary_tree_bytes(temporary_root) > caps[
            "aggregate_incremental_disk_bytes"
        ]:
            _refuse("resource_or_monitor_failure", "reservation_cap")
        resize_reservation(
            reservation_path,
            int(
                caps["aggregate_incremental_disk_bytes"]
                - caps["temporary_disk_peak_bytes"]
            ),
        )
        peak_rss, monitor_samples = _parent_rss_checkpoint(
            sample_parent_rss,
            cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
            peak_bytes=peak_rss,
            samples=monitor_samples,
        )
        producer_root = FS2._create_owned_directory(temporary_root, "producer")
        producer = execute_producer(
            repository=repository,
            replay_root=producer_root,
            participants_per_cohort=21,
            absolute_deadline=absolute_deadline,
            vault_key=secrets.token_bytes(32),
            opaque_key=secrets.token_bytes(32),
            freeze_key=secrets.token_bytes(32),
            invocation_nonce=secrets.token_hex(32),
            rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
        )
        producer = _validate_full_producer(producer, contract, repository=repository)
        peak_rss = max(
            peak_rss,
            int(producer["peak_process_tree_RSS_bytes"]),
            int(producer.get("outer_process_tree_RSS_bytes", 0)),
        )
        monitor_samples += int(producer["monitor_samples"]) + int(
            producer.get("outer_monitor_samples", 0)
        )
        if monotonic() >= absolute_deadline:
            _refuse("resource_or_monitor_failure", "absolute_deadline")
        verifier_root = FS2._create_owned_directory(temporary_root, "verifier")
        verifier = execute_verifier(
            repository=repository,
            producer_root=producer_root,
            verifier_root=verifier_root,
            proof_path=repository / PROOF_PATH,
            proof_sha256=proof_sha256,
            absolute_deadline=absolute_deadline,
            rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
            input_byte_cap=134_217_728,
            output_byte_cap=int(caps["public_target_free_result_bytes"]),
            record_cap=int(contract["full_producer_schedule"]["prediction_rows"]),
        )
        if (
            verifier.get("aggregate_scores_exactly_match") is not True
            or verifier.get("prediction_stream_validation_passes") != 2
            or verifier.get("prediction_rows") != 91_392
            or verifier.get("prediction_sets") != 1_428
            or verifier.get("target_deliveries") != 2
            or verifier.get("scores") != 2
            or verifier.get("identity_verification", {}).get(
                "exact_identity_artifacts_verified"
            )
            != 9
            or verifier.get("model_fits") != 0
            or verifier.get("model_inference_runs") != 0
            or verifier.get("parameter_updates") != 0
        ):
            _refuse("verifier_output_invalid")
        if verifier.get("verifier_worker_pid") == producer.get(
            "isolated_replay_worker_pid"
        ):
            _refuse("producer_verifier_process_not_isolated")
        peak_rss = max(peak_rss, int(verifier["peak_process_tree_RSS_bytes"]))
        monitor_samples += int(verifier["mandatory_process_monitor_samples"])
        if qualification._temporary_tree_bytes(temporary_root) > caps[
            "aggregate_incremental_disk_bytes"
        ]:
            _refuse("resource_or_monitor_failure", "aggregate_disk_cap")
        resize_reservation(reservation_path, 0)
        qualification._unlink_invocation_file(
            reservation_path, invocation_root=temporary_root
        )
        peak_rss, monitor_samples = _parent_rss_checkpoint(
            sample_parent_rss,
            cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
            peak_bytes=peak_rss,
            samples=monitor_samples,
        )
    except Exception as exc:
        failure_family = _public_failure_family(exc)
    finally:
        if temporary_root is not None:
            try:
                FS2._remove_owned_tree(temporary_root)
            except Exception:
                failure_family = (
                    "FS3-publication_collision_partial_write_or_cleanup_escape"
                )
                retained_generated_payload_bytes = None
            else:
                retained_generated_payload_bytes = 0
    peak_rss, monitor_samples = _parent_rss_checkpoint(
        sample_parent_rss,
        cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
        peak_bytes=peak_rss,
        samples=monitor_samples,
    )
    runtime = monotonic() - started
    if runtime > float(caps["wall_time_seconds"]):
        failure_family = "FS3-resource_or_monitor_failure"
    route = (
        "FS3_PASS"
        if failure_family is None
        and producer is not None
        and verifier is not None
        and retained_generated_payload_bytes == 0
        else "FS3_PARK"
    )
    result = _aggregate_result(
        route=route,
        contract=contract,
        proof_sha256=proof_sha256,
        receipt_sha256=receipt_identity.sha256,
        runtime_seconds=runtime,
        observed_free_before=observed_before,
        observed_free_after_reservation=observed_after_reservation,
        peak_rss_bytes=peak_rss,
        monitor_samples=monitor_samples,
        producer=producer,
        verifier=verifier,
        failure_family=failure_family,
        retained_generated_payload_bytes=retained_generated_payload_bytes,
    )
    return _stage_fsync_and_promote(
        output,
        result,
        byte_cap=int(caps["public_target_free_result_bytes"]),
        started=started,
        absolute_deadline=absolute_deadline,
        monotonic=monotonic,
        sample_parent_rss=sample_parent_rss,
        rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
    )


def run_registered_rehearsal(
    output: str | Path,
    *,
    receipt: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sole FS3 attempt only after its exact wrapper proof exists."""

    return _run_with_dependencies(
        Path(output),
        Path(receipt),
        root=root,
        proof=None,
        execute_producer=FS2._execute_replay_child_fs2,
        execute_verifier=_execute_strict_verifier_child,
        free_disk_bytes=FS2._free_disk_bytes,
        reserve_disk=FS2._create_disk_reservation,
        resize_reservation=FS2._resize_disk_reservation,
        monotonic=time.monotonic,
        time_ns=time.time_ns,
    )


def inspect_result(path: str | Path) -> dict[str, Any]:
    _, payload = qualification.read_no_follow(path, byte_cap=1_048_576)
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS3-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    if (
        not isinstance(value, Mapping)
        or value.get("schema_name") != RESULT_SCHEMA
        or set(value) != RESULT_KEYS
        or value.get("route") not in {"FS3_PASS", "FS3_PARK"}
        or (
            value.get("failure_family") is not None
            and value.get("failure_family") not in PUBLIC_FAILURE_FAMILIES
        )
    ):
        _refuse("publication_collision_partial_write_or_cleanup_escape")
    core.assert_target_free(value)
    return dict(value)


def implementation_identity() -> dict[str, Any]:
    repository = _repo_root()
    paths = IMPLEMENTATION_ARTIFACT_ALLOWLIST[:-1]
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_FS3_full_wrapper_identity",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "contract_sha256": FS3.CONTRACT_SHA256,
        "artifacts": [
            {
                "path": path,
                "bytes": (repository / path).stat().st_size,
                "sha256": hashlib.sha256((repository / path).read_bytes()).hexdigest(),
            }
            for path in paths
        ],
        "full_scale_runs": 0,
        "real_or_private_operations": 0,
        "scientific_claim_established": False,
    }
