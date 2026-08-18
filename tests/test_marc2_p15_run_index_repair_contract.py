import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_p15_run_index_repair_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_P15_RUN_INDEX_REPAIR_PREREGISTRATION.md"
TEST_PATH = ROOT / "tests/test_marc2_p15_run_index_repair_contract.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2P15RunIndexRepairContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_bytes = CONTRACT_PATH.read_bytes()
        cls.contract = json.loads(cls.contract_bytes)

    def test_identity_and_status_are_frozen(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_p15_run_index_repair_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR12A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )

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
        self.assertEqual(total, 301_432)

    def test_observed_route_and_private_boundary_are_exact(self):
        observed = self.contract["observed_route_binding"]
        self.assertEqual(observed["VR11P_route"], "MARC2VR11P-R2")
        self.assertEqual(observed["frozen_predicate_class"], "P15")
        self.assertFalse(observed["failed_private_value_available"])
        self.assertFalse(observed["private_result_reinspection_allowed"])
        self.assertFalse(observed["unpadded_run_index_observed_privately"])

    def test_standards_policy_is_narrow_and_source_preserving(self):
        standards = self.contract["standards_basis"]
        self.assertEqual(standards["BIDS_version"], "1.11.1")
        self.assertEqual(standards["run_entity_format"], "run-<index>")
        self.assertEqual(standards["index_semantics"], "nonnegative_integer")
        repair = self.contract["frozen_repair"]
        self.assertEqual(repair["accepted_source_digit_widths"], [1, 2])
        self.assertEqual(repair["semantic_grouping"], "base10_integer")
        self.assertTrue(repair["selected_member_names_remain_source_exact"])
        self.assertTrue(repair["reservation_uses_source_exact_UTF8_name_bytes"])
        self.assertFalse(repair["subject_or_session_label_broadening"])
        self.assertFalse(repair["task_or_suffix_broadening"])

    def test_generated_matrix_and_neighboring_refusals_are_frozen(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(
            matrix["success_variants"],
            [
                "padded_control",
                "unpadded_single_digit",
                "bundle_consistent_mixed_width",
            ],
        )
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_success_paths"], 12)
        self.assertEqual(
            matrix["required_refusal_classes"], ["P15", "P16", "P18", "P19"]
        )
        self.assertEqual(len(matrix["required_refusal_witnesses"]), 8)
        self.assertEqual(self.contract["direct_refusal_minimum"], 36)

    def test_acceptance_and_caps_are_bounded(self):
        self.assertEqual(len(self.contract["acceptance_gates"]), 14)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 30)
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
        self.assertIn("not a claim about the consumed", text)
        self.assertIn("no private access", text.lower())


if __name__ == "__main__":
    unittest.main()
