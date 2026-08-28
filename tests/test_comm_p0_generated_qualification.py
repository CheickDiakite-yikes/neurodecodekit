from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification

ROOT = Path(__file__).resolve().parents[1]
HAS_CLASSICAL = (
    importlib.util.find_spec("numpy") is not None
    and importlib.util.find_spec("sklearn") is not None
)


def _activation(root: Path, artifact_path: str) -> dict[str, object]:
    artifact = qualification._file_artifact(root, artifact_path)
    value: dict[str, object] = {
        "schema_name": qualification.ACTIVATION_SCHEMA,
        "schema_version": qualification.SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "contract_sha256": core.CONTRACT_SHA256,
        "generated_qualification_execution_authorized": True,
        "implementation_commit_remotely_green": True,
        "implementation_base_python_job_green": True,
        "implementation_optional_neuro_readers_job_green": True,
        "activation_commit_remotely_green": True,
        "activation_base_python_job_green": True,
        "activation_optional_neuro_readers_job_green": True,
        "single_official_invocation": True,
        "network_during_invocation_allowed_false": True,
        "implementation_commit": "1" * 40,
        "activation_commit": "2" * 40,
        "implementation_CI_run_id": 1,
        "implementation_base_python_job_id": 2,
        "implementation_optional_neuro_readers_job_id": 3,
        "activation_CI_run_id": 4,
        "activation_base_python_job_id": 5,
        "activation_optional_neuro_readers_job_id": 6,
        "implementation_artifacts": [artifact],
        "implementation_artifact_set_sha256": core.sha256_json([artifact]),
    }
    value["activation_proof_sha256"] = core.sha256_json(value)
    return value


def _fake_fold_executor(**values: object) -> qualification.ProcessMeasurement:
    feature_path = Path(values["feature_path"])
    label_path = Path(values["label_path"])
    output_path = Path(values["output_path"])
    held_out = str(values["held_out"])
    byte_cap = int(values["byte_cap"])
    features = [json.loads(line) for line in feature_path.read_text().splitlines()]
    labels = [json.loads(line) for line in label_path.read_text().splitlines()]
    if any(row["participant_id"] == held_out for row in labels):
        raise AssertionError("held-out labels crossed the model boundary")
    held = [row for row in features if row["participant_id"] == held_out]
    contract_path = Path(values["contract_path"])
    contract = json.loads(contract_path.read_text())
    rows: list[dict[str, object]] = [
        {
            "record_type": "fold_header",
            "schema_name": "neurodecodekit.comm_p0_generated_model_worker",
            "schema_version": "0.1.0",
            "gate_id": core.GATE_ID,
            "cohort_id": held[0]["cohort_id"],
            "held_out_participant": held_out,
            "source_participants": len({row["participant_id"] for row in labels}),
            "held_out_labels_received": 0,
            "trial_plan_objects_received": 0,
            "target_vault_capabilities_received": 0,
        }
    ]
    for condition in contract["conditions"]:
        for feature in held:
            command = max(range(4), key=lambda index: feature["central"][index])
            probabilities = [0.05, 0.05, 0.05, 0.05]
            probabilities[command] = 0.85
            rows.append(
                {
                    "record_type": "prediction",
                    "item_id": feature["item_id"],
                    "cohort_id": feature["cohort_id"],
                    "participant_id": feature["participant_id"],
                    "endpoint": feature["endpoint"],
                    "phase": feature["phase"],
                    "condition": condition,
                    "probabilities": probabilities,
                }
            )
    prediction_count = len(rows) - 1
    rows.append(
        {
            "record_type": "fold_ledger",
            "schema_name": "neurodecodekit.comm_p0_generated_model_worker",
            "held_out_participant": held_out,
            "prior_fits": 1,
            "residualizer_fits": 2,
            "classifier_fits": 15,
            "temperature_calibration_fits": 15,
            "model_inference_runs": 17,
            "prediction_sets": 34,
            "prediction_rows": prediction_count,
            "target_deliveries": 0,
            "scores": 0,
            "post_target_updates": 0,
        }
    )
    qualification.create_no_replace_file(
        output_path,
        b"".join(core.canonical_json_bytes(row) for row in rows),
        byte_cap=byte_cap,
    )
    return qualification.ProcessMeasurement(0.01, 1024, 1)


