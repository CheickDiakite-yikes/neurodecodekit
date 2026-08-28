"""Generated-only COMM-P0 FS3 producer and independent verifier coordinator."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification
from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as FS2


GATE_ID = "COMM-P0-G-FS3-v0"
RUN_ID = "COMM-P0-G-FS3-R0"
SCHEMA_VERSION = "0.1.0"
CONTRACT_PATH = Path(
    "registries/communication_eeg_prospective_generated_single_execution_"
    "dual_verification_contract.v0.json"
)
CONTRACT_SHA256 = "99022366ce5aa59266d855ef9d4fd84c9cc7a1bf4f960c9398022b8e582a3771"
RESULT_SCHEMA = "neurodecodekit.comm_p0_generated_FS3_reduced_qualification"
PRODUCER_INPUTS = (
    "score-contract.json",
    "score-trials.ndjson",
    "predictions.ndjson",
    "score-freeze.json",
    "sealed-targets.json",
    "score-live.ndjson",
    "score-freeze.key",
    "score-aggregate.json",
)


def _refuse(family: str, detail: str = "") -> None:
    raise core.CommP0GeneratedRefusal(f"FS3-{family}", detail)


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else core._repo_root()


def load_contract(root: str | Path | None = None) -> dict[str, Any]:
    repository = _repo_root(root)
    identity, payload = qualification.read_no_follow(
        repository / CONTRACT_PATH,
        byte_cap=1_048_576,
    )
    if identity.sha256 != CONTRACT_SHA256:
        _refuse("parent_hash_or_green_proof_drift")
    try:
        contract = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal("FS3-parent_hash_or_green_proof_drift") from exc
    if (
        not isinstance(contract, Mapping)
        or contract.get("gate_id") != GATE_ID
        or contract.get("run_id") != RUN_ID
        or contract.get("schema_version") != SCHEMA_VERSION
    ):
        _refuse("parent_hash_or_green_proof_drift")
    parents = contract.get("bound_parents")
    if not isinstance(parents, list) or len(parents) != 10:
        _refuse("parent_hash_or_green_proof_drift")
    for row in parents:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
            _refuse("parent_hash_or_green_proof_drift")
        observed, _ = qualification.read_no_follow(
            repository / str(row["path"]),
            byte_cap=8 * 1024 * 1024,
        )
        if observed.size_bytes != row["bytes"] or observed.sha256 != row["sha256"]:
            _refuse("parent_hash_or_green_proof_drift")
    return dict(contract)


def plan(root: str | Path | None = None) -> dict[str, Any]:
    contract = load_contract(root)
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_FS3_plan",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "mode": "generated_only_single_producer_independent_verifier",
        "registration_remotely_green_on_GitHub_main": True,
        "implementation_proof_present": False,
        "registration_authorizes_execution_now": False,
        "reduced_qualification": {
            "isolated_model_replays": contract["implementation_scope"][
                "implementation_qualification_replays"
            ],
            "participants_per_cohort_maximum": contract["implementation_scope"][
                "implementation_qualification_participants_per_cohort_maximum"
            ],
            "refusal_observations": contract["implementation_scope"][
                "implementation_qualification_refusal_observations"
            ],
        },
        "full_producer_schedule": contract["full_producer_schedule"],
        "independent_verifier_scorer_schedule": contract[
            "independent_verifier_scorer_schedule"
        ],
        "resource_caps": contract["resource_caps"],
        "official_qualification_activated": False,
        "real_or_private_operations_authorized": False,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "full FS3 rehearsal remains closed pending exact implementation proof",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
    }


def _open_read(path: Path) -> int:
    return os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))


def _execute_verifier_child(
    *,
    repository: Path,
    producer_root: Path,
    verifier_root: Path,
    absolute_deadline: float,
    rss_cap_bytes: int,
    input_byte_cap: int,
    output_byte_cap: int,
    record_cap: int,
) -> dict[str, Any]:
    for name in PRODUCER_INPUTS:
        if not (producer_root / name).is_file():
            _refuse("producer_transcript_missing_or_substituted", name)
    score_output = verifier_root / "independent-score.json"
    verification_output = verifier_root / "verification-result.json"
    qualification.create_no_replace_file(score_output, b"", byte_cap=1)
    qualification.create_no_replace_file(verification_output, b"", byte_cap=1)
    input_paths = tuple(producer_root / name for name in PRODUCER_INPUTS)
    descriptors = [_open_read(path) for path in input_paths]
    descriptors.extend(
        (
            os.open(score_output, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)),
            os.open(verification_output, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)),
        )
    )
    command = (
        sys.executable,
        "-m",
        "neurodecodekit.experiments.comm_p0_generated_verifier_worker",
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
        "--producer-aggregate-fd",
        str(descriptors[7]),
        "--verifier-score-output-fd",
        str(descriptors[8]),
        "--verification-output-fd",
        str(descriptors[9]),
        "--input-byte-cap",
        str(input_byte_cap),
        "--output-byte-cap",
        str(output_byte_cap),
        "--record-cap",
        str(record_cap),
    )
    environment = qualification._sanitized_child_environment(verifier_root, repository)
    try:
        measurement = FS2._run_monitored_tree_command(
            command,
            pass_fds=descriptors,
            environment=environment,
            cwd=repository,
            deadline_monotonic=absolute_deadline,
            rss_cap_bytes=rss_cap_bytes,
        )
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
    _, payload = qualification.read_no_follow(
        verification_output,
        byte_cap=output_byte_cap,
    )
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal("FS3-verifier_output_invalid") from exc
    if (
        not isinstance(value, Mapping)
        or value.get("schema_name")
        != "neurodecodekit.comm_p0_generated_FS3_independent_verification"
        or value.get("aggregate_scores_exactly_match") is not True
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


def _validate_reduced_producer(
    producer: Mapping[str, Any], *, participants_per_cohort: int
) -> None:
    ledger = producer.get("ledger")
    inventory = producer.get("prediction_inventory")
    expected_ledger = qualification._expected_model_ledger(participants_per_cohort)
    if not isinstance(ledger, Mapping) or any(
        ledger.get(key) != value for key, value in expected_ledger.items()
    ):
        _refuse("producer_schedule_or_counter_drift")
    expected_rows = participants_per_cohort * len(core.COHORTS) * 128 * 17
    expected_sets = participants_per_cohort * len(core.COHORTS) * len(core.ENDPOINTS) * 17
    if (
        not isinstance(inventory, Mapping)
        or inventory.get("rows") != expected_rows
        or inventory.get("sets") != expected_sets
        or producer.get("refusal_observations") != 70
        or producer.get("target_deliveries") != 2
        or producer.get("scores") != 2
        or producer.get("post_target_updates") != 0
        or producer.get("complete_prediction_records_materialized") is not False
        or producer.get("maximum_prediction_rows_buffered", 257) > 256
    ):
        _refuse("producer_schedule_or_counter_drift")


def run_reduced_qualification(
    *,
    root: str | Path | None = None,
    participants_per_cohort: int = 3,
    timeout_seconds: float = 180.0,
) -> dict[str, Any]:
    """Run two reduced generated producer/verifier pairs; never full FS3."""

    contract = load_contract(root)
    maximum = contract["implementation_scope"][
        "implementation_qualification_participants_per_cohort_maximum"
    ]
    if participants_per_cohort < 1 or participants_per_cohort > maximum:
        _refuse("qualification_cohort_cardinality")
    repository = _repo_root(root)
    caps = contract["resource_caps"]
    started = time.monotonic()
    absolute_deadline = started + min(timeout_seconds, float(caps["wall_time_seconds"]))
    vault_key = secrets.token_bytes(32)
    opaque_key = secrets.token_bytes(32)
    freeze_key = secrets.token_bytes(32)
    invocation_nonce = secrets.token_hex(32)
    producers: list[dict[str, Any]] = []
    verifiers: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="comm-p0-g-FS3-dev-") as temporary:
        parent = Path(temporary)
        for index in range(2):
            replay_root = parent / f"producer-{index + 1}"
            verifier_root = parent / f"verifier-{index + 1}"
            replay_root.mkdir(mode=0o700)
            verifier_root.mkdir(mode=0o700)
            producer = FS2._execute_replay_child_fs2(
                repository=repository,
                replay_root=replay_root,
                participants_per_cohort=participants_per_cohort,
                absolute_deadline=absolute_deadline,
                vault_key=vault_key,
                opaque_key=opaque_key,
                freeze_key=freeze_key,
                invocation_nonce=invocation_nonce,
                rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
            )
            _validate_reduced_producer(
                producer,
                participants_per_cohort=participants_per_cohort,
            )
            verifier = _execute_verifier_child(
                repository=repository,
                producer_root=replay_root,
                verifier_root=verifier_root,
                absolute_deadline=absolute_deadline,
                rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
                input_byte_cap=134_217_728,
                output_byte_cap=int(caps["public_target_free_result_bytes"]),
                record_cap=max(100_000, int(producer["prediction_inventory"]["rows"])),
            )
            if verifier["verifier_worker_pid"] == producer["isolated_replay_worker_pid"]:
                _refuse("producer_verifier_process_not_isolated")
            producers.append(producer)
            verifiers.append(verifier)
    if (
        producers[0]["isolated_replay_worker_pid"]
        == producers[1]["isolated_replay_worker_pid"]
        or verifiers[0]["verifier_worker_pid"] == verifiers[1]["verifier_worker_pid"]
        or producers[0]["canonical_surface"] != producers[1]["canonical_surface"]
        or producers[0]["canonical_replay_sha256"]
        != producers[1]["canonical_replay_sha256"]
        or verifiers[0]["verifier_aggregate_sha256"]
        != verifiers[1]["verifier_aggregate_sha256"]
    ):
        _refuse("determinism_or_process_isolation_failure")
    runtime = time.monotonic() - started
    result = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "mode": "reduced_generated_only_implementation_qualification",
        "participants_per_cohort": participants_per_cohort,
        "isolated_model_replays": 2,
        "isolated_verifier_replays": 2,
        "distinct_producer_and_verifier_PIDs": True,
        "canonical_producer_surfaces_equivalent": True,
        "verifier_aggregate_scores_equivalent": True,
        "canonical_replay_sha256": producers[0]["canonical_replay_sha256"],
        "verifier_aggregate_sha256": verifiers[0]["verifier_aggregate_sha256"],
        "prediction_rows_per_replay": producers[0]["prediction_inventory"]["rows"],
        "prediction_sets_per_replay": producers[0]["prediction_inventory"]["sets"],
        "refusal_observations": sum(row["refusal_observations"] for row in producers),
        "producer_target_deliveries": sum(row["target_deliveries"] for row in producers),
        "verifier_target_deliveries": sum(row["target_deliveries"] for row in verifiers),
        "producer_scores": sum(row["scores"] for row in producers),
        "verifier_scores": sum(row["scores"] for row in verifiers),
        "post_target_updates": 0,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": max(
            *(int(row["peak_process_tree_RSS_bytes"]) for row in producers),
            *(int(row["outer_process_tree_RSS_bytes"]) for row in producers),
            *(int(row["peak_process_tree_RSS_bytes"]) for row in verifiers),
        ),
        "mandatory_process_monitor_samples": sum(
            int(row["monitor_samples"]) + int(row["outer_monitor_samples"])
            for row in producers
        )
        + sum(int(row["mandatory_process_monitor_samples"]) for row in verifiers),
        "network_requests": 0,
        "network_bytes": 0,
        "real_or_private_reads": 0,
        "human_or_device_operations": 0,
        "official_qualification_invocations": 0,
        "retained_generated_payload_bytes": 0,
        "end_to_end_device_latency_measured": False,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "reduced qualification; no full FS3 rehearsal ran",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
    }
    core.assert_target_free(result)
    if (
        result["refusal_observations"] != 140
        or result["post_target_updates"] != 0
        or result["retained_generated_payload_bytes"] != 0
        or runtime > min(timeout_seconds, float(caps["wall_time_seconds"]))
        or result["peak_process_tree_RSS_bytes"] > caps["peak_process_tree_RSS_bytes"]
    ):
        _refuse("qualification_acceptance_gate_failure")
    return result


def implementation_identity() -> dict[str, Any]:
    repository = _repo_root()
    paths = (
        "src/neurodecodekit/experiments/comm_p0_generated_dual_verification.py",
        "src/neurodecodekit/experiments/comm_p0_generated_verifier_worker.py",
        "src/neurodecodekit/comm_p0_FS3_cli.py",
        "tests/test_comm_p0_generated_dual_verification.py",
    )
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_FS3_implementation_identity",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "contract_sha256": CONTRACT_SHA256,
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
