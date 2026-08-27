from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/communication_live_session_g0_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/COMMUNICATION_LIVE_SESSION_G0_IMPLEMENTATION.md"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class CommunicationLiveSessionG0ImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_prerequisite_green_proofs_are_exact(self) -> None:
        self.assertEqual(self.record["lane_id"], "COMM-LIVE-G0")
        proofs = self.record["prerequisite_green_proofs"]
        self.assertEqual(
            proofs["amendment_1"]["commit"],
            "2715d8a8344f5c58dd64f6865639822ec83888aa",
        )
        self.assertEqual(proofs["amendment_1"]["CI_run_id"], 33_106_893_586)
        self.assertEqual(
            proofs["source_chunk_v0"]["commit"],
            "788c34354aab3e73656ada6ea1ad62af6b7852bc",
        )
        self.assertEqual(proofs["source_chunk_v0"]["CI_run_id"], 33_109_065_198)
        self.assertTrue(proofs["source_chunk_v0"]["present_on_GitHub_main"])

    def test_artifact_set_binds_every_exact_input(self) -> None:
        artifact_set = self.record["artifact_set"]
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

    def test_qualification_remains_closed_and_all_forbidden_counters_are_zero(self) -> None:
        qualification = self.record["official_generated_qualification"]
        self.assertFalse(qualification["executed"])
        self.assertFalse(qualification["invocation_consumed"])
        for key, value in self.record["operation_counters"].items():
            self.assertEqual(value, 0, key)
        self.assertFalse(self.record["capabilities"]["real_stream_or_device_adapter"])
        self.assertFalse(self.record["capabilities"]["real_model_or_provider_adapter"])

    def test_document_states_engineering_and_scientific_boundaries(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("official one-shot qualification has not run", text)


if __name__ == "__main__":
    unittest.main()
