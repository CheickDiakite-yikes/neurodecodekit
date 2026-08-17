import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_generated_diagnostic_relay_contract.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_GENERATED_DIAGNOSTIC_RELAY_PREREGISTRATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2GeneratedDiagnosticRelayContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_predecessor_are_exact(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_generated_diagnostic_relay_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR8B")
        proof = self.contract["green_VR8A_closeout_proof"]
        self.assertEqual(
            proof["commit"], "8bbb8e36406a5043fdbf1a2e285b070d1bdfc0db"
        )
        self.assertEqual(proof["CI_run_id"], 31_986_401_715)
        self.assertEqual(proof["base_python_job_id"], 95_262_067_116)
        self.assertEqual(proof["optional_neuro_job_id"], 95_262_067_131)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_fixed_artifacts_are_exact_and_tracked(self):
        fixed = self.contract["fixed_inputs"]
        self.assertEqual(len(fixed), 17)
        self.assertEqual(sum(row["bytes"] for row in fixed), 622_989)
        seen = set()
        for row in fixed:
            with self.subTest(path=row["path"]):
                self.assertEqual(set(row), {"role", "path", "bytes", "sha256"})
                self.assertNotIn(row["path"], seen)
                seen.add(row["path"])
                self.assertNotIn(".codex_work", row["path"])
                path = ROOT / row["path"]
                self.assertTrue(path.is_file())
                payload = path.read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_full_scale_composition_is_frozen(self):
        composition = self.contract["generated_composition"]
        self.assertEqual(composition["inventory_rows"], 1_227)
        self.assertEqual(composition["regular_file_rows"], 1_025)
        self.assertEqual(composition["directory_rows"], 202)
        self.assertTrue(composition["exact_central_directory_parser_required"])
        self.assertTrue(composition["exact_live_manifest_composer_required"])
        self.assertEqual(
            composition["synthetic_live_normalization_fields"],
            ["transport_body_sha256"],
        )
        self.assertFalse(composition["member_local_headers_materialized"])
        self.assertFalse(composition["member_payloads_materialized"])
        self.assertFalse(composition["consumed_VR7P_may_be_imported_or_called"])

    def test_route_matrix_is_exact_and_replayed(self):
        matrix = self.contract["route_matrix"]
        self.assertEqual([row["case"] for row in matrix], ["success", "F02", "F03", "F04"])
        self.assertEqual(matrix[0]["expected_disposition"], "VR6_success")
        for row, nested in zip(
            matrix[1:],
            ("MARC2VR2-F02", "MARC2VR2-F03", "MARC2VR2-F04"),
            strict=True,
        ):
            self.assertEqual(row["expected_outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["expected_nested_VR2_route"], nested)
        replay = self.contract["replay_policy"]
        self.assertEqual(replay["central_directory_orders"], ["canonical", "reversed"])
        self.assertEqual(replay["matrix_paths_per_replay"], 8)
        self.assertEqual(replay["exact_replays"], 2)

    def test_output_firewall_and_mutations_are_strict(self):
        relay = self.contract["relay_contract"]
        self.assertEqual(
            relay["published_refusal_fields"],
            ["case", "disposition", "outer_VR6_route", "nested_VR2_route"],
        )
        self.assertFalse(relay["exception_text_or_reason_published"])
        self.assertFalse(relay["member_person_session_run_or_value_published"])
        mutations = self.contract["qualification"]
        self.assertGreaterEqual(mutations["minimum_direct_refusals"], 24)
        required = " ".join(mutations["required_refusal_classes"]).lower()
        for token in ("route", "reason", "path", "parser", "interval", "hash", "thread", "rss"):
            self.assertIn(token, required)

    def test_resources_are_bounded_and_one_threaded(self):
        caps = self.contract["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["materialized_generated_input_bytes"], 8 * 1024**2)
        self.assertEqual(caps["aggregate_output_bytes"], 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_private_bytes"], 0)

    def test_authority_and_current_operations_are_zero(self):
        self.assertTrue(
            all(value is False for value in self.contract["authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        next_gate = self.contract["next_gate"]
        self.assertTrue(next_gate["generated_implementation_after_registration_green"])
        self.assertFalse(next_gate["private_diagnostic_execution_authorized"])
        self.assertTrue(next_gate["future_private_read_requires_new_Tier_C_decision"])

    def test_registration_artifacts_and_claim_boundary_are_exact(self):
        registration = self.contract["registration_artifacts"]
        self.assertEqual(sha256_file(ROOT / registration["document_path"]), registration["document_sha256"])
        self.assertEqual(sha256_file(ROOT / registration["test_path"]), registration["test_sha256"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability specified", text)
        self.assertIn("Scientific claim not established", text)
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
