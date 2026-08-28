import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification
from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as rehearsal


ROOT = Path(__file__).resolve().parents[1]


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
        "contract_sha256": rehearsal.CONTRACT_SHA256,
        "registration_commit": "e93058d5a9d4907c494dda5ae40881b47b76aa24",
        "implementation_commit": "1" * 40,
        "implementation_CI_run_id": 1,
        "implementation_base_python_job_id": 2,
        "implementation_optional_neuro_readers_job_id": 3,
        "registration_remotely_green_on_GitHub_main": True,
        "implementation_remotely_green_on_GitHub_main": True,
        "both_required_implementation_jobs_green": True,
        "rehearsal_execution_authorized_under_Tier_B": True,
        "official_qualification_activated": False,
        "official_marker_operations_authorized": False,
        "real_private_network_device_or_release_authorized": False,
        "full_scale_rehearsal_attempts_before_proof": 0,
        "implementation_artifacts": rows,
        "implementation_artifact_set_sha256": core.sha256_json(rows),
    }
    value["proof_sha256"] = core.sha256_json(value)
    return value


def _fake_replay(pid: int, *, surface: str = "same", peak_rss: int = 64_000_000) -> dict:
    expected = rehearsal.load_contract(ROOT)["schedule_per_replay"]
    ledger = {
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
    }
    return {
        "canonical_surface": {"surface": surface},
        "canonical_replay_sha256": hashlib.sha256(surface.encode()).hexdigest(),
        "isolated_replay_worker_pid": pid,
        "ledger": ledger,
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
        "peak_process_tree_RSS_bytes": peak_rss,
        "outer_process_tree_RSS_bytes": peak_rss + 1,
        "monitor_samples": 10,
        "outer_monitor_samples": 5,
    }


def _small_reservation(path: Path, _: int) -> None:
    path.write_bytes(b"reserved")


def _small_resize(path: Path, size: int) -> None:
    with path.open("r+b") as handle:
        handle.truncate(size)


def _free_disk_bytes(_: Path) -> int:
    return 24 * 1024**3


def _clock() -> callable:
    values = iter((0.0, 1.0, 2.0, 3.0))
    return lambda: next(values)


def test_contract_and_future_proof_are_strict() -> None:
    contract = rehearsal.load_contract(ROOT)
    proof = _proof()

    assert contract["gate_id"] == rehearsal.GATE_ID
    assert rehearsal.validate_implementation_proof(proof, root=ROOT) == proof
    proof["official_qualification_activated"] = True
    with pytest.raises(core.CommP0GeneratedRefusal, match="parent_hash"):
        rehearsal.validate_implementation_proof(proof, root=ROOT)


