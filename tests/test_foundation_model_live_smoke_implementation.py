import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/foundation_model_live_smoke_implementation.v0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FoundationModelLiveSmokeImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_implementation_is_hash_bound_and_not_executed(self):
        self.assertEqual(
            self.registry["status"],
            "implemented_locally_validated_not_executed_pending_remote_green",
        )
        for path_key, hash_key in (
            ("module_path", "module_sha256"),
            ("CLI_path", "CLI_sha256"),
            ("test_path", "test_sha256"),
            ("documentation_path", "documentation_sha256"),
        ):
            relative = self.registry["implementation_binding"][path_key]
            self.assertEqual(
                sha256(ROOT / relative),
                self.registry["implementation_binding"][hash_key],
            )
        state = self.registry["execution_state"]
        self.assertFalse(state["provider_invocation_started"])
        self.assertFalse(state["result_available"])
        self.assertFalse(state["stage_consumed"])
        self.assertFalse(state["rerun_authorized"])

    def test_provider_surface_is_exactly_the_authorized_terra_boundary(self):
        provider = self.registry["provider_request_contract"]
        self.assertEqual(provider["model_id"], "gpt-5.6-terra")
        self.assertEqual(provider["endpoint"], "https://api.openai.com/v1/responses")
        self.assertEqual(provider["reasoning_effort"], "low")
        self.assertEqual(provider["service_tier"], "default")
        self.assertFalse(provider["store"])
        self.assertFalse(provider["stream"])
        self.assertEqual(provider["tools"], [])
        self.assertEqual(provider["maximum_requests"], 12)
        self.assertEqual(provider["retry_count"], 0)
        self.assertEqual(provider["maximum_credential_reads"], 1)

    def test_no_irreversible_access_occurred_during_implementation(self):
        self.assertTrue(
            all(
                type(value) is int and value == 0
                for value in self.registry["current_access_counters"].values()
            )
        )
        privacy = self.registry["privacy_guards"]
        self.assertTrue(privacy["synthetic_blinded_structured_evidence_only"])
        for field in (
            "raw_EEG_or_MEG_allowed",
            "dense_embedding_or_NeuroToken_allowed",
            "target_reference_label_or_intended_text_allowed",
            "participant_identity_or_local_path_allowed",
        ):
            self.assertFalse(privacy[field])

    def test_document_preserves_remote_green_and_scientific_boundaries(self):
        document = (ROOT / self.registry["implementation_binding"]["documentation_path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("Execution remains", document)
        self.assertIn("CI is green for that exact commit", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("no provider call", document)
        acceptance = self.registry["precommit_acceptance"]
        self.assertTrue(acceptance["exact_implementation_commit_remote_green_required_before_execution"])
        self.assertFalse(acceptance["remote_green_passed"])


if __name__ == "__main__":
    unittest.main()
