import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    dreyer_c5r_1_stage_h_live_recovery as recovery,
)
from neurodecodekit.datasets import (
    dreyer_c5r_1_stage_h_live_recovery_qualification as qualification,
)

ROOT = Path(__file__).resolve().parents[1]


class DreyerRecoveryQualificationTests(unittest.TestCase):
    def test_decision_identity_and_scope_are_exact(self):
        decision = qualification.load_green_decision()

        self.assertEqual(decision["decision_id"], qualification.DECISION_ID)
        self.assertEqual(
            hashlib.sha256(
                (ROOT / qualification.DECISION_RELATIVE_PATH).read_bytes()
            ).hexdigest(),
            qualification.DECISION_SHA256,
        )
        self.assertTrue(
            decision["authorization_after_decision_green"][
                "run_one_registered_generated_qualification_after_coordinator_remote_green"
            ]
        )
        self.assertFalse(
            decision["authorization_after_decision_green"]["write_or_read_real_EDF"]
        )

    def test_full_development_matrix_is_exact_and_deterministic(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-q-") as temporary:
            matrix = qualification.run_development_matrix(temporary)

        self.assertEqual(matrix["total_cases"], 65)
        self.assertEqual(matrix["valid_H1_replays"], 2)
        self.assertTrue(matrix["valid_H1_byte_deterministic"])
        self.assertEqual(matrix["inherited_stage_H_valid_cases"], 2)
        self.assertEqual(matrix["inherited_stage_H_refusals"], 18)
        self.assertEqual(matrix["ordered_successor_refusals"], 43)
        self.assertEqual(
            tuple(matrix["successor_case_order"]),
            recovery.ORDERED_SUCCESSOR_REFUSAL_CASES,
        )
        self.assertTrue(matrix["marker_before_capability"])
        self.assertTrue(matrix["response_closure"])
        self.assertTrue(matrix["no_staging_or_unaccepted_payload_debris"])
        self.assertTrue(matrix["consumed_rerun_refusal"])

    def test_result_validation_rejects_malformed_and_nonzero_real_operations(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-result-") as temporary:
            path = Path(temporary) / "result.json"
            path.write_text("{\"duplicate\":1,\"duplicate\":2}\n", encoding="utf-8")
            with self.assertRaises(qualification.QualificationRefusal):
                qualification.inspect_result(path)

            result = qualification._result(
                status="failed_consumed_generated_only",
                matrix=None,
                runtime=0.1,
                peak_rss=1024,
                generated_output_bytes=0,
                allocated_bytes=0,
                free_before=1024**3,
                free_after=1024**3,
            )
            result["operation_counters"]["real_EDF_payload_or_header_reads"] = 1
            with self.assertRaises(qualification.QualificationRefusal):
                qualification.validate_result(result)

    def test_official_guard_refuses_preexisting_consumed_marker_before_matrix(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-consumed-") as temporary:
            repository = Path(temporary)
            decision = repository / qualification.DECISION_RELATIVE_PATH
            decision.parent.mkdir(parents=True)
            decision.write_bytes(
                (ROOT / qualification.DECISION_RELATIVE_PATH).read_bytes()
            )
            qualification_root = repository / qualification.QUALIFICATION_RELATIVE_ROOT
            qualification_root.mkdir(parents=True)
            (qualification_root / qualification.CONSUMED_MARKER_NAME).write_text(
                "preserve\n", encoding="ascii"
            )
            environ = {key: "1" for key in recovery.THREAD_ENV_KEYS}
            with self.assertRaises(qualification.QualificationRefusal) as caught:
                qualification.run_official_qualification(
                    repo_root=repository,
                    environ=environ,
                )
            self.assertEqual(caught.exception.code, "HL1R1-Q-CONSUMED")
            self.assertEqual(
                (qualification_root / qualification.CONSUMED_MARKER_NAME).read_text(
                    encoding="ascii"
                ),
                "preserve\n",
            )

    def test_cli_has_no_path_or_real_execution_arguments(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_qualification_cli",
                "--help",
            ],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("plan", completed.stdout)
        self.assertIn("qualify", completed.stdout)
        self.assertIn("inspect", completed.stdout)
        self.assertNotIn("URL", completed.stdout)
        self.assertNotIn("EDF", completed.stdout)
        self.assertNotIn("HL2", completed.stdout)

    def test_plan_preserves_real_data_and_claim_boundaries(self):
        plan = qualification.registered_plan()

        self.assertEqual(plan["registered_attempts_maximum"], 1)
        self.assertFalse(plan["real_command_available"])
        self.assertFalse(plan["network_allowed"])
        self.assertFalse(plan["HL2_authority"])
        self.assertFalse(plan["real_EDF_authority"])


if __name__ == "__main__":
    unittest.main()
