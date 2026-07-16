import inspect
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:  # pragma: no cover
    NUMPY_AVAILABLE = False

from neurodecodekit.experiments.train_only_failure_discrimination_gate import (
    StageBGateError,
    _enforce_resource_caps,
    _resolve_output_root,
    new_runtime_access_counters,
    run_static_stage_b_gate,
    run_target_blind_stage_b_gate,
    score_frozen_stage_b,
)


TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None
REPO_ROOT = Path(__file__).resolve().parents[1]


class TrainOnlyFailureDiscriminationGateTests(unittest.TestCase):
    def test_cli_exposes_all_five_staged_commands(self):
        from neurodecodekit.cli import build_parser

        help_text = build_parser().format_help()
        for command in (
            "loop48-stage-b-static-gate",
            "loop48-stage-b-create-derivatives",
            "loop48-stage-b-target-blind",
            "loop48-stage-b-inspect-freeze",
            "loop48-stage-b-score",
        ):
            self.assertIn(command, help_text)

    def test_counter_inventory_matches_frozen_contract(self):
        contract = json.loads(
            (
                REPO_ROOT / "registries" / "loop48_train_only_discrimination_contract.v0.json"
            ).read_text()
        )
        counters = new_runtime_access_counters()
        self.assertEqual(set(counters), set(contract["required_runtime_access_counters"]))
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_registered_stage_functions_keep_commit_and_green_evidence_gates(self):
        static = inspect.signature(run_static_stage_b_gate).parameters
        self.assertIn("implementation_commit", static)
        self.assertIn("implementation_push_ci_run_id", static)
        self.assertIn("implementation_pr_ci_run_id", static)
        target_blind = inspect.signature(run_target_blind_stage_b_gate).parameters
        self.assertIn("implementation_commit", target_blind)
        scoring = inspect.signature(score_frozen_stage_b).parameters
        self.assertIn("green_freeze_commit", scoring)
        self.assertIn("freeze_push_ci_run_id", scoring)
        self.assertIn("freeze_pr_ci_run_id", scoring)

    def test_output_root_is_scoped_and_resource_caps_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registered = _resolve_output_root(root, ".codex_work/loop48_stage_b", True)
            self.assertEqual(registered, (root / ".codex_work/loop48_stage_b").resolve())
            with self.assertRaisesRegex(StageBGateError, "registered execution output"):
                _resolve_output_root(root, "../another-project", True)
        caps = {
            "total_generated_artifact_bytes": 32,
            "maximum_checkpoint_bytes": 4,
            "maximum_prediction_payload_bytes": 4,
            "maximum_working_array_bytes": 16,
            "parameter_update_runtime_sec": 10,
            "end_to_end_runtime_sec": 20,
            "peak_rss_bytes": 1024,
        }
        with self.assertRaisesRegex(StageBGateError, "resource caps"):
            _enforce_resource_caps(
                caps,
                generated_bytes=33,
                checkpoint_bytes=0,
                prediction_bytes=0,
                working_array_bytes=0,
                parameter_runtime=0,
                end_to_end_runtime=0,
                peak_rss=0,
            )


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class TrainOnlyFailureDiscriminationGateArrayTests(unittest.TestCase):
    def test_target_blind_derivative_validation_rejects_targets_and_overlap(self):
        from neurodecodekit.experiments.train_only_failure_discrimination_gate import (
            _validate_target_blind_derivatives,
        )

        channels = np.asarray([f"M{index:03d}" for index in range(102)])
        fit = {
            "signals": np.zeros((44, 102, 8), dtype="float32"),
            "channel_names": channels,
            "item_ids": np.asarray([f"fit-{index}" for index in range(44)]),
            "metadata": {
                "source_cache_sha256": "a" * 64,
                "diagnostic_assignment_sha256": "b" * 64,
            },
        }
        check = {
            "signals": np.zeros((11, 102, 8), dtype="float32"),
            "channel_names": channels.copy(),
            "item_ids": np.asarray([f"check-{index}" for index in range(11)]),
            "metadata": {
                "source_cache_sha256": "a" * 64,
                "diagnostic_assignment_sha256": "b" * 64,
            },
        }
        _validate_target_blind_derivatives(fit, check)
        check["target_texts"] = np.asarray(["LEAK"] * 11)
        with self.assertRaisesRegex(StageBGateError, "forbidden target"):
            _validate_target_blind_derivatives(fit, check)
        check.pop("target_texts")
        check["item_ids"][0] = fit["item_ids"][0]
        with self.assertRaisesRegex(StageBGateError, "overlap"):
            _validate_target_blind_derivatives(fit, check)

    def test_transformed_audit_detects_padding_and_keeps_check_targets_unavailable(self):
        from neurodecodekit.experiments.train_only_failure_discrimination_gate import (
            transformed_cache_audit,
        )

        rng = np.random.default_rng(48)
        fit = rng.standard_normal((44, 102, 12), dtype=np.float32)
        check = rng.standard_normal((11, 102, 12), dtype=np.float32)
        fit_lengths = np.full(44, 10, dtype="int32")
        check_lengths = np.full(11, 10, dtype="int32")
        fit[:, :, 10:] = 0
        check[:, :, 10:] = 0
        target_ids = np.zeros((44, 3), dtype="int16")
        target_ids[:, 0] = 1
        target_lengths = np.ones(44, dtype="int32")
        clean = transformed_cache_audit(
            fit_signals=fit,
            fit_input_lengths=fit_lengths,
            fit_target_token_ids=target_ids,
            fit_target_lengths=target_lengths,
            fit_item_ids=[f"fit-{index}" for index in range(44)],
            check_signals=check,
            check_input_lengths=check_lengths,
            check_item_ids=[f"check-{index}" for index in range(11)],
            sampling_rate_hz=100.0,
        )
        self.assertFalse(clean["gross_defect"])
        self.assertFalse(clean["scope"]["check_target_lengths_available_before_green_freeze"])
        check[0, 0, 11] = 1.0
        dirty = transformed_cache_audit(
            fit_signals=fit,
            fit_input_lengths=fit_lengths,
            fit_target_token_ids=target_ids,
            fit_target_lengths=target_lengths,
            fit_item_ids=[f"fit-{index}" for index in range(44)],
            check_signals=check,
            check_input_lengths=check_lengths,
            check_item_ids=[f"check-{index}" for index in range(11)],
            sampling_rate_hz=100.0,
        )
        self.assertTrue(dirty["gross_defect"])
        self.assertEqual(dirty["nonzero_padding_count"], 1)


