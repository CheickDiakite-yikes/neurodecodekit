from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries"
    / "communication_live_session_g0_registration_proof.v0.json"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


class CommunicationLiveSessionG0RegistrationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_remote_proof_is_exact_and_green(self) -> None:
        self.assertEqual(
            self.proof["registration_commit"],
            "fb69324262b27ba9d8f0db1b42725e438c29d385",
        )
        remote = self.proof["remote_proof"]
        self.assertEqual(remote["CI_run_id"], 33104044102)
        self.assertEqual(remote["CI_conclusion"], "success")
        self.assertEqual(remote["head_sha"], self.proof["registration_commit"])
        self.assertEqual(
            [(job["name"], job["job_id"], job["conclusion"]) for job in remote["jobs"]],
            [
                ("Base Python", 98629017931, "success"),
                ("Optional Neuro Readers", 98629018115, "success"),
            ],
        )

    def test_bound_artifacts_are_byte_exact(self) -> None:
        artifacts = self.proof["artifacts"]
        self.assertEqual(len(artifacts), self.proof["artifact_count"])
        self.assertEqual(
            sum(artifact["bytes"] for artifact in artifacts),
            self.proof["artifact_bytes_total"],
        )
        for artifact in artifacts:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifact["sha256"],
                artifact["path"],
            )
        self.assertEqual(
            hashlib.sha256(_canonical_bytes(artifacts)).hexdigest(),
            self.proof["canonical_artifact_set_sha256"],
        )

    def test_effect_is_narrow_and_delayed(self) -> None:
        effect = self.proof["effect"]
        self.assertTrue(effect["RW3_stage_A_SourceChunk_implementation_authorized"])
        self.assertTrue(effect["RW3_stage_A_synthetic_fixture_generation_authorized"])
        self.assertTrue(effect["generated_LiveSession_implementation_authorized"])
        self.assertFalse(effect["generated_qualification_authorized_now"])
        self.assertTrue(
            effect[
                "generated_qualification_requires_implementation_commit_push_and_both_jobs_green"
            ]
        )
        self.assertFalse(effect["later_RW3_adapter_stage_authorized"])

    def test_nonoperation_and_claim_boundary_are_honest(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.proof["operation_counters"].values())
        )
        claims = self.proof["claim_boundary"]
        self.assertTrue(claims["engineering_registration_proven"])
        for key, value in claims.items():
            if key != "engineering_registration_proven":
                self.assertFalse(value, key)
        self.assertTrue(self.proof["active_gate"]["all_authority_flags_false"])

    def test_frontier_matches_proof(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        live = frontier["parallel_tier_A_communication_program"][
            "generated_live_session_preregistration"
        ]
        self.assertEqual(live["status"], "registration_remotely_green")
        self.assertEqual(live["registration_commit"], self.proof["registration_commit"])
        self.assertEqual(live["registration_CI_run_id"], 33104044102)
        self.assertTrue(live["both_required_jobs_green"])
        self.assertTrue(live["generated_implementation_authorized_now"])
        self.assertFalse(live["generated_qualification_authorized_now"])


if __name__ == "__main__":
    unittest.main()