def test_implementation_record_binds_every_nonself_artifact() -> None:
    path = (
        ROOT
        / "registries/communication_eeg_prospective_generated_two_child_"
        "rehearsal_implementation.v0.json"
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    observed_bytes = 0
    for row in record["artifacts"]:
        payload = (ROOT / row["path"]).read_bytes()
        observed_bytes += len(payload)
        assert row["bytes"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
    assert record["artifact_summary"] == {
        "count": len(record["artifacts"]),
        "bytes": observed_bytes,
    }
    assert record["generated_mock_qualification"]["focused_tests_passed"] == 15


def test_public_run_transition_never_executes_rehearsal(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    receipt = tmp_path / "receipt.json"

    if (ROOT / rehearsal.PROOF_PATH).exists():
        proof = rehearsal.load_implementation_proof(ROOT)
        assert proof["official_qualification_activated"] is False
        assert proof["real_private_network_device_or_release_authorized"] is False
    else:
        with pytest.raises(
            core.CommP0GeneratedRefusal, match="implementation_proof_absent"
        ):
            rehearsal.run_registered_rehearsal(output, receipt=receipt, root=ROOT)
    assert not output.exists()
    assert not receipt.exists()


def test_mock_two_child_pass_creates_separate_receipt_and_aggregate(tmp_path: Path) -> None:
    pids = iter((101, 202))

    def execute_replay(**_: object) -> dict:
        return _fake_replay(next(pids))

    output = tmp_path / "result.json"
    receipt = tmp_path / "receipt.json"
    result = rehearsal._run_with_dependencies(
        output,
        receipt,
        root=ROOT,
        proof=_proof(),
        execute_replay=execute_replay,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )

    assert result["route"] == "FS2_PASS"
    assert result["completed_replay_children"] == 2
    assert result["expected_replay_children"] == 2
    assert result["distinct_replay_worker_PIDs"] is True
    assert result["observed_generated_counters"] == {
        key: result["registered_totals"][key]
        for key in result["observed_generated_counters"]
        if key != "post_target_updates"
    } | {"post_target_updates": 0}
    assert result["official_qualification"] is False
    assert result["official_marker_operations"] == 0
    assert result["retained_generated_payload_bytes"] == 0
    assert rehearsal.inspect_result(output) == result
    receipt_value = json.loads(receipt.read_text(encoding="utf-8"))
    assert receipt_value["schema_name"] == rehearsal.RECEIPT_SCHEMA
    with pytest.raises(core.CommP0GeneratedRefusal):
        qualification.validate_activation_binding(receipt_value, root=ROOT)
    assert not any(path.name.startswith(".comm-p0-g-fs2-") for path in tmp_path.iterdir())


def test_canonical_mismatch_parks_and_consumes_without_rerun(tmp_path: Path) -> None:
    calls = 0

    def execute_replay(**_: object) -> dict:
        nonlocal calls
        calls += 1
        return _fake_replay(100 + calls, surface=f"surface-{calls}")

    output = tmp_path / "result.json"
    receipt = tmp_path / "receipt.json"
    result = rehearsal._run_with_dependencies(
        output,
        receipt,
        root=ROOT,
        proof=_proof(),
        execute_replay=execute_replay,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )

    assert calls == 2
    assert result["route"] == "FS2_PARK"
    assert result["failure_family"] == "FS2-canonical_replay_mismatch"
    assert receipt.exists()
    with pytest.raises(core.CommP0GeneratedRefusal, match="duplicate_or_missing"):
        rehearsal._run_with_dependencies(
            output,
            receipt,
            root=ROOT,
            proof=_proof(),
            execute_replay=execute_replay,
            free_disk_bytes=_free_disk_bytes,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 124,
        )


def test_resource_drift_parks_with_target_free_failure(tmp_path: Path) -> None:
    calls = 0

    def execute_replay(**_: object) -> dict:
        nonlocal calls
        calls += 1
        return _fake_replay(
            300 + calls,
            peak_rss=600 * 1024 * 1024,
        )

    output = tmp_path / "result.json"
    receipt = tmp_path / "receipt.json"
    result = rehearsal._run_with_dependencies(
        output,
        receipt,
        root=ROOT,
        proof=_proof(),
        execute_replay=execute_replay,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )

    assert calls == 1
    assert result["route"] == "FS2_PARK"
    assert result["failure_family"] == "FS2-resource_or_monitor_failure"
    core.assert_target_free(result)


def test_symlink_or_existing_destination_refuses_without_execution(tmp_path: Path) -> None:
    target = tmp_path / "elsewhere.json"
    target.write_text("untouched", encoding="utf-8")
    output = tmp_path / "result.json"
    output.symlink_to(target)
    receipt = tmp_path / "receipt.json"
    called = False

    def execute_replay(**_: object) -> dict:
        nonlocal called
        called = True
        return _fake_replay(1)

    with pytest.raises(core.CommP0GeneratedRefusal, match="duplicate_or_missing"):
        rehearsal._run_with_dependencies(
            output,
            receipt,
            root=ROOT,
            proof=_proof(),
            execute_replay=execute_replay,
            free_disk_bytes=_free_disk_bytes,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
        )
    assert called is False
    assert target.read_text(encoding="utf-8") == "untouched"
    assert not receipt.exists()


def test_free_space_refuses_before_receipt_or_child(tmp_path: Path) -> None:
    called = False

    def execute_replay(**_: object) -> dict:
        nonlocal called
        called = True
        return _fake_replay(1)

    with pytest.raises(core.CommP0GeneratedRefusal, match="free_space_preflight"):
        rehearsal._run_with_dependencies(
            tmp_path / "result.json",
            tmp_path / "receipt.json",
            root=ROOT,
            proof=_proof(),
            execute_replay=execute_replay,
            free_disk_bytes=lambda _: 19 * 1024**3,
            reserve_disk=_small_reservation,
            resize_reservation=_small_resize,
            monotonic=_clock(),
            time_ns=lambda: 123,
        )
    assert called is False
    assert list(tmp_path.iterdir()) == []


def test_reservation_failure_consumes_receipt_before_payload_work(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    receipt = tmp_path / "receipt.json"
    called = False

    def reserve_disk(_: Path, __: int) -> None:
        assert receipt.exists()
        raise OSError("fixture reservation failure")

    def execute_replay(**_: object) -> dict:
        nonlocal called
        called = True
        return _fake_replay(1)

    result = rehearsal._run_with_dependencies(
        output,
        receipt,
        root=ROOT,
        proof=_proof(),
        execute_replay=execute_replay,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=reserve_disk,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )

    assert result["route"] == "FS2_PARK"
    assert result["attempt_consumed"] is True
    assert result["completed_replay_children"] == 0
    assert receipt.exists()
    assert called is False


def test_children_share_one_absolute_deadline_and_avoid_official_capability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    deadlines: list[float] = []
    pids = iter((401, 402))

    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("official qualification capability was touched")

    monkeypatch.setattr(qualification, "load_and_validate_activation", forbidden)
    monkeypatch.setattr(qualification, "create_consumed_marker", forbidden)
    monkeypatch.setattr(qualification, "run_official_qualification", forbidden)

    def execute_replay(**kwargs: object) -> dict:
        deadlines.append(float(kwargs["absolute_deadline"]))
        return _fake_replay(next(pids))

    result = rehearsal._run_with_dependencies(
        tmp_path / "result.json",
        tmp_path / "receipt.json",
        root=ROOT,
        proof=_proof(),
        execute_replay=execute_replay,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )

    assert result["route"] == "FS2_PASS"
    assert deadlines == [180.0, 180.0]


@pytest.mark.parametrize("escape_kind", ["symlink", "hardlink"])
def test_owned_tree_cleanup_refuses_escape_inodes(
    tmp_path: Path, escape_kind: str
) -> None:
    external = tmp_path / "external.txt"
    external.write_text("untouched", encoding="utf-8")
    owned = tmp_path / "owned"
    owned.mkdir()
    candidate = owned / "candidate"
    if escape_kind == "symlink":
        candidate.symlink_to(external)
    else:
        os.link(external, candidate)

    with pytest.raises(core.CommP0GeneratedRefusal, match="publication_collision"):
        rehearsal._remove_owned_tree(owned)

    assert external.read_text(encoding="utf-8") == "untouched"


def test_socket_guard_blocks_network_calls_in_child(tmp_path: Path) -> None:
    guard_root = rehearsal._write_socket_guard(tmp_path)
    environment = dict(os.environ)
    environment["NDK_FS2_GUARD_DIR"] = str(guard_root)
    environment["PYTHONPATH"] = os.pathsep.join((str(guard_root), str(ROOT / "src")))
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import socket\n"
                "try:\n"
                "    socket.getaddrinfo('example.com', 443)\n"
                "except RuntimeError as exc:\n"
                "    assert 'FS2-forbidden_operation_nonzero' in str(exc)\n"
                "else:\n"
                "    raise SystemExit(3)\n"
            ),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    rehearsal._remove_owned_tree(guard_root)


def test_inspector_refuses_extra_public_output_key(tmp_path: Path) -> None:
    pids = iter((501, 502))
    output = tmp_path / "result.json"
    result = rehearsal._run_with_dependencies(
        output,
        tmp_path / "receipt.json",
        root=ROOT,
        proof=_proof(),
        execute_replay=lambda **_: _fake_replay(next(pids)),
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_small_reservation,
        resize_reservation=_small_resize,
        monotonic=_clock(),
        time_ns=lambda: 123,
    )
    result["participant_predictions"] = []
    malformed = tmp_path / "malformed.json"
    malformed.write_text(json.dumps(result), encoding="utf-8")

    with pytest.raises(core.CommP0GeneratedRefusal, match="publication_collision"):
        rehearsal.inspect_result(malformed)


def test_cli_help_plan_and_fail_closed_run(tmp_path: Path) -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "src")
    help_run = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_rehearsal_cli", "--help"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    plan_run = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_rehearsal_cli", "plan"],
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
            "neurodecodekit.comm_p0_rehearsal_cli",
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
    assert "implementation_proof_absent" in closed_run.stdout
    assert list(tmp_path.iterdir()) == []
