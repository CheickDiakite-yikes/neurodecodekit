import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_f03_five_route_discriminator_contract.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_F03_FIVE_ROUTE_DISCRIMINATOR_PREREGISTRATION.md"
)
TEST_PATH = ROOT / "tests/test_marc2_f03_five_route_discriminator_contract.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2F03FiveRouteDiscriminatorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_bytes = CONTRACT_PATH.read_bytes()
        cls.contract = json.loads(cls.contract_bytes)

    def test_identity_and_status_are_frozen(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_f03_five_route_discriminator_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR10B")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )

    def test_green_prior_proof_is_exact(self):
        proof = self.contract["green_prior_proof"]
        self.assertEqual(
            proof["VR10A_implementation_commit"],
            "84103a5fab86b7c7c8d3cf3af00c9efe3457470c",
        )
        self.assertEqual(proof["VR10A_implementation_CI_run_id"], 31998811585)
        self.assertEqual(proof["VR10A_implementation_base_job_id"], 95295212461)
        self.assertEqual(
            proof["VR10A_implementation_optional_job_id"], 95295212440
        )
        self.assertEqual(
            proof["VR10A_closeout_commit"],
            "92d028139573309e5636b2f520c915e66113f7aa",
        )
        self.assertEqual(proof["VR10A_closeout_CI_run_id"], 32001355120)
        self.assertEqual(proof["VR10A_closeout_base_job_id"], 95302164129)
        self.assertEqual(proof["VR10A_closeout_optional_job_id"], 95302164150)
        self.assertTrue(proof["both_required_jobs_green_for_both_commits"])

    def test_fixed_inputs_match_exact_tracked_files(self):
        seen = set()
        total = 0
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], seen)
                seen.add(binding["role"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(sha256_file(path), binding["sha256"])
                total += binding["bytes"]
        self.assertEqual(len(seen), 10)
        self.assertEqual(total, 390_842)

    def test_five_routes_and_precedence_are_exact(self):
        routes = self.contract["ordered_discriminator_routes"]
        self.assertEqual([row["priority"] for row in routes], [1, 2, 3, 4, 5])
        self.assertEqual(
            [row["predicate_id"] for row in routes],
            [
                "F03P03_member_name_UTF8_length_at_most_1024",
                "F03P15_suffix_bearing_BIDS_identity",
                "F03P16_exact_freewill_task_token",
                "F03P18_unique_logical_run_companion",
                "F03P19_complete_four_companion_set",
            ],
        )
        self.assertEqual(
            [row["result_route"] for row in routes],
            [
                "MARC2VR10B-R1",
                "MARC2VR10B-R2",
                "MARC2VR10B-R3",
                "MARC2VR10B-R4",
                "MARC2VR10B-R5",
            ],
        )
        self.assertTrue(all(row["first_match_stops"] for row in routes))
        self.assertEqual(
            self.contract["generated_control_route"], "MARC2VR10B-G1"
        )

    def test_generated_matrix_is_exact_and_replayed(self):
        matrix = self.contract["generated_qualification_matrix"]
        self.assertEqual(len(matrix["cases"]), 6)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 24)
        self.assertEqual(matrix["required_exact_parser_entry_visits"], 29_448)
        self.assertEqual(matrix["required_VR6_calls"], 24)
        self.assertEqual(matrix["required_discriminator_calls"], 24)
        self.assertEqual(matrix["control_G1_paths"], 4)
        self.assertEqual(matrix["classified_R1_through_R5_paths"], 20)

    def test_output_firewall_is_coarse_and_recursive(self):
        firewall = self.contract["output_firewall"]
        self.assertTrue(firewall["recursive_forbidden_key_scan_required"])
        self.assertTrue(firewall["one_route_per_decision_required"])
        self.assertFalse(firewall["failed_value_allowed"])
        self.assertFalse(firewall["private_G1_result_allowed"])
        forbidden = set(firewall["forbidden_public_keys"])
        for key in (
            "member_name",
            "path",
            "row_index",
            "subject_id",
            "session_id",
            "run_id",
            "failed_value",
            "exception",
            "private_manifest",
            "signal",
            "target",
            "prediction",
        ):
            self.assertIn(key, forbidden)

    def test_acceptance_and_caps_are_bounded(self):
        self.assertEqual(len(self.contract["acceptance_gates"]), 14)
        self.assertEqual(self.contract["direct_refusal_minimum"], 45)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 45)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["generated_input_bytes"], 16 * 1024**2)
        self.assertEqual(caps["aggregate_output_bytes"], 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)

    def test_every_current_authority_and_operation_is_false_or_zero(self):
        self.assertTrue(
            all(value is False for value in self.contract["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )

    def test_registration_artifact_hashes_match(self):
        registration = self.contract["registration_artifacts"]
        self.assertEqual(sha256_file(DOC_PATH), registration["document_sha256"])
        self.assertEqual(sha256_file(TEST_PATH), registration["test_sha256"])

    def test_private_identity_is_not_copied(self):
        text = self.contract_bytes.decode("utf-8")
        for forbidden in (
            ".codex_work",
            "member_inventory.private",
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        ):
            self.assertNotIn(forbidden, text)

    def test_document_keeps_engineering_and_science_separate(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability sought", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("no private executor", text.lower())
        self.assertIn("one coarse class code", text)


if __name__ == "__main__":
    unittest.main()
