import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.evaluation.local_eeg_tooling import (
    CapabilitySpec,
    DEFAULT_TOOL_SPECS,
    ToolSpec,
    _inspect_tool,
    audit_local_eeg_tooling,
    validate_local_eeg_tooling_report,
    write_local_eeg_tooling_report,
)


JSON_SPEC = ToolSpec(
    tool_id="json",
    distribution=None,
    module="json",
    role="test-only standard-library probe",
    capabilities=(CapabilitySpec("json", "loads"),),
)
MISSING_SPEC = ToolSpec(
    tool_id="definitely_missing",
    distribution="neurodecodekit-definitely-missing",
    module="neurodecodekit_definitely_missing",
    role="test-only unavailable probe",
    capabilities=(CapabilitySpec("neurodecodekit_definitely_missing", "missing"),),
)


class LocalEegToolingTests(unittest.TestCase):
    def test_fixed_matrix_covers_local_first_eeg_stack(self):
        self.assertEqual(
            [spec.tool_id for spec in DEFAULT_TOOL_SPECS],
            [
                "numpy",
                "scipy",
                "scikit_learn",
                "mne",
                "pyriemann",
                "moabb",
                "braindecode",
            ],
        )

    def test_audit_is_deterministic_in_shape_and_keeps_imports_isolated(self):
        optional_modules = {spec.module for spec in DEFAULT_TOOL_SPECS}
        before = optional_modules.intersection(sys.modules)
        report = audit_local_eeg_tooling(tool_specs=(JSON_SPEC, MISSING_SPEC))
        after = optional_modules.intersection(sys.modules)

        self.assertEqual(before, after)
        self.assertFalse(report["environment"]["base_process_imported_optional_tools"])
        self.assertEqual(report["summary"]["tool_count"], 2)
        self.assertEqual(report["summary"]["available_module_count"], 1)
        self.assertEqual(report["summary"]["missing_tool_ids"], ["definitely_missing"])
        self.assertEqual(report["tools"][0]["probe_status"], "import_ready")
        self.assertEqual(report["tools"][1]["probe_status"], "not_installed")
        self.assertFalse(report["summary"]["brainvision_reader_ready"])
        self.assertFalse(report["summary"]["ocular_ica_substrate_ready"])
        self.assertFalse(report["summary"]["mne_csp_substrate_ready"])
        self.assertTrue(
            all(
                report["access_counters"][field] == 0
                for field in (
                    "successful_network_operations",
                    "downloads",
                    "real_or_protected_data_reads",
                    "target_or_label_reads",
                    "raw_signal_reads",
                    "model_loads",
                    "training_runs",
                    "inference_runs",
                    "scoring_runs",
                    "provider_calls",
                    "device_or_hardware_operations",
                )
            )
        )
        self.assertEqual(
            report["resources"]["output_bytes"],
            len((json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")),
        )

    def test_duplicate_ids_and_tiny_output_cap_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "tool_ids must be unique"):
            audit_local_eeg_tooling(tool_specs=(JSON_SPEC, JSON_SPEC))
        with self.assertRaisesRegex(ValueError, "exceeds output cap"):
            audit_local_eeg_tooling(tool_specs=(JSON_SPEC,), max_output_bytes=1)

    def test_malformed_probe_output_is_sanitized(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="not-json local/path/that/must/not/be/retained",
            stderr="secret stderr",
        )
        with (
            patch(
                "neurodecodekit.evaluation.local_eeg_tooling.importlib.util.find_spec",
                return_value=object(),
            ),
            patch(
                "neurodecodekit.evaluation.local_eeg_tooling.subprocess.run",
                return_value=completed,
            ),
        ):
            result = _inspect_tool(JSON_SPEC, timeout_seconds=1.0)
        self.assertEqual(result["probe_status"], "malformed_probe_output")
        rendered = json.dumps(result, sort_keys=True)
        self.assertNotIn("local/path", rendered)
        self.assertNotIn("secret stderr", rendered)
        self.assertGreater(result["captured_output_bytes"], 0)

    def test_timeout_is_classified_without_retry(self):
        with (
            patch(
                "neurodecodekit.evaluation.local_eeg_tooling.importlib.util.find_spec",
                return_value=object(),
            ),
            patch(
                "neurodecodekit.evaluation.local_eeg_tooling.subprocess.run",
                side_effect=subprocess.TimeoutExpired("probe", 0.25),
            ) as run,
        ):
            result = _inspect_tool(JSON_SPEC, timeout_seconds=0.25)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result["probe_status"], "timeout")
        self.assertEqual(result["runtime_seconds"], 0.25)

    def test_writer_validates_caps_and_never_overwrites(self):
        report = audit_local_eeg_tooling(tool_specs=(JSON_SPEC,))
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "audit.json"
            written = write_local_eeg_tooling_report(output, report)
            self.assertEqual(written, report["resources"]["output_bytes"])
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)
            with self.assertRaises(FileExistsError):
                write_local_eeg_tooling_report(output, report)

    def test_validator_rejects_forbidden_operation_counter(self):
        report = audit_local_eeg_tooling(tool_specs=(JSON_SPEC,))
        malformed = copy.deepcopy(report)
        malformed["access_counters"]["downloads"] = 1
        with self.assertRaisesRegex(ValueError, "downloads"):
            validate_local_eeg_tooling_report(malformed)

    def test_cli_writes_and_prints_the_same_bounded_report(self):
        report = audit_local_eeg_tooling(tool_specs=(JSON_SPEC,))
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "audit.json"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                patch(
                    "neurodecodekit.evaluation.local_eeg_tooling.audit_local_eeg_tooling",
                    return_value=report,
                ),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                code = main(["inspect-local-eeg-tooling", "--out", str(output)])
            self.assertEqual(code, 0, stderr.getvalue())
            self.assertEqual(json.loads(stdout.getvalue()), report)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
