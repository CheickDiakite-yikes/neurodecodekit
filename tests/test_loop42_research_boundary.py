import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop42_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_42_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
DEVICES_PATH = REPO_ROOT / "registries" / "devices.v0.json"
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


class Loop42ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))
        cls.pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
        cls.ci = CI_PATH.read_text(encoding="utf-8")
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop42_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["loop_id"], 42)
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 45)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])
        self.assertFalse(boundary["authorization"]["authorization_request_prepared"])
        self.assertFalse(boundary["authorization"]["preregistration_prepared"])

    def test_candidate_is_exact_and_not_a_purchase_or_decoding_decision(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(
            decision["current_qualification_level"],
            "L42-Q0_official_specification_candidate_only",
        )
        self.assertEqual(
            decision["selected_future_mechanics_candidate"],
            "openbci_cyton_8ch_usb_radio",
        )
        self.assertFalse(decision["selection_is_purchase_recommendation"])
        self.assertFalse(decision["device_owned_or_present_now"])
        self.assertFalse(decision["connectivity_is_signal_quality"])
        self.assertFalse(decision["connectivity_is_decoding"])
        self.assertFalse(decision["capture_to_arrival_latency_available_now"])

    def test_candidate_selection_matches_the_existing_device_registry(self):
        selection = self.boundary["candidate_selection_audit"]
        self.assertEqual(self.devices["schema_name"], selection["device_registry_schema"])
        self.assertEqual(self.devices["schema_version"], selection["device_registry_version"])
        self.assertEqual(len(self.devices["records"]), 13)
        eeg_records = [
            row
            for row in self.devices["records"]
            if any("EEG" in signal or "ExG" in signal for signal in row.get("signals", []))
        ]
        self.assertEqual(len(eeg_records), 7)
        self.assertEqual(selection["registry_record_count"], 13)
        self.assertEqual(selection["eeg_or_exg_candidate_count"], 7)
        self.assertEqual(selection["selected_registry_id"], "openbci_cyton")
        cyton = next(row for row in self.devices["records"] if row["id"] == "openbci_cyton")
        self.assertEqual(cyton["channels"]["ExG"], 8)
        self.assertEqual(cyton["sampling_rate_hz"]["ExG"], 250)
        self.assertTrue(selection["daisy_excluded"])
        self.assertTrue(selection["wifi_shield_excluded"])

    def test_candidate_descriptor_preserves_modality_and_configuration_limits(self):
        descriptor = self.boundary["candidate_descriptor"]
        self.assertEqual(descriptor["brainflow_board_id_name"], "CYTON_BOARD")
        self.assertEqual(descriptor["brainflow_board_id_value"], 0)
        self.assertEqual(descriptor["native_exg_channels"], 8)
        self.assertEqual(descriptor["nominal_sampling_rate_hz"], 250)
        self.assertEqual(descriptor["native_packet_bytes"], 33)
        self.assertEqual(descriptor["sample_counter_modulus"], 256)
        self.assertFalse(descriptor["network_transport_required"])
        self.assertIn("battery_only", descriptor["power_requirement"])
        self.assertIn("unavailable", descriptor["exact_future_firmware"])
        self.assertIn("only_when", descriptor["modality"])
        self.assertIn("not_EEG", descriptor["measurement_class_without_electrodes"])

    def test_identity_packet_timing_and_anomaly_contracts_are_exact(self):
        self.assertEqual(len(self.boundary["identity_record_fields"]), 28)
        self.assertEqual(len(self.boundary["packet_contract"]["required_packet_fields"]), 16)
        self.assertEqual(len(self.boundary["timing_observables"]), 7)
        self.assertEqual(len(self.boundary["anomaly_classes"]), 10)
        self.assertEqual(
            [row["timing_id"] for row in self.boundary["timing_observables"]],
            [
                "sample_counter",
                "adapter_timestamp",
                "host_arrival_monotonic",
                "host_retrieval_monotonic",
                "marker_timestamp",
                "physical_capture_time",
                "render_or_text_time",
            ],
        )
        packet = self.boundary["packet_contract"]
        self.assertFalse(packet["counter_wrap_is_gap"])
        self.assertTrue(packet["counter_wrap_must_be_distinguished_from_reset"])
        self.assertEqual(packet["missing_packet_repair"], "forbidden")
        self.assertEqual(packet["duplicate_packet_repair"], "forbidden")
        self.assertEqual(packet["reordered_packet_sorting"], "forbidden")

    def test_privacy_and_safety_fail_closed(self):
        privacy = self.boundary["privacy_locality_contract"]
        self.assertEqual(len(privacy["required_surfaces"]), 10)
        self.assertFalse(privacy["wifi_shield_allowed"])
        self.assertFalse(privacy["cloud_upload_allowed"])
        self.assertFalse(privacy["raw_data_git_allowed"])
        self.assertFalse(privacy["support_log_sharing_allowed"])
        self.assertTrue(privacy["network_off_test_required_before_locality_claim"])
        self.assertFalse(privacy["local_file_claim_is_privacy_claim"])
        safety = self.boundary["safety_consent_contract"]
        self.assertEqual(len(safety["requirements"]), 10)
        self.assertFalse(safety["human_session_allowed_now"])
        self.assertFalse(safety["consent_template_exists_now"])
        self.assertFalse(safety["retention_schedule_exists_now"])
        self.assertIn("battery_power_only", " ".join(safety["requirements"]))

    def test_qualification_ladder_and_stages_cannot_be_collapsed(self):
        levels = self.boundary["qualification_levels"]
        stages = self.boundary["future_stage_sequence"]
        self.assertEqual(len(levels), 6)
        self.assertEqual([row["level_id"] for row in levels], [f"L42-Q{i}" for i in range(6)])
        self.assertTrue(levels[0]["available_now"])
        self.assertTrue(all(not row["available_now"] for row in levels[1:]))
        self.assertEqual(len(stages), 4)
        self.assertEqual([row["stage_id"] for row in stages], ["L42-A", "L42-B", "L42-C", "L42-D"])
        self.assertTrue(all(row["separate_authorization_required"] for row in stages))
        self.assertFalse(stages[0]["hardware_allowed"])
        self.assertFalse(stages[1]["hardware_allowed"])
        self.assertTrue(stages[2]["hardware_allowed"])
        self.assertFalse(stages[2]["participant_allowed"])
        self.assertTrue(stages[3]["participant_allowed"])

    def test_dependencies_remain_unsatisfied(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop29_planning_research_available_now"])
        self.assertTrue(dependencies["loop38_planning_research_available_now"])
        self.assertTrue(dependencies["loop41_planning_research_available_now"])
        self.assertFalse(dependencies["loop38_device_lifecycle_execution_satisfied_now"])
        self.assertFalse(dependencies["loop41_stream_to_neurotoken_execution_satisfied_now"])
        self.assertFalse(dependencies["rw3_stage_a_authorized_now_dependency"])
        self.assertFalse(dependencies["compatible_causal_preprocessing_available_now"])
        self.assertFalse(dependencies["ethics_consent_retention_packet_exists_now"])
        self.assertFalse(dependencies["all_execution_dependencies_satisfied_now"])

    def test_fixtures_gates_and_refusals_are_exact(self):
        fixtures = self.boundary["future_fixture_families"]
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(fixtures), 30)
        self.assertEqual(len(gates), 34)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L42-G{index:02d}" for index in range(1, 35)],
        )
        self.assertEqual(len(refusals), 46)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L42-R{index:02d}" for index in range(1, 47)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "firmware",
            "daisy",
            "wifi",
            "packet",
            "counter",
            "timestamp",
            "capture",
            "replay",
            "network",
            "consent",
            "battery",
            "target",
            "resource",
            "signal",
            "decoding",
            "portable",
        ):
            self.assertIn(term, combined)

    def test_resources_are_small_and_access_counters_are_zero(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_generated_experiment_bytes"], 0)
        self.assertEqual(resources["current_device_session_seconds"], 0)
        self.assertEqual(resources["future_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_stage_d_max_session_sec"], 600)
        self.assertEqual(resources["future_peak_rss_bytes"], 1_073_741_824)
        self.assertEqual(resources["future_raw_session_bytes"], 67_108_864)
        self.assertEqual(resources["future_derived_artifact_bytes"], 33_554_432)
        self.assertEqual(resources["future_total_generated_bytes"], 100_663_296)
        self.assertEqual(resources["future_cloud_upload_bytes"], 0)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_operations"], 4)
        self.assertEqual(counters["public_search_queries"], 12)
        self.assertEqual(counters["official_or_primary_pages_opened"], 9)
        for key, value in counters.items():
            if isinstance(value, int) and key not in {
                "high_level_public_web_operations",
                "public_search_queries",
                "official_or_primary_pages_opened",
            }:
                self.assertEqual(value, 0, key)

    def test_sources_are_official_and_bound_to_the_decision(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 9)
        self.assertEqual(
            {row["source_id"] for row in sources},
            {
                "openbci_cyton_format",
                "openbci_cyton_sdk",
                "openbci_cyton_specs",
                "openbci_eeg_setup",
                "openbci_gui",
                "openbci_privacy",
                "brainflow_supported_boards",
                "brainflow_data_format",
                "brainflow_license",
            },
        )
        self.assertTrue(
            all(
                row["authority"] in {"OpenBCI", "BrainFlow"} and row["url"].startswith("https://")
                for row in sources
            )
        )

    def test_claim_taxonomy_stays_at_specification_level(self):
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(claims), 7)
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(not row["available_now"] for row in claims[1:]))
        boundary = self.boundary["claim_boundary"]
        self.assertIn("candidate", boundary["engineering_capability_added"])
        self.assertIn("no_sdk", boundary["scientific_claim_not_established"])
        self.assertEqual(len(boundary["forbidden_promotions"]), 8)

    def test_roadmap_row_and_machine_summary_match(self):
        self.assertEqual(self.roadmap["schema_version"], "0.19.0")
        self.assertEqual(len(self.roadmap["loops"]), 20)
        self.assertTrue(all(row["execution_authorized"] is False for row in self.roadmap["loops"]))
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 42)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["selected_future_candidate"], "openbci_cyton_8ch_usb_radio")
        self.assertEqual(row["identity_field_count"], 28)
        self.assertEqual(row["timing_observable_count"], 7)
        self.assertEqual(row["future_fixture_family_count"], 30)
        self.assertEqual(row["future_requirement_count"], 34)
        self.assertEqual(row["future_refusal_count"], 46)
        self.assertEqual(row["false_authorization_field_count"], 45)
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["authorization_request_prepared"])

    def test_no_runtime_dependency_or_implementation_was_added(self):
        self.assertNotIn("brainflow", self.pyproject.lower())
        self.assertNotIn("openbci", self.pyproject.lower())
        self.assertNotIn("brainflow", self.ci.lower())
        self.assertNotIn("openbci", self.ci.lower())
        source_text = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted((REPO_ROOT / "src").rglob("*.py"))
        ).lower()
        self.assertNotIn("loop42", source_text)
        self.assertNotIn("import brainflow", source_text)
        self.assertNotIn("from brainflow", source_text)

    def test_research_and_public_status_preserve_the_boundary(self):
        for term in (
            "OpenBCI Cyton",
            "purchase recommendation",
            "L42-Q0",
            "33-byte",
            "capture-to-arrival",
            "battery",
            "Scientific claim not established",
        ):
            self.assertIn(term, self.research)
        for path, text in self.public_status.items():
            self.assertIn("Loop 42", text, path)
            self.assertIn("Not Started", text, path)
            self.assertIn("unauthorized", text.lower(), path)


if __name__ == "__main__":
    unittest.main()