class CommP0GeneratedQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = core.load_contract(ROOT)

    def test_official_entry_is_activation_locked_before_marker_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "consumed.json"
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal, "score_before_exact_green_freeze"
            ):
                qualification.run_official_qualification(
                    Path(temporary) / "result.json",
                    consumed_marker=marker,
                    root=ROOT,
                )
            self.assertFalse(marker.exists())
            self.assertFalse(qualification.OFFICIAL_IMPLEMENTATION_ACTIVATED)

    def test_future_activated_entry_consumes_marker_before_any_work(self) -> None:
        activation = {"activation": "generated-test-only"}
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "consumed.json"
            with (
                mock.patch.object(qualification, "OFFICIAL_IMPLEMENTATION_ACTIVATED", True),
                mock.patch.object(
                    qualification,
                    "load_and_validate_activation",
                    return_value=activation,
                ),
                self.assertRaisesRegex(
                    core.CommP0GeneratedRefusal,
                    "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
                ),
            ):
                qualification.run_official_qualification(
                    Path(temporary) / "result.json",
                    consumed_marker=marker,
                    root=ROOT,
                )
            self.assertTrue(marker.is_file())
            record = json.loads(marker.read_bytes())
            self.assertEqual(record["activation_sha256"], core.sha256_json(activation))

    def test_activation_binding_is_offline_exact_and_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact_path = "implementation.py"
            (root / artifact_path).write_text("value = 1\n", encoding="utf-8")
            activation = _activation(root, artifact_path)
            self.assertEqual(
                qualification.validate_activation_binding(activation, root=root),
                activation,
            )
            tampered = copy.deepcopy(activation)
            tampered["implementation_artifacts"][0]["sha256"] = "0" * 64
            tampered["activation_proof_sha256"] = core.sha256_json(
                {key: value for key, value in tampered.items() if key != "activation_proof_sha256"}
            )
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
            ):
                qualification.validate_activation_binding(tampered, root=root)

    def test_consumed_marker_is_durable_no_replace_and_symlink_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / "consumed.json"
            identity = qualification.create_consumed_marker(
                marker,
                invocation_nonce="nonce",
                activation_sha256="a" * 64,
            )
            self.assertEqual(identity.size_bytes, marker.stat().st_size)
            self.assertEqual(marker.stat().st_nlink, 1)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "post_score_mutation_repeat_or_output_replacement",
            ):
                qualification.create_consumed_marker(
                    marker,
                    invocation_nonce="nonce",
                    activation_sha256="a" * 64,
                )
            target = root / "target"
            target.write_text("protected", encoding="utf-8")
            link = root / "link"
            link.symlink_to(target)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "post_score_mutation_repeat_or_output_replacement",
            ):
                qualification.create_consumed_marker(
                    link,
                    invocation_nonce="nonce",
                    activation_sha256="a" * 64,
                )
            self.assertEqual(target.read_text(), "protected")

    def test_read_refuses_symlinked_parent_and_child_home_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual = root / "actual"
            actual.mkdir()
            (actual / "payload.json").write_text("{}", encoding="utf-8")
            linked = root / "linked"
            linked.symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "filesystem_capability_publication_or_cleanup_escape",
            ):
                qualification.read_no_follow(
                    linked / "payload.json",
                    byte_cap=128,
                )
            environment = qualification._sanitized_child_environment(root, ROOT)
            self.assertEqual(environment["HOME"], str(root / "home"))
            self.assertTrue((root / "home").is_dir())
            self.assertNotEqual(environment["HOME"], str(Path.home()))

    def test_prediction_stream_is_canonical_bounded_and_one_link(self) -> None:
        records = []
        for index in range(300):
            records.append(
                {
                    "record_type": "prediction",
                    "item_id": f"opaque-{index:03d}",
                    "cohort_id": "discovery",
                    "participant_id": f"P-{index // 100}",
                    "endpoint": core.ENDPOINTS[index % 2],
                    "phase": "shadow",
                    "condition": f"condition-{index % 3}",
                    "probabilities": [0.25, 0.25, 0.25, 0.25],
                }
            )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "predictions.ndjson"
            identity, inventory = qualification.write_prediction_stream(
                path, records, byte_cap=1_000_000, maximum_rows_buffered=256
            )
            self.assertEqual(inventory.rows, 300)
            self.assertEqual(identity.size_bytes, path.stat().st_size)
            self.assertEqual(path.stat().st_nlink, 1)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal, "private_derivative_cap_breach"
            ):
                qualification.write_prediction_stream(
                    Path(temporary) / "too-large.ndjson",
                    records,
                    byte_cap=100,
                )
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal, "private_derivative_cap_breach"
            ):
                qualification.write_prediction_stream(
                    Path(temporary) / "too-buffered.ndjson",
                    records,
                    byte_cap=1_000_000,
                    maximum_rows_buffered=257,
                )

    def test_fold_assembler_never_materializes_complete_prediction_payload(self) -> None:
        participant = "P-stream-01"
        item_ids = ("opaque-a", "opaque-b")
        records: list[dict[str, object]] = [
            {
                "record_type": "fold_header",
                "cohort_id": "discovery",
                "held_out_participant": participant,
                "held_out_labels_received": 0,
                "trial_plan_objects_received": 0,
                "target_vault_capabilities_received": 0,
            }
        ]
        for condition in self.contract["conditions"]:
            for index, item_id in enumerate(item_ids):
                records.append(
                    {
                        "record_type": "prediction",
                        "item_id": item_id,
                        "cohort_id": "discovery",
                        "participant_id": participant,
                        "endpoint": core.ENDPOINTS[index],
                        "phase": "shadow",
                        "condition": condition,
                        "probabilities": [0.25, 0.25, 0.25, 0.25],
                    }
                )
        prediction_rows = len(records) - 1
        records.append(
            {
                "record_type": "fold_ledger",
                "held_out_participant": participant,
                "prior_fits": 1,
                "residualizer_fits": 2,
                "classifier_fits": 15,
                "temperature_calibration_fits": 15,
                "model_inference_runs": 17,
                "prediction_sets": 34,
                "prediction_rows": prediction_rows,
                "target_deliveries": 0,
                "scores": 0,
                "post_target_updates": 0,
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fold_path = root / "fold.ndjson"
            fold_path.write_bytes(b"".join(core.canonical_json_bytes(record) for record in records))
            output_path = root / "predictions.ndjson"
            assembler = qualification.PredictionStreamAssembler(
                output_path,
                byte_cap=1_000_000,
                maximum_rows_buffered=256,
            )
            ledger = assembler.append_fold(
                fold_path,
                expected_cohort="discovery",
                expected_participant=participant,
                expected_items=item_ids,
                contract=self.contract,
            )
            with mock.patch.object(
                qualification,
                "read_no_follow",
                side_effect=AssertionError("whole-payload reader used"),
            ):
                identity, inventory = assembler.finalize()
            self.assertEqual(ledger["prediction_rows"], prediction_rows)
            self.assertEqual(inventory.rows, prediction_rows)
            self.assertEqual(
                identity, qualification._hash_no_follow(output_path, byte_cap=1_000_000)
            )
            self.assertEqual(assembler.maximum_rows_observed, 1)
            self.assertLessEqual(assembler.maximum_rows_observed, 256)

    def test_hmac_tamper_refuses_before_target_descriptor_open(self) -> None:
        prediction = {
            "record_type": "prediction",
            "item_id": "opaque",
            "cohort_id": "discovery",
            "participant_id": "P-1",
            "endpoint": "free_choice_intend",
            "phase": "shadow",
            "condition": "equal_prior",
            "probabilities": [0.25, 0.25, 0.25, 0.25],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prediction_path = root / "predictions.ndjson"
            identity, inventory = qualification.write_prediction_stream(
                prediction_path, [prediction], byte_cap=4096
            )
            target_path = root / "targets.json"
            target_path.write_text('{"opaque":0}', encoding="utf-8")
            key = b"freeze-key-at-least-thirty-two-bytes"
            freeze = qualification.build_hmac_freeze_attestation(
                identity=identity,
                inventory=inventory,
                invocation_nonce="nonce",
                contract_sha256=core.CONTRACT_SHA256,
                implementation_hashes={"coordinator": "1" * 64},
                split_sha256="2" * 64,
                capability_sha256="3" * 64,
                schedule_sha256="4" * 64,
                key=key,
            )
            freeze["prediction_file"]["sha256"] = "0" * 64
            opened = []
            original = qualification.read_no_follow

            def tracked(path: str | Path, *, byte_cap: int):
                opened.append(Path(path))
                return original(path, byte_cap=byte_cap)

            with (
                mock.patch.object(qualification, "read_no_follow", side_effect=tracked),
                self.assertRaisesRegex(
                    core.CommP0GeneratedRefusal,
                    "prediction_row_or_probability_tamper_after_freeze",
                ),
            ):
                qualification._score_transaction(
                    contract=self.contract,
                    trial_records=[],
                    prediction_path=prediction_path,
                    target_path=target_path,
                    freeze_attestation=freeze,
                    freeze_key=key,
                    byte_cap=4096,
                )
            self.assertNotIn(target_path, opened)

    def test_process_monitor_failure_and_absolute_deadline_refuse(self) -> None:
        environment = dict(os.environ)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def failed_monitor(pid: int) -> int:
                del pid
                raise RuntimeError("monitor unavailable")

            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "total_permission_or_free_space_floor_breach",
            ):
                qualification.run_monitored_command(
                    [sys.executable, "-c", "import time; time.sleep(1)"],
                    pass_fds=(),
                    environment=environment,
                    cwd=root,
                    deadline_monotonic=time.monotonic() + 2,
                    rss_cap_bytes=1_000_000_000,
                    monitor=failed_monitor,
                )
            with self.assertRaisesRegex(core.CommP0GeneratedRefusal, "temporary_output_cap_breach"):
                qualification.run_monitored_command(
                    [sys.executable, "-c", "import time; time.sleep(1)"],
                    pass_fds=(),
                    environment=environment,
                    cwd=root,
                    deadline_monotonic=time.monotonic() - 1,
                    rss_cap_bytes=1_000_000_000,
                    monitor=lambda pid: 1,
                )

    def test_domain_refusals_and_shortcut_routes_are_exact(self) -> None:
        observations = qualification.domain_refusals.exercise_domain_refusals(self.contract)
        self.assertEqual(len(observations), 70)
        qualification.domain_refusals.validate_observations(observations, self.contract)
        shortcuts = qualification.shortcut_fixture_accounting()
        self.assertEqual(
            tuple(row["fixture"] for row in shortcuts), qualification.SHORTCUT_FIXTURES
        )
        self.assertTrue(shortcuts[0]["neural_evidence_gate_pass"])
        self.assertTrue(all(not row["neural_evidence_gate_pass"] for row in shortcuts[1:]))
        self.assertTrue(all(not row["scientific_value"] for row in shortcuts))

    @unittest.skipUnless(HAS_CLASSICAL, "requires optional classical stack")
    def test_reduced_two_replay_path_is_deterministic_and_target_firewalled(self) -> None:
        result = qualification.run_development_replay_pair(
            root=ROOT,
            participants_per_cohort=3,
            timeout_seconds=90,
            execute_fold=_fake_fold_executor,
            score_monitor=lambda pid: 1024,
        )
        self.assertFalse(result["official_qualification"])
        self.assertEqual(result["isolated_child_process_replays"], 2)
        self.assertTrue(result["replay_equivalent"])
        self.assertEqual(result["shortcut_fixture_accounting_records_per_replay"], 7)
        self.assertEqual(result["numerical_shortcut_fixture_executions_per_replay"], 7)
        self.assertEqual(result["shortcut_prediction_rows_per_replay"], 91_392)
        self.assertEqual(result["shortcut_target_deliveries_per_replay"], 14)
        self.assertEqual(result["shortcut_scores_per_replay"], 14)
        self.assertEqual(result["refusal_observations"], 140)
        self.assertEqual(result["target_deliveries"], 2)
        self.assertEqual(result["scores"], 2)
        self.assertEqual(result["post_target_updates"], 0)
        self.assertEqual(result["network_bytes"], 0)
        self.assertEqual(result["real_or_private_reads"], 0)
        self.assertEqual(result["device_operations"], 0)
        self.assertEqual(result["retained_generated_payload_bytes_after_proof"], 0)
        self.assertFalse(result["end_to_end_latency_measured"])
        self.assertEqual(result["prediction_transport_write_batch_rows_maximum"], 1)
        self.assertFalse(result["complete_prediction_records_materialized_for_development_scoring"])
        self.assertEqual(
            result["remaining_activation_blockers"],
            [
                "separate exact-green activation before one official generated "
                "qualification"
            ],
        )
        self.assertGreater(result["mandatory_process_monitor_samples"], 0)
        core.assert_target_free(result)

    def test_replay_mismatch_and_public_output_cap_refuse(self) -> None:
        first = {"canonical_surface": {"value": 1}}
        second = {"canonical_surface": {"value": 2}}
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "nondeterministic_fixture_prediction_or_freeze_replay",
        ):
            if first["canonical_surface"] != second["canonical_surface"]:
                qualification._refuse("nondeterministic_fixture_prediction_or_freeze_replay")
        oversized = {
            "warning": "x" * (self.contract["resource_caps"]["public_aggregate_output_bytes"] + 1)
        }
        self.assertGreater(
            len(core.canonical_json_bytes(oversized)),
            self.contract["resource_caps"]["public_aggregate_output_bytes"],
        )
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(core.CommP0GeneratedRefusal, "temporary_output_cap_breach"),
        ):
            qualification.create_no_replace_file(
                Path(temporary) / "oversized.json",
                core.canonical_json_bytes(oversized),
                byte_cap=self.contract["resource_caps"]["public_aggregate_output_bytes"],
            )


if __name__ == "__main__":
    unittest.main()
