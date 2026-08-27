from __future__ import annotations

import hashlib
import inspect
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import fields, replace
from io import StringIO
from pathlib import Path

from neurodecodekit import comm_g2_cli
from neurodecodekit.experiments import comm_g2_generated_proof as experiment


ROOT = Path(__file__).resolve().parents[1]


class CommG2GeneratedProofImplementationTests(unittest.TestCase):
    def test_registration_and_frozen_module_are_exact(self) -> None:
        contract = experiment.load_registration(ROOT)
        self.assertEqual(
            contract["contract_id"],
            "COMM-G2-generated-proof-qualification-contract-v0",
        )
        module = ROOT / experiment.FROZEN_G1_MODULE_PATH
        self.assertEqual(
            hashlib.sha256(module.read_bytes()).hexdigest(),
            experiment.FROZEN_G1_MODULE_SHA256,
        )

    def test_implementation_record_binds_exact_artifacts(self) -> None:
        record = experiment.load_implementation_record(ROOT)
        self.assertEqual(
            record["status"],
            "implementation_ready_pending_exact_commit_push_remote_green",
        )
        self.assertFalse(record["official_qualification"]["executed"])
        for artifact in record["artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(artifact["bytes"], len(payload))
            self.assertEqual(artifact["sha256"], hashlib.sha256(payload).hexdigest())

    def test_fold_job_has_no_held_out_target_field(self) -> None:
        self.assertEqual(
            {field.name for field in fields(experiment.FoldJob)},
            {
                "held_out_participant",
                "source_rows",
                "source_targets",
                "held_out_rows",
            },
        )
        source = inspect.getsource(experiment._predict_fold)
        self.assertNotIn("held_out_targets", source)
        self.assertNotIn("target_vault", source)
        scorer_source = inspect.getsource(experiment._score_after_freeze)
        self.assertNotIn("_fit_", scorer_source)
        self.assertNotIn("train", scorer_source.lower())

    def test_plan_is_bounded_and_generated_only(self) -> None:
        plan = experiment.plan()
        self.assertEqual(plan["full_isolated_replays"], 2)
        self.assertEqual(plan["total_parameter_updates"], 120)
        self.assertEqual(plan["total_prediction_rows"], 2880)
        self.assertEqual(plan["real_or_private_operations"], 0)
        self.assertEqual(plan["scientific_value"], "none_generated_engineering_only")

    def test_canonical_digest_binds_cue_timing_and_all_metadata(self) -> None:
        try:
            from neurodecodekit.experiments import comm_g1_generated as g1

            rows, targets, _ = g1.generate_fixture()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        original = experiment.canonical_fixture_digest(rows, targets)
        cue_rows = list(rows)
        cue_rows[0] = replace(cue_rows[0], cue=(1.0, 0.0, 0.0, 0.0))
        timing_rows = list(rows)
        timing_rows[0] = replace(timing_rows[0], timing=(0.25, 0.75))
        dtype_rows = list(rows)
        dtype_rows[0] = replace(dtype_rows[0], signal=dtype_rows[0].signal.astype("float32"))
        geometry_rows = list(rows)
        changed_geometry = list(geometry_rows[0].channel_geometry)
        changed_geometry[0] = (0.1, 0.2, 0.3)
        geometry_rows[0] = replace(
            geometry_rows[0], channel_geometry=tuple(changed_geometry)
        )
        self.assertNotEqual(original, experiment.canonical_fixture_digest(cue_rows, targets))
        self.assertNotEqual(
            original, experiment.canonical_fixture_digest(timing_rows, targets)
        )
        self.assertNotEqual(
            original, experiment.canonical_fixture_digest(dtype_rows, targets)
        )
        with self.assertRaisesRegex(Exception, "CHANNEL-GEOMETRY"):
            experiment.canonical_fixture_digest(geometry_rows, targets)

    @staticmethod
    def _predictions() -> list[dict[str, object]]:
        predictions = []
        for participant_index in range(6):
            participant = f"gsub-{participant_index + 1:02d}"
            for item_index in range(24):
                item_id = f"{participant}-item-{item_index:02d}"
                for condition in experiment.g1.CONDITIONS:
                    predictions.append(
                        {
                            "item_id": item_id,
                            "participant_id": participant,
                            "condition": condition,
                            "probabilities": [0.25, 0.25, 0.25, 0.25],
                        }
                    )
        return predictions

    @staticmethod
    def _manifests() -> list[dict[str, object]]:
        return [
            {
                "held_out_participant": f"gsub-{index + 1:02d}",
                "held_out_item_ids": [
                    f"gsub-{index + 1:02d}-item-{item:02d}" for item in range(24)
                ],
            }
            for index in range(6)
        ]

    def test_prediction_inventory_and_freeze_are_strict(self) -> None:
        predictions = self._predictions()
        manifests = self._manifests()
        freeze = experiment.build_prediction_freeze(predictions, manifests)
        experiment.verify_prediction_freeze(predictions, manifests, freeze)
        with self.assertRaisesRegex(experiment.CommG2Refusal, "DUPLICATE"):
            experiment.validate_prediction_inventory([*predictions[:-1], predictions[0]])
        with self.assertRaisesRegex(experiment.CommG2Refusal, "NONFINITE"):
            malformed = [dict(value) for value in predictions]
            malformed[0] = {**malformed[0], "probabilities": [float("nan"), 0.3, 0.3, 0.4]}
            experiment.validate_prediction_inventory(malformed)

    def test_non_replacing_publication_and_symlink_refusal(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            output = root / "result.json"
            experiment._publish_no_replace(output, b"{}\n")
            self.assertEqual(experiment._read_regular_no_follow(output), b"{}\n")
            with self.assertRaisesRegex(experiment.CommG2Refusal, "OUTPUT-CLOBBER"):
                experiment._publish_no_replace(output, b"changed")
            target = root / "target"
            target.mkdir()
            link = root / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(experiment.CommG2Refusal, "DIRECTORY-CAPABILITY"):
                experiment._publish_no_replace(link / "escaped", b"x")

    def test_output_must_remain_inside_neurodecodekit(self) -> None:
        experiment._require_output_within_repository(
            ROOT / "registries" / "result.json", ROOT
        )
        with self.assertRaisesRegex(
            experiment.CommG2Refusal, "OUTPUT-OUTSIDE-REPOSITORY"
        ):
            experiment._require_output_within_repository(
                ROOT.parent / "another-project" / "result.json", ROOT
            )

    def test_resource_caps_refuse_each_registered_surface(self) -> None:
        base = {
            "runtime_seconds": 0,
            "peak_process_tree_RSS_bytes": 0,
            "generated_input_bytes": 0,
            "private_generated_output_bytes": 0,
            "public_output_bytes": 0,
            "temporary_disk_bytes": 0,
        }
        experiment.enforce_resource_caps(base)
        for field, cap in (
            ("runtime_seconds", "wall_time_seconds"),
            ("peak_process_tree_RSS_bytes", "peak_process_tree_RSS_bytes"),
            ("generated_input_bytes", "generated_input_bytes_total_maximum"),
            ("private_generated_output_bytes", "private_generated_output_bytes_total_maximum"),
            ("public_output_bytes", "public_output_bytes_maximum"),
            ("temporary_disk_bytes", "temporary_disk_bytes_maximum"),
        ):
            with self.assertRaises(experiment.CommG2Refusal):
                experiment.enforce_resource_caps(
                    {**base, field: experiment.CAPS[cap] + 1}
                )

    def test_child_process_is_real_and_returns_only_requested_value(self) -> None:
        value = experiment._run_child(
            experiment.plan, timeout_seconds=10, rss_reader=lambda _pid: 0
        )
        self.assertEqual(value["lane_id"], "COMM-G2")
        self.assertEqual(value["real_or_private_operations"], 0)
        environment = experiment._run_child(
            experiment._environment_snapshot,
            timeout_seconds=10,
            rss_reader=lambda _pid: 0,
        )
        self.assertEqual(environment, experiment._sanitized_child_environment())
        self.assertNotIn("OPENAI_API_KEY", environment)

    def test_cleanup_refuses_replaced_root_without_deleting_replacement(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            parent = Path(directory)
            owned = parent / "owned"
            owned.mkdir()
            info = owned.stat()
            identity = (info.st_dev, info.st_ino)
            moved = parent / "moved"
            owned.rename(moved)
            owned.mkdir()
            sentinel = owned / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(experiment.CommG2Refusal, "CLEANUP-IDENTITY"):
                experiment._secure_remove_tree(owned, identity)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
            self.assertTrue(moved.is_dir())

    def test_every_registered_adversarial_family_is_implemented(self) -> None:
        contract = experiment.load_registration(ROOT)
        self.assertEqual(
            list(experiment.ADVERSARIAL_FAMILIES),
            contract["adversarial_qualification"]["families"],
        )
        self.assertEqual(len(experiment.ADVERSARIAL_FAMILIES), 35)

    def test_all_35_adversarial_families_execute_without_model_fit(self) -> None:
        try:
            rows, targets, _ = experiment.g1.generate_fixture()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        predictions = self._predictions()
        manifests = self._manifests()
        freeze = experiment.build_prediction_freeze(predictions, manifests)
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            refusal_ids = experiment.exercise_adversarial_refusals(
                rows,
                targets,
                predictions,
                manifests,
                freeze,
                Path(directory),
            )
        self.assertEqual(
            refusal_ids,
            [f"G2-{family}" for family in experiment.ADVERSARIAL_FAMILIES],
        )

    def test_cli_exposes_only_plan_qualify_and_inspect(self) -> None:
        help_text = comm_g2_cli._parser().format_help()
        self.assertIn("{plan,qualify,inspect}", help_text)
        self.assertNotIn("real", help_text.lower())
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(comm_g2_cli.main(["plan"]), 0)
        value = json.loads(output.getvalue())
        self.assertEqual(value["lane_id"], "COMM-G2")

    def test_qualifier_checks_registration_and_remote_proof_before_replays(self) -> None:
        source = inspect.getsource(experiment.run_generated_qualification)
        self.assertLess(source.index("load_registration"), source.index("collector ="))
        self.assertLess(
            source.index("validate_remote_green_proof"), source.index("_run_child")
        )
        self.assertNotIn("requests", source)
        self.assertNotIn("http", source.lower())

    @unittest.skipUnless(
        os.environ.get("NDK_COMM_G2_DEV_REPLAY") == "1",
        "single generated replay is opt-in and is not the official qualification",
    )
    def test_opt_in_single_replay_development_path(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            workdir = Path(directory) / "replay"
            workdir.mkdir()
            runtime_temp = Path(directory) / "runtime"
            runtime_temp.mkdir()
            result = experiment._run_child(
                experiment._run_replay,
                "development-replay",
                str(workdir),
                timeout_seconds=85,
                child_tempdir=runtime_temp,
            )
        deterministic = result["deterministic"]
        self.assertEqual(deterministic["schedule"]["residualizer_fits"], 6)
        self.assertEqual(
            deterministic["schedule"]["classifier_or_prior_fits"], 54
        )
        self.assertEqual(deterministic["schedule"]["prediction_rows"], 1440)
        self.assertEqual(deterministic["router_outcome"], "COMM-G2-R1")
        self.assertEqual(len(deterministic["adversarial_refusal_ids"]), 35)


if __name__ == "__main__":
    unittest.main()
