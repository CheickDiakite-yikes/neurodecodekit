import copy
import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_variable_width_run_index_repair as vr16a


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_published_task_selector_repair_contract.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_PUBLISHED_TASK_SELECTOR_REPAIR_PREREGISTRATION.md"


def _published_source() -> dict:
    source = vr16a.build_generated_variant("three_digit", "canonical")
    for row in source["entries"]:
        name = row.get("member_name") if isinstance(row, dict) else None
        if not isinstance(name, str) or vr16a._variable_core_match(name) is None:
            continue
        name = name.replace("_task-freewill_", "_task-reachingandgrasping_")
        match = vr16a._variable_core_match(name)
        assert match is not None
        row["member_name"] = vr16a._replace_match_run(
            name, match, match.group("run").zfill(4)
        )
    return source


class Marc2PublishedTaskSelectorRepairPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_research_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR20A")
        proof = self.contract["green_research_proof"]
        self.assertEqual(
            proof["commit"], "d5556d6b530f076742a3614c80e96606fc452560"
        )
        self.assertEqual(proof["CI_run_id"], 32_483_267_516)
        self.assertEqual(proof["base_python_job_id"], 96_774_089_213)
        self.assertEqual(proof["optional_neuro_job_id"], 96_774_089_325)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["private_or_dataset_payload_operations"], 0)

    def test_fixed_inputs_match_size_and_sha256(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), self.contract["fixed_input_count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows), self.contract["fixed_input_bytes"]
        )
        for row in rows:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_primary_source_and_repair_identity_are_exact(self):
        source = self.contract["primary_source_binding"]
        self.assertEqual(source["descriptor_DOI"], "10.1038/s41597-025-06039-9")
        self.assertEqual(source["figshare_version"], 1)
        self.assertEqual(source["published_task_label"], "reachingandgrasping")
        self.assertEqual(source["published_run_example"], "0003")
        self.assertEqual(len(source["raw_BIDS_suffixes"]), 4)

        repair = self.contract["frozen_repair"]
        self.assertEqual(repair["required_task_label"], "reachingandgrasping")
        self.assertFalse(
            repair["task_alias_casefold_prefix_suffix_or_heuristic_allowed"]
        )
        self.assertTrue(repair["published_four_digit_run_success_required"])
        self.assertTrue(repair["source_exact_member_names_required"])
        self.assertFalse(repair["source_or_selected_rows_rewritten"])
        self.assertFalse(repair["private_execute_surface_allowed"])

    def test_published_fixture_hits_only_the_known_old_task_guard(self):
        source = _published_source()
        before = copy.deepcopy(source)
        core = [
            row["member_name"]
            for row in source["entries"]
            if isinstance(row, dict)
            and vr16a._variable_core_match(row.get("member_name", "")) is not None
        ]
        self.assertEqual(len(core), 952)
        self.assertTrue(all("task-reachingandgrasping" in name for name in core))
        self.assertTrue(all("_run-000" in name for name in core))
        with self.assertRaises(vr16a.VariableWidthRunIndexRepairRefusal) as caught:
            vr16a.adapt_variable_width_source(source)
        self.assertEqual(caught.exception.route, vr16a.REFUSAL_ROUTES[3])
        self.assertEqual(source, before)

    def test_matrix_and_resources_are_bounded(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["success_variants"]), 5)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_success_paths"], 20)
        self.assertGreaterEqual(len(matrix["required_refusal_witnesses"]), 19)
        self.assertEqual(self.contract["direct_refusal_minimum"], 50)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 32 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)

    def test_authority_and_claim_boundary_are_closed(self):
        self.assertTrue(
            all(value is False for value in self.contract["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        gate = self.contract["implementation_gate"]
        self.assertTrue(gate["this_registration_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["private_confirmation_packet_allowed_now"])
        self.assertFalse(gate["private_or_neural_execution_authorized"])
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_sought", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_document_preserves_stop_and_claim_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("20 success paths", text)
        self.assertIn("source member names", text)
        self.assertIn("Do not open or list `.codex_work`", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
