from __future__ import annotations

import inspect
import json
import math
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path

from neurodecodekit import comm_r0_cli
from neurodecodekit.experiments import comm_r0_generated as experiment


ROOT = Path(__file__).resolve().parents[1]


class CommR0GeneratedImplementationTests(unittest.TestCase):
    def test_registration_is_exact_and_activation_fails_closed(self) -> None:
        contract = experiment.load_registration(ROOT)
        self.assertEqual(contract["registration_id"], "COMM-R0-REPLICATION-v0")
        self.assertEqual(tuple(contract["conditions_full_control"]), experiment.NEURAL_CONDITIONS)
        self.assertEqual(
            tuple(contract["language_control_arms"]), experiment.LANGUAGE_CONDITIONS
        )
        self.assertEqual(
            tuple(contract["generated_qualification_required_refusals"]),
            experiment.REQUIRED_REFUSALS,
        )
        if (ROOT / experiment.ACTIVATION_PATH).exists():
            activation = experiment.load_activation(ROOT)
            self.assertTrue(activation["authority"]["generated_qualification"])
        else:
            with self.assertRaisesRegex(
                experiment.CommR0GeneratedRefusal, "ACTIVATION-ABSENT"
            ):
                experiment.load_activation(ROOT)

    def test_plan_is_bounded_generated_only_and_matches_schedule(self) -> None:
        plan = experiment.plan()
        self.assertEqual(plan["participants"], 12)
        self.assertEqual(plan["replays"], 2)
        self.assertEqual(plan["parameter_update_fits_per_replay"], 156)
        self.assertEqual(plan["model_inference_runs_per_replay"], 144)
        self.assertEqual(plan["prediction_sets_per_replay"], 180)
        self.assertEqual(plan["prediction_rows_per_replay"], 4320)
        self.assertEqual(plan["real_or_private_operations"], 0)
        self.assertEqual(plan["scientific_value"], "none_generated_engineering_only")

    def test_predictor_signature_cannot_accept_held_out_targets(self) -> None:
        parameters = tuple(inspect.signature(experiment.predict_capabilities).parameters)
        self.assertEqual(parameters, ("capabilities",))
        source = inspect.getsource(experiment.predict_capabilities)
        self.assertNotIn("held_targets", source)
        self.assertNotIn("target_vault", source)

    def test_target_firewall_recurses_and_refuses_forbidden_keys(self) -> None:
        experiment.assert_target_free_payload(
            {"participant": "synthetic", "rows": [{"item_id": "x"}]}
        )
        for key in ("target", "targets", "label", "labels", "reference_text", "intended_text"):
            with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "TARGET-LEAK"):
                experiment.assert_target_free_payload({"nested": [{key: "forbidden"}]})

    def test_generated_fixture_replay_binds_signal_metadata_and_targets(self) -> None:
        try:
            rows, targets, size = experiment.generate_fixture()
            replay_rows, replay_targets, replay_size = experiment.generate_fixture()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        self.assertEqual(len(rows), 288)
        self.assertEqual(size, replay_size)
        digest = experiment.canonical_fixture_digest(rows, targets)
        self.assertEqual(
            digest, experiment.canonical_fixture_digest(replay_rows, replay_targets)
        )
        changed = list(rows)
        changed[0] = replace(changed[0], cue=(1.0, 0.0, 0.0, 0.0))
        self.assertNotEqual(digest, experiment.canonical_fixture_digest(changed, targets))

    def test_fold_capabilities_exclude_held_out_targets_and_rows(self) -> None:
        try:
            rows, targets, _ = experiment.generate_fixture()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        capabilities, vault = experiment.prepare_fold_capabilities(rows, targets)
        self.assertEqual(len(capabilities), 12)
        for capability in capabilities:
            self.assertEqual(len(capability.source_rows), 264)
            self.assertEqual(len(capability.held_out_rows), 24)
            self.assertEqual(len(capability.source_targets), 264)
            self.assertFalse(
                {row.item_id for row in capability.held_out_rows}
                & set(capability.source_targets)
            )
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "PRE-FREEZE"):
            vault.deliver(None)
        forged = experiment.CommittedPredictionFreeze({"synthetic": True}, "0" * 64)
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "PRE-FREEZE"):
            vault.deliver(forged)
        predictions = [
            {
                "item_id": row.item_id,
                "participant_id": row.participant_id,
                "session_id": row.session_id,
                "condition": condition,
                "probabilities": [0.25, 0.25, 0.25, 0.25],
            }
            for row in rows
            for condition in experiment.ALL_CONDITIONS
        ]
        freeze = experiment.build_prediction_freeze(predictions)
        committed = vault.arm(predictions, freeze)
        self.assertEqual(len(vault.deliver(committed)), 288)
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "REPEATED"):
            vault.deliver(committed)

    def test_causal_record_and_partial_route_never_proxy_missing_sensors(self) -> None:
        try:
            rows, _targets, _ = experiment.generate_fixture(
                participants=("timing-a", "timing-b")
            )
        except RuntimeError as exc:
            self.skipTest(str(exc))
        timing = experiment.causal_timing_record(rows[0])
        self.assertEqual(timing["right_context_seconds"], 0.0)
        self.assertTrue(timing["trial_boundary_oracle_used"])
        self.assertFalse(timing["continuous_or_live_claim_allowed"])
        full = experiment.route_condition_inventory(has_eog=True, has_oral_emg=True)
        self.assertEqual(full["route"], "full_control")
        self.assertTrue(full["full_peripheral_adjusted_claim_allowed"])
        partial = experiment.route_condition_inventory(has_eog=True, has_oral_emg=False)
        self.assertEqual(partial["route"], "partial_control")
        self.assertIn("oral_EMG_only", partial["unavailable_conditions"])
        self.assertIn("peripheral_context_P", partial["unavailable_conditions"])
        self.assertNotIn("oral_EMG_only", partial["conditions"])
        self.assertFalse(partial["full_peripheral_adjusted_claim_allowed"])

    def test_all_k_minus_one_derangements_are_distinct_complete_and_source_only(self) -> None:
        try:
            rows, targets, _ = experiment.generate_fixture(
                participants=("source-a", "source-b")
            )
            np = experiment.g1._np()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        residuals = np.arange(len(rows) * 3, dtype="float64").reshape(len(rows), 3)
        outputs = [
            experiment.cyclic_source_derangement(rows, targets, residuals, shift=shift)
            for shift in range(1, 4)
        ]
        self.assertEqual(len({value.tobytes() for value in outputs}), 3)
        for output in outputs:
            self.assertEqual(
                sorted(map(tuple, output.tolist())),
                sorted(map(tuple, residuals.tolist())),
            )
            self.assertFalse(np.array_equal(output, residuals))
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "SHIFT"):
            experiment.cyclic_source_derangement(rows, targets, residuals, shift=0)

    def test_language_arms_are_target_blind_and_item_deranged(self) -> None:
        try:
            rows, _targets, _ = experiment.generate_fixture(
                participants=("held-a", "held-b")
            )
            np = experiment.g1._np()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        held_rows = [row for row in rows if row.participant_id == "held-a"]
        prior = np.tile(np.asarray([0.4, 0.3, 0.2, 0.1]), (len(held_rows), 1))
        candidate = np.asarray(
            [np.roll([0.7, 0.1, 0.1, 0.1], index % 4) for index in range(len(held_rows))]
        )
        first = experiment._derive_language_arms(held_rows, prior, candidate)
        second = experiment._derive_language_arms(held_rows, prior, candidate)
        self.assertEqual(set(first), set(experiment.LANGUAGE_CONDITIONS))
        for condition in experiment.LANGUAGE_CONDITIONS:
            self.assertTrue(np.array_equal(first[condition], second[condition]))
        self.assertFalse(
            np.array_equal(
                first["neural_plus_language"],
                first["item_deranged_neural_plus_language"],
            )
        )
        source = inspect.getsource(experiment._derive_language_arms)
        self.assertNotIn("targets", source)
        self.assertNotIn("participant_id}|", source)

    @staticmethod
    def _synthetic_predictions() -> tuple[list[dict[str, object]], dict[str, int]]:
        predictions: list[dict[str, object]] = []
        targets: dict[str, int] = {}
        for participant in experiment.PARTICIPANTS:
            for item_index in range(24):
                item_id = f"{participant}-item-{item_index:02d}"
                target = item_index % 4
                targets[item_id] = target
                for condition in experiment.ALL_CONDITIONS:
                    if condition in {"P_plus_residual_EEG", "neural_only", "neural_plus_language"}:
                        probability = [0.01, 0.01, 0.01, 0.01]
                        probability[target] = 0.97
                    else:
                        probability = [0.25, 0.25, 0.25, 0.25]
                    predictions.append(
                        {
                            "item_id": item_id,
                            "participant_id": participant,
                            "session_id": f"ses-{item_index // 8 + 1}",
                            "condition": condition,
                            "probabilities": probability,
                        }
                    )
        return predictions, targets

    def test_prediction_freeze_and_scorer_enforce_one_shot_surfaces(self) -> None:
        predictions, targets = self._synthetic_predictions()
        freeze = experiment.build_prediction_freeze(predictions)
        experiment.verify_prediction_freeze(predictions, freeze)
        committed = experiment.commit_prediction_freeze(predictions, freeze)
        self.assertFalse(
            freeze[
                "contains_individual_prediction_probability_target_participant_outcome_or_private_path"
            ]
        )
        score = experiment.score_predictions(predictions, targets, committed)
        self.assertEqual(score["route"], "COMM-R0-G-R1")
        self.assertTrue(all(score["gates"].values()))
        self.assertFalse(score["language_arms_change_neural_router"])
        tampered = [dict(row) for row in predictions]
        tampered[0] = {**tampered[0], "probabilities": [0.7, 0.1, 0.1, 0.1]}
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "TAMPER"):
            experiment.verify_prediction_freeze(tampered, freeze)

    def test_exact_sign_flip_schedule_is_deterministic(self) -> None:
        values = [0.2] * 12
        self.assertEqual(experiment.exact_one_sided_sign_flip(values), 1 / 4096)
        self.assertTrue(
            math.isclose(
                experiment.exact_one_sided_sign_flip([0.0] * 12),
                1.0,
                abs_tol=0.0,
            )
        )

    def test_every_registered_resource_cap_refuses(self) -> None:
        base = {
            "runtime_seconds": 0,
            "peak_process_tree_RSS_bytes": 0,
            "generated_input_bytes": 0,
            "private_output_bytes": 0,
            "temporary_disk_bytes": 0,
            "public_output_bytes": 0,
        }
        experiment.enforce_resource_caps(base)
        mapping = {
            "runtime_seconds": "wall_time_seconds",
            "peak_process_tree_RSS_bytes": "peak_process_tree_RSS_bytes",
            "generated_input_bytes": "generated_input_bytes",
            "private_output_bytes": "private_output_bytes",
            "temporary_disk_bytes": "temporary_disk_bytes",
            "public_output_bytes": "public_output_bytes",
        }
        for field, cap in mapping.items():
            with self.assertRaises(experiment.CommR0GeneratedRefusal):
                experiment.enforce_resource_caps(
                    {**base, field: experiment.CAPS[cap] + 1}
                )

    def test_all_registered_adversarial_families_execute(self) -> None:
        try:
            rows, targets, _ = experiment.generate_fixture()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        capabilities, _vault = experiment.prepare_fold_capabilities(rows, targets)
        predictions = [
            {
                "item_id": row.item_id,
                "participant_id": row.participant_id,
                "session_id": row.session_id,
                "condition": condition,
                "probabilities": [0.25, 0.25, 0.25, 0.25],
            }
            for row in rows
            for condition in experiment.ALL_CONDITIONS
        ]
        freeze = experiment.build_prediction_freeze(predictions)
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            refusals = experiment.exercise_required_refusals(
                rows,
                targets,
                capabilities,
                predictions,
                freeze,
                Path(directory),
            )
        self.assertEqual(tuple(refusals), experiment.REQUIRED_REFUSALS)

    def test_cli_exposes_no_real_execution_surface(self) -> None:
        help_text = comm_r0_cli._parser().format_help()
        self.assertIn("{plan,qualify,inspect}", help_text)
        self.assertNotIn("download", help_text.lower())
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(comm_r0_cli.main(["plan"]), 0)
        self.assertEqual(json.loads(output.getvalue())["lane_id"], "COMM-R0-G")

    def test_qualifier_checks_registration_activation_and_green_proof_before_replay(self) -> None:
        source = inspect.getsource(experiment.run_generated_qualification)
        self.assertLess(source.index("load_registration"), source.index("load_activation"))
        self.assertLess(source.index("load_activation"), source.index("load_activation_proof"))
        self.assertLess(source.index("load_activation_proof"), source.index("_run_replay"))
        self.assertNotIn("requests", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("collect_remote", source)

    @unittest.skipUnless(
        os.environ.get("NDK_COMM_R0_DEV_REPLAY") == "1",
        "full generated replay is opt-in and is not the registered qualification",
    )
    def test_opt_in_full_generated_replay(self) -> None:
        for name in experiment.g1.THREAD_ENVIRONMENT:
            self.assertEqual(os.environ.get(name), "1")
        replay = experiment._run_replay()
        self.assertEqual(replay["score"]["route"], "COMM-R0-G-R1")
        self.assertEqual(replay["ledger"]["residualizer_fits"], 12)
        self.assertEqual(replay["ledger"]["classifier_or_prior_fits"], 144)
        self.assertEqual(replay["ledger"]["prediction_rows"], 4320)

    def test_output_publication_refuses_clobber_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            output = root / "result.json"
            experiment.g2._publish_no_replace(output, b"{}\n")
            with self.assertRaisesRegex(Exception, "OUTPUT-CLOBBER"):
                experiment.g2._publish_no_replace(output, b"changed")
            target = root / "target"
            target.mkdir()
            link = root / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(Exception, "DIRECTORY-CAPABILITY"):
                experiment.g2._publish_no_replace(link / "escaped.json", b"x")


if __name__ == "__main__":
    unittest.main()
