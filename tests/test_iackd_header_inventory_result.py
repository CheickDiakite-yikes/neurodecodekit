import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/iackd_channel_inventory_result.v0.json"
DOCUMENT_PATH = ROOT / "docs/IACKD_CHANNEL_INVENTORY_RESULT.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDHeaderInventoryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_result_is_complete_consumed_R5_and_not_rerunnable(self):
        self.assertEqual(
            self.result["status"],
            "complete_consumed_IACKDH_R5_two_header_signatures_no_rerun",
        )
        execution = self.result["execution"]
        self.assertEqual(execution["registered_execution_ordinal"], 1)
        self.assertTrue(execution["consumed"])
        self.assertFalse(execution["retry_allowed"])
        self.assertFalse(execution["rerun_allowed"])
        self.assertEqual(self.result["diagnosis"]["diagnostic_route"], "IACKDH-R5")

    def test_remote_green_chain_preceded_the_real_audit(self):
        proof = self.result["green_proof_chain"]
        self.assertEqual(
            proof["implementation"]["commit"],
            "16621cc484f4bec4a9474b9ac20d5b7d9314152f",
        )
        self.assertEqual(proof["implementation"]["push_CI_run_id"], 31_415_213_841)
        self.assertEqual(
            proof["request"]["commit"],
            "56531c64b6733f93c9def80ad57125e0ee998fd8",
        )
        self.assertEqual(proof["request"]["push_CI_run_id"], 31_416_489_006)
        self.assertEqual(
            proof["decision"]["commit"],
            "04f2706b56315186fac0c9a82686e9a360dbaf1e",
        )
        self.assertEqual(proof["decision"]["push_CI_run_id"], 31_424_361_969)
        self.assertTrue(all(row["both_required_jobs_green"] for row in proof.values()))

    def test_execution_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_objects"], 128)
        self.assertEqual(measured["input_bytes"], 161_792)
        self.assertEqual(measured["network_body_bytes"], 161_792)
        self.assertEqual(measured["body_SHA256_passes"], 128)
        self.assertEqual(measured["semantic_parse_passes"], 128)
        self.assertEqual(measured["generated_output_bytes"], 5_515)
        self.assertEqual(measured["retained_generated_bytes"], 5_759)
        self.assertLess(measured["runtime_seconds"], 120)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertIsNone(measured["producer_is_causal"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_two_aggregate_signatures_cover_every_header(self):
        groups = self.result["diagnosis"]["signature_groups"]
        self.assertEqual(len(groups), 2)
        self.assertEqual(sum(row["occurrence_count"] for row in groups), 128)
        self.assertEqual(
            [(row["occurrence_count"], row["declared_channel_count"]) for row in groups],
            [(96, 29), (32, 31)],
        )
        first, second = groups
        self.assertFalse(first["allowlisted_name_presence"]["M1"])
        self.assertFalse(first["allowlisted_name_presence"]["M2"])
        self.assertTrue(second["allowlisted_name_presence"]["M1"])
        self.assertTrue(second["allowlisted_name_presence"]["M2"])
        for row in groups:
            presence = row["allowlisted_name_presence"]
            self.assertTrue(presence["HEOG"])
            self.assertTrue(presence["VEOG"])
            self.assertTrue(presence["TRIGGER"])
            self.assertFalse(presence["HEO"])
            self.assertFalse(presence["VEO"])
            self.assertEqual(row["sampling_rate_hz"], "1024")

    def test_first_header_failed_both_frozen_predicates(self):
        first = self.result["diagnosis"]["first_header_diagnosis"]
        self.assertEqual(first["declared_channel_count"], 29)
        self.assertFalse(first["canonical_32_plus_4_count_gate_passed"])
        self.assertFalse(first["canonical_name_gate_passed"])
        self.assertFalse(first["combined_gate_passed"])
        self.assertEqual(
            first["canonical_name_presence"],
            {"HEOG": True, "M1": False, "M2": False, "VEOG": True},
        )

    def test_all_acceptance_gates_passed(self):
        gates = self.result["acceptance_gate_results"]
        self.assertEqual(len(gates), 11)
        self.assertTrue(all(gates.values()))

    def test_only_authorized_header_counters_are_nonzero(self):
        counters = self.result["access_counters"]
        allowed = {
            "real_VHDR_requests": 128,
            "real_VHDR_body_bytes": 161_792,
            "real_header_parses": 128,
        }
        for name, value in counters.items():
            self.assertEqual(value, allowed.get(name, 0), name)

    def test_public_result_has_no_individual_path_or_unallowlisted_name(self):
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("sub-", serialized)
        self.assertNotIn(".vhdr", serialized.lower())
        self.assertFalse(self.result["public_artifact_bindings"]["contains_local_path"])
        self.assertFalse(
            self.result["public_artifact_bindings"]
            ["contains_raw_header_or_unallowlisted_channel_name"]
        )

    def test_public_artifact_hashes_and_claim_language_are_current(self):
        bindings = self.result["public_artifact_bindings"]
        self.assertEqual(bindings["document_sha256"], sha256(DOCUMENT_PATH))
        self.assertEqual(bindings["invariant_test_sha256"], sha256(Path(__file__)))
        compact = " ".join(self.document.split())
        self.assertIn("Engineering capability added:", compact)
        self.assertIn("Scientific claim not established:", compact)
        self.assertIn("two-signature compatibility contract", compact)
        self.assertIn("no neural effect", compact)


if __name__ == "__main__":
    unittest.main()
