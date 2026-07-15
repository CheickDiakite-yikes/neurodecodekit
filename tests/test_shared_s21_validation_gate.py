import tempfile
import unittest
from pathlib import Path


try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:  # pragma: no cover
    NUMPY_AVAILABLE = False


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class SharedS21ValidationGateTests(unittest.TestCase):
    def test_runtime_counter_inventory_matches_frozen_contract(self):
        import json

        from neurodecodekit.experiments.shared_s21_validation_gate import (
            new_runtime_access_counters,
        )

        contract = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "registries"
                / "loop26_shared_validation_contract.v0.json"
            ).read_text()
        )
        counters = new_runtime_access_counters()
        self.assertEqual(set(counters), set(contract["required_runtime_access_counters"]))
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_target_blind_derivative_validation_rejects_targets_and_identity_drift(self):
        from neurodecodekit.experiments.shared_s21_validation_gate import (
            SharedS21GateError,
            _validate_target_blind_derivatives,
        )

        channel_names = np.asarray([f"M{index:03d}" for index in range(102)])
        train = {
            "signals": np.zeros((55, 102, 8), dtype="float32"),
            "channel_names": channel_names,
            "metadata": {"source_cache_sha256": "a" * 64},
        }
        validation = {
            "signals": np.zeros((6, 102, 8), dtype="float32"),
            "channel_names": channel_names.copy(),
            "metadata": {"source_cache_sha256": "a" * 64},
        }
        _validate_target_blind_derivatives(train, validation)
        validation["target_texts"] = np.asarray(list("ABCDEF"))
        with self.assertRaisesRegex(SharedS21GateError, "forbidden target"):
            _validate_target_blind_derivatives(train, validation)
        validation.pop("target_texts")
        validation["metadata"]["source_cache_sha256"] = "b" * 64
        with self.assertRaisesRegex(SharedS21GateError, "different sources"):
            _validate_target_blind_derivatives(train, validation)

    def test_split_binding_rejects_duplicates_and_output_root_is_scoped(self):
        from neurodecodekit.experiments.shared_s21_validation_gate import (
            SharedS21GateError,
            _partition_indices,
            _resolve_output_root,
        )

        split = {
            "membership": {
                "rows": [
                    {"source_row_index": 0, "split": "train"},
                    {"source_row_index": 0, "split": "val"},
                ]
            }
        }
        with self.assertRaisesRegex(SharedS21GateError, "duplicated"):
            _partition_indices(split)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registered = _resolve_output_root(root, ".codex_work/loop26", True)
            self.assertEqual(registered, (root / ".codex_work/loop26").resolve())
            with self.assertRaisesRegex(SharedS21GateError, "registered execution output"):
                _resolve_output_root(root, "../other-project", True)

    def test_cli_exposes_staged_commands(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        help_text = parser.format_help()
        for command in (
            "loop26-static-gate",
            "loop26-create-derivatives",
            "loop26-target-blind-gate",
            "loop26-inspect-freeze",
            "loop26-score",
        ):
            self.assertIn(command, help_text)

    def test_exact_counters_caps_and_tracked_freeze_gate_fail_closed(self):
        from neurodecodekit.experiments.shared_s21_validation_gate import (
            EXACT_TARGET_BLIND_COUNTERS,
            SharedS21GateError,
            _enforce_run_caps,
            _path_tracked_at_head,
            _validate_exact_target_blind_counters,
            _validate_exact_scoring_counters,
        )

        counters = {name: 0 for name in EXACT_TARGET_BLIND_COUNTERS}
        counters.update(EXACT_TARGET_BLIND_COUNTERS)
        _validate_exact_target_blind_counters(counters)
        scored = dict(counters)
        scored.update(
            {
                "archive_header_reads": 22,
                "archive_row_member_streams": 10,
                "validation_target_rows_delivered_after_prediction_freeze": 6,
                "validation_scoring_runs": 1,
            }
        )
        _validate_exact_scoring_counters(scored)
        counters["target_blind_model_inference_runs"] = 23
        with self.assertRaisesRegex(SharedS21GateError, "counter"):
            _validate_exact_target_blind_counters(counters)

        caps = {
            "total_generated_artifact_bytes": 32,
            "maximum_checkpoint_bytes": 4,
            "maximum_prediction_payload_bytes": 2,
            "total_parameter_update_runtime_sec": 1200,
            "total_end_to_end_runtime_sec": 1500,
            "peak_rss_bytes": 1024,
        }
        with self.assertRaisesRegex(SharedS21GateError, "generated artifacts"):
            _enforce_run_caps(
                caps,
                generated_bytes=33,
                checkpoint_bytes=0,
                prediction_bytes=0,
                parameter_runtime=0,
                end_to_end_runtime=0,
                peak_rss=0,
            )

        root = Path(__file__).resolve().parents[1]
        self.assertTrue(
            _path_tracked_at_head(
                root, root / "registries/loop26_shared_validation_contract.v0.json"
            )
        )
        self.assertFalse(_path_tracked_at_head(root, root.parent / "outside-freeze.json"))

    def test_working_array_bound_counts_resident_and_transform_copies(self):
        from neurodecodekit.experiments.shared_s21_validation_gate import (
            _target_blind_working_array_upper_bound,
        )

        train = {
            "signals": np.zeros((55, 102, 8), dtype="float32"),
            "input_lengths": np.zeros(55, dtype="int32"),
            "metadata": {},
        }
        validation = {
            "signals": np.zeros((6, 102, 8), dtype="float32"),
            "input_lengths": np.zeros(6, dtype="int32"),
            "metadata": {},
        }
        resident = sum(
            value.nbytes
            for bundle in (train, validation)
            for value in bundle.values()
            if hasattr(value, "nbytes")
        )
        expected = resident + 2 * train["signals"].nbytes
        self.assertEqual(_target_blind_working_array_upper_bound(train, validation), expected)


if __name__ == "__main__":
    unittest.main()
