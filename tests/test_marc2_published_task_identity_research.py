import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc2_published_task_identity_research.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2PublishedTaskIdentityResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_tier_a_boundary_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_published_task_identity_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR20R")
        self.assertIn("tier_A", self.record["status"])

    def test_bound_local_artifacts_are_current(self):
        for row in self.record["artifact_bindings"]:
            with self.subTest(path=row["path"]):
                path = ROOT / row["path"]
                self.assertEqual(path.stat().st_size, row["bytes"])
                self.assertEqual(sha256_file(path), row["sha256"])

    def test_public_dataset_identity_is_exact(self):
        source = self.record["public_source_identity"]
        self.assertEqual(source["figshare_record_id"], 28_632_599)
        self.assertEqual(source["figshare_file_id"], 57_518_986)
        self.assertEqual(source["archive_bytes"], 13_591_548_048)
        self.assertEqual(source["license"], "CC BY 4.0")
        self.assertEqual(source["published_task_label"], "reachingandgrasping")
        self.assertEqual(source["published_run_example"], "0003")
        self.assertEqual(len(source["raw_BIDS_suffixes"]), 4)

    def test_old_assumption_and_consumed_route_are_distinct(self):
        diagnosis = self.record["diagnosis"]
        self.assertEqual(diagnosis["old_required_task_label"], "freewill")
        self.assertEqual(diagnosis["published_task_label"], "reachingandgrasping")
        self.assertNotEqual(
            diagnosis["old_required_task_label"], diagnosis["published_task_label"]
        )
        self.assertEqual(diagnosis["consumed_route"], "MARC2VR18P-R4")
        self.assertEqual(diagnosis["generated_implication_route"], "MARC2VR19A-G1")
        self.assertTrue(diagnosis["public_root_cause_supported"])
        self.assertFalse(diagnosis["private_row_or_value_inspected"])

    def test_repair_requirements_preserve_source_exact_identity(self):
        repair = self.record["repair_requirements"]
        self.assertEqual(repair["required_task_label"], "reachingandgrasping")
        self.assertTrue(repair["source_exact_member_names_required"])
        self.assertTrue(repair["source_exact_run_spelling_required"])
        self.assertTrue(repair["four_companion_completeness_required"])
        self.assertTrue(repair["eight_GiB_reservation_cap_unchanged"])
        self.assertFalse(repair["modify_consumed_or_frozen_module_allowed"])

    def test_all_real_and_scientific_operations_are_zero(self):
        for value in self.record["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.record["operation_counters"].values():
            self.assertEqual(value, 0)
        boundary = self.record["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["neural_effect"])
        self.assertFalse(boundary["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
