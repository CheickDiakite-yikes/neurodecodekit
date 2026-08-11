from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.experiments import iackd_role_aware_dual_reversal as iackd2


ROOT = Path(__file__).resolve().parents[1]


def _has_exact_stack() -> bool:
    try:
        iackd2.dependency_versions()
    except (Exception, SystemExit):
        return False
    return True


HAS_EXACT_STACK = _has_exact_stack()


class IACKD2BaseTests(unittest.TestCase):
    def test_registered_plan_is_exact_target_free_and_dependency_light(self) -> None:
        plan = iackd2.registered_plan(ROOT)
        self.assertEqual(plan["contract_sha256"], iackd2.CONTRACT_SHA256)
        self.assertEqual(plan["participant_hand_units"], 30)
        self.assertEqual(plan["arm_count"], 2)
        self.assertEqual(plan["primary_matrix_fits"], 660)
        self.assertEqual(plan["primary_prediction_sets"], 900)
        self.assertEqual(plan["real_or_public_payload_reads"], 0)
        self.assertEqual(plan["old_retained_bundle_operations"], 0)
        self.assertFalse(plan["scientific_claim"])

    def test_registration_proof_and_contract_are_immutable(self) -> None:
        contract = iackd2.load_registered_contract(ROOT)
        self.assertEqual(
            iackd2.REGISTRATION_COMMIT,
            "5bdab3055a8a1c5200b5ec6c0037e401d8c817ce",
        )
        self.assertEqual(iackd2.REGISTRATION_CI_RUN_ID, 31448911258)
        self.assertEqual(iackd2.REGISTRATION_BASE_JOB_ID, 93648969685)
        self.assertEqual(iackd2.REGISTRATION_OPTIONAL_JOB_ID, 93648969711)
        self.assertEqual(
            contract["status"],
            "prospective_registration_frozen_real_execution_unauthorized",
        )
        self.assertEqual(
            contract["source_semantics_contract"]["policy_sha256"],
            iackd2.semantics.POLICY_SHA256,
        )

    def test_streaming_inventory_replays_without_payload_access(self) -> None:
        summary = iackd2.validate_streaming_inventory(ROOT)
        self.assertEqual(summary["selected_objects"], 1_340)
        self.assertEqual(summary["selected_payload_bytes"], 7_249_113_684)
        self.assertEqual(summary["run_groups"], 128)
        self.assertEqual(summary["objects_per_run_group"], 10)
        self.assertEqual(summary["largest_run_group_bytes"], 82_064_564)
        self.assertEqual(summary["largest_individual_object_bytes"], 73_200_640)
        self.assertEqual(summary["geometry_objects"], 60)
        self.assertEqual(summary["geometry_bytes"], 56_386)

    def test_mock_transport_fails_closed_on_identity_and_content_drift(self) -> None:
        body = b"generated-body"
        path = "generated/sub-00/eeg/generated.vhdr"
        etag = "generated-etag"
        valid = iackd2.MockResponse(path=path, status=200, body=body, etag=etag)
        summary = iackd2.verify_mock_response(
            valid,
            expected_path=path,
            expected_size=len(body),
            expected_etag=etag,
            expected_sha256=iackd2._sha256_bytes(body),
        )
        self.assertEqual(summary["body_bytes"], len(body))
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F04"):
            iackd2.verify_mock_response(
                iackd2.MockResponse(
                    path=path,
                    status=302,
                    body=body,
                    etag=etag,
                ),
                expected_path=path,
                expected_size=len(body),
                expected_etag=etag,
                expected_sha256=iackd2._sha256_bytes(body),
            )
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F05"):
            iackd2.verify_mock_response(
                valid,
                expected_path=path,
                expected_size=len(body),
                expected_etag=etag,
                expected_sha256="0" * 64,
            )

    def test_target_firewall_rejects_nested_aliases(self) -> None:
        iackd2._assert_target_free({"item_ids": ["generated-1"], "features": [[0.0]]})
        for key in (
            "target_value",
            "class_label",
            "signed_direction",
            "prediction_probability",
            "participant_outcome",
        ):
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    iackd2.DualReversalRefusal,
                    "IACKD2S-F09",
                ):
                    iackd2._assert_target_free({"nested": {key: [0, 1]}})

    def test_output_path_and_cap_refuse_existing_relative_and_symlink_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            root = Path(temporary)
            valid = root / "new.json"
            iackd2._ensure_output_preflight(valid, 1024)
            existing = root / "existing.json"
            existing.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F13"):
                iackd2._ensure_output_preflight(existing, 1024)
            with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F13"):
                iackd2._ensure_output_preflight(Path("relative.json"), 1024)
            with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F13"):
                iackd2._ensure_output_preflight(valid, 8 * 1024 * 1024 + 1)
            symlink_parent = root / "linked"
            symlink_parent.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F13"):
                iackd2._ensure_output_preflight(symlink_parent / "report.json", 1024)

    def test_router_reaches_every_frozen_outcome(self) -> None:
        routes = iackd2._route_reachability()
        self.assertEqual(
            set(routes.values()),
            {
                "IACKD2-R0",
                "IACKD2-R1",
                "IACKD2-R2",
                "IACKD2-R3",
                "IACKD2-R4",
                "IACKD2-R5",
            },
        )

    def test_default_cli_is_a_no_write_plan(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(iackd2.main([]), 0)
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["mode"], "generated_fixture_only_no_real_or_public_access")
        self.assertEqual(plan["real_or_public_payload_reads"], 0)


