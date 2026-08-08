import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "foundation_model_live_smoke_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "FOUNDATION_MODEL_LIVE_SMOKE_PREREGISTRATION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FoundationModelLiveSmokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_contract_is_fm1_preregistered_and_unexecuted(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.foundation_model_live_smoke_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["stage_id"], "FM-1")
        self.assertEqual(
            self.contract["status"],
            "preregistered_not_authorized_not_implemented_not_executed",
        )
        self.assertIn("Preregistered; not authorized", self.doc)

    def test_source_files_are_hash_bound_without_a_committed_plan(self):
        bindings = self.contract["source_bindings"]
        pairs = (
            ("strategy_path", "strategy_sha256"),
            ("strategy_registry_path", "strategy_registry_sha256"),
            ("FM0_fixture_path", "FM0_fixture_sha256"),
            ("FM0_implementation_registry_path", "FM0_implementation_registry_sha256"),
        )
        for path_key, hash_key in pairs:
            with self.subTest(path=bindings[path_key]):
                self.assertEqual(bindings[hash_key], sha256(REPO_ROOT / bindings[path_key]))
        self.assertEqual(bindings["FM0_plan_bytes"], 34349)
        self.assertEqual(bindings["FM0_item_count"], 3)
        self.assertEqual(bindings["FM0_condition_count"], 12)

    def test_provider_and_matrix_are_single_model_and_exactly_bounded(self):
        provider = self.contract["provider_contract"]
        matrix = self.contract["experiment_matrix"]
        self.assertEqual(provider["model_id"], "gpt-5.6-terra")
        self.assertEqual(provider["reasoning_effort"], "low")
        self.assertEqual(provider["service_tier"], "default")
        self.assertFalse(provider["store"])
        self.assertFalse(provider["stream"])
        self.assertEqual(provider["tools"], [])
        self.assertEqual(provider["retry_count"], 0)
        self.assertEqual(matrix["maximum_provider_requests"], 12)
        self.assertEqual(matrix["requests_per_condition"], 3)
        self.assertEqual(
            matrix["condition_ids"],
            ["FM-A00", "FM-A01", "FM-A02", "FM-A03"],
        )

    def test_resource_and_price_caps_are_small_and_consistent(self):
        caps = self.contract["resource_caps"]
        provider = self.contract["provider_contract"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["maximum_provider_requests"], 12)
        self.assertEqual(
            caps["maximum_total_output_tokens"],
            12 * provider["maximum_output_tokens_per_request"],
        )
        self.assertLessEqual(caps["maximum_generated_result_bytes"], 2 * 1024 * 1024)
        self.assertLessEqual(caps["maximum_standard_provider_charge_usd"], 0.5)
        self.assertEqual(
            self.contract["pricing_snapshot"][
                "short_context_input_usd_per_million_tokens"
            ],
            2.0,
        )

    def test_credential_and_protected_content_fail_closed(self):
        privacy = self.contract["credential_and_privacy"]
        self.assertEqual(privacy["credential_environment_variable"], "OPENAI_API_KEY")
        self.assertEqual(privacy["maximum_credential_reads"], 1)
        for field, value in privacy.items():
            if field.endswith("authorized") or field.endswith("persisted"):
                with self.subTest(field=field):
                    self.assertFalse(value)
        self.assertTrue(privacy["synthetic_blinded_structured_evidence_only"])

    def test_every_execution_authorization_remains_false(self):
        authorization = dict(self.contract["authorization"])
        self.assertTrue(authorization.pop("contract_documentation_tests_commit_and_push_authorized_now"))
        self.assertTrue(
            authorization.pop(
                "synthetic_fixture_only_implementation_tests_commit_and_push_authorized_now"
            )
        )
        self.assertTrue(all(value is False for value in authorization.values()))
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_doc_preserves_no_science_and_one_shot_boundary(self):
        for phrase in (
            "exactly 12, sequential",
            "retries:                   zero",
            "no provider call occurs",
            "Scientific claim not established:",
            "cannot establish decoding accuracy",
        ):
            self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
