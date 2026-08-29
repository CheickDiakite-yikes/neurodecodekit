import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live_recovery as recovery


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_authorization_request.v0.json"
)


def fixed_disk(_path):
    return type(
        "Usage",
        (),
        {"free": recovery.MINIMUM_FREE_DISK_BYTES + 1024**3},
    )()


def fixed_clock():
    return 100.0


def run_case(root: Path, name: str, case: str | None = None):
    workspace = root / name
    workspace.mkdir()
    return recovery.run_development_case(
        workspace,
        case=case,
        disk_usage_reader=fixed_disk,
        rss_reader=lambda: 16 * 1024**2,
        clock=fixed_clock,
    )


class DreyerStageHLiveRecoveryContractTests(unittest.TestCase):
    def test_green_decision_and_consumed_source_identity_are_exact(self):
        decision = recovery.load_green_recovery_decision()

        self.assertEqual(decision["packet_id"], recovery.PACKET_ID)
        self.assertEqual(
            decision["green_request_proof"]["commit"],
            recovery.REQUEST_PROOF_COMMIT,
        )
        self.assertTrue(
            decision["authorization_after_decision_green"][
                "implement_additive_standard_library_successor"
            ]
        )
        self.assertFalse(
            decision["authorization_after_decision_green"][
                "run_registered_successor_generated_qualification"
            ]
        )
        for path, digest in recovery.LEGACY_ARTIFACTS:
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_ordered_43_case_inventory_matches_request(self):
        request = json.loads(REQUEST.read_text(encoding="utf-8"))

        self.assertEqual(
            tuple(
                request["mandatory_generated_qualification"][
                    "ordered_successor_refusal_cases"
                ]
            ),
            recovery.ORDERED_SUCCESSOR_REFUSAL_CASES,
        )
        self.assertEqual(len(recovery.ORDERED_SUCCESSOR_REFUSAL_CASES), 43)

    def test_valid_H1_is_deterministic_marker_first_closed_and_clean(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-valid-") as temporary:
            root = Path(temporary)
            first = run_case(root, "first")
            second = run_case(root, "second")

            self.assertEqual(first.report, second.report)
            self.assertEqual(first.report["route"], "DREYER-H1")
            self.assertEqual(first.events[:4], (
                "marker_durable",
                "transaction_entered",
                "staging_created",
                "opener_constructed",
            ))
            self.assertLess(
                first.events.index("marker_durable"),
                first.events.index("opener_constructed"),
            )
            self.assertEqual(first.opener_constructions, 1)
            self.assertEqual(first.requests, 1)
            self.assertTrue(first.response_closed)
            self.assertTrue(first.marker_path.is_file())
            self.assertTrue(first.output_path.is_file())
            self.assertTrue(first.final_payload_path.is_file())
            self.assertFalse(
                (first.marker_path.parent / recovery.STAGING_DIRECTORY_NAME).exists()
            )
            self.assertEqual(
                recovery.inspect_generated_report(first.output_path),
                first.report,
            )

    def test_all_premarker_cases_refuse_before_new_transaction_debris(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-pre-") as temporary:
            root = Path(temporary)
            for index, case in enumerate(sorted(recovery.PREMARKER_CASES)):
                workspace = root / f"case-{index:02d}"
                workspace.mkdir()
                with self.subTest(case=case):
                    with self.assertRaises(recovery.RecoveryRefusal) as caught:
                        recovery.run_development_case(
                            workspace,
                            case=case,
                            disk_usage_reader=fixed_disk,
                            rss_reader=lambda: 16 * 1024**2,
                            clock=fixed_clock,
                        )
                    self.assertEqual(caught.exception.case, case)
                    private_root = workspace / recovery.PRIVATE_ROOT_RELATIVE_PATH
                    generated_marker = private_root / recovery.CASE_MARKER_NAME
                    if case not in {"preexisting_consumed_marker", "consumed_rerun"}:
                        self.assertFalse(generated_marker.exists())

    def test_every_postmarker_case_is_H0_or_sanitized_publication_refusal(self):
        postmarker = [
            case
            for case in recovery.ORDERED_SUCCESSOR_REFUSAL_CASES
            if case not in recovery.PREMARKER_CASES
        ]
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-post-") as temporary:
            root = Path(temporary)
            for index, case in enumerate(postmarker):
                with self.subTest(case=case):
                    workspace = root / f"case-{index:02d}"
                    workspace.mkdir()
                    if case in recovery.PUBLICATION_REFUSAL_CASES:
                        with self.assertRaises(recovery.RecoveryRefusal) as caught:
                            recovery.run_development_case(
                                workspace,
                                case=case,
                                disk_usage_reader=fixed_disk,
                                rss_reader=lambda: 16 * 1024**2,
                                clock=fixed_clock,
                            )
                        self.assertEqual(caught.exception.case, case)
                    else:
                        result = recovery.run_development_case(
                            workspace,
                            case=case,
                            disk_usage_reader=fixed_disk,
                            rss_reader=lambda: 16 * 1024**2,
                            clock=fixed_clock,
                        )
                        self.assertEqual(result.report["route"], "DREYER-H0")
                        self.assertEqual(result.report["refusal_case"], case)
                        self.assertTrue(result.output_path.is_file())
                        self.assertTrue(result.response_closed)
                    private_root = workspace / recovery.PRIVATE_ROOT_RELATIVE_PATH
                    self.assertFalse(
                        (private_root / recovery.STAGING_DIRECTORY_NAME).exists()
                    )
                    self.assertFalse(
                        (private_root / recovery.FINAL_PAYLOAD_NAME).exists()
                    )

    def test_unexpected_exception_text_never_reaches_public_H0(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-sanitize-") as temporary:
            result = run_case(
                Path(temporary),
                "unexpected",
                "opener_factory_unexpected_exception",
            )

            payload = result.output_path.read_text(encoding="utf-8")
            self.assertEqual(result.report["route"], "DREYER-H0")
            self.assertEqual(
                result.report["refusal_case"],
                "opener_factory_unexpected_exception",
            )
            self.assertNotIn("secret", payload.casefold())
            self.assertNotIn("valueerror", payload.casefold())
            self.assertNotIn("traceback", payload.casefold())
            self.assertNotIn(str(result.marker_path.parent), payload)

    def test_response_close_failure_downgrades_and_removes_payload(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-close-") as temporary:
            result = run_case(
                Path(temporary),
                "close",
                "response_close_failure",
            )

            self.assertEqual(result.report["route"], "DREYER-H0")
            self.assertEqual(
                result.report["refusal_code"],
                "HL1R1-TEARDOWN",
            )
            self.assertTrue(result.report["teardown"]["response_closed"])
            self.assertTrue(result.report["teardown"]["cleanup_complete"])
            self.assertFalse(result.final_payload_path.exists())

    def test_foreign_cleanup_capability_cannot_remove_foreign_file(self):
        with tempfile.TemporaryDirectory(prefix="ndk-hl1r1-foreign-") as temporary:
            root = Path(temporary)
            foreign = root / "foreign"
            foreign.write_bytes(b"keep")
            workspace = root / "workspace"
            workspace.mkdir()

            with self.assertRaises(recovery.RecoveryRefusal):
                recovery.run_development_case(
                    workspace,
                    case="foreign_cleanup_capability",
                    disk_usage_reader=fixed_disk,
                    rss_reader=lambda: 16 * 1024**2,
                    clock=fixed_clock,
                )
            self.assertEqual(foreign.read_bytes(), b"keep")

    def test_plan_and_cli_expose_no_execution_command(self):
        plan = recovery.registered_plan()
        self.assertFalse(plan["registered_qualification_authority"])
        self.assertFalse(plan["real_command_available"])
        self.assertFalse(plan["HL2_authority"])
        self.assertFalse(plan["real_EDF_authority"])

        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_cli",
                "--help",
            ],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("plan", completed.stdout)
        self.assertIn("inspect", completed.stdout)
        self.assertNotIn("execute", completed.stdout)
        self.assertNotIn("qualify", completed.stdout)


if __name__ == "__main__":
    unittest.main()
