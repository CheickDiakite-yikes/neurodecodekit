from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.experiments import iackd_role_aware_dual_reversal as core
from neurodecodekit.experiments import iackd_transport_stable_dual_reversal_real as real


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in real.THREAD_ENV_KEYS}


def _has_exact_stack() -> bool:
    try:
        real.dependency_versions()
    except (Exception, SystemExit):
        return False
    return True


HAS_EXACT_STACK = _has_exact_stack()


class IACKD2RealBaseTests(unittest.TestCase):
    def test_plan_binds_green_decision_without_real_operation(self) -> None:
        plan = real.registered_plan(ROOT)
        self.assertEqual(plan["decision_commit"], real.DECISION_COMMIT)
        self.assertEqual(plan["decision_CI_run_id"], real.DECISION_CI_RUN_ID)
        self.assertEqual(plan["object_count"], 1_340)
        self.assertEqual(plan["payload_bytes"], 7_249_113_684)
        self.assertEqual(plan["fits"], 660)
        self.assertEqual(plan["prediction_sets"], 900)
        self.assertEqual(plan["real_or_public_operations"], 0)
        self.assertEqual(plan["old_retained_bundle_operations"], 0)
        self.assertFalse(plan["scientific_claim"])

    def test_decision_and_inventory_hashes_are_exact(self) -> None:
        decision = real.load_registered_decision(ROOT)
        inventory = real.load_registered_inventory(ROOT)
        self.assertEqual(
            decision["user_authorization"]["actual_message_verbatim"],
            "continue",
        )
        self.assertEqual(len(inventory["selected_objects"]), 1_340)
        self.assertEqual(
            inventory["selection"]["selected_payload_bytes"],
            7_249_113_684,
        )

    def test_default_cli_is_dry_run_and_has_no_bundle_argument(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(real.main([]), 0)
        plan = json.loads(output.getvalue())
        self.assertIn("dry_run", plan["mode"])
        parser = real.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        self.assertNotIn("--bundle", option_strings)
        self.assertNotIn("--old-bundle", option_strings)

    def test_output_preflight_and_writer_fail_closed(self) -> None:
        regular_temp_root = Path(tempfile.gettempdir()).resolve()
        with tempfile.TemporaryDirectory(dir=regular_temp_root) as temporary:
            root = Path(temporary)
            candidate = root / "new.json"
            real._qualification_output_preflight(candidate, 1024)
            candidate.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F07"):
                real._qualification_output_preflight(candidate, 1024)
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F14"):
                real._qualification_output_preflight(root / "next.json", 0)
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F14"):
                real._write_exclusive(root / "large.bin", b"12", 1)
            self.assertFalse((root / "large.bin").exists())

    def test_response_guards_refuse_status_redirect_size_etag_and_encoding(self) -> None:
        body = b"fixture"
        url = "https://fixture.invalid/object"
        etag = hashlib.md5(body, usedforsecurity=False).hexdigest()  # noqa: S324
        valid = real.FixtureResponse(body=body, url=url, etag=etag)
        real._validate_response(
            valid,
            url=url,
            expected_bytes=len(body),
            expected_etag=etag,
        )
        cases = (
            real.FixtureResponse(body=body, url=url, etag=etag, status=500),
            real.FixtureResponse(body=body, url=f"{url}/redirect", etag=etag),
            real.FixtureResponse(body=body, url=url, etag="0" * 32),
            real.FixtureResponse(body=body, url=url, etag=etag, content_encoding="gzip"),
        )
        for response in cases:
            with self.subTest(response=response):
                with self.assertRaises(real.RealDualReversalRefusal):
                    real._validate_response(
                        response,
                        url=url,
                        expected_bytes=len(body),
                        expected_etag=etag,
                    )

    def test_metadata_transport_accepts_registered_framing_profiles(self) -> None:
        body = b'{"fixture":"metadata"}'
        url = "https://fixture.invalid/metadata"
        sha256 = hashlib.sha256(body).hexdigest()
        cases = (
            ("exact", None, "fixed_length", "exact"),
            (str(len(body) + 1), None, "fixed_length", "different"),
            (None, "chunked", "chunked", "unavailable"),
            (None, None, "close_delimited", "unavailable"),
        )
        for ordinal, (length, transfer, framing, length_state) in enumerate(cases):
            with self.subTest(framing=framing, length_state=length_state):
                validation, parsed = real._transport_stable_metadata_response(
                    real.FixtureResponse(
                        body=body,
                        url=url,
                        etag="fixture",
                        content_length=length,
                        transfer_encoding=transfer,
                    ),
                    url=url,
                    expected_bytes=len(body),
                    expected_sha256=sha256,
                    parser=json.loads,
                    ordinal=ordinal,
                )
                self.assertEqual(validation.framing_profile, framing)
                self.assertEqual(validation.content_length_state, length_state)
                self.assertEqual(
                    (validation.read_calls, validation.hash_calls, validation.parse_calls),
                    (1, 1, 1),
                )
                self.assertEqual(parsed, {"fixture": "metadata"})

    def test_metadata_transport_refuses_ambiguity_and_hash_drift(self) -> None:
        body = b'{"fixture":"metadata"}'
        url = "https://fixture.invalid/metadata"
        cases = (
            (
                real.FixtureResponse(
                    body=body,
                    url=url,
                    etag="fixture",
                    transfer_encoding="chunked",
                ),
                hashlib.sha256(body).hexdigest(),
            ),
            (
                real.FixtureResponse(
                    body=body,
                    url=url,
                    etag="fixture",
                    content_length=None,
                ),
                "0" * 64,
            ),
        )
        for ordinal, (response, sha256) in enumerate(cases):
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F05"):
                real._transport_stable_metadata_response(
                    response,
                    url=url,
                    expected_bytes=len(body),
                    expected_sha256=sha256,
                    parser=json.loads,
                    ordinal=ordinal,
                )

    def test_machine_safety_is_measured_and_fails_closed(self) -> None:
        safe = real.preconsumption_machine_safety(
            ROOT,
            environ=THREAD_ENV,
            disk_usage_reader=lambda _: real._DiskUsageFixture(
                free=real.MINIMUM_FREE_DISK_BYTES + 1
            ),
            cpu_count_reader=lambda: 8,
            loadavg_reader=lambda: (4.0, 0.0, 0.0),
        )
        self.assertTrue(safe["passed_before_consumed_marker"])
        self.assertEqual(safe["one_minute_load_per_logical_CPU"], 0.5)
        failures = (
            {
                "disk_usage_reader": lambda _: real._DiskUsageFixture(
                    free=real.MINIMUM_FREE_DISK_BYTES - 1
                ),
                "cpu_count_reader": lambda: 8,
                "loadavg_reader": lambda: (1.0, 0.0, 0.0),
            },
            {
                "disk_usage_reader": lambda _: real._DiskUsageFixture(
                    free=real.MINIMUM_FREE_DISK_BYTES + 1
                ),
                "cpu_count_reader": lambda: 2,
                "loadavg_reader": lambda: (2.1, 0.0, 0.0),
            },
            {
                "disk_usage_reader": lambda _: real._DiskUsageFixture(
                    free=real.MINIMUM_FREE_DISK_BYTES + 1
                ),
                "cpu_count_reader": lambda: 2,
                "loadavg_reader": mock.Mock(side_effect=OSError("unavailable")),
            },
        )
        for readers in failures:
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F03"):
                real.preconsumption_machine_safety(
                    ROOT,
                    environ=THREAD_ENV,
                    **readers,
                )

    def test_real_wrapper_refuses_before_stream_when_machine_gate_fails(self) -> None:
        contract = real.load_registered_contract(ROOT)
        inventory = real.load_registered_inventory(ROOT)
        evidence = real.ImplementationEvidence("a" * 40, 1, 2, 3)
        with (
            mock.patch.object(real, "load_registered_contract", return_value=contract),
            mock.patch.object(real, "load_registered_decision", return_value={}),
            mock.patch.object(real, "load_registered_inventory", return_value=inventory),
            mock.patch.object(real, "_validate_implementation_registry", return_value={}),
            mock.patch.object(
                real,
                "preconsumption_machine_safety",
                side_effect=real.RealDualReversalRefusal(real.REFUSAL_IDS[2], "sentinel"),
            ),
            mock.patch.object(real, "run_streaming_derivative_build") as stream,
            self.assertRaisesRegex(real.RealDualReversalRefusal, "sentinel"),
        ):
            real.run_registered_streaming_execution(
                repo_root=ROOT,
                evidence=evidence,
                environ=THREAD_ENV,
            )
        stream.assert_not_called()

    def test_additive_module_has_no_consumed_executor_or_old_root_interface(self) -> None:
        source = Path(real.__file__).read_text(encoding="utf-8")
        self.assertNotIn("iackd_role_aware_dual_reversal_real", source)
        self.assertNotIn(
            ".codex_work/iackd_role_aware_dual_reversal/real_execution_v0",
            source,
        )

    def test_geometry_accepts_only_complete_explicit_unavailability(self) -> None:
        coordinate = b'{"EEGCoordinateSystem":"CapTrak","EEGCoordinateUnits":"m"}'
        valid = b"name\tx\ty\tz\nC3\t0.1\t0.2\t0.3\nHEOG\tn/a\tn/a\tn/a\n"
        parsed = real._parse_geometry_pair(valid, coordinate)
        self.assertEqual(parsed, {"c3": (0.1, 0.2, 0.3)})
        partial = b"name\tx\ty\tz\nC3\t0.1\tn/a\t0.3\n"
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F09"):
            real._parse_geometry_pair(partial, coordinate)

    def test_cleanup_removes_only_an_invocation_created_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invocation = root / "invocation"
            invocation.mkdir()
            group = invocation / "group"
            group.mkdir()
            (group / "payload.bin").write_bytes(b"fixture")
            outside = root / "outside.bin"
            outside.write_bytes(b"keep")
            real._remove_invocation_group(invocation, group)
            self.assertFalse(group.exists())
            self.assertEqual(outside.read_bytes(), b"keep")
            with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F17"):
                real._remove_invocation_group(invocation, root)

    def test_analysis_marks_consumed_before_model_cache_read(self) -> None:
        contract = real.load_registered_contract(ROOT)
        receipt = {
            "contract_sha256": real.CONTRACT_SHA256,
            "decision_sha256": real.DECISION_SHA256,
            "implementation_commit": "a" * 40,
            "measurements": {
                "payload_requests": 1_340,
                "payload_bytes": 7_249_113_684,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / real.PRIVATE_ROOT_RELATIVE_PATH
            private.mkdir(parents=True)

            def stop_at_model_read(**_kwargs):
                marker = private / "analysis_consumed.v0.json"
                self.assertTrue(marker.is_file())
                raise real.RealDualReversalFailure(real.REFUSAL_IDS[12], "sentinel")

            evidence = real.ImplementationEvidence("a" * 40, 1, 2, 3)
            with (
                mock.patch.object(real, "load_registered_contract", return_value=contract),
                mock.patch.object(real, "load_registered_decision", return_value={}),
                mock.patch.object(real, "_validate_implementation_registry", return_value={}),
                mock.patch.object(real, "_tracked_at_head", return_value=True),
                mock.patch.object(real, "_load_public_receipt", return_value=receipt),
                mock.patch.object(
                    real,
                    "load_target_free_model_stage",
                    side_effect=stop_at_model_read,
                ),
                self.assertRaisesRegex(real.RealDualReversalFailure, "sentinel"),
            ):
                real.run_registered_target_blind_analysis(
                    repo_root=root,
                    evidence=evidence,
                    environ=THREAD_ENV,
                )

    def test_public_freeze_and_result_reject_extra_fields(self) -> None:
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F15"):
            real.validate_public_freeze(
                {
                    "schema_name": "neurodecodekit.iackd2r_prediction_freeze",
                    "unexpected_target_values": [0, 1],
                }
            )
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F18"):
            real.validate_public_result(
                {
                    "schema_name": "neurodecodekit.iackd2r_result",
                    "individual_prediction": [0, 1],
                }
            )


@unittest.skipUnless(HAS_EXACT_STACK, "requires exact NumPy SciPy MNE sklearn stack")
class IACKD2RealExactStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="iackd2-real-tests-")
        cls.root = Path(cls.temporary.name)
        cls.contract = real.load_registered_contract(ROOT)
        fixture_contract, fixture_inventory, cls.opener = (
            real._mock_contract_inventory_transport()
        )
        cls.receipt = real.run_streaming_derivative_build(
            workspace_root=cls.root,
            contract=fixture_contract,
            inventory=fixture_inventory,
            opener=cls.opener,
            environ=THREAD_ENV,
            private_root_relative="private",
            public_receipt_relative="receipt.json",
            strict_registered=False,
            implementation_commit="fixture",
        )
        generated = core.build_generated_derivatives(ROOT)
        cls.model_stage = generated["model_stage"]
        cls.scorer_stage = {**generated["scorer_stage"], "sealed_shard_reads": 0}
        cls.matrix = real.run_target_blind_model_matrix(
            cls.model_stage,
            contract=cls.contract,
        )
        cls.replay = real.run_target_blind_model_matrix(
            cls.model_stage,
            contract=cls.contract,
        )
        cls.prediction_payload = real._private_prediction_bytes(
            cls.matrix,
            model_stage=cls.model_stage,
            contract=cls.contract,
        )
        cls.prediction_path = cls.root / "predictions.npz"
        cls.prediction_path.write_bytes(cls.prediction_payload)
        cls.replayed_matrix = real._load_private_predictions(
            cls.prediction_path,
            expected_sha256=hashlib.sha256(cls.prediction_payload).hexdigest(),
            maximum_bytes=8 * 1024 * 1024,
            model_stage=cls.model_stage,
            contract=cls.contract,
        )
        physiology = real.load_target_free_physiology_summary(
            private_root=cls.root / "private",
            contract=cls.contract,
            expected_shards=2,
        )
        manifest_payload = (
            cls.root / "private" / "private_derivative_manifest.v0.json"
        ).read_bytes()
        manifest = json.loads(manifest_payload)
        provenance = {
            "private_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
            "source_binding_set_sha256": real._canonical_sha256(
                sorted(row["source_binding_sha256"] for row in manifest["run_summaries"])
            ),
            "source_hash_set_sha256": cls.receipt["derivatives"][
                "source_hash_set_sha256"
            ],
            "derivative_set_sha256": cls.receipt["derivatives"][
                "derivative_set_sha256"
            ],
        }
        cls.freeze = real.build_prediction_freeze(
            source_kind="generated_fixture",
            matrix=cls.replayed_matrix,
            model_stage=cls.model_stage,
            contract=cls.contract,
            implementation_commit="fixture",
            acquisition_receipt_sha256=hashlib.sha256(
                (cls.root / "receipt.json").read_bytes()
            ).hexdigest(),
            provenance=provenance,
            physiology_summary=physiology,
            private_prediction_payload_sha256=hashlib.sha256(
                cls.prediction_payload
            ).hexdigest(),
            measurements={
                "producer_is_causal_in_samples": True,
                "end_to_end_latency_measured": False,
            },
            access_counters={},
        )
        cls.score = real.score_frozen_matrix(
            matrix=cls.replayed_matrix,
            model_stage=cls.model_stage,
            scorer_stage=cls.scorer_stage,
            freeze=cls.freeze,
            contract=cls.contract,
        )
        cls.qualification_path = cls.root / "qualification.json"
        cls.qualification = real.run_generated_real_executor_qualification(
            cls.qualification_path,
            environ=THREAD_ENV,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_mocked_stream_is_balanced_causal_and_storage_bounded(self) -> None:
        self.assertEqual(self.receipt["measurements"]["payload_requests"], 22)
        self.assertEqual(self.receipt["measurements"]["run_groups"], 2)
        self.assertEqual(self.receipt["measurements"]["retained_source_trials"], 8)
        self.assertEqual(self.receipt["measurements"]["peak_concurrent_raw_run_groups"], 1)
        self.assertEqual(
            self.receipt["derivatives"]["minimum_fit_rows_per_class_per_unit_arm"],
            1,
        )
        self.assertEqual(
            self.receipt["derivatives"]["minimum_final_rows_per_class_per_unit_arm"],
            1,
        )
        self.assertTrue(self.receipt["measurements"]["producer_is_causal_in_samples"])
        self.assertFalse((self.root / "private" / "temporary").exists())
        self.assertEqual(len(self.opener.calls), 26)

    def test_model_and_sealed_shards_are_structurally_separate(self) -> None:
        np = real._np()
        model_paths = sorted((self.root / "private" / "derivatives" / "model").iterdir())
        sealed_paths = sorted((self.root / "private" / "derivatives" / "sealed").iterdir())
        self.assertEqual(len(model_paths), 2)
        self.assertEqual(len(sealed_paths), 1)
        for path in model_paths:
            with np.load(path, allow_pickle=False) as archive:
                final_keys = [name for name in archive.files if "_final_" in name]
                self.assertFalse(
                    [
                        name
                        for name in final_keys
                        if any(token in name for token in ("target", "actual", "cue"))
                    ]
                )
        with np.load(sealed_paths[0], allow_pickle=False) as archive:
            self.assertEqual(
                set(archive.files),
                {
                    "C2I_item_ids",
                    "C2I_actual_action",
                    "C2I_cue_surrogate",
                    "I2C_item_ids",
                    "I2C_actual_action",
                    "I2C_cue_surrogate",
                },
            )

    def test_matrix_replay_and_private_roundtrip_are_exact(self) -> None:
        self.assertEqual(self.matrix["parameter_update_fits"], 660)
        self.assertEqual(self.matrix["target_blind_inference_calls"], 900)
        self.assertEqual(self.matrix["prediction_sets"], 900)
        self.assertEqual(
            self.matrix["canonical_private_prediction_sha256"],
            self.replay["canonical_private_prediction_sha256"],
        )
        self.assertEqual(
            self.matrix["canonical_private_prediction_sha256"],
            self.replayed_matrix["canonical_private_prediction_sha256"],
        )

    def test_odd_derangement_is_deterministic_and_near_balanced(self) -> None:
        np = real._np()
        labels = np.asarray([0, 0, 0, 1, 1, 1, 1], dtype="int8")
        runs = np.asarray(["01"] * len(labels))
        first = real._registered_train_derangement(labels, runs, key="C2I|sub-01|left")
        second = real._registered_train_derangement(labels, runs, key="C2I|sub-01|left")
        self.assertTrue(np.array_equal(first, second))
        for source in (0, 1):
            counts = np.bincount(first[labels == source], minlength=2)
            self.assertLessEqual(abs(int(counts[0]) - int(counts[1])), 1)

    def test_target_leak_split_drift_and_freeze_tamper_fail_closed(self) -> None:
        np = real._np()
        leaked = copy.copy(self.model_stage)
        leaked_final = dict(self.model_stage["final"])
        key = sorted(leaked_final)[0]
        rows = dict(leaked_final[key])
        rows["actual_action"] = np.zeros(len(rows["item_ids"]), dtype="int8")
        leaked_final[key] = rows
        leaked["final"] = leaked_final
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F12"):
            real._validate_target_free_model_stage(leaked, contract=self.contract)

        drifted = copy.copy(self.model_stage)
        drifted_final = dict(self.model_stage["final"])
        rows = dict(drifted_final[key])
        rows["runs"] = np.asarray(["01"] * len(rows["runs"]))
        drifted_final[key] = rows
        drifted["final"] = drifted_final
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F12"):
            real._validate_target_free_model_stage(drifted, contract=self.contract)

        tampered = dict(self.freeze)
        tampered["private_prediction_payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F15"):
            real.validate_freeze_against_matrix(
                tampered,
                matrix=self.matrix,
                model_stage=self.model_stage,
                contract=self.contract,
            )

    def test_scorer_is_aggregate_only_and_one_arm_cannot_rescue(self) -> None:
        self.assertEqual(self.score["route"], "IACKD2-R5")
        self.assertEqual(self.score["H1"], {"C2I": True, "I2C": True})
        self.assertEqual(self.score["H2"], {"C2I": True, "I2C": True})
        self.assertEqual(self.score["H3"], {"C2I": True, "I2C": True})
        self.assertFalse(self.score["individual_participant_metrics_published"])
        self.assertFalse(self.score["one_arm_rescue_allowed"])
        self.assertNotIn("participant_margins_private", json.dumps(self.score))

    def test_public_result_is_semantically_bound_after_rehash(self) -> None:
        result = {
            "schema_name": "neurodecodekit.iackd2r_result",
            "schema_version": real.SCHEMA_VERSION,
            "status": "complete_one_frozen_score_no_rerun",
            "source_kind": "real_public_IACKD2R",
            "contract_sha256": real.CONTRACT_SHA256,
            "decision_sha256": real.DECISION_SHA256,
            "implementation_commit": "a" * 40,
            "freeze_evidence": {
                "commit": "b" * 40,
                "push_CI_run_id": 1,
                "base_python_job_id": 2,
                "optional_neuro_job_id": 3,
                "both_required_jobs_green": True,
            },
            "freeze_record_sha256": "c" * 64,
            "acquisition_receipt_sha256": "d" * 64,
            "score": self.score,
            "inventory": {
                "participants": 15,
                "participant_hand_units": 30,
                "arms": 2,
                "fit_rows": 2880,
                "final_rows": 960,
                "parameter_update_fits": 660,
                "prediction_sets": 900,
            },
            "measurements": {
                "input_payload_bytes": 7249113684,
                "acquisition_runtime_seconds": 1.0,
                "target_blind_runtime_seconds": 1.0,
                "scoring_runtime_seconds": 1.0,
                "peak_RSS_bytes": 1,
                "public_result_bytes": 0,
                "producer_is_causal_in_samples": True,
                "end_to_end_latency_measured": False,
            },
            "access_counters": {
                "raw_payload_reads": 1340,
                "real_signal_run_parses": 128,
                "scorer_model_cache_reads": 128,
                "sealed_target_shard_reads": 128,
                "model_parameter_update_fits": 660,
                "target_blind_model_inference_calls": 900,
                "prediction_sets": 900,
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
            "warnings": [],
            "unavailable_fields": [],
            "claim_boundary": {
                "registered_scientific_outcome": self.score["maximum_claim"],
                "not_established": "brain_specific_origin_unseen_person_generalization_language_or_thought_decoding_real_time_hardware_home_use_assistive_or_clinical_result",
            },
        }
        real._finalize_result_bytes(result, maximum_bytes=4 * 1024 * 1024)
        real.validate_public_result(result)

        tampered = copy.deepcopy(result)
        tampered["decision_sha256"] = "0" * 64
        tampered["result_record_sha256"] = real._canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "result_record_sha256"
            }
        )
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F18"):
            real.validate_public_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["freeze_evidence"]["both_required_jobs_green"] = False
        tampered["result_record_sha256"] = real._canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "result_record_sha256"
            }
        )
        with self.assertRaisesRegex(real.RealDualReversalRefusal, "IACKD2R-F18"):
            real.validate_public_result(tampered)

    def test_measured_qualification_is_inspectable_and_claim_bounded(self) -> None:
        loaded = real.load_qualification_report(self.qualification_path)
        self.assertEqual(loaded, self.qualification)
        self.assertTrue(all(loaded["acceptance_gates"].values()))
        self.assertEqual(loaded["model_matrix"]["primary_parameter_update_fits"], 660)
        self.assertEqual(loaded["model_matrix"]["primary_prediction_sets"], 900)
        self.assertEqual(loaded["synthetic_score"]["route"], "IACKD2-R5")
        self.assertFalse(loaded["synthetic_score"]["has_scientific_value"])
        self.assertEqual(loaded["access_counters"]["real_or_public_payload_requests"], 0)
        self.assertLessEqual(loaded["measurements"]["output_bytes"], 8 * 1024 * 1024)


