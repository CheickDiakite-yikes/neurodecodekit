import importlib.util
import gc
import json
import tempfile
import unittest
import warnings
from pathlib import Path

from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
from neurodecodekit.demo.evidence import load_demo_evidence
from neurodecodekit.evaluation.report import build_text_report
from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class DemoEvidenceTests(unittest.TestCase):
    def test_loader_reproduces_examples_and_keeps_real_rows_aggregate_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_demo_fixture(root)
            evidence = load_demo_evidence(root, artifact_paths=paths)

            self.assertEqual(len(evidence.examples), 19)
            self.assertEqual(evidence.example(0).target, evidence.example(0).prediction)
            self.assertEqual(evidence.signal_rows(0)["signals"].shape[0], 5)
            self.assertEqual(len(evidence.aggregate_rows()), 6)
            self.assertEqual(
                evidence.proof_summary()["real_results_displayed"],
                "aggregate metrics only",
            )
            self.assertFalse(evidence.proof_summary()["decoder_causal"])
            self.assertFalse(evidence.proof_summary()["real_session_adapter_authorized"])
            self.assertTrue(all(len(row) == 3 for row in evidence.provenance_rows()))

            edited = evidence.score(0, "BAD")
            self.assertFalse(edited.exact_match)
            with self.assertRaisesRegex(ValueError, "unknown demo channels"):
                evidence.signal_rows(0, ["missing-channel"])

    def test_loader_rejects_prediction_report_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_demo_fixture(root)
            predictions_path = paths["synthetic_ctc_predictions"]
            predictions = predictions_path.read_text().splitlines()
            predictions[0] = "WRONG"
            predictions_path.write_text("\n".join(predictions) + "\n")

            with self.assertRaisesRegex(ValueError, "disagree"):
                load_demo_evidence(root, artifact_paths=paths)


@unittest.skipUnless(importlib.util.find_spec("gradio"), "Gradio not installed")
@unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class DemoAppTests(unittest.TestCase):
    def test_blocks_and_startup_audit_expose_required_proof_boundaries(self):
        from neurodecodekit.demo.app import audit_demo, build_demo

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_demo_fixture(root)
            evidence = load_demo_evidence(root, artifact_paths=paths)
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="unclosed event loop",
                    category=ResourceWarning,
                )
                demo = build_demo(root, evidence=evidence)
                config_text = json.dumps(demo.get_config_file(), default=str)
                demo.close()
                audit = audit_demo(root, evidence=evidence)
                del demo
                gc.collect()

            self.assertIn("Held-out synthetic example", config_text)
            self.assertIn("Aggregate evidence", config_text)
            self.assertIn("Predictive confidence", config_text)
            self.assertTrue(audit["gate_passed"])
            self.assertTrue(all(audit["checks"].values()))
            self.assertEqual(audit["display_examples"], 19)
            self.assertGreater(audit["component_count"], 20)


def _write_demo_fixture(root: Path) -> dict[str, Path]:
    arrays, metadata = make_synthetic_sentence_arrays(
        sentences=24,
        channels=5,
        letter_classes=4,
        seed=71,
    )
    paths = {
        "synthetic_sentence_cache": root / "synthetic.npz",
        "synthetic_ctc_report": root / "synthetic_report.json",
        "synthetic_ctc_predictions": root / "predictions.txt",
        "strict_real_report": root / "strict.json",
        "cross_session_report": root / "cross.json",
        "calibration_report": root / "calibration.json",
    }
    save_sentence_npz_cache(paths["synthetic_sentence_cache"], **arrays, metadata=metadata)

    eval_indices = list(range(19))
    targets = [str(arrays["target_texts"][index]) for index in eval_indices]
    predictions = list(targets)
    synthetic = build_text_report(targets=targets, predictions=predictions, max_examples=19)
    prior = build_text_report(
        targets=targets,
        predictions=[targets[0]] * len(targets),
        max_examples=1,
    )
    synthetic["baseline"] = {"eval_indices": eval_indices, "causal": False}
    synthetic["comparators"] = {"prior_only": {"summary": prior["summary"]}}
    _write_json(paths["synthetic_ctc_report"], synthetic)
    paths["synthetic_ctc_predictions"].write_text(
        "\n".join(predictions) + "\n",
        encoding="utf-8",
    )

    strict = _comparison_report(
        targets=["ABC", "BCD"],
        predictions=["A", "B"],
        prior_predictions=["AAA", "AAA"],
        delta=-0.02,
        interval=[-0.2, 0.15],
    )
    cross = _comparison_report(
        targets=["ABC", "BCD", "CDA"],
        predictions=["A", "B", "C"],
        prior_predictions=["ABC", "BCD", "AAA"],
        delta=0.14,
        interval=[0.11, 0.17],
    )
    _write_json(paths["strict_real_report"], strict)
    _write_json(paths["cross_session_report"], cross)

    validation_rows = []
    holdout_rows = []
    for family, identity, adapted in (
        ("stationary_diagonal", 0.4, 0.2),
        ("stationary_channel_mixing", 0.5, 0.8),
        ("within_row_time_varying", 0.45, 0.65),
    ):
        for size in (1, 2):
            validation_rows.append(
                {
                    "shift_family": family,
                    "calibration_rows": size,
                    "median_identity_cer": identity,
                    "median_adapted_cer": adapted,
                }
            )
        holdout_rows.append(
            {
                "shift_family": family,
                "seed_count": 3,
                "median_identity_cer": identity,
                "median_adapted_cer": adapted,
                "median_cer_gain": identity - adapted,
            }
        )
    calibration = {
        "decision": {
            "selected_calibration_rows": 1,
            "real_session_adapter_authorized": False,
        },
        "validation_aggregate": validation_rows,
        "holdout": {"aggregate": holdout_rows},
    }
    _write_json(paths["calibration_report"], calibration)
    return paths


def _comparison_report(
    *,
    targets: list[str],
    predictions: list[str],
    prior_predictions: list[str],
    delta: float,
    interval: list[float],
) -> dict:
    report = build_text_report(targets=targets, predictions=predictions, max_examples=1)
    prior = build_text_report(targets=targets, predictions=prior_predictions, max_examples=1)
    report["comparators"] = {"prior_only": {"summary": prior["summary"]}}
    report["comparisons"] = {
        "tiny_ctc_vs_prior_only": {
            "n_paired_sentences": len(targets),
            "corpus_cer_delta_a_minus_b": delta,
            "paired_bootstrap_delta_ci95": interval,
        }
    }
    return report


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
