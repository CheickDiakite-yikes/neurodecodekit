import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/classical_eeg_adapter_contract.v0.json"
DOC_PATH = ROOT / "docs/CLASSICAL_EEG_ADAPTER_PREREGISTRATION.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ClassicalEegAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_plan_only_unimplemented_and_unexecuted(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_B_contract_only_not_implemented_not_executed",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["adapter_specification_and_plan_validation_only"])
        self.assertTrue(
            all(
                not value
                for key, value in scope.items()
                if key != "adapter_specification_and_plan_validation_only"
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_every_source_binding_matches_the_current_frozen_artifact(self):
        for source in self.contract["source_bindings"].values():
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])

    def test_three_complementary_adapters_are_exact_and_unselected(self):
        adapters = self.contract["adapter_families"]
        self.assertEqual(
            [row["adapter_id"] for row in adapters],
            [
                "fixed_low_frequency_shrinkage_lda",
                "fixed_8_to_30_hz_csp_lda",
                "regularized_riemannian_mdm",
            ],
        )
        self.assertEqual(adapters[0]["feature_contract"]["feature_dimensions_formula"], "5C")
        self.assertEqual(adapters[1]["feature_contract"]["CSP_components"], 4)
        self.assertEqual(adapters[2]["feature_contract"]["metric"], "riemann")
        selection = self.contract["selection_contract"]
        self.assertFalse(selection["winner_selected_now"])
        self.assertFalse(selection["protected_S20_selection_allowed"])
        self.assertFalse(selection["synthetic_fixture_selection_allowed"])
        self.assertEqual(selection["mandatory_future_comparator"], "train_only_no_signal_prior")

    def test_availability_is_bound_to_audit_without_install_or_fallback(self):
        status = {
            row["adapter_id"]: row["audited_local_status"]
            for row in self.contract["adapter_families"]
        }
        self.assertIn("substrate_available", status["fixed_low_frequency_shrinkage_lda"])
        self.assertIn("unavailable", status["fixed_8_to_30_hz_csp_lda"])
        self.assertIn("unavailable", status["regularized_riemannian_mdm"])
        dependency = self.contract["dependency_contract"]
        self.assertTrue(dependency["specification_module_standard_library_only"])
        self.assertFalse(dependency["base_dependencies_added"])
        self.assertFalse(dependency["optional_dependencies_installed_now"])
        self.assertFalse(dependency["adapter_imports_attempted_now"])
        self.assertFalse(dependency["silent_fallback_between_adapter_families"])

    def test_group_fit_and_evaluation_firewalls_are_fail_closed(self):
        split = self.contract["grouped_split_contract"]
        self.assertEqual(split["group_cross_partition_count_required"], 0)
        self.assertEqual(split["pair_cross_partition_count_required"], 0)
        self.assertFalse(split["row_level_random_split_allowed"])
        self.assertFalse(split["split_reassignment_after_any_label_or_outcome"])
        self.assertEqual(len(self.contract["fit_scope_contract"]), 6)
        self.assertTrue(
            all(
                "train_groups_only" in row["fit_scope"] or "data_independent" in row["fit_scope"]
                for row in self.contract["fit_scope_contract"]
            )
        )
        firewall = self.contract["evaluation_firewall"]
        self.assertTrue(
            all(
                value is False
                for key, value in firewall.items()
                if key != "forbidden_recursive_field_fragments"
            )
        )
        self.assertEqual(len(firewall["forbidden_recursive_field_fragments"]), 10)

    def test_plan_refusals_and_resource_caps_are_exact(self):
        fixture = self.contract["plan_fixture"]
        self.assertEqual(fixture["seed"], 5504)
        self.assertEqual(fixture["items"], 96)
        self.assertEqual(fixture["groups"], 48)
        self.assertEqual(fixture["partition_item_counts"], {"train": 48, "check": 32, "final": 16})
        self.assertEqual(fixture["partition_group_counts"], {"train": 24, "check": 16, "final": 8})
        refusals = self.contract["required_refusal_matrix"]
        self.assertEqual(len(refusals), 12)
        self.assertEqual(len(refusals), len(set(refusals)))
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["maximum_CPU_threads"], 1)
        self.assertEqual(caps["maximum_workers"], 1)
        self.assertEqual(caps["maximum_generated_output_bytes"], 1024 * 1024)

    def test_docs_and_tracker_preserve_claim_and_current_phase(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability if all gates pass", document)
        self.assertIn("Scientific claim not established", document)
        row = next(line for line in queue.splitlines() if line.startswith("| 4 |"))
        self.assertIn("| Complete |", row)
        self.assertIn("classical", row.lower())
        self.assertEqual(sum(line.startswith("| ") for line in queue.splitlines()), 21)


if __name__ == "__main__":
    unittest.main()
