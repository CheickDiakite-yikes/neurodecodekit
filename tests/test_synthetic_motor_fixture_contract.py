import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/synthetic_motor_fixture_contract.v0.json"
DOC_PATH = ROOT / "docs/SYNTHETIC_MOTOR_FIXTURE_PREREGISTRATION.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
CML_PATH = ROOT / "registries/loop55_causal_motor_lattice_research.v0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyntheticMotorFixtureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.cml = json.loads(CML_PATH.read_text(encoding="utf-8"))

    def test_registration_is_fixture_only_and_unexecuted(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_B_fixture_only_not_implemented_not_executed",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["fixture_generation_only"])
        self.assertTrue(all(not value for key, value in scope.items() if key != "fixture_generation_only"))
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_every_source_is_hash_bound(self):
        for source in self.contract["source_bindings"].values():
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])

    def test_factor_families_match_the_frozen_research_recommendation(self):
        registered = [row["factor_id"] for row in self.contract["factor_families"]]
        expected = self.cml["synthetic_factor_isolation_gate"]["factor_families"]
        self.assertEqual(registered, expected)
        self.assertEqual(len(registered), len(set(registered)))

    def test_pairs_partitions_shapes_and_synthetic_identity_are_exact(self):
        identity = self.contract["fixture_identity"]
        self.assertEqual(identity["seed"], 5503)
        self.assertEqual(identity["item_count"], 96)
        self.assertEqual(identity["partition_counts"], {"train": 48, "check": 32, "final": 16})
        self.assertTrue(identity["pair_members_must_share_partition"])
        self.assertEqual(identity["channel_names"], [f"SYN{index:02d}" for index in range(8)])
        self.assertTrue(identity["channel_identity_is_synthetic_not_anatomical"])
        self.assertEqual(self.contract["required_arrays"]["signals"]["shape"], [96, 8, 256])

    def test_mutations_resources_and_optional_dependencies_are_bounded(self):
        mutations = [row["mutation_id"] for row in self.contract["mutation_contract"]]
        self.assertEqual(len(mutations), 8)
        self.assertEqual(len(mutations), len(set(mutations)))
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["maximum_cpu_threads"], 1)
        self.assertEqual(caps["maximum_workers"], 1)
        self.assertEqual(caps["maximum_generated_output_bytes"], 4 * 1024 * 1024)
        deps = self.contract["dependency_contract"]
        self.assertFalse(deps["base_dependencies_added"])
        self.assertTrue(deps["imports_must_be_lazy"])
        self.assertFalse(deps["network_install_or_runtime_fetch_allowed"])

    def test_privacy_authorization_and_claim_ceiling_fail_closed(self):
        privacy = self.contract["privacy_and_leakage"]
        self.assertFalse(privacy["target_reference_intended_or_prompt_text_created_or_read"])
        self.assertFalse(privacy["real_channel_names_created_or_read"])
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["tier_B_fixture_implementation_and_bounded_synthetic_replay_allowed"])
        for field in (
            "CML_architecture_implementation_allowed_by_this_contract",
            "parameter_update_model_inference_or_scoring_allowed",
            "real_public_or_protected_data_access_allowed",
            "download_network_provider_stream_device_or_hardware_allowed",
            "scientific_claim_upgrade_allowed",
        ):
            self.assertFalse(authorization[field], field)
        self.assertIn("Scientific claim not established", DOC_PATH.read_text(encoding="utf-8"))

    def test_execution_queue_keeps_work_order_three_in_progress(self):
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        row = next(line for line in queue.splitlines() if line.startswith("| 3 |"))
        self.assertIn("In Progress", row)
        self.assertIn("synthetic", row.lower())


if __name__ == "__main__":
    unittest.main()
