import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cli import main
from neurodecodekit.evaluation.ai_research_policy import (
    MAX_REPORT_BYTES,
    build_synthetic_proposal,
    build_validation_envelope,
    canonical_json_bytes,
    inspect_ai_research_policy,
    load_ai_research_policy,
    load_json_object,
    sha256_json,
    validate_ai_research_proposal,
    write_bounded_json,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "registries" / "loop55_ai_research_policy.v0.json"
FIXTURE = ROOT / "fixtures" / "loop55_ai_synthetic_proposal.v0.json"


class AIResearchPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_ai_research_policy(POLICY)
        cls.fixture = load_json_object(FIXTURE)

    def validate(self, proposal):
        return validate_ai_research_proposal(proposal, self.policy)

    def assert_rejected(self, proposal, path):
        report = self.validate(proposal)
        self.assertFalse(report.accepted)
        self.assertIn(path, {row.path for row in report.violations})
        return report

    def test_committed_fixture_matches_builder_and_is_accepted(self):
        built = build_synthetic_proposal(self.policy)
        self.assertEqual(built, self.fixture)
        report = self.validate(self.fixture)
        self.assertTrue(report.accepted)
        self.assertEqual(report.violations, ())
        self.assertTrue(all(value == 0 for value in report.access_counters.values()))

    def test_replay_hashes_are_deterministic_and_order_independent(self):
        first = self.validate(self.fixture)
        reordered = dict(reversed(list(self.fixture.items())))
        second = self.validate(reordered)
        self.assertEqual(first.proposal_sha256, second.proposal_sha256)
        self.assertEqual(first.to_dict()["validation_core_sha256"], second.to_dict()["validation_core_sha256"])
        self.assertEqual(canonical_json_bytes(self.fixture), canonical_json_bytes(reordered))

    def test_unknown_top_level_and_nested_fields_are_rejected(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["execute_python"] = "print('no')"
        self.assert_rejected(proposal, "$")
        proposal = copy.deepcopy(self.fixture)
        proposal["representation_recipe"]["secret_feature"] = "target"
        self.assert_rejected(proposal, "$.representation_recipe")

    def test_target_language_and_pretrained_leakage_are_rejected(self):
        for field in (
            "uses_target_text",
            "uses_performed_labels_during_pretraining",
            "uses_pretrained_weights",
            "uses_language_model",
        ):
            with self.subTest(field=field):
                proposal = copy.deepcopy(self.fixture)
                proposal["representation_recipe"][field] = True
                self.assert_rejected(proposal, f"$.representation_recipe.{field}")

    def test_final_observation_and_endpoint_drift_are_rejected(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["observation_scope"] = "final_metrics"
        self.assert_rejected(proposal, "$.observation_scope")
        proposal = copy.deepcopy(self.fixture)
        proposal["objective_id"] = "sentence_WER"
        self.assert_rejected(proposal, "$.objective_id")

    def test_noncausal_window_and_future_context_are_rejected(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["representation_recipe"]["input_window_ms"] = [-200, 300]
        self.assert_rejected(proposal, "$.representation_recipe.input_window_ms")
        proposal = copy.deepcopy(self.fixture)
        proposal["representation_recipe"]["right_context_ms"] = 1
        self.assert_rejected(proposal, "$.representation_recipe.right_context_ms")
        proposal = copy.deepcopy(self.fixture)
        proposal["representation_recipe"]["producer_causal"] = False
        self.assert_rejected(proposal, "$.representation_recipe.producer_causal")

    def test_parameter_hyperparameter_and_mask_rules_are_enforced(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["representation_recipe"]["trainable_parameters"] = 10001
        self.assert_rejected(proposal, "$.representation_recipe.trainable_parameters")
        proposal = copy.deepcopy(self.fixture)
        proposal["search_parameters"]["learning_rate"] = 0.002
        self.assert_rejected(proposal, "$.search_parameters.learning_rate")
        proposal = copy.deepcopy(self.fixture)
        proposal["search_parameters"]["mask_fraction"] = 0.0
        self.assert_rejected(proposal, "$.search_parameters.mask_fraction")

    def test_output_caps_and_all_synthetic_zero_counters_are_enforced(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["requested_budget"]["maximum_generated_output_bytes"] = MAX_REPORT_BYTES + 1
        self.assert_rejected(proposal, "$.requested_budget.maximum_generated_output_bytes")
        proposal = copy.deepcopy(self.fixture)
        proposal["requested_budget"]["parameter_update_runs"] = 1
        self.assert_rejected(proposal, "$.requested_budget.parameter_update_runs")
        proposal = copy.deepcopy(self.fixture)
        proposal["access_counters"]["EEG_reads"] = 1
        self.assert_rejected(proposal, "$.access_counters.EEG_reads")

    def test_boolean_zero_and_untrusted_warning_text_are_rejected(self):
        proposal = copy.deepcopy(self.fixture)
        proposal["requested_budget"]["parameter_update_runs"] = False
        self.assert_rejected(proposal, "$.requested_budget.parameter_update_runs")
        proposal = copy.deepcopy(self.fixture)
        proposal["access_counters"]["EEG_reads"] = False
        self.assert_rejected(proposal, "$.access_counters.EEG_reads")
        proposal = copy.deepcopy(self.fixture)
        proposal["warnings"] = ["target text copied here"]
        report = self.assert_rejected(proposal, "$.warnings")
        self.assertNotIn("target text copied here", report.to_dict()["proposal_warnings"])

    def test_policy_summary_discloses_limits_and_unavailable_science(self):
        summary = inspect_ai_research_policy(self.policy)
        self.assertEqual(summary["maximum_trainable_parameters"], 10000)
        self.assertEqual(summary["maximum_future_fit_runs"], 12)
        self.assertEqual(summary["maximum_future_ai_proposal_runs"], 4)
        self.assertFalse(summary["real_or_protected_execution_authorized"])
        self.assertIn("EEG_hand_or_key_effect", summary["unavailable_fields"])

    def test_validation_envelope_reports_zero_runs_and_bounded_inputs(self):
        envelope = build_validation_envelope(POLICY, FIXTURE)
        self.assertTrue(envelope["accepted"])
        measurements = envelope["measurements"]
        self.assertGreater(measurements["policy_input_bytes"], 0)
        self.assertGreater(measurements["proposal_input_bytes"], 0)
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_bounded_writer_refuses_overwrite_and_oversized_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            written = write_bounded_json(path, {"ok": True}, maximum_bytes=64)
            self.assertEqual(written, path.stat().st_size)
            with self.assertRaises(FileExistsError):
                write_bounded_json(path, {"ok": True})
            with self.assertRaises(ValueError):
                write_bounded_json(Path(tmp) / "large.json", {"value": "x" * 100}, maximum_bytes=32)

    def test_canonical_json_rejects_nan(self):
        with self.assertRaises(ValueError):
            canonical_json_bytes({"value": float("nan")})
        self.assertEqual(len(sha256_json({"ok": True})), 64)

    def test_cli_inspect_make_validate_and_reject_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "proposal.json"
            report_path = Path(tmp) / "report.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["inspect-ai-research-policy", "--policy", str(POLICY)]), 0)
                self.assertEqual(
                    main(
                        [
                            "make-ai-research-proposal-fixture",
                            "--policy",
                            str(POLICY),
                            "--out",
                            str(generated),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    main(
                        [
                            "validate-ai-research-proposal",
                            "--policy",
                            str(POLICY),
                            "--proposal",
                            str(generated),
                            "--out-report",
                            str(report_path),
                        ]
                    ),
                    0,
                )
            self.assertLess(report_path.stat().st_size, MAX_REPORT_BYTES)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["accepted"])

            invalid = json.loads(generated.read_text(encoding="utf-8"))
            invalid["representation_recipe"]["uses_target_text"] = True
            invalid_path = Path(tmp) / "invalid.json"
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "validate-ai-research-proposal",
                            "--policy",
                            str(POLICY),
                            "--proposal",
                            str(invalid_path),
                        ]
                    ),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
