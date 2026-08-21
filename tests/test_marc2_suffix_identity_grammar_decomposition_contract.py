import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_grammar_decomposition_contract.v0.json"
)


class Marc2SuffixIdentityGrammarDecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_consumed_route_binding(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR15A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )
        observed = self.contract["observed_route_binding"]
        self.assertEqual(observed["VR14P_status"], "consumed")
        self.assertEqual(observed["VR14P_route"], "MARC2VR13P-R2")
        self.assertFalse(
            observed["failed_value_predicate_row_path_identity_or_person_available"]
        )

    def test_fixed_inputs_match_exact_bytes_and_hashes(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), 11)
        self.assertEqual(sum(row["bytes"] for row in rows), 215_394)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )

    def test_ordered_route_table_is_complete_and_unique(self):
        rows = self.contract["ordered_route_table"]
        self.assertEqual(len(rows), 16)
        self.assertEqual(
            [row["route"] for row in rows],
            [f"MARC2VR15A-R{index}" for index in range(1, 17)],
        )
        self.assertEqual(len({row["class"] for row in rows}), 16)
        self.assertEqual(rows[-1]["class"], "multiple_identity_classes")

    def test_generated_matrix_and_resources_are_bounded(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["cases"]), 17)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 68)
        self.assertEqual(matrix["required_VR12A_calls"], 68)
        self.assertEqual(matrix["route_count_each"], 4)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLessEqual(caps["generated_input_bytes_maximum"], 32 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)

    def test_private_neural_and_claim_authority_remains_closed(self):
        auth = self.contract["authorization_state"]
        self.assertTrue(auth["artifact_only_static_analysis_authorized_under_charter"])
        self.assertTrue(
            auth[
                "generated_only_implementation_after_registration_green_authorized_under_charter"
            ]
        )
        for key, value in auth.items():
            if key.endswith("authorized") and "under_charter" not in key:
                self.assertFalse(value, key)
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )


if __name__ == "__main__":
    unittest.main()
