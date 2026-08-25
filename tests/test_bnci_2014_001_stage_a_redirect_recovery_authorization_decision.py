import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT
    / "registries/bnci_2014_001_stage_a_redirect_recovery_authorization_decision.v0.json"
)
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_AUTHORIZATION_DECISION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageARedirectRecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_exact_maintainer_message_is_bound(self):
        message = self.decision["maintainer_decision"]
        payload = message["message"].encode("utf-8")
        self.assertEqual(payload, b"continue, ")
        self.assertEqual(payload.hex(), message["utf8_hex"])
        self.assertEqual(len(payload), message["utf8_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), message["sha256"])
        self.assertTrue(message["interpreted_under_short_form_charter_rule"])

    def test_request_and_proof_are_green(self):
        request = self.decision["green_request"]
        proof = self.decision["green_request_proof"]
        self.assertEqual(request["commit"], "69527929cbe590cf4d8a83cfc68bbff9867c28c9")
        self.assertEqual(request["CI_run_id"], 32_783_593_146)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], "326c23a06888e2ee2787bc3c6feac98dfb6d747b")
        self.assertEqual(proof["CI_run_id"], 32_784_392_927)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_six_packet_artifacts_are_exact(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 19_038)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_delayed_effect_and_claim_boundary_are_closed(self):
        delayed = self.decision["delayed_effect"]
        self.assertTrue(all(value is False for value in delayed.values()))
        claims = self.decision["claim_boundary"]
        self.assertFalse(claims["scientific_claim_established"])
        self.assertFalse(claims["unseen_person_generalization"])
        self.assertFalse(claims["EEG_beyond_EOG"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering authority added", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
