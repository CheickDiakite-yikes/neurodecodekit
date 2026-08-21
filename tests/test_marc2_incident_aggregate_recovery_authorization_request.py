import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_incident_aggregate_recovery_authorization_request.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs/MARC_2_INCIDENT_AGGREGATE_RECOVERY_AUTHORIZATION_PACKET.md"
)


def _git_blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


class Marc2IncidentAggregateRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_identity_and_green_incident_proof_are_exact(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR14P")
        proof = self.request["green_incident_proof"]
        self.assertEqual(proof["commit"], "1563cae48a9424b38f13a42b25e17e8587a18c92")
        self.assertEqual(proof["CI_run_id"], 32_442_807_612)
        self.assertEqual(proof["base_python_job_id"], 96_656_682_033)
        self.assertEqual(proof["optional_neuro_job_id"], 96_656_682_232)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_fixed_inputs_are_byte_hash_and_blob_exact(self):
        for row in self.request["fixed_inputs"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob(payload), row["git_blob"])

    def test_current_authority_and_operations_are_all_false_or_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["authorization"].values())
        )
        self.assertTrue(
            all(
                value == 0
                for value in self.request["current_operation_counters"].values()
            )
        )

    def test_future_scope_is_aggregate_only_and_bounded(self):
        paths = self.request["future_fixed_paths"]
        self.assertTrue(paths["aggregate_report"].endswith("report.aggregate.v0.json"))
        self.assertTrue(
            paths["private_manifest_forbidden"].endswith("cohort.private.v0.json")
        )
        self.assertFalse(paths["generic_path_or_output_override_allowed"])
        caps = self.request["future_resource_caps"]
        self.assertEqual(caps["aggregate_report_content_opens"], 1)
        self.assertEqual(caps["aggregate_report_bytes_maximum"], 65_536)
        self.assertEqual(caps["structural_source_opens"], 0)
        self.assertEqual(caps["private_manifest_operations"], 0)
        self.assertEqual(caps["retry_rerun_resume"], 0)

    def test_routes_and_claim_ceiling_remain_strict(self):
        routes = self.request["future_route_ceiling"]
        self.assertEqual(len(routes["allowed_routes"]), 8)
        self.assertEqual(routes["allowed_routes"][0], "MARC2VR13P-R1")
        self.assertEqual(routes["allowed_routes"][-1], "MARC2VR13P-R8")
        self.assertEqual(routes["FW2_or_CIL1_execution_effect"], "none")
        claims = self.request["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_request", "scientific_ceiling"}:
                self.assertFalse(value)
        for phrase in (
            "all-false request",
            "one future read of only",
            "Every authorization",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.document)


if __name__ == "__main__":
    unittest.main()
