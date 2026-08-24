import os
import tempfile
import unittest
from pathlib import Path


def _exact_optional_stack_available():
    try:
        import importlib.metadata

        return {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "scikit-learn")
        } == {"numpy": "2.5.2", "scipy": "1.18.0", "scikit-learn": "1.9.0"}
    except importlib.metadata.PackageNotFoundError:
        return False


NUMERICAL = (
    os.environ.get("NEURODECODEKIT_BNCI_NUMERICAL_TESTS") == "1"
    or _exact_optional_stack_available()
)


@unittest.skipUnless(NUMERICAL, "set NEURODECODEKIT_BNCI_NUMERICAL_TESTS=1")
class BNCINumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neurodecodekit.experiments import (
            bnci_2014_001_cross_participant_eeg_gain as experiment,
        )

        cls.experiment = experiment
        experiment.assert_exact_versions()
        experiment.assert_single_thread_environment()

    def test_generated_mat_causality_dimensions_and_malformed_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.experiment.run_generated_mat_cases(Path(directory) / "mat")
        self.assertEqual(result["runs"], 6)
        self.assertEqual(result["trials"], 288)
        self.assertEqual(result["feature_dimensions"], {"E1": 88, "E2": 1012, "P": 102})
        self.assertEqual(result["malformed_refusals"], 1)
        self.assertFalse(result["geometry_available"])

    def test_log_euclidean_reference_is_fitted_from_source_only(self):
        import numpy as np

        values = np.arange(8 * 1012, dtype="float64").reshape(8, 1012) / 1000.0
        labels = list(self.experiment.CLASSES) * 2
        model = self.experiment.fit_logistic(
            values,
            labels,
            C=0.1,
            log_euclidean_reference=True,
        )
        np.testing.assert_allclose(model.source_reference, values.mean(axis=0))
        np.testing.assert_allclose(model.mean, np.zeros(1012), atol=1e-12)
        shifted = values + 100.0
        self.assertFalse(np.array_equal(model.source_reference, shifted.mean(axis=0)))

    def test_fold_target_capability_and_exact_schedule_without_isolation(self):
        rows, targets, _bytes = self.experiment.build_generated_feature_cohort()
        participant = "A01"
        source = [row for row in rows if row["participant"] != participant]
        held_all = [row for row in rows if row["participant"] == participant]
        held_e = [row for row in held_all if row["session"] == "E"]
        capability, manifest = self.experiment._source_target_capability(
            source, held_all, targets
        )
        self.assertEqual(len(capability), 384)
        self.assertEqual(manifest["held_out_target_rows"], 0)
        self.assertTrue(
            set(capability).isdisjoint(
                {str(row["opaque_row_id"]) for row in held_all}
            )
        )
        result = self.experiment._run_single_fold(
            participant, source, held_e, capability
        )
        self.assertEqual(result["fit_count"], 52)
        self.assertEqual(result["prediction_sets"], 55)
        self.assertEqual(result["model_inference_runs"], 55)
        self.assertEqual(len(result["predictions"]), 24 * 16)

    def test_one_fold_runs_in_spawned_target_firewalled_process(self):
        rows, targets, _bytes = self.experiment.build_generated_feature_cohort()
        participant = "A01"
        source = [row for row in rows if row["participant"] != participant]
        held_all = [row for row in rows if row["participant"] == participant]
        held_e = [row for row in held_all if row["session"] == "E"]
        capability, _manifest = self.experiment._source_target_capability(
            source, held_all, targets
        )
        result = self.experiment._run_fold_isolated(
            participant, source, held_e, capability
        )
        self.assertEqual(result["fit_count"], 52)
        self.assertEqual(len(result["predictions"]), 24 * 16)


if __name__ == "__main__":
    unittest.main()
