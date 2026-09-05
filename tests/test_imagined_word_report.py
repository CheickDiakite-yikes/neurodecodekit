"""Hand-calculated, generated-only scorer checks; no signals, models, or source I/O."""

import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from neurodecodekit.evaluation import imagined_word_report as report


def records():
    """Unequal class/person counts distinguish trial, class, and person means."""
    predictions, targets = [], []
    # Person A: 3/4 correct, but class-macro accuracy 1/2. Person B: all correct.
    for person, labels in (("A", ["left", "left", "left", "right"]),
                           ("B", ["left", "right"])):
        for trial, target in enumerate(labels):
            identity = {"participant": person, "session": "5", "trial_id": str(trial)}
            eeg = [0.8, 0.2] if person == "A" or target == "left" else [0.2, 0.8]
            predictions.append({**identity, "probabilities": {
                "eeg": eeg, **{arm: [0.5, 0.5] for arm in report.DEFAULT_CONTROL_ARMS},
                "cue": [0.5, 0.5],
            }})
            targets.append({**identity, "target": target})
    return predictions, targets


def score(predictions=None, targets=None, **kwargs):
    fixture_predictions, fixture_targets = records()
    return report.score_predictions(
        fixture_predictions if predictions is None else predictions,
        fixture_targets if targets is None else targets,
        class_labels=["left", "right"], expected_participants=["A", "B"],
        diagnostic_arms=["cue"], bootstrap_samples=100, **kwargs,
    )


class ImaginedWordArithmeticTests(unittest.TestCase):
    def test_five_class_probabilities_use_explicit_vocabulary_order(self):
        labels = ["down", "left", "right", "select", "up"]
        predictions, targets = [], []
        for person in ("A", "B"):
            for index, label in enumerate(labels):
                identity = {"participant": person, "session": "5", "trial_id": str(index)}
                predictions.append({**identity, "probabilities": {
                    "eeg": [float(column == index) for column in range(5)],
                    **{arm: [.2] * 5 for arm in report.DEFAULT_CONTROL_ARMS},
                }})
                targets.append({**identity, "target": label})
        result = report.score_predictions(
            predictions, targets, class_labels=labels, bootstrap_samples=100,
        )
        self.assertEqual(result["summary_by_arm"]["eeg"]["macro_log_loss"]["participant_mean"], 0)
        self.assertAlmostEqual(result["comparisons"]["prior"]["macro_log_loss"]["mean_gain"],
                               math.log(5))
        self.assertEqual([row["arms"]["eeg"]["word"] for row in result["prediction_rows"]],
                         labels * 2)

    def test_class_macro_and_equal_person_metrics_against_hand_calculation(self):
        result = score()
        people = {person["participant"]: person for person in result["participants"]}
        a, b = people["A"]["arms"]["eeg"], people["B"]["arms"]["eeg"]
        self.assertAlmostEqual(a["macro_log_loss"], (-math.log(.8) - math.log(.2)) / 2)
        self.assertAlmostEqual(a["balanced_accuracy"], .5)
        self.assertAlmostEqual(a["exact_accuracy"], .75)
        self.assertAlmostEqual(b["macro_log_loss"], -math.log(.8))
        summary = result["summary_by_arm"]["eeg"]
        self.assertAlmostEqual(summary["balanced_accuracy"]["participant_mean"], .75)
        self.assertAlmostEqual(summary["exact_accuracy"]["participant_mean"], .875)
        self.assertNotAlmostEqual(summary["exact_accuracy"]["participant_mean"], 5 / 6)
        self.assertEqual(people["A"]["class_counts"], {"left": 3, "right": 1})

    def test_paired_bootstrap_and_all_null_edges_have_correct_sign(self):
        result = score()
        comparison = result["comparisons"]["prior"]
        a = math.log(2) + (math.log(.8) + math.log(.2)) / 2
        b = math.log(2) + math.log(.8)
        loss = comparison["macro_log_loss"]
        self.assertAlmostEqual(loss["mean_gain"], (a + b) / 2)
        self.assertEqual(loss["positive_people"], 1)
        self.assertEqual(loss["tied_people"], 0)
        # With two people the paired bootstrap has only means a, b, and (a+b)/2.
        self.assertAlmostEqual(loss["descriptive_ci95"][0], a)
        self.assertAlmostEqual(loss["descriptive_ci95"][1], b)
        self.assertAlmostEqual(comparison["balanced_accuracy"]["mean_gain"], .25)
        self.assertAlmostEqual(comparison["exact_accuracy"]["mean_gain"], .25)
        self.assertEqual(set(result["comparisons"]), set(report.DEFAULT_CONTROL_ARMS))
        self.assertEqual(set(result["diagnostic_comparisons"]), {"cue"})
        self.assertEqual(result, score())

    def test_join_uses_full_identity_not_target_row_position(self):
        predictions, targets = records()
        self.assertEqual(score(predictions, targets), score(predictions, list(reversed(targets))))
        # Trial 0 occurs for both people; it is not a globally unique identity.
        self.assertEqual(score()["n_trials"], 6)

    def test_zero_probability_floor_and_argmax_tie_order(self):
        predictions, targets = records()
        for row in predictions:
            row["probabilities"]["eeg"] = [1., 0.]
        result = score(predictions, targets)
        expected = -math.log(report.PROBABILITY_FLOOR) / 2
        for person in result["participants"]:
            self.assertAlmostEqual(person["arms"]["eeg"]["macro_log_loss"], expected)
        for row in result["prediction_rows"]:
            self.assertEqual(row["arms"]["prior"]["word"], "left")
            self.assertEqual(row["arms"]["prior"]["confidence"], .5)

    def test_one_person_does_not_get_a_spurious_interval(self):
        predictions, targets = records()
        result = report.score_predictions(
            [row for row in predictions if row["participant"] == "B"],
            [row for row in targets if row["participant"] == "B"],
            class_labels=["left", "right"], expected_participants=["B"],
            diagnostic_arms=["cue"], bootstrap_samples=100,
        )
        self.assertIsNone(result["comparisons"]["prior"]["macro_log_loss"]["descriptive_ci95"])


