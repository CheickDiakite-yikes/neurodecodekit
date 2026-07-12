import copy
import tempfile
import types
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock


class LocalPrecisionRuntimeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            import torch
        except ImportError:
            raise unittest.SkipTest("NumPy and PyTorch are optional") from None
        cls.np = np
        cls.torch = torch

    def _fixture(self, root: Path) -> Path:
        from neurodecodekit.training.precision_runtime_fixture import (
            PrecisionRuntimeFixtureProtocol,
            prepare_precision_runtime_fixture,
        )

        protocol = PrecisionRuntimeFixtureProtocol(
            selection_seed=9401,
            qualification_seed=9402,
            items_per_partition=12,
            items_per_family=2,
            channels=5,
            sampling_rate_hz=100.0,
            minimum_samples=16,
            maximum_samples=32,
            length_multiple_samples=4,
            value_min=-4.0,
            value_max=4.0,
        )
        output = root / "fixture"
        prepare_precision_runtime_fixture(
            output,
            max_total_bytes=128 * 1024,
            protocol=protocol,
            require_registered_protocol=False,
        )
        return output / "manifest.json"

    def _checkpoint(self, root: Path) -> Path:
        from neurodecodekit.models.tiny_causal_encoder import (
            TinyCausalEncoderConfig,
            _build_model,
            save_tiny_causal_encoder_checkpoint,
        )

        torch = self.torch
        torch.manual_seed(9240)
        model = _build_model(
            torch,
            input_dim=5 * 16,
            hidden_dim=12,
            embedding_dim=8,
            n_classes=6,
        ).to("cpu")
        model.eval()
        parameter_count = sum(int(value.numel()) for value in model.parameters())
        training = types.SimpleNamespace(
            model=model,
            normalization_mean=self.np.linspace(-0.2, 0.2, 5, dtype="float32"),
            normalization_std=self.np.linspace(0.8, 1.2, 5, dtype="float32"),
            parameter_count=parameter_count,
            encoder_parameter_count=1076,
            probe_parameter_count=54,
            parameter_bytes_float32=parameter_count * 4,
            best_epoch=1,
            config=TinyCausalEncoderConfig(),
        )
        path = root / "test-checkpoint.npz"
        save_tiny_causal_encoder_checkpoint(
            path,
            training=training,
            metadata={
                "proof_posture": "nonregistered_target_free_test_mechanics_only",
                "geometry": {
                    "n_channels": 5,
                    "kernel_size": 16,
                    "stride": 4,
                    "n_classes": 6,
                    "sampling_rate_hz": 100.0,
                },
                "selection_frozen_before_test": True,
                "training_runs_for_loop24": 0,
            },
        )
        return path

    @staticmethod
    def _fake_profiler(candidate, _frame):
        required = candidate.candidate_id == "dynamic_qint8_qnnpack"
        return {
            "required": required,
            "passed": True,
            "required_operator_contains": (
                "quantized::linear_dynamic" if required else None
            ),
            "operator_names": (
                ["quantized::linear_dynamic"] if required else []
            ),
            "raw_trace_saved": False,
        }

    @staticmethod
    def _timing_runner(ratios):
        def run(_payload, candidate_id, frames):
            value = float(ratios[candidate_id]) * 100.0
            path = {
                "raw_times_sec": [value / 1e9 * frames.frame_count],
                "number_per_run": 1,
                "measurement_repeats": 1,
                "median_ns_per_frame": value,
                "p25_ns_per_frame": value,
                "p75_ns_per_frame": value,
                "p95_ns_per_frame": value,
                "iqr_over_median": 0.0,
                "timer_threshold_iqr_over_median": 0.1,
                "timer_min_run_time_sec": 0.05,
                "timer_max_run_time_sec": 0.25,
                "timer_num_threads": 1,
            }
            return {
                "frames_per_call": frames.frame_count,
                "candidate_construct_sec": 0.001,
                "first_frame_sec": 0.0001,
                "imported_empty_worker_peak_rss_bytes": 32 * 1024 * 1024,
                "worker_peak_rss_bytes": 64 * 1024 * 1024,
                "worker_peak_rss_delta_bytes": 32 * 1024 * 1024,
                "candidate_construction_temporary_bytes": 1024,
                "paths": {
                    "producer_frame_normalize_encode_probe": dict(path),
                    "fixed_float64_decoder_frame_update": dict(path),
                    "full_incremental_frame_pipeline": dict(path),
                },
                "candidate_materialized_from_in_memory_payload": True,
                "checkpoint_reads": 0,
                "partition_file_opens": 0,
            }

        return run

    def _run_gate(
        self,
        root: Path,
        *,
        forced_qualification: bool,
        failed_candidate: str | None = None,
    ):
        import neurodecodekit.experiments.local_precision_runtime_gate as gate

        fixture = self._fixture(root)
        checkpoint = self._checkpoint(root)
        ratios = {
            "float32_eager_reference": 1.0,
            "float16_eager_cpu": 0.7 if forced_qualification else 1.2,
            "dynamic_qint8_qnnpack": 1.3,
        }
        measured_runner = self._timing_runner(ratios)

        def timing_runner(payload, candidate_id, frames):
            if candidate_id == failed_candidate:
                raise RuntimeError("intentional test timing refusal")
            return measured_runner(payload, candidate_id, frames)

        patches = [
            mock.patch.object(gate, "profile_candidate_operator", self._fake_profiler)
        ]
        if forced_qualification:
            patches.extend(
                [
                    mock.patch.object(
                        gate,
                        "_compare_candidate_replay",
                        return_value={"passed": True},
                    ),
                    mock.patch.object(
                        gate,
                        "_select_candidate",
                        return_value={
                            "default_before_gate": "float32_eager_reference",
                            "status": (
                                "provisional_replacement_requires_one_time_qualification"
                            ),
                            "provisional_replacement_candidate": "float16_eager_cpu",
                            "replacement_candidates_passing": ["float16_eager_cpu"],
                            "storage_only_candidates": [],
                            "candidate_results": {},
                            "qualification_required": True,
                            "thresholds_candidates_and_fixture_changed_after_open": False,
                            "tie_break": [],
                        },
                    ),
                ]
            )
        with patches[0]:
            if len(patches) == 1:
                return gate.run_local_precision_runtime_gate(
                    fixture_manifest_path=fixture,
                    checkpoint_path=checkpoint,
                    out_dir=root / "gate",
                    require_registered_environment=False,
                    require_registered_fixture=False,
                    require_registered_checkpoint=False,
                    enforce_authorized_output_root=False,
                    timing_worker_runner=timing_runner,
                )
            with patches[1], patches[2]:
                return gate.run_local_precision_runtime_gate(
                    fixture_manifest_path=fixture,
                    checkpoint_path=checkpoint,
                    out_dir=root / "gate",
                    require_registered_environment=False,
                    require_registered_fixture=False,
                    require_registered_checkpoint=False,
                    enforce_authorized_output_root=False,
                    timing_worker_runner=timing_runner,
                )

    def test_no_replacement_keeps_qualification_physically_unopened_and_is_inspectable(self):
        from neurodecodekit.experiments.local_precision_runtime_gate import (
            CANDIDATE_IDS,
            inspect_local_precision_runtime_report,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self._run_gate(root, forced_qualification=False)
            available = sum(
                report["candidates"][name]["status"] == "available"
                for name in CANDIDATE_IDS
            )
            self.assertFalse(report["qualification"]["opened"])
            self.assertEqual(report["access"]["counters"]["qualification_partition_opens"], 0)
            self.assertEqual(
                report["access"]["counters"]["timing_worker_processes"],
                available * 12,
            )
            self.assertEqual(
                [row["index"] for row in report["access"]["ordered_events"]],
                list(range(12)),
            )
            self.assertLessEqual(report["resources"]["report_bytes"], 1024 * 1024)
            self.assertLessEqual(
                report["resources"]["total_generated_bytes"], 4 * 1024 * 1024
            )
            summary = inspect_local_precision_runtime_report(root / "gate" / "gate.json")
            self.assertFalse(summary["qualification_opened"])
            self.assertTrue(summary["producer_causal"])
            self.assertFalse(summary["end_to_end_latency_measured"])

    def test_selected_candidate_opens_qualification_once_after_selection_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._run_gate(Path(tmp), forced_qualification=True)
            self.assertTrue(report["qualification"]["opened"])
            self.assertEqual(report["qualification"]["candidate_id"], "float16_eager_cpu")
            self.assertEqual(report["access"]["counters"]["qualification_partition_opens"], 1)
            events = report["access"]["ordered_events"]
            self.assertIn("selection_report", events[8]["registered_step"])
            self.assertIn("qualification", events[9]["registered_step"])
            self.assertEqual(events[10]["details"]["compared_candidates"], [
                "float32_eager_reference",
                "float16_eager_cpu",
            ])

    def test_incomplete_available_candidate_timing_parks_without_qualification(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._run_gate(
                Path(tmp),
                forced_qualification=False,
                failed_candidate="float16_eager_cpu",
            )
        self.assertFalse(report["gate_passed"])
        self.assertFalse(report["resources"]["timing_protocol_passed"])
        self.assertEqual(
            report["decision"],
            "park_timer_protocol_or_balanced_order_mismatch",
        )
        self.assertFalse(report["qualification"]["opened"])

    def test_frozen_selection_rules_separate_replacement_from_storage_only(self):
        import neurodecodekit.experiments.local_precision_runtime_gate as gate

        provenance = {
            "fallback_used": False,
            "autocast_used": False,
            "compile_used": False,
            "architecture_changed": False,
            "training_runs": 0,
            "parameter_updates": 0,
        }
        records = {}
        for candidate_id, payload_bytes in (
            ("float32_eager_reference", 10_000),
            ("float16_eager_cpu", 9_000),
            ("dynamic_qint8_qnnpack", 4_000),
        ):
            records[candidate_id] = {
                "status": "available",
                "provenance": dict(provenance),
                "profiler": {"required": False, "passed": True},
                "correctness": {"passed": True},
                "storage": {
                    "deterministic_serialized_numeric_payload_bytes": payload_bytes
                },
            }
        timing = {
            "candidates": {
                "float32_eager_reference": self._aggregate_row(1.0),
                "float16_eager_cpu": self._aggregate_row(0.75),
                "dynamic_qint8_qnnpack": self._aggregate_row(1.0),
            }
        }
        selection = gate._select_candidate(
            candidate_records=records,
            timing=timing,
            contract=gate._load_contract(),
        )
        self.assertEqual(selection["provisional_replacement_candidate"], "float16_eager_cpu")
        self.assertEqual(selection["storage_only_candidates"], ["dynamic_qint8_qnnpack"])

    @staticmethod
    def _aggregate_row(ratio):
        interval = {"lower": ratio, "upper": ratio, "resamples": 2000}
        paths = {
            name: {
                "paired_latency_ratio": ratio,
                "p95_latency_ratio": ratio,
                "paired_latency_ratio_bootstrap_95_interval": dict(interval),
            }
            for name in (
                "producer_frame_normalize_encode_probe",
                "fixed_float64_decoder_frame_update",
                "full_incremental_frame_pipeline",
            )
        }
        return {
            "status": "measured",
            "paths": paths,
            "worker_peak_rss_delta_bytes_median": 32 * 1024 * 1024,
        }

    def test_bootstrap_replay_is_deterministic_and_empty_is_explicit(self):
        from neurodecodekit.experiments.local_precision_runtime_gate import (
            _paired_bootstrap_interval,
        )

        first = _paired_bootstrap_interval(
            [0.7, 0.8, 0.75, 0.72], seed=2404, resamples=2000
        )
        second = _paired_bootstrap_interval(
            [0.7, 0.8, 0.75, 0.72], seed=2404, resamples=2000
        )
        self.assertEqual(first, second)
        self.assertLessEqual(first["lower"], first["upper"])
        self.assertEqual(
            _paired_bootstrap_interval([], seed=2404, resamples=2000),
            {"lower": None, "upper": None, "resamples": 2000},
        )

    def test_real_isolated_worker_runs_timer_without_file_reopens(self):
        import neurodecodekit.experiments.local_precision_runtime_gate as gate
        from neurodecodekit.models.precision_candidates import (
            FLOAT32_REFERENCE,
            extract_frozen_producer_payload,
        )
        from neurodecodekit.models.tiny_causal_encoder import (
            load_tiny_causal_encoder_checkpoint,
        )
        from neurodecodekit.training.precision_runtime_fixture import (
            load_precision_runtime_partition,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            checkpoint = self._checkpoint(root)
            producer, _metadata = load_tiny_causal_encoder_checkpoint(checkpoint)
            partition = load_precision_runtime_partition(
                manifest,
                "selection",
                require_registered_protocol=False,
            )
            frames = gate._extract_frame_bundle(producer, partition)
            result = gate._run_timing_worker(
                extract_frozen_producer_payload(producer),
                FLOAT32_REFERENCE,
                frames,
            )
        self.assertEqual(result["frames_per_call"], frames.frame_count)
        self.assertEqual(result["checkpoint_reads"], 0)
        self.assertEqual(result["partition_file_opens"], 0)
        self.assertEqual(set(result["paths"]), set(gate.TIMED_PATHS))
        self.assertTrue(
            all(row["median_ns_per_frame"] > 0 for row in result["paths"].values())
        )

    def test_artifact_tamper_and_report_cap_fail_closed(self):
        import neurodecodekit.experiments.local_precision_runtime_gate as gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self._run_gate(root, forced_qualification=False)
            report_path = root / "gate" / "gate.json"
            payload_name = next(iter(report["artifacts"]["candidate_payloads"].values()))[
                "file"
            ]
            payload_path = root / "gate" / payload_name
            original_payload = payload_path.read_bytes()
            payload_path.write_bytes(original_payload + b"tamper")
            with self.assertRaisesRegex(ValueError, "byte count mismatch"):
                gate.inspect_local_precision_runtime_report(report_path)
            payload_path.write_bytes(original_payload)

            original_report = report_path.read_bytes()
            report_path.write_bytes(original_report.replace(b"retain_float32", b"retain-float32", 1))
            with self.assertRaisesRegex(ValueError, "hash binding mismatch"):
                gate.inspect_local_precision_runtime_report(report_path)
            report_path.write_bytes(original_report)

            capped_dir = root / "capped"
            capped_dir.mkdir()
            (capped_dir / "selection.json").write_bytes(
                (root / "gate" / "selection.json").read_bytes()
            )
            tiny_caps = replace(gate.LocalPrecisionRuntimeCaps(), maximum_report_bytes_total=64)
            with self.assertRaises(gate.Loop24GateRefusal) as raised:
                gate._write_final_artifacts(
                    output_dir=capped_dir,
                    report=copy.deepcopy(report),
                    payload_bytes={},
                    fixture_bytes=0,
                    caps=tiny_caps,
                )
            self.assertEqual(raised.exception.refusal_id, "resource_cap_exceeded")

    def test_unsafe_output_and_forbidden_access_refuse_before_expansion(self):
        import neurodecodekit.experiments.local_precision_runtime_gate as gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(gate.Loop24GateRefusal) as collision:
                gate._validate_output_directory(
                    existing, enforce_authorized_output_root=False
                )
            self.assertEqual(collision.exception.refusal_id, "output_collision_or_unsafe_path")
            with self.assertRaises(gate.Loop24GateRefusal) as unsafe:
                gate._validate_output_directory(
                    root / "not-authorized", enforce_authorized_output_root=True
                )
            self.assertEqual(unsafe.exception.refusal_id, "output_collision_or_unsafe_path")

        counters = gate._new_access_counters()
        counters.update(
            {
                "manifest_metadata_reads": 1,
                "checkpoint_file_reads": 1,
                "selection_partition_opens": 1,
                "candidate_conversions": 1,
                "real_data_reads": 1,
            }
        )
        with self.assertRaises(gate.Loop24GateRefusal) as forbidden:
            gate._validate_access_boundary(counters)
        self.assertEqual(
            forbidden.exception.refusal_id,
            "consumed_seed_or_real_evidence_accessed",
        )

    def test_cli_exposes_only_the_frozen_loop24_inputs(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        fixture = parser.parse_args(
            ["make-precision-runtime-fixture", "--out-dir", ".codex_work/loop24/fixture"]
        )
        inspect_fixture = parser.parse_args(
            ["inspect-precision-runtime-fixture", "--manifest", "manifest.json"]
        )
        gate = parser.parse_args(
            [
                "local-precision-runtime-gate",
                "--fixture-manifest",
                "manifest.json",
                "--out-dir",
                ".codex_work/loop24/gate",
            ]
        )
        inspect_report = parser.parse_args(
            ["inspect-local-precision-runtime-report", "--report", "gate.json"]
        )
        self.assertEqual(fixture.func.__name__, "_cmd_make_precision_runtime_fixture")
        self.assertEqual(
            inspect_fixture.func.__name__, "_cmd_inspect_precision_runtime_fixture"
        )
        self.assertEqual(gate.func.__name__, "_cmd_local_precision_runtime_gate")
        self.assertEqual(
            gate.checkpoint,
            "cache/loop22_tiny_causal_encoder/checkpoint.npz",
        )
        self.assertEqual(
            inspect_report.func.__name__, "_cmd_inspect_local_precision_runtime_report"
        )
        for forbidden_name in ("seed", "training", "target", "real_data", "candidate"):
            self.assertNotIn(forbidden_name, vars(gate))


if __name__ == "__main__":
    unittest.main()
