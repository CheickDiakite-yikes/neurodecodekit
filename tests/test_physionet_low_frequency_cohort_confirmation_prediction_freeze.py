import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_prediction_freeze.v0.json"
)
CONTRACT_PATH = (
    ROOT / "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT / "registries/physionet_low_frequency_cohort_confirmation_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREDICTION_FREEZE.md"
EXPECTED_FILE_SHA256 = "6a546ca32a92b35c9c3448cecb5831f926d02f519a563d2ad803944c8d1f487a"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyPredictionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_freeze_is_exact_hash_locked_and_canonical(self):
        self.assertEqual(sha256(FREEZE_PATH), EXPECTED_FILE_SHA256)
        payload = dict(self.freeze)
        expected = payload.pop("freeze_record_sha256")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(expected, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(
            self.freeze["contract_sha256"],
            "ce0dcf5e5ddd598fb69b5baa73f827bbc3f51c4aeab8578d2d2eebda87cd0935",
        )

    def test_green_implementation_binding_is_exact(self):
        self.assertEqual(
            self.freeze["implementation_commit"],
            "8242674e5821b2c923c0c79baa3a6ea20a27d838",
        )
        self.assertEqual(self.freeze["implementation_ci_run_id"], 31359548779)
        self.assertEqual(self.freeze["implementation_base_python_job_id"], 93365527795)
        self.assertEqual(self.freeze["implementation_optional_neuro_job_id"], 93365527849)
        self.assertEqual(self.freeze["implementation_registry_sha256"], sha256(IMPLEMENTATION_PATH))

    def test_complete_prediction_hash_inventory_has_no_individual_outputs(self):
        expected_conditions = tuple(
            row["condition_id"]
            for row in self.contract["prediction_contract"]["conditions"]
        )
        self.assertEqual(tuple(self.freeze["condition_ids"]), expected_conditions)
        participants = set(self.contract["dataset_binding"]["participants"])
        hashes = self.freeze["prediction_set_sha256"]
        self.assertEqual(set(hashes), set(self.freeze["condition_ids"]))
        self.assertEqual(sum(len(rows) for rows in hashes.values()), 216)
        for rows in hashes.values():
            self.assertEqual(set(rows), participants)
            for value in rows.values():
                self.assertRegex(value, r"^[0-9a-f]{64}$")
        for forbidden in ("predictions", "targets", "probabilities", "participant_outcomes"):
            self.assertNotIn(forbidden, self.freeze)
        self.assertFalse(self.freeze["target_firewall"]["individual_outputs_committed"])

    def test_counts_firewall_and_resources_are_within_contract(self):
        counters = self.freeze["operation_counters"]
        self.assertEqual(counters["parameter_update_fits"], 144)
        self.assertEqual(counters["target_blind_model_inference_runs"], 216)
        self.assertEqual(counters["participant_condition_prediction_sets"], 216)
        self.assertEqual(counters["individual_predictions"], 3240)
        self.assertEqual(counters["final_target_rows_available_to_model_stage"], 0)
        self.assertEqual(counters["scoring_events"], 0)
        firewall = self.freeze["target_firewall"]
        self.assertEqual(firewall["fit_target_rows_available"], 720)
        self.assertEqual(firewall["final_signal_rows_available"], 360)
        self.assertEqual(firewall["final_target_rows_available_to_model_stage"], 0)
        self.assertTrue(firewall["both_final_target_sets_frozen_together"])
        self.assertFalse(firewall["prediction_derivative_contains_targets"])
        resources = self.freeze["resources_through_freeze"]
        caps = self.contract["resource_caps"]["analysis_and_scoring"]
        self.assertLessEqual(resources["runtime_seconds"], caps["wall_time_seconds_through_prediction_freeze"])
        self.assertLessEqual(resources["peak_rss_bytes"], caps["peak_rss_bytes"])
        self.assertLessEqual(resources["generated_private_bytes"], caps["private_generated_bytes"])
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)

    def test_freeze_is_not_a_scientific_result(self):
        self.assertEqual(self.freeze["source_kind"], "real_physionet")
        self.assertEqual(self.freeze["source_file_count"], 72)
        self.assertEqual(self.freeze["source_payload_bytes"], 184252032)
        self.assertEqual(
            self.freeze["status"],
            "all_run11_and_run12_predictions_frozen_targets_not_delivered",
        )
        self.assertEqual(
            self.freeze["claim_boundary"]["current"],
            "prediction_hashes_only_no_scientific_result",
        )
        document = " ".join(DOC_PATH.read_text(encoding="utf-8").split())
        self.assertIn("Scientific claim not established", document)
        self.assertIn("no final target has been delivered or scored", document)
        self.assertIn("no task accuracy", document)


if __name__ == "__main__":
    unittest.main()
