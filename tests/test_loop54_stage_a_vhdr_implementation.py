import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.preprocess.vhdr_ledger import load_implementation_record


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/loop54_stage_a_vhdr_implementation.v0.json"
DOCUMENT_PATH = ROOT / "docs/LOOP_54_STAGE_A_VHDR_IMPLEMENTATION.md"
HISTORICAL_CLI_SHA256 = "370b6b1d27e2e0cb3550c3fe7bba9c39ac02f5f08867f447ff54292277b4cf65"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Loop54StageAVHDRImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_identity_status_contract_and_green_authorization_are_bound(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop54_stage_a_vhdr_implementation",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(
            registry["status"],
            "implemented_synthetic_qualified_pending_exact_commit_remote_green",
        )
        contract = registry["contract_binding"]
        self.assertEqual(contract["sha256"], sha256(ROOT / contract["path"]))
        authorization = registry["authorization_binding"]
        self.assertEqual(
            authorization["commit"],
            "2177b36f56464361bc51b2656406da7575ff1a1f",
        )
        self.assertEqual(authorization["push_CI_run_id"], 31286428489)
        self.assertEqual(authorization["base_python_job_id"], 93176025548)
        self.assertEqual(authorization["optional_neuro_readers_job_id"], 93176025560)
        self.assertTrue(authorization["all_required_jobs_green_before_implementation"])

    def test_owned_sources_are_hash_bound_and_shared_cli_preserves_commands(self):
        loaded = load_implementation_record(ROOT)
        self.assertEqual(loaded["schema_name"], self.registry["schema_name"])
        for name, binding in self.registry["implementation_binding"].items():
            if name == "CLI":
                self.assertEqual(binding["sha256"], HISTORICAL_CLI_SHA256)
                current = (ROOT / binding["path"]).read_text(encoding="utf-8")
                self.assertIn('"loop54-vhdr-ledger"', current)
                self.assertIn('"inspect-loop54-vhdr-ledger"', current)
            else:
                self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]), name)

    def test_parser_surfaces_and_all_refusals_are_implemented_without_base_dependency(self):
        surfaces = self.registry["implemented_surfaces"]
        self.assertEqual(surfaces["base_dependencies_added"], [])
        self.assertEqual(surfaces["dry_run_default_CLI_command"], "loop54-vhdr-ledger")
        self.assertEqual(
            surfaces["metadata_only_inspection_CLI_command"],
            "inspect-loop54-vhdr-ledger",
        )
        self.assertTrue(surfaces["twenty_two_refusal_classes"])
        self.assertTrue(surfaces["no_follow_one_open_one_read_source_verifier"])
        self.assertTrue(surfaces["exclusive_summary_then_ledger_commit_marker"])
        self.assertFalse(surfaces["generated_payload_committed"])
        self.assertFalse(surfaces["real_registered_execution_completed"])

    def test_synthetic_qualification_and_access_ledger_preserve_real_data_boundary(self):
        qualification = self.registry["synthetic_qualification"]
        self.assertEqual(qualification["focused_tests_passed"], 24)
        self.assertEqual(qualification["mutation_subtests_passed"], 24)
        self.assertEqual(qualification["registered_refusal_classes_covered"], 22)
        self.assertEqual(qualification["retained_synthetic_fixture_files"], 0)
        self.assertEqual(qualification["registered_S20_path_stats_or_reads"], 0)
        self.assertEqual(qualification["real_or_protected_bytes_read"], 0)
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        self.assertTrue(all(not value for value in self.registry["execution_gate"].values()))

    def test_resources_and_pending_execution_order_are_exact(self):
        resources = self.registry["resource_contract"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["registered_real_executions"], 1)
        self.assertEqual(resources["registered_VHDR_content_opens"], 1)
        self.assertEqual(resources["expected_input_bytes"], 11705)
        self.assertEqual(resources["maximum_read_bytes"], 16384)
        self.assertEqual(resources["maximum_generated_output_bytes"], 1024**2)
        self.assertFalse(
            self.registry["local_verification"]["measured_registered_execution_completed"]
        )

    def test_document_has_two_sentence_boundary_and_no_execution_claim(self):
        normalized = " ".join(self.document.split()).lower()
        for phrase in (
            "implemented and synthetic-qualified",
            "does not execute the registered s20 pass",
            "no preexisting path is read, followed, overwritten, deleted, or renamed",
            "engineering capability added:",
            "scientific claim not established:",
            "do not rerun, substitute, amend, or continue into loop 54-b",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