class ImaginedWordValidationTests(unittest.TestCase):
    def test_no_silent_record_or_participant_selection(self):
        predictions, targets = records()
        mutations = (
            (predictions + [predictions[0]], targets, "Duplicate prediction"),
            (predictions, targets + [targets[0]], "Duplicate target"),
            (predictions, targets[:-1], "identical record identities"),
            (predictions[:4], targets[:4], "expected participant set"),
        )
        for p, y, message in mutations:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                score(p, y)

    def test_missing_class_refuses_instead_of_averaging_present_classes(self):
        predictions, targets = records()
        targets[3]["target"] = "left"
        with self.assertRaisesRegex(ValueError, "Every class is required for participant A"):
            score(predictions, targets)

    def test_target_fields_cannot_enter_prediction_schema(self):
        predictions, targets = records()
        predictions[0]["target"] = "left"
        with self.assertRaisesRegex(ValueError, "exactly"):
            score(predictions, targets)

    def test_declared_null_controls_cannot_be_silently_omitted(self):
        predictions, targets = records()
        for row in predictions:
            del row["probabilities"]["noise"]
        with self.assertRaisesRegex(ValueError, "All four null controls are required"):
            score(predictions, targets, control_arms=["prior", "metadata", "shuffled"])

    def test_unknown_class_wrong_session_missing_arm_and_invalid_probability_refuse(self):
        predictions, targets = records()
        invalid = (
            [float("nan"), .5], [float("inf"), .5], [-.1, 1.1], [.4, .4],
            [True, False], ["0.5", "0.5"], [.5], None,
        )
        for probability in invalid:
            p = copy.deepcopy(predictions)
            p[0]["probabilities"]["eeg"] = probability
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                score(p, targets)
        y = copy.deepcopy(targets)
        y[0]["target"] = "not a word in this vocabulary"
        with self.assertRaisesRegex(ValueError, "outside the declared vocabulary"):
            score(predictions, y)
        p = copy.deepcopy(predictions)
        p[0]["session"] = "0"
        with self.assertRaisesRegex(ValueError, "outside the declared held-out session"):
            score(p, targets)
        p = copy.deepcopy(predictions)
        del p[0]["probabilities"]["noise"]
        with self.assertRaisesRegex(ValueError, "exactly the declared arms"):
            score(p, targets)


