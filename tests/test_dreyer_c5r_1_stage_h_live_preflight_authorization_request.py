from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_preflight_authorization_request.v0.json"
)
DOC_PATH = ROOT / "docs/DREYER_C5R_1_STAGE_H_LIVE_PREFLIGHT_AUTHORIZATION_PACKET.md"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class DreyerC5R1StageHLivePreflightAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_proof_anchors_are_exact(self) -> None:
        self.assertEqual(self.request["packet_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.request["status"], "request_only_all_authority_false")
        proof = self.request["proof_anchors"]
        self.assertEqual(
            proof["Stage_H_implementation_commit"],
            "634fc9826f16352abb4fa1fc940c7bc6c2a0a795",
        )
        self.assertEqual(proof["Stage_H_implementation_CI_run_id"], 32_933_431_849)
        self.assertEqual(
            proof["Stage_H_generated_result_commit"],
            "af161844a9b49423a769440ed8f424bdae7836a0",
        )
        self.assertEqual(proof["Stage_H_generated_result_CI_run_id"], 32_934_121_394)
        self.assertTrue(proof["all_named_jobs_green"])

    def test_artifact_set_hashes_every_exact_bound_input(self) -> None:
        artifact_set = self.request["artifact_set"]
        rows = artifact_set["artifacts"]
        self.assertEqual(len(rows), artifact_set["artifact_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), artifact_set["artifact_bytes"])
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
        self.assertEqual(
            hashlib.sha256(_canonical_bytes(rows)).hexdigest(),
            artifact_set["canonical_sha256"],
        )

    def test_exact_member_sensor_gate_and_resource_envelope_are_narrow(self) -> None:
        member = self.request["exact_member"]
        self.assertEqual(member["participant"], "sub-01")
        self.assertEqual(member["run"], "R1")
        self.assertEqual(member["bytes"], 14_805_604)
        self.assertEqual(
            member["sha256"],
            "a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185",
        )
        live = self.request["requested_stage_HL2_one_real_invocation"]
        self.assertEqual(live["HTTP_GET_requests_exact"], 1)
        self.assertEqual(live["remaining_119_payload_requests"], 0)
        self.assertEqual(live["model_runs"], 0)
        self.assertEqual(live["scores"], 0)
        sensor = self.request["sensor_gate"]
        self.assertEqual(len(sensor["EEG_labels"]), 27)
        self.assertEqual(sensor["EOG_count"], 3)
        self.assertEqual(sensor["EMG_count"], 2)
        resources = self.request["resource_envelope"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["payload_network_bytes_maximum"], 16 << 20)
        self.assertEqual(resources["incremental_disk_bytes_maximum"], 32 << 20)
        self.assertEqual(resources["free_disk_bytes_minimum"], 10 << 30)

    def test_every_authority_flag_and_request_counter_is_false_or_zero(self) -> None:
        for key, value in self.request["authority"].items():
            self.assertIs(value, False, key)
        for key, value in self.request["operation_counters_at_request"].items():
            self.assertEqual(value, 0, key)

    def test_exclusions_preserve_other_files_models_and_claim_boundary(self) -> None:
        exclusions = set(self.request["explicit_exclusions"])
        self.assertIn("remaining_119_R1_R2_EDFs", exclusions)
        self.assertIn(
            "model_training_inference_calibration_selection_prediction_target_delivery_or_scoring",
            exclusions,
        )
        self.assertIn(
            "consumed_BNCI_EEGMMIDB_S20_S21_S24_S25_SpanishBCBL_or_other_private_artifact_access",
            exclusions,
        )
        self.assertIn("scientific_claim_not_established", self.request["claim_boundary"])

    def test_packet_text_is_request_only_and_explains_short_form_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("every authority flag remains false", text)
        self.assertIn("This packet therefore asks to risk one exact", text)
        self.assertIn("sole active Tier C", text)
        self.assertIn("Engineering capability requested:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
