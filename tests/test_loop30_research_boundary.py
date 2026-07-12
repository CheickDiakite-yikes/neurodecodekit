import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop30_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_30_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
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


class Loop30ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_research_only_and_all_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop30_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_local_replay_ui_execution_blocked",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 30)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_is_target_free_replay_without_runtime_or_live_source(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["future_source_mode"], "synthetic_replay")
        self.assertTrue(decision["future_trace_must_be_new"])
        self.assertTrue(decision["future_trace_must_be_target_free"])
        self.assertFalse(decision["future_trace_seed_selected"])
        self.assertFalse(decision["future_trace_payload_generated"])
        self.assertFalse(decision["current_ui_exists"])
        self.assertFalse(decision["current_server_was_launched"])
        self.assertFalse(decision["live_source_in_scope"])
        self.assertFalse(decision["real_data_in_scope"])
        self.assertEqual(decision["maximum_current_latency_claim_level"], 0)
        self.assertEqual(decision["maximum_future_loop30_latency_claim_level"], 3)

    def test_existing_evidence_preserves_stable_but_wrong_and_consumed_boundaries(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 6)
        self.assertFalse(evidence["loop21_causal_chunk_replay"]["decoder_causality_established"])
        loop23 = evidence["loop23_streaming_ctc"]
        self.assertEqual(loop23["exact_sequences_observed"], 5)
        self.assertEqual(loop23["exact_sequences_required"], 6)
        self.assertEqual(loop23["test_sequences"], 8)
        self.assertEqual(loop23["registered_revision_events"], 0)
        self.assertFalse(loop23["stable_output_was_always_correct"])
        self.assertTrue(loop23["seed_consumed"])
        self.assertFalse(evidence["loop24_precision_runtime"]["eligible_as_loop30_trace"])
        self.assertTrue(evidence["brain2qwerty_v2"]["whole_sentence_noncausal"])
        self.assertTrue(
            all(row.get("payload_read_now", False) is False for row in evidence.values())
        )

    def test_source_modes_are_mutually_distinct_and_only_future_replay_is_in_scope(self):
        modes = {row["source_mode"]: row for row in self.boundary["source_mode_taxonomy"]}
        self.assertEqual(
            set(modes),
            {"artifact_replay", "synthetic_replay", "recorded_replay", "live"},
        )
        self.assertTrue(modes["artifact_replay"]["allowed_in_future_loop30"])
        self.assertTrue(modes["synthetic_replay"]["allowed_in_future_loop30"])
        self.assertFalse(modes["recorded_replay"]["allowed_in_future_loop30"])
        self.assertFalse(modes["live"]["allowed_in_future_loop30"])
        self.assertTrue(modes["live"]["may_be_called_live"])
        self.assertTrue(all(row["allowed_now"] is False for row in modes.values()))

    def test_trace_contract_is_deterministic_and_forbids_target_leakage(self):
        trace = self.boundary["future_target_free_trace"]
        self.assertIsNone(trace["seed"])
        self.assertTrue(trace["seed_must_be_frozen_before_generation"])
        self.assertTrue(trace["producer_must_be_deterministic"])
        self.assertEqual(len(trace["required_event_fields"]), 30)
        required = set(trace["required_event_fields"])
        self.assertTrue(
            {
                "trace_event_id",
                "source_mode",
                "proof_posture",
                "committed_prefix_length",
                "finalized",
                "cumulative_revision_count",
                "source_config_trace_and_payload_hashes",
            }.issubset(required)
        )
        forbidden_inputs = set(trace["producer_inputs_forbidden"])
        self.assertTrue(
            {
                "target_text",
                "labels",
                "prompt_text",
                "consumed_predictions",
                "model_logits",
                "real_signal",
            }.issubset(forbidden_inputs)
        )
        forbidden_fields = set(trace["forbidden_event_fields"])
        self.assertTrue(
            {"target", "label", "correct", "confidence", "probability"}.issubset(forbidden_fields)
        )
        self.assertTrue(trace["inspectable_without_server_launch"])
        self.assertFalse(trace["committable_now"])
        self.assertEqual(trace["generated_artifact_cap_bytes"], 32 * 1024**2)

    def test_clock_domains_and_latency_ladder_do_not_overload_end_to_end_time(self):
        clocks = self.boundary["clock_domains"]
        self.assertEqual(len(clocks), 9)
        self.assertEqual(len({row["clock_id"] for row in clocks}), 9)
        self.assertTrue(all(row["cross_domain_subtraction_allowed"] is False for row in clocks))
        self.assertEqual(
            next(row for row in clocks if row["clock_id"] == "user_observed_time")["unit"],
            "unavailable_until_measured",
        )
        levels = self.boundary["latency_claim_ladder"]
        self.assertEqual([row["level"] for row in levels], list(range(6)))
        self.assertEqual(levels[3]["maximum_claim"], "local_replay_presentation_latency")
        self.assertEqual(
            levels[5]["maximum_claim"],
            "end_to_end_latency_for_the_exact_device_protocol",
        )
        ledger = self.boundary["future_latency_ledger"]
        self.assertTrue(ledger["missing_stage_must_be_labeled_unavailable"])
        self.assertFalse(ledger["zero_may_replace_unavailable"])
        self.assertFalse(ledger["replay_schedule_may_be_called_capture_latency"])
        self.assertFalse(ledger["compute_rtf_may_be_called_end_to_end_latency"])
        self.assertFalse(ledger["end_to_end_latency_measured_now"])

    def test_hypothesis_contract_separates_stability_finalization_and_confidence(self):
        contract = self.boundary["incremental_hypothesis_contract"]
        self.assertTrue(contract["explicit_finalization_event_required"])
        self.assertFalse(contract["silence_or_no_change_may_imply_finalization"])
        self.assertTrue(contract["revision_history_required"])
        self.assertTrue(contract["committed_prefix_required"])
        self.assertFalse(contract["stability_is_correctness"])
        self.assertFalse(contract["stability_is_confidence"])
        self.assertFalse(contract["entropy_is_calibrated_confidence"])
        self.assertIn("Loop34", contract["predictive_confidence_status"])
        self.assertTrue(contract["no_signal_comparator_visibility_required"])
        self.assertFalse(contract["quality_metrics_in_target_free_trace_allowed"])

    def test_network_and_file_contract_is_fixed_loopback_and_fail_closed(self):
        privacy = self.boundary["privacy_network_contract"]
        self.assertEqual(privacy["server_name"], "127.0.0.1")
        self.assertFalse(privacy["server_name_user_override_allowed"])
        self.assertFalse(privacy["share"])
        self.assertFalse(privacy["analytics_enabled"])
        self.assertFalse(privacy["enable_monitoring"])
        self.assertTrue(privacy["strict_cors"])
        self.assertEqual(privacy["max_threads"], 1)
        self.assertEqual(privacy["workers"], 1)
        self.assertEqual(privacy["state_session_capacity"], 2)
        self.assertEqual(privacy["allowed_paths"], [])
        self.assertFalse(privacy["upload_components_allowed"])
        self.assertFalse(privacy["arbitrary_file_browser_allowed"])
        self.assertFalse(privacy["service_worker_allowed"])
        self.assertFalse(privacy["external_network_dependency_allowed"])
        self.assertEqual(privacy["non_loopback_request_or_websocket_tolerance"], 0)

    def test_browser_and_accessibility_contracts_are_explicit(self):
        browser = self.boundary["browser_qa_contract"]
        self.assertEqual(browser["required_viewports"], ["desktop", "mobile"])
        self.assertTrue(browser["request_ledger_required"])
        self.assertTrue(browser["websocket_ledger_required"])
        self.assertEqual(browser["service_workers"], "block")
        self.assertEqual(browser["non_loopback_requests_allowed"], 0)
        self.assertEqual(browser["non_loopback_websockets_allowed"], 0)
        self.assertEqual(browser["browser_long_task_threshold_ms"], 50)
        self.assertEqual(browser["browser_long_tasks_allowed_during_fixed_replay"], 0)
        self.assertTrue(browser["event_timing_unavailable_must_be_reported"])
        self.assertFalse(browser["browser_qa_executed_now"])
        access = self.boundary["accessibility_contract"]
        self.assertEqual(access["concise_status_role"], "status")
        self.assertIn("log", access["sequential_trace_role"])
        self.assertFalse(access["color_only_status_allowed"])
        self.assertFalse(access["focus_theft_allowed"])
        self.assertFalse(access["forced_autoscroll_allowed"])
        self.assertTrue(access["keyboard_navigation_required"])
        self.assertTrue(access["reduced_motion_required"])

    def test_future_requirements_and_refusals_are_complete_and_unique(self):
        gates = self.boundary["future_requirements"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 18)
        self.assertEqual(len({row["requirement_id"] for row in gates}), 18)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [
                f"L30-G{index:02d}_{row['requirement_id'].split('_', 1)[1]}"
                for index, row in enumerate(gates, 1)
            ],
        )
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(set(refusals)), 30)
        self.assertEqual(
            [value.split("_", 1)[0] for value in refusals],
            [f"L30-R{index:02d}" for index in range(1, 31)],
        )
        combined = " ".join(refusals)
        for phrase in (
            "non_loopback_bind",
            "confidence",
            "consumed_artifact",
            "target_label",
            "websocket",
            "accessibility",
        ):
            self.assertIn(phrase, combined)

    def test_dependencies_and_files_keep_implementation_absent(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop30_planning_research_complete"])
        self.assertFalse(dependencies["loop30_preregistration_prepared"])
        self.assertFalse(dependencies["loop30_authorization_request_prepared"])
        self.assertFalse(dependencies["loop30_runtime_or_UI_exists"])
        self.assertFalse(dependencies["loop30_trace_fixture_exists"])
        self.assertFalse(dependencies["loop25_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop23_consumed_seed_must_remain_closed"])
        self.assertFalse(dependencies["rw3_dependency_satisfied_now"])
        forbidden = (
            "docs/LOOP_30_PREREGISTRATION.md",
            "docs/LOOP_30_AUTHORIZATION_PACKET.md",
            "registries/loop30_interaction_contract.v0.json",
            "registries/loop30_authorization_request.v0.json",
            "src/neurodecodekit/demo/streaming.py",
            "src/neurodecodekit/demo/replay.py",
            "cache/loop30",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))

    def test_resources_and_protected_access_are_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_workers"], 1)
        self.assertEqual(resources["current_downloaded_payload_bytes"], 0)
        self.assertEqual(resources["current_generated_planning_artifact_cap_bytes"], 8 * 1024**2)
        self.assertEqual(resources["current_server_launches"], 0)
        self.assertEqual(resources["current_browser_qa_runs"], 0)
        self.assertIsNone(resources["external_browser_peak_rss_bytes"])
        self.assertIsNone(resources["end_to_end_research_runtime_sec"])
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 32 * 1024**2)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1024**3)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 10)
        protected = {
            key: value
            for key, value in counters.items()
            if key != "high_level_public_web_research_operations"
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_and_human_note_cover_the_interaction_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 16)
        self.assertEqual(len({row["source_id"] for row in sources}), 16)
        self.assertTrue(
            all(
                row["url"].startswith("https://") or row["url"].startswith("docs/")
                for row in sources
            )
        )
        for phrase in (
            "Continuous Output Is Not Yet Low-Latency Output",
            "Partial Hypotheses Need A Revision Ledger",
            "One Timestamp Field Would Create A False Latency Claim",
            "Localhost Is A Measured Security Property",
            "18 machine requirements and all 30 refusal cases",
            "does not establish",
        ):
            self.assertIn(phrase, self.research)

    def test_roadmap_keeps_loop30_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 30)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["research_registry"], "registries/loop30_research_boundary.v0.json")
        self.assertEqual(row["future_source_mode"], "synthetic_replay")
        self.assertEqual(row["clock_domain_count"], 9)
        self.assertEqual(row["future_requirement_count"], 18)
        self.assertEqual(row["future_refusal_count"], 30)
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["trace_fixture_exists"])
        self.assertFalse(row["server_or_browser_run_authorized"])

    def test_public_status_keeps_research_separate_from_execution(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                lowered = contents.lower()
                self.assertIn("loop 30", lowered)
                self.assertIn("planning research", lowered)
                self.assertIn("not started", lowered)
                self.assertIn("target-free", lowered)
                self.assertIn("replay", lowered)
        combined = "\n".join(self.public_status.values())
        self.assertIn("18", combined)
        self.assertIn("30", combined)
        self.assertNotIn("Loop 30 is complete", combined)


if __name__ == "__main__":
    unittest.main()