class ImaginedWordFileAndReportTests(unittest.TestCase):
    @staticmethod
    def envelope(predictions):
        return {
            "class_labels": ["left", "right"], "primary_arm": "eeg",
            "control_arms": list(report.DEFAULT_CONTROL_ARMS), "diagnostic_arms": ["cue"],
            "expected_participants": ["A", "B"], "heldout_session": "5",
            "records": predictions,
        }

    def test_digest_or_schema_failure_never_opens_target_file(self):
        predictions, _ = records()
        data = json.dumps(self.envelope(predictions)).encode()
        with patch.object(Path, "read_bytes", return_value=data) as read:
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                report.score_frozen_files("predictions.json", "targets.json",
                                          expected_prediction_sha256="0" * 64)
            self.assertEqual(read.call_count, 1)
        invalid = self.envelope(predictions)
        invalid["records"][0]["reference"] = "leaked"
        data = json.dumps(invalid).encode()
        with patch.object(Path, "read_bytes", return_value=data) as read:
            with self.assertRaisesRegex(ValueError, "exactly"):
                report.score_frozen_files(
                    "predictions.json", "targets.json",
                    expected_prediction_sha256=hashlib.sha256(data).hexdigest(),
                )
            self.assertEqual(read.call_count, 1)

    def test_duplicate_json_fields_refuse_before_targets(self):
        data = b'{"records": [], "records": []}'
        with patch.object(Path, "read_bytes", return_value=data) as read:
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                report.score_frozen_files(
                    "predictions.json", "targets.json",
                    expected_prediction_sha256=hashlib.sha256(data).hexdigest(),
                )
            self.assertEqual(read.call_count, 1)

    def test_generated_files_score_and_render_every_prediction_and_control(self):
        predictions, targets = records()
        with tempfile.TemporaryDirectory(prefix="imagined-word-generated-") as directory:
            root = Path(directory)
            p = root / "predictions.json"
            y = root / "targets.json"
            data = json.dumps(self.envelope(predictions)).encode()
            p.write_bytes(data)
            y.write_text(json.dumps({"records": targets}), encoding="utf-8")
            result = report.score_frozen_files(
                p, y, expected_prediction_sha256=hashlib.sha256(data).hexdigest(),
                bootstrap_samples=100,
            )
            self.assertEqual(result["provenance"]["prediction_sha256"], hashlib.sha256(data).hexdigest())
            path = report.write_html_report(result, root / "report.html")
            document = path.read_text(encoding="utf-8")
            self.assertEqual(document.count("data-person="), 6)
            self.assertIn("Every participant and arm", document)
            self.assertIn("Window diagnostic", document)
            self.assertIn("not a no-signal control", document)
            self.assertIn("eye movements", document)
            self.assertIn("not corrected", document)
            self.assertNotIn("https://", document)
            self.assertNotIn("http://", document)
            self.assertNotIn("<script src=", document)
            self.assertEqual(set(result["prediction_rows"][0]["arms"]),
                             {"eeg", "prior", "metadata", "shuffled", "noise", "cue"})

    def test_html_escapes_untrusted_word_and_identity_text(self):
        predictions, targets = records()
        malicious = "</script><img src=x onerror=alert(1)>"
        for row in targets:
            if row["target"] == "left":
                row["target"] = malicious
        for row in predictions + targets:
            row["trial_id"] += "' onclick='alert(2)"
        result = report.score_predictions(
            predictions, targets, class_labels=[malicious, "right"],
            diagnostic_arms=["cue"], bootstrap_samples=100,
        )
        document = report.render_html_report(result)
        self.assertNotIn(malicious, document)
        self.assertIn("&lt;/script&gt;&lt;img", document)
        self.assertIn("&#x27; onclick=&#x27;", document)


if __name__ == "__main__":
    unittest.main()
