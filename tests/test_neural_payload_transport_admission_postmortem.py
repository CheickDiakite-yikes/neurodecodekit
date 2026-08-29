from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/neural_payload_transport_admission_postmortem.v0.json"
DOCUMENT = ROOT / "docs/NEURAL_PAYLOAD_TRANSPORT_ADMISSION_POSTMORTEM_2026_08_29.md"


class NeuralPayloadTransportAdmissionPostmortemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_evidence_bindings_are_exact(self) -> None:
        for binding in self.record["evidence_bindings"].values():
            path = ROOT / binding["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), binding["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])
            blob = hashlib.sha1(
                f"blob {len(payload)}\0".encode("ascii") + payload
            ).hexdigest()
            self.assertEqual(blob, binding["git_blob"])
        ofner = self.record["evidence_bindings"]["ofner_result_proof"]
        self.assertEqual(ofner["CI_run_id"], 33_280_371_097)
        self.assertEqual(ofner["base_python_job_id"], 99_174_411_928)
        self.assertEqual(ofner["optional_neuro_readers_job_id"], 99_174_412_006)
        self.assertTrue(ofner["both_required_jobs_green"])

    def test_artifact_only_causal_conclusion_does_not_invent_transport_cause(self) -> None:
        conclusion = self.record["minimal_causal_conclusion"]
        self.assertIn("transport_admissibility", conclusion["established"])
        for key, value in conclusion.items():
            if key != "established":
                self.assertFalse(value, key)

    def test_observations_preserve_success_failure_and_science_boundaries(self) -> None:
        observations = self.record["observed_evidence"]
        self.assertEqual(observations["dreyer"]["accepted_body_bytes"], 0)
        self.assertFalse(observations["dreyer"]["specific_transport_cause_known"])
        self.assertEqual(observations["ofner"]["accepted_GDF_body_bytes"], 0)
        self.assertFalse(observations["ofner"]["specific_transport_cause_known"])
        self.assertEqual(observations["bnci"]["accepted_payload_bytes"], 779_873_919)
        self.assertTrue(observations["bnci"]["all_size_and_SHA256_checks_passed"])
        self.assertFalse(observations["bnci"]["scientific_result"])
        self.assertFalse(observations["iackd"]["scientific_result"])

    def test_NPA1_separates_transport_from_semantics(self) -> None:
        architecture = self.record["selected_architecture"]
        self.assertEqual(architecture["protocol_id"], "NPA1-v0")
        self.assertEqual(
            architecture["identity_order"],
            [
                "scientific_source_identity",
                "transport_capability_identity",
                "HTTP_framing_admissibility",
                "bounded_content_identity",
                "semantic_sensor_eligibility",
            ],
        )
        self.assertFalse(architecture["new_general_network_framework_allowed"])
        self.assertFalse(architecture["heavy_base_dependency_allowed"])

    def test_generated_next_step_is_bounded_and_network_free(self) -> None:
        requirements = self.record["generated_qualification_requirements"]
        self.assertEqual(requirements["minimum_deterministic_replays"], 2)
        self.assertGreaterEqual(requirements["minimum_named_adversarial_families"], 24)
        self.assertEqual(requirements["CPU_threads"], 1)
        self.assertEqual(requirements["workers"], 1)
        self.assertEqual(requirements["runtime_cap_seconds"], 30)
        self.assertEqual(requirements["peak_RSS_cap_bytes"], 256 * 1024**2)
        self.assertEqual(requirements["network_requests"], 0)
        self.assertEqual(requirements["retained_generated_payload_bytes"], 0)

    def test_live_canary_is_separate_closed_and_nonsemantic(self) -> None:
        canary = self.record["future_live_canary_contract"]
        self.assertFalse(canary["authorized_now"])
        self.assertEqual(canary["maximum_opaque_payload_bytes"], 256)
        self.assertEqual(canary["semantic_parses"], 0)
        self.assertEqual(canary["payload_retained_bytes"], 0)
        self.assertEqual(canary["retries_or_reruns"], 0)
        self.assertFalse(canary["raw_URL_or_header_publication"])
        self.assertFalse(canary["scientific_or_semantic_use_of_segment"])

    def test_no_source_or_irreversible_authority_is_created(self) -> None:
        source = self.record["fresh_source_admission"]
        self.assertIsNone(source["source_selected_now"])
        self.assertFalse(source["Dreyer_reuse_allowed"])
        self.assertFalse(source["Ofner_reuse_allowed"])
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        authority = self.record["authority"]
        self.assertIsNone(authority["active_Tier_C_packet"])
        self.assertFalse(authority["network_or_real_data_authorized"])
        self.assertFalse(
            authority["payload_header_signal_event_target_or_label_access_authorized"]
        )
        self.assertFalse(authority["model_training_prediction_or_scoring_authorized"])
        self.assertFalse(authority["device_release_or_claim_upgrade_authorized"])

    def test_claim_boundary_and_human_document_are_explicit(self) -> None:
        boundary = self.record["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No fresh source is selected", document)


if __name__ == "__main__":
    unittest.main()
