import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import bnci_2014_001_acquisition as acquisition
from neurodecodekit.evaluation import bnci_2014_001_score as scorer


ROOT = Path(__file__).resolve().parents[1]


def _score_fixture():
    identities = []
    targets = []
    for participant in scorer.PARTICIPANTS:
        for trial, target in enumerate(scorer.CLASSES):
            identity = {
                "participant": participant,
                "session": "E",
                "run_ordinal": 0,
                "trial_ordinal": trial,
                "opaque_row_id": hashlib.sha256(
                    f"{participant}/E/0/{trial}".encode()
                ).hexdigest(),
            }
            identities.append(identity)
            targets.append(target)
    prediction_rows = scorer.generated_passing_rows(identities, targets)
    target_rows = [
        {**identity, "target": target}
        for identity, target in zip(identities, targets, strict=True)
    ]
    target_rows.sort(key=scorer._target_sort_key)
    prediction_payload = scorer.canonical_prediction_jsonl(prediction_rows)
    target_payload = scorer.canonical_target_jsonl(target_rows)
    bindings = scorer.FreezeBindings(
        configuration_hash="a" * 64,
        code_hash="b" * 64,
        source_cache_hashes={"generated": "c" * 64},
        split_protocol_hash="d" * 64,
        sealed_target_payload_sha256=hashlib.sha256(target_payload).hexdigest(),
    )
    freeze = scorer.build_prediction_freeze(prediction_payload, bindings=bindings)
    return prediction_payload, target_payload, bindings, freeze


class BNCIAcquisitionTests(unittest.TestCase):
    def test_registered_plan_is_exact_and_does_not_allow_parse(self):
        plan = acquisition.registered_plan()
        self.assertEqual(plan["file_count"], 18)
        self.assertEqual(plan["accepted_payload_bytes_exact"], 779_873_919)
        self.assertEqual(
            {row["relative_path"] for row in plan["members"]},
            {
                f"sourcedata/A{participant:02d}{session}.mat"
                for participant in range(1, 10)
                for session in ("E", "T")
            },
        )
        self.assertFalse(plan["MAT_content_parse_allowed"])

    def test_generated_transport_resume_integrity_alias_caps_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            result = acquisition.run_generated_acquisition_cases(Path(directory) / "cases")
        self.assertEqual(result["accepted_files"], 3)
        self.assertEqual(result["accepted_payload_requests"], 4)
        self.assertEqual(result["refusal_cases"], 7)
        self.assertEqual(result["temporary_generated_payload_bytes"], 64)
        self.assertEqual(result["cleanup_owner"], "caller_owned_generated_work_root")

    def test_base_imports_do_not_load_optional_numerical_packages(self):
        command = (
            "import sys; "
            "import neurodecodekit.datasets.bnci_2014_001_acquisition; "
            "import neurodecodekit.evaluation.bnci_2014_001_score; "
            "import neurodecodekit.experiments.bnci_2014_001_cross_participant_eeg_gain; "
            "print(','.join(sorted(n for n in ('numpy','scipy','sklearn') if n in sys.modules)))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "")

    def test_cli_exposes_plan_and_generated_qualification_but_no_execute(self):
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.bnci_c3c5_cli", "--help"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("plan", completed.stdout)
        self.assertIn("qualify", completed.stdout)
        self.assertNotIn("execute", completed.stdout)


class BNCIScorerTests(unittest.TestCase):
    def test_freeze_replays_and_rejects_prediction_or_binding_mutation(self):
        prediction_payload, _target_payload, bindings, freeze = _score_fixture()
        self.assertEqual(
            scorer.validate_prediction_freeze(
                freeze, prediction_payload, bindings=bindings
            ),
            json.loads(json.dumps(scorer._parse_jsonl(prediction_payload, kind="test"))),
        )
        with self.assertRaises(scorer.BNCIScoreRefusal):
            scorer.validate_prediction_freeze(
                freeze, prediction_payload + b"{}\n", bindings=bindings
            )
        changed = scorer.FreezeBindings(
            configuration_hash="0" * 64,
            code_hash=bindings.code_hash,
            source_cache_hashes=bindings.source_cache_hashes,
            split_protocol_hash=bindings.split_protocol_hash,
            sealed_target_payload_sha256=bindings.sealed_target_payload_sha256,
        )
        with self.assertRaises(scorer.BNCIScoreRefusal):
            scorer.validate_prediction_freeze(
                freeze, prediction_payload, bindings=changed
            )

    def test_checkpoint_refusal_delivers_zero_targets(self):
        prediction_payload, _target_payload, bindings, freeze = _score_fixture()
        loads = 0

        def forbidden_loader():
            nonlocal loads
            loads += 1
            raise AssertionError("target loader must stay closed")

        with self.assertRaises(scorer.BNCIScoreRefusal):
            scorer.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: False,
                sealed_target_loader=forbidden_loader,
            )
        self.assertEqual(loads, 0)

    def test_one_delivery_scores_generated_router_and_rejects_target_swap(self):
        prediction_payload, target_payload, bindings, freeze = _score_fixture()
        loads = 0

        def loader():
            nonlocal loads
            loads += 1
            return target_payload

        result = scorer.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: True,
            sealed_target_loader=loader,
        )
        self.assertEqual(loads, 1)
        self.assertEqual(result["route"], "BNCIC3C5-R5")
        self.assertTrue(result["C3_passed"])
        self.assertTrue(result["C5_partial_passed"])
        swapped = target_payload.replace(b'"left_hand"', b'"right_hand"', 1)
        with self.assertRaises(scorer.BNCIScoreRefusal):
            scorer.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: True,
                sealed_target_loader=lambda: swapped,
            )

    def test_metrics_sign_flip_and_router_boundaries(self):
        self.assertEqual(scorer.exact_sign_flip_p([0.0] * 9), 1.0)
        self.assertEqual(scorer.exact_sign_flip_p([0.1] * 9), 1 / 512)
        self.assertEqual(
            {
                scorer.route_result(integrity=False, C3=False, C5_partial=False),
                scorer.route_result(integrity=True, C3=False, C5_partial=False),
                scorer.route_result(integrity=True, C3=True, C5_partial=False),
                scorer.route_result(integrity=True, C3=False, C5_partial=True),
                scorer.route_result(integrity=True, C3=True, C5_partial=True),
            },
            {
                "BNCIC3C5-R0",
                "BNCIC3C5-R2",
                "BNCIC3C5-R3",
                "BNCIC3C5-R4",
                "BNCIC3C5-R5",
            },
        )


if __name__ == "__main__":
    unittest.main()
