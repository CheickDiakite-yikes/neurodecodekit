import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_f03_predicate_decomposition_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_F03_PREDICATE_DECOMPOSITION_PREREGISTRATION.md"
TEST_PATH = ROOT / "tests/test_marc2_f03_predicate_decomposition_contract.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2F03PredicateDecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_bytes = CONTRACT_PATH.read_bytes()
        cls.contract = json.loads(cls.contract_bytes)

    def test_identity_and_status_are_frozen(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_f03_predicate_decomposition_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR10A")
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
        self.assertEqual(len(seen), 14)
        self.assertEqual(total, 453_477)

    def test_twenty_leaf_partition_is_exact(self):
        leaves = self.contract["F03_leaf_predicates"]
        self.assertEqual(len(leaves), 20)
        self.assertEqual(len({row["predicate_id"] for row in leaves}), 20)
        statuses = [row["status"] for row in leaves]
        self.assertEqual(statuses.count("excluded_by_committed_evidence"), 15)
        self.assertEqual(statuses.count("unresolved_source_dependent"), 5)
        self.assertTrue(all(row["private_observation"] is False for row in leaves))

    def test_unresolved_five_are_exact(self):
        unresolved = [
            row["predicate_id"]
            for row in self.contract["F03_leaf_predicates"]
            if row["status"] == "unresolved_source_dependent"
        ]
        self.assertEqual(
            unresolved,
            [
                "F03P03_member_name_UTF8_length_at_most_1024",
                "F03P15_suffix_bearing_BIDS_identity",
                "F03P16_exact_freewill_task_token",
                "F03P18_unique_logical_run_companion",
                "F03P19_complete_four_companion_set",
            ],
        )

    def test_generated_matrix_is_full_scale_and_replayed(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(len(matrix["cases"]), 6)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 24)
        self.assertEqual(matrix["required_exact_parser_entry_visits"], 29_448)
        self.assertEqual(matrix["required_VR6_calls"], 24)
        self.assertEqual(matrix["control_success_paths"], 4)
        self.assertEqual(matrix["nested_F03_paths"], 20)
        self.assertTrue(matrix["mutation_before_exact_parser_required"])

    def test_acceptance_and_caps_are_bounded(self):
        acceptance = self.contract["acceptance_gates"]
        self.assertEqual(len(acceptance), 12)
        self.assertEqual(self.contract["direct_refusal_minimum"], 40)
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
        self.assertIn("does not assert that any one", text)
        self.assertIn("no private access", text.lower())


if __name__ == "__main__":
    unittest.main()
