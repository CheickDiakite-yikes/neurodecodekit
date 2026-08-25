from __future__ import annotations

import importlib.util
import io
import inspect
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.datasets import bnci_2014_001_stage_q as core  # noqa: E402
from neurodecodekit.datasets import bnci_2014_001_stage_q_live as live  # noqa: E402


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


class BNCIStageQLiveControlTests(unittest.TestCase):
    def _activation(self) -> dict[str, object]:
        return {
            "lane_id": core.LANE_ID,
            "status": "remotely_green_live_execution_enabled",
            "green_stage_a_result": {
                "commit": core.STAGE_A_RESULT_COMMIT,
                "CI_run_id": core.STAGE_A_RESULT_CI_RUN_ID,
                "base_python_job_id": core.STAGE_A_RESULT_BASE_JOB_ID,
                "optional_neuro_readers_job_id": core.STAGE_A_RESULT_OPTIONAL_JOB_ID,
                "both_required_jobs_green": True,
            },
            "green_implementation": {
                "commit": "a" * 40,
                "CI_head_sha": "a" * 40,
                "CI_conclusion": "success",
                "CI_run_id": 1,
                "base_python_job_id": 2,
                "base_python_job_name": "Base Python",
                "base_python_job_conclusion": "success",
                "optional_neuro_readers_job_id": 3,
                "optional_neuro_readers_job_name": "Optional Neuro Readers",
                "optional_neuro_readers_job_conclusion": "success",
                "both_required_jobs_green": True,
            },
            "qualified_generated_core": {
                "path": live.QUALIFIED_RESULT_RELATIVE_PATH.as_posix(),
                "sha256": live.QUALIFIED_RESULT_SHA256,
                "consumed": True,
                "may_be_repeated": False,
            },
            "implementation_artifacts": [
                {"path": path, "bytes": 1, "sha256": "b" * 64}
                for path in live.LIVE_IMPLEMENTATION_ARTIFACTS
            ],
            "authority": {
                "one_live_Stage_Q_execution": True,
                "network_bytes": 0,
                "model_runs": 0,
                "training_runs": 0,
                "prediction_sets": 0,
                "target_deliveries": 0,
                "scores": 0,
                "reruns": 0,
                "Stage_P": False,
                "Stage_T": False,
                "claim_upgrade": False,
            },
        }

    def _remote_proof(self) -> dict[str, object]:
        return {
            "branch": "codex/stage-q-test",
            "head_sha": "c" * 40,
            "remote_head_sha": "c" * 40,
            "CI_run_id": 10,
            "CI_head_sha": "c" * 40,
            "CI_conclusion": "success",
            "base_python_job_id": 11,
            "base_python_job_name": "Base Python",
            "base_python_job_conclusion": "success",
            "optional_neuro_readers_job_id": 12,
            "optional_neuro_readers_job_name": "Optional Neuro Readers",
            "optional_neuro_readers_job_conclusion": "success",
        }

    def test_activation_requires_exact_commit_ci_artifacts_and_authority(self) -> None:
        self.assertEqual(live.validate_activation_document(self._activation())["lane_id"], core.LANE_ID)
        mutations = []
        bad_commit = self._activation()
        bad_commit["green_implementation"]["commit"] = "HEAD"
        mutations.append(bad_commit)
        bad_head = self._activation()
        bad_head["green_implementation"]["CI_head_sha"] = "b" * 40
        mutations.append(bad_head)
        bad_ci = self._activation()
        bad_ci["green_implementation"]["CI_run_id"] = 0
        mutations.append(bad_ci)
        missing_artifact = self._activation()
        missing_artifact["implementation_artifacts"] = missing_artifact["implementation_artifacts"][:-1]
        mutations.append(missing_artifact)
        broad_authority = self._activation()
        broad_authority["authority"]["Stage_P"] = True
        mutations.append(broad_authority)
        extra_field = self._activation()
        extra_field["expanded_scope"] = True
        mutations.append(extra_field)
        for value in mutations:
            with self.subTest(value=value):
                with self.assertRaises(core.BNCIStageQRefusal):
                    live.validate_activation_document(value)

    def test_authenticated_envelope_roundtrip_and_tamper_refusal(self) -> None:
        key = bytes(range(32))
        payload = b"fold-scoped-targets"
        envelope = live.seal_payload(payload, key)
        self.assertNotIn(payload, envelope)
        self.assertEqual(live.unseal_payload(envelope, key), payload)
        changed = bytearray(envelope)
        changed[-1] ^= 1
        with self.assertRaisesRegex(core.BNCIStageQRefusal, "authentication"):
            live.unseal_payload(bytes(changed), key)

    def test_remote_green_collector_requires_fresh_head_and_both_jobs(self) -> None:
        head = "c" * 40
        responses = [
            subprocess.CompletedProcess([], 0, f"{head}\trefs/heads/codex/stage-q-test\n", ""),
            subprocess.CompletedProcess(
                [],
                0,
                json.dumps(
                    [
                        {
                            "databaseId": 10,
                            "headSha": head,
                            "status": "completed",
                            "conclusion": "success",
                        }
                    ]
                ),
                "",
            ),
            subprocess.CompletedProcess(
                [],
                0,
                json.dumps(
                    {
                        "headSha": head,
                        "status": "completed",
                        "conclusion": "success",
                        "jobs": [
                            {
                                "databaseId": 11,
                                "name": "Base Python",
                                "status": "completed",
                                "conclusion": "success",
                            },
                            {
                                "databaseId": 12,
                                "name": "Optional Neuro Readers",
                                "status": "completed",
                                "conclusion": "success",
                            },
                        ],
                    }
                ),
                "",
            ),
        ]
        with mock.patch.object(
            core,
            "_git_output",
            side_effect=[b"codex/stage-q-test\n", f"{head}\n".encode()] * 2,
        ):
            proof = live.collect_remote_green_proof(
                ROOT, runner=mock.Mock(side_effect=responses)
            )
        self.assertEqual(proof, self._remote_proof())

        responses[0] = subprocess.CompletedProcess(
            [], 0, f"{'d' * 40}\trefs/heads/codex/stage-q-test\n", ""
        )
        with mock.patch.object(
            core,
            "_git_output",
            side_effect=[b"codex/stage-q-test\n", f"{head}\n".encode()],
        ):
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "remote head"):
                live.collect_remote_green_proof(
                    ROOT, runner=mock.Mock(side_effect=responses)
                )

    @unittest.skipUnless(NUMPY_AVAILABLE, "Stage Q fold-array test requires NumPy")
    def test_fold_capabilities_exclude_held_out_T_and_source_labels(self) -> None:
        np = core._np()
        participants = np.repeat(np.arange(9, dtype="uint8"), 2 * 288)
        sessions = np.tile(np.repeat(np.arange(2, dtype="uint8"), 288), 9)
        source, held_out_e, held_out_t = live.fold_masks(participants, sessions, 0)
        self.assertEqual((int(source.sum()), int(held_out_e.sum()), int(held_out_t.sum())), (4608, 288, 288))
        self.assertFalse(source[participants == 0].any())
        self.assertFalse(held_out_e[sessions == 0].any())

    @unittest.skipUnless(NUMPY_AVAILABLE, "Stage Q derivative test requires NumPy")
    def test_one_copy_shards_and_fold_manifests_exclude_held_out_T(self) -> None:
        np = core._np()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "stage-q"
            identities = {
                "participant_index": np.repeat(np.arange(9, dtype="uint8"), 2).tolist(),
                "session_index": np.tile(np.arange(2, dtype="uint8"), 9).tolist(),
                "run_ordinal": [0] * 18,
                "trial_ordinal": [0] * 18,
                "trial_start_sample": [0] * 18,
                "opaque_row_id": [f"{index:064x}".encode() for index in range(18)],
            }
            with mock.patch.multiple(
                core,
                ROWS_TOTAL=18,
                SOURCE_ROWS_PER_FOLD=16,
                HELD_OUT_E_ROWS_PER_FOLD=1,
                FEATURE_DIMENSIONS={"E1": 1},
            ):
                manifest, total = live._write_live_derivatives(
                    root,
                    output,
                    {"E1": [np.asarray([index], dtype="float32") for index in range(18)]},
                    identities,
                    np.arange(18, dtype="uint8") % 4,
                    np.zeros(18, dtype="uint8"),
                    np.asarray([0, 1] * 9, dtype="uint8"),
                    key_factory=lambda size: bytes([7]) * size,
                    scoring_key_path=root / "scoring-keys.private.json",
                )
            self.assertGreater(total, 0)
            self.assertTrue(manifest["scoring_keys_are_outside_the_fold_capability_tree"])
            self.assertEqual(manifest["held_out_T_rows_exposed_per_fold"], 0)
            self.assertEqual(manifest["participant_session_signal_shards"], 18)
            with np.load(
                output / "participant_signal_shards/A01T.target_free.private.v0.npz",
                allow_pickle=False,
            ) as archive:
                self.assertFalse(set(archive.files).intersection({"target_index", "artifact_flag"}))
                self.assertEqual(archive["participant_index"].tolist(), [0])
                self.assertEqual(archive["session_index"].tolist(), [0])
            delivery = json.loads(
                (output / "fold_capabilities/fold_A01.delivery.private.v0.json").read_text(
                    encoding="utf-8"
                )
            )
            delivered = {row["file"] for row in delivery["signal_shards"]}
            self.assertNotIn(
                "participant_signal_shards/A01T.target_free.private.v0.npz", delivered
            )
            self.assertIn(
                "participant_signal_shards/A01E.target_free.private.v0.npz", delivered
            )
            self.assertEqual(delivery["held_out_T_rows_delivered"], 0)
            with np.load(
                output / "fold_capabilities/fold_A01.source_targets.private.v0.npz",
                allow_pickle=False,
            ) as archive:
                self.assertEqual(archive["target_index"].shape, (16,))
            scoring_keys = json.loads(
                (root / "scoring-keys.private.json").read_text(encoding="utf-8")
            )["keys"]
            scoring_envelope = (output / "scoring_target_vault/fold_A01.sealed.v0.bin").read_bytes()
            scoring_plaintext = live.unseal_payload(scoring_envelope, bytes.fromhex(scoring_keys["A01"]))
            with np.load(io.BytesIO(scoring_plaintext), allow_pickle=False) as archive:
                self.assertEqual(archive["target_index"].tolist(), [1])

    def test_one_copy_layout_has_a_conservative_preflight_margin(self) -> None:
        duplicated_signal_bytes = (
            len(core.PARTICIPANTS)
            * (core.SOURCE_ROWS_PER_FOLD + core.HELD_OUT_E_ROWS_PER_FOLD)
            * sum(core.FEATURE_DIMENSIONS.values())
            * 4
        )
        self.assertGreater(duplicated_signal_bytes, core.PRIVATE_OUTPUT_CAP_BYTES)
        self.assertLess(
            live.private_layout_preflight_bound_bytes(), core.PRIVATE_OUTPUT_CAP_BYTES
        )

    def test_anchored_writer_refuses_symlink_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            (root / "redirect").symlink_to(outside)
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "ancestry"):
                live._exclusive_write(root, root / "redirect/output.bin", b"no")
            self.assertFalse((Path(outside) / "output.bin").exists())

    def test_temporary_directory_requires_exclusive_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "existing"
            candidate.mkdir()
            (candidate / "unrelated.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "already exists"):
                live._exclusive_directory(root, candidate)
            self.assertEqual((candidate / "unrelated.txt").read_text(encoding="utf-8"), "keep")

    @unittest.skipUnless(NUMPY_AVAILABLE, "Stage Q orchestration test requires NumPy")
    def test_generated_end_to_end_live_orchestration_orders_marker_and_receipt(self) -> None:
        np = core._np()
        members = (
            core.PayloadMember("sourcedata/A01T.mat", 1, "0" * 64),
            core.PayloadMember("sourcedata/A01E.mat", 1, "1" * 64),
        )
        task_run = core.TaskRun(
            signal=np.zeros((2, 1), dtype="float32"),
            starts=np.asarray([0, 1500], dtype="int64"),
            targets=np.asarray([1, 2], dtype="uint8"),
            artifacts=np.asarray([0, 0], dtype="uint8"),
            artifacts_available=True,
        )
        activation = self._activation()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def private_manifest(_root, _members):
                self.assertTrue((root / core.STAGE_Q_MARKER_RELATIVE_PATH).is_file())
                return {"status": "fixture"}

            patches = (
                mock.patch.object(core, "_repo_root", return_value=root.resolve()),
                mock.patch.object(core, "load_public_bindings"),
                mock.patch.object(core, "assert_exact_versions", return_value={"numpy": "2.5.2", "scipy": "1.18.0"}),
                mock.patch.object(core, "registered_members", return_value=members),
                mock.patch.object(core, "_private_manifest", side_effect=private_manifest),
                mock.patch.object(core, "_read_exact_member", return_value=b"x"),
                mock.patch.object(core, "parse_verified_mat_payload", return_value=([task_run], 1)),
                mock.patch.object(
                    core,
                    "extract_target_free_run_features",
                    return_value={"E1": np.asarray([[0.0], [1.0]], dtype="float32")},
                ),
                mock.patch.object(live, "read_green_live_activation", return_value=activation),
                mock.patch.object(
                    live,
                    "validate_remote_green_proof",
                    return_value=self._remote_proof(),
                ),
            )
            with mock.patch.multiple(
                core,
                PARTICIPANTS=("A01",),
                MAT_FILE_COUNT=2,
                TASK_RUNS_PER_FILE=1,
                TRIALS_PER_RUN=2,
                ROWS_TOTAL=4,
                SOURCE_ROWS_PER_FOLD=0,
                HELD_OUT_E_ROWS_PER_FOLD=2,
                FEATURE_DIMENSIONS={"E1": 1},
            ):
                for patcher in patches:
                    patcher.start()
                try:
                    receipt = live.execute_registered_stage_q_live(
                        root,
                        environ={name: "1" for name in core.THREAD_ENVIRONMENT},
                        remote_green_proof=self._remote_proof(),
                        key_factory=lambda size: bytes([9]) * size,
                    )
                finally:
                    for patcher in reversed(patches):
                        patcher.stop()
            self.assertEqual(receipt["operations"]["MAT_content_opens"], 2)
            self.assertEqual(receipt["operations"]["MAT_semantic_parses"], 2)
            self.assertEqual(receipt["operations"]["model_runs"], 0)
            self.assertTrue((root / core.STAGE_Q_OUTPUT_RELATIVE_PATH / "manifest.private.v0.json").is_file())
            self.assertTrue((root / core.STAGE_Q_RECEIPT_RELATIVE_PATH).is_file())
            self.assertTrue((root / live.SCORING_KEY_VAULT_RELATIVE_PATH).is_file())

    def test_disk_preflight_refuses_before_marker_or_private_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                mock.patch.object(core, "_repo_root", return_value=root.resolve()),
                mock.patch.object(core, "assert_single_thread_environment"),
                mock.patch.object(core, "assert_exact_versions", return_value={}),
                mock.patch.object(core, "load_public_bindings"),
                mock.patch.object(live, "read_green_live_activation", return_value=self._activation()),
                mock.patch.object(
                    live,
                    "validate_remote_green_proof",
                    return_value=self._remote_proof(),
                ),
                mock.patch.object(core, "registered_members", return_value=()),
                mock.patch.object(
                    live.shutil,
                    "disk_usage",
                    return_value=type("Usage", (), {"free": 1})(),
                ),
                mock.patch.object(core, "_private_manifest") as private_manifest,
            ):
                with self.assertRaisesRegex(core.BNCIStageQRefusal, "free-disk"):
                    live.execute_registered_stage_q_live(
                        root,
                        environ={name: "1" for name in core.THREAD_ENVIRONMENT},
                        remote_green_proof=self._remote_proof(),
                    )
            self.assertFalse((root / core.STAGE_Q_MARKER_RELATIVE_PATH).exists())
            private_manifest.assert_not_called()

    def test_final_resource_enforcement_refuses_runtime_rss_and_output(self) -> None:
        with mock.patch.object(time, "perf_counter", return_value=core.RUNTIME_CAP_SECONDS + 1):
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "runtime"):
                live._assert_resource_caps(started=0.0, private_bytes=0)
        with mock.patch.object(time, "perf_counter", return_value=1.0), mock.patch.object(
            core, "peak_process_rss_bytes", return_value=core.PEAK_RSS_CAP_BYTES + 1
        ):
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "RSS"):
                live._assert_resource_caps(started=0.0, private_bytes=0)
        with mock.patch.object(time, "perf_counter", return_value=1.0), mock.patch.object(
            core, "peak_process_rss_bytes", return_value=1
        ):
            with self.assertRaisesRegex(core.BNCIStageQRefusal, "derivative"):
                live._assert_resource_caps(
                    started=0.0, private_bytes=core.PRIVATE_OUTPUT_CAP_BYTES + 1
                )

    def test_consumption_and_success_publication_order_is_fail_closed(self) -> None:
        source = inspect.getsource(live.execute_registered_stage_q_live)
        marker_write = source.index("_exclusive_write(repo, marker, marker_payload)")
        self.assertLess(source.index("layout_bound ="), marker_write)
        self.assertLess(source.index("free_before ="), marker_write)
        self.assertLess(source.index("_exclusive_directory(repo, temporary)"), marker_write)
        receipt_write = source.index("_exclusive_write(repo, temporary_receipt, receipt_payload)")
        final_gate = source.index("_assert_resource_caps(", receipt_write)
        promotion = source.index("temporary.rename(output)")
        self.assertLess(receipt_write, final_gate)
        self.assertLess(final_gate, promotion)

    def test_live_cli_help_and_missing_activation_refusal(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SRC)
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.bnci_c3c5_stage_q_live_cli", "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("green-activated", completed.stdout)
        self.assertFalse((ROOT / live.LIVE_ACTIVATION_RELATIVE_PATH).exists())


if __name__ == "__main__":
    unittest.main()