@unittest.skipUnless(NUMPY_AVAILABLE and TORCH_AVAILABLE, "NumPy and Torch not installed")
class TrainOnlyFailureDiscriminationTrainingTests(unittest.TestCase):
    def test_seed_4801_replays_deterministically_on_synthetic_arrays(self):
        from neurodecodekit.experiments.train_only_failure_discrimination_gate import (
            _array_map_sha256,
            _train_exact_registered_fit,
        )

        rng = np.random.default_rng(4801)
        signals = rng.standard_normal((2, 102, 8), dtype=np.float32)
        lengths = np.asarray([8, 8], dtype="int64")
        target_ids = np.zeros((2, 2), dtype="int64")
        target_ids[:, 0] = np.asarray([1, 2])
        target_lengths = np.ones(2, dtype="int64")
        first = _train_exact_registered_fit(
            signals=signals,
            input_lengths=lengths,
            target_token_ids=target_ids,
            target_lengths=target_lengths,
            architecture="candidate",
            execution_seed=4801,
        )
        second = _train_exact_registered_fit(
            signals=signals,
            input_lengths=lengths,
            target_token_ids=target_ids,
            target_lengths=target_lengths,
            architecture="candidate",
            execution_seed=4801,
        )
        first_arrays = {
            name: value.detach().cpu().numpy()
            for name, value in first["model"].state_dict().items()
        }
        second_arrays = {
            name: value.detach().cpu().numpy()
            for name, value in second["model"].state_dict().items()
        }
        self.assertEqual(_array_map_sha256(first_arrays), _array_map_sha256(second_arrays))
        self.assertEqual(first["telemetry"], second["telemetry"])
        self.assertEqual(first["loss_history_sha256"], second["loss_history_sha256"])

    def test_full_synthetic_target_blind_orchestration_freezes_exact_inventory(self):
        from neurodecodekit.evaluation.train_only_failure_discrimination import (
            validate_prediction_freeze_record,
        )
        from neurodecodekit.experiments import train_only_failure_discrimination_gate as gate

        rng = np.random.default_rng(4800)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "loop48_stage_b"
            output.mkdir()
            channels = np.asarray([f"M{index:03d}" for index in range(102)])
            fit_signals = rng.standard_normal((44, 102, 8), dtype=np.float32)
            check_signals = rng.standard_normal((11, 102, 8), dtype=np.float32)
            fit_lengths = np.full(44, 8, dtype="int32")
            check_lengths = np.full(11, 8, dtype="int32")
            target_ids = np.zeros((44, 2), dtype="int16")
            target_ids[:, 0] = 1 + (np.arange(44) % 3)
            target_lengths = np.ones(44, dtype="int32")
            target_texts = np.asarray(
                [chr(ord("A") + int(value) - 1) for value in target_ids[:, 0]]
            )
            common = {
                "source_cache_sha256": "a" * 64,
                "diagnostic_assignment_sha256": "b" * 64,
            }
            fit_arrays = {
                "signals": fit_signals,
                "input_lengths": fit_lengths,
                "target_token_ids": target_ids,
                "target_lengths": target_lengths,
                "target_texts": target_texts,
                "channel_names": channels,
                "source_row_indices": np.arange(44, dtype="int32"),
                "item_ids": np.asarray([f"fit-{index}" for index in range(44)]),
                "semantic_ids": np.asarray([f"semantic-{index}" for index in range(44)]),
            }
            check_arrays = {
                "signals": check_signals,
                "input_lengths": check_lengths,
                "channel_names": channels,
                "source_row_indices": np.arange(44, 55, dtype="int32"),
                "item_ids": np.asarray([f"check-{index}" for index in range(11)]),
                "semantic_ids": np.asarray([f"semantic-{index}" for index in range(44, 55)]),
            }
            gate._write_npz(
                output / gate.FIT_BUNDLE_NAME,
                fit_arrays,
                {
                    "schema": {
                        "name": "neurodecodekit.loop48_stage_b_fit_bundle",
                        "version": 0,
                    },
                    "contains_targets": True,
                    **common,
                },
            )
            gate._write_npz(
                output / gate.CHECK_INPUTS_NAME,
                check_arrays,
                {
                    "schema": {
                        "name": "neurodecodekit.loop48_stage_b_check_inputs",
                        "version": 0,
                    },
                    "contains_targets": False,
                    **common,
                },
            )
            counters = new_runtime_access_counters()
            counters.update(
                {
                    "source_cache_stat_reads": 1,
                    "source_cache_hash_passes": 1,
                    "split_report_metadata_reads": 1,
                    "archive_header_reads": 14,
                    "archive_row_member_streams": 7,
                    "fit_signal_rows_delivered": 44,
                    "fit_target_rows_delivered": 44,
                    "check_signal_rows_delivered": 11,
                }
            )
            (output / gate.STATIC_REPORT_NAME).write_text(
                json.dumps({"resources": {"runtime_sec": 0.01}}), encoding="utf-8"
            )
            (output / gate.DERIVATIVE_REPORT_NAME).write_text(
                json.dumps(
                    {
                        "status": "passed",
                        "access_counters": counters,
                        "static_audit": {
                            "infeasible_row_count": 0,
                            "gross_defect": False,
                        },
                        "resources": {"runtime_sec": 0.01},
                    }
                ),
                encoding="utf-8",
            )
            freeze_path = Path(tmp) / "freeze.json"
            head = gate._git_head(REPO_ROOT)
            with (
                mock.patch.object(gate, "_git_head", return_value=head),
                mock.patch.object(gate, "_tracked_worktree_clean", return_value=True),
            ):
                report = gate.run_target_blind_stage_b_gate(
                    repo_root=REPO_ROOT,
                    implementation_commit=head,
                    freeze_record_out=freeze_path,
                    output_root=output,
                    enforce_registered_paths=False,
                )
            freeze = json.loads(freeze_path.read_text())
            validate_prediction_freeze_record(freeze)
            self.assertEqual(report["status"], "predictions_frozen_check_targets_unavailable")
            self.assertEqual(len(report["fit_condition_ids"]), 20)
            self.assertEqual(len(report["prediction_condition_ids"]), 41)
            self.assertEqual(freeze["access_counters"]["optimizer_steps"], 4800)
            self.assertEqual(freeze["access_counters"]["target_blind_model_inference_runs"], 35)
            self.assertEqual(freeze["check_target_rows_delivered"], 0)


if __name__ == "__main__":
    unittest.main()
