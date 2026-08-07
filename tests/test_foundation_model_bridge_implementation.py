import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.evaluation.foundation_model_bridge import (
    build_ablation_plan_file,
    inspect_ablation_plan_file,
    load_json_object,
    validate_synthetic_evidence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "foundation_model_bridge_v0.json"
DOC_PATH = REPO_ROOT / "docs" / "FOUNDATION_MODEL_BRIDGE_V0.md"
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


class FoundationModelBridgeImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_is_fm0_implemented_no_call(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.foundation_model_bridge_implementation",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["stage_id"], "FM-0")
        self.assertIn("implemented_and_locally_validated", registry["status"])
        self.assertEqual(registry["strategy_commit"], "35debc7")

    def test_strategy_and_implementation_sources_are_hash_bound(self):
        for group_name in ("strategy_binding", "implementation_binding"):
            group = self.registry[group_name]
            for key, value in group.items():
                if key.endswith("_path"):
                    hash_key = key.removesuffix("_path") + "_sha256"
                    if hash_key in group:
                        with self.subTest(path=value):
                            self.assertEqual(group[hash_key], sha256(REPO_ROOT / value))

    def test_committed_fixture_validates_and_matches_declared_shape(self):
        fixture_path = REPO_ROOT / self.registry["implementation_binding"]["fixture_path"]
        fixture = load_json_object(fixture_path)
        validate_synthetic_evidence(fixture)
        measured = self.registry["measured_roundtrip"]
        self.assertEqual(fixture_path.stat().st_size, measured["source_fixture_bytes"])
        self.assertEqual(len(fixture["items"]), measured["source_items"])
        self.assertEqual(
            sum(len(row["ctc_nbest"]) for row in fixture["items"]),
            measured["source_CTC_hypotheses"],
        )
        self.assertEqual(
            sum(len(row["neural_key_frames"]) for row in fixture["items"]),
            measured["source_neural_frames"],
        )

    def test_measured_plan_replays_byte_exactly(self):
        fixture_path = REPO_ROOT / self.registry["implementation_binding"]["fixture_path"]
        measured = self.registry["measured_roundtrip"]
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            summary = build_ablation_plan_file(fixture_path, plan_path)
            inspection = inspect_ablation_plan_file(plan_path)
            self.assertEqual(plan_path.stat().st_size, measured["compiled_plan_bytes"])
            self.assertEqual(sha256(plan_path), measured["plan_file_sha256"])
            self.assertEqual(summary["plan_core_sha256"], measured["plan_core_sha256"])
            self.assertEqual(inspection["condition_count"], measured["compiled_condition_plans"])
            self.assertEqual(
                inspection["source_top_key_probability_count"],
                measured["source_top_key_probabilities"],
            )

    def test_resources_and_access_remain_below_caps_and_zero(self):
        caps = self.registry["resource_caps"]
        measured = self.registry["measured_roundtrip"]
        self.assertLess(measured["build_runtime_seconds"], caps["maximum_runtime_seconds"])
        self.assertLess(measured["inspect_runtime_seconds"], caps["maximum_runtime_seconds"])
        self.assertLess(measured["build_peak_rss_bytes"], caps["maximum_peak_rss_bytes"])
        self.assertLess(measured["inspect_peak_rss_bytes"], caps["maximum_peak_rss_bytes"])
        self.assertLess(measured["source_fixture_bytes"], caps["maximum_input_bytes"])
        self.assertLess(measured["compiled_plan_bytes"], caps["maximum_output_bytes"])
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_only_local_synthetic_implementation_is_authorized(self):
        authorization = dict(self.registry["authorization"])
        self.assertTrue(
            authorization.pop("synthetic_no_call_implementation_tests_docs_commit_and_push_authorized")
        )
        self.assertTrue(all(value is False for value in authorization.values()))
        model = self.registry["selected_future_model_metadata"]
        self.assertFalse(model["external_call_enabled"])
        self.assertFalse(model["fine_tuning_used"])
        self.assertFalse(model["custom_embedding_injection"])

    def test_document_and_public_surfaces_report_implementation_without_science(self):
        for phrase in (
            "Implemented and locally validated",
            "not an OpenAI wire request",
            "34,349",
            "API credential",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.doc)
        for path in PUBLIC_STATUS_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("FM-0", content)
                self.assertIn("34,349", content)
                self.assertIn("provider", content.lower())


if __name__ == "__main__":
    unittest.main()
