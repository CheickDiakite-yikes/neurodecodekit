import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class CausalPreprocessingGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            import scipy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("NumPy and SciPy are optional") from None
        cls.np = np

    def _bundle(self, root: Path) -> Path:
        from neurodecodekit.preprocess.causal_preprocessing import (
            make_test_filter_bundle,
            save_filter_bundle,
        )

        bundle = make_test_filter_bundle(
            self.np.asarray([[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]], dtype="float64")
        )
        static = root / "static"
        static.mkdir()
        path = static / "filter_bundle.json"
        save_filter_bundle(path, bundle, {"passed": True, "warnings": []})
        return path

    def _fixture(self, root: Path, bundle: Path) -> Path:
        from neurodecodekit.training.causal_preprocessing_fixture import (
            CausalPreprocessingFixtureProtocol,
            prepare_causal_preprocessing_fixture,
        )

        protocol = CausalPreprocessingFixtureProtocol(
            development_seed=9601,
            qualification_seed=9602,
            item_lengths=tuple([1001] * 12),
        )
        output = root / "fixture"
        prepare_causal_preprocessing_fixture(
            output,
            static_filter_bundle_path=bundle,
            protocol=protocol,
            require_registered_protocol=False,
            require_static_gate=True,
            enforce_authorized_output_root=False,
        )
        return output / "manifest.json"

    def test_injected_static_gate_has_exact_counters_and_bounded_report(self):
        from neurodecodekit.experiments.causal_preprocessing_gate import (
            inspect_causal_preprocessing_report,
            run_static_causal_preprocessing_gate,
        )
        from neurodecodekit.preprocess.causal_preprocessing import make_test_filter_bundle

        bundle = make_test_filter_bundle(
            self.np.asarray([[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]], dtype="float64")
        )
        audit = {"passed": True, "warnings": [], "checks": {"injected": True}}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "static-gate"
            report = run_static_causal_preprocessing_gate(
                out_dir=output,
                enforce_authorized_output_root=False,
                require_registered_environment=False,
                design_factory=lambda: bundle,
                audit_runner=lambda _: audit,
            )
            self.assertTrue(report["gate_passed"])
            self.assertTrue(report["access"]["exact_counter_match"])
            self.assertEqual(report["access"]["counters"]["filter_design_runs"], 1)
            summary = inspect_causal_preprocessing_report(output / "static_gate.json")
            self.assertTrue(summary["gate_passed"])

    def test_complete_gate_passes_exact_schedule_and_opens_qualification_once(self):
        from neurodecodekit.experiments.causal_preprocessing_gate import (
            inspect_causal_preprocessing_report,
            run_causal_preprocessing_gate,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self._bundle(root)
            fixture = self._fixture(root, bundle)
            output = root / "gate"
            report = run_causal_preprocessing_gate(
                fixture_manifest_path=fixture,
                filter_bundle_path=bundle,
                out_dir=output,
                enforce_authorized_output_root=False,
                require_registered_environment=False,
                require_registered_fixture=False,
                require_registered_filter=False,
            )
            self.assertTrue(report["gate_passed"])
            self.assertTrue(report["access"]["exact_counter_match"])
            counters = report["access"]["counters"]
            self.assertEqual(counters["canonical_preprocessing_runs"], 24)
            self.assertEqual(counters["chunk_schedule_runs"], 168)
            self.assertEqual(counters["resume_runs"], 240)
            self.assertEqual(counters["future_mutation_control_runs"], 72)
            self.assertEqual(counters["qualification_partition_opens"], 1)
            self.assertEqual(counters["model_runs"], 0)
            self.assertTrue(report["resources"]["all_caps_passed"])
            self.assertGreater(report["resources"]["input_bytes"], 0)
            self.assertGreater(report["resources"]["output_bytes"], 0)
            summary = inspect_causal_preprocessing_report(output / "gate.json")
            self.assertTrue(summary["gate_passed"])

    def test_development_failure_keeps_qualification_physically_unopened(self):
        import neurodecodekit.experiments.causal_preprocessing_gate as gate

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self._bundle(root)
            fixture = self._fixture(root, bundle)
            original_loader = gate.load_causal_preprocessing_partition
            opened = []

            def recording_loader(*args, **kwargs):
                opened.append(args[1])
                return original_loader(*args, **kwargs)

            with (
                mock.patch.object(gate, "load_causal_preprocessing_partition", recording_loader),
                mock.patch.object(gate, "_runs_bitwise_equal", return_value=False),
            ):
                report = gate.run_causal_preprocessing_gate(
                    fixture_manifest_path=fixture,
                    filter_bundle_path=bundle,
                    out_dir=root / "failed-gate",
                    enforce_authorized_output_root=False,
                    require_registered_environment=False,
                    require_registered_fixture=False,
                    require_registered_filter=False,
                )
            self.assertEqual(opened, ["development"])
            self.assertFalse(report["gate_passed"])
            self.assertFalse(report["qualification"]["opened"])
            self.assertEqual(report["access"]["counters"]["qualification_partition_opens"], 0)
            self.assertTrue(report["access"]["exact_counter_match"])

    def test_report_hash_tamper_is_refused(self):
        from neurodecodekit.experiments.causal_preprocessing_gate import (
            inspect_causal_preprocessing_report,
            run_static_causal_preprocessing_gate,
        )
        from neurodecodekit.preprocess.causal_preprocessing import make_test_filter_bundle

        bundle = make_test_filter_bundle(
            self.np.asarray([[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]], dtype="float64")
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "static-gate"
            run_static_causal_preprocessing_gate(
                out_dir=output,
                enforce_authorized_output_root=False,
                require_registered_environment=False,
                design_factory=lambda: bundle,
                audit_runner=lambda _: {"passed": True, "warnings": []},
            )
            path = output / "static_gate.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["decision"] = "tampered"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "report hash mismatch"):
                inspect_causal_preprocessing_report(path)

    def test_cli_exposes_only_registered_loop25_inputs(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        fixture = parser.parse_args(
            [
                "make-causal-preprocessing-fixture",
                "--static-filter-bundle",
                "filter_bundle.json",
                "--out-dir",
                ".codex_work/loop25/fixture",
            ]
        )
        inspect_fixture = parser.parse_args(
            ["inspect-causal-preprocessing-fixture", "--manifest", "manifest.json"]
        )
        static_gate = parser.parse_args(
            [
                "causal-preprocessing-gate",
                "--static-only",
                "--out-dir",
                ".codex_work/loop25/static",
            ]
        )
        full_gate = parser.parse_args(
            [
                "causal-preprocessing-gate",
                "--fixture-manifest",
                "manifest.json",
                "--filter-bundle",
                "filter_bundle.json",
                "--out-dir",
                ".codex_work/loop25/gate",
            ]
        )
        inspect_report = parser.parse_args(
            ["inspect-causal-preprocessing-report", "--report", "gate.json"]
        )
        self.assertEqual(fixture.func.__name__, "_cmd_make_causal_preprocessing_fixture")
        self.assertEqual(
            inspect_fixture.func.__name__, "_cmd_inspect_causal_preprocessing_fixture"
        )
        self.assertTrue(static_gate.static_only)
        self.assertEqual(full_gate.func.__name__, "_cmd_causal_preprocessing_gate")
        self.assertEqual(
            inspect_report.func.__name__, "_cmd_inspect_causal_preprocessing_report"
        )
        for forbidden_name in (
            "real_data",
            "target",
            "checkpoint",
            "model",
            "training",
            "rw3",
            "device",
        ):
            self.assertNotIn(forbidden_name, vars(full_gate))


if __name__ == "__main__":
    unittest.main()
