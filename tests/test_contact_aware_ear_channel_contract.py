import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/contact_aware_ear_channel_contract.v0.json"
DOC_PATH = ROOT / "docs/CONTACT_AWARE_EAR_CHANNEL_PREREGISTRATION.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContactAwareEarChannelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_synthetic_only_unimplemented_and_unexecuted(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_B_synthetic_only_not_implemented_not_executed",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["generic_post_acquisition_channel_adapter_only"])
        self.assertTrue(scope["synthetic_fixture_generation_and_validation_only"])
        self.assertTrue(
            all(
                value is False
                for key, value in scope.items()
                if key
                not in {
                    "generic_post_acquisition_channel_adapter_only",
                    "synthetic_fixture_generation_and_validation_only",
                }
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_every_source_binding_matches_exactly(self):
        for source in self.contract["source_bindings"].values():
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])

    def test_primary_sources_support_direction_without_product_claim(self):
        sources = {row["source_id"]: row for row in self.contract["primary_source_boundaries"]}
        self.assertEqual(len(sources), 4)
        patent = sources["US20230225659A1"]
        self.assertIn("dynamic_subset_selection_based_on_impedance_or_noise", patent["supports"])
        self.assertIn("current_AirPods_EEG_capability", patent["does_not_support"])
        openbci = sources["OpenBCI_cEEGrid_documentation"]
        self.assertIn("concrete_16_channel_around_the_ear_research_surface", openbci["supports"])

    def test_fixture_inventory_and_geometry_boundary_are_exact(self):
        fixture = self.contract["synthetic_fixture"]
        self.assertEqual(fixture["seed"], 5505)
        self.assertEqual(fixture["items"], 48)
        self.assertEqual(fixture["channels"], 16)
        self.assertEqual(fixture["channels_per_side"], 8)
        self.assertEqual(fixture["samples_per_item"], 256)
        self.assertEqual(fixture["sampling_rate_hz"], 128.0)
        self.assertEqual(len(fixture["scenario_ids"]), 8)
        self.assertEqual(fixture["scenario_item_count"], 6)
        self.assertIn("not_measured_not_anatomical", fixture["geometry_provenance"])

    def test_masks_selection_and_causality_are_fail_closed(self):
        arrays = self.contract["array_contract"]
        for name in (
            "observed_mask",
            "channel_present_mask",
            "contact_score_valid_mask",
            "eligible_mask",
            "selected_mask",
            "adapted_observed_mask",
        ):
            self.assertIn(name, arrays)
        policy = self.contract["quality_and_selection_policy"]
        self.assertFalse(policy["policy_fit_or_learning"])
        self.assertEqual(policy["maximum_selected_channels_per_side"], 4)
        self.assertEqual(policy["minimum_selected_channels_per_side"], 2)
        self.assertTrue(policy["bilateral_minimum_required"])
        self.assertEqual(policy["unknown_contact_action"], "ineligible")
        self.assertEqual(policy["selected_weight_total_left"], 0.5)
        self.assertEqual(policy["selected_weight_total_right"], 0.5)
        causality = self.contract["causality_contract"]
        self.assertEqual(causality["required_right_context_samples"], 0)
        self.assertEqual(causality["post_event_samples"], 0)
        self.assertTrue(causality["future_tail_prefix_invariance_required"])

    def test_refusals_resources_dependencies_and_authorization_are_exact(self):
        refusals = self.contract["required_refusal_matrix"]
        self.assertEqual(len(refusals), 16)
        self.assertEqual(len(refusals), len(set(refusals)))
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["maximum_CPU_threads"], 1)
        self.assertEqual(caps["maximum_workers"], 1)
        self.assertEqual(caps["maximum_generated_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(caps["maximum_network_bytes"], 0)
        dependency = self.contract["dependency_contract"]
        self.assertEqual(dependency["implementation_optional_extra"], "array")
        self.assertTrue(dependency["implementation_requires_only_numpy"])
        self.assertFalse(dependency["optional_dependency_install_allowed_now"])
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["tier_B_lazy_numpy_synthetic_implementation_allowed_after_contract_green"])
        self.assertFalse(authorization["real_public_or_protected_data_access_allowed"])
        self.assertFalse(authorization["physical_electrode_switching_or_hardware_allowed"])

    def test_docs_and_tracker_preserve_claim_and_current_phase(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability if all gates pass", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("does not control electrodes", " ".join(document.split()))
        row = next(line for line in queue.splitlines() if line.startswith("| 5 |"))
        self.assertIn("| Complete |", row)
        self.assertIn("ear-channel", row.lower())
        self.assertEqual(sum(line.startswith("| ") for line in queue.splitlines()), 21)


if __name__ == "__main__":
    unittest.main()
