import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "foundation_model_decoder_strategy.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "FOUNDATION_MODEL_DECODER_STRATEGY_2026-08-06.md"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "BUILD_NOTES.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "DECISIONS.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FoundationModelDecoderStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_strategy_selects_layered_decoder_without_gpt_scale_training(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.foundation_model_decoder_strategy",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["created_at"], "2026-08-06")
        self.assertEqual(
            registry["decision"],
            "use_compact_causal_sensor_adapter_then_frozen_foundation_model_decoder",
        )
        layers = registry["architecture"]["layers"]
        self.assertEqual([row["layer_id"] for row in layers], ["FM-L0", "FM-L1", "FM-L2"])
        self.assertTrue(layers[1]["training_may_be_required"])
        self.assertFalse(layers[2]["training_selected_now"])

    def test_hosted_candidate_is_explicit_and_not_embedding_injection(self):
        candidate = self.registry["selected_hosted_candidate"]
        self.assertEqual(candidate["provider"], "OpenAI")
        self.assertEqual(candidate["model_id"], "gpt-5.6-sol")
        self.assertEqual(candidate["endpoint"], "responses")
        self.assertEqual(candidate["candidate_reasoning_effort"], "low")
        self.assertEqual(candidate["input_modalities"], ["text", "image"])
        self.assertTrue(candidate["structured_outputs_supported"])
        self.assertFalse(candidate["custom_hidden_embedding_input_supported"])
        self.assertFalse(candidate["fine_tuning_supported_now"])
        self.assertFalse(candidate["fine_tuning_selected_now"])

    def test_frozen_loop31_loop55_and_cml_artifacts_remain_hash_bound(self):
        boundary = self.registry["frozen_boundary"]
        pairs = (
            ("loop31_research_path", "loop31_research_sha256"),
            ("loop31_registry_path", "loop31_registry_sha256"),
            ("loop55_research_path", "loop55_research_sha256"),
            ("loop55_registry_path", "loop55_registry_sha256"),
            ("cml_research_path", "cml_research_sha256"),
            ("cml_registry_path", "cml_registry_sha256"),
        )
        for path_key, hash_key in pairs:
            with self.subTest(path=boundary[path_key]):
                self.assertEqual(boundary[hash_key], sha256(REPO_ROOT / boundary[path_key]))
        self.assertFalse(boundary["this_strategy_amends_consumed_loop31"])
        self.assertFalse(boundary["this_strategy_amends_frozen_loop55"])
        self.assertFalse(boundary["this_strategy_authorizes_real_or_protected_execution"])

    def test_hosted_export_is_compact_and_excludes_sensitive_payloads(self):
        export = self.registry["architecture"]["hosted_evidence_export"]
        allowed = " ".join(export["allowed_fields"])
        forbidden = " ".join(export["forbidden_fields"])
        for phrase in ("CTC", "top_key", "entropy", "timestamps", "uncertainty"):
            self.assertIn(phrase, allowed)
        for phrase in (
            "raw_EEG",
            "dense_source_embeddings",
            "absolute_local_paths",
            "participant_names",
            "target_or_reference_text",
            "intended_sentence_text",
            "performed_target_labels",
        ):
            self.assertIn(phrase, forbidden)
        self.assertFalse(export["continuous_NeuroToken_cache_replaced"])
        self.assertFalse(export["continuous_NeuroToken_directly_injected_into_hosted_model"])
        self.assertTrue(export["future_local_continuous_prefix_adapter_is_separate"])

    def test_four_conditions_preserve_matched_language_controls(self):
        matrix = self.registry["matched_ablation_matrix"]
        self.assertEqual([row["condition_id"] for row in matrix], ["FM-A00", "FM-A01", "FM-A02", "FM-A03"])
        self.assertEqual(matrix[0]["ctc_evidence"], "absent")
        self.assertEqual(matrix[1]["neural_evidence"], "absent")
        self.assertEqual(matrix[2]["neural_evidence"], "matched")
        self.assertEqual(matrix[3]["neural_evidence"], "fixed_cyclic_item_derangement")
        interpretation = self.registry["scientific_interpretation"]
        self.assertFalse(interpretation["FM_A00_improvement_alone_is_neural_evidence"])
        self.assertFalse(interpretation["fluency_or_plausibility_is_decoding_proof"])
        self.assertEqual(len(interpretation["required_incremental_conjunction"]), 5)

    def test_only_synthetic_no_call_stage_is_eligible(self):
        stages = self.registry["stage_sequence"]
        self.assertEqual([row["stage_id"] for row in stages], ["FM-0", "FM-1", "FM-2", "FM-3"])
        self.assertEqual([row["eligible_now"] for row in stages], [True, False, False, False])
        self.assertEqual(stages[0]["provider_calls"], 0)
        self.assertEqual(stages[0]["real_or_protected_reads"], 0)

    def test_synthetic_caps_are_small_and_no_call(self):
        caps = self.registry["synthetic_stage_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertLessEqual(caps["maximum_input_json_bytes"], 1024**2)
        self.assertLessEqual(caps["maximum_generated_json_bytes"], 1024**2)
        self.assertLessEqual(caps["maximum_wall_seconds"], 30)
        self.assertLessEqual(caps["maximum_peak_rss_bytes"], 256 * 1024**2)
        for field in (
            "network_calls",
            "provider_model_calls",
            "local_model_calls",
            "training_runs",
            "real_or_protected_reads",
            "target_or_label_reads",
        ):
            self.assertEqual(caps[field], 0)

    def test_every_external_or_scientific_permission_and_counter_is_zero(self):
        authorization = dict(self.registry["authorization"])
        self.assertTrue(authorization.pop("planning_documentation_tests_commit_and_push_authorized_now"))
        self.assertTrue(authorization.pop("synthetic_no_call_bridge_implementation_authorized_now"))
        self.assertTrue(all(value is False for value in authorization.values()))
        self.assertTrue(all(value == 0 for value in self.registry["current_access_counters"].values()))

    def test_document_states_exact_capability_and_claim_boundary(self):
        for phrase in (
            "compact trained sensor adapter",
            "GPT-5.6 Sol",
            "Four Matched Conditions",
            "FM-A02",
            "fixed cyclically deranged item",
            "Synthetic No-Call Bridge",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.doc)

    def test_public_status_surfaces_record_the_additive_strategy(self):
        for path in PUBLIC_STATUS_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("gpt-5.6-sol", content.lower())
                self.assertIn("no-call", content.lower())
                self.assertIn("FM-A02", content)


if __name__ == "__main__":
    unittest.main()
