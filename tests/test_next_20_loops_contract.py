import json
import re
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
LOOP24_PATH = REPO_ROOT / "registries" / "local_precision_runtime_contract.v0.json"
RW3_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
RW3_REQUEST_PATH = REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"


class NextTwentyLoopsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.loops = cls.roadmap["loops"]

    def test_identity_range_and_planning_boundary_are_exact(self):
        roadmap = self.roadmap
        self.assertEqual(
            roadmap["schema_name"], "neurodecodekit.next_twenty_loops_roadmap"
        )
        self.assertEqual(roadmap["schema_version"], "0.1.0")
        self.assertEqual(roadmap["roadmap_id"], "loops-25-44")
        self.assertEqual(roadmap["status"], "planning_only_not_execution_authorization")
        self.assertEqual(
            roadmap["range"],
            {"first_loop": 25, "last_loop": 44, "loop_count": 20},
        )
        boundary = roadmap["current_boundary"]
        self.assertEqual(boundary["current_numbered_gate"], 24)
        self.assertFalse(boundary["loop24_execution_authorized"])
        self.assertFalse(boundary["rw3_stage_a_authorized"])
        self.assertFalse(boundary["general_continuation_is_authorization"])
        self.assertFalse(boundary["roadmap_approval_is_loop_execution_authorization"])

    def test_exactly_twenty_contiguous_loops_are_grouped_four_per_phase(self):
        self.assertEqual([row["loop_id"] for row in self.loops], list(range(25, 45)))
        phases = self.roadmap["phases"]
        self.assertEqual([row["phase_id"] for row in phases], ["P1", "P2", "P3", "P4", "P5"])
        self.assertTrue(all(len(row["loop_ids"]) == 4 for row in phases))
        self.assertEqual(
            [loop_id for phase in phases for loop_id in phase["loop_ids"]],
            list(range(25, 45)),
        )
        phase_counts = Counter(row["phase_id"] for row in self.loops)
        self.assertEqual(phase_counts, Counter({f"P{index}": 4 for index in range(1, 6)}))

    def test_every_loop_is_detailed_not_started_and_unauthorized(self):
        required_text = {
            "title",
            "priority",
            "effort",
            "proof_posture",
            "core_question",
            "why_high_value",
            "build_deliverable",
            "research_deliverable",
            "data_scope",
            "acceptance_boundary",
            "stop_rule",
            "authorization_boundary",
            "resource_cap",
        }
        for row in self.loops:
            with self.subTest(loop=row["loop_id"]):
                self.assertEqual(row["status"], "Not Started")
                self.assertFalse(row["execution_authorized"])
                self.assertEqual(row["proof_posture"], "planned_not_authorized")
                self.assertTrue(all(isinstance(row[key], str) and row[key].strip() for key in required_text))
                self.assertGreaterEqual(len(row["controls"]), 3)
                self.assertGreaterEqual(len(row["primary_metrics"]), 4)
                self.assertIn(row["priority"], {"P0", "P1", "P2"})
                self.assertIn(row["effort"], {"S", "M", "L"})

    def test_loop_dependencies_are_unique_acyclic_and_point_backward(self):
        loop_ids = {row["loop_id"] for row in self.loops}
        for row in self.loops:
            dependencies = row["depends_on"]
            with self.subTest(loop=row["loop_id"]):
                self.assertEqual(len(dependencies), len(set(dependencies)))
                self.assertTrue(set(dependencies).issubset(loop_ids))
                self.assertTrue(all(dependency < row["loop_id"] for dependency in dependencies))
                self.assertEqual(len(row["external_gates"]), len(set(row["external_gates"])))

    def test_protected_real_evidence_and_consumed_seeds_remain_explicit(self):
        protected = self.roadmap["protected_evidence"]
        self.assertEqual(protected["synthetic_seeds"], [2203, 2303, 2353])
        real_text = " ".join(protected["real_cohorts"])
        self.assertIn("S21 session-1", real_text)
        self.assertIn("S21 session-2", real_text)
        self.assertIn("S7 EEG", real_text)
        self.assertIn("consumed", real_text)
        self.assertTrue(any("target-free fixture" in rule for rule in protected["rules"]))
        loop_text = json.dumps(self.loops, sort_keys=True)
        self.assertIn("source-test", loop_text)
        self.assertIn("session-2", loop_text)
        self.assertIn("consumed", loop_text)

    def test_global_caps_controls_and_closeout_requirements_are_frozen(self):
        constraints = self.roadmap["global_constraints"]
        self.assertIn("one numerical thread", constraints["cpu"])
        self.assertIn("32 MiB", constraints["storage"])
        self.assertIn("No download", constraints["data"])
        self.assertIn("no-signal prior", constraints["evaluation"])
        self.assertIn("sensitive", constraints["privacy"])
        for term in ["bytes", "runtime", "peak RSS", "access counters", "proceed, park, or kill"]:
            self.assertIn(term, constraints["closeout"])
        self.assertTrue(all("thread" in row["resource_cap"].lower() or row["loop_id"] in {27, 29, 35, 38, 44} for row in self.loops))

    def test_primary_sources_are_unique_secure_and_cover_core_workstreams(self):
        sources = self.roadmap["primary_sources"]
        self.assertGreaterEqual(len(sources), 10)
        self.assertEqual(len({row["source_id"] for row in sources}), len(sources))
        self.assertEqual(len({row["url"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        source_ids = {row["source_id"] for row in sources}
        self.assertTrue(
            {
                "brain2qwerty_v2",
                "brain2qwerty_v1",
                "mne_resampling",
                "bids_derivatives",
                "moabb_benchmark",
                "lsl_time_sync",
                "executorch",
                "eeg_identity_privacy",
                "nist_privacy_framework",
                "model_cards",
                "datasheets",
                "selective_prediction",
            }.issubset(source_ids)
        )

    def test_existing_loop24_and_rw3_execution_flags_remain_false(self):
        loop24 = json.loads(LOOP24_PATH.read_text(encoding="utf-8"))
        rw3 = json.loads(RW3_PATH.read_text(encoding="utf-8"))
        rw3_request = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                value is False
                for key, value in loop24["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertTrue(
            all(
                value is False
                for key, value in rw3["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        request_flags = []
        for key, value in rw3_request.items():
            if key.endswith("authorized_now"):
                request_flags.append(value)
        for section in rw3_request.values():
            if isinstance(section, dict):
                request_flags.extend(
                    value
                    for key, value in section.items()
                    if key.endswith("authorized_now")
                )
        self.assertTrue(request_flags)
        self.assertTrue(all(value is False for value in request_flags))

    def test_human_roadmap_and_public_tracker_cover_all_twenty_loops(self):
        roadmap_doc = (REPO_ROOT / "docs" / "LOOPS_25_44_ROADMAP.md").read_text(
            encoding="utf-8"
        )
        research_doc = (
            REPO_ROOT / "docs" / "NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md"
        ).read_text(encoding="utf-8")
        tracker_doc = (REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md").read_text(
            encoding="utf-8"
        )
        for row in self.loops:
            heading = rf"^## Loop {row['loop_id']} - {re.escape(row['title'])}$"
            with self.subTest(loop=row["loop_id"]):
                self.assertRegex(roadmap_doc, re.compile(heading, re.MULTILINE))
                self.assertIn(f"| {row['loop_id']} |", tracker_doc)
        self.assertIn("registries/next_20_loops.v0.json", roadmap_doc)
        self.assertIn("planning only", roadmap_doc.lower())
        self.assertIn("Brain2Qwerty v2", research_doc)
        self.assertIn("MNE", research_doc)
        self.assertIn("BIDS", research_doc)
        self.assertIn("MOABB", research_doc)


if __name__ == "__main__":
    unittest.main()
