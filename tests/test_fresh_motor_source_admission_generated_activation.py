from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import fresh_motor_source_admission as admission


ROOT = Path(__file__).resolve().parents[1]
ACTIVATION = (
    ROOT / "registries/fresh_motor_source_admission_generated_qualification_activation.v0.json"
)


class FreshMotorSourceAdmissionGeneratedActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(ACTIVATION.read_text(encoding="utf-8"))

    def test_activation_binds_exact_green_implementation(self) -> None:
        self.assertEqual(self.record["recorded_at"], "2026-08-31T02:10:19Z")
        self.assertEqual(
            self.record["implementation_commit"],
            "d9229c1d8e9c56e2ce31da0dec0dcf302fe73eee",
        )
        self.assertEqual(self.record["implementation_CI_run_id"], 33_349_080_445)
        self.assertEqual(self.record["base_python_job_id"], 99_358_753_480)
        self.assertEqual(self.record["optional_neuro_readers_job_id"], 99_358_753_302)
        self.assertTrue(self.record["both_required_jobs_green"])

    def test_bound_runtime_artifacts_match(self) -> None:
        rows = self.record["bound_artifacts"]
        self.assertEqual(
            [row["path"] for row in rows],
            [path.as_posix() for path in admission.IMPLEMENTATION_ARTIFACT_PATHS],
        )
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])

    def test_runtime_loader_accepts_exact_record(self) -> None:
        observed = admission._load_implementation_activation(ROOT)
        self.assertEqual(observed, self.record)

    def test_authority_remains_generated_only(self) -> None:
        self.assertEqual(self.record["maximum_official_qualification_executions"], 1)
        self.assertEqual(
            self.record["official_qualification_root"],
            admission.OFFICIAL_QUALIFICATION_ROOT.as_posix(),
        )
        self.assertFalse(self.record["network_or_GitHub_API_authority"])
        self.assertFalse(self.record["official_index_or_real_source_authority"])
        self.assertFalse(self.record["model_score_or_scientific_claim_authority"])

    def test_scope_and_artifact_mutations_refuse(self) -> None:
        cases = (
            (
                "second_execution",
                lambda value: value.__setitem__("maximum_official_qualification_executions", 2),
            ),
            (
                "different_root",
                lambda value: value.__setitem__("official_qualification_root", ".codex_work/other"),
            ),
            (
                "network_authority",
                lambda value: value.__setitem__("network_or_GitHub_API_authority", True),
            ),
            ("artifact_order", lambda value: value["bound_artifacts"].reverse()),
            (
                "artifact_hash",
                lambda value: value["bound_artifacts"][0].__setitem__("sha256", "0" * 64),
            ),
        )
        for name, mutate in cases:
            with (
                self.subTest(name=name),
                tempfile.TemporaryDirectory(prefix="fmsr1-activation-") as directory,
            ):
                root = Path(directory)
                for relative in admission.IMPLEMENTATION_ARTIFACT_PATHS:
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / relative).read_bytes())
                changed = copy.deepcopy(self.record)
                mutate(changed)
                activation = root / admission.ACTIVATION_RELATIVE_PATH
                activation.parent.mkdir(parents=True, exist_ok=True)
                activation.write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(admission.FMSR1AdmissionRefusal):
                    admission._load_implementation_activation(root)


if __name__ == "__main__":
    unittest.main()
