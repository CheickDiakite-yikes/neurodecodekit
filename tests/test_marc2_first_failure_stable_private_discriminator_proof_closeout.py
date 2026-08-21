import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_result.v0.json"
)
PROOF_DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_FIRST_FAILURE_STABLE_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)
EXPECTED_PROOF = {
    "commit": "668812367acd8ca3ae9d0603dcde9b4b5aa02d58",
    "CI_run_id": 32_477_528_982,
    "base_python_job_id": 96_756_873_128,
    "optional_neuro_job_id": 96_756_873_357,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR18P-G1",
    "preproof_implementation_registry_bytes": 8_361,
    "preproof_implementation_registry_sha256": (
        "fe57de79cd7891f6d60b975bbe4373d5810b57c540c255335337414b08d5af50"
    ),
    "preproof_result_registry_bytes": 3_654,
    "preproof_result_registry_sha256": (
        "478d23e4f52646bb237e4ef6a38e65401c6315f84febc4c9c20a366f585db403"
    ),
    "qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2FirstFailureStablePrivateDiscriminatorProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.implementation["remote_implementation_proof"], EXPECTED_PROOF
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_PROOF)

    def test_owned_artifacts_match_current_proof_safe_worktree(self):
        artifacts = self.implementation["owned_artifacts"]
        self.assertEqual(len(artifacts), self.implementation["owned_artifact_count"])
        self.assertEqual(
            sum(artifact["bytes"] for artifact in artifacts),
            self.implementation["owned_artifact_bytes"],
        )
        for artifact in artifacts:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_closeout_binds_exact_preproof_git_blobs(self):
        text = PROOF_DOC_PATH.read_text(encoding="utf-8")
        for blob in (
            "c3d52b78c280a3ec5dafc70857eadb41b76602c4",
            "17725cdf19b514e7a76722139316747f90bac466",
            "2734e025b8e07c8b3036119e0aa3ea695bdc3ffb",
            "d4477735a21256e366b21b303978404453b223ee",
            "d3df4b78d3ab4b9b11af5645e32808bcef2c7c28",
            "23824ee5c47dba67a53b6b45dd9454c1f47a558b",
            "1dc288a355ead98a0ea27eef87f4448e82a7fbf4",
        ):
            self.assertIn(blob, text)

    def test_closeout_repeats_nothing_and_private_stage_is_delayed(self):
        self.assertFalse(
            EXPECTED_PROOF["qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        self.assertTrue(
            all(
                value == 0
                for value in self.implementation["operation_counters"].values()
            )
        )
        self.assertFalse(self.implementation["private_execution_authorized_now"])
        self.assertFalse(self.result["private_execution_authorized_now"])


if __name__ == "__main__":
    unittest.main()
