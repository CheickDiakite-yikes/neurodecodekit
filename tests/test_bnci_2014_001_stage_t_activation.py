from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.evaluation import bnci_2014_001_stage_t_live as stage_t  # noqa: E402


ACTIVATION_PATH = ROOT / stage_t.ACTIVATION_RELATIVE_PATH
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_T_SCORING_ACTIVATION.md"


class BNCIStageTActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.activation = json.loads(ACTIVATION_PATH.read_text(encoding="utf-8"))

    def test_schema_and_green_barriers_are_exact(self) -> None:
        value = stage_t.validate_activation_document(self.activation)
        self.assertEqual(
            value["green_implementation"]["commit"],
            "7ba4f7c30f260bc7603e8928ad8d9ff010e54872",
        )
        self.assertEqual(
            value["green_prediction_freeze"]["commit"],
            "2517fd16e7bf4cca077c46686320fe26c992ed69",
        )
        self.assertEqual(value["green_prediction_freeze"]["CI_run_id"], 32_908_059_166)
        self.assertTrue(value["green_prediction_freeze"]["both_required_jobs_green"])

    def test_prediction_freeze_artifact_is_bound(self) -> None:
        row = self.activation["prediction_freeze_artifact"]
        payload = (ROOT / row["path"]).read_bytes()
        self.assertEqual(len(payload), row["bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_every_implementation_artifact_identity_is_bound(self) -> None:
        for row in self.activation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])

    def test_authority_is_one_score_without_update_or_rerun(self) -> None:
        authority = self.activation["authority"]
        self.assertTrue(authority["one_target_delivery_of_nine_sealed_fold_sets"])
        self.assertTrue(authority["one_aggregate_score"])
        self.assertEqual(authority["post_target_updates"], 0)
        self.assertEqual(authority["reruns"], 0)
        self.assertFalse(authority["held_out_T_delivery"])
        self.assertFalse(
            authority["individual_prediction_probability_target_or_participant_outcome_public"]
        )

    def test_document_states_delayed_effect_and_interpretation_ceiling(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("delayed effect", text)
        self.assertIn("both required CI jobs", text)
        self.assertIn("2,592 target identities", text)
        self.assertIn("cannot establish thought or language decoding", text)


if __name__ == "__main__":
    unittest.main()
