import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


class CausalPreprocessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
            import scipy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("NumPy and SciPy are optional") from None
        cls.np = np

    def setUp(self):
        from neurodecodekit.preprocess.causal_preprocessing import make_test_filter_bundle

        self.bundle = make_test_filter_bundle(
            self.np.asarray([[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]], dtype="float64")
        )
        self.signal = self.np.random.default_rng(2500).normal(size=(5, 1024)).astype(
            "float32"
        )

    def test_all_registered_schedules_and_resume_cuts_are_bitwise_exact(self):
        from neurodecodekit.experiments.causal_preprocessing_gate import (
            _run_resume,
            _run_schedule,
        )
        from neurodecodekit.preprocess.causal_preprocessing import load_registered_contract

        contract = load_registered_contract()
        reference = _run_schedule(
            self.signal,
            bundle=self.bundle,
            source_start_sample=1000,
            schedule_rule="all_remaining_samples",
            schedule_seed=2511,
        )
        for schedule in contract["registered_chunk_schedules"]:
            replay = _run_schedule(
                self.signal,
                bundle=self.bundle,
                source_start_sample=1000,
                schedule_rule=schedule["rule"],
                schedule_seed=2511,
            )
            self.np.testing.assert_array_equal(reference["values"], replay["values"])
            self.np.testing.assert_array_equal(
                reference["source_indices"], replay["source_indices"]
            )
            self.assertEqual(reference["final_state_sha256"], replay["final_state_sha256"])
        for cut in contract["registered_resume_cut_source_samples"]:
            replay = _run_resume(
                self.signal,
                cut=cut,
                bundle=self.bundle,
                source_start_sample=1000,
            )
            self.np.testing.assert_array_equal(reference["values"], replay["values"])
            self.np.testing.assert_array_equal(
                reference["timestamps_sec"], replay["timestamps_sec"]
            )
            self.assertEqual(reference["final_state_sha256"], replay["final_state_sha256"])

    def test_timestamps_phase_lock_bounds_and_flush(self):
        from neurodecodekit.preprocess.causal_preprocessing import CausalPreprocessor

        processor = CausalPreprocessor(
            self.bundle,
            source_start_sample=1230,
            require_registered=False,
        )
        output = processor.push(self.signal, chunk_start_sample=1230)
        expected_indices = self.np.arange(0, 1024, 10, dtype="int64")
        self.np.testing.assert_array_equal(output.source_indices, expected_indices)
        self.np.testing.assert_array_equal(
            output.timestamps_sec,
            (1230 + expected_indices).astype("float64") / 1000.0,
        )
        self.assertEqual(output.values.dtype, self.np.dtype("float32"))
        self.assertGreaterEqual(float(output.values.min()), -5.0)
        self.assertLessEqual(float(output.values.max()), 5.0)
        flush = processor.flush()
        self.assertEqual(flush["invented_source_samples"], 0)
        self.assertEqual(flush["invented_output_samples"], 0)

    def test_state_tampering_configuration_change_and_source_gap_are_refused(self):
        from neurodecodekit.preprocess.causal_preprocessing import (
            CausalPreprocessingRefusal,
            CausalPreprocessor,
        )

        processor = CausalPreprocessor(
            self.bundle,
            source_start_sample=0,
            require_registered=False,
        )
        processor.push(self.signal[:, :100], chunk_start_sample=0)
        state = processor.snapshot()
        tampered = copy.deepcopy(state)
        tampered["source_samples_seen"] += 1
        with self.assertRaisesRegex(CausalPreprocessingRefusal, "semantic hash"):
            CausalPreprocessor(
                self.bundle,
                source_start_sample=0,
                require_registered=False,
                state=tampered,
            )
        changed_bundle = replace(self.bundle, pipeline_config_sha256="different-test-pipeline")
        with self.assertRaisesRegex(CausalPreprocessingRefusal, "pipeline_config_sha256"):
            CausalPreprocessor(
                changed_bundle,
                source_start_sample=0,
                require_registered=False,
                state=state,
            )
        with self.assertRaisesRegex(CausalPreprocessingRefusal, "expected chunk start"):
            processor.push(self.signal[:, 100:110], chunk_start_sample=101)

    def test_malformed_chunks_and_post_flush_calls_are_refused(self):
        from neurodecodekit.preprocess.causal_preprocessing import (
            CausalPreprocessingRefusal,
            CausalPreprocessor,
        )

        def fresh():
            return CausalPreprocessor(
                self.bundle,
                source_start_sample=0,
                require_registered=False,
            )

        with self.assertRaises(CausalPreprocessingRefusal):
            fresh().push(self.signal.astype("float64"), chunk_start_sample=0)
        with self.assertRaises(CausalPreprocessingRefusal):
            fresh().push(self.signal[:, :0], chunk_start_sample=0)
        nonfinite = self.signal.copy()
        nonfinite[0, 0] = self.np.nan
        with self.assertRaises(CausalPreprocessingRefusal):
            fresh().push(nonfinite, chunk_start_sample=0)
        processor = fresh()
        processor.push(self.signal[:, :10], chunk_start_sample=0)
        processor.flush()
        with self.assertRaises(CausalPreprocessingRefusal):
            processor.push(self.signal[:, 10:20], chunk_start_sample=10)
        with self.assertRaises(CausalPreprocessingRefusal):
            processor.flush()

    def test_filter_bundle_roundtrip_and_hash_tamper(self):
        from neurodecodekit.preprocess.causal_preprocessing import (
            CausalPreprocessingRefusal,
            load_filter_bundle,
            save_filter_bundle,
        )

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.json"
            save_filter_bundle(path, self.bundle, {"passed": True, "warnings": []})
            loaded, audit = load_filter_bundle(path, require_registered=False)
            self.assertEqual(loaded.filter_sos_sha256, self.bundle.filter_sos_sha256)
            self.assertTrue(audit["passed"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["bundle"]["combined_sos_float64"][0][0] = 0.5
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(CausalPreprocessingRefusal):
                load_filter_bundle(path, require_registered=False)


if __name__ == "__main__":
    unittest.main()