@unittest.skipUnless(HAS_EXACT_STACK, "requires the exact frozen optional IACKD-2 stack")
class IACKD2ExactStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="iackd2-tests-")
        cls.root = Path(cls.temporary.name)
        cls.reader_rows = []
        for index, include_optional in enumerate((False, True)):
            fixture = iackd2.write_generated_brainvision_fixture(
                cls.root / f"reader-{index}",
                include_optional_references=include_optional,
            )
            cls.reader_rows.append(iackd2.read_and_qualify_generated_brainvision(fixture))
        cls.derivatives = iackd2.build_generated_derivatives(ROOT)
        cls.model_stage = cls.derivatives["model_stage"]
        cls.scorer_stage = cls.derivatives["scorer_stage"]
        cls.matrix = iackd2.run_generated_model_matrix(cls.model_stage)
        cls.replay = iackd2.run_generated_model_matrix(cls.model_stage)
        cls.freeze = iackd2._freeze_record(cls.matrix, cls.model_stage)
        cls.score = iackd2.score_generated_matrix(
            cls.matrix,
            cls.model_stage,
            cls.scorer_stage,
            cls.freeze,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_generated_reader_preserves_source_roles_geometry_and_dimensions(self) -> None:
        self.assertEqual([row["row_count"] for row in self.reader_rows], [29, 31])
        self.assertEqual(
            [row["optional_M1_M2_present"] for row in self.reader_rows],
            [False, True],
        )
        for row in self.reader_rows:
            self.assertEqual(row["predictive_EEG_count"], 26)
            self.assertEqual(
                row["dimensions"],
                {
                    "primary": 130,
                    "central": 15,
                    "occipital": 15,
                    "ocular": 10,
                    "early": 78,
                    "late": 78,
                    "prewindow": 130,
                    "timing": 4,
                },
            )
            self.assertTrue(row["causal_future_tail_invariant"])
            self.assertFalse(row["MNE_inferred_types_authoritative"])

    def test_generated_derivatives_are_strictly_split_and_target_firewalled(self) -> None:
        derivatives = self.derivatives
        model_stage = self.model_stage
        scorer_stage = self.scorer_stage
        self.assertEqual(derivatives["generated_source_rows"], 4_096)
        self.assertEqual(model_stage["fit_rows"], 3_136)
        self.assertEqual(model_stage["final_rows"], 960)
        self.assertEqual(scorer_stage["sealed_rows"], 960)
        self.assertEqual(len(model_stage["fit"]), 60)
        self.assertEqual(len(model_stage["final"]), 60)
        self.assertEqual(len(scorer_stage["sealed"]), 60)
        self.assertNotIn("sealed", model_stage)
        for key, rows in model_stage["final"].items():
            iackd2._assert_target_free(rows)
            self.assertNotIn("fit_targets", rows)
            self.assertEqual(
                len(rows["item_ids"]),
                len(scorer_stage["sealed"][key]["item_ids"]),
            )
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F09"):
            iackd2.run_generated_model_matrix(derivatives)

    def test_seeded_derangement_is_balanced_within_every_run_and_class(self) -> None:
        np = iackd2._np()
        rows = next(iter(self.model_stage["fit"].values()))
        labels = rows["fit_targets"]
        shuffled = iackd2._fixed_train_label_derangement(
            labels,
            rows["runs"],
            key="generated-unit",
        )
        for run_id in sorted(set(rows["runs"].tolist())):
            for source in (0, 1):
                mask = (rows["runs"] == run_id) & (labels == source)
                self.assertEqual(np.bincount(shuffled[mask], minlength=2).tolist(), [4, 4])

    def test_full_matrix_counts_and_deterministic_replay_are_exact(self) -> None:
        self.assertEqual(self.matrix["parameter_update_fits"], 660)
        self.assertEqual(self.matrix["target_blind_inference_calls"], 900)
        self.assertEqual(self.matrix["prediction_sets"], 900)
        self.assertEqual(
            self.matrix["canonical_private_prediction_sha256"],
            self.replay["canonical_private_prediction_sha256"],
        )
        self.assertEqual(
            self.matrix["condition_prediction_sha256"],
            self.replay["condition_prediction_sha256"],
        )
        self.assertEqual(self.freeze["final_target_rows_visible_to_model_stage"], 0)
        self.assertEqual(self.freeze["parameter_update_fits"], 660)
        self.assertEqual(self.freeze["prediction_sets"], 900)
        self.assertFalse(self.freeze["individual_predictions_published"])

    def test_constructed_full_conjunction_is_aggregate_only_and_non_scientific(self) -> None:
        self.assertEqual(self.score["synthetic_route"], "IACKD2-R5")
        self.assertEqual(self.score["H1"], {"C2I": True, "I2C": True})
        self.assertEqual(self.score["H2"], {"C2I": True, "I2C": True})
        self.assertEqual(self.score["H3"], {"C2I": True, "I2C": True})
        self.assertTrue(self.score["H1_conjunction"])
        self.assertTrue(self.score["H3_conjunction"])
        self.assertFalse(self.score["individual_participant_metrics_published"])
        encoded = json.dumps(self.score, sort_keys=True)
        self.assertNotIn("participant_margins_private", encoded)

    def test_malformed_matrix_and_report_fail_closed(self) -> None:
        malformed = copy.deepcopy(self.matrix)
        malformed["prediction_sets"] = 899
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F12"):
            iackd2.score_generated_matrix(
                malformed,
                self.model_stage,
                self.scorer_stage,
                self.freeze,
            )
        broken_freeze = dict(self.freeze)
        broken_freeze["prediction_sets"] = 899
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F12"):
            iackd2.score_generated_matrix(
                self.matrix,
                self.model_stage,
                self.scorer_stage,
                broken_freeze,
            )
        with self.assertRaisesRegex(iackd2.DualReversalRefusal, "IACKD2S-F15"):
            iackd2.validate_qualification_report({"status": "invented"})


if __name__ == "__main__":
    unittest.main()
