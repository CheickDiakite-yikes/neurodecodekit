import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_l2_fixed_header_activation_authorization_request.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_ACTIVATION_AUTHORIZATION_PACKET.md"
)


class DreyerStageHL2FixedHeaderActivationAuthorizationRequestTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_request_identity_and_green_basis_are_exact(self):
        self.assertEqual(self.request["request_id"], "DREYER-C5R-1-HL2-A0")
        self.assertEqual(self.request["status"], "request_only_all_authority_false")
        green = self.request["green_basis"]
        self.assertEqual(
            green["result_proof_commit"],
            "1ae340354352d544d6d99fe5af6f354ab668bf9c",
        )
        self.assertEqual(green["result_proof_CI_run_id"], 33_255_170_805)
        self.assertEqual(green["result_proof_base_python_job_id"], 99_107_500_593)
        self.assertEqual(
            green["result_proof_optional_neuro_readers_job_id"], 99_107_500_410
        )
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_bound_proof_artifacts_are_exact_and_canonical(self):
        rows = self.request["bound_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        summary = self.request["bound_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 10_425)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_member_and_one_shot_transport_are_exact(self):
        member = self.request["exact_member"]
        self.assertEqual(member["participant"], "sub-01")
        self.assertEqual(member["run"], "R1")
        self.assertEqual(member["bytes"], 14_805_604)
        self.assertEqual(len(member["sha256"]), 64)
        transport = self.request["transport_contract"]
        self.assertTrue(transport["verified_TLS"])
        self.assertTrue(transport["direct_GET"])
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["fallbacks_or_substitutions"], 0)

    def test_sensor_gate_and_resources_are_frozen(self):
        gate = self.request["sensor_gate"]
        self.assertEqual(len(gate["EEG_labels"]), 27)
        self.assertEqual(gate["EEG_count"], 27)
        self.assertEqual(gate["EOG_count"], 3)
        self.assertEqual(gate["wrist_EMG_count"], 2)
        self.assertEqual(gate["physiological_sampling_rate_hz"], 512)
        resources = self.request["resource_envelope"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["payload_network_bytes_maximum"], 16 * 1024**2)
        self.assertEqual(resources["incremental_disk_bytes_maximum"], 32 * 1024**2)
        self.assertEqual(resources["free_disk_bytes_minimum"], 10 * 1024**3)

    def test_every_authority_flag_and_operation_counter_is_false_or_zero(self):
        for key, value in self.request["authority"].items():
            self.assertFalse(value, key)
        for key, value in self.request["operation_counters_at_request"].items():
            self.assertEqual(value, 0, key)

    def test_fresh_decision_and_ordered_green_barriers_are_required(self):
        barriers = self.request["activation_barriers"]
        self.assertTrue(barriers["request_commit_push_and_two_job_green_required"])
        self.assertTrue(
            barriers[
                "request_proof_closeout_commit_push_and_two_job_green_required"
            ]
        )
        self.assertTrue(barriers["fresh_packet_bound_maintainer_words_required"])
        self.assertTrue(
            barriers["separate_decision_commit_push_and_two_job_green_required"]
        )
        self.assertFalse(barriers["earlier_short_form_may_activate"])

    def test_document_states_engineering_and_scientific_boundaries(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("Every authority flag", document)
        self.assertIn("one exact 14,805,604-byte public EDF", document)


if __name__ == "__main__":
    unittest.main()
