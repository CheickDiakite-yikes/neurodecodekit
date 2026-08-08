import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "foundation_model_live_smoke_contract.v0.json"
DECISION_PATH = (
    REPO_ROOT / "registries" / "foundation_model_live_smoke_authorization_decision.v0.json"
)
DOC_PATH = REPO_ROOT / "docs" / "FOUNDATION_MODEL_LIVE_SMOKE_AUTHORIZATION_DECISION.md"


class FoundationModelLiveSmokeAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_decision_is_exactly_bound_to_the_green_contract(self):
        binding = self.decision["contract_binding"]
        self.assertEqual(
            binding["contract_sha256"],
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            binding["contract_commit"],
            "7db14d51cbe8bde5a5d7ac43479b20e575e9ae7c",
        )
        self.assertEqual(binding["contract_push_CI_run_id"], 31267860543)
        self.assertEqual(binding["contract_push_CI_conclusion"], "success")

    def test_exact_user_sentence_matches_the_frozen_request(self):
        self.assertEqual(
            self.decision["exact_authorization_text"],
            self.contract["exact_authorization_request"],
        )

    def test_authorization_matches_model_call_resource_and_spend_caps(self):
        auth = self.decision["authorization"]
        caps = self.contract["resource_caps"]
        provider = self.contract["provider_contract"]
        self.assertEqual(auth["maximum_invocations"], 1)
        self.assertEqual(auth["maximum_API_credential_reads"], 1)
        self.assertEqual(auth["maximum_external_network_calls"], 12)
        self.assertEqual(auth["maximum_provider_model_calls"], 12)
        self.assertEqual(auth["authorized_model_ids"], [provider["model_id"]])
        self.assertEqual(auth["authorized_endpoint"], provider["endpoint"])
        self.assertEqual(
            auth["maximum_estimated_standard_provider_charge_usd"],
            caps["maximum_standard_provider_charge_usd"],
        )
        self.assertTrue(auth["standard_service_only"])
        self.assertTrue(auth["no_tools"])
        self.assertTrue(auth["store_false"])
        self.assertTrue(auth["no_retries"])

    def test_every_access_counter_is_zero_at_decision(self):
        self.assertTrue(
            all(value == 0 for value in self.decision["access_counters_at_decision"].values())
        )
        self.assertFalse(self.decision["execution_started"])
        self.assertFalse(self.decision["result_available"])

    def test_doc_preserves_execution_order_and_claim_boundary(self):
        for phrase in (
            "Authorized; implementation and execution not started",
            "read `OPENAI_API_KEY` once",
            "consumed even if it fails or parks",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
