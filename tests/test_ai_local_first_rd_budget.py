import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/ai_local_first_rd_budget.v0.json"


class AILocalFirstBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_allocations_equal_the_authorized_ceiling_without_forcing_spend(self):
        self.assertEqual(self.registry["aggregate_provider_budget_ceiling"], 50.0)
        self.assertTrue(self.registry["budget_is_ceiling_not_spend_target"])
        self.assertEqual(
            sum(row["ceiling_USD"] for row in self.registry["ceiling_allocations"]),
            50.0,
        )
        self.assertEqual(
            self.registry["conservative_remaining_portfolio_ceiling_USD"],
            49.5,
        )

    def test_FM1_is_conservatively_reserved_and_cannot_be_rerun(self):
        accounting = self.registry["FM1_accounting"]
        self.assertEqual(accounting["completed_response_local_estimate_USD"], 0.002394)
        self.assertFalse(accounting["third_attempt_usage_and_actual_charge_available"])
        self.assertEqual(accounting["conservative_reserved_ceiling_USD"], 0.5)
        self.assertFalse(accounting["FM1_rerun_authorized"])
        reserve = self.registry["ceiling_allocations"][0]
        self.assertEqual(reserve["lane_id"], "FM1_ACCOUNTING_RESERVE")
        self.assertFalse(reserve["may_fund_FM1_rerun"])

    def test_standing_scope_keeps_data_target_hardware_and_claim_gates_closed(self):
        scope = self.registry["standing_provider_scope"]
        self.assertTrue(
            scope[
                "synthetic_or_public_nonprotected_target_free_development_calls_under_committed_contract"
            ]
        )
        for field in (
            "protected_data_allowed",
            "target_or_reference_delivery_allowed",
            "raw_EEG_or_MEG_upload_allowed",
            "dense_embedding_or_NeuroToken_upload_allowed",
            "scientific_scoring_or_claim_upgrade_allowed",
            "hardware_purchase_connection_or_recording_allowed",
            "large_data_or_model_download_allowed",
            "release_allowed",
        ):
            self.assertFalse(scope[field])
        self.assertTrue(
            all(
                value == 0
                for value in self.registry["new_operations_during_budget_record"].values()
            )
        )

    def test_document_and_patent_boundary_reject_shipping_product_hype(self):
        binding = self.registry["documentation_binding"]
        document_path = ROOT / binding["path"]
        self.assertEqual(
            hashlib.sha256(document_path.read_bytes()).hexdigest(),
            binding["sha256"],
        )
        patent = self.registry["earbud_patent_boundary"]
        self.assertEqual(patent["publication"], "US20230225659A1")
        self.assertTrue(patent["earbud_form_electrode_selection_described"])
        self.assertTrue(patent["EEG_named_as_possible_biosignal"])
        self.assertFalse(patent["AirPods_term_present"])
        self.assertFalse(patent["shipping_product_proven"])
        self.assertFalse(patent["thought_to_text_proven"])
        document = document_path.read_text(encoding="utf-8")
        self.assertIn("pending patent application", document)
        self.assertIn("not evidence that current", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
