import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"


class NextScientificLoopsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_schema_and_exact_twenty_loop_range(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.next_scientific_loops",
        )
        self.assertEqual(self.registry["schema_version"], "0.3.0")
        self.assertEqual(self.registry["loop_range"], [45, 64])
        loops = self.registry["loops"]
        self.assertEqual(len(loops), 20)
        self.assertEqual([row["loop_id"] for row in loops], list(range(45, 65)))

    def test_five_phases_each_have_four_contiguous_loops(self):
        phases = self.registry["phases"]
        self.assertEqual(len(phases), 5)
        self.assertEqual([row["phase_id"] for row in phases], [f"P{i}" for i in range(6, 11)])
        for index, phase in enumerate(phases):
            start = 45 + index * 4
            self.assertEqual(phase["loop_ids"], list(range(start, start + 4)))
            self.assertTrue(phase["exit_gate"])

    def test_every_execution_and_global_authorization_is_false(self):
        self.assertTrue(all(not row["execution_authorized"] for row in self.registry["loops"]))
        authorization = self.registry["global_authorization"]
        self.assertEqual(len(authorization), 9)
        self.assertTrue(all(value is False for value in authorization.values()))

    def test_current_proof_boundary_keeps_consumed_and_final_sets_closed(self):
        boundary = self.registry["current_proof_boundary"]
        for key in (
            "positive_real_neural_advantage",
            "unseen_person_generalization",
            "real_time_end_to_end_decoding",
            "portable_or_home_hardware",
            "independent_reproduction",
            "scientific_replication",
        ):
            self.assertFalse(boundary[key])
        self.assertTrue(boundary["S21_session2_consumed_never_tune"])
        self.assertTrue(boundary["S21_session1_validation_consumed_never_rerun"])
        self.assertTrue(boundary["S7_EEG_consumed_never_tune"])
        self.assertTrue(boundary["S25_final_only_unopened"])

    def test_each_loop_has_complete_scientific_work_order(self):
        required = {
            "loop_id",
            "phase_id",
            "title",
            "priority",
            "status",
            "execution_authorized",
            "core_question",
            "scientific_claim_target",
            "build_deliverable",
            "data_scope",
            "controls",
            "primary_metrics",
            "acceptance_gate",
            "kill_or_park_rule",
            "depends_on",
            "future_resource_cap",
            "authorization_boundary",
        }
        for row in self.registry["loops"]:
            self.assertEqual(set(row), required, row["loop_id"])
            expected_status = {
                45: "Complete",
                46: "Parked; Registered Gate Failed",
                47: "Parked; Shared Attribution Gate Failed",
                48: "Preregistered; Authorization Pending",
            }.get(row["loop_id"], "Not Started")
            self.assertEqual(row["status"], expected_status)
            self.assertTrue(row["controls"])
            self.assertTrue(row["primary_metrics"])
            self.assertIn("authoriz", row["authorization_boundary"].lower())

    def test_critical_source_neural_gate_is_strict(self):
        loop46 = self.registry["loops"][1]
        self.assertEqual(loop46["loop_id"], 46)
        self.assertIn("2,908", loop46["core_question"])
        self.assertIn("0.05", loop46["acceptance_gate"])
        self.assertIn("p <= 0.05", loop46["acceptance_gate"])
        self.assertIn("881145d", loop46["authorization_boundary"])
        self.assertIn("0.938177", loop46["authorization_boundary"])
        self.assertIn("0.751235", loop46["authorization_boundary"])
        self.assertFalse(loop46["execution_authorized"])
        controls = " ".join(loop46["controls"])
        for term in ("no-signal", "zero-signal", "derangement", "displacement", "linear"):
            self.assertIn(term, controls)

        loop47 = next(row for row in self.registry["loops"] if row["loop_id"] == 47)
        self.assertIn("same shared Loop 46 scoring event", loop47["core_question"])
        self.assertIn("no post-Loop-46 target open", loop47["authorization_boundary"])
        self.assertIn("complete control conjunction failed", loop47["authorization_boundary"])
        self.assertFalse(loop47["execution_authorized"])

        loop48 = next(row for row in self.registry["loops"] if row["loop_id"] == 48)
        self.assertIn("loop48_failure_localization_contract.v0.json", loop48["build_deliverable"])
        self.assertIn("F5", loop48["build_deliverable"])
        self.assertIn("four exact committed", loop48["data_scope"])
        self.assertIn("<=30 seconds", loop48["future_resource_cap"])
        self.assertIn("Every authorization field is false", loop48["authorization_boundary"])
        self.assertFalse(loop48["execution_authorized"])

    def test_s25_is_final_only_with_zero_fit_and_strict_gate(self):
        loop51 = next(row for row in self.registry["loops"] if row["loop_id"] == 51)
        loop52 = next(row for row in self.registry["loops"] if row["loop_id"] == 52)
        self.assertIn("zero candidate fit rows", loop51["controls"])
        self.assertIn("zero calibration rows", loop51["controls"])
        self.assertIn("1,009,939,983", loop51["future_resource_cap"])
        self.assertIn(">=48", loop52["acceptance_gate"])
        self.assertIn(">=0.05", loop52["acceptance_gate"])
        self.assertIn("p <=0.05", loop52["acceptance_gate"])
        self.assertIn("consumed", loop52["kill_or_park_rule"])

    def test_eeg_home_and_device_claims_stay_separate(self):
        loop55 = next(row for row in self.registry["loops"] if row["loop_id"] == 55)
        loop58 = next(row for row in self.registry["loops"] if row["loop_id"] == 58)
        loop60 = next(row for row in self.registry["loops"] if row["loop_id"] == 60)
        self.assertIn("EEG sensor-signal", loop55["scientific_claim_target"])
        self.assertEqual(loop58["scientific_claim_target"], "device mechanics only")
        self.assertIn("never home text decoding", loop60["scientific_claim_target"])
        self.assertIn("battery-only", " ".join(loop60["controls"]))

    def test_reproduction_and_replication_are_separate(self):
        loop62 = next(row for row in self.registry["loops"] if row["loop_id"] == 62)
        loop63 = next(row for row in self.registry["loops"] if row["loop_id"] == 63)
        self.assertIn("author-artifact", loop62["scientific_claim_target"])
        self.assertEqual(
            loop63["scientific_claim_target"],
            "independent scientific replication",
        )
        self.assertIn("independent implementation", " ".join(loop63["controls"]))

    def test_sources_and_kill_branches_are_explicit(self):
        sources = self.registry["source_bindings"]
        self.assertEqual(len(sources), 10)
        self.assertEqual(len({row["source_id"] for row in sources}), 10)
        self.assertEqual(len(self.registry["cross_loop_kill_branches"]), 10)
        combined = " ".join(row["response"] for row in self.registry["cross_loop_kill_branches"])
        for term in ("S25", "negative", "neural", "release"):
            self.assertIn(term, combined)

    def test_human_roadmap_matches_machine_boundary(self):
        roadmap = (REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md").read_text(
            encoding="utf-8"
        )
        for loop_id in range(45, 65):
            self.assertIn(f"Loop {loop_id}", roadmap)
        self.assertIn("every experiment", roadmap)
        self.assertIn("unauthorized", roadmap)
        self.assertIn("S25 stays final-only", roadmap)


if __name__ == "__main__":
    unittest.main()