class IACKD2RImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record_path = (
            ROOT
            / "registries"
            / "iackd_transport_stable_dual_reversal_real_implementation.v0.json"
        )
        cls.record = json.loads(cls.record_path.read_text(encoding="utf-8"))

    def test_record_binds_green_decision_and_transport(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_transport_stable_dual_reversal_real_implementation",
        )
        self.assertEqual(
            self.record["status"],
            "generated_fixture_qualified_exact_additive_executor_requires_remote_green_before_public_access",
        )
        decision = self.record["green_authorization_decision"]
        self.assertEqual(decision["commit"], real.DECISION_COMMIT)
        self.assertEqual(decision["push_CI_run_id"], real.DECISION_CI_RUN_ID)
        self.assertEqual(decision["base_python_job_id"], real.DECISION_BASE_JOB_ID)
        self.assertEqual(
            decision["optional_neuro_job_id"], real.DECISION_OPTIONAL_JOB_ID
        )
        self.assertTrue(decision["both_required_jobs_green"])
        transport = self.record["green_transport_implementation"]
        self.assertEqual(transport["commit"], real.TRANSPORT_IMPLEMENTATION_COMMIT)
        self.assertTrue(transport["both_required_jobs_green"])

    def test_tracked_implementation_hashes_match(self) -> None:
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                observed = hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest()
                self.assertEqual(observed, binding["sha256"])

    def test_interface_is_additive_and_preserves_payload_and_firewall(self) -> None:
        interface = self.record["implemented_interface"]
        self.assertFalse(interface["old_executor_modified_or_called"])
        self.assertFalse(interface["old_root_or_retained_bundle_interface_exists"])
        stream = interface["fresh_stream"]
        self.assertEqual(stream["object_count"], 1_340)
        self.assertEqual(stream["payload_bytes"], 7_249_113_684)
        self.assertTrue(
            stream["payload_fixed_length_ETag_bytes_and_full_SHA256_unchanged"]
        )
        self.assertEqual(
            set(stream["metadata_framing_profiles"]),
            {"fixed_length", "chunked", "close_delimited"},
        )
        safety = interface["preconsumption_machine_safety"]
        self.assertEqual(safety["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(safety["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertTrue(safety["failure_before_consumed_marker"])
        firewall = interface["target_firewall"]
        self.assertEqual(firewall["final_target_rows_visible_to_model"], 0)
        self.assertTrue(firewall["green_freeze_required_before_score"])

    def test_fixture_metrics_and_real_counters_are_bounded(self) -> None:
        fixture = self.record["fixture_qualification"]
        self.assertTrue(fixture["all_gates_passed"])
        self.assertEqual(fixture["acceptance_gate_count"], 18)
        self.assertEqual(fixture["metadata_read_hash_parse_calls"], [4, 4, 4])
        self.assertEqual(fixture["parameter_update_fits"], 660)
        self.assertEqual(fixture["prediction_sets"], 900)
        self.assertTrue(fixture["deterministic_replay"])
        self.assertEqual(fixture["synthetic_route"], "IACKD2-R5")
        self.assertFalse(fixture["scientific_claim"])
        self.assertLessEqual(fixture["peak_RSS_bytes"], 512 * 1024**2)
        self.assertLessEqual(fixture["output_bytes"], 8 * 1024**2)
        self.assertTrue(
            all(
                value == 0
                for value in self.record[
                    "implementation_real_access_counters"
                ].values()
            )
        )

    def test_consumed_executor_is_byte_unchanged(self) -> None:
        old_module = (
            ROOT
            / "src"
            / "neurodecodekit"
            / "experiments"
            / "iackd_role_aware_dual_reversal_real.py"
        )
        self.assertEqual(
            hashlib.sha256(old_module.read_bytes()).hexdigest(),
            "7490896f799a2e576f24d1d612765141dc9bdb881ec1c87ffd2aca02c3c9b173",
        )

    def test_document_separates_engineering_and_scientific_claims(self) -> None:
        document = (
            ROOT / "docs" / "IACKD_TRANSPORT_STABLE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("does not import, call, modify", document)
        self.assertIn("exact observed byte count and registered SHA-256", document)


if __name__ == "__main__":
    unittest.main()
