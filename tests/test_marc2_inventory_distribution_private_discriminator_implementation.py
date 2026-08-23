import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/"
    "marc2_inventory_distribution_private_discriminator_implementation.v0.json"
)


class Marc2InventoryDistributionPrivateDiscriminatorImplementationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_record_is_stage_1_only_or_exactly_proof_closed(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_inventory_distribution_private_discriminator_implementation",
        )
        self.assertEqual(self.record["lane_id"], "MARC2-VR30P")
        proof = self.record["remote_implementation_proof"]
        if proof is None:
            self.assertFalse(
                self.record["stage_2_status"]["private_execution_available_now"]
            )
            self.assertTrue(
                self.record["stage_2_status"][
                    "proof_closeout_required_before_readiness"
                ]
            )
        else:
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
            self.assertEqual(proof["qualification_route"], "MARC2VR30P-G1")
            self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
            self.assertEqual(proof["private_operations_during_proof_closeout"], 0)

    def test_every_implementation_artifact_is_exact(self):
        for artifact in self.record["implementation_artifacts"]:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_generated_measurements_pass_every_cap(self):
        measured = self.record["generated_qualification"]
        caps = self.record["resource_caps"]
        self.assertEqual(measured["route"], "MARC2VR30P-G1")
        self.assertEqual(measured["paths"], 32)
        self.assertEqual(measured["source_content_opens"], 32)
        self.assertEqual(measured["VR29A_calls"], 32)
        self.assertEqual(measured["nested_VR25A_calls"], 32)
        self.assertEqual(measured["nested_R1_filter_calls"], 16)
        self.assertEqual(
            measured["VR29A_route_counts"],
            {
                "MARC2VR29A-G1": 4,
                "MARC2VR29A-G2": 4,
                "MARC2VR29A-R1": 8,
                "MARC2VR29A-R2": 8,
                "MARC2VR29A-R3": 8,
            },
        )
        self.assertEqual(
            measured["VR25A_route_counts"],
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-G2": 4,
                "MARC2VR25A-R1": 16,
                "MARC2VR25A-R2": 4,
                "MARC2VR25A-R3": 4,
            },
        )
        self.assertGreaterEqual(measured["direct_refusals"], 90)
        self.assertTrue(measured["deterministic_replay"])
        self.assertTrue(measured["marker_preceded_every_source_open"])
        self.assertLessEqual(
            measured["runtime_seconds"], caps["generated_runtime_seconds_maximum"]
        )
        self.assertLess(
            measured["peak_RSS_bytes"], caps["peak_RSS_bytes_maximum_exclusive"]
        )
        self.assertLessEqual(
            measured["peak_incremental_output_bytes"],
            caps["peak_incremental_output_bytes_maximum"],
        )
        self.assertEqual(measured["retained_generated_output_bytes"], 0)

    def test_every_forbidden_operation_counter_is_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )

    def test_wrapper_does_not_import_or_name_consumed_private_executors(self):
        source = (
            ROOT
            / "src/neurodecodekit/datasets/"
            "marc2_inventory_distribution_private_discriminator.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "marc2_published_task_private_confirmation as",
            "marc2_r5_private_discriminator as",
            "marc2_selection_boundary_private_confirmation as",
            "marc2_inventory_taxonomy_private_discriminator as",
            ".codex_work/marc2_published_task_private_confirmation",
            ".codex_work/marc2_inventory_taxonomy_private_discriminator",
        ):
            self.assertNotIn(forbidden, source)

    def test_interface_has_no_generic_path_or_policy_override(self):
        surface = self.record["surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(
            surface[
                "generic_path_URL_output_threshold_route_reason_retry_or_substitution_arguments"
            ],
            0,
        )
        self.assertTrue(surface["public_execute_refuses_without_remote_proof"])
        self.assertTrue(surface["marker_precedes_source_content_open"])


if __name__ == "__main__":
    unittest.main()
