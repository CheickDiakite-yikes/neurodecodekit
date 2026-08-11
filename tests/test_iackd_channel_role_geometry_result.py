import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries" / "iackd_channel_role_geometry_result.v0.json"
DOCUMENT_PATH = ROOT / "docs" / "IACKD_CHANNEL_ROLE_GEOMETRY_RESULT.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDChannelRoleGeometryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_result_is_complete_consumed_R1_and_not_rerunnable(self):
        self.assertEqual(
            self.result["status"],
            "complete_consumed_IACKDR_R1_control_taxonomy_mismatch_no_rerun",
        )
        execution = self.result["execution"]
        self.assertEqual(execution["registered_execution_ordinal"], 1)
        self.assertTrue(execution["consumed"])
        self.assertFalse(execution["retry_allowed"])
        self.assertFalse(execution["rerun_allowed"])
        self.assertEqual(self.result["diagnosis"]["diagnostic_route"], "IACKDR-R1")

    def test_remote_green_chain_preceded_the_real_audit(self):
        proof = self.result["green_proof_chain"]
        expected = {
            "registration": (
                "228ccd03f5e0b5d02ba104e13b77b04f2032df78",
                31_427_931_578,
            ),
            "implementation": (
                "9f6fef9540ae0a1fe52cbf24b17b0af89147beae",
                31_430_151_368,
            ),
            "request": (
                "86174bc86123bc010bac2f40a9d72147dc8aef05",
                31_431_064_259,
            ),
            "decision": (
                "f6eb5ab650a0232a17d2f8f56c582c90bf0cf420",
                31_444_154_297,
            ),
        }
        for name, (commit, ci_run) in expected.items():
            with self.subTest(name=name):
                self.assertEqual(proof[name]["commit"], commit)
                self.assertEqual(proof[name]["push_CI_run_id"], ci_run)
                self.assertTrue(proof[name]["both_required_jobs_green"])

    def test_execution_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_objects"], 316)
        self.assertEqual(measured["input_bytes"], 457_602)
        self.assertEqual(measured["network_body_bytes"], 457_602)
        self.assertEqual(measured["body_SHA256_passes"], 316)
        self.assertEqual(measured["semantic_parse_passes"], 316)
        self.assertEqual(measured["generated_output_bytes"], 9_779)
        self.assertEqual(measured["retained_generated_bytes"], 10_027)
        self.assertLess(measured["runtime_seconds"], 180)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertIsNone(measured["producer_is_causal"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_source_declares_one_26_channel_predictive_core(self):
        diagnosis = self.result["diagnosis"]
        self.assertEqual(diagnosis["predictive_EEG_count"], 26)
        self.assertEqual(diagnosis["core_schema_count"], 1)
        self.assertEqual(
            [(row["occurrence_count"], row["row_count"]) for row in diagnosis["channel_schema_groups"]],
            [(96, 29), (32, 31)],
        )
        self.assertEqual(diagnosis["reference_values"], ["average"])

    def test_R1_is_exactly_the_two_control_taxonomy_failures(self):
        reconciliation = self.result["diagnosis"]["H1_reconciliation"]
        false_fields = {name for name, value in reconciliation.items() if value is False}
        self.assertEqual(
            false_fields,
            {
                "all_source_agreement_checks_pass",
                "present_sidecar_type_counts_reconcile",
                "required_control_BIDS_roles_valid",
            },
        )
        controls = self.result["diagnosis"]["control_taxonomy"]
        self.assertEqual(controls["source_types"], {"HEOG": "MISC", "VEOG": "MISC", "Trigger": "MISC"})
        self.assertEqual(
            controls["sidecar_counts"],
            {"EOGChannelCount": 0, "MiscChannelCount": 3, "TriggerChannelCount": 0},
        )
        self.assertFalse(controls["frozen_role_map_candidate_admissible"])

    def test_geometry_is_complete_for_all_30_groups(self):
        geometry = self.result["diagnosis"]["geometry"]
        self.assertEqual(geometry["groups_total"], 30)
        self.assertEqual(geometry["central_groups_complete"], 30)
        self.assertEqual(geometry["occipital_groups_complete"], 30)
        self.assertEqual(geometry["predictive_EEG_geometry_coverage_count"], 26)
        self.assertEqual(
            [(row["occurrence_count"], row["electrode_count"], row["finite_coordinate_count"]) for row in geometry["signature_groups"]],
            [(22, 29, 26), (8, 31, 28)],
        )

    def test_every_execution_and_safety_gate_has_expected_outcome(self):
        gates = self.result["acceptance_gate_results"]
        self.assertEqual(len(gates), 9)
        self.assertFalse(
            gates["all_128_channel_tables_and_sidecars_and_30_geometry_pairs_reconcile"]
        )
        for name, value in gates.items():
            if name == "all_128_channel_tables_and_sidecars_and_30_geometry_pairs_reconcile":
                continue
            self.assertTrue(value, name)

    def test_only_authorized_metadata_counters_are_nonzero(self):
        counters = self.result["access_counters"]
        allowed = {
            "real_metadata_requests": 316,
            "real_metadata_body_bytes": 457_602,
            "real_metadata_parses": 316,
        }
        for name, value in counters.items():
            self.assertEqual(value, allowed.get(name, 0), name)

    def test_public_result_has_no_individual_identity_or_path(self):
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("sub-", serialized)
        self.assertNotIn(".tsv", serialized.lower())
        self.assertFalse(self.result["public_artifact_bindings"]["contains_local_path"])
        self.assertFalse(
            self.result["public_artifact_bindings"]["contains_individual_identity_or_outcome"]
        )

    def test_public_artifact_hashes_and_claim_language_are_current(self):
        bindings = self.result["public_artifact_bindings"]
        self.assertEqual(bindings["document_sha256"], sha256(DOCUMENT_PATH))
        self.assertEqual(bindings["invariant_test_sha256"], sha256(Path(__file__)))
        compact = " ".join(self.document.split())
        self.assertIn("Engineering capability added:", compact)
        self.assertIn("Scientific claim not established:", compact)
        self.assertIn("control-taxonomy mismatch", compact)
        self.assertIn("no neural effect", compact)


if __name__ == "__main__":
    unittest.main()
