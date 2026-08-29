import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live as live

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_generated_qualification_result.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT / "registries/dreyer_c5r_1_stage_h_live_implementation.v0.json"
)


class DreyerStageHLiveQualificationCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )

    def test_consumed_attempt_is_rejected_and_cannot_activate_HL2(self):
        self.assertEqual(
            self.result["status"],
            "consumed_rejected_post_run_failure_cleanup_gate",
        )
        self.assertFalse(self.result["post_run_acceptance_audit"]["all_gates_passed"])
        self.assertTrue(self.result["routing"]["registered_qualification_consumed"])
        self.assertFalse(self.result["routing"]["registered_qualification_rerun_allowed"])
        self.assertFalse(self.result["routing"]["HL2_activation_allowed"])
        self.assertFalse(self.result["routing"]["HL2_real_invocation_consumed"])

    def test_exact_qualified_source_bytes_are_frozen(self):
        for artifact in self.implementation["tracked_file_hashes"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_activation_loader_rejects_failed_implementation_record(self):
        digest = hashlib.sha256(IMPLEMENTATION_PATH.read_bytes()).hexdigest()
        with self.assertRaises(live.StageHLiveRefusal) as caught:
            live.load_implementation_record(ROOT, expected_sha256=digest)
        self.assertEqual(caught.exception.code, "HL1-PROOF")

    def test_post_marker_opener_refusal_reproduces_cleanup_defect(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).absolute()
            (root / ".codex_work").mkdir(mode=0o700)

            def refuse_opener():
                raise live.StageHLiveRefusal(
                    "HL1-TRANSPORT",
                    "generated opener refusal",
                )

            with self.assertRaises(live.StageHLiveRefusal) as caught:
                live._execute_after_proof(
                    root,
                    root / "result.json",
                    live._generated_evidence(),
                    live._generated_remote_proof(),
                    refuse_opener,
                    environ=live._generated_environment(),
                    disk_usage_reader=live._generated_disk_usage,
                    rss_reader=lambda: 1,
                    generated_only=True,
                )
            private_root = root / live.PRIVATE_ROOT_RELATIVE_PATH
            self.assertEqual(caught.exception.code, "HL1-TRANSPORT")
            self.assertTrue((private_root / live.CONSUMED_MARKER_NAME).is_file())
            self.assertTrue((private_root / live.STAGING_DIRECTORY_NAME).is_dir())
            self.assertFalse((root / "result.json").exists())

    def test_all_real_scientific_and_release_counters_are_zero(self):
        counters = self.implementation["implementation_access_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))
        self.assertFalse(self.result["routing"]["Dreyer_lane_scientifically_parked"])


if __name__ == "__main__":
    unittest.main()
