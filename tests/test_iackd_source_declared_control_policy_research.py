import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "iackd_source_declared_control_policy_research.v0.json"
)
DOCUMENT_PATH = ROOT / "docs" / "IACKD_SOURCE_DECLARED_CONTROL_POLICY_RESEARCH.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


class IACKDSourceDeclaredControlPolicyResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_research_is_artifact_only_and_prospective(self):
        self.assertEqual(self.registry["lane_id"], "IACKD-H3")
        self.assertEqual(
            self.registry["status"],
            "planning_complete_artifact_only_prospective_policy_no_real_execution",
        )
        self.assertFalse(self.registry["authorization"]["real_reader_authorized"])
        self.assertFalse(self.registry["authorization"]["IACKD2_authorized"])

    def test_green_H2_result_is_the_only_dataset_specific_input(self):
        evidence = self.registry["evidence_inputs"]
        self.assertEqual(
            evidence["H2_result_commit"],
            "580f11fc60d2882a11bf4e765bb33b60ffc0bd04",
        )
        self.assertEqual(evidence["H2_result_CI_run_id"], 31_444_931_063)
        self.assertEqual(
            evidence["H2_result_registry_sha256"],
            "e6f0665aa5eb822f64c8575ea5931c2fdcebda1e85156e0971b0ff1387158715",
        )
        self.assertEqual(evidence["Git_ignored_execution_artifacts_read"], 0)

    def test_candidate_policy_hash_is_canonical(self):
        self.assertEqual(
            self.registry["candidate_policy_sha256"],
            canonical_sha256(self.registry["candidate_policy"]),
        )
        self.assertNotEqual(
            self.registry["candidate_policy_sha256"],
            "435352a007a0def493f90a99550a1943ba7debbf0f4b0e75316ac480b908822d",
        )

    def test_source_types_roles_and_model_inclusion_are_separate(self):
        policy = self.registry["candidate_policy"]
        self.assertEqual(
            policy["semantic_layers"],
            ["source_type", "functional_role", "model_inclusion"],
        )
        self.assertEqual(
            policy["source_count_reconciliation"],
            "count_exact_source_type_before_functional_role_assignment",
        )
        self.assertFalse(policy["functional_role_may_rewrite_source_type_count"])

    def test_predictive_core_is_exact_and_controls_are_nonpredictive(self):
        rules = self.registry["candidate_policy"]["role_rules"]
        predictive = rules[0]
        self.assertEqual(predictive["functional_role"], "predictive_eeg")
        self.assertEqual(len(predictive["source_names"]), 26)
        self.assertTrue(predictive["model_inclusion"])
        self.assertEqual(predictive["source_type"], "EEG")
        for rule in rules[1:]:
            self.assertFalse(rule["model_inclusion"], rule["functional_role"])
        self.assertEqual(rules[2]["source_type"], "MISC")
        self.assertEqual(rules[3]["source_type"], "MISC")

    def test_two_source_count_groups_are_preserved_without_name_reclassification(self):
        groups = self.registry["candidate_policy"]["source_count_groups"]
        self.assertEqual(
            [(row["occurrence_count"], row["EEG"], row["MISC"], row["total_rows"]) for row in groups],
            [(96, 26, 3, 29), (32, 28, 3, 31)],
        )
        self.assertEqual(
            self.registry["candidate_policy"]["trigger_source_count_bucket"], "MISC"
        )

    def test_geometry_and_reference_requirements_are_exact(self):
        policy = self.registry["candidate_policy"]
        self.assertEqual(policy["sampling_frequency_hz"], 1024)
        self.assertEqual(policy["reference"], "average")
        self.assertEqual(policy["coordinate_system"], "CapTrak")
        self.assertEqual(policy["coordinate_units"], "m")
        self.assertEqual(
            policy["required_regional_views"],
            {"central": ["C3", "C4", "Cz"], "occipital": ["O1", "Oz", "O2"]},
        )

    def test_every_access_counter_is_zero(self):
        for name, value in self.registry["access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_next_qualification_is_bounded_and_synthetic_only(self):
        qualification = self.registry["next_bounded_qualification"]
        self.assertEqual(qualification["real_or_public_data_reads"], 0)
        self.assertEqual(qualification["network_requests"], 0)
        self.assertEqual(qualification["CPU_threads"], 1)
        self.assertLessEqual(qualification["wall_time_seconds"], 30)
        self.assertLessEqual(qualification["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLessEqual(qualification["generated_output_bytes"], 2 * 1024 * 1024)

    def test_document_hash_and_claim_boundary_are_current(self):
        self.assertEqual(
            self.registry["public_artifact_bindings"]["document_sha256"],
            sha256(DOCUMENT_PATH),
        )
        compact = " ".join(self.document.split())
        self.assertIn("Engineering capability proposed:", compact)
        self.assertIn("Scientific claim not established:", compact)
        self.assertIn("source type", compact)
        self.assertIn("functional role", compact)


if __name__ == "__main__":
    unittest.main()
