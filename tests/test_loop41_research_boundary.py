import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop41_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_41_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
RW3_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "CODEX_NEXT_20_LOOPS_PROMPT.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "docs" / "POST_20_ROADMAP.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop41ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.rw3 = json.loads(RW3_PATH.read_text(encoding="utf-8"))
        cls.pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
        cls.ci = CI_PATH.read_text(encoding="utf-8")
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop41_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["loop_id"], 41)
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 42)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_preserves_the_exact_claim_ceiling(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(
            decision["maximum_current_claim_class"], "L41-C0_no_stream_to_neurotoken_result"
        )
        self.assertFalse(decision["integration_implementation_exists_now"])
        self.assertFalse(decision["decoder_in_scope"])
        self.assertFalse(decision["live_source_in_scope"])
        self.assertFalse(decision["end_to_end_latency_measured_now"])
        self.assertFalse(decision["capture_to_arrival_latency_available_for_replay"])
        self.assertIn("target_free_replay", decision["maximum_future_loop41_claim"])

    def test_dependencies_fail_closed(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop20_neurotoken_interface_available_now"])
        self.assertTrue(dependencies["loop21_causal_mock_producer_proof_available_now"])
        self.assertFalse(dependencies["loop21_proof_is_loop41_runtime_evidence"])
        self.assertFalse(dependencies["loop25_execution_and_closeout_satisfied_now"])
        self.assertFalse(dependencies["loop37_execution_and_closeout_satisfied_now"])
        self.assertFalse(dependencies["loop39_relevant_matrix_satisfied_now"])
        self.assertFalse(dependencies["rw3_stage_a_authorized_now_dependency"])
        self.assertFalse(dependencies["all_execution_dependencies_satisfied_now"])
        self.assertTrue(dependencies["separate_loop41_authorization_required"])

    def test_current_interface_audit_matches_repository_contracts(self):
        audit = self.boundary["current_interface_audit"]
        self.assertEqual(audit["rw3_source_chunk_schema"], "neurodecodekit.source_chunk")
        self.assertEqual(audit["rw3_source_chunk_schema_version"], "0.1.0")
        self.assertEqual(audit["rw3_registered_schedule_count"], 5)
        self.assertEqual(audit["rw3_state_byte_cap"], 4096)
        self.assertEqual(audit["neurotoken_schema"], "neurotoken-cache")
        self.assertEqual(audit["neurotoken_schema_version"], 0)
        self.assertTrue(audit["loop21_mock_producer_is_causal"])
        self.assertEqual(audit["loop21_mock_producer_right_context_samples"], 0)
        self.assertFalse(audit["loop21_serialized_resume_state_exists"])
        self.assertFalse(audit["loop25_runtime_preprocessor_exists"])
        self.assertFalse(audit["complete_join_exists"])

    def test_rw3_schedule_and_source_contract_are_inherited_exactly(self):
        source = self.rw3["source_chunk_schema"]
        self.assertEqual(source["schema_name"], "neurodecodekit.source_chunk")
        self.assertEqual(source["schema_version"], "0.1.0")
        self.assertEqual(len(self.rw3["registered_schedules"]), 5)
        self.assertEqual(self.rw3["state_contract"]["max_serialized_state_bytes"], 4096)
        schedules = [row["schedule_id"] for row in self.boundary["schedule_matrix"]]
        self.assertEqual(
            schedules,
            [
                "single_sample",
                "fixed_20ms",
                "native_packet",
                "deterministic_jitter_5_to_30ms",
                "whole_source",
            ],
        )

    def test_taxonomies_are_exact_and_clocks_remain_distinct(self):
        self.assertEqual(len(self.boundary["integration_layers"]), 6)
        self.assertEqual(len(self.boundary["clock_ledger"]), 7)
        self.assertEqual(len(self.boundary["clock_rules"]), 10)
        self.assertEqual(len(self.boundary["anomaly_classes"]), 8)
        self.assertEqual(len(self.boundary["schedule_matrix"]), 5)
        self.assertEqual(len(self.boundary["resume_cuts"]), 5)
        self.assertEqual(len(self.boundary["identity_and_hash_bindings"]), 18)
        self.assertEqual(len(self.boundary["future_fixture_families"]), 28)
        self.assertEqual(len(self.boundary["future_stage_sequence"]), 4)
        self.assertEqual(
            [row["clock_id"] for row in self.boundary["clock_ledger"]],
            [
                "source",
                "corrected",
                "arrival",
                "preprocess_ready",
                "token_available",
                "decoder_emission",
                "render_presented",
            ],
        )
        self.assertTrue(
            all(
                row["separate_authorization_required"]
                for row in self.boundary["future_stage_sequence"]
            )
        )

    def test_state_is_bounded_hash_bound_and_has_no_payload_history(self):
        state = self.boundary["state_contract"]
        self.assertEqual(len(state["state_components"]), 7)
        self.assertTrue(state["state_payload_history_forbidden"])
        self.assertEqual(state["future_source_chunk_state_bytes"], 4096)
        self.assertEqual(state["future_total_serialized_state_bytes"], 65536)
        self.assertIn("uninterrupted", state["resume_rule"])
        self.assertIn("refuse", state["collision_rule"])

    def test_gates_and_refusals_cover_semantic_failures(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 32)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L41-G{index:02d}" for index in range(1, 33)],
        )
        self.assertEqual(len(refusals), 42)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L41-R{index:02d}" for index in range(1, 43)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "target",
            "clock",
            "interpolation",
            "deduplication",
            "reordering",
            "gap",
            "schedule",
            "resume",
            "state",
            "timestamp",
            "provenance",
            "runtime",
            "network",
            "device",
            "latency",
            "scientific",
        ):
            self.assertIn(term, combined)

    def test_resources_and_research_access_are_zero_and_bounded(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_timeout_sec_per_worker"], 60)
        self.assertEqual(resources["future_peak_rss_bytes"], 1_073_741_824)
        self.assertEqual(
            resources["future_total_generated_fixture_state_cache_and_report_bytes"], 33_554_432
        )
        self.assertEqual(resources["future_complete_integration_state_bytes"], 65_536)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_operations"], 2)
        self.assertEqual(counters["public_search_queries"], 4)
        self.assertEqual(counters["official_or_primary_pages_opened"], 8)
        for key, value in counters.items():
            if isinstance(value, int) and key not in {
                "high_level_public_web_operations",
                "public_search_queries",
                "official_or_primary_pages_opened",
            }:
                self.assertEqual(value, 0, key)

    def test_sources_are_official_and_complete(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        ids = {row["source_id"] for row in sources}
        self.assertEqual(
            ids,
            {
                "lsl_time_synchronization",
                "lsl_introduction",
                "lsl_faq",
                "liblsl_postprocessing_flags",
                "w3c_high_resolution_time",
                "python_time",
                "bids_derivatives_introduction",
                "bids_derivatives_common_data_types",
            },
        )
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_research_document_contains_boundaries_and_closeout(self):
        for text in (
            "Loop 41 Primary-Source Research",
            "experiment is `Not Started`",
            "seven clock views",
            "42 false execution authorization fields",
            "capture-to-text latency are unavailable",
            "No integration runtime",
            "Engineering capability added:",
            "Scientific claim not established:",
            "no neural advantage",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.21.0")
        current = self.roadmap["current_boundary"]
        self.assertTrue(current["loop41_research_packet_prepared"])
        self.assertEqual(current["loop41_clock_view_count"], 7)
        self.assertEqual(current["loop41_anomaly_class_count"], 8)
        self.assertEqual(current["loop41_future_fixture_family_count"], 28)
        self.assertEqual(current["loop41_future_requirement_count"], 32)
        self.assertEqual(current["loop41_future_refusal_count"], 42)
        self.assertFalse(current["loop41_preregistration_prepared"])
        self.assertFalse(current["loop41_execution_authorized"])
        self.assertFalse(current["loop41_dependency_rw3_stage_a_satisfied"])
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 41)
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["execution_authorized"])
        for path, text in self.public_status.items():
            with self.subTest(path=path):
                self.assertIn("Loop 41", text)
                self.assertIn("planning research", text.lower())
                self.assertIn("Not Started", text)
                self.assertIn("unauthorized", text.lower())

    def test_no_loop41_runtime_dependency_or_payload_was_added(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop41", source_text)
        for dependency in ("pylsl", "brainflow", "pyxdf"):
            self.assertNotIn(dependency, self.pyproject.lower())
            self.assertNotIn(dependency, self.ci.lower())
        tracked_output = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        tracked_payload_suffixes = {".xdf", ".edf", ".bdf", ".fif", ".npz", ".npy", ".pt", ".pth"}
        tracked = [
            path for path in tracked_output if Path(path).suffix.lower() in tracked_payload_suffixes
        ]
        self.assertEqual(tracked, [])

    def test_claim_boundary_refuses_scientific_inference(self):
        claim = self.boundary["claim_boundary"]
        self.assertIn("machine_checkable", claim["engineering_capability_added"])
        self.assertIn("no_source_chunk", claim["scientific_claim_not_established"])
        self.assertEqual(len(claim["warnings"]), 6)
        self.assertIn("replay_scheduling_latency_is_not_capture_to_text_latency", claim["warnings"])


if __name__ == "__main__":
    unittest.main()
