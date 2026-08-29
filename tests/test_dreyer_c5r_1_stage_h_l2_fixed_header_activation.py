import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_l2 as hl2


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / hl2.ACTIVATION_RELATIVE_PATH
DOCUMENT = ROOT / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_ACTIVATION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DreyerStageHL2FixedHeaderActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.activation = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_activation_binds_exact_green_implementation(self):
        green = self.activation["green_implementation"]
        self.assertEqual(
            green["commit"], "a9cd0be7c22996154c28bb568e05c623606e7424"
        )
        self.assertEqual(green["CI_run_id"], 33_260_534_900)
        self.assertEqual(green["base_python_job_id"], 99_121_591_361)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_121_591_482)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])
        artifacts = self.activation["bound_implementation_artifacts"]
        self.assertEqual(len(artifacts), 6)
        self.assertEqual(sum(row["bytes"] for row in artifacts), 79_741)
        for row in artifacts:
            path = ROOT / row["path"]
            self.assertEqual(path.stat().st_size, row["bytes"])
            self.assertEqual(_sha256(path), row["sha256"])

    def test_activation_is_strict_and_no_authority_before_own_green(self):
        evidence = hl2.ActivationEvidence(
            activation_sha256=_sha256(REGISTRY),
            activation_commit="1" * 40,
            activation_ci_run_id=1,
            activation_base_job_id=1,
            activation_optional_job_id=1,
        )
        hl2.validate_activation(self.activation, evidence, repo_root=ROOT)
        self.assertEqual(
            self.activation["status"],
            "no_authority_record_effective_only_after_own_remote_green",
        )
        barrier = self.activation["activation_barrier"]
        self.assertFalse(barrier["effective_before_own_remote_green"])
        self.assertFalse(barrier["registered_execution_authority_now"])
        self.assertFalse(barrier["real_EDF_access_authority_now"])
        self.assertEqual(
            set(self.activation["activation_record_operation_counters"].values()),
            {0},
        )
        self.assertEqual(set(self.activation["claim_boundary"].values()), {False})

    def test_one_shot_order_resources_and_claim_language_are_frozen(self):
        ordered = self.activation["ordered_execution_after_remote_green"]
        self.assertEqual(ordered["registered_invocations_maximum"], 1)
        self.assertTrue(ordered["marker_before_opener_or_request"])
        self.assertEqual(ordered["real_HTTP_GET_requests_exact"], 1)
        self.assertEqual(ordered["fixed_header_semantic_parses_maximum"], 1)
        self.assertEqual(ordered["retries"], 0)
        self.assertEqual(ordered["reruns"], 0)
        resources = self.activation["resource_envelope"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["peak_process_tree_RSS_bytes_maximum"], 256 * 1024**2)
        self.assertEqual(resources["minimum_free_disk_bytes"], 10 * 1024**3)
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
