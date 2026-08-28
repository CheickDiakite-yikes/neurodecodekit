from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_dual_verification_rehearsal as rehearsal
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification
from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as FS2
from neurodecodekit.experiments import comm_p0_generated_strict_verifier_worker as strict_verifier


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_RECORD = ROOT / "registries" / (
    "communication_eeg_prospective_generated_single_execution_dual_"
    "verification_full_rehearsal_implementation.v0.json"
)


def _artifact_rows() -> list[dict[str, object]]:
    rows = []
    for relative in rehearsal.IMPLEMENTATION_ARTIFACT_ALLOWLIST:
        payload = (ROOT / relative).read_bytes()
        rows.append(
            {
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return rows


def _proof() -> dict[str, object]:
    rows = _artifact_rows()
    value = {
        "schema_name": rehearsal.PROOF_SCHEMA,
        "schema_version": rehearsal.SCHEMA_VERSION,
        "gate_id": rehearsal.GATE_ID,
        "run_id": rehearsal.RUN_ID,
        "contract_sha256": rehearsal.FS3.CONTRACT_SHA256,
        "registration_commit": "d42650897317b0dc353d3607a25e71f2e0d4e7c9",
        "prior_implementation_commit": "a3b561b118d606ee009c413d2f2419e976d4bc3d",
        "prior_proof_closeout_commit": "ccabfafb411e219292b103ce2327568112056286",
        "full_wrapper_implementation_commit": "d" * 40,
        "full_wrapper_CI_run_id": 1,
        "full_wrapper_base_python_job_id": 2,
        "full_wrapper_optional_neuro_readers_job_id": 3,
        "all_ordered_parents_remotely_green_on_GitHub_main": True,
        "both_required_full_wrapper_jobs_green": True,
        "one_FS3_rehearsal_authorized_under_Tier_B": True,
        "official_qualification_activated": False,
        "official_marker_operations_authorized": False,
        "real_private_network_device_or_release_authorized": False,
        "full_scale_FS3_attempts_before_proof": 0,
        "implementation_artifacts": rows,
        "implementation_artifact_set_sha256": core.sha256_json(rows),
    }
    value["proof_sha256"] = core.sha256_json(value)
    return value


def _activation(proof_sha256: str) -> dict[str, object]:
    value = {
        "schema_name": rehearsal.ACTIVATION_SCHEMA,
        "schema_version": rehearsal.SCHEMA_VERSION,
        "gate_id": rehearsal.GATE_ID,
        "run_id": rehearsal.RUN_ID,
        "implementation_proof_sha256": proof_sha256,
        "implementation_proof_commit": "e" * 40,
        "implementation_proof_CI_run_id": 4,
        "implementation_proof_base_python_job_id": 5,
        "implementation_proof_optional_neuro_readers_job_id": 6,
        "proof_remotely_green_on_GitHub_main": True,
        "one_FS3_rehearsal_activated": True,
        "full_scale_FS3_attempts_before_activation": 0,
        "official_real_private_network_device_release_or_claim_authorized": False,
    }
    value["activation_record_sha256"] = core.sha256_json(value)
    return value


def _fake_producer(pid: int = 101) -> dict[str, object]:
    expected = FS2.load_contract(ROOT)["schedule_per_replay"]
    return {
        "canonical_surface": {"surface": "one-full-producer"},
        "canonical_replay_sha256": hashlib.sha256(b"one-full-producer").hexdigest(),
        "isolated_replay_worker_pid": pid,
        "ledger": {
            key: expected[key]
            for key in (
                "prior_fits",
                "residualizer_fits",
                "classifier_fits",
                "temperature_calibration_fits",
                "model_inference_runs",
                "prediction_sets",
                "prediction_rows",
                "post_target_updates",
            )
        },
        "prediction_inventory": {
            "rows": expected["prediction_rows"],
            "sets": expected["prediction_sets"],
        },
        "maximum_prediction_rows_buffered": 1,
        "complete_prediction_records_materialized": False,
        "shortcut_fixture_executions": expected[
            "numerical_shortcut_fixture_executions"
        ],
        "shortcut_counters": {
            "prediction_rows": expected["prediction_rows"],
            "target_deliveries": expected["shortcut_target_deliveries"],
            "scores": expected["shortcut_scores"],
        },
        "refusal_observations": expected["refusal_observations"],
        "target_deliveries": expected["cohort_target_deliveries"],
        "scores": expected["cohort_scores"],
        "post_target_updates": 0,
        "generated_input_bytes_written": 1_000,
        "private_output_bytes_written": 2_000,
        "temporary_disk_peak_bytes": 3_000,
        "peak_process_tree_RSS_bytes": 64_000_000,
        "outer_process_tree_RSS_bytes": 65_000_000,
        "monitor_samples": 10,
        "outer_monitor_samples": 5,
    }


def _fake_verifier(pid: int = 202, *, match: bool = True) -> dict[str, object]:
    return {
        "aggregate_scores_exactly_match": match,
        "verifier_worker_pid": pid,
        "verifier_aggregate_sha256": hashlib.sha256(b"aggregate").hexdigest(),
        "model_fits": 0,
        "model_inference_runs": 0,
        "parameter_updates": 0,
        "prediction_stream_validation_passes": 2,
        "prediction_rows": 91_392,
        "prediction_sets": 1_428,
        "target_deliveries": 2,
        "scores": 2,
        "identity_verification": {"exact_identity_artifacts_verified": 9},
        "physical_target_envelope_descriptors": 1,
        "logical_target_partitions": ["discovery", "independent_replication"],
        "peak_process_tree_RSS_bytes": 32_000_000,
        "mandatory_process_monitor_samples": 7,
    }


def _small_reservation(path: Path, _: int) -> None:
    path.write_bytes(b"reserved")


def _small_resize(path: Path, size: int) -> None:
    with path.open("r+b") as handle:
        handle.truncate(min(size, 16))


def _free_disk(_: Path) -> int:
    return 24 * 1024**3


def _clock() -> object:
    value = -0.01

    def current() -> float:
        nonlocal value
        value += 0.01
        return value

    return current


def _run_mock(
    tmp_path: Path,
    *,
    execute_producer=_fake_producer,
    execute_verifier=_fake_verifier,
) -> dict[str, object]:
    producer = rehearsal._GeneratedMockExecutor(execute_producer())
    verifier = rehearsal._GeneratedMockExecutor(execute_verifier())
    return rehearsal._run_with_dependencies(
        tmp_path / "result.json",
        tmp_path / "receipt.json",
        root=ROOT,
        proof=_proof(),
        execute_producer=producer,
        execute_verifier=verifier,
        free_disk_bytes=_free_disk,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
        sample_parent_rss=lambda: 48_000_000,
    )


def test_contract_plan_and_future_proof_are_strict() -> None:
    plan = rehearsal.plan(ROOT)
    proof = _proof()

    assert plan["registered_attempts_maximum"] == 1
    assert plan["independent_verifier_scorer_schedule"][
        "prediction_stream_validation_passes"
    ] == 2
    assert (
        plan["independent_verifier_scorer_schedule"]["exact_identity_descriptors"]
        == 9
    )
    assert plan["full_wrapper_implementation_proof_present"] is False
    assert plan["official_qualification_activated"] is False
    assert rehearsal.validate_implementation_proof(proof, root=ROOT) == proof
    activation = _activation(str(proof["proof_sha256"]))
    assert rehearsal.validate_digest_activation(
        activation, expected_proof_sha256=str(proof["proof_sha256"])
    ) == activation
    activation["implementation_proof_sha256"] = "0" * 64
    with pytest.raises(core.CommP0GeneratedRefusal, match="activation_binding"):
        rehearsal.validate_digest_activation(
            activation, expected_proof_sha256=str(proof["proof_sha256"])
        )
    proof["official_qualification_activated"] = True
    with pytest.raises(core.CommP0GeneratedRefusal, match="parent_hash"):
        rehearsal.validate_implementation_proof(proof, root=ROOT)


def test_real_callback_path_rejects_in_memory_proof(tmp_path: Path) -> None:
    with pytest.raises(core.CommP0GeneratedRefusal, match="real_callback_gate"):
        rehearsal._run_with_dependencies(
            tmp_path / "result.json",
            tmp_path / "receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_producer=FS2._execute_replay_child_fs2,
            execute_verifier=rehearsal._execute_strict_verifier_child,
            free_disk_bytes=_free_disk,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
            sample_parent_rss=lambda: 48_000_000,
        )
    assert list(tmp_path.iterdir()) == []

    class ExecutableSubclass(rehearsal._GeneratedMockExecutor):
        def __call__(self, **kwargs):
            return FS2._execute_replay_child_fs2(**kwargs)

    with pytest.raises(core.CommP0GeneratedRefusal, match="callback_identity"):
        rehearsal._run_with_dependencies(
            tmp_path / "subclass-result.json",
            tmp_path / "subclass-receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_producer=ExecutableSubclass(_fake_producer()),
            execute_verifier=rehearsal._GeneratedMockExecutor(_fake_verifier()),
            free_disk_bytes=_free_disk,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
            sample_parent_rss=lambda: 48_000_000,
        )
    assert list(tmp_path.iterdir()) == []

    with pytest.raises(core.CommP0GeneratedRefusal, match="callback_identity"):
        rehearsal._run_with_dependencies(
            tmp_path / "wrapped-result.json",
            tmp_path / "wrapped-receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_producer=lambda **kwargs: FS2._execute_replay_child_fs2(**kwargs),
            execute_verifier=lambda **kwargs: rehearsal._execute_strict_verifier_child(
                **kwargs
            ),
            free_disk_bytes=_free_disk,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
            sample_parent_rss=lambda: 48_000_000,
        )
    assert list(tmp_path.iterdir()) == []


def test_mock_pass_consumes_receipt_and_publishes_target_free_result(
    tmp_path: Path,
) -> None:
    result = _run_mock(tmp_path)

    assert result["route"] == "FS3_PASS"
    assert result["attempt_consumed"] is True
    assert result["completed_full_producer_runs"] == 1
    assert result["completed_independent_verifier_runs"] == 1
    assert result["distinct_producer_and_verifier_PIDs"] is True
    assert result["aggregate_scores_exactly_match"] is True
    assert result["official_marker_operations"] == 0
    assert result["retained_generated_payload_bytes"] == 0
    assert rehearsal.inspect_result(tmp_path / "result.json") == result
    receipt = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["schema_name"] == rehearsal.RECEIPT_SCHEMA
    with pytest.raises(core.CommP0GeneratedRefusal):
        qualification.validate_activation_binding(receipt, root=ROOT)
    assert not any(path.name.startswith(".comm-p0-g-fs3-") for path in tmp_path.iterdir())


def test_verifier_mismatch_parks_after_receipt_without_second_attempt(
    tmp_path: Path,
) -> None:
    result = _run_mock(tmp_path, execute_verifier=lambda: _fake_verifier(match=False))

    assert result["route"] == "FS3_PARK"
    assert result["failure_family"] == "FS3-verifier_output_invalid"
    assert (tmp_path / "receipt.json").exists()
    with pytest.raises(core.CommP0GeneratedRefusal, match="duplicate_or_missing"):
        _run_mock(tmp_path)


def test_pre_receipt_space_and_path_refusals_do_not_consume(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    target = tmp_path / "elsewhere.json"
    target.write_text("untouched", encoding="utf-8")
    output.symlink_to(target)
    producer = rehearsal._GeneratedMockExecutor(_fake_producer())
    verifier = rehearsal._GeneratedMockExecutor(_fake_verifier())

    with pytest.raises(core.CommP0GeneratedRefusal, match="duplicate_or_missing"):
        rehearsal._run_with_dependencies(
            output,
            tmp_path / "receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_producer=producer,
            execute_verifier=verifier,
            free_disk_bytes=_free_disk,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
            sample_parent_rss=lambda: 48_000_000,
        )
    assert producer.calls == 0
    assert target.read_text(encoding="utf-8") == "untouched"
    assert not (tmp_path / "receipt.json").exists()

    clean = tmp_path / "clean"
    clean.mkdir()
    with pytest.raises(core.CommP0GeneratedRefusal, match="free_space_preflight"):
        rehearsal._run_with_dependencies(
            clean / "result.json",
            clean / "receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_producer=producer,
            execute_verifier=verifier,
            free_disk_bytes=lambda _: 19 * 1024**3,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
            sample_parent_rss=lambda: 48_000_000,
        )
    assert list(clean.iterdir()) == []


def test_post_receipt_reservation_failure_consumes_without_producer(
    tmp_path: Path,
) -> None:
    def reserve(_: Path, __: int) -> None:
        assert (tmp_path / "receipt.json").exists()
        raise OSError("generated fixture reservation failure")

    producer = rehearsal._GeneratedMockExecutor(_fake_producer())
    verifier = rehearsal._GeneratedMockExecutor(_fake_verifier())

    result = rehearsal._run_with_dependencies(
        tmp_path / "result.json",
        tmp_path / "receipt.json",
        root=ROOT,
        proof=_proof(),
        execute_producer=producer,
        execute_verifier=verifier,
        free_disk_bytes=_free_disk,
        reserve_disk=reserve,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
        sample_parent_rss=lambda: 48_000_000,
    )

    assert result["route"] == "FS3_PARK"
    assert result["attempt_consumed"] is True
    assert result["completed_full_producer_runs"] == 0
    assert producer.calls == 0


def test_one_deadline_is_shared_and_official_capability_is_never_touched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("official capability was touched")

    monkeypatch.setattr(qualification, "load_and_validate_activation", forbidden)
    monkeypatch.setattr(qualification, "create_consumed_marker", forbidden)
    monkeypatch.setattr(qualification, "run_official_qualification", forbidden)

    producer = rehearsal._GeneratedMockExecutor(_fake_producer())
    verifier = rehearsal._GeneratedMockExecutor(_fake_verifier())

    result = rehearsal._run_with_dependencies(
        tmp_path / "result.json",
        tmp_path / "receipt.json",
        root=ROOT,
        proof=_proof(),
        execute_producer=producer,
        execute_verifier=verifier,
        free_disk_bytes=_free_disk,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
        sample_parent_rss=lambda: 48_000_000,
    )

    assert result["route"] == "FS3_PASS"
    assert producer.deadlines + verifier.deadlines == [180.0, 180.0]


def test_strict_verifier_binds_identities_and_exact_full_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    proof = _proof()
    proof_path = tmp_path / "proof.json"
    proof_path.write_bytes(core.canonical_json_bytes(proof))
    identity_fds = [os.open(ROOT / path, os.O_RDONLY) for path in rehearsal.STRICT_IDENTITY_PATHS]
    identity_fds.append(os.open(proof_path, os.O_RDONLY))
    dummy_path = tmp_path / "dummy"
    dummy_path.write_bytes(b"fixture")
    dummy_fd = os.open(dummy_path, os.O_RDONLY)
    score_path = tmp_path / "score.json"
    verification_path = tmp_path / "verification.json"
    score_fd = os.open(score_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    verification_fd = os.open(
        verification_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
    )

    records = [
        {"participant_id": participant, "condition": "signal", "endpoint": "E1"}
        for participant in ("P01", "P02")
        for _ in range(2)
    ]

    def fixture_iterator(*_: object, **__: object):
        return iter(records)

    def legacy_result(**_: object) -> dict[str, object]:
        for _ in strict_verifier.score_worker._iter_ndjson_descriptor():
            pass
        for _ in strict_verifier.score_worker._iter_ndjson_descriptor():
            pass
        return {
            "schema_name": "legacy",
            "schema_version": "0.1.0",
            "gate_id": rehearsal.GATE_ID,
            "verifier_worker_pid": 99,
            "producer_aggregate_sha256": "a" * 64,
            "verifier_aggregate_sha256": "a" * 64,
            "aggregate_scores_exactly_match": True,
            "prediction_stream_validation_passes": 2,
            "prediction_rows": 4,
            "prediction_sets": 2,
            "score": {
                "prediction_quality": {
                    "assigned_prediction_rows": 4,
                    "present_prediction_rows": 4,
                    "valid_prediction_rows": 4,
                    "missing_prediction_rows_retained": 0,
                    "invalid_prediction_rows_retained": 0,
                    "rows_dropped": 0,
                }
            },
            "target_deliveries": 2,
            "scores": 2,
            "model_fits": 0,
            "transform_fits": 0,
            "model_inference_runs": 0,
            "threshold_or_calibration_selection_operations": 0,
            "prediction_sets_created": 0,
            "prediction_rows_created": 0,
            "parameter_updates": 0,
            "language_model_operations": 0,
            "post_target_updates": 0,
            "contains_row_level_output": False,
            "generated_only": True,
            "official_qualification": False,
            "scientific_claim_established": False,
            "capability_audit": {},
        }

    monkeypatch.setattr(strict_verifier, "_assert_active_socket_guard", lambda: None)
    monkeypatch.setattr(
        strict_verifier, "_assert_loaded_capsule_identities", lambda **_: None
    )
    monkeypatch.setattr(strict_verifier.legacy, "descriptor_main", legacy_result)
    monkeypatch.setattr(
        strict_verifier.score_worker, "_iter_ndjson_descriptor", fixture_iterator
    )
    monkeypatch.setattr(strict_verifier, "EXPECTED_PREDICTION_ROWS", 4)
    monkeypatch.setattr(strict_verifier, "EXPECTED_PREDICTION_SETS", 2)
    monkeypatch.setattr(strict_verifier, "EXPECTED_ROWS_PER_SET", 2)
    try:
        result = strict_verifier.descriptor_main(
            contract_fd=dummy_fd,
            trial_manifest_fd=dummy_fd,
            prediction_stream_fd=dummy_fd,
            freeze_attestation_fd=dummy_fd,
            target_envelope_fd=dummy_fd,
            live_observations_fd=dummy_fd,
            hmac_key_fd=dummy_fd,
            producer_aggregate_fd=dummy_fd,
            verifier_score_output_fd=score_fd,
            verification_output_fd=verification_fd,
            identity_fds=identity_fds,
            expected_proof_sha256=str(proof["proof_sha256"]),
            input_byte_cap=1_048_576,
            output_byte_cap=1_048_576,
            record_cap=91_392,
        )
    finally:
        for descriptor in (*identity_fds, dummy_fd, score_fd, verification_fd):
            os.close(descriptor)

    assert result["prediction_stream_validation_passes"] == 2
    assert result["prediction_rows"] == 4
    assert result["prediction_sets"] == 2
    assert result["observed_rows_per_prediction_set"] == 2
    assert result["identity_verification"]["exact_identity_artifacts_verified"] == 9


def test_observed_rows_per_set_rejects_balanced_total_with_unequal_sets() -> None:
    records = [
        *(
            {"participant_id": "P01", "condition": "signal", "endpoint": "E1"}
            for _ in range(3)
        ),
        {"participant_id": "P02", "condition": "signal", "endpoint": "E1"},
    ]
    completed: list[dict[str, int]] = []
    original = (
        strict_verifier.EXPECTED_PREDICTION_ROWS,
        strict_verifier.EXPECTED_PREDICTION_SETS,
        strict_verifier.EXPECTED_ROWS_PER_SET,
    )
    strict_verifier.EXPECTED_PREDICTION_ROWS = 4
    strict_verifier.EXPECTED_PREDICTION_SETS = 2
    strict_verifier.EXPECTED_ROWS_PER_SET = 2
    try:
        with pytest.raises(Exception, match="observed_rows_per_set"):
            list(strict_verifier._audit_prediction_records(records, completed))
    finally:
        (
            strict_verifier.EXPECTED_PREDICTION_ROWS,
            strict_verifier.EXPECTED_PREDICTION_SETS,
            strict_verifier.EXPECTED_ROWS_PER_SET,
        ) = original
    assert completed == []


def test_strict_verifier_rejects_reduced_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(strict_verifier, "_assert_active_socket_guard", lambda: None)
    monkeypatch.setattr(
        strict_verifier,
        "_verify_identities",
        lambda *_args, **_kwargs: {
            "exact_identity_artifacts_verified": 9,
            "identity_set_sha256": "a" * 64,
        },
    )
    monkeypatch.setattr(
        strict_verifier.legacy,
        "descriptor_main",
        lambda **_: {
            **_fake_verifier(),
            "prediction_rows": 13_056,
            "prediction_sets": 204,
            "post_target_updates": 0,
            "transform_fits": 0,
            "prediction_sets_created": 0,
            "prediction_rows_created": 0,
            "language_model_operations": 0,
        },
    )
    with pytest.raises(Exception, match="exact_full_inventory_mismatch"):
        strict_verifier.descriptor_main(
            contract_fd=0,
            trial_manifest_fd=0,
            prediction_stream_fd=0,
            freeze_attestation_fd=0,
            target_envelope_fd=0,
            live_observations_fd=0,
            hmac_key_fd=0,
            producer_aggregate_fd=0,
            verifier_score_output_fd=1,
            verification_output_fd=1,
            identity_fds=(),
            expected_proof_sha256="a" * 64,
            input_byte_cap=1,
            output_byte_cap=1,
            record_cap=91_392,
        )


def test_strict_verifier_rejects_invalid_probability_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(strict_verifier, "_assert_active_socket_guard", lambda: None)
    monkeypatch.setattr(
        strict_verifier,
        "_verify_identities",
        lambda *_args, **_kwargs: {
            "exact_identity_artifacts_verified": 9,
            "identity_set_sha256": "a" * 64,
        },
    )
    value = {
        **_fake_verifier(),
        "post_target_updates": 0,
        "transform_fits": 0,
        "prediction_sets_created": 0,
        "prediction_rows_created": 0,
        "language_model_operations": 0,
        "score": {
            "prediction_quality": {
                "assigned_prediction_rows": 91_392,
                "present_prediction_rows": 91_392,
                "valid_prediction_rows": 91_391,
                "missing_prediction_rows_retained": 0,
                "invalid_prediction_rows_retained": 1,
                "rows_dropped": 0,
            }
        },
    }
    monkeypatch.setattr(
        strict_verifier.legacy, "descriptor_main", lambda **_: value
    )
    with pytest.raises(Exception, match="exact_full_inventory_mismatch"):
        strict_verifier.descriptor_main(
            contract_fd=0,
            trial_manifest_fd=0,
            prediction_stream_fd=0,
            freeze_attestation_fd=0,
            target_envelope_fd=0,
            live_observations_fd=0,
            hmac_key_fd=0,
            producer_aggregate_fd=0,
            verifier_score_output_fd=1,
            verification_output_fd=1,
            identity_fds=(),
            expected_proof_sha256="a" * 64,
            input_byte_cap=1,
            output_byte_cap=1,
            record_cap=91_392,
        )


def test_producer_descriptor_open_rejects_symlink_and_hardlink(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"generated")
    symlink = tmp_path / "symlink"
    symlink.symlink_to(source)
    directory_fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(core.CommP0GeneratedRefusal, match="nonregular_or_hardlinked"):
            rehearsal._open_regular_at(directory_fd, symlink.name)
        hardlink = tmp_path / "hardlink"
        os.link(source, hardlink)
        with pytest.raises(core.CommP0GeneratedRefusal, match="nonregular_or_hardlinked"):
            rehearsal._open_regular_at(directory_fd, source.name)
    finally:
        os.close(directory_fd)


def test_actual_isolated_capsule_binds_code_and_blocks_socket(tmp_path: Path) -> None:
    verifier_root = tmp_path / "verifier"
    verifier_root.mkdir()
    proof = _proof()
    proof_path = tmp_path / "proof.json"
    proof_path.write_bytes(core.canonical_json_bytes(proof))
    identity_fds = [
        os.open(ROOT / path, os.O_RDONLY) for path in rehearsal.STRICT_IDENTITY_PATHS
    ]
    identity_fds.append(os.open(proof_path, os.O_RDONLY))
    output_path = tmp_path / "identity.json"
    output_fd = os.open(
        output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
    )
    guard_root, capsule_root = rehearsal._write_verifier_capsule(
        verifier_root, identity_fds
    )
    script = (
        "import json,os,sys;"
        "g=sys.argv.pop(1);c=sys.argv.pop(1);o=int(sys.argv.pop(1));"
        "p=sys.argv.pop(1);sys.path[:0]=[g,c];import sitecustomize;"
        "from neurodecodekit.experiments import "
        "comm_p0_generated_strict_verifier_worker as w;"
        "w._assert_active_socket_guard();"
        "v=w._verify_identities(tuple(map(int,sys.argv[1:])),"
        "expected_proof_sha256=p);"
        "os.write(o,json.dumps(v,sort_keys=True).encode('utf-8'))"
    )
    environment = {
        "HOME": str(verifier_root),
        "LANG": "C.UTF-8",
        "PATH": "/usr/bin:/bin",
        "TMPDIR": str(verifier_root),
        "PYTHONHASHSEED": "0",
        "NDK_FS3_GUARD_DIR": str(guard_root),
        "NDK_FS3_CAPSULE_DIR": str(capsule_root),
    }
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-S",
                "-c",
                script,
                str(guard_root),
                str(capsule_root),
                str(output_fd),
                str(proof["proof_sha256"]),
                *(str(value) for value in identity_fds),
            ],
            cwd=verifier_root,
            env=environment,
            pass_fds=(*identity_fds, output_fd),
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        for descriptor in (*identity_fds, output_fd):
            os.close(descriptor)

    assert completed.returncode == 0, completed.stderr
    observed = json.loads(output_path.read_text(encoding="utf-8"))
    assert observed["exact_identity_artifacts_verified"] == 9


def test_production_capsule_entrypoint_refuses_malformed_stream(tmp_path: Path) -> None:
    producer_root = tmp_path / "producer"
    verifier_root = tmp_path / "verifier"
    producer_root.mkdir()
    verifier_root.mkdir()
    for name in rehearsal.FS3.PRODUCER_INPUTS:
        (producer_root / name).write_bytes(b"x")
    proof = _proof()
    proof_path = tmp_path / "proof.json"
    proof_path.write_bytes(core.canonical_json_bytes(proof))

    with pytest.raises(core.CommP0GeneratedRefusal, match="resource_or_monitor_failure"):
        rehearsal._execute_strict_verifier_child(
            repository=ROOT,
            producer_root=producer_root,
            verifier_root=verifier_root,
            proof_path=proof_path,
            proof_sha256=str(proof["proof_sha256"]),
            absolute_deadline=time.monotonic() + 10.0,
            rss_cap_bytes=536_870_912,
            input_byte_cap=1_048_576,
            output_byte_cap=1_048_576,
            record_cap=91_392,
        )
    assert (verifier_root / "code-capsule").is_dir()
    assert (verifier_root / "network-guard").is_dir()


def test_publication_crossing_deadline_removes_invocation_output(tmp_path: Path) -> None:
    values = iter((1.0, 1.0, 1.0, 181.0))
    output = tmp_path / "result.json"
    with pytest.raises(core.CommP0GeneratedRefusal, match="deadline_after_promotion"):
        rehearsal._stage_fsync_and_promote(
            output,
            {"runtime_seconds": 0.0, "scientific_claim_established": False},
            byte_cap=1_048_576,
            started=0.0,
            absolute_deadline=180.0,
            monotonic=lambda: next(values),
            sample_parent_rss=lambda: 48_000_000,
            rss_cap_bytes=536_870_912,
        )
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []


def test_publication_rejects_unreported_final_rss_sample(tmp_path: Path) -> None:
    samples = iter((48_000_000, 49_000_000))
    output = tmp_path / "result.json"
    with pytest.raises(core.CommP0GeneratedRefusal, match="parent_RSS_after_promotion"):
        rehearsal._stage_fsync_and_promote(
            output,
            {
                "runtime_seconds": 0.0,
                "peak_process_tree_RSS_bytes": 47_000_000,
                "mandatory_process_monitor_samples": 5,
                "scientific_claim_established": False,
            },
            byte_cap=1_048_576,
            started=0.0,
            absolute_deadline=180.0,
            monotonic=lambda: 1.0,
            sample_parent_rss=lambda: next(samples),
            rss_cap_bytes=536_870_912,
        )
    assert not output.exists()


def test_cli_help_plan_and_fail_closed_run(tmp_path: Path) -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "src")
    help_run = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_FS3_rehearsal_cli", "--help"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    plan_run = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_FS3_rehearsal_cli", "plan"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    closed_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "neurodecodekit.comm_p0_FS3_rehearsal_cli",
            "run",
            "--output",
            str(tmp_path / "result.json"),
            "--receipt",
            str(tmp_path / "receipt.json"),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert help_run.returncode == 0
    assert "generated-only" in help_run.stdout
    assert plan_run.returncode == 0
    assert json.loads(plan_run.stdout)["registered_attempts_maximum"] == 1
    assert closed_run.returncode == 2
    refusal = json.loads(closed_run.stdout)
    assert "proof_activation_absent" in refusal["detail"]
    assert refusal["attempt_consumed"] is False
    assert refusal["route"] is None
    assert list(tmp_path.iterdir()) == []


def test_implementation_record_binds_nonself_artifacts_and_zero_execution() -> None:
    record = json.loads(IMPLEMENTATION_RECORD.read_text(encoding="utf-8"))
    for row in record["implementation_artifacts"]:
        payload = (ROOT / row["path"]).read_bytes()
        assert row["bytes"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
    assert record["mock_qualification"]["focused_tests_expected"] == 18
    assert record["operation_counters"]["full_scale_FS3_runs"] == 0
    assert record["operation_counters"]["official_qualification_invocations"] == 0
    assert not any(record["claim_boundary"].values())
